# Migration — variant → canonical, with blast-radius safety

In an existing repo with variant names, `quenching-align` **proposes convergence to the canonical
name** — deterministic and prescriptive, but **safe**. Deterministic ≠ automatic: the mapping
is repeatable, but each migration passes its **own** confirmation, and a code-coupled rename is
a distinct item.

## 1. Map variant → canonical

Each existing section matches a canonical home **by function**:

| Variant (examples) | Canonical |
| --- | --- |
| `docs/arquitetura/`, `docs/architecture-docs/` | `docs/standards/` (or `standards/architecture/` if only that) |
| `docs/adr/`, `docs/decisions` (as ADRs) | `docs/decisions/` |
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
surface) become canonical English; the **body prose MAY stay in the repo's language**.

### 1b. File-slug translation + prefix-cluster folding

Convergence reaches the **filename** too — a non-English concept-doc slug and a prefix-cluster
are both smells `quenching-align` resolves as renames (each swept for its blast radius, ⇒ §3–4).

- **Translate non-English slugs** on the technical homes (`standards/`, `decisions/`, `vision/`,
  `backlog/`, `documentation/`, `reference/` non-identifier) to canonical English describing the concept:
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
  `reference/repositories/<repo>` mirrors the real repo; an ADR keeps its `NNNN-` prefix. The
  slug is the greppable key to the asset — anglicizing it is data loss.
- **Content is content — only the surface converges.** Body prose may be Portuguese; the slug,
  folder, and frontmatter are English.

### 1c. Retired canonical home — `guides/` → `documentation/`

OKF v0.9 retired the `guides/` home; its content now lives in the `documentation/` home. A repo
already conformant on the **old** canonical (`docs/guides/`) is therefore a migration candidate
too — not a variant name, but a retired home. Scaffold the `documentation/` skeleton (its
`index.md` + the four section listings + `.pages`), restamp `type: guide` → `type: documentation`,
and relocate each `docs/guides/**` doc **by shape** — per item, like Content relocation below,
because a legacy `guides/` folder mixes both quadrants: a **task recipe / how-to** ("how do I do
X") → `docs/documentation/how-to/`; a **learning-oriented tutorial** → `docs/documentation/getting-started/`.
Sweep the blast radius like any rename (its **own** confirmation when links reach product code).
Without this rule `align` would read a conformant `guides/` and never migrate it.

### 1d. Renamed backlog item — `idea` → `task`

OKF v0.11 renamed the backlog item concept: a `backlog/*.md` carrying the legacy
`type: idea` restamps to `type: task` (same home, same minimal stamp; the optional
`priority`/`tags` keys are NOT backfilled — an untriaged legacy item simply stays
untriaged). The backlog `index.md` heading **"Developed ledger" renames to "Completed
ledger"** with columns `Task | Outcome | Date` — **existing rows preserved** (map
`Idea` → `Task`, `Developed into` → `Outcome`). The DERIVED
`<!-- BEGIN/END GENERATED -->` zone is installed/regenerated (align already regenerates
every `index.md`); an index that predates the markers gains them without touching the
fixed prose around them. A legacy mold reference `backlog/idea.md` maps to
`backlog/task.md`.

### Content relocation (distinct from rename)

A doc filed under the **wrong subject** moves to its subject home — a job/task framework under
`code/` → `workflows/`; "code defines YAML" under `platform/` → `ci-cd/`. Relocation is a
**semantic placement** call: propose it **per item, with OK**, and measure the referrer blast
radius — never fold it into a bulk opt-in.

## 2. Flag the variant as DEPRECATABLE

A variant name enters the plan's migration list with its proposed canonical destination.

## 3. Measure and SURFACE the blast radius BEFORE executing

A variant path is often **load-bearing beyond `docs/`**. Sweep for **every** reference — not
only `docs/` cross-links, but **product code** (path constants, imports, **docstrings**) and
**gitignored-but-live maps**:

```bash
git grep -n "docs/arquitetura"                 # tracked files
grep -rn --no-ignore "docs/arquitetura" .      # includes gitignored; ripgrep-aliased grep silently skips them
```

**Report the scope in the proposal:** how many files, which reach **code**, and which
non-`docs/` referrers (skills, `CLAUDE.md`, prose links) the rename will edit. The OK covers
exactly this **enumerated** set, shown in the proposal — never deferred to an after-the-fact
wrap-up.

## 4. Propose the migration; NEVER rename/delete without OK — code-coupled ⇒ its OWN confirmation

Human confirmation and "do not delete without OK" remain in effect. A migration whose blast
radius reaches **product code**, or is otherwise irreversible, is a **distinct confirmation
item** with its scope shown — never folded into a bulk "align all" opt-in. A rename that
resolves to a code constant is a **refactor of the target's product**, not a docs move: alert
the user, never perform it silently. **Exception — cycle-authorized runs:** a run invoked by
`quenching-cycle` under its cycle-authorization contract
([cycle.md §contract](../../quenching-cycle/references/cycle.md)) replaces only the batch gate
with narration — a code-coupled rename still confirms on its own, always.

## 5. Frontmatter migration (field renames)

While aligning legacy docs, migrate field names to OKF (MERGE, never clobber):

- `summary:` → `description:`
- `updated:` → `timestamp:`
- add non-empty `type:` (from the home's vocabulary in [taxonomy.md](taxonomy.md))
- rename the retired type `type: guide` → `type: documentation` (its home moved to `documentation/`)
- rename the retired type `type: idea` → `type: task` (the backlog item concept was renamed in v0.11 — see §1d)
- normalize enums to canonical English (`authority: vigente` → `current`; `audience: ambos` → `both`)
- preserve third-party keys (a legacy `status:`, OKF-consumer keys, site-generator keys)
- convert each front-door `README.md` → `index.md` (strip its frontmatter; keep boundary +
  listing). The one `INDEX.md` of a standards layer becomes `standards/index.md` with the
  DERIVED `<!-- BEGIN/END GENERATED -->` zone.

## 6. Install only the missing canonical homes that apply

A repo without data does not receive `catalog/`; the baseline is completeness **of what
fits**, not a blind checklist. The same rule governs the **candidate sub-standards** one level
down: a consideration checklist, evidence-gated generation, recorded deferral.
