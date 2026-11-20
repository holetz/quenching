# quenching-vitrine

A Claude Code mod that opens a pane beside the session with the quenching specs the session touched.
It is the Claude counterpart of the OpenCode vitrine (`integrations/opencode-vitrine`) and keeps its own
code: a mod loads only files inside its own folder.

## What it shows

`/quenching-vitrine` opens the pane. Nothing opens it by itself.

- **Specs the session touched**: cited in the conversation, named by a `cq specs ...` Bash call or a
  `mcp__quenching__specs_*` tool call, or the spec of the branch or commit the session is on. The list is rebuilt
  from the conversation each time the pane opens, so a reloaded mod keeps it.
- **A spec's document in tabs**, with stage, priority, complexity, age, task progress, runner state, block reason
  and assignee in the header. A task, or the whole spec, goes to the composer.
- **Dependencies**: who the spec waits for, who waits for it, the epic's members and the member's "Part of" block.
- **Configuration**: every key of `cq config schema --values --json`, grouped by category, with the layer that
  gave the value. It writes only through `cq config set|unset --layer project|local`.

## What it runs

Argv only, no shell, from the session's working directory:

- `cq specs list|status|show|schedule|find ...` (reads)
- `cq config schema --values --json` (read) and `cq config set|unset <key> ... --layer project|local` (the one write)
- `git branch --show-current` and `git rev-parse HEAD` (the session's own branch and commit)

It never installs quenching into a project: skills keep arriving by `cq deploy`, and this mod is never part of it.

## Requirements

`cq` on `PATH` (the target's own `.agents/quenching/bin/cq` or a global one). Without it the pane says so and
shows nothing else.

## Install

The mod installs separately from the skills, through the marketplace this repository publishes:

```
/plugin marketplace add holetz/quenching
/plugin install quenching-vitrine@quenching
```

## Verify

```bash
claude plugin validate integrations/claude-vitrine
claude plugin test integrations/claude-vitrine
```

Tested on Claude Code 2.1.328 (mod API of build 2.1.325). The mod API is young: a Claude release can change it.
