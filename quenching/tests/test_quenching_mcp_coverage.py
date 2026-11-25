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

    def test_every_option_and_parameter_the_bodies_cite_exists_on_the_tool(self):
        bad = [f"{label}: {tool} {opt}"
               for label, tool, opt in coverage.uncited_options(coverage.bodies(str(PLUGIN)))]
        self.assertEqual(bad, [], "add the parameter to the tool's inputSchema "
                                  "(quenching/specs/mcp.py) or an OPTION_PARAM entry with its reason")

    def test_a_cited_option_or_parameter_the_tool_lacks_is_reported(self):
        found = coverage.uncited_options([
            ("a.md", "run `cq specs show --spec 3 --bogus`"),
            ("b.md", "call `specs_show(spec=3, bogus=true)`")])
        self.assertEqual(found, [("a.md", "specs_show", "bogus"), ("b.md", "specs_show", "bogus")])

    def test_specs_show_full_is_cited_and_served(self):
        self.assertEqual(coverage.uncited_options([
            ("a.md", "`cq specs show --spec 3 --full --json`; `specs_show(spec=3, full=true)`")]), [])

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

    def test_a_launch_root_before_the_pillar_is_skipped_not_read_as_the_verb(self):
        for text in ('cq --root "$TARGET_ROOT" delivery status --json',
                     "cq --root '/tmp/x' ops doctor", "cq --root=. proof status",
                     ".agents/quenching/bin/cq --root <worktree> security audit"):
            with self.subTest(text):
                match = coverage.CITE.search(text)
                self.assertIsNotNone(match)
                path = coverage.verb_path(match.group(1).split())
                self.assertIn(path[0], ("delivery", "ops", "proof", "security"))
        self.assertIsNone(coverage.CITE.search("`cq --root <worktree>` is the form"))

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

    def test_a_verb_a_tool_covers_leaves_no_shell_residue(self):
        for prefix in (("specs", "status"), ("git", "worktree"), ("components", "read"),
                       ("security", "leak"), ("specs", "claim")):
            with self.subTest(prefix):
                self.assertEqual(coverage.cli_residue(prefix), [])

    def test_the_residue_keeps_the_exceptions_and_the_verbs_with_no_tool(self):
        specs = coverage.cli_residue(("specs",))
        for path in (("specs", "serve"), ("specs", "migrate"), ("specs", "sync")):
            self.assertIn(path, specs)
        self.assertNotIn(("specs", "status"), specs)
        self.assertEqual(coverage.cli_residue(("git",)), [("git", "identity")])
        self.assertEqual(coverage.cli_residue(("deploy",)), [("deploy",)])

    def test_a_pillar_with_no_tool_below_collapses_to_one_path(self):
        self.assertEqual(coverage.cli_residue(("portal",)), [("portal",)])
        self.assertEqual(coverage.cli_residue(("specs", "sync")), [("specs", "sync")])

    def test_the_whole_router_residue_has_each_path_once_and_never_the_lease_take(self):
        whole = coverage.cli_residue(())
        self.assertEqual(len(whole), len(set(whole)))
        for path in (("deploy",), ("modules",), ("mcp",), ("portal",), ("specs", "serve")):
            self.assertIn(path, whole)
        self.assertFalse(any(path[:3] == ("specs", "claim", "take") or path == ("specs",)
                             or path == ("specs", "claim") for path in whole))
        self.assertEqual(coverage.cli_residue(("specs", "claim", "take")), [])

    def test_a_prefix_that_names_no_verb_is_left_to_the_caller(self):
        self.assertIsNone(coverage.cli_residue(("specs", "bogus")))
        self.assertIsNone(coverage.cli_residue(("nopillar",)))

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
