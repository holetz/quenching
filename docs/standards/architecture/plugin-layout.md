---
type: standard
title: Plugin layout — what may live under commands/
description: commands/** is the only tree Claude Code registers, so everything that is not an entry point lives under assets/ and is cited by absolute path
resource: plugins/quenching/commands/**, plugins/quenching/assets/**
tags: [architecture, plugin, commands, layout, claude-code]
timestamp: 2026-07-27
audience: both
authority: current
source: collapse-skills-into-commands spec (2026-07-26) — proved by the migration itself
maintainer: quenching
---

# Plugin layout — what may live under `commands/`

The rule the collapse to one file per entry point created, and that nothing previously stated.

## `commands/**` is the only tree Claude Code registers

Every `.md` under `commands/` **is** a command. Not "is treated as one if it looks right" — the
path is the identity, so `commands/docs/align/references/conformance.md` registers as
`/docs:align:references:conformance` and appears in the surface a session pays for.

Therefore: **anything that is not an entry point lives outside `commands/`.** Shared procedure,
reference files, fixtures, eval cases, notes.

This is not a style preference. Before the collapse the question could not arise — a
`references/` folder sat beside a `SKILL.md`, inside `skills/`, which Claude Code registered by
folder rather than by file. Moving bodies into `commands/` made the adjacency illegal, and
nothing in the repo said so.

## Where it goes instead: `assets/`

In this plugin, `assets/`. Its meaning is **deliberately wider** than it once was.

`assets/` used to mean *"the installable payload — copied into target repos, never executed
here"*. References are neither installed nor copied, so they did not fit that sentence. The
definition is now:

> **`assets/` is everything Claude Code must not surface as an entry point.**

The installable payload is a subset of that, not the whole of it.

**This widening was weighed against splitting the folder** (`assets/payload/` +
`assets/internal/`, say) and rejected while writing this standard, which is the point at which
the fudge would have shown. It does not read as one: both halves share the single property that
defines the folder — Claude Code ignores them — and the split would have bought a second
directory level, a second citation prefix, and 351 more path rewrites to distinguish two things
no reader confuses. If a future addition sits under `assets/` for a *third* reason, revisit; a
folder meaning three things is a folder meaning nothing.

Current subtrees: `bin/` `hooks/` `templates/` `docs/` `specs/` `claude/` (the installable
payload) · `references/` (shared procedure) · `evals/` (measured case sets).

## References are cited by absolute path, never relatively

Every citation of a bundled reference is:

```
${CLAUDE_PLUGIN_ROOT}/assets/references/<name>/<file>.md
```

`${CLAUDE_PLUGIN_ROOT}` substitutes inside a command body — measured, not assumed
([/docs/reference/tools/claude-code-skill-command-mechanics.md](/docs/reference/tools/claude-code-skill-command-mechanics.md)
rows 1–2, re-measured 2026-07-26 on Claude Code 2.1.215).

Relative paths are not merely inconvenient here, they are **wrong**: a relative path encodes the
depth of the *citing* file, so `commands/docs/documentation/build.md` and `commands/align.md`
would need different strings for the same target. The absolute form is one string everywhere,
which is what makes the citation set mechanically rewritable and mechanically checkable.

## The layout rule needs no check of its own

A stray file under `commands/` is a file with no `description`, which `skills.py doctor` already
reports as **`sk-no-description`** — an error. Adding a second check for the same defect would
give one failure two names.

That claim is evidence, not argument: `skills.py selftest` builds a throwaway surface containing
a `docs/references/homes.md` and asserts the finding fires.

## How a violation actually presents

Worth writing down, because it is silent. A reference parked under `commands/` does not error at
load. It registers, costs its slot in the always-on listing, and appears in the `/` menu as a
command that does nothing when invoked. Nothing fails; the surface is just quietly wrong. That is
why the rule is stated structurally here rather than left to be noticed.
