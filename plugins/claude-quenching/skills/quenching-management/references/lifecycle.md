# Lifecycle — install receipt, reconcile/upgrade, consent modes, rollout channels

> **Way back:** [../SKILL.md](../SKILL.md) (agent roadmap) ·
> [README.md](README.md) (`references/` index) ·
> installation mechanics: [installation.md](installation.md).

Installing once (Steps 1-7) leaves the target with **copies** of the package's
payloads — and copies drift: the package evolves here, the target adapts there,
and after a few months nobody can tell an *intentional adaptation* from a
*rotted copy*. This file is the single home of the **conduction layer** that
turns the one-shot install into a **guided, continuously evolving harness**:
the install receipt (manifest), the reconcile/upgrade classes, the consent
modes (`advise` × `managed`) and the distribution channels (stamped copy ×
plugin rollout).

## 1. Install receipt — the manifest

Every install/upgrade (Steps 5/7) **records what it did** in a manifest at the
target: `.claude/quenching-manifest.json` (template:
[../assets/templates/claude/quenching-manifest.json](../assets/templates/claude/quenching-manifest.json)).
One entry per installed artifact:

```json
{
  "method": "claude-quenching",
  "methodVersion": "<package version at install time>",
  "mode": "advise",
  "channel": "stamp",
  "updatedAt": "<ISO date>",
  "artifacts": [
    {
      "id": "hooks/protect-generated.py",
      "version": "<package version that stamped it>",
      "dest": ".claude/hooks/protect-generated.py",
      "adaptations": ["renamed <x>→<y>", "prefix=arq", "docsDir=docs"]
    }
  ]
}
```

- **`id`** — the payload's path **inside the package** (`assets/…`-relative):
  the stable join key between target copy and package source.
- **`version`** — the package version that stamped this artifact (the package
  version lives in the plugin manifest, `plugin.json` → `version`). This is
  what makes upgrade detection **evidence, not diffing heuristics**.
- **`dest` + `adaptations`** — where it landed and what was deliberately
  changed (rename, path repoint, config values). Adaptations are
  **re-applied on upgrade** — they are the target's convention, which wins.
  (Translating an `audience: agent`/`both` payload is **not** an adaptation — the
  agent-facing surface stays English; see §2.)
- **`mode` / `channel`** — see §3 and §4.

Doctrine:

- The manifest is **structure/method metadata, not content** — writing it is
  part of the approved install item, not a separate consent.
- **Missing manifest + quenching artifacts present** = *untracked install*
  (smell): Step 1 detects it and the report proposes **backfilling** the
  manifest from evidence (which payloads are recognizably the package's) as a
  P2 item before any upgrade is offered. A backfilled entry records
  **`version: "unknown"`** — the version that stamped a bare copy is
  unknowable — which §2 treats as **Upgradable** (a pre-manifest copy cannot be
  proven current, so it rejoins the upgrade path instead of masquerading as
  Current).
- Step 1 **reads the manifest first** when present: it is the cheapest derived
  shape (what is installed, at which version, in which mode) and the input to
  §2.

## 2. Reconcile — the upgrade path

The re-audit (Step 8, trigger 3 — payload
[../assets/commands/quenching-reaudit/](../assets/commands/quenching-reaudit/SKILL.md))
gains a **reconcile scope**: with the manifest present, it classifies **every
entry** by comparing manifest × target disk × package:

| Class | Evidence | Action |
| --- | --- | --- |
| **Current** | `version` == package version · `dest` exists · wiring intact | none |
| **Upgradable** | package version > entry `version`, **or** entry `version` is `"unknown"` (backfilled untracked install — cannot be proven Current) | apply the package's new artifact to `dest`, **re-applying recorded `adaptations`**; bump entry |
| **Adapted** | `dest` diverges from what the recorded version stamped, beyond recorded `adaptations` | surface the unrecorded delta; propose **recording it as an adaptation** (target convention wins) or reverting to package — never silently overwrite |
| **Rotted** | `dest` missing, or hook entry orphan/dangling (8b) | re-install / re-wire from the package |
| **Orphaned** | entry exists, artifact deliberately removed from target | propose removing the entry (and flag if the gap it covered re-opens) |

Rules:

- **Upgrade replaces only what an OK already covered**: the artifact was
  approved item-by-item at install; upgrading it to the package's newer
  version is maintenance of that same consent (see §3 for who confirms).
- **Adaptations always survive.** An upgrade that cannot re-apply a recorded
  adaptation cleanly degrades to a **proposal with the conflict shown** —
  never a silent clobber.
- **A translated agent-facing surface is a migration candidate, not an
  adaptation.** Localized prose/headings in an `audience: agent`/`both` copy (a
  pre-English-rule install) is **not** recorded as an "Adapted" convention that
  wins — it surfaces as a **normalize-to-English** migration item, proposed **with
  OK** (agent-facing English is canonical, like the `docs/` names). Only
  `audience: human` copies may keep the repo's language.
- A **new** payload class (something never installed in this target) is
  **not** an upgrade — it re-enters as a normal Step 4 gap + Step 5 install,
  with its own OK, in any mode.
- A **pre-manifest stale copy** (installed before the receipt existed) rejoins
  the upgrade path through backfill: it enters the manifest with
  `version: "unknown"`, is classified **Upgradable**, and is re-stamped from the
  current package with any detected adaptations re-applied. This is how a copy
  that lagged a later method contract (e.g. an installed authoring skill that
  still teaches a superseded frontmatter vocabulary) is detected and refreshed
  without a per-file version stamp.

## 3. Consent modes — `advise` × `managed`

The operation model has **two modes**, recorded in the manifest (`mode`) and
granted/revoked only by the human:

- **`advise`** (default) — audit-by-default + install-with-confirmation,
  item-by-item. Everything in SKILL.md's operation model, unchanged.
- **`managed`** (explicit opt-in) — a **standing consent** for the maintenance
  loop to **apply, without per-item re-confirmation, the bounded reconcile
  classes of §2 only**: *Upgradable* (re-stamp newer version, adaptations
  re-applied), *Rotted* (re-install/re-wire what was already approved), and
  manifest hygiene (*Orphaned* entry removal after the human removed the
  artifact). Every managed apply is **appended to the audit-trail**
  (`audit-config-change.py` hook — who/when/what) and is git-reversible.

What **never** enters `managed`, in any mode, under any OK:

- **Human direction** — vision (3), memory (10), boundary doctrine (12): a draft
  may be written (labeled `authority: background`, behind the ratification gate),
  but **ratifying** it as authoritative is **never** a standing consent (Step 6,
  the `draft-direction` class below): consent to *maintain structure* is never
  consent to *ratify direction*.
- **Deletions/renames of pre-existing target artifacts** — deprecation stays a
  recommendation; removal keeps requiring an explicit OK per item.
- **Generated artifacts** — the `protect-generated` doctrine holds.
- **First install of a new payload** — standing consent covers what was
  granted, never grows silently. New capability = new report item = new OK.

The **grant** itself is an explicit item: the report proposes `managed` only
when the loop is already installed and at least one reconcile cycle ran clean
in `advise`; the human flips `mode` (or asks the method to, as a confirmed
item). **Revoking is one edit** (`mode: "advise"`) and the loop honors it on
the next run. Hooks keep their contract in both modes: they **observe/propose,
never mutate** — even in `managed`, the applying link is the re-audit
command/skill run, not a hook.

### Generation consent classes — derived content × direction drafts

Two apply regimes beyond structure carry their own bounded consent
([module-contract.md](module-contract.md) part 3), distinct from `advise`/`managed`:

- **`generate-derived`** — an **explicit, enumerated grant** to WRITE derived
  standards content (dim 2) into **absent/empty** subjects: the report lists each
  subject to fill **with its `file:line` anchor**, and — per subject — the
  **candidate sub-standards** to generate (each anchored) vs. **defer**; **one OK**
  authorizes generating them all. Additive, git-reversible, under the anti-fabrication rail
  (`current` anchored; unproven → `authority: background`) + **mandatory adversarial
  review**. Closest to "first install of new content" → it **does not auto-enter
  `managed`** (granted per audit). Writes that modify an **existing authored body**
  are excluded — those stay **per-item OK** (the rename/delete-risk tier).
  Frontmatter re-stamp + `INDEX.md` regeneration remain in `managed` (reversible).
- **`draft-direction`** — the human-direction dims (3/10/12) may be **drafted and
  written**, but only as a labeled `authority: background` draft behind a **human
  ratification gate**. This class **never** enters `managed` and is **never**
  covered by a `generate-derived` bulk grant: direction is not derivable, so the
  human ratifies each draft before it becomes authoritative.

## 4. Distribution channels — stamped copy × plugin rollout

The manifest's `channel` records how payloads reach this target:

- **`stamp`** (default) — Steps 5/7 copy from `assets/`, adapt to the derived
  shape, record in the manifest. Fully per-target: names, paths and language
  converge to the repo's conventions. Cost: upgrades are per-repo reconcile
  runs (§2).
- **`plugin`** (org rollout) — when the profile signal is *several repos/teams
  need the same setup* (monorepo, platform org), the method **proposes
  packaging the approved payload set as an internal plugin + marketplace**
  (scaffold: [../assets/plugin/](../assets/plugin/README.md)). What changes:
  - **Hooks wire themselves**: a plugin's `hooks/hooks.json` registers with
    the plugin — no manual `settings.json` merge per repo (the merge-not-
    clobber procedure of [installation.md](installation.md) remains only for
    `stamp`). Paths use `${CLAUDE_PLUGIN_ROOT}` (install cache), state that
    must survive updates uses `${CLAUDE_PLUGIN_DATA}`.
  - **Upgrades flow by version**: bump `version` in `plugin.json`/marketplace
    entry on every release — consumers only receive updates when it changes —
    and repos refresh via `/plugin marketplace update`.
  - **Repos pre-configure adoption**: `extraKnownMarketplaces` +
    `enabledPlugins` in the repo's `.claude/settings.json` prompt every team
    member to install on folder trust.
  - Trade-off (why `stamp` stays the default): a plugin is **canonical for
    everyone** — no per-target renaming or per-repo adaptation of the payloads it
    carries. Choose `plugin` when uniformity across repos is worth more than
    per-repo fit; the audit/report/consent layers (Steps 1-4, 6, §3) are
    unchanged — only the **delivery** of payloads moves.

Both channels feed the **same manifest**: `plugin` entries record the plugin
version as `version`, so the reconcile table (§2) reads identically.
