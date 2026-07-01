---
name: quenching-map
description: >-
  Creates, prunes, and chains CLAUDE.md files in a repo so they are a MAP (what
  I do now / which file contains what), not a contract. Applies the line-by-line
  pruning criterion, enforces the line ceiling, splits into sub-CLAUDE.md files
  by scope, fixes links and the root↔sub chain, and converts mandatory-rule-in-prose
  into a hook and long-procedure into a skill. Use when the user asks to "create/
  prune the CLAUDE.md", "the CLAUDE.md is too large", "prune the CLAUDE.md",
  "fix the CLAUDE.md links", "split the CLAUDE.md into sub-files", "update the
  repo map", or when a CLAUDE.md exceeded the ceiling / became a contract / has
  broken links / fossils.
when_to_use: >-
  keep CLAUDE.md files as a lean, chained, fossil-free map (CLAUDE.md hygiene /
  always-loaded context budget).
allowed-tools: Read, Grep, Glob, Edit, Write
---

# CLAUDE.md hygiene — the repo map

> Skill-template of the `quenching-management` method. Generic and portable:
> adapt the line ceiling and paths to the conventions of the repo where it is
> installed.

CLAUDE.md is **always-loaded** (enters the context on every session) — each
line spends a fixed budget. It is a **map**, not a contract: "what the agent
does now / which file contains what", with short-directive + link, never the
full detail. Knowledge that is only sometimes-relevant lives in **skills**
(on-demand).

## Pruning criterion (per line) — the central test

For **each line**, ask: *"If I remove this line, would Claude make a mistake?"*

- **No mistake ⇒ cut.** Model default, style already in the linter, obvious
  practice ("write clean code"), file-by-file description, long tutorial.
- **Mistake, but enforcement ⇒ convert to hook** (mandatory rule in prose:
  "always/never/before committing" → deterministic hook).
- **Mistake, but procedure ⇒ convert to skill** ("when I do X, I follow Y").
- **Mistake, and it's detail that always changes ⇒ becomes a link** to the
  current doc.
- **Mistake, and it's broad and stable ⇒ keep** (non-obvious command, environment
  quirk, specific architecture decision, branch/PR etiquette).

## Procedure

1. **Inventory** all CLAUDE.md files (`find . -name CLAUDE.md`) and measure size.
   Above the repo ceiling ⇒ prune/split.
2. **Prune** line-by-line by the criterion above; convert what is hook/skill/link.
3. **Check for fossils:** every directive that cites a standard — check the current
   standards layer whether the standard **is still the current one**; fossil =
   update/repoint.
4. **Chain:** knowledge about a subfolder goes into a sub-CLAUDE.md for that scope,
   pointed to from the root; each link must resolve.
5. **Fix broken links** and the root↔sub chain (pointed-but-missing and
   orphaned-but-unpointed).
6. **`@import` does not save context** — it expands inline; use only for human
   maintenance, not to "trim".

## What belongs / does not belong in CLAUDE.md

- ✅ non-obvious commands · style that differs from the default · test/runner ·
  repo etiquette · project-specific architecture · environment quirks · gotchas.
- ❌ what is inferred from the code · language default convention · detailed API
  (link instead) · volatile info · long explanation · file-by-file description ·
  obvious practice.

Keep each CLAUDE.md within the ceiling; if a validation hook exists
(`validate-claude-md.py`), it flags violations automatically.
