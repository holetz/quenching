# `.claude/quenching.json` — the recognised keys

The specs front's own copy of what `.claude/quenching.json` recognises — the keys `cq specs
config` reads, their defaults, and the refusals a malformed value earns. Specs are provider-owned:
the file configures the GitHub or Azure Boards transport and placement, never a repository store.
This is the slice used by the provider health checks.

## Contents

`cq components read <this file>` returns the heading index; `--sections` addresses one.

## The recognised keys

<!-- rules -->

| Key | Values | Default | Read by |
| --- | --- | --- | --- |
| `backend` | `github` · `azure-boards` | derived from the repository remote | provider selection and legacy-value refusal |
| `worktreeSetup` | a shell command, run as written | none | `/quenching:specs:execute`'s isolation offer, after `git worktree add` |
| `sharedPaths` | a list of repo-relative paths | none — an absent or empty list declares no shared area | `cq git worktree link`, from the isolation flow |
| `azureStates` | `{"plans": "<state>", "archive": "<state>"}` | **none, deliberately** — refuses (exit 2, `sp-az-no-states`) rather than guess | the `azure-boards` backend only |
| `hooks` | `{"<event>": [{"command": "<cmd>", ...}]}` | none — an absent key declares no events | the command that owns the event |
| `profiles` | `{"installed": ["knowledge", "specs", "design", "components"]}` | none — an absent key leaves all four fronts installed | the align conductor |
| `azurePlacement` | `{areaPath, workItemType, discoveryTag, team, iterationPath, boardColumn, defaultSubject}` — `workItemType` retired, see `workItemTypes` below | per sub-key — `areaPath` **none, deliberately**, the rest default | the `azure-boards` backend only |
| `azureColumns` | `{"<board state>": "<lane>", …}` — any subset | `{}` — falls back to `azurePlacement.boardColumn` per state | the `azure-boards` backend only |
| `subjects` | `{"<key>": {name, description, parent, tags}, …}` | `{}` | `/quenching:specs:create`'s subject proposal |
| `tagCatalog` | `{"<tag>": "<description>", …}` | `{}` | `/quenching:specs:create`'s tag proposal |
| `workItemTypes` | `{"<key>": {description, azure, github, default}, …}` | `{}` | `/quenching:specs:create`'s type proposal, `cq specs new --type`, and every backend's `create_spec` |

`azureStates` is the one key whose absence is a refusal rather than a
default — a guessed state mapping would not fail loudly, it would read every archived spec as
active in half the projects it ran against.

The checker's own settings (`warnAsError`, `ignoreGlobs`) and the bundle root never lived in this
file — they come from the target's own `.claude/hooks/hooks-config.json`, and the bundle root is
the fixed `/docs/` convention no configuration names.
