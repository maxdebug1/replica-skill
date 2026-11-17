# competitor: learn from another channel without copying it

Studies a channel (or a topic's top videos) to find what its audience
responds to, where it is weak, and what the user's channel can do that it
does not.

Read: `references/algorithm-guide.md` (outliers and why they happen),
`references/thumbnail-ctr-guide.md`, `references/seo-playbook.md`.

## Inputs

- One to three channels, or a topic query.
- The user's channel context, so the comparison is relevant.

## Data

```bash
python3 execution/fetch_channel_data.py @them --max 100 --markdown --out youtube/data/them.json   # 5 units
python3 execution/search_competitor_videos.py "topic" --days 365 --markdown                       # 102 units
python3 execution/fetch_transcript.py URL --format timed      # for the structure of 2 or 3 outliers
```

Dry-run first and tell the user the quota cost. Without keys, ask for the
channel URL and read the public Videos tab sorted by Popular, and the most
recent 30 uploads.

## What to extract

1. **Outliers.** Videos at 2x or more the channel's own median `[API]`. What
   do they share: topic, angle, title shape, thumbnail style, length, age?
   Separate topic outliers (the subject is in demand) from packaging
   outliers (same subject, better framing).
2. **Formats and series.** Recurring formats and how each performs.
3. **Cadence and trend.** Upload frequency, and whether recent videos
   perform above or below older ones.
4. **Structure of the best videos.** From transcripts: hook type, time to the
   first payoff, number of beats, CTA placement. Learn the structure; never
   reuse the words.
5. **Audience voice.** Recurring questions and complaints in the comments of
   the top videos (read them on the page). Unanswered questions are video
   ideas.
6. **Gaps.** Topics their audience asks for that they have not made, formats
   they do not use, viewers they ignore.

## Rules

- Their titles, thumbnails, scripts and footage are theirs. Do not imitate a
  thumbnail closely or reuse a title verbatim.
- Search results are anonymous relevance ranking, not what any viewer sees.
- Subscriber counts from the API are rounded. Say so.

## Output: `youtube/competitors/{{name}}.md`

The outlier table, patterns with how many videos each rests on, structure
notes, the gap list, and three ideas for the user's channel that use what
was learned without copying it. Feed the gaps to `ideate`.
