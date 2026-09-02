---
type: standard
title: Install profiles — the front is the unit of alignment
description: A profile declares which of the seven local fronts a repository asks the root align to conduct; provider-owned specs and the security and git pillars remain available axes, and the profile does not alter command files or host invocation behavior
resource: .claude/quenching.json, plugins/quenching/commands/align.md, plugins/quenching/commands/knowledge/**, plugins/quenching/commands/specs/**, plugins/quenching/commands/design/**, plugins/quenching/commands/components/**, plugins/quenching/commands/ops/**, plugins/quenching/commands/proof/**, plugins/quenching/commands/toolchain/**, plugins/quenching/commands/delivery/**, plugins/quenching/commands/security/**, plugins/quenching/commands/git/**
tags: [architecture, install, profiles, fronts, configuration]
timestamp: 2026-09-02
audience: both
authority: current
source: spec 1111 — a fresh Claude Code 2.1.258 session showed no observable profile-controlled context difference, so the profile contract is limited to `/align` conduction scope
maintainer: quenching
---

# Install profiles — the front is the unit of alignment

An install profile is the declaration, in `.claude/quenching.json`, of which entries a repository
asks the root `/align` conductor to consider. It is a planning and conduction scope, not an
installation mechanism: the plugin's command files remain present and their host invocation and
context behavior remain unchanged.

## The seven local fronts and the non-conducted axes

The plugin exposes seven local fronts, one provider-owned specs axis, and two pillars. The profile
uses the same entry names, while `/align` can conduct only the seven local fronts:

| Entry | Commands | Kind |
| --- | --- | --- |
| `knowledge` | `/quenching:knowledge:*` | front |
| `specs` | `/quenching:specs:*` | provider-owned axis |
| `design` | `/quenching:design:*` | front |
| `components` | `/quenching:components:*` | front |
| `ops` | `/quenching:ops:*` | front |
| `proof` | `/quenching:proof:*` | front |
| `toolchain` | `/quenching:toolchain:*` | front |
| `delivery` | `/quenching:delivery:*` | front |
| `security` | `/quenching:security:*` | pillar |
| `git` | `/quenching:git:*` | pillar |

`specs` has no local tree, and `security` and `git` have no conductor row. Their commands remain
available through their own namespaces regardless of the local-front scope.

## The declaration

A profile is a `shared.profiles.installed` list in the repository envelope:

```json
{
  "backend": "github",
  "shared": {
    "profiles": {
      "installed": ["knowledge", "specs", "components"]
    }
  }
}
```

An absent profile means that all seven local fronts are eligible for `/align`, which is the
default behavior. A declared list names the entries the conductor may run; malformed values belong
to the configuration doctor's findings and never become a silent partial scope.

## What `/align` does with a profile

Before probing, `/align` reads `cq specs config --json`. If `shared.profiles.installed` is absent,
it considers all seven local fronts. If it is present, it conducts only the named local fronts in
the declared dependency order and reports each other local front as skipped by profile. The
provider-owned axis and pillars are not rows in this conductor and are not silently invoked.

The profile does not remove, shorten, hide or rewrite a command. A human who knows a command name
can still invoke it, and a direct front command keeps its own contract. The profile changes only
which local align stages the root conductor considers in this run.

## Boundary

The host's command-registration and context rules are outside this repository's profile contract.
Do not infer a residency, invocation or context effect from a profile entry. If the host exposes a
future supported mechanism, it needs its own measured spec and explicit adapter; this standard
remains valid without it.

Declaring all seven local fronts installed — the profile of this repository when one is needed —
keeps the conductor's default behavior. Omitting the profile is the ordinary equivalent and avoids
duplicating that declaration.
