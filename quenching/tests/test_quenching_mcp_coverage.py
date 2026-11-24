"""Every `cq <pillar> <verb>` a skill, agent or reference body cites has an MCP tool, or a declared exception."""
import pathlib
import sys
import unittest

try:
    import _paths  # noqa: F401  — must precede the `quenching` import
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.mcp import catalog, coverage
from quenching.specs import mcp as specs_mcp

PLUGIN = pathlib.Path(__file__).resolve().parents[1]


class Coverage(unittest.TestCase):
    def test_every_verb_the_skill_agent_and_reference_bodies_cite_has_a_tool(self):
        bodies = coverage.bodies(str(PLUGIN))
        self.assertTrue(any(label.startswith("agents") for label, _ in bodies))
        self.assertTrue(any(label.startswith("skills") for label, _ in bodies))
        self.assertTrue(any(label.startswith("references") for label, _ in bodies))
        missing = [f"{label}: cq {' '.join(path)}" for label, path in coverage.uncovered(bodies)]
        self.assertEqual(missing, [], "add a catalog row (quenching/mcp/catalog.py) or an "
                                      "EXCEPTIONS entry with its reason (quenching/mcp/coverage.py)")

    def test_an_uncatalogued_verb_is_reported_with_its_body(self):
        found = coverage.uncovered([("skills/x.md", "run `.agents/quenching/bin/cq specs scrub 3`")])
        self.assertEqual(found, [("skills/x.md", ("specs", "scrub"))])

    def test_an_exception_a_catalog_row_and_a_hand_written_tool_are_covered(self):
        text = ("cq specs serve --port 1; cq deploy --target .; cq specs validate --spec 3; "
                "cq specs section 3 Tasks --write; cq git worktree acquire --branch b")
        self.assertEqual(coverage.uncovered([("a.md", text)]), [])

    def test_prose_that_names_no_verb_is_not_counted(self):
        for text in ("the cq specs write operations", "cq git pr", "cq components session",
                     "cq security", "cq is the launcher", "cq knowledge site-source docs"):
            with self.subTest(text):
                self.assertEqual(coverage.uncovered([("a.md", text)]), [])

    def test_a_choices_positional_is_part_of_the_verb(self):
        self.assertEqual(coverage.verb_path(["git", "worktree", "release", "--path"]),
                         ("git", "worktree", "release"))
        self.assertEqual(coverage.verb_path(["security", "leak"]), ("security", "leak"))
        self.assertIsNone(coverage.verb_path(["git", "worktree"]))

    def test_every_hand_written_specs_tool_names_its_verb(self):
        self.assertEqual(set(specs_mcp.COVERS), set(specs_mcp.TOOLS) | set(specs_mcp.WRITES))
        for name, path in specs_mcp.COVERS.items():
            with self.subTest(name):
                self.assertEqual(coverage.verb_path(["specs", *path]), ("specs", *path))

    def test_no_exception_is_also_a_tool(self):
        rows = {(row.pillar, *row.path) for row in catalog.CATALOG.values()}
        self.assertFalse(rows & set(coverage.EXCEPTIONS))
        for path, reason in coverage.EXCEPTIONS.items():
            self.assertTrue(reason.strip(), path)
            self.assertEqual(coverage.verb_path(list(path)), path)

    def test_taking_a_live_lease_reaches_no_agent_grant(self):
        from quenching.deploy import translate
        self.assertNotIn("specs_claim_take", catalog.tool_names())
        self.assertIn(("specs", "claim", "take"), coverage.EXCEPTIONS)
        for name in ("spec-orchestrator", "spec-runner"):
            with self.subTest(name):
                fields, _ = translate.split_frontmatter((PLUGIN / "agents" / f"{name}.md").read_text())
                tools = fields["tools"]
                self.assertNotIn("Bash(cq specs claim:*)", tools)
                for verb in ("acquire", "renew", "release", "list"):
                    self.assertIn(f"Bash(cq specs claim {verb}:*)", tools)
                self.assertNotIn("take", translate.transform_tools(tools, True))
                permissions = translate.opencode_permissions(tools)
                self.assertFalse(any("take" in key for key in permissions))


if __name__ == "__main__":
    unittest.main()
