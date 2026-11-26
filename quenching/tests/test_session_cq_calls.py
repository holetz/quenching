"""`session digest` tells a `cq` call that fell to the shell from one served by the MCP server.

The count is the parser's, never a model recalling its own run: a `Bash` that runs `cq <verb>`,
`mcp__quenching__<tool>` / `quenching_<tool>` calls and `tools.quenching.<tool>(` inside a Code
Mode `execute` are read from the transcript lines and nowhere else.
"""
import contextlib
import io
import json
import pathlib
import tempfile
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.session import cqcalls
from quenching.session.commands.cli import build_parser
from quenching.session.evidence import digest_command
from quenching.session.parse import read_lines


def use(name, uuid, skill="demo:run", **inp):
    return {"type": "assistant", "uuid": uuid, "attributionSkill": skill,
            "message": {"content": [{"type": "tool_use", "name": name, "input": inp}]}}


def bash(uuid, command, skill="demo:run"):
    return use("Bash", uuid, skill, command=command)


ENTRY = {"type": "user", "uuid": "u0",
         "message": {"content": "<command-name>/demo:run</command-name>"}}


def lines(*records):
    return [json.dumps(r) for r in (ENTRY, *records)]


class ShellVerbs(unittest.TestCase):
    def test_a_cq_call_is_reduced_to_its_verb_path(self):
        self.assertEqual(cqcalls.shell_verbs(".agents/quenching/bin/cq specs status --spec 1 --json"),
                         [("specs", "status")])
        self.assertEqual(cqcalls.shell_verbs("cd /w && .agents/quenching/bin/cq git worktree acquire --branch b"),
                         [("git", "worktree", "acquire")])
        self.assertEqual(cqcalls.shell_verbs("cq --root /w proof doctor"), [("proof", "doctor")])

    def test_prose_and_non_verbs_count_nothing(self):
        self.assertEqual(cqcalls.shell_verbs("echo hello && ls"), [])
        self.assertEqual(cqcalls.shell_verbs("grep -rn cq specs"), [])

    def test_two_calls_in_one_command_are_two(self):
        self.assertEqual(cqcalls.shell_verbs("cq specs status --spec 1; cq specs validate --spec 1"),
                         [("specs", "status"), ("specs", "validate")])


class McpTools(unittest.TestCase):
    def test_the_three_forms(self):
        self.assertEqual(cqcalls.mcp_tools("mcp__quenching__specs_status", {}), ["specs_status"])
        self.assertEqual(cqcalls.mcp_tools("quenching_git_state", {}), ["git_state"])
        code = "const a = await tools.quenching.specs_status({id: 1}); await tools.quenching['git_state']({})"
        self.assertEqual(cqcalls.mcp_tools("mcp__opencode__execute", {"code": code}),
                         ["specs_status", "git_state"])

    def test_a_grouped_tool_counts_under_the_verb_it_names(self):
        self.assertEqual(cqcalls.mcp_tools("mcp__quenching__specs_read", {"verb": "status"}),
                         ["specs_status"])
        self.assertEqual(cqcalls.mcp_tools("quenching_git_write", {"verb": "commit"}),
                         ["git_commit"])
        self.assertEqual(cqcalls.mcp_tools("mcp__quenching__components_read", {"verb": "read"}),
                         ["components_read"])
        code = ("await tools.quenching.specs_read({ verb: 'status', spec: 1 });"
                " await tools.quenching['git_read']({\"verb\": \"state\"})")
        self.assertEqual(cqcalls.mcp_tools("mcp__opencode__execute", {"code": code}),
                         ["specs_status", "git_state"])

    def test_help_or_no_verb_keeps_the_published_name(self):
        self.assertEqual(cqcalls.mcp_tools("mcp__quenching__git_read", {"verb": "help"}),
                         ["git_read"])
        self.assertEqual(cqcalls.mcp_tools("mcp__quenching__git_read", {}), ["git_read"])

    def test_other_servers_count_nothing(self):
        self.assertEqual(cqcalls.mcp_tools("mcp__opencode__read", {}), [])
        self.assertEqual(cqcalls.mcp_tools("Bash", {"command": "cq specs status"}), [])


class Digest(unittest.TestCase):
    def model(self, *records):
        return read_lines(lines(*records), "fixture")

    def digest(self, model, name="demo:run"):
        cmd = next(c for c in model["_commands"] if c.name == name)
        return digest_command(cmd, [], 200, 20)

    def test_counts_split_shell_from_mcp_per_command_and_per_session(self):
        model = self.model(
            bash("a", "cq specs status --spec 1 --json"),
            bash("b", "cq specs status --spec 1 --json"),
            bash("c", "cq deploy --target . --write"),
            use("mcp__quenching__specs_status", "d"),
            use("mcp__quenching__git_state", "e"),
            use("mcp__opencode__read", "f", file_path="/x"),
            use("Bash", "g", skill=None, command="cq git state --json"))
        out = self.digest(model)
        self.assertEqual(out["counts"]["cqShell"], 3)
        self.assertEqual(out["counts"]["cqMcp"], 2)
        self.assertTrue(out["cq"]["connected"])
        self.assertEqual(out["cq"]["shell"], {"specs status": 2, "deploy": 1})
        self.assertEqual(out["cq"]["fellToShell"], {"specs status": 2})
        self.assertEqual(out["cq"]["cliByDesign"], {"deploy": 1})
        total = cqcalls.summarize(model["cq"]["shell"], model["cq"]["mcp"])
        self.assertEqual((total["shellCalls"], total["mcpCalls"]), (4, 2))
        self.assertEqual(total["fellToShell"], {"specs status": 2, "git state": 1})
        self.assertAlmostEqual(total["shellRatio"], 4 / 6, places=3)

    def test_without_an_mcp_call_nothing_is_said_to_have_fallen(self):
        model = self.model(bash("a", "cq specs status --spec 1"))
        out = self.digest(model)
        self.assertFalse(out["cq"]["connected"])
        self.assertEqual(out["cq"]["fellToShell"], {})
        self.assertEqual(out["counts"]["cqShell"], 1)

    def test_a_session_with_no_cq_call_has_no_ratio(self):
        out = self.digest(self.model(use("Read", "a", file_path="/x")))
        self.assertIsNone(out["cq"]["shellRatio"])


class OpenCode(unittest.TestCase):
    def test_code_mode_keeps_only_the_tool_names_never_the_code(self):
        from quenching.session.opencode_transcript import _tool_use
        code = "const secret = 'KEEP-OUT'; await tools.quenching.specs_status({id: 1});"
        block = {"type": "tool", "name": "mcp__opencode__execute", "state": {"input": {"code": code}}}
        use_, _ = _tool_use(block)
        self.assertEqual(cqcalls.mcp_tools(use_["name"], use_["input"]), ["specs_status"])
        self.assertNotIn("KEEP-OUT", json.dumps(use_))

    def test_a_bridged_grouped_tool_keeps_only_its_verb(self):
        from quenching.session.opencode_transcript import _tool_use
        use_, _ = _tool_use({"type": "tool", "name": "quenching_specs_read",
                             "state": {"input": {"verb": "status", "spec": 1, "body": "KEEP-OUT"}}})
        self.assertEqual({"verb": "status"}, use_["input"])
        self.assertEqual(cqcalls.mcp_tools(use_["name"], use_["input"]), ["specs_status"])

    def test_a_bridged_server_tool_keeps_its_name(self):
        from quenching.session.opencode_transcript import _tool_use
        use_, _ = _tool_use({"type": "tool", "name": "quenching_specs_status", "state": {"input": {}}})
        self.assertEqual(cqcalls.mcp_tools(use_["name"], use_["input"]), ["specs_status"])


class Cli(unittest.TestCase):
    def test_json_digest_carries_the_session_total(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "s.jsonl"
            path.write_text("\n".join(lines(
                bash("a", "cq specs status --spec 1"),
                use("mcp__quenching__specs_status", "b"))), encoding="utf-8")
            args = build_parser().parse_args(["digest", str(path), "--json"])
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                args.func(args)
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["cq"]["shellCalls"], 1)
        self.assertEqual(payload["cq"]["mcpCalls"], 1)
        self.assertEqual(payload["cq"]["fellToShell"], {"specs status": 1})


if __name__ == "__main__":
    unittest.main()
