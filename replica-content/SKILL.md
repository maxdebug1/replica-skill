---
name: replica-content
description: >-
  Plans the content that brings customers to an app clone after it ships:
  3 to 5 pillars built from the fixes and the angle, topic clusters mapped
  to buyer stages, every idea scored on customer impact, fit, search and
  effort, an information-gain gate so nothing is the eleventh copy of the
  same article, a 60/30/10 calendar, and a plan to distribute each piece.
  Every customer claim points at real evidence in replica/feedback.md. Use
  when the user says "content strategy", "what should I write about",
  "blog plan", "editorial calendar", "topic clusters", "SEO content",
  "why do my posts bring no customers", "how do I get traffic", or after
  /replica-deploy.
---

# replica-content

The app is live. Nobody knows. This skill plans what to publish so the people
who hate the original find yours, without paid ads and without inventing
anything.

Reads `replica/fixes.md` (the three lists, the fix plan and the angle),
`replica/feedback.md`, `replica/recon.md`, `replica/features.csv`,
`replica/brand.md`, `replica/brand.json` and `replica/launch/`. Writes
`replica/content/`: `pillars.md`, `plan.csv`, `plan.md`, `calendar.md`,
`distribution.md`.

```bash
python3 plan.py replica/content/plan.csv --config replica/brand.json --out replica/content/plan.md
```

Start from `plan.example.csv` in this folder.

## The rules

- **No invented evidence.** "Customers ask about this" needs a link: a theme
  in `feedback.md`, a review URL, a thread, a support ticket the user shows
  you. `plan.py` refuses a customer impact of 7 or more with no evidence.
- **No made-up numbers.** Search volume and difficulty come from a tool the
  user has (Search Console, Ahrefs, Semrush, a keyword planner) or the cell
  says `unknown`. Never guess a volume. Do not quote stats in a post unless
  the source is linked.
- **Reviewers are research, not authors.** Use the words they use for the
  problem in titles and headings. Do not paste their reviews into posts.
- **The original's name stays out by default.** "Alternative to X" and
  "X vs you" pages are the highest-intent pages a clone can write, and also
  the riskiest. They must be factual, dated, and checked by a lawyer in the
  user's country first. `plan.py` errors on any name from `avoid` unless the
  row's `legal` column says `cleared`. The rebrand sweep will list those
  pages too: review each hit by hand. Category pages ("booking links with
  flat pricing") need no name and are usually enough.
- **Every searchable piece passes the information-gain gate.** Before
  committing to it, read the current top results for its query and write
  one sentence on what yours adds that none of them have: your own product
  data, a real worked example, a working tool or template, a clearer answer,
  a stronger opinion. No sentence, no piece.

## Step 1: pillars

Pick 3 to 5 pillars, the topics the app should own. Find them four ways and
keep the ones that show up in more than one:

| lens | where it comes from |
| --- | --- |
| product-led | the jobs in `recon.md` and the fixes in `fixes.md` |
| audience-led | "what is unsolved" in `fixes.md`: whole groups the original ignores |
| search-led | what the user's keyword tool shows volume for in the category |
| competitor-led | what the original and 2 or 3 alternatives publish, and what they skip |

A good pillar ties to something the app does, matters to the people in the
angle, has search or social interest, and is broad enough for 6+ pieces.
`pillars.md`: each pillar, why (with evidence), and its subtopic clusters.

For the booking example: "booking for small teams" (the angle), "fewer
no-shows" (the text-reminder fix), "time zones without confusion" (the
time-zone fix), "fair scheduling pricing" (the billing complaints).

## Step 2: ideas, by buyer stage

For each cluster, write ideas across the four stages. Most clones skip the
last one and lose customers they already won.

| stage | modifiers | from |
| --- | --- | --- |
| awareness | what is, how to, guide to | the "hate" themes, in the users' words |
| consideration | best, vs, alternatives, comparison | the angle; category pages first |
| decision | pricing, reviews, demo, trial | `launch/pricing.md` and the billing themes |
| implementation | template, example, setup, how to use | your own flows, the importer, support questions |

Formats that tend to work for a small app:

- **Use-case pages**: {{persona}} + {{job}}. "Booking links for tutors."
  One per group in "what is unsolved".
- **Hub and spoke**: one full guide per pillar, then the spokes, linked both
  ways. Most of it can live under `/blog`. Build the hub first.
- **Templates and free tools**: a working template or small calculator the
  user can use without signing up, with the app as the next step.
- **A stats page for the category**: one-line, sourced, dated facts that
  writers can cite. Cheap to keep fresh, and it earns links and AI citations.
  Every stat linked to its source.
- **Your own data**: what you learned building and running it, shared as
  build-in-public posts ("what 140 reviews of scheduling apps say"), with
  the sample size stated.

## Step 3: score and gate

One row per idea in `plan.csv`:

```
title,kind,type,pillar,stage,keyword,volume,impact,fit,search,effort,gain,evidence,legal
```

- `kind`: `searchable`, `shareable` or `experimental`.
- `impact` (40%): how often it came up in the reviews, how many people, how
  painful. Highest weight, and it needs `evidence`.
- `fit` (30%): does it lead to the product? Does a fix answer it?
- `search` (20%): volume, competition, long tail, trend. From the tool.
- `effort` (10%): how easy it is to make well. 10 is easy.
- `gain`: the information-gain sentence. Required for searchable rows.

```bash
python3 plan.py replica/content/plan.csv --config replica/brand.json --out replica/content/plan.md
```

It scores every row (1 to 10, weighted), ranks them, checks the split and
the pillar count, and exits 1 on any error: a searchable piece with no
keyword or no gain sentence, a high impact with no evidence, a score out of
range, the original's name without legal clearance. Make the top of the list
first.

## Step 4: calendar

`calendar.md`, from the ranked list. Start at **60% searchable, 30%
shareable, 10% experimental**. A brand-new site can lean harder on
searchable to build a base. Pick a pace the user can keep (one good piece a
week beats five rushed ones), hub before spokes, and the decision and
implementation pieces early, because they convert the traffic you already
have.

Each blog post: 10 title options before drafting, then about five passes
(structure, clarity, evidence, line edit, title and SEO). Keyword in the
title, first paragraph, a heading and the URL. Link to the hub and to the
product where it truly helps.

## Step 5: distribution

Making it is half the job. `distribution.md`, per flagship piece:

- **Owned first**: the blog, the email list, the in-app changelog. This is
  the only audience nobody can take away. Everything else should point here.
- **Rented**: the social accounts. Cut each flagship into posts at creation
  time: headings that stand alone, one stat per graphic, a short clip.
- **Borrowed**: other people's audiences. The communities and threads from
  the review research where the original's unhappy users already talk,
  podcasts and newsletters in the niche, guest posts. Follow each
  community's self-promotion rules. Answer the question first.

One strong piece sent everywhere beats a fresh weak piece per platform.

## Step 6: measure

After 4 to 8 weeks: which pieces bring sign-ups, not only visits (from the
analytics set up in `/replica-deploy`). Update the winners, cut what did
nothing, and feed new questions from support and new reviews back into
`plan.csv`.

## Output

`replica/content/` complete, `plan.py` passing, the first month on the
calendar, and the hub for the top pillar outlined. Summary: the pillars,
the top 10 pieces with their scores and evidence, and the split. The loop
from here: new reviews, new fixes, new pieces.
