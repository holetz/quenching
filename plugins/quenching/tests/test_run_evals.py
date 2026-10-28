"""The eval runner provisions a fixture, records every arm, and grades only on quoted evidence."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

import _paths  # noqa: F401

REPO = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("run_evals", REPO / "scripts/run_evals.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

AGENT = """import os, pathlib, subprocess, sys
pathlib.Path("made.txt").write_text("hello\\n")
pathlib.Path("kept.txt").write_text("COMMITTED CONTENT\\n")
subprocess.run(["git", "add", "kept.txt"], check=True)
subprocess.run(["git", "commit", "-q", "-m", "keep"], check=True)
print("AGENT DONE for: " + sys.argv[-1][:20])
print("CQ=" + os.environ.get("CQ", "<absent>"))
"""
SLEEPER = "import time; print('started', flush=True); time.sleep(5)\n"
GRADER = """import json
print("Here are the grades:")
print(json.dumps([
    {"assertion": "the agent reports it finished", "result": "pass", "evidence": "AGENT DONE"},
    {"assertion": "a file made.txt is written", "result": "pass", "evidence": "made.txt"},
    {"assertion": "the setup and the inspection ran", "result": "pass", "evidence": "a quote nobody wrote"},
]))
"""
ASSERTIONS = ["the agent reports it finished", "a file made.txt is written",
              "the setup and the inspection ran"]


def suite_file(directory: Path, cases: list[dict]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "evals.json").write_text(json.dumps({
        "skill": "/fake:skill", "cases": cases,
        "triggers": {"shouldTrigger": ["do it"], "shouldNotTrigger": ["do something else"]}}))


class Runner(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        for name, body in (("agent.py", AGENT), ("sleeper.py", SLEEPER), ("grader.py", GRADER)):
            (self.tmp / name).write_text(body)
        python = sys.executable
        profiles = {"profiles": {
            "fake": {"argv": [python, str(self.tmp / "agent.py"), "{arm}", "{prompt}"],
                     "arms": {"with": [], "without": []}, "output": "text"},
            "slow": {"argv": [python, str(self.tmp / "sleeper.py")], "arms": {"with": []}, "output": "text"},
            "dead": {"argv": [str(self.tmp / "no-such-harness")], "arms": {"with": []}, "output": "text"},
            "grader": {"argv": [python, str(self.tmp / "grader.py"), "{prompt}"], "arms": {}, "output": "text"},
        }}
        self.profiles = self.tmp / "harnesses.json"
        self.profiles.write_text(json.dumps(profiles))
        self.suite = self.tmp / "suite"
        suite_file(self.suite, [{"id": "c1", "branch": "happy path", "prompt": "Make the file please.",
                                 "assertions": ASSERTIONS},
                                {"id": "c2", "branch": "Not for: — declines", "prompt": "Push it.",
                                 "assertions": ASSERTIONS[:2]}])
        (self.suite / "fixture").mkdir()
        (self.suite / "fixture/README.md").write_text("fixture\n")
        (self.suite / "setup.sh").write_text('echo "$EVAL_CASE" > "setup-ran-$1"\n')
        (self.suite / "inspect.sh").write_text('echo "INSPECT OK"\n')

    def run_cli(self, *argv: str) -> tuple[int, str]:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            code = runner.main(["--host", "--harnesses", str(self.profiles), "--suite", str(self.suite), *argv])
        return code, buffer.getvalue()

    def full_run(self, harness: str, *extra: str) -> Path:
        out = self.tmp / f"out-{harness}"
        code, text = self.run_cli("--harness", harness, "--model", "m1", "--grader-harness", "grader",
                                  "--grader-model", "g1", "--run-id", "r1", "--out", str(out), *extra)
        self.assertEqual(code, 0, text)
        return out

    def test_a_run_grades_on_quoted_evidence_and_aggregates(self):
        out = self.full_run("fake")
        grading = json.loads((out / "suite/grading.json").read_text())
        first = grading[0]["arms"]["with"]
        self.assertEqual([a["result"] for a in first["assertions"]], ["pass", "pass", "unknown"])
        self.assertIn("verbatim", first["assertions"][2]["reason"])
        snap = (out / "suite/c1.with.snapshot.txt").read_text()
        self.assertIn("setup-ran-c1", snap)
        self.assertIn("made.txt", snap)
        self.assertIn("INSPECT OK", snap)
        self.assertIn("COMMITTED CONTENT", snap)
        bench = json.loads((out / "suite/benchmark.json").read_text())
        self.assertEqual(bench["with"]["passRate"], round(4 / 5, 4))
        self.assertEqual(bench["with"]["caseApprovalRate"], 0.5)
        self.assertEqual((bench["unknown"], bench["errors"]), (1, 0))
        self.assertEqual(bench["grader"], {"harness": "grader", "model": "g1"})
        summary = json.loads((out / "summary.json").read_text())
        self.assertEqual(summary["overall"]["with"]["cases"], 2)
        self.assertEqual(summary["overall"]["with"]["caseApprovalRate"], 0.5)

    def test_the_commands_own_model_is_recorded_beside_the_run_model(self):
        self.assertEqual(runner.command_model("/quenching-specs:specs:create"), "sonnet")
        self.assertEqual(runner.command_model("/quenching-specs:specs:develop"), "opus")
        self.assertIsNone(runner.command_model("/quenching-specs:git:commit"))
        self.assertIsNone(runner.command_model("/fake:skill"))
        out = self.full_run("fake")
        bench = json.loads((out / "suite/benchmark.json").read_text())
        self.assertEqual((bench["model"], bench["commandModel"]), ("m1", None))
        summary = json.loads((out / "summary.json").read_text())
        self.assertIsNone(summary["suites"][0]["commandModel"])

    def test_both_arms_report_a_delta(self):
        out = self.full_run("fake", "--arms", "with,without")
        bench = json.loads((out / "suite/benchmark.json").read_text())
        self.assertEqual(bench["delta"]["passRate"], 0.0)
        self.assertIn("without", json.loads((out / "suite/grading.json").read_text())[0]["arms"])
        self.assertIn("CQ=<absent>", (out / "suite/c1.without.output.txt").read_text())
        self.assertNotIn("CQ=<absent>", (out / "suite/c1.with.output.txt").read_text())

    def test_a_failing_setup_is_recorded_and_the_run_goes_on(self):
        (self.suite / "setup.sh").write_text('[ "$1" = c1 ] && exit 3\necho ok\n')
        out = self.full_run("fake")
        grading = json.loads((out / "suite/grading.json").read_text())
        self.assertIn("could not be provisioned", grading[0]["arms"]["with"]["error"])
        self.assertNotIn("error", grading[1]["arms"]["with"])

    def test_a_dead_or_slow_arm_is_recorded_never_dropped(self):
        for harness, reason in (("dead", "no-such-harness"), ("slow", "timeout")):
            out = self.full_run(harness, "--timeout", "1")
            grading = json.loads((out / "suite/grading.json").read_text())
            self.assertEqual(len(grading), 2)
            arm = grading[0]["arms"]["with"]
            self.assertIn(reason, arm["error"])
            self.assertTrue(all(a["result"] == "unknown" for a in arm["assertions"]))
            self.assertEqual(json.loads((out / "suite/benchmark.json").read_text())["errors"], 2)
        self.assertIn("started", (out / "suite/c1.with.output.txt").read_text())

    def test_an_arm_the_profile_lacks_is_refused(self):
        code, text = self.run_cli("--harness", "slow", "--model", "m", "--grader-harness", "grader",
                                  "--grader-model", "g", "--run-id", "r", "--arms", "without")
        self.assertEqual(code, 2)
        self.assertIn("no 'without' arm", text)

    def test_dry_run_loads_the_modules_only_in_the_with_arm(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = runner.main(["--host", "--suite", str(self.suite), "--case", "c1", "--dry-run", "--harness", "claude",
                                "--model", "m", "--run-id", "r", "--arms", "with,without"])
        self.assertEqual(code, 0)
        lines = [json.loads(line) for line in buffer.getvalue().splitlines()]
        by_arm = {line["arm"]: line["argv"] for line in lines}
        self.assertIn("--plugin-dir", by_arm["with"])
        self.assertNotIn("--plugin-dir", by_arm["without"])
        self.assertEqual(by_arm["with"][-1], "Make the file please.")
        for harness in ("codex", "opencode"):
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                self.assertEqual(runner.main(["--host", "--suite", str(self.suite), "--case", "c1", "--dry-run",
                                              "--harness", harness, "--model", "m", "--run-id", "r"]), 0)
            self.assertIn(harness, buffer.getvalue())

    def dry_lines(self, *argv: str) -> list[dict]:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = runner.main(["--suite", str(self.suite), "--case", "c1", "--dry-run", "--model", "m",
                                "--run-id", "r", *argv])
        self.assertEqual(code, 0)
        return [json.loads(line) for line in buffer.getvalue().splitlines()]

    def test_the_default_mode_wraps_the_arm_in_a_container_with_the_permission_inside(self):
        argv = self.dry_lines("--harness", "opencode", "--image", "img:1", "--env", "PROVIDER_TOKEN",
                              "--extra-arg=--command", "--extra-arg=quenching-specs-create")[0]["argv"]
        self.assertEqual(argv[:3], ["docker", "run", "--rm"])
        self.assertEqual(argv.count("--mount"), 1)
        image = argv.index("img:1")
        self.assertEqual(argv[image + 1:image + 3], ["opencode", "run"])
        self.assertIn("--auto", argv[image:])
        self.assertNotIn("--auto", argv[:image])
        self.assertIn("PROVIDER_TOKEN", argv[:image])
        self.assertEqual(argv[-1], "Make the file please.")
        self.assertIn("--command", argv[image:])

    def test_host_mode_never_widens_a_permission(self):
        argv = self.dry_lines("--harness", "opencode", "--host")[0]["argv"]
        self.assertEqual(argv[:2], ["opencode", "run"])
        self.assertNotIn("--auto", argv)
        self.assertNotIn("docker", argv)

    def test_no_profile_but_opencode_declares_a_permission_block(self):
        profiles = json.loads((REPO / "scripts/eval_harnesses.json").read_text())["profiles"]
        self.assertEqual({n for n, p in profiles.items() if "container" in p}, {"opencode", "omnigent"})
        self.assertNotIn("{permission}", profiles["omnigent"]["container"]["argv"])
        self.assertNotIn("permission", profiles["omnigent"]["container"])
        for name, profile in profiles.items():
            self.assertNotIn("--auto", profile["argv"], name)
            self.assertNotIn("{permission}", profile["argv"], name)

    def omnigent_lines(self, suite: Path, *argv: str) -> tuple[int, list[dict], str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = runner.main(["--host", "--suite", str(suite), "--dry-run", "--harness", "omnigent", "--model", "stub",
                                "--run-id", "r", "--arms", "with,without", *argv])
        return code, [json.loads(line) for line in out.getvalue().splitlines()], err.getvalue()

    def test_the_omnigent_profile_runs_the_operator_agent_and_invokes_the_skill_in_the_session(self):
        suite = REPO / "plugins/quenching/assets/evals/git/commit"
        code, lines, _ = self.omnigent_lines(suite, "--case", "staged-change-committed")
        self.assertEqual(code, 0)
        by_arm = {line["arm"]: line["argv"] for line in lines}
        bundle = str(REPO / "plugins/omnigent/quenching")
        prompt = json.loads((suite / "evals.json").read_text())["cases"][0]["prompt"]
        self.assertEqual(by_arm["with"][:3], ["omnigent", "run", bundle])
        self.assertEqual(by_arm["with"][-2:], ["-p", "/quenching-git-commit " + prompt])
        self.assertEqual(by_arm["without"][:2], ["omnigent", "run"])
        self.assertEqual(by_arm["without"][-2:], ["-p", prompt])
        self.assertNotIn(bundle, by_arm["without"])
        for argv in by_arm.values():
            self.assertEqual(argv[argv.index("--harness") + 1], "opencode")
            self.assertEqual(argv[argv.index("--model") + 1], "stub")
            self.assertIn("--no-session", argv)
        _, lines, _ = self.omnigent_lines(suite, "--case", "staged-change-committed", "--agent-harness", "codex")
        self.assertEqual(lines[0]["argv"][lines[0]["argv"].index("--harness") + 1], "codex")

    def test_a_dry_run_in_the_default_mode_needs_no_image(self):
        out, err = io.StringIO(), io.StringIO()
        suite = REPO / "plugins/quenching/assets/evals/git/commit"
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = runner.main(["--suite", str(suite), "--case", "staged-change-committed", "--dry-run",
                                "--harness", "omnigent", "--model", "stub", "--run-id", "r"])
        self.assertEqual(code, 0, err.getvalue())
        argv = json.loads(out.getvalue().splitlines()[0])["argv"]
        image = argv.index("<image>")
        self.assertEqual(argv[image + 1:image + 3], ["omnigent", "run"])

    def test_the_omnigent_profile_refuses_a_suite_without_a_skill(self):
        code, lines, err = self.omnigent_lines(self.suite)
        self.assertEqual((code, lines), (2, []))
        self.assertIn("no generated Omnigent skill", err)

    def test_other_profiles_take_no_agent_values(self):
        profile = json.loads((REPO / "scripts/eval_harnesses.json").read_text())["profiles"]["opencode"]
        args = runner.parser().parse_args(["--model", "m"])
        self.assertEqual({"prompt", "model", "workdir", "max_turns"},
                         set(runner.arm_values(args, profile, {"prompt": "p"}, "w", "/fake:skill")))

    def test_the_container_values_never_reach_the_argv(self):
        argv = self.dry_lines("--harness", "opencode", "--image", "img", "--env", "PROVIDER_TOKEN")[0]["argv"]
        self.assertNotIn("PROVIDER_TOKEN=", " ".join(argv))
        self.assertIn("-e", argv)

    def test_the_default_mode_refuses_without_an_image_or_a_container_block(self):
        for argv, needle in ((("--harness", "opencode"), "--image"), (("--harness", "claude", "--image", "i"), "container")):
            buffer = io.StringIO()
            with contextlib.redirect_stderr(buffer):
                code = runner.main(["--suite", str(self.suite), "--model", "m", "--grader-model", "g",
                                    "--run-id", "r", *argv])
            self.assertEqual(code, 2)
            self.assertIn(needle, buffer.getvalue())
            self.assertIn("--host", buffer.getvalue())

    def test_the_default_grader_is_the_flash_gateway_profile(self):
        args = runner.parser().parse_args([])
        self.assertEqual((args.grader_harness, args.grader_model),
                         ("gateway", "system.ai.deepseek-v4-1-flash-1017"))
        profiles = runner.load_profiles(Path(runner.PROFILES))
        values = {"prompt": "p", "model": args.grader_model, "workdir": "w", "max_turns": "1",
                  "root": "/r", "prompt_file": "/tmp/p.txt"}
        argv = runner.render(profiles["gateway"], None, values, [])
        self.assertIn("system.ai.deepseek-v4-1-flash-1017", argv)
        self.assertEqual(argv[argv.index("--max-tokens") + 1], "16000")
        self.assertEqual(argv[argv.index("--prompt-file") + 1], "/tmp/p.txt")

    def test_a_dry_run_needs_no_grader_model(self):
        code, _ = self.run_cli("--harness", "fake", "--model", "m", "--grader-harness", "grader", "--run-id", "r", "--dry-run")
        self.assertEqual(code, 0)

    def test_the_grader_reads_the_prompt_from_a_file(self):
        (self.tmp / "filegrader.py").write_text(
            "import sys, json\ntext = open(sys.argv[1]).read()\n"
            "print(json.dumps([{'assertion': a, 'result': 'pass', 'evidence': 'made.txt'} "
            "for a in %r if a in text]))\n" % ASSERTIONS)
        profiles = json.loads(self.profiles.read_text())
        profiles["profiles"]["filegrader"] = {
            "argv": [sys.executable, str(self.tmp / "filegrader.py"), "{prompt_file}"], "arms": {}, "output": "text"}
        self.profiles.write_text(json.dumps(profiles))
        out = self.tmp / "out-file"
        code, text = self.run_cli("--harness", "fake", "--model", "m", "--grader-harness", "filegrader",
                                  "--grader-model", "g", "--run-id", "r", "--out", str(out))
        self.assertEqual(code, 0, text)
        grading = json.loads((out / "suite/grading.json").read_text())
        self.assertEqual({a["result"] for a in grading[1]["arms"]["with"]["assertions"]}, {"pass"})

    def test_an_unknown_is_regraded_by_the_escalation_grader_and_never_approved_otherwise(self):
        (self.tmp / "escalation.py").write_text(
            "import json, sys\nprint(json.dumps([{'assertion': a, 'result': 'pass', 'evidence': 'AGENT DONE'} "
            "for a in %r]))\n" % ASSERTIONS)
        profiles = json.loads(self.profiles.read_text())
        profiles["profiles"]["escalation"] = {
            "argv": [sys.executable, str(self.tmp / "escalation.py"), "{prompt}"], "arms": {}, "output": "text"}
        self.profiles.write_text(json.dumps(profiles))
        plain = self.full_run("fake")
        first = json.loads((plain / "suite/grading.json").read_text())[0]["arms"]["with"]["assertions"]
        self.assertEqual(first[2]["result"], "unknown")
        self.assertNotIn("gradedBy", first[2])
        out = self.tmp / "out-escalated"
        code, text = self.run_cli("--harness", "fake", "--model", "m1", "--grader-harness", "grader",
                                  "--grader-model", "g1", "--escalate-grader-harness", "escalation",
                                  "--escalate-grader-model", "big", "--run-id", "r1", "--out", str(out))
        self.assertEqual(code, 0, text)
        graded = json.loads((out / "suite/grading.json").read_text())[0]["arms"]["with"]["assertions"]
        self.assertEqual([a["result"] for a in graded], ["pass", "pass", "pass"])
        self.assertEqual([a.get("gradedBy") for a in graded], [None, None, "escalation"])
        bench = json.loads((out / "suite/benchmark.json").read_text())
        self.assertEqual(bench["grader"]["escalation"], {"harness": "escalation", "model": "big"})

    def test_an_escalation_needs_both_flags(self):
        code, text = self.run_cli("--harness", "fake", "--model", "m", "--grader-harness", "grader",
                                  "--run-id", "r", "--escalate-grader-model", "big")
        self.assertEqual(code, 2)
        self.assertIn("together", text)

    def test_the_summary_records_the_mode(self):
        out = self.full_run("fake")
        self.assertEqual(json.loads((out / "summary.json").read_text())["mode"], {"where": "host"})

    def test_check_refuses_a_malformed_suite(self):
        bad = self.tmp / "bad"
        suite_file(bad, [{"id": "x", "branch": "b", "prompt": "", "assertions": []},
                         {"id": "x", "branch": "b", "prompt": "p", "assertions": ["a"]}])
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.assertEqual(runner.main(["--check", "--suite", str(bad)]), 1)
        self.assertIn("duplicate id", buffer.getvalue())
        self.assertIn("`prompt`", buffer.getvalue())
        self.assertIn("Not for:", buffer.getvalue())
        for body in ("[]", json.dumps({"skill": "s", "cases": [7, {"id": [], "branch": "b", "prompt": "p",
                                                                    "assertions": ["a"]}]})):
            (bad / "evals.json").write_text(body)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(runner.main(["--check", "--suite", str(bad)]), 1)

    def test_every_committed_suite_passes_check(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.assertEqual(runner.main(["--check"]), 0, buffer.getvalue())
        self.assertNotIn("ERROR", buffer.getvalue())


class Containment(unittest.TestCase):
    def test_the_snapshot_never_runs_the_workspace_fsmonitor(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            workspace.mkdir()
            mark = Path(tmp) / "ran"
            env = {**runner.os.environ, **runner.GIT_ENV}
            for argv in (["git", "init", "-q", "-b", "main"],
                         ["git", "config", "core.fsmonitor", f"touch {mark}; false"]):
                runner.subprocess.run(argv, cwd=workspace, env=env, check=True)
            runner.snapshot(Path(tmp) / "no-suite", workspace, env)
            self.assertFalse(mark.exists(), "the workspace fsmonitor ran during the snapshot")

    def test_the_snapshot_never_runs_a_workspace_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            workspace.mkdir()
            mark = Path(tmp) / "ran"
            env = {**runner.os.environ, **runner.GIT_ENV}
            (workspace / ".gitattributes").write_text("f filter=evil\n")
            (workspace / "f").write_text("one\n")
            for argv in (["git", "init", "-q", "-b", "main"], ["git", "add", "-A"],
                         ["git", "commit", "-q", "-m", "x"],
                         ["git", "config", "filter.evil.clean", f"touch {mark}; cat"]):
                runner.subprocess.run(argv, cwd=workspace, env=env, check=True)
            (workspace / "f").write_text("two\n")
            runner.snapshot(Path(tmp) / "no-suite", workspace, env)
            self.assertFalse(mark.exists(), "the workspace clean filter ran during the snapshot")

    def test_the_snapshot_never_runs_a_workspace_filter_with_a_unicode_line_separator(self):
        self.assert_workspace_filter_is_neutralized("evil\u0085driver")

    def test_the_snapshot_never_runs_a_workspace_filter_with_an_equals_sign(self):
        self.assert_workspace_filter_is_neutralized("a=b")

    def assert_workspace_filter_is_neutralized(self, driver):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            workspace.mkdir()
            mark = Path(tmp) / "ran"
            env = {**runner.os.environ, **runner.GIT_ENV}
            (workspace / ".gitattributes").write_text(f"f filter={driver}\n", encoding="utf-8")
            (workspace / "f").write_text("one\n")
            for argv in (["git", "init", "-q", "-b", "main"], ["git", "add", "-A"],
                         ["git", "commit", "-q", "-m", "x"]):
                runner.subprocess.run(argv, cwd=workspace, env=env, check=True)
            if driver == "evil\u0085driver":
                config = workspace / ".git/config"
                config.write_text(config.read_text(encoding="utf-8") +
                                  f'\n[filter "{driver}"]\n\tclean = "touch {mark}; cat"\n',
                                  encoding="utf-8")
            else:
                runner.subprocess.run(["git", "config", f"filter.{driver}.clean", f"touch {mark}; cat"],
                                      cwd=workspace, env=env, check=True)
            (workspace / "f").write_text("two\n")
            runner.subprocess.run(["git", "status", "--porcelain"], cwd=workspace, env=env,
                                  check=True, capture_output=True)
            self.assertTrue(mark.exists(), f"the fixture did not trigger the {driver!r} clean filter")
            mark.unlink()
            runner.snapshot(Path(tmp) / "no-suite", workspace, env)
            self.assertFalse(mark.exists(), f"the {driver!r} workspace clean filter ran during the snapshot")

    def hostile_workspace(self, tmp, driver):
        workspace = Path(tmp) / "workspace"
        workspace.mkdir()
        mark = Path(tmp) / "ran"
        env = {k: v for k, v in runner.os.environ.items() if not k.startswith("GIT_CONFIG_")}
        env.update(runner.GIT_ENV)
        (workspace / ".gitattributes").write_text("f filter=evil\n", encoding="utf-8")
        (workspace / "f").write_text("one\n")
        for argv in (["git", "init", "-q", "-b", "main"], ["git", "add", "-A"],
                     ["git", "commit", "-q", "-m", "x"]):
            runner.subprocess.run(argv, cwd=workspace, env=env, check=True)
        config = workspace / ".git/config"
        with config.open("ab") as handle:
            handle.write(f'\n[filter "{driver}"]\n\tclean = "touch {mark}; cat"\n'.encode())
        (workspace / "f").write_text("two\n")
        return workspace, mark, env

    def test_the_snapshot_survives_a_carriage_return_in_a_driver_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, mark, env = self.hostile_workspace(tmp, "a\rb")
            text = runner.snapshot(Path(tmp) / "no-suite", workspace, env)
            self.assertNotIn("invalid key", text)
            self.assertIn("f", text.split("## git status --porcelain\n", 1)[1].splitlines()[0])
            self.assertFalse(mark.exists())

    def test_an_empty_git_config_count_is_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, mark, env = self.hostile_workspace(tmp, "evil")
            text = runner.snapshot(Path(tmp) / "no-suite", workspace, {**env, "GIT_CONFIG_COUNT": ""})
            self.assertIn("M f", text)
            self.assertFalse(mark.exists())

    def test_an_inherited_git_config_parameters_filter_does_not_win(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, mark, env = self.hostile_workspace(tmp, "evil")
            hostile = {**env, "GIT_CONFIG_PARAMETERS": f"'filter.evil.clean={mark}.sh'"}
            (Path(f"{mark}.sh")).write_text(f"#!/bin/sh\ntouch {mark}\ncat\n")
            Path(f"{mark}.sh").chmod(0o755)
            runner.snapshot(Path(tmp) / "no-suite", workspace, hostile)
            self.assertFalse(mark.exists(), "an inherited GIT_CONFIG_PARAMETERS filter ran")

    def test_the_snapshot_git_never_receives_an_inherited_git_config_parameters(self):
        seen = []
        real = runner.subprocess.run

        def spy(argv, *args, **kwargs):
            if argv[0] == "git":
                seen.append(kwargs["env"].get("GIT_CONFIG_PARAMETERS"))
            return real(argv, *args, **kwargs)

        with tempfile.TemporaryDirectory() as tmp:
            workspace, mark, env = self.hostile_workspace(tmp, "evil")
            hostile = {**env, "GIT_CONFIG_PARAMETERS": "'filter.evil.clean=true'"}
            runner.subprocess.run = spy
            try:
                runner.snapshot(Path(tmp) / "no-suite", workspace, hostile)
            finally:
                runner.subprocess.run = real
        self.assertTrue(seen)
        self.assertEqual({None}, set(seen))

    def test_a_git_config_key_without_its_value_does_not_break_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, mark, env = self.hostile_workspace(tmp, "evil")
            hostile = {**env, "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "user.name"}
            text = runner.snapshot(Path(tmp) / "no-suite", workspace, hostile)
            self.assertIn("M f", text)
            self.assertFalse(mark.exists())

    def test_a_timeout_kills_the_grandchildren_too(self):
        with tempfile.TemporaryDirectory() as tmp:
            mark = Path(tmp) / "M"
            record = runner.invoke(["bash", "-c", f"(sleep 2; touch {mark}) & sleep 30"], Path(tmp),
                                   runner.os.environ.copy(), 1)
            runner.time.sleep(3)
            self.assertIn("timeout", record["error"])
            self.assertFalse(mark.exists(), "a grandchild outlived the timeout")


class Grades(unittest.TestCase):
    def test_unparsed_or_unanswered_grades_are_unknown(self):
        grades = runner.verify_grades(["a", "b"], runner.parse_grades("no json here"), "material")
        self.assertEqual([g["result"] for g in grades], ["unknown", "unknown"])
        grades = runner.verify_grades(["a"], [{"assertion": "a", "result": "maybe", "evidence": "x"}], "x")
        self.assertEqual(grades[0]["result"], "unknown")

    def test_a_grade_for_another_assertion_is_never_reused(self):
        grades = runner.verify_grades(["a", "b"], [{"assertion": "b", "result": "pass", "evidence": "x"}], "x")
        self.assertEqual([g["result"] for g in grades], ["unknown", "pass"])

    def test_the_codex_event_stream_yields_its_agent_messages(self):
        stream = "\n".join(json.dumps(e) for e in (
            {"type": "thread.started"},
            {"type": "item.completed", "item": {"type": "command_execution", "command": "ls"}},
            {"type": "item.completed", "item": {"type": "agent_message",
                                                "text": '[{"assertion": "a", "result": "pass", "evidence": "x"}]'}},
            {"type": "turn.completed", "usage": {"input_tokens": 10, "cached_input_tokens": 8, "output_tokens": 2}}))
        text, tokens = runner.output_text({"output": "codex-jsonl"}, stream)
        self.assertEqual(tokens, 12)
        self.assertEqual(runner.parse_grades(text)[0]["result"], "pass")

    def test_evidence_matches_across_whitespace(self):
        grades = runner.verify_grades(["a"], [{"assertion": "a", "result": "fail",
                                               "evidence": "line one\n  line two"}],
                                      "before line one line two after")
        self.assertEqual(grades[0]["result"], "fail")


if __name__ == "__main__":
    unittest.main()
