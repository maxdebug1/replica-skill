# seo: be found in search and suggested

YouTube SEO is mostly about matching a real query with a video that answers
it, then packaging it so the right viewers click. Metadata helps YouTube
understand the video; it does not rescue a video nobody wants.

Read: `references/seo-playbook.md` in full, and
`references/dataforseo-integration.md` if DataForSEO is connected.

## Inputs

- The video topic or draft title, or an existing video URL to fix.
- The target viewer from `youtube/context.md`.
- Optional live data: DataForSEO keyword volumes and the YouTube SERP;
  `search_competitor_videos.py "query" --markdown` (102 units) for what
  ranks now.

## Steps

1. **Find the query.** List 5 to 15 ways the viewer would phrase the need.
   Use YouTube's own search suggestions (type the seed in the search box and
   read the dropdown), DataForSEO volumes if available `[DFS]`, and the
   titles of videos that already rank. Never state a search volume without
   a source.
2. **Check the field.** For the top query, who ranks? Big channels only, or
   small channels with high reach ratios (a gap)? How old are the top
   results (old results mean room for a fresh one)?
3. **Choose one primary query** and two or three secondary ones. A video
   targets one search intent.
4. **Write the metadata** following the playbook:
   - Title: primary query (or its natural phrasing) in the first 60
     characters, plus the reason to click. Give 5 options with different
     angles.
   - Description: the first two lines restate the promise with the query in
     plain language; then a summary, chapters, links, and hashtags.
   - Chapters: real sections, named with the words people search.
   - Tags: a few, accurate, including common misspellings. Low weight; do not
     spend time here.
   - Spoken keywords: say the primary query naturally in the first 30
     seconds (YouTube processes speech for captions).
   - Captions: upload or correct them; auto-captions mangle names and
     jargon.
5. **Suggested, not just search.** For broad topics most views come from
   Suggested and Browse. Name the one or two big videos this one should
   appear next to, and make its packaging a natural next click from them.

## Fixing an existing video

Read the video's traffic sources first (Analytics `traffic --video ID`). If
search is already a large share, small title changes can cost rankings: test
one change at a time and wait 7 to 14 days. If search is near zero, rewrite
freely.

## Output

Primary and secondary queries (tagged), 5 titles, a description, chapters,
tags, and the "next to" videos, saved to `youtube/seo/{{slug}}.md`. Run
`metadata` to assemble the full upload package.
