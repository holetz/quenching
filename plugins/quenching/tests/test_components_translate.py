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


DESCRIPTION_BASELINES = {
    "plugins/quenching/commands/align.md": 772,
    "plugins/quenching/commands/components/align.md": 719,
    "plugins/quenching/commands/specs/conclude.md": 844,
    "plugins/quenching/commands/specs/triage.md": 795,
    "plugins/quenching/commands/specs/execute.md": 686,
    "plugins/quenching/commands/knowledge/align.md": 646,
    "plugins/quenching/commands/knowledge/documentation/write.md": 563,
    "plugins/quenching/commands/components/agent/new.md": 556,
    "plugins/quenching/commands/design/align.md": 555,
    "plugins/quenching/commands/components/hook/new.md": 555,
    "plugins/quenching/commands/knowledge/documentation/produce.md": 541,
    "plugins/quenching/commands/knowledge/documentation/build.md": 522,
    "plugins/quenching/commands/knowledge/documentation/review.md": 517,
    "plugins/quenching/commands/proof/layer/new.md": 495,
    "plugins/quenching/commands/knowledge/documentation/plan.md": 493,
    "plugins/quenching/commands/design/genre/new.md": 490,
    "plugins/quenching/commands/proof/align.md": 484,
}


TRIGGER_PHRASES = {
    "plugins/quenching/commands/align.md": ("align the repo", "align everything", "align and update everything", "set up quenching here", "converge this repository", "run all the aligns", "fix both fronts", "fix all fronts"),
    "plugins/quenching/commands/components/align.md": ("align the skills", "align and update the skills", "migrate my commands", "fix the .claude surface", "collapse the skill wrappers", "audit the command bodies", "review the skill descriptions", "shorten the descriptions", "converge the automation surface"),
    "plugins/quenching/commands/specs/conclude.md": ("conclude this spec", "close it out", "wrap up the plan", "review the branch", "archive this spec", "abandon this spec", "it will not be built"),
    "plugins/quenching/commands/specs/triage.md": ("triage the specs", "prioritize the front", "rank the plans", "what matters most", "re-rank these", "order the plans", "which of these first"),
    "plugins/quenching/commands/specs/execute.md": ("execute this spec", "build it", "implement the tasks", "apply the plan", "start working on it", "continue building", "run the next task", "work through the tasks"),
    "plugins/quenching/commands/knowledge/align.md": ("align the docs", "align and update docs", "fix the documentation structure", "install the OKF bundle", "set up /docs/", "converge the knowledge base"),
    "plugins/quenching/commands/knowledge/documentation/write.md": ("write the documentation pages", "draft the docs from the plan", "apply the documentation writing pass"),
    "plugins/quenching/commands/components/agent/new.md": ("create an agent", "add a subagent", "make a verifier agent", "delegate this to an agent", "set up something that audits our migrations and reports back"),
    "plugins/quenching/commands/design/align.md": ("align the design", "set up the design front", "install the brand pack", "rebuild the design projections", "fix design drift"),
    "plugins/quenching/commands/components/hook/new.md": ("create a hook", "add a validation hook", "check this after every edit", "block that command before it runs", "catch it automatically whenever a migration lands"),
    "plugins/quenching/commands/knowledge/documentation/produce.md": ("produce the documentation", "run the documentation pipeline", "generate the complete docs site"),
    "plugins/quenching/commands/knowledge/documentation/build.md": ("build the docs site", "generate the site for /docs", "fix the documentation site's nav"),
    "plugins/quenching/commands/knowledge/documentation/review.md": ("review the documentation", "score the docs pages", "critique the documentation quality"),
    "plugins/quenching/commands/proof/layer/new.md": ("create a proof layer", "add a test layer", "define a verification layer", "organize tests into a layer"),
    "plugins/quenching/commands/knowledge/documentation/plan.md": ("plan the documentation", "diagnose the docs structure", "design the documentation architecture"),
    "plugins/quenching/commands/design/genre/new.md": ("create a design genre", "add a report genre", "define a deck contract", "mint an editorial format", "make one genre render to HTML and PDF"),
    "plugins/quenching/commands/proof/align.md": ("align the proof front", "set up the verification surface", "fix proof drift", "converge the test gate"),
}


TYPED_ONLY_COMMANDS = (
    "plugins/quenching/commands/components/command/retro.md",
)


def source_description(path):
    line = next(line for line in path.read_text(encoding="utf-8").splitlines()
                if line.startswith("description: "))
    return line.removeprefix("description: ")


def generated_description(text):
    line = next(line for line in text.splitlines() if line.startswith("description: "))
    return json.loads(line.removeprefix("description: "))


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

    def test_package_description_review_reduces_routed_surface_and_preserves_slots(self):
        source = translate.REPOSITORY
        translate.configure(str(source / "plugins" / "quenching"),
                            str(self.root / "quenching-codex"))
        tree = translate.generated_tree()
        adaptation = translate.read_adaptation()
        after = 0

        for relative, baseline in DESCRIPTION_BASELINES.items():
            command = source / relative
            description = source_description(command)
            after += len(description)
            self.assertLess(len(description), baseline, relative)
            self.assertTrue("Triggers on " in description or "Use when " in description, relative)
            self.assertIn("Not for:", description, relative)

            command_path = command.relative_to(source / "plugins" / "quenching" / "commands")
            skill_key = "skills/quenching-" + "-".join(command_path.with_suffix("").parts) + "/SKILL.md"
            projected = generated_description(tree[skill_key].decode("utf-8"))
            self.assertEqual(projected,
                             translate.transform_platform(description, adaptation),
                             relative)
            self.assertIn("Not for:", projected, skill_key)
            for phrase in TRIGGER_PHRASES[relative]:
                self.assertIn(f'"{phrase}"', description, relative)
                translated_phrase = translate.transform_platform(f'"{phrase}"', adaptation)
                self.assertIn(translated_phrase, projected, skill_key)

        self.assertLess(after, sum(DESCRIPTION_BASELINES.values()))
        for relative in TYPED_ONLY_COMMANDS:
            text = (source / relative).read_text(encoding="utf-8")
            self.assertIn("disable-model-invocation: true", text, relative)
