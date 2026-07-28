---
slug: instrument-and-extend-skill-front
title: Capacidades estrategicas no front .claude/
verification: per-section
approved: 2026-07-27
branch:
  base: main
  work: plan/instrument-and-extend-skill-front
---

# Capacidades estrategicas no front .claude/

## Problem

This spec's first revision found the `.claude/` front uninstrumented and fixed that: the
front now has its tool (`skills.py` — `lint`/`doctor`/`registry`/`budget`/`selftest`, `sk-*`
codes), the three skills branch on data, the surface went on a measured diet, the standards
exist, and `/skill:eval` measures whether a skill teaches anything. That work shipped
(sections 1–5 of the previous revision) and is not re-planned here.

What replaced it as the gap is the layer above: **strategic capability use**. The
2026-07-27 research pass (hookify, plugin-dev, agent-sdk-dev, the official capability docs)
landed the execution-profile doctrine and its surface in commit `44e09b8` —
`skill-new/capabilities.md` (the priced levers: `context: fork`, model/effort pins, the
delegation test, the hook scope/handler ladders, the invocation-surface budget controls),
`/skill:new` step 4, the two new mints `/skill:agent:new` + `/skill:hook:new` with their
molds, the `agents.md`/`hooks.md` standards born `authority: background`, and `skills.py`'s
new codes (`sk-fork-gate`, `sk-profile-value`, and doctor's report-only wider surface).

But the layer is new-born, and the distance between "the doctrine exists" and "the doctrine
is proven and closed" is exactly this front's founding lesson — *a rule with no verifier
decays*:

- **Nothing has measured it.** Neither new mint has an eval; the doctrine's routing and its
  teaching value are hypotheses again.
- **The plugin does not eat its own cooking.** Its own commands were authored before the
  profile doctrine existed; no one has audited them under it, so the doctrine's first real
  application has not happened.
- **Two mechanical blind spots.** `skills.py`'s minimal frontmatter parser skips nested
  blocks, so a frontmatter `hooks:` block — the ladder's narrowest rung — is invisible to
  `lint`; and `budget` ignores `agents/*.md` descriptions, which are always-on context by
  the same rule as a command's.
- **The ceiling is stale.** `budget` reads 9,868 characters against the 2,083 ceiling — the
  crossing signal is firing with nothing to catch it, because the surface is still shrinking
  under the in-flight `specs-flow-consolidation` fold.
- **The original tail is unresolved.** `/skill:package` (section 7 of the first revision)
  was never built or dismissed, and the two new standards need their graduation evidence.

## Proposal

- **Prove the layer**: run `/skill:eval` on both new mints, tune on the measured hit rates,
  and extend the functional checks so the two commands' routing is proven in a fresh
  process like the rest of the surface.
- **Apply the layer to its own author**: a read-only profile audit of the plugin's own
  commands under `capabilities.md`, then one confirmed pass applying only the levers with a
  stated buy — the doctrine's first real application, dogfooded.
- **Close the mechanical blind spots**: `lint` learns to read frontmatter `hooks:` blocks;
  `budget` learns to count agent descriptions; the ceiling is re-measured and re-set once
  the fold lands.
- **Resolve the tail**: decide `/skill:package` from a real packaging run or dismiss it in
  writing; graduate `agents.md`/`hooks.md` on evidence, not on time passing.
- **Release**: after the consolidation spec's manual/README rewrites land, verify the
  enumerations carry the new surface, then bump the version lockstep.

## Out of Scope

- **Rewriting any command body to satisfy the doctrine.** Authoring stays human-gated;
  findings route to `/skill:new`, as always.
- **The consolidation spec's own files while it is in flight** — the align fold (its tasks
  4.3/4.4), the manuals/CLAUDE.md/README rewrites (5.4/5.5), the workspace migration (5.6).
  This spec only sequences after them and verifies residue; two specs editing one file is
  how a branch stops being reviewable.
- **A hookify-style runtime rule engine.** The plugin teaches *wiring* scoped hooks; it
  ships no always-on engine of its own — that is the exact tax the doctrine exists to
  prevent.
- **A skill-search/index command for large surfaces** — still answers a problem no adopting
  repo has; `skills.py budget` will say when that changes.
- **Porting profile checks to the `docs/`/`specs/` fronts** — the capability layer proves
  itself on this front first, same rule as the first revision.
- **Output styles, MCP configuration, statusline, `.claude/workflows/`** — still deferred;
  inventoried only if `agents/` + hooks prove the report-only pattern worth widening.

## Impact

### Standards this spec will write into docs/standards/

- docs/standards/automation/context-budget.md
- docs/standards/automation/agents.md
- docs/standards/automation/hooks.md

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/skills.py` — the two mechanical gaps (frontmatter hooks,
  agent descriptions in `budget`), the re-set ceiling.
- `plugins/quenching/assets/bin/functional-checks.sh` — one routing probe per new mint.
- `plugins/quenching/commands/**` — only the levers the profile audit confirms, one pass.
- `plugins/quenching/assets/evals/skill/agent/new/`, `assets/evals/skill/hook/new/` — the
  eval case sets and their first runs.
- `plugins/quenching/README.md`, the three `QUENCHING.md` manuals — residue verification
  only, after consolidation 5.4/5.5.
- Release lockstep: `VERSION`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`,
  the `VERSION` constant in `skills.py`/`specs.py`/`okf-validate.py`.

## Validation

- `python3 assets/bin/skills.py selftest` — PASS, including the frontmatter-hooks cases
  task 2.1 adds.
- `python3 assets/bin/skills.py --root . doctor --json` and `lint --json` — exit 0 over the
  post-fold surface.
- `python3 assets/bin/skills.py --root . budget --json` — exit 0 against the re-set ceiling,
  and the ceiling's number is one a run produced, stated in `context-budget.md`.
- Both new mints have committed `evals.json` + `grading.json` + `benchmark.json`, and each
  delta is stated as a number — zero reported as zero.
- `./assets/bin/functional-checks.sh` — exit 0, including the new-mint probes, with the
  probes sandboxed (Handoff: the two known failure modes).
- `python3 assets/hooks/okf-validate.py ../../docs` — 0 errors.
- All version sources agree (`--version` on the three scripts, `VERSION`, both manifests).

## Design

Carried from the first revision, still binding:

1. **The tool owns the thresholds; doctrine cites codes.** New rules enter as `sk-*` codes
   or they decay.
2. **Evaluation is on-demand, never a sweep stage** — a converging loop must not spawn
   subagents.
3. **`budget` reports; it never gates.**

New with the capability layer:

4. **The execution profile is authored and priced.** Default = all levers off; each
   departure enters the mint's plan with its stated buy. `capabilities.md` is the single
   owner; standards and manuals cite it.
5. **The wider surface is report-only.** `doctor` names `agents/`/hooks findings and routes
   them to the mints; the sweep's write set never grows. Auto-fixing `settings.json` stays
   out until a real broken-wiring case argues for it.
6. **Two mints, not one widened `/skill:new`.** An agent definition and a hook are
   different artifact contracts (voice, molds, verification) and the path is the identity —
   three entry points route better than one overloaded one.
7. **Frontmatter `hooks:` is the ladder's narrowest rung**, so making it visible to `lint`
   (task 2.1) parses only the shapes the mold emits — the minimal parser grows a case, not
   a YAML implementation; anything else stays a warn, fail-open.
8. **The ceiling is re-set only from a measurement**, and only once the surface stops
   moving (after the fold) — a number set mid-shrink can never fire honestly.

## Alternatives Considered

- **Fold agent/hook minting into `/skill:new` as modes** — rejected: a technique is a
  parameter of a verb, but these are different *objects* with different contracts; and one
  three-headed description routes worse than three bounded ones.
- **Ship a hookify-style dynamic rule engine** — rejected: its economics are right (zero
  tokens on no-match) and are adopted as doctrine, but an always-on engine process on every
  tool call is the tax this plugin refuses; targets get scoped wiring instead.
- **Teach `lint` to judge fork-worthiness** — rejected: only the `fork` + `AskUserQuestion`
  incoherence is mechanical (`sk-fork-gate`); "should this command fork" is a claim about
  behaviour, and moving it into the tool would move the anti-fabrication boundary.

## Open Decisions

- **`/skill:package`'s fate** — decided by task 4.1 from a real packaging run of this
  repo's own surface, not from taste.
- **Whether `/skill:eval` gains a profile arm** (measuring a fork's overhead, or a hook's
  cost claim, with/without) — decided after 1.1/1.2 show what the current two arms already
  reveal about profile choices.
- **The re-set ceiling's number** — produced by task 2.3's measurement after the fold; not
  guessable now.
- **Whether the report-only inventory widens** to `.claude/workflows/`/output styles —
  decided by whether `agents/` + hooks findings actually get acted on in an adopting repo.
- **Whether the doctrine audit ever reads `benchmark.json` instead of the body** — carried
  from the first revision; still waiting on committed benchmarks to exist (1.1/1.2 create
  the first two).

## Risks

- **The concurrent consolidation session.** Its remaining tasks own the align fold, the
  manuals, CLAUDE.md/README and the workspace migration. Mitigation: this spec's tasks name
  disjoint files, and 1.4/2.3/3.3/5.1 are explicitly sequenced after the consolidation
  tasks they depend on — the Handoff names the dependency per task.
- **The profile audit over-applies levers.** A doctrine fresh from research invites
  enthusiasm. Mitigation: 3.1 is read-only and reports the *buy* per lever; 3.2 applies
  only confirmed rows under one OK; the two standing never-rules (no `context: fork` on
  gating sweeps, no haiku on import-memory classification/executors) are invariants, not
  rows.
- **Parser creep in `skills.py`.** Frontmatter hooks need nested parsing. Mitigation:
  design decision 7 — parse the mold's shapes, warn on anything else, keep the parser
  deliberately minimal and self-contained.
- **Eval cost.** Each `/skill:eval` run spawns 2 subagents per case. ACCEPTED — it is the
  price of the front's own founding rule, the human authorizes the spend at the eval's plan
  gate, and the artifacts are committed so the runs are not repeated idly.

## Handoff

State of play (2026-07-27, after task 3.1): **sections 1 and 2 are done and green.**
`specs-flow-consolidation` has landed (archived `outcome: done`, merged to `main`), so the
sequencing dependencies in 3.3 and 5.1 are satisfied and nothing here is blocked on another
session. Work is on branch `plan/instrument-and-extend-skill-front`, cut from `main`. The
doctrine's single owner is `plugins/quenching/assets/references/skill-new/capabilities.md`; the
standards are `docs/standards/automation/{skills,agents,hooks,context-budget}.md`.
`budget` now reads 11,565 chars against the re-set ceiling of 11,565 (`9c1e42c`).

**The six rows task 3.2 stands on**, from 3.1's audit — blast-radius order, each with its buy:

1. `/specs:align` grants bare `Bash` *alongside* `Bash(python3:*)`/`Bash(py:*)`, so the scoped
   grants are dead weight. Scope it, or state the reason.
2. Four bare-`Bash` grants state no reason: `/docs:documentation:build`,
   `/docs:glossary-backfill`, `/docs:harness`, `/docs:import-memory`.
3. Five **inline** `effort:` pins (`/docs:define`, `/docs:status`, `/specs:status`,
   `/specs:create` = `low`; `/docs:glossary-backfill` = `medium`) were never priced against
   `capabilities.md` §The cache trap — an inline pin invalidates the whole session prompt cache.
   Drop them, or write the cost into README's model-policy table.
4. Frontmatter `hooks:` running `okf-validate.py` on `/docs:add`, `/docs:learn`, `/docs:define`
   — scope-ladder rung 1, and the surface currently has **zero** instances of the block task
   2.1 taught `lint` to read.
5. `/specs:continue` renders `specs.py next --front --json` at render time, converting its only
   tool call into text. **Blocked on an unproven fact**: `functional-checks.sh` proves
   `${CLAUDE_PLUGIN_ROOT}` substitutes in a *body*, never in a `!` line — prove that first, and
   the same block is why the three aligns' probes stay on hold.
6. `/skill:align` §7 gains a **collection-only** read-only `Task` (not granted today); every
   doctrine verdict stays with the orchestrator.

**Nothing is fork-eligible** — all 24 commands either gate mid-flow or must land their report
where the OK follows, and `/docs:status` + `/specs:status` say so in their own bodies.
`disable-model-invocation`/`user-invocable` are forbidden by CLAUDE.md's default-invocation rule;
`paths:` does not apply because every command is generic-axis, not domain-bound.

**Two things 3.2 must not undo.** `/skill:agent:new`'s intent-phrased routing was BORROWED from
the target repo — without `docs/standards/automation/agents.md` present, the phrase routed to
`/skill:new`. The trigger now on the description is what earns it, and probes d and e in
`functional-checks.sh` guard both mints: do not "shorten" either description without re-running
the suite. A `#` inside a frontmatter description is read as a YAML comment and silently
truncates it.

Facts an executor cannot derive: `functional-checks.sh` has two recorded failure modes — the
sandbox needs the repo's own `enabledPlugins` copied in, and check 3's probes create real specs
in the live workspace unless sandboxed. `skills.py parse_frontmatter` ignores indented lines
outside the `hooks:` case 2.1 added; `specs.py` has the identical defect, so this spec's own
nested `branch:` record reads back as null in `status --json` while being present in the file.

## Tasks

### 1. Prove the capability layer

- [x] 1.1 Run `/skill:eval` against `/skill:agent:new` — derive the cases from its branches
      (delegation-test reroute included), both arms, evidence-graded, artifacts committed
      files: plugins/quenching/assets/evals/skill/agent/new/
      verify: test -f plugins/quenching/assets/evals/skill/agent/new/evals.json
      commit: 2f0cff3
- [x] 1.2 Run `/skill:eval` against `/skill:hook:new` — the declining case is a session-wide
      hook request that must come back scoped
      files: plugins/quenching/assets/evals/skill/hook/new/
      verify: test -f plugins/quenching/assets/evals/skill/hook/new/evals.json
      commit: f5b49c7
- [x] 1.3 Fold the measured results back: description tuning only on hit rates (eval step
      7), body fixes via `/skill:new`; re-lint after every edit
      files: plugins/quenching/commands/skill/agent/new.md, plugins/quenching/commands/skill/hook/new.md
      verify: python3 assets/bin/skills.py lint commands/skill --json
      commit: 69ace04
- [x] 1.4 After consolidation 4.5 passes, add one sandboxed routing probe per new mint to
      the functional checks (Handoff: the two recorded failure modes)
      files: plugins/quenching/assets/bin/functional-checks.sh
      verify: cd plugins/quenching && ./assets/bin/functional-checks.sh
      commit: c959ec5

### 2. Close the mechanical blind spots

- [x] 2.1 Teach `skills.py lint` to read a frontmatter `hooks:` block (the mold's shape
      only) and apply the ladder codes to it; extend `selftest` with a covered and an
      uncovered case
      files: plugins/quenching/assets/bin/skills.py
      verify: python3 assets/bin/skills.py selftest
      commit: b1bd9b9
- [x] 2.2 Count `agents/*.md` descriptions in `budget` and record it in `docs/standards/automation/context-budget.md`
      files: plugins/quenching/assets/bin/skills.py, docs/standards/automation/context-budget.md
      verify: python3 assets/bin/skills.py --root . budget --json
      commit: eae7e43
- [x] 2.3 Post-fold, re-measure and re-set `DEFAULT_CEILING` + `docs/standards/automation/context-budget.md` §ceiling
      files: plugins/quenching/assets/bin/skills.py, docs/standards/automation/context-budget.md
      verify: python3 assets/bin/skills.py --root . budget --json
      commit: 9c1e42c

### 3. Apply the doctrine to its own author

- [x] 3.1 Read-only profile audit of every plugin command under `capabilities.md` — one
      commit: 88eae15
      report: command · lever · stated buy · verdict (apply / leave / forbidden-by-invariant)
- [x] 3.2 Apply the confirmed levers in one pass, one plan → one OK; the two standing
      never-rules are untouchable
      files: plugins/quenching/commands/
      verify: python3 assets/bin/skills.py --root . lint --json
      commit: 7ad7d9b
- [ ] 3.3 After consolidation 5.5, update the README model-policy rows for what 3.2 changed
      files: plugins/quenching/README.md

### 4. Resolve the original tail

- [ ] 4.1 Decide `/skill:package` by packaging this repo's own `.claude`-style surface once
      for real: mint the command from what the run required, or record the dismissal in
      this spec's Discoveries with the observed reason
- [ ] 4.2 Graduate `docs/standards/automation/agents.md` + `docs/standards/automation/hooks.md` to `current`
      when an adopting surface follows them — or record what the first real surface
      contradicted and amend
      files: docs/standards/automation/agents.md, docs/standards/automation/hooks.md
      verify: python3 assets/hooks/okf-validate.py ../../docs

### 5. Release

- [ ] 5.1 After consolidation 5.4/5.5, verify the three `QUENCHING.md` manuals, `CLAUDE.md`
      and `README.md` enumerate the two mints, `capabilities.md`, and the new `sk-*` codes;
      fix residue only
      files: plugins/quenching/assets/docs/QUENCHING.md, plugins/quenching/assets/specs/QUENCHING.md, plugins/quenching/assets/claude/QUENCHING.md
- [ ] 5.2 Bump the version lockstep — `VERSION`, both manifests, and the `VERSION` constant
      in all three scripts
      verify: python3 assets/bin/skills.py --version && python3 assets/bin/specs.py --version && python3 assets/hooks/okf-validate.py --version && cat VERSION

## Discoveries

- specs.py parse_frontmatter skips indented lines (l.499), so the nested branch/priority/merge records its own SCHEMA declares (l.171-186) parse to '' and status --json reports them null — the exact specs.py twin of the skills.py hooks: blind spot task 2.1 fixes
- skill/eval step 5 prescribes Task subagents for both arms, but a Task subagent inherits the session plugin registry — so the without-arm still lists the command it is defined by lacking, contradicting evaluation.md 'no path to its body'. Honest isolation needs a sandboxed claude -p with enabledPlugins present/absent, the pattern functional-checks.sh already uses
- assets/evals/specs/capture/ is stale twice over: the folder mirrors the retired /specs:capture path (now /specs:create) and its benchmark.json names a third retired skill, quenching-specs-backlog-add — eval artifacts do not follow a command rename automatically, which is the one property the mirrored-tree design claimed
- a trigger probe capped at --max-turns 3 reported two FALSE misses: both arms were still orienting with Bash when the cap cut them off (error_max_turns), and at --max-turns 8 both routed correctly — tuning on the truncated run would have removed a working trigger, which the contract forbids. functional-checks.sh check 3 probes at --max-turns 4 and carries the same risk (task 1.4)
- skills.py lint reports /skill:new with sk-trigger-position and /skill:eval with BOTH sk-trigger-position and sk-no-boundary — the two commands 1.3 routes body fixes to, and the one that measures routing, are themselves the least routable on the front (task 3.x territory)
- CLAUDE.md documents functional-checks.sh as '~5 min, 7 assertions'; task 1.4 took it to 9 assertions across 7 sandboxed sessions, so both numbers are now residue for task 5.1 to correct
- an intent-shaped routing probe grades the FIXTURE unless the fixture contains the subject the phrase names: 'audits our migrations' did not route in a bare scratch repo (the session challenged the premise — 'There are no migrations to audit' — and ended in success, not truncation), while the identical phrase routed twice in the eval fixture that carried a migration file
- /skill:agent:new's intent-phrased routing is borrowed, not earned: 'set up something that audits our migrations and reports back' routes to skill:agent:new only when the target repo already carries docs/standards/automation/agents.md — without it the same phrase routes to /skill:new (single-variable test, both runs subtype success). Task 1.1 measured that trigger 5/5 in a fixture that shipped agents.md, so the rate was fixture-assisted; every trigger the description carries names an artifact, none is intent-shaped, which is the gap 1.3 closed for /skill:hook:new
- sk-unscoped-bash's message offers 'or state the reason in the body' but the check never reads the body — /specs:execute, /specs:conclude and /docs:align each carry a 'Why Bash is unrestricted here' section and are warned anyway, so the finding cannot distinguish a priced grant from an unpriced one (5 of the 8 warned commands state nothing)
- README.md §Cost model still states the surface's always-on total as '30,705 characters to 2,083 (~7,676 to ~521 tokens), a 93% cut' — task 2.3 re-set the ceiling to 11,565 after the fold, so both the figure and the percentage are stale residue for task 5.1; a ceiling re-measurement has no checker that notices its own prose citations going out of date
