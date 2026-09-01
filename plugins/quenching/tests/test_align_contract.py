"""Contract tests for the knowledge alignment and documentation orchestration surfaces."""

import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
ALIGN_DECLARATION = ROOT.parent.parent / "docs" / "standards" / "architecture" / "align-surface.md"


class KnowledgeAlignmentContract(unittest.TestCase):
    def test_align_preflights_evidence_and_classifies_residuals(self):
        align = (ROOT / "commands" / "knowledge" / "align.md").read_text(encoding="utf-8")

        for marker in (
            "preflight",
            "source-gap",
            "plugin-package-gap",
            "plan-drift",
            "not-applicable",
            "### Mapa editorial de publicação",
            "Semantic resource ambiguity",
        ):
            self.assertIn(marker, align)

        preflight = align.index("Before the inventory")
        inventory = align.index("### 2. Inventory + map")
        self.assertLess(preflight, inventory)

    def test_align_convergence_order_is_explicit(self):
        align = (ROOT / "commands" / "knowledge" / "align.md").read_text(encoding="utf-8")
        verify = align.split("### 8. Verify, then decide: loop or stop", 1)[1].split(
            "### 9. Report", 1
        )[0]
        checks = (
            "cq knowledge validate /docs --json",
            "cq knowledge project docs --check",
            "cq knowledge nav docs --check",
            "cq knowledge site-source docs site-source --check",
            "strict site build",
            "documentation-site-check.py",
        )
        positions = [verify.index(check) for check in checks]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("--glossary-term", verify)
        self.assertIn("never the first lexical glossary entry", verify)

    def test_conductor_order_follows_the_architecture_declaration(self):
        declaration = ALIGN_DECLARATION.read_text(encoding="utf-8")
        edges_block = declaration.split("## Conductor order and dependency edges", 1)[1].split(
            "The conductor has a separate named", 1
        )[0]
        edges = re.findall(r"^\|\s*`([^`]+)\s+→\s+([^`]+)`\s*\|", edges_block, re.MULTILINE)
        self.assertGreater(len(edges), 1)
        declared_order = [edges[0][0], *[target for _, target in edges]]
        self.assertEqual(
            [source for source, target in edges[1:]],
            declared_order[1:-1],
        )

        align = (ROOT / "commands" / "align.md").read_text(encoding="utf-8")
        execution = align.split("## Execution order", 1)[1].split("## Workflow", 1)[0]
        rows = [line for line in execution.splitlines() if line.startswith("| `")]
        parsed = []
        for row in rows:
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            front = re.match(r"`([^`]+)`", cells[0]).group(1)
            route = cells[1].strip("`")
            dependency = cells[2].strip("`")
            parsed.append((front, route, dependency))

        self.assertGreater(len(parsed), 1)
        self.assertEqual(len({front for front, _, _ in parsed}), len(parsed))
        self.assertEqual([front for front, _, _ in parsed], declared_order)
        for index, (front, route, dependency) in enumerate(parsed):
            with self.subTest(front=front):
                self.assertEqual(route, f"/quenching:{front}:align")
                self.assertEqual(dependency, "applicability" if index == 0 else parsed[index - 1][0])

        workflow = align.split("## Workflow", 1)[1].split("## Invariants", 1)[0]
        stage_positions = [workflow.index(f"### Front: `{front}`") for front, _, _ in parsed]
        self.assertEqual(stage_positions, sorted(stage_positions))
        self.assertIn("### Applicability", workflow)
        # The conductor is Markdown, and the session reader consumes completed transcripts rather
        # than intercepting Skill calls. This assertion therefore proves declaration/stage order,
        # not runtime invocation order.

    def test_build_gates_catalog_and_glossary_qa(self):
        build = (ROOT / "commands" / "knowledge" / "documentation" / "build.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("catalog-publication-check.py", build)
        self.assertIn("accepted publication map contains an approved", build)
        self.assertIn("catalog route", build)
        self.assertIn("not-applicable", build)
        self.assertIn("reference/catalog/index.md", build)
        self.assertIn("--glossary-term", build)
        self.assertIn("first lexical glossary entry", build)

    def test_build_checks_all_generated_paths_for_tracking(self):
        build = (ROOT / "commands" / "knowledge" / "documentation" / "build.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("site/`, `.quenching/`, and `site-source/` ignored", build)
        self.assertIn("git ls-files site .quenching site-source", build)
        self.assertIn("site-source-tracked", build)
        self.assertIn("already-tracked generated source is **REPORTED**", build)

    def test_embedded_documentation_references_use_current_paths(self):
        architecture = (
            ROOT / "assets" / "references" / "knowledge-documentation" / "architecture.md"
        ).read_text(encoding="utf-8")
        validation = (
            ROOT / "assets" / "references" / "knowledge-documentation" / "validation.md"
        ).read_text(encoding="utf-8")

        legacy_home = "docs/" + "documentation"
        self.assertNotIn(legacy_home, architecture)
        self.assertNotIn(legacy_home, validation)
        self.assertNotIn("--plan .quenching/documentation/plan.md --config", validation)
        self.assertIn("site-source/assets/glossary-abbreviations.txt", validation)
        self.assertIn("--glossary-term", validation)


if __name__ == "__main__":
    unittest.main()
