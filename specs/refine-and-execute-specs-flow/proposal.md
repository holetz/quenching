# Refino, rito minimo e execucao eficiente no front specs/

## Why

The `specs/` front is strong on structure and weak on **thinking** and **execution**. A critical
review of all twelve `quenching-specs-*` skills, the three references, and `specs.py` found three
structural holes plus five concrete defects.

**No refinement exists.** No skill ever attacks a plan. `quenching-specs-explore` is a stance with
no steps, no techniques, no stop condition, and no output artifact — so an exploration that
produced a comparison table and a recommendation dies in conversation context, which is exactly
what gets summarized away. `quenching-specs-plan-update` only reacts to an edit the human already
formulated. Nobody generates the questions. `quenching-specs-plan-propose` writes all three
artifacts in one pass under a guardrail that says *"prefer reasonable decisions to keep momentum"*,
so a plan reaches `applyReady` without anyone having disagreed with it. The optional `design.md`
compounds this: alternatives, risks, and open decisions have **no mandatory home**, so an absent
`design.md` cannot distinguish "we weighed alternatives and there were none" from "we never
thought about it".

**The minimum ritual is not minimum.** A 20-minute task costs three invocations and three gates
(`propose|from-claude` → `apply` → `archive`). `quenching-specs-plan-from-claude` requires the
plan to already be a file under `~/.claude/plans/`, which forces archaeology over something that
was on screen seconds ago, has no path for plan text pasted inline, and ends by *telling* the user
to run `/specs:plan:apply` instead of offering to chain. So for small work the front gets bypassed
entirely — and the branch and the OKF distillation, the only irreducible value of the ritual, are
lost. The three-artifact ceremony is the cost, not the value.

**`quenching-specs-plan-apply` does not verify, does not commit, and cannot delegate.** It is a
serial single-context loop that writes code and ticks a checkbox. It never runs the test suite,
has no per-task validation command, no retry loop, and no failure budget; it never commits, so N
tasks pile into one uncommitted blob and the branch it offered buys no per-task revert; and
`tasks.md` carries no execution metadata (`parse_tasks` extracts only `id`/`checked`/`text`), so
in a long plan the early artifacts fall out of the context window and no executor sub-agent could
be dispatched even if policy allowed it. The cost model permits fan-out for the cheap `docs/`
sweeps and forbids it for the one skill that burns the most context.

**Five concrete defects** found alongside the three holes:

1. `specs.py next` never emits a design action — `compute_next` goes from `proposal` straight to
   `tasks` — but `quenching-specs-plan-propose` §5a documents that it emits "write/delete design".
   An instruction for a state the tool cannot produce.
2. `specs.py validate` never inspects `design.md`. An unfilled scaffold (HTML comments only)
   survives forever, passes validate, and `applyReady` stays true. The "delete it if there is no
   decision" doctrine has zero enforcement.
3. `quenching-specs-plan-from-claude` requires confirmations at Steps 4 and 6 but does not carry
   `AskUserQuestion` in `allowed-tools` — every sibling does.
4. `quenching-specs-plan-apply` never commits.
5. `## Impact` is unparsed prose, so the declared blast radius is never checked against what apply
   actually wrote into `docs/standards/` — silent drift between plan and bundle.

## What Changes

- **A refinement skill exists.** `quenching-specs-plan-refine` (`/specs:plan:refine`) interrogates
  a plan's artifacts in four selectable modes — `interview`, `critic`, `premortem`,
  `alternatives` — one question at a time with an inline recommendation, accumulating answers and
  applying them in **one** edit at the end, with a declared stop condition.
- **Refinement is visible but never blocking.** `.specs.json` records `refined`, and
  `specs.py validate` emits `sp-unrefined` as a **warning** when a plan has `tasks.md` and no
  recorded refinement, so `/specs:status` surfaces it without gating apply.
- **The plan templates force the thinking.** `proposal.md` gains `## Out of Scope` and
  `## Validation`; `design.md` becomes required-with-explicit-fallback (`- none`) and gains
  `## Alternatives Considered` and `## Open Decisions`. Emptiness becomes a stated answer instead
  of an omission.
- **`## Impact` becomes machine-checkable.** The `docs/standards/` paths it declares are parsed,
  so `specs.py validate` can confirm every declared standard has a `tasks.md` item and
  `quenching-specs-plan-archive` can confirm each one was actually written.
- **`quenching-specs-explore` lands its output.** A new closing step offers three destinations for
  what an exploration produced: a `design.md` draft, a backlog task, or `docs/knowledge/`.
- **The minimum ritual becomes one invocation.** `quenching-specs-plan-from-claude` accepts an
  inline plan (not only a file path), gains `AskUserQuestion` + `Skill` in `allowed-tools`, and
  offers to chain into apply; `quenching-specs-plan-apply` offers to chain into archive at 100%.
  `/specs:plan:from-claude` plus two confirmations becomes branch → tracked tasks → distillation.
- **`quenching-specs-plan-apply` verifies and commits.** It refuses to start on a dirty tree,
  runs each task's declared `verify` command, loops on failure with a re-read at two consecutive
  failures and a five-attempt budget, runs a four-item diff self-review before committing, and
  commits one task at a time as `plan/<name>: <id> <title>`.
- **The verification policy is declared per plan, not guessed.** `propose` records
  `per-task` / `per-section` (default) / `end-of-plan` in `.specs.json`, so apply never has to
  decide when to test.
- **`tasks.md` carries execution context.** Optional indented `files:` / `pattern:` / `verify:`
  lines under a checkbox, parsed by `specs.py` and backward compatible with every existing plan.
- **Executors may be delegated; parallelism must be earned.** A per-task executor sub-agent is
  allowed when the task declares `files:` and touches no `docs/`; the orchestrator keeps every
  confirmation, every checkbox flip, and every `docs/` write. Two tasks run in parallel only when
  a `[P]` marker was set at propose time **and** their `files:` sets are disjoint. Serial stays
  the default.
- **A failed task is distinguishable from an untried one.** `specs.py` records attempt state so
  `next` stops re-offering a task that already burned its budget.
- **The three documented defects are fixed**: `next` gains its design action, `validate` inspects
  `design.md`, and `from-claude` gets its missing tool.

## Out of Scope

- Replicating BMAD's six agent personas (Analyst/PM/Architect/SM/Dev/QA) — the front already
  partitions by front and taxonomy; personas would add always-on description cost with no new
  information.
- A separate `/specs:plan:analyze` skill — its deterministic half becomes `specs.py validate`
  coverage checks, its judgment half becomes `refine --mode critic`.
- A `quenching-specs-plan-quick` express lane — reconsidered only if the chaining in this plan
  fails to remove the friction in practice.
- Splitting refinement into per-artifact skills (`refine-proposal`, `refine-design`) — the axis is
  "refine by interrogation"; the technique is a parameter.
- Any change to the `docs/`, `.claude/`, or cross-front conductors.

## Validation

- `python assets/hooks/okf-validate.py assets/docs` → `0 error(s), 0 warning(s)`, and
  `assets/specs/backlog --listing-root` likewise.
- `python assets/bin/specs.py --version`, `okf-validate.py --version`, `VERSION`,
  `plugin.json`, and the marketplace manifest all agree.
- A throwaway workspace exercises the new `specs.py` surface end to end: `new` → `status` →
  `next` (design action appears) → `task --check` → `validate` (`sp-unrefined`, coverage,
  `design.md` scaffold detection) → `archive --force`.
- Every pre-existing plan fixture still parses after the `tasks.md` metadata change (backward
  compatibility).
- Bijection holds at 28 ↔ 28: every skill has a wrapper and every wrapper a skill.
- Each new `SKILL.md` description stays under the 1,536-character cap with trigger phrases in the
  second sentence.

## Impact

**Standards this plan will write into `docs/standards/`:**

- `docs/standards/workflows/plan-artifacts.md` — the plan artifact contract: required sections
  with explicit-none fallbacks, the parseable `## Impact`, the refinement record, and what
  `applyReady` does and does not guarantee.
- `docs/standards/workflows/task-execution.md` — the execution contract: the three verification
  policies and when each applies, the failure budget, commit-per-task, the diff self-review, and
  the delegation + `[P]` disjunction rule.

**Standard at `authority: background` this plan may resolve:** none identified — both standards
above are new.

**Plugin code and skills this plan expects to touch:**

- `plugins/claude-quenching/assets/bin/specs.py` — `parse_tasks` metadata, `compute_next` design
  action, `_validate_plan` (design scaffold, `sp-unrefined`, Impact coverage), attempt state,
  `.specs.json` fields, `VERSION`.
- `plugins/claude-quenching/assets/specs/templates/{proposal,design,tasks}.md` and
  `assets/specs/schema.json`.
- New: `plugins/claude-quenching/skills/quenching-specs-plan-refine/` (`SKILL.md` +
  `references/techniques.md`) and `plugins/claude-quenching/commands/specs/plan/refine.md`.
- Edited skills: `quenching-specs-plan-propose`, `quenching-specs-plan-apply`,
  `quenching-specs-plan-from-claude`, `quenching-specs-explore`, `quenching-specs-plan-archive`,
  `quenching-specs-plan-update`, `quenching-specs-status`.
- Edited references: `quenching-specs-plan-propose/references/{artifacts,spec-driven}.md`.
- Release lockstep: `VERSION`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`,
  `assets/hooks/okf-validate.py` `VERSION` constant.
- The three operator manuals — `assets/docs/QUENCHING.md`, `assets/specs/QUENCHING.md`,
  `assets/claude/QUENCHING.md` — because they enumerate the command surface and it gains
  `/specs:plan:refine`.
- `plugins/claude-quenching/README.md` (cost model row for the new skill and for executor
  delegation) and the root `CLAUDE.md` (twenty-seven → twenty-eight, the new skill's row).
