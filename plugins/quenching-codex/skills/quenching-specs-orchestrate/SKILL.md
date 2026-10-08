---
name: quenching-specs-orchestrate
description: "Run an epic or a list of specs through the orchestrator agent. Use for \"orchestrate this epic\", \"run these specs in waves\". Not for: ONE spec → quenching-specs-execute; ranking → quenching-specs-triage."
---

<!-- GENERATED FROM plugins/quenching/commands/specs/orchestrate.md -->


# quenching-specs-orchestrate — conduct an epic or a queue

**Input**: `$ARGUMENTS` — an epic id or a list of spec ids, and optionally `--autonomous`. Empty or ambiguous → run
`cq specs list --json` and ask which with **AskUserQuestion**.

This command is a launcher. The protocol (waves, routing, budgets, acceptance, audit) lives in the
`orchestrator` agent definition, `../../agents/orchestrator.md`; do not restate it.

## Workflow

### 1. Resolve the set
Resolve `cq` per [align/tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool; branch on the exit code. Confirm each id exists with `cq specs show --spec <id> --json`.
**Done when:** the epic id or the list of spec ids is verified to exist.

### 2. Check who can run alone
Split the set from the `show` payloads: **runs alone** is a spec with `approved` recorded or
`complexity: low`; **needs a human** is `medium` or above with no `approved`. Nothing needs a
human → go to step 3. Otherwise ask once with **AskUserQuestion**, naming the specs on each side:

- **Develop now** — run `quenching-specs-develop <id>` in this session, one spec after another,
  for the specs that need a human, then launch everything. A develop of a `medium` spec costs about
  40k tokens of this session (its body and references alone are about 17k), so this is offered
  only for **two specs or fewer**; for more, end the run by listing one
  `quenching-specs-develop <id>` line per spec and `quenching-specs-orchestrate` again after.
- **Launch the independent subset** — only the specs that run alone and depend on none of the
  ones that need a human.
- **Force it** — `--autonomous`: every spec runs, and the approval is stamped
  `by=orchestrator-forced`, never `by=human`.

`--autonomous` already given → skip the question. **Done when:** the set to launch is fixed.

### 3. Launch the orchestrator
Codex ships no plugin sub-agents, so follow `../../agents/orchestrator.md` in this session instead: ignore its `tools:` allow-list, keep its prohibitions (no git stash, checkout, reset, rebase or commit amend; edit no file yourself), and take as its input, in at most 1,500 characters: the epic id or
the spec ids, the base branch, and the word `autonomous` when it was forced. Pass nothing else; it
carries its own protocol, and without `autonomous` it blocks a spec that still needs approval.
**Done when:** the orchestrator has returned its fixed report.

### 4. Relay
Show its per-spec blocks and totals line unchanged. A spec in state `blocked`, `failed` or
`continue` is named with its note and left for the human; never retry it here.
**Done when:** the report is shown and every non-`done` spec is named.
