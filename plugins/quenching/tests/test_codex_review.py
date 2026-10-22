"""Executable proofs for `cq codex review`, against a fake `codex` — never the real one."""
from __future__ import annotations

import contextlib
import io
import json
import ntpath
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
from quenching.codex.guard import BYPASS, GuardError, refs, run_skip, strict_refs, tree
from quenching.codex.review import NOT_MEASURED, RULE, build_argv, measured_tokens, run_review

GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t"}


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
        git = {**GIT_ENV, "PATH": os.environ["PATH"], "HOME": str(self.tmp)}
        for args in (["init", "-q", "-b", "main"], ["add", "."], ["commit", "-q", "-m", "base"]):
            if args[0] == "add":
                (self.worktree / "kept.py").write_text("x = 1\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(self.worktree), *args], check=True, env=git,
                           capture_output=True)
        self.prompt = self.tmp / "prompt.md"
        self.prompt.write_text("Revise o diff contra origin/main.\n", encoding="utf-8")
        self.log = self.tmp / "argv.log"
        self.env = {"PATH": str(self.tmp / "bin"), "CODEX_HOME": str(self.tmp / "home"),
                    "FAKE_CODEX_LOG": str(self.log)}
        self.settings = {**DEFAULTS, "timeoutSeconds": 20}

    def review(self, run: str | None = "r1", root: pathlib.Path | None = None,
               **settings) -> tuple[dict, int]:
        return run_review(str(root or self.root), {**self.settings, **settings},
                          str(self.worktree), str(self.prompt), run, env=self.env)

    def calls(self) -> list:
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()]

    def test_the_argv_bypasses_the_sandbox_and_ignores_the_user(self):
        argv = build_argv("m", "/w", "/w/review.md")
        self.assertEqual(["exec", BYPASS, "--ignore-user-config", "--ignore-rules"], argv[:4])
        self.assertNotIn("-s", argv)
        self.assertEqual("-", argv[-1])
        self.assertNotIn("--ephemeral", argv)
        self.assertIn("model_reasoning_effort=high", argv)

    def test_a_review_writes_the_run_and_measures_tokens(self):
        payload, code = self.review()
        self.assertEqual(0, code, payload)
        self.assertFalse(payload["fallback"])
        self.assertIsNone(payload["guard"])
        run_dir = self.root / ".quenching" / "codex" / "r1"
        self.assertEqual(str(run_dir / "review.md"), payload["reviewPath"])
        self.assertIn("no findings", (run_dir / "review.md").read_text(encoding="utf-8"))
        self.assertTrue((run_dir / "events.jsonl").is_file())
        self.assertEqual({"total_tokens": 4242}, payload["tokens"])

    def test_the_fake_receives_the_fixed_argv_and_the_prompt_with_the_rule(self):
        self.review(model="gpt-test")
        argv, stdin = self.calls()
        review_path = str(self.root / ".quenching" / "codex" / "r1" / "review.md")
        self.assertEqual(build_argv("gpt-test", str(self.worktree.resolve()), review_path), argv)
        expected = f"Revise o diff contra origin/main.\n\n{RULE}\n"
        self.assertEqual({"stdin": expected}, stdin)
        prompt_md = self.root / ".quenching" / "codex" / "r1" / "prompt.md"
        self.assertEqual(expected, prompt_md.read_text(encoding="utf-8"))

    def test_secrets_never_reach_codex(self):
        self.env.update({"GH_TOKEN": "s", "GITHUB_TOKEN": "s", "AWS_SECRET_ACCESS_KEY": "s",
                         "FAKE_CODEX_MODE": "env"})
        payload, code = self.review()
        self.assertEqual(0, code)
        seen = pathlib.Path(payload["reviewPath"]).read_text(encoding="utf-8")
        for secret in ("GH_TOKEN", "GITHUB_TOKEN", "AWS_SECRET_ACCESS_KEY"):
            self.assertNotIn(f'"{secret}"', seen)
        self.assertIn('"PATH"', seen)

    def test_a_new_file_trips_the_guard(self):
        self.env["FAKE_CODEX_MODE"] = "write"
        payload, code = self.review()
        self.assertEqual((2, "codex-git-guard"), (code, payload["code"]))
        self.assertEqual(["stray.txt"], payload["changed"])
        self.assertIn("stray.txt", payload["message"])
        self.assertIn("human", payload["message"])

    def test_an_edit_to_an_already_dirty_file_trips_the_guard(self):
        (self.worktree / "kept.py").write_text("x = 2\n", encoding="utf-8")
        self.env["FAKE_CODEX_MODE"] = "edit"
        payload, code = self.review()
        self.assertEqual((2, ["kept.py"]), (code, payload["changed"]))

    def test_a_commit_trips_the_guard(self):
        self.env.update({**GIT_ENV, "FAKE_CODEX_MODE": "commit", "HOME": str(self.tmp)})
        self.env["PATH"] += os.pathsep + os.path.dirname(shutil.which("git"))
        payload, code = self.review()
        self.assertEqual(2, code)
        self.assertIn("head", payload["guard"]["moved"])
        self.assertEqual([], payload["changed"])

    def guarded(self, mode: str, run: str = "r1") -> tuple[dict, int]:
        self.env.update({**GIT_ENV, "FAKE_CODEX_MODE": mode, "HOME": str(self.tmp)})
        self.env["PATH"] += os.pathsep + os.path.dirname(shutil.which("git"))
        return self.review(run=run)

    def commit_ignore(self, rules: str) -> None:
        (self.worktree / ".gitignore").write_text(rules, encoding="utf-8")
        env = {**GIT_ENV, "PATH": os.environ["PATH"], "HOME": str(self.tmp)}
        for args in (["add", "."], ["commit", "-q", "-m", "ignore"]):
            subprocess.run(["git", "-C", str(self.worktree), *args], check=True, env=env,
                           capture_output=True)

    def test_a_new_branch_trips_the_guard(self):
        payload, code = self.guarded("branch")
        self.assertEqual((2, "codex-git-guard"), (code, payload["code"]))
        self.assertIn("allRefs", payload["guard"]["moved"])

    def test_a_new_tag_trips_the_guard(self):
        payload, code = self.guarded("tag")
        self.assertEqual((2, "codex-git-guard"), (code, payload["code"]))
        self.assertIn("allRefs", payload["guard"]["moved"])

    def test_a_swapped_index_blob_trips_the_guard(self):
        env = {**GIT_ENV, "PATH": os.environ["PATH"], "HOME": str(self.tmp)}
        (self.worktree / "kept.py").write_text("x = 5\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.worktree), "add", "kept.py"], check=True, env=env)
        (self.worktree / "kept.py").write_text("x = 9\n", encoding="utf-8")  # status stays MM
        payload, code = self.guarded("index")
        self.assertEqual((2, "codex-git-guard"), (code, payload["code"]))
        self.assertIn("index", payload["guard"]["moved"])
        self.assertEqual([], payload["changed"])

    def test_a_local_settings_file_ignored_by_git_trips_the_guard(self):
        self.commit_ignore("settings.local.json\n")
        payload, code = self.guarded("ignored")
        self.assertEqual((2, "codex-git-guard"), (code, payload["code"]))
        self.assertEqual([".claude/settings.local.json"], payload["changed"])

    def test_an_unrelated_ignored_file_is_not_a_change(self):
        self.commit_ignore("cache/\n")
        (self.worktree / "cache").mkdir()
        (self.worktree / "cache" / "x.pyc").write_text("1", encoding="utf-8")
        payload, code = self.review()
        self.assertEqual(0, code, payload)

    def test_a_git_that_fails_after_the_run_fails_closed(self):
        payload, code = self.guarded("break-index")
        self.assertEqual((2, "codex-git-guard"), (code, payload["code"]))
        self.assertIn("cannot read the tree after", payload["message"])

    def test_an_unreadable_file_after_the_run_fails_closed(self):
        self.env.update({**GIT_ENV, "FAKE_CODEX_MODE": "unreadable", "HOME": str(self.tmp)})
        self.addCleanup(lambda: os.path.exists(self.worktree / "unreadable.txt")
                        and os.chmod(self.worktree / "unreadable.txt", 0o644))
        code, out = self.cli_review("unreadable", "--json")
        payload = json.loads(out)
        self.assertEqual((2, "codex-git-guard"), (code, payload["code"]))
        self.assertIn("cannot read the tree after", payload["message"])

    def test_every_exit_2_guard_refusal_says_there_is_no_fallback(self):
        self.env["FAKE_CODEX_MODE"] = "write"
        changed, code = self.review("changed")
        self.assertEqual((2, "codex-git-guard"), (code, changed["code"]))
        git_failed, code = self.guarded("break-index")
        self.assertEqual((2, "codex-git-guard"), (code, git_failed["code"]))
        path = self.worktree / "unreadable.txt"
        path.write_text("x\n", encoding="utf-8")
        os.chmod(path, 0)
        self.addCleanup(os.chmod, path, 0o644)
        unreadable, code = self.review("unreadable")
        self.assertEqual((2, "codex-git-guard"), (code, unreadable["code"]))
        for payload in (changed, git_failed, unreadable):
            self.assertIs(False, payload.get("fallback"), payload["message"])

    def test_an_unreadable_file_before_the_run_fails_closed_and_removes_the_run_dir(self):
        path = self.worktree / "unreadable.txt"
        path.write_text("x\n", encoding="utf-8")
        os.chmod(path, 0)
        self.addCleanup(os.chmod, path, 0o644)
        code, out = self.cli_review("early", "--json")
        self.assertEqual((2, "codex-git-guard"), (code, json.loads(out)["code"]))
        self.assertFalse((self.root / ".quenching" / "codex" / "early").exists())
        self.assertFalse(self.log.exists())

    def test_a_git_that_fails_before_the_run_refuses(self):
        os.chmod(self.worktree / ".git" / "index", 0)
        self.addCleanup(os.chmod, self.worktree / ".git" / "index", 0o644)
        payload, code = self.review()
        self.assertEqual((2, "codex-git-guard"), (code, payload["code"]))
        self.assertIn("before the run", payload["message"])
        self.assertFalse(self.log.exists())

    def git(self, *args: str) -> None:
        env = {**GIT_ENV, "PATH": os.environ["PATH"], "HOME": str(self.tmp)}
        subprocess.run(["git", "-C", str(self.worktree), *args], check=True, env=env,
                       capture_output=True)

    def snap(self) -> dict:
        return {**refs(str(self.worktree), strict=True), **strict_refs(str(self.worktree)),
                "tree": tree(str(self.worktree))}

    def test_refs_reads_strictly_and_a_failing_reflog_is_not_zero(self):
        real = subprocess.run

        def broken(argv, *a, **kw):
            if "reflog" in argv:
                return subprocess.CompletedProcess(argv, 128, "", "fatal: bad reflog")
            return real(argv, *a, **kw)

        with mock.patch("quenching.codex.guard.subprocess.run", broken):
            with self.assertRaises(GuardError):
                refs(str(self.worktree), strict=True)
            self.assertEqual(0, refs(str(self.worktree))["reflogLength"])

    def test_a_detached_head_and_no_stash_are_state_not_failure(self):
        self.git("checkout", "-q", "--detach")
        state = refs(str(self.worktree), strict=True)
        self.assertEqual(("", ""), (state["branch"], state["stash"]))

    def test_an_edit_behind_assume_unchanged_or_skip_worktree_changes_the_snapshot(self):
        for flag, undo in (("--assume-unchanged", "--no-assume-unchanged"),
                           ("--skip-worktree", "--no-skip-worktree")):
            with self.subTest(flag=flag):
                self.git("update-index", flag, "kept.py")
                before = self.snap()
                (self.worktree / "kept.py").write_text(f"x = {flag}\n", encoding="utf-8")
                self.assertNotEqual(before, self.snap())
                self.git("update-index", undo, "kept.py")
                (self.worktree / "kept.py").write_text("x = 1\n", encoding="utf-8")

    def test_marking_a_file_assume_unchanged_changes_the_snapshot(self):
        before = self.snap()
        self.git("update-index", "--assume-unchanged", "kept.py")
        self.assertNotEqual(before, self.snap())

    def test_retargeting_an_ignored_symlink_changes_the_snapshot(self):
        self.commit_ignore(".claude/skills/\n")
        link = self.worktree / ".claude" / "skills" / "foo"
        link.parent.mkdir(parents=True)
        os.symlink("/one", link)
        before = self.snap()
        self.assertIn(".claude/skills/foo", before["tree"])
        link.unlink()
        os.symlink("/two", link)
        self.assertNotEqual(before, self.snap())

    def test_writing_through_an_ignored_symlink_changes_the_snapshot(self):
        self.commit_ignore(".claude/skills/\ncache/\n")
        target = self.worktree / "cache" / "real.json"
        target.parent.mkdir(parents=True)
        target.write_text("one", encoding="utf-8")
        link = self.worktree / ".claude" / "skills" / "foo"
        link.parent.mkdir(parents=True)
        os.symlink(target, link)
        before = self.snap()
        target.write_text("two", encoding="utf-8")
        self.assertNotEqual(before, self.snap())

    def test_writing_through_a_tracked_symlink_changes_the_snapshot(self):
        self.commit_ignore("cache/\n")
        target = self.worktree / "cache" / "config.json"
        target.parent.mkdir(parents=True)
        target.write_text("one", encoding="utf-8")
        os.symlink("cache/config.json", self.worktree / "link.json")
        self.git("add", "link.json")
        self.git("commit", "-q", "-m", "link")
        before = self.snap()
        self.assertIn("link.json", before["tree"])
        target.write_text("two", encoding="utf-8")
        self.assertNotEqual(before, self.snap())

    def test_writing_through_an_ignored_symlink_outside_local_config_changes_the_snapshot(self):
        self.commit_ignore("link.txt\n")
        target = self.tmp / "outside.txt"
        target.write_text("one", encoding="utf-8")
        os.symlink(target, self.worktree / "link.txt")
        before = self.snap()
        self.assertIn("link.txt", before["tree"])
        target.write_text("two", encoding="utf-8")
        self.assertNotEqual(before, self.snap())

    def test_the_run_dir_inside_the_worktree_is_not_a_change(self):
        payload, code = self.review(root=self.worktree)
        self.assertEqual(0, code, payload)
        self.assertTrue((self.worktree / ".quenching" / "codex" / "r1" / "review.md").is_file())

    def test_a_backslash_skip_still_hides_the_run_dir(self):
        out = self.worktree / ".quenching" / "codex" / "r1"
        out.mkdir(parents=True)
        (out / "review.md").write_text("ok", encoding="utf-8")
        skip = run_skip(ntpath.join(str(self.worktree), ".quenching", "codex", "r1"),
                        str(self.worktree), ntpath)
        self.assertEqual(".quenching/codex/r1", skip)
        self.assertNotIn(".quenching/codex/r1/review.md", tree(str(self.worktree), skip))
        self.assertIn(".quenching/codex/r1/review.md", tree(str(self.worktree), None))
        raw = ntpath.join(".quenching", "codex", "r1")
        with mock.patch("os.sep", "\\"):  # as on Windows
            self.assertNotIn(".quenching/codex/r1/review.md", tree(str(self.worktree), raw))

    def test_a_run_dir_on_another_drive_has_no_skip_and_does_not_raise(self):
        self.assertIsNone(run_skip("C:\\repo\\.quenching\\codex\\r1", "D:\\worktree", ntpath))
        self.assertIsNone(run_skip("D:\\other\\r1", "D:\\worktree", ntpath))

    def test_a_cross_drive_run_dir_does_not_break_the_review(self):
        with mock.patch("os.path.relpath", side_effect=ValueError("path is on mount 'C:'")):
            payload, code = self.review()
        self.assertEqual(0, code, payload)

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

    def test_refusals(self):
        self.assertEqual("codex-run-name", self.review(run="../x")[0]["code"])
        self.review()
        self.assertEqual("codex-run-exists", self.review()[0]["code"])
        self.prompt.unlink()
        self.assertEqual("codex-prompt-missing", self.review(run="r2")[0]["code"])
        self.prompt.write_text("x", encoding="utf-8")
        self.env["PATH"] = str(self.tmp / "empty")
        payload, code = self.review(run="r4")
        self.assertEqual((2, "codex-missing"), (code, payload["code"]))
        shutil.rmtree(self.worktree)
        self.assertEqual("codex-worktree-missing", self.review(run="r3")[0]["code"])
        self.worktree.mkdir()
        payload, code = self.review(run="r5")
        self.assertEqual((2, "codex-worktree-not-git"), (code, payload["code"]))

    def test_a_default_run_name_is_a_utc_stamp(self):
        payload, _ = self.review(run=None)
        self.assertRegex(payload["run"], r"^\d{8}T\d{6}Z$")

    def run_main(self, argv: list[str]) -> tuple[int, str]:
        # the fake stays first on PATH; git's own directory follows, as the guard reads git
        env = {**self.env, "PATH": self.env["PATH"] + os.pathsep
               + os.path.dirname(shutil.which("git"))}
        buffer = io.StringIO()
        with mock.patch.dict(os.environ, env), contextlib.redirect_stdout(buffer):
            code = main(argv)
        return code, buffer.getvalue()

    def cli_review(self, run: str, *flags: str) -> tuple[int, str]:
        return self.run_main(["--root", str(self.root), "review", "--worktree",
                              str(self.worktree), "--prompt", str(self.prompt), "--run", run,
                              *flags])

    def test_the_cli_exits_2_when_git_fails_after_the_run(self):
        self.env.update({**GIT_ENV, "FAKE_CODEX_MODE": "break-index", "HOME": str(self.tmp)})
        code, out = self.cli_review("after", "--json")
        payload = json.loads(out)
        self.assertEqual((2, "codex-git-guard"), (code, payload["code"]))
        self.assertIn("cannot read the tree after", payload["message"])

    def test_the_cli_exits_2_when_git_fails_before_the_run(self):
        os.chmod(self.worktree / ".git" / "index", 0)
        self.addCleanup(os.chmod, self.worktree / ".git" / "index", 0o644)
        code, out = self.cli_review("before")
        self.assertEqual(2, code, out)
        self.assertIn("git guard", out)
        code, out = self.cli_review("before2", "--json")
        self.assertEqual((2, "codex-git-guard"), (code, json.loads(out)["code"]))

    def test_the_cli_exits_2_when_the_review_changed_the_tree(self):
        self.env["FAKE_CODEX_MODE"] = "write"
        code, out = self.cli_review("changed", "--json")
        self.assertEqual((2, "codex-git-guard"), (code, json.loads(out)["code"]))

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
        self.assertTrue(json.loads(out)["findingsNeedReproduction"])

    def test_the_cli_emits_the_guard_payload_instead_of_a_bare_refusal(self):
        self.env["FAKE_CODEX_MODE"] = "write"
        code, out = self.run_main(["--root", str(self.root), "review", "--worktree",
                                   str(self.worktree), "--prompt", str(self.prompt),
                                   "--run", "g1", "--json"])
        self.assertEqual(2, code)
        self.assertEqual(["stray.txt"], json.loads(out)["changed"])

    def test_base_and_head_are_gone(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            main(["--root", str(self.root), "review", "--worktree", str(self.worktree),
                  "--prompt", str(self.prompt), "--base", "main"])


if __name__ == "__main__":
    unittest.main()
