"""Executable proofs for `cq codex implement`, against a fake `codex` in a throwaway git repo.

`PATH` holds only the fake and `git`; the quota is a stub, so no test reaches the real Codex.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.codex import main
from quenching.codex.config import DEFAULTS
from quenching.codex.implement import BYPASS, build_argv, clean_env, run_implement

FAKE = r'''#!/usr/bin/env python3
import json, os, subprocess, sys, time
argv = sys.argv[1:]
with open(os.environ["FAKE_LOG"], "a", encoding="utf-8") as handle:
    handle.write(json.dumps({"argv": argv, "env": sorted(os.environ), "stdin": sys.stdin.read()})
                 + "\n")
if argv[:1] == ["sandbox"]:
    sys.exit(0 if os.environ.get("FAKE_SANDBOX", "ok") == "ok" else 1)
mode = os.environ.get("FAKE_MODE", "write")
cwd = argv[argv.index("-C") + 1]
if mode == "hang":
    time.sleep(30)
if mode in ("write", "stray", "commit"):
    with open(os.path.join(cwd, "src", "a.py"), "a", encoding="utf-8") as handle:
        handle.write("print('codex')\n")
if mode == "stray":
    with open(os.path.join(cwd, "other.py"), "w", encoding="utf-8") as handle:
        handle.write("x\n")
if mode == "commit":
    subprocess.run(["git", "-C", cwd, "commit", "-qam", "codex"], check=True)
print(json.dumps({"type": "turn.completed", "usage": {"input_tokens": 100, "output_tokens": 20}}))
with open(argv[argv.index("-o") + 1], "w", encoding="utf-8") as handle:
    handle.write("feito\n")
sys.exit(3 if mode == "fail" else 0)
'''


class Quota:
    """The probe stub: one snapshot per call, in order."""

    def __init__(self, *used, state="available"):
        self.used, self.state, self.calls = list(used), state, []

    def __call__(self, settings: dict, env=None) -> dict:
        self.calls.append(settings)
        used = self.used.pop(0) if self.used else None
        limits = {"primary": {"usedPercent": used}} if used is not None else {}
        return {"state": self.state, "reason": f"primary {used}%", "rateLimits": limits}


class FakeBackend:
    def __init__(self, tasks):
        self.tasks = tasks

    def read_spec(self, spec_id):
        return {"tasks": self.tasks}, {}


def task(files=("src/a.py",), verify="true") -> dict:
    return {"id": "2.2", "files": list(files), "verify": verify, "checked": False,
            "blocked": False}


class Implement(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        fake = bin_dir / "codex"
        fake.write_text(FAKE.replace("/usr/bin/env python3", sys.executable), encoding="utf-8")
        fake.chmod(0o755)
        os.symlink(shutil.which("git"), bin_dir / "git")
        self.repo = self.tmp / "repo"
        (self.repo / "src").mkdir(parents=True)
        (self.repo / "src" / "a.py").write_text("print('a')\n", encoding="utf-8")
        (self.repo / ".gitignore").write_text(".quenching/\n", encoding="utf-8")
        for cmd in (["init", "-q"], ["add", "."],
                    ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base"]):
            subprocess.run(["git", "-C", str(self.repo), *cmd], check=True)
        self.prompt = self.tmp / "prompt.md"
        self.prompt.write_text("Implemente a tarefa 2.2.\n", encoding="utf-8")
        self.log = self.tmp / "calls.log"
        self.env = {"PATH": str(bin_dir), "FAKE_LOG": str(self.log), "GH_TOKEN": "secret",
                    "AWS_SECRET_ACCESS_KEY": "s", "GIT_AUTHOR_NAME": "t",
                    "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                    "GIT_COMMITTER_EMAIL": "t@t", "HOME": str(self.tmp)}
        self.settings = {**DEFAULTS, "timeoutSeconds": 20, "executor": dict(DEFAULTS["executor"])}
        self.tasks = [task()]

    def implement(self, quota=None, run="r1", **executor):
        self.settings["executor"].update(executor)
        with mock.patch("quenching.codex.implement.open_backend",
                        return_value=(FakeBackend(self.tasks), {})):
            return run_implement(str(self.repo), self.settings, "7", "2.2", str(self.repo),
                                 str(self.prompt), run, env=self.env,
                                 quota=quota or Quota(10, 12))

    def calls(self) -> list:
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()]

    def test_the_default_argv_bypasses_and_never_also_sandboxes(self):
        argv = build_argv(DEFAULTS["executor"], "m", "/w", "/w/m.md")
        self.assertIn(BYPASS, argv)
        self.assertNotIn("-s", argv)
        for flag in ("--ignore-user-config", "--ignore-rules", "--json"):
            self.assertIn(flag, argv)
        self.assertIn("model_reasoning_effort=medium", argv)
        self.assertEqual(argv[argv.index("-C") + 1], "/w")

    def test_the_sandbox_opt_in_replaces_the_bypass(self):
        executor = {**DEFAULTS["executor"], "sandbox": "workspace-write"}
        argv = build_argv(executor, "m", "/w", "/w/m.md", windows=False)
        self.assertNotIn(BYPASS, argv)
        self.assertEqual(argv[argv.index("-s") + 1], "workspace-write")
        windows = build_argv(executor, "m", "/w", "/w/m.md", windows=True)
        self.assertIn('windows.sandbox="unelevated"', windows)

    def test_secrets_never_reach_codex(self):
        env = clean_env({"GH_TOKEN": "1", "GITHUB_TOKEN": "2", "AWS_X": "3", "AZURE_Y": "4",
                         "GOOGLE_Z": "5", "PATH": "/bin"})
        self.assertEqual(env, {"PATH": "/bin"})

    def test_a_write_inside_files_is_reported_with_tokens_and_quota_delta(self):
        payload, code = self.implement()
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload["reason"], "codex wrote the task")
        self.assertEqual(payload["tokens"]["total_tokens"], 120)
        self.assertEqual((payload["quotaBefore"], payload["quotaAfter"]), (10, 12))
        self.assertFalse(payload["stopLoss"])
        call = self.calls()[0]
        self.assertNotIn("GH_TOKEN", call["env"])
        self.assertNotIn("AWS_SECRET_ACCESS_KEY", call["env"])
        self.assertIn("Não rode nenhum comando git", call["stdin"])
        self.assertIn("src/a.py", call["stdin"])

    def test_a_large_quota_jump_trips_the_stop_loss_but_keeps_the_diff(self):
        payload, code = self.implement(quota=Quota(10, 30))
        self.assertEqual(code, 0)
        self.assertEqual(payload["quotaDelta"], 20)
        self.assertTrue(payload["stopLoss"])

    def test_a_write_outside_files_trips_the_guard(self):
        self.env["FAKE_MODE"] = "stray"
        payload, code = self.implement()
        self.assertEqual((code, payload["code"]), (2, "codex-git-guard"))
        self.assertEqual(payload["outside"], ["other.py"])
        self.assertEqual(payload["discard"], ["src/a.py"])

    def test_a_commit_trips_the_guard(self):
        self.env["FAKE_MODE"] = "commit"
        payload, code = self.implement()
        self.assertEqual(code, 2)
        self.assertIn("head", payload["guard"]["moved"])
        self.assertIn("reflogLength", payload["guard"]["moved"])

    def test_a_failing_or_hanging_codex_falls_back(self):
        self.env["FAKE_MODE"] = "fail"
        payload, code = self.implement()
        self.assertEqual((code, payload["reason"]), (1, "codex exited 3"))
        self.env["FAKE_MODE"] = "hang"
        self.settings["timeoutSeconds"] = 1
        payload, code = self.implement(run="r2")
        self.assertEqual(code, 1)
        self.assertTrue(payload["timedOut"])

    def test_an_ineligible_task_never_starts_codex(self):
        self.tasks = [task(files=["docs/x.md"])]
        payload, code = self.implement()
        self.assertEqual(code, 1)
        self.assertIn("docs/", payload["reason"])
        self.assertFalse(self.log.exists())

    def test_the_quota_reserve_blocks_the_dispatch(self):
        payload, code = self.implement(quota=Quota(10, state="unavailable"))
        self.assertEqual(code, 1)
        self.assertFalse(self.log.exists())

    def test_an_unavailable_opt_in_sandbox_falls_back_instead_of_bypassing(self):
        self.env["FAKE_SANDBOX"] = "bwrap"
        payload, code = self.implement(sandbox="workspace-write")
        self.assertEqual(code, 1)
        self.assertIn("workspace-write sandbox is unavailable", payload["reason"])
        self.assertTrue(all(c["argv"][:1] == ["sandbox"] for c in self.calls()))

    def test_a_dirty_tree_outside_files_is_refused(self):
        (self.repo / "loose.txt").write_text("x", encoding="utf-8")
        payload, code = self.implement()
        self.assertEqual((code, payload["code"]), (2, "codex-tree-dirty"))

    def test_the_cli_emits_the_guard_payload_instead_of_a_bare_refusal(self):
        self.env["FAKE_MODE"] = "stray"
        out = io.StringIO()
        with mock.patch("quenching.codex.implement.open_backend",
                        return_value=(FakeBackend(self.tasks), {})), \
                mock.patch("quenching.codex.implement.probe", Quota(10, 12)), \
                mock.patch.dict(os.environ, self.env, clear=True), \
                contextlib.redirect_stdout(out):
            code = main(["implement", "--root", str(self.repo), "--json", "--spec", "7",
                         "--task", "2.2", "--worktree", str(self.repo),
                         "--prompt", str(self.prompt), "--run", "cli"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(out.getvalue())["outside"], ["other.py"])


if __name__ == "__main__":
    unittest.main()
