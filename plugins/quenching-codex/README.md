# quenching-codex (generated)

This plugin is generated from `plugins/quenching/`, which is the only editable source.
Run `python3 scripts/sync_codex_plugin.py --write` to refresh it.

# quenching (plugin)

An **OKF-centric knowledge-base aligner** for the Codex surface of any
repository. It carries one canonical **Open Knowledge Format (OKF v0.1)** bundle
of `/.knowledge/` and the tools to install it, force an existing base into conformance,
insert new knowledge, capture terms into a fixed glossary, drain the project's Codex
Code memory into it, import external sources into it, keep the repo's `AGENTS.md` a thin pointer over it, and organize
the repo's own **automation surface** (`.agents/skills/` + `.agents/skills/`) under one
taxonomy — so every repository that adopts the plugin looks the **same**. It also carries the repo's
**spec-driven plan cycle**: the ten `quenching-specs-*` commands over a `specs` front whose **backend is
configurable** — `files` (a dedicated branch), `github`, or `azure-boards` — with the OKF bundle
as its knowledge substrate, driven end to end by the bundled stdlib `cq specs`.

All of it sits behind **one interface, repeated on every front**: ONE `align` per front —
probe-first, so a clean front costs a couple of tool calls — that forces the structure into
shape and carries that front's content stages. Read the next section and you know the whole
plugin.

## The three fronts, the fourth pillar, and the one align per front

The plugin acts on **three** surfaces of a repository, and the interface is the **same on each**.
Every front has exactly ONE align, and one more spans all three. A fourth axis, `git`, is a
**pillar** rather than a front — it converges no tree of its own, so it carries no align at all
(see [`architecture/align-surface.md`](../../.knowledge/standards/architecture/align-surface.md)
§The fourth pillar has no align):

| Front / pillar | Namespace | **align** — probe-first, structure + content |
| --- | --- | --- |
| `/.knowledge/` — the OKF bundle | `quenching-knowledge-*` | `quenching-knowledge-align` |
| `/.specs/` — the native spec-driven workspace | `quenching-specs-*` | `quenching-specs-align` |
| `.agents/` — the automation surface | `quenching-components-*` | `quenching-components-align` |
| *(pillar)* — a repository's own git facts | `quenching-git-*` | **none** |
| **all three fronts** | *(root)* | **`/align`** |

**The probe comes before the inventory.** Each align opens by running its front's own verifier
(`cq knowledge validate`, `cq specs doctor`/`validate`, `cq components doctor`/`lint`) and stops when it
finds nothing — no inventory, no plan, no confirmation. Otherwise: one read-only inventory → ONE
consolidated plan → one OK → apply → verify, then the front's content stages, each run only when
the probe found it work:

| Front | Content its align carries beyond structure |
| --- | --- |
| `docs` | drains project memory, thins the harness (moving durable knowledge into homes), and OFFERS the glossary backfill on a cheap proxy — looping to a fixpoint, the one front with a real internal loop |
| `specs` | none driven — an empty section, a complete spec awaiting its close, an unresolved discovery are each **reported with the command that owns it**; every cycle action needs fresh human intent |
| `.agents/` | audits every command **body** against the writing doctrine — the one thing the migration itself is forbidden to fix — and reports each violation with the `quenching-components-command-new` that closes it |

The cross-front `/align` conducts the three in dependency order on one nested OK and **loops
across fronts**, because they feed each other: a spec's distillation is glossary work the
`docs` front must then index; the skill front creates the rule and registry that the `docs`
listings must carry.

The **cycle conductor** is the second conductor: `quenching-specs-cycle` conducts the lifecycle of
ONE spec — capture, define, build, close — entering at the derived stage, invoking each stage as the
command that owns it, and writing nothing itself. It runs as **two halves authorized separately**,
defining and then building, because deciding what a spec is and deciding to build it are two
decisions and no gear collapses that seam. It shares the cycle-authorization contract with `/align`,
and derives each half's gears plan from the spec's `priority.complexity`
([`specs-cycle/gears.md`](assets/references/specs-cycle/gears.md)).

**N specs is a different run, and a different shape for each regime.**
`quenching-specs-execute-queue` builds N as a **serial queue over a single isolation**;
`quenching-specs-develop-batch` defines N as a **parallel batch**. Neither has a gear: both derive
their run from the fan-out contract
([`specs-fanout/fanout.md`](assets/references/specs-fanout/fanout.md)), whose criterion is one —
whatever writes to the working tree serializes, whatever does not, does not.

Every entry point shares one contract: any item whose blast radius reaches **product code**
confirms on its own, always — and inside a conducted run, so does every **irreversible close**.
That contract lives once, in
[`align/convergence.md`](assets/references/align/convergence.md).

## The thirty-four commands

**One file per entry point** — Codex merged custom commands into skills, so each
`commands/<path>.md` carries both the description that routes to it and the body that runs;
there is no `skills/` tree and no wrapper. Measured by `cq components doctor --json`, never
transcribed by hand — a number written into prose goes stale the first time a command is minted
([`naming/command-surface.md`](../../.knowledge/standards/naming/command-surface.md) §The surface
invariant). The thirty-four split by front and pillar: `quenching-knowledge-*` for the nine
that act on the OKF `/.knowledge/` bundle (one nested a level deeper at `quenching-knowledge-documentation-build`),
`quenching-specs-*` for the ten that act on the native `/.specs/` workspace (three of them
conduct more than one stage — `quenching-specs-cycle` over one spec, `quenching-specs-execute-queue`
and `quenching-specs-develop-batch` over N), `quenching-components-*` for the seven that
act on the target's `.agents/` automation surface (six of them nested a level deeper, only
`quenching-components-align` flat), `quenching-git-*` for the **seven** that act on a
repository's own git facts — `branch`, `commit`, `pr:create`, `merge`, `sync`, `cleanup`,
`pr:review` — none of them nested more than the two `pr:` verbs, none of them carrying an
`align` (§The three fronts, the fourth pillar, and the one align per front, above), and the
root `/align` for the one that spans the three fronts. Codex
auto-routes to a command by its `description`; typing the command is the explicit entry point.

### The `git` pillar — a repository's own git facts, minted alongside the three fronts

| Command | Does |
| --- | --- |
| `quenching-git-branch` | Takes isolation for a build — worktree, branch, or in place — recommending a worktree, stating its cost, and stamping the `branch:` record. |
| `quenching-git-commit` | Commits what is already staged, under the target's own convention when one is declared. Never `git add -A`. |
| `quenching-git-pr-create` | Pushes and opens a pull request, with `Closes #<n>` when an issue is named, reporting plainly whether that keyword will actually close it. |
| `quenching-git-merge` | Merges a branch home on one of four strategies, offered and never chosen for the human. |
| `quenching-git-sync` | Rebases a work branch onto the latest base, with `--update-refs` so a stacked branch is not orphaned. |
| `quenching-git-cleanup` | Prunes branches merged or gone and worktrees git still registers with no directory on disk — nothing pruned the human did not pick from that report. |
| `quenching-git-pr-review` | Works through a PR's unresolved review threads, one confirmation per thread. |

None of the seven carries an `align`: the pillar converges no tree, only answers questions about
the target's own live git state, so there is nothing a probe could find drifted
([`architecture/align-surface.md`](../../.knowledge/standards/architecture/align-surface.md) §The
fourth pillar has no align). The `specs` front hands off to this pillar rather than executing git
itself — `quenching-specs-execute` invokes `git:branch` for isolation, `quenching-specs-conclude`
reviews, distils, archives and proves the pre-merge gate green, then **names**
`git:pr:create`/`git:merge` as the human's own next command instead of running either.

> The per-command prose below predates the v3 `specs` fold and the align fold — the surface
> facts above and in `AGENTS.md` win where they disagree; a full rewrite is parked as its own
> spec.

### `quenching-knowledge-align` — structure (installer + force-aligner + validator)

Derives the target's current `/.knowledge/` shape, maps every existing section to a
canonical **home**, and produces an **alignment plan**: which homes to scaffold,
which variant names to migrate (a non-English `/.knowledge/<arquitetura>/` → `/.knowledge/standards/`), which
misfiled docs to relocate, which frontmatter to stamp/normalize, which `index.md`
to (re)generate, and the blast radius of any rename that reaches product code. It
presents the **full plan** and executes on **one**
confirmation. A rename whose blast radius reaches product code (path constants,
imports, docstrings) is its **own** confirmation item — never folded into the batch
OK. After executing it re-runs the conformance checker on the output.

Triggers: *"align the knowledge base to OKF"*, *"install the docs structure"*,
*"force OKF conformance"*, *"migrate /.knowledge/ to the standard"*.

### `quenching-knowledge-add` — content (insertion tool)

Classifies a new piece of information into its **home + `type` + mold**, determines
its path identity, fills the mold with a complete OKF stamp (`type` + recommended
fields + method labels, `resource` derived and never invented), writes the concept
doc, updates the folder's `index.md`, enriches the glossary when the concept names
a repo-specific term, and validates.

Triggers: *"insert new information into the base"*, *"add a standard/table/announcement"*,
*"record knowledge in the OKF docs"*.

### `quenching-specs-triage` — rank the whole front

The prioritization sweep over `/.specs/plans/`: reads every spec's
frontmatter and derived stage **directly** (no sub-agents — a front is small by nature) plus
`/.knowledge/vision/` when present, and builds **ONE** ordered table with a one-line reason per row —
re-ranks of already-ranked specs only with an explicit reason, staleness flags, duplicate-merge
suggestions. **One OK** applies the whole plan (a rejected plan applies nothing; a human-set
ranking is never silently clobbered), writing each spec's
`priority: {level, criticality, complexity, date}` record and nothing else. Its output is what
`cq specs next --front` ranks on. It never removes a spec, never infers completion, and never treats
staleness as abandonment.

Triggers: *"triage the specs"*, *"prioritize the front"*, *"rank the plans"*,
*"re-rank these"*.

### `quenching-knowledge-import` — import an external source into the bundle

The **batch** counterpart of `quenching-knowledge-add`. Reads an external source — local
files/folders, or URLs — and mints **multiple** conformant OKF concept docs from it in one
force-with-one-confirmation pass: scope the source read-only, extract knowledge units and
classify each into its home + `type` + mold, dedupe within the source and against the
existing bundle, present **one** ingestion plan, then mint each doc under the insert
procedure ([`knowledge-add/homes.md`](assets/references/knowledge-add/homes.md),
its single owner — enrich cites, never restates). A Codex-native analogue of the OKF
reference implementation's `enrich` command, **without** BigQuery or heavy deps. Web
ingestion is **bounded** (seed list + host allowlist + page cap, never an open crawl);
minted docs are attributed to the source and enter `authority: background` unless proven in
the target's code; secrets/PII/transient chatter are never ingested. Additive only — it
mints and merges, never deletes. Requires an existing OKF bundle (run `quenching-knowledge-align` first).

Triggers: *"import/ingest a source into the base"*, *"enrich the knowledge base from X"*,
*"generate OKF docs from these files/URLs"*, *"pull this doc/site into /.knowledge/"*.

### `quenching-knowledge-learn` — capture generic knowledge

Files one piece of understanding the human states — a concept, glossary term,
explanation, mental model, or learning — into the `concepts/` home, with a
`type: concept` stamp, the OKF recommended fields, `resource` derived from what
the knowledge concerns, and an updated `index.md`. If the information is really a
contract / decision / procedure / external-asset fact, it
routes to its home via `quenching-knowledge-add`. As a tail step it **enriches the glossary**
(`glossary.md`) whenever the concept introduces a repo-specific term.

Triggers: *"add this knowledge"*, *"record what we learned"*, *"capture this concept /
glossary term"*, *"put this in the knowledge base"*.

### `quenching-knowledge-glossary-backfill` — backfill the glossary from the whole bundle

Sweeps the **entire** `/.knowledge/` bundle — not just a fresh capture — for repo-specific terms
that already exist in the docs but were never fed into the glossary. Lists doc paths
cheaply, slices the bundle by home, fans a sub-agent out per slice (each returning compact
candidate terms, never full bodies), merges every slice into **one** consolidated plan, and
writes the backfill to `glossary.md` on a single confirmation — the orchestrator
alone edits the glossary. The bulk, retroactive counterpart of the tail step the other
knowledge skills run per capture.

Triggers: *"scan the docs for glossary terms"*, *"backfill the glossary"*, *"sweep the
bundle for missing terms"*, *"find terms we never added to the glossary"*.

### `quenching-knowledge-define` — add/refine one glossary term

Adds or refines **one** entry in the fixed glossary — `glossary.md`, the repo's
A–Z lookup of terms, acronyms, and domain vocabulary (a flat, alphabetically sorted bullet
list in the same syntax every `index.md` uses; the one deliberate exception to "one concept
per file"). Confirms the term is repo-specific, derives the link to the concept doc that
defines it (never invents one), inserts the entry in alphabetical position with a
one-sentence definition, and **MERGES** rather than clobbering a filled entry. The on-demand,
single-term counterpart of the glossary tail step the other knowledge skills run;
`quenching-knowledge-glossary-backfill` is the whole-bundle bulk counterpart.

Triggers: *"add a term to the glossary"*, *"define this term"*, *"add this acronym / jargon
to the glossary"*, *"update the glossary"*.

### `quenching-knowledge-import-memory` — drain project memory into the bundle

Migrates the durable facts in the project's Codex memory
(`~/.codex/projects/<cwd>/memory/`) — promoting each memory into a `standard` or `concept`
doc in the `/.knowledge/` bundle, or a spec (always untriaged) in `/.specs/plans/` — then
**clears each memory once its doc has landed and passed the
conformance check**. Presents one migration plan and executes on a single
confirmation; a `user` memory or an unroutable fact is flagged and kept, never
silently deleted.

Triggers: *"convert the memory into docs"*, *"move project memory into the knowledge
base"*, *"turn memories into standards/backlog/knowledge"*, *"flush the memory into docs"*.

### `quenching-components-harness-align` — refactor AGENTS.md/AGENTS.md into thin pointers

Refactors a repo's **harness files** — the root `AGENTS.md`, every subfolder
`AGENTS.md`, and `AGENTS.md` — into thin, honest navigation pointers over the bundle.
Inventories every harness file, classifies each unit (**KEEP** the harness-operational —
build/run/test commands, env, etiquette needed every turn; **MOVE** durable knowledge
into its `/.knowledge/` home via `quenching-knowledge-add`, leaving a citing pointer; **DEDUPE** what
`/.knowledge/` already holds; **FLAG** contradictions; keep-and-report the unroutable), presents
one refactor plan, executes on a single confirmation (a product-code edit confirms on its
own), rewrites each file from the harness molds, and **self-verifies every pointer
resolves** — the validator exempts `AGENTS.md`/`AGENTS.md`, so pointer honesty is checked
here. Move, never copy: after the run each fact lives in exactly one place.

Triggers: *"refactor AGENTS.md"*, *"slim down AGENTS.md"*, *"move AGENTS.md content into
docs"*, *"make AGENTS.md point to the knowledge base"*, *"align AGENTS.md/AGENTS.md with /.knowledge/"*.

### `quenching-knowledge-status` — read the bundle, change nothing

The `docs` front's only read-only view (`quenching-knowledge-status`), and the counterpart of
`quenching-specs-status`. It reports every conformance finding in the validator's own codes and
the bundle's **density** — concept docs per home with empty homes shown as `0`, glossary size,
which `standards/` subjects hold anything — then splits it into what `quenching-knowledge-align` would fix on
one OK, what its content stages would then drive, and what neither closes because it needs
a human.

Density figures carry **no finding code**, deliberately: a bundle can pass every check while
holding scaffolded-but-empty homes and a placeholder glossary, and that is a signal worth seeing
but not a defect list to chase. It writes nothing, and owns no contract, citing `conformance.md`
and `cycle.md` so the preview and the sweep cannot disagree.

Triggers: *"what's the status of the docs"*, *"how healthy is the knowledge base"*, *"show me the
docs dashboard"*, *"what would quenching-knowledge-align do"*, *"is the bundle conformant"*.

### `quenching-knowledge-documentation-build` — create/update the documentation **site**

Owns the thin **site layer** that renders the bundle's `documentation/` home as an
mkdocs-material site (invoked as `quenching-knowledge-documentation-build`, the one wrapper nested a level
below its namespace, because it acts on one home rather than the bundle). That layer is the
`mkdocs.yml` + `requirements.txt` at the repo **root** — outside `/.knowledge/` — plus one
`awesome-pages` `.pages` nav file per section, inside it. The skill inventories the layer
read-only, reports every finding under a `site-*` code (config absent, unfilled
`<placeholder>`, a section with no `.pages`, a stale nav, a `docs_dir` aimed elsewhere,
an absolute `/.knowledge/<other-home>/…` link that dies in the built HTML), presents **one** plan,
and applies on one OK — **MERGE, never clobber**: a customized `mkdocs.yml` gets only its
missing required keys, always shown as a diff, and re-aiming `docs_dir` confirms on its own.
It closes with a real `mkdocs build --strict` into a throwaway dir, and reports `unverified`
rather than claiming a build that never ran.

**It never touches a page.** Page-level drift — a section without `index.md`, an unstamped
doc, a link that escapes the site root — is *reported* with the command that fixes it
(`quenching-knowledge-align`, `quenching-knowledge-add`), never repaired here. `quenching-knowledge-align` step 7 still stamps the
**first** install as part of scaffolding; everything after that is this skill. The site is
rooted at `documentation/`: the other homes stay the team's internal surface, unpublished.

Triggers: *"create the mkdocs"*, *"set up the docs site"*, *"update mkdocs"*, *"regenerate
the docs nav"*, *"build the documentation site"*, *"the site is missing the new pages"*.

### `quenching-components-command-new` + `quenching-components-align` — the automation family

Where the other skills organize a repo's *knowledge*, this pair organizes its
**automation surface**: the repo's own `.agents/skills/` and `.agents/skills/`. One
taxonomy axis governs everything, asked as up to two questions — first the
**category/subject** the command belongs to (`git`, `deploy`, ..., when one is evident; a
`commit` command under `git` lives at `.agents/skills/git/commit.md` → `/git:commit`), then
the older test read against it: **domain-bound** (serves ONE folder; pathed after that folder
plus a verb, `.agents/skills/communications/teams/create.md` → `/communications:teams:create`)
or **generic** (serves the repo as a whole; a flat `verb-object`). With both a category and a
real folder, that folder either nests inside the category or is replaced by it, per the
convention already in force for that category in that repo. Two OKF artifacts anchor the family
in the bundle:
the **rule** at `/.knowledge/standards/automation/skills.md` (`type: standard`, born
`authority: background`) and the **registry** at
`/.knowledge/documentation/reference/automation.md` (`type: documentation`), whose
`<!-- GENERATED:BEGIN/END -->` zone is derived from `.agents/skills/*/SKILL.md`
frontmatter and written only by these two skills — the same anti-drift pattern as
`backlog/index.md`. The doctrine lives once, in
[`components-command-new/doctrine.md`](assets/references/components-command-new/doctrine.md)
(how a SKILL.md is written: predictability, one trigger per branch, checkable step
criteria, the no-op test) and
[`components-command-new/taxonomy.md`](assets/references/components-command-new/taxonomy.md)
(the axis, naming, mirroring, registry format); the sweep cites, never restates.

**`quenching-components-command-new`** (per-item) mints or edits ONE conformant skill: reads the rule
(offering to create it on first run), classifies, derives name + wrapper, drafts under
the doctrine, presents ONE plan, writes on a single OK, then runs the OKF tail
(regenerate the registry zone, glossary offer, self-check). Without an OKF bundle the
mint still proceeds (skill + wrapper only) and suggests `quenching-knowledge-align` once.

Triggers: *"create a skill"*, *"mint a skill for X"*, *"organize this skill"*, *"wire a
command for this skill"*.

**`quenching-components-align`** (sweep) migrates the *existing* surface: read-only inventory
(including directory-scoped `**/.agents/skills/`, an accepted variation), ONE
consolidated plan — renames, wrapper mirroring, rule + registry creation when missing,
keep-and-report for unclassifiables, deletion only on the human's word — applied on one
OK (a code-coupled rename confirms individually), then post-apply verification: zone
regenerated, every wrapper resolves, registry matches `.agents/skills/` exactly.

Triggers: *"organize the skills"*, *"migrate the skills to the taxonomy"*, *"align the
commands to the monorepo"*, *"standardize the automation surface"*.

### `quenching-align-all` — the three fronts, one confirmation

The **structural** cross-front conductor: where the front conductors loop, this one runs the
*one* align of each of the **three** fronts, once, in dependency order — `quenching-knowledge-align`
(`/.knowledge/`) →
`quenching-specs-align` (`/.specs/`) → `quenching-components-align` (`.agents/`). One read-only probe of
the three fronts → **one** OK authorizes the whole run under the shared cycle-authorization
contract → each sweep runs under its own doctrine, narrating its own plan → one consolidated
report.

The order is a **dependency, not a preference**: `/.knowledge/` first because the other two write OKF
artifacts *into* the bundle (the skill front's rule + registry, the `/.knowledge/standards/` docs a
spec's distillation mints); `/.specs/` before `.agents/` matters **only in a migration** — a
legacy `openspec/` repo carries CLI-generated `openspec-*` skill + `opsx/` command shadow copies that
`quenching-specs-align` clears before `quenching-components-align` would otherwise inventory them.
**Front presence decides the pass** — an absent `/.knowledge/` bundle is what the plugin installs, so
Front 1 always runs; an absent `/.specs/` workspace is what `quenching-specs-align` scaffolds (from
the native `assets/specs/` payload, no external tool); an empty `.agents/` surface skips Front 3
with a note. It **conducts, never reimplements**, never loops a front to force a clean result, and
never acts on a front's reported residue — it names the residue and the command that closes it.

Triggers: *"align everything"*, *"align the whole repo"*, *"run all the aligns"*, *"normalize
this repo"*, *"install quenching in this repo"*, *"set the repo up end to end"*.

## The `specs` flow — the ten `quenching-specs-*` commands

The plugin's **spec-driven plan cycle**. **Where a spec is stored is declared, not fixed**: a
target repo names its backend in `.agents/quenching.json` — `backend: "files"` (on a dedicated
branch, never sharing one with the code), `"github"`, or `"azure-boards"` — and the selected
backend is the source of truth. No backend leaves a spec dividing a branch with the code it
tracks; the conceptual model (fourteen sections, seven frontmatter records, derived stages) is
identical whichever one is chosen — only *where and how* it is serialized differs, which is why
every command drives `scripts/bin/cq specs` (uniform `--json`, strict exit codes `0` ok · `1`
findings · `2` refusal) rather than a path. `files` and `github` are validated against this
repository; `azure-boards` ships implemented but **without an end-to-end run against a real
Azure DevOps project** — `doctor`'s `sp-backend-unproved` finding, plus a one-line stderr warning
on its first write each process, name that gap every time it is selected. Every command on this
front reads the `/.knowledge/` bundle
as context going in and distils durable knowledge back out when a spec closes.

The **unit of work is a spec** — ONE canonical markdown document for its whole pre-archive life.
Under `files` it is a real file, `/.specs/plans/<slug>.md`, moving exactly once to
`/.specs/archive/`; under `github` or `azure-boards` it is an issue or work item
**whose body is the whole document** — no sub-issues, no child work items; a document past
GitHub's 65,536-character body ceiling (two of this repository's 69 specs) spills into
continuation comments on its own issue and comes back byte for byte — and there may be **no
`/.specs/` folder on disk at all**. **Frontmatter records human judgments** (`priority`, `refined`,
`approved`, `branch`, `reviewed`, `merge`, `outcome`); the filesystem or backend, git and section
presence record everything else — `ready` is a *derived* stage, and the OK to build is the
`approved: {date}` stamp. Four more frontmatter keys — `tags`, `assignee`, `start`, `target` — are
**state, never records**: each has a faithful native counterpart on at least one backend (issue
labels/assignees on `github`, `System.Tags`/`System.AssignedTo`/the two scheduling dates on
`azure-boards`) and is reassembled from it on read rather than kept in the document, so a human's
edit on the tracker IS the spec's new value. A fifth key, `summary:`, is neither a record nor one
of those four — one line saying what the spec is, written at capture and refreshed by every
`quenching-specs-develop` bank, with no native counterpart anywhere, and it is what
`cq specs next --front --table` prints as its `Summary` column. `.agents/quenching.json` is where a target declares
`backend`, the per-backend placement (`azureStates`, `azurePlacement`, `azureColumns`) and the
project's own `subjects`/`tagCatalog` — the closed sets `quenching-specs-create` proposes a spec's subject
and tags from, confirmed by a human, never picked silently. Because a spec writes its durable rule
**directly into `/.knowledge/standards/`** (honestly `authority`-graded), there is no second store to
bridge to:
isolation-while-building is a real git **branch or worktree** (offered inline by `quenching-specs-execute`
when it starts from the base branch, recorded as `branch: {base, work}`, each task committed alone
with its sha on the task line). `cq specs export --spec <slug> | --all` dumps the canonical markdown to disk on demand —
write-only, nothing reads it back, so it is never a second store — the mitigation `## Risks`
names for losing access to an external backend.

| Command | Role |
| --- | --- |
| `quenching-specs-status` | The front's only **read-only** view: specs by derived stage with task progress, the frontmatter records as the history they narrate, the verifier results — split into what `quenching-specs-align` would fix, what a cycle command closes, and what neither closes. |
| `quenching-specs-create` | ONE spec in `plans/`, ONE call, ONE closing screen — effort proportional to input, never an interrogation. A sentence becomes `## Problem`, `## Overview` and `summary:`; a Codex plan file becomes every section it actually supports, mapped and never invented. Subject, type, tags and `complexity` are resolved and written with the capture, then shown — corrected or not — on the one screen at the end, which also offers to hand straight into `quenching-specs-develop`, with or without questions. |
| `quenching-specs-develop` | Questions grouped by dependency — independent ones in one `AskUserQuestion` call, sequential where an answer changes the next — each with an inline recommendation, the bank chosen by the spec's derived stage: generative shaping, adversarial interrogation (recording `refined:`), gate-gap filling, discovery resolution, and the `approved` stamp offer. Never edits code. |
| `quenching-specs-execute` | Builds `## Tasks` one verified commit at a time: clean tree required, isolation offered inline when it starts from the base branch, `verify:` run under the spec's declared policy, four-item diff self-review, then the box ticked with the subject of the commit it is about to make (`cq specs task --check --subject`) so code and box land in ONE commit. Writes only the `/.knowledge/standards/` a task explicitly names; everything else is one `cq specs discover` line. Marks an isolated branch's own description with the slug(s) it built there — never under `In place` — so `conclude` can self-discover it later. Stops at the last commit. |
| `quenching-specs-conclude` | Closes a spec out, resumable, **merging last**: whole-branch review (`reviewed:`), the emergent `/.knowledge/`, the archive with `outcome: done` (refuses on open boxes unless forced) or `abandoned` (always allowed), ONE distillation pass, the release obligations your standards attach to the merge itself (a version bump, a changelog entry — never a spec task) and the `merge: {strategy, subject, pr}` stamp — all on the work branch — and only then the merge, by the **route** you chose alongside the strategy: local, or a pull request where `gh` resolves the repo (pushed, opened and merged in one consented block, with `pr:` recorded). Called with no `--spec`, reads the branch's own marking first — one valid slug resolves silently, several ask, none falls to a diff-measured offer to materialize a minimal spec — before falling back to a plain list-and-ask. Nothing is committed to the base after it. |
| `quenching-specs-triage` | Ranks the whole front in ONE confirmed table, writing `priority: {level, criticality, complexity, date}` per spec and nothing else — merging, never clobbering a human's ranking. |
| `quenching-specs-align` | The front's align + installer — see below. |
| `quenching-specs-cycle` | The **cycle conductor** over ONE spec: capture, define, build, close — entering at the derived stage, invoking each stage as the command that owns it, never reimplementing any, and writing nothing of its own. **Two halves, two authorizations** (defining, then building), each opening on its own gears plan derived from `priority.complexity`, re-evaluated at the end of every stage and re-asked when the work reveals a larger size. A slug that resolves to nothing is captured through `quenching-specs-create` — with no authorization declared, so capture keeps its own gate — and the run carries on at defining. Typed-only: a whole lifecycle is a human's choice. |
| `quenching-specs-execute-queue` | Builds **N specs as a serial queue over a single isolation**: isolate once, `quenching-specs-execute` N times on that same branch, one `quenching-specs-conclude` with no `--spec` closing the lot into one pull request against the declared `integrationBranch`. Serialization is the feature — it removes the collision by construction and makes spec N's gate run over the result of 1..N−1, which the conductor re-runs after each spec under that spec's own declared policy. Candidates are filtered by the fan-out entry contract; ONE plan carries the whole list, the N, the recursion form and the human's stopping criterion **before** any isolation. A local block leaves its `[!]` and comes off the branch's `quenching-slugs:` line so the PR never implies it carries what it does not; a contaminating one stops and asks. |
| `quenching-specs-develop-batch` | Takes **N specs below the `ready` gate toward `ready` as a parallel batch** — every admitted spec launched in one message, each defined by `quenching-specs-develop` in a sub-agent of its own. It fans out for real because nothing it runs takes a branch or writes code, so the write sets are disjoint by construction. A question no evidence answers becomes an `## Open Decisions` line rather than an invented answer: the batch buys the drafting, not the judgment. The authorization, a contaminating block and every `approved` stamp stay with the conductor, which re-derives each spec's real stage from disk before offering it. |

The shared facts live once — the layout, the fourteen canonical sections, the gates, the record
vocabulary, the `cq specs` surface, and the `/.specs/`↔`/.knowledge/` boundary in
[`specs-develop/spec-driven.md`](assets/references/specs-develop/spec-driven.md),
the execution mechanics in
[`specs-execute/execution.md`](assets/references/specs-execute/execution.md),
the git defaults (read-if-present, never installed) in
[`git/conventions.md`](assets/references/git/conventions.md),
the distillation doctrine in
[`specs-conclude/distill.md`](assets/references/specs-conclude/distill.md).
The per-spec commands are never conducted by any sweep, because each needs fresh human intent a
conducted pass does not have. Every command on this front is **quenching-native** — no
`metadata.generatedBy` anywhere.

### `quenching-specs-align` — force the `/.specs/` workspace into shape

The front's align + installer, **probe-first**: `cq specs doctor` + `validate` run before
anything is read, so a conformant workspace costs two tool calls and stops. Otherwise: ONE plan →
one OK. It **fixes**: the scaffold (copies the native `assets/specs/` payload when absent),
offers to **remove** a legacy tool copy under `.agents/hooks/`, applies the remedies the tools declare, normalizes
spec and archive names, stamps missing frontmatter, and **folds older layouts** — the v2 `backlog/`+`ready/` split and the
v1 three-file plans — into `plans/` (`cq specs migrate`; basenames unchanged, `archive/**` never
touched). It also **migrates a legacy `openspec/` workspace** one-way, losing interop with the
external CLI by design.

**It aligns conformance and reports the cycle** — an empty section, a complete spec awaiting its
close, an unresolved discovery are each **reported with the command that owns it**, never
auto-closed: it never authors a spec, never moves one to `archive/`, and never invents a repair
`cq specs` did not state. The contract lives in
[`specs-align/conformance.md`](assets/references/specs-align/conformance.md).


## The signature: a canonical OKF bundle of `/.knowledge/`

The plugin installs **the same tree** in every repo (adapted to what fits — a repo
without data gets no `catalog/`):

```
/.knowledge/               # OKF bundle root
  index.md               # the ONLY index.md with frontmatter: okf_version: "0.1" + home listing
  glossary.md            # the fixed A–Z term lookup, bundle root — not inside a home
  standards/             # "how WE do it" (current) — architecture/ code/ naming/ data-modeling/
                         #   ci-cd/ workflows/ mlops/ quality/ platform/  (type: standard)
  catalog/               # our data — <system>/index.md · <schema>.md · <schema>/<table>.md
  vision/                # direction by area (type: vision)
  documentation/         # product docs site — Diátaxis prose (type: documentation)
  concepts/              # generic knowledge we hold (type: concept)
  external/              # what we consume — tools/ libraries/ regulations/ (type: external)
```

The **spec workspace** lives **outside** this bundle, at `/.specs/` (`plans/` +
`archive/`, one `<slug>.md` per spec, and no listing file — `cq specs list` derives
what the folder holds) — a quenching-managed sibling created by `quenching-specs-create` and ranked by `quenching-specs-triage`,
not scanned by the OKF validator. An
agreed-but-unproven decision is a `standard` with `authority: background` (there is no separate
`decisions/` home).

**OKF-strict rules the plugin enforces:**

- `index.md` is **reserved** — a listing, **no frontmatter** (the one exception is the
  root `/.knowledge/index.md`, which carries **only** `okf_version: "0.1"`).
- Every concept doc (non-`index.md`/`log.md`) carries **non-empty `type`** from the
  fixed vocabulary above, plus the OKF recommended fields and the method's extra keys.
- `log.md` is **retired**: nothing creates one, appends to one, or checks one. The name
  stays reserved so a log surviving an earlier alignment is recognized rather than flagged
  as a malformed concept doc — retired is not unreserved.
- Links are **relative** within a home, **absolute from the bundle root** (`/.knowledge/...`)
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

## Model policy

The command registry is built at **session start**, so a change under `commands/**` is not testable
in the session that writes it. `assets/checks/functional-checks.sh` is the only check that proves the
surface loads:
it spawns fresh `claude -p` processes — each loading the checkout under test via `--plugin-dir`, so
it sees a branch — and asserts on captured tool calls that `../..` substitutes in a
command body, that a conductor reaches its stage by registry name, and that a spoken phrase still
routes by description alone.

Each check is a **billed agent session**, so it belongs to the command that changes the surface —
`quenching-components-command-new` after minting or editing one, `quenching-components-command-eval` when it tunes a description — and not to
the spec cycle, which would charge every spec for a front most of them never touch. The default run
is the body subset; spoken routing is opt-in (`--only 3`) because `quenching-components-command-eval` measures it better,
graded and with a should-not-trigger arm.

**The model policy is conservative — judgment is never downgraded:**

| Surface | Policy |
| --- | --- |
| `quenching-knowledge-define` | **no pin** — the edit is mechanical, but an inline `effort: low` is part of the session's prompt-cache key, so it recomputes every input token on the next request ([`capabilities.md`](assets/references/components-command-new/capabilities.md) §Model and effort). A single-entry edit does not buy that back. **No hook either** — the rung-1 frontmatter block this row once described was removed when the plugin's own wiring covered the same case, and that wiring was later discontinued outright, so nothing answers a write event here any more (`/.knowledge/standards/automation/hooks.md`). What checks conformance at write time is the body's own **Self-check against the conformance core** step, run by the command, not fired by anything |
| `quenching-specs-create` | **`model: sonnet`** — the capture is mechanical and effort-proportional, so the tier it does not need is the expensive one. Zero interrogation before the write, no sub-agents. The pin is paid for once, in the **cache trap** ([`capabilities.md`](assets/references/components-command-new/capabilities.md) §Model and effort): an inline `model:` is part of the session's prompt-cache key, so **changing** it recomputes every input token on the next request. A pin left alone costs nothing after the first run, which is what makes a stable pin affordable and pin-churn expensive. **The closing screen's hand-off into `quenching-specs-develop` (`model: opus`) is the one path that changes the pin mid-session** — an inline `model:` switch recomputes the input tokens on the very next request, so the hand-off is not free the way an ordinary `Skill` invocation is; unmeasured as of this writing, and worth a real run before assuming the cost is negligible |
| `quenching-specs-triage` | **`model: opus`**, no `effort` override — the *reading* is cheap (a few small frontmatter blocks) but the *output* is a ranking grounded in `vision/`, which is exactly the judgment the top tier exists for; the human plan-gate contains misjudgment but should not have to catch it. No sub-agents |
| `quenching-specs-status` | **no pin**, no sub-agents, **no `Write`/`Edit` in `allowed-tools`** — it classifies against a fixed finding vocabulary it does not own, and `cq specs status` is scoped to full-progress plans rather than run per plan. The former `effort: low` was dropped for the cache trap: a read-only view is not worth invalidating the session's prompt cache |
| `quenching-knowledge-status` | **no pin**, no sub-agents, **no `Write`/`Edit` in `allowed-tools`** — the `docs` counterpart of the row above, and its `effort: low` was dropped for the same reason. Both bodies also forbid `context: fork` by name: each doubles as a sweep's preview, and the report has to land in the conversation where the OK will be given |
| `quenching-specs-conclude` | **`model: opus`**, no sub-agents — the branch review, the merge choice, the outcome, and the distillation are all judgment; there is nothing mechanical here to downgrade, and the review reads a whole branch diff for coherence rather than one task's |
| `quenching-knowledge-glossary-backfill` | **no pin** on the orchestrator (the former inline `effort: medium` charged the cache trap); slice sub-agents `model: haiku` + `effort: low` (pure extraction, cross-checked by the orchestrator) — a sub-agent's pin is cache-safe, it has its own context. `Bash` scoped to `python3`/`py`: its reading is `Grep`/`Glob`/`Task`, and the checker is the only shell it runs |
| `quenching-knowledge-import-memory` | classification sub-agents `model: sonnet` + `effort: low`; **executor sub-agents inherit the session model** (their self-check authorizes memory deletion). `Bash` stays unrestricted **and is now priced in the body**: step 1 derives the memory directory as one compound shell expression, which no prefix grant can match |
| `quenching-knowledge-align` / `quenching-components-harness-align` | repo-wide grep/find sweeps delegable to one read-only `haiku` + `effort: low` collector; every classification stays with the orchestrator when run standalone. `quenching-components-harness-align`'s `Bash` is scoped to `git grep` / `git check-ignore` / `grep` / `python3` / `py` — the two-scan sweep, the build-artifact check, the checker, and nothing else; `quenching-knowledge-align` keeps the unrestricted grant its body prices. **Exception:** under `quenching-knowledge-align`'s parallel content prep, harness's read-only discovery (steps 1–4, incl. MOVE/KEEP classification) runs in a background `Task` agent pinned `model: sonnet` — never haiku, same misclassification-risk rationale as the cycle's assessment agent |
| `quenching-knowledge-align` (content passes) | per-pass read-only assessment via a `sonnet` + `effort: low` sub-agent (haiku ruled out: a false "nothing to do" ends the loop early) |
| `/align` | no pin, no sub-agents — the front probe is a handful of globs and two CLI calls, and every write belongs to the sweep it invokes (which carries its own policy row) |
| `quenching-specs-align` | no pin; `Bash` scoped to `python3` / `py` / `mkdir` / `cp` / `mv` / `git mv` / `rm` — the asset copy, the confirmed renames and the approved shadow-copy deletions of step 6, and nothing wider (it previously granted bare `Bash` *alongside* those scopes, which made them dead). **Two** repo scans cover the whole rename set (never two per rename — [`sweep-doctrine.md`](assets/references/align/sweep-doctrine.md) §3), and only the bucketing of a large hit list is delegable to one read-only `haiku` + `effort: low` collector, after the scans. `cq specs status` runs only for full-progress plans, and the conductor hands down its inventory instead of making align re-collect it. Every classification, `cq specs`-stated-repair judgment, and the fix-vs-report split stays with the orchestrator |
| `quenching-knowledge-import` | extraction/executor sub-agents may run `model: haiku` + `effort: low` — import **deletes nothing**, so a misclassification only misfiles a doc (correctable); the orchestrator keeps each `index.md` honest and resolves cross-slice dedup |
| `quenching-knowledge-add` / `quenching-knowledge-learn` | no pin — they inherit the session model (they classify, route, and gate operations). **Neither carries a frontmatter hook block** — the rung-1 blocks these two once carried were removed when the plugin's own wiring covered the same case, and that wiring was later discontinued outright, so no hook fires on their writes (`/.knowledge/standards/automation/hooks.md`). Each body's own **Self-check against the conformance core** step is the conformance check at write time: a step the command runs, not a rung anything enforces |
| `quenching-knowledge-documentation-build` | no pin, no sub-agents — the inventory is a handful of globs plus one config parse, and the expensive step is an external `mkdocs build`, not tokens; the config **merge** and the fix-vs-report split are exactly the judgment the plan gate exists to contain. `Bash` stays unrestricted **and is now priced in the body**: it drives a toolchain the plugin does not own, reachable through `pip`, `uv` or a bare `python -m` |
| `quenching-components-command-new` | no pin, no sub-agents — classification on the axis, doctrine-grade drafting, and the plan gates inherit the session model |
| `quenching-components-align` | no pin. Its §7 doctrine audit **may delegate collection** to read-only `Task` collectors — one per slice, reporting *what each body contains* (which levers its frontmatter carries, what it cites, where its steps end) on a surface large enough that reading every body would bury the conversation. Every verdict stays with the orchestrator: "this body has no positive prescription" is a claim about behaviour, and the read that makes it must also weigh the fix |
| `quenching-specs-develop` | **`model: opus`** — the whole command *is* judgment: generating the questions a spec never answered, recommending an answer to each, and deciding when the interrogation is done. There is nothing mechanical here to downgrade, and a cheap model that asks generic questions produces exactly the refinement theatre the command exists to replace. Cost is bounded by each bank's declared stop condition, not by a model tier. One **read-only** sub-agent is permitted, and only for the adversarial and gate banks: it sweeps the code and the `/.knowledge/standards/` the spec declares and returns one table (`assets/references/specs-develop/questions.md` §Gathering the evidence). It reads; it never asks, writes, or decides — every question, every `cq specs` call and every confirmation stays with the orchestrator. **This is not `context: fork`**, which cannot ask a question at all, so the never-fork rule is untouched |
| `quenching-specs-execute` | **`model: sonnet`** — the loop is write · verify · self-review · tick · commit against a spec that already decided what to build, and the judgment it does keep is gated by a human at every confirmation. A per-task **executor sub-agent is permitted** when the task declares `files:` and touches no `/.knowledge/` — pinned to the **session model, never `haiku`**; with this command pinned, *session model* means `sonnet` for those executors (it writes production code, the same rationale that protects `quenching-knowledge-import-memory`'s executors). The orchestrator keeps spec selection, every confirmation, every `cq specs task --check`/`--block`, every `/.knowledge/standards/` write, the commit, and the pause decision. Two tasks run concurrently only when `cq specs parallel` reports the `[P]` group eligible; serial is the default. **This is not `context: fork`** — the orchestrator stays in the live conversation, so the never-fork rule is untouched (`assets/references/specs-execute/execution.md` §This is not `context: fork`) |
| `quenching-specs-cycle` | **no pin** — typed-only (`disable-model-invocation: true`): a whole lifecycle is a human's choice, so the description pays no routed budget; each half's plan gate and every nested confirmation stay in the conducting session, and each stage runs under its own policy row |
| `quenching-specs-execute-queue` | **no pin** on the conductor; **one executor sub-agent per spec, pinned to the session model — never `haiku`**: each runs `quenching-specs-execute` over the repo's production code, the same rationale that protects `quenching-knowledge-import-memory`'s executors. `Bash` is unrestricted **and priced in the body**: the queue drives the target repo's own `git` and re-runs the repo's own declared gate after every spec, neither enumerable in advance — and it is the *only* file-touching tool granted, because every read the conductor makes goes through `cq` and the repo's files are read inside the sub-agents |
| `quenching-specs-develop-batch` | **no pin** on the conductor; **N sub-agents launched in ONE message**, one slug each, pinned to the session model — never `haiku`, since a misdrafted section is one a human is about to approve. `Bash` scoped to `python3` / `py` / `git status` — the tool, plus the porcelain check that *measures* the disjunction the batch claims instead of asserting it; no sub-agent may talk to the human, stamp `approved`, promote a discovery or write into `/.knowledge/` |

Two rules are deliberate and must survive any future "optimization":

- **Never add `context: fork` to these skills.** Every sweep skill gates on a mid-flow
  confirmation (one plan → one OK) when run standalone — and even a cycle-authorized run
  ([`align/convergence.md`](assets/references/align/convergence.md)
  §cycle-authorization) must still surface code-coupled confirmations mid-flow, which a forked
  context cannot present.
- **Never downgrade classification or executor agents to haiku** in
  `quenching-knowledge-import-memory` — a misclassification becomes a wrong memory deletion.

**Fan-out cost — the saving is context isolation, not concurrency.** What an N-spec run saves comes
from each spec running in a **sub-agent of its own context**: an in-session queue would make spec N
re-send the previous N−1 specs' context on every turn, and that is the cost the sub-agent removes.
Serializing the build therefore costs none of the saving — and `quenching-specs-execute-queue` adds
a second one on top, since **one** `quenching-specs-conclude` instead of N pays for the branch
review, the release obligations and the archive once rather than per spec. Against that sit the
serial run's own charges: the declared gate is re-run after every spec, and the conductor's own
preamble is re-sent every turn of a run that may hold N specs — which is why these bodies load their
contract by section (`cq components read --sections`) rather than by file. **There is no cap on N
and no soft warning** in either entry: the size is decided on the plan, and a threshold nobody
measured would add the appearance of measurement without the measurement.

**External backend cost — network, not tokens.** `github`/`azure-boards` reach the vendor through
`subprocess` over `gh`/`az`, never a bundled HTTP client, so every write and every list is one
process spawn plus one network round trip, cached only for the lifetime of the running
`cq specs` process. Measured on `github`: a 12-command build cycle spent 33 `gh` calls, because
`list` re-lists every issue with no cache between processes. `azure-boards`'s `list` reads in
batches of 200 through `az devops invoke --resource workitemsbatch` — 1 + ⌈N/200⌉ calls for a
listing rather than 1 + N, `az work-item show` having no batch form of its own — mitigated
further by the same per-process cache. Neither binary is a plugin dependency until a target repo
declares that backend: `files` never shells out, and a missing `gh`/`az`, a missing extension, or
a missing auth is a named **refusal (exit 2)**, on the first operation, never mid-build.

## Install

```bash
claude --plugin-dir ./plugins/quenching
```

All skills reach the shared payload via `../../assets/...`.

The CLI is bundled inside the plugin and is **not** installed in the user's PATH. Codex skills define a per-call `cq` wrapper that resolves the installed plugin and executes `scripts/cq` by absolute path; the wrapper is repeated because each Bash call and each sub-agent may start with a fresh shell. The resolver and its no-global-install rule live in `references/align/tool-resolution.md`.

## Upgrade

Resolution is **plugin-first, with no user-level install**: every skill resolves the installed plugin copy at call time, so a version bump reaches consumers when Codex refreshes the plugin. There is no global `cq` executable to keep in sync.

Publishing the bump itself is mechanized, not a manual edit. `cq specs release <version>` moves the
four version-carrying files together and creates the tag in one act: `.claude-plugin/plugin.json`,
`VERSION`, the marketplace manifest's plugin entry, and the one shared `common/version.py` constant
every pillar's `--version` reads. This
repository's own `/release` command (`.agents/skills/release.md` — not shipped by the plugin)
drives it: run once, deliberately, at the **`develop → main` merge**, never at a spec's own
conclude, it reads what accumulated on `develop` since the last release, proposes a patch/minor/major
bump with its reasoning, and gates on one confirmation before merging, bumping, tagging and pushing.
See [`/.knowledge/standards/ci-cd/versioning-release.md`](/.knowledge/standards/ci-cd/versioning-release.md) for
why each half of the lockstep matters, and
[`/.knowledge/standards/git/branching.md`](/.knowledge/standards/git/branching.md) for the `develop`/`main` split
`/release` publishes into.

- **4.2.0:** **nothing is written after the thing it describes, so the merge is last.** The
  task→commit anchor inverted from the commit's **sha** to its **subject** — known *before* the
  commit exists — which let two writes move ahead of the events they record. `quenching-specs-execute` now
  ticks the box with `cq specs task --check --subject` and commits code and box together, so one
  task is literally one commit and the per-task bookkeeping commit is gone. `quenching-specs-conclude`
  reordered: the branch review, the emergent `/.knowledge/`, the archive, the distillation and the
  `merge: {strategy, subject}` stamp all land on the work branch, and **the merge is its last
  action** — one merge carries the spec's whole footprint and nothing is committed to the base
  after it. Rebase stops destroying the record, since a subject survives a rewrite; the squash
  caveat stands. A **25th command** (an isolation command, since retired) extracts the git *action* — branch or
  worktree, at **any** stage rather than only at build time — and `cq specs next --front` became
  branch-aware, so the front router (since retired) returned the spec whose branch you were standing on and demoted
  one alive elsewhere. `parse_frontmatter` learned block mappings (indent-scoped), which is what
  lets an explicit-none merge record wrap or carry a comma. New `assets/checks/conclude-order-check.sh`
  asserts the ordering on a real history — the one claim no in-process check can see. The always-on
  ceiling fired on the 25th command exactly as designed and was re-measured to **12,726**.
- **4.1.0:** **the capability layer got proved, applied and closed.** Both new mints were measured
  by `quenching-components-command-eval` — `quenching-components-agent-new` at +0.364 pass rate for 182,367 fewer tokens,
  `quenching-components-hook-new` at +0.5 for 52.5% cheaper — and each gained an intent-shaped trigger plus a
  sandboxed routing probe, taking `functional-checks.sh` to **9 assertions across 7 sandboxed
  sessions**. `cq components` closed its two blind spots: `lint` now reads a **frontmatter `hooks:`
  block** (the scope ladder's narrowest rung, the mold's shape only, fail-open via
  `sk-hook-unparseable`) and serves both rungs from one implementation, and the cost report counts
  `agents/*.md` descriptions as its own breakdown line; the ceiling was re-measured and re-set to
  **11,565** from a run. The profile doctrine was then applied to its own author: five inline
  `effort:` pins dropped for the prompt-cache trap, `Bash` scoped on `quenching-specs-align`,
  `quenching-components-harness-align` and `quenching-knowledge-glossary-backfill` and priced in the body of the two that keep it,
  frontmatter `hooks:` blocks on `quenching-knowledge-add`/`quenching-knowledge-learn`/`quenching-knowledge-define`, and a collection-only
  `Task` for `quenching-components-align`'s doctrine audit — `sk-unscoped-bash` 8 → 5, every survivor stating
  its reason. `/.knowledge/standards/automation/hooks.md` graduated to `authority: current` on that
  adopting surface; `agents.md` stayed `background` because there is no `.agents/agents/` anywhere
  to follow it. A proposed `components package` verb was **dismissed on a real packaging run**: four mechanical
  operations, then six fields that came back requiring a human. Still twenty-four commands.
- **1.0.0:** **the middle front went fully native — the external OpenSpec CLI is gone.** The
  `openspec/` workspace this plugin used to *drive* (`@fission-ai/openspec`, `openspec init`,
  `config.yaml`, a main-spec store, delta specs) is replaced by a **native `specs` front** the
  plugin owns end to end. There is **no `npm i -g`, no Node prerequisite, no delta format**: the
  deterministic rails are the new bundled stdlib **`scripts/bin/cq specs`**
  (`new`/`list`/`status`/`next`/`task`/`backlog`/`validate`/`archive`/`doctor`, uniform `--json`,
  exit codes `0`/`1`/`2`), the second self-contained tool beside `cq knowledge validate`, installed by
  `quenching-specs-align` into a target's `.agents/hooks/`. The **unit of work is a plan**
  (`/.specs/<plan-name>/`: `proposal.md`, `design.md`, `tasks.md`, `.specs.json`), not an
  "OpenSpec change" — and because a plan writes its durable rule **straight into
  `/.knowledge/standards/`**, honestly `authority`-graded, there is nothing to sync: isolation-while-building
  is a real git **branch or worktree** (offered by `/specs:apply`), not a markdown delta. The
  `specs`-front conductor pipeline drops to **3 stages** (align → plan-archive → backlog-triage) —
  the old sync stage and `openspec-sync-specs` skill are **removed**. Commands moved from `/opsx:*`
  to **`quenching-specs-*`** (plan skills under `quenching-specs-develop`, inbox under `/specs:capture`), the inbox
  from `openspec/backlog/` to **`/.specs/backlog/`**, and every finding code from `os-*` to `sp-*`.
  All twenty-seven skills now share **one `quenching-<front>-<object>-<verb>` taxonomy** — no
  separate `openspec-*` family, no `metadata.generatedBy` anywhere. New
  **`/specs:from-claude`** turns a `~/.agents/plans/*.md`
  file into an archivable plan so ad-hoc work gains the archive-time distillation. `quenching-specs-align`
  **migrates a legacy `openspec/` workspace one-way** (flatten, fold main specs into
  `/.knowledge/standards/`, drop `config.yaml`/deltas, clear the CLI shadow copies) — interop with the
  external CLI is lost by design. Still **twenty-seven** skills; the skill↔wrapper bijection holds
  at 27↔27.
- **0.19.0:** **the `openspec/` front's lifecycle closed, and the sweep contract given one
  owner.** Two new quenching-native skills complete the front. **`quenching-specs-status`**
  is its only read-only view — changes with progress and state, the backlog by
  priority, the three verifier results, split into what `quenching-specs-align` would fix, what
  `/specs:align-and-update` would drive, and what neither closes; it reports in the sweep's own
  `os-*` vocabulary, so it is an honest dry run of the sweep you are about to authorize.
  **`/specs:archive`** is the exit `archive-change` could not give: a
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
  [`align/sweep-doctrine.md`](assets/references/align/sweep-doctrine.md),
  and each align states only its own front's deltas. The `openspec/` ↔ `/.knowledge/` boundary is
  declared normatively once, in the specs-develop skill's `openspec.md` §Boundary (retired along
  with `openspec/` support itself in 1.0.0). The backlog's
  prose "self-check" is gone: `cq knowledge validate` gained **`--listing-root`** and now checks
  `openspec/backlog/` for real (`type: task` is also exempted from the `resource` recommendation,
  since the mold omits it on purpose) — the same checker that guards `/.knowledge/`, pointed at a tree
  the bundle root never covers.
  **Performance.** `/specs:align-and-update` hands its assessment inventory down to
  `quenching-specs-align` instead of making it re-collect against an untouched disk (a pass paid for
  `doctor`/`validate`/`list --json` three times); `status --json` is scoped to full-progress
  changes rather than run per active change; the rename blast-radius sweep is **two** repo scans
  for the whole set instead of two per rename; `/specs:archive` invokes
  `openspec-sync-specs` directly via `Skill` with the delta analysis it already built, instead of
  spending a `general-purpose` sub-agent to re-derive it; and the task-capture hot path drops the
  glossary tail step, which was an expected no-op costing two bundle reads on a path whose whole
  contract is "seconds".
  **Defects fixed.** Eleven references to three commands that do not exist (`/opsx:implement`,
  `/opsx:archive`, `/opsx:revise` — CLI names that survived the adaptation) now point at the real
  wrappers. Six skills instructed tools their `allowed-tools` did not grant (`AskUserQuestion`,
  `TodoWrite`, `Task`/`Skill` in archive, `Bash` in both backlog skills). The two backlog
  descriptions said "OKF backlog", contradicting every other statement that the inbox is outside
  the bundle.
  **The documentation site got an owner.** New **`quenching-knowledge-documentation-build`**
  (`quenching-knowledge-documentation-build`) owns the mkdocs-material **site layer** over the `documentation/`
  home end to end: install, config **merge** (missing required keys only, shown as a diff),
  `.pages` nav regeneration as sections come and go, `site/` gitignore, the opt-in Pages workflow,
  and a real `mkdocs build --strict` verification that says `unverified` rather than lying. Until
  now that layer was stamped **once** by `quenching-knowledge-align` step 7 and then drifted with no command
  to fix it: a section added later had no `.pages`, and a customized `mkdocs.yml` had nowhere to be
  merged forward. The new skill touches the **site layer only** — page-level drift is reported with
  the command that fixes it, never repaired — and align's step 7 now names it as the owner it hands
  off to. It is an on-demand tool, deliberately **not** a stage of `quenching-knowledge-align-and-update`'s
  loop (like `quenching-knowledge-import`): a site build is a publishing act, not part of reaching an OKF
  fixpoint. Twenty-four skills → **twenty-seven** (fifteen `quenching-*` + twelve `openspec-*`);
  the skill↔wrapper bijection holds at 27↔27.
- **0.18.0:** **the interface completed — one 2×4 matrix, and `converge` renamed.** 0.17.0 gave
  every front an `align`; this release gives every front an **`align-and-update`** and renames
  the concept so it says what it does. `quenching-converge` → **`quenching-knowledge-align-and-update`**
  (`knowledge:converge` → `knowledge:align-and-update`, both retired since) — clean cut, no compatibility alias. New
  **`specs:align-and-update`** (retired since) drives the cycle actions
  `quenching-specs-align` only reports: align → archive each complete change (syncing specs and
  distilling into `/.knowledge/`) → sync leftover deltas → triage the inbox, looped; **each archive
  confirms on its own**. New **`quenching-components-align-and-update`** (`components:align-and-update`, retired since)
  adds the one thing the align is forbidden to do — a **read-only doctrine audit of every skill
  body**, reported with the `quenching-components-command-new` that fixes it, never rewritten. New
  **`quenching-align-and-update-all`** (root `/align-and-update`) loops all three fronts,
  because they feed each other (an archive's distillation is glossary work; the skill front's
  registry is a `/.knowledge/` listing). **Architectural fix:** the cycle-authorization + convergence
  contract left `quenching-converge/references/cycle.md` — where it had become misplaced, being
  cited by every conductor — for its own neutral owner,
  `quenching-align-and-update-all/references/convergence.md`; each front's `cycle.md` now holds
  only that front's pipeline and routing. The contract also grew a second never-covered class
  beside code-coupled items: **irreversible cycle actions** (an OpenSpec archive, a backlog
  removal) always gate individually, and authorization **nests one level** so the cross-front
  run still costs exactly one OK. Twenty-one skills → **twenty-four** (fourteen `quenching-*` +
  ten `openspec-*`); the skill↔wrapper bijection holds at 24↔24.
- **0.17.0:** **one interface across the three fronts.** The plugin acts on three surfaces —
  `/.knowledge/`, `openspec/`, `.agents/` — but only two had an align sweep. New **`quenching-specs-align`**
  (quenching-native) gives the `openspec/` workspace the same
  install-and-force-conformance entry point: scaffold via `openspec init`, doctor/validate,
  canonical change + archive names, the `backlog/` inbox and its derived zone, `config.yaml`'s
  `context:` thinned into a pointer at `/.knowledge/`, and removal of the CLI-generated
  `.agents/skills/openspec-*` + `.agents/skills/opsx/` shadow copies — with cycle actions
  (archive, triage, sync, boundary smells) **reported, never driven**. Its contract lives in
  the new `specs-align/references/conformance.md`; `quenching-components-align` now explicitly
  leaves the `openspec-*`/`opsx/` surface to it. New **`quenching-align-all`** (root `/align`)
  is the second conductor: the three aligns in dependency order (`/.knowledge/` → `openspec/` →
  `.agents/`) on **one** confirmation, orthogonal to `quenching-knowledge-align-and-update` (which loops the
  `docs` front alone to a fixpoint). The cycle-authorization contract in
  `quenching-knowledge-align-and-update/references/cycle.md` is now the shared normative home for **both**
  conductors. Nineteen skills → **twenty-one** (twelve `quenching-*` + nine `openspec-*`), and
  the skill↔wrapper bijection is preserved.
- **0.16.0:** **verb-first command surface, honest namespaces.** Renamed the command wrappers
  so each names its action, and split the `quenching-*` surface by the artifact it touches.
  `opsx:` keeps its namespace and every `openspec-*` skill name (upstream alignment); only the
  commands change: `apply`→`implement`, `update`→`revise`, `sync`→`sync-specs`,
  `backlog`→`backlog-add`. The seven quenching-native `docs:` skills rename in lockstep with
  their command: `insert`→`add`, `enrich`→`import`, `knowledge`→`learn`, `glossary`→`define`,
  `knowledge-scan`→`glossary-backfill` (the name no longer lies), `memory-to-docs`→`import-memory`,
  `cycle`→`converge`. `align`/`harness` stay. A new **`skill:` namespace** carries the two
  `.agents/`-automation skills out of `docs:` — `quenching-components-command-new` → `quenching-components-command-new`,
  `quenching-components-align` → `quenching-components-align` (skill names unchanged, namespace honest). Clean
  cut, no compatibility aliases; the 19-skill/19-wrapper bijection is preserved.
- **0.15.0:** every skill is now `user-invocable: false` (hidden from the `/` menu) and paired
  with a thin **command wrapper** — `/opsx:*` for the eight `openspec-*` skills, `quenching-knowledge-*` for
  the eleven `quenching-*` skills; Codex still auto-routes by `description`, the wrappers are the
  explicit user entry points. **Renamed** the backlog pair into the OpenSpec family — capture
  and triage, quenching-native — they own the `openspec/backlog/` inbox and carry
  no `metadata.generatedBy`. **Removed** `quenching-visualize` and the offline HTML diagram
  generator it drove (`assets/tools/okf-visualize.py` + the vendored `viewer/` — Cytoscape.js +
  marked). Twenty skills → **nineteen** (eleven `quenching-*` + eight `openspec-*`).
- **0.14.0:** added the **automation family** — `quenching-components-command-new` (mint/edit ONE
  conformant skill: single-axis classification domain-bound × generic, flattened-path
  naming, mirrored command wrapper, writing doctrine, OKF tail) and
  `quenching-components-align` (migrate the existing `.agents/skills/` + `.agents/skills/`
  surface to the taxonomy in one plan → one OK). Two OKF artifacts now maintained in
  target repos: the rule `/.knowledge/standards/automation/skills.md` (born
  `authority: background`) and the registry `/.knowledge/documentation/reference/automation.md`
  with a GENERATED zone only the pair writes. New `assets/templates/automation/` molds
  (skill, command wrapper, registry, standard). Fourteen quenching skills → **twenty** in
  all.
- **0.13.0:** straightened the work pipeline to `openspec/backlog/` (task) →
  `openspec/changes/…` (design records the decision) → `/.knowledge/standards/` (proven rule), with no
  middle element. **Moved the backlog out of the OKF bundle** to `openspec/backlog/` — a
  quenching-managed sibling of `/.specs/`/`changes/`, no longer scanned by `cq knowledge validate`, and
  `type: task` left the OKF `type` vocabulary; `quenching-backlog`/`-triage` still own capture,
  triage, the derived index zone, and an on-write self-check (the new
  `quenching-backlog/references/backlog-zone.md` is its single owner). **Retired the standalone
  `decisions/` ADR home**: an agreed-but-unproven decision is now a `standards/` doc with
  `authority: background`, a proven one `authority: current`; a change's rationale/alternatives
  live in its `design.md` while active and distill to a `standard` at archive time.
  `migration.md` gains rules (§1e/§1f) to relocate an existing bundle's `backlog/` home → `openspec/backlog/`
  and restamp its `decisions/` ADRs into `standards/`. Still **eighteen** skills.
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
