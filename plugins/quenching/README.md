# quenching (plugin)

An **OKF-centric knowledge-base aligner** for the Claude Code surface of any
repository. It carries one canonical **Open Knowledge Format (OKF v0.1)** bundle
of `docs/` and the tools to install it, force an existing base into conformance,
insert new knowledge, capture terms into a fixed glossary, drain the project's Claude
Code memory into it, import external sources into it, keep the repo's `CLAUDE.md` a thin pointer over it, and organize
the repo's own **automation surface** (`.claude/skills/` + `.claude/commands/`) under one
taxonomy — so every repository that adopts the plugin looks the **same**. It also carries the repo's
**spec-driven plan cycle**: a **fully native** `specs/` front (the nine `/specs:*` commands)
with the OKF bundle as its knowledge substrate — no external
CLI, driven by the bundled stdlib `specs.py`.

All of it sits behind **one interface, repeated on every front**: ONE `align` per front —
probe-first, so a clean front costs a couple of tool calls — that forces the structure into
shape and carries that front's content stages. Read the next section and you know the whole
plugin.

## The three fronts and the one align per front

The plugin acts on **three** surfaces of a repository, and the interface is the **same on each**.
Every front has exactly ONE align, and one more spans all three:

| Front | Namespace | **align** — probe-first, structure + content |
| --- | --- | --- |
| `docs/` — the OKF bundle | `/docs:*` | `/docs:align` |
| `specs/` — the native spec-driven workspace | `/specs:*` | `/specs:align` |
| `.claude/` — the automation surface | `/skill:*` | `/skill:align` |
| **all three** | *(root)* | **`/align`** |

**The probe comes before the inventory.** Each align opens by running its front's own verifier
(`okf-validate.py`, `specs.py doctor`/`validate`, `skills.py doctor`/`lint`) and stops when it
finds nothing — no inventory, no plan, no confirmation. Otherwise: one read-only inventory → ONE
consolidated plan → one OK → apply → verify, then the front's content stages, each run only when
the probe found it work:

| Front | Content its align carries beyond structure |
| --- | --- |
| `docs/` | drains project memory, thins the harness (moving durable knowledge into homes), and OFFERS the glossary backfill on a cheap proxy — looping to a fixpoint, the one front with a real internal loop |
| `specs/` | none driven — an empty section, a complete spec awaiting its close, an unresolved discovery are each **reported with the command that owns it**; every cycle action needs fresh human intent |
| `.claude/` | audits every command **body** against the writing doctrine — the one thing the migration itself is forbidden to fix — and reports each violation with the `/skill:new` that closes it |

The cross-front `/align` conducts the three in dependency order on one nested OK and **loops
across fronts**, because they feed each other: a spec's distillation is glossary work the
`docs/` front must then index; the skill front creates the rule and registry that the `docs/`
listings must carry.

Every entry point shares one contract: any item whose blast radius reaches **product code**
confirms on its own, always — and inside a conducted run, so does every **irreversible close**.
That contract lives once, in
[`align-all/convergence.md`](assets/references/align-all/convergence.md).

## The twenty-six commands

**One file per entry point** — Claude Code merged custom commands into skills, so each
`commands/<path>.md` carries both the description that routes to it and the body that runs;
there is no `skills/` tree and no wrapper. The twenty-six split by front: `/docs:*` for the ten
that act on the OKF `docs/` bundle (one nested a level deeper at `/docs:documentation:build`),
`/specs:*` for the nine that act on the native `specs/` workspace, `/skill:*` for the six that
act on the target's `.claude/` automation surface (two nested: `/skill:agent:new`,
`/skill:hook:new`), and the root `/align` for the one that spans all three fronts. Claude
auto-routes to a command by its `description`; typing the command is the explicit entry point.

> The per-command prose below predates the v3 `specs/` fold and the align fold — the surface
> facts above and in `CLAUDE.md` win where they disagree; a full rewrite is parked as its own
> spec.

### `quenching-docs-align` — structure (installer + force-aligner + validator)

Derives the target's current `docs/` shape, maps every existing section to a
canonical **home**, and produces an **alignment plan**: which homes to scaffold,
which variant names to migrate (`docs/arquitetura/` → `docs/standards/`), which
misfiled docs to relocate, which frontmatter to stamp/normalize, which `index.md`
to (re)generate, and the blast radius of any rename that reaches product code. It
presents the **full plan** and executes on **one**
confirmation. A rename whose blast radius reaches product code (path constants,
imports, docstrings) is its **own** confirmation item — never folded into the batch
OK. After executing it re-runs the conformance checker on the output.

Triggers: *"align the knowledge base to OKF"*, *"install the docs structure"*,
*"force OKF conformance"*, *"migrate docs/ to the standard"*.

### `quenching-docs-add` — content (insertion tool)

Classifies a new piece of information into its **home + `type` + mold**, determines
its path identity, fills the mold with a complete OKF stamp (`type` + recommended
fields + method labels, `resource` derived and never invented), writes the concept
doc, updates the folder's `index.md`, enriches the glossary when the concept names
a repo-specific term, and validates.

Triggers: *"insert new information into the base"*, *"add a standard/table/announcement"*,
*"record knowledge in the OKF docs"*.

### `/specs:triage` — rank the whole front

The prioritization sweep over `specs/plans/`: reads every spec's
frontmatter and derived stage **directly** (no sub-agents — a front is small by nature) plus
`docs/vision/` when present, and builds **ONE** ordered table with a one-line reason per row —
re-ranks of already-ranked specs only with an explicit reason, staleness flags, duplicate-merge
suggestions. **One OK** applies the whole plan (a rejected plan applies nothing; a human-set
ranking is never silently clobbered), writing each spec's
`priority: {level, criticality, complexity, date}` record and nothing else. Its output is what
`/specs:continue` stands on. It never removes a spec, never infers completion, and never treats
staleness as abandonment.

Triggers: *"triage the specs"*, *"prioritize the front"*, *"rank the plans"*,
*"re-rank these"*.

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
the knowledge concerns, and an updated `index.md`. If the information is really a
contract / decision / procedure / external-asset fact, it
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
one-sentence definition, and **MERGES** rather than clobbering a filled entry. The on-demand,
single-term counterpart of the glossary tail step the other knowledge skills run;
`quenching-docs-glossary-backfill` is the whole-bundle bulk counterpart.

Triggers: *"add a term to the glossary"*, *"define this term"*, *"add this acronym / jargon
to the glossary"*, *"update the glossary"*.

### `quenching-docs-import-memory` — drain project memory into the bundle

Migrates the durable facts in the project's Claude Code memory
(`~/.claude/projects/<cwd>/memory/`) — promoting each memory into a `standard` or `knowledge`
doc in the `docs/` bundle, or a spec (always untriaged) in `specs/plans/` — then
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
one OK, what its content stages would then drive, and what neither closes because it needs
a human.

Density figures carry **no finding code**, deliberately: a bundle can pass every check while
holding scaffolded-but-empty homes and a placeholder glossary, and that is a signal worth seeing
but not a defect list to chase. It writes nothing, and owns no contract, citing `conformance.md`
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
(regenerate the registry zone, glossary offer, self-check). Without an OKF bundle the
mint still proceeds (skill + wrapper only) and suggests `quenching-docs-align` once.

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

### `quenching-align-all` — the three fronts, one confirmation

The **structural** cross-front conductor: where the front conductors loop, this one runs the
*one* align of each of the **three** fronts, once, in dependency order — `quenching-docs-align`
(`docs/`) →
`quenching-specs-align` (`specs/`) → `quenching-skill-align` (`.claude/`). One read-only probe of
the three fronts → **one** OK authorizes the whole run under the shared cycle-authorization
contract → each sweep runs under its own doctrine, narrating its own plan → one consolidated
report.

The order is a **dependency, not a preference**: `docs/` first because the other two write OKF
artifacts *into* the bundle (the skill front's rule + registry, the `docs/standards/` docs a
spec's distillation mints); `specs/` before `.claude/` matters **only in a migration** — a
legacy `openspec/` repo carries CLI-generated `openspec-*` skill + `opsx/` command shadow copies that
`quenching-specs-align` clears before `quenching-skill-align` would otherwise inventory them.
**Front presence decides the pass** — an absent `docs/` bundle is what the plugin installs, so
Front 1 always runs; an absent `specs/` workspace is what `quenching-specs-align` scaffolds (from
the native `assets/specs/` payload, no external tool); an empty `.claude/` surface skips Front 3
with a note. It **conducts, never reimplements**, never loops a front to force a clean result, and
never acts on a front's reported residue — it names the residue and the command that closes it.

Triggers: *"align everything"*, *"align the whole repo"*, *"run all the aligns"*, *"normalize
this repo"*, *"install quenching in this repo"*, *"set the repo up end to end"*.

## The `specs/` flow — the nine `/specs:*` commands

The plugin's **spec-driven plan cycle**, and it is **entirely native**: no `npm i -g`, no Node
runtime, no `config.yaml`, no main-spec store, and no delta format. The deterministic rails are
the bundled stdlib `assets/bin/specs.py` (uniform `--json`, strict exit codes `0` ok · `1`
findings · `2` refusal), the same self-contained mold as the OKF hook — a command branches on
data, never on prose. `/specs:align` installs it into a target's `.claude/hooks/`. Every command
on this front reads the `docs/` bundle as context going in and distils durable knowledge back out
when a spec closes.

The **unit of work is a spec** — ONE markdown file, `specs/plans/YYYY-MM-DD-<slug>.md`, living
its whole pre-archive life in one folder and moving exactly once, to `specs/archive/`.
**Frontmatter records human judgments** (`priority`, `refined`, `approved`, `branch`,
`reviewed`, `merge`, `outcome`); the filesystem, git and section presence record everything else
— `ready` is a *derived* stage, and the OK to build is the `approved: {date}` stamp. Because a
spec writes its durable rule **directly into `docs/standards/`** (honestly `authority`-graded),
there is no second store to bridge to: isolation-while-building is a real git **branch or
worktree** (taken by `/specs:isolate` at any stage, recorded as `branch: {base, work}`, each task committed
alone with its sha on the task line).

| Command | Role |
| --- | --- |
| `/specs:continue` | The router: one `specs.py next --front` call ranks every candidate with a reason per row and hands off to the one command that fits. Never builds, edits, or closes anything itself. |
| `/specs:isolate` | Takes **or reports** git isolation for ONE spec at any stage: the `plan/<slug>` branch or a worktree beside the repo, and the write-once `branch: {base, work}` stamp. Reporting is a complete use of it. `execute` delegates here; `create` and `develop` name it on request. Never merges — that keeps `conclude`'s gates. |
| `/specs:status` | The front's only **read-only** view: specs by derived stage with task progress, the frontmatter records as the history they narrate, the verifier results — split into what `/specs:align` would fix, what a cycle command closes, and what neither closes. |
| `/specs:create` | ONE spec in `plans/` — effort proportional to input, never an interrogation. A sentence becomes `## Problem` alone; a Claude Code plan file becomes every section it actually supports, mapped and never invented. |
| `/specs:develop` | One question at a time with an inline recommendation, the bank chosen by the spec's derived stage — generative shaping, adversarial interrogation (recording `refined:`), gate-gap filling, discovery resolution, and the `approved` stamp offer. Never edits code. |
| `/specs:execute` | Builds `## Tasks` one verified commit at a time: clean tree required, isolation delegated to `/specs:isolate`, `verify:` run under the spec's declared policy, four-item diff self-review, then the box ticked with the subject of the commit it is about to make (`specs.py task --check --subject`) so code and box land in ONE commit. Writes only the `docs/standards/` a task explicitly names; everything else is one `specs.py discover` line. Stops at the last commit. |
| `/specs:conclude` | Closes a spec out, resumable, **merging last**: whole-branch review (`reviewed:`), the emergent `docs/`, the archive with `outcome: done` (refuses on open boxes unless forced) or `abandoned` (always allowed), ONE distillation pass and the `merge: {strategy, subject}` stamp — all on the work branch — and only then the merge. Nothing is committed to the base after it. |
| `/specs:triage` | Ranks the whole front in ONE confirmed table, writing `priority: {level, criticality, complexity, date}` per spec and nothing else — merging, never clobbering a human's ranking. |
| `/specs:align` | The front's align + installer — see below. |

The shared facts live once — the layout, the thirteen canonical sections, the gates, the record
vocabulary, the `specs.py` surface, and the `specs/`↔`docs/` boundary in
[`specs-develop/spec-driven.md`](assets/references/specs-develop/spec-driven.md),
the execution mechanics in
[`specs-execute/execution.md`](assets/references/specs-execute/execution.md),
the git defaults (read-if-present, never installed) in
[`specs-isolate/git.md`](assets/references/specs-isolate/git.md),
the distillation doctrine in
[`specs-conclude/distill.md`](assets/references/specs-conclude/distill.md).
The per-spec commands are never conducted by any sweep, because each needs fresh human intent a
conducted pass does not have. Every command on this front is **quenching-native** — no
`metadata.generatedBy` anywhere.

### `/specs:align` — force the `specs/` workspace into shape

The front's align + installer, **probe-first**: `specs.py doctor` + `validate` run before
anything is read, so a conformant workspace costs two tool calls and stops. Otherwise: ONE plan →
one OK. It **fixes**: the scaffold (copies the native `assets/specs/` payload when absent),
installs `specs.py` into `.claude/hooks/`, applies the remedies the tools declare, normalizes
spec and archive names, stamps missing frontmatter, regenerates the `plans/index.md` zone via
`specs.py plans reindex`, and **folds older layouts** — the v2 `backlog/`+`ready/` split and the
v1 three-file plans — into `plans/` (`specs.py migrate`; basenames unchanged, `archive/**` never
touched). It also **migrates a legacy `openspec/` workspace** one-way, losing interop with the
external CLI by design.

**It aligns conformance and reports the cycle** — an empty section, a complete spec awaiting its
close, an unresolved discovery are each **reported with the command that owns it**, never
auto-closed: it never authors a spec, never moves one to `archive/`, and never invents a repair
`specs.py` did not state. The contract lives in
[`specs-align/conformance.md`](assets/references/specs-align/conformance.md).


## The signature: a canonical OKF bundle of `docs/`

The plugin installs **the same tree** in every repo (adapted to what fits — a repo
without data gets no `catalog/`):

```
docs/                    # OKF bundle root
  index.md               # the ONLY index.md with frontmatter: okf_version: "0.1" + home listing
  standards/             # "how WE do it" (current) — architecture/ code/ naming/ data-modeling/
                         #   ci-cd/ workflows/ mlops/ quality/ platform/  (type: standard)
  catalog/               # our data — <system>/index.md · <schema>.md · <schema>/<table>.md
  vision/                # direction by area (type: vision)
  documentation/         # product docs site — Diátaxis prose (type: documentation)
  knowledge/             # generic knowledge we hold (type: knowledge) — ships fixed glossary.md (A–Z term lookup)
  reference/             # what we consume — tools/ libraries/ regulations/ (type: reference)
```

The **spec workspace** lives **outside** this bundle, at `specs/` (`plans/` +
`archive/`, one `YYYY-MM-DD-<slug>.md` per spec; `plans/index.md` carries a derived listing
zone) — a quenching-managed sibling created by `/specs:create` and ranked by `/specs:triage`,
not scanned by the OKF validator. An
agreed-but-unproven decision is a `standard` with `authority: background` (there is no separate
`decisions/` home).

**OKF-strict rules the plugin enforces:**

- `index.md` is **reserved** — a listing, **no frontmatter** (the one exception is the
  root `docs/index.md`, which carries **only** `okf_version: "0.1"`).
- Every concept doc (non-`index.md`/`log.md`) carries **non-empty `type`** from the
  fixed vocabulary above, plus the OKF recommended fields and the method's extra keys.
- `log.md` is **retired**: nothing creates one, appends to one, or checks one. The name
  stays reserved so a log surviving an earlier alignment is recognized rather than flagged
  as a malformed concept doc — retired is not unreserved.
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
| `docs/QUENCHING.md` | `/docs:align` | the "I want to → run this" table, the homes and `type` vocabulary, the ten `/docs:*` commands, the shared operating model (probe first, one plan → one OK, MERGE, generated zones), the enforcement hook and every config knob, recipes, and a finding-code → fix troubleshooting table |
| `specs/QUENCHING.md` | `/specs:align` | the single-folder layout, the create → develop → approve → execute → conclude lifecycle, the nine `/specs:*` commands, the frontmatter record vocabulary, the `specs.py` tool, the `specs/` ↔ `standards/` boundary, the OKF bridge, and the older-workspace migrations |
| `.claude/QUENCHING.md` | `/skill:align` | the single taxonomy axis, one file per entry point, the six `/skill:*` commands, the rule + registry artifacts, hook/settings hygiene |

They complement, never duplicate, the reserved listings: `docs/index.md` says **what** is in the
bundle, `QUENCHING.md` says **how** it is worked. `QUENCHING.md` is an **exempt** basename in
`okf-validate.py` (alongside `CLAUDE.md`/`AGENTS.md`) — a payload file, never an OKF concept.
The refresh rule is owned once, by
[`commands/docs/align.md`](commands/docs/align.md) §4, and cited by the other two:
absent → install · older banner → overwrite · same-or-newer → leave · **banner removed by a
human → keep and report**. The banner's version is filled from `VERSION` at copy time, so a
release adds no new lockstep item.

## Cost model

The plugin keeps its context and token footprint predictable on three levels:

1. **Always-on metadata (shared cap).** Every command's `description` is loaded into context
   each session, and Claude Code truncates at **1,536 characters** per command — a budget
   shared with every other installed plugin. Collapsing the 28 skill+wrapper pairs into one
   file per entry point first took the surface's always-on total from **30,705 characters to
   2,083**, measured by `skills.py budget`.

   **What that saving cost, stated plainly:** the deleted skill description is where the quoted
   trigger phrases and the `Not for:` boundary lived, so every command reported
   `sk-trigger-position` and `sk-no-boundary` against a description written as a `/`-menu label.
   Both are warnings, so the budget looked clean while the routing information was absent — see
   `docs/standards/naming/command-surface.md` §Why there is no longer a wrapper.

   **Where it stands now: 12,726 characters** (~3,182 approximate tokens) across 26 commands and
   0 agent definitions, measured 2026-07-28 — the ceiling fired the day `/specs:isolate` was
   minted, exactly as a zero-headroom ratchet is meant to, and was revised from that measurement. Most of the difference between 2,083 and that figure
   is the routing information being bought back deliberately — the triggers and boundaries the
   collapse had dropped. That measurement is also the current default ceiling, which has **no
   headroom by construction**: it equals the surface's total, so the next always-on command
   crosses it the day it is minted — `/skill:retro`, the 26th, took the other exit instead:
   `disable-model-invocation: true` drops its description from the always-on total entirely, so
   it cost **0** of the 12,726 characters and the ceiling never fired. The rule and the revision
   procedure live in
   [`docs/standards/automation/context-budget.md`](/docs/standards/automation/context-budget.md).
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
| `/docs:define` | **no pin** — the edit is mechanical, but an inline `effort: low` is part of the session's prompt-cache key, so it recomputes every input token on the next request ([`capabilities.md`](assets/references/skill-new/capabilities.md) §The cache trap). A single-entry edit does not buy that back. Carries a frontmatter `hooks:` block instead — `okf-validate.py` on its own `Write`/`Edit`, the scope ladder's narrowest rung, costing nothing to any other operation |
| `/specs:create` | **no pin** — same cache-trap reasoning; the capture is mechanical and effort-proportional, and its cost was never the model tier. Zero interrogation, no sub-agents |
| `/specs:triage` | no pin, no `effort` override — the *reading* is cheap (a few small frontmatter blocks) but the *output* is a ranking grounded in `vision/`, which is exactly the judgment the session model exists for; the human plan-gate contains misjudgment but should not have to catch it. No sub-agents |
| `/specs:isolate` | no pin, no sub-agents — a handful of `git` reads, one branch or worktree creation, and one frontmatter stamp. `Bash` is scoped to `git`/`python3`/`py`; the whole command is a decision the human makes and a record it writes |
| `/specs:status` | **no pin**, no sub-agents, **no `Write`/`Edit` in `allowed-tools`** — it classifies against a fixed finding vocabulary it does not own, and `specs.py status` is scoped to full-progress plans rather than run per plan. The former `effort: low` was dropped for the cache trap: a read-only view is not worth invalidating the session's prompt cache |
| `/docs:status` | **no pin**, no sub-agents, **no `Write`/`Edit` in `allowed-tools`** — the `docs` counterpart of the row above, and its `effort: low` was dropped for the same reason. Both bodies also forbid `context: fork` by name: each doubles as a sweep's preview, and the report has to land in the conversation where the OK will be given |
| `/specs:conclude` | no pin, no sub-agents — the branch review, the merge choice, the outcome, and the distillation are all judgment; there is nothing mechanical here to downgrade |
| `/docs:glossary-backfill` | **no pin** on the orchestrator (the former inline `effort: medium` charged the cache trap); slice sub-agents `model: haiku` + `effort: low` (pure extraction, cross-checked by the orchestrator) — a sub-agent's pin is cache-safe, it has its own context. `Bash` scoped to `python3`/`py`: its reading is `Grep`/`Glob`/`Task`, and the checker is the only shell it runs |
| `/docs:import-memory` | classification sub-agents `model: sonnet` + `effort: low`; **executor sub-agents inherit the session model** (their self-check authorizes memory deletion). `Bash` stays unrestricted **and is now priced in the body**: step 1 derives the memory directory as one compound shell expression, which no prefix grant can match |
| `/docs:align` / `/docs:harness` | repo-wide grep/find sweeps delegable to one read-only `haiku` + `effort: low` collector; every classification stays with the orchestrator when run standalone. `/docs:harness`'s `Bash` is scoped to `git grep` / `git check-ignore` / `grep` / `python3` / `py` — the two-scan sweep, the build-artifact check, the checker, and nothing else; `/docs:align` keeps the unrestricted grant its body prices. **Exception:** under `/docs:align`'s parallel content prep, harness's read-only discovery (steps 1–4, incl. MOVE/KEEP classification) runs in a background `Task` agent pinned `model: sonnet` — never haiku, same misclassification-risk rationale as the cycle's assessment agent |
| `/docs:align` (content passes) | per-pass read-only assessment via a `sonnet` + `effort: low` sub-agent (haiku ruled out: a false "nothing to do" ends the loop early) |
| `/align` | no pin, no sub-agents — the front probe is a handful of globs and two CLI calls, and every write belongs to the sweep it invokes (which carries its own policy row) |
| `/specs:align` | no pin; `Bash` scoped to `python3` / `py` / `mkdir` / `cp` / `mv` / `git mv` / `rm` — the asset copy, the confirmed renames and the approved shadow-copy deletions of step 6, and nothing wider (it previously granted bare `Bash` *alongside* those scopes, which made them dead). **Two** repo scans cover the whole rename set (never two per rename — [`sweep-doctrine.md`](assets/references/align-all/sweep-doctrine.md) §3), and only the bucketing of a large hit list is delegable to one read-only `haiku` + `effort: low` collector, after the scans. `specs.py status` runs only for full-progress plans, and the conductor hands down its inventory instead of making align re-collect it. Every classification, `specs.py`-stated-repair judgment, and the fix-vs-report split stays with the orchestrator |
| `/docs:import` | extraction/executor sub-agents may run `model: haiku` + `effort: low` — import **deletes nothing**, so a misclassification only misfiles a doc (correctable); the orchestrator keeps each `index.md` honest and resolves cross-slice dedup |
| `/docs:add` / `/docs:learn` | no pin — they inherit the session model (they classify, route, and gate operations). Both carry a frontmatter `hooks:` block running `okf-validate.py` on their own `Write`/`Edit` — rung 1 of the scope ladder and rung 1 of the handler ladder, firing only while the command runs |
| `/docs:documentation:build` | no pin, no sub-agents — the inventory is a handful of globs plus one config parse, and the expensive step is an external `mkdocs build`, not tokens; the config **merge** and the fix-vs-report split are exactly the judgment the plan gate exists to contain. `Bash` stays unrestricted **and is now priced in the body**: it drives a toolchain the plugin does not own, reachable through `pip`, `uv` or a bare `python -m` |
| `/skill:new` | no pin, no sub-agents — classification on the axis, doctrine-grade drafting, and the plan gates inherit the session model |
| `/skill:align` | no pin. Its §7 doctrine audit **may delegate collection** to read-only `Task` collectors — one per slice, reporting *what each body contains* (which levers its frontmatter carries, what it cites, where its steps end) on a surface large enough that reading every body would bury the conversation. Every verdict stays with the orchestrator: "this body has no positive prescription" is a claim about behaviour, and the read that makes it must also weigh the fix |
| `/specs:develop` | no pin, no sub-agents — the whole command *is* judgment: generating the questions a spec never answered, recommending an answer to each, and deciding when the interrogation is done. There is nothing mechanical here to downgrade, and a cheap model that asks generic questions produces exactly the refinement theatre the command exists to replace. Cost is bounded by each bank's declared stop condition, not by a model tier |
| `/specs:continue` | no pin, no sub-agents — one `specs.py next --front` call and a hand-off; the ranking logic lives in the tool, not the model |
| `/specs:execute` | no pin. A per-task **executor sub-agent is permitted** when the task declares `files:` and touches no `docs/` — pinned to the **session model, never `haiku`** (it writes production code, the same rationale that protects `/docs:import-memory`'s executors). The orchestrator keeps spec selection, every confirmation, every `specs.py task --check`/`--block`, every `docs/standards/` write, the commit, and the pause decision. Two tasks run concurrently only when `specs.py parallel` reports the `[P]` group eligible; serial is the default. **This is not `context: fork`** — the orchestrator stays in the live conversation, so the never-fork rule is untouched (`assets/references/specs-execute/execution.md` §This is not `context: fork`) |

Two rules are deliberate and must survive any future "optimization":

- **Never add `context: fork` to these skills.** Every sweep skill gates on a mid-flow
  confirmation (one plan → one OK) when run standalone — and even a cycle-authorized run
  ([`align-all/convergence.md`](assets/references/align-all/convergence.md)
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
the key Claude Code uses to detect and apply an upgrade. Mirror it in the marketplace manifest's
plugin entry (`.claude-plugin/marketplace.json`) too, and keep the `VERSION` constant in **all
three** shipped scripts — `assets/hooks/okf-validate.py`, `assets/bin/specs.py` and
`assets/bin/skills.py` — in lockstep with that pair, since each one's `--version` is what its
installing align compares against an already-installed copy in a target repo (`/docs:align` for
the hook, `/specs:align` for `specs.py`, `/skill:align` for `skills.py`). Six sources, one number.

- **4.2.0:** **nothing is written after the thing it describes, so the merge is last.** The
  task→commit anchor inverted from the commit's **sha** to its **subject** — known *before* the
  commit exists — which let two writes move ahead of the events they record. `/specs:execute` now
  ticks the box with `specs.py task --check --subject` and commits code and box together, so one
  task is literally one commit and the per-task bookkeeping commit is gone. `/specs:conclude`
  reordered: the branch review, the emergent `docs/`, the archive, the distillation and the
  `merge: {strategy, subject}` stamp all land on the work branch, and **the merge is its last
  action** — one merge carries the spec's whole footprint and nothing is committed to the base
  after it. Rebase stops destroying the record, since a subject survives a rewrite; the squash
  caveat stands. A **25th command**, `/specs:isolate`, extracts the git *action* — branch or
  worktree, at **any** stage rather than only at build time — and `specs.py next --front` became
  branch-aware, so `/specs:continue` returns the spec whose branch you are standing on and demotes
  one alive elsewhere. `parse_frontmatter` learned block mappings (indent-scoped), which is what
  lets an explicit-none merge record wrap or carry a comma. New `assets/bin/conclude-order-check.sh`
  asserts the ordering on a real history — the one claim no in-process check can see. The budget
  ceiling fired on the 25th command exactly as designed and was re-measured to **12,726**.
- **4.1.0:** **the capability layer got proved, applied and closed.** Both new mints were measured
  by `/skill:eval` — `/skill:agent:new` at +0.364 pass rate for 182,367 fewer tokens,
  `/skill:hook:new` at +0.5 for 52.5% cheaper — and each gained an intent-shaped trigger plus a
  sandboxed routing probe, taking `functional-checks.sh` to **9 assertions across 7 sandboxed
  sessions**. `skills.py` closed its two blind spots: `lint` now reads a **frontmatter `hooks:`
  block** (the scope ladder's narrowest rung, the mold's shape only, fail-open via
  `sk-hook-unparseable`) and serves both rungs from one implementation, and `budget` counts
  `agents/*.md` descriptions as its own breakdown line; the ceiling was re-measured and re-set to
  **11,565** from a run. The profile doctrine was then applied to its own author: five inline
  `effort:` pins dropped for the prompt-cache trap, `Bash` scoped on `/specs:align`,
  `/docs:harness` and `/docs:glossary-backfill` and priced in the body of the two that keep it,
  frontmatter `hooks:` blocks on `/docs:add`/`/docs:learn`/`/docs:define`, and a collection-only
  `Task` for `/skill:align`'s doctrine audit — `sk-unscoped-bash` 8 → 5, every survivor stating
  its reason. `docs/standards/automation/hooks.md` graduated to `authority: current` on that
  adopting surface; `agents.md` stayed `background` because there is no `.claude/agents/` anywhere
  to follow it. `/skill:package` was **dismissed on a real packaging run**: four mechanical
  operations, then six fields that came back requiring a human. Still twenty-four commands.
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
