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
from _tools import WINDOWS, fake_tool, link_tool
from quenching.codex import main
from quenching.codex.config import DEFAULTS
from quenching.codex.guard import GuardError
from quenching.codex.implement import (BYPASS, NOT_MEASURED, build_argv, clean_env,
                                      measured_tokens, run_implement)

FAKE = r'''import json, os, subprocess, sys, time
argv = sys.argv[1:]
with open(os.environ["FAKE_LOG"], "a", encoding="utf-8") as handle:
    handle.write(json.dumps({"argv": argv, "env": sorted(os.environ),
                             "stdin": sys.stdin.buffer.read().decode("utf-8")})
                 + "\n")
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
if mode == "orphan":
    subprocess.run(["git", "-C", cwd, "symbolic-ref", "HEAD", "refs/heads/gone"], check=True)
if mode == "corrupt":
    with open(os.path.join(cwd, "OUTSIDE.py"), "w", encoding="utf-8") as handle:
        handle.write("x\n")
    with open(os.path.join(cwd, ".git", "index"), "wb") as handle:
        handle.write(b"DIRC")
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
        fake_tool(bin_dir, "codex", FAKE)
        path = str(bin_dir)
        if WINDOWS:
            # A bare `git` is searched as `git.exe` only, so a `.cmd` forwarder is never reached:
            # git's own directory joins PATH instead, and it holds no `codex`.
            path += os.pathsep + os.path.dirname(shutil.which("git"))
        else:
            link_tool(bin_dir, "git")
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
        self.env = {"PATH": path, "FAKE_LOG": str(self.log), "GH_TOKEN": "secret",
                    "AWS_SECRET_ACCESS_KEY": "s", "GIT_AUTHOR_NAME": "t",
                    "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                    "GIT_COMMITTER_EMAIL": "t@t", "HOME": str(self.tmp)}
        if WINDOWS:
            # Every Windows process carries these; without them a `.cmd` cannot start its shell.
            self.env.update({k: os.environ[k] for k in ("SystemRoot", "ComSpec") if k in os.environ})
        self.settings = {**DEFAULTS, "timeoutSeconds": 20,
                         "executor": {**DEFAULTS["executor"], "enabled": True}}
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

    def test_the_argv_always_bypasses_and_never_asks_for_a_sandbox(self):
        argv = build_argv(DEFAULTS["executor"], "m", "/w", "/w/m.md")
        self.assertEqual(["exec", BYPASS], argv[:2])
        self.assertNotIn("-s", argv)
        self.assertFalse([a for a in argv if "sandbox" in a and a != BYPASS])
        for flag in ("--ignore-user-config", "--ignore-rules", "--json"):
            self.assertIn(flag, argv)
        self.assertIn("model_reasoning_effort=medium", argv)
        self.assertEqual(argv[argv.index("-C") + 1], "/w")

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
        self.assertIn("other.py", payload["message"])
        self.assertIn("needs-human", payload["message"])
        self.assertIs(False, payload["fallback"])

    def test_a_failing_git_status_after_the_run_fails_closed(self):
        self.env["FAKE_MODE"] = "corrupt"
        payload, code = self.implement()
        self.assertEqual((code, payload["code"]), (2, "codex-git-guard"))
        self.assertIs(True, payload["statusUnreadable"])
        self.assertIs(False, payload["ok"])
        self.assertIs(False, payload["fallback"])
        self.assertNotIn("discard", payload)
        self.assertIn("needs-human", payload["message"])
        self.assertIn("worktree status unreadable", payload["guard"]["moved"][0])

    def test_a_failing_git_status_before_the_run_never_starts_codex(self):
        (self.repo / ".git" / "index").write_bytes(b"DIRC")
        payload, code = self.implement()
        self.assertEqual((code, payload["code"]), (2, "codex-git-guard"))
        self.assertIs(True, payload["statusUnreadable"])
        self.assertNotIn("discard", payload)
        self.assertIn("needs-human", payload["message"])
        self.assertFalse(self.log.exists())

    def test_unreadable_refs_after_the_run_fail_closed(self):
        self.env["FAKE_MODE"] = "orphan"
        payload, code = self.implement()
        self.assertEqual((code, payload["code"]), (2, "codex-git-guard"))
        self.assertIs(True, payload["refsUnreadable"])
        self.assertIs(False, payload["ok"])
        self.assertIs(False, payload["fallback"])
        self.assertNotIn("discard", payload)
        self.assertIn("needs-human", payload["message"])
        self.assertIn("worktree refs unreadable", payload["guard"]["moved"][0])

    def test_unreadable_refs_before_the_run_never_start_codex(self):
        with mock.patch("quenching.codex.implement.refs",
                        side_effect=GuardError("git rev-parse HEAD failed (128): broken")):
            payload, code = self.implement()
        self.assertEqual((code, payload["code"]), (2, "codex-git-guard"))
        self.assertIs(True, payload["refsUnreadable"])
        self.assertNotIn("discard", payload)
        self.assertIn("needs-human", payload["message"])
        self.assertFalse(self.log.exists())
        self.assertFalse((self.repo / ".quenching" / "codex" / "r1").exists())

    def test_a_worktree_outside_git_is_not_a_toplevel(self):
        outside = self.tmp / "plain"
        outside.mkdir()
        with mock.patch("quenching.codex.implement.open_backend",
                        return_value=(FakeBackend(self.tasks), {})):
            payload, code = run_implement(str(self.repo), self.settings, "7", "2.2",
                                          str(outside), str(self.prompt), "r1", env=self.env,
                                          quota=Quota(10, 12))
        self.assertEqual((code, payload["code"]), (2, "codex-worktree-not-toplevel"))
        self.assertFalse(self.log.exists())

    def test_a_commit_trips_the_guard(self):
        self.env["FAKE_MODE"] = "commit"
        payload, code = self.implement()
        self.assertEqual(code, 2)
        self.assertIn("head", payload["guard"]["moved"])
        self.assertIn("reflogLength", payload["guard"]["moved"])
        self.assertEqual(payload["outside"], [])
        self.assertNotIn("needs-human", payload["message"])
        self.assertIs(False, payload["fallback"])

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
        self.tasks = [task(files=["docs/index.md"])]
        payload, code = self.implement()
        self.assertEqual(code, 1)
        self.assertIn("docs/", payload["reason"])
        self.assertFalse(self.log.exists())

    def test_a_protected_verified_task_dispatches_the_small_tier_eligible_reports(self):
        self.tasks = [task(verify="make test")]
        payload, code = self.implement(maxTaskTokens=0)
        self.assertEqual(code, 0, payload)
        small_tier = DEFAULTS["executor"]["modelSmallTier"]
        self.assertEqual((payload["class"], payload["model"]), ("verified", small_tier))
        argv = self.calls()[0]["argv"]
        self.assertEqual(argv[argv.index("-m") + 1], small_tier)

    def test_the_quota_reserve_blocks_the_dispatch(self):
        payload, code = self.implement(quota=Quota(10, state="unavailable"))
        self.assertEqual(code, 1)
        self.assertFalse(self.log.exists())

    def test_codex_is_the_only_process_started(self):
        self.implement()
        self.assertEqual([["exec", BYPASS]], [c["argv"][:2] for c in self.calls()])

    def test_a_dotted_files_entry_matches_the_path_git_status_reports(self):
        self.tasks = [task(files=("./src/a.py",))]
        (self.repo / "src" / "a.py").write_text("print('dirty')\n", encoding="utf-8")
        payload, code = self.implement()
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload["reason"], "codex wrote the task")
        self.assertEqual(payload["files"], ["src/a.py"])
        self.assertFalse(payload.get("outside"))

    def test_a_dirty_tree_outside_files_is_refused(self):
        (self.repo / "loose.txt").write_text("x", encoding="utf-8")
        payload, code = self.implement()
        self.assertEqual((code, payload["code"]), (2, "codex-tree-dirty"))
        self.assertIn("loose.txt", payload["message"])
        self.assertIn("needs-human", payload["message"])

    def test_the_cli_emits_the_guard_payload_instead_of_a_bare_refusal(self):
        self.env["FAKE_MODE"] = "stray"
        out = io.StringIO()
        with mock.patch("quenching.codex.implement.open_backend",
                        return_value=(FakeBackend(self.tasks), {})), \
                mock.patch("quenching.codex.implement.probe", Quota(10, 12)), \
                mock.patch("quenching.codex.load_settings", return_value=(self.settings, [])), \
                mock.patch.dict(os.environ, self.env, clear=True), \
                contextlib.redirect_stdout(out):
            code = main(["implement", "--root", str(self.repo), "--json", "--spec", "7",
                         "--task", "2.2", "--worktree", str(self.repo),
                         "--prompt", str(self.prompt), "--run", "cli"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(out.getvalue())["outside"], ["other.py"])


class TheTokens(unittest.TestCase):
    """`measured_tokens` reads what `codex exec --json` printed, and never guesses."""

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_unreadable_events_are_not_measured(self):
        events = self.tmp / "events.jsonl"
        events.write_text("not json\n", encoding="utf-8")
        self.assertEqual(NOT_MEASURED, measured_tokens(str(events)))
        self.assertEqual(NOT_MEASURED, measured_tokens(str(self.tmp / "absent.jsonl")))

    def test_turn_completed_usage_is_measured(self):
        events = pathlib.Path(__file__).resolve().parent / "fixtures" / "codex" / \
            "events-turn-completed.jsonl"
        self.assertEqual({"input_tokens": 24763, "cached_input_tokens": 24448,
                          "output_tokens": 122, "total_tokens": 24885},
                         measured_tokens(str(events)))

    def test_every_turn_completed_is_summed_over_the_rollout_format(self):
        events = self.tmp / "events.jsonl"
        events.write_text("\n".join(json.dumps(e) for e in [
            {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 7}}},
            {"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 2}},
            {"type": "turn.completed", "usage": {"input_tokens": 5, "output_tokens": 1}}]) + "\n",
                          encoding="utf-8")
        self.assertEqual({"input_tokens": 15, "output_tokens": 3, "total_tokens": 18},
                         measured_tokens(str(events)))

    def test_the_rollout_format_alone_keeps_its_last_total(self):
        events = self.tmp / "events.jsonl"
        events.write_text("\n".join(json.dumps(e) for e in [
            {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 7}}},
            {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 9}}}]) + "\n",
                          encoding="utf-8")
        self.assertEqual({"total_tokens": 9}, measured_tokens(str(events)))


class TheReviewIsGone(unittest.TestCase):
    def test_cq_codex_review_is_not_a_command(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            main(["review", "--worktree", ".", "--prompt", "p.md"])
        self.assertEqual(2, raised.exception.code)


if __name__ == "__main__":
    unittest.main()
