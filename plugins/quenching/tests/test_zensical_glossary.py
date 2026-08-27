"""Fixtures for the glossary projection consumed by Zensical's abbr extension."""

from __future__ import annotations

import re
import unittest


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
