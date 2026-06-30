# Dimension 15 — MCP

> Part of the `quenching-management` evolution log. Index, anchor state, and backlog: [../README.md](../README.md). ID convention (R*/Rev*) and routing: [README.md](README.md).
>
> This file collects the rounds (`R*`) and revisions (`Rev*`) that touched **MCP server coverage / `.mcp.json`**.

## Current state

> Active summary of each boundary in this dimension (what is valid today). Detail and rationale are in the history below.

- **R1 · MCP coverage** — dimension 15 (MCP servers/`.mcp.json`): `project`-scoped
  and versioned, secret via `${VAR}`, ghost dependency (active server outside
  `.mcp.json`), prompt-injection vector, allowlist by `serverUrl`. Owner:
  `update-config`. (round 1)

## Round and revision history

> Most recent rounds at the top. Revisions (`Rev*`) are nested under the round they refine.

### Round 1 — 2026-06-28 · boundary: MCP coverage

- **Change:** new **dimension 15 — "External integration — MCP servers
  (.mcp.json)"** in `dimensions-template.md` (purpose/good/detection/smells/
  remediation/owner=`update-config`); count "14→15" adjusted in `SKILL.md`
  (Step 2 and References); detection command 15 in `detection-and-smells.md`
  (`.mcp.json`/`managed-mcp.json`, literal-secret grep, mention in CLAUDE.md);
  MCP→`update-config` delegation line in `delegation.md`. Conceptual diff: the
  method now sees the **external integration surface** — the only dependency that
  lives outside the repo but decides what the agent can do inside it.
- **Why:** the 14 dimensions covered only internal artifacts; an MCP server active
  in the session (e.g., `context7` in this repo) without a versioned `project`
  entry is a **ghost dependency** (scope `local`/`user`, invisible to the repo) and
  an uncatalogued prompt-injection vector. The repo **does not have** `.mcp.json`
  or `managed-mcp.json` (confirmed by Glob) even though it uses MCP — a real gap.
- **Sources:** [Connect Claude Code to tools via MCP — Claude Code Docs](https://code.claude.com/docs/en/mcp)
  (accessed 2026-06-28) — confirms the 3 scopes `local`/`project`/`user`, `.mcp.json`
  at the root as "designed to be checked into version control", `${VAR}` expansion
  for secrets, `claude mcp list`/`/mcp`; [Control MCP server access — Claude Code
  Docs](https://code.claude.com/docs/en/managed-mcp) (accessed 2026-06-28) —
  `managed-mcp.json`, allowlist by `serverUrl`/`serverCommand` (`serverName` is not
  a security control). Catalogue: `research/06-mcp.md`.
- **Rejected/superseded:** discarded creating a **complete MCP security dimension**
  (tool-poisoning, rug-pull, `mcp-scan`, confused-deputy) — that is pentest scope,
  not knowledge management (Simplicity First; the dimension signals the injection
  vector, it does not audit exploits). Discarded assigning owner "—" to the
  dimension: `.mcp.json` is session config, naturally falls under `update-config`
  (existing owner).
- **Next candidate:** "Boundary detection by heuristic" (refine dimension 12 with
  concrete checks) or "Memory hygiene" (refine dimension 10).
