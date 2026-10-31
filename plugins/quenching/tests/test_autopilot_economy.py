"""Contract for the autopilot's mechanical capture and economy mode."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
AUTOPILOT = ROOT / "plugins/quenching/commands/specs/autopilot.md"


def text():
    return re.sub(r"\s+", " ", AUTOPILOT.read_text(encoding="utf-8"))


class MechanicalCaptureTests(unittest.TestCase):
    def test_conductor_creates_decided_members_without_the_architect(self):
        body = text()
        self.assertIn("**Mechanical capture, by default.**", body)
        self.assertIn("with no `quenching-specs:spec-architect`", body)
        self.assertIn("`cq specs new", body)

    def test_architect_is_only_for_real_decomposition(self):
        body = text()
        self.assertIn("launched only for real decomposition", body)
        self.assertIn("`proposal-only`", body)


class EconomyModeTests(unittest.TestCase):
    def test_threshold_is_two_members_low_or_medium(self):
        body = text()
        self.assertIn("**at most 2 members, every one `low` or `medium`**", body)
        self.assertIn("runs without `quenching-specs:orchestrator`", body)
        self.assertIn("3 or more members, or any `high`/`xhigh`", body)

    def test_trio_and_acceptance_rules_are_cited_not_restated(self):
        body = text()
        self.assertIn("`quenching-specs:spec-runner` → `quenching-specs:verifier` → `quenching-specs:git-steward`", body)
        self.assertIn("plugins/quenching/agents/orchestrator.md", body)
        self.assertIn("acceptance only on a verifier PASS", body)

    def test_launches_still_counted_and_no_new_grant(self):
        body = text()
        self.assertIn("Every launch counts in `launches`", body)
        head = AUTOPILOT.read_text(encoding="utf-8").split("---")[1]
        self.assertIn(
            "allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Bash(git:*), Bash, Read, Grep, Glob, Agent, Task, TaskStop",
            head,
        )


if __name__ == "__main__":
    unittest.main()
