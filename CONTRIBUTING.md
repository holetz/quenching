# Contributing

## Opening an issue

Open an ordinary issue with the **Bug report** or **Feature request** template. You do not need to
write a spec.

Specs are different: they are created by the tool (`/quenching:specs:create`), carry a structured
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

Durable knowledge lives in [docs/index.md](docs/index.md); the product manual is
[plugins/quenching/README.md](plugins/quenching/README.md).
