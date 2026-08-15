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
`cq specs` surface live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md)
§The `specs/` layout §The fourteen sections §The gates and the stage-scoped explicit-none rule
§The `cq specs` tool surface §The report mold, which owns the shape step 8 prints in.

## The one rule: effort proportional to input

This command has two inputs of wildly different richness, and exactly one behaviour: **write down
what you were given, and nothing more.**


| Input                   | What gets written                        |
| ----------------------- | ---------------------------------------- |
| a sentence              | `## Problem`, alone                      |
| a Claude Code plan file | every section the plan actually supports |

The same richness decides the `complexity` this command computes and proposes (step 6): a
sentence is the smallest problem a capture can hold, and a plan file is the largest — the
levels in between are the develop pass's to re-evaluate when it closes.


## Doctrine

- **A sentence becomes `## Problem` and stops.** `cq specs new` stamps the frontmatter (`slug`,
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
[communication.md](/.knowledge/standards/agents/communication.md) §Declaring it declares.
- **MERGE, never clobber.** `cq specs new` refuses (exit 2) on an existing slug. Take that as the
answer: sharpen the existing spec instead, or pick a different slug.
- **Compute `complexity`, never ask for it.** The level derives from the classification (step 1),
is proposed with the scale in front of the human, and is written only on confirmation — the
same proposal the triage sweep makes, narrowed to the one field this command computes.

## Resolving the tool

Resolve `cq specs` per
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool; branch on the **exit code** (0 ok · 1 findings · 2 refusal), never on prose.

## Workflow

### 1. Classify the input

**Prose** → the sentence path. **A path to an existing `.md`**, or an explicit ask to convert a
plan → the plan-file path. This is the one decision the CLI cannot make for you: `cq specs new`
(step 4) resolves the backend, the workspace and the seed on its own, and reports a legacy
`backlog/`/`ready/` folder as a finding rather than writing into one.
**Done when:** the path is chosen.

### 2. Derive the slug

Take a title and a one-sentence problem from the input, and derive a kebab slug in the repo's
declared language. On the plan-file path, derive it from the plan's title or goal ("Add rate
limiting to the API" → `add-api-rate-limiting`).

**The collision check is `cq specs new`'s exit 2** (`sp-slug-exists`, naming where it is) — never a
front listing first, which under `github` is a paginated fetch of every issue (2.4s measured).
**Done when:** a canonical slug is in hand.

### 3. Plan-file path only — read it, and read the bundle

Read the whole plan file, then read
[specs-create/plan-mapping.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-create/plan-mapping.md)
§The mapping and classify the plan's parts against it.

**On the sentence path, skip this step entirely** — reading a bundle to write two sentences is
exactly the cost this command exists to avoid.
**Done when:** the plan's parts are classified, or the sentence path skipped this.

### 4. Propose a subject, a type and tags, where the target declares them

```bash
cq specs config --json
```

Read `subjects`, `workItemTypes` and `tagCatalog`. **All three absent or empty → skip this step
whole** — most repositories declare none of them, and proposing from nothing is not a lighter
version of this step, it is the wrong step. Where only one or two are declared, propose only
those — this is per-key, never all-or-nothing.

**A declared `subjects`:** read each key's `name`/`description`, judge which one the input best
fits, and confirm with **one** `AskUserQuestion` naming the candidate and its description —
never silently pick one, and never skip the confirmation because a `defaultSubject` exists:
`cq specs new` falls back to it on its own where nothing was resolved, but a human still chose
this spec's content and gets the same say over where it is filed.

**A declared `workItemTypes`:** read each key's `description` — the same prompt material a
`tagCatalog` value already is — judge which entry the input best fits, and confirm with **one**
`AskUserQuestion` naming the candidate and its description, in the SAME question as the subject
where both apply. Never skip the confirmation because a `default` entry exists: `cq specs new`
falls back to it on its own where nothing was resolved, but a human still chose what kind of
work this is and gets the same say `subjects` already gets.

**A declared `tagCatalog`:** read each tag's description — this prose is prompt material, not
documentation, written for exactly this judgment — and propose zero or more that fit the input, in
the SAME
question as the subject and the type where all apply, or its own `AskUserQuestion` otherwise. A
tag outside the declared catalog is never proposed: `tagCatalog` is the closed set this judgment
draws from.

**The write is always the deterministic verb, never this command inventing its own.** The chosen
subject's key is carried to step 5's `--subject`, the chosen type's key to step 5's `--type`; any
confirmed catalog tag beyond the subject's own fixed ones is carried to step 5's follow-up
`cq specs tags` call — nothing is written here, only decided.
**Done when:** a subject (or none), a type (or none) and zero or more tags are confirmed, or the
step was skipped whole.

### 5. Create the plan

```bash
cq specs new <slug> --title "<title>" [--subject <key>] [--type <key>]
```

`--subject`/`--type` only where step 4 resolved one. Exit 2 means the slug already exists — say
so and stop, never invent a variant to get past it. `sp-no-subject`/`sp-subject-unknown`/
`sp-type-unknown` means step 4's own resolution disagrees with the target's declared config RIGHT
NOW (a race, or a stale read) — re-run `cq specs config --json` and redo step 4 rather than
retrying blind. `sp-az-workitemtype-only-answer` means the target still declares the retired
`azurePlacement.workItemType` with no `workItemTypes` catalog resolving one — name the finding
and its remedy verbatim, and stop; migrating the target's config is not this command's call to
make. Any other backend failure (`sp-backend-unavailable`, `sp-worktree-unusable`,
`sp-worktree-failed`) is reported verbatim, naming `/quenching:specs:align`.

**Where step 4 confirmed a catalog tag beyond the subject's own fixed ones**, one follow-up call,
right after this one succeeds:

```bash
cq specs tags <slug> "<subject's fixed tags>,<confirmed catalog tag>,..."
```

`cq specs tags` **replaces** the whole list, never appends — the full set, fixed tags included,
or the fixed ones `--subject` just applied are lost. Skip this call whole when no catalog tag was
confirmed beyond what `--subject` already applied.
**Done when:** the tool exited 0 and reported the locator it created, and any confirmed catalog
tag is applied.

### 6. Write the sections

Always write `## Problem` — the problem or opportunity in the source's own framing. Two sentences
is a complete answer.

```bash
cq specs section <slug> Problem --write   # body on stdin
```

**Sentence path: stop here.** Write nothing into any other heading.

**Plan-file path:** additionally write every section the plan actually supports, in ONE call —
`cq specs section <slug> "<Heading>,<Heading>…" --write`, the bodies on stdin delimited by their
own `## <Heading>` lines, the set matching what was declared. Where the plan was silent on a
section you are writing others around, write `- none — <what the source did not record>`. Never
fabricate.
**Done when:** `## Problem` is filled, and no section beyond what the input supported exists.

### 6. Compute and propose `complexity`

The level this command writes is the orchestrator's own input — each one changes the gears
plan the orchestrator will present for this spec:

| Level | What it changes in the gears plan |
| --- | --- |
| `low` | the whole cycle runs in one session on a single authorization and ends opening a PR |
| `medium` | the larger stages run isolated in sub-agents |
| `high` | the stage-by-stage stops and confirmations are kept |
| `xhigh` | at least one judgment stage (adversarial review, premortem) joins the plan |

**Compute it from the classification, never by interrogating.** The sentence path yields
`low`, the plan-file path yields `medium` — the input is all the evidence a capture is
allowed to hold, and anything else is the interrogation this command never does. The close
of the develop pass re-evaluates it, so a `medium` that grew stays honest.

**Propose it, and let the human adjust it on the same screen.** Present the computed level
with the table above, using **AskUserQuestion** with the four levels as the choice — the
human's word decides, and the proposal only starts the conversation.

Then stamp, **on the human's confirmation only**:
```bash
cq specs record <slug> priority --set complexity=<level> --set date=<today>
```
The tool merges — `level`, `criticality` and any earlier fields survive, and `date` is the
record's own, never the capture `date:`. A rejection writes nothing and stops.
**Done when:** `complexity` is on disk with the human's level, or the human declined and
nothing was written.
### 7. Check

Run `cq specs validate --spec <slug>` — the spec's own conformance, and the whole check.
**Done when:** the check is clean, or the residue is reported verbatim.

### 8. Report

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md \
  --sections "§The report mold" --rules-only
```

Emit §The report mold. Its single-spec header line carries the locator `cq specs new` returned — the
`path` field, `plans/<slug>.md` under `files` and an issue URL under `github` — which the mold
already requires be the tool's own answer rather than a filename this command assembled.

One body block, **optional**: on the plan-file path, which sections were filled from which part of
the source, the task count derived, which sections carry an explicit none — and plainly that the
source file was **read, never moved or deleted**. A one-line capture has none of this, and the block
is omitted whole rather than printed empty.

Close on §The next-step block: `/quenching:specs:develop <slug>` to take it further, or
`/quenching:specs:continue` to be told what to do next across the whole front.

**Done when:** the summary is shown.

## Invariants to never violate

- Never interrogate — no scope, task, design, or policy questions on either path.
- Never write a heading the input did not support.
- Never invent content a source plan lacks.
- **Never carry a plan's merge obligations into `## Tasks`.** On the plan-file path a native plan's
  "Etapas" routinely end in a version bump, a changelog entry or *update the docs*; none of them
  converts, because what the release *is* is unknowable until the last task lands.
  `/quenching:specs:conclude` owns them, along with the `/.knowledge/` the work *reveals* and the cycle's
  own closing actions. A standard the plan declares the spec will write still becomes a checkbox.
- Never work around `cq specs new`'s exit 2 by inventing a slug variant.
- Never interrogate the human for `complexity` — compute it from the input and propose it; a
  rejected proposal writes nothing.