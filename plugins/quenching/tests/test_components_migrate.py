"""Executable proofs for `cq components migrate`: the legacy `.claude/` source moves to `.agents/`."""
from __future__ import annotations

import contextlib
import io
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.components.commands.cli import main as components_main

COMMAND = ("---\ndescription: Create a table.\nallowed-tools: Bash\n---\n"
           "Read .claude/references/bundle/rules.md and .claude/commands/bundle/tabela/criar.md.\n"
           "Then run /bundle:tabela:criar, never /bundle:tabela:criar:x.\n"
           + "".join(f"Step {n}: a line of body that the move keeps unchanged.\n"
                     for n in range(20)))


class Migrate(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = pathlib.Path(tmp.name)
        self.git("init", "-q")
        self.write(".claude/commands/bundle/tabela/criar.md", COMMAND)
        self.write(".claude/references/bundle/rules.md", "rules\n")
        self.write(".agents/skills/bundle/tabela/criar/SKILL.md", "translated copy\n")
        self.write(".agents/references/bundle/rules.md", "translated rules\n")
        self.write(".claude/quenching.json", '{"backend": "github"}\n')
        self.write(".claude/agents/runner.md", "---\nname: runner\n---\n")
        self.write("CLAUDE.md", "# Instructions\n")
        self.git("add", "-A")
        self.git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "legacy")

    def git(self, *argv):
        return subprocess.run(["git", "-C", str(self.repo), *argv], check=True,
                              capture_output=True, text=True).stdout

    def write(self, rel, text):
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def run_cli(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = components_main(["migrate", "--target", str(self.repo), "--json", *argv])
        return code, json.loads(out.getvalue() or "{}")

    def test_plan_writes_nothing_and_exits_1(self):
        code, payload = self.run_cli()
        self.assertEqual((1, False), (code, payload["conformant"]))
        self.assertEqual({".claude/commands/bundle/tabela/criar.md":
                          ".agents/skills/bundle-tabela-criar/SKILL.md"}, payload["renames"])
        self.assertTrue((self.repo / ".claude/commands/bundle/tabela/criar.md").is_file())

    def test_write_moves_the_source_and_drops_the_translation(self):
        self.assertEqual(0, self.run_cli("--write")[0])
        skill = (self.repo / ".agents/skills/bundle-tabela-criar/SKILL.md").read_text()
        self.assertTrue(skill.startswith("---\nname: bundle-tabela-criar\ndescription:"))
        self.assertIn(".agents/references/bundle/rules.md", skill)
        self.assertIn(".agents/skills/bundle-tabela-criar/SKILL.md", skill)
        self.assertIn("run /bundle-tabela-criar, never /bundle:tabela:criar:x.", skill)
        self.assertEqual("rules\n", (self.repo / ".agents/references/bundle/rules.md").read_text())
        self.assertFalse((self.repo / ".agents/skills/bundle").exists())
        self.assertFalse((self.repo / ".claude/commands").exists())
        self.assertEqual('{"backend": "github"}\n',
                         (self.repo / ".agents/quenching.json").read_text())
        self.assertEqual("# Instructions\n", (self.repo / "AGENTS.md").read_text())
        self.assertEqual("@AGENTS.md\n", (self.repo / "CLAUDE.md").read_text())
        self.assertTrue((self.repo / ".claude/agents/runner.md").is_file())
        status = self.git("status", "--porcelain")
        self.assertIn("R  .claude/commands/bundle/tabela/criar.md -> "
                      ".agents/skills/bundle-tabela-criar/SKILL.md", status)

    def test_second_pass_is_conformant(self):
        self.run_cli("--write")
        code, payload = self.run_cli()
        self.assertEqual((0, True), (code, payload["conformant"]))

    def test_two_configurations_that_differ_are_a_conflict_and_nothing_is_written(self):
        self.write(".agents/quenching.json", '{"backend": "git"}\n')
        self.git("add", "-A")
        code, payload = self.run_cli()
        self.assertEqual(1, code)
        self.assertEqual(".agents/quenching.json", payload["conflicts"][0]["path"])
        self.assertEqual(2, self.run_cli("--write")[0])
        self.assertTrue((self.repo / ".claude/commands/bundle/tabela/criar.md").is_file())

    def test_own_instructions_in_both_harness_files_are_a_conflict(self):
        self.write("AGENTS.md", "# Other\n")
        self.git("add", "-A")
        code, payload = self.run_cli()
        self.assertEqual(1, code)
        self.assertEqual("AGENTS.md", payload["conflicts"][0]["path"])

    def test_an_agents_md_equal_to_claude_md_only_turns_claude_md_into_the_pointer(self):
        self.write("AGENTS.md", "# Instructions\n")
        self.git("add", "-A")
        code, payload = self.run_cli()
        self.assertEqual(1, code)
        self.assertEqual([], payload["conflicts"])
        self.assertIn({"op": "pointer", "path": "CLAUDE.md"}, payload["operations"])

    def test_outside_git_refuses(self):
        with tempfile.TemporaryDirectory() as plain:
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                code = components_main(["migrate", "--target", plain, "--json"])
        self.assertEqual(2, code)


if __name__ == "__main__":
    unittest.main()
