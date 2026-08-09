---
type: standard
title: Retiring a reserved artifact — drop the checker, keep the reservation
description: A reserved filename that is retired keeps its slot in RESERVED and its skip in the hard block; only its checker goes, because unreserving it silently converts every surviving file into a malformed concept doc — plus the one departure this house made knowingly, and the three things that made it payable
resource: plugins/quenching/assets/hooks/okf-validate.py, plugins/quenching/assets/references/docs-align/conformance.md, plugins/quenching/assets/references/docs-align/okf-spec.md
tags: [architecture, okf, validator, reserved-names, deprecation]
timestamp: 2026-08-08
audience: both
authority: current
source: retire-docs-log spec (task 6.1); §The one time this was deliberately not followed added at the close of the remover-a-capability-quenching-md spec (2026-08-08), which removed `"QUENCHING.md"` from `EXEMPT` outright and accepted the blast radius this standard tabulates — recorded here so a reader of the rule learns of its one measured exception from the rule itself
maintainer: quenching
---

# Retiring a reserved artifact — drop the checker, keep the reservation

When this repo stops producing a file that its validator treats as a **reserved filename**,
the artifact is **retired**, never **unreserved**. Retiring removes the checker; the name
keeps its slot in the reserved set and its skip in the hard block.

## The rule

Retiring a reserved artifact is exactly three changes, and the third is the one everyone
forgets to *not* make:

1. **Remove its checker** — the dispatch to `check_<name>` and every finding code it emitted.
2. **Stop producing it** — no command creates, seeds, or appends to it; no skeleton ships one.
3. **Change nothing else.** The name stays in `RESERVED`
   ([okf-validate.py](/plugins/quenching/assets/hooks/okf-validate.py)) and stays in
   `hard_block_exempt()`. Its per-file branch stays too, returning no findings.

A retired artifact must also stay **out of the concept-doc count** wherever the tooling counts
docs — it is still not authored knowledge, and a retired file is not suddenly content.

## Why the reservation is load-bearing

Deleting the checker makes the validator silent about the file. That silence hides what the
reserved set is actually doing, and makes removing it look like harmless cleanup. It is not:
the reserved branch is what *keeps* the file out of the concept-doc path.

Drop the name from `RESERVED` and every surviving instance falls through to `check_concept`:

| What the file has | What it starts reporting |
| --- | --- |
| no frontmatter (the normal case) | **ERROR** `no-frontmatter` — and the bundle stops conforming |
| frontmatter without `type` | **ERROR** `missing-type` |
| any of the above, with `hardBlock` on | the `PreToolUse` gate **denies writes to the file** |

So the blast radius is not this repo — it is **every already-aligned target repo** that still
has the file on disk. They did nothing, upgraded the plugin, and their bundle went red. That
is the whole difference between the two words: **retired means nobody produces it; unreserved
means everybody who still has it is now broken.**

## The one time this was deliberately not followed

The rule above is the default, and it has been departed from **once**, knowingly: the
`remover-a-capability-quenching-md` spec (2026-08-08) removed `"QUENCHING.md"` from `EXEMPT`
entirely, along with everything else that named it. The condition the human set was *nothing may
be left referencing it — not even a code constant*, which the rule's third change cannot satisfy
by construction.

What made the departure payable, and what a future one has to match:

- **The blast radius was named before the fact, not discovered after.** The consequence this
  standard tabulates — an already-aligned target repo with a surviving `QUENCHING.md` starts
  reporting `no-frontmatter`, and denies writes to that file under `hardBlock` — was recorded as
  `ACCEPTED` in that spec's `## Risks`, with the reasoning in its `## Design`.
- **It rode a major bump.** Breaking already-aligned targets is exactly what a major release is
  for; the same departure inside a patch would not have been payable.
- **The rule was not amended.** Its scope — any reserved-or-exempt name — is unchanged, and the
  next retirement starts from *keep the reservation* again. What that spec removed was one name
  under one stated condition, not the reason the reservation is load-bearing.

## The consequence for disposition

Because the reservation survives, a retired artifact is **legible and writable forever**, and
`/docs:align` neither creates nor deletes one. Whether to keep or delete a surviving file is
the target repo's call, not the sweep's — a sweep that deleted it would be destroying content
it never owned. `/docs:status` reports it as a **figure with no finding code**, in the same
register as the density table: informative, never something to chase, with no owning command
to name.

## The guard

A rule whose failure is silent needs a test, not a paragraph. `okf-validate.py selftest`
carries a fixture bundle holding both shapes a surviving log takes — one with a `type:` in its
frontmatter, one with no frontmatter at all — and asserts three things at once: the tree
validates clean, the name is still in `RESERVED`, and `hard_block_exempt()` still covers it.
Undoing any leg of the retirement fails it.

This is what made the rule `authority: current` rather than `background`: the retirement of
`/.docs/log.md` was carried out under it, and the fixture was verified to fail when the
reservation is removed.
