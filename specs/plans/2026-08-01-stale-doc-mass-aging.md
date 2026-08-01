---
slug: stale-doc-mass-aging
title: Um resource glob amplo envelhece o bundle inteiro a cada branch
verification: per-section
---

# Um resource glob amplo envelhece o bundle inteiro a cada branch

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

Dois sintomas do mesmo mecanismo, os dois achados como by-product da conclusão de
`read-by-section-not-by-file` (2026-08-01) e **nenhum causado por ela**.

**Sintoma 1 — o `CLAUDE.md` promete um número que o skeleton não devolve.** A seção *Operating this
repo* diz que `python3 assets/hooks/okf-validate.py assets/docs` dá `0 error(s), 0 warning(s)`. Ele
devolve `0 error(s), 1 warning(s)`: `stale-doc` em `assets/docs/standards/agents/communication.md`,
cujo `timestamp: 2026-07-30` precede um commit de 2026-07-31 no `resource` dele. A promessa é
literalmente falsa hoje, e um `CLAUDE.md` que declara um número verificável errado treina toda
sessão futura a ignorar a diferença entre a promessa e o que ela mede.

**Sintoma 2 — o bundle do próprio repo devolve 26 `stale-doc`.** `okf-validate.py docs` sai com 0
erros e **26 warnings**, todos `stale-doc`. A causa é mecânica, não é apodrecimento real: quase todo
standard deste repo tem `plugins/quenching/**` (ou um glob igualmente amplo) no seu `resource`, e
`stale-doc` dispara quando o `timestamp` do doc precede o último commit que tocou esse glob. Como
**qualquer** branch que mexa no plugin toca esse glob, uma branch envelhece o bundle inteiro de uma
vez — 26 docs passam a "poder não descrever mais o que governam" porque um deles foi editado.

**Por que isso corrói o sinal.** `stale-doc` é a única **Advisory finding** do repo: a categoria
existe para o caso em que um check não consegue distinguir "errado" de "vale uma olhada", e ela só
funciona enquanto for pequena. A 26 por branch ela não é mais lida — vira ruído de fundo que some
com o resto, e o dia em que um `stale-doc` significar apodrecimento de verdade ninguém vai
distinguir dos outros 25.

**O que este spec NÃO deve assumir.** Que a saída certa seja estreitar os globs de `resource`: um
glob amplo pode estar correto — um standard sobre a superfície de comandos realmente governa
`commands/**`. Estreitar por reflexo troca ruído por uma mentira mais silenciosa. As saídas a
considerar e precificar incluem, sem ordem de preferência: estreitar onde o glob for de fato
frouxo; fazer `stale-doc` comparar contra os arquivos que o glob resolve em vez do glob todo;
tratar o warning como agregado em vez de por-doc; ou aceitar o número e consertar só a frase do
`CLAUDE.md`. Essa última é a mais barata e resolve só o sintoma 1.
