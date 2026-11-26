"""`shared.mcp.mount` as the deploy writes it: the three forms the registry reads, the named `core`
expanded into the pillars it publishes, and the grants that never name a tool the mount hides."""

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

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "assets" / "bin"))

try:
    import _paths  # noqa: F401
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401

from quenching.deploy import translate  # noqa: E402
from quenching.mcp import catalog  # noqa: E402

PY = ["/opt/py/bin/python3"]
# The pillars `core` publishes; the table below carries them, and the last test binds the two.
CORE = ["specs", "git", "components"]


class Mounts(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.target = pathlib.Path(tmp.name)
        subprocess.run(["git", "-C", str(self.target), "init", "-q"], check=True,
                       capture_output=True)
        xdg = pathlib.Path(tempfile.mkdtemp(dir=tmp.name, prefix="xdg-"))
        env = mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(xdg), "OPENCODE_CONFIG": ""})
        env.start()
        self.addCleanup(env.stop)
        precompile = mock.patch("quenching.deploy.cli._precompile", return_value=None)
        precompile.start()
        self.addCleanup(precompile.stop)

    def deploy(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = deploy_main(["--target", str(self.target), *argv, "--json"])
        return code, json.loads(out.getvalue() or "{}")

    def configure(self, mount):
        document = {"shared": {"mcp": {"command": PY, "mount": mount}}}
        path = self.target / ".agents/quenching.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    def args(self):
        servers = json.loads((self.target / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]
        return servers["quenching"]["args"]

    def test_the_default_mount_registers_the_whole_server(self):
        code, payload = self.deploy("--modules", "specs", "--write")
        self.assertEqual(0, code, payload)
        self.assertEqual(["mcp"], self.args()[-1:])
        self.assertEqual([], self.deploy("--check")[1]["changes"])

    def test_the_specs_mount_keeps_its_own_pillar_form(self):
        self.configure("specs")
        code, payload = self.deploy("--modules", "specs", "--write")
        self.assertEqual(0, code, payload)
        self.assertEqual(["specs", "mcp"], self.args()[-2:])
        self.assertEqual([], self.deploy("--check")[1]["changes"])

    def test_core_expands_into_the_pillars_it_publishes(self):
        self.configure("core")
        code, payload = self.deploy("--modules", "specs", "--write")
        self.assertEqual(0, code, payload)
        self.assertEqual(["mcp", "--only", ",".join(CORE)], self.args()[-3:])
        self.assertEqual(CORE, list(catalog.MOUNTS["core"]))
        self.assertEqual([], self.deploy("--check")[1]["changes"])

    def test_a_comma_list_of_pillars_is_the_argv_verbatim(self):
        self.configure("specs,git")
        code, payload = self.deploy("--modules", "specs", "--write")
        self.assertEqual(0, code, payload)
        self.assertEqual(["mcp", "--only", "specs,git"], self.args()[-3:])

    def test_a_mount_naming_no_routed_pillar_is_refused_before_anything_is_written(self):
        self.configure("nope")
        code, payload = self.deploy("--modules", "specs", "--write")
        self.assertEqual(2, code, payload)
        self.assertEqual("ct-deploy-mcp", payload["code"])
        self.assertIn("nope", payload["message"])
        self.assertFalse((self.target / ".mcp.json").exists())

    def test_the_agents_grant_no_tool_the_mount_does_not_publish(self):
        self.configure("core")
        self.assertEqual(0, self.deploy("--modules", "specs", "--harness", "claude",
                                        "--write")[0])
        agent = self.target / ".claude/agents/quenching-spec-runner.md"
        lines = [line for line in agent.read_text(encoding="utf-8").splitlines()
                 if line.startswith("tools:")]
        self.assertTrue(lines, agent)
        granted = {name.strip().split("__")[-1] for name in lines[0][len("tools:"):].split(",")
                   if "__" in name}
        self.assertTrue(granted)
        hidden = {tool for tool in catalog.tool_names()
                  if catalog.pillar_of(tool) not in CORE}
        self.assertEqual(set(), granted & hidden)

    def test_the_payload_agent_re_read_under_the_mount_publishes_the_same_agent(self):
        # The payload keeps its agents unmounted; a target-local deploy re-translates them under
        # the declared mount and must land on the bytes the source deploy wrote.
        source = (PLUGIN_ROOT / "agents" / "spec-runner.md").read_text(encoding="utf-8")
        mount = frozenset(catalog.mount_pillars("specs"))
        payload = translate.agent_document(source, "spec-runner")
        self.assertIn("mcp__quenching__git_write", payload)
        self.assertEqual(translate.agent_document(source, "spec-runner", mount=mount),
                         translate.agent_document(payload, "spec-runner", mount=mount))


class TheShellDoor(unittest.TestCase):
    """A pillar the mount hides keeps the shell grant its verbs would otherwise lose, so the
    narrowed deploy never closes both doors on the same verb."""

    KNOWLEDGE = "---\ndescription: k\ntools: Bash(cq knowledge:*)\n---\n\nbody\n"
    SPECS = "---\ndescription: s\ntools: Bash(cq specs status:*)\n---\n\nbody\n"

    def tools(self, text: str) -> str:
        return next(line for line in text.splitlines() if line.startswith("tools:"))

    def test_a_pillar_outside_the_mount_keeps_its_shell_door(self):
        text = translate.agent_document(self.KNOWLEDGE, "k", narrow=True,
                                        mount=frozenset(CORE))
        self.assertIn("Bash(.agents/quenching/bin/cq knowledge:*)", self.tools(text))
        self.assertNotIn("mcp__quenching__knowledge", text)

    def test_a_published_pillar_still_loses_the_shell_door(self):
        text = translate.agent_document(self.SPECS, "s", narrow=True, mount=frozenset(CORE))
        tools = self.tools(text)
        self.assertNotIn("Bash(", tools)
        self.assertIn("mcp__quenching__specs_read", tools)

    def test_the_copilot_projection_follows_the_same_mount(self):
        hidden = translate.copilot_tools("Bash(cq knowledge:*)", narrow=True,
                                           mount=frozenset(CORE))
        self.assertEqual(["execute"], hidden)
        shown = translate.copilot_tools("Bash(cq knowledge:*)", narrow=True)
        self.assertIn("execute", shown)
        self.assertTrue(any(name.startswith("quenching/knowledge_") for name in shown), shown)

    def test_the_whole_router_residue_is_also_filtered_by_the_mount(self):
        from quenching.mcp import coverage
        residue = coverage.cli_residue((), frozenset(CORE))
        verbs = {" ".join(path) for path in residue}
        self.assertIn("knowledge", verbs)
        self.assertNotIn("specs status", verbs)


from quenching.deploy.cli import main as deploy_main  # noqa: E402

if __name__ == "__main__":
    unittest.main()
