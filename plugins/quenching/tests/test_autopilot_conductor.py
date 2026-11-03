"""Contract for the autopilot conductor: the dirty base it decides at step 1, the decisions it
persists in the epic's `## Design` before the launch that depends on them, and the resume it
chooses instead of a cold relaunch."""

import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
AUTOPILOT = ROOT / "plugins/quenching/commands/specs/autopilot.md"


def text() -> str:
    return re.sub(r"\s+", " ", AUTOPILOT.read_text(encoding="utf-8"))


def step(number: int) -> str:
    """One `### N.` block, so an assertion cannot pass on another step's prose."""
    body = text()
    start = body.index(f"### {number}. ")
    following = body.find(f"### {number + 1}. ", start)
    return body[start:] if following == -1 else body[start:following]


class DirtyBaseDecision(unittest.TestCase):
    """The base checkout's dirt is decided at step 1 — the round that discovered it at the
    first worktree cut spent a whole runner to learn it."""

    def test_step_1_decides_the_dirty_base_before_the_first_cut(self):
        body = step(1)
        self.assertIn("A dirty checkout is decided HERE, never discovered at the first worktree "
                      "cut", body)
        self.assertIn("it is the human's work, an upgrade or a fix in progress", body)
        self.assertIn("a path that appeared after the round opened is this run's", body)

    def test_the_two_authorized_answers_and_the_stop(self):
        body = step(1)
        self.assertIn("when a new spec is permitted, the fix spec above absorbs it", body)
        self.assertIn("every worktree of the round is cut from `origin/<base>`, which never "
                      "carries the base's uncommitted files", body)
        self.assertIn("`cq git branch` accepts that authorized cut with the base still dirty",
                      body)
        self.assertIn("With neither answer the round stops before its first launch", body)
        self.assertIn("`dirty: <n> path(s) — <fix spec|cut from origin/<base>>`", body)


class DecisionsPersistedInTheDesign(unittest.TestCase):
    """A decision that lives only in a brief dies with the relaunch: it is written in the
    epic's `## Design`, dated, before the launch that depends on it."""

    def test_step_4_appends_to_the_design_and_never_rewrites_it(self):
        body = step(4)
        self.assertIn("a READ, AN APPEND AND ONE WRITE", body)
        self.assertIn("`cq specs section --write` REPLACES the section", body)

    def test_every_delegated_decision_is_written_before_the_launch_it_governs(self):
        body = step(4)
        self.assertIn("every decision this session took as the delegated owner", body)
        self.assertIn("written BEFORE the launch that depends on it", body)
        self.assertIn("A decision that lives only in a brief is lost at the next relaunch", body)
        self.assertIn("the briefs of steps 5 and 6 name the composite and the bullet instead of "
                      "restating it", body)


if __name__ == "__main__":
    unittest.main()
