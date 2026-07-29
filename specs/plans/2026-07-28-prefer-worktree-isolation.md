---
slug: prefer-worktree-isolation
title: Prefer worktrees for spec isolation and remove them after a successful merge
verification: per-section
priority: {level: 20, criticality: medium, date: 2026-07-28}
---

# Prefer worktrees for spec isolation and remove them after a successful merge

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

Duas coisas a ajustar na isolação de uma spec, ambas sobre worktree.

A primeira: `/specs:isolate` oferece branch **ou** worktree, e hoje a branch é o
caminho de menor atrito — o worktree é a alternativa que só aparece quando
alguém pede. Deveria ser o contrário: uma spec construída num worktree deixa o
repositório principal intocado, o que permite trabalhar em várias specs em
paralelo e mantém a árvore limpa que `/specs:execute` exige. A preferência
precisa inverter, sem que a branch simples deixe de ser possível.

A segunda: nada apaga o worktree depois. `/specs:conclude` termina no merge —
essa é sua última ação — e o worktree fica no disco, ao lado do repositório,
apontando para uma branch já integrada. Quem conclui várias specs acumula
diretórios órfãos que ninguém sabe se ainda são necessários. Depois de um merge
bem-sucedido, o worktree deveria ser removido.

Fica em aberto o quanto disso é automático: remover um worktree é irreversível
para qualquer trabalho não commitado que ainda esteja nele, e `conclude` já
oferece — sem executar — a deleção da branch.
