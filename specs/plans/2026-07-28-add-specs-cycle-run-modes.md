---
slug: add-specs-cycle-run-modes
title: Add customizable run modes to the specs cycle commands
verification: per-section
priority: {level: 4, criticality: high, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# Add customizable run modes to the specs cycle commands

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

Este spec começou pedindo "run modes" customizáveis para `/specs:develop`, `/specs:execute` e
`/specs:conclude`. O `## Problem` guarda o pedido como ele foi feito; o `## Proposal` guarda o que
sobrou dele depois de confrontá-lo com o que o repositório já decidiu por escrito. Ler nessa ordem é o
caminho curto para entender por que os dois não são a mesma coisa.

A conclusão, em uma linha: dos três eixos pedidos, dois já têm mecanismo — o banco de perguntas que
`/specs:develop` deriva do estágio do spec, e a oferta de isolamento de `/specs:isolate` — e o terceiro
colide com o prompt cache da sessão. O que sobra é real e não é um flag: **uma declaração de gasto no
workspace**, no mesmo `specs/config.json` que já carrega `worktreeSetup`.

Por onde entrar. `## Alternatives Considered` tem o menu de modo escrito como seu melhor defensor o
escreveria, ao lado de não-fazer-nada e da menor coisa que funcionaria — é lá que a recusa é
argumentada, não afirmada. `## Design` decide como a declaração se comporta: onde mora, por que
`specs.py` lê e nunca executa, e o teste fechado que impede o arquivo de virar um sistema de
configuração. `## Out of Scope` é a parte que impede a ideia de voltar, cada eixo com o documento que o
recusa. `## Risks` guarda o único jeito silencioso disso dar errado — um gate estreito que passa verde.

A entrega é pequena e cabe em quatro grupos de task: uma chave em `specs.py`, quatro textos que a
descrevem, dois standards e uma prova. `## Validation` é toda determinística de propósito — um spec
sobre custo de check não abre a build gerando sessões de agente. E `## Open Decisions` é honesto sobre
o que não se decide daqui: se a chave vale a pena depende de uma medição que pertence a
`reduce-execute-conclude-cost`.

## Problem

`/specs:develop`, `/specs:execute` e `/specs:conclude` rodam cada um de uma única forma fixa, então
um humano que queira uma passada mais barata ou mais minuciosa não tem alavanca nenhuma além de
editar o corpo do comando. Deveria existir um run mode fácil de customizar, perguntado ao humano
quando o comando é invocado, cobrindo pelo menos três eixos:

- **Quantas perguntas chegam ao humano** — normal, só as críticas, ou totalmente autônomo.
- **Se a run se muda para um worktree.**
- **Nível de esforço** — normal, alto (uma rodada de crítica), muito alto (duas rodadas de
  crítica), e assim por diante.

## Proposal

O escopo passa a ser **uma declaração de gasto, morando no workspace**, mais o registro escrito de
que o menu de modos do `## Problem` não será construído. O `## Problem` fica como foi pedido; este é
o que sobrou dele depois de confrontá-lo com o que o repositório já decidiu.

Depois desta entrega:

- `specs/config.json` reconhece uma segunda chave, `gateCommand`, carregando o comando que o gate
  pré-merge de `/specs:conclude` (passo 6) executa quando a `## Validation` do spec não declara
  escopo próprio.
- `specs.py config --json` devolve `gateCommand` ao lado de `worktreeSetup`. Ausência continua
  valendo `null`, exit 0 e nenhuma saída que valha ler.
- Uma chave escrita errado continua caindo em `sp-config-unknown-key` (warn) e um JSON quebrado em
  `sp-config-unparseable` (warn) — nenhum finding novo é criado, e nenhum dos dois vira `error`.
- `/specs:conclude` lê a declaração em vez de escolher o escopo na hora, e **reporta o comando que
  rodou e de onde veio a declaração**: da `## Validation` do spec, do workspace, ou de nenhum dos
  dois.
- `/specs:status` mostra o que o workspace declara, sem escrever nada.
- O contrato do arquivo ganha dono próprio em `docs/standards/workflows/specs-config.md`, e
  `docs/standards/workflows/worktree-setup.md` continua dona do hook de worktree — consentimento,
  cwd, e o que acontece quando o setup falha.
- Está escrito, em `## Out of Scope` e no standard novo, por que volume de perguntas, forma de
  isolamento e nível de esforço não voltam como flag de invocação. Quem tiver a ideia de novo lê o
  motivo em vez de repropor.
- Nada passa a recusar. A declaração é lida como dado, na mesma postura de `skills.py budget`, que
  reporta e nunca bloqueia.

## Out of Scope

- **O menu de modo perguntado na invocação, nas três formas do `## Problem`.** É a coisa mais próxima
  de in-scope, e a que este spec recusa de propósito. Três motivos independentes, cada um já
  registrado no repositório: (1) `questions.md` abre dizendo que o
  `--mode critic|premortem|alternatives|interview` da v2 foi removido porque fazia o humano escolher a
  interrogação **antes de qualquer coisa ter lido o spec**, e `develop.md` §One loop, not a menu
  repete a decisão; (2) `docs/standards/architecture/read-only-views.md` (`authority: current`)
  estabelece que `allowed-tools` é concedido **por comando, não por invocação** — um modo que promete
  escrever menos é aplicado só pela prosa do corpo, enquanto a concessão que poderia impedir a escrita
  fica aberta a run inteira; (3) `capabilities.md` §The cache trap: model e effort fazem parte da
  chave do prompt cache da sessão, então um pin inline troca os dois e invalida o cache inteiro.
- **Um default declarado para a forma de isolamento.** `/specs:isolate` já oferece Worktree (padrão),
  Branch e In place, e o bloco de plano dessa oferta **é** o consentimento para o `worktreeSetup`
  declarado (`worktree-setup.md` §The consent is the isolation offer). Pré-responder a pergunta
  apagaria a única tela onde o comando do target pode ser julgado, e Worktree já lidera sem heurística
  nenhuma — um default declarado não compraria nada e custaria o consentimento.
- **Profundidade de interrogação em `/specs:develop`.** "Uma rodada de crítica" já é o banco
  adversarial, e "duas" é rodar o comando de novo: `questions.md` §Bank: adversarial diz que um spec
  que merece duas lentes recebe duas, escolhidas pelo estado dele. O que o eixo pedia contra isso é
  exatamente a exploração livre que a front abriu mão de ter (§A declared stop condition).
- **Pin de `model` ou `effort` em qualquer comando do ciclo.** Quais passos de `/specs:execute` e
  `/specs:conclude` sobrevivem num modelo mais fraco é a pergunta do spec
  `reduce-execute-conclude-cost`, decidida com evidência de transcript. Este spec não responde e não
  presume a resposta.
- **Uma task de bump de versão.** `versioning-release.md` §When the bump happens é explícita: as seis
  strings se movem uma vez, em `/specs:conclude` passo 5, e nunca como task.
- **Qualquer recusa nova.** A declaração é dado. Nenhum exit code muda, nenhum finding sobe de `warn`
  para `error`, e nada passa a bloquear um merge que não bloqueava antes.
- **Uma segunda chave, e um segundo consumidor, nesta entrega.** Ficam registrados em
  `## Open Decisions` com a evidência que decide cada um, em vez de entrarem sem medida.
- **Migrar `worktreeSetup` para outro arquivo ou renomear a chave.** O contrato ganha dono novo; a
  chave existente não se move, porque um target que já a declarou não pode ser quebrado por uma
  reorganização de documentação.
- **Corrigir o exemplo obsoleto de `docs/standards/automation/skills.md:45`.** Ele cita
  `/specs:refine --mode`, comando que não existe mais. É a edição vizinha mais tentadora e fica de
  fora: é um standard de outro assunto, com outro dono, e `/docs:add` é o caminho — encaminhado, não
  feito aqui.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/workflows/specs-config.md` — o contrato do arquivo `specs/config.json`: onde mora,
  o conjunto **fechado** de chaves, o que a ausência significa, quais findings existem, quem lê cada
  chave, e a regra de `## Design` D4 (uma chave declara gasto, nunca julgamento)
- `docs/standards/workflows/worktree-setup.md` — revisado: perde §One file, one key para o dono novo
  e continua dono do hook (consentimento pela oferta de isolamento, cwd dentro do worktree, setup
  que falha não desfaz o worktree)

### Standards at `authority: background` this spec may resolve

- none — nenhum standard `background` é provado nem promovido por esta entrega.
  `docs/standards/automation/context-budget.md` é `background` e é **citado** aqui, mas o que o
  graduaria é `skills.py budget` rodando em dois repos adotantes, coisa que este spec não faz.

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/specs.py` — `CONFIG_KEYS`, `load_config`, `cmd_config` e o trecho de
  config de `cmd_doctor` (`specs.py:952-986`, `specs.py:2834`, `specs.py:2877-2888`)
- `plugins/quenching/commands/specs/conclude.md` — o passo 6 lê a declaração, o passo 7 reporta a
  procedência
- `plugins/quenching/commands/specs/status.md` — mostra o que o workspace declara
- `plugins/quenching/assets/specs/QUENCHING.md` — a linha 432 descreve `specs.py config` como
  devolvendo o `specs/config.json` declarado
- `plugins/quenching/assets/references/specs-isolate/git.md` — a linha 118 fala do arquivo como
  fonte de uma chave
- `docs/knowledge/glossary.md` — a entrada **Worktree setup** descreve `specs/config.json` como
  carregando um comando; passa a valer para um conjunto de chaves. Roteado por `/docs:define`, nomeado
  pela task 3.3

## Validation

Tudo abaixo roda a partir da raiz do repositório, é determinístico e não gera sessão de agente
nenhuma — o que importa aqui, porque o assunto do spec é justamente custo de check.

**1. O lockstep e o selftest continuam de pé.**

```bash
cat plugins/quenching/VERSION
python3 plugins/quenching/assets/bin/specs.py --version      # bate com VERSION
python3 plugins/quenching/assets/bin/specs.py selftest       # exit 0
```

**2. A chave nova aparece, e a ausência continua custando zero.**

```bash
python3 plugins/quenching/assets/bin/specs.py config --json
```
Neste repositório, que não declara nada, tem que devolver exit 0 com `worktreeSetup: null` **e**
`gateCommand: null`, e a forma humana tem que imprimir as duas linhas com `(none declared)`.

**3. Um workspace de rascunho prova as três formas do valor.** Criar `specs/plans/` vazio mais um
`specs/config.json`, uma vez por caso, e conferir o que sai:

| `specs/config.json` | `config --json` | `doctor --json` |
| --- | --- | --- |
| `{"gateCommand": "./assets/bin/functional-checks.sh"}` | a string, exit 0 | sem finding de config |
| `{"gate_command": "x"}` | `gateCommand: null`, exit 0 | `sp-config-unknown-key` (**warn**), exit 1 |
| `{"gateCommand": ""}` | `gateCommand: null`, exit 0 | sem finding — string vazia é ausência |
| `{` | ambas `null`, exit 0 | `sp-config-unparseable` (**warn**), exit 1 |

Nenhuma linha dessa tabela pode virar `error`, e nenhum `--json` pode sair com traceback.

**4. A superfície de comandos continua conforme depois das edições de corpo.**

```bash
cd plugins/quenching
python3 assets/bin/skills.py --root . doctor --json    # 26 commands, nenhum finding
python3 assets/bin/skills.py --root . lint --json      # exit 0
python3 assets/bin/skills.py --root . budget --json    # o total não sobe
```
O baseline de hoje é `total: 12875` contra `ceiling: 12726`, ou seja o ratchet **já disparou** antes
desta entrega (`ok: false`, exit 1) — é condição pré-existente e não é desta entrega para consertar.
O que esta entrega tem que provar é que o número **não sobe**: nenhum comando novo é criado e nenhuma
`description` cresce para explicar a chave.

**5. O bundle aceita o standard novo.**

```bash
python3 plugins/quenching/assets/hooks/okf-validate.py docs
```
`0 error(s)`. O baseline de hoje é `0 error(s), 14 warning(s)`, todos `stale-doc` pré-existentes, e
`worktree-setup.md` **não** é um deles. A entrega não pode acrescentar `error` nenhum, e a revisão da
task 3.2 atualiza o `timestamp` daquele doc junto com o conteúdo, então ela também não pode criar um
`stale-doc` novo.

**6. O spec fecha as próprias contas.**

```bash
python3 plugins/quenching/assets/bin/specs.py validate --spec add-specs-cycle-run-modes --json
```
Sem `sp-impact-uncovered`: os dois caminhos declarados em `## Impact` são nomeados pelas tasks 3.1 e
3.2.

**Não faz parte deste conjunto:** `./assets/bin/functional-checks.sh`. Ele gera uma sessão de agente
por check, nenhum comando aqui muda o registro de comandos, e `surface-verification.md` já diz que
essa verificação pertence à front de skill — rodá-lo aqui seria o gasto que este spec existe para
tornar declarado.

## Design

As alternativas de **forma inteira** — incluindo o menu de modo que o `## Problem` pediu — estão em
`## Alternatives Considered`. Aqui ficam as decisões, cada uma com a alternativa pesada dentro dela.

### D1. A declaração mora no workspace, nunca na invocação

O que foi removido da v2 era um **seletor de interrogação perguntado ao humano antes de qualquer
coisa ter lido o spec**. `gateCommand` difere em três eixos, e essa diferença é o spec inteiro:

| | `--mode` da v2 | `gateCommand` |
| --- | --- | --- |
| quem declara | o humano, na invocação | o workspace, no disco |
| quando | a cada run, antes de ler o spec | uma vez, antes de qualquer run existir |
| o que seleciona | qual julgamento o comando aplica | quanto o comando gasta |

Um modo escolhe julgamento; uma declaração de gasto escolhe orçamento.
`docs/standards/architecture/read-only-views.md` recusa o primeiro porque a garantia ficaria na prosa
enquanto a concessão de ferramentas continua aberta a run inteira — e não diz nada contra o segundo,
porque um orçamento declarado não promete que nada será escrito.

### D2. Uma chave, carregando um comando, lido e nunca executado por `specs.py`

`gateCommand` é uma string com um comando de shell, rodado como escrito — exatamente a forma de
`worktreeSetup` (`specs.py:952-986`). `specs.py` lê o valor e **nunca** executa: o único caminho que
a ferramenta conhece é a raiz do workspace, e se o comando resolve só pode ser julgado por quem tem o
checkout na mão. Quem executa é `/specs:conclude` passo 6, no branch de trabalho, e reporta o exit
code.

A alternativa dentro desta decisão era um **número** — "no máximo N sessões de agente". Perdeu porque
nada no repositório conta sessões: o teto teria que ser contado por um modelo, e um teto que só um
modelo verifica é o problema da alternativa A com outra roupa. O comando **é** o teto, expresso na
única unidade que alguém pode conferir.

### D3. Ausência custa zero, e os dois findings que já existem são a guarda inteira

`load_config` devolve `null` para arquivo ausente, chave ausente, JSON quebrado e chave desconhecida,
e `cmd_doctor` transforma os dois últimos em `sp-config-unparseable` e `sp-config-unknown-key`, ambos
`warn` (`specs.py:2879` e `specs.py:2885`). Esse mecanismo já cobre o modo de falha real de uma chave
nova — `gate_command` escrito onde `gateCommand` era esperado, seguido de silêncio. **Nenhum finding
novo entra com esta entrega**, e nenhum dos dois sobe para `error`: um workspace com config malformada
continua sendo um workspace.

### D4. O teste fechado para qualquer chave futura: nomeia um gasto, nunca um julgamento

`worktree-setup.md` §Why a config file, in a front that had none diz que um arquivo declarativo
extensível ganha no momento em que existe um segundo parâmetro, e que até lá o schema é uma chave.
Este spec é esse momento — e o preço de abrir é declarar a regra que impede o arquivo de virar um
sistema de configuração:

> Uma chave de `specs/config.json` declara **quanto** um comando gasta ou **qual código do target**
> ele roda. Nunca declara qual julgamento ele aplica, quantas perguntas ele faz, ou o que ele tem
> permissão de escrever.

`worktreeSetup` passa (qual código do target). `gateCommand` passa (quanto gasta). Os três eixos do
`## Problem` falham todos os três.

### D5. O consumidor reporta o escopo e a procedência, e um escopo declarado é piso, não teto

`/specs:conclude` passo 6 já manda rodar "o escopo que o diff justifica" e já trata resultado
inconclusivo como não-verde. A mudança é que o escopo deixa de ser derivado e passa a ser lido — e o
relatório do passo 7 tem que dizer **de onde veio**: da `## Validation` do spec, do `gateCommand` do
workspace, ou de nenhum dos dois. Um gate que rodou menos do que o leitor imagina é o modo de falha
silencioso desta entrega (`## Risks`), e a procedência no relatório é a cura. O standard novo declara
a outra metade: um escopo declarado é piso, nunca teto — nada impede um humano de rodar mais.

### D6. Dois donos: o arquivo e o hook

`worktree-setup.md` diz hoje, com `authority: current`, que `worktreeSetup` é a **única** chave
reconhecida. Uma segunda chave torna essa frase falsa, então revisar aquele doc é **requisito da
entrega**, não arrumação. A divisão recomendada segue a regra de dono único que a front aplica em todo
lugar:

- `docs/standards/workflows/specs-config.md` (novo) — o contrato do **arquivo**: onde mora, o conjunto
  fechado de chaves, o que a ausência significa, quais findings existem, quem lê cada chave, e a regra
  de D4.
- `docs/standards/workflows/worktree-setup.md` (revisado) — continua dono do **hook**: consentimento
  pela oferta de isolamento, cwd dentro do worktree novo, setup que falha não desfaz o worktree. Perde
  só a seção §One file, one key e ganha uma linha citando o dono novo.

A alternativa — retitular `worktree-setup.md` para cobrir os dois — está em `## Open Decisions`: é um
rename com blast radius em três linhas `resource:` e no índice do layer, ou seja code-coupled, com
gate próprio.

### Contratos que este design não pode contrariar

- `docs/standards/architecture/read-only-views.md` — concessão de ferramentas é por comando; nenhum
  modo promete o que a concessão não impõe.
- `docs/standards/workflows/worktree-setup.md` — o consentimento é a oferta de isolamento; a ausência
  de declaração nunca é finding.
- `docs/standards/automation/context-budget.md` — o teto sem folga; nenhum comando novo é criado, e
  nenhuma descrição cresce para explicar um modo.
- `docs/standards/ci-cd/versioning-release.md` — o bump acontece no conclude, nunca como task.
- `docs/standards/quality/surface-verification.md` — inconclusivo não é passa; um harness que gera
  sessões de agente é cobrado por sessão.
- `CLAUDE.md`, as duas regras que precisam sobreviver a qualquer refactor: nada de `context: fork` nos
  comandos de sweep, e nada de `haiku` na classificação de `/docs:import-memory`.

## Alternatives Considered

Alternativas de **forma inteira**, cada uma escrita como seu melhor defensor a escreveria. As
alternativas de decisão isolada ficam em `## Design`.

| # | Alternativa | Custo | O que compra | Por que perdeu |
| --- | --- | --- | --- | --- |
| A | **Menu de modo na invocação**, como o `## Problem` pede | uma pergunta a mais em três comandos; texto de descrição contra um teto sem folga | controle explícito, por run, sem editar nada no disco | três decisões já registradas: `questions.md` (escolher a interrogação antes de ler o spec), `read-only-views.md` (concessão de ferramentas é por comando, não por invocação), `capabilities.md` §The cache trap (model/effort estão na chave do prompt cache) |
| B | **Registro por spec no frontmatter**, ao lado de `verification` | chave nova em `schema.json`, escrita pelo banco gate | a política viaja com o spec e sobrevive ao archive | custo de harness é propriedade do repositório, não de um spec; e `spec-driven.md` §Frontmatter admite só o que nenhuma derivação responde — o comando do gate é uma propriedade do repo, derivável dele |
| C | **Declaração no workspace** (escolhida) | uma chave em `specs/config.json`, dois consumidores, uma norma, o bookkeeping do lockstep | tira o julgamento de custo da prosa e põe no disco, lido por ferramenta | — |
| D | **Não fazer nada** | zero | zero | o escopo do gate pré-merge continua sendo derivado na hora, por um modelo, em cada run — e `conclude.md` passo 6 já chama a reação de rodar a suíte inteira de "the expensive way to learn nothing", ou seja o próprio comando já sabe que falta o parâmetro |
| E | **A menor coisa que funcionaria**: uma frase em `/specs:conclude` passo 6 mandando rodar o check mais barato do repo e dizer que escolheu | uma linha de corpo; zero mudança em `specs.py`, zero lockstep, zero norma | 80% do benefício por ~5% da mudança | a escolha continua sendo de um modelo, refeita a cada run — exatamente a forma "garantia na prosa" que `read-only-views.md` recusa. Perde por pouco, e é a alternativa a reabrir se C ficar caro |
| F | **Comprar emprestado o padrão read-if-present**: um doc em `docs/standards/` com o comando no frontmatter, como as convenções de git do target | zero formato novo | reusa um contrato que a front já aplica | perde pelo motivo que `worktree-setup.md` §Why a config file já registrou: obriga `specs.py` a parsear frontmatter markdown para achar um executável, e mistura a casa dos **contratos** com um ponteiro operacional |
| G | **Comandos irmãos por profundidade** (`develop-critic`, `develop-premortem`, …) | quatro descrições always-on para sempre | cada modo roteável por si | `context-budget.md` — o teto está sem folga por desenho; e `skills.md` §Single-axis classification diz que uma técnica é parâmetro de um verbo, nunca um eixo novo |

A tensão que este spec tem que declarar: `docs/standards/automation/skills.md:45` ainda cita
`/specs:refine --mode` como **a forma certa** de expressar quatro técnicas de um verbo. O argumento
citado ali é contra G, não a favor de A — e o comando que ele nomeia não existe mais desde o colapso.
O exemplo é obsoleto e a correção é de outro dono: `/docs:add` sobre `skills.md`, oferecido em
`## Open Decisions` e não feito aqui.

## Open Decisions

- **A chave se paga?** O gate pré-merge é o único lugar do ciclo onde uma declaração de gasto muda o
  que é efetivamente gasto — essa é a suposição que sustenta o spec inteiro. **Como se decide:** o
  spec irmão `reduce-execute-conclude-cost` vai medir onde o dinheiro de `/specs:execute` e
  `/specs:conclude` realmente vai, a partir de transcript. Se o gate pré-merge não for o maior item,
  a alternativa E de `## Alternatives Considered` (uma frase no corpo, zero código) passa a ser a
  entrega certa. Este spec não presume o resultado e não bloqueia esperando por ele.
- **Um segundo consumidor: `/specs:execute` também lê `gateCommand`?** O `verify:` de uma task pode
  ser tão caro quanto o gate. **Como se decide:** procurar, no arquivo, um spec concluído cujo
  `verify:` invocou um harness que gera sessões de agente. Se não existir nenhum, a chave fica com um
  consumidor só, e a extensão fica registrada aqui em vez de construída sem medida.
- **A casa do contrato: doc novo ou retítulo?** A recomendação é
  `docs/standards/workflows/specs-config.md` como dona do arquivo, com `worktree-setup.md` ficando
  dona do hook. **Como se decide:** depende do spec irmão `revise-standards-subject-folders`, que
  pode mexer nas pastas de assunto fixas — se `workflows/` mudar de forma, a decisão de nome muda com
  ela. Enquanto isso a alternativa é retitular `worktree-setup.md`, que é um rename com blast radius
  em três `resource:` e no índice, ou seja code-coupled e com gate próprio.
- **O exemplo obsoleto em `docs/standards/automation/skills.md:45`.** Ele cita
  `/specs:refine --mode`, um comando que não existe mais, como a forma certa de uma técnica ser
  parâmetro de um verbo. **Como se decide:** não aqui. É um `/docs:add` sobre `skills.md`, oferecido
  como encaminhamento e deliberadamente fora de `## Tasks`, porque corrigir um standard de outro
  assunto de dentro deste spec é exatamente o bulk-copy que a front recusa.

## Risks

- **Um gate declarado estreito passa verde e o merge leva uma regressão que a suíte larga teria
  pego.** É o modo de falha silencioso desta entrega, e o pior deles, porque o relatório diz "verde".
  *Mitigação:* `/specs:conclude` passo 7 passa a reportar **procedência** — se o escopo veio da
  `## Validation` do spec, do `gateCommand` do workspace, ou de nenhum dos dois — e o standard novo
  declara que um escopo declarado é **piso, nunca teto**: nada impede um humano de rodar mais.
  `surface-verification.md` já cobre a metade adjacente: inconclusivo não conta como passa.
- **Contradição direta com um standard `authority: current`.** `worktree-setup.md` §One file, one key
  diz que `worktreeSetup` é a **única** chave reconhecida. Uma segunda chave torna essa frase falsa
  no instante em que entra. *Mitigação:* a revisão desse doc não é arrumação, é requisito — task
  4.2, e o próprio doc já previu o momento ("An extensible declarative file wins the moment there is
  a second parameter").
- **`specs.py` é território disputado.** Quatro specs irmãos mexem no mesmo arquivo:
  `split-specs-py-backlog-renderer`, `dedupe-specs-py-spec-reader`, `add-specs-py-record-writer` e
  `name-the-scaffolded-stage`. *Mitigação:* a fronteira que este spec mantém é estreita e nomeada —
  só `CONFIG_KEYS`, `load_config`, `cmd_config` e o trecho de config de `cmd_doctor`
  (`specs.py:952-986` e `specs.py:2834`, `specs.py:2877-2888`). Nenhum dos quatro nomeia essa região;
  se algum passar por ela, quem mergear depois resolve o conflito, e este spec não presume o desenho
  de nenhum deles.
- **Sobreposição de assunto com `reduce-execute-conclude-cost`.** Os dois specs falam de custo do
  ciclo. *Fronteira mantida:* este spec entrega **a declaração** — onde o parâmetro mora, quem o lê,
  o que a ausência significa. Aquele spec decide **quais passos** de `/specs:execute` e
  `/specs:conclude` sobrevivem num modelo ou effort mais fraco, com evidência de transcript. Nenhum
  pin de `model`/`effort` entra por aqui, e nenhuma chave de config é presumida por lá.
- **Sobreposição de caminho com `revise-standards-subject-folders`.** Este spec declara escrever em
  `docs/standards/workflows/`, uma pasta que aquele spec pode reorganizar. *Fronteira mantida:* o
  caminho declarado em `## Impact` é o de hoje; se a pasta mudar antes do merge, o caminho segue a
  reorganização e o conteúdo do standard não muda.
- **O arquivo de config virar um sistema de configuração.** É o medo que `worktree-setup.md` §Why a
  config file registrou por escrito, e abrir a segunda chave é o momento em que ele fica real.
  *Mitigação:* o teste fechado de `## Design` D4 entra no standard novo — uma chave declara **gasto**
  ou **qual código do target rodar**, nunca qual julgamento o comando aplica.
- ACCEPTED — **custo permanente**: uma chave a mais num contrato lido por máquina, uma linha a mais no
  manual do operador (`assets/specs/QUENCHING.md:432`) e uma coisa a mais que `/specs:status`
  imprime. É aceitável porque a reversão é barata: tirar a chave de `CONFIG_KEYS` degrada um target
  que a declarou para `sp-config-unknown-key` (warn), o comportamento já projetado, e nunca para uma
  quebra.
- ACCEPTED — **o bookkeeping do lockstep**. Mexer em `specs.py` obriga as seis strings de versão a se
  moverem juntas. É aceitável porque `versioning-release.md` já põe esse movimento em
  `/specs:conclude` passo 5, fora de `## Tasks`, e nenhuma task aqui o duplica.

## Tasks

Serial de ponta a ponta, sem `[P]`: são quatro edições de texto de um arquivo cada e uma mudança de
ferramenta, então provar disjunção compraria segundos e custaria um marcador a manter. Cada texto de
checkbox cabe em uma linha, porque `specs.py next` entrega ao executor a primeira linha e só ela.

### 1. A declaração em specs.py

- [ ] 1.1 Adicionar `gateCommand` a `CONFIG_KEYS` e ao retorno de `load_config`, com a regra de valor de `worktreeSetup`
      files: plugins/quenching/assets/bin/specs.py
      pattern: plugins/quenching/assets/bin/specs.py (load_config, specs.py:952-986)
      verify: python3 plugins/quenching/assets/bin/specs.py config --json  (as duas chaves aparecem, ambas null neste repo, exit 0)
- [ ] 1.2 Estender a saída humana de `cmd_config` para imprimir as duas chaves, com `(none declared)` na ausente
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py config  (duas linhas, nenhuma chave omitida)
- [ ] 1.3 Provar num workspace de rascunho que `cmd_doctor` não precisa de finding novo, citando a saída das quatro linhas da tabela de ## Validation §3
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py --root /tmp/acrm-ws/specs doctor --json

### 2. Os consumidores

- [ ] 2.1 Fazer o passo 6 de `/specs:conclude` ler `gateCommand` quando a `## Validation` do spec não declara escopo, e o passo 7 reportar a procedência
      files: plugins/quenching/commands/specs/conclude.md
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json  (exit 0)
- [ ] 2.2 Fazer `/specs:status` mostrar o que o workspace declara, sem ganhar tool grant nenhum
      files: plugins/quenching/commands/specs/status.md
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json  (26 commands, sem findings)
- [ ] 2.3 Atualizar a linha de `specs.py config` no manual do operador para nomear o conjunto de chaves
      files: plugins/quenching/assets/specs/QUENCHING.md
- [ ] 2.4 Corrigir em `specs-isolate/git.md` a frase que trata o arquivo como fonte de uma chave só
      files: plugins/quenching/assets/references/specs-isolate/git.md

### 3. Os standards

- [ ] 3.1 Escrever docs/standards/workflows/specs-config.md com o contrato do arquivo, o conjunto fechado de chaves e a regra de ## Design D4
      files: docs/standards/workflows/specs-config.md, docs/standards/workflows/index.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs  (0 error(s))
- [ ] 3.2 Revisar docs/standards/workflows/worktree-setup.md: tirar §One file, one key, citar o dono novo, manter o hook, atualizar o timestamp
      files: docs/standards/workflows/worktree-setup.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs  (0 error(s), nenhum stale-doc novo)
- [ ] 3.3 Corrigir via `/docs:define` a entrada Worktree setup do glossário, que descreve o arquivo como carregando um comando
      files: docs/knowledge/glossary.md

### 4. A prova

- [ ] 4.1 Rodar o conjunto de `## Validation` inteiro e registrar a saída de cada comando, com o `budget` antes e depois
      verify: ver ## Validation
