"""Executable proofs for `cq deploy`: install the surface in an empty target."""
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
    import _paths  # noqa: F401
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.deploy.cli import main as deploy_main


class Deploy(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.target = pathlib.Path(tmp.name)
        self.git("init", "-q")

    def git(self, *argv):
        return subprocess.run(["git", "-C", str(self.target), *argv], check=True,
                              capture_output=True, text=True).stdout

    def run_deploy(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = deploy_main(["--target", str(self.target), *argv, "--json"])
        return code, json.loads(out.getvalue() or "{}")

    def target_cq(self, *argv):
        return subprocess.run([sys.executable, ".agents/quenching/bin/cq", *argv],
                              cwd=self.target, capture_output=True, text=True)

    def write(self, rel: str, text: str):
        path = self.target / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_write_creates_the_generic_layer_without_claude_md(self):
        code, payload = self.run_deploy("--modules", "core", "--write")
        self.assertEqual(0, code)
        self.assertTrue(payload["written"])
        for rel in ("AGENTS.md", ".agents/quenching.json", ".agents/.quenching-deploy.json",
                    ".agents/skills/quenching-specs-create/SKILL.md",
                    ".agents/quenching/bin/cq", ".claude/skills/quenching-specs-create/SKILL.md"):
            self.assertTrue((self.target / rel).exists(), rel)
        for rel in ("CLAUDE.md", ".claude/CLAUDE.md", ".claude/commands", ".claude/references"):
            self.assertFalse((self.target / rel).exists(), rel)
        version = self.target_cq("--version")
        self.assertEqual(0, version.returncode, version.stderr)
        status = self.target_cq("components", "status", "--json")
        self.assertEqual(0, status.returncode, status.stderr)
        document = json.loads(status.stdout)
        self.assertEqual((0, 44), (document["commands"], document["generated"]))
        template = (self.target / ".agents/quenching/assets/templates/harness/agents-root.md").read_text()
        self.assertIn("quenching-knowledge-add", template)
        self.assertNotIn("quenching-align:knowledge:add", template)
        check, again = self.run_deploy("--modules", "core", "--check")
        self.assertEqual((0, []), (check, again["changes"]))
        local = self.target_cq("deploy", "--target", ".", "--modules", "core", "--check", "--json")
        self.assertEqual(0, local.returncode, local.stdout + local.stderr)
        self.assertEqual([], json.loads(local.stdout)["changes"])

    def test_check_reports_drift_without_writing(self):
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        skill = self.target / ".agents/skills/quenching-specs-create/SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")
        code, payload = self.run_deploy("--modules", "core", "--check")
        self.assertEqual(1, code)
        self.assertIn({"path": ".agents/skills/quenching-specs-create/SKILL.md",
                       "change": "update"}, payload["changes"])
        self.assertIn("local edit", skill.read_text(encoding="utf-8"))

    def test_an_unowned_generated_skill_refuses_and_writes_nothing(self):
        self.write(".agents/skills/quenching-specs-create/SKILL.md",
                   "---\ndescription: mine\n---\nkeep me\n")
        code, payload = self.run_deploy("--modules", "core", "--write")
        self.assertEqual(2, code)
        self.assertEqual(".agents/skills/quenching-specs-create/SKILL.md", payload["conflicts"][0]["path"])
        self.assertFalse((self.target / ".agents/quenching").exists())
        self.assertIn("keep me", (self.target / ".agents/skills/quenching-specs-create/SKILL.md").read_text())

    def test_module_selection_limits_skills_and_enabled_pillars(self):
        self.assertEqual(0, self.run_deploy("--modules", "specs", "--write")[0])
        self.assertTrue((self.target / ".agents/skills/quenching-specs-create/SKILL.md").exists())
        self.assertFalse((self.target / ".agents/skills/quenching-knowledge-align").exists())
        modules = json.loads(self.target_cq("modules", "--json").stdout)
        enabled = {row["name"]: row["enabled"] for row in modules["modules"]}
        self.assertTrue(enabled["quenching-specs"])
        self.assertFalse(enabled["quenching-align"])
        config = json.loads((self.target / ".agents/quenching.json").read_text())
        self.assertEqual(["specs"], config["shared"]["profiles"]["installed"])
        self.assertNotIn("backend", config)

    def test_a_target_owned_skill_survives_and_is_bridged(self):
        self.write(".agents/skills/my-skill/SKILL.md",
                   "---\ndescription: Mine.\n---\n\nRead .agents/references/notes.md.\n")
        self.write(".agents/references/notes.md", "notes\n")
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        self.assertTrue((self.target / ".agents/skills/my-skill/SKILL.md").exists())
        copied = self.target / ".claude/skills/my-skill/SKILL.md"
        self.assertTrue(copied.exists())
        self.assertIn("generated from .agents/skills/my-skill/SKILL.md", copied.read_text())
        bridge = json.loads((self.target / ".claude/skills/.generated-files.json").read_text())
        self.assertIn("my-skill/SKILL.md", bridge["files"])
        self.assertEqual(0, self.target_cq("components", "bridge", "--target", ".",
                                           "--check", "--json").returncode)

    def test_a_pointer_only_claude_md_is_pruned_only_on_request(self):
        self.write("AGENTS.md", "# Mine\n")
        self.write("CLAUDE.md", "@AGENTS.md\n")
        code, payload = self.run_deploy("--modules", "core", "--write")
        self.assertEqual(0, code)
        self.assertTrue((self.target / "CLAUDE.md").exists())
        self.assertTrue(any("--prune-legacy" in warning for warning in payload["warnings"]))
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write", "--prune-legacy")[0])
        self.assertFalse((self.target / "CLAUDE.md").exists())

    def test_a_legacy_config_is_left_in_place_and_not_shadowed(self):
        self.write(".claude/quenching.json", "{}\n")
        code, payload = self.run_deploy("--modules", "core", "--write")
        self.assertEqual(0, code)
        self.assertFalse((self.target / ".agents/quenching.json").exists())
        self.assertTrue(any("legacy .claude/quenching.json" in warning for warning in payload["warnings"]))

    def test_target_owned_skills_are_audited_while_generated_ones_are_not(self):
        self.write(".agents/skills/my-skill/SKILL.md",
                   "---\ndescription: Mine.\n---\n\nread notes\n")
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        status = json.loads(self.target_cq("components", "status", "--json").stdout)
        self.assertEqual((1, 44), (status["commands"], status["generated"]))
        lint = self.target_cq("components", "lint", "--json")
        self.assertEqual(0, lint.returncode, lint.stderr)

    def test_a_legacy_claude_surface_is_refused(self):
        self.write(".claude/commands/x.md", "---\ndescription: x\n---\n")
        code, payload = self.run_deploy("--modules", "core", "--write")
        self.assertEqual(2, code)
        self.assertEqual("ct-deploy-legacy", payload["code"])
        self.assertFalse((self.target / ".agents/quenching").exists())

    def test_an_upgrade_keeps_the_selection_the_manifest_recorded(self):
        self.assertEqual(0, self.run_deploy("--modules", "all", "--write")[0])
        design = self.target / ".agents/skills/quenching-design-align/SKILL.md"
        self.assertTrue(design.exists())
        code, payload = self.run_deploy("--write")
        self.assertEqual(0, code)
        self.assertEqual([], [change for change in payload["changes"]
                              if change["change"] == "delete"])
        self.assertEqual([], payload["changes"])
        self.assertTrue(design.exists())

    def test_an_explicit_flag_still_narrows_a_recorded_selection(self):
        self.assertEqual(0, self.run_deploy("--modules", "all", "--write")[0])
        code, payload = self.run_deploy("--modules", "core", "--write")
        self.assertEqual(0, code)
        self.assertIn({"path": ".agents/skills/quenching-design-align/SKILL.md",
                       "change": "delete"}, payload["changes"])
        self.assertFalse((self.target / ".agents/skills/quenching-design-align").exists())

    def test_the_opencode_harness_writes_its_subagents(self):
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        agent = self.target / ".opencode/agents/quenching-verifier.md"
        text = agent.read_text(encoding="utf-8")
        self.assertIn("mode: subagent", text)
        self.assertIn('".agents/quenching/bin/cq git audit *": allow', text)
        self.assertIn("Source model tier: `sonnet`.", text)
        self.assertIn("tools:\n  task: false", text)

    def test_a_harness_that_is_not_selected_writes_no_agents(self):
        self.assertEqual(0, self.run_deploy("--modules", "core", "--harness", "claude",
                                            "--write")[0])
        self.assertFalse((self.target / ".opencode/agents").exists())

    def test_uvx_runtime_writes_a_pinned_shim_and_no_vendored_package(self):
        self.assertEqual(0, self.run_deploy("--modules", "specs", "--runtime", "uvx", "--write")[0])
        shim = (self.target / ".agents/quenching/bin/cq").read_text()
        self.assertIn("uvx --from", shim)
        self.assertIn("#subdirectory=plugins/quenching", shim)
        self.assertFalse((self.target / ".agents/quenching/assets/bin/quenching").exists())
        self.assertFalse((self.target / ".agents/quenching/assets/bin/cq").exists())


if __name__ == "__main__":
    unittest.main()
