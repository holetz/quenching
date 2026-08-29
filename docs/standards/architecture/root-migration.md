---
type: standard
title: A declared root migrates by structural detection, never by `okf_version`
description: When a plugin release renames a root it itself declares — the bundle root moved from `/.docs/` to `/docs/` once — the migration is detected site by site from what sits on disk, never gated on a version bump, and resolved through exactly one route, `/quenching:knowledge:align`
resource: plugins/quenching/assets/bin/quenching/knowledge/checks.py, plugins/quenching/assets/bin/quenching/knowledge/validate.py, plugins/quenching/assets/references/knowledge-align/migration.md
tags: [architecture, bundle, okf, migration, convention]
timestamp: 2026-08-13
audience: both
authority: background
source: renomear-docs-para-knowledge spec (task 4.2, 2026-08-13) — the detection side is proven by `test_knowledge.py`'s `LegacyRootDetector`/`LegacyHomeDetector`/`LegacyDocQuadrantDetector`/`LegacyGlossaryDetector` fixtures; the end-to-end resolution through `/quenching:knowledge:align` against a discard bundle in the old layout is proven at `/quenching:specs:conclude`'s pre-merge `## Validation` gate, which is what promotes this doc to `authority: current`
maintainer: quenching
---

# A declared root migrates by structural detection, never by `okf_version`

[bundle-root.md](bundle-root.md) fixes two roots — `/docs/` and `/.specs/` — and states
neither ever moves via configuration. This standard is the other half: the **one route** by
which a fixed root's value may still change, between plugin releases.

## Detection is structural, site by site — never version-gated

`okf_version` versions the capabilities of the Open Knowledge Framework, never this plugin's own
layout, so a version bump is neither necessary nor sufficient evidence that a root moved.
`cq knowledge validate` instead emits four independent findings, each looking at exactly one site
and each idempotent — migrating that one site clears it, whether or not the others have migrated
yet: `okf-legacy-root` (the new root absent, the pre-rename one present), `okf-legacy-home` (a
pre-rename home name at the bundle root), `okf-legacy-doc-quadrant` (a pre-rename Diátaxis
quadrant under `documentation/`), `okf-legacy-glossary` (`glossary.md` sitting inside a home
instead of at the bundle root). The exact severities and messages are
[conformance.md](/plugins/quenching/assets/references/knowledge-align/conformance.md)
§Pre-rename layout's, cited rather than restated here.

## Resolution is exactly one route

`/quenching:knowledge:align` is the only command that resolves an `okf-legacy-*` finding — never a
hand `git mv`, never a target improvising its own path. The procedure —
[migration.md](/plugins/quenching/assets/references/knowledge-align/migration.md) §1g —
renames the root first, then the homes, quadrants and glossary underneath it, each swept for
blast radius and each gated on its **own** confirmation the moment it reaches product code (a
path default, a docstring, a hook's own root constant): a root rename is never a bare `git mv`
precisely because its own name is always also a path constant somewhere in the tool that
validates the bundle.

## No dual-root compatibility window

At any moment exactly one root name is valid, matching
[bundle-root.md](bundle-root.md)'s own invariant that a root is a fixed convention, not a
setting with two accepted values during a transition. The old root and the new one are never
both read at once; the migration is one rename per site, immediately superseding the old name.

## This rule has already been exercised once

The bundle root itself is the worked example: it was `/.docs/` until `renomear-docs-para-knowledge`
(2026-08-13) moved it to `/docs/` — the same structural detection and the same one-route
resolution this standard describes, proven on the plugin's own bundle before being written down
as a rule for every future root rename, including a `/.specs/` this spec deliberately left
unrenamed (## Out of Scope) but for which this machinery now exists.
