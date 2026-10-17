"""Executable proofs for the `.claude/quenching.json` seed, `cq config init|check` and the doctor."""
from __future__ import annotations

import copy
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.codex import config as codex_config
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
        del cut["shared"]["codex"]["executor"]["sandbox"]
        del cut["specs"]["chat"]
        self.assertEqual(["shared.codex.executor.sandbox", "specs.chat.budgetUsd",
                          "specs.chat.model", "specs.chat.timeoutSeconds"],
                         seed.missing_keys(cut, str(self.repo)))

    def test_extra_keys_are_not_reported(self):
        doc = seed.seed_document(str(self.repo))
        doc["shared"]["codex"]["unknown"] = 1
        self.assertEqual([], seed.missing_keys(doc, str(self.repo)))


if __name__ == "__main__":
    unittest.main()
