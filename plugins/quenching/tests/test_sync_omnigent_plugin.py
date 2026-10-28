"""The Omnigent operator agent generator: source-tools lock, shell rule, model table and drift."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("sync_omnigent_plugin", REPO / "scripts/sync_omnigent_plugin.py")
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)

def optional(name):
    """An optional runtime, reached by name so the suite's stdlib-only import rule stays true; None when absent."""
    try:
        return importlib.import_module(name)
    except ImportError:
        return None


celpy = optional("celpy")
json_to_cel = optional("celpy.adapter").json_to_cel if celpy else None
omnigent_spec = optional("omnigent.spec")


def evaluate(tools, name, arguments=None, event_type="tool_call"):
    expression = sync.cel_expression(sync.permission_model(tools))
    env = celpy.Environment()
    data = {"name": name} if arguments is None else {"name": name, "arguments": arguments}
    event = json_to_cel({"type": event_type, "data": data})
    return str(env.program(env.compile(expression)).evaluate({"event": event})["result"])


class SourceToolsLock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = sync.generated_tree()

    def test_one_skill_per_source_command_one_sub_agent_per_source_agent_and_the_tree_validates(self):
        skills = sorted(r for r in self.tree if r.startswith("skills/") and r.endswith("/SKILL.md"))
        configs = sorted(r for r in self.tree if r.startswith("agents/") and r.endswith("/config.yaml"))
        self.assertEqual(len(list((sync.SOURCE / "commands").rglob("*.md"))), len(skills))
        self.assertEqual(len(sync.oc.agent_names()), len(configs))
        self.assertIn("skills/quenching-specs-develop/SKILL.md", skills)
        self.assertIn("agents/verifier/config.yaml", configs)
        self.assertEqual([], sync.validate(self.tree))

    def test_the_bundle_carries_no_payload_and_no_permissions_or_model_files(self):
        tops = {rel.split("/", 1)[0] for rel in self.tree}
        self.assertEqual({"skills", "agents", "config.yaml", "instructions.md", "README.md",
                          ".generated-from.json"}, tops)

    def test_operator_config_declares_skills_none_the_sub_agents_and_the_mcp_on_the_tag(self):
        text = self.tree["config.yaml"].decode("utf-8")
        self.assertIn('name: "quenching"', text)
        self.assertIn("harness: opencode", text)
        self.assertRegex(text, r"(?m)^skills: none$")
        self.assertNotRegex(text, r"(?m)^\s*model:")
        for agent in sync.oc.agent_names():
            self.assertIn(json.dumps(agent), text)
        version = (sync.SOURCE / "VERSION").read_text(encoding="utf-8").strip()
        self.assertIn(f"git+https://github.com/holetz/quenching@{version}#subdirectory=plugins/quenching", text)
        self.assertNotIn(f"@v{version}", text)
        self.assertIn('"quenching-mcp"', text)

    def test_a_head_the_source_does_not_grant_is_denied_independently(self):
        model = sync.permission_model("Read, Edit, Bash(cq:*)")
        self.assertNotIn("sys_os_edit", model["denied"])
        self.assertIn("sys_os_write", model["denied"])
        self.assertIn("Write", model["denied"])
        self.assertNotIn("sys_os_read", model["denied"])
        self.assertIn("Grep", model["denied"])

    def test_every_sub_agent_denies_exactly_what_its_source_does_not_grant(self):
        for source in sorted((sync.SOURCE / "agents").glob("*.md")):
            fields, _ = sync.oc.frontmatter(source.read_text(encoding="utf-8"), source)
            names = sync.tool_names(fields.get("tools"))
            heads = {n.split("(", 1)[0] for n in names}
            model = sync.permission_model(fields.get("tools"))
            for head, tools in {**sync.WRITE_HEADS, **sync.READ_HEADS}.items():
                for tool in tools:
                    self.assertEqual(head not in heads, tool in model["denied"], (source.name, tool))
            if "Bash" not in names and not any(n.startswith("Bash(cq") for n in names):
                self.assertTrue(set(sync.SHELL_TOOLS) <= set(model["denied"]), source.name)
            self.assertEqual(bool({"Agent", "Task"} & set(names)), model["spawn"], source.name)
            config = self.tree[f"agents/{source.stem}/config.yaml"].decode("utf-8")
            self.assertIn(json.dumps(sync.cel_expression(model)), config, source.name)

    def test_every_skill_and_sub_agent_carries_the_source_grant_never_a_missing_key(self):
        for source in sorted((sync.SOURCE / "commands").rglob("*.md")):
            name = "quenching-" + "-".join(source.relative_to(sync.SOURCE / "commands").with_suffix("").parts)
            fields, _ = sync.oc.frontmatter(source.read_text(encoding="utf-8"), source)
            text = self.tree[f"skills/{name}/SKILL.md"].decode("utf-8")
            self.assertTrue(text.startswith(f"---\nname: {name}\ndescription: "), name)
            if "allowed-tools" in fields:
                self.assertIn(f"\nallowed-tools: {json.dumps(fields['allowed-tools'])}\n---\n", text, name)
        for source in sorted((sync.SOURCE / "agents").glob("*.md")):
            fields, _ = sync.oc.frontmatter(source.read_text(encoding="utf-8"), source)
            text = self.tree[f"agents/{source.stem}/instructions.md"].decode("utf-8")
            self.assertTrue(text.startswith(f"---\ntools: {fields['tools']}\n---\n"), source.stem)

    def test_a_scoped_agent_allowlist_and_non_cq_bash_are_listed_never_widened(self):
        model = sync.permission_model("Agent(a, b), Bash(python3:*), Bash(cq specs show:*), Read")
        self.assertTrue(set(sync.SPAWN_TOOLS) <= set(model["denied"]))
        self.assertFalse(model["spawn"])
        self.assertEqual(2, len(model["not_expressed"]))
        self.assertEqual("scoped", model["shell"])
        self.assertEqual(["specs show"], model["verbs"])
        lone = sync.permission_model("Bash(python3:*), Read")
        self.assertEqual("denied", lone["shell"])
        self.assertTrue(set(sync.SHELL_TOOLS) <= set(lone["denied"]))

    def test_sub_agent_config_pins_a_harness_and_no_model_and_names_the_policy(self):
        text = self.tree["agents/git-steward/config.yaml"].decode("utf-8")
        self.assertIn("harness: opencode", text)
        self.assertNotRegex(text, r"(?m)^\s*model:")
        self.assertIn(sync.CEL_HANDLER, text)
        self.assertEqual("0.19.1", sync.OMNIGENT_VERSION)
        self.assertIn("v0.19.1", self.tree["README.md"].decode("utf-8"))

    def test_prose_is_rerooted_to_omnigent_and_references_become_mcp_resources(self):
        text = self.tree["skills/quenching-specs-status/SKILL.md"].decode("utf-8")
        self.assertNotRegex(text, r"(?i)opencode")
        self.assertIn(sync.CQ_WRAPPER, self.tree["agents/verifier/instructions.md"].decode("utf-8"))
        everything = b"".join(self.tree.values()).decode("utf-8")
        self.assertNotIn(sync.ROOT + "/references/", everything)
        self.assertIn(sync.REFERENCES_URI, text)

    def test_sub_agents_are_cited_by_their_registered_name_and_bundled_protocol(self):
        everything = b"".join(self.tree.values()).decode("utf-8")
        for name in sync.oc.agent_names():
            self.assertNotRegex(everything, rf"\bquenching-{name}(?![\w/:-])")
        self.assertNotIn(sync.ROOT + "/agents/", everything)
        text = self.tree["skills/quenching-specs-orchestrate/SKILL.md"].decode("utf-8")
        self.assertIn("`agents/orchestrator/instructions.md`", text)
        self.assertIn("Start the `orchestrator` agent", text)

    def test_a_payload_sub_agent_protocol_is_a_finding(self):
        tree = dict(self.tree)
        rel = "skills/quenching-specs-status/SKILL.md"
        tree[rel] = tree[rel] + f"\nSee {sync.ROOT}/agents/scout.md.\n".encode()
        self.assertTrue(any(p.startswith(f"{rel}: cites a sub-agent protocol") for p in sync.validate(tree)))

    def test_a_dangling_reference_resource_is_a_finding(self):
        tree = dict(self.tree)
        rel = "skills/quenching-specs-status/SKILL.md"
        tree[rel] = tree[rel] + f"\nSee {sync.REFERENCES_URI}no/such/file.md.\n".encode()
        self.assertIn(f"{rel}: cites {sync.REFERENCES_URI}no/such/file.md, which the source does not carry",
                      sync.validate(tree))


class ModelTable(unittest.TestCase):
    def test_only_measured_cells_are_filled(self):
        data = sync.compat()
        ids = ["quenching-git-commit", "quenching-specs-status", "quenching-knowledge-define"]
        rows = {line.split("|")[1].strip("` "): line for line in sync.compat_doc(ids, data).splitlines()
                if line.startswith("| `")}
        self.assertEqual(0, rows["quenching-specs-status"].count("/3"))
        self.assertEqual(len(data["models"]), rows["quenching-specs-status"].count("unmeasured"))
        self.assertEqual(len(data["models"]), rows["quenching-git-commit"].count("/3"))
        self.assertIn("2/3, 80%", rows["quenching-knowledge-define"])

    def test_cost_figures_come_from_the_json(self):
        figures = sync.costs(sync.compat())
        self.assertAlmostEqual(0.0206, figures["per_case"]["deepseek-v4-1-flash-1017"], places=4)
        self.assertAlmostEqual(0.1303, figures["per_case"]["opus-5-5"], places=4)
        self.assertIn("0.1856", json.dumps(sync.compat()))


class Drift(unittest.TestCase):
    def test_check_reports_a_changed_a_missing_and_a_stray_file(self):
        tree = sync.generated_tree()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            sync.write(tree, target)
            self.assertEqual([], sync.differences(tree, target))
            (target / "README.md").write_text("edited\n", encoding="utf-8")
            (target / "instructions.md").unlink()
            (target / "stray.txt").write_text("x\n", encoding="utf-8")
            self.assertEqual(["README.md", "instructions.md", "stray.txt"], sync.differences(tree, target))

    def test_the_committed_tree_and_model_table_have_no_drift(self):
        self.assertEqual([], sync.differences(sync.generated_tree(), sync.TARGET))
        self.assertEqual(sync.model_compat(), sync.MODEL_COMPAT.read_bytes())


@unittest.skipIf(celpy is None, "cel-python is not importable")
class AdversarialCommands(unittest.TestCase):
    TOOLS = "Bash(cq git commit:*), Bash(cq specs next:*), Read, Bash(python3:*)"

    def shell(self, command):
        return evaluate(self.TOOLS, "sys_os_shell", {"command": command})

    def test_granted_verbs_pass_whole_and_chained(self):
        for command in ("cq git commit --subject x", "cq specs next --json && cq git commit -m y",
                        "  cq git commit  ", "cq git commit -m 'a b'"):
            self.assertEqual("ALLOW", self.shell(command), command)

    def test_everything_the_regex_cannot_split_is_denied(self):
        for command in ("cq git commit; rm -rf /", "cq git commit $(rm x)", "cq git commit\nrm x",
                        "cq git commitx", "cq git push", "cq git commit > f", "cq git commit `id`",
                        "cq specs next | sh", "python3 x", "cq git commit \\\n x", "cq git commit&&rm x"):
            self.assertEqual("DENY", self.shell(command), command)

    def test_missing_or_malformed_command_is_denied(self):
        self.assertEqual("DENY", evaluate(self.TOOLS, "sys_os_shell"))
        self.assertEqual("DENY", evaluate(self.TOOLS, "sys_os_shell", {}))
        self.assertEqual("DENY", evaluate(self.TOOLS, "Bash", {"command": 5}))

    def test_ungranted_tools_are_denied_and_granted_ones_allowed(self):
        self.assertEqual("DENY", evaluate(self.TOOLS, "Write", {}))
        self.assertEqual("DENY", evaluate(self.TOOLS, "Task"))
        self.assertEqual("ALLOW", evaluate(self.TOOLS, "sys_os_read", {}))
        self.assertEqual("ALLOW", evaluate(self.TOOLS, "Write", {}, event_type="request"))

    def test_bare_cq_grant_allows_any_cq_verb_but_not_other_commands(self):
        self.assertEqual("ALLOW", evaluate("Bash(cq:*)", "Bash", {"command": "cq anything at all"}))
        self.assertEqual("DENY", evaluate("Bash(cq:*)", "Bash", {"command": "ls"}))


@unittest.skipIf(omnigent_spec is None, "omnigent is not importable")
class LoaderAcceptsTheBundle(unittest.TestCase):
    def test_the_operator_loads_with_its_skills_sub_agents_and_mcp(self):
        with tempfile.TemporaryDirectory() as directory:
            sync.write(sync.generated_tree(), Path(directory))
            loaded = omnigent_spec.load(Path(directory))
            self.assertEqual("quenching", loaded.name)
            self.assertEqual("none", loaded.skills_filter)
            self.assertEqual(len(list((sync.SOURCE / "commands").rglob("*.md"))), len(loaded.skills))
            self.assertEqual(sync.oc.agent_names(), sorted(agent.name for agent in loaded.sub_agents))
            self.assertEqual(["quenching"], [server.name for server in loaded.mcp_servers])


if __name__ == "__main__":
    unittest.main()
