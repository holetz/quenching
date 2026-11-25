"""A bancada lê os formatos que o deploy ainda não escreve, e ausência é `absent`, nunca erro."""

import collections
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_ROOT = PLUGIN_ROOT.parent
FIXTURE = PLUGIN_ROOT / "tests" / "fixtures" / "copilot-bench"

try:
    import _paths  # noqa: F401
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401

from scripts import copilot_bench  # noqa: E402


class TheReader(unittest.TestCase):
    def test_the_fixture_github_surface_is_read(self):
        clients = copilot_bench.measure_clients(FIXTURE)
        self.assertEqual("present", clients["github"]["state"])
        self.assertEqual({name: True for name in copilot_bench.GITHUB_FORMATS},
                         clients["github"]["formats"])
        self.assertEqual(1, clients["agents"]["github"]["count"])
        self.assertEqual("reviewer.agent", clients["agents"]["github"]["rows"][0]["name"])
        self.assertEqual(["agents.instructions.md"], clients["rules"]["github"]["paths"])

    def test_the_jsonc_workspace_file_is_read_with_its_comment_and_trailing_comma(self):
        vscode = copilot_bench.measure_clients(FIXTURE)["vscode"]
        self.assertEqual("present", vscode["state"])
        self.assertTrue(all(vscode["keys"].values()), vscode["keys"])
        self.assertEqual(["**/.agents/quenching/assets/**"], vscode["filesExclude"])
        self.assertEqual(["**/.agents/quenching/assets/**"], vscode["searchExclude"])
        self.assertEqual(["chat.agent.sandbox"], vscode["sandbox"])

    def test_the_access_report_is_measured_alongside_the_clients(self):
        clients = copilot_bench.measure_clients(FIXTURE)
        self.assertEqual("present", clients["access"]["family"]["state"])
        self.assertIn("copilotCli", clients["access"])
        with tempfile.TemporaryDirectory() as empty:
            rows = copilot_bench.bench(pathlib.Path(empty), "target")["hypotheses"]
        h12 = next(row for row in rows if row["id"] == "H12")
        self.assertIn("regra(s)", h12["observation"])

    def test_the_agent_frontmatter_carries_the_fields_a_client_discovers(self):
        row = copilot_bench.measure_clients(FIXTURE)["agents"]["github"]["rows"][0]
        self.assertTrue(row["description"])
        self.assertEqual("Read, Grep, Glob", row["tools"])
        self.assertEqual("sonnet", row["model"])

    def test_absence_is_reported_as_absent_and_never_raises(self):
        with tempfile.TemporaryDirectory() as empty:
            clients = copilot_bench.measure_clients(pathlib.Path(empty))
            mcp = copilot_bench.measure_mcp(pathlib.Path(empty))
            skills = copilot_bench.measure_skills(pathlib.Path(empty))
        self.assertEqual("absent", clients["github"]["state"])
        self.assertEqual("absent", clients["vscode"]["state"])
        self.assertEqual(0, clients["agents"]["claude"]["count"])
        self.assertEqual("absent", mcp["state"])
        self.assertEqual("absent", skills["state"])

    def test_the_matrix_has_one_row_per_hypothesis_with_a_verdict_and_a_member(self):
        with tempfile.TemporaryDirectory() as empty:
            rows = copilot_bench.bench(pathlib.Path(empty), "target")["hypotheses"]
        self.assertEqual([f"H{number}" for number in range(1, 14)], [row["id"] for row in rows])
        for row in rows:
            self.assertIn(row["verdict"], copilot_bench.VERDICTS, row)
            self.assertTrue(row["member"], row)
            self.assertTrue(row["observation"], row)

    def test_the_insiders_directories_are_read_like_the_stable_ones(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = pathlib.Path(tmp)
            (home / ".vscode-insiders" / "extensions" / "ms.example-1.0").mkdir(parents=True)
            (home / ".config" / "Code - Insiders" / "logs" / "20260101T000000").mkdir(parents=True)
            (home / ".copilot" / "session-state").mkdir(parents=True)
            with mock.patch.object(copilot_bench, "home", return_value=home):
                clients = copilot_bench.measure_clients(home)
        states = {item["name"]: item["state"] for item in clients["cost"]}
        self.assertEqual("present", states["copilot-cli-session-state"])
        self.assertEqual("present", states["vscode-insiders-logs"])
        self.assertEqual("absent", states["vscode-logs"])
        self.assertEqual(1, clients["extensions"]["count"])
        self.assertIn("ms.example-1.0", clients["extensions"]["installed"])

    def test_the_threshold_table_carries_value_source_and_date(self):
        for limit in copilot_bench.THRESHOLDS:
            self.assertIsInstance(limit["value"], int)
            self.assertTrue(limit["source"])
            self.assertRegex(limit["date"], r"^\d{4}-\d{2}-\d{2}$")


class TheDisposableTarget(unittest.TestCase):
    """The probe against a target the deploy really installed: the user's surface, not the source."""

    @classmethod
    def setUpClass(cls):
        cls.root, cls.facts = copilot_bench.deploy_target("all")
        cls.payload = copilot_bench.bench(cls.root, "deploy", "all", cls.facts)

    def test_the_server_the_target_registers_answers_the_catalog_it_deployed(self):
        # The source checkout declares its own mount (454: `core`), so comparing it with a
        # disposable target deployed at the default would compare two different mounts. The
        # catalog is the invariant: the target publishes what the catalog carries.
        from quenching.mcp import catalog
        target = self.payload["measurements"]["mcp"]
        self.assertEqual("ok", target["state"], target)
        self.assertEqual(len(catalog.tool_names()), target["tools"])
        counts = collections.Counter(catalog.pillar_of(name) for name in catalog.tool_names())
        self.assertEqual(dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))),
                         target["byPillar"])

    def test_both_skill_copies_exist_and_the_bridge_is_byte_identical(self):
        skills = self.payload["measurements"]["skills"]
        self.assertEqual("present", skills["state"])
        self.assertEqual(13, skills["source"]["count"])
        self.assertEqual(skills["source"]["count"], skills["bridge"]["count"])
        self.assertEqual([], skills["bridge"]["changes"])

    def test_the_largest_description_is_the_same_one_the_source_file_carries(self):
        skills = self.payload["measurements"]["skills"]
        largest = skills["descriptions"]["largest"]
        source = (PLUGIN_ROOT / "skills" / largest["skill"] / "SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(len(copilot_bench.frontmatter_fields(source)["description"]),
                         largest["chars"])
        self.assertLessEqual(largest["chars"], skills["descriptions"]["cut"])
        self.assertEqual([], skills["descriptions"]["overCut"])

    def test_the_deploy_writes_no_github_surface(self):
        clients = self.payload["measurements"]["clients"]
        self.assertEqual("absent", clients["github"]["state"])
        self.assertEqual({name: False for name in copilot_bench.GITHUB_FORMATS},
                         clients["github"]["formats"])


if __name__ == "__main__":
    unittest.main()
