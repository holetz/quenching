"""`quenching-mcp` — the catalog of CLI verbs served as MCP tools over the common core.

The schemas are derived from each pillar's own parser, so these tests read the parser back and
compare; the calls dispatch in-process through the `cq` router against a throwaway git repo.
"""
import io
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
from quenching.mcp import catalog, server


def rpc(request_id, method, params=None):
    message = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        message["params"] = params
    return message


def git_repo(tmp: str) -> str:
    subprocess.run(["git", "init", "-q", "-b", "main", tmp], check=True)
    for key, value in (("user.name", "t"), ("user.email", "t@example.invalid")):
        subprocess.run(["git", "-C", tmp, "config", key, value], check=True)
    pathlib.Path(tmp, "a.txt").write_text("a\n", encoding="utf-8")
    subprocess.run(["git", "-C", tmp, "add", "a.txt"], check=True)
    subprocess.run(["git", "-C", tmp, "commit", "-qm", "one"], check=True)
    return tmp


class Catalog(unittest.TestCase):
    def test_every_row_resolves_to_a_verb_of_its_pillar(self):
        for name, row in catalog.CATALOG.items():
            with self.subTest(name):
                self.assertIn(row.cls, catalog.CLASSES)
                self.assertIn(row.pillar, catalog.router().PILLARS)
                self.assertTrue(name.startswith(row.pillar + "_"))
                catalog.resolve(row)

    def test_the_long_running_verbs_are_not_catalogued(self):
        paths = {(row.pillar, row.path) for row in catalog.CATALOG.values()}
        for verb in (("specs", ("serve",)), ("portal", ("serve",)), ("specs", ("mcp",)),
                     ("codex", ("implement",))):
            self.assertNotIn(verb, paths)

    def test_the_external_class_names_the_moves_that_leave_the_machine(self):
        external = {n for n, r in catalog.CATALOG.items() if r.cls == "external"}
        self.assertTrue({"git_push", "git_pr_create", "git_pr_merge", "git_pr_record",
                         "codex_review"} <= external)
        self.assertTrue(catalog.annotations(catalog.CATALOG["git_pr_merge"])["destructiveHint"])


class Schema(unittest.TestCase):
    def test_the_schema_is_the_parser_read_back(self):
        verb = catalog.resolve(catalog.CATALOG["components_read"])
        shape = catalog.schema(verb)
        self.assertFalse(shape["additionalProperties"])
        self.assertEqual(shape["required"], ["path"])
        props = shape["properties"]
        self.assertEqual(props["rules_only"]["type"], "boolean")
        self.assertEqual(props["sections"]["type"], "array")
        self.assertNotIn("root", props)
        self.assertNotIn("json", props)

    def test_choices_become_an_enum_and_int_an_integer(self):
        props = catalog.schema(catalog.resolve(catalog.CATALOG["git_history_log"]))["properties"]
        self.assertEqual(props["max_count"]["type"], "integer")
        self.assertNotIn("kind", props)  # filled by the verb path
        self.assertEqual(props["revs"]["type"], "array")

    def test_a_flag_added_to_the_parser_reaches_the_tool_unedited(self):
        verb = catalog.resolve(catalog.CATALOG["git_base"])
        verb.parser.add_argument("--fresh-flag", choices=["a", "b"], help="new")
        props = catalog.schema(verb)["properties"]
        self.assertEqual(props["fresh_flag"], {"type": "string", "enum": ["a", "b"],
                                               "description": "new"})

    def test_every_option_of_every_tool_is_typed(self):
        for name, row in catalog.CATALOG.items():
            for prop in catalog.schema(catalog.resolve(row))["properties"].values():
                self.assertIn(prop["type"], ("boolean", "string", "integer", "number", "array"),
                              name)


class Argv(unittest.TestCase):
    def test_options_go_as_flag_equals_value_and_the_server_adds_root_and_json(self):
        cmd, as_json = catalog.argv(catalog.CATALOG["components_read"],
                                    {"path": "x.md", "sections": ["A", "B"], "rules_only": True},
                                    "/repo")
        self.assertTrue(as_json)
        self.assertEqual(cmd, ["--root", "/repo", "components", "read", "--sections=A",
                               "--sections=B", "--rules-only", "--json", "x.md"])

    def test_a_pillar_without_router_root_gets_the_verbs_own_root(self):
        cmd, _ = catalog.argv(catalog.CATALOG["git_base"], {}, "/repo")
        self.assertEqual(cmd, ["git", "base", "--root=/repo", "--json"])

    def test_the_verb_path_fills_a_positional_with_choices(self):
        cmd, _ = catalog.argv(catalog.CATALOG["git_worktree_add"], {"branch": "b"}, "/r")
        self.assertEqual(cmd[:3], ["git", "worktree", "add"])

    def test_an_argument_outside_the_schema_is_refused(self):
        for args in ({"nope": 1}, {"root": "/elsewhere"}, {"json": False}):
            with self.assertRaises(server.ToolArgs):
                catalog.argv(catalog.CATALOG["git_base"], args, "/r")

    def test_a_wrong_type_or_a_dash_positional_is_refused(self):
        with self.assertRaises(server.ToolArgs):
            catalog.argv(catalog.CATALOG["git_pr_view"], {"number": "1"}, "/r")
        with self.assertRaises(server.ToolArgs):
            catalog.argv(catalog.CATALOG["git_specs"], {"branch": "--add=x"}, "/r")
        with self.assertRaises(server.ToolArgs):
            catalog.argv(catalog.CATALOG["git_specs"], {}, "/r")


class Surface(unittest.TestCase):
    def test_initialize_names_the_quenching_server(self):
        reply = server.handle(rpc(1, "initialize", {"protocolVersion": "2025-06-18"}), "/x",
                              None, catalog.surface())
        self.assertEqual(reply["result"]["serverInfo"]["name"], "quenching")

    def test_tools_list_carries_the_catalog_and_the_specs_tools(self):
        tools = server.handle(rpc(2, "tools/list"), "/x", None,
                              catalog.surface())["result"]["tools"]
        by_name = {t["name"]: t for t in tools}
        self.assertTrue(set(catalog.CATALOG) <= set(by_name))
        self.assertIn("specs_status", by_name)
        for name, row in catalog.CATALOG.items():
            self.assertEqual(by_name[name]["annotations"], catalog.annotations(row), name)
            self.assertEqual(by_name[name]["inputSchema"]["type"], "object")
        self.assertTrue(by_name["git_base"]["annotations"]["readOnlyHint"])
        self.assertTrue(by_name["git_push"]["annotations"]["openWorldHint"])

    def test_an_absent_pillar_publishes_no_tool(self):
        surface = catalog.surface(present=lambda pillar: pillar not in ("ops", "specs"))
        names = {t["name"] for t in surface.list_tools()}
        self.assertFalse({n for n in names if n.startswith(("ops_", "specs_"))})
        self.assertIn("proof_doctor", names)
        self.assertFalse(surface.has_tool("ops_doctor"))


class Calls(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = git_repo(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def call(self, name, args):
        reply = server.handle(rpc(9, "tools/call", {"name": name, "arguments": args}),
                              self.root, None, catalog.surface())
        return reply["result"]

    def test_a_read_tool_returns_the_verbs_json(self):
        result = self.call("git_base", {})
        payload = json.loads(result["content"][0]["text"])
        self.assertFalse(result["isError"])
        self.assertEqual(payload["base"], "main")

    def test_a_write_tool_runs_the_verb_and_returns_its_json(self):
        result = self.call("git_specs", {"branch": "main", "add": "7"})
        self.assertFalse(result["isError"], result)
        self.assertTrue(json.loads(result["content"][0]["text"])["ok"])
        described = subprocess.run(["git", "-C", self.root, "config", "branch.main.description"],
                                   capture_output=True, text=True).stdout
        self.assertIn("quenching-specs: 7", described)

    def test_a_bad_argument_is_a_tool_error_and_the_cwd_stays(self):
        held = os.getcwd()
        result = self.call("git_base", {"nope": True})
        self.assertTrue(result["isError"])
        self.assertEqual(json.loads(result["content"][0]["text"])["code"], "mcp-bad-arguments")
        self.assertEqual(os.getcwd(), held)


class Hostile(unittest.TestCase):
    """Every catalogued tool, fed arguments it does not admit: a tool error each time, the cwd
    where it was, and a server that still answers afterwards."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = git_repo(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.surface = catalog.surface()

    def bad_calls(self):
        for name, row in catalog.CATALOG.items():
            yield name, {"not_an_argument": True}
            for prop in catalog.schema(catalog.resolve(row))["properties"]:
                yield name, {prop: {"an": "object"}}

    def test_every_tool_refuses_every_ill_typed_argument_and_the_loop_survives(self):
        held = os.getcwd()
        calls = list(self.bad_calls())
        lines = [json.dumps(rpc(i, "tools/call", {"name": name, "arguments": args}))
                 for i, (name, args) in enumerate(calls)] + [json.dumps(rpc("last", "ping"))]
        out = io.StringIO()
        self.assertEqual(server.serve(self.root, self.surface,
                                      io.StringIO("\n".join(lines) + "\n"), out), 0)
        replies = [json.loads(line) for line in out.getvalue().splitlines()]
        self.assertEqual(len(replies), len(calls) + 1)
        for (name, args), reply in zip(calls, replies):
            with self.subTest(name=name, args=args):
                self.assertTrue(reply["result"]["isError"])
                payload = json.loads(reply["result"]["content"][0]["text"])
                self.assertEqual(payload["code"], "mcp-bad-arguments")
        self.assertEqual(replies[-1], {"jsonrpc": "2.0", "id": "last", "result": {}})
        self.assertEqual(os.getcwd(), held)

    def test_a_missing_required_argument_is_refused_for_every_tool_that_has_one(self):
        for name, row in catalog.CATALOG.items():
            if catalog.schema(catalog.resolve(row)).get("required"):
                payload, failed = catalog.call(name, {}, self.root)
                self.assertTrue(failed, name)
                self.assertEqual(payload["code"], "mcp-bad-arguments", name)

    def test_a_verb_that_exits_or_crashes_after_moving_the_cwd_is_contained(self):
        held = os.getcwd()
        router = catalog.router()
        real = router.main

        def exits(argv):
            os.chdir(tempfile.gettempdir())
            raise SystemExit(3)

        def crashes(argv):
            os.chdir(tempfile.gettempdir())
            raise RuntimeError("boom")

        try:
            for fake, code in ((exits, "mcp-core-failure"), (crashes, "mcp-core-failure")):
                router.main = fake
                payload, failed = catalog.call("git_base", {}, self.root)
                self.assertTrue(failed)
                self.assertEqual(payload["code"], code)
                self.assertEqual(os.getcwd(), held)
        finally:
            router.main = real
        payload, failed = catalog.call("git_base", {}, self.root)
        self.assertFalse(failed)

    def test_a_root_that_does_not_exist_is_a_tool_error(self):
        payload, failed = catalog.call("git_history_log", {"revs": ["HEAD"], "max_count": 1},
                                       os.path.join(self.root, "missing"))
        self.assertTrue(failed)
        self.assertEqual(payload["code"], "mcp-core-failure")


if __name__ == "__main__":
    unittest.main()
