---
type: decision
title: The fronts are arguments of the align skill, and their routers are retired
description: Why seven front routers left the listing, the align conducts every front with the front as its argument, and each front's text became references published by its module
resource: quenching/skills/quenching-align/SKILL.md, quenching/references/**, quenching/assets/modules.json, quenching/assets/bin/quenching/deploy/tree.py, quenching/assets/bin/quenching/common/modules.py
tags: [decision, architecture, skills, align, deploy]
timestamp: 2026-11-27
audience: both
authority: current
source: spec 676
maintainer: quenching
---

# 0023 — The fronts are arguments of the align skill

## Context

- [ADR 0019](0019-router-skills-and-target-dialect-source.md) gave each vertical or front a router
  skill. The design, ops, proof, toolchain, delivery, security and opensource routers each carried
  only `align` and `status` plus a minor flow, yet each one's description sat in every session's
  listing.
- The align already conducts all the fronts in dependency order; a front's own align was a second
  door to the same work.

## Decision

- `/quenching-align [front]` converges every front, or only the named one. `/quenching-align status
  [front]` reads one front or all, and ends on the security audit.
- The seven front routers are removed. Their text moved to `quenching/references/<front>-align/`,
  and each front's module still publishes it (`generatedSupport.references`), so a target that
  selects only that module still receives only its own text.
- `knowledge` and `components` stay routers for their other flows; their `align`, `status` and
  `harness-align` rows moved to the align skill (`/quenching-align components`).
- The retired routes answer with a hint to the new one (`RETIRED_ROUTES`), and a module's own
  name resolves as a namespace head even with no skill.

## Consequences

- The resident listing drops from 13 to 6 descriptions.
- Every `/quenching-<front> align|status` citation became `/quenching-align <front>` or
  `/quenching-align status <front>`.

## Grant

The `allowed-tools` of `quenching-align` is the union of the grants the retired routes already held
for their align and status flows, and nothing else:

| Tool | Held before by |
| --- | --- |
| `Bash` (unrestricted) | the knowledge `align` and `harness-align` flows |
| `Read`, `Grep`, `Glob` | every router and flow |
| `Write`, `Edit` | the ops, proof, toolchain, delivery, opensource, knowledge and components aligns |
| `Task` | the knowledge `align`, the components `align` and `harness-align` flows |
| `Skill` | the previous `quenching-align` and the knowledge `align` flow |
| `AskUserQuestion` | the design, ops, proof, toolchain, delivery, opensource, knowledge and components aligns |

The security audit that ends `status` needs no tool of its own: `security_read` runs under the
`Bash(cq:*)` the security router held, which the unrestricted `Bash` includes.

## Verification ruler

No probe or selector rule was dropped. The functional probes for the ops and proof fronts now call
`/quenching-align status ops` and `/quenching-align status proof`, and each
`scripts/toolchain/affected.py` rule that watched the skill folder of a retired front router
folder watches `quenching/references/<front>-align/` and selects the same tests.

## Supersession

Supersedes in part [ADR 0019](0019-router-skills-and-target-dialect-source.md): the rule that every
front has its own router skill. The rest of 0019 stands.
