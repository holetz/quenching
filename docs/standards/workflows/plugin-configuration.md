---
type: standard
title: Plugin configuration contract
description: "`.agents/quenching.json` is the plugin's single configuration home, with `.claude/quenching.json` read as legacy; provider selection is derived from the repository remote, while placement, Azure mappings, lifecycle hooks, profiles, proposal catalogues and the `git` pillar's per-artifact writing directives remain explicit target settings"
resource: .agents/quenching.json, plugins/quenching/assets/bin/quenching/common/config.py, plugins/quenching/assets/bin/quenching/specs/config.py, plugins/quenching/assets/bin/quenching/specs/store.py, plugins/quenching/assets/bin/quenching/ops/**, plugins/quenching/assets/bin/quenching/proof/**, plugins/quenching/assets/bin/quenching/git/base.py, plugins/quenching/assets/bin/quenching/git/conventions.py, plugins/quenching/assets/bin/quenching/config/**
tags: [workflows, specs, configuration, provider, plugin]
timestamp: 2026-10-28
audience: both
authority: current
source: specs 1065, 1075, 1405, 1907, 1908, 1909, 1910, 1911, 1912, 2092, 2118 — lineage in decision 0004
maintainer: quenching
---

# Plugin configuration contract

<!-- rules -->

The target repository has one configuration file; the layers around it (user, `quenching` branch) and the few settings read outside it are named below. It is a plain JSON object whose root carries
provider-neutral metadata and explicit namespaces for settings owned by a front or shared by more
than one pillar. The file is configuration, not a second specs store: specs remain
on the `quenching` branch (or, deprecated, in the selected tracker).

## One configuration home

Every projection reads:

```text
.agents/quenching.json
```

The file sits in the target repository's generic layer, beside `.agents/skills/`
([surface-translation.md](../architecture/surface-translation.md) §Target repositories). The loader
(`common/config.py`, `config_path`) resolves exactly one repository file:

- `.claude/quenching.json` present → the legacy file is read, unchanged, exactly as before the
  generic layer existed, so an upgrade never swaps a repository onto a stale `.agents/` copy.
- Absent → `.agents/quenching.json` is read.
- Both present → the legacy file is still read, and the loader's payload (`load_config`) reports
  the home as `shadowedPath`. The two are never merged; `cq components migrate` is what moves the
  home: it removes the legacy file when both are identical and reports a conflict when they differ.

Whoever writes (`cq config init`, `cq doctor --setup`) writes the file that was read, so a legacy
target is never split across two files. Every other module resolves the path through
`common/config`, never by literal. A leftover `/.specs/config.json` is diagnostic residue and is
never merged with this file.

There is no per-front configuration file. One repository file and one namespace owner keep a
declaration visible to every reader that needs it.

## The user layer

A second file, `~/.config/quenching/config.json` (overridden by `$QUENCHING_USER_CONFIG`), carries
the same envelope for the person rather than the repository. `load_config` reads it and merges it
under each namespace **key by key, the repository winning**: a key the repository declares
replaces the user's value whole, never merged into it, and a key only the user declares fills in.
The merged result is what `namespace()` and `data` return, so no reader changes.

Only the namespaces (`shared`, `specs`, `ops`, `proof`, `delivery`) count there. The root `backend`
and the pre-envelope flat keys describe one repository, so they are ignored and listed in
`userConfig.ignoredKeys`. A missing file is a no-op; an unreadable one is reported in
`userConfig.unparseable` and never fatal. A namespace the repository declares as a non-object
stays invalid. `present` and `path` still describe only the repository file.

## The branch layer and the effective view

With root `"backend": "git"`, a third file counts: `quenching.json` on the `quenching` branch, whose
`specs` namespace may declare `subjects`, `tagCatalog`, `workItemTypes`, `azurePlacement`,
`azureColumns`, `azureStates`, `artifactLanguage`, `card` and `cardAt`. Each key present there
replaces the same key from the other layers, whole. Any other key on the branch is ignored, and
with any other `backend` the branch is not read at all.

The precedence, lowest to highest, is `default` < `user` < `repository` < `branch`.
`cq config show --effective [--json]` prints every key with its effective value and the layer that
supplied it, plus each layer's path, `present` and `unparseable` state (the branch layer also
carries `applies`). A key is one row per `namespace.key`, because layers replace a key whole; the
exception is a key whose default lives in code as data (`shared.codex` and `shared.autonomy`), shown leaf by leaf
with `default` where no layer declares the leaf. A key absent from every layer and without a
default in code does not appear. The verb only reads: an unreadable layer is reported on its row of
`layers` and never fatal.

## The seed and the missing-keys check

`cq config init [--write]` creates the configuration file (`.agents/quenching.json` unless the legacy file is the one read) with every adjustable default spelled
out: `shared.codex` (including `executor`), `shared.autonomy`, `shared.contextBudgets`,
`shared.okfValidate`, `shared.workHost` (its leaves with a non-null default; `target`,
`dockerContext` and `runner` stay absent because the loader warns on a null), `specs.chat`, the
detected `shared.profiles.installed`, and `backend: git`. Without `--write` it prints the document
and writes nothing. The document is built from the owning modules' own default constants
(`config/seed.py`), so it cannot drift from the code; the two defaults that live where the
`quenching-specs` module cannot import them are restated and pinned to their owners by a test.

`init` refuses an existing file (exit 2, `cq-config-present`) and never merges into a file a human
edited. `cq config check` flattens the file to dotted leaves and lists the seeded leaves it lacks
(exit 1; exit 2 when the file is absent or not an object); it never reports extra keys, and reads
only the repository file. `cq doctor` prints the same list as a `config` block and a line in its
report, but only reports: a missing key is information, never a failed prerequisite.
`/quenching-align:align` runs `check` before the fronts and, under its one authorization, seeds an
absent file.

## The envelope and its owners

The root-level envelope is deliberately small:

```json
{
  "backend": "github",
  "shared": {
    "worktreeSetup": "./scripts/wt-setup.sh",
    "sharedPaths": [".cache"],
    "regenerablePaths": ["__pycache__", ".quenching/coverage"],
    "hooks": {
      "after_specs_execute_task": [
        {"command": "/my:security-review", "optional": true}
      ]
    },
    "profiles": {"installed": ["knowledge", "specs", "components"]},
    "gitConventions": {"commitSubject": "Prefixe o subject com o ticket entre colchetes."}
  },
  "specs": {
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

`shared.regenerablePaths` lists the ignored paths the repo regenerates on its own. `cq git worktree
retire` discards them without `--discard-ignored` and still stands on any other ignored file, such as
a `.env`. An entry without a slash matches that name at any depth; an entry with a slash matches that
path from the repo root, itself or anything under it. An absent key declares nothing.

Ownership follows the meaning of the key, not the module that happens to read it:

| Namespace | Owned declarations | Boundary |
| --- | --- | --- |
| root | `backend` | legacy/provider metadata only; provider selection comes from `origin` |
| `shared` | `worktreeSetup`, `sharedPaths`, `regenerablePaths`, `hooks`, `profiles`, `gitConventions`, `autonomy`, `workHost`, `okfValidate`, `contextBudgets`, `codex` | settings used by more than one local surface or by isolation |
| `specs` | Azure state and placement mappings, `subjects`, `tagCatalog`, `workItemTypes`, `chat`, `artifactLanguage`, `card`, `cardAt` | provider-owned plan lifecycle and proposal conventions |
| `delivery` | `provider` | the delivery front's explicit provider declaration; it chooses no pipeline policy |
| `ops` | `opsRoot`, `router`, `registry` | operations inventory, router and generated registry |
| `proof` | `proofRoot`, `layers`, `measuredRoots`, `proofExclusions`, `ratchetPath` | verification inventory, layers and coverage evidence |

The shared loader discovers the home, parses JSON, derives provider metadata, and classifies the
envelope. It does not interpret a front's values. Each adapter validates and resolves only its own
namespace. `ops`, `proof`, and `git` consume the common boundary directly; they do not import the
specs adapter to obtain shared configuration.

## The `shared.codex` block

`shared.codex` configures `cq codex` (`codex/config.py`): `crossReview` (`auto` · `off`),
`maxUsedPercent` (`{primary: 80, secondary: 90}`), `timeoutSeconds` (`900`), `model` (`gpt-6-astra`)
and the `executor` object. Its keys and their effect are owned by
[codex-pillar.md](../architecture/codex-pillar.md); a leaf of the wrong shape falls back to its
default and is named in the payload's warnings, and `cq config show --effective` lists every leaf.
`delivery.provider` is read by `delivery/config.py`; `specs.artifactLanguage`, `specs.card` and
`specs.cardAt` by `specs/config.py` (the last three may also sit on the `quenching` branch).

## Settings read outside the file

Three things configure the plugin without being keys of the configuration file, and none is a
second home for those keys:

- `.claude/hooks/hooks-config.json` and `hooks-config.local.json` carry the checker's `okfValidate`
  block; `shared.okfValidate` wins key by key (`knowledge/config.py`).
- `~/.config/quenching/projects.json` is the portal's registry of projects (`portal/registry.py`).
- Constants in code: the `git` and `gh` timeouts and the probe's app-server deadline are not keys.

`cq doctor --setup` previews a minimal configuration file from the detected provider and
fronts, and `--write` confirms it. It records the deprecated root `backend` of the detected tracker;
`cq config init` (above) is the seed to use, because it writes `backend: git` and every default.

## The autonomy block

`shared.autonomy` holds five keys whose defaults live in code (`config/autonomy.py`) and reproduce the
behavior before the block existed. A partial block completes leaf by leaf; `cq config show --effective`
lists each leaf with its value and layer.

| Key | Values | Default | Read by |
| --- | --- | --- | --- |
| `runAloneUpTo` | `none` · `low` · `medium` · `high` · `xhigh` | `low` | `/quenching-specs:specs:orchestrate` and the `orchestrator`: the highest `complexity` that runs without `approved` |
| `merge` | `policy` · `never` · `dependencies` · `all` | `policy` | the `orchestrator`: `policy` defers to the epic's dated text, `never` merges nothing, `dependencies` only specs with a dependent, `all` every leaf |
| `maxWorkers` | integer 1-8 | `3` | the `orchestrator`'s parallelism |
| `maxLaunches` | integer ≥ 1 | `40` | `/quenching-specs:specs:autopilot`, when `--max-launches` is absent |
| `livenessMinutes` | integer ≥ 1 | `20` | `/quenching-specs:specs:autopilot`'s liveness stop |

A value of the wrong shape falls back to the leaf default and is named in the `warnings` of the
effective view; it is never applied silently. An explicit flag wins over the key. No value grants a
permission, removes a sandbox or loosens a verifier check: `merge: all` applies only under
`autonomous`, still on green CI and a verifier PASS.

## Limits and checker settings

Four optional keys carry a limit or a checker setting whose default lives in code. An absent key, or a
leaf of the wrong shape, leaves the default and names the ignored value in a warning on stderr; an
explicit flag wins over the key.

| Key | Values | Default | Read by |
| --- | --- | --- | --- |
| `shared.okfValidate` | `{warnAsError: boolean, ignoreGlobs: list of strings}` | `false`, `[]` | `cq knowledge validate`; wins key by key over `.claude/hooks/hooks-config.local.json` and `hooks-config.json` |
| `shared.contextBudgets` | `{main, worker, conductor}`, positive integers | `200000` / `100000` / `150000` | `cq session context` per role; `cq specs estimate --worker-budget` uses `worker` |
| `shared.autonomy.maxLaunches` | integer ≥ 1 | `40` | `/quenching-specs:specs:autopilot` (see the autonomy block); the launch ceiling lives only there |
| `shared.workHost` | `{target, dockerContext, runner, remoteRoot, syncFlags, syncExclude, pullBack, protectedPaths, minFreeGb}` | disabled | `cq config host --plan`; see [work-host.md](work-host.md) |
| `specs.chat` | `{model: string, budgetUsd: number > 0, timeoutSeconds: number > 0}` | `sonnet`, `0.50`, `300` | the portal's `--chat`; `--chat-budget-usd` wins over `budgetUsd` |

The internal timeouts of `git` and `gh` stay in code.

## Provider-derived selection

The provider is derived from the repository's `origin` remote:

- a `github.com` host selects GitHub Issues;
- an Azure DevOps host selects Azure Boards;
- no recognized remote host is an exit-2 refusal, never a silent switch to another provider.

The root `backend` value selects the store: `git` for the `quenching` branch, otherwise a
deprecated tracker backend established from the remote. Unsupported or retired backend values are
refused. Specs are read and written only after that selection succeeds.

<!-- rationale -->

The `specs` namespace does not name a local specs root, archive, or storage branch.
The retired `specsBranch` key is no longer read.

## The store and its credential

<!-- rules -->

Location is data of the repository; the credential is data of the person. The repository file may
say which store the specs live in; it never carries anything that authenticates.

```json
// .agents/quenching.json
{"specs": {"store": {"azure": {"organization": "https://dev.azure.com/<org>", "project": "<project>"},
                     "github": {"repository": "<owner>/<name>"}}}}

// ~/.config/quenching/config.json (user layer)
{"specs": {"credential": {"azure":  {"source": "login", "configDir": "~/.config/azure-<name>"},
                          "github": {"source": "env",   "env": "<VARIABLE_NAME>"}}}}
```

- **Declared wins; nothing declared is the previous behaviour.** A declared Azure pair is returned
  without `az devops configure --list` and without the project-name round trip; a declared GitHub
  repository is returned without `gh repo view` (the open-issue count is then unknown). A bare
  organisation name is normalised to `https://dev.azure.com/<name>`.
- **The repository layer is read raw** from the configuration file, because the merged view hides
  which file a key came from. `specs.credential` there, or any `specs.store` key named like a secret
  (`token`, `pat`, `password`, `secret`, `key`, case-insensitive, any depth), is refused as
  `sp-store-secret`; any other unknown store key as `sp-store-unknown-key`; a wrong shape or value as
  `sp-store-invalid`.
- **Sources** are `login` and `env`. `login` optionally sets `AZURE_CONFIG_DIR` / `GH_CONFIG_DIR` from
  `configDir` (expanded; a path, not a secret). `env` reads the named variable at call time and sets
  `AZURE_DEVOPS_EXT_PAT` / `GH_TOKEN`. Any other source, `keyring` included, is `sp-credential-source`
  (a keyring is reached through the CLI's own login); an unset variable is
  `sp-credential-env-missing`, naming the variable only.
- **The secret travels only in the environment of the one `az`/`gh` subprocess.** It is never put in
  argv, a refusal, a cache file or the config view; `cq specs config --json` prints the declared
  `store` and a `storeRefusal`, never a credential.
- Every refusal is an exit-2 `BackendRefusal` with nothing read or written; the leak gate stays in
  force on every write.

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

<!-- rationale -->

The command result vocabulary remains uniform: `0` means the requested state is valid, `1` means
the command found reportable drift, and `2` means it refused to guess, migrate, or operate without
an unambiguous declaration.

## Migration is diagnostic

The plugin does not rewrite an installed target's file, create a migration command, or choose a
release boundary for this breaking change. To migrate, move each listed root key into the
destination namespace named by `sp-config-unscoped`, then run the owning front's verifier. A
configuration is ready only when the refusal disappears and the front-specific defaults or
required declarations are evaluated normally.

This standard defines the contract for every projection: the Codex projection preserves the same
ownership, refusal payload and no-fallback rule and reads the same configuration file.
