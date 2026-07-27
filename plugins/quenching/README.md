# quenching (plugin)

An **OKF-centric knowledge-base aligner** for the Claude Code surface of any
repository. It carries one canonical **Open Knowledge Format (OKF v0.1)** bundle
of `docs/` and the tools to install it, force an existing base into conformance,
insert new knowledge, capture terms into a fixed glossary, drain the project's Claude
Code memory into it, import external sources into it, keep the repo's `CLAUDE.md` a thin pointer over it, and organize
the repo's own **automation surface** (`.claude/skills/` + `.claude/commands/`) under one
taxonomy — so every repository that adopts the plugin looks the **same**. It also carries the repo's
**spec-driven plan cycle**: a **fully native** `specs/` front (the thirteen `quenching-specs-*`
skills plus `/specs` commands) with the OKF bundle as its knowledge substrate — no external
CLI, driven by the bundled stdlib `specs.py`.

All of it sits behind **one interface, repeated on every front**: `align` puts a surface into
shape; `align-and-update` also pulls its content in and loops until nothing changes. Read the
next section and you know the whole plugin.

## The three fronts and the 2×4 interface

The plugin acts on **three** surfaces of a repository, and the interface is the **same on each**.
Every front has exactly two entry points, and two more span all three:

| Front | Namespace | **align** — structure, ONE pass | **align-and-update** — + content, LOOPED |
| --- | --- | --- | --- |
| `docs/` — the OKF bundle | `/docs:*` | `/docs:align` → `quenching-docs-align` | `/docs:align-and-update` → `quenching-docs-align-and-update` |
| `specs/` — the native spec-driven workspace | `/specs:*` | `/specs:align` → `quenching-specs-align` | `/specs:align-and-update` → `quenching-specs-align-and-update` |
| `.claude/` — the automation surface | `/skill:*` | `/skill:align` → `quenching-skill-align` | `/skill:align-and-update` → `quenching-skill-align-and-update` |
| **all three** | *(root)* | **`/align`** → `quenching-align-all` | **`/align-and-update`** → `quenching-align-and-update-all` |

**The two columns answer different questions.** An **align** forces a front into the canonical
*shape* — one read-only inventory → ONE consolidated plan → one OK → apply → verify — and stops.
An **align-and-update** runs that align as its first stage and then keeps going: it pulls
*content* in from wherever that front's knowledge is sitting out-of-band, and **loops** until a
whole pass changes nothing (a fixpoint).

| Front | What its align-and-update adds beyond align |
| --- | --- |
| `docs/` | drains project memory, thins the harness (moving durable knowledge into homes), backfills the glossary |
| `specs/` | archives each complete plan (**distilling** its by-products into `docs/`) and triages the inbox — the cycle actions `quenching-specs-align` only *reports*. A **3-stage** pipeline: there is no sync stage, because a plan writes its rule straight into `docs/standards/` |
| `.claude/` | audits every skill **body** against the writing doctrine — the one thing `quenching-skill-align` is forbidden to touch — and reports each violation with the `/skill:new` that fixes it |

The cross-front `/align-and-update` **loops across fronts**, because they feed each other: a
plan archive distils docs into `docs/` that the glossary must then index; the skill front
creates the rule and registry that the `docs/` listings must carry.

Every entry point shares one contract: any item whose blast radius reaches **product code**
confirms on its own, always — and inside a conducted run, so does every **plan archive**.
That contract lives once, in
[`quenching-align-and-update-all/references/convergence.md`](skills/quenching-align-and-update-all/references/convergence.md).

## The thirty skills

Every skill is `user-invocable: false` (hidden from the `/` menu) and paired with a thin
**command wrapper**. All thirty share one `quenching-<front>-<object>-<verb>` taxonomy and
split by front: `/docs:*` for the eleven that act on the OKF `docs/` bundle (one nested a level
deeper at `/docs:documentation:build`), `/specs:*` for the thirteen that act on the native `specs/`
workspace (the plan skills under `/specs:develop`, the inbox under `/specs:capture`), `/skill:*`
for the four that act on the target's `.claude/` automation surface, and the root `/align` +
`/align-and-update` for the two that span all three fronts. Claude still auto-routes to a skill by
its `description`; the wrappers under `commands/` are the explicit user entry points.

### `quenching-docs-align` — structure (installer + force-aligner + validator)

Derives the target's current `docs/` shape, maps every existing section to a
canonical **home**, and produces an **alignment plan**: which homes to scaffold,
which variant names to migrate (`docs/arquitetura/` → `docs/standards/`), which
misfiled docs to relocate, which frontmatter to stamp/normalize, which `index.md`
to (re)generate, where to establish `log.md`, and the blast radius of any rename
that reaches product code. It presents the **full plan** and executes on **one**
confirmation. A rename whose blast radius reaches product code (path constants,
imports, docstrings) is its **own** confirmation item — never folded into the batch
OK. After executing it re-runs the conformance checker on the output.

Triggers: *"align the knowledge base to OKF"*, *"install the docs structure"*,
*"force OKF conformance"*, *"migrate docs/ to the standard"*.

### `quenching-docs-add` — content (insertion tool)

Classifies a new piece of information into its **home + `type` + mold**, determines
its path identity, fills the mold with a complete OKF stamp (`type` + recommended
fields + method labels, `resource` derived and never invented), writes the concept
doc, updates the folder's `index.md`, appends to `log.md`, enriches the glossary when
the concept names a repo-specific term, and validates.

Triggers: *"insert new information into the base"*, *"add a standard/table/announcement"*,
*"record knowledge in the OKF docs"*.

### `quenching-specs-capture` — park one task in the inbox

A specs-front skill (invoked as `/specs:capture`). Captures
**ONE task** into `specs/backlog/` — the definition phase, a quenching-managed sibling of the plan
folders and `specs/archive/`, **outside** the OKF `docs/` bundle — in seconds: a minimal
`type: task` stamp (title, one-sentence gist, timestamp), with optional `priority`
(`critical|high|medium|low`) and `tags` (themes) **only when the human states them
inline** ("park X, high priority, theme auth"). **Zero interrogation** — what was not
said is left out; a task without `priority` is untriaged, a valid state. Dedupes by
slug/title (MERGE, never clobber), regenerates the derived GENERATED zone in `backlog/index.md`
via `specs.py backlog reindex`, logs the creation to the bundle's `docs/log.md`, and closes by
running the real checker over the inbox — `okf-validate.py specs/backlog --listing-root`, the same
validator that guards `docs/`, pointed at a tree the hook's `docsDir` config does not reach.
Deliberately **not** in the hot path: the glossary tail step every other capture skill runs, which
for a parked task was an expected no-op costing two bundle reads. The per-item counterpart of
`quenching-specs-triage`.

Triggers: *"add to the backlog"*, *"park a task"*, *"capture a task"*, *"note this for
later"*.

### `quenching-specs-triage` — prioritize the definition phase

A specs-front skill (invoked as `/specs:triage`). The
prioritization sweep over the whole inbox at `specs/backlog/`: reads every task's
frontmatter **directly** (no sub-agents — a backlog is small by nature) plus `docs/vision/`
when present, and builds **ONE triage plan** — a proposed priority + tags per untriaged task with a
one-line rationale, re-ranks of already-triaged tasks only with an explicit reason,
staleness flags, duplicate-merge suggestions. **One OK** applies the whole plan (a
rejected plan applies nothing; a human-set priority is never silently clobbered).
Completion/removal enters the plan **only when the human states a task is done** — the
removed task gains a row in the index's archive/ record. Regenerates the zone via
`specs.py backlog reindex` and logs one consolidated update. Stage 3 of the front's pipeline.

Triggers: *"prioritize the backlog"*, *"triage the backlog"*, *"groom the backlog"*,
*"re-rank the tasks"*.

### `quenching-docs-import` — import an external source into the bundle

The **batch** counterpart of `quenching-docs-add`. Reads an external source — local
files/folders, or URLs — and mints **multiple** conformant OKF concept docs from it in one
force-with-one-confirmation pass: scope the source read-only, extract knowledge units and
classify each into its home + `type` + mold, dedupe within the source and against the
existing bundle, present **one** ingestion plan, then mint each doc under the insert
procedure ([`quenching-docs-add/references/homes.md`](skills/quenching-docs-add/references/homes.md),
its single owner — enrich cites, never restates). A Claude-native analogue of the OKF
reference implementation's `enrich` command, **without** BigQuery or heavy deps. Web
ingestion is **bounded** (seed list + host allowlist + page cap, never an open crawl);
minted docs are attributed to the source and enter `authority: background` unless proven in
the target's code; secrets/PII/transient chatter are never ingested. Additive only — it
mints and merges, never deletes. Requires an existing OKF bundle (run `quenching-docs-align` first).

Triggers: *"import/ingest a source into the base"*, *"enrich the knowledge base from X"*,
*"generate OKF docs from these files/URLs"*, *"pull this doc/site into docs/"*.

### `quenching-docs-learn` — capture generic knowledge

Files one piece of understanding the human states — a concept, glossary term,
explanation, mental model, or learning — into the `knowledge/` home, with a
`type: knowledge` stamp, the OKF recommended fields, `resource` derived from what
the knowledge concerns, an updated `index.md`, and a `log.md` entry. If the
information is really a contract / decision / procedure / external-asset fact, it
routes to its home via `quenching-docs-add`. As a tail step it **enriches the glossary**
(`knowledge/glossary.md`) whenever the concept introduces a repo-specific term.

Triggers: *"add this knowledge"*, *"record what we learned"*, *"capture this concept /
glossary term"*, *"put this in the knowledge base"*.

### `quenching-docs-glossary-backfill` — backfill the glossary from the whole bundle

Sweeps the **entire** `docs/` bundle — not just a fresh capture — for repo-specific terms
that already exist in the docs but were never fed into the glossary. Lists doc paths
cheaply, slices the bundle by home, fans a sub-agent out per slice (each returning compact
candidate terms, never full bodies), merges every slice into **one** consolidated plan, and
writes the backfill to `knowledge/glossary.md` on a single confirmation — the orchestrator
alone edits the glossary. The bulk, retroactive counterpart of the tail step the other
knowledge skills run per capture.

Triggers: *"scan the docs for glossary terms"*, *"backfill the glossary"*, *"sweep the
bundle for missing terms"*, *"find terms we never added to the glossary"*.

### `quenching-docs-define` — add/refine one glossary term

Adds or refines **one** entry in the fixed glossary — `knowledge/glossary.md`, the repo's
A–Z lookup of terms, acronyms, and domain vocabulary (a flat, alphabetically sorted bullet
list in the same syntax every `index.md` uses; the one deliberate exception to "one concept
per file"). Confirms the term is repo-specific, derives the link to the concept doc that
defines it (never invents one), inserts the entry in alphabetical position with a
one-sentence definition, **MERGES** rather than clobbering a filled entry, and appends a
`log.md` update. The on-demand, single-term counterpart of the glossary tail step the
other knowledge skills run; `quenching-docs-glossary-backfill` is the whole-bundle bulk counterpart.

Triggers: *"add a term to the glossary"*, *"define this term"*, *"add this acronym / jargon
to the glossary"*, *"update the glossary"*.

### `quenching-docs-import-memory` — drain project memory into the bundle

Migrates the durable facts in the project's Claude Code memory
(`~/.claude/projects/<cwd>/memory/`) — promoting each memory into a `standard` or `knowledge`
doc in the `docs/` bundle, or a backlog `task` (always untriaged) in `specs/backlog/` — then
**clears each memory once its doc has landed and passed the
conformance check**. Presents one migration plan and executes on a single
confirmation; a `user` memory or an unroutable fact is flagged and kept, never
silently deleted.

Triggers: *"convert the memory into docs"*, *"move project memory into the knowledge
base"*, *"turn memories into standards/backlog/knowledge"*, *"flush the memory into docs"*.

### `quenching-docs-harness` — refactor CLAUDE.md/AGENTS.md into thin pointers

Refactors a repo's **harness files** — the root `CLAUDE.md`, every subfolder
`CLAUDE.md`, and `AGENTS.md` — into thin, honest navigation pointers over the bundle.
Inventories every harness file, classifies each unit (**KEEP** the harness-operational —
build/run/test commands, env, etiquette needed every turn; **MOVE** durable knowledge
into its `docs/` home via `quenching-docs-add`, leaving a citing pointer; **DEDUPE** what
`docs/` already holds; **FLAG** contradictions; keep-and-report the unroutable), presents
one refactor plan, executes on a single confirmation (a product-code edit confirms on its
own), rewrites each file from the harness molds, and **self-verifies every pointer
resolves** — the validator exempts `CLAUDE.md`/`AGENTS.md`, so pointer honesty is checked
here. Move, never copy: after the run each fact lives in exactly one place.

Triggers: *"refactor CLAUDE.md"*, *"slim down CLAUDE.md"*, *"move CLAUDE.md content into
docs"*, *"make CLAUDE.md point to the knowledge base"*, *"align CLAUDE.md/AGENTS.md with docs/"*.

### `quenching-docs-status` — read the bundle, change nothing

The `docs/` front's only read-only view (`/docs:status`), and the counterpart of
`quenching-specs-status`. It reports every conformance finding in the validator's own codes and
the bundle's **density** — concept docs per home with empty homes shown as `0`, glossary size,
which `standards/` subjects hold anything — then splits it into what `/docs:align` would fix on
one OK, what `/docs:align-and-update` would then drive, and what neither closes because it needs
a human.

Density figures carry **no finding code**, deliberately: a bundle can pass every check while
holding scaffolded-but-empty homes and a placeholder glossary, and that is a signal worth seeing
but not a defect list to chase. It writes nothing — `allowed-tools` carries no `Write` or `Edit`,
which is the enforcement rather than a promise — and owns no contract, citing `conformance.md`
and `cycle.md` so the preview and the sweep cannot disagree.

Triggers: *"what's the status of the docs"*, *"how healthy is the knowledge base"*, *"show me the
docs dashboard"*, *"what would /docs:align do"*, *"is the bundle conformant"*.

### `quenching-docs-documentation-build` — create/update the documentation **site**

Owns the thin **site layer** that renders the bundle's `documentation/` home as an
mkdocs-material site (invoked as `/docs:documentation:build`, the one wrapper nested a level
below its namespace, because it acts on one home rather than the bundle). That layer is the
`mkdocs.yml` + `requirements.txt` at the repo **root** — outside `docs/` — plus one
`awesome-pages` `.pages` nav file per section, inside it. The skill inventories the layer
read-only, reports every finding under a `site-*` code (config absent, unfilled
`<placeholder>`, a section with no `.pages`, a stale nav, a `docs_dir` aimed elsewhere,
an absolute `/docs/<other-home>/…` link that dies in the built HTML), presents **one** plan,
and applies on one OK — **MERGE, never clobber**: a customized `mkdocs.yml` gets only its
missing required keys, always shown as a diff, and re-aiming `docs_dir` confirms on its own.
It closes with a real `mkdocs build --strict` into a throwaway dir, and reports `unverified`
rather than claiming a build that never ran.

**It never touches a page.** Page-level drift — a section without `index.md`, an unstamped
doc, a link that escapes the site root — is *reported* with the command that fixes it
(`/docs:align`, `/docs:add`), never repaired here. `quenching-docs-align` step 7 still stamps the
**first** install as part of scaffolding; everything after that is this skill. The site is
rooted at `documentation/`: the other homes stay the team's internal surface, unpublished.

Triggers: *"create the mkdocs"*, *"set up the docs site"*, *"update mkdocs"*, *"regenerate
the docs nav"*, *"build the documentation site"*, *"the site is missing the new pages"*.

### `quenching-skill-new` + `quenching-skill-align` — the automation family

Where the other skills organize a repo's *knowledge*, this pair organizes its
**automation surface**: the repo's own `.claude/skills/` and `.claude/commands/`. One
taxonomy axis governs everything — a skill is **domain-bound** (serves ONE folder;
named as the flattened folder path + verb, `communications-teams-create`, and mirrored
by a thin command wrapper at `.claude/commands/communications/teams/create.md` →
`/communications:teams:create`) or **generic** (serves the repo as a whole; named
verb-object, never mirrored). Two OKF artifacts anchor the family in the bundle:
the **rule** at `docs/standards/automation/skills.md` (`type: standard`, born
`authority: background`) and the **registry** at
`docs/documentation/reference/automation.md` (`type: documentation`), whose
`<!-- GENERATED:BEGIN/END -->` zone is derived from `.claude/skills/*/SKILL.md`
frontmatter and written only by these two skills — the same anti-drift pattern as
`backlog/index.md`. The doctrine lives once, in
[`quenching-skill-new/references/doctrine.md`](skills/quenching-skill-new/references/doctrine.md)
(how a SKILL.md is written: predictability, one trigger per branch, checkable step
criteria, the no-op test) and
[`quenching-skill-new/references/taxonomy.md`](skills/quenching-skill-new/references/taxonomy.md)
(the axis, naming, mirroring, registry format); the sweep cites, never restates.

**`quenching-skill-new`** (per-item) mints or edits ONE conformant skill: reads the rule
(offering to create it on first run), classifies, derives name + wrapper, drafts under
the doctrine, presents ONE plan, writes on a single OK, then runs the OKF tail
(regenerate the registry zone, glossary offer, `log.md`, self-check). Without an OKF
bundle the mint still proceeds (skill + wrapper only) and suggests `quenching-docs-align` once.

Triggers: *"create a skill"*, *"mint a skill for X"*, *"organize this skill"*, *"wire a
command for this skill"*.

**`quenching-skill-align`** (sweep) migrates the *existing* surface: read-only inventory
(including directory-scoped `**/.claude/skills/`, an accepted variation), ONE
consolidated plan — renames, wrapper mirroring, rule + registry creation when missing,
keep-and-report for unclassifiables, deletion only on the human's word — applied on one
OK (a code-coupled rename confirms individually), then post-apply verification: zone
regenerated, every wrapper resolves, registry matches `.claude/skills/` exactly.

Triggers: *"organize the skills"*, *"migrate the skills to the taxonomy"*, *"align the
commands to the monorepo"*, *"standardize the automation surface"*.

### `quenching-docs-align-and-update` — the `docs/` front, aligned AND updated

The **`docs/` front's conductor**, one of three. Runs the front's sweeps as a dependency pipeline —
`quenching-docs-align` (structure), then `quenching-docs-import-memory` and `quenching-docs-harness` (feed
content in from the two out-of-band stores: project memory and the harness files), then
`quenching-docs-glossary-backfill` (backfill the glossary from the now-complete bundle) — **one pass at a
time**. The gate runs **once**, before Pass 1: a read-only assessment → **one** confirmation
authorizes the whole run; later passes narrate their plan without a gate, and a code-coupled
item still confirms on its own — each pass then runs its applicable stages → a re-assessment,
looping until a full pass changes **nothing** and the validator is clean (a fixpoint). It **conducts, never reimplements**: every change is made by the sub-skill it invokes,
under that sub-skill's own doctrine and its own confirmation for code-coupled renames. The
per-item and on-demand skills (`quenching-docs-add`, `quenching-docs-learn`, `quenching-docs-define`,
`quenching-docs-import`) are **not** loop stages — each acts on one human-stated
item or one named external source, so the cycle **surfaces** the content gaps only
a human-supplied input can fill rather than fabricating content to close them. Bounded by a pass cap and a no-progress
guard: it converges or reports the residue, never spins.

Triggers: *"align and update the docs"*, *"run the full quenching cycle"*, *"loop the skills
until the knowledge base is done"*, *"drive the repo to OKF convergence"*, *"keep aligning and
capturing until nothing's left"*.

### `quenching-skill-align-and-update` — the `.claude/` front, aligned AND updated

The **`.claude/` front's conductor**, and the plugin's most honest one. Stage 1 is
`quenching-skill-align`; Stage 2 is a **read-only doctrine audit** of every skill *body* — the
one thing the align is forbidden by invariant to touch. A body that violates
[the writing doctrine](skills/quenching-skill-new/references/doctrine.md) becomes a **finding**, not
a fix: rewriting it is authoring, and authoring needs the human whose intent the skill encodes,
so the report names the file, the violated rule, and the exact `/skill:new <name>` that opens the
edit.

This front has **no out-of-band store to drain** — unlike `docs/` (project memory, harness
files) and `specs/` (completed plans) — so it converges in **1–2 passes**, essentially
always. The loop is not ceremony: a Stage 1 rename shifts the registry and can dangle a wrapper,
and re-assessing catches that in the same run. But the skill will not pretend to more work than
the front has, and its report says so plainly.

Triggers: *"align and update the skills"*, *"bring the automation surface up to date"*, *"audit
the skills against the doctrine"*, *"run the full skill cycle"*.

### `quenching-align-all` — the three fronts, one confirmation

The **structural** cross-front conductor: where the front conductors loop, this one runs the
*one* align of each of the **three** fronts, once, in dependency order — `quenching-docs-align`
(`docs/`) →
`quenching-specs-align` (`specs/`) → `quenching-skill-align` (`.claude/`). One read-only probe of
the three fronts → **one** OK authorizes the whole run under the shared cycle-authorization
contract → each sweep runs under its own doctrine, narrating its own plan → one consolidated
report.

The order is a **dependency, not a preference**: `docs/` first because the other two write OKF
artifacts *into* the bundle (the skill front's rule + registry, the specs front's `log.md`
entry); `specs/` before `.claude/` matters **only in a migration** — a legacy `openspec/` repo
carries CLI-generated `openspec-*` skill + `opsx/` command shadow copies that
`quenching-specs-align` clears before `quenching-skill-align` would otherwise inventory them.
**Front presence decides the pass** — an absent `docs/` bundle is what the plugin installs, so
Front 1 always runs; an absent `specs/` workspace is what `quenching-specs-align` scaffolds (from
the native `assets/specs/` payload, no external tool); an empty `.claude/` surface skips Front 3
with a note. It **conducts, never reimplements**, never loops a front to force a clean result, and
never acts on a front's reported residue — it names the residue and the command that closes it.

Triggers: *"align everything"*, *"align the whole repo"*, *"run all the aligns"*, *"normalize
this repo"*, *"install quenching in this repo"*, *"set the repo up end to end"*.

### `quenching-align-and-update-all` — every front, until nothing changes anywhere

The top of the conductor hierarchy, and the **owner of the shared contract** every conductor
cites ([`references/convergence.md`](skills/quenching-align-and-update-all/references/convergence.md):
cycle-authorization, the convergence condition, the anti-spin guards, and why per-item skills are
never stages). It invokes the three *front conductors* — two levels of delegation, zero re-derived
logic — and **loops across fronts**, which is the whole reason it is not just three sequential
runs. The concrete feedback edges:

- `quenching-specs-align-and-update` archives a plan → its distillation mints docs into `docs/` → the
  `docs/` front's glossary stage must now index those terms.
- `quenching-skill-align-and-update` creates the rule and registry in `docs/` → the `docs/`
  front's `index.md` and `log.md` must list them.
- the `docs/` front's harness stage moves a fact into `docs/` → a plan reading `standards/` as a
  binding contract now finds it there instead of in `CLAUDE.md`.

A single pass leaves every one of those half-done. **Authorization nests one level**: each front
conductor inherits the run's single OK and passes it down verbatim to its stages rather than
asking again, so the human confirms **once for the whole repo** — and after that only two things
interrupt, the two the contract never covers: a rename touching product code, and a plan
archive. Cross-front pass cap **3** (each front conductor keeps its own internal cap of 5).

Triggers: *"align and update everything"*, *"bring the whole repo up to date"*, *"run the full
quenching cycle on every front"*, *"converge the repo end to end"*, *"do everything until nothing
is left"*.

## The `specs/` flow — the native `quenching-specs-*` skills + `/specs` commands

The plugin's **spec-driven plan cycle**, and it is now **entirely native**: the plugin absorbed
what it used to borrow from the external OpenSpec CLI, so there is **no `npm i -g`, no Node
runtime, no `openspec init`, no `config.yaml`, no main-spec store, and no delta format**. The
deterministic rails are the bundled stdlib `assets/bin/specs.py` (subcommands
`new`/`list`/`status`/`next`/`task`/`backlog`/`validate`/`archive`/`doctor`, uniform `--json`,
strict exit codes `0` ok · `1` findings · `2` refusal), the same self-contained mold as the OKF
hook — a skill branches on data, never on prose. `quenching-specs-align` installs it into a
target's `.claude/hooks/`. Every one of these thirteen skills reads the `docs/` bundle as context
going in and distils durable knowledge back out at archive time.

The **unit of work is a plan** — `specs/<plan-name>/` holding `proposal.md`, an optional
`design.md`, `tasks.md`, and `.specs.json` — not an "OpenSpec change". Because a plan writes its
durable rule **directly into `docs/standards/`** (honestly `authority`-graded), there is no second
store for a delta to bridge to: isolation-while-building is a real git **branch or worktree**
(offered by `quenching-specs-apply`), with merge, history, and reversion.

| Skill | `/specs` | Role + OKF bridge |
| --- | --- | --- |
| `quenching-specs-explore` | `/specs:explore` | Thinking partner before/during a plan. Bridge: reads `knowledge/`, `glossary.md`, `standards/` as ground truth; routes durable insights to `quenching-docs-learn` / `quenching-docs-add` (standard) / `quenching-docs-define`. Never implements. |
| `quenching-specs-develop` | `/specs:develop` | Creates a plan and generates its artifacts until apply-ready — **no deltas**; the `docs/standards/` docs it will write appear as `tasks.md` items and declared `## Impact` scope. Bridge: reads relevant `standards/` and glossary first; a `specs/backlog/` task used as seed is retired into the archive/ record when the artifacts are apply-ready (one confirmation). |
| `quenching-specs-refine` | `/specs:refine` | **New.** Interrogates a plan's artifacts before it is built — the questions nobody asked, generated rather than waited for. Four modes (`interview` default, `critic`, `premortem`, `alternatives`), **one question at a time with an inline recommendation**, answers accumulated and applied in **ONE** edit at the end, under a declared stop condition. Records `refined: {mode, date}` in `.specs.json`, clearing `sp-unrefined`. **Never gates** — `applyReady` is untouched. |
| `quenching-specs-apply` | `/specs:apply` | Implements `tasks.md` **and proves each task** — refuses to start on a dirty tree, **opens by offering branch/worktree isolation** (recommended, never imposed), then per task: writes the code, runs its `verify:` under the plan's declared `verification` policy, retries within a **five-attempt budget** (re-reading from scratch at two consecutive failures, reporting *blocked* at five), self-reviews the diff on four items, and **commits that task alone** as `plan/<name>: <id> <title>`. Bridge: reads the touched subjects' `standards/` as binding contracts; pauses on conflicts; writes the plan's durable rules straight into `docs/standards/`, honestly `authority`-graded; ticks each box via `specs.py task --check`. Offers the whole-branch review and chains into archive at 100%. |
| `quenching-specs-develop` | `/specs:develop` | Revises existing planning artifacts, keeps them coherent; never edits code. |
| `quenching-specs-from-claude` | `/specs:from-claude` | **New.** Turns a Claude Code native plan (`~/.claude/plans/*.md`, or a given path) into an archivable front plan, so the work gains the archive-time distillation instead of dying in the plan file: `## Context` → proposal *Why*, decisions → `design.md`, phases/steps → `tasks.md` checkboxes. Runs `specs.py new`, one confirmation; offers to link and retire a seeding backlog task. |
| `quenching-specs-archive` | `/specs:archive` | Checks completion via `specs.py status`, moves the plan to `specs/archive/YYYY-MM-DD-<name>/` via `specs.py archive`. Bridge: a post-archive **distillation pass** (one plan, one OK) — **the single bridge** — carries by-products the plan did not already write into `docs/`: understanding → `knowledge/`, terms → glossary, a follow-up → a backlog task. Nothing is synced (the behavior landed in `standards/` during apply), nothing is bulk-copied. |

The shared facts live once — the `specs/` layout, plan artifact graph, `specs.py` surface, and the
`specs/`↔`docs/` boundary in
[`quenching-specs-develop/references/spec-driven.md`](skills/quenching-specs-develop/references/spec-driven.md),
the per-artifact authoring doctrine in
[`quenching-specs-develop/references/artifacts.md`](skills/quenching-specs-develop/references/artifacts.md),
the distillation doctrine in
[`quenching-specs-archive/references/distill.md`](skills/quenching-specs-archive/references/distill.md)
— and the `/specs` commands are thin wrappers that invoke the skills (no duplicated bodies). **Two**
of the thirteen are **stages of the front's 3-stage pipeline** when `quenching-specs-align-and-update`
conducts it — `quenching-specs-archive` and `quenching-specs-triage`; the other plan
skills (`propose`, `apply`, `update`, `from-claude`) and `explore` never are, because each needs
fresh human intent a conducted pass does not have. Every skill on this front is **quenching-native**
— no `metadata.generatedBy` anywhere. The inbox pair (`quenching-specs-capture`,
`quenching-specs-triage`, detailed above) owns the `specs/backlog/` definition phase that seeds
this flow, and two more close gaps a bare plan cycle would leave open:

| Skill | `/specs` | Why it exists |
| --- | --- | --- |
| `quenching-specs-status` | `/specs:status` | The front's only **read-only** view. Active plans with task progress and state (ready to archive · in progress · blocked · stale with its age), the backlog by priority, and the `specs.py doctor`/`validate` + backlog-check results — split into what `/specs:align` would fix, what `/specs:align-and-update` would then drive, and what neither closes. It reports in the sweep's own `sp-*` vocabulary, so it doubles as an honest dry run: the plan you would be authorizing, before you authorize it. Writes nothing — its `allowed-tools` carry no `Write` or `Edit`. |
| `quenching-specs-archive` | `/specs:archive` | The exit `plan-archive` cannot give. Archiving offers to **distil the decisions** — wrong for a plan that was dropped: you would enshrine a rule nobody adopted. Abandon moves the plan to `archive/` with an `ABANDONED.md`, **syncs nothing** (there is no delta), offers to **restore the backlog task** the plan consumed at propose time (untriaged — its old ranking rested on a decision now reversed), and harvests at most `authority: background`. Never inferred from staleness, by any sweep or conductor: only a human's word starts it. |

`quenching-specs-archive` closes the one real hole in the task lifecycle. `quenching-specs-develop`
retires a seed task into the archive/ record at **apply-ready** — *developed*, not *done* — so a
plan dropped afterwards used to leave the ledger claiming work that no longer existed. That
state now has a name (`sp-ledger-orphan`, reported by both align and status) and a command that
prevents it.

### `quenching-specs-align` — force the `specs/` workspace into shape

The **third align**, and the front's installer. Read-only inventory (`specs.py doctor`,
`specs.py validate`, `specs.py list --json`, `status --json` per plan, the `backlog/`, the
`.claude/` surface) → **ONE** plan → one OK. It **fixes**: the scaffold (copies the native
`assets/specs/` payload when absent — no external tool), installs `specs.py` into
`.claude/hooks/`, applies the remedies `doctor`/`validate` declare, plan and archive names
(kebab-case canonical English; `YYYY-MM-DD-<name>` derived from `.specs.json` `created`, never
filesystem mtime), and the `backlog/` inbox (seed, `type: task` stamps, index frontmatter, the
GENERATED markers and their derived zone via `specs.py backlog reindex`). It also **migrates a
legacy `openspec/` workspace** one-way: flatten to `specs/`, fold the main spec store into
`docs/standards/`, drop `config.yaml`, rename `.openspec.yaml` → `.specs.json`, discard the
now-meaningless deltas, and clear the CLI-generated `.claude/skills/openspec-*` +
`.claude/commands/opsx/` shadow copies (a locally *diverged* copy is kept and reported). That
migration loses interop with the external OpenSpec CLI — it is deliberately one direction.

**It aligns conformance and reports the cycle** — a complete-but-unarchived plan, a blocked or
stale plan, untriaged tasks, a `specs/`↔`standards/` boundary smell are each **reported with the
skill that owns them** (`/specs:archive`, `/specs:develop`, `/specs:archive`,
`/specs:triage`), never auto-closed — it never authors a spec, moves a plan into
`archive/`, or invents a repair `specs.py` did not state. The contract — the canonical workspace,
every `sp-*` finding code, fixes vs. reports, the legacy migration — lives in
[`quenching-specs-align/references/conformance.md`](skills/quenching-specs-align/references/conformance.md).

Triggers: *"align specs"*, *"align the specs workspace"*, *"scaffold specs"*, *"make specs
conformant"*, *"clean up specs/"*, *"migrate openspec to specs"*, *"normalize the backlog and the
plans"*.

### `quenching-specs-align-and-update` — the `specs/` front, aligned AND updated

The front's conductor, and the exact complement of the align above: where `quenching-specs-align`
**reports** the cycle actions it finds, this one **drives** them. **Three** stages, in dependency
order — `quenching-specs-align` (structure) → `quenching-specs-archive` (each complete plan) →
`quenching-specs-triage` (rank what remains) — looped until a full pass changes nothing and
`specs.py doctor`/`validate` are clean. There is **no sync stage**: a plan writes its rule straight
into `docs/standards/` as it is built, so there is nothing left to merge.

Stage 2 is the front's real content stage **and** the OKF bridge: archiving a plan distils the
by-products it produced into `docs/`. It is also the one action the run's single OK deliberately
does **not** cover — every archive confirms on its own, because moving a plan out of `specs/` is
irreversible in the sense that matters and a plan whose tasks are all checked may still be waiting
on a deploy.

Three lines it never crosses: it **never proposes or implements** (those need human intent a
conducted pass lacks — no backlog task becomes a plan here, no `tasks.md` checkbox is ticked),
it **never infers completion** (`specs.py` must report every artifact `done` and every task
`- [x]`; a task leaves the backlog only when a human says it is done), and it **never hand-edits a
spec or a `standards/` doc a plan already committed**. A blocked plan, a stale plan, and a
`specs/`↔`standards/` boundary smell stay **reported**, each with its owning command. The pipeline
and routing table live in
[`quenching-specs-align-and-update/references/cycle.md`](skills/quenching-specs-align-and-update/references/cycle.md).

Triggers: *"align and update specs"*, *"bring the specs workspace up to date"*, *"close
out the finished plans and re-rank the backlog"*, *"run the full specs cycle"*.

The backlog lifecycle the inbox pair closes: **Capture** (`quenching-specs-capture`, task mold) →
**Triage** (`quenching-specs-triage`, optional) → **Develop**
(`quenching-specs-explore`/`quenching-specs-develop` seed a plan from the task) → **Distill** (artifacts
apply-ready → the task leaves the tree; the archive/ record records the plan).

> **Migration note:** a target repo that already carries a legacy external-CLI `openspec/`
> workspace — plus the local copies (`.claude/skills/openspec-*/`, `.claude/commands/opsx/`) that
> `openspec init` generated — is migrated to the native `specs/` front **one way** when it adopts
> the plugin: `/specs:align` flattens the workspace, folds the main specs into `docs/standards/`,
> drops `config.yaml`/deltas, and removes the shadow copies (keeping any locally diverged copy and
> reporting it). Interop with the external `@fission-ai/openspec` CLI is lost by design.
> `/skill:align` deliberately leaves the `openspec-*`/`opsx/` surface to `/specs:align`.

## The signature: a canonical OKF bundle of `docs/`

The plugin installs **the same tree** in every repo (adapted to what fits — a repo
without data gets no `catalog/`):

```
docs/                    # OKF bundle root
  index.md               # the ONLY index.md with frontmatter: okf_version: "0.1" + home listing
  log.md                 # bundle change history (## YYYY-MM-DD, newest first)
  standards/             # "how WE do it" (current) — architecture/ code/ naming/ data-modeling/
                         #   ci-cd/ workflows/ mlops/ quality/ platform/  (type: standard)
  catalog/               # our data — <system>/index.md · <schema>.md · <schema>/<table>.md
  vision/                # direction by area (type: vision)
  documentation/         # product docs site — Diátaxis prose (type: documentation)
  knowledge/             # generic knowledge we hold (type: knowledge) — ships fixed glossary.md (A–Z term lookup)
  reference/             # what we consume — tools/ libraries/ regulations/ (type: reference)
```

The **definition phase** lives **outside** this bundle, at `specs/backlog/` (`<task-slug>.md`,
`type: task`, optional `priority`/`tags`/`complexity`; a derived index zone) — a
quenching-managed sibling of the plan folders and `specs/archive/`, captured by `quenching-specs-capture`
and prioritized by `quenching-specs-triage`, not scanned by the OKF validator. An
agreed-but-unproven decision is a `standard` with `authority: background` (there is no separate
`decisions/` home).

**OKF-strict rules the plugin enforces:**

- `index.md` is **reserved** — a listing, **no frontmatter** (the one exception is the
  root `docs/index.md`, which carries **only** `okf_version: "0.1"`).
- Every concept doc (non-`index.md`/`log.md`) carries **non-empty `type`** from the
  fixed vocabulary above, plus the OKF recommended fields and the method's extra keys.
- `log.md` uses `## YYYY-MM-DD` headings, newest entries first.
- Links are **relative** within a home, **absolute from the bundle root** (`/docs/...`)
  across homes.
- Folder names **and concept-doc file slugs**, frontmatter keys/enums, and the `type`
  vocabulary are **canonical English** (cross-repo greppable); **body prose may follow the
  repo's language**, and identifier-derived slugs (catalog tables, repo names)
  stay verbatim.
- **Structure is aggregated and listed** — a run of prefix-clustered files
  (`nomenclatura-*.md`) folds into a subject subfolder; every folder that holds concept docs
  has an honest `index.md`. The validator flags (WARN) a missing `index.md` (`dir-no-index`),
  a listing that links to a nonexistent file (`index-broken-link`), and a concept doc nothing
  links to (`index-orphan`).

The full contract lives in the skills' `references/` (`okf-spec.md`, `taxonomy.md`,
`migration.md`, `conformance.md`, `homes.md`) and the installable payload in
[`assets/`](assets/README.md).

## What a target repo gets to *read*

Structure without explanation is a puzzle. Each of the three aligns therefore installs a
**`QUENCHING.md` operator manual** beside the front it owns — static, repo-agnostic, English,
and identical in every adopting repo:

| Manual | Installed by | Covers |
| --- | --- | --- |
| `docs/QUENCHING.md` | `quenching-docs-align` | the "I want to → run this" table, the homes and `type` vocabulary, the eleven `/docs:*` commands, the shared operating model (one plan → one OK, MERGE, generated zones), the enforcement hook and every config knob, recipes, and a finding-code → fix troubleshooting table |
| `specs/QUENCHING.md` | `quenching-specs-align` | the workspace layout, the capture → triage → explore → propose → apply → archive → distill lifecycle (and the abandon and from-claude branches off it), the thirteen `/specs:*` commands, the `specs.py` tool, the `specs/` ↔ `standards/` boundary, the OKF bridge, the backlog contract and its ledger's two meanings |
| `.claude/QUENCHING.md` | `quenching-skill-align` | the single taxonomy axis, naming and mirroring, `/skill:new` + `/skill:align`, the rule + registry artifacts, hook/settings hygiene |

They complement, never duplicate, the reserved listings: `docs/index.md` says **what** is in the
bundle, `QUENCHING.md` says **how** it is worked. `QUENCHING.md` is an **exempt** basename in
`okf-validate.py` (alongside `CLAUDE.md`/`AGENTS.md`) — a payload file, never an OKF concept.
The refresh rule is owned once, by
[`quenching-docs-align/SKILL.md`](skills/quenching-docs-align/SKILL.md) §4, and cited by the other two:
absent → install · older banner → overwrite · same-or-newer → leave · **banner removed by a
human → keep and report**. The banner's version is filled from `VERSION` at copy time, so a
release adds no new lockstep item.

## Cost model

The plugin keeps its context and token footprint predictable on three levels:

1. **Always-on metadata (shared cap).** Every command's `description` is loaded into context
   each session, and Claude Code truncates at **1,536 characters** per command — a budget
   shared with every other installed plugin. Collapsing the 28 skill+wrapper pairs into one
   file per entry point took the surface's always-on total from **30,705 characters to 2,083**
   (~7,676 → ~521 approximate tokens), a **93% cut**, measured by `skills.py budget`.

   **What that saving cost, stated plainly:** the deleted skill description is where the quoted
   trigger phrases and the `Not for:` boundary lived, so every command now reports
   `sk-trigger-position` and `sk-no-boundary` against a description written as a `/`-menu label.
   Both are warnings, so the budget looks clean while the routing information is absent — see
   `docs/standards/naming/command-surface.md` §Why there is no longer a wrapper.
2. **Body on invocation.** A command's body loads only when it runs; every body stays well
   under 500 lines. Shared procedure lives once, in its owners —
   [`docs-add/homes.md`](assets/references/docs-add/homes.md) (the insert procedure) and
   [`docs-align/conformance.md`](assets/references/docs-align/conformance.md) (the checks) —
   and the other commands cite it by `${CLAUDE_PLUGIN_ROOT}` absolute path, never restate it.
3. **References on demand.** `assets/references/**/*.md` files are read only when a step needs
   them. They sit under `assets/` rather than beside a command because `commands/**` is the only
   tree Claude Code registers — `docs/standards/architecture/plugin-layout.md`.

Because the command registry is built at **session start**, none of that is testable in the session
that changes it. `assets/bin/functional-checks.sh` is the only check that proves the surface loads:
it spawns fresh `claude -p` processes and asserts on captured tool calls that
`${CLAUDE_PLUGIN_ROOT}` substitutes in a command body, that a conductor reaches its stage by
registry name, and that a spoken phrase still routes by description alone.

**Model policy** (conservative — judgment is never downgraded):

| Surface | Policy |
| --- | --- |
| `/docs:define` | `effort: low`; no model pin (mechanical single-entry edit) |
| `/specs:capture` | `effort: low`; no model pin (mechanical single-task capture; zero interrogation, no sub-agents) |
| `/specs:triage` | no pin, no `effort` override — the *reading* is cheap (a few small frontmatter blocks) but the *output* is a ranking grounded in `vision/`, which is exactly the judgment the session model exists for; the human plan-gate contains misjudgment but should not have to catch it. No sub-agents |
| `/specs:status` | `effort: low`; no model pin, no sub-agents, **no `Write`/`Edit` in `allowed-tools`** — it classifies against a fixed finding vocabulary it does not own, and `specs.py status` is scoped to full-progress plans rather than run per plan |
| `/specs:archive` | no pin, no sub-agents — the reason, the confirmation, and the harvest are all judgment; there is nothing mechanical here to downgrade |
| `/docs:glossary-backfill` | `effort: medium`; slice sub-agents `model: haiku` + `effort: low` (pure extraction, cross-checked by the orchestrator) |
| `/docs:import-memory` | classification sub-agents `model: sonnet` + `effort: low`; **executor sub-agents inherit the session model** (their self-check authorizes memory deletion) |
| `/docs:align` / `/docs:harness` | repo-wide grep/find sweeps delegable to one read-only `haiku` + `effort: low` collector; every classification stays with the orchestrator when run standalone. **Exception:** under `/docs:align-and-update`'s parallel prep, harness's read-only discovery (steps 1–4, incl. MOVE/KEEP classification) runs in a background `Task` agent pinned `model: sonnet` — never haiku, same misclassification-risk rationale as the cycle's assessment agent |
| `/docs:align-and-update` | per-pass read-only assessment via a `sonnet` + `effort: low` sub-agent (haiku ruled out: a false "nothing to do" ends the loop early) |
| `/align` | no pin, no sub-agents — the front probe is a handful of globs and two CLI calls, and every write belongs to the sweep it invokes (which carries its own policy row) |
| `/specs:align-and-update` | no pin, **no sub-agents** — `specs.py` answers the whole assessment in one call and a backlog is small by nature, so the orchestrator reads everything itself; the archive gate is human judgment and must never be delegated |
| `/skill:align-and-update` | no pin, no sub-agents — the doctrine audit is exactly the judgment the session model exists for, and the surface is small enough to read directly |
| `/align-and-update` | no pin, no sub-agents — it only probes and delegates; the cost sits in the three front conductors, each with its own row |
| `/specs:align` | no pin; **two** repo scans cover the whole rename set (never two per rename — [`sweep-doctrine.md`](assets/references/align-all/sweep-doctrine.md) §3), and only the bucketing of a large hit list is delegable to one read-only `haiku` + `effort: low` collector, after the scans. `specs.py status` runs only for full-progress plans, and the conductor hands down its inventory instead of making align re-collect it. Every classification, `specs.py`-stated-repair judgment, and the fix-vs-report split stays with the orchestrator |
| `/docs:import` | extraction/executor sub-agents may run `model: haiku` + `effort: low` — import **deletes nothing**, so a misclassification only misfiles a doc (correctable); the orchestrator keeps each `index.md`/`log.md` honest and resolves cross-slice dedup |
| `/docs:add` / `/docs:learn` | no pin — they inherit the session model (they classify, route, and gate operations) |
| `/docs:documentation:build` | no pin, no sub-agents — the inventory is a handful of globs plus one config parse, and the expensive step is an external `mkdocs build`, not tokens; the config **merge** and the fix-vs-report split are exactly the judgment the plan gate exists to contain |
| `/skill:new` / `/skill:align` | no pin, no sub-agents — classification on the axis, doctrine-grade drafting, and the plan gates inherit the session model |
| `/specs:refine` | no pin, no sub-agents — the whole skill *is* judgment: generating the questions a plan never answered, recommending an answer to each, and deciding when the interrogation is done. There is nothing mechanical here to downgrade, and a cheap model that asks generic questions produces exactly the refinement theatre the skill exists to replace. Cost is bounded by the mode's declared stop condition, not by a model tier |
| the six plan-authoring `quenching-specs-*` skills (`explore`, `plan-propose`, `plan-update`, `plan-from-claude`, `plan-archive`, and `plan-refine`'s row above) | no pin, and **no sub-agents at all** — they run on the session model (they author artifacts, offer branch/worktree isolation, and gate the OKF distillation). The expensive steps are the git and `specs.py` calls, not tokens. (`/specs:apply`, `/specs:align`, `/specs:align-and-update`, `/specs:status`, `/specs:archive`, and `/specs:capture`/`-triage` have their own rows.) |
| `/specs:apply` | no pin. **Amended:** a per-task **executor sub-agent is now permitted** when the task declares `files:` and touches no `docs/` — pinned to the **session model, never `haiku`** (it writes production code, the same rationale that protects `/docs:import-memory`'s executors). The orchestrator keeps plan selection, every confirmation, every `specs.py task --check`/`--attempt`, every `docs/standards/` write, the commit, and the pause decision. Two tasks run concurrently only when `specs.py parallel` reports the `[P]` group eligible; serial is the default. **This is not `context: fork`** — the orchestrator stays in the live conversation, so the never-fork rule is untouched (`assets/references/specs-apply/execution.md` §This is not `context: fork`) |

Two rules are deliberate and must survive any future "optimization":

- **Never add `context: fork` to these skills.** Every sweep skill gates on a mid-flow
  confirmation (one plan → one OK) when run standalone — and even a cycle-authorized run
  ([`/align-and-update/references/convergence.md`](assets/references/align-and-update-all/convergence.md)
  §cycle-authorization) must still surface code-coupled confirmations mid-flow, which a forked
  context cannot present.
- **Never downgrade classification or executor agents to haiku** in
  `/docs:import-memory` — a misclassification becomes a wrong memory deletion.

**Enforcement hook cost.** The `Stop` sweep is **dirty-gated** by default
(`stopScan: "dirty"`): a turn that edits no `docs/**` file costs one stat (<5 ms); a dirty
turn triggers ONE single-pass read of the bundle (each `.md` read exactly once), bounded by
`deadlineMs` checked inside the walk. `stopScan: "always"` restores the unconditional
every-turn sweep. The installed script is versioned (`okf-validate.py --version`, lockstep
with `VERSION`), and `/docs:align` step 6 offers the **upgrade** — overwrite the script
only, preserving the target's `hooks-config.json`. Details:
[`assets/hooks/README.md`](assets/hooks/README.md).

## Install

```bash
claude --plugin-dir ./plugins/quenching
```

All skills reach the shared payload via `${CLAUDE_PLUGIN_ROOT}/assets/...`.

## Upgrade

Bump `version` in `.claude-plugin/plugin.json` and `VERSION` on each release; that is
the key Claude Code uses to detect and apply an upgrade. Keep the `VERSION` constant in **both**
shipped scripts — `assets/hooks/okf-validate.py` and `assets/bin/specs.py` — in lockstep with that
pair, since each one's `--version` is what its installing align compares against an already-installed
copy in a target repo.

- **1.0.0:** **the middle front went fully native — the external OpenSpec CLI is gone.** The
  `openspec/` workspace this plugin used to *drive* (`@fission-ai/openspec`, `openspec init`,
  `config.yaml`, a main-spec store, delta specs) is replaced by a **native `specs/` front** the
  plugin owns end to end. There is **no `npm i -g`, no Node prerequisite, no delta format**: the
  deterministic rails are the new bundled stdlib **`assets/bin/specs.py`**
  (`new`/`list`/`status`/`next`/`task`/`backlog`/`validate`/`archive`/`doctor`, uniform `--json`,
  exit codes `0`/`1`/`2`), the second self-contained tool beside `okf-validate.py`, installed by
  `quenching-specs-align` into a target's `.claude/hooks/`. The **unit of work is a plan**
  (`specs/<plan-name>/`: `proposal.md`, `design.md`, `tasks.md`, `.specs.json`), not an
  "OpenSpec change" — and because a plan writes its durable rule **straight into
  `docs/standards/`**, honestly `authority`-graded, there is nothing to sync: isolation-while-building
  is a real git **branch or worktree** (offered by `/specs:apply`), not a markdown delta. The
  `specs/`-front conductor pipeline drops to **3 stages** (align → plan-archive → backlog-triage) —
  the old sync stage and `openspec-sync-specs` skill are **removed**. Commands moved from `/opsx:*`
  to **`/specs:*`** (plan skills under `/specs:develop`, inbox under `/specs:capture`), the inbox
  from `openspec/backlog/` to **`specs/backlog/`**, and every finding code from `os-*` to `sp-*`.
  All twenty-seven skills now share **one `quenching-<front>-<object>-<verb>` taxonomy** — no
  separate `openspec-*` family, no `metadata.generatedBy` anywhere. New
  **`quenching-specs-from-claude`** (`/specs:from-claude`) turns a `~/.claude/plans/*.md`
  file into an archivable plan so ad-hoc work gains the archive-time distillation. `quenching-specs-align`
  **migrates a legacy `openspec/` workspace one-way** (flatten, fold main specs into
  `docs/standards/`, drop `config.yaml`/deltas, clear the CLI shadow copies) — interop with the
  external CLI is lost by design. Still **twenty-seven** skills; the skill↔wrapper bijection holds
  at 27↔27.
- **0.19.0:** **the `openspec/` front's lifecycle closed, and the sweep contract given one
  owner.** Two new quenching-native skills complete the front. **`quenching-specs-status`**
  (`/specs:status`) is its only read-only view — changes with progress and state, the backlog by
  priority, the three verifier results, split into what `/specs:align` would fix, what
  `/specs:align-and-update` would drive, and what neither closes; it reports in the sweep's own
  `os-*` vocabulary, so it is an honest dry run of the sweep you are about to authorize.
  **`quenching-specs-archive`** (`/specs:archive`) is the exit `archive-change` could not give: a
  change that will **not** be built is archived with an `ABANDONED.md` and **no spec sync**, its
  seed backlog task is offered back (untriaged), and the harvest is capped at
  `authority: background`. That closes the one real hole in the task lifecycle — `quenching-specs-develop`
  retires a seed task at **apply-ready** (*developed*, not *done*), so a change dropped afterwards
  used to leave the archive/ record claiming work that no longer existed; that state now has a
  name (`os-ledger-orphan`, with `os-ledger-in-flight` for its healthy sibling) and a command that
  prevents it. Abandonment is never inferred: no sweep and no conductor may invoke it, at any
  authorization level.
  **Redundancy removed.** The three aligns' shared doctrine — convergence over accommodation, one
  plan → one OK with code-coupled items gating individually, the cycle-authorized narration
  exception, blast radius, MERGE-never-clobber, never-delete-on-a-guess,
  align-conformance-report-the-cycle — now lives once in
  [`quenching-align-all/references/sweep-doctrine.md`](skills/quenching-align-all/references/sweep-doctrine.md),
  and each align states only its own front's deltas. The `openspec/` ↔ `docs/` boundary is
  declared normatively once, in `quenching-specs-develop/references/openspec.md` §Boundary. The backlog's
  prose "self-check" is gone: `okf-validate.py` gained **`--listing-root`** and now checks
  `openspec/backlog/` for real (`type: task` is also exempted from the `resource` recommendation,
  since the mold omits it on purpose) — the same checker that guards `docs/`, pointed at a tree
  the hook's `docsDir` never reaches.
  **Performance.** `quenching-specs-align-and-update` hands its assessment inventory down to
  `quenching-specs-align` instead of making it re-collect against an untouched disk (a pass paid for
  `doctor`/`validate`/`list --json` three times); `status --json` is scoped to full-progress
  changes rather than run per active change; the rename blast-radius sweep is **two** repo scans
  for the whole set instead of two per rename; `quenching-specs-archive` invokes
  `openspec-sync-specs` directly via `Skill` with the delta analysis it already built, instead of
  spending a `general-purpose` sub-agent to re-derive it; and the task-capture hot path drops the
  glossary tail step, which was an expected no-op costing two bundle reads on a path whose whole
  contract is "seconds".
  **Defects fixed.** Eleven references to three commands that do not exist (`/opsx:implement`,
  `/opsx:archive`, `/opsx:revise` — CLI names that survived the adaptation) now point at the real
  wrappers. Six skills instructed tools their `allowed-tools` did not grant (`AskUserQuestion`,
  `TodoWrite`, `Task`/`Skill` in archive, `Bash` in both backlog skills). The two backlog
  descriptions said "OKF backlog", contradicting every other statement that the inbox is outside
  the bundle. The `/docs:*` command count in the `docs/QUENCHING.md` row said nine while the
  skill count beside it said ten — both now read the same number.
  **The documentation site got an owner.** New **`quenching-docs-documentation-build`**
  (`/docs:documentation:build`) owns the mkdocs-material **site layer** over the `documentation/`
  home end to end: install, config **merge** (missing required keys only, shown as a diff),
  `.pages` nav regeneration as sections come and go, `site/` gitignore, the opt-in Pages workflow,
  and a real `mkdocs build --strict` verification that says `unverified` rather than lying. Until
  now that layer was stamped **once** by `quenching-docs-align` step 7 and then drifted with no command
  to fix it: a section added later had no `.pages`, and a customized `mkdocs.yml` had nowhere to be
  merged forward. The new skill touches the **site layer only** — page-level drift is reported with
  the command that fixes it, never repaired — and align's step 7 now names it as the owner it hands
  off to. It is an on-demand tool, deliberately **not** a stage of `quenching-docs-align-and-update`'s
  loop (like `quenching-docs-import`): a site build is a publishing act, not part of reaching an OKF
  fixpoint. Twenty-four skills → **twenty-seven** (fifteen `quenching-*` + twelve `openspec-*`);
  the skill↔wrapper bijection holds at 27↔27.
- **0.18.0:** **the interface completed — one 2×4 matrix, and `converge` renamed.** 0.17.0 gave
  every front an `align`; this release gives every front an **`align-and-update`** and renames
  the concept so it says what it does. `quenching-converge` → **`quenching-docs-align-and-update`**
  (`/docs:converge` → `/docs:align-and-update`) — clean cut, no compatibility alias. New
  **`quenching-specs-align-and-update`** (`/specs:align-and-update`) drives the cycle actions
  `quenching-specs-align` only reports: align → archive each complete change (syncing specs and
  distilling into `docs/`) → sync leftover deltas → triage the inbox, looped; **each archive
  confirms on its own**. New **`quenching-skill-align-and-update`** (`/skill:align-and-update`)
  adds the one thing the align is forbidden to do — a **read-only doctrine audit of every skill
  body**, reported with the `/skill:new` that fixes it, never rewritten. New
  **`quenching-align-and-update-all`** (root `/align-and-update`) loops all three fronts,
  because they feed each other (an archive's distillation is glossary work; the skill front's
  registry is a `docs/` listing). **Architectural fix:** the cycle-authorization + convergence
  contract left `quenching-converge/references/cycle.md` — where it had become misplaced, being
  cited by every conductor — for its own neutral owner,
  `quenching-align-and-update-all/references/convergence.md`; each front's `cycle.md` now holds
  only that front's pipeline and routing. The contract also grew a second never-covered class
  beside code-coupled items: **irreversible cycle actions** (an OpenSpec archive, a backlog
  removal) always gate individually, and authorization **nests one level** so the cross-front
  run still costs exactly one OK. Twenty-one skills → **twenty-four** (fourteen `quenching-*` +
  ten `openspec-*`); the skill↔wrapper bijection holds at 24↔24.
- **0.17.0:** **one interface across the three fronts.** The plugin acts on three surfaces —
  `docs/`, `openspec/`, `.claude/` — but only two had an align sweep. New **`quenching-specs-align`**
  (`/specs:align`, quenching-native) gives the `openspec/` workspace the same
  install-and-force-conformance entry point: scaffold via `openspec init`, doctor/validate,
  canonical change + archive names, the `backlog/` inbox and its derived zone, `config.yaml`'s
  `context:` thinned into a pointer at `docs/`, and removal of the CLI-generated
  `.claude/skills/openspec-*` + `.claude/commands/opsx/` shadow copies — with cycle actions
  (archive, triage, sync, boundary smells) **reported, never driven**. Its contract lives in
  the new `quenching-specs-align/references/conformance.md`; `quenching-skill-align` now explicitly
  leaves the `openspec-*`/`opsx/` surface to it. New **`quenching-align-all`** (root `/align`)
  is the second conductor: the three aligns in dependency order (`docs/` → `openspec/` →
  `.claude/`) on **one** confirmation, orthogonal to `quenching-docs-align-and-update` (which loops the
  `docs/` front alone to a fixpoint). The cycle-authorization contract in
  `quenching-docs-align-and-update/references/cycle.md` is now the shared normative home for **both**
  conductors. Nineteen skills → **twenty-one** (twelve `quenching-*` + nine `openspec-*`), and
  the skill↔wrapper bijection is preserved.
  Same release: **each front now installs a `QUENCHING.md` operator manual** — the answer to
  "how is this repo operated?" finally ships *into* the target instead of living only in this
  README. New payload files `assets/docs/QUENCHING.md`, `assets/openspec/QUENCHING.md`, and
  `assets/claude/QUENCHING.md` are copied by their front's align under a four-branch refresh
  rule owned once by `quenching-docs-align/SKILL.md` §4 (absent → install · older banner → overwrite
  · same-or-newer → leave · **banner removed by a human → keep and report**), with the version
  filled from `VERSION` at copy time. `QUENCHING.md` joins `CLAUDE.md`/`AGENTS.md` as an
  **exempt** basename in `okf-validate.py`, so the manual is never stamped, never converted to
  `index.md`, and never counted as an orphan; the `README.md` → `index.md` migration rule is
  untouched. The root `docs/index.md` and the root-harness mold now point at the manual.
- **0.16.0:** **verb-first command surface, honest namespaces.** Renamed the command wrappers
  so each names its action, and split the `quenching-*` surface by the artifact it touches.
  `opsx:` keeps its namespace and every `openspec-*` skill name (upstream alignment); only the
  commands change: `apply`→`implement`, `update`→`revise`, `sync`→`sync-specs`,
  `backlog`→`backlog-add`. The seven quenching-native `docs:` skills rename in lockstep with
  their command: `insert`→`add`, `enrich`→`import`, `knowledge`→`learn`, `glossary`→`define`,
  `knowledge-scan`→`glossary-backfill` (the name no longer lies), `memory-to-docs`→`import-memory`,
  `cycle`→`converge`. `align`/`harness` stay. A new **`skill:` namespace** carries the two
  `.claude/`-automation skills out of `docs:` — `quenching-skill-new` → `/skill:new`,
  `quenching-skill-align` → `/skill:align` (skill names unchanged, namespace honest). Clean
  cut, no compatibility aliases; the 19-skill/19-wrapper bijection is preserved.
- **0.15.0:** every skill is now `user-invocable: false` (hidden from the `/` menu) and paired
  with a thin **command wrapper** — `/opsx:*` for the eight `openspec-*` skills, `/docs:*` for
  the eleven `quenching-*` skills; Claude still auto-routes by `description`, the wrappers are the
  explicit user entry points. **Renamed** the backlog pair into the OpenSpec family:
  `quenching-backlog` → `quenching-specs-capture` and `quenching-backlog-triage` →
  `quenching-specs-triage` (quenching-native — they own the `openspec/backlog/` inbox and carry
  no `metadata.generatedBy`). **Removed** `quenching-visualize` and the offline HTML diagram
  generator it drove (`assets/tools/okf-visualize.py` + the vendored `viewer/` — Cytoscape.js +
  marked). Twenty skills → **nineteen** (eleven `quenching-*` + eight `openspec-*`).
- **0.14.0:** added the **automation family** — `quenching-skill-new` (mint/edit ONE
  conformant skill: single-axis classification domain-bound × generic, flattened-path
  naming, mirrored command wrapper, writing doctrine, OKF tail) and
  `quenching-skill-align` (migrate the existing `.claude/skills/` + `.claude/commands/`
  surface to the taxonomy in one plan → one OK). Two OKF artifacts now maintained in
  target repos: the rule `docs/standards/automation/skills.md` (born
  `authority: background`) and the registry `docs/documentation/reference/automation.md`
  with a GENERATED zone only the pair writes. New `assets/templates/automation/` molds
  (skill, command wrapper, registry, standard). Fourteen quenching skills → **twenty** in
  all.
- **0.13.0:** straightened the work pipeline to `openspec/backlog/` (task) →
  `openspec/changes/…` (design records the decision) → `docs/standards/` (proven rule), with no
  middle element. **Moved the backlog out of the OKF bundle** to `openspec/backlog/` — a
  quenching-managed sibling of `specs/`/`changes/`, no longer scanned by `okf-validate.py`, and
  `type: task` left the OKF `type` vocabulary; `quenching-backlog`/`-triage` still own capture,
  triage, the derived index zone, and an on-write self-check (the new
  `quenching-backlog/references/backlog-zone.md` is its single owner). **Retired the standalone
  `decisions/` ADR home**: an agreed-but-unproven decision is now a `standards/` doc with
  `authority: background`, a proven one `authority: current`; a change's rationale/alternatives
  live in its `design.md` while active and distill to a `standard` at archive time.
  `migration.md` gains rules (§1e/§1f) to relocate an existing `docs/backlog/` → `openspec/backlog/`
  and restamp `docs/decisions/` ADRs into `standards/`. Still **eighteen** skills.
- **0.12.0:** narrowed the OKF taxonomy from eleven homes to **nine** — retired the
  `communications/` and `presentations/` homes (and dropped the leftover empty
  `superpowers/` folder), removing the `communication`/`communication-template` types from
  the vocabulary (the `sidecar` type stays, now scoped to `reference/regulations/` extracts).
  Same release: added an optional **`complexity`** field to backlog tasks — a rough size in
  development hours, stamped only when stated (like `priority`/`tags`), surfaced as a column
  in `backlog/index.md`'s derived zone and proposable by `quenching-backlog-triage`.
- **0.11.0:** absorbed the OpenSpec spec-driven cycle — six `openspec-*` skills (adapted
  from OpenSpec 1.6.0's generated skills, with OKF knowledge bridges) plus thin `/opsx`
  commands; the backlog lifecycle now seeds `quenching-specs-develop` (the previous
  brainstorming-based flow is retired). Same release: renamed the backlog item `idea` →
  `task` (optional `priority`/`tags`; derived GENERATED zone in `backlog/index.md`;
  "Developed" → "Completed" ledger) and added `quenching-backlog` (capture) +
  `quenching-backlog-triage` (triage sweep) — ten quenching skills → twelve, eighteen in
  all.
- **0.9.0:** retired the `guides/` home into `documentation/how-to/`; added the `documentation/`
  home (Diátaxis product docs) and a shippable mkdocs-material site setup (`assets/mkdocs/`).
