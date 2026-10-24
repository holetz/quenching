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
from quenching.specs.commands.estimate import (EXECUTE_BODY, EXECUTOR_FIXED_TOKENS,
                                               SMALL_TIER_CEILING, cmd_estimate, estimate_build,
                                               estimate_task)
from quenching.specs.commands.output import Emitter


class DeclaredReading(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.preamble = self.root / "execute.md"
        self.preamble.write_bytes(b"p" * 20)
        (self.root / "a.py").write_bytes(b"a" * 400)
        standard = self.root / "docs/standards/agents/communication.md"
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
                               "- /docs/standards/agents/communication.md §Only a slice\n"
                               "- /docs/standards/agents/communication.md\n"
                               "<!-- /docs/standards/agents/ephemeral-writes.md -->")
        self.assertEqual(["/docs/standards/agents/communication.md"], result["standards"])
        self.assertEqual(["a.py", "docs/standards/agents/communication.md"],
                         [r["path"] for r in result["sections"][0]["files"]])
        self.assertTrue(result["complete"])

    def test_missing_new_files_and_undeclared_tasks_are_never_free_evidence(self):
        result = self.estimate("- [ ] 1.1 Task\n      files: missing.py (new)\n- [ ] 1.2 No files\n")
        row = result["sections"][0]
        self.assertFalse(result["complete"])
        self.assertEqual(2, len(row["unresolved"]))
        self.assertIsNone(row["files"][0]["bytes"])
        self.assertGreater(row["estimatedTokens"], 0)

    def test_generated_mirror_keeps_size_but_adds_no_reading_tokens(self):
        mirror = self.root / "plugins/quenching-specs/big.py"
        mirror.parent.mkdir(parents=True)
        mirror.write_bytes(b"x" * 4000)
        (mirror.parent / ".generated-from.json").write_text("{}")
        task = "- [ ] 1.1 Task\n      files: a.py\n"
        baseline = self.estimate(task)["sections"][0]
        info = self.info(task)
        info["tasks"][0]["files"].append("plugins/quenching-specs/big.py")
        row = estimate_build(info, self.root, preamble=self.preamble)["sections"][0]
        self.assertEqual(baseline["estimatedTokens"], row["estimatedTokens"])
        self.assertEqual(baseline["bytes"], row["bytes"])
        self.assertEqual({"path": "plugins/quenching-specs/big.py", "bytes": 4000,
                          "writeOnly": "generated mirror"}, row["files"][1])
        self.assertEqual([], row["unresolved"])

    def test_missing_generated_mirror_is_not_unresolved(self):
        generated = self.root / "plugins/quenching-specs"
        generated.mkdir(parents=True)
        (generated / ".generated-files.json").write_text("{}")
        for suffix in ("", " (new)"):
            with self.subTest(suffix=suffix):
                row = self.estimate("- [ ] 1.1 Task\n      files: "
                                    f"plugins/quenching-specs/nested/missing.py{suffix}\n")["sections"][0]
                self.assertEqual("generated mirror", row["files"][0]["writeOnly"])
                self.assertIsNone(row["files"][0]["bytes"])
                self.assertEqual([], row["unresolved"])
                self.assertTrue(row["complete"])

    def test_authored_file_under_generated_directory_is_counted(self):
        authored = self.root / "plugins/quenching-specs/big.py"
        authored.parent.mkdir(parents=True)
        authored.write_bytes(b"x" * 4000)
        (authored.parent / ".generated-from.json").write_text("{}")
        manifest = self.root / "plugins/quenching/assets/modules.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({"modules": [{"path": "plugins/quenching-specs",
                                                     "authored": ["big.py"]}]}))
        result = self.estimate("- [ ] 1.1 Task\n      files: plugins/quenching-specs/big.py\n")
        row = result["sections"][0]
        self.assertEqual([{"path": "plugins/quenching-specs/big.py", "bytes": 4000}], row["files"])
        self.assertEqual(20 + result["specBuildBytes"] + 4000, row["bytes"])
        self.assertEqual([], row["unresolved"])

    def test_normal_file_is_counted(self):
        result = self.estimate("- [ ] 1.1 Task\n      files: a.py\n")
        row = result["sections"][0]
        self.assertEqual([{"path": "a.py", "bytes": 400}], row["files"])
        self.assertEqual(20 + result["specBuildBytes"] + 400, row["bytes"])
        self.assertEqual([], row["unresolved"])

    def test_impact_standard_is_counted_even_when_also_declared_under_generated_dir(self):
        (self.root / "docs" / ".generated-from.json").write_text("{}")
        standard = "docs/standards/agents/communication.md"
        result = self.estimate(f"- [ ] 1.1 Task\n      files: {standard}\n", f"- /{standard}\n")
        row = result["sections"][0]
        self.assertEqual([{"path": standard, "bytes": 80}], row["files"])
        self.assertEqual(20 + result["specBuildBytes"] + 80, row["bytes"])

    def test_invalid_module_manifest_does_not_prevent_mirror_detection(self):
        generated = self.root / "plugins/quenching-specs"
        generated.mkdir(parents=True)
        (generated / ".generated-from.json").write_text("{}")
        manifest = self.root / "plugins/quenching/assets/modules.json"
        manifest.parent.mkdir(parents=True)
        for contents in ("{invalid", "[]", '{"modules": null}'):
            with self.subTest(contents=contents):
                manifest.write_text(contents)
                row = self.estimate("- [ ] 1.1 Task\n      files: "
                                    "plugins/quenching-specs/missing.py\n")["sections"][0]
                self.assertEqual("generated mirror", row["files"][0]["writeOnly"])
                self.assertEqual([], row["unresolved"])

    def test_root_marker_and_invalid_paths_do_not_make_mirrors(self):
        (self.root / ".generated-from.json").write_text("{}")
        (self.root / "escape").symlink_to(self.root.parent, target_is_directory=True)
        result = self.estimate("- [ ] 1.1 Task\n      files: a.py, ../outside, /absolute, "
                               "escape/outside, a.py (comment)\n")
        row = result["sections"][0]
        self.assertEqual(4, len(row["unresolved"]))
        self.assertTrue(all("writeOnly" not in file for file in row["files"]))

    def test_nearest_generated_directory_controls_authored_exception(self):
        nested = self.root / "plugins/quenching-specs/nested"
        nested.mkdir(parents=True)
        (nested / ".generated-files.json").write_text("{}")
        (nested.parent / ".generated-from.json").write_text("{}")
        (nested / "big.py").write_bytes(b"x" * 4000)
        manifest = self.root / "plugins/quenching/assets/modules.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({"modules": [{"path": "plugins/quenching-specs",
                                                     "authored": ["nested/big.py"]}]}))
        row = self.estimate("- [ ] 1.1 Task\n      files: "
                            "plugins/quenching-specs/nested/big.py\n")["sections"][0]
        self.assertEqual("generated mirror", row["files"][0]["writeOnly"])

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


class SmallTierProjection(unittest.TestCase):
    setUp = DeclaredReading.setUp
    info = DeclaredReading.info
    VERIFY = "      verify: python3 -m unittest discover -s tests -p test_a.py\n"

    def project(self, tasks, task_id="1.1"):
        return estimate_task(self.info(tasks), task_id, self.root)

    def test_projects_files_and_pattern_with_tokenizer_factor_and_fixed_prompt(self):
        (self.root / "b.py").write_bytes(b"b" * 400)
        row = self.project("- [ ] 1.1 Task\n      files: a.py\n      pattern: b.py\n" + self.VERIFY)
        self.assertEqual(200, row["readTokens"])
        self.assertEqual(260 + EXECUTOR_FIXED_TOKENS, row["projectedTokens"])
        self.assertTrue(row["oracleProtected"])
        self.assertTrue(row["smallTierEligible"])

    def test_oracle_inside_files_or_missing_verify_is_not_protected(self):
        inside = self.project("- [ ] 1.1 Task\n      files: a.py, tests/test_a.py\n" + self.VERIFY)
        self.assertFalse(inside["oracleProtected"])
        self.assertEqual(["tests/test_a.py"], inside["oracleInFiles"])
        self.assertFalse(inside["smallTierEligible"])
        named = self.project("- [ ] 1.1 Task\n      files: a.py, check.sh\n      verify: bash check.sh\n")
        self.assertFalse(named["oracleProtected"])
        bare = self.project("- [ ] 1.1 Task\n      files: a.py\n")
        self.assertFalse(bare["oracleProtected"])
        self.assertIn("no verify: oracle", bare["reasons"])

    def test_docs_writes_and_projection_above_the_ceiling_are_not_eligible(self):
        docs = self.project("- [ ] 1.1 Task\n      files: a.py, docs/standards/agents/communication.md\n"
                            + self.VERIFY)
        self.assertTrue(docs["oracleProtected"])
        self.assertFalse(docs["smallTierEligible"])
        room = SMALL_TIER_CEILING - EXECUTOR_FIXED_TOKENS
        (self.root / "big.py").write_bytes(b"x" * (int(room / 1.3) * 4 + 8))
        big = self.project("- [ ] 1.1 Task\n      files: big.py\n" + self.VERIFY)
        self.assertGreater(big["projectedTokens"], SMALL_TIER_CEILING)
        self.assertTrue(big["oracleProtected"])
        self.assertFalse(big["smallTierEligible"])

    def test_new_file_is_free_but_a_missing_one_blocks_and_unknown_task_is_none(self):
        new = self.project("- [ ] 1.1 Task\n      files: fresh.py (new)\n" + self.VERIFY)
        self.assertTrue(new["smallTierEligible"])
        missing = self.project("- [ ] 1.1 Task\n      files: gone.py\n" + self.VERIFY)
        self.assertFalse(missing["smallTierEligible"])
        self.assertIsNone(self.project("- [ ] 1.1 Task\n      files: a.py\n", "9.9"))


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
        self.assertEqual("2.1", parser.parse_args(["estimate", "42", "--task", "2.1"]).task)

    def run_cmd(self, backend, budget=100000, json_output=True, task=None):
        args = argparse.Namespace(spec=1, worker_budget=budget, json=json_output, task=task)
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

    def test_task_flag_emits_the_projection_and_refuses_an_unknown_task(self):
        backend = MemoryBackend()
        backend.create_spec("plans", "---\ntitle: Estimate\ndate: 2026-10-14\n---\n"
                            "## Tasks\n- [ ] 1.1 Task\n      files: x.py (new)\n"
                            "      verify: python3 -m unittest\n")
        code, body = self.run_cmd(backend, task="1.1")
        payload = json.loads(body)
        self.assertEqual((0, "small-tier-projection"), (code, payload["kind"]))
        self.assertIn("smallTierEligible", payload)
        code, body = self.run_cmd(backend, task="7.7")
        self.assertEqual((2, "sp-unknown-task"), (code, json.loads(body)["code"]))

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
