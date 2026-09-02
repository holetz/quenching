"""Keep published surface listings derived from the structures they describe.

Counts come from ``commands/**/*.md`` and the site set comes from the same allow-list used by the
site-source staging rail. The prose remains hand-written, but a changed population or nav cannot
silently leave its consumers stale.
"""
from __future__ import annotations

import json
import pathlib
import re
import tomllib
import unittest

import _paths  # noqa: F401
from quenching.knowledge.site_source import _selected_files

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "quenching"
COMMANDS = PLUGIN_ROOT / "commands"
DOCS = REPO_ROOT / "docs"
README = REPO_ROOT / "README.md"
PROJECT_COMMANDS = DOCS / "project" / "commands.md"
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
PLUGIN_MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
ZENSICAL = REPO_ROOT / "zensical.toml"
ADAPTATION = PLUGIN_ROOT / "assets" / "translation" / "codex-adaptation.json"

INVOCABLE = re.compile(r"`(/[a-z][a-z:-]*)`")


def _commands_on_disk() -> set[str]:
    return {
        "/quenching:" + path.relative_to(COMMANDS).with_suffix("").as_posix().replace("/", ":")
        for path in COMMANDS.rglob("*.md")
    }


def _published_docs_on_disk() -> set[str]:
    return {
        path.relative_to(DOCS).as_posix()
        for path in _selected_files(DOCS)
        if path.suffix == ".md"
    }


def _nav_paths(value: object) -> set[str]:
    if isinstance(value, str):
        return {value} if value.endswith(".md") else set()
    if isinstance(value, list):
        paths: set[str] = set()
        for item in value:
            paths.update(_nav_paths(item))
        return paths
    if isinstance(value, dict):
        paths: set[str] = set()
        for item in value.values():
            paths.update(_nav_paths(item))
        return paths
    return set()


def _manifest_descriptions() -> list[str]:
    marketplace = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    return [marketplace["description"], marketplace["plugins"][0]["description"],
            json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))["description"]]


class ManifestSurfaceTests(unittest.TestCase):
    def test_manifest_counts_match_the_command_population(self):
        commands = _commands_on_disk()
        counts = {
            "commands": len(commands),
            "local fronts": len({command.split(":")[1] for command in commands
                                  if command.split(":")[1] in {
                                      "knowledge", "design", "components", "ops", "proof",
                                      "toolchain", "delivery",
                                  }}),
            "specs commands": sum(command.startswith("/quenching:specs:") for command in commands),
            "git commands": sum(command.startswith("/quenching:git:") for command in commands),
        }
        for description in _manifest_descriptions():
            for label, count in counts.items():
                if label == "local fronts":
                    pattern = rf"\b{count} (?:local|aligned) fronts\b"
                else:
                    pattern = rf"\b{count} {re.escape(label)}\b"
                self.assertRegex(description, pattern)

    def test_manifest_count_check_discriminates_a_changed_population(self):
        commands = _commands_on_disk()
        self.assertNotIn("/quenching:invented:command", commands)
        self.assertNotEqual(len(commands), len(commands | {"/quenching:invented:command"}))

    def test_manifest_projection_covers_each_namespace_derived_from_the_surface(self):
        commands = _commands_on_disk()
        expected = {
            "knowledge": 13,
            "specs": 6,
            "design": 3,
            "components": 7,
            "ops": 3,
            "proof": 3,
            "toolchain": 2,
            "delivery": 2,
            "security": 1,
            "git": 11,
        }
        actual = {
            namespace: sum(command.startswith(f"/quenching:{namespace}:") for command in commands)
            for namespace in expected
        }
        self.assertEqual(actual, expected)


class ListingSurfaceTests(unittest.TestCase):
    def test_project_catalog_lists_exactly_the_commands_on_disk(self):
        listed = set(INVOCABLE.findall(PROJECT_COMMANDS.read_text(encoding="utf-8")))
        self.assertEqual(listed, _commands_on_disk())

    def test_front_counts_and_workflow_prose_use_the_current_surface(self):
        texts = [
            README.read_text(encoding="utf-8"),
            (DOCS / "index.md").read_text(encoding="utf-8"),
            (DOCS / "tutorials" / "getting-started.md").read_text(encoding="utf-8"),
            (DOCS / "how-to" / "adopt-quenching.md").read_text(encoding="utf-8"),
            (DOCS / "standards" / "architecture" / "index.md").read_text(encoding="utf-8"),
            ADAPTATION.read_text(encoding="utf-8"),
        ]
        combined = "\n".join(texts).lower()
        self.assertGreaterEqual(combined.count("seven"), 1)
        for stale in ("five local fronts", "five fronts", "five-front order", "develop` → `main",
                       "develop` carries"):
            self.assertNotIn(stale, combined)

    def test_root_workflow_prose_matches_the_declared_ci_and_branch_flow(self):
        root_readme = README.read_text(encoding="utf-8").lower()
        self.assertIn("runs on pushes and pull requests", root_readme)
        self.assertIn("single **`main`** branch", root_readme)
        for stale in ("workflow_dispatch", "apply enabled", "checkout of `develop`"):
            self.assertNotIn(stale, root_readme)

    def test_zensical_nav_matches_every_published_markdown_document(self):
        config = tomllib.loads(ZENSICAL.read_text(encoding="utf-8"))
        nav = _nav_paths(config["project"]["nav"])
        published = _published_docs_on_disk()
        self.assertEqual(nav, published,
                         f"missing={sorted(published - nav)}, extra={sorted(nav - published)}")

    def test_nav_check_discriminates_missing_and_extra_paths(self):
        expected = {"index.md", "glossary.md"}
        self.assertNotEqual(expected, expected - {"glossary.md"})
        self.assertNotEqual(expected, expected | {"rogue.md"})


if __name__ == "__main__":
    unittest.main()
