"""Contract for the orchestrator's stop between waves and the autopilot's opt-in tree-token ceiling."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
AUTOPILOT = ROOT / "plugins/quenching/commands/specs/autopilot.md"
ORCHESTRATOR = ROOT / "plugins/quenching/agents/orchestrator.md"


def text(path):
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))


class OrchestratorBudgetTests(unittest.TestCase):
    def test_grant_is_exactly_the_context_verb(self):
        head = ORCHESTRATOR.read_text(encoding="utf-8").split("---")[1]
        self.assertIn("Bash(cq components session context:*)", head)

    def test_stops_between_waves_and_returns_budget_continue(self):
        body = text(ORCHESTRATOR)
        self.assertIn("session context --self orchestrator-", body)
        self.assertIn("a stop is never mid-wave", body)
        self.assertIn("NOTE: budget: <peak>/<budget> before wave <N>", body)
        self.assertIn("exit 2 (not measured) never stops the run", body)


class AutopilotTreeCeilingTests(unittest.TestCase):
    def test_flag_is_opt_in_without_default(self):
        body = text(AUTOPILOT)
        self.assertIn("[--max-tree-tokens <n>]", body)
        self.assertIn("with **no default**", body)
        self.assertIn("without it nothing is read or compared", body)

    def test_ceiling_is_per_model_from_by_model(self):
        body = text(AUTOPILOT)
        self.assertIn("`input + cacheRead + cacheWrite + output`", body)
        self.assertIn("never summing tiers", body)
        self.assertIn("cq components session cost", body)

    def test_budget_continue_is_relaunched_with_progress(self):
        body = text(AUTOPILOT)
        self.assertIn("is relaunched, not retried", body)
        self.assertIn("is not a failure, but needs progress", body)
        self.assertIn("`needs-human`", body)

    def test_allowed_tools_not_widened(self):
        head = AUTOPILOT.read_text(encoding="utf-8").split("---")[1]
        self.assertIn(
            "allowed-tools: Bash(cq:*), Bash(git:*), Bash, Read, Grep, Glob, Agent, Task, TaskStop",
            head,
        )


if __name__ == "__main__":
    unittest.main()
