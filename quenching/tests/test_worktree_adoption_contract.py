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


if __name__ == "__main__":
    unittest.main()
