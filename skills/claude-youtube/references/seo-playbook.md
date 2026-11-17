# SEO playbook

Rules and limits for YouTube metadata. Evidence levels as in
`algorithm-guide.md`: [official], [observed], [rule of thumb]. Limits change;
when in doubt, check YouTube Studio itself.

## Hard limits [official]

| field | limit |
| --- | --- |
| title | 100 characters |
| description | 5,000 characters |
| tags | 500 characters in total (a tag with spaces counts its quotes) |
| hashtags | more than 60 on a video and YouTube ignores all of them |
| chapters | first timestamp 0:00, at least 3 timestamps, each chapter at least 10 seconds, listed in order |
| thumbnail | 1280 x 720 recommended (minimum width 640), JPG, PNG or GIF; check the current file size limit in Studio |
| Shorts length | up to 3 minutes, square or vertical |

Angle brackets are not allowed in titles or descriptions.

## Titles

- **Truncation.** Titles are cut off in many surfaces (home feed on mobile,
  suggested column). Put the words that carry the click and the query in
  roughly the first 50 to 60 characters [observed].
- **One promise.** The title says what the viewer gets or the question it
  answers. The thumbnail shows it; the title explains it. Do not repeat
  the thumbnail text in the title [rule of thumb].
- **Search titles** use the viewer's words for the query, close to the
  start. **Browse titles** can be more curiosity-led because the viewer did
  not ask for anything [rule of thumb].
- **Specificity beats adjectives.** Numbers, names, results and stakes do
  more than "amazing" or "ultimate" [rule of thumb].
- **No misleading titles.** YouTube's spam and deceptive practices policy
  covers metadata that misrepresents the content [official].

Formulas worth trying (in `thumbnail-ctr-guide.md` too): the result
("I fixed sour espresso in 3 changes"), the question ("Why does my espresso
taste sour?"), the comparison ("$100 vs $1,000 grinder"), the mistake
("Stop doing this to your espresso"), the challenge or experiment, the list
with a number.

## Descriptions

Layout that works for people and for search [rule of thumb]:

1. **First two lines** (shown before "more", and in search snippets): the
   promise in plain words, including the main query naturally.
2. **Summary** of what the video covers, two to five lines, using the
   secondary queries where they fit.
3. **Chapters.**
4. **Links**: the most relevant next video or playlist first, then
   resources, products (with affiliate disclosure), socials.
5. **Credits and disclosures**: music licences, sources, paid promotion.
6. **Hashtags**: a few. The first three can appear above the title
   [official].

Do not stuff keywords or list unrelated terms; YouTube treats that as spam
[official].

## Tags

Tags play a minimal role in discovery and mainly help with commonly
misspelled terms [official]. Add a handful of accurate ones and move on.

## Chapters

- They help viewers navigate and can appear in Google search results as key
  moments [official].
- Name chapters with the words people search for, not inside jokes.
- YouTube can generate automatic chapters; written ones are usually better
  named.

## Captions and spoken words

- YouTube generates automatic captions from speech [official]. Uploading a
  corrected caption file fixes names and jargon and helps accessibility.
- Say the main query naturally early in the video [rule of thumb].

## Playlists and series

Playlists give Suggested and end screens a clear "next video". Name them as
a viewer would search ("Espresso for beginners") [rule of thumb].

## VideoObject schema (for an embed on your own site)

When the creator embeds the video on their website or blog, add structured
data so Google can show it as a video result. Minimal JSON-LD:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "{{title}}",
  "description": "{{the first two description lines}}",
  "thumbnailUrl": ["https://i.ytimg.com/vi/{{VIDEO_ID}}/maxresdefault.jpg"],
  "uploadDate": "{{2026-01-31T08:00:00+00:00}}",
  "duration": "{{PT12M30S}}",
  "embedUrl": "https://www.youtube.com/embed/{{VIDEO_ID}}",
  "contentUrl": "https://www.youtube.com/watch?v={{VIDEO_ID}}",
  "hasPart": [
    {"@type": "Clip", "name": "{{chapter}}", "startOffset": 0, "endOffset": 75,
     "url": "https://www.youtube.com/watch?v={{VIDEO_ID}}&t=0"}
  ]
}
</script>
```

`name`, `thumbnailUrl` and `uploadDate` are required by Google; the rest are
recommended. Validate with Google's Rich Results Test.
