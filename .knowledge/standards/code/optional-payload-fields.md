---
type: standard
title: An optional payload field is `null` or absent, never a sentinel
description: Optional `cq specs` JSON fields use `null` for the absence of a usable answer, never a sentinel; the former `overview` projection and `summary` field are retired, and any future body projection must name one source and one shared detector
resource: plugins/quenching/assets/bin/quenching/specs/parse/text.py, plugins/quenching/assets/bin/quenching/specs/commands/read.py
tags: [code, cli, json-payload, explicit-none, findings]
timestamp: 2026-08-22
audience: both
authority: current
source: abandonar-slug-por-id-nativo (task 5.4) — the former `## Overview`/`overview` projection and `real_prose_or_none()` detector were retired by d29ae43; the title now supplies the short listing description and `summary` is not a contract field
maintainer: quenching
---

# Optional payload fields: `null` means no answer

The `cq specs` contract currently projects no optional body field. The former `## Overview`
section and its `overview` payload were retired; the former `real_prose_or_none()` helper was
deleted with them. The ranked table's `Summary` label is supplied by the native spec title, and
`summary` is not a frontmatter or JSON contract field.

Keeping this standard is still useful because a future payload field must make its absence honest.
When a source has no usable answer, the payload uses `null` — never a sentinel string, the literal
`- none` bullet, or a missing key that forces clients to guess which version of the tool they are
talking to.

## The source and detector must be singular

A future optional field names one canonical source and one shared detector in the tool. It does not
read a second file, call the backend again, or re-derive the source's states in each consumer.
The detector must distinguish the source's authored answer from template guidance and preserve the
source's own explicit-none convention; it must not silently turn an intentional null into prose.

The ready gate's `has_real_content` helper is not automatically the right detector for a payload:
it counts an explicit `- none — <reason>` as filled because a gate needs to distinguish an answered
null from an omitted section. A payload consumer must define its null semantics in the shared tool
layer and test absent, empty/template-only and explicit-none inputs together.

## Retired fields stay retired

Do not reintroduce `overview`, `real_prose_or_none()` or `summary` to make a consumer convenient.
If a new consumer needs a short description, read the native title; if it needs document-derived
state, expose that state through the command that owns its derivation and declare any unavailable
fields explicitly, as `cq specs list --lean --json` does.
