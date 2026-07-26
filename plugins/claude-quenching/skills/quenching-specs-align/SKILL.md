---
name: quenching-specs-align
description: >-
  Forces a repository's specs/ workspace into the canonical shape this plugin defines — the
  sweep counterpart of quenching-docs-align.
  Use when the user asks to "align specs", "align the specs workspace", "scaffold specs",
  "make specs conformant", "clean up specs/", "normalize the backlog and the plans", or
  "migrate openspec to specs". Scaffolds specs/ from the plugin's assets, installs specs.py,
  applies doctor/validate's DECLARED remedies, normalizes plan and archive names, seeds and
  stamps the backlog inbox and regenerates its zone, and migrates a legacy openspec/
  workspace one-way. Cycle
  actions are REPORTED, never driven — a complete-but-unarchived plan routes to
  quenching-specs-plan-archive, untriaged tasks to quenching-specs-backlog-triage. ONE plan,
  one confirmation. Not for: aligning
  docs/ → quenching-docs-align; the rest of the .claude surface → quenching-skill-align; all
  three fronts at once → quenching-align-all; driving the cycle actions this one only reports
  → quenching-specs-align-and-update.
when_to_use: >-
  installing and force-aligning a repo's specs/ workspace to the canonical shape in one plan →
  one OK.
allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(py:*), Bash, Write, Edit, Task
user-invocable: false
---

# quenching-specs-align — force the `specs/` workspace into shape

The third align. Where `quenching-docs-align` converges a repo's `docs/` bundle and
`quenching-skill-align` its `.claude/` automation surface, this skill converges its
**spec-driven workspace** — so every repo that adopts the plugin carries the same `specs/`
too. Quenching-native: this front is **entirely plugin-owned** — no external CLI, no Node
runtime, no `config.yaml`, no separate spec store, no delta format. It is what installs the
front (there is no `init` step to run — scaffolding is an asset copy) and what keeps it
conformant.

The facts it works against live once and are cited, never restated — the `specs/` layout,
the plan artifact graph, and the `specs.py` tool surface in
[../quenching-specs-plan-propose/references/spec-driven.md](../quenching-specs-plan-propose/references/spec-driven.md);
the backlog index-zone format and on-write check in
[../quenching-specs-backlog-add/references/backlog-zone.md](../quenching-specs-backlog-add/references/backlog-zone.md).
The contract **this** skill owns — the canonical workspace, every finding code, which findings
it fixes versus only reports, and the one-way `openspec/`→`specs/` migration — is
[references/conformance.md](references/conformance.md). Do not restate its code table; keep this
SKILL aligned to it.

## Doctrine

The sweep contract every align shares — convergence over accommodation, one plan → one OK with
code-coupled items gating individually, the cycle-authorized narration exception, the
two-scan blast-radius procedure, MERGE-never-clobber, never-delete-on-a-guess, and
align-conformance-report-the-cycle — lives once in
[../quenching-align-all/references/sweep-doctrine.md](../quenching-align-all/references/sweep-doctrine.md).
Read it as this skill's doctrine. What follows is only what is **specific to `specs/`**:

- **The whole front is plugin-owned; there is no ownership line to respect.** Unlike the old
  `openspec/` surface (half of which belonged to an external CLI), the sweep may align every
  part of `specs/` — scaffold, rename, seed, stamp, regenerate — bounded only by
  never-delete-on-a-guess and code-coupled-renames-gate-individually. But repairs still come
  from `specs.py doctor`'s own **declared** remedy, never an invented one: an invented fix can
  silently corrupt a plan.
- **The archive is history.** An archived plan folder is never rewritten beyond its name, and a
  plan is never deleted. A folder's date comes from its `.specs.json` `created`, never from
  filesystem mtime, which a checkout rewrites.
- **Legacy migration is one-way.** A legacy `openspec/` workspace folds into `specs/` by the
  procedure in [conformance](references/conformance.md) §Migrating a legacy `openspec/`
  workspace — flatten, fold the main specs into `docs/standards/` by a human-chosen cut, drop
  `config.yaml`, convert `.openspec.yaml`→`.specs.json`, discard the delta folders once folded,
  remove the shadow copies and `/opsx:*` wrappers. Interop with the external OpenSpec CLI is
  **lost** — say so before applying. This is the **only** place `openspec/` is touched.
- **A diverged shadow copy is kept.** A legacy `openspec init` generated local
  `.claude/skills/openspec-*` copies of skills this plugin ships; identical ones are removal
  candidates, but one a repo has customized (`sp-shadow-diverged`) is kept and reported — the
  general never-delete-on-a-guess rule, applied to the one `.claude/` surface this sweep may
  touch, and only during a legacy migration.
- **The cycle findings this front reports** are enumerated in
  [conformance](references/conformance.md) §Findings the sweep REPORTS: a complete-but-unarchived
  plan, a blocked one, a stale one, untriaged tasks, a ledger orphan. Never archive, never rank,
  never propose, never abandon.

## Workflow (force-with-1-confirmation)

### 1. Resolve the tool + workspace, inventory (read-only)
Resolve `specs.py` by the fallback in
[../quenching-specs-backlog-add/references/backlog-zone.md](../quenching-specs-backlog-add/references/backlog-zone.md)
§Resolving the tool (plugin path `${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py` → the target's
`.claude/hooks/specs.py` → the declared manual check, saying so in the report), invoked via
`python3` or `py`. Resolve the `specs/` root at the repo root. If **neither** `specs/` nor a
legacy `openspec/` exists, that is expected — Step 4 offers to scaffold.
Then collect, writing nothing: `specs.py doctor`, `specs.py validate`, `specs.py list --json`
(names, statuses, `lastModified`); `Glob` `specs/backlog/*.md` + read `backlog/index.md`;
`Glob` a legacy `openspec/` tree (to detect `sp-legacy-workspace`) and read it if present;
`Glob` `.claude/skills/openspec-*/SKILL.md` and `.claude/commands/opsx/*.md` (shadow copies,
relevant only under a legacy migration); read `docs/index.md` for `okf_version`.

**`status --json` is conditional, not routine.** The only finding it feeds is `sp-plan-complete`
— which this sweep **reports**, never fixes. Run `specs.py status --plan <n> --json` only for the
plans `list --json` already shows at full task progress (plus any the user named), never once per
active plan by default: a workspace with a dozen open plans would otherwise pay a dozen payloads
in context to produce one line of report.

**Supplied inventory (handoff).** When the caller passes an inventory —
`quenching-specs-align-and-update` Stage 1 always does, because its Step 2 assessment collected
exactly these sources moments earlier — take it as given and skip the collection above. Nothing
has written to disk between that assessment and this invocation, so re-running `doctor`,
`validate`, and `list --json` returns the same bytes at full cost. Re-collect only what the
handoff does not carry.

**Done when:** every source above is in hand (collected or supplied) and nothing has changed.

### 2. Classify every finding
Map what the inventory holds onto the finding codes in
[references/conformance.md](references/conformance.md), splitting the two tables: what the sweep
**fixes** (structure incl. `sp-no-workspace`/`sp-legacy-workspace`, naming, the `backlog/`
inbox, shadow copies) and what it only **reports** (`sp-plan-complete`, `sp-plan-blocked`,
`sp-plan-stale`, `sp-backlog-untriaged`, `sp-ledger-orphan`, `sp-ledger-in-flight`). A legacy
`openspec/` fold that means folding main specs into `docs/standards/` requires an OKF bundle —
if `docs/index.md` with `okf_version` is absent, that fold **stops** and the skill suggests
`/docs:align` first. For a shadow copy, diff it against the plugin's skill of the same name
before classifying: identical → removal candidate, divergent → `sp-shadow-diverged`,
keep-and-report. **Done when:** every finding carries a code and lands in exactly one table.

### 3. Sweep the blast radius of every rename
Run the shared procedure in
[../quenching-align-all/references/sweep-doctrine.md](../quenching-align-all/references/sweep-doctrine.md)
§3 — two repo scans total for the whole rename set, never two per rename — over every planned
plan folder, archived folder, and task slug. **This front's delta:** a plan name leaks further
than any other name the plugin renames, because it becomes a branch name, a PR title, a CI job,
and a script argument. Treat `sp-plan-name` as always worth the scan even when the folder looks
internal.
**Done when:** each planned rename is marked coupled or free, with its hits.

### 4. Present ONE plan → gate
One plan, in sections: scaffold (copy `${CLAUDE_PLUGIN_ROOT}/assets/specs/` into `specs/` when
`sp-no-workspace`, plus install `specs.py` into `.claude/hooks/` and the operator manual
`specs/QUENCHING.md` — install / refresh / leave); legacy **migration** (the one-way fold above,
each main-spec→`docs/standards/` mapping shown as a human-chosen cut, interop-lost stated);
tool repairs (each quoting `specs.py doctor`/`validate`'s own message); renames (old →
canonical, coupled ones marked); backlog work (seed / stamps / zone install / zone regeneration
/ index frontmatter stripped); shadow copies to remove and diverged ones kept-and-reported. Then,
separately and explicitly labelled **"reported, not applied"**, the cycle findings with their
owning skill. Wait for the single confirmation; each code-coupled rename awaits its own.
**Done when:** the user has answered; declined → nothing written, run ends.

### 5. Apply exactly what was approved
Copy `assets/specs/` and install `specs.py` if approved; run the migration fold if approved;
apply each tool-stated repair; rename the confirmed folders and update every reference site
alongside its individually confirmed rename; seed `specs/backlog/` from
`${CLAUDE_PLUGIN_ROOT}/assets/specs/backlog/index.md` when missing; install the operator manual
from `${CLAUDE_PLUGIN_ROOT}/assets/specs/QUENCHING.md` to `specs/QUENCHING.md` under the
four-branch manual-install rule in
[../quenching-docs-align/SKILL.md](../quenching-docs-align/SKILL.md) §4 (cited, never restated —
same banner, same version fill, same never-clobber-a-de-bannered-copy branch); stamp `type: task`
(MERGE) and rename task slugs; install the GENERATED markers without touching the fixed prose or
the Completed ledger; delete the approved shadow copies and any `/opsx:*` wrappers under a
migration. **Done when:** every confirmed row is applied and nothing outside the plan changed.

### 6. Verify, log, report
Re-run `specs.py doctor` and `specs.py validate` — clean, or the residual message reported
verbatim. Regenerate the `backlog/index.md` DERIVED zone with `specs.py backlog reindex`, then
run the backlog check in
[../quenching-specs-backlog-add/references/backlog-zone.md](../quenching-specs-backlog-add/references/backlog-zone.md)
§The on-write check — `okf-validate.py specs/backlog --listing-root`, exit 0 with no
`index-broken-link` / `index-orphan` — plus the two things the validator cannot see (zone matches
disk, Completed ledger untouched). The OKF hook is docs-scoped by config, so it does not fire on
`specs/`; this run is the coverage.
In a repo with an OKF bundle, append **one** consolidated entry to `docs/log.md` per
**Appending to `log.md`** in
[../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md):
`**Update**: [specs/](/specs/backlog/index.md) — aligned workspace (N renamed, M tasks stamped,
K shadow copies removed)`. Then report the counts **and** the reported-not-applied residue, each
with the command that closes it (`/specs:plan:archive`, `/specs:plan:update`,
`/specs:plan:abandon`, `/specs:backlog:triage`). **Done when:** doctor/validate state, counts, and
residue are all reported.

## Invariants to never violate

- Never author, edit, or delete a plan's proposal, design, tasks, or contents — only folder
  names and the quenching-managed `backlog/` are this sweep's to write. (A legacy fold's
  main-spec→`docs/standards/` mapping is the one authored crossing, and it is human-chosen.)
- Never move a plan into `archive/`, never set a task's `priority`, never propose a plan —
  those are `quenching-specs-plan-archive`, `quenching-specs-backlog-triage`, and
  `quenching-specs-plan-propose`.
- Never write anything before the plan's OK; a code-coupled rename never rides the batch. A
  cycle-authorized run replaces only the batch gate with narration — never a code-coupled item's
  own OK.
- Never derive an archive date from filesystem mtime — read `.specs.json` `created`, or report
  and leave the name alone.
- Never delete a **diverged** shadow copy, and never touch any `.claude/` skill or command
  outside `openspec-*` / `opsx/` under a legacy migration — that surface is
  `quenching-skill-align`'s.
- Never hand-edit inside the `backlog/index.md` GENERATED markers, never add frontmatter to
  `backlog/index.md`, and never leave the zone stale.
- Never overwrite a `specs/QUENCHING.md` whose `claude-quenching` banner a human removed — keep
  it and report it.
- Never invent a repair the tool did not state.
- Never hand this SKILL.md `context: fork` — both gates are mid-flow.
