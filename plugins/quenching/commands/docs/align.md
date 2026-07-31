---
description: Force docs/ into the canonical OKF v0.1 bundle AND pull in the content sitting out-of-band — one command, probe first, looped to a fixpoint. Triggers on "align the docs", "align and update docs", "fix the documentation structure", "install the OKF bundle", "set up docs/", "converge the knowledge base". Probes okf-validate.py plus two cheap out-of-band signals before reading anything, so a conformant bundle with nothing waiting costs three calls and stops. Otherwise: one inventory, ONE plan, one OK, the structural pass, the content stages that have work (memory, harness), then the whole-bundle glossary sweep OFFERED on a cheap proxy — looping until a pass changes nothing. Conducts its stages by invoking them, never reimplements them. Not for: adding ONE doc → /docs:add; capturing ONE fact a human just stated → /docs:learn; ONE glossary term → /docs:define; importing an external source → /docs:import; reading the bundle without changing it → /docs:status; the mkdocs site layer → /docs:documentation:build.
argument-hint: [optional-docs-path]
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Task, Skill, AskUserQuestion
---

# /quenching:docs:align — force the knowledge base into OKF shape, and keep filling it

**Input**: `$ARGUMENTS` (optionally a `docs/` path or a scope; omit to align the whole bundle).

The **`docs/` front's one entry point**. It installs and enforces a single canonical OKF v0.1
bundle so every repo that adopts this plugin looks the same — **and** it pulls in the durable
content sitting outside the bundle (project memory, a fat harness) and backfills the glossary,
looping until a pass changes nothing.

Structure and content are one command because they are one dependency chain: nothing can be filed
into a tree that is not there, and a glossary swept before the content lands misses terms. Splitting
them cost an entry point and bought a second thing to remember to run.

The payload (skeleton, molds, validator) lives at `${CLAUDE_PLUGIN_ROOT}/assets/`; the contract at
`${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/`:

- [docs-align/okf-spec.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/okf-spec.md) — the normative OKF v0.1 rules (MUST/SHOULD/MAY).
- [docs-align/taxonomy.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/taxonomy.md) — the canonical tree, homes, `type` vocabulary, boundaries.
- [docs-align/migration.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/migration.md) — variant→canonical map + blast-radius doctrine.
- [docs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md) — the exact checks the validator applies.
- [docs-align/cycle.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/cycle.md) — the stage pipeline, the parallel-prep flow, and the finding → owning-command routing table.

The executable checker is `${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py`
(`python3 okf-validate.py <docs-dir>` → exit 0 = conforms). Invoke it by its **literal quoted
path** on every call, never through a shell variable holding the interpreter plus the path —
[specs-create/specs-front.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-create/specs-front.md)
§Write the resolved path literally on every invocation.

**Why `Bash` is unrestricted here.** The checker is invoked through `python3`, but a bundle-root
detection, a two-scan blast radius (`git grep` / `grep --no-ignore`), and a `.claude/settings.json`
merge are all shell work this command cannot do through a narrower grant.

## Doctrine (non-negotiable)

The sweep contract every align shares — probe before the inventory, convergence over
accommodation, one plan → one OK with code-coupled items gating individually, the cycle-authorized
narration exception, the two-scan blast-radius procedure, MERGE-never-clobber,
never-delete-on-a-guess, and align-conformance-report-the-cycle — lives once in
[align/sweep-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/sweep-doctrine.md).
Read it as this command's doctrine. What follows is only what is **specific to `docs/`**:

- **This is the one front with a real loop.** `docs/` has two out-of-band stores that feed it and a
  glossary derived from everything in it, so one pass genuinely creates work for the next: a fact
  the harness MOVEs in is a term the glossary must then index. The loop ends at a **fixpoint** —
  a pass that changed nothing with the validator clean — never after a fixed count, bounded by a
  pass cap and a no-progress guard
  ([convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md)).
- **Conduct the content stages, never reimplement them.** Steps 6–7 **invoke**
  `/quenching:docs:import-memory`, `/quenching:docs:harness` and `/quenching:docs:glossary-backfill` through the `Skill` tool
  under their registry names (`quenching:docs:import-memory`, …). Each runs under its own doctrine
  and its own code-coupled confirmations. If a stage's behaviour must change, change that command.
- **The expensive stage is offered, never assumed.** The glossary sweep reads the whole bundle, and
  no cheap signal proves it has work — so it is gated on a free proxy and **offered** with its cost
  (sweep-doctrine §Probe before the inventory). Everything else this command does is probed.
- **Per-item commands are stage tools, not stages.** `/quenching:docs:add`, `/quenching:docs:learn`, `/quenching:docs:define`
  each act on ONE item a human states, and a loop pass has no fresh human input — so they are never
  stages. They are what the stages already delegate to. A content gap only they can close is
  **surfaced** in the report, never fabricated.
- **Completeness of what fits, evidence-gated.** A repo without data gets no `catalog/`; a
  standard is generated only with observed `file:line` evidence; the rest is a recorded
  deferral, never a silent skip.
- **Folders over prefix-clusters.** When sibling files share a subject prefix
  (`nomenclatura-classes.md`, `nomenclatura-funcoes.md`, `nomenclatura-modulos.md`, …), that
  prefix **is** the subject and the repetition is the "filename repeats the folder" smell →
  promote the cluster into a subfolder (canonical English), strip the prefix, generate the
  folder's `index.md` (`code/symbol-naming/{classes,functions,modules,…}.md`). Keep flat files
  when a folder adds ceremony without aiding disclosure (a lone file, an incoherent prefix, two
  short siblings on an axis unlikely to grow). Favor the folder when it earns its keep, not by reflex.
- **English canonical surface — structure + frontmatter; content may be local.** Folder names
  **and concept-doc file slugs**, frontmatter keys, enum values, and the `type` vocabulary are
  canonical English, cross-repo greppable (`nomenclatura-variaveis.md` → `naming/variables.md`,
  `validacao-desenvolvimento.md` → `development-validation.md`). Frontmatter stays English; the
  **body prose MAY follow the repo's language** — only the content, never the surface.
  **Exception — identifier-derived names are verbatim, never translated:** a catalog
  `<schema>`/`<table>` slug mirrors the real object, `reference/repositories/<repo>` the real
  repo — anglicizing them would sever the greppable tie to the asset.

## Workflow (probe → ONE OK → pass → re-probe → loop)

### 1. Probe — the three reads that decide whether anything else runs
Resolve the bundle root (`docs/` or the repo's variant), then read all three signals and nothing
else:
```bash
okf-validate.py <docs> --json          # structure: exit 0 = conformant
ls ~/.claude/projects/<cwd>/memory/    # out-of-band store 1: any undrained memory?
```
plus one `Read` of each harness file that exists (`CLAUDE.md`, `AGENTS.md`) — a fat one inlines
durable knowledge; a thin one points. The glossary is **not** probed: it has no cheap signal, so
it is proxied in step 7 instead.

Branch as sweep-doctrine §Probe before the inventory prescribes:

| Probe result | What happens |
| --- | --- |
| validator exit 0 with no findings, memory dir empty, harness thin | **STOP.** Report "`docs/` conformant, N docs, nothing out-of-band, nothing to align" and end. No inventory, no plan, no confirmation. |
| exit 0 and the only findings are ones this command **surfaces** rather than closes (cycle.md's routing table, rightmost column `No`) | STOP the same way, then list them with the command that closes each. |
| any signal shows work | Continue to step 2. |

**No bundle at all** (no `index.md` / `okf_version`) is not a failure — it is the
install case, and step 4 scaffolds it.
**Done when:** the three signals are in hand and the run has either stopped or committed to a pass.

### 2. Inventory + map → the alignment plan (read-only)
Detect the existing sections, which docs carry frontmatter, and match each section to a canonical
home via the variant→canonical map
([docs-align/migration.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/migration.md)) —
top-level (`arquitetura/`→`standards/`) and subfolder (`codigo/`→`code/`). Read
[docs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md) and
route every probe finding to its owner via
[docs-align/cycle.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/cycle.md)'s table. Produce
the plan — enumerate:
  - **(a)** homes to scaffold (only those that apply), **plus the operator manual**
    `<docs>/QUENCHING.md` — install / refresh / leave, per the rule in step 4;
  - **(b)** variants to migrate/rename (with per-item destination);
  - **(b2)** **prefix-clusters to fold into subfolders** (`nomenclatura-*` siblings → a
    `symbol-naming/` folder, prefix stripped) — one folder per coherent cluster; note the ones
    kept flat and why;
  - **(b3)** **non-English slugs to translate** — every concept-doc file slug on a technical home
    that is not canonical English, with its English target (`convencoes.md` → `conventions.md`);
    leave identifier-derived names (catalog tables, repo names) verbatim;
  - **(c)** misfiled docs to relocate (semantic placement, per item);
  - **(d)** frontmatter to stamp/normalize — add non-empty `type`, migrate `summary:`→
    `description:` and `updated:`→`timestamp:`, normalize enums to canonical English;
  - **(e)** `index.md` files to (re)generate (reserved listings) — **one per directory that
    holds concept docs** (the `dir-no-index` set from the checker), plus any `index.md` that
    wrongly carries frontmatter, or `README.md` to convert to `index.md`;
  - **(f)** the **blast radius** of every code-coupled rename (a slug translation or a
    cluster-fold is a rename — sweep its references like any other);
  - **(g)** **which content stages will run this pass** — memory (dir non-empty), harness (fat),
    each with its count. A stage the probe found empty is skipped, not run to confirm it is empty.

On a later pass, re-derive only what the previous pass could have changed; never re-inventory a
converged half of the bundle.
**Done when:** one plan enumerates (a)–(g), with a per-item destination and a scope per rename.

### 3. Present the full plan → gate on ONE OK
Show the whole plan, including which content stages will run and the pass cap the OK authorizes:
*"this authorizes up to `<cap>` passes over the stages below; any item that touches product code
still pauses for its own confirmation, always."*

For each variant rename, sweep references per sweep-doctrine §The blast-radius sweep and **report
the scope**: how many files, which reach **product code**, which non-`docs/` referrers (commands,
`CLAUDE.md`, prose links) the rename edits. When the rename set is more than a handful, delegate
the mechanical collection to **one read-only `Task` sub-agent** (`model: haiku`, `effort: low`)
returning `rename → [file:line, …]` and classify each hit yourself. The batch OK covers exactly the
enumerated docs-only set. Each **code-coupled** rename is its **own** confirmation item.

This gate runs **once per run**, before pass 1 — later passes narrate their plan and do not re-ask
([convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md)
§cycle-authorization).
**Done when:** one OK covers the batch, or each code-coupled item was answered on its own, or the
plan was rejected and nothing was written.

### 4. Execute the structural pass (invasive)
- **Scaffold** missing homes from `${CLAUDE_PLUGIN_ROOT}/assets/docs/` (copy the applicable
  `index.md` listings **and any `.pages` nav sidecars**, e.g. `documentation/**`; adapt boundary
  lines to the repo). When scaffolding `knowledge/`, also copy
  its **fixed `glossary.md` seed** — the repo's A–Z term lookup — and list it in
  `knowledge/index.md` (it is the only pre-seeded concept doc the skeleton ships).
- **Install the operator manual** — copy `${CLAUDE_PLUGIN_ROOT}/assets/docs/QUENCHING.md` to
  `<docs>/QUENCHING.md`, replacing the banner's `<VERSION>` placeholder with the plugin's
  `VERSION` file. **This is the manual-install rule the other two fronts cite** (`/quenching:specs:align`,
  `/quenching:skill:align`) — same four branches, their own asset and destination:
  - **absent** → install;
  - **present, banner stamp older than the plugin** → overwrite (nothing repo-specific is lost —
    the manual is static payload);
  - **present, banner stamp same or newer** → leave it, silently;
  - **present, no `quenching` banner** → a human took it over: **keep it verbatim** and
    report it. Never clobber.
  The manual is **exempt** from OKF ([docs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md)) —
  never stamp it, never convert it to `index.md`. List it in the root `index.md` (this step's
  regeneration) so it is reachable from the bundle's front door.
- **Migrate** variants: move the folder, update every cross-ref found in step 3 (relative
  within a home, absolute `/docs/...` across homes).
- **Stamp/merge** frontmatter with the molds in `${CLAUDE_PLUGIN_ROOT}/assets/templates/`
  (`standard-front.md` for standards, `concept-front.md` otherwise).
- **Regenerate** every `index.md` deterministically — **one for every directory that holds
  concept docs** (create the missing ones the `dir-no-index` check reports; a subject folder,
  a freshly folded cluster, and a catalog schema dir all get a front door). Each listing links
  its real children (no `dir-no-index`, no `index-broken-link`, no `index-orphan` left behind);
  strip stray frontmatter; for `standards/index.md` rebuild only the
  `<!-- BEGIN/END GENERATED -->` zone from disk.
- **Write** `okf_version: "0.1"` into the root `docs/index.md` frontmatter.
- **Never create a `log.md`, and never touch one that is already there.** The artifact is
  retired: the name stays reserved so a surviving log is recognized rather than flagged, and
  whether to keep or delete it is the target repo's call, not this sweep's.

**Done when:** every approved (a)–(f) item is on disk and no unapproved item was touched.

### 5. Install the hook, the language declaration and the site layer — pass 1 only, offered
All three are one-shot scaffolding, not loop stages; skip this step entirely on later passes.

**The enforcement hook.** Offer to copy **exactly**
`${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py` + `hooks-config.json` into the target's
`.claude/hooks/` (never the directory recursively), and merge `settings.snippet.json` into
`.claude/settings.json` (`PostToolUse` + `Stop` propose; opt-in `PreToolUse` hard-block via
`hardBlock: true`). Set `docsDir` if the bundle root is not `docs/`.

**Ask the tool for the state; never hand-compare a version here.** One call answers installed,
shipped and wired at once:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/assets/bin/skills.py" drift --json
```

Read this front's row (`okf-validate.py`) and act on its `status`: `behind` → offer to overwrite
**only the script**, never `hooks-config.json`, which holds the target's own knobs; `ahead` → leave
it alone and **say so** — the target is ahead of this plugin, a fact to state rather than a
regression to force; `absent` → the install offer above. A `sk-tool-unwired` finding is the one the
script cannot fix by being copied: the file is on disk and no `hooks` block invokes it, so offer
the `settings.snippet.json` merge even though the version is current. See
[hooks/README.md](${CLAUDE_PLUGIN_ROOT}/assets/hooks/README.md).

**The language declaration.** Ask **once**, and only when the target's **root** harness file
(`CLAUDE.md` / `AGENTS.md`) carries no declaration yet. Ask for one BCP-47 tag — `pt-BR`, `en`,
`ja` — and write a single line into that root file:

    Language: <tag> — the contract is docs/standards/agents/communication.md

That line carries **a value and a citation, and nothing else**: never a paraphrase of the rule, and
never a second configuration key. The rule itself belongs to
`docs/standards/agents/communication.md`, which the structural pass (step 4) has already put on
disk — so the citation resolves the moment it is written.

**Declining is a complete answer.** A repo that declares nothing is under no constraint, and
nothing becomes non-conformant for it. Never infer a tag from the prose already sitting in the
bundle, never write the line into a nested harness file — only the root one is in context at
session start, which is the whole reason this form was chosen — and on a repo that already declares
one, read it and move on rather than asking again.

**The mkdocs site.** Only if the bundle has a `documentation/` home. Offer to copy from
`${CLAUDE_PLUGIN_ROOT}/assets/mkdocs/`: `mkdocs.yml.tmpl` → the repo **root** as `mkdocs.yml`
**only if absent** (never clobber a customized one — show a diff and let the user merge), filling
`site_name`/`site_description`; `requirements.txt` → repo root; on request, `ci-github-pages.yml` →
`.github/workflows/docs.yml` (opt-in, platform-specific). The `.pages` nav files ship **with** the
`documentation/` skeleton (step 4), so nav needs no separate install.

This is the **first install only**. The site layer's owner is `/quenching:docs:documentation:build`: every
later update, nav regeneration, config merge, and build verification is **its** job. If the install
is anything more than stamping two absent files — a customized `mkdocs.yml` to merge, a `docs_dir`
pointing elsewhere, `.pages` files no longer matching the tree — hand off to that command instead of
resolving it here.
**Done when:** the three offers have been made once and answered, or the pass is >1 and this step
was skipped.

### 6. Run the content stages that have work, in order
Invoke each through the `Skill` tool under its **registry name** — `quenching:docs:import-memory`,
`quenching:docs:harness`. Three citation forms exist, and which one is correct depends on **where
the command comes from**, never on who reads it: `quenching:docs:harness` is what the `Skill` tool
resolves; `/quenching:docs:harness` is what a human types wherever this is installed as a plugin;
the bare form `/<front>:<verb>`, carrying no plugin prefix, resolves **only** where that command
file lives in the target repo's own `.claude/commands/`. Declare the cycle-authorization mode to each
([convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md)
§cycle-authorization), and **skip any stage the probe found empty**:

1. `quenching:docs:import-memory` — drain the project's memory dir into its homes, clearing each
   memory once its doc lands and passes conformance.
2. `quenching:docs:harness` — thin `CLAUDE.md`/`AGENTS.md`, MOVEing durable knowledge into homes.

The order and the reason for it are
[docs-align/cycle.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/cycle.md) §The stage
pipeline's, not this body's. When **both** have work this pass, follow its §Parallel prep —
harness's read-only discovery runs in a background `Task` agent while the drain executes inline.
**Writes to `docs/` are one stage at a time, always.**

Record what each stage reports it changed; the loop decision in step 8 reads it.
**Done when:** each non-empty stage has run and reported, or every stage was empty and skipped.

### 7. Offer the glossary sweep — never automatic
Read the free proxy: the count of concept docs in the bundle against the number of entries in
`knowledge/glossary.md`, plus whether steps 4 and 6 created any docs this pass. A bundle that grew
and a glossary that did not is the signal.

Offer `quenching:docs:glossary-backfill` with what it costs (a whole-bundle sweep, fanned out per
home) and what the proxy shows. Use **AskUserQuestion** when the answer is a plain yes/no. A
declined offer is a complete answer — record it and do not re-offer on a later pass of the same
run. Never run the sweep to discover whether it had work.
**Done when:** the offer has been made once per run and answered, or the proxy showed no gap and
the offer was deliberately not made.

### 8. Verify, then decide: loop or stop
Re-run `okf-validate.py <docs> --json` and confirm: every non-reserved doc has frontmatter and a
non-empty `type`; every `index.md` is frontmatter-free (root only `okf_version`); and the
**structural-integrity WARNs are cleared — zero `dir-no-index`, `index-broken-link`,
`index-orphan`** (these are WARN, so exit 0 alone does not prove them clean — inspect the
findings).

Then re-run step 1's probe — never the step 2 inventory — and decide by the four outcomes in
[convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md)
§The convergence contract: **progress** → another pass from step 2 under the same OK, narrating its
plan; **converged** → step 9; **residue** → stop and report; **pass cap reached** → stop and report
what remains. The guards there (pass cap, no-progress, never-widen-scope) apply unchanged.

Re-probing rather than re-inventorying is what keeps a second pass cheap — and it is the same three
signals, so a stage that emptied itself this pass is simply absent from the next.
**Done when:** the run has converged, hit residue, or hit the cap — and which one is recorded.

### 9. Report
Summarize the whole run: N passes, what each stage did across all of them, the final validator
state, and — explicitly — what was **deliberately not closed**, each with the command that closes
it (per-item content needing human input, unroutable harness facts, deferred sub-standards, a
declined glossary sweep).

**The report is the record.** This step used to also append a closing entry to `docs/log.md`;
that artifact is retired, and the sweep leaves no trace of itself in the bundle. What the pass
did to `docs/` is legible from `docs/` and from the repo's own history — a self-describing
entry added nothing a reader could not already see, and cost a write on every run.
**Done when:** the report names the residue with its owning command.

## Invariants to never violate
- Never inventory before the probe, and never run a stage to find out whether it had work — the
  one stage with no cheap signal is **offered**, not entered.
- Never put a concept `type` on an `index.md`; never leave a concept doc without one.
- Never invent a `resource:` — derive it as a **glob set** of what the doc governs (standards) or
  the asset URI (catalog/reference); empty is disallowed, and self-pointing (`resource-self`) is
  too, except a bundle-level aggregate like `knowledge/glossary.md`.
- Never delete or rename without OK; code-coupled renames get their own confirmation. A slug
  translation and a cluster-fold are renames — same rule. A cycle-authorized run replaces only the
  batch gate with narration — never a code-coupled item's own OK, and never widens to product code.
- Never translate an **identifier-derived** slug (catalog table/schema, repo name) — it mirrors
  a real asset; anglicizing it breaks the greppable tie.
- Never leave a directory that holds concept docs without an `index.md`, and never leave a
  listing that links to a nonexistent file (a lying index).
- Never hand-edit a `<!-- BEGIN/END GENERATED -->` zone — regenerate it from disk.
- Never stamp, rename, or OKF-validate `QUENCHING.md`, and never overwrite one whose
  `quenching` banner a human removed — keep it and report it.
- Never reimplement a content stage's logic here — **invoke** it, and never let two stages write
  `docs/` concurrently.
- Never author content to close a gap that needs human input — **surface** it with its per-item
  command, never fabricate a standard, a concept, or a term.
- Never loop past the pass cap, never re-run a no-progress pass, and never treat validator exit 0
  alone as converged.
