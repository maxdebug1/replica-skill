# calendar: a publishing schedule the creator can keep

Turns the strategy and the idea backlog into dated work: what to film, edit
and publish each week, with the production steps behind each upload.

Read: `references/repurposing-guide.md` for how one long video feeds Shorts
and other platforms, and the channel template for cadence defaults.

## Inputs

- `youtube/strategy.md` (pillars and cadence) and `youtube/ideas.md`.
- Capacity in hours a week, and how long one video takes them end to end
  (ask; do not assume).
- Fixed dates: launches, seasons, holidays, events in the niche, sponsor
  deadlines.
- The time zone of the audience (Studio: Audience, "When your viewers are on
  YouTube") `[Studio]`.

## Rules

- Work backwards from each publish date: idea locked, script, film, edit,
  thumbnail and title, upload and schedule. Default lead times from the
  creator's own answer, padded by 20 percent.
- Mix pillars so the same series does not run three weeks in a row unless it
  is the channel's main format.
- Seasonal and search topics publish ahead of their peak (several weeks for
  search to pick them up). If DataForSEO is connected, check the monthly
  trend `[DFS]`.
- Publish time matters less than consistency. Pick a slot an hour or two
  before the audience's peak and keep it.
- Leave a buffer: one banked video, or one empty week a month.
- Shorts slots come from the long videos (see `repurpose`) unless the
  strategy makes Shorts a separate line.

## Output: `youtube/calendar.md`

```markdown
| publish | pillar | title (working) | format | script by | film by | edit by | thumbnail | Shorts cut from it |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {{date}} | Help | ... | long 12 min | ... | ... | ... | concept A | 2 |
```

Add a weekly checklist: publish, reply to comments in the first hours, pin a
comment, share to the places in the repurposing plan, read the 48-hour
numbers. Offer an `.ics` or CSV export if they use a calendar or Notion.
