"""Under `autonomous` the `conclude` flow opens its own PR, and the runner reports its url.

Publication cannot depend on an orchestrator that may never exist: the same
`pr-create <id> autonomous` invocation the `low` path chains runs after the green gate, and the
`pr` record it stamps is what the runner returns on `PR:` and the orchestrator adopts on PASS.
Outside `autonomous` nothing changes — the handoff is named and never invoked.
"""
import pathlib
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
CONCLUDE = PLUGIN_ROOT / "skills" / "quenching-specs" / "references" / "conclude.md"
RUNNER = PLUGIN_ROOT / "agents" / "spec-runner.md"


class ConcludeAutonomous(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = " ".join(CONCLUDE.read_text(encoding="utf-8").split())

    def test_it_invokes_pr_create_with_the_autonomous_word(self):
        self.assertIn('Skill("quenching-git", "pr-create <id> autonomous")',
                      self.text)
        self.assertIn("**Under `autonomous` the run opens the PR itself, whatever the "
                      "complexity**", self.text)
        self.assertIn("`/quenching-git pr-create <id> autonomous` owns its own push",
                      self.text)

    def test_outside_autonomous_the_handoff_is_named_and_not_invoked(self):
        self.assertIn('Skill("quenching-git", "pr-create <id>")', self.text)
        self.assertIn("`low` chains the provider handoff", self.text)
        self.assertIn("name the handoff and stop", self.text)
        self.assertNotIn("stops at the named PR handoff", self.text,
                         "the autonomous run no longer stops before its own PR")

    def test_a_conflict_only_inside_a_generated_zone_is_mechanical(self):
        # the step 7 recipe and the table row both cover the generated zones, not only the mirrors
        self.assertIn("A conflict only inside a generated zone", self.text)
        self.assertIn("§Enumerated generated zones", self.text)
        self.assertIn("`cq proof readme --write`", self.text)
        self.assertIn("`git merge-file --theirs <ours> <base> <theirs>`", self.text)
        self.assertIn("every conflict marker of the file sits between the zone's delimiters",
                      self.text)
        self.assertIn("a conflict only in the deployed surface or inside a generated zone",
                      self.text)


class RunnerReportsThePrRecord(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = " ".join(RUNNER.read_text(encoding="utf-8").split())

    def test_the_report_line_names_the_pr_record(self):
        self.assertIn("PR: <the url of the spec's `pr` record, or ->", self.text)

    def test_the_runner_adopts_rather_than_opens_a_second(self):
        self.assertIn("the `conclude` you invoke does it through "
                      "`/quenching-git pr-create <id> autonomous`", self.text)
        self.assertIn("the `spec-orchestrator` ADOPTS that PR after the `spec-verifier` PASS "
                      "instead of opening a second", self.text)


if __name__ == "__main__":
    unittest.main()
