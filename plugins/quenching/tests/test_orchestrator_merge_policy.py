"""Contract: the orchestrator merges leaves only under a policy that names the merge."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
CANONICAL = "forced execution, push, PR and merge of every member"


def text(rel):
    body = (ROOT / rel).read_text(encoding="utf-8")
    return re.sub(r"\s+", " ", body)


class MergePolicyTests(unittest.TestCase):
    def test_orchestrator_requires_the_policy_to_name_the_merge(self):
        body = text("plugins/quenching/agents/orchestrator.md")
        self.assertIn(CANONICAL, body)
        self.assertNotIn("carries the dated autonomy policy", body)

    def test_improve_records_the_canonical_text_only_when_forced_execution_is_chosen(self):
        body = text("plugins/quenching/commands/specs/improve.md")
        self.assertIn(CANONICAL, body)
        self.assertIn("no forced execution, no push, no merge", body)

    def test_autopilot_still_records_the_canonical_text(self):
        self.assertIn(CANONICAL, text("plugins/quenching/commands/specs/autopilot.md"))


if __name__ == "__main__":
    unittest.main()
