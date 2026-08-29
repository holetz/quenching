"""Fixtures for the glossary projection consumed by Zensical's abbr extension."""

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def glossary_to_abbr(markdown: str) -> str:
    """Project canonical glossary bullets into Python-Markdown abbreviations."""
    entries = []
    pattern = re.compile(
        r"^[-*] (?:\[(?P<linked>[^]]+)\]\([^)]*\)|\*\*(?P<bold>[^*]+)\*\*) — (?P<definition>.+)$"
    )
    for line in markdown.splitlines():
        match = pattern.match(line)
        if match:
            term = match.group("linked") or match.group("bold")
            entries.append(f"*[{term.strip()}]: {match.group('definition').strip()}")
    return "\n".join(entries) + ("\n" if entries else "")


class GlossaryProjectionTests(unittest.TestCase):
    def test_projects_simple_and_compound_terms(self) -> None:
        source = """- **ASRC** — expected loss stage
- **chave conformada** — key shared across models
"""
        self.assertEqual(
            glossary_to_abbr(source),
            "*[ASRC]: expected loss stage\n*[chave conformada]: key shared across models\n",
        )

    def test_projects_linked_term_without_using_its_internal_link(self) -> None:
        source = "- [Grão](concepts/grain.md) — the row-level fact represented by a model\n"
        projection = glossary_to_abbr(source)
        self.assertEqual(projection, "*[Grão]: the row-level fact represented by a model\n")
        self.assertNotIn("concepts/grain.md", projection)

    def test_ignores_non_term_prose(self) -> None:
        self.assertEqual(glossary_to_abbr("# Glossary\n\nExplanation\n"), "")

    def test_template_enables_global_glossary_tooltips_and_route(self) -> None:
        template = (ROOT / "assets/zensical/zensical.toml.tmpl").read_text()
        self.assertIn('abbr                               = {}', template)
        self.assertIn('[project.markdown_extensions.pymdownx.snippets]', template)
        self.assertIn('base_path = [ "docs/documentation" ]', template)
        self.assertIn('check_paths = true', template)
        self.assertIn('auto_append = [ "assets/glossary-abbreviations.md" ]', template)
        self.assertIn('{ "Glossary"        = [ "reference/glossary.md" ] }', template)

    def test_published_page_is_a_projection_not_a_second_source(self) -> None:
        page = (ROOT / "assets/knowledge/documentation/reference/glossary.md").read_text()
        self.assertIn('source: /docs/glossary.md', page)
        self.assertIn('source_sha256:', page)
        self.assertIn('never second sources', page)

    def test_capability_checker_accepts_a_site_directory(self) -> None:
        checker = ROOT / "assets/checks/zensical-capability-check.py"
        site = ROOT / "assets/checks/fixtures/zensical-capabilities/healthy"
        run = subprocess.run(
            [sys.executable, str(checker), str(site), "--enabled", "autorefs,mkdocstrings"],
            capture_output=True, text=True,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
