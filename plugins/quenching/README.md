# quenching (plugin)

An **OKF-centric knowledge-base aligner** for the Claude Code surface of any
repository. It carries one canonical **Open Knowledge Format (OKF v0.1)** bundle
of `/docs/` and the tools to install it, force an existing base into conformance,
insert new knowledge, capture terms into a fixed glossary, drain the project's Claude
Code memory into it, import external sources into it, keep the repo's `CLAUDE.md` a thin pointer over it, and organize
the repo's own **automation surface** (`.claude/commands/`) under one
taxonomy — so every repository that adopts the plugin looks the **same**. It also carries the repo's
**spec-driven plan lifecycle**: the six `/quenching:specs:*` commands over a provider-owned specs
front backed by GitHub or Azure Boards, with the OKF bundle as its knowledge substrate, driven end
to end by the bundled stdlib `cq specs`.

The **design front** adds one DTCG source at `/.design/tokens.json`, deterministic projections
for Impeccable and editorial media, and a human-arbitrated import path for an Impeccable-authored
`DESIGN.md`. Impeccable remains optional and owns web craft; quenching owns the source, product
projection, genres, and non-web adapters.

All of it sits behind **one interface, repeated on every front**: ONE `align` per front —
probe-first, so a clean front costs a couple of tool calls — that forces the structure into
shape and carries that front's content stages. Read the next section and you know the whole
plugin.

## The seven fronts, the non-converging axes, and the one align per front

The plugin acts on **seven** surfaces of a repository, and the interface is the **same on each**.
Seven local fronts have an align, the provider-owned specs axis has no local tree to converge,
and one root command spans the seven aligned fronts. The `security` and `git` axes are
**pillars** rather than fronts — they converge no tree of their own, so they carry no align at all
(see [`architecture/align-surface.md`](../../docs/standards/architecture/align-surface.md)
§The security subject is pillar-shaped and §The git pillar has no align):

| Front / pillar | Namespace | **align** — probe-first, structure + content |
| --- | --- | --- |
| `/docs/` — the OKF bundle | `/quenching:knowledge:*` | `/quenching:knowledge:align` |
| provider-owned specs — GitHub issues or Azure work items | `/quenching:specs:*` | lifecycle and status commands |
| `/.design/` — the DTCG design source | `/quenching:design:*` | `/quenching:design:align` |
| `.claude/` — the automation surface | `/quenching:components:*` | `/quenching:components:align` |
| target-declared operations root | `/quenching:ops:*` | `/quenching:ops:align` |
| target-declared verification root | `/quenching:proof:*` | `/quenching:proof:align` |
| target-declared toolchain surface | `/quenching:toolchain:*` | `/quenching:toolchain:align` |
| target-declared delivery surface | `/quenching:delivery:*` | `/quenching:delivery:align` |
| *(pillar)* — read-only security questions | `/quenching:security:*` | **none** |
| *(pillar)* — a repository's own git facts | `/quenching:git:*` | **none** |
| **all seven aligned fronts** | *(root)* | **`/quenching:align`** |

**The probe comes before the inventory.** Each implemented align opens by running its front's own verifier
(`cq knowledge validate`, `cq design doctor`, `cq components doctor`/`lint`, `cq ops doctor`, `cq proof doctor`, `cq toolchain doctor`, `cq delivery doctor`); a clean
probe stops with nothing to inventory, plan, or confirm. Otherwise: one read-only inventory → ONE
consolidated plan → one OK → apply → verify, then the front's content stages, each run only when
the probe found it work:

| Front | Content its align carries beyond structure |
| --- | --- |
| `docs` | drains project memory, thins the harness (moving durable knowledge into homes), and OFFERS the glossary backfill on a cheap proxy — looping to a fixpoint, the one front with a real internal loop |
| `specs` | none driven — an empty section, a complete spec awaiting its close, an unresolved discovery are each **reported with the command that owns it**; every lifecycle action needs fresh human intent |
| `/.design/` | imports or preserves an external `DESIGN.md` only after source arbitration, installs missing brand assets, builds projections, and reports optional Impeccable detector results |
| `.claude/` | audits every command **body** against the writing doctrine — the one thing the migration itself is forbidden to fix — and reports each violation with the `/quenching:components:command:new` that closes it |
| `ops` | probes the declared root and router, applies mechanical and structural drift under one plan, and reports judgement findings; status is the read-only view |
| `proof` | probes the declared verification surface, applies bounded gate repairs, reports judgement findings, and keeps status read-only |
| `toolchain` | probes manifests, locks, language pins and tool configuration, applies only bounded repairs, and leaves build policy with the target owner; status is the read-only view |
| `delivery` | probes provider-equivalent workflows, reports pipeline reachability and provenance, and leaves provider, environment, promotion, publication and permission policy with the target owner; status is the read-only view |

The cross-front `/quenching:align` conducts the seven aligned fronts in dependency order on one nested OK and **loops
across fronts**, because they feed each other: a spec's distillation is glossary work the
`docs` front must then index; the design front installs product/design standards; the components front creates the rule and registry that the `docs`
listings must carry.

The specs axis has no sweep conductor: each spec is captured, defined, built, reviewed and closed
by the command that owns that stage. Defining and building remain separate decisions, and each
stage's own authorization and verification contract stays visible to the human.

Every entry point shares one contract: any item whose blast radius reaches **product code**
confirms on its own, always — and inside a conducted run, so does every **irreversible close**.
That contract lives once, in
[`align/convergence.md`](assets/references/align/convergence.md).

## The 54 commands

**One file per entry point** — Claude Code merged custom commands into skills, so each
`commands/<path>.md` carries both the description that routes to it and the body that runs; there is
no `skills/` tree and no wrapper. The tables below are the manual, and the count is a property of
their rows rather than a second structural inventory: the `53` in this heading is the manual's
canonical displayed total, while [`tests/test_readme_surface.py`](tests/test_readme_surface.py)
reads it and fails the suite whenever these tables
and `commands/**` disagree
([`quality/surface-verification.md`](../../docs/standards/quality/surface-verification.md)
§A hand-written inventory of the surface needs a machine holding its lockstep).

The split is by front and pillar: `/quenching:knowledge:*` acts on the OKF `/docs/` bundle,
`/quenching:specs:*` on provider-owned issues and work items, `/quenching:design:*` on the DTCG
source and its projections, `/quenching:components:*` on the target's `.claude/` automation surface,
`/quenching:ops:*` on the target's operations surface, `/quenching:proof:*` on the target's verification surface, `/quenching:toolchain:*` on the target's toolchain surface, `/quenching:delivery:*` on the target's delivery surface, and `/quenching:git:*` on a repository's own git facts. Two commands sit at the root. Claude auto-routes to a command by its `description`; typing the command is
the explicit entry point.

### The `knowledge` front — the OKF `/docs/` bundle

| Command | Does |
| --- | --- |
| `/quenching:knowledge:align` | Forces `/docs/` into the canonical OKF bundle and pulls in the content sitting out-of-band — probe first, then ONE confirmed plan, looped to a fixpoint. |
| `/quenching:knowledge:status` | The front's only **read-only** view: where the bundle stands, what is conformant, what drifted. Writes nothing. |
| `/quenching:knowledge:add` | Inserts ONE concept doc — right home, right type, honest stamp. |
| `/quenching:knowledge:learn` | Captures ONE piece of generic understanding into `concepts/`, for what is true beyond this repo. |
| `/quenching:knowledge:define` | Adds or refines ONE entry in the fixed glossary. |
| `/quenching:knowledge:glossary-backfill` | Sweeps the whole bundle for terms nobody ever defined, and backfills them. |
| `/quenching:knowledge:import` | Imports an external source — files, folders, URLs — into the bundle as many docs, with provenance. |
| `/quenching:knowledge:import-memory` | Drains the project's Claude Code memory into the bundle, then clears it. |
| `/quenching:knowledge:documentation:produce` | Conducts the whole documentation pipeline: site layer, sourced pages, bounded review, strict-build QA. |
| `/quenching:knowledge:documentation:plan` | Builds the sourced architecture — reader journeys and the output contracts each page answers to. |
| `/quenching:knowledge:documentation:write` | Writes the Diátaxis pages from that plan, sourced and never invented. |
| `/quenching:knowledge:documentation:review` | Scores pages against the eleven-dimension quality gate **without changing a byte**. |
| `/quenching:knowledge:documentation:build` | Owns the Zensical site layer — extensions, CSS, nav, and the strict build. |

### The `design` front — the `/.design/` DTCG source and projections

| Command | Does |
| --- | --- |
| `/quenching:design:align` | Installs or converges the brand pack, preserves source truth, arbitrates external DESIGN.md proposals, and rebuilds every projection. |
| `/quenching:design:status` | Reports DTCG validity, generated identity, sidecar/assets, genres, adapters, and optional Impeccable detector state without writing. |
| `/quenching:design:genre:new` | Mints ONE editorial genre contract with fields, register, and HTML/Typst/PDF destinations. |

`cq design build` and `cq design import` are the deterministic rails used by these commands. The
source is DTCG 2025.10; `DESIGN.md` is a deliberately lossy portable projection, while rich
motion, shadows, breakpoints, and snippets remain in the source and sidecar.

### The `components` front — the target's `.claude/` surface

| Command | Does |
| --- | --- |
| `/quenching:components:align` | Converges the whole `.claude/` surface onto one file per entry point, then audits every body and rewrites every description against the writing doctrine. |
| `/quenching:components:status` | Reports the command count, fronts and finding codes for the target's automation surface without writing. |
| `/quenching:components:command:new` | Mints or edits ONE command — the structural half, including its `description`. |
| `/quenching:components:command:eval` | Measures whether a command actually teaches anything: with/without runs, graded on evidence rather than on how the body reads. |
| `/quenching:components:command:retro` | Mines ONE session for what it evidences about ONE command that ran in it — cost, redundancy, bugs, and what the human had to fix by hand. |
| `/quenching:components:agent:new` | Mints or edits ONE subagent definition, scoping its tools to the narrowest set and pricing its always-on cost. |
| `/quenching:components:hook:new` | Wires ONE scoped hook — the narrowest scope and cheapest handler that still catch what they must. Warns by default; blocks only on the human's word. |
| `/quenching:components:harness:align` | Refactors `CLAUDE.md`/`AGENTS.md` into thin pointers over the bundle, so doctrine lives once. |

### The ops front — the target's declared operations surface

| Command | Does |
| --- | --- |
| `/quenching:ops:align` | Probes the declared operations root and router, applies mechanical and structural drift under one plan, and reports judgement findings without driving them. |
| `/quenching:ops:status` | Reports the root, router, packages, lifecycle, findings by band, and registry freshness without writing. |
| `/quenching:ops:entrypoint:new` | Mints ONE Python entry point from the contract, registers it in the declared router, and regenerates the operations registry. |

### The proof front — the target's declared verification surface

| Command | Does |
| --- | --- |
| `/quenching:proof:align` | Probes the proof gate, applies mechanical and bounded structural repairs under one plan, defers a floor when the measured surface changes, and reports judgement findings without driving them. |
| `/quenching:proof:status` | Reports layers, fixtures, measured roots, floors, CI evidence, findings by band, and the explicit fact that the suite was not run — without writing. |
| `/quenching:proof:layer:new` | Mints one named layer with its marker, reach, budget, fixture home and collection rule, then proposes test moves for a separate confirmation. |

### The toolchain front — manifests, locks, pins and tool configuration

| Command | Does |
| --- | --- |
| `/quenching:toolchain:align` | Probes applicability, inventories the target's toolchain artifacts, applies only mechanical and bounded structural repairs, and reports target-owned build policy. |
| `/quenching:toolchain:status` | Reports applicability, manifests, locks, language pins, tool configuration and `tc-*` findings without writing. |

### The delivery front — workflows, reachability and release shape

| Command | Does |
| --- | --- |
| `/quenching:delivery:align` | Probes provider-equivalent workflows, applies bounded pipeline-shape repairs under one plan, and reports provider and release policy without choosing it. |
| `/quenching:delivery:status` | Reports applicability, workflow inventory, reachability, provenance and `delivery-*` findings without writing or running a pipeline. |

### The security pillar — read-only repository security questions

| Command | Does |
| --- | --- |
| `/quenching:security:status` | Reports security questions and ownership findings without aligning, repairing or writing repository values. |

### The `git` pillar — a repository's own git facts

| Command | Does |
| --- | --- |
| `/quenching:git:branch` | Takes isolation for a build — worktree, branch, or in place — recommending a worktree, stating its cost, and stamping the `branch:` record. |
| `/quenching:git:commit` | Commits what is already staged, under the target's own convention when one is declared. Never `git add -A`. |
| `/quenching:git:commit-incremental` | Turns the current worktree's pending changes into cohesive commits with explicit paths and safe stop conditions. |
| `/quenching:git:push` | Publishes one branch to an exact remote and refspec after measuring preconditions and receiving confirmation, without force or PR side effects. |
| `/quenching:git:revert` | Creates a compensating commit for one known target after showing its effect and requiring an explicit mainline for merges, without rewriting history. |
| `/quenching:git:pr:create` | Pushes and opens a pull request, with `Closes #<n>` when an issue is named, reporting plainly whether that keyword will actually close it. |
| `/quenching:git:pr:status` | Reports one read-only snapshot of a pull request's provider state, checks, reviews, threads and mergeability, preserving unknown causes. |
| `/quenching:git:merge` | Merges a branch home on one of four strategies, offered and never chosen for the human. |
| `/quenching:git:sync` | Rebases a work branch onto the latest base, with `--update-refs` so a stacked branch is not orphaned. |
| `/quenching:git:cleanup` | Prunes branches merged or gone and worktrees git still registers with no directory on disk — nothing pruned the human did not pick from that report. |
| `/quenching:git:pr:review` | Works through a PR's unresolved review threads, one confirmation per thread. |

The `security` and `git` pillars carry no `align`: they converge no tree, only answer read-only
questions about the target's live evidence, so there is nothing a probe could find drifted
([`architecture/align-surface.md`](../../docs/standards/architecture/align-surface.md) §The
security subject is pillar-shaped and §The git pillar has no align). The `specs` axis hands off to
the git pillar rather than executing git
itself — `/quenching:specs:execute` invokes `/quenching:git:branch` for isolation, and
`/quenching:specs:conclude` reviews, distils, archives and proves the pre-merge gate green, then
**names** `/quenching:git:pr:create` or `/quenching:git:merge` as the human's own next command
instead of running either.

### The two root commands

| Command | Does |
| --- | --- |
| `/quenching:align` | The one align that spans the seven aligned fronts, on ONE confirmation — conducting each front's own align in dependency order, never reimplementing any of them. |
| `/quenching:handoff` | Compacts the current conversation into a handoff document a fresh session can continue from — referencing existing plans, issues, commits and diffs rather than duplicating them. |

The `specs` front has six commands and a flow worth reading as a whole, so it gets its own section
below.

## The `specs` flow — the six `/quenching:specs:*` commands

The plugin's **spec-driven plan cycle** is provider-owned: GitHub issues and Azure Boards work
items are the system of record, and their body carries the canonical spec. The conceptual model
(thirteen sections, seven frontmatter records, derived stages) is identical whichever provider is
chosen — only *where and how* it is serialized differs, which is why every command drives
`assets/bin/cq specs` (uniform `--json`, strict exit codes `0` ok · `1` findings · `2` refusal)
rather than a repository path. Azure Boards ships implemented but **without an end-to-end run
against a real Azure DevOps project** — `doctor`'s `sp-backend-unproved` finding, plus a one-line
stderr warning on its first write each process, names that gap every time it is selected. Every
command on this front reads the `/docs/` bundle as context going in and distils durable
knowledge back out when a spec closes.

The **unit of work is a spec** — ONE canonical markdown document for its whole lifecycle. It is an
issue or work item **whose body is the whole document** — no sub-issues, no child work items; a document past
GitHub's 65,536-character body ceiling (two of this repository's 69 specs) spills into
continuation comments on its own issue and comes back byte for byte — with no repository specs tree
required. **Frontmatter records human judgments** (`priority`, `refined`,
`approved`, `branch`, `reviewed`, `merge`, `outcome`); the provider, git and section state record
everything else — `ready` is a *derived* stage, and the OK to build is the
`approved: {date}` stamp. Four more frontmatter keys — `tags`, `assignee`, `start`, `target` — are
**state, never records**: each has a faithful native counterpart on at least one backend (issue
labels/assignees on `github`, `System.Tags`/`System.AssignedTo`/the two scheduling dates on
`azure-boards`) and is reassembled from it on read rather than kept in the document, so a human's
edit on the tracker IS the spec's new value. A fifth key, `summary:`, is neither a record nor one
of those four — one line saying what the spec is, written at capture and refreshed by every
`/quenching:specs:develop` pass, with no native counterpart anywhere, and it is what
`cq specs next --front --table` prints as its `Summary` column. `.claude/quenching.json` is where a target declares
`backend`, the per-backend placement (`azureStates`, `azurePlacement`, `azureColumns`) and the
project's own `subjects`/`tagCatalog` — the closed sets `/quenching:specs:create` proposes a spec's subject
and tags from, confirmed by a human, never picked silently. Because a spec writes its durable rule
**directly into `/docs/standards/`** (honestly `authority`-graded), there is no second store to
bridge to:
isolation-while-building is a real git **branch or worktree** (offered inline by `/quenching:specs:execute`
when it starts from the base branch, recorded as `branch: {base, work}`, each task committed alone
with its sha on the task line). `cq specs export --spec <slug> | --all` dumps the canonical markdown to disk on demand —
write-only, nothing reads it back, so it is never a second store — the mitigation `## Risks`
names for losing access to an external backend.

| Command | Role |
| --- | --- |
| `/quenching:specs:status` | The front's only **read-only** view: specs by derived stage with task progress, the frontmatter records as the history they narrate, the verifier results, and provider configuration findings. |
| `/quenching:specs:create` | ONE spec in `plans/`, ONE call, ONE closing screen — effort proportional to input, never an interrogation. A sentence becomes `## Problem` and `summary:`; a Claude Code plan file becomes every section it actually supports, mapped and never invented. Subject, type, tags and `complexity` are resolved and written with the capture, then shown — corrected or not — on the one screen at the end, which also offers to hand straight into `/quenching:specs:develop` — whether that pass asks anything is the `complexity` the same screen shows. |
| `/quenching:specs:develop` | Two operations in ONE pass, both derived and neither offered as a choice: **compose** takes the spec from wherever its derived stage leaves it to a closed ten-section ready set, and **refine** argues with the composed spec and may overturn anything in it, the proposal included. Discovery resolution opens the pass, the approval close ends it — recommending approve, refine, or refine with the premortem against the spec's own signals. Questions grouped by dependency, each with an inline recommendation; one edit per pass, records `refined:`. Never edits code. |
| `/quenching:specs:execute` | Builds `## Tasks` one verified commit at a time: clean tree required, isolation offered inline when it starts from the base branch, `verify:` run under the spec's declared policy, four-item diff self-review, then the box ticked with the subject of the commit it is about to make (`cq specs task --check --subject`) so code and box land in ONE commit. Writes only the `/docs/standards/` a task explicitly names; everything else is one `cq specs discover` line. Marks an isolated branch's own description with the slug(s) it built there — never under `In place` — so `conclude` can self-discover it later. Stops at the last commit. |
| `/quenching:specs:conclude` | Closes a spec out, resumable, **merging last**: whole-branch review (`reviewed:`), the emergent `/docs/`, the archive with `outcome: done` (refuses on open boxes unless forced) or `abandoned` (always allowed), ONE distillation pass, the release obligations your standards attach to the merge itself (a version bump, a changelog entry — never a spec task) and the `merge: {strategy, subject, pr}` stamp — all on the work branch — and only then the merge, by the **route** you chose alongside the strategy: local, or a pull request where `gh` resolves the repo (pushed, opened and merged in one consented block, with `pr:` recorded). Called with no `--spec`, reads the branch's own marking first — one valid slug resolves silently, several ask, none falls to a diff-measured offer to materialize a minimal spec — before falling back to a plain list-and-ask. Nothing is committed to the base after it. |
| `/quenching:specs:triage` | Ranks the whole front in ONE confirmed table, writing `priority: {level, criticality, complexity, date}` per spec and nothing else — merging, never clobbering a human's ranking. |

The shared facts live once — the provider-owned document, the thirteen canonical sections, the
gates, the record vocabulary, and the `cq specs` surface in
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

## The signature: a canonical OKF bundle of `/docs/`

The plugin installs **the same tree** in every repo (adapted to what fits — a repo
without data gets no `catalog/`):

```
/docs/               # OKF bundle root
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

Specs live in the configured external provider and are not a second repository tree or part of
the OKF bundle. `/quenching:specs:create` and `/quenching:specs:triage` operate through `cq specs`,
not through files checked into the target repository. An agreed-but-unproven decision is a
`standard` with `authority: background` (there is no separate
`decisions/` home).

**OKF-strict rules the plugin enforces:**

- `index.md` is **reserved** — a listing, **no frontmatter** (the one exception is the
  root `/docs/index.md`, which carries **only** `okf_version: "0.1"`).
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

The OKF contract lives in the skills' `references/`; the installable payload is in
[`assets/`](assets/README.md).

## Model policy

The command registry loads at **session start**, so surface changes require fresh `claude -p`
processes. `assets/checks/functional-checks.sh` runs them with `--plugin-dir` and proves root
substitution, conductor reachability and description routing. Each check is a **billed agent
session** owned by the command that changes the surface; the default is the body subset and
spoken routing is opt-in (`--only 3`).

**The model policy is conservative — judgment is never downgraded:**

| Surface | Policy |
| --- | --- |
| `/quenching:knowledge:define` | **no pin** — the edit is mechanical, but an inline `effort: low` is part of the session's prompt-cache key, so it recomputes every input token on the next request ([`capabilities.md`](assets/references/components-command-new/capabilities.md) §Model and effort). A single-entry edit does not buy that back. **No hook either** — the rung-1 frontmatter block this row once described was removed when the plugin's own wiring covered the same case, and that wiring was later discontinued outright, so nothing answers a write event here any more (`/docs/standards/automation/hooks.md`). What checks conformance at write time is the body's own **Self-check against the conformance core** step, run by the command, not fired by anything |
| `/quenching:specs:create` | **`model: sonnet`** — the capture is mechanical and effort-proportional, so the tier it does not need is the expensive one. Zero interrogation before the write, no sub-agents. The pin is paid for once, in the **cache trap** ([`capabilities.md`](assets/references/components-command-new/capabilities.md) §Model and effort): an inline `model:` is part of the session's prompt-cache key, so **changing** it recomputes every input token on the next request. A pin left alone costs nothing after the first run, which is what makes a stable pin affordable and pin-churn expensive. **The closing screen's hand-off into `/quenching:specs:develop` (`model: opus`) is the one path that changes the pin mid-session** — an inline `model:` switch recomputes the input tokens on the very next request, so the hand-off is not free the way an ordinary `Skill` invocation is; unmeasured as of this writing, and worth a real run before assuming the cost is negligible |
| `/quenching:specs:triage` | **`model: opus`**, no `effort` override — the *reading* is cheap (a few small frontmatter blocks) but the *output* is a ranking grounded in `vision/`, which is exactly the judgment the top tier exists for; the human plan-gate contains misjudgment but should not have to catch it. No sub-agents |
| `/quenching:specs:status` | **no pin**, no sub-agents, **no `Write`/`Edit` in `allowed-tools`** — it classifies against a fixed finding vocabulary it does not own, and `cq specs status` is scoped to full-progress plans rather than run per plan. The former `effort: low` was dropped for the cache trap: a read-only view is not worth invalidating the session's prompt cache |
| `/quenching:knowledge:status` | **no pin**, no sub-agents, **no `Write`/`Edit` in `allowed-tools`** — the `docs` counterpart of the row above, and its `effort: low` was dropped for the same reason. Both bodies also forbid `context: fork` by name: each doubles as a sweep's preview, and the report has to land in the conversation where the OK will be given |
| `/quenching:specs:conclude` | **`model: opus`**, no sub-agents — the branch review, the merge choice, the outcome, and the distillation are all judgment; there is nothing mechanical here to downgrade, and the review reads a whole branch diff for coherence rather than one task's |
| `/quenching:knowledge:glossary-backfill` | **no pin** on the orchestrator (the former inline `effort: medium` charged the cache trap); slice sub-agents `model: haiku` + `effort: low` (pure extraction, cross-checked by the orchestrator) — a sub-agent's pin is cache-safe, it has its own context. `Bash` scoped to `python3`/`py`: its reading is `Grep`/`Glob`/`Task`, and the checker is the only shell it runs |
| `/quenching:knowledge:import-memory` | classification sub-agents `model: sonnet` + `effort: low`; **executor sub-agents inherit the session model** (their self-check authorizes memory deletion). `Bash` stays unrestricted **and is now priced in the body**: step 1 derives the memory directory as one compound shell expression, which no prefix grant can match |
| `/quenching:knowledge:align` / `/quenching:components:harness:align` | repo-wide grep/find sweeps delegable to one read-only `haiku` + `effort: low` collector; every classification stays with the orchestrator when run standalone. `/quenching:components:harness:align`'s `Bash` is scoped to `git grep` / `git check-ignore` / `grep` / `python3` / `py` — the two-scan sweep, the build-artifact check, the checker, and nothing else; `/quenching:knowledge:align` keeps the unrestricted grant its body prices. **Exception:** under `/quenching:knowledge:align`'s parallel content prep, harness's read-only discovery (steps 1–4, incl. MOVE/KEEP classification) runs in a background `Task` agent pinned `model: sonnet` — never haiku, same misclassification-risk rationale as the cycle's assessment agent |
| `/quenching:knowledge:align` (content passes) | per-pass read-only assessment via a `sonnet` + `effort: low` sub-agent (haiku ruled out: a false "nothing to do" ends the loop early) |
| `/quenching:align` | no pin, no sub-agents — the front probe is a handful of globs and two CLI calls, and every write belongs to the sweep it invokes (which carries its own policy row) |
| `/quenching:knowledge:import` | extraction/executor sub-agents may run `model: haiku` + `effort: low` — import **deletes nothing**, so a misclassification only misfiles a doc (correctable); the orchestrator keeps each `index.md` honest and resolves cross-slice dedup |
| `/quenching:knowledge:add` / `/quenching:knowledge:learn` | no pin — they inherit the session model (they classify, route, and gate operations). **Neither carries a frontmatter hook block** — the rung-1 blocks these two once carried were removed when the plugin's own wiring covered the same case, and that wiring was later discontinued outright, so no hook fires on their writes (`/docs/standards/automation/hooks.md`). Each body's own **Self-check against the conformance core** step is the conformance check at write time: a step the command runs, not a rung anything enforces |
| `/quenching:knowledge:documentation:build` | no pin, no sub-agents — the inventory is a handful of globs plus one config parse, and the expensive step is an external `zensical build`, not tokens; the config **merge** and the fix-vs-report split are exactly the judgment the plan gate exists to contain. `Bash` stays unrestricted **and is now priced in the body**: it drives a toolchain the plugin does not own, reachable through `pip`, `uv` or a bare `python -m` |
| `/quenching:knowledge:documentation:produce` | no pin, no sub-agents — the conductor sequences four named stages under one authorization and reports their summaries; it has no `Write`/`Edit` grant |
| `/quenching:knowledge:documentation:plan` | no pin, no sub-agents — source diagnosis, IA and six contracts require the session's judgment; only the plan-of-record is written |
| `/quenching:knowledge:documentation:write` | no pin on the author; large batches may fan out `Task` slices pinned to the session model, never `haiku`, because each slice writes human-facing prose |
| `/quenching:knowledge:documentation:review` | no pin, read-only; large page sets may fan out `Task` slices without write tools, returning condensed rubric verdicts |
| `/quenching:components:command:new` | no pin, no sub-agents — classification on the axis, doctrine-grade drafting, and the plan gates inherit the session model |
| `/quenching:components:align` | no pin. Its §7 doctrine audit **may delegate collection** to read-only `Task` collectors — one per slice, reporting *what each body contains* (which levers its frontmatter carries, what it cites, where its steps end) on a surface large enough that reading every body would bury the conversation. Every verdict stays with the orchestrator: "this body has no positive prescription" is a claim about behaviour, and the read that makes it must also weigh the fix |
| `/quenching:specs:develop` | **`model: opus`** — the whole command *is* judgment: generating the questions a spec never answered, recommending an answer to each, and deciding when the interrogation is done. There is nothing mechanical here to downgrade, and a cheap model that asks generic questions produces exactly the refinement theatre the command exists to replace. Cost is bounded by each stage's declared stop condition and by one edit per pass, not by a model tier. One **read-only** sub-agent is permitted, and only for compose and refine: it sweeps the code and the `/docs/standards/` the spec declares and returns one table (`assets/references/specs-develop/questions.md` §Gathering the evidence). It reads; it never asks, writes, or decides — every question, every `cq specs` call and every confirmation stays with the orchestrator. **This is not `context: fork`**, which cannot ask a question at all, so the never-fork rule is untouched |
| `/quenching:specs:execute` | **`model: sonnet`** — the loop is write · verify · self-review · tick · commit against a spec that already decided what to build, and the judgment it does keep is gated by a human at every confirmation. A per-task **executor sub-agent is permitted** when the task declares `files:` and touches no `/docs/` — pinned to the **session model, never `haiku`**; with this command pinned, *session model* means `sonnet` for those executors (it writes production code, the same rationale that protects `/quenching:knowledge:import-memory`'s executors). The orchestrator keeps spec selection, every confirmation, every `cq specs task --check`/`--block`, every `/docs/standards/` write, the commit, and the pause decision. Two tasks run concurrently only when `cq specs parallel` reports the `[P]` group eligible; serial is the default. **This is not `context: fork`** — the orchestrator stays in the live conversation, so the never-fork rule is untouched (`assets/references/specs-execute/execution.md` §This is not `context: fork`) |

Shared contracts keep gates explicit; missing `gh` or `az` is a named refusal
(exit 2).

## Install

Published installation (recommended): from inside Claude Code, add the marketplace and install
the plugin:

```text
/plugin marketplace add holetz/claude-quenching
/plugin install quenching@quenching
```

Run `/reload-plugins` after installation when the session was already open.

Local development only:

```bash
claude --plugin-dir ./plugins/quenching
```

`--plugin-dir` loads the checkout directly for plugin development and testing; it is not the
normal adoption or upgrade path. A published installation is managed by Claude Code. All skills
reach the shared payload via `${CLAUDE_PLUGIN_ROOT}/assets/...`.

## Uninstall or reverse

To remove the installed plugin while keeping the marketplace available:

```text
/plugin uninstall quenching@quenching
/reload-plugins
```

Removing the marketplace itself (`/plugin marketplace remove quenching`) also uninstalls plugins
installed from it. Neither operation deletes the target repository's `/docs/`, `.claude/` or
`.claude/quenching.json` files: those are repository-owned data and configuration. To reverse an
alignment, review and revert the target repository's own commits; uninstalling the plugin is not
a data rollback. If an upgrade is the problem, disable or uninstall the plugin first, then
reinstall the previously published version or load its known checkout with `--plugin-dir` for
development-only recovery. Reload the session after changing the installation.

The CLI has two equivalent entry points: `bin/cq` on the plugin-managed `PATH` and
`assets/bin/cq` with an explicit plugin root. Their resolution rules are in
[`assets/references/align/tool-resolution.md`](assets/references/align/tool-resolution.md).

## Upgrade

The release history is kept in the root [`CHANGELOG.md`](../../CHANGELOG.md). The plugin version is
updated only by a deliberate release; `cq specs release <version>` checks the changelog entry and
updates the published artifacts in lockstep. See
[`ci-cd/versioning-release.md`](../../docs/standards/ci-cd/versioning-release.md) for the release
contract.
