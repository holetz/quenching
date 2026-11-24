"""`cq doctor` recommends `core.untrackedCache` on Windows and never applies it (spec 386)."""
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
from quenching.common import doctor, gitcache


class UntrackedCache(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = os.path.join(tmp.name, "repo")
        os.makedirs(self.root)
        # The user's own git config must decide nothing here.
        empty = os.path.join(tmp.name, "gitconfig")
        pathlib.Path(empty).write_text("", encoding="utf-8")
        env = mock.patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": empty, "GIT_CONFIG_NOSYSTEM": "1"})
        env.start()
        self.addCleanup(env.stop)

    def git(self, *argv) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", self.root, *argv], capture_output=True, text=True)

    def report(self):
        return gitcache.untracked_cache_report(self.root, platform="nt")

    def test_off_windows_nothing_is_reported(self):
        self.git("init", "-q")
        self.assertIsNone(gitcache.untracked_cache_report(self.root, platform="posix"))

    def test_outside_a_git_work_tree_nothing_is_reported(self):
        self.assertIsNone(self.report())

    def test_an_unset_cache_names_the_command_and_leaves_the_config_alone(self):
        self.git("init", "-q")
        report = self.report()
        self.assertEqual({"enabled": False, "command": "git config core.untrackedCache true"},
                         report)
        self.assertIn("git config core.untrackedCache true", gitcache.untracked_cache_line(report))
        self.assertNotEqual(0, self.git("config", "--get", "core.untrackedCache").returncode)

    def test_an_enabled_cache_prints_no_line(self):
        self.git("init", "-q")
        self.git("config", "core.untrackedCache", "true")
        report = self.report()
        self.assertEqual({"enabled": True, "command": None}, report)
        self.assertIsNone(gitcache.untracked_cache_line(report))

    def test_many_files_turns_it_on_unless_the_key_says_otherwise(self):
        self.git("init", "-q")
        self.git("config", "feature.manyFiles", "true")
        self.assertTrue(self.report()["enabled"])
        self.git("config", "core.untrackedCache", "false")
        self.assertFalse(self.report()["enabled"])

    def test_the_doctor_reports_it_without_changing_its_exit(self):
        self.git("init", "-q")
        os.makedirs(os.path.join(self.root, ".claude"))
        pathlib.Path(self.root, ".claude", "quenching.json").write_text(
            json.dumps({"shared": {"profiles": {"installed": ["components"]}}}), encoding="utf-8")
        real = gitcache.untracked_cache_report
        outputs = {}
        for as_json in (True, False):
            out = io.StringIO()
            with mock.patch.object(doctor, "untracked_cache_report",
                                   side_effect=lambda root: real(root, platform="nt")), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(0, doctor.run(as_json, self.root))
            outputs[as_json] = out.getvalue()
        self.assertEqual({"enabled": False, "command": "git config core.untrackedCache true"},
                         json.loads(outputs[True])["gitCache"])
        self.assertIn("core.untrackedCache is off", outputs[False])
        self.assertIn("(not applied)", outputs[False])
        self.assertNotEqual(0, self.git("config", "--get", "core.untrackedCache").returncode)


if __name__ == "__main__":
    unittest.main()
