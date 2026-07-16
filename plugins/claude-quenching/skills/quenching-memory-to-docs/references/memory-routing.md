# Memory routing — from a memory file to an OKF home

How `quenching-memory-to-docs` turns each project-memory file into a concept doc in the right
OKF home. **Content decides the home**; the memory's `metadata.type` is only a hint. Once the
home is chosen, the concept is filed exactly as `quenching-insert` would — see
[../../quenching-insert/references/homes.md](../../quenching-insert/references/homes.md) for the
`type`/mold/path shape and the index/log procedure, and
[../../quenching-align/references/taxonomy.md](../../quenching-align/references/taxonomy.md) for the
boundaries.

This skill writes to **only four homes** — `standards/`, `decisions/`, `backlog/`, `knowledge/`.
`vision/`, `documentation/`, `reference/` (and `catalog/`) are out of
scope; collapse to the nearest of the four (below) or flag-and-keep.

## The memory file

A Claude Code project memory lives under
`~/.claude/projects/<encoded-cwd>/memory/` as one fact per `.md` file with frontmatter:

```yaml
---
name: <kebab-slug>
description: <one-line summary>
metadata:
  type: user | feedback | project | reference
---
<the fact; feedback/project add **Why:** and **How to apply:** lines; [[links]] to siblings>
```

`MEMORY.md` (same folder) is the index — one `- [Title](file.md) — hook` line per memory.

## Routing table — memory `type` → likely home (content overrides)

| Memory `type` | What it holds | Likely OKF home | OKF `type` |
| --- | --- | --- | --- |
| `feedback` | how you should work (a correction / confirmed approach, with a why) | a durable working rule → `standards/workflows/` (or `standards/code`, `standards/quality` by subject); a step-by-step *how WE work* → `standards/workflows/`; an explanation of *why* → `knowledge/` | `standard` / `knowledge` |
| `project` | ongoing work, goals, constraints not derivable from code/git | a **thing to explore or build** → `backlog/` (a `task`, **always untriaged** — inventing a priority the human never stated would violate anti-fabrication); an **open decision** → `decisions/`; a **binding constraint/rule** → `standards/`; **direction** (no deadline) → `knowledge/` (this skill emits no `vision/`) | `task` / `decision` / `standard` / `knowledge` |
| `reference` | pointer to an external resource (URL, dashboard, ticket, tool, lib) | facts about a **named tool/lib/regulation we consume** collapse into `knowledge/` (this skill emits no `reference/` docs) | `knowledge` |
| `user` | who the user is (role, expertise, preferences) | **usually not repo docs** — personal/session context. Only migrate a **durable, team-relevant** fact (a role convention, an authority) → `knowledge/` or `standards/workflows/`. Otherwise **flag and ask**; never silently delete a `user` memory. | `knowledge` / `standard` |

### Tie-breakers (four homes only)
- "how **WE** do it" (proven, current) → `standards/`; open with alternatives → `decisions/`.
- a fact about a **named external** asset we consume → **collapses into `knowledge/`** (no `reference/` output).
- a **thing to explore or build** → `backlog/` (a `task`, always untriaged); **direction** (no deadline) → `knowledge/` (this skill emits no `vision/`); a **procedure** for how WE work → `standards/workflows/`, else `knowledge/` (no `documentation/` output).
- If a memory carries **several** facts, split it — one concept per file across the right homes.
- Anything that fits **none** of the four → flag-and-keep (do not fabricate an out-of-scope doc).

## Salvaging content

A memory is terse. When promoting it to a concept doc:
- **Derive `resource` honestly** — from the URL/ticket/tool the memory names, the code glob it
  concerns, or the domain. Never fabricate; a memory with no locatable asset gets a domain
  descriptor as `resource`, or `authority: background` if it is background understanding.
- **`source`** = the memory's origin if recorded, else "project memory".
- **`timestamp`** = today (memories store when written; if the body gives a date, keep it in the body).
- Keep the memory's `**Why:**`/`**How to apply:**` prose in the doc body — that is the salvage.
- Resolve `[[links]]` to the sibling memories' new doc paths when those are migrated in the same
  run; leave the human a note for any that stay in memory.

## Deletion contract

A memory is removed **only after** its concept doc is written and passes the conformance
self-check. For each migrated memory: delete its `.md` file and prune its `- [..](..)` line from
`MEMORY.md`. Leave `MEMORY.md` in place even if it ends empty. A memory that could **not** be
routed (no documentary home, a `user` fact the human did not clear, or one that only fits an
out-of-scope home — `vision`/`documentation`/`reference`/`catalog` — and
cannot be collapsed into one of the four) **stays** — report it, never delete it.
