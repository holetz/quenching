---
slug: configurable-spec-backend
title: Configurable backend for spec management (files, GitHub, Azure DevOps)
verification: per-section
refined: {mode: gate, date: 2026-07-31}
approved: {date: 2026-07-31}
---

# Configurable backend for spec management (files, GitHub, Azure DevOps)

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

     AUDIENCE. Each section names who reads it. `## Overview`/`## Problem`/`## Proposal`/
     `## Design` are for the human — examples and plain language belong there.
     `## Handoff`/`## Tasks` are for agents — terse, with `files:`/`verify:`/`pattern:`
     metadata. An orchestrator never sends the human sections to an executor; that is what
     lets one file serve both audiences without bloating agent context. -->

## Overview

Este spec torna configurável **onde** os specs de um repositório vivem. Hoje são sempre arquivos em
`specs/`, na mesma branch do código — o que polui o histórico e faz a `main` perder o rastro de um
spec assim que o trabalho migra para uma branch. A partir daqui um repositório declara seu
**backend** — arquivos numa branch dedicada, GitHub ou Azure Boards — e nenhum deles deixa o spec
dividir branch com o código.

`## Problem` explica as duas dores; `## Proposal` lista o que passa a ser verdade, incluindo as duas
mudanças que ele arrasta — a leitura passa a ser granular, e o vínculo entre uma task e seu commit
passa a ser o sha em vez do subject. `## Design` registra as decisões que sustentam isso e por que a
arquitetura hoje declarada como "puramente nativa" precisa ser reescrita;
`## Alternatives Considered` guarda as formas mais baratas descartadas; `## Impact` nomeia os cinco
standards que o trabalho escreve ou reescreve; `## Risks` carrega o preço aceito — sem o binário do
backend externo (`gh`/`az`) e sem cópia local, um spec externo depende da ferramenta que o hospeda.
## Problem

Hoje o fluxo de specs depende de um conjunto de arquivos vivendo em `specs/` para funcionar. Isso
tem dois custos. O primeiro é que o acompanhamento de tarefas polui o código e o histórico do git,
misturando a gestão do trabalho com o trabalho em si. O segundo, e mais grave, é de visibilidade:
no momento em que o trabalho migra para uma branch, a `main` deixa de saber o que está acontecendo
com aquele spec — e pode facilmente concluir que ele ainda não começou a ser desenvolvido ou
executado, quando na verdade já está em andamento em outro lugar.

O que se busca é uma solução duradoura: uma CLI que, conforme configuração determinística do
repositório alvo, defina onde a gestão dos specs acontece — em arquivos, no GitHub ou no Azure
DevOps. No caso de arquivos, uma opção aventada para viabilizar a configuração é centralizar os
arquivos de specs em uma branch própria, de modo que a visibilidade não dependa da branch de
trabalho em que se está.

## Proposal

- Um repositório alvo declara em `.claude/quenching.json` qual backend é a **fonte da verdade** dos
  seus specs: `files` (numa branch dedicada), `github` ou `azure-boards`.
- **Nenhum backend deixa o spec dividir branch com o código.** O modo antigo — specs em `specs/` na
  mesma branch do trabalho — deixa de existir: era ele que causava as duas dores do `## Problem`,
  poluir o histórico e sumir da `main` quando o trabalho migra.
- A configuração do plugin deixa `specs/config.json` e passa a `.claude/quenching.json`, neutra
  entre as frentes — um repo com backend externo pode não ter **pasta `specs/` alguma**.
- A `main` enxerga o estado de um spec em andamento **independentemente da branch de trabalho**: o
  rastro do spec não desaparece quando o trabalho migra.
- Todos os comandos `/specs:*` e o `specs.py` operam **identicamente** sobre qualquer backend — o
  modelo conceitual (as 14 seções, os records de frontmatter, os estágios derivados) é o mesmo;
  muda apenas **onde e como** ele é serializado.
- A CLI expõe **leitura granular**: o agente pede uma seção ou uma task por vez e nunca é obrigado
  a receber o documento inteiro. O documento completo continua disponível sob pedido explícito.
- Quando o backend é externo, o spec vive na ferramenta externa **sem contraparte local
  autoritativa**.
- A serialização externa é **híbrida**: usa os construtos nativos da ferramenta onde há mapeamento
  (as tarefas de `## Tasks` viram sub-issues / itens filhos) e cai para markdown serializado onde
  não há equivalente.
- O vínculo task→commit passa a ser o **sha** em toda a superfície, em vez do subject.
- v1 implementa os três backends; `files` e `github` são validados neste repositório;
  `azure-boards` é entregue **sem validação end-to-end**.
## Out of Scope

- **Validação end-to-end do backend `azure-boards`** — implementado mas não exercitado neste
  esforço, por não haver ambiente Azure DevOps para provar aqui. Vira também um risco `ACCEPTED` e
  uma lacuna declarada de `## Validation`.
- **Sincronização bidirecional em tempo real / webhooks** — mudanças feitas direto na ferramenta
  externa não são refletidas por listeners vivos; leitura/escrita acontece via `specs.py`, não por
  sync contínuo.
- **Migração automática de specs existentes ao trocar de backend** — mudar `backend` em
  `.claude/quenching.json` não converte specs já criados de um store para outro.
- **A migração das specs deste repositório para a branch dedicada** — 32 specs em `plans/` e 20 em
  `archive/` continuam onde estão; movê-las é trabalho à parte. O `specs.py export` entregue aqui é
  o que a torna viável depois.
- **Manter o modo "specs na branch do código"** — deliberadamente removido, não deferido. Ele é a
  causa das duas dores do `## Problem`; mantê-lo como opção é manter o problema disponível.
## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/architecture/spec-backend.md` — a interface de backend, a fonte-da-verdade única,
  a serialização híbrida e a leitura granular
- `docs/standards/workflows/plugin-configuration.md` — `.claude/quenching.json` como casa única da
  config do plugin
- `docs/standards/workflows/worktree-setup.md` — reescrito: a config muda de `specs/config.json`
  para `.claude/quenching.json`, e o argumento de §"Why a config file, in a front that had none"
  muda com ela
- `docs/standards/workflows/task-execution.md` — reescrito: §"One commit per task" passa do anchor
  por subject com tick-antes-do-commit para o anchor por sha com tick-depois
- `docs/standards/workflows/plan-git-record.md` — reescrito: §"The task→commit link is the commit's
  own subject" deixa de valer

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/specs.py` — a interface de backend e as três implementações
- `plugins/quenching/commands/specs/*.md` — os nove bodies, de Read-no-caminho para leitura granular
- `plugins/quenching/assets/references/specs-develop/spec-driven.md` — a declaração "entirely
  native — no external CLI, no main spec store, no delta format" que esta spec reverte
- `plugins/quenching/assets/references/specs-isolate/git.md` — o contrato de `specs/config.json`
- `plugins/quenching/assets/references/specs-create/specs-front.md` — a resolução do tool
- `.gitignore` — `.claude/worktrees/`

## Validation

- `python3 assets/bin/specs.py selftest` — a lista canônica de casos roda contra o backend `files`
  E contra um backend fake em memória, com resultado **idêntico**. Esta é a prova da afirmação
  central do `## Proposal` ("todos operam identicamente"), e vale para os três sem tocar a rede.
- **Workspace descartável** para `files` em branch dedicada: `new` → `status`/`next`/`section`/
  `task` → `promote`, o protocolo que o `CLAUDE.md` já exige quando a lógica do `specs.py` muda.
- **`github`, end-to-end real neste repositório**: criar uma spec de teste, escrever três seções,
  criar duas tasks como sub-issues, ticá-las, promover, e remover a issue ao fim. Cada comando deve
  imprimir o **mesmo JSON** que o backend `files` imprime para o mesmo estado.
- `python3 assets/bin/skills.py --root . doctor --json` → 26 comandos, 0 findings.
- `python3 assets/hooks/okf-validate.py docs` → 0 error(s).
- O lockstep de versão: `VERSION` e as três ferramentas shipped concordam.
- `git status --porcelain` fica **vazio** depois de qualquer operação do backend `files` — a
  worktree persistente não pode sujar a árvore que `/specs:execute` exige limpa.
- **`azure-boards` não é exercitado end-to-end** — ver `## Out of Scope` e o risco `ACCEPTED`
  correspondente em `## Risks`.

## Design

- **Decisão: o backend selecionado é a fonte da verdade — não há store canônico duplicado.**
  Externo significa que o spec vive na ferramenta, sem cópia local autoritativa.
- **Contrato vinculante que esta decisão contradiz e portanto reescreve:**
  `plugins/quenching/assets/references/specs-develop/spec-driven.md` hoje afirma *"entirely native —
  no external CLI, no main spec store, no delta format"*. Esta decisão reverte isso: o backend
  externo **é** um store externo e a serialização híbrida reintroduz uma forma de mapeamento/delta.
  A declaração formal do standard-a-reescrever está em `## Impact`; a reescrita em si acontece no
  `/specs:execute`.
- **Decisão: `.claude/quenching.json` é a casa única da config do plugin.** Recebe a chave
  `backend` nova e absorve o `worktreeSetup` que hoje vive em `specs/config.json`. Realocar toca o
  standard `worktree-setup.md`, o glossário e a validação `sp-config-*` (que passa a ler o novo
  local).
- **Decisão: camada de mapeamento por backend.** Uma interface de backend em `specs.py`
  (list/status/show/section/task/discover/promote/validate) com implementações por target; a
  serialização híbrida (nativo onde possível, markdown senão) vive dentro de cada implementação
  externa.
- **Decisão: a leitura é granular por construção.** A CLI expõe seção-a-seção e task-a-task
  (`show --spec <slug> --section <Heading>` / `--task <id>`); o documento inteiro sai apenas sob
  pedido explícito. O risco que isto endereça não é de I/O, é de **contexto**: um agente que recebe
  as catorze seções para editar uma paga o custo em toda chamada. Cache local é liberdade de
  implementação interna do `specs.py` — **não** é um store: não é autoritativo, nada fora da CLI o
  lê, e a fonte da verdade segue sendo o backend.
- **Decisão: o transporte externo delega aos CLIs oficiais.** `gh api` e `az boards` via
  `subprocess`, não HTTP próprio. Auth, paginação e erros de API deixam de ser código nosso. Um
  binário ausente é uma **recusa (exit 2)** nomeando o binário e o `auth login` correspondente,
  nunca um traceback. Custo aceito e declarado: o backend externo não funciona sem o binário
  instalado — CI e container precisam provisioná-lo.
- **Decisão: o anchor task→commit é o sha, em toda a superfície.** O sha foi abandonado antes
  porque o anchor precisava entrar num arquivo versionado na branch do código, custando um commit
  de bookkeeping por task. Como nenhum backend deixa mais o spec dividir branch com o código, essa
  razão desaparece: no `files` a escrita cai na branch de specs, no externo cai fora do git. O sha
  é um vínculo estritamente mais forte — sobrevive a um `commit-msg` hook que reescreva a mensagem,
  que hoje é um caso de falha declarado. A ordem inverte: commit primeiro, tick depois.
- **Decisão: o backend `files` opera por worktree persistente em `.claude/worktrees/`.** Criada sob
  demanda na branch de specs e reutilizada, o que mantém o backend `files` sendo *arquivos* — o
  parser de seções e todo o código existente continuam valendo sem uma linha de tradução. Um
  lockfile serializa processos concorrentes. **`.claude/worktrees/` precisa estar ignorado**, e a
  CLI recusa criar a worktree se não estiver: uma worktree untracked quebraria o gate de árvore
  limpa de `/specs:execute` — o backend sabotaria a si mesmo.
- **Decidido (task 1.2): a branch de specs é configurável, com default `specs`.** A chave
  `specsBranch` em `.claude/quenching.json`; ausente, o backend `files` usa `specs`. Fixo seria mais
  barato, mas `specs` é um nome curto e plausível de já existir num repo alvo, e um backend que
  colide com uma branch alheia falha na primeira operação sem recurso. Namespaced (`quenching/specs`)
  evita a colisão e custa legibilidade a todo repo que não tinha o problema. Configurável paga o
  custo apenas onde ele existe. A confirmação prometida — o primeiro repo alvo real — segue de pé:
  se nenhum precisar do override, a chave é candidata a ser retirada.
- **Refinado (task 2.1): a interface de backend carrega o documento, não os verbos.** O `## Design`
  listava `list/status/show/section/task/discover/promote/validate` como a interface. Implementados
  como métodos por backend, cada implementação reparsearia as catorze seções, e "todos operam
  identicamente" seria provado só por teste — três parsers que podem divergir. A interface entregue
  são cinco primitivas sobre o documento canônico (`list_specs`, `read_spec`, `write_spec`,
  `create_spec`, `move_spec`); os oito verbos são código compartilhado sobre elas. A afirmação
  central passa a valer **por construção**. A serialização híbrida não é perdida: um backend externo
  serializa nativo como quiser desde que remonte o documento canônico na leitura — que é exatamente
  "a serialização híbrida vive dentro de cada implementação externa". A leitura granular também não:
  o custo que ela endereça é o **contexto** do agente, não I/O, então `show --section` devolve uma
  seção mesmo que o backend tenha buscado o documento inteiro.
## Alternatives Considered

- **Externo como projeção read-only:** rejeitada — o time quer read-write completo (gerir o spec
  pela ferramenta), não só espelho de leitura.
- **Só branch de specs dedicada, sem externo:** rejeitada — resolve a visibilidade mas adia a
  integração externa, que o time quer entregar junto.
- **Modelo nativo por backend (bifurcar a superfície por target):** rejeitada — bifurcaria
  `develop`/`execute`/`conclude` por backend; escolhido o modelo constante com serialização híbrida.

## Open Decisions

- **Como os sete records de frontmatter se serializam no GitHub** — labels (pesquisáveis, sem valor
  estruturado), campos no corpo da issue (estruturados, invisíveis na lista), ou mistos. **Decidido
  na** task 4.2, medindo o que a API de labels e sub-issues realmente oferece; o que for decidido
  vira uma linha em `## Design` antes da task ser ticada.
- **O nome da branch dedicada de specs** — fixo (`specs`), namespaced (`quenching/specs`) ou
  configurável. **Decidido na** task 1.2; a inclinação é configurável com default `specs`,
  confirmada quando o primeiro repo alvo real for configurado.
- **Se selecionar `azure-boards` emite um aviso de não-validado** — um aviso a cada operação é
  honesto mas vira ruído permanente; o silêncio faz o usuário descobrir sozinho. **Decidido na**
  task 6.3, quando o `github` estiver validado e o custo real da falta de prova for visível.

## Risks

- **Perder o acesso ao backend externo é perder o spec** — token revogado, repositório arquivado,
  migração de tenant. Com `files` o git era a cópia; externo, por decisão do `## Proposal`, não tem
  contraparte local. `ACCEPTED` — quem escolhe um backend externo já confia àquela ferramenta o
  código, as issues e o histórico. *Mitigação:* `specs.py export --spec <slug> | --all` despeja o
  markdown canônico em disco sob demanda; nada o lê de volta e nada o mantém sincronizado, então
  não é um segundo store.
- **`gh` / `az` viram requisito de runtime do backend externo** — `ACCEPTED`, consequência direta
  da decisão de transporte. *Mitigação:* recusa exit 2 nomeando o binário e o `auth login`
  correspondente, na primeira operação, nunca a meio de um build.
- **`azure-boards` entrega sem prova end-to-end** — `ACCEPTED`, não há ambiente Azure DevOps para
  exercitá-lo aqui. *Mitigação:* o selftest contra o backend fake prova o contrato de interface, e
  `## Open Decisions` carrega a decisão sobre avisar o usuário.
- **A worktree persistente suja a árvore e quebra o gate de `/specs:execute`** — uma falha
  silenciosa do backend contra si mesmo. *Mitigação:* a task 1.1 ignora o caminho **e** faz a CLI
  recusar criar a worktree se ele não estiver ignorado; `## Validation` exige
  `git status --porcelain` vazio.
- **Um refactor parcial deixa metade da superfície lendo arquivo e metade lendo a CLI** — o estado
  intermediário é pior que qualquer um dos dois. *Mitigação:* a seção 5 migra os nove bodies numa
  seção só, e `verification: per-section` verifica antes de sair dela.
- **A reescrita de cinco standards perde a razão original de cada regra** — três deles narram
  explicitamente decisões anteriores e por que foram tomadas. *Mitigação:* cada task de reescrita
  preserva a narrativa antiga como o que foi revertido, em vez de apagá-la.

## Handoff

- O `specs.py` é stdlib-only e sem dependências, e continua sendo: o transporte externo é
  `subprocess` sobre `gh`/`az`, nunca uma biblioteca HTTP.
- A ordem das seções é deliberada — o backend `github` prova a interface **antes** de os nove
  bodies serem reescritos. Se a interface se revelar errada na seção 4, a superfície ainda está
  intacta e o custo é uma seção.
- Cinco standards são reescritos, três deles narrando decisões anteriores. A reescrita preserva a
  narrativa antiga como "o que foi revertido"; `worktree-setup.md` §"Why a config file" já foi
  feito assim e é o exemplo a imitar.
- Nenhuma edição em `commands/**` é testável na sessão que a escreve — o registry é montado no
  início da sessão. A seção 5 termina com `doctor`, não com um teste funcional.

**Estado após 3.1 (seções 1 e 2 completas, verificadas):**

- **Config** — `.claude/quenching.json` no raiz do repo: `backend` (default `files`),
  `specsBranch` (default `specs`), `worktreeSetup`. Quatro findings de config no `doctor`. Este
  repo não tem o arquivo: roda todo nos defaults.
- **Interface** — `SpecBackend` expõe cinco primitivas sobre o documento canônico
  (`list_specs`/`read_spec`/`write_spec`/`create_spec`/`move_spec`). Os verbos da CLI são código
  compartilhado sobre elas; `resolve_one` e `derive_info` são puras e usadas por todos. Um backend
  que derivar qualquer coisa por conta própria está quebrado.
- **`open_backend(root)`** resolve o backend e **recusa exit 2** um declarado e não implementado —
  nunca cai para `files`.
- **`MemoryBackend`** é o outro lado da igualdade; `BACKEND_CASES` (8 casos) roda os dois no
  selftest e exige resultado idêntico fora de `path` e `text`. Ele guarda o filename porque a data
  vem do nome do arquivo, não do frontmatter.
- **`show`** entrega índice por default, `--section`/`--task` repetíveis, e o documento inteiro só
  com `--full`, que recusa combinar com seletor.
- **Worktree de specs** em `.claude/worktrees/<branch>`, criada sob demanda com `--orphan`,
  consumindo os guardas de 1.1. `resolve_files_root` responde sem git nos três casos que não podem
  virar worktree — o que preserva um `specs/` já populado como store pré-migração.

**Armadilhas conhecidas, registradas como discoveries:**

- `cmd_list` ainda lê `read_text(s["path"])` direto, contornando o backend. **Corrigir antes da
  4.1**, ou `list` quebra no `github`.
- O campo `root` do JSON emite o root declarado, não o resolvido — mente num repo migrado (seção 5).
- `doctor` lê o root direto e reportaria `sp-no-workspace` falsamente num repo migrado.
- Falta ao selftest a asserção genérica de que `parser.choices == DISPATCH`.
- `cmd_promote` ainda checa destino ocupado por `os.path.exists` sobre caminho derivado do root.
## Tasks

### 1. Configuração

- [x] 1.1 Ignorar `.claude/worktrees/` no `.gitignore` e fazer o `specs.py` recusar (exit 2) criar
      a worktree de specs se o caminho não estiver ignorado
      files: .gitignore, plugins/quenching/assets/bin/specs.py
      verify: git status --porcelain fica vazio após uma operação do backend files
      subject: plan/configurable-spec-backend: 1.1 ignora .claude/worktrees/ e recusa worktree nao ignorada
- [x] 1.2 Ler `.claude/quenching.json` no `specs.py` — a chave `backend`, o nome da branch de specs
      (per ## Open Decisions) e o `worktreeSetup` migrado de `specs/config.json`
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 assets/bin/specs.py selftest
      subject: plan/configurable-spec-backend: 1.2 le .claude/quenching.json — backend, specsBranch, worktreeSetup
- [x] 1.3 Reapontar os findings `sp-config-unparseable` e `sp-config-unknown-key` para o novo local
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 assets/bin/specs.py selftest
      subject: plan/configurable-spec-backend: 1.3 reaponta os findings de config para .claude/quenching.json
- [x] 1.4 Escrever docs/standards/workflows/plugin-configuration.md (authority: current once proved)
      verify: python3 assets/hooks/okf-validate.py docs
      subject: plan/configurable-spec-backend: 1.4 escreve o standard de configuracao do plugin
- [x] 1.5 Reescrever docs/standards/workflows/worktree-setup.md para o novo caminho da config,
      preservando a narrativa da decisão que ele reverte
      verify: python3 assets/hooks/okf-validate.py docs
      subject: plan/configurable-spec-backend: 1.5 reescreve worktree-setup.md para o novo caminho da config

### 2. Interface de backend

- [x] 2.1 Definir a interface de backend em specs.py — list/status/show/section/task/discover/
      promote/validate — com o backend `files` como implementação de referência
      files: plugins/quenching/assets/bin/specs.py
      subject: plan/configurable-spec-backend: 2.1 define a interface de backend com files como referencia
- [x] 2.2 Backend fake in-memory, exercitável sem rede e sem disco
      files: plugins/quenching/assets/bin/specs.py
      subject: plan/configurable-spec-backend: 2.2 backend fake in-memory sobre a derivacao compartilhada
- [x] 2.3 Rodar a lista canônica de casos do selftest contra `files` E contra o fake, exigindo
      resultado idêntico
      verify: python3 assets/bin/specs.py selftest
      subject: plan/configurable-spec-backend: 2.3 lista canonica de casos rodando contra files e contra o fake
- [x] 2.4 Leitura granular: `show --spec <slug> [--section <Heading> | --task <id>]`, com o
      documento inteiro apenas sob pedido explícito
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 assets/bin/specs.py selftest
      subject: plan/configurable-spec-backend: 2.4 leitura granular — show por secao e por task
- [x] 2.5 Escrever docs/standards/architecture/spec-backend.md (authority: current once proved)
      verify: python3 assets/hooks/okf-validate.py docs
      subject: plan/configurable-spec-backend: 2.5 escreve o standard da interface de backend

### 3. Backend files em branch dedicada

- [x] 3.1 Worktree persistente em `.claude/worktrees/` para a branch de specs, criada sob demanda e
      reutilizada; a branch de specs é criada vazia se não existir
      files: plugins/quenching/assets/bin/specs.py
      subject: plan/configurable-spec-backend: 3.1 worktree persistente para a branch de specs
- [x] 3.2 Lockfile serializando processos `specs.py` concorrentes sobre a worktree de specs
      files: plugins/quenching/assets/bin/specs.py
      subject: plan/configurable-spec-backend: 3.2 lockfile serializando escritores sobre a worktree de specs
- [x] 3.3 Exercitar o ciclo completo em workspace descartável: new → status/next/section/task →
      promote, com a árvore de trabalho permanecendo limpa
      verify: git status --porcelain vazio ao fim do ciclo
      subject: plan/configurable-spec-backend: 3.3 ciclo completo em workspace descartavel com arvore limpa

### 4. Backend github

- [ ] 4.1 Transporte via `gh api` em subprocess; binário ausente é recusa exit 2 nomeando
      `gh auth login`
      files: plugins/quenching/assets/bin/specs.py
- [ ] 4.2 Serialização híbrida — `## Tasks` vira sub-issues, as demais seções viram markdown no
      corpo; decidir e registrar per ## Open Decisions como os sete records se serializam
      files: plugins/quenching/assets/bin/specs.py
- [ ] 4.3 Anchor por sha: o commit acontece primeiro e a CLI grava o sha real na sub-issue; um tick
      que falha é reportado, nunca deixado implícito
      files: plugins/quenching/assets/bin/specs.py
- [ ] 4.4 Reescrever docs/standards/workflows/task-execution.md §One commit per task para o anchor
      por sha, preservando por que o subject foi escolhido antes
      verify: python3 assets/hooks/okf-validate.py docs
- [ ] 4.5 Reescrever docs/standards/workflows/plan-git-record.md §The task→commit link
      verify: python3 assets/hooks/okf-validate.py docs
- [ ] 4.6 E2E real neste repositório: criar spec de teste, escrever três seções, criar e ticar duas
      tasks, promover, remover a issue; os JSONs devem bater com os do backend `files`

### 5. Superfície

- [ ] 5.1 Migrar os nove bodies de `/specs:*` de Read-no-caminho para a leitura granular do
      `specs.py`
      files: plugins/quenching/commands/specs/align.md, plugins/quenching/commands/specs/conclude.md, plugins/quenching/commands/specs/continue.md, plugins/quenching/commands/specs/create.md, plugins/quenching/commands/specs/develop.md, plugins/quenching/commands/specs/execute.md, plugins/quenching/commands/specs/isolate.md, plugins/quenching/commands/specs/status.md, plugins/quenching/commands/specs/triage.md
- [ ] 5.2 Retirar de spec-driven.md a declaração "entirely native — no external CLI, no main spec
      store, no delta format", registrando o que a substitui
      files: plugins/quenching/assets/references/specs-develop/spec-driven.md
- [ ] 5.3 Atualizar specs-isolate/git.md e specs-create/specs-front.md para o novo caminho de config
      files: plugins/quenching/assets/references/specs-isolate/git.md, plugins/quenching/assets/references/specs-create/specs-front.md
- [ ] 5.4 Confirmar a superfície: doctor com 26 comandos e 0 findings, lint sem regressão
      verify: python3 assets/bin/skills.py --root . doctor --json

### 6. Backend azure-boards

- [ ] 6.1 Transporte via `az boards` em subprocess, com o mesmo contrato de recusa da task 4.1
      files: plugins/quenching/assets/bin/specs.py
- [ ] 6.2 Serialização híbrida para work items — tasks como itens filhos, seções como markdown
      files: plugins/quenching/assets/bin/specs.py
- [ ] 6.3 Decidir per ## Open Decisions se selecionar `azure-boards` emite aviso de não-validado

### 7. Export e fechamento

- [ ] 7.1 `specs.py export --spec <slug> | --all` — dump do markdown canônico, sem leitura de volta
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 assets/bin/specs.py selftest
- [ ] 7.2 Lockstep de versão: VERSION e as três ferramentas shipped concordam
      verify: cat VERSION && python3 assets/bin/specs.py --version
- [ ] 7.3 Atualizar plugins/quenching/README.md — os três backends, a config e o custo do binário
      files: plugins/quenching/README.md

## Discoveries

- cmd_promote ainda checa sp-dest-exists por os.path.exists sobre um caminho derivado do root — sem sentido num backend externo. A checagem de destino ocupado precisa virar pergunta ao backend na secao 4.
- cmd_list ainda le read_text(s['path']) direto, contornando backend.read_spec — o unico comando que sobrou assim. Funciona no backend files e quebra em qualquer externo; corrigir antes da task 4.1 exercitar list no github.
- O selftest so tem a asercao especifica sp-plans-subcommand-back; falta uma generica de que set(parser.choices) == set(DISPATCH). Um subcomando registrado em so uma das duas superficies passaria despercebido.
- Num repo migrado, o campo 'root' do JSON mente: todo comando emite o root declarado por find_specs_root, nao o resolvido pela worktree de specs. Sao ~12 call sites de emit e o valor pode ser consumido pelos bodies — pertence a secao 5.
- doctor le o root direto, sem open_backend (de proposito: diagnosticar nao pode criar worktree). Num repo migrado ele reporta sp-no-workspace falsamente. Precisa de um modo resolve-mas-nao-crie.
- Um workspace pre-migracao (specs/ na arvore de codigo) NAO e serializado: o lock guarda a worktree de specs, e nao ha onde por um lock que o git ignore na arvore de codigo. Medido: 6 escritores concorrentes dao 4-de-6 sem worktree e 6-de-6 com. Os 49 specs DESTE repo estao nesse estado ate serem migrados.
- migrate nao e classificado como escritor de proposito (reescreve o layout do workspace declarado, nunca a worktree), mas num repo ja migrado ele opera sobre um specs/ que nao existe mais — mesma familia do gap do doctor.
