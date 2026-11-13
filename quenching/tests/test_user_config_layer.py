"""Executable proofs for the user configuration layer: the repository wins key by key."""
from __future__ import annotations

import json
import os
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
from quenching.common.config import USER_CONFIG_ENV, load_config, namespace


class UserConfigLayer(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = pathlib.Path(tmp.name) / "repo"
        (self.repo / ".claude").mkdir(parents=True)
        self.user = pathlib.Path(tmp.name) / "user.json"
        patch = mock.patch.dict(os.environ, {USER_CONFIG_ENV: str(self.user)})
        patch.start()
        self.addCleanup(patch.stop)

    def _repo(self, doc):
        (self.repo / ".claude" / "quenching.json").write_text(json.dumps(doc))

    def _load(self):
        return load_config(str(self.repo), detect_provider_info=False)

    def test_repository_wins_key_by_key(self):
        self.user.write_text(json.dumps({
            "shared": {"codex": {"crossReview": "off"}, "worktreeSetup": "make user"}}))
        self._repo({"shared": {"codex": {"crossReview": "auto"}}})
        shared = namespace(self._load(), "shared")
        self.assertEqual(shared["codex"], {"crossReview": "auto"})   # replaced whole, not merged
        self.assertEqual(shared["worktreeSetup"], "make user")       # filled from the user

    def test_user_layer_alone_and_absent(self):
        self._repo({"shared": {}})
        self.assertFalse(self._load()["userConfig"]["present"])
        self.user.write_text(json.dumps({"shared": {"sharedPaths": [".env"]}}))
        cfg = self._load()
        self.assertEqual(cfg["shared"]["sharedPaths"], [".env"])
        self.assertEqual(cfg["data"]["shared"]["sharedPaths"], [".env"])
        self.assertEqual(cfg["userConfig"]["keys"], {"shared": ["sharedPaths"]})

    def test_backend_and_flat_keys_are_ignored_and_bad_file_is_not_fatal(self):
        self.user.write_text(json.dumps({"backend": "azure-boards", "hooks": {}}))
        self._repo({"shared": {}})
        cfg = self._load()
        self.assertNotIn("backend", cfg["data"])
        self.assertEqual(cfg["userConfig"]["ignoredKeys"], ["backend", "hooks"])
        self.assertIsNone(cfg["migrationRefusal"])
        self.user.write_text("{nope")
        cfg = self._load()
        self.assertTrue(cfg["userConfig"]["unparseable"])
        self.assertIsNone(cfg["unparseable"])



class LocalLayer(UserConfigLayer):
    """`.agents/quenching.local.json`: placed per key by the registry scope."""

    def _local(self, doc):
        (self.repo / ".agents").mkdir(exist_ok=True)
        (self.repo / ".agents" / "quenching.local.json").write_text(json.dumps(doc))

    def test_a_machine_key_in_the_local_layer_beats_the_project(self):
        self._repo({"shared": {"worktreeSlots": {"max": 12, "min": 4}}})
        self._local({"shared": {"worktreeSlots": {"max": 6}}})
        cfg = self._load()
        self.assertEqual({"max": 6, "min": 4}, namespace(cfg, "shared")["worktreeSlots"])
        self.assertEqual(["shared.worktreeSlots.max"], cfg["localConfig"]["applied"])

    def test_an_either_key_only_fills_what_the_project_leaves_out(self):
        self.user.write_text(json.dumps({"shared": {"autonomy": {"maxWorkers": 2}}}))
        self._repo({"shared": {"autonomy": {"merge": "never"}}})
        self._local({"shared": {"autonomy": {"merge": "all", "maxWorkers": 5}}})
        block = namespace(self._load(), "shared")["autonomy"]
        self.assertEqual("never", block["merge"])
        self.assertEqual(5, block["maxWorkers"])

    def test_a_project_key_in_the_local_layer_is_flagged_and_ignored(self):
        self._repo({"shared": {"worktreeSetup": "make"}})
        self._local({"shared": {"worktreeSetup": "rm -rf /", "gitConventions": {"prTitle": "x"}},
                     "specs": {"subjects": {"a": {}}}})
        cfg = self._load()
        self.assertEqual("make", namespace(cfg, "shared")["worktreeSetup"])
        self.assertNotIn("gitConventions", namespace(cfg, "shared"))
        self.assertEqual({"shared.worktreeSetup", "shared.gitConventions.prTitle",
                          "specs.subjects"},
                         {row["key"] for row in cfg["localConfig"]["ignored"]})

    def test_a_local_layer_without_a_repository_file_still_applies(self):
        (self.repo / ".claude").rmdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self._local({"shared": {"contextBudgets": {"main": 1000}}})
        self.assertEqual({"main": 1000}, namespace(self._load(), "shared")["contextBudgets"])

    def test_an_unreadable_local_file_is_reported_not_fatal(self):
        self._repo({})
        (self.repo / ".agents").mkdir(exist_ok=True)
        (self.repo / ".agents" / "quenching.local.json").write_text("{nope")
        self.assertTrue(self._load()["localConfig"]["unparseable"])


if __name__ == "__main__":
    unittest.main()
