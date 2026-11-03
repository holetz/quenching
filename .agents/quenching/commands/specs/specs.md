---
description: "Run one specs flow (create, develop, execute, conclude, triage, status, orchestrate), picked by name or stage. Use for \"build it\", \"rank the backlog\". Not for: git → /quenching-git-branch; rounds → /quenching-specs-autopilot."
argument-hint: "[create|develop|execute|conclude|triage|status|orchestrate] [id or description] [flags]"
allowed-tools: Bash(.agents/quenching/bin/cq:*), Bash(.agents/quenching/bin/cq.cmd:*), Read
---

# /quenching-specs-specs — one entry point for the specs flows

**Input**: `$ARGUMENTS` — an optional flow name, then what that flow takes (a spec id, a
description, a plan path, flags). The remaining words go to the flow untouched.

This command carries no flow of its own. It picks ONE flow, loads that flow's reference and
follows it as if it were this body, so the model's skill list pays for one description and each
flow's text is read only when the flow runs.

**Grant.** The router grants only `cq` and `Read`, enough to load a flow's reference; it widens no flow's tool grant. A tool the chosen flow needs beyond that comes from the conductor agent's own tools, or is asked of the human in a main session; the typed shortcut carries the flow's exact grant.

## Resolving the tool

Resolve `cq` (`.agents/quenching/bin/cq components read` is the section reader every `§X` citation resolves through)
per [align/tool-resolution.md](.agents/quenching/assets/references/align/tool-resolution.md)
§Resolving the tool; branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

## Workflow

### 1. Pick the flow
The first word of `$ARGUMENTS` naming a flow in the table below picks it, and the rest is the
flow's input. No flow named → with an id, `.agents/quenching/bin/cq specs status --spec <id> --json` and the derived
stage pick it; with no id, the request's own words do (a problem to capture, a ranking, a status
question). An input that fits two flows is asked on a decision sheet, never guessed; a sub-agent
returns `STATE: blocked` with `NOTE: needs-human:` carrying it.

| Flow | Reference | Picked when |
| --- | --- | --- |
| `create` | [specs-flows/create.md](.agents/quenching/assets/references/specs-flows/create.md) | a problem, plan or idea to capture; no spec id |
| `develop` | [specs-flows/develop.md](.agents/quenching/assets/references/specs-flows/develop.md) | stage `captured`, `proposed` or `designed`, or a refine request |
| `execute` | [specs-flows/execute.md](.agents/quenching/assets/references/specs-flows/execute.md) | stage `ready` or `approved`, or a build with tasks still open |
| `conclude` | [specs-flows/conclude.md](.agents/quenching/assets/references/specs-flows/conclude.md) | every task checked, or an explicit close or abandon |
| `triage` | [specs-flows/triage.md](.agents/quenching/assets/references/specs-flows/triage.md) | a ranking of the open front |
| `status` | [specs-flows/status.md](.agents/quenching/assets/references/specs-flows/status.md) | a read of the front or of one spec's state |
| `orchestrate` | [specs-flows/orchestrate.md](.agents/quenching/assets/references/specs-flows/orchestrate.md) | an epic or a list of specs to run through the orchestrator |

`autopilot`, `improve` and `board` are typed-only commands and are never routed here.
**Done when:** exactly one flow is chosen, with its input.

### 2. Load the flow and follow it
Run `.agents/quenching/bin/cq components read` on the chosen flow's reference from the table above, with its
`.agents/quenching/assets/references/specs-flows/` path. Read the flow whole, once, and follow it from its own `## Workflow` with the input from step 1:
its steps, `Done when:` lines and invariants bind this run exactly as they bound the standalone
command. A `/quenching-specs-<flow>` the flow names as the next step is the typed shortcut to
the same reference, and a conductor reaches the same flow by calling this command with `flow` and
the id.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.

## Declared autonomy

Autonomy is **recognised, never inferred**. It is declared by the literal `autonomous` in the input, or by
the human's own words asking to run to the end without asking: "autônomo", "sem parar", "até o PR". "Execute
isto" is not a declaration. An ambiguous input is asked of the human on a decision sheet; a sub-agent
returns `needs-human:`. The reach is what the declaration names: "até o PR" never authorises a merge, and
merge and deploy keep requiring their own declaration.

Declared, this entry chains the flows in order, reading each reference in its turn: `develop` (stamping
`approved` as `orchestrator-forced`), `execute`, then `conclude` (`--outcome done` only with every task checked). Each flow
keeps its own `Done when:`. It stops only on a real block
(`/docs/standards/workflows/task-execution.md` §After approval, the executor decides, records and stops only on a real block),
and ends with **one report**: the final stage and every `decision:` line of `## Discoveries`. A budget stop
(`continue`) stands as always.

## Invariants

- Never run two flows in one invocation, except under §Declared autonomy; otherwise the flow's own next-step block names the following one.
- Never edit what a flow's reference says: a flow's behavior changes in its reference, never here.
- Never route `autopilot`, `improve` or `board`.
