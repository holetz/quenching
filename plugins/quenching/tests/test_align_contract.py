"""Contract tests for the knowledge alignment and documentation orchestration surfaces."""

import pathlib
import unittest

import _paths  # noqa: F401


ROOT = pathlib.Path(__file__).resolve().parents[1]


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
