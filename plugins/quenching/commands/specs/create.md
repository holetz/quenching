---
description: Capture or create a spec. Triggers on "convert to a spec", "add to the backlog", "create a spec".
argument-hint: [what to capture, a plan path, or a plan from this session]
allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(py:*), AskUserQuestion, Skill
model: sonnet
---
# /quenching:specs:create — capture one spec, one screen, one turn

**Input**: `$ARGUMENTS` — a short description of the problem, a path to a Claude or Codex plan
file, or a plan already developed in this session (including a `<proposed_plan>` block). With no
argument and no identifiable plan in the conversation, ask what to capture.

Creates ONE spec. That locator is a spec's whole active life, so what is created here is what gets
built: this command creates it, `/quenching:specs:develop` fills its sections, `/quenching:specs:execute` builds it, and
`/quenching:specs:conclude` closes it out under the same identity.

The layout, the thirteen canonical sections, the gates, the front's on-write check and the
`cq specs` surface live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md)
§The thirteen sections §The gates and the stage-scoped explicit-none rule
§The `cq specs` tool surface §The report mold, which owns the shape step 6's report prints in.

**One screen, at the end, with the work already done.** Every field this command presumes —
subject, type, tags, `complexity` — is resolved and WRITTEN before anyone is asked anything; the
one human touchpoint is the closing screen (step 6), where what was written and what was presumed
are both on the table, next to the one open question: develop it now, or stop here.

## The one rule: effort proportional to input

This command has two inputs of wildly different richness, and exactly one behaviour: **write down
what you were given, and nothing more.**


| Input                   | What gets written                        |
| ----------------------- | ----------------------------------------- |
| a sentence              | `## Problem`, `summary:`  |
| a Claude or Codex plan, from a file or this session | every section the plan actually supports |

The same richness decides the `complexity` this command computes and writes (step 4), **inversely**:
a sentence carries the least evidence, so its definition questions still need a human, while a plan
file already answered most of them. The develop pass re-evaluates the level when it closes.


## Doctrine

- **A sentence becomes `## Problem` and `summary:` in ONE call, and stops.**
  `cq specs new` stamps the frontmatter (`slug`, `title`, `date`, `verification`) and, through the
  flags and stdin step 5 always supplies, the heading and the one-line précis together —
  never as two follow-up calls. Every other canonical heading is left ABSENT, which the
  stage-scoped explicit-none rule
  ([spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md) §The gates)
  makes legal. Writing thirteen `- none` headings here would make a fresh capture derive as
  `designed` and clear the whole ready gate without anyone having thought anything.
- **Never invent what the input lacks.** On the plan-source path, `- none — the plan recorded no alternatives` is honest; a fabricated risk is not. Where the source said nothing, either leave
the heading absent or write an explicit none that *says* the source was silent.
- **Kebab slug in the repo's declared language.** `slugify` folds accents (`criação` → `criacao`)
and `SLUG_RE` refuses (exit 2) on a bad one — derive it in the language
[communication.md](/.knowledge/standards/agents/communication.md) §Declaring it declares.
- **MERGE, never clobber.** `cq specs new` refuses (exit 2) on an existing slug. Take that as the
answer: sharpen the existing spec instead, or pick a different slug.
- **Never ask for a metadata field before the spec exists.** Subject, type, tags and `complexity`
  are each computed from the input, written WITH the capture, and shown — never gated on a question
  asked before there is a spec, a locator or a text for the human to judge. The confirmation moves
  to AFTER the write: the closing screen (step 6) is where a wrong presumption gets corrected, or —
  if nobody looks — `/quenching:specs:develop`'s first pass reviews them
  ([spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md) §Frontmatter).

## Resolving the tool

Resolve `cq specs` per
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool; branch on the **exit code** (0 ok · 1 findings · 2 refusal), never on prose.

## Workflow

### 1. Classify the input

**Prose** → the sentence path. **A path to an existing `.md`**, an explicit ask to convert a plan,
or a plan already developed in this session — including the contents of `<proposed_plan>` — → the
plan-source path. Use the complete plan available in the conversation as the source; it does not
need an intermediate file. With no argument and no identifiable plan in the conversation, ask what
to capture. Never search plan directories automatically for a candidate. This is the one decision
the CLI cannot make for you: `cq specs new`
(step 5) resolves the backend, the workspace and the seed on its own, and reports a legacy
`backlog/`/`ready/` folder as a finding rather than writing into one.
**Done when:** the path is chosen.

### 2. Derive the slug

Take a title and a one-sentence problem from the input, and derive a kebab slug in the repo's
declared language. On the plan-source path, derive it from the plan's title or goal ("Add rate
limiting to the API" → `add-api-rate-limiting`).

**The collision check is `cq specs new`'s exit 2** (`sp-slug-exists`, naming where it is) — never a
front listing first, which under `github` is a paginated fetch of every issue (2.4s measured).
**Done when:** a canonical slug is in hand.

### 3. Plan-source path only — read it, and read the bundle

Read the whole plan file, or the complete plan content from the current session, then read
[specs-create/plan-mapping.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-create/plan-mapping.md)
§The mapping and classify the plan's parts against it. When the plan is inside
`<proposed_plan>`, use that block as the plan source and ignore the wrapper itself.

**On the sentence path, skip this step entirely** — reading a bundle to write two sentences is
exactly the cost this command exists to avoid.
**Done when:** the plan's parts are classified, or the sentence path skipped this.

### 4. Resolve a subject, a type, tags and `complexity` — decide, never ask

```bash
cq specs config --json
```

Read `subjects`, `workItemTypes` and `tagCatalog`. **All three absent or empty → skip this step
whole** — most repositories declare none of them, and resolving from nothing is not a lighter
version of this step, it is the wrong step. Where only one or two are declared, resolve only
those — this is per-key, never all-or-nothing.

**A declared `subjects`:** read each key's `name`/`description`, judge which one the input best
fits — or fall back to `azurePlacement.defaultSubject` where nothing beats it — and carry the
chosen key to step 5's `--subject`. Keep the one-line reason it was chosen: the closing screen
(step 6) shows it, which is where a wrong presumption is caught, not here.

**A declared `workItemTypes`:** read each key's `description` — the same prompt material a
`tagCatalog` value already is — judge which entry the input best fits, or fall back to a declared
`default`, and carry the chosen key to step 5's `--type`. Keep the one-line reason for step 6.

**A declared `tagCatalog`:** read each tag's description — prompt material, not documentation,
written for exactly this judgment — and resolve zero or more that fit the input. A tag outside the
declared catalog is never chosen: `tagCatalog` is the closed set this judgment draws from. Carry
whatever was resolved to step 5's `--tags`; the subject's own fixed tags need not be repeated —
`cq specs new` folds them in on its own.

**Compute `complexity`** from the classification (step 1), never by interrogating: the **sentence
path yields `high`**, the **plan-source path yields `medium`**, and `low` only where the input
explicitly asks for an unattended pass. The level answers how much a human needs to be part of the
process, never the size or difficulty of the input — the four levels and what each buys are
[gears.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-cycle/gears.md) §The scale, never
transcribed here.

**A sentence yields `high` because a sentence is the least evidence a capture can hold.** The level
governs who answers the definition questions, so the poorest input is the one whose questions most
need a human — and `low` now also has the pass stamp `approved` itself, which makes it a positive
claim nobody has yet earned the right to make. Guessing upward is free; guessing downward is not
(`/quenching:specs:triage` states the same asymmetry for a ranked row's floor).

Carry the level to step 5's `--complexity`, and the one-line reason ("a sentence — the least
evidence a capture can hold, so its questions still need a human") to step 6. The close of the develop pass re-evaluates it, so a level
that turns out too small stays correctable.

**Every one of these four is a presumption, not a verdict.** Nothing here is confirmed before it is
written — step 6 is where the human sees it and can correct it in one answer.
**Done when:** a subject, a type, zero or more tags and a `complexity` level are each resolved (to
a value, or explicitly to none) and reasoned, or the step was skipped whole.

### 5. Capture in ONE call

Write `## Problem` — the problem or opportunity in the source's own framing, two sentences on the
sentence path.

**Plan-source path:** additionally write every section the plan actually supports, its own
`## <Heading>` block in the same stream. Where the plan was
silent on a section you are writing others around, write `- none — <what the source did not
record>`. Never fabricate.

**`summary:` goes in the same call** — ONE line, the précis every ranked listing prints
(`cq specs next --front --table`). Capture is the only moment at which the problem has just been
read and compressing it costs nothing. Write what the spec IS and why it matters, never what it
will do to the codebase.

Everything step 4 resolved, everything above, and the closing `validate` — **one Bash block**,
chained with `&&` per
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool:

```bash
cq specs new <slug> --title "<title>" \
  [--subject <key>] [--type <key>] [--tags "<subject's fixed tags>,<confirmed catalog tags>"] \
  --summary "<one line>" --complexity <level> <<'EOF' \
&& cq specs validate --spec <slug>
## Problem

<two sentences, or what the source supports>

## <Heading>

<plan-source path only: every other section the plan actually supports>
EOF
```

Quote the delimiter (`<<'EOF'`) so nothing in the prose is expanded by the shell. `--subject`/
`--type`/`--tags` only where step 4 resolved one; `--tags`, when present, carries the **whole**
list — the subject's own fixed tags are folded in by the tool, never lost.

**Refusals, all before anything is written:** exit 2 means the slug already exists
(`sp-slug-exists`) — say so and stop, never invent a variant. `sp-bad-complexity` means step 4's
computed level is wrong — recompute and retry the same call. `sp-stray-heading` (`source: stream`)
or `sp-write-duplicate-heading` means the stdin stream is malformed — fix the stream and retry the
same call, never split it into smaller ones. `sp-no-subject`/`sp-subject-unknown`/`sp-type-unknown`
means step 4's own resolution disagrees with the target's declared config RIGHT NOW (a race, or a
stale read) — re-run `cq specs config --json` and redo step 4 rather than retrying blind.
`sp-az-workitemtype-only-answer` means the target still declares the retired
`azurePlacement.workItemType` with no `workItemTypes` catalog resolving one — name the finding and
its remedy verbatim, and stop; migrating the target's config is not this command's call to make.
Any other backend failure (`sp-backend-unavailable`, `sp-worktree-unusable`,
`sp-worktree-failed`) is reported verbatim, naming `/quenching:specs:align`.

The chained `cq specs validate --spec <slug>` is the whole of what checking this spec means — its
own finding, if any, is named verbatim in step 6, never silently swallowed by the `&&`.
**Sentence path: nothing beyond `## Problem` is in the stream.** A plan from a
file or the current session may add only sections its source supports.
**Done when:** `cq specs new` exited 0, `validate` ran in the same call, and the locator it
returned is in hand.

### 6. The one screen — summary, correction and direction

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md \
  --sections "§The report mold" --rules-only
```

Emit §The report mold's fixed header, then one body block showing what was written and what was
presumed and why — the shape differs by path:

| Path | What the body block shows |
| --- | --- |
| sentence | `summary:`, and the drafted `## Problem` text **in full**, exactly what a human wants to check about the capture. Plus subject, type, tags and `complexity`, each with its one-line reason |
| plan source | subject, type, tags and `complexity` (each reasoned), and the **list** of sections filled with the task count. **Never the bodies** — the plan is large and the human just wrote it |

Then the next-step block — `/quenching:specs:develop <slug>` and `/quenching:specs:cycle <slug>`
named as the two forward candidates — and **one** `AskUserQuestion`, immediately after, exactly as
`/quenching:specs:execute` prints the same block and then opens its own `AskUserQuestion` at 100%:
the block is the suggestion, the question is the offer that follows it, and only
`/quenching:specs:create` and `/quenching:specs:execute` carry that second half.

Two options — the third the old screen carried, *with or without questions*, is now the
`complexity` on the screen itself:

1. **Develop now (Recommended)** — narrate, then invoke `quenching:specs:develop <slug>` through
   the **Skill** tool, with **no declared sentence at all**. Whether that pass asks anything is the
   `complexity` this capture just wrote and showed on this same screen: `high` and `xhigh` ask,
   `low` and `medium` answer from evidence and park the rest in `## Open Decisions`. The level is on
   the screen, so correcting it with `Other` is also how the human chooses to be asked or not.
2. **Stop here** — nothing more is invoked; the report above is the whole of this run.

**The correction is `Other`**, which the tool always offers and which the question text invites
explicitly ("…or answer `Other` to correct any presumption before continuing"). A correction is
applied with the deterministic verb that owns the field — `cq specs tags <slug> "<whole list>"`
(fixed tags included, or they are lost), `cq specs record <slug> priority --set
complexity=<level> --set date=<today>`, `cq specs summary <slug> "<line>"`, `cq specs section
<slug> "<Heading>" --write` — **and only then** honour whichever of the three options the same
answer also names. An `Other` answer that names no direction falls to option 2.

There is no patch-then-edit sequence to reason about: the capture already made ONE write with
everything the input supported (step 5); a correction, when there is one, is one more write; and
each bank `/quenching:specs:develop` runs makes ONE write of its own — its own batching contract
already requires this.
**Done when:** the screen has been shown and the human's answer — a correction, a direction, or
both — has been fully honoured.

## Invariants to never violate

- Never interrogate — no scope, task, design, or policy questions on either path.
- Never write a heading the input did not support.
- Never invent content a source plan lacks.
- **Never carry a plan's merge obligations into `## Tasks`.** On the plan-source path a native plan's
  "Etapas" routinely end in a version bump, a changelog entry or *update the docs*; none of them
  converts, because what the release *is* is unknowable until the last task lands.
  `/quenching:specs:conclude` owns them, along with the `/.knowledge/` the work *reveals* and the cycle's
  own closing actions. A standard the plan declares the spec will write still becomes a checkbox.
- Never work around `cq specs new`'s exit 2 by inventing a slug variant.
- **Never ask for a metadata field before the spec exists.** Subject, type, tags and `complexity`
  are resolved and written in step 5; the human is asked only after, on the closing screen.
- **Never invoke `/quenching:specs:develop` without the human having chosen a direction** on the
  closing screen — a correction alone, with no direction named, ends the run at option 3.
- **Never print the closing screen without naming what was presumed and why.** A subject, a type, a
  tag or a `complexity` level with no stated reason costs the human a re-read of the config to judge
  it; the reason is what makes disagreeing cost one second instead.
