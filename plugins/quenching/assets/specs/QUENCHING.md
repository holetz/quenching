<!-- quenching v<VERSION> · operator manual · generated payload.
     Refreshed by /specs:align (or /align). Edit the plugin asset, not this copy —
     a run with a newer plugin overwrites this file. Remove this banner to keep
     your own version: the align will then leave it alone and report it. -->

# Operating the spec-driven plan workspace

This is `specs/` — where a change to this product is **thought through, specified, built, and
recorded** before it becomes history. Its unit of work is a **spec**: ONE markdown file that
lives through its whole lifecycle in a single folder, enriched in place, built on an isolated
branch, and archived when it closes. It is operated through the `/specs:*` commands of the
[`quenching`](https://github.com/eloysekonell/quenching) plugin.

This file is the **operator manual** for that workspace. Its sibling
`../docs/QUENCHING.md` covers the knowledge base; the two are connected by a deliberate bridge
described in §6.

**Fully native — nothing external to install.** This front has **no npm package, no Node
runtime, no external CLI, no `config.yaml`, no delta format, and no separate spec store**. The
one tool is `specs.py` — a single stdlib-only Python script (the same mold as the OKF validator),
installed into `.claude/hooks/specs.py` by `/specs:align`. All you need is Python:

```bash
python3 --version           # or `py --version` on Windows
```

---

## 1. I want to… → run this

| I want to… | Command |
| --- | --- |
| Be told which spec now, and which command next | `/specs:continue` |
| See where everything stands, changing nothing | `/specs:status` |
| Park an idea — or bring in a Claude Code plan file | `/specs:create` |
| Think it through, fill it out, argue with it, or approve it | `/specs:develop` |
| Take a branch or worktree for it — at any stage | `/specs:isolate` |
| Build it, one verified commit per task | `/specs:execute` |
| Close it out — review, archive, distil, then merge | `/specs:conclude` |
| Rank everything that is parked | `/specs:triage` |
| Fix the workspace itself — scaffold, filenames, the v2/v1 fold | `/specs:align` |
| Align **every** front (`docs/`, `specs/`, `.claude/`) | `/align` |

> `/specs:develop` is the short form of `/quenching:specs:develop`; use the long form if
> another plugin claims the namespace. Claude also routes to these commands from prose ("flesh
> out the session-tokens spec") — the command is the explicit entry point.

**Eight commands, flat.** The previous surface had eleven: `capture` + `from-claude` folded into
**`create`** (effort proportional to input, never an interrogation); `explore` + `refine` + the
per-spec half of `triage` folded into **`develop`** (one loop whose question bank follows the
spec's derived stage); `apply` became **`execute`** (it stops at the last commit); `archive`
grew the branch review and the merge and became **`conclude`**; and `align-and-update` was
deleted — `/specs:align` now opens with a probe, so running it on a clean workspace costs a
couple of tool calls and says so. **`continue`** is new: the router that answers "which spec
now, and which command?" without you memorizing any of this.

---

## 2. The layout

The front lives at the **repo root** — never inside `docs/`. **One spec is ONE markdown file for
its entire lifecycle.** Phases enrich it; they never split it.

```
specs/
  QUENCHING.md              # this manual (payload — not a spec)
  plans/                    # a spec's WHOLE pre-archive life — defined, approved, building
    index.md                # derived listing (generated zone, frontmatter-free)
    2026-07-25-<slug>.md    # one spec per file
  archive/                  # done or abandoned, told apart by `outcome:` frontmatter
    2026-06-30-<slug>.md
```

**One active folder, one hop.** A spec sits in `plans/` from capture to completion and moves
exactly once, to `archive/`, when it closes. There is no `backlog/` and no `ready/`: everything
that split used to imply about completeness is **derived** from the spec's own sections, and the
one fact it carried that no derivation reproduces — *a human said go* — is now the
`approved: {date}` frontmatter record (§7).

**Every file is `YYYY-MM-DD-<slug>.md`, in both folders.** The date records when the spec was
**born** and is stamped once, at creation — archiving moves the file and never renames it. So the
basename is stable for the whole lifecycle, `git log --follow` reads as one history, and a plain
`ls` of either folder is chronological: a file listing IS the status view, and no file listing
reads frontmatter.

**Identity is the slug, not the path.** Every command and cross-reference names the bare slug;
`specs.py` resolves it to the one file ending in `-<slug>.md`, wherever it sits. Two matches is a
refusal, never a guess.

**One truth, not two.** There is no "main spec" store and no proposed "delta" to reconcile with
it. A spec writes its durable rule **directly** into the OKF `docs/` bundle — a decision into
`docs/standards/` (honestly `authority`-graded), an understanding into `docs/knowledge/` — as it
is built. Isolation-while-building is what a **branch or worktree** gives you, with real merge,
history, and reversion — not a markdown reimplementation of version control.

---

## 3. The lifecycle

One file, one move, and a frontmatter that narrates the history.

```
   create                enrich, in place                approve            build             close
      │                        │                            │                 │                  │
      ▼                        ▼                            ▼                 ▼                  ▼
  plans/2026-07-25-<slug>.md ──────────────────────────────────────────────────────►  archive/…-<slug>.md
      │   ## Problem           derived stages:            approved: {date}   branch: {base,work}   │
      │      ↓ ## Proposal     captured → proposed →      (develop offers    per-task subject: …   │
      │      ↓ ## Design       designed → refined →        it at the gate;   blocked → - [!] …     │
      │      ↓ refined:        ready (the ten gate         execute asks      reviewed: {date}      │
      │                        sections, computed)         inline)           merge: {strategy,     │
      │                                                                      subject}             │
      │  a spec that will NOT be built goes straight to conclude             outcome: done │ abandoned
      └──────────────────────────────────────────────────────────────────────────────┐
                                                                                     ▼
                                                                   OKF distillation (offered)
                                                            docs/standards · knowledge · glossary
```

**`ready` is derived, and the gate is a floor.** A spec is `ready` when the ten definition
sections are filled — the nine `## Problem` … `## Risks` plus `## Tasks`. An empty section is
answered with an explicit `- none — <reason>`; a heading present with an empty body is malformed.
The gate refuses nothing by itself: it is what `execute` reports against when there is no task to
hand out.

**`approved` is the human OK.** `develop` offers the stamp when the gate is met; `execute` on an
unapproved spec never refuses — it shows what the spec commits to, asks inline, stamps on a yes.
Section completeness can never stand in for it, because an agent can satisfy every section itself.

**Archiving refuses to lie.** Closing as `done` while `- [ ]` boxes remain exits 2 and lists them
(overridable with `--force`). `outcome: abandoned` is always allowed — open tasks are exactly
what you expect when closing out work that will not be built.

**There is no ledger and no task inbox.** The thing you park and the thing you build are the same
file. A finished spec is in `archive/` with `outcome: done`; a dropped one with
`outcome: abandoned`; `git log --follow` is the rest of the story.

Not every spec needs every stage: one already clear in scope is created, filled out, approved and
built in a single sitting.

---

## 4. The commands, one by one

### `/specs:continue` — which spec now, and which command?

The router. One `specs.py next --front` call ranks every candidate — executing first, then
closest to done, then priority, then age — with a one-line reason per row, and hands off to the
one command that fits: `develop` for a spec with gate gaps, `execute` for an approved one with
open tasks, `conclude` for one whose boxes are all ticked, `triage` when nothing carries a
ranking to stand on. It never builds, edits, or closes anything itself.

### `/specs:status` — look, change nothing

The read-only view. Reports every spec by derived stage with task progress, each spec's
frontmatter records as the history they narrate (ranked, interrogated, approved, built, reviewed,
merged, closed), and the verifier results (`specs.py doctor` / `validate`) — split into what
`/specs:align` would fix on one OK, what a cycle command closes, and what neither closes because
it needs you. It speaks the sweep's own `sp-*` vocabulary, so it doubles as an honest dry run.

### `/specs:create` — park ONE spec, or convert a plan file

Effort proportional to input, **zero interrogation**. A sentence becomes
`plans/YYYY-MM-DD-<slug>.md` carrying `## Problem` and nothing else, in seconds — every other
heading left absent, a *not-yet*, which is what keeps a fresh capture from deriving as `designed`.
A Claude Code plan file (`~/.claude/plans/*.md`, or a path you give it) becomes every section it
actually supports — mapped, never invented — so the work gains the lifecycle and the archive-time
distillation instead of dying in a one-shot file. The native file is read, never moved or deleted.
The date is stamped here and **never rewritten**.

### `/specs:develop` — think it through, fill it out, argue with it, approve it

One loop, one question at a time with an inline recommendation, answers accumulated and applied
in **a single confirmed edit** — abandon it halfway and the spec is exactly as it was. The
spec's own derived stage picks the question bank:

| The spec is… | `develop` asks |
| --- | --- |
| raw (only `## Problem`) | generative — what is this, why now, what shape, what is excluded |
| `proposed` | adversarial — alternatives, premortem, critique |
| `designed` | the gate's gaps — `## Impact`, `## Validation`, the `verification` policy |
| carrying open `## Discoveries` | resolve each — promote to its own spec, or dismiss with a reason |
| at the gate | **the `approved` stamp** — your OK to build |

It reads the relevant `docs/standards/` and the glossary first, so wording does not contradict a
rule you already agreed on. A real interrogation records `refined: {mode, date}`, which clears
the `sp-unrefined` warning — a warning, never a gate: **a spec may always be built unrefined.**
It never edits code, and it never invents an explicit none on your behalf.

### `/specs:isolate` — take a branch, at any stage

Isolation is not a privilege of building. Creating and developing a spec also write into
`plans/` and dirty your tree, and sometimes a spec should be born on the branch that will carry
its work — so this command takes **or reports** isolation for one spec whenever you want it.

It offers a **branch** (`plan/<slug>`, the default) or a **worktree** beside the repo, commits an
uncommitted spec file onto the new branch so the base keeps no trace of it, and stamps
`branch: {base, work}`. `base` is captured while it is still true: after a merge, git cannot say
what the branch was cut from.

**Asking is a complete use of it.** "Am I isolated?" costs a few `git` reads and writes nothing.
A spec whose branch is already alive is never given a second one — you are offered a checkout or
a worktree over the existing branch instead.

`/specs:execute` delegates here rather than reimplementing it; `/specs:create` and
`/specs:develop` name it when you ask, and never volunteer it. **It never merges** — the merge
stays inside `/specs:conclude`, behind that command's review and archive gates.

### `/specs:execute` — build it, prove it, commit it

**It refuses to start on a dirty tree** — it commits one task at a time, and a commit cannot tell
your task's diff from an unrelated edit already sitting there. It offers isolation — a branch or
a worktree — and records the choice as `branch: {base, work}`, because after the merge git cannot
say what the base was.

Per task it writes the code, runs that task's `verify:` under the spec's declared policy,
self-reviews the diff (reuse · useless defense · obvious comment · dead code), **ticks the box
with the subject of the commit it is about to make** — `specs.py task --check <id> --subject
"<line>"` — and then commits the code and the ticked box together. One task is exactly one commit,
and no bookkeeping commit follows it: a subject is known before its commit, so the box can ride
inside it. Your repo's own commit conventions govern when declared
(`docs/standards/git/**`, read if present, **never installed**); otherwise the plugin's default
subject is `plan/<slug>: <id> <title>`.

When attempts stop converging it writes the task **blocked, in the file**:

```markdown
- [!] 2.3 Implement the gate check — blocked: waiting on the vendor SDK
```

`next` skips it and moves on, so one bad task never stalls the spec. There is **no attempt
counter** — a written reason stops the same runaway loop while being legible to whoever unblocks
it.

It reads the touched subjects' `standards/` as **binding contracts** and pauses when the spec
conflicts with one rather than quietly picking a side. It writes the `docs/standards/` doc a task
**explicitly names**; everything else the work reveals costs one line in `## Discoveries`
(`specs.py discover`) and no authoring. It stops at the last commit — the branch review, the
merge, and the archive are `/specs:conclude`, which is what makes a half-finished build
resumable.

What it will **never** do, whatever the pressure: disable or delete a test, edit the check so it
stops failing, or pass `--no-verify`. A green checkbox has to mean something.

### `/specs:conclude` — close it out, shipped or dropped

Four stages, resumable — the `reviewed`, `merge` and `outcome` records plus git say which already
ran, so a second call picks up where the first stopped:

1. **Review the whole branch** — the judgment no per-task diff could make: coherence, layering,
   two tasks solving the same problem differently. Records `reviewed: {date}`.
2. **Write the emergent `docs/`** — the standards and knowledge the work *revealed* (resolved
   from `## Discoveries`), as opposed to the declared docs `execute` already wrote.
3. **Archive + distil** — `outcome: done` refuses while boxes are open (`--force` if you know
   why); `abandoned` is always allowed and distils **nothing as adopted** — at most a narrow
   `authority: background` note. The outcome is **your word**, never inferred from progress or
   staleness. Both the archive move and the distillation land on the **work branch**.
4. **Merge — the last action, without exception.** Strategy offered, never chosen for you: merge
   commit (default), squash, rebase, or fast-forward. `merge: {strategy, subject}` is stamped on
   the branch *before* the merge, so **nothing is ever committed to the base after it** and one
   merge carries the code, the emergent docs, the archived spec and the distillation together.
   **On a squash it offers to keep the branch**, because the per-task commits survive only there.

### `/specs:triage` — rank the whole front

Reads every spec's frontmatter and derived stage directly — no sub-agents — and proposes **one**
ordered table with a one-line reason per row. On one OK it writes each spec's
`priority: {level, criticality, complexity, date}` record and nothing else, merging with (never
clobbering) a ranking you set yourself. Its output is what `continue` stands on. It never removes
a spec, never infers completion, never treats staleness as abandonment.

### `/specs:align` — force the workspace into shape

The sweep, probe-first: it opens with `specs.py doctor` + `validate`, and a conformant workspace
costs those two calls and stops. Otherwise: scaffolds `specs/` when absent, installs `specs.py`
and this manual, **folds an older `backlog/` + `ready/` layout into `plans/`** and a v1
three-file layout into single files (`specs.py migrate`), normalizes filenames and slugs, stamps
missing frontmatter, regenerates the listing zone, and migrates a legacy `openspec/` workspace
(§10). One plan, one OK; a rename whose blast radius reaches code confirms on its own.

**It aligns conformance and only *reports* the cycle.** An empty section, a complete spec
awaiting approval, an unresolved discovery — each is reported with the command that owns it.
Writing even `- none — <reason>` would be authoring an answer only you can give.

---

## 5. The boundary that must never blur

| Store | Answers | Owned by |
| --- | --- | --- |
| `specs/plans/` | a change **in flight** — its problem, design, and task list | the `/specs:*` commands, until it archives |
| `docs/standards/` | **HOW we build** (binding contracts, current behavior) | the `/docs:*` commands; a spec writes here directly |
| `specs/archive/` | what was **done or dropped**, told apart by `outcome:` | `/specs:conclude` |
| `docs/vision/` | settled **direction**, no deadline | `/docs:add` |

Content is never duplicated across them. A spec's rationale and considered alternatives live in
its `## Design` **while it is active**, and distill into a `standard` at conclude time. The spec
**is** the change: what it proves out lands in `docs/standards/` as it is built — there is no
second store for it to duplicate.

---

## 6. The OKF bridge

This front reads the `../docs/QUENCHING.md` knowledge bundle as context going in, and distils
durable knowledge back out — but, being native, it writes into `docs/` **directly** rather than
through a spec-sync:

- **Going in** — `create`, `develop`, and `execute` read `docs/standards/` (binding),
  `docs/knowledge/`, and `docs/knowledge/glossary.md` (vocabulary) before writing anything, so
  artifacts do not contradict rules the repo already agreed on.
- **While building** — `execute` writes the `docs/standards/` doc a task explicitly names,
  honestly `authority`-graded (`background` for agreed-but-unproven, `current` once implemented
  and proved). Everything else the work reveals is one `## Discoveries` line.
- **Going out** — `conclude` writes the emergent docs and offers the **distillation pass** for
  the remaining by-products (a term, an understanding, a follow-up spec). Durable knowledge
  crosses; the archived spec stays as history.

If the target has no OKF bundle (`docs/index.md` with `okf_version`), the standards-writing and
the distillation are skipped, and `/docs:align` is suggested once.

---

## 7. The spec file contract

One file per spec, flat, no subfolders, the same shape in both folders.

```yaml
---
slug: session-tokens          # required — the identity key every command names
title: <one line>             # required
verification: per-task        # required — per-task | per-section | end-of-plan
priority: {level: 2, criticality: high, complexity: medium, date: 2026-07-24}   # triage's ranking
refined: {mode: premortem, date: 2026-07-25}   # once a real interrogation has run
approved: {date: 2026-07-26}                   # a human said go — develop offers it, execute asks inline
branch: {base: main, work: plan/session-tokens} # stamped when isolation is taken; write-once
reviewed: {date: 2026-07-28}                   # a human read the whole branch diff
merge: {strategy: merge-commit, commit: abc1234} # the chosen strategy and its resulting sha
outcome: done                                  # stamped at archive — done | abandoned
---
```

**Frontmatter records human judgments; everything else is derived.** There is no `created` field
(the filename's date prefix is that fact), no `phase` field (the folder is that fact), and no
`ready` flag (the ten gate sections are that fact). Read top to bottom, the records narrate the
spec's history in order: ranked, interrogated, approved, built, reviewed, merged, closed. A
record is written only by its owning command; `approved`, `branch`, `merge` and `outcome` are
write-once — rewriting one would falsify a fact that already happened. A spec carries no OKF
`type:` — it is not a concept doc, it lives outside the bundle, and `specs.py validate` is what
checks it.

Fourteen canonical headings, in this order: `## Overview`, `## Problem`, `## Proposal`,
`## Out of Scope`, `## Impact`, `## Validation`, `## Design`, `## Alternatives Considered`,
`## Open Decisions`, `## Risks`, `## Handoff`, `## Tasks`, `## Discoveries`, `## Outcome`.
**Headings are a parsed contract** — canonical English, exactly as written; body prose follows
your repo's language. A heading outside the set is a stray and `validate` flags it.

A heading is required only once **its own gate** is reached — before that, its absence is a
*not-yet*, not an omission. That is what keeps a freshly created spec four lines long instead of
a fourteen-heading skeleton.

Two sections are load-bearing for machinery, not just for thinking: `## Validation` is the
fallback for a task with no `verify:` line, and `## Impact` is the one machine-parsed
declaration.

`## Overview` is warn-only, like `## Handoff` — never one of the ten sections the `ready` gate
requires. It sits first, ahead of `## Problem`, and is written **last**: `/specs:develop` fills
it once the other sections have settled, because connecting them is only possible after they
exist. An empty one on a spec that otherwise meets the gate is reported as `sp-overview-missing`.

A completed task carries its implementing commit; a blocked one carries its reason — both in the
task line's own metadata grammar, never in a sidecar:

```markdown
- [x] 3.2 Validate the token — files: src/auth.py — verify: pytest tests/auth — commit: abc1234
- [!] 2.3 Implement the gate check — blocked: waiting on the vendor SDK
```

`plans/index.md` carries a `<!-- BEGIN GENERATED -->` … `<!-- END GENERATED -->` zone rebuilt
**deterministically** by `specs.py plans reindex`: counts, then one table per **derived stage**
(oldest-first inside each, so stale specs surface). **Never hand-edit inside that zone** and
never add frontmatter to `plans/index.md`.

---

## 8. The `specs.py` tool

A stdlib-only Python script, no dependencies. Every subcommand takes `--json` and returns
**strict exit codes**: **0** ok · **1** findings · **2** refusal. A command branches on the exit
code and the JSON, never on prose.

| Command | Use |
| --- | --- |
| `specs.py new <slug> [--title T] [--verification P]` | create in `plans/` with `## Problem` alone; stamps the date ONCE |
| `specs.py list [--json]` | every spec, grouped by folder and derived stage |
| `specs.py status --spec <slug> [--json]` | sections, stage, tasks, the frontmatter records, commits, and the gate's outstanding list |
| `specs.py section <slug> "<Heading>" [--write]` | read or write ONE section; `--write` creates it in canonical position |
| `specs.py next --spec <slug> [--json]` | THE single next action for one spec; skips `[!]` |
| `specs.py next --front [--json]` | the ranked candidate list with a reason per row — the only place ranking logic lives |
| `specs.py task --spec <slug> --check ID [--commit SHA] \| --uncheck ID \| --block ID --reason MSG` | flip a checkbox mechanically; `--commit` writes the sha onto the task line |
| `specs.py discover <slug> "<text>"` | append one line to `## Discoveries` |
| `specs.py parallel --spec <slug> [--json]` | prove a `[P]` group's `files:` are disjoint; exit 1 if not |
| `specs.py plans reindex` | regenerate the `plans/index.md` GENERATED zone by derived stage |
| `specs.py promote <slug> [--outcome done\|abandoned] [--force]` | the one hop, `plans/` → `archive/`; **exit 2** with what is missing |
| `specs.py validate [--spec <slug>]` | the canonical heading set, the gates, filenames, the records, the `sp-*` codes |
| `specs.py doctor` | workspace shape, v2/v1 leftovers; remedies **declared** for the command to apply |
| `specs.py migrate [--dry-run]` | one-way fold to the current layout (v2 `backlog/`+`ready/` → `plans/`; v1 three-file → one file); **exit 2** if already current |

There is no `init` (scaffold is an asset copy), no `store`, no `profiles`, no telemetry, and no
delta parser. `/specs:align` installs the script into `.claude/hooks/specs.py`; run it yourself
any time:

```bash
python3 .claude/hooks/specs.py doctor --json      # workspace health (and legacy detection)
python3 .claude/hooks/specs.py list --json        # every spec, by folder and stage
```

**`--block` requires `--reason`.** The tool refuses without one: a blocked task with no reason is
exactly the hidden state the marker replaced.

---

## 9. Recipes and troubleshooting

**Setting the workspace up.** `/specs:align` — it scaffolds `plans/` + `archive/`, installs
`specs.py`, and folds any older layout. No package to `npm i` first.

**From idea to shipped.** `/specs:create` → `/specs:develop` until the gate is met and the
`approved` stamp is offered → `/specs:execute` (accept the branch isolation) → `/specs:conclude`.

**Coming back after a while.** `/specs:continue` — it ranks the front and names the one command
to run next. Or `/specs:status` for the full picture without touching anything. Or just
`ls specs/plans`: the listing IS the status view, oldest first.

**Deciding not to build something.** `/specs:conclude` with `outcome: abandoned`, never `done`.
Done distils its decisions as adopted knowledge; abandoned does not.

**Health check.** `specs.py doctor && specs.py validate`, plus
`okf-validate.py specs/plans --listing-root` for the **listing**. Read each for what it owns: a
spec carries no OKF `type:` (it is not a concept doc), so the bundle validator checks `index.md`
and `specs.py validate` checks the specs.

| Symptom | What is going on |
| --- | --- |
| `list` exits 2 and every row says `legacy: true` | The workspace still has the old `backlog/` + `ready/` folders. Run `/specs:align` — it drives `specs.py migrate`, which folds both into `plans/` without renaming a single file. |
| `list` says the workspace is empty, but there are files in `specs/` | It is a **v1 workspace** (one folder per plan). `specs.py doctor` detects the leftovers and declares `migrate` as the remedy — or just `/specs:align`. |
| A freshly created spec shows as `designed` | Someone stamped all fourteen headings at creation. An explicit none counts as *filled*, so a skeleton derives as designed. `create` writes `## Problem` alone on purpose. |
| `execute` asks me to approve a spec I already promoted | The old `ready/` folder recorded your OK; the record vocabulary replaced it. Say yes once — it stamps `approved: {date}` and never asks again. |
| `promote` refuses with open boxes | The outcome is `done` and the work is not. Finish them, pass `--force` if you know why, or switch to `outcome: abandoned`. |
| Two commands both refuse with "slug matches 2 files" | Two specs resolve to the same slug. Identity IS the slug — rename one. |
| A task went quiet and nothing says why | It should not have. `--block` requires `--reason`, and the reason is written into the line: `- [!] 2.3 … — blocked: <why>`. |
| `plans/index.md` disagrees with the files | Its generated zone is stale — `specs.py plans reindex` rebuilds it from disk. Never hand-edit inside the markers. |
| An archived spec's `commit:` shas do not resolve | The spec was squash-merged and its branch deleted. The `merge:` record says which strategy ran; keep the branch next time — `conclude` offers exactly that on a squash. |
| `python3: command not found` | Install Python 3, or use `py` on Windows. This front needs nothing else — no Node, no npm package. |
| I still have an `openspec/` folder | Legacy external-CLI workspace. `/specs:align` migrates it one-way (§10). |

---

## 10. Upgrading, and migrating older workspaces

### Upgrading a repo that still holds the v2 `backlog/` + `ready/` layout

**You must re-align manually — nothing migrates on its own.** The plugin ships to other
repositories, and Claude Code applies an upgrade from the `VERSION`/`plugin.json` bump — so a
repo can wake up with the current commands over the older folders, having run no migration.

The exposure is loud rather than silent this time: `specs.py list` still reads the old folders,
but **exits 2** and marks every row `legacy: true` until the fold runs. The fix is one command —
**`/specs:align`** — which drives `specs.py migrate`: every file in `backlog/` and `ready/` moves
into `plans/` with its basename unchanged, `archive/**` is never touched, and an already-current
workspace exits 2. Nothing is renamed, so every slug, date, and cross-reference survives. The
completeness `ready/` used to imply is recomputed from the sections; the OK it used to record is
whatever `approved` records say — a spec you promoted but never built simply gets asked once by
`execute`.

### Upgrading a repo that still holds a v1 three-file workspace

v1 kept one **folder** per plan (`proposal.md` / `design.md` / `tasks.md` + a `.specs.json`
sidecar). **v2+ `list` reads a v1 workspace as EMPTY, not as wrong format** — `specs.py doctor`
is the one command that sees it and declares the remedy. `/specs:align` drives the same one-way
fold: each plan folder becomes one file (`## Why`→`## Problem`, `## What Changes`→`## Proposal`,
`## Context`+`## Decisions`→`## Design`, `tasks.md`→`## Tasks` with every checkbox state
preserved); the birth date comes from `.specs.json`'s `created`, falling back to the path's first
commit — **never invented**; a section the v1 plan never recorded is written
`- none — not recorded in the v1 plan`; a plan folder still holding any other file is **kept, not
deleted**, and reported; and **`specs/archive/**` is never touched** — it stays as history, in
v1 shape, deliberately.

### Migrating from a legacy `openspec/` workspace

Earlier still, this front was driven by the external `@fission-ai/openspec` CLI and lived in
`openspec/`. If this repo still has one, `/specs:align` migrates it **one-way** into the native
`specs/` front, inside its single plan → one OK:

- `openspec/` → `specs/`; each change folder becomes a spec file; `changes/archive/` →
  `specs/archive/` (the delta was the only reason for the `changes/` nesting).
- Each `openspec/specs/<capability>/spec.md` is **folded into `docs/standards/`** — the cut is
  chosen by you in the spec, never inferred. No OKF bundle → the fold stops and `/docs:align` is
  suggested first.
- The CLI scaffolding is dropped: `config.yaml` and every `.openspec.yaml` removed — no sidecar
  survives; a spec's state is its frontmatter and its folder.
- Non-diverged shadow copies (`.claude/skills/openspec-*`, `.claude/commands/opsx/`) and the
  `/opsx:*` wrappers are removed.

**This is one-way and loses interop with the external OpenSpec CLI.** The align says so before
applying, and a rename whose blast radius reaches product code confirms on its own.

---

## 11. The other fronts

| Front | Manual | Status (read-only) | Align |
| --- | --- | --- | --- |
| `docs/` — the OKF knowledge bundle | `../docs/QUENCHING.md` | `/docs:status` | `/docs:align` |
| `specs/` — this workspace | this file | `/specs:status` | `/specs:align` |
| `.claude/` — the automation surface | `../.claude/QUENCHING.md` | — | `/skill:align` |

**One align per front.** Each opens with its front's own verifier (the probe), so a clean front
costs a couple of tool calls and says so; each carries its front's content stages, conditional on
the probe finding work. `/align` conducts the three in dependency order on one confirmation —
`docs/` first (the other two write artifacts into it), then `specs/`, then `.claude/` — because
the fronts feed each other: a spec's distillation is glossary work, and the skill front's
registry is a `docs/` listing. A front this repo does not use simply has no manual — the paths
above are references, not promises.

The normative spec-driven facts — the folders, the fourteen canonical sections, the gates, the
derived stages, the record vocabulary, the full `specs.py` surface — live in the plugin's
`assets/references/specs-develop/spec-driven.md`. This file is the operator's view; that is the
specification.
