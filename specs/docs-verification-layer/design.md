# Design — Verification layer for the docs/ front

## Context

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

## Decisions

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
