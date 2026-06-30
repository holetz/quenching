# Reference catalog — evolution of the `quenching-management` skill

> **Way back:** human entry → [../../README.md](../../README.md) · system
> design → [../../ARCHITECTURE.md](../../docs/method/architecture.md) · evolution spine →
> [../README.md](../README.md).

Research input for the [`quenching-evolutionist`](../../.claude/agents/quenching-evolutionist.md) agent to evolve the method of the [`quenching-management`](../../plugins/claude-quenching/skills/quenching-management/SKILL.md) skill. Documented techniques + citable sources (URL + date), prioritizing official Anthropic docs, organized by angle and mapped to evolution boundaries and the 15 template dimensions.

> **Generated on 2026-06-28** by the `deep-research` workflow: 13 research angles in parallel (WebSearch + WebFetch), each with adversarial anti-hallucination verification. **121 unique sources** (152 citations). This catalog is **living**: enrich it with each new case tackled.
>
> **Addendum 2026-06-29:** angle **15 — [Open Knowledge Format (OKF)](15-okf-google.md)** (Google Cloud, Jun/2026), via a new round of the `deep-research` workflow (6 angles, 25 claims verified / 0 refuted) + direct fetch of the primary spec. Boundary still **not addressed** by any round — registered as a candidate in the advancement backlog of the [spine](../README.md).

## Where to start

- **[00-evolution-fronts.md](00-evolution-fronts.md)** — the entry map: each candidate boundary from the spine (`../README.md`) → files and anchor sources; inverted index by dimension (1–14).
- **[SOURCES.md](SOURCES.md)** — consolidated bibliography by tier (official → engineering → spec → academic → community), with verification caveats.
- **Angle files (01–13)** — each contains a Synthesis + detailed Sources (key techniques, what it feeds) + Verification notes.

## Angle index

| # | File | Angle | Sources | Feeds |
| --- | --- | --- | --- | --- |
| 1 | [01-agent-skills.md](01-agent-skills.md) | Anthropic Agent Skills — authorship, structure and progressive disclosure | 11 | Dimension 6 (skills); boundaries "progressive disclosure / context budget" and "trigger optimization (subtrigger)" |
| 2 | [02-subagents.md](02-subagents.md) | Claude Code Subagents — design, tool scope and orchestration | 11 | Dimension 7 (sub-agents); boundary "skills vs sub-agents vs commands — decision guide" |
| 3 | [03-hooks.md](03-hooks.md) | Claude Code Hooks — deterministic lifecycle automation | 11 | Dimension 8 (hooks) |
| 4 | [04-claude-md-memory.md](04-claude-md-memory.md) | CLAUDE.md and Claude Code memory files | 12 | Dimension 1 (map/CLAUDE.md); boundary "progressive disclosure / context budget" |
| 5 | [05-slash-commands.md](05-slash-commands.md) | Custom Slash Commands in Claude Code | 12 | Dimension 9 (commands); boundary "skills vs sub-agents vs commands" |
| 6 | [06-mcp.md](06-mcp.md) | Model Context Protocol (MCP) in Claude Code | 11 | Candidate boundary "MCP coverage" (currently without a dimension) |
| 7 | [07-context-engineering.md](07-context-engineering.md) | Context engineering for agents (Anthropic) | 12 | Boundary "progressive disclosure / context budget"; dimensions 1/6/7 |
| 8 | [08-writing-tools-for-agents.md](08-writing-tools-for-agents.md) | Writing effective tools for agents (Anthropic) | 12 | Dimensions 6 and 7 (description as trigger contract; sub-agent return format) |
| 9 | [09-building-effective-agents.md](09-building-effective-agents.md) | Effective agent patterns and multi-agent systems | 12 | Dimension 7; method philosophy (audit+apply-with-confirmation; goal-driven) |
| 10 | [10-agents-md-interop.md](10-agents-md-interop.md) | AGENTS.md and cross-tool interoperability | 12 | Boundary "AGENTS.md / cross-tool interoperability"; dimension 1 |
| 11 | [11-memory-management.md](11-memory-management.md) | Persistent agent memory management (Anthropic) | 11 | Boundary "Memory hygiene"; dimension 10 (memory) |
| 12 | [12-knowledge-architecture-external.md](12-knowledge-architecture-external.md) | Knowledge architecture and documentation (external references) | 13 | Dimensions 2/3/4/5/12/13; boundary doctrine (single canonical home) |
| 13 | [13-skill-description-evals.md](13-skill-description-evals.md) | Description/trigger optimization and skill evaluation | 12 | Dimension 6 (skills); boundary "trigger optimization (subtrigger)" |
| 14 | [14-eval-fixtures.md](14-eval-fixtures.md) | Curator fixtures harness — detection (R12) + prescription (R34); planted profile → expected emphasis | 2 | Core/workflow (eval of the audit itself); Step 4 (fit-to-repo); dim 1/format |
| 15 | [15-okf-google.md](15-okf-google.md) | Open Knowledge Format (OKF v0.1, Google Cloud, Jun/2026) — open markdown+frontmatter format for agent knowledge | 12 | Dimension 11 (catalog); dims 2/10/12; candidate "AGENTS.md/interop" (knowledge × behavior) |

## How to enrich this catalog

As new cases are tackled, add material without breaking the pattern:
1. **New angle:** create `NN-<slug>.md` following the structure of existing ones (H1 → `## Synthesis` → `## Sources` → `## How it feeds the method evolution` → `## ⚠️ Verification notes`).
2. **Register in `00-frentes`** which boundary/dimension it serves, and in **`SOURCES.md`** the new sources.
3. **Re-running the research:** the workflow script is saved in `<session>/workflows/scripts/knowledge-catalog-claude-*.js` — edit the `ANGLES` list and re-invoke the Workflow to regenerate/expand.
4. **Always date** sources and maintain adversarial verification (the agent rule requires URL + date).

## Limits of this research (honesty)

- **Community** sources (60 of the 152) help find techniques, but are not normative — confirm against official docs before citing in a round.
- Verification covers URL existence, tier and summary fidelity; it does **not** revalidate that the practice is still current/active in the current version of Claude Code — product docs change.
- Snapshot of 2026-06-28: new skills/hooks/MCP resources may have emerged since; an old decision may be **superseded** in a future round (see the `supersedes Round N` rule in the agent).
