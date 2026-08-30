from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import _paths  # noqa: F401
from quenching.knowledge.nav import build_nav
from quenching.knowledge.site_source import MANIFEST_NAME, site_source_findings, stage_site_source


class SiteSourceTests(unittest.TestCase):
    def test_stages_only_the_allowlist_and_is_checkable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "docs"
            destination = Path(tmp) / "site-source"
            docs_root = "/docs/"
            glossary_route = docs_root + "glossary"
            (root / "tutorials").mkdir(parents=True)
            (root / "catalog").mkdir()
            (root / "external").mkdir()
            (root / "assets").mkdir()
            (root / "index.md").write_text("# Home\n")
            (root / "glossary.md").write_text("# Terms\n")
            (root / "tutorials" / "index.md").write_text("# Tutorials\n")
            (root / "tutorials" / "guide.md").write_text(
                "# Guide\n\n[private catalogue](../catalog/item.md), [private harness](../CLAUDE.md), "
                "[plugin note](/plugins/quenching/assets/references/note.md), "
                "[external note](https://example.test/note), [protocol-relative](//example.test/note), "
                f"[root]({docs_root}), [glossary]({glossary_route}), and [home](index.md).\n\n"
                "```md\n[code](/plugins/quenching/assets/references/note.md)\n```\n"
            )
            (root / "tutorials" / "CLAUDE.md").write_text("private harness\n")
            (root / "catalog" / "huge-table.md").write_text("catalogue data\n")
            (root / "external" / "vendor.md").write_text("external fact\n")
            (root / "assets" / "styles.css").write_text("body {}\n")

            payload = stage_site_source(root, destination)

            self.assertEqual(payload["files"], 5)
            self.assertTrue((destination / MANIFEST_NAME).is_file())
            self.assertFalse((destination / "catalog").exists())
            self.assertFalse((destination / "external").exists())
            self.assertFalse((destination / "tutorials" / "CLAUDE.md").exists())
            rendered_guide = (destination / "tutorials" / "guide.md").read_text()
            rendered_prose = rendered_guide.split("```", 1)[0]
            self.assertNotIn("](../catalog", rendered_guide)
            self.assertNotIn("](../CLAUDE", rendered_guide)
            self.assertNotIn("](/plugins", rendered_prose)
            self.assertNotIn("](../external", rendered_guide)
            self.assertIn("private catalogue", rendered_guide)
            self.assertIn("https://example.test/note", rendered_guide)
            self.assertIn("//example.test/note", rendered_guide)
            self.assertIn(f"]({docs_root})", rendered_guide)
            self.assertIn(f"]({glossary_route})", rendered_guide)
            self.assertIn("[code](/plugins/quenching/assets/references/note.md)", rendered_guide)
            self.assertIn("[home](index.md)", rendered_guide)
            checked, findings = site_source_findings(root, destination)
            self.assertFalse(findings, checked)

            (destination / "rogue.md").write_text("must not be read\n")
            _, findings = site_source_findings(root, destination)
            self.assertEqual([finding["code"] for finding in findings], ["site-source-stale"])

    def test_source_changes_require_a_new_stage_and_stage_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "docs"
            destination = Path(tmp) / "site-source"
            root.mkdir()
            (root / "index.md").write_text("# Home\n")
            stage_site_source(root, destination)
            before = (destination / MANIFEST_NAME).read_bytes()
            stage_site_source(root, destination)
            self.assertEqual(before, (destination / MANIFEST_NAME).read_bytes())

            (root / "index.md").write_text("# Changed\n")
            _, findings = site_source_findings(root, destination)
            self.assertEqual({finding["code"] for finding in findings}, {"site-source-stale"})

    def test_refuses_to_replace_an_unowned_destination(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "docs"
            destination = Path(tmp) / "site-source"
            root.mkdir()
            destination.mkdir()
            with self.assertRaises(ValueError):
                stage_site_source(root, destination)


class SiteNavTests(unittest.TestCase):
    def test_nav_uses_the_same_allowlist_as_the_staged_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for home in ("tutorials", "catalog", "external", "scratch"):
                (root / home).mkdir()
                (root / home / "index.md").write_text(f"# {home}\n")
            (root / "index.md").write_text("# Home\n")
            (root / "glossary.md").write_text("# Glossary\n")

            nav = build_nav(str(root))
            rendered_paths = repr(nav)
            self.assertIn("tutorials/index.md", rendered_paths)
            self.assertIn("glossary.md", rendered_paths)
            self.assertNotIn("catalog/index.md", rendered_paths)
            self.assertNotIn("external/index.md", rendered_paths)
            self.assertNotIn("scratch/index.md", rendered_paths)


if __name__ == "__main__":
    unittest.main()
