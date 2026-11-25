"""A client that reads several directories still gets each generated skill once.

Measured 2026-11-25: Claude Code 2.1.332 reads `.claude/skills` only, Codex 0.165.0 reads
`.agents/skills` only, and VS Code + Copilot Chat discovers every `SKILL.md` under `.agents/skills`,
`.github/skills` and `.claude/skills` before deduplicating by name. The deploy publishes into the
minimal cover of what the declared harnesses read; a target that declares two exclusive readers
(`claude` and `codex`) keeps the two copies because neither client reads the other's directory.
"""
from __future__ import annotations

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

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401

from quenching.components.commands import bridge  # noqa: E402
from quenching.deploy import tree as deploy_tree  # noqa: E402
from quenching.deploy.cli import main as deploy_main  # noqa: E402

# Every directory a client of this era reads: VS Code + Copilot Chat discovers all three.
CLIENT_DIRS = (".agents/skills", ".github/skills", ".claude/skills")
AGENTS_SKILLS = ".agents/skills"
CLAUDE_SKILLS = ".claude/skills"
BOTH = {AGENTS_SKILLS, CLAUDE_SKILLS}


def skill_md_dirs(tree: dict, name: str) -> set[str]:
    return {directory for directory in CLIENT_DIRS
            if f"{directory}/{name}/SKILL.md" in tree}


def skill_md_count(tree: dict) -> int:
    return sum(1 for rel in tree
               if rel.endswith("/SKILL.md")
               and rel.startswith(tuple(directory + "/" for directory in CLIENT_DIRS)))


class Publication(unittest.TestCase):
    """The cover over the declared harnesses, read off the tree the deploy builds."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.target = pathlib.Path(tmp.name)
        self.source = deploy_tree.source_root()

    def build(self, *harnesses: str) -> dict:
        return deploy_tree.build_tree(self.source, self.target, ["quenching-specs"],
                                      list(harnesses))

    def assert_published_once(self, expected: set[str], *harnesses: str) -> None:
        built = self.build(*harnesses)
        tree, names = built["tree"], built["manifest"]["skills"]
        self.assertTrue(names)
        for name in names:
            self.assertEqual(expected, skill_md_dirs(tree, name), (harnesses, name))
        self.assertEqual(len(names) * len(expected), skill_md_count(tree), harnesses)

    def test_claude_alone_publishes_only_the_claude_copy(self):
        self.assert_published_once({CLAUDE_SKILLS}, "claude")

    def test_a_client_that_reads_both_does_not_force_a_second_copy(self):
        self.assert_published_once({CLAUDE_SKILLS}, "claude", "opencode")

    def test_codex_alone_publishes_only_the_generic_copy(self):
        self.assert_published_once({AGENTS_SKILLS}, "codex")

    def test_opencode_alone_publishes_once_in_the_generic_layer_it_prefers(self):
        self.assert_published_once({AGENTS_SKILLS}, "opencode")

    def test_no_harness_keeps_the_generic_layer(self):
        self.assert_published_once({AGENTS_SKILLS})

    def test_two_exclusive_readers_keep_the_two_copies(self):
        self.assert_published_once(BOTH, "claude", "codex")
        self.assert_published_once(BOTH, "claude", "codex", "opencode")

    def test_only_the_claude_copy_carries_the_bridge_marker(self):
        tree = self.build("claude", "codex")["tree"]
        name = "quenching-specs"
        claude = tree[f"{CLAUDE_SKILLS}/{name}/SKILL.md"][0].decode()
        agents = tree[f"{AGENTS_SKILLS}/{name}/SKILL.md"][0].decode()
        self.assertIn(bridge.marker(name), claude)
        self.assertNotIn(bridge.marker(name), agents)

    def test_the_seed_names_the_published_directory(self):
        built = self.build("claude")
        self.assertIn("`.claude/skills/` (published", built["seeds"]["AGENTS.md"])
        self.assertNotIn("`.agents/skills/` (source)", built["seeds"]["AGENTS.md"])

    def test_a_claude_only_target_without_own_skills_has_no_bridge_manifest(self):
        tree = self.build("claude")["tree"]
        self.assertNotIn(f"{CLAUDE_SKILLS}/.generated-files.json", tree)


class Upgrade(unittest.TestCase):
    """A real deploy, narrowed after the fact: the redundant copy is a deletion, never drift."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.target = pathlib.Path(tmp.name)
        subprocess.run(["git", "-C", str(self.target), "init", "-q"], check=True,
                       capture_output=True)
        env = mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.target / ".xdg"),
                                           "OPENCODE_CONFIG": ""})
        env.start()
        self.addCleanup(env.stop)
        precompile = mock.patch("quenching.deploy.cli._precompile", return_value=None)
        precompile.start()
        self.addCleanup(precompile.stop)

    def deploy(self, *argv: str) -> tuple[int, dict]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = deploy_main(["--target", str(self.target), *argv, "--json"])
        return code, json.loads(out.getvalue() or "{}")

    def test_switching_to_claude_only_deletes_the_generic_copy(self):
        self.assertEqual(0, self.deploy("--modules", "specs", "--harness", "claude",
                                        "--harness", "codex", "--write")[0])
        self.assertTrue((self.target / AGENTS_SKILLS / "quenching-specs/SKILL.md").is_file())
        code, payload = self.deploy("--harness", "claude", "--check")
        self.assertEqual(1, code)
        self.assertIn({"path": f"{AGENTS_SKILLS}/quenching-specs/SKILL.md",
                       "change": "delete"}, payload["changes"])
        self.assertEqual(0, self.deploy("--harness", "claude", "--write")[0])
        self.assertFalse((self.target / AGENTS_SKILLS / "quenching-specs").exists())
        self.assertTrue((self.target / CLAUDE_SKILLS / "quenching-specs/SKILL.md").is_file())
        code, payload = self.deploy("--check")
        self.assertEqual((0, []), (code, payload["changes"]))


if __name__ == "__main__":
    unittest.main()
