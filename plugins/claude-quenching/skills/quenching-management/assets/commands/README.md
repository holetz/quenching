# assets/commands/ — command-skill payloads of the method

The **commands** the [`quenching-management`](../../SKILL.md) method installs in a
target repo live here. By the doctrine of dimension 9, **every new command is
born as a skill** — *"custom commands have been merged into skills … A file at
`.claude/commands/<name>.md` and a skill at `.claude/skills/<name>/SKILL.md` both
create `/<name>` and work the same way … Skills are recommended"* (Claude Code
docs). Therefore, each payload here is a **`SKILL.md`** with a trigger-description
(dim 6), installed in `.claude/skills/<prefix>-<name>/` of the target — invocable
via `/<name>` **and** auto-triggered by the model. The legacy
`.claude/commands/<name>.md` format is retained only for the pure **manual
shortcut with side-effects** (and then with `disable-model-invocation: true`).

> **Not "active" in this skill.** They live under `assets/` (≥2 levels below),
> so Claude Code **does not** discover them as live skills — they are **payloads**,
> copied out when the method is applied.

## Inventory

| Path | Type | Installs in | Addresses |
| --- | --- | --- | --- |
| `quenching-reaudit/SKILL.md` | command-skill | `.claude/skills/<prefix>-reauditar/` | trigger (3) of Step 8 (on-demand re-audit) — dim 9 + core + dim 7 |

## `quenching-reaudit` — on-demand re-audit

Materializes **trigger (3)** of the recurring maintenance cycle (Step 8 of
SKILL.md): re-runs **Steps 1-7** of the method (audit) **when the operator
wants**, across the entire repo or only the scope the argument provides
(`argument-hint`), without waiting for the next cycle. It is a **skill** (not a
legacy command) for two reasons from the dim 9 doctrine: (a) **reads and proposes**
— no side-effect (so it keeps auto-triggering); (b) operators tend to **forget**
to invoke it, so auto-triggering by description adds value. Uses **`context: fork`
+ `agent: quenching-auditor`** to run the scan in **clean context** (the Explore-
like agent skips CLAUDE.md to keep context cheap), returning only the condensed
scorecard (dim 7 return contract), not the dump.

## How to install (summary)

1. **Copy** `quenching-reaudit/` to `.claude/skills/<prefix>-reauditar/` of the
   target.
2. **Rename** the folder/`name` to the derived taxonomy (`<prefix>`); the skill is
   an agent-facing surface — keep its `description`/body **English**.
3. Ensure the `quenching-auditor` sub-agent (from `../agents/`) is also installed
   in `.claude/agents/` of the target — the `agent:` frontmatter field references
   it. If the repo uses another auditor name, point `agent:` to it.
4. **Fix** the reference paths (`references/detection-and-smells.md`) to the shape
   derived in Step 0.
5. If the repo already had an equivalent `/audit-claude-md`/`/audit-*`, **deprecate
   it** (do not remove without OK) — deprecation doctrine in
   [../../references/installation.md](../../references/installation.md).
