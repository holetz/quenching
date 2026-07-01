# Dimension 7 · Sub-agents

A sub-agent is **isolated work that keeps the parent's context clean** — it runs in its own
context window and returns only a condensed result. It is the home for verbose, disposable
work: a log sweep or dependency scan happens in isolation, and the parent gets the summary,
not the dump.

> **Canonical home — `.claude/agents/` · Adaptive.** Naming and model choice follow the
> repo; the method ships generic molds, not domain workers. See
> [Fixed vs. adaptive](../architecture.md).

## Why it belongs in the method

The reason to spawn a sub-agent is **context economy under isolation**: a noisy side task
(scanning a hundred files, reading a long log) would flood the main thread with tokens the
agent will never reference again. Run it in a separate window and the parent receives only
the high-signal result ([Create custom subagents](https://code.claude.com/docs/en/sub-agents),
[How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)).

That makes the **return contract** the whole game. A good sub-agent returns a *condensed
summary* of high-entropy fields — never the dump of what it read — and uses **semantic
identifiers** the parent understands (`file:line`, slug, name), not opaque IDs, which
measurably reduces hallucination downstream. There's a simple violation detector: if the
return is close in size to the context it consumed, isolation was breached — it became a
read proxy, not a condensing worker. Anthropic's guidance also cautions that multi-agent
structure is a cost, not a default — reach for it when isolation pays, not reflexively
([Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)).

## What "good" looks like

- Complete frontmatter (`name` / `description` / `tools` / `model`); body = role + inputs +
  numbered steps + an **explicit return format**.
- `tools` **minimal and always declared** — without the field, a sub-agent inherits *all*
  the parent's tools, breaking least-privilege.
- A read-only audit profile is Explore-like: `Read, Grep, Glob`, a cheap model, plan mode.
- Invoked by a sibling skill — not orphaned.

## How it drifts

- **No return format**, or a **flooding return** that hands back everything it read.
- **Opaque identifiers** (UUID/hash) in the return instead of `file:line`/slug.
- **Missing `tools`** — inherits everything; or overly broad tools.
- **Wrong home** — a sub-agent for a step the operator needs to direct (should be a skill),
  or a skill dumping verbose output into the main context (should be a sub-agent).

## How the method closes the gap

It fixes the return contract, declares minimal tools, assigns a cheap model to audit
profiles, and moves work to the right home. The payload is the `quenching-auditor` read-only
mold and an agent template, authored with the `quenching-skills` discipline — see
[Bundled artifacts](../../plugin/artifacts.md).

## Sources

- [Create custom subagents — Claude Code Docs](https://code.claude.com/docs/en/sub-agents) — Anthropic · accessed 2026-06-28
- [How we built our multi-agent research system — Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system) — Anthropic · 2025-06-13
- [Building effective agents — Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents) — Anthropic · accessed 2026-06-28
- [Orchestrate teams of Claude Code sessions — Claude Code Docs](https://code.claude.com/docs/en/agent-teams) — Anthropic · accessed 2026-06-28
