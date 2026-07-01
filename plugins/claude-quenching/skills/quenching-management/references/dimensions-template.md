# Adaptable knowledge management template — the dimensions

> **Back path:** [../SKILL.md](../SKILL.md) (agent roadmap) ·
> human overview & architecture: the project docs site ·
> [README.md](README.md) (`references/` index).

> **ADAPTABLE — read this first.** This template **does not impose a foreign
> structure**. The method first **derives** the conventions from the target repo (Step 1
> of [SKILL.md](../SKILL.md): locates CLAUDE.md, discovers where each knowledge layer
> lives, inventories `.claude/`, reads the language/taxonomy) and only then
> confronts the dimensions below. **Where the repo already has its own convention, the
> repo's convention wins** — with **one exception**: the **names of `docs/` homes**
> (dim 2/3/5/11) are a **prescriptive canonical taxonomy**
> ([docs-taxonomy.md](docs-taxonomy.md)); there the repo **converges to the canonical name**
> (the variant name is deprecatable, **with OK** — never renamed without confirmation), not
> preserved as-is. The 15 dimensions are a **coverage checklist** (what a Claude Code-ready
> repo typically needs), not a rigid mold. In a greenfield repo, they become the roadmap to
> **install** the structure (stamping payloads from [../assets/](../assets/)); in an existing
> repo, they become the roadmap to **audit** what's there and **install** what's missing.

Each dimension has 6 fields:

- **Purpose** — what this artifact is for.
- **How "good" looks** — the healthy state (the audit target).
- **Detection** — where to look (operational detail, adaptive + bash, in [detection-and-smells.md](detection-and-smells.md)).
- **Smells** — signals of Partial/Drifted/Absent.
- **Remediation** — the concrete action.
- **Payload** — the artifact **from the package** ([../assets/](../assets/)) that the method **installs** to fill the gap; `—` = no payload, the method only proposes (human content decision).

> **`docs/` names are CANONICAL (dim 2/3/5/11), other paths are examples.**
> The `docs/` tree (`standards/`, `decisions/`, `vision/`, `backlog/`, `guides/`,
> `reference/`, `catalog/`, `communications/`, `presentations/`) is a **prescriptive
> canonical taxonomy** — single source in [docs-taxonomy.md](docs-taxonomy.md). In a
> repo with variant names (`docs/arquitetura/`, `docs/adr/`, `VISION.md`), the method
> **maps variant→canonical and PROPOSES the migration** (with OK), not preserving the
> repo's name. Paths **outside** `docs/` (`.claude/`, root) and the rule *«X defines Y»*
> (canonical source generates the artifact, the generated one is never hand-edited) are
> examples — derive/swap for the concrete pair of the repo in Step 1.

---

## The 15 dimensions — one file each

Each dimension lives in its **own file** under [dimensions/](dimensions/README.md) (six
fields: Purpose · How "good" looks · Detection · Smells · Remediation · Payload). Open
**only** the dimension you are scoring — the transversal doctrine above applies to all of
them. The `docs/`-family dimensions (2/3/5/11) additionally link to
[docs-taxonomy.md](docs-taxonomy.md) (the canonical tree); dim 8 links to
[scripts-taxonomy.md](scripts-taxonomy.md); the per-dimension bash lives in
[detection-and-smells.md](detection-and-smells.md).

| # | Dimension | File | Detection block |
| --- | --- | --- | --- |
| 1 | Entry map — CLAUDE.md | [dimensions/dim-01-claude-md.md](dimensions/dim-01-claude-md.md) | 1b |
| 2 | Standards — `docs/standards/` | [dimensions/dim-02-standards.md](dimensions/dim-02-standards.md) | 2b |
| 3 | Vision — `docs/vision/` | [dimensions/dim-03-vision.md](dimensions/dim-03-vision.md) | (2b family) |
| 4 | What's missing — backlog | [dimensions/dim-04-backlog.md](dimensions/dim-04-backlog.md) | (2b family) |
| 5 | Open decisions — `docs/decisions/` | [dimensions/dim-05-decisions.md](dimensions/dim-05-decisions.md) | (2b family) |
| 6 | Skills — `.claude/skills/` | [dimensions/dim-06-skills.md](dimensions/dim-06-skills.md) | 6b |
| 7 | Sub-agents — `.claude/agents/` | [dimensions/dim-07-subagents.md](dimensions/dim-07-subagents.md) | 7b |
| 8 | Hooks — `.claude/settings.json` + `scripts/` | [dimensions/dim-08-hooks.md](dimensions/dim-08-hooks.md) | 8b |
| 9 | Commands — `.claude/commands/` | [dimensions/dim-09-commands.md](dimensions/dim-09-commands.md) | 9b |
| 10 | Memory — memory directory + index | [dimensions/dim-10-memory.md](dimensions/dim-10-memory.md) | (see dim 10) |
| 11 | Data / domain catalog — `docs/catalog/` | [dimensions/dim-11-catalog.md](dimensions/dim-11-catalog.md) | (2b family) |
| 12 | Boundary doctrine — transversal *(method core)* | [dimensions/dim-12-boundaries.md](dimensions/dim-12-boundaries.md) | (see dim 12) |
| 13 | Derived conventions — code + naming | [dimensions/dim-13-conventions.md](dimensions/dim-13-conventions.md) | — |
| 14 | Behavioral guardrails — how the LLM should code | [dimensions/dim-14-guardrails.md](dimensions/dim-14-guardrails.md) | 14b |
| 15 | External integration — MCP servers (`.mcp.json`) | [dimensions/dim-15-mcp.md](dimensions/dim-15-mcp.md) | (see dim 15) |

---

## How the method scores (summary)

For each dimension, assign **Present / Partial / Drifted / Absent** with evidence
`file:line`. The operational rule for the four states and the adaptive globs/greps
per dimension are in [detection-and-smells.md](detection-and-smells.md). The final report
follows [report-format.md](report-format.md); the gap → payload map and the deprecation
doctrine are in [installation.md](installation.md).
