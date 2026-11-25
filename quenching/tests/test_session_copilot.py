"""The Copilot reader: where the client keeps a session, which session a call means, and that no
message content ever reaches a payload."""
import json
import os
import pathlib
import sqlite3
import tempfile
import unittest
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.session import copilot

SLOT = pathlib.Path("/checkout/slot-1").resolve()
REPO = pathlib.Path("/checkout").resolve()
OTHER = pathlib.Path("/elsewhere").resolve()


def schema(db):
    db.executescript("""
        CREATE TABLE sessions (id TEXT PRIMARY KEY, cwd TEXT, repository TEXT, host_type TEXT,
                               branch TEXT, summary TEXT, created_at TEXT, updated_at TEXT);
        CREATE TABLE turns (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, turn_index INT,
                            user_message TEXT, assistant_response TEXT, timestamp TEXT);
        CREATE TABLE assistant_usage_events (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT,
                               turn_index INT, agent_id TEXT, parent_tool_call_id TEXT, model TEXT,
                               input_tokens INT, output_tokens INT, cache_read_tokens INT,
                               cache_write_tokens INT, reasoning_tokens INT, total_nano_aiu INT,
                               created_at TEXT);""")


def ledger(home, rows, seat=("s1", REPO, "2026-11-25T10:00:00Z", "2026-11-25T10:10:00Z"), fresh=True):
    db = sqlite3.connect(home / copilot.STORE)
    if fresh:
        schema(db)
    db.execute("INSERT INTO sessions VALUES (?,?,?,?,?,?,?,?)",
               (seat[0], str(seat[1]), "holetz/quenching", "github", "main", "SECRET summary",
                seat[2], seat[3]))
    db.execute("INSERT INTO turns (session_id, turn_index, user_message, assistant_response) "
               "VALUES (?,?,?,?)", (seat[0], 1, "SECRET question", "SECRET answer"))
    for row in rows:
        db.execute("INSERT INTO assistant_usage_events (session_id, agent_id, model, input_tokens, "
                   "output_tokens, cache_read_tokens, cache_write_tokens, reasoning_tokens, "
                   "total_nano_aiu, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)", row)
    db.commit()
    db.close()


def event_log(home, session="s1", records=()):
    folder = home / copilot.STATE / session
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "events.jsonl").write_text(
        "\n".join(records if all(isinstance(r, str) for r in records)
                  else [json.dumps(r) for r in records]) + "\n", encoding="utf-8")
    return folder


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = pathlib.Path(self.tmp.name) / "copilot"
        self.home.mkdir()
        patcher = mock.patch.dict(os.environ, {"QUENCHING_COPILOT_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)


class TheHome(Fixture):
    def test_the_precedence_names_every_layer(self):
        self.assertEqual(pathlib.Path("/asked"), copilot.home("/asked"))
        self.assertEqual(self.home, copilot.home(None))
        with mock.patch.dict(os.environ, {"COPILOT_HOME": "/client"}, clear=False):
            os.environ.pop(copilot.HOME_ENV, None)
            self.assertEqual(pathlib.Path("/client"), copilot.home(None))
            os.environ.pop("COPILOT_HOME", None)
            self.assertEqual(pathlib.Path.home() / ".copilot", copilot.home(None))

    def test_the_running_client_is_what_asks_when_no_flag_does(self):
        self.assertTrue(copilot.wants_copilot(None, None))
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(copilot.HOME_ENV, None)
            os.environ.pop("COPILOT_HOME", None)
            self.assertFalse(copilot.wants_copilot(None, None))


class Resolution(Fixture):
    def test_a_named_session_resolves_and_an_unknown_one_refuses(self):
        ledger(self.home, [])
        self.assertEqual(("s1", "Copilot session id"), copilot.resolve(self.home, "s1", REPO))
        with self.assertRaises(copilot.CopilotError) as raised:
            copilot.resolve(self.home, "nope", REPO)
        self.assertEqual("se-no-transcript", raised.exception.code)

    def test_the_most_recent_session_for_this_directory_wins(self):
        ledger(self.home, [])
        ledger(self.home, [], seat=("s2", REPO, "2026-11-25T12:00:00Z", "2026-11-25T12:30:00Z"),
               fresh=False)
        self.assertEqual(("s2", "most recent Copilot session in this directory"),
                         copilot.resolve(self.home, None, REPO))
        self.assertEqual(("s1", "Copilot session id"), copilot.resolve(self.home, "s1", OTHER))

    def test_a_slot_worktree_belongs_to_the_checkout_that_cut_it(self):
        ledger(self.home, [], seat=("slot", SLOT, "2026-11-25T10:00:00Z", "2026-11-25T10:10:00Z"))
        (self.home / copilot.STATE / "slot").mkdir(parents=True)
        (self.home / copilot.STATE / "slot" / "workspace.yaml").write_text(
            f"cwd: {SLOT}\ngit_root: {REPO}\nclient_name: vscode-agent-host\n", encoding="utf-8")
        found = copilot.sessions(self.home)
        self.assertTrue(copilot.in_scope(found["slot"], REPO))
        self.assertFalse(copilot.in_scope(found["slot"], OTHER))

    def test_a_missing_store_or_ledger_refuses_by_name(self):
        with self.assertRaises(copilot.CopilotError) as missing:
            copilot.sessions(self.home)
        self.assertEqual("se-no-transcript", missing.exception.code)
        db = sqlite3.connect(self.home / copilot.STORE)
        db.execute("CREATE TABLE sessions (id TEXT)")
        db.commit()
        db.close()
        with self.assertRaises(copilot.CopilotError) as unreadable:
            copilot.sessions(self.home)
        self.assertEqual("se-no-transcript", unreadable.exception.code)
        self.assertIn("assistant_usage_events", unreadable.exception.message)


class NoContent(Fixture):
    def test_neither_the_summary_nor_a_turn_reaches_a_payload(self):
        ledger(self.home, [("s1", None, "gpt", 10, 5, 0, 0, 0, None, "2026-11-25T10:00:01Z")])
        dumped = repr([copilot.sessions(self.home), copilot.requests(self.home, ["s1"])])
        self.assertNotIn("SECRET", dumped)
        self.assertNotIn("summary", dumped)


MAIN, ORCH, RUNNER = "main-1", "orch-1", "run-1"


def started(agent, name, call, at="2026-11-25T10:00:00Z"):
    return {"type": "subagent.started", "agentId": agent, "timestamp": at,
            "data": {"agentName": name, "toolCallId": call}}


def launch(call, agent=None, at="2026-11-25T09:59:59Z"):
    record = {"type": "tool.execution_start", "timestamp": at,
              "data": {"toolCallId": call, "toolName": "Agent"}}
    if agent is not None:
        record["agentId"] = agent
    return record


class TheEventLog(Fixture):
    def test_the_tree_comes_from_the_launch_call_and_names_from_the_start(self):
        event_log(self.home, records=[
            {"type": "session.start", "data": {"producer": "copilot-agent",
                                               "context": {"cwd": str(REPO), "gitRoot": str(REPO)}}},
            launch("c1"), started(ORCH, "quenching-spec-orchestrator", "c1"),
            launch("c2", ORCH), started(RUNNER, "quenching-spec-runner", "c2"),
            {"type": "subagent.completed", "agentId": RUNNER, "timestamp": "2026-11-25T10:05:00Z",
             "data": {"agentName": "quenching-spec-runner"}}])
        agents, facts = copilot.events(self.home, "s1")
        self.assertEqual("quenching-spec-runner", agents[RUNNER]["name"])
        self.assertEqual(ORCH, agents[RUNNER]["parent"])
        self.assertIsNone(agents[ORCH]["parent"])
        self.assertEqual([RUNNER], copilot.descendant_ids(agents, ORCH))
        self.assertEqual([], copilot.descendant_ids(agents, RUNNER))
        self.assertEqual("copilot-agent", facts["producer"])
        self.assertEqual([], facts["anomalies"])
        self.assertEqual("main", copilot.agent_name(None, agents))
        self.assertEqual("quenching-spec-runner", copilot.agent_name(RUNNER, agents))
        self.assertTrue(copilot.agent_name("abcdef123456", agents).startswith("unknown"))

    def test_the_client_and_git_root_come_from_the_workspace(self):
        folder = event_log(self.home, records=[])
        (folder / "workspace.yaml").write_text(
            f"cwd: {SLOT}\ngit_root: {REPO}\nclient_name: vscode-agent-host\n"
            "name: |-\n  SECRET prompt\n", encoding="utf-8")
        agents, facts = copilot.events(self.home, "s1")
        self.assertEqual("vscode-agent-host", facts["client"])
        self.assertEqual(str(SLOT), facts["cwd"])
        self.assertEqual(str(REPO), facts["gitRoot"])
        self.assertNotIn("SECRET", repr(facts))

    def test_a_missing_or_unparsable_log_is_an_anomaly_not_a_crash(self):
        agents, facts = copilot.events(self.home, "none")
        self.assertEqual({}, agents)
        self.assertIn("no event log", facts["anomalies"][0]["message"])
        event_log(self.home, records=["{not json", "[]", json.dumps(launch("c1"))])
        agents, facts = copilot.events(self.home, "s1")
        self.assertEqual(2, len(facts["anomalies"]))
        self.assertEqual([], copilot.descendant_ids(agents, ORCH))


class TheRequests(Fixture):
    def test_fresh_input_is_the_prompt_total_minus_what_the_cache_served(self):
        ledger(self.home, [("s1", None, "gpt", 1000, 7, 900, 50, 3, 2_500_000_000, "2026-11-25T10:00:01Z")])
        rows, anomalies = copilot.requests(self.home, ["s1"])
        request = rows["s1"][0]
        self.assertEqual((1000, 900, 50, 50, 3, 2_500_000_000),
                         (request.input, request.cache_read, request.cache_write, request.fresh,
                          request.reasoning, request.nano_aiu))
        self.assertEqual([], anomalies)

    def test_the_cache_above_the_total_is_an_anomaly_and_a_zero_fresh(self):
        ledger(self.home, [("s1", None, "gpt", 10, 1, 20, 0, 0, None, "2026-11-25T10:00:01Z")])
        rows, anomalies = copilot.requests(self.home, ["s1"])
        self.assertEqual(0, rows["s1"][0].fresh)
        self.assertEqual(1, len(anomalies))
        self.assertIn("more cache tokens than prompt tokens", anomalies[0]["message"])

    def test_since_drops_old_requests_and_flags_one_with_no_timestamp(self):
        ledger(self.home, [
            ("s1", None, "gpt", 10, 1, 0, 0, 0, None, "2026-11-25T09:00:00Z"),
            ("s1", None, "gpt", 20, 1, 0, 0, 0, None, "not a timestamp"),
            ("s1", None, "gpt", 30, 1, 0, 0, 0, None, "2026-11-25T11:00:00Z")])
        cutoff = copilot.parse_instant("2026-11-25T10:00:00Z")
        rows, anomalies = copilot.requests(self.home, ["s1"], since=cutoff)
        self.assertEqual([30], [r.input for r in rows["s1"]])
        self.assertEqual(1, len(anomalies))
        everything, _ = copilot.requests(self.home, ["s1"])
        self.assertEqual({10, 20, 30}, {r.input for r in everything["s1"]})
        self.assertIsNone(next(r for r in everything["s1"] if r.input == 20).at)

    def test_requests_stay_oldest_first_and_unknown_fields_are_not_invented(self):
        ledger(self.home, [
            ("s1", ORCH, "", 5, 2, 0, 0, 0, None, "2026-11-25T10:02:00Z"),
            ("s1", None, "gpt", 1, 1, 0, 0, 0, -1, "2026-11-25T10:01:00Z")])
        rows, _ = copilot.requests(self.home, ["s1"])
        self.assertEqual([1, 5], [r.input for r in rows["s1"]])
        self.assertEqual(copilot.UNKNOWN, rows["s1"][1].model)
        self.assertIsNone(rows["s1"][0].nano_aiu)   # a negative count is not a credit
