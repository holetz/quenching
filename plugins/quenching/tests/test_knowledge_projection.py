"""The glossary's abbreviation snippet is deterministic, source-addressed and gateable.

The route half of this module's subject is gone: the bundle root became `docs_dir`, so the
canonical glossary publishes itself and there is no derived page to keep in step. The tests for
`render_route`, `rewrite_link` and the publication-map decision went with the code they proved —
removed, not skipped, per `standards/workflows/retiring-a-standard.md`. What remains is the one
projection that is a real derivation rather than a copy.
"""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

import _paths  # noqa: F401
from quenching.knowledge.projection import (
    parse_glossary,
    projection_findings,
    render_abbreviations,
    write_projection,
)


class GlossaryProjection(unittest.TestCase):
    def test_parser_reads_only_terms_and_wrapped_definitions(self):
        entries = parse_glossary("""# Glossary

Prose — not an entry.

## Terms

- [**ASRC**](standards/loss.md) — expected loss stage
  with a wrapped definition.
- **Local term** — a local meaning

## How to enrich

- **Prose** — not a term.
""")
        self.assertEqual([entry.term for entry in entries], ["ASRC", "Local term"])
        self.assertEqual(entries[0].definition, "expected loss stage with a wrapped definition.")

    def test_snippet_is_addressed_to_the_source_it_was_derived_from(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "glossary.md"
            source.write_text("## Terms\n\n- **ASRC** — expected loss stage\n")
            snippet = render_abbreviations(source, parse_glossary(source.read_text()))
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            self.assertIn(f"source_sha256: {digest}", snippet)
            self.assertIn("*[ASRC]: expected loss stage", snippet)

    def test_a_definition_keeps_a_link_label_and_drops_its_target(self):
        # An abbr definition renders inside a tooltip attribute; markdown syntax would show up
        # there literally.
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "glossary.md"
            source.write_text("## Terms\n\n- **Probe** — the pass [align](standards/a.md) runs\n")
            snippet = render_abbreviations(source, parse_glossary(source.read_text()))
            self.assertIn("*[Probe]: the pass align runs", snippet)
            self.assertNotIn("standards/a.md", snippet)

    def test_title_cased_term_gains_running_prose_variant(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "glossary.md"
            source.write_text(
                "## Terms\n\n"
                "- **ASRC** — an acronym\n"
                "- **Derived stage** — computed, never written\n"
                "- **Probe** — the verifier pass\n"
                "- **probe** — a distinct lowercase entry\n"
            )
            snippet = render_abbreviations(source, parse_glossary(source.read_text()))
            self.assertIn("*[Derived stage]: computed, never written", snippet)
            self.assertIn("*[derived stage]: computed, never written", snippet)
            # An acronym keeps its exact form only.
            self.assertNotIn("*[aSRC]:", snippet)
            self.assertNotIn("*[asrc]:", snippet)
            # A lowercase form another entry claims is never shadowed by a variant.
            self.assertEqual(snippet.count("*[probe]:"), 1)
            self.assertIn("*[probe]: a distinct lowercase entry", snippet)

    def test_punctuation_term_is_declared_unabbreviatable_rather_than_emitted_broken(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "glossary.md"
            source.write_text("## Terms\n\n- [**`[P]` marker**](standards/task.md) — opt-in marker\n")
            snippet = render_abbreviations(source, parse_glossary(source.read_text()))
            self.assertIn("explicit glossary abbr fallback", snippet)
            self.assertNotIn("*[[P] marker]:", snippet)

    def test_write_then_check_is_idempotent_to_the_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "docs"
            (root / "assets").mkdir(parents=True)
            source = root / "glossary.md"
            source.write_text("---\ntype: concept\n---\n\n## Terms\n\n- **ASRC** — expected loss\n")
            payload = write_projection(root)
            checked, findings = projection_findings(root)
            self.assertFalse(findings, checked)
            self.assertEqual(checked["terms"], 1)
            snippet = root / "assets" / "glossary-abbreviations.txt"
            before = snippet.read_bytes()
            write_projection(root)
            self.assertEqual(before, snippet.read_bytes())
            self.assertEqual(payload["snippet"], str(snippet))

    def test_a_snippet_left_behind_by_an_older_glossary_is_a_finding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "docs"
            root.mkdir(parents=True)
            source = root / "glossary.md"
            source.write_text("## Terms\n\n- **ASRC** — expected loss stage\n")
            write_projection(root)
            source.write_text("## Terms\n\n- **ASRC** — changed definition\n")
            _, findings = projection_findings(root)
            self.assertEqual({f["code"] for f in findings}, {"glossary-snippet-stale"})

    def test_an_absent_glossary_is_not_a_finding(self):
        # A bundle may legitimately carry no vocabulary yet; inventing one is not this module's
        # business, and reporting its absence would make every young bundle red.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "docs"
            root.mkdir(parents=True)
            payload, findings = projection_findings(root)
            self.assertFalse(findings)
            self.assertEqual(write_projection(root)["skipped"],
                             "canonical glossary is absent or empty")


if __name__ == "__main__":
    unittest.main()
