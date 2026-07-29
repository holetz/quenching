---
type: standard
title: Worktree setup contract
description: The `specs/config.json` contract — the one recognised key, where the file lives, what its absence means, who runs the declared command and with which cwd, and why the consent is the isolation offer rather than a prompt of its own
resource: plugins/quenching/assets/bin/specs.py, plugins/quenching/commands/specs/isolate.md, plugins/quenching/assets/references/specs-isolate/git.md
tags: [workflows, specs, worktree, configuration, consent]
timestamp: 2026-07-28
audience: both
authority: current
source: prefer-worktree-isolation plan (task 4.2)
maintainer: quenching
---

# Worktree setup contract

A worktree is a fresh checkout: it carries what git tracks and nothing else — no `node_modules/`,
no `.venv/`, no `.env`, no build output. In a repository with installed dependencies that makes the
recommended isolation the one that breaks at the first `verify:`. This standard is the one hook
that closes that gap, and the bounds that keep a hook from becoming a configuration system.

## One file, one key

```
specs/config.json
```

At the **root of the specs workspace**, beside `plans/` and `archive/` — not in `docs/`, which is a
different bundle with a different owner, and not at the repo root, which belongs to the target.

```json
{"worktreeSetup": "./scripts/wt-setup.sh"}
```

`worktreeSetup` is the **only** recognised key. It holds a shell command, run as written.

Read by `specs.py` with `json.load` — a plain object, no new format, no prose to parse. The file is
also exempt from the stray-file check at the workspace root, alongside `QUENCHING.md` and
`schema.json`.

## Absence is the normal case, and never a finding

| State | `worktreeSetup` | Is it a finding? |
| --- | --- | --- |
| no `config.json` | `null` | no |
| file present, key absent | `null` | no |
| the declared command does not resolve | `null` in effect — reported as not run | no |
| an unrecognised key | `null` | **`sp-config-unknown-key`** (warn) |
| malformed JSON | `null` | **`sp-config-unparseable`** (warn) |

Most repositories declare nothing, so declaring nothing must cost nothing — `specs.py config`
exits 0 with `worktreeSetup: null` and no output worth reading.

**The two warnings exist for one failure mode**: `worktree_setup` written where `worktreeSetup` was
expected. That file is valid JSON, the key is simply never read, the setup silently never runs, and
the human concludes the feature is broken. Both findings are `warn`, never `error` — a workspace
with a malformed config is still a workspace, and every other command still works. Neither is ever
raised as a raw traceback: a truncated JSON file is a finding, not an exception.

## Who runs it, and where

`/specs:isolate` runs it — **once**, immediately after `git worktree add`, with **cwd inside the
newly created worktree**. The cwd is the entire point: the tree that lacks the dependencies is the
tree that must install them.

`specs.py` reads the value and never executes it. That split is not ceremony — the workspace root
is the only thing `specs.py` knows, and whether the command resolves can only be judged relative to
the new worktree, whose path `specs.py` is never told. The check belongs where the answer exists.

**A failing setup never undoes the worktree.** The worktree exists either way; whether it is usable
is a fact to report, not a reason to tear down a tree that may already hold the human's chosen
isolation. `/specs:isolate` reports the output and the exit code, and says plainly which of the two
happened. A command whose first token does not resolve is reported as not run, for that reason,
rather than executed and blamed on the shell.

Only `/specs:isolate` runs it, and only on creation. Re-running setup over a worktree that already
exists is a second entry point for the same hook and is deliberately not offered.

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

This reverses a recorded decision, and the reversal is stated rather than quietly made. The specs
front deliberately had no configuration: `specs.py` loads its schema and templates from
`assets/specs/` when adjacent and from embedded constants otherwise, never from the target.

The alternatives were real. `specs/worktree-setup.sh`, whose mere existence would be the
declaration, is deterministic by a single `stat` and has no format to get wrong — but it can hold
exactly one parameter forever. A `docs/standards/` doc with the path in frontmatter would follow
the read-if-present contract already used for a target's git conventions — but it forces `specs.py`
to parse markdown frontmatter to find an executable, and mixes the home of *contracts* with an
operational pointer.

An extensible declarative file wins the moment there is a second parameter. Until there is, the
schema is **one key**, and the two doctor findings above are what keep "extensible" from meaning
"silently ignores whatever you typed".
