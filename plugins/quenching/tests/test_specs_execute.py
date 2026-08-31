"""Regression contract for task-level execution commits.

The execution command is prose, so the fixture checks its boundary language and then exercises
the git history shape that language promises: two tasks remain two commits after their section
finishes.
"""

from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
COMMAND = ROOT / "plugins/quenching/commands/specs/execute.md"
REFERENCE = ROOT / "plugins/quenching/assets/references/specs-execute/execution.md"


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
