---
type: standard
title: Surface verification
description: How a change to the command surface is proven — a fresh process because the registry is built at session start, assertions on captured tool_use rather than prose, and the three preconditions a functional check must satisfy to measure what it claims
resource: plugins/claude-quenching/assets/bin/functional-checks.sh, plugins/claude-quenching/commands/**
tags: [quality, verification, automation, commands, functional-tests]
timestamp: 2026-07-27
audience: both
authority: current
source: collapse-skills-into-commands spec (tasks 7.1-7.3)
maintainer: claude-quenching
---

# Surface verification

What it takes to claim a change under `commands/**` works. The sibling
[bundle-verification.md](bundle-verification.md) covers the `docs/` front, where a checker reads
files and reports findings; this standard covers the one front whose correctness **no in-process
check can observe at all**. `assets/bin/functional-checks.sh` is the implementation.

Distinct from [../automation/skill-evaluation.md](../automation/skill-evaluation.md), which asks
whether a command *teaches* anything. This asks the prior question: whether it **loads**.

## Nothing under `commands/**` is testable in the session that writes it

The command registry is built at **session start**
([../../reference/tools/claude-code-skill-command-mechanics.md](../../reference/tools/claude-code-skill-command-mechanics.md)
§4). A file created or edited now is not invocable until a new process. Every mechanical check can
therefore pass while the entire surface is unreachable:

- `skills.py lint` and `doctor` read frontmatter off disk. Disk is not the registry.
- A citation-resolution script proves a path **exists**. It does not prove the placeholder that
  spells it ever **expands**.
- The session that made the change cannot invoke the change. Anything it reports about the new
  surface is inference from the file it just wrote.

**Never report a surface change as working on the strength of the session that made it.** Run
`assets/bin/functional-checks.sh`, which spawns one fresh `claude -p` per check.

## Assert on what the process did, never on what it said

Each check reads `tool_use` events out of `--output-format stream-json --verbose` and asserts on
their inputs — a `Read` whose path lands under `assets/references/`, a `Skill` whose name is
`claude-quenching:docs:align`. It never greps the assistant's prose.

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

## The three preconditions a check must satisfy

Each was learned by a check that would otherwise have measured something other than what it
claimed:

1. **Redirect stdin.** `claude -p` without `< /dev/null` waits on stdin and warns. Non-obvious,
   and it makes an otherwise correct check hang.
2. **An invasive check runs in a throwaway repo with its own `enabledPlugins`.** A `git init`
   scratch dir carrying
   `{"enabledPlugins": {"claude-quenching@claude-quenching": true}}` gets the real surface —
   the plugin loads from the marketplace path — while anything the command writes lands in the
   scratch dir.
3. **Satisfy the command's own preconditions, or you measure the precondition.** A spoken-routing
   probe for `/docs:add` invoked nothing in an empty sandbox — correctly, because there was no OKF
   bundle to add to. That reads as a routing failure and is not one. Re-run against a real bundle,
   it routed immediately. A check on a surface whose commands have preconditions must meet them
   before its result means anything.

**Rules 2 and 3 pull against each other, and the tension is real.** A routing probe needs a
populated repo to satisfy rule 3; a command that *writes* then writes there for real. Check 3's
capture probes ran against the live repo and left two captured specs behind, committed in
`5f31d19` — and in the v1 shape, because a stale `.claude/hooks/specs.py` resolved ahead of the
plugin's copy. **A probe that reaches a writing command produces real artifacts. Either sandbox it
with the preconditions reproduced, or expect residue and clean it up in the same commit.**

## What this does not cover

- **Whether the command is any good.** Evidence-graded with/without measurement is
  [../automation/skill-evaluation.md](../automation/skill-evaluation.md)'s.
- **Frontmatter and body conformance.** Mechanical and in-process: `skills.py lint` / `doctor`.
- **`allowed-tools` enforcement.** Never observed to restrict anything, for commands or skills
  (`claude-code-skill-command-mechanics.md` row 6). Not verified here, and not to be claimed
  anywhere until it is measured.
