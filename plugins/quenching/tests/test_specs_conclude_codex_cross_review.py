"""Locks the Codex cross-review rules in conclude step 2 (text contract)."""
from __future__ import annotations

import pathlib
import unittest

CONCLUDE = (pathlib.Path(__file__).resolve().parent.parent / "commands" / "specs" / "conclude.md").read_text()


def step2() -> str:
    start = CONCLUDE.index("### 2. Review the whole branch diff")
    return CONCLUDE[start:CONCLUDE.index("### 3.", start)]


class ConcludeCodexCrossReview(unittest.TestCase):
    def test_probe_then_review_in_step_two(self):
        text = step2()
        self.assertIn("cq codex probe --json", text)
        self.assertIn("cq codex review --worktree", text)

    def test_fallback_is_reported_and_never_blocks(self):
        text = step2()
        self.assertIn("Codex: fallback (<reason>)", text)
        self.assertIn("never blocks `reviewed`", text)

    def test_codex_only_findings_need_reproduction(self):
        text = step2()
        self.assertIn("only Codex", text)
        self.assertIn("reproduced", text)

    def test_autonomous_row_exists(self):
        self.assertIn("| Step 2 — the Codex review |", CONCLUDE)


if __name__ == "__main__":
    unittest.main()
