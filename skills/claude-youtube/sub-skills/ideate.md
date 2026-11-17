# ideate: what to make next

Produces a ranked list of video ideas with evidence that people want each
one. An idea without a demand signal is a guess, and the list says which is
which.

Read: `references/algorithm-guide.md` (audience-first),
`references/dataforseo-integration.md` if connected, and the channel's
template.

## Inputs

`youtube/strategy.md` (pillars) or `youtube/context.md`, and any of: the
channel's own outliers, competitor gaps from `youtube/competitors/`,
comments, DataForSEO, search suggestions.

## Where ideas come from, strongest signal first

1. **The channel's own outliers** `[API]` or `[Studio]`. A sequel, a deeper
   cut, the same question for a different viewer.
2. **Questions in the comments** of the channel and its competitors.
   Repeated questions are demand you can see.
3. **Competitor outliers** with high reach ratios `[API]`: the topic travels
   beyond one channel's audience.
4. **Search demand.** YouTube search suggestions, and DataForSEO volumes and
   trends `[DFS]`. Strong for Help content.
5. **Adjacent audiences.** What the viewers also watch (Studio: Audience,
   "Other channels your audience watches") `[Studio]`.
6. **The creator's own unfair advantage.** Things only they can film: access,
   experiments, a story.

## For each idea

```
{{n}}. {{working title}}
Pillar: {{...}} | Type: Hub / Help / Hero | Format: {{long / Short}}
Demand signal: {{the evidence, tagged}} (or "none, a bet")
Angle: {{why this version beats what exists}}
Packaging hook: {{the thumbnail idea in one line}}
Effort: S / M / L
```

## Ranking

Score demand (0 to 3), fit with the channel's viewer (0 to 3), the creator's
edge (0 to 3) and effort (S 3, M 2, L 1). Sort by the total, then check the
top 10 are not all one pillar. Mark ideas with zero demand signal as bets;
a healthy list has a few, not many.

## Output: `youtube/ideas.md`

Twenty ideas, ranked, with the top three expanded into a title shortlist and
thumbnail concept each. Next: `script` for the top idea, `calendar` to
schedule the rest.
