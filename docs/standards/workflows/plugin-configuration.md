---
type: standard
title: Plugin configuration contract
description: `.claude/quenching.json` is the plugin's single configuration home; provider selection is derived from the repository remote, while placement, Azure mappings, lifecycle hooks, profiles, proposal catalogues and the `git` pillar's per-artifact writing directives remain explicit target settings
resource: plugins/quenching/assets/bin/quenching/specs/**, plugins/quenching/assets/bin/quenching/knowledge/**, plugins/quenching/assets/bin/quenching/git/**, plugins/quenching/assets/references/git/isolation.md, plugins/quenching/assets/references/git/conventions.md, plugins/quenching/assets/references/specs-align/conformance.md
tags: [workflows, specs, configuration, provider, plugin]
timestamp: 2026-09-01
audience: both
authority: current
source: remover-backend-local-do-plugin (task 4.4) — provider selection moved out of repository storage configuration; `.claude/quenching.json` now carries only provider placement and shared plugin settings; extended by declarar-as-convencoes-de-escrita-da-camada-git-no-quenching-json (spec 1075, 2026-09-01) with `gitConventions`
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
| `gitConventions` | `{"<artifact>": "<directive>", ...}` over five recognised sub-keys | `{}` | the `git` pillar, through `cq git conventions` |

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

## The `git` pillar's writing directives

`gitConventions` is how a target tells the plugin how to word the texts the `git` pillar writes,
without publishing a standard that also governs its humans. Five recognised sub-keys, one per
artifact:

```json
{
  "gitConventions": {
    "commitSubject": "Prefixe o subject com o ticket entre colchetes; imperativo, sem ponto final.",
    "branchName": "feat/<ticket>-<handle-kebab>.",
    "prTitle": "O subject do primeiro commit, sem o prefixo do ticket.",
    "prBody": "Tres blocos: o que muda, como provar, o que fica de fora.",
    "mergeSubject": "Merge <branch> (<strategy>)."
  }
}
```

Every value is prompt material, exactly as `subjects.<key>.description` and `tagCatalog` values
are: an agent reads the directive and writes the text. **The core never interpolates a
placeholder, expands a template, or judges the text that came out** — `<ticket>` above is the
target's own notation for its own reader, not a field the plugin fills.

Resolution is **per artifact**, and the artifacts never move together:

| Order | What governs |
| --- | --- |
| 1 | the caller's explicit value |
| 2 | `gitConventions.<artifact>` |
| 3 | `docs/standards/git/**`, for what the doc covers |
| 4 | the plugin's own default |

The configuration outranks the target's own git standard because it is addressed to the plugin by
name and is narrower — one artifact per sub-key, against a document that governs humans too — and
because a key that lost to any `docs/standards/git/**` would be dead in exactly the repositories
most likely to declare both. The standard still governs every artifact the configuration does not
name.

`cq git conventions --json` is the one reader of both declared layers: `config` carries the
directives, `configUnknown` the sub-keys nothing reads, and `governs`/`declared` answer the docs
layer and only it. A single word over three layers would have to lie in the ordinary case, where
the configuration names two artifacts and the target's own doc covers the rest.

Two `doctor` findings exist so that a directive which never applies is named rather than silent:
`sp-config-unknown-git-convention` for a sub-key outside the five, and
`sp-config-bad-git-convention` for a recognised sub-key whose value is not a non-empty string. Both
are `warn` — the same argument `sp-config-unknown-key` carries one key up.

**No command writes `gitConventions` into a target.** A directive the plugin authored stops being
the target's, which is the prohibition the `git` pillar's own `conventions.md` already carries for
`docs/standards/git/**`.

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

The OKF bundle is always `/docs/` ([bundle-root.md](../architecture/bundle-root.md)). Specs
are in the selected provider. No setting in this file names a specs directory, branch, archive, or
worktree for provider documents.
