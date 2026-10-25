"""Contract: the orchestrator ends its turn only with no active worker, or with a reported stop."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]


def waiting_section():
    body = (ROOT / "plugins/quenching/agents/orchestrator.md").read_text(encoding="utf-8")
    match = re.search(r"## Waiting\n(.*?)(?=\n## )", body, re.S)
    assert match, "## Waiting section is missing"
    return re.sub(r"\s+", " ", match.group(1))


class TurnEndTests(unittest.TestCase):
    def test_turn_ends_only_when_every_worker_returned_and_passed_the_verifier(self):
        text = waiting_section()
        self.assertIn("The turn ends only when every worker you launched has returned", text)
        self.assertIn("passed the verifier", text)

    def test_stopping_with_active_workers_requires_a_report_with_the_reason(self):
        text = waiting_section()
        self.assertIn("report, with the reason, that you stopped with workers still active", text)

    def test_a_waiting_sentence_is_not_the_end_of_the_turn(self):
        self.assertIn("is not the end of the turn", waiting_section())


if __name__ == "__main__":
    unittest.main()
