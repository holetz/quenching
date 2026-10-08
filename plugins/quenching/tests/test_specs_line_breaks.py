"""Spec text is split on `\\n` only: a U+2028 inside a task line stays inside that line (spec 1392)."""
import unittest
from types import SimpleNamespace

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring

from test_specs_duplicate_heading import _Base
from quenching.specs.commands.task import cmd_discover
from quenching.specs.parse.sections import parse_sections
from quenching.specs.parse.tasks import parse_tasks
from quenching.specs.parse.text import split_lines

ODD = [" ", " ", "\x85", "\v", "\f", "\x1c", "\x1d", "\x1e"]


class TheSplit(unittest.TestCase):
    def test_it_breaks_on_newline_and_crlf_only(self):
        self.assertEqual(split_lines("a\nb\r\nc\n"), ["a", "b", "c"])
        self.assertEqual(split_lines("a\nb\n", keepends=True), ["a\n", "b\n"])
        self.assertEqual(split_lines(""), [])
        for c in ODD:
            with self.subTest(char=hex(ord(c))):
                self.assertEqual(split_lines(f"a{c}b\nc"), [f"a{c}b", "c"])


class TheTaskParser(unittest.TestCase):
    def test_a_break_inside_a_task_line_keeps_its_metadata(self):
        for c in ODD:
            with self.subTest(char=hex(ord(c))):
                text = ("## Tasks\n\n### 1. A\n\n"
                        f"- [ ] 1.2 a{c}b\n      files: a.py\n      verify: true\n")
                task = parse_tasks(text)[0]
                self.assertEqual(task["files"], ["a.py"])
                self.assertEqual(task["verify"], "true")
                self.assertIn("Tasks", parse_sections(text))


class TheDiscoverWriter(_Base):
    def test_it_refuses_a_text_that_would_be_more_than_one_line(self):
        before = self.text()
        for c in ["\n", "\r", *ODD]:
            with self.subTest(char=hex(ord(c))):
                code, obj = self.call(cmd_discover,
                                      SimpleNamespace(json=True, spec=1, text=f"achado{c}outro"))
                self.assertEqual(code, 2, obj)
                self.assertEqual(obj.get("code"), "sp-discover-multiline")
                self.assertEqual(self.text(), before)

    def test_it_records_a_single_line(self):
        code, _ = self.call(cmd_discover, SimpleNamespace(json=True, spec=1, text="achado"))
        self.assertEqual(code, 0)
        self.assertIn("- achado", self.text())


if __name__ == "__main__":
    unittest.main()
