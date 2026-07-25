---
type: standard
title: Skill authoring and alignment
description: How the plugin's skills are classified, authored, named, mirrored as commands, and swept into conformance
resource: plugins/claude-quenching/skills/**, plugins/claude-quenching/commands/**
tags: [automation, skills, taxonomy, authoring]
timestamp: 2026-07-24
audience: both
authority: current
source: add-quenching-skill-pair change (skill-authoring + skill-alignment deltas)
maintainer: claude-quenching
---

# Skill authoring and alignment

The contract for how a skill enters and stays in this plugin's automation surface, distilled from
the `add-quenching-skill-pair` change. `quenching-skill-new` mints or edits one skill; `quenching-skill-align`
sweeps the whole surface into conformance. The command naming these produce is governed by
[command-surface.md](../naming/command-surface.md); the writing-doctrine detail lives once in
`plugins/claude-quenching/skills/quenching-skill-new/references/` and is cited, never restated.

## Single-axis classification

Every skill is classified on **exactly one axis**, and all naming and placement derive from it:

- **Domain-bound** — serves one folder subtree / one front. Named as the flattened path plus a
  verb, and mirrored by a thin command wrapper (see [command-surface.md](../naming/command-surface.md)).
- **Generic** — serves the surface as a whole. Named verb-object, never mirrored under a path: a
  flat command or none.

The classification test is naming the one folder/front the skill acts on: exactly one answer means
domain-bound; "the whole surface" means generic; several unrelated targets means the skill is kept
as-is and reported, never forced onto the axis.

## Authoring (`quenching-skill-new`)

- **Mirrored wrapper** for every domain-bound skill; a generic skill stays flat.
- **Writing doctrine** applied to every `SKILL.md`: predictable naming, trigger phrases in the
  description's second sentence, a no-op self-test, no negation-only guidance, a body well under
  the size cap with shared procedure pushed into `references/`.
- **Read the taxonomy rule before minting** (this standard); offer to create it from the template
  when a bundle-carrying repo lacks it.
- **One plan → one OK**: classification, names, files to write, and the OKF tail presented as a
  single plan, applied on one confirmation.
- **OKF tail** on every mint: regenerate the derived registry's GENERATED zone, offer a glossary
  entry for any coined term, append a log entry, and self-check.

## Alignment (`quenching-skill-align`)

- **Read-only inventory** of the existing skill + command surface before any plan.
- **One consolidated migration plan, one confirmation** — renames, wrapper mirroring, and the rule
  + registry created from the molds when missing; a rename referenced by product code or scripts
  gets its own individual confirmation.
- **MERGE, never clobber; never delete without a human word.** Only names, placement, and missing
  scaffolding change — existing skill bodies are preserved. An unclassifiable skill is kept and
  reported, never forced.
- **Post-apply verification**: regenerate the registry zone, confirm every wrapper resolves to a
  skill and vice versa (the bijection), and report residue.

## Convergence condition

The surface is aligned when every domain-bound skill carries the flattened-path name and a mirrored
wrapper, every generic skill carries a verb-object name with no stray wrapper, the bijection holds,
and the registry's GENERATED zone matches disk.
