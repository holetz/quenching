# claude-quenching (plugin)

An **OKF-centric knowledge-base aligner** for the Claude Code surface of any
repository. It carries one canonical **Open Knowledge Format (OKF v0.1)** bundle
of `docs/` and the tools to install it, force an existing base into conformance,
insert new knowledge, capture terms into a fixed glossary, drain the project's Claude
Code memory into it, import external sources into it, keep the repo's `CLAUDE.md` a thin pointer over it, and organize
the repo's own **automation surface** (`.claude/skills/` + `.claude/commands/`) under one
taxonomy — so every repository that adopts the plugin looks the **same**. It also carries the repo's
**spec-driven change cycle**: six `openspec-*` skills (plus `/opsx` commands) that drive the
[OpenSpec](https://github.com/Fission-AI/OpenSpec) CLI with the OKF bundle as their
knowledge substrate.

## The nineteen skills

Every skill is `user-invocable: false` (hidden from the `/` menu) and paired with a thin
**command wrapper** — `/opsx:*` for the eight `openspec-*` skills, and for the eleven
`quenching-*` skills `/docs:*` (the nine that act on the OKF `docs/` bundle) plus `/skill:*`
(the two that act on the target's `.claude/` automation surface). Claude still auto-routes to
a skill by its `description`; the wrappers under `commands/` are the explicit user entry points.

### `quenching-align` — structure (installer + force-aligner + validator)

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

### `quenching-add` — content (insertion tool)

Classifies a new piece of information into its **home + `type` + mold**, determines
its path identity, fills the mold with a complete OKF stamp (`type` + recommended
fields + method labels, `resource` derived and never invented), writes the concept
doc, updates the folder's `index.md`, appends to `log.md`, enriches the glossary when
the concept names a repo-specific term, and validates.

Triggers: *"insert new information into the base"*, *"add a standard/table/announcement"*,
*"record knowledge in the OKF docs"*.

### `openspec-backlog` — park one task in the inbox

A quenching-native member of the `openspec-*` family (invoked as `/opsx:backlog-add`). Captures
**ONE task** into `openspec/backlog/` — the task inbox, a quenching-managed sibling of
`openspec/specs/` and `changes/`, **outside** the OKF `docs/` bundle — in seconds: a minimal
`type: task` stamp (title, one-sentence gist, timestamp), with optional `priority`
(`critical|high|medium|low`) and `tags` (themes) **only when the human states them
inline** ("park X, high priority, theme auth"). **Zero interrogation** — what was not
said is left out; a task without `priority` is untriaged, a valid state. Dedupes by
slug/title (MERGE, never clobber), regenerates the derived GENERATED zone in
`backlog/index.md`, logs the creation to the bundle's `docs/log.md`, and self-checks on write
(the OKF hook does not cover the backlog). The per-item counterpart of
`openspec-backlog-triage`.

Triggers: *"add to the backlog"*, *"park a task"*, *"capture a task"*, *"note this for
later"*.

### `openspec-backlog-triage` — prioritize the task inbox

A quenching-native member of the `openspec-*` family (invoked as `/opsx:backlog-triage`). The
prioritization sweep over the whole inbox at `openspec/backlog/`: reads every task's
frontmatter **directly** (no sub-agents — a backlog is small by nature) plus `docs/vision/`
when present, and builds **ONE triage plan** — a proposed priority + tags per untriaged task with a
one-line rationale, re-ranks of already-triaged tasks only with an explicit reason,
staleness flags, duplicate-merge suggestions. **One OK** applies the whole plan (a
rejected plan applies nothing; a human-set priority is never silently clobbered).
Completion/removal enters the plan **only when the human states a task is done** — the
removed task gains a row in the index's Completed ledger. Regenerates the zone and logs
one consolidated update.

Triggers: *"prioritize the backlog"*, *"triage the backlog"*, *"groom the backlog"*,
*"re-rank the tasks"*.

### `quenching-import` — import an external source into the bundle

The **batch** counterpart of `quenching-add`. Reads an external source — local
files/folders, or URLs — and mints **multiple** conformant OKF concept docs from it in one
force-with-one-confirmation pass: scope the source read-only, extract knowledge units and
classify each into its home + `type` + mold, dedupe within the source and against the
existing bundle, present **one** ingestion plan, then mint each doc under the insert
procedure ([`quenching-add/references/homes.md`](skills/quenching-add/references/homes.md),
its single owner — enrich cites, never restates). A Claude-native analogue of the OKF
reference implementation's `enrich` command, **without** BigQuery or heavy deps. Web
ingestion is **bounded** (seed list + host allowlist + page cap, never an open crawl);
minted docs are attributed to the source and enter `authority: background` unless proven in
the target's code; secrets/PII/transient chatter are never ingested. Additive only — it
mints and merges, never deletes. Requires an existing OKF bundle (run `quenching-align` first).

Triggers: *"import/ingest a source into the base"*, *"enrich the knowledge base from X"*,
*"generate OKF docs from these files/URLs"*, *"pull this doc/site into docs/"*.

### `quenching-learn` — capture generic knowledge

Files one piece of understanding the human states — a concept, glossary term,
explanation, mental model, or learning — into the `knowledge/` home, with a
`type: knowledge` stamp, the OKF recommended fields, `resource` derived from what
the knowledge concerns, an updated `index.md`, and a `log.md` entry. If the
information is really a contract / decision / procedure / external-asset fact, it
routes to its home via `quenching-add`. As a tail step it **enriches the glossary**
(`knowledge/glossary.md`) whenever the concept introduces a repo-specific term.

Triggers: *"add this knowledge"*, *"record what we learned"*, *"capture this concept /
glossary term"*, *"put this in the knowledge base"*.

### `quenching-glossary-backfill` — backfill the glossary from the whole bundle

Sweeps the **entire** `docs/` bundle — not just a fresh capture — for repo-specific terms
that already exist in the docs but were never fed into the glossary. Lists doc paths
cheaply, slices the bundle by home, fans a sub-agent out per slice (each returning compact
candidate terms, never full bodies), merges every slice into **one** consolidated plan, and
writes the backfill to `knowledge/glossary.md` on a single confirmation — the orchestrator
alone edits the glossary. The bulk, retroactive counterpart of the tail step the other
knowledge skills run per capture.

Triggers: *"scan the docs for glossary terms"*, *"backfill the glossary"*, *"sweep the
bundle for missing terms"*, *"find terms we never added to the glossary"*.

### `quenching-define` — add/refine one glossary term

Adds or refines **one** entry in the fixed glossary — `knowledge/glossary.md`, the repo's
A–Z lookup of terms, acronyms, and domain vocabulary (a flat, alphabetically sorted bullet
list in the same syntax every `index.md` uses; the one deliberate exception to "one concept
per file"). Confirms the term is repo-specific, derives the link to the concept doc that
defines it (never invents one), inserts the entry in alphabetical position with a
one-sentence definition, **MERGES** rather than clobbering a filled entry, and appends a
`log.md` update. The on-demand, single-term counterpart of the glossary tail step the
other knowledge skills run; `quenching-glossary-backfill` is the whole-bundle bulk counterpart.

Triggers: *"add a term to the glossary"*, *"define this term"*, *"add this acronym / jargon
to the glossary"*, *"update the glossary"*.

### `quenching-import-memory` — drain project memory into the bundle

Migrates the durable facts in the project's Claude Code memory
(`~/.claude/projects/<cwd>/memory/`) — promoting each memory into a `standard` or `knowledge`
doc in the `docs/` bundle, or a backlog `task` (always untriaged) in `openspec/backlog/` — then
**clears each memory once its doc has landed and passed the
conformance check**. Presents one migration plan and executes on a single
confirmation; a `user` memory or an unroutable fact is flagged and kept, never
silently deleted.

Triggers: *"convert the memory into docs"*, *"move project memory into the knowledge
base"*, *"turn memories into standards/backlog/knowledge"*, *"flush the memory into docs"*.

### `quenching-harness` — refactor CLAUDE.md/AGENTS.md into thin pointers

Refactors a repo's **harness files** — the root `CLAUDE.md`, every subfolder
`CLAUDE.md`, and `AGENTS.md` — into thin, honest navigation pointers over the bundle.
Inventories every harness file, classifies each unit (**KEEP** the harness-operational —
build/run/test commands, env, etiquette needed every turn; **MOVE** durable knowledge
into its `docs/` home via `quenching-add`, leaving a citing pointer; **DEDUPE** what
`docs/` already holds; **FLAG** contradictions; keep-and-report the unroutable), presents
one refactor plan, executes on a single confirmation (a product-code edit confirms on its
own), rewrites each file from the harness molds, and **self-verifies every pointer
resolves** — the validator exempts `CLAUDE.md`/`AGENTS.md`, so pointer honesty is checked
here. Move, never copy: after the run each fact lives in exactly one place.

Triggers: *"refactor CLAUDE.md"*, *"slim down CLAUDE.md"*, *"move CLAUDE.md content into
docs"*, *"make CLAUDE.md point to the knowledge base"*, *"align CLAUDE.md/AGENTS.md with docs/"*.

### `quenching-skill` + `quenching-skill-align` — the automation family

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
[`quenching-skill/references/doctrine.md`](skills/quenching-skill/references/doctrine.md)
(how a SKILL.md is written: predictability, one trigger per branch, checkable step
criteria, the no-op test) and
[`quenching-skill/references/taxonomy.md`](skills/quenching-skill/references/taxonomy.md)
(the axis, naming, mirroring, registry format); the sweep cites, never restates.

**`quenching-skill`** (per-item) mints or edits ONE conformant skill: reads the rule
(offering to create it on first run), classifies, derives name + wrapper, drafts under
the doctrine, presents ONE plan, writes on a single OK, then runs the OKF tail
(regenerate the registry zone, glossary offer, `log.md`, self-check). Without an OKF
bundle the mint still proceeds (skill + wrapper only) and suggests `quenching-align` once.

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

### `quenching-converge` — run the sweep skills to convergence

The **conductor**. Runs the plugin's sweep/structural skills as a dependency pipeline —
`quenching-align` (structure), then `quenching-import-memory` and `quenching-harness` (feed
content in from the two out-of-band stores: project memory and the harness files), then
`quenching-glossary-backfill` (backfill the glossary from the now-complete bundle) — **one pass at a
time**. The gate runs **once**, before Pass 1: a read-only assessment → **one** confirmation
authorizes the whole run; later passes narrate their plan without a gate, and a code-coupled
item still confirms on its own — each pass then runs its applicable stages → a re-assessment,
looping until a full pass changes **nothing** and the validator is clean (a fixpoint). It **conducts, never reimplements**: every change is made by the sub-skill it invokes,
under that sub-skill's own doctrine and its own confirmation for code-coupled renames. The
per-item and on-demand skills (`quenching-add`, `quenching-learn`, `quenching-define`,
`quenching-import`) are **not** loop stages — each acts on one human-stated
item or one named external source, so the cycle **surfaces** the content gaps only
a human-supplied input can fill rather than fabricating content to close them. Bounded by a pass cap and a no-progress
guard: it converges or reports the residue, never spins.

Triggers: *"run the full quenching cycle"*, *"loop the skills until the knowledge base is done"*,
*"exhaust the OKF improvement opportunities"*, *"drive the repo to OKF convergence"*, *"run all the
quenching skills in a loop"*.

## The OpenSpec flow — the `openspec-*` family + `/opsx` commands

The plugin's **spec-driven change cycle**, adapted from the skills OpenSpec 1.6.0 generates
(`metadata.generatedBy` tracks the upstream version) so target repos don't need per-repo
copies. Each skill keeps the upstream CLI-driven mechanics intact — `openspec new change`,
`status --json`, `instructions --json`, `list --json` are the contract that survives
upstream upgrades — and gains **OKF knowledge bridges**: the `docs/` bundle is read as
context going in, and durable knowledge is distilled back out.

**Requires the OpenSpec CLI**: `npm i -g @fission-ai/openspec` (≥ 1.6.0, Node ≥ 20.19), and
`openspec init` once per target repo to scaffold `openspec/{config.yaml,specs/,changes/}`.
The plugin ships no setup skill — `openspec init` is the installer.

| Skill | `/opsx` | Role + OKF bridge |
| --- | --- | --- |
| `openspec-explore` | `/opsx:explore` | Thinking partner before/during a change. Bridge: reads `knowledge/`, `glossary.md`, `standards/` as ground truth; routes durable insights to `quenching-learn` / `quenching-add` (standard) / `quenching-define`. |
| `openspec-propose` | `/opsx:propose` | Creates a change and generates all artifacts until apply-ready. Bridge: reads relevant `standards/` and glossary first; an `openspec/backlog/` task used as seed is retired into the Completed ledger when the artifacts are apply-ready (one confirmation). |
| `openspec-apply-change` | `/opsx:implement` | Implements `tasks.md` checkbox by checkbox. Bridge: reads the touched subjects' `standards/` as binding contracts; pauses on conflicts; routes durable learning to its OKF home. |
| `openspec-update-change` | `/opsx:revise` | Revises existing planning artifacts, keeps them coherent; never edits code. Faithful port. |
| `openspec-sync-specs` | `/opsx:sync-specs` | Merges a change's delta specs into `openspec/specs/` (current behavior). Boundary: `openspec/specs/` = WHAT the product does; `docs/standards/` = HOW we build — never duplicated. |
| `openspec-archive-change` | `/opsx:archive` | Checks completion, offers the sync, moves the change to `changes/archive/`. Bridge: a post-archive **distillation pass** (one plan, one OK) mints the change's durable knowledge into `docs/` — decision → `standards/` (authority-graded), understanding → `knowledge/`, terms → glossary. Nothing is bulk-copied. |

The shared facts live once — the OpenSpec layout/CLI/formats in
[`openspec-propose/references/openspec.md`](skills/openspec-propose/references/openspec.md),
the distillation doctrine in
[`openspec-archive-change/references/distill.md`](skills/openspec-archive-change/references/distill.md)
— and the `/opsx` commands are thin wrappers that invoke the skills (no duplicated bodies).
These six are **on-demand tools, not `quenching-converge` loop stages** (like enrich). The family
also has two **quenching-native** members — `openspec-backlog` (`/opsx:backlog-add`) and
`openspec-backlog-triage` (`/opsx:backlog-triage`), detailed above — that own the
`openspec/backlog/` task inbox seeding this flow (no `metadata.generatedBy`, since they are not
CLI-generated). The backlog lifecycle they close: **Capture** (`openspec-backlog`, task mold) →
**Triage** (`openspec-backlog-triage`, optional) → **Develop**
(`openspec-explore`/`openspec-propose` seed a change from the task) → **Distill** (artifacts
apply-ready → the task leaves the tree; the Completed ledger records the change).

> **Migration note:** a target repo that already carries local copies
> (`.claude/skills/openspec-*/`, `.claude/commands/opsx/`) generated by `openspec init`
> should **remove them** when adopting the plugin — otherwise both copies register the same
> triggers and command names.

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

The **task inbox** lives **outside** this bundle, at `openspec/backlog/` (`<task-slug>.md`,
`type: task`, optional `priority`/`tags`/`complexity`; a derived index zone) — a
quenching-managed sibling of `openspec/specs/` and `changes/`, captured by `openspec-backlog`
and prioritized by `openspec-backlog-triage`, not scanned by the OKF validator. An
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

## Cost model

The plugin keeps its context and token footprint predictable on three levels:

1. **Always-on metadata (shared cap).** Every skill's `description` + `when_to_use` is
   loaded into context each session, and Claude Code truncates each skill at **1,536
   combined characters** — a budget shared with every other installed plugin. All nineteen
   skills fit under the cap and carry their verbatim trigger phrases in the **second**
   sentence, so truncation can never eat them.
2. **Body on invocation.** A `SKILL.md` body loads only when the skill runs; every body
   stays well under 500 lines. Shared procedure lives once, in its owners —
   [`quenching-add/references/homes.md`](skills/quenching-add/references/homes.md)
   (the insert procedure) and
   [`quenching-align/references/conformance.md`](skills/quenching-align/references/conformance.md)
   (the checks) — and the other skills cite it, never restate it.
3. **References on demand.** `references/*.md` files are read only when a step needs them.

**Model policy** (conservative — judgment is never downgraded):

| Surface | Policy |
| --- | --- |
| `quenching-define` | `effort: low`; no model pin (mechanical single-entry edit) |
| `openspec-backlog` | `effort: low`; no model pin (mechanical single-task capture; zero interrogation, no sub-agents) |
| `openspec-backlog-triage` | no pin, no `effort` override — priority judgment inherits the session default; the human plan-gate contains misjudgment; no sub-agents |
| `quenching-glossary-backfill` | `effort: medium`; slice sub-agents `model: haiku` + `effort: low` (pure extraction, cross-checked by the orchestrator) |
| `quenching-import-memory` | classification sub-agents `model: sonnet` + `effort: low`; **executor sub-agents inherit the session model** (their self-check authorizes memory deletion) |
| `quenching-align` / `quenching-harness` | repo-wide grep/find sweeps delegable to one read-only `haiku` + `effort: low` collector; every classification stays with the orchestrator when run standalone. **Exception:** under `quenching-converge`'s parallel prep, harness's read-only discovery (steps 1–4, incl. MOVE/KEEP classification) runs in a background `Task` agent pinned `model: sonnet` — never haiku, same misclassification-risk rationale as the cycle's assessment agent |
| `quenching-converge` | per-pass read-only assessment via a `sonnet` + `effort: low` sub-agent (haiku ruled out: a false "nothing to do" ends the loop early) |
| `quenching-import` | extraction/executor sub-agents may run `model: haiku` + `effort: low` — import **deletes nothing**, so a misclassification only misfiles a doc (correctable); the orchestrator keeps each `index.md`/`log.md` honest and resolves cross-slice dedup |
| `quenching-add` / `quenching-learn` | no pin — they inherit the session model (they classify, route, and gate operations) |
| `quenching-skill` / `quenching-skill-align` | no pin, no sub-agents — classification on the axis, doctrine-grade drafting, and the plan gates inherit the session model |
| the six spec-cycle `openspec-*` skills | no pin, no sub-agents to downgrade — they run on the session model (they author artifacts, implement code, and gate the OKF distillation); the only sub-agent call is archive's optional sync delegation, which inherits the session model. (`openspec-backlog`/`-triage` have their own rows above.) |

Two rules are deliberate and must survive any future "optimization":

- **Never add `context: fork` to these skills.** Every sweep skill gates on a mid-flow
  confirmation (one plan → one OK) when run standalone — and even a cycle-authorized run
  ([`quenching-converge/references/cycle.md`](skills/quenching-converge/references/cycle.md)
  §cycle-authorization) must still surface code-coupled confirmations mid-flow, which a forked
  context cannot present.
- **Never downgrade classification or executor agents to haiku** in
  `quenching-import-memory` — a misclassification becomes a wrong memory deletion.

**Enforcement hook cost.** The `Stop` sweep is **dirty-gated** by default
(`stopScan: "dirty"`): a turn that edits no `docs/**` file costs one stat (<5 ms); a dirty
turn triggers ONE single-pass read of the bundle (each `.md` read exactly once), bounded by
`deadlineMs` checked inside the walk. `stopScan: "always"` restores the unconditional
every-turn sweep. The installed script is versioned (`okf-validate.py --version`, lockstep
with `VERSION`), and `quenching-align` step 6 offers the **upgrade** — overwrite the script
only, preserving the target's `hooks-config.json`. Details:
[`assets/hooks/README.md`](assets/hooks/README.md).

## Install

```bash
claude --plugin-dir ./plugins/claude-quenching
```

All skills reach the shared payload via `${CLAUDE_PLUGIN_ROOT}/assets/...`.

## Upgrade

Bump `version` in `.claude-plugin/plugin.json` and `VERSION` on each release; that is
the key Claude Code uses to detect and apply an upgrade.

- **0.16.0:** **verb-first command surface, honest namespaces.** Renamed the command wrappers
  so each names its action, and split the `quenching-*` surface by the artifact it touches.
  `opsx:` keeps its namespace and every `openspec-*` skill name (upstream alignment); only the
  commands change: `apply`→`implement`, `update`→`revise`, `sync`→`sync-specs`,
  `backlog`→`backlog-add`. The seven quenching-native `docs:` skills rename in lockstep with
  their command: `insert`→`add`, `enrich`→`import`, `knowledge`→`learn`, `glossary`→`define`,
  `knowledge-scan`→`glossary-backfill` (the name no longer lies), `memory-to-docs`→`import-memory`,
  `cycle`→`converge`. `align`/`harness` stay. A new **`skill:` namespace** carries the two
  `.claude/`-automation skills out of `docs:` — `quenching-skill` → `/skill:new`,
  `quenching-skill-align` → `/skill:align` (skill names unchanged, namespace honest). Clean
  cut, no compatibility aliases; the 19-skill/19-wrapper bijection is preserved.
- **0.15.0:** every skill is now `user-invocable: false` (hidden from the `/` menu) and paired
  with a thin **command wrapper** — `/opsx:*` for the eight `openspec-*` skills, `/docs:*` for
  the eleven `quenching-*` skills; Claude still auto-routes by `description`, the wrappers are the
  explicit user entry points. **Renamed** the backlog pair into the OpenSpec family:
  `quenching-backlog` → `openspec-backlog` and `quenching-backlog-triage` →
  `openspec-backlog-triage` (quenching-native — they own the `openspec/backlog/` inbox and carry
  no `metadata.generatedBy`). **Removed** `quenching-visualize` and the offline HTML diagram
  generator it drove (`assets/tools/okf-visualize.py` + the vendored `viewer/` — Cytoscape.js +
  marked). Twenty skills → **nineteen** (eleven `quenching-*` + eight `openspec-*`).
- **0.14.0:** added the **automation family** — `quenching-skill` (mint/edit ONE
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
  commands; the backlog lifecycle now seeds `openspec-propose` (the previous
  brainstorming-based flow is retired). Same release: renamed the backlog item `idea` →
  `task` (optional `priority`/`tags`; derived GENERATED zone in `backlog/index.md`;
  "Developed" → "Completed" ledger) and added `quenching-backlog` (capture) +
  `quenching-backlog-triage` (triage sweep) — ten quenching skills → twelve, eighteen in
  all.
- **0.9.0:** retired the `guides/` home into `documentation/how-to/`; added the `documentation/`
  home (Diátaxis product docs) and a shippable mkdocs-material site setup (`assets/mkdocs/`).
