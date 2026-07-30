---
slug: commit-on-worktree-specs
title: Commit work at the end of develop, create and execute when a spec is already isolated in a worktree
verification: per-section
priority: {level: 13, criticality: medium, complexity: 3, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# Commit work at the end of develop, create and execute when a spec is already isolated in a worktree

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

Este spec fecha uma lacuna de git em UM comando do front `specs/`: `/specs:develop` grava seções no
arquivo do spec e deixa a árvore suja, mesmo quando o spec já está isolado num branch ou worktree que
existe só para carregar esse trabalho.

`## Problem` mostra por que isso não é desleixo cosmético: o comando seguinte, `/specs:execute`, recusa
começar com a árvore suja, e o override que ele oferece dobra a edição do `develop` para dentro do
commit da primeira tarefa. `## Proposal` diz o que passa a ser verdade — um commit por edição
confirmada, e somente quando o spec já está isolado e o HEAD daqui aponta para esse isolamento.

`## Design` responde as três perguntas de mecânica: **quem** executa o commit (a ferramenta
`specs.py`, não o comando, e há três razões independentes para isso), **onde** fica a fronteira entre
"o arquivo do spec é o produto do trabalho" e "um commit precisa de um unit que alguém confirmou", e
**por que** a regra que `/specs:develop` já declara sobre git continua intacta em vez de precisar ser
revogada.

As duas seções que argumentam com o resto: `## Alternatives Considered` guarda as cinco formas
recusadas — inclusive a mais barata delas, que continua sendo a resposta certa para outra pergunta — e
`## Risks` guarda o caso em que um commit automático seria errado. Esse caso não é hipotético: ele
aconteceu nesta sessão, em 32 specs de uma vez, e é o que produziu a condição de gate.

O resto orienta a construção. `## Out of Scope` registra que `/specs:create` saiu por um motivo
mecânico e não por preferência, e que merge nunca entra. `## Impact` declara o único standard que este
spec escreve. `## Validation` diz com que comandos qualquer pessoa confirma que funcionou, e por que
um deles é deliberadamente omitido. `## Open Decisions` guarda quatro perguntas que ninguém precisa
responder para começar, cada uma com o que a decide. `## Tasks` é a lista na ordem em que as
dependências permitem: a ferramenta, depois os corpos, depois o standard que o trabalho prova.
## Problem

Quando um spec já tem trabalho isolado em seu próprio worktree, esperava-se que `/specs:develop`,
`/specs:create` e `/specs:execute` sempre terminassem a execução comitando esse trabalho. Lido
contra o código, o enunciado é verdadeiro em um terço e falso nos outros dois — e a lacuna real é
mais estreita, e mais grave, do que "não é garantido".

**O que já comita hoje:**

- `/specs:execute` comita uma vez por tarefa, com o código e o checkbox no MESMO commit —
  `assets/references/specs-execute/execution.md:145`
  (`git add {os arquivos da tarefa} {o arquivo do spec} && git commit -m "{subject}"`).
- `/specs:isolate` comita o arquivo do spec sozinho quando a isolação é tomada e o arquivo ainda não
  estava comitado — `commands/specs/isolate.md:140`.

**O que não comita:**

- `/specs:develop` não *pode* comitar: seu `allowed-tools` é
  `Read, Grep, Glob, Edit, Bash(python3:*), Bash(py:*), AskUserQuestion`
  (`commands/specs/develop.md:4`), e nenhum verbo git está ao seu alcance.
- `/specs:create` idem (`commands/specs/create.md:4`).
- `/specs:execute` deixa um resíduo: o passo 6 reescreve `## Handoff` DEPOIS do último commit
  (`commands/specs/execute.md:179-183`) e nada comita essa reescrita, embora
  `docs/standards/workflows/plan-git-record.md:171-173` já contrate exatamente um
  `plan/{slug}: record ...` para ela.

**Por que agora.** O custo não fica no `develop`; ele cai no comando seguinte. `/specs:execute`
recusa começar com `git status --porcelain` não vazio (`commands/specs/execute.md:61-64`,
`execution.md` §The precondition). Então a sequência ordinária create → isolate → develop → execute
bate na recusa **sempre**, e o override que `execute` oferece faz a edição de definição do `develop`
viajar dentro do commit da tarefa 1.1 — um commit cujo subject diz `plan/{slug}: 1.1 {título}`. Isso
falsifica a propriedade que `docs/standards/workflows/task-execution.md:121-130` e
`plan-git-record.md` vendem juntas: `git log` lido como a lista de tarefas do spec, e `git revert`
desfazendo exatamente uma tarefa.

## Proposal

- `/specs:develop` termina **cada edição confirmada de bank** com UM commit do arquivo do spec —
  quando, e somente quando, o work ref do spec está vivo e é o que o HEAD daqui aponta.
- A condição de gate é lida como **dado**, nunca adivinhada: os três campos
  `branch: {work, live, current}` que `specs.py` já calcula por spec (`assets/bin/specs.py:1921`)
  passam a ser legíveis também em `status --spec`, e `live` com `current` verdadeiros são a condição
  inteira.
- A condição fala de **isolação viva sob o HEAD atual**, não de worktree: um branch simples e um
  worktree produzem a mesma fricção e recebem o mesmo tratamento.
- O commit é mecânico e nunca fica ao alcance de um LLM: `specs.py` ganha o verbo que estagia
  SOMENTE o arquivo do spec, por pathspec, e comita com o subject que o comando lhe entrega.
- O `allowed-tools` de `/specs:develop` continua byte a byte o de hoje — `Bash(python3:*)` já cobre
  o verbo novo, e nenhum grant de git é concedido a um comando cujo trabalho são perguntas.
- `/specs:execute` passa a comitar a reescrita final de `## Handoff` sob o subject
  `plan/{slug}: record the handoff`, fechando o único resíduo que ele deixa hoje e cumprindo o que
  `plan-git-record.md` já contrata.
- **Nenhum prompt novo** aparece em `/specs:develop`. O commit é silencioso durante a passada e
  aparece uma vez no relatório final, com o subject que gravou.
- A sequência create → isolate → develop → execute deixa de bater na recusa de árvore limpa, e
  nenhum commit de tarefa carrega mais uma edição de definição que não é dele.

## Out of Scope

- **`/specs:create`.** O enunciado original o incluía, mas o gate não pode disparar lá: um spec
  acabado de nascer não tem `plan/{slug}` vivo, porque o slug não existia um instante antes. E o caso
  que sobraria já está resolvido — `/specs:isolate` comita o arquivo do spec sozinho na primeira vez
  que a isolação é tomada (`commands/specs/isolate.md:140`). Incluir `create` seria escrever um ramo
  morto.
- **Distinguir worktree de branch simples.** Exigiria `git worktree list`, isto é, um grant de git em
  `/specs:develop`, e não compra nada: a recusa de árvore limpa de `/specs:execute` e o commit mal
  rotulado da tarefa 1.1 acontecem igualmente nas duas formas.
- **Comitar quando o spec NÃO está isolado.** Deliberadamente recusado; `## Risks` guarda o caso real
  que decidiu isso.
- **Merge, review de branch e archive.** Continuam sendo `/specs:conclude`, com seus próprios gates.
  Este spec só comita, e comitar nunca implica integrar.
- **Os comandos de align.** Que `/docs:align`, `/specs:align` e `/skill:align` proponham worktree e
  mergem ao final é o spec irmão `align-in-worktree-then-merge`, e nada aqui decide por ele.
- **Regenerar `plans/index.md`.** O commit estagia somente o arquivo do spec. Uma passada de
  `develop` que muda o derived stage deixa a zona GENERATED desatualizada — o que já era verdade
  antes deste spec, porque `develop` nunca reindexou. `/specs:align` regenera a zona, e o spec irmão
  `decide-plans-index-need` pode remover o artefato inteiro.
- **O bump de versão do lockstep.** Tocar `assets/bin/specs.py` cria uma obrigação de release
  (`docs/standards/ci-cd/versioning-release.md`), e `/specs:conclude` a resolve no passo 5, no
  branch, antes do merge — nunca como tarefa, porque o que o release É só se sabe depois da última
  tarefa (`commands/specs/conclude.md:75-78`).

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/workflows/plan-git-record.md` — o commit do arquivo do spec como terceiro caso da
  regra "every record is written before the thing it describes": a condição de gate (`live` e
  `current`), o staging por pathspec, a gramática do subject `plan/{slug}: record ...` e a regra de que
  um commit recusado nunca reverte a escrita que ele descreveria

### Standards at `authority: background` this spec may resolve

- none — nenhum standard relevante está em `authority: background` hoje. Os cinco docs de
  `docs/standards/workflows/` são todos `current`, incluindo os três que este spec cita como
  vinculantes (`plan-git-record.md`, `task-execution.md`, `worktree-setup.md`).

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/specs.py` — o verbo de commit e os campos `live`/`current` em
  `status --spec`
- `plugins/quenching/commands/specs/develop.md` — o commit no passo 6 e a linha de relatório no passo
  8, sem tocar em `allowed-tools`
- `plugins/quenching/commands/specs/execute.md` — o commit da reescrita final de `## Handoff` no
  passo 6
- `plugins/quenching/assets/references/specs-isolate/git.md` — a gramática `plan/{slug}: record ...`
  passa a nomear seus dois novos usos, em §Commit messages

## Validation

Tudo abaixo roda a partir de `plugins/quenching/`, exceto onde o caminho diz o contrário.

**O lockstep primeiro** — `VERSION` e os três scripts publicados têm de concordar:

```bash
cat VERSION
python3 assets/bin/specs.py --version
python3 assets/bin/skills.py --version
python3 assets/hooks/okf-validate.py --version
```

**A superfície não muda** — nenhum comando novo, nenhum `allowed-tools` alargado:

```bash
python3 assets/bin/skills.py --root . doctor --json   # 26 commands, no findings
python3 assets/bin/skills.py --root . lint --json     # exit 0, e nenhum sk-unscoped-bash novo
python3 assets/bin/specs.py selftest                  # schema e template sem drift
```

**O verbo novo, em workspace descartável.** `specs.py` não tem fixture no repositório, e é assim que o
`CLAUDE.md` manda exercitá-lo:

```bash
python3 {caminho}/specs.py new probe-commit --title "Probe"
git checkout -b plan/probe-commit
printf 'x\n' | python3 {caminho}/specs.py section probe-commit Proposal --write
python3 {caminho}/specs.py commit --spec probe-commit \
        --subject "plan/probe-commit: record the shape bank"
git log -1 --format=%s      # tem de imprimir exatamente o subject passado
git status --porcelain       # tem de sair vazio
```

**As duas recusas são observadas, nunca presumidas:**

- HEAD em um ref que não é o work ref do spec → o verbo sai **2** e nada é comitado;
- um hook `pre-commit` que rejeita → o verbo sai **1**, relata o stderr do git verbatim, e a seção
  gravada permanece no disco. Nunca `--no-verify`.

**A falsificação antes da confiança**, per `docs/standards/workflows/task-execution.md`
§A `verify:` that cannot fail proves nothing when it passes (linha 47): cada asserção acima roda contra
a árvore **antes** da correção e tem de sair diferente de zero. Em particular o `git status --porcelain`
vazio — hoje ele imprime o arquivo do spec, e um check que passa nas duas árvores não prova nada.

**Invariantes que têm de continuar valendo:**

- `python3 assets/hooks/okf-validate.py assets/docs` → 0 error(s), 0 warning(s);
- o `allowed-tools` de `commands/specs/develop.md` byte a byte igual ao de hoje;
- nenhuma chamada `git add -A` em lugar nenhum do diff.

`./assets/bin/functional-checks.sh` **não** entra aqui. O `CLAUDE.md` do repositório é explícito: o
harness pertence ao front skill — `/skill:new` depois de mintar ou editar um comando — e não vai no
`## Validation` de um spec nem no `verify:` de uma tarefa, porque cada check é uma sessão de agente
faturada.

## Design

### O gate é um fato de dados, não um julgamento

A condição é `live` **e** `current`, e ela já existe. `specs.py next --front --json` devolve
`branch: {work, live, current}` para cada spec (`assets/bin/specs.py:1921`), derivado de duas
chamadas git para o front INTEIRO (`_git_refs`, `assets/bin/specs.py:1872-1881`) — nunca uma por
spec. E `_work_ref` (`assets/bin/specs.py:1884-1891`) já resolve o ref pelo record `branch:` quando
existe, caindo no default `plan/{slug}` quando não, porque um humano pode ter cortado o branch à mão.

Regra durável: **o ref é o sinal; o record nunca é.** É a mesma regra que
`assets/references/specs-isolate/git.md` §Recording the isolation declara, e este spec a consome em
vez de inventar uma segunda.

O que falta é apenas superfície: `status --spec` hoje devolve `records.branch` cru e nada sobre
liveness. Ele passa a devolver o mesmo objeto de três campos, reusando `_git_refs`. Duas chamadas git
por invocação, e `/specs:develop` já chama `status` no passo 2 — custo marginal zero.

### `specs.py` executa o commit; o comando decide e nomeia

Três formas foram pesadas, e a escolha tem três razões independentes:

1. **O `allowed-tools` de `/specs:develop` continua idêntico.** `Bash(python3:*)` já cobre o verbo
   novo. Conceder `Bash(git:*)` a um comando cuja doutrina é *"Never edit code"* também falsificaria
   a frase com que `commands/specs/execute.md:48-51` justifica seu próprio `Bash` irrestrito:
   *"Its siblings are scoped to `python3`/`py` because they only ever talk to `specs.py`."*
2. **A disciplina de staging fica em código, não em confiança.** `git add -A` é proibido
   (`commands/specs/isolate.md:191-192`, `assets/references/specs-isolate/git.md:314-319`), e a forma
   de garantir isso é o LLM nunca ter a chamada em mão.
3. **Há precedente.** `promote` já faz um `git mv` (`spec-driven.md` §The `specs.py` tool surface). O
   front não estreia aqui a ideia de a ferramenta tocar git.

O comando entrega o subject; a ferramenta nunca o inventa. É o que mantém
`assets/references/specs-isolate/git.md` como dono único da gramática de mensagens, com a ferramenta
apenas executando o que lhe passaram.

### O staging é por pathspec, nunca pelo índice

`git add {caminho} && git commit` comitaria também o que já estivesse estagiado no índice. Em um
worktree onde o humano tem trabalho paralelo meio-estagiado, isso rouba as mudanças dele para um
commit chamado `record`. A forma correta ignora o índice:

    git commit -- {o caminho do arquivo do spec}

Regra durável: **um commit de bookkeeping nomeia seus próprios caminhos e nunca herda o índice.**
Este é o risco cuja falha seria silenciosa, e por isso ele mora em código e não em prosa.

### `_git` engole falhas; este verbo não pode

`_git` (`assets/bin/specs.py:1859-1870`) devolve `""` para toda forma de falha — sem git no PATH,
fora de um repositório, exit diferente de zero — e a docstring diz por quê: para todo chamador
existente, ausência é *"este repo não tem fatos de git"*. Isso é certo para ranquear e errado para
comitar. O verbo novo precisa de caminho próprio, com os três exits que o front já usa em toda parte:
**0** comitado · **1** o git recusou, com o stderr verbatim · **2** a pré-condição não vale. Nunca
`--no-verify`, nunca `--no-gpg-sign` (`assets/references/specs-execute/execution.md:172`).

### Um commit por edição confirmada de bank

`questions.md` §Accumulate; apply in ONE edit per bank já faz de cada bank exatamente um diff que o
humano aprova uma vez. Esse é o *reviewable unit* que faltava: o mesmo OK que autoriza a escrita
autoriza o commit, e o limite do commit passa a seguir **o limite da confirmação** — do mesmo modo
que, em `/specs:execute`, ele segue o limite da tarefa. Uma passada que cruza dois banks produz dois
commits, e é correto que produza: os dois estados intermediários são reais, e `questions.md` diz
exatamente isso (*"The edit lands per bank, not per pass… and the stage between them is real"*).

Regra durável, e é a resposta ao "onde fica a fronteira": **o arquivo do spec é o work product, e o
que torna um commit legítimo é existir um unit que alguém confirmou.** Em `execute` esse unit é a
tarefa; em `develop` é a edição de bank. Onde não há confirmação nenhuma, não há commit — que é
exatamente por que `create` saiu do escopo e por que o gate existe.

### A regra que `/specs:develop` declara sobre git sobrevive intacta

O passo 8 diz: *"Isolation is forwarded, never offered… Never raise it unprompted; this command's job
is questions, and a prompt about git in the middle of one is friction for everyone"*
(`commands/specs/develop.md:152-155`).

O **objeto** da proibição é *levantar isolação*; a **razão declarada** é a fricção do prompt. Um
commit silencioso de uma edição que o humano já aprovou não levanta isolação e não pergunta nada — a
regra não precisa mudar, e ganha uma frase que diz o que ela nunca proibiu. Qualquer versão que
**pergunte** antes de comitar viola a regra, e é a própria regra que a recusa.

### A escrita precede o commit, e um commit recusado nunca a desfaz

Este é o único ponto em que a ordem importa, e o premortem foi quem o encontrou. As seções são
gravadas por `specs.py section --write` **antes** do commit, e nessa ordem um `pre-commit` que rejeita
deixa a árvore exatamente como uma passada de `develop` de hoje a deixaria: as respostas no disco, o
commit ausente, a recusa relatada.

A ordem inversa — comitar e depois gravar — é impossível aqui e é bom que seja: não há nada para
comitar antes de a seção existir. Então a regra não precisa ser escolhida, só declarada.

Regra durável: **um commit recusado nunca reverte a escrita que ele descreveria.** É a mesma forma da
regra que `/specs:execute` aplica ao contrário — lá o tick é desfeito quando o commit falha
(`assets/references/specs-execute/execution.md:156-157`), porque lá o tick *afirma* que o commit
existe. Uma seção escrita não afirma nada sobre git, então não há nada a desfazer. As duas regras
parecem opostas e são a mesma: **nenhum artefato deve sobreviver afirmando um commit que não
aconteceu.**
## Alternatives Considered

Cinco formas inteiras foram recusadas. As alternativas de dentro de uma decisão ficam em `## Design`.

| Forma | Custo | O que compra | Por que perdeu |
| --- | --- | --- | --- |
| **Não fazer nada** | zero | nenhuma mudança de superfície, nenhum grant novo, nenhum commit surpresa | o defeito é demonstrável e recorrente: a recusa de árvore limpa em toda sequência develop → execute, e a edição de definição rotulada como tarefa 1.1 |
| **Estreitar a pré-condição de `/specs:execute` para ignorar o arquivo do spec** | um comando, um parágrafo | remove o defeito demonstrável a ~20% da mudança, e `develop` continua sem git | conserta o sintoma no comando que não o causou, e deixa a edição de um bank sem registro nenhum na história quando a execução nunca chega — que é justamente a razão de ter tomado isolação |
| **Comitar sempre, sem gate** | um verbo, nenhuma leitura de estado | atende o enunciado original ao pé da letra | esta sessão rodou 32 passadas de `develop` em `main` sem isolação: teria produzido 32 commits que ninguém pediu, no branch base |
| **Delegar o commit a `/specs:isolate` via `Skill`** | `Skill` em `develop`, um modo novo em `isolate` | git fica no único comando que é dono das convenções de git | invocar um comando de 7 passos que termina em `AskUserQuestion` como primitiva de commit reintroduz o prompt que o passo 8 proíbe, e alarga o contrato de `isolate` para dentro do território do irmão `align-in-worktree-then-merge` |
| **Perguntar antes de comitar** | zero código | o humano decide caso a caso | é literalmente o que `commands/specs/develop.md:152-155` proíbe, e a razão declarada — fricção — se paga em cada passada, para servir uma minoria |

A segunda linha é a rival séria, e continua sendo a resposta certa para **outra** pergunta: se algum
dia `## Handoff` e o gate de árvore limpa forem revistos juntos, ela volta à mesa. O que a derrota
aqui não é o custo, e sim o escopo — ela cura a colisão entre dois comandos e não cura a ausência de
registro dentro de um.

A terceira linha merece ser lida ao contrário do que parece: o datapoint das 32 passadas não é um
argumento contra este spec, é a **evidência que produziu o gate**. Sem ele, a forma recusada seria a
forma escolhida.

## Open Decisions

- **O verbo aceita mais de um caminho, ou só o arquivo do spec?** Hoje só `develop` e `execute`
  precisam dele, e ambos precisam de um caminho. Um `create` futuro precisaria de dois (o arquivo do
  spec e `plans/index.md`). **Decidido por:** o resultado do spec irmão `decide-plans-index-need` — se
  o artefato sair, a pergunta desaparece com ele. Até lá, um caminho, e alargar depois é aditivo.
- **O mesmo gate deve alcançar `/specs:triage`?** `triage` escreve o record `priority` em VÁRIOS specs
  e também suja a árvore, então o argumento do `## Problem` se aplica em parte. **Decidido por:** se
  alguma passada de `triage` chega a rodar estando sobre o branch de um spec. Ela ranqueia o front
  inteiro, então normalmente não, e o gate `current` valeria para no máximo um dos specs que ela toca —
  o que produziria um commit parcial da passada, pior que nenhum. Fica fora até que essa passada
  exista de fato.
- **O relatório menciona o commit em uma linha, ou fica silencioso?** Recomendação registrada: uma
  linha, com o subject gravado. **Decidido por:** a mesma razão que faz `/specs:conclude` relatar o
  destino do worktree (`commands/specs/conclude.md:349-351`) — uma escrita não relatada é
  indistinguível de uma que nunca aconteceu. Fica aqui, e não em `## Design`, porque ninguém mediu
  ainda se a linha extra incomoda numa passada de três banks; a decisão é de ergonomia, não de
  correção.
- **O subject nomeia o bank?** `plan/{slug}: record the shape bank` é mais informativo que
  `plan/{slug}: record the spec`, e `git log` passaria a narrar a interrogação. **Decidido por:** se a
  gramática de `assets/references/specs-isolate/git.md` §Commit messages admite o qualificador sem
  virar um formato — ela hoje declara `plan/{slug}: record {what}`, e "the shape bank" é um `{what}`
  legítimo. A leitura é que sim, mas a palavra final é de quem é dono daquele arquivo.

## Risks

- **Um commit automático onde ninguém o queria.** Aconteceu de verdade: esta sessão rodou
  `/specs:develop` autonomamente sobre 32 specs em `main`, sem isolação, deixando 32 arquivos de spec
  modificados em uma única árvore de trabalho. Sem gate, seriam 32 commits no branch base que ninguém
  pediu. Mitigação: o gate `live` **e** `current` exclui exatamente esse caso — nenhuma das 32
  passadas tinha `plan/{slug}` vivo, e o HEAD era `main`. O datapoint é evidência **a favor** do gate,
  não contra o spec, e é a razão de ele existir em vez de um commit incondicional.
- **Um hook `pre-commit` do repositório alvo rejeita o commit no meio de uma passada.** Mitigação:
  exit 1 com o stderr do git verbatim; a seção já está gravada no disco, então nada do pensamento é
  perdido, e a passada **relata** a recusa em vez de escondê-la. Nunca `--no-verify`. A falha aqui
  seria ruidosa, que é a categoria aceitável.
- **O trabalho paralelo do humano é roubado para um commit de bookkeeping.** Um `git add` seguido de
  `git commit` levaria também o que já estivesse no índice. Mitigação: staging por pathspec
  (`## Design` §O staging é por pathspec), que ignora o índice por construção. Esta é a falha que
  seria **silenciosa**, e por isso a mitigação é código e não prosa.
- **Uma passada de três banks produz três commits de `record` e o `git log` do branch fica ruidoso.**
  ACCEPTED — é o mesmo trade que `/specs:execute` já faz com um commit por tarefa, e por baixo é a
  mesma regra: um commit por unit confirmado. Três commits legíveis são melhores que um blob cuja
  autoria de cada resposta ninguém recupera.
- **`plans/index.md` fica desatualizado depois de um commit que muda o derived stage.** ACCEPTED — já
  é verdade hoje, porque `develop` nunca reindexou; `/specs:align` regenera a zona. Alargar o staging
  para incluir o índice seria decidir pelo spec irmão `decide-plans-index-need`, que pode remover o
  artefato inteiro.
- **Sobreposição com `resolve-spec-from-worktree`.** Aquele spec decide COMO um spec é resolvido a
  partir do seu próprio worktree antes de cair no branch atual. Este consome a resolução que ele
  produzir e não a altera: aqui só entra a leitura de `live`/`current` **depois** de o spec já estar
  resolvido. Boundary mantido: se ele mudar a resolução, o gate deste spec continua valendo sem
  edição; se ele não for construído, o gate também vale. Nenhum dos dois assume o resultado do outro.
- **Sobreposição com `align-in-worktree-then-merge`.** Aquele leva worktree e merge aos comandos de
  align. Este toca apenas comandos `/specs:*` e apenas commit — **nunca merge**, que segue sendo a
  última ação de `/specs:conclude`. Se ambos forem construídos, o verbo de `specs.py` deste spec é
  reusável por aquele, e não o contrário; mas nada aqui presume que ele será.
- **Conflito de merge em `specs.py`.** Os specs irmãos `add-specs-py-record-writer`,
  `dedupe-specs-py-spec-reader` e `split-specs-py-backlog-renderer` reescrevem partes do mesmo
  arquivo. Mitigação: a mudança daqui é aditiva — um subparser e uma função novos — e a alteração em
  `status --spec` apenas inclui um objeto que `_candidate` já constrói. Nenhuma delas reescreve o
  parser que aqueles três disputam.
- **Sobreposição com `stop-develop-offering-follow-up-specs`.** Aquele também edita o passo 8 de
  `commands/specs/develop.md`. Boundary: este spec **adiciona** ao passo 8 uma linha sobre o commit e
  não toca no que aquele quer remover.
- **A frase que este spec adiciona ao passo 8 pode ser lida como permissão para perguntar sobre git.**
  Mitigação: a frase é escrita como um invariante negativo (*"comita sem perguntar; nunca ofereça"*),
  não como uma exceção à regra existente, e `## Alternatives Considered` guarda "perguntar antes de
  comitar" como forma explicitamente recusada.

## Tasks

### 1. O verbo em specs.py

- [ ] 1.1 Expor `branch: {work, live, current}` em `specs.py status --spec`, reusando `_git_refs` e `_work_ref`, sem uma chamada git por spec
      files: plugins/quenching/assets/bin/specs.py
      pattern: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py status --spec commit-on-worktree-specs --json | python3 -c "import json,sys; b=json.load(sys.stdin)['branch']; assert set(b)=={'work','live','current'}, b"
- [ ] 1.2 Adicionar `specs.py commit --spec {slug} --subject {linha}` — staging por pathspec do arquivo do spec, exit 2 quando o work ref não está vivo ou não é o HEAD daqui, exit 1 quando o git recusa (stderr verbatim), exit 0 comitado. Nunca `git add -A`, nunca `--no-verify`, nunca `--no-gpg-sign`
      files: plugins/quenching/assets/bin/specs.py
      verify: a sequência de ## Validation §O verbo novo em workspace descartável — `git log -1 --format=%s` igual ao subject passado e `git status --porcelain` vazio
- [ ] 1.3 Provar as duas recusas de 1.2 rodando cada asserção contra a árvore ANTES da correção e observando exit diferente de zero, per docs/standards/workflows/task-execution.md §A `verify:` that cannot fail
      verify: os dois runs vermelhos registrados no relatório da tarefa, um por recusa — um check que passa nas duas árvores é rejeitado

### 2. Os corpos dos comandos

- [ ] 2.1 Em commands/specs/develop.md passo 6, comitar a edição confirmada do bank quando `live` e `current`, com o subject `plan/{slug}: record the {nome} bank`, e no passo 8 relatá-lo em uma linha — escrito como invariante negativo ("comita sem perguntar; nunca ofereça"), sem alterar `allowed-tools`
      files: plugins/quenching/commands/specs/develop.md
      verify: grep -c 'Bash(python3' plugins/quenching/commands/specs/develop.md e a linha `allowed-tools:` idêntica à de HEAD~ (git diff da linha 4 vazio)
- [ ] 2.2 Em commands/specs/execute.md passo 6, comitar a reescrita final de `## Handoff` sob `plan/{slug}: record the handoff`, fechando o resíduo que docs/standards/workflows/plan-git-record.md já contrata
      files: plugins/quenching/commands/specs/execute.md
      pattern: plugins/quenching/commands/specs/execute.md
- [ ] 2.3 Em assets/references/specs-isolate/git.md §Commit messages, nomear os dois novos usos da gramática `plan/{slug}: record ...`
      files: plugins/quenching/assets/references/specs-isolate/git.md
- [ ] 2.4 Provar que a superfície não mudou
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json (26 commands, no findings) e lint --json com exit 0 e nenhum sk-unscoped-bash novo

### 3. O standard

- [ ] 3.1 Escrever em docs/standards/workflows/plan-git-record.md o commit do arquivo do spec como terceiro caso de "every record is written before the thing it describes" — a condição de gate, o staging por pathspec, a gramática do subject, e a regra de que um commit recusado nunca reverte a escrita (authority: current, provado por 1.2 e 2.1)
      files: docs/standards/workflows/plan-git-record.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs — 0 error(s), 0 warning(s)
- [ ] 3.2 Rodar o lockstep e o selftest ao fim da seção
      verify: cat plugins/quenching/VERSION mais os três `--version` concordando, e python3 plugins/quenching/assets/bin/specs.py selftest saindo 0
