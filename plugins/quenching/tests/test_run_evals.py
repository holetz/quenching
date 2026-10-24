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
            code = runner.main(["--harnesses", str(self.profiles), "--suite", str(self.suite), *argv])
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
        code, text = self.run_cli("--harness", "slow", "--model", "m", "--grader-model", "g",
                                  "--run-id", "r", "--arms", "without")
        self.assertEqual(code, 2)
        self.assertIn("no 'without' arm", text)

    def test_dry_run_loads_the_modules_only_in_the_with_arm(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = runner.main(["--suite", str(self.suite), "--case", "c1", "--dry-run", "--harness", "claude",
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
                self.assertEqual(runner.main(["--suite", str(self.suite), "--case", "c1", "--dry-run",
                                              "--harness", harness, "--model", "m", "--run-id", "r"]), 0)
            self.assertIn(harness, buffer.getvalue())

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
