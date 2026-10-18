"""Executable proofs for the `.claude/quenching.json` seed, `cq config init|check` and the doctor."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.codex import config as codex_config
from quenching.common import doctor
from quenching.config import main as config_main
from quenching.config import autonomy, host, seed
from quenching.knowledge import config as knowledge_config
from quenching.session.commands import context as context_mod
from quenching.specs import portal


class SeedDocument(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = pathlib.Path(tmp.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)

    def test_seed_covers_every_default_tree(self):
        doc = seed.seed_document(str(self.repo))
        shared = doc["shared"]
        self.assertEqual(codex_config.DEFAULTS, shared["codex"])
        self.assertEqual(autonomy.DEFAULTS, shared["autonomy"])
        self.assertEqual(context_mod.BUDGETS, shared["contextBudgets"])
        self.assertEqual({"warnAsError", "ignoreGlobs"}, set(shared["okfValidate"]))
        self.assertEqual({k for k, v in host.DEFAULTS.items() if v is not None},
                         set(shared["workHost"]))
        self.assertEqual({"model", "budgetUsd", "timeoutSeconds"}, set(doc["specs"]["chat"]))
        self.assertEqual("git", doc["backend"])
        self.assertIn("installed", shared["profiles"])

    def test_restated_defaults_equal_their_owners(self):
        self.assertEqual(knowledge_config.DEFAULTS, seed.OKF_VALIDATE)
        defaults = {"model": "sonnet", "budgetUsd": portal.chat_mod.DEFAULT_BUDGET_USD,
                    "timeoutSeconds": portal.chat_mod.CHAT_TIMEOUT_SECONDS}
        self.assertEqual(defaults, portal.chat_settings(None))
        self.assertEqual(defaults, seed.CHAT)

    def test_seed_loads_without_a_single_warning(self):
        (self.repo / ".claude").mkdir()
        (self.repo / ".claude" / "quenching.json").write_text(
            json.dumps(seed.seed_document(str(self.repo))))
        root = str(self.repo)
        self.assertEqual([], autonomy.coerce(seed.seed_document(root)["shared"]["autonomy"])[1])
        self.assertEqual([], host.load_settings(root)[1])
        self.assertEqual([], codex_config.load_settings(root)[1])
        for role in context_mod.BUDGETS:
            self.assertEqual(context_mod.BUDGETS[role], context_mod.effective_budgets(root)[role])

    def test_seed_is_a_copy_not_the_owner_dict(self):
        seed.seed_document(str(self.repo))["shared"]["codex"]["executor"]["enabled"] = False
        self.assertTrue(codex_config.DEFAULTS["executor"]["enabled"])

    def test_missing_keys_lists_exactly_the_deleted_leaves(self):
        doc = seed.seed_document(str(self.repo))
        self.assertEqual([], seed.missing_keys(doc, str(self.repo)))
        cut = copy.deepcopy(doc)
        del cut["shared"]["codex"]["executor"]["reasoningEffort"]
        del cut["specs"]["chat"]
        self.assertEqual(["shared.codex.executor.reasoningEffort", "specs.chat.budgetUsd",
                          "specs.chat.model", "specs.chat.timeoutSeconds"],
                         seed.missing_keys(cut, str(self.repo)))

    def test_extra_keys_are_not_reported(self):
        doc = seed.seed_document(str(self.repo))
        doc["shared"]["codex"]["unknown"] = 1
        self.assertEqual([], seed.missing_keys(doc, str(self.repo)))


class InitAndCheck(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = pathlib.Path(tmp.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.file = self.repo / ".claude" / "quenching.json"

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = config_main(["--root", str(self.repo), *argv])
        return code, out.getvalue(), err.getvalue()

    def test_preview_writes_nothing(self):
        code, out, _ = self.run_cli("init", "--json")
        self.assertEqual(0, code)
        self.assertFalse(self.file.exists())
        self.assertFalse(json.loads(out)["written"])

    def test_write_creates_the_seed_and_check_is_clean(self):
        self.assertEqual(0, self.run_cli("init", "--write")[0])
        self.assertEqual(seed.seed_document(str(self.repo)), json.loads(self.file.read_text()))
        code, out, _ = self.run_cli("check", "--json")
        self.assertEqual((0, []), (code, json.loads(out)["missing"]))

    def test_init_refuses_an_existing_file(self):
        self.file.parent.mkdir()
        self.file.write_text("{}")
        code, _, err = self.run_cli("init", "--write")
        self.assertEqual(2, code)
        self.assertIn("already exists", err)
        self.assertEqual("{}", self.file.read_text())

    def test_check_names_the_deleted_leaf_with_exit_1(self):
        self.run_cli("init", "--write")
        doc = json.loads(self.file.read_text())
        del doc["shared"]["autonomy"]["maxLaunches"]
        self.file.write_text(json.dumps(doc))
        code, out, _ = self.run_cli("check", "--json")
        self.assertEqual((1, ["shared.autonomy.maxLaunches"]), (code, json.loads(out)["missing"]))

    def test_check_refuses_when_the_file_is_absent(self):
        self.assertEqual(2, self.run_cli("check")[0])


class DoctorReport(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = pathlib.Path(tmp.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)

    def test_absent_file_is_reported_not_missing_keys(self):
        self.assertEqual({"present": False, "missing": []}, doctor.config_report(str(self.repo)))

    def test_missing_keys_are_named(self):
        (self.repo / ".claude").mkdir()
        (self.repo / ".claude" / "quenching.json").write_text(json.dumps({"shared": {}}))
        report = doctor.config_report(str(self.repo))
        self.assertTrue(report["present"])
        self.assertIn("shared.codex.executor.reasoningEffort", report["missing"])
        self.assertIn("missing", doctor._config_line(report))

    def test_a_module_without_the_seed_reports_nothing(self):
        with mock.patch.dict(sys.modules, {"quenching.config.seed": None}):
            self.assertIsNone(doctor.config_report(str(self.repo)))
        self.assertIsNone(doctor._config_line(None))

    def test_run_adds_the_block_to_the_json(self):
        out = io.StringIO()
        with mock.patch.object(doctor, "inspect_environment", return_value={
                "root": str(self.repo), "python": {"available": True, "version": "3.12.0",
                                                    "required": ">=3.11"},
                "backend": None, "profile": {"effective": []}, "requirements": [],
                "missing": []}), contextlib.redirect_stdout(out):
            self.assertEqual(0, doctor.run(True, str(self.repo)))
        self.assertEqual({"present": False, "missing": []}, json.loads(out.getvalue())["config"])


if __name__ == "__main__":
    unittest.main()
