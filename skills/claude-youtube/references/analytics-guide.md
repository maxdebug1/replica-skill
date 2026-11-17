# Analytics guide

Which numbers matter, in which order, and how to read them without fooling
yourself. Evidence levels as in `algorithm-guide.md`.

## The hierarchy

Read top down. A lower metric only matters once the one above it is
understood.

1. **Watch time and views trend** (90 days): is the channel growing?
2. **Traffic sources**: where views come from (Browse, Suggested, Search,
   Shorts feed, external, channel pages, notifications, playlists).
3. **Impressions and impressions CTR** (Studio only): are thumbnails shown,
   and clicked?
4. **Average view duration and average percentage viewed**, and the
   retention curve: do viewers stay?
5. **Returning viewers and subscribers per 1,000 views**: do they come back?
6. **Engagement** (likes, comments, shares): a supporting signal, not a goal.
7. **Revenue, RPM**: an outcome of all the above plus the audience's ad value.

Subscriber count is a lagging, partial measure. Many views come from
non-subscribers; Studio's "subscribed status" report shows the split
[official].

## The funnel ratios

Compute these per video and compare with the channel's own medians:

| ratio | formula | what it shows |
| --- | --- | --- |
| impressions CTR | views from impressions / impressions | packaging pull |
| average percentage viewed | average view duration / length | content hold |
| subscribers per 1,000 views | subscribers gained / views x 1,000 | conversion |
| returning viewer share | returning / unique viewers | loyalty |
| engagement rate | (likes + comments) / views | resonance (public proxy) |
| views per day | views / days since publish | velocity (public proxy) |

The last two are what `fetch_channel_data.py` can compute from public data.
Label them as proxies.

## Baselines, not benchmarks

- The right comparison is the channel's own median of comparable videos
  (same format, similar length, similar age). Studio's "typical
  performance" range does this for the first days [official].
- Universal benchmarks are mostly unreliable. The one YouTube publishes:
  half of channels and videos have impressions CTR between 2 and 10 percent
  [official]. Retention "targets" such as "50 percent" depend heavily on
  length and format [rule of thumb].
- Use medians, not means: one viral video ruins an average.

## Timing

- Analytics data lags by up to two or three days [observed].
- Read packaging at 24 to 72 hours (impressions, CTR, early AVD).
- Read content and strategy at 28 days and 90 days.
- Compare videos at the same age.

## RPM and CPM [official definitions]

- **CPM**: what advertisers pay per 1,000 monetized ad impressions, before
  YouTube's share. Advertiser-facing.
- **RPM**: what the creator earns per 1,000 views (all views, monetized or
  not), after YouTube's share, across all revenue sources in Studio. The
  creator-facing number.
- RPM is always much lower than CPM because not every view shows an ad and
  YouTube takes its share.

### By niche

YouTube publishes no RPM or CPM by niche. What drives it [observed]:

- **Advertiser demand for the audience**: topics close to expensive purchases
  or business decisions (personal finance, investing, business software,
  insurance, real estate, B2B tech) attract higher bids. Broad entertainment,
  gaming, music and kids' content usually attract lower bids.
- **Viewer country**: ad markets differ greatly by country.
- **Season**: rates usually rise toward the end of the year (holiday
  advertising) and dip at the start of the year.
- **Format**: long videos can carry mid-roll ads (eligible from 8 minutes);
  Shorts use a different revenue pool with much lower RPM.

To estimate relative ad value before a channel is monetized, Google Ads
cost-per-click for the niche's main keywords (from DataForSEO's keyword
data, `[DFS]`) is a reasonable proxy for how much advertisers value that
audience. Report it as a proxy, never as an RPM.

Never quote a third-party RPM figure as what this channel will earn. If the
channel is monetized, its own RPM is in Studio.

## Traps

- One video is an anecdote; look for a pattern across at least five.
- Two things changed at once: you cannot tell which worked.
- A spike from an external share inflates everything for a week.
- Comparing a Short with a long video on any metric.
- Survivorship: what the top videos share, the bottom ones may share too.
