"""Repository-surface translation keeps Claude configuration authoritative."""
import json
import tempfile
import unittest
from pathlib import Path

import _paths  # noqa: F401 — must precede the quenching import
from quenching.components.commands import translate


COMMAND = """---
description: Translate this repository surface.
allowed-tools: Read
---

Use `.claude/quenching.json` and CLAUDE.md.
"""


class RepositorySurfaceTranslation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        claude = self.root / ".claude"
        (claude / "commands" / "specs").mkdir(parents=True)
        (claude / "commands" / "specs" / "status.md").write_text(COMMAND, encoding="utf-8")
        (claude / "quenching.json").write_text('{"backend": "github"}\n', encoding="utf-8")
        (self.root / "CLAUDE.md").write_text("# Claude harness\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_writes_codex_skills_and_harness_without_copying_configuration(self):
        translate.configure(str(self.root), str(self.root))
        translate.write_tree(translate.generated_tree())

        skill = self.root / ".agents" / "skills" / "specs" / "status" / "SKILL.md"
        self.assertTrue(skill.is_file())
        self.assertIn("name: quenching-specs-status", skill.read_text(encoding="utf-8"))
        self.assertNotIn("allowed-tools:", skill.read_text(encoding="utf-8"))
        self.assertEqual((self.root / ".agents" / "AGENTS.md").read_text(encoding="utf-8"), "# Codex harness\n")
        self.assertEqual(json.loads((self.root / ".claude" / "quenching.json").read_text(encoding="utf-8")),
                         {"backend": "github"})
        self.assertFalse((self.root / ".agents" / "quenching.json").exists())

    def test_coexisting_surfaces_are_clean_after_generation(self):
        translate.configure(str(self.root), str(self.root))
        translate.write_tree(translate.generated_tree())
        self.assertEqual(translate.differences(translate.generated_tree()), [])
        self.assertTrue((self.root / ".claude" / "commands" / "specs" / "status.md").is_file())
        self.assertTrue((self.root / ".agents" / "skills" / "specs" / "status" / "SKILL.md").is_file())

