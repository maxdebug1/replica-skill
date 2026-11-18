import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from _load import load, ROOT

plan = load("replica-content", "plan")


def row(**kw):
    base = {"title": "How to cut no-shows", "kind": "searchable", "pillar": "no-shows",
            "stage": "awareness", "keyword": "reduce no-shows", "volume": "unknown",
            "impact": "8", "fit": "9", "search": "7", "effort": "6",
            "gain": "Our own beta numbers", "evidence": "replica/feedback.md", "legal": ""}
    base.update(kw)
    return base


def errors(issues):
    return [i["message"] for i in issues if i["level"] == "error"]


class Plan(unittest.TestCase):
    def test_weighted_score(self):
        scored, _ = plan.check([row()])
        # 0.4*8 + 0.3*9 + 0.2*7 + 0.1*6 = 7.9
        self.assertEqual(scored[0]["score"], 7.9)

    def test_ranked_highest_first(self):
        scored, _ = plan.check([row(title="low", impact="2", evidence=""),
                                row(title="high", impact="10")])
        self.assertEqual([s["title"] for s in scored], ["high", "low"])

    def test_information_gain_gate(self):
        _, issues = plan.check([row(gain="")])
        self.assertTrue(any("information-gain" in m for m in errors(issues)))
        _, issues = plan.check([row(kind="shareable", gain="", keyword="")])
        self.assertEqual(errors(issues), [])

    def test_high_impact_needs_evidence(self):
        _, issues = plan.check([row(evidence="")])
        self.assertTrue(any("no evidence" in m for m in errors(issues)))
        _, issues = plan.check([row(evidence="", impact="6")])
        self.assertEqual(errors(issues), [])

    def test_bad_values(self):
        _, issues = plan.check([row(kind="viral", fit="11", search="lots")])
        msgs = " ".join(errors(issues))
        self.assertIn("kind must be", msgs)
        self.assertIn("fit is 11", msgs)
        self.assertIn("search must be a number", msgs)

    def test_original_name_needs_legal(self):
        r = row(title="The Calendly alternative for teams")
        _, issues = plan.check([r], avoid=["Calendly"])
        self.assertTrue(any("lawyer" in m for m in errors(issues)))
        _, issues = plan.check([dict(r, legal="cleared")], avoid=["Calendly"])
        self.assertEqual(errors(issues), [])
        _, issues = plan.check([row(keyword="acuityscheduling vs")],
                               avoid=["Acuity Scheduling"])
        self.assertTrue(any("lawyer" in m for m in errors(issues)))

    def test_split_and_pillar_warnings(self):
        _, issues = plan.check([row(title=str(i)) for i in range(5)])
        warns = " ".join(i["message"] for i in issues if i["level"] == "warning")
        self.assertIn("searchable is 100%", warns)
        self.assertIn("1 pillars", warns)

    def test_shipped_example_passes(self):
        path = os.path.join(ROOT, "replica-content", "plan.example.csv")
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(plan.main([path, "--avoid", "Name Of The Original App"]), 0)
        self.assertIn("searchable 64%", buf.getvalue())

    def test_cli_config_out_and_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = os.path.join(tmp, "plan.csv")
            with open(csv_path, "w") as fh:
                fh.write("title,kind,keyword,impact,fit,search,effort,gain,evidence\n"
                         "Calendly vs us,searchable,x,5,5,5,5,y,\n")
            cfg = os.path.join(tmp, "brand.json")
            with open(cfg, "w") as fh:
                json.dump({"avoid": ["Calendly"]}, fh)
            out = os.path.join(tmp, "plan.md")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(plan.main([csv_path, "--config", cfg, "--out", out]), 1)
            with open(out) as fh:
                self.assertIn("## Errors", fh.read())
            buf = io.StringIO()
            with redirect_stdout(buf):
                plan.main([csv_path, "--json"])
            self.assertEqual(json.loads(buf.getvalue())["ideas"][0]["score"], 5.0)


if __name__ == "__main__":
    unittest.main()
