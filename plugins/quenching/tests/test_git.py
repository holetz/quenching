"""The `git` pillar's four subcommands, exercised against real throwaway git repositories —
the same choice `test_golden.py` makes for the other three pillars, taken further here
because `base`, `stale` and `conventions` read facts (refs, a branch's own description, live
worktrees, an on-disk standards folder) no filesystem-only fixture reproduces honestly.

No pre-refactor script owned this pillar, so nothing here is migrated: `pilar-git-e-specs-
agnosticas-ao-git`, task 3.5, wrote every case from the four subcommands' own contracts.
"""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.git.base import (_init_default_branch, _is_host_default, _origin_head_branch,
                                resolve_base)
from quenching.git.conventions import STANDARDS_DIR, _declared_docs
from quenching.git.slugs import _read_slugs, cmd_slugs
from quenching.git.stale import _gone_branches, _merged_branches, _orphan_worktrees

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
CQ = str(PLUGIN_ROOT / "assets" / "bin" / "cq")


def _run(cwd: str, *argv: str) -> None:
    subprocess.run(["git", *argv], cwd=cwd, check=True, capture_output=True, text=True)


def _init_repo(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    _run(path, "init", "-q", "-b", "main")
    _run(path, "config", "user.email", "test@example.com")
    _run(path, "config", "user.name", "Test")
    with open(os.path.join(path, "a.txt"), "w", encoding="utf-8") as f:
        f.write("x\n")
    _run(path, "add", "a.txt")
    _run(path, "commit", "-q", "-m", "init")
    return path


def _cq_json(cwd: str, *argv: str) -> dict:
    proc = subprocess.run([sys.executable, CQ, "git", *argv, "--json"], cwd=cwd,
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


class RepoCase(unittest.TestCase):
    def setUp(self):
        # Restored via addCleanup, in LIFO order — BEFORE the tempdir cleanup below runs, so a
        # test that `os.chdir`s into the repo never leaves the process cwd pointing at a
        # directory `tmp.cleanup()` is about to delete out from under every test that follows.
        self.addCleanup(os.chdir, os.getcwd())
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = tmp.name
        self.repo = _init_repo(os.path.join(self.tmp, "repo"))


class Base(RepoCase):
    def test_falls_back_to_main_with_nothing_declared_or_configured(self):
        base, is_default = resolve_base(self.repo)
        self.assertEqual(base, "main")
        self.assertFalse(is_default)

    def test_init_default_branch_is_read_back_verbatim(self):
        _run(self.repo, "config", "init.defaultBranch", "trunk")
        self.assertEqual(_init_default_branch(self.repo), "trunk")

    def test_origin_head_resolves_as_base_when_nothing_declared(self):
        _run(self.repo, "update-ref", "refs/remotes/origin/main", "HEAD")
        _run(self.repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
        base, _is_default = resolve_base(self.repo)
        self.assertEqual(base, "main")

    def test_origin_head_symbolic_ref_resolves_to_the_branch_name(self):
        self.assertIsNone(_origin_head_branch(self.repo))
        _run(self.repo, "update-ref", "refs/remotes/origin/develop", "HEAD")
        _run(self.repo, "symbolic-ref", "refs/remotes/origin/HEAD",
             "refs/remotes/origin/develop")
        self.assertEqual(_origin_head_branch(self.repo), "develop")

    def test_is_host_default_is_false_for_an_unknown_backend(self):
        self.assertFalse(_is_host_default(self.repo, "unknown-provider", "main"))

    def test_is_host_default_is_false_when_the_host_cli_cannot_answer(self):
        # no GitHub remote in this throwaway repo — a missing or refusing host CLI reads as
        # "unknown", never as a crash.
        self.assertFalse(_is_host_default(self.repo, "github", "main"))

    def test_cq_git_base_json_matches_the_resolved_pair(self):
        payload = _cq_json(self.repo, "base")
        self.assertEqual((payload["base"], payload["isDefault"]), ("main", False))


class Slugs(RepoCase):
    def setUp(self):
        super().setUp()
        _run(self.repo, "branch", "feature-a")

    def test_no_marking_reads_as_empty(self):
        lines, slugs, idx = _read_slugs(self.repo, "feature-a")
        self.assertEqual((lines, slugs, idx), ([], [], None))

    def test_add_is_a_read_merge_write_that_preserves_other_lines(self):
        _run(self.repo, "config", "branch.feature-a.description",
             "a human wrote this by hand\nquenching-slugs: alpha-widget")
        os.chdir(self.repo)
        cmd_slugs(SimpleNamespace(branch="feature-a", add="beta-widget", json=True))
        _lines, slugs, _idx = _read_slugs(".", "feature-a")
        self.assertEqual(slugs, ["alpha-widget", "beta-widget"])
        desc = subprocess.run(["git", "config", "branch.feature-a.description"],
                              capture_output=True, text=True).stdout
        self.assertIn("a human wrote this by hand", desc)
        self.assertEqual(desc.count("quenching-slugs:"), 1)

    def test_adding_the_same_slug_twice_does_not_duplicate_it(self):
        os.chdir(self.repo)
        cmd_slugs(SimpleNamespace(branch="feature-a", add="alpha-widget", json=True))
        cmd_slugs(SimpleNamespace(branch="feature-a", add="alpha-widget", json=True))
        _lines, slugs, _idx = _read_slugs(".", "feature-a")
        self.assertEqual(slugs, ["alpha-widget"])

    def test_cq_git_slugs_json_round_trips_through_the_add_flag(self):
        _cq_json(self.repo, "slugs", "feature-a", "--add", "gamma-widget")
        payload = _cq_json(self.repo, "slugs", "feature-a")
        self.assertEqual(payload["slugs"], ["gamma-widget"])


class Stale(RepoCase):
    def test_a_trivially_merged_branch_is_reported_merged(self):
        _run(self.repo, "branch", "feature-b")
        merged = _merged_branches(self.repo, "main", {"main"})
        self.assertIn("feature-b", merged)

    def test_a_protected_branch_is_excluded_even_if_merged(self):
        _run(self.repo, "branch", "feature-c")
        merged = _merged_branches(self.repo, "main", {"main", "feature-c"})
        self.assertNotIn("feature-c", merged)

    def test_a_branch_whose_upstream_is_gone_is_reported_gone(self):
        _run(self.repo, "remote", "add", "origin", "https://example.invalid/repo.git")
        _run(self.repo, "branch", "feature-d")
        _run(self.repo, "update-ref", "refs/remotes/origin/feature-d", "HEAD")
        _run(self.repo, "branch", "--set-upstream-to=origin/feature-d", "feature-d")
        _run(self.repo, "update-ref", "-d", "refs/remotes/origin/feature-d")
        self.assertIn("feature-d", _gone_branches(self.repo, {"main"}))

    def test_an_orphan_worktree_is_a_registered_path_missing_on_disk(self):
        wt = os.path.join(self.tmp, "wt1")
        _run(self.repo, "worktree", "add", "-q", "-b", "wt-branch", wt)
        shutil.rmtree(wt)
        orphans = _orphan_worktrees(self.repo)
        self.assertEqual([o["path"] for o in orphans], [wt])
        self.assertEqual(orphans[0]["branch"], "wt-branch")

    def test_a_live_worktree_is_not_reported_orphan(self):
        wt = os.path.join(self.tmp, "wt2")
        _run(self.repo, "worktree", "add", "-q", "-b", "wt-branch-2", wt)
        self.assertEqual(_orphan_worktrees(self.repo), [])

    def test_cq_git_stale_json_excludes_base_and_reports_merged(self):
        _run(self.repo, "branch", "feature-e")
        payload = _cq_json(self.repo, "stale")
        names = {b["branch"] for b in payload["staleBranches"]}
        self.assertIn("feature-e", names)
        self.assertNotIn("main", names)


class Conventions(RepoCase):
    def test_nothing_declared_is_an_empty_list(self):
        self.assertEqual(_declared_docs(self.repo), [])

    def test_a_declared_doc_is_reported_with_its_authority(self):
        d = os.path.join(self.repo, ".knowledge", "standards", "git")
        os.makedirs(d)
        with open(os.path.join(d, "commit-messages.md"), "w", encoding="utf-8") as f:
            f.write("---\ntype: standard\nauthority: background\n---\n# x\n")
        self.assertEqual(_declared_docs(self.repo),
                         [{"path": f"{STANDARDS_DIR}/commit-messages.md",
                           "authority": "background"}])

    def test_index_md_is_excluded_as_the_bundle_own_listing(self):
        d = os.path.join(self.repo, ".knowledge", "standards", "git")
        os.makedirs(d)
        with open(os.path.join(d, "index.md"), "w", encoding="utf-8") as f:
            f.write("# listing\n")
        self.assertEqual(_declared_docs(self.repo), [])

    def test_cq_git_conventions_json_reports_defaults_with_nothing_declared(self):
        payload = _cq_json(self.repo, "conventions")
        self.assertEqual((payload["governs"], payload["declared"]), ("defaults", []))


if __name__ == "__main__":
    unittest.main()
