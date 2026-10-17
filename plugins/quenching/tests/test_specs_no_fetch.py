"""`cq specs status --no-fetch` resolves no remote, calls no API and writes no cache."""

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

CQ = pathlib.Path(__file__).resolve().parent.parent / "assets" / "bin" / "cq"


class NoFetch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="quenching-no-fetch-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = os.path.join(self.tmp, "repo")
        self.bin = os.path.join(self.tmp, "bin")
        self.log = os.path.join(self.tmp, "gh.log")
        os.makedirs(self.repo)
        os.makedirs(self.bin)
        gh = os.path.join(self.bin, "gh")
        with open(gh, "w") as handle:
            handle.write(f'#!/bin/sh\necho "$@" >> {self.log}\nexit 1\n')
        os.chmod(gh, 0o755)
        self.env = {**os.environ, "PATH": self.bin + os.pathsep + os.environ["PATH"],
                    "XDG_CACHE_HOME": os.path.join(self.tmp, "cache")}
        subprocess.run(["git", "init", "-q", self.repo], check=True)
        subprocess.run(["git", "-C", self.repo, "remote", "add", "origin",
                        "https://github.com/example/fixture.git"], check=True)

    def status(self):
        run = subprocess.run([sys.executable, str(CQ), "--root", self.repo, "specs", "status",
                              "--spec", "1", "--no-fetch", "--json"],
                             capture_output=True, text=True, env=self.env)
        return run.returncode, json.loads(run.stdout or run.stderr)

    def declare_git(self):
        os.makedirs(os.path.join(self.repo, ".claude"))
        with open(os.path.join(self.repo, ".claude", "quenching.json"), "w") as handle:
            json.dump({"backend": "git"}, handle)

    def test_the_github_backend_refuses_without_the_api_or_a_cache(self):
        code, payload = self.status()
        self.assertEqual(2, code)
        self.assertEqual("sp-no-local-read", payload["code"])
        self.assertFalse(os.path.exists(self.log), "gh was called")
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "cache", "quenching", "github")))

    def test_a_missing_local_ref_is_named_rather_than_an_unknown_id(self):
        self.declare_git()
        code, payload = self.status()
        self.assertEqual(2, code)
        self.assertEqual("sp-no-local-ref", payload["code"])


if __name__ == "__main__":
    unittest.main()
