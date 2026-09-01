---
type: standard
title: Security pillar
description: A read-only pillar that reports workflow permissions, secret and ignore coverage, advisory dependency configuration and access ownership without owning a converged tree
resource: .github/workflows/**, .gitignore, pyproject.toml, .claude/quenching.json, plugins/quenching/commands/security/**, plugins/quenching/assets/bin/quenching/security/**
tags: [architecture, security, pillar, read-only, permissions]
timestamp: 2026-08-31
audience: both
authority: background
source: spec 1071 (task 1.1) — the security subject was classified as pillar-shaped by the axis contract; this declaration fixes its questions and boundary before route implementation
maintainer: quenching
---

# Security pillar

`security` is a read-only pillar. It answers live questions about a target repository's security
posture while the authoritative artifacts remain owned by their respective fronts or by the
target owner. It does not own a canonical tree that this plugin can converge.

## Live questions

The pillar reports one structured result per question. Each result carries a stable question key,
an honest state (`present`, `missing`, `not-measured` or `refused`) and the path or paths that
support it. An empty or unavailable source is evidence about measurement, not permission to invent
a secure value.

| Question | Evidence read | Ownership boundary |
| --- | --- | --- |
| Are workflow and job permissions explicit and bounded? | Provider workflow files and their workflow/job permission declarations | `delivery` owns pipeline shape; the target owner decides whether a permission is safe. |
| Do ignore rules cover the secret classes the repository exposes? | Repository ignore patterns and the secret-bearing paths they cover | The target owns secret policy; the pillar never adds or edits an ignore rule. |
| Is advisory dependency configuration present? | Dependency-advisory or update configuration and the manifests it names | `toolchain` owns dependency declarations; the pillar only reports advisory coverage. |
| Who may touch the relevant security surface? | Access-ownership declarations such as CODEOWNERS or an equivalent provider artifact | The provider and target owner own access policy; the pillar does not grant or revoke access. |

The route may report `not-measured` when a target provider has no comparable static source. It must
preserve the distinction between a source that is absent, a source that cannot be read, and a
source that was read and contains no matching declaration.

## Boundary with fronts

The axis contract in [`align-surface.md`](align-surface.md) distinguishes a front, which owns a
tree with a drift probe and a decisive verifier, from a pillar, which answers live questions
without such a converged tree. Security is therefore not a front: its evidence is distributed
across delivery, toolchain, repository hygiene and provider access controls.

The pillar may read neighbouring evidence but never becomes its writer:

| Surface | Owner | Security relationship |
| --- | --- | --- |
| Workflow triggers, jobs and stages | `delivery` | Read permissions as evidence; do not repair the workflow. |
| Manifests, locks and advisory tooling | `toolchain` | Report advisory coverage; do not change dependency configuration. |
| Shared configuration keys | Shared arbiter-by-key contract | Read ownership declarations; do not add an arbiter row for this pillar. |
| Ignore and secret-handling hygiene | Target repository owner | Report coverage or its absence; never expose secret values. |
| Provider access policy | Provider and target owner | Report the available ownership declaration; never mutate access. |

## Read-only surface

The pillar exposes a normalized `cq security --json` route and one human-facing status/audit body.
The JSON payload contains data only on stdout, with diagnostics on stderr, and uses the plugin's
typed exits: `0` for a conformant or measured result, `1` for reported observations and `2` for
misuse or refusal. The route never writes values, repair files, configuration or generated
artifacts.

The status/audit body presents the route's structured results and names the owner of any action.
It is not a dry-run mode of an align command, and it does not invent a security-specific
convergence plan.

## Deliberate absences

Security has no align route because it owns no tree to converge, no doctor because there is no
security-owned canonical surface to verify, and no bands file because there are no front findings
whose disposition this pillar may classify. It also has no conductor row: the conductor runs
converging fronts, while security is a read-only observation pillar.

These absences are part of the contract. Adding one would falsely turn a live question into a
repair obligation and would let the pillar claim decisions that belong to delivery, toolchain or
the target owner.
