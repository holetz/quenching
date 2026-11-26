"""`cq specs list --json` is lean by default, pages like the MCP's `specs_list`, and keeps the
full document-derived shape behind `--full`."""
from __future__ import annotations

import contextlib
import io
import json
import unittest
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands import read as read_module
from quenching.specs.commands.cli import DISPATCH, build_parser
from quenching.specs.commands.output import Emitter

SPECS = 5


def _list(*argv: str) -> dict:
    backend = MemoryBackend()
    for n in range(SPECS):
        backend.create_spec("plans", f"---\ntitle: Spec {n}\ndate: 2026-01-01\n---\n\n"
                            f"# Spec {n}\n\n## Problem\n\nO problema {n}.\n")
    args = build_parser()[0].parse_args(["list", *argv])
    buf = io.StringIO()
    with mock.patch.object(read_module, "open_backend", lambda _root: (backend, {})), \
            contextlib.redirect_stdout(buf):
        DISPATCH["list"](args, "/nowhere", Emitter())
    return json.loads(buf.getvalue())


class ListJsonShape(unittest.TestCase):
    def test_json_is_lean_by_default(self):
        payload = _list("--json")
        self.assertTrue(payload["lean"])
        self.assertNotIn("stage", payload["specs"][0])
        self.assertNotIn("returned", payload)

    def test_full_restores_the_document_derived_shape(self):
        payload = _list("--json", "--full")
        self.assertNotIn("lean", payload)
        self.assertIn("stage", payload["specs"][0])
        self.assertIn("tasks", payload["specs"][0])


class ListJsonPaging(unittest.TestCase):
    def test_limit_and_offset_window_with_the_mcp_keys(self):
        payload = _list("--json", "--limit", "2", "--offset", "1")
        self.assertEqual(SPECS, payload["count"])
        self.assertEqual(2, len(payload["specs"]))
        self.assertEqual((2, 1, 3), (payload["returned"], payload["offset"],
                                     payload["nextOffset"]))

    def test_last_page_has_no_next_offset(self):
        payload = _list("--json", "--limit", "10", "--offset", "3")
        self.assertEqual(2, payload["returned"])
        self.assertIsNone(payload["nextOffset"])

    def test_paging_also_cuts_the_full_shape(self):
        payload = _list("--json", "--full", "--limit", "2")
        self.assertEqual(2, len(payload["specs"]))
        self.assertEqual(2, payload["nextOffset"])
        self.assertIn("stage", payload["specs"][0])

    def test_limit_outside_the_mcp_bounds_is_refused(self):
        for bad in ("0", "201", "x"):
            with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
                build_parser()[0].parse_args(["list", "--limit", bad])


if __name__ == "__main__":
    unittest.main()
