---
slug: align-in-worktree-then-merge
title: Have the align commands propose a worktree and merge at the end, as specs already does
verification: per-section
priority: {level: 15, criticality: medium, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# Have the align commands propose a worktree and merge at the end, as specs already does

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

Os aligns são as varreduras do plugin: cada um força uma frente do repositório — `docs/`,
`specs/`, `.claude/` — para a mesma forma canônica, e `/align` conduz os três. Hoje todos escrevem
direto na árvore em que a sessão está e não commitam nada, então o resultado de uma varredura
autorizada é um diff sujo misturado a qualquer outra edição em curso. O `## Problem` conta isso do
ponto de vista de quem sente o incômodo.

Este spec dá aos aligns o formato que a frente de specs já tem, mas não por cópia. `## Design`
explica por que a leitura literal do título não funciona: a sonda precisa rodar antes de qualquer
árvore ser criada, três leituras que os aligns fazem não existem num checkout novo, o condutor não
pode dar uma árvore para cada front, e um merge automático daria a uma varredura autoridade que
nenhum gate de revisão sustenta. `## Proposal` lista o que fica verdadeiro depois.

`## Alternatives Considered` guarda as sete formas pesadas, e duas delas orientam o resto: "não
fazer nada" é a mais forte e é o motivo de `In place` liderar a oferta; "a menor coisa que
funcionaria" não foi recusada e sim absorvida como a primeira tarefa, porque é o aviso barato que
torna a recomendação honesta. `## Out of Scope` fecha os caminhos adjacentes que este spec
deliberadamente não abre — rodar o setup do repo alvo, drenar memória sob isolamento, dar merge a
`/specs:isolate`.

`## Risks` é o resultado do premortem: sete histórias de fracasso, cada uma com como seria
detectada, e a pior delas é a drenagem de memória falhando em silêncio — que é a razão de o desenho
**pular** aquele estágio em vez de consertar o caminho. `## Open Decisions` guarda o que
honestamente não está decidido, começando pela suposição que sustenta o spec inteiro e que ninguém
mediu: se as pessoas realmente rodam align com árvore suja.

`## Impact` declara o único documento de `docs/standards/` que este spec escreve e lista os seis
arquivos que ele altera — neste repo os corpos de comando são o código-fonte. `## Validation` diz
qual comando prova cada parte, inclusive o que o linter **não** pega, e nomeia a parte que nenhum
comando prova nesta sessão: o registro de comandos é montado no início da sessão, então mudança em
`commands/**` não é testável na sessão que a escreve, e isso fica como verificação manual declarada.

`## Tasks` está ordenado de propósito e a ordem carrega o argumento: o instrumento barato de medida
vem primeiro, o contrato compartilhado depois, os quatro corpos um a um, o standard, e a verificação
no fim. `## Handoff` carrega o que um executor não deriva — as duas regras deste repo que nenhum
refactor pode quebrar, e os três fatos que foram medidos em vez de supostos.
## Problem

Os aligns escrevem direto na árvore em que a sessão está. `/docs:align`,
`/specs:align`, `/skill:align` e o condutor `/align` podem tocar dezenas de
arquivos numa só varredura autorizada, e tudo isso cai no repositório principal
— sem branch, sem worktree, sem um ponto de integração no fim.

A frente de specs já resolveu isso: `/specs:isolate` tira o trabalho da árvore
principal e `/specs:conclude` faz o merge por último, de modo que uma única
integração carrega tudo o que a branch produziu. Os aligns não têm equivalente.

O ajuste pedido é dar aos aligns o mesmo formato: propor o uso de um worktree
antes de começar a escrever, e realizar o merge ao final da varredura.

## Proposal

Depois desta mudança:

- Os quatro aligns — `/docs:align`, `/specs:align`, `/skill:align` e o condutor `/align` —
  **oferecem isolamento** dentro da mesma tabela de plano em que já pedem UM OK. Escolher a
  forma é o próprio OK; não existe segundo prompt e não existe estado "este repo já está
  autorizado".
- A oferta só aparece quando a sonda achou trabalho. Um front conformante continua custando
  as duas ou três chamadas de sonda e para sem criar branch, worktree ou commit — a regra
  probe-before-inventory não é enfraquecida em nada.
- Aceito o worktree, a varredura escreve nele, o verificador do front roda nele, e o run
  fecha com UM commit por front na branch `align/{escopo}-{AAAA-MM-DD}`.
- O merge acontece e é a última ação do run, mas é **item de confirmação próprio**, sempre —
  inclusive sob autorização de ciclo. Ele entra na classe que `sweep-doctrine.md` §3 já
  chama de irreversível, ao lado do rename acoplado a código.
- Um run de `/align` cria **no máximo um** worktree, de propriedade do condutor. Os três
  front aligns herdam a árvore exatamente como já herdam o OK: um nível de aninhamento, e um
  align invocado como estágio nunca faz a oferta por conta própria.
- `In place` lidera a oferta e recusar é resposta completa: nenhuma branch, nenhum worktree,
  nenhum commit, nenhum registro.
- Nada registra o run. Nenhum record de frontmatter, nenhuma linha em `docs/`, nenhum
  `log.md`: o nome da branch e o `git log` são o registro.
- Três leituras que um worktree novo não consegue responder ficam declaradas e tratadas uma
  a uma, em vez de silenciosamente erradas: a pasta de memória do projeto, a varredura de
  blast radius sobre arquivos gitignored, e a instalação de ferramenta em `.claude/`.
- Os três aligns que hoje não declaram `AskUserQuestion` passam a declarar. Isso é o ganho
  colateral que vale citar: `sk-fork-gate` é um **error** do linter quando `context: fork`
  aparece ao lado de um grant `AskUserQuestion`, então a proibição que hoje é só prosa passa
  a ser mecânica nos quatro corpos, e não apenas em `/docs:align`.

## Out of Scope

- **Rodar o `worktreeSetup` do repo alvo.** `/specs:isolate` roda esse comando porque um
  `verify:` de tarefa precisa das dependências instaladas. Um align não precisa: os três
  verificadores (`okf-validate.py`, `specs.py`, `skills.py`) são Python stdlib e rodam num
  checkout recém-criado. Executar shell arbitrário do alvo para uma varredura que só reescreve
  markdown é escalada de privilégio sem contrapartida. Consequência boa: o contrato em
  `docs/standards/workflows/worktree-setup.md` §Who runs it, and where continua valendo
  literalmente — só `/specs:isolate` roda o hook, e este spec não precisa emendá-lo.
- **Um worktree por front dentro de `/align`.** É a pergunta que o desenho responde com "um
  só", e a alternativa está registrada em `## Alternatives Considered` com o motivo de ter
  perdido. Não é trabalho adiado; é caminho fechado.
- **Drenar a memória do projeto dentro de um worktree.** `/docs:import-memory` apaga cada
  memória depois de escrever o doc e verificar a conformidade. Sob isolamento o doc fica numa
  branch não integrada enquanto a memória já foi apagada: descartar a branch é perda de dado
  irreversível. O estágio é pulado com razão declarada e reportado com o comando que o fecha,
  que é o formato "report the cycle" que os aligns já usam.
- **Dar merge a `/specs:isolate`.** Continua fora, pelo motivo que `specs-isolate/git.md`
  §Merging is not here já dá: um merge invocável sozinho rodaria contra um spec que ninguém
  revisou. Este spec adiciona merge aos aligns, não ao isolate.
- **Ensinar os aligns a exigir árvore limpa.** Eles deliberadamente não exigem, e o worktree
  existe justamente para o caso de árvore suja. Transformar sujeira em recusa trocaria um
  incômodo por um bloqueio.
- **Um record tipo `branch: {base, work}` para o run de align.** O frontmatter registra
  julgamento humano sobre UM spec, e um align não tem spec nem arquivo onde gravar. Ver
  também a regra "no sweep records itself".
- **Os comandos por item.** `/docs:add`, `/docs:learn`, `/docs:define`, `/skill:new`,
  `/specs:create` não são varreduras: agem sobre um item que um humano acabou de enunciar, e
  quem está isolando é quem os invoca. Ficam intocados.
- **Instalar `docs/standards/git/**` num repo alvo.** Proibido pelo contrato read-if-present;
  a nomenclatura de branch deste desenho é *default* do plugin, e um alvo que já declarou as
  próprias convenções de git ganha delas.

## Impact

Escopo declarado para revisão humana. Este spec não toca código de aplicação — o repo não tem — e
não toca nenhum dos três scripts shipados, então o lockstep de versão não muda por conta dele.

### Standards this spec will write into docs/standards/

- `docs/standards/architecture/align-surface.md` — a regra arquitetural de isolamento do align: a
  oferta dentro do bloco de plano que já existe, uma árvore por run com aninhamento de um nível, os
  três carve-outs de leitura, o merge como item irreversível de confirmação própria, e a distinção
  explícita de que um commit numa branch `align/*` **não** é a varredura se registrando no sentido
  que a seção No sweep records itself proíbe.

Um documento só, e é o que já possui a regra arquitetural da superfície de align. Um segundo doc
sobre o mesmo assunto seria a segunda cópia que divergiria em silêncio.

### Standards em `authority: background` que este spec pode resolver

- none — `align-surface.md` já é `authority: current`, e nenhum outro standard deste repo tem
  regra de isolamento de align esperando prova.

### Código do produto que este spec espera tocar

Neste repo os corpos de comando **são** o código-fonte, então isto é a lista real de alteração:

- `plugins/quenching/assets/references/align/sweep-doctrine.md` — a seção nova de isolamento, lida
  como doutrina pelos quatro aligns;
- `plugins/quenching/assets/references/align/convergence.md` — uma frase em §Nesting: o worktree
  aninha um nível como a autorização, e um front align aninhado nunca faz a oferta;
- `plugins/quenching/commands/docs/align.md` — a linha de oferta no bloco de plano, os três
  carve-outs, o estágio de memória pulado sob isolamento, e a linha de invariante
  `context: fork` que hoje falta neste corpo e existe nos outros três;
- `plugins/quenching/commands/specs/align.md` — a oferta, os carve-outs, e os grants de git
  escopados;
- `plugins/quenching/commands/skill/align.md` — idem, mais a frase no corpo que declara por que
  `Bash(git -C:*)` é largo;
- `plugins/quenching/commands/align.md` — o condutor: cria no máximo uma árvore, passa adiante, e
  faz a confirmação de merge no fim.

Nada em `plugins/quenching/assets/bin/**` nem em `assets/hooks/**`: nenhum script muda, e é por
isso que o lockstep sai intacto. A obrigação de release que uma mudança de corpo cria é de
`/specs:conclude`, não deste spec.

## Validation

A política declarada no frontmatter é `per-section`, e ela não custa nada extra aqui: todo `verify:`
deste spec é uma chamada de Python sub-segundo ou um grep. Esta seção é o fallback para tarefa sem
`verify:` e o conjunto de invariantes que precisa continuar valendo no fim.

**A superfície de comandos continua conformante.** Rodado de `plugins/quenching/`:

```bash
python3 assets/bin/skills.py --root . doctor --json     # 26 commands, no findings
python3 assets/bin/skills.py --root . lint --json       # exit 0
```

`lint` em particular precisa sair **sem `sk-metadata-cap` novo** (nenhuma `description` muda) e
**sem `sk-unscoped-bash` novo** em `specs/align.md` e `skill/align.md`, cujos grants de git são
todos prefixados.

**Aviso honesto sobre o que o linter não pega.** `sk-unscoped-bash` dispara só para o token `Bash`
pelado (`assets/bin/skills.py:821`), então `Bash(git -C:*)` **não** é flagrado mecanicamente. A
justificativa em prosa no corpo é a única defesa desse grant, e é por isso que ela é obrigatória e
não opcional — ver o ACCEPTED correspondente em `## Risks`.

**A proibição de `context: fork` continua valendo, e passa a ser mecânica.** Dois greps mais uma
prova positiva:

```bash
! grep -rn 'context: fork' plugins/quenching/commands/docs/align.md \
    plugins/quenching/commands/specs/align.md \
    plugins/quenching/commands/skill/align.md plugins/quenching/commands/align.md
grep -c 'Never hand this command file .context: fork' plugins/quenching/commands/docs/align.md \
    plugins/quenching/commands/specs/align.md \
    plugins/quenching/commands/skill/align.md plugins/quenching/commands/align.md   # 1 em cada
grep -l 'AskUserQuestion' plugins/quenching/commands/*/align.md plugins/quenching/commands/align.md
```

A prova positiva de que o gate mecânico realmente fecha: copiar um dos quatro corpos para um
diretório temporário, acrescentar `context: fork` ao frontmatter da **cópia**, e rodar
`python3 assets/bin/skills.py lint {a cópia} --json` esperando exit 1 com `sk-fork-gate`. Nenhum
arquivo do repo é modificado, e o que se mede é a única coisa que importa: que a combinação
proibida agora é um error de linter nos quatro aligns, e não só em `/docs:align`.

**Os três selftests e o esqueleto shipado.** De `plugins/quenching/`:

```bash
python3 assets/bin/skills.py selftest
python3 assets/bin/specs.py selftest
python3 assets/hooks/okf-validate.py selftest
python3 assets/hooks/okf-validate.py assets/docs                        # 0 error(s), 0 warning(s)
python3 assets/hooks/okf-validate.py assets/specs/plans --listing-root   # 0 error(s), 0 warning(s)
```

**O lockstep de versão sai intacto.** Nenhum script muda, então `cat VERSION` e os três
`--version` continuam concordando **sem bump**. O bump que a mudança de corpo eventualmente exige é
obrigação de release e pertence a `/specs:conclude`, não a este spec.

**O bundle `docs/` deste repo não ganha finding novo.**

```bash
python3 plugins/quenching/assets/hooks/okf-validate.py docs
```

Este comando **já** reporta três `stale-doc` (WARN) antes de qualquer mudança deste spec, então o
critério é diferencial: nenhum finding **novo** atribuível a este spec. E há um finding que este
spec cria se a tarefa 4.1 for descuidada: `align-surface.md` tem `timestamp: 2026-07-29` e um
`resource:` que inclui os quatro corpos de align, logo editar os corpos sem atualizar o
`timestamp` do standard faz ele mesmo virar `stale-doc`. A tarefa 4.1 atualiza o `timestamp` junto
com o conteúdo, e este check é o que prova.

**O que este spec deliberadamente NÃO usa como validação.** `./assets/bin/functional-checks.sh`
fica fora, e não por esquecimento: por
[docs/standards/quality/surface-verification.md](/docs/standards/quality/surface-verification.md),
essa harness pertence à frente de skill, não entra em `## Validation` de spec nem em `verify:` de
tarefa, cada check é uma sessão de agente cobrada, e medido em todo o arquivo **todo run vermelho
que ela já produziu rastreou para defeito nela mesma, nenhum para regressão de superfície**. Se
alguém quiser medir roteamento falado dos aligns depois desta mudança, o comando é `/skill:eval`.

**O que nenhum comando prova nesta sessão.** Que os aligns realmente oferecem isolamento e que a
oferta aparece mid-flow só é observável numa sessão nova, porque o registro de comandos é montado no
início da sessão e nenhuma mudança em `commands/**` é testável na sessão que a escreve. Essa parte é
**verificação manual declarada**: rodar `/docs:align` num repo com árvore suja, numa sessão nova,
conferir que a linha de forma aparece dentro do bloco de plano e não num segundo prompt, e **dizer
no relatório que o check foi manual** — nunca pulá-lo em silêncio.

## Design

### O que os aligns fazem hoje — e por que isso reescreve a leitura do `## Problem`

O `## Problem` diz "sem branch, sem worktree, sem um ponto de integração no fim". Lido contra
o código, o ponto de integração existe e é o diff sujo: **nenhum align commita nada**. `/align`
não tem git algum em `allowed-tools` (`plugins/quenching/commands/align.md:4`), `/specs:align`
tem só `Bash(git mv:*)` (`plugins/quenching/commands/specs/align.md:4`), `/skill:align` tem só
`git grep` e `grep` (`plugins/quenching/commands/skill/align.md:4`). A varredura termina, o
humano lê `git diff` e commita.

Então o defeito real é mais estreito, e mais desagradável, do que "falta branch":

1. **Desfazer uma varredura ruim custa o trabalho alheio.** O desfazer é `git checkout -- .`,
   e ele leva embora também o que o humano tinha não commitado na árvore por outro motivo. Os
   aligns, ao contrário de `/specs:execute`, não exigem árvore limpa nem reclamam de uma suja.
2. **Não sobra artefato nomeado para revisar depois.** Quarenta arquivos tocados aparecem
   misturados a qualquer outra edição em curso, sem fronteira.
3. **A superfície é a maior do plugin.** Um OK autoriza três fronts e até 3 passes cruzados
   (`plugins/quenching/commands/align.md:85`), cada front align com cap interno 5.

O worktree resolve (1) e (2). O commit por front dá nome ao artefato de (2). (3) é projeto
declarado, não defeito, e nada aqui mexe nele.

### A sonda vem antes do worktree, sempre

`docs/standards/architecture/align-surface.md:43-58` chama probe-before-inventory de
load-bearing e não de otimização: um align caro em repo limpo é um align que ninguém roda
quando o repo cresce, que é exatamente quando a deriva acumula. Um worktree criado antes da
sonda cobraria criação de árvore no caso no-op, que é o caso comum.

Regra durável: **a sonda roda no checkout invocador; se ela para, nada foi criado.** A linha de
isolamento entra na tabela de plano que já existe (passo 3 de `/docs:align`, passo 5 de
`/specs:align`, passo 4 de `/skill:align`, passo 2 de `/align`), nunca antes dela.

```
sonda (checkout invocador)
  |
  +-- limpa ------------------> reporta e para        (nenhuma árvore criada)
  |
  +-- achou trabalho
        |
        inventário + blast radius (checkout invocador: precisa dos gitignored)
        |
        UMA tabela de plano ---- inclui a linha de forma: In place | Worktree
        |
        +-- In place ---------> escreve aqui, verifica aqui, para (como hoje)
        |
        +-- Worktree ---------> cria ../{repo}-align-{escopo}
                                 escreve lá, verifica lá, UM commit por front
                                 |
                                 merge: confirmação PRÓPRIA, sempre
                                   |
                                   +-- sim -> git -C {checkout da base} merge
                                   |            exit 0 -> worktree remove (sem --force)
                                   +-- não -> reporta branch, caminho e o comando exato
```

### Três leituras que um worktree novo não responde, e o que cada uma recebe

Um worktree carrega só o que o git rastreia. Isso quebra três coisas concretas, e cada uma
recebe uma regra explícita em vez de ficar silenciosamente errada:

1. **A pasta de memória do projeto.** `/docs:align` sonda `ls ~/.claude/projects/{cwd}/memory/`
   (`plugins/quenching/commands/docs/align.md:91`) — o caminho **deriva do cwd**. De dentro do
   worktree ele resolve para outro diretório de projeto, vazio, e o estágio conclui que não há
   memória. Resolver o caminho a partir do checkout invocador corrige a leitura, mas não o
   estágio: `/docs:import-memory` **apaga** cada memória depois de escrever o doc e verificar a
   conformidade, e um doc numa branch não integrada com a memória já apagada é perda de dado se
   a branch for descartada. Regra: **sob isolamento o estágio de memória não roda** — é pulado
   com razão declarada e reportado com `/docs:import-memory`.
2. **A varredura de blast radius.** `align/sweep-doctrine.md:107-108` exige
   `grep -rn --no-ignore` explicitamente "so gitignored surfaces are never skipped". Num
   worktree recém-criado não existe arquivo gitignored nenhum, então a varredura sub-reportaria
   sistematicamente e um rename acoplado a código passaria por interno. Regra: **as duas
   varreduras rodam no checkout invocador**; os hits são paths relativos ao repo e resolvem nas
   duas árvores, então a lista atravessa sem tradução.
3. **A instalação de ferramenta em `.claude/`.** `/docs:align` copia `okf-validate.py` e faz
   merge em `.claude/settings.json` (`plugins/quenching/commands/docs/align.md:196-218`),
   `/specs:align` instala `specs.py`, `/skill:align` instala `skills.py`. Um
   `settings.local.json` gitignored não existe no worktree, e um hook instalado numa branch não
   integrada não protege ninguém enquanto o merge não acontece. Regra: **instalação de
   ferramenta e merge de settings acontecem no checkout invocador**, nunca no worktree.

O desenho escreve em duas árvores, e isso é assumido em voz alta. O que impede a confusão é que
a divisão é por natureza do dado, não por conveniência: conteúdo rastreado do repo vai para o
worktree; estado fora-de-banda e ferramenta instalada ficam onde o humano está.

### Nomes, e o fato de que um align não tem slug

`specs-isolate/git.md:77-95` fixa `plan/{slug}` e um worktree em `../{repo}-{slug}`, ao lado do
repo e nunca dentro dele. O slug é único, então a branch é única. Um align não tem slug e
**recorre**: rodar duas vezes é normal. A data é o desempatador.

- branch: `align/{escopo}-{AAAA-MM-DD}`, com escopo em `docs`, `specs`, `skill`, `repo`
  (`repo` é o run de `/align`);
- worktree: `../{repo}-align-{escopo}`;
- colisão com uma branch já existente: sufixo numérico, nunca reuso e nunca `--force`.

O namespace `align/` ao lado de `plan/` mantém `git branch --list 'plan/*'` significando
exatamente o que significa hoje — trabalho de spec em voo — sem que uma varredura apareça
naquela lista e confunda `specs.py next --front`, que ranqueia justamente sobre `plan/{slug}`
estar vivo.

### Onde o run é registrado: em lugar nenhum

`docs/standards/architecture/align-surface.md:81-104` §No sweep records itself é categórico: a
conta que um sweep dá do próprio run vai no relatório, nunca no artefato que ele mantém. Logo:
sem record de frontmatter, sem entrada em índice, sem `log.md`. O nome da branch e o `git log`
são o registro, e um leitor que precise dele lê git.

Um record no estilo `branch: {base, work}` também não cabe por um segundo motivo: o frontmatter
de spec registra julgamento humano sobre UM spec, e um align não tem spec.

### O merge é a última ação e gate sozinho

`align/sweep-doctrine.md:78-98` já carve-out duas classes que a autorização de ciclo nunca
absorve: item acoplado a código, e ação irreversível. Um merge na base move uma ref que
descartar árvore de trabalho não desfaz — é exatamente a segunda classe. Então o merge:

- é **um item de confirmação próprio**, com o que ele vai fazer mostrado, mesmo quando o run
  veio de `/align` com OK dado no início;
- oferece as **mesmas quatro estratégias** que `specs-isolate/git.md:223-247` já documenta,
  default `merge-commit`, sem inventar uma quinta política;
- roda no checkout que já tem a base, localizado antes:
  `git -C {caminho} merge`. **Nunca `git checkout {base}`** — de dentro de um worktree isso
  falha com `fatal: '{base}' is already used by worktree at ...`, exit 128, ou seja, quebra
  precisamente na forma de isolamento recomendada;
- quando nenhum checkout tem a base, diz isso e para sem merge, em vez de fabricar um;
- depois de um merge com exit 0, remove o worktree pelo checkout da base e **nunca com
  `--force`** — `git worktree remove` já recusa árvore com arquivo modificado ou não
  rastreado, e a recusa é fato a reportar, não a atropelar.

Recusar o merge é resposta completa: o run reporta a branch, o caminho do worktree e o comando
exato de merge, e a árvore fica.

### O `cd` não é um fork, e o passo de escrita não vai para sub-agente

Esta é a restrição que o desenho não pode violar, e ela tem duas metades.

A primeira é a regra já escrita: `context: fork` é proibido nos aligns porque toda varredura
gate num plano mid-flow, e um run autorizado por ciclo ainda precisa fazer aparecer confirmação
acoplada a código no meio do fluxo — o que um contexto forkado não consegue apresentar. Um
worktree não muda nada disso: **entrar no worktree é mudar cwd, não mudar sessão.** A conversa é
a mesma, a tabela de plano é a mesma, a confirmação de merge aparece na mesma sessão.

A segunda metade é a tentação nova que este spec cria e precisa fechar: "manda o passo de
escrita para um sub-agente que trabalha no worktree". Isso é `context: fork` por outro nome —
o sub-agente não consegue apresentar a confirmação do rename acoplado a código nem a do merge.
Regra durável: **o passo de escrita de um align nunca é delegado.** O uso de sub-agente que os
aligns já têm continua sendo o único permitido, e ele é read-only por construção: bucketing
mecânico de uma lista de hits grande, e coletores de doutrina que reportam texto e nunca
veredito.

Há um ganho mecânico aqui que vale colher. `skills.py` emite `sk-fork-gate` como **error**
quando `context: fork` aparece ao lado de um grant `AskUserQuestion`
(`plugins/quenching/assets/bin/skills.py:851-857`), com a justificativa exata desta regra: um
contexto forkado não apresenta pergunta mid-flow, então um dos dois é mentira. Hoje só
`/docs:align` declara `AskUserQuestion`, então só ele está mecanicamente protegido. Implementar
a oferta de forma com `AskUserQuestion` nos quatro corpos converte a proibição de prosa em
proibição linteada nos quatro. Vale notar também que `/docs:align` é o único dos quatro cujo
bloco de invariantes **não** tem a linha `Never hand this command file context: fork` — os
outros três têm. Fechar essa lacuna é tarefa deste spec.

### O condutor cria no máximo um worktree, nunca um por front

Três árvores não convergem, e a razão está no próprio contrato do condutor. As arestas
cruzadas (`plugins/quenching/commands/align.md:60-68`) são: `/specs:align` conclui um spec e a
distilação vira trabalho de glossário no front `docs/`; `/skill:align` cria a regra e o registry
**dentro de `docs/`**, que o front `docs/` precisa então listar; o estágio harness de
`/docs:align` move um fato para `docs/` que um spec deveria citar. Cada front precisa **ver** a
escrita dos outros. Em worktrees separados, `/skill:align` escreveria
`docs/standards/automation/skills.md` numa árvore onde o scaffold de `docs/` feito pelo front 1
não existe, e o loop cruzado nunca alcançaria fixpoint. Somando: 3 fronts × até 3 passes
cruzados seriam até nove criações e nove merges por run, com conflitos entre as próprias
árvores.

Portanto o worktree **aninha exatamente como a autorização aninha**, um nível
(`align/convergence.md:76-79`): o align mais externo cria a árvore e a passa adiante; um front
align que recebe a declaração de autorização de ciclo sabe que está aninhado e **não faz a
oferta**. Isso é uma frase acrescentada à declaração que o condutor já emite, não um mecanismo
novo.

### O custo de permissão, declarado no corpo

`docs/standards/automation/skills.md:124-135` exige grant estreito e reporta `Bash` pelado como
`sk-unscoped-bash`, com uma exceção: um comando que roda o toolchain do repo alvo pode ter grant
largo **se o corpo disser isso e disser por quê**.

`Bash(git worktree:*)`, `Bash(git status:*)`, `Bash(git add:*)`, `Bash(git commit:*)` e
`Bash(git merge:*)` são prefixos honestos. O merge dentro do checkout da base é o caso que não
fecha: ele é `git -C {caminho} merge`, cujo prefixo é `git -C`, e `Bash(git -C:*)` libera
qualquer subcomando de git. Esse é o único grant largo do desenho, e ele segue o precedente que
`plugins/quenching/commands/specs/isolate.md:42-47` já usa — declarar no corpo por que o grant é
largo, com a fronteira sendo consentimento e não escopo. `/docs:align` já tem `Bash` sem escopo
e não muda.

## Alternatives Considered

| Forma | Custa | Compra | Fecha |
| --- | --- | --- | --- |
| **Oferta na tabela de plano, uma árvore por run, merge com gate próprio** *(escolhida)* | grants de git em três corpos, três carve-outs declarados, ~40 linhas de doutrina | isolamento opcional, artefato nomeado, integração no fim | a árvore por front |
| A menor coisa que funcionaria: só reportar a árvore suja | ~4 linhas por corpo | o aviso antes do estrago | o artefato nomeado |
| Paridade por cópia com `/specs:isolate` | igual à escolhida, mais merge automático | simetria de leitura entre as duas frentes | a revisão antes do merge |
| Emprestar: invocar `/specs:isolate` do align | ensinar um modo sem spec ao isolate | zero doutrina nova de isolamento | a fronteira per-item |
| Transformar o run de align num spec | um spec fabricado por run | reuso total de isolate e conclude | a fronteira anti-fabricação |
| Não fazer nada | zero | zero | nada |
| Commit-snapshot antes da varredura | um commit na base por run | reverter sem worktree | o histórico limpo do humano |
| Oferta só em `/align` | quase zero | o caso de maior blast radius | o caso de front único |

**A menor coisa que funcionaria: nenhum worktree, nenhum commit, nenhum merge — o bloco de plano
ganha uma linha dizendo que a árvore tem N arquivos não commitados e que desfazer a varredura com
`git checkout -- .` levaria esses arquivos também.** Quatro linhas por corpo, nenhum grant novo,
nenhuma doutrina nova, e fecha o perigo (1) do `## Design` — o desfazer destrutivo — informando em
vez de isolar. Não fecha o perigo (2), o artefato nomeado para revisar. **Não perdeu: foi
absorvida.** É a tarefa 1.1 e é o que um run `In place` recebe, porque é ela que torna a
recomendação da oferta honesta em vez de retórica. Também é o instrumento de medida da primeira
entrada de `## Open Decisions`.

**Paridade por cópia: cada align ganha a oferta no formato de `/specs:isolate`, com Worktree
liderando e merge automático no fim.** É a leitura literal do título deste spec, e perde por dois
motivos independentes. Primeiro, "cada align" implicaria árvore por front, e três árvores não
convergem: as arestas cruzadas exigem que cada front veja a escrita dos outros, e `/skill:align`
escreveria a regra e o registry num `docs/` que o front 1 nunca scaffoldou. Segundo, o merge
automático dá a uma varredura autoridade de merge sem nenhum gate de revisão — e é exatamente por
isso que `specs-isolate/git.md` §Merging is not here mantém merge fora de `/specs:isolate`: um
merge invocável sozinho rodaria contra trabalho que ninguém leu, e teria que duplicar cada recusa
que `/specs:conclude` já possui. O align não tem estágio de review nem de archive onde pendurar
esse gate, então o gate passa a ser o próprio item de confirmação.

**Emprestar em vez de construir: o align invoca `/specs:isolate` e não escreve isolamento nenhum.**
Seria o reuso ideal — a oferta, a nomenclatura, o custo do checkout fresco e a remoção do worktree
já estão escritos ali. Perde porque `/specs:isolate` é spec-scoped de ponta a ponta: o passo 1
seleciona um spec, o passo 6 estampa `branch: {base, work}` no arquivo do spec, e a própria oferta
mostra `plan/{slug}`. Sem spec não há o que selecionar nem onde estampar, então "emprestar" viraria
ensinar um modo sem spec a um comando cuja identidade é agir sobre UM spec — e
`align/convergence.md` §Per-item commands are stage tools, not stages é explícito que um comando
que age sobre um item enunciado por um humano nunca é estágio de varredura. O que **é** emprestado,
e sem custo, é a nomenclatura, a regra do `git -C`, as quatro estratégias e a remoção do worktree:
tudo citado de `specs-isolate/git.md`, nada reescrito.

**Transformar o run de align num spec: `/specs:create` um spec "align run" e reusar
`/specs:isolate` mais `/specs:conclude` sem escrever uma linha nova de isolamento.** Reuso máximo,
zero doutrina nova, e o `branch: {base, work}` já teria onde morar. Perde na mesma fronteira
anti-fabricação: criar um spec por varredura fabrica exatamente o que essa fronteira existe para
impedir. Também polui `plans/` com um spec por run de sweep, contamina
`specs.py next --front` (que ranqueia sobre `plan/{slug}` vivo), e deixa `/specs:conclude` com
archive e distilação que não têm o que fazer.

**Não fazer nada: o diff não commitado já é a superfície de revisão, e `git stash` já é o
isolamento do humano.** É a alternativa mais forte, e é o motivo de `In place` liderar a oferta em
vez de `Worktree`. Perde só no ponto onde ela realmente perde: o desfazer é `git checkout -- .`,
que leva embora o trabalho não commitado que o humano tinha na árvore por outro motivo — e os
aligns, ao contrário de `/specs:execute`, não exigem árvore limpa nem reclamam de uma suja.
Continua sendo a escolha correta para um repo com árvore limpa, e o desenho diz isso em voz alta.

**Commit-snapshot: antes de escrever, commitar a árvore como está na branch atual, para que a
varredura seja reversível com um `git revert`.** Mais barato que worktree, não precisa de segundo
checkout, e resolve o desfazer destrutivo. Perde porque commitar na base é precisamente o que o
`## Problem` quer evitar, e porque o commit seria do trabalho do humano, não da varredura — o
plugin assinaria uma mensagem sobre mudanças que não fez.

**Oferta só em `/align`, nunca num align de front único.** Quase de graça e cobre o caso de maior
raio. Perde por pouco, e por isso não está morta: continua registrada em `## Open Decisions` como a
pergunta que o primeiro uso em anger decide.
## Open Decisions

- **A suposição que sustenta o spec inteiro nunca foi medida: as pessoas rodam align com árvore
  suja?** Se um align é sempre rodado em árvore limpa — que é o que um operador disciplinado faz, e
  o que `/specs:execute` até exige — então o perigo do desfazer destrutivo nunca dispara, e todo
  este spec compra apenas "uma branch com nome". **Como se decide:** a tarefa 1.1 (a linha de
  árvore suja no bloco de plano) é o instrumento. Ela é barata, roda em todo align, e reporta um
  fato: quantos arquivos não commitados havia quando a varredura começou. Depois de alguns runs
  reais, ou o fato aparece e o resto do spec está justificado, ou não aparece e as tarefas do grupo
  3 devem ser reconsideradas antes de serem construídas.
- **A oferta deve existir num align de front único, ou só em `/align`?** `/align` é o caso de maior
  raio — três fronts, até 3 passes cruzados, um OK. Um `/skill:align` sozinho toca o `commands/**`
  de um repo e converge em 1–2 passes por natureza. Talvez a oferta só se pague no condutor.
  **Como se decide:** primeiro uso em anger num repo alvo com árvore suja, que é a mesma fórmula
  que `/specs:isolate` §Doctrine já usa para deixar aberta a oferta não solicitada em `create` e
  `develop`. Até lá o desenho oferece nos quatro, porque restringir depois é uma linha e ampliar
  depois é uma decisão.
- **Escrever em duas árvores no mesmo run confunde o relatório?** Os carve-outs 2 e 3 deixam
  varredura de referências e instalação de ferramenta no checkout invocador enquanto o conteúdo vai
  para o worktree. Isso está certo por natureza do dado, mas produz um relatório que fala de dois
  lugares. A alternativa é adiar a instalação de ferramenta para **depois** do merge, o que dá um
  relatório de um só lugar e um estado a mais para carregar. **Como se decide:** ler o primeiro
  relatório real de um run isolado de `/docs:align`, que é o align com mais escrita fora de `docs/`.
  Se ele não for legível numa leitura, adiar a instalação vence.
- **Qual estratégia de merge é o default certo para uma varredura?** O desenho reusa as quatro que
  `specs-isolate/git.md` já documenta com `merge-commit` como default, para não inventar uma quinta
  política. Mas um sweep não tem commits por tarefa cujo `subject:` precise resolver depois, que é
  o argumento que sustenta `merge-commit` na frente de specs — então `squash` pode ser o default
  honesto aqui. **Como se decide:** olhar o `git log` da base depois dos primeiros runs isolados; se
  os commits por front não são consultados por ninguém, o default muda para `squash`. A decisão não
  bloqueia nada: as quatro estratégias são oferecidas de qualquer forma.

## Risks

Sete histórias de fracasso, geradas do conteúdo deste spec e não de uma lista genérica. Cada uma
tem probabilidade, gravidade e — o que mais importa — **como seria detectada**, porque a falha que
ninguém percebe é pior que a barulhenta.

**Worktrees de align acumulam ao lado do repo.** Provável, gravidade baixa, hoje indetectável: o
humano recusa o merge, esquece, e seis diretórios `../{repo}-align-docs` sobram apontando para
branches já integradas ou abandonadas, nenhuma obviamente segura de apagar. Mitigação: a sonda
**reporta qualquer worktree `align/*` existente** — é um `git worktree list`, a mesma chamada que o
passo de isolamento já precisa fazer — e oferece integrar ou remover antes de criar outro. Custo
zero no caso limpo, porque no caso limpo a sonda para antes.

**O merge conflita com o trabalho do próprio humano.** Provável em varredura longa, gravidade
média, detecção alta: o git sai diferente de zero e diz o que colidiu. Mitigação: reportar a saída
do git **literalmente**, nunca resolver conflito automaticamente, e deixar a branch e o worktree de
pé. Um sweep que resolve conflito é um sweep escrevendo prosa autoral, que é o que a fronteira
anti-fabricação proíbe em toda parte.

**A drenagem de memória não faz nada, em silêncio.** Média, gravidade **alta**, detecção nenhuma —
é a pior linha desta tabela. Se alguém "simplificar" o carve-out 1 para "resolver o caminho a
partir do checkout invocador", o estágio roda, encontra memória, escreve o doc na branch, **apaga a
memória**, e a branch é descartada. Mitigação: o desenho escolhe **pular** o estágio sob
isolamento, não corrigir o caminho. Um skip com razão declarada é barulhento; um caminho corrigido
é silenciosamente frágil, e a diferença entre os dois é a diferença entre um relatório honesto e
perda de dado.

**A varredura de blast radius sub-reporta.** Média, gravidade alta, detecção nenhuma: rodada de
dentro do worktree, `grep -rn --no-ignore` não acha nada gitignored porque nada gitignored existe
ali, e um rename acoplado a código passa por interno e pega o OK do lote — furando exatamente a
exceção que `sweep-doctrine.md` §3 nunca deixa a autorização absorver. Mitigação: carve-out 2
(as duas varreduras no checkout invocador) mais uma invariante explícita em cada corpo.

**Alguém acrescenta `context: fork` a um align "para isolar o run no worktree".** Improvável,
gravidade **catastrófica**: todo gate desaparece, inclusive a confirmação de rename acoplado a
código e a de merge. Detecção parcial hoje — `sk-fork-gate` é error só quando o corpo declara
`AskUserQuestion`, o que só `/docs:align` faz. Mitigação: declarar `AskUserQuestion` nos quatro
corpos, o que torna a proibição linteada nos quatro, mais o grep de `## Validation` como cinto.

**O hook fica instalado numa branch e ninguém está protegido.** Média, gravidade média, detecção
razoável: `skills.py drift` reporta `sk-tool-unwired` ou `sk-tool-absent` na próxima rodada.
Mitigação: carve-out 3 — instalação de ferramenta e merge de `.claude/settings.json` acontecem no
checkout invocador, nunca no worktree.

**`In place` vira o caminho de sempre e o worktree nunca é usado.** ACCEPTED — as ~40 linhas de
doutrina e os grants de git teriam sido pagos por um caminho que ninguém escolhe. É risco aceito
porque a sequência de tarefas o testa antes de pagar o resto: a linha de árvore suja é a primeira
tarefa e é o instrumento de medida. Ver a primeira entrada de `## Open Decisions`.

Dois riscos que não vêm de história de fracasso, e são aceitos com o motivo dito:

**ACCEPTED — o grant `Bash(git -C:*)` é largo.** `docs/standards/automation/skills.md`
§`allowed-tools` is always scoped exige o conjunto mais estreito, e este não é estreito: ele
libera qualquer subcomando de git precedido de `-C`. Aceito porque a alternativa é pior: sem `-C`,
o merge no checkout da base exigiria `git checkout {base}`, que **falha** de dentro de um worktree
(exit 128) — ou seja, quebra precisamente na forma de isolamento recomendada. O que a exceção
documentada do standard cobra em troca é uma frase no corpo dizendo que o grant é largo e por quê,
e o precedente já existe em `/specs:isolate`.

**ACCEPTED — a linha de invariante `context: fork` faltando em `/docs:align` é reparo adjacente.**
Um revisor pode chamar de escopo esticado: os outros três aligns têm a linha, `/docs:align` não, e
isso não é o assunto deste spec. Aceito porque é uma linha, no mesmo conjunto de arquivos, e
fechando exatamente a lacuna da qual o risco catastrófico acima depende.

**Sobreposição com specs irmãos em desenvolvimento paralelo, e a fronteira que este spec mantém.**
Dois outros specs mexem em worktree e isolamento ao mesmo tempo que este, e nenhum dos três pode
supor o resultado do outro:

- `commit-on-worktree-specs` — commitar ao fim de `develop`, `create` e `execute` quando o spec já
  está isolado num worktree. Fronteira: aquele spec decide o comportamento de commit dos comandos
  `/specs:*` dentro de um worktree `plan/{slug}`; **este** spec só decide o de um align dentro de um
  worktree `align/{escopo}-{data}`, e não acrescenta commit a nenhum comando `/specs:*`. Se os dois
  landarem, a gramática de subject de `specs-isolate/git.md` §Commit messages é o ponto onde eles
  precisam concordar, e este spec a segue sem alterá-la.
- `resolve-spec-from-worktree` — resolver um spec pelo próprio worktree antes de cair no branch
  atual. Fronteira: este spec **não** cria worktree que contenha spec algum e usa namespace de
  branch separado (`align/` e não `plan/`) exatamente para que uma resolução worktree-aware nunca
  confunda uma varredura com um spec em voo, e para que `git branch --list 'plan/*'` continue
  significando o que significa hoje para `specs.py next --front`.

Nenhuma das duas fronteiras é resolvida aqui, e nenhum dos dois arquivos é tocado por este spec.

**Risco de leitura errada, com mitigação escrita:** alguém vai ler "no sweep records itself" e
concluir que um align commitando viola a regra. Não viola — a regra proíbe a varredura acrescentar
entrada **dentro do artefato que ela mantém**, e a própria frase final da regra manda o leitor que
precisa da conta ler o git. Mitigação: escrever essa distinção no standard, o que é parte do que
`## Impact` declara.

## Tasks

Ordenadas por dependência. Nenhuma tarefa carrega `[P]`, **de propósito**: os conjuntos de `files:`
do grupo 3 são provavelmente disjuntos, mas quatro corpos precisam terminar dizendo a mesma coisa, e
quatro autores paralelos não convergem em prosa. Serial é o default e aqui ele é escolhido.

### 1. O instrumento barato primeiro

- [ ] 1.1 Acrescentar ao bloco de plano dos quatro aligns uma linha que informa quantos arquivos não
      commitados a árvore tem e que desfazer a varredura com `git checkout -- .` levaria esses
      arquivos também — a menor coisa que funcionaria, absorvida como tarefa e como instrumento de
      medida da primeira entrada de `## Open Decisions`
      files: plugins/quenching/commands/align.md, plugins/quenching/commands/docs/align.md, plugins/quenching/commands/specs/align.md, plugins/quenching/commands/skill/align.md
      verify: grep -c 'git checkout -- .' plugins/quenching/commands/align.md plugins/quenching/commands/docs/align.md plugins/quenching/commands/specs/align.md plugins/quenching/commands/skill/align.md

### 2. O contrato compartilhado

- [ ] 2.1 Escrever a seção de isolamento em `sweep-doctrine.md`, depois de §1 Probe before the
      inventory: a oferta dentro do bloco de plano que já existe, a nomenclatura
      `align/{escopo}-{data}` e `../{repo}-align-{escopo}`, os três carve-outs como tabela, o commit
      por front, e o merge como item de confirmação própria. **Teto de 35 linhas**: se não couber,
      ela vira arquivo separado citado só do passo de plano, para não cobrar tokens no caminho no-op
      que a regra da sonda existe para manter barato
      files: plugins/quenching/assets/references/align/sweep-doctrine.md
      pattern: plugins/quenching/assets/references/align/sweep-doctrine.md
      verify: awk '/^## /{s=0} /^## .*[Ii]solation/{s=1;n=0} s{n++} END{print n; exit !(n>0 && n<=35)}' plugins/quenching/assets/references/align/sweep-doctrine.md
- [ ] 2.2 Acrescentar a `convergence.md` §Nesting a frase de que o worktree aninha um nível
      exatamente como a autorização aninha, e que um front align que recebe a declaração de
      autorização de ciclo **não** faz a oferta de isolamento
      files: plugins/quenching/assets/references/align/convergence.md
      verify: grep -n 'worktree' plugins/quenching/assets/references/align/convergence.md

### 3. Os quatro corpos, um a um

- [ ] 3.1 `/docs:align`: linha de forma no plano do passo 3, os três carve-outs (memória resolvida
      no checkout invocador **e** estágio pulado sob isolamento com razão declarada; blast radius no
      checkout invocador; instalação de hook e merge de `settings.json` no checkout invocador),
      `AskUserQuestion` já está declarado, e a linha de invariante `context: fork` que falta neste
      corpo e existe nos outros três
      files: plugins/quenching/commands/docs/align.md
      verify: python3 plugins/quenching/assets/bin/skills.py lint plugins/quenching/commands/docs/align.md --json
- [ ] 3.2 `/specs:align`: a oferta no plano do passo 5, os carve-outs que se aplicam (blast radius e
      instalação de `specs.py` no checkout invocador), e os grants escopados
      `Bash(git worktree:*)`, `Bash(git status:*)`, `Bash(git add:*)`, `Bash(git commit:*)`,
      `Bash(git merge:*)`, `Bash(git -C:*)` mais `AskUserQuestion`
      files: plugins/quenching/commands/specs/align.md
      verify: python3 plugins/quenching/assets/bin/skills.py lint plugins/quenching/commands/specs/align.md --json
- [ ] 3.3 `/skill:align`: a oferta no plano do passo 4, os carve-outs, os mesmos grants, e a frase
      no corpo que declara por que `Bash(git -C:*)` é largo — o merge roda no checkout que já tem a
      base e `git checkout {base}` falha de dentro de um worktree
      files: plugins/quenching/commands/skill/align.md
      verify: python3 plugins/quenching/assets/bin/skills.py lint plugins/quenching/commands/skill/align.md --json
- [ ] 3.4 `/align` como condutor: cria **no máximo uma** árvore, para o run inteiro, escopo `repo`;
      passa a declaração adiante junto com a de autorização; nenhum front align aninhado oferece; e
      a confirmação de merge é a última ação, item próprio mesmo sob o OK dado no início
      files: plugins/quenching/commands/align.md
      verify: python3 plugins/quenching/assets/bin/skills.py lint plugins/quenching/commands/align.md --json

### 4. O standard declarado

- [ ] 4.1 Escrever a regra de isolamento em `docs/standards/architecture/align-surface.md`
      (`authority: current`, porque os corpos do grupo 3 a provaram), incluindo a distinção de que um
      commit numa branch `align/*` não é a varredura se registrando no sentido que §No sweep records
      itself proíbe — e **atualizar o `timestamp` do doc**, senão ele mesmo vira `stale-doc` por ter
      os quatro corpos no próprio `resource:`
      files: docs/standards/architecture/align-surface.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs

### 5. Verificação

- [ ] 5.1 Rodar a lista de `## Validation` inteira — `doctor`, `lint`, os três selftests, os dois
      checks de esqueleto, os quatro `--version` contra `VERSION`, e o bundle `docs/` conferido em
      diferencial contra os três `stale-doc` pré-existentes
      verify: cd plugins/quenching && python3 assets/bin/skills.py --root . doctor --json && python3 assets/bin/skills.py --root . lint --json && python3 assets/bin/skills.py selftest && python3 assets/bin/specs.py selftest && python3 assets/hooks/okf-validate.py selftest
- [ ] 5.2 Provar que o gate mecânico fecha: copiar um dos quatro corpos para um diretório
      temporário, acrescentar `context: fork` ao frontmatter da cópia, lintar a cópia e esperar exit
      1 com `sk-fork-gate`. Nenhum arquivo do repo é modificado
      verify: python3 plugins/quenching/assets/bin/skills.py lint {a cópia temporária} --json
- [ ] 5.3 Rodar a verificação manual declarada em `## Validation` numa sessão nova — `/docs:align`
      num repo de árvore suja, conferindo que a linha de forma aparece dentro do bloco de plano e
      não num segundo prompt — e **dizer no relatório que o check foi manual**
