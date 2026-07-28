---
slug: fix-conclude-abandoned-branch-harvest
title: conclude --outcome abandoned can harvest a note and delete it in the same run
verification: per-section
---

# conclude --outcome abandoned can harvest a note and delete it in the same run

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

`/specs:conclude --outcome abandoned` destila na branch de trabalho e **depois**
oferece apagar essa mesma branch. Uma nota `authority: background` â€” a Ãºnica
colheita que o caminho abandonado permite â€” pode ser escrita e jogada fora na
mesma execuÃ§Ã£o, sem que nada avise.

A ordem herdada do caminho `done` Ã© a causa: lÃ¡ a destilaÃ§Ã£o precede o merge, e
o merge Ã© o que leva os commits da branch para a base. No caminho abandonado
nÃ£o hÃ¡ merge, entÃ£o nada carrega a nota para fora da branch antes da oferta de
deleÃ§Ã£o.

Descoberto ao fechar `move-conclude-merge-last`, cujo `## Out of Scope`
congelou deliberadamente o caminho abandonado â€” entÃ£o o defeito atravessou a
spec intocado e existe hoje apenas como uma linha em `## Discoveries`.

Duas saÃ­das plausÃ­veis, nenhuma decidida: commitar a nota na base antes de
oferecer a deleÃ§Ã£o (mas entÃ£o hÃ¡ escrita na base num comando que nÃ£o mergeia),
ou recusar a deleÃ§Ã£o enquanto a destilaÃ§Ã£o tiver escrito algo, dizendo o que
seria perdido.
