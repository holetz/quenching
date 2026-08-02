---
slug: fix-the-files-field-parser-splitting-on-commas-inside-parentheses
title: Fix the `files:` field parser splitting on commas inside parentheses
verification: per-section
---

# Fix The Files Field Parser Splitting On Commas Inside Parentheses

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

`specs.py next` quebra o campo `files:` de uma tarefa **separando por vírgula sem respeitar
parênteses**, então um comentário entre parênteses dentro de um caminho vira um caminho falso
entregue ao executor.

**Repro registrada**, descoberta na tarefa 0.1 de
`route-commands-without-always-on-descriptions` (arquivado 2026-08-02, `## Discoveries`). O campo
escrito no spec era:

```
files: plugins/quenching/commands/zzprobe.md (descartável, revertido ao fim)
```

e `specs.py next` devolveu **duas** entradas, partindo na vírgula de dentro dos parênteses:

```
plugins/quenching/commands/zzprobe.md (descartável
revertido ao fim)
```

**Por que é pior do que parece.** O consumidor do `files:` é um executor — humano ou agente — que
recebe a lista como "os arquivos desta tarefa". Nenhum dos dois pedaços existe no disco, e nem o
parser nem o executor têm como saber a diferença entre um caminho inventado por um bug de parsing e
um caminho que a tarefa vai **criar**, que é o caso normal de uma tarefa que escreve arquivo novo.
Logo o modo de falha é silencioso: o executor recebe lixo com a mesma confiança que recebe um
caminho real.

**O que ainda não se sabe**, e é trabalho de `/specs:develop` e não deste `## Problem`:

- se o defeito está só em `next` ou no leitor de `files:` compartilhado, e portanto se `task`,
  `parallel` e `status` dividem o mesmo bug;
- se a correção é o parser respeitar parênteses, ou se `files:` deveria **recusar** um comentário
  em vez de tentar interpretá-lo — as duas respostas são defensáveis e a segunda é mais barata;
- se algum spec vivo hoje carrega um `files:` com parênteses, o que decide se isto é urgente ou
  apenas correto.

Nada disso foi consertado pelo spec que descobriu: ele estava medindo outra coisa, contornou
escrevendo o caminho sem comentário, e registrou.
