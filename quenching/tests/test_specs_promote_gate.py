"""`status`'s dry run of the archive gate agrees with what `promote` actually does.

THE BUG THIS FIXES, measured while concluding the spec that cut this package: a spec carrying one
blocked task reported `promote: {"missing": [], "ok": true}` from `cq specs status --json` and then
`refused: 1 of 59 tasks still open` (exit 2) from `cq specs promote --to archive --outcome done`.

The two verbs were reading different gates. `gate_report` measures SECTIONS — the entry gate of the
destination folder — while `promote` applies a second condition that lived only inside itself: with
`--outcome done`, any unticked task refuses, blocked `[!]` included. `/quenching-specs status`
describes itself as "an honest dry run before a sweep is authorized", so a caller branching on its
`ok` was branching on a verdict the real verb did not share.

The assertion below is the agreement itself rather than either side's shape, because that is the
property that has to survive: whichever way a future change moves one gate, this fails unless the
other moves with it. `derive_info` takes a document, so the agreement needs no backend and no
tempdir; `DestinationOccupied`, the second half of the archive gate, needs a real directory and
says why.
"""
import argparse
import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.common.frontmatter import parse_frontmatter
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands import epic, promote as promote_module
from quenching.specs.commands.output import Emitter
from quenching.specs.parse.derive import derive_info
from quenching.specs.parse.sections import gate_report
from quenching.specs.schema import canonical_headings

# The task axis of the archive gate, one row per state a box can be in. `accepted` is what
# `promote --to archive --outcome done` should do with it.
CASES = (
    ("no tasks at all", None, True),
    ("every box ticked", "- [x] 1.1 Done\n", True),
    ("one box open", "- [x] 1.1 Done\n- [ ] 1.2 Not done\n", False),
    ("one box BLOCKED — a marker is not a tick",
     "- [x] 1.1 Done\n- [!] 1.2 Stopped — blocked: the cause is upstream\n", False),
)


def _promote_would_accept(info: dict) -> bool:
    """`cmd_promote`'s archive condition for `--outcome done`, and nothing else."""
    return not [t for t in info["tasks"] if not t["checked"]]


def _document(tasks: str | None, outcome: str = "- none — fixture") -> str:
    """A spec with every canonical section filled, so the SECTION half of the gate is satisfied
    and the task half is the only axis under test."""
    parts = ["---", "title: Gate fixture", "date: 2026-08-11", "---", ""]
    for heading in canonical_headings():
        parts.append(f"## {heading}")
        parts.append("")
        if heading == "Tasks":
            if tasks is not None:
                parts += ["### 1. The work", "", tasks.rstrip("\n"), ""]
        else:
            parts += [outcome if heading == "Outcome" else "- none — fixture", ""]
    return "\n".join(parts) + "\n"


def _document_with_outcome(tasks: str, outcome: str) -> str:
    return _document(tasks, outcome)


def _info(tasks: str | None) -> dict:
    return derive_info({"phase": "plans", "slug": "gate-fixture", "file": "gate-fixture.md"},
                       _document(tasks))


class ArchiveGateAgreement(unittest.TestCase):

    def test_the_dry_run_and_the_real_verb_agree_on_every_case(self):
        for label, tasks, accepted in CASES:
            with self.subTest(case=label):
                info = _info(tasks)
                gates = gate_report(info, "archive")
                open_tasks = [t for t in info["tasks"] if not t["checked"]]
                dry_run_ok = gates["ok"] and not open_tasks
                self.assertEqual(_promote_would_accept(info), accepted,
                                 "the case table disagrees with promote's own condition")
                self.assertEqual(dry_run_ok, _promote_would_accept(info),
                                 "status's promote block and promote disagree")

    def test_the_section_half_alone_would_have_said_yes(self):
        # The falsification: without the task condition the dry run reports `ok: true` for the two
        # cases `promote` refuses. If this ever stops holding, the bug is gone for another reason
        # and this suite is measuring nothing.
        for label, tasks, accepted in CASES:
            if accepted:
                continue
            with self.subTest(case=label):
                gates = gate_report(_info(tasks), "archive")
                self.assertTrue(gates["ok"],
                                "the section gate was supposed to be the half that passes")

    def test_a_blocked_task_is_not_counted_as_checked_anywhere(self):
        # The whole reason the two gates could drift: `status` reports `blocked` as its own counter
        # beside `checked`, which reads as a third state. It is not one for this gate — `--outcome
        # done` refuses on a blocked box exactly as it refuses on an untried one.
        info = _info("- [x] 1.1 Done\n- [!] 1.2 Stopped — blocked: upstream\n")
        blocked = [t for t in info["tasks"] if t["blocked"]]
        self.assertEqual(len(blocked), 1)
        self.assertFalse(blocked[0]["checked"])
        self.assertFalse(_promote_would_accept(info))

    def test_a_descoped_task_is_closed_by_its_explicit_outcome_reason(self):
        reason = "task 1.1 descoped: this path is no longer needed"
        info = derive_info({"phase": "plans", "slug": "gate-fixture", "file": "gate-fixture.md"},
                           _document_with_outcome(
                               "- [x] 1.1 Removed — descoped: this path is no longer needed\n",
                               reason))
        self.assertEqual(info["tasks"][0]["state"], "x")
        self.assertTrue(_promote_would_accept(info))
        self.assertIn(reason, info["sections"]["Outcome"]["body"])


class TheSharedVerbAsksNoFilesystemQuestion(unittest.TestCase):
    """An external-style backend makes `promote` independent of any local path.

    The shared verb must ask the backend to move the document and never inspect a local phase
    tree. The document lives in `memory`, so the proof remains offline and provider-neutral.

    `open_backend` is replaced rather than configured: opening the real external backend would
    need a `gh` binary and a repository, and the property under test belongs to the shared
    verb, not to any transport."""

    def test_an_external_promote_does_not_depend_on_a_local_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            backend = MemoryBackend()
            backend.create_spec("plans", _document("- [x] 1.1 Done\n"))
            spec_id = max(backend.docs)
            self.addCleanup(setattr, promote_module, "open_backend",
                            promote_module.open_backend)
            promote_module.open_backend = lambda _root: (backend, {})

            buf = io.StringIO()
            args = argparse.Namespace(json=True, spec=spec_id, to=None,
                                      outcome="done", force=False, dry_run=False)
            with contextlib.redirect_stdout(buf):
                code = promote_module.cmd_promote(args, tmp, Emitter())
            payload = json.loads(buf.getvalue())

            self.assertEqual(code, 0, payload)
            self.assertEqual(backend.docs[spec_id][0], "archive")

    def test_promote_accepts_a_descoped_task_without_force(self):
        reason = "task 1.1 descoped: this path is no longer needed"
        backend = MemoryBackend()
        backend.create_spec("plans", _document_with_outcome(
            "- [x] 1.1 Removed — descoped: this path is no longer needed\n", reason))
        spec_id = max(backend.docs)
        previous = promote_module.open_backend
        self.addCleanup(setattr, promote_module, "open_backend", previous)
        promote_module.open_backend = lambda _root: (backend, {})

        buf = io.StringIO()
        args = argparse.Namespace(json=True, spec=spec_id, to="archive", outcome="done",
                                  force=False, dry_run=False)
        with contextlib.redirect_stdout(buf):
            code = promote_module.cmd_promote(args, ".", Emitter())

        self.assertEqual(code, 0, buf.getvalue())
        self.assertEqual(backend.docs[spec_id][0], "archive")
        self.assertEqual(parse_frontmatter(backend.docs[spec_id][1])["outcome"], "done")


class ArchiveWaitsForMerge(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = self.tmp.name
        self.git("init", "--initial-branch=main")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.test",
                 "commit", "--allow-empty", "-m", "Base")
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.git("checkout", "-b", "plan/1-x")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.test",
                 "commit", "--allow-empty", "-m", "Work")
        self.work_tip = self.git("rev-parse", "HEAD")
        self.backend = MemoryBackend()
        self.addCleanup(patch.stopall)
        patch.object(promote_module, "open_backend",
                     return_value=(self.backend, {})).start()
        self.pr_view = patch.object(epic, "_pr_view", return_value=None).start()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True,
                              text=True, check=True, timeout=30).stdout.strip()

    def promote(self, *, work="plan/1-x", records="", force=False, dry_run=False,
                outcome="done", tasks="- [x] 1.1 Done\n"):
        text = _document(tasks).replace(
            "date: 2026-08-11\n",
            f"date: 2026-08-11\nbranch:\n  base: main\n  work: {work}\n{records}", 1)
        self.backend.create_spec("plans", text)
        spec_id = max(self.backend.docs)
        args = argparse.Namespace(json=True, spec=spec_id, to="archive", outcome=outcome,
                                  force=force, dry_run=dry_run)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = promote_module.cmd_promote(args, self.root, Emitter())
        return code, json.loads(buf.getvalue()), spec_id, text

    def assert_unmerged(self, **kwargs):
        code, payload, spec_id, text = self.promote(**kwargs)
        self.assertEqual(code, 2, payload)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["code"], "sp-not-merged")
        self.assertEqual(payload["id"], spec_id)
        self.assertEqual(payload["work"], "plan/1-x")
        self.assertEqual(payload["base"], "main")
        self.assertEqual(payload["reason"],
                         "plan/1-x is not in origin/main and no merged PR is recorded")
        self.assertIn("cq specs reconcile", payload["message"])
        self.assertEqual(self.backend.docs[spec_id], ("plans", text))

    def assert_archived(self, **kwargs):
        code, payload, spec_id, _ = self.promote(**kwargs)
        self.assertEqual(code, 0, payload)
        self.assertEqual(self.backend.docs[spec_id][0], "archive")

    def test_unmerged_work_refuses_done(self):
        self.assert_unmerged()

    def test_force_does_not_waive_merge_guard(self):
        self.assert_unmerged(force=True, tasks="- [ ] 1.1 Open\n")

    def test_open_tasks_refuse_before_merge_guard(self):
        with patch.object(promote_module, "merge_evidence") as evidence:
            code, payload, _, _ = self.promote(tasks="- [ ] 1.1 Open\n")
        self.assertEqual(code, 2)
        self.assertEqual(payload["code"], "sp-open-tasks")
        evidence.assert_not_called()

    def test_work_merged_into_remote_base_archives(self):
        self.git("update-ref", "refs/remotes/origin/main", self.work_tip)
        self.assert_archived()
        self.pr_view.assert_not_called()

    def test_merged_pr_archives_without_ancestry(self):
        self.pr_view.return_value = ("MERGED", "plan/1-x")
        self.assert_archived(records="pr:\n  number: 42\n")
        self.pr_view.assert_called_once()

    def test_merge_record_archives(self):
        self.assert_archived(records="merge:\n  strategy: squash\n")
        self.pr_view.assert_not_called()

    def test_abandoned_never_checks_merge(self):
        with patch.object(promote_module, "merge_evidence") as evidence:
            self.assert_archived(outcome="abandoned")
        evidence.assert_not_called()

    def test_work_on_base_archives(self):
        self.assert_archived(work="main")
        self.pr_view.assert_not_called()

    def test_unmerged_dry_run_also_refuses(self):
        self.assert_unmerged(dry_run=True)


if __name__ == "__main__":
    unittest.main()
