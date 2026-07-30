---
type: standard
title: Plugin layout — what may live under commands/
description: commands/** is the only tree Claude Code registers, so everything that is not an entry point lives under assets/ and is cited by absolute path
resource: plugins/quenching/commands/**, plugins/quenching/assets/**
tags: [architecture, plugin, commands, layout, claude-code]
timestamp: 2026-07-30
audience: both
authority: current
source: collapse-skills-into-commands spec (2026-07-26) — proved by the migration itself; the self-contained-mold rule from the verify-allowed-tools-enforcement spec (2026-07-28)
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

### The revisit happened, and the answer was a name rather than a split

That trigger fired (2026-07-29). The inventory had drifted past three reasons without anyone
counting: `bin/` alone held four lifecycles — two tools installed into target repos (`specs.py`,
`skills.py`), one the plugin runs but never installs (`session.py`, which says so in its own
docstring), and two bash harnesses that grade *this checkout* and are payload of nothing
(`functional-checks.sh`, `conclude-order-check.sh`). `mkdocs/` was missing from the inventory
line above entirely.

**The split stayed rejected.** Nothing in the drift touched the reasoning against it. What the
folder needed was the fourth reason **named and given its own subtree**, which is exactly what
`evals/` had already done for the third: the two harnesses moved to `checks/`.

The rule that decides where an executable sits, made explicit by the same move: **by how it is
invoked, not by whether it ships.** `okf-validate.py` stays in `hooks/` beside the
`hooks-config.json` it loads from its own directory, even though it is the CLI sibling of the two
tools in `bin/` and the third member of the release lockstep — separating the pair breaks config
loading in every installed copy. Symmetry of *kind* is not a reason to move a file; adjacency it
depends on is a reason not to.

Current subtrees, by the reason each is here:

| Reason | Subtrees |
| --- | --- |
| payload copied whole by an align | `docs/` `specs/` `claude/` `mkdocs/` · `hooks/*.json` |
| payload applied per insert (molds) | `templates/` |
| tool the plugin executes | `bin/` · `hooks/okf-validate.py` |
| artifact of developing this repository | `references/` `evals/` `checks/` |

Four rows is one past what the warning above tolerates, so the warning needs restating rather
than quietly exceeding: what makes a folder mean nothing is a **membership rule that is a list**.
This one's rule is still the single sentence in the blockquote, and the four rows are
consequences of it that a reader can derive. Revisit when a subtree stops being derivable from
that sentence — not when the table gains a row.

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

### `<name>` is the owning command's path, flattened

`commands/docs/add.md` owns `references/docs-add/`; `commands/align.md` owns `references/align/`.
The path, with `/` → `-`, and nothing else — which is why `references/align-all/`, carrying the
name of the retired `quenching-align-all` skill, was renamed: a directory name that lies is
forbidden by [../naming/command-surface.md](../naming/command-surface.md), and it lies about the
one thing this convention encodes.

**Owning is not exclusive.** `references/align/` is cited by seven commands and
`references/skill-new/` by four. The folder is named for the command that would have to *change*
the procedure, not for every command that reads it — that is what keeps a single name answerable
when a rule has several readers.

**`evals/` encodes the same source differently, and the difference is deliberate.** An eval tree
keeps the slashes — `commands/skill/hook/new.md` ↔ `evals/skill/hook/new/` — because it mirrors
exactly one command 1:1 and is renamed in the same mechanical step as that command, so the two
paths differ by one prefix and a reviewer finds it without searching
([skill-eval/evaluation.md](/plugins/quenching/assets/references/skill-eval/evaluation.md)
§Where the artifacts live). A reference folder is shared, has no 1:1 to preserve, and gains a flat
listing from being flattened. Same input, two encodings, two jobs — do not reconcile them.

### A mold cites nothing it does not also install

The rule above governs citation **inside** the plugin, where `${CLAUDE_PLUGIN_ROOT}` resolves.
Anything an align **copies into a target repo** is the opposite case: the copy lands in a repo that
has none of this repository's `docs/`, and may have none of this plugin either. A cross-reference to
`quality/surface-verification.md` is correct in the plugin's own bundle and dangles in every repo
cut from the mold.

**The test is "does a copy of this leave the plugin?", not which folder it sits in.** Three trees
answer yes today — `assets/templates/**` (the harness and front-matter molds),
`assets/docs/**` (the OKF skeleton and the operator manual, both copied by `/docs:align`) and
`assets/specs/templates/**` — and a fourth added later inherits the rule without amending this
list. Naming one folder was how a `${CLAUDE_PLUGIN_ROOT}` citation reached `assets/docs/` unnoticed:
the reasoning covered it, the wording did not, and nothing else checks. **No validator catches
this** — a path that fails to resolve reads as ordinary prose, so the rule is the only guard.

So **a template states its caveat self-contained**, citing only what the same align installs
alongside it. This is why a mold and the plugin's own copy of the same standard legitimately differ
in wording: `skills.md` may point at the measurement behind a rule, while
`skills-standard.md` states the rule and stops. That difference is the rule being obeyed, not
drift — do not "reconcile" them.

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
