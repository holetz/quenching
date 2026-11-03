"""Executable proofs for `cq config host`: the shared.workHost block and its inert plan."""
from __future__ import annotations

import io
import json
import os
import pathlib
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.common.config import USER_CONFIG_ENV
from quenching.config import main
from quenching.config.host import build_plan, load_settings


class WorkHost(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = pathlib.Path(tmp.name) / "repo"
        (self.repo / ".claude").mkdir(parents=True)
        self.user = pathlib.Path(tmp.name) / "user.json"
        patch = mock.patch.dict(os.environ, {USER_CONFIG_ENV: str(self.user)})
        patch.start()
        self.addCleanup(patch.stop)

    def _user(self, block):
        self.user.write_text(json.dumps({"shared": {"workHost": block}}))

    def test_absent_block_is_disabled(self):
        settings, warnings = load_settings(str(self.repo))
        self.assertFalse(settings["enabled"])
        self.assertEqual(warnings, [])

    def test_user_layer_enables_and_repository_wins(self):
        self._user({"target": "gpu@host", "minFreeGb": 5})
        (self.repo / ".claude" / "quenching.json").write_text(
            json.dumps({"shared": {"workHost": {"target": "other"}}}))
        settings, _ = load_settings(str(self.repo))
        self.assertEqual(settings["target"], "other")
        self.assertEqual(settings["minFreeGb"], 10)   # the repository block replaces the user's

    def test_bad_values_warn_and_fall_back(self):
        self._user({"target": "h", "minFreeGb": -1, "pullBack": "x", "bogus": 1})
        settings, warnings = load_settings(str(self.repo))
        self.assertEqual(settings["minFreeGb"], 10)
        self.assertEqual(settings["pullBack"], [])
        self.assertEqual(len(warnings), 3)

    def test_plan_has_checksum_disk_and_pullback(self):
        self._user({"target": "h", "pullBack": ["dist/*"], "minFreeGb": 7})
        settings, _ = load_settings(str(self.repo))
        with mock.patch("subprocess.run") as run:
            steps, notes = build_plan(settings, "proj", ["make", "test"])
            run.assert_not_called()
        names = [s["step"] for s in steps]
        self.assertEqual(names, ["disk", "push", "run", "pull"])
        self.assertIn("--checksum", steps[1]["argv"])
        self.assertIn("-ge 7", steps[0]["argv"][-1])
        self.assertEqual(notes, [])

    def test_plan_warns_when_nothing_comes_back_and_uses_runner(self):
        self._user({"target": "h", "runner": "/bin/remote-run"})
        settings, _ = load_settings(str(self.repo))
        steps, notes = build_plan(settings, "proj", ["make"])
        self.assertEqual(steps[2]["argv"][0], "/bin/remote-run")
        self.assertEqual(len(notes), 1)

    def test_plan_refuses_protected_path_and_disabled(self):
        self._user({"target": "h", "protectedPaths": ["/srv/personal"]})
        settings, _ = load_settings(str(self.repo))
        with self.assertRaises(ValueError):
            build_plan(settings, "p", ["rm", "-rf", "/srv/personal/x"])
        with self.assertRaises(ValueError):
            build_plan({**settings, "enabled": False}, "p", ["ls"])

    def test_cli(self):
        self._user({"target": "h"})
        out = io.StringIO()
        with redirect_stdout(out):
            rc = main(["--root", str(self.repo), "host", "--json"])
        self.assertEqual(rc, 0)
        self.assertTrue(json.loads(out.getvalue())["enabled"])
        out = io.StringIO()
        with redirect_stdout(out):
            rc = main(["--root", str(self.repo), "host", "--plan", "--json", "--", "make", "test"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out.getvalue())["steps"][2]["step"], "run")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--root", str(self.repo), "host", "--plan"]), 2)


if __name__ == "__main__":
    unittest.main()
