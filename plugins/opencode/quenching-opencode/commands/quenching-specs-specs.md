---
description: "Run one specs flow (create, develop, execute, conclude, triage, status, orchestrate), picked by name or stage. Use for \"build it\", \"rank the backlog\". Not for: git → quenching-git-branch; rounds → quenching-specs-autopilot."
---

<!-- GENERATED FROM plugins/quenching/commands/specs/specs.md -->

<!-- OPENCODE RUNTIME START -->
## OpenCode runtime

Delegate only through OpenCode's task tool, to the registered subagents named `quenching-<agent>` (protocol copies live under `~/.opencode/quenching/agents/`). Never launch the Claude CLI and never request a Claude model during an OpenCode run. Source model tiers are not pinned here: every command and subagent runs on the model the OpenCode session configures; a declared tier or effort below is a preference to report, not a switch. Token usage comes from host telemetry when it exists, otherwise it is `not measured`; `cq components session cost` reads no OpenCode log and refuses (exit 2, unmeasured), while `cq components session context` and `cache` read the OpenCode database. If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OPENCODE RUNTIME END -->


# quenching-specs-specs — one entry point for the specs flows

**Input**: `$ARGUMENTS` — an optional flow name, then what that flow takes (a spec id, a
description, a plan path, flags). The remaining words go to the flow untouched.

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
flow's input. No flow named → with an id, `cq specs status --spec <id> --json` and the derived
stage pick it; with no id, the request's own words do (a problem to capture, a ranking, a status
question). An input that fits two flows is asked on a decision sheet, never guessed; a sub-agent
returns `STATE: blocked` with `NOTE: needs-human:` carrying it.

| Flow | Reference | Picked when |
| --- | --- | --- |
| `create` | [specs-flows/create.md](~/.opencode/quenching/references/specs-flows/create.md) | a problem, plan or idea to capture; no spec id |
| `develop` | [specs-flows/develop.md](~/.opencode/quenching/references/specs-flows/develop.md) | stage `captured`, `proposed` or `designed`, or a refine request |
| `execute` | [specs-flows/execute.md](~/.opencode/quenching/references/specs-flows/execute.md) | stage `ready` or `approved`, or a build with tasks still open |
| `conclude` | [specs-flows/conclude.md](~/.opencode/quenching/references/specs-flows/conclude.md) | every task checked, or an explicit close or abandon |
| `triage` | [specs-flows/triage.md](~/.opencode/quenching/references/specs-flows/triage.md) | a ranking of the open front |
| `status` | [specs-flows/status.md](~/.opencode/quenching/references/specs-flows/status.md) | a read of the front or of one spec's state |
| `orchestrate` | [specs-flows/orchestrate.md](~/.opencode/quenching/references/specs-flows/orchestrate.md) | an epic or a list of specs to run through the orchestrator |

`autopilot`, `improve` and `board` are typed-only commands and are never routed here.
**Done when:** exactly one flow is chosen, with its input.

### 2. Load the flow and follow it
Run `cq components read` on the chosen flow's reference from the table above, with its
`~/.opencode/quenching/references/specs-flows/` path. Read the flow whole, once, and follow it from its own `## Workflow` with the input from step 1:
its steps, `Done when:` lines and invariants bind this run exactly as they bound the standalone
command. A `quenching-specs-<flow>` the flow names as the next step is the typed shortcut to
the same reference, and a conductor reaches the same flow by calling this command with `flow` and
the id.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.

## Invariants

- Never run two flows in one invocation; the flow's own next-step block names the following one.
- Never edit what a flow's reference says: a flow's behavior changes in its reference, never here.
- Never route `autopilot`, `improve` or `board`.
