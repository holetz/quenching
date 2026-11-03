"""`cache` reads Claude JSONL and the OpenCode database into one shape, never opens content and
never sums across models."""
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

MINUTE = 60_000
START = 1_790_000_000_000


def assistant(mid, at, model="opus", inp=0, read=0, write=0, out=1, ttl1h=0):
    usage = {"input_tokens": inp, "cache_read_input_tokens": read, "cache_creation_input_tokens": write,
             "output_tokens": out, "cache_creation": {"ephemeral_1h_input_tokens": ttl1h,
                                                      "ephemeral_5m_input_tokens": write - ttl1h}}
    return {"type": "assistant", "timestamp": at, "message": {"id": mid, "model": model, "usage": usage}}


def run(*argv):
    args = build_parser().parse_args(["cache", *argv])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
        code = args.func(args)
    return code, buf.getvalue()


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.projects = self.root / "projects"
        patcher = mock.patch.dict(os.environ, {"QUENCHING_TRANSCRIPTS_ROOT": str(self.projects)})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.db = self.root / "opencode.db"

    def claude(self):
        project = self.projects / "-p"
        sub = project / "s1" / "subagents"
        sub.mkdir(parents=True)
        (project / "s1.jsonl").write_text("\n".join(json.dumps(r) for r in [
            assistant("m1", "2026-10-01T10:00:00Z", write=10000, ttl1h=10000),
            assistant("m2", "2026-10-01T10:30:00Z", read=10000, write=100, ttl1h=100),
            assistant("x", "2026-10-01T10:30:01Z", model="<synthetic>"),
        ]) + "\n")
        (sub / "agent-a.jsonl").write_text("\n".join(json.dumps(r) for r in [
            assistant("s1", "2026-10-01T10:00:00Z", model="sonnet", write=8000),
            assistant("s2", "2026-10-01T10:07:00Z", model="sonnet", write=8000),
        ]) + "\n")
        (sub / "agent-a.meta.json").write_text('{"agentType":"quenching-specs:verifier"}')

    def opencode(self, content="SECRET"):
        db = sqlite3.connect(self.db)
        db.executescript("""
            CREATE TABLE session (id TEXT, parent_id TEXT, agent TEXT, directory TEXT);
            CREATE TABLE session_v2 (id TEXT, parent_id TEXT, agent TEXT, directory TEXT);
            CREATE TABLE session_message (id TEXT, session_id TEXT, type TEXT, seq INT, data TEXT);
            CREATE TABLE message (id TEXT, session_id TEXT, time_created INT, data TEXT);
            CREATE TABLE instruction_state (session_id TEXT, current_values TEXT);
            CREATE TABLE instruction_blob (hash TEXT, value TEXT);""")
        db.executemany("INSERT INTO session_v2 VALUES (?,?,?,?)", [
            ("root", None, "build", "/repo"), ("kid", "root", "quenching-spec-runner", "/elsewhere"),
            ("other", None, "build", "/other")])
        db.execute("INSERT INTO session VALUES ('old', NULL, 'build', '/repo')")
        steps = [("root", "assistant", 0, 6000, 0), ("root", "assistant", 1, 100, 6000),
                 ("root", "assistant", 40, 7000, 0), ("kid", "assistant", 0, 9000, 0),
                 ("root", "compaction", 41, 50, 3000), ("other", "assistant", 0, 5000, 0)]
        for n, (sid, kind, minute, inp, read) in enumerate(steps):
            db.execute("INSERT INTO session_message VALUES (?,?,?,?,?)", (
                f"m{n}", sid, kind, n, json.dumps({
                    "time": {"created": START + minute * MINUTE}, "model": {"id": "deepseek"},
                    "content": content,
                    "tokens": {"input": inp, "output": 2, "reasoning": 3, "cache": {"read": read, "write": 0}}})))
        db.execute("INSERT INTO session_message VALUES ('u', 'root', 'user', 9, ?)", (json.dumps({"text": content}),))
        db.execute("INSERT INTO message VALUES ('l', 'old', 1, ?)", (json.dumps({
            "role": "assistant", "modelID": "deepseek", "time": {"created": START},
            "tokens": {"input": 11, "output": 1, "reasoning": 0, "cache": {"read": 0, "write": 0}}}),))
        listing = json.dumps([{"name": "a", "description": "x" * 39}, {"name": "b", "description": "y" * 39}])
        db.execute("INSERT INTO instruction_blob VALUES ('h', ?)", (listing,))
        db.execute("INSERT INTO instruction_state VALUES ('kid', ?)", (json.dumps({"core/skill-guidance": "h"}),))
        db.commit()
        db.close()


class ClaudeTests(Fixture):
    def setUp(self):
        super().setUp()
        self.claude()

    def test_roles_ttl_and_synthetic(self):
        code, out = run("--harness", "claude", "--all", "--json")
        data = json.loads(out)
        self.assertEqual(code, 0)
        rows = {r["role"]: r for r in data["rows"]}
        self.assertEqual(len(data["rows"]), 2, "a synthetic record is no request")
        self.assertEqual((rows["main"]["requests"], rows["main"]["write1h"]), (2, 10100))
        self.assertEqual((rows["subagent"]["agent"], rows["subagent"]["write5m"]), ("verifier", 16000))

    def test_a_write_is_a_miss(self):
        data = json.loads(run("--harness", "claude", "--all", "--json")[1])
        sub = [g for g in data["gaps"] if g["role"] == "subagent"]
        self.assertEqual([(g["gap"], g["cold"]) for g in sub], [("5-10m", 1)])
        main = [g for g in data["gaps"] if g["role"] == "main"]
        self.assertEqual([(g["gap"], g["cold"]) for g in main], [("30-60m", 0)])


class OpenCodeTests(Fixture):
    def setUp(self):
        super().setUp()
        self.opencode()
        self.argv = ("--harness", "opencode", "--opencode-db", str(self.db), "--json")

    def test_scope_follows_the_root_session(self):
        data = json.loads(run(*self.argv, "--directory", "/repo")[1])
        rows = {(r["role"], r["agent"]): r for r in data["rows"]}
        self.assertEqual(set(rows), {("main", "main"), ("subagent", "spec-runner")})
        self.assertEqual(rows[("main", "main")]["requests"], 5, "v2 steps, the compaction, the legacy row")
        self.assertEqual(rows[("main", "main")]["sessions"], 2)

    def test_reasoning_counts_as_output(self):
        data = json.loads(run(*self.argv, "--directory", "/repo")[1])
        kid = next(r for r in data["rows"] if r["role"] == "subagent")
        self.assertEqual((kid["input"], kid["cacheRead"], kid["output"]), (9000, 0, 5))

    def test_input_is_the_miss(self):
        data = json.loads(run(*self.argv, "--directory", "/repo")[1])
        cold = {g["gap"]: (g["cold"], g["coldTokens"]) for g in data["gaps"]}
        self.assertEqual(cold["30-60m"], (1, 7000))
        self.assertEqual(cold["<2m"][0], 0)

    def test_skill_listing_is_measured_for_opencode(self):
        data = json.loads(run(*self.argv, "--directory", "/repo")[1])
        self.assertEqual(data["skillListing"], [{"harness": "opencode", "role": "subagent", "agent": "spec-runner",
                                                 "sessions": 1, "entriesMedian": 2, "charsMedian": 80,
                                                 "tokensEstimate": 20}])

    def test_content_never_reaches_the_output(self):
        self.assertNotIn("SECRET", run(*self.argv, "--all")[1])

    def test_a_directory_outside_the_scope_is_empty(self):
        code, out = run(*self.argv, "--directory", "/nowhere")
        self.assertNotEqual(code, 0)
        self.assertIn("se-no-usage", out)

    def test_unknown_schema_is_an_anomaly_not_a_crash(self):
        empty = self.root / "empty.db"
        sqlite3.connect(empty).close()
        self.claude()
        code, out = run("--opencode-db", str(empty), "--all", "--json")
        data = json.loads(out)
        self.assertEqual(code, 1)
        self.assertIn("no OpenCode session tables", data["anomalies"][0]["message"])


class SourcesTests(Fixture):
    def test_a_missing_store_does_not_hide_the_other(self):
        self.claude()
        data = json.loads(run("--opencode-db", str(self.root / "absent.db"), "--all", "--json")[1])
        self.assertIn("no OpenCode database", data["unavailable"]["opencode"])
        self.assertTrue(data["rows"])

    def test_models_never_sum(self):
        self.claude()
        self.opencode()
        data = json.loads(run("--opencode-db", str(self.db), "--all", "--json")[1])
        self.assertEqual({r["model"] for r in data["rows"]}, {"opus", "sonnet", "deepseek"})
        self.assertNotIn("total", data)

    def test_bad_since_is_refused(self):
        self.assertIn("se-bad-since", run("--since", "ontem", "--json")[1])

    def test_boundary_needs_a_real_sample(self):
        from quenching.session.commands.cache import Req, summarize
        from datetime import datetime, timedelta, timezone
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)

        def req(minute, inp, read):
            return Req("h", "s", "main", "main", "m", base + timedelta(minutes=minute), inp, read, 0, 0, 0, 1)
        few = summarize([req(0, 9000, 0), req(7, 9000, 0)])[2]
        self.assertEqual(few[0]["coldFromGap"], None)
        many = [req(n * 7, 9000, 0) for n in range(11)]
        self.assertEqual(summarize(many)[2][0]["coldFromGap"], "5-10m")


if __name__ == "__main__":
    unittest.main()
