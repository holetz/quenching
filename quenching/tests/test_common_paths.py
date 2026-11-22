"""`quenching.common.paths` — the one normalisation every consumer of `files:` compares through."""
from __future__ import annotations

import pathlib
import sys
import unittest

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.codex import eligible
from quenching.common.paths import escapes_repo, repo_path


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

    def test_the_codex_pillar_compares_through_the_same_function(self):
        self.assertIs(eligible.repo_path, repo_path)


if __name__ == "__main__":
    unittest.main()
