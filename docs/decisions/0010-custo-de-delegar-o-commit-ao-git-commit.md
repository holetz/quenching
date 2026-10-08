---
type: decision
title: Cost of delegating each commit to git:commit
description: The measured per-task cost of Skill("quenching:git:commit") in /quenching:specs:execute, against a bare git commit with the same contract, and the recommended option
resource: docs/decisions/index.md
tags: [decision, cost, measured, specs]
timestamp: 2026-10-07
audience: both
authority: current
source: spec 1138
maintainer: quenching
---

# Cost of delegating each commit to git:commit

`/quenching:specs:execute` step 5e delegates every task commit to `Skill("quenching:git:commit")`
(decision of #1131). Each delegation reloads the command body and re-reads the same references the
execute run already loaded once in step 5d. This decision measures that cost and compares the
options the spec named.

## Measurement

Unit: characters actually loaded into the context, read from the tree on 2026-10-07. Tokens are an
estimate at 4 characters per token; the host exposes no per-skill token count.

| Loaded by one delegation | Characters |
| --- | --- |
| `commands/git/commit.md` body | 4898 |
| `git/conventions.md` §The declared-directive layer + §The read-if-present rule | 4220 |
| `git/commit.md` §Commit messages | 1057 |
| `cq git conventions --json` output | 1125 |
| **Total per task** | **11300 (about 2.8k tokens)** |

A bare `git commit -m "<subject>" && git log -1 --format=%s` with its output is about 0.1k tokens.

## Projection for a 22-task spec (holetz/eclume#57)

| Option | First task | Each later task | 22 tasks |
| --- | --- | --- | --- |
| Keep the delegation | 2.8k | 2.8k | about 62k tokens |
| Deterministic call (`cq git commit`, or the bare command until it exists) | 0.1k | 0.1k | about 2k tokens |
| Load the body once per execution | 2.8k | 0.1k | about 5k tokens |

Every figure is context added, and each stays in context for all later turns, so the real cost is
higher than the sum. Step 5d already loads the conventions sections, `§Commit messages` and
`cq git conventions --json` once per run, so 6.4k of the 11.3k per task is a repeat of a read the
run already holds.

## Recommendation

Stop delegating per task. Execute should commit the existing index itself with the same contract
(index as staged, never `--no-verify`, subject taken from the task and conferred against the
conventions step 5d already holds), through one deterministic `cq git commit` call. That keeps one
commit boundary in a tool, not in a re-read prose body, and saves about 60k tokens on a 22-task spec.
"Load once" is the fallback: it saves nearly as much but keeps a 4.9k body in context for the run.
`/quenching:git:commit` stays the entry point for a human commit. Implementing this is a follow-up
spec; this decision changed no command.

## Limits

The figures are loaded characters, not a tokenizer count, and the sections can change; re-measure
before building the follow-up.
