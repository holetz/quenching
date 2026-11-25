"""A bancada lê os formatos que o deploy ainda não escreve, e ausência é `absent`, nunca erro."""

import pathlib
import sys
import tempfile
import unittest

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
        self.assertEqual(["**/.agents/quenching/assets/**"], vscode["searchExclude"])
        self.assertEqual(["chat.agent.sandbox"], vscode["sandbox"])

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

    def test_the_threshold_table_carries_value_source_and_date(self):
        for limit in copilot_bench.THRESHOLDS:
            self.assertIsInstance(limit["value"], int)
            self.assertTrue(limit["source"])
            self.assertRegex(limit["date"], r"^\d{4}-\d{2}-\d{2}$")


if __name__ == "__main__":
    unittest.main()
