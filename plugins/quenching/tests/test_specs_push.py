"""`cq specs push`, the pending line of `cq specs status` and the code-side sync points, over
a temporary bare remote: nothing here reaches a network or the repository under test."""

import argparse
import contextlib
import io
import json
import os
import unittest
from types import SimpleNamespace
from unittest import mock

import _paths  # noqa: F401
import test_specs_backends as canonical
from test_specs_cards import FakeCard
from test_specs_git_backend import GitStoreFixture, _sh
from quenching.git import push as git_push
from quenching.git import pull
from quenching.specs.backends import git as git_mod
from quenching.specs.backends.git import GitBackend
from quenching.specs.commands import push as push_mod
from quenching.specs.commands import read as read_mod
from quenching.specs.commands.output import Emitter


class PushVerb(GitStoreFixture):
    def setUp(self):
        super().setUp()
        self.path = self.clone("a")
        os.makedirs(os.path.join(self.path, ".claude"))
        with open(os.path.join(self.path, ".claude", "quenching.json"), "w") as handle:
            json.dump({"backend": "git"}, handle)
        self.backend = GitBackend(self.path)
        for title in ("One", "Two"):
            self.backend.create_spec("plans", canonical._case_doc(title))
        self.store = mock.patch.object(push_mod, "open_git_backend",
                                       return_value=(self.backend, {}))
        self.store.start()
        self.addCleanup(self.store.stop)

    def write(self, spec_id: int, line: str) -> None:
        info, _ = self.backend.read_spec(spec_id)
        self.backend.write_spec(info, info["text"] + f"\n{line}\n")

    def run_push(self, drop=None):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = push_mod.cmd_push(argparse.Namespace(json=True, drop=drop), self.path,
                                     Emitter())
        return code, json.loads(buf.getvalue())

    def test_push_sends_every_pending_spec_in_one_parentless_commit(self):
        self.write(1, "one")
        self.write(2, "two")
        before = self.remote_tip()
        code, got = self.run_push()
        self.assertEqual(0, code, got)
        self.assertEqual(([1, 2], "collapsed"), (got["sent"], got["history"]))
        self.assertNotEqual(before, self.remote_tip())
        self.assertEqual(["[skip ci] specs: write 1; write 2"], self.remote_log())
        self.assertIsNone(self.backend._pending())

    def test_drop_discards_the_named_spec_and_sends_the_rest(self):
        self.write(1, "kept")
        self.write(2, "dropped")
        code, got = self.run_push(drop=[2])
        self.assertEqual(0, code, got)
        self.assertEqual(([1], [2]), (got["sent"], got["dropped"]))
        self.assertTrue(self.remote_file("specs/1.md").endswith("kept\n"))
        self.assertNotIn("dropped", self.remote_file("specs/2.md"))
        self.assertIsNone(self.backend._pending())

    def test_nothing_pending_on_a_single_commit_branch_pushes_nothing(self):
        before = self.remote_tip()
        code, got = self.run_push()
        self.assertEqual(0, code, got)
        self.assertIsNone(got["commit"])
        self.assertEqual(before, self.remote_tip())

    def test_a_conflict_refuses_and_keeps_the_pending_ref(self):
        self.write(1, "local")
        other = GitBackend(self.clone("b"))
        info, _ = other.read_spec(1)
        other.write_spec(info, info["text"] + "\nremote\n")
        other.push()
        pending = self.backend._pending()
        with mock.patch("quenching.specs.backends.git.FETCH_TTL_S", 0):
            from quenching.specs.backends.base import BackendRefusal
            with self.assertRaises(BackendRefusal) as caught:
                self.run_push()
        self.assertEqual("sp-git-stale-write", caught.exception.err["code"])
        self.assertEqual(pending, self.backend._pending())

    def test_a_repository_without_the_git_store_refuses(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = push_mod.cmd_push(argparse.Namespace(json=True, drop=None),
                                     self.clone("plain"), Emitter())
        self.assertEqual(2, code)
        self.assertEqual("sp-push-no-store", json.loads(buf.getvalue())["code"])

    def test_status_reports_the_pending_specs_and_since_when(self):
        self.write(2, "pending")
        buf = io.StringIO()
        with mock.patch.object(read_mod, "open_backend", return_value=(self.backend, {})), \
                contextlib.redirect_stdout(buf):
            read_mod.cmd_status(argparse.Namespace(json=True, spec="1", epic=None,
                                                   no_fetch=False), self.path, Emitter())
        pending = json.loads(buf.getvalue())["pending"]
        self.assertEqual([2], pending["specs"])
        self.assertRegex(pending["since"], r"^\d{4}-\d{2}-\d{2}T")
        self.run_push()
        buf = io.StringIO()
        with mock.patch.object(read_mod, "open_backend", return_value=(self.backend, {})), \
                contextlib.redirect_stdout(buf):
            read_mod.cmd_status(argparse.Namespace(json=True, spec="1", epic=None,
                                                   no_fetch=False), self.path, Emitter())
        self.assertIsNone(json.loads(buf.getvalue())["pending"])

    def test_the_code_side_sync_sends_what_is_pending_and_nothing_else(self):
        self.assertEqual("nothing pending", push_mod.sync_store(self.path)["skipped"])
        self.write(1, "synced")
        got = push_mod.sync_store(self.path)
        self.assertEqual(([1], "collapsed"), (got["sent"], got["history"]))
        self.assertTrue(self.remote_file("specs/1.md").endswith("synced\n"))

    def _failing_card(self) -> FakeCard:
        """Spec 1's title changes locally while its tracker refuses every update."""
        fake = FakeCard()
        fake.fail_updates = True
        self.backend._card_client = fake
        info, _ = self.backend.read_spec(1)
        self.backend.write_spec(info, info["text"].replace("title: One", "title: Renamed"))
        return fake

    def test_a_card_failure_after_the_code_side_sync_is_a_warning_not_a_failed_sync(self):
        fake = self._failing_card()
        got = push_mod.sync_store(self.path)
        self.assertTrue(got["ok"], got)
        self.assertEqual([1], got["sent"])
        self.assertEqual([1], [f["id"] for f in got["cardFailures"]])
        self.assertEqual(["update"], fake.verbs())
        note = git_push._specs_note(got)
        self.assertIn("spec store synced (1 spec(s) sent)", note)
        self.assertIn("warning: spec 1 is written, but its card could not be updated", note)
        self.assertNotIn("not synced", note)

    def test_the_push_verb_reports_a_card_failure_beside_the_push(self):
        self._failing_card()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = push_mod.cmd_push(argparse.Namespace(json=False, drop=None), self.path,
                                     Emitter())
        self.assertEqual(0, code, buf.getvalue())
        self.assertIn("pushed 1 spec(s)", buf.getvalue())
        self.assertIn("warning: spec 1 is written, but its card could not be updated",
                      buf.getvalue())
        self.assertIsNone(self.backend._pending())

    def test_a_sync_point_under_no_fetch_still_reaches_the_remote(self):
        other = GitBackend(self.clone("b"))
        info, _ = other.read_spec(2)
        other.write_spec(info, info["text"] + "\nfrom b\n")
        other.push()
        with mock.patch.dict(os.environ, {git_mod.NO_FETCH_ENV: "1"}), \
                mock.patch.object(git_mod, "FETCH_TTL_S", 0):
            self.write(1, "offline read, online sync")
            got = push_mod.sync_store(self.path)
        self.assertTrue(got["ok"], got)
        self.assertEqual(([1], 2), (got["sent"], got["attempts"]))   # stale lease, then fetch
        self.assertTrue(self.remote_file("specs/1.md").endswith("offline read, online sync\n"))
        self.assertTrue(self.remote_file("specs/2.md").endswith("from b\n"))
        self.assertIsNone(self.backend._pending())

    def test_a_pr_create_syncs_the_store_after_opening_the_pr(self):
        self.write(2, "with the pr")

        def gh(*argv, stdin=None):
            return 0, "https://github.com/o/r/pull/7\n", ""
        with mock.patch("os.getcwd", return_value=self.path), \
                mock.patch.object(pull, "_provider", return_value="github"), \
                mock.patch.object(pull, "_gh", side_effect=gh), \
                mock.patch.object(pull, "_branch_ok", return_value=True), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            code = pull.cmd_pr(SimpleNamespace(
                action="create", base="main", head="plan/2-x", title="t", body="b", spec=None,
                json=True, work_item=None, transition_work_items=False,
                delete_source_branch=False))
        payload = json.loads(out.getvalue())
        self.assertEqual(0, code, payload)
        self.assertEqual((7, [2]), (payload["number"], payload["specs"]["sent"]))
        self.assertTrue(self.remote_file("specs/2.md").endswith("with the pr\n"))
        self.assertIsNone(self.backend._pending())

    def test_a_code_push_syncs_the_store_after_the_branch(self):
        self.write(2, "with the code")
        _sh(self.path, "checkout", "--quiet", "-b", "plan/2-x")
        _sh(self.path, "-c", "user.name=f", "-c", "user.email=f@example.test", "commit",
            "--quiet", "--allow-empty", "-m", "work")
        with mock.patch("os.getcwd", return_value=self.path), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            code = git_push.cmd_push(SimpleNamespace(branch="plan/2-x", remote="origin",
                                                     json=True))
        payload = json.loads(out.getvalue())
        self.assertEqual(0, code, payload)
        self.assertEqual([2], payload["specs"]["sent"])
        self.assertTrue(self.remote_file("specs/2.md").endswith("with the code\n"))

    def test_a_merge_syncs_after_its_stamp(self):
        def gh(*argv):
            if "state" in argv:
                return 0, json.dumps({"state": "MERGED"}), ""
            return 0, json.dumps({"number": 7, "headRefName": "plan/1-x"}), ""
        order = []
        real_sync = push_mod.sync_store

        def sync(root):
            order.append("sync")
            return real_sync(self.path)
        with mock.patch.object(pull, "_gh", side_effect=gh), \
                mock.patch.object(pull, "_provider", return_value="github"), \
                mock.patch.object(pull, "open_backend", return_value=(self.backend, {})), \
                mock.patch("quenching.specs.commands.fields.open_backend",
                           return_value=(self.backend, {})), \
                mock.patch.object(pull, "sync_store", side_effect=sync), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            code = pull.cmd_pr(SimpleNamespace(action="merge", url="https://github.com/o/r/pull/7",
                                               wait=0, json=True, spec="1"))
        payload = json.loads(out.getvalue())
        self.assertEqual(0, code, payload)
        self.assertEqual(["sync"], order)
        self.assertEqual([1], payload["specs"]["sent"])
        self.assertIn("merge:", self.remote_file("specs/1.md"))
        self.assertIsNone(self.backend._pending())


if __name__ == "__main__":
    unittest.main()
