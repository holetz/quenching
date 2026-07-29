---
slug: fix-functional-checks-encoding
title: functional-checks.sh fails for lack of evidence, not by verdict
verification: per-section
priority: {level: 2, criticality: high, complexity: 2, date: 2026-07-28}
---

# functional-checks.sh fails for lack of evidence, not by verdict

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

## Overview

- none — only `## Problem` is filled; nothing else exists yet to connect.

## Problem

`assets/bin/functional-checks.sh` nÃ£o consegue gatear nada no Windows, e falha
de um jeito que se parece com um veredito real.

A linha 32 lÃª a captura `--output-format stream-json` com um `open()` sem
encoding. O stream Ã© UTF-8; o default da plataforma no Windows Ã© cp1252, entÃ£o
a leitura levanta `UnicodeDecodeError`, `tools()` nÃ£o emite nada, e **toda
asserÃ§Ã£o falha por falta de evidÃªncia** â€” indistinguÃ­vel, na saÃ­da, de uma
superfÃ­cie que nÃ£o carregou.

Medido trÃªs vezes em 2026-07-28: a `main` pristina (`96f6657`) marcou 3
passed/6 failed e a branch `plan/move-conclude-merge-last` marcou 4 passed/5
failed, com as mesmas cinco falhas de check 3 nas duas. O check 1a
("Read a file under assets/references/") **inverteu o veredito** entre execuÃ§Ãµes
idÃªnticas do mesmo script: FAIL na pristina, PASS na branch, FAIL de novo mais
tarde na mesma branch.

Da mesma famÃ­lia: `print()` em python escreve CRLF em stdout no Windows, entÃ£o
qualquer pipeline de shell que leia um valor de um heredoc python embutido
recebe um CR final â€” quebrou silenciosamente a asserÃ§Ã£o `git log --grep` do
`conclude-order-check.sh` atÃ© `tr -d '\r'` ser acrescentado.

A regra jÃ¡ estÃ¡ escrita: `docs/standards/quality/surface-verification.md`
Â§As quatro prÃ©-condiÃ§Ãµes, item 4 â€” ler a evidÃªncia com encoding explÃ­cito, e
tratar um stream de zero eventos como **inconclusivo**, nunca como falha. O que
falta Ã© o script obedecÃª-la.

Enquanto isso, `functional-checks.sh` continua declarado OBRIGATÃ“RIO no
`## Validation` de specs que tocam `commands/**`, e nÃ£o pode cumprir esse papel.
