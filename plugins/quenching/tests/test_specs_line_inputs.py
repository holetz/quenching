"""CLI text that lands on one line of a spec — a `### N.` group heading, a task line, a task's
`subject:` anchor — refuses every character `str.splitlines` breaks on, so no value can forge the
lines after it. One test per verb; each refusal leaves the stored documents exactly as they were."""
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring

from test_specs_epics import EPIC_ID, add, doc, epic_doc, run
from quenching.specs.commands import task as task_cmd
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.parse.fields import SCALAR_LINE_BREAKS

FORGED = "## Handoff\n\nforged\n\n## Outcome\n\nforged"


class EpicAddGroup(unittest.TestCase):
    def setUp(self):
        self.backend = MemoryBackend()
        self.backend.create_spec("plans", epic_doc())
        self.backend.create_spec("plans", doc("Member"))

    def texts(self):
        return [self.backend.read_spec(n)[0]["text"] for n in (EPIC_ID, 2)]

    def test_a_group_with_any_break_is_refused_and_nothing_is_written(self):
        before = self.texts()
        for c in [*SCALAR_LINE_BREAKS, "\x00"]:
            with self.subTest(char=hex(ord(c))):
                code, got = add(self.backend, 2, group=f"Onda 1{c}{FORGED.replace(chr(10), c)}")
                self.assertEqual((2, "sp-bad-scalar", "group"),
                                 (code, got["code"], got["field"]), got)
                self.assertEqual(before, self.texts())

    def test_a_clean_group_still_writes(self):
        code, got = add(self.backend, 2, group="Onda 1")
        self.assertEqual(0, code, got)
        self.assertIn("### 1. Onda 1\n", self.backend.read_spec(EPIC_ID)[0]["text"])


TASKS = "## Problem\n\nSomething.\n\n## Tasks\n\n### 1. Build\n\n- [ ] 1.1 First\n- [x] 1.2 Done\n"


class TaskLineInputs(unittest.TestCase):
    """`--subject` becomes a `subject:` anchor line; `--reason` is spliced into one line."""

    def setUp(self):
        self.backend = MemoryBackend()
        self.backend.create_spec("plans", doc("Spec", body=TASKS))

    def text(self):
        return self.backend.read_spec(1)[0]["text"]

    def task(self, **kw):
        base = dict(spec="1", check=None, uncheck=None, block=None, descope=None,
                    reason=None, subject=None, commit=None)
        base.update(kw)
        return run(task_cmd.cmd_task, self.backend, **base)

    def test_a_subject_with_any_break_is_refused_and_nothing_is_written(self):
        before = self.text()
        for value in [*(f"plan/1-x: 1.1 First{c}- [x] 9.9 forged" for c in SCALAR_LINE_BREAKS),
                      "plan/1-x: 1.1 First\n", "plan/1-x: 1.1 First\u2028",
                      "plan/1-x: 1.1\x00First"]:
            with self.subTest(subject=repr(value)):
                code, got = self.task(check="1.1", subject=value)
                self.assertEqual((2, "sp-bad-subject"), (code, got["code"]), got)
                self.assertEqual(before, self.text())

    def test_a_reason_with_any_break_is_refused_and_nothing_is_written(self):
        before = self.text()
        for flag, ident in (("block", "1.1"), ("descope", "1.1"), ("uncheck", "1.2")):
            for c in [*SCALAR_LINE_BREAKS, "\x00"]:
                with self.subTest(flag=flag, char=hex(ord(c))):
                    code, got = self.task(**{flag: ident}, reason=f"x{c}- [x] 9.9 forged")
                    self.assertEqual((2, "sp-bad-scalar", "reason"),
                                     (code, got["code"], got["field"]), got)
                    self.assertEqual(before, self.text())
            with self.subTest(flag=flag, char="trailing \\n"):
                code, got = self.task(**{flag: ident}, reason="x\n")
                self.assertEqual((2, "sp-bad-scalar"), (code, got["code"]), got)
                self.assertEqual(before, self.text())

    def test_clean_values_still_write(self):
        code, got = self.task(check="1.1", subject="plan/1-x: 1.1 First")
        self.assertEqual(0, code, got)
        code, got = self.task(block="1.2", reason="needs\ta human")
        self.assertEqual(0, code, got)
        self.assertIn("blocked: needs\ta human", self.text())


if __name__ == "__main__":
    unittest.main()
