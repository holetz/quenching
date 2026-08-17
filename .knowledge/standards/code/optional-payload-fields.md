---
type: standard
title: An optional payload field is `null` or absent, never a sentinel
description: A `cq specs` JSON field that answers "is there a usable value here" — like `overview` in `cq specs list --json` — reads back `null` for every state that is not a real answer (missing heading, present-and-empty, an explicit `- none — <reason>`), and the three-state detector that decides this lives once in the tool, never replicated per consumer
resource: plugins/quenching/assets/bin/quenching/specs/parse/text.py, plugins/quenching/assets/bin/quenching/specs/commands/read.py
tags: [code, cli, json-payload, explicit-none, findings]
timestamp: 2026-08-16
audience: both
authority: current
source: spec plan/corrigir-e-baratear-a-passada-de-triage (task 1.3) — the `## Open Decisions` this spec captured, resolved by order of arrival: this branch merged first, so it writes the standard `wire-the-overview-consumers` (ready, not yet built) will extend into `next --front`/`next --spec`/`status`
maintainer: quenching
---

# An optional payload field is `null` or absent, never a sentinel

**Three input states collapse into one output state.** A section's body can be absent (the
heading does not exist), present-and-empty (nothing but the shipped template's guidance
comment), or an explicit `- none — <reason>` (a human answered "nothing to say, on purpose").
None of the three is a usable answer, and a JSON payload projecting that section as a field
reads all three back as `null` — never three different sentinels, never the literal `- none`
bullet, and never a missing key that only some clients know to check for.

## The detector lives once, in the tool

`real_prose_or_none(text)`
([parse/text.py:65](../../../plugins/quenching/assets/bin/quenching/specs/parse/text.py#L65))
is the shared three-state check: it returns the body's own trimmed prose when there is a real
answer, `None` otherwise. It is deliberately **not** the same function as `has_real_content`
([parse/text.py:43](../../../plugins/quenching/assets/bin/quenching/specs/parse/text.py#L43)),
which the `## Handoff`/`## Impact`-style ready-gate already uses and which counts an explicit
none as *filled* — that is correct for a gate, where an omission and a null must both block
the same way, and wrong for a payload field, where a null has to read back as `null` rather
than as the literal bullet a human wrote.

`EXPLICIT_NONE_RE` ([parse/text.py:62](../../../plugins/quenching/assets/bin/quenching/specs/parse/text.py#L62))
matches a bulleted line starting with `none` (case-insensitive) — the same convention
`- none — <reason>` already carries everywhere else in this front's own frontmatter records
(`RECORD_NONE_RE`, `schema.py`), applied here to a section's markdown body instead of a
frontmatter scalar.

## One proven consumer today

`cmd_list`'s `overview` field
([commands/read.py:51](../../../plugins/quenching/assets/bin/quenching/specs/commands/read.py#L51))
is the first field built on this rule: `real_prose_or_none(info["sections"].get("Overview",
{}).get("body", ""))`, read from the same document `cmd_list` already holds for every other
field on the row — no second file read, no second call to the backend. `null` in the JSON
payload means "nothing usable was written yet," and a caller that ignores the field entirely
gets the same behaviour it always had.

## Extending this to a new field or a new consumer

The same three-state detector applies wherever a heading's body — never a frontmatter scalar,
which already has its own explicit-none convention — is projected as one field of a payload.
A new consumer calls `real_prose_or_none` directly; it never re-derives the three states from
`has_real_content` or from a bespoke regex, which is exactly the duplication `## Risks` of the
spec that wrote this standard flagged as a live risk between two branches building the same
rule in parallel.
