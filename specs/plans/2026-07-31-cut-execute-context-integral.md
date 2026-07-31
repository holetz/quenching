---
slug: cut-execute-context-integral
title: Cut the context integral of /specs:execute
verification: per-section
---

# Cut the context integral of /specs:execute

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

O custo de uma run é `turnos × contexto`. O spec `cut-specs-execute-turns`
(`archive/2026-07-30`) atacou a metade **turnos**, pela redação do corpo. Este ataca a metade
**contexto**, por um mecanismo que nenhum spec existente toca: **quando** e **quanto** entra na
janela.

A run que construiu aquele spec foi medida por código lendo o próprio transcript —
`session-evidence.md` §The rule a counted claim must obey, nunca por recordação — em 344 turnos:

- integral total **17,4M tokens-turno**;
- **6 chamadas de `Read` = 35%** dela (6,09M), contra 15% das 67 chamadas de `Bash`;
- a maior única: **um `Read` do arquivo da spec, 7.735 tokens no turno 13, repago 331 vezes =
  2,56M — 15% da sessão inteira**.

A ordenação é o achado: seis leituras pesaram mais que sessenta e sete chamadas de shell por mais
de dois para um, por serem maiores e terem chegado antes. Uma chamada barata feita cedo custa mais
que uma cara feita tarde.

Três coisas seguem disso, todas medidas na mesma run:

1. **O passo 4 manda ler a spec com `Read`, e `specs.py section` já existe.** As seis seções que o
   passo 4 exige custam 5.358 tokens via `section` contra 8.555 do arquivo — **−37,4%**, ou ~1,06M
   tokens-turno naquela run, 6% do total. A diferença é quase toda o comentário HTML do template:
   ~37 linhas idênticas em toda spec, sem informação nenhuma sobre a spec que as carrega.

2. **Ler a referência inteira quando a edição é de uma seção.** Na mesma run os dois padrões
   coexistiram, o que dá uma comparação direta: `execution.md`, `execute.md` e `task-execution.md`
   lidos inteiros custaram 2,86M tokens-turno; `artifacts.md`, `spec-driven.md` e `conformance.md`
   lidos por seção caíram dentro do total de `Bash`, a ~800 chars por chamada — e serviram
   exatamente as mesmas edições.

3. **A integral é quadrática nos turnos, e nenhum comando oferece parar.** Um bloco que entra no
   turno 13 é repago nos 331 seguintes. Duas sessões de 172 turnos custam ~metade de uma de 344
   pelo mesmo trabalho. O `## Handoff` — agora com cadência de quatro eventos — mais `git log` e os
   `subjects` de `specs.py status` já são o trilho de retomada completo. Nada usa isso:
   `/quenching:specs:execute` roda até acabar, e nada sugere fechar a sessão numa fronteira de seção.

O entendimento por trás dos três está em `docs/standards/automation/context-budget.md` §The other
half, `authority: background` porque é uma run. O que falta é o comando mudar.

## Proposal

- O passo 4 de `/quenching:specs:execute` lê as seções da spec por `specs.py section`, não o
  arquivo inteiro.
- A doutrina **"cite a seção, não o arquivo"** vira regra escrita: um comando que edita uma seção
  de uma referência lê aquela seção. Vale para todo comando que cita uma referência, não só para a
  frente specs.
- `/quenching:specs:execute` passa a **oferecer parar numa fronteira de seção** quando a janela já
  é longa, nomeando o comando que retoma. Oferece, nunca impõe — e a retomada não custa nada de
  novo, porque o `## Handoff` e o `git log` já a suportam.

## Out of Scope

- **O instrumento de medição de custo** — `session.py` ganhando um subcomando de custo,
  `/quenching:skill:retro` lendo custo, a política de modelo. É do `reduce-execute-conclude-cost`,
  grupo 1, que está `ready` com 14 tasks e 0 construídas.
- **A decisão de delegar um executor** (passo 5b). Mesmo spec irmão.
- **A metade turnos.** Entregue por `cut-specs-execute-turns`, já arquivado e merged.
- **Um limiar numérico para "a janela já é longa".** Inventá-lo antes de medir é fixar o resultado;
  a oferta pode ser dirigida a evento, como a cadência do `## Handoff` já é.

## Validation

Medir com o mesmo método que produziu o `## Problem`: rodar `/quenching:specs:execute` sobre um
spec de tamanho comparável e comparar a integral `tokens × turnos restantes` por categoria.

- Reportar os **pares crus** de cada lado, cada um carregando o `closed` / `mayIncludeTurnsFrom`
  que `session.py` anexa.
- **Não subtrair** um limite superior de um número exato — a mesma razão que `cut-specs-execute-turns`
  registrou na sua própria `## Validation`, e a razão de aquele spec não ter afirmado nenhum
  "cortou N turnos".
- Toda contagem vem de código lendo o transcript, nunca de um modelo recordando a própria run.

## Risks

- **Ler por seção pode esconder contexto que a leitura inteira dava de graça.** Uma edição
  informada pelo arquivo todo pode ser melhor que uma informada por uma seção — e a diferença não
  aparece numa medição de tokens.
- **Parar e retomar move custo em vez de eliminá-lo** se a sessão nova precisar reler muito para
  recuperar o estado. É exatamente o que o `## Handoff` existe para impedir, mas isso é a hipótese
  a medir, não um fato estabelecido.
- **Os três números vêm de UMA run.** O entendimento está em `context-budget.md` como
  `authority: background`, e este spec não deve tratá-lo como provado.
