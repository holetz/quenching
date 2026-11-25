"""Executable proofs for `cq config show --effective`: each value carries the layer it came from."""
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
from quenching.config import main
from quenching.config.effective import effective


class EffectiveConfig(unittest.TestCase):
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

    def _rows(self, branch=None):
        with mock.patch("quenching.specs.backends.git.branch_config",
                        return_value=branch or {}):
            payload = effective(str(self.repo))
        return {row["key"]: row for row in payload["values"]}, payload

    def test_autonomy_defaults_are_listed_leaf_by_leaf(self):
        rows, _ = self._rows()
        self.assertEqual({"value": "policy", "source": "default"},
                         {k: rows["shared.autonomy.merge"][k] for k in ("value", "source")})

    def test_repository_beats_user_and_user_fills_in(self):
        self.user.write_text(json.dumps({
            "shared": {"autonomy": {"maxWorkers": 5}, "worktreeSetup": "make user"}}))
        self._repo({"shared": {"autonomy": {"maxLaunches": 7}}})
        rows, _ = self._rows()
        # the repository block replaces the user's whole: maxWorkers falls back to the default
        self.assertEqual((3, "default"), (rows["shared.autonomy.maxWorkers"]["value"],
                                          rows["shared.autonomy.maxWorkers"]["source"]))
        self.assertEqual(("repository", 7), (rows["shared.autonomy.maxLaunches"]["source"],
                                             rows["shared.autonomy.maxLaunches"]["value"]))
        self.assertEqual(("user", "make user"), (rows["shared.worktreeSetup"]["source"],
                                                 rows["shared.worktreeSetup"]["value"]))

    def test_user_autonomy_block_is_attributed_to_user(self):
        self.user.write_text(json.dumps({"shared": {"autonomy": {"maxWorkers": 5}}}))
        rows, _ = self._rows()
        self.assertEqual((5, "user"), (rows["shared.autonomy.maxWorkers"]["value"],
                                       rows["shared.autonomy.maxWorkers"]["source"]))
        self.assertEqual("default", rows["shared.autonomy.merge"]["source"])

    def test_a_leftover_codex_block_is_named_obsolete_and_never_refused(self):
        self._repo({"shared": {"codex": {"executor": {"enabled": True}}}})
        rows, payload = self._rows()
        self.assertFalse([key for key in rows if key.startswith("shared.codex")])
        self.assertTrue([w for w in payload["warnings"] if "shared.codex is obsolete" in w])

    def test_branch_layer_wins_only_with_backend_git(self):
        self._repo({"specs": {"subjects": {"a": 1}}, "backend": "git"})
        rows, payload = self._rows({"subjects": {"b": 2}, "worktreeSetup": "ignored"})
        self.assertEqual(("branch", {"b": 2}), (rows["specs.subjects"]["source"],
                                                rows["specs.subjects"]["value"]))
        self.assertNotIn("specs.worktreeSetup", rows)
        self.assertEqual("repository", rows["backend"]["source"])
        self.assertTrue(next(x for x in payload["layers"] if x["name"] == "branch")["applies"])

        self._repo({"specs": {"subjects": {"a": 1}}})
        rows, payload = self._rows({"subjects": {"b": 2}})
        self.assertEqual(("repository", {"a": 1}), (rows["specs.subjects"]["source"],
                                                   rows["specs.subjects"]["value"]))
        self.assertFalse(next(x for x in payload["layers"] if x["name"] == "branch")["applies"])

    def test_unreadable_user_file_is_reported_not_fatal(self):
        self.user.write_text("{nope")
        _, payload = self._rows()
        layer = next(x for x in payload["layers"] if x["name"] == "user")
        self.assertTrue(layer["unparseable"])

    def test_cli_json_and_required_flag(self):
        self._repo({"shared": {"worktreeSetup": "make"}})
        with mock.patch("sys.stdout") as out:
            code = main(["--root", str(self.repo), "show", "--effective", "--json"])
        self.assertEqual(0, code)
        printed = "".join(call.args[0] for call in out.write.call_args_list)
        self.assertEqual("repository", next(
            row for row in json.loads(printed)["values"]
            if row["key"] == "shared.worktreeSetup")["source"])
        with mock.patch("sys.stderr"):
            self.assertEqual(3, main(["--root", str(self.repo), "show"]))



class LocalProvenance(EffectiveConfig):
    def _local(self, doc):
        (self.repo / ".agents").mkdir(exist_ok=True)
        (self.repo / ".agents" / "quenching.local.json").write_text(json.dumps(doc))

    def test_each_value_names_the_layer_that_won_it(self):
        self._repo({"shared": {"worktreeSlots": {"max": 12}, "autonomy": {"merge": "never"},
                               "worktreeSetup": "make"}})
        self._local({"shared": {"worktreeSlots": {"max": 6}, "worktreeSetup": "other",
                                "autonomy": {"merge": "all", "maxWorkers": 5}}})
        rows, payload = self._rows()
        self.assertEqual((6, "local"), (rows["shared.worktreeSlots.max"]["value"],
                                        rows["shared.worktreeSlots.max"]["source"]))
        self.assertEqual("default", rows["shared.worktreeSlots.min"]["source"])
        self.assertEqual(("never", "repository"), (rows["shared.autonomy.merge"]["value"],
                                                   rows["shared.autonomy.merge"]["source"]))
        self.assertEqual((5, "local"), (rows["shared.autonomy.maxWorkers"]["value"],
                                        rows["shared.autonomy.maxWorkers"]["source"]))
        self.assertEqual("repository", rows["shared.worktreeSetup"]["source"])
        self.assertTrue(any("shared.worktreeSetup" in w for w in payload["warnings"]))
        self.assertIn("local", [layer["name"] for layer in payload["layers"]])


if __name__ == "__main__":
    unittest.main()
