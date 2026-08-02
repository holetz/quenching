---
slug: align-descriptions-across-surfaces
title: Um align de descrições que resolve a superfície antes de revisar
verification: per-section
---

# Um align de descrições que resolve a superfície antes de revisar

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

O `/skill:align` resolve a superfície como `.claude/` e nunca pergunta **qual** superfície carrega
a massa de descrição. Como a descrição é o único texto sempre em contexto, revisar a superfície
errada não é uma revisão incompleta — é uma revisão que reporta limpo enquanto o custo real está
em outro lugar.

Medido numa run de `/skill:align` neste repositório em 2026-08-02:

| Superfície | Comandos | Chars | % do teto | Findings de descrição |
| --- | --- | --- | --- | --- |
| `.claude/commands/**` (a revisada) | 2 | 1.419 | 11% | 5 |
| `plugins/quenching/commands/**` (a real) | 26 | 12.756 | **99,1%** | **21** |

A run revisou 11% da superfície e reportou como se fosse a superfície. Os 21 findings — 11
`sk-trigger-position` e 10 `sk-no-boundary` — ficaram invisíveis porque o `budget` e o `lint` nunca
foram apontados para o diretório do plugin, que é onde este repositório de fato constrói comandos.
Num repo que *constrói* um plugin, `.claude/` é a superfície de desenvolvimento e
`plugins/*/commands/**` é o produto; a convenção aponta para a primeira e o custo está na segunda.

Quatro lacunas concretas do estágio de revisão de descrição atual (§8 do `/skill:align`), na
framing de quem pediu:

1. **Resolução de superfície não existe como estágio.** Nada enumera `.claude/commands/**`,
   superfícies escopadas por diretório (`**/.claude/commands/**`), `plugins/*/commands/**` e
   `.claude/agents/*.md`, nem mede cada uma com `budget --root` antes de escolher o que revisar.
2. **A amplitude não é derivada da pressão.** 99,1% do teto somado a 21 findings deveria forçar
   uma passada ampla e o comando dizer isso sozinho, sem flag e sem ser perguntado.
3. **O teste do competidor não escala para N=26.** Falta agrupar por namespace e rodar dentro
   antes de cruzado — e falta uma detecção que hoje não existe em lugar nenhum: **qual frase entre
   aspas aparece em duas descrições**, que é bug de roteamento decidível por parser, não por
   leitura.
4. **Agentes ficam fora.** O `budget` já os conta — 2.265 caracteres aqui, mais que os dois
   comandos locais somados — e o §8 os ignora inteiramente.

**A restrição que faz disto uma spec e não uma edição.** A superfície tem **119 caracteres de
folga** (12.756 / 12.875). A descrição de um 27º comando custa na faixa de 400–650, então cunhar
este comando estoura o teto **antes** de ele fazer qualquer trabalho. O re-baseline medido é parte
declarada do escopo, não contabilidade descoberta no fim — o mesmo mecanismo que
`restore-routing-info-on-docs-commands` já registra como o ratchet funcionando.

**Relação com as specs vizinhas.** `restore-routing-info-on-docs-commands` (plans/, prioridade 2,
criticidade alta, não construída) é o **conteúdo**: fecha os mesmos 21 findings uma vez, em 11
descrições nomeadas. Esta é o **instrumento**: recorrente, e sobre qualquer superfície. São
complementares — construir aquela não remove a causa que produziu esta, que é a resolução de
superfície.
