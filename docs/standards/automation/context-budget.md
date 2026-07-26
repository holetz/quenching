---
type: standard
title: Always-on context budget
description: What a skill surface costs before anything fires — the two description caps, what when_to_use may carry, and the per-surface ceiling
resource: plugins/claude-quenching/skills/*/SKILL.md, plugins/claude-quenching/commands/**
tags: [automation, skills, context, budget, performance]
timestamp: 2026-07-25
audience: both
authority: background
source: instrument-and-extend-skill-front plan — measured on this plugin's own 28-skill surface
maintainer: claude-quenching
---

# Always-on context budget

A skill's body loads only when the skill fires. Its **metadata never stops loading**: the
`description` and `when_to_use` of every skill, plus the `description` of every command wrapper,
are in context on every session before a single skill is selected. That is the budget this
standard governs. The mechanical rules live in [skills.md](skills.md) §The verifier and are
implemented by `skills.py`; this file owns the numbers and what may occupy them.

Born `authority: background`: the ceiling below is **one surface's measurement**, not a proven
threshold. It graduates to `current` once `skills.py budget` has run on this plugin plus at least
two adopting repos.

## Count the parsed value, never the YAML source

Every character count here is taken on the **parsed** frontmatter value. A description written as
a folded block scalar —

```yaml
description: >-
  First line of the description, wrapped
  across several indented lines.
```

— costs its *folded string*. The block indentation and the newlines are syntax the YAML parser
removes before Claude Code ever sees the field.

This is not pedantry. Counting the source lines instead inflates a description by roughly two
characters per line, which was enough to invent two cap violations on this plugin's own surface
that the model never paid for: the two skills reported at 1,568 and 1,559 measure 1,497 and 1,444
parsed, against a 1,536 cap. `skills.py` counts parsed, and any measurement offered against this
standard must say which it used.

## The two caps, per skill

| Cap | Applies to | Code | Severity |
| --- | --- | --- | --- |
| **1,536** | `description` + `when_to_use` together | `sk-metadata-cap` | error — Claude Code truncates past it |
| **1,024** | `description` alone | `sk-description-portable` | warning — the Agent Skills standard's hard limit |

They are different limits for different reasons and both apply.

**1,536** is what Claude Code will hold. What truncation eats is the **tail**, which is exactly
where the `Not for:` routing boundary lives — so a description that overflows loses the part that
tells the reader when *not* to fire it.

**1,024** is the Agent Skills standard. `when_to_use` is a Claude-Code-only extension; a surface
that relies on it is not portable to any other host, and a description over 1,024 is not portable
at all. This is a warning rather than an error because portability is a goal a repo may
legitimately decline — but it should decline it on purpose.

## What each field may carry

**`description`** — three things, in this order, and nothing else:

1. the leading concept: what the skill does and to what, in its own vocabulary;
2. the trigger phrases, quoted verbatim, one per distinct way a user asks — in the **second
   sentence**, so truncation cannot reach them (`sk-trigger-position`);
3. the boundary: `Not for: <adjacent job> → <owning skill>` (`sk-no-boundary`).

**`when_to_use`** — the job the skill is for, in one clause. It may add a relation the description
does not state. It may **not** restate the `Not for:` boundary: that is the same routing
information paid for twice inside one budget, and it is the doctrine's own **Duplication** failure
mode. Trimming exactly this from 28 skills on this surface recovered 2,944 characters and lost
nothing.

**What belongs in neither** — how the skill works. The step order, the tool calls, the checks it
runs: a reader who needs those has already fired the skill and loaded the body. A description's
job is to let a reader predict **when it fires and what will exist when it finishes**, not how.
Cutting exactly this prose from 17 over-limit descriptions on this surface recovered 2,605
characters without touching a single trigger phrase.

## The per-surface ceiling

`skills.py budget` sums the whole surface and compares it against a ceiling:

```bash
skills.py budget --json              # against the default ceiling
skills.py budget --ceiling 40000     # against a surface's own
```

The current default is **36,503 characters** — this plugin's measured baseline before the diet,
across 28 skills and 28 wrappers. It is a number a run produced, not one somebody picked, and it
is **revised only from a measurement**.

`budget` **reports; it never refuses.** Over the ceiling exits 1 and lists the skills sorted by
cost; exit 2 is unreachable from it. A surface may legitimately be large, and the decision to cut
is a human's.

Two things follow from the ceiling being per-surface rather than per-skill:

- **A new skill is not free.** Minting one adds its metadata plus its wrapper's to every session
  in the repo, forever. That is the honest cost to weigh against what the skill saves.
- **Trimming is bounded by discovery.** Where a description cannot shrink without dropping a
  trigger phrase, it is **reported, not trimmed** — which triggers earn their place is decided on
  measured should-trigger / should-not-trigger hit rates, not by whoever is editing that day.

## Rough conversion

`budget` reports `approxTokens` as characters ÷ 4. It is a rule of thumb for the report, not a
tokenizer count, and no decision should turn on the last digit. On this surface the diet moved
~9,126 approximate tokens to ~7,738 — the useful signal is the direction and the order of
magnitude.
