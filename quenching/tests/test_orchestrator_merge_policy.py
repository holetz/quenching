"""Contract: the orchestrator merges leaves only under a policy that names the merge."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = "forced execution, push, PR and merge of every member"


def text(rel):
    body = (ROOT / rel).read_text(encoding="utf-8")
    return re.sub(r"\s+", " ", body)


class MergePolicyTests(unittest.TestCase):
    def test_orchestrator_requires_the_policy_to_name_the_merge(self):
        body = text("quenching/agents/spec-orchestrator.md")
        self.assertIn(CANONICAL, body)
        self.assertNotIn("carries the dated autonomy policy", body)

    def test_prohibition_matches_the_merge_step(self):
        body = text("quenching/agents/spec-orchestrator.md")
        self.assertNotIn("never merge or close a spec yourself", body)
        self.assertIn("never a raw `git merge`", body)

    def test_merge_reasons_stamp_failed_and_checks_unreadable_are_mapped(self):
        body = text("quenching/agents/spec-orchestrator.md")
        self.assertIn("`stamp-failed` is a merge that happened", body)
        self.assertIn("`checks-unreadable`", body)

    def test_improve_records_the_canonical_text_only_when_forced_execution_is_chosen(self):
        body = text("quenching/skills/quenching-specs/references/improve.md")
        self.assertIn(CANONICAL, body)
        self.assertIn("no forced execution, no push, no merge", body)

    def test_autopilot_still_records_the_canonical_text(self):
        self.assertIn(CANONICAL, text("quenching/skills/quenching-specs/references/autopilot.md"))


if __name__ == "__main__":
    unittest.main()
