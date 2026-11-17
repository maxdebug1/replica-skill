---
name: claude-youtube
description: >-
  A YouTube growth strategist in one skill: channel audits, video SEO
  (titles, descriptions, tags, chapters), retention scripts and hooks,
  thumbnail concepts, content strategy and calendars, Shorts, analytics
  reads, repurposing, monetization, competitor research, metadata and video
  ideas. Routes to 14 sub-skills, grounds advice in reference guides and, when
  keys are set, in live data from the YouTube Data and Analytics APIs or
  DataForSEO. Never invents a statistic. Use when the user says "audit my
  channel", "why is my video not getting views", "write a YouTube script",
  "title ideas", "thumbnail ideas", "YouTube SEO", "content calendar",
  "Shorts strategy", "read my analytics", "how do I monetize", "spy on a
  competitor channel", "video ideas", "repurpose this video", or mentions
  YouTube growth, CTR, retention, watch time or the algorithm.
---

# claude-youtube

One entry point for YouTube work. This file decides what the user needs,
gathers the minimum context once, sends the work to the right sub-skill, and
checks the result against the quality gates before it goes back.

```
sub-skills/   the 14 workflows (read the one you route to, in full, first)
references/   the knowledge each workflow cites (read only the ones it names)
templates/    channel-type playbooks (read the one that matches the channel)
execution/    Python tools for live YouTube data (optional, keys needed)
```

Paths in this skill are relative to this file's folder. Commands run from the
user's project, so call the tools by their full path (for example
`python3 ~/.claude/skills/claude-youtube/execution/fetch_channel_data.py`).

Write the user's files into a `youtube/` folder in their project
(`youtube/context.md`, `youtube/audit.md`, `youtube/scripts/...`), so the
sub-skills can read each other's work.

## The rules, which are not negotiable

- **Never invent a number.** No made-up view counts, CTRs, RPMs, search
  volumes, subscriber counts or "studies show". Every figure carries its
  source tag (below). If there is no data, say so and give the method to get
  it.
- **Benchmarks are ranges, not targets.** A reference range describes many
  channels. The user's own trailing median is the baseline that matters.
- **Read what you are allowed to read.** Public pages, the official APIs
  within their terms, and the user's own Studio exports. No scraping behind
  logins, no buying views, subscribers, comments or watch time, no
  engagement pods, no misleading thumbnails. Those break YouTube's policies
  and get channels terminated.
- **Disclosure is not optional.** Paid placements get YouTube's paid
  promotion box and a spoken disclosure. Realistic AI-generated or altered
  content gets YouTube's altered or synthetic content label where its policy
  requires one.
- **Other creators' work is research.** Learn structure from transcripts and
  titles. Never republish their scripts, thumbnails or footage.

### Source tags

Tag every number you report with where it came from:

| tag | meaning |
| --- | --- |
| `[API]` | fetched now with `execution/` from the YouTube Data or Analytics API |
| `[DFS]` | fetched now from DataForSEO (see `references/dataforseo-integration.md`) |
| `[Studio]` | from a YouTube Studio export or screenshot the user gave you |
| `[user]` | the user told you |
| `[ref]` | a general range from `references/`, not about this channel |
| `[est]` | your own estimate, with the arithmetic shown |

## Step 1: route

Match the request to one sub-skill. If it spans several, run them in the
order shown and pass outputs forward.

| the user wants | sub-skill | references it uses |
| --- | --- | --- |
| a full review of a channel, "why am I stuck" | `sub-skills/audit.md` | algorithm, analytics, seo, thumbnail |
| to rank in search, fix titles/descriptions/tags | `sub-skills/seo.md` | seo-playbook, dataforseo |
| a full video script | `sub-skills/script.md` | retention-scripting |
| only the first 30 seconds | `sub-skills/hook.md` | retention-scripting |
| thumbnail concepts or a thumbnail critique | `sub-skills/thumbnail.md` | thumbnail-ctr |
| positioning, niche, pillars, a 90-day plan | `sub-skills/strategy.md` | algorithm, repurposing |
| a publishing schedule | `sub-skills/calendar.md` | repurposing |
| Shorts: ideas, scripts, a Shorts strategy | `sub-skills/shorts.md` | shorts-playbook |
| to understand their numbers | `sub-skills/analyze.md` | analytics, algorithm |
| to turn one video into many pieces | `sub-skills/repurpose.md` | repurposing, shorts |
| to make money from the channel | `sub-skills/monetize.md` | monetization, analytics |
| to study another channel | `sub-skills/competitor.md` | algorithm, thumbnail, seo |
| the full upload package for one video | `sub-skills/metadata.md` | seo-playbook, thumbnail |
| what to make next | `sub-skills/ideate.md` | algorithm, dataforseo |

Common chains:

- New channel: `strategy` then `ideate` then `calendar`.
- One video, start to finish: `ideate` then `script` (which calls `hook`)
  then `thumbnail` then `metadata`.
- Stalled channel: `audit` then `analyze` then `strategy`.
- After publishing: `analyze` (at 48 hours and 28 days) then `repurpose`.

If the request is ambiguous ("help with my YouTube"), ask one question:
what result they want in the next 90 days.

## Step 2: context, gathered once

Check for `youtube/context.md`. If it exists, read it and only ask what is
missing. If not, collect this and write it:

```markdown
# Channel context
- Channel: {{@handle or URL, or "not started"}}
- Niche and the viewer it serves: {{one sentence}}
- Channel type: {{education | entertainment | tutorial | vlog | review |
  commentary | niche-authority | personal-brand | shorts-first}}
- Stage: {{subscribers, videos published, monetized yes/no}} [user]
- Goal for the next 90 days: {{e.g. reach YPP, 2 videos a week, first sponsor}}
- Capacity: {{hours a week, solo or team, on camera or faceless}}
- Constraints: {{language, budget, topics to avoid}}
- Data available: {{API key yes/no, OAuth yes/no, DataForSEO yes/no, Studio exports}}
```

Then read the matching file in `templates/`. It sets the default formats,
lengths, cadence and pitfalls for that kind of channel. A user can be two
types (a personal-brand education channel); read both and say which rule
wins where they conflict.

## Step 3: data, if it is there

Check what is available before promising live numbers:

```bash
python3 execution/utils/youtube_auth.py --check    # API key, OAuth client, token
python3 execution/utils/quota_tracker.py           # Data API units left today
```

| tool | what it gets | cost |
| --- | --- | --- |
| `fetch_channel_data.py @handle --markdown` | public stats, last 50 uploads, outliers | 3 units |
| `fetch_video_analytics.py overview --days 28` | the user's own watch time, AVD, subs | Analytics quota, not Data |
| `search_competitor_videos.py "topic" --markdown` | top videos for a query, ranked by reach | 102 units |
| `fetch_transcript.py URL --format timed` | captions as text, for structure study | no API quota |
| `utils/quota_tracker.py --estimate ...` | prices a plan before running it | free |

Always `--dry-run` a search batch first and tell the user the cost. With no
keys, every sub-skill still works from what the user pastes: Studio
screenshots, CSV exports, links. Say which mode you are in.

DataForSEO, if its MCP server is connected, adds search volume, keyword
ideas and YouTube SERP data. See `references/dataforseo-integration.md`.

## Step 4: run the sub-skill

Read the sub-skill file in full and follow it. It names the references to
read; read those sections, not every reference. Keep the user's voice: if
they gave you past scripts or titles, match them.

## Step 5: quality gates

Before anything goes back to the user, check it:

1. **Sourced.** Every number has a tag. No `[ref]` range is presented as
   this channel's result.
2. **Specific.** Advice names the video, the timestamp, the title, the
   change. "Improve your thumbnails" fails; "the last 4 thumbnails use 9+
   words of text; cut to 3 or fewer, here are three rewrites" passes.
3. **Prioritised.** At most 3 to 5 actions, ranked by expected impact times
   ease. Say what to ignore for now.
4. **Packaging matches content.** The title and thumbnail promise exactly
   what the first 30 seconds deliver. Flag any mismatch: it is the commonest
   cause of a good-CTR, bad-retention video.
5. **Within the limits.** Titles at most 100 characters (aim to front-load
   the first 50 to 60), descriptions at most 5,000, tags at most 500 in
   total, chapters valid (see `references/seo-playbook.md`).
6. **Policy-safe.** Nothing that is misleading metadata, fake engagement,
   undisclosed sponsorship, or reused content without transformation.
7. **Measurable.** Each recommendation says which metric should move and
   when to check it (usually 48 hours for packaging, 28 days for strategy).

If a gate fails, fix it before replying; do not list the failure as a
caveat.

## Output

Lead with the answer (the 3 to 5 actions or the finished asset), then the
evidence, then the next sub-skill to run. Save the full version to
`youtube/` and say where.
