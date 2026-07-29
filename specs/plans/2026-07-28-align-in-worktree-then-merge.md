---
slug: align-in-worktree-then-merge
title: Have the align commands propose a worktree and merge at the end, as specs already does
verification: per-section
---

# Have the align commands propose a worktree and merge at the end, as specs already does

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a thirteen-heading skeleton. Every other heading below is created on
     first write by `specs.py section <slug> "<Heading>" --write`, which inserts it in the
     canonical position with the guidance comment kept here.

     THE STAGE-SCOPED EXPLICIT-NONE RULE. A heading is required — and required to carry
     `- none — <reason>` when it has nothing in it — only once ITS OWN gate is reached:

       new (capture)        `## Problem`
       ready (derived)      the nine definition sections (`## Problem` .. `## Risks`)
                            AND `## Tasks`
       ready (warn only)    `## Handoff` non-empty
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

     AUDIENCE. Each section names who reads it. `## Problem`/`## Proposal`/`## Design` are for
     the human — examples and plain language belong there. `## Handoff`/`## Tasks` are for
     agents — terse, with `files:`/`verify:`/`pattern:` metadata. An orchestrator never sends
     the human sections to an executor; that is what lets one file serve both audiences
     without bloating agent context. -->

## Problem

Os aligns escrevem direto na árvore em que a sessão está. `/docs:align`,
`/specs:align`, `/skill:align` e o condutor `/align` podem tocar dezenas de
arquivos numa só varredura autorizada, e tudo isso cai no repositório principal
— sem branch, sem worktree, sem um ponto de integração no fim.

A frente de specs já resolveu isso: `/specs:isolate` tira o trabalho da árvore
principal e `/specs:conclude` faz o merge por último, de modo que uma única
integração carrega tudo o que a branch produziu. Os aligns não têm equivalente.

O ajuste pedido é dar aos aligns o mesmo formato: propor o uso de um worktree
antes de começar a escrever, e realizar o merge ao final da varredura.
