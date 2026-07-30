---
description: Force a repo's specs/ workspace into the canonical shape — probe first, so a clean one costs two tool calls. Triggers on "align specs", "set up the specs workspace", "install the spec front", "migrate openspec", "fix the specs folder", "is my specs workspace conformant", "scaffold specs". Scaffolds when absent, installs specs.py and the operator manual, folds an older backlog/ plus ready/ layout or a v1 three-file one into plans/, normalizes filenames and slugs, stamps missing frontmatter, and regenerates the listing zone. One plan, one OK, with code-coupled renames gating individually. Authoring and cycle actions are reported with the command that closes each, never performed. Not for: creating a spec → /specs:create; building one → /specs:execute; ranking the front → /specs:triage; the read-only view of what is here → /specs:status.
argument-hint: [optional-scope]
allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(py:*), Bash(mkdir:*), Bash(cp:*), Bash(mv:*), Bash(git mv:*), Bash(rm:*), Write, Edit, Task
---

# /specs:align — force the `specs/` workspace into shape

**Input**: `$ARGUMENTS` (optionally a `specs/` path or a scope; omit to align the whole workspace).

One of the plugin's three aligns. Where `/docs:align` converges a repo's `docs/` bundle and
`/skill:align` its `.claude/` command surface, this one converges its **spec-driven workspace** —
so every repo that adopts the plugin carries the same `specs/` too. Quenching-native: this front is
**entirely plugin-owned** — no external CLI, no Node runtime, no `config.yaml`, no separate spec
store, no delta format. It is what installs the front (there is no `init` step — scaffolding is an
asset copy) and what keeps it conformant.

**It probes before it inventories.** Two tool calls decide whether there is any work at all, and a
conformant workspace ends the run there. That is what makes this safe to run habitually rather than
only when something is already broken.

The facts it works against live once and are cited, never restated — the `specs/` layout, the
fourteen canonical sections, the derived stages and the `specs.py` surface in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md);
the listing-zone format and on-write check in
[specs-create/plans-zone.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-create/plans-zone.md).
The contract **this** command owns — the probe, the canonical workspace, every finding code, which
findings it fixes versus only reports, and the migrations — is
[specs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md).
Do not restate its code table; keep this body aligned to it.

## Doctrine

The sweep contract every align shares — probe before the inventory, convergence over
accommodation, one plan → one OK with code-coupled items gating individually, the cycle-authorized
narration exception, the two-scan blast-radius procedure, MERGE-never-clobber,
never-delete-on-a-guess, and align-conformance-report-the-cycle — lives once in
[align/sweep-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/sweep-doctrine.md).
Read it as this command's doctrine. What follows is only what is **specific to `specs/`**:

- **This front's probe is `specs.py doctor` + `specs.py validate`.** Both exit 0 with no findings
  → say so and stop, before any inventory
  ([conformance](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md) §The probe).
  `doctor` in particular is the only command that tells an **unmigrated** workspace apart from an
  empty one, so it must run first either way — a scaffold offer on a repo that actually holds
  unmigrated work would be the worst outcome here.
- **The whole front is plugin-owned; there is no ownership line to respect.** Unlike the old
  `openspec/` surface (half of which belonged to an external CLI), the sweep may align every part
  of `specs/` — scaffold, rename, seed, stamp, regenerate — bounded only by never-delete-on-a-guess
  and code-coupled-renames-gate-individually. But repairs still come from the tool's own
  **declared** remedy, never an invented one: an invented fix can silently corrupt a spec.
- **The archive is history, and that is stronger than any naming rule.** `specs/archive/**` holds
  v1 three-file plan folders that are **deliberately never migrated**; they are never flagged,
  renamed, or rewritten, and no `sp-bad-filename` fires inside them. A date comes from frontmatter
  or the path's first commit, never from filesystem mtime, which a checkout rewrites.
- **Migrations are one-way, and `specs.py migrate` owns both folds.** A legacy `openspec/`
  workspace folds into `specs/` first (interop with the external CLI is **lost** — say so before
  applying); then `specs.py migrate` folds `backlog/` + `ready/` into `plans/` and any v1
  three-file folder into one file. Never hand-fold either.
- **A diverged shadow copy is kept.** A legacy `openspec init` generated local
  `.claude/skills/openspec-*` copies of commands this plugin ships; identical ones are removal
  candidates, but one a repo has customized (`sp-shadow-diverged`) is kept and reported — the
  general never-delete-on-a-guess rule, applied to the one `.claude/` surface this sweep may touch,
  and only during a legacy migration.
- **Authoring is reported, never supplied.** A present-but-empty heading (`sp-empty-section`), a
  missing gate section, a stray heading: all are **content**, and writing even `- none — <reason>`
  would be authoring an answer only the human can give. They join the cycle findings in
  [conformance](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md) §Findings the
  sweep REPORTS — a complete spec awaiting close-out, a blocked one, a stale one. Never archive,
  never author, never abandon, never rank.

## Workflow (probe → force-with-1-confirmation)

### 1. Probe — the two calls that decide whether anything else runs
Resolve `specs.py` by the fallback in
[specs-create/plans-zone.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-create/plans-zone.md)
§Resolving the tool, invoked via `python3` or `py`. Resolve the `specs/` root at the repo root,
then:
```bash
specs.py doctor --json
specs.py validate --json
```
Branch exactly as
[conformance](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md) §The probe
prescribes: **both clean → report "`specs/` conformant, N specs, nothing to align" and STOP**;
clean but for REPORTS-table codes → stop the same way and list them with the command that closes
each; otherwise continue to step 2.

Neither `specs/` nor a legacy `openspec/` exists → `sp-no-workspace`, which is not a failure: it is
what step 4 offers to scaffold.

**The installed copy is a third question, and one call answers it:**
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/assets/bin/skills.py" drift --json
```
Read this front's row (`specs.py`) and carry it into step 5's scaffold section: `behind` → offer
the overwrite; `absent` → offer the install; `ahead` → **left alone and reported**, because the
target being ahead of this plugin is a fact to state, not a regression to force. Run it from the
**plugin path** — an installed copy answers from the same stale `VERSION` it is being asked about,
and refuses (exit 2) rather than lie. A drift row does **not** by itself make an otherwise-clean
workspace non-conformant: report it with the install offer and stop as prescribed above.
**Done when:** the two payloads are in hand and the run has either stopped or been committed to a
full sweep.

### 2. Inventory (read-only)
Only now, and writing nothing: `specs.py list --json` (slugs, folders, derived stages, task
progress); `Glob` `specs/plans/*.md` and read `plans/index.md`; `Glob` a legacy `openspec/` tree
(to detect `sp-legacy-workspace`) and read it if present; `Glob`
`.claude/skills/openspec-*/SKILL.md` and `.claude/commands/opsx/*.md` (shadow copies, relevant only
under a legacy migration); read `docs/index.md` for `okf_version`.

**`validate --json` from the probe already covers every spec**, so there is no per-spec fan-out to
plan and no reason to re-run it. Reach for `specs.py status --spec <slug> --json` only when a
specific spec's gates must be shown to the human in the plan — never once per spec by default.

**Supplied inventory (handoff).** When a conductor passes one, take it as given and re-collect only
what the handoff does not carry: nothing has written to disk in between, so re-reading returns the
same bytes at full cost.
**Done when:** every source above is in hand (collected or supplied) and nothing has changed.

### 3. Classify every finding
Map the inventory onto the codes in
[specs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md),
splitting the two tables: what the sweep **fixes** (structure, the migrations, filenames and slugs,
frontmatter stamps, the `plans/` listing, shadow copies) and what it only **reports**.
**`sp-v2-layout` and `sp-v1-leftover` are classified before anything else** — until the fold runs,
every other reading of the workspace is about files that are not where they will be. A legacy
`openspec/` fold requires an OKF bundle for its main-spec cut: if `docs/index.md` with
`okf_version` is absent, that fold **stops** and this command suggests `/docs:align` first. For a
shadow copy, diff it against the plugin's command of the same name before classifying: identical →
removal candidate, divergent → `sp-shadow-diverged`, keep-and-report.
**Done when:** every finding carries a code and lands in exactly one table.

### 4. Sweep the blast radius of every rename
Run the shared procedure in
[align/sweep-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/sweep-doctrine.md)
§The blast-radius sweep — two repo scans total for the whole set, never two per rename — over every planned
filename change and every `sp-duplicate-slug` rename. **This front's delta:** a **slug** leaks
further than any other name the plugin renames, because identity here *is* the slug — every
command, cross-reference, branch name, PR title, CI job and script argument names it, and no phase
move ever renames the file, so the slug outlives the whole lifecycle. Treat a slug rename as always
worth the scan even when the file looks internal.
**Done when:** each planned rename is marked coupled or free, with its hits.

### 5. Present ONE plan → gate
One plan, in sections: scaffold (copy `${CLAUDE_PLUGIN_ROOT}/assets/specs/` into `specs/` when
`sp-no-workspace`, plus install `specs.py` into `.claude/hooks/` and the operator manual
`specs/QUENCHING.md` — install / refresh / leave); **migrations** (the legacy `openspec/` fold with
each main-spec→`docs/standards/` cut shown and interop-lost stated; then the fold, shown as
`specs.py migrate --dry-run`'s own output — every spec's destination, the source of each date, and
every folder that will be **kept** because it still holds a file); tool repairs (each quoting the
tool's own message and remedy); renames (old → canonical, coupled ones marked); frontmatter stamps;
listing work (seed / zone install / zone regeneration / frontmatter stripped); shadow copies to
remove and diverged ones kept-and-reported. Then, separately and explicitly labelled **"reported,
not applied"**, every authoring and cycle finding with the command that closes it. Wait for the
single confirmation; each code-coupled rename awaits its own.
**Done when:** the user has answered; declined → nothing written, run ends.

### 6. Apply exactly what was approved
Copy `assets/specs/` and install `specs.py` if approved; run the legacy fold, then
`specs.py migrate`, if approved — **never hand-fold**, and report every folder the tool kept; apply
each tool-stated repair; rename the confirmed files and update every reference site alongside its
individually confirmed rename; install the operator manual from
`${CLAUDE_PLUGIN_ROOT}/assets/specs/QUENCHING.md` to `specs/QUENCHING.md` under the four-branch
manual-install rule in [/docs:align](${CLAUDE_PLUGIN_ROOT}/commands/docs/align.md) §4 (cited, never
restated — same banner, same version fill, same never-clobber-a-de-bannered-copy branch); stamp the
missing frontmatter keys (MERGE); install the GENERATED markers without touching the fixed prose;
delete the approved shadow copies and any `/opsx:*` wrappers under a legacy migration.
**Done when:** every confirmed row is applied and nothing outside the plan changed.

### 7. Verify, log, report
Re-run the probe's two commands — clean, or the residual message reported verbatim (a REPORTS-table
code is a clean result, not a failure). Regenerate the `plans/index.md` GENERATED zone with
`specs.py plans reindex`, then run `okf-validate.py specs/plans --listing-root` — exit 0, no
`index-broken-link` / `index-orphan`. **Read each checker for what it owns**
([conformance](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md) §What checks the
plans listing): `specs.py validate` for the spec files, the OKF checker for `index.md` alone — a
spec carries no OKF `type:` and pointing the bundle validator at one proves nothing. Then confirm
the one thing neither tool sees: the zone matches disk. The OKF hook is docs-scoped by config, so
it does not fire on `specs/`; this run is the coverage.

This sweep writes nothing into the `docs/` bundle — the `specs/` front records itself, and the
bundle log it used to append to is retired. Report the counts **and** the reported-not-applied
residue, each with the command that closes it.
**Done when:** the probe's re-run state, the counts, and the residue are all reported.

## Invariants to never violate

- Never inventory before the probe, and never continue past a clean probe. A conformant workspace
  ends the run at step 1 — that is the whole reason this command is cheap enough to run habitually.
- Never author a spec's sections — not a `## Problem`, not a missing gate heading, and **not an
  explicit `- none — <reason>`**. A section is content; only filenames, frontmatter keys and the
  `plans/` listing are this sweep's to write. (A legacy fold's main-spec→`docs/standards/` mapping
  is the one authored crossing, and it is human-chosen.)
- Never `promote` a spec, and never propose one — that is `/specs:develop` and `/specs:conclude`.
- Never write a frontmatter record this command does not own. `priority`, `refined`, `approved`,
  `branch`, `reviewed`, `merge` and `outcome` each have exactly one writer, and none of them is a
  sweep.
- Never hand-fold a workspace. `specs.py migrate` is the declared remedy; a hand fold silently
  drops sections and invents birth dates.
- Never touch `specs/archive/**` — not its v1 plan folders, not their names, not their contents.
- Never write anything before the plan's OK; a code-coupled rename never rides the batch. A
  cycle-authorized run replaces only the batch gate with narration — never a code-coupled item's
  own OK.
- Never derive a spec's date from filesystem mtime while a truer source exists — frontmatter, then
  the path's first commit; otherwise report and leave the name alone.
- Never delete a **diverged** shadow copy, and never touch any `.claude/` skill or command outside
  `openspec-*` / `opsx/` under a legacy migration — that surface is `/skill:align`'s.
- Never hand-edit inside the `plans/index.md` GENERATED markers, never add frontmatter to
  `plans/index.md`, and never leave the zone stale.
- Never stamp an OKF `type:` on a spec file to quiet the bundle validator — the checker is pointed
  at the listing, not at the specs.
- Never overwrite a `specs/QUENCHING.md` whose `quenching` banner a human removed — keep it and
  report it.
- Never invent a repair the tool did not state.
- Never hand this command file `context: fork` — both gates are mid-flow.
