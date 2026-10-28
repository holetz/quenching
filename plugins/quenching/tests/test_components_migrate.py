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
from quenching.components.commands import translate
from quenching.components.commands.cli import main as components_main

COMMAND = ("---\ndescription: Create a table.\nallowed-tools: Bash\n---\n"
           "Read .claude/references/bundle/rules.md and .claude/commands/bundle/tabela/criar.md.\n"
           "Then run /bundle:tabela:criar, never /bundle:tabela:criar:x.\n"
           'Or call Skill(skill="bundle:tabela:criar"), Skill(\'bundle:tabela:criar\', args="t"), '
           'Skill(bundle:tabela:criar) or {"skill": "bundle:tabela:criar"}, '
           'never Skill(skill="bundle:tabela:criar:x").\n'
           "Branch with /quenching-specs:git:branch first.\n"
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
        tree = self.translation()
        self.write(".agents/skills/bundle/tabela/criar/SKILL.md",
                   tree["skills/bundle/tabela/criar/SKILL.md"].decode())
        self.write(".agents/references/bundle/rules.md", tree["references/bundle/rules.md"].decode())
        self.write(".claude/quenching.json", '{"backend": "github"}\n')
        self.write(".claude/agents/runner.md", "---\nname: runner\n---\n")
        self.write("CLAUDE.md", "# Instructions\n")
        self.git("add", "-A")
        self.git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "legacy")

    def translation(self):
        translate.configure(str(self.repo), str(self.repo))
        return translate.generated_tree()

    def commit(self, message="next"):
        self.git("add", "-A")
        self.git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", message)

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

    def test_untracked_home_beside_the_legacy_file_is_a_conflict(self):
        self.write(".agents/quenching.json", '{"backend": "git"}\n')
        code, payload = self.run_cli()
        self.assertEqual(1, code)
        self.assertEqual("the home exists but is not tracked", payload["conflicts"][0]["why"])
        self.assertTrue((self.repo / ".claude/quenching.json").is_file())

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

    def test_an_agents_md_without_claude_md_gets_the_pointer(self):
        self.git("mv", "CLAUDE.md", "AGENTS.md")
        code, payload = self.run_cli()
        self.assertEqual(1, code)
        self.assertIn({"op": "pointer", "path": "CLAUDE.md"}, payload["operations"])
        self.assertEqual(0, self.run_cli("--write")[0])
        self.assertEqual("@AGENTS.md\n", (self.repo / "CLAUDE.md").read_text())

    def test_a_manual_skill_with_the_translation_name_is_a_conflict_and_nothing_is_written(self):
        self.write(".agents/skills/bundle/tabela/criar/SKILL.md",
                   "---\nname: criar\ndescription: My own skill.\n---\nhand written\n")
        self.commit()
        code, payload = self.run_cli()
        self.assertEqual(1, code)
        self.assertIn({"path": ".agents/skills/bundle/tabela/criar/SKILL.md",
                       "with": ".claude/commands/bundle/tabela/criar.md",
                       "why": "differs from the translation of its source"}, payload["conflicts"])
        self.assertEqual(2, self.run_cli("--write")[0])
        self.assertEqual("", self.git("status", "--porcelain"))

    def test_a_manual_reference_with_the_translation_path_is_a_conflict(self):
        self.write(".agents/references/bundle/rules.md", "my own rules\n")
        self.commit()
        code, payload = self.run_cli()
        self.assertEqual(".agents/references/bundle/rules.md", payload["conflicts"][0]["path"])

    def test_a_stale_translation_of_an_earlier_source_is_still_the_old_translation(self):
        self.write(".claude/references/bundle/rules.md", "rules, revised\n")
        self.write(".claude/commands/bundle/tabela/criar.md", COMMAND + "A later line.\n")
        self.commit()
        code, payload = self.run_cli()
        self.assertEqual((1, []), (code, payload["conflicts"]))
        self.assertIn({"op": "remove", "path": ".agents/skills/bundle/tabela/criar/SKILL.md",
                       "why": "translation of .claude/commands/bundle/tabela/criar.md"},
                      payload["operations"])

    def test_a_translation_from_an_older_translator_is_the_old_translation(self):
        rel = ".agents/skills/bundle/tabela/criar/SKILL.md"
        text = (self.repo / rel).read_text()
        start = text.index("<!-- CODEX RUNTIME START -->")
        end = text.index("<!-- CODEX RUNTIME END -->\n\n") + len("<!-- CODEX RUNTIME END -->\n\n")
        text = text[:start] + text[end:]
        text = text.replace("/quenching-specs:git:branch", "quenching-git-branch")
        text = text.replace(".agents/references/", ".claude/references/")
        self.write(rel, text)
        self.commit()
        self.assertEqual([], self.run_cli()[1]["conflicts"])

    def test_a_copy_edited_beside_its_source_is_retired_one_edited_ahead_is_not(self):
        rules = ".claude/references/bundle/rules.md"
        self.write(rules, "head\nrules\ntail\n")
        self.write(".agents/references/bundle/rules.md", "head\nrules\ntail\n")
        self.commit()
        self.write(rules, "head, revised\nrules\ntail, revised\n")
        self.write(".agents/references/bundle/rules.md", "head\nrules\ntail, revised\n")
        self.commit()
        self.assertEqual([], self.run_cli()[1]["conflicts"])
        self.write(".agents/references/bundle/rules.md", "head\nrules\ntail, only here\n")
        self.commit()
        self.assertEqual(".agents/references/bundle/rules.md",
                         self.run_cli()[1]["conflicts"][0]["path"])

    def test_the_skill_tool_forms_are_rewritten(self):
        self.assertEqual(0, self.run_cli("--write")[0])
        skill = (self.repo / ".agents/skills/bundle-tabela-criar/SKILL.md").read_text()
        self.assertIn('Or call Skill(skill="bundle-tabela-criar"), '
                      'Skill(\'bundle-tabela-criar\', args="t"), Skill(bundle-tabela-criar) or '
                      '{"skill": "bundle-tabela-criar"}, never Skill(skill="bundle:tabela:criar:x").',
                      skill)

    def test_legacy_openspec_and_opsx_stay_where_they_are(self):
        self.write(".claude/commands/opsx/propose.md", "---\ndescription: Propose.\n---\nbody\n")
        self.write(".claude/skills/openspec-propose/SKILL.md",
                   "---\nname: openspec-propose\ndescription: Openspec.\n---\nbody\n")
        self.commit()
        code, payload = self.run_cli()
        touched = json.dumps(payload["operations"]) + json.dumps(payload["conflicts"])
        self.assertNotIn("opsx", touched)
        self.assertNotIn("openspec", touched)
        self.assertEqual(0, self.run_cli("--write")[0])
        self.assertTrue((self.repo / ".claude/commands/opsx/propose.md").is_file())
        self.assertTrue((self.repo / ".claude/skills/openspec-propose/SKILL.md").is_file())
        self.assertEqual(0, self.run_cli()[0])

    def test_a_nested_skill_flattens_with_its_sibling_files_and_the_bridge_copies_them(self):
        nested = ".agents/skills/mlops/comum/"
        self.write(nested + "SKILL.md", "---\nname: comum\ndescription: Shared.\n---\n"
                                        "Run .agents/skills/mlops/comum/scripts/run.sh.\n")
        self.write(nested + "scripts/run.sh", "#!/bin/sh\necho ok\n")
        self.write(nested + "references/notes.md", "notes\n")
        self.write(nested + "deeper/SKILL.md", "---\nname: deeper\ndescription: Deeper.\n---\n")
        self.write(nested + "deeper/data.txt", "data\n")
        self.commit()
        code, payload = self.run_cli()
        self.assertEqual([], payload["conflicts"])
        self.assertEqual(".agents/skills/mlops-comum/scripts/run.sh",
                         payload["renames"][nested + "scripts/run.sh"])
        self.assertEqual(0, self.run_cli("--write")[0])
        flat = self.repo / ".agents/skills/mlops-comum"
        self.assertEqual({"SKILL.md", "scripts/run.sh", "references/notes.md"},
                         {p.relative_to(flat).as_posix() for p in flat.rglob("*") if p.is_file()})
        self.assertIn("Run .agents/skills/mlops-comum/scripts/run.sh.", (flat / "SKILL.md").read_text())
        self.assertTrue((self.repo / ".agents/skills/mlops-comum-deeper/data.txt").is_file())
        self.assertFalse((self.repo / ".agents/skills/mlops").exists())
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(0, components_main(["bridge", "--target", str(self.repo), "--write",
                                                 "--json"]))
        copy = self.repo / ".claude/skills/mlops-comum"
        self.assertEqual("#!/bin/sh\necho ok\n", (copy / "scripts/run.sh").read_text())
        self.assertEqual("notes\n", (copy / "references/notes.md").read_text())

    def test_outside_git_refuses(self):
        with tempfile.TemporaryDirectory() as plain:
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                code = components_main(["migrate", "--target", plain, "--json"])
        self.assertEqual(2, code)


if __name__ == "__main__":
    unittest.main()
