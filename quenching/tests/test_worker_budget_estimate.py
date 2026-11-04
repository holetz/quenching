"""Contract: the worker budget is a size estimate; only the conductor budget stops a run.

The surfaces are prose, so the fixture pins the sentences that bind them: the runner never returns
`budget:`, `execute` under `autonomous` prints the peak and carries on, and the orchestrator keeps
the between-wave stop the autopilot relaunches.
"""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "quenching/agents/spec-runner.md"
ORCHESTRATOR = ROOT / "quenching/agents/spec-orchestrator.md"
SPECS = ROOT / "quenching/skills/quenching-specs/references"
AUTOPILOT = SPECS / "autopilot.md"
STANDARD = ROOT / "docs/standards/automation/context-discipline.md"


def flat(path):
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))


class TheWorkerEstimateTests(unittest.TestCase):
    def test_runner_never_returns_a_budget_stop(self):
        runner = flat(RUNNER)

        self.assertIn("size estimate", runner)
        self.assertIn("It is not a stop limit", runner)
        self.assertNotIn("NOTE: budget:", runner)
        self.assertNotIn("budget stop", runner)

    def test_execute_autonomous_prints_the_peak_and_carries_on(self):
        body = flat(SPECS / "execute.md")
        step = body[body.index("h. **At a section boundary"):body.index("**Pause if:**")]

        self.assertIn("a worker's budget is a size estimate, not a stop limit", step)
        self.assertIn("**Under `autonomous`, exit 1 asks nothing and stops nothing**", step)
        self.assertIn("In a human-led run, exit 1 → ask once", step)


class TheConductorStopTests(unittest.TestCase):
    def test_orchestrator_keeps_the_between_wave_stop(self):
        orchestrator = flat(ORCHESTRATOR)

        self.assertIn("You stay under 150k tokens of context, and that number stops you", orchestrator)
        self.assertIn("NOTE: budget: <peak>/<budget> before wave <N>", orchestrator)
        self.assertNotIn("budget stop without progress", orchestrator)

    def test_autopilot_relaunches_the_conductor_note(self):
        autopilot = flat(AUTOPILOT)

        self.assertIn("A `budget:` continue is relaunched, not retried", autopilot)
        self.assertIn("its own conductor budget, measured between waves, never a worker's size estimate", autopilot)


class TheStandardTests(unittest.TestCase):
    def test_standard_reserves_the_stop_for_the_conductor(self):
        standard = flat(STANDARD)

        self.assertIn("The worker budget is a size estimate, not a stop limit", standard)
        self.assertIn("Only the conductor budget is enforced", standard)
        self.assertNotIn("Only the worker budget is enforced", standard)


if __name__ == "__main__":
    unittest.main()
