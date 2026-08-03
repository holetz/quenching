---
slug: close-the-files-backend-leaks-in-specs-py
title: Close the four files-backend leaks left in the shared layer of specs.py
verification: per-section
---

# Close the four files-backend leaks left in the shared layer of specs.py

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

A spec `configurable-spec-backend` moveu `specs.py` para uma interface de cinco primitivas sobre o
documento canônico, com os oito verbos da CLI como código compartilhado por cima. A revisão da
branch, no conclude, encontrou **quatro pontos onde o backend `files` ainda vaza por essa camada
compartilhada** — todos registrados como `## Discoveries` daquela spec e nenhum deles um defeito no
que foi entregue. Nenhum quebra o backend `files`; três são inertes ou mentirosos sob um backend
externo, e o quarto é uma lacuna de asserção.

1. **`cmd_promote` deriva `dest_path` do `root` e chama `os.path.exists` para `sp-dest-exists`**
   ([specs.py:3830](plugins/quenching/assets/bin/specs.py:3830)). Sob `github` ou `azure-boards` a
   checagem sempre passa — o caminho não existe e nunca existiria. "Destino ocupado" precisa virar
   uma pergunta ao backend, ou sair da camada compartilhada.
2. **`cmd_doctor` lê o `root` cru** (`os.path.isdir` em
   [specs.py:6021](plugins/quenching/assets/bin/specs.py:6021), `os.listdir` mais abaixo), sem
   `open_backend`. Isso é deliberado — diagnosticar não pode criar a worktree de specs — mas num
   repo já migrado ele reporta `sp-no-workspace` **falsamente**. Falta um modo resolve-mas-não-crie.
   `cmd_migrate` é da mesma família: opera sobre um `specs/` que num repo migrado não existe mais.
3. **O campo `root` do JSON emite o root declarado**, não o resolvido, em oito sites de `emit`. Sob
   um backend externo ele não significa nada, e `list` chega a imprimir `no specs under /…/specs`
   tendo consultado o GitHub. Os bodies dos comandos consomem esse valor.
4. **O selftest só tem a asserção específica `sp-plans-subcommand-back`** contra as duas superfícies
   (argparse e `DISPATCH`). Falta a genérica `set(parser.choices) == set(DISPATCH)`: um subcomando
   registrado em só uma das duas passaria despercebido, que é exatamente a forma de um revert
   parcial.
