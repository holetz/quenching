# Backlog → task inbox + duas skills (v0.11.0) — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans para implementar este plano tarefa a tarefa (escolha do usuário: execução inline nesta sessão). Steps usam checkboxes (`- [ ]`) para tracking.

**Goal:** Implementar a spec `docs/superpowers/specs/2026-07-14-backlog-skills-design.md`: renomear o conceito `idea` → `task` no home `backlog/`, adicionar keys opcionais `priority`/`tags`, instalar uma zona GENERATED derivada em `backlog/index.md`, renomear o ledger "Developed" → "Completed", e criar duas skills novas (`quenching-backlog` captura; `quenching-backlog-triage` triagem) — plugin passa de dez para doze skills, versão 0.10.0 → 0.11.0.

**Architecture:** Sete commits ordenados para que nada cite prosa que ainda não existe e o skeleton `assets/docs/` permaneça conformante a cada passo: (1) mold+seed, (2) propagação em assets/, (3) propagação em references/ + quenching-insert, (4) skill de captura, (5) skill de triagem, (6) paleta do visualize + bumps de versão + README/CLAUDE.md, (7) verificação final. As references são atualizadas ANTES das skills novas porque ambas as skills citam o novo bullet da zona em `homes.md`.

**Tech Stack:** Markdown (skills = prosa executável), Python 3 stdlib-only (2 scripts), JSON (manifests). Não há suíte de testes — a verificação é o validador `okf-validate.py`, o gerador `okf-visualize.py` e greps de aceitação.

## Contexto

O `backlog/` hoje é o "raw idea inbox": mínimo, plano, sem metadados de prioridade. Três lacunas práticas (spec §Problem): captura sem trigger dedicado, index sem visão do conjunto, nada ajuda a priorizar. A spec (aprovada, supersede em parte a de 2026-07-08) resolve com: `type: task`, keys opcionais `priority` (`critical|high|medium|low`) e `tags`, zona derivada no index, e o par captura+triagem. Restrições do usuário: captura continua mínima e em segundos; tudo OKF v0.1-conformante; termos canônicos em inglês.

Decisão adicional do usuário nesta sessão: ao editar a linha do contrato do bundle no `CLAUDE.md` raiz, **corrigir também o `guides/` desatualizado** (home aposentado na v0.9 → `documentation/`; defeito pré-existente na mesma linha).

## Global Constraints (da spec — valem para toda tarefa)

- Caminhos-base: repo `/home/unicred/Projetos/claude-quenching`; plugin `plugins/claude-quenching/` (abreviado `PC/` abaixo).
- `priority` é enum fixo de quatro valores: `critical | high | medium | low`. Ausente = **untriaged** (estado válido, não defeito).
- `tags` carrega os temas; normalizados contra tags já presentes no backlog (reusar `auth`, não cunhar `authentication`).
- Home `backlog/` continua **flat** (sem subpastas); slugs kebab-case em inglês; frontmatter canônico inglês; corpo 1–3 frases pode seguir a língua do repo.
- Sem `done-criteria`, `vision_refs`, estimates, assignees, due dates ou campo status. `resource` deliberadamente omitido (WARN `missing-resource` esperado e documentado no mold).
- `description` de cada SKILL.md ≤ **1.536 caracteres**, com trigger phrases na **segunda frase**; corpo bem abaixo de 500 linhas; **nunca** `context: fork`.
- Zona GENERATED: rebuilt **exclusivamente** do frontmatter das tasks, só entre `<!-- BEGIN GENERATED: ... -->` / `<!-- END GENERATED -->`; formato documentado UMA vez em `homes.md` §Updating `index.md`; ledger Completed fica FORA da zona.
- **Zero mudança funcional** em `okf-validate.py` (só bump da const `VERSION`); validador não ganha checks de priority/type-value/zona.
- `quenching-cycle` inalterado (triage é ferramenta on-demand, como enrich/visualize).
- Token "idea" sobrevive APENAS em: `quenching-align/references/migration.md` (mapeamentos legados) e na entrada legacy da paleta de `okf-visualize.py`. O grep de aceitação (spec §Verification item 3) é o critério.
- Versões em lockstep: `VERSION` = `plugin.json` = entry do `marketplace.json` = const `VERSION` dos DOIS scripts = `0.11.0`.
- Mensagens de commit em português (padrão do repo), terminando com `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

---

### Task 0: Salvar o plano no repositório

**Files:**
- Create: `docs/superpowers/plans/2026-07-14-backlog-task-inbox.md`

- [ ] **Step 1: Copiar este arquivo de plano para o repo**

```bash
mkdir -p docs/superpowers/plans
cp /home/unicred/.claude/plans/crie-um-plano-com-eventual-giraffe.md docs/superpowers/plans/2026-07-14-backlog-task-inbox.md
```

- [ ] **Step 2: Commit**

```bash
git add docs/superpowers/plans/2026-07-14-backlog-task-inbox.md
git commit -m "Plano — backlog task inbox com prioridades e 2 skills

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 1: Mold `task.md` + seed `backlog/index.md`

**Files:**
- Rename+rewrite: `PC/assets/templates/backlog/idea.md` → `PC/assets/templates/backlog/task.md`
- Rewrite: `PC/assets/docs/backlog/index.md`

**Interfaces:**
- Produces: o mold `backlog/task.md` e o formato da zona GENERATED que TODAS as tarefas seguintes citam (marcadores idênticos aos de `standards/index.md`: `<!-- BEGIN GENERATED: ... -->` multi-linha anotado + `<!-- END GENERATED -->`).

- [ ] **Step 1: Renomear o mold**

```bash
cd /home/unicred/Projetos/claude-quenching
git mv plugins/claude-quenching/assets/templates/backlog/idea.md plugins/claude-quenching/assets/templates/backlog/task.md
```

- [ ] **Step 2: Reescrever `PC/assets/templates/backlog/task.md` com exatamente este conteúdo**

````markdown
---
type: task              # OKF concept type — non-empty
title: <one-line name of the task>
description: <one sentence — the gist>
timestamp: <ISO 8601 — e.g. 2026-07-14>
tags: [<theme>, ...]                   # OPTIONAL — the task's theme(s), normalized against tags already in the backlog
priority: <critical|high|medium|low>   # OPTIONAL — absent = untriaged (a valid state; triage fills it)
---

# <task title>

<1–3 sentences: what the task is, why it might matter, any seed context.
No done-criteria, no vision_refs, no estimates — that thinking happens in
`superpowers:brainstorming` or at execution, not here.>

<!-- MOLD (claude-quenching · backlog task) → becomes `backlog/<task-slug>.md`.
     `backlog/` is the TASK INBOX: the fast, low-ceremony landing spot for a unit of work —
     raw (needs `superpowers:brainstorming` first) or already clear in scope — parked between
     "I thought of this" and "I'm working on this". `tags`/`priority` are OPTIONAL: stamp them
     only when the human states them inline, and DROP the lines otherwise — a task without
     `priority` is untriaged, a valid state `quenching-backlog-triage` exists to fill.
     `resource` is intentionally omitted — nothing is built yet to point at (the resulting
     `missing-resource` WARN is expected, not a defect). Once the task is developed into an
     approved spec (`docs/superpowers/specs/…`) or done, the file LEAVES the tree and the
     transition is recorded in `backlog/index.md`'s Completed ledger (mirroring how an
     implemented ADR distills into `standards/` and leaves `decisions/`). -->
````

- [ ] **Step 3: Reescrever `PC/assets/docs/backlog/index.md` com exatamente este conteúdo**

(Conformidade: index sem frontmatter; zona vazia usa placeholder itálico SEM links — padrão de `standards/index.md` — então não gera `index-broken-link`/`index-orphan`.)

````markdown
# `backlog/` — the task inbox

The fast, low-ceremony landing spot for a **task** — a unit of work captured in seconds,
raw (it needs `superpowers:brainstorming` before it becomes work) or already clear in
scope — parked between "I thought of this" and "I'm working on this". A raw task feeds
`superpowers:brainstorming`, which develops it into an approved design spec
(`docs/superpowers/specs/…`); a clear one goes straight to execution.

**Boundary:** a *parked* unit of work — distinct from `vision/` (settled direction with no
deadline) and `decisions/` (a settled decision with considered alternatives). Each task
carries `type: task`, a title, a one-sentence gist, and a timestamp; `tags` (themes) and
`priority` (`critical|high|medium|low`) are **optional** — a task without `priority` is
**untriaged**, a valid state `quenching-backlog-triage` exists to fill. No done-criteria,
no `vision_refs`, no estimates (that thinking belongs to brainstorming/execution).

## Organization

```
backlog/
  <task-slug>.md     # one task per file (type: task) — flat, no subfolders
```

## Lifecycle

1. **Capture** — a task lands here in seconds (`quenching-backlog`, or generic
   `quenching-insert` routing; minimal `task` mold — priority/tags only when stated).
2. **Triage (optional)** — `quenching-backlog-triage` proposes priority/tags in one
   plan → one OK sweep; a task may also be born triaged (stated inline at capture).
3. **Develop / execute** — `superpowers:brainstorming` for raw tasks; direct execution
   for tasks already clear in scope.
4. **Leave the tree** — once developed into an approved spec or done, the file is
   **removed** and the transition recorded in the Completed ledger below. Removal happens
   on completion/approval, never on triage; an abandoned development leaves the task in
   place.

## What does NOT go here

- A task already developed or done (remove it; log it in the Completed ledger).
- Settled direction with no deadline (→ `vision/`).
- A settled decision with considered alternatives (→ `decisions/`).

## Current tasks

<!-- BEGIN GENERATED: rebuilt from the tasks' frontmatter by `quenching-backlog`/
     `quenching-backlog-triage`/`quenching-insert`/`quenching-align` — DO NOT edit by hand.
     Content, in order:
       **N tasks** · X critical · Y high · Z medium · W low · K untriaged
       one table per priority level (Critical → High → Medium → Low → Untriaged; empty
       groups omitted), columns `Task | Description | Tags | Since` (Since = the task's
       `timestamp`), rows OLDEST-FIRST within each group so stale tasks surface;
       then "By theme": alphabetical bullets `**<tag>** (n): [task-a](task-a.md), …`
       (a task with two tags appears under both).
-->
_(no tasks parked — this listing is regenerated deterministically from `backlog/*.md` frontmatter)_
<!-- END GENERATED -->

## Completed ledger

Record each task here when it is completed — or its approved spec supersedes it — and you
remove the file (curated history, kept **outside** the generated zone):

| Task | Outcome | Date |
| --- | --- | --- |
| _(none yet)_ | | |

Mold: `backlog/task.md` (applied by `quenching-backlog` / `quenching-insert`).
````

- [ ] **Step 4: Verificar que o skeleton continua conformante**

```bash
cd plugins/claude-quenching && python3 assets/hooks/okf-validate.py assets/docs
```
Esperado: `0 error(s), 0 warning(s)`.

- [ ] **Step 5: Commit**

```bash
git add -A plugins/claude-quenching/assets/templates/backlog plugins/claude-quenching/assets/docs/backlog
git commit -m "Backlog task inbox — mold task.md e seed index.md com zona derivada

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: Propagação em `assets/` (payload instalável 100% task)

**Files:**
- Modify: `PC/assets/docs/index.md:19`, `PC/assets/docs/vision/index.md:7-8`, `PC/assets/templates/concept-front.md:2`, `PC/assets/templates/vision/area.md:28-29`, `PC/assets/templates/harness/claude-root.md:30`, `PC/assets/templates/README.md:15`, `PC/assets/README.md:17`

- [ ] **Step 1: Aplicar os sete edits exatos (old → new)**

1. `assets/docs/index.md:19`
   - old: `* [backlog/](/docs/backlog/index.md) — raw idea inbox (pre-brainstorming), one file per idea`
   - new: `* [backlog/](/docs/backlog/index.md) — task inbox (raw or scoped; optional priority/tags), one file per task`
2. `assets/docs/vision/index.md:7-8`
   - old: `A **raw idea** toward` / `it lands in [backlog/](/docs/backlog/index.md) (the idea inbox); what **has already become`
   - new: `A **raw task** toward` / `it lands in [backlog/](/docs/backlog/index.md) (the task inbox); what **has already become`
3. `assets/templates/concept-front.md:2` — no comentário do enum de `type`: `standard|decision|vision|idea|documentation|` → `standard|decision|vision|task|documentation|`
4. `assets/templates/vision/area.md:28-29`
   - old: `> A **raw idea** toward this direction lives in \`backlog/\` (the idea inbox); what **has`
   - new: `> A **raw task** toward this direction lives in \`backlog/\` (the task inbox); what **has`
5. `assets/templates/harness/claude-root.md:30`
   - old: `- [docs/backlog/](docs/backlog/index.md) — raw idea inbox (pre-brainstorming).`
   - new: `- [docs/backlog/](docs/backlog/index.md) — task inbox (park now, triage later).`
6. `assets/templates/README.md:15`
   - old: `| \`backlog/idea.md\` | \`backlog/<idea-slug>.md\` | \`idea\` |`
   - new: `| \`backlog/task.md\` | \`backlog/<task-slug>.md\` | \`task\` |`
7. `assets/README.md:17` — na row de `templates/`: `\`backlog/idea\`` → `\`backlog/task\``. (A linha "27 `index.md` listings" NÃO muda — nenhum index novo.)

- [ ] **Step 2: Verificar**

```bash
cd plugins/claude-quenching && python3 assets/hooks/okf-validate.py assets/docs
grep -rni "idea" assets --include='*.md' --include='*.py'
```
Esperado: validador `0/0`; grep vazio (a entrada legacy da paleta só entra na Task 6; matches em `viewer/vendor/*.js` são ruído de lib minificada e podem ser ignorados).

- [ ] **Step 3: Commit**

```bash
git add plugins/claude-quenching/assets
git commit -m "Backlog task inbox — propagação em assets/

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: Propagação em `references/` + `quenching-insert/SKILL.md`

**Files:**
- Modify: `PC/skills/quenching-align/references/taxonomy.md`, `.../okf-spec.md`, `.../migration.md`, `.../conformance.md`, `PC/skills/quenching-insert/references/homes.md`, `PC/skills/quenching-insert/SKILL.md`, `PC/skills/quenching-harness/references/harness-routing.md`, `PC/skills/quenching-memory-to-docs/references/memory-routing.md`, `PC/skills/quenching-visualize/references/viz.md`

**Interfaces:**
- Produces: o bullet da zona em `homes.md` §Updating `index.md` e a routing row `task`/`backlog/task.md` — citados pelas skills das Tasks 4 e 5.

- [ ] **Step 1: `taxonomy.md` (4 edits)**

1. Linha 22 (árvore):
   - old: `  backlog/                     # raw idea inbox (pre-brainstorming) — <idea-slug>.md (type: idea)`
   - new: `  backlog/                     # task inbox — <task-slug>.md (type: task; optional priority/tags); DERIVED index zone`
2. Linha 43 (tabela de vocabulário): `| \`backlog/\` | \`idea\` | \`<idea-slug>.md\` |` → `| \`backlog/\` | \`task\` | \`<task-slug>.md\` |`
3. Linha 78 (bullet de `vision/`): `A raw idea toward it → \`backlog/\`` → `A raw task toward it → \`backlog/\``
4. Linhas 79-83 — substituir o bullet do backlog inteiro por:

```markdown
- **`backlog/`** — the **task inbox** (`type: task`): fast, low-ceremony capture of a unit
  of work — raw (pre-`superpowers:brainstorming`) or already clear in scope. Flat
  (`<task-slug>.md`, no subfolders); no `vision_refs`/done-criteria/estimates; **optional**
  `priority` (`critical|high|medium|low` — absent = untriaged, a valid state) and `tags`
  (themes). Its `index.md` carries a **DERIVED zone** (summary + per-priority tables +
  by-theme bullets, rebuilt from the tasks' frontmatter — format owned by `homes.md`
  §Updating `index.md`) plus a curated **Completed ledger** outside the zone. Captured by
  `quenching-backlog` (or generic `quenching-insert` routing); prioritized by
  `quenching-backlog-triage`. Once a task is developed into an approved spec or done, it
  **leaves** the tree (the Completed ledger keeps the trail).
```

- [ ] **Step 2: `okf-spec.md:30`** — na lista do vocabulário: `\`vision\`, \`idea\`, \`documentation\`` → `\`vision\`, \`task\`, \`documentation\``

- [ ] **Step 3: `migration.md` — o único sobrevivente deliberado de "idea"**

Inserir após §1c (linha ~72, antes de "### Content relocation"):

```markdown
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
```

E em §5 (Frontmatter migration), adicionar bullet logo após o do `type: guide` (linha 119):

```markdown
- rename the retired type `type: idea` → `type: task` (the backlog item concept was renamed in v0.11 — see §1d)
```

- [ ] **Step 4: `conformance.md` §Verify gate (linha ~88)**

- old (fim da seção): `` and `standards/index.md`'s GENERATED zone matching disk.``
- new: `` and the GENERATED zones matching disk — `standards/index.md`'s "Current docs" tables and `backlog/index.md`'s task listing (each rebuilt exclusively from the frontmatter on disk).``

- [ ] **Step 5: `homes.md` (3 edits)**

1. Linha 22 (routing row — a row FICA na tabela, per spec):
   - old: `| a **raw idea** to capture (pre-brainstorming) | \`backlog/\` | \`idea\` | \`backlog/idea.md\` | \`<idea-slug>.md\` |`
   - new: `| a **task** to park (raw or already scoped) | \`backlog/\` | \`task\` | \`backlog/task.md\` | \`<task-slug>.md\` |`
2. Linhas 49-54 (tie-breaker) — substituir o bullet inteiro por:

```markdown
- **task vs vision/decisions:** a **parked unit of work** is a `task` in `backlog/` — raw
  (no scope or alternatives yet, pre-`superpowers:brainstorming`) or already clear in
  scope; a **settled direction** with no deadline is a `vision`; a **settled decision**
  with considered alternatives is a `decision`. A raw task graduates to a
  `decision`/`vision`/`standard` only after brainstorming develops it into an approved
  spec; on completion/approval the task file leaves `backlog/` (its Completed ledger
  keeps the trail).
```

3. §Updating `index.md` — novo bullet após o bullet do `standards/index.md` (após linha 99):

```markdown
- **`backlog/index.md`** has a DERIVED zone too: rebuild only what is between
  `<!-- BEGIN GENERATED -->` / `<!-- END GENERATED -->`, exclusively from `backlog/*.md`
  frontmatter (`title`/`description`/`tags`/`priority`/`timestamp`) — a summary line
  (`**N tasks** · X critical · Y high · Z medium · W low · K untriaged`), one
  `Task | Description | Tags | Since` table per priority level (Critical → High →
  Medium → Low → Untriaged; empty groups omitted; rows oldest-first within each group),
  then alphabetical "By theme" bullets (`**<tag>** (n): [task-a](task-a.md), …` — a task
  lists under each of its tags). A task with an unknown `priority` value renders under
  Untriaged. Never hand-edit inside the markers; the **Completed ledger** stays OUTSIDE
  the zone (curated by hand, rows only on completion). If a target's `backlog/index.md`
  predates the markers, install them without touching the fixed prose around them.
```

- [ ] **Step 6: `quenching-insert/SKILL.md` (3 edits)**

1. Na `description` (linha ~7), remover o trigger: `"record a domain decision", "capture a raw idea", "draft an announcement"` → `"record a domain decision", "draft an announcement"`.
2. No fim da `description`: `Not for: installing/aligning the whole docs/ structure → quenching-align.` → `Not for: installing/aligning the whole docs/ structure → quenching-align; parking a task in the backlog → quenching-backlog.` (Recontar: deve continuar ≤ 1.536 chars.)
3. No Workflow, step "Update `index.md`" (step 5, ~linha 80-83): após a frase sobre a zona GENERATED de `standards/`, acrescentar: `For \`backlog/\`, the index's task listing is likewise a DERIVED zone — regenerate it from the tasks' frontmatter per the \`backlog/index.md\` bullet in [references/homes.md](references/homes.md); never hand-edit inside the markers.`

- [ ] **Step 7: `harness-routing.md` (2 edits)**

1. Linha 53: `| roadmap / TODO / next-steps item (raw, unscoped) | **MOVE** | \`backlog/\` (\`idea\`), or \`vision/\` (\`vision\`) for settled direction with no deadline |` → `| roadmap / TODO / next-steps item (raw, unscoped) | **MOVE** | \`backlog/\` (\`task\`, untriaged), or \`vision/\` (\`vision\`) for settled direction with no deadline |`
2. Linha 65: `a **raw idea** → \`backlog/\`` → `a **parked task** → \`backlog/\``

- [ ] **Step 8: `memory-routing.md` (2 edits — sempre untriaged, anti-fabricação)**

1. Linha 37 (row `project`): `a **raw idea / thing to explore or build** → \`backlog/\` (a raw \`idea\`)` → `a **thing to explore or build** → \`backlog/\` (a \`task\`, **always untriaged** — inventing a priority the human never stated would violate anti-fabrication)`; e na coluna de types: `\`idea\` / \`decision\` / \`standard\` / \`knowledge\`` → `\`task\` / \`decision\` / \`standard\` / \`knowledge\``
2. Linha 44 (tie-breaker): `a **raw idea / thing to explore** → \`backlog/\` (a raw \`idea\`);` → `a **thing to explore or build** → \`backlog/\` (a \`task\`, always untriaged);`

- [ ] **Step 9: `viz.md:44` (lista de types + nota legacy)**

1. `\`vision\`, \`idea\`, \`documentation\`` → `\`vision\`, \`task\`, \`documentation\``
2. Após `an unknown/absent \`type\` falls back to a neutral slate.`, inserir: `The retired \`idea\` type keeps its legacy colour so an un-migrated bundle still renders.` (o token nu `` `idea` `` não casa com nenhum padrão do grep de aceitação.)

- [ ] **Step 10: Verificar o grep de aceitação parcial**

```bash
grep -rn "type: idea\|backlog/idea\|idea-slug\|raw idea" plugins/claude-quenching --include='*.md'
```
Esperado: apenas `skills/quenching-align/references/migration.md` (§1d e §5).

- [ ] **Step 11: Commit**

```bash
git add plugins/claude-quenching/skills
git commit -m "Backlog task inbox — propagação em references e quenching-insert

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: Skill nova `quenching-backlog` (captura de UMA task)

**Files:**
- Create: `PC/skills/quenching-backlog/SKILL.md`

**Interfaces:**
- Consumes: mold `assets/templates/backlog/task.md` (Task 1); bullet da zona e routing row em `homes.md` (Task 3).
- Produces: a skill que a Task 6 lista no README/CLAUDE.md. Padrão per-item (peer de `quenching-glossary`), sem gate de confirmação, `effort: low`.

- [ ] **Step 1: Criar `PC/skills/quenching-backlog/SKILL.md` com exatamente este conteúdo**

````markdown
---
name: quenching-backlog
description: >-
  Captures ONE task into the repo's OKF backlog/ — the task inbox — in seconds: a minimal
  type: task stamp, with optional priority/tags only when the human states them inline.
  Use when the user asks to "add to the backlog", "park a task", "capture a task", "note
  this for later", or "backlog this". Extracts title + gist from the phrasing ("park X,
  high priority, theme auth" → priority: high, tags: [auth]; tags normalized against ones
  already in the backlog), dedupes by slug/title (MERGE, never clobber), writes
  backlog/<task-slug>.md from the task mold, regenerates the derived GENERATED zone in
  backlog/index.md, logs the creation, and self-checks. Zero interrogation: what was not
  said is left out — no priority means untriaged, a valid state. Not for: prioritizing
  the whole backlog → quenching-backlog-triage; any other kind of doc → quenching-insert.
when_to_use: >-
  parking ONE task in the backlog/ inbox, fast and minimal. The prioritization sweep is
  quenching-backlog-triage; routing any other kind of doc is quenching-insert.
allowed-tools: Read, Grep, Glob, Write, Edit
effort: low
---

# quenching-backlog — park one task in the inbox

Files ONE task into the canonical OKF bundle's task inbox,
[`backlog/`](../../assets/docs/backlog/index.md) — the fast, low-ceremony landing spot for
a unit of work, raw (it needs `superpowers:brainstorming` before it becomes work) or
already clear in scope, parked between "I thought of this" and "I'm working on this". The
mold is `${CLAUDE_PLUGIN_ROOT}/assets/templates/backlog/task.md`; the routing row, the
derived-zone format, and the shared index/log/glossary procedure live with
`quenching-insert`
([../quenching-insert/references/homes.md](../quenching-insert/references/homes.md)); the
`type` vocabulary and conformance rules with `quenching-align`
([../quenching-align/references/taxonomy.md](../quenching-align/references/taxonomy.md),
[.../conformance.md](../quenching-align/references/conformance.md)). For prioritizing the
whole inbox instead of capturing one task, see `quenching-backlog-triage`.

## Doctrine

- **Capture in seconds — the stamp stays minimal.** `type: task`, title, one-sentence
  gist, timestamp. `priority` (`critical|high|medium|low`) and `tags` (themes) are
  stamped ONLY when the human states them inline. No `done-criteria`, no `vision_refs`,
  no estimates — that thinking belongs to `superpowers:brainstorming` or execution, never
  to capture. `resource` is deliberately omitted (nothing built yet to point at); the
  resulting `missing-resource` WARN is expected, not a defect.
- **Zero interrogation.** Never ask for a priority, a theme, or scope. What was not said
  is left out; a task without `priority` is **untriaged** — a valid state
  `quenching-backlog-triage` exists to fill, not a gap to chase at capture time.
- **Tags are normalized, never minted casually.** Reuse a theme already present in the
  backlog's tasks (`auth`, not a fresh `authentication`); a genuinely new theme is fine.
- **Flat home, English kebab slug.** One task per file, `backlog/<task-slug>.md`, no
  subfolders. Frontmatter is canonical English; the 1–3-sentence body may follow the
  repo's language.
- **MERGE, never clobber.** A slug/title collision merges into the existing task (fill
  missing keys, sharpen the gist) or aborts if it is the same task — never overwrite.
- **The zone is derived, never hand-edited.** `backlog/index.md`'s task listing is
  rebuilt exclusively from the tasks' frontmatter, only between the GENERATED markers,
  per the `backlog/index.md` bullet in
  [../quenching-insert/references/homes.md](../quenching-insert/references/homes.md)
  §**Updating `index.md`**. The Completed ledger stays outside the zone, untouched.

## Workflow

### 1. Resolve the bundle
Find `docs/backlog/` (the bundle root may be a variant — resolve it as the other skills
do). If the home or its `index.md` is **missing**, stop and offer `quenching-align` to
install the skeleton, then resume.

### 2. Extract from the user's phrasing
Take the title and one-sentence gist from what the human said. Parse `priority`/`tags`
ONLY when stated inline ("park X, high priority, theme auth" → `priority: high`,
`tags: [auth]`). Normalize tags against the ones already present in `backlog/*.md`
frontmatter. **Zero interrogation** — what was not said is left out.

### 3. Dedupe
`Grep`/`Glob` `backlog/` for a similar slug or title. On a collision, MERGE into the
existing task (never clobber a filled key) — or abort and say so if it is the same task.

### 4. Stamp and write
Fill the `task.md` mold and write `backlog/<task-slug>.md` (English kebab slug). Drop the
optional keys that were not stated; `priority` only ever takes
`critical|high|medium|low`.

### 5. Regenerate the derived zone
Rebuild `backlog/index.md`'s GENERATED zone from the tasks' frontmatter, per the
`backlog/index.md` bullet in **Updating `index.md`**
([../quenching-insert/references/homes.md](../quenching-insert/references/homes.md)). If
a target's `backlog/index.md` predates the markers, install them without touching the
fixed prose around them.

### 6. Log and enrich the glossary
Append `**Creation**: [<title>](/docs/backlog/<task-slug>.md) — <one line>` per
**Appending to `log.md`**, then run the shared glossary tail step per **Enriching the
glossary** (both in
[../quenching-insert/references/homes.md](../quenching-insert/references/homes.md)) —
normally a no-op for a task.

### 7. Self-check against the conformance core
Verify every file you touched against
[../quenching-align/references/conformance.md](../quenching-align/references/conformance.md),
plus this skill's own gate: the GENERATED zone matches the tasks on disk and every zone
link resolves.

## Invariants to never violate

- Never interrogate the human at capture — no priority, theme, or scope questions; absent
  keys stay absent (untriaged is a valid state).
- Never invent a `priority` or a tag the human did not state, and never use a priority
  value outside `critical|high|medium|low`.
- Never clobber an existing task on collision — MERGE or abort.
- Never hand-edit inside the GENERATED markers, never touch the Completed ledger at
  capture, and never add frontmatter to `backlog/index.md`.
- Never expand the stamp — no `done-criteria`, `vision_refs`, estimates, assignees, or a
  status field; status is positional (in the tree = open).
````

- [ ] **Step 2: Verificar budget e proibições**

```bash
python3 - <<'EOF'
import re
t = open("plugins/claude-quenching/skills/quenching-backlog/SKILL.md").read()
fm = t.split("---")[1]
d = re.search(r"description: >-\n((?:  .*\n)+)", fm).group(1)
d_len = len(re.sub(r"\s+", " ", d).strip())
assert d_len <= 1536, d_len
assert "context: fork" not in t
print("description:", d_len, "chars · body:", t.count("\n"), "lines · OK")
EOF
```
Esperado: `description: ~810 chars` (≤1536), sem `context: fork`, corpo < 500 linhas.

- [ ] **Step 3: Commit**

```bash
git add plugins/claude-quenching/skills/quenching-backlog
git commit -m "Skill quenching-backlog — captura de uma task no inbox

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: Skill nova `quenching-backlog-triage` (sweep de priorização)

**Files:**
- Create: `PC/skills/quenching-backlog-triage/SKILL.md`

**Interfaces:**
- Consumes: bullet da zona em `homes.md` (Task 3); doutrina do ledger no seed (Task 1).
- Produces: a skill sweep que a Task 6 lista no README/CLAUDE.md. ONE plan → ONE OK; SEM sub-agentes; SEM `effort` override; SEM exceção cycle-authorized (triage não é estágio do cycle); nunca `context: fork`.

- [ ] **Step 1: Criar `PC/skills/quenching-backlog-triage/SKILL.md` com exatamente este conteúdo**

````markdown
---
name: quenching-backlog-triage
description: >-
  Sweeps the repo's OKF backlog/ task inbox and proposes ONE consolidated triage plan — a
  priority (critical|high|medium|low) and tags for each untriaged task, grounded in
  vision/ when present — applied on a single confirmation. Use when the user asks to
  "prioritize the backlog", "triage the backlog", "groom the backlog", or "re-rank the
  tasks". Reads every task's frontmatter directly (no sub-agents — the backlog is small
  by nature), builds one table of proposals with one-line rationales, flags stale tasks
  and duplicates, re-ranks an already-triaged task only with an explicit reason, then
  applies the edits (MERGE — never silently clobber a human-set priority), regenerates
  the derived zone in backlog/index.md, and logs one consolidated update.
  Completion/removal enters the plan only when the human states a task is done — never
  inferred. Not for: capturing ONE task → quenching-backlog; developing a task into a
  spec → superpowers:brainstorming.
when_to_use: >-
  prioritizing the WHOLE backlog/ inbox in one plan → one OK sweep. Capturing a single
  task is quenching-backlog; developing one is superpowers:brainstorming.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# quenching-backlog-triage — prioritize the task inbox

Sweeps the canonical OKF bundle's **entire** task inbox,
[`backlog/`](../../assets/docs/backlog/index.md), and proposes priorities and themes for
what is parked there — the sweep counterpart of the per-item `quenching-backlog` capture.
Unlike `quenching-knowledge-scan`, this sweep fans **no** sub-agents out: a backlog is
small by nature and each task is a few frontmatter lines, so the orchestrator reads
everything directly. The derived-zone format and the shared index/log procedure live with
`quenching-insert`
([../quenching-insert/references/homes.md](../quenching-insert/references/homes.md)); the
`type` vocabulary and conformance rules with `quenching-align`
([../quenching-align/references/taxonomy.md](../quenching-align/references/taxonomy.md),
[.../conformance.md](../quenching-align/references/conformance.md)). Triage is an
**on-demand tool** like `quenching-enrich`/`quenching-visualize` — it is not a
`quenching-cycle` loop stage and carries no cycle-authorization exception: the plan gate
below always applies.

## Doctrine

- **Propose, don't invent.** Every proposed priority and tag traces to the task's own
  title/gist and, when present, the direction in `vision/` — each with a one-line
  rationale in the plan. Priorities only ever take `critical|high|medium|low`.
- **One plan, one OK.** Every proposal merges into ONE consolidated table before any
  write. A single confirmation approves the whole plan; partial adjustments → re-plan; a
  rejected plan applies **nothing**.
- **MERGE, never clobber.** A human-set priority is never silently overwritten — a
  re-rank of an already-triaged task enters the plan only with an explicit reason, and
  only the approved edits are applied.
- **Untriaged is a valid state.** A task the plan cannot honestly rank stays untriaged —
  no forced ranking. An invalid priority value found in a target (e.g.
  `priority: urgent`) renders under Untriaged and the plan proposes the fix.
- **Completion is stated, never inferred.** A removal + Completed-ledger row enters the
  plan only when the human says the task is done or its spec was approved. Triage alone
  never removes a task; an abandoned development leaves the task in place.
- **The zone is derived; the ledger is curated.** Rebuild only between the GENERATED
  markers per the `backlog/index.md` bullet in
  [../quenching-insert/references/homes.md](../quenching-insert/references/homes.md)
  §**Updating `index.md`**; the Completed ledger lives outside the zone and gains rows
  only for approved completions.

## Workflow

### 1. Read the backlog directly
Find `docs/backlog/` (the bundle root may be a variant — resolve it as the other skills
do); if the home is missing, stop and offer `quenching-align`, then resume. `Glob`
`backlog/*.md` and read each task's frontmatter **directly — no sub-agents**. Read
`vision/` when present to ground the proposals. Note stale tasks (old `timestamp`),
near-duplicate pairs, and any invalid `priority` value.

### 2. Build ONE triage plan
One table: `Task | Current | Proposed priority | Proposed tags | Rationale (one line)`.
Include: a proposal for every untriaged task (or an honest "stays untriaged"); re-ranks
of triaged tasks **only with an explicit reason**; staleness flags (old `Since`);
duplicate MERGE suggestions; fixes for invalid priority values; completions **only when
the human stated the task is done**. Tags normalized against the ones already in the
backlog.

### 3. One OK
Present the plan and **wait for a single confirmation**. Partial adjustments → adjust and
re-present; rejection → apply nothing and stop.

### 4. Apply exactly what was approved
Edit each task's frontmatter as listed (MERGE — fill/replace only the approved keys,
never a silent clobber). An approved duplicate MERGE moves content into the surviving
task and removes the other; an approved completion removes the file and adds a
`Task | Outcome | Date` row to the Completed ledger (outside the zone), with Outcome a
link to the resulting spec/PR/standard or a one-line "done — …".

### 5. Regenerate, log, self-check
Rebuild the GENERATED zone from the tasks' frontmatter (per the `homes.md` bullet;
install the markers first if the target's index predates them, without touching the
fixed prose). Append ONE consolidated entry per **Appending to `log.md`** in
[../quenching-insert/references/homes.md](../quenching-insert/references/homes.md):
`**Update**: [backlog/](/docs/backlog/index.md) — triaged N tasks (X ranked, Y re-ranked,
Z completed)`. Self-check every touched file against
[../quenching-align/references/conformance.md](../quenching-align/references/conformance.md),
plus this skill's own gate: the zone matches disk and its links resolve.

## Invariants to never violate

- Never write anything before the single consolidated confirmation; a rejected plan
  applies nothing.
- Never silently clobber a human-set priority — a re-rank always carries an explicit
  reason and an explicit approval.
- Never infer completion — removal and its Completed-ledger row happen only for tasks the
  human stated are done; an abandoned development leaves the task in place.
- Never use a priority value outside `critical|high|medium|low`, and never force a rank
  on a task the plan cannot honestly ground.
- Never hand-edit inside the GENERATED markers (regenerate the whole zone), never add
  frontmatter to `backlog/index.md`, and never fan out sub-agents — the orchestrator
  reads and writes everything itself.
````

- [ ] **Step 2: Verificar budget e proibições** (mesmo script da Task 4, trocando o path para `quenching-backlog-triage`). Esperado: description ~900 chars ≤1536; sem `context: fork`; corpo < 500 linhas.

- [ ] **Step 3: Commit**

```bash
git add plugins/claude-quenching/skills/quenching-backlog-triage
git commit -m "Skill quenching-backlog-triage — sweep de priorização do backlog

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: Paleta do visualize + bumps de versão + README + CLAUDE.md

**Files:**
- Modify: `PC/assets/tools/okf-visualize.py:45,68`, `PC/assets/hooks/okf-validate.py:85`, `PC/VERSION`, `PC/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (raiz), `PC/README.md`, `CLAUDE.md` (raiz)

- [ ] **Step 1: `okf-visualize.py`**

1. Linha 45: `VERSION = "0.10.0"  # kept in lockstep with the plugin VERSION file` → `VERSION = "0.11.0"  # kept in lockstep with the plugin VERSION file`
2. Linha 68 — substituir a entrada `"idea"` por DUAS entradas (mesmo vermelho; `"task"` primeiro; a legacy fica, comentada):
   - old:
     ```python
         "idea": "#ef4444",
     ```
   - new:
     ```python
         "task": "#ef4444",
         "idea": "#ef4444",  # legacy pre-0.11 backlog type — kept for un-migrated bundles
     ```

- [ ] **Step 2: `okf-validate.py:85`** — `VERSION = "0.10.0"` → `VERSION = "0.11.0"` (única mudança; zero funcional).

- [ ] **Step 3: `PC/VERSION`** — conteúdo passa a ser `0.11.0`.

- [ ] **Step 4: `PC/.claude-plugin/plugin.json` (3 edits)**

1. `"version": "0.10.0"` → `"version": "0.11.0"`
2. Na `description`: inserir o papel novo e atualizar a contagem —
   - old: `...imports external sources as OKF docs, renders the bundle as a self-contained offline HTML diagram, and loops it all to convergence. Ten skills (the routing story lives in each skill's own description) plus...`
   - new: `...imports external sources as OKF docs, parks and triages a task backlog, renders the bundle as a self-contained offline HTML diagram, and loops it all to convergence. Twelve skills (the routing story lives in each skill's own description) plus...`
3. `keywords`: adicionar `"backlog"` (após `"conformance"`).

- [ ] **Step 5: `.claude-plugin/marketplace.json` (raiz — 4 edits no entry do plugin + 1 no topo)**

1. Description do marketplace (topo): `...aligner, inserter, knowledge-capturer, ...` → `...aligner, inserter, task-backlog capturer and triager, knowledge-capturer, ...`
2. Entry: `"version": "0.10.0"` → `"0.11.0"`
3. Entry description: `Ten skills — align (structure), insert (any doc), knowledge (concepts), ...` → `Twelve skills — align (structure), insert (any doc), backlog + backlog-triage (the task inbox: capture + prioritize), knowledge (concepts), ...`
4. Entry `keywords`: adicionar `"backlog"` (espelha o plugin.json).

- [ ] **Step 6: `PC/README.md` (6 edits)**

1. Linha 11: `## The ten skills` → `## The twelve skills` (ajustar também qualquer frase introdutória "ten skills" próxima).
2. Inserir DUAS seções `###` novas imediatamente após a seção `### quenching-insert` (antes de `### quenching-enrich`):

```markdown
### `quenching-backlog` — park one task in the inbox

Captures **ONE task** into `backlog/` — the task inbox — in seconds: a minimal
`type: task` stamp (title, one-sentence gist, timestamp), with optional `priority`
(`critical|high|medium|low`) and `tags` (themes) **only when the human states them
inline** ("park X, high priority, theme auth"). **Zero interrogation** — what was not
said is left out; a task without `priority` is untriaged, a valid state. Dedupes by
slug/title (MERGE, never clobber), regenerates the derived GENERATED zone in
`backlog/index.md`, logs the creation, and self-checks. The per-item counterpart of
`quenching-backlog-triage`.

Triggers: *"add to the backlog"*, *"park a task"*, *"capture a task"*, *"note this for
later"*.

### `quenching-backlog-triage` — prioritize the task inbox

The prioritization sweep over the whole inbox: reads every task's frontmatter
**directly** (no sub-agents — a backlog is small by nature) plus `vision/` when present,
and builds **ONE triage plan** — a proposed priority + tags per untriaged task with a
one-line rationale, re-ranks of already-triaged tasks only with an explicit reason,
staleness flags, duplicate-merge suggestions. **One OK** applies the whole plan (a
rejected plan applies nothing; a human-set priority is never silently clobbered).
Completion/removal enters the plan **only when the human states a task is done** — the
removed task gains a row in the index's Completed ledger. Regenerates the zone and logs
one consolidated update.

Triggers: *"prioritize the backlog"*, *"triage the backlog"*, *"groom the backlog"*,
*"re-rank the tasks"*.
```

3. Linha ~101: `standard, backlog \`idea\`, decision, or \`knowledge\` doc in the` → `standard, backlog \`task\` (always untriaged), decision, or \`knowledge\` doc in the`
4. Linha ~179 (árvore): `  backlog/               # raw idea inbox — feeds superpowers:brainstorming (type: idea)` → `  backlog/               # task inbox — optional priority/tags; derived index zone (type: task)`
5. §Cost model: `All ten skills fit under the cap` → `All twelve skills fit under the cap`; recalcular a estimativa de chars agregada com:
   ```bash
   python3 -c "
   import re, glob
   tot = 0
   for p in glob.glob('plugins/claude-quenching/skills/*/SKILL.md'):
       fm = open(p).read().split('---')[1]
       for m in re.findall(r'(?:description|when_to_use): >-\n((?:  .*\n)+)', fm):
           tot += len(re.sub(r'\s+', ' ', m).strip())
   print(tot)"
   ```
   e atualizar o número no texto (`~10.2k chars ≈ 2.5k tokens` → o valor recalculado).
   Na tabela **Model policy**, adicionar duas rows:
   - `| \`quenching-backlog\` | \`effort: low\`; no model pin (mechanical single-task capture; zero interrogation, no sub-agents) |`
   - `| \`quenching-backlog-triage\` | no pin, no \`effort\` override — priority judgment inherits the session default; the human plan-gate contains misjudgment; no sub-agents |`
6. §Upgrade (changelog): nova entrada acima da `0.10.0`/`0.9.0`:
   - `- **0.11.0:** renamed the backlog item \`idea\` → \`task\` (optional \`priority\`/\`tags\`; derived GENERATED zone in \`backlog/index.md\`; "Developed" → "Completed" ledger) and added \`quenching-backlog\` (capture) + \`quenching-backlog-triage\` (triage sweep) — ten skills → twelve.`

- [ ] **Step 7: `CLAUDE.md` raiz (4 edits)**

1. Parágrafo de abertura (§What this repository is): `via ten skills plus a self-contained enforcement hook` → `via twelve skills plus a self-contained enforcement hook`.
2. Heading `## The ten skills and how they relate` → `## The twelve skills and how they relate`; na tabela, adicionar duas rows após a row de `quenching-insert`:
   - `| \`quenching-backlog\` | Captures ONE task into \`backlog/\` in seconds — minimal \`type: task\` stamp; inline-stated \`priority\`/\`tags\` only (zero interrogation; untriaged is a valid state); dedupes, regenerates the index's derived zone, logs. |`
   - `| \`quenching-backlog-triage\` | The prioritization sweep: reads task frontmatter directly (no sub-agents), proposes ONE triage plan (priority/tags with rationale, staleness, duplicates), applies on one OK, regenerates the zone. Completion only when human-stated. On-demand tool, not a cycle stage. |`
3. §The OKF bundle contract — linha do tree: `\`vision/\`, \`backlog/\`, \`guides/\`, \`knowledge/\`` → `\`vision/\`, \`backlog/\` (task inbox: \`type: task\`, optional \`priority\`/\`tags\`, derived index zone), \`documentation/\`, \`knowledge/\`` — **inclui o drive-by aprovado**: `guides/` (home aposentado na v0.9) vira `documentation/`.
4. Conferir se alguma outra menção "ten skills" existe no arquivo (`grep -n "ten skills" CLAUDE.md`) e atualizar.

- [ ] **Step 8: Verificar**

```bash
cd plugins/claude-quenching
python3 assets/tools/okf-visualize.py --version    # 0.11.0
python3 assets/hooks/okf-validate.py --version     # 0.11.0
cat VERSION                                        # 0.11.0
python3 assets/tools/okf-visualize.py assets/docs --out /tmp/okf-diagram.html   # exit 0 + contagem de nós/arestas
python3 assets/hooks/okf-validate.py assets/docs   # 0 error(s), 0 warning(s)
```

- [ ] **Step 9: Commit**

```bash
git add plugins/claude-quenching/assets/tools/okf-visualize.py plugins/claude-quenching/assets/hooks/okf-validate.py plugins/claude-quenching/VERSION plugins/claude-quenching/.claude-plugin/plugin.json .claude-plugin/marketplace.json plugins/claude-quenching/README.md CLAUDE.md
git commit -m "v0.11.0 — paleta task no visualize, bumps em lockstep, README e CLAUDE.md para doze skills

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 7: Verificação final (spec §Verification — sem edits)

- [ ] **Step 1: Contrato manual de verificação do repo**

```bash
cd /home/unicred/Projetos/claude-quenching/plugins/claude-quenching
python3 assets/hooks/okf-validate.py assets/docs            # → 0 error(s), 0 warning(s)
python3 assets/tools/okf-visualize.py assets/docs --out /tmp/okf-diagram.html   # exit 0
python3 assets/tools/okf-visualize.py --version              # 0.11.0
python3 assets/hooks/okf-validate.py --version               # 0.11.0
cat VERSION                                                  # 0.11.0
grep '"version"' .claude-plugin/plugin.json ../../.claude-plugin/marketplace.json  # ambos 0.11.0
```

- [ ] **Step 2: Greps de aceitação (sobreviventes deliberados apenas)**

```bash
cd /home/unicred/Projetos/claude-quenching
grep -rn "type: idea\|backlog/idea\|idea-slug\|raw idea" plugins/claude-quenching
#   → SOMENTE skills/quenching-align/references/migration.md (§1d + §5)
#     (matches binários/minificados em assets/tools/viewer/vendor/ são ruído, se aparecerem)
grep -n '"idea"' plugins/claude-quenching/assets/tools/okf-visualize.py
#   → a entrada legacy da paleta, adjacente à nova "task"
grep -rn "Developed ledger" plugins/claude-quenching
#   → SOMENTE migration.md §1d (que documenta o rename)
grep -rni "ten skills" plugins/claude-quenching CLAUDE.md
#   → vazio
```

- [ ] **Step 3: Budgets das skills novas/editadas**

```bash
python3 - <<'EOF'
import re
for p in ("plugins/claude-quenching/skills/quenching-backlog/SKILL.md",
          "plugins/claude-quenching/skills/quenching-backlog-triage/SKILL.md",
          "plugins/claude-quenching/skills/quenching-insert/SKILL.md"):
    t = open(p).read()
    fm = t.split("---")[1]
    d = re.search(r"description: >-\n((?:  .*\n)+)", fm).group(1)
    n = len(re.sub(r"\s+", " ", d).strip())
    assert n <= 1536, (p, n)
    assert "context: fork" not in t, p
    print(f"{p}: description {n} chars, {t.count(chr(10))} lines — OK")
EOF
```

- [ ] **Step 4: Reportar o resultado dos quatro itens da spec §Verification ao usuário** (com outputs reais; se algo falhar, corrigir antes de declarar concluído — superpowers:verification-before-completion).

---

## Notas de execução

- **Ordem importa:** references (Task 3) vêm ANTES das skills novas (Tasks 4-5) porque ambas citam o bullet da zona em `homes.md`. O skeleton `assets/docs/` só é tocado nas Tasks 1-2 e permanece conformante em todo commit.
- **Os greps só ficam totalmente limpos na Task 6** (README/CLAUDE.md limpam por último) — o grep de aceitação completo é a Task 7, não um gate intermediário.
- Nunca escrever o `.html` do visualize dentro de `assets/docs/` (usar `/tmp`).
- Fora de escopo (spec §Out of scope): nada em `okf-validate.py` além do bump; nada no `quenching-cycle`; sem expansão de detalhe per-task; sem promoção automática de task desenvolvida.
