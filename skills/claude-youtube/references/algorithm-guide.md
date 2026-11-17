# Algorithm guide

How YouTube decides what to show, in enough detail to make decisions. The
recommendation system is not public; this guide sticks to what YouTube has
said itself and to patterns visible in creators' own analytics.

Evidence levels used in every reference file:

- **[official]** YouTube has said it in its Help Center, Creator Insider,
  the YouTube blog or Liaison posts.
- **[observed]** consistently visible in creator analytics and widely
  reported, but not stated by YouTube.
- **[rule of thumb]** a working heuristic. Useful, not a law. Check it
  against the channel's own data.

## The model: it follows the viewer, not the video

YouTube's stated goal is to show each viewer the videos they are most likely
to watch and be satisfied with [official]. It does not rank videos in the
abstract; it predicts, per viewer and per moment, which video they would
choose and value. Practical consequences:

- There is no single "algorithm score" for a video. A video does well when
  it keeps finding more viewers like the ones who enjoyed it.
- Signals YouTube names: what viewers click, how long they watch, whether
  they come back, likes and dislikes, "not interested", shares, and survey
  responses about satisfaction [official].
- The viewer's own history (what they watched, searched, subscribed to,
  skipped) matters as much as anything about the video [official].

## Three discovery systems, plus Shorts

Most long-form views come through three surfaces that select differently.
Studio's traffic source report shows which one a video lives on.

| system | where | what it is picking for | what you control |
| --- | --- | --- | --- |
| **Browse** | Home feed, Subscriptions | this viewer's interests right now, from their history and the channels they return to | packaging (thumbnail and title), consistency for the viewers who return |
| **Suggested** | Up Next, the column and the end of a video | what someone watching *this* video will want next | topic adjacency to big videos, series and playlists, end screens |
| **Search** | the search results page | relevance to the query, then engagement for that query | the query match in title, description, captions; answering the query fast |

**Shorts** run in their own swipe feed where the viewer did not pick the
video; the decision is whether they keep watching or swipe away [official].
Shorts and long-form performance are evaluated separately, and YouTube has
said Shorts do not hurt a channel's long-form recommendations [official].

A video can start on one system and move to another: a search video that
satisfies viewers often starts appearing in Suggested next to the big
videos on the same topic [observed].

## The testing cascade [observed]

The pattern most channels see after uploading:

1. **First hours: the closest audience.** Subscribers with notifications,
   returning viewers, and people whose history most strongly matches. These
   viewers click more easily than strangers, so early CTR is usually the
   highest the video will see.
2. **Expansion.** If those viewers click and stay, YouTube shows the video to
   progressively broader, colder groups. Impressions rise, and CTR usually
   falls as it does. Falling CTR with rising impressions is normal, not a
   problem.
3. **Plateau or second life.** The video settles at the audience size where
   satisfaction holds. Some videos are picked up again weeks or months later,
   when a topic trends or a related video goes big.

What this means for decisions:

- Judge a video at the same age as the channel's other videos (Studio's
  "typical performance" bands do this), not at day 1 against day 30.
- Do not delete and re-upload a video that started slowly; changing title
  and thumbnail is the reversible way to retest packaging [rule of thumb].
- A channel's returning audience is the launch pad. Uploading off-topic for
  that audience gives the cascade a weak first step [observed].

## CTR and average view duration together

Neither number means much alone.

- **Impressions CTR**: of the times a thumbnail was shown on YouTube, how
  often it was clicked. YouTube's own Help Center says half of all channels
  and videos have an impressions CTR between 2 and 10 percent [official].
  It is affected by where impressions came from (Browse and Suggested
  impressions convert lower than notifications and search) and by how
  broad the audience has become.
- **Average view duration (AVD) and average percentage viewed (APV)**: how
  long viewers watch. Longer videos naturally have lower APV and higher AVD.
  Compare within a length band.
- **The pair**: high CTR with low retention suggests packaging that
  over-promises; low CTR with high retention suggests a good video with
  weak packaging. Both low points to the topic [rule of thumb].
- YouTube has said it looks beyond CTR and watch time to satisfaction,
  because clickbait raises CTR and lowers satisfaction [official].

## Outliers

An outlier is a video well above the channel's own median, commonly read as
2x or more [rule of thumb]. Outliers are the best evidence a channel has of
what its audience wants. Separate:

- **Topic outliers**: the subject is in demand beyond the usual audience.
  Make more on that topic.
- **Packaging outliers**: a familiar subject framed in a way that worked.
  Reuse the framing.
- **Luck outliers**: an external share or trend. Note it; do not build a
  strategy on one.

`fetch_channel_data.py` computes `outlier` as views over the median of the
videos fetched; `search_competitor_videos.py` computes `reach_ratio` as views
over the channel's subscribers.

## Myths to correct when users raise them

- "The algorithm is punishing me." YouTube does not penalise channels for a
  slow video; a slow video gets fewer impressions because fewer viewers
  chose it [official].
- "Upload time is everything." It mostly affects the first hours; it rarely
  makes or breaks a video [rule of thumb].
- "Tags rank videos." Tags have a minor role, mainly for misspellings
  [official].
- "Shorts kill a long-form channel." See above [official].
- "Unlisting or deleting videos boosts the rest." No evidence of this; a
  deleted video's watch history is lost [rule of thumb].
