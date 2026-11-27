"""`.agents/skills` is the source of every generated skill, and `claude` adds its projection.

Measured 2026-11-25: Claude Code 2.1.332 reads `.claude/skills` only, Codex 0.165.0 reads
`.agents/skills` only, OpenCode reads both and prefers `.agents/skills`, and VS Code + Copilot Chat
discovers every `SKILL.md` under `.agents/skills`, `.github/skills` and `.claude/skills` before
deduplicating by name. So the deploy writes each generated skill in `.agents/skills` whatever the
harnesses, and with `claude` projects it into `.claude/skills`: the same bytes plus the bridge
marker, the rule the bridge applies to a target's own skills (ADR 0022).
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

    def assert_published(self, expected: set[str], *harnesses: str) -> None:
        built = self.build(*harnesses)
        tree, names = built["tree"], built["manifest"]["skills"]
        self.assertTrue(names)
        for name in names:
            self.assertEqual(expected, skill_md_dirs(tree, name), (harnesses, name))
        self.assertEqual(len(names) * len(expected), skill_md_count(tree), harnesses)

    def test_claude_alone_writes_the_source_and_its_projection(self):
        self.assert_published(BOTH, "claude")

    def test_claude_and_opencode_write_the_source_and_its_projection(self):
        self.assert_published(BOTH, "claude", "opencode")

    def test_every_harness_writes_the_source_and_its_projection(self):
        self.assert_published(BOTH, "claude", "codex", "opencode")

    def test_opencode_alone_writes_only_the_source(self):
        self.assert_published({AGENTS_SKILLS}, "opencode")

    def test_codex_alone_writes_only_the_source(self):
        self.assert_published({AGENTS_SKILLS}, "codex")

    def test_no_harness_keeps_the_source(self):
        self.assert_published({AGENTS_SKILLS})

    def cited_paths(self, tree: dict, directory: str) -> set[str]:
        import re
        cite = re.compile(r"(\.(?:agents|claude)/skills/quenching-[a-z-]+/[A-Za-z0-9/._-]+\.md)")
        found: set[str] = set()
        for rel, entry in tree.items():
            if rel.startswith(directory + "/") and rel.endswith(".md"):
                data = entry[0] if isinstance(entry, tuple) else entry
                text = data.decode("utf-8") if isinstance(data, bytes) else str(data)
                body = "\n".join(line for line in text.splitlines()
                                 if "by cq components bridge" not in line)
                found.update(cite.findall(body))
        return found

    def test_both_copies_cite_the_source(self):
        # A router reads each flow by path; `.agents/skills` always exists, so both copies cite it.
        tree = self.build("claude", "opencode")["tree"]
        for directory in (AGENTS_SKILLS, CLAUDE_SKILLS):
            cited = self.cited_paths(tree, directory)
            self.assertTrue(cited, directory)
            self.assertEqual(set(), {path for path in cited
                                     if not path.startswith(AGENTS_SKILLS + "/")}, directory)
            self.assertEqual(set(), {path for path in cited if path not in tree}, directory)

    def test_the_projection_is_the_source_plus_the_marker(self):
        tree = self.build("claude")["tree"]
        name = "quenching-specs"
        prefix = f"{AGENTS_SKILLS}/{name}/"
        sources = {rel[len(prefix):]: entry[0] for rel, entry in tree.items()
                   if rel.startswith(prefix)}
        self.assertIn("SKILL.md", sources)
        for rel, data in sources.items():
            projected = tree[f"{CLAUDE_SKILLS}/{name}/{rel}"][0]
            expected = (bridge.with_marker(data.decode(), name).encode()
                        if rel == "SKILL.md" else data)
            self.assertEqual(expected, projected, rel)
        self.assertNotIn(bridge.marker(name), sources["SKILL.md"].decode())

    def test_the_seed_names_the_source_and_the_copy(self):
        built = self.build("claude")
        self.assertIn("`.agents/skills/` (source) and `.claude/skills/` (generated copy)",
                      built["seeds"]["AGENTS.md"])

    def test_a_generic_target_seed_names_no_bridge_it_does_not_have(self):
        for harnesses in (("opencode",), ("codex",), ()):
            seed = self.build(*harnesses)["seeds"]["AGENTS.md"]
            self.assertIn("`.agents/skills/` (source", seed)
            self.assertNotIn(".claude/skills", seed)

    def test_a_mirrored_skill_is_the_deploys_not_the_bridges(self):
        # Its source now sits in `.agents/skills` too; the bridge must not claim it.
        (self.target / ".agents").mkdir()
        (self.target / ".agents/.quenching-deploy.json").write_text(json.dumps({
            "skills": ["quenching-specs"],
            "mirrors": [".agents/skills/quenching-ops", ".claude/skills/quenching-ops",
                        ".agents/quenching/assets/bin/quenching/ops"]}))
        self.assertEqual({"quenching-specs", "quenching-ops"}, bridge.deploy_owned(self.target))

    def test_a_claude_target_without_own_skills_has_no_bridge_manifest(self):
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

    def test_dropping_claude_deletes_only_the_projection(self):
        self.assertEqual(0, self.deploy("--modules", "specs", "--harness", "claude",
                                        "--write")[0])
        self.assertTrue((self.target / AGENTS_SKILLS / "quenching-specs/SKILL.md").is_file())
        self.assertTrue((self.target / CLAUDE_SKILLS / "quenching-specs/SKILL.md").is_file())
        code, payload = self.deploy("--harness", "opencode", "--check")
        self.assertEqual(1, code)
        self.assertIn({"path": f"{CLAUDE_SKILLS}/quenching-specs/SKILL.md",
                       "change": "delete"}, payload["changes"])
        self.assertNotIn(f"{AGENTS_SKILLS}/quenching-specs/SKILL.md",
                         {change["path"] for change in payload["changes"]})
        self.assertEqual(0, self.deploy("--harness", "opencode", "--write")[0])
        self.assertFalse((self.target / CLAUDE_SKILLS / "quenching-specs").exists())
        self.assertTrue((self.target / AGENTS_SKILLS / "quenching-specs/SKILL.md").is_file())
        code, payload = self.deploy("--check")
        self.assertEqual((0, []), (code, payload["changes"]))

    def test_a_claude_only_target_of_7_18_gains_the_source(self):
        # 7.18.x published a claude-only target's skills only under `.claude/skills`.
        self.assertEqual(0, self.deploy("--modules", "specs", "--harness", "claude",
                                        "--write")[0])
        manifest_path = self.target / ".agents/.quenching-deploy.json"
        manifest = json.loads(manifest_path.read_text())
        import shutil
        shutil.rmtree(self.target / AGENTS_SKILLS / "quenching-specs")
        manifest["files"] = {rel: digest for rel, digest in manifest["files"].items()
                             if not rel.startswith(AGENTS_SKILLS + "/")}
        manifest_path.write_text(json.dumps(manifest))
        code, payload = self.deploy("--check")
        self.assertEqual(1, code)
        self.assertIn({"path": f"{AGENTS_SKILLS}/quenching-specs/SKILL.md", "change": "create"},
                      payload["changes"])
        self.assertEqual(0, self.deploy("--write")[0])
        self.assertTrue((self.target / AGENTS_SKILLS / "quenching-specs/SKILL.md").is_file())
        self.assertEqual((0, []), (lambda r: (r[0], r[1]["changes"]))(self.deploy("--check")))


if __name__ == "__main__":
    unittest.main()
