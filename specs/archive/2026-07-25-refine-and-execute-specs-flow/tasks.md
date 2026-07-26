# Tasks — Refino, rito minimo e execucao eficiente no front specs/

Sections are ordered so each is independently shippable: stopping after any section leaves the
plugin in a coherent, releasable state (design.md §Risks, "The plan is large").

## 1. Fix the documented defects

- [x] 1.1 Add the design action to `compute_next` in `assets/bin/specs.py` — between the proposal
      and tasks branches, emit `write_artifact`/`design` when `design.md` is a bare scaffold, so
      the tool produces the state `quenching-specs-plan-propose` §5a already documents
- [x] 1.2 Add `sp-design-scaffold` (warn) to `_validate_plan` in `assets/bin/specs.py` — flag a
      `design.md` that exists but has no real content after `strip_comments`
- [x] 1.3 Add `AskUserQuestion` and `Skill` to `allowed-tools` in
      `skills/quenching-specs-plan-from-claude/SKILL.md` (Steps 4 and 6 already require a
      confirmation the frontmatter does not permit)
- [x] 1.4 Verify: in a throwaway workspace, `specs.py new x` → `next` names design → fill design →
      `next` names tasks; `validate` reports `sp-design-scaffold` before the fill and not after

## 2. Harden the plan artifact contract

- [x] 2.1 Add `## Out of Scope` and `## Validation` to `assets/specs/templates/proposal.md`, with
      comment guidance that an empty section is written as an explicit `- none`, never omitted
- [x] 2.2 Add `## Alternatives Considered` and `## Open Decisions` to
      `assets/specs/templates/design.md` and replace the "delete this file" comment with the
      required-with-explicit-fallback rule (design.md §Decisions 3)
- [x] 2.3 Make `## Impact` machine-checkable: define the parsed form (a bullet list of
      `docs/standards/**` paths under a fixed sub-heading) in the proposal template, and add
      `parse_impact_standards()` to `assets/bin/specs.py`
- [x] 2.4 Add `sp-impact-uncovered` (warn) to `_validate_plan` — a `docs/standards/` path declared
      in `## Impact` with no matching `tasks.md` item
- [x] 2.5 Confirm `applyRequires` still excludes `design` in `assets/specs/schema.json` — a
      required section set is not a required dependency (design.md §Decisions 3, consequence)
- [x] 2.6 Update `skills/quenching-specs-plan-propose/references/artifacts.md` for the new
      sections, the explicit-none rule, and the parsed `## Impact`
- [x] 2.7 Update `skills/quenching-specs-plan-propose/references/spec-driven.md` §Artifact formats
      and §The `specs.py` tool surface to match
- [x] 2.8 Verify: an existing archived plan under `specs/archive/` still passes
      `specs.py validate` unchanged (backward compatibility)

## 3. Mint the refinement skill

- [x] 3.1 Write `skills/quenching-specs-plan-refine/SKILL.md` — description under the
      1,536-character cap with trigger phrases in the second sentence and the "Not for:" boundary
      against `plan-update` (reactive) and `explore` (unbounded)
- [x] 3.2 Write `skills/quenching-specs-plan-refine/references/techniques.md` — the four mode
      scripts (`interview`, `critic`, `premortem`, `alternatives`) and the three shared mechanics:
      one question at a time with an inline recommendation, accumulate and apply in ONE edit, and
      the declared stop condition
- [x] 3.3 Write the mirrored wrapper `commands/specs/plan/refine.md` (bijection: 28 ↔ 28)
- [x] 3.4 Record refinement in `.specs.json`: add `refined: {mode, date}`, written by the skill
      and read by `specs.py`
- [x] 3.5 Add `sp-unrefined` (warn, never error) to `_validate_plan` — a plan with `tasks.md` and
      no `refined` record
- [x] 3.6 Surface `sp-unrefined` in `skills/quenching-specs-status/SKILL.md`'s finding vocabulary,
      under "what neither /specs:align nor /specs:align-and-update closes"
- [x] 3.7 Verify: the wrapper resolves, the description is within cap, and
      `specs.py validate` reports `sp-unrefined` on an unrefined plan and drops it after a refine

## 4. Land what exploration and revision produce

- [x] 4.1 Add a closing "Landing" step to `skills/quenching-specs-explore/SKILL.md` — offer three
      destinations for what the exploration produced (a `design.md` draft, a `specs/backlog/`
      task, or `docs/knowledge/`), keeping offer-never-auto-capture
- [x] 4.2 Cross-reference `quenching-specs-plan-refine` from
      `skills/quenching-specs-plan-update/SKILL.md` (reactive vs. generative boundary) and from
      `skills/quenching-specs-plan-propose/SKILL.md` (offer a refine pass at apply-ready)

## 5. Make apply verify and commit

- [x] 5.1 Add the `tasks.md` execution metadata format (indented `files:` / `pattern:` / `verify:`
      lines) to `assets/specs/templates/tasks.md` and to `references/artifacts.md`
- [x] 5.2 Extend `parse_tasks` in `assets/bin/specs.py` to return the three metadata fields,
      leaving `CHECKBOX_RE` untouched so existing plans keep parsing
- [x] 5.3 Add the per-plan verification policy: `verification: per-task | per-section |
      end-of-plan` (default `per-section`) written to `.specs.json` by `specs.py new` and by
      `quenching-specs-plan-propose`
- [x] 5.4 Add per-task attempt state to `.specs.json` (attempt count, last error) and make
      `compute_next` skip a task that exhausted its budget, reporting it as blocked
- [x] 5.5 Add the dirty-tree precondition to `skills/quenching-specs-plan-apply/SKILL.md` — refuse
      to start when `git status --porcelain` is non-empty, stating why (an unrelated diff cannot
      be told from the task's)
- [x] 5.6 Add the validation loop to the same skill — run the task's `verify`, re-read the task
      and the current diff from scratch after two consecutive failures, hard budget of five
      attempts, then stop the loop and report
- [x] 5.7 Add the four-item diff self-review before each commit (reuse, useless defense, obvious
      comment, dead code) and the per-task commit `plan/<name>: <id> <title>`
- [x] 5.8 Add the end-of-plan full-diff review offer, distinct from the per-task self-review
      (design.md §Decisions 8)
- [x] 5.9 Add `Skill` to `allowed-tools` in `quenching-specs-plan-apply` and offer to chain into
      `quenching-specs-plan-archive` at 100% task completion
- [x] 5.10 Add the hard rules to the skill: never disable a test, never edit the validation
      command to make it pass, never `--no-verify`, never `--no-gpg-sign`

## 6. Delegation and parallelism

- [x] 6.1 Add the executor delegation rule to `skills/quenching-specs-plan-apply/SKILL.md` — a
      per-task sub-agent is permitted when the task declares `files:` and touches no `docs/`,
      pinned to the session model; the orchestrator keeps plan selection, every confirmation,
      every `specs.py task --check`, every `docs/standards/` write, and the pause decision
- [x] 6.2 State explicitly in the same section that this is NOT `context: fork` and why the
      never-fork rule is untouched (design.md §Decisions 6)
- [x] 6.3 Add the `[P]` marker to the `tasks.md` format — set at propose time only, honored by
      apply only when the marked tasks' `files:` sets are disjoint and neither writes `docs/`
- [x] 6.4 Add the disjunction check to `assets/bin/specs.py` so the marker is verified
      mechanically, not judged in prose
- [x] 6.5 Decide per design.md §Open Decisions whether `[P]` ships here or defers — if it defers,
      strike 6.3 and 6.4 and record the deferral in the plan, do not leave them silently unticked

## 7. Write the standards (the durable rules this plan proves)

- [x] 7.1 Write `docs/standards/workflows/plan-artifacts.md` — required sections with
      explicit-none fallbacks, the parsed `## Impact`, the refinement record, and what
      `applyReady` does and does not guarantee (`authority: current` once sections 2–3 are
      implemented and verified, else `background`)
- [x] 7.2 Write `docs/standards/workflows/task-execution.md` — the three verification policies and
      when each applies, the failure budget, commit-per-task, the two-level review split, and the
      delegation + `[P]` disjunction rule including the never-fork distinction (`authority:
      current` once sections 5–6 are implemented and verified, else `background`)
- [x] 7.3 Update `docs/standards/workflows/index.md` to list both new docs, and append both to
      `docs/log.md`
- [x] 7.4 Verify both docs against
      `skills/quenching-docs-align/references/conformance.md` (frontmatter stamp, type, index
      honesty)

## 8. Surface, docs, and release

- [x] 8.1 Update the three operator manuals — `assets/docs/QUENCHING.md`,
      `assets/specs/QUENCHING.md`, `assets/claude/QUENCHING.md` — for `/specs:plan:refine`
- [x] 8.2 Update the root `CLAUDE.md`: twenty-seven → twenty-eight skills, the new skill's row in
      the skills table, and the `specs/` front paragraph
- [x] 8.3 Update `plugins/claude-quenching/README.md` — the cost-model row for
      `quenching-specs-plan-refine` and the amended row for the plan-authoring skills (executor
      delegation is now permitted in `plan-apply`; the never-fork rule is unchanged)
- [x] 8.4 Bump the version in lockstep: `VERSION`, `.claude-plugin/plugin.json`,
      `.claude-plugin/marketplace.json`, and the `VERSION` constant in **both**
      `assets/bin/specs.py` and `assets/hooks/okf-validate.py`
- [x] 8.5 Verify the skeleton: `okf-validate.py assets/docs` and
      `okf-validate.py assets/specs/backlog --listing-root` both report 0 errors, 0 warnings
- [x] 8.6 Verify the lockstep: `VERSION`, `specs.py --version`, and `okf-validate.py --version`
      all agree
- [x] 8.7 Verify the bijection: 28 skills, 28 wrappers, every wrapper resolving to a skill and
      every skill to a wrapper
- [x] 8.8 Verify `specs.py` end to end in a throwaway workspace: `new` → `status` → `next` →
      `task --check` → `validate` (all new codes) → `archive --force`
