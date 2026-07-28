# Change log — `standards/`

History of the standards bundle, most recent first. Each entry is grouped under a
`## YYYY-MM-DD` heading and prefixed `**Creation**` / `**Update**` / `**Deprecation**`.

## 2026-07-28

**Update**: [Plan git record contract](/docs/standards/workflows/plan-git-record.md), [Plan lifecycle contract](/docs/standards/workflows/plan-lifecycle.md) and [Task execution contract](/docs/standards/workflows/task-execution.md) — rewritten by the `move-conclude-merge-last` spec around the commit **subject** as the task→commit anchor. A subject is known *before* its commit exists, so every record is now written before the thing it describes: the ticked box travels inside its own task commit, `merge: {strategy, subject}` is stamped on the work branch, and the merge becomes the last action of `/specs:conclude`. `branch:` changes owner to the new `/specs:isolate`. Rebase stops destroying the record; the squash caveat stands.

**Update**: four standards refreshed by that spec's branch review, none of them declared by a task — their `resource` globs simply cover what it touched. [Command surface naming](/docs/standards/naming/command-surface.md) still named a root `/align-and-update` that [Align surface](/docs/standards/architecture/align-surface.md) had already recorded as deleted, so two `authority: current` docs disagreed about what exists. [Always-on context budget](/docs/standards/automation/context-budget.md) records that its deliberately zero-headroom ceiling **fired exactly as predicted** when `/specs:isolate` became the 25th command (11,565 → 12,726), and prices the shape: a ratchet with no headroom makes every new command a three-file bookkeeping change. [Spec file contract](/docs/standards/workflows/plan-artifacts.md) gains the **third** copy of the record vocabulary — `assets/specs/schema.json`, which *shadows* `DEFAULT_SCHEMA` via `load_schema()` rather than falling back to it, so a change made only to the constant is invisible in the layout the plugin ships. [Surface verification](/docs/standards/quality/surface-verification.md) gains a fourth precondition — read the capture with an explicit encoding, because a check that cannot decode its evidence fails *for lack of evidence* in a way indistinguishable from a real failure — and the ordering-check pattern (`conclude-order-check.sh`), for rules phrased as a "never after" that no linter can observe.

## 2026-07-27

**Update**: [Spec file contract](/docs/standards/workflows/plan-artifacts.md) and [Task execution contract](/docs/standards/workflows/task-execution.md) — reconciled with what the `specs-flow-consolidation` branch shipped, found by its branch review. `plan-artifacts.md` was retitled from "Spec lifecycle contract" and its superseded v2 lifecycle claims (folder-is-the-phase, promote-as-the-human-OK, the five-key frontmatter list, the `backlog/`/`ready/` sub-stages) are now pointers into [plan-lifecycle.md](/docs/standards/workflows/plan-lifecycle.md); the explicit-none gate table names the derived `ready` stage. `task-execution.md`'s `resource` pointed at the deleted `commands/specs/apply.md` (`resource-unresolved`) and is repointed at `execute.md` + `conclude.md`, and §Review splits now names the two commands that own the two levels. Two `authority: current` docs no longer assert the contract the branch deleted.

**Creation**: [Align surface — one align per front, probe first](/docs/standards/architecture/align-surface.md) — the 1×4 column that replaced the 2×4 matrix (`align-and-update` deleted on all four fronts) and the probe-before-inventory rule that makes a no-op align cost a couple of tool calls (`authority: current` — the fold landed and `functional-checks.sh` proved the surface loads).

**Creation**: [Plan git record contract](/docs/standards/workflows/plan-git-record.md) — the per-task `commit:` field written by `specs.py task --check --commit`, the write-once `branch`/`merge` frontmatter records, the squash caveat, and the read-if-present (never installed) contract for a target's `docs/standards/git/**` (`authority: current` — this spec's own build exercises every piece).

**Creation**: [Plan lifecycle contract](/docs/standards/workflows/plan-lifecycle.md) — the v3 single-folder lifecycle (`plans/` + `archive/`), the derived `ready` stage with the `approved: {date}` record, and the frontmatter-records-human-judgments rule; supersedes the v2 lifecycle claims in plan-artifacts.md (`authority: current` — the shipped `specs.py`/`schema.json` rails implement it).

## 2026-07-26

**Creation**: [Plugin layout — what may live under `commands/`](/docs/standards/architecture/plugin-layout.md) — `commands/**` is the only tree Claude Code registers, so everything that is not an entry point lives under `assets/` and is cited by `${CLAUDE_PLUGIN_ROOT}` absolute path (`authority: current` — the collapse migration proved it).

**Update**: [Command surface naming](/docs/standards/naming/command-surface.md), [Command authoring and alignment](/docs/standards/automation/skills.md), [Always-on context budget](/docs/standards/automation/context-budget.md) — the skill↔wrapper pair is retired; the command path is the identity. §Why the wrapper still exists is replaced by the trigger it fired, and the budget is re-derived at 2,083 characters from the collapsed surface.

**Update**: `resource` globs repointed off the deleted `plugins/quenching/skills/` tree in [skill-evaluation.md](/docs/standards/automation/skill-evaluation.md), [bundle-verification.md](/docs/standards/quality/bundle-verification.md), [plan-artifacts.md](/docs/standards/workflows/plan-artifacts.md) and [task-execution.md](/docs/standards/workflows/task-execution.md) — the validator reported all four as `resource-unresolved`.

## 2026-07-06

**Creation**: `standards/` home scaffolded by `quenching` — subject subfolders
established, `index.md` seeded with the derived-listing markers.
