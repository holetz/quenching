"""The Copilot projection of every shipped agent against the tools its own body cites: a tool the
body calls and the projection drops leaves the agent discovered and unable to act (spec 488)."""

import pathlib
import re
import sys
import unittest

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = PLUGIN_ROOT.parent
sys.path.insert(0, str(PLUGIN_ROOT / "assets" / "bin"))

try:
    import _paths  # noqa: F401
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401

from quenching.deploy import translate  # noqa: E402
from quenching.mcp import catalog  # noqa: E402

AGENTS = sorted((PLUGIN_ROOT / "agents").glob("*.md"))
MOUNTS = (None, frozenset({"specs", "git", "components"}))
DEGRADATION = "**Without the `quenching` MCP tools in this session**"


def cited(body: str, mount: frozenset[str] | None) -> set[str]:
    """Every published tool name the body names, inside the pillars the mount publishes."""
    names = set(catalog.tool_names())
    return {word for word in re.findall(r"\b[a-z]+_[a-z0-9_]+\b", body)
            if word in names and (mount is None or catalog.pillar_of(word) in mount)}


def projected(tools: list[str]) -> set[str]:
    return {name.split("/", 1)[1] for name in tools if name.startswith(f"{translate.MCP_SERVER}/")}


class CopilotAgentTools(unittest.TestCase):

    def test_there_are_agents_to_prove(self):
        self.assertEqual(sorted(translate.AGENTS), [path.stem for path in AGENTS])

    def test_every_tool_the_body_cites_is_in_the_projection(self):
        for path in AGENTS:
            fields, body = translate.split_frontmatter(path.read_text(encoding="utf-8"))
            for mount in MOUNTS:
                for narrow in (False, True):
                    with self.subTest(agent=path.stem, mount=mount, narrow=narrow):
                        tools = translate.copilot_tools(fields.get("tools", ""), narrow, mount)
                        if f"{translate.MCP_SERVER}/*" in tools:
                            continue
                        self.assertEqual(set(), cited(body, mount) - projected(tools))

    def test_shell_and_delegation_grants_keep_their_client_tool(self):
        for path in AGENTS:
            fields, _ = translate.split_frontmatter(path.read_text(encoding="utf-8"))
            heads = {name.split("(", 1)[0] for name in translate._grant_names(fields.get("tools", ""))}
            tools = translate.copilot_tools(fields.get("tools", ""))
            with self.subTest(agent=path.stem):
                if "Bash" in heads:
                    self.assertIn("execute", tools)
                if heads & {"Agent", "Task"}:
                    self.assertIn("agent", tools)

    def test_every_published_agent_carries_the_degradation_rule(self):
        for path in AGENTS:
            text = translate.copilot_agent_document(path.read_text(encoding="utf-8"), path.stem)
            with self.subTest(agent=path.stem):
                self.assertIn(DEGRADATION, text)

    def test_the_deployed_projection_names_what_the_source_body_cites(self):
        deployed = REPO / ".github" / "agents"
        if not deployed.is_dir():
            self.skipTest("this checkout declares no github projection")
        for path in AGENTS:
            target = deployed / f"{translate.agent_name(path.stem)}.agent.md"
            line = next(line for line in target.read_text(encoding="utf-8").splitlines()
                        if line.startswith("tools:"))
            tools = [item.strip() for item in line[len("tools:"):].strip(" []").split(",")]
            _, body = translate.split_frontmatter(path.read_text(encoding="utf-8"))
            with self.subTest(agent=path.stem):
                self.assertIn(DEGRADATION, target.read_text(encoding="utf-8"))
                if f"{translate.MCP_SERVER}/*" not in tools:
                    self.assertEqual(set(), cited(body, MOUNTS[1]) - projected(tools))


if __name__ == "__main__":
    unittest.main()
