---
type: standard
title: Subagent authoring
description: When work becomes a subagent, the definition contract for .claude/agents/, and how the surface is inventoried
resource: plugins/quenching/commands/components/agent/new.md, plugins/quenching/commands/components/align.md, plugins/quenching/assets/bin/quenching/components/**
tags: [automation, agents, delegation]
timestamp: 2026-11-03
audience: both
authority: current
source: skill-front capability research (2026-07-27) — hookify/plugin-dev/agent-sdk-dev + official docs; instrument-and-extend-skill-front plan §6; spec 2163 (2026-11-03)
maintainer: quenching
---

# Subagent authoring

<!-- rules -->

A **subagent** is a delegation: work runs in a fresh context and only its result returns.
One definition per file at `.claude/agents/<name>.md`, minted by `/quenching-align:components:agent:new` under
one plan → one OK, inventoried (report-only) by `/quenching-align:components:align`.

## When work is a subagent — and when it is not

Whether a wait is safe and what a new context pays differ per harness; read them from
`cq components session cache` ([context-discipline.md](context-discipline.md) §The prompt cache is a
per-harness measurement). Delegate when the returned summary is **much smaller than the work** that produced it (a
repo-wide sweep, a many-file audit, a read that ends in one table), when slices run in
parallel, or when the tool set must be narrower than the conversation's. Keep work inline
when its output is as large as itself (a rewrite lands in context anyway), when it is one
quick lookup, or when the handoff context would cost what the isolation saves. A recurring
*workflow* is a command; a delegated *unit of work* is an agent — the two are not rivals,
and a command may invoke an agent as one step.

## The definition contract

- **`description` is always-on context** — the same cost discipline and caps as a
  command's, counted on the parsed value. It states what the agent does **and when to invoke
  it**; an empty one is `sk-agent-no-description` (the agent can never be delegated to).
- **`tools` is scoped** to the narrowest set — read-only (`Read, Grep, Glob`) for a
  verifier; omitting the field grants everything, which is a choice a reader must be able to
  see was made.
- **`Skill` in a fenced `tools:` is a hole.** A skill's `allowed-tools` widen the agent that runs
  it, and `Skill(<name>)` restricts nothing (measured, Claude Code 2.1.294), so an agent without
  unrestricted `Bash` never holds `Skill`: it `Read`s the command body and follows it with its own
  grants. `cq components lint` reports the breach as `sk-agent-skill-widens` (spec 1365).
- **`model`/`effort` pins** are cache-safe here (the agent owns its context) but follow the
  same policy as everywhere: mechanical extraction may run cheap; judgment — anything that
  gates a deletion, ranks, or authors — inherits the session's.
- **`skills`, `memory`** are opened deliberately, never defaulted into: a
  preloaded skill's full body persists for the whole run, and agent memory is a recurring
  per-run cost.
- **The body is a system prompt, in second person** ("You are…") — a command body is
  imperative; the two voices never mix.

## The verifier shape

The highest-value agent for a kept-conformant repo: it **inspects and reports; it never
edits**. Its definition carries numbered check areas, an explicit **"not checked here"**
list (the false-positive control), *if-present* guards on optional features so minimal
artifacts pass clean, and a fixed report — status, critical findings, warnings, passed
checks, recommendations citing the standard each applies. Fixes re-enter through the
command that owns authoring, under its own confirmation.

The full pricing doctrine lives once, in
`plugins/quenching/assets/references/components-command-new/capabilities.md`
§Subagents; this standard is the repo-side projection of it.

## Plugin-shipped agents

The plugin ships exactly five agents in `plugins/quenching/agents/`, all prefixed `spec-` (as opposed
to a target's own `.claude/agents/`). Git (branch, commit, PR, merge, cleanup) and decomposition into
slices are flows of their verticals, not agents: `/quenching-specs:specs:develop` proposes and captures
the slices in the main session, and the orchestrator publishes after the verifier's PASS.

| Agent | Pin | Role |
|---|---|---|
| `spec-runner` | sonnet/medium (opus when `complexity: high`, passed by the orchestrator) | Builds ONE developed spec in its own worktree (execute, conclude); runs develop only under declared autonomy |
| `spec-verifier` | sonnet/low | Audits the real git and spec state and returns PASS or FAIL with evidence; read-only |
| `spec-reviewer` | opus/high | Reviews an epic's accepted commits for correctness, reproducing what it reports; read-only, once per epic, launched by the autopilot conductor |
| `spec-scout` | sonnet/low | Maps the code and standards a set of specs touches, at most ~2k tokens; read-only |
| `spec-orchestrator` | opus/medium | Conducts an epic or a queue, never a single spec; accepts a result only on a `spec-verifier` PASS and then publishes it |

Rules:

- One file per agent, `name` matching the filename, `description` within the command cap.
- `tools` is the narrowest allowlist: an orchestrator holds no `Edit`/`Write`, a verifier and a
  scout are read-only, and delegation is limited to the plugin's own `quenching-specs:spec-*` agent types.
- The shared protocol lives once, in the orchestrator body, which the cache reuses across sessions;
  never in a scratchpad file a prompt points at.
- Every worker and the orchestrator forbid `git stash`, `checkout`, `switch` and `reset`, and end
  in a fixed return report. A worker result is accepted only on a `spec-verifier` PASS.
- **The fixed report carries the gate's exit in a field of its own.** A worker states
  `GATE: pass | fail | not-run — <command>` and `GATE_EXIT: <code | not-run>` as two lines, in
  every STATE; the verifier reads the code as a claim and never parses a number out of prose. A
  gate that did not run says `not-run` — an omitted line is read as inconclusive, never as a pass.
- **A task that writes no repository file is accepted without a commit.** `files: (operational)`
  declares it; the verifier requires a sha only from the tasks that declared paths, and the scope
  check still charges any file the task wrote as an out-of-scope diff, so the marker can never hide
  a change.
- Plugin agents cannot carry hooks, so prohibitions are prose, enforced by the verifier's audit.
- Pass `model` explicitly when delegating; a declared pin may not survive into a subagent.
- Models: no `haiku` for agents that write product code, except the per-task executor of
  `/quenching-specs:specs:execute` on a task with a protected oracle (an executable `verify:` whose
  tests sit outside its `files:`, nothing under `/docs/`, projected context ≤ 80k by
  `cq specs estimate --task`) — ADR 0014. Judgment agents (`spec-orchestrator`, `spec-verifier`,
  `spec-reviewer`, `spec-runner`) never descend, and `import-memory` stays never-`haiku`.
