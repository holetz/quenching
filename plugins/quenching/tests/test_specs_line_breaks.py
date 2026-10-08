"""Spec text is split on `\\n` only: a U+2028 inside a task line stays inside that line (spec 1392)."""
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring

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


if __name__ == "__main__":
    unittest.main()
