# Dimension 10 · Memory

Memory is **what the agent discovered while working** — build commands, debug insights,
project constraints, user preferences — kept durable between sessions and machine-local. It
is the counterpart of CLAUDE.md: CLAUDE.md is what *any teammate* needs (versioned); memory
is what *the agent learned* (local).

> **Canonical home — the project memory directory + `MEMORY.md` index · Adaptive.** The
> type prefixes and path are derived from the repo. The method **signals**, it does not
> write memory. See [Fixed vs. adaptive](../architecture.md).

## Why it belongs in the method

Memory is powerful and dangerous for the same reason: it persists. Done well, it is the
mechanism that lets an agent carry hard-won context across sessions without re-deriving it
([Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool),
[Managing context on the Claude Developer Platform](https://claude.com/blog/context-management)).
Done badly, it is a vector for **context poisoning**: a stale or wrong memory loads into
every future session and quietly corrupts the agent's view of the project
([Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

So the method treats memory as a **hygiene** problem with a load ceiling. The index is read
at startup but only its first slice loads — so each entry must be one short line (title +
hook + link), with detail in topic files read on demand. And because memory shares the
surface with CLAUDE.md and `docs/`, its cardinal sin is **duplication**: a memory that
repeats something already in the code or the standards should *link* to it, not copy it
(the [boundary doctrine](12-boundary-doctrine.md) applied to memory).

## What "good" looks like

- The `MEMORY.md` index has **one short line per memory**, within the load ceiling; detail
  lives in on-demand topic files.
- Each entry is **dated, with provenance**, and named by a type prefix the repo adopts.
- It **references** what already lives in the repo (`@path`/link) rather than duplicating it.

## How it drifts

- **Index orphan** — a topic file with no index line, or an index past the load ceiling.
- **Duplicates the repo** instead of linking.
- **Vague temporal reference** — "recently"/"last time" instead of an exact date.
- **Silent conflict** — two contradictory entries left to last-write-wins.
- **Degraded freshness** — an expired fact poisoning future context.

## How the method closes the gap

This is a **human content decision**: the method **points out** the smell and the
`file:line`, but writing and pruning memory is the job of the memory flow (`/memory`), not
this method. There is no install payload — only a signal and an optional entry template. See
[Bundled artifacts](../../plugin/artifacts.md).

## Sources

- [Memory tool — Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) — Anthropic · accessed 2026-06-28
- [Managing context on the Claude Developer Platform — Anthropic News](https://claude.com/blog/context-management) — Anthropic · accessed 2026-06-28
- [Context engineering: memory, compaction, and tool clearing — Claude Cookbook](https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools) — Anthropic · accessed 2026-06-28
- [Effective context engineering for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic · accessed 2026-06-28
