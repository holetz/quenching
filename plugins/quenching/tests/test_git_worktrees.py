"""`quenching.git.worktrees` — worktrees read from files, against a real throwaway repository."""
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.git.worktrees import list_worktrees, session_slug, with_slugs


def _git(cwd, *args):
    subprocess.run(["git", "-C", cwd, "-c", "user.name=t", "-c", "user.email=t@t", *args],
                   check=True, capture_output=True)


class ListWorktreesTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = os.path.realpath(tmp.name)
        self.main = os.path.join(self.base, "repo")
        os.mkdir(self.main)
        _git(self.main, "init", "-q", "-b", "main")
        _git(self.main, "commit", "-q", "--allow-empty", "-m", "init")
        self.plain = os.path.join(self.base, "wt-plain")
        self.dotted = os.path.join(self.base, "wt.dotted")
        _git(self.main, "worktree", "add", "-q", "-b", "feat-a", self.plain)
        _git(self.main, "worktree", "add", "-q", "--detach", self.dotted)

    def _rows(self, root):
        with mock.patch("subprocess.run", side_effect=AssertionError("process opened")), \
             mock.patch("subprocess.Popen", side_effect=AssertionError("process opened")):
            return list_worktrees(root)

    def test_lists_main_first_then_linked_without_a_process(self):
        self.assertEqual(self._rows(self.main), [
            {"path": self.main, "branch": "main", "main": True},
            {"path": self.plain, "branch": "feat-a", "main": False},
            {"path": self.dotted, "branch": None, "main": False},
        ])

    def test_a_linked_root_sees_the_same_set(self):
        self.assertEqual(self._rows(self.plain), self._rows(self.main))

    def test_a_removed_directory_is_skipped(self):
        subprocess.run(["rm", "-rf", self.plain], check=True)
        self.assertNotIn(self.plain, [row["path"] for row in self._rows(self.main)])

    def test_a_subdirectory_resolves_to_the_enclosing_checkout(self):
        sub = os.path.join(self.main, "plugins", "deep")
        os.makedirs(sub)
        self.assertEqual(self._rows(sub), self._rows(self.main))
        nested = os.path.join(self.plain, "x")
        os.mkdir(nested)
        self.assertEqual(self._rows(nested), self._rows(self.main))

    def test_separate_git_dir_names_the_checkout_not_the_store_parent(self):
        meta = os.path.join(self.base, "meta")
        os.mkdir(meta)
        repo = os.path.join(self.base, "sep")
        _git(self.base, "init", "-q", "-b", "main", "--separate-git-dir",
             os.path.join(meta, "store.git"), repo)
        self.assertEqual(self._rows(repo), [{"path": repo, "branch": "main", "main": True}])
        sub = os.path.join(repo, "a")
        os.mkdir(sub)
        self.assertEqual(self._rows(sub), self._rows(repo))

    def test_a_relative_gitdir_pointer_resolves_against_its_own_file(self):
        entry = os.path.join(self.main, ".git", "worktrees", "wt-plain")
        with open(os.path.join(entry, "gitdir"), "w", encoding="utf-8") as stream:
            stream.write("../../../../wt-plain/.git\n")
        expected = self._rows(self.main)
        self.assertIn(self.plain, [row["path"] for row in expected])
        for cwd in ("/", entry):
            before = os.getcwd()
            os.chdir(cwd)
            try:
                self.assertEqual(self._rows(self.main), expected)
            finally:
                os.chdir(before)

    def test_not_a_repository_is_empty(self):
        self.assertEqual(list_worktrees(self.base), [])

    def test_slug_encodes_dots_and_slashes(self):
        self.assertEqual(session_slug("/a/b.c/d"), "-a-b-c-d")
        rows = with_slugs(self._rows(self.main))
        slug = next(row["slug"] for row in rows if row["path"] == self.dotted)
        self.assertNotIn(".", slug)
        self.assertNotIn("/", slug)


if __name__ == "__main__":
    unittest.main()
