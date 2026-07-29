---
slug: narrow-the-stale-doc-trigger-to-content-drift
title: Narrow The Stale Doc Trigger To Content Drift
verification: per-section
---

# Narrow The Stale Doc Trigger To Content Drift

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

O aviso `stale-doc` do `okf-validate.py` dispara quando o `timestamp` de um doc é anterior ao
último commit que tocou **qualquer** arquivo casado pelo seu `resource:`. Como os globs são largos
por bom motivo (`assets/**`, `specs/**`, ou os três scripts nomeados um a um), o gatilho mede
**atividade no raio do glob**, não deriva de conteúdo.

O efeito foi medido durante o `/specs:conclude` da spec `prefer-worktree-isolation`, em 2026-07-29.
A contagem em `docs/` na raiz saiu de **6** avisos `stale-doc` no início da revisão para **15** no
fim, ao longo de quatro commits legítimos:

- o bump do lockstep de versão tocou `specs.py`, `skills.py` e `okf-validate.py` — e um bump de
  versão toca as três ferramentas **por definição**, então acende todo doc cujo `resource:` nomeia
  qualquer uma delas;
- cada commit da própria conclusão (carimbo `reviewed`, `## Outcome`, a movimentação para
  `archive/`) tocou `specs/**`, acendendo todo doc cujo glob cobre o workspace.

Nenhum dos 15 docs teve o **assunto** alterado. Entre os acesos estão justamente
`ci-cd/versioning-release.md` (que descreve o lockstep corretamente e foi aceso por um lockstep
executado exatamente como ele manda) e `quality/parse-honesty.md`, `naming/command-surface.md`,
`workflows/plan-artifacts.md` — docs que ninguém encostou.

O problema não é o ruído em si, é o que ele faz com a decisão do humano. Com quase todo standard
aceso, `stale-doc` deixa de separar o doc que envelheceu do doc que apenas estava perto de uma
mudança. As duas saídas disponíveis hoje são igualmente ruins: recarimbar em massa é carimbar
`authority` sem lastro — a revisão de conteúdo que o carimbo alega não aconteceu — e ignorar em
massa é treinar o operador a não ler a única checagem que existe para desatualização. A spec
`prefer-worktree-isolation` recusou as duas e deixou os 15 avisos de pé, registrando o motivo.

Vale notar o que **não** é o problema: o `stale-doc` acerta quando o `resource:` é estreito. Dois
avisos desta mesma conclusão eram verdadeiros — `worktree-setup.md` e `plan-git-record.md`
carimbavam `2026-07-28` e tinham sido escritos em 2026-07-29 — e foram fechados por recarimbo
honesto. A regra não está errada em toda parte; ela perde resolução à medida que o glob cresce.

Fica em aberto qual é a correção: apertar o gatilho (comparar contra commits que tocam o assunto do
doc, e não o raio do glob), tratar mudanças que só mexem em versão como não-substantivas, mudar a
granularidade do `resource:`, ou reclassificar o achado. Relacionado, mas distinto, é
`2026-07-25-expose-finding-advisory-as-data`, que trata de **expor** a natureza advisory do achado
como dado — não da precisão do gatilho.
