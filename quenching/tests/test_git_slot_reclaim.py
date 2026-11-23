"""Reclaiming a slot whose spec is archived: `release` carries `.quenching/handoff/` to the
primary checkout, `cq git stale` reports the held slot as `kind: slot` only with every piece of
evidence in favour, and `cq git prune --slot` releases it against the approved tip and id."""
from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import unittest
from types import SimpleNamespace
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.git import slots
from quenching.git.ignored import declared_regenerable
from quenching.git.prune import cmd_prune
from quenching.git.stale import entry_id, stale_report
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

    def held(self, spec="7", merged=True):
        """A slot held under a quenching lock naming `spec`, with one commit merged (pushed to
        origin/main) or not."""
        got = self.run_verb("acquire", branch=f"plan/{spec}-x")[1]
        path = got["path"]
        pathlib.Path(path, f"f-{spec}.txt").write_text("f\n", encoding="utf-8")
        _git(path, "add", f"f-{spec}.txt")
        _git(path, "commit", "-q", "-m", "work")
        if merged:
            _git(path, "push", "-q", "origin", "HEAD:main")
            _git(self.main, "fetch", "-q", "origin")
        _git(self.main, "worktree", "unlock", path)
        _git(self.main, "worktree", "lock", "--reason",
             slots.lock_reason(spec, "s1"), path)
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
        self.assertEqual(got["ignored"]["unrecognized"], [os.path.join(".tmp", "w.txt")])
        pathlib.Path(path, "f-7.txt").write_text("changed\n", encoding="utf-8")
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


class StaleReportsHeldSlots(ReclaimRepo):
    def report(self, phases):
        with mock.patch("quenching.git.stale._open_pr_heads", return_value=set()), \
                mock.patch.object(slots, "spec_phases", return_value=phases), \
                mock.patch.object(slots, "processes_in", return_value=[]):
            return stale_report(self.main)

    def test_an_archived_holder_is_a_slot_candidate_and_a_live_one_is_preserved(self):
        done = os.path.realpath(self.held("7"))
        live = os.path.realpath(self.held("8"))
        report = self.report({"7": "archive", "8": "plans"})
        rows = {e["ref"]: e for e in report["manifest"] if e["kind"] == "slot"}
        self.assertEqual(rows[done]["status"], "candidate")
        self.assertEqual(rows[done]["reasons"], ["archived-holder"])
        self.assertTrue(rows[done]["recommended"])
        self.assertEqual(rows[done]["spec"], "7")
        self.assertEqual(rows[done]["action"]["cq"][:4], ["cq", "git", "prune", "--slot"])
        self.assertEqual(rows[live]["status"], "preserved")
        self.assertEqual(rows[live]["reasons"], ["holder-not-archived"])
        self.assertIsNone(rows[live]["action"])
        worktree_refs = {e["ref"] for e in report["manifest"] if e["kind"] == "worktree"}
        self.assertFalse({done, live} & worktree_refs)
        group = next(g for g in report["groups"] if g["kind"] == "slot")
        self.assertEqual(group["ids"], [rows[done]["id"]])


class PruneReleasesTheSlot(ReclaimRepo):
    def prune(self, phases, **kw):
        args = SimpleNamespace(branch=None, worktree=None, remote_branch=None, slot=None,
                               remote="origin", expect_tip=None, id=None,
                               confirm_inactive=False, json=True)
        vars(args).update(kw)
        buf = io.StringIO()
        with mock.patch("quenching.git.stale._open_pr_heads", return_value=set()), \
                mock.patch.object(slots, "spec_phases", return_value=phases), \
                mock.patch.object(slots, "processes_in", return_value=[]), \
                contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            code = cmd_prune(args)
        return code, json.loads(buf.getvalue())

    def approved(self, path):
        real = os.path.realpath(path)
        return {"slot": path, "expect_tip": _git(path, "rev-parse", "HEAD").strip(),
                "id": entry_id("slot", real), "confirm_inactive": True}

    def state(self, path):
        return next(s["state"] for s in slots.survey(self.main)["slots"] if s["path"] == path)

    def test_an_approved_candidate_is_released_and_its_handoff_carried(self):
        path = self.held("7")
        self.handoff(path, "next.md", "h\n")
        code, out = self.prune({"7": "archive"}, **self.approved(path))
        self.assertEqual(code, 0, out)
        self.assertTrue(out["released"])
        self.assertEqual(self.state(path), "free")
        self.assertTrue(pathlib.Path(self.main, ".quenching", "handoff", "next.md").exists())

    def test_every_missing_approval_is_a_refusal_and_the_slot_stays_held(self):
        path = self.held("7")
        good = self.approved(path)
        for change, code in (({"confirm_inactive": False}, "git-prune-inactivity-unconfirmed"),
                             ({"expect_tip": None}, "git-prune-tip-required"),
                             ({"expect_tip": "0" * 40}, "git-prune-tip-changed"),
                             ({"id": "slot:000000000000"}, "git-prune-id-mismatch")):
            got, out = self.prune({"7": "archive"}, **{**good, **change})
            self.assertEqual((got, out["code"]), (2, code))
        got, out = self.prune({"7": "plans"}, **good)
        self.assertEqual((got, out["code"]), (2, "git-prune-not-reported"))
        self.assertEqual(self.state(path), "held")


if __name__ == "__main__":
    unittest.main()
