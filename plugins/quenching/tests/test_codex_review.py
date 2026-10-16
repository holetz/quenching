"""Executable proofs for `cq codex review`, against a fake `codex` — never the real one."""
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
import time
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
import test_codex_probe as fake  # the fake binary; a module import collects no test twice
from quenching.codex import main
from quenching.codex.config import DEFAULTS
from quenching.codex.review import (NOT_MEASURED, PROMPT_ONLY_RULE, build_argv, measured_tokens,
                                    run_review)


class TheReview(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        (self.tmp / "bin").mkdir()
        fake.write_fake(self.tmp / "bin")
        self.root = self.tmp / "repo"
        self.worktree = self.tmp / "worktree"
        self.root.mkdir()
        self.worktree.mkdir()
        self.prompt = self.tmp / "prompt.md"
        self.prompt.write_text("Revise o diff contra origin/main.\n", encoding="utf-8")
        self.log = self.tmp / "argv.log"
        self.env = {"PATH": str(self.tmp / "bin"), "CODEX_HOME": str(self.tmp / "home"),
                    "FAKE_CODEX_LOG": str(self.log)}
        self.settings = {**DEFAULTS, "timeoutSeconds": 20}

    def review(self, run: str | None = "r1", **settings) -> tuple[dict, int]:
        return run_review(str(self.root), {**self.settings, **settings}, str(self.worktree),
                          str(self.prompt), run, env=self.env)

    def calls(self) -> list:
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()]

    def test_the_argv_is_always_read_only_and_ignores_the_user(self):
        argv = build_argv("m", "/w", "/w/review.md")
        self.assertEqual(["exec", "-s", "read-only", "--ignore-user-config", "--ignore-rules"],
                         argv[:5])
        self.assertEqual("-", argv[-1])
        self.assertNotIn("--ephemeral", argv)
        self.assertIn("model_reasoning_effort=high", argv)

    def test_a_review_writes_the_run_and_measures_tokens(self):
        payload, code = self.review()
        self.assertEqual(0, code)
        self.assertFalse(payload["fallback"])
        run_dir = self.root / ".quenching" / "codex" / "r1"
        self.assertEqual(str(run_dir / "review.md"), payload["reviewPath"])
        self.assertIn("no findings", (run_dir / "review.md").read_text(encoding="utf-8"))
        self.assertTrue((run_dir / "events.jsonl").is_file())
        self.assertEqual({"total_tokens": 4242}, payload["tokens"])

    def test_the_fake_receives_the_fixed_argv_and_the_prompt_on_stdin(self):
        self.review(model="gpt-test")
        argv, stdin = self.calls()
        review_path = str(self.root / ".quenching" / "codex" / "r1" / "review.md")
        self.assertEqual(build_argv("gpt-test", str(self.worktree), review_path), argv)
        self.assertEqual({"stdin": "Revise o diff contra origin/main.\n"}, stdin)

    def test_a_timeout_stops_codex_and_reports_the_fallback(self):
        self.env["FAKE_CODEX_MODE"] = "hang"
        started = time.monotonic()
        payload, code = self.review(timeoutSeconds=1)
        self.assertLess(time.monotonic() - started, 10)
        self.assertEqual(1, code)
        self.assertTrue(payload["timedOut"])
        self.assertTrue(payload["fallback"])
        self.assertIsNone(payload["reviewPath"])
        self.assertEqual(NOT_MEASURED, payload["tokens"])

    def test_a_failing_codex_falls_back(self):
        self.env["FAKE_CODEX_MODE"] = "fail"
        payload, code = self.review()
        self.assertEqual((1, "codex exited 3"), (code, payload["reason"]))

    def test_no_usage_event_is_not_measured(self):
        self.env["FAKE_CODEX_MODE"] = "no-usage"
        payload, code = self.review()
        self.assertEqual((0, NOT_MEASURED), (code, payload["tokens"]))

    def test_unreadable_events_are_not_measured(self):
        events = self.tmp / "events.jsonl"
        events.write_text("not json\n", encoding="utf-8")
        self.assertEqual(NOT_MEASURED, measured_tokens(str(events)))
        self.assertEqual(NOT_MEASURED, measured_tokens(str(self.tmp / "absent.jsonl")))

    def test_refusals(self):
        self.assertEqual("codex-run-name", self.review(run="../x")[0]["code"])
        self.review()
        self.assertEqual("codex-run-exists", self.review()[0]["code"])
        self.prompt.unlink()
        self.assertEqual("codex-prompt-missing", self.review(run="r2")[0]["code"])
        shutil.rmtree(self.worktree)
        self.assertEqual("codex-worktree-missing", self.review(run="r3")[0]["code"])
        self.worktree.mkdir()
        self.prompt.write_text("x", encoding="utf-8")
        self.env["PATH"] = str(self.tmp / "empty")
        payload, code = self.review(run="r4")
        self.assertEqual((2, "codex-missing"), (code, payload["code"]))

    def test_a_default_run_name_is_a_utc_stamp(self):
        payload, _ = self.review(run=None)
        self.assertRegex(payload["run"], r"^\d{8}T\d{6}Z$")

    def run_main(self, argv: list[str]) -> tuple[int, str]:
        buffer = io.StringIO()
        with mock.patch.dict(os.environ, self.env), contextlib.redirect_stdout(buffer):
            code = main(argv)
        return code, buffer.getvalue()

    def test_the_command_line(self):
        base = ["--root", str(self.root), "review", "--worktree", str(self.worktree),
                "--prompt", str(self.prompt)]
        code, out = self.run_main([*base, "--run", "c1"])
        self.assertEqual(0, code)
        self.assertIn("codex review — review written; tokens: 4242", out)
        code, out = self.run_main([*base, "--run", "c1", "--json"])
        self.assertEqual(2, code)
        self.assertEqual("codex-run-exists", json.loads(out)["code"])
        self.env["FAKE_CODEX_MODE"] = "fail"
        code, out = self.run_main([*base, "--run", "c2", "--json"])
        self.assertEqual(1, code)
        self.assertTrue(json.loads(out)["fallback"])


class ThePromptOnlyFallback(unittest.TestCase):
    """The host's sandbox fails, as `bwrap` does where unprivileged user namespaces are denied."""

    calls = TheReview.calls
    run_main = TheReview.run_main

    def setUp(self):
        TheReview.setUp(self)
        self.env["FAKE_CODEX_SANDBOX"] = "bwrap"
        git = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@t", "PATH": os.environ["PATH"], "HOME": str(self.tmp)}

        def run(*args: str) -> None:
            subprocess.run(["git", "-C", str(self.worktree), *args], check=True, env=git,
                           capture_output=True)

        run("init", "-q", "-b", "main")
        (self.worktree / "kept.py").write_text("x = 1\n", encoding="utf-8")
        (self.worktree / "gone.py").write_text("y = 1\n", encoding="utf-8")
        run("add", ".")
        run("commit", "-q", "-m", "base")
        run("tag", "base")
        (self.worktree / "kept.py").write_text("x = 2\n", encoding="utf-8")
        (self.worktree / "gone.py").unlink()
        run("add", "-A")
        run("commit", "-q", "-m", "head")

    def test_the_sandbox_failure_turns_the_review_prompt_only(self):
        payload, code = run_review(str(self.root), self.settings, str(self.worktree),
                                   str(self.prompt), "p1", env=self.env, base="base")
        self.assertEqual((0, "prompt-only"), (code, payload["mode"]))
        self.assertIn("RTM_NEWADDR", payload["sandbox"]["reason"])
        argv, stdin = self.calls()
        self.assertEqual(["exec", "-s", "read-only", "--ignore-user-config", "--ignore-rules"],
                         argv[:5])
        for wider in ("workspace-write", "danger-full-access",
                      "--dangerously-bypass-approvals-and-sandbox"):
            self.assertNotIn(wider, " ".join(argv))
        text = stdin["stdin"]
        self.assertTrue(text.startswith("Revise o diff contra origin/main."))
        self.assertIn(PROMPT_ONLY_RULE, text)
        self.assertIn("-x = 1\n+x = 2", text)
        self.assertIn("## kept.py @ HEAD", text)
        self.assertNotIn("## gone.py @", text)
        prompt_md = self.root / ".quenching" / "codex" / "p1" / "prompt.md"
        self.assertEqual(text, prompt_md.read_text(encoding="utf-8"))

    def test_without_a_base_codex_is_never_called(self):
        payload, code = run_review(str(self.root), self.settings, str(self.worktree),
                                   str(self.prompt), "p2", env=self.env)
        self.assertEqual((1, "unavailable"), (code, payload["mode"]))
        self.assertTrue(payload["fallback"])
        self.assertFalse(self.log.exists())
        self.assertFalse((self.root / ".quenching" / "codex" / "p2").exists())

    def test_an_unreadable_diff_is_a_refusal(self):
        payload, code = run_review(str(self.root), self.settings, str(self.worktree),
                                   str(self.prompt), "p3", env=self.env, base="no-such-ref")
        self.assertEqual((2, "codex-diff-unreadable"), (code, payload["code"]))
        self.assertFalse(self.log.exists())

    def test_a_working_sandbox_stays_sandboxed(self):
        self.env["FAKE_CODEX_SANDBOX"] = "ok"
        payload, code = run_review(str(self.root), self.settings, str(self.worktree),
                                   str(self.prompt), "p4", env=self.env, base="base")
        self.assertEqual((0, "sandboxed"), (code, payload["mode"]))
        self.assertEqual({"stdin": "Revise o diff contra origin/main.\n"}, self.calls()[1])

    def test_the_command_line_takes_base_and_head(self):
        # the fake stays first on PATH; git's own directory is added only so `cq` can diff
        self.env["PATH"] += os.pathsep + os.path.dirname(shutil.which("git"))
        code, out = self.run_main(["--root", str(self.root), "review", "--worktree",
                                   str(self.worktree), "--prompt", str(self.prompt), "--run",
                                   "p5", "--base", "base", "--head", "HEAD", "--json"])
        self.assertEqual((0, "prompt-only"), (code, json.loads(out)["mode"]))


if __name__ == "__main__":
    unittest.main()
