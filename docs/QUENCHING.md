<!-- quenching v1.0.0 · operator manual · generated payload.
     Refreshed by /docs:align (or /align). Edit the plugin asset, not this copy —
     a run with a newer plugin overwrites this file. Remove this banner to keep
     your own version: the align will then leave it alone and report it. -->

# Operating this knowledge base

This repository's `docs/` is an **Open Knowledge Format (OKF v0.1) bundle**, installed and
maintained by the [`quenching`](https://github.com/eloysekonell/quenching) Claude
Code plugin. Every repository that adopts the plugin ends up with the **same tree in the same
places**, so moving between repos costs you nothing.

This file is the **operator manual**: how knowledge gets in, who is allowed to change what, and
which command to run. It is a payload file — not an OKF concept doc, and the validator skips it.

> **This file vs [`index.md`](index.md).** They answer different questions and neither replaces
> the other:
> - **[`index.md`](index.md)** is the bundle's reserved **front door** — *what* is in here (the
>   homes, their boundaries, the link listing). It is generated from disk and must never lie.
> - **`QUENCHING.md`** (this file) is *how the bundle is **operated*** — the commands, the
>   confirmation rules, the enforcement hook, the recipes. It is static, repo-agnostic, and
>   identical in every repo the plugin touches.

---

## 1. I want to… → run this

| I want to… | Command | Scope |
| --- | --- | --- |
| Record a rule or convention **we follow** | `/docs:add` | ONE doc |
| Capture an understanding, concept, or learning | `/docs:learn` | ONE doc |
| Define a term, acronym, or codename | `/docs:define` | ONE glossary entry |
| Pull an external doc, folder, or URL into the base | `/docs:import` | MANY docs |
| Move the agent's project memory into the base | `/docs:import-memory` | MANY docs |
| Fix the structure — homes, stamps, indexes | `/docs:align` | WHOLE bundle |
| Catch the glossary up on terms already documented | `/docs:glossary-backfill` | WHOLE bundle |
| Slim `CLAUDE.md` / `AGENTS.md` down to pointers | `/docs:harness` | harness files |
| Create/update the published docs **site** (mkdocs) | `/docs:documentation:build` | `documentation/` + root config |
| Do all of the above until nothing changes | `/docs:align-and-update` | WHOLE bundle, looped |
| Align **every** front (`docs/`, `specs/`, `.claude/`) | `/align` | whole repo |
| Align **and update** every front, looped | `/align-and-update` | whole repo, looped |

Every command is a thin wrapper over a skill; Claude also routes to the same skill on its own
when you describe the intent in prose ("record that we always use X"). The wrapper is the
**explicit** entry point — use it when you want to be sure which one runs.

> Commands are namespaced by plugin. `/docs:add` is the short form of
> `/quenching:docs:add`; use the long form if another plugin claims the same namespace.

**Not sure between `add` and `learn`?** Ask: *is this a rule we are bound by, or something we
understand?* A binding rule (naming, architecture, CI, review policy) is a **standard** →
`/docs:add`. A domain concept, a mental model, a "why it works this way" → **knowledge** →
`/docs:learn`. If you guess wrong, the skill re-routes and tells you.

---

## 2. The bundle at a glance

The live listing is in [`index.md`](index.md) — this section is the fixed contract behind it.

### The homes

| Home | Holds | `type` |
| --- | --- | --- |
| `standards/` | **how WE do it** — current contracts and conventions, by subject | `standard` |
| `catalog/` | **our data** — systems, schemas, tables | `system`, `schema`, `table` |
| `vision/` | direction by area, no deadline | `vision` |
| `documentation/` | the product docs site (Diátaxis: getting-started · how-to · reference · concepts) | `documentation` |
| `knowledge/` | **generic understanding we hold** — concepts, explanations, learnings | `knowledge` |
| `reference/` | facts about **what WE CONSUME** — tools, libraries, regulations | `reference`, `sidecar` |

A repo without data gets no `catalog/`; homes are installed only when they apply.

**The boundaries that matter.** `standards/` = *how WE build*. `knowledge/` = *what we
understand* (non-binding). `reference/` = *what we consume* (external). `catalog/` = *our data*.
There is **no `decisions/` home**: an agreed-but-unproven decision is a `standard` carrying
`authority: background`; once it is proven in the code it becomes `authority: current`.

### Reserved and exempt filenames

| File | Rule |
| --- | --- |
| `index.md` | A **listing**, never a concept. No frontmatter at all — except the bundle-root `index.md`, which carries **only** `okf_version: "0.1"`. |
| `log.md` | **Retired.** Nothing writes one and nothing checks one, but the name stays reserved so a log left over from an earlier alignment is recognized rather than read as a malformed concept doc. Keep it, delete it — the validator is silent either way. |
| `CLAUDE.md`, `AGENTS.md` | Harness pointers. Exempt from OKF — their honesty is checked by `/docs:harness`, not by the validator. |
| `QUENCHING.md` | This manual. Exempt — a plugin payload, not authored knowledge. |
| anything else `.md` | A **concept doc**: MUST carry parseable YAML frontmatter with a **non-empty `type`**. |

### The frontmatter stamp

Required: `type`. Recommended (missing → warning): `title`, `description`, `resource`,
`timestamp`. `standards/` docs additionally carry `authority: current|background`. `resource` is
always **derived** from what the doc concerns — a `file:line` anchor, an asset URI — and is
**never invented**.

### Language

Folder names, concept-doc file slugs, frontmatter keys, and `type` values are **canonical
English** so they stay greppable across every repo. **Body prose may follow this repo's
language.** Slugs derived from real identifiers (a catalog table, a repository name) stay
verbatim — anglicizing them would break the tie to the real asset.

### Finding a term

Unfamiliar word, acronym, or codename? The glossary is the A–Z lookup:

```bash
grep -i '<term>' docs/knowledge/glossary.md
```

No entry means it is not defined yet — add it with `/docs:define`.

---

## 3. The commands, one by one

### `/docs:add` — insert ONE concept doc

Classifies what you state into its home + `type` + mold, derives the path, writes the doc with a
complete stamp, updates that folder's `index.md`, and offers a glossary entry when the doc
introduces a repo-specific term. **Writes exactly one concept doc.**
*Not for:* structural repair (`/docs:align`), or a task (`/specs:backlog:add`).

### `/docs:learn` — capture ONE piece of generic knowledge

The `knowledge/` counterpart of `add`. Files an understanding you state under
`knowledge/<subject>/` with a `type: knowledge` stamp, then runs the same index + log + glossary
tail. If what you stated is really a binding rule, a how-to, or an external fact, it re-routes to
`/docs:add`. *Not for:* draining agent memory (`/docs:import-memory`).

### `/docs:define` — add or refine ONE glossary term

Edits `knowledge/glossary.md` — a flat, alphabetically sorted bullet list, the one deliberate
exception to "one concept per file". Confirms the term is repo-specific, inserts it in
alphabetical position with a one-sentence definition and a **derived** link (never invented), and
**MERGES** into a filled entry rather than clobbering it. *Not for:* a full concept doc
(`/docs:learn`), or a bundle-wide sweep (`/docs:glossary-backfill`).

### `/docs:import` — ingest an external source as MANY docs

The batch fan-out of `add`. Reads local files/folders or URLs, extracts knowledge units,
classifies each into its home, dedupes within the source **and** against what the bundle already
holds, presents **one** ingestion plan, then mints every doc under the same insert procedure.
Web ingestion is **bounded** (seed list + host allowlist + page cap — never an open crawl).
Minted docs are attributed to the source and enter as `authority: background` until proven here.
**Additive only — it never deletes.** Requires an existing bundle; run `/docs:align` first.

### `/docs:import-memory` — drain the agent's project memory

Reads `~/.claude/projects/<this-repo>/memory/`, promotes each durable memory into a `standard`,
a `knowledge` doc, or a task in `specs/backlog/`, and **clears each memory only after its doc
has landed and passed the conformance check**. A `user` memory or an unroutable fact is flagged
and **kept**, never silently deleted. One plan, one confirmation.

### `/docs:align` — force the whole bundle into shape

The installer, migrator, and validator in one. Scaffolds missing homes, migrates variant folder
names (`docs/arquitetura/` → `docs/standards/`), folds prefix-clustered files into subject
subfolders (`nomenclatura-*.md` → `naming/`), translates non-English slugs, stamps missing
frontmatter (**MERGE** — a filled key and any third-party key survive), regenerates every
`index.md`, writes `okf_version`, installs this manual, then re-runs the validator. It also offers
to install or upgrade the enforcement hook, and — when the repo has a `documentation/` home — an
mkdocs-material site setup.

**Invasive by design.** It presents the complete plan and executes on **one** confirmation. A
rename whose blast radius reaches **product code** (imports, path constants, docstrings) is
**always its own separate confirmation** — it never rides the batch OK.

### `/docs:glossary-backfill` — catch the glossary up

Sweeps the **whole** bundle for repo-specific terms that are already documented but were never
listed, fanning sub-agents out per home slice, then merges every slice into **one** plan applied
on a single confirmation. `catalog/**` and `reference/repositories/**` are listed but not
body-scanned by default. The bulk, retroactive counterpart of the per-capture glossary step.

### `/docs:harness` — make `CLAUDE.md` a thin pointer

Refactors the root `CLAUDE.md`, every subfolder `CLAUDE.md`, and `AGENTS.md` into honest
navigation pointers over this bundle. Every unit of content is classified: **KEEP** the
harness-operational (build/run/test commands, env vars, agent etiquette needed every turn),
**MOVE** durable knowledge into its `docs/` home leaving a citing pointer, **DEDUPE** what the
bundle already holds, **FLAG** contradictions, and keep-and-report the unroutable. Then it
verifies **every pointer resolves**. Move, never copy: after the run each fact lives in exactly
one place.

### `/docs:documentation:build` — create/update the docs **site**

Owns the thin **site layer** that renders `documentation/` as an mkdocs-material site: the
`mkdocs.yml` + `requirements.txt` at the repo **root** (outside the bundle) and one `.pages` nav
file per section (inside it). It installs the layer when absent, **merges** it forward when a
human has customized it (missing required keys only, always shown as a diff), rewrites a stale
nav after pages come and go, gitignores `site/`, installs the GitHub Pages workflow on request,
and proves the result with `mkdocs build --strict` — reporting `unverified` rather than claiming
a build that never ran.

It **never touches a page.** A section with no `index.md`, an unstamped page, or an absolute
`/docs/<other-home>/…` link that dies in the built HTML is **reported** with the command that
fixes it (`/docs:align`, `/docs:add`). The site is rooted at `documentation/` — the other homes
are your internal surface and stay unpublished; re-aiming `docs_dir` is its own confirmation.
Run it after adding pages, after a section is created, or whenever the nav looks wrong.

### `/docs:align-and-update` — align, then keep going until nothing changes

This front's conductor, and the exact complement of `/docs:align`: the align fixes **structure**
in one pass, this **also pulls content in** — from the agent's project memory and from your
harness files — and backfills the glossary, looping until stable. Every front has this same pair
(`/specs:align-and-update`, `/skill:align-and-update`); `/align-and-update` runs all three.

Runs `align` → `import-memory` → `harness` → `glossary-backfill` as a dependency
pipeline, **pass after pass**, until a full pass changes nothing and the validator is clean (a
fixpoint). **One** OK at the start authorizes the whole run; code-coupled items still confirm
individually. It conducts, never reimplements — every change is made by the sub-skill under its
own doctrine. The per-item commands (`add`, `learn`, `define`, `import`) are **not** loop stages:
each needs a human-supplied input, so the cycle **surfaces** those gaps rather than fabricating
content to close them. Bounded by a pass cap and a no-progress guard — it converges or reports
the residue, never spins.

---

## 4. How these skills behave — the operating model

Read this once and every command becomes predictable.

- **One plan → one OK.** Sweeps never write incrementally while you watch. You see the complete
  plan, you answer once, it executes exactly that.
- **A code-coupled change always confirms alone.** If a rename would edit product code, CI, or
  scripts, it is pulled out of the batch and asked separately, with its blast radius shown —
  even inside a `/docs:align-and-update` or `/align` run that you already authorized.
- **MERGE, never clobber.** Stamping fills a *missing* key. A key you set — including one no OKF
  consumer knows about — survives every sweep.
- **Generated zones are derived from disk.** Anything between `<!-- BEGIN GENERATED -->` and
  `<!-- END GENERATED -->` is rebuilt from the files it describes. **Never hand-edit inside
  one** — edit the source docs and re-run the command that owns the zone.
- **Nothing is invented.** A `resource:` comes from a real anchor; a glossary link comes from a
  doc that exists; a standard is generated only with observed `file:line` evidence. What cannot
  be grounded becomes a recorded deferral, never a plausible-sounding fill.
- **Deletion needs your word.** No sweep removes a doc, a memory, or a skill because it looks
  obsolete. The one exception is `/docs:import-memory`, which clears a memory **only after** its
  replacement doc has landed and validated.
- **Convergence, not accommodation.** A variant name is treated as a migration candidate, not a
  local convention to preserve. That is the point: every adopting repo looks the same.

---

## 5. The enforcement hook

`.claude/hooks/okf-validate.py` is a zero-dependency Python checker that keeps future edits
conformant. It **proposes**, it does not block — unless you opt in.

| Event | Behavior |
| --- | --- |
| `PostToolUse` (`Write`/`Edit`) | Validates the touched `docs/**` file and proposes the fix. Exit 0 — the edit stands. |
| `Stop` | End-of-turn sweep of the whole bundle, proposing residual gaps. **Dirty-gated**: a turn that edited no `docs/**` file costs one `stat`. |
| `PreToolUse` | **Opt-in.** Denies the two hard violations before they land — an `index.md` carrying a `type`, or a concept doc with no `type`. Off by default. |

Config lives in `.claude/hooks/hooks-config.json`, block `okfValidate`. Per-developer overrides
go in `hooks-config.local.json` (gitignore it).

| Knob | Default | Effect |
| --- | --- | --- |
| `enabled` | `true` | `false` makes the hook inert. |
| `docsDir` | `"docs"` | The bundle root, relative to the repo root. |
| `warnAsError` | `false` | Promotes recommended-field warnings to failures. |
| `blockOnFail` | `false` | Escalates the `PostToolUse`/`Stop` proposal to `decision: block`. |
| `hardBlock` | `false` | Turns on the `PreToolUse` deny gate (also uncomment its block in `settings.json`). |
| `deadlineMs` | `4000` | Bounds the `Stop` sweep; aborting keeps the dirty marker for next turn. |
| `stopScan` | `"dirty"` | `"always"` restores the unconditional every-turn sweep. |
| `ignoreGlobs` | *(none)* | Bundle-relative globs to skip — for regenerated or vendored paths. |

Run it yourself any time:

```bash
python3 .claude/hooks/okf-validate.py docs           # human report; exit 0 = conforms
python3 .claude/hooks/okf-validate.py docs --json    # machine-readable findings
python3 .claude/hooks/okf-validate.py --version      # must match the plugin's version
```

---

## 6. Recipes

**Adopting the plugin in an existing repo.** Run `/align` (all three fronts) or `/docs:align`
(this one). Accept the hook install when offered. Then `/docs:harness` to move whatever knowledge
is inlined in `CLAUDE.md` into its home, and `/docs:import-memory` if the agent has accumulated
project memory. Finish with `/docs:glossary-backfill`.

**A normal working day.** You decide something → `/docs:add`. You learn something → `/docs:learn`.
A term keeps coming up → `/docs:define`. Something to do later → `/specs:backlog:add`. Each is
seconds, one doc, no interrogation.

**After a big refactor or a doc dump.** `/docs:align-and-update` — it will align the structure, drain
memory, re-thin the harness, and backfill the glossary, looping until stable, then report exactly
what it could not resolve without you.

**Onboarding a new source of truth** (a wiki export, a vendor's docs site) → `/docs:import`.

---

## 7. Troubleshooting

Codes come from the validator (`--json` prints them).

| Code | Severity | Means | Fix |
| --- | --- | --- | --- |
| `no-frontmatter` | ERROR | A concept doc has no `---` block. | `/docs:align`, or add the stamp by hand. |
| `broken-frontmatter` | ERROR | The `---` block opens but never closes. | Close it; re-run. |
| `missing-type` | ERROR | No non-empty `type`. | Pick the home's `type` (§2), or `/docs:align`. |
| `missing-<field>` | WARN | `title`/`description`/`resource`/`timestamp` absent. | Fill it — `resource` must be derived, never invented. |
| `index-has-type` | ERROR | An `index.md` carries a concept `type`. | Move that content into a real concept doc; keep the index a listing. |
| `index-has-frontmatter` | ERROR | A non-root `index.md` has any frontmatter. | Strip it. |
| `root-no-okf-version` · `root-okf-version-mismatch` · `root-extra-keys` | WARN | The root `index.md` frontmatter is wrong. | It carries **only** `okf_version: "0.1"`. |
| `dir-no-index` | WARN | A folder holds concept docs but has no front door. | `/docs:align` regenerates it. |
| `index-broken-link` | WARN | A listing points at a file that does not exist (a **lying index**). | `/docs:align`. |
| `index-orphan` | WARN | A concept doc nothing links to. | Add it to its folder's `index.md` — `/docs:align`. |
| `readme-not-index` | WARN | A `README.md` inside the bundle. | OKF reserves `index.md` as the listing — convert it. (`QUENCHING.md` is exempt and never flagged.) |
| `bundle-no-index` | WARN | The bundle root has no `index.md`. | `/docs:align`. |

The structural WARNs (`dir-no-index`, `index-broken-link`, `index-orphan`) do **not** fail
exit-0 — OKF tolerates them — but `/docs:align` treats them as must-fix in its own verify gate. A
bundle it leaves behind has none.

**The hook is noisy on generated docs.** Add their paths to `ignoreGlobs`.
**The hook fires on every turn.** Confirm `stopScan` is `"dirty"`.
**`--version` disagrees with the plugin.** Run `/docs:align` — step 6 offers the upgrade,
overwriting only the script and preserving your `hooks-config.json`.

---

## 8. The other fronts, and the real contract

`quenching` acts on three surfaces, each with its own align and its own manual:

| Front | Manual | Align (structure, one pass) | Align-and-update (+ content, looped) |
| --- | --- | --- | --- |
| `docs/` — this knowledge bundle | this file | `/docs:align` | `/docs:align-and-update` |
| `specs/` — the spec-driven plan workspace | `../specs/QUENCHING.md` | `/specs:align` | `/specs:align-and-update` |
| `.claude/` — the automation surface | `../.claude/QUENCHING.md` | `/skill:align` | `/skill:align-and-update` |

`/align` runs the three aligns in dependency order on one confirmation; `/align-and-update` runs
the three conductors the same way and loops across fronts, because they feed each other (a plan's
archive distils docs the glossary must then index). A front this repo does not use
simply has no manual.

The **normative** contract — the OKF spec, the taxonomy, the migration map, the exact conformance
checks — lives in the plugin's own `skills/*/references/*.md`, not here. This file is the
operator's view; that is the specification.
