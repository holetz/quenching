"""Repository-surface translation keeps Claude configuration authoritative."""
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


class AdaptationMap(unittest.TestCase):
    def test_the_adaptation_map_is_the_payloads_whatever_the_pair(self):
        expected = translate.payload_root() / "assets" / "translation" / "codex-adaptation.json"
        with tempfile.TemporaryDirectory() as tmp:
            translate.configure(tmp, tmp)
            self.assertEqual(translate.manifest(), expected)
            self.assertIsInstance(translate.read_adaptation(), dict)


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

