<!-- claude-quenching v<VERSION> · operator manual · generated payload.
     Refreshed by /specs:align (or /align). Edit the plugin asset, not this copy —
     a run with a newer plugin overwrites this file. Remove this banner to keep
     your own version: the align will then leave it alone and report it. -->

# Operating the spec-driven plan workspace

This is `specs/` — where a change to this product is **thought through, specified, built, and
recorded** before it becomes history. Its unit of work is a **spec**: ONE markdown file that lives through its whole
lifecycle, moving between three phase folders — captured, built on an isolated branch, and
archived when done. It is operated through the `/specs:*` commands of the
[`claude-quenching`](https://github.com/eloysekonell/claude-quenching) plugin.

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
| See where everything stands, changing nothing | `/specs:status` |
| Park an idea I just had | `/specs:capture` |
| Think it through before committing to it | `/specs:explore` |
| Flesh it out — or revise it — until it can be built | `/specs:develop` |
| Argue with it before building: poke holes, weigh alternatives | `/specs:refine` |
| Bring in a Claude Code plan file | `/specs:from-claude` |
| Build it (opens by offering branch/worktree isolation) | `/specs:apply` |
| Close it out — shipped, or dropped | `/specs:archive` |
| Sweep what is parked, and every spec's discoveries | `/specs:triage` |
| Fix the workspace itself — scaffold, filenames, the v1 fold | `/specs:align` |
| Fix it **and** drive the cycle, to a fixpoint | `/specs:align-and-update` |
| Align **and update** every front (`docs/`, `specs/`, `.claude/`) | `/align-and-update` |

> `/specs:develop` is the short form of `/claude-quenching:specs:develop`; use the long form if
> another plugin claims the namespace. Claude also routes to these skills from prose ("flesh out
> the session-tokens spec") — the command is the explicit entry point.

**Eleven commands, flat.** v1 nested them under `/specs:plan:*` and `/specs:backlog:*` because a
parked task and the spec it seeded were different objects. They are one file now, so the nesting
described a distinction that no longer exists. `propose` and `update` became one `develop`
(creating a section and revising one are the same call), and `archive` and `abandon` became one
`archive` (same command, opposite `--outcome`).

---

## 2. The layout

The front lives at the **repo root** — never inside `docs/`. **One spec is ONE markdown file for
its entire lifecycle.** Phases enrich it; they never split it.

```
specs/
  QUENCHING.md              # this manual (payload — not a spec)
  backlog/                  # DEFINITION — captured → proposed → designed → refined
    index.md                # derived listing (generated zone, frontmatter-free)
    2026-07-25-<slug>.md    # one spec per file
  ready/                    # EXECUTION — ready to build, or building
    2026-07-14-<slug>.md
  archive/                  # done or abandoned, told apart by `outcome:` frontmatter
    2026-06-30-<slug>.md
```

**The folder is the phase, and it is the single truth.** There is no `phase:` frontmatter field:
two declared sources of one fact will diverge, and a folder cannot lie. The transition is a
`git mv` performed by `specs.py promote`, so `git log` narrates the lifecycle.

**Every file is `YYYY-MM-DD-<slug>.md`, in every folder.** The date records when the spec was
**born** and is stamped once, at capture — promote moves the file and never renames it. So the
basename is stable for the whole lifecycle, `git log --follow` reads as one history, and a plain
`ls` of any folder is chronological. That last property is the point: a file listing IS the status
view, and no file listing reads frontmatter.

**Identity is the slug, not the path.** Every command and cross-reference names the bare slug;
`specs.py` resolves it to the one file ending in `-<slug>.md`, wherever it sits. Two matches is a
refusal, never a guess.

**One truth, not two.** There is no "main spec" store and no proposed "delta" to reconcile with
it. A spec writes its durable rule **directly** into the OKF `docs/` bundle — a decision into
`docs/standards/` (honestly `authority`-graded), an understanding into `docs/knowledge/` — as it is
built. Isolation-while-building is what a **branch or worktree** gives you, with real merge,
history, and reversion — not a markdown reimplementation of version control.

---

## 3. The lifecycle

One file moves through three folders. Nothing is ever copied, split, or renamed.

```
   capture                    enrich, in place                 promote (the OK)
      │                             │                                 │
      ▼                             ▼                                 ▼
  backlog/2026-07-25-<slug>.md ───────────────────────────►  ready/2026-07-25-<slug>.md
      │   ## Problem                                              │   same basename
      │      ↓ ## Proposal          derived stages:               │
      │      ↓ ## Design            captured → proposed →         │  build: code, verified
      │      ↓ refined:             designed → refined            │  + committed per task
      │                                                           │  durable rules → docs/standards/
      │  a spec that will NOT be built                            │  discoveries → ## Discoveries
      │  skips straight to archive                                │
      └──────────────────────────┐                                ▼ promote --to archive
                                 ▼                    archive/2026-07-25-<slug>.md
                    outcome: abandoned                     outcome: done
                                                                  │
                                                                  ▼ OKF distillation (offered)
                                                    docs/standards · knowledge · glossary
```

**`promote` is the human OK, and it is gated.** Moving a spec into `ready/` requires the ten
definition sections to be filled — the nine `## Problem` … `## Risks` plus `## Tasks`. Missing any
of them is **exit 2 with the list**, not a warning. An empty section is filled with an explicit
`- none — <reason>`; a heading present with an empty body is malformed and refuses. So the
one-plan-one-OK doctrine becomes one auditable `git mv` in your history.

`## Tasks` is in that gate on purpose: nothing enters the execution phase with nothing to execute.

**Archiving refuses to lie.** Promoting to `archive/` with `outcome: done` while `- [ ]` boxes
remain exits 2 and lists them (overridable with `--force`). `outcome: abandoned` is always allowed
— open tasks are exactly what you expect when closing out work that will not be built.

**There is no ledger and no task inbox.** The thing you park and the thing you build are the same
file, so the two meanings a ledger row had to carry — *developed* versus *done* — simply do not
arise. A finished spec is in `archive/` with `outcome: done`; a dropped one is there with
`outcome: abandoned`; `git log --follow` is the rest of the story.

Not every spec needs every stage: one already clear in scope is captured, filled out, and promoted
in a single sitting.

**`/specs:status` reads this whole picture and writes nothing** — what is open, what is ready to
archive, what is blocked or stale, how the backlog is ranked, and what a sweep would change if you
ran one. It is the honest way to look before you authorize anything.

---

## 4. The commands, one by one

### `/specs:status` — look, change nothing

The only command here that cannot write. Reports every spec by phase and derived stage, task
progress, what is blocked or stale, and the verifier results (`specs.py doctor` / `validate`) —
then splits what it found into what `/specs:align` would fix on one OK, what
`/specs:align-and-update` would drive, and what neither closes because it needs you. It speaks the
sweep's own `sp-*` vocabulary, so the two never disagree.

### `/specs:capture` — park ONE spec

Seconds, minimal, **zero interrogation**. Runs `specs.py new`, which stamps
`backlog/YYYY-MM-DD-<slug>.md` carrying `## Problem` and nothing else. Every other heading is left
absent — a *not-yet*, not an omission — which is what keeps a fresh capture from deriving as
`designed` and sailing through every gate. The date is stamped here and **never rewritten**.

### `/specs:explore` — think, don't build

A stance, not a workflow. Reads code, active specs, and the OKF bundle (`knowledge/`,
`glossary.md`, `standards/`) as ground truth, draws ASCII diagrams, asks the questions that sharpen
the requirement. **It never implements.**

### `/specs:develop` — fill it out, or revise it

Walks the gate: `specs.py next` names the next unfilled section, you confirm, it writes it via
`specs.py section --write` — which creates the heading in **canonical position**, so a spec whose
`## Tasks` was written before its `## Proposal` still reads in contract order. Revising a filled
section is the same call.

Reads the relevant `docs/standards/` and the glossary first, so the wording does not contradict a
rule you already agreed on. An empty section is answered `- none — <reason>`, never deleted —
*we drew the boundary and nothing fell outside it* and *nobody ever drew the boundary* read
identically when the heading is missing, and only one is safe to build on. It **never edits code**,
and it never invents an explicit none on your behalf.

When the gate is met it **offers the promote**. That promote is your OK.

### `/specs:refine` — argue with it before you build it

A spec becomes promotable the moment its sections have content. Nothing in that gate requires
anyone to have **disagreed** with it. This is the disagreement: it generates the questions the
sections never answered, asks them **one at a time with a recommendation** so you can answer in a
word, and applies every accumulated answer in **one** edit at the end — so a refinement you abandon
halfway leaves the spec exactly as it was.

Four modes pick the technique: `interview` (default), `critic`, `premortem`, `alternatives`. Each
has a declared stop condition, so it terminates instead of wandering. It records
`refined: {mode, date}` in the spec's frontmatter, which clears `sp-unrefined` — **a warning, never
a gate**: nothing here refuses to let you build an unrefined spec.

### `/specs:from-claude` — bring in a Claude Code plan file

Turns a native plan (`~/.claude/specs/*.md`, or an explicit path) into a spec, so the work gains
the phase gates and the archive-time distillation instead of dying in a one-shot file. The native
file is **read, never moved or deleted**.

### `/specs:apply` — build it, prove it, commit it

**It refuses to start on a dirty tree** — it commits one task at a time, and a commit cannot tell
your task's diff from an unrelated edit already sitting there. Then it **offers isolation** — a
branch or a worktree — so the build has real version control around it.

Per task it writes the code, runs that task's `verify:` under the spec's declared policy,
self-reviews the diff (reuse · useless defense · obvious comment · dead code), commits it alone,
and only then ticks the box with `specs.py task --check`.

When attempts stop converging it writes the task **blocked, in the file**:

```markdown
- [!] 2.3 Implement the gate check — blocked: waiting on the vendor SDK
```

`next` skips it and moves on, so one bad task never stalls the spec. There is **no attempt
counter**: v1 kept one in a sidecar and stopped at five, which meant a task went quiet with no
trace of *why*. A written reason stops the same runaway loop while being legible to whoever has to
unblock it.

It reads the touched subjects' `standards/` as **binding contracts** and pauses when the spec
conflicts with one rather than quietly picking a side. Durable rules go **straight into
`docs/standards/`**; things noticed in passing go to `## Discoveries` (`specs.py discover`) for
triage to judge later, so nothing interrupts you mid-build.

What it will **never** do, whatever the pressure: disable or delete a test, edit the check so it
stops failing, or pass `--no-verify`. A green checkbox has to mean something.

### `/specs:archive` — close it out, shipped or dropped

One command, two outcomes, and the outcome is **your word** — never inferred from progress or age.

`--outcome done` refuses (exit 2) while boxes are still open, listing them; `--force` is there for
when you know why. It then offers **one OKF distillation pass**: the durable by-products get minted
into `docs/` — a proven rule → `standards/` (authority-graded), a generic understanding →
`knowledge/`, new vocabulary → the glossary. **Nothing is bulk-copied.** There is no spec-sync
step — the rules were written to `docs/standards/` while it was built.

`--outcome abandoned` is **always allowed** (open tasks are exactly what you expect) and distils
**nothing as adopted** — at most a narrow `authority: background` note on what you learned by not
building it. Archiving a dropped spec as done would enshrine a rule nobody kept.

### `/specs:triage` — sweep what is parked, and what was noticed

Reads every backlog spec by **derived stage** and every active spec's `## Discoveries`, then
proposes **one** table: what to pick up, what has gone stale, what duplicates what — and for each
discovery, `→ promoted: <new-slug>` or `→ dismissed: <reason>`, resolved **in place** so provenance
is never lost. **One OK** applies it all.

### `/specs:align` — force the workspace into shape

The sweep. Scaffolds the three phase folders when absent, installs `specs.py`, **folds a v1
three-file workspace one-way** (`specs.py migrate`), normalizes filenames and slugs, stamps missing
frontmatter, and regenerates the backlog listing zone. It also migrates a legacy `openspec/`
workspace (§10).

**It aligns conformance and only *reports* content.** An empty section, a missing gate heading, a
stray heading, a complete spec awaiting promote — each is reported with the command that owns it.
Writing even `- none — <reason>` would be authoring an answer only you can give. One plan, one OK;
a rename whose blast radius reaches code confirms on its own.

### `/specs:align-and-update` — align, then close out what is finished

This front's conductor: **three** stages in dependency order — `align` (structure) → `archive`
(each complete spec) → `triage` (sweep what remains) — looped until a full pass changes nothing.
There is **no sync stage**: with no separate spec store, a spec's rules are already in
`docs/standards/`.

Stage 2 is the one thing the run's single OK deliberately does **not** cover — **every archive asks
you separately**, because the outcome is a claim only you can make.

---

## 5. The boundary that must never blur

| Store | Answers | Owned by |
| --- | --- | --- |
| `specs/backlog/`, `specs/ready/` | a change **in flight** — its problem, design, and task list | the `/specs:*` commands, until it archives |
| `docs/standards/` | **HOW we build** (binding contracts, current behavior) | the `/docs:*` commands; a plan writes here directly |
| `specs/archive/` | what was **done or dropped**, told apart by `outcome:` | `/specs:archive` |
| `docs/vision/` | settled **direction**, no deadline | `/docs:add` |

Content is never duplicated across them. A spec's rationale and considered alternatives live in
its `design.md` **while it is active**, and distill into a `standard` at archive time. The plan
**is** the change: what it proves out lands in `docs/standards/` as it is built — there is no
second store for it to duplicate.

---

## 6. The OKF bridge

This front reads the `../docs/QUENCHING.md` knowledge bundle as context going in, and distils
durable knowledge back out — but, being native, it writes into `docs/` **directly** rather than
through a spec-sync:

- **Going in** — `explore`, `propose`, `from-claude`, and `apply` read `docs/standards/`
  (binding), `docs/knowledge/`, and `docs/knowledge/glossary.md` (vocabulary) before writing
  anything, so artifacts do not contradict rules the repo already agreed on.
- **While building** — `apply` writes the durable rules a plan proves out **straight into
  `docs/standards/`**, honestly `authority`-graded (`background` for agreed-but-unproven,
  `current` once implemented and proved). There is no delta and no main-spec copy to reconcile.
- **Going out** — `archive` offers the **distillation pass** (§4) for the remaining by-products
  (a term, an understanding, a follow-up task). Durable knowledge crosses; the archived plan stays
  as history.

If the target has no OKF bundle (`docs/index.md` with `okf_version`), the standards-writing and
the distillation are skipped, and `/docs:align` is suggested once.

---

## 7. The spec file contract

One file per spec, flat, no subfolders, the same shape in all three folders.

```yaml
---
slug: session-tokens          # required — the identity key every command names
title: <one line>             # required
verification: per-task        # required — per-task | per-section | end-of-plan
refined: {mode: premortem, date: 2026-07-25}   # once a refinement pass has run
outcome: done                 # stamped by `promote --to archive` — done | abandoned
---
```

There is **no `created` field** (the filename's date prefix is that fact) and **no `phase` field**
(the folder is that fact). A spec carries no OKF `type:` either — it is not a concept doc, it lives
outside the bundle, and `specs.py validate` is what checks it.

Thirteen canonical headings, in this order: `## Problem`, `## Proposal`, `## Out of Scope`,
`## Impact`, `## Validation`, `## Design`, `## Alternatives Considered`, `## Open Decisions`,
`## Risks`, `## Handoff`, `## Tasks`, `## Discoveries`, `## Outcome`. **Headings are a parsed
contract** — canonical English, exactly as written; body prose follows your repo's language. A
heading outside the set is a stray and `validate` flags it.

A heading is required only once **its own phase gate** is reached — before that, its absence is a
*not-yet*, not an omission. That is what keeps a freshly captured spec four lines long instead of a
thirteen-heading skeleton.

Two sections are load-bearing for machinery, not just for thinking: `## Validation` is the fallback
for a task with no `verify:` line, and `## Impact` is the one machine-parsed declaration.

A blocked task is a **visible marker**, never a hidden counter:

```markdown
- [!] 2.3 Implement the gate check — blocked: waiting on the vendor SDK
```

`next` skips it, and the reason is right there for whoever unblocks it. There is no attempt budget.

`backlog/index.md` carries a `<!-- BEGIN GENERATED -->` … `<!-- END GENERATED -->` zone rebuilt
**deterministically** by `specs.py backlog reindex`: counts, then one table per **derived stage**
(oldest-first inside each, so stale specs surface). **Never hand-edit inside that zone** and never
add frontmatter to `backlog/index.md`.

---

## 8. The `specs.py` tool

A stdlib-only Python script, no dependencies. Every subcommand takes `--json` and returns **strict
exit codes**: **0** ok · **1** findings · **2** refusal. A skill branches on the exit code and the
JSON, never on prose.

| Command | Use |
| --- | --- |
| `specs.py new <slug> [--title T] [--verification P]` | capture into `backlog/` with `## Problem` alone; stamps the date ONCE |
| `specs.py list [--json]` | every spec, grouped by folder and derived stage |
| `specs.py status --spec <slug> [--json]` | sections, stage, tasks, and the destination phase's outstanding gates |
| `specs.py section <slug> "<Heading>" [--write]` | read or write ONE section; `--write` creates it in canonical position |
| `specs.py promote <slug> [--to ready\|archive] [--outcome done\|abandoned] [--force]` | the gated transition; **exit 2** with the missing list |
| `specs.py next --spec <slug> [--json]` | THE single next action; skips `[!]` |
| `specs.py task --spec <slug> --check ID \| --uncheck ID \| --block ID --reason MSG` | flip or block a checkbox mechanically |
| `specs.py discover <slug> "<text>"` | append one line to `## Discoveries` |
| `specs.py parallel --spec <slug> [--json]` | prove a `[P]` group's `files:` are disjoint; exit 1 if not |
| `specs.py backlog reindex` | regenerate the `backlog/index.md` GENERATED zone by derived stage |
| `specs.py validate [--spec <slug>]` | the canonical heading set, the phase-scoped rule, filenames, the `sp-*` codes |
| `specs.py doctor` | workspace shape, v1 leftovers; remedies **declared** for the skill to apply |
| `specs.py migrate [--dry-run]` | one-way v1 → v2 fold; **exit 2** if already v2 |

There is no `init` (scaffold is an asset copy), no `store`, no `profiles`, no telemetry, and no
delta parser. `archive` is gone — it folded into `promote --to archive`. `/specs:align` installs
the script into `.claude/hooks/specs.py`; run it yourself any time:

```bash
python3 .claude/hooks/specs.py doctor --json      # workspace health (and v1 detection)
python3 .claude/hooks/specs.py list --json        # every spec, by phase and stage
```

**`--block` requires `--reason`.** The tool refuses without one: a blocked task with no reason is
exactly the hidden state the marker replaced.

---

## 9. Recipes and troubleshooting

**Setting the workspace up.** `/specs:align` — it scaffolds the three phase folders, installs
`specs.py`, and folds any v1 workspace. No package to `npm i` first.

**From idea to shipped.** `/specs:capture` → `/specs:explore` if it is still fuzzy →
`/specs:develop` until the gate is met → `/specs:refine` if it deserves an argument →
**promote** (your OK) → `/specs:apply` (accept the branch isolation) → `/specs:archive`.

**Coming back after a while.** `/specs:status` first — what is open, what is ready to close, what
has gone stale — without touching anything. Or just `ls specs/backlog specs/ready`: the listing IS
the status view, oldest first, which is exactly the triage question.

**Deciding not to build something.** `/specs:archive` with `--outcome abandoned`, never `done`.
Done distils its decisions as adopted knowledge; abandoned does not.

**Health check.** `specs.py doctor && specs.py validate`, plus
`okf-validate.py specs/backlog --listing-root` for the **listing**. Read each for what it owns: a
spec carries no OKF `type:` (it is not a concept doc), so the bundle validator checks `index.md`
and `specs.py validate` checks the specs.

| Symptom | What is going on |
| --- | --- |
| `list` says the workspace is empty, but there are files in `specs/` | It is a **v1 workspace**. v2 globs the three phase folders and a `specs/<plan>/` tree matches none of them. Run `specs.py doctor` — it detects v1 leftovers and declares `migrate` as the remedy — or just `/specs:align`. |
| `promote` refuses with a list of headings | That is the gate doing its job. Fill each one, or answer `- none — <reason>`. A heading that exists but is **empty** also refuses: it is neither an answer nor a not-yet. |
| A freshly captured spec shows as `designed` | Someone stamped all thirteen headings at capture. An explicit none counts as *filled*, so a skeleton derives as designed. Capture writes `## Problem` alone on purpose. |
| `promote --to archive` refuses with open boxes | The outcome is `done` and the work is not. Finish them, pass `--force` if you know why, or switch to `--outcome abandoned`. |
| Two commands both refuse with "slug matches 2 files" | Two specs resolve to the same slug. Identity in v2 *is* the slug — rename one. |
| A task went quiet and nothing says why | It should not have. `--block` requires `--reason`, and the reason is written into the line: `- [!] 2.3 … — blocked: <why>`. |
| `backlog/index.md` disagrees with the files | Its generated zone is stale — `specs.py backlog reindex` rebuilds it from disk. Never hand-edit inside the markers. |
| `python3: command not found` | Install Python 3, or use `py` on Windows. This front needs nothing else — no Node, no npm package. |
| I still have an `openspec/` folder | Legacy external-CLI workspace. `/specs:align` migrates it one-way (§10), then folds it to v2. |

---

## 10. Upgrading, and migrating older workspaces

### Upgrading a repo that still holds a v1 `specs/` workspace

**You must re-align manually. Nothing migrates on its own.** The plugin ships to other
repositories, and Claude Code applies an upgrade from the `VERSION`/`plugin.json` bump — so a repo
can wake up with v2 skills over a v1 three-file workspace, having run no migration. **No format
coexistence is built for that case**, by design: supporting both would double every skill's
complexity, which is the opposite of the point.

The exposure this leaves is worth naming, because it is silent: **v2 `list` reads a v1 workspace as
EMPTY, not as wrong format.** It globs `backlog/`, `ready/`, and `archive/`, and a `specs/<plan>/`
tree matches none of them — so a skill can conclude there is nothing parked when there is
unmigrated work sitting right there.

`specs.py doctor` is the one command that sees it, and it declares the remedy:

```bash
python3 .claude/hooks/specs.py doctor --json     # -> sp-v1-leftover, remedy: specs.py migrate
```

The fix is one command — **`/specs:align`**, which drives the fold on one confirmation. Run it
first in any repo that upgraded across this boundary.

The fold is **one-way** and mechanical: each plan folder becomes one file (`## Why`→`## Problem`,
`## What Changes`→`## Proposal`, `## Context`+`## Decisions`→`## Design`, `tasks.md`→`## Tasks`
with every checkbox state preserved); the birth date comes from `.specs.json`'s `created`, falling
back to the path's first commit — **never invented**; a section the v1 plan never recorded is
written `- none — not recorded in the v1 plan`; a plan folder still holding any other file is
**kept, not deleted**, and reported for you; and **`specs/archive/**` is never touched** — it stays
as history, in v1 shape, deliberately.

### Migrating from a legacy `openspec/` workspace

Earlier still, this front was driven by the external `@fission-ai/openspec` CLI and lived in
`openspec/`. If this repo still has one, `/specs:align` migrates it **one-way** into the native
`specs/` front, inside its single plan → one OK:

- `openspec/` → `specs/`; `changes/<n>/` → `specs/<n>/`; `changes/archive/` → `specs/archive/`
  (the delta was the only reason for the `changes/` nesting — without it, specs sit flat).
- Each `openspec/specs/<capability>/spec.md` is **folded into `docs/standards/`** — the cut is
  chosen by you in the spec, never inferred. No OKF bundle → the fold stops and `/docs:align` is
  suggested first.
- The CLI scaffolding is dropped: `config.yaml` and every `.openspec.yaml` removed — v2 keeps
  no sidecar at all; a spec's state is its frontmatter and its folder.
- The delta folders are discarded once their content is folded or confirmed obsolete.
- Non-diverged shadow copies (`.claude/skills/openspec-*`, `.claude/commands/opsx/`) and the
  `/opsx:*` wrappers are removed.

**This is one-way and loses interop with the external OpenSpec CLI** — the migrated workspace no
longer runs under `@fission-ai/openspec`. The align says so before applying, and a rename whose
blast radius reaches product code confirms on its own.

---

## 11. The other fronts

| Front | Manual | Status (read-only) | Align (structure, one pass) | Align-and-update (+ content, looped) |
| --- | --- | --- | --- | --- |
| `docs/` — the OKF knowledge bundle | `../docs/QUENCHING.md` | `/docs:status` | `/docs:align` | `/docs:align-and-update` |
| `specs/` — this workspace | this file | `/specs:status` | `/specs:align` | `/specs:align-and-update` |
| `.claude/` — the automation surface | `../.claude/QUENCHING.md` | — | `/skill:align` | `/skill:align-and-update` |

`/align` runs the three aligns in dependency order on one confirmation; `/align-and-update` runs
the three conductors the same way and loops across fronts, because they feed each other (a plan's
archive distils docs the glossary must then index). A front this repo does not use simply has no
manual — the paths above are references, not promises.

The normative spec-driven facts — the three folders, the thirteen canonical sections, the phase
gates, the derived stages, the full `specs.py` surface — live in the plugin's
`skills/quenching-specs-develop/references/spec-driven.md`. This file is the operator's view;
that is the specification.
