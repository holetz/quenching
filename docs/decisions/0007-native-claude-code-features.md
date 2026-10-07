---
type: decision
title: Native Claude Code features
description: Adopt, defer or reject verdicts for the Claude Code features the plugin had reinvented or not yet used (spike S26)
resource: plugins/quenching
tags: [decision, platform, hooks, agents, evals]
timestamp: 2026-10-07
audience: both
authority: current
source: mapeamento-critico S26
maintainer: quenching
---

# Native Claude Code features

Spike S26 asked, per native feature, whether the plugin should adopt it. Facts below were read from
the official docs on 2026-10-07: [skills](https://code.claude.com/docs/en/skills),
[plugins-reference](https://code.claude.com/docs/en/plugins-reference),
[plugin-evals](https://code.claude.com/docs/en/plugin-evals),
[sub-agents](https://code.claude.com/docs/en/sub-agents),
[hooks](https://code.claude.com/docs/en/hooks).

| Feature | Verdict |
| --- | --- |
| Skill-scoped `hooks:` for mechanical invariants | Adopt (one warn-level hook now, more by mint) |
| Plugin `agents/` frontmatter | Adopt (already shipped; verified valid, no fix needed) |
| `model:` pins vs `effort:` | Keep the pins; the standard was amended |
| `claude plugin eval` | Defer |
| `${CLAUDE_PLUGIN_DATA}` for caches | Defer; no `--data-dir` |
| `workflows/` plugin component | Defer (needs the owner's explicit request) |
| `/doctor prompt-audit`, `/skill-doctor` | Adopt as manual second opinions, no integration |

## Skill-scoped hooks — adopt

The hooks reference gives the frontmatter form (`hooks:` > event > `matcher` + `hooks:` list with
`type: command`) and states that a skill's hooks stay registered from invocation to session end; the
skills page says the same applies to plugin skills. Hooks are deterministic where the prose
"Invariants to never violate" are not. `${CLAUDE_PLUGIN_ROOT}` is exported to hook processes, so a
bundled script resolves.

Implemented: `/quenching:git:commit` carries a `PreToolUse` `Bash` hook running
`assets/hooks/warn-git-add-all.sh`. It **warns** (`systemMessage` plus `additionalContext`, exit 0)
on `git add -A`, `--all` or `.`, in line with the "warn by default; block by consent" rule of
[hooks.md](../standards/automation/hooks.md). Its handler guards its own absence
(`test -f ... || exit 0`) and has a 5-second timeout. The command's `allowed-tools` never listed
`git add`, so this is a second, deterministic layer and not the only one.

Not done here: the stash and checkout bans for `spec-runner`. Plugin agents do **not** support the
`hooks`, `mcpServers` or `permissionMode` fields (sub-agents page: they "are ignored when loading
agents from a plugin"), so the ban cannot live in `agents/spec-runner.md`. The routes are a hook on
the owning `specs:*` command's frontmatter (those bodies are under edit elsewhere) or a
plugin-level `hooks/hooks.json`, which the plugin discontinued for session-wide cost. A command
frontmatter hook on `specs:execute` is the recommended follow-up, at `ask` or warn level first.

## Plugin `agents/` — adopt, verified

The six files in `plugins/quenching/agents/` use `name`, `description`, `tools`, `model`, `effort`.
The sub-agents page lists `model`, `effort` (low, medium, high, xhigh, max), `tools` and
`disallowedTools` as supported for plugin agents, and none of the six uses `hooks`, `mcpServers` or
`permissionMode`. `orchestrator` restricts spawning with `Agent(quenching:spec-runner, ...)`; the
page documents the `Agent(type)` allowlist and the scoped `plugin:agent` identifier, so the scoped
form is the correct one. No file needed fixing.

## `model:` pins versus `effort:` — keep the pins, amend the standard

`docs/standards/automation/skills.md` already calls a pin "an authored, priced decision", yet read
as a contradiction because five `/quenching:specs:*` commands pin `model:` with no stated buy. The
pins are intended (opus for develop, conclude and triage, which are judgment; sonnet for create and
execute, which are throughput), so the standard now names them and points here. Removing them would
need edits to `specs/*` bodies, which this spike does not touch. The docs confirm `model` and
`effort` both override the session for the turn; `effort:` shares the cache-key concern, so it is
not a cheaper lever for inline commands. Revisit with a measurement (cache-miss tokens per spec run)
before adding `effort:` pins.

## `claude plugin eval` — defer

The native runner (plugin-evals page) needs Claude Code v2.1.269+, runs cases with and without the
plugin, grades by `regex`, `tool_used`, `tool_order`, `file_exists`, `llm` and `baseline`, and bills
the model calls (roughly cases x runs, doubled by the baseline arm). `experimental.evals` marks its
manifest shape as unstable. It overlaps the repo's `/quenching:components:command:eval` and
`assets/evals/components`, which already run in the local gate. Defer until the manifest shape leaves
`experimental` and a cost-capped pilot (`--max-cost-usd`, `--ablation none`) on one command shows it
catches what the in-repo evals miss. Do not replace the in-repo infrastructure on documentation alone.

## `${CLAUDE_PLUGIN_DATA}` — defer, no `--data-dir`

It resolves to `~/.claude/plugins/data/<id>/`, survives updates, and is deleted on last uninstall.
It is substituted in skill, command and agent bodies and exported to hook, MCP stdio and LSP
processes, but is **not** present in the environment of commands run through the Bash tool, so `cq`
cannot read it. A body that wants it must pass it as an argument. `cq` should not gain a `--data-dir`
flag now: no cache currently needs to survive plugin updates, and the `azure.py` temp files go
through a separate fix (write outside the user's checkout) that does not need this directory. Adopt
when a concrete cache (spec-store mirror, per-spec lock) is specified; the flag is then the minimal
bridge.

## `workflows/` — defer

The manifest supports a `workflows` component (`.js` files). Fan-out would gain determinism, but the
Workflow tool is used only on the owner's explicit request, and the batch orchestration is under
active change. Revisit then.

## `/doctor prompt-audit` and `/skill-doctor` — adopt as manual aids

Run them by hand as a second opinion on descriptions and as usage evidence before consolidating
commands. They write nothing in the repo and need no integration.
