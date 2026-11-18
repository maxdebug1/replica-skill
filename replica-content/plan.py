#!/usr/bin/env python3
"""Content plan scorer for replica-content. Standard library only.

Scores every idea in a content plan, ranks them, checks the calendar split
and the pillar count, and refuses the mistakes that waste a clone's content:
searchable pieces with nothing new to say, "customers ask this" with no
evidence, and the original app's name without a legal check.

    python3 plan.py replica/content/plan.csv
    python3 plan.py plan.csv --config replica/brand.json --out replica/content/plan.md
    python3 plan.py plan.csv --avoid "Calendly" --json

plan.csv columns (see plan.example.csv):

    title,kind,type,pillar,stage,keyword,volume,impact,fit,search,effort,
    gain,evidence,legal

kind is searchable, shareable or experimental. impact, fit, search and effort
are 1 to 10 (effort 10 means easy). Score = 0.4 impact + 0.3 fit + 0.2 search
+ 0.1 effort. gain is the information-gain sentence. evidence is a URL or a
replica/ reference. legal is "cleared" once a lawyer has checked a piece that
names the original.

Exit code 1 on any error, 0 when there are only warnings.
"""

import argparse
import csv
import json
import re
import sys

WEIGHTS = (("impact", 0.4), ("fit", 0.3), ("search", 0.2), ("effort", 0.1))
KINDS = ("searchable", "shareable", "experimental")
TARGET = {"searchable": 60, "shareable": 30, "experimental": 10}
STAGES = {"awareness", "consideration", "decision", "implementation"}
SPLIT_SLACK = 15
EVIDENCE_FROM = 7


def cell(row, key):
    return (row.get(key) or "").strip()


def name_pattern(name):
    parts = [re.escape(p) for p in re.split(r"[\s_-]+", name.strip()) if p]
    return re.compile(r"[\s_-]?".join(parts), re.I) if parts else None


def check(rows, avoid=()):
    """Return (scored rows, issues). Each issue: level, row, title, message."""
    issues = []
    scored = []
    names = [(a.strip(), name_pattern(a)) for a in avoid if a.strip()]

    def add(level, n, title, msg):
        issues.append({"level": level, "row": n, "title": title, "message": msg})

    for n, row in enumerate(rows, 2):   # row 1 is the header
        title = cell(row, "title")
        if not title:
            continue
        kind = cell(row, "kind").lower()
        if kind not in KINDS:
            add("error", n, title, "kind must be searchable, shareable or experimental")
        nums = {}
        for key, _ in WEIGHTS:
            raw = cell(row, key)
            try:
                val = float(raw)
            except ValueError:
                add("error", n, title, "%s must be a number from 1 to 10" % key)
                continue
            if not 1 <= val <= 10:
                add("error", n, title, "%s is %s, must be 1 to 10" % (key, raw))
                continue
            nums[key] = val
        score = (round(sum(nums[k] * w for k, w in WEIGHTS), 1)
                 if len(nums) == len(WEIGHTS) else None)

        if kind == "searchable":
            if not cell(row, "keyword"):
                add("error", n, title, "searchable with no target keyword")
            if not cell(row, "gain"):
                add("error", n, title, "fails the information-gain gate: say what it "
                                       "adds that the top results do not, or cut it")
            stage = cell(row, "stage").lower()
            if stage not in STAGES:
                add("warning", n, title, "no buyer stage (awareness, consideration, "
                                         "decision, implementation)")
            if not cell(row, "volume"):
                add("warning", n, title, "no volume: use the keyword tool's number "
                                         "or write unknown, never a guess")
        if nums.get("impact", 0) >= EVIDENCE_FROM and not cell(row, "evidence"):
            add("error", n, title, "impact %g with no evidence: link the theme, review "
                                   "or thread, or lower it" % nums["impact"])

        text = " ".join(cell(row, k) for k in ("title", "keyword", "gain"))
        hit = [label for label, rx in names if rx and rx.search(text)]
        if hit and cell(row, "legal").lower() != "cleared":
            add("error", n, title, "names %s: a lawyer checks it first, then set "
                                   "legal to cleared" % ", ".join(hit))
        elif hit:
            add("warning", n, title, "names %s (cleared): keep it factual and dated, "
                                     "and expect the rebrand sweep to list it"
                % ", ".join(hit))

        scored.append({"row": n, "title": title, "kind": kind,
                       "pillar": cell(row, "pillar"), "stage": cell(row, "stage").lower(),
                       "keyword": cell(row, "keyword"), "score": score,
                       "evidence": cell(row, "evidence")})

    if not scored:
        add("error", 0, "", "no ideas in the plan")
        return scored, issues

    split = split_of(scored)
    for kind, target in TARGET.items():
        if abs(split[kind] - target) > SPLIT_SLACK:
            add("warning", 0, "", "%s is %d%% of the plan, the starting split is %d%%"
                % (kind, split[kind], target))
    pillars = {s["pillar"].lower() for s in scored if s["pillar"]}
    if not 3 <= len(pillars) <= 5:
        add("warning", 0, "", "%d pillars, aim for 3 to 5" % len(pillars))
    if any(not s["pillar"] for s in scored):
        add("warning", 0, "", "%d ideas have no pillar"
            % sum(1 for s in scored if not s["pillar"]))

    scored.sort(key=lambda s: (s["score"] is None, -(s["score"] or 0), s["row"]))
    return scored, issues


def split_of(scored):
    total = len(scored)
    return {k: round(100.0 * sum(1 for s in scored if s["kind"] == k) / total)
            for k in KINDS}


def render(scored, issues):
    out = ["# Content plan", "",
           "| # | score | idea | kind | pillar | stage | keyword |",
           "| --- | --- | --- | --- | --- | --- | --- |"]
    for i, s in enumerate(scored, 1):
        out.append("| %d | %s | %s | %s | %s | %s | %s |" % (
            i, "-" if s["score"] is None else "%.1f" % s["score"], s["title"],
            s["kind"], s["pillar"] or "-", s["stage"] or "-", s["keyword"] or "-"))
    if scored:
        split = split_of(scored)
        out += ["", "Split: %s (start at 60/30/10)."
                % ", ".join("%s %d%%" % (k, split[k]) for k in KINDS)]
    errors = [i for i in issues if i["level"] == "error"]
    warnings = [i for i in issues if i["level"] == "warning"]
    for label, group in (("Errors", errors), ("Warnings", warnings)):
        if group:
            out += ["", "## %s" % label, ""]
            for i in group:
                where = "row %d, %s: " % (i["row"], i["title"]) if i["row"] else ""
                out.append("- %s%s" % (where, i["message"]))
    out += ["", "%d ideas, %d errors, %d warnings." % (len(scored), len(errors),
                                                       len(warnings))]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("plan", help="plan.csv")
    ap.add_argument("--avoid", default="", help="comma-separated names (the original "
                                                "app, its company)")
    ap.add_argument("--config", help="brand.json, for its avoid list")
    ap.add_argument("--out", help="also write the report to this file")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    avoid = [x for x in args.avoid.split(",") if x.strip()]
    try:
        if args.config:
            with open(args.config, encoding="utf-8") as fh:
                avoid += json.load(fh).get("avoid", [])
        with open(args.plan, encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
    except (OSError, ValueError) as exc:
        print("plan: %s" % exc, file=sys.stderr)
        return 2
    scored, issues = check(rows, avoid)
    report = render(scored, issues)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(report + "\n")
    print(json.dumps({"ideas": scored, "issues": issues}, indent=2) if args.json
          else report)
    return 1 if any(i["level"] == "error" for i in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
