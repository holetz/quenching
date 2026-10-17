"""The shared optional-leaf reader and the keys that ride on it: default, valid, invalid."""
from __future__ import annotations

import contextlib
import io
import json
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
from quenching.common.config import setting
from quenching.knowledge import config as okf
from quenching.session.commands.context import BUDGETS, effective_budgets
from quenching.specs import portal as portal_mod
from quenching.specs.commands import estimate as estimate_mod

POSITIVE = lambda v: isinstance(v, int) and not isinstance(v, bool) and v > 0  # noqa: E731


def repo(document=None) -> str:
    tmp = tempfile.TemporaryDirectory()
    root = pathlib.Path(tmp.name)
    (root / ".claude").mkdir()
    if document is not None:
        (root / ".claude" / "quenching.json").write_text(json.dumps(document), encoding="utf-8")
    repo.keep.append(tmp)
    return str(root)


repo.keep = []


class SettingTests(unittest.TestCase):
    def test_absent_valid_invalid(self):
        self.assertEqual((7, None), setting(repo(), "shared", "a.b", 7, POSITIVE))
        self.assertEqual((9, None), setting(repo({"shared": {"a": {"b": 9}}}), "shared", "a.b", 7, POSITIVE))
        value, warning = setting(repo({"shared": {"a": {"b": "x"}}}), "shared", "a.b", 7, POSITIVE)
        self.assertEqual(7, value)
        self.assertIn("shared.a.b", warning)

    def test_block_that_is_not_an_object_warns(self):
        value, warning = setting(repo({"shared": {"a": 3}}), "shared", "a.b", 7, POSITIVE)
        self.assertEqual(7, value)
        self.assertTrue(warning)


class OkfValidateTests(unittest.TestCase):
    def test_precedence_over_hooks_config(self):
        root = repo({"shared": {"okfValidate": {"warnAsError": True, "ignoreGlobs": 5}}})
        hooks = pathlib.Path(root, ".claude", "hooks")
        hooks.mkdir()
        (hooks / "hooks-config.json").write_text(json.dumps(
            {"okfValidate": {"warnAsError": False, "ignoreGlobs": ["x/"]}}), encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()) as err:
            cfg = okf._load_config(root)
        self.assertTrue(cfg["warnAsError"])
        self.assertEqual(["x/"], cfg["ignoreGlobs"])
        self.assertIn("ignoreGlobs", err.getvalue())

    def test_defaults(self):
        self.assertEqual(okf.DEFAULTS, okf._load_config(repo()))


class BudgetTests(unittest.TestCase):
    def test_defaults_and_override(self):
        self.assertEqual(BUDGETS, effective_budgets(repo()))
        root = repo({"shared": {"contextBudgets": {"worker": 50000, "main": -1}}})
        with contextlib.redirect_stderr(io.StringIO()) as err:
            got = effective_budgets(root)
        self.assertEqual({**BUDGETS, "worker": 50000}, got)
        self.assertIn("contextBudgets.main", err.getvalue())

    def test_estimate_default_is_resolved_at_runtime(self):
        args = mock.Mock(worker_budget=None, json=True)
        out = mock.Mock()
        root = repo({"shared": {"contextBudgets": {"worker": 1234}}})
        with mock.patch.object(estimate_mod, "open_backend", return_value=(None, {"code": "stop"})):
            estimate_mod.cmd_estimate(args, root, out)
        self.assertEqual(1234, args.worker_budget)


class ChatTests(unittest.TestCase):
    def test_defaults_valid_invalid(self):
        self.assertEqual({"model": "sonnet", "budgetUsd": 0.5, "timeoutSeconds": 300.0},
                         portal_mod.chat_settings(repo()))
        root = repo({"specs": {"chat": {"model": "opus", "budgetUsd": 1.25, "timeoutSeconds": 0}}})
        with contextlib.redirect_stderr(io.StringIO()) as err:
            got = portal_mod.chat_settings(root)
        self.assertEqual({"model": "opus", "budgetUsd": 1.25, "timeoutSeconds": 300.0}, got)
        self.assertIn("chat.timeoutSeconds", err.getvalue())


if __name__ == "__main__":
    unittest.main()
