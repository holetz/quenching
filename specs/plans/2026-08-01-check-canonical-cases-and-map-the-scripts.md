---
slug: check-canonical-cases-and-map-the-scripts
title: Check the CANONICAL_CASES lockstep and make the shipped scripts navigable
verification: per-section
priority: {level: 31, criticality: low, complexity: 2, date: 2026-08-01}
---

# Check the CANONICAL_CASES lockstep and make the shipped scripts navigable

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

Os quatro scripts embarcados somam **7.399 linhas** — `assets/bin/specs.py` (3.108),
`assets/bin/skills.py` (1.980), `assets/hooks/okf-validate.py` (1.375) e `assets/bin/session.py`
(936) — e a pergunta que abriu esta captura foi a óbvia: quebrar em módulos e pôr um `CLAUDE.md`
para não precisar ler tudo. **Medindo, a primeira metade da pergunta já tem resposta escrita e a
segunda esconde um defeito.**

Do total, ~1.378 linhas são docstring e template embutido e ~662 são comentário: código real
≈ 4.400. E a duplicação entre scripts — o parser de frontmatter que aparece três vezes — é ~120
linhas × 3, **~3% do total**. Não é ela que faz os arquivos grandes; o que faz `specs.py` ter 3.100
linhas são catorze subcomandos mais `schema.json` e `templates/spec.md` embutidos como constantes.

Extrair um módulo compartilhado está **barrado por contrato já escrito**:
[frontmatter-parsing.md](/docs/standards/code/frontmatter-parsing.md) §Why there are three copies
and not one module. Cada script é copiado sozinho para o `.claude/hooks/` de um repo alvo pelo seu
próprio align, então um `frontmatter.py` extraído viraria um quarto arquivo a instalar, achar no
`sys.path` e versionar contra três chamadores — troca um problema de duplicação por um de
distribuição, num repo cujo contrato é stdlib-only, zero dependências e sem build step.

Sobra o que ninguém cobre, e o primeiro item é **defeito latente, não organização**:

1. **A lockstep de `CANONICAL_CASES` não tem verificador.** As três cópias estão byte-idênticas
   hoje — o segmento AST das três dá `sha256 73b3c6df9fcb`, catorze linhas cada, em
   `specs.py:743`, `skills.py:527` e `okf-validate.py:396`. Mas **nada prova isso**: cada
   `selftest` roda a *própria* lista contra o *próprio* parser, então acrescentar um caso em um só
   arquivo passa nos três. O mecanismo pega drift de **parser**, nunca drift de **lista** — e é
   justamente a lista que os três comentários chamam de unidade de lockstep (*"EDIT ALL THREE, OR
   NONE"*) e que o standard chama de *"the lockstep unit"*. Um check cross-tool que extrai o
   segmento AST das três e compara o hash fecha o buraco.

2. **Não há mapa de coordenadas dos scripts.** Os docstrings de módulo (80–109 linhas cada) já
   contam o que cada tool faz, mas nenhum diz *onde* está o quê, nem por que a duplicação existe —
   de modo que uma sessão futura refaz do zero a análise acima antes de descobrir que o módulo
   compartilhado está proibido. O repo já tem o molde do ponteiro fino em
   [docs/standards/CLAUDE.md](/docs/standards/CLAUDE.md), 22 linhas.

3. **Os banners de seção não são greppáveis.** Os arquivos separam seções com `# ---- #` sem
   marcador consistente, então não existe como obter um sumário sem abrir o arquivo — que é
   exatamente a leitura integral que se queria evitar.

Vizinhas verificadas, nenhuma cobrindo os três: `check-the-lockstep-itself` é o lockstep de
**versões** (`VERSION` × sete superfícies), vizinho mas distinto — aquele compara números de
release, este compara a lista de casos do parser, e como ambos propõem o `selftest` como casa, a
ordem de merge importa; `split-specs-py-backlog-renderer` e `dedupe-specs-py-spec-reader` tratam do
tamanho e da duplicação **internos** a `specs.py`, enquanto este é inter-arquivo e de navegação.
