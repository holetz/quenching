---
type: standard
title: Design front
description: The single DTCG source, its portable and editorial projections, explicit arbitration with Impeccable, and the boundary between web and non-web drift
resource: plugins/quenching/assets/bin/quenching/design/**, plugins/quenching/assets/design/**, plugins/quenching/commands/design/**
tags: [architecture, design, dtcg, impeccable, projections]
timestamp: 2026-08-28
audience: both
authority: current
source: design-front architecture proposal revision 2, confirmed by the implementation and plugins/quenching/tests/test_design.py
maintainer: quenching
---

# Design front

The design front keeps values, judgment, and artifacts in separate layers without duplicating
authority. It is a quenching front; Impeccable is an optional consumer and remains the owner of
screen craft.

## One source, three output classes

`/.design/tokens.json` is a DTCG 2025.10 document. Quenching-specific values occupy only the
`org.quenching` extension; free-form component properties do not pretend to be tokens of a
`string` type that DTCG does not have ([model.py](../../../plugins/quenching/assets/bin/quenching/design/model.py)).

`cq design build` projects this source into three classes:

| Class | Artifacts | Authority |
| --- | --- | --- |
| Interoperability | `PRODUCT.md`, `DESIGN.md`, `.impeccable/design.json` | complete derivatives for external consumers |
| Editorial | `MEDIUM.md` and genre-rendered instances | contracts and medium-specific outputs |
| Internal adapters | `tokens.css`, `tokens.typ`, `tokens.py`, `brand-api.md` | values from the same DTCG graph at runtime |

The executable list and in-memory calculation live in
[build.py](../../../plugins/quenching/assets/bin/quenching/design/build.py):70. A pointer is not a
valid projection because consumers read the artifact's content.

## The portable boundary is deliberately lossy

`DESIGN.md` emits only `colors`, `typography`, `rounded`, `spacing`, and components limited to
eight properties — the closed set is in
[model.py](../../../plugins/quenching/assets/bin/quenching/design/model.py):29. Motion, shadows,
breakpoints, ramps, and complete snippets stay in DTCG and sidecar schema 2. An import never
removes DTCG tokens omitted by the projection; it names them as retained.

`PRODUCT.md` comes from canonical headings in the OKF homes. `## Platform` must be the plain value
`web`, `ios`, `android`, or `adaptive`; the generator refuses to infer it. The three portable
artifacts are created at the root, the location shared by context searches and the Impeccable 4.1.2
detector.

## Two directions, one human choice

An `DESIGN.md` written by `/impeccable document` is a proposed change. `cq design import` folds its
portable subset into `tokens.json`; `cq design build` makes the current source win. The doctor
reports byte-level divergence and does not choose taste — the fold implementation is in
[importer.py](../../../plugins/quenching/assets/bin/quenching/design/importer.py):27.

The GENERATED header declares provenance, not arbitration. A first align preserves an external
`DESIGN.md` until it creates and imports the source; only then does it build the projections
([align.py](../../../plugins/quenching/assets/bin/quenching/design/align.py):68).

## Verification split by competence

`cq design doctor` decides source validity, generated identity, orphaned assets, and repeated
literals in non-web primitives ([doctor.py](../../../plugins/quenching/assets/bin/quenching/design/doctor.py):21).
The Impeccable detector decides web drift in color, font, radius, and size when installed. Its
absence never fails the build or becomes an invented green result.

## One genre, N destinations

A contract under `/.design/genres/` declares fields, registry, and media. `cq design render` applies
the same tokens to HTML or Typst; PDF is a compilation of the Typst projection, not a second
template. The two operations and their gates live in
[genre.py](../../../plugins/quenching/assets/bin/quenching/design/genre.py):23. Button, input,
navigation, chip, and card form the interoperable vocabulary; eyebrow, rule, and frame are the
editorial extension of the brand pack.

## Alignment order

The `/align` root command conducts `/docs/` → `/.design/` → `.claude/`. Design comes after knowledge
because it projects product truth and installs standards; it comes before components because the
consolidated report must describe the final surface. The deterministic entry point for the new
pillar is in
[cq](../../../plugins/quenching/assets/bin/cq):66.
