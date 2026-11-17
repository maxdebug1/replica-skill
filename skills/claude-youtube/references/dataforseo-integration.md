# DataForSEO integration

DataForSEO is a paid data API that adds what the YouTube APIs do not:
search volume, keyword ideas, and YouTube search result pages as YouTube
shows them. Use it when the user has an account and its MCP server is
connected. Every number from it is tagged `[DFS]`.

## Is it connected?

DataForSEO publishes an official MCP server. When it is connected, its tools
appear with a DataForSEO prefix; exact tool names vary by server version, so
list the available tools and match on the API endpoint they wrap, using the
table below. If it is not connected, say so and fall back to YouTube search
suggestions and `search_competitor_videos.py`. Do not invent volumes.

Setup, if the user wants it: create a DataForSEO account, take the API login
and password from the dashboard, and add the official DataForSEO MCP server
to Claude with those credentials in its environment. Credentials go in the
MCP server's configuration, never in chat or in project files.

## The endpoints that matter for YouTube

All costs are charged per request by DataForSEO; check current prices in
their dashboard and tell the user before running a batch.

| need | DataForSEO API (v3) | use it in |
| --- | --- | --- |
| what ranks for a query on YouTube | `serp/youtube/organic/live/advanced` | seo, competitor, ideate |
| details of one video | `serp/youtube/video_info/live/advanced` | competitor |
| a video's subtitles | `serp/youtube/video_subtitles/live/advanced` | competitor, repurpose |
| a video's comments | `serp/youtube/video_comments/live/advanced` | competitor, ideate |
| Google search volume for keywords | `keywords_data/google_ads/search_volume/live` | seo, ideate |
| keyword ideas around a seed | `dataforseo_labs/google/keyword_ideas/live` or `keyword_suggestions/live` | ideate |
| trend over time | `keywords_data/google_trends/explore/live` (YouTube search can be selected as the source) | calendar, ideate |
| Google results with video carousels | `serp/google/organic/live/advanced` | seo (does Google show videos for this query?) |

## How to use the numbers

- **Search volume is Google search volume**, not YouTube search volume,
  unless the endpoint says otherwise. It is still a good relative signal of
  demand. Say which it is.
- **Google Trends with the YouTube source** gives relative interest (0 to
  100) over time, not absolute counts. Use it for seasonality and direction.
- **Cost per click** from Google Ads data is a proxy for how much advertisers
  value an audience (see `analytics-guide.md`, RPM by niche). Never present it
  as an RPM.
- **YouTube SERP** results are for the location and language requested.
  Record both.
- **Video carousels in Google results** for a query mean a video can earn
  Google traffic too: a strong sign for Help content.

## Typical calls by sub-skill

- `ideate`: keyword ideas for each pillar seed, then search volume for the
  top 50, then the YouTube SERP for the top 10 queries to see how strong the
  ranking videos are.
- `seo`: YouTube SERP for the primary query and two variants, plus search
  volume for the variants to choose the phrasing.
- `competitor`: YouTube SERP for the competitor's main queries; comments on
  their top 3 videos for unanswered questions.
- `calendar`: Trends for seasonal topics, 5 years, to find the peak month.

Store the raw responses in `youtube/data/dfs-{{date}}-{{query}}.json` so a
number can be traced back.
