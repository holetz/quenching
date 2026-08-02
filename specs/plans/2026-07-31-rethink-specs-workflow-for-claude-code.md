---
slug: rethink-specs-workflow-for-claude-code
title: Rethink the specs workflow for Claude Code worktrees
verification: per-section
refined: {mode: gate, date: 2026-08-01}
priority: {level: 28, criticality: medium, date: 2026-08-01}
---

# Rethink the specs workflow for Claude Code worktrees

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

Este spec tira o plugin do ramo de **possuir** worktrees. O fluxo de isolação foi desenhado quando
ninguém mais as criava, então `/specs:isolate` cria e nomeia e `/specs:conclude` destrói — e no Claude
Code a worktree já existe, com outro nome e em outro lugar, o que faz o plugin criar a segunda. Três
specs em `plans/` são sintomas dessa colisão; nenhuma ataca a causa.

`## Proposal` afirma a inversão: adotar por padrão, criar só sob pedido explícito, **nunca** remover,
e integrar sempre por Pull Request em vez de merge local. `## Design` registra as cinco decisões e
nomeia os contratos que elas reescrevem — incluindo o parágrafo de `git.md` que justifica
`plan/<slug>` justamente pelo ranqueamento que esta mudança substitui. `## Alternatives Considered`
guarda as três formas descartadas, entre elas apagar `/specs:isolate` de vez. `## Out of Scope`
declara as três specs que isto subsume e as duas outras causas que não são esta.
`## Impact` declara os quatro standards que a execução promete escrever — três reescritas e um novo,
que é onde a inversão passa a morar. `## Open Decisions` carrega as três coisas que seguem sem dono,
entre elas onde passa a morar o consentimento do `worktreeSetup` quando não existe mais uma oferta de
isolação para carregá-lo; a quarta — a forma do record de integração — foi fechada e virou decisão em
`## Design`.
## Problem

O fluxo de isolação da frente `specs/` foi desenhado em torno do VSCode, que não tem forma
confortável de operar worktrees do git. Essa restrição é a razão de a frente carregar a própria
maquinaria de isolação — `/specs:isolate`, o record `branch: {base, work}`, a criação e a remoção da
worktree — e de vários comandos raciocinarem sobre em que branch um spec está.

O desenvolvimento migrou para o Claude Code, que opera worktrees nativamente. Nesse cenário a mesma
maquinaria atrapalha mais do que ajuda, e vale rever o fluxo inteiro para aproveitar worktrees de
verdade — junto com o que a `2026-07-31-configurable-spec-backend` entregará de graça.

O que o disco mostra é mais concreto do que isso. O plugin coloca a worktree em `../<repo>-<slug>`,
**nunca dentro do repo**, numa branch `plan/<slug>` cujo nome `specs.py next --front` usa para
ranquear; o Claude Code coloca em `.claude/worktrees/<nome>-<hash>`, dentro do repo, numa branch
`claude/<nome>-<hash>`. Das cinco worktrees vivas hoje, uma só está numa branch `plan/*`, e uma
delas está checada numa branch que não é a sua. Três specs em `plans/` — `resolve-spec-from-worktree`,
`commit-on-worktree-specs` e `align-in-worktree-then-merge` — são sintomas dessa colisão, e nenhuma
ataca a causa: **dois donos para a mesma worktree.**

## Proposal

- O plugin **deixa de possuir worktrees**. `/specs:isolate` separa **detectar** de **criar**: estando
  numa árvore de trabalho fora da base, ele **adota** — grava `branch: {base, work}` com a branch
  real, qualquer que seja o nome, e prepara a árvore se ela ainda não foi preparada.
- **Criar continua disponível, sob pedido explícito**, e deixa de ser o caminho recomendado. É o que
  mantém o plugin usável num repositório sem Claude Code.
- **Nada no plugin remove uma worktree, nunca.** `/specs:conclude` para de remover a que encontrou:
  reporta o caminho e a deixa de pé.
- `plan/<slug>` deixa de ser requisito e volta a ser apenas o default de quem *o plugin* corta.
  Qualquer branch passa a ser legítima, e o vínculo spec↔branch vem do record `branch:`, não do nome
  — o que obriga `specs.py next --front` a trocar a fonte do seu ranqueamento de "está em voo".
- A integração passa a ser **sempre um Pull Request**. `/specs:conclude` arquiva e distila na branch
  de trabalho como hoje, e sua última ação passa a ser **abrir o PR**, sob confirmação, em vez de
  fazer o merge local. As quatro estratégias de merge deixam de ser oferecidas.
- Os três aligns (`/docs:align`, `/specs:align`, `/skill:align`) também deixam de propor worktree.

## Out of Scope

- **As três specs que este trabalho subsume** — `resolve-spec-from-worktree` (a detecção *é* a
  adoção), `commit-on-worktree-specs` (o commit passa a ser consequência de a worktree ser a do
  spec) e `align-in-worktree-then-merge` (propor worktree num align deixa de fazer sentido quando o
  plugin não as possui). Este spec **não apaga nenhuma**: cada uma fecha com
  `/specs:conclude <slug>` como `abandoned`, por decisão humana.
- **A cerimônia por spec** — a quantidade de comandos e turnos de `create` → `develop` → `execute` →
  `conclude`. É uma causa diferente da posse da worktree, e atacá-la aqui misturaria duas coisas.
- **A visibilidade de um spec entre worktrees** — a `configurable-spec-backend` já a entrega, pondo
  os specs numa branch dedicada.
- **Renomear as branches `claude/*` vivas para `plan/*`, ou migrar as worktrees existentes.** A
  adoção passa a aceitar o nome que encontrar; mexer no que já está de pé é trabalho à parte e
  arriscado.
- **Acompanhar o PR até o merge.** A run termina ao abrir o PR; o que acontece depois é do host.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/workflows/plan-git-record.md` — reescrito: o record da integração, o fim da
  remoção de worktree, e `plan/<slug>` rebaixado ao default de quem *o plugin* corta.
- `docs/standards/workflows/plan-lifecycle.md` — reescrito: o vocabulário de records ganha
  `pr: {number, url}` e marca `merge:` como legado só-leitura.
- `docs/standards/workflows/worktree-setup.md` — reescrito: §The consent is the isolation offer não
  sobrevive a uma adoção (ver `## Open Decisions`).
- `docs/standards/workflows/worktree-ownership.md` (novo) — a regra durável que este spec prova: o
  plugin não possui worktrees — adota por padrão, cria sob pedido, **nunca** remove; qualquer branch
  é legítima e o vínculo spec↔branch é o record, não o nome.

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/specs.py` — o record `pr:`, a leitura do `merge:` legado, e a fonte
  do "está em voo" em `next --front`.
- `plugins/quenching/commands/specs/isolate.md` — separar **detectar** de **criar**.
- `plugins/quenching/commands/specs/conclude.md` — abrir o PR como última ação; parar de remover a
  worktree que encontrou.
- `plugins/quenching/assets/references/specs-isolate/git.md` — §Merge strategies, §The worktree is
  removed after a successful merge, §Branch and worktree names.
- `plugins/quenching/commands/docs/align.md`, `.../specs/align.md`, `.../skill/align.md` — deixam de
  propor worktree.

## Design

- **Decisão: adotar é o padrão, criar é sob pedido.** A alternativa de delegar a criação ao fluxo
  nativo do Claude Code garantiria um único criador por construção, mas acoplaria o plugin a um
  recurso do harness que ele não controla e abandonaria o repositório sem Claude Code — que é alvo
  declarado do produto. Manter o caminho de criação, rebaixado a não-recomendado, compra o mesmo
  resultado no caso comum sem pagar esse preço.
- **Decisão: a assimetria criar/remover é deliberada.** Criar uma worktree é reversível; remover não
  é. E sob Claude Code a árvore que `/specs:conclude` removeria é justamente aquela onde a sessão do
  humano está de pé. Tratar as duas capacidades simetricamente é o que produziria o dano, então o
  plugin mantém uma e abandona a outra por inteiro — não "remove só o que criou", que exigiria um
  record de proveniência e ainda erraria quando ele faltasse.
- **Decisão: qualquer branch é legítima, e o record é a fonte do vínculo.** O nome deixa de carregar
  significado operacional.
- **Decisão: a integração é sempre um PR, e `/specs:conclude` abre e para.** A ordem que a frente já
  garante sobrevive — arquivar e distilar na branch de trabalho, e o PR como última ação da run, de
  modo que nada é commitado na base depois. O que muda é que o merge passa a acontecer **fora da
  run**, e portanto não pode mais ser descrito no fechamento.
- **Decisão: o record da integração é `pr: {number, url}`, e `merge:` vira legado só-leitura.** Sob
  PR nada de `merge: {strategy, subject}` sobrevive ao teste de admissão: não há escolha de
  estratégia — o host decide — e o `subject` nomearia um commit que esta run nunca vê. `pr:` é
  estampado write-once logo após `gh pr create` retornar, e `merge:` continua sendo **lido** para
  sempre, pelo mesmo precedente que `plan-git-record.md` já aplica a `commit:` versus `subject:`
  (§Two forms are read, forever). Isto abre a **primeira exceção declarada** à regra "todo record é
  escrito antes da coisa que descreve": o número do PR só existe depois do PR, porque é fato do host
  e não do git. A exceção é estreita — o commit do record cai na branch de trabalho, nunca na base,
  que é o que aquela regra existe para proteger — mas custa um segundo push para que o record entre
  no PR, e `plan-git-record.md` passa a dizer isso em vez de ser contradito em silêncio.

**Contratos vinculantes que estas decisões reescrevem** — declarados aqui, reescritos na execução:

- `plugins/quenching/assets/references/specs-isolate/git.md` §Merge strategies — as quatro
  estratégias deixam de ser oferecidas.
- o mesmo arquivo, §The worktree is removed after a successful merge — a remoção deixa de existir.
- o mesmo arquivo, §Branch and worktree names — hoje justifica `plan/<slug>` precisamente porque
  `specs.py next --front` ranqueia casando no nome. Esse argumento cai com a decisão acima, e a
  narrativa antiga é preservada como o que foi revertido.
- `docs/standards/workflows/worktree-setup.md` §The consent is the isolation offer — ver
  `## Open Decisions`: numa adoção não existe oferta para carregar o consentimento.
## Alternatives Considered

Quatro formas foram comparadas — diferentes em forma, não em parâmetro. A escolhida está em
`## Proposal`; as três derrotadas ficam aqui com a razão de terem perdido.

- **Sair do ramo: apagar `/specs:isolate` e o record `branch:`, deixando o git para o humano.** A
  menor superfície de todas, e o único argumento realmente forte contra ela é o `base`: depois do
  merge o git não sabe mais de onde a branch foi cortada, e é exatamente essa a razão de o record
  existir. Perderia também o sinal de "está em voo" que `/specs:continue` usa. Rejeitada por
  descartar dois fatos que nada reconstrói, para resolver um problema de posse.
- **Inverter: `/specs:isolate` deixa de rodar `git worktree add` e passa a acionar o fluxo nativo do
  Claude Code.** Garante um único criador por construção, que é o resultado mais limpo possível.
  Rejeitada por acoplar o plugin a um recurso do harness que ele não controla, abandonando o
  repositório sem Claude Code — que é alvo declarado do produto.
- **Remendar: manter `plan/<slug>` e `../<repo>-<slug>`, só ensinando cada comando a notar que está
  numa worktree.** É o caminho mais barato e nada quebra hoje; são as três specs já em `plans/`.
  Rejeitada por manter dois criadores da mesma coisa — ou seja, por manter a causa e tratar apenas
  os sintomas, que é como esses três specs nasceram.

## Open Decisions

- ~~Como o record `merge:` se serializa quando a integração é um PR.~~ **Fechada em 2026-08-01**, no
  bank `gate` — a decisão está em `## Design` (record novo `pr: {number, url}`, write-once,
  estampado após `gh pr create` retornar; `merge:` legado só-leitura). As duas derrotadas: manter
  `merge:` com explicit none exigiria afrouxar `sp-bad-merge` para aceitar um record que não afirma
  nada; aposentar o campo sem substituto deixaria o spec arquivado sem o link do PR quando o host
  não puder mais ser consultado.
- **De onde `specs.py next --front` passa a tirar o "está em voo".** Ler o `branch:` de cada spec
  (autoritativo, mas custa abrir cada arquivo) ou perguntar ao git por qualquer branch/worktree viva
  e casar contra os records. **Decidido** na task que reescreve o ranqueamento, medindo o custo real
  com as 32 specs de `plans/`.
- **Onde mora o consentimento do `worktreeSetup` numa adoção.** Hoje ele *é* a escolha "Worktree" na
  oferta de isolação: o comando do repositório alvo é exibido verbatim no bloco de plano e escolher
  Worktree é o OK para ele. Adotando uma worktree que já existe não há oferta, e sem outra forma o
  plugin passaria a executar shell do alvo sem tela onde julgá-lo — o que o contrato proíbe.
  **Decidido** antes de a adoção rodar setup algum; enquanto não estiver decidido, a adoção não roda
  setup.
- **O que "sempre via PR" faz num repositório sem remote ou sem host.** Degradar para reportar que a
  branch está pronta, ou recusar. **Decidido** na task que reescreve `/specs:conclude`, junto com a
  decisão sobre qual binário (`gh`, `az`) o caminho recomendado passa a exigir.
## Handoff

- **Pré-requisito declarado: `configurable-spec-backend` mergeada.** As duas reescrevem os mesmos
  três lugares — `specs-isolate/git.md`, `docs/standards/workflows/worktree-setup.md` e `specs.py` —
  e ela já está `approved` com sete seções de tasks. Começar antes significa reescrever os mesmos
  parágrafos duas vezes. Depois dela, três coisas vêm de graça: a config já mora em
  `.claude/quenching.json`, `.claude/worktrees/` já está ignorado e reconhecido pela CLI, e o anchor
  task→commit já é o sha — o que tira `plan/<slug>` do caminho crítico do vínculo.
- **Observação de campo, verificada neste repositório em 2026-07-31:** `git status --porcelain` fica
  **limpo** no checkout principal com cinco worktrees presentes em `.claude/worktrees/`, mesmo com o
  path **fora** do `.gitignore` — o git exclui do status as worktrees que ele mesmo registrou. Isso
  contradiz o que a `## Handoff` da `configurable-spec-backend` afirma ("uma worktree untracked
  quebraria o gate de árvore limpa"). O fato importa aqui porque a adoção depende de worktrees dentro
  do repo não sujarem a árvore que `/specs:execute` exige limpa.
- Nenhuma edição em `commands/**` é testável na sessão que a escreve — o registry é montado no início
  da sessão. Toda seção que mexe em body termina em `doctor`, não em teste funcional.
