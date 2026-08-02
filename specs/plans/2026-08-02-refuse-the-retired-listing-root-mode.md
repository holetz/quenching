---
slug: refuse-the-retired-listing-root-mode
title: okf-validate aceita o modo --listing-root aposentado e julga specs/ como bundle
verification: per-section
---

# okf-validate aceita o modo --listing-root aposentado e julga specs/ como bundle

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a fourteen-heading skeleton. Every other heading below is created on
     first write by `specs.py section <slug> "<Heading>" --write`, which inserts it in the
     canonical position with the guidance comment kept here.

     THE STAGE-SCOPED EXPLICIT-NONE RULE. A heading is required — and required to carry
     `- none — <reason>` when it has nothing in it — only once ITS OWN gate is reached:

       new (capture)        `## Problem`
       ready (derived)      the nine definition sections (`## Problem` .. `## Risks`)
                            AND `## Tasks`
       ready (warn only)    `## Overview` non-empty, `## Handoff` non-empty
       promote -> archive/  `## Outcome`

     `ready` is a DERIVED STAGE, not a folder: a spec lives in `plans/` for its whole active
     life, and filling those ten sections is what makes it ready. Nothing refuses on that
     gate — it is a floor `execute` reports against, and the human's go-ahead is the
     `approved:` frontmatter record, asked for inline.

     Before its gate, a heading's absence is NOT an omission — it is a not-yet. After its
     gate, three rules decide whether a section counts as filled:

       1. `- none — <reason>` counts as filled. An omission and a null are different facts.
       2. A heading present with an EMPTY body is malformed and refuses. It is neither an
          answer nor a not-yet.
       3. An absent heading before its gate is legal.

     Headings are a PARSED contract — canonical English, exactly as written here. Body prose
     follows the repo's language. A heading outside this set is a stray and validate flags it.
     *(`standards/agents/communication.md` owns that language rule for a repo whose bundle has
     one. This template states it self-contained rather than citing it: `/specs:align` is native
     and installs here into repos that never adopted the bundle, where that path resolves to
     nothing.)*

     AUDIENCE. Each section names who reads it. `## Overview`/`## Problem`/`## Proposal`/
     `## Design` are for the human — examples and plain language belong there.
     `## Handoff`/`## Tasks` are for agents — terse, with `files:`/`verify:`/`pattern:`
     metadata. An orchestrator never sends the human sections to an executor; that is what
     lets one file serve both audiences without bloating agent context. -->

## Problem

[specs-align/conformance.md](/plugins/quenching/assets/references/specs-align/conformance.md)
§The OKF validator is never pointed at `specs/` é explícita nas duas metades:

> `plans/index.md` é um **artefato aposentado**. (…) Os quatro [códigos] se foram, junto com o
> **modo `--listing-root` que os lia**.

E, sobre por que a frente inteira fica fora do validador: um spec carrega `slug`/`title`/
`verification` e deliberadamente **nenhum `type:` OKF** — não é um concept doc, vive fora do
bundle, e `specs.py validate` é um contrato mais forte que presença-de-tipo.

Mas o modo aposentado **falha aberto**. Medido com a 4.5.0 do repo em 2026-08-02, sobre os 36
specs em `plans/`:

```
okf-validate.py specs/plans --listing-root   →  181 findings, exit 1
```

| Código | Ocorrências |
| --- | --- |
| `missing-type` | 36 |
| `missing-description` | 36 |
| `missing-resource` | 36 |
| `missing-timestamp` | 36 |
| `index-orphan` | 36 |
| `bundle-no-index` | 1 |

Cada uma das 181 é o validador exigindo de um spec exatamente aquilo que o contrato diz que um
spec deliberadamente não tem. A flag aposentada não é rejeitada: é aceita em silêncio, e o
validador roda o conjunto de regras de concept doc sobre arquivos que não são concept docs.

**Três consequências:**

1. **A recusa é o comportamento certo, e não acontece.** Uma ferramenta apontada para algo que ela
   não modela deve sair 2, como as outras da suíte fazem. Emitir 181 findings é afirmar que
   encontrou 181 problemas.
2. **Treina o operador a ignorar o validador.** 181 warnings que ninguém pode ou deve fechar são
   ruído que faz um finding real passar despercebido.
3. **A pressão que ele cria é para violar um invariante declarado.** A saída manda "regenerate the
   folder's index.md" e carimbar `type:`/`description:`/`resource:`/`timestamp:` — e o
   `/specs:create` lista, entre seus invariantes, *"Never stamp an OKF `type:` on a spec to quiet
   the bundle validator"* e *"never add frontmatter to `plans/index.md`"*. A ferramenta empurra
   para exatamente os dois atos que o comando proíbe.

**Como foi encontrado, e o agravante.** O corpo do `/specs:create` em cache (4.4.0) manda, no seu
passo 8, rodar `okf-validate.py specs/plans --listing-root` — um modo que a 4.5.0 já havia
aposentado. Seguir o comando ao pé da letra produz as 181. Atualizar o cache remove o chamador,
mas não o defeito: enquanto a flag for aceita, qualquer corpo antigo, runbook ou hábito continua
capaz de apontar o validador do bundle para uma frente que ele não modela.
