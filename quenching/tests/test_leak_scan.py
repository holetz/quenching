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
    def test_prefixed_provider_tokens_are_caught_and_their_lookalikes_are_not(self):
        samples = {
            "github-token": "gh" + "p_" + "A1b2" * 9,
            "aws-access-key-id": "AK" + "IA" + "ABCDEFGHIJ234567",
            "anthropic-api-key": "sk-" + "ant-" + "api03-" + "x" * 30,
            "openai-project-key": "sk-" + "proj-" + "y" * 48,
            "slack-token": "xo" + "xb-" + "1234567890-abc",
            "gitlab-token": "gl" + "pat-" + "z" * 20,
            "private-key": "-----BEGIN " + "PGP PRIVATE KEY BLOCK-----",
        }
        pats = leak.patterns(generic_only=True)
        for label, sample in samples.items():
            found = leak.scan_text("f.md", f"token = {sample}\n", pats)
            self.assertEqual([label], [f.label for f in found], label)
            self.assertNotIn(sample, found[0].excerpt, label)
        prose = ("a `ghp_` prefix, the AKIA family, `sk-ant-` keys and a password=example "
                 "line in prose are not tokens\n")
        self.assertEqual([], leak.scan_text("f.md", prose, pats))

    def test_hidden_unicode_is_caught_but_a_leading_bom_and_emoji_joiners_are_not(self):
        pats = leak.patterns(generic_only=True)
        for char in ("\u200b", "\u202e", "\u2066", "\U000e0041", "\ufeff"):
            found = leak.scan_text("SKILL.md", f"run the step{char} now\n", pats)
            self.assertEqual(["hidden-unicode"], [f.label for f in found], repr(char))
        self.assertEqual([], leak.scan_text("f.md", "\ufeffa file an editor saved with a BOM\n",
                                            pats))
        self.assertEqual([], leak.scan_text("f.md", "a family \U0001f468\u200d\U0001f469\n",
                                            pats))

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
        with mock.patch.dict(os.environ, {"HOME": "/home/jane.doe"}):
            self.assertTrue(leak.path_patterns()["home-slug"].search(
                "~/.claude/projects/-home-jane-doe-repo/memory"))
        with mock.patch.dict(os.environ, {"HOME": "/"}):
            self.assertEqual(leak.path_patterns(), {})

    def test_slug_of_a_root_home_ignores_a_flag_and_a_word_ending_in_it(self):
        slug = "-" + "root"
        text = f"run cq --root . then temp{slug} and {slug}-repo\n"
        with mock.patch.dict(os.environ, {"HOME": "/root"}):
            pat = leak.path_patterns()["home-slug"]
            self.assertEqual([m.group() for m in pat.finditer(text)], [slug])
            self.assertEqual(leak.normalize_paths(f"run cq --root . then temp{slug}\n"),
                             f"run cq --root . then temp{slug}\n")
            self.assertEqual(leak.normalize_paths(f"~/.claude/projects/{slug}-repo/m\n"),
                             "~/.claude/projects/<project>/m\n")

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
        text = (f"a {scratch}/out.txt\nb {HOME}/repo/docs/index.md\nc {HOME}/repo\n"
                f"d {HOME}/.config/q\ne ~/.claude/projects/-home-alice-repo/memory/m.md\n")
        self.assertEqual(leak.normalize_paths(text, f"{HOME}/repo"),
                         "a <scratchpad>/out.txt\nb docs/index.md\nc .\nd ~/.config/q\n"
                         "e ~/.claude/projects/<project>/memory/m.md\n")

    def test_a_windows_root_is_relative_in_either_separator(self):
        root = "C:\\work\\repo"
        text = f"a {root}\\docs\\x.md\nb C:/work/repo/docs/y.md\nc {root}\nd C:\\work\\repository\n"
        self.assertEqual(leak.normalize_paths(text, root),
                         "a docs\\x.md\nb docs/y.md\nc .\nd C:\\work\\repository\n")

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

    def test_push_judges_an_added_line_that_starts_with_plus_plus(self):
        base = git(self.repo, "rev-parse", "HEAD").strip()
        pathlib.Path(self.repo, "a.txt").write_text("clean\n++ acme-corp\n", encoding="utf-8")
        git(self.repo, "commit", "-q", "-am", "plus")
        head = git(self.repo, "rev-parse", "HEAD").strip()
        found = leak.scan_push(self.repo, f"refs/heads/main {head} refs/heads/main {base}\n",
                               leak.patterns())
        self.assertEqual([f.label for f in found], ["denylist:3"])

    def test_new_ref_is_judged_against_the_destination_remote_only(self):
        pathlib.Path(self.repo, "a.txt").write_text(f"clean\ncpf {CPF}\n", encoding="utf-8")
        git(self.repo, "commit", "-q", "-am", "leak")
        head = git(self.repo, "rev-parse", "HEAD").strip()
        git(self.repo, "update-ref", "refs/remotes/private/main", head)
        line = f"refs/heads/main {head} refs/heads/main {leak.ZERO_SHA}\n"
        pats = leak.patterns(generic_only=True)
        self.assertEqual([f.label for f in leak.scan_push(self.repo, line, pats, "public")],
                         ["brazilian-cpf"])
        self.assertEqual([f.label for f in leak.scan_push(self.repo, line, pats)],
                         ["brazilian-cpf"])
        self.assertEqual(leak.scan_push(self.repo, line, pats, "private"), [])

    def test_an_old_tip_this_clone_lacks_is_judged_as_a_new_ref(self):
        pathlib.Path(self.repo, "a.txt").write_text(f"clean\ncpf {CPF}\n", encoding="utf-8")
        git(self.repo, "commit", "-q", "-am", "leak")
        head = git(self.repo, "rev-parse", "HEAD").strip()
        pats = leak.patterns(generic_only=True)
        new_ref = f"refs/heads/main {head} refs/heads/main {leak.ZERO_SHA}\n"
        for unknown in ("8921fe5" + "0" * 32 + "1", "--all", "HEAD~1"):
            line = f"refs/heads/main {head} refs/heads/main {unknown}\n"
            for remote in (None, "origin"):
                found = leak.scan_push(self.repo, line, pats, remote)
                self.assertEqual(found, leak.scan_push(self.repo, new_ref, pats, remote))
                self.assertEqual([f.label for f in found], ["brazilian-cpf"])

    def test_a_local_sha_that_is_not_a_full_object_name_refuses(self):
        base = git(self.repo, "rev-parse", "HEAD").strip()
        pats = leak.patterns(generic_only=True)
        for forged in ("--all", "HEAD", "HEAD~1", base[:12], base.upper()):
            with self.subTest(forged=forged):
                line = f"refs/heads/main {forged} refs/heads/main {base}\n"
                with self.assertRaises(leak.PushInputInvalid) as raised:
                    leak.scan_push(self.repo, line, pats, "origin")
                self.assertIsInstance(raised.exception, subprocess.CalledProcessError)
                self.assertIn(repr(forged), raised.exception.stderr)

    def test_a_sha256_null_name_deletes_and_creates_like_the_sha1_one(self):
        pathlib.Path(self.repo, "a.txt").write_text(f"clean\ncpf {CPF}\n", encoding="utf-8")
        git(self.repo, "commit", "-q", "-am", "leak")
        head = git(self.repo, "rev-parse", "HEAD").strip()
        pats = leak.patterns(generic_only=True)
        zero256 = "0" * 64
        deleted = f"(delete) {zero256} refs/heads/main {head}\n"
        self.assertEqual(leak.scan_push(self.repo, deleted, pats, "origin"), [])
        sha1_new = f"refs/heads/main {head} refs/heads/main {leak.ZERO_SHA}\n"
        sha256_new = f"refs/heads/main {head} refs/heads/main {zero256}\n"
        with mock.patch.object(leak, "_known_commit", side_effect=AssertionError("asked")):
            for remote in (None, "origin"):
                found = leak.scan_push(self.repo, sha256_new, pats, remote)
                self.assertEqual(found, leak.scan_push(self.repo, sha1_new, pats, remote))
                self.assertEqual([f.label for f in found], ["brazilian-cpf"])

    def test_existing_ref_merging_a_published_base_judges_only_what_the_remote_lacks(self):
        git(self.repo, "checkout", "-q", "-b", "work")
        pathlib.Path(self.repo, "w.txt").write_text("work\n", encoding="utf-8")
        git(self.repo, "add", "w.txt")
        git(self.repo, "commit", "-q", "-m", "work")
        old_tip = git(self.repo, "rev-parse", "HEAD").strip()
        git(self.repo, "update-ref", "refs/remotes/origin/work", old_tip)
        git(self.repo, "checkout", "-q", "main")
        pathlib.Path(self.repo, "a.txt").write_text(f"clean\ncpf {CPF}\n", encoding="utf-8")
        git(self.repo, "commit", "-q", "-am", "published on main")
        git(self.repo, "update-ref", "refs/remotes/origin/main",
            git(self.repo, "rev-parse", "HEAD").strip())
        git(self.repo, "checkout", "-q", "work")
        git(self.repo, "merge", "-q", "--no-ff", "-m", "merge main", "main")
        pathlib.Path(self.repo, "w.txt").write_text(f"work\ncpf {CPF}\n", encoding="utf-8")
        git(self.repo, "commit", "-q", "-am", "new on work")
        head = git(self.repo, "rev-parse", "HEAD").strip()
        line = f"refs/heads/work {head} refs/heads/work {old_tip}\n"
        pats = leak.patterns(generic_only=True)
        self.assertEqual([f.where for f in leak.scan_push(self.repo, line, pats, "origin")],
                         [f"commit {head[:12]} (diff)"])
        self.assertEqual(len(leak.scan_push(self.repo, line, pats)), 2)

    def test_staged_scans_a_type_change(self):
        os.remove(pathlib.Path(self.repo, "a.txt"))
        try:
            os.symlink(f"{HOME}/secret", pathlib.Path(self.repo, "a.txt"))
        except (OSError, NotImplementedError):
            self.skipTest("this platform cannot create a symlink")
        git(self.repo, "add", "a.txt")
        found = leak.scan_staged(self.repo, leak.patterns(generic_only=True))
        self.assertEqual([(f.where, f.label) for f in found], [("a.txt", "home-path")])

    def test_all_scans_tracked_files_and_skips_binaries(self):
        pathlib.Path(self.repo, "bin.dat").write_bytes(b"\0" + DATABRICKS_HOST.encode())
        pathlib.Path(self.repo, "c.md").write_text(f"{HOME}/secret\n", encoding="utf-8")
        git(self.repo, "add", ".")
        found = leak.scan_all(self.repo, leak.patterns(generic_only=True))
        self.assertEqual([(f.where, f.label) for f in found], [("c.md", "home-path")])


if __name__ == "__main__":
    unittest.main()
