"""Executable-prose contracts keep the estimate out of approval and the build cost measured at conclude."""
from pathlib import Path
import re
import unittest


PLUGIN = Path(__file__).resolve().parents[1]


def prose(path):
    return re.sub(r"\s+", " ", (PLUGIN / path).read_text().replace("**", "").replace("`", ""))


class BuildSizeApproval(unittest.TestCase):
    def test_develop_runs_no_size_check_before_approval(self):
        text = prose("skills/quenching-specs/references/develop.md")
        close = text[text.index("### 8. Close"):]
        self.assertIn("No size check runs before approval", close)
        for marker in ("overBudget", "workerBudgetTokens", "STATE: blocked", "needs-human: <budget"):
            self.assertNotIn(marker, close)

    def test_shared_approval_rule_never_gates_on_a_budget(self):
        text = prose("references/specs-develop/questions.md")
        close = text[text.index("## Approval —"):text.index("## Gathering the evidence")]
        self.assertIn("No token-budget check precedes approval", close)
        for marker in ("overBudget", "No automatic approval", "Decompose", "size check"):
            self.assertNotIn(marker, close)

    def test_manual_describes_a_heuristic_without_guaranteeing_fit(self):
        text = prose("README.md")
        for marker in ("cq specs estimate", "bytes / 4", "200000", "never proves", "unresolved"):
            self.assertIn(marker, text)


class ObservedCostAtConclude(unittest.TestCase):
    def test_measurement_precedes_archive_and_has_explicit_build_scope(self):
        text = prose("skills/quenching-specs/references/conclude.md")
        step = text[text.index("### 4. Write"):text.index("### 5. Distil")]
        self.assertLess(step.index("cq components session cost"), step.index("cq specs promote"))
        self.assertNotIn("cq session cost", text)
        for marker in ("buildCost", "build-only", "explicit", "per model", "maxRequestExposureTokens",
                       "unavailable", "Codex", "Never infer", "provenance", "never a context peak"):
            self.assertIn(marker, step)
        self.assertIn("measurements=", step)
        self.assertIn("status=unavailable", step)


if __name__ == "__main__":
    unittest.main()
