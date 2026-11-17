# Retention scripting guide

How to write so people keep watching. Evidence levels as in
`algorithm-guide.md`. Retention advice is mostly [rule of thumb]: test it
against the channel's own retention curves.

## How to read a retention curve

Studio's audience retention graph, or `fetch_video_analytics.py retention
--video ID`, which returns `audienceWatchRatio` (share of viewers still
watching at each point) and `relativeRetentionPerformance` (how that compares
with YouTube videos of similar length) [official].

| shape | usual cause |
| --- | --- |
| cliff in the first 5 seconds | the first frame or line does not match the thumbnail and title |
| steep slope to 30 to 60 s | intro too long, the promise not confirmed, throat-clearing |
| steady gentle decline | normal; slope steepness is the pacing grade |
| a dip at one moment | a tangent, a sponsor read, a slow section, an audio problem |
| a bump | people rewinding or skipping to it: a key moment, move it earlier or tease it |
| a drop before the end | a goodbye signal ("so that's it"), the end screen arriving too early |

## The hook (first 30 seconds)

The hook's job: **confirm** the click (the viewer is in the right place),
**raise the stakes** (why it matters to them), and **open a loop** (a
question only the full video closes).

Frameworks:

1. **Result first.** Show the end state, then promise how. "This bread cost
   40 cents. Here's the whole method."
2. **Problem, then promise.** Name the viewer's exact frustration in their
   words, then the payoff.
3. **Bold claim with proof.** A claim that sounds wrong, with immediate
   evidence. Only if true.
4. **Cold open.** Start in the middle of the most interesting moment, then
   rewind.
5. **The question they already have.** Ask it verbatim, promise a straight
   answer.
6. **Stakes.** What it costs to get this wrong.

Remove from the opening: greetings, channel intros, logo stings, "in this
video I will", subscribe asks, sponsor reads, long context.

## Keeping the middle

- **Escalation.** Order sections so each is at least as interesting as the
  one before; save the strongest payoff for late but give a real one early.
- **Open loops.** Tease something specific ahead ("the third mistake is the
  one that cost me the most"). Close every loop you open.
- **Bridges.** End each section with a reason to continue: "but", "which
  means", "except". Avoid "next up" lists that let viewers judge the rest
  and leave.
- **Pattern interrupts** every 30 to 90 seconds: change shot size, cut to
  B-roll, a graphic, a demo, a question to the viewer, a story, a change of
  location or pace. The interval depends on format: faster for
  entertainment, slower for deep tutorials.
- **Cut the obvious.** If the viewer could predict the next sentence, cut it.

## Pacing in words

Most presenters speak about 140 to 170 words a minute on YouTube
[rule of thumb]. Measure the creator's own pace with
`fetch_transcript.py --format json` (it reports words per minute) and size
scripts from that.

## CTAs

- **Subscribe**: once, after a payoff, tied to a reason ("there's a part two
  coming on..."). Not in the first minute.
- **Comment prompts**: a specific question, not "let me know what you think".
- **Next video**: the strongest CTA. Name a specific video and why it follows,
  before the energy drops. End screens need 5 to 20 seconds at the end
  [official].
- **Sponsor**: after the hook and setup, bridged in and out, disclosed.

## Endings

No wind-down. The last line leads straight into the end screen's video. A
summary at the end makes viewers leave; put any recap before the final
payoff.

## Script hygiene

- Write for speaking: short sentences, contractions, one idea each.
- Read it aloud with a timer.
- Mark visuals in the script (`[B-ROLL]`, `[GFX]`, `[DEMO]`, `[CUT]`).
- Every fact has a source in the notes.
