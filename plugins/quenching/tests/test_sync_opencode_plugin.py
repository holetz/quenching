"""The OpenCode distribution generator: layout, deny-only permissions, and drift detection."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("sync_opencode_plugin", REPO / "scripts/sync_opencode_plugin.py")
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class GeneratedTree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = sync.generated_tree()

    def text(self, rel):
        return self.tree[rel].decode("utf-8")

    def test_one_command_per_source_command_and_one_subagent_per_agent(self):
        commands = sorted(r for r in self.tree if r.startswith("commands/"))
        self.assertEqual(len(list((sync.SOURCE / "commands").rglob("*.md"))), len(commands))
        self.assertIn("commands/quenching-specs-develop.md", commands)
        self.assertEqual({f"agents/quenching-{n}.md" for n in sync.agent_names()},
                         {r for r in self.tree if r.startswith("agents/")})

    def test_the_tree_validates_clean(self):
        self.assertEqual([], sync.validate(self.tree))

    def test_no_claude_or_codex_resolution_survives_in_commands_or_agents(self):
        for rel in (r for r in self.tree if r.startswith(("commands/", "agents/"))):
            text = self.text(rel)
            for marker in ("CLAUDE_PLUGIN_ROOT", "codex plugin list", "../../references/", "/quenching-specs:"):
                self.assertNotIn(marker, text, rel)

    def test_cq_bash_blocks_define_the_opencode_wrapper(self):
        text = self.text("commands/quenching-specs-status.md") + self.text("agents/quenching-verifier.md")
        self.assertIn(sync.OPENCODE_CQ_WRAPPER, text)

    def test_tool_resolution_reference_is_rewritten_for_opencode(self):
        text = self.text("quenching/references/align/tool-resolution.md")
        self.assertIn("OpenCode does **not** require `cq`", text)
        self.assertNotIn("codex plugin list", text)

    def test_read_only_agent_is_never_wider_than_its_source(self):
        header = self.text("agents/quenching-verifier.md").split("\n---\n", 1)[0]
        self.assertIn("mode: subagent", header)
        self.assertIn("edit: deny", header)
        self.assertIn("bash: ask", header)
        self.assertIn("task: false", header)
        self.assertNotIn("model:", header)

    def test_the_cq_payload_is_the_codex_translation_verbatim(self):
        sync.translate.configure(str(sync.SOURCE), str(sync.CODEX_TARGET))
        codex = sync.translate.generated_tree()
        self.assertEqual(codex["scripts/cq"], self.tree["quenching/scripts/cq"])


class Permissions(unittest.TestCase):
    def test_scoped_bash_is_ask_and_unrestricted_bash_is_allow(self):
        self.assertEqual("ask", sync.permissions("Read, Bash(cq specs status:*), Bash(cq git audit:*)")["bash"])
        self.assertEqual("allow", sync.permissions("Bash, Read, Edit")["bash"])
        self.assertEqual("deny", sync.permissions("Read, Grep")["bash"])

    def test_edit_webfetch_and_task_follow_the_source(self):
        granted = sync.permissions("Agent(quenching-specs:verifier, quenching-specs:scout), Read, Write")
        self.assertEqual(("allow", "deny", "allow"), (granted["edit"], granted["webfetch"], granted["task"]))

    def test_no_tools_line_adds_no_permission_block(self):
        self.assertEqual({}, sync.permissions(None))


class Platform(unittest.TestCase):
    def test_module_qualified_ids_and_agents_map_to_opencode_names(self):
        text = sync.platform("run /quenching-specs:specs:execute then quenching-specs:verifier on Claude Code")
        self.assertEqual("run quenching-specs-execute then quenching-verifier on OpenCode", text)

    def test_an_unowned_module_id_refuses(self):
        with self.assertRaises(ValueError):
            # Built by concatenation so the citation check does not read it as a live command id.
            sync.platform("/quenching-design:" + "specs:execute")

    def test_shared_configuration_path_survives(self):
        self.assertEqual(".claude/quenching.json", sync.platform(".claude/quenching.json"))


class CheckAndWrite(unittest.TestCase):
    def test_write_then_check_is_clean_and_any_edit_is_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(1, sync.main(["--check", "--target", tmp]))
            self.assertEqual(0, sync.main(["--write", "--target", tmp]))
            self.assertEqual(0, sync.main(["--check", "--target", tmp]))
            command = Path(tmp) / "commands/quenching-specs-status.md"
            command.write_text(command.read_text() + "hand edit\n")
            stale = Path(tmp) / "commands/stale.md"
            stale.write_text("---\n")
            self.assertEqual(1, sync.main(["--check", "--target", tmp]))
            self.assertEqual(0, sync.main(["--write", "--target", tmp]))
            self.assertTrue(stale.exists(), "a file no manifest owned is left alone")
            manifest = json.loads((Path(tmp) / sync.MANIFEST).read_text())
            self.assertNotIn("commands/stale.md", manifest["files"])


if __name__ == "__main__":
    unittest.main()
