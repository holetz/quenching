"""`cq git preflight` against a throwaway repo with a bare origin and a fake `gh` on PATH."""
from __future__ import annotations

import json
import os
import pathlib
import stat
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
CQ = str(PLUGIN_ROOT / "assets" / "bin" / "cq")
AUTOPILOT = PLUGIN_ROOT / "commands" / "specs" / "autopilot.md"

FAKE_GH = """#!/bin/sh
case "$1 $2" in
  "auth status") exit ${FAKE_GH_AUTH:-0} ;;
  "run list") echo '[{"databaseId": 7, "status": "completed", "conclusion": "failure"}]' ;;
  "run view") if [ "$FAKE_GH_STEPS" = "1" ]; then
      echo '{"jobs": [{"steps": [{"name": "build"}]}]}'; else echo '{"jobs": [{"steps": []}]}'; fi ;;
  *) exit 1 ;;
esac
"""


def _git(cwd, *argv):
    subprocess.run(["git", *argv], cwd=cwd, check=True, capture_output=True, text=True)


class Preflight(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = pathlib.Path(tmp.name)
        self.repo = str(root / "repo")
        bare = str(root / "origin.git")
        os.makedirs(self.repo)
        _git(self.repo, "init", "-q", "-b", "main")
        _git(self.repo, "config", "user.email", "t@example.com")
        _git(self.repo, "config", "user.name", "T")
        (root / "repo" / "a.txt").write_text("x\n")
        _git(self.repo, "add", "a.txt")
        _git(self.repo, "commit", "-q", "-m", "init")
        _git(str(root), "init", "-q", "--bare", bare)
        _git(self.repo, "remote", "add", "origin", bare)
        _git(self.repo, "push", "-q", "origin", "main:quenching")
        gh_dir = root / "bin"
        gh_dir.mkdir()
        gh = gh_dir / "gh"
        gh.write_text(FAKE_GH)
        gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
        self.path = f"{gh_dir}{os.pathsep}{os.environ['PATH']}"

    def run_cq(self, *argv, **env):
        proc = subprocess.run([sys.executable, CQ, "git", "preflight", *argv, "--json"],
                              cwd=self.repo, capture_output=True, text=True,
                              env={**os.environ, "PATH": self.path, **env})
        return proc.returncode, json.loads(proc.stdout)

    def test_green_when_ci_ran_steps(self):
        code, out = self.run_cq(FAKE_GH_STEPS="1")
        self.assertEqual(code, 0, out)
        ids = {c["id"]: c["status"] for c in out["checks"]}
        self.assertEqual(ids, {"store": "ok", "types": "skipped", "push": "ok",
                               "ghAuth": "ok", "ci": "ok"})
        self.assertTrue(out["mergesAllowed"])
        self.assertIs(out["checks"][2]["noVerify"], False)

    def test_ci_without_steps_is_unavailable_and_blocks_merges(self):
        code, out = self.run_cq(FAKE_GH_STEPS="0")
        self.assertEqual(code, 1)
        self.assertEqual(out["failed"], ["ci"])
        self.assertFalse(out["mergesAllowed"])
        self.assertFalse(out["plannedMerges"])

    def test_gh_not_authenticated_fails(self):
        code, out = self.run_cq(FAKE_GH_STEPS="1", FAKE_GH_AUTH="1")
        self.assertEqual(code, 1)
        self.assertEqual(out["failed"], ["ghAuth"])

    def test_unknown_remote_is_a_refusal(self):
        code, out = self.run_cq("--remote", "nowhere")
        self.assertEqual(code, 2)
        self.assertEqual(out["code"], "git-preflight-remote-unknown")


if __name__ == "__main__":
    unittest.main()
