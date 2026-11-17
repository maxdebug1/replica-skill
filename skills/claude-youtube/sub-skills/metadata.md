# metadata: the full upload package for one video

Everything that goes into YouTube Studio for one upload, checked against the
limits, ready to paste.

Read: `references/seo-playbook.md` (limits, chapters, description layout)
and `references/thumbnail-ctr-guide.md` (title and thumbnail pairing).

## Inputs

The final script or transcript (`fetch_transcript.py --format timed` once
uploaded as unlisted), the primary query from `seo` if it was run, the
thumbnail concept, links to include, sponsor details if any.

## The package

```markdown
# Upload package: {{working title}}

## Title (pick one)
1. {{title}}  ({{n}} chars)
2. ...
3. ...
Recommended: {{n}}, because {{reason}}. Test 2 against it if Test and Compare is available.

## Thumbnail
{{concept and text, from the thumbnail sub-skill}}

## Description
{{2 lines: the promise in plain words, with the primary query}}

{{3 to 5 lines: what the video covers, for search and for people deciding}}

{{chapters}}
0:00 {{...}}
...

{{links: the related video or playlist first, then resources, then socials}}
{{sponsor disclosure line, if any}}

{{up to 3 hashtags}}

## Tags
{{comma separated, under 500 characters total}}

## Settings
- Category: {{...}}
- Audience: {{made for kids yes/no: the creator's legal call under COPPA, never guessed}}
- Paid promotion: {{yes/no}}
- Altered or synthetic content: {{yes/no, per YouTube's disclosure rules}}
- Language and caption language: {{...}}
- Captions: upload the corrected file
- End screen: {{the specific next video or playlist}}, subscribe element
- Cards: {{time}} {{video}} (only where it helps the viewer)
- Playlist: {{...}}
- Pinned comment: {{a question or the next step}}
- Publish: {{date and time, audience time zone}}
```

## Checks before handing it over

- Title 100 characters or fewer, most important words in the first 60.
- Description 5,000 characters or fewer; the first two lines make sense on
  their own in search.
- Chapters: first at 0:00, at least three, each at least 10 seconds,
  ascending.
- Hashtags: a few relevant ones (3 to 5 is plenty; over 60 and YouTube
  ignores them all).
- Tags under 500 characters in total.
- No misleading claims in title, thumbnail or description; the video
  delivers what they promise.
- Sponsor disclosed in the setting and in words.

Save to `youtube/uploads/{{slug}}.md`.
