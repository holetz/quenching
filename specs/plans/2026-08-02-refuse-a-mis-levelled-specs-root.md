---
slug: refuse-a-mis-levelled-specs-root
title: specs.py passa em silêncio quando --root aponta um nível acima do workspace
verification: per-section
---

# specs.py passa em silêncio quando --root aponta um nível acima do workspace

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

`specs.py --root` quer o **diretório `specs/` em si**; `skills.py --root` quer o **container** que
tem `commands/` ou `.claude/` embaixo. As duas ferramentas do mesmo plugin usam o mesmo nome de
flag para níveis diferentes da árvore, e as duas documentam isso corretamente no `--help`:

```
specs.py   --root ROOT   the specs/ workspace directory (default: nearest specs/ upward)
skills.py  --root ROOT   the surface root holding commands/ (default: nearest .claude/ or commands/ upward)
```

O problema não é a semântica divergente — é o que acontece quando alguém erra o nível. Medido
neste repositório em 2026-08-02, com 58 specs no workspace e `--root .` apontando a raiz do repo:

| Invocação | Saída | Exit |
| --- | --- | --- |
| `specs.py --root . list` | `no specs under <raiz>` | **0** |
| `specs.py --root . validate` | limpo | **0** |
| `specs.py --root . status` | recusa | 2 |
| `specs.py --root <specs/ vazio de verdade> list` | `no specs under <dir>` | 0 |

Três problemas compostos:

1. **O falso-vazio é indistinguível do vazio real.** A linha impressa e o código de saída de um
   root errado são iguais aos de um workspace genuinamente vazio. Todo corpo de comando do plugin
   é instruído a *"branch on the exit code, never on prose"* — e o código de saída aqui não
   carrega a diferença.
2. **`validate` passa sem ter lido nada.** Sai 0 sobre 58 specs que nunca abriu. Uma validação que
   passa por não olhar é pior que uma que falha.
3. **A ferramenta discorda de si mesma.** Mesma entrada errada, três subcomandos, dois códigos de
   saída: `status` recusa com 2, `list` e `validate` passam com 0. `status` já demonstra que a
   recusa é o comportamento pretendido.

**Por que o erro de nível é provável, não hipotético.** O bloco de verificação do
[CLAUDE.md](/CLAUDE.md) ensina `skills.py --root . doctor` a partir de `plugins/quenching/`, onde
`--root .` é a resposta certa. Transferir esse hábito para `specs.py --root .` é o caminho de menor
resistência, e a resposta que se recebe é um sucesso silencioso. Aconteceu numa sessão real de
`/skill:align` nesta data, e só foi percebido porque o número (`0 specs`) contradizia um `ls` feito
segundos antes.

**O que este spec NÃO afirma.** Que a semântica de `--root` deva ser unificada entre as duas
ferramentas. Talvez deva, mas isso é uma mudança de superfície com custo próprio, e um root mal
nivelado que recusa já remove o dano sem tocar em nenhum chamador existente.
