---
slug: migrate-this-repo-to-github-backend
title: Migrar as specs deste repositório para o backend github
verification: per-section
---

# Migrar as specs deste repositório para o backend github

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

Esta spec executa a migração que `configurable-spec-backend` deixou declaradamente para depois:
mover os specs deste repositório do backend `files` na branch do código para o backend `github`,
e apagar a pasta local no mesmo movimento.

`## Problem` diz por que o estado atual não é neutro; `## Proposal` lista o que passa a ser verdade
e o que sai do repo; `## Design` registra as decisões de execução — a idempotência do migrador, o
ritmo contra o rate limit e a ordem em que a config entra; `## Risks` carrega o que uma migração
parcial custa e o que a torna retomável. A correção de fidelidade que a torna segura é a spec
`fix-github-backend-tasks-fidelity` e **não** faz parte desta.

## Problem

As specs deste repositório continuam na branch do código — **44 em `specs/plans/` e 24 em
`specs/archive/`, com 700 tasks**, medido em 2026-08-02 e crescendo a cada spec nova. É exatamente o estado que `configurable-spec-backend` foi escrita
para acabar, e que ela declarou fora do próprio escopo: *"as specs deste repositório continuam na
branch do código — a migração é trabalho à parte, e é por isso que `task-execution.md` documenta que
este repo ainda tica com `--subject` antes da commit"*.

Enquanto isso durar, este repositório paga as duas dores do `## Problem` daquela spec **e** não
exercita o próprio produto que entrega: os três backends existem, o `github` foi provado end-to-end
uma vez contra uma spec de teste descartável, e nenhum repo real roda sobre ele. Um backend que
ninguém usa é um backend cujas regressões ninguém sente.

Há ainda um custo específico deste repo: `task-execution.md` documenta o anchor por `--subject`
antes da commit **como concessão temporária** a um workspace não migrado, quando o anchor por sha
já é o que os standards preferem. A concessão só se aposenta quando a migração acontece.

## Proposal

- `.claude/quenching.json` passa a declarar `backend: github`. É a única chave necessária:
  `specsBranch` só vale para o `files`, `azureStates` só para o `azure-boards`, e este repo não usa
  `worktreeSetup`.
- **Todos os specs viram issues** em `holetz/claude-quenching` — os de `plans/` abertas, os de
  `archive/` fechadas — e as 700 tasks viram sub-issues, ticadas ou abertas conforme o documento.
- **`specs/plans/` e `specs/archive/` saem do repositório em uma commit.** O git guarda o conteúdo
  no histórico e `specs.py export` regenera o markdown sob demanda; manter as duas cópias é manter
  dois lugares que parecem a fonte da verdade.
- `specs/QUENCHING.md` — o manual do operador — **fica**. Ele é instalado pelo plugin e não é um
  spec; o que sai é o store, não a documentação da frente.
- O migrador é **idempotente e retomável**: um spec já presente no GitHub é pulado, então uma
  interrupção por rate limit se resolve rodando de novo.
- Depois da migração, `python3 specs.py list --json` sobre o GitHub devolve os mesmos specs, com
  as mesmas fases, estágios derivados, records e contagens de task que o backend `files` devolvia
  antes — comparados por igualdade, não por inspeção.

## Out of Scope

- **A correção de fidelidade do backend `github`** — é a spec `fix-github-backend-tasks-fidelity`,
  pré-requisito desta e não parte dela.
- **Os cinco achados abertos do conclude de `configurable-spec-backend`** — `sp-dest-exists` inerte,
  `doctor` reportando `sp-no-workspace` falso, o campo `root` mentindo, a asserção genérica de
  dispatch e o `/specs:align` sem pasta. Nenhum impede a migração; os dois primeiros ficam
  **visíveis** depois dela, que é o argumento de as specs deles existirem.
- **Reescrever `task-execution.md` para o anchor por sha** — a concessão do `--subject` fica de pé
  aqui e se aposenta na spec que a mede depois de a migração assentar; trocar a ordem de tick e
  commit no meio de uma migração é misturar dois riscos.
- **Reduzir o custo de rede do backend `github`** — 33 chamadas para um ciclo de 12 comandos é
  discovery registrada naquela spec, e vira dor de uso diário, não de migração.
- **Trocar de backend outra vez** — nada aqui constrói caminho de volta. `specs.py export` é o que
  torna uma saída futura viável, e ele já existe.

## Impact

### Standards this spec will write into docs/standards/

- none — a migração não descobre regra nova: o contrato do backend está em
  `docs/standards/architecture/spec-backend.md` e o da config em
  `docs/standards/workflows/plugin-configuration.md`, ambos escritos por
  `configurable-spec-backend` e nenhum contradito aqui. O que esta spec produz é **estado**, não
  contrato.

### Product code this spec expects to touch

- `.claude/quenching.json` — criado, com `backend: github`
- `specs/plans/**`, `specs/archive/**` — removidos do repositório após a migração verificada
- `CLAUDE.md` — a seção "Where knowledge lives" descreve `specs/plans/` como pasta em disco

## Validation

- **Igualdade antes-e-depois, medida e não inspecionada**: `specs.py list --json` e
  `specs.py status --spec <slug> --json` para todos os specs são capturados sobre o backend `files`
  **antes** da migração e comparados campo a campo com os mesmos comandos sobre o `github` depois.
  Divergem por construção apenas `path` (caminho de arquivo contra URL da issue) e `root`, este
  último por um achado já registrado.
- **`specs.py section --spec <slug> --moment build` devolve texto idêntico** nos dois lados, para os
  todos eles — a prova de que a serialização híbrida sobreviveu ao dado real, e não só ao selftest.
- `git status --porcelain` vazio ao fim, e `specs/` contendo apenas `QUENCHING.md`.
- `python3 assets/bin/skills.py --root . doctor --json` → 26 comandos, 0 findings.
- `python3 assets/hooks/okf-validate.py docs` → 0 error(s).
- `specs.py doctor` é rodado e seus achados **registrados**, não corrigidos: `sp-no-workspace` falso
  num repo migrado é achado conhecido com spec própria, e vê-lo aqui é a confirmação de que aquela
  spec descreve algo real.

## Design

- **Decisão: a migração usa as cinco primitivas do backend, nunca `gh` à mão.** O migrador importa
  `specs.py` e chama `create_spec(phase, filename, text)` com o documento lido do disco — que é o
  caminho que `create_spec` já declara existir para exatamente este caso (*"only matters for the
  migration path that hands `create_spec` a document that already carries tasks"*). Um script que
  montasse issues por conta própria seria uma segunda serialização, e a primeira leitura pela CLI a
  desmentiria.
- **Decisão: a idempotência é por slug, e é o que torna a migração retomável.** Antes de cada
  criação o migrador consulta `list_specs()` e pula o que já existe. Cerca de 1.500 chamadas mutantes contra
  os secondary rate limits do GitHub tornam a interrupção o caso provável, não o excepcional — e a
  alternativa a retomar é limpar 67 issues à mão.
- **Decisão: uma pausa deliberada entre chamadas de escrita.** O GitHub recomenda ao menos um
  segundo entre requisições que criam conteúdo, e o limite secundário não é o de 5.000/h que o
  `X-RateLimit-Remaining` mostra — é outro, e ele responde 403 sem contador. Ir devagar de propósito
  é mais barato que descobrir o teto no meio de setecentas sub-issues.
- **Decisão: a config entra ANTES do apagamento e DEPOIS da verificação.** A ordem é: migrar com o
  backend ainda em `files` (o migrador abre o `github` explicitamente, sem depender da config),
  verificar a igualdade dos dois lados, escrever `.claude/quenching.json`, verificar de novo pela
  CLI, e só então remover a pasta. Declarar `github` antes de haver algo lá torna todos os specs
  invisíveis a todo `/specs:*` — o pior estado intermediário disponível.
- **Decisão: o apagamento da pasta é uma commit própria, separada da migração.** Uma commit que
  apaga 67 arquivos é o registro que um humano vai procurar quando quiser o conteúdo de volta, e
  misturá-la com a config a esconde.
- **Decisão: as issues criadas não recebem label alguma.** A fase é o estado da issue e os sete
  records ficam no frontmatter dentro do corpo — as duas decisões são de `configurable-spec-backend`
  (tasks 4.2 e a docstring de `GitHubBackend`), e uma label acrescentada só na migração seria um
  fato que só os specs migrados carregam.
- **Decisão: o `## Discoveries` desta spec é onde a migração registra o que ela mesma revelar.** Uma
  migração é a primeira execução real do backend sobre dado que não foi escrito para ele; o que
  aparecer ali é achado, não defeito desta spec, e vai para uma spec própria.

## Alternatives Considered

- **Migrar só `plans/` e deixar `archive/` como markdown inerte:** rejeitada — corta a migração pela
  metade em custo, e deixa o histórico partido em dois lugares: uma spec concluída depois vira issue
  fechada, as 24 antigas não. Um `specs.py list` que não enxerga metade do arquivo é pior que um
  demorado.
- **Backend `files` em branch dedicada, em vez de `github`:** rejeitada — resolve as duas dores
  originais e é muito mais barata, mas não exercita o backend externo que este repositório entrega e
  ninguém usa. É também a alternativa que `configurable-spec-backend` já pesou e recusou em
  `## Alternatives Considered`.
- **Manter os arquivos como snapshot congelado ao lado do GitHub:** rejeitada — dois lugares que
  parecem a fonte da verdade, e nada declarando qual vence. O git já é o snapshot, e ele não se
  confunde com um store.

## Open Decisions

- none — o backend, o escopo (tudo), a remoção da pasta local e a ordem de execução foram decididos
  antes da spec ser escrita; `## Design` os registra.

## Risks

- **Uma migração interrompida deixa metade dos specs em cada lado** — `MITIGATED`: o migrador é
  idempotente por slug e a config só entra depois da verificação, então o estado intermediário é
  "alguns specs também existem no GitHub", com o backend `files` ainda autoritativo e todo comando
  funcionando. Retomar é rodar de novo.
- **Os secondary rate limits do GitHub barram a migração no meio** — `ACCEPTED`: ~1.500 chamadas
  mutantes é muito acima do que a API espera de uma sessão. *Mitigação:* pausa deliberada entre
  escritas, e a idempotência acima transforma um 403 em "rodar de novo mais tarde".
- **Perder o acesso ao GitHub passa a ser perder as specs** — `ACCEPTED`, e é a decisão de
  `configurable-spec-backend` §"o backend selecionado é a fonte da verdade", não uma escolha nova
  desta spec. *Mitigação:* `specs.py export --all`, mais o histórico do git, que guarda os
  arquivos na commit anterior à remoção.
- **`/specs:align` para de funcionar neste repositório** — `ACCEPTED`: é o único body ainda acoplado
  ao backend `files`, e o que ele significa sem pasta é decisão de produto que
  `decide-what-specs-align-means-without-a-folder` foi criada para tomar. As outras oito operam
  pelas primitivas.
- **`doctor` passa a reportar `sp-no-workspace` falso e `list` a mentir o campo `root`** —
  `ACCEPTED`: os dois estão registrados em `close-the-files-backend-leaks-in-specs-py`. Vê-los é a
  confirmação de que aquela spec descreve algo real, e a `## Validation` os registra em vez de os
  corrigir.
- **Um documento que o backend não remonta fielmente é perda silenciosa** — `MITIGATED` pelo
  pré-requisito: `fix-github-backend-tasks-fidelity` prova o round trip byte a byte sobre estes
  mesmos documentos antes que qualquer um deles saia do disco.

## Handoff

- **Esta spec não começa antes de `fix-github-backend-tasks-fidelity` estar mergeada.** O bloqueio é
  concreto e medido: sem ela, os grupos `### N.` de 47 specs somem na escrita e não voltam pela CLI.
- `gh` 2.45 está autenticado neste ambiente como `holetz`, com escopos `repo`/`read:org`/`workflow`.
  `holetz/claude-quenching` é privado, tem issues habilitadas e **zero issues hoje** — os quatro
  itens que `repos/:owner/:repo/issues` devolve são pull requests, que `_load` já descarta.
- A API de sub-issues (`repos/:owner/:repo/issues/:n/sub_issues`) foi exercitada pelo E2E da task
  4.6 de `configurable-spec-backend` contra este mesmo repositório, e a issue de teste foi removida
  ao fim. Não há resto daquele exercício.
- O migrador é código descartável e **não** entra em `plugins/quenching/` — o produto declara a
  migração automática entre backends fora de escopo, e um script de uma vez só neste repo não é
  motivo para reverter aquela decisão.
- Ordem de grandeza medida em 2026-08-02: 68 issues-mãe, 700 sub-issues, 24 fechamentos —
  **~1.500 chamadas mutantes**, na casa de 30 a 45 minutos com a pausa entre escritas.

## Tasks

### 1. Capturar o estado de partida

- [ ] 1.1 Capturar `list --json` e `status --json` de todos os specs sobre o backend `files`, mais o
      texto de `section --moment build` de cada um, como baseline em disco fora do repo
      verify: python3 assets/bin/specs.py list --json
      subject: plan/migrate-this-repo-to-github-backend: 1.1 captura o baseline de todos os specs sobre files
- [ ] 1.2 Confirmar que o pré-requisito está mergeado — o round trip híbrido devolve todos os
      documentos byte a byte
      verify: python3 assets/bin/specs.py selftest
      subject: plan/migrate-this-repo-to-github-backend: 1.2 confirma a fidelidade do round trip antes de escrever

### 2. Migrar

- [ ] 2.1 Escrever o migrador descartável — importa `specs.py`, abre o backend `github`
      explicitamente, pula por slug o que já existe e pausa entre escritas
      subject: plan/migrate-this-repo-to-github-backend: 2.1 migrador idempotente sobre as cinco primitivas
- [ ] 2.2 Ensaiar contra UM spec com grupos e uma task de título longo, conferir a issue e as
      sub-issues, e remover o que o ensaio criou
      subject: plan/migrate-this-repo-to-github-backend: 2.2 ensaio de um spec com grupos e titulo longo
- [ ] 2.3 Rodar a migração de todos os specs, retomando quantas vezes o rate limit exigir
      subject: plan/migrate-this-repo-to-github-backend: 2.3 migra todos os specs para issues e sub-issues

### 3. Verificar e assumir o backend

- [ ] 3.1 Comparar campo a campo o baseline da 1.1 com os mesmos comandos sobre o `github`, com
      `path` e `root` como as únicas divergências admitidas
      subject: plan/migrate-this-repo-to-github-backend: 3.1 igualdade campo a campo entre files e github
- [ ] 3.2 Escrever `.claude/quenching.json` com `backend: github` e reconfirmar pela CLI, sem
      `--root` e sem variável de ambiente
      files: .claude/quenching.json
      verify: python3 assets/bin/specs.py config --json
      subject: plan/migrate-this-repo-to-github-backend: 3.2 declara backend github em .claude/quenching.json
- [ ] 3.3 Rodar `specs.py doctor` e registrar seus achados em `## Discoveries` sem corrigi-los
      subject: plan/migrate-this-repo-to-github-backend: 3.3 registra os achados do doctor num repo migrado

### 4. Tirar a pasta do repositório

- [ ] 4.1 Remover `specs/plans/` e `specs/archive/` em uma commit própria, mantendo
      `specs/QUENCHING.md`
      files: specs/plans, specs/archive
      verify: git status --porcelain
      subject: plan/migrate-this-repo-to-github-backend: 4.1 remove o store local, mantendo o manual do operador
- [ ] 4.2 Atualizar `CLAUDE.md` — `specs/plans/` deixa de ser pasta em disco e passa a ser o que
      `specs.py list` deriva do GitHub
      files: CLAUDE.md
      verify: python3 assets/bin/skills.py --root . doctor --json
      subject: plan/migrate-this-repo-to-github-backend: 4.2 CLAUDE.md descreve a frente sem pasta local
