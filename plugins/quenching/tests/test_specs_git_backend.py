"""The `git` store backend, offline: a temporary bare repository is the remote and temporary
clones are the writers. Nothing here reaches a network or the repository under test.

The canonical sequence the external providers share runs against `GitBackend` too, and its
observations must equal both the memory fake's and the GitHub transport fixture's."""

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
from quenching.specs import config as config_mod
from quenching.specs.backends import git as git_mod
from quenching.specs.backends import github as gh_mod
from quenching.specs.backends.base import BackendRefusal
from quenching.specs.backends.git import COUNTER_PATH, GitBackend
from quenching.specs.backends.github import GitHubBackend
from quenching.specs.backends.memory import MemoryBackend


def _sh(cwd: str, *argv: str) -> str:
    run = subprocess.run(["git", *argv], cwd=cwd, capture_output=True, text=True)
    if run.returncode != 0:
        raise AssertionError(f"git {' '.join(argv)} failed: {run.stderr}")
    return run.stdout


class GitStoreFixture(unittest.TestCase):
    """A bare remote plus clones, an isolated cache home and a committer identity."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="quenching-git-store-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        env = {"XDG_CACHE_HOME": os.path.join(self.tmp, "cache"),
               "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.test",
               "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.test"}
        patcher = mock.patch.dict(os.environ, env)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.remote = os.path.join(self.tmp, "remote.git")
        _sh(self.tmp, "init", "--quiet", "--bare", self.remote)
        git_mod._STORES.clear()
        backends_mod._BACKEND_CACHE.clear()
        self.addCleanup(git_mod._STORES.clear)
        self.addCleanup(backends_mod._BACKEND_CACHE.clear)

    def clone(self, name: str) -> str:
        path = os.path.join(self.tmp, name)
        _sh(self.tmp, "clone", "--quiet", self.remote, path)
        return path

    def remote_log(self) -> list[str]:
        return _sh(self.remote, "log", "--format=%s", "quenching").splitlines()

    def remote_file(self, path: str) -> str:
        run = subprocess.run(["git", "cat-file", "blob", f"quenching:{path}"], cwd=self.remote,
                             capture_output=True, check=True)
        return run.stdout.decode("utf-8")


class CanonicalEquivalence(GitStoreFixture):
    """The shared five-primitive sequence observes the same thing through every store."""

    def test_git_agrees_with_the_memory_fake_and_the_github_fixture(self):
        git_result = canonical._external_sequence(GitBackend(self.clone("a")))
        memory_result = canonical._external_sequence(MemoryBackend())
        transport = canonical.GithubRemoteFixture()
        github = GitHubBackend("owner/repo", os.getcwd(), types={"incidente": "Bug"},
                               open_issues=0)
        with mock.patch.object(gh_mod, "_gh_run", side_effect=transport):
            github_result = canonical._external_sequence(github)
        self.assertEqual(set(git_result), set(memory_result))
        for step in git_result:
            if step == "allocatedId":
                continue
            for other in (memory_result, github_result):
                with self.subTest(step=step):
                    self.assertEqual(json.dumps(git_result[step], sort_keys=True, default=str),
                                     json.dumps(other[step], sort_keys=True, default=str))
        self.assertEqual(git_result["allocatedId"], 1)

    def test_the_document_round_trips_byte_for_byte(self):
        backend = GitBackend(self.clone("a"))
        text = "---\ntitle: Ação\n---\r\n\n## Problem\r\n\ntrailing   \n\tno final newline"
        backend.create_spec("plans", text)
        fresh = GitBackend(self.clone("b"))
        info, err = fresh.read_spec(1)
        self.assertEqual({}, err)
        self.assertEqual(text, info["text"])
        self.assertEqual(text, self.remote_file("specs/1.md"))


class Layout(GitStoreFixture):
    def test_the_first_write_bootstraps_an_orphan_branch(self):
        backend = GitBackend(self.clone("a"))
        self.assertEqual([], backend.list_specs())
        locator = backend.create_spec("plans", canonical._case_doc())
        self.assertEqual("quenching:specs/1.md", locator)
        self.assertEqual(["[skip ci] specs: create 1"], self.remote_log())
        self.assertEqual("", _sh(self.remote, "log", "--format=%P", "quenching").strip())
        self.assertEqual("2\n", self.remote_file(COUNTER_PATH))

    def test_the_counter_allocates_under_cas_and_honours_an_explicit_id(self):
        backend = GitBackend(self.clone("a"))
        for _ in range(3):
            backend.create_spec("plans", canonical._case_doc())
        self.assertEqual("quenching:specs/101.md",
                         backend.create_spec("plans", canonical._case_doc(), spec_id=101))
        self.assertEqual("quenching:specs/102.md",
                         backend.create_spec("plans", canonical._case_doc()))
        with self.assertRaises(BackendRefusal) as caught:
            backend.create_spec("plans", canonical._case_doc(), spec_id=2)
        self.assertEqual("sp-git-id-taken", caught.exception.err["code"])
        self.assertEqual([1, 2, 3, 101, 102], [r["id"] for r in backend.list_specs()])

    def test_archive_is_a_directory_and_leaves_the_document_untouched(self):
        backend = GitBackend(self.clone("a"))
        backend.create_spec("plans", canonical._case_doc())
        info, _ = backend.read_spec(1)
        self.assertEqual("quenching:specs/archive/1.md", backend.move_spec(info, "archive"))
        self.assertEqual(canonical._case_doc(), self.remote_file("specs/archive/1.md"))
        self.assertEqual([("archive", "closed")],
                         [(r["phase"], r["state"]) for r in backend.list_specs(lean=True)])
        self.assertEqual("[skip ci] specs: archive 1", self.remote_log()[0])

    def test_a_batch_writes_n_specs_in_one_commit(self):
        backend = GitBackend(self.clone("a"))
        for _ in range(3):
            backend.create_spec("plans", canonical._case_doc())
        infos = [backend.read_spec(n)[0] for n in (1, 2, 3)]
        backend.write_specs([(info, info["text"] + f"\n<!-- {info['id']} -->\n")
                             for info in infos])
        self.assertEqual("[skip ci] specs: write 1 2 3", self.remote_log()[0])
        self.assertEqual(4, len(self.remote_log()))
        self.assertTrue(self.remote_file("specs/3.md").endswith("<!-- 3 -->\n"))

    def test_an_unchanged_write_makes_no_commit(self):
        backend = GitBackend(self.clone("a"))
        backend.create_spec("plans", canonical._case_doc())
        info, _ = backend.read_spec(1)
        backend.write_spec(info, info["text"])
        self.assertEqual(1, len(self.remote_log()))


class CompareAndSwap(GitStoreFixture):
    def _two_writers(self):
        seed = GitBackend(self.clone("seed"))
        seed.create_spec("plans", canonical._case_doc("One"))
        seed.create_spec("plans", canonical._case_doc("Two"))
        return GitBackend(self.clone("a")), GitBackend(self.clone("b"))

    def test_two_clones_writing_different_specs_both_land(self):
        a, b = self._two_writers()
        info_a, _ = a.read_spec(1)
        info_b, _ = b.read_spec(2)
        a.write_spec(info_a, info_a["text"] + "\nfrom a\n")
        b.write_spec(info_b, info_b["text"] + "\nfrom b\n")   # stale tip: rejected, re-applied
        self.assertTrue(self.remote_file("specs/1.md").endswith("from a\n"))
        self.assertTrue(self.remote_file("specs/2.md").endswith("from b\n"))
        self.assertEqual(["[skip ci] specs: write 2", "[skip ci] specs: write 1"],
                         self.remote_log()[:2])

    def test_the_same_spec_written_concurrently_refuses_the_second_writer(self):
        a, b = self._two_writers()
        info_a, _ = a.read_spec(1)
        info_b, _ = b.read_spec(1)
        a.write_spec(info_a, info_a["text"] + "\nfrom a\n")
        with self.assertRaises(BackendRefusal) as caught:
            b.write_spec(info_b, info_b["text"] + "\nfrom b\n")
        self.assertEqual("sp-git-stale-write", caught.exception.err["code"])
        self.assertTrue(self.remote_file("specs/1.md").endswith("from a\n"))

    def test_a_writer_that_rereads_after_its_own_write_is_not_stale(self):
        a, _ = self._two_writers()
        info, _ = a.read_spec(1)
        a.write_spec(info, info["text"] + "\nfirst\n")
        a.write_spec(info, info["text"] + "\nfirst\nsecond\n")
        self.assertTrue(self.remote_file("specs/1.md").endswith("second\n"))

    def test_concurrent_creates_from_two_clones_never_share_an_id(self):
        a, b = GitBackend(self.clone("a")), GitBackend(self.clone("b"))
        self.assertEqual("quenching:specs/1.md", a.create_spec("plans", canonical._case_doc()))
        self.assertEqual("quenching:specs/2.md", b.create_spec("plans", canonical._case_doc()))
        self.assertEqual("3\n", self.remote_file(COUNTER_PATH))


class Reading(GitStoreFixture):
    def test_a_fresh_fetch_cache_skips_the_fetch_and_an_expired_one_does_not(self):
        a_path = self.clone("a")
        GitBackend(a_path).list_specs()
        GitBackend(self.clone("b")).create_spec("plans", canonical._case_doc())
        self.assertEqual([], GitBackend(a_path).list_specs())
        with mock.patch.object(git_mod, "FETCH_TTL_S", 0):
            self.assertEqual([1], [r["id"] for r in GitBackend(a_path).list_specs()])

    def test_a_read_only_mirror_never_touches_the_target_and_refuses_writes(self):
        target = self.clone("target")    # before the branch exists: no tracking ref yet
        GitBackend(self.clone("writer")).create_spec("plans", canonical._case_doc())
        mirror = GitBackend(target, mirror_dir=os.path.join(self.tmp, "data", "mirror.git"))
        self.assertEqual([1], [r["id"] for r in mirror.list_specs()])
        self.assertEqual("", _sh(target, "for-each-ref", "refs/remotes/origin/quenching"))
        info, _ = mirror.read_spec(1)
        for call in (lambda: mirror.write_spec(info, "x"),
                     lambda: mirror.create_spec("plans", "x"),
                     lambda: mirror.move_spec(info, "archive")):
            with self.assertRaises(BackendRefusal) as caught:
                call()
            self.assertEqual("sp-git-read-only", caught.exception.err["code"])

    def test_an_unknown_id_is_the_shared_refusal(self):
        backend = GitBackend(self.clone("a"))
        info, err = backend.read_spec(7)
        self.assertIsNone(info)
        self.assertEqual("sp-unknown-id", err["code"])


class Configuration(GitStoreFixture):
    def _declare(self, path: str, specs: dict | None = None) -> None:
        os.makedirs(os.path.join(path, ".claude"), exist_ok=True)
        document = {"backend": "git", **({"specs": specs} if specs else {})}
        with open(os.path.join(path, ".claude", "quenching.json"), "w", encoding="utf-8") as fh:
            json.dump(document, fh)

    def test_the_factory_opens_the_git_store_when_declared(self):
        path = self.clone("a")
        self._declare(path)
        backend, err = backends_mod.open_backend(path)
        self.assertEqual({}, err)
        self.assertIsInstance(backend, GitBackend)
        self.assertEqual("git", config_mod.load_config(path)["backend"])
        self.assertIsNone(config_mod.load_config(path)["unknownBackend"])

    def test_the_branch_config_wins_over_the_local_one_for_specs_axis_keys(self):
        path = self.clone("a")
        self._declare(path, {"tagCatalog": {"local": "from .claude"},
                             "subjects": {"s": {"name": "S", "description": "local"}}})
        GitBackend(self.clone("b")).write_config(
            {"tagCatalog": {"branch": "from the branch"}, "artifactLanguage": "pt-BR"})
        cfg = config_mod.load_config(path)
        self.assertEqual({"branch": "from the branch"}, cfg["tagCatalog"])
        self.assertEqual("local", cfg["subjects"]["s"]["description"])
        self.assertEqual("pt-BR", cfg["artifactLanguage"])


if __name__ == "__main__":
    unittest.main()
