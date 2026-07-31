---
slug: collapse-remaining-language-clause-restatements
title: Collapse Remaining Language Clause Restatements
verification: per-section
---

# Collapse Remaining Language Clause Restatements

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

O spec `declare-repo-body-language` instalou o dono único da regra de língua em
`docs/standards/agents/communication.md` e colapsou **seis** reenunciações — as normativas, que
vivem em `docs/` e `plugins/quenching/assets/references/`. Ele deliberadamente deixou as demais de
fora, e registrou o porquê e o censo completo em seu `## Open Decisions`: as que restam são **texto
de template entregue**, que aterra em um repositório-alvo que pode não ter bundle algum para citar,
ou **condição lateral dentro de body de comando**, que é a surface em inglês que aquele
`## Out of Scope` protege. As duas categorias precisam de decisões diferentes das seis já feitas, e
é por isso que este spec existe separado.

**O censo, transcrito para que ninguém precise redescobri-lo** (custou uma passagem adversarial no
spec anterior; as linhas são as de então e devem ser reconferidas):

- `plugins/quenching/assets/README.md:115`
- `plugins/quenching/assets/templates/harness/claude-root.md:71`
- `plugins/quenching/assets/templates/harness/claude-subfolder.md:32`
- `plugins/quenching/assets/bin/specs.py:292`
- `plugins/quenching/assets/specs/templates/spec.md:39`
- `plugins/quenching/commands/docs/add.md:37`
- `plugins/quenching/commands/docs/align.md:79`
- `plugins/quenching/commands/docs/define.md:76`
- `plugins/quenching/commands/docs/learn.md:41` e `:79`
- `plugins/quenching/commands/docs/harness.md` passo 7 — **a décima-primeira**, encontrada durante a
  execução e registrada na `## Discoveries` daquele spec, fora do censo original

**A restrição que o spec anterior já descobriu:** as gêmeas de template obrigam edição em par —
`assets/bin/specs.py` e `assets/specs/templates/spec.md` carregam o mesmo texto sob a regra "edit
both or neither".

**E a restrição que a revisão de branch daquele spec acrescentou:** um artefato que um align copia
para o repositório-alvo **não pode citar o que a cópia não instala**. `plugin-layout.md`
§*A mold cites nothing it does not also install* foi emendada por aquele conclude justamente para
enunciar isso pelo teste em vez de por uma pasta só. Isso decide boa parte deste spec de antemão:
para as entradas de `assets/templates/**` e `assets/specs/templates/**`, colapsar em uma citação ao
doc dono seria **exatamente** a violação que aquela regra descreve — o alvo pode não ter o bundle.
Provavelmente a resposta certa ali é manter o enunciado autocontido, como `okf-spec.md` já faz, e
não colapsar. O trabalho real deste spec é decidir isso categoria por categoria, com evidência.
