"""The `run` record: the spec-runner's last step, a short scalar record that merges cleanly."""
import argparse
import contextlib
import io
import json
import pathlib
import sys
import unittest
from unittest.mock import patch

try:
    import _paths  # noqa: F401  — must precede the `quenching` import
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands.fields import cmd_record, record_field_value_error
from quenching.specs.commands.output import Emitter
from quenching.specs.parse.records import spec_records
from quenching.specs.schema import load_schema


class RunRecord(unittest.TestCase):
    def setUp(self):
        self.backend = MemoryBackend()
        self.backend.create_spec("plans", "---\ntitle: Run\ndate: 2026-10-16\n"
                                 "priority: {complexity: medium}\n---\n## Problem\nx\n")

    def write(self, values):
        args = argparse.Namespace(spec=1, name="run", set=values, json=True)
        stream = io.StringIO()
        with patch("quenching.specs.commands.fields.open_backend", return_value=(self.backend, {})), \
                contextlib.redirect_stdout(stream):
            code = cmd_record(args, ".", Emitter())
        return code, json.loads(stream.getvalue())

    def test_declared_optional_with_closed_state_and_verifier(self):
        schema = load_schema()
        self.assertIn("run", schema["frontmatter"]["optional"])
        rec = schema["frontmatter"]["records"]["run"]
        self.assertEqual("spec-runner", rec["writtenBy"])
        self.assertEqual(["state", "verifier", "by", "date"], rec["fields"])
        for state in ("done", "continue", "blocked", "failed"):
            self.assertIsNone(record_field_value_error(rec, "state", state))
        for verdict in ("pass", "fail", "not-run"):
            self.assertIsNone(record_field_value_error(rec, "verifier", verdict))
        self.assertIsNotNone(record_field_value_error(rec, "state", "running"))
        self.assertIsNotNone(record_field_value_error(rec, "verifier", "maybe"))

    def test_write_merges_without_losing_fields_or_other_records(self):
        self.assertEqual(0, self.write(["state=continue", "verifier=not-run", "date=2026-10-17"])[0])
        code, payload = self.write(["state=done", "verifier=pass", "by=verifier"])
        self.assertEqual(0, code)
        info = self.backend.read_spec(1)[0]
        self.assertEqual({"state": "done", "verifier": "pass", "by": "verifier", "date": "2026-10-17"},
                         spec_records(info["frontmatter"])["run"])
        self.assertEqual("medium", info["frontmatter"]["priority"]["complexity"])

    def test_an_invalid_state_is_refused_and_writes_nothing(self):
        code, _ = self.write(["state=running"])
        self.assertNotEqual(0, code)
        self.assertIsNone(spec_records(self.backend.read_spec(1)[0]["frontmatter"])["run"])

    def test_omitting_verifier_in_a_later_stamp_keeps_the_stored_verdict(self):
        self.write(["state=continue", "verifier=pass", "by=verifier", "date=2026-10-17"])
        code, _ = self.write(["state=done", "date=2026-10-18"])
        self.assertEqual(0, code)
        self.assertEqual({"state": "done", "verifier": "pass", "by": "verifier",
                          "date": "2026-10-18"},
                         spec_records(self.backend.read_spec(1)[0]["frontmatter"])["run"])

    def test_a_verdict_without_the_verifier_attestation_is_refused_and_writes_nothing(self):
        for verdict in ("pass", "fail"):
            code, payload = self.write(["state=done", f"verifier={verdict}", "date=2026-10-17"])
            self.assertEqual(2, code)
            self.assertEqual("sp-run-verdict-unattested", payload["code"])
        self.assertIsNone(spec_records(self.backend.read_spec(1)[0]["frontmatter"])["run"])

    def test_not_run_needs_no_attestation_and_drops_a_stored_one(self):
        self.write(["state=continue", "verifier=pass", "by=verifier", "date=2026-10-17"])
        code, _ = self.write(["state=done", "verifier=not-run"])
        self.assertEqual(0, code)
        run = spec_records(self.backend.read_spec(1)[0]["frontmatter"])["run"]
        self.assertEqual("not-run", run["verifier"])
        self.assertNotIn("by", run)

    def test_spec_runner_contract_does_not_derive_verifier_from_the_gate(self):
        path = pathlib.Path(__file__).resolve().parents[1] / "agents" / "spec-runner.md"
        text = path.read_text()
        self.assertIn("NEVER the source of `verifier`", text)
        self.assertIn("OMIT `--set verifier=`", text)
        self.assertNotIn("verdict of the repository gate or verifier", text)
        self.assertIn("`--set by=verifier`", text)
        orchestrator = (path.parent / "orchestrator.md").read_text()
        self.assertIn("--set verifier=<pass|fail> --set by=verifier", orchestrator)
        steward = (path.parent / "git-steward.md").read_text()
        self.assertIn("cq git pr merge --url <url> --wait 90 --json`, plus `--spec <id>`", steward)


if __name__ == "__main__":
    unittest.main()
