"""`cq git refresh`: the local base moves by fast-forward only, keeps uncommitted work, switches no
branch, and the conclude and merge bodies name the verb."""
from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import subprocess
import unittest
from types import SimpleNamespace

import _paths  # noqa: F401  — must precede the `quenching` import
from quenching.git.refresh import cmd_refresh
from test_git import RepoCase, _run


def _out(cwd, *argv):
    return subprocess.run(["git", *argv], cwd=cwd, check=True, capture_output=True,
                          text=True).stdout.strip()

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _commit(repo, name, text="x\n"):
    pathlib.Path(repo, name).write_text(text, encoding="utf-8")
    _run(repo, "add", name)
    _run(repo, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "-m", name)


def _refresh(repo, base="main"):
    os.chdir(repo)
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        code = cmd_refresh(SimpleNamespace(base=base, remote="origin", json=True))
    return code, json.loads(out.getvalue())


class Refresh(RepoCase):
    def setUp(self):
        super().setUp()
        _run(self.repo, "branch", "-M", "main")
        self.remote = os.path.join(self.tmp, "remote.git")
        subprocess.run(["git", "init", "-q", "--bare", self.remote], check=True)
        _run(self.repo, "remote", "add", "origin", self.remote)
        _run(self.repo, "push", "-q", "origin", "main")
        self.other = os.path.join(self.tmp, "other")
        subprocess.run(["git", "clone", "-q", self.remote, self.other], check=True)

    def _advance_remote(self, name="remote.txt"):
        _commit(self.other, name)
        _run(self.other, "push", "-q", "origin", "HEAD:main")

    def _head(self, ref="main"):
        return _out(self.repo, "rev-parse", ref)

    def test_fast_forwards_the_checked_out_base_and_keeps_uncommitted_work(self):
        self._advance_remote()
        pathlib.Path(self.repo, "wip.txt").write_text("mine\n", encoding="utf-8")
        code, payload = _refresh(self.repo)
        self.assertEqual((code, payload["action"]), (0, "updated"))
        self.assertTrue(payload["dirty"])
        self.assertTrue(pathlib.Path(self.repo, "remote.txt").exists())
        self.assertEqual(pathlib.Path(self.repo, "wip.txt").read_text(encoding="utf-8"), "mine\n")

    def test_a_dirty_path_the_incoming_diff_collides_with_is_refused_and_kept(self):
        self._advance_remote("clash.txt")
        pathlib.Path(self.repo, "clash.txt").write_text("mine\n", encoding="utf-8")
        before = self._head()
        code, payload = _refresh(self.repo)
        self.assertEqual((code, payload["reason"]), (1, "merge-refused"))
        self.assertEqual(self._head(), before)
        self.assertEqual(pathlib.Path(self.repo, "clash.txt").read_text(encoding="utf-8"), "mine\n")

    def test_moves_the_ref_without_switching_the_branch_the_checkout_is_on(self):
        _run(self.repo, "checkout", "-q", "-b", "work")
        self._advance_remote()
        code, payload = _refresh(self.repo)
        self.assertEqual((code, payload["action"]), (0, "updated"))
        self.assertEqual(_out(self.repo, "rev-parse", "--abbrev-ref", "HEAD"), "work")
        self.assertEqual(self._head(), self._head("refs/remotes/origin/main"))

    def test_updates_the_base_checked_out_in_another_worktree(self):
        _run(self.repo, "checkout", "-q", "-b", "work")
        self._advance_remote()
        other = os.path.join(self.tmp, "slot")
        _run(self.repo, "worktree", "add", "-q", other, "main")
        code, payload = _refresh(self.repo)
        self.assertEqual((code, payload["action"]), (0, "updated"))
        self.assertTrue(pathlib.Path(other, "remote.txt").exists())

    def test_a_diverged_base_is_reported_and_untouched(self):
        self._advance_remote()
        _commit(self.repo, "local.txt")
        before = self._head()
        code, payload = _refresh(self.repo)
        self.assertEqual((code, payload["reason"]), (1, "diverged"))
        self.assertEqual(self._head(), before)

    def test_current_and_ahead_are_successes_that_change_nothing(self):
        code, payload = _refresh(self.repo)
        self.assertEqual((code, payload["action"]), (0, "current"))
        _commit(self.repo, "local.txt")
        before = self._head()
        code, payload = _refresh(self.repo)
        self.assertEqual((code, payload["action"]), (0, "ahead"))
        self.assertEqual(self._head(), before)

    def test_a_failed_fetch_is_a_finding(self):
        _run(self.repo, "remote", "set-url", "origin", os.path.join(self.tmp, "missing.git"))
        code, payload = _refresh(self.repo)
        self.assertEqual((code, payload["reason"]), (1, "fetch-failed"))


class TheCloseNamesTheVerb(unittest.TestCase):
    def test_conclude_and_merge_bodies_call_it(self):
        for rel in ("quenching/skills/quenching-specs/references/conclude.md",
                    "quenching/skills/quenching-git/references/merge.md"):
            text = " ".join((ROOT / rel).read_text(encoding="utf-8").split())
            self.assertIn("cq git refresh", text, rel)


if __name__ == "__main__":
    unittest.main()
