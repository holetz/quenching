"""Executable proofs for the read-only security pillar."""
from __future__ import annotations

import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.security import main
from quenching.security.probe import (
    access_ownership,
    advisory_dependency_configuration,
    build_report,
    secret_ignore_coverage,
    workflow_permissions,
)


class SecurityQuestions(unittest.TestCase):
    def test_empty_repository_reports_each_question_without_writing(self):
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            before = sorted(root.iterdir())
            report = build_report(str(root)).as_dict()
            self.assertTrue(report["ok"])
            self.assertTrue(report["readOnly"])
            self.assertEqual(
                {"workflow-permissions", "secret-ignore-coverage",
                 "advisory-dependency-configuration", "access-ownership"},
                {item["key"] for item in report["questions"]},
            )
            self.assertEqual(before, sorted(root.iterdir()))

    def test_workflow_permissions_counts_workflow_and_job_declarations(self):
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            workflow = root / ".github" / "workflows" / "ci.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(
                "permissions:\n  contents: read\njobs:\n"
                "  test:\n    permissions:\n      actions: read\n", encoding="utf-8")
            result = workflow_permissions(root).as_dict()
            self.assertEqual("present", result["state"])
            evidence = result["evidence"][0]
            self.assertEqual(1, evidence["workflowDeclarations"])
            self.assertEqual(1, evidence["jobDeclarations"])

    def test_secret_ignore_coverage_groups_known_patterns(self):
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            (root / ".gitignore").write_text(
                "# comment\n.env\n*.pem\nid_rsa\nservice-secret.json\n!public.key\n", encoding="utf-8")
            result = secret_ignore_coverage(root).as_dict()
            self.assertEqual("present", result["state"])
            self.assertEqual(
                {"environment-files", "private-keys", "credential-files"},
                set(result["details"]["patterns"]),
            )

    def test_advisory_and_access_questions_find_known_files(self):
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            (root / ".github").mkdir()
            (root / ".github" / "dependabot.yml").write_text("version: 2\n", encoding="utf-8")
            (root / ".github" / "CODEOWNERS").write_text("* @owners\n", encoding="utf-8")
            (root / "pyproject.toml").write_text(
                "[tool.pip-audit]\nformat = 'columns'\n", encoding="utf-8")
            self.assertEqual("present", advisory_dependency_configuration(root).state)
            self.assertEqual("present", access_ownership(root).state)

    def test_cli_reports_version_json_and_missing_root(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(0, main(["--version"]))
        self.assertRegex(output.getvalue().strip(), r"^cq security \d+\.\d+\.\d+$")

        with tempfile.TemporaryDirectory() as raw:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(0, main(["--root", raw, "--json"]))
            payload = json.loads(output.getvalue())
            self.assertEqual("security", payload["pillar"])
            self.assertTrue(payload["readOnly"])

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(2, main(["--root", "/path/that/does/not/exist", "--json"]))
        self.assertEqual("security-root-missing", json.loads(output.getvalue())["code"])


if __name__ == "__main__":
    unittest.main()
