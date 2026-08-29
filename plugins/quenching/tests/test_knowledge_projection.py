"""The glossary projection is deterministic, source-addressed and gateable."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import _paths  # noqa: F401
from quenching.knowledge.projection import (
    parse_glossary,
    projection_findings,
    render_abbreviations,
    render_route,
    rewrite_link,
    write_projection,
)


PLAN = """### Mapa editorial de publicação
| Home | Decisão | Motivo | Público | Rota publicada |
| --- | --- | --- | --- | --- |
| glossary.md | publicar derivado | vocabulary | readers | reference/glossary.md |
| standards/ | publicar derivado | contracts | readers | reference/standards/ |
| concepts/ | não publicar | internal | — | — |
"""


class GlossaryProjection(unittest.TestCase):
    def test_parser_reads_only_terms_and_wrapped_definitions(self):
        entries = parse_glossary("""# Glossary

Prose — not an entry.

## Terms

- [**ASRC**](../standards/loss.md) — expected loss stage
  with a wrapped definition.
- **Local term** — a local meaning

## How to enrich

- **Prose** — not a term.
""")
        self.assertEqual([entry.term for entry in entries], ["ASRC", "Local term"])
        self.assertEqual(entries[0].definition, "expected loss stage with a wrapped definition.")

    def test_links_map_from_bundle_paths_to_published_routes(self):
        routes = {"standards": "reference/standards", "glossary.md": "reference/glossary.md"}
        self.assertEqual(
            rewrite_link("../standards/loss.md#stage", "glossary.md",
                         "reference/glossary.md", routes),
            "standards/loss.md#stage",
        )
        self.assertIsNone(rewrite_link("../concepts/mental-model.md", "glossary.md",
                                       "reference/glossary.md", routes))

    def test_renderings_carry_the_same_source_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "glossary.md"
            source.write_text("## Terms\n\n- **ASRC** — expected loss stage\n")
            entries = parse_glossary(source.read_text())
            route = render_route(source, entries, {"glossary.md": "reference/glossary.md"})
            snippet = render_abbreviations(source, entries)
            digest = __import__("hashlib").sha256(source.read_bytes()).hexdigest()
            self.assertIn(f"source_sha256: {digest}", route)
            self.assertIn(f"source_sha256: {digest}", snippet)
            self.assertIn("*[ASRC]: expected loss stage", snippet)

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

    def test_punctuation_term_gets_explicit_route_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "glossary.md"
            source.write_text("## Terms\n\n- [**`[P]` marker**](../standards/task.md) — opt-in marker\n")
            entries = parse_glossary(source.read_text())
            route = render_route(source, entries, {"standards": "reference/standards"})
            snippet = render_abbreviations(source, entries)
            self.assertIn('<abbr title="opt-in marker">&#91;P&#93; marker</abbr>', route)
            self.assertIn("explicit glossary abbr fallback", snippet)
            self.assertNotIn("*[[P] marker]:", snippet)

    def test_write_then_check_is_idempotent_and_updates_index_and_nav(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "docs" / "glossary.md"
            source.parent.mkdir(parents=True)
            source.write_text("---\ntype: concept\n---\n\n## Terms\n\n- **ASRC** — expected loss stage\n")
            reference = root / "docs" / "documentation" / "reference"
            reference.mkdir(parents=True)
            (reference / "index.md").write_text("# Reference\n")
            config = root / "zensical.toml"
            config.write_text("[project]\nnav = [\n  \"index.md\",\n]\n")
            write_projection(root / "docs", PLAN, config)
            payload, findings = projection_findings(root / "docs", PLAN, config)
            self.assertFalse(findings, payload)
            before = {
                str(path.relative_to(root)): path.read_bytes()
                for path in (reference / "glossary.md", reference / "index.md", root / "zensical.toml",
                              root / "docs" / "documentation" / "assets" / "glossary-abbreviations.md")
            }
            write_projection(root / "docs", PLAN, config)
            after = {name: (root / name).read_bytes() for name in before}
            self.assertEqual(before, after)
            self.assertEqual(payload["terms"], 1)

    def test_stale_source_hash_and_projection_are_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "docs"
            source = root / "glossary.md"
            source.parent.mkdir(parents=True)
            source.write_text("## Terms\n\n- **ASRC** — expected loss stage\n")
            write_projection(root, PLAN)
            source.write_text("## Terms\n\n- **ASRC** — changed definition\n")
            _, findings = projection_findings(root, PLAN)
            self.assertEqual({finding["code"] for finding in findings},
                             {"glossary-source-hash-stale", "glossary-route-stale", "glossary-snippet-stale"})

    def test_explicit_unpublish_does_not_materialize_or_leave_exposure(self):
        plan = PLAN.replace("publicar derivado | vocabulary", "não publicar | vocabulary")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "docs"
            source = root / "glossary.md"
            source.parent.mkdir(parents=True)
            source.write_text("## Terms\n\n- **ASRC** — expected loss stage\n")
            payload = write_projection(root, plan)
            self.assertEqual(payload["skipped"], "canonical glossary is explicitly unpublished")
            self.assertFalse((root / "documentation" / "reference" / "glossary.md").exists())
            _, findings = projection_findings(root, plan)
            self.assertFalse(findings)


if __name__ == "__main__":
    unittest.main()
