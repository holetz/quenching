---
type: reference
title: Claude Code skill and command loading mechanics
description: Measured facts about how Claude Code loads plugin commands vs skills — placeholder substitution, the Skill-tool registry, startup-time discovery, and the unified frontmatter schema
resource: plugins/claude-quenching/commands/**, plugins/claude-quenching/skills/*/SKILL.md
tags: [claude-code, plugins, skills, commands, frontmatter, tooling]
timestamp: 2026-07-26
audience: both
authority: background
source: skill-description-tiering spec, task 0.2 gate spike — measured on Claude Code 2.1.215
maintainer: claude-quenching
---

# Claude Code skill and command loading mechanics

Facts about **how Claude Code itself loads a plugin's commands and skills**. External tool
behavior, not our contract — how we choose to *use* it belongs in
[standards/automation/](/docs/standards/automation/index.md).

Everything below was measured against **Claude Code 2.1.215** on Linux, by probing throwaway
command and skill files in fresh `claude -p` processes. Where a claim is inference rather than
observation, it says so.

## The findings

| # | Behavior | Status |
| --- | --- | --- |
| 1 | `${CLAUDE_PLUGIN_ROOT}` **substitutes inside a `commands/*.md` body**, exactly as it does in `SKILL.md` | Observed |
| 2 | A **command is invocable by name through the Skill tool**, and its body expands with substitution intact | Observed |
| 3 | A command is registered in the Skill-tool listing under its **command path** (`plugin:docs:add`), carrying its own frontmatter `description` | Observed |
| 4 | The command/skill registry is built **at session start** — a file created mid-session is not discoverable until a new process | Observed |
| 5 | Commands and skills share **one frontmatter schema** | Inferred from the binary |
| 6 | `allowed-tools` did **not** restrict tool access | Observed, narrow — see the caveat |

### 1–2. Placeholder substitution reaches command bodies

The documented substitution table grants `${CLAUDE_PLUGIN_ROOT}` to *"Skill and agent content"*
and does not name `commands/**`. It nonetheless resolves there: a command body containing the
placeholder expanded to the absolute plugin root, on **both** invocation paths — typed as a slash
command, and invoked by name through the Skill tool.

This is what makes a command file able to cite a bundled `references/*.md` the way a skill does.

Corroborated by precedent: Anthropic ships four `commands/**` files using the placeholder, one of
them (`ralph-wiggum/commands/ralph-loop.md`) load-bearingly **inside `allowed-tools` itself** and
again in an executing `!` block.

### 3. Commands appear in the Skill-tool registry

A command is listed alongside skills and can be invoked by name — the same path a conductor uses
to invoke a stage. The listed description is the command file's own frontmatter `description`,
byte-for-byte.

Consequence worth noting: a plugin shipping both a skill and a wrapper command for it puts **two**
descriptions in the always-on listing, not one.

### 4. Discovery happens at startup

Creating a command or skill file does not make it invocable in the running session; the attempt
fails as an unknown skill. Any spike that adds a surface file must run in a **new process**.

### 5. One frontmatter schema

The 2.1.215 binary carries `user-invocable`, `allowed-tools`, `disallowed-tools`, `argument-hint`,
and `disable-model-invocation` in a single key list — a unified parser rather than two, consistent
with commands and skills having converged. Also present: **`hide-from-slash-command-tool`**,
observed in a shipped Anthropic command, which controls whether an entry surfaces in the slash
menu.

This last key matters to anyone weighing `disable-model-invocation: true`: the usual objection —
that dropping `user-invocable: false` floods the `/` menu with duplicates — appears to have a
frontmatter answer.

### 6. `allowed-tools` was not observed to restrict tools

A probe declaring `allowed-tools: ["Bash(echo:*)"]` still completed a `Write`, verified on the
filesystem rather than by self-report, in **all four** cells of command × skill by slash-invocation
× Skill-tool-invocation.

**Read this narrowly.** It establishes *parity* between commands and skills, which is what it was
run to determine. It does **not** establish that `allowed-tools` never restricts anything: the
runs used `claude -p` on one machine under that machine's permission settings, and no interactive
session was tested. Treat it as a lead.

The open question it raises — whether a skill's read-only guarantee is enforced or merely
declared — is tracked as its own spec rather than asserted here.

## Provenance

Measured during the task 0.2 gate spike of the `skill-description-tiering` spec, which was
[abandoned](/specs/archive/2026-07-26-skill-description-tiering.md) on the result. All probe files
were reverted. Re-measure before relying on any row: these are one version's observed behavior,
not a published contract.
