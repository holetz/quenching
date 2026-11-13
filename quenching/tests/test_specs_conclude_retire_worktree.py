"""Locks the conclude step that retires a done spec's worktree after the merge (text contract)."""
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
    def test_step_seven_calls_the_existing_retire_verb_from_the_base_checkout(self):
        text = step(7)
        self.assertIn("retire the spec's worktree once the merge is confirmed", text)
        self.assertIn("cd <the base's checkout> && .agents/quenching/bin/cq git worktree retire", text)
        self.assertIn("--branch <branch.work> --base <branch.base>", text)

    def test_the_step_never_forces_and_reports_a_refusal(self):
        text = step(7)
        self.assertIn("Never pass `--force` or `--discard-ignored`", text)
        self.assertIn("A refusal is information, not an obstacle", text)
        self.assertIn("git-worktree-retire-not-merged", text)
        self.assertNotIn("retire --force", text)

    def test_it_adds_no_removal_logic_and_asks_nothing_under_autonomous(self):
        self.assertIn("this step adds no removal logic of its own", step(7))
        autonomous = CONCLUDE[CONCLUDE.index("## Under `autonomous`"):CONCLUDE.index("## Workflow")]
        self.assertIn("retiring the worktree of a `done` spec", autonomous)
        self.assertIn("never forced", autonomous)

    def test_the_resumed_already_merged_row_points_at_the_step(self):
        row = next(line for line in CONCLUDE.splitlines() if line.startswith("| already merged"))
        self.assertIn("retiring the worktree (step 7)", row)

    def test_the_abandoned_path_still_removes_no_worktree(self):
        self.assertIn("do not remove any worktree", step(7))


if __name__ == "__main__":
    unittest.main()
