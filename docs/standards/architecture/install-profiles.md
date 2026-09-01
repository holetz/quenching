---
type: standard
title: Install profiles — the front is the unit of installation
description: A profile declares which of the seven local fronts, provider-owned `specs`, and the `security` and `git` pillars a repository uses, in `.claude/quenching.json` — what it turns on and off is the residency of an entry's command descriptions (`disable-model-invocation: true`), never a command or a file; the `/align` conductor runs the installed local fronts in dependency order and names an uninstalled one in its report instead of failing on it, while the pillars carry no conductor to skip at all, only their own residency toggles
resource: .claude/quenching.json, plugins/quenching/commands/align.md, plugins/quenching/commands/knowledge/**, plugins/quenching/commands/specs/**, plugins/quenching/commands/design/**, plugins/quenching/commands/components/**, plugins/quenching/commands/ops/**, plugins/quenching/commands/proof/**, plugins/quenching/commands/toolchain/**, plugins/quenching/commands/delivery/**, plugins/quenching/commands/security/**, plugins/quenching/commands/git/**
tags: [architecture, install, profiles, fronts, configuration]
timestamp: 2026-08-31
audience: both
authority: current
source: extensible-surface-and-budget-retirement plan (task 4.1, 2026-08-06); the `git` pillar, installed by default and carrying no conductor of its own, added by pilar-git-e-specs-agnosticas-ao-git (task 6.3); specs 1067 and 1069 admitted the `toolchain` and `delivery` fronts; spec 1071 established the read-only `security` pillar; varrer-nomes-de-comando-legados (2026-08-27) retired the local specs backend; spec 1072 updates the profile unit and conductor boundary
maintainer: quenching
---

# Install profiles — the front is the unit of installation

An install profile is the declaration, in `.claude/quenching.json`, of which fronts — and the two
pillars, `security` and `git` — a repository uses. What it turns on and off is the **residency** of an entry's
command descriptions: an entry out of the profile is not removed, not shortened, and not made
uninvocable — its commands stay reachable by name and stay citable, and their descriptions simply
stop being carried in every session's always-on context.

## The front is the unit of installation — and two pillars join the same list

The plugin installs seven local fronts, one provider-owned axis, and two pillars, and installation
is decided per entry, never per command:

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

These names are the ones the profile uses. The `components` front is the `.claude/` surface of the
target repository; [align-surface.md](align-surface.md) §The aligned-front column names the same seven
local fronts and the alignless axes from the align side — where the distinction actually bites:
`specs` has no local tree, while `security` and `git` are pillars that earn no row of their own to
conduct.

A profile is the set of entries declared installed:

```json
{
  "backend": "github",
  "profiles": { "installed": ["knowledge", "specs", "design", "components", "ops", "proof", "toolchain", "delivery", "security", "git"] }
}
```

The block lives in the file that already carries the plugin's other declarations, and holds the
same place in the recognised set as any other key
([plugin-configuration.md](../workflows/plugin-configuration.md) §The recognised keys). Absent, it
declares nothing and nothing changes: behaviour with no profile is behaviour with all declared entries
installed. That is the ordinary case, and it is why `installed` lists what is **on** rather than
what is off — the current behaviour is the default, and a profile is an explicit declaration over
it. **The pillars default on the same way** — they are not local fronts a repository opts into,
they are the plugin's read-only procedures, resident unless a profile says otherwise.

## What a profile turns on and off

A profile turns **residency** on and off — never a command, never a file. The mechanism is the
field `disable-model-invocation: true`, which removes a command's description from always-on
context entirely while the command stays invocable by name and keeps its description at full
length ([../automation/skills.md](../automation/skills.md) §The admission criterion).

A front in `installed` keeps its descriptions resident — that is what makes the front usable by
spoken routing. A front out of it has every command carry the field: nothing in a session's
context reaches its commands, and a human who knows a name still types it. The profile changes the
one thing the field changes — residency — and nothing else.

**The profile is not a removal.** The alternative — uninstalling a front by deleting its commands —
is simpler to measure and worse to operate: a command that is gone cannot be cited by name by the
aligns, and cannot be typed by a human who knows it. The field keeps both, which is why the
profile is a residency decision and why `/align` can still name a front that is out of it.

## What `/align` does with an uninstalled front

`/align` conducts the installed local **fronts** in dependency order, on one nested OK per run
([align-surface.md](align-surface.md) §The aligned-front column). With a profile, it conducts **the
installed ones** — in the same dependency order — and an uninstalled front is named in the report
and skipped. It is never an error, and it is never a question.

- The conductor does not invoke the uninstalled front's align, and does not ask whether to.
- The report names the front and why it was not conducted — one line, once per run. The report is
  the align's only account of its own run
  ([align-surface.md](align-surface.md) §No sweep records itself), so the mention lives there,
  never in the bundle.
- Declaring all seven local fronts installed — the profile of this repository itself — changes nothing:
  the conductor behaves exactly as it did before the profile existed.

Why the conductor must not fail: an uninstalled front is a legitimate configuration, not a defect.
The assumption a profile exists to retire is that a repository has all seven local fronts or something
is wrong — and a conductor that refused on the retired assumption would make the profile unusable
for the one case it exists to serve.

**The pillars have no conductor to skip, and turning them off skips nothing.** They earn no row in
the align column at all ([align-surface.md](align-surface.md) §The security subject is pillar-shaped
and §The git pillar has no align), so there is no align invocation for `/align` to withhold and no
"not conducted" line to report — an uninstalled pillar is purely a residency fact, read the same way any other command's
`disable-model-invocation: true` is read, with no conductor-side behavior riding on it.
