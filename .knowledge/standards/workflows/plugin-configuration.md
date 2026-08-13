---
type: standard
title: Plugin configuration contract
description: `.claude/quenching.json` as the plugin's single configuration home — where it lives and why it left the specs workspace, the recognised keys and their defaults, the two keys that deliberately have none and refuse instead, the two keys with two consumers each — the release verb and the base-inference chain — the three keys whose prose is prompt material an agent reads to decide, why every other way it can be wrong is a field rather than an exception, and why a stranded `specs/config.json` is named instead of merged
resource: plugins/quenching/assets/bin/quenching/specs/**, plugins/quenching/assets/bin/quenching/knowledge/**, plugins/quenching/assets/references/specs-execute/git.md, plugins/quenching/assets/references/specs-align/conformance.md
tags: [workflows, specs, configuration, backend, plugin]
timestamp: 2026-08-11
audience: both
authority: current
source: configurable-spec-backend plan (task 1.4); `azureStates` documented by the same plan's branch review at conclude, which found the table listing three keys against four in the code; the bundle-root config key added by the enxugar-create-e-eliminar-o-rung-hooks spec (2026-08-03) once the checker went plugin-wired and a per-repo override could no longer be read from the script's own directory — recorded there as a Discovery deferred out of that spec's `## Impact`, and written at its conclude, and removed by the docs-em-diretorio-customizado spec (task 1.4, 2026-08-06) — the bundle root became the fixed `/.knowledge/` convention, and the key that said where the bundle lives had nothing left to say ([bundle-root.md](../architecture/bundle-root.md)); `integrationBranch`/`releaseBranch` added by the configurable-branch-strategy spec (task 2.1, 2026-08-04) — the develop/main flow's two consumers, [branching.md](../git/branching.md); `azurePlacement`/`azureColumns`/`subjects`/`tagCatalog` added by provar-e-posicionar-o-backend-azure-boards (task 2.8), which also measured `areaPath`'s absence against this org's own board (761 unrelated work items under the project's default area); `workItemTypes` added and `azurePlacement.workItemType` retired by suportar-tipo-workitem-azure-por-tags (task 6.1), which moved a spec's type from one repo-wide default to a per-spec choice resolved from a declared catalog — measured live (task 4.3) against a real Azure Boards project (org unicredbr, team "Diretoria Risco")
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
  "worktreeSetup": "./scripts/wt-setup.sh",
  "integrationBranch": "develop",
  "releaseBranch": "main"
}
```

Read with `json.load` — a plain object, no new format, no prose to parse. **`cq specs` is the one
reader**, and the file is the *plugin's* configuration rather than the `specs/` front's
(§The configuration stopped belonging to one front).

## The recognised keys

| Key | Values | Default | Read by |
| --- | --- | --- | --- |
| `backend` | `files` · `github` · `azure-boards` | `files` | the spec backend selection |
| `specsBranch` | any branch name | `specs` | the `files` backend only |
| `worktreeSetup` | a shell command, run as written | none | `/quenching:specs:execute`'s isolation offer, after `git worktree add` |
| `azureStates` | `{"plans": "<state>", "archive": "<state>"}` | **none, deliberately** | the `azure-boards` backend only |
| `integrationBranch` | any branch name | **none** — `cq specs release` applies `develop` at the point of use | the release verb, and the base-inference chain for a spec with no stamped `branch` record |
| `releaseBranch` | any branch name | **none** — `cq specs release` applies `main` at the point of use | the release verb only |
| `hooks` | `{"<event>": [{"command": "<cmd>", ...}]}` | none — an absent key declares no events | the command that owns the event, through the config the core read |
| `profiles` | `{"installed": ["knowledge", "specs", "components"]}` | none — an absent key leaves all three fronts installed | the `/align` conductor, through the config the core read |
| `azurePlacement` | `{areaPath, workItemType, discoveryTag, team, iterationPath, boardColumn, defaultSubject, repository}` — `workItemType` retired, see `workItemTypes` below | per sub-key — `areaPath` **none, deliberately**, the rest default (see below) | the `azure-boards` backend only |
| `azureColumns` | `{"<board state>": "<lane>", …}` — any subset | `{}` — falls back to `azurePlacement.boardColumn` per state | the `azure-boards` backend only |
| `subjects` | `{"<key>": {name, description, parent, tags}, …}` | `{}` | `/quenching:specs:create`'s subject proposal, and every backend's `create_spec` |
| `tagCatalog` | `{"<tag>": "<description>", …}` | `{}` | `/quenching:specs:create`'s tag proposal — an agent reads the description to choose |
| `workItemTypes` | `{"<key>": {description, azure, github, default}, …}` | `{}` | `/quenching:specs:create`'s type proposal, `cq specs new --type`, and every backend's `create_spec` |

**The checker's settings never lived in this file, and the bundle root is not one either.**
`warnAsError`, `blockOnFail`, `hardBlock`, `deadlineMs`, `stopScan` and `ignoreGlobs` come from the
target's own `.claude/hooks/hooks-config.json`, which the target maintains by hand — nothing
installs one any more. The bundle root the checker validates is the fixed `/.knowledge/` convention,
which no configuration names ([bundle-root.md](../architecture/bundle-root.md)) — the
key that used to say where the bundle lives is gone rather than relocated. Whether the other six
deserve a home in this file is **open** — they are currently reachable only by a target
hand-writing a file no command creates.

`worktreeSetup` keeps the contract it had in its old home unchanged — who runs it, with which cwd,
what a failure means, and why the consent is the isolation offer rather than a prompt of its own,
are all owned by [worktree-setup.md](worktree-setup.md). Only the file it is read from moved.

**`specsBranch` is configurable rather than fixed** because `specs` is a short, plausible name a
target repository may already use for something else, and a backend that collides with an existing
branch fails on its first operation with no recourse. Namespacing it (`quenching/specs`) would avoid
the collision and charge the longer name to every repository that never had the problem. Configurable
pays the cost only where it exists — and if no real target ever sets it, the key is a candidate for
removal rather than a permanent fixture.

**`integrationBranch`/`releaseBranch` default to `None` here, deliberately, unlike every other
key in this table.** `cq specs release` applies `develop`/`main` itself once a value is missing —
those two strings are its constants, not `load_config`'s. The reason is the base-inference chain:
resolving an unstamped spec's `base` must be able to tell "this repo declared an integration
branch" from "this repo declared nothing", because only the first should ever win over
`git symbolic-ref refs/remotes/origin/HEAD`. Folding the default into `load_config`'s own return
would erase that distinction for every repository that never opted into the develop/main flow —
[branching.md](../git/branching.md) — and infer `develop` for one that has no such branch at all.

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

**`hooks` is where a repository declares the work it wants attached to an event a command
announces** — `{"after_specs_execute_task": [{"command": "/my:security-review",
"optional": true}]}` is the shape, and `after_specs_execute_task` is the one event this plugin
ships. The core reads the block whole and validates its **shape** — an event must map to a list
of hook objects each carrying a `command`; a hook with `enabled: false` is filtered out of the
read and never announced — and interprets nothing: it does not know what the declared command is
for, and it never evaluates a `condition`. The three-part contract and the reason the extension
lives in config rather than in a command are [extension-points.md](../automation/extension-points.md).

**`profiles` is where a repository declares which fronts it uses** —
`{"installed": ["knowledge", "specs", "components"]}` is the shape, the three names the plugin's own
fronts ([install-profiles.md](../architecture/install-profiles.md) §The front is the unit of
installation). The core reads the block and validates its **shape** — `installed` must be a list
of non-empty strings — and interprets nothing: what a front is, and what the list means, is the
standard's, not the loader's. Absent, it declares nothing and nothing changes: behaviour with no
profile is behaviour with all three fronts installed, which is the ordinary case. What a profile
turns on and off, and what `/align` does with an uninstalled front, are
[install-profiles.md](../architecture/install-profiles.md).
## `azurePlacement`, and the one sub-key with no default

Where a work item is born — its area, its type, its parent, its iteration, its board column — is
declared here rather than derived, for the argument
[spec-backend.md](../architecture/spec-backend.md) §Placement is declared, and reaffirmed on every
write states in full. This standard is where each sub-key's own default, or its absence, is argued.

**`areaPath` has no default, and refuses (exit 2, `sp-az-no-area`) exactly like `azureStates`
does.** Measured against this org's own target project: the project's default area is its root,
and the declared board covers **one** sub-area of 761 otherwise-unrelated work items. A guessed
default would not fail loudly — it would write into the wrong part of somebody else's board,
silently indistinguishable from a right write until a human goes looking.

**`discoveryTag` defaults to `quenching-spec`.** Unlike `areaPath`, this name is the TOOL's, not
the project's — the same argument `specsBranch` already carries — so it defaults rather than
refuses; configurable only to resolve a collision with a tag the project already uses.

**`workItemType` is RETIRED and no longer read for resolution** — the type a spec is born under
is now `workItemTypes`' business (below), which answers per spec rather than once for the whole
repository. The key stays recognised, never folded into the generic unknown-key finding, because
a repository that still declares it gets a graduated signal: beside a `workItemTypes` catalog that
already resolves a type, it is dead configuration, named once at create and once by `doctor`;
being the only thing that ever resolved a type, ignoring it would silently change what a create
writes, so the create refuses instead (exit 2, `sp-az-workitemtype-only-answer`) — the same
argument `areaPath` and `azureStates` already carry, applied to a key losing its old job rather
than to one that never had a default.

**`team`, `iterationPath`, `boardColumn` and `defaultSubject` are all optional**, and `team` is
required in practice only once a spec write needs to resolve a board column — `azureColumns`
consults a per-team field, so a repository that never declares `team` simply never gets a column
applied. `boardColumn` is the de-para's fallback for a board state absent from `azureColumns`,
never a value written on its own.

**`repository` has no default, and its absence is never a refusal** — the opposite shape from
`areaPath`. It names the Azure Repos repository backing this target's CODE, and
[spec-backend.md](../architecture/spec-backend.md) already establishes why nothing here derives
it: an Azure DevOps remote URL carries an organization and a repository, and the repository is not
the project, so a board project's own configuration says nothing about which repository (if any)
holds the code. Declared, it resolves once to the repository's and project's ids and every write
that just stamped `branch:` or a task's `subject:` links the matching branch or commit as an
`ArtifactLink` on the work item. Absent — the ordinary case, since most `azure-boards` targets keep
their code elsewhere entirely — nothing is attempted and nothing is missing: there is no native
surface to render onto. It never covers a PR: `pr:`/`merge.pr` always name a `github` pull request,
and Azure Repos' own `PullRequestId` artifact scheme names a pull request that is itself in Azure
Repos — not the same artifact, so not a mapping either key could honestly make.

## Three keys are prompt material, not documentation

`subjects.<key>.description`, every `tagCatalog` value and every `workItemTypes.<key>.description`
are prose an AGENT reads to decide — `/quenching:specs:create` proposes a subject, a tag or a type by
reading these descriptions, and a human confirms. That makes them closer to a prompt than to a
code comment: a vague or misleading description does not fail loudly, it makes the agent propose
the wrong subject, tag or type, confidently.

**The same review this file already gets is what reviews them** — there is no second reviewer for
this prose, because there is no second author. `.claude/quenching.json` belongs to the target
repository, so whoever maintains it there is who decides what a subject, a tag or a type means;
this plugin only ever reads the description, never writes or grades it. A description that stops
matching what its subject, tag or type is actually for is a configuration bug in the same sense a
wrong `areaPath` is — silent, and found by a human noticing the wrong proposal rather than by a
check.

## Absence is the normal case, and never a finding

Most repositories declare nothing, so declaring nothing must cost nothing: `cq specs config` exits 0
with the defaults and no output worth reading. An absent file, an absent key, and a malformed one
all yield **the documented defaults** — never `null`, and never a refusal.

That last part is the load-bearing half. A loader that returned a null backend when nothing was
declared would break every repository that configured nothing while every configured one kept
working, which is the failure shape that survives longest unnoticed. The test suite asserts the
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
