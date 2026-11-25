"""`shared.workspace.vscode`: the recommended block, the doctor report and the deploy seed."""

from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import sys
import tempfile
import unittest

try:
    import _paths  # noqa: F401
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.common import doctor
from quenching.common import workspace
from quenching.common.jsonc import jsonc_loads


class TheBlock(unittest.TestCase):
    def test_the_snippet_parses_as_jsonc(self):
        document = jsonc_loads(workspace.snippet())
        self.assertEqual(document, workspace.recommended())

    def test_the_four_generated_trees_are_excluded_at_the_root(self):
        block = jsonc_loads(workspace.snippet())["files.exclude"]
        self.assertEqual(list(block), list(workspace.EXCLUDED))
        self.assertTrue(all(value is True for value in block.values()))
        self.assertNotIn("**/", "".join(block))

    def test_the_request_ceiling_is_the_declared_headroom(self):
        self.assertEqual(100, jsonc_loads(workspace.snippet())
                         ["chat.agent.maxRequests"])
        self.assertEqual(workspace.MAX_REQUESTS, workspace.recommended()
                         ["chat.agent.maxRequests"])


class TheReport(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = pathlib.Path(tmp.name)

    def write(self, text: str):
        path = self.root / workspace.PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_an_absent_file_names_every_key(self):
        report = workspace.report(str(self.root))
        self.assertEqual("absent", report["state"])
        self.assertFalse(report["complete"])
        self.assertEqual(list(workspace.KEYS), report["missing"])
        self.assertEqual(list(workspace.EXCLUDED), report["missingExclusions"])

    def test_the_snippet_is_complete(self):
        self.write(workspace.snippet())
        report = workspace.report(str(self.root))
        self.assertEqual("present", report["state"])
        self.assertTrue(report["complete"], report)
        self.assertEqual([], report["missing"])
        self.assertEqual([], report["missingExclusions"])
        self.assertEqual(workspace.MAX_REQUESTS, report["maxRequests"])

    def test_a_partial_exclusion_names_the_missing_path(self):
        document = workspace.recommended()
        del document["files.exclude"]["site-source"]
        self.write(json.dumps(document))
        report = workspace.report(str(self.root))
        self.assertFalse(report["complete"])
        self.assertEqual(["site-source"], report["missingExclusions"])
        self.assertIn("site-source", report["missingExclusions"])

    def test_a_low_request_ceiling_is_a_gap(self):
        document = workspace.recommended()
        document["chat.agent.maxRequests"] = 25
        self.write(json.dumps(document))
        report = workspace.report(str(self.root))
        self.assertFalse(report["complete"])
        self.assertEqual(25, report["maxRequests"])
        self.assertEqual([], report["missing"])  # present, but below the recommended headroom

    def test_an_unreadable_file_is_a_state_never_an_error(self):
        self.write("{ this is not json")
        report = workspace.report(str(self.root))
        self.assertEqual("unreadable", report["state"])
        self.assertTrue(report["reason"])

    def test_a_non_object_root_is_unreadable(self):
        self.write("[]")
        self.assertEqual("unreadable", workspace.report(str(self.root))["state"])

    def test_jsonc_comments_and_trailing_commas_are_read(self):
        self.write("""
        {
          // the block the doctor prints
          "files.exclude": {".agents/quenching": true, ".claude/skills": true, "site": true,
                            "site-source": true},
          "chat.agent.maxRequests": 100,
        }
        """)
        self.assertTrue(workspace.report(str(self.root))["complete"])


class TheDeclaration(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = pathlib.Path(tmp.name)

    def write(self, document):
        path = self.root / ".agents" / "quenching.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document), encoding="utf-8")

    def test_absent_reads_as_false_with_no_error(self):
        self.write({"backend": "git"})
        self.assertEqual((False, None), workspace.declared(str(self.root)))

    def test_true_and_false_read_from_the_repository_document(self):
        self.write({"shared": {"workspace": {"vscode": True}}})
        self.assertEqual((True, None), workspace.declared(str(self.root)))
        self.write({"shared": {"workspace": {"vscode": False}}})
        self.assertEqual((False, None), workspace.declared(str(self.root)))

    def test_a_malformed_block_names_the_error_and_never_a_value(self):
        self.write({"shared": {"workspace": "yes"}})
        value, error = workspace.declared(str(self.root))
        self.assertFalse(value)
        self.assertIn("shared.workspace", error)
        self.write({"shared": {"workspace": {"vscode": "yes"}}})
        value, error = workspace.declared(str(self.root))
        self.assertFalse(value)
        self.assertIn("true or false", error)
        self.write({"shared": {"workspace": {"github": True}}})
        value, error = workspace.declared(str(self.root))
        self.assertFalse(value)
        self.assertIn("unknown key", error)


class TheDoctor(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = pathlib.Path(tmp.name)
        (self.root / ".agents").mkdir()
        (self.root / ".agents" / "quenching.json").write_text(
            json.dumps({"backend": "git"}), encoding="utf-8")

    def settings(self, text: str):
        path = self.root / workspace.PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def run_doctor(self, **kwargs):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = doctor.run(False, str(self.root), **kwargs)
        return code, out.getvalue()

    def payload(self, **kwargs):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = doctor.run(True, str(self.root), **kwargs)
        return code, json.loads(out.getvalue())

    def test_workspace_prints_the_block_and_writes_nothing(self):
        code, payload = self.payload(workspace=True)
        self.assertEqual(0, code)
        self.assertEqual("absent", payload["workspace"]["state"])
        self.assertEqual(workspace.recommended(), jsonc_loads(payload["snippet"]))
        self.assertFalse((self.root / workspace.PATH).exists())

    def test_workspace_human_names_the_state_and_the_live_half(self):
        code, human = self.run_doctor(workspace=True)
        self.assertEqual(0, code)
        self.assertIn("not declared", human)
        self.assertIn("live half is not proved here", human)

    def test_workspace_with_write_is_refused(self):
        code, payload = self.payload(workspace=True, write=True)
        self.assertEqual(2, code)
        self.assertTrue(payload["message"].endswith("`--workspace` writes nothing"))

    def test_the_standard_report_carries_the_workspace_when_the_file_exists(self):
        self.settings(workspace.snippet())
        code, payload = self.payload()
        self.assertEqual(0, code)
        self.assertTrue(payload["workspace"]["complete"])
        code, human = self.run_doctor()
        self.assertEqual(0, code)
        self.assertIn("workspace:", human)
        self.assertIn("2/2 recommended key(s) present", human)

    def test_the_standard_report_is_silent_without_the_file_or_the_key(self):
        code, payload = self.payload()
        self.assertEqual(0, code)
        self.assertNotIn("workspace", payload)
        code, human = self.run_doctor()
        self.assertEqual(0, code)
        self.assertNotIn("workspace:", human)

    def test_a_declared_seed_names_the_command_that_writes_it(self):
        (self.root / ".agents" / "quenching.json").write_text(
            json.dumps({"backend": "git", "shared": {"workspace": {"vscode": True}}}),
            encoding="utf-8")
        code, human = self.run_doctor()
        self.assertEqual(0, code)
        self.assertIn("`cq deploy --write` seeds it", human)

    def test_a_partial_file_names_the_gap(self):
        document = workspace.recommended()
        del document["files.exclude"]["site"]
        self.settings(json.dumps(document))
        code, human = self.run_doctor()
        self.assertEqual(0, code)
        self.assertIn("site", human)
        self.assertIn("cq doctor --workspace", human)
