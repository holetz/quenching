---
name: quenching-specs-create
description: "Capture or create a spec. Triggers on \"convert to a spec\", \"add to the backlog\", \"create a spec\". Not for: refining an existing spec → quenching-specs-develop; executing it → quenching-specs-execute."
---

<!-- GENERATED FROM plugins/quenching/commands/specs/create.md -->

# quenching-specs-create — capture one spec, one screen, one turn

**Input**: `$ARGUMENTS` — a short description of the problem, a path to a Claude or Codex plan
file, or a plan already developed in this session (including a `<proposed_plan>` block). With no
argument and no identifiable plan in the conversation, ask what to capture.

Creates ONE spec. That locator is a spec's whole active life, so what is created here is what gets
built: this command creates it, `quenching-specs-develop` fills its sections, `quenching-specs-execute` builds it, and
`quenching-specs-conclude` closes it out under the same identity.

The layout, the thirteen canonical sections, the gates, the front's on-write check and the
`cq specs` surface live in
[specs-develop/spec-driven.md](../../references/specs-develop/spec-driven.md)
§The thirteen sections §The gates and the stage-scoped explicit-none rule
§The `cq specs` tool surface §The report mold, which owns the shape step 6's report prints in.

Resolve the fields before the closing screen.

## The one rule: effort proportional to input

This command has two inputs of wildly different richness, and exactly one behaviour: **write down
what you were given, and nothing more.**


| Input                   | What gets written                        |
| ----------------------- | ----------------------------------------- |
| a sentence              | a descriptive title, `## Problem` |
| a Claude or Codex plan, from a file or this session | every section the plan actually supports |

The same richness decides the `complexity` this command computes and writes (step 4), **inversely**:
a sentence carries the least evidence, so its definition questions still need a human, while a plan
file already answered most of them. The develop pass re-evaluates the level when it closes.


## Resolving the tool

Resolve `cq specs` per
[align/tool-resolution.md](../../references/align/tool-resolution.md)
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

### 2. Choose the title

Take a descriptive title and a one-sentence problem from the input. On the plan-source path, use
the plan's title or goal ("Add rate limiting to the API" → "Add API rate limiting"). The title is
the human-readable name sent to the provider; the provider-native ID is assigned when it stores
the spec.

**Done when:** a descriptive title is in hand.

### 3. Plan-source path only — read it, and read the bundle

Read the whole plan file, or the complete plan content from the current session, then read
[specs-create/plan-mapping.md](../../references/specs-create/plan-mapping.md)
§The mapping and classify the plan's parts against it. When the plan is inside
`<proposed_plan>`, use that block as the plan source and ignore the wrapper itself.

**On the sentence path, skip this step entirely** — reading a bundle to write two sentences is
exactly the cost this command exists to avoid.
**Done when:** the plan's parts are classified, or the sentence path skipped this.

### 4. Resolve a subject, a type, tags and `complexity` — decide, never ask

```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs config --json
```

Read `subjects`, `workItemTypes` and `tagCatalog`. **All three absent or empty → skip only the
metadata lookups** — most repositories declare none of them; still compute `complexity` below.
Where only one or two are declared, resolve only those — this is per-key, never all-or-nothing.

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

**Compute `complexity`** from the classification (step 1), never by interrogating: both the
**sentence path and the plan-source path yield `medium`**, and `low` only where the input explicitly
asks for an unattended pass. The level answers how much a human needs to be part of the process,
never the size or difficulty of the input — the four levels and what each buys are
[gears.md](../../references/specs-cycle/gears.md) §The scale, never
transcribed here.

**A capture presumes `medium` because that is the level whose judgment is deferred.** `medium` puts
a human on every question of the definition and then **recommends** whether the spec needs arguing
with — judged against a composed spec rather than guessed from a sentence, which is the one input
that could never support the guess. Presuming `high` here would run a refine pass over every
sentence anyone captured, on no evidence that it was needed; presuming `low` would claim the pass
may stamp its own `approved`, which nobody has yet earned the right to make. Guessing upward costs
a refine nobody asked for; guessing downward costs a spec built on nobody's word
(`quenching-specs-triage` states the same asymmetry for a ranked row's floor).

Carry the level to step 5's `--complexity`, and the one-line reason ("a capture, so a human answers
the definition and the close recommends whether it needs arguing with") to step 6. The close of the
develop pass re-evaluates it, so a level that turns out too small stays correctable.

**Every one of these four is a presumption, not a verdict.** Nothing here is confirmed before it is
written — step 6 is where the human sees it and can correct it in one answer.
**Done when:** a subject, a type, zero or more tags and a `complexity` level are each resolved (to
a value, or explicitly to none) and reasoned; metadata may be absent, but `complexity` is always
resolved.

### 5. Capture in ONE call

Write `## Problem` — the problem or opportunity in the source's own framing, two sentences on the
sentence path.

**Plan-source path:** additionally write every section the plan actually supports, its own
`## <Heading>` block in the same stream. Where the plan was
silent on a section you are writing others around, write `- none — <what the source did not
record>`. Never fabricate.

Everything step 4 resolved, everything above, and the closing `validate` — **one Bash block**,
chained with `&&` per
[align/tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool:

```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs new "<title>" \
  [--subject <key>] [--type <key>] [--tags "<subject's fixed tags>,<confirmed catalog tags>"] \
  --complexity <level> <<'EOF' \
&& python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs validate --spec <id>
## Problem

<two sentences, or what the source supports>

## <Heading>

<plan-source path only: every other section the plan actually supports>
EOF
```

Quote the delimiter (`<<'EOF'`) so nothing in the prose is expanded by the shell. `--subject`/
`--type`/`--tags` only where step 4 resolved one; `--tags`, when present, carries the **whole**
list — the subject's own fixed tags are folded in by the tool, never lost.

**Refusals, all before anything is written:** `sp-bad-complexity` means step 4's computed level
is wrong — recompute and retry the same call. `sp-stray-heading` (`source: stream`)
or `sp-write-duplicate-heading` means the stdin stream is malformed — fix the stream and retry the
same call, never split it into smaller ones. `sp-no-subject`/`sp-subject-unknown`/`sp-type-unknown`
means step 4's own resolution disagrees with the target's declared config RIGHT NOW (a race, or a
stale read) — re-run `cq specs config --json` and redo step 4 rather than retrying blind.
`sp-az-workitemtype-only-answer` means the target still declares the retired
`azurePlacement.workItemType` with no `workItemTypes` catalog resolving one — name the finding and
its remedy verbatim, and stop; migrating the target's config is not this command's call to make.
Any other backend failure (`sp-backend-unavailable`, `sp-worktree-unusable`,
`sp-worktree-failed`) is reported verbatim, with the finding's own declared remedy and nothing
invented beside it.

The chained `cq specs validate --spec <id>` is the whole of what checking this spec means — its
own finding, if any, is named verbatim in step 6, never silently swallowed by the `&&`.
**Sentence path: nothing beyond `## Problem` is in the stream.** A plan from a
file or the current session may add only sections its source supports.
**Done when:** `cq specs new` exited 0, `validate` ran in the same call, and the locator it
returned is in hand.

### 6. The one screen — capture, correction and direction

```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" components read ../../references/specs-develop/spec-driven.md \
  --sections "§The report mold" --rules-only
```

Emit §The report mold's fixed header, then one body block showing what was written and what was
presumed and why — the shape differs by path:

| Path | What the body block shows |
| --- | --- |
| sentence | the descriptive title and drafted `## Problem` text **in full**, exactly what a human wants to check about the capture. Plus subject, type, tags and `complexity`, each with its one-line reason |
| plan source | subject, type, tags and `complexity` (each reasoned), and the **list** of sections filled with the task count. **Never the bodies** — the plan is large and the human just wrote it |

Then the next-step block — `quenching-specs-develop <id>` and `quenching-specs-cycle <id>`
named as the two forward candidates — and **one** `AskUserQuestion`, immediately after, exactly as
`quenching-specs-execute` prints the same block and then opens its own `AskUserQuestion` at 100%:
the block is the suggestion, the question is the offer that follows it, and only
`quenching-specs-create` and `quenching-specs-execute` carry that second half.

Two options — the third the old screen carried, *with or without questions*, is now the
`complexity` on the screen itself:

1. **Develop now (Recommended)** — narrate, then invoke `quenching:specs:develop <id>` through
   the **Skill** tool, with **no declared sentence at all**. Whether that pass asks anything is the
   `complexity` this capture just wrote and showed on this same screen: `high` and `xhigh` ask,
   `low` and `medium` answer from evidence and park the rest in `## Open Decisions`. The level is on
   the screen, so correcting it with `Other` is also how the human chooses to be asked or not.
2. **Stop here** — nothing more is invoked; the report above is the whole of this run.

**The correction is `Other`**, which the tool always offers and which the question text invites
explicitly ("…or answer `Other` to correct any presumption before continuing"). A correction is
applied with the deterministic verb that owns the field — `cq specs tags <id> "<whole list>"`
(fixed tags included, or they are lost), `cq specs record <id> priority --set
complexity=<level> --set date=<today>`, `cq specs section <id> "<Heading>" --write` — **and only
then** honour whichever of the two options the same answer also names. An `Other` answer that names
no direction falls to option 2.

There is no patch-then-edit sequence to reason about: the capture already made ONE write with
everything the input supported (step 5); a correction, when there is one, is one more write; and
and `quenching-specs-develop` makes ONE write per pass — its own batching contract already
requires this.
**Done when:** the screen has been shown and the human's answer — a correction, a direction, or
both — has been fully honoured.

## Invariants to never violate

- Never interrogate — no scope, task, design, or policy questions on either path.
- Never write a heading the input did not support.
- Never invent content a source plan lacks.
- **Never carry a plan's merge obligations into `## Tasks`.** On the plan-source path a native plan's
  "Etapas" routinely end in a version bump, a changelog entry or *update the docs*; none of them
  converts, because what the release *is* is unknowable until the last task lands.
  `quenching-specs-conclude` owns them, along with the `/docs/` the work *reveals* and the cycle's
  own closing actions. A standard the plan declares the spec will write still becomes a checkbox.
- Never accept a generated title or a `titleize` fallback when the input lacks a descriptive title.
- **Never ask for a metadata field before the spec exists.** Subject, type, tags and `complexity`
  are resolved and written in step 5; the human is asked only after, on the closing screen.
- **Never invoke `quenching-specs-develop` without the human having chosen a direction** on the
  closing screen — a correction alone, with no direction named, ends the run at option 2.
- **Never print the closing screen without naming what was presumed and why.** A subject, a type, a
  tag or a `complexity` level with no stated reason costs the human a re-read of the config to judge
  it; the reason is what makes disagreeing cost one second instead.
