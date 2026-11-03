---
name: quenching-knowledge-knowledge
description: "Run one knowledge flow on the OKF bundle (add, learn, define, import, align, status, documentation). Use for \"add a standard\", \"define this term\", \"align the docs\". Not for: specs → quenching-specs-specs."
allowed-tools: "Bash(cq:*), Bash(cq.cmd:*), Read"
---

<!-- GENERATED FROM plugins/quenching/commands/knowledge/knowledge.md -->

<!-- OMNIGENT RUNTIME START -->
## Omnigent runtime

This runs inside the `quenching` operator agent on whatever model the server's policy selects; it pins none and names no vendor CLI. The bundle carries no payload: read a reference through the `quenching` MCP server's resources (`quenching://references/<path>`), and prefer its tools (`<pillar>_<verb>`) to a shell `cq`, which resolves only where a local install sits under `$QUENCHING_OMNIGENT_ROOT`. Delegate only to the operator's declared sub-agents. Source model tiers and effort are not switches: a declared tier or effort below is a preference to report. Token usage comes from host telemetry when it exists, otherwise it is `not measured`. A tool the permission policy denies stays denied: report it, never route around it. If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OMNIGENT RUNTIME END -->


# quenching-knowledge-knowledge — one entry point for the knowledge flows

**Input**: `$ARGUMENTS` — an optional flow name, then what that flow takes. The remaining words go to the flow untouched.

This command carries no flow of its own. It picks ONE flow, loads that flow's reference and
follows it as if it were this body, so the model's skill list pays for one description and each
flow's text is read only when the flow runs.

**Grant.** The router grants only `cq` and `Read`, enough to load a flow's reference; it widens no flow's tool grant. A tool the chosen flow needs beyond that comes from the conductor agent's own tools, or is asked of the human in a main session; the typed shortcut carries the flow's exact grant.

## Resolving the tool

Resolve `cq` (`cq components read` is the section reader every `§X` citation resolves through)
per [align/tool-resolution.md](quenching://references/align/tool-resolution.md)
§Resolving the tool; branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

## Workflow

### 1. Pick the flow
The first word of `$ARGUMENTS` naming a flow in the table below picks it, and the rest is the
flow's input. No flow named → the request's own words pick it. An input that fits two flows is asked on a decision sheet, never guessed; a sub-agent
returns `STATE: blocked` with `NOTE: needs-human:` carrying it.

| Flow | Reference | Picked when |
| --- | --- | --- |
| `add` | [knowledge-flows/add.md](quenching://references/knowledge-flows/add.md) | a new concept doc (standard, table, announcement) for the bundle |
| `learn` | [knowledge-flows/learn.md](quenching://references/knowledge-flows/learn.md) | one piece of generic knowledge to record in `concepts/` |
| `define` | [knowledge-flows/define.md](quenching://references/knowledge-flows/define.md) | one glossary term to add or refine |
| `glossary-backfill` | [knowledge-flows/glossary-backfill.md](quenching://references/knowledge-flows/glossary-backfill.md) | a sweep of the whole bundle for missing glossary terms |
| `import` | [knowledge-flows/import.md](quenching://references/knowledge-flows/import.md) | an external source (files, folders, URLs) to ingest as many docs |
| `import-memory` | [knowledge-flows/import-memory.md](quenching://references/knowledge-flows/import-memory.md) | the host memory to drain into the bundle and clear |
| `align` | [knowledge-flows/align.md](quenching://references/knowledge-flows/align.md) | forcing `/docs/` into the canonical bundle |
| `status` | [knowledge-flows/status.md](quenching://references/knowledge-flows/status.md) | a read-only report of where the bundle stands |
| `documentation-plan` | [knowledge-flows/documentation-plan.md](quenching://references/knowledge-flows/documentation-plan.md) | a sourced documentation plan with reader journeys |
| `documentation-write` | [knowledge-flows/documentation-write.md](quenching://references/knowledge-flows/documentation-write.md) | pages to write from a documentation plan |
| `documentation-review` | [knowledge-flows/documentation-review.md](quenching://references/knowledge-flows/documentation-review.md) | a score of documentation pages against the quality gate |
| `documentation-build` | [knowledge-flows/documentation-build.md](quenching://references/knowledge-flows/documentation-build.md) | the Zensical site layer, navigation or strict build |
| `documentation-produce` | [knowledge-flows/documentation-produce.md](quenching://references/knowledge-flows/documentation-produce.md) | the whole documentation pipeline in one run |


**Done when:** exactly one flow is chosen, with its input.

### 2. Load the flow and follow it
Run `cq components read` on the chosen flow's reference from the table above, with its
`quenching://references/knowledge-flows/` path. Read the flow whole, once, and follow it from its own `## Workflow` with the input from step 1:
its steps, `Done when:` lines and invariants bind this run exactly as they bound the standalone
command. A `quenching-knowledge-<flow>` the flow names as the next step is the typed shortcut to
the same reference, and a conductor reaches the same flow by calling this command with the flow name and
the input.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.

## Invariants

- Never run two flows in one invocation; the flow's own next-step block names the following one.
- Never edit what a flow's reference says: a flow's behavior changes in its reference, never here.
