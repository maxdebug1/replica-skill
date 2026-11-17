"""Tests for skills/claude-youtube: layout, frontmatter and the offline parts of the tools."""

import datetime as dt
import json
import os
import re
import sys
import tempfile
import unittest

from _load import ROOT, load

YT = os.path.join(ROOT, "skills", "claude-youtube")
EXE = os.path.join("skills", "claude-youtube", "execution")
if os.path.join(ROOT, EXE) not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, EXE))

SUB_SKILLS = ["audit", "seo", "script", "hook", "thumbnail", "strategy", "calendar", "shorts",
              "analyze", "repurpose", "monetize", "competitor", "metadata", "ideate"]
REFERENCES = ["algorithm-guide", "seo-playbook", "retention-scripting-guide", "thumbnail-ctr-guide",
              "shorts-playbook", "analytics-guide", "monetization-guide", "repurposing-guide",
              "dataforseo-integration"]
TEMPLATES = ["education", "entertainment", "tutorial", "vlog", "review", "commentary",
             "niche-authority", "personal-brand", "shorts-first"]

channel = load(EXE, "fetch_channel_data")
search = load(EXE, "search_competitor_videos")
transcript = load(EXE, "fetch_transcript")
analytics = load(EXE, "fetch_video_analytics")
quota = load(os.path.join(EXE, "utils"), "quota_tracker")
auth = load(os.path.join(EXE, "utils"), "youtube_auth")

NOW = dt.datetime(2026, 6, 1, tzinfo=dt.timezone.utc)


def listing(folder):
    return sorted(f[:-3] for f in os.listdir(os.path.join(YT, folder)) if f.endswith(".md"))


class Layout(unittest.TestCase):
    def test_files_match_the_tree(self):
        self.assertEqual(listing("sub-skills"), sorted(SUB_SKILLS))
        self.assertEqual(listing("references"), sorted(REFERENCES))
        self.assertEqual(listing("templates"), sorted(t + "-channel" for t in TEMPLATES))
        for script in ("fetch_channel_data", "fetch_video_analytics", "search_competitor_videos",
                       "fetch_transcript", "utils/quota_tracker", "utils/youtube_auth"):
            self.assertTrue(os.path.isfile(os.path.join(YT, "execution", script + ".py")), script)

    def test_orchestrator_frontmatter_and_routes(self):
        with open(os.path.join(YT, "SKILL.md"), encoding="utf-8") as fh:
            text = fh.read()
        fm = re.match(r"^---\n(.*?)\n---\n", text, re.S).group(1)
        self.assertIn("name: claude-youtube\n", fm + "\n")
        self.assertGreater(len(fm), 200)
        for s in SUB_SKILLS:
            self.assertIn("sub-skills/%s.md" % s, text, s)

    def test_every_referenced_file_exists(self):
        pat = re.compile(r"`((?:sub-skills|references|templates|execution)/[\w./-]+\.(?:md|py))`")
        for dirpath, _, files in os.walk(YT):
            for fn in files:
                if fn.endswith(".md"):
                    with open(os.path.join(dirpath, fn), encoding="utf-8") as fh:
                        for ref in pat.findall(fh.read()):
                            self.assertTrue(os.path.exists(os.path.join(YT, ref)), "%s -> %s" % (fn, ref))

    def test_plugin_manifest(self):
        with open(os.path.join(ROOT, "skills", ".claude-plugin", "plugin.json")) as fh:
            plugin = json.load(fh)
        self.assertEqual(plugin["name"], "claude-youtube")
        self.assertEqual(plugin["skills"], "./")
        with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json")) as fh:
            market = json.load(fh)
        self.assertIn({"name": "claude-youtube", "source": "./skills"},
                      [{"name": p["name"], "source": p["source"]} for p in market["plugins"]])


class ChannelData(unittest.TestCase):
    def test_parse_duration(self):
        self.assertEqual(channel.parse_duration("PT1H2M3S"), 3723)
        self.assertEqual(channel.parse_duration("PT45S"), 45)
        self.assertEqual(channel.parse_duration("P1DT1S"), 86401)
        self.assertEqual(channel.parse_duration("P0D"), 0)
        with self.assertRaises(ValueError):
            channel.parse_duration("12:00")

    def test_parse_channel_ref(self):
        cid = "UC" + "a" * 22
        self.assertEqual(channel.parse_channel_ref(cid), ("id", cid))
        self.assertEqual(channel.parse_channel_ref("@Some.Handle"), ("handle", "@Some.Handle"))
        self.assertEqual(channel.parse_channel_ref("https://www.youtube.com/@abc/videos"), ("handle", "@abc"))
        self.assertEqual(channel.parse_channel_ref("https://youtube.com/channel/%s" % cid), ("id", cid))
        self.assertEqual(channel.parse_channel_ref("youtube.com/user/oldname"), ("username", "oldname"))
        with self.assertRaises(channel.ChannelError):
            channel.parse_channel_ref("https://www.youtube.com/c/Custom")

    def test_plan_units(self):
        self.assertEqual(quota.estimate(channel.plan_units(50)), 3)
        self.assertEqual(quota.estimate(channel.plan_units(500)), 21)

    def _video(self, vid, views, days_ago, seconds=600, desc=""):
        pub = (NOW - dt.timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")
        return {"id": vid, "snippet": {"title": "t" + vid, "publishedAt": pub, "description": desc},
                "statistics": {"viewCount": str(views), "likeCount": "10", "commentCount": "5"},
                "contentDetails": {"duration": "PT%dS" % seconds}}

    def test_shape_and_summarise(self):
        items = [self._video("a", 1000, 10), self._video("b", 4000, 20, desc="0:00 Intro\n1:00 Part"),
                 self._video("c", 2000, 30, seconds=50), self._video("d", 500, 40)]
        videos = [channel.shape_video(i, NOW) for i in items]
        self.assertEqual(videos[0]["views_per_day"], 100.0)
        self.assertEqual(videos[0]["engagement_rate"], 0.015)
        self.assertEqual(videos[2]["format_guess"], "short")
        self.assertTrue(videos[1]["has_chapters"])
        s = channel.summarise({"subscribers": 3000}, videos)
        self.assertEqual(s["median_views"], 1500)
        self.assertEqual(s["top"][0]["title"], "tb")
        self.assertEqual(s["top"][0]["outlier"], 2.67)
        self.assertEqual(s["median_days_between_uploads"], 10.0)
        self.assertEqual((s["long_count"], s["short_count"]), (3, 1))
        self.assertEqual(s["median_views_per_subscriber"], 0.5)
        self.assertIn("# ", channel.render_markdown({"channel": {"title": "X", "subscribers": None,
                      "total_views": 1, "video_count": 4}, "summary": s, "source": "test",
                      "fetched_at": NOW.isoformat()}))


class Search(unittest.TestCase):
    def test_score_ranks_by_reach(self):
        pub = "2026-05-22T00:00:00Z"
        vids = [
            {"id": "big", "snippet": {"title": "Big", "channelId": "A", "publishedAt": pub},
             "statistics": {"viewCount": "100000"}, "contentDetails": {"duration": "PT10M"}},
            {"id": "small", "snippet": {"title": "Small", "channelId": "B", "publishedAt": pub},
             "statistics": {"viewCount": "50000", "likeCount": "900", "commentCount": "100"},
             "contentDetails": {"duration": "PT8M"}},
            {"id": "hidden", "snippet": {"title": "Hidden", "channelId": "C", "publishedAt": pub},
             "statistics": {"viewCount": "10"}, "contentDetails": {"duration": "PT1M"}},
        ]
        out = search.score(vids, {"A": 1000000, "B": 5000, "C": None}, NOW)
        self.assertEqual([v["id"] for v in out], ["small", "big", "hidden"])
        self.assertEqual(out[0]["reach_ratio"], 10.0)
        self.assertEqual(out[0]["engagement"], 0.02)
        self.assertEqual(out[0]["views_per_day"], 5000.0)
        self.assertIsNone(out[2]["reach_ratio"])

    def test_title_patterns(self):
        tp = search.title_patterns(["How I fixed it in 2026?", "Why you SHOULD care", "plain"])
        self.assertEqual(tp["has_number"], 0.33)
        self.assertEqual(tp["has_question"], 0.33)
        self.assertEqual(tp["first_person"], 0.33)
        self.assertEqual(tp["addresses_you"], 0.33)
        self.assertEqual(tp["has_all_caps_word"], 0.33)
        self.assertEqual(tp["has_year"], 0.33)

    def test_one_search_costs_102(self):
        self.assertEqual(quota.estimate(search.plan_units(25)), 102)
        self.assertEqual(quota.estimate(search.plan_units(100)), 204)


class Quota(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "q.json")

    def test_spend_persist_and_refuse(self):
        day = dt.date(2026, 3, 1)
        t = quota.QuotaTracker(self.path, limit=250, today=day)
        t.spend("search.list")
        t.spend("videos.list", 3)
        self.assertEqual(t.used, 103)
        t2 = quota.QuotaTracker(self.path, limit=250, today=day)
        self.assertEqual(t2.used, 103)
        self.assertEqual(t2.state["calls"], {"search.list": 1, "videos.list": 3})
        with self.assertRaises(quota.QuotaExceeded):
            t2.spend("search.list", 2)
        self.assertEqual(t2.used, 103)  # a refused call is not charged

    def test_new_day_resets(self):
        quota.QuotaTracker(self.path, today=dt.date(2026, 3, 1)).spend("search.list")
        self.assertEqual(quota.QuotaTracker(self.path, today=dt.date(2026, 3, 2)).used, 0)

    def test_reserve_and_unknown_method(self):
        t = quota.QuotaTracker(self.path, limit=150, reserve=60, today=dt.date(2026, 3, 1))
        self.assertEqual(t.remaining, 90)
        self.assertFalse(t.can_spend(100))
        with self.assertRaises(KeyError):
            quota.cost_of("videos.insert")

    def test_pacific_day_boundary(self):
        # 07:30 UTC is still the previous day in Los Angeles, in winter and in summer.
        self.assertEqual(quota.pacific_today(dt.datetime(2026, 1, 15, 7, 30, tzinfo=dt.timezone.utc)),
                         dt.date(2026, 1, 14))
        self.assertEqual(quota.pacific_today(dt.datetime(2026, 7, 15, 6, 30, tzinfo=dt.timezone.utc)),
                         dt.date(2026, 7, 14))


class Transcript(unittest.TestCase):
    VTT = (
        "WEBVTT\nKind: captions\nLanguage: en\n\n"
        "00:00:00.000 --> 00:00:02.000 align:start position:0%\n"
        "so<00:00:00.500><c> today</c>\n\n"
        "00:00:02.000 --> 00:00:04.000\nso today\nwe bake bread\n\n"
        "00:00:04.000 --> 00:00:06.000\nwe bake bread\nfrom scratch\n\n"
        "00:00:40.000 --> 00:00:42.500\nPart two.\n"
    )
    SRT = "1\n00:00:01,000 --> 00:00:03,000\nHello <i>there</i>\n\n2\n00:01:05,500 --> 00:01:07,000\nGeneral\n"

    def test_vtt_dedupes_rolling_lines(self):
        cues = transcript.parse_captions(self.VTT)
        self.assertEqual([c["text"] for c in cues], ["so today", "we bake bread", "from scratch", "Part two."])
        self.assertEqual(transcript.to_text(cues), "so today we bake bread from scratch\n\nPart two.\n")
        self.assertEqual(transcript.to_timed(cues),
                         "[00:00] so today we bake bread from scratch\n[00:40] Part two.\n")
        st = transcript.stats(cues)
        self.assertEqual(st["words"], 9)
        self.assertEqual(st["first_30s_words"], 7)

    def test_srt(self):
        cues = transcript.parse_captions(self.SRT)
        self.assertEqual(cues[0], {"start": 1.0, "end": 3.0, "text": "Hello there"})
        self.assertEqual(cues[1]["start"], 65.5)
        self.assertEqual(transcript.clock(3725), "1:02:05")

    def test_video_id(self):
        for ref in ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=1", "https://youtu.be/dQw4w9WgXcQ",
                    "https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"):
            self.assertEqual(transcript.video_id(ref), "dQw4w9WgXcQ")
        with self.assertRaises(transcript.TranscriptError):
            transcript.video_id("not a video")

    def test_cli_on_a_file(self):
        path = os.path.join(tempfile.mkdtemp(), "c.vtt")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.VTT)
        out = os.path.join(os.path.dirname(path), "t.json")
        self.assertEqual(transcript.main(["--file", path, "--format", "json", "--out", out]), 0)
        with open(out, encoding="utf-8") as fh:
            self.assertEqual(json.load(fh)["stats"]["words"], 9)


class Analytics(unittest.TestCase):
    def test_build_query(self):
        q = analytics.build_query("top-videos", "2026-01-01", "2026-01-28", limit=10)
        self.assertEqual(q["ids"], "channel==MINE")
        self.assertEqual(q["maxResults"], 10)
        self.assertEqual(q["sort"], "-views")
        q = analytics.build_query("retention", "2026-01-01", "2026-01-28", video="abc")
        self.assertEqual(q["filters"], "video==abc;audienceType==ORGANIC")
        with self.assertRaises(ValueError):
            analytics.build_query("retention", "2026-01-01", "2026-01-28")
        self.assertTrue(analytics.REPORTS["revenue"]["monetary"])

    def test_date_range_lags(self):
        self.assertEqual(analytics.date_range(28, end=dt.date(2026, 2, 28)), ("2026-02-01", "2026-02-28"))

    def test_rows_and_totals(self):
        res = {"columnHeaders": [{"name": "day"}, {"name": "views"}, {"name": "estimatedMinutesWatched"},
                                 {"name": "averageViewPercentage"}, {"name": "subscribersGained"},
                                 {"name": "subscribersLost"}],
               "rows": [["2026-01-01", 100, 300, 40.0, 5, 1], ["2026-01-02", 300, 600, 60.0, 7, 2]]}
        rows = analytics.rows_to_dicts(res)
        self.assertEqual(rows[1]["views"], 300)
        t = analytics.totals(rows)
        self.assertEqual(t["views"], 400)
        self.assertEqual(t["averageViewDurationSeconds"], 135.0)
        self.assertEqual(t["averageViewPercentage"], 55.0)
        self.assertEqual(t["netSubscribers"], 9)
        self.assertEqual(analytics.rows_to_dicts({"columnHeaders": [{"name": "x"}]}), [])


class Auth(unittest.TestCase):
    def test_pkce_pair(self):
        import base64
        import hashlib
        v, c = auth.pkce_pair()
        self.assertTrue(43 <= len(v) <= 128)
        self.assertEqual(c, base64.urlsafe_b64encode(hashlib.sha256(v.encode()).digest()).rstrip(b"=").decode())

    def test_missing_key_explains(self):
        old = os.environ.pop("YOUTUBE_API_KEY", None)
        try:
            with self.assertRaises(auth.AuthError) as cm:
                auth.api_key()
            self.assertIn("YOUTUBE_API_KEY", str(cm.exception))
        finally:
            if old is not None:
                os.environ["YOUTUBE_API_KEY"] = old

    def test_load_client(self):
        path = os.path.join(tempfile.mkdtemp(), "c.json")
        with open(path, "w") as fh:
            json.dump({"installed": {"client_id": "id", "client_secret": "s"}}, fh)
        c = auth.load_client(path)
        self.assertEqual(c["client_id"], "id")
        self.assertEqual(c["token_uri"], "https://oauth2.googleapis.com/token")
        with self.assertRaises(auth.AuthError):
            auth.load_client(path + ".missing")

    def test_scopes_are_read_only(self):
        for s in auth.DEFAULT_SCOPES + [auth.SCOPE_MONETARY]:
            self.assertTrue(s.endswith("readonly"), s)


if __name__ == "__main__":
    unittest.main()
