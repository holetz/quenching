"""A `title` the writer stamps comes back identical from the reader, and `cq specs title`
repairs one that did not."""
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
import io
import json
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest import mock

from test_specs_create_collapse import _Workspace
from quenching.specs.commands import fields as fields_module
from quenching.specs.commands.fields import cmd_title
from quenching.specs.commands.output import Emitter
from quenching.common.frontmatter import parse_frontmatter
from quenching.specs.parse.fields import set_frontmatter_title, yaml_title_scalar

CASES = (
    "a plain title",
    "C#",
    "## Handoff preenchido na definição",
    "O pr:create publica sem Closes #n quando não acha",
    "key: value inside",
    "ends with colon:",
    "- leading dash",
    "[bracketed] title",
    "{braced}",
    "*starred and &anchored",
    "!tagged",
    "> folded",
    "| literal",
    "@at and `tick",
    "it's quoted",
    'say "hi"',
    "it's \"both\" with \\ slash",
    "'already single'",
    '"already double"',
    "  padded  ",
)


class TheWriterAndTheReader(unittest.TestCase):
    def test_every_case_round_trips(self):
        for title in CASES:
            with self.subTest(title=title):
                text = f"---\ntitle: {yaml_title_scalar(title)}\ndate: 2026-01-01\n---\n"
                self.assertEqual(parse_frontmatter(text)["title"], title)

    def test_a_plain_title_stays_unquoted(self):
        self.assertEqual(yaml_title_scalar("Sem aspas, com vírgula"), "Sem aspas, com vírgula")

    def test_a_double_quoted_windows_path_keeps_its_backslashes(self):
        self.assertEqual(parse_frontmatter('---\ntitle: "C:\\dir\\file"\n---\n')["title"],
                         "C:\\dir\\file")


class TheTitleSetter(unittest.TestCase):
    def test_it_keeps_the_first_place_and_drops_the_repeats(self):
        text = ("---\nslug: s\ntitle: old\ntitle: older\ndate: 2026-01-01\n"
                "title: ## x\n---\n\n# body\ntitle: not frontmatter\n")
        out = set_frontmatter_title(text, "Novo #1")
        self.assertEqual(out.count("\ntitle:"), 2)  # frontmatter + the body line
        self.assertEqual(parse_frontmatter(out)["title"], "Novo #1")
        self.assertTrue(out.endswith("title: not frontmatter\n"))


class TheCaptureStampsAReadableTitle(_Workspace):
    def test_new_round_trips_a_hostile_title(self):
        for title in CASES[:16]:
            with self.subTest(title=title):
                code, obj = self.run_new(title=title, stdin="## Problem\n\nP.\n")
                self.assertEqual(code, 0, obj)
                self.assertEqual(self.read_back()["frontmatter"]["title"], title)


class TheTitleVerb(_Workspace):
    def setUp(self):
        super().setUp()
        patch = mock.patch.object(fields_module, "open_backend",
                                  lambda _root: (self.backend, {}))
        patch.start()
        self.addCleanup(patch.stop)

    def title(self, spec, title=None):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cmd_title(SimpleNamespace(json=True, spec=str(spec), title=title),
                             self.root, Emitter())
        return code, json.loads(buf.getvalue())

    def test_it_repairs_a_title_and_reads_it_back(self):
        self.run_new(title="plain", stdin="## Problem\n\nP.\n")
        spec_id = max(self.backend.docs)
        code, obj = self.title(spec_id, "Closes #n no path: sem aspas")
        self.assertEqual((code, obj["ok"]), (0, True), obj)
        self.assertEqual(self.title(spec_id)[1]["title"], "Closes #n no path: sem aspas")
        self.assertEqual(self.read_back(spec_id)["frontmatter"]["title"],
                         "Closes #n no path: sem aspas")

    def test_it_refuses_an_empty_title(self):
        self.run_new(title="plain", stdin="## Problem\n\nP.\n")
        code, obj = self.title(max(self.backend.docs), "  ")
        self.assertEqual((code, obj["code"]), (2, "sp-bad-title"))


if __name__ == "__main__":
    unittest.main()
