# `.claude/quenching.json` — the recognised keys

The specs front's own copy of what `.claude/quenching.json` recognises — the keys `cq specs
config` reads, their defaults, and the two refusals a malformed value earns. This is not the
plugin's whole configuration story: it is the slice `specs-align/conformance.md` needs to judge a
target's file, kept here so that judgment does not depend on a bundle standard a target may not
have installed.

## Contents

`cq components read <this file>` returns the heading index; `--sections` addresses one.

## The recognised keys

<!-- rules -->

| Key | Values | Default | Read by |
| --- | --- | --- | --- |
| `backend` | `files` · `github` · `azure-boards` | `files` | the spec backend selection |
| `specsBranch` | any branch name | `specs` | the `files` backend only |
| `worktreeSetup` | a shell command, run as written | none | `/quenching:specs:execute`'s isolation offer, after `git worktree add` |
| `azureStates` | `{"plans": "<state>", "archive": "<state>"}` | **none, deliberately** — refuses (exit 2, `sp-az-no-states`) rather than guess | the `azure-boards` backend only |
| `integrationBranch` | any branch name | **none** — `cq specs release` applies `develop` at the point of use | the release verb, and the base-inference chain for a spec with no stamped `branch` record |
| `releaseBranch` | any branch name | **none** — `cq specs release` applies `main` at the point of use | the release verb only |
| `hooks` | `{"<event>": [{"command": "<cmd>", ...}]}` | none — an absent key declares no events | the command that owns the event |
| `profiles` | `{"installed": ["knowledge", "specs", "components"]}` | none — an absent key leaves all three fronts installed | the `/align` conductor |
| `azurePlacement` | `{areaPath, workItemType, discoveryTag, team, iterationPath, boardColumn, defaultSubject}` — `workItemType` retired, see `workItemTypes` below | per sub-key — `areaPath` **none, deliberately**, the rest default | the `azure-boards` backend only |
| `azureColumns` | `{"<board state>": "<lane>", …}` — any subset | `{}` — falls back to `azurePlacement.boardColumn` per state | the `azure-boards` backend only |
| `subjects` | `{"<key>": {name, description, parent, tags}, …}` | `{}` | `/quenching:specs:create`'s subject proposal |
| `tagCatalog` | `{"<tag>": "<description>", …}` | `{}` | `/quenching:specs:create`'s tag proposal |
| `workItemTypes` | `{"<key>": {description, azure, github, default}, …}` | `{}` | `/quenching:specs:create`'s type proposal, `cq specs new --type`, and every backend's `create_spec` |

`integrationBranch`/`releaseBranch` default to `None` here, deliberately, unlike the other keys:
the base-inference chain must be able to tell "this repo declared an integration branch" from
"this repo declared nothing", because only the first wins over `git symbolic-ref
refs/remotes/origin/HEAD`. `azureStates` is the one key whose absence is a refusal rather than a
default — a guessed state mapping would not fail loudly, it would read every archived spec as
active in half the projects it ran against.

The checker's own settings (`warnAsError`, `ignoreGlobs`) and the bundle root never lived in this
file — they come from the target's own `.claude/hooks/hooks-config.json`, and the bundle root is
the fixed `/.knowledge/` convention no configuration names.
