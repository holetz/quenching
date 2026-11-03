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
        self.assertIn("the worktree cut proceeds on that authorization with the base still dirty",
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


class ResumeInsteadOfRelaunch(unittest.TestCase):
    """A `needs-human` decided in minutes goes back to the SAME agent with
    `SendMessage({to: <agentId>})`; the cold launch is the exception, named one by one, and a
    resume never counts as a launch."""

    @classmethod
    def setUpClass(cls):
        cls.body = text()

    def test_the_answered_needs_human_is_resumed_in_place(self):
        self.assertIn("A `needs-human:` already answered is RESUMED, not relaunched", self.body)
        self.assertIn("write the answer as a dated bullet in the epic's `## Design`", self.body)
        self.assertIn("`SendMessage({to: <agentId>})`", self.body)

    def test_the_window_is_measured_never_assumed(self):
        self.assertIn("The window is not a constant", self.body)
        self.assertIn("`cq components session cache --json`", self.body)
        self.assertIn("§The prompt cache is a per-harness measurement", self.body)

    def test_a_cold_relaunch_is_the_named_exception(self):
        for exception in ("for `budget:`", "no `SendMessage` in your grants",
                          "for an `agentId` lost",
                          "for a decision taken outside the measured window",
                          "for a decision that repeats one already in the epic's `## Design`"):
            self.assertIn(exception, self.body)

    def test_a_resume_is_not_a_launch(self):
        self.assertIn("A resume is not a launch", self.body)
        self.assertIn("it counts in `resumes:` of the round block and never in `launches`",
                      self.body)

    def test_step_5_hands_the_blocked_worker_to_the_same_agent(self):
        body = step(5)
        self.assertIn("takes the resume rule of the invariants", body)
        self.assertIn("it goes back to the same agent by `SendMessage`", body)


class BriefWithAStablePrefix(unittest.TestCase):
    """The fixed text opens the brief and the variables close it, so two prompts of the same
    type share a cacheable prefix. The gain between distinct agents is assumed, not measured
    here, and the body says so."""

    @classmethod
    def setUpClass(cls):
        cls.body = step(5)

    def test_the_fixed_text_opens_and_the_variables_close(self):
        self.assertIn("it OPENS with the fixed text every prompt of that type shares", self.body)
        self.assertIn("and CLOSES with the variables: the spec id, the worktree, the epic id and "
                      "the decision it carries", self.body)
        self.assertLess(self.body.index("it OPENS with the fixed text"),
                        self.body.index("and CLOSES with the variables"))

    def test_the_assumption_is_declared_and_names_its_measurement(self):
        self.assertIn("the gain BETWEEN distinct agents is ASSUMED, not measured in this "
                      "repository", self.body)
        self.assertIn("generations inside one agent", self.body)
        self.assertIn("`cq components session cache` is the measurement that would confirm or "
                      "refute it", self.body)

    def test_the_orchestrator_brief_is_ordered_the_same_way(self):
        self.assertIn("its brief ordered the same way", self.body)
        self.assertIn("the epic id, the base branch, the deadline and the decision last", self.body)


if __name__ == "__main__":
    unittest.main()
