"""Recorded context windows and exposure are separate, including in public CLI output."""
import contextlib
import io
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest
from unittest import mock

import _paths  # noqa: F401
from quenching.session.commands.cli import build_parser
from quenching.session.model import bare_agent

CQ = Path(__file__).resolve().parents[1] / "assets/bin/cq"


def usage(inp, windows=None, **extra):
    value = {"input_tokens": inp, "cache_read_input_tokens": 0,
             "cache_creation_input_tokens": 0, "output_tokens": 1, **extra}
    if windows is not None:
        value["iterations"] = [{"type": "message", "input_tokens": window} for window in windows]
    return value


def request(mid, tokens):
    return {"type": "assistant", "message": {"id": mid, "usage": tokens}}


def run(*argv):
    args = build_parser().parse_args(["context", "--json", *map(str, argv)])
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = args.func(args)
    return code, json.loads(output.getvalue())


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.path = self.base / "session.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, *records, path=None):
        target = path or self.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(json.dumps(record) for record in records) + "\n")
        return target

    def test_streaming_final_usage_and_multiexecutor_peak(self):
        self.write(request("a", usage(12, [12], output_tokens=1)),
                   request("a", usage(240000, [140000, 100000], output_tokens=8)),
                   request("a", usage(12, [12], output_tokens=1)),
                   request("a", None), request("b", usage(90000, [90000])))
        code, data = run(self.path)
        self.assertEqual(code, 0)
        self.assertEqual((data["peakContext"], data["peakUpperBound"], data["turns"], data["integral"]),
                         (140000, 240000, 2, 330000))
        self.assertEqual((data["role"], data["budget"], data["remaining"]), ("main", 200000, 60000))
        self.assertFalse(data["currentTurnIncluded"])

    def test_exact_boundary_and_above(self):
        for peak, code in ((200000, 0), (200001, 1)):
            self.write(request("a", usage(peak, [peak])))
            actual, data = run(self.path)
            self.assertEqual(actual, code)
            self.assertEqual(data["exceeded"], code == 1)
            self.assertEqual(data["remaining"], 200000 - peak)

    def test_advisor_iterations_are_excluded_and_cache_counts(self):
        tokens = usage(100, [100])
        tokens["cache_read_input_tokens"] = 1000
        tokens["cache_creation_input_tokens"] = 2000
        tokens["iterations"][0].update(cache_read_input_tokens=1000, cache_creation_input_tokens=2000)
        tokens["iterations"].append({"type": "advisor", "input_tokens": 999999})
        self.write(request("a", tokens), {"isCompactSummary": True, **request("b", usage(999999, [999999]))})
        code, data = run(self.path)
        self.assertEqual(code, 0)
        self.assertEqual((data["peakContext"], data["integral"], data["turns"]), (3100, 3100, 1))

    def test_missing_and_partial_iterations_never_claim_a_peak(self):
        for records, coverage in (([request("a", usage(120000))], "none"),
                                  ([request("a", usage(120000)), request("b", usage(10, [10]))], "partial")):
            self.write(*records)
            code, data = run(self.path)
            self.assertEqual(code, 2)
            self.assertIsNone(data["peakContext"])
            self.assertEqual(data["peakUpperBound"], 120000)
            self.assertIsNone(data["remaining"])
            self.assertIsNone(data["exceeded"])
            self.assertEqual(data["iterationCoverage"], coverage)

    def test_agent_roles_come_from_metadata_and_unknown_refuses(self):
        for kind, role, budget in (("quenching-specs:spec-runner", "worker", 100000),
                                    ("quenching-specs:orchestrator", "conductor", 150000),
                                    ("quenching:autopilot", "conductor", 150000),
                                    ("Explore", "unknown", None), (7, "unknown", None)):
            agent = self.base / "session/subagents/agent-worker.jsonl"
            self.write(request("a", usage(110000, [110000])), path=agent)
            agent.with_suffix(".meta.json").write_text(json.dumps({"agentType": kind}))
            code, data = run(agent)
            self.assertEqual((data["role"], data["budget"]), (role, budget))
            self.assertEqual(code, 2 if budget is None else 1 if role == "worker" else 0)

    def test_deployed_agent_name_keeps_its_role(self):
        self.assertEqual(bare_agent("quenching-spec-runner"), "spec-runner")
        self.assertEqual(bare_agent("quenching-specs:spec-runner"), "spec-runner")
        self.assertEqual(bare_agent("quenching:orchestrator"), "orchestrator")

    def test_missing_or_invalid_agent_metadata_refuses(self):
        agent = self.base / "session/subagents/agent-a.jsonl"
        self.write(request("a", usage(1, [1])), path=agent)
        self.assertEqual(run(agent)[0], 2)
        for raw in ("{invalid", "[]"):
            agent.with_suffix(".meta.json").write_text(raw)
            self.assertEqual(run(agent)[0], 2)

    def test_empty_unsupported_and_unreadable_refuse(self):
        for records in ([], [{"type": "event_msg", "payload": {"type": "token_count"}}],
                        [request("a", None)], [request("a", {})]):
            self.write(*records)
            code, data = run(self.path)
            self.assertEqual(code, 2)
            self.assertIsNone(data["peakContext"])
        self.assertEqual(run(self.base / "missing.jsonl")[0], 2)
        self.path.write_bytes(b'\xff')
        self.assertEqual(run(self.path)[0], 2)

    def test_malformed_line_prevents_green_partial_measurement(self):
        self.write(request("a", usage(10, [10])))
        with self.path.open("a") as stream:
            stream.write("{broken\n")
        code, data = run(self.path)
        self.assertEqual(code, 2)
        self.assertEqual(data["anomalies"][0]["code"], "se-unparsed-line")
        self.assertEqual(data["observedIterationPeak"], 10)
        self.assertIsNone(data["peakContext"])

    def test_invalid_usage_never_becomes_zero(self):
        for bad in (-1, True, "12", None):
            for field in ("input_tokens", "cache_read_input_tokens", "output_tokens"):
                tokens = usage(10, [10])
                tokens[field] = bad
                self.write(request("a", tokens))
                code, data = run(self.path)
                self.assertEqual(code, 2, (field, bad))
                self.assertTrue(data["anomalies"])
        tokens = usage(10, [10])
        tokens["iterations"][0]["input_tokens"] = True
        self.write(request("a", tokens))
        self.assertEqual(run(self.path)[0], 2)

    def test_iteration_larger_than_request_is_an_inconclusive_misread(self):
        self.write(request("a", usage(10, [20])))
        code, data = run(self.path)
        self.assertEqual(code, 2)
        self.assertEqual(data["anomalies"][0]["code"], "se-invalid-executor-iteration")
        self.assertIsNone(data["peakContext"])

    def test_non_object_and_bad_message_are_named(self):
        for record in ([], 42, {"type": "assistant", "message": []},
                       {"type": "assistant", "message": {"id": 42, "usage": usage(1, [1])}}):
            self.write(record)
            code, data = run(self.path)
            self.assertEqual(code, 2)
            self.assertTrue(data["anomalies"])

    def test_no_selector_never_picks_latest_session(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(run()[1]["code"], "se-no-live-session")

    def test_environment_and_explicit_precedence(self):
        self.write(request("a", usage(1, [1])))
        other = self.write(request("b", usage(2, [2])), path=self.base / "other.jsonl")
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": str(self.path)}):
            self.assertEqual(run()[1]["peakContext"], 1)
            self.assertEqual(run(other)[1]["peakContext"], 2)

    def test_session_id_and_agent_id_resolution(self):
        cwd = Path.cwd().resolve()
        project = self.base / "projects" / str(cwd).replace("/", "-").replace(".", "-")
        self.write(request("main", usage(1, [1])), path=project / "live.jsonl")
        agent = project / "live/subagents/agent-a.jsonl"
        self.write(request("agent", usage(2, [2])), path=agent)
        agent.with_suffix(".meta.json").write_text('{"agentType":"quenching-specs:spec-runner"}')
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": "live", "QUENCHING_TRANSCRIPTS_ROOT": str(project.parent)}):
            self.assertEqual(run()[1]["peakContext"], 1)
            self.assertEqual(run("--agent", "a")[1]["role"], "worker")
            self.assertEqual(run("--agent", "../a")[0], 2)
            self.assertEqual(run("--agent", "missing")[0], 2)

    def call(self, stamp, command, *, path):
        """Append a recorded Bash call, the way the host writes an in-flight tool use."""
        record = {"type": "assistant", "timestamp": stamp, "message": {
            "id": f"call-{stamp}", "usage": usage(5, [5]),
            "content": [{"type": "tool_use", "name": "Bash", "input": {"command": command}}]}}
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record) + "\n")

    def self_session(self):
        project = self.base / "projects" / "-home-checkout"
        main = self.write(request("main", usage(1, [1])), path=project / "live.jsonl")
        agents = {}
        for name in ("w1", "w2"):
            agent = self.write(request(name, usage(2, [2])), path=project / f"live/subagents/agent-{name}.jsonl")
            agent.with_suffix(".meta.json").write_text('{"agentType":"quenching-specs:spec-runner"}')
            agents[name] = agent
        return project, main, agents

    def test_self_marker_selects_the_caller_transcript(self):
        project, main, agents = self.self_session()
        self.call("2026-10-17T10:00:00Z", "cq components session context --self 1632 --json", path=agents["w1"])
        self.call("2026-10-17T10:05:00Z", "cq components session context --self 1700 --json", path=agents["w2"])
        self.call("2026-10-17T10:06:00Z", "grep -- '--self 1632' notes.md", path=main)
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": "live",
                                          "QUENCHING_TRANSCRIPTS_ROOT": str(project.parent)}):
            code, data = run("--self", "1632")
            self.assertEqual(data["transcript"], str(agents["w1"]))
            self.assertEqual((data["role"], data["budget"]), ("worker", 100000))
            self.assertIn("self marker", data["resolvedBy"])
            self.assertEqual(run("--self", "999")[1]["code"], "se-self-not-found")
            self.assertEqual(run("--self", "163")[1]["code"], "se-self-not-found")
            self.call("2026-10-17T10:00:00Z", "cq components session context --self 1632", path=agents["w2"])
            self.assertEqual(run("--self", "1632")[1]["code"], "se-self-ambiguous")
            self.call("2026-10-17T10:09:00Z", "cq components session context --self 1632", path=main)
            code, data = run("--self", "1632")
            self.assertEqual((data["transcript"], data["role"]), (str(main), "main"))
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            run("--self", "1632", "--agent", "w1")

    def test_bare_session_id_resolves_from_a_sibling_worktree(self):
        root = self.base / "projects"
        target = self.write(request("main", usage(7, [7])), path=root / "-home-checkout" / "live.jsonl")
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": "live", "QUENCHING_TRANSCRIPTS_ROOT": str(root)}):
            code, data = run()
            self.assertEqual((code, data["transcript"]), (0, str(target)))
            self.assertEqual(data["resolvedBy"], "session id across project dirs")
            self.write(request("x", usage(1, [1])), path=root / "-home-other" / "live.jsonl")
            self.assertEqual(run()[1]["code"], "se-no-transcript")

    def test_public_cq_route_json_at_both_levels(self):
        self.write(request("a", usage(3, [3])))
        for argv in (["components", "session", "context", str(self.path), "--json"],
                     ["components", "session", "--json", "context", str(self.path)]):
            proc = subprocess.run(["python3", str(CQ), *argv], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(json.loads(proc.stdout)["peakContext"], 3)



class OpenCodeContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "opencode.db"
        db = sqlite3.connect(self.db)
        db.executescript("""
            CREATE TABLE session_v2 (id TEXT, parent_id TEXT, agent TEXT, directory TEXT);
            CREATE TABLE session_message (id TEXT, session_id TEXT, type TEXT, seq INT, data TEXT);""")
        db.executemany("INSERT INTO session_v2 VALUES (?,?,?,?)", [
            ("ses_root", None, "build", "/r"), ("ses_kid", "ses_root", "quenching-spec-runner", "/r"),
            ("ses_odd", "ses_root", "explore", "/r")])
        steps = [("ses_root", 1000, 500), ("ses_kid", 40000, 60000), ("ses_kid", 1000, 110000), ("ses_odd", 5, 5)]
        for n, (sid, inp, read) in enumerate(steps):
            db.execute("INSERT INTO session_message VALUES (?,?,'assistant',?,?)", (f"m{n}", sid, n, json.dumps({
                "time": {"created": 1_790_000_000_000}, "model": {"id": "deepseek"},
                "tokens": {"input": inp, "output": 1, "reasoning": 0, "cache": {"read": read, "write": 0}}})))
        db.commit()
        db.close()
        patcher = mock.patch.dict(os.environ, {"QUENCHING_OPENCODE_DB": str(self.db)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def live(self, session, *argv):
        with mock.patch.dict(os.environ, {"OPENCODE_SESSION_ID": session, "CLAUDE_CODE_SESSION_ID": "claude"}):
            return run(*argv)

    def test_worker_over_budget_measures_itself_and_the_marker_is_not_needed(self):
        code, out = self.live("ses_kid", "--self", "2149")
        self.assertEqual(code, 1)
        self.assertEqual((out["role"], out["peakContext"], out["budget"], out["exceeded"], out["turns"]),
                         ("worker", 111000, 100000, True, 2))
        self.assertEqual(out["measurement"], "recorded-OpenCode-usage")

    def test_main_session_is_within_budget(self):
        code, out = self.live("ses_root")
        self.assertEqual((code, out["role"], out["peakContext"]), (0, "main", 1500))

    def test_child_is_selected_by_agent(self):
        self.assertEqual(self.live("ses_root", "--agent", "ses_kid")[1]["role"], "worker")

    def test_explicit_session_id_needs_no_environment(self):
        self.assertEqual(run("ses_kid")[1]["peakContext"], 111000)

    def test_unknown_role_and_unknown_session_are_unmeasured(self):
        self.assertEqual(self.live("ses_odd")[0], 2)
        code, out = self.live("ses_none")
        self.assertEqual((code, out["code"]), (2, "se-context-inconclusive"))

    def test_missing_database_refuses(self):
        with mock.patch.dict(os.environ, {"QUENCHING_OPENCODE_DB": str(self.db) + ".none"}):
            code, out = self.live("ses_root")
        self.assertEqual((code, out["code"]), (2, "se-no-transcript"))


if __name__ == "__main__":
    unittest.main()
