"""`quenching.common.paths` — the one normalisation every consumer of `files:` compares through."""
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
from quenching.common.config import find_repo_root
from quenching.common.paths import escapes_repo, native_path, repo_path


class NativePath(unittest.TestCase):
    def test_a_git_path_on_windows_takes_the_backslash_form(self):
        self.assertEqual(native_path("C:/Users/x/repo-slot-1", windows=True),
                         "C:\\Users\\x\\repo-slot-1")
        self.assertEqual(native_path("C:\\Users\\x", windows=True), "C:\\Users\\x")

    def test_posix_is_identity(self):
        for path in ("/home/x/repo", "/home//x/../y", ""):
            self.assertEqual(native_path(path, windows=False), path)

    def test_an_empty_answer_stays_empty(self):
        self.assertEqual(native_path("", windows=True), "")

    def test_the_repository_root_git_reports_is_the_one_os_path_builds(self):
        # a root without a config file comes from `rev-parse --show-toplevel`, which prints `/`
        # on Windows; the backend cache and every `os.path.join` key on this exact string
        with tempfile.TemporaryDirectory() as tmp:
            root = os.path.realpath(tmp)
            subprocess.run(["git", "init", "-q", root], check=True)
            nested = os.path.join(root, "a", "b")
            os.makedirs(nested)
            self.assertEqual(find_repo_root(nested), root)

    def test_two_repositories_in_one_process_each_get_their_own_top(self):
        # the MCP server is one live process serving many `--root`s: the `_TOPLEVEL` cache is a
        # directory → native top map, never one value for the whole process
        with tempfile.TemporaryDirectory() as tmp:
            tops = [os.path.join(os.path.realpath(tmp), name) for name in ("one", "two")]
            for top in tops:
                subprocess.run(["git", "init", "-q", top], check=True)
                os.makedirs(os.path.join(top, "sub"))
            for _ in range(2):  # the second round answers from the cache
                for top in tops:
                    self.assertEqual(find_repo_root(os.path.join(top, "sub")), top)
                    self.assertEqual(find_repo_root(top), top)


class RepoPath(unittest.TestCase):
    def test_a_leading_dot_directory_keeps_its_dot(self):
        self.assertEqual(repo_path(".github/workflows/ci.yml"), ".github/workflows/ci.yml")
        self.assertEqual(repo_path("./.github/w.yml (new)"), ".github/w.yml")

    def test_every_spelling_of_one_path_is_the_same_path(self):
        for spelling in ("a.py", "./a.py", "src/../a.py", "a.py (new)", "a.py  (new) ",
                         " ./src/../a.py", "/a.py", ".\\a.py"):
            self.assertEqual(repo_path(spelling), "a.py", spelling)

    def test_the_root_and_the_outside_are_kept_visible(self):
        self.assertEqual(repo_path("."), ".")
        self.assertEqual(repo_path("./"), ".")
        self.assertEqual(repo_path("../x"), "../x")
        self.assertEqual(repo_path("a/../../x"), "../x")

    def test_escapes_repo_is_by_segment(self):
        self.assertTrue(escapes_repo(".."))
        self.assertTrue(escapes_repo("../x"))
        self.assertFalse(escapes_repo("..x/a"))
        self.assertFalse(escapes_repo("a/.."))
        self.assertFalse(escapes_repo("."))


if __name__ == "__main__":
    unittest.main()
