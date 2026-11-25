"""`cost` measures a Copilot session from the client's ledger and event log: per agent and model,
fresh input against the cache the client served, the credit it reported, and the peak that decides
`overBudget` — never one total across models."""
import contextlib
import io
import json
import os
import pathlib
import sqlite3
import tempfile
import unittest
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.session.commands.cli import build_parser

CWD = pathlib.Path.cwd().resolve()
ORCH, RUN, RUN2, RUN3, SCOUT = "orch-1", "run-1", "run-2", "run-3", "scout-1"
OTHER_ORCH = "orch-2"
HOST = "vscode-agent-host"


def store(home, usage, seat=("s1", str(CWD), "2026-11-25T09:00:00Z", "2026-11-25T11:00:00Z")):
    db = sqlite3.connect(home / "session-store.db")
    db.executescript("""
        CREATE TABLE sessions (id TEXT PRIMARY KEY, cwd TEXT, repository TEXT, host_type TEXT,
                               branch TEXT, summary TEXT, created_at TEXT, updated_at TEXT);
        CREATE TABLE assistant_usage_events (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT,
                               turn_index INT, agent_id TEXT, parent_tool_call_id TEXT, model TEXT,
                               input_tokens INT, output_tokens INT, cache_read_tokens INT,
                               cache_write_tokens INT, reasoning_tokens INT, total_nano_aiu INT,
                               created_at TEXT);""")
    db.execute("INSERT INTO sessions VALUES (?,?,?,?,?,?,?,?)",
               (seat[0], seat[1], "holetz/quenching", "github", "main", "SECRET", seat[2], seat[3]))
    for row in usage:
        db.execute("INSERT INTO assistant_usage_events (session_id, agent_id, model, input_tokens, "
                   "output_tokens, cache_read_tokens, cache_write_tokens, reasoning_tokens, "
                   "total_nano_aiu, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)", row)
    db.commit()
    db.close()


def log(home, records, seat=("s1", str(CWD))):
    folder = home / "session-state" / seat[0]
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "events.jsonl").write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    (folder / "workspace.yaml").write_text(f"cwd: {seat[1]}\nclient_name: {HOST}\n", encoding="utf-8")


def launch(call, parent=None):
    record = {"type": "tool.execution_start", "data": {"toolCallId": call, "toolName": "Agent"}}
    if parent:
        record["agentId"] = parent
    return record


def started(agent, name, call, at):
    return {"type": "subagent.started", "agentId": agent, "timestamp": at,
            "data": {"agentName": name, "toolCallId": call}}


def tree(home, seat=("s1", str(CWD))):
    log(home, [
        {"type": "session.start", "data": {"producer": "copilot-agent",
                                           "context": {"cwd": seat[1], "gitRoot": seat[1]}}},
        launch("c1"), started(ORCH, "quenching-spec-orchestrator", "c1", "2026-11-25T09:10:00Z"),
        launch("c2", ORCH), started(RUN, "quenching-spec-runner", "c2", "2026-11-25T09:20:00Z"),
        launch("c3", ORCH), started(RUN2, "quenching-spec-runner", "c3", "2026-11-25T09:30:00Z"),
        launch("c4"), started(OTHER_ORCH, "quenching-spec-orchestrator", "c4", "2026-11-25T10:00:00Z"),
        launch("c5", OTHER_ORCH), started(RUN3, "quenching-spec-runner", "c5", "2026-11-25T10:04:00Z"),
        launch("c6"), started(SCOUT, "quenching-spec-scout", "c6", "2026-11-25T09:40:00Z"),
    ], seat=seat)


def usage(session="s1"):
    return [
        # session, agent, model, input(total), output, cacheRead, cacheWrite, reasoning, nano, at
        (session, None, "gpt", 1000, 10, 800, 0, 2, 1_000_000_000, "2026-11-25T09:05:00Z"),
        (session, ORCH, "gpt", 200_000, 100, 150_000, 0, 0, 2_000_000_000, "2026-11-25T09:15:00Z"),
        (session, RUN, "gpt", 220_000, 200, 210_000, 0, 50, 3_000_000_000, "2026-11-25T09:25:00Z"),
        (session, RUN, "gpt", 40_000, 20, 30_000, 0, 1, 500_000_000, "2026-11-25T09:26:00Z"),
        (session, RUN2, "other", 30_000, 5, 20_000, 0, 0, None, "2026-11-25T09:35:00Z"),
        (session, SCOUT, "other", 8_000, 3, 6_000, 0, 0, 4_000_000_000, "2026-11-25T09:45:00Z"),
        (session, OTHER_ORCH, "other", 160_000, 30, 100_000, 0, 0, 4_000_000_000, "2026-11-25T10:05:00Z"),
        (session, RUN3, "other", 12_000, 3, 10_000, 0, 0, 4_000_000_000, "2026-11-25T10:06:00Z"),
    ]


def run(*argv):
    args = build_parser().parse_args(["cost", *argv, "--json"])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
        code = args.func(args)
    return code, json.loads(buf.getvalue())


class CostCopilot(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = pathlib.Path(self.tmp.name) / "copilot"
        self.home.mkdir()
        patcher = mock.patch.dict(os.environ, {
            "QUENCHING_TRANSCRIPTS_ROOT": str(self.home / "claude"), "COPILOT_HOME": "",
            "QUENCHING_COPILOT_HOME": "", "OPENCODE_SESSION_ID": "", "CLAUDE_CODE_SESSION_ID": ""})
        patcher.start()
        self.addCleanup(patcher.stop)

    def visible(self, *argv):
        return run("--copilot-home", str(self.home), "s1", *argv)

    def rows(self, data):
        return {(g["agentType"], g["model"]): g for g in data["groups"]}

    def test_the_tree_by_agent_and_model_with_fresh_input_and_prompt_peak(self):
        store(self.home, usage())
        tree(self.home)
        code, data = self.visible()
        self.assertEqual(0, code)
        self.assertEqual("Copilot session id", data["resolvedBy"])
        self.assertEqual(str(self.home / "session-store.db") + "#s1", data["subagents"])
        self.assertEqual(HOST, data["session"]["client"])
        rows = self.rows(data)
        self.assertEqual({("main", "gpt"), ("spec-orchestrator", "gpt"), ("spec-orchestrator", "other"),
                          ("spec-runner", "gpt"), ("spec-runner", "other"), ("spec-scout", "other")}, set(rows))
        run_row = rows[("spec-runner", "gpt")]
        self.assertEqual((2, 20_000, 240_000, 0, 220, 51), (run_row["requests"], run_row["input"],
                                                            run_row["cacheRead"], run_row["cacheWrite"],
                                                            run_row["output"], run_row["reasoning"]))
        self.assertEqual(220_000, run_row["maxWindow"])     # the prompt total, cache included
        self.assertEqual(200, rows[("main", "gpt")]["input"])
        models = {m["model"]: m for m in data["byModel"]}
        self.assertEqual({"gpt", "other"}, set(models))
        self.assertNotIn("total", data)
        self.assertNotIn("SECRET", json.dumps(data))

    def test_the_credit_is_reported_only_where_every_request_reported_it(self):
        store(self.home, usage())
        tree(self.home)
        data = self.visible()[1]
        rows = self.rows(data)
        self.assertEqual(2.0, rows[("spec-orchestrator", "gpt")]["aiCredits"])
        self.assertEqual(3.5, rows[("spec-runner", "gpt")]["aiCredits"])
        self.assertIsNone(rows[("spec-runner", "other")]["aiCredits"])   # one request had no count
        self.assertEqual(4.0, rows[("spec-scout", "other")]["aiCredits"])
        self.assertEqual(4.0, rows[("spec-orchestrator", "other")]["aiCredits"])
        models = {m["model"]: m for m in data["byModel"]}
        self.assertEqual(6.5, models["gpt"]["aiCredits"])
        self.assertIsNone(models["other"]["aiCredits"])

    def test_over_budget_reads_the_recorded_peak_against_the_role_budget(self):
        store(self.home, usage())
        tree(self.home)
        data = self.visible()[1]
        agents = {a["agentId"]: a for a in data["agents"]}
        self.assertEqual(("worker", 220_000, 200_000, True),
                         (agents[RUN]["role"], agents[RUN]["peakContext"], agents[RUN]["budget"],
                          agents[RUN]["exceeded"]))
        self.assertEqual(("conductor", 200_000, 150_000, True),
                         (agents[ORCH]["role"], agents[ORCH]["peakContext"],
                          agents[ORCH]["budget"], agents[ORCH]["exceeded"]))
        self.assertEqual(("conductor", 160_000, 150_000, True),
                         (agents[OTHER_ORCH]["role"], agents[OTHER_ORCH]["peakContext"],
                          agents[OTHER_ORCH]["budget"], agents[OTHER_ORCH]["exceeded"]))
        self.assertEqual(("unknown", 8_000, None, None),
                         (agents[SCOUT]["role"], agents[SCOUT]["peakContext"],
                          agents[SCOUT]["budget"], agents[SCOUT]["exceeded"]))
        self.assertFalse(agents["main"]["exceeded"])
        self.assertEqual([ORCH, OTHER_ORCH, RUN], sorted(data["overBudget"]))

    def test_usd_is_opt_in_and_null_for_a_model_the_table_does_not_price(self):
        store(self.home, usage())
        tree(self.home)
        plain = self.visible()[1]
        self.assertNotIn("usd", plain["groups"][0])
        priced = self.visible("--usd")[1]
        self.assertTrue(all(row["usd"] is None for row in priced["groups"] + priced["byModel"]))
        self.assertIn("list price", priced["pricing"]["basis"])

    def test_the_running_client_is_the_source_when_no_flag_asks(self):
        store(self.home, usage())
        tree(self.home)
        with mock.patch.dict(os.environ, {"COPILOT_HOME": str(self.home)}):
            code, data = run()
        self.assertEqual(0, code)
        self.assertEqual("most recent Copilot session in this directory", data["resolvedBy"])

    def test_self_is_refused_naming_the_scope_that_works(self):
        store(self.home, usage())
        tree(self.home)
        code, data = self.visible("--self", "runner-1")
        self.assertEqual(2, code)
        self.assertEqual("se-copilot-self", data["code"])
        self.assertIn("--descendants-of", data["message"])

    def test_a_missing_store_refuses_by_name(self):
        code, data = self.visible()
        self.assertEqual(2, code)
        self.assertEqual("se-no-transcript", data["code"])
        self.assertIn("session store", data["message"])



class CostCopilotScopes(CostCopilot):
    def test_descendants_of_keeps_only_the_subtree(self):
        store(self.home, usage())
        tree(self.home)
        data = self.visible("--descendants-of", ORCH)[1]
        self.assertEqual({("spec-runner", "gpt"), ("spec-runner", "other")}, set(self.rows(data)))

    def test_descendants_of_main_keeps_every_subagent_and_never_the_root(self):
        store(self.home, usage())
        tree(self.home)
        data = self.visible("--descendants-of", "main")[1]
        self.assertEqual({"spec-orchestrator", "spec-runner", "spec-scout"},
                         {g["agentType"] for g in data["groups"]})
        self.assertNotIn("main", {a["agentId"] for a in data["agents"]})

    def test_nested_keeps_only_agents_that_have_a_parent(self):
        store(self.home, usage())
        tree(self.home)
        data = self.visible("--nested")[1]
        self.assertEqual({"spec-runner"}, {g["agentType"] for g in data["groups"]})

    def test_latest_orchestrator_keeps_the_last_one_started(self):
        store(self.home, usage())
        tree(self.home)
        data = self.visible("--latest-orchestrator")[1]
        self.assertEqual({("spec-runner", "other")}, set(self.rows(data)))
        self.assertEqual({RUN3}, {a["agentId"] for a in data["agents"]})

    def test_an_unknown_agent_and_a_missing_orchestrator_refuse(self):
        store(self.home, usage())
        tree(self.home)
        code, data = self.visible("--descendants-of", "nope")
        self.assertEqual((2, "se-unknown-agent"), (code, data["code"]))
        log(self.home, [])
        code, data = self.visible("--latest-orchestrator")
        self.assertEqual((2, "se-no-orchestrator"), (code, data["code"]))

    def test_since_keeps_only_the_window(self):
        store(self.home, usage())
        tree(self.home)
        data = self.visible("--since", "2026-11-25T09:27:00Z")[1]
        self.assertEqual({("spec-runner", "other"), ("spec-scout", "other"),
                          ("spec-orchestrator", "other")}, set(self.rows(data)))
        self.assertEqual({RUN2, RUN3, SCOUT, OTHER_ORCH}, {a["agentId"] for a in data["agents"]})
