# assets/skills/ — skill-template payloads of the method

The **skills** the [`quenching-management`](../../SKILL.md) method installs into the
target repo live here, one folder per skill (`<skill>/SKILL.md`). These are the
**on-demand steps** that **APPLY** changes to the knowledge base **with human
OK** — the only link in the cycle that mutates the base (the hook only observes/
proposes; the sub-agent only returns a summary). Each is a **template**: the
`description` is routing code (dim 6 — 3rd person, what-it-does + when-to-use +
user literal phrases + exclusion clause against neighbors) and the internal paths
are **derived to the target** in Step 0.

> **Not "active" in this skill.** They live under `assets/skills/` (≥2 levels
> below), so Claude Code **does not** discover them as live skills — they are
> **payloads**, copied to `.claude/skills/<prefix>-<name>/` of the target when
> the method is applied.

## Inventory

| Path | Installs in | Addresses dimension |
| --- | --- | --- |
| `quenching-map/` | `.claude/skills/<prefix>-mapa/` | 1 (CLAUDE.md as map, not contract), 13 (conventions) — line-by-line pruning, ceiling, root↔sub chain, prose-rule → hook |
| `quenching-docs/` | `.claude/skills/<prefix>-docs/` | 2, 4, 5, 11, 13 — docs-as-code: current reference, backlog, ADR, direction, domain; one Diátaxis quadrant per artifact + index |
| `quenching-standards/` | `.claude/skills/<prefix>-standards/` | 2 — orchestrator: builds/updates the ENTIRE `standards/` layer (fan-out of `quenching-writer` per topic in parallel + `INDEX.md` regenerated from disk) |
| `quenching-announcement/` | `.claude/skills/<prefix>-announcement/` | 2 — DIRECTED/outbound communication: reads the CHANNEL template and fills it |
| `quenching-skills/` | `.claude/skills/<prefix>-skills/` | 6, 7, 9 — creates/edits skills, sub-agents and commands; description-as-routing + trigger testing + home choice + tools least-privilege |
| `quenching-config/` | `.claude/skills/<prefix>-config/` | 8 (hooks), 15 (MCP) — settings.json, hooks, `.mcp.json` in project scope with secrets via `${VAR}` |
| `quenching-guardrails/` | `.claude/skills/<prefix>-guardrails/` | 14 — Think-Before-Coding, Simplicity First, Surgical Changes, Goal-Driven Execution |

## One skill per operable dimension — orchestrator apart

Six skills each cover **one dimension (or a cohesive trio)**; `quenching-docs`
edits **ONE** artifact at a time. `quenching-standards` is the **orchestrator** —
it doesn't edit one doc, it edits the entire `standards/` layer via fan-out of
the `quenching-writer` sub-agent (from [../agents/](../agents/README.md)).
Distinguish them in Step 0: *"document ONE standard"* → `quenching-docs`;
*"build/update the standards layer"* → `quenching-standards`.

## How to install (summary)

1. **Copy** the skill folder to `.claude/skills/<prefix>-<name>/` of the target.
2. **Rename** folder/`name` to the derived taxonomy (`<prefix>`); the
   `description` is **agent routing code → keep it English**, keeping the
   **literal trigger phrases** users of that repo would actually type so routing
   still fires.
3. **Fix the internal paths** in `SKILL.md` (`docs/` layers, reference, sub-agent
   names referenced by `agent:`) to the real shape derived in Step 0 of
   [../../references/detection-and-smells.md](../../references/detection-and-smells.md).
4. If the skill does fan-out (`quenching-standards`), **ensure the sub-agent**
   (`quenching-writer`) is also installed in `.claude/agents/` of the target.
5. If the repo already had an equivalent skill, **deprecate it** (do not remove
   without OK) — deprecation doctrine in
   [../../references/installation.md](../../references/installation.md).
