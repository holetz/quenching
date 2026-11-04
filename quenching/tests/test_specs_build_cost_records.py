"""Observed cost remains a schema-backed, provenance-carrying scalar record across backends."""
import argparse
import contextlib
import io
import json
import unittest
from unittest.mock import patch

import _paths  # noqa: F401
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands.fields import cmd_record, record_field_value_error
from quenching.specs.commands.output import Emitter
from quenching.specs.parse.records import spec_records
from quenching.specs.schema import load_schema


class BuildCostRecord(unittest.TestCase):
    def setUp(self):
        self.backend = MemoryBackend()
        self.backend.create_spec("plans", "---\ntitle: Cost\ndate: 2026-10-14\n"
                                 "priority: {complexity: medium}\n---\n## Problem\nx\n")

    def write(self, values):
        args = argparse.Namespace(spec=1, name="buildCost", set=values, json=True)
        stream = io.StringIO()
        with patch("quenching.specs.commands.fields.open_backend", return_value=(self.backend, {})), \
                contextlib.redirect_stdout(stream):
            code = cmd_record(args, ".", Emitter())
        return code, json.loads(stream.getvalue())

    def test_declares_optional_conclude_owned_record_with_closed_status(self):
        schema = load_schema()
        self.assertIn("buildCost", schema["frontmatter"]["optional"])
        rec = schema["frontmatter"]["records"]["buildCost"]
        self.assertEqual("conclude", rec["writtenBy"])
        self.assertIsNone(record_field_value_error(rec, "status", "measured"))
        self.assertIsNone(record_field_value_error(rec, "status", "unavailable"))
        self.assertIsNotNone(record_field_value_error(rec, "status", "estimated"))

    def test_per_model_measurements_round_trip_through_generic_backend_writer(self):
        observed = json.dumps([
            {"model": "sonnet", "requests": 2, "input": 100, "cacheRead": 200,
             "cacheWrite": 50, "output": 40, "maxRequestExposureTokens": 250},
            {"model": "opus", "requests": 1, "input": 50, "cacheRead": 0,
             "cacheWrite": 0, "output": 20, "maxRequestExposureTokens": 50},
        ], separators=(",", ":"))
        source = "Claude Code; build-only scope /provided/subagents; agents a,b; exit 0"
        code, payload = self.write(["status=measured", "date=2026-10-14", "source=" + source,
                                    "measurements=" + observed, "reason="])
        self.assertEqual(0, code)
        info = self.backend.read_spec(1)[0]
        stored = spec_records(info["frontmatter"])["buildCost"]
        self.assertEqual(source, stored["source"])
        self.assertEqual(observed, stored["measurements"])
        self.assertEqual(2, len(json.loads(stored["measurements"])))
        self.assertEqual(stored, payload["value"])
        self.assertEqual("medium", info["frontmatter"]["priority"]["complexity"])

    def test_unavailable_has_reason_and_no_invented_numeric_measurement(self):
        code, _ = self.write(["status=unavailable", "date=2026-10-14", "source=Codex",
                              "measurements=", "reason=Native telemetry was not measured"])
        self.assertEqual(0, code)
        info = self.backend.read_spec(1)[0]
        stored = spec_records(info["frontmatter"])["buildCost"]
        self.assertEqual("unavailable", stored["status"])
        self.assertEqual("", stored["measurements"])
        self.assertIn("not measured", stored["reason"])

    def test_unknown_estimated_status_refuses_without_mutating_document(self):
        original = dict(self.backend.docs)
        code, payload = self.write(["status=estimated"])
        self.assertEqual(2, code)
        self.assertEqual("sp-invalid-record-value", payload["code"])
        self.assertEqual(original, self.backend.docs)


if __name__ == "__main__":
    unittest.main()
