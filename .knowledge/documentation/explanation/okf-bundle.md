---
type: documentation
title: The OKF bundle
description: The signature /.knowledge/ tree every adopted repository shares — its homes, the strict rules that keep it greppable, and why sameness is the feature.
resource: plugins/quenching/README.md
tags:
  - explanation
  - okf
timestamp: 2026-08-28
audience: both
authority: current
source: plugins/quenching/README.md §The signature; /.knowledge/ home index pages of this repository
maintainer: Israel Holetz
---

# The OKF bundle

Open any repository that adopted quenching and you already know where everything is. That is
the product's signature: one canonical **Open Knowledge Format (OKF v0.1)** bundle at
`/.knowledge/`, the same tree everywhere — adapted only by omission (a repo without data gets
no `catalog/`), never by rearrangement.

## The bundle tree

```text
/.knowledge/               # OKF bundle root
  index.md                 # the ONLY index.md with frontmatter: okf_version: "0.1"
  glossary.md              # the fixed A–Z term lookup — bundle root, not inside a home
  standards/               # "how WE do it", current — architecture/ code/ naming/ quality/ …
  concepts/                # generic knowledge we hold
  external/                # what we consume — tools/ libraries/ regulations/
  documentation/           # the product docs site — Diátaxis prose (this very site)
  catalog/                 # our data — system → catalog → schema → table
  vision/                  # direction by area, no schedule
```

| Home | Answers | `type` |
| --- | --- | --- |
| `standards/` | "how do WE do this, today?" — the current contract | `standard` |
| `concepts/` | "what do we understand that is true beyond this repo?" | `concept` |
| `external/` | "how does a tool/library/regulation we consume actually behave?" | `external` |
| `documentation/` | "what does a reader of our product need?" | `documentation` |
| `catalog/` | "what does this table mean and how do I reach it?" | `system`/`schema`/`table` |
| `vision/` | "where is this area heading?" — no deadlines, no order | `vision` |

Two deliberate absences: there is no `decisions/` home — an agreed-but-unproven decision is a
`standard` with `authority: background`, promoted to `current` when proven — and specs are
**not** in the bundle at all: they live on the configured provider
([the spec lifecycle](spec-lifecycle.md)), while the durable rules they earn land in
`standards/`.

## The strict rules

Sameness only pays if it is mechanical, so the format is strict where grep needs it to be:

- **`index.md` is reserved** — a pure listing, no frontmatter (the root index alone carries
  `okf_version`). Every folder with concept docs has an honest one.
- **Every concept doc carries a non-empty `type`** from the fixed vocabulary — and the type
  follows the home the doc sits in.
- **Names are canonical English** — folder names, file slugs, frontmatter keys and enums —
  while body **prose follows the repository's own language**. A term like
  `standards/quality/` greps identically in every adopted repo, whether its prose is English
  or Portuguese.
- **Links are relative within a home, absolute from the bundle root across homes** — one rule,
  no relative `../../` archaeology.
- **The glossary is one file, at the root.** The single deliberate exception to "one concept
  per file": a flat A–Z lookup, one entry per term, each linking to its full doc when one
  exists. Downstream, the documentation pipeline *projects* it — never copies it — into the
  published site ([reference/glossary.md](../reference/glossary.md)) with `<abbr>` definitions
  on every page.

The validator enforces what prose cannot: `cq knowledge validate .knowledge` reports missing
indexes, broken listing links, orphan docs and unresolvable `resource` pointers, with zero
errors as the bundle gate.

## Why sameness is the feature

For a human, the payoff is orientation: the tenth adopted repository costs nothing to learn.
For an agent, it is stronger — the bundle is a *contract*. An agent can answer "what is our
naming standard?" with one glob (`/.knowledge/standards/naming/`), resolve any unfamiliar term
in one file (`glossary.md`), and trust that a doc's `type` and `authority` mean the same thing
in every repository it ever visits. Cross-repo tooling becomes possible for the same reason:
`cq` can validate, project and index any bundle without per-repo configuration.

## TL;DR for agents

!!! abstract "TL;DR for agents"
    - Root: `/.knowledge/index.md` with `okf_version: "0.1"`; term lookup at
      `/.knowledge/glossary.md`; homes: `standards/ concepts/ external/ documentation/
      catalog/ vision/`.
    - Contract: reserved frontmatter-free `index.md` listings; non-empty `type` per doc,
      following the home; English identifiers, repo-language prose; relative links in-home,
      root-absolute across homes.
    - Verify: `cq knowledge validate .knowledge` — exit `0` and "0 error(s)" is the gate.

**Next:** how a spec turns work into new `standards/` entries —
[The spec lifecycle](spec-lifecycle.md).
