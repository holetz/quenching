---
description: "Run one components flow (command, agent or hook mint, align, status, harness align). Use for \"create a command\", \"align the skills\", \"wire a hook\", \"slim down AGENTS.md\". Not for: knowledge docs → quenching-knowledge-knowledge."
---

<!-- GENERATED FROM plugins/quenching/commands/components/components.md -->

<!-- OPENCODE RUNTIME START -->
## OpenCode runtime

Delegate only through OpenCode's task tool, to the registered subagents named `quenching-<agent>` (protocol copies live under `~/.opencode/quenching/agents/`). Never launch the Claude CLI and never request a Claude model during an OpenCode run. Source model tiers are not pinned here: every command and subagent runs on the model the OpenCode session configures; a declared tier or effort below is a preference to report, not a switch. Token usage comes from host telemetry when it exists, otherwise it is `not measured`; `cq components session cost` reads no OpenCode log and refuses (exit 2, unmeasured), while `cq components session context` and `cache` read the OpenCode database. If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OPENCODE RUNTIME END -->


# quenching-components-components — one entry point for the components flows

**Input**: `$ARGUMENTS` — an optional flow name, then what that flow takes. The remaining words go to the flow untouched.

This command carries no flow of its own. It picks ONE flow, loads that flow's reference and
follows it as if it were this body, so the model's skill list pays for one description and each
flow's text is read only when the flow runs.

**Grant.** The router grants only `cq` and `Read`, enough to load a flow's reference; it widens no flow's tool grant. A tool the chosen flow needs beyond that comes from the conductor agent's own tools, or is asked of the human in a main session; the typed shortcut carries the flow's exact grant.

## Resolving the tool

Resolve `cq` (`cq components read` is the section reader every `§X` citation resolves through)
per [align/tool-resolution.md](~/.opencode/quenching/references/align/tool-resolution.md)
§Resolving the tool; branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

## Workflow

### 1. Pick the flow
The first word of `$ARGUMENTS` naming a flow in the table below picks it, and the rest is the
flow's input. No flow named → the request's own words pick it. An input that fits two flows is asked on a decision sheet, never guessed; a sub-agent
returns `STATE: blocked` with `NOTE: needs-human:` carrying it.

| Flow | Reference | Picked when |
| --- | --- | --- |
| `command-new` | [components-flows/command-new.md](~/.opencode/quenching/references/components-flows/command-new.md) | minting or editing ONE skill or command |
| `agent-new` | [components-flows/agent-new.md](~/.opencode/quenching/references/components-flows/agent-new.md) | minting or editing ONE subagent definition |
| `hook-new` | [components-flows/hook-new.md](~/.opencode/quenching/references/components-flows/hook-new.md) | wiring ONE scoped hook |
| `align` | [components-flows/align.md](~/.opencode/quenching/references/components-flows/align.md) | converging the whole `.agents/skills` surface and its descriptions |
| `status` | [components-flows/status.md](~/.opencode/quenching/references/components-flows/status.md) | a read-only report of the automation surface |
| `harness-align` | [components-flows/harness-align.md](~/.opencode/quenching/references/components-flows/harness-align.md) | refactoring AGENTS.md into pointers over the `/docs/` bundle |

`command:eval`, `command:retro` are typed-only commands and are never routed here.

**Done when:** exactly one flow is chosen, with its input.

### 2. Load the flow and follow it
Run `cq components read` on the chosen flow's reference from the table above, with its
`~/.opencode/quenching/references/components-flows/` path. Read the flow whole, once, and follow it from its own `## Workflow` with the input from step 1:
its steps, `Done when:` lines and invariants bind this run exactly as they bound the standalone
command. A `quenching-components-<flow>` the flow names as the next step is the typed shortcut to
the same reference, and a conductor reaches the same flow by calling this command with the flow name and
the input.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.

## Invariants

- Never run two flows in one invocation; the flow's own next-step block names the following one.
- Never edit what a flow's reference says: a flow's behavior changes in its reference, never here.
- Never route `command:eval`, `command:retro`.
