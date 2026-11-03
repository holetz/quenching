"""Executable proofs for the `shared.autonomy` block of `cq config show --effective`."""
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
from quenching.common.config import USER_CONFIG_ENV
from quenching.config.autonomy import DEFAULTS, coerce
from quenching.config.effective import effective


class AutonomyBlock(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = pathlib.Path(tmp.name) / "repo"
        (self.repo / ".claude").mkdir(parents=True)
        self.user = pathlib.Path(tmp.name) / "user.json"
        patch = mock.patch.dict(os.environ, {USER_CONFIG_ENV: str(self.user)})
        patch.start()
        self.addCleanup(patch.stop)

    def _effective(self, repo=None, user=None):
        if repo is not None:
            (self.repo / ".claude" / "quenching.json").write_text(json.dumps(repo))
        if user is not None:
            self.user.write_text(json.dumps(user))
        payload = effective(str(self.repo))
        return {row["key"]: row for row in payload["values"]}, payload

    def test_defaults_are_listed_leaf_by_leaf_and_match_todays_behaviour(self):
        rows, payload = self._effective()
        for leaf, value in DEFAULTS.items():
            row = rows[f"shared.autonomy.{leaf}"]
            self.assertEqual((value, "default"), (row["value"], row["source"]))
        self.assertEqual(
            (3, 40, 20, "low", "policy"),
            tuple(DEFAULTS[k] for k in ("maxWorkers", "maxLaunches", "livenessMinutes",
                                        "runAloneUpTo", "merge")))
        self.assertEqual([], payload["warnings"])

    def test_repository_beats_user_and_completes_leaf_by_leaf(self):
        rows, _ = self._effective(
            repo={"shared": {"autonomy": {"maxWorkers": 2}}},
            user={"shared": {"autonomy": {"maxWorkers": 5, "merge": "all"}}})
        self.assertEqual((2, "repository"), (rows["shared.autonomy.maxWorkers"]["value"],
                                              rows["shared.autonomy.maxWorkers"]["source"]))
        self.assertEqual("default", rows["shared.autonomy.merge"]["source"])

    def test_user_value_counts_when_the_repository_is_silent(self):
        rows, _ = self._effective(user={"shared": {"autonomy": {"runAloneUpTo": "medium"}}})
        self.assertEqual(("medium", "user"), (rows["shared.autonomy.runAloneUpTo"]["value"],
                                              rows["shared.autonomy.runAloneUpTo"]["source"]))

    def test_invalid_values_fall_back_to_the_default_and_are_named(self):
        rows, payload = self._effective(repo={"shared": {"autonomy": {
            "maxWorkers": 99, "merge": "yes", "livenessMinutes": True, "maxLaunches": 7,
            "colour": 1}}})
        self.assertEqual((3, "default"), (rows["shared.autonomy.maxWorkers"]["value"],
                                          rows["shared.autonomy.maxWorkers"]["source"]))
        self.assertEqual("policy", rows["shared.autonomy.merge"]["value"])
        self.assertEqual(20, rows["shared.autonomy.livenessMinutes"]["value"])
        self.assertEqual((7, "repository"), (rows["shared.autonomy.maxLaunches"]["value"],
                                             rows["shared.autonomy.maxLaunches"]["source"]))
        text = "\n".join(payload["warnings"])
        for needle in ("maxWorkers", "merge", "livenessMinutes", "colour"):
            self.assertIn(needle, text)

    def test_a_block_that_is_not_an_object_keeps_every_default(self):
        settings, warnings = coerce("fast")
        self.assertEqual(DEFAULTS, settings)
        self.assertEqual(1, len(warnings))


if __name__ == "__main__":
    unittest.main()
