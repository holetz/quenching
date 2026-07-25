# The canonical `specs/` workspace + the exact checks `quenching-specs-align` applies

The single owner of the **specs-workspace conformance contract**: what a canonical `specs/`
surface looks like, the finding codes the sweep produces, which findings the sweep **fixes**
versus which it only **reports**, and the one-way **migration** of a legacy `openspec/`
workspace. The spec-driven facts themselves — the layout, the plan artifact graph, the artifact
formats, the `specs.py` tool surface — live once in
[`../../quenching-specs-plan-propose/references/spec-driven.md`](../../quenching-specs-plan-propose/references/spec-driven.md)
and are cited here, never restated. The backlog index-zone format and its on-write check live
once in
[`../../quenching-specs-backlog-add/references/backlog-zone.md`](../../quenching-specs-backlog-add/references/backlog-zone.md).

This is the `specs/` analogue of
[`../../quenching-docs-align/references/conformance.md`](../../quenching-docs-align/references/conformance.md).
Two checkers cover it, and neither is prose: `specs.py doctor` and `specs.py validate` cover the
plan/workspace shape (both `--json`, strict exit codes); `okf-validate.py specs/backlog
--listing-root` covers the inbox's frontmatter, listing, and link integrity
([`backlog-zone.md`](../../quenching-specs-backlog-add/references/backlog-zone.md) §The on-write check).
Only the genuinely workspace-specific property — the zone-matches-disk check — is verified by the
sweep beyond what the tools report.

The whole `specs/` front is **plugin-owned**: unlike the old `openspec/` surface (half of which
belonged to an external CLI), there is no CLI-owned/quenching-managed ownership line here. The
sweep can align every part of it — scaffold, rename, seed, stamp, regenerate — bounded only by
the never-delete-on-a-guess and code-coupled-renames-gate-individually rules the three aligns
share ([`../../quenching-align-all/references/sweep-doctrine.md`](../../quenching-align-all/references/sweep-doctrine.md)).

## The canonical workspace

```
specs/
  <plan-name>/           # active plan
    .specs.json          # metadata (schema, name, title, created, backlogTask)
    proposal.md          # required
    design.md            # OPTIONAL
    tasks.md             # required
  archive/YYYY-MM-DD-<name>/     # history, never rewritten
  backlog/               # the task inbox
    index.md             # frontmatter-free listing + DERIVED zone + Completed ledger
    <task-slug>.md       # type: task
```

## Findings the sweep FIXES (inside the one plan → one OK)

### Structure

| Code | Condition | Fix |
| --- | --- | --- |
| `sp-no-workspace` | No `specs/` anywhere and no legacy `openspec/` | Offer to scaffold `specs/` by copying `${CLAUDE_PLUGIN_ROOT}/assets/specs/` (backlog seed + templates + schema) — the installer half, exactly as `quenching-docs-align` scaffolds the OKF homes. Declining ends the run. |
| `sp-legacy-workspace` | A legacy `openspec/` workspace is present | Run the **migration procedure** below (one-way). This is the only place `openspec/` is touched. |
| `sp-doctor` | `specs.py doctor` reports a repairable finding | Apply the remedy the tool **declares** in its JSON, never an invented one. |
| `sp-invalid-plan` | `specs.py validate` fails for a plan (missing `proposal.md`/`tasks.md`, a malformed checkbox, unparseable tasks) | Fix only what is mechanical (a `sp-bad-checkbox` line, a missing `.specs.json`). Anything needing authoring routes to `quenching-specs-plan-update`. |

### Naming

| Code | Condition | Fix |
| --- | --- | --- |
| `sp-plan-name` | An active plan folder is not kebab-case canonical English (`AddAuth/`, `nova-autenticacao/`) | Rename the folder to the canonical slug. **Always blast-radius-swept** — a plan name appears in branch names, PR titles, CI, and scripts; every hit outside `specs/` makes it a code-coupled item with its own confirmation. |
| `sp-archive-name` | An archived plan is not `YYYY-MM-DD-<name>` | Rename to the canonical form, deriving the date from the plan's `.specs.json` `created` (never from filesystem mtime, which a checkout rewrites). If no date can be derived, report — never guess. |
| `sp-task-slug` | A `backlog/*.md` slug is not kebab-case canonical English | Rename per the same English-canonical-surface rule the OKF bundle applies (`quenching-docs-align` doctrine); body prose may stay in the repo's language. |

### The `backlog/` inbox

| Code | Condition | Fix |
| --- | --- | --- |
| `sp-backlog-missing` | `specs/backlog/` absent | Seed it from `${CLAUDE_PLUGIN_ROOT}/assets/specs/backlog/index.md` (the fixed prose + the empty DERIVED zone). Every repo has an inbox — unlike an OKF home, it is not evidence-gated. |
| `sp-index-frontmatter` | `backlog/index.md` carries frontmatter | Strip it — the index is a reserved, frontmatter-free listing, same rule as an OKF `index.md`. |
| `sp-task-untyped` | A task file has unparseable frontmatter or an empty/missing `type` | Stamp `type: task` (MERGE — fill what is missing, preserve what is filled, including third-party keys). |
| `sp-zone-missing` | `backlog/index.md` predates the `<!-- BEGIN GENERATED -->` / `<!-- END GENERATED -->` markers | `specs.py backlog reindex` installs the zone **without touching the fixed prose or the Completed ledger** (it anchors on `## Current tasks`). |
| `sp-zone-stale` | The DERIVED zone does not match `backlog/*.md` on disk | `specs.py backlog reindex` regenerates the whole zone deterministically from frontmatter. Never hand-edit inside the markers. |
| `sp-zone-broken-link` | A zone or ledger link resolves to nothing | Reindex fixes zone links; a broken **ledger** link (outside the zone) is reported, never rewritten — the ledger is curated by hand. |

### Shadow copies of the plugin's own skills (migration only)

A legacy `openspec init` generated local `.claude/skills/openspec-*/` and `.claude/commands/opsx/`
copies. In a repo adopting this plugin they are **duplicates**. These codes fire only during a
legacy migration (`sp-legacy-workspace`); a native `specs/` workspace never has them.

| Code | Condition | Fix |
| --- | --- | --- |
| `sp-shadow-skill` | `.claude/skills/openspec-<x>/SKILL.md` carries `metadata.generatedBy` **and** the plugin ships a skill covering it | Propose removal in the plan; the batch OK covers it. |
| `sp-shadow-command` | `.claude/commands/opsx/*.md` is a CLI-generated wrapper for a plugin-shipped skill | Propose removal alongside its skill. |
| `sp-shadow-diverged` | A shadow copy exists but its body **differs** from the plugin's (locally customized) | **Keep and report**, with the observed divergence — a repo may have deliberately forked a skill. Removal only on the human's explicit word. |

This is the one place the `.claude/` surface is touched: **only** `openspec-*` skills and the
`opsx/` wrappers. Everything else under `.claude/` belongs to `quenching-skill-align`.

## Migrating a legacy `openspec/` workspace (`sp-legacy-workspace`)

One-way, inside the single plan → one OK. Interop with the external OpenSpec CLI is **lost** —
say so before applying:

1. **Rename and flatten.** `openspec/` → `specs/`; `changes/<n>/` → `specs/<n>/`;
   `changes/archive/` → `specs/archive/`. (The delta was the only thing that made the
   `changes/` nesting necessary; without it, plans sit flat.)
2. **Fold the main specs into `docs/`.** For each `openspec/specs/<capability>/spec.md`,
   **propose** a mapping to one or more `docs/standards/<subject>/<concept>.md` — the cut is
   **chosen by the human in the plan, never inferred** (a capability spec may become 1 or N
   standards). If the target has **no** OKF bundle (`docs/index.md` with `okf_version`), the
   fold **stops** and the skill suggests `/docs:align` first.
3. **Drop the CLI scaffolding.** Remove `config.yaml`; convert each `.openspec.yaml` →
   `.specs.json` (carry `created`; set `schema: spec-driven`).
4. **Discard the delta folders** (`specs/<n>/specs/…` inside a change) **only after** it is
   confirmed their content was folded into `docs/standards/` (step 2) or is obsolete.
5. **Remove non-diverged shadow copies** (`sp-shadow-*`) and the `/opsx:*` wrappers.

Renames with a code blast radius gate individually
([`sweep-doctrine.md`](../../quenching-align-all/references/sweep-doctrine.md) §3).

## Findings the sweep REPORTS (never auto-closes)

Cycle actions, not conformance defects: driving them needs judgment a sweep does not have, and
each has an owning skill the report names.

| Code | Condition | Routes to |
| --- | --- | --- |
| `sp-plan-complete` | `specs.py status --plan <n> --json` shows every artifact `done` and `applyReady`, all tasks `- [x]`, yet the plan is still in `specs/` | `quenching-specs-plan-archive` (`/specs:plan:archive`) |
| `sp-plan-blocked` | A plan has been `blocked` on the same artifact across the sweep's window | `quenching-specs-plan-update` (`/specs:plan:update`) |
| `sp-plan-stale` | `specs.py list --json` `lastModified` older than **90 days** with unfinished tasks | Report with the age; the human decides — revise (`/specs:plan:update`), finish and archive (`/specs:plan:archive`), or abandon (`/specs:plan:abandon`). Staleness is evidence, never a verdict |
| `sp-backlog-untriaged` | N tasks carry no `priority`, or a `priority` outside `critical\|high\|medium\|low` | `quenching-specs-backlog-triage` (`/specs:backlog:triage`) — priority is triage's to set, never align's |
| `sp-ledger-orphan` | A `backlog/index.md` **Completed ledger** row names a plan that exists in neither `specs/` nor `specs/archive/` | Report the row and the missing plan. `quenching-specs-plan-abandon` (`/specs:plan:abandon`) reopens such a task **going forward**; an already-orphaned row is a hand fix. Never rewrite the ledger |
| `sp-ledger-in-flight` | A ledger row names a plan still **active** in `specs/` | Not a defect — the honest in-flight state: the task was developed, the work is not finished. Report as work in progress |

Untriaged is a **valid state**, a stale plan is **not** a defect, and an unarchived complete plan
may be waiting on a deploy. Reporting them is the whole job — the anti-fabrication boundary the
plugin draws everywhere between a sweep and a decision.

### The ledger's two meanings

`backlog/index.md`'s Completed ledger records **two transitions** with the same row shape:
*developed* (the task became a plan, written by `quenching-specs-plan-propose` at apply-ready) and
*done* (the work finished, written by `quenching-specs-backlog-triage` on a human's word). The
Outcome column distinguishes them — `plan <name>` versus a one-line "done — …" — and the two
codes above keep the distinction honest: a *developed* row whose plan is still active is
`sp-ledger-in-flight` (fine, in progress), one whose plan has vanished is `sp-ledger-orphan` (the
task was lost). Neither is ever auto-repaired.

## The convergence condition

The workspace is **aligned** when: `specs.py doctor` and `specs.py validate` are clean; every
active plan and archived folder carries a canonical name; `backlog/` exists with a
frontmatter-free `index.md`, a DERIVED zone matching disk, and every task stamped `type: task`;
no legacy `openspec/` remains; and no undiverged shadow copy remains. Everything else the sweep
found is **reported residue** — named, with its owning skill, never silently dropped.
