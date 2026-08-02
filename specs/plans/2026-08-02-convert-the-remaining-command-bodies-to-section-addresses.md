---
slug: convert-the-remaining-command-bodies-to-section-addresses
title: Converter os outros vinte e cinco corpos à doutrina de §endereço
verification: per-section
---

# Converter os outros vinte e cinco corpos à doutrina de §endereço

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

     MOMENT. Each section belongs to one of three moments on the spec's timeline: `decision`
     (the human, deciding whether to build), `build` (the executor, in step 4 of
     `/specs:execute`), `close` (`/specs:conclude`, at archive time). `## Discoveries` belongs
     to none of them — captured indiscriminately while building, resolved later by
     `/specs:develop`'s triage sweep on its own schedule. An orchestrator sends an executor
     exactly the `build` set; that is what lets one file serve every moment without bloating
     agent context. -->

## Problem

`docs/standards/automation/context-discipline.md` §Open less regra 2 declara, desde 2026-08-02, que
**uma citação de referência num corpo de comando É um endereço `§`** — e que um caminho nu é um
finding, não um estilo. A regra é escrita como regra da **superfície inteira** e está **provada em
um comando só**: `/quenching:specs:execute`, que é onde a medição existe. O próprio standard diz
isso em voz alta — *"Converting the other twenty-five command bodies to this shape is future work;
only `/quenching:specs:execute` is converted today."*

Este spec é esse trabalho.

**O que a conversão de um comando rendeu**, medido pelo `narrow-the-execute-preamble` (arquivado
2026-08-02): o preâmbulo daquele comando caiu de 160.856 para 111.583 chars por turno, **−30,6%**,
e **−61,2%** contra o ponto de partida de antes de `read-by-section`. Todo char do preâmbulo é
re-enviado em todo turno da run, então o corte é multiplicado pela run inteira.

**Por que a extrapolação não é o argumento.** O `## Out of Scope` daquele spec recusou converter os
vinte e cinco de uma vez por duas razões que continuam valendo e que este spec tem de responder,
não ignorar: o número de qualquer outro comando seria **estimativa** — e esta front já derrubou uma
estimativa de 25–35% para 7% medidos —, e vinte e seis corpos numa branch é um raio de explosão
que nenhuma revisão de branch lê de verdade.

**A regra a aplicar tem três metades**, todas de `context-discipline.md` §Open less regra 2, e a
experiência de aplicá-las uma vez diz que a terceira é a que escapa:

1. todo `§`endereço carrega o arquivo a que pertence, no mesmo link ou colado nele;
2. um endereço nunca é partido por quebra de linha — **foi o que a revisão de branch pegou duas
   vezes no único comando já convertido**, reintroduzido por uma task posterior à que escreveu a
   regra;
3. um passo do próprio corpo é `passo 5g`, nunca `§5g` — o `§` fica com um sentido só.

Sobe junto a regra que o mesmo standard carrega: **uma referência usada só num ramo condicional é
lida naquele ramo**, não no preâmbulo que todo turno paga.

## Discoveries

- Decidir o lote: os 25 numa branch é o raio de explosão que narrow-the-execute-preamble recusou; por front (docs/specs/skill) ou por comando são as alternativas óbvias.
- A regra 2 (endereço nunca partido por quebra de linha) só foi pega por revisão de branch, duas vezes, no único comando convertido — vale medir se um check de skills.py lint sobre citações é barato o bastante para substituir a leitura humana.
