---
type: decision
title: The orchestrator's Agent(...) list is documentary
description: Why the Agent(type) allowlist in the orchestrator's tools restricts nothing when it runs as a subagent, and the accepted decision to document it and audit the launched types instead of blocking them
resource: plugins/quenching/agents/orchestrator.md
tags: [decision, agents, orchestrator, security]
timestamp: 2026-10-11
audience: both
authority: current
source: spec 1517
maintainer: quenching
---

# The orchestrator's Agent(...) list is documentary

This decision supersedes the passage of [0007](0007-native-claude-code-features.md) that says
`orchestrator` "restricts spawning with `Agent(quenching:spec-runner, ...)`". It replaces spec 1513.

## Finding

The official sub-agents documentation (checked against Claude Code 2.1.296) honours an
`Agent(type)` allowlist only for an agent run as the main thread (`claude --agent`). In a subagent
definition the list of types is ignored. `plugins/quenching/agents/orchestrator.md` declares
`tools: Agent(quenching:spec-runner, quenching:verifier, ...)` and
`commands/specs/orchestrate.md` launches it as a subagent, so it can launch any type. The capability
reference already says so (`components-command-new/capabilities.md`); 0007 contradicted it.

## Decision

Accepted by the human on 2026-10-11: accept and document. No grant, hook or `permissions.deny` is
added.

- The `Agent(...)` list stays in `orchestrator.md` as documentation of intent, and the agent says so.
- An audit compares the types the orchestrator actually launched (the `agentType` rows of
  `cq components session cost`) with the declared list and reports any type outside it on the
  `AUDIT` line of the orchestrator's totals. It runs in the orchestrator's own report because it
  already holds the cost verb, so no grant widens; the verifier sees one spec, not the whole run.
- 0007 stays as the historical record and carries a pointer to this decision.

## Consequence

The restriction is no longer claimed. An unexpected type is noticed after the fact, not prevented.
