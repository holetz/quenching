# The 15 dimensions

The method's coverage checklist. Each dimension is a facet of a repository's
**knowledge surface**; the audit scores every one of them (full coverage), and
the report then **modulates emphasis** by the repo's profile (see
[the workflow](workflow.md), Step 4).

| # | Dimension | What it covers | Package artifact |
| --- | --- | --- | --- |
| 1 | CLAUDE.md / context budget | the map (root + sub-CLAUDE.md), progressive disclosure, pruning | `quenching-map` skill + `validate-claude-md.py` hook |
| 2 | Normative reference & `docs/` | the canonical `docs/` taxonomy (standards, decisions, vision, backlog, guides, reference, catalog, communications, presentations) | `quenching-docs`, `quenching-standards`, `quenching-announcement` skills + `docs/` scaffold |
| 3 | Direction / VISION | where the repo is heading | — (proposes only; human content) |
| 4 | Backlog | tracked, prioritized work | `docs/backlog/` scaffold |
| 5 | ADR / decisions | recorded architectural decisions | `docs/decisions/` scaffold |
| 6 | Skills | trigger-routed capabilities, no bloat | `quenching-skills` skill (+ domain-artifact recognition) |
| 7 | Sub-agents | isolated-context workers with a return contract | `quenching-auditor`, `quenching-writer` workers |
| 8 | Hooks (+ `scripts/` home) | lifecycle/tool-event automation; executable-logic taxonomy | the 6 bundled hooks + `scripts/` scaffold |
| 9 | Commands | composable, model-invocable steps | `quenching-reaudit` command-skill |
| 10 | Memory | hygiene, load ceiling, CLAUDE.md × Auto Memory boundary | — (proposes only; human content) |
| 11 | Catalog / domain | generated × curated separation, consumption doctrine | `docs/catalog/` scaffold + templates |
| 12 | Boundary doctrine | map × current × direction × decision; single home | — (proposes the home; human content) |
| 13 | Conventions | naming/prefix taxonomy, frontmatter | `quenching-map` skill + frontmatter templates |
| 14 | Guardrails | behavioral rules + deterministic enforcement | `quenching-guardrails` skill + `protect-generated.py` hook |
| 15 | MCP | versioned `.mcp.json`, secrets via `${VAR}`, allowlist | `quenching-config` skill |

> **Three dimensions never install (3 · 10 · 12)** — they are **human content
> decisions**. The method only **proposes** the text/diff; the repo writes it.
> This is the limit "modulate the METHOD, never define the CONTENT".

The full, self-contained catalog — each dimension with purpose · what "good"
looks like · detection · smells · remediation · payload — lives in the skill's
[`references/dimensions-template.md`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/dimensions-template.md).
