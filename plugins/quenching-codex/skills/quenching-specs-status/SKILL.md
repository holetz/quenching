---
name: quenching-specs-status
description: "Read the provider-owned specs front without writing. Use for specs status, front state, or provider configuration; never for fixing, migrating, or building a spec."
---

<!-- GENERATED FROM plugins/quenching/commands/specs/status.md -->


# quenching-specs-status — read the provider-owned front

**Input**: `$ARGUMENTS` — optionally one spec slug.

Reports the specs front without writing. The canonical documents live in the repository provider:
GitHub Issues or Azure Boards. There is no local `/.specs/` root to scaffold, align or migrate.

## Workflow

1. Resolve `cq` through the repository's declared tool-resolution rule.
2. With a slug, run `cq specs status --spec <slug> --json`; without one, run `cq specs list --json`.
   The command's payload is the source of the stage, records, task progress and provider locator.
3. Run `cq specs config --json` when the report needs to explain provider selection. A missing or
   unrecognised provider is a refusal, never a fallback to local files.
4. Report the tool's JSON and exit code. Do not enumerate local folders, infer a filesystem root,
   or re-render provider data into a second source of truth.

## Invariants

- Never write, scaffold, align, migrate or repair anything.
- Never treat an absent local `/.specs/` directory as a finding; external backends do not use it.
- Never call `FilesBackend`, infer `backend: files`, or offer a local fallback.
- Use `quenching-specs-develop`, `quenching-specs-execute`, or `quenching-specs-conclude` for
  lifecycle work on one named provider-owned spec.
