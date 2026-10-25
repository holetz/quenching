# quenching-omnigent (generated)

This Omnigent distribution is generated from `plugins/quenching/`, the only editable source. Run
`python3 scripts/sync_omnigent_plugin.py --write` to refresh it; never edit it by hand.

It carries 61 command bundles and 7 agent bundles (`agents/<id>/config.yaml` plus
`instructions.md`) and the payload they cite (`quenching/`, including the bundled `cq`). Pinned
Omnigent version: `v0.19.1` (server image `omnigent-server:v0.19.1`).

## Install

```bash
mkdir -p ~/.omnigent/quenching
cp -R quenching/. ~/.omnigent/quenching/
omnigent run --agent agents/quenching-git-commit --harness <harness> --model <model> -p "<prompt>"
```

Prose paths assume `~/.omnigent/quenching`; `cq` honours `QUENCHING_OMNIGENT_ROOT` for another root. Bundles pin
no model: `--harness` and `--model` choose the runtime.

## Permissions

Each bundle carries one deny-only policy; see `PERMISSIONS.md` for what each denies and what Omnigent
cannot express. See `MODEL-COMPAT.md` for the models measured on the quenching commands.
