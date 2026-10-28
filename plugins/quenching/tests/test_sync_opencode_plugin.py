"""The OpenCode distribution generator: layout, deny-only permissions, and drift detection."""
import importlib.util
import json
import re
import subprocess
import sys
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

    def test_every_agent_bash_map_mirrors_the_cq_grants_of_its_source_tools(self):
        for source in sorted((sync.SOURCE / "agents").glob("*.md")):
            tools = next(line[6:].strip() for line in source.read_text(encoding="utf-8").splitlines()
                         if line.startswith("tools:"))
            grants = re.findall(r"Bash\(cq( [^:()]+)?:\*\)", tools)
            header = self.text(f"agents/quenching-{source.stem}.md").split("\n---\n", 1)[0]
            if re.search(r"(^|, )Bash(,|$)", tools):
                expected = "  bash: allow\n"
            elif grants:
                rules = "".join(f'    "cq{verbs} *": allow\n' for verbs in grants)
                expected = f'  bash:\n    "*": ask\n{rules}'
            elif "Bash(" in tools:
                expected = "  bash: ask\n"
            else:
                expected = "  bash: deny\n"
            self.assertIn(expected, header + "\n", source.name)

    def test_read_only_agent_is_never_wider_than_cq_allow(self):
        header = self.text("agents/quenching-verifier.md").split("\n---\n", 1)[0]
        self.assertIn("mode: subagent", header)
        self.assertIn("edit: deny", header)
        self.assertIn('bash:\n    "*": ask\n    "cq specs status *": allow\n    "cq specs show *": allow\n'
                      '    "cq git audit *": allow\n    "cq git pr view *": allow', header)
        self.assertNotIn('"cq *"', header)
        self.assertIn("webfetch: deny", header)
        self.assertIn("task: false", header)
        self.assertNotIn("model:", header)

    def test_the_cq_payload_is_the_codex_translation_verbatim(self):
        sync.translate.configure(str(sync.SOURCE), str(sync.CODEX_TARGET))
        codex = sync.translate.generated_tree()
        self.assertEqual(codex["scripts/cq"], self.tree["quenching/scripts/cq"])


class Payload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = sync.generated_tree()

    def test_the_payload_carries_the_checks_and_the_zensical_assets_the_commands_cite(self):
        self.assertIn("quenching/checks/documentation-site-check.py", self.tree)
        self.assertTrue(any(r.startswith("quenching/zensical/") for r in self.tree))
        self.assertFalse([r for r in self.tree if r.startswith("quenching/checks/") and r.endswith(".sh")])

    def test_the_ci_templates_do_not_ship_and_the_readme_shows_the_cq_pattern(self):
        self.assertFalse([r for r in self.tree if r.endswith(("ci-github-pages.yml", "azure-pipelines-docs.yml"))])
        self.assertIn('"cq *": "allow"', self.tree["README.md"].decode())
        self.assertIn('"cq <verbs> *": allow', self.tree["README.md"].decode())

    def test_a_cited_payload_path_the_tree_lacks_is_a_finding(self):
        tree = {"commands/x.md": f"see {sync.ROOT}/checks/gone.py".encode(), "quenching/checks/here.py": b""}
        self.assertEqual(1, len(sync.dangling_payload_citations(tree)))
        tree["quenching/checks/gone.py"] = b""
        self.assertEqual([], sync.dangling_payload_citations(tree))

    def test_the_readme_install_copies_into_the_destination_without_nesting_on_reinstall(self):
        readme = self.tree["README.md"].decode()
        self.assertIn("cp -R quenching/. ~/.opencode/quenching/", readme)
        self.assertNotIn("cp -R quenching ~/.opencode/quenching\n", readme)

    def test_every_generated_agent_opens_its_bash_map_with_the_catch_all(self):
        for path, content in self.tree.items():
            if path.startswith("agents/") and '"*": ask' in content.decode():
                block = content.decode().split("bash:", 1)[1].split("\n")[1:]
                self.assertEqual('"*": ask', block[0].strip(), path)


class Permissions(unittest.TestCase):
    def test_scoped_cq_bash_allows_only_the_granted_verbs_and_asks_for_the_rest(self):
        self.assertEqual({"cq specs status *": "allow", "cq git audit *": "allow", "*": "ask"},
                         sync.permissions("Read, Bash(cq specs status:*), Bash(cq git audit:*)")["bash"])
        self.assertEqual({"cq specs show *": "allow", "*": "ask"},
                         sync.permissions("Read, Bash(git ls-files:*), Bash(cq specs show:*)")["bash"])
        self.assertEqual({"cq *": "allow", "*": "ask"}, sync.permissions("Read, Bash(cq:*)")["bash"])

    def test_the_catch_all_comes_first_because_opencode_applies_the_last_matching_rule(self):
        bash = sync.permissions("Read, Bash(cq specs status:*), Bash(cq git audit:*)")["bash"]
        self.assertEqual(["*", "cq specs status *", "cq git audit *"], list(bash))

    def test_scoped_bash_without_cq_stays_ask(self):
        self.assertEqual("ask", sync.permissions("Read, Bash(git ls-files:*)")["bash"])

    def test_registered_agent_carries_the_cq_pattern_map_and_denies_edit_and_webfetch(self):
        registered, _ = sync.agent_files(sync.SOURCE / "agents" / "scout.md")
        header = registered.split("\n---\n", 1)[0]
        self.assertIn('  bash:\n    "*": ask\n    "cq specs show *": allow\n    "cq components read *": allow\n', header)
        self.assertIn("  edit: deny\n  webfetch: deny\n", header)

    def test_unrestricted_bash_is_allow(self):
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


class BundledCq(unittest.TestCase):
    def test_the_bundled_cq_enables_every_module_in_an_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(0, sync.main(["--write", "--target", tmp]))
            cq = str(Path(tmp) / "quenching/scripts/cq")
            work = Path(tmp) / "work"
            work.mkdir()

            def run(*args):
                return subprocess.run([sys.executable, cq, *args], cwd=work, capture_output=True, text=True)

            modules = run("modules", "--json")
            self.assertEqual(0, modules.returncode, modules.stderr)
            rows = json.loads(modules.stdout)["modules"]
            self.assertEqual([], [m["name"] for m in rows if not m["enabled"]])
            config = run("specs", "config")
            self.assertEqual(0, config.returncode, config.stderr)
            manifest = json.loads((Path(tmp) / "quenching/.claude-plugin/plugin.json").read_text())
            self.assertEqual((sync.SOURCE / "VERSION").read_text().strip(), manifest["version"])


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
