# repurpose: one video, many pieces

Gets more reach from work already done, without posting the same file
everywhere. Each platform gets a version made for how people use it.

Read: `references/repurposing-guide.md` and `references/shorts-playbook.md`.

## Inputs

- The video: URL, transcript (`python3 execution/fetch_transcript.py URL
  --format timed`), or the script.
- Where the creator posts, and what has worked there before `[user]`.
- Rights: the creator must own or have licensed everything reused
  (music, clips, guests' consent to be clipped).

## Steps

1. **Map the video.** From the timed transcript, list self-contained moments:
   a tip, a story, a strong opinion, a demo result, a surprising number
   (with its source). Note start and end times.
2. **Score each moment:** does it make sense with no context, does it have a
   hook in its first line, does it end on a point? Keep the top 3 to 8.
3. **Assign each moment a destination** and rewrite it for that place:

| destination | what to make |
| --- | --- |
| YouTube Shorts | 9:16 cut, new hook line, burned-in captions, linked to the full video |
| TikTok, Instagram Reels | same cut, platform-native caption and audio choices; remove other platforms' watermarks |
| LinkedIn, X | text post that makes the point in writing, video natively uploaded if used |
| Newsletter or blog | the full argument as an article with the video embedded; good for search |
| Podcast | the audio, if the video works without pictures |
| Community tab | a poll or question from the video's topic to warm up the next upload |

4. **Sequence it.** Shorts and clips in the days after the long video to
   push viewers to it; the article when the video has settled.

## Rules

- Rewrite the hook for each platform; the first line that worked on YouTube
  may not suit a feed with different defaults.
- No re-uploading other people's content as "repurposing". YouTube's reused
  content policy affects monetization when there is no meaningful added
  value.

## Output: `youtube/repurpose/{{slug}}.md`

The moments table (time range, idea, hook line, destination), the rewritten
pieces, and a posting sequence.
