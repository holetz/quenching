"""`cache --harness copilot` reads the client's ledger into the same request shape as Claude Code and
OpenCode: the prompt total with its cache subset, the client as `host`, and cold requests by gap."""
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
RUN = "run-1"
HOST = "vscode-agent-host"
MODEL = "customendpoint/deepseek-v4-flash"


def store(home, usage, seat=("s1", str(CWD))):
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
               (seat[0], seat[1], "holetz/quenching", "github", "main", "SECRET summary",
                "2026-11-25T09:00:00Z", "2026-11-25T12:00:00Z"))
    for row in usage:
        db.execute("INSERT INTO assistant_usage_events (session_id, agent_id, model, input_tokens, "
                   "output_tokens, cache_read_tokens, cache_write_tokens, reasoning_tokens, "
                   "total_nano_aiu, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)", row)
    db.commit()
    db.close()


def log(home, session="s1"):
    folder = home / "session-state" / session
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "events.jsonl").write_text("\n".join(json.dumps(r) for r in [
        {"type": "tool.execution_start", "data": {"toolCallId": "c1", "toolName": "Agent"}},
        {"type": "subagent.started", "agentId": RUN, "timestamp": "2026-11-25T09:55:00Z",
         "data": {"agentName": "quenching-spec-runner", "toolCallId": "c1"}},
    ]) + "\n", encoding="utf-8")
    (folder / "workspace.yaml").write_text(f"cwd: {CWD}\nclient_name: {HOST}\n", encoding="utf-8")


def usage():
    return [
        # session, agent, model, input(total), output, cacheRead, cacheWrite, reasoning, nano, at
        ("s1", None, MODEL, 10_000, 10, 0, 0, 1, None, "2026-11-25T10:00:00Z"),
        ("s1", None, MODEL, 20_000, 10, 12_000, 0, 1, None, "2026-11-25T10:10:00Z"),
        ("s1", None, "other", 10_000, 4, 0, 0, 0, None, "2026-11-25T10:11:00Z"),
        ("s1", RUN, MODEL, 6_000, 5, 4_000, 0, 0, None, "2026-11-25T10:20:00Z"),
        ("s1", None, "other", 12_000, 4, 0, 0, 0, None, "2026-11-25T11:30:00Z"),
        ("s1", RUN, MODEL, 8_000, 5, 0, 0, 0, None, "2026-11-25T11:31:00Z"),
    ]


def run(*argv):
    args = build_parser().parse_args(["cache", *argv, "--json"])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
        code = args.func(args)
    return code, json.loads(buf.getvalue())


class CacheCopilot(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = pathlib.Path(self.tmp.name) / "copilot"
        self.home.mkdir()
        patcher = mock.patch.dict(os.environ, {
            "COPILOT_HOME": "", "QUENCHING_COPILOT_HOME": "",
            "QUENCHING_TRANSCRIPTS_ROOT": str(self.home / "claude"),
            "QUENCHING_OPENCODE_DB": str(self.home / "opencode.db")})
        patcher.start()
        self.addCleanup(patcher.stop)

    def measure(self, *argv):
        return run("--harness", "copilot", "--copilot-home", str(self.home),
                   "--directory", str(CWD), *argv)

    def rows(self, data):
        return {(r["role"], r["agent"], r["model"]): r for r in data["rows"]}

    def test_rows_by_agent_and_model_with_the_client_as_host(self):
        store(self.home, usage())
        log(self.home)
        code, data = self.measure()
        self.assertEqual(0, code)
        self.assertEqual("copilot", next(iter(data["rows"]))["harness"])
        rows = self.rows(data)
        main = rows[("main", "main", MODEL)]
        self.assertEqual((HOST, 2, 18_000, 12_000, 0, 20),
                         (main["host"], main["requests"], main["input"], main["cacheRead"],
                          main["cacheWrite"], main["output"]))
        self.assertEqual(12_000, main["readAfterGap5m"])   # the 10-minute gap into the cached prompt
        runner = rows[("subagent", "spec-runner", MODEL)]
        self.assertEqual((2, 10_000, 4_000), (runner["requests"], runner["input"], runner["cacheRead"]))
        other = rows[("main", "main", "other")]
        self.assertEqual((2, 22_000, 0), (other["requests"], other["input"], other["cacheRead"]))
        self.assertEqual(str(self.home / "session-store.db"), data["sources"]["copilot"])
        self.assertNotIn("SECRET", json.dumps(data))

    def test_the_hit_rate_never_passes_one_and_models_is_never_one_total(self):
        store(self.home, usage())
        log(self.home)
        data = self.measure()[1]
        for row in data["rows"]:
            self.assertLessEqual(row["hitRate"], 1)
        hits = {(r["role"], r["agent"], r["model"]): r["hitRate"] for r in data["rows"]}
        self.assertEqual(0.4, hits[("main", "main", MODEL)])
        self.assertEqual(0.0, hits[("main", "main", "other")])
        self.assertAlmostEqual(4_000 / 14_000, hits[("subagent", "spec-runner", MODEL)], 4)
        self.assertNotIn("total", data)

    def test_a_cold_request_is_counted_after_its_gap(self):
        store(self.home, usage())
        log(self.home)
        data = self.measure()[1]
        gaps = {(g["role"], g["model"], g["gap"]): g for g in data["gaps"]}
        cold = gaps[("subagent", MODEL, ">60m")]
        self.assertEqual((1, 1, 8000, 1.0), (cold["requests"], cold["cold"], cold["coldTokens"],
                                              cold["coldRate"]))
        warm = gaps[("main", MODEL, "10-30m")]
        self.assertEqual((1, 0), (warm["requests"], warm["cold"]))

    def test_usd_is_opt_in_and_null_for_a_model_the_table_does_not_price(self):
        store(self.home, usage())
        log(self.home)
        plain = self.measure()[1]
        self.assertNotIn("usd", plain["rows"][0])
        priced = self.measure("--usd")[1]
        self.assertTrue(all(row["usd"] is None for row in priced["rows"]))
        self.assertIn("list price", priced["pricing"]["basis"])

    def test_all_includes_the_copilot_store_and_a_session_narrows_it(self):
        store(self.home, usage())
        log(self.home)
        data = run("--harness", "all", "--copilot-home", str(self.home),
                   "--directory", str(CWD), "--json")[1]
        self.assertEqual({MODEL, "other"}, {r["model"] for r in data["rows"]})
        self.assertIn("opencode", data["unavailable"])     # no OpenCode database in this fixture
        narrowed = self.measure("--session", "s1")[1]
        self.assertEqual(6, sum(r["requests"] for r in narrowed["rows"]))
        code, missing = self.measure("--session", "nope")
        self.assertEqual((2, "se-no-usage"), (code, missing["code"]))

    def test_a_missing_store_is_unavailable_and_the_other_harnesses_still_answer(self):
        code, data = run("--harness", "all", "--copilot-home", str(self.home),
                         "--directory", str(CWD), "--json")
        self.assertEqual(2, code)
        self.assertIn("no Copilot session store", data["unavailable"]["copilot"])
        missing = self.measure()
        self.assertEqual(2, missing[0])
        self.assertEqual("se-no-usage", missing[1]["code"])
        self.assertIn("no Copilot session store", missing[1]["unavailable"]["copilot"])

    def test_inflow_names_the_copilot_gap_instead_of_pretending_to_read_it(self):
        store(self.home, usage())
        log(self.home)
        code, data = self.measure("--inflow")
        self.assertEqual(2, code)
        self.assertIn("not read by --inflow", data["unavailable"]["copilot"])


class CacheCopilotAnalysis(CacheCopilot):
    def test_a_cache_write_is_reported_and_an_inverted_read_clamps_to_zero(self):
        store(self.home, [
            ("s1", None, MODEL, 10_000, 5, 0, 3_000, 0, None, "2026-11-25T10:00:00Z"),
            ("s1", None, MODEL, 10_000, 5, 20_000, 0, 0, None, "2026-11-25T10:10:00Z")])
        log(self.home)
        code, data = self.measure()
        self.assertEqual(1, code)                        # the inverted record is a finding
        self.assertIn("more cache tokens than prompt tokens", data["anomalies"][0]["message"])
        row = data["rows"][0]
        self.assertEqual((3_000, 7_000), (row["cacheWrite"], row["input"]))   # the write is prompt too
        self.assertEqual(3_750, data["rows"][0]["ttl"]["writeNow"])  # 3000 writes at the 5-minute rate

    def test_a_boundary_needs_ten_requests_in_the_bucket(self):
        rows = [("s1", None, MODEL, 10_000, 5, 0, 0, 0, None,
                 f"2026-11-25T{hour:02d}:00:00Z") for hour in range(10, 21)]
        store(self.home, rows)
        log(self.home)
        data = self.measure()[1]
        self.assertEqual([{"harness": "copilot", "model": MODEL, "role": "main",
                           "coldFromGap": ">60m"}], data["boundaries"])

    def test_since_keeps_only_the_window(self):
        store(self.home, usage())
        log(self.home)
        data = self.measure("--since", "2026-11-25T10:15:00Z")[1]
        rows = {(r["role"], r["agent"], r["model"]): r["input"] for r in data["rows"]}
        self.assertEqual(3, sum(r["requests"] for r in data["rows"]))
        self.assertEqual(10_000, rows[("subagent", "spec-runner", MODEL)])
        self.assertEqual(12_000, rows[("main", "main", "other")])

    def test_every_row_carries_the_same_shape_as_the_other_harnesses(self):
        store(self.home, usage())
        log(self.home)
        row = self.measure()[1]["rows"][0]
        for key in ("harness", "host", "model", "role", "agent", "sessions", "requests", "input",
                    "cacheRead", "cacheWrite", "output", "hitRate", "firstRequestMedian",
                    "peakMedian", "readAfterGap5m", "missedAfterGap5to60", "ttl"):
            self.assertIn(key, row)
