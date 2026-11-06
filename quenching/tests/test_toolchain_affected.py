"""The affected-test selector: what a diff reaches, and every road back to the whole suite.

The rules are exercised against the real tree (a rule that names a test which stopped existing is
the failure mode worth catching), the git side against a throwaway repository, and the fail-open
answers one by one. Each case asserts `complete`, because "ran the whole suite" and "ran nothing"
must never be confused for each other.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
# Shaped like a suite path but never exists; assembled so the citation check does not read the
# fixture as a claim about a file in this checkout.
MISSING_TEST = "quenching/" + "tests/test_that_was_removed.py"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.toolchain import affected  # noqa: E402


class Selection(unittest.TestCase):
    def selected(self, *paths: str) -> affected.Selection:
        return affected.select(REPO_ROOT, files=list(paths))

    def test_a_mapped_source_selects_its_tests_alone(self):
        got = self.selected("quenching/assets/bin/quenching/git/audit.py")
        self.assertFalse(got.complete)
        self.assertIn("quenching/tests/test_git.py", got.tests)
        self.assertNotIn("quenching/tests/test_deploy.py", got.tests)

    def test_a_direct_import_adds_a_test_the_rule_does_not_name(self):
        got = self.selected("quenching/assets/bin/quenching/config/autonomy.py")
        self.assertFalse(got.complete)
        self.assertIn("quenching/tests/test_autonomy_config.py", got.tests)

    def test_each_global_file_runs_the_whole_suite(self):
        for path in ("pyproject.toml", "uv.lock", "scripts/toolchain/tmproot.py",
                     "quenching/tests/_paths.py", "quenching/assets/bin/quenching/common/io.py"):
            with self.subTest(path=path):
                got = self.selected(path)
                self.assertTrue(got.complete)
                self.assertIn("fail-open", got.reasons[0])

    def test_a_changed_test_selects_itself(self):
        got = self.selected("quenching/tests/test_deploy.py")
        self.assertEqual(("quenching/tests/test_deploy.py",), got.tests)
        self.assertFalse(got.complete)

    def test_a_path_no_rule_covers_fails_open(self):
        got = self.selected("mystery/thing.txt")
        self.assertTrue(got.complete)
        self.assertIn("no rule covers", got.reasons[0])

    def test_documentation_alone_selects_nothing_and_is_not_a_failure(self):
        got = self.selected("docs/index.md")
        self.assertEqual((), got.tests)
        self.assertFalse(got.complete)

    def test_a_rule_naming_a_test_that_disappeared_fails_open(self):
        broken = (affected.Rule(("mystery/",), ("test_that_never_existed",)),)
        with mock.patch.object(affected, "RULES", broken):
            got = self.selected("mystery/thing.py")
        self.assertTrue(got.complete)
        self.assertIn("does not exist", got.reasons[0])

    def test_a_deleted_test_fails_open_instead_of_selecting_a_missing_path(self):
        got = self.selected(MISSING_TEST)
        self.assertTrue(got.complete)
        self.assertIn("deleted or moved", got.reasons[0])

    def test_a_workflow_change_reaches_the_proof_tests(self):
        got = self.selected(".github/workflows/ci.yml")
        self.assertFalse(got.complete)
        self.assertIn("quenching/tests/test_proof.py", got.tests)

    def test_no_change_is_an_empty_selection(self):
        got = affected.select(REPO_ROOT, files=[])
        self.assertEqual((), got.tests)
        self.assertFalse(got.complete)

    def test_every_rule_names_a_test_that_exists(self):
        for rule in affected.RULES:
            tests, problem = affected._resolve_tests(REPO_ROOT, rule.tests)
            with self.subTest(prefix=rule.prefixes[0]):
                self.assertIsNone(problem)
                self.assertTrue(tests, rule.prefixes[0])

    def test_the_cli_prints_the_selection_as_json(self):
        proc = subprocess.run([sys.executable, "-m", "scripts.toolchain.affected", "--json",
                               "quenching/assets/bin/quenching/git/audit.py"],
                              cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(0, proc.returncode, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertIn("quenching/tests/test_git.py", payload["tests"])


class GitSide(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = pathlib.Path(self._tmp.name)
        self.git("init", "-q", "-b", "main")
        (self.root / "kept.txt").write_text("one\n", encoding="utf-8")
        self.git("add", "kept.txt")
        self.git("commit", "-q", "-m", "base")

    def git(self, *argv: str) -> str:
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *argv],
                              cwd=self.root, check=True, capture_output=True, text=True).stdout

    def test_the_working_tree_and_untracked_files_are_read(self):
        (self.root / "kept.txt").write_text("two\n", encoding="utf-8")
        (self.root / "new.txt").write_text("new\n", encoding="utf-8")
        self.assertEqual(("kept.txt", "new.txt"), affected.changed_paths(self.root))

    def test_the_merge_base_includes_committed_work(self):
        self.git("checkout", "-q", "-b", "work")
        (self.root / "committed.txt").write_text("x\n", encoding="utf-8")
        self.git("add", "committed.txt")
        self.git("commit", "-q", "-m", "task")
        self.assertEqual(("committed.txt",), affected.changed_paths(self.root, "main"))

    def test_an_unresolvable_base_fails_open(self):
        got = affected.select(self.root, base="no-such-ref")
        self.assertTrue(got.complete)
        self.assertIn("cannot resolve the merge base", got.reasons[0])


if __name__ == "__main__":
    unittest.main()
