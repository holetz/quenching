---
slug: fix-skills-read-sections-splitting-on-commas
title: Consertar --sections de skills.py read partindo o valor na vírgula
verification: per-section
---

# Consertar --sections de skills.py read partindo o valor na vírgula

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

`skills.py read --sections` quebra o valor **na vírgula, incondicionalmente**, então toda seção
cujo título contém uma vírgula é inendereçável pelo nome completo — a chamada recusa com `exit 2`.

**Medido em 2026-08-02** (spec `narrow-the-execute-preamble`, `## Risks`): **sete** das seções das
cinco referências que `/quenching:specs:execute` cita caem nisso, três delas em `execution.md`,
incluindo a maior — `§The commit — one per task, carrying its own ticked box`, 4.638 chars.

**Pior, a mensagem de erro lista a seção recusada em `available:`** — ela diz que a seção existe e
recusa a entregá-la, o que é o oposto de um erro acionável.

**A repro é esta própria front, duas vezes.** O `narrow-the-execute-preamble` contornou escrevendo
toda citação em **forma de prefixo** que pare antes da vírgula — o `§The commit` do corpo já
funcionava por sorte, não por regra. E a conclusão daquele spec, em 2026-08-02, teve de citar
`§Tooling asides` para endereçar a seção `## Tooling asides, relocated` que ela mesma acabara de
criar. O contorno funciona e é barato; o defeito é que ele é obrigatório e invisível até morder.

É da mesma família de
[fix-the-files-field-parser-splitting-on-commas-inside-parentheses](/specs/plans/2026-08-02-fix-the-files-field-parser-splitting-on-commas-inside-parentheses.md),
e é **outro parser em outro call site**: aquele é `specs.py next` partindo `files:`, este é
`skills.py read` partindo `--sections`.

**Por que agora.** `docs/standards/automation/context-discipline.md` §Open less passou a declarar,
como regra da superfície inteira, que toda citação de referência num corpo de comando é um
endereço `§`. Converter os outros vinte e cinco corpos multiplica por vinte e cinco a chance de
alguém escrever o nome completo de uma seção com vírgula e receber `exit 2` no turno 1.

## Discoveries

- A forma de prefixo é o contorno em uso hoje e funciona; decidir se o conserto a mantém válida (compatibilidade) ou se --sections passa a exigir o nome completo.
