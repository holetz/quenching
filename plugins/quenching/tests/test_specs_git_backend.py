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

    def remote_tip(self) -> str:
        run = subprocess.run(["git", "rev-parse", "--verify", "--quiet", "quenching"],
                             cwd=self.remote, capture_output=True, text=True)
        return run.stdout.strip()

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
        self.assertEqual(["[skip ci] specs: archive 1"], self.remote_log())

    def test_a_batch_writes_n_specs_in_one_pending_commit_sent_by_one_push(self):
        backend = GitBackend(self.clone("a"))
        for _ in range(3):
            backend.create_spec("plans", canonical._case_doc())
        infos = [backend.read_spec(n)[0] for n in (1, 2, 3)]
        backend.write_specs([(info, info["text"] + f"\n<!-- {info['id']} -->\n")
                             for info in infos])
        self.assertEqual(["[skip ci] specs: create 3"], self.remote_log())
        self.assertEqual("collapsed", backend.push()["history"])
        self.assertEqual(["[skip ci] specs: write 1 2 3"], self.remote_log())
        self.assertTrue(self.remote_file("specs/3.md").endswith("<!-- 3 -->\n"))

    def test_an_unchanged_write_leaves_no_pending_commit(self):
        backend = GitBackend(self.clone("a"))
        backend.create_spec("plans", canonical._case_doc())
        info, _ = backend.read_spec(1)
        backend.write_spec(info, info["text"])
        self.assertIsNone(backend._pending())
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
        b.write_spec(info_b, info_b["text"] + "\nfrom b\n")
        a.push()
        self.assertEqual(2, b.push()["attempts"])   # stale lease: fetched, replayed, retried
        self.assertTrue(self.remote_file("specs/1.md").endswith("from a\n"))
        self.assertTrue(self.remote_file("specs/2.md").endswith("from b\n"))
        self.assertEqual(["[skip ci] specs: write 2"], self.remote_log())

    def test_the_same_spec_written_concurrently_refuses_at_the_sync(self):
        a, b = self._two_writers()
        info_a, _ = a.read_spec(1)
        info_b, _ = b.read_spec(1)
        a.write_spec(info_a, info_a["text"] + "\nfrom a\n")
        b.write_spec(info_b, info_b["text"] + "\nfrom b\n")   # local: nothing to collide with
        a.push()
        pending = b._pending()
        with mock.patch.object(git_mod, "FETCH_TTL_S", 0):
            with self.assertRaises(BackendRefusal) as caught:
                b.push()
        err = caught.exception.err
        self.assertEqual("sp-git-stale-write", err["code"])
        self.assertEqual([1], err["ids"])
        local_blob, remote_blob = err["conflicts"][0]["localBlob"], err["conflicts"][0]["remoteBlob"]
        self.assertIn(local_blob[:12], err["message"])
        self.assertIn(remote_blob[:12], err["message"])
        self.assertEqual(pending, b._pending())    # the local side is kept for recovery
        self.assertTrue(_sh(self.tmp, "--git-dir", os.path.join(b.repo_root, ".git"), "cat-file",
                            "-p", local_blob).endswith("from b\n"))
        self.assertTrue(b.read_spec(1)[0]["text"].endswith("from b\n"))   # reads keep local
        b.push(drop=(1,))
        self.assertIsNone(b._pending())
        self.assertTrue(self.remote_file("specs/1.md").endswith("from a\n"))

    def test_a_writer_that_rereads_after_its_own_write_is_not_stale(self):
        a, _ = self._two_writers()
        info, _ = a.read_spec(1)
        a.write_spec(info, info["text"] + "\nfirst\n")
        a.write_spec(info, info["text"] + "\nfirst\nsecond\n")
        a.push()
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

    def test_no_fetch_reads_the_local_ref_even_when_the_cache_expired(self):
        a_path = self.clone("a")
        GitBackend(a_path).list_specs()
        GitBackend(self.clone("b")).create_spec("plans", canonical._case_doc())
        with mock.patch.object(git_mod, "FETCH_TTL_S", 0), \
                mock.patch.dict(os.environ, {git_mod.NO_FETCH_ENV: "1"}):
            self.assertEqual([], GitBackend(a_path).list_specs())
        with mock.patch.object(git_mod, "FETCH_TTL_S", 0):
            self.assertEqual([1], [r["id"] for r in GitBackend(a_path).list_specs()])

    def test_an_external_commit_after_the_ttl_is_seen_by_the_same_instance(self):
        a_path = self.clone("a")
        b = GitBackend(self.clone("b"))
        b.create_spec("plans", canonical._case_doc())
        backend = GitBackend(a_path)
        now = [1000.0]    # injected clock: no real sleep, no dependence on how fast the test runs
        with mock.patch.object(git_mod.time, "monotonic", lambda: now[0]):
            self.assertEqual([1], [r["id"] for r in backend.list_specs()])   # memoizes a non-null tip
            b.create_spec("plans", canonical._case_doc())
            _sh(a_path, "fetch", "--quiet", "origin", "+quenching:refs/remotes/origin/quenching")
            with mock.patch.dict(os.environ, {git_mod.NO_FETCH_ENV: "1"}):
                now[0] += 0.5
                self.assertEqual([1], [r["id"] for r in backend.list_specs()])   # inside the memo window
                now[0] += 2.0   # past the window, still far inside FETCH_TTL_S
                self.assertEqual([1, 2], sorted(r["id"] for r in backend.list_specs()))

    def test_the_portal_etag_moves_after_an_external_commit_to_the_store_ref(self):
        from quenching.specs import portal as portal_mod
        a_path = self.clone("a")
        writer = self.clone("w")
        GitBackend(writer).create_spec("plans", canonical._case_doc())
        _sh(a_path, "fetch", "--quiet", "origin", "+quenching:refs/remotes/origin/quenching")
        headers = {"Host": "127.0.0.1:4321", "X-Quenching-Token": "t"}
        with mock.patch.dict(os.environ, {git_mod.NO_FETCH_ENV: "1"}), \
                mock.patch.object(git_mod, "TIP_MEMO_S", 0), \
                mock.patch.object(portal_mod, "TTL_SECONDS", 0):
            backends_mod._BACKEND_CACHE[a_path] = GitBackend(a_path)
            portal = portal_mod.Portal(a_path, "t", True, "127.0.0.1", 4321)
            status, hdrs, body = portal.handle("GET", "/api/specs", headers)
            self.assertEqual(200, status, body)
            etag = hdrs["ETag"]
            self.assertEqual(304, portal.handle("GET", "/api/specs",
                                                {**headers, "If-None-Match": etag})[0])
            outside = GitBackend(writer)
            info, _ = outside.read_spec(1)
            outside.write_spec(info, info["text"].replace(
                "title: Alpha", "title: Renamed outside the portal", 1))
            outside.push()
            _sh(a_path, "fetch", "--quiet", "origin", "+quenching:refs/remotes/origin/quenching")
            status, hdrs, _ = portal.handle("GET", "/api/specs",
                                            {**headers, "If-None-Match": etag})
            self.assertEqual(200, status)
            self.assertNotEqual(etag, hdrs["ETag"])

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


class PendingWrites(GitStoreFixture):
    """Writes accumulate in one local pending commit; only a sync reaches the remote, and the
    branch it leaves always holds one parentless commit."""

    def _seeded(self, count: int = 2) -> tuple[str, GitBackend]:
        path = self.clone("a")
        backend = GitBackend(path)
        for n in range(count):
            backend.create_spec("plans", canonical._case_doc(f"Spec {n + 1}"))
        return path, backend

    def _append(self, backend: GitBackend, spec_id: int, line: str) -> None:
        info, _ = backend.read_spec(spec_id)
        backend.write_spec(info, info["text"] + f"\n{line}\n")

    def test_a_deferred_write_leaves_the_remote_untouched(self):
        _, backend = self._seeded()
        before = self.remote_tip()
        self._append(backend, 1, "local")
        self._append(backend, 2, "local too")
        self.assertEqual(before, self.remote_tip())
        pending = backend._pending()
        self.assertEqual(before, backend._parent(pending))   # one commit on the remote tip
        self.assertEqual("[skip ci] specs: write 1; write 2",
                         _sh(backend.repo_root, "log", "-1", "--format=%s", pending).strip())

    def test_the_pending_state_dates_the_first_unsent_write(self):
        _, backend = self._seeded()
        with mock.patch.dict(os.environ, {"GIT_AUTHOR_DATE": "2026-01-02T03:04:05+00:00",
                                          "GIT_COMMITTER_DATE": "2026-01-02T03:04:05+00:00"}):
            self._append(backend, 1, "first")
        self._append(backend, 2, "later")
        self.assertEqual({"specs": [1, 2], "since": "2026-01-02T03:04:05+00:00"},
                         {k: v for k, v in backend.pending_state().items() if k != "commit"})

    def test_reads_see_their_own_writes_across_instances_and_without_a_fetch(self):
        path, backend = self._seeded()
        self._append(backend, 1, "local")
        self.assertTrue(GitBackend(path).read_spec(1)[0]["text"].endswith("local\n"))
        with mock.patch.dict(os.environ, {git_mod.NO_FETCH_ENV: "1"}):
            self.assertTrue(GitBackend(path).read_spec(1)[0]["text"].endswith("local\n"))
            self.assertTrue(GitBackend(path).has_local_ref())

    def test_a_read_after_a_remote_move_replays_in_memory_and_never_moves_the_pending_ref(self):
        path, backend = self._seeded()
        self._append(backend, 1, "local")
        pending = backend._pending()
        other = GitBackend(self.clone("b"))
        self._append(other, 2, "remote")
        other.push()
        with mock.patch.object(git_mod, "FETCH_TTL_S", 0):
            fresh = GitBackend(path)
            self.assertTrue(fresh.read_spec(1)[0]["text"].endswith("local\n"))
            self.assertTrue(fresh.read_spec(2)[0]["text"].endswith("remote\n"))
        self.assertEqual(pending, backend._pending())

    def test_a_write_after_a_fetch_persists_the_replay_on_the_new_tip(self):
        path, backend = self._seeded()
        self._append(backend, 1, "local")
        other = GitBackend(self.clone("b"))
        self._append(other, 2, "remote")
        other.push()
        with mock.patch.object(git_mod, "FETCH_TTL_S", 0):
            fresh = GitBackend(path)
            self._append(fresh, 1, "again")
        self.assertEqual(self.remote_tip(), fresh._parent(fresh._pending()))
        self.assertEqual({"specs": [1], "commit": fresh._pending()},
                         {k: v for k, v in fresh.pending_state().items() if k != "since"})

    def test_a_sync_is_one_parentless_commit_with_every_pending_change(self):
        _, backend = self._seeded()
        self._append(backend, 1, "one")
        self._append(backend, 2, "two")
        backend.create_spec("plans", canonical._case_doc("Three"))
        self.assertEqual(["[skip ci] specs: write 1; write 2; create 3"], self.remote_log())
        self.assertEqual("", _sh(self.remote, "log", "--format=%P", "quenching").strip())
        self.assertTrue(self.remote_file("specs/1.md").endswith("one\n"))
        self.assertTrue(self.remote_file("specs/2.md").endswith("two\n"))
        self.assertIsNone(backend._pending())
        self.assertIsNone(backend.pending_state())

    def test_archive_syncs_and_carries_the_pending_writes(self):
        _, backend = self._seeded()
        self._append(backend, 2, "pending")
        info, _ = backend.read_spec(1)
        backend.move_spec(info, "archive")
        self.assertEqual(["[skip ci] specs: write 2; archive 1"], self.remote_log())
        self.assertTrue(self.remote_file("specs/2.md").endswith("pending\n"))

    def test_a_write_landing_between_the_push_and_the_close_survives(self):
        path, backend = self._seeded()
        self._append(backend, 1, "sent")
        late = GitBackend(path)
        real_push = GitBackend._push

        def push_then_write(this, lease, commit):
            result = real_push(this, lease, commit)
            self._append(late, 2, "late-write")
            return result
        with mock.patch.object(GitBackend, "_push", push_then_write):
            backend.push()
        self.assertTrue(self.remote_file("specs/1.md").endswith("sent\n"))
        self.assertNotIn("late-write", self.remote_file("specs/2.md"))
        pending = backend._pending()
        self.assertEqual(self.remote_tip(), backend._parent(pending))
        self.assertTrue(GitBackend(path).read_spec(2)[0]["text"].endswith("late-write\n"))
        backend.push()
        self.assertTrue(self.remote_file("specs/2.md").endswith("late-write\n"))
        self.assertEqual(1, len(self.remote_log()))

    def _drifted(self) -> tuple[str, GitBackend, GitBackend, str]:
        """Clone `a` holds a pending write on spec 1 based on T0; another clone then moves the
        remote twice (T1, T2). Returns the path, the syncing instance, the other clone and T1,
        the tip a late writer in clone `a` read before the sync fetched T2."""
        path, backend = self._seeded(3)
        self._append(backend, 1, "sent")
        other = GitBackend(self.clone("b"))
        self._append(other, 3, "x1")
        other.push()
        _sh(path, "fetch", "--quiet", "origin", "+quenching:refs/remotes/origin/quenching")
        return path, backend, other, self.remote_tip()

    def _sync_with_late_write(self, backend: GitBackend, path: str, late_tip: str,
                              spec_id: int, line: str) -> None:
        """`backend.push()`, with a second instance of the same clone writing `spec_id` between
        the push and the close, on the tracking tip it read before the sync's fetch."""
        late = GitBackend(path)
        real_push = GitBackend._push

        def push_then_write(this, lease, commit):
            result = real_push(this, lease, commit)
            if result[0] == 0 and this is backend:
                with mock.patch.object(late, "_local_tip", return_value=late_tip):
                    self._append(late, spec_id, line)
            return result
        with mock.patch.object(git_mod, "FETCH_TTL_S", 0), \
                mock.patch.object(GitBackend, "_push", push_then_write):
            backend.push()

    def test_a_late_write_on_an_older_tip_never_reverts_the_remote(self):
        path, backend, other, t1 = self._drifted()
        self._append(other, 3, "x2")
        other.push()
        self._sync_with_late_write(backend, path, t1, 2, "late-2")
        self.assertTrue(self.remote_file("specs/3.md").endswith("x2\n"))
        self.assertEqual([2], backend.pending_state()["specs"])   # only the late write's intent
        with mock.patch.object(git_mod, "FETCH_TTL_S", 0):
            GitBackend(path).push()
        self.assertTrue(self.remote_file("specs/3.md").endswith("x2\n"))
        self.assertTrue(self.remote_file("specs/2.md").endswith("late-2\n"))
        self.assertTrue(self.remote_file("specs/1.md").endswith("sent\n"))

    def test_a_late_write_on_an_older_tip_never_resurrects_an_archived_spec(self):
        path, backend, other, t1 = self._drifted()
        info, _ = other.read_spec(3)
        other.move_spec(info, "archive")
        self._sync_with_late_write(backend, path, t1, 2, "late-2")
        with mock.patch.object(git_mod, "FETCH_TTL_S", 0):
            GitBackend(path).push()
        names = _sh(self.remote, "ls-tree", "-r", "--name-only", "quenching").split()
        self.assertIn("specs/archive/3.md", names)
        self.assertNotIn("specs/3.md", names)
        self.assertTrue(self.remote_file("specs/2.md").endswith("late-2\n"))

    def test_a_late_write_to_a_spec_the_sync_moved_refuses_at_the_next_sync(self):
        path, backend, other, t1 = self._drifted()
        self._append(other, 3, "x2")
        other.push()
        self._sync_with_late_write(backend, path, t1, 3, "late-3")
        with mock.patch.object(git_mod, "FETCH_TTL_S", 0):
            with self.assertRaises(BackendRefusal) as caught:
                GitBackend(path).push()
        self.assertEqual([3], caught.exception.err["ids"])
        self.assertTrue(self.remote_file("specs/3.md").endswith("x2\n"))

    def test_the_close_never_moves_the_tracking_ref_backward(self):
        path, backend = self._seeded()
        self._append(backend, 1, "sent")
        other = GitBackend(self.clone("b"))
        real_push = GitBackend._push

        def push_then_newer_tip(this, lease, commit):
            result = real_push(this, lease, commit)
            if result[0] == 0 and this is backend:
                with mock.patch.object(git_mod, "FETCH_TTL_S", 0):
                    self._append(other, 2, "newer")
                    other.push()
                _sh(path, "fetch", "--quiet", "origin",
                    "+quenching:refs/remotes/origin/quenching")
            return result
        with mock.patch.object(GitBackend, "_push", push_then_newer_tip):
            backend.push()
        self.assertEqual(self.remote_tip(), backend._local_tip())

    def test_a_conflict_on_a_stale_cached_tip_is_judged_again_on_a_fresh_fetch(self):
        path, backend = self._seeded()
        t0 = self.remote_tip()
        other = GitBackend(self.clone("b"))
        self._append(other, 1, "remote")
        other.push()
        with mock.patch.object(git_mod, "FETCH_TTL_S", 0):
            self._append(GitBackend(path), 1, "local on the new tip")
        _sh(path, "update-ref", "refs/remotes/origin/quenching", t0)   # a stale tracking ref
        result = GitBackend(path).push()                               # the cache is fresh
        self.assertEqual("collapsed", result["history"])
        self.assertTrue(self.remote_file("specs/1.md").endswith("local on the new tip\n"))

    def test_a_write_blocked_by_another_conflict_names_the_written_spec(self):
        path, backend = self._seeded()
        self._append(backend, 1, "local")
        other = GitBackend(self.clone("b"))
        self._append(other, 1, "remote")
        self._append(other, 2, "remote")
        other.push()
        with mock.patch.object(git_mod, "FETCH_TTL_S", 0):
            fresh = GitBackend(path)
            info, _ = fresh.read_spec(2)
        with self.assertRaises(BackendRefusal) as caught:
            fresh.write_spec(info, info["text"] + "\nmine\n")
        err = caught.exception.err
        self.assertEqual(([2], [1]), (err["ids"], err["blockedBy"]))
        self.assertIn("spec(s) 2 changed", err["message"])

    def test_a_local_write_never_fetches(self):
        _, backend = self._seeded()
        info, _ = backend.read_spec(1)
        calls = []
        real = GitBackend._git

        def spy(this, *argv, **kwargs):
            calls.append(argv[0])
            return real(this, *argv, **kwargs)
        with mock.patch.object(git_mod, "FETCH_TTL_S", 0), \
                mock.patch.object(GitBackend, "_git", spy):
            backend.write_spec(info, info["text"] + "\noffline\n")
        self.assertNotIn("fetch", calls)
        self.assertEqual([1], backend.pending_state()["specs"])

    def test_writing_a_spec_back_to_its_remote_text_retires_the_pending_ref(self):
        _, backend = self._seeded()
        info, _ = backend.read_spec(1)
        original = info["text"]
        backend.write_spec(info, original + "\nedit\n")
        info, _ = backend.read_spec(1)
        backend.write_spec(info, original)
        self.assertIsNone(backend._pending())
        self.assertIsNone(backend.pending_state())

    def _race(self, backend: GitBackend, rival: GitBackend, times: int):
        """Patch `backend._commit` so `rival` (another process of the same clone) moves the
        pending ref between `backend`'s read of it and its compare-and-swap, `times` times."""
        lost = [0]
        real = GitBackend._commit

        def commit_then_rival_writes(*args, **kwargs):
            result = real(backend, *args, **kwargs)
            if lost[0] < times:
                lost[0] += 1
                self._append(rival, 2, f"rival {lost[0]}")
            return result
        return mock.patch.object(backend, "_commit", side_effect=commit_then_rival_writes), lost

    def test_two_processes_racing_the_pending_ref_retry_and_both_land(self):
        path, backend = self._seeded()
        rival = GitBackend(path)
        info, _ = backend.read_spec(1)
        patcher, lost = self._race(backend, rival, 1)
        with patcher:
            backend.write_spec(info, info["text"] + "\nmine\n")
        self.assertEqual(1, lost[0])
        self.assertEqual([1, 2], backend.pending_state()["specs"])
        fresh = GitBackend(path)
        self.assertTrue(fresh.read_spec(1)[0]["text"].endswith("mine\n"))
        self.assertTrue(fresh.read_spec(2)[0]["text"].endswith("rival 1\n"))

    def test_a_pending_ref_that_keeps_moving_refuses_and_writes_nothing(self):
        path, backend = self._seeded()
        rival = GitBackend(path)
        info, _ = backend.read_spec(1)
        patcher, lost = self._race(backend, rival, git_mod.MAX_ATTEMPTS)
        with patcher, self.assertRaises(BackendRefusal) as caught:
            backend.write_spec(info, info["text"] + "\nmine\n")
        self.assertEqual("sp-git-cas-exhausted", caught.exception.err["code"])
        self.assertEqual(git_mod.MAX_ATTEMPTS, lost[0])
        self.assertEqual([2], backend.pending_state()["specs"])
        self.assertNotIn("mine", GitBackend(path).read_spec(1)[0]["text"])

    def test_a_refused_collapse_with_nothing_pending_appends_nothing(self):
        _, backend = self._seeded()
        _sh(self.remote, "config", "receive.denyNonFastForwards", "true")
        self._append(backend, 1, "appended")
        self.assertEqual("appended", backend.push()["history"])
        tip = self.remote_tip()
        for _ in range(2):
            result = backend.push()
            self.assertEqual((None, True), (result["commit"], result["collapseRefused"]))
        self.assertEqual(tip, self.remote_tip())
        self.assertEqual(2, len(self.remote_log()))

    def test_a_plain_fast_forward_from_an_old_runtime_is_collapsed_by_the_next_sync(self):
        _, backend = self._seeded()
        old = self.clone("old")
        _sh(old, "fetch", "--quiet", "origin", "quenching")
        tree = _sh(old, "rev-parse", "FETCH_HEAD^{tree}").strip()
        child = _sh(old, "commit-tree", tree, "-p", "FETCH_HEAD", "-m", "old runtime").strip()
        _sh(old, "push", "--quiet", "origin", f"{child}:refs/heads/quenching")
        self.assertEqual(2, len(self.remote_log()))
        with mock.patch.object(git_mod, "FETCH_TTL_S", 0):
            self.assertEqual("collapsed", GitBackend(backend.repo_root).push()["history"])
        self.assertEqual(1, len(self.remote_log()))

    def test_a_remote_that_refuses_the_rewrite_receives_a_fast_forward(self):
        _, backend = self._seeded()
        _sh(self.remote, "config", "receive.denyNonFastForwards", "true")
        self._append(backend, 1, "appended")
        result = backend.push()
        self.assertEqual("appended", result["history"])
        self.assertEqual(2, len(self.remote_log()))
        self.assertTrue(self.remote_file("specs/1.md").endswith("appended\n"))
        self.assertIsNone(backend._pending())
        _sh(self.remote, "config", "receive.denyNonFastForwards", "false")
        self.assertEqual("collapsed", backend.push()["history"])
        self.assertEqual(1, len(self.remote_log()))

    def test_a_mirror_ignores_the_pending_ref(self):
        path, backend = self._seeded(1)
        self._append(backend, 1, "local")
        mirror = GitBackend(path, mirror_dir=os.path.join(self.tmp, "data", "mirror.git"))
        self.assertNotIn("local", mirror.read_spec(1)[0]["text"])


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
