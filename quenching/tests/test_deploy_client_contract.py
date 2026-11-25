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
        commands = [hook["command"] for groups in hooks.values() for group in groups
                    for hook in group["hooks"] if hook.get("type") == "command"]
        ours = [command for command in commands if MARKER in command]
        self.assertEqual(1, len(ours), ours)
        code, _, bodies = ours[0].partition(' -I -c "')[2].partition('"')
        self.assertIsNone(EXPANSIVE.search(code), code)
        self.assertEqual(list(BODIES), bodies.split())

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


if __name__ == "__main__":
    unittest.main()
