# quenching

A command surface for teams that build with AI agents: it keeps a repository's knowledge,
specs and version-control workflow in one canonical, verifiable shape. It is not a security
boundary: a command declared read-only does not contain an assistant that has a shell.

quenching reaches a repository only through `cq deploy`, which installs the surface into that
repository for Claude Code, Codex and OpenCode
([ADR 0017](docs/decisions/0017-install-only-by-deploy.md)). The single editable source lives in
[`plugins/quenching/`](plugins/quenching/). Two plugins that install into no repository sit beside
it: the Claude Code band [`plugins/claude/quenching-hud/`](plugins/claude/quenching-hud/) (the only
entry of this repository's Claude marketplace) and the OpenCode Desktop Specs panel
[`plugins/opencode/quenching-vitrine/`](plugins/opencode/quenching-vitrine/).

**Core fronts** — maintained actively, with reliability, adoption and cost as priorities:
`knowledge`, `specs`, `git` and `components`. **Non-core fronts** — `design`, `ops`, `proof`,
`toolchain`, `delivery` and `security`: they stay in the surface under the same names, are
human-only (`disable-model-invocation: true`) and receive reduced maintenance, meaning defect fixes
but no new features. Type the command name to use one.

Release history is maintained in the [`CHANGELOG`](CHANGELOG.md).

The `CI` workflow (`.github/workflows/ci.yml`) runs on pushes to `main` and on pull requests. It installs the locked
toolchain, runs the repository gate on Python 3.11 and 3.13, lints with ruff and reports the functional checks (exit 2 is inconclusive).

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
artifacts in `site/` and `.cache/` stay out of Git. The site payload deploy carries into a target
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

Try it first in a disposable repository. This repository publishes from the
single **`main`** branch ([`docs/standards/git/branching.md`](docs/standards/git/branching.md)); a
deliberate release creates the tag, so install from a tag rather than an in-progress checkout.

From a clone of this repository, deploy the surface into the target:

```bash
python3 plugins/quenching/assets/bin/cq deploy --target <repo> --write
```

Or, with no clone, through `uvx` (the target needs Python 3.11+ and does not need Node):

```bash
uvx --from "git+https://github.com/holetz/quenching@<tag>#subdirectory=plugins/quenching" \
  cq deploy --target . --modules core --write
```

`<tag>` is a release tag such as `7.0.0` (list them with
`git ls-remote --tags https://github.com/holetz/quenching`); a literal `<tag>` fails with
`Git operation failed`. To upgrade an installed target, drop `--modules`: the recorded manifest
keeps its modules, while `--modules core` narrows a wider install and deletes the rest.

`--modules` takes `core` (the default: specs, git, knowledge and components), `all` or a comma
list; `--harness` takes `claude`, `codex`, `opencode` or `none`; `--runtime vendor` (default,
offline) vendors the runtime while `--runtime uvx` writes a pinned shim; `--check` reports drift.
Deploy writes `AGENTS.md` (only when absent), `.agents/skills/`, `.agents/quenching/` and the
generated `.claude/skills/` bridge. It does not create `CLAUDE.md` and does not run alignment; the
target's own `/quenching-knowledge-align` installs `/docs/` and converges the fronts.

In the target, every command is `/quenching-<front>-<verb>` (`/quenching-specs-create`,
`/quenching-knowledge-align`, …), and the target carries its own `.agents/quenching/bin/cq`. To
upgrade, run `cq deploy --target <repo> --write` again from a newer checkout or release tag: the
target's recorded manifest keeps the selected modules, harnesses and runtime. The full contract is
[deploy-mode.md](docs/standards/architecture/deploy-mode.md); the command manual, uninstall and
upgrade notes are in the [plugin README](plugins/quenching/README.md#install).

> **Succession note.** A target that still has the retired `quenching` or `quenching-<module>`
> plugins installed should uninstall them before deploying: they compete with the deployed copy for
> the same command names.

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
