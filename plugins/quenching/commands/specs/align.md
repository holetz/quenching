---
description: Align specs/ to the canonical workspace — scaffold, validate, inbox, shadow copies
argument-hint: [optional-scope]
allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(py:*), Bash, Write, Edit, Task
---

# /specs:align — force the `specs/` workspace into shape

**Input**: `$ARGUMENTS` (optionally a `specs/` path or a scope; omit to align the whole workspace).

The third align. Where `/docs:align` converges a repo's `docs/` bundle and
`/skill:align` its `.claude/` automation surface, this skill converges its
**spec-driven workspace** — so every repo that adopts the plugin carries the same `specs/`
too. Quenching-native: this front is **entirely plugin-owned** — no external CLI, no Node
runtime, no `config.yaml`, no separate spec store, no delta format. It is what installs the
front (there is no `init` step to run — scaffolding is an asset copy) and what keeps it
conformant.

The facts it works against live once and are cited, never restated — the `specs/` layout,
the plan artifact graph, and the `specs.py` tool surface in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md);
the backlog index-zone format and on-write check in
[specs-capture/backlog-zone.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-capture/backlog-zone.md).
The contract **this** skill owns — the canonical workspace, every finding code, which findings
it fixes versus only reports, and the one-way `openspec/`→`specs/` migration — is
[specs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md). Do not restate its code table; keep this
SKILL aligned to it.

## Doctrine

The sweep contract every align shares — convergence over accommodation, one plan → one OK with
code-coupled items gating individually, the cycle-authorized narration exception, the
two-scan blast-radius procedure, MERGE-never-clobber, never-delete-on-a-guess, and
align-conformance-report-the-cycle — lives once in
[align-all/sweep-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align-all/sweep-doctrine.md).
Read it as this skill's doctrine. What follows is only what is **specific to `specs/`**:

- **The whole front is plugin-owned; there is no ownership line to respect.** Unlike the old
  `openspec/` surface (half of which belonged to an external CLI), the sweep may align every
  part of `specs/` — scaffold, rename, seed, stamp, regenerate — bounded only by
  never-delete-on-a-guess and code-coupled-renames-gate-individually. But repairs still come
  from `specs.py doctor`'s own **declared** remedy, never an invented one: an invented fix can
  silently corrupt a plan.
- **The archive is history — and in v2 that is stronger than a naming rule.** `specs/archive/**`
  holds v1 three-file plan folders that are **deliberately never migrated**; they are never
  flagged, renamed, or rewritten, and no `sp-bad-filename` fires inside them. A date comes from
  frontmatter or the path's first commit, never from filesystem mtime, which a checkout rewrites.
- **Two migrations, both one-way, in this order.** A legacy `openspec/` workspace folds into
  `specs/` first ([conformance](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md) §Migrating a legacy `openspec/`
  workspace — interop with the external CLI is **lost**, say so before applying); then a v1
  three-file workspace folds to single files via **`specs.py migrate`**
  ([conformance](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md) §Migrating a v1 workspace). The v1 fold is the tool's
  own declared remedy for `doctor`'s `sp-v1-leftover` — run it, never hand-fold a plan.
- **A v1 workspace reads as EMPTY, not as wrong.** v2 `list` globs the three phase folders, and a
  v1 `specs/<plan>/` tree matches none of them. `doctor` is the only command that detects it, so
  this sweep runs `doctor` **before** concluding anything about what the workspace holds — a
  scaffold offer on a repo that actually holds unmigrated work would be the worst outcome here.
- **A diverged shadow copy is kept.** A legacy `openspec init` generated local
  `.claude/skills/openspec-*` copies of skills this plugin ships; identical ones are removal
  candidates, but one a repo has customized (`sp-shadow-diverged`) is kept and reported — the
  general never-delete-on-a-guess rule, applied to the one `.claude/` surface this sweep may
  touch, and only during a legacy migration.
- **Authoring is reported, never supplied — and v2 widens what that covers.** A present-but-empty
  heading (`sp-empty-section`), a missing gate section, a stray heading: all are **content**, and
  writing even `- none — <reason>` would be authoring an answer only the human can give. They join
  the cycle findings in [conformance](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md) §Findings the sweep REPORTS — a
  complete spec awaiting promote, a blocked one, a stale one. Never promote, never author, never
  abandon.
- **There is no ledger to police.** The backlog task and the spec it seeded are one file now, so
  v1's `sp-ledger-orphan` / `sp-ledger-in-flight` describe nothing and are gone.

## Workflow (force-with-1-confirmation)

### 1. Resolve the tool + workspace, inventory (read-only)
Resolve `specs.py` by the fallback in
[specs-capture/backlog-zone.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-capture/backlog-zone.md)
§Resolving the tool (plugin path `${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py` → the target's
`.claude/hooks/specs.py` → the declared manual check, saying so in the report), invoked via
`python3` or `py`. Resolve the `specs/` root at the repo root. If **neither** `specs/` nor a
legacy `openspec/` exists, that is expected — Step 4 offers to scaffold.
Then collect, writing nothing: **`specs.py doctor` first** (it is the only command that tells a
v1 workspace apart from an empty one), then `specs.py validate --json` and `specs.py list --json`
(slugs, phases, derived stages, task progress); `Glob` `specs/backlog/*.md` + read
`backlog/index.md`; `Glob` a legacy `openspec/` tree (to detect `sp-legacy-workspace`) and read it
if present; `Glob` `.claude/skills/openspec-*/SKILL.md` and `.claude/commands/opsx/*.md` (shadow
copies, relevant only under a legacy migration); read `docs/index.md` for `okf_version`.

**`validate --json` already covers every spec**, so there is no per-spec fan-out to plan: one
invocation returns every finding for the whole workspace, keyed by file. Reach for
`specs.py status --spec <slug> --json` only when a specific spec's gates must be shown to the
human in the plan — never once per spec by default.

**Supplied inventory (handoff).** When the caller passes an inventory —
`/specs:align-and-update` Stage 1 always does, because its Step 2 assessment collected
exactly these sources moments earlier — take it as given and skip the collection above. Nothing
has written to disk between that assessment and this invocation, so re-running `doctor`,
`validate`, and `list --json` returns the same bytes at full cost. Re-collect only what the
handoff does not carry.

**Done when:** every source above is in hand (collected or supplied) and nothing has changed.

### 2. Classify every finding
Map what the inventory holds onto the finding codes in
[specs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md), splitting the two tables: what the sweep
**fixes** (structure incl. `sp-no-workspace`/`sp-v1-workspace`/`sp-legacy-workspace`, filenames
and slugs, frontmatter stamps, the `backlog/` listing, shadow copies) and what it only **reports**
(`sp-empty-section`, `sp-gate-unmet`, `sp-stray-heading`, `sp-handoff-empty`,
`sp-impact-uncovered`, `sp-unrefined`, `sp-no-outcome`, `sp-spec-complete`, `sp-spec-blocked`,
`sp-spec-stale`). **`sp-v1-workspace` is classified before anything else** — until the fold runs,
every other reading of the workspace is about files that are not there yet. A legacy
`openspec/` fold that means folding main specs into `docs/standards/` requires an OKF bundle —
if `docs/index.md` with `okf_version` is absent, that fold **stops** and the skill suggests
`/docs:align` first. For a shadow copy, diff it against the plugin's skill of the same name
before classifying: identical → removal candidate, divergent → `sp-shadow-diverged`,
keep-and-report. **Done when:** every finding carries a code and lands in exactly one table.

### 3. Sweep the blast radius of every rename
Run the shared procedure in
[align-all/sweep-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align-all/sweep-doctrine.md)
§3 — two repo scans total for the whole rename set, never two per rename — over every planned
filename change and every `sp-duplicate-slug` rename. **This front's delta:** a **slug** leaks
further than any other name the plugin renames, because identity in v2 *is* the slug — every
command, cross-reference, branch name, PR title, CI job, and script argument names it, and a
`promote` never renames the file, so the slug outlives every phase move. Treat a slug rename as
always worth the scan even when the file looks internal.
**Done when:** each planned rename is marked coupled or free, with its hits.

### 4. Present ONE plan → gate
One plan, in sections: scaffold (copy `${CLAUDE_PLUGIN_ROOT}/assets/specs/` into `specs/` when
`sp-no-workspace`, plus install `specs.py` into `.claude/hooks/` and the operator manual
`specs/QUENCHING.md` — install / refresh / leave); **migrations** (the legacy `openspec/` fold
with each main-spec→`docs/standards/` cut shown and interop-lost stated; then the v1 fold, shown
as `specs.py migrate --dry-run`'s own output — every spec's destination, the source of each date,
and every plan folder that will be **kept** because it still holds a file); tool repairs (each
quoting `doctor`/`validate`'s own message); renames (old → canonical, coupled ones marked);
frontmatter stamps; backlog listing work (seed / zone install / zone regeneration / frontmatter
stripped); shadow copies to remove and diverged ones kept-and-reported. Then, separately and
explicitly labelled **"reported, not applied"**, every authoring and cycle finding with the
command that closes it. Wait for the single confirmation; each code-coupled rename awaits its own.
**Done when:** the user has answered; declined → nothing written, run ends.

### 5. Apply exactly what was approved
Copy `assets/specs/` and install `specs.py` if approved; run the legacy fold, then
`specs.py migrate`, if approved — **never hand-fold a plan**, and report every folder the tool
kept; apply each tool-stated repair; rename the confirmed files and update every reference site
alongside its individually confirmed rename; seed `specs/backlog/` from
`${CLAUDE_PLUGIN_ROOT}/assets/specs/backlog/index.md` when missing; install the operator manual
from `${CLAUDE_PLUGIN_ROOT}/assets/specs/QUENCHING.md` to `specs/QUENCHING.md` under the
four-branch manual-install rule in
[/docs:align](${CLAUDE_PLUGIN_ROOT}/commands/docs/align.md) §4 (cited, never restated —
same banner, same version fill, same never-clobber-a-de-bannered-copy branch); stamp the missing
frontmatter keys (MERGE); install the GENERATED markers without touching the fixed prose; delete
the approved shadow copies and any `/opsx:*` wrappers under a legacy migration.
**Done when:** every confirmed row is applied and nothing outside the plan changed.

### 6. Verify, log, report
Re-run `specs.py doctor` and `specs.py validate` — clean, or the residual message reported
verbatim (a REPORTS-table code is a clean result, not a failure). Regenerate the
`backlog/index.md` GENERATED zone with `specs.py backlog reindex`, then run
`okf-validate.py specs/backlog --listing-root` — exit 0, no `index-broken-link` / `index-orphan`.
**Read each checker for what it owns** ([conformance](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md) §What checks the
backlog listing): `specs.py validate` for the spec files, the OKF checker for `index.md` alone —
a v2 spec carries no OKF `type:` and pointing the bundle validator at one proves nothing. Then
confirm the one thing neither tool sees: the zone matches disk. The OKF hook is docs-scoped by
config, so it does not fire on `specs/`; this run is the coverage.
In a repo with an OKF bundle, append **one** consolidated entry to `docs/log.md` per
**Appending to `log.md`** in
[docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md):
`**Update**: [specs/](/specs/backlog/index.md) — aligned workspace (N migrated, M renamed,
K shadow copies removed)`. Then report the counts **and** the reported-not-applied residue, each
with the command that closes it. **Done when:** doctor/validate state, counts, and residue are all
reported.

## Invariants to never violate

- Never author a spec's sections — not a `## Problem`, not a missing gate heading, and **not an
  explicit `- none — <reason>`**. A section is content; only filenames, frontmatter keys, and the
  `backlog/` listing are this sweep's to write. (A legacy fold's main-spec→`docs/standards/`
  mapping is the one authored crossing, and it is human-chosen.)
- Never `promote` a spec in any direction, and never propose one — those are the promote flows
  and `/specs:develop`.
- Never hand-fold a v1 plan. `specs.py migrate` is the declared remedy; a hand fold silently
  drops sections and invents birth dates.
- Never touch `specs/archive/**` — not its v1 plan folders, not their names, not their contents.
- Never write anything before the plan's OK; a code-coupled rename never rides the batch. A
  cycle-authorized run replaces only the batch gate with narration — never a code-coupled item's
  own OK.
- Never derive a spec's date from filesystem mtime while a truer source exists — frontmatter, then
  the path's first commit; otherwise report and leave the name alone.
- Never delete a **diverged** shadow copy, and never touch any `.claude/` skill or command
  outside `openspec-*` / `opsx/` under a legacy migration — that surface is
  `/skill:align`'s.
- Never hand-edit inside the `backlog/index.md` GENERATED markers, never add frontmatter to
  `backlog/index.md`, and never leave the zone stale.
- Never stamp an OKF `type:` on a spec file to quiet the bundle validator — the checker is
  pointed at the listing, not at the specs.
- Never overwrite a `specs/QUENCHING.md` whose `quenching` banner a human removed — keep
  it and report it.
- Never invent a repair the tool did not state.
- Never hand this command file `context: fork` — both gates are mid-flow.
