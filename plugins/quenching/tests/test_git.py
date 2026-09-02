"""The `git` pillar's six subcommands, exercised against real throwaway git repositories —
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
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.git.base import (_init_default_branch, _is_host_default, _origin_head_branch,
                                resolve_base)
from quenching.git.conventions import STANDARDS_DIR, _declared_docs
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
    def _origin_with_merged_branch(self):
        origin = os.path.join(self.tmp, "origin.git")
        os.makedirs(origin, exist_ok=True)
        _run(origin, "init", "-q", "--bare")
        _run(self.repo, "remote", "add", "origin", origin)
        _run(self.repo, "push", "-q", "-u", "origin", "main")
        _run(self.repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")

        _run(self.repo, "branch", "remote-feature")
        _run(self.repo, "checkout", "-q", "remote-feature")
        pathlib.Path(self.repo, "remote-feature.txt").write_text("remote\n", encoding="utf-8")
        _run(self.repo, "add", "remote-feature.txt")
        _run(self.repo, "commit", "-q", "-m", "remote feature")
        _run(self.repo, "push", "-q", "-u", "origin", "remote-feature")
        _run(self.repo, "checkout", "-q", "main")
        _run(self.repo, "merge", "-q", "--ff-only", "remote-feature")
        _run(self.repo, "push", "-q", "origin", "main")
        return origin

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


class Worktree(RepoCase):
    def setUp(self):
        super().setUp()
        self.relative = "shared"
        config = pathlib.Path(self.repo) / ".claude" / "quenching.json"
        config.parent.mkdir()
        config.write_text(json.dumps({"sharedPaths": [self.relative]}) + "\n", encoding="utf-8")
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

    def test_missing_optional_sections_are_omitted_not_fabricated(self):
        payload_step = _normalise_prose(self.payload_step)
        self.assertIn("Omit an absent or empty optional section", payload_step)
        self.assertIn("never replace it with invented prose", payload_step)

    def test_prose_assertions_match_reflowed_markdown(self):
        reflowed = (self.payload_step.replace("branch facts", "branch\n**facts**")
                    .replace("never replace it with invented prose",
                             "never **replace**\n`it` with invented prose"))
        payload_step = _normalise_prose(reflowed)
        self.assertIn("branch facts", payload_step)
        self.assertIn("never replace it with invented prose", payload_step)

    def test_provider_locator_fixture_keeps_github_and_azure_native(self):
        github = "append exactly `Closes #<n>` to the generated body"
        azure = "pass it as `--work-items <n>` to Azure"
        self.assertIn(github, self.payload_step)
        self.assertIn(azure, self.payload_step)
        self.assertIn("do not invent a `Closes #<n>` sentence", self.payload_step)

    def test_payload_is_shown_once_before_the_single_external_write_confirmation(self):
        self.assertEqual(self.command.count("**AskUserQuestion**"), 1)
        self.assertIn("provider-native link (or its absence)", self.payload_step)
        self.assertIn("one confirmation", self.command.lower())

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
            "not for: opening a pr",
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
            "git push --set-upstream",
            "head:refs/heads/<branch>",
            "askuserquestion",
            "origin",
            "dirty tree",
            "detached head",
            "divergent",
            "no commits\nahead",
            "/quenching:git:pr:create",
        ):
            self.assertIn(phrase.lower(), lower)

    def test_push_command_has_no_force_or_hidden_history_operation(self):
        command = PUSH_COMMAND.read_text(encoding="utf-8").lower()
        for forbidden in (
            "--force",
            "--force-with-lease",
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
        ):
            self.assertIn(phrase.lower(), lower)

    def test_revert_command_preserves_history_and_does_not_publish_or_rewrite(self):
        command = REVERT_COMMAND.read_text(encoding="utf-8").lower()
        for forbidden in (
            "git reset",
            "git rebase",
            "git push",
            "git add",
            "git commit",
            "--force",
            "--no-verify",
            "cq specs record",
        ):
            self.assertNotIn(forbidden, command)
        self.assertIn("new revert commit", command)
        self.assertIn("never resolve a conflict", command)

    def test_cleanup_selects_reported_remote_branches_before_deleting(self):
        cleanup = CLEANUP_COMMAND.read_text(encoding="utf-8").lower()
        self.assertIn("remoteBranches".lower(), cleanup)
        self.assertIn("git push origin --delete", cleanup)
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
