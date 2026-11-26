"""Contract: `develop` asks the epic's grant authorization up front, before the execute, never at the verify."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
DEVELOP = "quenching/skills/quenching-specs/references/develop.md"


def text(rel):
    return re.sub(r"\s+", " ", (ROOT / rel).read_text(encoding="utf-8"))


class DevelopEpicAuthorizationTests(unittest.TestCase):
    def test_develop_asks_the_authorization_before_the_execute(self):
        body = text(DEVELOP)
        for phrase in ("Ask the epic's authorization before the execute, never at the verify",
                       "checks 9 and 10",
                       "a hook, settings, a workflow, a grant, the gate",
                       "dated bullet",
                       "written to that `## Design` before `execute`"):
            self.assertIn(phrase, body)

    def test_the_question_sits_in_the_apply_step_before_the_records(self):
        body = text(DEVELOP)
        self.assertLess(body.index("Ask the epic's authorization"),
                        body.index("Then the frontmatter records this command owns"))


if __name__ == "__main__":
    unittest.main()
