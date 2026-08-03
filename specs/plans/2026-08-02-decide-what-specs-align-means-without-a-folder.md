---
slug: decide-what-specs-align-means-without-a-folder
title: Decide what /specs:align means on a backend with no folder, filename or rename
verification: per-section
---

# Decide what /specs:align means on a backend with no folder, filename or rename

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

`align.md` é o **único body de `/specs:*` ainda acoplado ao backend `files`**: ele inventaria por
`Glob specs/plans/*.md` e stampa frontmatter direto no arquivo. A spec `configurable-spec-backend`
migrou os outros oito bodies para leitura granular por `specs.py` e deixou este de fora
deliberadamente, registrando o porquê como discovery — não por falta de tempo, mas porque **o que
`/specs:align` significa num backend externo é uma decisão que aquela spec não tomou.**

O comando existe para forçar o workspace numa forma canônica. Quase tudo que ele faz pressupõe um
sistema de arquivos:

- **escanear a pasta** — não há pasta; há uma query ao backend;
- **normalizar filename e slug** — não há filename; o slug é o título ou um campo da issue;
- **renomear** — não há rename; há um update de campo, e um rename acoplado a código nem sequer é a
  mesma operação;
- **dobrar layouts antigos** (`backlog/`+`ready/` → `plans/`, v1 três-arquivos → um) — não há layout
  antigo possível num store que nasceu depois deles;
- **instalar `specs.py` e o manual do operador** — isso continua valendo, e é a parte que não
  depende do backend.

Sobra um resto real: stampar frontmatter faltando e regenerar o que for derivado. Mas se a
convergência de um backend externo é só isso, `/specs:align` sob `github` pode ser um comando quase
vazio — e vale decidir se ele **diz isso e para** (o que o body já faz hoje, com uma frase acrescida
pela spec anterior), se ele ganha um significado próprio por backend, ou se a operação some e o
probe do front passa a responder "nada a convergir aqui" como resultado conformante.

A decisão precede o código. Esta spec é para tomá-la.
