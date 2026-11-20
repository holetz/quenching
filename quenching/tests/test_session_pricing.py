"""quenching's one price table: what `cq components session cost|cache --usd` and the
`quenching-cache` plugin price with, and the gate's refusal of an unusable or stale copy."""
import contextlib
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.session import pricing
from quenching.session.commands.cli import build_parser

REPO = pathlib.Path(__file__).resolve().parents[2]


class TheTable(unittest.TestCase):
    def test_the_shipped_table_is_usable(self):
        self.assertEqual([], pricing.problems())

    def test_exact_version_match_prefixes_and_tiers(self):
        self.assertEqual("opus-5-5", pricing.model_key("us.anthropic.claude-opus-5-5-20260401"))
        self.assertIsNone(pricing.model_key("claude-3-7-sonnet-20250219"))
        self.assertIsNone(pricing.rates("claude-opus-5-6"))      # not Opus 5's price
        self.assertEqual(4, pricing.rates("claude-opus-5-5")["input"])
        self.assertEqual(8, pricing.rates("claude-opus-5-5-fast")["input"])
        self.assertEqual(0.5, pricing.rates("claude-haiku-5-5", 150_000)["input"])
        self.assertEqual(8, pricing.rates("claude-opus-5-5")["write1h"])
        self.assertEqual(5, pricing.rates("claude-opus-5-5")["write5m"])

    def test_usd_worked_by_hand(self):
        # 228K read at $0.20/M + 1K written for 1h at $8/M + 100 output at $20/M
        self.assertAlmostEqual(0.0456 + 0.008 + 0.002, pricing.usd(
            "claude-opus-5-5", cache_read=228_000, write1h=1_000, output=100))
        self.assertIsNone(pricing.usd("gpt-x", input=1))

    def test_problems_name_an_implausible_table(self):
        bad = {"sourceDate": "2026-1-1", "output": 5, "fast": 2, "cacheWrite": {"5m": 1.25},
               "models": {"Opus 6": {"input": 5, "cacheRead": 6}}}
        found = pricing.problems(bad)
        self.assertTrue(any("sourceDate" in p for p in found))
        self.assertTrue(any("family-version" in p for p in found))
        self.assertTrue(any("implausible" in p for p in found))
        self.assertTrue(any("cacheWrite" in p for p in found))


def assistant(mid, at, model="claude-opus-5-5", read=0, write=0, ttl1h=0, out=0):
    usage = {"input_tokens": 0, "cache_read_input_tokens": read, "cache_creation_input_tokens": write,
             "output_tokens": out, "cache_creation": {"ephemeral_1h_input_tokens": ttl1h,
                                                      "ephemeral_5m_input_tokens": write - ttl1h}}
    return {"type": "assistant", "timestamp": at, "message": {"id": mid, "model": model, "usage": usage}}


class CacheUsdAndSession(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.projects = pathlib.Path(tmp.name) / "projects"
        project = self.projects / "-p"
        project.mkdir(parents=True)
        (project / "chat-a.jsonl").write_text("\n".join(json.dumps(r) for r in [
            assistant("a1", "2026-10-01T10:00:00Z", write=1_000_000, ttl1h=1_000_000),
            assistant("a2", "2026-10-01T10:10:00Z", read=1_000_000)]) + "\n")
        (project / "chat-b.jsonl").write_text(json.dumps(
            assistant("b1", "2026-10-01T11:00:00Z", model="claude-opus-9", write=10)) + "\n")
        patcher = mock.patch.dict(os.environ, {"QUENCHING_TRANSCRIPTS_ROOT": str(self.projects)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_cache(self, *argv):
        args = build_parser().parse_args(["cache", "--harness", "claude", "--directory", "/p", "--json", *argv])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            args.func(args)
        return json.loads(buf.getvalue())

    def test_usd_is_opt_in_per_row_and_null_for_an_unpriced_model(self):
        plain = self.run_cache()
        self.assertNotIn("usd", plain["rows"][0])
        self.assertNotIn("pricing", plain)
        priced = {r["model"]: r["usd"] for r in self.run_cache("--usd")["rows"]}
        self.assertEqual(8.2, priced["claude-opus-5-5"])  # 1M written 1h at $8/M + 1M read at $0.20/M
        self.assertIsNone(priced["claude-opus-9"])
        self.assertEqual(pricing.table()["sourceDate"], self.run_cache("--usd")["pricing"]["sourceDate"])

    def test_session_narrows_to_one_chat(self):
        rows = self.run_cache("--session", "chat-a")["rows"]
        self.assertEqual(["claude-opus-5-5"], [r["model"] for r in rows])
        self.assertEqual(2, rows[0]["requests"])


class CostUsd(unittest.TestCase):
    def test_each_group_and_model_row_is_priced_at_the_5m_floor(self):
        from quenching.session.commands.cost import price_rows
        row = {"model": "claude-opus-5-5", "input": 0, "cacheRead": 1_000_000, "cacheWrite": 1_000_000, "output": 0}
        out = {"groups": [dict(row, agentType="a")], "byModel": [dict(row)]}
        price_rows(out)
        self.assertEqual([5.2, 5.2], [r["usd"] for r in out["groups"] + out["byModel"]])
        self.assertIn("5-minute", out["pricing"]["basis"])


class PluginCommands(unittest.TestCase):
    def test_a_marketplace_plugin_declares_the_commands_it_registers(self):
        import shutil
        from quenching.common.modules import load_manifest
        self.assertEqual(["quenching-cache"], next(p for p in load_manifest(REPO)["plugins"]
                                                   if p["name"] == "quenching-cache")["commands"])
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            shutil.copytree(REPO / "quenching", root / "quenching",
                            ignore=shutil.ignore_patterns("tests", "__pycache__"))
            path = root / "quenching" / "assets" / "modules.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            for entry in data["plugins"]:
                (root / entry["path"]).mkdir(parents=True, exist_ok=True)
            data["plugins"][0]["commands"] = "quenching-cache"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "commands must be a list"):
                load_manifest(root)


class TheGeneratedCopies(unittest.TestCase):
    def test_the_plugin_copies_are_current(self):
        run = subprocess.run([sys.executable, str(REPO / "scripts" / "cache_plugin_sync.py"), "--check"],
                             capture_output=True, text=True)
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
