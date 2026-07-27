---
slug: docs-verification-layer
title: Verification layer for the docs/ front
verification: per-section
---

# Verification layer for the docs/ front

## Problem

`okf-validate.py` returns exit 0 on this repository's own bundle — a bundle holding 33 markdown
files, of which 21 are `index.md`, 2 are `log.md` and 1 is `QUENCHING.md`. Five are concept docs,
and `knowledge/glossary.md` still carries the shipped seed placeholder as its only entry, in a repo
that coined *OKF*, *front*, *home*, *mold*, *harness*, *blast radius*, *fixpoint*,
*cycle-authorization* and *GENERATED zone*. Structural conformance is currently compatible with a
knowledge base that knows nothing, and nothing in the front reports that.

The gap is not doctrine. The glossary tail step is specified in six places — `homes.md`
§Enriching the glossary, `quenching-docs-add`, `quenching-docs-learn`,
`quenching-docs-import-memory`, `quenching-docs-define`, and `quenching-specs-plan-archive`'s
`distill.md` — and produced zero entries across two real distillation runs. An invariant written
six times and executed zero times is the argument for a deterministic rail rather than a seventh
restatement. The same holds for `resource:`: four skills forbid inventing one, and the validator
never checks that it points at anything. The repo's own seed, `knowledge/glossary.md`, ships
`resource: docs/**` — self-pointing, which the doctrine explicitly disallows.

The `specs/` front already has its read-only counterpart in `quenching-specs-status`, described as
"the front's only read-only view … doubles as an honest dry run before the OK". The `docs/` front
has none, so the only way to learn what `/docs:align` would do is to invoke the invasive skill and
read the plan from inside it.

## Proposal

- A new read-only skill `quenching-docs-status` and its mirrored wrapper `/docs:status` report the
  whole `docs/` front without writing anything, splitting findings into what `/docs:align` fixes,
  what `/docs:align-and-update` drives, and what neither closes.
- That report carries **bundle density** alongside conformance: homes scaffolded vs. empty, concept
  docs per home, glossary term count — so an empty bundle stops reading as a healthy one.
- `okf-validate.py` gains three checks: `resource-unresolved` (a path- or glob-shaped `resource`
  matching nothing on disk), `resource-self` (a `resource` whose scope contains the doc itself),
  and `glossary-broken-link` (the `index-broken-link` rule applied to `knowledge/glossary.md`).
- `okf-validate.py` gains a `stale-doc` WARN: the doc's `timestamp` is older than the last commit
  touching the paths its `resource` globs name.
- The shipped seed `assets/docs/knowledge/glossary.md` stops violating the anti-self-pointing rule
  it is meant to demonstrate.
- The skill/wrapper bijection recorded in `docs/standards/naming/command-surface.md` moves from
  27 ↔ 27 to its true current count plus this plan's addition.

## Out of Scope

- **The `authority: superseded` enum, `superseded_by:`, and a `/docs:deprecate` skill.** The
  `**Deprecation**` log prefix is reserved in four places and never written by any `docs-*` skill,
  and the enum has no state for a retired standard. Real, but it changes a contract that touches
  every mold, the validator, `taxonomy.md` and all three `QUENCHING.md` manuals — a different blast
  radius from this plan, which only observes. It is Plan B.
- **Provenance and idempotent re-ingestion for `quenching-docs-import`** (`source_uri` + content
  hash so a changed source is detectable). Deferred because the import path shows no evidence of
  having run on this repo; optimizing an unexercised path is speculation.
- **Inverting the harness default toward `AGENTS.md`** now that it is a Linux Foundation open spec
  with 60k+ adopting repos, while `assets/templates/harness/` ships only `claude-root.md` and
  `claude-subfolder.md`. Well-founded but independent — it blocks nothing here. Routed to
  `specs/backlog/`.
- **Cross-document contradiction detection between two `standards/` docs.** Needs a semantic pass,
  not a deterministic check, so it does not belong in a validator-centred plan.
- **A retrieval/query skill over the bundle.** Grep over a bundle with a greppable `type` already
  answers it; a second read path would age without earning its keep.

## Impact

### Standards this plan will write into docs/standards/

- `docs/standards/quality/bundle-verification.md` — what the `docs/` front machine-checks versus
  what it leaves to a skill's prose self-check, and the rule that an invariant restated in more
  than two skills is owed a deterministic check rather than a third restatement

### Standards at `authority: background` this plan may resolve

- none — no `authority: background` standard currently governs the `docs/` front's verification.

### Product code this plan expects to touch

- `plugins/quenching/assets/hooks/okf-validate.py` — the four new checks, their codes, and
  the `--version` bump
- `plugins/quenching/assets/docs/knowledge/glossary.md` — the self-pointing `resource:` in
  the shipped seed
- `plugins/quenching/skills/quenching-docs-align/references/conformance.md` — the finding
  codes are owned here and cited by every skill's self-check
- `plugins/quenching/skills/quenching-docs-status/` and
  `plugins/quenching/commands/docs/status.md` — the new skill and its mirrored wrapper
- `plugins/quenching/assets/docs/QUENCHING.md`, `assets/specs/QUENCHING.md`,
  `assets/claude/QUENCHING.md` — all three enumerate the command surface
- `plugins/quenching/VERSION`, `.claude-plugin/plugin.json`,
  `.claude-plugin/marketplace.json`, `assets/bin/specs.py` — the release lockstep quartet
- `CLAUDE.md`, `plugins/quenching/README.md` — the skill count and the 27 ↔ 27 bijection

## Validation

- `python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/docs`
  → `0 error(s), 0 warning(s)`, including the corrected glossary seed.
- `python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/specs/backlog --listing-root`
  → `0 error(s), 0 warning(s)` (the new checks must not regress the backlog listing root).
- The four new finding codes each fire on a purpose-built fixture and stay silent on the shipped
  skeleton: a doc with `resource:` naming a nonexistent path, a doc whose `resource` glob contains
  itself, a `glossary.md` linking a deleted doc, and a doc whose `timestamp` predates the last
  commit touching its `resource` globs.
- `--json` output remains parseable and every new finding carries a code, a severity and a path;
  no existing code changes severity.
- Version lockstep holds: `cat VERSION`, `specs.py --version` and `okf-validate.py --version` agree.
- `/docs:status` run against this repository writes nothing — verified by a clean `git status` after
  the run — and reports the five concept docs, the empty homes, and the one-entry glossary.
- Every wrapper resolves to a skill and every skill to a wrapper (the bijection), and the three
  `QUENCHING.md` manuals enumerate the new command.

## Design

### Context

Binding contracts this design must not contradict:

- `docs/standards/naming/command-surface.md` — every skill is `quenching-<front>-<object>-<verb>`,
  mirrored one-to-one by a wrapper at `commands/<front>/<verb>.md`. A skill that reads the bundle
  belongs under `/docs:`. The bijection is stated there as 27 ↔ 27 and is now stale.
- `docs/standards/automation/skills.md` — single-axis classification; `quenching-docs-status` is
  **domain-bound** (it serves exactly one front), so it takes the flattened-path name and a
  mirrored wrapper. Writing doctrine applies: trigger phrases in the description's second sentence,
  body well under the size cap, shared procedure cited from its owning `references/`.
- `quenching-docs-align/references/conformance.md` is the **single owner** of finding codes; every
  skill's self-check cites it. New codes are defined there and nowhere else.
- `CLAUDE.md` — never add `context: fork` to these skills; keep each `description` under the
  1,536-character cap; push shared procedure into the owning `references/*.md`.
- `okf-validate.py` is stdlib-only and self-contained, and runs in three modes: CLI, `PostToolUse`
  (single file), and `Stop` (whole tree, dirty-gated, `deadlineMs: 4000`).

Two shapes already in the repo constrain the solution more than anything else:

**The existing WARN-but-must-fix precedent.** `dir-no-index`, `index-broken-link` and
`index-orphan` are WARN — OKF says a consumer MUST tolerate broken links — yet the skills treat
them as blocking in their own verify gate. That is the slot the new integrity checks belong in.

**The existing resource exemption.** `TYPES_WITHOUT_RESOURCE = ("task",)` already encodes "this
kind of doc has nothing to point at, so the WARN would be permanent noise." The glossary needs the
same mechanism for a different reason, not a new one.

### Decisions

**The anchor is the `resource` glob set plus `timestamp`. Not `file:line`.** Four skills instruct
deriving `resource` from `file:line` anchors; all five `resource` values in this repo's own bundle
are globs or comma-separated glob lists, and none is a `file:line`. Practice has already answered
the question the doctrine got wrong: `file:line` says *where the rule is written* and silently
rots on any insertion above the line, while a glob says *what this doc governs* — which is exactly
the input a staleness check needs. Staleness is therefore
`git log -1 --format=%cI -- <globs>` compared against the doc's `timestamp`. This adds no new
state, no manifest, and no second source of truth. The doctrine text is corrected to describe the
glob-set practice rather than the practice being bent to the doctrine.

**Staleness is CLI-only and never runs in the hook path.** One `git log` subprocess per concept
doc is fine for an on-demand sweep and unacceptable under a 4-second `Stop` deadline on a bundle
with hundreds of docs. This follows the structural-integrity checks, which are already documented
as "whole-tree — CLI + `Stop` only"; staleness narrows that further to CLI. A repo that is not a
git checkout skips the check silently rather than reporting a finding it cannot compute.

**`stale-doc` is advisory; the three integrity checks are WARN-but-must-fix.**
`resource-unresolved`, `resource-self` and `glossary-broken-link` describe a doc that is provably
lying about itself, so they join the structural-integrity set the skills treat as blocking in
their verify gate. `stale-doc` describes a doc that *may* still be perfectly correct — code moved
under a rule that did not change — so it is reported and never blocks. Conflating the two would
make the must-fix set unusable, since every mature bundle carries some legitimately stale-looking
doc.

**No new code is an ERROR.** ERROR fails conformance and every target repo would begin failing on
its next run for docs that were conformant when written. The plugin's "convergence over
accommodation" governs what a sweep *fixes*, not what a validator *escalates*; a check introduced
at ERROR would break the exit-code contract in repos the plan never touched.

**The glossary is exempt from `resource-self` and `stale-doc`, and keeps its `resource`.** The
honest scope of `knowledge/glossary.md` really is the whole bundle, so `resource: docs/**` is not
a fabrication — the problem is only that self-containment makes the doc eternally fresh, which is
precisely what makes the anti-self-pointing rule load-bearing rather than cosmetic. Rather than
inventing a false narrower scope, the seed is exempted through the mechanism that already exists
for `task`, generalized from "types without resource" to "docs whose resource is a bundle-level
aggregate". This keeps one mechanism instead of two.

**`quenching-docs-status` is a new skill, not a flag on `quenching-docs-align`.** The align skill's
`allowed-tools` includes `Write` and `Edit`; a read-only mode inside it would be a promise the tool
grants cannot keep. `quenching-specs-status` establishes the pattern — no `Write`/`Edit` in
`allowed-tools`, owns no contract, cites all three — and this mirrors it exactly.

**The status report reuses the assessment already specified inside the conductor.** Step 2 of
`quenching-docs-align-and-update/SKILL.md` already defines the read-only opportunity survey and
`references/cycle.md` already owns the opportunity → skill routing table. `quenching-docs-status`
cites both rather than re-deriving them, and the conductor keeps its own copy of the invocation.
One authority per concern is the rule that made the rest of this plugin coherent.

**Density is reported, never coded as a finding.** See `## Open Decisions`.

## Alternatives Considered

- **A `docfresh`-style SHA manifest pinning each doc to a tree-hash of its globs.** More correct
  than `timestamp`, because it does not depend on an LLM writing an honest date at capture time.
  Rejected for now on cost: it introduces a generated artifact that must be kept in lockstep,
  regenerated on every doc write, and reconciled after a rebase — a whole new drift surface, added
  to fix a failure mode that has not yet been observed. `timestamp` is a WARN, so the cost of it
  being wrong is a noisy line, not a broken build. If field use shows `timestamp` is routinely
  wrong, the manifest is the escalation and this design does not foreclose it.
- **`file:line` anchors, as four skills currently instruct.** Rejected on evidence: zero of five
  real `resource` values use them, and the format cannot survive ordinary editing without a
  rewrite step nobody has built.
- **Extending `quenching-docs-align` with a `--dry-run`-style read-only mode instead of a new
  skill.** Rejected — it would break the front's one-skill-one-concern shape and leave the read
  path gated behind a skill that holds write tools.
- **Making the whole plan a validator change with no new skill.** Rejected: the codes would fire
  but the density signal — empty homes, an empty glossary — has no finding code by design, so it
  would have no reporting surface and the original problem would remain invisible.
- **Shipping the deprecation lifecycle in the same plan.** Rejected on blast radius: it changes the
  `authority` enum, which touches every mold, the taxonomy, the validator and all three operator
  manuals. This plan only observes; mixing an observation layer with a contract change would make
  both harder to review and to revert.

## Open Decisions

- **How an installed-but-empty home is reported.** Reporting every empty home as a finding is
  permanent noise in a repo that legitimately has no `mlops/`; not reporting it loses the signal
  that motivated the plan. The plan ships the middle position — density appears in the
  `/docs:status` report as a **table with no finding code**, so it informs without accumulating as
  a defect to chase. **How the rest gets decided:** the sharper form is "installed, empty, *and*
  the repo clearly contains code that subject governs", which needs evidence from a real target
  repo to specify without guessing. It is decided by running `/docs:status` against two or three
  adopting repos and seeing whether the empty-home rows read as signal or as wallpaper; the
  outcome routes to a follow-up plan, not to this one. Task 5.3 records the observation.

  **Observation from task 4.5 (n=1, this repository).** The zeros read as **signal**, decisively:
  four of six homes and seven of ten `standards/` subjects are installed and empty, against five
  concept docs — while the validator reports nothing a sweep would fix. The density table is the
  only part of the report carrying information, which is exactly the failure the plan was written
  against. Two caveats keep this from settling the decision. First, this repo is the pathological
  case — it *authored* the mold, so it has every home the mold installs and content for almost
  none; an adopting repo scaffolds only its applicable homes and would show fewer, more meaningful
  zeros. Second, the sharper form ("empty **and** the repo clearly contains code that subject
  governs") is untested here, because a plugin repo has no `mlops/` or `data-modeling/` code to
  contradict the emptiness. The decision still needs two or three adopting repos; this run
  confirms only that the figures are worth printing, not how they should be scored.
- **Whether `resource-unresolved` should understand glob syntax beyond `*`/`**`.** The five
  observed values use only those two, so the plan implements only those and reports anything it
  cannot parse as unresolved-unknown rather than as a violation. Decided by the first target repo
  that uses a brace or character-class glob; until then, guessing at syntax nobody writes is
  speculation.

## Risks

- **Git pathspec semantics differ from shell globbing.** `git log -- 'plugins/**/SKILL.md'` does
  not mean what it appears to mean without `:(glob)` pathspec magic. Mitigation: task 3.2 pins the
  behavior with a fixture that would fail under naive pathspec passing, and the implementation
  uses explicit `:(glob)` prefixes.
- **A comma-separated `resource` is a plugin convention, not a spec.** Three of five real values
  are comma-separated lists; nothing documents that as the format. Mitigation: the standard written
  in task 5.1 states it, so the parser and the doctrine agree from the start.
- **New WARNs make previously quiet target repos noisy on upgrade.** Mitigation: none of the four
  is an ERROR, `stale-doc` never runs in the hook path, and the release notes name the new codes so
  an operator can recognize them as new rather than as regressions.
- **`/docs:status` drifting from the conductor's assessment it cites.** Two read paths that must
  agree is exactly the duplication this plugin avoids elsewhere. Mitigation: the status skill cites
  `cycle.md`'s routing table as its owner and restates none of it; task 4.3 verifies the finding
  vocabulary matches.
- **The plan enlarges the surface it is measuring.** Adding a skill means editing three
  `QUENCHING.md` manuals, the README count, the CLAUDE.md count and the bijection standard —
  lockstep items that are easy to half-apply. Mitigation: section 6 makes each one an explicit task
  rather than a remembered chore.

## Tasks

### 1. Fixtures first

- [x] 1.1 Create a throwaway fixture bundle under the scratchpad with one doc per new code: a
      `resource:` naming a nonexistent path, a `resource` glob containing the doc itself, a
      `glossary.md` linking a deleted doc, and a doc whose `timestamp` predates the last commit
      touching its `resource` globs
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py <fixture> --json
- [x] 1.2 Record the current baseline so regressions are visible: run the validator over
      `assets/docs` and over `assets/specs/backlog --listing-root` and capture both outputs
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/docs

### 2. Resource integrity checks

- [x] 2.1 Add a `resource` parser: split on commas, trim, classify each entry as path-shaped,
      glob-shaped (`*`/`**` only), URI-shaped, or unparseable
      files: plugins/quenching/assets/hooks/okf-validate.py
- [x] 2.2 Add `resource-unresolved` (WARN) — a path- or glob-shaped entry matching nothing on disk;
      an entry the parser cannot classify is reported as unknown, never as a violation
      files: plugins/quenching/assets/hooks/okf-validate.py
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py <fixture> --json
- [x] 2.3 Add `resource-self` (WARN) — the doc's own path falls inside its declared resource scope
      files: plugins/quenching/assets/hooks/okf-validate.py
- [x] 2.4 Generalize `TYPES_WITHOUT_RESOURCE` into a bundle-aggregate exemption covering
      `knowledge/glossary.md`, so it keeps `resource: docs/**` without firing `resource-self`
      files: plugins/quenching/assets/hooks/okf-validate.py
      pattern: plugins/quenching/assets/hooks/okf-validate.py

### 3. Glossary links and staleness

- [x] 3.1 Add `glossary-broken-link` (WARN) — apply the existing `index-broken-link` link-resolution
      rule to `knowledge/glossary.md`, reusing the same helper rather than a second implementation
      files: plugins/quenching/assets/hooks/okf-validate.py
- [x] 3.2 Add `stale-doc` (WARN, advisory) — `git log -1 --format=%cI` over the resource globs using
      explicit `:(glob)` pathspec magic, compared against `timestamp`; pin the pathspec behavior
      with a fixture that would fail under naive passing
      files: plugins/quenching/assets/hooks/okf-validate.py
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py <fixture> --json
- [x] 3.3 Gate `stale-doc` to CLI only — never `PostToolUse`, never `Stop` — and skip it silently
      when the tree is not a git checkout
      files: plugins/quenching/assets/hooks/okf-validate.py
- [x] 3.4 Fix the shipped seed's self-pointing `resource` per the 2.4 exemption, and confirm the
      skeleton still validates clean
      files: plugins/quenching/assets/docs/knowledge/glossary.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/docs
- [x] 3.5 Document the four new codes in the conformance contract — their severity, which are
      must-fix in a skill's verify gate, and that `stale-doc` is advisory and CLI-only
      files: plugins/quenching/skills/quenching-docs-align/references/conformance.md

### 4. The status skill

- [x] 4.1 Write `quenching-docs-status/SKILL.md` — read-only (`allowed-tools` with no `Write`/`Edit`),
      description under the 1,536-char cap with trigger phrases in the second sentence, no
      `context: fork`, owning no contract and citing `conformance.md` and `cycle.md`
      files: plugins/quenching/skills/quenching-docs-status/SKILL.md
      pattern: plugins/quenching/skills/quenching-specs-status/SKILL.md
- [x] 4.2 Add the report's three sections — what `/docs:align` fixes, what `/docs:align-and-update`
      drives, what neither closes — routed by `cycle.md`'s opportunity table, cited not restated
      files: plugins/quenching/skills/quenching-docs-status/SKILL.md
- [x] 4.3 Add the density table (homes scaffolded vs empty, concept docs per home, glossary term
      count) as reported figures carrying no finding code, and verify the skill's finding
      vocabulary matches `conformance.md` exactly
      files: plugins/quenching/skills/quenching-docs-status/SKILL.md
- [x] 4.4 Write the mirrored wrapper `/docs:status`
      files: plugins/quenching/commands/docs/status.md
      pattern: plugins/quenching/commands/specs/status.md
- [x] 4.5 Run `/docs:status` against this repository and confirm it writes nothing and reports the
      five concept docs, the empty homes and the one-entry glossary
      verify: git status --porcelain

### 5. The standard and the deferred work

- [x] 5.1 Write `docs/standards/quality/bundle-verification.md` (`authority: current` once the
      checks land) — what the front machine-checks versus what it leaves to a skill's prose
      self-check, the rule that an invariant restated in more than two skills is owed a
      deterministic check, and the comma-separated `resource` glob-set format
      files: docs/standards/quality/bundle-verification.md
- [x] 5.2 Correct the `file:line` instruction in the four skills that state it, so the doctrine
      describes the glob-set practice it actually produced
      files: plugins/quenching/skills/quenching-docs-add/SKILL.md, plugins/quenching/skills/quenching-docs-add/references/homes.md, plugins/quenching/skills/quenching-docs-align/SKILL.md, plugins/quenching/skills/quenching-docs-learn/SKILL.md
- [x] 5.3 Record the empty-home observation from 4.5 in `design.md` §Open Decisions, and park the
      two deferred items — import provenance and the AGENTS.md harness inversion — via
      `/specs:backlog:add`

### 6. Surface lockstep

- [x] 6.1 Enumerate `/docs:status` in all three operator manuals
      files: plugins/quenching/assets/docs/QUENCHING.md, plugins/quenching/assets/specs/QUENCHING.md, plugins/quenching/assets/claude/QUENCHING.md
- [x] 6.2 Update the skill count and the stale 27 ↔ 27 bijection to the true current count
      files: CLAUDE.md, plugins/quenching/README.md, docs/standards/naming/command-surface.md
- [x] 6.3 Bump the release quartet in lockstep
      files: plugins/quenching/VERSION, plugins/quenching/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/hooks/okf-validate.py

### 7. Verification

- [x] 7.1 Both skeleton validations clean
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/docs
- [x] 7.2 Backlog listing root still clean — the new checks must not regress it
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/specs/backlog --listing-root
- [x] 7.3 Each new code fires on its fixture and stays silent on the skeleton; no existing code
      changed severity; `--json` stays parseable with a code, severity and path per finding
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py <fixture> --json
- [x] 7.4 Version lockstep and the wrapper bijection both hold
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py --version
