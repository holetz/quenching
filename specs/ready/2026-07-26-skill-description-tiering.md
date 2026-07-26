---
slug: skill-description-tiering
title: Two-tier skill description policy: cut always-on metadata by 83%
verification: per-section
---

# Two-tier skill description policy: cut always-on metadata by 83%

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

The plugin's skill metadata is **always on**. A `SKILL.md` body loads only when the skill
fires, but every skill's `description` + `when_to_use`, plus every command wrapper's
`description`, sit in context on every session before anything is selected.

Measured on this working tree with the repo's own instrument
(`skills.py --root plugins/claude-quenching budget`, which counts the **parsed** frontmatter
value as [context-budget.md](../../docs/standards/automation/context-budget.md) requires):

| | chars | ~tokens |
| --- | ---: | ---: |
| 28 skill `description` | 25,875 | |
| 28 skill `when_to_use` | 2,761 | |
| 28 wrapper `description` | 2,069 | |
| **total always-on** | **30,705** | **~7,676** |

That is **84.1%** of the standard's own 36,503 ceiling, consumed before a single skill runs.

The existing standard already forbids the worst waste â€” procedure prose in a description, a
`Not for:` restated in `when_to_use` â€” and a prior diet recovered ~5,500 characters by
enforcing exactly that. What it does **not** question is its own uniformity: it requires every
skill to carry a leading concept, verbatim trigger phrases, and a routing boundary
(`sk-trigger-position`, `sk-no-boundary`), as if every skill were equally likely to be selected
by the model from prose.

**Almost none of them are.** These skills are operated by typed command â€” `/docs:align`,
`/specs:apply`. The description exists so the *model* can decide to fire a skill; when the
human types the command, that decision already happened and the description bought nothing.
Worse, the stage skills are invoked **by name from a conductor's body**, so their descriptions
are never read for routing by anyone, ever.

A note on evidence: the session that produced this spec observed the *installed* plugin's
skill listing rendering 11 of its skills with the name alone and no description â€” descriptions
that were written, cap-conformant, and structurally identical to ones that did render. That
observation is against the installed build (30 skills, nested `plan-`/`backlog-` names), not
against this tree (28, flat names), and the mechanism was never determined, so it is recorded
as a prompt for this work rather than as a measurement supporting it. The measurement above
stands on its own.

## Proposal

Split the surface into **two tiers** by how a skill is actually reached, and spend description
budget only where routing genuinely happens.

The line is one the architecture already drew â€” `CLAUDE.md` describes the plugin as a set of
entry points plus *"a stage of one of these eight invokes, or a per-item capture tool"*. That
yields three routing classes, and only one of them needs a description:

1. **Stages** â€” invoked by a conductor, by name, from its body. The description is never read
   for routing. Dead weight, in full.
2. **Entry points** â€” the align matrix and the plan cycle. Always typed as a command; the
   wrapper is the interface the human sees.
3. **Capture tools** â€” spoken mid-conversation ("anota isso", "pÃµe esse termo no glossÃ¡rio").
   The description is the *only* thing that makes them reachable.

**Tier A (5)** â€” full description, compressed: `quenching-docs-add`, `quenching-docs-learn`,
`quenching-docs-define`, `quenching-specs-capture`, `quenching-specs-explore`.

**Tier B (23)** â€” everything else: a one-line stub, **the command wrapper's `description`
verbatim**. Those strings already exist, are already concise (~74 chars), and are already
human-reviewed for the `/` menu. Reusing them creates the invariant
`wrapper.description â‰¡ skill.description`, so a Tier B skill carries one string to maintain
instead of two that can drift apart.

`when_to_use` is dropped on all 28 â€” a Claude-Code-only extension whose remaining content is a
restatement of the description's first clause.

Projected, from the same instrument:

| | today | after | cut |
| --- | ---: | ---: | ---: |
| Tier A (5) `desc`+`wtu` | 4,107 | 1,290 | 69% |
| Tier B (23) `desc`+`wtu` | 24,529 | 1,710 | 93% |
| skill-side subtotal | 28,636 | 3,000 | **89%** |
| wrappers (unchanged) | 2,069 | 2,069 | â€” |
| **total always-on** | **30,705** | **5,069** | **83%** |
| ~tokens | ~7,676 | ~1,267 | |

**~25,600 characters â€” roughly 6,400 tokens â€” off every session in every repo that installs
the plugin.** Nothing changes in what the user sees when they type `/`.

## Out of Scope

- **The command wrappers.** Their `description` is the human-facing interface and the source
  of the Tier B stub; it is read, not rewritten. Their 2,069 characters stay.
- **Skill bodies and `references/`.** Load-on-invocation, already governed by `sk-body-length`.
  Not touched.
- **Renaming or merging skills.** The surface stays 28 skills and 28 wrappers. Cutting the
  *number* of skills is a different argument with different evidence.
- **The per-skill caps themselves** (1,536 `sk-metadata-cap`, 1,024 `sk-description-portable`).
  They stay as written; this spec changes what fills them, not their height.
- **Pruning Tier A trigger phrases.** Deciding *which* triggers earn their place is settled on
  measured should-trigger / should-not-trigger rates via `quenching-skill-eval`, which the
  standard already mandates and this spec does not short-circuit. Task 3 compresses everything
  around the triggers and leaves the trigger set intact; pruning is a follow-up gated on a
  measurement that does not exist yet.
- **The installed-build divergence.** This tree is 28 flat-named skills at `specs 2.0.0`; the
  build loaded in the authoring session was 30 nested-named. Reconciling them is not this
  spec's job â€” but see `## Risks`.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/automation/context-budget.md` â€” **revised, not created.** This is the
  first-class item. The standard today mandates a uniform three-part description for every
  skill; the two-tier policy contradicts that for 23 of 28. It gains a Â§Tiers section, loses
  the implication that triggers and a boundary are universal, and has its `when_to_use`
  paragraph reduced to "do not use it". Its `authority: background` and its graduation
  condition are re-stated against the new measurement.

### Tooling that must change with it (not standards â€” no doc promised)

- `plugins/claude-quenching/assets/bin/skills.py` â€” `sk-trigger-position` and `sk-no-boundary`
  are `warn` findings that fire when a description quotes no trigger phrase or omits
  `Not for:`. Both are **true of every Tier B stub by design**, so without tier-awareness this
  spec lands 46 new warnings and makes `lint` useless. The linter must learn the tier and
  scope both checks to Tier A. `DEFAULT_CEILING` (36,503) is also revised â€” from the
  post-change measurement, per the standard's own "revised only from a measurement" rule.
- `plugins/claude-quenching/assets/templates/automation/skill.md` â€” the mold that teaches a
  new skill's frontmatter; it must teach the tier declaration.

### Skills whose doctrine teaches the old rule

- `quenching-skill-new` + `references/doctrine.md` â€” instructs authors to put triggers in the
  second sentence so truncation cannot eat them. Correct for Tier A, wrong for Tier B.
- `quenching-skill-align` and `quenching-skill-align-and-update` â€” the sweep and the body
  audit; both judge descriptions against the doctrine they cite.

### Surface edited but owning no contract

- 28 Ã— `plugins/claude-quenching/skills/*/SKILL.md` â€” frontmatter only.
- `plugins/claude-quenching/README.md` Â§Cost model â€” states the thirty fit under the cap; must
  speak of the **sum** and of the tiers, and its skill count is stale.

## Validation

Every claim in this spec is mechanically checkable; none of it rests on reading prose.

- **The saving is real** â€” `skills.py --root plugins/claude-quenching budget --json` before and
  after. Baseline is 30,705 characters / ~7,676 tokens; the target is â‰¤ 5,500 total always-on.
  The instrument counts parsed frontmatter, which is the standard's own requirement.
- **Nothing became non-conformant** â€” `skills.py --root plugins/claude-quenching lint` exits 0
  with no new finding code. Specifically `sk-trigger-position` and `sk-no-boundary` must not
  fire on a Tier B stub, and `sk-no-description` must not fire at all.
- **The wrapper invariant holds** â€” for all 23 Tier B skills, the skill `description` equals
  its wrapper's `description` byte-for-byte. Checked by script, not by eye.
- **Tier A still routes** â€” `quenching-skill-eval` on each of the five, comparing
  should-trigger / should-not-trigger rates before and after compression. This is the one
  claim a diff cannot settle, and the standard already names eval as the arbiter. A Tier A
  skill whose measured trigger rate drops is reverted, not argued with.
- **The bundle still passes** â€” `okf-validate.py assets/docs` and
  `okf-validate.py assets/specs/backlog --listing-root` both clean, since the standard doc is
  edited in `docs/` and the payload is untouched.
- **Version lockstep** â€” if `skills.py` changes, `VERSION`, `plugin.json`, the marketplace
  manifest, and both other shipped scripts stay in step per `CLAUDE.md` Â§Releasing.

## Design

### How a skill declares its tier

The linter cannot guess the tier, and it must not: `skills.py` ships into target repos, so it
may not carry a hard-coded list of this plugin's skills. The tier is **declared**, in
frontmatter:

```yaml
routing: direct     # reached by a typed command, or named by a conductor's body
routing: inferred   # the model must decide from prose â€” the description is load-bearing
```

**Absent means `inferred`.** That default is what keeps the change safe for every repo that
already installed the plugin: a skill that says nothing keeps today's behavior and today's
checks. Only an explicit `routing: direct` relaxes anything. The field is a declaration an
author makes on purpose, and it is greppable â€” which the alternatives (inferring the tier from
description length, or from whether a wrapper exists) are not, and both of those would silently
reclassify a skill as a side effect of an unrelated edit.

### What each check does with it

| Check | `inferred` | `direct` |
| --- | --- | --- |
| `sk-no-description` | error | error (a stub is still a description) |
| `sk-metadata-cap` (1,536) | error | error |
| `sk-description-portable` (1,024) | warn | warn |
| `sk-trigger-position` | warn | **not applicable** |
| `sk-no-boundary` | warn | **not applicable** |

A new `sk-wrapper-drift` (warn) fires when a `routing: direct` skill's description differs from
its wrapper's â€” the invariant made mechanical, so the two strings cannot rot apart unnoticed.

### The Tier A compression recipe

The five keep a real description. What gets cut is settled by function, not by taste â€” a
description exists to let a reader predict **when it fires and what exists when it finishes**:

1. **Cut the scaffold.** `Use when the user asks to` plus the quoting apparatus, ~40 chars
   each, carries no signal.
2. **Cut the mechanism.** "updates the folder's `index.md`, appends a `log.md` entry, and
   self-checks" â€” the body teaches this on invocation. The standard already forbids it; the
   five drifted back.
3. **Cut the dead boundaries.** A `Not for: ... -> <Tier B skill>` disambiguates against
   something that no longer competes for inferred routing. Only Tier-A-vs-Tier-A boundaries
   survive.
4. **Keep every trigger phrase.** Untouched in this spec â€” see `## Out of Scope`.
5. **Keep the mechanism fragments that discriminate.** "zero interrogation, untriaged is valid"
   separates fast capture from the plan cycle; "never implements" separates explore from apply.
   These read as mechanism but do routing work, and cutting them by rule would be the
   predictable failure of applying rule 2 blindly.

Measured result: 4,107 -> 1,290 characters across the five.

### The Tier B stub

The wrapper's `description`, verbatim. Not paraphrased â€” copied, so `sk-wrapper-drift` can
check it. `when_to_use` deleted. Median stub ~74 characters, against a median 1,066 today.

### Why this order

Tasks are phased so that the risky part is last and independently revertible. The tier
declaration and the linter change land **before** any description is cut (otherwise the tree
spends a commit in a state where `lint` is noise), and Tier A compression lands after Tier B,
because Tier B is mechanical and Tier A is the part that needs `quenching-skill-eval` to
adjudicate.

## Alternatives Considered

- **A uniform, more aggressive trim â€” no tiers.** Enforce the existing standard harder on all
  28. Rejected: it recovers maybe 6,000 of the 25,600 characters, because the floor is the
  concept + triggers + boundary the standard requires of *every* skill. It keeps paying for
  trigger phrases on skills only ever reached by a typed command or by a conductor naming them.
  It optimizes the text and leaves the wrong question unasked.
- **One router skill per front (3 descriptions instead of 28).** A `quenching-docs` router
  whose description carries the triggers and whose body is a routing table. Cheapest of all,
  but it adds a hop to every invocation, and the hop is paid on the *direct* path that is
  supposed to be the common one. Held in reserve: if the two tiers prove insufficient, this is
  the next step, and it composes with them rather than replacing them.
- **Raise the ceiling.** The standard's 36,503 is a measured baseline, and 30,705 sits under
  it. Rejected: it treats the ceiling as the goal. The ceiling was set from one surface's
  pre-diet measurement and permits regression back to it; the surface being under it is not
  evidence the surface is cheap.
- **Delete `when_to_use` only.** Recovers 2,761 characters for near-zero risk, and is a
  genuinely good change. Rejected as *the* answer because it is 11% of the available saving â€”
  it is folded in here as part of task 1 rather than standing alone.
- **Infer the tier instead of declaring it** (from description length, or from whether a
  wrapper exists). Rejected in `## Design`: it makes an unrelated edit silently reclassify a
  skill.

## Open Decisions

- **Tier A membership.** Five are proposed â€” `quenching-docs-add`, `quenching-docs-learn`,
  `quenching-docs-define`, `quenching-specs-capture`, `quenching-specs-explore` â€” on the
  argument that they are the only ones a user reaches by *speaking* rather than typing.
  `quenching-docs-add` is the weakest of the five: it overlaps `learn` and `define`, and if
  eval shows it never wins a routing contest against them it should drop to Tier B. Settled by
  measurement in task 5, not before.
- **The field name and its values.** `routing: direct | inferred` reads well and defaults
  safely, but it is a new frontmatter key on a surface that also ships into other repos. If a
  future Agent Skills revision claims `routing`, this collides. Spellings considered and not
  chosen: `tier: a|b` (opaque), `discovery:` (overloaded with the `discover` subcommand).
- **The new `DEFAULT_CEILING`.** Must come from the post-change measurement, per the standard's
  own rule. ~5,100 is the projection; the number written into `skills.py` is whatever
  `budget --json` reports once tasks 1-4 have landed, not this estimate.
- **Whether the standard graduates.** It is `authority: background`, and its graduation
  condition is `skills.py budget` having run on this plugin plus two adopting repos. This spec
  gives it a second, much larger measurement on one surface â€” which is not the stated
  condition. It stays `background` unless someone argues otherwise explicitly.

## Risks

- **Tier B stops being reachable from prose.** This is the deliberate trade, not a side effect:
  say "align the docs" instead of typing `/docs:align` and nothing fires. Mitigation is
  structural â€” for stages it is irrelevant (a conductor names them), and for entry points the
  wrapper is in the `/` menu and the installed `QUENCHING.md` enumerates every command. The
  honest residual: a user who has internalized prose invocation will feel this, and it is
  reversible per skill by flipping one frontmatter line.
- **Tier A compression drops a trigger that mattered.** Task 3 keeps every trigger phrase for
  exactly this reason, but the surrounding compression could still shift how the description
  reads to the matcher. Contained by task 5's eval gate and by the revert rule: a measured drop
  is reverted, not defended.
- **The `wrapper == skill` invariant couples two files.** Editing a wrapper's description now
  silently changes a skill's routing text. `sk-wrapper-drift` catches divergence but not a
  synchronized change nobody thought through. Accepted: one string that must agree beats two
  that may disagree.
- **`skills.py` ships into target repos.** A repo running an older copy will not know
  `routing:` and will emit `sk-trigger-position` / `sk-no-boundary` on every Tier B skill of an
  upgraded plugin â€” noise, not breakage, and the reason `skills.py --version` is in the
  lockstep set. Repos upgrade the tool with the plugin.
- **The installed build is not this tree.** Authoring measured 28 flat-named skills at
  `specs 2.0.0`; the loaded plugin was 30 with nested `plan-`/`backlog-` names. Anyone applying
  this spec against the *installed* surface will find Tier A names that do not exist
  (`quenching-specs-backlog-add` for `quenching-specs-capture`, and so on). Task 0 re-runs
  `budget` and reconciles the names before anything is edited â€” the spec's numbers are a
  baseline to re-confirm, never to trust blind.
- **Cheap to reverse.** Every edit is frontmatter. `git revert` restores the old surface with no
  migration, no data, and no target-repo state to unwind.

## Tasks

Phased so the risky part is last and each phase is independently revertible. `PY` below is the
real interpreter (`C:/Users/holet/AppData/Local/Programs/Python/Python312/python.exe` on this
machine â€” `python3`/`py` are the Windows Store stub), `SK` is
`plugins/claude-quenching/assets/bin/skills.py`, `--root` is `plugins/claude-quenching`.

### 0. Reconcile the baseline

- [ ] 0.1 Re-run the measurement and reconcile the surface against this spec before editing
      anything. Confirm the skill count, the flat `quenching-specs-*` names, and the 30,705
      baseline. If the applying tree is the nested 30-skill build instead, re-derive the Tier A
      names and correct `## Design` before proceeding â€” do not map them by guess.
      verify: `$PY $SK --root plugins/claude-quenching budget --json`

### 1. The safe cut â€” no tiering yet

- [ ] 1.1 Delete `when_to_use` from all 28 `SKILL.md` frontmatters. It is a Claude-Code-only
      extension and its content restates the description's first clause; the standard already
      forbids it carrying the boundary. Recovers 2,761 characters on its own.
      files: plugins/claude-quenching/skills/*/SKILL.md
      verify: `$PY $SK --root plugins/claude-quenching lint --json`
- [ ] 1.2 Cut procedure prose from every description that still carries it â€” the step order,
      the tool calls, the checks. This enforces the *existing* standard, which already says a
      description may not say how the skill works; several drifted back since the last diet. No
      trigger phrase and no `Not for:` is touched in this task.
      files: plugins/claude-quenching/skills/*/SKILL.md
      verify: `$PY $SK --root plugins/claude-quenching budget --json`

### 2. The tier declaration and the linter

- [ ] 2.1 Add the `routing: direct | inferred` field to the skill schema and the mold, with
      absent defaulting to `inferred` so every existing repo keeps today's behavior.
      files: plugins/claude-quenching/assets/templates/automation/skill.md
- [ ] 2.2 Teach `skills.py` the tier: parse `routing`, and scope `sk-trigger-position` and
      `sk-no-boundary` to `inferred` skills only. Without this, task 3 lands 46 warnings and
      makes `lint` useless.
      files: plugins/claude-quenching/assets/bin/skills.py
      verify: `$PY $SK --root plugins/claude-quenching lint --json`
- [ ] 2.3 Add `sk-wrapper-drift` (warn): a `routing: direct` skill whose `description` differs
      from its wrapper's. This makes the Tier B invariant mechanical instead of aspirational.
      files: plugins/claude-quenching/assets/bin/skills.py
      verify: `$PY $SK --root plugins/claude-quenching lint --json`
- [ ] 2.4 Version lockstep per `CLAUDE.md` Â§Releasing â€” `skills.py` changed, so `VERSION`,
      `plugin.json`, the marketplace manifest, and the other shipped scripts move together.
      files: plugins/claude-quenching/VERSION, plugins/claude-quenching/.claude-plugin/plugin.json, .claude-plugin/marketplace.json

### 3. Tier B â€” the 23 stubs

- [ ] 3.1 Stamp `routing: direct` on the 23 non-capture skills and replace each description
      with its command wrapper's `description`, copied verbatim (not paraphrased, so 2.3 can
      check it). Expected 24,529 -> 1,710 characters.
      files: plugins/claude-quenching/skills/*/SKILL.md
      verify: `$PY $SK --root plugins/claude-quenching lint --json`

### 4. Tier A â€” the five that must still route

- [ ] 4.1 Stamp `routing: inferred` on `quenching-docs-add`, `quenching-docs-learn`,
      `quenching-docs-define`, `quenching-specs-capture`, `quenching-specs-explore`, and apply
      the `## Design` compression recipe to each: cut the scaffold, the mechanism, and the
      boundaries that point at Tier B. Keep every trigger phrase and the discriminating
      fragments. Expected 4,107 -> 1,290 characters.
      files: plugins/claude-quenching/skills/quenching-docs-add/SKILL.md, plugins/claude-quenching/skills/quenching-docs-learn/SKILL.md, plugins/claude-quenching/skills/quenching-docs-define/SKILL.md, plugins/claude-quenching/skills/quenching-specs-capture/SKILL.md, plugins/claude-quenching/skills/quenching-specs-explore/SKILL.md
      verify: `$PY $SK --root plugins/claude-quenching lint --json`

### 5. The doctrine that teaches it

- [ ] 5.1 Revise the standard `docs/standards/automation/context-budget.md` â€” the first-class
      item. Add a Â§Tiers section, stop implying triggers and a boundary are universal, reduce
      the `when_to_use` paragraph to "do not use it", and restate the graduation condition
      against the new measurement. Keep `authority: background` unless argued otherwise.
      files: docs/standards/automation/context-budget.md
- [ ] 5.2 Update the new `DEFAULT_CEILING` in `skills.py` from the measurement task 6.1
      produces â€” never from this spec's ~5,100 projection.
      files: plugins/claude-quenching/assets/bin/skills.py
- [ ] 5.3 [P] Rewrite `README.md` Â§Cost model: it claims the thirty fit under the cap, which
      optimizes per-skill height instead of the sum, and its skill count is stale.
      files: plugins/claude-quenching/README.md
- [ ] 5.4 [P] Teach the tier in `quenching-skill-new` and its `references/doctrine.md`, which
      today tells every author to put triggers in the second sentence against truncation â€”
      right for Tier A, wrong for Tier B. Minting a skill must now ask which tier it is.
      files: plugins/claude-quenching/skills/quenching-skill-new/SKILL.md, plugins/claude-quenching/skills/quenching-skill-new/references/doctrine.md
- [ ] 5.5 [P] Teach the tier to the two sweeps that judge descriptions against that doctrine â€”
      `quenching-skill-align` (the migration) and `quenching-skill-align-and-update` (the body
      audit). Neither may report a Tier B stub as a defect.
      files: plugins/claude-quenching/skills/quenching-skill-align/SKILL.md, plugins/claude-quenching/skills/quenching-skill-align-and-update/SKILL.md

### 6. Prove it

- [ ] 6.1 Measure the result and confirm the target: `lint` exits 0 with no new code, `budget`
      reports total always-on at or under 5,500 characters against the revised ceiling.
      verify: `$PY $SK --root plugins/claude-quenching lint --json && $PY $SK --root plugins/claude-quenching budget --json`
- [ ] 6.2 Script-check the Tier B invariant: for all 23, skill `description` equals wrapper
      `description` byte-for-byte. By script, never by eye.
      verify: `$PY $SK --root plugins/claude-quenching lint --json`
- [ ] 6.3 Run `quenching-skill-eval` on each Tier A skill and compare should-trigger /
      should-not-trigger rates against the pre-change baseline. **This is the gate**: a skill
      whose measured trigger rate drops is reverted, not defended. If no baseline was captured
      before task 4.1, capture one by evaluating the pre-change descriptions from git history.
- [ ] 6.4 [P] Confirm the shipped payload is untouched and still conformant.
      verify: `$PY plugins/claude-quenching/assets/hooks/okf-validate.py plugins/claude-quenching/assets/docs && $PY plugins/claude-quenching/assets/hooks/okf-validate.py plugins/claude-quenching/assets/specs/backlog --listing-root`
