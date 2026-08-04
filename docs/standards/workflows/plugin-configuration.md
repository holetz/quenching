---
type: standard
title: Plugin configuration contract
description: `.claude/quenching.json` as the plugin's single configuration home — where it lives and why it left the specs workspace, the five recognised keys and their defaults, the one key that deliberately has none and refuses instead, the one key a second tool reads and why it had nowhere else to live, why every other way it can be wrong is a field rather than an exception, and why a stranded `specs/config.json` is named instead of merged
resource: plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/hooks/okf-validate.py, plugins/quenching/assets/references/specs-execute/git.md, plugins/quenching/assets/references/specs-create/specs-front.md
tags: [workflows, specs, configuration, backend, plugin]
timestamp: 2026-08-03
audience: both
authority: current
source: configurable-spec-backend plan (task 1.4); `azureStates` documented by the same plan's branch review at conclude, which found the table listing three keys against four in the code; `docsDir` added by the enxugar-create-e-eliminar-o-rung-hooks spec (2026-08-03) once the checker went plugin-wired and a per-repo override could no longer be read from the script's own directory — recorded there as a Discovery deferred out of that spec's `## Impact`, and written at its conclude
maintainer: quenching
---

# Plugin configuration contract

One file holds everything a target repository declares to this plugin. This standard is where it
lives, what it may say, and the reading rules that keep a configuration file from becoming a source
of exceptions.

## One file, at the repo root

```
.claude/quenching.json
```

At the **root of the target repository**, beside the rest of `.claude/` — not inside `specs/`, and
not inside `docs/`.

```json
{
  "backend": "files",
  "specsBranch": "specs",
  "worktreeSetup": "./scripts/wt-setup.sh"
}
```

Read with `json.load` — a plain object, no new format, no prose to parse. **`specs.py` is no longer
its only reader**: `okf-validate.py` reads `docsDir` from the same file, which is what makes this
the *plugin's* configuration rather than the `specs/` front's (§The configuration stopped belonging
to one front).

## The recognised keys

| Key | Values | Default | Read by |
| --- | --- | --- | --- |
| `backend` | `files` · `github` · `azure-boards` | `files` | the spec backend selection |
| `specsBranch` | any branch name | `specs` | the `files` backend only |
| `worktreeSetup` | a shell command, run as written | none | `/specs:execute`'s isolation offer, after `git worktree add` |
| `azureStates` | `{"plans": "<state>", "archive": "<state>"}` | **none, deliberately** | the `azure-boards` backend only |
| `docsDir` | a path relative to the repo root | `docs` | `okf-validate.py`, as CLI **and** hook |

**`docsDir` is the one key `specs.py` does not read, and it is here because it had nowhere else to
live.** The checker's other settings (`warnAsError`, `blockOnFail`, `hardBlock`, `deadlineMs`,
`stopScan`, `ignoreGlobs`) come from the target's own `.claude/hooks/hooks-config.json`, which the
target maintains by hand — nothing installs one any more. `docsDir` could not: the checker is now
wired by the plugin's own `hooks/hooks.json`, so it runs from the plugin's tree, and a per-repo
override has to be read relative to the **project directory** rather than the script's. This file is
the only per-repo configuration the plugin already resolves that way, so `docsDir` was moved into
it and takes precedence over any `hooks-config.json` value.

Whether the other six deserve the same treatment is **open** — they are currently reachable only by
a target hand-writing a file no command creates.

`worktreeSetup` keeps the contract it had in its old home unchanged — who runs it, with which cwd,
what a failure means, and why the consent is the isolation offer rather than a prompt of its own,
are all owned by [worktree-setup.md](worktree-setup.md). Only the file it is read from moved.

**`specsBranch` is configurable rather than fixed** because `specs` is a short, plausible name a
target repository may already use for something else, and a backend that collides with an existing
branch fails on its first operation with no recourse. Namespacing it (`quenching/specs`) would avoid
the collision and charge the longer name to every repository that never had the problem. Configurable
pays the cost only where it exists — and if no real target ever sets it, the key is a candidate for
removal rather than a permanent fixture.

**`azureStates` is the one key with no default, and the absence is the decision.** A phase maps onto
a state, and what the states *are* is defined by the Azure DevOps project's **process**: Basic says
To Do/Doing/Done, Agile says New/Active/Resolved/Closed, Scrum says New/…/Done/Removed, and a
customised process says whatever it likes. GitHub needs no equivalent because open/closed is
universal. A guessed default would not fail loudly — it would read every archived spec as active in
half the projects it ran against, which is the failure shape that survives longest unnoticed. So
`azure-boards` **refuses (exit 2, `sp-az-no-states`)** with the shape to declare, and reads and
writes nothing.

This is also the one key whose absence is a refusal rather than a default, and the exception is
narrow on purpose: it refuses only for the backend that needs it. A repository on `files` or
`github` never sees it, which is why §Absence is the normal case below still holds.

## Absence is the normal case, and never a finding

Most repositories declare nothing, so declaring nothing must cost nothing: `specs.py config` exits 0
with the defaults and no output worth reading. An absent file, an absent key, and a malformed one
all yield **the documented defaults** — never `null`, and never a refusal.

That last part is the load-bearing half. A loader that returned a null backend when nothing was
declared would break every repository that configured nothing while every configured one kept
working, which is the failure shape that survives longest unnoticed. `specs.py selftest` asserts the
defaults against a path that cannot exist, so the assertion never depends on the checkout it runs in.

## Every way it can be wrong is a field, never an exception

`load_config` reports; `doctor` judges. The loader never raises and never refuses — it returns what
it read alongside what it could not use, and each finding below is `warn`, because a repository with
a malformed config is still a repository and every other command still works.

| State | Effect | Finding |
| --- | --- | --- |
| no file, or a key absent | the default | no |
| an unrecognised key | the default | `sp-config-unknown-key` |
| an unrecognised `backend` value | the default backend, with the typed value quoted back | `sp-config-unknown-backend` |
| malformed JSON | all defaults | `sp-config-unparseable` |
| a `specs/config.json` still on disk | not read | `sp-config-legacy-location` |

**These findings exist for one failure mode**: something written where something else was expected —
`worktree_setup` for `worktreeSetup`, `gitlab` for a backend that exists. The file is valid JSON, the
key or the value is simply never used, nothing runs, and the human concludes the feature is broken.
An unrecognised backend keeps the typed string in the report precisely so `doctor` can quote it back;
degrading to the default backend rather than to no backend keeps a typo from taking the tool down.

## Why it left the specs workspace

This relocates a file whose old home was itself a recorded decision, and the reversal is stated
rather than quietly made. `specs/config.json` sat at the root of the specs workspace, holding one
key, and [worktree-setup.md](worktree-setup.md) argued that home deliberately: not in `docs/`, a
different bundle with a different owner, and not at the repo root, which belongs to the target.

Two things broke it, and neither existed when it was chosen:

- **A repository may have no `specs/` folder at all.** Once the backend can be external, the specs
  workspace is no longer guaranteed to exist — and a configuration file that lives inside the
  workspace cannot be the thing that says where the workspace is, or whether there is one.
- **The configuration stopped belonging to one front.** `backend` is not a specs-workspace
  parameter; it decides what the workspace *is*. `.claude/` is the one directory every front already
  shares, and it belongs to this plugin's surface rather than to the target's own layout — which was
  the real objection to the repo root.

The old argument's conclusion — one extensible file, a schema of named keys, and findings that keep
"extensible" from meaning "silently ignores whatever you typed" — is not reversed. It is the part
that carried over.

## A stranded config is named, never merged

A repository that upgrades without moving its file is the one shape where every command keeps
working and nothing it declared is read. `load_config` returns the leftover path as `legacyPath` and
does not read it; `doctor` raises `sp-config-legacy-location` pointing at the new home.

Merging the two would be worse than either. A repository with two configuration files and no stated
winner cannot be reasoned about from the outside, and the moment their keys disagree there is no
answer to which one is in effect. One file plainly stranded and named is a state a human can fix in
one move.

The stranded file also stays **exempt from the specs-root stray-file check**, even though nothing
reads it any more. Reporting it as a stray would offer to move it into a phase folder, which is the
one thing that must not happen to it.
