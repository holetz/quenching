# quenching

A **Claude Code plugin** for teams that build with AI agents: it keeps a repository's knowledge,
specs and version-control workflow in one canonical, verifiable shape. It is not a security
boundary: a command declared read-only does not contain an assistant that has a shell.

This repository contains the **plugin marketplace** and the plugin's source. The plugin itself lives in
[`plugins/quenching/`](plugins/quenching/).

**Core fronts** — maintained actively, with reliability, adoption and cost as priorities:
`knowledge`, `specs`, `git` and `components`. **Non-core fronts** — `design`, `ops`, `proof`,
`toolchain`, `delivery` and `security`: they stay in the plugin under the same names, are
human-only (`disable-model-invocation: true`) and receive reduced maintenance, meaning defect fixes
but no new features. Type the command name to use one.

Release history is maintained in the [`CHANGELOG`](CHANGELOG.md).

The Codex sibling lives in [`plugins/quenching-codex/`](plugins/quenching-codex/). Claude remains
the only editable source; refresh the Codex snapshot locally with:

```bash
python3 scripts/sync_codex_plugin.py --write
python3 scripts/sync_codex_plugin.py --check
```

The `CI` workflow (`.github/workflows/ci.yml`) runs on pushes to `main` and on pull requests. It installs the locked
toolchain, runs the repository gate on Python 3.11 and 3.13, lints with ruff and reports the functional checks (exit 2 is inconclusive); it does not write the generated snapshot in CI. Refresh
the Codex artifact locally after changing Claude sources.

## Local development

This checkout declares its toolchain in `pyproject.toml` and pins resolution in `uv.lock`:
the published `cq` requires Python 3.11 or newer.

```bash
uv sync --all-groups
bash scripts/verify_repo.sh
python3 plugins/quenching/assets/bin/cq knowledge site-source docs site-source --write
uv run zensical build --clean --strict
python3 plugins/quenching/assets/checks/documentation-site-check.py site --local --remote-policy error
uv run pytest plugins/quenching/tests -q
```

The root `zensical.toml` is only the configuration of this repository's development site;
artifacts in `site/` and `.cache/` stay out of Git. The payload the plugin installs into a target
project remains in `plugins/quenching/assets/zensical/`.

## What it does

The command surface acts on seven local fronts of a target repository — the `/docs/` OKF bundle
(`knowledge`), the `/.design/` DTCG design source (`design`), the `.claude/` automation surface
(`components`), the declared operations root (`ops`), the declared verification root (`proof`),
the declared toolchain surface (`toolchain`), and the declared delivery surface (`delivery`) —
alongside provider-owned `specs` and the read-only `security` and `git` pillars. Root `/align`
spans the seven local aligned fronts on one confirmation. Every aligned front has exactly one
**align**: probe-first, so a conformant front costs a couple of tool calls and stops. The full
command-by-command manual, the fronts, and the cost model live in the
[plugin README](plugins/quenching/README.md) — this file stays a thin pointer over it rather
than a second, driftable copy.

There is no background write hook in the current artifact. Conformance is evaluated explicitly by
the commands and validators; the disposable experiment records that boundary instead of implying
that a declared read-only command provides shell or Python containment.

The design source is DTCG 2025.10 at `/.design/tokens.json`; `cq design build` emits portable
`PRODUCT.md`/`DESIGN.md`, the Impeccable sidecar, and HTML/Typst adapters. Impeccable is an
optional consumer, and `cq design import` is the explicit route for folding its proposals back.

## Install

The paths below install the packaged Claude plugin. Try it first in a disposable repository.

This repository publishes from the single **`main`** branch
([`docs/standards/git/branching.md`](docs/standards/git/branching.md)). Pull requests merge into
`main`, and a deliberate local release act creates the tag and publishes the accumulated work.
Installing normally therefore gets the repository's default branch, not an arbitrary in-progress
checkout.

Published plugin path: inside Claude Code, add this marketplace and install the plugin:

```text
/plugin marketplace add holetz/claude-quenching
/plugin install quenching@quenching
```

Run `/reload-plugins` after installation when Claude Code was already open.

Local development only (no marketplace publish needed):

```bash
claude --plugin-dir ./plugins/quenching
```

`--plugin-dir` loads the working checkout directly for plugin development and testing; it is not
the normal adoption or upgrade path. A published installation is managed by Claude Code.

Then, inside a target repository, use the `/` menu — every command is
`/quenching:<front>:<verb>` when installed as a plugin (`/quenching:knowledge:align`,
`/quenching:specs:execute`, `/quenching:components:command:new`, …); the bare `/<front>:<verb>`
form only resolves in a repo that vendored the file into its own `.claude/commands/`. The full,
current list — one file per entry point — is the
[plugin README](plugins/quenching/README.md), never duplicated here.

Or add this marketplace and enable the plugin the usual way (see the
[plugin README](plugins/quenching/README.md)).

> **Succession note.** This plugin reuses the marketplace/plugin **name**
> `quenching` as the lean, OKF-centric successor of the 15-dimension
> audit plugin. **Do not enable both at once** (name collision) — this one
> replaces it.

## Cost model

Skill metadata fits Claude Code's 1,536-char per-skill listing cap (trigger phrases in the
second sentence, truncation-safe); skill bodies load only on invocation and shared procedure
lives once in its owning reference file; heavy sweeps fan out to cheaper sub-agents (haiku /
sonnet at low effort) while every classification and destructive gate stays on the session
model; and the enforcement hook's `Stop` sweep is dirty-gated — a turn that touches no
`docs/**` file costs one stat. Full policy:
[plugin README → Model policy](plugins/quenching/README.md#model-policy).

## License

[MIT](LICENSE) © Israel Holetz.
