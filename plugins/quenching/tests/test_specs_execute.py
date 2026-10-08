"""Regression contract for task-level execution commits.

The execution command is prose, so the fixture checks its boundary language and then exercises
the git history shape that language promises: two tasks remain two commits after their section
finishes.
"""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
COMMAND = ROOT / "plugins/quenching/commands/specs/execute.md"
REFERENCE = ROOT / "plugins/quenching/assets/references/specs-execute/execution.md"
CONCLUDE = ROOT / "plugins/quenching/commands/specs/conclude.md"
SCALE = ROOT / "plugins/quenching/assets/references/specs-develop/spec-driven.md"


def git(cwd, *args):
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()


class TaskExecutionContractTests(unittest.TestCase):
    def test_execute_commits_through_the_deterministic_verb(self):
        command = COMMAND.read_text(encoding="utf-8")
        commit = (ROOT / "plugins/quenching/commands/git/commit.md").read_text(encoding="utf-8")

        self.assertIn('cq git commit --subject "<subject>"', command)
        self.assertNotIn('Skill("quenching:git:commit"', command)
        self.assertIn("single commit boundary", commit)
        self.assertNotIn("git commit -m", command)
        self.assertNotIn('--subject "plan/<id>-<handle>', command)

    def test_external_backend_records_task_after_the_commit(self):
        command = COMMAND.read_text(encoding="utf-8")
        reference = REFERENCE.read_text(encoding="utf-8")

        self.assertLess(command.index("git add <the task's declared files>"),
                        command.index('cq git commit --subject "<subject>"'))
        self.assertLess(command.index('cq git commit --subject "<subject>"'),
                        command.index("cq specs task --check <task-id>"))
        self.assertIn('--commit "<sha reported by cq git commit>"', command)
        self.assertIn("spec tick **fails**", reference)
        self.assertIn("preserve the commit", reference)
        self.assertNotIn("<the spec file>", reference)

    def test_execute_runs_enabled_hooks_and_reports_optional_failures(self):
        command = COMMAND.read_text(encoding="utf-8")
        config = json.loads((ROOT / ".agents" / "quenching.json").read_text(encoding="utf-8"))

        self.assertIn('Skill("<declared hook command>",', command)
        self.assertIn("optional: true", command)
        self.assertIn("condition", command)
        self.assertIn("enabled: false", command)
        self.assertIn("An optional hook failure is reported", command)
        self.assertIn("git remote set-head origin -a", command)
        self.assertIn("make `refs/remotes/origin/HEAD` resolve", command)
        self.assertIn("Name the work checkout and the diff in that context", command)
        self.assertIn("git -C <toplevel> diff", command)
        hooks = config["shared"]["hooks"]["after_specs_execute_task"]
        self.assertEqual([h["command"] for h in hooks], ["/security-review"])
        self.assertTrue(hooks[0]["optional"])
        self.assertTrue(hooks[0]["condition"])
        self.assertIn("unresolved", command)

    def test_low_gear_chains_conclude_to_the_provider_pr_skill(self):
        conclude = CONCLUDE.read_text(encoding="utf-8")
        scale = SCALE.read_text(encoding="utf-8")

        self.assertIn('Skill("quenching:git:pr:create", "<id>")', conclude)
        self.assertIn("`low` chains the provider handoff", conclude)
        self.assertNotIn('"<id> autonomous")', conclude)
        self.assertIn("do not invoke it", conclude)
        self.assertIn('Skill("quenching:git:pr:create", "<id>")', scale)
        self.assertIn("The other levels retain", scale)

    def test_explicit_subject_commits_only_staged_files(self):
        with tempfile.TemporaryDirectory() as directory:
            git(directory, "init", "-q", "-b", "main")
            git(directory, "config", "user.email", "execute-check@example.invalid")
            git(directory, "config", "user.name", "task execution check")
            Path(directory, "README.md").write_text("seed\n", encoding="utf-8")
            git(directory, "add", "README.md")
            git(directory, "commit", "-qm", "seed")

            Path(directory, "staged.txt").write_text("staged\n", encoding="utf-8")
            Path(directory, "unstaged.txt").write_text("unstaged\n", encoding="utf-8")
            git(directory, "add", "staged.txt")
            git(directory, "commit", "-qm", "explicit subject wins")

            self.assertEqual(git(directory, "log", "-1", "--format=%s"),
                             "explicit subject wins")
            self.assertEqual(git(directory, "show", "--format=", "--name-only", "HEAD"),
                             "staged.txt")
            self.assertEqual(git(directory, "status", "--short"), "?? unstaged.txt")

    def test_boundary_keeps_each_task_commit_and_has_no_reset_contract(self):
        command = COMMAND.read_text(encoding="utf-8").lower()
        reference = REFERENCE.read_text(encoding="utf-8").lower()

        for text in (command, reference):
            self.assertNotIn("section squash", text)
            self.assertNotIn("git reset --soft", text)
            self.assertNotIn("re-stamped onto the section", text)
        self.assertIn("keep the task commits", command)
        self.assertIn("one per task", reference)

        with tempfile.TemporaryDirectory() as directory:
            git(directory, "init", "-q", "-b", "main")
            git(directory, "config", "user.email", "execute-check@example.invalid")
            git(directory, "config", "user.name", "task execution check")
            Path(directory, "README.md").write_text("seed\n", encoding="utf-8")
            git(directory, "add", "README.md")
            git(directory, "commit", "-qm", "seed")
            base = git(directory, "rev-parse", "HEAD")

            for filename, subject in (
                ("task-one.txt", "plan/x: 1.1 first task"),
                ("task-two.txt", "plan/x: 1.2 second task"),
            ):
                Path(directory, filename).write_text(filename + "\n", encoding="utf-8")
                git(directory, "add", filename)
                git(directory, "commit", "-qm", subject)

            self.assertEqual(git(directory, "rev-list", "--count", f"{base}..HEAD"), "2")
            subjects = git(directory, "log", "--format=%s", f"{base}..HEAD").splitlines()
            self.assertEqual(
                subjects,
                ["plan/x: 1.2 second task", "plan/x: 1.1 first task"],
            )


if __name__ == "__main__":
    unittest.main()
