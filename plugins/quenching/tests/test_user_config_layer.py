"""Executable proofs for the user configuration layer: the repository wins key by key."""
from __future__ import annotations

import json
import os
import pathlib
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


if __name__ == "__main__":
    unittest.main()
