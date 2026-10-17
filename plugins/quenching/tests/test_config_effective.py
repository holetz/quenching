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

    def test_codex_defaults_are_listed_leaf_by_leaf(self):
        rows, _ = self._rows()
        self.assertEqual({"value": "auto", "source": "default"},
                         {k: rows["shared.codex.crossReview"][k] for k in ("value", "source")})
        self.assertEqual("default", rows["shared.codex.maxUsedPercent.primary"]["source"])
        self.assertEqual(80, rows["shared.codex.maxUsedPercent.primary"]["value"])

    def test_repository_beats_user_and_user_fills_in(self):
        self.user.write_text(json.dumps({
            "shared": {"codex": {"crossReview": "off"}, "worktreeSetup": "make user"}}))
        self._repo({"shared": {"codex": {"timeoutSeconds": 60}}})
        rows, _ = self._rows()
        # the repository block replaces the user's whole: crossReview falls back to the default
        self.assertEqual(("auto", "default"), (rows["shared.codex.crossReview"]["value"],
                                                rows["shared.codex.crossReview"]["source"]))
        self.assertEqual(("repository", 60), (rows["shared.codex.timeoutSeconds"]["source"],
                                              rows["shared.codex.timeoutSeconds"]["value"]))
        self.assertEqual(("user", "make user"), (rows["shared.worktreeSetup"]["source"],
                                                 rows["shared.worktreeSetup"]["value"]))

    def test_user_codex_block_is_attributed_to_user(self):
        self.user.write_text(json.dumps({"shared": {"codex": {"crossReview": "off"}}}))
        rows, _ = self._rows()
        self.assertEqual(("off", "user"), (rows["shared.codex.crossReview"]["value"],
                                           rows["shared.codex.crossReview"]["source"]))
        self.assertEqual("default", rows["shared.codex.model"]["source"])

    def test_branch_layer_wins_only_with_backend_git(self):
        self._repo({"specs": {"subjects": {"a": 1}}, "backend": "git"})
        rows, payload = self._rows({"subjects": {"b": 2}, "worktreeSetup": "ignored"})
        self.assertEqual(("branch", {"b": 2}), (rows["specs.subjects"]["source"],
                                                rows["specs.subjects"]["value"]))
        self.assertNotIn("specs.worktreeSetup", rows)
        self.assertEqual("repository", rows["backend"]["source"])
        self.assertTrue(next(l for l in payload["layers"] if l["name"] == "branch")["applies"])

        self._repo({"specs": {"subjects": {"a": 1}}})
        rows, payload = self._rows({"subjects": {"b": 2}})
        self.assertEqual(("repository", {"a": 1}), (rows["specs.subjects"]["source"],
                                                   rows["specs.subjects"]["value"]))
        self.assertFalse(next(l for l in payload["layers"] if l["name"] == "branch")["applies"])

    def test_unreadable_user_file_is_reported_not_fatal(self):
        self.user.write_text("{nope")
        _, payload = self._rows()
        layer = next(l for l in payload["layers"] if l["name"] == "user")
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


if __name__ == "__main__":
    unittest.main()
