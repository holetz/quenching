---
slug: verify-allowed-tools-enforcement
title: Verify Allowed Tools Enforcement
verification: per-section
priority: {level: 3, criticality: critical, date: 2026-07-28}
refined: {mode: gate, date: 2026-07-28}
approved: {date: 2026-07-28}
branch: {base: main, work: plan/verify-allowed-tools-enforcement}
---

# Verify Allowed Tools Enforcement

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a thirteen-heading skeleton. Every other heading below is created on
     first write by `specs.py section <slug> "<Heading>" --write`, which inserts it in the
     canonical position with the guidance comment kept here.

     THE PHASE-SCOPED EXPLICIT-NONE RULE. A heading is required — and required to carry
     `- none — <reason>` when it has nothing in it — only once ITS OWN phase gate is reached:

       new (capture)        `## Problem`
       promote -> ready/    the nine definition sections (`## Problem` .. `## Risks`)
                            AND `## Tasks`
       ready/  (warn only)  `## Handoff` non-empty
       promote -> archive/  `## Outcome`

     Before its gate, a heading's absence is NOT an omission — it is a not-yet. After its
     gate, three rules decide whether a section counts as filled:

       1. `- none — <reason>` counts as filled. An omission and a null are different facts.
       2. A heading present with an EMPTY body is malformed and refuses. It is neither an
          answer nor a not-yet.
       3. An absent heading before its gate is legal.

     Headings are a PARSED contract — canonical English, exactly as written here. Body prose
     follows the repo's language. A heading outside this set is a stray and validate flags it.

     AUDIENCE. Each section names who reads it. `## Problem`/`## Proposal`/`## Design` are for
     the human — examples and plain language belong there. `## Handoff`/`## Tasks` are for
     agents — terse, with `files:`/`verify:`/`pattern:` metadata. An orchestrator never sends
     the human sections to an executor; that is what lets one file serve both audiences
     without bloating agent context. -->

## Problem

Three artifacts assert that `allowed-tools` enforces a read-only guarantee: the doctrine bullet in
`/docs:status` and `/specs:status` â€” *"The `allowed-tools` above carry no `Write` or `Edit` â€” that
is the enforcement, not a promise"* â€” and the same clause in the plugin README's `/docs:status`
paragraph.

**A standing rule already forbids this.**
[standards/quality/surface-verification.md](/docs/standards/quality/surface-verification.md)
Â§What this does not cover is `authority: current` and says of `allowed-tools` enforcement:
*"Never observed to restrict anything â€¦ not to be claimed anywhere until it is measured."* The
surface violates its own contract in three places.

The evidence behind that rule is
[reference/tools/claude-code-skill-command-mechanics.md](/docs/reference/tools/claude-code-skill-command-mechanics.md)
Â§6 â€” a probe declaring `allowed-tools: ["Bash(echo:*)"]` still completed a `Write`, verified on the
filesystem rather than by self-report, in all four cells of command Ã— skill by slash-invocation Ã—
Skill-tool-invocation. That row is deliberately narrow: one Linux machine, `claude -p`, Claude Code
2.1.215, no interactive session tested, and a permission mode may fully account for it. It is a
lead, not a verdict â€” which is precisely why nothing may claim the enforcement yet.

**The claim also propagates.** `plugins/quenching/assets/templates/automation/skills-standard.md`
is the mold every aligned repo's `docs/standards/automation/skills.md` is cut from. Its
Â§`allowed-tools` is always scoped says *"grant the narrowest set"* and never says the grant is a
declaration rather than a lock â€” the exact gap that produced all three sentences here, shipped
outward to every target repo.

What is at stake is not an incident: no failure is known to have come from it, and all three
commands are written not to write regardless. It is that a stated guarantee is unbacked, in a repo
whose whole premise is that a claim carries the evidence for it.

## Proposal

- No artifact in this repo claims `allowed-tools` enforces anything. All three instances of the
  claim are **deleted**, not reworded: `commands/docs/status.md`, `commands/specs/status.md`, and
  the plugin `README.md`.
- `/docs:status` and `/specs:status` still guarantee zero writes â€” backed by the "Zero writes, no
  exceptions" bullet and its enumerated no-stamp / no-index / no-marker list, which a reader can
  audit against the numbered steps.
- `docs/standards/automation/skills.md` Â§`allowed-tools` is always scoped states what a scoped
  grant is known to buy â€” a declaration `skills.py lint` checks â€” and cites
  `surface-verification.md` for what it has never been observed to buy.
- `assets/templates/automation/skills-standard.md` carries the same caveat **self-contained**, so a
  repo cut from the mold does not inherit the gap that produced this defect.
- `surface-verification.md`'s *"not to be claimed anywhere until it is measured"* has zero
  violations in the repo.

## Out of Scope

- **Measuring whether `allowed-tools` restricts anything.** Ruled out at definition: this spec
  removes an unbacked claim, not the knowledge gap behind it.
  [row 6](/docs/reference/tools/claude-code-skill-command-mechanics.md) owns that question at
  `authority: background`, and its reliance table already states the condition for reopening â€”
  nobody should lean on the row until it is measured properly. No probe, no `functional-checks.sh`
  assertion, no re-measurement here.
- **The twelve commands scoping `Bash` to `python3`/`py`.** Same mechanism, larger exposure, and
  equally unmeasured â€” but no body claims those grants restrict anything, so there is no false
  statement to remove. It becomes work only if the measurement above ever happens.
- **Enforcing the read-only property some other way** â€” a `PreToolUse` hook, or an audit proving no
  numbered step writes. That builds a guarantee; this spec removes a claim to one.
- **A `skills.py` lint code for the claim.** Rejected in `## Design`: it would match on prose, so it
  fires on any body legitimately discussing the caveat â€” including the corrected ones.
- **`README.md` lines 479-480, the cost-model rows.** They record that both status commands declare
  no `Write`/`Edit`, which is a true statement about what the surface costs. They assert no
  enforcement and are left alone.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/automation/skills.md` â€” Â§`allowed-tools` is always scoped gains the rule that a
  grant is a declaration `skills.py lint` checks, never a restriction, cross-referencing
  `quality/surface-verification.md` for the measurement behind it

### Standards at `authority: background` this spec may resolve

- none â€” row 6 of `reference/tools/claude-code-skill-command-mechanics.md` stays
  `authority: background` and unmeasured, per `## Out of Scope`

### Product code this spec expects to touch

- `plugins/quenching/commands/docs/status.md` â€” the doctrine bullet's last sentence
- `plugins/quenching/commands/specs/status.md` â€” the same sentence
- `plugins/quenching/README.md` â€” the `/docs:status` paragraph's same clause
- `plugins/quenching/assets/templates/automation/skills-standard.md` â€” the mold gains the rule-only
  caveat
- `docs/reference/tools/claude-code-skill-command-mechanics.md` â€” Â§What has been relied upon records
  the episode

## Validation

```bash
# 1. zero surviving instances of the claim
grep -rn "is the enforcement\|enforcement rather than a promise" --include='*.md' plugins/ docs/
#    expect: no matches

# 2. the command surface's conformance is unchanged
cd plugins/quenching
python3 assets/bin/skills.py --root . doctor    # 24 commands, 0 error(s), 0 warning(s)
python3 assets/bin/skills.py --root . lint      # exit 0, the same five pre-existing warnings

# 3. both edited OKF docs stay conformant
python3 plugins/quenching/assets/hooks/okf-validate.py docs   # 0 error(s), 0 warning(s)

# 4. the surface still LOADS â€” the only check for a commands/** change
./plugins/quenching/assets/bin/functional-checks.sh           # 9/9 assertions, exit 0
python3 plugins/quenching/assets/bin/specs.py validate        # 0/0 â€” no check-3 residue survived
```

Check 4 is required by `docs/standards/quality/surface-verification.md`, `authority: current`:
nothing under `commands/**` is testable in the session that writes it, and check 1 of the harness
invokes `/quenching:specs:status` â€” one of the two bodies this spec edits â€” so a botched edit fails
there and nowhere else.

## Design

**Delete the sentence rather than correct it.** The doctrine bullet's enumerated list â€” no stamp,
no index regeneration, no `log.md` entry, not even a marker file â€” already *is* the guarantee.
Correcting the sentence in place adds two lines to each body to restate a fact recorded twice
already (row 6 and `surface-verification.md`), which is the sediment the writing doctrine warns
against. Naming the body as the backing was rejected for the same reason: it answers a question no
reader of a deletion is left holding.

**The deletion is correct regardless of what a measurement would find.** Even if `allowed-tools`
does restrict, `surface-verification.md` forbids the claim *until it is measured*. The outcome of
the ruled-out probe therefore cannot change this spec's action â€” which is what makes ruling it out
safe rather than merely cheap.

**Cross-reference from `skills.md`; do not move or duplicate the rule.** Both command-body
sentences were written by sessions holding `docs/standards/automation/skills.md`, the
command-authoring standard, and not `surface-verification.md`, a verification standard an authoring
session has no reason to open. Â§`allowed-tools` is always scoped says *"grant the narrowest set the
workflow needs"* and stops, leaving a reader to infer the grant is a lock. One pointer in the
section authors actually read closes that path. Relocating the clause into `skills.md` was
rejected: its home under "What this does not cover" is defensible, and moving it churns two
standards to fix three sentences.

**The template's caveat is self-contained, not a pointer.** A target repo has no
`surface-verification.md` to cite, so a cross-reference there would dangle. The mold's version
states the caveat in one sentence and stops.

**Binding contract this design knowingly strains.** `skills.md` Â§The verifier holds that *"a rule
whose only check is a sentence decays, because nothing fails when it is broken."* This design ships
a prose-only rule anyway, because the mechanical alternative keys on wording rather than on a
threshold. **ACCEPTED** â€” the tradeoff is stated rather than hidden, and `## Risks` carries it.

**Verified clean, no edit.** `assets/claude/QUENCHING.md` line 191 states the scoped grant as a cost
item and claims no enforcement.

## Alternatives Considered

| Shape | Why it lost |
| --- | --- |
| **Measure first, then act on the result** â€” probe interactive Ã— each permission mode Ã— both invocation paths, update row 6, reword on what it says. | The deletion is required either way (see `## Design`), so the measurement cannot change the action â€” it only delays it behind a probe harness two sibling specs are already contending over. |
| **Enforce the read-only property independently** â€” a `PreToolUse` hook, or an audit proving no numbered step writes. | Builds a guarantee to replace a claim nobody has shown is needed: no incident exists, and all three commands are written not to write. A permanent surface cost for a hypothetical. |
| **Aim at the surface-wide scoping** â€” treat the twelve `Bash(python3:*)` grants as the real target. | Genuinely the larger exposure, but there is no false statement there to remove â€” only an unmeasured assumption, which is the shape ruled out above. |

## Open Decisions

- none â€” the measurement was ruled OUT in `## Out of Scope` rather than deferred, and the
  prose-only-rule tradeoff is an accepted risk rather than an open one. Nothing this spec depends on
  is awaiting evidence.

## Risks

- **The rule has no mechanical check.** `skills.py` cannot flag a fourth instance, because the only
  signature is wording. **ACCEPTED** â€” a lint code keyed on prose would fire on every body
  legitimately discussing the caveat, including the corrected ones. `## Design` names this as a
  deliberate strain on `skills.md` Â§The verifier's *"a rule whose only check is a sentence decays"*.
- **The mold's caveat reaches repos nobody measured.** `/skill:align` cuts a target repo's own
  `skills.md` from the template. Mitigated by construction: the template states a rule about what
  may be *claimed* and asserts nothing about Claude Code's behaviour, so no target inherits a fact
  that could be false for its version.
- **Deleting the sentence deletes the reasoning with it.** A future reader asks what backs "Zero
  writes, no exceptions" and re-adds a mechanism claim. Mitigated by tasks 2.1 and 2.2 â€” the answer
  moves to where authors read rather than disappearing.
- **`functional-checks.sh` residue is committed.** Check 3 fires capture probes into the real
  `specs/plans/` (sibling spec `isolate-functional-checks-probes` owns the fix). Mitigated: task
  4.2's `verify:` chains `specs.py validate` after the harness, so surviving residue fails the task
  instead of being noticed later.

## Handoff

**The three sentences, located.**

- `plugins/quenching/commands/docs/status.md` line 34-35 â€” *"The `allowed-tools` above carry no
  `Write` or `Edit` â€” that is the enforcement, not a promise."*
- `plugins/quenching/commands/specs/status.md` line 34-35 â€” the same, worded *"no `Write` and no
  `Edit`"*.
- `plugins/quenching/README.md` line 207-208 â€” *"`allowed-tools` carries no `Write` or `Edit`, which
  is the enforcement rather than a promise"*. This one is mid-sentence: deleting it needs the clause
  re-joined, e.g. *"It writes nothing, and owns no contract, citing â€¦"*.

**Baseline before any edit,** to compare the verify runs against: `skills.py doctor` â€” 24 commands,
0 error(s), 0 warning(s). `skills.py lint` â€” exit 0 with five warnings (`sk-no-boundary`,
`sk-step-criterion`, `sk-trigger-position`, and two `sk-unscoped-bash`), **none of them in the files
this spec edits**. A sixth warning appearing means the edit broke something.

**Already swept during definition.** Every `allowed-tools` mention in the repository was read; the
three above are the only enforcement claims. `README.md` lines 479-480 (the cost-model rows) and
`assets/claude/QUENCHING.md` line 191 state the grant as a cost, claim nothing, and are
deliberately left alone â€” do not "fix" them.

## Tasks

### 1. Remove the claim

- [x] 1.1 Delete the enforcement sentence from the /docs:status and /specs:status doctrine bullets
      files: plugins/quenching/commands/docs/status.md, plugins/quenching/commands/specs/status.md
      verify: cd plugins/quenching && python3 assets/bin/skills.py --root . doctor && python3 assets/bin/skills.py --root . lint
      subject: plan/verify-allowed-tools-enforcement: 1.1 Delete the enforcement sentence from the /docs:status and /specs:status doctrine bullets
- [x] 1.2 Delete the same clause from the plugin README's /docs:status paragraph, re-joining the sentence
      files: plugins/quenching/README.md
      subject: plan/verify-allowed-tools-enforcement: 1.2 Delete the same clause from the plugin README's /docs:status paragraph, re-joining the sentence

### 2. Close the authoring gap that produced it

- [ ] 2.1 Add to docs/standards/automation/skills.md Â§`allowed-tools` is always scoped: the grant is a declaration lint checks, not a restriction â€” cross-referencing quality/surface-verification.md
      files: docs/standards/automation/skills.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
- [ ] 2.2 Add the rule-only caveat â€” a rule about what may be claimed, no assertion about Claude Code â€” to the mold
      files: plugins/quenching/assets/templates/automation/skills-standard.md
      pattern: docs/standards/automation/skills.md

### 3. Record the episode where row 6's readers will find it

- [ ] 3.1 Record in docs/reference/tools/claude-code-skill-command-mechanics.md Â§What has been relied upon that three artifacts asserted row 6's contrary until this spec removed them
      files: docs/reference/tools/claude-code-skill-command-mechanics.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs

### 4. Prove it

- [ ] 4.1 Prove zero surviving instances of the claim across plugins/ and docs/
      verify: ! grep -rn "is the enforcement\|enforcement rather than a promise" --include='*.md' plugins/ docs/
- [ ] 4.2 Run the surface's functional checks and revert any check-3 residue in the same commit
      verify: ./plugins/quenching/assets/bin/functional-checks.sh && python3 plugins/quenching/assets/bin/specs.py validate

## Discoveries

- Task 4.1's verify: grep pattern 'is the enforcement' cannot match commands/docs/status.md or commands/specs/status.md — the phrase wraps across a line break there ('that is the' / 'enforcement, not a promise'), and grep is line-based. As written the check passes vacuously and would report zero instances even with both sentences intact. A multiline-capable check (grep -Pzo, or ripgrep -U) is needed for 4.1 to prove its claim.
