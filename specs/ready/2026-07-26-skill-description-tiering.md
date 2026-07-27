---
slug: skill-description-tiering
title: "Two-tier skill description policy: cut always-on metadata by 87%"
verification: per-section
refined: {mode: interview, date: 2026-07-26}
---

# Two-tier skill description policy: cut always-on metadata by 87%

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

### Why it is always on: the plugin picked the worst row

All 28 skills carry `user-invocable: false`. Claude Code's own invocation table makes that the
one setting that pays the cost and collects none of the benefit:

| Frontmatter | You invoke | Claude invokes | When loaded into context |
| --- | --- | --- | --- |
| (default) | Yes | Yes | Description **always in context** |
| `disable-model-invocation: true` | Yes | No | Description **not in context** |
| `user-invocable: false` | No | Yes | Description **always in context** |

`user-invocable: false` means the description is always resident **and** the human cannot type
the skill — which is exactly why 28 command wrappers exist to front them. So the surface pays
for 28 always-on descriptions, and then pays again for 28 wrapper descriptions that are the
strings a human actually reads.

The third row is not a bug to fix in this spec: flipping to `disable-model-invocation: true`
would drop every description from context, but it also makes all 28 skills typable, surfacing
28 duplicate entries in the `/` menu beside the wrappers. That trade only closes once the
wrappers are gone — see `## Out of Scope`.

### What the existing standard does and does not question

The existing standard already forbids the worst waste — procedure prose in a description, a
`Not for:` restated in `when_to_use` — and a prior diet recovered ~5,500 characters by
enforcing exactly that. What it does **not** question is its own uniformity: it requires every
skill to carry a leading concept, verbatim trigger phrases, and a routing boundary
(`sk-trigger-position`, `sk-no-boundary`), as if every skill were equally likely to be selected
by the model from prose.

**None of them are.** These skills are operated by typed command — `/docs:align`,
`/specs:apply`. The description exists so the *model* can decide to fire a skill; when the
human types the command, that decision already happened and the description bought nothing.
Worse, the stage skills are invoked **by name from a conductor's body**, so their descriptions
are never read for routing by anyone, ever.

A note on evidence: the session that produced this spec observed the *installed* plugin's
skill listing rendering 11 of its skills with the name alone and no description — descriptions
that were written, cap-conformant, and structurally identical to ones that did render. That
observation is against the installed build (30 skills, nested `plan-`/`backlog-` names), not
against this tree (28, flat names), and the mechanism was never determined, so it is recorded
as a prompt for this work rather than as a measurement supporting it. The measurement above
stands on its own.

## Proposal

Split the surface by how a skill is actually reached, and spend description budget only where
routing genuinely happens.

The line is one the architecture already drew — `CLAUDE.md` describes the plugin as a set of
entry points plus *"a stage of one of these eight invokes, or a per-item capture tool"*. That
yields three routing classes:

1. **Stages** — invoked by a conductor, by name, from its body. The description is never read
   for routing. Dead weight, in full.
2. **Entry points** — the align matrix and the plan cycle. Always typed as a command; the
   wrapper is the interface the human sees.
3. **Capture tools** — spoken mid-conversation ("anota isso", "põe esse termo no glossário").

Earlier drafts of this spec kept class 3 on a full description as a "Tier A" of five. **That
exemption is withdrawn: all 28 skills are Tier B.** The five capture tools keep a stub like
everything else. They do not go dark — a stub stays in context and `user-invocable: false`
keeps Claude able to invoke from it — but they route from ~74 characters instead of ~1,066.
That is the deliberate trade, taken with the eval that would have measured it dropped
(`## Open Decisions`).

**Tier B (all 28)** — a one-line stub, **the command wrapper's `description` verbatim**. Those
strings already exist, are already concise (~74 chars), and are already human-reviewed for the
`/` menu. Reusing them creates the invariant `wrapper.description ≡ skill.description`, so a
skill carries one string to maintain instead of two that can drift apart.

**Tier A survives as a mechanism, not as membership.** `skills.py` ships into target repos
whose surfaces are genuinely mixed, and a prose-routed skill there still needs its triggers and
its boundary. The `routing:` declaration and the tier-scoped checks are built here and exercised
here at `direct`; `inferred` is what a target repo declares.

`when_to_use` is dropped on all 28 — a Claude-Code-only extension whose remaining content is a
restatement of the description's first clause.

Because a Tier B stub **is** its wrapper's description byte-for-byte, the skill side collapses
to exactly the wrapper total:

| | today | after | cut |
| --- | ---: | ---: | ---: |
| 28 skill `description` | 25,875 | 2,069 | 92% |
| 28 skill `when_to_use` | 2,761 | 0 | 100% |
| skill-side subtotal | 28,636 | 2,069 | **93%** |
| wrappers (unchanged) | 2,069 | 2,069 | — |
| **total always-on** | **30,705** | **4,138** | **86.5%** |
| ~tokens | ~7,676 | ~1,035 | |

**~26,600 characters — roughly 6,600 tokens — off every session in every repo that installs
the plugin.** Nothing changes in what the user sees when they type `/`.

### The gate that may make this spec unnecessary

Claude Code has since **merged custom commands into skills**: a `commands/deploy.md` and a
`skills/deploy/SKILL.md` "both create `/deploy` and work the same way". If a command body can
also reach a bundled reference file — `${CLAUDE_PLUGIN_ROOT}` is documented to resolve in
*"Skill and agent content, anywhere the placeholder appears"*, but `commands/**` is not named
explicitly — then the 28 skill/wrapper pairs can collapse into 28 single command files, taking
always-on to 2,069 and deleting the duplication that created the tier problem in the first
place.

That collapse is **its own spec**, not this one: it is a structural migration whose revert is a
migration, where this spec's revert is `git revert` on frontmatter. But it is cheap to find out
which spec should run, so **task 0.2 spikes the premise first** and branches:

- **spike PASSES** → this spec is abandoned (`/specs:archive`), the collapse spec opens, and no
  throwaway stub is ever written.
- **spike FAILS** → this spec continues at task 1.1 and banks the 86.5%.

## Out of Scope

- **The collapse of skills into `commands/**`.** Its own spec, opened only if task 0.2's spike
  passes. Reasoned about here (`## Proposal`, `## Alternatives Considered`) and decided by a
  measurement, never folded in — this spec's whole risk profile is "frontmatter only".
- **Changing the invocation flags** — `disable-model-invocation: true`, dropping
  `user-invocable: false`. This is the lever that takes descriptions to *zero* rather than to a
  stub, and it is deliberately deferred: while the wrappers exist it surfaces 28 duplicate `/`
  entries, so it only pays off inside the collapse. Recorded in `## Problem` so the next spec
  inherits the finding.
- **The command wrappers.** Their `description` is the human-facing interface and the source
  of the Tier B stub; it is read, not rewritten. Their 2,069 characters stay.
- **Skill bodies and `references/`.** Load-on-invocation, already governed by `sk-body-length`.
  Not touched.
- **Renaming or merging skills.** The surface stays 28 skills and 28 wrappers. Cutting the
  *number* of skills is a different argument with different evidence.
- **The per-skill caps themselves** (1,536 `sk-metadata-cap`, 1,024 `sk-description-portable`).
  They stay as written; this spec changes what fills them, not their height.
- **The installed-build divergence.** This tree is 28 flat-named skills at `specs 2.0.0`; the
  build loaded in the authoring session was 30 nested-named. Reconciling them is not this
  spec's job — but see `## Risks`.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/automation/context-budget.md` — **revised, not created.** This is the
  first-class item. The standard today mandates a uniform three-part description for every
  skill; the tier policy contradicts that for every skill on this surface. It gains a §Tiers
  section, loses the implication that triggers and a boundary are universal, carries the
  compression recipe as guidance for `inferred` skills, and has its `when_to_use` paragraph
  reduced to "do not use it". Its `authority: background` and its graduation condition are
  re-stated against the new measurement.

### Tooling that must change with it (not standards — no doc promised)

- `plugins/claude-quenching/assets/bin/skills.py` — `sk-trigger-position` and `sk-no-boundary`
  are `warn` findings that fire when a description quotes no trigger phrase or omits
  `Not for:`. Both are **true of every Tier B stub by design**, so without tier-awareness this
  spec lands 56 new warnings and makes `lint` useless. The linter must learn the tier and
  scope both checks to `inferred`. `DEFAULT_CEILING` (36,503) is also revised — from the
  post-change measurement, per the standard's own "revised only from a measurement" rule.
- `plugins/claude-quenching/assets/templates/automation/skill.md` — the mold that teaches a
  new skill's frontmatter; it must teach the tier declaration.

### Skills whose doctrine teaches the old rule

- `quenching-skill-new` + `references/doctrine.md` — instructs authors to put triggers in the
  second sentence so truncation cannot eat them. Correct for `inferred`, wrong for `direct`.
- `quenching-skill-align` and `quenching-skill-align-and-update` — the sweep and the body
  audit; both judge descriptions against the doctrine they cite.

### Surface edited but owning no contract

- 28 × `plugins/claude-quenching/skills/*/SKILL.md` — frontmatter only.
- `plugins/claude-quenching/README.md` §Cost model — states the thirty fit under the cap; must
  speak of the **sum** and of the tiers, and its skill count is stale.

## Validation

Every claim in this spec is mechanically checkable; none of it rests on reading prose.

- **The spike is decisive either way** — task 0.2 produces a yes/no on whether a command body
  resolves `${CLAUDE_PLUGIN_ROOT}`, carries `allowed-tools`, and can be invoked by a conductor.
  A partial or ambiguous result counts as FAIL and this spec continues; the collapse spec does
  not open on a maybe.
- **The saving is real** — `skills.py --root plugins/claude-quenching budget --json` before and
  after. Baseline is 30,705 characters / ~7,676 tokens; the target is ≤ 4,300 total always-on.
  The instrument counts parsed frontmatter, which is the standard's own requirement.
- **Nothing became non-conformant** — `skills.py --root plugins/claude-quenching lint` exits 0
  with no new finding code. Specifically `sk-trigger-position` and `sk-no-boundary` must not
  fire on a Tier B stub, and `sk-no-description` must not fire at all.
- **The wrapper invariant holds** — for all 28 skills, the skill `description` equals its
  wrapper's `description` byte-for-byte. Checked by script, not by eye.
- **The bundle still passes** — `okf-validate.py assets/docs` and
  `okf-validate.py assets/specs/backlog --listing-root` both clean, since the standard doc is
  edited in `docs/` and the payload is untouched.
- **Version lockstep** — if `skills.py` changes, `VERSION`, `plugin.json`, the marketplace
  manifest, and both other shipped scripts stay in step per `CLAUDE.md` §Releasing.

## Design

### The spike and its branch

Task 0.2 answers three questions against a throwaway command file in this plugin, in this
order, stopping at the first NO:

1. Does `${CLAUDE_PLUGIN_ROOT}` substitute inside a `commands/*.md` body? The docs grant
   substitution to "Skill and agent content" and state that commands are now skills, but they
   do not name `commands/**` in the substitution table. This is the load-bearing unknown: every
   one of the 28 skills cites at least one `references/*.md`, so without a portable absolute
   path a command file cannot replace a skill.
2. Does a command file honour `allowed-tools` frontmatter? The docs say commands "support the
   same frontmatter"; the sweeps depend on it.
3. Can a conductor invoke a command by name via the Skill tool, the way it invokes a stage
   skill today? Five conductors depend on this.

Three YES → the collapse is viable and this spec is abandoned in its favour. Anything else →
this spec proceeds. The spike writes nothing outside its throwaway file and is reverted whatever
the answer.

### How a skill declares its tier

The linter cannot guess the tier, and it must not: `skills.py` ships into target repos, so it
may not carry a hard-coded list of this plugin's skills. The tier is **declared**, in
frontmatter:

```yaml
routing: direct     # reached by a typed command, or named by a conductor's body
routing: inferred   # the model must decide from prose — the description is load-bearing
```

**Absent means `inferred`.** That default is what keeps the change safe for every repo that
already installed the plugin: a skill that says nothing keeps today's behavior and today's
checks. Only an explicit `routing: direct` relaxes anything. The field is a declaration an
author makes on purpose, and it is greppable — which the alternatives (inferring the tier from
description length, or from whether a wrapper exists) are not, and both of those would silently
reclassify a skill as a side effect of an unrelated edit.

Keying the tier off Claude Code's own `disable-model-invocation` instead was considered and
does not work here: this plugin cannot set that flag while the wrappers exist (`## Problem`),
so every skill would classify as `inferred` and the warnings would fire anyway.

### What each check does with it

| Check | `inferred` | `direct` |
| --- | --- | --- |
| `sk-no-description` | error | error (a stub is still a description) |
| `sk-metadata-cap` (1,536) | error | error |
| `sk-description-portable` (1,024) | warn | warn |
| `sk-trigger-position` | warn | **not applicable** |
| `sk-no-boundary` | warn | **not applicable** |

A new `sk-wrapper-drift` (warn) fires when a `routing: direct` skill's description differs from
its wrapper's — the invariant made mechanical, so the two strings cannot rot apart unnoticed.

### The Tier B stub

The wrapper's `description`, verbatim. Not paraphrased — copied, so `sk-wrapper-drift` can
check it. `when_to_use` deleted. Median stub ~74 characters, against a median 1,066 today.
All 28 skills take one.

### The compression recipe, for `inferred` skills elsewhere

No skill on this surface is `inferred`, so nothing here applies the recipe — it ships as
doctrine in the standard (task 4.1) for target repos that do have prose-routed skills. A
description exists to let a reader predict **when it fires and what exists when it finishes**:

1. **Cut the scaffold.** `Use when the user asks to` plus the quoting apparatus, ~40 chars
   each, carries no signal.
2. **Cut the mechanism.** "updates the folder's `index.md`, appends a `log.md` entry, and
   self-checks" — the body teaches this on invocation.
3. **Cut the dead boundaries.** A `Not for: ... -> <direct skill>` disambiguates against
   something that no longer competes for inferred routing. Only inferred-vs-inferred boundaries
   survive.
4. **Keep every trigger phrase.** Which triggers earn their place is settled on measured
   should-trigger / should-not-trigger rates via `quenching-skill-eval`, never by taste.
5. **Keep the mechanism fragments that discriminate.** "zero interrogation, untriaged is valid"
   separates fast capture from the plan cycle; "never implements" separates explore from apply.
   These read as mechanism but do routing work, and cutting them by rule would be the
   predictable failure of applying rule 2 blindly.

### Why this order

Tasks are phased so the decisive question is asked first and each phase is independently
revertible. The spike runs before anything is edited, so a passing spike costs one throwaway
file instead of 28 stubs. The tier declaration and the linter change land **before** any
description is cut, otherwise the tree spends a commit in a state where `lint` is noise.

## Alternatives Considered

- **A uniform, more aggressive trim — no tiers.** Enforce the existing standard harder on all
  28. Rejected: it recovers maybe 6,000 of the 26,600 characters, because the floor is the
  concept + triggers + boundary the standard requires of *every* skill. It keeps paying for
  trigger phrases on skills only ever reached by a typed command or by a conductor naming them.
  It optimizes the text and leaves the wrong question unasked.
- **Keep a Tier A of five capture tools.** This spec's own earlier draft: `quenching-docs-add`,
  `docs-learn`, `docs-define`, `specs-capture`, `specs-explore` keep a compressed full
  description because they are reached by *speaking* rather than typing. Withdrawn by decision:
  the residual saving (1,290 vs ~370 chars) does not justify a second policy, a second lint
  path, and an eval gate, when a stub is still in context and still model-invocable. The recipe
  that would have compressed them survives as doctrine for target repos.
- **Change the invocation flags instead of the strings.** `disable-model-invocation: true`
  removes the description from context entirely — a 100% skill-side cut against this spec's
  93%. Rejected *here* and deferred to the collapse: it makes all 28 skills typable, doubling
  the `/` menu while the wrappers still exist. It is the right answer to a question this spec
  is not asking.
- **Collapse the pairs into single command files.** Strictly better than this spec if it works
  — always-on 2,069, one file per entry point, and the `wrapper == skill` duplication gone
  rather than made mechanical. Not rejected: promoted to its own spec and gated on task 0.2.
  This supersedes the earlier "one router skill per front" idea, which added a hop on the
  common path to save descriptions the collapse removes outright.
- **Raise the ceiling.** The standard's 36,503 is a measured baseline, and 30,705 sits under
  it. Rejected: it treats the ceiling as the goal. The ceiling was set from one surface's
  pre-diet measurement and permits regression back to it; the surface being under it is not
  evidence the surface is cheap.
- **Delete `when_to_use` only.** Recovers 2,761 characters for near-zero risk, and is a
  genuinely good change. Rejected as *the* answer because it is 10% of the available saving —
  it is folded in here as part of task 1 rather than standing alone.
- **Infer the tier instead of declaring it** (from description length, or from whether a
  wrapper exists). Rejected in `## Design`: it makes an unrelated edit silently reclassify a
  skill.

## Open Decisions

- **Does the spike pass?** The one decision that determines whether this spec is built at all.
  Settled by task 0.2, before any edit. Ambiguity counts as FAIL.
- **The field name and its values.** `routing: direct | inferred` reads well and defaults
  safely, but it is a new frontmatter key on a surface that also ships into other repos. If a
  future Agent Skills revision claims `routing`, this collides. Spellings considered and not
  chosen: `tier: a|b` (opaque), `discovery:` (overloaded with the `discover` subcommand).
- **The new `DEFAULT_CEILING`.** Must come from the post-change measurement, per the standard's
  own rule. ~4,100 is the projection; the number written into `skills.py` is whatever
  `budget --json` reports once tasks 1-3 have landed, not this estimate.
- **Whether the standard graduates.** It is `authority: background`, and its graduation
  condition is `skills.py budget` having run on this plugin plus two adopting repos. This spec
  gives it a second, much larger measurement on one surface — which is not the stated
  condition. It stays `background` unless someone argues otherwise explicitly.

**Resolved during refinement (2026-07-26):**

- ~~Tier A membership.~~ **None.** All 28 skills are Tier B; the five capture tools lose their
  exemption. Tier A remains a mechanism for target repos.
- ~~Whether to eval the capture tools' trigger rates.~~ **No.** The eval gate is dropped: prose
  routing is no longer a promise this surface makes, so measuring it measures something the
  spec has decided not to optimize. No baseline is captured — see `## Risks`.

## Risks

- **The five capture tools route from a weaker string.** Not "stop being reachable": a stub
  stays in context and `user-invocable: false` keeps Claude able to invoke from it, so
  "anota isso" matches ~74 characters instead of ~1,066. Whether that is enough is **unmeasured
  by choice** — the eval that would have told us was dropped. The honest residual: this is the
  one user-visible behavior change in the spec, it is reversible per skill by restoring one
  description, and nobody will notice it from a lint run.
- **No before/after baseline for trigger rates.** Dropping the eval means a later regression
  has nothing to compare against. Accepted; recoverable by evaluating the pre-change
  descriptions from git history if the question is ever reopened.
- **A passing spike makes this spec's stubs throwaway.** Mitigated structurally by running the
  spike at task 0.2, before the first stub is written — the cost of a pass is one reverted
  file, not 28 edits.
- **The `wrapper == skill` invariant couples two files.** Editing a wrapper's description now
  silently changes a skill's routing text. `sk-wrapper-drift` catches divergence but not a
  synchronized change nobody thought through. Accepted: one string that must agree beats two
  that may disagree.
- **`skills.py` ships into target repos.** A repo running an older copy will not know
  `routing:` and will emit `sk-trigger-position` / `sk-no-boundary` on every Tier B skill of an
  upgraded plugin — noise, not breakage, and the reason `skills.py --version` is in the
  lockstep set. Repos upgrade the tool with the plugin.
- **The installed build is not this tree.** Authoring measured 28 flat-named skills at
  `specs 2.0.0`; the loaded plugin was 30 with nested `plan-`/`backlog-` names. Anyone applying
  this spec against the *installed* surface will find a different skill count and different
  names. Task 0.1 re-runs `budget` and reconciles before anything is edited — the spec's
  numbers are a baseline to re-confirm, never to trust blind.
- **Cheap to reverse.** Every edit is frontmatter. `git revert` restores the old surface with no
  migration, no data, and no target-repo state to unwind.

## Tasks

Phased so the decisive question is asked first and each phase is independently revertible. `PY`
below is whatever real interpreter the applying machine has — `python3` on Linux, but
`C:/Users/holet/AppData/Local/Programs/Python/Python312/python.exe` on the Windows box where
this spec was authored, since there `python3`/`py` are the Windows Store stub. Resolve it once
at task 0.1 rather than trusting either spelling. `SK` is
`plugins/claude-quenching/assets/bin/skills.py`, `--root` is `plugins/claude-quenching`.

### 0. Reconcile the baseline, then decide whether to build this at all

- [ ] 0.1 Re-run the measurement and reconcile the surface against this spec before editing
      anything. Confirm the skill count, the flat `quenching-specs-*` names, and the 30,705
      baseline. If the applying tree is the nested 30-skill build instead, correct the counts
      in `## Problem` and `## Proposal` before proceeding — do not map them by guess.
      verify: `$PY $SK --root plugins/claude-quenching budget --json`
- [ ] 0.2 **The gate.** Spike the three questions in `## Design` §The spike and its branch
      against one throwaway command file: does `${CLAUDE_PLUGIN_ROOT}` substitute in a
      `commands/*.md` body, does a command honour `allowed-tools`, can a conductor invoke a
      command by name via the Skill tool. Revert the throwaway file either way.
      **Three YES → stop here**: abandon this spec via `/specs:archive`, and open the collapse
      spec. **Anything else → continue at 1.1.** An ambiguous result is a FAIL.

### 1. The safe cut — no tiering yet

- [ ] 1.1 Delete `when_to_use` from all 28 `SKILL.md` frontmatters. It is a Claude-Code-only
      extension and its content restates the description's first clause; the standard already
      forbids it carrying the boundary. Recovers 2,761 characters on its own.
      files: plugins/claude-quenching/skills/*/SKILL.md
      verify: `$PY $SK --root plugins/claude-quenching lint --json`
- [ ] 1.2 Cut procedure prose from every description that still carries it — the step order,
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
      `sk-no-boundary` to `inferred` skills only. Without this, task 3 lands 56 warnings and
      makes `lint` useless.
      files: plugins/claude-quenching/assets/bin/skills.py
      verify: `$PY $SK --root plugins/claude-quenching lint --json`
- [ ] 2.3 Add `sk-wrapper-drift` (warn): a `routing: direct` skill whose `description` differs
      from its wrapper's. This makes the Tier B invariant mechanical instead of aspirational.
      files: plugins/claude-quenching/assets/bin/skills.py
      verify: `$PY $SK --root plugins/claude-quenching lint --json`
- [ ] 2.4 Version lockstep per `CLAUDE.md` §Releasing — `skills.py` changed, so `VERSION`,
      `plugin.json`, the marketplace manifest, and the other shipped scripts move together.
      files: plugins/claude-quenching/VERSION, plugins/claude-quenching/.claude-plugin/plugin.json, .claude-plugin/marketplace.json

### 3. Tier B — all 28 stubs

- [ ] 3.1 Stamp `routing: direct` on all 28 skills and replace each description with its
      command wrapper's `description`, copied verbatim (not paraphrased, so 2.3 can check it).
      This includes the five capture tools, which no longer hold an exemption. Expected
      25,875 -> 2,069 characters.
      files: plugins/claude-quenching/skills/*/SKILL.md
      verify: `$PY $SK --root plugins/claude-quenching lint --json`

### 4. The doctrine that teaches it

- [ ] 4.1 Revise the standard `docs/standards/automation/context-budget.md` — the first-class
      item. Add a §Tiers section, stop implying triggers and a boundary are universal, carry the
      compression recipe as guidance for `inferred` skills, reduce the `when_to_use` paragraph
      to "do not use it", and restate the graduation condition against the new measurement.
      Keep `authority: background` unless argued otherwise.
      files: docs/standards/automation/context-budget.md
- [ ] 4.2 Update the new `DEFAULT_CEILING` in `skills.py` from the measurement task 5.1
      produces — never from this spec's ~4,100 projection.
      files: plugins/claude-quenching/assets/bin/skills.py
- [ ] 4.3 [P] Rewrite `README.md` §Cost model: it claims the thirty fit under the cap, which
      optimizes per-skill height instead of the sum, and its skill count is stale.
      files: plugins/claude-quenching/README.md
- [ ] 4.4 [P] Teach the tier in `quenching-skill-new` and its `references/doctrine.md`, which
      today tells every author to put triggers in the second sentence against truncation —
      right for `inferred`, wrong for `direct`. Minting a skill must now ask which tier it is.
      files: plugins/claude-quenching/skills/quenching-skill-new/SKILL.md, plugins/claude-quenching/skills/quenching-skill-new/references/doctrine.md
- [ ] 4.5 [P] Teach the tier to the two sweeps that judge descriptions against that doctrine —
      `quenching-skill-align` (the migration) and `quenching-skill-align-and-update` (the body
      audit). Neither may report a Tier B stub as a defect.
      files: plugins/claude-quenching/skills/quenching-skill-align/SKILL.md, plugins/claude-quenching/skills/quenching-skill-align-and-update/SKILL.md

### 5. Prove it

- [ ] 5.1 Measure the result and confirm the target: `lint` exits 0 with no new code, `budget`
      reports total always-on at or under 4,300 characters against the revised ceiling.
      verify: `$PY $SK --root plugins/claude-quenching lint --json && $PY $SK --root plugins/claude-quenching budget --json`
- [ ] 5.2 Script-check the Tier B invariant: for all 28, skill `description` equals wrapper
      `description` byte-for-byte. By script, never by eye.
      verify: `$PY $SK --root plugins/claude-quenching lint --json`
- [ ] 5.3 [P] Confirm the shipped payload is untouched and still conformant.
      verify: `$PY plugins/claude-quenching/assets/hooks/okf-validate.py plugins/claude-quenching/assets/docs && $PY plugins/claude-quenching/assets/hooks/okf-validate.py plugins/claude-quenching/assets/specs/backlog --listing-root`
