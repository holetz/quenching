"""Epic members in another repository's git store, offline: two bare stores side by side play
`holetz/forge` and `holetz/quenching`, and a clone of the first is the repository the epic
lives in. Nothing here reaches a network or writes into the foreign store."""

import argparse
import contextlib
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
import test_specs_backends as canonical
from quenching.specs import backends as backends_mod
from quenching.specs import members as members_mod
from quenching.specs.backends import git as git_mod
from quenching.specs.backends.git import GitBackend
from quenching.specs.commands import epic as epic_cmd
from quenching.specs.commands import next as next_cmd
from quenching.specs.commands import promote as promote_cmd
from quenching.specs.commands import read as read_cmd
from quenching.specs.commands import validate as validate_cmd
from quenching.specs.commands.output import Emitter
from quenching.specs.parse.fields import set_frontmatter_key
from quenching.specs.members import own_repo, read_members, sibling_url


def _sh(cwd: str, *argv: str) -> str:
    run = subprocess.run(["git", *argv], cwd=cwd, capture_output=True, text=True)
    if run.returncode != 0:
        raise AssertionError(f"git {' '.join(argv)} failed: {run.stderr}")
    return run.stdout


class SiblingUrl(unittest.TestCase):
    def test_the_trailing_owner_and_repo_are_swapped_in_every_url_shape(self):
        cases = {
            "https://github.com/holetz/forge.git": "https://github.com/holetz/quenching.git",
            "https://github.com/holetz/forge": "https://github.com/holetz/quenching",
            "git@github.com:holetz/forge.git": "git@github.com:holetz/quenching.git",
            "/srv/stores/holetz/forge.git": "/srv/stores/holetz/quenching.git",
        }
        for url, want in cases.items():
            with self.subTest(url=url):
                self.assertEqual("holetz/forge", own_repo(url))
                self.assertEqual(want, sibling_url(url, "holetz/quenching"))

    def test_an_azure_devops_url_has_no_sibling(self):
        url = "https://dev.azure.com/org/project/_git/forge"
        self.assertIsNone(own_repo(url))
        self.assertIsNone(sibling_url(url, "holetz/quenching"))


class TwoStores(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="quenching-epic-members-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        env = {"XDG_CACHE_HOME": os.path.join(self.tmp, "cache"),
               "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.test",
               "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.test"}
        patcher = mock.patch.dict(os.environ, env)
        patcher.start()
        self.addCleanup(patcher.stop)
        os.environ.pop(git_mod.NO_FETCH_ENV, None)
        for cache in (git_mod._STORES, backends_mod._BACKEND_CACHE, members_mod._FOREIGN):
            cache.clear()
            self.addCleanup(cache.clear)
        owner = os.path.join(self.tmp, "holetz")
        os.makedirs(owner)
        self.forge_remote = os.path.join(owner, "forge.git")
        self.quenching_remote = os.path.join(owner, "quenching.git")
        for remote in (self.forge_remote, self.quenching_remote):
            _sh(self.tmp, "init", "--quiet", "--bare", remote)
        self.forge = os.path.join(self.tmp, "forge")
        _sh(self.tmp, "clone", "--quiet", self.forge_remote, self.forge)
        quenching = os.path.join(self.tmp, "quenching")
        _sh(self.tmp, "clone", "--quiet", self.quenching_remote, quenching)
        self.local = GitBackend(self.forge)
        self.local.create_spec("plans", canonical._case_doc("Forge one"))
        self.seed = seed = GitBackend(quenching)
        seed.create_spec("plans", canonical._case_doc("Quenching one"))
        seed.create_spec("plans", canonical._case_doc("Quenching two"))
        self.quenching_tip = _sh(self.quenching_remote, "rev-parse", "quenching").strip()

    def read(self, keys):
        return read_members(self.local, keys, self.forge)

    def test_a_mixed_list_reads_each_store_once_and_keys_by_the_item(self):
        calls = []
        real = GitBackend.read_specs

        def spy(backend, ids):
            calls.append((backend.mirror_dir is not None, sorted(ids)))
            return real(backend, ids)

        with mock.patch.object(GitBackend, "read_specs", spy):
            members, unreadable = self.read(["1", "holetz/quenching#2", "holetz/quenching#9"])
        self.assertEqual(set(), unreadable)
        self.assertEqual("Forge one", members["1"]["frontmatter"]["title"])
        self.assertEqual("Quenching two", members["holetz/quenching#2"]["frontmatter"]["title"])
        self.assertIsNone(members["holetz/quenching#9"])
        self.assertEqual([(False, ["1"]), (True, ["2", "9"])], calls)

    def test_a_reference_to_this_repository_is_the_bare_member(self):
        members, unreadable = self.read(["holetz/forge#1"])
        self.assertEqual(set(), unreadable)
        self.assertEqual("Forge one", members["holetz/forge#1"]["frontmatter"]["title"])
        self.assertEqual({}, members_mod._FOREIGN)

    def test_a_store_that_cannot_be_read_is_unreadable_never_missing(self):
        members, unreadable = self.read(["1", "holetz/absent#1"])
        self.assertEqual({"holetz/absent#1"}, unreadable)
        self.assertIsNone(members["holetz/absent#1"])
        self.assertEqual("Forge one", members["1"]["frontmatter"]["title"])

    def test_no_fetch_without_a_mirror_is_unreadable(self):
        with mock.patch.dict(os.environ, {git_mod.NO_FETCH_ENV: "1"}):
            _, unreadable = self.read(["holetz/quenching#1"])
        self.assertEqual({"holetz/quenching#1"}, unreadable)

    def test_nothing_is_written_into_either_repository(self):
        forge_refs = _sh(self.forge, "for-each-ref", "--format=%(refname)")
        self.read(["holetz/quenching#1"])
        self.assertEqual(self.quenching_tip,
                         _sh(self.quenching_remote, "rev-parse", "quenching").strip())
        self.assertEqual(forge_refs, _sh(self.forge, "for-each-ref", "--format=%(refname)"))
        mirrors = os.path.join(self.tmp, "cache", "quenching", "mirrors")
        self.assertEqual(1, len(os.listdir(mirrors)))



EPIC_TASKS = ("## Tasks\n\n### 1. Wave\n"
              "- [ ] S1 Quenching one — spec: holetz/quenching#1\n"
              "- [ ] S2 Quenching two — spec: holetz/quenching#2 — after: S1\n")
EPIC_CLOSE = ("\n## Proposal\n\nx\n\n## Out of Scope\n\n- none — x\n\n## Validation\n\nx\n"
              "\n## Design\n\nx\n\n## Outcome\n\nx\n")


class CrossRepositoryEpic(TwoStores):
    """The epic verbs over an epic in `forge` whose items live in `quenching`."""

    def setUp(self):
        super().setUp()
        info, _ = self.seed.read_spec(1)
        self.seed.write_spec(info, set_frontmatter_key(info["text"], "outcome", "done"))
        self.seed.move_spec(self.seed.read_spec(1)[0], "archive")
        info, _ = self.seed.read_spec(2)
        self.seed.write_spec(info, set_frontmatter_key(info["text"], "approved", "2026-10-24"))
        self.quenching_tip = _sh(self.quenching_remote, "rev-parse", "quenching").strip()
        self.epic = "2"
        self.local.create_spec("plans", "---\ntitle: Program\ndate: 2026-10-24\n"
                               "workItemType: epic\n---\n\n## Problem\n\nx\n\n" + EPIC_TASKS)

    def run_cmd(self, fn, **kw):
        args = argparse.Namespace(json=True, **kw)
        buf = io.StringIO()
        with contextlib.ExitStack() as stack:
            for mod in (epic_cmd, next_cmd, promote_cmd, read_cmd, validate_cmd):
                stack.enter_context(mock.patch.object(mod, "open_backend",
                                                      return_value=(self.local, {})))
            stack.enter_context(contextlib.redirect_stdout(buf))
            code = fn(args, self.forge, Emitter())
        text = buf.getvalue().strip()
        return code, (json.loads(text) if text else {})

    def extend_epic(self, line):
        info, _ = self.local.read_spec(self.epic)
        self.local.write_spec(info, info["text"] + line)

    def status(self):
        code, got = self.run_cmd(read_cmd.cmd_status, epic=self.epic, spec=None)
        self.assertEqual(0, code, got)
        return got

    def test_status_derives_the_item_from_the_member_in_its_own_store(self):
        got = self.status()
        rows = {r["label"]: r for r in got["items"]}
        self.assertEqual(("done", "archive"), (rows["S1"]["status"], rows["S1"]["stage"]))
        self.assertEqual("holetz/quenching#2", rows["S2"]["spec"])
        self.assertNotEqual("missing", rows["S2"]["status"])

    def test_next_offers_the_foreign_member_once_its_local_dependency_is_done(self):
        code, got = self.run_cmd(next_cmd.cmd_next, epic=self.epic, spec=None, front=False,
                                 limit=None)
        self.assertEqual(0, code, got)
        self.assertEqual(["S2"], [r["label"] for r in got["ready"]])

    def test_an_unreadable_store_blocks_its_item_and_validate_only_warns(self):
        self.extend_epic("- [ ] S3 Elsewhere — spec: holetz/absent#1\n"
                         "- [ ] S4 Ghost — spec: holetz/quenching#9\n")
        blocked = {b["label"]: b for b in self.status()["blocked"]}
        self.assertEqual("unreadable", blocked["S3"]["status"])
        self.assertIn("holetz/absent", blocked["S3"]["reasons"][0])
        _, got = self.run_cmd(validate_cmd.cmd_validate, spec=None, phase=None, by_code=False)
        found = {(f["code"], f["severity"]) for f in got["findings"]
                 if f["code"].startswith("sp-epic")}
        self.assertIn(("sp-epic-member-unreadable", "warn"), found)
        self.assertIn(("sp-epic-missing-member", "error"), found)
        self.assertNotIn("sp-epic-divergent", {c for c, _ in found})

    def test_add_lists_a_reference_with_its_foreign_title_and_writes_nothing_there(self):
        info, _ = self.local.read_spec(self.epic)
        self.local.write_spec(info, info["text"].replace(
            "- [ ] S2 Quenching two — spec: holetz/quenching#2 — after: S1\n", ""))
        code, got = self.run_cmd(epic_cmd.cmd_epic, epic_cmd="add", epic=self.epic,
                                 spec="Holetz/Quenching#2", after="S1", group=None, label=None)
        self.assertEqual((0, "holetz/quenching#2"), (code, got["spec"]), got)
        text = self.local.read_spec(self.epic)[0]["text"]
        self.assertIn("Quenching two — spec: holetz/quenching#2 — after: S1", text)
        self.assertEqual(self.quenching_tip,
                         _sh(self.quenching_remote, "rev-parse", "quenching").strip())

    def test_add_refuses_a_reference_whose_store_cannot_be_read(self):
        code, got = self.run_cmd(epic_cmd.cmd_epic, epic_cmd="add", epic=self.epic,
                                 spec="holetz/absent#1", after=None, group=None, label=None)
        self.assertEqual((2, "sp-epic-member-unreadable"), (code, got.get("code")))

    def test_the_epic_does_not_archive_as_done_while_a_foreign_member_is_open(self):
        self.extend_epic(EPIC_CLOSE)
        code, got = self.run_cmd(promote_cmd.cmd_promote, spec=self.epic, to=None,
                                 outcome="done", force=False, dry_run=True)
        self.assertEqual((2, "sp-open-tasks", 1), (code, got.get("code"), got.get("open")), got)


    def test_a_foreign_member_pr_is_read_against_its_own_repository(self):
        member = {"phase": "archive", "frontmatter": {"pr": {"number": 7}}}
        seen = []

        def fake_run(argv, **kw):
            seen.append(argv)
            return subprocess.CompletedProcess(argv, 0, '{"state": "MERGED"}', "")

        with mock.patch.object(epic_cmd.subprocess, "run", fake_run):
            got = epic_cmd.pr_states({"holetz/quenching#5": member}, self.forge)
        self.assertEqual({"holetz/quenching#5": "MERGED"}, got)
        self.assertEqual(["--repo", "holetz/quenching"], seen[0][4:6])


if __name__ == "__main__":
    unittest.main()
