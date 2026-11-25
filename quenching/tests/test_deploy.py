"""Executable proofs for `cq deploy`: install the surface in an empty target."""
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
    import _paths  # noqa: F401
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.common import access
from quenching.common.deploy import dumps_hash_manifest
from quenching.deploy import translate
from quenching.deploy import cli as deploy_cli
from quenching.deploy import tree as deploy_tree
from quenching.deploy.cli import main as deploy_main

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_ROOT = PLUGIN_ROOT.parent
REAL = PLUGIN_ROOT / "assets" / "bin" / "cq"
VERSION = (PLUGIN_ROOT / "VERSION").read_text().strip()
REAL_PRECOMPILE = deploy_cli._precompile


def launcher(path) -> list[str]:
    """The argv that runs the shebang launcher `bin/cq` itself.

    Windows cannot execute a shebang script (`[WinError 193]`); its door is `cq.cmd`, whose text
    `test_the_windows_launcher_forwards_arguments_and_the_exit_code` proves. There the same
    `bin/cq` runs under this interpreter, as a POSIX shebang would run it.
    """
    return [sys.executable, str(path)] if os.name == "nt" else [str(path)]


class Deploy(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.target = pathlib.Path(tmp.name)
        self.git("init", "-q")
        # The user's global OpenCode config decides whether the depth is written; keep it out.
        self.xdg = pathlib.Path(tempfile.mkdtemp(dir=tmp.name, prefix="xdg-"))
        env = mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.xdg), "OPENCODE_CONFIG": ""})
        env.start()
        self.addCleanup(env.stop)
        # A real `compileall` costs a subprocess per write; the tests that prove it stop this stub.
        self.precompile = mock.patch("quenching.deploy.cli._precompile", return_value=None)
        self.precompile.start()
        self.addCleanup(self.precompile.stop)

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
        path.write_text(text, encoding="utf-8", newline="\n")  # the LF it says, on Windows too

    def test_write_creates_the_generic_layer_without_claude_md(self):
        code, payload = self.run_deploy("--modules", "core", "--write")
        self.assertEqual(0, code)
        self.assertTrue(payload["written"])
        for rel in ("AGENTS.md", ".agents/quenching.json", ".agents/.quenching-deploy.json",
                    ".agents/skills/quenching-specs/SKILL.md",
                    ".agents/quenching/bin/cq", ".claude/skills/quenching-specs/SKILL.md"):
            self.assertTrue((self.target / rel).exists(), rel)
        for rel in ("CLAUDE.md", ".claude/CLAUDE.md", ".claude/commands", ".claude/references"):
            self.assertFalse((self.target / rel).exists(), rel)
        version = self.target_cq("--version")
        self.assertEqual(0, version.returncode, version.stderr)
        status = self.target_cq("components", "status", "--json")
        self.assertEqual(0, status.returncode, status.stderr)
        document = json.loads(status.stdout)
        self.assertEqual((0, 6), (document["commands"], document["generated"]))
        template = (self.target / ".agents/quenching/assets/templates/harness/agents-root.md").read_text()
        self.assertIn("quenching-knowledge-add", template)
        self.assertNotIn("quenching-align:knowledge:add", template)
        check, again = self.run_deploy("--modules", "core", "--check")
        self.assertEqual((0, []), (check, again["changes"]))
        local = self.target_cq("deploy", "--target", ".", "--modules", "core", "--check", "--json")
        self.assertEqual(0, local.returncode, local.stdout + local.stderr)
        self.assertEqual([], json.loads(local.stdout)["changes"])

    def test_every_text_the_deploy_writes_is_lf(self):
        """Seeds, settings and the manifest are written as text: LF on Windows too."""
        self.write(".claude/settings.json", json.dumps({"permissions": {"allow": ["Read"]}}))
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        for rel in ("AGENTS.md", ".agents/quenching.json", ".agents/.quenching-deploy.json",
                    ".claude/settings.json"):
            self.assertNotIn(b"\r\n", (self.target / rel).read_bytes(), rel)

    def test_the_identity_hooks_ship_warn_until_active_and_refuse_an_outside_email(self):
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        for hook in ("pre-commit", "pre-push"):
            path = self.target / ".agents/quenching/assets/githooks" / hook
            self.assertTrue(path.is_file(), hook)
            if os.name != "nt":  # Windows has no execute bit; git for Windows runs a hook without one
                self.assertTrue(path.stat().st_mode & 0o111, hook)
        self.assertEqual([], self.run_deploy("--modules", "core", "--check")[1]["warnings"])
        config = json.loads((self.target / ".agents/quenching.json").read_text(encoding="utf-8"))
        config["shared"]["gitIdentity"] = {"allowedEmails": ["dev@example.org"]}
        self.write(".agents/quenching.json", json.dumps(config))
        warnings = self.run_deploy("--modules", "core", "--check")[1]["warnings"]
        self.assertTrue(any("git config core.hooksPath .agents/quenching/assets/githooks" in w
                            for w in warnings), warnings)
        self.git("config", "core.hooksPath", ".agents/quenching/assets/githooks")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "user.name", "Dev")
        self.assertEqual([], self.run_deploy("--modules", "core", "--check")[1]["warnings"])
        self.git("add", "-A")
        refused = subprocess.run(
            ["git", "-C", str(self.target), "-c", "user.email=someone@corp.example", "commit",
             "-q", "-m", "outside"], capture_output=True, text=True)
        self.assertNotEqual(0, refused.returncode)
        self.assertIn("someone@corp.example", refused.stdout + refused.stderr)
        self.git("-c", "user.email=dev@example.org", "commit", "-q", "-m", "inside")
        self.assertEqual("dev@example.org", self.git("log", "-1", "--format=%ae").strip())

    def test_build_tree_writes_the_copilot_projection_only_when_asked(self):
        names = ("spec-orchestrator", "spec-reviewer", "spec-runner", "spec-scout",
                 "spec-verifier")
        plain = deploy_tree.build_tree(PLUGIN_ROOT, self.target, ["quenching-specs"],
                                       ["claude"])
        self.assertFalse([rel for rel in plain["tree"] if rel.startswith(".github/")])
        projected = deploy_tree.build_tree(PLUGIN_ROOT, self.target, ["quenching-specs"],
                                           ["claude"], projections=["github"])
        for name in names:
            rel = f".github/agents/quenching-{name}.agent.md"
            self.assertIn(rel, projected["tree"])
            text = projected["tree"][rel][0].decode("utf-8")
            self.assertTrue(text.startswith(f"---\nname: quenching-{name}\n"))
            self.assertIn("target: github-copilot", text)
            self.assertIn(rel, projected["manifest"]["files"])
        self.assertNotIn(".github/agents", "".join(plain["manifest"]["files"]))

    def configure_projections(self, value):
        self.write(".agents/quenching.json",
                   json.dumps({"shared": {"projections": value}}, indent=2) + "\n")

    def test_the_copilot_agents_are_written_and_removed_with_the_declaration(self):
        self.configure_projections(["github"])
        self.assertEqual(0, self.run_deploy("--modules", "specs", "--write")[0])
        agents = sorted((self.target / ".github/agents").glob("quenching-*.agent.md"))
        self.assertEqual(5, len(agents), agents)
        text = (self.target / ".github/agents/quenching-spec-verifier.agent.md").read_text()
        self.assertIn("target: github-copilot", text)
        self.assertNotIn("Bash(", text.split("---", 2)[1])
        self.configure_projections([])
        self.assertEqual(0, self.run_deploy("--modules", "specs", "--write")[0])
        self.assertFalse((self.target / ".github/agents").exists())

    def test_an_unknown_projection_is_refused_before_anything_is_written(self):
        self.configure_projections(["copilot"])
        code, payload = self.run_deploy("--modules", "specs", "--write")
        self.assertEqual((2, "ct-deploy-projection"), (code, payload["code"]))
        self.assertIn("copilot", payload["message"])
        self.assertFalse((self.target / ".agents/.quenching-deploy.json").exists())

    def test_a_projection_of_the_wrong_shape_is_refused(self):
        self.configure_projections("github")
        code, payload = self.run_deploy("--modules", "specs", "--write")
        self.assertEqual((2, "ct-deploy-projection"), (code, payload["code"]))
        self.assertFalse((self.target / ".agents/.quenching-deploy.json").exists())

    def test_a_local_skill_and_agent_survive_a_deploy(self):
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        skill = self.target / ".agents/skills/bundle-local/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("---\nname: bundle-local\ndescription: a target's own skill\n---\n\nBody.\n",
                         encoding="utf-8")
        agent = self.target / ".claude/agents/local-agent.md"
        agent.parent.mkdir(parents=True, exist_ok=True)
        agent.write_text("---\nname: local-agent\ndescription: a target's own agent\n---\n\nBody.\n",
                         encoding="utf-8")
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        self.assertTrue(skill.is_file())
        self.assertTrue(agent.is_file())
        check, again = self.run_deploy("--modules", "core", "--check")
        self.assertEqual((0, []), (check, again["changes"]))

    def test_generated_skill_grants_both_launchers_and_names_the_platform(self):
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        skill = (self.target / ".agents/skills/quenching-components/SKILL.md").read_text()
        # The registered server replaces the covered verbs; the residue keeps both launchers.
        self.assertNotIn("Bash(.agents/quenching/bin/cq:*)", skill)
        self.assertIn("Bash(.agents/quenching/bin/cq deploy:*)", skill)
        self.assertIn("Bash(.agents/quenching/bin/cq.cmd deploy:*)", skill)
        self.assertIn("mcp__quenching", skill)
        self.assertIn("on Windows it calls `cq.cmd`", skill)
        self.assertEqual(1, skill.count("**Launcher.**"))
        agent = (self.target / ".agents/quenching/agents/spec-runner.md").read_text()
        self.assertNotIn("**Launcher.**", agent)

    def test_check_reports_drift_without_writing(self):
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        skill = self.target / ".agents/skills/quenching-specs/SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")
        code, payload = self.run_deploy("--modules", "core", "--check")
        self.assertEqual(1, code)
        self.assertIn({"path": ".agents/skills/quenching-specs/SKILL.md",
                       "change": "edited"}, payload["changes"])
        self.assertIn("local edit", skill.read_text(encoding="utf-8"))

    def test_a_write_refuses_to_discard_a_local_edit_until_forced(self):
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        skill = self.target / ".agents/skills/quenching-specs/SKILL.md"
        pristine = skill.read_bytes()
        skill.write_bytes(pristine + b"\nlocal edit\n")
        code, payload = self.run_deploy("--modules", "core", "--write")
        self.assertEqual((2, "ct-deploy-edited"), (code, payload["code"]))
        self.assertEqual([".agents/skills/quenching-specs/SKILL.md"], payload["paths"])
        self.assertIn(b"local edit", skill.read_bytes())
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write", "--force")[0])
        self.assertEqual(pristine, skill.read_bytes())

    def test_an_upstream_change_to_an_unedited_file_is_an_update(self):
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        rel = ".agents/skills/quenching-specs/SKILL.md"
        path = self.target / ".agents/.quenching-deploy.json"
        manifest = json.loads(path.read_text())
        # The recorded bytes and the disk agree, the source moved on: simulate an older deploy.
        old = b"an older release\n"
        (self.target / rel).write_bytes(old)
        import hashlib
        manifest["files"][rel] = hashlib.sha256(old).hexdigest()
        manifest["version"] = "0.0.1"
        path.write_text(json.dumps(manifest, indent=2) + "\n")
        code, payload = self.run_deploy("--modules", "core", "--check")
        self.assertEqual(1, code)
        self.assertIn({"path": rel, "change": "update"}, payload["changes"])
        self.assertEqual("0.0.1", payload["installedVersion"])
        self.assertTrue(any("0.0.1" in w for w in payload["warnings"]))
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])

    def test_a_crlf_checkout_of_the_surface_is_clean_and_a_real_edit_is_still_edited(self):
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        owned = json.loads((self.target / ".agents/.quenching-deploy.json").read_text())["files"]
        converted = []
        for rel in owned:
            path = self.target / rel
            data = path.read_bytes()
            if b"\n" in data and b"\0" not in data:
                path.write_bytes(data.replace(b"\n", b"\r\n"))  # what core.autocrlf checks out
                converted.append(rel)
        self.assertTrue(converted)
        code, payload = self.run_deploy("--modules", "core", "--check")
        self.assertEqual((0, []), (code, payload["changes"]))
        code, payload = self.run_deploy("--modules", "core", "--write")
        self.assertEqual((0, True), (code, payload["written"]))
        self.assertIn(b"\r\n", (self.target / converted[0]).read_bytes())
        skill = self.target / ".agents/skills/quenching-specs/SKILL.md"
        skill.write_bytes(skill.read_bytes() + b"local edit\r\n")
        code, payload = self.run_deploy("--modules", "core", "--check")
        self.assertIn({"path": ".agents/skills/quenching-specs/SKILL.md", "change": "edited"},
                      payload["changes"])

    def test_the_tree_carries_lf_text_and_untouched_binary(self):
        from quenching.deploy.tree import eol_canonical
        self.assertEqual(b"a\nb\n", eol_canonical(b"a\r\nb\r\n"))
        self.assertEqual(b"\x89PNG\r\n\x00\r\n", eol_canonical(b"\x89PNG\r\n\x00\r\n"))
        self.assertEqual(b"\xff\r\n", eol_canonical(b"\xff\r\n"))

    def test_a_symlinked_directory_cannot_carry_a_write_outside_the_target(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        (self.target / ".agents").mkdir()
        link = self.target / ".agents/skills"
        if os.name == "nt":
            # A symlink needs a privilege an ordinary account lacks; a junction carries the same
            # escape, needs none, and `realpath` resolves it too.
            import _winapi
            _winapi.CreateJunction(outside.name, str(link))
        else:
            os.symlink(outside.name, link)
        code, payload = self.run_deploy("--modules", "core", "--write")
        self.assertEqual(2, code)
        self.assertEqual([], os.listdir(outside.name))

    def test_remove_plans_then_deletes_the_owned_surface_and_keeps_edits(self):
        self.write(".claude/settings.json", json.dumps({"permissions": {"allow": ["Read"]}}))
        self.write(".agents/skills/my-skill/SKILL.md", "---\ndescription: Mine.\n---\n\nBody.\n")
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        edited = self.target / ".agents/skills/quenching-git/SKILL.md"
        edited.write_text("mine now\n", encoding="utf-8")
        code, payload = self.run_deploy("--remove")
        self.assertEqual(1, code)
        self.assertFalse(payload["written"])
        self.assertTrue((self.target / ".agents/quenching/bin/cq").exists())
        self.assertIn(".agents/skills/quenching-git/SKILL.md", payload["kept"])
        code, payload = self.run_deploy("--remove", "--write")
        self.assertEqual(0, code)
        self.assertFalse((self.target / ".agents/quenching").exists())
        self.assertFalse((self.target / ".agents/.quenching-deploy.json").exists())
        self.assertFalse((self.target / ".agents/skills/quenching-specs").exists())
        self.assertEqual("mine now\n", edited.read_text(encoding="utf-8"))
        for rel in ("AGENTS.md", ".agents/quenching.json", ".agents/skills/my-skill/SKILL.md"):
            self.assertTrue((self.target / rel).exists(), rel)
        settings = json.loads((self.target / ".claude/settings.json").read_text())
        self.assertEqual({"permissions": {"allow": ["Read"]}}, settings)

    def pycs(self) -> set[str]:
        root = self.target / ".agents/quenching"
        return {p.relative_to(root).as_posix() for p in root.rglob("*.pyc")}

    def test_a_write_precompiles_the_payload_so_a_first_call_writes_no_bytecode(self):
        self.precompile.stop()
        code, payload = self.run_deploy("--modules", "core", "--write")
        self.assertEqual(0, code)
        self.assertEqual([], [w for w in payload["warnings"] if "bytecode" in w])
        compiled = self.pycs()
        self.assertTrue(any(p.startswith("assets/bin/quenching/common/__pycache__/") for p in compiled))
        self.assertTrue(any(p.startswith("assets/hooks/") for p in compiled), compiled)
        status = self.target_cq("components", "status", "--json")
        self.assertEqual(0, status.returncode, status.stderr)
        self.assertEqual(compiled, self.pycs())
        manifest = (self.target / ".agents/.quenching-deploy.json").read_text(encoding="utf-8")
        self.assertNotIn("__pycache__", manifest)
        self.assertEqual((0, []), (lambda r: (r[0], r[1]["changes"]))(
            self.run_deploy("--modules", "core", "--check")))

    def test_a_precompile_that_cannot_run_is_a_warning_not_a_refusal(self):
        self.precompile.stop()
        with mock.patch.object(deploy_cli, "_precompile", side_effect=lambda target, _python:
                               REAL_PRECOMPILE(target, [str(self.target / "no-such-python")])):
            code, payload = self.run_deploy("--modules", "core", "--write")
        self.assertEqual(0, code)
        self.assertTrue(payload["written"])
        self.assertTrue(any("bytecode was not precompiled" in w for w in payload["warnings"]),
                        payload["warnings"])

    def test_remove_takes_the_bytecode_of_every_removed_module_with_it(self):
        self.precompile.stop()
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        self.assertTrue(self.pycs())
        self.assertEqual(0, self.run_deploy("--remove", "--write")[0])
        self.assertFalse((self.target / ".agents/quenching").exists())

    def test_remove_refuses_a_target_that_was_never_deployed(self):
        code, payload = self.run_deploy("--remove", "--write")
        self.assertEqual((2, "ct-deploy-remove"), (code, payload["code"]))

    def test_a_group_writable_surface_is_not_drift(self):
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        skill = self.target / ".agents/skills/quenching-specs/SKILL.md"
        skill.chmod(0o664)
        code, payload = self.run_deploy("--modules", "core", "--check")
        self.assertEqual((0, []), (code, payload["changes"]))

    @unittest.skipIf(os.name == "nt", "Windows derives the executable bit from the extension")
    def test_a_non_executable_cq_is_still_drift(self):
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        (self.target / ".agents/quenching/bin/cq").chmod(0o644)
        code, payload = self.run_deploy("--modules", "core", "--check")
        self.assertEqual(1, code)
        self.assertIn({"path": ".agents/quenching/bin/cq", "change": "mode"}, payload["changes"])

    def test_an_unowned_generated_skill_refuses_and_writes_nothing(self):
        self.write(".agents/skills/quenching-specs/SKILL.md",
                   "---\ndescription: mine\n---\nkeep me\n")
        code, payload = self.run_deploy("--modules", "core", "--write")
        self.assertEqual(2, code)
        self.assertEqual(".agents/skills/quenching-specs/SKILL.md", payload["conflicts"][0]["path"])
        self.assertFalse((self.target / ".agents/quenching").exists())
        self.assertIn("keep me", (self.target / ".agents/skills/quenching-specs/SKILL.md").read_text())

    def drop_from_manifest(self, rel: str):
        path = self.target / ".agents/.quenching-deploy.json"
        manifest = json.loads(path.read_text())
        del manifest["files"][rel]
        path.write_text(json.dumps(manifest, indent=2) + "\n")

    def test_an_unowned_bridge_copy_with_the_generated_bytes_is_adopted(self):
        self.write(".agents/skills/my-skill/SKILL.md", "---\ndescription: Mine.\n---\n\nBody.\n")
        self.assertEqual(0, self.run_deploy("--modules", "specs", "--write")[0])
        bridge = self.target / ".claude/skills/my-skill/SKILL.md"
        before = bridge.read_bytes()
        self.drop_from_manifest(".claude/skills/my-skill/SKILL.md")
        code, payload = self.run_deploy("--modules", "specs", "--check")
        self.assertEqual(1, code)
        self.assertIn({"path": ".claude/skills/my-skill/SKILL.md", "change": "adopt"},
                      payload["changes"])
        self.assertEqual([], payload["conflicts"])
        self.assertEqual(0, self.run_deploy("--modules", "specs", "--write")[0])
        self.assertEqual(before, bridge.read_bytes())
        manifest = json.loads((self.target / ".agents/.quenching-deploy.json").read_text())
        self.assertIn(".claude/skills/my-skill/SKILL.md", manifest["files"])
        code, payload = self.run_deploy("--modules", "specs", "--check")
        self.assertEqual((0, []), (code, payload["changes"]))

    def test_an_unowned_bridge_copy_that_differs_still_refuses(self):
        self.write(".agents/skills/my-skill/SKILL.md", "---\ndescription: Mine.\n---\n\nBody.\n")
        self.assertEqual(0, self.run_deploy("--modules", "specs", "--write")[0])
        self.drop_from_manifest(".claude/skills/my-skill/SKILL.md")
        self.write(".claude/skills/my-skill/SKILL.md", "edited by hand\n")
        code, payload = self.run_deploy("--modules", "specs", "--write")
        self.assertEqual(2, code)
        self.assertEqual("ct-deploy-unowned", payload["code"])
        self.assertEqual("edited by hand\n",
                         (self.target / ".claude/skills/my-skill/SKILL.md").read_text())

    def test_module_selection_limits_skills_and_enabled_pillars(self):
        self.assertEqual(0, self.run_deploy("--modules", "specs", "--write")[0])
        self.assertTrue((self.target / ".agents/skills/quenching-specs/SKILL.md").exists())
        self.assertFalse((self.target / ".agents/skills/quenching-knowledge").exists())
        modules = json.loads(self.target_cq("modules", "--json").stdout)
        enabled = {row["name"]: row["enabled"] for row in modules["modules"]}
        self.assertTrue(enabled["quenching-specs"])
        self.assertFalse(enabled["quenching-knowledge"])
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
        self.assertEqual((1, 6), (status["commands"], status["generated"]))
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
        design = self.target / ".agents/skills/quenching-design/SKILL.md"
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
        self.assertIn({"path": ".agents/skills/quenching-design/SKILL.md",
                       "change": "delete"}, payload["changes"])
        self.assertFalse((self.target / ".agents/skills/quenching-design").exists())

    def test_narrowing_the_modules_leaves_no_orphan_bridge_skill_in_one_write(self):
        self.assertEqual(0, self.run_deploy("--modules", "all", "--harness", "claude",
                                            "--write")[0])
        self.write(".agents/skills/quenching-design/notes.md", "kept by the target\n")
        code, _payload = self.run_deploy("--modules", "core", "--write")
        self.assertEqual(0, code)
        self.assertFalse((self.target / ".claude/skills/quenching-design/SKILL.md").exists())
        self.assertTrue((self.target / ".claude/skills/quenching-design/notes.md").exists())
        bridge = json.loads((self.target / ".claude/skills/.generated-files.json").read_text())
        self.assertNotIn("quenching-design/SKILL.md", bridge["files"])
        code, payload = self.run_deploy("--check")
        self.assertEqual(0, code)
        self.assertEqual([], payload["changes"])

    def test_a_tracked_mirror_outside_the_selection_is_checked_against_the_source(self):
        """A module the selection left out but whose mirror the target tracks cannot age quietly."""
        self.assertEqual(0, self.run_deploy("--modules", "core", "--harness", "claude",
                                            "--write")[0])
        stale = {".agents/skills/quenching-design/SKILL.md": "stale skill\n",
                 ".agents/quenching/assets/bin/quenching/design/align.py": "# stale\n"}
        for rel, text in stale.items():
            self.write(rel, text)
        code, payload = self.run_deploy("--check")
        self.assertEqual(1, code)
        self.assertEqual(stale.keys(), {c["path"] for c in payload["changes"]
                                        if c["path"] in stale and c["change"] == "update"})
        self.assertEqual([], payload["conflicts"])
        self.assertEqual(0, self.run_deploy("--write")[0])
        for rel in stale:
            self.assertNotEqual(stale[rel], (self.target / rel).read_text(encoding="utf-8"), rel)
        code, payload = self.run_deploy("--check")
        self.assertEqual((0, []), (code, payload["changes"]))
        # The module stays outside the selection: nothing else of it appeared.
        self.assertFalse((self.target / ".agents/skills/quenching-ops").exists())

    def test_modules_all_expands_in_registry_order_under_any_hash_seed(self):
        # Hash randomization is fixed at interpreter start, so each seed needs its own child.
        probe = ("import json; from quenching.deploy import tree; "
                 "print(json.dumps(tree.normalize_modules(['all'], "
                 "tree.load_modules(tree.source_root()))))")
        orders = []
        for seed in ("1", "2"):
            run = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True,
                                 cwd=PLUGIN_ROOT / "assets" / "bin",
                                 env={**os.environ, "PYTHONHASHSEED": seed})
            self.assertEqual(0, run.returncode, run.stderr)
            orders.append(json.loads(run.stdout))
        registry = json.loads((PLUGIN_ROOT / "assets/modules.json").read_text())["modules"]
        self.assertEqual([module["name"] for module in registry if "owned" in module], orders[0])
        self.assertEqual(orders[0], orders[1])

    def test_the_opencode_harness_writes_its_subagents(self):
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        agent = self.target / ".opencode/agents/quenching-spec-verifier.md"
        text = agent.read_text(encoding="utf-8")
        self.assertIn("mode: subagent", text)
        self.assertIn("  quenching_git_audit: allow", text)
        self.assertNotIn('".agents/quenching/bin/cq git audit *": allow', text)
        self.assertIn("Source model tier: `sonnet`.", text)
        self.assertIn("tools:\n  task: false", text)

    def test_the_opencode_orchestrator_may_launch_only_the_agents_its_source_names(self):
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        text = (self.target / ".opencode/agents/quenching-spec-orchestrator.md").read_text(
            encoding="utf-8")
        self.assertIn('  task:\n    "*": deny\n'
                      '    "quenching-spec-runner": allow\n'
                      '    "quenching-spec-verifier": allow\n'
                      '    "quenching-spec-scout": allow\n', text)
        self.assertNotIn("tools:\n  task: false", text)

    def test_a_harness_that_is_not_selected_writes_no_agents(self):
        self.assertEqual(0, self.run_deploy("--modules", "core", "--harness", "claude",
                                            "--write")[0])
        self.assertFalse((self.target / ".opencode/agents").exists())

    def test_uvx_runtime_writes_a_pinned_shim_and_no_vendored_package(self):
        self.assertEqual(0, self.run_deploy("--modules", "specs", "--runtime", "uvx", "--write")[0])
        shim = (self.target / ".agents/quenching/bin/cq").read_text()
        self.assertIn("uvx --from", shim)
        self.assertIn("#subdirectory=quenching", shim)
        self.assertFalse((self.target / ".agents/quenching/assets/bin/quenching").exists())
        self.assertFalse((self.target / ".agents/quenching/assets/bin/cq").exists())

    def configure(self, document: dict):
        self.write(".agents/quenching.json", json.dumps(document, indent=2) + "\n")

    PY = ["/opt/py/bin/python3"]
    UV = ["uv", "run", "--no-project", "python"]

    def mcp_config(self, command=None, mount=None):
        option = {"command": command or self.PY}
        if mount is not None:
            option["mount"] = mount
        return {"shared": {"mcp": option}}

    def test_the_mcp_option_generates_one_file_per_harness(self):
        self.configure(self.mcp_config())
        code, payload = self.run_deploy("--modules", "specs", "--write")
        self.assertEqual(0, code, payload)
        claude = json.loads((self.target / ".mcp.json").read_text())
        self.assertEqual({"command": "/opt/py/bin/python3",
                          "args": [".agents/quenching/assets/bin/cq", "mcp"]},
                         claude["mcpServers"]["quenching"])
        self.assertFalse((self.target / ".codex/config.toml").exists())
        opencode = json.loads((self.target / "opencode.json").read_text())
        self.assertEqual(["/opt/py/bin/python3", ".agents/quenching/assets/bin/cq", "mcp"],
                         opencode["mcp"]["quenching"]["command"])
        self.assertTrue(opencode["mcp"]["quenching"]["enabled"])
        for rel in (".mcp.json", "opencode.json"):
            self.assertIn(rel, [c["path"] for c in payload["changes"]])
        manifest = json.loads((self.target / ".agents/.quenching-deploy.json").read_text())
        self.assertEqual({"mount": "all", "command": self.PY}, manifest["mcp"])
        self.assertEqual([], self.run_deploy("--check")[1]["changes"])

    def test_the_cli_fallback_keeps_both_doors(self):
        self.configure({"shared": {"mcp": {"cliFallback": True}}})
        code, payload = self.run_deploy("--modules", "core", "--write")
        self.assertEqual(0, code, payload)
        skill = (self.target / ".agents/skills/quenching-components/SKILL.md").read_text()
        self.assertIn("Bash(.agents/quenching/bin/cq:*)", skill)
        self.assertIn("Bash(.agents/quenching/bin/cq.cmd:*)", skill)
        self.assertIn("mcp__quenching", skill)
        opencode = (self.target / ".opencode/agents/quenching-spec-verifier.md").read_text()
        self.assertIn('".agents/quenching/bin/cq git audit *": allow', opencode)
        claude = (self.target / ".claude/agents/quenching-spec-verifier.md").read_text()
        self.assertIn("Bash(.agents/quenching/bin/cq git audit:*)", claude)
        manifest = json.loads((self.target / ".agents/.quenching-deploy.json").read_text())
        self.assertTrue(manifest["mcp"]["cliFallback"])
        self.assertEqual([], self.run_deploy("--check")[1]["changes"])

    def test_the_narrow_default_reaches_every_harness_but_the_payload(self):
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        claude = (self.target / ".claude/agents/quenching-spec-verifier.md").read_text()
        tools = next(line for line in claude.splitlines() if line.startswith("tools:"))
        self.assertNotIn("bin/cq", tools)
        self.assertIn("mcp__quenching__specs_status", tools)
        payload = (self.target / ".agents/quenching/agents/spec-verifier.md").read_text()
        self.assertIn("Bash(.agents/quenching/bin/cq specs status:*)", payload)
        manifest = json.loads((self.target / ".agents/.quenching-deploy.json").read_text())
        self.assertNotIn("cliFallback", manifest["mcp"])
        for rel in (".agents/skills", ".claude/agents", ".opencode/agents"):
            for path in (self.target / rel).rglob("*.md"):
                head = path.read_text(encoding="utf-8").split("\n---\n", 1)[0]
                self.assertNotIn("claim take", head, path)
        self.assertEqual([], self.run_deploy("--check")[1]["changes"])

    def test_the_specs_mount_keeps_both_doors(self):
        self.configure(self.mcp_config(mount="specs"))
        self.assertEqual(0, self.run_deploy("--modules", "core", "--write")[0])
        skill = (self.target / ".agents/skills/quenching-components/SKILL.md").read_text()
        self.assertIn("Bash(.agents/quenching/bin/cq:*)", skill)

    def test_the_specs_mount_stays_a_declared_option(self):
        self.configure(self.mcp_config(mount="specs"))
        code, payload = self.run_deploy("--modules", "specs", "--write")
        self.assertEqual(0, code, payload)
        server = json.loads((self.target / ".mcp.json").read_text())["mcpServers"]["quenching"]
        self.assertEqual([".agents/quenching/assets/bin/cq", "specs", "mcp"], server["args"])
        self.configure(self.mcp_config(mount="all"))
        self.assertEqual(0, self.run_deploy("--modules", "specs", "--write")[0])
        server = json.loads((self.target / ".mcp.json").read_text())["mcpServers"]["quenching"]
        self.assertEqual([".agents/quenching/assets/bin/cq", "mcp"], server["args"])
        self.assertEqual([], self.run_deploy("--check")[1]["changes"])

    def test_a_uv_prefix_reaches_neither_the_mcp_nor_the_hooks(self):
        self.configure(self.mcp_config(command=self.UV))
        code, payload = self.run_deploy("--modules", "core", "--write")
        self.assertEqual(0, code, payload)
        server = json.loads((self.target / ".mcp.json").read_text())["mcpServers"]["quenching"]
        self.assertNotIn(server["command"], ("uv", "uvx"))
        self.assertNotIn("run", server["args"])
        own = [c for c in self.hook_commands() if ".agents/quenching/assets/hooks/" in c]
        self.assertEqual(1, len(own))
        self.assertFalse(own[0].startswith("uv"), own[0])
        self.assertIn(" -I -c ", own[0])
        warning = [w for w in payload["warnings"] if "runs through uv" in w]
        self.assertTrue(warning, payload["warnings"])
        self.assertIn("the hooks and the MCP server run", warning[0])
        manifest = json.loads((self.target / ".agents/.quenching-deploy.json").read_text())
        self.assertEqual(own[0].split(" -I -c ")[0].split(" "), manifest["claudeSettings"]["command"])
        self.assertEqual(manifest["claudeSettings"]["command"], manifest["mcp"]["command"])
        self.assertEqual([server["command"], *server["args"][:-2]], manifest["mcp"]["command"])
        self.assertEqual((0, []), (self.run_deploy("--check")[0], self.run_deploy("--check")[1]["changes"]))

    def test_a_uv_prefix_warns_without_the_claude_harness(self):
        self.configure(self.mcp_config(command=self.UV))
        code, payload = self.run_deploy("--modules", "specs", "--harness", "opencode", "--write")
        self.assertEqual(0, code, payload)
        command = json.loads((self.target / "opencode.json").read_text())["mcp"]["quenching"]["command"]
        self.assertNotIn(command[0], ("uv", "uvx"))
        self.assertTrue(any("runs through uv" in w for w in payload["warnings"]), payload["warnings"])

    def test_without_the_option_the_whole_server_is_registered_anyway(self):
        self.configure({"shared": {"profiles": {"installed": ["specs"]}}})
        code, payload = self.run_deploy("--modules", "specs", "--write")
        self.assertEqual(0, code, payload)
        server = json.loads((self.target / ".mcp.json").read_text())["mcpServers"]["quenching"]
        self.assertEqual([".agents/quenching/assets/bin/cq", "mcp"], server["args"][-2:])
        self.assertFalse((self.target / ".codex/config.toml").exists())
        self.assertTrue((self.target / "opencode.json").exists())
        manifest = json.loads((self.target / ".agents/.quenching-deploy.json").read_text())
        self.assertEqual("all", manifest["mcp"]["mount"])
        self.assertEqual([".mcp.json", "opencode.json"], sorted(manifest["mcpFiles"]))
        self.assertEqual([], self.run_deploy("--check")[1]["changes"])

    def test_turning_the_option_off_keeps_the_recorded_prefix(self):
        self.configure(self.mcp_config())
        self.assertEqual(0, self.run_deploy("--modules", "specs", "--write")[0])
        self.configure({"shared": {"profiles": {"installed": ["specs"]}}})
        code, payload = self.run_deploy("--modules", "specs", "--write")
        self.assertEqual(0, code, payload)
        server = json.loads((self.target / ".mcp.json").read_text())["mcpServers"]["quenching"]
        self.assertEqual("/opt/py/bin/python3", server["command"])

    def test_a_hand_written_mcp_file_keeps_its_own_entries(self):
        self.configure(self.mcp_config())
        self.write(".mcp.json", '{"mcpServers": {"mine": {"command": "x"}}}\n')
        self.write("opencode.json", '{"theme": "dark", "mcp": {"mine": {"type": "local"}}}\n')
        code, payload = self.run_deploy("--modules", "specs", "--write")
        self.assertEqual(0, code, payload)
        servers = json.loads((self.target / ".mcp.json").read_text())["mcpServers"]
        self.assertEqual({"command": "x"}, servers["mine"])
        self.assertIn("quenching", servers)
        opencode = json.loads((self.target / "opencode.json").read_text())
        self.assertEqual("dark", opencode["theme"])
        self.assertEqual({"type": "local"}, opencode["mcp"]["mine"])
        self.assertIn("quenching", opencode["mcp"])
        self.assertEqual([], self.run_deploy("--check")[1]["changes"])

    def test_an_entry_a_codex_deploy_wrote_is_taken_out_and_the_users_stays(self):
        self.configure(self.mcp_config())
        self.assertEqual(0, self.run_deploy("--modules", "specs", "--write")[0])
        self.write(".codex/config.toml", 'model = "o3"\n\n[mcp_servers.mine]\ncommand = "x"\n\n'
                   '[mcp_servers.quenching]\ncommand = "uv"\nargs = ["a"]\n')
        path = self.target / ".agents/.quenching-deploy.json"
        manifest = json.loads(path.read_text())
        manifest["harnesses"] = ["claude", "codex", "opencode"]
        manifest["mcpFiles"] = [".codex/config.toml", ".mcp.json", "opencode.json"]
        path.write_text(json.dumps(manifest))
        code, payload = self.run_deploy("--modules", "specs", "--write")
        self.assertEqual(0, code, payload)
        codex = (self.target / ".codex/config.toml").read_text()
        self.assertIn('model = "o3"', codex)
        self.assertIn('[mcp_servers.mine]\ncommand = "x"', codex)
        self.assertNotIn("[mcp_servers.quenching]", codex)
        self.assertEqual(["claude", "opencode"],
                         json.loads(path.read_text())["harnesses"])

    def test_remove_takes_out_only_the_quenching_entry(self):
        self.write(".mcp.json", '{"mcpServers": {"mine": {"command": "x"}}}\n')
        self.assertEqual(0, self.run_deploy("--modules", "specs", "--write")[0])
        self.assertEqual(0, self.run_deploy("--remove", "--write")[0])
        self.assertEqual({"mcpServers": {"mine": {"command": "x"}}},
                         json.loads((self.target / ".mcp.json").read_text()))
        self.assertFalse((self.target / ".codex/config.toml").exists())
        self.assertFalse((self.target / "opencode.json").exists())

    def test_a_file_that_is_not_json_is_left_alone_with_a_warning(self):
        self.write("opencode.json", '{ // comment\n  "theme": "dark"\n}\n')
        code, payload = self.run_deploy("--modules", "specs", "--write")
        self.assertEqual(0, code, payload)
        self.assertEqual('{ // comment\n  "theme": "dark"\n}\n',
                         (self.target / "opencode.json").read_text())
        self.assertTrue(any("opencode.json" in w for w in payload["warnings"]))

    def test_a_uvx_runtime_without_the_option_registers_nothing_and_warns(self):
        code, payload = self.run_deploy("--modules", "specs", "--runtime", "uvx", "--write")
        self.assertEqual(0, code, payload)
        for rel in (".mcp.json", "opencode.json"):
            self.assertFalse((self.target / rel).exists(), rel)
        self.assertTrue(any("MCP" in w for w in payload["warnings"]))

    def test_opencode_gets_the_depth_and_the_sibling_allows(self):
        code, payload = self.run_deploy("--modules", "specs", "--harness", "opencode", "--write")
        self.assertEqual(0, code, payload)
        opencode = json.loads((self.target / "opencode.json").read_text())
        self.assertEqual(4, opencode["experimental"]["subagent_depth"])
        primary = os.path.realpath(self.target).replace(os.sep, "/")
        home = os.path.expanduser("~").replace(os.sep, "/")
        wanted = [f"{os.path.dirname(primary)}/{os.path.basename(primary)}-slot-*", f"{primary}.*"]
        wanted = ["~" + p[len(home):] if p.startswith(home + "/") else p for p in wanted]
        self.assertEqual({p: "allow" for p in wanted}, opencode["permission"]["external_directory"])
        self.assertEqual({p: "allow" for p in access.OPENCODE_BASH},
                         opencode["permission"]["bash"])
        manifest = json.loads((self.target / ".agents/.quenching-deploy.json").read_text())
        self.assertEqual({"subagentDepth": 4, "externalDirectory": wanted,
                          "bash": list(access.OPENCODE_BASH)}, manifest["opencodeConfig"])
        self.assertEqual([], self.run_deploy("--check")[1]["changes"])

    def test_check_keeps_the_patterns_another_machine_recorded(self):
        self.assertEqual(0, self.run_deploy("--modules", "specs", "--harness", "opencode",
                                            "--write")[0])
        other = ["~/elsewhere/repo-slot-*", "~/elsewhere/repo.*"]
        manifest_path = self.target / ".agents/.quenching-deploy.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["opencodeConfig"]["externalDirectory"] = other
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        opencode = json.loads((self.target / "opencode.json").read_text())
        opencode["permission"]["external_directory"] = {p: "allow" for p in other}
        (self.target / "opencode.json").write_text(json.dumps(opencode, indent=2) + "\n",
                                                   encoding="utf-8")
        self.assertEqual([], self.run_deploy("--check")[1]["changes"])
        self.assertEqual(0, self.run_deploy("--write")[0])
        rewritten = json.loads((self.target / "opencode.json").read_text())
        self.assertNotIn(other[0], rewritten["permission"]["external_directory"])

    def test_a_slot_resolves_to_its_primary_checkout(self):
        from quenching.deploy.cli import _primary_checkout
        self.git("-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q",
                 "--allow-empty", "-m", "seed")
        slot = self.target / "slot"
        self.git("worktree", "add", "-q", "--detach", str(slot))
        self.assertEqual(os.path.realpath(self.target), os.path.realpath(_primary_checkout(slot)))

    def test_a_global_experimental_key_keeps_the_depth_out_with_a_warning(self):
        (self.xdg / "opencode").mkdir()
        (self.xdg / "opencode" / "opencode.jsonc").write_text(
            '{\n  // mine\n  "experimental": {"todo": true},\n}\n', encoding="utf-8")
        code, payload = self.run_deploy("--modules", "specs", "--harness", "opencode", "--write")
        self.assertEqual(0, code, payload)
        opencode = json.loads((self.target / "opencode.json").read_text())
        self.assertNotIn("experimental", opencode)
        self.assertIn("external_directory", opencode["permission"])
        self.assertTrue(any("subagent_depth" in w and "todo" in w for w in payload["warnings"]))

    def test_check_keeps_the_depth_a_global_key_kept_out_of_this_machine(self):
        # The recorded depth names the machine that wrote the manifest; re-deriving it under this
        # machine's global config would read a committed `opencode.json` as drift.
        self.assertEqual(0, self.run_deploy("--modules", "specs", "--harness", "opencode",
                                            "--write")[0])
        (self.xdg / "opencode").mkdir()
        (self.xdg / "opencode" / "opencode.jsonc").write_text(
            '{"experimental": {"todo": true}}\n', encoding="utf-8")
        code, payload = self.run_deploy("--check")
        self.assertEqual([], payload["changes"], payload)

    def test_dropping_the_opencode_harness_takes_the_extras_out(self):
        self.write("opencode.json", '{"theme": "dark", "permission": {"edit": "ask"}}\n')
        self.assertEqual(0, self.run_deploy("--modules", "specs", "--harness", "opencode",
                                            "--write")[0])
        self.assertEqual(0, self.run_deploy("--harness", "claude", "--write")[0])
        self.assertEqual({"theme": "dark", "permission": {"edit": "ask"}, "$schema":
                          "https://opencode.ai/config.json"},
                         json.loads((self.target / "opencode.json").read_text()))

    def test_claude_approves_the_registered_server_and_gives_it_back(self):
        self.write(".claude/settings.json", '{"enabledMcpjsonServers": ["mine"]}\n')
        self.assertEqual(0, self.run_deploy("--modules", "specs", "--harness", "claude",
                                            "--write")[0])
        doc = json.loads((self.target / ".claude/settings.json").read_text())
        self.assertEqual(["mine", "quenching"], doc["enabledMcpjsonServers"])
        self.assertEqual([], self.run_deploy("--check")[1]["changes"])
        self.assertEqual(0, self.run_deploy("--remove", "--write")[0])
        self.assertEqual({"enabledMcpjsonServers": ["mine"]},
                         json.loads((self.target / ".claude/settings.json").read_text()))

    def test_the_harness_filter_selects_which_mcp_file_is_written(self):
        self.configure(self.mcp_config())
        self.assertEqual(0, self.run_deploy("--modules", "specs", "--harness", "claude",
                                            "--write")[0])
        self.assertTrue((self.target / ".mcp.json").exists())
        self.assertFalse((self.target / "opencode.json").exists())

    def test_the_option_refuses_a_uvx_runtime_and_an_invalid_shape(self):
        self.configure(self.mcp_config())
        code, payload = self.run_deploy("--runtime", "uvx", "--write")
        self.assertEqual(2, code)
        self.assertEqual("ct-deploy-mcp", payload["code"])
        self.assertFalse((self.target / ".mcp.json").exists())
        for option in ({"shared": {"mcp": {"command": []}}},
                       {"shared": {"mcp": {"command": "uv"}}},
                       {"shared": {"mcp": {"mount": "chat", "command": ["uv"]}}},
                       {"shared": {"mcp": {"command": ["uv"], "extra": True}}},
                       {"shared": {"mcp": {"cliFallback": "yes"}}}):
            self.configure(option)
            code, payload = self.run_deploy("--modules", "specs", "--write")
            self.assertEqual(2, code, option)
            self.assertEqual("ct-deploy-mcp", payload["code"], option)

    def test_the_mcp_file_outside_the_root_is_not_adopted(self):
        parent = self.target
        (parent / ".mcp.json").write_text('{"mcpServers": {"parent": {}}}\n', encoding="utf-8")
        child = parent / "nested"
        child.mkdir()
        self.target = child
        self.configure(self.mcp_config())
        self.assertEqual(0, self.run_deploy("--modules", "specs", "--harness", "claude",
                                            "--write")[0])
        self.assertTrue((child / ".mcp.json").exists())
        self.assertEqual('{"mcpServers": {"parent": {}}}\n',
                         (parent / ".mcp.json").read_text())

    # --- .claude/settings.json: quenching's own hooks, merged into the user's file -----------

    def settings(self):
        return json.loads((self.target / ".claude/settings.json").read_text())

    def hook_commands(self):
        return [h["command"] for g in self.settings().get("hooks", {}).get("PreToolUse", [])
                for h in g["hooks"]]

    def test_write_merges_the_hooks_and_keeps_the_users_entries(self):
        user = {"enabledPlugins": {"context7": True},
                "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "guard.sh"}]}]}}
        self.write(".claude/settings.json", json.dumps(user))
        code, payload = self.run_deploy("--modules", "core", "--write")
        self.assertEqual(0, code)
        self.assertIn("settings", [c["change"] for c in payload["changes"]])
        commands = self.hook_commands()
        self.assertEqual("guard.sh", commands[0])
        own = [c for c in commands if ".agents/quenching/assets/hooks/" in c]
        self.assertEqual(1, len(own))  # one process runs every body of the matcher
        self.assertTrue(own[0].endswith('" deny-claude-coauthor warn-git-add-all'), own[0])
        self.assertEqual({"commit": "", "pr": ""}, self.settings()["attribution"])
        self.assertEqual({"context7": True}, self.settings()["enabledPlugins"])
        for name in ("dispatch", "deny-claude-coauthor", "warn-git-add-all"):
            self.assertTrue((self.target / f".agents/quenching/assets/hooks/{name}.py").is_file(), name)
        manifest = json.loads((self.target / ".agents/.quenching-deploy.json").read_text())
        self.assertEqual(["deny-claude-coauthor", "warn-git-add-all"], sorted(manifest["claudeSettings"]["hooks"]))
        self.assertNotIn(".claude/settings.json", manifest["files"])
        before = (self.target / ".claude/settings.json").read_text()
        code, again = self.run_deploy("--modules", "core", "--write")
        self.assertEqual(0, code)
        self.assertEqual(before, (self.target / ".claude/settings.json").read_text())
        self.assertEqual((0, []), (self.run_deploy("--modules", "core", "--check")[0], again["changes"]))

    def test_check_flags_settings_drift(self):
        self.run_deploy("--modules", "core", "--write")
        path = self.target / ".claude/settings.json"
        document = self.settings()
        document["hooks"] = {}
        path.write_text(json.dumps(document))
        code, payload = self.run_deploy("--modules", "core", "--check")
        self.assertEqual(1, code)
        self.assertEqual(["settings"], [c["change"] for c in payload["changes"]])

    def test_a_narrower_module_set_or_harness_removes_only_the_own_hooks(self):
        self.write(".claude/settings.json", json.dumps({"model": "x"}))
        self.run_deploy("--modules", "specs,git", "--write")
        self.assertEqual(1, len(self.hook_commands()))
        self.assertIn("warn-git-add-all", self.hook_commands()[0])
        self.run_deploy("--modules", "specs", "--write")
        self.assertEqual(1, len(self.hook_commands()))
        self.assertTrue(self.hook_commands()[0].endswith('" deny-claude-coauthor'))
        self.assertFalse((self.target / ".agents/quenching/assets/hooks/warn-git-add-all.py").exists())
        code, _ = self.run_deploy("--modules", "specs", "--harness", "opencode", "--write")
        self.assertEqual(0, code)
        self.assertEqual({"model": "x"}, self.settings())

    def test_a_settings_file_the_deploy_created_is_deleted_when_it_empties(self):
        self.run_deploy("--modules", "core", "--write")
        self.assertTrue((self.target / ".claude/settings.json").is_file())
        self.run_deploy("--modules", "core", "--harness", "opencode", "--write")
        self.assertFalse((self.target / ".claude/settings.json").exists())

    def test_the_removed_codex_harness_is_refused(self):
        code, payload = self.run_deploy("--modules", "core", "--harness", "codex", "--write")
        self.assertEqual(2, code)
        self.assertEqual("ct-deploy-harness", payload["code"])
        self.assertFalse((self.target / ".agents/.quenching-deploy.json").exists())

    def test_an_invalid_settings_file_refuses_with_exit_2_and_writes_nothing(self):
        self.write(".claude/settings.json", "{not json")
        code, payload = self.run_deploy("--modules", "core", "--write")
        self.assertEqual(2, code)
        self.assertFalse((self.target / ".agents/.quenching-deploy.json").exists())
        self.assertEqual("{not json", (self.target / ".claude/settings.json").read_text())

    def test_a_settings_path_that_is_a_directory_refuses_before_any_write(self):
        (self.target / ".claude/settings.json").mkdir(parents=True)
        code, _ = self.run_deploy("--modules", "core", "--write")
        self.assertEqual(2, code)
        self.assertFalse((self.target / ".agents/.quenching-deploy.json").exists())

    def test_the_attribution_warning_survives_an_unchanged_merge(self):
        self.write(".claude/settings.json", json.dumps({"attribution": {"commit": "mine"}}))
        self.run_deploy("--modules", "core", "--write")
        code, payload = self.run_deploy("--modules", "core", "--json")
        self.assertEqual(0, code)
        self.assertIn("attribution.commit", json.dumps(payload.get("warnings", payload)))


class SourceDialect(unittest.TestCase):
    """The source is written in the target dialect; the deploy refuses what is not."""

    def test_plugin_root_marker_is_refused(self):
        with self.assertRaises(ValueError):
            translate.transform_platform("run ${CLAUDE_PLUGIN_ROOT}/x")

    def test_plugin_surface_id_is_refused(self):
        with self.assertRaises(ValueError):
            translate.transform_platform("use /quenching-specs:create")

    def test_target_dialect_passes_unchanged(self):
        text = "use /quenching-specs create and .agents/quenching/bin/cq specs"
        self.assertEqual(text, translate.transform_platform(text))


class McpGrants(unittest.TestCase):
    """Each `Bash(cq …)` grant also grants the `quenching` MCP tools under the same verb prefix."""

    VERIFIER = ("---\ndescription: v\ntools: Read, Bash(cq specs status:*), "
                "Bash(cq git audit:*)\n---\n\nbody\n")
    RUNNER = "---\ndescription: r\ntools: Bash, Read\n---\n\nbody\n"

    def test_a_claude_agent_lists_the_tools_its_cq_grants_cover(self):
        text = translate.agent_document(self.VERIFIER, "spec-verifier")
        tools = next(line for line in text.splitlines() if line.startswith("tools:"))
        for name in ("mcp__quenching__specs_status", "mcp__quenching__specs_epic_progress",
                     "mcp__quenching__git_audit"):
            self.assertIn(name, tools)
        self.assertNotIn("mcp__quenching__specs_record", tools)

    def test_a_full_bash_agent_lists_every_tool_and_a_skill_names_the_server(self):
        tools = next(line for line in translate.agent_document(self.RUNNER, "spec-runner")
                     .splitlines() if line.startswith("tools:"))
        self.assertIn("mcp__quenching__specs_section_write", tools)
        self.assertIn("mcp__quenching__git_commit", tools)
        skill = translate.skill_document(
            "---\ndescription: s\nallowed-tools: Bash(cq:*), Read\n---\n\n# s\n", "s")
        self.assertIn("allowed-tools: Bash(.agents/quenching/bin/cq:*), Read, mcp__quenching\n",
                      skill)

    def test_opencode_denies_the_server_then_allows_the_covered_tools(self):
        text = translate.opencode_agent_document(self.VERIFIER, "spec-verifier")
        deny = text.index('  "quenching_*": deny')
        self.assertGreater(text.index("  quenching_specs_status: allow"), deny)
        self.assertIn("  quenching_git_audit: allow", text)
        self.assertNotIn("quenching_specs_record", text)
        self.assertIn('  "quenching_*": allow',
                      translate.opencode_agent_document(self.RUNNER, "spec-runner"))

    def test_opencode_allows_the_non_cq_shell_grants_the_source_lists(self):
        raw = ("---\ndescription: o\ntools: Bash(cq specs status:*), Bash(git worktree list:*), "
               "Bash(gh pr view:*), Bash(bash scripts/verify_repo.sh:*)\n---\n\nbody\n")
        text = translate.opencode_agent_document(raw, "o")
        ask = text.index('    "*": ask')
        for pattern in ("git worktree list *", "gh pr view *", "bash scripts/verify_repo.sh *"):
            self.assertGreater(text.index(f'    "{pattern}": allow'), ask)
        self.assertNotIn('"git *"', text)

    def test_a_narrow_claude_agent_drops_the_shell_grant_its_tools_replace(self):
        text = translate.agent_document(self.VERIFIER, "spec-verifier", narrow=True)
        tools = next(line for line in text.splitlines() if line.startswith("tools:"))
        self.assertNotIn("Bash(", tools)
        for name in ("mcp__quenching__specs_status", "mcp__quenching__git_audit", "Read"):
            self.assertIn(name, tools)
        self.assertEqual(tools, next(line for line in translate.agent_document(
            self.VERIFIER, "spec-verifier").splitlines() if line.startswith("tools:"))
            .replace("Bash(.agents/quenching/bin/cq specs status:*), ", "")
            .replace("Bash(.agents/quenching/bin/cq git audit:*), ", ""))

    def test_a_narrow_skill_keeps_only_the_residue_on_both_launchers(self):
        skill = translate.skill_document(
            "---\ndescription: s\nallowed-tools: Bash(cq:*), Bash(cq.cmd:*), Bash(git log:*), "
            "Read\n---\n\n# s\n", "s", narrow=True)
        grants = next(line for line in skill.splitlines() if line.startswith("allowed-tools:"))
        self.assertNotIn("Bash(.agents/quenching/bin/cq:*)", grants)
        self.assertNotIn("Bash(.agents/quenching/bin/cq.cmd:*)", grants)
        for launcher in ("cq", "cq.cmd"):
            for verb in ("deploy", "specs serve", "specs sync", "portal"):
                self.assertIn(f"Bash(.agents/quenching/bin/{launcher} {verb}:*)", grants)
            self.assertNotIn(f"Bash(.agents/quenching/bin/{launcher} specs status:*)", grants)
        self.assertNotIn("take", grants)
        for name in ("Bash(git log:*)", "Read", "mcp__quenching"):
            self.assertIn(name, grants)

    def test_a_narrow_scoped_grant_keeps_its_uncovered_verbs(self):
        skill = translate.skill_document(
            "---\ndescription: s\nallowed-tools: Bash(cq git:*), Bash(cq specs bogus:*)\n---\n\n# s\n",
            "s", narrow=True)
        self.assertIn("Bash(.agents/quenching/bin/cq git identity:*)", skill)
        self.assertNotIn("Bash(.agents/quenching/bin/cq git:*)", skill)
        self.assertIn("Bash(.agents/quenching/bin/cq specs bogus:*)", skill)
        self.assertIn("mcp__quenching__git_commit", skill)

    def test_a_narrow_opencode_agent_allows_the_tools_and_not_the_shell(self):
        text = translate.opencode_agent_document(self.VERIFIER, "spec-verifier", narrow=True)
        self.assertIn("  bash: deny", text)
        self.assertNotIn("bin/cq", text)
        self.assertIn("  quenching_specs_status: allow", text)
        self.assertIn("  quenching_git_audit: allow", text)
        raw = ("---\ndescription: o\ntools: Bash(cq specs:*), Bash(gh pr view:*)\n---\n\nbody\n")
        text = translate.opencode_agent_document(raw, "o", narrow=True)
        self.assertIn('    ".agents/quenching/bin/cq specs serve *": allow', text)
        self.assertIn('    "gh pr view *": allow', text)
        self.assertNotIn('".agents/quenching/bin/cq specs *"', text)
        self.assertIn("  quenching_specs_status: allow", text)

    def test_a_narrow_translation_is_identical_the_second_time(self):
        once = translate.agent_document(self.VERIFIER, "spec-verifier", narrow=True)
        self.assertEqual(once, translate.agent_document(once, "spec-verifier", narrow=True))
        raw = "---\ndescription: s\nallowed-tools: Bash(cq:*), Read\n---\n\n# s\n"
        skill = translate.skill_document(raw, "s", narrow=True)
        self.assertEqual(skill, translate.skill_document(skill, "s", narrow=True))

    def test_a_second_translation_is_identical(self):
        once = translate.agent_document(self.VERIFIER, "spec-verifier")
        self.assertEqual(once, translate.agent_document(once, "spec-verifier"))
        skill = translate.skill_document(
            "---\ndescription: s\nallowed-tools: Bash(cq specs handoff:*)\n---\n\n# s\n", "s")
        self.assertIn("mcp__quenching__specs_handoff_write", skill)
        self.assertEqual(skill, translate.skill_document(skill, "s"))


class CopilotAgents(unittest.TestCase):
    """The third projection: the same source as the Copilot custom-agent format, never wider."""

    VERIFIER = ("---\ndescription: v\n"
                "tools: Read, Grep, Glob, Bash(cq specs status:*), Bash(cq git audit:*)\n"
                "model: sonnet\neffort: low\n---\n\nbody\n")
    RUNNER = "---\ndescription: r\ntools: Bash, Read, Skill\nmodel: sonnet\neffort: medium\n---\n\nbody\n"

    def field(self, text: str, key: str) -> str:
        line = next(line for line in text.splitlines() if line.startswith(f"{key}:"))
        return line[len(key) + 1:].strip()

    def test_a_copilot_agent_names_the_documented_aliases_and_the_mcp_tools(self):
        text = translate.copilot_agent_document(self.VERIFIER, "spec-verifier")
        self.assertEqual("quenching-spec-verifier", self.field(text, "name"))
        tools = self.field(text, "tools")
        for alias in ("read", "search"):
            self.assertIn(alias, tools)
        for name in ("quenching/specs_status", "quenching/git_audit"):
            self.assertIn(name, tools)
        for claude in ("Bash(", "Read", "Grep", "Glob", "Skill"):
            self.assertNotIn(claude, tools)
        self.assertEqual("true", self.field(text, "include-custom-instructions"))
        self.assertEqual("github-copilot", self.field(text, "target"))
        self.assertIn("Claude Sonnet 4.6", self.field(text, "model"))
        self.assertEqual("low", self.field(text, "reasoning-effort"))

    def test_the_small_tier_never_enters_the_band(self):
        for text in (translate.copilot_agent_document(self.VERIFIER, "spec-verifier"),
                     translate.copilot_agent_document(self.RUNNER, "spec-runner")):
            self.assertNotIn("haiku", text.lower())

    def test_a_full_bash_grant_names_the_tools_and_never_the_catch_all(self):
        tools = self.field(translate.copilot_agent_document(self.RUNNER, "spec-runner"), "tools")
        self.assertIn("execute", tools)
        self.assertIn("quenching/specs_section_write", tools)
        self.assertIn("quenching/git_commit", tools)
        self.assertNotIn("*", tools)
        self.assertNotIn("Skill", tools)

    def test_a_narrow_agent_drops_the_covered_shell_and_keeps_the_mcp_names(self):
        text = translate.copilot_agent_document(self.VERIFIER, "spec-verifier", narrow=True)
        tools = self.field(text, "tools")
        self.assertNotIn("execute", tools)
        self.assertIn("quenching/specs_status", tools)
        self.assertIn("quenching/git_audit", tools)

    def test_the_mount_keeps_a_tool_out_of_the_projection(self):
        self.assertEqual(["execute"],
                         translate.copilot_tools("Bash(cq specs status:*)",
                                                 mount=frozenset({"git"})))

    def test_the_model_band_refuses_the_small_tier_and_an_unknown_band(self):
        with self.assertRaises(ValueError):
            translate.copilot_agent_document(
                "---\ndescription: x\ntools: Read\nmodel: haiku\n---\n\nb\n", "x")
        with self.assertRaises(ValueError):
            translate.copilot_agent_document(
                "---\ndescription: x\ntools: Read\nmodel: gpt\n---\n\nb\n", "x")

    def test_an_unmapped_tool_head_is_refused_instead_of_dropped(self):
        with self.assertRaises(ValueError):
            translate.copilot_agent_document(
                "---\ndescription: x\ntools: Magic\n---\n\nb\n", "x")

    def test_no_model_band_omits_the_model_field(self):
        text = translate.copilot_agent_document(
            "---\ndescription: x\ntools: Read\n---\n\nb\n", "x")
        self.assertFalse(any(line.startswith("model:") for line in text.splitlines()))


class TargetLauncher(unittest.TestCase):
    """The `bin/cq` of a vendored target is generated by the deploy: the one file whose whole job is
    to be *equivalent* to `assets/bin/cq`, and which nothing else would catch drifting.

    The load-bearing assertion is not "it runs" but that invoking through the launcher and invoking
    the target's `assets/bin/cq` directly produce the same bytes and the same exit code. That is the
    `os.execv` claim, and it goes silently false if anyone rewrites the launcher as an import:
    `assets/bin/cq` reaches its `quenching` package through the `sys.path[0]` Python builds from the
    script's directory, which under any in-process form would be `bin/`."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.roots = {}
        for selection in ("core", "all"):
            target = pathlib.Path(cls.tmp.name) / selection
            target.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=target, check=True)
            subprocess.run([sys.executable, str(REAL), "deploy", "--target", str(target),
                            "--modules", selection, "--harness", "none", "--write"],
                           check=True, capture_output=True)
            cls.roots[selection] = target
        cls.payload = cls.roots["all"] / ".agents/quenching"
        cls.shim = cls.payload / "bin/cq"

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def cq(self, selection, *args):
        return subprocess.run([*launcher(self.roots[selection] / ".agents/quenching/bin/cq"), *args],
                              capture_output=True, text=True)

    def test_it_is_generated_and_executable(self):
        self.assertTrue(self.shim.is_file(), f"the launcher does not resolve: {self.shim}")
        self.assertTrue(os.access(self.shim, os.X_OK), f"the launcher carries no execute bit: {self.shim}")

    def test_the_source_ships_no_launcher_of_its_own(self):
        self.assertFalse((PLUGIN_ROOT / "bin").exists())

    def test_the_windows_launcher_forwards_arguments_and_the_exit_code(self):
        """`cq.cmd` is not runnable here, so its text carries the contract: the real entry point, `%*`, the exit code."""
        source = (self.payload / "bin/cq.cmd").read_text(encoding="utf-8")
        self.assertIn("..\\assets\\bin\\cq", source)
        self.assertIn("py -3", source)
        self.assertIn("%*", source)
        self.assertIn("exit /b %ERRORLEVEL%", source)
        self.assertNotIn("execv", source)

    def test_the_windows_branch_runs_cq_in_the_same_process(self):
        """The `nt` branch holds no second interpreter and, run as if on Windows, answers like the real `cq`."""
        source = self.shim.read_text(encoding="utf-8")
        nt_branch = source.split('if os.name == "nt":')[1].split("os.execv")[0]
        self.assertNotIn("subprocess", source)
        self.assertIn("sys.path.insert(0", nt_branch)
        self.assertIn('["main"](sys.argv[1:])', nt_branch)
        probe = self.payload / "bin/cq_nt_probe"
        probe.write_text(source.replace('os.name == "nt"', "True", 1), encoding="utf-8")
        try:
            for argv in (["--version"], ["nosuch pillar", "a b"]):
                with self.subTest(argv=argv):
                    real = subprocess.run([sys.executable, str(self.payload / "assets/bin/cq"), *argv],
                                          capture_output=True, text=True)
                    nt = subprocess.run([sys.executable, str(probe), *argv], capture_output=True, text=True)
                    self.assertEqual(real.returncode, nt.returncode)
                    self.assertEqual(real.stdout, nt.stdout)
                    self.assertEqual(real.stderr.replace("cq_nt_probe", "cq"), nt.stderr.replace("cq_nt_probe", "cq"))
            self.assertNotEqual(0, nt.returncode)
            self.assertIn("nosuch pillar", nt.stderr)
        finally:
            probe.unlink()

    def test_the_windows_branch_forces_utf8_streams_before_main(self):
        """`runpy.run_path` skips cq's `__main__` block, so the launcher itself must force UTF-8."""
        probe = self.payload / "bin/cq_nt_utf8_probe"
        probe.write_text(self.shim.read_text(encoding="utf-8").replace('os.name == "nt"', "True", 1),
                         encoding="utf-8")
        env = {**os.environ, "PYTHONIOENCODING": "cp1252"}
        env.pop("PYTHONUTF8", None)
        try:
            run = subprocess.run([sys.executable, str(probe), "nosuchā"], capture_output=True, env=env)
        finally:
            probe.unlink()
        self.assertNotEqual(0, run.returncode)
        self.assertIn("nosuchā", run.stderr.decode("utf-8"))

    def test_it_exposes_fourteen_pillars(self):
        run = subprocess.run([sys.executable, str(REAL), "--help"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        choices = next(line.strip() for line in run.stdout.splitlines()
                       if line.strip().startswith("{") and line.strip().endswith("}"))
        pillars = set(choices[1:-1].split(","))
        self.assertEqual(14, len(pillars))
        self.assertEqual({"specs", "knowledge", "design", "components", "ops", "proof", "git",
                          "toolchain", "delivery", "security", "opensource", "portal", "config", "mcp"}, pillars)

    def test_it_answers_the_version_lockstep(self):
        run = subprocess.run([*launcher(self.shim), "--version"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout.strip(), VERSION)

    def test_every_published_version_surface_is_in_lockstep(self):
        """Every published consumer must receive the same version."""
        marketplace = json.loads(
            (REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        marketplace_versions = {item["name"]: item["version"] for item in marketplace["plugins"]}
        self.assertEqual({"quenching-hud", "quenching-vitrine", "quenching-cache"}, set(marketplace_versions))
        self.assertEqual({VERSION}, set(marketplace_versions.values()), marketplace_versions)

    def test_a_deploy_installs_nothing_of_the_marketplace_mods(self):
        """The mods install through the marketplace, never through `cq deploy`."""
        for selection, root in self.roots.items():
            installed = [str(path.relative_to(root)) for path in root.rglob("*") if path.is_file()]
            leaked = [path for path in installed if "claude-vitrine" in path or "claude-hud" in path
                      or "quenching-vitrine" in path or "quenching-hud" in path]
            self.assertEqual([], leaked, selection)

    def test_the_entrypoint_declares_and_checks_the_python_floor_before_package_imports(self):
        source = REAL.read_text(encoding="utf-8")
        self.assertIn("PYTHON_FLOOR = (3, 11)", source)
        self.assertLess(source.index("if not _check_python_floor():"),
                        source.index("from quenching.common.output import"))
        self.assertIn("cq-python-floor:", source)

    def test_each_pillar_uses_the_same_version_grammar(self):
        pillars = ("specs", "knowledge", "design", "components", "ops", "proof", "git",
                   "toolchain", "delivery", "security", "opensource", "portal", "config")
        for pillar in pillars:
            with self.subTest(pillar=pillar):
                run = subprocess.run([*launcher(self.shim), pillar, "--version"],
                                     capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertEqual(run.stdout.strip(), f"cq {pillar} {VERSION}")

    def test_it_is_a_literally_equivalent_invocation(self):
        """Same argv through both doors — same stdout, same exit code. The `os.execv` claim."""
        argv = ["components", "doctor", "--root", str(PLUGIN_ROOT), "--json"]
        through_shim = subprocess.run([*launcher(self.shim), *argv], capture_output=True, text=True)
        direct = subprocess.run([sys.executable, str(self.payload / "assets/bin/cq"), *argv],
                                capture_output=True, text=True)
        self.assertEqual(through_shim.stdout, direct.stdout)
        self.assertEqual(through_shim.returncode, direct.returncode)

    def test_an_argument_with_a_space_arrives_whole(self):
        """`os.execv` on Windows joins argv unquoted: `"dois termos"` arrived as two arguments."""
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "bin").mkdir()
            (root / "assets/bin").mkdir(parents=True)
            launcher = root / "bin/cq"
            launcher.write_bytes(self.shim.read_bytes())
            (root / "assets/bin/cq").write_text(
                "import json, sys\nprint(json.dumps(sys.argv[1:]))\nsys.exit(3)\n", encoding="utf-8")
            run = subprocess.run([sys.executable, str(launcher), "dois termos", "x"],
                                 capture_output=True, text=True)
        self.assertEqual(3, run.returncode, run.stderr)
        self.assertEqual(["dois termos", "x"], json.loads(run.stdout))

    def test_a_refusal_arrives_as_exit_2(self):
        """Every command body branches on 0/1/2. A launcher that normalised one would break all of them."""
        run = subprocess.run([*launcher(self.shim), "knowledge", "--root", "."], capture_output=True, text=True)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)

    def test_argparse_misuse_arrives_as_the_distinct_usage_exit(self):
        run = subprocess.run([*launcher(self.shim), "knowledge", "--root", ".", "validate", "--bogus"],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 3, run.stdout + run.stderr)
        self.assertIn("usage: cq knowledge validate", run.stderr)

    def test_a_core_target_refuses_an_undeployed_front_by_its_module(self):
        run = self.cq("core", "design", "--help")
        self.assertEqual(2, run.returncode, run.stdout)
        self.assertIn("quenching-design, which is not enabled", run.stderr)
        self.assertIn("cq deploy --modules", run.stderr)
        self.assertIn("(module quenching-design is not enabled)", self.cq("core", "--help").stdout)
        rows = {row["name"]: row["enabled"]
                for row in json.loads(self.cq("core", "modules", "--json").stdout)["modules"]}
        self.assertTrue(rows["quenching-specs"])
        self.assertFalse(rows["quenching-design"])

    def test_a_target_with_every_module_reaches_every_front(self):
        self.assertEqual(0, self.cq("all", "design", "--help").returncode)
        rows = json.loads(self.cq("all", "modules", "--json").stdout)["modules"]
        self.assertTrue(all(row["enabled"] for row in rows), rows)


class HashManifestMerge(unittest.TestCase):
    """Two specs that regenerate neighbouring hash entries must merge without a conflict."""

    @staticmethod
    def manifest(hashes: dict[str, str], separated: bool) -> str:
        document = {"generator": "cq deploy", "version": "1", "files": hashes}
        return dumps_hash_manifest(document) if separated else json.dumps(document, indent=2) + "\n"

    def merge(self, separated: bool) -> subprocess.CompletedProcess:
        base = {"a/one": "1", "a/two": "2", "a/three": "3", "a/four": "4"}
        ours, theirs = {**base, "a/two": "22"}, {**base, "a/three": "33"}
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for name, hashes in (("ours", ours), ("base", base), ("theirs", theirs)):
                path = pathlib.Path(tmp) / name
                path.write_text(self.manifest(hashes, separated), encoding="utf-8", newline="\n")
                paths.append(str(path))
            return subprocess.run(["git", "merge-file", "-p", *paths], capture_output=True, text=True)

    def test_neighbouring_entries_merge_clean_with_the_separator_and_conflict_without(self):
        self.assertEqual(1, self.merge(separated=False).returncode)
        merged = self.merge(separated=True)
        self.assertEqual(0, merged.returncode, merged.stdout)
        self.assertEqual({"a/one": "1", "a/two": "22", "a/three": "33", "a/four": "4"},
                         json.loads(merged.stdout)["files"])

    def test_the_separator_changes_no_value_a_reader_sees(self):
        hashes = {"a/one": "1", "a/two": "2"}
        self.assertEqual(json.loads(self.manifest(hashes, False)), json.loads(self.manifest(hashes, True)))


if __name__ == "__main__":
    unittest.main()
