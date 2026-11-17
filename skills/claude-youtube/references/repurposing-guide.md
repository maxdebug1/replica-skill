# Repurposing guide

The Hub, Hero, Help content model and how one video becomes several pieces
across platforms. Evidence levels as in `algorithm-guide.md`.

## Hub, Hero, Help

A planning model Google introduced for brand channels on YouTube, still a
useful way to balance a calendar [rule of thumb]:

| type | purpose | frequency | example (home espresso channel) |
| --- | --- | --- | --- |
| **Help** | answers what people search for; evergreen, steady views | often | "Why is my espresso sour? 5 fixes" |
| **Hub** | regular series for the returning audience | on a schedule | "Saturday grinder test", weekly Q&A |
| **Hero** | big, shareable, occasional; reaches new audiences | a few times a year | "I tried every espresso machine under $500" |

Most channels need a base of Help or Hub and occasional Hero. A calendar of
only Hero burns out the creator; only Help can plateau.

## One video, many pieces

From a 12-minute long video:

| piece | made from | platform |
| --- | --- | --- |
| 2 to 5 Shorts | self-contained moments with their own hook | YouTube Shorts, TikTok, Instagram Reels |
| 1 to 3 text posts | the strongest argument or number | LinkedIn, X, Threads |
| 1 article | the full script, edited for reading, video embedded | blog, newsletter, Medium |
| 1 carousel | the steps or list as slides | Instagram, LinkedIn |
| 1 poll or question | the topic, before or after the upload | YouTube community posts |
| audio | the full video if it works without pictures | podcast feeds |

## Workflow

1. Get a timed transcript: `python3 execution/fetch_transcript.py URL
   --format timed` (or the script).
2. Mark moments that stand alone: one idea, a hook in the first line, a
   clean ending. Score them.
3. For each platform, rewrite the opening line and the caption for that
   feed. Re-edit for the aspect ratio. Burn in captions.
4. Sequence: Shorts and clips in the days after the long video, pointing to
   it; the article once the video has settled; the community post before
   the next upload.
5. Track which pieces drove views back to the video (Studio: traffic from
   Shorts, external sources).

## Platform notes [observed]

- **TikTok and Reels** favour native-looking content. Remove other
  platforms' watermarks and re-export from the source file.
- **LinkedIn and X** reward the argument in text; a video upload there is a
  bonus, not the point.
- **Blogs and newsletters** capture Google search traffic that YouTube does
  not, and the embed can carry VideoObject schema
  (`seo-playbook.md`).
- **Podcasts** need audio that makes sense without visuals; cut or describe
  visual-only moments.

## Rights and rules

- Repurpose only what the creator owns or licensed for every platform used.
  Music licences often do not carry across platforms.
- Get guests' consent before clipping them.
- YouTube's reused content policy (for monetization) concerns other people's
  content without meaningful added value; repurposing your own content is
  fine [official].
