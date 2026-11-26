"""Contract: a session the harness already isolated adopts that worktree instead of cutting one.

The prose is the product here — the runner and the orchestrator are read by a model, not by
a parser — so each assertion normalizes whitespace and markup first and then looks for the
rule, never for a layout."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]


def text(rel):
    body = (ROOT / rel).read_text(encoding="utf-8")
    return re.sub(r"\s+", " ", body).replace("`", "")


class TheRunnerAdopts(unittest.TestCase):
    def test_the_runner_checks_for_a_linked_worktree_before_cutting(self):
        body = text("quenching/agents/spec-runner.md")
        self.assertIn("git rev-parse --git-dir", body)
        self.assertIn("git rev-parse --git-common-dir", body)
        self.assertIn("cq git worktree adopt --json", body)
        self.assertIn("never cut a second worktree", body)

    def test_a_slot_is_used_as_it_stands_and_is_never_cut_again(self):
        body = text("quenching/agents/spec-runner.md")
        self.assertIn("git-worktree-slot", body)
        self.assertIn("use it as it stands", body)


class TheOrchestratorAdopts(unittest.TestCase):
    def test_the_orchestrator_asks_adopt_at_the_open(self):
        body = text("quenching/agents/spec-orchestrator.md")
        self.assertIn("cq git worktree adopt --json", body)
        self.assertIn("one worker at a time", body)
        self.assertIn("Bash(cq git worktree adopt:*)", body)

    def test_the_adopted_path_is_named_in_every_worker_prompt(self):
        body = text("quenching/agents/spec-orchestrator.md")
        self.assertIn("the worktree the adoption above reported", body)
        self.assertIn("names that path instead of none", body)



class TheDoctrine(unittest.TestCase):
    def test_the_isolation_reference_names_adoption_and_its_two_sources(self):
        body = text("quenching/references/git/isolation.md")
        self.assertIn("A worktree the harness cut is adopted, never cut again", body)
        self.assertIn("cq git worktree adopt", body)
        self.assertIn("sharedPaths", body)
        self.assertIn("shared.regenerablePaths", body)
        self.assertIn("never overwriting a path already present", body)

    def test_the_manual_recommends_new_worktree_and_the_hook(self):
        body = text("quenching/README.md")
        self.assertIn("New Worktree", body)
        self.assertIn("cq git worktree adopt", body)
        self.assertIn("never cuts a second one", body)
        self.assertNotIn("Open a Copilot session with Branch isolation, not", body)

class TheHookStandard(unittest.TestCase):
    def test_hooks_md_declares_the_session_start_adoption_at_rung_4(self):
        body = text("docs/standards/automation/hooks.md")
        self.assertIn("adopt-worktree", body)
        self.assertIn("rung-4", body)
        self.assertIn("SessionStart", body)
        self.assertIn("discards the answer", body)
        self.assertIn("zero tokens", body)

    def test_a_session_start_adoption_is_not_a_worktree_create(self):
        body = text("docs/standards/automation/hooks.md")
        self.assertIn("A SessionStart hook is not a WorktreeCreate", body)
        self.assertIn("it cuts nothing and takes no slot", body)


class TheSetupStandard(unittest.TestCase):
    def test_adopt_and_the_copilot_setup_are_the_preparation_entry_points(self):
        body = text("docs/standards/workflows/worktree-setup.md")
        self.assertIn("cq git worktree adopt", body)
        self.assertIn("once per worktree the harness cut", body)
        self.assertIn("copilot-setup-steps.yml", body)
        self.assertIn("No other entry point exists", body)

    def test_the_adopted_tree_shares_the_declared_regenerable_directories(self):
        body = text("docs/standards/workflows/worktree-setup.md")
        self.assertIn("shared.regenerablePaths", body)
        self.assertIn("shares the primary's", body)
        self.assertIn("never replaced", body)


if __name__ == "__main__":
    unittest.main()
