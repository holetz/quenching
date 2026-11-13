"""Post-merge close reuses promote's gates and is idempotent across backend moves."""
import argparse
import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import _paths  # noqa: F401
from quenching.common.frontmatter import parse_frontmatter
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands import epic, promote, reconcile
from quenching.specs.commands.output import Emitter
from test_specs_promote_gate import _document


class Reconcile(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = tmp.name
        self.git("init", "--initial-branch=main")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.test",
                 "commit", "--allow-empty", "-m", "Base")
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.git("checkout", "-b", "plan/1-x")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.test",
                 "commit", "--allow-empty", "-m", "Work")
        self.work_tip = self.git("rev-parse", "HEAD")
        self.backend = MemoryBackend()
        for module in (reconcile, promote):
            p = patch.object(module, "open_backend", return_value=(self.backend, {}))
            p.start()
            self.addCleanup(p.stop)
        p = patch.object(epic, "_pr_view", return_value=None)
        self.pr_view = p.start()
        self.addCleanup(p.stop)

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True,
                              text=True, check=True, timeout=30).stdout.strip()

    def spec(self, *, merged=True, work="plan/1-x", outcome="Delivered the work.",
             tasks="- [x] 1.1 Done\n"):
        text = _document(tasks, outcome).replace(
            "date: 2026-08-11\n",
            f"date: 2026-08-11\nbranch:\n  base: main\n  work: {work}\n", 1)
        self.backend.create_spec("plans", text)
        if merged:
            self.git("update-ref", "refs/remotes/origin/main", self.work_tip)
        return max(self.backend.docs)

    def run_reconcile(self, *, write=False, as_json=True, remote="origin"):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = reconcile.cmd_reconcile(
                argparse.Namespace(json=as_json, write=write, remote=remote),
                self.root, Emitter())
        self.assertEqual(code, 0, buf.getvalue())
        return json.loads(buf.getvalue()) if as_json else buf.getvalue()

    def test_dry_run_leaves_the_merged_spec_in_plans(self):
        spec_id = self.spec()
        payload = self.run_reconcile()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["specs"][0]["id"], spec_id)
        self.assertEqual(payload["specs"][0]["action"], "would-archive")
        self.assertEqual(self.backend.docs[spec_id][0], "plans")
        self.pr_view.assert_not_called()

    def test_write_archives_as_done_and_a_second_run_is_empty(self):
        spec_id = self.spec()
        self.assertEqual(self.run_reconcile(write=True)["specs"][0]["action"], "archived")
        phase, text = self.backend.docs[spec_id]
        self.assertEqual(phase, "archive")
        self.assertEqual(parse_frontmatter(text)["outcome"], "done")
        self.assertEqual(self.run_reconcile(write=True)["specs"], [])

    def test_missing_outcome_needs_a_human_even_with_write(self):
        for outcome in ("", "<!-- fill this in -->"):
            with self.subTest(outcome=outcome):
                spec_id = self.spec(outcome=outcome)
                row = next(r for r in self.run_reconcile(write=True)["specs"]
                           if r["id"] == spec_id)
                self.assertEqual(row["action"], "needs-human")
                self.assertEqual(row["why"], "merged but ## Outcome is not written")
                self.assertEqual(self.backend.docs[spec_id][0], "plans")

    def test_unmerged_and_non_isolated_specs_are_not_listed(self):
        self.spec(merged=False)
        self.spec(merged=False, work="main")
        self.assertEqual(self.run_reconcile(write=True)["specs"], [])

    def test_open_tasks_use_the_promote_refusal(self):
        spec_id = self.spec(tasks="- [ ] 1.1 Still open\n")
        row = self.run_reconcile(write=True)["specs"][0]
        self.assertEqual(row["action"], "needs-human")
        self.assertIn("1 of 1 tasks still open", row["why"])
        self.assertEqual(self.backend.docs[spec_id][0], "plans")

    def test_fetch_happens_once_and_evidence_reuses_it(self):
        self.spec()
        self.spec()
        with patch.object(reconcile.subprocess, "run", side_effect=OSError) as fetch, \
                patch.object(promote, "merge_evidence", return_value=(True, "fixture")) as evidence:
            payload = self.run_reconcile(remote="upstream")
        self.assertEqual(payload["count"], 2)
        self.assertEqual(payload["remote"], "upstream")
        fetch.assert_called_once_with(["git", "fetch", "--quiet", "upstream"],
                                      cwd=self.root, capture_output=True, text=True, timeout=30)
        self.assertEqual(evidence.call_count, 2)
        for call in evidence.call_args_list:
            self.assertEqual(call.args[2], "upstream")
            self.assertEqual(call.kwargs, {"fetch": False})

    def test_human_output_explains_a_missing_outcome(self):
        self.spec(outcome="")
        human = self.run_reconcile(as_json=False)
        self.assertIn("reconcile — 1 merged spec(s) not archived", human)
        self.assertIn("needs-human", human)
        self.assertIn("merged but ## Outcome is not written", human)


if __name__ == "__main__":
    unittest.main()


class ReconcileReleasesTheSlot(Reconcile):
    def test_an_archived_spec_gives_its_slot_back(self):
        from quenching.git import slots

        self.git("checkout", "-q", "main")
        slot = os.path.join(os.path.dirname(self.root),
                            os.path.basename(self.root) + "-slot-1")
        self.addCleanup(subprocess.run, ["rm", "-rf", slot])
        self.git("worktree", "add", "-q", "--lock", "--reason", "quenching: 1 · s · h · d",
                 slot, "plan/1-x")
        self.spec()
        row = self.run_reconcile(write=True)["specs"][0]
        self.assertEqual(row["action"], "archived")
        self.assertTrue(row["slot"]["released"], row)
        state = slots.survey(self.root)["slots"][0]
        self.assertEqual(state["state"], "free")
        self.assertIsNone(state["branch"])

    def test_a_spec_built_outside_a_slot_releases_nothing(self):
        self.spec()
        self.assertIsNone(self.run_reconcile(write=True)["specs"][0]["slot"])
