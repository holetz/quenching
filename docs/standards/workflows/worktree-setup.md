---
type: standard
title: Worktree setup contract
description: The `worktreeSetup` hook — what it is for, where it is declared now that the plugin's config moved to `.claude/quenching.json`, what its absence means, who runs the declared command and with which cwd, why the consent is the isolation offer rather than a prompt of its own, and the record of why the specs front took a config file at all
resource: plugins/quenching/assets/bin/specs.py, plugins/quenching/commands/specs/isolate.md, plugins/quenching/assets/references/specs-isolate/git.md
tags: [workflows, specs, worktree, configuration, consent]
timestamp: 2026-07-31
audience: both
authority: current
source: prefer-worktree-isolation plan (task 4.2), relocated by configurable-spec-backend plan (task 1.5)
maintainer: quenching
---

# Worktree setup contract

A worktree is a fresh checkout: it carries what git tracks and nothing else — no `node_modules/`,
no `.venv/`, no `.env`, no build output. In a repository with installed dependencies that makes the
recommended isolation the one that breaks at the first `verify:`. This standard is the one hook
that closes that gap, and the bounds that keep a hook from becoming a configuration system.

## Where it is declared

```json
{"worktreeSetup": "./scripts/wt-setup.sh"}
```

In `.claude/quenching.json` at the **repo root**, the plugin's single configuration home. The file
itself — every recognised key, the defaults, the reading rules, and the findings that judge a
malformed one — is owned by [plugin-configuration.md](plugin-configuration.md). This standard owns
only what the key *means*.

`worktreeSetup` holds a shell command, run as written.

## Absence is the normal case, and never a finding

| State | `worktreeSetup` | Is it a finding? |
| --- | --- | --- |
| nothing declared | `null` | no |
| the declared command does not resolve | `null` in effect — reported as not run | no |
| the key misspelt (`worktree_setup`) | `null` | **`sp-config-unknown-key`** (warn) |

Most repositories declare nothing, so declaring nothing must cost nothing — `specs.py config` exits
0 with `worktreeSetup: null` and no output worth reading.

**The misspelling is the failure mode the finding exists for**: the file is valid JSON, the key is
simply never read, the setup silently never runs, and the human concludes the feature is broken. It
is `warn` and never `error` — a repository with a malformed config is still a repository, and every
other command still works. Neither it nor a truncated JSON file is ever raised as a raw traceback.

## Who runs it, and where

`/specs:isolate` runs it — **once**, immediately after `git worktree add`, with **cwd inside the
newly created worktree**. The cwd is the entire point: the tree that lacks the dependencies is the
tree that must install them.

`specs.py` reads the value and never executes it. That split is not ceremony — whether the command
resolves can only be judged relative to the new worktree, whose path `specs.py` is never told. The
check belongs where the answer exists.

**A failing setup never undoes the worktree.** The worktree exists either way; whether it is usable
is a fact to report, not a reason to tear down a tree that may already hold the human's chosen
isolation. `/specs:isolate` reports the output and the exit code, and says plainly which of the two
happened. A command whose first token does not resolve is reported as not run, for that reason,
rather than executed and blamed on the shell.

Only `/specs:isolate` runs it, and only on creation. Re-running setup over a worktree that already
exists is a second entry point for the same hook and is deliberately not offered.

**This hook is not the specs backend's worktree.** The `files` backend keeps its own persistent
worktree for the dedicated specs branch, created on demand and never set up: it holds spec files,
not a build. `worktreeSetup` runs for the *isolation* worktree a human works in, and nowhere else.

## The consent is the isolation offer, not a prompt of its own

This hook executes **the target repository's code**, which no `/specs:*` command did before it. The
bound is not a new confirmation:

- the command is displayed **verbatim** in `/specs:isolate`'s plan block — the same block that
  already shows the spec, the base, the branch name and the worktree path;
- choosing **Worktree** in that offer **is** the OK for the command shown;
- there is no second prompt, and no remembered "this repository is authorised" state.

The human judges the command on the same screen where they choose the form, which is the only
screen on which judging it is possible — a prompt fired later, after the decision, asks about
something already committed to. The invariant that carries it: **the command is never run without
having been displayed first.**

## Why a config file, in a front that had none

This section is the record of an earlier reversal, kept because the argument still decides things.
The specs front deliberately had no configuration: `specs.py` loads its schema and templates from
`assets/specs/` when adjacent and from embedded constants otherwise, never from the target. Taking
a config file at all reversed that.

The alternatives were real. `specs/worktree-setup.sh`, whose mere existence would be the
declaration, is deterministic by a single `stat` and has no format to get wrong — but it can hold
exactly one parameter forever. A `docs/standards/` doc with the path in frontmatter would follow
the read-if-present contract already used for a target's git conventions — but it forces `specs.py`
to parse markdown frontmatter to find an executable, and mixes the home of *contracts* with an
operational pointer.

An extensible declarative file wins the moment there is a second parameter, and the schema was held
to **one key** until there was one. That moment arrived: `backend` and `specsBranch` are the second
and third, and they are why the shape chosen here was the right bet.

### What has since been revised, and what has not

The **file** moved — `specs/config.json` became `.claude/quenching.json`, for reasons that did not
exist when this section was first written and that are recorded in
[plugin-configuration.md](plugin-configuration.md) §Why it left the specs workspace. The original
argument placed it inside the specs workspace precisely to keep it out of the repo root; what
changed is that a repository may now have no specs workspace at all.

The **conclusion** did not move. One extensible declarative file, a schema of named keys, and
findings that keep "extensible" from meaning "silently ignores whatever you typed" — that is the
part this section argued for, and it is the part still in force. Only its address changed.
