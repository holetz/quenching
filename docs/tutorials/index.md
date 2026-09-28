# Getting started

You learn quenching by running it — and the first run is deliberately safe: every front opens
with a read-only probe, so nothing changes until you say so. That loop — probe, one plan, one
OK, apply, verify — is the plugin's entire interface, and the tutorial below teaches it the
honest way: by making you watch it refuse to act on a clean repository.

## Tutorials

- [Getting started](getting-started.md) — install the plugin, verify the CLI answers, probe a
  repository read-only, and run your first alignment. **~10 min** (estimated from its 4 steps,
  excluding your repo's own alignment time).
- [First workflow study](first-workflow-study.md) — run one disposable, deterministic
  status/check/write/check experiment and inspect its evidence boundary. **~5 min**.

What you leave with: a loaded plugin, a `cq` that answers, and the one mental model every other
command reuses — so the [how-to guides](../how-to/index.md) read as variations on a loop you
have already run.

**Already know the basics?** Jump to the [how-to guides](../how-to/index.md); the model behind
the commands is in [Concepts](../explanation/index.md).
