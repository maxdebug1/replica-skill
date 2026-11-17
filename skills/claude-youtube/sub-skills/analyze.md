# analyze: read the numbers and say what they mean

Turns Studio data or API reports into a short list of conclusions, each one
tied to a decision. Numbers without a decision attached are trivia.

Read: `references/analytics-guide.md` (the hierarchy and funnel ratios) and
`references/algorithm-guide.md` (why a metric moves).

## Inputs, best to worst

1. OAuth analytics:
   ```bash
   python3 execution/fetch_video_analytics.py overview --days 28
   python3 execution/fetch_video_analytics.py top-videos --days 90
   python3 execution/fetch_video_analytics.py traffic --days 28
   python3 execution/fetch_video_analytics.py retention --video ID
   python3 execution/fetch_video_analytics.py subscribed --days 28
   ```
2. A Studio Advanced mode export (CSV), which also carries impressions and
   impressions CTR (the API does not).
3. Screenshots of Studio tabs.
4. Public data only (`fetch_channel_data.py`): views, likes, comments. Say
   that retention and CTR cannot be judged from this.

## Questions to answer, in this order

1. **Compared with what?** Set the baseline: the channel's own median over
   the last 10 to 20 comparable videos (same format, similar length). Every
   "good" or "bad" is relative to that.
2. **One video, early (first 48 hours).** Impressions, impressions CTR, and
   average view duration vs baseline at the same age (Studio shows typical
   performance ranges for this). Packaging problem, content problem, or
   both?
3. **One video, settled (28 days).** Traffic source mix. Retention curve
   shape: early cliff, steady slope, dips at specific moments (watch those
   moments and name the cause), spikes (rewatched parts).
4. **The channel (90 days).** Views and watch time trend, the share from
   Browse, Suggested, Search and Shorts, returning vs new viewers,
   subscribers per 1,000 views.
5. **What changed?** Line up changes in the numbers with changes the creator
   made (upload days, format, length, topic). Correlation, labelled as such.

## Traps to call out

- Small samples: one video is an anecdote. Say how many videos a pattern
  rests on.
- Survivorship: the top 5 videos share traits with the bottom 5 too; check.
- CTR and impressions move against each other. Never praise or blame CTR
  without the impressions count.
- Data lag: the last two or three days are incomplete.
- Seasonality and one-off spikes (a share from a big account).

## Output: `youtube/analysis-{{date}}.md`

Three to five findings, each: the observation with tagged numbers, the
likely cause (and the confidence), the decision it implies, and the metric
that will confirm it.
