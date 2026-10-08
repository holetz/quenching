"""The `git` pillar's six subcommands, exercised against real throwaway git repositories —
the same choice `test_golden.py` makes for the other three pillars, taken further here
because `base`, `stale` and `conventions` read facts (refs, a branch's own description, live
worktrees, an on-disk standards folder) no filesystem-only fixture reproduces honestly.

No pre-refactor script owned this pillar, so nothing here is migrated: `pilar-git-e-specs-
agnosticas-ao-git`, task 3.5, wrote every case from the four subcommands' own contracts.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.git.base import (_init_default_branch, _is_host_default, _origin_head_branch,
                                resolve_base)
from quenching.git.conventions import STANDARDS_DIR, _declared_docs
from quenching.git.pr import (labelled_links, normalize_azure_pull_request,
                              normalize_github_pull_request, normalize_pull_request,
                              review_link)
from quenching.git.slugs import _read_specs, cmd_specs
from quenching.git.stale import (_gone_branches, _merged_branches, _merged_remote_branches,
                                 _orphan_worktrees, _unregistered_worktrees)

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
CQ = str(PLUGIN_ROOT / "assets" / "bin" / "cq")
PR_CREATE = PLUGIN_ROOT / "commands" / "git" / "pr" / "create.md"
PR_STATUS = PLUGIN_ROOT / "commands" / "git" / "pr" / "status.md"
PUSH_COMMAND = PLUGIN_ROOT / "commands" / "git" / "push.md"
REVERT_COMMAND = PLUGIN_ROOT / "commands" / "git" / "revert.md"
PR_REFERENCE = PLUGIN_ROOT / "assets" / "references" / "git" / "pr.md"
MERGE_REFERENCE = PLUGIN_ROOT / "assets" / "references" / "git" / "merge.md"
COMMIT_COMMAND = PLUGIN_ROOT / "commands" / "git" / "commit.md"
COMMIT_INCREMENTAL_COMMAND = PLUGIN_ROOT / "commands" / "git" / "commit-incremental.md"
CLEANUP_COMMAND = PLUGIN_ROOT / "commands" / "git" / "cleanup.md"
SYNC_COMMAND = PLUGIN_ROOT / "commands" / "git" / "sync.md"


def _normalise_prose(text: str) -> str:
    return " ".join(text.translate(str.maketrans("", "", "*_`")).split())


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

    def test_is_host_default_is_unknown_for_an_unknown_backend(self):
        self.assertIsNone(_is_host_default(self.repo, "unknown-provider", "main"))

    def test_is_host_default_is_unknown_when_the_host_cli_cannot_answer(self):
        # no GitHub remote in this throwaway repo — a missing or refusing host CLI reads as
        # "unknown", never as a crash.
        self.assertIsNone(_is_host_default(self.repo, "github", "main"))

    def test_is_host_default_distinguishes_a_known_github_default(self):
        result = SimpleNamespace(returncode=0, stdout="main\n")
        with mock.patch.object(subprocess, "run", return_value=result):
            self.assertTrue(_is_host_default(self.repo, "github", "main"))
            self.assertFalse(_is_host_default(self.repo, "github", "develop"))

    def test_is_host_default_asks_azure_through_its_runner(self):
        with mock.patch("quenching.git.base._az_run", return_value=(0, "main\n", "")) as run:
            self.assertTrue(_is_host_default(self.repo, "azure-boards", "main"))
        run.assert_called_once_with(self.repo, "repos", "show", "--query", "defaultBranch", "-o", "tsv")

    def test_is_host_default_is_unknown_for_an_azure_runner_failure(self):
        with mock.patch("quenching.git.base._az_run", return_value=(127, "", "missing")):
            self.assertIsNone(_is_host_default(self.repo, "azure-boards", "main"))

    def test_cq_git_base_json_matches_the_resolved_pair(self):
        payload = _cq_json(self.repo, "base")
        self.assertEqual((payload["base"], payload["isDefault"]), ("main", None))


class Specs(RepoCase):
    def setUp(self):
        super().setUp()
        _run(self.repo, "branch", "feature-a")

    def test_no_marking_reads_as_empty(self):
        lines, specs, idx = _read_specs(self.repo, "feature-a")
        self.assertEqual((lines, specs, idx), ([], [], None))

    def test_add_is_a_read_merge_write_that_preserves_other_lines(self):
        _run(self.repo, "config", "branch.feature-a.description",
             "a human wrote this by hand\nquenching-specs: 17")
        os.chdir(self.repo)
        cmd_specs(SimpleNamespace(branch="feature-a", add="23", remove=None, json=True))
        _lines, specs, _idx = _read_specs(".", "feature-a")
        self.assertEqual(specs, ["17", "23"])
        desc = subprocess.run(["git", "config", "branch.feature-a.description"],
                              capture_output=True, text=True).stdout
        self.assertIn("a human wrote this by hand", desc)
        self.assertEqual(desc.count("quenching-specs:"), 1)

    def test_adding_the_same_slug_twice_does_not_duplicate_it(self):
        os.chdir(self.repo)
        cmd_specs(SimpleNamespace(branch="feature-a", add="17", remove=None, json=True))
        cmd_specs(SimpleNamespace(branch="feature-a", add="17", remove=None, json=True))
        _lines, specs, _idx = _read_specs(".", "feature-a")
        self.assertEqual(specs, ["17"])

    def test_remove_drops_one_id_and_keeps_the_other(self):
        _run(self.repo, "config", "branch.feature-a.description", "quenching-specs: 17,23")
        _cq_json(self.repo, "specs", "feature-a", "--remove", "17")
        payload = _cq_json(self.repo, "specs", "feature-a")
        self.assertEqual(payload["specs"], ["23"])

    def test_cq_git_specs_json_round_trips_through_the_add_flag(self):
        _cq_json(self.repo, "specs", "feature-a", "--add", "41")
        payload = _cq_json(self.repo, "specs", "feature-a")
        self.assertEqual(payload["specs"], ["41"])


class Stale(RepoCase):
    def _origin_with_merged_branch(self, remote="origin"):
        remote_repo = os.path.join(self.tmp, f"{remote}.git")
        os.makedirs(remote_repo, exist_ok=True)
        _run(remote_repo, "init", "-q", "--bare")
        _run(self.repo, "remote", "add", remote, remote_repo)
        _run(self.repo, "push", "-q", "-u", remote, "main")
        _run(self.repo, "symbolic-ref", f"refs/remotes/{remote}/HEAD",
             f"refs/remotes/{remote}/main")

        _run(self.repo, "branch", "remote-feature")
        _run(self.repo, "checkout", "-q", "remote-feature")
        pathlib.Path(self.repo, "remote-feature.txt").write_text("remote\n", encoding="utf-8")
        _run(self.repo, "add", "remote-feature.txt")
        _run(self.repo, "commit", "-q", "-m", "remote feature")
        _run(self.repo, "push", "-q", "-u", remote, "remote-feature")
        _run(self.repo, "checkout", "-q", "main")
        _run(self.repo, "merge", "-q", "--ff-only", "remote-feature")
        _run(self.repo, "push", "-q", remote, "main")
        return remote_repo

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

    def test_an_unregistered_worktree_is_reported_with_branch_and_size(self):
        wt = pathlib.Path(self.tmp, "unregistered")
        _run(self.repo, "worktree", "add", "-q", "-b", "unregistered-branch", str(wt))
        (wt / "ignored.bin").write_bytes(b"payload\n")
        pointer = (wt / ".git").read_text(encoding="utf-8").split(":", 1)[1].strip()
        admin = pathlib.Path(pointer)
        (admin / "gitdir").unlink()

        rows = _cq_json(self.repo, "stale")["unregisteredWorktrees"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["path"], str(wt))
        self.assertEqual(rows[0]["branch"], "unregistered-branch")
        self.assertGreater(rows[0]["size"], 0)
        self.assertEqual(_unregistered_worktrees(self.repo), rows)

    def test_plain_sibling_clone_and_other_repository_worktree_are_silent(self):
        pathlib.Path(self.tmp, "plain").mkdir()
        clone = pathlib.Path(self.tmp, "clone")
        subprocess.run(["git", "clone", "-q", self.repo, str(clone)], check=True,
                       capture_output=True, text=True)

        other = _init_repo(os.path.join(self.tmp, "other-repo"))
        other_worktree = pathlib.Path(self.tmp, "other-worktree")
        _run(other, "worktree", "add", "-q", "-b", "other-branch", str(other_worktree))

        self.assertEqual(_cq_json(self.repo, "stale")["unregisteredWorktrees"], [])

    def test_cq_git_stale_json_excludes_base_and_reports_merged(self):
        _run(self.repo, "branch", "feature-e")
        payload = _cq_json(self.repo, "stale")
        names = {b["branch"] for b in payload["staleBranches"]}
        self.assertIn("feature-e", names)
        self.assertNotIn("main", names)

    def test_merged_origin_branch_is_reported_with_remote_identity(self):
        self._origin_with_merged_branch()
        rows = _merged_remote_branches(self.repo, "main", {"main"})
        self.assertEqual(rows, [{"remote": "origin", "branch": "remote-feature",
                                 "reasons": ["merged"]}])

    def test_origin_head_and_protected_current_branch_are_not_remote_candidates(self):
        self._origin_with_merged_branch()
        rows = _merged_remote_branches(self.repo, "main", {"main", "remote-feature"})
        self.assertEqual(rows, [])

    def test_cq_git_stale_adds_remote_list_without_changing_local_lists(self):
        self._origin_with_merged_branch()
        payload = _cq_json(self.repo, "stale")
        self.assertEqual(payload["remoteBranches"],
                         [{"remote": "origin", "branch": "remote-feature",
                           "reasons": ["merged"]}])
        self.assertIn("remote-feature", {b["branch"] for b in payload["staleBranches"]})
        self.assertEqual(payload["orphanWorktrees"], [])

    def test_cq_git_stale_reads_the_selected_remote(self):
        self._origin_with_merged_branch("upstream")
        payload = _cq_json(self.repo, "stale", "--remote", "upstream")
        self.assertEqual(payload["remote"], "upstream")
        self.assertEqual(payload["remoteBranches"],
                         [{"remote": "upstream", "branch": "remote-feature",
                           "reasons": ["merged"]}])


class Audit(RepoCase):
    """`cq git audit` — the verifier's facts read with a fixed argv inside a registered worktree."""

    def setUp(self):
        super().setUp()
        self.wt = os.path.join(self.tmp, "wt")
        _run(self.repo, "worktree", "add", "-q", "-b", "spec/1", self.wt)
        _run(self.wt, "config", "user.email", "test@example.com")
        _run(self.wt, "config", "user.name", "Test")
        pathlib.Path(self.wt, "b.txt").write_text("b\n", encoding="utf-8")
        _run(self.wt, "add", "b.txt")
        _run(self.wt, "commit", "-q", "-m", "task")
        self.sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.wt, check=True,
                                  capture_output=True, text=True).stdout.strip()

    def _audit(self, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, CQ, "git", "audit", *argv, "--json"],
                              cwd=self.repo, capture_output=True, text=True)

    def test_reports_the_worktree_facts(self):
        pathlib.Path(self.wt, "loose.txt").write_text("x\n", encoding="utf-8")
        payload = _cq_json(self.repo, "audit", "--worktree", self.wt, "--base", "main",
                           "--branch", "spec/1", "--sha", self.sha)
        self.assertEqual(payload["changed"], ["b.txt"])
        self.assertEqual(len(payload["commits"]), 1)
        self.assertEqual(payload["status"], ["?? loose.txt"])
        self.assertEqual(payload["stash"], [])
        self.assertEqual(payload["ancestry"], {self.sha: True})
        self.assertTrue(payload["reflog"]["head"])
        self.assertNotIn("gate", payload)

    def test_gate_flag_is_gone(self):
        proc = self._audit("--worktree", self.wt, "--base", "main", "--branch", "spec/1", "--gate")
        self.assertNotEqual(proc.returncode, 0)

    def test_status_does_not_run_a_configured_filter(self):
        marker = os.path.join(self.tmp, "PWNED_status")
        pathlib.Path(self.wt, ".gitattributes").write_text("*.txt filter=evil\n", encoding="utf-8")
        _run(self.wt, "add", ".gitattributes")
        _run(self.wt, "commit", "-q", "-m", "attrs")
        _run(self.repo, "config", "filter.evil.clean", f"touch {marker}; cat")
        _run(self.repo, "config", "filter.evil.required", "true")
        pathlib.Path(self.wt, "b.txt").write_text("changed\n", encoding="utf-8")
        payload = _cq_json(self.repo, "audit", "--worktree", self.wt, "--base", "main",
                           "--branch", "spec/1")
        self.assertFalse(os.path.exists(marker))
        self.assertIn(" M b.txt", payload["status"])

    def test_unregistered_worktree_is_refused(self):
        other = _init_repo(os.path.join(self.tmp, "other"))
        proc = self._audit("--worktree", other, "--base", "main", "--branch", "main")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("audit-worktree-unregistered", proc.stdout)

    def test_option_shaped_refs_are_refused_and_write_nothing(self):
        target = pathlib.Path(self.tmp, "outside")
        target.write_text("keep\n", encoding="utf-8")
        for argv in ((f"--base=--output={target}", "--branch", "spec/1"),
                     ("--base", "main", "--branch=-D"),
                     ("--base", "main", "--branch", "spec/1", f"--sha=--output={target}")):
            proc = self._audit("--worktree", self.wt, *argv)
            self.assertEqual(proc.returncode, 2, argv)
            self.assertIn("audit-ref-invalid", proc.stdout)
        self.assertEqual(target.read_text(encoding="utf-8"), "keep\n")

    def test_repository_fsmonitor_config_runs_nothing(self):
        marker = pathlib.Path(self.tmp, "pwn")
        _run(self.repo, "config", "core.fsmonitor", f"touch {marker}")
        _cq_json(self.repo, "audit", "--worktree", self.wt, "--base", "main", "--branch", "spec/1")
        self.assertFalse(marker.exists())


    def test_base_origin_excludes_a_dependency_merged_through_the_remote(self):
        remote = os.path.join(self.tmp, "origin.git")
        _run(self.tmp, "init", "-q", "--bare", "-b", "main", remote)
        _run(self.repo, "remote", "add", "origin", remote)
        _run(self.repo, "push", "-q", "origin", "main")
        other = os.path.join(self.tmp, "other")
        _run(self.tmp, "clone", "-q", remote, other)
        _run(other, "config", "user.email", "test@example.com")
        _run(other, "config", "user.name", "Test")
        pathlib.Path(other, "dep.txt").write_text("a\n", encoding="utf-8")
        _run(other, "add", "dep.txt")
        _run(other, "commit", "-q", "-m", "dep merged by gh")
        _run(other, "push", "-q", "origin", "main")
        _run(self.repo, "fetch", "-q", "origin")
        wt = os.path.join(self.tmp, "wt-c")
        _run(self.repo, "worktree", "add", "-q", "-b", "spec/c", wt, "origin/main")
        _run(wt, "config", "user.email", "test@example.com")
        _run(wt, "config", "user.name", "Test")
        pathlib.Path(wt, "c.txt").write_text("c\n", encoding="utf-8")
        _run(wt, "add", "c.txt")
        _run(wt, "commit", "-q", "-m", "task c")
        stale = _cq_json(self.repo, "audit", "--worktree", wt, "--base", "main", "--branch", "spec/c")
        fresh = _cq_json(self.repo, "audit", "--worktree", wt, "--base", "origin/main",
                         "--branch", "spec/c")
        self.assertEqual(stale["changed"], ["c.txt", "dep.txt"])
        self.assertEqual(fresh["changed"], ["c.txt"])

    def test_bodies_name_origin_base(self):
        for rel in ("agents/verifier.md", "agents/orchestrator.md", "commands/specs/conclude.md"):
            text = (PLUGIN_ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("origin/<base>", text, rel)
        verifier = (PLUGIN_ROOT / "agents" / "verifier.md").read_text(encoding="utf-8")
        self.assertIn("--base origin/<base>", verifier)


class VerifierGrants(unittest.TestCase):
    """The read-only `verifier` holds no grant whose `*` sits mid-pattern, and no raw `git` or
    `bash` grant: those admitted `branch -D`, `clean -fdx`, `--output=<file>` and arbitrary code."""

    def test_no_wildcard_mid_pattern_and_no_raw_git_or_bash(self):
        text = (PLUGIN_ROOT / "agents" / "verifier.md").read_text(encoding="utf-8")
        tools = next(line for line in text.splitlines() if line.startswith("tools:"))
        grants = re.findall(r"Bash\(([^)]*)\)", tools)
        self.assertIn("cq git audit:*", grants)
        for grant in grants:
            self.assertNotIn("*", grant.removesuffix(":*"), grant)
            self.assertFalse(grant.startswith(("git ", "bash ")), grant)

class Worktree(RepoCase):
    def setUp(self):
        super().setUp()
        self.relative = "shared"
        config = pathlib.Path(self.repo) / ".claude" / "quenching.json"
        config.parent.mkdir()
        config.write_text(json.dumps({"shared": {"sharedPaths": [self.relative]}}) + "\n",
                          encoding="utf-8")
        pathlib.Path(self.repo, ".gitignore").write_text(f"/{self.relative}\n", encoding="utf-8")
        _run(self.repo, "add", ".claude/quenching.json", ".gitignore")
        _run(self.repo, "commit", "-q", "-m", "declare shared path")

    @property
    def link(self):
        return pathlib.Path(self.repo, self.relative)

    @property
    def store(self):
        common = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=self.repo, check=True, capture_output=True, text=True).stdout.strip()
        return pathlib.Path(f"{pathlib.Path(common).parent}.{self.relative}")

    def test_absent_path_creates_the_shared_store_link(self):
        payload = _cq_json(self.repo, "worktree", "link")
        self.assertEqual(payload["paths"][0]["state"], "created")
        self.assertTrue(self.link.is_symlink())
        self.assertEqual(self.link.resolve(), self.store.resolve())

    def test_legacy_flat_shared_paths_are_refused(self):
        config = pathlib.Path(self.repo) / ".claude" / "quenching.json"
        config.write_text(json.dumps({"sharedPaths": [self.relative]}) + "\n",
                          encoding="utf-8")
        proc = subprocess.run([sys.executable, CQ, "git", "worktree", "link", "--json"],
                              cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["code"], "sp-config-unscoped")
        self.assertEqual(payload["keys"], ["sharedPaths"])
        self.assertFalse(self.link.exists())

    def test_existing_link_to_the_store_is_unchanged(self):
        self.store.mkdir()
        self.link.symlink_to(self.store)
        payload = _cq_json(self.repo, "worktree", "link")
        self.assertEqual(payload["paths"][0]["state"], "unchanged")
        self.assertTrue(self.link.is_symlink())
        self.assertEqual(self.link.resolve(), self.store.resolve())

    def test_existing_link_to_another_place_is_repointed(self):
        other = pathlib.Path(self.tmp, "other")
        other.mkdir()
        self.link.symlink_to(other)
        payload = _cq_json(self.repo, "worktree", "link")
        self.assertEqual(payload["paths"][0]["state"], "repointed")
        self.assertEqual(self.link.resolve(), self.store.resolve())

    def test_primary_and_worktree_resolve_to_the_same_store(self):
        primary = _cq_json(self.repo, "worktree", "link")
        worktree = pathlib.Path(self.tmp, "worktree")
        _run(self.repo, "worktree", "add", "-q", "-b", "shared-wt", str(worktree))
        secondary = _cq_json(str(worktree), "worktree", "link")
        self.assertEqual(primary["paths"][0]["store"], secondary["paths"][0]["store"])
        self.assertEqual(pathlib.Path(self.repo, self.relative).resolve(),
                         (worktree / self.relative).resolve())

    def test_real_directory_with_content_is_refused_without_deleting_it(self):
        self.link.mkdir()
        keep = self.link / "keep"
        keep.write_text("preserve\n", encoding="utf-8")
        proc = subprocess.run([sys.executable, CQ, "git", "worktree", "link", "--json"],
                              cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(json.loads(proc.stdout)["code"], "git-worktree-path-not-empty")
        self.assertEqual(keep.read_text(encoding="utf-8"), "preserve\n")
        self.assertFalse(self.store.exists())

    def test_directory_with_only_dotenv_is_refused_and_preserved(self):
        self.link.mkdir()
        dotenv = self.link / ".env"
        dotenv.write_text("SECRET=keep\n", encoding="utf-8")
        proc = subprocess.run([sys.executable, CQ, "git", "worktree", "link", "--json"],
                              cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(json.loads(proc.stdout)["code"], "git-worktree-path-not-empty")
        self.assertEqual(dotenv.read_text(encoding="utf-8"), "SECRET=keep\n")
        self.assertFalse(self.store.exists())

    def test_second_run_is_idempotent_and_exits_zero(self):
        _cq_json(self.repo, "worktree", "link")
        before = os.lstat(self.link)
        payload = _cq_json(self.repo, "worktree", "link")
        after = os.lstat(self.link)
        self.assertEqual(payload["paths"][0]["state"], "unchanged")
        self.assertEqual((before.st_dev, before.st_ino), (after.st_dev, after.st_ino))


class LifecycleBehavior(RepoCase):
    """The lifecycle cases that prose-only command tests cannot prove.

    Each case creates the refs it inspects and then asks Git to perform the operation. The
    command bodies still own the confirmation and refusal policy; these tests pin the Git facts
    that policy promises to show and preserve.
    """

    def _add_bare_remote(self, name="origin"):
        remote = os.path.join(self.tmp, f"{name}.git")
        os.makedirs(remote, exist_ok=True)
        _run(remote, "init", "-q", "--bare")
        _run(self.repo, "remote", "add", name, remote)
        _run(self.repo, "push", "-q", "-u", name, "main")
        return remote

    def test_rebase_then_confirmed_lease_push_replaces_only_the_expected_remote_tip(self):
        self._add_bare_remote()
        _run(self.repo, "checkout", "-q", "-b", "feature")
        pathlib.Path(self.repo, "feature.txt").write_text("feature\n", encoding="utf-8")
        _run(self.repo, "add", "feature.txt")
        _run(self.repo, "commit", "-q", "-m", "feature work")
        _run(self.repo, "push", "-q", "-u", "origin", "feature")
        old_remote_tip = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo,
                                         check=True, capture_output=True, text=True).stdout.strip()

        _run(self.repo, "checkout", "-q", "main")
        pathlib.Path(self.repo, "base.txt").write_text("base\n", encoding="utf-8")
        _run(self.repo, "add", "base.txt")
        _run(self.repo, "commit", "-q", "-m", "base advances")
        _run(self.repo, "push", "-q", "origin", "main")
        _run(self.repo, "checkout", "-q", "feature")
        _run(self.repo, "rebase", "-q", "origin/main")
        rebased_tip = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo,
                                      check=True, capture_output=True, text=True).stdout.strip()
        self.assertNotEqual(rebased_tip, old_remote_tip)

        _run(self.repo, "push", "-q", f"--force-with-lease=refs/heads/feature:{old_remote_tip}",
             "origin", "HEAD:refs/heads/feature")
        remote_tip = subprocess.run(["git", "ls-remote", "origin", "refs/heads/feature"],
                                     cwd=self.repo, check=True, capture_output=True,
                                     text=True).stdout.split()[0]
        self.assertEqual(remote_tip, rebased_tip)

    def test_revert_creates_a_new_commit_and_preserves_the_target(self):
        pathlib.Path(self.repo, "a.txt").write_text("changed\n", encoding="utf-8")
        _run(self.repo, "add", "a.txt")
        _run(self.repo, "commit", "-q", "-m", "change to compensate")
        target = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo, check=True,
                                capture_output=True, text=True).stdout.strip()

        _run(self.repo, "revert", "--no-edit", target)
        revert = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo, check=True,
                                capture_output=True, text=True).stdout.strip()
        subject = subprocess.run(["git", "show", "-s", "--format=%s", "HEAD"],
                                 cwd=self.repo, check=True, capture_output=True,
                                 text=True).stdout.strip()
        self.assertNotEqual(revert, target)
        self.assertTrue(subject.startswith("Revert \"change to compensate\""))
        self.assertEqual(pathlib.Path(self.repo, "a.txt").read_text(encoding="utf-8"), "x\n")
        _run(self.repo, "merge-base", "--is-ancestor", target, "HEAD")


class PullRequestNormalization(unittest.TestCase):
    def test_azure_keeps_rest_url_as_api_and_builds_the_browser_link(self):
        payload = {
            "pullRequestId": 42,
            "url": "https://dev.azure.com/org/proj/_apis/git/repositories/r/pullRequests/42",
            "repository": {"webUrl": "https://dev.azure.com/org/proj/_git/repo"},
        }
        expected = {
            "id": 42,
            "webUrl": "https://dev.azure.com/org/proj/_git/repo/pullrequest/42",
            "apiUrl": payload["url"],
        }
        self.assertEqual(normalize_azure_pull_request(payload), expected)
        self.assertEqual(normalize_pull_request("azure-boards", payload), expected)
        self.assertEqual(review_link(expected), expected["webUrl"])
        self.assertEqual(labelled_links(expected),
                         {"Link para revisão": expected["webUrl"], "API URL": payload["url"]})

    def test_azure_never_uses_an_api_endpoint_as_the_human_link(self):
        payload = {
            "pullRequestId": 7,
            "url": "https://dev.azure.com/org/proj/_apis/git/pullRequests/7",
            "webUrl": "https://dev.azure.com/org/proj/_apis/git/pullRequests/7",
        }
        snapshot = normalize_azure_pull_request(payload)
        self.assertIsNone(snapshot["webUrl"])
        self.assertIsNone(review_link(snapshot))

    def test_github_separates_html_url_and_derives_missing_api_url(self):
        payload = {"number": 9, "url": "https://github.com/o/r/pull/9"}
        repository = {"owner": {"login": "o"}, "name": "r"}
        self.assertEqual(normalize_github_pull_request(payload, repository), {
            "id": 9,
            "webUrl": payload["url"],
            "apiUrl": "https://api.github.com/repos/o/r/pulls/9",
        })


class Conventions(RepoCase):
    def test_nothing_declared_is_an_empty_list(self):
        self.assertEqual(_declared_docs(self.repo), [])

    def test_a_declared_doc_is_reported_with_its_authority(self):
        d = os.path.join(self.repo, "docs", "standards", "git")
        os.makedirs(d)
        with open(os.path.join(d, "commit-messages.md"), "w", encoding="utf-8") as f:
            f.write("---\ntype: standard\nauthority: background\n---\n# x\n")
        self.assertEqual(_declared_docs(self.repo),
                         [{"path": f"{STANDARDS_DIR}/commit-messages.md",
                           "authority": "background"}])

    def test_index_md_is_excluded_as_the_bundle_own_listing(self):
        d = os.path.join(self.repo, "docs", "standards", "git")
        os.makedirs(d)
        with open(os.path.join(d, "index.md"), "w", encoding="utf-8") as f:
            f.write("# listing\n")
        self.assertEqual(_declared_docs(self.repo), [])

    def test_cq_git_conventions_json_reports_defaults_with_nothing_declared(self):
        payload = _cq_json(self.repo, "conventions")
        self.assertEqual((payload["governs"], payload["declared"]), ("defaults", []))

    def _declare(self, conventions: dict) -> None:
        """Through the envelope's `shared` namespace — where every cross-front setting lives."""
        d = os.path.join(self.repo, ".claude")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "quenching.json"), "w", encoding="utf-8") as f:
            json.dump({"shared": {"gitConventions": conventions}}, f)

    def test_the_declared_directives_ride_the_payload(self):
        self._declare({"commitSubject": "[TICKET] no imperativo",
                       "prBody": "tres blocos"})
        payload = _cq_json(self.repo, "conventions")
        self.assertEqual(payload["config"], {"commitSubject": "[TICKET] no imperativo",
                                             "prBody": "tres blocos"})
        self.assertEqual(payload["configUnknown"], [])

    def test_a_sub_key_nothing_reads_comes_back_named(self):
        self._declare({"prDescription": "x"})
        payload = _cq_json(self.repo, "conventions")
        self.assertEqual((payload["config"], payload["configUnknown"]), ({}, ["prDescription"]))

    def test_governs_and_declared_still_answer_only_the_docs_layer(self):
        """The two older fields keep their meaning exactly. A config that declares every
        directive still leaves `governs: defaults` when no `docs/standards/git/**` exists —
        merging the two layers into one word would make the common case (config names some
        artifacts, the target's doc covers the rest) unreportable."""
        self._declare({"commitSubject": "x", "branchName": "y", "prTitle": "z",
                       "prBody": "w", "mergeSubject": "v"})
        payload = _cq_json(self.repo, "conventions")
        self.assertEqual((payload["governs"], payload["declared"]), ("defaults", []))
        self.assertEqual(len(payload["config"]), 5)

    def test_the_human_line_names_each_declared_directive(self):
        self._declare({"commitSubject": "[TICKET] no imperativo"})
        proc = subprocess.run([sys.executable, CQ, "git", "conventions"], cwd=self.repo,
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("gitConventions.commitSubject", proc.stdout)
        self.assertIn("[TICKET] no imperativo", proc.stdout)


class PullRequestPayload(unittest.TestCase):
    """The PR command's spec-id payload is a deterministic, fixture-shaped contract.

    The command surface is Markdown rather than executable Python. These fixtures therefore
    exercise the observable payload recipe and its provider gates without making a network call or
    pretending that a live PR can be proved offline.
    """

    @classmethod
    def setUpClass(cls):
        cls.command = PR_CREATE.read_text(encoding="utf-8")
        cls.payload_step = cls.command.split("### 2. Resolve title, body and the provider link", 1)[1]

    def test_spec_payload_names_the_canonical_sections_in_order(self):
        self.assertIn('cq specs section "<id>" \\', self.payload_step)
        positions = [self.payload_step.index(f"`{heading}`") for heading in
                     ("Problem", "Proposal", "Impact", "Validation")]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("`Tasks` summary", self.payload_step)
        self.assertIn("branch facts", _normalise_prose(self.payload_step))

    def test_pr_create_selects_a_named_remote_and_defaults_to_origin(self):
        command = self.command.lower()
        self.assertIn("remote:<name>", command)
        self.assertIn("git remote -v", command)
        self.assertIn("git remote get-url <remote>", command)
        self.assertIn("git push -u <remote> <branch>", command)
        self.assertIn("origin", command)

    def test_missing_optional_sections_are_omitted_not_fabricated(self):
        payload_step = _normalise_prose(self.payload_step)
        self.assertIn("optional", payload_step)
        self.assertIn("invent", payload_step)

    def test_prose_assertions_match_reflowed_markdown(self):
        reflowed = (self.payload_step.replace("branch facts", "branch\n**facts**")
                    .replace("never replace it with invented prose",
                             "never **replace**\n`it` with invented prose"))
        payload_step = _normalise_prose(reflowed)
        self.assertIn("branch facts", payload_step)
        self.assertIn("never replace it with invented prose", payload_step)

    def test_provider_locator_fixture_keeps_github_and_azure_native(self):
        github = "append exactly `Closes #<n>` to the generated body"
        self.assertIn("take it from the status id, never from path", _normalise_prose(self.payload_step))
        azure = "pass it as `--work-items <n>` to Azure"
        self.assertIn(github, self.payload_step)
        self.assertIn(azure, self.payload_step)
        self.assertIn("do not invent a `Closes #<n>` sentence", self.payload_step)

    def test_payload_is_shown_once_before_the_single_external_write_confirmation(self):
        self.assertEqual(self.command.count("**AskUserQuestion**"), 1)
        self.assertIn("provider-native link (or its absence)", self.payload_step)
        self.assertIn("one confirmation", self.command.lower())

    def test_azure_source_branch_deletion_is_an_explicit_offer(self):
        command = self.command.lower()
        reference = MERGE_REFERENCE.read_text(encoding="utf-8").lower()
        combined = f"{command}\n{reference}"
        self.assertIn("separate source-branch deletion offer", combined)
        self.assertIn("[--delete-source-branch true]", command)
        self.assertIn("squash", reference)

    def test_status_command_routes_both_providers_and_normalizes_the_snapshot(self):
        command = PR_STATUS.read_text(encoding="utf-8")
        reference = PR_REFERENCE.read_text(encoding="utf-8")
        combined = f"{command}\n{reference}"
        for phrase in (
            "cq specs config --json",
            "git remote get-url origin",
            "gh repo view",
            "gh pr view",
            "gh api graphql",
            "az repos pr show",
            "az repos pr list",
            "az devops invoke",
            "provider",
            "pullRequest",
            "source",
            "base",
            "checks",
            "approvals",
            "unresolvedThreads",
            "mergeability",
            "spec",
            "nextStep",
            "unknown",
            "pagination",
        ):
            self.assertIn(phrase, combined)

    def test_status_command_is_read_only_and_keeps_provider_failures_distinct(self):
        command = PR_STATUS.read_text(encoding="utf-8").lower()
        reference = PR_REFERENCE.read_text(encoding="utf-8").lower()
        combined = f"{command}\n{reference}"
        for phrase in (
            "read-only",
            "not for:",
            "/quenching:git:pr:create",
            "/quenching:git:pr:review",
            "/quenching:git:merge",
            "authentication",
            "permission",
            "not-found",
            "never pushes",
            "never push, create, edit",
        ):
            self.assertIn(phrase, combined)
        for forbidden in (
            "gh pr create",
            "gh pr merge",
            "git push",
            "az repos pr update",
            "resolvereviewthread",
            "askuserquestion",
        ):
            self.assertNotIn(forbidden, command)

    def test_push_command_resolves_destination_upstream_and_normal_refspec(self):
        command = PUSH_COMMAND.read_text(encoding="utf-8")
        lower = command.lower()
        for phrase in (
            "git status --porcelain --untracked-files=all",
            "git branch --show-current",
            "git remote -v",
            "git remote get-url <remote>",
            "cq git base --json",
            "git ls-remote",
            "git rev-list --left-right --count",
            "git log",
            "git reflog show <branch>",
            "git push --set-upstream",
            "git push --force-with-lease=refs/heads/<branch>:<expected-remote-sha>",
            "head:refs/heads/<branch>",
            "askuserquestion",
            "origin",
            "dirty tree",
            "detached head",
            "divergent",
            "no commits ahead",
            "/quenching:git:pr:create",
        ):
            self.assertIn(phrase.lower(), lower)

    def test_push_command_only_allows_a_confirmed_lease_after_proven_rebase(self):
        command = PUSH_COMMAND.read_text(encoding="utf-8").lower()
        for required in (
            "same work after a rebase",
            "expected remote sha",
            "current\nremote sha",
            "fresh confirmation",
            "unproven divergence",
        ):
            self.assertIn(required, command)
        for forbidden in (
            "git fetch",
            "git add",
            "git commit",
            "git rebase",
            "git reset",
            "git merge",
            "gh pr create",
            "--no-verify",
        ):
            self.assertNotIn(forbidden, command)
        self.assertNotIn("git push --force ", command)

    def test_revert_command_resolves_commit_or_task_and_requires_merge_mainline(self):
        command = REVERT_COMMAND.read_text(encoding="utf-8")
        lower = command.lower()
        for phrase in (
            "commit:<ref>",
            "spec:<id> task:<id>",
            "cq specs status --spec",
            "git log --grep",
            "--fixed-strings",
            "git rev-parse --verify",
            "git merge-base --is-ancestor",
            "git rev-list --parents",
            "git show",
            "git diff <target>^ <target>",
            "mainline:<n>",
            "git revert <target>",
            "git revert -m <mainline> <target>",
            "git revert --continue",
            "git revert --abort",
            "askuserquestion",
            "no spec record",
            "cq specs task --spec",
            "--uncheck",
            "--reason",
            "## discoveries",
        ):
            self.assertIn(phrase.lower(), lower)

    def test_revert_command_preserves_history_and_does_not_publish_or_rewrite(self):
        command = REVERT_COMMAND.read_text(encoding="utf-8").lower()
        for forbidden in (
            "git reset",
            "git rebase",
            "git push",
            "git add",
            "--force",
            "--no-verify",
            "cq specs record",
        ):
            self.assertNotIn(forbidden, command)
        self.assertIn("new revert commit", command)
        self.assertIn("never resolve a conflict", command)
        self.assertIn("only after", command)
        self.assertIn("new revert commit is verified", command)

    def test_cleanup_selects_reported_remote_branches_before_deleting(self):
        cleanup = CLEANUP_COMMAND.read_text(encoding="utf-8").lower()
        self.assertIn("remoteBranches".lower(), cleanup)
        self.assertIn("git push <remote> --delete", cleanup)
        self.assertIn("remote:<name>", cleanup)
        self.assertIn("--remote <remote>", cleanup)
        self.assertIn("local selection", cleanup)
        self.assertIn("remote selection", cleanup)
        self.assertIn("remote branch is never", cleanup)
        self.assertIn("confirmation", cleanup)
        self.assertEqual(cleanup.count("**askuserquestion**"), 2)

    def test_cleanup_does_not_fetch_or_prune_implicitly(self):
        cleanup = CLEANUP_COMMAND.read_text(encoding="utf-8").lower()
        self.assertIn("do not fetch", cleanup)
        self.assertIn("git remote prune", cleanup)
        self.assertIn("fresh `remotebranches` list", cleanup)

    def test_cleanup_protects_force_and_unreported_remote_deletion(self):
        cleanup = CLEANUP_COMMAND.read_text(encoding="utf-8").lower()
        self.assertIn("never delete a remote branch", cleanup)
        self.assertIn("did not report in `remotebranches`", cleanup)
        self.assertIn("git push --force", cleanup)
        self.assertIn("never --force", cleanup)


class CommitVerb(RepoCase):
    def _commit(self, *argv):
        return subprocess.run([sys.executable, CQ, "git", "commit", *argv, "--json"],
                              cwd=self.repo, capture_output=True, text=True)

    def _head(self):
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo,
                              capture_output=True, text=True).stdout.strip()

    def _stage(self, name="b.txt"):
        with open(os.path.join(self.repo, name), "w", encoding="utf-8") as f:
            f.write("b\n")
        _run(self.repo, "add", name)

    def test_commits_the_staged_index_and_reports_the_recorded_subject(self):
        self._stage()
        proc = self._commit("--subject", "plan/1-x: 1.1 Do it")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)
        self.assertEqual(out["sha"], self._head())
        self.assertEqual(out["subject"], "plan/1-x: 1.1 Do it")
        self.assertTrue(out["subjectMatches"])

    def test_refuses_an_empty_index_and_a_blank_subject(self):
        before = self._head()
        self.assertEqual(self._commit("--subject", "s").returncode, 2)
        self._stage()
        self.assertEqual(self._commit("--subject", "   ").returncode, 2)
        self.assertEqual(self._head(), before)

    def test_never_stages_on_the_callers_behalf(self):
        with open(os.path.join(self.repo, "a.txt"), "a", encoding="utf-8") as f:
            f.write("changed\n")
        self.assertEqual(self._commit("--subject", "s").returncode, 2)

    def test_hooks_run_and_a_failing_hook_leaves_head_unchanged(self):
        hook = os.path.join(self.repo, ".git", "hooks", "pre-commit")
        with open(hook, "w", encoding="utf-8") as f:
            f.write("#!/bin/sh\nexit 1\n")
        os.chmod(hook, 0o755)
        before = self._head()
        self._stage()
        self.assertEqual(self._commit("--subject", "s").returncode, 1)
        self.assertEqual(self._head(), before)


class CommitSubjectContract(unittest.TestCase):
    def test_omitted_subject_derives_or_refuses_without_a_question(self):
        command = COMMIT_COMMAND.read_text(encoding="utf-8").lower()
        self.assertNotIn("omitted → ask", command)
        self.assertIn("explicit subject always wins", command)
        self.assertIn("ambiguous or missing context", command)
        self.assertIn("refuse", command)
        self.assertNotIn("askuserquestion", command)

    def test_subject_resolution_keeps_the_staged_index_boundary(self):
        command = COMMIT_COMMAND.read_text(encoding="utf-8").lower()
        self.assertIn("commits the existing index only", command)
        self.assertIn("never `git add -a`", command)
        self.assertIn("amends history", command)


class SyncContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lower = SYNC_COMMAND.read_text(encoding="utf-8").lower()

    def test_sync_fetches_without_persisting_pruning_configuration(self):
        for phrase in ("git remote get-url origin", "git fetch origin <base>",
                       "no persistent fetch configuration is changed", "no-remote"):
            self.assertIn(phrase, self.lower)
        for forbidden in ("git config fetch.prune", "fetch.prune=true", "configure fetch.prune",
                          "pruning configuration"):
            self.assertNotIn(forbidden, self.lower)

    def test_sync_hands_rebased_publication_to_push_with_a_lease(self):
        self.assertIn("force-with-lease", self.lower)
        self.assertIn("git:push", self.lower)
        self.assertIn("do not publish", self.lower)


class IncrementalCommitContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.command = COMMIT_INCREMENTAL_COMMAND.read_text(encoding="utf-8")
        cls.lower = cls.command.lower()

    def test_snapshot_covers_clean_staged_unstaged_and_untracked_states(self):
        for phrase in ("git status --short", "git diff --name-status", "git diff --cached --name-status",
                       "git ls-files --others --exclude-standard", "clean\nsnapshot", "no-op"):
            self.assertIn(phrase.lower(), self.lower)

    def test_safety_guards_stop_before_staging(self):
        for phrase in ("unmerged", "pre-staging refusal", "credential", "secret", "cannot be read safely",
                       "no `git add` run before every guard passes"):
            self.assertIn(phrase.lower(), self.lower)

    def test_each_group_stages_explicit_paths_without_broad_selectors(self):
        self.assertIn("git add --", self.lower)
        self.assertIn("explicit path list", self.lower)
        self.assertIn("never uses `git add -a`", self.lower)
        self.assertIn("git add .", self.lower)

    def test_subjects_are_resolved_without_interaction_and_reported(self):
        for phrase in ("gitconventions.commitSubject", "chore: <short english imperative>",
                       "one short imperative subject", "resolved english subject"):
            self.assertIn(phrase.lower(), self.lower)
        self.assertIn("askuserquestion", self.lower)
        self.assertIn("with one confirmation", self.lower)
        self.assertNotIn("without confirmation", self.lower)

    def test_content_guards_have_bounded_reads_and_do_not_report_secret_values(self):
        for phrase in ("1 mib per file", "10 mib total", "scan content, not only filenames",
                       "private-key headers", "api[_-]?key", "client[_-]?secret",
                       "never the value"):
            self.assertIn(phrase, self.lower)

    def test_hooks_and_failures_preserve_previous_commits_and_residue(self):
        for phrase in ("hooks stay enabled", "if staging fails\nor a commit fails", "leave earlier commits intact",
                       "preserve the remaining\nworktree changes", "never amend, reset"):
            self.assertIn(phrase.lower(), self.lower)
        self.assertIn("--no-verify", self.lower)
        self.assertIn("--no-gpg-sign", self.lower)


if __name__ == "__main__":
    unittest.main()


def _cq(cwd: str, *argv: str, stdin: str | None = None,
        env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, CQ, "git", *argv, "--json"], cwd=cwd, input=stdin,
                          capture_output=True, text=True, env=env)


def _sha(cwd: str, ref: str = "HEAD") -> str:
    return subprocess.run(["git", "rev-parse", ref], cwd=cwd, check=True, capture_output=True,
                          text=True).stdout.strip()


class State(RepoCase):
    """`cq git state` — what the bodies read before acting, with no `Bash(git …)` grant."""

    def test_reports_branch_status_staged_and_remotes(self):
        _run(self.repo, "remote", "add", "origin", "https://example.invalid/o/r.git")
        pathlib.Path(self.repo, "new.txt").write_text("n\n", encoding="utf-8")
        pathlib.Path(self.repo, "staged.txt").write_text("s\n", encoding="utf-8")
        _run(self.repo, "add", "staged.txt")
        payload = _cq_json(self.repo, "state")
        self.assertEqual(payload["branch"], "main")
        self.assertIn("?? new.txt", payload["status"])
        self.assertEqual(payload["staged"], ["staged.txt"])
        self.assertEqual(payload["remotes"], {"origin": "https://example.invalid/o/r.git"})

    def test_repository_config_runs_nothing(self):
        marker = pathlib.Path(self.tmp, "pwn")
        _run(self.repo, "config", "core.fsmonitor", f"touch {marker}")
        pathlib.Path(self.repo, ".gitattributes").write_text("*.txt filter=evil\n", encoding="utf-8")
        _run(self.repo, "config", "filter.evil.clean", f"touch {marker}; cat")
        pathlib.Path(self.repo, "a.txt").write_text("changed\n", encoding="utf-8")
        _cq_json(self.repo, "state")
        self.assertFalse(marker.exists())


class WorktreeAdd(RepoCase):
    """`cq git worktree add` — the `branch` step's cut, from the fetched remote base."""

    def setUp(self):
        super().setUp()
        self.remote = os.path.join(self.tmp, "origin.git")
        _run(self.tmp, "init", "-q", "--bare", "-b", "main", self.remote)
        _run(self.repo, "remote", "add", "origin", self.remote)
        _run(self.repo, "push", "-q", "origin", "main")
        other = os.path.join(self.tmp, "other")
        _run(self.tmp, "clone", "-q", self.remote, other)
        _run(other, "config", "user.email", "test@example.com")
        _run(other, "config", "user.name", "Test")
        pathlib.Path(other, "dep.txt").write_text("d\n", encoding="utf-8")
        _run(other, "add", "dep.txt")
        _run(other, "commit", "-q", "-m", "dependency merged through gh")
        _run(other, "push", "-q", "origin", "main")
        self.remote_tip = _sha(other)
        self.path = os.path.join(self.tmp, "wt")

    def test_cuts_from_the_fetched_remote_base_with_no_upstream(self):
        payload = _cq_json(self.repo, "worktree", "add", "--path", self.path,
                           "--branch", "plan/1-x", "--base", "main")
        self.assertTrue(payload["fromRemote"])
        self.assertEqual(payload["startSha"], self.remote_tip)
        self.assertEqual(_sha(self.path), self.remote_tip)
        upstream = subprocess.run(["git", "rev-parse", "--abbrev-ref", "plan/1-x@{upstream}"],
                                  cwd=self.path, capture_output=True, text=True)
        self.assertNotEqual(upstream.returncode, 0)

    def test_without_the_remote_falls_back_to_the_local_base_and_says_so(self):
        _run(self.repo, "remote", "remove", "origin")
        payload = _cq_json(self.repo, "worktree", "add", "--path", self.path,
                           "--branch", "plan/1-x", "--base", "main")
        self.assertFalse(payload["fromRemote"])
        self.assertEqual(payload["startSha"], _sha(self.repo, "main"))

    def test_links_the_declared_shared_paths_in_the_new_worktree(self):
        config = pathlib.Path(self.repo, ".claude", "quenching.json")
        config.parent.mkdir()
        config.write_text(json.dumps({"shared": {"sharedPaths": ["shared"]}}) + "\n",
                          encoding="utf-8")
        pathlib.Path(self.repo, ".gitignore").write_text("/shared\n", encoding="utf-8")
        _run(self.repo, "add", ".claude/quenching.json", ".gitignore")
        _run(self.repo, "commit", "-q", "-m", "declare shared path")
        _run(self.repo, "push", "-q", "origin", "main:main", "--force")
        payload = _cq_json(self.repo, "worktree", "add", "--path", self.path,
                           "--branch", "plan/1-x", "--base", "main")
        self.assertEqual([p["state"] for p in payload["paths"]], ["created"])
        self.assertTrue(os.path.islink(os.path.join(self.path, "shared")))

    def test_option_shaped_names_and_taken_targets_are_refused_and_create_nothing(self):
        cases = (("--branch=-D", "--base", "main", "--path", self.path),
                 ("--branch", "plan/1-x", "--base=--output=/tmp/x", "--path", self.path),
                 ("--branch", "plan/1-x", "--base", "main", "--remote=--upload-pack=touch",
                  "--path", self.path),
                 ("--branch", "main", "--base", "main", "--path", self.path),
                 ("--branch", "plan/1-x", "--base", "main", "--path", self.repo))
        for argv in cases:
            proc = _cq(self.repo, "worktree", "add", *argv)
            self.assertEqual(proc.returncode, 2, (argv, proc.stdout))
        self.assertFalse(os.path.exists(self.path))
        branches = subprocess.run(["git", "branch", "--list", "plan/*"], cwd=self.repo,
                                  capture_output=True, text=True).stdout
        self.assertEqual(branches.strip(), "")

    def test_repository_hooks_and_fsmonitor_run_nothing(self):
        marker = pathlib.Path(self.tmp, "pwn")
        hooks = pathlib.Path(self.repo, ".git", "hooks", "post-checkout")
        hooks.write_text(f"#!/bin/sh\ntouch {marker}\n", encoding="utf-8")
        hooks.chmod(0o755)
        _run(self.repo, "config", "core.fsmonitor", f"touch {marker}")
        _cq_json(self.repo, "worktree", "add", "--path", self.path, "--branch", "plan/1-x",
                 "--base", "main")
        self.assertFalse(marker.exists())


class PushVerb(RepoCase):
    """`cq git push` — one local branch to one configured remote, never forced."""

    def setUp(self):
        super().setUp()
        self.remote = os.path.join(self.tmp, "origin.git")
        _run(self.tmp, "init", "-q", "--bare", "-b", "main", self.remote)
        _run(self.repo, "remote", "add", "origin", self.remote)
        _run(self.repo, "push", "-q", "origin", "main")
        _run(self.repo, "checkout", "-q", "-b", "plan/1-x")
        pathlib.Path(self.repo, "b.txt").write_text("b\n", encoding="utf-8")
        _run(self.repo, "add", "b.txt")
        _run(self.repo, "commit", "-q", "-m", "task")

    def test_pushes_under_its_own_name_and_sets_upstream(self):
        payload = _cq_json(self.repo, "push", "--branch", "plan/1-x")
        self.assertEqual(payload["sha"], _sha(self.repo))
        self.assertEqual(_sha(self.remote, "refs/heads/plan/1-x"), _sha(self.repo))
        upstream = subprocess.run(["git", "rev-parse", "--abbrev-ref", "plan/1-x@{upstream}"],
                                  cwd=self.repo, capture_output=True, text=True).stdout.strip()
        self.assertEqual(upstream, "origin/plan/1-x")

    def test_a_rewritten_branch_is_refused_not_forced(self):
        _cq_json(self.repo, "push", "--branch", "plan/1-x")
        before = _sha(self.remote, "refs/heads/plan/1-x")
        _run(self.repo, "commit", "-q", "--amend", "-m", "rewritten")
        proc = _cq(self.repo, "push", "--branch", "plan/1-x")
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertEqual(_sha(self.remote, "refs/heads/plan/1-x"), before)

    def test_option_shaped_or_unknown_names_are_refused(self):
        for argv in (("--branch=--force",), ("--branch", "+plan/1-x"),
                     ("--branch", "nope"), ("--branch", "plan/1-x", "--remote=--mirror"),
                     ("--branch", "plan/1-x", "--remote", "elsewhere")):
            proc = _cq(self.repo, "push", *argv)
            self.assertEqual(proc.returncode, 2, (argv, proc.stdout))
        heads = subprocess.run(["git", "for-each-ref", "refs/heads"], cwd=self.remote,
                               capture_output=True, text=True).stdout
        self.assertNotIn("plan/1-x", heads)


class PruneVerb(RepoCase):
    """`cq git prune` — acts only on what a fresh `cq git stale` reports, never by force."""

    def setUp(self):
        super().setUp()
        _run(self.repo, "branch", "merged")
        _run(self.repo, "checkout", "-q", "-b", "unmerged")
        pathlib.Path(self.repo, "u.txt").write_text("u\n", encoding="utf-8")
        _run(self.repo, "add", "u.txt")
        _run(self.repo, "commit", "-q", "-m", "unmerged work")
        _run(self.repo, "checkout", "-q", "main")

    def _branches(self) -> str:
        return subprocess.run(["git", "branch", "--list"], cwd=self.repo, capture_output=True,
                              text=True).stdout

    def test_a_reported_merged_branch_is_deleted(self):
        _cq_json(self.repo, "prune", "--branch", "merged")
        self.assertNotIn("merged", self._branches().replace("unmerged", ""))

    def test_an_unreported_branch_is_refused_and_stands(self):
        for argv in (("--branch", "unmerged"), ("--branch", "main"), ("--branch=-D",),
                     ("--worktree", self.repo), ("--remote-branch", "main")):
            proc = _cq(self.repo, "prune", *argv)
            self.assertEqual(proc.returncode, 2, (argv, proc.stdout))
        self.assertIn("unmerged", self._branches())

    def test_a_reported_remote_branch_is_deleted_on_that_remote_only(self):
        remote = os.path.join(self.tmp, "origin.git")
        _run(self.tmp, "init", "-q", "--bare", "-b", "main", remote)
        _run(self.repo, "remote", "add", "origin", remote)
        _run(self.repo, "push", "-q", "origin", "main", "merged", "unmerged")
        _run(self.repo, "fetch", "-q", "origin")
        refused = _cq(self.repo, "prune", "--remote-branch", "unmerged")
        self.assertEqual(refused.returncode, 2)
        _cq_json(self.repo, "prune", "--remote-branch", "merged")
        heads = subprocess.run(["git", "for-each-ref", "--format=%(refname)", "refs/heads"],
                               cwd=remote, capture_output=True, text=True).stdout.split()
        self.assertEqual(sorted(heads), ["refs/heads/main", "refs/heads/unmerged"])


FAKE_GH = """#!/usr/bin/env python3
import json, os, sys
log = os.environ["FAKE_GH_LOG"]
with open(log, "a", encoding="utf-8") as f:
    f.write(json.dumps({"argv": sys.argv[1:], "stdin": "" if sys.stdin.isatty() else sys.stdin.read()}) + "\\n")
if sys.argv[1:3] == ["pr", "checks"]:
    sys.stdout.write(os.environ.get("FAKE_GH_CHECKS", "[]"))
    sys.stderr.write(os.environ.get("FAKE_GH_CHECKS_ERR", ""))
    sys.exit(int(os.environ.get("FAKE_GH_CHECKS_RC", "0")))
if sys.argv[1:3] == ["pr", "create"]:
    print("https://github.com/o/r/pull/42")
sys.exit(0)
"""


class PullRequestVerbs(RepoCase):
    """`cq git pr create|merge` — the steward's PR writes, through a fake `gh` on PATH."""

    URL = "https://github.com/o/r/pull/42"

    def setUp(self):
        super().setUp()
        bindir = pathlib.Path(self.tmp, "bin")
        bindir.mkdir()
        gh = bindir / "gh"
        gh.write_text(FAKE_GH, encoding="utf-8")
        gh.chmod(0o755)
        self.log = pathlib.Path(self.tmp, "gh.log")
        self.env = {**os.environ, "PATH": f"{bindir}{os.pathsep}{os.environ['PATH']}",
                    "FAKE_GH_LOG": str(self.log)}

    def _calls(self) -> list[dict]:
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()]

    def _merge(self, checks: str, rc: str = "0", err: str = "") -> subprocess.CompletedProcess:
        env = {**self.env, "FAKE_GH_CHECKS": checks, "FAKE_GH_CHECKS_RC": rc,
               "FAKE_GH_CHECKS_ERR": err}
        return _cq(self.repo, "pr", "merge", "--url", self.URL, env=env)

    def _merge_calls(self) -> list[list[str]]:
        return [c["argv"] for c in self._calls() if c["argv"][:2] == ["pr", "merge"]]

    def test_all_green_merges_with_merge_only(self):
        proc = self._merge('[{"name":"gate","bucket":"pass"},{"name":"x","bucket":"skipping"}]')
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(self._merge_calls(), [["pr", "merge", self.URL, "--merge"]])

    def test_red_pending_or_absent_checks_never_merge(self):
        cases = (('[{"name":"gate","bucket":"fail"}]', "1", "", "failed"),
                 ('[{"name":"gate","bucket":"pending"}]', "8", "", "pending"),
                 ('[{"name":"gate"}]', "0", "", "pending"),
                 ("", "1", "no checks reported on the 'x' branch", "no-checks"),
                 ("not json", "1", "boom", "checks-unreadable"))
        for checks, rc, err, reason in cases:
            proc = self._merge(checks, rc, err)
            self.assertEqual(proc.returncode, 1, (checks, proc.stdout))
            self.assertEqual(json.loads(proc.stdout)["reason"], reason)
        self.assertEqual(self._merge_calls(), [])

    def test_option_shaped_url_and_out_of_range_wait_are_refused(self):
        for argv in (("--url=-d",), ("--url", f"{self.URL} --squash"),
                     ("--url", self.URL, "--wait", "600")):
            proc = _cq(self.repo, "pr", "merge", *argv, env=self.env)
            self.assertEqual(proc.returncode, 2, (argv, proc.stdout))
        self.assertEqual(self._calls(), [])

    def test_pending_is_re_read_until_green_within_the_wait(self):
        from quenching.git import pull
        answers = iter([("pending", [{"name": "gate", "bucket": "pending"}], ""),
                        ("green", [{"name": "gate", "bucket": "pass"}], "")])
        with mock.patch.object(pull, "_checks", side_effect=lambda url: next(answers)), \
                mock.patch.object(pull, "_gh", return_value=(0, "", "")) as gh, \
                mock.patch.object(pull.time, "sleep") as sleep, \
                contextlib.redirect_stdout(io.StringIO()):
            code = pull.cmd_pr(SimpleNamespace(action="merge", url=self.URL, wait=60, json=True))
        self.assertEqual(code, 0)
        sleep.assert_called_once_with(pull.POLL_S)
        gh.assert_called_once_with("pr", "merge", self.URL, "--merge")

    def test_create_names_base_and_head_and_sends_the_body_on_stdin(self):
        payload = _cq(self.repo, "pr", "create", "--base", "main", "--head", "plan/1-x",
                      "--title", "-a title that looks like a flag", "--body", "Closes #1",
                      env=self.env)
        self.assertEqual(payload.returncode, 0, payload.stderr)
        self.assertEqual(json.loads(payload.stdout)["number"], 42)
        (call,) = self._calls()
        self.assertEqual(call["argv"], ["pr", "create", "--base=main", "--head=plan/1-x",
                                        "--title=-a title that looks like a flag",
                                        "--body-file=-"])
        self.assertEqual(call["stdin"], "Closes #1")

    def test_create_refuses_option_shaped_branches(self):
        for argv in (("--base=-d", "--head", "plan/1-x"), ("--base", "main", "--head=--web")):
            proc = _cq(self.repo, "pr", "create", *argv, "--title", "t", env=self.env)
            self.assertEqual(proc.returncode, 2, (argv, proc.stdout))
        self.assertEqual(self._calls(), [])
