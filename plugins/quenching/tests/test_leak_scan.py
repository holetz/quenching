"""Executable proofs for the leak gate's scanner (`quenching.common.leak`).

Every sample that a pattern must catch is assembled at run time: written literally, it would trip
the very gate it tests the moment this file is committed."""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.common import leak

HOME = "/home/alice"
DATABRICKS_HOST = "adb-" + "1234567890" + ".7.azure" + "databricks.net"
CPF = "123.456" + ".789-09"


def git(root: str, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True,
                          text=True).stdout


def init_repo(root: str) -> None:
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "dev@example.org")
    git(root, "config", "user.name", "Dev")
    git(root, "config", "commit.gpgsign", "false")
    git(root, "config", "core.hooksPath", "/dev/null")


class LeakEnv(unittest.TestCase):
    """A fake `$HOME` and a denylist file of the test's own."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.denylist = pathlib.Path(self.tmp, "denylist.txt")
        self.denylist.write_text("# private terms\n\nacme-corp\n", encoding="utf-8")
        patcher = mock.patch.dict(os.environ, {"HOME": HOME, leak.DENYLIST_ENV: str(self.denylist)})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self._tmp.cleanup)


class Patterns(LeakEnv):
    def test_generic_patterns_catch_each_class_and_name_the_line(self):
        text = f"ok\nhost {DATABRICKS_HOST}\ncpf {CPF}\n"
        found = leak.scan_text("f.md", text, leak.patterns(generic_only=True))
        self.assertEqual([(f.line, f.label) for f in found],
                         [(2, "azure-databricks-host"), (3, "brazilian-cpf")])

    def test_path_patterns_come_from_home_never_from_the_code(self):
        pats = leak.path_patterns()
        self.assertTrue(pats["home-path"].search(f"see {HOME}/x"))
        self.assertTrue(pats["home-slug"].search("~/.claude/projects/-home-alice-repo/memory"))
        self.assertFalse(pats["home-path"].search("/home/alicea/x"))
        with mock.patch.dict(os.environ, {"HOME": "/"}):
            self.assertEqual(leak.path_patterns(), {})

    def test_denylist_is_case_insensitive_and_skips_comments(self):
        pats = leak.patterns()
        self.assertIn("denylist:3", pats)
        self.assertEqual(len([k for k in pats if k.startswith("denylist")]), 1)
        self.assertTrue(leak.scan_text("x", "Org ACME-Corp here", pats))

    def test_missing_denylist_fails_closed_unless_generic_only_or_not_required(self):
        self.denylist.unlink()
        with self.assertRaises(leak.DenylistMissing):
            leak.patterns()
        self.assertNotIn("denylist:3", leak.patterns(generic_only=True))
        self.assertIn("home-path", leak.patterns(require_denylist=False))


class Normalize(LeakEnv):
    def test_scratchpad_root_home_and_slug_get_their_relative_form(self):
        scratch = "/tmp/claude-1000/-home-alice-repo/0f1e2d3c-4b5a-6978-8a9b-0c1d2e3f4a5b/scratchpad"
        text = (f"a {scratch}/out.txt\nb {HOME}/repo/docs/x.md\nc {HOME}/repo\n"
                f"d {HOME}/.config/q\ne ~/.claude/projects/-home-alice-repo/memory/m.md\n")
        self.assertEqual(leak.normalize_paths(text, f"{HOME}/repo"),
                         "a <scratchpad>/out.txt\nb docs/x.md\nc .\nd ~/.config/q\n"
                         "e ~/.claude/projects/<project>/memory/m.md\n")

    def test_guard_normalizes_then_refuses_what_has_no_relative_form(self):
        clean, found = leak.guard_text(f"p {HOME}/x\n", None)
        self.assertEqual((clean, found), ("p ~/x\n", []))
        _, found = leak.guard_text("org acme-corp\n", None)
        self.assertEqual([f.label for f in found], ["denylist:3"])
        refusal = leak.store_refusal(found)
        self.assertEqual((refusal["code"], refusal["exit"]), ("sp-leak", 2))
        self.assertIn("nothing was written", refusal["message"])

    def test_guard_with_previous_judges_only_the_lines_it_adds(self):
        previous = f"legacy acme-corp\np {HOME}/x\n"
        clean, found = leak.guard_text(previous + "new line\n", None, previous)
        self.assertEqual((clean, found), ("legacy acme-corp\np ~/x\nnew line\n", []))
        _, found = leak.guard_text(previous + "added acme-corp\n", None, previous)
        self.assertEqual([(f.line, f.label) for f in found], [(3, "denylist:3")])

    def test_guard_runs_without_a_denylist(self):
        self.denylist.unlink()
        _, found = leak.guard_text(f"host {DATABRICKS_HOST}\n", None)
        self.assertEqual([f.label for f in found], ["azure-databricks-host"])


class Scans(LeakEnv):
    def setUp(self):
        super().setUp()
        self.repo = str(pathlib.Path(self.tmp, "repo"))
        os.mkdir(self.repo)
        init_repo(self.repo)
        pathlib.Path(self.repo, "a.txt").write_text("clean\n", encoding="utf-8")
        git(self.repo, "add", "a.txt")
        git(self.repo, "commit", "-q", "-m", "base")

    def test_staged_scans_the_index_and_the_author_email(self):
        pathlib.Path(self.repo, "b.txt").write_text(f"x\n{DATABRICKS_HOST}\n", encoding="utf-8")
        git(self.repo, "add", "b.txt")
        git(self.repo, "config", "user.email", "me@acme-corp.example")
        found = leak.scan_staged(self.repo, leak.patterns())
        self.assertEqual({(f.where, f.line, f.label) for f in found},
                         {("git config user.email", 1, "denylist:3"), ("b.txt", 2, "azure-databricks-host")})

    def test_push_scans_headers_and_added_lines_of_unpublished_commits(self):
        base = git(self.repo, "rev-parse", "HEAD").strip()
        pathlib.Path(self.repo, "a.txt").write_text(f"clean\ncpf {CPF}\n", encoding="utf-8")
        git(self.repo, "commit", "-q", "-am", "mention acme-corp")
        head = git(self.repo, "rev-parse", "HEAD").strip()
        found = leak.scan_push(self.repo, f"refs/heads/main {head} refs/heads/main {base}\n",
                               leak.patterns())
        self.assertEqual(sorted(f.label for f in found), ["brazilian-cpf", "denylist:3"])
        deleted = f"(delete) {leak.ZERO_SHA} refs/heads/main {base}\n"
        self.assertEqual(leak.scan_push(self.repo, deleted, leak.patterns()), [])

    def test_all_scans_tracked_files_and_skips_binaries(self):
        pathlib.Path(self.repo, "bin.dat").write_bytes(b"\0" + DATABRICKS_HOST.encode())
        pathlib.Path(self.repo, "c.md").write_text(f"{HOME}/secret\n", encoding="utf-8")
        git(self.repo, "add", ".")
        found = leak.scan_all(self.repo, leak.patterns(generic_only=True))
        self.assertEqual([(f.where, f.label) for f in found], [("c.md", "home-path")])


if __name__ == "__main__":
    unittest.main()
