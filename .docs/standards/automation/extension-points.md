---
type: standard
title: Extension points contract
description: The extension point — an event a command declares for the repository that installed the plugin to attach its own work; the three-part contract (the declaration lives in config the core reads and never interprets; the body announces name, command and prompt and moves on; `condition` is never evaluated by whoever announces); the declared shape; and why the extension lives in config rather than in a command
resource: .claude/quenching.json, plugins/quenching/commands/specs/execute.md, plugins/quenching/assets/bin/quenching/specs/**
tags: [automation, extension, configuration, plugin]
timestamp: 2026-08-10
audience: both
authority: current
source: extensible-surface-and-budget-retirement plan (task 3.1, 2026-08-06)
maintainer: quenching
---

# Extension points contract

An extension point is a place in a command's flow where the repository that installed this plugin
can declare its own work. The declaration lives in configuration, and the body that announces it
stays dumb. Three parts make the contract, and each has one owner: the config holds the
declaration, the owning command's body announces it, and neither interprets it.

## A point of extension is a declared event

A point of extension is an **event** in a command's run — `before_<command>` and `after_<command>`,
named after the command whose flow carries the event. The command that owns the event is the one
that **announces** it; the hooks are what the declaring repository attached to the event.

The one event this plugin ships today is `after_specs_execute_task` on `/specs:execute` — a hook
runs after each task the spec cycle commits. Nothing here is specific to it: the contract is the
same for every event a command declares.

## The declaration lives in config, and the core reads it without interpreting it

The `.claude/quenching.json` of the target repository declares the hooks under the `hooks` key —
[plugin-configuration.md](../workflows/plugin-configuration.md) holds the key's place in the
recognised set. The core (`cq specs`) reads the file whole and validates its **shape**; it never
interprets what a hook **does**. It does not know what the declared command is for, does not run
it, and does not decide when it applies — the config is a declaration, and the reading rules are
the only machinery it gets.

Reading is not interpretation, but it is not nothing either: a hook with `enabled: false` is
**filtered out of the read** — it never reaches whoever announces — and a hook without `enabled`
counts as enabled. That is a filter on the declaration's shape, the same kind of read that yields
the defaults for an absent key; it is not a judgement about whether the hook should run.

## The body announces — name, command and prompt — and moves on

The command that owns the event reads the hooks declared for it (through the config the core
already read) and **announces** them: it prints the event's name, the declared command, and the
prompt whoever executes the hook must follow — then moves on. Announcing is not executing: the
body does not invoke the declared command, does not wait for it, and does not integrate its
result into its own flow. The announcement is the whole obligation of the owning command.

One consequence: a command announces the hooks its config declares, whether or not the hook was
written for this repository. The announcement is what makes a declared hook visible; a hook
nobody announces is a declaration nothing acts on.

## `condition` is never evaluated by whoever announces

A hook may declare a `condition` — the circumstances under which it applies. Whoever announces
never evaluates it. The announcing body does not decide whether the condition holds, does not
filter on it, and does not state its truth; it prints the declared hook and moves on. The filter
that does happen — `enabled: false` — happens in the read, before the announcement, and is the
only one the contract allows there.

## The declared shape

```json
{
  "backend": "github",
  "hooks": {
    "after_specs_execute_task": [
      { "command": "/my:security-review", "optional": true }
    ]
  }
}
```

| Field | Meaning |
| --- | --- |
| the event key | `before_<command>` / `after_<command>` — which command's flow carries the hook |
| `command` | the command whoever executes the hook invokes when it fires |
| `optional` | `true` — the hook's failure does not block the flow that announced it; absent — it does |
| `enabled` | `false` — filtered out of the read, never announced; absent — enabled |
| `condition` | the circumstances under which the hook applies — declared, never evaluated by whoever announces |
| `prompt` | the instruction whoever executes the hook must follow — what the announcement prints alongside the name and the command |

## Why config and not a command

A declared hook costs nothing in always-on context: it is configuration, and configuration is not
a command. A command is an entry point — a file under `commands/` that Claude Code registers and
loads into every session; a hook is a row in a file the core reads on demand. The surface can
grow by configuration — a repository declares a hook, the owning command announces it, nothing
new was minted and nothing new loads. That is the property the spec-kit's
`.specify/extensions.yml` proved, and the reason the extension point exists here.

The other half of the same rule: a hook is **not** a command's back door. It cannot extend a
command that does not announce it — an event nobody owns is a declaration nothing acts on — and
the command that announces it never evaluates it. The extension is exactly as big as the
announcement.
