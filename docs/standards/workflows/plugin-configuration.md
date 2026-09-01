---
type: standard
title: Plugin configuration contract
description: `.claude/quenching.json` is the plugin's single configuration home; provider selection is derived from the repository remote, while placement, Azure mappings, lifecycle hooks, profiles, proposal catalogues and the `git` pillar's per-artifact writing directives remain explicit target settings
resource: .claude/quenching.json, plugins/quenching/assets/bin/quenching/common/config.py, plugins/quenching/assets/bin/quenching/specs/config.py, plugins/quenching/assets/bin/quenching/ops/**, plugins/quenching/assets/bin/quenching/proof/**, plugins/quenching/assets/bin/quenching/git/base.py, plugins/quenching/assets/bin/quenching/git/conventions.py
tags: [workflows, specs, configuration, provider, plugin]
timestamp: 2026-09-01
audience: both
authority: current
source: spec 1065 (task 3.1) — the namespaced envelope and migration refusal are implemented and covered by the source test matrix; extended by spec 1075 (2026-09-01) with `shared.gitConventions`, the `git` pillar's per-artifact writing directives
maintainer: quenching
---

# Plugin configuration contract

The target repository has one configuration home. It is a plain JSON object whose root carries
provider-neutral metadata and explicit namespaces for settings owned by a front or shared by more
than one pillar. The file is configuration, not a second specs store: provider-owned specs remain
on the selected external provider.

## One configuration home

The Claude projection reads:

```text
.claude/quenching.json
```

The file is at the root of the target repository, beside the rest of `.claude/`. The Codex
projection uses the corresponding `.agents/quenching.json` home; both projections carry the same
envelope and namespace contract. A leftover `/.specs/config.json` is diagnostic residue and is
never merged with this file.

There is no per-front configuration file and no precedence order between two configuration
sources. One file and one namespace owner keep a declaration visible to every reader that needs
it.

## The envelope and its owners

The root-level envelope is deliberately small:

```json
{
  "backend": "github",
  "shared": {
    "worktreeSetup": "./scripts/wt-setup.sh",
    "sharedPaths": [".cache"],
    "hooks": {
      "after_specs_execute_task": [
        {"command": "/my:security-review", "optional": true}
      ]
    },
    "profiles": {"installed": ["knowledge", "specs", "components"]},
    "gitConventions": {"commitSubject": "Prefixe o subject com o ticket entre colchetes."}
  },
  "specs": {
    "specsBranch": "specs",
    "azureStates": {"plans": "New", "archive": "Closed"},
    "azurePlacement": {"areaPath": "Project\\Specs"},
    "azureColumns": {},
    "subjects": {},
    "tagCatalog": {},
    "workItemTypes": {}
  },
  "ops": {
    "opsRoot": "scripts",
    "router": "pyproject.toml",
    "registry": "scripts/registry.md"
  },
  "proof": {
    "proofRoot": "tests",
    "layers": {},
    "measuredRoots": ["src"],
    "proofExclusions": [],
    "ratchetPath": null
  }
}
```

Ownership follows the meaning of the key, not the module that happens to read it:

| Namespace | Owned declarations | Boundary |
| --- | --- | --- |
| root | `backend` | legacy/provider metadata only; provider selection comes from `origin` |
| `shared` | `worktreeSetup`, `sharedPaths`, `hooks`, `profiles`, `gitConventions` | settings used by more than one local surface or by isolation |
| `specs` | `specsBranch`, Azure state and placement mappings, `subjects`, `tagCatalog`, `workItemTypes` | provider-owned plan lifecycle and proposal conventions |
| `ops` | `opsRoot`, `router`, `registry` | operations inventory, router and generated registry |
| `proof` | `proofRoot`, `layers`, `measuredRoots`, `proofExclusions`, `ratchetPath` | verification inventory, layers and coverage evidence |

The shared loader discovers the home, parses JSON, derives provider metadata, and classifies the
envelope. It does not interpret a front's values. Each adapter validates and resolves only its own
namespace. `ops`, `proof`, and `git` consume the common boundary directly; they do not import the
specs adapter to obtain shared configuration.

## Provider-derived selection

The provider is derived from the repository's `origin` remote:

- a `github.com` host selects GitHub Issues;
- an Azure DevOps host selects Azure Boards;
- no recognized remote host is an exit-2 refusal, never a silent switch to another provider.

The root `backend` value is not a second provider selector. Unsupported or retired backend values
are refused, and a valid provider is still established from the remote. Provider-owned specs are
read and written only after that selection succeeds.

The `specs` namespace does not name a local specs root, archive, or storage branch. A declared
`specsBranch` is a lifecycle input for the branch record, not a repository-backed specs store.

## No flat fallback and no merge

The old root-level front keys are migration evidence, not a compatibility API. If a configuration
contains one of them — whether alone or alongside a namespace — the common loader returns the
dedicated `sp-config-unscoped` refusal with exit `2`. The payload names every offending key, its
destination namespace, whether the document is pure-flat or mixed, and the direct migration
instruction.

```json
{
  "code": "sp-config-unscoped",
  "exit": 2,
  "shape": "mixed",
  "keys": ["opsRoot"],
  "destinations": [{"key": "opsRoot", "namespace": "ops"}]
}
```

The front must not read a flat key as an absent namespace, merge flat and namespaced values, or let
the namespaced value silently win. The absence of a front-owned declaration is a different state:
it uses the adapter's documented default or its existing required-key refusal.

Unknown namespace and invalid namespace-shape diagnostics remain visible at the envelope boundary.
An unknown namespace is not treated as a new front, and an array or scalar where a namespace object
is expected is not flattened into one. Unknown keys inside an accepted namespace remain that
namespace adapter's responsibility; no other adapter may claim them.

## The `git` pillar's writing directives

`shared.gitConventions` is how a target tells the plugin how to word the texts the `git` pillar
writes, without publishing a standard that also governs its humans. Five recognised sub-keys, one
per artifact — `commitSubject`, `branchName`, `prTitle`, `prBody`, `mergeSubject`:

```json
{
  "shared": {
    "gitConventions": {
      "commitSubject": "Prefixe o subject com o ticket entre colchetes; imperativo, sem ponto final.",
      "branchName": "feat/<ticket>-<handle-kebab>.",
      "prTitle": "O subject do primeiro commit, sem o prefixo do ticket.",
      "prBody": "Tres blocos: o que muda, como provar, o que fica de fora.",
      "mergeSubject": "Merge <branch> (<strategy>)."
    }
  }
}
```

It is `shared` for the same reason `worktreeSetup` and `hooks` are: the `git` pillar runs inside
every front's build loop, and it consumes the common boundary directly rather than through the
specs adapter.

Every value is prompt material, exactly as `subjects.<key>.description` and `tagCatalog` values
are: an agent reads the directive and writes the text. **The core never interpolates a placeholder,
expands a template, or judges the text that came out** — `<ticket>` above is the target's own
notation for its own reader, not a field the plugin fills.

Resolution is **per artifact**, and the artifacts never move together:

| Order | What governs |
| --- | --- |
| 1 | the caller's explicit value |
| 2 | `shared.gitConventions.<artifact>` |
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
are `warn`. A `gitConventions` declared at the root instead is neither — it is the envelope's own
`sp-config-unscoped` refusal, which names `shared` as its destination.

**No command writes `gitConventions` into a target.** A directive the plugin authored stops being
the target's, which is the prohibition the `git` pillar's own `conventions.md` already carries for
`docs/standards/git/**`. The pillar reads this key and never repairs it, which is why it takes no
arbiter row under
[configuration-arbitration.md](../architecture/configuration-arbitration.md).

## Defaults and refusals

Defaults apply only after the document has passed the envelope boundary. In particular:

- `ops` refuses `op-config-missing` when either `opsRoot` or `router` is absent; it never guesses
  `scripts/` or a router;
- `proof` keeps its documented proof-root and ratchet defaults, and refuses malformed declarations
  at its own boundary;
- `specs` keeps its provider, Azure, catalogue, hook and profile semantics without
  importing values from `ops` or `proof`;
- `git` derives its base branch from git facts (`origin/HEAD`, then `init.defaultBranch`, then
  `main`) and does not use a front-owned flat key as a fallback.

The command result vocabulary remains uniform: `0` means the requested state is valid, `1` means
the command found reportable drift, and `2` means it refused to guess, migrate, or operate without
an unambiguous declaration.

## Migration is diagnostic

The plugin does not rewrite an installed target's file, create a migration command, or choose a
release boundary for this breaking change. To migrate, move each listed root key into the
destination namespace named by `sp-config-unscoped`, then run the owning front's verifier. A
configuration is ready only when the refusal disappears and the front-specific defaults or
required declarations are evaluated normally.

This standard defines the source projection's contract. Its Codex projection must preserve the
same ownership, refusal payload and no-fallback rule while using `.agents/quenching.json` as its
configuration home.
