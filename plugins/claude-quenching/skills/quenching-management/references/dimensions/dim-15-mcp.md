# 15. External integration — MCP servers (.mcp.json)

> **Back path:** [../dimensions-template.md](../dimensions-template.md) (dimensions index +
> transversal doctrine) · [../../SKILL.md](../../SKILL.md) (agent roadmap).

- **Purpose:** the **external integration surface** the Claude Code agent can access in the session (tools, databases, APIs via Model Context Protocol). It is the only dimension of **dependency that lives outside the repo** but affects what the agent can do inside it.

- **How "good" looks:** servers the team should have stay in **`project` scope** (`.mcp.json` at the root, versioned and reviewed as infra code); secrets via `${VAR}`-expansion, **never hardcoded** in `env`/`headers`; minimal OAuth scope per server; the root CLAUDE.md declares **which** servers are expected and in which scope; in a corporate context there is a `managed-mcp.json` with an allowlist by `serverUrl`/`serverCommand` (not by `serverName`, which the user chooses).

- **Detection:** look for `.mcp.json` at the root; cross-reference with what CLAUDE.md documents and with the servers actually connected (`claude mcp list` / `/mcp`, outside of read-only — ask the user). Active server in the session **without** a versioned `project` entry = undeclared dependency (lives in `local`/`user` scope, invisible to the repo).

- **Smells:** MCP server connected but absent from `.mcp.json` (phantom dependency in `local`/`user` scope); credential/literal token in `env`/`headers` of the versioned `.mcp.json`; server that consumes external content (issues, web, messages, user data) **not** flagged as a prompt-injection vector in CLAUDE.md; corporate allowlist based only on `serverName`; `.mcp.json` edited without review (it is infra code).

- **Remediation:** promote expected server to `project` scope and version it; replace literal secret with `${VAR}`; declare expected servers in the root CLAUDE.md; flag external-content servers as injection vectors. The method **detects and proposes**; editing `.mcp.json`/secrets is a team decision.

- **Payload:** skill-template [../../assets/skills/quenching-config/](../../assets/skills/quenching-config/) (session configuration/`settings.json`/`.mcp.json`); the boundary/scope doctrine is signaled by the method core.
