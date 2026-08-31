# `.claude/quenching.json` — the envelope and recognised namespaces

The specs front's own copy of what `.claude/quenching.json` recognises — the root metadata and
namespaced declarations `cq specs config` reads, their defaults, and the refusals a malformed value
earns. Specs are provider-owned: the file configures the GitHub or Azure Boards transport and
placement, never a repository store. Other namespaces are read by their owning front.

## Contents

`cq components read <this file>` returns the heading index; `--sections` addresses one.

## The envelope and recognised namespaces

<!-- rules -->

| Key | Values | Default | Read by |
| --- | --- | --- | --- |
| `backend` | `github` · `azure-boards` | derived from the repository remote | provider selection and legacy-value refusal |
| `shared.worktreeSetup` | a shell command, run as written | none | `/quenching:specs:execute`'s isolation offer, after `git worktree add` |
| `shared.sharedPaths` | a list of repo-relative paths | none — an absent or empty list declares no shared area | `cq git worktree link`, from the isolation flow |
| `shared.hooks` | `{"<event>": [{"command": "<cmd>", ...}]}` | none — an absent key declares no events | the command that owns the event |
| `shared.profiles` | `{"installed": ["knowledge", "specs", "design", "components"]}` | none — an absent key leaves all four fronts installed | the align conductor |
| `specs.azureStates` | `{"plans": "<state>", "archive": "<state>"}` | **none, deliberately** — refuses (exit 2, `sp-az-no-states`) rather than guess | the `azure-boards` backend only |
| `specs.azurePlacement` | `{areaPath, workItemType, discoveryTag, team, iterationPath, boardColumn, defaultSubject}` — `workItemType` retired, see `workItemTypes` below | per sub-key — `areaPath` **none, deliberately**, the rest default | the `azure-boards` backend only |
| `specs.azureColumns` | `{"<board state>": "<lane>", …}` — any subset | `{}` — falls back to `azurePlacement.boardColumn` per state | the `azure-boards` backend only |
| `specs.subjects` | `{"<key>": {name, description, parent, tags}, …}` | `{}` | `/quenching:specs:create`'s subject proposal |
| `specs.tagCatalog` | `{"<tag>": "<description>", …}` | `{}` | `/quenching:specs:create`'s tag proposal |
| `specs.workItemTypes` | `{"<key>": {description, azure, github, default}, …}` | `{}` | `/quenching:specs:create`'s type proposal, `cq specs new --type`, and every backend's `create_spec` |
| `specs.specsBranch` | a branch name | `specs` | specs lifecycle records |
| `specs.fanoutMinComplexity` | `low` · `medium` · `high` · `xhigh` | `medium` | specs fan-out selection |
| `ops.opsRoot`, `ops.router` | repository-relative paths | none — `op-config-missing` when absent | `cq ops` |
| `ops.registry` | a repository-relative path | `<ops.opsRoot>/README.md` | `cq ops registry` |
| `proof.proofRoot` | a repository-relative path | `tests` | `cq proof` |
| `proof.layers`, `proof.measuredRoots`, `proof.proofExclusions`, `proof.ratchetPath` | proof declarations | documented proof defaults | `cq proof` |

`specs.azureStates` is the one key whose absence is a refusal rather than a
default — a guessed state mapping would not fail loudly, it would read every archived spec as
active in half the projects it ran against.

Root-level front-owned keys such as `opsRoot`, `router`, `proofRoot`, `layers`, `hooks` and
`worktreeSetup` are legacy flat declarations. A flat or mixed document is refused with
`sp-config-unscoped` and exit 2, naming each key and its destination namespace; no namespace wins
and no value is merged.

The checker's own settings (`warnAsError`, `ignoreGlobs`) and the bundle root never lived in this
file — they come from the target's own `.claude/hooks/hooks-config.json`, and the bundle root is
the fixed `/docs/` convention no configuration names.
