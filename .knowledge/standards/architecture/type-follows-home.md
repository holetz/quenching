---
type: standard
title: A doc's `type:` is the signature of its home, and renames with it
description: Every home in the canonical tree owns exactly one `type:` value (`standards/` → `standard`, `concepts/` → `concept`, and so on) — a home that renames without restamping every doc's `type:` recreates the naming complaint one level down, in the most greppable field of the bundle, and nothing today checks for the mismatch
resource: /.knowledge/**
tags: [architecture, taxonomy, frontmatter, okf, convention]
timestamp: 2026-08-13
audience: both
authority: current
source: renomear-docs-para-knowledge spec (task 1.2, 2026-08-13) — proved by the rename itself: every doc under the home that became `concepts/` was restamped `type: concept` in the same commit that moved it
maintainer: quenching
---

# A doc's `type:` is the signature of its home, and renames with it

## The rule

The canonical tree fixes exactly one `type:` per home — `standards/**` is `standard`,
`concepts/**` is `concept`, `vision/` is `vision`, and so on
([taxonomy.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-align/taxonomy.md) §The `type`
vocabulary is the tool's own source of this table). A home's name and a doc's `type:` are two
spellings of the same fact, not two independent choices — so when a home renames, every doc it
holds restamps its `type:` **in the same commit**, never left for later.

## Why this is worth stating on its own

Leaving a stale `type:` after a home renames does not just miss a cosmetic update. `type:` is the
field a grep or a validator reads first — it is the bundle's most greppable signature of what a
doc claims to be. A doc that says `type: knowledge` while sitting under `concepts/` is lying in
the one field a tool trusts without opening the file, in exactly the place the rename was meant to
stop being confusing. Renaming the folder and leaving the `type:` behind recreates the original
naming complaint **one level down** — invisible to a directory listing, visible to anything that
reads frontmatter.

## Proved, not just proposed

`renomear-docs-para-knowledge` renamed the home that held generic concept docs to `concepts/` and
restamped every doc under it from `type: knowledge` to `type: concept` in the same task (1.2) that
moved the files — never as a follow-up sweep. The same discipline applied to `documentation/**`
(`type: documentation`, unchanged by the quadrant rename) and to `external/**`
(`type: external`). No doc was left holding a home's old name in its own frontmatter.

## The enforcement gap

Nothing today **checks** this. `cq knowledge validate` has no finding for "this doc's `type:`
does not match the vocabulary its home declares", and `taxonomy.md`'s table is read by a human (or
an agent) doing a migration, not by any validator at check time. A future rename that forgets the
restamp — one home at a time, one doc at a time — would ship a bundle that looks converged from a
directory listing and is not, and nothing in the shipped skeleton or the validator would say so.
Closing this gap is a natural next spec: a `home↔type` map beside `taxonomy.md`'s table, and a
finding in `cq knowledge validate` that reads it.
