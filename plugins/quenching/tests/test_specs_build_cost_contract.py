"""Executable-prose contracts keep the estimate ahead of approval and decomposition gated."""
from pathlib import Path
import re
import unittest


PLUGIN = Path(__file__).resolve().parents[1]


def prose(path):
    return re.sub(r"\s+", " ", (PLUGIN / path).read_text().replace("**", "").replace("`", ""))


class BuildSizeApproval(unittest.TestCase):
    def test_develop_checks_estimate_before_either_approval_route(self):
        text = prose("commands/specs/develop.md")
        close = text[text.index("### 8. Close"):]
        self.assertLess(close.index("cq specs estimate"), close.index("stamp it here"))
        for marker in ("overBudget", "workerBudgetTokens", "forced low", "STATE: blocked",
                       "spec-architect", "proposal-only", "never proves the full build fits"):
            self.assertIn(marker, close)

    def test_shared_approval_rule_covers_low_and_estimate_uncertainty(self):
        text = prose("assets/references/specs-develop/questions.md")
        close = text[text.index("## Approval —"):text.index("## Gathering the evidence")]
        for marker in ("overBudget", "No automatic approval", "forced low", "unknown inputs",
                       "complexity", "explicitly accept", "spec-architect"):
            self.assertIn(marker, close)

    def test_architect_proposal_has_no_write_and_capture_requires_authorization(self):
        text = prose("agents/spec-architect.md")
        for marker in ("proposal-only", "Do not create", "explicit authorization", "worker budget",
                       "original problem", "Do not develop, approve or execute"):
            self.assertIn(marker, text)

    def test_manual_describes_a_heuristic_without_guaranteeing_fit(self):
        text = prose("README.md")
        for marker in ("cq specs estimate", "bytes / 4", "100000", "never proves", "unresolved"):
            self.assertIn(marker, text)


class ObservedCostAtConclude(unittest.TestCase):
    def test_measurement_precedes_archive_and_has_explicit_build_scope(self):
        text = prose("commands/specs/conclude.md")
        step = text[text.index("### 4. Write"):text.index("### 5. Distil")]
        self.assertLess(step.index("cq session cost"), step.index("cq specs promote"))
        for marker in ("buildCost", "build-only", "explicit", "per model", "maxRequestExposureTokens",
                       "unavailable", "Codex", "Never infer", "provenance", "never a context peak"):
            self.assertIn(marker, step)
        self.assertIn("measurements=", step)
        self.assertIn("status=unavailable", step)


if __name__ == "__main__":
    unittest.main()
