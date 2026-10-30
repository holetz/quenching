---
type: standard
title: Worktree setup contract
description: The `worktreeSetup` hook prepares a code-isolation worktree from `.agents/quenching.json`; its absence is normal, the declaration is displayed verbatim before it runs, and provider-owned specs never use this hook as persistent storage
resource: plugins/quenching/assets/bin/quenching/specs/**, plugins/quenching/commands/specs/execute.md, plugins/quenching/commands/git/branch.md, plugins/quenching/assets/references/git/isolation.md
tags: [workflows, specs, worktree, configuration, consent]
timestamp: 2026-10-30
audience: both
authority: current
source: prefer-worktree-isolation plan (task 4.2), revised by remover-backend-local-do-plugin (task 4.6); aligned to the loader by spec 1912 (namespaced example, real specs store); consent rewritten when the worktree became the unasked default (2026-10-30)
maintainer: quenching
---

# Worktree setup contract

<!-- rules -->

A worktree is a fresh checkout: it carries what git tracks and nothing else — no `node_modules/`,
no `.venv/`, no `.env`, no build output. In a repository with installed dependencies that makes the
default isolation the one that breaks at the first `verify:`. This standard is the one hook
that closes that gap, and the bounds that keep a hook from becoming a configuration system.

## Where it is declared

```json
{"shared": {"worktreeSetup": "./scripts/wt-setup.sh"}}
```

In `.agents/quenching.json` at the **repo root**, the plugin's single configuration home. The file
itself — every recognised key, the defaults, the reading rules, and the findings that judge a
malformed one — is owned by [plugin-configuration.md](plugin-configuration.md). This standard owns
only what the key *means*.

`worktreeSetup` lives in the `shared` namespace and holds a shell command, run as written. A flat
root-level `worktreeSetup` is refused with `sp-config-unscoped` (exit 2) and never read.

## Absence is the normal case, and never a finding

| State | `worktreeSetup` | Is it a finding? |
| --- | --- | --- |
| nothing declared | `null` | no |
| the declared command does not resolve | `null` in effect — reported as not run | no |
| the key misspelt (`worktree_setup`) | `null` | **`sp-config-unknown-key`** (warn) |

Most repositories declare nothing, so declaring nothing must cost nothing — `cq specs config` exits
0 with `worktreeSetup: null` and no output worth reading.

**The misspelling is the failure mode the finding exists for**: the file is valid JSON, the key is
simply never read, the setup silently never runs, and the human concludes the feature is broken. It
is `warn` and never `error` — a repository with a malformed config is still a repository, and every
other command still works. Neither it nor a truncated JSON file is ever raised as a raw traceback.

## Who runs it, and where

The isolation cut runs it — **once**, immediately after `git worktree add`, with **cwd inside the newly
created worktree**. The cwd is the entire point: the tree that lacks
the dependencies is the tree that must install them.

`cq specs` reads the value and never executes it. That split is not ceremony — whether the command
resolves can only be judged relative to the new worktree, whose path `cq specs` is never told. The
check belongs where the answer exists.

**A failing setup never undoes the worktree.** The worktree exists either way; whether it is usable
is a fact to report, not a reason to tear down a tree that may already hold the human's chosen
isolation. `/quenching-specs:specs:execute` reports the output and the exit code, and says plainly which of the two
happened. A command whose first token does not resolve is reported as not run, for that reason,
rather than executed and blamed on the shell.

Only the isolation cut runs it, and only on creation. Re-running setup over a worktree that already
exists is a second entry point for the same hook and is deliberately not offered.

**This hook prepares only the code-isolation worktree.** Specs live on the `quenching` branch (or,
deprecated, in the selected tracker), so no persistent specs worktree exists and this command is
never used to host, archive, or migrate a spec document.

## The consent is the declaration, displayed before it runs

This hook executes **the target repository's code**, which no `/quenching-specs:specs:*` command did before it. The
bound is not a new confirmation:

- the command is displayed **verbatim** in the block that reports the cut — the same block that
  shows the spec, the base, the branch name and the worktree path;
- running it is the default, and the declaration in the target's own tracked configuration is the
  OK for it — under `autonomous` too, where no human reads the display;
- there is no second prompt, and no remembered "this repository is authorised" state.

The human judges the command where it lives: a tracked line in the repository, reviewed in the same
diff that carries every other change, instead of a question repeated on every build. The invariant
that carries it: **the command is never run without having been displayed first.**

## Why this setting stays in the shared configuration

<!-- rationale -->

The setting belongs in `.agents/quenching.json` because it is a target-repository operation, not a
provider storage operation. The shared file already carries Azure placement, hooks, profiles, and
proposal catalogues; keeping `worktreeSetup` there gives every command one read path and one shape
checker without making the code worktree part of the provider contract.

The conclusion is deliberately narrow: one declarative command, displayed before execution, run
once when the worktree is cut. It does not select a provider, name a specs root, or
create a persistent store.
