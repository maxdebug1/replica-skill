# audit: a full channel review

Finds the one to three things holding a channel back, with evidence, and a
ranked fix list. An audit is a diagnosis, not a list of everything that
could be better.

Read: `references/algorithm-guide.md` (the funnel), `references/analytics-guide.md`
(the metric hierarchy), then the packaging sections of `seo-playbook.md` and
`thumbnail-ctr-guide.md` as needed.

## Inputs

- The channel (@handle or URL) and `youtube/context.md`.
- Public data: `python3 execution/fetch_channel_data.py @handle --max 100 --out youtube/data/channel.json --markdown` (5 units).
- Private data, best: `fetch_video_analytics.py overview --days 90`,
  `top-videos --days 365`, `traffic --days 90`, `subscribed --days 90`.
- From Studio (not in the API): impressions and impressions CTR per video.
  Ask for the Advanced mode export (Content, last 365 days) as CSV.

No data at all? Ask for screenshots of Studio's Overview, Content and
Audience tabs. Do not audit from vibes.

## The method: walk the funnel, stop at the first leak

Each stage only matters if the one before it works.

1. **Are they being shown?** Impressions trend over 90 days, and which
   surface they come from (Browse, Suggested, Search, Shorts feed). Flat or
   falling impressions with healthy CTR and retention points to topic
   demand or too few uploads, not packaging.
2. **Do people click?** Impressions CTR per video against the channel's own
   median. Read CTR together with impressions: CTR falls as a video reaches
   colder audiences, so a big video with low CTR is often fine.
3. **Do they stay?** Average view percentage and the retention curve's first
   30 seconds. A steep drop in the first 30 seconds is a hook or
   packaging-mismatch problem; a slow even decline is a pacing problem.
4. **Do they come back?** Returning viewers, subscribers per 1,000 views,
   views from subscribers vs non-subscribers.
5. **Is the catalogue coherent?** Do the top 10 videos by views share a
   viewer? If the outliers serve a different audience than the rest, the
   channel has two channels in it.

## Checks on the catalogue (from public data)

- Outliers: which videos did 2x+ the channel median `[API]`. What do they
  share: topic, title shape, format, length, thumbnail style?
- Underperformers: below 0.5x. Same question.
- Cadence: median days between uploads, and whether views dropped after
  gaps.
- Long vs Shorts split and the median of each.
- Packaging hygiene on the last 10 uploads: title length, keyword in the
  first 60 characters, chapters on long videos, description first two
  lines, custom thumbnails.
- Channel page: banner promise, trailer, sections, links, handle.

## Output: `youtube/audit.md`

```markdown
# Audit: {{channel}}  ({{date}}, data: {{API / Studio / screenshots}})

## The diagnosis
{{One paragraph: the stage where the funnel leaks, and the evidence.}}

## Do these, in order
1. {{action}}: {{why, with tagged numbers}}. Check {{metric}} after {{time}}.
2. ...
(3 to 5 items maximum)

## Evidence
{{funnel table, outlier table, hygiene checklist}}

## Ignore for now
{{things that are imperfect but not the bottleneck}}
```

Next: `analyze` for a deeper read of the numbers, or `strategy` if the
diagnosis is positioning.
