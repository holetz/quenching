"""The Omnigent distribution generator: source-tools lock, shell rule, model table and drift."""
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

    def test_one_bundle_per_source_command_and_agent_and_the_tree_validates(self):
        configs = sorted(r for r in self.tree if r.endswith("/config.yaml"))
        self.assertEqual(len(list((sync.SOURCE / "commands").rglob("*.md"))) + len(sync.oc.agent_names()),
                         len(configs))
        self.assertIn("agents/quenching-specs-develop/config.yaml", configs)
        self.assertIn("agents/quenching-verifier/config.yaml", configs)
        self.assertEqual([], sync.validate(self.tree))

    def test_a_head_the_source_does_not_grant_is_denied_independently(self):
        model = sync.permission_model("Read, Edit, Bash(cq:*)")
        self.assertNotIn("sys_os_edit", model["denied"])
        self.assertIn("sys_os_write", model["denied"])
        self.assertIn("Write", model["denied"])
        self.assertNotIn("sys_os_read", model["denied"])
        self.assertIn("Grep", model["denied"])

    def test_every_bundle_denies_exactly_what_its_source_does_not_grant(self):
        for kind, key in (("commands", "allowed-tools"), ("agents", "tools")):
            for source in sorted((sync.SOURCE / kind).rglob("*.md")):
                fields, _ = sync.oc.frontmatter(source.read_text(encoding="utf-8"), source)
                names = sync.tool_names(fields.get(key))
                heads = {n.split("(", 1)[0] for n in names}
                model = sync.permission_model(fields.get(key))
                for head, tools in {**sync.WRITE_HEADS, **sync.READ_HEADS}.items():
                    for tool in tools:
                        self.assertEqual(head not in heads, tool in model["denied"], (source.name, tool))
                if "Bash" not in names and not any(n.startswith("Bash(cq") for n in names):
                    self.assertTrue(set(sync.SHELL_TOOLS) <= set(model["denied"]), source.name)
                self.assertEqual(bool({"Agent", "Task"} & set(names)), model["spawn"], source.name)

    def test_every_instructions_file_carries_the_source_grant_never_a_missing_key(self):
        for kind, key in (("commands", "allowed-tools"), ("agents", "tools")):
            for source in sorted((sync.SOURCE / kind).rglob("*.md")):
                name = ("quenching-" + "-".join(source.relative_to(sync.SOURCE / kind).with_suffix("").parts)
                        if kind == "commands" else sync.AGENT_PREFIX + source.stem)
                fields, _ = sync.oc.frontmatter(source.read_text(encoding="utf-8"), source)
                text = self.tree[f"agents/{name}/instructions.md"].decode("utf-8")
                self.assertTrue(text.startswith(f"---\n{key}: {fields[key]}\n---\n"), name)

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

    def test_config_pins_a_harness_and_no_model_and_names_the_policy(self):
        text = self.tree["agents/quenching-git-commit/config.yaml"].decode("utf-8")
        self.assertIn("harness: opencode", text)
        self.assertNotRegex(text, r"(?m)^\s*model:")
        self.assertIn(sync.CEL_HANDLER, text)
        self.assertEqual("0.19.1", sync.OMNIGENT_VERSION)
        self.assertIn("v0.19.1", self.tree["README.md"].decode("utf-8"))

    def test_prose_is_rerooted_to_omnigent(self):
        text = self.tree["agents/quenching-specs-status/instructions.md"].decode("utf-8")
        self.assertNotRegex(text, r"(?i)opencode")
        self.assertIn(sync.CQ_WRAPPER, self.tree["agents/quenching-verifier/instructions.md"].decode("utf-8"))
        self.assertNotRegex(text, r"(?i)opencode")
        self.assertIn("Omnigent does **not** require `cq`",
                      self.tree["quenching/references/align/tool-resolution.md"].decode("utf-8"))


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
            (target / "PERMISSIONS.md").unlink()
            (target / "stray.txt").write_text("x\n", encoding="utf-8")
            self.assertEqual(["PERMISSIONS.md", "README.md", "stray.txt"], sync.differences(tree, target))

    def test_the_committed_tree_has_no_drift(self):
        self.assertEqual([], sync.differences(sync.generated_tree(), sync.TARGET))


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
class LoaderAcceptsEveryBundle(unittest.TestCase):
    def test_every_bundle_loads_with_the_omnigent_spec_loader(self):
        with tempfile.TemporaryDirectory() as directory:
            sync.write(sync.generated_tree(), Path(directory))
            for bundle in sorted((Path(directory) / "agents").iterdir()):
                loaded = omnigent_spec.load(bundle)
                self.assertEqual(bundle.name, loaded.name)


if __name__ == "__main__":
    unittest.main()
