"""O piso agnóstico: os artefatos que qualquer cliente lê, e que nenhum membro do épico 453 pode
quebrar. Só afirma o que já é verdade — uma entrada por evento e matcher, uma ponte byte a byte,
uma recusa — e nada que dependa de um cliente em particular."""

import contextlib
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "assets" / "bin"))

try:
    import _paths  # noqa: F401
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401

from quenching.components.commands import bridge  # noqa: E402
from quenching.deploy.cli import main as deploy_main  # noqa: E402
from quenching.deploy.settings import MARKER  # noqa: E402

BODIES = ("deny-claude-coauthor", "warn-git-add-all")
SESSION_BODIES = ("adopt-worktree",)
# The characters bash, PowerShell and cmd each expand; the hook's `-c` code carries none of them.
EXPANSIVE = re.compile(r'[$`"]')


class ClientContract(unittest.TestCase):
    """One real deploy, read as a client reads it."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.target = pathlib.Path(cls.tmp.name)
        subprocess.run(["git", "-C", str(cls.target), "init", "-q"], check=True,
                       capture_output=True)
        xdg = pathlib.Path(tempfile.mkdtemp(dir=cls.tmp.name, prefix="xdg-"))
        env = mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(xdg), "OPENCODE_CONFIG": ""})
        env.start()
        cls.addClassCleanup(env.stop)
        precompile = mock.patch("quenching.deploy.cli._precompile", return_value=None)
        precompile.start()
        cls.addClassCleanup(precompile.stop)
        # A target's own skill, so the bridge has one file to prove: the deploy-generated
        # skills are the deploy's, and the bridge never expects or orphans them.
        own = cls.target / ".agents" / "skills" / "target-own" / "SKILL.md"
        own.parent.mkdir(parents=True)
        own.write_text("---\nname: target-own\ndescription: A target's own skill.\n---\n\nBody.\n",
                       encoding="utf-8")
        cls.code, cls.payload = cls.deploy("--modules", "all", "--write")

    @classmethod
    def deploy(cls, *argv) -> tuple[int, dict]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = deploy_main(["--target", str(cls.target), *argv, "--json"])
        return code, json.loads(out.getvalue() or "{}")

    def read(self, rel: str):
        return json.loads((self.target / rel).read_text(encoding="utf-8"))

    def test_one_quenching_entry_in_the_mcp_file(self):
        self.assertEqual(0, self.code, self.payload)
        servers = self.read(".mcp.json")["mcpServers"]
        self.assertIn("quenching", servers)
        self.assertEqual(["mcp"], servers["quenching"]["args"][-1:])
        self.assertTrue(servers["quenching"]["command"])

    def test_the_settings_file_approves_the_server_by_name(self):
        settings = self.read(".claude/settings.json")
        self.assertIn("quenching", settings["enabledMcpjsonServers"])
        self.assertNotIn("quenching", settings.get("disabledMcpjsonServers") or [])

    def test_one_hook_entry_per_event_and_matcher_runs_the_marker_without_an_expansive_character(self):
        hooks = self.read(".claude/settings.json")["hooks"]
        pairs = [(event, group.get("matcher", "")) for event, groups in hooks.items()
                 for group in groups]
        self.assertEqual(len(pairs), len(set(pairs)), pairs)
        expected = {"PreToolUse": BODIES, "SessionStart": SESSION_BODIES}
        self.assertEqual(sorted(expected), sorted(hooks))
        for event, bodies in expected.items():
            ours = [hook["command"] for group in hooks[event] for hook in group["hooks"]
                    if hook.get("type") == "command" and MARKER in hook["command"]]
            self.assertEqual(1, len(ours), ours)
            code, _, tail = ours[0].partition(' -I -c "')[2].partition('"')
            self.assertIsNone(EXPANSIVE.search(code), code)
            self.assertEqual(list(bodies), tail.split(), event)
        self.assertEqual("startup|resume|clear|compact",
                         hooks["SessionStart"][0].get("matcher"))
        self.assertEqual(300, hooks["SessionStart"][0]["hooks"][0]["timeout"])

    def test_the_bridge_owns_the_targets_skills_and_not_the_deploys(self):
        expected = bridge.expected_tree(self.target)
        self.assertEqual({"target-own/SKILL.md"}, set(expected))
        result = bridge.plan(self.target)
        self.assertEqual([], result["changes"])
        self.assertEqual([], result["conflicts"])

    def test_the_claude_skills_copy_is_byte_identical_to_the_source(self):
        expected = bridge.expected_tree(self.target)
        self.assertTrue(expected)
        for rel, data in expected.items():
            path = self.target / bridge.DESTINATION / rel
            self.assertTrue(path.is_file(), rel)
            self.assertEqual(data, bridge._canonical(path), rel)
        self.assertTrue((self.target / bridge.MANIFEST).is_file())

    def test_the_deploy_refuses_a_copilot_harness(self):
        code, payload = self.deploy("--harness", "copilot")
        self.assertEqual(2, code)
        self.assertEqual("ct-deploy-harness", payload["code"])

    def test_without_the_key_no_client_projection_is_written(self):
        self.assertFalse((self.target / ".github").exists())


class TheClientProjection(unittest.TestCase):
    """`shared.projections: ["github"]`: the Copilot subagents, from the same source, opt-in."""

    ALIASES = {"read", "search", "edit", "execute", "agent", "web", "todo"}

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        xdg = pathlib.Path(tempfile.mkdtemp(dir=str(self.tmp), prefix="xdg-"))
        env = mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(xdg), "OPENCODE_CONFIG": ""})
        env.start()
        self.addCleanup(env.stop)
        precompile = mock.patch("quenching.deploy.cli._precompile", return_value=None)
        precompile.start()
        self.addCleanup(precompile.stop)

    def deploy(self, projections, name="target"):
        target = self.tmp / name
        target.mkdir()
        subprocess.run(["git", "-C", str(target), "init", "-q"], check=True, capture_output=True)
        document = {} if projections is None else {"shared": {"projections": projections}}
        path = target / ".agents/quenching.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(document), encoding="utf-8")
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = deploy_main(["--target", str(target), "--modules", "all", "--write", "--json"])
        return code, json.loads(out.getvalue() or "{}"), target

    def frontmatter(self, path: pathlib.Path) -> dict[str, str]:
        body = path.read_text(encoding="utf-8").split("---", 2)[1]
        return {line.split(":", 1)[0]: line.split(":", 1)[1].strip()
                for line in body.splitlines() if ":" in line}

    def test_the_five_agents_carry_the_native_format(self):
        code, payload, target = self.deploy(["github"])
        self.assertEqual(0, code, payload)
        agents = sorted((target / ".github/agents").glob("quenching-*.agent.md"))
        self.assertEqual(5, len(agents), agents)
        self.assertFalse((target / ".github/instructions").exists())
        setup = target / ".github/workflows/copilot-setup-steps.yml"
        self.assertTrue(setup.is_file(), setup)
        self.assertIn("  copilot-setup-steps:\n", setup.read_text(encoding="utf-8"))
        for path in agents:
            fields = self.frontmatter(path)
            self.assertTrue(fields["description"])
            self.assertEqual("true", fields["include-custom-instructions"])
            self.assertEqual("github-copilot", fields["target"])
            self.assertIn("Claude ", fields["model"])
            self.assertNotIn("haiku", fields["model"].lower())
            tools = fields["tools"].strip("[]").split(", ")
            self.assertTrue(tools)
            for tool in tools:
                self.assertTrue(tool in self.ALIASES or tool.startswith("quenching/"), tool)
            for claude in ("Bash(", "Read", "Grep", "Glob", "Skill", "*"):
                self.assertNotIn(claude, fields["tools"])

    def test_an_unknown_projection_is_refused_and_writes_nothing(self):
        code, payload, target = self.deploy(["copilot"])
        self.assertEqual((2, "ct-deploy-projection"), (code, payload["code"]))
        self.assertFalse((target / ".agents/.quenching-deploy.json").exists())
        self.assertFalse((target / ".github").exists())

    def test_removing_the_key_removes_the_projection(self):
        code, payload, target = self.deploy(["github"])
        self.assertEqual(0, code, payload)
        (target / ".agents/quenching.json").write_text(json.dumps({}), encoding="utf-8")
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = deploy_main(["--target", str(target), "--modules", "all", "--write", "--json"])
        self.assertEqual(0, code, json.loads(out.getvalue() or "{}"))
        self.assertFalse((target / ".github/agents").exists())


if __name__ == "__main__":
    unittest.main()
