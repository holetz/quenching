"""CLI text that lands on one line of a spec — a `### N.` group heading, a task line, a task's
`subject:` anchor — refuses every character `str.splitlines` breaks on, so no value can forge the
lines after it. One test per verb; each refusal leaves the stored documents exactly as they were."""
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring

from test_specs_epics import EPIC_ID, add, doc, epic_doc
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


if __name__ == "__main__":
    unittest.main()
