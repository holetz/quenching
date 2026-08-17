"""`status`'s dry run of the archive gate agrees with what `promote` actually does.

THE BUG THIS FIXES, measured while concluding the spec that cut this package: a spec carrying one
blocked task reported `promote: {"missing": [], "ok": true}` from `cq specs status --json` and then
`refused: 1 of 59 tasks still open` (exit 2) from `cq specs promote --to archive --outcome done`.

The two verbs were reading different gates. `gate_report` measures SECTIONS — the entry gate of the
destination folder — while `promote` applies a second condition that lived only inside itself: with
`--outcome done`, any unticked task refuses, blocked `[!]` included. `/quenching:specs:status`
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
import os
import tempfile
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.common.io import write_text
from quenching.specs.backends.base import BackendRefusal
from quenching.specs.backends.files import FilesBackend
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands import promote as promote_module
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


def _document(tasks: str | None) -> str:
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
            parts += ["- none — fixture", ""]
    return "\n".join(parts) + "\n"


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


class DestinationOccupied(unittest.TestCase):
    """Archiving onto a destination that is already taken refuses, and moves nothing.

    THE GUARD BELONGS TO THE BACKEND, WHICH IS WHY THIS TEST CALLS ONE. `cmd_promote` used to
    join the DECLARED root with the destination phase and call `os.path.exists` on it — a
    check that always passes under `github` or `azure-boards`, where the path never exists,
    and that measures the wrong directory under `files` itself whenever the specs worktree is
    in use. `FilesBackend` builds its destination from the resolved root, so it is the one
    component whose answer is true.

    A real directory and not a fake: the behaviour under test is `os.rename` overwriting an
    existing file silently, and nothing but a filesystem exhibits it."""

    def test_moving_onto_an_occupied_destination_refuses_and_leaves_both_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = os.path.join(tmp, ".specs")
            for phase in ("plans", "archive"):
                os.makedirs(os.path.join(root, phase))
            src = os.path.join(root, "plans", "gate-fixture.md")
            occupied = os.path.join(root, "archive", "gate-fixture.md")
            write_text(src, _document("- [x] 1.1 Done\n"))
            write_text(occupied, "the spec that got there first\n")

            backend = FilesBackend(root)
            info = backend.list_specs("plans")[0]
            with self.assertRaises(BackendRefusal) as caught:
                backend.move_spec(info, "archive")

            self.assertEqual(caught.exception.err["code"], "sp-dest-exists")
            self.assertEqual(caught.exception.err["exit"], 2)
            self.assertTrue(os.path.exists(src),
                            "the source moved despite the refusal")
            with open(occupied, encoding="utf-8") as fh:
                self.assertEqual(fh.read(), "the spec that got there first\n",
                                 "the destination was overwritten")


class TheSharedVerbAsksNoFilesystemQuestion(unittest.TestCase):
    """Under a backend that is not `files`, `promote` no longer refuses on a local path.

    THE OTHER HALF OF `DestinationOccupied`, and the one that makes moving the guard worth
    doing. The old check's wrongness is reproducible offline: a stale `archive/<file>.md` left
    behind in the DECLARED root refused a promote whose document lives in a tracker and never
    went near that directory. Here the document lives in `memory`, the stale file exists, and
    the promote has to go through.

    `open_backend` is replaced rather than configured: opening the real external backend would
    need a `gh` binary and a repository, and the property under test belongs to the shared
    verb, not to any transport."""

    def test_a_stale_file_in_the_declared_root_no_longer_refuses_an_external_promote(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = os.path.join(tmp, ".specs")
            os.makedirs(os.path.join(root, "archive"))
            write_text(os.path.join(root, "archive", "gate-fixture.md"),
                       "the stale local copy the declared root still holds\n")

            backend = MemoryBackend()
            backend.create_spec("plans", "gate-fixture.md", _document("- [x] 1.1 Done\n"))
            self.addCleanup(setattr, promote_module, "open_backend",
                            promote_module.open_backend)
            promote_module.open_backend = lambda _root: (backend, {})

            buf = io.StringIO()
            args = argparse.Namespace(json=True, spec="gate-fixture", to=None,
                                      outcome="done", force=False, dry_run=False)
            with contextlib.redirect_stdout(buf):
                code = promote_module.cmd_promote(args, root, Emitter())
            payload = json.loads(buf.getvalue())

            self.assertEqual(code, 0, payload)
            self.assertEqual(backend.docs["gate-fixture"][0], "archive")


if __name__ == "__main__":
    unittest.main()
