---
name: quenching-specs-execute-queue
description: "Build N specs in one run — one isolation, one branch, one pull request, serial by construction. Triggers on \"execute these specs\", \"build the queue\", \"run these three specs in one go\", \"take the next N specs to a PR\", \"queue the front\", \"build everything that is ready\". Candidates come from the ranked front filtered by the fan-out entry contract; the authorization plan carries the whole list, the N, the recursion form and the human's stopping criterion before any isolation, and its OK authorizes the run. Each spec runs in a sub-agent of its own context via quenching-specs-execute; one quenching-specs-conclude with no --spec closes it. A local block marks [!] and the queue moves on; a contaminating one stops and asks. Not for: building ONE spec → quenching-specs-execute; taking N specs to ready in parallel → quenching-specs-develop-batch; ONE spec's whole lifecycle → quenching-specs-cycle; reviewing and merging a branch → quenching-specs-conclude; ranking the front → quenching-specs-triage."
---

<!-- GENERATED FROM plugins/quenching/commands/specs/execute-queue.md -->


# quenching-specs-execute-queue — N specs, one isolation, one pull request

**Input**: `$ARGUMENTS` — a list of spec slugs, or nothing. Omitted → propose the queue from the
ranked front, top-down.

Builds N specs as a **serial queue over a single isolation**: isolate once, run
`quenching-specs-execute` N times on that same branch, close with one
`quenching-specs-conclude`. Serialization is the feature — it removes the collision by
construction and makes spec N's gate run over the result of 1..N−1.

**This command invokes and never reimplements.** Every write belongs to the stage that makes it,
under that stage's own doctrine.

**Why `Bash` is unrestricted, and why it is the only file-touching tool granted.** Like
`quenching-specs-execute`, the queue drives the target repo's `git` and re-runs the repo's own
declared gate after each spec — commands that are the repo's, not the plugin's, and cannot be
enumerated in advance. Every read the conductor makes goes through `cq`, so no `Read`/`Glob`/`Grep`
is granted — the repo's own files are read inside the executor sub-agents, never here.

**Every `§X` in this body is an address, and it is loaded as one — never by opening the file:**

```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" components read <the cited file> --sections "§A" --sections "§B"
```

One call, N sections, no frontmatter; a unique prefix resolves, and `--rules-only` narrows to the
`<!-- rules -->` half. A conductor's preamble is re-sent every turn of a run that may hold N specs,
so what is loaded at turn one is paid for the length of the whole queue.

**The contract, owned once** —
[fanout.md](../../references/specs-fanout/fanout.md) §The two regimes
§The queue's shape §The branch carries the slugs §The entry contract §Classifying a block
§The recursive return. Every rule this queue runs on lives there, and is cited, never restated.

## Resolving the tool

Resolve `cq` (`cq components read` is the section reader every `§X` citation in this body resolves
through) per
[align/tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool; branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

## Workflow

### 1. Assemble the candidates
Read the front and the workspace in one call:

```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs next --front --json    # the ranked candidates, each with stage, priority, branch liveness
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs config --json          # backend, worktreeSetup, fanoutMinComplexity
```

Slugs given → resolve each against that payload, in the order the human typed them; one that does
not resolve is named and dropped, never guessed at. Nothing given → propose from the ranking,
top-down.

Then filter every candidate through the entry contract:

```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" components read ../../references/specs-fanout/fanout.md \
  --sections "§The entry contract" --rules-only
```

`priority.complexity` decides where a spec joins and nothing else does. A candidate the contract
sends to the defining regime is listed as **excluded**, with `quenching-specs-develop-batch
<slug>` beside it; one whose `priority` record carries no `complexity` has nothing for the
contract to read, so it is named and routed to `quenching-specs-triage`. A candidate whose work
branch is alive and held elsewhere
(`branch.live` with `branch.current` false) is excluded too, naming where — queueing it would fork
the work.
**Done when:** every candidate carries its derived stage, its `complexity`, and a verdict — queued,
or excluded with the command that closes it.

### 2. Present ONE authorization plan → its OK is the run
Print the plan **before any isolation and before any write**. It carries, in this order:

- **the whole list**, in queue order — one row per spec: slug · derived stage · `complexity` ·
  tasks remaining · the locator the tool returned;
- **the N**, stated as a number;
- the base branch, the branch the queue will cut, the isolation form, and the primary
  branch the single pull request will target;
- **all three forms** of §The recursive return, with **no recursion** pre-marked and said on
  screen to be the *provisional* default — until a real run absorbs a promoted spec, nothing has
  measured what a second generation adds to the PR;
- **the human's own stopping criterion**, in their words.

Then ask with ONE **AskUserQuestion**, carrying the approval, the recursion form and the stopping
criterion. An adjustment — a spec dropped, the order changed — re-presents the plan and asks
again. **The OK of this plan is the run's authorization.**

**No flag reaches this plan.** The one argument is a list of slugs: nothing changes mode, effort,
isolation, or the volume of questions. **There is no cap on N and no soft warning** (§The queue's
shape) — the plan shows the list and the N, which is what the human decides on; a threshold nobody
measured would add the appearance of measurement without the measurement.

Declare the authorization verbatim to every stage this run invokes, naming this command as the
grantor, per
[convergence.md](../../references/align/convergence.md)
§The cycle-authorization contract:
*"Running under quenching-specs-execute-queue authorization granted at run start — skip your
plan-confirmation pause; present your plan as narration and execute; code-coupled and irreversible
items still gate individually."*

A queued spec whose `approved` record is unset is settled **here**, with one line saying what it
commits to — the sub-agent that builds it cannot ask. The plan's OK stamps it,
`cq specs record "<slug>" approved --set date=<today>`, never by editing the frontmatter.
**Done when:** the plan is approved as presented, or the run is declined with nothing written.

### 3. Isolate once, for the whole queue
Load the precondition and the naming rules:

```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" components read ../../references/specs-execute/execution.md \
  --sections "§The precondition"
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" components read ../../references/git/isolation.md \
  --sections "§Branch and worktree names"
```

`git status --porcelain` non-empty → **refuse to start**; offer to commit or stash.

Cut **one** ref for the whole queue, named `plan/<the first slug>` — the name is a suggestion
there, never a contract, which is exactly what lets one branch carry N specs. Worktree leads, with
its cost stated in the offer as `quenching-specs-execute` states it; on a worktree a declared
`worktreeSetup` runs once with cwd inside the new tree, and **every stage from here runs with that
cwd**.

**Nothing is stamped here.** Each `quenching-specs-execute` then starts on a branch that is not
the base, adopts it, and stamps its own `branch:` record — so the queue cuts the ref and never
writes the record for it.
**Done when:** the tree was clean and this checkout is on the queue's single work ref.

### 4. Run the queue, one spec at a time
Load the shape and the block classification once, before the first spec:

```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" components read ../../references/specs-fanout/fanout.md \
  --sections "§The queue's shape" --sections "§Classifying a block" \
  --sections "§The branch carries the slugs"
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" components read ../../references/specs-execute/execution.md \
  --sections "§Delegating an executor"
```

For each spec, in queue order:

a. **Dispatch ONE `Task` sub-agent, pinned to the session model — never `haiku`.** Its whole
   instruction is to invoke `quenching:specs:execute <slug>` through the Skill tool under step 2's
   authorization sentence, and to return: tasks checked, tasks blocked, **the classification of any
   block**, the commits it made, and **the gate command it ran** under the spec's declared policy.
   The conductor keeps every confirmation and all the bookkeeping (§Delegating an executor).

b. **Run that returned gate command again, over the branch as it now stands.** Never judge who
   chose the policy — a declared policy is authoritative by definition (§The entry contract). This
   is the run over 1..N that parallel building never performs (§The two regimes).

c. **Act on the classification** (§Classifying a block):

   | What came back | What the queue does |
   | --- | --- |
   | nothing blocked | move to the next spec |
   | **local** | leave the executor's `[!]` where it is, take the slug off `quenching-slugs:`, move on |
   | **contaminating** | stop and ask with **AskUserQuestion** — carry on with the next spec, or end the queue here |
   | **red gate** | stop, whatever the classification said |

   A slug comes off the line by the read-merge-write in
   [isolation.md](../../references/git/isolation.md) §Marking the branch with
   the specs it built — one line, rewritten and never duplicated.

d. **`complexity` risen mid-run → leave the run and re-authorize.** Return to step 2 with a fresh
   plan; the run's OK does not cover the larger size. The rise is a fact this run *observes* —
   `complexity` declares `[triage, create, develop]` as its writers, so nothing here stamps it.

**Done when:** every queued spec has finished or the queue stopped for a stated reason, and
`quenching-slugs:` names exactly what the branch carries.

### 5. Take the recursive return the plan chose
The **only** source is specs promoted out of `## Discoveries` on this pass — read the front back
with `cq specs list --json` and filter them through §The entry contract exactly as step 1 does.
The form was chosen in step 2:

- **no recursion** → nothing is absorbed; what this run revealed waits in `plans/`.
- **one generation** → queue the specs promoted on this pass, once. A second generation is never
  offered.
- **unbounded fixpoint** → repeat until a pass promotes nothing. The entry contract is the bound:
  a promoted spec at or above the fan-out floor needs `ready`/`approved`, so it leaves the return
  rather than extending it.

A return re-enters step 4 **on the same branch** — never a second isolation, never a second pull
request. Announce each generation as it opens: which specs it absorbed, and which of the two
bounds — the form's own, or the human's stated stopping criterion — closed it.
**Done when:** the chosen form has nothing left to absorb, or the stopping criterion was met and
is named.

### 6. Close the branch out — one conclude, one pull request
Invoke `quenching:specs:conclude` through the Skill tool **with no `--spec`**, under step 2's
authorization sentence, and on the **pull-request route** against the primary branch — the route
was approved in step 2's plan and is never rediscussed here
([convergence.md](../../references/align/convergence.md) §The PR route).
`conclude` resolves the whole set from the branch's `quenching-slugs:` line, which is the queue's
only handoff to it (§The branch carries the slugs).
**Done when:** `conclude` has returned and the pull request it opened is named with its link.

### 7. Report

```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" components read ../../references/specs-develop/spec-driven.md \
  --sections "§The report mold" --rules-only
```

Emit §The report mold on its **front-wide** header form, substituted for this run — `## The queue —
4 specs on plan/<first slug>` — because a queue is N specs, not one. Three body blocks:

1. **Built** — fixed. One row per spec: slug · tasks checked · the commits it made · the gate's
   verdict after it.
2. **Left out** — fixed, printing `—` when empty. Every spec excluded at step 1 and every one
   blocked mid-queue, each with its reason and the command that closes it. This block is what keeps
   the pull request from implying it carries what it does not.
3. **The return** — optional. Each generation absorbed, and what closed it.

Close on §The next-step block, its recommended line naming the pull request opened in step 6.
**Done when:** the report names what entered the pull request, what did not, and why.

## Output during the queue

Progress as it happens, not a report — the mold governs step 7, this governs the loop. Its glyphs
are §The report mold's and mean the same, and this banner prints plain text, never a heading:

```
Queue: 4 specs → plan/<first slug> → PR against the primary branch

[2/4] <slug> — executing · 6 tasks
✓ execute: 6/6 checked, 2 commits
✓ gate: pnpm test — passed
✓ branch mark: quenching-slugs: <slug1>,<slug2>
```

## Hard rules — no exceptions, and no "just this once"

- **Never leave a blocked spec's slug on `quenching-slugs:`.** That line is the whole set
  `conclude` builds the pull request from, so a slug left on it makes the PR claim work it does not
  carry — and nothing downstream can tell the difference.
- **Never chain.** One branch, one pull request, against the primary branch — no
  stacked branches, no stacked PRs, no rebase-on-green queue. Chaining trades a merge conflict for
  a rebase conflict and couples the specs' fates in sequence.
- **Never run a spec's executor on `haiku`.** It is writing production code, under the same model
  policy that protects `quenching-knowledge-import-memory`'s classifiers.

## Invariants to never violate

- Invoke every stage, never reimplement one — `quenching-specs-execute` per spec,
  `quenching-specs-conclude` once. If a stage must behave differently, change the stage.
- Present the whole list, the N, all three recursion forms and the stopping criterion **before**
  the isolation, and never apply an authorization to a queue the plan did not present.
- Keep the run flagless: the one argument is a list of slugs, and no invocation flag changes mode,
  effort, isolation or the volume of questions.
- Cap nothing: no ceiling on N, and no soft warning about its size. The plan is where the size is
  decided.
- Run the verification policy each spec declares, and never judge who chose it.
- Observe a risen `complexity`; never stamp it, and never carry the old authorization past it.
- Write no file of your own. The one write this body makes is the `quenching-slugs:` line, and only
  to remove a blocked spec's slug from it.
- Never review the branch, merge, archive or distil from here — that is `quenching-specs-conclude`,
  invoked once at the end.
- Never hand this command file `context: fork` — the contaminating-block stop and the `complexity`
  re-authorization are mid-flow confirmations, and a forked context can present neither. This
  command has no gear, so it has no minimal-gear admission either.
