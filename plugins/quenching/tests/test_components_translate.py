"""Repository-surface translation keeps Claude configuration authoritative."""
import argparse
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import _paths  # noqa: F401 — must precede the quenching import
from quenching.common.frontmatter import parse_frontmatter
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
    "plugins/quenching/commands/align.md": ("align the repo", "align everything", "set up quenching here"),
    "plugins/quenching/commands/components/align.md": ("align the skills", "audit the command bodies", "shorten the descriptions"),
    "plugins/quenching/commands/specs/conclude.md": ("conclude this spec", "close it out", "abandon this spec"),
    "plugins/quenching/commands/specs/triage.md": ("triage the specs", "prioritize the front", "which of these first"),
    "plugins/quenching/commands/specs/execute.md": ("execute this spec", "build it", "implement the tasks", "continue building"),
    "plugins/quenching/commands/knowledge/align.md": ("align the docs", "set up /docs/", "converge the knowledge base"),
    "plugins/quenching/commands/knowledge/documentation/write.md": ("write the documentation pages", "draft the docs from the plan"),
    "plugins/quenching/commands/components/agent/new.md": ("create an agent", "add a subagent", "make a verifier agent"),
    "plugins/quenching/commands/design/align.md": ("align the design", "install the brand pack", "fix design drift"),
    "plugins/quenching/commands/components/hook/new.md": ("create a hook", "check this after every edit", "block that command"),
    "plugins/quenching/commands/knowledge/documentation/produce.md": ("produce the documentation", "generate the complete docs site"),
    "plugins/quenching/commands/knowledge/documentation/build.md": ("build the docs site", "fix the docs nav"),
    "plugins/quenching/commands/knowledge/documentation/review.md": ("review the documentation", "score the docs pages"),
    "plugins/quenching/commands/proof/layer/new.md": ("create a proof layer", "add a test layer"),
    "plugins/quenching/commands/knowledge/documentation/plan.md": ("plan the documentation", "design the documentation architecture"),
    "plugins/quenching/commands/design/genre/new.md": ("create a design genre", "define a deck contract"),
    "plugins/quenching/commands/proof/align.md": ("align the proof front", "fix proof drift"),
}


TYPED_ONLY_COMMANDS = (
    "plugins/quenching/commands/components/command/retro.md",
)


def source_description(path):
    return str(parse_frontmatter(path.read_text(encoding="utf-8"))["description"])


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

    def _manifest(self, payload):
        translate.configure(str(self.root), str(self.root))
        (self.root / ".agents" / ".generated-files.json").unlink(missing_ok=True)
        translate.write_tree(translate.generated_tree())
        (self.root / ".agents" / ".generated-files.json").write_text(json.dumps(payload), encoding="utf-8")

    def test_manifest_paths_that_escape_the_destination_delete_nothing(self):
        victim = self.root / "victim.txt"
        victim.write_text("keep", encoding="utf-8")
        outside = self.root.parent / f"{self.root.name}-outside"
        outside.mkdir()
        (outside / "target.txt").write_text("keep", encoding="utf-8")
        (self.root / ".agents").mkdir()
        (self.root / ".agents" / "link").symlink_to(outside)
        self.addCleanup(lambda: [p.unlink() for p in outside.iterdir()] and outside.rmdir() or None)
        for rel in ("../victim.txt", str(victim), "link/target.txt"):
            with self.subTest(rel=rel):
                self._manifest({"files": [rel]})
                with self.assertRaises(ValueError):
                    translate.write_tree(translate.generated_tree())
                self.assertTrue(victim.is_file())
                self.assertTrue((outside / "target.txt").is_file())

    def test_manifest_without_files_is_a_structured_refusal(self):
        self._manifest({})
        with self.assertRaises(ValueError):
            translate.write_tree(translate.generated_tree())
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = translate.cmd_translate(argparse.Namespace(
                check=False, write=True, diff=False, source=str(self.root), target=str(self.root), json=True),
                str(self.root))
        self.assertEqual(code, 2)
        self.assertIn("ct-translation-refused", out.getvalue())

    def test_check_without_a_codex_surface_reports_no_drift(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = translate.cmd_translate(argparse.Namespace(
                check=True, write=False, diff=False, source=str(self.root), target=str(self.root), json=True),
                str(self.root))
        payload = json.loads(out.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["reconciliation"], "absent")
        self.assertEqual(payload["changed"], [])
        self.assertNotIn("ct-translation-drift", out.getvalue())
        self.assertFalse((self.root / ".agents").exists())

    def test_check_with_an_unmanifested_codex_surface_still_reports_drift(self):
        (self.root / ".agents").mkdir()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = translate.cmd_translate(argparse.Namespace(
                check=True, write=False, diff=False, source=str(self.root), target=str(self.root), json=True),
                str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("ct-translation-drift", out.getvalue())

    def test_damaged_manifest_never_raises_a_traceback(self):
        for payload in ({"files": [], "sha256": ["x"]}, {"files": [], "sha256": "x"}):
            with self.subTest(payload=payload):
                self._manifest(payload)
                self.assertEqual(translate.reconciliation(translate.generated_tree()), "untracked")

    def test_directory_entry_in_manifest_is_skipped_not_fatal(self):
        self._manifest({"files": ["skills"]})
        translate.write_tree(translate.generated_tree())
        self.assertTrue((self.root / ".agents" / "skills").is_dir())
        self.assertEqual(translate.differences(translate.generated_tree()), [])

    def test_manifest_with_conflict_markers_is_regenerated(self):
        self._manifest({})
        manifest = self.root / ".agents" / ".generated-files.json"
        manifest.write_text("<<<<<<< HEAD\n{}\n=======\n{}\n>>>>>>> main\n", encoding="utf-8")
        stale = self.root / ".agents" / "skills" / "gone" / "SKILL.md"
        stale.parent.mkdir(parents=True)
        stale.write_text("old", encoding="utf-8")
        translate.write_tree(translate.generated_tree())
        self.assertFalse(stale.exists())
        self.assertIn("files", json.loads(manifest.read_text(encoding="utf-8")))

    CONFLICT = "<<<<<<< HEAD\n{}\n=======\n{}\n>>>>>>> main\n"

    def test_conflicted_manifest_recovery_still_refuses_paths_outside_the_destination(self):
        translate.configure(str(self.root), str(self.root))
        translate.write_tree(translate.generated_tree())
        outside = self.root.parent / f"{self.root.name}-elsewhere"
        self.addCleanup(lambda: __import__("shutil").rmtree(outside, ignore_errors=True))
        __import__("shutil").copytree(self.root / ".agents" / "skills", outside)
        __import__("shutil").rmtree(self.root / ".agents" / "skills")
        (self.root / ".agents" / "skills").symlink_to(outside)
        (self.root / ".claude" / "commands" / "specs" / "status.md").write_text(
            COMMAND + "\nSource edit.\n", encoding="utf-8")
        (self.root / ".agents" / ".generated-files.json").write_text(self.CONFLICT, encoding="utf-8")
        with self.assertRaises(ValueError):
            translate.write_tree(translate.generated_tree())
        self.assertNotIn("Source edit.", (outside / "specs" / "status" / "SKILL.md").read_text(encoding="utf-8"))

    def test_check_reports_a_conflicted_manifest(self):
        translate.configure(str(self.root), str(self.root))
        translate.write_tree(translate.generated_tree())
        manifest = self.root / ".agents" / ".generated-files.json"
        args = argparse.Namespace(check=True, write=False, diff=False, source=str(self.root),
                                  target=str(self.root), json=True)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(translate.cmd_translate(args, str(self.root)), 0)
        manifest.write_text(self.CONFLICT, encoding="utf-8")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = translate.cmd_translate(args, str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("ct-manifest-conflicted", out.getvalue())

    def test_check_reports_a_manifest_that_lost_an_entry(self):
        translate.configure(str(self.root), str(self.root))
        translate.write_tree(translate.generated_tree())
        manifest = self.root / ".agents" / ".generated-files.json"
        args = argparse.Namespace(check=True, write=False, diff=False, source=str(self.root),
                                  target=str(self.root), json=True)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(translate.cmd_translate(args, str(self.root)), 0)
        document = json.loads(manifest.read_text(encoding="utf-8"))
        lost = document["files"].pop(0)
        document["sha256"].pop(lost)
        manifest.write_text(json.dumps(document), encoding="utf-8")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(translate.cmd_translate(args, str(self.root)), 1)
        self.assertIn("ct-manifest-drift", out.getvalue())
        manifest.unlink()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(translate.cmd_translate(args, str(self.root)), 0)

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
        self.assertEqual(translate.reconciliation(tree),
                         "source-changed")
        translate.write_tree(tree)
        skill = self.root / ".agents" / "skills" / "specs" / "status" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\nCodex body edit.\n", encoding="utf-8")
        tree = translate.generated_tree()
        self.assertEqual(translate.reconciliation(tree),
                         "target-changed")

    def test_generated_from_is_stable_across_source_edits(self):
        translate.configure(str(self.root), str(self.root))
        translate.write_tree(translate.generated_tree())
        marker = self.root / ".agents" / ".generated-from.json"
        before = marker.read_bytes()
        self.assertNotIn(b"source_sha256", before)
        command = self.root / ".claude" / "commands" / "specs" / "status.md"
        command.write_text(COMMAND + "\nSource edit.\n", encoding="utf-8")
        translate.write_tree(translate.generated_tree())
        self.assertEqual(marker.read_bytes(), before)

    def test_reverse_write_propagates_body_and_refuses_frontmatter(self):
        translate.configure(str(self.root), str(self.root))
        translate.write_tree(translate.generated_tree())
        skill = self.root / ".agents" / "skills" / "specs" / "status" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\nCodex body edit.\n", encoding="utf-8")
        args = argparse.Namespace(source=str(self.root), target=str(self.root), check=False, write=True,
                                  diff=False, json=True)
        self.assertEqual(translate.cmd_translate(args, str(self.root)), 0)
        source_text = (self.root / ".claude" / "commands" / "specs" / "status.md").read_text()
        self.assertNotIn("Codex runtime", source_text)
        self.assertNotIn("host sub-agents only", source_text)
        self.assertNotIn("CODEX RUNTIME", source_text)
        self.assertIn("Claude body edit.", (self.root / ".claude" / "commands" / "specs" / "status.md")
                      .read_text(encoding="utf-8"))
        skill.write_text(skill.read_text(encoding="utf-8").replace("name: quenching-specs-status",
                                                                     "name: changed"), encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(translate.cmd_translate(args, str(self.root)), 2)
        self.assertIn("Claude side is authoritative", output.getvalue())

    def test_human_only_commands_get_a_codex_policy_that_blocks_implicit_invocation(self):
        commands = self.root / ".claude" / "commands" / "git"
        commands.mkdir(parents=True)
        (commands / "cleanup.md").write_text(
            "---\ndescription: Prune.\ndisable-model-invocation: true\n---\n\nBody.\n", encoding="utf-8")
        translate.configure(str(self.root), str(self.root))
        tree = translate.generated_tree()

        self.assertEqual(tree["skills/git/cleanup/agents/openai.yaml"],
                         b"policy:\n  allow_implicit_invocation: false\n")
        self.assertNotIn("skills/specs/status/agents/openai.yaml", tree)

    def test_package_translation_keeps_both_harness_names_exempt(self):
        source = translate.payload_root()
        translate.configure(str(source), str(self.root / "quenching-codex"))
        schema = translate.generated_tree()[
            "scripts/bin/quenching/knowledge/schema.py"
        ].decode("utf-8")

        self.assertIn('CLAUDE_HARNESS = "CLAUDE" + ".md"', schema)
        self.assertIn('EXEMPT = (CLAUDE_HARNESS, "AGENTS.md")', schema)

    def test_package_translation_adjusts_codex_check_root(self):
        source = translate.payload_root()
        translate.configure(str(source), str(self.root / "quenching-codex"))
        citation = translate.generated_tree()["checks/citation-check.sh"].decode("utf-8")
        functional = translate.generated_tree()["checks/functional-checks.sh"].decode("utf-8")
        self.assertIn('SELF_DIR/../../../"', citation)
        self.assertNotIn('SELF_DIR/../../../.."', citation)
        self.assertNotIn("claude -p", functional)
        self.assertIn("INCONCLUSIVE", functional)
        self.assertTrue(functional.rstrip().endswith("exit 2"))

    def test_codex_readme_accepts_changelog_extracted_from_upgrade_section(self):
        source = (
            "The CLI has two equivalent entry points: `bin/cq` and `assets/bin/cq`.\n\n"
            "## Upgrade\n\n"
            "The release history is kept in the root `CHANGELOG.md`.\n"
        )

        translated = translate.codex_readme(source)

        self.assertIn("The CLI is bundled inside the plugin", translated)
        self.assertIn("Resolution is **plugin-first, with no user-level install**", translated)
        self.assertNotIn("The release history is kept in the root", translated)
        self.assertTrue(translated.endswith("\n"))

    def test_package_description_review_reduces_routed_surface_and_preserves_slots(self):
        source = translate.payload_root().parent.parent
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
            self.assertTrue(any(lead in description for lead in ("Triggers on ", "Use when ", "Use for ")), relative)
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


class ModuleNamespaceTranslation(unittest.TestCase):
    def test_module_ids_become_one_codex_skill_id_and_a_wrong_owner_refuses(self):
        text = "see /quenching-specs:specs:develop, /quenching-align:align and /quenching-specs:handoff"
        self.assertEqual("see quenching-specs-develop, quenching-align and quenching-handoff",
                         translate.transform_platform(text, {"replacements": {}}))
        with self.assertRaises(ValueError):
            translate.transform_platform("/quenching-" + "design:specs:develop", {"replacements": {}})


class PayloadResolution(unittest.TestCase):
    """Where the translator finds itself, and what a BARE invocation therefore translates.

    Both were read off `Path(__file__).parents[7]`, a hop count that only lands in a development
    clone of the marketplace. An installed plugin carries the payload alone, so the adaptation map
    resolved two directories above it and every subcommand died on the missing JSON; a target repo
    invoking the bare probe measured the PACKAGED pair and reported that verdict as its own.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / ".claude" / "commands").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_payload_root_is_the_directory_carrying_the_adaptation_map(self):
        payload = translate.payload_root()
        self.assertTrue((payload / "assets" / "translation" / "codex-adaptation.json").is_file())
        self.assertTrue((payload / "commands").is_dir())

    def test_installed_layout_resolves_the_adaptation_map(self):
        """The layout that used to crash: the payload alone under `<marketplace>/<plugin>/<version>/`,
        with no `plugins/` tree anywhere above it."""
        installed = self.root / "cache" / "claude-quenching" / "quenching" / "9.9.9"
        installed.mkdir(parents=True)
        source = translate.payload_root() / "assets" / "translation" / "codex-adaptation.json"
        destination = installed / "assets" / "translation" / "codex-adaptation.json"
        destination.parent.mkdir(parents=True)
        destination.write_bytes(source.read_bytes())
        module = installed / "assets" / "bin" / "quenching" / "components" / "commands"
        module.mkdir(parents=True)
        resolved = next(parent for parent in (module / "translate.py").parents
                        if (parent / "assets" / "translation" / "codex-adaptation.json").is_file())
        self.assertEqual(resolved, installed)

    def test_bare_invocation_outside_the_marketplace_translates_the_callers_repository(self):
        translate.configure(None, None, str(self.root / ".claude"))
        self.assertEqual(translate.source(), self.root)
        self.assertEqual(translate.target(), self.root)
        self.assertFalse(translate.plugin_translation())
        self.assertEqual(translate.claude_surface(), self.root / ".claude")
        self.assertEqual(translate.codex_surface(), self.root / ".agents")

    def test_bare_invocation_inside_a_marketplace_with_the_sibling_translates_the_packaged_pair(self):
        payload = self.root / "plugins" / "quenching"
        payload.mkdir(parents=True)
        (self.root / "plugins" / "quenching-codex").mkdir()
        self.assertEqual(translate._default_pair(payload, str(self.root / ".claude")),
                         (payload, self.root / "plugins" / "quenching-codex"))

    def test_bare_invocation_inside_the_marketplace_without_the_sibling_translates_the_repository(self):
        payload = self.root / "plugins" / "quenching"
        payload.mkdir(parents=True)
        self.assertEqual(translate._default_pair(payload, str(self.root)),
                         (self.root, self.root))

    def test_the_adaptation_map_is_the_payloads_whatever_the_pair(self):
        expected = translate.payload_root() / "assets" / "translation" / "codex-adaptation.json"
        for source, target, root in ((None, None, str(self.root / ".claude")),
                                     (str(self.root), str(self.root), str(self.root / ".claude")),
                                     (None, None, str(translate.payload_root().parent.parent))):
            with self.subTest(source=source):
                translate.configure(source, target, root)
                self.assertEqual(translate.manifest(), expected)
                self.assertIsInstance(translate.read_adaptation(), dict)


class ConcludeGeneratedConflictRecipeTest(unittest.TestCase):
    def test_recipe_regenerates_the_specs_reader_before_concluding_the_merge(self):
        text = (Path(__file__).resolve().parents[1] / "commands" / "specs" / "conclude.md").read_text(encoding="utf-8")
        text = " ".join(text.split())
        self.assertNotIn("plugins/quenching-codex", text)
        for needle in ("regenerate before concluding the merge",
                       "python3 scripts/sync_specs_reader_plugin.py --write",
                       "python3 scripts/sync_specs_reader_plugin.py --check"):
            self.assertIn(needle, text)


class CodexRuntimeTranslation(unittest.TestCase):
    def test_skill_refuses_ambiguous_missing_or_failed_host_resolution(self):
        import os
        import subprocess
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cached = root / "plugins/cache/quenching/quenching-codex/6.4.0/scripts"
            cached.mkdir(parents=True)
            (cached / "cq").write_text("print('stale cache must not run')\n")
            tools = root / "tools"
            tools.mkdir()
            host = tools / "codex"
            active = {"name": "quenching-codex", "version": "6.4.0",
                      "marketplaceName": "quenching", "enabled": True}
            env = {**os.environ, "CODEX_HOME": str(root), "PATH": str(tools) + os.pathsep + os.environ["PATH"]}
            env.pop("PLUGIN_ROOT", None)
            env.pop("CODEX_PLUGIN_ROOT", None)
            for plugins, exit_code in (([], 0), ([active, active], 0),
                                       ([{**active, "version": "9.9.9"}], 0), ([active], 1)):
                with self.subTest(plugins=plugins, exit_code=exit_code):
                    payload = json.dumps({"installed": plugins})
                    host.write_text(f"#!/usr/bin/env python3\nprint({payload!r})\nraise SystemExit({exit_code})\n")
                    host.chmod(0o755)
                    result = subprocess.run(["bash", "-c", translate.CODEX_CQ_WRAPPER + "\ncq git status"],
                                            cwd=root, env=env, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                    self.assertNotIn("stale cache must not run", result.stdout)

    def test_skill_uses_the_enabled_package_instead_of_the_first_cached_copy(self):
        import os
        import re
        import subprocess
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for version in ("6.4.0", "6.8.0"):
                plugin = root / "plugins/cache/quenching/quenching-codex" / version
                (plugin / "scripts").mkdir(parents=True)
                (plugin / "scripts/cq").write_text(f"print({version!r})\n")
            tools = root / "tools"
            tools.mkdir()
            host = tools / "codex"
            first = subprocess.check_output(["find", str(root), "-name", "cq", "-print", "-quit"], text=True)
            selected = "6.8.0" if "/6.4.0/" in first else "6.4.0"
            payload = json.dumps({"installed": [{"name": "quenching-codex", "version": selected,
                                                 "marketplaceName": "quenching", "enabled": True}]})
            host.write_text(f"#!/usr/bin/env python3\nprint({payload!r})\n")
            host.chmod(0o755)
            env = {**os.environ, "CODEX_HOME": str(root), "PATH": str(tools) + os.pathsep + os.environ["PATH"]}
            env.pop("PLUGIN_ROOT", None)
            env.pop("CODEX_PLUGIN_ROOT", None)
            for command in ("cq git status", "cq --root . ops status", "cq --version"):
                with self.subTest(command=command):
                    text = translate.transform_codex_shell_blocks(f"```bash\n{command}\n```\n")
                    block = re.search(r"```bash\n(.*?)\n```", text, re.S)[1]
                    result = subprocess.run(["bash", "-c", block], cwd=root, env=env,
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout.strip(), selected)

    def test_generated_cli_runs_from_an_isolated_plugin_install(self):
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            installed = root / "cache/quenching-codex/6.4.0"
            translate.configure(str(translate.payload_root()), str(installed))
            for relative, content in translate.generated_tree().items():
                path = installed / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            launcher = [sys.executable, str(installed / "scripts/cq")]
            for front in ("specs", "components", "knowledge", "git", "design",
                          "ops", "proof", "toolchain", "delivery", "security"):
                with self.subTest(front=front):
                    result = subprocess.run([*launcher, front, "--help"], cwd=root,
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for command in ("cost", "context"):
                with self.subTest(command=command):
                    result = subprocess.run(
                        [*launcher, "components", "session", command, "--json"],
                        cwd=root, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                    self.assertIn("se-codex-telemetry-unavailable", result.stdout)
                    self.assertNotIn("Traceback", result.stderr)

    def test_runtime_maps_active_models_preserving_fixture_data(self):
        saved = (translate.SOURCE, translate.TARGET, translate.MANIFEST)
        self.addCleanup(lambda: setattr(translate, "SOURCE", saved[0]))
        self.addCleanup(lambda: setattr(translate, "TARGET", saved[1]))
        self.addCleanup(lambda: setattr(translate, "MANIFEST", saved[2]))
        translate.configure(str(translate.payload_root()), str(translate.payload_root()))
        adaptation = translate.read_adaptation()
        raw = "model: opus\neffort: high\nNever haiku for product code; sonnet worker.\n```python\nfixture = 'opus'\n```\n"
        result = translate.transform_codex_runtime(raw, adaptation)
        self.assertIn("model: gpt-6-astra", result)
        self.assertIn("effort: high", result)
        self.assertIn("Never gpt-6-luna for product code; gpt-6.1-sol worker", result)
        self.assertIn("fixture = 'opus'", result)
        self.assertIn("model: opus", raw)

    def test_runtime_policy_admits_luna_only_on_a_protected_oracle(self):
        adaptation = {"runtime": {"models": {"opus": "gpt-6-astra", "sonnet": "gpt-6.1-sol",
                                             "haiku": "gpt-6-luna"}}}
        policy = translate.codex_runtime_policy(adaptation)
        self.assertIn("`oracleProtected` and `smallTierEligible`", policy)
        self.assertIn("Never use gpt-6-luna for judgment roles or for import-memory", policy)
        self.assertNotIn("Never use gpt-6-luna for product code", policy)

    def test_generated_protocols_use_codex_models_and_host_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            translate.configure(str(translate.payload_root()), tmp)
            tree = translate.generated_tree()
        orchestrator = tree["agents/orchestrator.md"].decode()
        autopilot = tree["skills/quenching-specs-autopilot/SKILL.md"].decode()
        memory = tree["skills/quenching-knowledge-import-memory/SKILL.md"].decode()
        self.assertIn("model: gpt-6-astra", orchestrator)
        self.assertIn("spec-runner` on gpt-6.1-sol", orchestrator)
        self.assertNotIn("CLAUDE_CODE_SESSION_ID", orchestrator)
        self.assertIn("host-provided usage", orchestrator)
        self.assertIn("liveness as unmeasured", autopilot)
        self.assertNotIn("transcript's mtime", autopilot)
        self.assertNotIn("~/.codex/projects/", memory)
        self.assertIn("existing Claude-format project memory data", memory)
        self.assertNotIn("read with\n`cq components session cost`", autopilot)
        self.assertIn("`model: gpt-6.1-sol`, `effort: low`", memory)
        self.assertIn("Use Codex host sub-agents only", memory)
        self.assertIn(".claude/quenching.json", translate.transform_platform(".claude/quenching.json", translate.read_adaptation()))

    def test_generated_measurements_refuse_instead_of_launching_source_runtime(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            translate.configure(str(translate.payload_root()), tmp)
            tree = translate.generated_tree()
            script = Path(tmp) / "functional-checks.sh"
            script.write_bytes(tree["checks/functional-checks.sh"])
            result = subprocess.run(["bash", str(script)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("INCONCLUSIVE", result.stderr)
        self.assertIn(b"se-codex-telemetry-unavailable", tree["scripts/bin/quenching/session/commands/cost.py"])
        self.assertIn(b'CONFIG_FILE = os.path.join(".claude", "quenching.json")',
                      tree["scripts/bin/quenching/common/config.py"])

    def test_generated_config_reads_the_shared_claude_envelope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            translate.configure(str(translate.payload_root()), str(root / "out"))
            code = translate.generated_tree()["scripts/bin/quenching/common/config.py"].decode()
            (root / ".claude").mkdir()
            (root / ".claude/quenching.json").write_text(json.dumps({"specs": {"backend": "git"}}))
            namespace = {"__name__": "generated_shared_config"}
            exec(compile(code, "generated_config.py", "exec"), namespace)
            cfg = namespace["load_config"](str(root), detect_provider_info=False)
            self.assertEqual(cfg["specs"]["backend"], "git")

    def test_runtime_prefix_edits_are_refused_without_changing_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            command = root / ".claude/commands/specs/status.md"
            command.parent.mkdir(parents=True)
            command.write_text(COMMAND)
            translate.configure(str(root), str(root))
            tree = translate.generated_tree()
            translate.write_tree(tree)
            skill = root / ".agents/skills/specs/status/SKILL.md"
            skill.write_text(skill.read_text().replace("Use Codex host sub-agents only", "Use other sub-agents"))
            with self.assertRaisesRegex(ValueError, "runtime policy change"):
                translate.propagate_bodies_from_codex(tree)
            self.assertEqual(command.read_text(), COMMAND)


class CodexReviewRemoval(unittest.TestCase):
    """A Codex run never nests Codex: the generated surface carries no Codex review step."""

    def setUp(self):
        saved = (translate.SOURCE, translate.TARGET, translate.MANIFEST)
        self.addCleanup(lambda: setattr(translate, "SOURCE", saved[0]))
        self.addCleanup(lambda: setattr(translate, "TARGET", saved[1]))
        self.addCleanup(lambda: setattr(translate, "MANIFEST", saved[2]))
        translate.configure(str(translate.payload_root()), str(translate.payload_root()))

    def test_removal_cuts_the_span_and_keeps_the_rest(self):
        adaptation = {"removals": [{"command": "specs/x", "from": "A", "until": "C", "replace": "N "}]}
        self.assertEqual(translate.apply_removals("1 A B C 2", "specs/x", adaptation), "1 N C 2")
        self.assertEqual(translate.apply_removals("1 A B C 2", "specs/y", adaptation), "1 A B C 2")

    def test_missing_marker_fails_instead_of_going_silent(self):
        adaptation = {"removals": [{"command": "specs/x", "from": "ZZZ", "replace": ""}]}
        with self.assertRaises(ValueError):
            translate.apply_removals("1 A B C 2", "specs/x", adaptation)

    def test_generated_skills_carry_no_codex_review_step(self):
        skills = {path: data.decode() for path, data in translate.generated_tree().items()
                  if path.startswith("skills/") and path.endswith("SKILL.md")}
        self.assertTrue(skills)
        for path, text in skills.items():
            with self.subTest(skill=path):
                self.assertNotRegex(text, r"cq codex (probe|review)")
                self.assertNotRegex(text, r"scripts/cq'[^\n]*\bcodex (probe|review)\b")
        for name in ("autopilot", "conclude"):
            self.assertIn("Codex review: unavailable", skills[f"skills/quenching-specs-{name}/SKILL.md"])
