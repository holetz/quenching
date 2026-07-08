# Documentation Home + MkDocs Site Setup — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `documentation/` home to the OKF bundle (Diátaxis product docs), fusing the retired `guides/` home into `documentation/how-to/`, and ship a batteries-included mkdocs-material site setup that `quenching-align` installs.

**Architecture:** This repo has **no application code and no test framework** — it is markdown "skills" (doctrine a future Claude executes) plus one stdlib-only Python validator. The "tests" are therefore (1) `python3 assets/hooks/okf-validate.py assets/docs` reporting `0 error(s), 0 warning(s)`, and (2) `grep` sweeps proving no live `guides/` / `type: guide` / `"guide"` reference survives except intentional migration/changelog mentions. The change is doctrine edits + a new skeleton home + a new `assets/mkdocs/` payload. Implement **on top of the current working tree** (base = the uncommitted "backlog-idea" feature).

**Tech Stack:** Markdown (OKF v0.1), YAML frontmatter, Python 3 (stdlib validator), MkDocs + Material + `mkdocs-awesome-pages-plugin`.

**Spec:** [docs/superpowers/specs/2026-07-08-documentation-home-design.md](../specs/2026-07-08-documentation-home-design.md)

## Global Constraints

- **Version: 0.9.0 combined** with the parallel "backlog-idea" feature. `plugins/claude-quenching/VERSION` and `.claude-plugin/plugin.json` are **already `0.9.0`** in the working tree — **DO NOT re-bump**. The hook's `--version` string in `assets/hooks/okf-validate.py` must stay in lockstep (`0.9.0`).
- **Base = current working tree**, NOT `HEAD`. The tree already contains uncommitted backlog-idea edits (`type: backlog-item`→`idea`, `taxonomy.md`, `okf-spec.md`, `concept-front.md`, README, etc.) and untracked skills (`quenching-enrich/`, `quenching-visualize/`, `assets/tools/`). Your `guide`→`documentation` edits land on the **same enum lines** backlog-idea already touched. Never revert a backlog-idea change.
- **Do not disturb the pre-staged rename** `assets/templates/backlog/backlog-item.md → idea.md` (it is staged in the index). Commit only your own paths per task (`git add <explicit paths>`), never `git add -A`.
- **Branch:** `feature/documentation-home` (already checked out; the spec commit is `HEAD`).
- **One `type` per home:** every page under `documentation/**` carries `type: documentation`. `type: guide` is retired.
- **OKF canonical surface is English** (folder names, slugs, frontmatter keys, `type`); body prose may be local.
- **`index.md` is a reserved, frontmatter-free listing**; it must list its real children (no `dir-no-index`, `index-orphan`, `index-broken-link`). `.pages` files are YAML, not `.md`, and are invisible to the validator.
- **Skill `description` frontmatter cap: 1536 chars**; keep skill bodies < 500 lines.
- **Never** add `context: fork` to any skill. **Never** downgrade `quenching-memory-to-docs` classifier/executor sub-agents to `haiku`.
- **Frequent commits:** one commit per task, message prefix `feat:`/`docs:`.
- **Validator command (run from `plugins/claude-quenching/`):** `python3 assets/hooks/okf-validate.py assets/docs` → must end with `0 error(s), 0 warning(s)`.

> **OPEN DECISION (surface to the user, do not silently change):** the spec picked `mkdocs-awesome-pages-plugin` (config via `.pages`). Context7 shows a maintained successor, `mkdocs-awesome-nav` (config via `.nav.yml`), by the same author. This plan implements **awesome-pages** as specced (stable, widely used). If the user prefers the successor, only Task 1's `.pages` files and Task 8's `mkdocs.yml`/`requirements.txt` change.

---

## File Structure

**Create (new home skeleton — `plugins/claude-quenching/assets/docs/documentation/`):**
- `index.md` + `.pages` — home front door + nav order
- `getting-started/index.md` + `getting-started/.pages`
- `how-to/index.md` + `how-to/.pages`
- `reference/index.md` + `reference/.pages`
- `concepts/index.md` + `concepts/.pages`

**Create (mkdocs payload — `plugins/claude-quenching/assets/mkdocs/`):**
- `mkdocs.yml.tmpl` — Material config mold (stamped at target repo root)
- `requirements.txt` — mkdocs-material + awesome-pages
- `ci-github-pages.yml` — optional GitHub Pages workflow
- `README.md` — what the payload is + how align stamps it

**Delete:**
- `plugins/claude-quenching/assets/docs/guides/` (its `index.md`)

**Edit (doctrine + wiring):** `taxonomy.md`, `okf-spec.md`, `migration.md`, `concept-front.md`, `homes.md`, `assets/docs/index.md`, `assets/docs/knowledge/index.md`, `assets/docs/communications/index.md`, `quenching-align/SKILL.md`, `quenching-insert/SKILL.md`, `quenching-knowledge/SKILL.md`, `quenching-knowledge-scan/SKILL.md`, `harness-routing.md`, `memory-routing.md`, `quenching-enrich/references/sources.md`, `quenching-visualize/references/viz.md`, `assets/tools/okf-visualize.py`, `README.md`, `.claude-plugin/plugin.json` (keywords only).

All paths below are relative to `plugins/claude-quenching/` unless noted. Run all `python3`/`grep` commands from that directory.

---

### Task 1: Create the `documentation/` home skeleton; delete `guides/`

**Files:**
- Create: `assets/docs/documentation/index.md`, `.pages`
- Create: `assets/docs/documentation/{getting-started,how-to,reference,concepts}/index.md` + `.pages`
- Delete: `assets/docs/guides/index.md`

**Interfaces:**
- Produces: the canonical `documentation/` tree consumed by every later doctrine task and by the mkdocs setup (Task 8). Section slugs are **exactly** `getting-started`, `how-to`, `reference`, `concepts`.

- [ ] **Step 1: Capture the baseline (validator must be clean BEFORE the change)**

Run: `python3 assets/hooks/okf-validate.py assets/docs`
Expected: ends with `0 error(s), 0 warning(s)` (the shipped skeleton is conformant by construction). If not clean, stop — something else is wrong.

- [ ] **Step 2: Write `assets/docs/documentation/index.md`**

```markdown
# `documentation/` — product documentation (Diátaxis, renderable site)

Prose documentation written for a human reader, structured as a Diátaxis site — the pages
you publish with a static-site generator. Absorbs the former `guides/` home. Each page
carries `type: documentation`.

**Boundary:** a page you would put on the published documentation site (narrative, for a
human) lives here; structured/typed knowledge for the team+agent to operate lives in the
other homes.

- vs. [knowledge/](/docs/knowledge/index.md) — a published-site explanation page →
  `concepts/`; internal team understanding (mental model, learning, glossary) → `knowledge/`.
- vs. [standards/](/docs/standards/index.md) — a how-to that describes the current
  *contract* (the rule) is a `standard`; teaching how to *execute* a task is a how-to here.
- vs. the root [reference/](/docs/reference/index.md) — our product's own reference lives in
  `reference/` below; facts about an external asset WE CONSUME go to the root `reference/` home.

## Sections (Diátaxis)

* [getting-started/](getting-started/index.md) — tutorials: learning-oriented, "get it running"
* [how-to/](how-to/index.md) — task-oriented recipes (the former `guides/`)
* [reference/](reference/index.md) — reference for our own product / API
* [concepts/](concepts/index.md) — explanation: how and why, for the site's reader

## Rendering this home

This home is a plain Markdown tree, consumable by any documentation site generator. The
plugin ships a batteries-included **mkdocs-material** setup that `quenching-align` installs
at the repo root (`mkdocs.yml`, `requirements.txt`):

- The generator points here — `docs_dir: docs/documentation` in `mkdocs.yml` (kept at the
  repo root, **outside** the bundle).
- Each reserved `index.md` doubles as the **section landing page** (mkdocs-material's
  `navigation.indexes` feature) — no separate landing file needed.
- Navigation follows the folder tree automatically via `mkdocs-awesome-pages-plugin`; the
  `.pages` file in each section sets its title and order.
- **Link caveat:** absolute OKF links (`/docs/standards/…`) point outside a site rooted at
  `documentation/` and will not resolve in the built HTML — keep these pages self-contained
  and cross-link to other homes sparingly.
```

- [ ] **Step 3: Write `assets/docs/documentation/.pages`**

```yaml
title: Documentation
nav:
  - index.md
  - getting-started
  - how-to
  - reference
  - concepts
  - ...
```

- [ ] **Step 4: Write the four section `index.md` files**

`assets/docs/documentation/getting-started/index.md`:

```markdown
# `getting-started/` — tutorials

Learning-oriented pages that carry a newcomer from zero to a first success with the product
(the Diátaxis **tutorial** quadrant). Each page carries `type: documentation`.

**Boundary:** a tutorial *teaches by doing* (a guided lesson); a recipe for someone who
already knows the product is a [how-to](../how-to/index.md); an explanation of how something
works is a [concept](../concepts/index.md).

## How to organize

The repo decides which tutorials exist — the skeleton ships none. Standalone pages live as
`.md` files here; group a coherent multi-page track into a subfolder with its own `index.md`.
One concept per file, kebab-case English slug; the folder carries the subject, so the
filename does not repeat it.
```

`assets/docs/documentation/how-to/index.md`:

```markdown
# `how-to/` — task recipes

Task-oriented pages that answer "how do I do X" for someone using the product (the Diátaxis
**how-to** quadrant). This section absorbs the former `guides/` home. Each page carries
`type: documentation`.

**Boundary:** a how-to gets a known task done for a user who already knows the basics; a
guided first lesson is a [tutorial](../getting-started/index.md); the current internal *rule*
for how WE build is a [standard](/docs/standards/index.md), not a how-to.

## How to organize

The repo decides which recipes exist — the skeleton ships none. Standalone pages live as
`.md` files here; group a coherent set into a subfolder with its own `index.md`. One concept
per file, kebab-case English slug.
```

`assets/docs/documentation/reference/index.md`:

```markdown
# `reference/` — product reference

Information-oriented pages describing our own product's surface — commands, API, options,
configuration (the Diátaxis **reference** quadrant). Each page carries `type: documentation`.

**Boundary:** this is reference for **our** product, aimed at its users. Facts about an
**external** asset WE CONSUME (a named tool / library / regulation) belong to the root
[reference/](/docs/reference/index.md) home, not here — the two are different homes at
different paths.

## How to organize

The repo decides what reference exists — the skeleton ships none. Standalone pages live as
`.md` files here; group by product area into subfolders with their own `index.md`.
```

`assets/docs/documentation/concepts/index.md`:

```markdown
# `concepts/` — explanation

Understanding-oriented pages that explain how and why the product works, for the reader of
the documentation site (the Diátaxis **explanation** quadrant). Each page carries
`type: documentation`.

**Boundary:** a concept page here is part of the **published site** for product users.
Internal team understanding — mental models, learnings, the glossary — is not a site page and
belongs in [knowledge/](/docs/knowledge/index.md).

## How to organize

The repo decides which concept pages exist — the skeleton ships none. Standalone pages live
as `.md` files here; group by subject into subfolders with their own `index.md`.
```

- [ ] **Step 5: Write the four section `.pages` files**

`assets/docs/documentation/getting-started/.pages`:
```yaml
title: Getting started
```
`assets/docs/documentation/how-to/.pages`:
```yaml
title: How-to guides
```
`assets/docs/documentation/reference/.pages`:
```yaml
title: Reference
```
`assets/docs/documentation/concepts/.pages`:
```yaml
title: Concepts
```

- [ ] **Step 6: Delete the retired `guides/` skeleton**

```bash
git rm assets/docs/guides/index.md
rmdir assets/docs/guides 2>/dev/null || true
```

- [ ] **Step 7: Run the validator — must still be clean**

Run: `python3 assets/hooks/okf-validate.py assets/docs`
Expected: `0 error(s), 0 warning(s)`. The new `documentation/index.md` lists its four real children; each child dir has an `index.md`; no orphan/broken-link/dir-no-index. `.pages` files are ignored (non-`.md`).

- [ ] **Step 8: Confirm `.pages` are invisible to the validator**

Run: `python3 assets/hooks/okf-validate.py assets/docs --json | python3 -c "import sys,json; d=json.load(sys.stdin); print([f for f in d.get('findings',[]) if '.pages' in str(f)])"`
Expected: `[]` (no finding mentions a `.pages` file). If `--json` shape differs, instead run `python3 assets/hooks/okf-validate.py assets/docs --json | grep -c '.pages'` → expected `0`.

- [ ] **Step 9: Commit**

```bash
git add assets/docs/documentation assets/docs/guides
git commit -m "feat: add documentation/ home skeleton, retire guides/ skeleton"
```

---

### Task 2: Doctrine tree — `taxonomy.md`

**Files:**
- Modify: `skills/quenching-align/references/taxonomy.md`

**Interfaces:**
- Consumes: the section slugs from Task 1.
- Produces: the canonical-tree definition every other skill cites.

- [ ] **Step 1: Swap the tree line (remove `guides/`, add `documentation/`)**

Replace:
```
  guides/                      # how-to + tutorials — subject subfolders (type: guide)
```
with:
```
  documentation/               # product docs (Diátaxis prose) — getting-started/ how-to/ reference/ concepts/ (type: documentation)
```

- [ ] **Step 2: Swap the `type`-table row**

Replace:
```
| `guides/` | `guide` | subject subfolders |
```
with:
```
| `documentation/**` | `documentation` | `getting-started/`·`how-to/`·`reference/`·`concepts/` |
```

- [ ] **Step 3: Replace the `guides/` "one by one" bullet**

Replace:
```
- **`guides/`** — how-to + tutorials (`type: guide`); the repo organizes them (subject
  subfolders welcome; audience silos like `onboarding/` are not).
```
with:
```
- **`documentation/`** — prose documentation for human readers, Diátaxis-structured; the
  home rendered as the product's documentation site (`type: documentation`). Four fixed
  subfolders: `getting-started/` (tutorial), `how-to/` (task recipes — absorbs the former
  `guides/`), `reference/` (our product's own reference), `concepts/` (explanation).
  Boundary: a published-site page → here; internal team understanding → `knowledge/`; a
  current contract → `standards/`. `audience: human`, `authority: current` by default. The
  plugin ships a mkdocs-material site setup (config + awesome-pages nav) that
  `quenching-align` installs at the repo root.
```

- [ ] **Step 4: Fix the `knowledge/` bullet's procedure cross-reference**

In the `knowledge/` bullet, replace `(→ \`guides/\`)` with `(→ \`documentation/how-to/\`)` (the phrase reads "…and **not** a procedure (→ `guides/`)").

- [ ] **Step 5: Add a `documentation/` line to the "Boundary rules" summary**

In the `## Boundary rules (memorable summary)` list, after the `knowledge/` line add:
```
- `documentation/` = "**prose docs for humans**, Diátaxis-structured (the published site)".
```

- [ ] **Step 6: Verify no live `guides` reference remains in this file**

Run: `grep -n "guides\|type: guide\|\`guide\`" skills/quenching-align/references/taxonomy.md`
Expected: only the intentional mention "absorbs the former `guides/`" (Step 3). No tree line, no type row, no bullet defining `guides/` as a home.

- [ ] **Step 7: Commit**

```bash
git add skills/quenching-align/references/taxonomy.md
git commit -m "docs: taxonomy — replace guides/ home with documentation/"
```

---

### Task 3: Type vocabulary — `okf-spec.md` + `concept-front.md`

**Files:**
- Modify: `skills/quenching-align/references/okf-spec.md`
- Modify: `assets/templates/concept-front.md`

**Interfaces:**
- Consumes: `type: documentation` from Task 2.
- Note: both lines were already edited by backlog-idea (they now contain `idea`). Change only the `guide` token.

- [ ] **Step 1: `okf-spec.md` — swap `guide` for `documentation` in the vocabulary list**

Replace:
```
  `table`, `decision`, `vision`, `idea`, `guide`, `knowledge`, `reference`,
```
with:
```
  `table`, `decision`, `vision`, `idea`, `documentation`, `knowledge`, `reference`,
```

- [ ] **Step 2: `concept-front.md` — swap `guide` for `documentation` in the type hint**

Replace:
```
type: <REQUIRED — the concept kind; pick the home's type from references/homes.md, e.g. standard|decision|vision|idea|guide|knowledge|reference|system|schema|table|communication|sidecar>
```
with:
```
type: <REQUIRED — the concept kind; pick the home's type from references/homes.md, e.g. standard|decision|vision|idea|documentation|knowledge|reference|system|schema|table|communication|sidecar>
```

- [ ] **Step 3: Verify**

Run: `grep -n "\`guide\`\|idea|guide\|vision', 'guide" skills/quenching-align/references/okf-spec.md assets/templates/concept-front.md`
Expected: no matches for `guide` as a standalone type token.

- [ ] **Step 4: Commit**

```bash
git add skills/quenching-align/references/okf-spec.md assets/templates/concept-front.md
git commit -m "docs: type vocabulary — guide -> documentation"
```

---

### Task 4: Insert routing — `homes.md`

**Files:**
- Modify: `skills/quenching-insert/references/homes.md`

**Interfaces:**
- Consumes: `documentation` type + section slugs.
- Produces: the routing every insert-capable skill (`insert`, `knowledge`, `harness`, `memory-to-docs`) cites.

- [ ] **Step 1: Replace the how-to/tutorial classification row with three documentation rows**

Replace:
```
| a **how-to / tutorial** | `guides/` | `guide` | `concept-front.md` | `<subject>/<slug>.md` |
```
with:
```
| a **how-to / task recipe** (product usage) | `documentation/how-to/` | `documentation` | `concept-front.md` | `how-to/<slug>.md` |
| a **tutorial** (learning-oriented) | `documentation/getting-started/` | `documentation` | `concept-front.md` | `getting-started/<slug>.md` |
| **product reference / explanation** (site page) | `documentation/{reference,concepts}/` | `documentation` | `concept-front.md` | `<section>/<slug>.md` |
```

- [ ] **Step 2: Add a documentation-vs-knowledge tie-breaker**

In `### Boundary tie-breakers`, after the `knowledge vs its neighbors` bullet, insert:
```
- **documentation vs knowledge:** a **published-site page** (narrative, for a human reading
  the docs) is `documentation/`; **internal team understanding** (mental model, learning,
  glossary) is `knowledge/`. Explanation that ships on the site → `documentation/concepts/`;
  explanation the team holds internally → `knowledge/`.
```

- [ ] **Step 3: Fix the "set of steps is a guide" phrase in the knowledge tie-breaker**

Replace `a set of steps is a\n  \`guide\`.` context — specifically replace:
```
a fact about a **named** external dependency is `reference`; a set of steps is a
  `guide`. When understanding hardens into a rule, it distills into `standards/` and leaves
```
with:
```
a fact about a **named** external dependency is `reference`; a set of steps for using the
  product is a `documentation` how-to. When understanding hardens into a rule, it distills
  into `standards/` and leaves
```

- [ ] **Step 4: Fix the "communications vs guides/presentations" tie-breaker**

Replace:
```
- **communications vs guides/presentations:** a **dated message to an audience** is a
  `communication`; a **how-to** is a `guide`; a **visual binary** is a `sidecar` under
  `presentations/`.
```
with:
```
- **communications vs documentation/presentations:** a **dated message to an audience** is a
  `communication`; a **how-to** is a `documentation` page; a **visual binary** is a `sidecar`
  under `presentations/`.
```

- [ ] **Step 5: Verify**

Run: `grep -n "guide\|guides/" skills/quenching-insert/references/homes.md`
Expected: no matches (all routes now say `documentation`).

- [ ] **Step 6: Commit**

```bash
git add skills/quenching-insert/references/homes.md
git commit -m "docs: insert routing — route how-to/tutorial to documentation/"
```

---

### Task 5: Index listings — root, knowledge, communications

**Files:**
- Modify: `assets/docs/index.md`
- Modify: `assets/docs/knowledge/index.md`
- Modify: `assets/docs/communications/index.md`

**Interfaces:**
- These are reserved `index.md` listings — no frontmatter (except the root's `okf_version`). Must stay validator-clean.

- [ ] **Step 1: Root `assets/docs/index.md` — swap the homes bullet**

Replace:
```
* [guides/](/docs/guides/index.md) — how-to + tutorials
```
with:
```
* [documentation/](/docs/documentation/index.md) — product docs site (Diátaxis: getting-started, how-to, reference, concepts)
```

- [ ] **Step 2: `assets/docs/knowledge/index.md` — replace the "vs guides/" boundary bullet**

Replace:
```
- vs. [guides/](/docs/guides/index.md) — guides teach **how to do X** (procedure);
  knowledge explains **what X is / why** (understanding). If it is a set of steps, it
  is a guide.
```
with:
```
- vs. [documentation/](/docs/documentation/index.md) — documentation is the published,
  human-facing product site (how-to, tutorials, product reference/concepts); knowledge is
  internal team understanding. If it is a page for the docs site, it is documentation.
```

- [ ] **Step 3: `assets/docs/communications/index.md` — fix the cross-link**

Replace:
```
distinct from [guides/](/docs/guides/index.md) (how-to), [decisions/](/docs/decisions/index.md)
```
with:
```
distinct from [documentation/](/docs/documentation/index.md) (how-to), [decisions/](/docs/decisions/index.md)
```

- [ ] **Step 4: Validate**

Run: `python3 assets/hooks/okf-validate.py assets/docs`
Expected: `0 error(s), 0 warning(s)`. (The root now links `documentation/index.md`, which exists from Task 1; no broken link.)

- [ ] **Step 5: Commit**

```bash
git add assets/docs/index.md assets/docs/knowledge/index.md assets/docs/communications/index.md
git commit -m "docs: index listings — point guides/ links at documentation/"
```

---

### Task 6: Migration doctrine — `migration.md`

**Files:**
- Modify: `skills/quenching-align/references/migration.md`

- [ ] **Step 1: Expand the top-level variant map**

Replace:
```
| `docs/guias/`, `docs/howto/`, `docs/tutorials/` | `docs/guides/` |
```
with:
```
| `docs/guias/`, `docs/howto/`, `docs/how-to/` | `docs/documentation/how-to/` |
| `docs/tutoriais/`, `docs/tutorials/`, `docs/getting-started/` | `docs/documentation/getting-started/` |
| `docs/documentacao/`, `docs/user-docs/`, `docs/site/`, `docs/manual/`, `docs/wiki/` | `docs/documentation/` |
```

- [ ] **Step 2: Fix the translate-slugs home list**

Replace:
```
- **Translate non-English slugs** on the technical homes (`standards/`, `decisions/`, `vision/`,
  `backlog/`, `guides/`, `reference/` non-identifier) to canonical English describing the concept:
```
with:
```
- **Translate non-English slugs** on the technical homes (`standards/`, `decisions/`, `vision/`,
  `backlog/`, `documentation/`, `reference/` non-identifier) to canonical English describing the concept:
```

- [ ] **Step 3: Add the retired-canonical-home rule after §1b**

Immediately before `### Content relocation (distinct from rename)`, insert:
```
### 1c. Retired canonical home — `guides/` → `documentation/how-to/`

OKF v0.9 retired the `guides/` home; its content now lives in `documentation/how-to/`. A repo
already conformant on the **old** canonical (`docs/guides/`) is therefore a migration candidate
too — not a variant name, but a retired home. Relocate `docs/guides/**` → `docs/documentation/how-to/**`,
restamp `type: guide` → `type: documentation`, scaffold the `documentation/` skeleton (its
`index.md` + the four section listings + `.pages`), and sweep the blast radius like any rename
(its **own** confirmation when links reach product code). Without this rule `align` would read a
conformant `guides/` and never migrate it.
```

- [ ] **Step 4: Add the type rename to §5 (frontmatter migration)**

In `## 5. Frontmatter migration (field renames)`, after the `add non-empty \`type:\`` line, insert:
```
- rename the retired type `type: guide` → `type: documentation` (its home moved to `documentation/how-to/`)
```

- [ ] **Step 5: Verify**

Run: `grep -n "guides/\|type: guide" skills/quenching-align/references/migration.md`
Expected: only intentional mentions — the `docs/guias/` variant source, the §1c heading/body ("retired the `guides/` home", "`docs/guides/**`"), and the §5 rename line. No mapping that treats `docs/guides/` as a live canonical destination.

- [ ] **Step 6: Commit**

```bash
git add skills/quenching-align/references/migration.md
git commit -m "docs: migration — variant map + retired guides/ -> documentation/how-to/ rule"
```

---

### Task 7: `quenching-align/SKILL.md` — description + new mkdocs install step

**Files:**
- Modify: `skills/quenching-align/SKILL.md`

**Interfaces:**
- Produces: the align workflow step that installs the mkdocs payload created in Task 8. References `${CLAUDE_PLUGIN_ROOT}/assets/mkdocs/`.

- [ ] **Step 1: Update the frontmatter `description` homes list**

In the `description:` block, replace `standards/ decisions/ vision/ backlog/\n  guides/ knowledge/ reference/ catalog/ communications/ presentations/` so `guides/` becomes `documentation/`:

Replace:
```
  conformance", "migrate docs/ to the standard", "make docs/ OKF-compliant", "organize
  docs/ into the canonical tree", or when docs/ has variant names / missing frontmatter /
  a lying index. Installs the canonical homes (standards/ decisions/ vision/ backlog/
  guides/ knowledge/ reference/ catalog/ communications/ presentations/), migrates
```
with:
```
  conformance", "migrate docs/ to the standard", "make docs/ OKF-compliant", "organize
  docs/ into the canonical tree", or when docs/ has variant names / missing frontmatter /
  a lying index. Installs the canonical homes (standards/ decisions/ vision/ backlog/
  documentation/ knowledge/ reference/ catalog/ communications/ presentations/), migrates
```

Then confirm the description is still ≤ 1536 chars: `python3 -c "import re,sys; t=open('skills/quenching-align/SKILL.md').read(); m=re.search(r'description: >-\n(.*?)\nwhen_to_use:', t, re.S); print(len(' '.join(m.group(1).split())))"` → expect a number ≤ 1536 (swap is length-neutral: `documentation/` vs `guides/` adds 7 chars — still well under).

- [ ] **Step 2: Insert the mkdocs-setup step between the hook step (6) and the diagram step (7)**

The workflow currently ends with `### 6. Wire the enforcement hook …` then `### 7. Offer the diagram (optional)`. Insert a new step and renumber the diagram to 8. Insert **before** `### 7. Offer the diagram (optional)`:

```
### 7. Offer the mkdocs site setup (optional)
If the bundle has a `documentation/` home, offer to install the batteries-included
**mkdocs-material** site setup so the product docs render as a site. Copy from
`${CLAUDE_PLUGIN_ROOT}/assets/mkdocs/`:
- `mkdocs.yml.tmpl` → the repo **root** as `mkdocs.yml` **only if absent** (never clobber a
  customized one — show a diff and let the user merge); fill `site_name`/`site_description`.
- `requirements.txt` → repo root (or merge its two lines into an existing docs-requirements).
- On request, `ci-github-pages.yml` → `.github/workflows/docs.yml` (opt-in; platform-specific).
The `.pages` nav files ship **with** the `documentation/` skeleton (Step 4), so nav needs no
separate install and no regeneration. See [../../assets/mkdocs/README.md](../../assets/mkdocs/README.md).
```

- [ ] **Step 3: Renumber the diagram step**

Change `### 7. Offer the diagram (optional)` to `### 8. Offer the diagram (optional)`.

- [ ] **Step 4: Verify**

Run: `grep -n "guides/\|### 7\|### 8" skills/quenching-align/SKILL.md`
Expected: description says `documentation/` (no `guides/`); two numbered headings `### 7. Offer the mkdocs site setup` and `### 8. Offer the diagram`.

- [ ] **Step 5: Commit**

```bash
git add skills/quenching-align/SKILL.md
git commit -m "feat: align — install mkdocs site setup; homes list guides -> documentation"
```

---

### Task 8: MkDocs payload — `assets/mkdocs/`

**Files:**
- Create: `assets/mkdocs/mkdocs.yml.tmpl`, `assets/mkdocs/requirements.txt`, `assets/mkdocs/ci-github-pages.yml`, `assets/mkdocs/README.md`

**Interfaces:**
- Consumes: `docs_dir: docs/documentation` and the `.pages` nav from Task 1.
- Produces: the payload `quenching-align` Step 7 (Task 7) stamps into a target repo.

- [ ] **Step 1: Write `assets/mkdocs/mkdocs.yml.tmpl`**

```yaml
# mkdocs.yml — Material for MkDocs config for the OKF `documentation/` home.
# quenching-align stamps this at the repo ROOT (outside docs/). Fill the <placeholders>.
site_name: "<YOUR PROJECT> — Documentation"
site_description: "<one-line description of the product docs>"
# site_url: https://<org>.github.io/<repo>/   # set for correct canonical/social links

docs_dir: docs/documentation

theme:
  name: material
  features:
    - navigation.indexes    # index.md is each section's landing page (matches the OKF reserved index)
    - navigation.sections
    - navigation.top
    - content.code.copy
    - search.suggest

plugins:
  - search
  - awesome-pages           # nav follows the folder tree via .pages files (shipped in the home)

markdown_extensions:
  - admonition
  - toc:
      permalink: true
  - pymdownx.superfences
```

- [ ] **Step 2: Write `assets/mkdocs/requirements.txt`**

```
mkdocs-material>=9.5
mkdocs-awesome-pages-plugin>=2.9
```

- [ ] **Step 3: Write `assets/mkdocs/ci-github-pages.yml`**

```yaml
# Copy to .github/workflows/docs.yml to publish the site to GitHub Pages on push to main.
name: docs
on:
  push:
    branches: [main]
permissions:
  contents: write
jobs:
  build-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.x"
      - run: pip install -r requirements.txt
      - run: mkdocs gh-deploy --force
```

- [ ] **Step 4: Write `assets/mkdocs/README.md`**

```markdown
# `assets/mkdocs/` — the site setup payload (mkdocs-material)

Inert here, like the rest of `assets/`. `quenching-align` (Step 7) stamps these into a target
repo so the `documentation/` home renders as a site. **The OKF markdown stays generator-neutral;
only this config layer is mkdocs-specific.**

| File | Stamped to | Notes |
| --- | --- | --- |
| `mkdocs.yml.tmpl` | repo root `mkdocs.yml` | only if absent; fill `site_name`/`site_description`; `docs_dir: docs/documentation` |
| `requirements.txt` | repo root | `mkdocs-material` + `mkdocs-awesome-pages-plugin` |
| `ci-github-pages.yml` | `.github/workflows/docs.yml` | opt-in; GitHub Pages via `mkdocs gh-deploy` |

Nav needs no file here — the `.pages` files ship inside `assets/docs/documentation/**` and the
`awesome-pages` plugin builds the nav from the folder tree.

## Build locally

```bash
pip install -r requirements.txt
mkdocs serve      # live preview at http://127.0.0.1:8000
mkdocs build      # static site into ./site
```

`index.md` in each section is the section landing page (`navigation.indexes`). Absolute OKF
links (`/docs/…`) to other homes will not resolve in a site rooted at `docs/documentation/` —
keep `documentation/` pages self-contained.
```

- [ ] **Step 5: Verify the YAML parses**

Run:
```bash
python3 -c "import yaml,sys" 2>/dev/null && for f in assets/mkdocs/mkdocs.yml.tmpl assets/mkdocs/ci-github-pages.yml; do python3 -c "import yaml;yaml.safe_load(open('$f'))" && echo "OK $f"; done || echo "PyYAML not present — skip (validated at build time)"
```
Expected: `OK assets/mkdocs/mkdocs.yml.tmpl` and `OK assets/mkdocs/ci-github-pages.yml` (or the skip message if PyYAML is absent).

- [ ] **Step 6: Smoke-test a real build (only if `mkdocs` is installed)**

Run:
```bash
command -v mkdocs >/dev/null && { \
  T=$(mktemp -d); mkdir -p "$T/docs"; cp -r assets/docs/documentation "$T/docs/documentation"; \
  sed 's/<YOUR PROJECT>/Smoke Test/; s/<one-line.*>/Smoke test/' assets/mkdocs/mkdocs.yml.tmpl > "$T/mkdocs.yml"; \
  ( cd "$T" && pip install -q -r "$OLDPWD/assets/mkdocs/requirements.txt" && mkdocs build --strict ) && echo "BUILD OK"; rm -rf "$T"; \
} || echo "mkdocs not installed — build test deferred (documented in assets/mkdocs/README.md)"
```
Expected: `BUILD OK`, or the "mkdocs not installed" message. If installed and it fails on `--strict`, read the error (commonly a nav/link warning) and fix the config before committing.

- [ ] **Step 7: Commit**

```bash
git add assets/mkdocs
git commit -m "feat: ship mkdocs-material site setup payload (config, nav deps, CI, README)"
```

---

### Task 9: Remaining wiring sweep

**Files:**
- Modify: `skills/quenching-insert/SKILL.md`, `skills/quenching-knowledge/SKILL.md`, `skills/quenching-knowledge-scan/SKILL.md`, `skills/quenching-harness/references/harness-routing.md`, `skills/quenching-memory-to-docs/references/memory-routing.md`, `skills/quenching-enrich/references/sources.md`, `skills/quenching-visualize/references/viz.md`, `assets/tools/okf-visualize.py`

- [ ] **Step 1: `quenching-insert/SKILL.md` — English-slug home list**

Replace `\`standards/\`·\`decisions/\`·\`vision/\`·\`backlog/\`·\`guides/\`·\`reference/\`` so `guides/` becomes `documentation/`:
```
  English on `standards/`·`decisions/`·`vision/`·`backlog/`·`documentation/`·`reference/` (as are
```

- [ ] **Step 2: `quenching-knowledge/SKILL.md` — two mentions**

Replace `Contracts, decisions, guides,` with `Contracts, decisions, documentation,`.
Replace `an open decision is an ADR; a set of steps is a \`guide\`; a` with `an open decision is an ADR; a set of steps for using the product is \`documentation\`; a`.

- [ ] **Step 3: `quenching-knowledge-scan/SKILL.md` — home-slice list**

In the slice list, replace `\`backlog/\`, \`guides/\`, \`knowledge/\`` with `\`backlog/\`, \`documentation/\`, \`knowledge/\`` (grep the exact line first: `grep -n "guides/" skills/quenching-knowledge-scan/SKILL.md`).

- [ ] **Step 4: `harness-routing.md` — two mentions**

Replace `| step-by-step procedure / onboarding | **MOVE** | \`guides/\` (\`guide\`) |` with `| step-by-step procedure / onboarding | **MOVE** | \`documentation/how-to/\` (\`documentation\`) |`.
Replace `a\n**procedure** → \`guides/\`; Don't duplicate` — specifically the text `a\n**procedure** → \`guides/\`.` becomes `a\n**procedure** → \`documentation/how-to/\`.` (the sentence "…**direction** → `vision/`; a **procedure** → `guides/`. Don't duplicate them here").

- [ ] **Step 5: `memory-routing.md` — three mentions (out-of-scope home label)**

Replace `\`vision/\`, \`guides/\`, \`reference/\`` with `\`vision/\`, \`documentation/\`, \`reference/\``.
Replace `\`standards/workflows/\`, else \`knowledge/\` (no \`guides/\` output).` with `\`standards/workflows/\`, else \`knowledge/\` (no \`documentation/\` output).`
Replace `\`vision\`/\`guide\`/\`reference\`/\`catalog\`/\`communications\`/\`presentations\`` with `\`vision\`/\`documentation\`/\`reference\`/\`catalog\`/\`communications\`/\`presentations\``.

- [ ] **Step 6: `quenching-enrich/references/sources.md` — unit target**

Replace `- One **how-to / procedure** → a \`guides/\` unit.` with `- One **how-to / procedure** → a \`documentation/how-to/\` unit.`

- [ ] **Step 7: `quenching-visualize/references/viz.md` — type vocabulary**

Replace `\`table\`, \`decision\`, \`vision\`, \`idea\`, \`guide\`, \`knowledge\`, \`reference\`,` with `\`table\`, \`decision\`, \`vision\`, \`idea\`, \`documentation\`, \`knowledge\`, \`reference\`,`.

- [ ] **Step 8: `assets/tools/okf-visualize.py` — palette key**

Replace `    "guide": "#22c55e",` with `    "documentation": "#22c55e",`.

- [ ] **Step 9: Verify the visualizer still imports/parses**

Run: `python3 -c "import ast; ast.parse(open('assets/tools/okf-visualize.py').read()); print('parse OK')"`
Expected: `parse OK`.

- [ ] **Step 10: Full-repo ghost-reference sweep**

Run: `grep -rn "guides/\|type: guide\|\"guide\"\|'guide'\|\`guide\`" plugins/claude-quenching 2>/dev/null || grep -rn "guides/\|type: guide" .`
Expected: **only** intentional survivors — the migration variant source `docs/guias/` mapping and §1c/§5 in `migration.md`, the "absorbs the former `guides/`" notes in `taxonomy.md`/`documentation/index.md`/`how-to/index.md`, and any README changelog line (added in Task 10). No live routing/tree/type reference to a `guides/` home. List each survivor and confirm it is intentional.

- [ ] **Step 11: Commit**

```bash
git add skills/quenching-insert/SKILL.md skills/quenching-knowledge/SKILL.md skills/quenching-knowledge-scan/SKILL.md skills/quenching-harness/references/harness-routing.md skills/quenching-memory-to-docs/references/memory-routing.md skills/quenching-enrich/references/sources.md skills/quenching-visualize/references/viz.md assets/tools/okf-visualize.py
git commit -m "docs: sweep remaining guide -> documentation references across skills + visualizer"
```

---

### Task 10: Keywords, README, and final verification

**Files:**
- Modify: `.claude-plugin/plugin.json` (keywords only — NOT version), `README.md`

- [ ] **Step 1: `README.md` — swap the homes-tree line**

Replace:
```
  guides/                # how-to + tutorials (type: guide)
```
with:
```
  documentation/         # product docs site — Diátaxis prose (type: documentation)
```

- [ ] **Step 2: `README.md` — add a changelog/what-changed note**

Find the top-level intro or a "What's new"/changelog area (grep: `grep -n "0.9.0\|## " README.md | head`). Add one line documenting the breaking change and the new setup, e.g. under the nearest version/notes heading:
```
- **0.9.0:** retired the `guides/` home into `documentation/how-to/`; added the `documentation/`
  home (Diátaxis product docs) and a shippable mkdocs-material site setup (`assets/mkdocs/`).
```
(If a `## Cost model` or model-policy section references homes/sub-agents, no change is needed — this feature adds no new sub-agent call.)

- [ ] **Step 3: `.claude-plugin/plugin.json` — add keywords (do NOT touch version)**

Confirm `"version": "0.9.0"` is unchanged. In the `keywords` array, add `"mkdocs"` and `"documentation"` if absent (grep: `grep -n "keywords\|version" .claude-plugin/plugin.json`). Edit only the keywords array.

- [ ] **Step 4: Confirm version lockstep**

Run:
```bash
echo "VERSION=$(cat VERSION)"; grep '"version"' .claude-plugin/plugin.json; grep -n "0.9.0\|__version__\|VERSION =" assets/hooks/okf-validate.py | head
python3 assets/hooks/okf-validate.py --version
```
Expected: `VERSION` file = `0.9.0`, plugin.json `"version": "0.9.0"`, and `okf-validate.py --version` prints `0.9.0`. If the hook prints anything else, update its version constant to `0.9.0` (lockstep) and re-run.

- [ ] **Step 5: Final full verification (the acceptance gate)**

Run:
```bash
python3 assets/hooks/okf-validate.py assets/docs
grep -rn "guides/\|type: guide" plugins/claude-quenching | grep -v -e "guias/" -e "former \`guides/\`" -e "retired the \`guides/\`" -e "docs/guides/\*\*" -e "type: guide\` →" -e "0.9.0:"
```
Expected: validator ends `0 error(s), 0 warning(s)`; the grep prints **nothing** (every remaining `guides/` mention is an intentional migration/changelog survivor and is filtered out). If the grep prints a line, that is a missed live reference — fix it before committing.

- [ ] **Step 6: Commit**

```bash
git add README.md .claude-plugin/plugin.json
git commit -m "docs: README homes/changelog + plugin keywords for documentation/mkdocs (0.9.0)"
```

---

## Self-Review (completed by plan author)

**Spec coverage** — every spec §5 "arquivos afetados" entry maps to a task:
- documentation/ skeleton (5 index + 5 .pages) → Task 1; delete guides/ → Task 1.
- taxonomy.md → Task 2; okf-spec.md + concept-front.md → Task 3; homes.md → Task 4.
- root/knowledge/communications index.md → Task 5; migration.md (+ retired-home rule) → Task 6.
- align SKILL.md (skeleton list + new mkdocs step) → Task 7; assets/mkdocs/* → Task 8.
- insert/knowledge/knowledge-scan SKILL, harness-routing, memory-routing, enrich/sources, viz.md, okf-visualize.py → Task 9.
- README, plugin.json keywords, VERSION lockstep, conformance.md (verified: no `guides` mention — no edit needed) → Task 10.
- Verification (validator 0/0, grep sweep, mkdocs build), edge cases, §4.5 coordination → Tasks 1/8/9/10 verification steps + Global Constraints.

**Placeholder scan:** the `<YOUR PROJECT>`/`<one-line…>` tokens in `mkdocs.yml.tmpl` are intentional user-fill placeholders in a shipped template (documented in Step 1 and the README), not plan gaps.

**Type consistency:** `type: documentation`, section slugs `getting-started`/`how-to`/`reference`/`concepts`, `docs_dir: docs/documentation`, and plugin `awesome-pages` are used identically across Tasks 1, 2, 4, 7, 8.

**Open items surfaced (not blockers):** awesome-pages vs the maintained awesome-nav successor (Global Constraints note) — confirm with the user; exact dependency pins may be tightened at install time.
