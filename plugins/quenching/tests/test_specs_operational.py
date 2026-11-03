"""`files: (operational)` — the declaration of a task that writes no repository file.

The annotation is closed grammar owned by `specs/parse/tasks.py`; this suite proves the
guards that keep it honest. `validate` refuses it beside a path (the marker would hide that
path from the verifier's collection of declared files) and warns when the marker has no
`verify:` to be proved by. A `[P]` group carrying one is never eligible, because a group's
proof is the disjointness of the paths its tasks declare and an operational task declares
none.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401

from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands import estimate as estimate_module
from quenching.specs.commands import next as next_module
from quenching.specs.commands import parallel as parallel_module
from quenching.specs.commands import validate as validate_module
from quenching.specs.commands.cli import DISPATCH
from quenching.specs.commands.output import Emitter


DOC = """---
title: Operational
date: 2026-11-03
verification: per-section
---

# Operational

## Problem

The task writes no repository file.

## Proposal

Declare it operational.

## Out of Scope

- none — the test document is the whole subject.

## Impact

- none — no standard is written here.

## Validation

- none — the verify of each task is the proof.

## Design

- none — the annotation is the design under test.

## Alternatives Considered

- none — the alternatives are recorded in the spec that owns the annotation.

## Open Decisions

- none — nothing is left open.

## Risks

- none — the guards are what the suite proves.

## Tasks

{tasks}
"""


class Workspace(unittest.TestCase):
    """One spec document in the memory backend, driven through the CLI's own DISPATCH.

    Every consumer reads the SAME parsed row, which is what makes `(operational)` one
    declaration rather than four readings of it."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = self.tmp.name
        self.backend = MemoryBackend()

    def write(self, tasks: str) -> int:
        self.backend.create_spec("plans", DOC.format(tasks=tasks))
        return max(self.backend.docs)

    def dispatch(self, verb: str, module, **kwargs):
        args = argparse.Namespace(json=True, **kwargs)
        buf = io.StringIO()
        with mock.patch.object(module, "open_backend",
                               lambda _root: (self.backend, {})), \
                contextlib.redirect_stdout(buf):
            code = DISPATCH[verb](args, self.root, Emitter())
        return code, json.loads(buf.getvalue())

    def validate(self, ident: int):
        return self.dispatch("validate", validate_module, spec=str(ident), phase=None,
                             by_code=False)

    def parallel(self, ident: int):
        return self.dispatch("parallel", parallel_module, spec=str(ident))

    def next(self, ident: int):
        return self.dispatch("next", next_module, spec=str(ident), front=False, table=False,
                             columns=None, order="rank")

    def estimate(self, ident: int, task: str | None = None):
        return self.dispatch("estimate", estimate_module, spec=str(ident),
                             worker_budget=100000, task=task)

    def codes(self, ident: int) -> list[str]:
        return [f["code"] for f in self.validate(ident)[1]["findings"]]


class Validate(Workspace):
    def test_operational_alone_is_accepted(self):
        ident = self.write("### 1. One\n\n- [ ] 1.1 Gate\n"
                           "      files: (operational)\n"
                           "      verify: systemctl --user is-active app\n")
        code, payload = self.validate(ident)
        self.assertEqual(code, 0)
        self.assertEqual([f for f in payload["findings"] if f["severity"] == "error"], [])
        self.assertNotIn("sp-files-annotation", self.codes(ident))
        self.assertNotIn("sp-files-operational", self.codes(ident))

    def test_operational_beside_a_path_is_refused(self):
        """The marker says the task writes no repository file; beside a path it would hide
        that path from the verifier's scope union, so the mixed form is an error."""
        ident = self.write("### 1. One\n\n- [ ] 1.1 Gate\n"
                           "      files: src/a.py, (operational)\n"
                           "      verify: make check\n")
        code, payload = self.validate(ident)
        self.assertEqual(code, 1)
        self.assertIn("sp-files-operational", [f["code"] for f in payload["findings"]])

    def test_an_operational_task_without_a_verify_is_warned_not_refused(self):
        """The annotation's only proof is the `verify:`: without one it proves nothing, and
        the finding says so without blocking the spec — the box is still tickable. The
        control below is what keeps the warning from firing on the proved task."""
        ident = self.write("### 1. One\n\n- [ ] 1.1 Gate\n      files: (operational)\n")
        code, payload = self.validate(ident)
        self.assertEqual(code, 0)
        warned = [f for f in payload["findings"] if f["code"] == "sp-operational-no-verify"]
        self.assertEqual(len(warned), 1)
        self.assertEqual(warned[0]["severity"], "warn")

        proved = self.write("### 1. One\n\n- [ ] 1.1 Gate\n      files: (operational)\n"
                            "      verify: make check\n")
        self.assertNotIn("sp-operational-no-verify", self.codes(proved))


class Parallel(Workspace):
    def test_a_group_with_an_operational_task_is_ineligible(self):
        ident = self.write("### 1. One\n\n"
                           "- [ ] 1.1 [P] Alpha\n      files: src/a.py\n"
                           "- [ ] 1.2 [P] Beta\n      files: (operational)\n"
                           "      verify: make check\n")
        code, payload = self.parallel(ident)
        self.assertEqual(code, 1)
        group = payload["groups"][0]
        self.assertFalse(group["eligible"])
        self.assertEqual(group["undeclared"], ["1.2"],
                         "an operational task declares no path, so the group has nothing "
                         "to prove disjoint")

    def test_a_group_of_declared_paths_stays_eligible(self):
        ident = self.write("### 1. One\n\n"
                           "- [ ] 1.1 [P] Alpha\n      files: src/a.py\n"
                           "- [ ] 1.2 [P] Beta\n      files: src/b.py\n")
        code, payload = self.parallel(ident)
        self.assertEqual(code, 0)
        self.assertTrue(payload["groups"][0]["eligible"])


class Next(Workspace):
    def test_an_operational_task_is_handed_on_as_no_files(self):
        """The chain `no files: → tick with no commit` already exists; the annotation adds
        the DECLARATION the verifier reads, never a second execution path."""
        ident = self.write("### 1. One\n\n- [ ] 1.1 Gate\n      files: (operational)\n"
                           "      verify: make check\n")
        code, payload = self.next(ident)
        self.assertEqual(code, 0)
        self.assertEqual(payload["action"], "implement_task")
        self.assertEqual(payload["files"], [])
        self.assertTrue(payload["operational"])

    def test_the_mixed_form_never_reaches_an_executor(self):
        ident = self.write("### 1. One\n\n- [ ] 1.1 Gate\n"
                           "      files: src/a.py, (operational)\n"
                           "      verify: make check\n")
        code, payload = self.next(ident)
        self.assertEqual(code, 1)
        self.assertEqual(payload["code"], "sp-files-operational")


class Estimate(Workspace):
    def test_an_operational_task_is_out_of_the_unresolved_inputs(self):
        ident = self.write("### 1. One\n\n- [ ] 1.1 Gate\n      files: (operational)\n"
                           "      verify: make check\n")
        code, payload = self.estimate(ident)
        self.assertEqual(code, 0)
        self.assertEqual(payload["sections"][0]["unresolved"], [])
        self.assertTrue(payload["complete"])

    def test_the_task_projection_has_nothing_to_size(self):
        ident = self.write("### 1. One\n\n- [ ] 1.1 Gate\n      files: (operational)\n"
                           "      verify: make check\n")
        code, row = self.estimate(ident, task="1.1")
        self.assertEqual(code, 0)
        self.assertEqual((row["bytes"], row["readTokens"], row["unresolved"]), (0, 0, []))
        self.assertFalse(row["smallTierEligible"],
                         "an operational task has no files: to pin a small tier on")


class CodexEligible(Workspace):
    def eligible(self, ident: int, task_id: str):
        from quenching.codex import eligible as eligible_module
        from quenching.codex.config import DEFAULTS
        settings = {**DEFAULTS, "maxUsedPercent": dict(DEFAULTS["maxUsedPercent"]),
                    "executor": {**DEFAULTS["executor"]}}
        quota = lambda _settings: {"state": "available", "reason": "test"}  # noqa: E731
        with mock.patch.object(eligible_module, "open_backend",
                               lambda _root: (self.backend, {})):
            return eligible_module.run_eligible(self.root, settings, str(ident), task_id,
                                                quota)

    def test_an_operational_task_is_refused_with_its_own_reason(self):
        ident = self.write("### 1. One\n\n- [ ] 1.1 Gate\n      files: (operational)\n"
                           "      verify: make check\n")
        payload, code = self.eligible(ident, "1.1")
        self.assertEqual(code, 1)
        self.assertIn("(operational)", payload["reason"])


if __name__ == "__main__":
    unittest.main()
