---
type: standard
title: Plugin configuration contract
description: `.claude/quenching.json` is the plugin's single configuration home; provider selection is derived from the repository remote, while placement, Azure mappings, lifecycle hooks, profiles and proposal catalogues remain explicit target settings
resource: plugins/quenching/assets/bin/quenching/specs/**, plugins/quenching/assets/bin/quenching/knowledge/**, plugins/quenching/assets/references/git/isolation.md, plugins/quenching/assets/references/specs-align/conformance.md
tags: [workflows, specs, configuration, provider, plugin]
timestamp: 2026-08-19
audience: both
authority: current
source: remover-backend-local-do-plugin (task 4.4) — provider selection moved out of repository storage configuration; `.claude/quenching.json` now carries only provider placement and shared plugin settings
maintainer: quenching
---

# Plugin configuration contract

One file holds the target settings that this plugin is allowed to declare. Provider selection is
derived from the repository remote; the file refines placement and project conventions without
creating a second specs store.

## One file at the repository root

```text
.claude/quenching.json
```

At the root of the target repository, beside the rest of `.claude/`. It is read with `json.load` as
a plain object. `cq specs` is the one reader for specs settings; no command switches the provider
mid-flight.

```json
{
  "worktreeSetup": "./scripts/wt-setup.sh",
  "azureStates": {"plans": "New", "archive": "Closed"},
  "azurePlacement": {"areaPath": "Project\\Specs"}
}
```

## Provider-derived selection

The provider comes from `origin`:

- `github.com` selects GitHub and uses issue URLs as spec locators.
- an Azure DevOps host selects Azure Boards and uses work-item URLs as spec locators.
- no remote or an unknown host refuses with exit 2; it never falls back to another provider.

The legacy `backend` key is refusal-only. `backend: files` is not a supported store and must not
create a repository directory, branch, or worktree. A configured provider value that disagrees
with the remote is also a refusal, because silently switching the system of record loses work.

## The recognised keys

| Key | Values | Default | Read by |
| --- | --- | --- | --- |
| `worktreeSetup` | a shell command, run as written | none | the execute isolation offer, after `git worktree add` |
| `azureStates` | `{"plans": "<state>", "archive": "<state>"}` | none — Azure refuses rather than guess | Azure Boards transport |
| `hooks` | `{"<event>": [{"command": "<cmd>", ...}]}` | none — no events | the command that owns the event |
| `profiles` | `{"installed": ["knowledge", "specs", "design", "components"]}` | none — all installed | the align conductor |
| `azurePlacement` | area, type, discovery tag, team, iteration, column and subject settings | per sub-key; `areaPath` has no default | Azure Boards transport |
| `azureColumns` | `{"<board state>": "<lane>", ...}` | `{}` — falls back to placement | Azure Boards transport |
| `subjects` | `{"<key>": {name, description, parent, tags}, ...}` | `{}` | spec creation proposal |
| `tagCatalog` | `{"<tag>": "<description>", ...}` | `{}` | spec creation proposal |
| `workItemTypes` | `{"<key>": {description, azure, github, default}, ...}` | `{}` | spec creation and provider create |

`azureStates` and `azurePlacement.areaPath` have no default because a guessed value writes a work
item into the wrong project state or area. Their absence is an actionable exit-2 refusal only
when Azure Boards is selected; GitHub does not read them.

`worktreeSetup` is an execution setting, not a specs-storage setting. Its command, cwd, failure
behavior, and human consent are owned by [worktree-setup.md](worktree-setup.md). A worktree is
isolation for code changes; it never hosts a provider document.

## Hooks, profiles and proposal prose

`hooks` declares work attached to an event a command announces. The core validates shape and
passes the command through; it does not evaluate the hook or its optional condition.

`profiles` declares which plugin fronts a target installs. The core validates a list of non-empty
strings and does not reinterpret the names.

`subjects.<key>.description`, `tagCatalog` values, and `workItemTypes.<key>.description` are prompt
material. An agent reads them to propose a subject, tag, or type, and a human confirms. They are
not executable configuration and the plugin never rewrites them.

## Absence and malformed values

The provider remote is required. Once a supported provider is selected, absent optional settings
use their documented defaults. `cq specs config` returns the parsed settings; `doctor` reports
malformed JSON, unknown keys, invalid values, and missing provider requirements.

Provider selection errors are refusals, not defaults. Other malformed settings remain findings so
the health command can report all of them in one pass, but a write never proceeds when its provider
or required Azure placement is unresolved.

There is no legacy configuration location to merge. A stranded repository-store configuration is
named and refused, never read alongside the new home, because two competing sources of truth have
no safe precedence rule.

## Configuration does not name roots

The OKF bundle is always `/.knowledge/` ([bundle-root.md](../architecture/bundle-root.md)). Specs
are in the selected provider. No setting in this file names a specs directory, branch, archive, or
worktree for provider documents.
