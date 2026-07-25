<!-- claude-quenching v<VERSION> · operator manual · generated payload.
     Refreshed by /specs:align (or /align). Edit the plugin asset, not this copy —
     a run with a newer plugin overwrites this file. Remove this banner to keep
     your own version: the align will then leave it alone and report it. -->

# Operating the spec-driven plan workspace

This is `specs/` — where a change to this product is **thought through, specified, built, and
recorded** before it becomes history. Its unit of work is a **plan**: a folder holding a
proposal, an optional design, and a task checklist, built on an isolated branch and archived
when done. It is operated through the `/specs:*` commands of the
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
| Park a task I just thought of | `/specs:backlog:add` |
| Prioritize everything parked | `/specs:backlog:triage` |
| Think an idea through before committing to it | `/specs:explore` |
| Turn a task or idea into a real plan with artifacts | `/specs:plan:propose` |
| Promote a Claude Code plan file into the workspace | `/specs:plan:from-claude` |
| Build it (opens by offering branch/worktree isolation) | `/specs:plan:apply` |
| Revise the plan without touching code | `/specs:plan:update` |
| Close the plan out and distill what it taught us | `/specs:plan:archive` |
| Drop a plan we are **not** going to build | `/specs:plan:abandon` |
| Fix the workspace itself — scaffold, names, inbox | `/specs:align` |
| Fix it **and** drive the cycle, to a fixpoint | `/specs:align-and-update` |
| Align **and update** every front (`docs/`, `specs/`, `.claude/`) | `/align-and-update` |

> `/specs:plan:propose` is the short form of `/claude-quenching:specs:plan:propose`; use the long
> form if another plugin claims the namespace. Claude also routes to these skills from prose
> ("propose a plan for X") — the command is the explicit entry point.

---

## 2. The layout

The front lives at the **repo root** — never inside `docs/`. It is **flat**: one folder per plan,
no `changes/` nesting, because there is no delta to keep separate from a main store.

```
specs/
  QUENCHING.md         # this manual (payload — not a spec, not a plan)
  <plan-name>/         # an ACTIVE plan, one folder each
    .specs.json        # plan metadata (schema, name, title, created, backlogTask)
    proposal.md        # what & why (+ the ## Impact scope)
    design.md          # how — OPTIONAL; delete it if the plan needs none
    tasks.md           # implementation checklist (- [ ] / - [x])
  archive/             # completed & abandoned plans, as YYYY-MM-DD-<plan-name>/
  backlog/             # THE TASK INBOX (quenching-managed, outside the docs/ bundle)
    index.md           # derived listing + the Completed ledger
    <task-slug>.md     # one parked task per file (type: task)
```

**One truth, not two.** There is no "main spec" store and no proposed "delta" to reconcile with
it. A plan writes its durable rule **directly** into the OKF `docs/` bundle — a decision into
`docs/standards/` (honestly `authority`-graded), an understanding into `docs/knowledge/` — as the
plan is built. Isolation-while-building is what a **branch or worktree** gives you (offered by
`/specs:plan:apply`), with real merge, history, and reversion — not a markdown reimplementation of
version control.

**`backlog/` is the task inbox**, a quenching-managed sibling of the plan folders and `archive/`,
**outside** the `docs/` OKF bundle. `specs.py` and the OKF validator both leave it to the backlog
skills, which validate it on every write (`okf-validate.py specs/backlog --listing-root`).

---

## 3. The lifecycle

```
  /specs:backlog:add          /specs:explore         /specs:plan:propose
        │                          │                     │
        ▼                          ▼                     ▼
   backlog/<task>.md  ──────►  (thinking)  ──────►  specs/<plan-name>/
        │                                            proposal · design? · tasks
        │  /specs:backlog:triage                          │
        ▼  (priority · tags · complexity)                 │ /specs:plan:apply
   still backlog/, now ranked                             ▼  (offers branch/worktree isolation)
                                                    code + tasks.md ticked
        ~/.claude/plans/*.md                              │  durable rules → docs/standards/
        │ /specs:plan:from-claude                         │
        └───────────────────────────►  specs/<plan-name>/ │
                                                           │
                                    /specs:plan:update ◄──┤ (plan drifted?)
                                                           │
                                                           ▼ /specs:plan:archive
                                              specs/archive/YYYY-MM-DD-<name>/
                                                           │
                                                           ▼ OKF distillation (offered)
                                             docs/standards · knowledge · glossary

   …or the plan is dropped instead:  /specs:plan:abandon
                                              specs/archive/YYYY-MM-DD-<name>/ + ABANDONED.md
                                              (nothing to un-sync — and the seed task comes BACK)
```

A task **leaves the inbox** when its plan becomes apply-ready or the work is simply done — the
file is removed and the transition recorded in the **Completed ledger** in `backlog/index.md`.
Removal never happens on triage, and an abandoned *exploration* (one that never reached a plan)
leaves the task in place to begin with.

**The ledger records two different things.** A row written at `/specs:plan:propose` time means
*developed* — the task became a plan, and the work has **not** shipped. A row written when you
state a task is done means *done*. The Outcome column is what tells them apart. If a developed
plan is later dropped, `/specs:plan:abandon` reopens its task, so retiring a task at propose time
is a reversible handoff rather than a deletion.

Not every plan starts as a task, and not every task needs the full cycle: a task already clear in
scope goes straight to execution.

**`/specs:status` reads this whole picture and writes nothing** — what is open, what is ready to
archive, what is blocked or stale, how the backlog is ranked, and what a sweep would change if you
ran one. It is the honest way to look before you authorize anything.

---

## 4. The commands, one by one

### `/specs:status` — look, change nothing

The only command here that cannot write. It reports the resolved workspace, every active plan
with its task progress and state (*ready to archive* · *in progress* · *blocked* · *stale, with
the age*), the backlog by priority, and the verifier results (`specs.py doctor` / `validate`,
plus the backlog check) — then splits what it found into what `/specs:align` would fix on one OK,
what `/specs:align-and-update` would then drive, and what neither closes because it needs you. Use
it as the preview before authorizing a sweep: it speaks the sweep's own `sp-*` finding vocabulary,
so the two never disagree.

### `/specs:backlog:add` — park ONE task

Seconds, minimal, **zero interrogation**. Extracts a title and a one-sentence gist from your
phrasing and stamps `type: task` with a timestamp. `priority` (`critical|high|medium|low`),
`tags`, and `complexity` (rough dev hours) are recorded **only if you say them inline** — *"park
the token refresh bug, high priority, theme auth, ~8h"*. What you did not say is left out: a task
with no priority is **untriaged**, which is a valid state. Dedupes by slug and title (MERGE, never
clobber), regenerates the derived zone in `backlog/index.md` (`specs.py backlog reindex`), and logs.

### `/specs:backlog:triage` — rank the WHOLE inbox

Reads every task's frontmatter directly (no sub-agents — a backlog is small by nature) plus
`docs/vision/` when it exists, then proposes **one** table: a priority, tags, and optionally a
complexity per untriaged task, each with a one-line rationale — plus staleness flags and
duplicate-merge suggestions. **One OK** applies it all; a rejected plan applies nothing. A
priority **you** set is never silently overwritten, and an already-triaged task is re-ranked only
with an explicit reason. Completion enters the plan **only when you state a task is done** — it is
never inferred.

### `/specs:explore` — think, don't build

A stance, not a workflow. Reads code, active plans, and the OKF bundle (`knowledge/`,
`glossary.md`, `standards/`) as ground truth, draws ASCII diagrams, asks the questions that
sharpen the requirement. **It never implements.** Insights route to a plan's artifacts or to the
`docs/` homes only on your word.

### `/specs:plan:propose` — create the plan and all its artifacts

Derives a kebab-case name, runs `specs.py new <name>`, then works the artifact graph to
apply-ready: `proposal.md`, an optional `design.md`, and `tasks.md`. Reads the relevant
`standards/` and the glossary first, so the artifacts speak this repo's vocabulary. If a
`backlog/` task seeded it, that task is retired into the Completed ledger when the artifacts are
ready (one confirmation). There is **no delta spec** to write — the durable rules land in
`docs/standards/` when the plan is built.

### `/specs:plan:from-claude` — promote a Claude Code plan file into the workspace

Turns a native Claude Code plan (`~/.claude/plans/*.md`, or an explicit path) into a real front
plan, so it gains the task tracking, isolation, and archive-time distillation the front provides
instead of dying in a one-shot file. Maps the native plan's `## Context` into the proposal's
*Why*, its decisions and risks into `design.md`, and its phases/steps into `tasks.md` checkboxes;
scaffolds with `specs.py new` and writes on **one** confirmation. The native file is **read, never
moved or deleted**. Offers to link and retire the seed `backlog/` task if one exists.

### `/specs:plan:apply` — implement it (opens by offering isolation)

Its **first act is to offer isolation** — a dedicated branch or a git worktree for the plan — so
the build has real version control (merge, history, reversion) around it rather than a markdown
imitation. It then works through `tasks.md` checkbox by checkbox (each flipped mechanically with
`specs.py task --check`), reads the touched subjects' `standards/` as **binding contracts**, and
pauses when the plan conflicts with one rather than quietly picking a side. Durable rules the plan
proves out are **written straight into `docs/standards/`** (honestly `authority`-graded); other
durable learning routes to `/docs:learn` or `/docs:add` — never into a loose code comment.

### `/specs:plan:update` — revise the plan, never the code

Applies your edit to one artifact, then checks **every other artifact against it in any
direction** and confirms each follow-on revision before writing. It only edits files that already
exist — creating a missing artifact is `/specs:plan:propose`.

### `/specs:plan:archive` — close it out and keep what it taught

Checks artifact and task completion (warnings never block — an incomplete item just asks for
confirmation), then moves the plan to `specs/archive/YYYY-MM-DD-<name>/` (`specs.py archive`).
Finally it offers **one OKF distillation pass**: the durable by-products the plan produced are
minted into `docs/` — a remaining decision → `standards/` (authority-graded), a generic
understanding → `knowledge/`, new vocabulary → the glossary. **Nothing is bulk-copied**; the
archived plan remains the history, and only what outlives it crosses the bridge. There is **no
spec-sync step** — the standards a plan touches were written into `docs/standards/` while it was
built.

### `/specs:plan:abandon` — drop a plan we are not going to build

The exit `/specs:plan:archive` cannot give you. Archiving a plan distils its decisions into
`docs/standards/` as knowledge the product adopted — wrong for work that was dropped, where you
would be enshrining a rule nobody kept.

`/specs:plan:abandon` asks why, moves the plan to `specs/archive/YYYY-MM-DD-<name>/` with an
`ABANDONED.md` recording the date and your reason, and **distils nothing as adopted** (at most a
narrow harvest of what you learned by *not* building it — a `standard` at `authority: background`;
a decision the plan *would* have made never crosses). Because the front has no separate spec
store, there is nothing to un-sync. It then offers to **reopen the backlog task** the plan
consumed at propose time — the task comes back *untriaged*, since whatever ranking it had was
based on a decision now reversed.

Abandonment is never inferred. No sweep, no conductor, and no age threshold triggers it — a plan
untouched for a year may be waiting on a vendor. `/specs:align` reports staleness with its age and
names this command; only you run it.

### `/specs:align` — force the workspace into shape

The sweep. Scaffolds `specs/` (backlog seed + templates + schema) when absent, applies only the
repairs `specs.py doctor` and `specs.py validate` themselves state (never an invented one),
normalizes plan and archive names to kebab-case / `YYYY-MM-DD-<name>`, seeds and stamps the
`backlog/` inbox and regenerates its derived zone (`specs.py backlog reindex`). It also **migrates
a legacy `openspec/` workspace one-way** (§10) and removes CLI-generated
`.claude/skills/openspec-*` and `.claude/commands/opsx/` **shadow copies** that duplicate what the
plugin ships.

**It aligns conformance and only *reports* the cycle.** A complete-but-unarchived plan, a stale
plan, untriaged tasks — each is reported with the command that owns it. This sweep never archives,
never ranks, never proposes, and never authors or deletes a plan's contents. One plan, one OK; a
rename whose blast radius reaches product code, branch names, CI, or scripts confirms on its own.

### `/specs:align-and-update` — align, then close out what is finished

This front's conductor, and the exact complement of the align above: where `/specs:align` only
**reports** the cycle actions, this one **drives** them. **Three** stages in dependency order —
`align` (structure) → `plan-archive` (each complete plan) → `backlog-triage` (rank what remains) —
looped until a full pass changes nothing and `specs.py doctor`/`validate` are clean. There is **no
sync stage**: with no separate spec store, a plan's rules are already in `docs/standards/`, and
the archive distils the rest.

Stage 2 is where the value is: archiving a plan distils the durable knowledge it produced into
`docs/`. It is also the one thing the run's single OK deliberately does **not** cover — **every
archive asks you separately**, because moving a plan out of `specs/` is irreversible in the sense
that matters and a plan whose tasks are all checked may still be waiting on a deploy.

Three lines it never crosses: it **never proposes or implements** (no task becomes a plan here, no
checkbox is ticked — those need your intent), it **never infers completion** (`specs.py status`
must report every artifact `done` and every task `- [x]`; a task leaves the backlog only when you
say it is done), and it **never abandons** (a blocked or stale plan stays reported, with the
command that owns it). Run `/specs:status` first to see what the single OK would be authorizing.

Every front has this same pair (`/docs:align-and-update`, `/skill:align-and-update`);
`/align-and-update` runs all three.

---

## 5. The boundary that must never blur

| Store | Answers | Owned by |
| --- | --- | --- |
| `specs/<plan>/` | a change **in flight** — its why, design, and task list | the plan commands, until it archives |
| `docs/standards/` | **HOW we build** (binding contracts, current behavior) | the `/docs:*` commands; a plan writes here directly |
| `specs/backlog/` | what we **might** do next | `/specs:backlog:add`, `/specs:backlog:triage` |
| `docs/vision/` | settled **direction**, no deadline | `/docs:add` |

Content is never duplicated across them. A plan's rationale and considered alternatives live in
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

## 7. The backlog contract

One file per task, flat, no subfolders.

```yaml
---
type: task                    # required
title: <one line>
description: <one sentence>
timestamp: <when it was parked>
priority: high                # OPTIONAL — critical | high | medium | low
tags: [auth, billing]         # OPTIONAL — themes, normalized against existing tags
complexity: 8                 # OPTIONAL — rough size in dev hours
---
```

`backlog/index.md` carries a `<!-- BEGIN GENERATED -->` … `<!-- END GENERATED -->` zone rebuilt
**deterministically from the tasks' frontmatter** by `specs.py backlog reindex`: counts, one table
per priority level (oldest-first inside each, so stale tasks surface), then a by-theme roll-up.
**Never hand-edit inside that zone** and never add frontmatter to `backlog/index.md`. The
**Completed ledger** below the zone is curated by hand and is never regenerated.

---

## 8. The `specs.py` tool

`specs.py` is the deterministic rail under the plan skills — a stdlib-only Python script, no
dependencies. Every subcommand takes `--json` and returns **strict exit codes**: **0** ok · **1**
findings · **2** refusal. A skill branches on the exit code and the JSON, never on prose.

| Command | Use |
| --- | --- |
| `specs.py new <name> [--title T] [--backlog-task SLUG]` | scaffold a plan folder + filled templates + `.specs.json` |
| `specs.py list [--json]` | active plans, task progress, `lastModified` |
| `specs.py status --plan <n> [--json]` | the artifact graph — `done`/`ready`/`blocked`, `applyReady`, resolved paths |
| `specs.py next --plan <n> [--json]` | THE single next action (write X · implement task Y · ready to archive) |
| `specs.py task --plan <n> --check ID \| --uncheck ID` | flip a `tasks.md` checkbox mechanically |
| `specs.py backlog reindex` | regenerate the `backlog/index.md` GENERATED zone from frontmatter |
| `specs.py validate [--plan <n>]` | required artifacts present, `tasks.md` parseable, kebab-case names |
| `specs.py archive <n> [--dry-run] [--force]` | move to `specs/archive/YYYY-MM-DD-<n>/`; exit 2 on open tasks without `--force` |
| `specs.py doctor` | workspace shape; remedies **declared** for the skill to apply |

There is no `init` (scaffold is an asset copy), no `store`, no `profiles`, no telemetry, and no
delta parser. `/specs:align` installs the script into `.claude/hooks/specs.py`; run it yourself
any time:

```bash
python3 .claude/hooks/specs.py doctor --json     # workspace health
python3 .claude/hooks/specs.py list --json        # active plans
```

---

## 9. Recipes and troubleshooting

**Setting the workspace up.** `/specs:align` — it scaffolds `specs/`, seeds the inbox, installs
`specs.py`, and clears any CLI shadow copies. No package to `npm i` first.

**From idea to shipped.** `/specs:backlog:add` → (later) `/specs:backlog:triage` →
`/specs:explore` if it is still fuzzy → `/specs:plan:propose` → `/specs:plan:apply` (accept the
branch/worktree isolation) → `/specs:plan:archive` (which offers the distillation).

**Already have a Claude Code plan?** `/specs:plan:from-claude` promotes it into the workspace so it
can be built and archived instead of being a one-shot file.

**Coming back after a while.** `/specs:status` first — it tells you what is open, what is ready to
close, and what has gone stale, without touching anything. Then act on what it names.

**Deciding not to build something.** `/specs:plan:abandon`, not `/specs:plan:archive`. Archive
distils the plan's decisions as adopted knowledge; abandon does not, and gives you your backlog
task back.

**Health check.** `specs.py doctor && specs.py validate && specs.py list --json`, plus
`okf-validate.py specs/backlog --listing-root` for the inbox (the same checker that guards
`docs/`, pointed at the backlog — `--listing-root` tells it this tree is a listing, not a bundle
root). `/specs:align` runs all of it and reports whatever it cannot fix; `/specs:status` runs it
read-only and fixes nothing.

| Symptom | What is going on |
| --- | --- |
| Two skills answer "propose a plan" | This repo still has CLI-generated `.claude/skills/openspec-*` or `.claude/commands/opsx/` copies shadowing the plugin's. Run `/specs:align` — it removes identical ones and reports diverged ones instead of deleting them. |
| A plan is done but still in `specs/` | `/specs:plan:archive`. `/specs:align` reports it but will never archive on its own. |
| A plan we decided against is cluttering `specs/` | `/specs:plan:abandon` — never `/specs:plan:archive`, which would distil its decisions as adopted. |
| A ledger row names a plan that no longer exists | The plan was dropped without `/specs:plan:abandon`, so the task was lost. Recreate it with `/specs:backlog:add` and fix the row by hand — the Completed ledger is never regenerated. |
| I want to know what a sweep would do before running it | `/specs:status`. It reports in the sweep's own finding vocabulary and writes nothing. |
| Tasks pile up unranked | `/specs:backlog:triage`. Untriaged is valid, not an error. |
| `backlog/index.md` disagrees with the files | Its generated zone is stale — `/specs:backlog:add`, `/specs:backlog:triage`, and `/specs:align` each rebuild it from disk with `specs.py backlog reindex`. |
| `python3: command not found` | Install Python 3, or use `py` on Windows. This front needs nothing else — no Node, no npm package. |
| I still have an `openspec/` folder | It is a legacy external-CLI workspace. `/specs:align` migrates it one-way to `specs/` (§10). |

---

## 10. Migrating from a legacy `openspec/` workspace

Earlier versions of this front were driven by the external `@fission-ai/openspec` CLI and lived in
`openspec/`. If this repo still has one, `/specs:align` migrates it **one-way** into the native
`specs/` front, inside its single plan → one OK:

- `openspec/` → `specs/`; `changes/<n>/` → `specs/<n>/`; `changes/archive/` → `specs/archive/`
  (the delta was the only reason for the `changes/` nesting — without it, plans sit flat).
- Each `openspec/specs/<capability>/spec.md` is **folded into `docs/standards/`** — the cut is
  chosen by you in the plan, never inferred. No OKF bundle → the fold stops and `/docs:align` is
  suggested first.
- The CLI scaffolding is dropped: `config.yaml` removed, each `.openspec.yaml` → `.specs.json`.
- The delta folders are discarded once their content is folded or confirmed obsolete.
- Non-diverged shadow copies (`.claude/skills/openspec-*`, `.claude/commands/opsx/`) and the
  `/opsx:*` wrappers are removed.

**This is one-way and loses interop with the external OpenSpec CLI** — the migrated workspace no
longer runs under `@fission-ai/openspec`. The align says so before applying, and a rename whose
blast radius reaches product code confirms on its own.

---

## 11. The other fronts

| Front | Manual | Align (structure, one pass) | Align-and-update (+ content, looped) |
| --- | --- | --- | --- |
| `docs/` — the OKF knowledge bundle | `../docs/QUENCHING.md` | `/docs:align` | `/docs:align-and-update` |
| `specs/` — this workspace | this file | `/specs:align` | `/specs:align-and-update` |
| `.claude/` — the automation surface | `../.claude/QUENCHING.md` | `/skill:align` | `/skill:align-and-update` |

`/align` runs the three aligns in dependency order on one confirmation; `/align-and-update` runs
the three conductors the same way and loops across fronts, because they feed each other (a plan's
archive distils docs the glossary must then index). A front this repo does not use simply has no
manual — the paths above are references, not promises.

The normative spec-driven facts — the layout, the plan artifact graph, the artifact formats, the
full `specs.py` surface — live in the plugin's
`skills/quenching-specs-plan-propose/references/spec-driven.md`. This file is the operator's view;
that is the specification.
