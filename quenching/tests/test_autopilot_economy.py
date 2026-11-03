"""Contract for the autopilot's mechanical capture and economy mode."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
AUTOPILOT = ROOT / "quenching/commands/specs/autopilot.md"


def text():
    return re.sub(r"\s+", " ", AUTOPILOT.read_text(encoding="utf-8"))


class MechanicalCaptureTests(unittest.TestCase):
    def test_conductor_creates_decided_members_in_this_session(self):
        body = text()
        self.assertIn("**Mechanical capture, by default.**", body)
        self.assertNotIn("spec-architect", body)
        self.assertIn("`cq specs new", body)

    def test_real_decomposition_stays_in_this_session(self):
        body = text()
        self.assertIn("**Decomposition, by this session.**", body)
        self.assertNotIn("`proposal-only`", body)


class EconomyModeTests(unittest.TestCase):
    def test_threshold_is_two_members_low_or_medium(self):
        body = text()
        self.assertIn("**at most 2 members, every one `low` or `medium`**", body)
        self.assertIn("runs without `quenching-specs:spec-orchestrator`", body)
        self.assertIn("3 or more members, or any `high`/`xhigh`", body)

    def test_pair_and_acceptance_rules_are_cited_not_restated(self):
        body = text()
        self.assertIn("`quenching-specs:spec-runner` → `quenching-specs:spec-verifier`", body)
        self.assertIn("quenching/agents/spec-orchestrator.md", body)
        self.assertIn("acceptance only on a spec-verifier PASS", body)

    def test_launches_still_counted_and_no_new_grant(self):
        body = text()
        self.assertIn("Every launch counts in `launches`", body)
        head = AUTOPILOT.read_text(encoding="utf-8").split("---")[1]
        self.assertIn(
            "allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Bash(git:*), Bash, Read, Grep, Glob, Agent, Task, TaskStop, SendMessage",
            head,
        )

    def test_a_blocked_economy_worker_is_resumed_the_same_way(self):
        """Economy mode has no orchestrator, so the worker it launched is the one to resume:
        the rule names it, and step 5 never sends an answered question to the human epic."""
        body = text()
        self.assertIn("in economy mode, a `spec-runner`) returns `blocked` with `NOTE: "
                      "needs-human:", body)
        self.assertIn("answered inside the measured window, it goes back to the same agent by "
                      "`SendMessage`", body)


if __name__ == "__main__":
    unittest.main()
