"""The cold-path parser shortcuts (spec 355) change cost, never results: each is compared
against the regex/recomputing form it replaced."""

import re
import sys
import pathlib
import unittest

try:
    import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401

from quenching.specs import schema
from quenching.specs.parse.sections import parse_sections
from quenching.specs.parse.tasks import parse_tasks
from quenching.specs.parse.text import has_real_content, mask_comments, split_lines, strip_comments

SAMPLES = ["", "\n", "a", "a\n", "a\nb", "a\r\nb\r\n", "a\rb", "a\r", "a\r\n", "\r\n\r\n",
           "x y\nz", "a\n\nb\n\n", "\n\na", "tail\r"]


def _old_split(text):
    lines = re.findall(r"[^\n]*\n|[^\n]+", text)
    return [ln[:-1].removesuffix("\r") if ln.endswith("\n") else ln for ln in lines]


def _old_mask(text):
    return re.sub(r"<!--.*?-->", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.DOTALL)


def _old_real(text):
    body = strip_comments(text)
    for line in _old_split(body):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        residue = re.sub(r"<[^>\n]+>", "", s)
        residue = re.sub(r"^[-*+]\s*(\[.?\])?\s*", "", residue)
        residue = re.sub(r"^\d+(?:\.\d+)*\s*", "", residue)
        if re.search(r"[A-Za-z0-9]", residue):
            return True
    return False


class ParserEquivalence(unittest.TestCase):
    def test_split_lines_matches_regex_form(self):
        for text in SAMPLES:
            with self.subTest(text=text):
                self.assertEqual(split_lines(text), _old_split(text))

    def test_mask_comments_matches_regex_form(self):
        for text in SAMPLES + ["a <!-- x\r\ny --> b", "<!--\n-->", "<!-- one --> <!-- two\n-->\nend"]:
            with self.subTest(text=text):
                self.assertEqual(mask_comments(text), _old_mask(text))

    def test_has_real_content_matches_old_form(self):
        for text in ["", "# h", "<x>", "<!-- c -->", "- [ ] 1.1", "- none — why", "plain",
                     "Plain <x>", "- <x>", "1.2", "é", "3 apples", "<!-- a --> text", "  \n x"]:
            with self.subTest(text=text):
                self.assertEqual(has_real_content(text), _old_real(text))

    def test_tasks_do_not_need_filled(self):
        text = "## Tasks\n\n- [ ] 1.1 do it\n  - files: `a.py`\n## Outcome\n"
        self.assertEqual(len(parse_tasks(text)), 1)
        lean = parse_sections(text, compute_filled=False)
        full = parse_sections(text)
        self.assertEqual({k: v["lines"] for k, v in lean.items()},
                         {k: v["lines"] for k, v in full.items()})
        self.assertFalse(lean["Tasks"]["filled"])
        self.assertTrue(full["Tasks"]["filled"])

    def test_load_schema_is_memoized(self):
        self.assertIs(schema.load_schema(), schema.load_schema())


if __name__ == "__main__":
    unittest.main()
