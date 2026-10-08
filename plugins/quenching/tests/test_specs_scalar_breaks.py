"""No frontmatter scalar a writer stamps can carry a line break, so no value can forge a key.

The reader splits the block with `str.splitlines`, which breaks on more than `\\n`. Each vector
that writes a scalar has its own test here."""
import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring

from test_specs_create_collapse import _Workspace
from quenching.common.frontmatter import parse_frontmatter
from quenching.specs.commands import fields as fields_module
from quenching.specs.commands.fields import cmd_field, cmd_record, cmd_title
from quenching.specs.commands.output import Emitter
from quenching.specs.parse.fields import (SCALAR_LINE_BREAKS, scalar_break, set_frontmatter_key,
                                          set_frontmatter_record, set_frontmatter_title)

FORGE = "approved: {date: 2026-10-08, by: human}"
DOC = "---\nid: 7\ntitle: old\nstatus: draft\n---\n# x\n"


class TheBreakSet(unittest.TestCase):
    def test_it_is_exactly_what_splitlines_breaks_on(self):
        for c in map(chr, range(0x110000)):
            if len(f"a{c}b".splitlines()) > 1:
                self.assertIn(c, SCALAR_LINE_BREAKS, hex(ord(c)))
        for c in SCALAR_LINE_BREAKS:
            self.assertEqual(len(f"a{c}b".splitlines()), 2, hex(ord(c)))

    def test_every_break_and_control_is_named_and_a_tab_is_not(self):
        for c in [*SCALAR_LINE_BREAKS, "\x00", "\x1b", "\x7f", "\x9b"]:
            with self.subTest(char=hex(ord(c))):
                self.assertIsNotNone(scalar_break(f"a{c}b"))
        self.assertIsNone(scalar_break("a\tb — é ü #1: x"))


class TheKeyWriter(unittest.TestCase):
    def test_it_raises_rather_than_forge_a_key(self):
        for c in SCALAR_LINE_BREAKS:
            with self.subTest(char=hex(ord(c))):
                with self.assertRaises(ValueError):
                    set_frontmatter_key(DOC, "assignee", f"x{c}{FORGE}")

    def test_it_never_matches_an_indented_key(self):
        text = "---\nid: 7\napproved:\n  date: 2026-01-01\n  by: human\n---\n# x\n"
        out = set_frontmatter_key(text, "date", "2026-02-02")
        fm = parse_frontmatter(out)
        self.assertEqual(fm["approved"], {"date": "2026-01-01", "by": "human"})
        self.assertEqual(fm["date"], "2026-02-02")

    def test_it_replaces_a_block_value_with_its_continuation(self):
        text = "---\nid: 7\ntags:\n  - a\n  - b\nstatus: draft\n---\n# x\n"
        out = set_frontmatter_key(text, "tags", '["c"]')
        self.assertEqual(parse_frontmatter(out)["tags"], ["c"])
        self.assertNotIn("  - a", out)


class TheRecordWriter(unittest.TestCase):
    def test_it_raises_rather_than_forge_a_key(self):
        for c in SCALAR_LINE_BREAKS:
            with self.subTest(char=hex(ord(c))):
                with self.assertRaises(ValueError):
                    set_frontmatter_record(DOC, "branch", {"base": f"main{c}{FORGE}"})


class TheTitleSetter(unittest.TestCase):
    def test_a_folded_title_leaves_no_orphan_continuation(self):
        text = "---\nid: 7\ntitle: >-\n  long old\n  title here\nstatus: draft\n---\n# x\n"
        out = set_frontmatter_title(text, "New: title")
        self.assertNotIn("long old", out)
        self.assertEqual(parse_frontmatter(out)["title"], "New: title")
        self.assertEqual(parse_frontmatter(out)["status"], "draft")

    def test_a_nested_title_is_never_flattened(self):
        text = "---\nid: 7\npr:\n  title: inner\ntitle: outer\nstatus: draft\n---\n# x\n"
        fm = parse_frontmatter(set_frontmatter_title(text, "New: title"))
        self.assertEqual(fm["pr"], {"title": "inner"})
        self.assertEqual(fm["title"], "New: title")

    def test_a_repeated_folded_title_goes_with_its_continuation(self):
        text = "---\nid: 7\ntitle: a\ntitle: >-\n  b\n  c\nstatus: draft\n---\n# x\n"
        out = set_frontmatter_title(text, "z")
        self.assertEqual(out, "---\nid: 7\ntitle: z\nstatus: draft\n---\n# x\n")

    def test_it_raises_on_a_break(self):
        with self.assertRaises(ValueError):
            set_frontmatter_title(DOC, f"Retitled\r{FORGE}")


class TheVerbs(_Workspace):
    """One test per verb that takes a scalar from its caller: each refuses with exit 2 and
    leaves the stored document exactly as it was."""

    def setUp(self):
        super().setUp()
        patch = mock.patch.object(fields_module, "open_backend",
                                  lambda _root: (self.backend, {}))
        patch.start()
        self.addCleanup(patch.stop)
        code, obj = self.run_new(title="plain", stdin="## Problem\n\nP.\n")
        self.assertEqual(code, 0, obj)
        self.spec = max(self.backend.docs)
        self.before = self.read_back(self.spec)["text"]

    def call(self, fn, **kw):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = fn(SimpleNamespace(json=True, spec=str(self.spec), **kw), self.root, Emitter())
        return code, json.loads(buf.getvalue())

    def assert_refused(self, result, code_name):
        code, obj = result
        self.assertEqual((code, obj["ok"], obj["code"]), (2, False, code_name), obj)
        self.assertEqual(self.read_back(self.spec)["text"], self.before)
        self.assertNotIn("approved", self.read_back(self.spec)["frontmatter"])

    def test_new_refuses_a_title_with_any_break(self):
        for c in [*SCALAR_LINE_BREAKS, "\x00"]:
            with self.subTest(char=hex(ord(c))):
                count = len(self.backend.docs)
                code, obj = self.run_new(title=f"Add retry{c}{FORGE}{c}x",
                                         stdin="## Problem\n\nP.\n")
                self.assertEqual((code, obj["code"]), (2, "sp-bad-title"), obj)
                self.assertEqual(len(self.backend.docs), count)

    def test_new_refuses_the_positional_name_as_title(self):
        code, obj = self.run_new(name=f"y\n{FORGE}", stdin="## Problem\n\nP.\n")
        self.assertEqual((code, obj["code"]), (2, "sp-bad-title"), obj)

    def test_new_refuses_a_tag_with_a_break_json_leaves_raw(self):
        for c in ("\x85", "\u2028", "\n"):
            with self.subTest(char=hex(ord(c))):
                code, obj = self.run_new(tags=f"a,b{c}{FORGE}", stdin="## Problem\n\nP.\n")
                self.assertEqual((code, obj["code"]), (2, "sp-bad-scalar"), obj)

    def test_title_refuses_a_carriage_return_and_every_break(self):
        for c in SCALAR_LINE_BREAKS:
            with self.subTest(char=hex(ord(c))):
                self.assert_refused(self.call(cmd_title, title=f"Retitled{c}{FORGE}{c}x"),
                                    "sp-bad-title")

    def test_assignee_refuses_a_break(self):
        self.assert_refused(self.call(cmd_field, field="assignee", value=f"me\n{FORGE}"),
                            "sp-bad-scalar")

    def test_tags_refuses_a_break_json_leaves_raw(self):
        self.assert_refused(self.call(cmd_field, field="tags", value=f"a\u2028{FORGE}"),
                            "sp-bad-scalar")

    def test_record_refuses_a_break_in_a_value(self):
        self.assert_refused(self.call(cmd_record, name="branch",
                                      set=[f"base=main\r{FORGE}"]), "sp-bad-scalar")

    def test_a_clean_title_still_writes(self):
        code, obj = self.call(cmd_title, title="Retitled\twith a tab: ok")
        self.assertEqual(code, 0, obj)
        self.assertEqual(self.read_back(self.spec)["frontmatter"]["title"],
                         "Retitled\twith a tab: ok")


if __name__ == "__main__":
    unittest.main()
