---
name: quenching-specs-autopilot
description: "Run improvement rounds (triage, map, epic, orchestrate, review, gate) until a deadline or a dry queue. Use for \"run the autopilot until 7am\". Not for: ONE epic → quenching-specs-orchestrate; owner-decided map → quenching-specs-improve."
---

<!-- GENERATED FROM plugins/quenching/commands/specs/autopilot.md -->


# quenching-specs-autopilot — rounds of improvement until a deadline or a dry queue

**Input**: `$ARGUMENTS` — `--until <date-time with offset>` (e.g. `2026-10-09T07:00-03:00`), or
nothing to run until the queue runs dry; optionally focus areas as in `quenching-specs-improve`.
Typed by the human only: **the invocation is the human's delegation** for the whole run — every
forced execution, push, PR and merge below is authorized by it, and by nothing else.

This session is the **conductor**. It decides as the owner's delegate, keeps only summaries, and
never builds: reading, mapping, decomposing, building and reviewing are agents
(`quenching:scout`, `quenching:spec-architect`, `quenching:orchestrator`, and a read-only opus
reviewer). The orchestrator's protocol (waves, workers, verifier, acceptance) lives in
`../../agents/orchestrator.md`; do not restate it.

**Why `Bash` is unrestricted here.** Step 1 and step 7 run the gate the target's root harness
declares in its operating section (`AGENTS.md` or `AGENTS.md`), whose command no fixed grant can name. No other
non-`cq`, non-`git` command is run.

## Invariants

- **Never forced.** A decision that **widens** a grant or a surface that executes code (hooks,
  scripts, CI, `allowed-tools`, an agent's `tools:`), or that chooses between designs of this
  autonomous protocol itself, is never taken by the conductor. It goes to the run's epic
  "decide with the human" — one per run, created on first need — and the round continues without
  it. **Narrowing** a grant is not widening it.
- **Relevance over activity.** A spec enters the run only with evidence (`path:line`, a command's
  output, a measurement) and a concrete consequence — the bar of `quenching-specs-improve`. "Nothing
  left to polish" is never a reason to invent work.
- **Findings become specs, never hot fixes.** What the correctness review finds is a spec of the
  next round; the conductor never patches `main` itself.
- **Liveness.** A worker with no activity for more than **20 min** (its transcript's mtime) and no
  live child process is stopped with `TaskStop` and relaunched **once**. A second stall goes to the
  final report, never a third launch.
- **Git is read-only for every agent this session briefs, except the orchestrator's workers.**
  Each brief forbids `git stash`, `checkout`, `switch`, `reset`, `restore`, `rebase`, `clean`,
  `commit --amend` and force-push. After every agent returns, audit `git status --short`,
  `git stash list` and `git worktree list`; any change is reported, never silently reverted.
- **Cost.** At most 3 workers at a time; each brief ≤ 1,500 characters, each return ≤ 800 words.
  Wait for completion notifications instead of polling. One correctness review per epic, never per
  spec. The conductor reads summaries, never diffs or file dumps.
- **The deadline binds launches.** With `--until`, no worker starts if it cannot finish before the
  deadline; what is in flight at the deadline is reported `continue` with its state.

## Workflow

### 1. Health
Resolve `cq` per [align/tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool; branch on the exit code. Read the root harness for the gate command and the
ephemeral area. Check, on `main`: the checkout is clean (`git status --short`), `git stash list` is
empty, `git worktree list` holds only this run's worktrees, and the gate is green. Anything red →
this round's first spec is fixing it (`cq specs new`, then steps 4–5 on it alone). Record the round's
start ref: `git rev-parse main`.
**Done when:** `main` is clean and green, or the fix is this round's first spec.

### 2. Queue
List the loose specs — open, in no epic — with `cq specs list --lean --json`, and the store's
errors with `cq specs validate`. Before any of them enters, one `quenching:scout` per batch proves
it is still relevant against the current code:

- the surface it describes has changed → record the evidence in `## Outcome`
  (`cq specs section <id> Outcome --write`) and `cq specs promote <id> --outcome abandoned`;
- it needs the human (the **never forced** list) → `cq specs epic add <human-epic> <id>`;
- otherwise it joins this round's queue.

**Done when:** every loose spec is queued, abandoned with evidence, or in the human epic.

### 3. Map
Only when the queue is short (fewer than three specs): run the mapping of
`quenching-specs-improve` steps 1–3 — read-only `quenching:scout` agents per area, evidence plus
consequence, no duplicate of an open spec, at most 15 candidates, every `high` re-checked — with
this session deciding the owner's questions as the delegated owner, except those on the
**never forced** list, which go to the human epic. Focus areas from `$ARGUMENTS` narrow the areas.
The map is ephemeral, under `<ephemeral area>/autopilot/<date>/`.
**Done when:** the candidates kept are listed with evidence, or the map found none.

### 4. Epic
Hand the queue and the kept candidates to `quenching:spec-architect`: it creates the epic and the
member specs (searching by title first), with waves whose `after:` serializes any two members that
touch the same files. Then write the epic's `## Design` with `cq specs section <epic> Design
--write`, carrying the **autonomy policy**: forced execution, push, PR and merge of every member
after a verifier PASS, authorized by this invocation, with its date. Check the result with
`cq specs status --epic <epic>` and `cq specs validate`.
**Done when:** the epic exists with its waves, its `## Design` carries the dated policy, and
`validate` raises no `sp-epic-*` finding.

### 5. Orchestrate
Start `quenching:orchestrator` on the epic with the word `autonomous`, the base branch and the
deadline (≤ 1,500 characters). Apply **Liveness** to every worker it reports. A spec it returns
`blocked` with a `needs-human:` note moves to the human epic; `failed` or `continue` is carried to
the report with its note, never retried in this round.
**Done when:** the orchestrator returned its fixed report and every non-`done` spec is placed.

### 6. Correctness review
After every epic that changed code, start one read-only opus agent over the epic's merges
(`git log --merges <round start>..main`). It reports only findings it **reproduced** — a command,
its output, the `path:line` — never style. When the epic touched a grant, a hook or anything that
executes, it runs a security review of the same range too. Each finding becomes a loose spec
(`cq specs new`, then its `## Problem` with the reproduction), queued for the next round.
**Done when:** the review returned and each reproduced finding is a spec.

### 7. Gate and audit
On `main`: pull, run the gate, and the audit of step 1. Red → the first spec of the next round.
Then decide whether to stop:

- **deadline** — `--until` is reached, or no worker of a next round could finish before it;
- **dry queue** — a whole round in which the queue (step 2), the map (step 3) and the review
  (step 6) produced **no** spec with evidence and consequence.

Neither → the next round starts at step 1.
**Done when:** the gate and the audit were read, and the run either stops or starts a new round.

### 8. Final report
Print: per epic, the merged specs with their PRs; the human epic and its members; every decision
this session took as the delegated owner; specs in flight at the deadline, as `continue` with their
state; second stalls; and the tokens the run spent.
**Done when:** the report is printed.
