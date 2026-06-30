# `evolution/log/` — evolution log by context

> **Path back:** human portal → [../../README.md](../../README.md) · system design
> → [../../ARCHITECTURE.md](../../docs/method/architecture.md) · evolution spine →
> [../README.md](../README.md) (read it **first**).

The **detailed** records of each round (`R*`) and revision (`Rev*`) of the method's
evolution live here, **one file per context** (one dimension or one theme). The
index, the anchor state (`current-round` / `last-revision`), the boundary backlog,
and the review queue live in the **spine** [../README.md](../README.md) — read it
**first**.

## Why the split

The old `EVOLUTION.md` accumulated the anchor state, the exclusion index **and** the
verbose log of all rounds in a single file — it exceeded 1,500 lines and became
hard to read, organise, and **revisit**. The split applies the method itself
(dim 1/15: *smallest high-signal set* + *just-in-time retrieval*): agents read the
**cheap spine** and open **only** the context file they will touch, instead of
loading the full history on every invocation.

## Anatomy of a context file

- **`## Current state`** — the **active** summary of each boundary in this dimension
  (what is valid today). This is what a reader consults to know the current
  definition without reading the history.
- **`## Round and revision history`** — the **complete** entries (Change · Why ·
  Sources · Rejected/superseded · Next candidate), most recent at the top. A
  revision (`Rev*`) is nested **under** the round it refines.

## ID convention

- **`R<N>` — _advance_ round** (agent `quenching-evolutionist`): attacks a **new**
  boundary, not yet addressed; **increments** `current-round`. Never re-attacks a
  boundary already done.
- **`Rev<K>` — _revision_** (agent `quenching-reviewer`): **critiques, refines,
  merges, prunes, or supersedes** a definition **already done**; does **not**
  increment `current-round` (it is not a new boundary) — it is tracked by
  `last-revision`. Marks the target round with `revised-by: Rev<K>` (refined) or
  `superseded-by: Rev<K>` (replaced) and updates the **Current state** of the
  context.

Both agents write to the **same** context files: the evolucionista pushes the
boundary forward; the revisor improves what is already here.

## Routing (dimension/theme → file)

| File | Covers | Rounds migrated |
| --- | --- | --- |
| `core-workflow.md` | base skeleton + eval cycle (cross-cutting) | R0, R12 |
| `dim-01-claude-md.md` | CLAUDE.md / context budget | R5 |
| `dim-02-docs.md` | normative reference & `docs/` structure | R13, R14, R15, R16 |
| `dim-06-skills.md` | skills (trigger, toolset bloat) | R4, R10 |
| `dim-07-subagents.md` | sub-agents (home/tools, return contract) | R6, R9 |
| `dim-08-hooks.md` | hooks (continuous audit, exit semantics) | R7 |
| `dim-08-scripts.md` | `scripts/` home (executable logic; thin-hook-calls-script; crosses dim 1/9) | R35 |
| `dim-09-commands.md` | legacy commands × skills | R8 |
| `dim-10-memory.md` | memory (Auto Memory) | R3 |
| `dim-12-boundaries.md` | boundary doctrine (Diataxis/DRY) | R2 |
| `dim-14-guardrails.md` | guardrails (actionable errors, poka-yoke) | R11 |
| `dim-15-mcp.md` | MCP / `.mcp.json` | R1 |

A new boundary that does not fit any existing dimension **opens a new file**
(`dim-NN-<slug>.md` or `nucleo-<slug>.md`) and gets a line in the spine index.
Keep the routing table in this file in sync.
