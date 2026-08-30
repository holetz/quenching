"""Repository-surface translation keeps Claude configuration authoritative."""
import argparse
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import _paths  # noqa: F401 — must precede the quenching import
from quenching.components.commands import translate


COMMAND = """---
description: Translate this repository surface. Not for: editing the generated Codex skill.
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
        (claude / "references" / "specs").mkdir(parents=True)
        (claude / "references" / "specs" / "guide.md").write_text(
            "Read .claude/commands/specs/status.md with Claude.\n", encoding="utf-8")
        (claude / "quenching.json").write_text('{"backend": "github"}\n', encoding="utf-8")
        (self.root / "CLAUDE.md").write_text("# Claude harness\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_writes_codex_skills_and_harness_without_copying_configuration(self):
        translate.configure(str(self.root), str(self.root))
        translate.write_tree(translate.generated_tree())

        skill = self.root / ".agents" / "skills" / "specs" / "status" / "SKILL.md"
        self.assertTrue(skill.is_file())
        skill_text = skill.read_text(encoding="utf-8")
        self.assertIn("name: quenching-specs-status", skill_text)
        self.assertNotIn("allowed-tools:", skill_text)
        self.assertIn("Not for:", skill_text)
        self.assertEqual((self.root / ".agents" / "references" / "specs" / "guide.md")
                         .read_text(encoding="utf-8"),
                         "Read .agents/skills/specs/status.md with Codex.\n")
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

    def test_preserves_codex_marketplace_configuration(self):
        marketplace = self.root / ".agents" / "plugins" / "marketplace.json"
        marketplace.parent.mkdir(parents=True)
        marketplace.write_text('{"plugins": []}\n', encoding="utf-8")
        translate.configure(str(self.root), str(self.root))
        translate.write_tree(translate.generated_tree())
        self.assertTrue(marketplace.is_file())
        self.assertEqual(translate.differences(translate.generated_tree()), [])

    def test_reconciliation_classifies_source_and_codex_body_changes(self):
        translate.configure(str(self.root), str(self.root))
        translate.write_tree(translate.generated_tree())
        command = self.root / ".claude" / "commands" / "specs" / "status.md"
        command.write_text(COMMAND + "\nSource edit.\n", encoding="utf-8")
        tree = translate.generated_tree()
        self.assertEqual(translate.reconciliation(translate.differences(tree), translate.source_digest()),
                         "source-changed")
        translate.write_tree(tree)
        skill = self.root / ".agents" / "skills" / "specs" / "status" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\nCodex body edit.\n", encoding="utf-8")
        tree = translate.generated_tree()
        self.assertEqual(translate.reconciliation(translate.differences(tree), translate.source_digest()),
                         "target-changed")

    def test_reverse_write_propagates_body_and_refuses_frontmatter(self):
        translate.configure(str(self.root), str(self.root))
        translate.write_tree(translate.generated_tree())
        skill = self.root / ".agents" / "skills" / "specs" / "status" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\nCodex body edit.\n", encoding="utf-8")
        args = argparse.Namespace(source=str(self.root), target=str(self.root), check=False, write=True,
                                  diff=False, json=True)
        self.assertEqual(translate.cmd_translate(args, str(self.root)), 0)
        self.assertIn("Claude body edit.", (self.root / ".claude" / "commands" / "specs" / "status.md")
                      .read_text(encoding="utf-8"))
        skill.write_text(skill.read_text(encoding="utf-8").replace("name: quenching-specs-status",
                                                                     "name: changed"), encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(translate.cmd_translate(args, str(self.root)), 2)
        self.assertIn("Claude side is authoritative", output.getvalue())

    def test_package_translation_keeps_both_harness_names_exempt(self):
        source = translate.REPOSITORY / "plugins" / "quenching"
        translate.configure(str(source), str(self.root / "quenching-codex"))
        schema = translate.generated_tree()[
            "scripts/bin/quenching/knowledge/schema.py"
        ].decode("utf-8")

        self.assertIn('CLAUDE_HARNESS = "CLAUDE" + ".md"', schema)
        self.assertIn('EXEMPT = (CLAUDE_HARNESS, "AGENTS.md")', schema)

    def test_package_translation_adjusts_codex_check_root(self):
        source = translate.REPOSITORY / "plugins" / "quenching"
        translate.configure(str(source), str(self.root / "quenching-codex"))
        citation = translate.generated_tree()["checks/citation-check.sh"].decode("utf-8")
        functional = translate.generated_tree()["checks/functional-checks.sh"].decode("utf-8")
        self.assertIn('SELF_DIR/../../../"', citation)
        self.assertNotIn('SELF_DIR/../../../.."', citation)
        self.assertIn('dirname "${BASH_SOURCE[0]}")/../../../"', functional)
        self.assertNotIn('dirname "${BASH_SOURCE[0]}")/../../../.."', functional)
