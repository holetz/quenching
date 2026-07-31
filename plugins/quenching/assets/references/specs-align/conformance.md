# The canonical `specs/` workspace + the exact checks `/specs:align` applies

The single owner of the **specs-workspace conformance contract**: what a canonical `specs/`
surface looks like, the probe that decides whether the sweep runs at all, the finding codes it
produces, which findings it **fixes** versus which it only **reports**, and the two one-way
**migrations** (an older quenching workspace, and a legacy `openspec/` one). The spec-driven facts
themselves — the phase folders, the fourteen canonical sections, the gates, the derived stages, the
`specs.py` surface — live once in
[`specs-develop/spec-driven.md`](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md)
and are cited here, never restated.

This is the `specs/` analogue of
[`docs-align/conformance.md`](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md).
**Two checkers cover it, both programs, and there is no third:** `specs.py doctor` and
`specs.py validate` cover the workspace and every spec file (both `--json`, strict exit codes).
Nothing is left for the sweep to verify by reading — see §The convergence condition for why that
matters more than it sounds.

The whole `specs/` front is **plugin-owned**: unlike the old `openspec/` surface (half of which
belonged to an external CLI), there is no CLI-owned/quenching-managed ownership line here. The
sweep can align every part of it — scaffold, rename, seed, stamp, regenerate — bounded only by
the never-delete-on-a-guess and code-coupled-renames-gate-individually rules the aligns share
([`align/sweep-doctrine.md`](${CLAUDE_PLUGIN_ROOT}/assets/references/align/sweep-doctrine.md)).

## Contents

- [The probe — this front's two commands](#the-probe--this-fronts-two-commands)
- [The canonical workspace](#the-canonical-workspace)
- [Findings the sweep FIXES (inside the one plan → one OK)](#findings-the-sweep-fixes-inside-the-one-plan--one-ok)
- [Migrating an older workspace](#migrating-an-older-workspace)
- [Migrating a legacy `openspec/` workspace (`sp-legacy-workspace`)](#migrating-a-legacy-openspec-workspace-sp-legacy-workspace)
- [Findings the sweep REPORTS (never auto-closes)](#findings-the-sweep-reports-never-auto-closes)
- [The OKF validator is never pointed at `specs/`](#the-okf-validator-is-never-pointed-at-specs)
- [The convergence condition](#the-convergence-condition)

## The probe — this front's two commands

The rule is the shared one — nothing is inventoried until the front's own verifier has said there
is work, and the same program closes the run
([`align/sweep-doctrine.md`](${CLAUDE_PLUGIN_ROOT}/assets/references/align/sweep-doctrine.md)
§Probe before the inventory, which also states why it is load-bearing rather than an
optimization). What follows is only its `specs/` instantiation.

**Two commands, before any inventory:**

```bash
specs.py doctor --json      # workspace shape;  exit 0 = conformant
specs.py validate --json    # every spec file;  exit 0 = conformant
```

Both exit **0** when nothing error-severity was found; warnings are reported and never set the exit
code. So the branch reads off the exit codes first, and off the severities only to explain itself:

| Result | What the sweep does |
| --- | --- |
| both exit 0, no findings at all | **STOP.** Report "`specs/` conformant, N specs, nothing to align" and end. No inventory, no plan, no confirmation. |
| both exit 0, findings are all REPORTS-table warnings | STOP the same way, then list those findings with the command that closes each. Structure is conformant; the residue is the cycle's. |
| either exits 1 or 2 | Run the full inventory and continue at §Findings the sweep FIXES. |

An error-severity REPORTS-table code — `sp-empty-section` is the one — therefore forces a full run
that can only report it. That is correct rather than wasteful: a malformed heading is neither an
answer nor a not-yet, and it is worth the human seeing it inside a plan rather than in a footnote.

`doctor` is also the only call that tells an **unmigrated** workspace apart from an empty one, so
it runs first on this front either way — offering to scaffold a repo that already holds unmigrated
work would be the worst outcome the probe can produce.

## The canonical workspace

```
specs/
  QUENCHING.md                 # the operator manual (payload — not a spec)
  plans/                       # a spec's whole active life: captured → … → ready → executing
    YYYY-MM-DD-<slug>.md       # ONE spec per file — no listing file; `specs.py list` derives it
  archive/                     # done or abandoned (`outcome:` tells them apart)
    YYYY-MM-DD-<slug>.md
    YYYY-MM-DD-<name>/         # v1 plan folders — HISTORICAL, never migrated
```

Three invariants define conformance, and every code below traces to one of them:

1. **One spec is one file**, named `YYYY-MM-DD-<slug>.md` in both folders. A directory inside
   `plans/` is unmigrated v1 work.
2. **The folder is the phase**, and there are only two — `plans/` and `archive/`. There is no
   `phase:` frontmatter field to disagree with them, and the stages *within* `plans/` are derived
   from section presence and frontmatter, never from a third folder.
3. **`archive/` is history.** Its v1 plan folders are deliberately not migrated, and are never
   flagged, renamed, or rewritten.

## Findings the sweep FIXES (inside the one plan → one OK)

Each is mechanical: a rename, a stamp, a regeneration, a copy, or a tool-declared remedy. Codes
marked **(tool)** are emitted by `specs.py doctor` or `validate` with their own declared remedy —
apply *that*, never an invented one, because an invented fix can silently corrupt a spec.

| Code | Fires when | Fix |
| --- | --- | --- |
| `sp-no-workspace` **(tool)** | No `specs/`, and no legacy `openspec/` | Offer to scaffold by copying `${CLAUDE_PLUGIN_ROOT}/assets/specs/` (both phase folders + the operator manual + template + schema). Declining ends the run. |
| `sp-v2-layout` **(tool)** | `backlog/` or `ready/` still holds specs | Run **`specs.py migrate`** (§Migrating an older workspace). It moves every file into `plans/` unrenamed. |
| `sp-v1-leftover` **(tool)** | A three-file plan folder sits at the specs root | Run **`specs.py migrate`** — the same command folds it into one file. |
| `sp-stray-dir` **(tool)** | A directory sits inside `plans/` | Unmigrated v1 work. Same remedy: `specs.py migrate`. Never fires inside `archive/`. |
| `sp-legacy-workspace` | A legacy `openspec/` tree is present | The one-way `openspec/` fold (§below). The only place `openspec/` is touched. |
| `sp-missing-phase` **(tool)** | `plans/` or `archive/` is absent | Create it. The folder IS the phase, so a missing one makes its specs unfindable. |
| `sp-stray-file` **(tool)** | A file at the specs root other than `QUENCHING.md` / `schema.json` | Move it into a phase folder, or report it. |
| `sp-bad-filename` | A file in a phase folder is not `YYYY-MM-DD-<slug>.md` | Rename to the canonical form, deriving the date from frontmatter or the path's first commit — **never** from mtime, which a checkout rewrites. No date derivable → report, never guess. |
| `sp-slug-mismatch` **(tool)** | Frontmatter `slug` disagrees with the filename suffix | Make the frontmatter match the filename — the filename is the identity a human reads in a listing. |
| `sp-missing-frontmatter` **(tool)** | `slug`, `title`, or `verification` absent | Stamp it (MERGE — fill what is missing, preserve what is filled, including third-party keys). |
| `sp-bad-verification` **(tool)** | `verification` outside the three declared values | Set the default (`per-section`) and say so, or take the value the human states. |
| `sp-duplicate-slug` **(tool)** | Two files resolve to one slug | Rename one. **Always blast-radius-swept**: a slug is what every command and cross-reference names, so it leaks into branch names, PR titles, CI, and scripts. Code-coupled → its own confirmation. |
| `sp-shadow-skill` | `.claude/skills/openspec-<x>/SKILL.md` carries `metadata.generatedBy` **and** the plugin ships a command covering it | Propose removal in the plan; the batch OK covers it. Legacy migration only. |
| `sp-shadow-command` | `.claude/commands/opsx/*.md` is a CLI-generated wrapper for a plugin-shipped command | Propose removal alongside its skill. |
| `sp-shadow-diverged` | A shadow copy exists but its body **differs** from the plugin's | **Keep and report** with the observed divergence — a repo may have deliberately forked it. Removal only on the human's explicit word. |

## Migrating an older workspace

One command folds every older layout forward, one-way, driven by the tool rather than by prose:

```bash
specs.py migrate --dry-run --json     # what would move, where, and where each date comes from
specs.py migrate --json               # exit 2 when there is nothing to migrate
```

It covers two shapes, and a workspace holding both is folded in one run:

### `backlog/` + `ready/` → `plans/` (`sp-v2-layout`)

- **Every file moves unrenamed.** The basename is the spec's identity from capture to archive, so
  the fold is a `git mv` and nothing else — no date is recomputed and no slug is touched.
- **The human OK the `backlog/` → `ready/` hop recorded is not lost**: it was never in the folder.
  A spec that had reached `ready/` is *derived* as `ready` from its ten filled sections, and the
  "a human said go" fact is `approved:` in frontmatter from here on.
- **A collision refuses before anything moves.** Two specs with the same basename in the two
  folders is exit 2 with both paths — never a silent overwrite, never a suffix invented to get
  past it.
- **A legacy folder still holding anything else is KEPT**, never deleted, and named in the report.

### A v1 three-file plan folder → one file (`sp-v1-leftover`)

- **Each folder folds into ONE file.** `proposal.md`'s `## Why`→`## Problem`,
  `## What Changes`→`## Proposal`; `design.md`'s `## Context` and `## Decisions` merge into
  `## Design` (kept as `###` sub-headings, so nothing is lost); `tasks.md` becomes `## Tasks` with
  every checkbox state preserved.
- **The birth date is never invented.** It comes from `.specs.json`'s `created`, falling back to
  the path's first commit date, and only then to mtime. A folder already named
  `YYYY-MM-DD-<slug>` keeps that date rather than gaining a second one.
- **A gate section the v1 plan never recorded** is written `- none — not recorded in the v1 plan`
  — a fact about the v1 plan, not an invented answer.
- **A folder still holding any other file is KEPT**, never deleted, and the leftover is reported:
  a `baseline.md` or a stray note is the human's to place.
- **A v1 `backlog/` task file** (`type: task`, the OKF-stamped inbox item that predates the specs
  front) becomes a **captured-stage spec**; its `priority`, `tags` and `complexity` are preserved
  as a line in `## Problem`, since spec frontmatter has no home for them. This is the second hop of
  `docs-align/migration.md` §1e.

Both folds share two guarantees:

- **`specs/archive/**` is never touched.** Its v1 plan folders stay as history, and
  `sp-bad-filename` / `sp-stray-dir` never fire inside it.
- **Say this before applying:** the fold is one-way. A repo that upgraded the plugin while holding
  a v1 workspace reads as *empty* to `list` until it runs — which is why the probe runs `doctor`,
  the one command that tells an unmigrated workspace apart from an empty one.

## Migrating a legacy `openspec/` workspace (`sp-legacy-workspace`)

Retained unchanged, and still the only place `openspec/` is touched: `openspec/` → `specs/`; each
`openspec/specs/<capability>/spec.md` folded into `docs/standards/` by a **human-chosen** cut (no
OKF bundle → the fold stops and `/docs:align` is suggested first); `config.yaml` removed; the delta
folders discarded once folded or confirmed obsolete; non-diverged shadow copies and `/opsx:*`
wrappers removed. **Interop with the external OpenSpec CLI is lost — say so before applying.** A
legacy workspace runs this fold first, then `specs.py migrate`.

## Findings the sweep REPORTS (never auto-closes)

Each names either **authoring** (which needs a human's intent) or a **cycle action** (which belongs
to another command). A sweep that filled these would be inventing content and calling it
conformance.

| Code | Fires when | Owner |
| --- | --- | --- |
| `sp-empty-section` | A canonical heading is present with an empty body — malformed, at any stage | The human. Filling it, even with `- none — <reason>`, is **authoring an answer**: only they know whether it is empty because nothing applies or because nobody thought about it. |
| `sp-gate-unmet` | A spec is missing a section its own gate requires | The human, via `/specs:develop` (which asks rather than fills). |
| `sp-stray-heading` | A `##` heading outside the canonical fourteen | The human — folding a stray into a canonical section is a judgment about what it *meant*. |
| `sp-overview-missing` | A spec meets the whole ready gate but carries an empty `## Overview` | `/specs:develop` — written last, once every other section has settled. |
| `sp-handoff-empty` | A spec being executed has an empty `## Handoff` | `/specs:execute`, which refreshes it on four events — a pause, a blocked task, a recorded discovery, the run's last commit. |
| `sp-impact-uncovered` | A `docs/standards/**.md` path declared under `## Impact` that no `## Tasks` item names | The human — add the task, or drop the declaration. Which of the two is correct is a judgment, so the sweep never picks. |
| `sp-unrefined` | A spec meets the whole ready gate but carries no `refined` record | `/specs:develop`'s adversarial bank. **Never gates** — a spec may always be built unrefined. |
| `sp-no-outcome` | An `archive/` spec carries no `outcome:` | The human — `done` and `abandoned` are opposite facts, and nothing can infer which was meant. |
| `sp-spec-complete` | Every `## Tasks` box in a spec is `- [x]` | `/specs:conclude`. This sweep never archives. |
| `sp-spec-blocked` | A spec carries `- [!]` tasks | The human — the reason is already written in the line. |
| `sp-spec-stale` | A spec untouched for **90 days** with open tasks | Report with the age; the human decides. Staleness is evidence, never a verdict — a spec untouched for a year may be waiting on a vendor. |

**There is no ledger code, and no `ready/`-folder code.** A captured spec and the spec it becomes
are one file, so v1's `sp-ledger-orphan` / `sp-ledger-in-flight` describe nothing. And with one
active folder there is no promote to police between stages: reaching the ready set is derived, and
the only promote left is the gated one into `archive/`.

## The OKF validator is never pointed at `specs/`

There is no listing here for it to check, and there never was a spec file it could judge. A spec
carries `slug`/`title`/`verification` and deliberately **no OKF `type:`** — it is not a concept
doc, it lives outside the bundle, and `specs.py validate` (the canonical heading set, the gates,
filename conformance, slug identity) is a far stronger contract than type-presence. Stamping an OKF
type on a spec purely to satisfy a validator that does not model it would be the second source of
truth this front exists to avoid.

`plans/index.md` is a **retired artifact**. It once carried a GENERATED zone, and four codes
(`sp-no-plans-index`, `sp-index-frontmatter`, `sp-no-generated-zone`, `sp-zone-stale`) policed it.
All four are gone, along with the `--listing-root` mode that read them. The sweep neither creates
nor deletes a surviving copy in a target repo
([`retiring-a-reserved-artifact.md`](/docs/standards/architecture/retiring-a-reserved-artifact.md)
§The consequence for disposition).

## The convergence condition

The workspace is conformant when `specs.py doctor` and `specs.py validate` both exit 0 or report
only codes from the REPORTS table. That is the whole condition — two programs, two exit codes.

**It is stated that way on purpose.** It used to carry a clause no program could evaluate: "the
GENERATED zone matches disk". Nothing computed it — `specs.py` never emitted a `changed` field for
a command to read — so the one clause that could actually rot was the one left to a human's eye,
and a listing wrong on disk passed every checker in the stack. The rule that came out of it is
[`generated-listings.md`](/docs/standards/architecture/generated-listings.md); the narrower lesson
belongs here: **a convergence condition may only name what a checker decides.** A clause a program
cannot evaluate is not a stricter standard, it is an unverified one.

That is the same condition the probe checks at the start — which is exactly why a second align over
an already-aligned workspace stops on two tool calls.
