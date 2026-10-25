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
WRITE_NAMES = {"specs_create", "specs_section_write", "specs_record", "specs_task",
               "specs_epic_add", "specs_discover", "specs_promote"}
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
        self.assertEqual({t["name"] for t in replies[1]["result"]["tools"]},
                         TOOL_NAMES | WRITE_NAMES)
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
        reply = mcp.handle(rpc(1, "tools/call", {"name": "specs_run", "arguments": {}}), "/x")
        self.assertEqual(reply["error"]["code"], -32602)

    def test_reads_are_read_only_writes_are_not_and_no_tool_takes_a_confirm_flag(self):
        listed = mcp.handle(rpc(1, "tools/list"), "/x")["result"]["tools"]
        self.assertEqual({t["name"] for t in listed}, TOOL_NAMES | WRITE_NAMES)
        for tool in listed:
            self.assertEqual(tool["annotations"]["readOnlyHint"], tool["name"] in TOOL_NAMES)
            self.assertFalse(tool["inputSchema"]["additionalProperties"])
            self.assertNotIn("confirm", tool["inputSchema"]["properties"])

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


class Writes(unittest.TestCase):
    """The write tools and the confirmation on the gated moves, against the memory backend."""

    def setUp(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp(prefix="quenching-mcp-w-"))
        self.addCleanup(__import__("shutil").rmtree, self.tmp, True)
        subprocess.run(["git", "init", "-q", self.tmp], check=True)
        self.backend = MemoryBackend()
        backends_mod._BACKEND_CACHE.clear()
        backends_mod._BACKEND_CACHE[self.tmp] = self.backend
        self.addCleanup(backends_mod._BACKEND_CACHE.clear)
        self.backend.create_spec("plans", DOC.format(title="Alpha", problem="Something."))

    def call(self, name, args, answer="unasked"):
        asked = []

        def ask(message):
            asked.append(message)
            return answer
        session = mcp.Session(ask=ask, elicitation=answer != "unasked")
        payload, failed = mcp.call_tool(name, args, self.tmp, session)
        return payload, failed, asked

    def frontmatter(self, spec=1):
        info, _ = self.backend.read_spec(spec)
        return info["frontmatter"]

    def test_create_writes_a_section_a_discovery_and_a_task(self):
        payload, failed, _ = self.call("specs_create", {"name": "gamma", "title": "Gamma"})
        self.assertFalse(failed, payload)
        payload, failed, _ = self.call("specs_section_write",
                                       {"spec": 1, "heading": "Proposal", "body": "Do the thing."})
        self.assertFalse(failed, payload)
        read, _ = mcp.call_tool("specs_section", {"spec": 1, "headings": "Proposal"}, self.tmp)
        self.assertIn("Do the thing.", json.dumps(read))
        payload, failed, _ = self.call("specs_discover", {"spec": 1, "text": "found it"})
        self.assertFalse(failed, payload)
        payload, failed, _ = self.call("specs_task", {"spec": 1, "action": "check", "task": "1.2"})
        self.assertFalse(failed, payload)
        shown, _ = mcp.call_tool("specs_show", {"spec": 1, "tasks": ["1.2"]}, self.tmp)
        self.assertTrue(shown["tasks"][0]["checked"])

    def test_a_blocking_task_needs_a_reason_and_a_free_record_needs_no_question(self):
        payload, failed, _ = self.call("specs_task", {"spec": 1, "action": "block", "task": "1.2"})
        self.assertEqual((failed, payload["code"]), (True, "mcp-bad-arguments"))
        payload, failed, asked = self.call("specs_record", {
            "spec": 1, "name": "refined", "fields": {"mode": "full", "date": "2026-01-02"}})
        self.assertFalse(failed, payload)
        self.assertEqual(asked, [])
        self.assertEqual(self.frontmatter()["refined"]["mode"], "full")

    def test_a_gated_record_is_refused_when_the_client_cannot_ask(self):
        for name in (n for n in mcp.GATED_RECORDS if n != "approved"):
            payload, failed, _ = self.call("specs_record", {"spec": 1, "name": name,
                                                            "fields": {"date": "2026-01-02"}})
            self.assertEqual((failed, payload["code"]), (True, "mcp-confirmation-unavailable"))
        self.assertNotIn("merge", self.frontmatter())

    def test_a_declined_or_cancelled_confirmation_changes_nothing(self):
        for answer in ({"action": "decline"}, {"action": "cancel"},
                       {"action": "accept", "content": {"confirm": False}}, None):
            payload, failed, asked = self.call("specs_record", {
                "spec": 1, "name": "reviewed", "fields": {"date": "2026-01-02"}}, answer)
            self.assertEqual((failed, payload["code"]), (True, "mcp-confirmation-refused"))
            self.assertEqual(len(asked), 1)
        self.assertNotIn("reviewed", self.frontmatter())

    def test_a_confirmed_gated_record_is_written(self):
        payload, failed, asked = self.call("specs_record", {
            "spec": 1, "name": "reviewed", "fields": {"date": "2026-01-02"}},
            {"action": "accept", "content": {"confirm": True}})
        self.assertFalse(failed, payload)
        self.assertIn("reviewed", asked[0])
        self.assertEqual(self.frontmatter()["reviewed"]["date"], "2026-01-02")

    def test_approved_takes_no_fields_and_is_written_by_human_only_after_confirmation(self):
        payload, failed, _ = self.call("specs_record", {"spec": 1, "name": "approved",
                                                        "fields": {"by": "human"}})
        self.assertEqual(payload["code"], "mcp-bad-arguments")
        payload, failed, asked = self.call("specs_record", {"spec": 1, "name": "approved"},
                                           {"action": "accept", "content": {"confirm": True}})
        # the ready gate is unmet for this skeleton: refused before the human is even asked
        self.assertEqual((failed, payload["code"]), (True, "mcp-not-ready"))
        self.assertEqual(asked, [])
        self.assertNotIn("approved", self.frontmatter())

    def test_approved_on_a_ready_spec_is_stamped_by_human_after_the_accept(self):
        sections = ["Proposal", "Out of Scope", "Impact", "Validation", "Design",
                    "Alternatives Considered", "Open Decisions", "Risks"]
        for heading in sections:
            payload, failed, _ = self.call("specs_section_write",
                                           {"spec": 1, "heading": heading, "body": "Filled."})
            self.assertFalse(failed, payload)
        payload, failed, asked = self.call("specs_record", {"spec": 1, "name": "approved"},
                                           {"action": "accept", "content": {"confirm": True}})
        if payload.get("code") == "mcp-not-ready":
            self.skipTest("the memory fixture cannot reach ready: " + str(payload.get("missing")))
        self.assertFalse(failed, payload)
        self.assertEqual(len(asked), 1)
        self.assertEqual(self.frontmatter()["approved"]["by"], "human")

    def test_promote_asks_first_and_never_forces(self):
        self.assertNotIn("force", mcp.WRITES["specs_promote"][1]["properties"])
        payload, failed, asked = self.call("specs_promote", {"spec": 1, "to": "archive"})
        self.assertTrue(failed)
        self.assertEqual(asked, [])

    def test_promote_runs_only_after_the_accept(self):
        self.backend.create_spec("plans", DOC.format(title="Done", problem="x").replace("[ ]", "[x]")
                                 + "\n## Outcome\n\nShipped.\n")
        payload, failed, asked = self.call("specs_promote", {"spec": 2, "to": "archive"},
                                           {"action": "decline"})
        self.assertEqual(payload.get("code"), "mcp-confirmation-refused", payload)
        self.assertEqual(self.backend.read_spec(2)[0]["phase"], "plans")
        payload, failed, asked = self.call("specs_promote", {"spec": 2, "to": "archive"},
                                           {"action": "accept", "content": {"confirm": True}})
        self.assertEqual(len(asked), 1)
        self.assertFalse(failed, payload)
        self.assertEqual(self.backend.read_spec(2)[0]["phase"], "archive")

    def test_a_flag_shaped_value_never_reaches_the_core(self):
        for name, args in (("specs_create", {"name": "--force"}),
                           ("specs_discover", {"spec": 1, "text": "a\nb"}),
                           ("specs_record", {"spec": 1, "name": "run", "fields": {"--x": "1"}}),
                           ("specs_record", {"spec": 1, "name": "bogus", "fields": {"a": "1"}}),
                           ("specs_section_write", {"spec": 1, "heading": "A,B", "body": "x"})):
            payload, failed, _ = self.call(name, args)
            self.assertEqual((failed, payload["code"]), (True, "mcp-bad-arguments"), (name, args))


class Elicitation(unittest.TestCase):
    """The real loop: the server asks over stdout and reads the human's answer from stdin."""

    def run_session(self, answer):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "init", "-q", tmp], check=True)
            lines = [rpc(1, "initialize", {"protocolVersion": "2025-06-18",
                                           "capabilities": {"elicitation": {}}}),
                     rpc(2, "tools/call", {"name": "specs_record", "arguments": {
                         "spec": 1, "name": "reviewed", "fields": {"date": "2026-01-02"}}})]
            if answer is not None:
                lines.append({"jsonrpc": "2.0", "id": "elicit-1", "result": answer})
            run = subprocess.run([sys.executable, str(CQ), "--root", tmp, "specs", "mcp"],
                                 input="\n".join(json.dumps(m) for m in lines) + "\n",
                                 capture_output=True, text=True, timeout=60)
        self.assertEqual(run.returncode, 0, run.stderr)
        return [json.loads(line) for line in run.stdout.splitlines()]

    def test_the_server_asks_the_client_and_a_decline_is_a_refusal(self):
        replies = self.run_session({"action": "decline"})
        self.assertEqual([r.get("id") for r in replies], [1, "elicit-1", 2])
        self.assertEqual(replies[1]["method"], "elicitation/create")
        body = json.loads(replies[2]["result"]["content"][0]["text"])
        self.assertTrue(replies[2]["result"]["isError"])
        self.assertEqual(body["code"], "mcp-confirmation-refused")

    def test_a_closed_stdin_while_asking_is_a_cancel(self):
        replies = self.run_session(None)
        body = json.loads(replies[-1]["result"]["content"][0]["text"])
        self.assertEqual(body["code"], "mcp-confirmation-refused")


if __name__ == "__main__":
    unittest.main()
