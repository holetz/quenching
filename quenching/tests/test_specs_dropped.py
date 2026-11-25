"""`(dropped → <id>)` — an abandoned task names the task that replaced it; `validate` refuses a target that is not a live task of the document and the verifier body carries the check-2 rule."""
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
from quenching.specs.commands import granular as granular_module
from quenching.specs.commands import next as next_module
from quenching.specs.commands import parallel as parallel_module
from quenching.specs.commands import task as task_module
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


class Dropped(Workspace):
    PLAIN = ("### 1. A\n\n"
             "- [x] 1.3 Old {m}\n      files: a.py\n      verify: true\n"
             "- [x] 1.6 New\n      files: b.py\n      verify: true\n      commit: abc1234\n")

    def test_valid_marker_passes_and_shows(self):
        ident = self.write(self.PLAIN.format(m="(dropped → 1.6)"))
        self.assertNotIn("sp-dropped-target", self.codes(ident))
        _, payload = self.dispatch("show", granular_module, spec=str(ident), task=["1.3"],
                                   full=False, section=None, line=None, grep=None)
        self.assertEqual(payload["tasks"][0]["dropped"], "1.6")

    def test_ascii_arrow_and_no_marker(self):
        ident = self.write(self.PLAIN.format(m="(dropped -> 1.6)"))
        self.assertNotIn("sp-dropped-target", self.codes(ident))
        _, payload = self.dispatch("show", granular_module, spec=str(ident), task=["1.3", "1.6"],
                                   full=False, section=None, line=None, grep=None)
        self.assertEqual([t["dropped"] for t in payload["tasks"]], ["1.6", None])

    def test_missing_target_is_refused(self):
        ident = self.write(self.PLAIN.format(m="(dropped → 9.9)"))
        self.assertIn("sp-dropped-target", self.codes(ident))

    def test_self_target_is_refused(self):
        ident = self.write(self.PLAIN.format(m="(dropped → 1.3)"))
        self.assertIn("sp-dropped-target", self.codes(ident))

    def test_dropped_target_is_refused(self):
        ident = self.write("### 1. A\n\n"
                           "- [x] 1.3 Old (dropped → 1.4)\n      verify: true\n"
                           "- [x] 1.4 Mid (dropped → 1.6)\n      verify: true\n"
                           "- [x] 1.6 New\n      verify: true\n")
        self.assertIn("sp-dropped-target", self.codes(ident))


class DescopeReplacedBy(Workspace):
    TWO = ("### 1. A\n\n"
           "- [ ] 1.1 Old\n      files: a.py\n      verify: true\n"
           "- [x] 1.2 New\n      files: b.py\n      verify: true\n      commit: abc1234\n")

    def descope(self, ident: int, **kw):
        return self.dispatch("task", task_module, spec=str(ident), check=None, uncheck=None,
                             block=None, descope="1.1", reason="rebuilt as 1.2", subject=None,
                             commit=None, **kw)

    def test_replaced_by_writes_the_dropped_marker_the_verifier_reads(self):
        ident = self.write(self.TWO)
        code, payload = self.descope(ident, replaced_by="1.2")
        self.assertEqual(code, 0, payload)
        self.assertIn("- [x] 1.1 Old (dropped → 1.2) — descoped: rebuilt as 1.2",
                      self.backend.docs[ident][1])
        _, shown = self.dispatch("show", granular_module, spec=str(ident), task=["1.1"],
                                 full=False, section=None, line=None, grep=None)
        self.assertEqual(shown["tasks"][0]["dropped"], "1.2")
        self.assertNotIn("sp-dropped-target", self.codes(ident))

    def test_without_replaced_by_the_line_carries_no_marker(self):
        ident = self.write(self.TWO)
        code, _ = self.descope(ident, replaced_by=None)
        self.assertEqual(code, 0)
        self.assertNotIn("dropped →", self.backend.docs[ident][1])

    def test_an_unknown_or_own_target_is_refused_and_writes_nothing(self):
        ident = self.write(self.TWO)
        before = self.backend.docs[ident][1]
        for target in ("9.9", "1.1"):
            code, payload = self.descope(ident, replaced_by=target)
            self.assertEqual(code, 1)
            self.assertFalse(payload["ok"])
        self.assertEqual(self.backend.docs[ident][1], before)

    def test_replaced_by_without_descope_is_refused(self):
        ident = self.write(self.TWO)
        code, payload = self.dispatch("task", task_module, spec=str(ident), check="1.1",
                                      uncheck=None, block=None, descope=None, reason=None,
                                      subject=None, commit=None, replaced_by="1.2")
        self.assertEqual(code, 1)
        self.assertFalse(payload["ok"])

    def test_a_descoped_task_with_a_stale_annotation_is_not_flagged(self):
        ident = self.write("### 1. A\n\n"
                           "- [x] 1.1 Old (dropped → 1.2) — descoped: rebuilt\n"
                           "      files: a.py (comentario velho)\n      verify: true\n"
                           "- [x] 1.2 New\n      files: b.py\n      verify: true\n"
                           "      commit: abc1234\n")
        self.assertNotIn("sp-files-annotation", self.codes(ident))
        live = self.write("### 1. A\n\n- [ ] 1.1 Old\n"
                          "      files: a.py (comentario velho)\n      verify: true\n")
        self.assertIn("sp-files-annotation", self.codes(live))


class VerifierBody(unittest.TestCase):
    def test_check_two_carries_the_dropped_rule(self):
        text = (pathlib.Path(__file__).resolve().parents[1] / "agents" / "spec-verifier.md").read_text()
        self.assertIn("(dropped →", text)
        self.assertIn('"dropped"', text)


if __name__ == "__main__":
    unittest.main()
