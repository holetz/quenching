# Dimension 13 · Conventions

Conventions are the **house rules the repo already follows** — import style, the
product code's language, naming, pins, the *"X defines Y"* rule. (Here "language"
means the *product code's* language, which the repo owns — the standards docs that
capture these conventions are themselves an agent-facing surface written in English.)
The dimension is about making the implicit explicit and keeping each rule in exactly
one owning doc.

> **Canonical home — `docs/standards/` (code & naming) cited from CLAUDE.md · Adaptive.**
> The conventions are the repo's own; the method captures and links them, it doesn't invent
> them. See [Fixed vs. adaptive](../architecture.md).

## Why it belongs in the method

A convention the team follows but never wrote down is invisible to the agent — so it
re-derives it, inconsistently, every session. Anthropic's guidance is to capture the
non-obvious house rules an agent can't infer and to keep them where they'll actually be read
([Best practices for Claude Code](https://code.claude.com/docs/en/best-practices)). The
skill-authoring guidance generalizes the discipline: a convention, like a skill description,
is most useful when it is **specific, single-sourced, and referenced** rather than restated
([Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

The method's contribution is the **single-home rule** applied to conventions: each one has
an owning doc in the [standards layer](02-standards.md), and CLAUDE.md
**cites it with a short directive + link** rather than copying the rule. Two docs stating
the same convention with different wording is the drift this dimension hunts.

## What "good" looks like

- Conventions are **explicit and unique**, each with an owning doc in the standards layer.
- CLAUDE.md cites them with a short directive and a link — not a copy.

## How it drifts

- **Practiced but not written** — a convention the code follows that lives nowhere.
- **Two docs, same convention, diverging.**
- **Cited in CLAUDE.md with no current doc behind it.**

## How the method closes the gap

It writes or unifies each convention in its owning doc and replaces copies with links. The
payload is the `quenching-docs` skill and the frontmatter/naming templates — see
[Bundled artifacts](../../plugin/artifacts.md).

## Sources

- [Best practices for Claude Code — Claude Code Docs](https://code.claude.com/docs/en/best-practices) — Anthropic · accessed 2026-06-28
- [Skill authoring best practices — Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — Anthropic · accessed 2026-06-28
- [Agent Skills Specification — agentskills.io](https://agentskills.io/specification) — accessed 2026-06-28
