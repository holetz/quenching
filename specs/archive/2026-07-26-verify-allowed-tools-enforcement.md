---
slug: verify-allowed-tools-enforcement
title: Verify Allowed Tools Enforcement
verification: per-section
priority: {level: 3, criticality: critical, date: 2026-07-28}
refined: {mode: gate, date: 2026-07-28}
approved: {date: 2026-07-28}
branch: {base: main, work: plan/verify-allowed-tools-enforcement}
reviewed: {date: 2026-07-28}
outcome: done
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
# 1. zero surviving instances of the claim — the check must be MULTILINE: the phrase wraps
#    across a line break in both command bodies, and a line-based grep finds only the README
python3 -c "import re,sys,pathlib; p=re.compile(r'is the\s+enforcement|enforcement\s+rather than a promise'); h=[str(f) for d in ('plugins','docs') for f in pathlib.Path(d).rglob('*.md') if p.search(f.read_text(encoding='utf-8',errors='replace'))]; print(*h,sep='\n'); sys.exit(1 if h else 0)"
#    expect: no matches, exit 0

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

**State: 6 of 7 tasks done, 4.2 blocked.** All three sentences are deleted, both authoring gaps are
closed, and the episode is recorded. Isolated on `plan/verify-allowed-tools-enforcement`, a worktree
at `../claude-quenching-verify-allowed-tools-enforcement`, cut from `main`. Nothing is merged.

**What is left.** Only 4.2, blocked on failures this branch did not cause — read its `- [!]` reason
in `## Tasks`. It needs a decision, not a retry: the two failing checks are properties of `main`.

**Measured baselines on this branch** (the ones written at definition were stale, see
`## Discoveries`): `skills.py doctor` â€” **25** commands, 0 error(s), 0 warning(s). `skills.py lint`
â€” exit 0 with **35** warnings, of which **two are in `commands/docs/status.md`**
(`sk-trigger-position`, `sk-no-boundary`); both concern that file's frontmatter description, which
this spec never touched, and both are present on `main`. `okf-validate.py docs` â€” 0 error(s),
**2** warning(s) (`resource-unresolved` on `standards/automation/agents.md`, `stale-doc` on
`standards/automation/hooks.md`), both pre-existing and proved so by a stash test. Every one of
these exits 0; only the figures recorded at definition were wrong.

**The claim-sweep must be multiline.** A line-based grep finds only the README, because the phrase
wraps across a line break in both command bodies. 4.2's predecessor 4.1 now carries a `python3`
check proven to exit 1 against `main` and 0 against `HEAD` â€” do not "simplify" it back to `grep`.

**`functional-checks.sh` cannot see this branch.** The plugin resolves through a marketplace
`directory` source pinned to the main checkout, so `${CLAUDE_PLUGIN_ROOT}` points there whatever
tree `claude -p` runs in (measured â€” see `## Discoveries`). Re-running the harness from this
worktree will never grade these edits; it must run on `main` after the merge.

**Already swept during definition, and still true.** Every `allowed-tools` mention in the repository
was read; the three now deleted were the only enforcement claims. `README.md` lines 479-480 (the
cost-model rows) and `assets/claude/QUENCHING.md` line 191 state the grant as a cost, claim nothing,
and are deliberately left alone â€” do not "fix" them.

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

- [x] 2.1 Add to docs/standards/automation/skills.md Â§`allowed-tools` is always scoped: the grant is a declaration lint checks, not a restriction â€” cross-referencing quality/surface-verification.md
      files: docs/standards/automation/skills.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
      subject: plan/verify-allowed-tools-enforcement: 2.1 Record in skills.md that an allowed-tools grant is a declaration lint checks, not a restriction
- [x] 2.2 Add the rule-only caveat â€” a rule about what may be claimed, no assertion about Claude Code â€” to the mold
      files: plugins/quenching/assets/templates/automation/skills-standard.md
      pattern: docs/standards/automation/skills.md
      subject: plan/verify-allowed-tools-enforcement: 2.2 Add the rule-only allowed-tools caveat to the skills-standard mold

### 3. Record the episode where row 6's readers will find it

- [x] 3.1 Record in docs/reference/tools/claude-code-skill-command-mechanics.md Â§What has been relied upon that three artifacts asserted row 6's contrary until this spec removed them
      files: docs/reference/tools/claude-code-skill-command-mechanics.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
      subject: plan/verify-allowed-tools-enforcement: 3.1 Record in the mechanics reference that three artifacts asserted row 6's contrary

### 4. Prove it

- [x] 4.1 Prove zero surviving instances of the claim across plugins/ and docs/
      verify: python3 -c "import re,sys,pathlib; p=re.compile(r'is the\s+enforcement|enforcement\s+rather than a promise'); h=[str(f) for d in ('plugins','docs') for f in pathlib.Path(d).rglob('*.md') if p.search(f.read_text(encoding='utf-8',errors='replace'))]; print(*h,sep='\n'); sys.exit(1 if h else 0)"
      subject: plan/verify-allowed-tools-enforcement: 4.1 Prove zero surviving instances of the claim across plugins/ and docs/
- [!] 4.2 Run the surface's functional checks and revert any check-3 residue in the same commit — blocked: verify exits 1 for two pre-existing reasons, neither caused by this branch. (a) functional-checks.sh: 5 passed, 3 failed, 1 inconclusive — all in check 3, spoken-trigger routing for specs:create x2, skill:hook:new, and skill:agent:new (turn cap). Check 3 grades routing by DESCRIPTION alone; this branch changes no frontmatter line in commands/** and touches none of those four commands (2 files, 2 insertions, 4 deletions, all inside doctrine bullets). The harness also loads the main checkout regardless of cwd, so it never saw this branch. Checks 1 and 2 passed 4/4. (b) specs.py validate: sp-handoff-empty on the sibling spec fix-skills-py-description-truncation, present before this run began. Neither converges within this spec's scope. No check-3 residue: the probes now sandbox into their own repos, and the tree was clean after the run.
      verify: ./plugins/quenching/assets/bin/functional-checks.sh && python3 plugins/quenching/assets/bin/specs.py validate

## Discoveries

- Task 4.1's verify: grep pattern 'is the enforcement' cannot match commands/docs/status.md or commands/specs/status.md — the phrase wraps across a line break there ('that is the' / 'enforcement, not a promise'), and grep is line-based. Measured against main with all three sentences intact, the declared pattern found 1 of 3 (only the README, whose clause happens to sit on one line) — so the task would have passed with both command bodies unfixed. RESOLVED during execution: 4.1's verify and ## Validation check 1 both replaced with a multiline python3 check, proven to exit 1 against main and 0 against HEAD.
- The spec's ## Handoff and ## Validation baselines are stale, measured before this branch: skills.py reports 25 commands not 24; lint exits 0 with 35 warnings not 5, and 2 of them ARE in commands/docs/status.md (sk-trigger-position, sk-no-boundary, both about the frontmatter description, neither touched by this spec); okf-validate.py docs reports 0 errors and 2 warnings not 0/0 (resource-unresolved on standards/automation/agents.md, stale-doc on standards/automation/hooks.md), both pre-existing and proved so by a stash test. Exit codes are 0 throughout, so every task verify still passes — only the stated figures were wrong.
- functional-checks.sh cannot validate commands/** edits made on a BRANCH or WORKTREE. The plugin resolves through the marketplace, a 'directory' source pinned to the main checkout (~/.claude/plugins/known_marketplaces.json -> C:\Users\holet\repos\claude-quenching), so ${CLAUDE_PLUGIN_ROOT} substitutes to the main checkout no matter which tree claude -p is launched from. Measured: check 1's probe run from this worktree Read C:/Users/holet/repos/claude-quenching/plugins/quenching/assets/references/specs-develop/spec-driven.md. This defeats the rationale in this spec's ## Validation and, more broadly, the standing rule in docs/standards/quality/surface-verification.md that the harness is the only check for a commands/** change — on every spec that isolates before editing commands/**, the harness grades the base, not the work. Also noted: installed_plugins.json lists an installPath cache at .../cache/claude-quenching/quenching/4.1.0 that does not exist on disk.
- functional-checks.sh check 1 crashes mid-stream on Windows and can report a FALSE PASS. Its tools() helper does open(sys.argv[2]) with no encoding, so Python uses cp1252 and dies with UnicodeDecodeError at the first non-cp1252 byte (observed: byte 0x9d at position 5555 of the stream-json log). Stdout keeps whatever lines printed before the crash, so the first assertion passed on a real match, but the second — 'read nothing under a skills/ tree' — asserts ABSENCE over truncated input, and any Read after the crash point is invisible to it. Fix: open(..., encoding='utf-8', errors='replace'). Same family as this spec's own 4.1 defect: a check that reports a verdict on data it could not read.

## Outcome

Shipped as specified. All three enforcement claims are deleted â€” the `/docs:status` and
`/specs:status` doctrine bullets and the plugin `README.md`'s `/docs:status` paragraph â€” and the
authoring gap that produced them is closed in both places a future author actually reads:
`docs/standards/automation/skills.md` Â§`allowed-tools` is always scoped, and the
`skills-standard.md` mold every aligned repo's copy is cut from. The episode is recorded against
row 6 of `reference/tools/claude-code-skill-command-mechanics.md`, where that row's readers will
find it. `surface-verification.md`'s *"not to be claimed anywhere until it is measured"* now has
zero violations in the repo.

**Merged as a merge commit**, so every per-task `subject:` in `## Tasks` resolves from `main` and
the branch is not load-bearing.

**Task 4.2 is `[!]` blocked, not done â€” closing as `done` was the human's explicit call.** Its
`verify:` is `functional-checks.sh`, and this spec measured why that can never converge from a
branch: the harness resolves `${CLAUDE_PLUGIN_ROOT}` through the marketplace's pinned clone, so it
grades the base checkout whatever tree `claude -p` runs in. That is now **precondition 5** of
`docs/standards/quality/surface-verification.md`, written during conclude. The harness's own
failures â€” check 3's spoken-trigger routing for `specs:create` Ã—2, `skill:hook:new` and
`skill:agent:new` â€” are properties of `main`, on four commands this branch never touched, and the
post-merge run reported them unchanged.

**The branch review changed one thing.** The paragraph task 2.1 added to `skills.md` opened with
*"never a restriction"* â€” this spec's own defect reproduced by the fix meant to remove it. Hedged
to *"whether it also restricts is unmeasured"*, matching the mold task 2.2 wrote and the
paragraph's own next sentence.

**What the next reader needs.** The measurement ruled out in `## Out of Scope` is still not done:
nobody knows whether `allowed-tools` restricts anything, row 6 stays `authority: background`, and
this spec removed a claim rather than the gap behind it. Two siblings still in `plans/` own the
harness defects this one only recorded â€” `fix-functional-checks-encoding` (check 1's cp1252 false
pass) and `isolate-functional-checks-probes` (check 3's residue). The twelve commands scoping
`Bash` to `python3`/`py` remain unmeasured too, and deliberately so: no body claims those grants
restrict anything, so there is no false statement there to remove.
