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

    def test_template_enables_global_glossary_tooltips_from_the_staged_source(self) -> None:
        template = (ROOT / "assets/zensical/zensical.toml.tmpl").read_text()
        self.assertIn('abbr                               = {}', template)
        self.assertIn('[project.markdown_extensions.pymdownx.snippets]', template)
        self.assertIn('docs_dir = "site-source"', template)
        self.assertIn('base_path = [ "site-source" ]', template)
        self.assertIn('check_paths = true', template)
        # `.txt`, not `.md`: the snippet is input data, not a documentation page.
        self.assertIn('auto_append = [ "assets/glossary-abbreviations.txt" ]', template)

    def test_the_canonical_glossary_is_staged_with_no_derived_route(self) -> None:
        # The derived `reference/glossary.md` route existed only because the canonical glossary
        # sat OUTSIDE `docs_dir` and had to be copied in. The staged source carries the canonical
        # route, so a second copy would be exactly the `okf-legacy-glossary` the validator forbids.
        skeleton = ROOT / "assets/knowledge"
        nested = [p for p in skeleton.rglob("glossary.md") if p.parent != skeleton]
        self.assertEqual(nested, [], "the skeleton must carry no glossary copy inside a home")
        self.assertTrue((skeleton / "glossary.md").is_file())
        template = (ROOT / "assets/zensical/zensical.toml.tmpl").read_text()
        self.assertNotIn("reference/glossary.md", template)

    def test_capability_checker_accepts_a_site_directory(self) -> None:
        checker = ROOT / "assets/checks/zensical-capability-check.py"
        site = ROOT / "assets/checks/fixtures/zensical-capabilities/healthy"
        run = subprocess.run(
            [sys.executable, str(checker), str(site), "--enabled", "autorefs,mkdocstrings"],
            capture_output=True, text=True,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
