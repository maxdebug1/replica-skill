# script: a full video script built for retention

Writes a script that delivers what the title and thumbnail promised, keeps
the viewer through the middle, and ends without losing them to a goodbye.

Read: `references/retention-scripting-guide.md` in full. Read the channel's
template in `templates/` for length and tone.

## Inputs

- Title and thumbnail concept (or run `thumbnail` and `seo` first). The
  script is written to the packaging, not the other way round.
- Target length. Default from the template; a script runs at about 140 to
  170 spoken words a minute for most presenters (measure theirs with
  `fetch_transcript.py --format json` on one of their videos: it reports
  words per minute).
- The creator's voice: two or three past transcripts or scripts. Match
  sentence length, humour, how they address the viewer.
- Research notes, sources, demo steps, the payoff.

## Structure

1. **Hook (0 to 30 s).** Run `sub-skills/hook.md`. Confirm the click, state
   the stakes, open a loop that only the full video closes.
2. **Setup (to about 10 percent).** The minimum context. Cut every sentence
   the viewer could skip without confusion.
3. **Body in escalating beats.** Each beat: a mini-promise, the delivery, and
   a bridge into the next beat ("that works, until..."). Order beats so the
   strongest payoff is late but a good one comes early.
4. **Pattern interrupts** every 30 to 90 seconds of runtime, planned in the
   script: a change of shot, a graphic, a demo, a question, a story, a
   reversal. Mark them `[B-ROLL]`, `[GFX]`, `[CUT]`, `[DEMO]`.
5. **Payoff.** Close every loop opened in the hook. If one stays open, the
   comments will tell you.
6. **End.** No "that's it for today". Point to one specific next video with a
   reason to watch it, while the energy is still up. Leave the end screen
   20 seconds.

CTAs: one subscribe ask at most, placed after a payoff (the viewer just got
value), not in the first minute. Sponsor reads after the hook and setup,
disclosed, and bridged in and out.

## Writing rules

- Write for the ear: short sentences, contractions, one idea per sentence.
- Concrete over abstract: a number, a name, a picture.
- Every line earns its place by moving the viewer forward. Read the draft
  aloud; cut what you skim.
- Facts get a source in the script notes. No invented statistics or quotes.

## Output: `youtube/scripts/{{slug}}.md`

```markdown
# {{title}}
Promise: {{what the viewer gets}} | Length: {{min}} (~{{words}} words) | Loops: {{list}}

| time | beat | script | visual |
| --- | --- | --- | --- |
| 0:00 | hook | ... | [CUT] ... |
...

## Sources
## Retention risks
{{the two places most likely to lose people, and what holds them}}
```
