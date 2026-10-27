# Contributing

## Opening an issue

Open an ordinary issue with the **Bug report** or **Feature request** template. You do not need to
write a spec.

Specs are different: they are created by the tool (`/quenching-specs:specs:create`), carry a structured
body that `cq specs` parses, and are labeled `spec`. Do not hand-write one. A maintainer converts an
accepted issue into a spec. To see only human issues, search `-label:spec`.

## Changing the repository

- Artifacts in this repository are written in English (see
  [the communication standard](docs/standards/agents/communication.md)).
- Command bodies and references are executable prose; treat edits to them like code.
- Run the single gate from the repository root before opening a pull request:

```bash
bash scripts/verify_repo.sh
```

### The leak hooks

`scripts/githooks/` carries a `pre-commit` and a `pre-push` hook that run `cq security leak`: they
refuse a commit or a push that carries a CPF, a CNPJ, a Databricks host, token or cluster id, a
private key or an absolute path under your home directory. Point
git at them once per checkout:

```bash
git config core.hooksPath scripts/githooks
```

The hooks run the generic patterns only (`--generic-only`), like the repository gate
(`cq security leak --all --generic-only`) and CI. There is no private denylist: a list of
organization-specific terms kept next to the repository would itself be the trace it should prevent,
so it was retired on 2026-10-27, and keeping those terms out is a review duty on every change. A finding is fixed
by removing the content, never by weakening a pattern or passing `--no-verify`.

Durable knowledge lives in [docs/index.md](docs/index.md); the product manual is
[plugins/quenching/README.md](plugins/quenching/README.md).
