# assets/templates/ — method templates

The **molds** that the [`quenching-management`](../../SKILL.md) method uses to shape the
artifacts of the target repo live here — **centralized** and organized by
**destination surface**. Two types coexist:

- **Header fragments** (`claude/`, `memory/`, `docs/docs-front.md`,
  `docs/standards-front.md`, `docs/decisions/adr.md`, `docs/backlog/backlog-item.md`) — the canonical
  frontmatter for an artifact type. The method **stamps** them at the top of the
  artifact **where missing**; they do not become standalone files in the target.
  They are the minimal form that makes the artifact **discoverable/routable**
  (the skill/agent `description` is routing code — dim 6/7) and **provenanced**
  (`audience`/`authority`/`updated` in docs — dim 2/12).
- **Body molds** (`docs/sidecar.md`, `docs/vision/area.md`,
  `docs/catalog/{system,schema,table}.md`) — the **full** skeleton of a page.
  These are **method templates, applied by the `quenching-docs` skill** on demand;
  the `docs/` skeleton does **not** ship them co-located anymore (they were
  centralized here).

> **These are not "assets" in this skill.** They live under `assets/` (≥2 levels
> deep), so Claude Code does **not** discover them as live skills/agents — they are
> **templates**, applied when the method runs, never final ready-to-use files.

## Naming logic

**The directory says WHERE (the destination surface); the file says WHAT (the artifact
the mold produces)** — noun in **English**, **kebab-case**, **no `_` prefix**. The
canonical `docs/` taxonomy is already all English (`decisions/`, `vision/`,
`backlog/`, `catalog/`…); file names follow it.

```
templates/
  claude/          # harness surface (.claude/ + CLAUDE.md)
    claude-md.md  skill.md  agent.md  quenching-manifest.json
  docs/            # mirrors the docs/ taxonomy
    docs-front.md  standards-front.md  sidecar.md
    decisions/adr.md   backlog/backlog-item.md   vision/area.md
    catalog/system.md  catalog/schema.md  catalog/table.md
  memory/          # agent memory store
    memory.md
```

## Inventory

| Path | Mold for | Applied in | Covers |
| --- | --- | --- | --- |
| `claude/claude-md.md` | CLAUDE.md skeleton | any `CLAUDE.md`/sub-`CLAUDE.md` | 1, 13 |
| `claude/skill.md` | skill frontmatter | `.claude/skills/<name>/SKILL.md` | 6 |
| `claude/agent.md` | sub-agent frontmatter | `.claude/agents/<name>.md` | 6, 7 |
| `claude/quenching-manifest.json` | install receipt (manifest) | `.claude/quenching-manifest.json` | core (lifecycle: reconcile/upgrade, consent mode, channel) |
| `docs/docs-front.md` | doc/folder frontmatter for `docs/` | header of any doc/`README` in `docs/` | 2, 12 |
| `docs/standards-front.md` | full mandatory OKF frontmatter for a standard | header of any `docs/standards/**` standard | 2, 13 |
| `docs/sidecar.md` | textual extract alongside binary | `presentations/`, `reference/regulations/` | 2, 12 |
| `docs/decisions/adr.md` | ADR frontmatter | `docs/decisions/*.md` | 5 |
| `docs/backlog/backlog-item.md` | backlog item frontmatter | `docs/backlog/**` | 4 |
| `docs/vision/area.md` | area direction shell | `docs/vision/<area>.md` | 3 |
| `docs/catalog/system.md` | system access card | `<system>/README.md` | 11 |
| `docs/catalog/schema.md` | consolidated schema index | `<system>/<catalog>/<schema>.md` | 11 |
| `docs/catalog/table.md` | detailed table page | `<system>/<catalog>/<schema>/<table>.md` | 11 |
| `memory/memory.md` | memory entry | agent memory (`MEMORY.md`/store) | 10 |

## How to apply (summary)

1. **Header** (fragments): copy the frontmatter to the top of the artifact **where
   missing** — do not overwrite one that is already filled in and correct; complete
   the missing fields.
2. **Body** (page molds): `docs/sidecar.md`, `docs/vision/area.md` and
   `docs/catalog/*` are applied by the `quenching-docs` skill when creating the page —
   they start **here**, not from the target.
3. **Fill in the placeholders** (`<...>`) and **remove the inline guidance comments**
   after deciding the value.
4. **Derive enums to the repo**: the `type` in `memory.md` and the labels in
   `docs-front.md` (`audience`/`authority`) follow the taxonomy detected in Step 0
   — do not force this method's list.
5. **Keep the agent-facing text English** (`audience: agent`/`both` — the majority
   of these molds); only `audience: human` material follows the repo's language.
   **Field names** stay stable (keys in English) to match the validation hooks
   (dim 8).
6. Keep the skill/agent `description` as **routing code** (dim 6):
   third person, literal triggers, exclusion against neighboring skills.
