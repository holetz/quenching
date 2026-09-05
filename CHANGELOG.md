# Changelog

Release history for the quenching plugin. The installation and upgrade contract remains in the plugin
README; this file keeps the versioned record that `cq specs release` checks before publishing.

Resolution is **plugin-first, with no install and no third rung** — every command reaches its tool
either bare through `bin/cq` on the PATH or at `${CLAUDE_PLUGIN_ROOT}/assets/bin/cq`, and both are
the same file inside the plugin — so a version bump reaches every consumer the moment Claude Code
applies the plugin upgrade; there is nothing installed to compare against and nothing to sync.

What a bump moves, when it moves, and why each half of the lockstep matters is one rule with one
owner: [`ci-cd/versioning-release.md`](docs/standards/ci-cd/versioning-release.md). The
short version for a consumer: the version is published once, deliberately, as a release — never at a
spec's own conclude — and `cq --version` is what answers which one you are running.

## 6.3.0

the ranked front became **native to the tool**. `cq specs next --front --table`
  renders the ordered listing itself instead of every caller re-deriving it, with `summary:` as its
  own column — one line saying what a spec is, written at capture and refreshed by every
  `/quenching:specs:develop` pass, and the only short description a ranked listing prints. Four
  command bodies dropped their hand-rolled renderers onto it.

## 6.2.0

`cq` stopped depending on how it was invoked. The tool resolves per call — bare on the
  PATH or at `${CLAUDE_PLUGIN_ROOT}/assets/bin/cq`, the same file either way — which removed the
  `PATH` assumption every body used to carry. Commands were also re-allocated by category, so a
  command's path names the front that owns it.

## 6.1.0

**`/.docs/` became `/docs/`.** The bundle, the commands, the standards, the
  skeleton and every citation moved together; `type` follows the home a doc sits in, and that rule
  became a standard rather than a convention people remembered.

## 6.0.1

the section squash — a build commits one commit **per `## Tasks` section**, not one per
  task, with the per-task subjects repaired onto the squashed commit afterwards. `/quenching:specs:execute`'s
  steps f/h/i were tightened to fit the body cap.

## 6.0.0

**the tooling modularized.** Three standalone tools from the pre-modularization
  layout became one binary, `cq`, over a `quenching` package with a pillar per front —
  `cq specs`, `cq knowledge`, `cq components`, `cq git`. The `skills` pillar was renamed
  `components` with it. Every command body drives the pillar, and nothing installs a copy of
  anything any more.

## 5.0.0

the Azure Boards backend stopped costing one `az` call per field. Writes batch into a
  single PATCH, the board column is resolved and diffed rather than written blind, and
  `architecture/spec-backend.md` was written to hold the placement and granular-reading rules the
  work revealed.

## 4.13.0

the specs front's preamble citations were aligned to the bodies that actually carry
  them, and the Azure Boards backend was positioned honestly — shipped, but without an end-to-end
  run against a real project, which `doctor`'s `sp-backend-unproved` finding names on every
  selection.

## 4.2.0

**nothing is written after the thing it describes, so the merge is last.** The
  task→commit anchor inverted from the commit's **sha** to its **subject** — known *before* the
  commit exists — which let two writes move ahead of the events they record. `/quenching:specs:execute` now
  ticks the box with `cq specs task --check --subject` and commits code and box together, so one
  task is literally one commit and the per-task bookkeeping commit is gone. `/quenching:specs:conclude`
  reordered: the branch review, the emergent `/docs/`, the archive, the distillation and the
  `merge: {strategy, subject}` stamp all land on the work branch, and **the merge is its last
  action** — one merge carries the spec's whole footprint and nothing is committed to the base
  after it. Rebase stops destroying the record, since a subject survives a rewrite; the squash
  caveat stands. A **25th command** (an isolation command, since retired) extracts the git *action* — branch or
  worktree, at **any** stage rather than only at build time — and `cq specs next --front` became
  branch-aware, so the front router (since retired) returned the spec whose branch you were standing on and demoted
  one alive elsewhere. `parse_frontmatter` learned block mappings (indent-scoped), which is what
  lets an explicit-none merge record wrap or carry a comma. The ordering check (now retired)
  asserted the ordering on a real history — the one claim no in-process check can see. The always-on
  ceiling fired on the 25th command exactly as designed and was re-measured to **12,726**.

## 4.1.0

**the capability layer got proved, applied and closed.** Both new mints were measured
  by `/quenching:components:command:eval` — `/quenching:components:agent:new` at +0.364 pass rate for 182,367 fewer tokens,
  `/quenching:components:hook:new` at +0.5 for 52.5% cheaper — and each gained an intent-shaped trigger plus a
  sandboxed routing probe, taking `functional-checks.sh` to **9 assertions across 7 sandboxed
  sessions**. `cq components` closed its two blind spots: `lint` now reads a **frontmatter `hooks:`
  block** (the scope ladder's narrowest rung, the mold's shape only, fail-open via
  `sk-hook-unparseable`) and serves both rungs from one implementation, and the cost report counts
  `agents/*.md` descriptions as its own breakdown line; the ceiling was re-measured and re-set to
  **11,565** from a run. The profile doctrine was then applied to its own author: five inline
  `effort:` pins dropped for the prompt-cache trap, `Bash` scoped on the specs-front align,
  `/quenching:components:harness:align` and `/quenching:knowledge:glossary-backfill` and priced in the body of the two that keep it,
  frontmatter `hooks:` blocks on `/quenching:knowledge:add`/`/quenching:knowledge:learn`/`/quenching:knowledge:define`, and a collection-only
  `Task` for `/quenching:components:align`'s doctrine audit — `sk-unscoped-bash` 8 → 5, every survivor stating
  its reason. `/docs/standards/automation/hooks.md` graduated to `authority: current` on that
  adopting surface; `agents.md` stayed `background` because there is no `.claude/agents/` anywhere
  to follow it. A proposed `components package` verb was **dismissed on a real packaging run**: four mechanical
  operations, then six fields that came back requiring a human. Still twenty-four commands.

## 1.0.0

**the middle front went fully native — the external OpenSpec CLI is gone.** The
  `openspec/` workspace this plugin used to *drive* (`@fission-ai/openspec`, `openspec init`,
  `config.yaml`, a main-spec store, delta specs) is replaced by a **native `specs` front** the
  plugin owns end to end. There is **no `npm i -g`, no Node prerequisite, no delta format**: the
  deterministic rails are the new bundled stdlib **`assets/bin/cq specs`**
  (`new`/`list`/`status`/`next`/`task`/`backlog`/`validate`/`archive`/`doctor`, uniform `--json`,
  exit codes `0`/`1`/`2`), the second self-contained tool beside `cq knowledge validate`, installed by
  the specs-front align into a target's `.claude/hooks/`. The **unit of work is a plan**
  (`/.specs/<plan-name>/`: `proposal.md`, `design.md`, `tasks.md`, `.specs.json`), not an
  "OpenSpec change" — and because a plan writes its durable rule **straight into
  `/docs/standards/`**, honestly `authority`-graded, there is nothing to sync: isolation-while-building
  is a real git **branch or worktree** (offered by `/specs:apply`), not a markdown delta. The
  `specs`-front conductor pipeline drops to **3 stages** (align → plan-archive → backlog-triage) —
  the old sync stage and `openspec-sync-specs` skill are **removed**. Commands moved from `/opsx:*`
  to **`/quenching:specs:*`** (plan skills under `/quenching:specs:develop`, inbox under `/specs:capture`), the inbox
  from `openspec/backlog/` to **`/.specs/backlog/`**, and every finding code from `os-*` to `sp-*`.
  All twenty-seven skills now share **one `quenching-<front>-<object>-<verb>` taxonomy** — no
  separate `openspec-*` family, no `metadata.generatedBy` anywhere. New
  **`/specs:from-claude`** turns a `~/.claude/plans/*.md`
  file into an archivable plan so ad-hoc work gains the archive-time distillation. That align
  **migrates a legacy `openspec/` workspace one-way** (flatten, fold main specs into
  `/docs/standards/`, drop `config.yaml`/deltas, clear the CLI shadow copies) — interop with the
  external CLI is lost by design. Still **twenty-seven** skills; the skill↔wrapper bijection holds
  at 27↔27.

## 0.19.0

**the `openspec/` front's lifecycle closed, and the sweep contract given one
  owner.** Two new quenching-native skills complete the front. **`/quenching:specs:status`**
  is its only read-only view — changes with progress and state, the backlog by
  priority, the three verifier results, split into what the specs-front align would fix, what
  `/specs:align-and-update` would drive, and what neither closes; it reports in the sweep's own
  `os-*` vocabulary, so it is an honest dry run of the sweep you are about to authorize.
  **`/specs:archive`** is the exit `archive-change` could not give: a
  change that will **not** be built is archived with an `ABANDONED.md` and **no spec sync**, its
  seed backlog task is offered back (untriaged), and the harvest is capped at
  `authority: background`. That closes the one real hole in the task lifecycle — `/quenching:specs:develop`
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
  and each align states only its own front's deltas. The `openspec/` ↔ `/docs/` boundary is
  declared normatively once, in the specs-develop skill's `openspec.md` §Boundary (retired along
  with `openspec/` support itself in 1.0.0). The backlog's
  prose "self-check" is gone: `cq knowledge validate` gained **`--listing-root`** and now checks
  `openspec/backlog/` for real (`type: task` is also exempted from the `resource` recommendation,
  since the mold omits it on purpose) — the same checker that guards `/docs/`, pointed at a tree
  the bundle root never covers.
  **Performance.** `/specs:align-and-update` hands its assessment inventory down to
  the specs-front align instead of making it re-collect against an untouched disk (a pass paid for
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
  (`/quenching:knowledge:documentation:build`) owns the mkdocs-material **site layer** over the `documentation/`
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

## 0.18.0

**the interface completed — one 2×4 matrix, and `converge` renamed.** 0.17.0 gave
  every front an `align`; this release gives every front an **`align-and-update`** and renames
  the concept so it says what it does. `quenching-converge` → **`quenching-knowledge-align-and-update`**
  (`knowledge:converge` → `knowledge:align-and-update`, both retired since) — clean cut, no compatibility alias. New
  **`specs:align-and-update`** (retired since) drives the cycle actions
  the specs-front align only reports: align → archive each complete change (syncing specs and
  distilling into `/docs/`) → sync leftover deltas → triage the inbox, looped; **each archive
  confirms on its own**. New **`quenching-components-align-and-update`** (`components:align-and-update`, retired since)
  adds the one thing the align is forbidden to do — a **read-only doctrine audit of every skill
  body**, reported with the `/quenching:components:command:new` that fixes it, never rewritten. New
  **`quenching-align-and-update-all`** (root `/align-and-update`) loops all three fronts,
  because they feed each other (an archive's distillation is glossary work; the skill front's
  registry is a `/docs/` listing). **Architectural fix:** the cycle-authorization + convergence
  contract left `quenching-converge/references/cycle.md` — where it had become misplaced, being
  cited by every conductor — for its own neutral owner,
  `quenching-align-and-update-all/references/convergence.md`; each front's `cycle.md` now holds
  only that front's pipeline and routing. The contract also grew a second never-covered class
  beside code-coupled items: **irreversible cycle actions** (an OpenSpec archive, a backlog
  removal) always gate individually, and authorization **nests one level** so the cross-front
  run still costs exactly one OK. Twenty-one skills → **twenty-four** (fourteen `quenching-*` +
  ten `openspec-*`); the skill↔wrapper bijection holds at 24↔24.

## 0.17.0

**one interface across the three fronts.** The plugin acts on three surfaces —
  `/docs/`, `openspec/`, `.claude/` — but only two had an align sweep. A new **specs-front align**
  (quenching-native) gives the `openspec/` workspace the same
  install-and-force-conformance entry point: scaffold via `openspec init`, doctor/validate,
  canonical change + archive names, the `backlog/` inbox and its derived zone, `config.yaml`'s
  `context:` thinned into a pointer at `/docs/`, and removal of the CLI-generated
  `.claude/skills/openspec-*` + `.claude/commands/opsx/` shadow copies — with cycle actions
  (archive, triage, sync, boundary smells) **reported, never driven**. Its contract lives in
  the new `specs-align/references/conformance.md`; `quenching-components-align` now explicitly
  leaves the `openspec-*`/`opsx/` surface to it. New **`quenching-align-all`** (root `/align`)
  is the second conductor: the three aligns in dependency order (`/docs/` → `openspec/` →
  `.claude/`) on **one** confirmation, orthogonal to `quenching-knowledge-align-and-update` (which loops the
  `docs` front alone to a fixpoint). The cycle-authorization contract in
  `quenching-knowledge-align-and-update/references/cycle.md` is now the shared normative home for **both**
  conductors. Nineteen skills → **twenty-one** (twelve `quenching-*` + nine `openspec-*`), and
  the skill↔wrapper bijection is preserved.

## 0.16.0

**verb-first command surface, honest namespaces.** Renamed the command wrappers
  so each names its action, and split the `quenching-*` surface by the artifact it touches.
  `opsx:` keeps its namespace and every `openspec-*` skill name (upstream alignment); only the
  commands change: `apply`→`implement`, `update`→`revise`, `sync`→`sync-specs`,
  `backlog`→`backlog-add`. The seven quenching-native `docs:` skills rename in lockstep with
  their command: `insert`→`add`, `enrich`→`import`, `knowledge`→`learn`, `glossary`→`define`,
  `knowledge-scan`→`glossary-backfill` (the name no longer lies), `memory-to-docs`→`import-memory`,
  `cycle`→`converge`. `align`/`harness` stay. A new **`skill:` namespace** carries the two
  `.claude/`-automation skills out of `docs:` — `quenching-components-command-new` → `/quenching:components:command:new`,
  `quenching-components-align` → `/quenching:components:align` (skill names unchanged, namespace honest). Clean
  cut, no compatibility aliases; the 19-skill/19-wrapper bijection is preserved.

## 0.15.0

every skill is now `user-invocable: false` (hidden from the `/` menu) and paired
  with a thin **command wrapper** — `/opsx:*` for the eight `openspec-*` skills, `/quenching:knowledge:*` for
  the eleven `quenching-*` skills; Claude still auto-routes by `description`, the wrappers are the
  explicit user entry points. **Renamed** the backlog pair into the OpenSpec family — capture
  and triage, quenching-native — they own the `openspec/backlog/` inbox and carry
  no `metadata.generatedBy`. **Removed** `quenching-visualize` and the offline HTML diagram
  generator it drove (`assets/tools/okf-visualize.py` + the vendored `viewer/` — Cytoscape.js +
  marked). Twenty skills → **nineteen** (eleven `quenching-*` + eight `openspec-*`).

## 0.14.0

added the **automation family** — `quenching-components-command-new` (mint/edit ONE
  conformant skill: single-axis classification domain-bound × generic, flattened-path
  naming, mirrored command wrapper, writing doctrine, OKF tail) and
  `quenching-components-align` (migrate the existing `.claude/skills/` + `.claude/commands/`
  surface to the taxonomy in one plan → one OK). Two OKF artifacts now maintained in
  target repos: the rule `/docs/standards/automation/skills.md` (born
  `authority: background`) and the registry `/docs/project/automation.md`
  with a GENERATED zone only the pair writes. New `assets/templates/automation/` molds
  (skill, command wrapper, registry, standard). Fourteen quenching skills → **twenty** in
  all.

## 0.13.0

straightened the work pipeline to `openspec/backlog/` (task) →
  `openspec/changes/…` (design records the decision) → `/docs/standards/` (proven rule), with no
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

## 0.12.0

narrowed the OKF taxonomy from eleven homes to **nine** — retired the
  `communications/` and `presentations/` homes (and dropped the leftover empty
  `superpowers/` folder), removing the `communication`/`communication-template` types from
  the vocabulary (the `sidecar` type stays, now scoped to `reference/regulations/` extracts).
  Same release: added an optional **`complexity`** field to backlog tasks — a rough size in
  development hours, stamped only when stated (like `priority`/`tags`), surfaced as a column
  in `backlog/index.md`'s derived zone and proposable by `quenching-backlog-triage`.

## 0.11.0

absorbed the OpenSpec spec-driven cycle — six `openspec-*` skills (adapted
  from OpenSpec 1.6.0's generated skills, with OKF knowledge bridges) plus thin `/opsx`
  commands; the backlog lifecycle now seeds `/quenching:specs:develop` (the previous
  brainstorming-based flow is retired). Same release: renamed the backlog item `idea` →
  `task` (optional `priority`/`tags`; derived GENERATED zone in `backlog/index.md`;
  "Developed" → "Completed" ledger) and added `quenching-backlog` (capture) +
  `quenching-backlog-triage` (triage sweep) — ten quenching skills → twelve, eighteen in
  all.

## 0.9.0

retired the `guides/` home into `documentation/how-to/`; added the `documentation/`
  home (Diátaxis product docs) and a shippable mkdocs-material site setup (`assets/mkdocs/`).
