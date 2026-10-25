"""Executable proofs for the guard's watch on the base checkout and the primary branch ref.

Real throwaway git repositories: a base checkout on `main` and a linked worktree, which is the
reviewed one. A fast-forward of the base is accepted; a rewind, a branch switch, a detached base
`HEAD` and a removed primary ref are barred.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.codex.guard import GuardError, base_moves, base_state

ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
       "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": os.devnull}


def git(cwd: str, *args: str) -> str:
    return subprocess.run(["git", "-C", cwd, *args], check=True, capture_output=True, text=True,
                          env=ENV).stdout.strip()


class BaseGuard(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = os.path.realpath(os.path.join(tmp.name, "base"))
        self.work = os.path.join(os.path.realpath(tmp.name), "work")
        os.makedirs(self.base)
        git(self.base, "init", "-q", "-b", "main")
        for n in "123":
            self.commit(n)
        git(self.base, "worktree", "add", "-q", "-b", "side", self.work)
        self.first = git(self.base, "rev-parse", "main~2")
        self.before = base_state(self.work)

    def commit(self, name: str) -> None:
        pathlib.Path(self.base, name).write_text(name)
        git(self.base, "add", name)
        git(self.base, "commit", "-qm", name)

    def moves(self) -> list[str]:
        return base_moves(self.work, self.before, base_state(self.work, self.before["primary"]))

    def test_reads_the_base_checkout_and_primary_ref(self):
        self.assertEqual(self.before["path"], self.base)
        self.assertEqual(self.before["primary"], "refs/heads/main")
        self.assertEqual(self.before["branch"], "refs/heads/main")
        self.assertEqual(self.before["head"], self.before["primaryRef"])

    def test_unchanged_is_accepted(self):
        self.assertEqual(self.moves(), [])

    def test_fast_forward_is_accepted(self):
        self.commit("4")
        self.assertNotEqual(base_state(self.work)["head"], self.before["head"])
        self.assertEqual(self.moves(), [])

    def test_reset_backwards_is_barred(self):
        git(self.base, "reset", "-q", "--hard", self.first)
        self.assertEqual(self.moves(), ["base HEAD rewound", "primary ref rewound"])

    def test_branch_force_to_a_non_descendant_is_barred(self):
        git(self.base, "checkout", "-q", "--detach")
        orphan = git(self.base, "commit-tree", "-m", "orphan", git(self.base, "write-tree"))
        git(self.base, "branch", "-f", "main", orphan)
        self.assertIn("primary ref rewound", self.moves())

    def test_branch_switch_is_barred(self):
        git(self.base, "checkout", "-q", "-b", "other")
        self.assertEqual(self.moves(), ["base branch switched"])

    def test_detached_base_head_is_barred(self):
        git(self.base, "checkout", "-q", "--detach")
        self.assertEqual(self.moves(), ["base HEAD detached"])

    def test_removed_primary_ref_is_barred(self):
        git(self.base, "checkout", "-q", "--detach")
        git(self.base, "branch", "-D", "main")
        self.assertIn("primary ref removed", self.moves())

    def test_other_worktrees_head_is_not_watched(self):
        pathlib.Path(self.work, "y").write_text("y")
        git(self.work, "add", "y")
        git(self.work, "commit", "-qm", "y")
        git(self.work, "reset", "-q", "--hard", "HEAD~1")
        self.assertEqual(self.moves(), [])

    def test_unreadable_git_fails_closed(self):
        with self.assertRaises(GuardError):
            base_state(os.path.join(self.base, "missing"))


if __name__ == "__main__":
    unittest.main()
