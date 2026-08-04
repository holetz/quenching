---
description: Answer "which spec now, and which command?" — read the whole plans/ front, show the ordering, and hand off. Triggers on "what should I work on", "what is next", "continue", "pick up where I left off", "which spec now", "what is in flight", "where were we", "resume the plan". One tool call, no sub-agents, no file reads: the ranking, the reason each spec sits where it does, and the one command to run next. Branch-aware — the spec whose plan/<slug> branch you are standing on comes back first, and one alive but checked out elsewhere is demoted rather than offered twice. Suggests ranking the front first when nothing has been started and nothing carries a priority. Hands off; never builds, edits, or closes anything itself. Not for: building a spec → /specs:execute; sharpening one → /specs:develop; taking a branch or worktree → /specs:execute; closing one out → /specs:conclude; the full conformance view of the workspace → /specs:status.
argument-hint: [slug]
allowed-tools: Bash(python3:*), Bash(py:*), AskUserQuestion, Skill
---

# /quenching:specs:continue — which spec now, and which command

**Input**: `$ARGUMENTS` — optionally a spec slug. With one, this answers "what is next **for that
spec**"; without one, "what is next **on the front**".

The router. Every other `/specs:*` command answers a question you already knew to ask; this one
answers the question you have when you sit down: *what now?*

**It must stay near-free.** One `specs.py` call, no file reads, no sub-agents. A router that costs
as much as the work it routes to is a router nobody runs — and this is the command that gets run
most often, on the least context, by someone who has just come back to a repo.

The layout, the derived stages and the `specs.py` surface live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md),
whose §The report mold owns the shape below — both cited and never restated.

## Resolving the tool

Resolve `specs.py` per
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool. Branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

## Doctrine

- **The tool ranks; this command reports and routes.** `specs.py next --front` is the only place
  the ordering lives — a live `plan/<slug>` ref first, then four lexicographic factors: what is
  already executing, then closest to done, then the human's `priority`, then age. Never re-sort its
  output, never add a factor of your own, and never argue with the top candidate.
- **A live branch is the strongest signal there is, in both directions.** Each candidate carries
  `branch: {work, live, current}`. Standing on `plan/<slug>` puts that spec at the top — you are
  already there. A branch alive but checked out *elsewhere* pushes its spec **below** the untouched
  ones: offering it would start a second run at work already under way, and the fix is to check the
  branch out, not to build it twice. Report the branch either way, because "why is this first?"
  and "why is this last?" have the same answer.
- **The ref is the signal, never the `branch:` record.** The tool reads git, so a branch cut by hand
  with no record still counts and a record whose ref is gone stops counting. Never infer that a spec
  is in flight from frontmatter alone.
- **Show the reason, not just the winner.** Each candidate carries a `reason` naming the one
  dominant factor. A recommendation whose grounds are visible can be overruled in one word; a bare
  answer has to be trusted or re-derived.
- **Hand off; never do the work.** This command runs no build, writes no section, stamps no record,
  closes nothing. It ends by invoking one of the four working commands, or by naming it.
- **Say when the ranking has nothing to stand on.** `needsTriage: true` means nothing is executing
  and nothing carries a `priority` — the order is age alone, which is an ordering, not a judgment.
  Say exactly that and offer `/quenching:specs:triage` first.
- **An empty front is an answer.** No specs is not an error and not a failure to route: it is
  `/quenching:specs:create`, in one line.

## Workflow

### 1. Ask the tool — once
With a slug:
```bash
specs.py next --spec "<slug>" --json
```
Without one:
```bash
specs.py next --front --json
```
That is the whole read. Do not open the spec files, do not run `status`, do not run `validate` —
each of those is a different command's job, and paying for them here is what makes a router stop
being worth running.
**Done when:** one JSON payload is in hand.

### 2. Route on the data
For **one spec**, the payload's `action` is the answer:

| `action` | What it means | Hand off to |
| --- | --- | --- |
| `write_section` | the ready gate is not met; `heading` names the first gap | `/quenching:specs:develop <slug>` |
| `implement_task` | there is an open task, with its `verify:` and `files:` | `/quenching:specs:execute <slug>` |
| `blocked` | every remaining task is `[!]`, with its reason | report the reasons; unblocking is the human's, then `/quenching:specs:execute` |
| `promote` | every task is done | `/quenching:specs:conclude <slug>` |
| `done` | it is archived | nothing to do; offer the front-wide view instead |

For **the front**, take `top` as the recommendation, then read that spec's own `action` by the same
table. `count` is 0 → say the front is empty and name `/quenching:specs:create`. `needsTriage` is true → say
the ordering rests on age alone and offer `/quenching:specs:triage` before anything else.

The top candidate's `branch` changes the hand-off, not the ranking:

| `branch` on the recommended spec | What to say |
| --- | --- |
| `current: true` | you are already on `<work>`; hand off to the `action`'s command as usual |
| `live: true`, `current: false` | it is in flight on `<work>` — offer to check it out **before** building, rather than routing straight into `execute` |
| `live: false` | nothing to say; route on the `action` alone |

Two things the payload does not decide, and which are named rather than routed around: a spec whose
`approved` is null still builds (`execute` asks inline), and unresolved `## Discoveries` lines are
`/quenching:specs:develop`'s discoveries bank.
**Done when:** exactly one next command is identified, with the spec it applies to.

### 3. Report the ordering, and offer the hand-off
Emit §The report mold. One body block, fixed: §The spec table with `Spec` `Title` `Stage` `Tasks`
`Priority` `Age` `State`, the top candidate carrying `→` and every row its `reason` as `State`.
`Age` is each candidate's `ageDays`, which `next --front` already returned. With more than a handful
of rows, show the top three and elide the rest with `…`.

Then §The next-step block, whose recommended line is the routed command with this spec's slug.

Only then offer the hand-off with **AskUserQuestion**: the recommended command (marked
"(Recommended)"), a different spec from the list, or stop here. Taken → invoke it with the `Skill`
tool, which takes the registry name and not the printed slash form. Declined → the block already
names the command, so stop without repeating it.
**Done when:** the hand-off was taken or declined, and the command name was stated either way.

## Output

```
## The specs front — 6 specs in plans/

| Spec | Title | Stage | Tasks | Priority | Age | State |
| --- | --- | --- | --- | --- | --- | --- |
| → session-tokens | Budget tokens per session | executing | 5/9 | 1 · high | 3d | on this branch (`plan/session-tokens`) |
| rate-limit-api | Rate limit the public API | ready | 0/12 | 2 · high | 9d | ready to build, untouched |
| webhook-retries | Retry failed webhooks | proposed | — | — | 21d | proposed |
| … 2 more | | | | | | |
| export-csv-timeout | Fix the CSV export timeout | ready | 2/8 | — | 4d | in flight on `plan/export-csv-timeout` — check it out to continue |

Next step
→ /quenching:specs:execute session-tokens   — task 3.2, verify: pnpm test auth/
  /quenching:specs:triage                   — 3 specs carry no priority
```

## Invariants to never violate

- Never re-rank, re-sort, or second-guess `next --front`'s ordering.
- Never read a spec file, run a second `specs.py` subcommand, or dispatch a sub-agent. One call.
- Never write anything: no section, no record, no checkbox, no listing zone.
- Never recommend a command the payload's `action` does not support — routing is a lookup, not a
  judgment.
- Never present an age-only ordering as a ranking. When `needsTriage` is true, say so and offer
  `/quenching:specs:triage`.
- Never route straight into building a spec whose branch is alive somewhere else — say where it is
  and let the human check it out first.
- Never read git yourself to decide what is in flight. `next --front` already did, and ranking lives
  in one place.
- Never refuse over a missing `approved` or an unmet gate — both are somebody else's to handle, and
  naming the command that handles them is this one's whole job.
- Never invoke a hand-off the human did not take.
