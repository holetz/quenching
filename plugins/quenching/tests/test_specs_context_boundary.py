"""Contract for the measured context boundary between develop, execute and conclude.

The three bodies are prose, so the fixture checks the language that binds them: the stage end
reads the live session size once, and the number decides only the tone of the next step.
"""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
SPECS = ROOT / "plugins/quenching/commands/specs"
MOLD = ROOT / "plugins/quenching/assets/references/specs-develop/report-mold.md"


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
        self.assertIn("\"(Recommended)\", is to run `/quenching:specs:conclude <id>` in a new session", body)


if __name__ == "__main__":
    unittest.main()
