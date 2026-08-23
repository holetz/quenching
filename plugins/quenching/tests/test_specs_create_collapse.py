"""The collapsed capture — `cq specs new` absorbing `summary`/`tags`/`priority.complexity`
and N sections into the ONE `backend.create_spec` call, instead of up to eight invocations.

Every refusal below must write nothing at all: a rejected capture leaves no spec behind for
`backend.list_specs()` to find, which is what proves the validation ran BEFORE `create_spec`
and not around it."""
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands import create as create_module
from quenching.specs.commands.create import cmd_new
from quenching.specs.commands.output import Emitter
from quenching.specs.schema import capture_form


class _Args:
    """`cmd_new`'s argparse namespace, with the defaults the parser gives it."""

    def __init__(self, **kw):
        self.json = True
        self.name = "gamma-lever"
        self.title = None
        self.verification = None
        self.subject = None
        self.type = None
        self.tags = None
        self.complexity = None
        self.__dict__.update(kw)


class _Workspace(unittest.TestCase):
    """An in-memory external-provider fixture for the one-call capture path."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = self.tmp.name
        self.backend = MemoryBackend()
        self._open = mock.patch.object(
            create_module, "open_backend", lambda _root: (self.backend, {}))
        self._config = mock.patch.object(
            create_module, "load_config",
            return_value={"backend": "github", "subjects": {},
                          "azurePlacement": {}, "workItemTypes": {}})
        self._open.start()
        self._config.start()
        self.addCleanup(self._open.stop)
        self.addCleanup(self._config.stop)

    def run_new(self, stdin=None, **kw):
        buf, stream = io.StringIO(), io.StringIO(stdin or "")
        stream.isatty = lambda: stdin is None
        with mock.patch("sys.stdin", stream), redirect_stdout(buf):
            code = cmd_new(_Args(**kw), self.root, Emitter())
        return code, json.loads(buf.getvalue())

    def read_back(self, spec_id=None):
        # `new` reports a locator, never an ID a caller could pass back — the store allocated
        # it, so the store is asked which one it just made.
        info, err = self.backend.read_spec(max(self.backend.docs)
                                           if spec_id is None else spec_id)
        self.assertFalse(err, err)
        return info

    def list_ids(self):
        return [s["id"] for s in self.backend.list_specs()]


class TheCollapsedCapture(_Workspace):
    def test_one_call_writes_frontmatter_tags_priority_and_n_sections(self):
        code, obj = self.run_new(
            tags="alpha,beta", complexity="high",
            stdin="## Problem\n\nO problema.\n")
        self.assertEqual(code, 0, obj)
        self.assertEqual(obj["ok"], True)

        info = self.read_back()
        fm = info["frontmatter"]
        # `summary:` is retired from the contract — `optional-payload-fields.md` §Retired
        # fields stay retired. The title carries the short description now.
        self.assertNotIn("summary", fm)
        self.assertEqual(fm.get("title"), "gamma-lever")
        self.assertEqual(fm.get("tags"), ["alpha", "beta"])
        self.assertEqual(fm.get("priority"), {"complexity": "high"})
        self.assertEqual(info["sections"]["Problem"]["body"].strip(), "O problema.")
        self.assertNotIn("Overview", info["sections"])

    def test_the_subject_s_fixed_tags_are_folded_into_an_explicit_tags_list(self):
        # No declared `subjects` in this bare workspace, so nothing to fold in here beyond
        # what was typed — this proves `--tags` alone still lands as the whole list, exactly
        # as `cq specs tags` renders one: split and stripped, never deduplicated.
        code, obj = self.run_new(tags="alpha, beta")
        self.assertEqual(code, 0, obj)
        info = self.read_back()
        self.assertEqual(info["frontmatter"].get("tags"), ["alpha", "beta"])

    def test_a_non_canonical_heading_in_the_stream_refuses_and_creates_nothing(self):
        code, obj = self.run_new(stdin="## Nao Canonico\n\nX\n")
        self.assertEqual(code, 2)
        self.assertEqual(obj["code"], "sp-stray-heading")
        self.assertEqual(self.list_ids(), [])

    def test_an_unresolved_heading_after_a_self_describing_stream_refuses_and_creates_nothing(self):
        code, obj = self.run_new(
            stdin="## Problem\n\nO problema.\n\n## Nao Canonico\n\nX\n")
        self.assertEqual(code, 2)
        self.assertEqual(obj["code"], "sp-stray-heading")
        self.assertEqual(obj["unresolvedBlocks"], [2])
        self.assertEqual(self.list_ids(), [])

    def test_a_repeated_heading_in_the_stream_refuses_and_creates_nothing(self):
        code, obj = self.run_new(
            stdin="## Problem\n\nA\n\n## Problem\n\nB\n")
        self.assertEqual(code, 2)
        self.assertEqual(obj["code"], "sp-write-duplicate-heading")
        self.assertEqual(self.list_ids(), [])

    def test_an_invalid_complexity_refuses_before_create_spec(self):
        code, obj = self.run_new(complexity="bogus")
        self.assertEqual(code, 2)
        self.assertEqual(obj["code"], "sp-bad-complexity")
        self.assertEqual(self.list_ids(), [])

    def test_empty_stdin_is_a_non_regression_over_todays_bare_capture(self):
        code, obj = self.run_new()
        self.assertEqual(code, 0, obj)
        info = self.read_back()
        expected = (capture_form()
                    .replace("<TITLE>", "gamma-lever")
                    .replace("<DATE>", info["date"])
                    .replace("<VERIFICATION>", "per-section"))
        self.assertEqual(info["text"], expected)
        self.assertNotIn("summary", info["frontmatter"])
        self.assertNotIn("tags", info["frontmatter"])
        self.assertNotIn("priority", info["frontmatter"])


if __name__ == "__main__":
    unittest.main()
