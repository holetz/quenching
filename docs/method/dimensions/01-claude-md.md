# Dimension 1 · CLAUDE.md entry map

The `CLAUDE.md` is the agent's **routing map** — the file that answers "what do I do
now, and which file holds what". It is the only artifact loaded into context *before
the first message of every session*.

> **Canonical home — the repo's `CLAUDE.md`(s) · Adaptive.** The method derives where
> they live and bends to the repo's language and prefixes; it does not relocate them.
> See [Fixed vs. adaptive](../architecture.md).

## Why it belongs in the method

Because it is **always loaded**, every line in CLAUDE.md spends a *fixed* slice of the
context budget on every turn, forever — unlike skills or `docs/`, which load on demand
only when relevant. Anthropic's own guidance frames CLAUDE.md as a place for the handful
of things the agent *cannot infer* — commands it can't guess, non-obvious gotchas, repo
etiquette — and warns against turning it into a contract or a tutorial
([Best practices](https://code.claude.com/docs/en/best-practices),
[Using CLAUDE.md files](https://claude.com/blog/using-claude-md-files)).

The deeper reason is **context economy**. Research on context engineering shows that an
agent's attention degrades as irrelevant tokens accumulate — a long, stale instruction
file doesn't just waste budget, it actively *poisons* every session it loads into
([Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).
The fix is **progressive disclosure**: keep the root a short map of short directives, and
push the detail behind links to on-demand homes — sub-`CLAUDE.md` by scope, skills for
procedures, `docs/` for standards
([How Claude remembers your project](https://code.claude.com/docs/en/memory),
[Set up Claude Code in a large codebase](https://code.claude.com/docs/en/large-codebases)).

## What "good" looks like

- The root is a **map, not a contract**: a short directive plus a link to the current
  detail, never the detail itself.
- It stays **within the repo's line ceiling** (a bundled hook validates this) and chains
  sub-`CLAUDE.md` by scope; every link resolves.
- Each line passes the **pruning test** — *"if I removed this line, would the agent make
  a mistake?"* If not, cut it or convert it: a mandatory rule becomes a
  [hook](08-hooks.md); a "when I do X I follow Y" procedure becomes a [skill](06-skills.md).
- The "common commands" it documents cite the single execution convention and link to the
  [`scripts/` map](08-hooks.md), rather than inlining build detail.

## How it drifts

- **Above the ceiling / became a contract** — long normative prose where a link belongs.
- **Fossil / context rot** — a directive describing a pattern the codebase already
  replaced, silently misleading every session.
- **Survives the pruning test** — a line that restates a model default, a linter rule, or
  an obvious practice.
- **Mandatory rule in prose that should be a hook** — guidance the model *can* ignore,
  where enforcement is needed.
- **Orphan or dangling sub-`CLAUDE.md`** — exists but unlinked, or linked but absent.

## How the method closes the gap

The method trims the root to a map, breaks scope into sub-files, prunes lines that fail
the test, and converts rules to hooks or procedures to skills. The payload is the
`quenching-map` skill plus the `validate-claude-md.py` line-ceiling hook and a CLAUDE.md
template — see [Bundled artifacts](../../plugin/artifacts.md).

## Sources

- [How Claude remembers your project — Claude Code Docs](https://code.claude.com/docs/en/memory) — Anthropic · accessed 2026-06-28
- [Best practices for Claude Code — Claude Code Docs](https://code.claude.com/docs/en/best-practices) — Anthropic · accessed 2026-06-28
- [Set up Claude Code in a monorepo or large codebase — Claude Code Docs](https://code.claude.com/docs/en/large-codebases) — Anthropic · accessed 2026-06-28
- [Using CLAUDE.md files: Customizing Claude Code for your codebase — Claude Blog](https://claude.com/blog/using-claude-md-files) — Anthropic · accessed 2026-06-28
- [Effective context engineering for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic · accessed 2026-06-28
