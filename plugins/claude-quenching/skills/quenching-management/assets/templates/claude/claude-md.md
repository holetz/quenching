# CLAUDE.md — <repo name / scope>

<!-- ENGLISH ON INSTALL — CLAUDE.md is an agent-facing surface, so it stays
     English: keep the `##` section headings and prose in English (a repo may
     rename/reorder headings to fit its own outline, but does not translate them).
     KEEP CANONICAL folder names + frontmatter keys: `docs/` folder names in links
     (standards/decisions/vision/…) and any frontmatter keys are structural
     identifiers, so validation stays stable. The target's product code and
     docstrings stay the repo's own language — never rewritten. Delete this
     comment once filled in. -->

> Map: "what I, the agent, am doing now / which file contains what". Short
> directive + link, never the full detail. Within the line budget. Always
> loaded — every line spends context budget.

## Project shape

<Thin orienting POINTER, not an architecture narrative: what it is, stack, how it
is built/tested/deployed — only the non-obvious, in a few lines. Do NOT re-narrate
the architecture here (layer-by-layer structure, module/folder layout, design
detail): that lives on-demand in the standards/architecture layer this map links
below — orient and link, never restate what that on-demand layer owns.>

## Map by subfolder / scope

- [<subarea>/CLAUDE.md](<subarea>/CLAUDE.md) — <what it contains>
- …

## Architecture reference (current/active)

Current/active standards/contracts in <standards layer>; index in <index>. Retrieve
the canonical doc when you need the detail.

## Common commands

```
<command Claude cannot guess>
```

## House conventions

- <style rule that differs from the default> — see <owning doc>.
- Coding guardrails: see skill `quenching-guardrails`.

## "X defines Y" rule (if applicable)

<canonical source generates the artifact; the generated artifact is never edited by hand.>
