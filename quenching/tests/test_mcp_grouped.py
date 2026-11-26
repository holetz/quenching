"""The grouped surface (`mcp/grouped.py`): one published tool per pillar and class, the verb as an
argument, every logical verb still reachable with the same dispatch."""

import json
import pathlib
import sys
import unittest
from unittest import mock

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "assets" / "bin"))

try:
    import _paths  # noqa: F401
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401

from quenching.mcp import catalog, cli as mcp_cli, grouped, server  # noqa: E402
from quenching.specs import mcp as specs_mcp  # noqa: E402


def rpc(request_id, method, params=None):
    message = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        message["params"] = params
    return message


def logical_names() -> list[str]:
    return [*catalog.CATALOG, *specs_mcp.TOOLS, *specs_mcp.WRITES]


class TheGroups(unittest.TestCase):
    def test_every_logical_tool_has_one_group_named_pillar_and_class(self):
        for name in logical_names():
            pillar, verb = grouped.split(name)
            group = grouped.group_of(name)
            self.assertEqual(f"{pillar}_{grouped.logical_class(name)}", group, name)
            self.assertEqual(name, grouped.logical(group, verb), name)

    def test_specs_push_is_external_and_the_other_hand_written_writes_are_write(self):
        self.assertEqual("specs_external", grouped.group_of("specs_push"))
        self.assertEqual("specs_write", grouped.group_of("specs_section_write"))
        self.assertEqual("specs_read", grouped.group_of("specs_status"))

    def test_a_verb_of_another_class_is_not_served_by_the_group(self):
        self.assertIsNone(grouped.logical("git_read", "commit"))
        self.assertEqual("git_commit", grouped.logical("git_write", "commit"))

    def test_no_verb_takes_an_argument_named_like_the_grouped_ones(self):
        for tool in mcp_cli.surface().inner.list_tools():
            props = tool["inputSchema"].get("properties", {})
            self.assertNotIn("verb", props, tool["name"])
            self.assertNotIn("of", props, tool["name"])


class ThePublishedList(unittest.TestCase):
    def setUp(self):
        self.surface = mcp_cli.surface()
        self.tools = self.surface.list_tools()

    def test_the_whole_server_publishes_one_tool_per_pillar_and_class(self):
        expected = {grouped.group_of(name) for name in self.surface._names()}
        self.assertEqual(expected, {tool["name"] for tool in self.tools})
        self.assertLessEqual(len(self.tools), 24)

    def test_the_core_mount_publishes_at_most_eight(self):
        tools = mcp_cli.surface(only=catalog.MOUNTS["core"]).list_tools()
        self.assertLessEqual(len(tools), 8)
        self.assertEqual({"specs", "git", "components"},
                         {tool["name"].rsplit("_", 1)[0] for tool in tools})

    def test_each_tool_enumerates_its_verbs_and_help(self):
        by_name = {tool["name"]: tool for tool in self.tools}
        verbs = by_name["git_read"]["inputSchema"]["properties"]["verb"]["enum"]
        self.assertIn("state", verbs)
        self.assertIn("help", verbs)
        self.assertNotIn("commit", verbs)
        self.assertEqual(["verb"], by_name["git_read"]["inputSchema"]["required"])

    def test_annotations_hold_for_the_whole_tool(self):
        by_name = {tool["name"]: tool["annotations"] for tool in self.tools}
        self.assertTrue(by_name["git_read"]["readOnlyHint"])
        self.assertFalse(by_name["git_write"]["readOnlyHint"])
        self.assertTrue(by_name["git_write"]["destructiveHint"])   # worktree retire
        self.assertTrue(by_name["git_external"]["openWorldHint"])
        self.assertTrue(by_name["specs_external"]["openWorldHint"])

    def test_the_list_is_far_smaller_than_one_tool_per_verb(self):
        per_verb = len(json.dumps(self.surface.inner.list_tools()))
        self.assertLess(len(json.dumps(self.tools)), per_verb // 3)


class TheCall(unittest.TestCase):
    def setUp(self):
        self.surface = mcp_cli.surface()

    def test_a_verb_goes_to_the_wrapped_surface_under_its_logical_name(self):
        with mock.patch.object(self.surface.inner, "call_tool",
                               return_value=({"ok": True}, False)) as call:
            payload, failed = self.surface.call_tool(
                "git_read", {"verb": "state", "root": "/w"}, "/x", None)
        self.assertEqual(({"ok": True}, False), (payload, failed))
        call.assert_called_once_with("git_state", {"root": "/w"}, "/x", None)

    def test_an_unknown_or_missing_verb_is_refused_with_the_verbs(self):
        for args in ({}, {"verb": "commit"}, {"verb": 3}):
            payload, failed = self.surface.call_tool("git_read", args, "/x", None)
            self.assertTrue(failed)
            self.assertEqual("mcp-unknown-verb", payload["code"])
            self.assertIn("state", payload["verbs"])

    def test_a_bad_argument_comes_back_with_the_verbs_schema(self):
        payload, failed = self.surface.call_tool(
            "git_read", {"verb": "state", "nope": 1}, "/x", None)
        self.assertTrue(failed)
        self.assertEqual("mcp-bad-arguments", payload["code"])
        self.assertIn("properties", payload["inputSchema"])

    def test_help_returns_each_verbs_schema_or_one(self):
        payload, failed = self.surface.call_tool("git_read", {"verb": "help"}, "/x", None)
        self.assertFalse(failed)
        self.assertIn("state", [entry["verb"] for entry in payload["verbs"]])
        payload, failed = self.surface.call_tool(
            "specs_write", {"verb": "help", "of": "section_write"}, "/x", None)
        self.assertFalse(failed)
        self.assertEqual(["section_write"], [entry["verb"] for entry in payload["verbs"]])
        self.assertIn("sections", payload["verbs"][0]["inputSchema"]["properties"])

    def test_the_protocol_lists_and_calls_the_grouped_names(self):
        tools = server.handle(rpc(1, "tools/list"), "/x", None, self.surface)["result"]["tools"]
        self.assertIn("specs_read", {tool["name"] for tool in tools})
        self.assertNotIn("specs_status", {tool["name"] for tool in tools})
        reply = server.handle(rpc(2, "tools/call", {"name": "specs_status", "arguments": {}}),
                              "/x", None, self.surface)
        self.assertIn("error", reply)

    def test_the_specs_only_server_is_grouped_too(self):
        surface = grouped.GroupedSurface(specs_mcp.SURFACE)
        self.assertEqual({"specs_read", "specs_write", "specs_external"},
                         {tool["name"] for tool in surface.list_tools()})


if __name__ == "__main__":
    unittest.main()
