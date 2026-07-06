# Dimension 15 · MCP — external integration

MCP servers are the **external surface** the agent can reach in a session — tools,
databases, APIs via the Model Context Protocol. This is the one dimension whose dependency
lives *outside* the repo yet shapes what the agent can do *inside* it.

> **Canonical home — `.mcp.json` at the repo root · Adaptive.** Which servers a repo
> declares is the repo's choice; the method enforces *how* they're declared, not *which*.
> See [Fixed vs. adaptive](../architecture.md).

## Why it belongs in the method

An MCP server expands the agent's reach — and its attack surface — so the method treats
`.mcp.json` as **infrastructure code**: versioned in `project` scope, reviewed, with secrets
injected via `${VAR}` expansion and never hardcoded
([Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp),
[Control MCP server access](https://code.claude.com/docs/en/managed-mcp)). A server that's
connected in a session but absent from the versioned config is a **phantom dependency** —
it lives in someone's local scope, invisible to the repo and to everyone else.

The sharper reason is **security**. Any server that pulls in external content — issues, web
pages, messages, user data — is a **prompt-injection vector**, and the protocol's own
threat modeling and the OWASP MCP guidance both treat untrusted MCP input as a first-class
risk ([MCP Security Best Practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices),
[OWASP MCP Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html)).
The method's rule is that CLAUDE.md must declare which servers are expected and flag the
external-content ones as injection vectors.

## What "good" looks like

- Team servers in **`project` scope** (`.mcp.json` at root), versioned and reviewed as infra.
- Secrets via `${VAR}` expansion — **never** literals in `env`/`headers`; minimal OAuth scope.
- The root CLAUDE.md declares which servers are expected and in which scope.
- External-content servers are **flagged as prompt-injection vectors**.

## How it drifts

- **Phantom dependency** — a server connected in-session but absent from `.mcp.json`.
- **Hardcoded secret** in a versioned `.mcp.json`.
- **External-content server not flagged** as an injection vector in CLAUDE.md.
- **`.mcp.json` edited without review** — it is infra code.

## How the method closes the gap

It **detects and proposes** — promote expected servers to `project` scope, replace literal
secrets with `${VAR}`, declare expected servers in CLAUDE.md, flag injection vectors — but
editing `.mcp.json` and secrets stays a team decision. The payload is the `quenching-config`
skill — see [Bundled artifacts](../../plugin/artifacts.md).

## Sources

- [Connect Claude Code to tools via MCP — Claude Code Docs](https://code.claude.com/docs/en/mcp) — Anthropic · accessed 2026-06-28
- [Control MCP server access for your organization — Claude Code Docs](https://code.claude.com/docs/en/managed-mcp) — Anthropic · accessed 2026-06-28
- [Introducing the Model Context Protocol — Anthropic](https://www.anthropic.com/news/model-context-protocol) — 2024-11-25
- [Security Best Practices — Model Context Protocol](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices) — accessed 2026-06-28
- [MCP Security Cheat Sheet — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html) — accessed 2026-06-28
