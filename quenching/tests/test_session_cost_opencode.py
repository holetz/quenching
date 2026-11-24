"""`cost` measures the tree of an OpenCode session from its database: the root and every child session by
`parent_id`, per agent and model, never summed across models, the database opened read-only, and a refusal
with a reason where there is nothing honest to read."""
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

START = 1_790_000_000_000
CWD = str(pathlib.Path.cwd().resolve())
OPUS = '{"id":"opus","providerID":"claude-agent"}'
SONNET = '{"id":"sonnet","providerID":"claude-agent"}'


def run(*argv):
    args = build_parser().parse_args(["cost", *argv, "--json"])
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = args.func(args)
    return code, json.loads(out.getvalue())


class OpenCodeCost(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.db = self.root / "opencode.db"
        patcher = mock.patch.dict(os.environ, {"QUENCHING_OPENCODE_DB": str(self.db),
                                               "QUENCHING_TRANSCRIPTS_ROOT": str(self.root / "projects")})
        patcher.start()
        self.addCleanup(patcher.stop)
        os.environ.pop("OPENCODE_SESSION_ID", None)
        db = sqlite3.connect(self.db)
        db.execute("CREATE TABLE session_v2 (id TEXT, parent_id TEXT, agent TEXT, model TEXT, directory TEXT, "
                   "tokens_input INT, tokens_output INT, tokens_reasoning INT, tokens_cache_read INT, "
                   "tokens_cache_write INT, time_created INT, time_updated INT)")
        rows = [
            # id, parent, agent, model, input, output, reasoning, read, write, created
            ("ses_root", None, "build", OPUS, 10, 100, 5, 1000, 50, 0),
            ("ses_orch1", "ses_root", "quenching-spec-orchestrator", SONNET, 1, 10, 0, 100, 10, 1),
            ("ses_run1", "ses_orch1", "quenching-spec-runner", SONNET, 2, 20, 4, 200, 20, 2),
            ("ses_orch2", "ses_root", "quenching-spec-orchestrator", OPUS, 3, 30, 0, 300, 30, 3),
            ("ses_run2", "ses_orch2", "quenching-spec-runner", OPUS, 4, 40, 6, 400, 40, 4),
            ("ses_run3", "ses_orch2", "quenching-spec-runner", OPUS, 5, 50, 0, 500, 50, 5),
            ("ses_other", None, "build", OPUS, 99, 99, 0, 99, 99, 6),
            ("ses_otherchild", "ses_other", "explore", "not-json", 7, 7, 0, 7, 7, 7)]
        db.executemany("INSERT INTO session_v2 (id, parent_id, agent, model, tokens_input, tokens_output, "
                       "tokens_reasoning, tokens_cache_read, tokens_cache_write, time_created, directory, "
                       "time_updated) VALUES (?,?,?,?,?,?,?,?,?,?, ?, ?)",
                       [(*r[:9], START + r[9], CWD, START + r[9]) for r in rows])
        db.commit()
        db.close()

    def rows(self, data):
        return {(g["agentType"], g["model"]): g for g in data["groups"]}

    def test_the_tree_by_agent_and_model_with_no_total(self):
        code, data = run("ses_root")
        self.assertEqual(code, 0)
        self.assertEqual(data["resolvedBy"], "OpenCode session id")
        rows = self.rows(data)
        self.assertEqual(set(rows), {("main", "opus"), ("spec-orchestrator", "sonnet"), ("spec-orchestrator", "opus"),
                                     ("spec-runner", "sonnet"), ("spec-runner", "opus")})
        runner = rows[("spec-runner", "opus")]
        self.assertEqual((runner["sessions"], runner["input"], runner["cacheRead"], runner["cacheWrite"],
                          runner["output"]), (2, 9, 900, 90, 96))
        self.assertIsNone(runner["requests"])
        self.assertIsNone(runner["maxWindow"])
        self.assertEqual(rows[("main", "opus")]["output"], 105)           # output plus reasoning
        models = {m["model"]: m for m in data["byModel"]}
        self.assertEqual(models["opus"]["input"], 10 + 3 + 9)
        self.assertEqual(models["sonnet"]["sessions"], 2)
        self.assertNotIn("total", data)
        self.assertNotIn("ses_other", json.dumps(data))                    # another root is not this tree

    def test_the_running_session_is_the_default_and_the_database_flag_picks_the_newest(self):
        os.environ["OPENCODE_SESSION_ID"] = "ses_orch2"
        code, data = run()
        self.assertEqual((code, data["resolvedBy"]), (0, "OPENCODE_SESSION_ID"))
        self.assertEqual(set(self.rows(data)), {("main", "opus"), ("spec-runner", "opus")})
        os.environ.pop("OPENCODE_SESSION_ID")
        code, data = run("--opencode-db", str(self.db))
        self.assertEqual((code, data["resolvedBy"]), (0, "most recent OpenCode session in this directory"))
        self.assertIn("ses_other", data["subagents"])

    def test_scopes(self):
        _, data = run("ses_root", "--descendants-of", "ses_orch2")
        self.assertEqual({k[0] for k in self.rows(data)}, {"spec-runner"})
        self.assertEqual(data["groups"][0]["sessions"], 2)
        _, data = run("ses_root", "--nested")
        self.assertEqual({k[0] for k in self.rows(data)}, {"spec-runner"})
        self.assertEqual(sum(g["sessions"] for g in data["groups"]), 3)
        _, data = run("ses_root", "--latest-orchestrator")                  # ses_orch2 started last
        self.assertEqual(sum(g["sessions"] for g in data["groups"]), 2)
        self.assertEqual({g["model"] for g in data["groups"]}, {"opus"})
        since = "2026-09-21T14:13:20.002Z"                                  # START is 2026-09-21T14:13:20Z, in ms
        _, data = run("ses_root", "--since", since)
        self.assertEqual(sum(g["sessions"] for g in data["groups"]), 4)

    def test_usd_prices_each_model_row(self):
        _, data = run("ses_root", "--usd")
        self.assertIn("usd", data["byModel"][0])
        self.assertIn("pricing", data)

    def test_the_database_is_never_written(self):
        before = self.db.read_bytes()
        run("ses_root")
        self.assertEqual(self.db.read_bytes(), before)

    def test_a_non_opencode_argument_stays_on_the_claude_code_path(self):
        code, data = run(str(self.root / "no-such-directory"))
        self.assertEqual(code, 2)
        self.assertNotIn("OpenCode", data["message"])

    def test_refusals_say_why(self):
        code, data = run("ses_missing")
        self.assertEqual((code, data["code"]), (2, "se-no-transcript"))
        code, data = run("ses_root", "--descendants-of", "ses_other")
        self.assertEqual((code, data["code"]), (2, "se-no-transcript"))
        code, data = run("ses_orch1", "--latest-orchestrator")
        self.assertEqual((code, data["code"]), (2, "se-no-orchestrator"))
        code, data = run("ses_root", "--self", "MARK")
        self.assertEqual((code, data["code"]), (2, "se-opencode-self"))
        code, data = run("ses_root", "--since", "yesterday")
        self.assertEqual((code, data["code"]), (2, "se-bad-since"))
        self.db.unlink()
        code, data = run("ses_root")
        self.assertEqual((code, data["code"]), (2, "se-no-transcript"))
        self.assertIn("no OpenCode database", data["message"])

    def test_a_database_without_the_generation_two_table_is_refused_not_empty(self):
        with contextlib.closing(sqlite3.connect(self.db)) as db:
            db.executescript("DROP TABLE session_v2; CREATE TABLE session (id TEXT);")
        code, data = run("ses_root")
        self.assertEqual((code, data["code"]), (2, "se-no-transcript"))
        self.assertIn("session_v2", data["message"])


if __name__ == "__main__":
    unittest.main()
