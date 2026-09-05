---
name: quenching-specs-status
description: "Read the provider-owned specs front without writing. Use when the user asks for \"specs status\", \"the status of the specs front\", or \"provider configuration\". Not for: developing or executing a spec → quenching-specs-develop, quenching-specs-execute; ranking the front → quenching-specs-triage."
---

<!-- GENERATED FROM plugins/quenching/commands/specs/status.md -->


# quenching-specs-status — read the provider-owned front

The canonical documents live in the repository provider: GitHub Issues or Azure Boards. There is no
local `/.specs/` root.

The recognised configuration envelope and its defaults live in
[specs-align/plugin-configuration.md](../../references/specs-align/plugin-configuration.md)
§The envelope and recognised namespaces. This command reports that provider-owned state; it does
not create a local specs store or infer missing configuration.

## Workflow

1. Resolve `cq` through the repository's declared tool-resolution rule.
   **Done when:** the tool path is resolved or refusal is reported.
2. With an ID, run `cq specs status --spec <id> --json`; without one, run `cq specs list --json`.
   The command's payload is the source of the stage, records, task progress and provider locator.
   **Done when:** the requested spec list or record is in hand.
3. Run `cq specs config --json` when the report needs to explain provider selection. A missing or
   unrecognised provider is a refusal, never a fallback to local files. **Done when:** provider
   configuration is reported when needed.
4. Report the tool's JSON and exit code. Do not enumerate local folders, infer a filesystem root,
   or re-render provider data into a second source of truth. **Done when:** the JSON, exit code, and
   refusal/absence state are reported.

## Invariants

- Never write, scaffold, align, migrate or repair anything.
- Never treat an absent local `/.specs/` directory as a finding; external backends do not use it.
- Never call `FilesBackend`, infer `backend: files`, or offer a local fallback.
- Use `quenching-specs-develop`, `quenching-specs-execute`, or `quenching-specs-conclude` for
  lifecycle work on one named provider-owned spec.
