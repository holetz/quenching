---
description: >-
  Rewrite ONE file under plugins/quenching/assets/references/ to this repo's
  prose model — the binding half first, rationale relocated under its marker and
  never deleted, no-op lines cut — and report the measured delta on the chars
  the citing bodies actually load. Triggers: "enxugar a prosa das references",
  "revisar esse reference", "marcar rules/rationale", "desinflar o custo de
  leitura das references", "tighten the references", "review the reference
  prose". Not for: cutting dead weight from a command body → /commands:tighten; minting a
  command, or its description → /quenching:components:command:new,
  /quenching:components:align; a knowledge/ standard or the OKF bundle →
  /quenching:knowledge:align; generating a documentation site → /docs:storyteller.
argument-hint: "[reference-path | --all] [--review] [--skip <path>]"
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(python3:*), Bash(grep:*), Bash(git grep:*), Bash(wc:*), Task
---

# /references:tighten — rules first, rationale marked, cost measured

**Input**: `$ARGUMENTS` — one or more paths under `plugins/quenching/assets/references/`, or
`--all` for the whole tree. `--review` reports the plan and writes nothing. `--skip <path>` drops
a file from a batch, repeatable, its path taken relative to the references root or to the repo
root — either resolves. No argument → ask which file, and stop.

A reference is read by a command body **through a `§`-address**, so its headings are its API and
its sections are its price list. This command lowers the price of the sections that are actually
addressed, without losing a single thing a future session could not reconstruct.

## The model, cited and never restated

| Rule | Owner |
| --- | --- |
| `<!-- rules -->` / `<!-- rationale -->`, marker reach, cold destination, section+children cost | [context-discipline.md](/.knowledge/standards/automation/context-discipline.md) §The rules/rationale marker convention |
| Rationale is relocated, never deleted; the bundle is never segmented into more files | [context-discipline.md](/.knowledge/standards/automation/context-discipline.md) §Two things measured and refused |
| Read the narrowest thing; a citation is a resolvable `§`-address; N sections in ONE call | [context-discipline.md](/.knowledge/standards/automation/context-discipline.md) §Open less: read the narrowest thing that answers the question |
| The no-op test, positive prescription, sediment / duplication / sprawl | [components-command-new/doctrine.md](/plugins/quenching/assets/references/components-command-new/doctrine.md) §The no-op test, §Positive prescription, §Named failure modes |
| The mention/use trap, and writing a mention as a placeholder | [prose-sweeps.md](/.knowledge/standards/quality/prose-sweeps.md) §Write the mention as a placeholder, not as an instance |
| A computed number restated in prose fans out — grep its literal form | [computed-fact-prose-fanout.md](/.knowledge/standards/quality/computed-fact-prose-fanout.md) |
| Which language the prose is written in | [communication.md](/.knowledge/standards/agents/communication.md) |

Resolve `cq` at `plugins/quenching/assets/bin/cq`, invoked by that literal quoted
path
([align/tool-resolution.md](/plugins/quenching/assets/references/align/tool-resolution.md)
§Resolving the tool).

## Workflow (one plan, one OK)

### 1. Resolve the target set and its citation map
Targets are files under `plugins/quenching/assets/references/`; `--all` globs the tree minus every
`--skip`. For each target, one grep over everything that could address it:

```bash
grep -rn -B2 -A3 "<dir>/<basename>.md" \
  plugins/quenching/commands plugins/quenching/assets/references plugins/quenching/assets/bin \
  .knowledge .claude
```

Record per target: **who cites it**, **which `§`-addresses each citer names**, and whether the
citer reads it whole or `--rules-only`. A citer under `plugins/quenching/commands/**` is **hot** —
every run of that command pays those sections; a citer that is another reference, a `knowledge/`
standard, or a Python docstring is **cold**. A citation naming the bare file with no `§` pays the
whole file: say so, because it changes what tightening this file buys.

**Done when:** every target carries its citer list, its addressed-section set, and the hot/cold
split — none of it from memory.

### 2. Measure the baseline
```bash
python3 "plugins/quenching/assets/bin/cq" components read <path>
python3 "plugins/quenching/assets/bin/cq" components read <path> --sections "<A>" --sections "<B>"
```
The index's `chars` **already includes a section's `###` children** — that number IS what the
reader returns and what the citer pays. Never add a section's prose to its children, and never
substitute `wc -c` on the file for the cited subtotal.

**Done when:** file total, per-section chars, and the addressed-set subtotal are written down as
numbers.

### 3. Classify every line into one of four moves
Read the file whole once — classification is a judgement over the argument, not a regex.

| Move | The line is | What happens to it |
| --- | --- | --- |
| **rule** | binding: name an input on which an agent behaves differently because the line exists | stays, above the marker, imperative and positive |
| **rationale** | the why: a measurement, a date, a reverted v1, the failure that motivated the rule | **relocated** below `<!-- rationale -->`, in full — never deleted, never paraphrased |
| **cut** | a no-op: restated context, praise for the approach, a rule a stricter rule already carries, a transition sentence | deleted, and quoted verbatim in the plan |
| **cite** | a fact another file owns, restated here | replaced by the owner's `§`-address |

The marker is **written once by this pass**, so no later read has to decide which sentences bind.
Mark **per sub-section**: a marker's reach ends at the next heading, so one `<!-- rationale -->`
inside a `###` would silently swallow every `###` after it.

**Done when:** every line in the file has exactly one of the four moves against it.

### 4. ONE plan, one OK
Present, per file, in this order: the addressed-section table (before-chars), the **cut** lines
verbatim, each **relocation** with its destination section, each **cite** with the owner it
resolves to, and the predicted after-chars for the addressed set only. State explicitly that
headings are unchanged — or, if one is genuinely wrong, report it with the citers that would have
to be swept and leave it alone.

Ask once, for the whole plan. `--review` stops here and reports the plan as the deliverable.

**Done when:** the plan is on screen with real before-numbers and nothing has been written.

### 5. Apply
Write the approved moves and nothing else. Two conditions bind every write:

- **A relocation destination is a section no hot citer addresses.** Rationale moved into a section
  a command body already loads has changed position without changing cost, and both files read as
  correct afterwards — only recomputing step 2 catches it.
- **The file's existing language stays.** This pass changes what the prose costs, not what it is
  written in.

**Done when:** every approved move is on disk and no unapproved edit rode along with it.

### 6. Verify against the citation map, then report what was measured
```bash
python3 "plugins/quenching/assets/bin/cq" components read <path> --sections "<A>" --sections "<B>"
python3 "plugins/quenching/assets/bin/cq" components read <path>
grep -rn "<any renamed or reworded form>" plugins/quenching .knowledge .claude
```
Every `§`-address the map collected must still resolve with exit 0 — that is the check that the
API survived the rewrite. Then re-measure and report **before → after per addressed section**,
plus the file total, as measured numbers. A pass that moved little says so; an estimated delta is
not a result.

If a command body under `plugins/quenching/commands/**` was touched at all, also run
`python3 "plugins/quenching/assets/bin/cq" components --root plugins/quenching doctor --json` and
`lint` before reporting.

**Done when:** every addressed `§` resolves, and the report carries measured before/after numbers.

## Batch mode (`--all`)

Build the citation map (step 1) **once, in this session** — it is one grep and the whole batch
shares it. Then delegate **one sub-agent per file**: that is the unit
[context-discipline.md](/.knowledge/standards/automation/context-discipline.md) §What a delegated
executor costs blesses, because a sub-agent runs cold and pays a full first read of everything it
opens. Hand each agent its own file path, its citation set, and its baseline numbers, so it
re-derives none of them.

- **First fan-out is plan-only.** Every agent returns steps 2–3 as a plan; nothing writes.
- **One table, one OK, for the whole batch.** Confirm once over all files, then fan out again —
  one agent per approved file — to apply and verify.
- **Never fan out per section**, and never let an agent widen its scope to a second file: the map
  that made the plan safe was built for one file at a time.

**Done when:** every file in the batch has an applied-or-skipped line and its measured delta, and
the skipped ones say why.

## Invariants to never violate

- **Never delete rationale to compact a file.** It is the one asset a model cannot reconstruct,
  and losing it is how a later session "fixes" a deliberate decision. Mark it and move it.
- **Never rename, delete, or re-level a heading that appears in the citation map.** Every citer
  breaks silently: the body still reads as correct and the `§` resolves to nothing.
- **Never relocate rationale into a section a hot citer already addresses** — the chars are still
  billed every turn, and nothing detects it.
- **Never report a delta that was not measured** by step 6's re-read.
- **Never write during `--review`**, and never edit a `knowledge/` standard, a command body, or a file
  outside `plugins/quenching/assets/references/` from here — report it with the command that owns
  it (`/quenching:knowledge:add`, `/commands:tighten`) instead.
