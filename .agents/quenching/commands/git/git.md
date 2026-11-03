---
description: "Run one git flow (branch, commit, merge, sync, PR create, review, status). Use for \"open a PR\", \"commit this\", \"cut a worktree\", \"sync with main\". Not for: specs → /quenching-specs-specs."
argument-hint: "[branch|commit|merge|sync|pr-create|pr-review|pr-status] [input]"
allowed-tools: Bash(.agents/quenching/bin/cq components read:*), Bash(.agents/quenching/bin/cq.cmd components read:*), Bash(.agents/quenching/bin/cq specs status:*), Read
---

# /quenching-git-git — one entry point for the git flows

**Input**: `$ARGUMENTS` — an optional flow name, then what that flow takes. The remaining words go to the flow untouched.

This command carries no flow of its own. It picks ONE flow, loads that flow's reference and
follows it as if it were this body, so the model's skill list pays for one description and each
flow's text is read only when the flow runs.

**Grant.** The router grants only `.agents/quenching/bin/cq components read`, `.agents/quenching/bin/cq specs status` and `Read`, enough to load a flow's reference and read a spec; it widens no flow's tool grant. A tool the chosen flow needs beyond that comes from the conductor agent's own tools, or is asked of the human in a main session; the typed shortcut carries the flow's exact grant.

## Resolving the tool

Resolve `cq` (`.agents/quenching/bin/cq components read` is the section reader every `§X` citation resolves through)
per [align/tool-resolution.md](.agents/quenching/assets/references/align/tool-resolution.md)
§Resolving the tool; branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

## Workflow

### 1. Pick the flow
The first word of `$ARGUMENTS` naming a flow in the table below picks it, and the rest is the
flow's input. No flow named → the request's own words pick it. An input that fits two flows is asked on a decision sheet, never guessed; a sub-agent
returns `STATE: blocked` with `NOTE: needs-human:` carrying it.

| Flow | Reference | Picked when |
| --- | --- | --- |
| `branch` | [git-flows/branch.md](.agents/quenching/assets/references/git-flows/branch.md) | isolation for a piece of work: a worktree or branch |
| `commit` | [git-flows/commit.md](.agents/quenching/assets/references/git-flows/commit.md) | committing what is already staged |
| `merge` | [git-flows/merge.md](.agents/quenching/assets/references/git-flows/merge.md) | merging a branch into its base |
| `sync` | [git-flows/sync.md](.agents/quenching/assets/references/git-flows/sync.md) | rebasing the work branch onto the latest base |
| `pr-create` | [git-flows/pr-create.md](.agents/quenching/assets/references/git-flows/pr-create.md) | pushing the branch and opening a PR |
| `pr-review` | [git-flows/pr-review.md](.agents/quenching/assets/references/git-flows/pr-review.md) | addressing a PR's unresolved review threads |
| `pr-status` | [git-flows/pr-status.md](.agents/quenching/assets/references/git-flows/pr-status.md) | a read-only read of a PR's checks, reviews and mergeability |

`cleanup`, `commit-incremental`, `push`, `revert` are typed-only commands and are never routed here.

**Done when:** exactly one flow is chosen, with its input.

### 2. Load the flow and follow it
Run `.agents/quenching/bin/cq components read` on the chosen flow's reference from the table above, with its
`.agents/quenching/assets/references/git-flows/` path. Read the flow whole, once, and follow it from its own `## Workflow` with the input from step 1:
its steps, `Done when:` lines and invariants bind this run exactly as they bound the standalone
command. A `/quenching-git-<flow>` the flow names as the next step is the typed shortcut to
the same reference, and a conductor reaches the same flow by calling this command with the flow name and
the input.
**Done when:** the flow ran to its own `Done when:`, or stopped on its own stop condition.

## Invariants

- Never run two flows in one invocation; the flow's own next-step block names the following one.
- Never edit what a flow's reference says: a flow's behavior changes in its reference, never here.
- Never route `cleanup`, `commit-incremental`, `push`, `revert`.
