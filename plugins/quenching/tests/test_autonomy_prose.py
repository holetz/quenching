"""Contract: each consumer names the shared.autonomy key it reads, and the canonical merge text stays."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
CANONICAL = "forced execution, push, PR and merge of every member"


def text(rel):
    return re.sub(r"\s+", " ", (ROOT / rel).read_text(encoding="utf-8"))


class AutonomyProseTests(unittest.TestCase):
    def test_orchestrate_reads_its_keys_from_the_effective_config(self):
        body = text("plugins/quenching/commands/specs/orchestrate.md")
        self.assertIn("cq config show --effective --json", body)
        for key in ("runAloneUpTo", "merge", "maxWorkers"):
            self.assertIn(f"shared.autonomy.{key}", body)

    def test_orchestrator_consumes_the_three_values_and_keeps_the_merge_text(self):
        body = text("plugins/quenching/agents/orchestrator.md")
        for key in ("runAloneUpTo=", "merge=", "maxWorkers"):
            self.assertIn(key, body)
        self.assertIn(CANONICAL, body)

    def test_autopilot_reads_its_keys_and_the_flag_wins(self):
        body = text("plugins/quenching/commands/specs/autopilot.md")
        self.assertIn("shared.autonomy.maxLaunches", body)
        self.assertIn("shared.autonomy.livenessMinutes", body)
        self.assertIn("the flag wins over the key", body)
        self.assertIn(CANONICAL, body)


if __name__ == "__main__":
    unittest.main()
