# Backlog → idea inbox, feeding `superpowers:brainstorming`

## Problem

`backlog/` in the OKF v0.1 bundle (the tree `claude-quenching` installs into target repos)
currently means "formal trackable work": every item requires `type: backlog-item`, a
`pillar` subfolder, `vision_refs` pointing at an existing `vision/` area, and a "Done
criteria" section. That's real friction for the actual moment an idea occurs — you don't
yet know its pillar, whether a `vision/` area exists for it, or what "done" looks like.

`claude-quenching` target repos increasingly also run the `superpowers` plugin, whose
`brainstorming` skill turns a raw idea into a design (written to
`docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`) and then a plan (`writing-plans`,
`docs/superpowers/plans/...`). Superpowers has no notion of a persistent "idea not yet
worked on" — an idea, once raised, goes straight through brainstorming to a spec in one
sitting. There's no cheap place to *park* an idea between "I thought of this" and "I'm
ready to brainstorm it."

## Decision

`backlog/` changes identity: it stops being formal trackable work and becomes the **raw
idea inbox** — the fast, low-ceremony landing spot for a thought, before anyone has
decided its scope, direction, or alternatives. It exists specifically to feed
`superpowers:brainstorming`.

### Lifecycle

1. **Capture** — an idea lands in `docs/backlog/<idea-slug>.md` in seconds, via
   `quenching-insert`'s existing generic classify → stamp → index → log procedure, just
   with a drastically lighter mold (see below). No pillar, no vision lookup, no done
   criteria.
2. **Develop** — when ready, the human invokes `superpowers:brainstorming` on the idea.
   Brainstorming's own "explore project context" step naturally finds `docs/backlog/`,
   now the known idea inbox. No changes to the superpowers plugin itself are needed or
   made — the bridge is one-directional and passive (a well-known, well-indexed folder
   brainstorming's existing due-diligence step discovers on its own).
3. **Distill** — once brainstorming's design doc lands and is approved in
   `docs/superpowers/specs/`, the raw idea has done its job: the idea file is **removed**
   from `backlog/` (mirrors how an implemented ADR distills into `standards/` and leaves
   `decisions/`) and the transition is recorded in a new **Developed ledger** table in
   `backlog/index.md` — mirroring `decisions/index.md`'s existing "Distilled ledger" — so
   the trail survives in `docs/` even though the raw file is gone (git history keeps the
   rest).
4. **Optional permanent OKF record** — if the outcome deserves a durable, cross-repo
   greppable record beyond superpowers' own spec file (an ADR, a `vision/` update), that's
   a separate, manual `quenching-insert` step afterward. Not automatic, not required.

An idea is removed from `backlog/` when its spec is **approved**, not when brainstorming
merely starts — an abandoned brainstorming session leaves the idea in place, since nothing
superseded it yet.

### The minimal mold

New `type: idea` replaces `type: backlog-item` everywhere. Flat path
`backlog/<idea-slug>.md` — no `<pillar>/` subfolder (that classification step is exactly
the friction being removed). Frontmatter keeps only the OKF-recommended fields that avoid
a validator WARN (`title`, `description`, `timestamp`); `resource` is deliberately omitted
— there's nothing built yet to point at, which is inherent to what an idea *is*, not an
oversight, so that one WARN is expected and documented rather than hidden.

```yaml
---
type: idea
title: <one-line name of the idea>
description: <one-sentence gist>
timestamp: <ISO 8601>
---

# <idea title>

<1-3 sentences: what the idea is, why it might matter, any seed context.
No pillar, no vision_refs, no done-criteria — that thinking happens in
brainstorming, not here.>
```

`assets/templates/backlog/backlog-item.md` is renamed to
`assets/templates/backlog/idea.md`. The old `pillar` / `vision_refs` / "Done criteria"
apparatus is retired outright — it no longer has a home anywhere in the taxonomy. That
ground is now covered by brainstorming's own spec plus the optional post-hoc
`decisions/`/`vision/` insert (step 4 above).

No new skill is introduced. `quenching-insert` already generically inserts one concept doc
per its `homes.md` routing table; adding `idea` as a (much lighter) row is the entire
mechanism required.

## What does NOT go in `backlog/` anymore

- An idea already brainstormed and distilled (remove it; see Developed ledger).
- Anything requiring `pillar`/`vision_refs`/done-criteria — that apparatus is retired.
- A settled decision with considered alternatives (→ `decisions/`).
- Settled direction with no deadline (→ `vision/`).

## Files to update (mechanical propagation of the decision above)

| File | Change |
| --- | --- |
| `plugins/claude-quenching/assets/docs/backlog/index.md` | Rewrite: boundary → idea inbox, flat organization, "what does NOT go here", lifecycle note, new Developed ledger table |
| `plugins/claude-quenching/assets/docs/index.md` | Update the `backlog/` home one-liner |
| `plugins/claude-quenching/assets/templates/backlog/backlog-item.md` → `idea.md` | Rewrite to the minimal mold |
| `plugins/claude-quenching/assets/templates/README.md` | Mold table row: path shape + type |
| `plugins/claude-quenching/assets/templates/concept-front.md` | Type-enum comment: `backlog-item` → `idea` |
| `plugins/claude-quenching/assets/README.md` | Templates listing line |
| `plugins/claude-quenching/skills/quenching-align/references/taxonomy.md` | Tree comment, type-vocab table row, per-home description bullet |
| `plugins/claude-quenching/skills/quenching-align/references/okf-spec.md` | Type vocabulary list |
| `plugins/claude-quenching/skills/quenching-insert/references/homes.md` | Classification table row; add an `idea` vs `vision`/`decisions` tie-breaker bullet |
| `plugins/claude-quenching/skills/quenching-insert/SKILL.md` | Trigger phrase: "add a backlog item" → "capture a raw idea" |
| `plugins/claude-quenching/skills/quenching-harness/references/harness-routing.md` | Verdict-table row for roadmap/TODO/next-steps |
| `plugins/claude-quenching/skills/quenching-memory-to-docs/references/memory-routing.md` | Routing rows referencing `backlog/<pillar>/` + `backlog-item` |
| `plugins/claude-quenching/README.md` | Tree comment + memory-to-docs prose wording |

## Verification

- `cd plugins/claude-quenching && python3 assets/hooks/okf-validate.py assets/docs` must
  still report 0 errors, 0 warnings on the shipped skeleton (the repo's own CLAUDE.md
  contract).
- `grep -rn "backlog-item\|<pillar>" plugins/claude-quenching` after edits must return
  nothing (confirms no stale reference survives).
- No changes to `assets/hooks/okf-validate.py` are needed — it only enforces a non-empty
  `type`, never a fixed vocabulary, so the `idea` rename requires no validator code change.

## Out of scope

- No changes to the `superpowers` plugin itself (external, not owned by this repo).
- No new `quenching-*` skill.
- No change to how `decisions/` or `vision/` work today.
- No automatic promotion from a distilled idea into `decisions/`/`vision/` — that stays a
  manual, optional `quenching-insert` step.
