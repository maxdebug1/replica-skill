#!/usr/bin/env python3
"""YouTube Data API v3 quota tracker for claude-youtube. Standard library only.

The Data API gives a project 10,000 units a day by default. The day resets at
midnight Pacific time. Every call costs units whether it returns one row or
fifty, and a search costs 100 times a list call, so a careless loop of
searches burns the whole day in under a minute. This file keeps a running
count on disk and refuses a call that would go over.

    python3 quota_tracker.py                        # what is used and left today
    python3 quota_tracker.py --estimate search.list=3 videos.list=2
    python3 quota_tracker.py --reset                # zero today's local count

The count is local. It only knows about calls made through these scripts. If
the same Google Cloud project is used elsewhere, the real remaining quota is
lower; the authoritative number is in the Cloud console under
APIs & Services, YouTube Data API v3, Quotas.

The YouTube Analytics API (fetch_video_analytics.py) has its own separate
quota and is not counted here.

Costs are from Google's published quota table for the Data API. If Google
changes them, edit COSTS.
"""

import argparse
import datetime as _dt
import json
import os
import sys

DAILY_LIMIT = 10000

COSTS = {
    "channels.list": 1,
    "videos.list": 1,
    "playlistItems.list": 1,
    "playlists.list": 1,
    "commentThreads.list": 1,
    "comments.list": 1,
    "videoCategories.list": 1,
    "i18nRegions.list": 1,
    "search.list": 100,
    "captions.list": 50,
    "captions.download": 200,
}

DEFAULT_PATH = os.path.join(os.path.expanduser("~"), ".cache", "claude-youtube", "quota.json")


class QuotaExceeded(Exception):
    pass


def pacific_today(now=None):
    """The quota day: the current date in America/Los_Angeles."""
    now = now or _dt.datetime.now(_dt.timezone.utc)
    try:
        from zoneinfo import ZoneInfo  # Python 3.9+
        return now.astimezone(ZoneInfo("America/Los_Angeles")).date()
    except Exception:
        # No tz database: approximate with PST (UTC-8). At worst the local
        # count resets an hour late during daylight saving time.
        return (now - _dt.timedelta(hours=8)).date()


def cost_of(method, calls=1):
    if method not in COSTS:
        raise KeyError("unknown API method %r. Known: %s" % (method, ", ".join(sorted(COSTS))))
    return COSTS[method] * int(calls)


def estimate(plan):
    """plan: {method: number_of_calls}. Returns total units."""
    return sum(cost_of(m, n) for m, n in plan.items())


class QuotaTracker:
    def __init__(self, path=None, limit=None, reserve=0, today=None):
        self.path = path or os.environ.get("YT_QUOTA_FILE") or DEFAULT_PATH
        env_limit = os.environ.get("YT_QUOTA_LIMIT")
        self.limit = int(limit if limit is not None else (env_limit or DAILY_LIMIT))
        self.reserve = int(reserve)
        self._today = today
        self.state = self._load()

    def today(self):
        return (self._today or pacific_today()).isoformat()

    def _fresh(self):
        return {"date": self.today(), "used": 0, "calls": {}}

    def _load(self):
        try:
            with open(self.path, encoding="utf-8") as fh:
                state = json.load(fh)
        except (OSError, ValueError):
            return self._fresh()
        if state.get("date") != self.today():
            return self._fresh()
        state.setdefault("used", 0)
        state.setdefault("calls", {})
        return state

    def save(self):
        folder = os.path.dirname(self.path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(self.state, fh, indent=2)
        os.replace(tmp, self.path)

    @property
    def used(self):
        return int(self.state["used"])

    @property
    def remaining(self):
        return max(0, self.limit - self.reserve - self.used)

    def can_spend(self, units):
        return units <= self.remaining

    def check(self, units, what="this run"):
        if not self.can_spend(units):
            raise QuotaExceeded(
                "%s needs %d units but only %d are left today (used %d of %d, reserve %d). "
                "The quota resets at midnight Pacific time."
                % (what, units, self.remaining, self.used, self.limit, self.reserve))

    def spend(self, method, calls=1):
        units = cost_of(method, calls)
        self.check(units, method)
        if self.state.get("date") != self.today():
            self.state = self._fresh()
        self.state["used"] = self.used + units
        self.state["calls"][method] = int(self.state["calls"].get(method, 0)) + int(calls)
        self.save()
        return units

    def reset(self):
        self.state = self._fresh()
        self.save()

    def summary(self):
        return {
            "date": self.state["date"], "limit": self.limit, "reserve": self.reserve,
            "used": self.used, "remaining": self.remaining,
            "calls": dict(self.state["calls"]),
        }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--estimate", nargs="*", metavar="METHOD=N",
                    help="price a plan, e.g. search.list=3 videos.list=2")
    ap.add_argument("--reset", action="store_true", help="zero today's local count")
    ap.add_argument("--file", help="quota file (default %s or $YT_QUOTA_FILE)" % DEFAULT_PATH)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    tracker = QuotaTracker(path=args.file)
    if args.reset:
        tracker.reset()
    if args.estimate is not None:
        plan = {}
        try:
            for item in args.estimate:
                method, _, n = item.partition("=")
                plan[method] = int(n or 1)
            units = estimate(plan)
        except (KeyError, ValueError) as exc:
            print("quota: %s" % exc, file=sys.stderr)
            return 2
        ok = tracker.can_spend(units)
        out = {"plan": plan, "units": units, "remaining": tracker.remaining, "fits": ok}
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print("plan costs %d units; %d left today; %s"
                  % (units, tracker.remaining, "fits" if ok else "DOES NOT FIT"))
        return 0 if ok else 1
    s = tracker.summary()
    if args.json:
        print(json.dumps(s, indent=2))
    else:
        print("quota day %s (Pacific): used %d of %d, %d left"
              % (s["date"], s["used"], s["limit"], s["remaining"]))
        for m, n in sorted(s["calls"].items()):
            print("  %-20s %4d calls  %6d units" % (m, n, cost_of(m, n) if m in COSTS else 0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
