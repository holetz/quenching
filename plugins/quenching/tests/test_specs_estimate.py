"""Reading estimates retain repetition boundaries, coverage gaps and budget uncertainty."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import _paths  # noqa: F401
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands.cli import build_parser
from quenching.specs.commands.estimate import EXECUTE_BODY, cmd_estimate, estimate_build
from quenching.specs.commands.output import Emitter


class DeclaredReading(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.preamble = self.root / "execute.md"
        self.preamble.write_bytes(b"p" * 20)
        (self.root / "a.py").write_bytes(b"a" * 400)
        standard = self.root / "docs/standards/rule.md"
        standard.parent.mkdir(parents=True)
        standard.write_bytes(b"s" * 80)

    def info(self, tasks, impact=""):
        backend = MemoryBackend()
        backend.create_spec("plans", "---\ntitle: Estimate\ndate: 2026-10-14\n---\n"
                            f"\n## Impact\n{impact}\n\n## Tasks\n{tasks}\n")
        return backend.read_spec(1)[0]

    def estimate(self, tasks, impact="", **kwargs):
        return estimate_build(self.info(tasks, impact), self.root, preamble=self.preamble, **kwargs)

    def test_deduplicates_in_a_section_but_counts_each_new_section(self):
        one = self.estimate("### 1. One\n- [ ] 1.1 First\n      files: a.py\n")
        many = self.estimate("### 1. One\n- [ ] 1.1 First\n      files: a.py, ./a.py\n"
                             "- [ ] 1.2 Second\n      files: a.py\n"
                             "### 2. Two\n- [ ] 2.1 Third\n      files: a.py\n")
        self.assertEqual(2, len(many["sections"]))
        self.assertEqual([1, 1], [len(s["files"]) for s in many["sections"]])
        self.assertEqual([2, 1], [s["taskCount"] for s in many["sections"]])
        self.assertEqual(many["maxSectionTokens"] * 2, many["totalReadTokens"])
        self.assertGreater(many["maxSectionTokens"], one["maxSectionTokens"])

    def test_charges_each_declared_impact_standard_and_no_other_section_path(self):
        result = self.estimate("- [ ] 1.1 Task\n      files: a.py\n",
                               "- /docs/standards/rule.md §Only a slice\n"
                               "- /docs/standards/rule.md\n"
                               "<!-- /docs/standards/hidden.md -->")
        self.assertEqual(["/docs/standards/rule.md"], result["standards"])
        self.assertEqual(["a.py", "docs/standards/rule.md"],
                         [r["path"] for r in result["sections"][0]["files"]])
        self.assertTrue(result["complete"])

    def test_missing_new_files_and_undeclared_tasks_are_never_free_evidence(self):
        result = self.estimate("- [ ] 1.1 Task\n      files: missing.py (new)\n- [ ] 1.2 No files\n")
        row = result["sections"][0]
        self.assertFalse(result["complete"])
        self.assertEqual(2, len(row["unresolved"]))
        self.assertIsNone(row["files"][0]["bytes"])
        self.assertGreater(row["estimatedTokens"], 0)

    def test_empty_spec_and_unavailable_preamble_are_incomplete(self):
        self.assertFalse(self.estimate("- none — no tasks")["complete"])
        self.preamble.unlink()
        result = self.estimate("- [ ] 1.1 Task\n      files: a.py\n")
        self.assertFalse(result["complete"])
        self.assertFalse(result["preamble"]["available"])

    def test_escape_absolute_path_directory_annotation_and_symlink_are_unresolved(self):
        (self.root / "escape").symlink_to(self.root.parent, target_is_directory=True)
        result = self.estimate("- [ ] 1.1 Task\n      files: ../outside, /absolute, escape/outside, "
                               "docs, a.py (comment)\n")
        self.assertEqual(5, len(result["sections"][0]["unresolved"]))
        self.assertFalse(result["complete"])

    def test_unicode_size_uses_utf8_bytes_and_rounds_up(self):
        (self.root / "a.py").write_text("ééé", encoding="utf-8")
        result = self.estimate("- [ ] 1.1 Task\n      files: a.py\n")
        self.assertEqual(6, result["sections"][0]["files"][0]["bytes"])
        row = result["sections"][0]
        self.assertEqual((row["bytes"] + 3) // 4, row["estimatedTokens"])

    def test_budget_boundary_is_a_known_reading_signal_never_a_fit_verdict(self):
        task = "- [ ] 1.1 Task\n      files: a.py\n"
        count = self.estimate(task)["maxSectionTokens"]
        self.assertFalse(self.estimate(task, budget=count)["overBudget"])
        self.assertTrue(self.estimate(task, budget=count - 1)["overBudget"])
        result = self.estimate(task)
        self.assertEqual(100000, result["workerBudgetTokens"])
        self.assertNotIn("fits", result)
        self.assertIn("never proves", result["uncertainty"])
        self.assertIn("iteration count", result["excluded"])

    def test_task_states_do_not_change_the_original_loading_estimate(self):
        open_task = self.estimate("- [ ] 1.1 Task\n      files: a.py\n")
        done_task = self.estimate("- [x] 1.1 Task\n      files: a.py\n")
        self.assertEqual(open_task["maxSectionTokens"], done_task["maxSectionTokens"])


class EstimatorCommand(unittest.TestCase):
    def test_default_preamble_is_the_shipped_execute_body(self):
        shipped = Path(__file__).resolve().parents[1] / "commands/specs/execute.md"
        self.assertEqual(shipped, EXECUTE_BODY)
        self.assertTrue(EXECUTE_BODY.is_file())
        backend = MemoryBackend()
        backend.create_spec("plans", "---\ntitle: Estimate\ndate: 2026-10-14\n---\n"
                            "## Tasks\n- [ ] 1.1 Task\n      files: commands/specs/execute.md\n")
        result = estimate_build(backend.read_spec(1)[0], Path(__file__).resolve().parents[1])
        self.assertTrue(result["preamble"]["available"])
        self.assertEqual(shipped.stat().st_size, result["preamble"]["bytes"])
        self.assertTrue(result["complete"])

    def test_cli_accepts_both_identity_forms_and_explicit_budget(self):
        parser, _ = build_parser()
        self.assertEqual("42", parser.parse_args(["estimate", "42"]).spec_id)
        args = parser.parse_args(["estimate", "--spec", "42", "--worker-budget", "50000"])
        self.assertEqual(("42", 50000), (args.spec, args.worker_budget))

    def run_cmd(self, backend, budget=100000, json_output=True):
        args = argparse.Namespace(spec=1, worker_budget=budget, json=json_output)
        stream = io.StringIO()
        with patch("quenching.specs.commands.estimate.open_backend", return_value=(backend, {})), \
                contextlib.redirect_stdout(stream):
            code = cmd_estimate(args, ".", Emitter())
        return code, stream.getvalue()

    def test_reads_provider_document_and_never_writes_it(self):
        backend = MemoryBackend()
        backend.create_spec("plans", "---\ntitle: Estimate\ndate: 2026-10-14\n---\n## Problem\nx\n")
        original = dict(backend.docs)
        code, body = self.run_cmd(backend)
        self.assertEqual(0, code)
        self.assertEqual("estimated-declared-reading", json.loads(body)["kind"])
        self.assertEqual(original, backend.docs)
        self.assertIn("NOT a build-fit verdict", self.run_cmd(backend, json_output=False)[1])

    def test_refuses_invalid_budget_and_propagates_provider_refusal(self):
        code, body = self.run_cmd(MemoryBackend(), budget=0)
        self.assertEqual(2, code)
        self.assertEqual("sp-bad-worker-budget", json.loads(body)["code"])
        code, body = self.run_cmd(MemoryBackend())
        self.assertEqual(1, code)
        self.assertEqual("sp-unknown-id", json.loads(body)["code"])
        args = argparse.Namespace(spec=1, worker_budget=100000, json=True)
        with patch("quenching.specs.commands.estimate.open_backend",
                   return_value=(None, {"code": "provider-refusal", "exit": 2, "message": "no"})), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(2, cmd_estimate(args, ".", Emitter()))


if __name__ == "__main__":
    unittest.main()
