---
slug: cut-conclude-run-cost
title: Cut /specs:conclude's token volume, with session b5bb123f as the evidence
verification: per-section
---

# Cut /specs:conclude's token volume, with session b5bb123f as the evidence

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

Analisar com rigor a sessão `b5bb123f-96cb-44ed-b532-5b67945639f8` — uma run completa de
`/specs:conclude` sobre `narrow-the-execute-preamble`, 17:53→18:32 de 2026-08-02, 403 eventos, em
`~/.claude/projects/-home-holetz-Projects-claude-quenching--claude-worktrees-spec-flow-token-optimization-91188e/`
— em busca de melhorias implementáveis no estágio `conclude` que reduzam o volume de tokens gasto
para executar o comando.

O spec pode ser amplo: o objetivo declarado é o **maior ganho possível**, desde que relevante — não
a menor mudança que produz algum ganho.

Existe um spec irmão vivo, `reduce-execute-conclude-cost` (stage `ready`, 0/14 tasks), que cobre
custo de run de `/specs:execute` **e** `/specs:conclude` por outro eixo. A fronteira entre os dois
não está decidida.
