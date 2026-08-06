---
type: standard
title: A shared mold carries only keys every citer may write
description: A frontmatter mold cited by several commands is a fill-in invitation, so a key only one writer may legitimately set stays out of it and lives with that writer's own contract — prevention where a deterministic check is not available
resource: plugins/quenching/assets/references/docs-add/homes.md, plugins/quenching/assets/references/docs-import/sources.md, plugins/quenching/commands/docs/*.md
tags: [architecture, frontmatter, references, anti-fabrication, ownership]
timestamp: 2026-07-30
audience: both
authority: current
source: add-import-provenance spec (2026-07-25) §Design Decisão 2 — proved by the source_uri rollout; the resource: precedent from the docs-verification-layer plan
maintainer: quenching
---

# A shared mold carries only keys every citer may write

`docs-add/homes.md` §The frontmatter stamp is a **mold**: a block of keys that four commands —
`/docs:add`, `/docs:learn`, `/docs:harness`, `/docs:import-memory` — cite by absolute path and fill
in when they mint a doc. That is what makes it worth owning once.

It is also what makes it dangerous. **A key in a shared mold is an instruction to supply a value.**
A command reading that block sees a field with a placeholder and fills it, because filling it is
precisely what the block is for. There is no way to write "leave this one alone" inside a mold that
is loud enough to survive four independent readers.

So the rule is about *membership*, not about wording:

> A key that only **one** writer may legitimately set does not go in the shared mold. It lives with
> that writer's own contract, and the mold gets at most a line saying the key exists and who owns it.

## Why a warning in the mold is not the same thing

The tempting alternative is to keep the key in the mold and annotate it — *"only `/docs:import`
writes this"*. This repo has already run that experiment with `resource:`.

`resource:` is documented as **derived, never invented** in four separate places, and nothing
verified it. The prohibition was stated more times than most rules in the bundle and still produced
invented values, because a field present in a fill-in block is answered by default and a prose
prohibition is a thing a reader has to *remember* at the moment they are busy doing something else.
[bundle-verification.md](../quality/bundle-verification.md) draws the checkable half of that lesson —
an invariant restated in more than two skills is owed a deterministic check.

This standard is the **other half, for the cases where no check is available**. Some invariants
cannot be machine-checked at all: whether a stamped URI is truthful is decidable only against the
source, at the instant it was read, and no validator in this front fetches anything. When a rule
cannot be enforced afterwards, the design move is to make the wrong value **hard to produce** rather
than easy to catch — and the cheapest version of that is not offering the field.

Prevention and enforcement are not alternatives to choose between. Reach for the check when one is
reachable; reach for this when one is not.

## What it looks like applied

`source_uri:` — the exact URI of the source unit an imported doc came from — is written by
`/docs:import` and by nothing else. Its contract lives in
`docs-import/sources.md` §Attribution, next to the command that owns it. `homes.md` carries a
four-line note saying the key is *deliberately not in the mold*, who writes it, and where the
contract is; the mold itself is untouched.

The measurement is what makes the rule checkable in practice even though the *value* is not:

```bash
grep -rl source_uri plugins/quenching/                 # exactly 5 paths: the contract, the
                                                       # command, and the three citers
grep -rl source_uri plugins/quenching/assets/templates/ # nothing — a hit here is the failure
```

A sixth file, or any hit under the shared templates, is the leak this standard exists to prevent.
That is the shape to reuse: the rule cannot check whether a value is *right*, but it can check
whether the key ever spread to somewhere that would invite a wrong one.

## The boundary

This is not a rule against shared molds — the mold is correct, and the alternative (each command
restating ten keys) is the duplication this repo spends most of its effort removing. It is a rule
about what a shared thing may *contain*: everything every citer legitimately writes, and nothing
else.

Nor does it apply to a key that is merely **optional**. `maintainer:` is optional and every citer
may set it, so it belongs in the mold. The test is not "may this be absent?" but **"may this citer
write it at all?"** — one no is enough to keep the key out.
