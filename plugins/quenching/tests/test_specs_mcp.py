"""`cq specs mcp` — the MCP read surface over stdio, a second port of the CLI's own core.

The protocol is driven twice: through a real subprocess pipe (stdout must carry JSON-RPC lines
only), and in-process against the memory backend for the tools, where the store is the fake the
rest of the specs suite uses.
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

try:
    import _paths  # noqa: F401  — must precede the `quenching` import
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.specs import backends as backends_mod
from quenching.specs import mcp
from quenching.specs.backends.memory import MemoryBackend

CQ = pathlib.Path(__file__).resolve().parent.parent / "assets" / "bin" / "cq"
DOC = ("---\ntitle: {title}\ndate: 2026-01-01\n---\n\n## Problem\n\n{problem}\n\n"
       "## Tasks\n\n### 1. First\n\n- [x] 1.1 one\n- [ ] 1.2 two\n")
TOOL_NAMES = {"specs_list", "specs_status", "specs_show", "specs_section", "specs_next",
              "specs_epic_progress"}
WRITE_VERBS = {"new", "section --write", "record", "task", "discover", "promote", "migrate",
               "serve", "release", "verification", "title", "tags"}


def rpc(request_id, method, params=None):
    message = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        message["params"] = params
    return message


class Stdio(unittest.TestCase):
    """The real process: only protocol lines on stdout, a notification gets no reply."""

    def test_the_pipe_carries_json_rpc_lines_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "init", "-q", tmp], check=True)
            lines = [rpc(1, "initialize", {"protocolVersion": "2025-06-18"}),
                     {"jsonrpc": "2.0", "method": "notifications/initialized"},
                     rpc(2, "tools/list"), rpc(3, "nope")]
            run = subprocess.run(
                [sys.executable, str(CQ), "--root", tmp, "specs", "mcp"],
                input="\n".join(json.dumps(m) for m in lines) + "\nnot json\n",
                capture_output=True, text=True, timeout=60)
        self.assertEqual(run.returncode, 0, run.stderr)
        replies = [json.loads(line) for line in run.stdout.splitlines()]
        self.assertEqual([r["id"] for r in replies], [1, 2, 3, None])
        self.assertEqual(replies[0]["result"]["protocolVersion"], "2025-06-18")
        self.assertEqual({t["name"] for t in replies[1]["result"]["tools"]}, TOOL_NAMES)
        self.assertEqual(replies[2]["error"]["code"], -32601)
        self.assertEqual(replies[3]["error"]["code"], -32700)


class Protocol(unittest.TestCase):
    def test_initialize_falls_back_to_a_supported_version(self):
        reply = mcp.handle(rpc(1, "initialize", {"protocolVersion": "1999-01-01"}), "/x")
        self.assertEqual(reply["result"]["protocolVersion"], mcp.PROTOCOL_VERSIONS[0])
        self.assertEqual(set(reply["result"]["capabilities"]), {"tools"})

    def test_a_notification_gets_no_reply_and_ping_answers(self):
        self.assertIsNone(mcp.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}, "/x"))
        self.assertEqual(mcp.handle(rpc(7, "ping"), "/x")["result"], {})

    def test_an_unknown_tool_is_a_protocol_error(self):
        reply = mcp.handle(rpc(1, "tools/call", {"name": "specs_write", "arguments": {}}), "/x")
        self.assertEqual(reply["error"]["code"], -32602)

    def test_every_tool_is_read_only_and_none_names_a_write_verb(self):
        listed = mcp.handle(rpc(1, "tools/list"), "/x")["result"]["tools"]
        self.assertEqual({t["name"] for t in listed}, TOOL_NAMES)
        for tool in listed:
            self.assertTrue(tool["annotations"]["readOnlyHint"])
            self.assertFalse(tool["inputSchema"]["additionalProperties"])

    def test_no_tool_builds_a_write_verb(self):
        samples = {"specs_list": {}, "specs_status": {"spec": 1}, "specs_show": {"spec": 1},
                   "specs_section": {"spec": 1, "headings": "Problem"}, "specs_next": {},
                   "specs_epic_progress": {"epic": 1}}
        for name, args in samples.items():
            argv = TOOLS_BUILD(name, args)
            self.assertNotIn("--write", argv)
            self.assertNotIn(argv[0], WRITE_VERBS, name)


def TOOLS_BUILD(name, args):
    return mcp.TOOLS[name][2](args)


class Arguments(unittest.TestCase):
    def test_an_argument_that_looks_like_a_flag_is_refused_before_the_core_runs(self):
        for name, args in (("specs_status", {"spec": "--help"}),
                           ("specs_section", {"spec": 1, "headings": "--write"}),
                           ("specs_show", {"spec": 1, "tasks": ["--full"]}),
                           ("specs_status", {"spec": "1;rm"}), ("specs_status", {})):
            payload, failed = mcp.call_tool(name, args, "/x")
            self.assertTrue(failed, (name, args))
            self.assertEqual(payload["code"], "mcp-bad-arguments")

    def test_section_needs_exactly_one_of_headings_or_moment(self):
        for args in ({"spec": 1}, {"spec": 1, "headings": "Problem", "moment": "build"}):
            self.assertTrue(mcp.call_tool("specs_section", args, "/x")[1])


class Tools(unittest.TestCase):
    def setUp(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp(prefix="quenching-mcp-"))
        self.addCleanup(__import__("shutil").rmtree, self.tmp, True)
        subprocess.run(["git", "init", "-q", self.tmp], check=True)
        self.backend = MemoryBackend()
        backends_mod._BACKEND_CACHE.clear()
        backends_mod._BACKEND_CACHE[self.tmp] = self.backend
        self.addCleanup(backends_mod._BACKEND_CACHE.clear)
        for title in ("Alpha", "Beta", "Gamma"):
            self.backend.create_spec("plans", DOC.format(title=title, problem="Something."))
        self.backend.create_spec("plans", DOC.format(title="Big", problem="word " * 20000))

    def call(self, name, args=None):
        payload, failed = mcp.call_tool(name, args or {}, self.tmp)
        return payload, failed

    def test_list_pages_with_a_next_offset(self):
        payload, failed = self.call("specs_list", {"limit": 3})
        self.assertFalse(failed)
        self.assertEqual((payload["returned"], payload["count"], payload["nextOffset"]), (3, 4, 3))
        payload, _ = self.call("specs_list", {"limit": 3, "offset": 3})
        self.assertEqual((payload["returned"], payload["nextOffset"]), (1, None))

    def test_status_names_the_stage_and_carries_no_section_body(self):
        payload, failed = self.call("specs_status", {"spec": 1})
        self.assertFalse(failed)
        self.assertEqual(payload["id"], 1)
        self.assertNotIn("Something.", json.dumps(payload))

    def test_show_returns_the_map_or_only_the_named_task(self):
        payload, _ = self.call("specs_show", {"spec": 1})
        self.assertEqual(payload["view"], "index")
        payload, _ = self.call("specs_show", {"spec": 1, "tasks": ["1.2"]})
        self.assertEqual([t["id"] for t in payload["tasks"]], ["1.2"])

    def test_section_reads_the_named_headings(self):
        payload, failed = self.call("specs_section", {"spec": 1, "headings": "Problem,Tasks"})
        self.assertFalse(failed)
        self.assertEqual([s["heading"] for s in payload["sections"]], ["Problem", "Tasks"])

    def test_an_answer_above_the_ceiling_is_cut_and_flagged(self):
        payload, failed = self.call("specs_section", {"spec": 4, "headings": "Problem"})
        self.assertFalse(failed)
        self.assertTrue(payload["truncated"])
        self.assertGreater(payload["chars"], mcp.MAX_CHARS)
        self.assertEqual(len(payload["text"]), mcp.MAX_CHARS)
        wire = mcp.handle(rpc(1, "tools/call", {"name": "specs_section", "arguments":
                                                {"spec": 4, "headings": "Problem"}}), self.tmp)
        text = wire["result"]["content"][0]["text"]
        self.assertLess(len(text), mcp.MAX_CHARS * 2 + 1000)
        self.assertTrue(json.loads(text)["truncated"])

    def test_next_pages_the_front_and_answers_for_one_spec(self):
        payload, _ = self.call("specs_next", {"limit": 2})
        self.assertEqual(len(payload["candidates"]), 2)
        self.assertEqual(payload["nextOffset"], 2)
        payload, _ = self.call("specs_next", {"spec": 1})
        self.assertEqual(payload["id"], 1)

    def test_a_refusal_is_a_tool_error_carrying_the_cli_code(self):
        payload, failed = self.call("specs_epic_progress", {"epic": 1})
        self.assertTrue(failed)
        self.assertEqual(payload["code"], "sp-epic-not-an-epic")
        payload, _ = self.call("specs_status", {"spec": 999})
        self.assertEqual((payload["ok"], payload["code"]), (False, "sp-unknown-id"))

    def test_a_core_exit_two_is_flagged_is_error(self):
        backends_mod._BACKEND_CACHE.clear()
        payload, failed = mcp.call_tool("specs_list", {}, self.tmp)
        self.assertTrue(failed)
        self.assertFalse(payload["ok"])


if __name__ == "__main__":
    unittest.main()
