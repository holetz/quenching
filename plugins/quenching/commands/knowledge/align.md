---
description: Force /.knowledge/ into the canonical OKF v0.1 bundle AND pull in the content sitting out-of-band — one command, probe first, looped to a fixpoint. Triggers on "align the docs", "align and update docs", "fix the documentation structure", "install the OKF bundle", "set up /.knowledge/", "converge the knowledge base". Probes cq knowledge validate plus two cheap out-of-band signals before reading anything. Otherwise: one inventory, ONE plan, one OK, the structural pass, the content stages that have work (memory, harness), then the whole-bundle glossary sweep OFFERED on a cheap proxy — looping until a pass changes nothing. Conducts its stages by invoking them, never reimplements them. Not for: adding one knowledge item → /quenching:knowledge:add; reading status only → /quenching:knowledge:status.
argument-hint: [optional-docs-path]
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Task, Skill, AskUserQuestion
---

# /quenching:knowledge:align — force the knowledge base into OKF shape, and keep filling it

**Input**: `$ARGUMENTS` (optionally a `/.knowledge/` path or a scope; omit to align the whole bundle).

The **`docs` front's one entry point**. It installs and enforces a single canonical OKF v0.1
bundle so every repo that adopts this plugin looks the same — **and** it pulls in the durable
content sitting outside the bundle (project memory, a fat harness) and backfills the glossary,
looping until a pass changes nothing.

The payload (skeleton, molds, validator) lives at `${CLAUDE_PLUGIN_ROOT}/assets/`; the contract at
`${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-align/`:

- [knowledge-align/okf-spec.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-align/okf-spec.md) — the normative OKF v0.1 rules (MUST/SHOULD/MAY).
- [knowledge-align/taxonomy.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-align/taxonomy.md) — the canonical tree, homes, `type` vocabulary, boundaries.
- [knowledge-align/migration.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-align/migration.md) — variant→canonical map + blast-radius doctrine.
- [knowledge-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-align/conformance.md) — the exact checks the validator applies.
- [knowledge-align/cycle.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-align/cycle.md) — the stage pipeline, the parallel-prep flow, and the finding → owning-command routing table.

The executable checker is `${CLAUDE_PLUGIN_ROOT}/assets/bin/cq`
(`python3 "${CLAUDE_PLUGIN_ROOT}/assets/bin/cq" knowledge validate /.knowledge` → exit 0 = conforms). Invoke it by its **literal quoted
path** on every call, never through a shell variable holding the interpreter plus the path —
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Write the resolved path literally on every invocation.

## Doctrine (non-negotiable)

Read [align/sweep-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/sweep-doctrine.md).
What follows is specific to `/.knowledge/`:

- **This is the one front with a real loop.** `/.knowledge/` has two out-of-band stores that feed it and a
  glossary derived from everything in it, so one pass genuinely creates work for the next: a fact
  the harness MOVEs in is a term the glossary must then index. The loop ends at a **fixpoint** —
  a pass that changed nothing with the validator clean — never after a fixed count, bounded by a
  pass cap and a no-progress guard
  ([convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md)).
- **Conduct the content stages, never reimplement them.** Steps 6–7 **invoke**
  `/quenching:knowledge:import-memory`, `/quenching:components:harness:align` and `/quenching:knowledge:glossary-backfill` through the `Skill` tool
  under their registry names (`quenching:knowledge:import-memory`, …). Each runs under its own doctrine
  and its own code-coupled confirmations. If a stage's behaviour must change, change that command.
- **The expensive stage is offered, never assumed.** The glossary sweep reads the whole bundle, and
  no cheap signal proves it has work — so it is gated on a free proxy and **offered** with its cost
  (sweep-doctrine §Probe before the inventory). Everything else this command does is probed.
- **Per-item commands are stage tools, not stages.** `/quenching:knowledge:add`, `/quenching:knowledge:learn`, `/quenching:knowledge:define`
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
  `<schema>`/`<table>` slug mirrors the real object, `external/repositories/<repo>` the real
  repo — anglicizing them would sever the greppable tie to the asset.

## Workflow (probe → ONE OK → pass → re-probe → loop)

### 1. Probe — the three reads that decide whether anything else runs
Resolve the bundle at its fixed root `/.knowledge/`, then read all three signals and nothing
else:
```bash
cq knowledge validate /.knowledge --json          # structure: exit 0 = conformant
ls ~/.claude/projects/<cwd>/memory/    # out-of-band store 1: any undrained memory?
```
plus one `Read` of each harness file that exists (`CLAUDE.md`, `AGENTS.md`) — a fat one inlines
durable knowledge; a thin one points. The glossary is **not** probed: it has no cheap signal, so
it is proxied in step 7 instead.

Branch as sweep-doctrine §Probe before the inventory prescribes:

| Probe result | What happens |
| --- | --- |
| validator exit 0 with no findings, memory dir empty, harness thin | **STOP.** Report "`/.knowledge/` conformant, N docs, nothing out-of-band, nothing to align" and end. No inventory, no plan, no confirmation. |
| exit 0 and the only findings are ones this command **surfaces** rather than closes (cycle.md's routing table, rightmost column `No`) | STOP the same way, then list them with the command that closes each. |
| any signal shows work | Continue to step 2. |

**No bundle at all** (no `index.md` / `okf_version`) is not a failure — it is the
install case, and step 4 scaffolds it.
**Done when:** the three signals are in hand and the run has either stopped or committed to a pass.

### 2. Inventory + map → the alignment plan (read-only)
When `$ARGUMENTS` names a home or subtree, keep the fixed-root probe whole-bundle but restrict this
inventory, plan, and structural write set to that scope; report out-of-scope findings without touching
them. With no argument, use the whole bundle.
Detect the existing sections, which docs carry frontmatter, and match each section to a canonical
home via the variant→canonical map
([knowledge-align/migration.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-align/migration.md)) —
top-level (`arquitetura/`→`standards/`) and subfolder (`codigo/`→`code/`). Read
[knowledge-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-align/conformance.md) and
route every probe finding to its owner via
[knowledge-align/cycle.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-align/cycle.md)'s table. Produce
the plan — enumerate:
  - **(a)** homes to scaffold (only those that apply);
  - **(a2)** pre-rename plugin-layout sites to migrate (`okf-legacy-root`/`-home`/`-doc-quadrant`/
    `-glossary` findings) — the bundle root, a home, a `documentation/` quadrant, or the glossary
    still sitting under a name a plugin release retired; resolved via
    [knowledge-align/migration.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-align/migration.md)
    §1g, each swept for blast radius like any other rename (f);
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
the scope**: how many files, which reach **product code**, which non-`/.knowledge/` referrers (commands,
`CLAUDE.md`, prose links) the rename edits. When the rename set is more than a handful, delegate
the mechanical collection to **one read-only `Task` sub-agent** (`model: haiku`, `effort: low`)
returning `rename → [file:line, …]` and classify each hit yourself. The batch OK covers exactly the
enumerated docs-only set. Each **code-coupled** rename is its **own** confirmation item.

This gate runs **once per run**, before pass 1 — later passes narrate their plan and do not re-ask
([convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md)
§The cycle-authorization contract).
**Done when:** one OK covers the batch, or each code-coupled item was answered on its own, or the
plan was rejected and nothing was written.

### 4. Execute the structural pass (invasive)
- **Scaffold** missing homes from `${CLAUDE_PLUGIN_ROOT}/assets/knowledge/` (copy the applicable
  `index.md` listings **and any `.pages` nav sidecars**, e.g. `documentation/**`; adapt boundary
  lines to the repo). When scaffolding `concepts/`, also copy
  its **fixed `glossary.md` seed** — the repo's A–Z term lookup — to the bundle root, and list it in
  `concepts/index.md` (it is the only pre-seeded concept doc the skeleton ships).
- **Migrate** variants: move the folder, update every cross-ref found in step 3 (relative
  within a home, absolute `/.knowledge/...` across homes).
- **Resolve `okf-legacy-*` sites** ([migration.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-align/migration.md)
  §1g): `git mv` the root/home/quadrant/glossary to its canonical name, root first, then repoint
  every code-coupled reference the blast-radius sweep found (a path default, a docstring, a hook's
  own root constant) — each such site is its **own** confirmation from step 3, never folded into
  the batch OK.
- **Stamp/merge** frontmatter with the molds in `${CLAUDE_PLUGIN_ROOT}/assets/templates/`
  (`standard-front.md` for standards, `concept-front.md` otherwise).
- **Regenerate** every `index.md` deterministically — **one for every directory that holds
  concept docs** (create the missing ones the `dir-no-index` check reports; a subject folder,
  a freshly folded cluster, and a catalog schema dir all get a front door). Each listing links
  its real children (no `dir-no-index`, no `index-broken-link`, no `index-orphan` left behind);
  strip stray frontmatter; for `standards/index.md` rebuild only the
  `<!-- BEGIN/END GENERATED -->` zone from disk.
- **Write** `okf_version: "0.1"` into the root `/.knowledge/index.md` frontmatter.
- **Never create a `log.md`, and never touch one that is already there.**

**Done when:** every approved (a)–(f) item is on disk and no unapproved item was touched.

### 5. Install the language declaration and the site layer — pass 1 only, offered
Both are one-shot scaffolding, not loop stages; skip this step entirely on later passes.

**The language declaration.** Ask **once**, and only when the target's **root** harness file
(`CLAUDE.md` / `AGENTS.md`) carries no declaration yet. Ask for one BCP-47 tag — `pt-BR`, `en`,
`ja` — and write a single line into that root file:

    Language: <tag> — the contract is /.knowledge/standards/agents/communication.md

That line carries **a value and a citation, and nothing else**: never a paraphrase of the rule, and
never a second configuration key. The rule itself belongs to
`/.knowledge/standards/agents/communication.md`, which the structural pass (step 4) has already put on
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

This is the **first install only**. The site layer's owner is `/quenching:knowledge:documentation:build`: every
later update, nav regeneration, config merge, and build verification is **its** job. If the install
is anything more than stamping two absent files — a customized `mkdocs.yml` to merge, a `docs_dir`
pointing elsewhere, `.pages` files no longer matching the tree — hand off to that command instead of
resolving it here.
**Done when:** the two offers have been made once and answered, or the pass is >1 and this step
was skipped.

### 6. Run the content stages that have work, in order
Invoke each through the `Skill` tool under its **registry name** — `quenching:knowledge:import-memory`,
`quenching:components:harness:align`. Which of the three citation forms is correct, and the condition on each,
is [sweep-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/sweep-doctrine.md) §7. Citing a command. Declare the cycle-authorization mode to each
([convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md)
§The cycle-authorization contract), and **skip any stage the probe found empty**:

1. `quenching:knowledge:import-memory` — drain the project's memory dir into its homes, clearing each
   memory once its doc lands and passes conformance.
2. `quenching:components:harness:align` — thin `CLAUDE.md`/`AGENTS.md`, MOVEing durable knowledge into homes.

The order and the reason for it are
[knowledge-align/cycle.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-align/cycle.md) §The stage
pipeline's, not this body's. When **both** have work this pass, follow its §Parallel prep —
harness's read-only discovery runs in a background `Task` agent while the drain executes inline.
**Writes to `/.knowledge/` are one stage at a time, always.**

Record what each stage reports it changed; the loop decision in step 8 reads it.
**Done when:** each non-empty stage has run and reported, or every stage was empty and skipped.

### 7. Offer the glossary sweep — never automatic
Read the free proxy: the count of concept docs in the bundle against the number of entries in
`glossary.md`, plus whether steps 4 and 6 created any docs this pass. A bundle that grew
and a glossary that did not is the signal.

Offer `quenching:knowledge:glossary-backfill` with what it costs (a whole-bundle sweep, fanned out per
home) and what the proxy shows. Use **AskUserQuestion** when the answer is a plain yes/no. A
declined offer is a complete answer — record it and do not re-offer on a later pass of the same
run. Never run the sweep to discover whether it had work.
**Done when:** the offer has been made once per run and answered, or the proxy showed no gap and
the offer was deliberately not made.

### 8. Verify, then decide: loop or stop
Re-run `cq knowledge validate /.knowledge --json` and confirm: every non-reserved doc has frontmatter and a
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

**The report is the record.** The sweep leaves no trace of itself in the bundle.
**Done when:** the report states the final convergence outcome and names any residue with its owning
command, or explicitly states that no residue remains.

## Invariants to never violate
- Never inventory before the probe, and never run a stage to find out whether it had work — the
  one stage with no cheap signal is **offered**, not entered.
- Never put a concept `type` on an `index.md`; never leave a concept doc without one.
- Never invent a `resource:` — derive it as a **glob set** of what the doc governs (standards) or
  the asset URI (catalog/external); empty is disallowed, and self-pointing (`resource-self`) is
  too, except a bundle-level aggregate like `glossary.md`.
- Never delete or rename without OK; code-coupled renames get their own confirmation. A slug
  translation and a cluster-fold are renames — same rule. A cycle-authorized run replaces only the
  batch gate with narration — never a code-coupled item's own OK, and never widens to product code.
- Never translate an **identifier-derived** slug (catalog table/schema, repo name) — it mirrors
  a real asset; anglicizing it breaks the greppable tie.
- Never leave a directory that holds concept docs without an `index.md`, and never leave a
  listing that links to a nonexistent file (a lying index).
- Never hand-edit a `<!-- BEGIN/END GENERATED -->` zone — regenerate it from disk.
- Never reimplement a content stage's logic here — **invoke** it, and never let two stages write
  `/.knowledge/` concurrently.
- Never author content to close a gap that needs human input — **surface** it with its per-item
  command, never fabricate a standard, a concept, or a term.
- Never loop past the pass cap, never re-run a no-progress pass, and never treat validator exit 0
  alone as converged.
