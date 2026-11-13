"""`cq git worktree acquire | release | slots` against real throwaway repositories.

A slot is reused across specs, so the properties under test are the ones a reuse can break: the
lock is the mutex (two takers never share a slot), the cap is a ceiling, a release never carries
one spec's dirt into the next, and the ignored caches survive the switch."""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import subprocess
import tempfile
import pathlib
import sys
import unittest
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.git import slots

CQ = str(pathlib.Path(__file__).resolve().parent.parent / "assets" / "bin" / "cq")


def _git(cwd, *args):
    return subprocess.run(["git", "-C", cwd, "-c", "user.name=t", "-c", "user.email=t@t", *args],
                          check=True, capture_output=True, text=True).stdout


def _args(**kw):
    base = dict(json=True, path=None, branch=None, base="main", remote="origin", spec=None,
                no_setup=True, wait=False, timeout_minutes=None, session="s1")
    base.update(kw)
    return argparse.Namespace(**base)


class SlotRepo(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = os.path.realpath(tmp.name)
        self.origin = os.path.join(self.base, "origin.git")
        _git(self.base, "init", "-q", "--bare", "-b", "main", self.origin)
        self.main = os.path.join(self.base, "repo")
        _git(self.base, "init", "-q", "-b", "main", self.main)
        with open(os.path.join(self.main, ".gitignore"), "w") as fh:
            fh.write(".venv/\n.tmp/\n")
        _git(self.main, "add", ".gitignore")
        _git(self.main, "commit", "-q", "-m", "init")
        _git(self.main, "remote", "add", "origin", self.origin)
        _git(self.main, "push", "-q", "origin", "main")
        self.config({"min": 1, "max": 3, "waitMinutes": 1, "pollSeconds": 1})
        cwd = os.getcwd()
        os.chdir(self.main)
        self.addCleanup(os.chdir, cwd)

    def config(self, worktree_slots):
        os.makedirs(os.path.join(self.main, ".agents"), exist_ok=True)
        with open(os.path.join(self.main, ".agents", "quenching.json"), "w") as fh:
            json.dump({"shared": {"worktreeSlots": worktree_slots}}, fh)

    def run_verb(self, verb, **kw):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            code = getattr(slots, verb)(_args(**kw))
        return code, json.loads(buf.getvalue())


class AcquireAndRelease(SlotRepo):
    def test_acquire_cuts_a_locked_slot_on_the_branch(self):
        code, out = self.run_verb("acquire", branch="plan/1-a", spec=None)
        self.assertEqual(code, 0, out)
        self.assertTrue(out["created"])
        self.assertEqual(os.path.basename(out["path"]), "repo-slot-1")
        self.assertEqual(_git(out["path"], "branch", "--show-current").strip(), "plan/1-a")
        reason = slots.parse_reason(out["lock"])
        self.assertEqual(reason["spec"], "plan/1-a")
        self.assertEqual(reason["session"], "s1")
        self.assertRegex(reason["date"], r"^\d{4}-\d\d-\d\dT")

    def test_release_then_acquire_reuses_the_directory_and_its_venv(self):
        _code, first = self.run_verb("acquire", branch="plan/1-a")
        os.makedirs(os.path.join(first["path"], ".venv", "lib"))
        code, out = self.run_verb("release", path=first["path"])
        self.assertEqual(code, 0, out)
        self.assertTrue(out["released"])
        _code, second = self.run_verb("acquire", branch="plan/2-b")
        self.assertEqual(second["path"], first["path"])
        self.assertFalse(second["created"])
        self.assertTrue(os.path.isdir(os.path.join(second["path"], ".venv", "lib")))

    def test_a_dirty_slot_is_never_released(self):
        _code, got = self.run_verb("acquire", branch="plan/1-a")
        with open(os.path.join(got["path"], "work.txt"), "w") as fh:
            fh.write("unsaved")
        code, out = self.run_verb("release", path=got["path"])
        self.assertEqual(code, 1)
        self.assertFalse(out["released"])
        self.assertEqual(slots.survey(self.main)["slots"][0]["state"], "held")

    def test_unrecognized_ignored_content_keeps_the_slot_held(self):
        _code, got = self.run_verb("acquire", branch="plan/1-a")
        os.makedirs(os.path.join(got["path"], ".tmp"))
        with open(os.path.join(got["path"], ".tmp", "notes.txt"), "w") as fh:
            fh.write("x")
        code, out = self.run_verb("release", path=got["path"])
        self.assertEqual(code, 1)
        self.assertIn(os.path.join(".tmp", "notes.txt"), out["ignored"])

    def test_an_unmerged_branch_survives_its_release(self):
        _code, got = self.run_verb("acquire", branch="plan/1-a")
        _git(got["path"], "commit", "-q", "--allow-empty", "-m", "work")
        _code, out = self.run_verb("release", path=got["path"])
        self.assertTrue(out["released"])
        self.assertFalse(out["branchDeleted"])
        self.assertTrue(_git(self.main, "branch", "--list", "plan/1-a").strip())

    def test_acquiring_a_branch_already_in_a_slot_returns_that_slot(self):
        _code, first = self.run_verb("acquire", branch="plan/1-a")
        code, again = self.run_verb("acquire", branch="plan/1-a")
        self.assertEqual(code, 0)
        self.assertEqual(again["path"], first["path"])
        self.assertEqual(len(slots.survey(self.main)["slots"]), 1)

    def test_release_refuses_a_worktree_that_is_not_a_slot(self):
        other = os.path.join(self.base, "repo-1")
        _git(self.main, "worktree", "add", "-q", "-b", "x", other)
        code, out = self.run_verb("release", path=other)
        self.assertEqual(code, 2)
        self.assertEqual(out["code"], "git-worktree-release-not-a-slot")


class TheCeiling(SlotRepo):
    def test_concurrent_takers_get_distinct_slots_and_the_extra_one_is_refused(self):
        procs = [subprocess.Popen([sys.executable, CQ, "git", "worktree", "acquire", "--branch",
                                   f"plan/{n}-x", "--base", "main", "--no-setup", "--json"],
                                  cwd=self.main, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, text=True)
                 for n in range(1, 5)]
        results = [(p.wait(), json.loads(p.stdout.read())) for p in procs]
        for p in procs:
            p.stdout.close()
        won = [out["path"] for code, out in results if code == 0]
        lost = [out for code, out in results if code != 0]
        self.assertEqual(len(won), 3, results)
        self.assertEqual(len(set(won)), 3)
        self.assertEqual(len(lost), 1)
        self.assertEqual(lost[0]["code"], "git-worktree-slots-full")
        self.assertEqual(len(lost[0]["holders"]), 3)
        self.assertTrue(all("release" in h for h in lost[0]["holders"]))

    def test_a_fresh_branch_with_no_work_is_never_taken_as_merged(self):
        for n in range(1, 4):
            self.run_verb("acquire", branch=f"plan/{n}-x")
        code, out = self.run_verb("acquire", branch="plan/9-new")
        self.assertEqual(code, 2, out)
        self.assertEqual(out["code"], "git-worktree-slots-full")

    def test_other_worktrees_are_never_counted(self):
        for n in range(3):
            _git(self.main, "worktree", "add", "-q", "-b", f"legacy-{n}",
                 os.path.join(self.base, f"repo-legacy-{n}"))
        code, out = self.run_verb("acquire", branch="plan/1-a")
        self.assertEqual(code, 0, out)
        view = slots.survey(self.main)
        self.assertEqual(len(view["slots"]), 1)
        self.assertEqual(len(view["others"]), 3)

    def test_at_the_ceiling_a_merged_clean_holder_is_freed(self):
        for n in range(1, 4):
            _code, got = self.run_verb("acquire", branch=f"plan/{n}-x")
            if n == 1:
                _git(got["path"], "commit", "-q", "--allow-empty", "-m", "work")
        _git(self.main, "push", "-q", "origin", "plan/1-x:main")
        code, out = self.run_verb("acquire", branch="plan/9-new")
        self.assertEqual(code, 0, out)
        self.assertEqual([f["branch"] for f in out["freed"]], ["plan/1-x"])

    def test_wait_times_out_to_needs_human(self):
        for n in range(1, 4):
            self.run_verb("acquire", branch=f"plan/{n}-x")
        with mock.patch.object(slots.time, "sleep"), \
                mock.patch.object(slots.time, "monotonic", side_effect=[0, 0, 61, 61, 61]):
            code, out = self.run_verb("acquire", branch="plan/9-new", wait=True,
                                      timeout_minutes=1)
        self.assertEqual(code, 2)
        self.assertEqual(out["code"], "git-worktree-slots-timeout")
        self.assertTrue(out["needsHuman"])


class Limits(unittest.TestCase):
    def test_defaults_and_a_ceiling_never_below_the_floor(self):
        with mock.patch.object(slots, "load_config", return_value={}):
            self.assertEqual(slots.limits("."), slots.DEFAULTS)
        cfg = {"namespaces": {"shared": {"worktreeSlots": {"min": 5, "max": 2, "pollSeconds": 0}}}}
        with mock.patch.object(slots, "load_config", return_value=cfg):
            got = slots.limits(".")
        self.assertEqual((got["min"], got["max"], got["pollSeconds"]), (5, 5, 30))


if __name__ == "__main__":
    unittest.main()
