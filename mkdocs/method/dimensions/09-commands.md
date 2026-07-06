# Dimension 9 · Commands

A command is a **shortcut for a flow** — invocable by the user as `/name` and, when
authorized, by Claude itself during a conversation. That second path is the point: a
command is a **composable building block** a skill, sub-agent or method step can chain,
not just a manual shortcut.

> **Canonical home — `.claude/commands/` (legacy) or `.claude/skills/<name>/` · Adaptive.**
> Naming follows the repo; the healthy default is that a new command is *born a skill*. See
> [Fixed vs. adaptive](../architecture.md).

## Why it belongs in the method

Modern Claude Code blurs the line between commands and skills on purpose: a slash command
defined as a skill gets an **auto-trigger** from its description and a support directory for
detail, while a bare `.md` command gets neither
([Slash Commands in the SDK](https://code.claude.com/docs/en/agent-sdk/slash-commands),
[Extend Claude with skills](https://code.claude.com/docs/en/skills)). So the method applies
a **migration criterion**: a command becomes a skill when it would benefit from
auto-trigger, when it outgrows ~50 lines or references external files, or when it gets
copied across repos. A pure manual side-effect shortcut (deploy/commit) stays a command —
and carries `disable-model-invocation: true` so the model can't fire it on its own.

The subtle failures are about **exposure**. Because the same description that drives
auto-trigger also lets the model *compose* a command into a larger flow, a weak description
leaves the building block inert; and a read-only step that *should* be chainable but is
gated with `disable-model-invocation` silently disappears from the model's toolset. The
descriptions also share a context budget (~1% of the window), so an inflated command can
get its routing keywords truncated.

## What "good" looks like

- New flows are **born as skills** (auto-triggerable); legacy `.md` commands are reserved
  for pure manual side-effects and carry `disable-model-invocation: true`.
- Each command mirrors a live skill/flow; minimal frontmatter (`description`,
  `allowed-tools`, `argument-hint`).
- Read-only, composable steps stay **un-gated** so the model can chain them.

## How it drifts

- **Migratable legacy command** — passes the migration criterion but still lives in
  `commands/`.
- **Gated-composable** — a read-only step hidden from the model by
  `disable-model-invocation`.
- **Auto-invocable side-effect** — a deploy/commit command *without* the flag.
- **Basename collision / silent shadowing** of a bundled skill name.

## How the method closes the gap

It migrates qualifying commands to skills, un-gates composable steps, gates side-effects, and
resolves name collisions. The method also **ships** the example: the `quenching-reaudit`
command-skill — read-only, auto-invocable, chainable — see
[Bundled artifacts](../../plugin/artifacts.md).

## Sources

- [Slash Commands in the SDK — Claude Code Docs](https://code.claude.com/docs/en/agent-sdk/slash-commands) — Anthropic · accessed 2026-06-28
- [Extend Claude with skills — Claude Code Docs](https://code.claude.com/docs/en/skills) — Anthropic · accessed 2026-06-28
- [Steering Claude Code: skills, hooks, subagents and more — Anthropic Blog](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more) — Anthropic · accessed 2026-06-28
- [Agent Skills Specification — agentskills.io](https://agentskills.io/specification) — accessed 2026-06-28
