"""Locks the post-merge step that archives a done spec and retires its worktree (text contract)."""
from __future__ import annotations

import pathlib
import unittest

CONCLUDE = (pathlib.Path(__file__).resolve().parent.parent / "skills" / "quenching-specs" / "references" / "conclude.md").read_text()


def step(number: int) -> str:
    """The flow's step `number`, on one line, so assertions never depend on the wrap."""
    start = CONCLUDE.index(f"### {number}. ")
    try:
        end = CONCLUDE.index(f"### {number + 1}. ", start)
    except ValueError:
        end = len(CONCLUDE)
    return " ".join(CONCLUDE[start:end].split())


class ConcludeRetiresTheWorktree(unittest.TestCase):
    def test_step_eight_calls_the_existing_retire_verb_from_the_base_checkout(self):
        text = step(8)
        self.assertIn("Then retire the spec's worktree", text)
        self.assertIn("cd <the base's checkout> && .agents/quenching/bin/cq git worktree retire", text)
        self.assertIn("--branch <branch.work> --base <branch.base>", text)

    def test_the_step_never_forces_and_reports_a_refusal(self):
        text = step(8)
        self.assertIn("Never pass `--force` or `--discard-ignored`", text)
        self.assertIn("A refusal is information, not an obstacle", text)
        self.assertNotIn("retire --force", text)

    def test_it_adds_no_removal_logic_and_asks_nothing_under_autonomous(self):
        self.assertIn("this step adds none of its own", step(8))
        autonomous = CONCLUDE[CONCLUDE.index("## Under `autonomous`"):CONCLUDE.index("## Workflow")]
        self.assertIn("the post-merge close", autonomous)
        self.assertIn("never forced", autonomous)

    def test_the_resumed_already_merged_row_points_at_the_step(self):
        row = next(line for line in CONCLUDE.splitlines() if line.startswith("| already merged"))
        self.assertIn("run only step 8, the post-merge close", row)

    def test_the_abandoned_path_still_removes_no_worktree(self):
        self.assertIn("do not remove any worktree", step(7))


if __name__ == "__main__":
    unittest.main()
