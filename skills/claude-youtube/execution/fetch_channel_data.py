#!/usr/bin/env python3
"""Channel stats and recent videos for claude-youtube. Standard library only.

Public data through the YouTube Data API v3 with an API key
(export YOUTUBE_API_KEY=...). Works on any public channel, yours or a
competitor's.

    python3 fetch_channel_data.py @handle
    python3 fetch_channel_data.py https://www.youtube.com/@handle --max 100
    python3 fetch_channel_data.py UCxxxxxxxxxxxxxxxxxxxxxx --out channel.json
    python3 fetch_channel_data.py @handle --markdown
    python3 fetch_channel_data.py @handle --dry-run     # price it, call nothing

Quota: 1 unit for the channel, 1 per 50 uploads listed, 1 per 50 videos
detailed. The default (50 videos) costs 3 units; --max 500 costs 21. No search
calls, so it never costs 100.

What it computes from the raw numbers, all labelled as derived:

    views_per_day      lifetime views / days since publish (min 1 day)
    engagement_rate    (likes + comments) / views
    outlier            views / median views of the videos fetched
    format_guess       "short" if 3 minutes or less, "long" otherwise. The
                       API does not say whether a video is a Short, and
                       duration is the only signal, so this is a guess and
                       is labelled one.

It does not estimate revenue, CTR or retention: the public API does not
expose them and this tool does not guess. For your own channel, use
fetch_video_analytics.py.
"""

import argparse
import datetime as _dt
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from utils.quota_tracker import QuotaExceeded, QuotaTracker  # noqa: E402
from utils.youtube_auth import ApiError, AuthError, data_api  # noqa: E402

SHORT_MAX_SECONDS = 180
DURATION = re.compile(r"^P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?)?$")
CHANNEL_ID = re.compile(r"^UC[\w-]{22}$")


class ChannelError(Exception):
    pass


def parse_duration(iso):
    """ISO 8601 duration as the API returns it (PT1H2M3S) to seconds."""
    if not iso:
        return 0
    m = DURATION.match(iso)
    if not m:
        raise ValueError("not an ISO 8601 duration: %r" % iso)
    d, h, mi, s = m.groups()
    return int(d or 0) * 86400 + int(h or 0) * 3600 + int(mi or 0) * 60 + int(float(s or 0))


def parse_channel_ref(ref):
    """Turn what a user types into an API lookup: ('id'|'handle'|'username', value)."""
    ref = ref.strip()
    if CHANNEL_ID.match(ref):
        return "id", ref
    if ref.startswith("@"):
        return "handle", ref
    m = re.search(r"youtube\.com/(?:(@[\w.\-]+)|channel/(UC[\w-]{22})|user/([\w.\-]+)|c/([\w.\-%]+))", ref)
    if m:
        handle, cid, user, custom = m.groups()
        if handle:
            return "handle", handle
        if cid:
            return "id", cid
        if user:
            return "username", user
        raise ChannelError(
            "legacy /c/%s URLs cannot be looked up through the API without a 100-unit "
            "search. Open the channel and use its @handle instead." % custom)
    if re.match(r"^[\w.\-]{3,30}$", ref):
        return "handle", "@" + ref
    raise ChannelError("cannot read a channel from %r. Use @handle, a channel URL or a UC... id." % ref)


def median(values):
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return 0
    mid = len(vals) // 2
    return vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2.0


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def parse_time(s):
    return _dt.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=_dt.timezone.utc)


def plan_units(max_videos):
    pages = max(1, math.ceil(max_videos / 50.0))
    return {"channels.list": 1, "playlistItems.list": pages, "videos.list": pages}


def shape_video(item, now):
    sn, st, cd = item.get("snippet", {}), item.get("statistics", {}), item.get("contentDetails", {})
    seconds = parse_duration(cd.get("duration"))
    published = sn.get("publishedAt")
    age_days = max(1.0, (now - parse_time(published)).total_seconds() / 86400.0) if published else None
    views, likes, comments = _int(st.get("viewCount")), _int(st.get("likeCount")), _int(st.get("commentCount"))
    return {
        "id": item.get("id"),
        "url": "https://www.youtube.com/watch?v=%s" % item.get("id"),
        "title": sn.get("title", ""),
        "published": published,
        "duration_seconds": seconds,
        "format_guess": "short" if 0 < seconds <= SHORT_MAX_SECONDS else "long",
        "views": views, "likes": likes, "comments": comments,
        "views_per_day": round(views / age_days, 1) if views is not None and age_days else None,
        "engagement_rate": round(((likes or 0) + (comments or 0)) / float(views), 4) if views else None,
        "tags": sn.get("tags", []),
        "title_length": len(sn.get("title", "")),
        "description_length": len(sn.get("description", "")),
        "has_chapters": bool(re.search(r"(?m)^\s*\(?0?0:00\)?\s", sn.get("description", ""))),
        "live": sn.get("liveBroadcastContent", "none"),
    }


def summarise(channel, videos):
    """Derived numbers over the fetched videos. Pure, no network."""
    out = {"videos_fetched": len(videos)}
    views = [v["views"] for v in videos if v["views"] is not None]
    med = median(views)
    for v in videos:
        v["outlier"] = round(v["views"] / med, 2) if med and v["views"] is not None else None
    out["median_views"] = med
    for fmt in ("long", "short"):
        sub = [v for v in videos if v["format_guess"] == fmt]
        out["%s_count" % fmt] = len(sub)
        out["%s_median_views" % fmt] = median([v["views"] for v in sub])
    dates = sorted(parse_time(v["published"]) for v in videos if v.get("published"))
    gaps = [(b - a).total_seconds() / 86400.0 for a, b in zip(dates, dates[1:])]
    out["median_days_between_uploads"] = round(median(gaps), 1) if gaps else None
    out["engagement_rate_median"] = median([v["engagement_rate"] for v in videos])
    out["with_chapters"] = sum(1 for v in videos if v["has_chapters"] and v["format_guess"] == "long")
    ranked = sorted((v for v in videos if v["outlier"] is not None), key=lambda v: -v["outlier"])
    out["top"] = [{"title": v["title"], "views": v["views"], "outlier": v["outlier"], "url": v["url"]}
                  for v in ranked[:5]]
    out["bottom"] = [{"title": v["title"], "views": v["views"], "outlier": v["outlier"], "url": v["url"]}
                     for v in ranked[-5:][::-1]] if len(ranked) > 5 else []
    subs = channel.get("subscribers")
    out["median_views_per_subscriber"] = round(med / subs, 3) if subs and med else None
    return out


def fetch(ref, max_videos=50, tracker=None, now=None):
    now = now or _dt.datetime.now(_dt.timezone.utc)
    kind, value = parse_channel_ref(ref)
    if tracker is not None:
        from utils.quota_tracker import estimate
        tracker.check(estimate(plan_units(max_videos)), "fetching %d videos" % max_videos)
    params = {"part": "snippet,statistics,contentDetails,brandingSettings"}
    params[{"id": "id", "handle": "forHandle", "username": "forUsername"}[kind]] = value
    res = data_api("channels.list", params, tracker)
    items = res.get("items") or []
    if not items:
        raise ChannelError("no channel found for %s" % ref)
    ch = items[0]
    sn, st = ch.get("snippet", {}), ch.get("statistics", {})
    channel = {
        "id": ch["id"], "title": sn.get("title"), "handle": sn.get("customUrl"),
        "url": "https://www.youtube.com/channel/%s" % ch["id"],
        "created": sn.get("publishedAt"), "country": sn.get("country"),
        "description": sn.get("description", ""),
        "subscribers": None if st.get("hiddenSubscriberCount") else _int(st.get("subscriberCount")),
        "subscribers_note": "rounded to 3 significant figures by YouTube",
        "total_views": _int(st.get("viewCount")), "video_count": _int(st.get("videoCount")),
        "keywords": ch.get("brandingSettings", {}).get("channel", {}).get("keywords", ""),
    }
    uploads = ch.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
    ids, page = [], None
    while uploads and len(ids) < max_videos:
        p = {"part": "contentDetails", "playlistId": uploads, "maxResults": 50}
        if page:
            p["pageToken"] = page
        res = data_api("playlistItems.list", p, tracker)
        ids += [it["contentDetails"]["videoId"] for it in res.get("items", [])]
        page = res.get("nextPageToken")
        if not page:
            break
    ids = ids[:max_videos]
    videos = []
    for i in range(0, len(ids), 50):
        res = data_api("videos.list", {"part": "snippet,statistics,contentDetails",
                                       "id": ",".join(ids[i:i + 50])}, tracker)
        videos += [shape_video(it, now) for it in res.get("items", [])]
    return {"fetched_at": now.isoformat(), "source": "YouTube Data API v3 (public)",
            "channel": channel, "summary": summarise(channel, videos), "videos": videos}


def render_markdown(data):
    c, s = data["channel"], data["summary"]
    lines = ["# %s" % c["title"], "",
             "Source: %s, fetched %s." % (data["source"], data["fetched_at"][:16]), "",
             "| metric | value |", "| --- | --- |",
             "| subscribers | %s |" % (c["subscribers"] if c["subscribers"] is not None else "hidden"),
             "| total views | %s |" % c["total_views"],
             "| videos (all time) | %s |" % c["video_count"],
             "| videos analysed | %s (%s long, %s short by duration) |"
             % (s["videos_fetched"], s["long_count"], s["short_count"]),
             "| median views, analysed | %s |" % s["median_views"],
             "| median views, long | %s |" % s["long_median_views"],
             "| median views, short | %s |" % s["short_median_views"],
             "| median days between uploads | %s |" % s["median_days_between_uploads"],
             "| median engagement rate | %s |" % s["engagement_rate_median"],
             "| median views per subscriber | %s |" % s["median_views_per_subscriber"],
             "", "## Outliers (views / channel median)", ""]
    for v in s["top"]:
        lines.append("- %sx  [%s](%s)  %s views" % (v["outlier"], v["title"], v["url"], v["views"]))
    if s["bottom"]:
        lines += ["", "## Underperformers", ""]
        for v in s["bottom"]:
            lines.append("- %sx  [%s](%s)  %s views" % (v["outlier"], v["title"], v["url"], v["views"]))
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("channel", help="@handle, channel URL or UC... id")
    ap.add_argument("--max", type=int, default=50, help="most recent uploads to fetch (default 50)")
    ap.add_argument("--out", help="write JSON here")
    ap.add_argument("--markdown", action="store_true", help="print a markdown summary")
    ap.add_argument("--dry-run", action="store_true", help="print the quota cost and stop")
    args = ap.parse_args(argv)
    from utils.quota_tracker import estimate
    plan = plan_units(args.max)
    if args.dry_run:
        tracker = QuotaTracker()
        print("would cost %d units (%s); %d left today"
              % (estimate(plan), ", ".join("%s x%d" % kv for kv in plan.items()), tracker.remaining))
        return 0
    try:
        data = fetch(args.channel, args.max, QuotaTracker())
    except (ChannelError, AuthError, ApiError, QuotaExceeded, ValueError) as exc:
        print("fetch_channel_data: %s" % exc, file=sys.stderr)
        return 2
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        print("wrote %s" % args.out, file=sys.stderr)
    if args.markdown:
        sys.stdout.write(render_markdown(data))
    elif not args.out:
        print(json.dumps(data, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
