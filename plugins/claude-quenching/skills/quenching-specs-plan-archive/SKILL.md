---
name: quenching-specs-plan-archive
description: >-
  Archives a COMPLETED plan — checks task and artifact completion via specs.py, moves the plan
  folder to specs/archive/YYYY-MM-DD-<name>/ (specs.py archive refuses with exit 2 on open tasks
  unless forced), then offers ONE OKF distillation pass: minting into docs/ only the by-products
  a plan left behind (a decision → standards/ authority-graded, generic understanding →
  knowledge/, a new term → glossary, a follow-up → specs/backlog/). Use when the user asks to
  "archive the plan", "finalize the plan", "close out this plan", or "the plan is done, wrap it
  up". The rule the plan implemented was ALREADY written into docs/standards/ during apply —
  archiving syncs nothing; it only catches what was not yet captured. Warnings never block:
  incomplete items just confirm, never silently stop. Not for: implementing remaining tasks →
  quenching-specs-plan-apply; a plan that will NOT be built (no distillation of a proved rule,
  reopen its seed task) → quenching-specs-plan-abandon; inserting an arbitrary doc into docs/ →
  quenching-docs-add.
when_to_use: >-
  finalizing and archiving a COMPLETED plan, including the post-archive OKF distillation offer.
  Implementation is quenching-specs-plan-apply; a plan that will not be built is
  quenching-specs-plan-abandon.
allowed-tools: Bash(python3:*), Bash(py:*), Bash(mkdir:*), Bash(mv:*), Read, Glob, Grep, Write, Edit, AskUserQuestion, Skill
user-invocable: false
---

# quenching-specs-plan-archive — archive a completed plan, then distill

Archive a completed plan, then offer to distill its durable by-products into the OKF
`docs/` bundle.

Spec-driven facts (the `specs/` layout, the plan artifact graph, the artifact formats, the
`specs.py` tool surface) live in
[../quenching-specs-plan-propose/references/spec-driven.md](../quenching-specs-plan-propose/references/spec-driven.md).
The distillation doctrine (what crosses to `docs/`, what stays) lives in
[references/distill.md](references/distill.md). Resolve `specs.py` by the fallback in
[../quenching-specs-backlog-add/references/backlog-zone.md](../quenching-specs-backlog-add/references/backlog-zone.md)
§Resolving the tool (plugin path → `.claude/hooks/specs.py` → declared manual check); invoke
with `python3` or `py`.

**This front is entirely native — there is no delta and no separate spec store, so archiving
does not sync anything.** A plan writes its durable rule **straight into `docs/standards/`** while
it is built (`quenching-specs-plan-apply`). By the time it is archived, most of what it proved is
already in `docs/`. This skill moves the finished plan into the archive and then does one thing
more: it catches the **by-products** — a decision left in `design.md`, an understanding, a term, a
follow-up task — that were not committed to a home yet. Nothing is bulk-copied.

**Exception — cycle-authorized runs.** Invoked as a **stage of the `specs/` front's pipeline** by
`quenching-specs-align-and-update` (or `quenching-align-and-update-all`) under the
cycle-authorization contract
([../quenching-align-and-update-all/references/convergence.md](../quenching-align-and-update-all/references/convergence.md)
§cycle-authorization), the plan name is **supplied** — skip Step 1's selection prompt — and the
routine confirmations become narration. **But the archive itself still confirms on its own**: it
is one of the two item classes the authorization never covers, because a plan the tool reports
complete may still be waiting on a deploy. Present what it will distill, and wait.

**Input**: Optionally specify a plan name. If omitted, check whether it can be inferred from
conversation context. If vague or ambiguous you MUST prompt for available plans.

**Steps**

1. **If no plan name provided, prompt for selection**

   Run `specs.py list --json` to get the active plans. Use the **AskUserQuestion tool** to let
   the user select. Show only active plans (not already under `specs/archive/`).

   **IMPORTANT**: Do NOT guess or auto-select a plan. Always let the user choose.

2. **Check completion status**

   Run `specs.py status --plan "<name>" --json`. Branch on the JSON and the exit code
   (**0** ok · **1** findings · **2** refusal), never on prose. Read from it:
   - each artifact's `state` (`done` / `ready` / `blocked`) and the resolved `artifactPaths` —
     use these paths, never assume them;
   - the task progress and `applyReady`.

   **If any artifact is not `done`, or `tasks.md` has open `- [ ]` items:**
   - Display a warning listing the incomplete artifacts and the open-task count.
   - Use the **AskUserQuestion tool** to confirm the user wants to archive anyway.
   - Proceed only if the user confirms. (A plan with no `tasks.md` archives without a
     task-related warning.)

3. **Perform the archive**

   Run a dry run first to see exactly what will move and whether the tool would refuse:
   ```bash
   specs.py archive <name> --dry-run
   ```
   Then archive:
   ```bash
   specs.py archive <name>
   ```
   The tool moves the plan folder to `specs/archive/YYYY-MM-DD-<name>/` and reports the resolved
   destination. **Exit codes:**
   - **0** — archived; read the JSON for the destination path.
   - **2** — refusal because `tasks.md` still has open items. If Step 2's confirmation already
     covered proceeding with incomplete tasks, re-run with `--force`
     (`specs.py archive <name> --force`); otherwise stop and surface the refusal — never force
     past open tasks the user has not agreed to.

   If the destination already exists (a same-name plan archived earlier today), the tool reports
   it — stop and suggest a different date or renaming the existing archive rather than
   overwriting history.

4. **Distill durable by-products into the OKF bundle (the single bridge)**

   If the repo carries an OKF bundle (`docs/index.md` with `okf_version`), run the distillation
   procedure in [references/distill.md](references/distill.md):
   - **harvest** the archived plan's artifacts for the **remaining** durable candidates —
     checking first what `docs/standards/` already received during apply, so the rule the plan
     implemented is **not** re-minted. Route each: a decision not yet captured →
     `standards/<subject>/` (`authority: current` only if the plan proved it, else `background`);
     generic understanding → `knowledge/`; a new repo-specific term → `knowledge/glossary.md`; an
     unpursued follow-up → `specs/backlog/` (via `quenching-specs-backlog-add`, outside the
     bundle);
   - present the candidates as **one plan, one confirmation** (an empty harvest is a valid,
     common outcome — a plan that captured its rules as it went taught nothing else durable; say
     so and finish);
   - mint each approved doc under the insert procedure
     ([../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md)) and
     log each in `docs/log.md` as distilled from the plan;
   - self-check against
     [../quenching-docs-align/references/conformance.md](../quenching-docs-align/references/conformance.md).

   No bundle → skip silently (optionally mention that `quenching-docs-align` installs one).

5. **Display summary**

   Show the archive completion summary:
   - plan name;
   - archive location (`specs/archive/YYYY-MM-DD-<name>/`);
   - what was distilled into `docs/` (docs minted, or "nothing durable — archive only");
   - a note about any warnings (incomplete artifacts/tasks the user confirmed past).

**Output On Success**

```
## Archive Complete

**Plan:** <plan-name>
**Archived to:** specs/archive/YYYY-MM-DD-<name>/
**Distilled:** <N docs minted into docs/> (or "nothing durable to distill")

All artifacts complete. All tasks complete.
```

**Guardrails**
- Always prompt for plan selection if not provided; never auto-select.
- Use `specs.py status --json` and its exit code for completion checking — never infer from
  prose.
- Don't block the archive on warnings — inform and confirm. Only `--force` past open tasks the
  user has explicitly agreed to.
- `.specs.json` moves with the folder — the tool preserves it; never edit the archived plan.
- Archiving syncs **nothing** — there is no delta and no separate spec store. The behavior a
  plan implemented is already in `docs/standards/` from apply; this step only harvests
  by-products.
- Distillation is **offer-and-confirm, never automatic**: one plan, one OK, strike-able items;
  never bulk-copy artifacts into `docs/`, never edit the archived plan, never fabricate a
  candidate (per [references/distill.md](references/distill.md) §Invariants).
