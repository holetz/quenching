---
description: Capture or create a spec. Triggers on "convert to a spec", "add to the backlog", "create a spec". Not for: filling a spec's remaining sections or building one.
argument-hint: [what to capture, or a path to a plan file]
allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(py:*), AskUserQuestion
model: sonnet
---
# /quenching:specs:create — capture one spec

**Input**: `$ARGUMENTS` — a short description of the problem, **or** a path to a Claude Code plan
file. With neither, glob `~/.claude/plans/*.md`; if that is empty too, ask what to capture.

Creates ONE spec. That locator is a spec's whole active life, so what is created here is what gets
built: this command creates it, `/quenching:specs:develop` fills its sections, `/quenching:specs:execute` builds it, and
`/quenching:specs:conclude` closes it out under the same identity. Nothing here to retire, hand off, or
reconcile — and no ledger.

The layout, the fourteen canonical sections, the gates, the front's on-write check and the
`specs.py` surface live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md).

## The one rule: effort proportional to input

This command has two inputs of wildly different richness, and exactly one behaviour: **write down
what you were given, and nothing more.**


| Input                   | What gets written                        |
| ----------------------- | ---------------------------------------- |
| a sentence              | `## Problem`, alone                      |
| a Claude Code plan file | every section the plan actually supports |


## Doctrine

- **A sentence becomes `## Problem` and stops.** `specs.py new` stamps the frontmatter (`slug`,
`title`, `date`, `verification`) and that one heading. `date` is the capture date, written here and
never again. Every other canonical heading is left ABSENT,
which the stage-scoped explicit-none rule
([spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md) §The gates)
makes legal. Writing fourteen `- none` headings here would make a fresh capture derive as
`designed` and clear the whole ready gate without anyone having thought anything.
- **Never invent what the input lacks.** On the plan-file path, `- none — the plan recorded no alternatives` is honest; a fabricated risk is not. Where the source said nothing, either leave
the heading absent or write an explicit none that *says* the source was silent.
- **Kebab slug in the repo's declared language.** `slugify` folds accents (`criação` → `criacao`)
and `SLUG_RE` refuses (exit 2) on a bad one — derive it in the language
[communication.md](docs/standards/agents/communication.md) declares.
- **MERGE, never clobber.** `specs.py new` refuses (exit 2) on an existing slug. Take that as the
answer: sharpen the existing spec instead, or pick a different slug.

## Resolving the tool

Resolve `specs.py` per
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool; branch on the **exit code** (0 ok · 1 findings · 2 refusal), never on prose.

## Workflow

### 1. Classify the input

**Prose** → the sentence path. **A path to an existing `.md`**, or an explicit ask to convert a
plan → the plan-file path. This is the one decision the CLI cannot make for you: `specs.py new`
(step 5) resolves the backend, the workspace and the seed on its own, and reports a legacy
`backlog/`/`ready/` folder as a finding rather than writing into one.
**Done when:** the path is chosen.

### 2. Derive the slug

Take a title and a one-sentence problem from the input, and derive a kebab slug in the repo's
declared language. On the plan-file path, derive it from the plan's title or goal ("Add rate
limiting to the API" → `add-api-rate-limiting`).

**The collision check is `specs.py new`'s exit 2** (`sp-slug-exists`, naming where it is) — never a
front listing first, which under `github` is a paginated fetch of every issue (2.4s measured).
**Done when:** a canonical slug is in hand.

### 3. Plan-file path only — read it, and read the bundle

Read the whole plan file, then read
[specs-create/plan-mapping.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-create/plan-mapping.md)
§The mapping and classify the plan's parts against it.

**On the sentence path, skip this step entirely** — reading a bundle to write two sentences is
exactly the cost this command exists to avoid.
**Done when:** the plan's parts are classified, or the sentence path skipped this.

### 4. Create the plan

```bash
specs.py new <slug> --title "<title>"
```

Exit 2 means the slug already exists — say so and stop, never invent a variant to get past it. Any
other backend failure (`sp-backend-unavailable`, `sp-worktree-unusable`, `sp-worktree-failed`) is
reported verbatim, naming `/quenching:specs:align`.
**Done when:** the tool exited 0 and reported the locator it created.

### 5. Write the sections

Always write `## Problem` — the problem or opportunity in the source's own framing. Two sentences
is a complete answer.

```bash
specs.py section <slug> Problem --write   # body on stdin
```

**Sentence path: stop here.** Write nothing into any other heading.

**Plan-file path:** additionally write each section the plan actually supports, via
`specs.py section <slug> "<Heading>" --write`. Where the plan was silent on a section you are
writing others around, write `- none — <what the source did not record>`. Never fabricate.
**Done when:** `## Problem` is filled, and no section beyond what the input supported exists.

### 6. Check

Run `specs.py validate --spec <slug>` — the spec's own conformance, and the whole check.
**Done when:** the check is clean, or the residue is reported verbatim.

### 7. Report

**Report the locator `specs.py new` returned** — its `path` field — and the slug. It is
`plans/<slug>.md` under `files` and an issue URL under `github`, and it is the tool's answer
rather than a filename this command assembled: a body that prints a path the backend never wrote
sends a human to a file that does not exist. On the plan-file path, add which
sections were filled from which part of the source, the task count derived, which sections carry an
explicit none — and say plainly that the source file was **read, never moved or deleted**. Name the
next step: `/quenching:specs:develop <slug>` to take it further, or `/quenching:specs:continue` to be told what to do
next across the whole front.

**Done when:** the summary is shown.

## Invariants to never violate

- Never interrogate — no scope, task, design, or policy questions on either path.
- Never write a heading the input did not support.
- Never invent content a source plan lacks.
- Never work around `specs.py new`'s exit 2 by inventing a slug variant.