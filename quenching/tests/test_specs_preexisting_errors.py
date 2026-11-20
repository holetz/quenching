"""Regression contract for the pre-existing error policy.

The policy is prose spread over the standard, the flows and the agents, so each surface is
checked for the same three commitments: proof on the base, a declared `[fix-preexistente]` task
or a captured spec, and a bar that never drops.
"""

from pathlib import Path
import unittest

import _paths  # noqa: F401

ROOT = Path(__file__).resolve().parents[2]
STANDARD = ROOT / "docs/standards/workflows/task-execution.md"
LIFECYCLE = ROOT / "docs/standards/workflows/plan-lifecycle.md"
EXECUTE = ROOT / "quenching/skills/quenching-specs/references/execute.md"
CONCLUDE = ROOT / "quenching/skills/quenching-specs/references/conclude.md"
RUNNER = ROOT / "quenching/agents/spec-runner.md"
VERIFIER = ROOT / "quenching/agents/spec-verifier.md"
ORCHESTRATOR = ROOT / "quenching/agents/spec-orchestrator.md"


def read(path):
    return path.read_text(encoding="utf-8")


class PreexistingErrorsTests(unittest.TestCase):
    def test_standard_carries_proof_criteria_and_capture(self):
        text = read(STANDARD)
        self.assertIn("### Pre-existing errors", text)
        for phrase in (
            "proves",
            ".quenching/red",
            "four criteria hold together",
            "[fix-preexistente]",
            "promoted: <id>",
            "The bar does not drop",
        ):
            self.assertIn(phrase, text, phrase)

    def test_lifecycle_names_the_exception(self):
        text = read(LIFECYCLE)
        self.assertIn("pre-existing error", text)
        self.assertIn("promoted: <id>", text)

    def test_flows_route_a_foreign_red(self):
        for path in (EXECUTE, CONCLUDE, RUNNER):
            text = read(path)
            self.assertIn("fix-preexistente", text, path.name)
            self.assertIn("promoted: <id>", text, path.name)
            self.assertIn(".quenching/red", text, path.name)

    def test_no_surface_authorizes_lowering_the_bar(self):
        for path in (EXECUTE, CONCLUDE, RUNNER):
            text = read(path)
            self.assertIn("xfail", text, path.name)
            self.assertIn("--no-verify", text.replace("`--no-verify`", "--no-verify"), path.name)

    def test_verifier_fails_suppression_in_a_fix_task(self):
        text = read(VERIFIER)
        self.assertIn("[fix-preexistente]", text)
        self.assertIn("is FAIL", text)

    def test_orchestrator_names_the_capturing_spec(self):
        text = read(ORCHESTRATOR)
        self.assertIn("pre-existing", text)
        self.assertIn("BASE-RED", text)


if __name__ == "__main__":
    unittest.main()
