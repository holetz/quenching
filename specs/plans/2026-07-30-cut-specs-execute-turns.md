---
slug: cut-specs-execute-turns
title: Cut /specs:execute's turn count through body wording
verification: per-section
---

# Cut /specs:execute's turn count through body wording

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

     AUDIENCE. Each section names who reads it. `## Overview`/`## Problem`/`## Proposal`/
     `## Design` are for the human — examples and plain language belong there.
     `## Handoff`/`## Tasks` are for agents — terse, with `files:`/`verify:`/`pattern:`
     metadata. An orchestrator never sends the human sections to an executor; that is what
     lets one file serve both audiences without bloating agent context. -->

## Problem

O custo de uma run de `/specs:execute` é `turnos × contexto` — a integral que o spec irmão
`reduce-execute-conclude-cost` mediu e cujo `## Design` D1/D2 já argumenta. Aquele spec ataca a
metade **contexto**: um subcomando de custo em `session.py`, `/skill:retro` lendo custo, a
delegação de executor no passo 5b, e dois standards. Este ataca a outra metade, **turnos**, e por um
mecanismo que aquele não toca: a redação do corpo de `/specs:execute` induz mais chamadas de
ferramenta do que o que ele garante exige.

Evidência de uma run real de 13 tasks (transcript `985b372b-348c-4911-a5dd-146ca0b4ab7b`, spec
`add-import-provenance`, medida por `session.py` em 2026-07-30): **93 tool calls** — 16 exatos
atribuídos a `/specs:execute` mais 77 de limite superior atribuídos ao stage — com
`repeatedReadTargets: 0`, `repeatedShellCommands: 0`, `interrupts: 0`, `interjections: 0`. Nada foi
lido duas vezes e nenhum comando de shell foi repetido: **não há desperdício de repetição a
colher**. O que sobra é estrutural, e é isto:

1. **`## Handoff` é especificado para ser reescrito depois de CADA task commitada** (passo 6). Numa
   spec de 13 tasks isso são 13 reescritas de ~400 palavras cada. Na run medida foram 4, e as quatro
   eram ~90% idênticas. O trilho de retomada por task já existe em `git log` mais os `subjects` que
   `specs.py status` devolve; o que só o Handoff carrega é o estado que nada deriva — uma sessão
   paralela no checkout, um hook não versionado, uma falha de desenho encontrada. Esse estado mudou
   três vezes na run inteira. A cadência deveria ser dirigida a evento (mudança de estado
   não-derivável, mais pausa e conclusão), não por task.

2. **O passo 5 apresenta d-e-f-g como atos separados**, então `verify` rodou como chamada própria,
   separada de `--check` e do commit. Encadear `verify && tick && commit` numa única chamada
   **preserva exatamente a ordenação que o corpo exige** — o `&&` é o que a impõe — e faz
   curto-circuito seguro na falha. São ~10 chamadas numa spec de 13 tasks, sem perder rigor algum.

3. **O passo 2 exige árvore limpa e não diz nada sobre ambiente quebrado.** Na run medida,
   `.claude/settings.json` fiava um hook que o commit `193578c` apagou; diagnosticar isso ad hoc
   custou ~10 chamadas. Uma verificação de uma linha — todo hook fiado resolve no disco? — o
   revelaria em uma.

4. **Um portão de seção reroda checks cujos insumos a seção não pode ter mudado.** Na run medida os
   três selftests rodaram no fecho da seção 1 e de novo em 5.1, quando o próprio spec declarava que
   nenhum script mudava. Um portão deveria ser escopado ao que a seção pôde quebrar.

5. **`/specs:execute` delega isolamento no passo 2 e nunca reconquista atribuição.** `session.py`
   arquiva o loop de build inteiro sob `/specs:isolate` (linhas 70-367) e deixa `/specs:execute`
   medido em 16 chamadas e 5,5 minutos — os passos 1 e 2 apenas. **Nenhum retro consegue medir o
   comando que é dono do build.** Isto é mais que um defeito de instrumentação: o grupo 1 de
   `reduce-execute-conclude-cost` constrói um relator de custo que herdaria essa má atribuição, então
   o achado precisa chegar àquele spec independentemente do que este entregar.

**Fronteira com `reduce-execute-conclude-cost`** (level 3, criticality high, stage ready, 14 tasks,
0 construídas): aquele spec é dono da medição de custo, da política de modelo, da delegação de
executor e dos dois standards de custo; o único ponto dele em `execute.md` é o passo 5b. Este spec
não toca 5b, não escreve standard de custo, não mexe em `session.py` e não propõe delegação. Se os
dois forem construídos, este deve vir depois, porque o achado 5 pode mudar o que aquele mede.

**O que ainda não foi decidido** e cabe ao `/specs:develop`: se o achado 5 se resolve aqui, no corpo
de `/specs:isolate`, ou é entregue ao spec irmão; e se um campo `constraint:` por task — que tornaria
a delegação de executor viável ao fazer a task se auto-briefar — pertence a este spec ou é mudança
de schema spec-driven, portanto de outro.
