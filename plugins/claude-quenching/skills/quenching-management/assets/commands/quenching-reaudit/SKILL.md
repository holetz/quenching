---
name: quenching-reaudit
description: >-
  On demand, re-runs the knowledge-surface audit of the repo (Steps 1-7 of the
  knowledge-management method), for the whole repo or just for what the argument
  specifies, delegating the scan to the auditor sub-agent in a clean context —
  and returns a fresh gap report (Present/Partial/Drifted/Absent) so the base
  does not rot between audits. Use when the user asks to "re-audit the knowledge",
  "run the audit again", "is the CLAUDE.md/docs/skills up to date?", "check the
  surface after this PR/refactor", "see what has aged in the knowledge base",
  "audit dimension X again" — or after a large code/model/team change that may
  have left the base stale (context rot).
when_to_use: >-
  on-demand re-run of the knowledge-base audit (Steps 1-7), for the whole repo or
  one dimension/path, keeping the base fresh between audits; this is the manual
  trigger of the recurring maintenance cycle.
argument-hint: "[scope: dimension | path | empty = whole repo]"
allowed-tools: Read, Grep, Glob, Bash
context: fork
agent: quenching-auditor
---

# Re-audit the knowledge surface (on demand)

> **Payload of the [`quenching-management`](../../../SKILL.md) method.** This is the
> **(3) on-demand trigger** of the recurring maintenance cycle (Step 8 of
> SKILL.md): re-examines the base **when the operator wants**, without waiting for
> the next cycle. Generic and portable — adapt the prefix/language to the
> conventions of the repo where it is installed. Installs as a **skill** (not a
> legacy command): it is a **manual work shortcut** that benefits from auto-
> triggering by description, **not** a side-effect; *"custom commands have been
> merged into skills … skills are recommended"*. (If the re-examination ever gains
> a side-effect — opening a PR, committing — then add `disable-model-invocation:
> true`.)

## Why a skill (and not a legacy command)

The doctrine of dimension 9 is **"every new command is born as a skill; it stays
a legacy command only as a pure manual shortcut with side-effects"**. Re-auditing
**reads and proposes** (does not change the state of the world), and operators
tend to **forget** to invoke it via `/name` — exactly the two migration criteria
(command→skill: auto-trigger + multi-repo/portable). So it is born as a skill
with a **trigger-description** (dim 6) + `argument-hint` for the scope, and
**`context: fork` + `agent: quenching-auditor`** to run the scan in **clean
context** (does not pollute the main thread — the Explore-like agent *"skips
CLAUDE.md to keep context small"*).

## Scope (`$ARGUMENTS`)

- **empty** → re-audit the whole repo (all 15 dimensions).
- **one dimension** (e.g., `docs`, `skills`, `hooks`, `mcp`, `9`) → only that one.
- **a path** (e.g., `docs/standards/`, `.claude/skills/`) → only the surface
  touched by that path (ideal after a localized PR/refactor).

Scope of this invocation: **$ARGUMENTS**

## What to do

1. **Derive the target repo shape** (Step 0 / Step 1 of the method): locate the
   CLAUDE.md(s), normative layer, direction, backlog, decisions, catalog/domain,
   memory, and the `.claude/` inventory. Empty variable ⇒ layer is **Absent**.
   The adaptive globs/greps live in `references/detection-and-smells.md` of the
   `quenching-management` skill.
2. **Run detection per dimension** (1-15, or only the scope from `$ARGUMENTS`)
   with the reference commands, **read-only**. Collect the minimum evidence that
   decides the state of each dimension.
3. **Score** each dimension **Present / Partial / Drifted / Absent**, always with
   `file:line` (concrete evidence, never impressions). **Drifted** is the state
   this re-audit hunts most: what existed and **has aged** since the last pass
   (index that lies, broken link, completed item still in the tree, fossil of a
   replaced standard).
4. **Do not decide boundaries or memory** — only gather the evidence. Boundary
   diagnosis (dim 12) and comparative memory reading (dim 10) stay in the main
   thread (and **installation** follows Steps 5-7, with confirmation).

## Return format (short — the fork condenses, does not dump)

- **Derived shape:** 1-2 lines (layer paths, language, taxonomy).
- **Scorecard:** one line per audited dimension — `N | dimension | state | file:line`.
- **Δ vs. expected / Drifted-Absent:** 3-8 items that have aged or are missing and
  deserve to become P1/P2 gaps.
- **Next step:** what to install (Steps 5-7, with OK) or what needs human judgment
  (boundaries, memory, trigger collision).

Do not dump the raw scan into the parent context — only the scorecard + the
highlights that support prioritization (dim 7 return contract).
