---
description: >-
  Run one step of the specs flow: capture, develop, execute, conclude, triage, status or orchestrate, picked by the flow you name or by the spec's real stage. Use for "create a spec", "develop this spec", "build it", "conclude it", "rank the backlog", "specs status", "orchestrate this epic". Not for: committing, branching or merging → /quenching-specs:git:branch; improvement rounds → /quenching-specs:specs:autopilot.
argument-hint: "[create|develop|execute|conclude|triage|status|orchestrate] [id or description] [flags]"
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Bash, Read, Glob, Grep, Write, Edit, Bash(python3:*), Bash(py:*), AskUserQuestion, Skill, Task, Agent
---

# /quenching-specs:specs:specs — one entry point for the specs flows

**Input**: `$ARGUMENTS` — an optional flow name, then what that flow takes (a spec id, a
description, a plan path, flags). The remaining words go to the flow untouched.

This command carries no flow of its own. It picks ONE flow, loads that flow's reference and
follows it as if it were this body, so the model's skill list pays for one description and each
flow's text is read only when the flow runs.

**Why `Bash` is unrestricted here.** The routed flows run the verification, `cq specs` and Git commands resolved from the live spec; the router grants the union of what its flows were granted, no more.

## Resolving the tool

Resolve `cq` (`cq components read` is the section reader every `§X` citation resolves through)
per [align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool; branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

## Workflow

### 1. Pick the flow
The first word of `$ARGUMENTS` naming a flow in the table below picks it, and the rest is the
flow's input. No flow named → with an id, `cq specs status --spec <id> --json` and the derived
stage pick it; with no id, the request's own words do (a problem to capture, a ranking, a status
question). An input that fits two flows is asked on a decision sheet, never guessed; a sub-agent
returns `STATE: blocked` with `NOTE: needs-human:` carrying it.

| Flow | Reference | Picked when |
| --- | --- | --- |
| `create` | [specs-flows/create.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-flows/create.md) | a problem, plan or idea to capture; no spec id |
| `develop` | [specs-flows/develop.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-flows/develop.md) | stage `captured`, `proposed` or `designed`, or a refine request |
| `execute` | [specs-flows/execute.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-flows/execute.md) | stage `ready` or `approved`, or a build with tasks still open |
| `conclude` | [specs-flows/conclude.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-flows/conclude.md) | every task checked, or an explicit close or abandon |
| `triage` | [specs-flows/triage.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-flows/triage.md) | a ranking of the open front |
| `status` | [specs-flows/status.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-flows/status.md) | a read of the front or of one spec's state |
| `orchestrate` | [specs-flows/orchestrate.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-flows/orchestrate.md) | an epic or a list of specs to run through the orchestrator |

`autopilot`, `improve` and `board` are typed-only commands and are never routed here.
**Done when:** exactly one flow is chosen, with its input.

### 2. Load the flow and follow it
```bash
.agents/quenching/bin/cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-flows/<flow>.md
```
Read the flow whole, once, and follow it from its own `## Workflow` with the input from step 1:
its steps, `Done when:` lines and invariants bind this run exactly as they bound the standalone
command. A `/quenching-specs:specs:<flow>` the flow names as the next step is the typed shortcut to
the same reference, and a conductor reaches the same flow by calling this command with `flow` and
the id.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.

## Invariants

- Never run two flows in one invocation; the flow's own next-step block names the following one.
- Never edit what a flow's reference says: a flow's behavior changes in its reference, never here.
- Never route `autopilot`, `improve` or `board`.
