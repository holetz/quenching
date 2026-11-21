"""Reclaiming a slot whose spec is archived: `release` carries `.quenching/handoff/` to the
primary checkout, `cq git stale` reports the held slot as `kind: slot` only with every piece of
evidence in favour, and `cq git prune --slot` releases it against the approved tip and id."""
from __future__ import annotations

import os
import pathlib
import unittest
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.git import slots
from quenching.git.ignored import declared_regenerable
from test_git_worktree_slots import SlotRepo, _git


class ReclaimRepo(SlotRepo):
    def setUp(self):
        super().setUp()
        exclude = pathlib.Path(self.main, ".git", "info", "exclude")
        exclude.parent.mkdir(parents=True, exist_ok=True)
        exclude.write_text(".quenching/\n.agents/\n", encoding="utf-8")

    def handoff(self, root, name, text):
        path = pathlib.Path(root, ".quenching", "handoff", name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path


class ReleaseCarriesTheHandoff(ReclaimRepo):
    def test_a_handoff_is_moved_to_the_primary_checkout_and_the_slot_is_released(self):
        got = self.run_verb("acquire", branch="plan/1-a")[1]
        self.handoff(got["path"], "next.md", "slot\n")
        code, out = self.run_verb("release", path=got["path"])
        self.assertEqual(code, 0, out)
        self.assertTrue(out["released"])
        moved = pathlib.Path(self.main, ".quenching", "handoff", "next.md")
        self.assertEqual(moved.read_text(encoding="utf-8"), "slot\n")
        self.assertEqual([h["to"] for h in out["handoff"]], [str(moved)])
        self.assertFalse(pathlib.Path(got["path"], ".quenching", "handoff").exists())

    def test_a_name_taken_in_the_primary_is_never_overwritten(self):
        got = self.run_verb("acquire", branch="plan/1-a")[1]
        kept = self.handoff(self.main, "next.md", "primary\n")
        self.handoff(got["path"], "next.md", "slot\n")
        code, out = self.run_verb("release", path=got["path"])
        self.assertEqual(code, 0, out)
        self.assertEqual(kept.read_text(encoding="utf-8"), "primary\n")
        target = pathlib.Path(out["handoff"][0]["to"])
        self.assertEqual(target.name, f"next-{os.path.basename(got['path'])}-1.md")
        self.assertEqual(target.read_text(encoding="utf-8"), "slot\n")

    def test_other_ignored_content_still_keeps_the_slot_held(self):
        got = self.run_verb("acquire", branch="plan/1-a")[1]
        self.handoff(got["path"], "next.md", "slot\n")
        pathlib.Path(got["path"], ".tmp").mkdir()
        pathlib.Path(got["path"], ".tmp", "work.txt").write_text("w\n", encoding="utf-8")
        code, out = self.run_verb("release", path=got["path"])
        self.assertEqual(code, 1, out)
        self.assertFalse(out["released"])
        self.assertTrue(pathlib.Path(got["path"], ".quenching", "handoff", "next.md").exists())


class Evidence(ReclaimRepo):
    def held(self, spec="7", merged=True):
        """A slot held under a quenching lock naming `spec`, with one commit merged (pushed to
        origin/main) or not."""
        got = self.run_verb("acquire", branch=f"plan/{spec}-x")[1]
        path = got["path"]
        pathlib.Path(path, "f.txt").write_text("f\n", encoding="utf-8")
        _git(path, "add", "f.txt")
        _git(path, "commit", "-q", "-m", "work")
        if merged:
            _git(path, "push", "-q", "origin", "HEAD:main")
            _git(self.main, "fetch", "-q", "origin")
        _git(self.main, "worktree", "unlock", path)
        _git(self.main, "worktree", "lock", "--reason",
             slots.lock_reason(spec, "s1"), path)
        return path

    def evidence(self, path, phase="archive", processes=()):
        slot = next(s for s in slots.survey(self.main)["slots"] if s["path"] == path)
        with mock.patch.object(slots, "processes_in", return_value=processes):
            return slots.reclaim_evidence(self.main, slot, "origin", "main",
                                          declared_regenerable({}), phase)

    def test_every_fact_in_favour_makes_the_slot_eligible(self):
        path = self.held()
        self.handoff(path, "next.md", "h\n")
        got = self.evidence(path, processes=[])
        self.assertTrue(got["eligible"], got)
        self.assertEqual(got["blockers"], [])
        self.assertEqual(got["spec"], "7")

    def test_each_contrary_fact_is_a_named_blocker(self):
        path = self.held()
        self.assertEqual(self.evidence(path, phase="plans")["blockers"], ["holder-not-archived"])
        self.assertEqual(self.evidence(path, phase=None)["blockers"], ["holder-unknown"])
        self.assertEqual(self.evidence(path, processes=[4242])["blockers"], ["process-in-slot"])
        self.assertEqual(self.evidence(path, processes=None)["blockers"],
                         ["process-lookup-unavailable"])
        pathlib.Path(path, ".tmp").mkdir()
        pathlib.Path(path, ".tmp", "w.txt").write_text("w\n", encoding="utf-8")
        got = self.evidence(path, processes=[])
        self.assertEqual(got["blockers"], ["ignored-content-unrecognized"])
        self.assertEqual(got["ignored"]["unrecognized"], [".tmp/w.txt"])
        pathlib.Path(path, "f.txt").write_text("changed\n", encoding="utf-8")
        self.assertIn("dirty", self.evidence(path, processes=[])["blockers"])

    def test_a_head_outside_the_remote_base_is_unmerged(self):
        path = self.held(merged=False)
        self.assertEqual(self.evidence(path, processes=[])["blockers"], ["unmerged-head"])

    def test_a_lock_naming_a_branch_is_not_a_spec(self):
        got = self.run_verb("acquire", branch="plan/1-a")[1]
        self.assertIn("holder-not-a-spec", self.evidence(got["path"], processes=[])["blockers"])

    @unittest.skipUnless(os.path.isdir("/proc/self"), "needs /proc")
    def test_this_process_is_seen_when_its_cwd_is_in_the_slot(self):
        path = self.held()
        os.chdir(path)
        self.assertIn(os.getpid(), slots.processes_in(path))
        os.chdir(self.main)
        self.assertNotIn(os.getpid(), slots.processes_in(path))


if __name__ == "__main__":
    unittest.main()
