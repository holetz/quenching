"""Epic members in another repository's git store, offline: two bare stores side by side play
`holetz/forge` and `holetz/quenching`, and a clone of the first is the repository the epic
lives in. Nothing here reaches a network or writes into the foreign store."""

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
        seed = GitBackend(quenching)
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


if __name__ == "__main__":
    unittest.main()
