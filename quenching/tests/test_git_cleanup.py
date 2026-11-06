"""Manifest-backed `cq git stale` / `cq git prune`: assessed worktrees, dated entries with stable
ids, grouped candidates, and snapshot revalidation at delete time."""
from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import subprocess
import unittest
from types import SimpleNamespace
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import
from quenching.git.prune import cmd_prune
from quenching.git.stale import entry_id, stale_report
from test_git import CLEANUP_COMMAND, RepoCase, _run

NO_PRS = mock.patch("quenching.git.stale._open_pr_heads", return_value=set())


def _prune(repo, **kw):
    args = SimpleNamespace(branch=None, worktree=None, remote_branch=None, remote="origin",
                           expect_tip=None, id=None, confirm_inactive=False, json=True)
    vars(args).update(kw)
    os.chdir(repo)
    out = io.StringIO()
    with NO_PRS, contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        code = cmd_prune(args)
    return code, out.getvalue()


class Assessment(RepoCase):
    def _worktree(self, name="wt", branch="wt-branch"):
        path = os.path.join(self.tmp, name)
        _run(self.repo, "worktree", "add", "-q", "-b", branch, path)
        return os.path.realpath(path)

    def _exclude(self, *patterns):
        """Ignore patterns every worktree of this throwaway repo shares."""
        exclude = pathlib.Path(self.repo, ".git", "info", "exclude")
        exclude.parent.mkdir(parents=True, exist_ok=True)
        exclude.write_text("\n".join(patterns) + "\n", encoding="utf-8")

    def _declare(self, *paths):
        config = pathlib.Path(self.repo, ".claude", "quenching.json")
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text(json.dumps({"shared": {"regenerablePaths": list(paths)}}) + "\n",
                          encoding="utf-8")

    def _report(self):
        with NO_PRS:
            return stale_report(self.repo)

    def _row(self, report, path):
        return next(w for w in report["worktrees"] if w["path"] == path)

    def test_a_clean_merged_linked_worktree_is_a_candidate_and_recommended(self):
        path = self._worktree()
        report = self._report()
        row = self._row(report, path)
        self.assertTrue(row["eligible"])
        self.assertEqual(row["ignored"], {"regenerable": [], "unrecognized": []})
        entry = next(e for e in report["manifest"] if e["kind"] == "worktree")
        self.assertEqual(entry["status"], "candidate")
        self.assertTrue(entry["recommended"])
        self.assertEqual(entry["action"]["argv"], ["git", "worktree", "remove", "--", path])
        self.assertIn("--confirm-inactive", entry["action"]["cq"])
        self.assertEqual(entry["id"], entry_id("worktree", path))

    def test_ignored_cache_only_worktree_is_candidate_and_recommended(self):
        self._exclude(".venv/")
        path = self._worktree()
        marker = pathlib.Path(path, ".venv", "lib", "marker")
        marker.parent.mkdir(parents=True)
        marker.write_text("x\n", encoding="utf-8")
        report = self._report()
        row = self._row(report, path)
        self.assertTrue(row["eligible"], row["blockers"])
        self.assertEqual(row["ignored"], {"regenerable": [".venv/"], "unrecognized": []})
        entry = next(e for e in report["manifest"] if e["kind"] == "worktree")
        self.assertTrue(entry["recommended"])
        self.assertEqual(entry["ignored"], row["ignored"])

    def test_a_declared_regenerable_path_is_silent(self):
        self._exclude("generated/")
        path = self._worktree()
        target = pathlib.Path(path, "generated", "report.json")
        target.parent.mkdir(parents=True)
        target.write_text("{}\n", encoding="utf-8")
        self._declare("generated")
        report = self._report()
        row = self._row(report, path)
        self.assertTrue(row["eligible"], row["blockers"])
        self.assertEqual(row["ignored"], {"regenerable": ["generated/"], "unrecognized": []})

    def test_undeclared_ignored_content_is_listed_and_preserved(self):
        self._exclude("*.tmp")
        path = self._worktree()
        pathlib.Path(path, "notes.tmp").write_text("x\n", encoding="utf-8")
        report = self._report()
        row = self._row(report, path)
        self.assertFalse(row["eligible"])
        self.assertIn("ignored-content-unrecognized", row["blockers"])
        self.assertEqual(row["ignored"], {"regenerable": [], "unrecognized": ["notes.tmp"]})
        entry = next(e for e in report["manifest"] if e["kind"] == "worktree")
        self.assertFalse(entry["recommended"])

    def test_dirty_untracked_locked_and_unmerged_worktrees_are_preserved_with_reasons(self):
        dirty = self._worktree("dirty", "dirty-b")
        pathlib.Path(dirty, "x.txt").write_text("x\n", encoding="utf-8")
        locked = self._worktree("locked", "locked-b")
        _run(self.repo, "worktree", "lock", locked)
        ahead = self._worktree("ahead", "ahead-b")
        pathlib.Path(ahead, "y.txt").write_text("y\n", encoding="utf-8")
        _run(ahead, "add", "y.txt")
        _run(ahead, "commit", "-q", "-m", "ahead")
        report = self._report()
        self.assertIn("untracked-files", self._row(report, dirty)["blockers"])
        self.assertIn("locked", self._row(report, locked)["blockers"])
        self.assertIn("unmerged-head", self._row(report, ahead)["blockers"])
        self.assertFalse(any(w["eligible"] for w in report["worktrees"]))

    def test_a_tracked_change_blocks_with_its_own_reason(self):
        path = self._worktree()
        pathlib.Path(path, "a.txt").write_text("changed\n", encoding="utf-8")
        report = self._report()
        self.assertIn("tracked-changes", self._row(report, path)["blockers"])

    def test_unavailable_pr_lookup_blocks_worktrees_and_recommends_nothing(self):
        path = self._worktree()
        with mock.patch("quenching.git.stale._open_pr_heads", return_value=None):
            report = stale_report(self.repo)
        self.assertIn("pr-lookup-unavailable", self._row(report, path)["blockers"])
        self.assertFalse(any(e["recommended"] for e in report["manifest"]))

    def test_open_pr_blocks_and_main_and_current_checkouts_are_not_assessed(self):
        path = self._worktree()
        with mock.patch("quenching.git.stale._open_pr_heads", return_value={"wt-branch"}):
            report = stale_report(self.repo)
        self.assertIn("open-pr", self._row(report, path)["blockers"])
        self.assertEqual([w["path"] for w in report["worktrees"]], [path])

    def test_manifest_dates_the_observed_tip_and_keeps_legacy_lists(self):
        _run(self.repo, "branch", "merged")
        report = self._report()
        entry = next(e for e in report["manifest"] if e["ref"] == "merged")
        sha = subprocess.run(["git", "rev-parse", "merged"], cwd=self.repo, capture_output=True,
                             text=True).stdout.strip()
        self.assertEqual(entry["tip"], sha)
        self.assertRegex(entry["tipDate"], r"^\d{4}-\d{2}-\d{2}T")
        self.assertIn("%cI", entry["dateSource"])
        self.assertTrue(entry["recommended"])
        self.assertEqual(report["staleBranches"], [{"branch": "merged", "reasons": ["merged"]}])
        group = next(g for g in report["groups"] if g["kind"] == "branch")
        self.assertEqual(group["ids"], [entry["id"]])


class Revalidation(RepoCase):
    def test_a_moved_tip_is_refused_and_the_branch_stands(self):
        _run(self.repo, "branch", "merged")
        old = subprocess.run(["git", "rev-parse", "merged"], cwd=self.repo, capture_output=True,
                             text=True).stdout.strip()
        code, _ = _prune(self.repo, branch="merged", expect_tip="0" * 40)
        self.assertEqual(code, 2)
        self.assertIn("merged", subprocess.run(["git", "branch"], cwd=self.repo,
                                               capture_output=True, text=True).stdout)
        code, _ = _prune(self.repo, branch="merged", expect_tip=old, id=entry_id("branch", "merged"))
        self.assertEqual(code, 0)

    def test_an_id_that_names_another_target_is_refused(self):
        _run(self.repo, "branch", "merged")
        code, out = _prune(self.repo, branch="merged", id=entry_id("branch", "other"))
        self.assertEqual(code, 2)
        self.assertIn("git-prune-id-mismatch", out)

    def test_a_live_worktree_needs_inactivity_confirmation_and_its_tip(self):
        path = os.path.realpath(os.path.join(self.tmp, "wt"))
        _run(self.repo, "worktree", "add", "-q", "-b", "wt-b", path)
        tip = subprocess.run(["git", "rev-parse", "HEAD"], cwd=path, capture_output=True,
                             text=True).stdout.strip()
        code, out = _prune(self.repo, worktree=path, expect_tip=tip)
        self.assertEqual((code, "git-prune-inactivity-unconfirmed" in out), (2, True))
        code, out = _prune(self.repo, worktree=path, confirm_inactive=True)
        self.assertEqual((code, "git-prune-tip-required" in out), (2, True))
        code, _ = _prune(self.repo, worktree=path, expect_tip="1" * 40, confirm_inactive=True)
        self.assertEqual(code, 2)
        self.assertTrue(os.path.isdir(path))
        code, _ = _prune(self.repo, worktree=path, expect_tip=tip, confirm_inactive=True,
                         id=entry_id("worktree", path))
        self.assertEqual(code, 0)
        self.assertFalse(os.path.isdir(path))

    def test_a_dirty_worktree_is_not_reported_so_it_is_refused(self):
        path = os.path.realpath(os.path.join(self.tmp, "wt"))
        _run(self.repo, "worktree", "add", "-q", "-b", "wt-b", path)
        pathlib.Path(path, "u.txt").write_text("u\n", encoding="utf-8")
        tip = subprocess.run(["git", "rev-parse", "HEAD"], cwd=path, capture_output=True,
                             text=True).stdout.strip()
        code, _ = _prune(self.repo, worktree=path, expect_tip=tip, confirm_inactive=True)
        self.assertEqual(code, 2)
        self.assertTrue(os.path.isdir(path))


class CommandBody(unittest.TestCase):
    def test_cleanup_shows_dates_groups_and_separate_worktree_confirmation(self):
        text = CLEANUP_COMMAND.read_text(encoding="utf-8")
        for needle in ("manifest", "--expect-tip", "--confirm-inactive", "tipDate", "groups"):
            self.assertIn(needle, text)
        self.assertNotIn("git branch -D", text.replace("Never `git branch -D`", ""))

    def test_cleanup_stops_only_when_the_manifest_is_empty(self):
        text = " ".join(CLEANUP_COMMAND.read_text(encoding="utf-8").split())
        self.assertIn("`manifest` empty", text)
        self.assertNotIn("All four lists", text)


if __name__ == "__main__":
    unittest.main()
