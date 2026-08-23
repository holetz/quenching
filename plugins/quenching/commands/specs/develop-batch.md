---
description: >-
  Take N specs below the `ready` gate to `ready` on ONE authorization — each spec in a sub-agent of
  its own, all launched together. Triggers on "define these specs", "develop the whole backlog",
  "fill in the sections of all of them", "take these specs to ready", "batch the spec definition".
  Nothing it runs takes a branch or writes code, which is what lets the batch run in real parallel;
  every sub-agent drafts its own spec and returns what it filled and what it left open, while the
  authorization, a contaminating block and `approved` all stay with the conductor. Not for:
  building N specs → /quenching:specs:execute-queue; ONE spec, with a human answering its questions
  → /quenching:specs:develop; ranking the front → /quenching:specs:triage.
argument-hint: [IDs-or-description]
allowed-tools: Bash(python3:*), Bash(py:*), Bash(git status:*), AskUserQuestion, Task
---

# /quenching:specs:develop-batch — N specs defined at once, on one authorization

**Input**: `$ARGUMENTS` — spec IDs, or a description of which specs to define.

Takes N specs sitting **below the `ready` gate** and has each one defined toward `ready` by a
sub-agent of its own, all launched in one message. `/quenching:specs:develop` is what runs inside
each; this command selects the set, holds every confirmation, and accounts for what came back.

**A batch, not a queue — and the name says so on purpose.** `create` and `develop` take no branch,
and under the `github` and `azure-boards` backends they touch no file at all, so N specs really do
run at the same time. Serialization is the declared feature of the *building* entry alone
(`/quenching:specs:execute-queue`); the criterion that splits the two regimes, and the collision
measurement behind it, is
[specs-fanout/fanout.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-fanout/fanout.md) §The two
regimes — a run never has to read it.

**Load now, and nothing else** — the rule every run applies to decide who is in:

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-fanout/fanout.md \
  --sections "§The entry contract" --rules-only
```

§The recursive return is loaded by step 3 and §Classifying a block by step 6 — each in the step
that uses it, never in a preamble every later turn pays for regardless.

## Resolving the tool

Resolve `cq` (`cq components read` is the section reader every `§X` citation here resolves through)
per
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool, §Write the resolved path literally on every invocation; branch on the **exit
code** (0 ok · 1 findings · 2 refusal) and the `--json`, never on prose.

## Doctrine

- **Admission derives from the derived stage and `priority.complexity`, and from nothing else.**
  No invocation flag, no menu — §The entry contract, already loaded, is the whole rule. A
  `complexity` this run observes rising is named and re-authorized, never stamped.
- **Every confirmation stays here.** No sub-agent talks to the human, stamps `approved`, or mints a
  spec out of a `## Discoveries` line. Each returns what it filled and what it left open; the split
  is
  [specs-execute/execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md)
  §Delegating an executor's, and it is unchanged by there being N of them.
- **A question no evidence answers becomes `## Open Decisions`.** That is `/quenching:specs:develop`'s
  own invariant — never invent an answer — and it is what makes a bank runnable with nobody to ask.
  The sub-agent writes what the spec, the `/.knowledge/standards/` its `## Impact` declares and
  `/.knowledge/glossary.md` support, and parks the rest with how it will be decided. **A batch buys
  the drafting, not the judgment.**
- **Invoke, never reimplement.** Each sub-agent runs `quenching:specs:develop` on its one spec,
  under that command's own banks and its own safe-write invariants. If defining must behave
  differently, change that command.
- **Parallel because the writes are disjoint, not because it is faster.** One ID per sub-agent,
  and none of them writes `/.knowledge/`, so the write sets are disjoint by construction rather than
  by a check. Step 7 measures that against `git status --porcelain` instead of asserting it.
- **Sub-agents pinned to the session model — never `haiku`.** A misdrafted section is a section a
  human is about to approve, so the model policy is §Delegating an executor's, unchanged.

## Workflow

### 1. Resolve the candidate set
Take the IDs from `$ARGUMENTS`, or take the whole front. Two calls carry the selection and the
fan-out floor §The entry contract measures every candidate against:

```bash
cq specs list --json      # every spec's derived stage AND its records, priority.complexity included
cq specs config --json    # fanoutMinComplexity — the floor §2's split reads
```

Both fields admission needs are on every row, so no per-spec read runs here. An ID matching two
specs is exit 2 — report both and stop, never guess which was meant. **One spec resolved is not a
batch:** name `/quenching:specs:develop <id>` and stop.
**Done when:** two or more candidates are in hand, each with its stage and its `complexity`, and
the floor is known.

### 2. Split the candidates by the entry contract
Apply §The entry contract to every candidate, and put each in exactly one group:

| The candidate | Group | What the plan says about it |
| --- | --- | --- |
| below `ready`, and the contract enters it **at defining** | **admitted** | it runs in this batch |
| the contract enters it **at building** | not admitted | `/quenching:specs:execute-queue`, once it is `ready`/`approved` |
| `ready` or beyond | not admitted | there is nothing left to define |
| no `complexity` on its `priority` record | not admitted | nothing to derive from — `/quenching:specs:triage` declares it |

The first two rows read their condition off the loaded contract; the levels are never transcribed
here, so a contract that moves a level moves this split with it.

Nothing is written in this step; the split is what the plan shows.
**Done when:** every candidate sits in exactly one group.

### 3. Present ONE plan → the OK is the run's authorization
One **AskUserQuestion**, one table: every admitted spec with its derived stage and its
`complexity`, then the three groups that were not admitted, each with the command that owns it,
then the N. **No cap and no soft warning** — the whole list and the N are on screen, and that is
what the human decides on.

**No per-spec read runs before the OK.** The derived stage already says which bank each spec will
get, and N reads ahead of an authorization that may be declined are N reads paid for nothing.

Present the recursion form on the same screen — load it now:

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-fanout/fanout.md \
  --sections "§The recursive return" --rules-only
```

All three forms are shown with **no recursion** pre-marked as the provisional default the contract
declares, and with the human's own stopping criterion. Promotion out of `## Discoveries` is this
command's, never a sub-agent's, and a promoted spec re-enters through step 2 like everything else.

The OK of this plan is the run's authorization. Declare it verbatim to every sub-agent, per
[align/convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md) §The
cycle-authorization contract, naming this command as the grantor — with the one clause a batch
changes, because a sub-agent has no human to interrupt:

*"Running under /quenching:specs:develop-batch authorization granted at run start — skip your
plan-confirmation pause; present your plan as narration and execute. Ask the human nothing: a
question no evidence answers goes to `## Open Decisions` with how it will be decided. Never stamp
`approved`, never stamp `complexity`, never mint a spec — return them to me instead."*
**Done when:** the plan is approved as presented (or trimmed and re-presented), or the run is
declined and nothing is written.

### 4. Launch every admitted spec at once
**N `Task` calls in ONE message** — N messages would be a serial queue wearing this command's name.
Each sub-agent is pinned to the session model, gets exactly one ID, invokes
`quenching:specs:develop` on it under step 3's declaration, runs the four-item self-review on what
it wrote before returning, and returns five things and no diff:

| The return | What it carries |
| --- | --- |
| **filled** | the sections written, and the records stamped — `refined`, `verification`, never `approved` |
| **open** | every `## Open Decisions` line, quoted, with how it will be decided |
| **parked** | every `## Discoveries` line it wrote, quoted — parked, never promoted |
| **complexity** | the level the pass revealed and the evidence that moved it, when it moved — unstamped |
| **block** | `local` or `contaminating`, with the reason, when the spec could not be taken further |

**Done when:** every launched sub-agent has returned.

### 5. Re-derive from disk, and validate
The returns are reports; disk is the fact.

```bash
cq specs list --json      # the stage each spec in the batch actually reached
cq specs validate --json  # the sp-* codes over the whole front, in one call
```

A spec a sub-agent called filled that did not reach `ready`, or that validate reports against, is
**not** offered for approval in step 7 — it is reported with what is missing. A malformed section
in one spec reaches no other spec, because the files were disjoint, so this never stops the batch.
**Done when:** every batched spec's real stage and validate state are in hand.

### 6. Classify what came back open
Load the classification now, and apply it to every `block` a sub-agent returned:

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-fanout/fanout.md \
  --sections "§Classifying a block" --rules-only
```

- **local** → the spec keeps exactly what it has, with its `## Open Decisions` line standing in for
  the queue's `[!]`; the rest of the batch is unaffected.
- **contaminating** → **stop and ask, before step 7.** A batch is launched at once, so the
  classification arrives after the siblings have already written: what it stops is the approval and
  any recursive return, never a draft that already exists. Present the block and what it may change
  in the other specs, and wait.

A spec whose `complexity` rose leaves the batch under §The entry contract: name it with the
evidence the sub-agent returned, stamp nothing, and ask for a **fresh** authorization — this run's
OK does not cover the level it moved to.
**Done when:** every returned block is classified and acted on, and every rise has been put to the
human.

### 7. Verify the working tree, then offer `approved`

```bash
git status --porcelain
cq specs config --json    # backend
```

Under `github` and `azure-boards` the batch changed no file at all — the specs are issues, and the
porcelain has nothing of theirs in it. Under `files` the specs **are** files, so the batch did write
the tree: the porcelain must name the batch's own `plans/<id>.md` and nothing else. Any other path
is a sub-agent that left its lane — report it before anything is approved.

Then the closing offer: one **AskUserQuestion** over the specs that really reached `ready`, asking
which carry `approved` today. Stamp only what the human named:

```bash
cq specs record <id> approved --set date=<today>
```

Write-once — a spec already carrying it reports the date it holds, which is the answer, not an
obstacle.
**Done when:** the porcelain is accounted for and every `approved` the human named is stamped.

### 8. Report
Per spec: the ID, the stage it reached, the records stamped, what it left open (quoted), and its
block if it had one. Then the run's own lines: the candidates that were not admitted with the
command each needs, every `complexity` rise and how it was authorized, and the recursion form the
plan chose with what it absorbed or deferred.

Close by naming what each outcome wants next — `/quenching:specs:execute-queue` for the specs that
reached `approved`, and `/quenching:specs:develop <id>` for one whose open decisions need a human
answering them one at a time.
**Done when:** every batched spec and every non-admitted candidate is named with its next command.

## Invariants to never violate

- **This command writes exactly one thing: the `approved` record the human named in step 7.** Every
  section and every other record belongs to the sub-agent that owns that spec.
- **Never hand this command file `context: fork`.** A contaminating block and a `complexity` rise
  both stop the run mid-flow and ask, and a forked context cannot present either. There is no
  minimal-gear admission here: this run opens no pull request for a review to live in.
- Never launch the batch in more than one message — N `Task` calls in one message is what makes the
  specs run at the same time.
- **One ID per sub-agent, one sub-agent per ID.** Two sub-agents sharing a spec is the only way
  this batch can collide, and the split is what makes the writes provably disjoint.
- Never let a sub-agent talk to the human, stamp `approved`, promote a `## Discoveries` line, or
  write into `/.knowledge/`.
- Never stamp `complexity` — this run observes the rise and re-authorizes; the writers are
  `[triage, create, develop]`.
- Never fabricate `approved`. It is stamped only for a spec a human just named on screen, and only
  after step 5 showed the stage it actually reached.
- Never admit a spec the entry contract excludes, and never let a trimmed plan silently re-admit
  one — an adjusted plan is re-presented before it runs.
- Never report a spec as `ready` on a sub-agent's word. Step 5's `cq specs list --json` is what says
  where it landed.
- Never open a cited reference as a file — `§X` is an address, loaded through
  `cq components read --sections`.
