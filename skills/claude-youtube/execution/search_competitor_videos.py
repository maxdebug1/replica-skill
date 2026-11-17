#!/usr/bin/env python3
"""Competitor video search for claude-youtube. Standard library only.

Finds the videos YouTube returns for a topic, then ranks them by how far each
one beat its own channel's size. A video with 400,000 views on a channel of
8,000 subscribers says more about the topic and packaging than one with
400,000 views on a channel of 4 million.

    python3 search_competitor_videos.py "sourdough for beginners"
    python3 search_competitor_videos.py "home espresso" --days 180 --order viewCount
    python3 search_competitor_videos.py "budget travel japan" --duration long --max 50
    python3 search_competitor_videos.py "ai tools" --region GB --lang en --markdown
    python3 search_competitor_videos.py "ai tools" --dry-run

Quota: every search page costs 100 units (50 results a page). Stats for the
results cost 1 unit per 50 videos, and channel sizes 1 unit per 50 channels.
One search with the default --max 25 costs 102 units. The default daily quota
of 10,000 units allows about 95 of those, so keep a list of queries and run
them once, not in a loop. --dry-run prices a run without calling anything.

Derived numbers (all computed here, all labelled):

    views_per_day   lifetime views / days since publish (min 1 day)
    reach_ratio     views / channel subscribers. Above 1 means the video
                    travelled well past the channel's own audience.
    engagement      (likes + comments) / views

Search results are YouTube's relevance ranking for an anonymous API caller in
the region given. They are not what any one viewer sees. Say so when you
report them.
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

from fetch_channel_data import median, parse_duration, parse_time  # noqa: E402
from utils.quota_tracker import QuotaExceeded, QuotaTracker, estimate  # noqa: E402
from utils.youtube_auth import ApiError, AuthError, data_api  # noqa: E402

DURATIONS = {"any": None, "short": "short", "medium": "medium", "long": "long"}


def plan_units(max_results):
    pages = max(1, math.ceil(max_results / 50.0))
    return {"search.list": pages, "videos.list": pages, "channels.list": pages}


def score(videos, channels, now):
    """Attach derived metrics. videos: Data API video items; channels: {id: subs}."""
    out = []
    for it in videos:
        sn, st = it.get("snippet", {}), it.get("statistics", {})
        views = int(st["viewCount"]) if st.get("viewCount") else None
        likes = int(st.get("likeCount") or 0)
        comments = int(st.get("commentCount") or 0)
        subs = channels.get(sn.get("channelId"))
        age = max(1.0, (now - parse_time(sn["publishedAt"])).total_seconds() / 86400.0)
        out.append({
            "id": it["id"], "url": "https://www.youtube.com/watch?v=%s" % it["id"],
            "title": sn.get("title", ""), "channel": sn.get("channelTitle", ""),
            "channel_id": sn.get("channelId"), "channel_subscribers": subs,
            "published": sn.get("publishedAt"),
            "duration_seconds": parse_duration(it.get("contentDetails", {}).get("duration")),
            "views": views, "likes": likes, "comments": comments,
            "views_per_day": round(views / age, 1) if views is not None else None,
            "reach_ratio": round(views / float(subs), 2) if views is not None and subs else None,
            "engagement": round((likes + comments) / float(views), 4) if views else None,
        })
    out.sort(key=lambda v: (v["reach_ratio"] is None, -(v["reach_ratio"] or 0)))
    return out


def title_patterns(titles):
    """Simple, countable features of a set of titles. No judgement, just counts."""
    n = len(titles) or 1
    feats = {
        "has_number": lambda t: bool(re.search(r"\d", t)),
        "has_question": lambda t: "?" in t,
        "has_brackets": lambda t: bool(re.search(r"[\[(]", t)),
        "has_colon_or_pipe": lambda t: bool(re.search(r"[:|]", t)),
        "first_person": lambda t: bool(re.search(r"\b(I|I'm|I've|my|we|our)\b", t)),
        "addresses_you": lambda t: bool(re.search(r"\b(you|your)\b", t, re.I)),
        "has_all_caps_word": lambda t: bool(re.search(r"\b[A-Z]{3,}\b", t)),
        "has_year": lambda t: bool(re.search(r"\b20\d\d\b", t)),
    }
    out = {k: round(sum(1 for t in titles if f(t)) / float(n), 2) for k, f in feats.items()}
    lengths = [len(t) for t in titles]
    out["median_length"] = median(lengths)
    out["over_60_chars"] = round(sum(1 for x in lengths if x > 60) / float(n), 2)
    return out


def search(query, max_results=25, days=None, order="relevance", duration="any",
           region=None, lang=None, tracker=None, now=None):
    now = now or _dt.datetime.now(_dt.timezone.utc)
    if tracker is not None:
        tracker.check(estimate(plan_units(max_results)), "searching %r" % query)
    ids, page = [], None
    while len(ids) < max_results:
        p = {"part": "snippet", "q": query, "type": "video", "order": order,
             "maxResults": min(50, max_results - len(ids))}
        if days:
            after = now - _dt.timedelta(days=days)
            p["publishedAfter"] = after.strftime("%Y-%m-%dT%H:%M:%SZ")
        if DURATIONS.get(duration):
            p["videoDuration"] = DURATIONS[duration]
        if region:
            p["regionCode"] = region
        if lang:
            p["relevanceLanguage"] = lang
        if page:
            p["pageToken"] = page
        res = data_api("search.list", p, tracker)
        ids += [it["id"]["videoId"] for it in res.get("items", []) if it.get("id", {}).get("videoId")]
        page = res.get("nextPageToken")
        if not page:
            break
    videos = []
    for i in range(0, len(ids), 50):
        res = data_api("videos.list", {"part": "snippet,statistics,contentDetails",
                                       "id": ",".join(ids[i:i + 50])}, tracker)
        videos += res.get("items", [])
    chan_ids = sorted({v["snippet"]["channelId"] for v in videos})
    channels = {}
    for i in range(0, len(chan_ids), 50):
        res = data_api("channels.list", {"part": "statistics", "id": ",".join(chan_ids[i:i + 50])}, tracker)
        for c in res.get("items", []):
            st = c.get("statistics", {})
            channels[c["id"]] = None if st.get("hiddenSubscriberCount") else int(st.get("subscriberCount") or 0) or None
    ranked = score(videos, channels, now)
    return {"query": query, "fetched_at": now.isoformat(),
            "params": {"order": order, "days": days, "duration": duration, "region": region, "lang": lang},
            "source": "YouTube Data API v3 search.list (anonymous relevance, not personalised)",
            "results": ranked, "title_patterns": title_patterns([v["title"] for v in ranked])}


def render_markdown(data):
    lines = ["# Search: %s" % data["query"], "",
             "Source: %s. Fetched %s. %d results." % (data["source"], data["fetched_at"][:16], len(data["results"])),
             "", "| reach | views | views/day | subs | title | channel |", "| --- | --- | --- | --- | --- | --- |"]
    for v in data["results"]:
        lines.append("| %s | %s | %s | %s | [%s](%s) | %s |" % (
            "%sx" % v["reach_ratio"] if v["reach_ratio"] is not None else "n/a", v["views"],
            v["views_per_day"], v["channel_subscribers"] if v["channel_subscribers"] else "hidden",
            v["title"].replace("|", "/"), v["url"], v["channel"].replace("|", "/")))
    tp = data["title_patterns"]
    lines += ["", "## Title patterns in these results", ""]
    lines += ["- %s: %s" % (k, tp[k]) for k in sorted(tp)]
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("query")
    ap.add_argument("--max", type=int, default=25, help="results (default 25, 50 per 100-unit page)")
    ap.add_argument("--days", type=int, help="only videos published in the last N days")
    ap.add_argument("--order", default="relevance", choices=["relevance", "viewCount", "date", "rating"])
    ap.add_argument("--duration", default="any", choices=sorted(DURATIONS),
                    help="short <4 min, medium 4 to 20, long >20 (YouTube's buckets)")
    ap.add_argument("--region", help="ISO country code, e.g. US")
    ap.add_argument("--lang", help="relevance language, e.g. en")
    ap.add_argument("--out", help="write JSON here")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    plan = plan_units(args.max)
    tracker = QuotaTracker()
    if args.dry_run:
        print("would cost %d units (%s); %d left today"
              % (estimate(plan), ", ".join("%s x%d" % kv for kv in plan.items()), tracker.remaining))
        return 0
    try:
        data = search(args.query, args.max, args.days, args.order, args.duration,
                      args.region, args.lang, tracker)
    except (AuthError, ApiError, QuotaExceeded, ValueError) as exc:
        print("search_competitor_videos: %s" % exc, file=sys.stderr)
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
