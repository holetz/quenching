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
import unittest.mock

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
CQ = str(PLUGIN_ROOT / "assets" / "bin" / "cq")
AUTOPILOT = PLUGIN_ROOT / "skills" / "quenching-specs" / "references" / "autopilot.md"

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

    def _advance_origin(self, branch):
        other = os.path.join(os.path.dirname(self.repo), "other")
        _git(os.path.dirname(self.repo), "clone", "-q", "-b", branch,
             os.path.join(os.path.dirname(self.repo), "origin.git"), other)
        _git(other, "config", "user.email", "t@example.com")
        _git(other, "config", "user.name", "T")
        pathlib.Path(other, "b.txt").write_text("y\n")
        _git(other, "add", "b.txt")
        _git(other, "commit", "-q", "-m", "ahead")
        _git(other, "push", "-q", "origin", branch)

    def test_a_branch_behind_its_remote_still_reaches_it(self):
        _git(self.repo, "push", "-q", "origin", "main")
        self._advance_origin("main")
        code, out = self.run_cq(FAKE_GH_STEPS="1")
        checks = {c["id"]: c for c in out["checks"]}
        self.assertEqual(code, 0, out)
        self.assertEqual(("ok", None), (checks["push"]["status"], checks["push"]["reason"]))

    def test_a_store_behind_its_remote_still_reaches_it(self):
        _git(self.repo, "branch", "quenching", "main")
        self._advance_origin("quenching")
        code, out = self.run_cq(FAKE_GH_STEPS="1")
        checks = {c["id"]: c for c in out["checks"]}
        self.assertEqual(code, 0, out)
        self.assertEqual("ok", checks["store"]["status"])

    def test_the_probe_never_creates_its_ref(self):
        self.run_cq(FAKE_GH_STEPS="1")
        listed = subprocess.run(["git", "ls-remote", "origin", "quenching-preflight-probe"],
                                cwd=self.repo, capture_output=True, text=True, check=True)
        self.assertEqual("", listed.stdout)

    def test_unknown_remote_is_a_refusal(self):
        code, out = self.run_cq("--remote", "nowhere")
        self.assertEqual(code, 2)
        self.assertEqual(out["code"], "git-preflight-remote-unknown")


class AutopilotContract(unittest.TestCase):
    def test_step_one_calls_preflight_and_gates_merges(self):
        body = AUTOPILOT.read_text(encoding="utf-8")
        self.assertIn("cq git preflight", body)
        self.assertIn("mergesAllowed", body)
        self.assertIn("no merges", body)
        self.assertIn("Bash(cq:*)", body)


class PushReason(unittest.TestCase):
    """A failed probe names why: only a refusal or missing credentials is a `fail`."""

    def setUp(self):
        sys.path.insert(0, str(PLUGIN_ROOT / "assets" / "bin"))
        from quenching.git import preflight
        self.preflight = preflight

    def probe(self, code, err):
        with unittest.mock.patch.object(self.preflight, "_tool", return_value=(code, "", err)):
            return self.preflight._dry_push("/r", "origin", "refs/heads/main")

    def test_each_stderr_lands_on_its_reason(self):
        cases = {
            "remote: Permission to o/r.git denied to u.\nfatal: unable to access "
            "'https://github.com/o/r/': The requested URL returned error: 403": ("fail", "read-only"),
            "fatal: could not read Username for 'https://github.com': terminal prompts disabled":
                ("fail", "no-credentials"),
            "git@github.com: Permission denied (publickey).": ("fail", "no-credentials"),
            "fatal: unable to access 'https://x/': Could not resolve host: x": ("unknown", "unreachable"),
            "error: something nobody anticipated": ("unknown", "probe-failed"),
        }
        for err, expected in cases.items():
            with self.subTest(err=err):
                status, _why, reason = self.probe(128, err)
                self.assertEqual(expected, (status, reason))

    def test_a_timeout_is_unreachable_not_a_refusal(self):
        self.assertEqual(("unknown", "unreachable"), self.probe(124, "timed out")[::2])

    def test_the_probe_targets_a_ref_the_remote_lacks_with_force(self):
        with unittest.mock.patch.object(self.preflight, "_tool", return_value=(0, "", "")) as tool:
            self.preflight._dry_push("/r", "origin", "refs/heads/main")
        argv = tool.call_args.args[1:]
        self.assertIn("--force", argv)
        self.assertEqual(f"refs/heads/main:{self.preflight.PROBE_REF}", argv[-1])


class AzurePreflight(unittest.TestCase):
    """On an Azure DevOps origin `ghAuth` probes the `az` PR route and `ci` is not read."""

    def setUp(self):
        sys.path.insert(0, str(PLUGIN_ROOT / "assets" / "bin"))
        from quenching.git import preflight
        self.preflight = preflight

    def test_the_auth_check_reads_az_on_azure(self):
        with unittest.mock.patch.object(self.preflight, "_tool",
                                        return_value=(0, "[]", "")) as tool:
            got = self.preflight._gh_auth("/r", "azure-boards")
        self.assertEqual((got["id"], got["status"]), ("ghAuth", "ok"))
        self.assertEqual(tool.call_args.args[1:5], ("az", "repos", "pr", "list"))

    def test_an_unreachable_az_route_fails(self):
        with unittest.mock.patch.object(self.preflight, "_tool",
                                        return_value=(1, "", "please run az login")):
            self.assertEqual(self.preflight._gh_auth("/r", "azure-boards")["status"], "fail")

    def test_ci_is_unknown_on_azure_and_runs_nothing(self):
        with unittest.mock.patch.object(self.preflight, "_tool") as tool:
            got = self.preflight._ci("/r", "main", "azure-boards")
        tool.assert_not_called()
        self.assertEqual(got["status"], "unknown")


if __name__ == "__main__":
    unittest.main()
