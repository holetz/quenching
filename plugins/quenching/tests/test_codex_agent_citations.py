"""The Codex validator refuses a skill that cites an agent the Codex tree does not carry."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import _paths  # noqa: F401

REPO_ROOT = Path(__file__).resolve().parents[3]

SCRIPT = REPO_ROOT / "scripts" / "validate_codex_plugin.py"
CODEX = REPO_ROOT / "plugins" / "quenching-codex"


def load():
    spec = importlib.util.spec_from_file_location("validate_codex_plugin", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AgentCitationTest(unittest.TestCase):
    def setUp(self):
        self.module = load()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "skills" / "demo").mkdir(parents=True)

    def skill(self, body: str) -> None:
        (self.root / "skills" / "demo" / "SKILL.md").write_text(body, encoding="utf-8")

    def test_dangling_path_is_refused(self):
        self.skill("Read `../../agents/orchestrator.md`.\n")
        with self.assertRaises(self.module.ValidationError):
            self.module.validate_agent_citations(self.root)

    def test_dangling_name_is_refused(self):
        self.skill("Start the `quenching:scout` agent.\n")
        with self.assertRaises(self.module.ValidationError):
            self.module.validate_agent_citations(self.root)

    def test_resolved_citation_passes(self):
        (self.root / "agents").mkdir()
        (self.root / "agents" / "scout.md").write_text("x", encoding="utf-8")
        self.skill("Run `quenching:scout` per `../../agents/scout.md`.\n")
        self.module.validate_agent_citations(self.root)

    def test_shipped_tree_has_no_dangling_citation(self):
        self.module.validate_agent_citations(CODEX)


if __name__ == "__main__":
    unittest.main()
