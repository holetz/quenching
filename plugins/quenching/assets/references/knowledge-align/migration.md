# Migration — variant → canonical, with blast-radius safety

In an existing repo with variant names, `/quenching:knowledge:align` **proposes convergence to the canonical
name**.

## Contents

`cq components read assets/references/knowledge-align/migration.md` returns the heading index;
`--sections` addresses one.

## 1. Map variant → canonical

Each existing section matches a canonical home **by function**:

| Variant (examples) | Canonical |
| --- | --- |
| `docs/arquitetura/`, `docs/architecture-docs/` | `docs/standards/` (or `standards/architecture/` if only that) |
| `docs/adr/`, `docs/decisions` (ADRs) | `docs/standards/<subject>/` — restamp `type: decision` → `standard` (§1f) |
| `docs/backlog/`, `BACKLOG.md`, `docs/tarefas/` | `specs/` (leaves the bundle — §1e) |
| `VISION.md`, `ROADMAP.md`, `docs/direcao/` | `docs/vision/` |
| `docs/catalogo_dados/`, `docs/dominio/`, `docs/data/` | `docs/catalog/` |
| `docs/normativos/`, `docs/regulamentos/` | `docs/reference/regulations/` (content) |
| `docs/guias/`, `docs/howto/`, `docs/how-to/` | `docs/documentation/how-to/` |
| `docs/tutoriais/`, `docs/tutorials/`, `docs/getting-started/` | `docs/documentation/getting-started/` |
| `docs/documentacao/`, `docs/user-docs/`, `docs/site/`, `docs/manual/`, `docs/wiki/` | `docs/documentation/` |

### 1a. Subfolder-level map (inside `standards/`)

Convergence applies one level down — a variant **subfolder** is a smell too:
`codigo/`→`code/` · `modelagem/`→`data-modeling/` · `nomenclatura/`→`naming/` ·
`plataforma/`→`platform/` · `arquitetura/`→`architecture/` · `qualidade/`→`quality/` ·
`servicos/`→ the fitting subject (usually `platform/`, or split by content). The folder name +
frontmatter (keys, enums, and the `title:`/`description:` free-text on this agent-facing
surface) become canonical English. **A migration never translates body prose** — which language it
is written in is owned by the bundle's `docs/standards/agents/communication.md`.

### 1b. File-slug translation + prefix-cluster folding

Convergence reaches the **filename** too — a non-English concept-doc slug and a prefix-cluster
are both smells `/quenching:knowledge:align` resolves as renames (each swept for its blast radius, ⇒ §3–4).

- **Translate non-English slugs** on the technical homes (`standards/`, `vision/`,
  `documentation/`, `reference/` non-identifier) to canonical English describing the concept:
  `convencoes.md`→`conventions.md` · `hierarquia-tasks.md`→`task-hierarchy.md` ·
  `validacao-desenvolvimento.md`→`development-validation.md` · `notebooks-spark.md`→`spark-notebooks.md`.
- **Fold a prefix-cluster into a subfolder** (prefix stripped, English leaf names, generated
  `index.md`):

  ```
  standards/code/nomenclatura-classes.md      standards/code/symbol-naming/classes.md
  standards/code/nomenclatura-funcoes.md   →  standards/code/symbol-naming/functions.md
  standards/code/nomenclatura-modulos.md      standards/code/symbol-naming/modules.md
  standards/code/nomenclatura-variaveis.md    standards/code/symbol-naming/variables.md
  standards/code/nomenclatura-simbolos.md     standards/code/symbol-naming/symbols.md
  ```

- **Identifier-derived slugs are verbatim — never translate them.** A catalog `<schema>`/
  `<table>` mirrors the real object (`dim_associado.md` stays `dim_associado.md`);
  `reference/repositories/<repo>` mirrors the real repo. The
  slug is the greppable key to the asset — anglicizing it is data loss.

### 1c. Retired canonical home — `guides/` → `documentation/`

<!-- rules -->
OKF v0.9 retired the `guides/` home; its content now lives in the `documentation/` home. A repo
already conformant on the **old** canonical (`docs/guides/`) is therefore a migration candidate
too — not a variant name, but a retired home. Scaffold the `documentation/` skeleton (its
`index.md` + the four section listings + `.pages`), restamp `type: guide` → `type: documentation`,
and relocate each `docs/guides/**` doc **by shape** — per item, like Content relocation below,
because a legacy `guides/` folder mixes both quadrants: a **task recipe / how-to** ("how do I do
X") → `docs/documentation/how-to/`; a **learning-oriented tutorial** → `docs/documentation/getting-started/`.
Sweep the blast radius like any rename (its **own** confirmation when links reach product code).

<!-- rationale -->
Without this rule `align` would read a conformant `guides/` and never migrate it.

### 1d. Renamed backlog item — `idea` → `task`

<!-- rules -->
OKF v0.11 renamed the backlog item concept: a `backlog/*.md` carrying the legacy
`type: idea` restamps to `type: task` (same minimal stamp; the optional
`priority`/`tags` keys are NOT backfilled — an untriaged legacy item simply stays
untriaged). The backlog `index.md` heading **"Developed ledger" renames to "Completed
ledger"** with columns `Task | Outcome | Date` — **existing rows preserved** (map
`Idea` → `Task`, `Developed into` → `Outcome`). **No GENERATED zone is installed or regenerated
in it.** A legacy mold reference `backlog/idea.md` maps to `backlog/task.md`. This restamp applies
**before** the hand-off in §1e, while the files are still OKF-stamped task docs.

<!-- rationale -->
§1e moves this folder into the `specs/` front, which carries no listing file at all
(`cq specs list` derives what `plans/` holds from disk), so a zone written here would be a
listing nobody produces and nobody reads.

### 1e. Backlog leaves the OKF bundle — `docs/backlog/` → the `specs/` front

OKF v0.13 moved parked work out of the `docs/` bundle, and it now lands in the `specs/` front as
**specs**, not as OKF docs — `cq knowledge validate` no longer scans it, and a spec carries no OKF
`type:` at all.

The move is two hops, and this sweep performs only the first:

1. **`/quenching:knowledge:align` moves the files.** `/quenching:specs:align` scaffolds the `specs/` workspace if absent;
   then every `docs/backlog/*.md` moves into the **legacy `backlog/` folder inside `specs/`**,
   applying the `idea`→`task` restamp (§1d) on the way. That folder is a staging area for hop 2,
   not a destination. This is its **own** confirmation, blast-radius swept (§3–4): the move rewrites
   every cross-link into `docs/backlog/`.
2. **`cq specs migrate` converts them.** That legacy folder is exactly the tool's input: each task
   file becomes a **captured-stage spec** in `specs/plans/`, with its `priority` / `tags` /
   `complexity` preserved as a line in `## Problem`. Name that second hop in the report and let
   `/quenching:specs:align` run it — **never hand-convert a task into a spec here**, which would be this
   sweep authoring content.

After both hops, `/quenching:specs:create` and `/quenching:specs:triage` own that work.

### 1f. Retired home — `decisions/` → `standards/`

<!-- rules -->
OKF v0.13 removed the standalone ADR home. A target's existing `docs/decisions/*.md`
(`type: decision`, usually `NNNN-slug.md` ADRs) migrates by restamping `type: decision` →
`type: standard` with `authority: background` (or `current` if the decision is clearly
implemented in the code), and relocating to the fitting `standards/<subject>/` — naming the
concept in an English slug, dropping the `NNNN-` prefix. This is a **per-item
semantic-placement call with its own OK**, blast-radius swept (§3–4) — never a bulk move.

<!-- rationale -->
A decision's rationale and still-open alternatives belong in an OpenSpec change's `design.md`,
not a docs home.

### Content relocation (distinct from rename)

A doc filed under the **wrong subject** moves to its subject home — a job/task framework under
`code/` → `workflows/`; "code defines YAML" under `platform/` → `ci-cd/`. Relocation is a
**semantic placement** call: propose it **per item, with OK**, and measure the referrer blast
radius — never fold it into a bulk opt-in.

## 2. Flag the variant as DEPRECATABLE

A variant name enters the plan's migration list with its proposed canonical destination.

## 3. Measure and SURFACE the blast radius BEFORE executing

The procedure is the shared one in
[`align/sweep-doctrine.md`](${CLAUDE_PLUGIN_ROOT}/assets/references/align/sweep-doctrine.md)
§The blast-radius sweep. Never run a scan per rename.

**This front's delta:** a variant *path* is often load-bearing beyond `docs/` in a way a bare
name is not — path constants, imports, and **docstrings** all embed it — so the alternation is
built from full path fragments (`docs/arquitetura`), not just folder names, and a hit inside a
docstring counts as product code.

**Report the scope in the proposal:** how many files, which reach **code**, and which
non-`docs/` referrers (skills, `CLAUDE.md`, prose links) the rename will edit. The OK covers
exactly this **enumerated** set, shown in the proposal — never deferred to an after-the-fact
wrap-up.

## 4. Propose the migration; NEVER rename/delete without OK — code-coupled ⇒ its OWN confirmation

A migration whose blast radius reaches **product code**, or is otherwise irreversible, is a
**distinct confirmation item** with its scope shown — never folded into a bulk "align all"
opt-in. A rename that resolves to a code constant is a **refactor of the target's product**, not
a docs move: alert the user, never perform it silently. **Exception — cycle-authorized runs:** a run invoked as a stage of
`/quenching:knowledge:align`'s cycle (or of `/align`) under the cycle-authorization contract
([convergence.md §contract](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md)) replaces only the batch gate
with narration — a code-coupled rename still confirms on its own, always.

## 5. Frontmatter migration (field renames)

While aligning legacy docs, migrate field names to OKF (MERGE, never clobber):

- `summary:` → `description:`
- `updated:` → `timestamp:`
- add non-empty `type:` (from the home's vocabulary in [taxonomy.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-align/taxonomy.md))
- rename the retired type `type: guide` → `type: documentation` (§1c)
- rename the retired type `type: idea` → `type: task` (§1d; the files then leave the bundle per §1e)
- rename the retired type `type: decision` → `type: standard` (§1f; stamp `authority: background`, or `current` if implemented)
- normalize enums to canonical English (`authority: vigente` → `current`; `audience: ambos` → `both`)
- preserve third-party keys (a legacy `status:`, OKF-consumer keys, site-generator keys)
- convert each front-door `README.md` → `index.md` (strip its frontmatter; keep boundary +
  listing). The one `INDEX.md` of a standards layer becomes `standards/index.md` with the
  DERIVED `<!-- BEGIN/END GENERATED -->` zone.

## 6. Install only the missing canonical homes that apply

A repo without data does not receive `catalog/`; the baseline is completeness **of what
fits**, not a blind checklist. The same rule governs the **candidate sub-standards** one level
down: a consideration checklist, evidence-gated generation, recorded deferral.
