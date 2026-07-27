---
description: Answer "which spec now, and which command?" — read the whole plans/ front, show the ordering, and hand off. Triggers on "what should I work on", "what is next", "continue", "pick up where I left off", "which spec now", "what is in flight", "where were we", "resume the plan". One tool call, no sub-agents, no file reads: the ranking, the reason each spec sits where it does, and the one command to run next. Suggests ranking the front first when nothing has been started and nothing carries a priority. Hands off; never builds, edits, or closes anything itself. Not for: building a spec → /specs:execute; sharpening one → /specs:develop; closing one out → /specs:conclude; the full conformance view of the workspace → /specs:status.
argument-hint: [slug]
allowed-tools: Bash(python3:*), Bash(py:*), AskUserQuestion, Skill
---

# /specs:continue — which spec now, and which command

**Input**: `$ARGUMENTS` — optionally a spec slug. With one, this answers "what is next **for that
spec**"; without one, "what is next **on the front**".

The router. Every other `/specs:*` command answers a question you already knew to ask; this one
answers the question you have when you sit down: *what now?*

**It must stay near-free.** One `specs.py` call, no file reads, no sub-agents. A router that costs
as much as the work it routes to is a router nobody runs — and this is the command that gets run
most often, on the least context, by someone who has just come back to a repo.

The layout, the derived stages and the `specs.py` surface live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md),
cited and never restated.

## Resolving the tool

Resolve `specs.py` by the fallback in
[specs-create/plans-zone.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-create/plans-zone.md)
§Resolving the tool. Branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

## Doctrine

- **The tool ranks; this command reports and routes.** `specs.py next --front` is the only place
  the ordering lives — four factors, lexicographic: what is already executing, then closest to
  done, then the human's `priority`, then age. Never re-sort its output, never add a factor of your
  own, and never argue with the top candidate.
- **Show the reason, not just the winner.** Each candidate carries a `reason` naming the one
  dominant factor. A recommendation whose grounds are visible can be overruled in one word; a bare
  answer has to be trusted or re-derived.
- **Hand off; never do the work.** This command runs no build, writes no section, stamps no record,
  closes nothing. It ends by invoking one of the four working commands, or by naming it.
- **Say when the ranking has nothing to stand on.** `needsTriage: true` means nothing is executing
  and nothing carries a `priority` — the order is age alone, which is an ordering, not a judgment.
  Say exactly that and offer `/specs:triage` first.
- **An empty front is an answer.** No specs is not an error and not a failure to route: it is
  `/specs:create`, in one line.

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
| `write_section` | the ready gate is not met; `heading` names the first gap | `/specs:develop <slug>` |
| `implement_task` | there is an open task, with its `verify:` and `files:` | `/specs:execute <slug>` |
| `blocked` | every remaining task is `[!]`, with its reason | report the reasons; unblocking is the human's, then `/specs:execute` |
| `promote` | every task is done | `/specs:conclude <slug>` |
| `done` | it is archived | nothing to do; offer the front-wide view instead |

For **the front**, take `top` as the recommendation, then read that spec's own `action` by the same
table. `count` is 0 → say the front is empty and name `/specs:create`. `needsTriage` is true → say
the ordering rests on age alone and offer `/specs:triage` before anything else.

Two things the payload does not decide, and which are named rather than routed around: a spec whose
`approved` is null still builds (`execute` asks inline), and unresolved `## Discoveries` lines are
`/specs:develop`'s discoveries bank.
**Done when:** exactly one next command is identified, with the spec it applies to.

### 3. Show the ordering, and offer the hand-off
Show the top candidate with its `reason`, then the rest as a short list — slug, stage, task
progress, and reason — so an overrule costs one word. With more than a handful, show the top three
and say how many are behind them.

Then offer the hand-off with **AskUserQuestion**: the recommended command (marked
"(Recommended)"), a different spec from the list, or stop here. Taken → invoke it with the `Skill`
tool. Declined → name the command and its argument in one line and stop.
**Done when:** the hand-off was taken or declined, and the command name was stated either way.

## Output

```
## The specs front — 6 specs in plans/

→ session-tokens · executing · 5/9 tasks · executing — 5/9 tasks done
    next: /specs:execute session-tokens  (task 3.2, verify: pnpm test auth/)

  rate-limit-api      · ready     · 0/12  · ready to build, untouched for 9d
  webhook-retries     · proposed  · —     · proposed, 21d old
  … 3 more
```

## Invariants to never violate

- Never re-rank, re-sort, or second-guess `next --front`'s ordering.
- Never read a spec file, run a second `specs.py` subcommand, or dispatch a sub-agent. One call.
- Never write anything: no section, no record, no checkbox, no listing zone.
- Never recommend a command the payload's `action` does not support — routing is a lookup, not a
  judgment.
- Never present an age-only ordering as a ranking. When `needsTriage` is true, say so and offer
  `/specs:triage`.
- Never refuse over a missing `approved` or an unmet gate — both are somebody else's to handle, and
  naming the command that handles them is this one's whole job.
- Never invoke a hand-off the human did not take.
