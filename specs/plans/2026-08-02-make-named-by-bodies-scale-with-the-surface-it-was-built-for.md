---
slug: make-named-by-bodies-scale-with-the-surface-it-was-built-for
title: Make named_by_bodies scale with the surface it was built for
verification: per-section
---

# Make Named By Bodies Scale With The Surface It Was Built For

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

`named_by_bodies` (`plugins/quenching/assets/bin/skills.py`) deriva, dos corpos de comando, o
conjunto de comandos que outro comando alcança **por nome** — o predicado do finding
`sk-inert-stage`. Ele compara **todo corpo contra todo nome**, com dois regexes por par, logo é
O(n²) em bytes de corpo.

**Medido nesta árvore em 2026-08-02**, na revisão de branch de
`route-commands-without-always-on-descriptions`, que é o spec que o criou:

| superfície | `named_by_bodies` |
| --- | ---: |
| 26 comandos (a real) | **195 ms** |
| 260 comandos (duplicando a real 10×) | **18.246 ms** |

93× para 10×, que é quadrático limpo (n^1,99). O método: duplicar os 26 comandos com nomes
sufixados e cronometrar a função direto, sem o resto do `lint`.

**Por que isso importa, e não é micro-otimização.** O spec que construiu o instrumento se
justifica inteiro por uma superfície de ~250 comandos — é o item 5 de `## Open Decisions` dele,
respondido "sim, ~250 é o alvo" — e a promessa que ele vende é "um custo que **para de crescer**
com n". O instrumento que ele entregou para proteger essa promessa cresce com n². No tamanho-alvo,
`lint` passa a levar ~18 s antes de reportar o primeiro finding.

Três agravantes:

- `cmd_lint` chama `named_by_bodies` em **toda** execução, inclusive `lint <um arquivo só>` — e
  nesse caso ele ainda re-descobre a superfície inteira do disco, porque o corpo que nomeia um
  estágio quase nunca é o arquivo sendo lintado.
- `lint` está na rotina de verificação declarada do `CLAUDE.md`, então o custo é pago por quem
  segue o manual.
- Os regexes são construídos como string e passados a `re.search`, que os compila via cache de 512
  entradas. A 250 comandos são ~500 padrões distintos por caller — bem no limite do cache, então
  parte do custo vira recompilação. Isso é secundário ao n², mas fica pior exatamente no
  tamanho-alvo.

**O que não está errado.** O predicado é **correto** e está provado por mutação: sete mutantes,
incluindo apagar cada braço e o descarte da barra inicial, todos pegos pelo `selftest`
(`docs/standards/quality/selftest-mutation.md` §*The second pass*). Nada aqui pede mudar o que ele
decide — só como ele chega lá. Uma reescrita que mude o conjunto de alvos é uma regressão, e o
`selftest` existente é o portão que diz isso.

**A forma candidata**, registrada como ponto de partida e não como decisão: uma varredura única por
corpo, com um regex de alternation sobre todos os nomes compilado uma vez, trocando n×n buscas por
n. Nenhuma medição foi feita sobre ela.
