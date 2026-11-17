#!/usr/bin/env python3
"""Private channel analytics for claude-youtube, through the YouTube Analytics API.

Your own channel only: it signs in with OAuth (read-only) as the channel's
owner or manager. Set up once, see utils/youtube_auth.py:

    python3 utils/youtube_auth.py --login              # views, watch time, retention
    python3 utils/youtube_auth.py --login --monetary   # plus revenue and RPM

Then:

    python3 fetch_video_analytics.py overview  --days 28
    python3 fetch_video_analytics.py top-videos --days 90 --limit 25
    python3 fetch_video_analytics.py traffic   --days 28 [--video ID]
    python3 fetch_video_analytics.py retention --video ID
    python3 fetch_video_analytics.py audience  --days 90
    python3 fetch_video_analytics.py geography --days 90
    python3 fetch_video_analytics.py devices   --days 28
    python3 fetch_video_analytics.py revenue   --days 90     # needs --monetary login
    python3 fetch_video_analytics.py overview --csv > overview.csv

Every report prints the exact query it ran, so a number can be traced back.

What the API does not give: thumbnail impressions and impression
click-through rate. Those live in YouTube Studio (Analytics, Advanced mode,
export). Export that table as CSV and hand it to the analyze sub-skill; do not
estimate CTR from views.

Analytics data lags by about two to three days, so the last days of a range
read low. The default end date is three days ago for that reason.

This API has its own quota, separate from the Data API's 10,000 units, so
these calls are not charged to quota_tracker.
"""

import argparse
import csv
import datetime as _dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from utils.youtube_auth import (ANALYTICS_API, DEFAULT_SCOPES, SCOPE_MONETARY,  # noqa: E402
                                ApiError, AuthError, http_json, oauth_token)

CORE = ("views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,"
        "subscribersGained,subscribersLost,likes,comments,shares")

REPORTS = {
    "overview": {"dimensions": "day", "metrics": CORE, "sort": "day"},
    "top-videos": {"dimensions": "video", "sort": "-views",
                   "metrics": "views,estimatedMinutesWatched,averageViewDuration,"
                              "averageViewPercentage,subscribersGained,likes,comments,shares"},
    "traffic": {"dimensions": "insightTrafficSourceType", "sort": "-views",
                "metrics": "views,estimatedMinutesWatched"},
    "retention": {"dimensions": "elapsedVideoTimeRatio",
                  "metrics": "audienceWatchRatio,relativeRetentionPerformance",
                  "needs_video": True},
    "audience": {"dimensions": "ageGroup,gender", "metrics": "viewerPercentage",
                 "sort": "-viewerPercentage"},
    "geography": {"dimensions": "country", "sort": "-views",
                  "metrics": "views,estimatedMinutesWatched,averageViewDuration"},
    "devices": {"dimensions": "deviceType", "sort": "-views",
                "metrics": "views,estimatedMinutesWatched"},
    "subscribed": {"dimensions": "subscribedStatus",
                   "metrics": "views,estimatedMinutesWatched,averageViewDuration"},
    "revenue": {"dimensions": "month", "sort": "month", "monetary": True,
                "metrics": "views,estimatedRevenue,estimatedAdRevenue,grossRevenue,"
                           "cpm,playbackBasedCpm,monetizedPlaybacks"},
}


def date_range(days, end=None, lag=3):
    end = end or (_dt.date.today() - _dt.timedelta(days=lag))
    start = end - _dt.timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()


def build_query(report, start, end, video=None, limit=None):
    spec = REPORTS[report]
    if spec.get("needs_video") and not video:
        raise ValueError("the %s report needs --video ID" % report)
    q = {"ids": "channel==MINE", "startDate": start, "endDate": end,
         "metrics": spec["metrics"], "dimensions": spec["dimensions"]}
    if spec.get("sort"):
        q["sort"] = spec["sort"]
    filters = []
    if video:
        filters.append("video==%s" % video)
    if report == "retention":
        filters.append("audienceType==ORGANIC")
    if filters:
        q["filters"] = ";".join(filters)
    if limit and spec["dimensions"] == "video":
        q["maxResults"] = int(limit)
    return q


def rows_to_dicts(response):
    """columnHeaders + rows from the API into a list of dicts."""
    names = [h["name"] for h in response.get("columnHeaders", [])]
    return [dict(zip(names, row)) for row in response.get("rows", []) or []]


def totals(rows):
    """Channel totals for an overview: sums, plus watch-time-weighted averages."""
    if not rows:
        return {}
    out = {}
    for key in ("views", "estimatedMinutesWatched", "subscribersGained", "subscribersLost",
                "likes", "comments", "shares"):
        if key in rows[0]:
            out[key] = sum(r.get(key) or 0 for r in rows)
    if out.get("views"):
        out["averageViewDurationSeconds"] = round(out["estimatedMinutesWatched"] * 60.0 / out["views"], 1)
        avp = [(r.get("averageViewPercentage") or 0, r.get("views") or 0) for r in rows]
        out["averageViewPercentage"] = round(sum(a * v for a, v in avp) / out["views"], 1)
    if "subscribersGained" in out:
        out["netSubscribers"] = out["subscribersGained"] - out.get("subscribersLost", 0)
    return out


def run(report, days=28, video=None, limit=25, end=None):
    spec = REPORTS[report]
    scopes = DEFAULT_SCOPES + ([SCOPE_MONETARY] if spec.get("monetary") else [])
    start, stop = date_range(days, end)
    q = build_query(report, start, stop, video, limit)
    token = oauth_token(scopes)
    res = http_json(ANALYTICS_API, q, headers={"Authorization": "Bearer " + token})
    rows = rows_to_dicts(res)
    out = {"report": report, "query": q, "source": "YouTube Analytics API v2 (private, owner)",
           "rows": rows}
    if report == "overview":
        out["totals"] = totals(rows)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("report", choices=sorted(REPORTS))
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--end", help="YYYY-MM-DD (default: three days ago, for data lag)")
    ap.add_argument("--video", help="limit to one video id")
    ap.add_argument("--limit", type=int, default=25, help="rows for top-videos")
    ap.add_argument("--csv", action="store_true", help="print rows as CSV")
    ap.add_argument("--out", help="write JSON here")
    args = ap.parse_args(argv)
    end = _dt.date.fromisoformat(args.end) if args.end else None
    try:
        data = run(args.report, args.days, args.video, args.limit, end)
    except (AuthError, ApiError, ValueError) as exc:
        print("fetch_video_analytics: %s" % exc, file=sys.stderr)
        if isinstance(exc, ApiError) and exc.status == 403:
            print("  403 usually means the signed-in Google account does not own or manage "
                  "this channel, or revenue was asked for without --monetary login.", file=sys.stderr)
        return 2
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        print("wrote %s" % args.out, file=sys.stderr)
    if args.csv:
        rows = data["rows"]
        if rows:
            w = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    elif not args.out:
        print(json.dumps(data, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
