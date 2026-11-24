"""`cq specs claim` — a spec's reservation on the origin, compared and swapped by the server.

Every case runs over a temporary bare remote and its clones; nothing reaches a network."""
from __future__ import annotations

import contextlib
import datetime
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import _paths  # noqa: F401 — must precede the `quenching` import
from quenching.specs import claims
from quenching.specs.commands import claim as claim_cmd
from quenching.specs.commands.cli import build_parser
from quenching.specs.commands.output import Emitter

CQ = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                  "assets", "bin", "cq")


def _sh(cwd: str, *argv: str) -> str:
    run = subprocess.run(["git", *argv], cwd=cwd, capture_output=True, text=True)
    if run.returncode != 0:
        raise AssertionError(f"git {' '.join(argv)} failed: {run.stderr}")
    return run.stdout


class ClaimFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="quenching-claims-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        env = {"GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.test",
               "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.test",
               "XDG_CACHE_HOME": os.path.join(self.tmp, "cache")}
        patcher = mock.patch.dict(os.environ, env)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.remote = os.path.join(self.tmp, "remote.git")
        _sh(self.tmp, "init", "--quiet", "--bare", self.remote)
        terminal = mock.patch.object(claim_cmd, "_terminal",
                                     side_effect=lambda root, ids: {i: i in self.terminal
                                                                    for i in ids})
        terminal.start()
        self.addCleanup(terminal.stop)
        self.terminal: set[str] = set()

    def clone(self, name: str) -> str:
        path = os.path.join(self.tmp, name)
        _sh(self.tmp, "clone", "--quiet", self.remote, path)
        return path

    def claim(self, root: str, *argv: str, at: datetime.datetime | None = None):
        parser, _ = build_parser()
        args = parser.parse_args(["claim", *argv, "--json"])
        buf = io.StringIO()
        clock = mock.patch.object(claims, "now", return_value=at) if at else contextlib.nullcontext()
        with clock, contextlib.redirect_stdout(buf):
            code = claim_cmd.cmd_claim(args, root, Emitter())
        return code, json.loads(buf.getvalue())

    def remote_lease(self, spec_id: str) -> dict:
        blob = _sh(self.remote, "cat-file", "blob", f"refs/quenching/claims/{spec_id}:lease.json")
        return json.loads(blob)


class AcquireRenewRelease(ClaimFixture):
    def setUp(self):
        super().setUp()
        self.a, self.b = self.clone("a"), self.clone("b")

    def test_acquire_writes_the_lease_on_the_remote_without_personal_identity(self):
        code, got = self.claim(self.a, "acquire", "7", "--session", "s1", "--label", "laptop")
        self.assertEqual((0, "remote"), (code, got["scope"]))
        lease = self.remote_lease("7")
        machine = _sh(self.a, "config", "--local", "--get", "quenching.machineId").strip()
        self.assertEqual(f"{machine}:s1", lease["holder"])
        self.assertEqual(("execute", "laptop", "7"), (lease["stage"], lease["label"], lease["spec"]))
        expires = claims._parse(lease["expires"]) - claims._parse(lease["acquired"])
        self.assertEqual(datetime.timedelta(minutes=45), expires)
        author = _sh(self.remote, "log", "-1", "--format=%an <%ae> %cn <%ce>",
                     "refs/quenching/claims/7")
        self.assertNotIn("fixture", author)
        self.assertNotIn(os.uname().nodename, json.dumps(lease) + author)

    def test_a_live_lease_of_another_machine_is_exit_1_with_the_holder(self):
        self.claim(self.a, "acquire", "7", "--session", "s1")
        code, got = self.claim(self.b, "acquire", "7", "--session", "s2")
        self.assertEqual((1, "held"), (code, got["reason"]))
        self.assertTrue(got["heldBy"]["holder"].endswith(":s1"))
        self.assertTrue(got["heldBy"]["live"])

    def test_the_same_machine_in_another_session_reacquires_its_own_lease(self):
        _, first = self.claim(self.a, "acquire", "7", "--session", "s1")
        code, got = self.claim(self.a, "acquire", "7", "--session", "s2")
        self.assertEqual(0, code)
        self.assertEqual(first["lease"]["acquired"], got["lease"]["acquired"])
        self.assertTrue(self.remote_lease("7")["holder"].endswith(":s2"))

    def test_renew_by_another_machine_is_exit_1_and_by_the_holder_moves_the_expiry(self):
        at = claims.now()
        self.claim(self.a, "acquire", "7", "--session", "s1", at=at)
        code, got = self.claim(self.b, "renew", "7", "--session", "s2")
        self.assertEqual((1, "not-holder"), (code, got["reason"]))
        later = at + datetime.timedelta(minutes=30)
        code, got = self.claim(self.a, "renew", "7", "--session", "s1", at=later)
        self.assertEqual(0, code)
        self.assertEqual(claims._stamp(later + datetime.timedelta(minutes=45)),
                         self.remote_lease("7")["expires"])
        code, got = self.claim(self.a, "renew", "8", "--session", "s1")
        self.assertEqual((1, "absent"), (code, got["reason"]))

    def test_release_only_by_the_holder_and_absent_is_ok(self):
        self.claim(self.a, "acquire", "7", "--session", "s1")
        code, got = self.claim(self.b, "release", "7")
        self.assertEqual((1, "not-holder"), (code, got["reason"]))
        code, got = self.claim(self.a, "release", "7")
        self.assertEqual((0, True), (code, got["released"]))
        self.assertEqual("", _sh(self.remote, "for-each-ref", "refs/quenching/claims/"))
        code, got = self.claim(self.a, "release", "7")
        self.assertEqual((0, False), (code, got["released"]))

    def test_release_with_a_stale_sha_loses_the_compare_and_swap(self):
        self.claim(self.a, "acquire", "7", "--session", "s1")
        store = claims.Store(self.a)
        sha, _ = store.read("7")
        self.claim(self.a, "renew", "7", "--session", "s1",
                   at=claims.now() + datetime.timedelta(minutes=1))
        self.assertFalse(store.swap("7", None, sha))
        self.assertIn("refs/quenching/claims/7", _sh(self.remote, "for-each-ref"))

    def test_an_expired_lease_is_taken_by_another_machine(self):
        self.claim(self.a, "acquire", "7", "--session", "s1")
        late = claims.now() + datetime.timedelta(minutes=45 + 3)
        code, got = self.claim(self.b, "acquire", "7", "--session", "s2", at=late)
        self.assertEqual(0, code)
        self.assertTrue(got["replaced"]["expired"])
        self.assertTrue(self.remote_lease("7")["holder"].endswith(":s2"))

    def test_the_clock_skew_keeps_a_just_expired_lease_live(self):
        self.claim(self.a, "acquire", "7", "--session", "s1")
        soon = claims.now() + datetime.timedelta(minutes=45 + 1)
        code, _ = self.claim(self.b, "acquire", "7", "--session", "s2", at=soon)
        self.assertEqual(1, code)

    def test_a_terminal_spec_has_its_lease_ignored(self):
        self.claim(self.a, "acquire", "7", "--session", "s1")
        self.terminal.add("7")
        code, got = self.claim(self.b, "acquire", "7", "--session", "s2")
        self.assertEqual(0, code)
        self.assertTrue(got["replaced"]["terminal"])
        _, listed = self.claim(self.b, "list")
        self.assertFalse(listed["claims"][0]["live"])

    def test_take_replaces_a_live_lease_and_names_who_was_taken(self):
        self.claim(self.a, "acquire", "7", "--session", "s1")
        code, got = self.claim(self.b, "take", "7", "--session", "s2")
        self.assertEqual(0, code)
        self.assertTrue(got["taken"]["holder"].endswith(":s1"))
        self.assertTrue(got["taken"]["live"])

    def test_list_reads_every_lease_with_mine_and_live(self):
        self.claim(self.a, "acquire", "7", "--session", "s1")
        self.claim(self.b, "acquire", "9", "--session", "s2")
        code, got = self.claim(self.a, "list")
        self.assertEqual(0, code)
        rows = {r["spec"]: r for r in got["claims"]}
        self.assertEqual({"7", "9"}, set(rows))
        self.assertEqual((True, False), (rows["7"]["mine"], rows["9"]["mine"]))
        self.assertTrue(all(r["live"] for r in rows.values()))

    def test_list_on_a_clone_without_an_id_writes_no_git_config(self):
        self.claim(self.b, "acquire", "9", "--session", "s2")
        fresh = self.clone("fresh")
        before = _sh(fresh, "config", "--local", "--list")
        code, got = self.claim(fresh, "list")
        self.assertEqual(0, code)
        self.assertEqual(before, _sh(fresh, "config", "--local", "--list"))
        self.assertNotIn("machineid", before.lower())
        self.assertIsNone(got["holder"])
        self.assertEqual([False], [r["mine"] for r in got["claims"]])

    def test_a_bad_id_is_a_refusal(self):
        code, got = self.claim(self.a, "acquire", "../x")
        self.assertEqual((2, "sp-claim-id"), (code, got["code"]))


class ExpiredRace(ClaimFixture):
    def test_two_takers_of_the_same_expired_lease_one_wins(self):
        a, b, c = self.clone("a"), self.clone("b"), self.clone("c")
        self.claim(a, "acquire", "7", "--session", "s1")
        late = claims.now() + datetime.timedelta(hours=1)
        store_b, store_c = claims.Store(b), claims.Store(c)
        sha, _ = store_b.read("7")
        lease_b = claims.new_lease("7", "mb:s", None, 45, late)
        lease_c = claims.new_lease("7", "mc:s", None, 45, late)
        results = [store_b.swap("7", store_b.make(lease_b), sha),
                   store_c.swap("7", store_c.make(lease_c), sha)]
        self.assertEqual([True, False], results)
        self.assertEqual("mb:s", self.remote_lease("7")["holder"])


class ParallelAcquire(ClaimFixture):
    def test_two_clones_racing_in_processes_exactly_one_wins(self):
        a, b = self.clone("a"), self.clone("b")
        for path in (a, b):        # each clone gets its machine id before the race
            claims.machine_id(path)
        procs = [subprocess.Popen([sys.executable, CQ, "specs", "claim", "acquire", "5",
                                   "--session", name, "--json"], cwd=path,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                 for name, path in (("sa", a), ("sb", b))]
        outs = [(p.wait(timeout=60), json.loads(p.stdout.read())) for p in procs]
        for p in procs:
            p.stdout.close()
            p.stderr.close()
        codes = sorted(code for code, _ in outs)
        self.assertEqual([0, 1], codes)
        winner = next(got for code, got in outs if code == 0)
        loser = next(got for code, got in outs if code == 1)
        self.assertEqual(winner["lease"]["holder"], loser["heldBy"]["holder"])
        self.assertEqual(winner["lease"]["holder"], self.remote_lease("5")["holder"])


class NoRemote(ClaimFixture):
    def test_without_a_remote_the_ref_is_local_and_still_compared(self):
        repo = os.path.join(self.tmp, "solo")
        _sh(self.tmp, "init", "--quiet", repo)
        code, got = self.claim(repo, "acquire", "3", "--session", "s1")
        self.assertEqual((0, "local"), (code, got["scope"]))
        self.assertIn("refs/quenching/claims/3", _sh(repo, "for-each-ref"))
        store = claims.Store(repo)
        sha, _ = store.read("3")
        other = store.make(claims.new_lease("3", "x:y", None, 45, claims.now()))
        self.assertFalse(store.swap("3", other, None))
        self.assertTrue(store.swap("3", other, sha))
        code, got = self.claim(repo, "list")
        self.assertEqual(("local", "x:y"), (got["scope"], got["claims"][0]["holder"]))


class Snapshot(ClaimFixture):
    def setUp(self):
        super().setUp()
        self.a, self.b = self.clone("a"), self.clone("b")
        claims._SNAPSHOTS.clear()
        self.addCleanup(claims._SNAPSHOTS.clear)

    def test_reading_carries_the_shape_and_mine_follows_the_machine(self):
        self.claim(self.a, "acquire", "7", "--session", "s1", "--label", "laptop")
        claims._SNAPSHOTS.clear()
        theirs = claims.reading(claims.snapshot(self.b), "7")
        self.assertEqual({"holder", "label", "expires", "mine", "live"}, set(theirs))
        self.assertEqual((False, True, "laptop"), (theirs["mine"], theirs["live"], theirs["label"]))
        claims._SNAPSHOTS.clear()
        mine = claims.reading(claims.snapshot(self.a), "7")
        self.assertTrue(mine["mine"] and mine["live"])
        self.assertIsNone(claims.reading(claims.snapshot(self.a), "8"))

    def test_an_expired_or_terminal_lease_is_not_live_and_the_read_is_cached(self):
        self.claim(self.a, "acquire", "7", "--session", "s1")
        claims._SNAPSHOTS.clear()
        snap = claims.snapshot(self.b)
        self.assertFalse(claims.reading(snap, "7", terminal=True)["live"])
        late = {**snap, "at": snap["at"] + datetime.timedelta(minutes=48)}
        self.assertFalse(claims.reading(late, "7")["live"])
        self.claim(self.a, "release", "7")
        self.assertIs(snap, claims.snapshot(self.b))

    def test_a_released_lease_leaves_the_mirror_on_the_next_read(self):
        self.claim(self.a, "acquire", "7", "--session", "s1")
        claims.snapshot(self.b)
        self.claim(self.a, "release", "7")
        claims._SNAPSHOTS.clear()
        self.assertIsNone(claims.reading(claims.snapshot(self.b), "7"))

    def test_the_read_never_writes_the_machine_id_and_never_raises(self):
        self.assertEqual("", claims.snapshot(self.b)["me"])
        broken = os.path.join(self.tmp, "not-a-repo")
        os.makedirs(broken)
        snap = claims.snapshot(broken)
        self.assertFalse(snap["available"])
        self.assertIsNone(claims.reading(snap, "7"))

    def test_without_a_remote_the_local_refs_are_read(self):
        repo = os.path.join(self.tmp, "solo")
        _sh(self.tmp, "init", "--quiet", repo)
        self.claim(repo, "acquire", "3", "--session", "s1")
        claims._SNAPSHOTS.clear()
        snap = claims.snapshot(repo)
        self.assertEqual("local", snap["scope"])
        self.assertTrue(claims.reading(snap, "3")["mine"])


if __name__ == "__main__":
    unittest.main()
