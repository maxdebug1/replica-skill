#!/usr/bin/env python3
"""API key and OAuth 2.0 handling for claude-youtube. Standard library only.

Two ways in, for two kinds of data:

1. API key, for public data (channel stats, video stats, search). Set it once:

       export YOUTUBE_API_KEY=...        # Google Cloud console, Credentials

   Restrict the key to the YouTube Data API v3 in the console.

2. OAuth 2.0, for private data you own (YouTube Analytics: watch time,
   retention, traffic sources, revenue). Create an OAuth client of type
   "Desktop app" in the Google Cloud console, download its JSON, and point at
   it:

       export YT_CLIENT_SECRET=~/.config/claude-youtube/client_secret.json
       python3 youtube_auth.py --login            # opens the consent page once
       python3 youtube_auth.py --login --monetary # also asks for revenue access

   The flow is the installed-app loopback flow with PKCE: a one-shot server on
   127.0.0.1 receives the code, nothing is sent anywhere but Google. The token
   (with its refresh token) is stored at ~/.config/claude-youtube/token.json
   with permissions 600. Delete that file to sign out, or revoke access at
   myaccount.google.com/permissions.

Scopes are read-only. Nothing in claude-youtube can upload, edit or delete.
"""

import argparse
import base64
import hashlib
import http.server
import json
import os
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

DATA_API = "https://www.googleapis.com/youtube/v3/"
ANALYTICS_API = "https://youtubeanalytics.googleapis.com/v2/reports"

SCOPE_READONLY = "https://www.googleapis.com/auth/youtube.readonly"
SCOPE_ANALYTICS = "https://www.googleapis.com/auth/yt-analytics.readonly"
SCOPE_MONETARY = "https://www.googleapis.com/auth/yt-analytics-monetary.readonly"
DEFAULT_SCOPES = [SCOPE_READONLY, SCOPE_ANALYTICS]

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "claude-youtube")
DEFAULT_CLIENT = os.path.join(CONFIG_DIR, "client_secret.json")
DEFAULT_TOKEN = os.path.join(CONFIG_DIR, "token.json")
USER_AGENT = "claude-youtube/1.0 (+stdlib urllib)"


class AuthError(Exception):
    pass


class ApiError(Exception):
    def __init__(self, status, reason, message):
        Exception.__init__(self, "HTTP %s %s: %s" % (status, reason, message))
        self.status = status
        self.reason = reason
        self.message = message


def api_key():
    key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if not key:
        raise AuthError(
            "no API key. Create one in the Google Cloud console (enable YouTube Data API v3, "
            "then Credentials, Create credentials, API key) and run: export YOUTUBE_API_KEY=...")
    return key


def _read_error(exc):
    try:
        body = json.loads(exc.read().decode("utf-8"))
        err = body.get("error", {})
        if isinstance(err, dict):
            reasons = [e.get("reason", "") for e in err.get("errors", []) if isinstance(e, dict)]
            return ",".join(r for r in reasons if r) or str(err.get("status", "")), err.get("message", "")
        return str(err), body.get("error_description", "")
    except Exception:
        return "", ""


def http_json(url, params=None, data=None, headers=None, timeout=30):
    """GET (or POST form data) and decode JSON. Raises ApiError on HTTP errors."""
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params, doseq=True)
    body = urllib.parse.urlencode(data).encode("ascii") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=dict(headers or {}))
    req.add_header("User-Agent", USER_AGENT)
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        reason, message = _read_error(exc)
        if reason == "quotaExceeded":
            message = (message or "") + " (Google says today's quota is spent. It resets at midnight Pacific.)"
        raise ApiError(exc.code, reason, message or exc.reason)


def data_api(method, params, tracker=None, key=None, token=None):
    """Call a Data API list method, e.g. data_api("videos.list", {...}).

    Charges the quota tracker before the request, so a refused call costs
    nothing locally. Uses the API key unless an OAuth token is given.
    """
    resource = method.split(".")[0]
    if tracker is not None:
        tracker.spend(method)
    params = dict(params)
    headers = {}
    if token:
        headers["Authorization"] = "Bearer " + token
    else:
        params["key"] = key or api_key()
    return http_json(DATA_API + resource, params, headers=headers)


# ---------------------------------------------------------------- OAuth 2.0

def load_client(path=None):
    path = os.path.expanduser(path or os.environ.get("YT_CLIENT_SECRET") or DEFAULT_CLIENT)
    try:
        with open(path, encoding="utf-8") as fh:
            raw = json.load(fh)
    except OSError:
        raise AuthError(
            "no OAuth client file at %s. In the Google Cloud console: enable the YouTube "
            "Analytics API, create an OAuth client ID of type Desktop app, download the JSON "
            "there (or set YT_CLIENT_SECRET)." % path)
    block = raw.get("installed") or raw.get("web") or raw
    for k in ("client_id", "client_secret"):
        if k not in block:
            raise AuthError("%s has no %s; is it an OAuth client JSON?" % (path, k))
    return {
        "client_id": block["client_id"],
        "client_secret": block["client_secret"],
        "auth_uri": block.get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
        "token_uri": block.get("token_uri", "https://oauth2.googleapis.com/token"),
    }


def pkce_pair():
    verifier = secrets.token_urlsafe(64)[:96]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


def _save_token(token, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(token, fh, indent=2)


def _load_token(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _stamp(token, now=None):
    token["expires_at"] = int((now or time.time()) + int(token.get("expires_in", 3600)) - 60)
    return token


def _refresh(client, token):
    fresh = http_json(client["token_uri"], data={
        "client_id": client["client_id"], "client_secret": client["client_secret"],
        "refresh_token": token["refresh_token"], "grant_type": "refresh_token",
    })
    token.update(fresh)
    return _stamp(token)


def _login(client, scopes, open_browser=True, timeout=300):
    verifier, challenge = pkce_pair()
    state = secrets.token_urlsafe(24)
    result = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            result.update({k: v[0] for k, v in qs.items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"claude-youtube: signed in. You can close this tab.")

        def log_message(self, *a):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    server.timeout = timeout
    redirect = "http://127.0.0.1:%d" % server.server_address[1]
    url = client["auth_uri"] + "?" + urllib.parse.urlencode({
        "client_id": client["client_id"], "redirect_uri": redirect, "response_type": "code",
        "scope": " ".join(scopes), "state": state, "access_type": "offline",
        "prompt": "consent", "code_challenge": challenge, "code_challenge_method": "S256",
    })
    print("Open this URL to grant read-only access:\n\n  %s\n" % url, file=sys.stderr)
    if open_browser:
        webbrowser.open(url)
    server.handle_request()
    server.server_close()
    if result.get("state") != state:
        raise AuthError("OAuth state mismatch or no response; try --login again")
    if "error" in result:
        raise AuthError("Google returned: %s" % result["error"])
    if "code" not in result:
        raise AuthError("no authorization code received")
    token = http_json(client["token_uri"], data={
        "client_id": client["client_id"], "client_secret": client["client_secret"],
        "code": result["code"], "code_verifier": verifier, "redirect_uri": redirect,
        "grant_type": "authorization_code",
    })
    token["scopes"] = list(scopes)
    return _stamp(token)


def oauth_token(scopes=None, client_path=None, token_path=None, interactive=True):
    """Return a valid access token string, refreshing or logging in as needed."""
    scopes = list(scopes or DEFAULT_SCOPES)
    token_path = os.path.expanduser(token_path or os.environ.get("YT_TOKEN_FILE") or DEFAULT_TOKEN)
    client = load_client(client_path)
    token = _load_token(token_path)
    if token and not set(scopes) <= set(token.get("scopes", [])):
        token = None  # needs a wider grant, e.g. --monetary
    if token and token.get("expires_at", 0) > time.time():
        return token["access_token"]
    if token and token.get("refresh_token"):
        try:
            token = _refresh(client, token)
            _save_token(token, token_path)
            return token["access_token"]
        except ApiError:
            token = None
    if not interactive:
        raise AuthError("not signed in. Run: python3 utils/youtube_auth.py --login")
    token = _login(client, scopes)
    _save_token(token, token_path)
    return token["access_token"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--login", action="store_true", help="run the OAuth consent flow")
    ap.add_argument("--monetary", action="store_true", help="also request revenue metrics")
    ap.add_argument("--check", action="store_true", help="report what is configured")
    args = ap.parse_args(argv)
    if args.login:
        scopes = DEFAULT_SCOPES + ([SCOPE_MONETARY] if args.monetary else [])
        try:
            oauth_token(scopes)
        except (AuthError, ApiError) as exc:
            print("auth: %s" % exc, file=sys.stderr)
            return 2
        print("signed in; token saved to %s" % (os.environ.get("YT_TOKEN_FILE") or DEFAULT_TOKEN))
        return 0
    has_key = bool(os.environ.get("YOUTUBE_API_KEY"))
    client = os.path.expanduser(os.environ.get("YT_CLIENT_SECRET") or DEFAULT_CLIENT)
    token = _load_token(os.path.expanduser(os.environ.get("YT_TOKEN_FILE") or DEFAULT_TOKEN))
    print("API key (public data):     %s" % ("set" if has_key else "missing, export YOUTUBE_API_KEY"))
    print("OAuth client (analytics):  %s" % ("found" if os.path.exists(client) else "missing, " + client))
    print("OAuth token:               %s" % (
        "present, scopes: " + ", ".join(s.rsplit("/", 1)[-1] for s in token.get("scopes", []))
        if token else "none, run --login"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
