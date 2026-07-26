# The canonical `specs/` workspace + the exact checks `quenching-specs-align` applies

The single owner of the **specs-workspace conformance contract**: what a canonical `specs/`
surface looks like, the finding codes the sweep produces, which findings the sweep **fixes**
versus which it only **reports**, and the two one-way **migrations** (a v1 three-file workspace,
and a legacy `openspec/` one). The spec-driven facts themselves — the three phase folders, the
thirteen canonical sections, the phase gates, the derived stages, the `specs.py` surface — live
once in
[`../../quenching-specs-develop/references/spec-driven.md`](../../quenching-specs-develop/references/spec-driven.md)
and are cited here, never restated.

This is the `specs/` analogue of
[`../../quenching-docs-align/references/conformance.md`](../../quenching-docs-align/references/conformance.md).
Two checkers cover it and neither is prose: `specs.py doctor` and `specs.py validate` cover the
workspace and every spec file (both `--json`, strict exit codes); `okf-validate.py specs/backlog
--listing-root` covers the **listing** and nothing else (§What checks the backlog listing). Only
the genuinely workspace-specific property — the zone-matches-disk check — is verified by the sweep
beyond what the tools report.

The whole `specs/` front is **plugin-owned**: unlike the old `openspec/` surface (half of which
belonged to an external CLI), there is no CLI-owned/quenching-managed ownership line here. The
sweep can align every part of it — scaffold, rename, seed, stamp, regenerate — bounded only by
the never-delete-on-a-guess and code-coupled-renames-gate-individually rules the three aligns
share ([`../../quenching-align-all/references/sweep-doctrine.md`](../../quenching-align-all/references/sweep-doctrine.md)).

## Contents

- [The canonical workspace](#the-canonical-workspace)
- [Findings the sweep FIXES (inside the one plan → one OK)](#findings-the-sweep-fixes-inside-the-one-plan--one-ok)
- [Migrating a v1 workspace (`sp-v1-workspace`)](#migrating-a-v1-workspace-sp-v1-workspace)
- [Migrating a legacy `openspec/` workspace (`sp-legacy-workspace`)](#migrating-a-legacy-openspec-workspace-sp-legacy-workspace)
- [Findings the sweep REPORTS (never auto-closes)](#findings-the-sweep-reports-never-auto-closes)
- [What checks the backlog listing](#what-checks-the-backlog-listing)
- [The convergence condition](#the-convergence-condition)

## The canonical workspace

```
specs/
  QUENCHING.md                 # the operator manual (payload — not a spec)
  backlog/                     # DEFINITION phase — captured → proposed → designed → refined
    index.md                   # frontmatter-free listing + GENERATED zone
    YYYY-MM-DD-<slug>.md       # ONE spec per file
  ready/                       # EXECUTION phase — ready to build, or building
    YYYY-MM-DD-<slug>.md
  archive/                     # done or abandoned (`outcome:` tells them apart)
    YYYY-MM-DD-<slug>.md
    YYYY-MM-DD-<name>/         # v1 plan folders — HISTORICAL, never migrated
```

Three invariants define conformance, and every code below traces to one of them:

1. **One spec is one file**, named `YYYY-MM-DD-<slug>.md` in every folder. A directory inside
   `backlog/` or `ready/` is unmigrated v1 work.
2. **The folder is the phase** — there is no `phase:` frontmatter field to disagree with it.
3. **`archive/` is history.** Its v1 plan folders are deliberately not migrated, and are never
   flagged, renamed, or rewritten.

## Findings the sweep FIXES (inside the one plan → one OK)

Each is mechanical: a rename, a stamp, a regeneration, a copy, or a tool-declared remedy.

| Code | Fires when | Fix |
| --- | --- | --- |
| `sp-no-workspace` | No `specs/`, no v1 workspace, no legacy `openspec/` | Offer to scaffold by copying `${CLAUDE_PLUGIN_ROOT}/assets/specs/` (three phase folders + backlog seed + template + schema). Declining ends the run. |
| `sp-v1-workspace` | `specs.py doctor` reports `sp-v1-leftover` — a three-file plan folder at the specs root | Run **`specs.py migrate`** (§below). The remedy is the tool's own, declared in its JSON. |
| `sp-legacy-workspace` | A legacy `openspec/` tree is present | The one-way `openspec/` fold (§below). The only place `openspec/` is touched. |
| `sp-missing-phase` | A phase folder is absent | Create it. The folder IS the phase, so a missing one makes its specs unfindable. |
| `sp-doctor` | `specs.py doctor` reports any other repairable finding | Apply the remedy the tool **declares**, never an invented one — an invented fix can silently corrupt a spec. |
| `sp-bad-filename` | A file in a phase folder is not `YYYY-MM-DD-<slug>.md` | Rename to the canonical form, deriving the date from frontmatter or the path's first commit — **never** from mtime, which a checkout rewrites. No date derivable → report, never guess. |
| `sp-slug-mismatch` | Frontmatter `slug` disagrees with the filename suffix | Make the frontmatter match the filename — the filename is the identity a human reads in a listing. |
| `sp-missing-frontmatter` | `slug`, `title`, or `verification` absent | Stamp it (MERGE — fill what is missing, preserve what is filled, including third-party keys). |
| `sp-bad-verification` | `verification` outside `per-task\|per-section\|end-of-plan` | Set the default (`per-section`) and say so, or take the value the human states. |
| `sp-duplicate-slug` | Two files resolve to one slug | Rename one. **Always blast-radius-swept**: a slug is what every command and cross-reference names, so it leaks into branch names, PR titles, CI, and scripts. Code-coupled → its own confirmation. |
| `sp-no-backlog-index` | `backlog/index.md` absent | Seed from `${CLAUDE_PLUGIN_ROOT}/assets/specs/backlog/index.md`. Every repo has a definition phase — unlike an OKF home, it is not evidence-gated. |
| `sp-index-frontmatter` | `backlog/index.md` carries frontmatter | Strip it — a reserved, frontmatter-free listing, the same rule an OKF `index.md` follows. |
| `sp-zone-missing` | `backlog/index.md` has no `<!-- BEGIN GENERATED -->` … `<!-- END GENERATED -->` markers | `specs.py backlog reindex` installs the zone without touching the fixed prose. |
| `sp-zone-stale` | The GENERATED zone disagrees with `backlog/*.md` on disk | `specs.py backlog reindex` regenerates it deterministically from disk. Never hand-edit inside the markers. |
| `sp-shadow-skill` | `.claude/skills/openspec-<x>/SKILL.md` carries `metadata.generatedBy` **and** the plugin ships a skill covering it | Propose removal in the plan; the batch OK covers it. Legacy migration only. |
| `sp-shadow-command` | `.claude/commands/opsx/*.md` is a CLI-generated wrapper for a plugin-shipped skill | Propose removal alongside its skill. |
| `sp-shadow-diverged` | A shadow copy exists but its body **differs** from the plugin's | **Keep and report** with the observed divergence — a repo may have deliberately forked it. Removal only on the human's explicit word. |

## Migrating a v1 workspace (`sp-v1-workspace`)

One-way, mechanical, and driven by the tool rather than by prose:

```bash
specs.py migrate --dry-run --json     # what would fold, where, and where each date comes from
specs.py migrate --json               # exit 2 when the workspace is already v2
```

What it does — and the guarantees the sweep states **before** applying:

- **Each v1 plan folder folds into ONE file.** `proposal.md`'s `## Why`→`## Problem`,
  `## What Changes`→`## Proposal`; `design.md`'s `## Context` and `## Decisions` merge into
  `## Design` (kept as `###` sub-headings, so nothing is lost); `tasks.md` becomes `## Tasks` with
  every checkbox state preserved. A plan with tasks lands in `ready/`, one without in `backlog/`.
- **The birth date is never invented.** It comes from `.specs.json`'s `created`, falling back to
  the path's first commit date, and only then to mtime.
- **A gate section the v1 plan never recorded** is written `- none — not recorded in the v1 plan`
  — a fact about the v1 plan, not an invented answer.
- **A plan folder still holding any other file is KEPT**, never deleted, and the leftover is
  reported: a `baseline.md` or a stray note is the human's to place.
- **`specs/archive/**` is never touched.** Its v1 plan folders stay as history, and
  `sp-bad-filename` / `sp-stray-dir` never fire inside it.
- **A v1 `backlog/` task file** (`type: task`) becomes a captured-stage spec; its `priority`,
  `tags`, and `complexity` are preserved as a line in `## Problem`, since v2 frontmatter has no
  home for them.

**Say this before applying:** the fold is one-way, and a target repo that upgraded the plugin while
holding a v1 workspace reads as *empty* to v2 `list` until it runs — which is why this sweep runs
`doctor` (the one command that detects it) before anything else.

## Migrating a legacy `openspec/` workspace (`sp-legacy-workspace`)

Retained unchanged, and still the only place `openspec/` is touched: `openspec/` → `specs/`; each
`openspec/specs/<capability>/spec.md` folded into `docs/standards/` by a **human-chosen** cut (no
OKF bundle → the fold stops and `/docs:align` is suggested first); `config.yaml` removed; the delta
folders discarded once folded or confirmed obsolete; non-diverged shadow copies and `/opsx:*`
wrappers removed. **Interop with the external OpenSpec CLI is lost — say so before applying.** A
legacy workspace reaching v2 runs this fold first, then `specs.py migrate`.

## Findings the sweep REPORTS (never auto-closes)

Each names either **authoring** (which needs a human's intent) or a **cycle action** (which belongs
to another skill). A sweep that filled these would be inventing content and calling it conformance.

| Code | Fires when | Owner |
| --- | --- | --- |
| `sp-empty-section` | A canonical heading is present with an empty body — malformed, in any phase | The human. Filling it, even with `- none — <reason>`, is **authoring an answer**: only they know whether it is empty because nothing applies or because nobody thought about it. |
| `sp-gate-unmet` | A spec is missing a section its own phase's gate requires | The human, via `specs.py section <slug> "<Heading>" --write`. |
| `sp-stray-heading` | A `##` heading outside the canonical thirteen | The human — folding a stray into a canonical section is a judgment about what it *meant*. |
| `sp-handoff-empty` | A `ready/` spec has an empty `## Handoff` | The apply skill, which refreshes it after each committed task and at every promote. |
| `sp-impact-uncovered` | A `docs/standards/**.md` path declared under `## Impact` that no `## Tasks` item names | The human — add the task, or drop the declaration. Which of the two is correct is a judgment, so the sweep never picks. |
| `sp-unrefined` | A `backlog/` spec meets the whole `ready/` gate but carries no `refined` record | The refine skill. **Never gates** — a spec may always be promoted unrefined. |
| `sp-no-outcome` | An `archive/` spec carries no `outcome:` | The human — `done` and `abandoned` are opposite facts, and nothing can infer which was meant. |
| `sp-spec-complete` | Every `## Tasks` box in a `ready/` spec is `- [x]` | The archive flow (`promote --to archive`). This sweep never promotes. |
| `sp-spec-blocked` | A `ready/` spec carries `- [!]` tasks | The human — the reason is already written in the line. |
| `sp-spec-stale` | A `ready/` spec untouched for **90 days** with open tasks | Report with the age; the human decides. Staleness is evidence, never a verdict — a spec untouched for a year may be waiting on a vendor. |

**There is no ledger code.** v1 needed `sp-ledger-orphan` and `sp-ledger-in-flight` because a
backlog task and the plan it seeded were two objects glued by a hand-curated row whose meaning
("developed", not "done") took a paragraph of doctrine to police. In v2 they are the same file, so
the row — and both codes — have nothing left to describe.

## What checks the backlog listing

`okf-validate.py specs/backlog --listing-root` checks the **listing**: `index.md` held to the
plain-listing rule (frontmatter-free, no broken links, no orphans).

It does **not** check the spec files, and must not be pointed at them expecting a verdict. A v2
spec carries `slug`/`title`/`verification` and deliberately **no OKF `type:`** — it is not a concept
doc, it lives outside the bundle, and `specs.py validate` (the canonical heading set, the phase
gates, filename conformance, slug identity) is a far stronger contract than type-presence.
Stamping an OKF type on a spec purely to satisfy a validator that does not model it would be the
second source of truth this front exists to avoid.

**So the sweep runs both and reads each for what it owns:** `specs.py validate` for the specs,
`okf-validate.py … --listing-root` for `index.md`.

## The convergence condition

The workspace is conformant when `specs.py doctor` and `specs.py validate` both exit 0 or report
only codes from the REPORTS table, `okf-validate.py specs/backlog --listing-root` exits 0, the
GENERATED zone matches disk, and no phase folder holds a directory. Anything left is either
authoring or a cycle action, each named with the command that closes it.
