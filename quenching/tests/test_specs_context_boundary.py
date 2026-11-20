"""Contract for the measured context boundary between develop, execute and conclude.

The three bodies are prose, so the fixture checks the language that binds them: the stage end
reads the live session size once, and the number decides only the tone of the next step.
"""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPECS = ROOT / "quenching/skills/quenching-specs/references"
MOLD = ROOT / "quenching/references/specs-develop/report-mold.md"
CADENCE = ROOT / "quenching/references/specs-execute/execution-cadence.md"


def text(path):
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))


def section(body, heading):
    start = body.index(heading)
    end = body.find(" ### ", start + len(heading))
    return body[start:end if end != -1 else None]


class StageEndContractTests(unittest.TestCase):
    def test_mold_owns_the_session_size_line(self):
        rules = section(text(MOLD), "### The session-size line").split("<!-- rationale -->")[0]
        self.assertIn("cq components session context --json", rules)
        for exit_code in ("| `0` |", "| `1` |", "| `2` |"):
            self.assertIn(exit_code, rules)
        self.assertIn("in a new session", rules)
        self.assertIn("(Recommended)", rules)
        self.assertIn("the number decides only the tone", rules)
        self.assertIn("nothing is recorded", rules)
        self.assertNotIn("cq specs record", rules)
        self.assertIn("An `autonomous` run prints no line", rules)

    def test_the_line_precedes_the_next_step_block(self):
        mold = text(MOLD)
        self.assertLess(mold.index("### The session-size line"), mold.index("### The next-step block"))

    def test_each_stage_end_prints_the_line(self):
        for name in ("develop.md", "execute.md", "conclude.md"):
            with self.subTest(command=name):
                self.assertIn("Print §The session-size line before the block", text(SPECS / name))

    def test_execute_offer_recommends_a_new_session_over_budget(self):
        body = text(SPECS / "execute.md")
        self.assertIn("(A, recommended) is to run `/quenching-specs conclude <id>` in a new session", body)


class SectionBoundaryContractTests(unittest.TestCase):
    def test_execute_boundary_measures_nothing_and_asks_nothing(self):
        body = text(SPECS / "execute.md")
        step = body[body.index("h. **At a section boundary"):body.index("**Pause if:**")]
        self.assertIn("keep the task commits", step)
        self.assertIn("No session-size read runs here and the boundary is never a question", step)
        self.assertNotIn("session context", step)
        self.assertNotIn("ask once", step)
        self.assertNotIn("section-boundary offer", body)
        self.assertNotIn("over-budget question", body)

    def test_cadence_boundary_measures_nothing(self):
        cadence = text(CADENCE)
        self.assertIn("The boundary measures nothing and asks nothing", cadence)
        self.assertNotIn("session context", cadence)
        self.assertIn("A count never stops a task midway", cadence)
        self.assertIn("adds no record and no fifth Handoff event", cadence)


class StandardContractTests(unittest.TestCase):
    def test_standard_records_that_the_threshold_decides_only_the_tone(self):
        standard = text(ROOT / "docs/standards/automation/context-discipline.md")
        rules = standard[standard.index("## Run for less time"):standard.index("## Measured context budgets")]
        rules = rules.split("<!-- rationale -->")[0]
        self.assertIn("The event triggers; the measured threshold decides only the tone — offer or recommendation.", rules)
        self.assertIn("cq components session context --json", rules)
        self.assertIn("Nothing is stopped and nothing is recorded.", rules)


if __name__ == "__main__":
    unittest.main()
