---
type: concept
title: Glossary
description: The repo's single A–Z lookup of terms, acronyms, and domain vocabulary — one entry per term, each linking to its full concept doc when one exists.
resource: /docs/**
tags: [glossary, vocabulary, terminology]
timestamp: 2026-08-29
audience: both
authority: current
source: quenching skeleton
maintainer: <the team>
---

# Glossary

The repository's **single source of truth for what a term means here**. One entry per
term, in the same bullet syntax every `index.md` uses: `* [<Term>](<path>.md) — <one-sentence
definition>` when a full concept doc exists, or `* **<Term>** — <one-sentence definition>`
when it doesn't — the glossary is the *index* of vocabulary, not the long-form home.

**Resolving a term.** When a repo-specific word, acronym, or piece of jargon is unclear,
**search this file first** (Ctrl-F, or `grep -i '<term>' /docs/glossary.md`). A
matching entry gives the local meaning and, when linked, points to the doc that explains
it in full. No entry means the term is not yet defined — capture it (see *How to enrich*).

**This file is the ONE deliberate exception to "one concept per file."** A glossary is
inherently a multi-term aggregate — a flat bullet list, not a concept doc per term. It is
also the one exception to an `index.md`'s "only list what exists" rule: an **unlinked**
entry (a term with no concept doc yet) is a normal, permanent, valid state, not a defect.
Keep the list **alphabetically sorted by Term**, keep each definition to a single
sentence, and **link out** rather than explaining in full here.

## Core vocabulary

Fifteen terms to read first; each has its full entry under *Terms*.

- **front** — one local surface of a repository (knowledge, specs, design, ops, proof, toolchain, delivery) with its own probe, align and status.
- **align** — probe a front, plan one confirmed change, apply it, and loop until nothing changes.
- **fixpoint** — the state where one more align pass changes nothing.
- **probe** — the read-only opening run of an align, before any plan.
- **gate** — a stop for a human go/no-go, or a check that must pass, before an irreversible step.
- **authority** — how binding a doc is: `current` (proven) or `background` (agreed, unproven).
- **OKF** — the fixed-shape `/docs/` knowledge bundle this plugin ships and validates.
- **home** — a top-level folder of the bundle with one fixed purpose (`standards/`, `decisions/`, ...).
- **mold** — the fixed shape a kind of file is minted from.
- **harness** — `CLAUDE.md` / `AGENTS.md`: thin pointers into `/docs/`.
- **moment** — the point on a spec's timeline a section is read at: decision, build or close.
- **handoff** — a spec's `## Handoff` section, refreshed on four events so the next run resumes.
- **sediment** — text that outlived the mechanism it described.
- **spec backend** — where a repository's specs live (GitHub issues, Azure work items or git); the provider ID is the identity.
- **cq** — the plugin's single CLI, which every command body calls for its deterministic reads and writes.

## Terms

- [**Advisory finding**](standards/quality/bundle-verification.md) — a WARN the commands' verify
  gate does **not** treat as blocking, reported so a human can look and never so a run stops.
- [**Agent-choice catalogue**](standards/workflows/agent-choice-catalogues.md) — the shared shape
  `subjects`, `tagCatalog` and `workItemTypes` all follow in `.claude/quenching.json`: an abstract
  key mapping to a `description` an agent reads to PROPOSE a choice, which a human then CONFIRMS —
  never silently picked.
- [**Align**](standards/architecture/align-surface.md) — the command of a front that probes it,
  plans one confirmed change and loops until nothing changes.
- [**Always-on metadata**](standards/automation/skills.md) — the frontmatter `description` of every
  command, resident in every session's context before anything fires and therefore the only surface
  cost paid whether or not a command runs.
- [**Anchorless strategy**](standards/workflows/plan-git-record.md) — a merge strategy that produces
  **no merge commit** — `fast-forward` and `rebase` — so the **Merge record** has nothing to name
  and carries an explicit none instead of a fabricated pointer.
- [**Anomaly sidecar**](standards/quality/parse-honesty.md) — a *second* function reporting what a
  parse could not represent faithfully, placed beside the parser rather than folded into its return.
- [**Approved record**](standards/workflows/plan-lifecycle.md) — the `approved: {date, by}` entry
  saying a spec may be built and on whose authority: `human`, `low-gear` (the `low` level) or
  `orchestrator-forced` (`--autonomous` forcing `low`); an absent `by:` reads as `human`.
- [**Authority**](standards/index.md) — the frontmatter field saying how binding a doc is: `current`
  (proven) or `background` (agreed but unproven).
- [**Batching contract**](standards/automation/context-discipline.md) — a named block in a command
  body naming which of its consecutive tool calls are ONE call, so the batching rule is checkable
  against the body instead of re-judged every run.
- [**Blocked task marker**](standards/workflows/task-execution.md) — the `- [!] <id> <title> —
  blocked: <reason>` line implementation writes when attempts stop converging, replacing the earlier
  hidden attempt counter; `cq specs next` skips it and the reason stays legible to whoever unblocks
  it.
- [**Boundary reminder**](standards/architecture/plugin-layout.md) — a one-clause line that states
  the *edge* of a rule the citing place already owns, seen from the other side
  (`/quenching:knowledge:add` saying a heading is canonical English while the body prose follows
  whatever language the repo declared), as opposed to a restatement, which repeats a fact the citing
  place neither owns nor can change.
- [**Branch record**](standards/workflows/plan-git-record.md) — the `branch: {base, work}`
  frontmatter entry stamped by `/quenching:specs:execute` once the work ref is resolved, write-once
  — for **any** branch that is not the repo's base (the one it cut and the one a human already had
  open alike), and for work done in place, where `work` equals `base`.
- [**Bundle density**](standards/quality/bundle-verification.md) — the figures
  `/quenching:knowledge:status` prints alongside conformance (concept docs per home, empty homes
  shown as `0`, glossary size, which `standards/` subjects hold anything), carrying **no finding
  code** by design: coding them would make permanent noise of a repo that legitimately has no
  `mlops/`, omitting them would hide a bundle passing every check while knowing nothing.
- [**Bundle root**](standards/architecture/bundle-root.md) — the fixed `/docs/` location of a
  target's OKF bundle, and `/.specs/` for a files-backend specs workspace, a convention no
  configuration file names because an LLM executor runs command bodies literally and a root it must
  resolve from config is a root it can resolve wrong.
- **Cache trap** (`plugins/quenching/assets/references/components-command-new/capabilities.md`) —
  the standing cost of an inline `model:`/`effort:` pin in a command's frontmatter: the pin is part
  of the session's prompt-cache key, so changing it makes the next request recompute every input
  token.
- [**Canonical case list**](standards/code/frontmatter-parser.md) — the twelve frontmatter rows the
  one shared `common/frontmatter.py` parser must decide correctly, held in
  `tests/test_frontmatter.py`'s `CANONICAL_CASES` and run by the test suite.
- [**Canonical set**](standards/code/canonical-set-parsing.md) — an ordered contract declared in one
  place and read in many: `schema.json`'s `sections` array, its `phases[].entryGate`, the
  frontmatter record vocabulary.
- [**Commit record**](standards/workflows/plan-git-record.md) — the `subject: <line>` field on a
  completed task line, written mechanically by `cq specs task --check --subject`, that links the
  checkbox to the commit implementing it by naming that commit's **subject** and resolving with `git
  log --grep --fixed-strings`.
- **Compose** (`plugins/quenching/assets/references/specs-develop/questions.md`) — the monotonic
  half of a `/quenching:specs:develop` pass: it takes a spec from wherever its derived stage leaves
  it to a closed ten-section ready set, filling what is absent and sharpening what is thin, and it
  never overturns what a human settled.
- [**Context (components)**](standards/naming/command-surface.md) — one of the four sibling contexts
  under the `components` front — `command/`, `agent/`, `hook/`, `harness/` — each named for the
  artifact it mints, none a sub-type of another. A front-level verb sits at the front's own root
  (`/quenching:components:align`); an artifact-level verb sits under its context
  (`/quenching:components:command:new`).
- [**Context integral**](standards/automation/context-discipline.md) — a run's true cost, `tokens ×
  turns remaining`, not `tokens`: every turn re-sends the whole conversation, so a block loaded once
  is paid once for each turn that follows it.
- [**Cosmetic handle**](standards/architecture/spec-backend.md) — the kebab-case tail beside a
  spec's native ID in a git name: `plan/974-citacao-pendurada`.
- [**Coverage ratchet**](standards/architecture/proof-front.md) — a per-source-root floor that a
  verification gate may raise after a successful run but may never lower, preserving progress
  without forcing tests toward a fixed percentage target.
- [**cq**](/plugins/quenching/assets/references/align/tool-resolution.md) — the plugin's one entry
  point, `${CLAUDE_PLUGIN_ROOT}/assets/bin/cq`, replacing the self-contained scripts each pillar
  used to ship separately.
- [**Declared root / resolved root**](standards/architecture/spec-backend.md) — the pair the shared
  layer of `cq specs` must never confuse.
- [**Dependency map**](standards/automation/dependency-sweep.md) — the table the **Dependency
  sweep** returns, written by the orchestrator into `### Mapa de dependências` under the spec's own
  `## Design` and **dated**: it names every file the proposal's area touches or is touched by, and
  what breaks or goes orphaned if it changes.
- [**Dependency sweep**](standards/automation/dependency-sweep.md) — the read-only sub-agent read
  `/quenching:specs:develop` runs **before** the bank asks, so the right question has something to
  be answered with; it fires on selecting the *shape* bank, and on the first entry into the
  *adversarial* bank for a spec that was born `proposed` and never swept.
- [**Derived marker**](standards/architecture/proof-front.md) — a test-runner marker projected from
  the test's layer directory by collection, never a hand-applied second declaration of the layer.
- [**Derived stage**](standards/workflows/plan-lifecycle.md) — a spec's position in its life
  (`captured` → `proposed` → `designed` → `refined` → `ready` → `approved` → `executing`), COMPUTED
  from which headings are filled and which records frontmatter carries rather than declared in a
  field, so it regresses on its own when a section empties instead of going stale; resolution is
  last-match-wins, which is why `executing` sorts last.
- [**Disabled gate**](standards/architecture/ops-front.md) — a verification call commented out
  inside an entry point, treated as a finding rather than an off configuration because the disabled
  state has no explicit record.
- [**DTCG**](standards/architecture/design-front.md) — Design Tokens Community Group format used
  here as the 2025.10 source schema for `/.design/tokens.json`.
- [**Empty-response honesty**](standards/quality/empty-response-honesty.md) — the obligation to
  separate, in an empty payload coming back from a third-party process, the answer that **never
  arrived** from the one that legitimately **holds nothing**: an exit 2 refusal at the reading choke
  point where a measured structural discriminant exists (for `gh`.
- [**Entry point**](standards/architecture/ops-front.md) — an operation exposed by the ops router
  and named in its generated registry, whose implementation may live in a domain package rather than
  in the router itself.
- [**Epic**](standards/workflows/epics.md) — a spec with `workItemType: epic` whose `## Tasks` items
  reference member specs and whose item state is derived from the members, never ticked.
- **Fixpoint** — the state an align reaches when one more pass changes nothing; the loop ends there.
- [**Fixture library**](standards/architecture/proof-front.md) — the shared home for fixtures needed
  by more than one test module, keeping reusable setup from becoming duplicated module definitions.
- [**Front**](standards/architecture/front-mold.md) — one local surface of a repository (knowledge,
  specs, design, ops, proof, toolchain, delivery) that has its own probe, align and status command.
- [**Gate**](standards/automation/plan-gates.md) — a point where a command stops for a human
  go/no-go before an irreversible write, or a check that must pass before it proceeds.
- [**Generated listing**](standards/architecture/generated-listings.md) — a file, or a marked zone
  inside one, that a command rebuilds from what a directory holds.
- [**Golden input**](standards/architecture/proof-front.md) — a fixed, named input used by a data
  test to compare a transformation's value and schema against an expected result.
- [**Handler ladder**](standards/automation/hooks.md) — the ordering a hook's handler is chosen
  from, cheapest first: a deterministic `command` script (zero tokens on no-match), then a `prompt`
  handler (one cheap judgment per firing), then an `agent` handler — which on a per-tool-call event
  is an LLM toll booth on every operation (`sk-hook-llm-frequent`). Climbed only when the rung below
  cannot express the check.
- [**Handoff**](standards/workflows/task-execution.md) — the `## Handoff` section of a spec,
  refreshed on four events so the next run picks up where the last stopped.
- **Harness** — the agent-facing instruction files of a repository (`CLAUDE.md`, `AGENTS.md`) that
  point into `/docs/` instead of duplicating it.
- [**Impeccable**](../standards/architecture/design-front.md) — optional screen-craft consumer that
  reads generated `PRODUCT.md`, `DESIGN.md`, and `.impeccable/design.json` artifacts.
- [**Integration branch**](standards/git/branching.md) — under the develop/main flow, `develop`:
  where every `plan/<id>-<handle>` merges at conclude. It accumulates as many specs as it likes with
  nothing published; it only becomes public once the **Publication branch** takes its deliberate
  merge. See that entry for the other half of the pair — and for the note that this repository no
  longer runs the flow both halves describe.
- [**Language declaration**](standards/agents/communication.md) — the single line on a repo's
- [**Layer**](standards/architecture/proof-front.md) — a declared, disjoint slice of a test suite
  whose reach and wall-clock budget describe what kind of verification it provides.
- [**Measured surface**](standards/architecture/proof-front.md) — the declared set of source roots a
  verification gate actually measures, with an unmeasured shipped root reported as drift rather than
  hidden behind an honest percentage.
- [**Merge record**](standards/workflows/plan-git-record.md) — the `merge: {strategy, subject, pr}`
  frontmatter entry stamped by `/quenching:specs:conclude`, write-once, **on the work branch before
  the merge** — which is what makes the merge that command's last action and leaves nothing to be
  committed to the base after it.
- [**Mold**](standards/architecture/shared-mold-keys.md) — the fixed shape (frontmatter keys and
  sections) a kind of file is minted from; shared molds keep several fronts consistent.
- [**Moment**](standards/workflows/plan-artifacts.md) — the point on a spec's timeline a canonical
  section is read at, one value per section: `decision` (the human, weighing whether to build),
  `build` (the executor), `close` (`/quenching:specs:conclude`).
- [**Normalized script pattern**](standards/architecture/ops-front.md) — a stable vocabulary for
  routine project operations, derived from GitHub's pattern so contributors can use predictable
  names without learning each repository's internal layout.
- [**OKF**](explanation/okf-bundle.md) — Open Knowledge Format, the fixed-shape `/docs/` bundle
  (homes, `index.md` listings, typed concept docs) this plugin ships and validates.
- [**Ops front**](standards/architecture/ops-front.md) — the plugin front that defines the canonical
  operations surface a target repository can converge toward, including its router, entry-point
  contract, and lifecycle.
- [**Order independence**](standards/architecture/proof-front.md) — evidence that a suite remains
  correct when sampled collection orders change, exposing state or fixture leakage that a stable run
  can hide.
- [**Origin key** (`source_uri`)](standards/quality/bundle-verification.md) — the frontmatter key
  holding the **exact** URI or path of the source unit an imported doc was minted from, written by
  `/quenching:knowledge:import` and by no other command; a doc with no external origin simply does
  not have it.
- [**`[P]` marker**](standards/workflows/task-execution.md) — the opt-in flag set on a task when the
  tasks are written, declaring it may run concurrently with its group; honoured only when `cq specs
  parallel` proves the group's `files:` sets disjoint, and never inferred while building.
- [**Package**](standards/architecture/plugin-layout.md) — the Python package under
  `plugins/quenching/assets/bin/quenching/`, the directory that replaced the four self-contained
  scripts the plugin used to ship. Split into `common/`, `specs/`, `knowledge/` and `components/`,
  with no file too large to be read whole in one tool call; `cq` is the only entry point that
  exposes it.
- [**Parked follow-up**](standards/workflows/plan-lifecycle.md) — an out-of-scope finding a
  definition pass records as ONE line of `## Discoveries` on the spec it is developing, instead of
  minting a spec for it.
- [**Parse honesty**](standards/quality/parse-honesty.md) — the obligation that a verifier names its
  own parse failure rather than reporting it as a content gap.
- [**Payload**](standards/architecture/plugin-layout.md) — everything the plugin carries for use
  **inside a target repo**, as opposed to a fact about this repo.
- [**Phantom command**](standards/architecture/plugin-layout.md) — a non-entry-point file left under
  `commands/`, which registers as a real `/` entry that does nothing; it does not error, so the only
  thing that catches it is `sk-no-description`, and it is why shared procedure lives under
  `assets/`.
- [**Phase gate**](standards/workflows/plan-artifacts.md) — the set of sections a spec must have
  filled before a heading counts as required, which is what makes the explicit-none rule
  stage-scoped rather than absolute.
- [**Pillar**](standards/naming/command-surface.md) — one of the three axes `cq` routes: `specs`,
  `knowledge` and `components`, passed as the first argument (`cq <pilar> <subcomando>…`). It is the
  single vocabulary of the fronts' axis, replacing the names `docs` / `specs` / `skill` that
  competed before the merge into one package.
- [**Plugin config**](standards/workflows/plugin-configuration.md) — `.claude/quenching.json`, the
  single file a target repository uses to declare anything to this plugin: `backend`,
  `worktreeSetup`, `azureStates`, `azurePlacement`, `azureColumns`, `subjects`, `tagCatalog`,
  `workItemTypes` and `shared.gitConventions` — the last of which carries the `git` pillar's
  per-artifact writing directives and outranks the target's own `docs/standards/git/**` for every
  artifact it names.
- [**PR record**](standards/workflows/plan-git-record.md) — the `pr: {number, url, date}`
  frontmatter entry stamped by `git:pr:create` the moment the provider returns the PR, on the PR
  route only, and **write-many** where the other git records are write-once: a PR may be closed and
  reopened, or force-pushed to a fresh number, and each is a new fact rather than a falsification of
  the old one.
- [**Preview-first**](standards/architecture/ops-front.md) — the rule that an entry point which
  writes outside the repository must show the intended operation before an explicit flag arms the
  write.
- [**Priced**](standards/quality/finding-remedy-applicability.md) — the boolean field
  `sk-unscoped-bash` carries in the JSON: the command body opens a line with the literal marker
  `**Why \`Bash\` is unrestricted here.**`, outside a fence, or it does not.
- [**Probe**](standards/architecture/align-surface.md) — the opening run of a front's own verifier
  (`cq knowledge validate`, `cq specs doctor`, `cq components doctor`) whose exit code decides
  whether an align inventories anything at all, making a no-op align cost a couple of tool calls;
  the same programs run again as the closing verification.
- [**Projection / storage**](standards/architecture/spec-backend.md) — the pair that decides whether
  a backend may map a canonical field onto a native construct.
- [**Promote**](standards/workflows/plan-lifecycle.md) — the gated `git mv` that moves a spec from
  `plans/` to `archive/` without renaming it, stamping `outcome: done | abandoned`.
- [**Proof front**](standards/architecture/proof-front.md) — the target repository's verification
  surface: declared test layers, fixture library, measured source roots, ratchets, and the CI gate
  that runs them.
- [**Prose fan-out**](standards/quality/computed-fact-prose-fanout.md) — the set of prose sites a
  fact a tool computes ages the moment it changes — a schema key, a surface's command count — and
  which every checker in this repo is blind to by construction: the selftest proves the key *works*.
- [**Provider ID**](standards/architecture/spec-backend.md) — the tracker's own identifier for a
  spec — a GitHub issue number, an Azure Boards work-item ID — and **the spec's whole identity**.
- [**Publication branch**](standards/git/branching.md) — under the develop/main flow, `main`: the
  one branch that takes the deliberate `develop → main` merge, the one moment the version lockstep
  moves and a tag is created.
- **Published skeleton** — the OKF bundle the plugin SHIPS, at
  `plugins/quenching/assets/knowledge/`: index files plus a single leaf standard
  (`standards/agents/communication.md`).
- **Refine** (`plugins/quenching/assets/references/specs-develop/questions.md`) — the non-monotonic
  half of a `/quenching:specs:develop` pass, and the only operation licensed to overturn what the
  spec already says, the `## Proposal` included.
- [**Refinement record**](standards/workflows/plan-artifacts.md) — the `refined: {mode, date}` entry
  a spec's **frontmatter** gains once it has been interrogated, whose absence raises the non-gating
  `sp-unrefined` warning.
- [**Remedy**](standards/quality/finding-remedy-applicability.md) — the `remedy` field every
  verifier finding carries, and the contract it takes on: naming an action the surface that emitted
  the finding actually offers. A remedy that describes the desired state, or an action the same CLI
  refuses, spends the trust of the whole output — not just that of the item carrying it.
- [**Report mold**](standards/architecture/report-mold.md) — the single section that owns the shape
  **every** command of a front prints its report in, cited by each body, which declares only its own
  delta.
- [**Reserved tag prefix**](standards/architecture/spec-backend.md) — `spec:`, the half of a
  tracker's native tag surface (`github` issue labels, `azure-boards` `System.Tags`) that belongs to
  the TOOL rather than to the document, and the rule that lets **storage** and **rendering** share
  one field without either reading the other's writes as the spec's own content.
- [**Resource glob set**](standards/quality/bundle-verification.md) — the format of an OKF doc's
  `resource:`, a plugin convention rather than an OKF rule: a **comma-separated** list of
  repo-root-relative paths and globs using `*`/`**` **only**, matched **segment-wise everywhere**
  including the `:(glob)` pathspec handed to `git log`, since plain `fnmatch` and git's default
  wildmatch both let `*` cross a `/` and would silently widen every shallow scope.
- [**Retired (reserved artifact)**](standards/architecture/retiring-a-reserved-artifact.md) — a
  reserved filename nothing produces or checks any more, but which **keeps** its slot in the
  validator's `RESERVED` set and its skip in the `PreToolUse` hard block.
- [**Retiring a standard**](standards/workflows/retiring-a-standard.md) — removing a bundle standard
  rather than deprecating it — `git rm` is the verb, the inheriting doc carries the `retired with
  <doc> (<spec>, <data>)` stamp, the citation sweep is human with the branch review as its net, and
  the GENERATED listing row goes in the same commit; distinct from the reserved artifact, which
  KEEPS its slot when retired.
- [**Routed command**](standards/automation/skills.md) — a command something reaches **without a
  human typing its name**, whether by a spoken trigger or by another command's body naming it; its
  `description` stays resident in every session's context and is charged against the **Always-on
  ceiling**.
- [**Router**](standards/architecture/ops-front.md) — the single canonical declaration that maps
  normalized operation names to their implementations, while convenience wrappers delegate rather
  than duplicate domain logic.
- [**Rules/rationale markers**](standards/automation/context-discipline.md) — the pair of HTML
  comments, `<!-- rules -->` and `<!-- rationale -->`, that split a normative section's binding half
  from the measurement and history behind it, so `cq components read --rules-only` can return the
  first without the second.
- [**Scope ladder**](standards/automation/hooks.md) — the four rungs a hook may be installed at,
  narrowest first: a command's own frontmatter `hooks:` block (fires only while that command runs),
  a `settings.json` hook with an event + `matcher`, a gated wide event, and an unmatched
  session-wide hook — the top rung, and a finding (`sk-hook-unmatched`) unless the reason nothing
  narrower suffices is stated where it is wired.
- [**Section boundary**](standards/automation/context-discipline.md) — the moment a `## N.`
  section's last task commits with none of its tasks blocked: each task commit stays intact and the
  build **offers** to stop — a clean point, because the resumption trail (`## Handoff`, `git log`,
  the recorded commit subjects) is already maintained for other reasons, which is what makes the cut
  nearly free.
- [**Section reader**](standards/automation/context-discipline.md) — the verb that resolves the `§X`
  address the prose was already writing: `cq components read <path> --sections "§A"` over free
  markdown, `cq specs section <id> "A,B"` over a spec's fourteen canonical headings.
- **Sediment** — text that outlived the mechanism it described, so it costs context and fires for
  nobody; the thing `tighten` removes.
- [**Self-matching guard**](standards/quality/self-matching-guards.md) — a structural checker whose
  own finding text names the construct it forbids, so a substring scan reports the checker as the
  violation.
- [**Shared mold**](standards/architecture/shared-mold-keys.md) — a frontmatter key block owned once
  and cited by several commands, so each mints a doc from the same stamp instead of restating it
  (`docs-add/homes.md` §The frontmatter stamp, cited by four).
- [**Spec backend**](standards/architecture/spec-backend.md) — where a repository's specs actually
  live: markdown files on a dedicated branch, GitHub issues, or Azure Boards work items, declared by
  `backend` in [the plugin config](standards/workflows/plugin-configuration.md).
- [**Typed-only command**](standards/automation/skills.md) — a command carrying
  `disable-model-invocation: true`, reached only by a human typing it; its `description` leaves
  every session's context.
- [**Verification policy**](standards/workflows/task-execution.md) — the per-spec declaration
  (`per-task`, `per-section`, `end-of-plan`) written at creation that decides when a task's
  `verify:` command runs, so execution never guesses and never asks mid-task.
- [**Version lockstep**](standards/ci-cd/versioning-release.md) — the four version strings a release
  must bump together, split into two halves read by two independent consumers: the `plugin.json`
  `version` + `VERSION` pair Claude Code compares to decide an upgrade fires, and the one shared
  `VERSION` constant every pillar's `--version` reads.
- [**Withdrawn contract residue**](standards/quality/withdrawn-contract-residue.md) — the prose
  still asserting a contract a change **removed**, and the sibling of **Prose fan-out**
  ([computed-fact-prose-fanout.md](standards/quality/computed-fact-prose-fanout.md)) for the case
  where nothing computes the fact: with no value to spell out, each site wrote the rule in its own
  words, so no grep finds the set.
- [**Worktree setup**](standards/workflows/worktree-setup.md) — the single key `worktreeSetup` in
  `.claude/quenching.json`, holding a command `/quenching:specs:execute` runs once inside a newly
  created worktree so a repo with installed dependencies gets a usable tree rather than one that
  breaks at the first `verify:`.
- [**Zensical**](external/tools/zensical-measured-behaviour.md) — the static site generator the
  Material for MkDocs team now ships, and the one this plugin's `documentation/` site layer stamps
  and verifies since spec 1003: it reads a `mkdocs.yml` natively but runs **no MkDocs plugin at
  all**, so the nav moved from `.pages` sidecars into an explicit `nav` list in `zensical.toml`.

## How to enrich

Add a term whenever a repo-specific word, acronym, or piece of jargon surfaces that a
newcomer would not know. Three ways in:

- **Automatically, as a tail of a capture.** The `quenching` knowledge skills
  (`quenching:knowledge:learn`, `quenching:knowledge:add`, `quenching:knowledge:import-memory`) each check, at
  the end of a capture, whether the new concept introduced a term that belongs here, and
  add or update the entry — linking it to the concept doc just written.
- **On demand, one term at a time.** Run `quenching:knowledge:define` to add or refine a single
  entry (inserted in alphabetical position, MERGE — never clobbering a filled definition).
- **In bulk, across the whole bundle.** Run `quenching:knowledge:glossary-backfill` to sweep every doc
  already in `/docs/` for repo-specific terms that were never fed into the glossary and
  backfill them in one pass.

Keep entries honest: define the term as **this repo** uses it, not the dictionary sense,
and let the linked doc carry the depth.
