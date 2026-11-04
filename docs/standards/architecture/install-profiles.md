---
type: standard
title: Install profiles — the front is the unit of alignment
description: A profile declares which of the eight local fronts a repository asks the root align to conduct; provider-owned specs and the security and git pillars remain available axes, and the profile does not alter skill files or host invocation behavior; the root align conducts the intersection of the profile with the enabled modules, and a module is one vertical or one front with the quenching- prefix
resource: .agents/quenching.json, quenching/assets/modules.json, quenching/assets/bin/quenching/deploy/tree.py, quenching/skills/**, quenching/references/align/tool-resolution.md
tags: [architecture, install, profiles, fronts, configuration]
timestamp: 2026-11-03
audience: both
authority: current
source: spec 1111, spec 1635, spec 1637, spec 2160, spec 2171, spec 2172, spec 2174; lineage in ADR 0017 and ADR 0019
maintainer: quenching
---

# Install profiles — the front is the unit of alignment

<!-- rules -->

An install profile is the declaration, in `.agents/quenching.json`, of which entries a repository
asks the root `quenching-align` conductor to consider. It is a planning and conduction scope, not an
installation mechanism: the skills remain present and their host invocation and context behavior
remain unchanged.

## Modules, and the eight local fronts

A module is the unit `cq deploy --modules` installs, and each is named for one vertical or one
front with the `quenching-` prefix ([source-layout.md](source-layout.md),
[command-surface.md](../naming/command-surface.md)). `quenching-specs` is mandatory: it owns the one
`cq` and carries three skills, `quenching-specs`, `quenching-handoff` and `quenching-align` (the
root conductor). `core` is `specs,git,knowledge,components`, the default selection. The historical
module `align` (and `quenching-align`) is an alias for `knowledge,components`, kept so a manifest
recorded before the split still resolves.

The profile uses the same entry names as the fronts, one provider-owned specs axis and two pillars,
while `quenching-align` can conduct only the eight local fronts:

| Entry | Skill | Kind | Module |
| --- | --- | --- | --- |
| `knowledge` | `quenching-knowledge` | front | `quenching-knowledge` |
| `specs` | `quenching-specs` | provider-owned axis | `quenching-specs` |
| `design` | `quenching-design` | front | `quenching-design` |
| `components` | `quenching-components` | front | `quenching-components` |
| `ops` | `quenching-ops` | front | `quenching-ops` |
| `proof` | `quenching-proof` | front | `quenching-proof` |
| `toolchain` | `quenching-toolchain` | front | `quenching-toolchain` |
| `delivery` | `quenching-delivery` | front | `quenching-delivery` |
| `opensource` | `quenching-opensource` | front | `quenching-opensource` |
| `security` | `quenching-security` | pillar | `quenching-security` |
| `git` | `quenching-git` | pillar | `quenching-git` |

`specs` has no local tree, and `security` and `git` have no conductor row. Their skills remain
available through their own names regardless of the local-front scope.

## Profiles intersect with enabled modules

Two independent facts decide whether `quenching-align` runs a local front, and the run takes their
**intersection**:

- **The module is enabled** — the target received the module that owns the front (the table's
  last column) with `cq deploy --modules`. `quenching-align` reads `cq modules --json` once, before
  the first front.
- **The profile names it** — or no profile is declared (§The declaration).

The profile restricts; an absent module removes. A front the profile names but whose module is not
enabled is reported `not-installed: <module>` and skipped, never invoked, and the fronts that
depend on it depend on the nearest earlier front that ran. A front whose module is enabled but the
profile omits is reported skipped by profile. Neither case is an error.

Deploying a module is the installation mechanism; the profile is not. Declaring an entry in
`shared.profiles.installed` never makes its module's skills exist, and enabling a module never
widens a declared profile. The root conductor itself lives in `quenching-specs`: with that module
absent there is no root align to read a profile, and each enabled front is run through its own
skill.

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

An absent profile means that all eight local fronts are eligible for the root align, which is the
default behavior. A declared list names the entries the conductor may run; malformed values belong
to the configuration doctor's findings and never become a silent partial scope.

## What `quenching-align` does with a profile

Before probing, the root align reads `cq specs config --json`. If `shared.profiles.installed` is
absent, it considers all eight local fronts whose module is enabled. If it is present, it conducts
only the named local fronts in the declared dependency order and reports each other local front as
skipped by profile. The provider-owned axis and pillars are not rows in this conductor and are not
silently invoked.

The profile does not remove, shorten, hide or rewrite a skill. A human who knows a skill name can
still invoke it, and a direct front skill keeps its own contract. The profile changes only which
local align stages the root conductor considers in this run.

## Boundary

The host's skill-registration and context rules are outside this repository's profile contract.
Do not infer a residency, invocation or context effect from a profile entry. If the host exposes a
future supported mechanism, it needs its own measured spec and explicit adapter; this standard
remains valid without it.

Declaring all eight local fronts installed — the profile of this repository when one is needed —
keeps the conductor's default behavior. Omitting the profile is the ordinary equivalent and avoids
duplicating that declaration.
