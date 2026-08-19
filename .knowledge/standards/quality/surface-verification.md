---
type: standard
title: Surface verification
description: How a change to the command surface is proven — a fresh process because the registry is built at session start, assertions on captured tool_use rather than prose, the five preconditions a functional check must satisfy to measure what it claims, why the harness belongs to the components front rather than the spec cycle and how to scope its cost, and how an ordering property is verified by running a real cycle
resource: plugins/quenching/assets/checks/functional-checks.sh, plugins/quenching/assets/checks/conclude-order-check.sh, plugins/quenching/commands/components/command/new.md, plugins/quenching/commands/specs/conclude.md, plugins/quenching/commands/**
tags: [quality, verification, automation, commands, functional-tests, cost]
timestamp: 2026-08-19
audience: both
authority: current
source: collapse-skills-into-commands spec (tasks 7.1-7.3); fourth precondition and the ordering-check pattern from the move-conclude-merge-last spec (2026-07-28); fifth precondition measured by the verify-allowed-tools-enforcement spec (2026-07-28), inverted into the --plugin-dir rule on 2026-07-29 by the cost review of the harness — which also measured, over the whole /.specs/archive/ record, that every red run this harness produced traced to a defect in itself and none to a surface regression, and narrowed its ownership to the components front on that evidence; the stale-installed-copy half of the check-3 residue account marked impossible once resolution went plugin-first (2026-08-03, enxugar-create-e-eliminar-o-rung-hooks spec); plugin-dir-for-functional-checks task 3.2 (2026-08-19) — the harness now witnesses the precondition with static and observed-path guards
maintainer: quenching
---

# Surface verification

What it takes to claim a change under `commands/**` works. The sibling
[bundle-verification.md](bundle-verification.md) covers the `docs` front, where a checker reads
files and reports findings; this standard covers the one front whose correctness **no in-process
check can observe at all**. `assets/checks/functional-checks.sh` is the implementation.

Distinct from [../automation/skill-evaluation.md](../automation/skill-evaluation.md), which asks
whether a command *teaches* anything. This asks the prior question: whether it **loads**.

## Nothing under `commands/**` is testable in the session that writes it

The command registry is built at **session start**
([../../reference/tools/claude-code-skill-command-mechanics.md](../../reference/tools/claude-code-skill-command-mechanics.md)
§4). A file created or edited now is not invocable until a new process. Every mechanical check can
therefore pass while the entire surface is unreachable:

- `cq components lint` and `doctor` read frontmatter off disk. Disk is not the registry.
- A citation-resolution script proves a path **exists**. It does not prove the placeholder that
  spells it ever **expands**.
- The session that made the change cannot invoke the change. Anything it reports about the new
  surface is inference from the file it just wrote.

**Never report a surface change as working on the strength of the session that made it.** Run
`assets/checks/functional-checks.sh`, which spawns a fresh `claude -p` per check. Who runs it and when
is §The harness belongs to the components front; which subset is §Scope the run to what the change can
break. Where no such harness exists, **say the command is unproven until a fresh session** rather
than quoting a linter as if it had loaded anything.

## Assert on what the process did, never on what it said

Each check reads `tool_use` events out of `--output-format stream-json --verbose` and asserts on
their inputs — a `Read` whose path lands under `assets/references/`, a `Skill` whose name is
`quenching:knowledge:align`. It never greps the assistant's prose.

This is the difference between a functional test and a self-report. A model asked *"did you read
your reference file?"* will answer yes on the strength of having intended to, and a check built on
that answer passes on a surface that never loaded. The event stream records the call or it does
not.

Two consequences worth keeping:

- **The prompt must not name what the check looks for.** Check 1 asks the command to report the
  citations *its own body* gave it and to read the first, without naming a path — so a `Read`
  under `assets/references/` can only mean the placeholder resolved in production.
- **Assert the negative too.** Every check pairs "the right thing happened" with "the retired thing
  did not" — no `Read` under a `skills/` tree, no `Skill` matching a `quenching-*` name. A missed
  rewrite and a wrong one fail differently, and only the pair catches both.

## The five preconditions a check must satisfy

Each was learned by a check that would otherwise have measured something other than what it
claimed:

1. **Redirect stdin.** `claude -p` without `< /dev/null` waits on stdin and warns. Non-obvious,
   and it makes an otherwise correct check hang.
2. **An invasive check runs in a throwaway repo with its own `enabledPlugins`.** A `git init`
   scratch dir carrying
   `{"enabledPlugins": {"quenching@quenching": true}}` gets the real surface —
   the plugin loads from the marketplace path — while anything the command writes lands in the
   scratch dir.
3. **Satisfy the command's own preconditions, or you measure the precondition.** A spoken-routing
   probe for `/quenching:knowledge:add` invoked nothing in an empty sandbox — correctly, because there was no OKF
   bundle to add to. That reads as a routing failure and is not one. Re-run against a real bundle,
   it routed immediately. A check on a surface whose commands have preconditions must meet them
   before its result means anything.
4. **Read the evidence encoding-safely, or the check fails for lack of evidence.** The stream-json
   capture is UTF-8; a bare `open()` decodes it in the platform default, which on Windows is cp1252
   and raises on the first non-ASCII byte. The extractor then yields no events and every assertion
   fails — **not because the surface broke, but because nothing could be read.** Those two outcomes
   are indistinguishable in the output, which is what makes this a precondition rather than a bug.
   Measured three times on 2026-07-28: pristine `main` scored *worse* than the branch under test,
   and one check flipped verdict across identical runs. Open the capture with an explicit
   `encoding="utf-8"`, and treat a zero-event stream as **inconclusive**, never as a failure.
   The **negative** halves are why this is not merely cosmetic: "read nothing under a `skills/`
   tree" passes vacuously over an empty stream, so an unreadable capture reports a clean surface.
   Gate every assertion on the capture carrying at least one `tool_use` event of any name.

5. **Load the plugin with `--plugin-dir`, from a sandbox that enables none — or you grade a
   checkout nobody is editing.** `${CLAUDE_PLUGIN_ROOT}` resolves through the marketplace's
   `directory` source, pinned to one clone in `~/.claude/plugins/known_marketplaces.json`, and
   serves whatever `~/.claude/plugins/cache/` last installed. A probe that enables the plugin
   through that registration therefore loads *that* copy whatever tree `claude -p` was launched
   from. Measured 2026-07-28, twice: from a worktree, check 1's probe read the **main** checkout's
   reference file; and the served cache was a `3.0.0` tree still carrying a command `4.2.0` had
   deleted. `claude -p --plugin-dir <the checkout under test>` in a box whose settings enable no
   plugin loads exactly one copy, and it is the right one.

   The harness now witnesses this precondition in two independent ways: `--selfcheck` counts
   every non-commented `claude -p` invocation and requires `--plugin-dir`, while the observed-path
   anchor checks the `tool_use` capture during each applicable check. The anchor's negative half,
   which rejects `/plugins/cache/` and `/plugins/marketplaces/`, is the grading guard because those
   paths identify the stale source even when Claude Code canonicalizes or copies the plugin
   directory. Its positive `$PLUGIN` prefix is the diagnostic companion: when it differs, the
   harness prints the observed path beside the expected checkout path.

**A check that can fail for lack of evidence cannot gate anything** until it can tell that state
apart from a real verdict. Say so in the report rather than quoting its pass count. An all-
inconclusive run must not exit 0 — `functional-checks.sh` exits **2** for *nothing could be
measured*, which is neither a pass nor a failure.

## The harness belongs to the components front, not to the spec cycle

**The command that changes the surface is the command that proves it still loads.** That is
`/quenching:components:command:new`, which mints and edits a command here, and `/quenching:components:command:eval`, which tunes a description on
measured hit rates. The harness is **not** a repo-wide post-change mandate, and it is **not** named
in a spec's `## Validation` or a task's `verify:`.

`assets/checks/conclude-order-check.sh` belongs to the same front, on the same rule: it proves an
ordering property of the spec cycle — nothing is written to the base branch after the merge — so it
is rerun when that ordering logic changes (`conclude.md`, `execute.md`, or the `cq specs` backend
code), never by an individual spec that happens to reach a merge.

That is a narrowing, and it was earned by evidence rather than by budget. Measured 2026-07-29 over
the whole `/.specs/archive/` record: **every red run this harness has ever produced traced to a
defect in the harness itself** — the cp1252 read, a hardcoded marketplace ref that made a live
command read as `Unknown command`, a turn cap that reported working triggers as misses, a probe
flaky enough to flip verdict on identical runs. **Not one traced to a surface regression.**
Meanwhile the one real routing defect the repo has recorded — a `/quenching:components:hook:new` trigger that
measured as a miss — was found by `/quenching:components:command:eval`, and check 3 gained a probe for it only afterwards.

**That measurement is scoped to `functional-checks.sh` alone.** It does not extend to
`citation-check.sh` or `conclude-order-check.sh` by proximity — no equivalent record exists for
either, and the defect class that earned the rule (a cp1252 read, a hardcoded marketplace ref, a
turn cap, a probe flaky across identical runs) has no counterpart in a tool with no LLM in its
loop: both are deterministic and cheap to run (`citation-check.sh` ~0.26s, `conclude-order-check.sh`
~1.0s, against this harness's full, non-deterministic `claude -p` sessions). That is reason to find
the rule plausible there too, never reason to assert what nobody has measured —
[citation-verification.md](citation-verification.md) records the opportunistic route chosen
instead: no dedicated measurement campaign, a red run's cause recorded when one actually happens.

A check that has only ever caught itself earns a narrow trigger. Two things follow:

- **It runs where the surface is edited, once**, not on every spec that happens to reach a merge.
  A spec whose work never touches `commands/**` was paying eight agent sessions to learn nothing.
- **`/quenching:components:command:eval` is the instrument for routing, and check 3 is a worse copy of it.** Step 7 of
  that command measures the same property with should-trigger *and* should-not-trigger prompts,
  graded per command, against five hardcoded phrases with no boundary arm. Check 3 is therefore
  **opt-in** (`--only 3`), kept only to re-guard phrases already tuned; the default run is
  `1,2,4`.

## Scope the run to what the change can break

Every check here is a fresh agent session, billed per run, and they are not interchangeable in
what can move them. Making a harness all-or-nothing is what turns a correct rule into a bill:

| what changed | what can regress | what to run |
| --- | --- | --- |
| a command **body** | placeholder resolution, a stale citation, a conductor's stage names | the default — checks 1, 2, 4 |
| a `description:` line | spoken routing, and nothing else | **`/quenching:components:command:eval`**; `--only 3` only to re-guard the tuned phrases |
| a conductor's stage names | the stage reached by registry name | `--only 2,4` |

**A verification tool with no selector will be run too often or not at all.** Give one to any check
that spawns processes, state its cost where the rule that mandates it is written, and default it to
the cheap subset rather than the exhaustive one.

## When a process-spawning check *does* gate a merge, it gates before it

Nothing above is specific to this harness: it holds for any check a repo's `## Validation` names
that costs real resources per run. `/quenching:specs:conclude` step 6 runs that gate on the **work branch,
before the merge**, and a red check stops the merge.

- Run afterwards, a failure's only repair is a commit on the base — the exact write that command's
  ordering exists to prevent. Run before, it still has somewhere to be fixed.
- **The branch must already carry the base**, or the merge produces a tree neither side validated.
  `git rev-list --count plan/<slug>..<base>` non-zero → stop and say so; catching the branch up is
  a write, and the human's call.
- **It is not re-run after the merge.** Same tree, full price, no new information. Only the
  assertion that *cannot* be made earlier stays there: that the merge commit's subject is the one
  recorded before it.

This ordering became possible only with precondition 5 satisfied. While every probe loaded the
marketplace's clone, a spec that isolated before editing `commands/**` could not prove its own
change at all — a green run graded the base and a red one indicted code the probe never loaded —
so the only honest moment left was after the merge, where a failure can be reported and no longer
fixed.

**Rules 2 and 3 pull against each other, and the tension is real.** A routing probe needs a
populated repo to satisfy rule 3; a command that *writes* then writes there for real. Check 3's
capture probes ran against the live repo and left two captured specs behind, committed in
`5f31d19` — and in the v1 shape, because at the time a stale installed copy under `.claude/hooks/`
resolved ahead of the plugin's own. That second half can no longer happen: resolution is plugin-first with
no fallback and no manual rung. The residue half is untouched by that, and is the rule here. **A probe that reaches a writing command produces real artifacts. Either sandbox it
with the preconditions reproduced, or expect residue and clean it up in the same commit.**

## An ordering property is verified by running the cycle, not by reading the commands

Some claims are about **when** something happens, not about what any one file says. *"Nothing is
written to the base branch after the merge"* is true or false of a run; no linter, and no reading of
`conclude.md`, can observe it. `assets/checks/conclude-order-check.sh` is the pattern: a throwaway
`git init` repo where a spec is created, a task executed and the spec concluded end to end, then
assertions on **real git state** — `HEAD` on the base *is* the merge commit, the task's commit lists
both the code file and the ticked spec file, each recorded subject resolves to exactly one commit.

It shares this standard's two rules — a separate process, and assertions on artifacts rather than
prose — and adds a third worth naming: **assert on what git can be asked, not on what the run
reported.** `git rev-parse`, `git show --stat` and `git log --grep` are answers a passing run cannot
fake. A cycle that claimed success while leaving a commit on the base fails on the first of them.

Prefer this shape whenever a rule is phrased as an ordering, a boundary, or a "never after" — those
are the rules most likely to be quietly violated by a future edit that reads correctly.

## What this does not cover

- **Whether the command is any good.** Evidence-graded with/without measurement is
  [../automation/skill-evaluation.md](../automation/skill-evaluation.md)'s.
- **Frontmatter and body conformance.** Mechanical and in-process: `cq components lint` / `doctor`.
- **`allowed-tools` enforcement.** Never observed to restrict anything, for commands or skills
  (`claude-code-skill-command-mechanics.md` row 6). Not verified here, and not to be claimed
  anywhere until it is measured.
