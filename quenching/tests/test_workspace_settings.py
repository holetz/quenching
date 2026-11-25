"""`shared.workspace.vscode`: the recommended block, the doctor report and the deploy seed."""

from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.common import doctor
from quenching.common import workspace
from quenching.common.jsonc import jsonc_loads
from quenching.deploy.cli import main as deploy_main


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


class TheTasksBlock(unittest.TestCase):
    def test_the_snippet_parses_and_carries_every_task(self):
        document = jsonc_loads(workspace.tasks_snippet())
        self.assertEqual("2.0.0", document["version"])
        self.assertEqual(list(workspace.TASK_LABELS),
                         [task["label"] for task in document["tasks"]])

    def test_every_cq_task_runs_the_target_local_launcher_with_its_windows_twin(self):
        document = jsonc_loads(workspace.tasks_snippet())
        for task in document["tasks"]:
            if not task["command"].startswith(workspace.CQ):
                continue
            self.assertEqual({"cwd": "${workspaceFolder}"}, task["options"])
            self.assertEqual([], task["problemMatcher"])
            self.assertTrue(task["windows"]["command"].startswith(workspace.CQ_WINDOWS))

    def test_the_spec_status_task_prompts_for_an_id(self):
        document = jsonc_loads(workspace.tasks_snippet())
        status = next(task for task in document["tasks"]
                      if task["label"] == "quenching: specs status")
        self.assertIn("${input:specId}", status["command"])
        self.assertEqual([{"id": "specId", "type": "promptString", "description": "Spec id"}],
                         document["inputs"])

    def test_the_gate_is_the_default_test_task(self):
        document = jsonc_loads(workspace.tasks_snippet())
        gate = next(task for task in document["tasks"] if task["label"] == "quenching: gate")
        self.assertEqual("bash scripts/verify_repo.sh", gate["command"])
        self.assertEqual({"kind": "test", "isDefault": True}, gate["group"])

    def test_open_slots_waits_for_the_workspace_projection(self):
        document = jsonc_loads(workspace.tasks_snippet())
        opener = next(task for task in document["tasks"]
                      if task["label"] == "quenching: open slots")
        self.assertEqual(["quenching: slots workspace"], opener["dependsOn"])
        self.assertIn("quenching-slots.code-workspace", opener["command"])


class TheTasksReport(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = pathlib.Path(tmp.name)

    def write(self, text: str):
        path = self.root / workspace.TASKS_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_an_absent_file_names_every_label(self):
        report = workspace.tasks_report(str(self.root))
        self.assertEqual("absent", report["state"])
        self.assertFalse(report["complete"])
        self.assertEqual(list(workspace.TASK_LABELS), report["missing"])

    def test_the_snippet_is_complete(self):
        self.write(workspace.tasks_snippet())
        report = workspace.tasks_report(str(self.root))
        self.assertEqual("present", report["state"])
        self.assertTrue(report["complete"], report)
        self.assertEqual([], report["missing"])

    def test_a_partial_file_names_the_missing_label(self):
        document = workspace.tasks_document()
        del document["tasks"][1]
        self.write(json.dumps(document))
        report = workspace.tasks_report(str(self.root))
        self.assertFalse(report["complete"])
        self.assertEqual(["quenching: deploy check"], report["missing"])

    def test_an_unreadable_file_is_a_state_never_an_error(self):
        self.write("{ nope")
        report = workspace.tasks_report(str(self.root))
        self.assertEqual("unreadable", report["state"])
        self.assertTrue(report["reason"])


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

    def tasks(self, text: str):
        path = self.root / workspace.TASKS_PATH
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

    def test_workspace_prints_both_blocks_and_writes_nothing(self):
        code, payload = self.payload(workspace=True)
        self.assertEqual(0, code)
        self.assertEqual("absent", payload["tasks"]["state"])
        self.assertEqual(workspace.tasks_document(), jsonc_loads(payload["tasksSnippet"]))
        self.assertFalse((self.root / workspace.TASKS_PATH).exists())

    def test_workspace_human_names_the_tasks_file_and_its_labels(self):
        code, human = self.run_doctor(workspace=True)
        self.assertEqual(0, code)
        self.assertIn(".vscode/tasks.json", human)
        self.assertIn("quenching: gate", human)

    def test_the_standard_report_carries_the_tasks_when_the_file_exists(self):
        self.tasks(workspace.tasks_snippet())
        code, payload = self.payload()
        self.assertEqual(0, code)
        self.assertTrue(payload["tasks"]["complete"])
        code, human = self.run_doctor()
        self.assertEqual(0, code)
        self.assertIn("tasks:", human)

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


class TheDeploy(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.target = pathlib.Path(tmp.name)
        subprocess.run(["git", "-C", str(self.target), "init", "-q"], check=True,
                       capture_output=True)
        xdg = pathlib.Path(tempfile.mkdtemp(dir=tmp.name, prefix="xdg-"))
        env = mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(xdg), "OPENCODE_CONFIG": ""})
        env.start()
        self.addCleanup(env.stop)
        precompile = mock.patch("quenching.deploy.cli._precompile", return_value=None)
        precompile.start()
        self.addCleanup(precompile.stop)

    def config(self, document):
        path = self.target / ".agents" / "quenching.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document), encoding="utf-8")

    def deploy(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = deploy_main(["--target", str(self.target), *argv, "--json"])
        return code, json.loads(out.getvalue() or "{}")

    def test_without_the_key_no_vscode_file_is_planned_or_written(self):
        code, payload = self.deploy("--modules", "specs", "--check")
        self.assertEqual(1, code)  # the fresh target still owes the whole surface
        self.assertNotIn(".vscode/settings.json",
                         [change["path"] for change in payload["changes"]])
        self.assertFalse((self.target / ".vscode").exists())

    def test_declared_key_seeds_the_block_only_when_absent(self):
        self.config({"shared": {"workspace": {"vscode": True}}})
        code, payload = self.deploy("--modules", "specs", "--check")
        self.assertEqual(1, code)
        self.assertIn({"change": "seed", "path": ".vscode/settings.json"}, payload["changes"])
        self.assertFalse((self.target / ".vscode").exists())
        code, payload = self.deploy("--modules", "specs", "--write")
        self.assertEqual(0, code)
        path = self.target / ".vscode" / "settings.json"
        self.assertEqual(workspace.recommended(), jsonc_loads(path.read_text(encoding="utf-8")))
        path.write_text(path.read_text(encoding="utf-8") + "\n// user edit\n", encoding="utf-8")
        code, payload = self.deploy("--modules", "specs", "--write")
        self.assertEqual(0, code)
        self.assertIn("// user edit", path.read_text(encoding="utf-8"))

    def test_declared_key_seeds_the_tasks_file_only_when_absent(self):
        self.config({"shared": {"workspace": {"vscode": True}}})
        code, payload = self.deploy("--modules", "specs", "--check")
        self.assertEqual(1, code)
        self.assertIn({"change": "seed", "path": ".vscode/tasks.json"}, payload["changes"])
        code, payload = self.deploy("--modules", "specs", "--write")
        self.assertEqual(0, code)
        path = self.target / ".vscode" / "tasks.json"
        self.assertEqual(workspace.tasks_document(), jsonc_loads(path.read_text(encoding="utf-8")))
        path.write_text(path.read_text(encoding="utf-8") + "\n// user edit\n", encoding="utf-8")
        code, payload = self.deploy("--modules", "specs", "--write")
        self.assertEqual(0, code)
        self.assertIn("// user edit", path.read_text(encoding="utf-8"))

    def test_a_declared_partial_tasks_file_is_suggested_and_never_rewritten(self):
        self.config({"shared": {"workspace": {"vscode": True}}})
        document = workspace.tasks_document()
        del document["tasks"][0]
        partial = json.dumps(document)
        path = self.target / ".vscode" / "tasks.json"
        path.parent.mkdir()
        path.write_text(partial, encoding="utf-8")
        code, payload = self.deploy("--modules", "specs", "--check")
        self.assertTrue(any(".vscode/tasks.json" in line and "quenching: gate" in line
                            for line in payload["suggestions"]), payload["suggestions"])
        code, payload = self.deploy("--modules", "specs", "--write")
        self.assertEqual(0, code)
        self.assertEqual(partial, path.read_text(encoding="utf-8"))

    def test_an_unreadable_tasks_file_is_a_suggestion_and_is_left_alone(self):
        self.config({"shared": {"workspace": {"vscode": True}}})
        path = self.target / ".vscode" / "tasks.json"
        path.parent.mkdir()
        path.write_text("{ nope", encoding="utf-8")
        code, payload = self.deploy("--modules", "specs", "--check")
        self.assertTrue(any("tasks.json" in line and "could not be read" in line
                            for line in payload["suggestions"]), payload["suggestions"])
        code, payload = self.deploy("--modules", "specs", "--write")
        self.assertEqual(0, code)
        self.assertEqual("{ nope", path.read_text(encoding="utf-8"))

    def deploy_human(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = deploy_main(["--target", str(self.target), *argv])
        return code, out.getvalue()

    def test_a_vscode_workspace_without_the_key_gets_a_suggestion(self):
        (self.target / ".vscode").mkdir()
        code, payload = self.deploy("--modules", "specs", "--check")
        self.assertEqual(1, code)
        self.assertTrue(any("shared.workspace.vscode" in line
                            for line in payload["suggestions"]), payload["suggestions"])
        code, human = self.deploy_human("--modules", "specs", "--check")
        self.assertIn("suggestion:", human)

    def test_no_vscode_workspace_means_no_suggestion(self):
        code, payload = self.deploy("--modules", "specs", "--check")
        self.assertEqual([], payload["suggestions"])

    def test_a_declared_partial_file_is_suggested_and_never_rewritten(self):
        self.config({"shared": {"workspace": {"vscode": True}}})
        partial = json.dumps({"chat.agent.maxRequests": 25})
        path = self.target / ".vscode" / "settings.json"
        path.parent.mkdir()
        path.write_text(partial, encoding="utf-8")
        code, payload = self.deploy("--modules", "specs", "--check")
        self.assertTrue(any("chat.agent.maxRequests >= 100" in line
                            for line in payload["suggestions"]), payload["suggestions"])
        code, payload = self.deploy("--modules", "specs", "--write")
        self.assertEqual(0, code)
        self.assertEqual(partial, path.read_text(encoding="utf-8"))

    def test_an_unreadable_file_is_a_suggestion_and_is_left_alone(self):
        path = self.target / ".vscode" / "settings.json"
        path.parent.mkdir()
        path.write_text("{ nope", encoding="utf-8")
        code, payload = self.deploy("--modules", "specs", "--check")
        self.assertTrue(any("could not be read" in line
                            for line in payload["suggestions"]), payload["suggestions"])
        code, payload = self.deploy("--modules", "specs", "--write")
        self.assertEqual(0, code)
        self.assertEqual("{ nope", path.read_text(encoding="utf-8"))

    def test_a_malformed_workspace_block_is_refused_before_any_write(self):
        self.config({"shared": {"workspace": {"vscode": "yes"}}})
        code, payload = self.deploy("--modules", "specs", "--write")
        self.assertEqual(2, code)
        self.assertEqual("ct-deploy-workspace", payload["code"])
        self.assertFalse((self.target / ".vscode").exists())
        self.assertFalse((self.target / ".agents" / ".quenching-deploy.json").exists())
