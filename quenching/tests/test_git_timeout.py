"""The git timeout: `$QUENCHING_GIT_TIMEOUT_S` overrides the 60 s default, and a timed-out git
says how to raise it."""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

try:
    import _paths  # noqa: F401
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401

from quenching.common import git as common_git

ENV = "QUENCHING_GIT_TIMEOUT_S"


class GitTimeoutValue(unittest.TestCase):
    def test_absent_is_the_default(self):
        with unittest.mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(ENV, None)
            self.assertEqual(common_git.git_timeout_s(), common_git.COMMAND_TIMEOUT_S)
            self.assertEqual(common_git.COMMAND_TIMEOUT_S, 60)

    def test_positive_number_wins(self):
        for raw, want in (("7", 7.0), (" 150 ", 150.0), ("2.5", 2.5)):
            with self.subTest(raw=raw), unittest.mock.patch.dict(os.environ, {ENV: raw}):
                self.assertEqual(common_git.git_timeout_s(), want)

    def test_invalid_falls_back_to_the_default(self):
        for raw in ("", "0", "-5", "abc", "inf", "nan"):
            with self.subTest(raw=raw), unittest.mock.patch.dict(os.environ, {ENV: raw}):
                self.assertEqual(common_git.git_timeout_s(), 60)


class GitTimeoutMessage(unittest.TestCase):
    def test_message_names_the_verb_the_limit_and_the_variable(self):
        argv = ("--no-optional-locks", "-c", "core.fsmonitor=false", "-C", "/x", "fetch", "origin")
        message = common_git.timeout_message(argv, 35)
        self.assertIn("git fetch timed out after 35s", message)
        self.assertIn(f"{ENV}=<seconds>", message)

    def test_git_run_timeout_returns_124_with_the_hint(self):
        expired = subprocess.TimeoutExpired(["git", "fetch"], 3)
        with tempfile.TemporaryDirectory() as tmp, \
                unittest.mock.patch.dict(os.environ, {ENV: "3"}), \
                unittest.mock.patch("subprocess.run", side_effect=expired) as run:
            code, out, err = common_git._git_run(tmp, "fetch", "origin", "refs/heads/main")
        self.assertEqual(run.call_args.kwargs["timeout"], 3.0)
        self.assertEqual((code, out), (124, ""))
        self.assertIn("git fetch timed out after 3s", err)
        self.assertIn(ENV, err)

    def test_git_reads_the_configured_limit(self):
        done = subprocess.CompletedProcess(["git"], 0, "ok\n", "")
        with tempfile.TemporaryDirectory() as tmp, \
                unittest.mock.patch.dict(os.environ, {ENV: "9"}), \
                unittest.mock.patch("subprocess.run", return_value=done) as run:
            self.assertEqual(common_git._git(tmp, "status"), "ok\n")
        self.assertEqual(run.call_args.kwargs["timeout"], 9.0)



class PreflightTimeout(unittest.TestCase):
    def test_probe_timeout_carries_the_hint_and_stays_unreachable(self):
        from quenching.git import preflight
        expired = subprocess.TimeoutExpired(["git", "ls-remote"], 4)
        with tempfile.TemporaryDirectory() as tmp, \
                unittest.mock.patch.dict(os.environ, {ENV: "4"}), \
                unittest.mock.patch("subprocess.run", side_effect=expired) as run:
            code, out, err = preflight._tool(tmp, "git", "ls-remote", "origin")
            gh_code, _gh_out, gh_err = preflight._tool(tmp, "/usr/bin/gh", "auth", "status")
        self.assertEqual(run.call_args.kwargs["timeout"], 4.0)
        self.assertEqual((code, out), (124, ""))
        self.assertIn("git ls-remote timed out after 4s", err)
        self.assertIn(ENV, err)
        self.assertEqual(gh_code, 124)
        self.assertIn("gh auth timed out after 4s", gh_err)
        self.assertEqual(preflight._push_reason(code, err), "unreachable")


if __name__ == "__main__":
    unittest.main()
