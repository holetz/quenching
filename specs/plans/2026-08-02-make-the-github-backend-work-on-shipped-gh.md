---
slug: make-the-github-backend-work-on-shipped-gh
title: O backend github funciona no gh que os repos realmente tem
verification: per-section
---

# O backend github funciona no gh que os repos realmente tem

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

## Overview

O backend `github` só roda num `gh` recente, sem dizer isso a ninguém, e a única prova que ele tinha
— o E2E da task 4.6 de `configurable-spec-backend` — rodou num ambiente que por acaso tinha a versão
certa. Esta spec troca a dependência por uma que o `gh` tem há muito mais tempo, e transforma a
falha restante numa recusa nomeada.

É a segunda vez que a mesma coisa acontece: uma capacidade provada uma vez, contra o caso que a
prova escolheu, encontrando a realidade na migração. `## Design` registra o que isso diz sobre a
forma de provar um backend externo.

## Problem

O backend `github` lista as issues de um repositório com `gh api --paginate --slurp`, e `--slurp`
**não existe antes do `gh` 2.52**. O `gh` deste ambiente é o 2.45.0 que a distribuição empacota, e
`list_specs` — a primeira primitiva que qualquer comando toca — morre com:

```
github refused listing the repository's issues — gh said: unknown flag: --slurp
```

Duas coisas erradas nisso, e a segunda é a pior:

1. **O backend não funciona no `gh` que um repositório realmente tem.** Nada no plugin declara uma
   versão mínima de `gh` — nem o README, nem `plugin-configuration.md`, nem a recusa
   `sp-gh-missing`, que fala em *instalar* o GitHub CLI como se qualquer versão servisse.
2. **A falha não é uma recusa nomeada.** `sp-gh-api-error` repassa a linha crua do `gh`, e o
   contrato que a task 4.1 de `configurable-spec-backend` estabeleceu é que cada modo de falha
   chega **nomeado e com o seu próprio remédio**. "unknown flag" não diz ao humano que a sua cópia
   do `gh` é velha, e nem que atualizar resolve.

A escolha do `--slurp` está documentada em comentário — `--paginate` sozinho concatena um array
JSON por página, o que não é um documento JSON — e a razão é correta. O que não foi verificado é se
havia outra forma de resolver o mesmo problema sem exigir uma versão que a task 4.6 tinha por acaso.
Medido em 2026-08-02 neste ambiente: `gh api --paginate --jq '.[]'` devolve **JSONL compacto**, um
objeto por linha, e funciona no 2.45.

## Proposal

- A listagem de issues deixa de usar `--slurp` e passa a `--paginate --jq '.[]'`, que devolve
  **JSONL** — um objeto JSON compacto por linha — e é entendido pelo `gh` que as distribuições
  empacotam hoje.
- O parsing passa a ser linha a linha, sem a estrutura de páginas: o backend nunca precisou da
  página, precisava dos itens.
- **Um `gh` velho demais para o que o backend pede vira recusa nomeada** — `sp-gh-too-old`, exit 2,
  dizendo a versão encontrada, o que falta e que `gh` atualizar resolve. Nunca mais uma linha crua
  de "unknown flag".
- A versão mínima de `gh` passa a estar **declarada** onde um humano a procura: no README, ao lado
  do custo do binário externo.

## Out of Scope

- **A migração das specs deste repositório** — é `migrate-this-repo-to-github-backend`, bloqueada
  nesta e retomada depois dela.
- **Uma checagem de versão de `gh` na abertura do backend** — pagar um `gh --version` por processo
  para prevenir um erro que a própria chamada já reporta é custo em todo caminho feliz para cobrir o
  infeliz. A recusa nomeada é reativa de propósito.
- **`az` e a mesma pergunta de versão** — o `azure-boards` continua sem prova end-to-end, e
  inventar um requisito de versão para ele seria mais um palpite não provado.
- **Os cinco achados abertos do conclude de `configurable-spec-backend`** — continuam com as suas
  próprias specs.

## Impact

### Standards this spec will write into docs/standards/

- none — a regra que isto revela (uma capacidade provada uma vez vale só contra o caso que a prova
  escolheu) já está escrita em `docs/standards/quality/unproven-capability-warning.md` e em
  `spec-backend.md` §"What this standard does not yet cover", ambas da leva anterior. O que falta
  aqui é aplicá-las, não escrevê-las de novo.

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/specs.py` — a listagem do `GitHubBackend` e a recusa nomeada
- `plugins/quenching/README.md` — a versão mínima de `gh`, ao lado do custo do binário externo

## Validation

- `python3 assets/bin/specs.py selftest` — a lista de casos de recusa do `gh` ganha a saída literal
  do `gh` 2.45 **deste ambiente** (`unknown flag: --slurp`), capturada e não inventada, exigindo
  `sp-gh-too-old`.
- **A listagem funciona de verdade contra este repositório**, com o `gh` 2.45 instalado: um
  `list_specs()` que devolve a lista sem exceção — hoje ela levanta `BackendRefusal`.
- Nenhuma issue é criada por esta spec: a prova é de leitura.
- `python3 assets/bin/skills.py --root . doctor --json` → 26 comandos, 0 findings.
- `python3 assets/hooks/okf-validate.py docs` → 0 error(s).

## Design

- **Decisão: `--jq '.[]'` e JSONL, não `--slurp` nem paginação própria.** O `gh` aplica o filtro por
  página e concatena as saídas, então o problema que o `--slurp` resolvia — "um array por página não
  é um documento" — desaparece pela raiz: o consumidor nunca quis o array, quis os itens. Paginar à
  mão (ler o header `Link`) resolveria também e devolveria ao nosso código a paginação que a decisão
  de transporte de `configurable-spec-backend` foi tomada para não ter.
- **Decisão: a incompatibilidade de versão é recusa reativa, não checagem preventiva.** Nomear
  `sp-gh-too-old` a partir do que o `gh` disse custa zero no caminho feliz; um `gh --version` na
  abertura custa um subprocess a toda invocação para cobrir um erro que a própria chamada já
  reporta. O mesmo raciocínio que faz `open_github_backend` resolver o repositório sob demanda.
- **Registrado: o que este bloqueio diz sobre provar um backend externo.** O E2E da task 4.6 rodou e
  passou; ele provou que o backend funciona **naquela máquina**, e a versão do `gh` era uma variável
  que ninguém declarou nem mediu. É o mesmo formato do defeito anterior — a spec de teste não tinha
  grupos `### N.` — e a lição já está escrita em `spec-backend.md`: *um backend é provado pelos
  documentos que ele vai realmente receber, não pelos que foram escritos para exercitá-lo*. Vale
  igual para o ambiente.

## Alternatives Considered

- **Declarar `gh >= 2.52` como requisito e não mudar o código:** rejeitada — empurra para todo repo
  alvo a obrigação de instalar um `gh` fora do gerenciador de pacotes, para comprar uma flag que uma
  alternativa disponível há anos substitui.
- **Paginar à mão pelo header `Link`:** rejeitada — devolve ao nosso código a paginação que a
  decisão "o transporte delega aos CLIs oficiais" existe para não ter.
- **Uma checagem de versão na abertura do backend:** rejeitada — ver `## Design`; custo no caminho
  feliz para cobrir o infeliz.

## Open Decisions

- none — a substituição, a forma da recusa e o lugar da declaração estão decididos em `## Design`.

## Risks

- **`--jq` muda o formato de saída numa versão futura do `gh`** — `ACCEPTED`: é a mesma família de
  aposta que o `--slurp` era, com a diferença de que `--jq` é anterior e muito mais usado.
  *Mitigação:* o parsing tolera linha vazia e recusa nomeadamente uma linha que não seja JSON, em
  vez de estourar.
- **A recusa `sp-gh-too-old` casa por texto do `gh`** — `ACCEPTED`: é como todas as outras recusas
  de transporte já funcionam (`GH_REFUSAL_CASES` e os seis sinais de stderr do `az`). *Mitigação:* o
  caso do selftest usa a saída literal deste ambiente, capturada e não escrita à mão.
- **A migração fica parada mais um ciclo** — `ACCEPTED`: o estado intermediário custa nada, porque
  nenhum spec saiu do disco ainda e a config continua declarando `files`.

## Handoff

- A saída literal a capturar é a do `gh` 2.45.0 deste ambiente: exit 1, stderr `unknown flag:
  --slurp`, seguido do bloco de uso. Vale capturar o fragmento e não a saída inteira.
- `gh api --paginate --jq '.[]'` foi verificado aqui: devolve JSON **compacto**, um objeto por
  linha, mesmo sem `-c` — o `gh` não usa a formatação indentada default do jq.
- O `sub_issues` é endpoint REST puro e responde normalmente no 2.45; nada mais no backend depende
  de flag recente.
- Nenhuma escrita é necessária para provar esta spec. `list_specs()` contra `holetz/claude-quenching`
  é leitura, e hoje ela levanta `BackendRefusal`.

## Tasks

### 1. A listagem funciona no gh empacotado

- [ ] 1.1 Trocar `--slurp` por `--paginate --jq '.[]'` e ler JSONL linha a linha, tolerando linha
      vazia e recusando nomeadamente uma linha que não seja JSON
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 assets/bin/specs.py selftest
      subject: plan/make-the-github-backend-work-on-shipped-gh: 1.1 listagem por JSONL, sem --slurp
- [ ] 1.2 Recusa nomeada `sp-gh-too-old` (exit 2) para um `gh` velho demais, com o caso do selftest
      usando a saída literal do gh 2.45 deste ambiente
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 assets/bin/specs.py selftest
      subject: plan/make-the-github-backend-work-on-shipped-gh: 1.2 recusa nomeada sp-gh-too-old
- [ ] 1.3 Provar `list_specs()` contra este repositório com o gh 2.45 instalado — sem criar nada
      subject: plan/make-the-github-backend-work-on-shipped-gh: 1.3 list_specs real contra o gh 2.45

### 2. O requisito passa a estar declarado

- [ ] 2.1 README nomeia a versão mínima de `gh`, ao lado do custo do binário externo
      files: plugins/quenching/README.md
      verify: python3 assets/bin/skills.py --root . doctor --json
      subject: plan/make-the-github-backend-work-on-shipped-gh: 2.1 README declara a versao minima de gh
