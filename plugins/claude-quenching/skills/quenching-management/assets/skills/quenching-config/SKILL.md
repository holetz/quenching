---
name: quenching-config
description: >-
  Configures a Claude Code repo session via settings.json, hooks, and .mcp.json —
  registers/fixes hooks (PostToolUse/InstructionsLoaded/Stop), manages permissions
  and env vars, and declares MCP servers in project scope with secrets via ${VAR}.
  Use when the user asks to "add/register a hook", "configure settings.json",
  "allow a command", "set an env var", "declare an MCP server", "remove the
  hardcoded secret from .mcp.json", "automate a validation in the session cycle",
  or when a hook points to a missing script / an active MCP server is not versioned.
when_to_use: >-
  configuration of settings.json/hooks/permissions/env and MCP servers
  (.mcp.json/managed-mcp.json) — deterministic enforcement and external integration.
allowed-tools: Read, Grep, Glob, Edit, Write
---

# Session configuration — hooks, settings, and MCP

> Skill-template of the `quenching-management` method. Generic and portable:
> merge into the repo's existing blocks, never overwrite the entire `settings.json`.

## Hooks — deterministic automation

A hook is **enforcement**, not judgment (guidance ≠ imposition). Use when the
action must be **guaranteed** in the session lifecycle.

- Declare in `settings.json` (events `PostToolUse`/`InstructionsLoaded`/`Stop`);
  scripts in `.claude/hooks/`.
- Each `command` points to an **existing** script; sensible `timeout`.
- Idempotent; explicit criterion/ceiling; never edit a generated artifact.
- Shared config committed (`hooks-config.json`); per-dev override in
  `*.local.json` (gitignored).
- Exit contract: `0` passes; `2` shows stderr to Claude as feedback.

The method package ships ready-made CLAUDE.md validation/audit hooks
(`assets/hooks/`) with the `settings.snippet.json` wiring.

## Permissions and env

- `permissions.allow`/`deny` per tool/command; minimum necessary.
- Project env vars in `settings.json`; secrets **never** in plaintext.

## MCP servers — external integration

- Servers the team must have go in **`project` scope** (`.mcp.json` in the root,
  versioned and reviewed as infrastructure code).
- **Secrets via `${VAR}`-expansion**, never literals in `env`/`headers`.
- Minimum OAuth scope per server; the root CLAUDE.md declares which servers are
  expected and in which scope.
- A server consuming external content (issues, web, messages) = **prompt-injection
  vector**: flag it in CLAUDE.md.
- Corporate: `managed-mcp.json` with allowlist by `serverUrl`/`serverCommand`
  (not by `serverName`, which the user chooses).
- Active server without a `project` entry = **phantom dependency** (local/user
  scope, invisible to the repo) ⇒ promote to `project`.
