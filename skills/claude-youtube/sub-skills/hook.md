# hook: the first 30 seconds

The opening decides whether the click was worth it. The job is narrow:
confirm the viewer is in the right place, make them want the rest, and get
out of the way.

Read: the hook section of `references/retention-scripting-guide.md`.

## Inputs

- The title and thumbnail (the hook continues their promise; it does not
  repeat them word for word, and it never contradicts them).
- The payoff: what the viewer has at the end.
- For a fix: the current hook and the retention curve's first 60 seconds
  `[Studio]` or `fetch_video_analytics.py retention --video ID` `[API]`.

## Write three hooks, each a different framework

Pick from the frameworks in the reference (result first, problem then
promise, the bold claim with proof, cold open in the action, the question
the viewer is already asking, the stakes). For each:

```
Framework: {{name}}
0:00  {{line 1: the first words. No greeting, no channel name, no "in this video".}}
0:05  {{line 2}}
...
0:25  {{the transition into the body}}
Visual: {{what is on screen in the first 3 seconds}}
Loop opened: {{the question only the full video answers}}
Words: {{n}} (~{{seconds}} s at the creator's pace)
```

## Checks

- First line: is it the most interesting thing you can say truthfully?
- Thumbnail match: does the first frame show what the thumbnail showed, or
  pay it off within seconds?
- No throat-clearing: welcome, intro sting, "before we start", subscribe ask,
  sponsor. Move all of them later or cut them.
- Credibility in one line, only if needed ("I tested 12 of these").
- Shorts: the hook is the first 1 to 2 seconds, and the loop matters more
  than the payoff. See `sub-skills/shorts.md`.

## Reading a retention curve's start

- A drop of more than about a third in the first 30 seconds is common, but
  compare against the channel's own other videos, not a universal number.
- Cliff at 0 to 5 s: packaging mismatch or a slow first frame.
- Cliff at 15 to 30 s: the setup is too long or the promise went vague.
- A bump later: people skipping ahead to the good part. Move it earlier.

Recommend one of the three, and say why.
