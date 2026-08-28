# Documentation architecture — intent-led structure and output contracts

The information architecture that turns source files into a navigable Diátaxis site, plus the
six intermediate contracts that make a documentation run reproducible.

## Contents

`cq components read ../../references/knowledge-documentation/architecture.md`
returns the heading index; `--sections <name>` addresses one.

<!-- rules -->

## Diagnose first

Before proposing structure, inventory the sources read-only:

```bash
rg --files -g '*.md'
rg -n '^#{1,3} ' .knowledge/documentation
rg -n '\]\(' .knowledge/documentation | rg -v 'http'
```

Record, in two to five lines, audience and intent, site state, and faults. Use this fault table:

| Fault | Signal | Fix |
| --- | --- | --- |
| Orphan page | `.md` not in nav (or in nav, no file) | wire it or report it |
| Duplication | same fact in two or more pages | one home, other pages link |
| Weak title | filename-as-title or `README` | rename to an intent |
| Wall of text | screens of prose without headings/lists/callouts | split and structure |
| Buried comparison | options described in prose | table or card grid |
| Buried process | steps described in prose | numbered list or Mermaid |
| Averaged page | beginner, expert and agent in one page | split or layer |

## Design by reader intent

Each page has exactly one intent. The usual top-level shape is:

| Section | Reader intent | Holds |
| --- | --- | --- |
| Get started | “Show me it works, fast” | landing, install, quick start |
| Guides / How-to | “Help me do a specific task” | task walkthroughs |
| Concepts | “Help me understand the model” | mental models, architecture |
| Reference | “Give me the exact detail” | APIs, options, catalogs |
| Maintain / Operate | “Keep it healthy” | operations, evolution, troubleshooting |

The narrative spine is landing → problem → solution → mental model → quick start → workflow →
reference → maintain. Use `navigation.footer` so the reader always has a next step.

## Reader journeys

Verify these three journeys end to end, without a dead end or forced backtracking:

- **5-minute evaluator:** landing → problem → quick start → verdict.
- **Working implementer:** quick start → guide → reference → troubleshooting.
- **Agent / LLM:** entry → matching heading → copyable contract or example.

## Navigation and routing table

Use `navigation.indexes` and relative links. Every section index carries a routing table:

| If you want to… | Go to |
| --- | --- |
| See it run in 30 seconds | [Quick start](../how-to/quick-start.md) |
| Understand why it is shaped this way | [Concepts](../explanation/index.md) |
| Look up an exact option | [Reference](../reference/index.md) |

<!-- rationale -->

The navigation answers a reader's question instead of mirroring storage. A short diagnosis catches
orphans and duplicated claims before prose makes them expensive to move.

## The seven output contracts

These are mandatory intermediate outputs. Produce them in order, show them once, and write pages
only after the plan is accepted. Store them in `.quenching/documentation/plan.md`, never as site
pages. If a contract cannot be filled, write `source gap: <what's missing>` rather than guessing.

### 1. Diagnosis

```markdown
### Diagnosis
- Sources found:      <files/dirs; who each is for>
- Target audience:    <primary readers + technical maturity>
- Current site state: <greenfield | existing nav shape | toolchain>
- Main problems:      <orphans · duplication · weak titles · walls · dumps>
- Truth/source risks: <claims with no obvious source; stats to verify>
- Visual opportunities: <where a flow/table/map would unlock a wall>
```

### 2. Reader journeys

```markdown
### Reader journeys
- 5-min evaluator:    landing → ? → ? → verdict (no full read needed)
- Working implementer: quickstart → guide → reference → troubleshooting
- Agent / LLM:        entry → matching heading → copy contract/example
```

### 3. Information architecture proposal

```markdown
### IA proposal
- New nav tree:       <intent-based sections & pages>
- Source → dest map:  <source.md → dest.md (+ split/merge)>
- Page intents:       <one intent per destination page>
- Out of scope:       <what is dropped and why>
- Becomes reference:  <which sources → reference pages>
- Becomes guide:      <which sources → how-to pages>
- Becomes concept:    <which sources → explanation pages>
```

### 4. Visual plan

```markdown
### Visual plan
- Cards:      <where "choose your path" applies>
- Tabs:       <where a concept has platform/profile/scenario variants>
- Mermaid:    <which flows/architectures/maps>
- Tables:     <which comparisons/params/decisions>
- Hero:       <landing(s) only>
- Badges:     <which pages get an info bar>
- Screenshots/assets: <need + strategy — proposed, see visual.md>
- NO visual:  <pages/sections that must stay plain text>
```

### 5. LLM-readability plan

```markdown
### LLM-readability plan
- TL;DR for agents:  <which pages carry a contract block>
- Input/output contracts: <which pages state them explicitly>
- Stable headings:   <headings that must not be renamed>
- Key anchors:       <#anchors agents will deep-link>
- Glossary/concept map: <exists? which terms defined once>
- Copyable examples: <which real commands/snippets>
```

### 6. Execution plan

```markdown
### Execution plan
- Files to edit:     <path → change>
- Markdown extensions needed: <attr_list, md_in_html, tabbed, emoji, mermaid, …>
- Risk per change:   <low | med | high — and why>
- Validation:        <strict build + visual QA + rubric threshold>
```

### 7. Mapa editorial de publicação

```markdown
### Mapa editorial de publicação
| Home | Decisão | Motivo | Público | Rota publicada |
| --- | --- | --- | --- | --- |
| documentation/ | publicar | <motivo> | <leitores> | <rota> |
| standards/ | publicar derivado | <motivo> | <leitores> | <rota ou índice> |
| concepts/ | não publicar | <motivo verificável> | — | — |
```

Inventarie `documentation/`, `standards/`, `concepts/`, `external/`, `catalog/` e `vision/`, além
do `glossary.md` na raiz. Cada linha decide **publicar**, **publicar derivado** ou **não publicar**;
nenhuma home recebe rota por implicação do nome. `publicar derivado` mantém a fonte fora do
`docs_dir` e declara a página, índice ou projeção que será servida. Uma decisão sem evidência fica
como `source gap:` no plano, nunca como conteúdo da página publicada.

## Contrato de catálogo derivado

Catálogos mantidos em `catalog/` são publicados como referência derivada, nunca como uma cópia
livre de toda a home. O contrato mínimo é:

| Parte | Contrato |
| --- | --- |
| Entrada | um inventário versionado com identificador estável, camada e fonte original |
| Índice camada/schema | `reference/catalog/index.md` agrupa primeiro por camada e depois por schema |
| Rota de detalhe | cada item usa `reference/catalog/<slug>.md`, com âncora estável e link de volta |
| Linhagem | cada item aponta para o arquivo-fonte, data/versão e transformação aplicada |
| Fronteira editorial | só campos aprovados no mapa são publicados; segredos, dumps e dados sem fonte ficam fora |

O índice é o único ponto de entrada no `nav`; páginas de detalhe são alcançáveis por links internos e
podem crescer sem uma entrada individual. A ausência de camada, schema ou fonte é um `source gap:` e
bloqueia a aceitação da projeção.

## Registro de capacidades

Cada capacidade específica do gerador recebe uma linha no plano de documentação com cinco campos:
`capability`, pré-requisito, decisão (`enabled` ou `disabled`), evidência de configuração/versão e
efeito HTML esperado. O registro também anota risco, `source gap:` e o teste que prova o efeito.
Uma capacidade sem pré-requisito ou fixture permanece desabilitada; a ausência é uma decisão
auditável, não um sucesso implícito.

## Recorte incremental e handoff

O recorte incremental é uma otimização, não uma nova fonte de verdade: `ref` deve resolver para um
commit existente, `timestamp` deve ser UTC e cada fonte deve apontar para exatamente um destino.
Ref inválida, plano ausente, renome/remoção ou dependência sem mapeamento fazem fallback para revisão
completa e entram no relatório como gap. Artefatos operacionais (planos, ledgers, scorecards e
relatórios) ficam fora de `docs_dir` e terminam em handoff explícito para commit humano.

## Invariants

- One idea and one reader intent per destination page.
- Claims without a source become `source gap:` entries in the ledger.
- Contracts are planning artifacts and stay outside `docs_dir`.
- Cada seção publicada precisa de conteúdo não vazio e de uma rota alcançável; contratos, TODOs e
  gaps permanecem no ledger interno, nunca na página servida.
- A home não publicada é uma decisão editorial explícita, com motivo; não é uma limitação silenciosa do gerador.
- Internal site links are relative and every page has a next step.
