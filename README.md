# quenching

A **Claude Code plugin** that forces any repository's `/docs/` into a single
canonical **[Open Knowledge Format (OKF v0.1)](https://github.com/GoogleCloudPlatform/knowledge-catalog)**
bundle — and keeps it that way. Every repository that adopts it ends up with the
**same rich, greppable knowledge tree** in the same places, so anyone moving
between repos sees one structure.

This repository is a **plugin marketplace**. The plugin itself lives in
[`plugins/quenching/`](plugins/quenching/).

The Codex sibling lives in [`plugins/quenching-codex/`](plugins/quenching-codex/). Claude remains
the only editable source; refresh the Codex snapshot locally with:

```bash
python3 scripts/sync_codex_plugin.py --write
python3 scripts/sync_codex_plugin.py --check
```

The `Sync Codex plugin` workflow runs on pushes and pull requests. It installs the locked
toolchain and runs the repository gate; it does not write the generated snapshot in CI. Refresh
the Codex artifact locally after changing Claude sources.

## Desenvolvimento local

Este checkout já declara o toolchain no `pyproject.toml` e fixa a resolução em `uv.lock`:
o `cq` publicado requer Python 3.11 ou mais recente.

```bash
uv sync --all-groups
bash scripts/verify_repo.sh
python3 plugins/quenching/assets/bin/cq knowledge site-source docs site-source --write
uv run zensical build --clean --strict
python3 plugins/quenching/assets/checks/documentation-site-check.py site --local --remote-policy error
uv run pytest plugins/quenching/tests -q
```

O `zensical.toml` raiz é somente a configuração do site de desenvolvimento deste repositório;
artefatos em `site/` e `.cache/` não entram no Git. O payload que o plugin instala em um projeto
alvo continua em `plugins/quenching/assets/zensical/`.

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

The **`cq knowledge hook`** hook (zero dependencies) keeps future edits
conformant: it validates touched `/docs/**` files against the OKF core on
`Write`/`Edit` and at `Stop`, and can optionally block a non-conformant write.

The design source is DTCG 2025.10 at `/.design/tokens.json`; `cq design build` emits portable
`PRODUCT.md`/`DESIGN.md`, the Impeccable sidecar, and HTML/Typst adapters. Impeccable is an
optional consumer, and `cq design import` is the explicit route for folding its proposals back.

## Install

This repository publishes from the single **`main`** branch
([`docs/standards/git/branching.md`](docs/standards/git/branching.md)). Pull requests merge into
`main`, and a deliberate local release act creates the tag and publishes the accumulated work.
Installing normally therefore gets the repository's default branch, not an arbitrary in-progress
checkout.

Local (no marketplace publish needed):

```bash
claude --plugin-dir ./plugins/quenching
```

Run from a checkout of `main` for the latest published repository state.

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
