---
slug: declare-repo-body-language
title: Declare the repo's body language in docs/standards so every command reads it for free
verification: per-section
priority: {level: 16, criticality: high, date: 2026-07-29}
refined: {mode: adversarial, date: 2026-07-30}
approved: {date: 2026-07-29}
---

# Declare the repo's body language in docs/standards so every command reads it for free

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

Vincula a expressão solta "the repo's language", à qual seis cláusulas espalhadas pelos standards e
pelas references entregues deferem sem que nenhuma delas a defina. Um repositório declara sua body
language como uma tag BCP-47 em uma linha do seu harness **raiz** — em contexto no início da sessão,
e funcionando sem um `docs/` bundle — enquanto um doc de standards entregue **é o dono** da regra que
essas seis cláusulas passam a citar em vez de reenunciar. A language declarada governa todo body,
inclusive as seções voltadas a agentes.

O dono vai para um subject novo, `docs/standards/agents/` — *como instruímos agentes* —, que faz a
árvore canônica travada crescer em um, porque `naming/` governa nomes e esta regra não nomeia nada, e
`automation/` colide nos repositórios mais propensos a adotar o bundle.

`/docs:align` pergunta uma vez, na adoção; o silêncio continua sem restrição, então a adoção é
opt-in por repositório e nada se torna retroativamente não conformante.

Este é também o spec que formaliza a própria regra sob a qual seu body está escrito: o corpo aqui
está em pt-BR e a estrutura — frontmatter, H1, `##` headings, metadados de task, caminhos e comandos
— segue em inglês canônico. `## Open Decisions` guarda o que este spec deliberadamente **não**
decide, incluindo o censo das outras dez reenunciações da mesma cláusula que ele não colapsa.
## Problem

Hoje os bodies dos specs são escritos em inglês, o que os torna difíceis de ler para os usuários de
um repositório cuja língua de trabalho não é o inglês (português, por exemplo). A regra da canonical
surface já fixa o que precisa permanecer em inglês — nomes de pasta, slugs de arquivo, chaves de
frontmatter, valores de `type` —, mas nada diz sobre onde um repositório *declara* em que língua seus
bodies devem ser escritos, de modo que hoje cada comando adivinha ou deixa a decisão para quem está
digitando.

Essa declaração precisa de uma casa própria no repositório — de preferência sob `docs/standards/` — e
alcançá-la tem de ser quase gratuito para o agente: barato o suficiente para que saber a configuração
correta nunca seja motivo para deixar de conferir. Um hook que a leia automaticamente é um mecanismo
candidato.

## Proposal

Seis cláusulas — duas em `docs/standards/`, quatro em `assets/references/` — deferem o body prose a
"the repo's language", e nada em lugar algum vincula essa expressão a um valor. Este spec a vincula,
com um mecanismo que serve tanto a este repositório quanto a todo repositório que o plugin alinha.

Um repositório declara sua body language em uma linha do seu arquivo de harness **raiz** (`CLAUDE.md`
/ `AGENTS.md`): em contexto no início da sessão, custando zero tool calls, e funcionando em um
repositório que tem `specs/` e nenhum `docs/` bundle. **Somente o harness raiz carrega a
declaração.** Um arquivo de harness aninhado (`docs/standards/CLAUDE.md`) é carregado quando aquela
pasta é tocada, não no início da sessão, então não entregaria nada do custo zero pelo qual esta forma
foi escolhida.

O enunciado da regra ganha **um único dono** — `docs/standards/agents/body-language.md`, entregue no
skeleton sob `assets/docs/`. As seis cláusulas deixam de reenunciar a regra e passam a citar esse doc:
o colapso que `docs/standards/architecture/plugin-layout.md` já defende, aplicado a uma regra que
havia sido escrita seis vezes.

`/docs:align` pergunta a language **uma vez**, quando um repositório adota o bundle, e escreve a
linha no harness raiz; `/docs:harness` a mantém dali em diante. **O silêncio conserva seu significado
atual** — um repositório que não declara nada não está sob restrição alguma, exatamente como as seis
cláusulas `MAY` são lidas hoje. Nada se torna retroativamente não conformante e nenhum repositório já
adotado precisa mudar.

Depois disso, um agente que precise saber em que língua um body está escrito lê essa informação de
graça no início da sessão, em vez de adivinhar ou perguntar a quem está digitando.
## Out of Scope

- **Traduzir os bodies que já existem.** Declarar uma language não reescreve os trinta e cinco docs
  em inglês sob `docs/standards/`, nem os de nenhum repositório-alvo. Isso é uma migração, e é spec
  próprio.
- **Enforcement por máquina.** Nenhuma verificação de língua natural entra em `okf-validate.py` —
  `assets/references/docs-align/conformance.md` já registra que um validador não consegue detectar a
  língua de um documento de forma confiável. A declaração é aplicada por convenção, como já é hoje.
- **A canonical surface.** Nomes de pasta, slugs de arquivo, chaves de frontmatter, valores de `type`
  e os `##` headings parseados permanecem em inglês canônico. Esta é a regra que já existe em
  `docs/standards/naming/command-surface.md`, nomeada aqui como o limite que este spec complementa —
  não algo que ele mude.
- **A própria surface do plugin.** As vinte e seis `description`s de comando e todo body sob
  `commands/**` são em inglês, qualquer que seja a language que um repositório-alvo declare.

## Impact

**Código e conteúdo que este spec toca:** os seis locais que reenunciam a regra, listados em
`## Design`; `docs/index.md` e `plugins/quenching/assets/docs/index.md`, cuja linha "only
`audience: human` material follows the repo's language" é mais estreita do que o que este spec
decide; `plugins/quenching/assets/references/docs-align/taxonomy.md`, cuja §The canonical tree
(locked) cresce em um subject; as duas listas de subtopics em `standards/index.md` e as duas novas
listagens de subject em `agents/index.md` (listagens reservadas, não standards — e é por isso que não
aparecem na lista abaixo); `plugins/quenching/commands/docs/align.md` (a pergunta única na adoção);
e `plugins/quenching/commands/docs/harness.md` (a linha da declaração como um KEEP que nunca
parafraseia a regra).

### Standards this spec will write into docs/standards/

- `docs/standards/agents/body-language.md` — o dono único da regra, escrito duas vezes no mesmo
  caminho relativo ao bundle: uma vez no skeleton entregue sob
  `plugins/quenching/assets/docs/`, e uma vez no bundle deste próprio repositório, para que o repo
  que entrega a regra seja também seu primeiro consumidor
## Validation

- `grep -rn "the repo.s language" docs/ plugins/quenching/assets/references/` retorna os cinco locais
  que citam o dono e **nenhuma** reenunciação da regra, mais a declaração autocontida deliberada de
  `okf-spec.md`. Uma sexta reenunciação **dentro dessas duas árvores** é falha; as reenunciações que
  vivem fora delas estão registradas em `## Open Decisions` e não pertencem a este invariante.
- A linha do harness raiz carrega um valor e uma citação e **nenhuma paráfrase da regra** — o
  invariante que mantém este design compatível com `/docs:harness` §Move, never copy.
- `grep -n 'agents/' plugins/quenching/assets/references/docs-align/taxonomy.md` mostra o subject
  dentro de §The canonical tree (locked), e os dois arquivos `standards/index.md` carregam sua linha de
  subtopic. Um subject que existe em disco mas não na árvore travada é a não conformidade que este
  spec está corrigindo, não um estado que ele possa deixar para trás.
- `python3 plugins/quenching/assets/hooks/okf-validate.py assets/docs` e o mesmo em `docs`
  reportam ambos `0 error(s), 0 warning(s)` com o novo subject e o novo doc de standards no lugar.
## Design

**Regra e valor são dois fatos diferentes, cada um em um lugar só.** A linha do harness carrega o
**valor** e uma citação; o doc de standards carrega o **contrato** — o que declarar significa, o que o
silêncio significa. Nenhum dos dois parafraseia o outro. É isso que mantém o mecanismo do lado certo
de `/docs:harness` §Move, never copy: uma regra reenunciada em um arquivo de harness é exatamente o
drift que aquele comando existe para remover, enquanto um valor mais uma citação não é reenunciação.

**O valor é uma tag BCP-47** (`pt-BR`, `en`), não um nome de língua. Um nome convida `Português`,
`portugues` e `Portuguese` a significarem a mesma coisa, e nenhuma citação resolve isso; uma tag é uma
string com uma grafia só.

**A language declarada governa todo body**, `## Handoff` e `## Tasks` incluídos — essas seções
continuam terse, porque são contexto de agente, mas terse na language declarada. Isso é mais amplo que
`docs/index.md`, que hoje limita a regra a material `audience: human`, então aquela linha e sua gêmea
no skeleton são reconciliadas como parte deste spec (ver `## Impact`).

**O dono é `docs/standards/agents/body-language.md`** — um subject novo, e a árvore travada cresce em
um para acomodá-lo. O subject é *como instruímos agentes*: o que a surface always-on declara a quem a
lê no início da sessão. Duas casas de aparência mais próxima foram rejeitadas nos autos, em
`## Alternatives Considered`; a forma curta é que `naming/` governa nomes e esta regra não nomeia
nada, e `automation/` colide justamente nos repositórios mais propensos a adotar o bundle — um repo
cujo próprio produto é automação não consegue distinguir "how we drive Claude Code" de "our automation
domain" sob uma única pasta. `automation/` também não está no conjunto entregue: é o subject local
deste repositório, o que é precisamente a ambiguidade que se está evitando.

Fazer a árvore travada crescer se sobrepõe ao spec enfileirado `revise-standards-subject-folders`;
ver `## Risks`.

Os quatro locais em `assets/references/**` citam o dono pelo seu caminho relativo ao bundle, que **só
resolve depois que o skeleton está instalado** — aceito, com a mitigação de que a ordem das tasks
entrega o doc antes que qualquer local seja editado para citá-lo. Em um repositório que usa `specs/` e
nunca adota o bundle a citação não resolve; ver `## Risks`.

O colapso, por camada:

| Camada | Local | Depois |
| --- | --- | --- |
| `docs/standards` | `naming/command-surface.md:118` | cita o dono |
| `docs/standards` | `workflows/plan-artifacts.md:69` | cita o dono |
| `assets/references` | `specs-develop/spec-driven.md:119` | cita o dono |
| `assets/references` | `docs-align/taxonomy.md:117` | cita o dono |
| `assets/references` | `docs-align/migration.md:40` | cita o dono |
| `assets/references` | `docs-align/okf-spec.md:111` | **conserva uma declaração autocontida** — é o contrato que outros implementadores leem, e um format spec que defere a um doc local do repo deixa de ser autodescritivo |
## Alternatives Considered

| Abordagem | Por que perdeu |
| --- | --- |
| **O dono sob `naming/`** — onde a cláusula sendo vinculada já vive | Vizinhança, não pertencimento. `docs/standards/naming/index.md` limita o subject a "the globally unique, predictable **names** this repo commits to", e a gêmea do skeleton o limita à nomenclatura de **dados** sem rodeios — `tables · columns · descriptions · schemas-catalogs`. Em que língua natural a prosa está escrita não nomeia nada. Colocá-lo ali significava esticar um subject declarado de dentro de uma task. |
| **O dono sob `automation/`** | A pasta existente que melhor se encaixa — o carregador é o harness always-on e `automation/context-budget.md` já governa esse budget — e rejeitada de todo modo, porque colide exatamente nos repositórios que adotam este bundle: um cujo produto *é* automação não consegue distinguir "how we drive Claude Code" de "our automation domain" sob uma única pasta. Também não está nos nove entregues; é o subject local deste repo, que é a mesma ambiguidade um nível abaixo. |
| **Uma chave em `docs/index.md`**, ao lado de `okf_version` | Ser legível por máquina não compra nada aqui: `docs-align/conformance.md` registra que nenhum validador jamais vai ramificar sobre esse valor, então o único consumidor é o agente — que lê o harness de graça. Também custa uma edição em `okf-spec.md`, cuja linha 92 fixa aquela listagem apenas a `okf_version`, colidindo com o spec enfileirado `upgrade-okf-to-v0-2`. E exclui um repositório com `specs/` e sem bundle. |
| **Um hook `SessionStart` injetando o valor** | Um processo por sessão, para sempre, para entregar uma constante que o harness auto-carregado já entrega de graça. `docs/standards/automation/hooks.md` exige que um hook justifique seu escopo; este não consegue. |
| **Só o doc de standards, sem carregador** | Dá à regra uma casa, uma autoridade e um mantenedor, mas nada faz um agente lê-la — descoberta é exatamente o custo que `## Problem` diz que precisa ficar perto de zero. |
| **Não fazer nada** | As seis cláusulas dizem `MAY`, então um repositório escrevendo português já é conformante sem declarar nada. Rejeitado porque a lacuna não é conformidade: é que um agente não tem como *saber*, e é isso que o faz adivinhar. |
| **`agents/` só neste repositório, criado sob demanda pelo `/docs:align` no alvo** — em vez de fazer o skeleton entregue crescer | Perdeu por transformar um risco limitado em universal. As quatro citações em `assets/references/**` são relativas ao bundle, então um subject criado sob demanda faz o risco "a citação não resolve" valer para todo bundle que ainda não rodou o align, e não apenas para um repositório `specs/`-only. Um subject que existe na árvore travada e não no skeleton entregue é também exatamente a divergência que o terceiro bullet de `## Validation` foi escrito para impedir. |
## Open Decisions

- **`AGENTS.md` é um carregador em pé de igualdade com `CLAUDE.md`?** Este spec assume que sim,
  porque o plugin já trata o par como um só em nove pontos e `/docs:harness` varre os dois. **Como
  será decidido:** pelo spec irmão `decide-agents-md-harness-default`, não por este. Se ele tornar
  `AGENTS.md` o alvo padrão, o que muda é a redação do doc dono, não este mecanismo — razão pela qual
  este spec não espera por ele.
- **As outras dez reenunciações da mesma cláusula `MAY`, fora das duas árvores que este spec varre,
  também colapsam?** O censo completo, levantado nesta passagem adversarial:
  `plugins/quenching/assets/README.md:115`,
  `plugins/quenching/assets/templates/harness/claude-root.md:71`,
  `plugins/quenching/assets/templates/harness/claude-subfolder.md:32`,
  `plugins/quenching/assets/bin/specs.py:292`,
  `plugins/quenching/assets/specs/templates/spec.md:39`,
  `plugins/quenching/commands/docs/add.md:37`, `plugins/quenching/commands/docs/align.md:79`,
  `plugins/quenching/commands/docs/define.md:76` e `plugins/quenching/commands/docs/learn.md:41` e
  `:79`. Este spec **não** as toca, e o limite que ele mantém é este: as seis que ele colapsa são
  enunciados **normativos** da regra (um standard ou uma reference compartilhada), enquanto essas dez
  são texto de template entregue — que aterra em um repositório-alvo que pode não ter bundle algum
  para citar — ou uma condição lateral dentro de um body de comando. **Como será decidido:** por um
  spec de follow-up próprio, porque as gêmeas de template obrigam edição em par (`specs.py` e
  `assets/specs/templates/spec.md`, "Edit both or neither") e os bodies de comando são a surface em
  inglês que `## Out of Scope` já protege. Até então o censo fica registrado aqui, para que ninguém
  precise redescobri-lo.
- **Quando o doc dono sai de `authority: background` para `current`?** A task 2 o entrega em
  `background` até a regra ser provada pelo uso, e nada declara o que conta como provado. **Como será
  decidido:** pelo primeiro comando que efetivamente ramifique sobre o valor declarado — hoje nenhum
  ramifica, porque `/docs:align` e `/docs:harness` apenas escrevem e preservam a linha. Quando esse
  consumidor existir, a promoção é uma edição de uma linha em `authority:`. Este spec não a agenda, e
  a decisão não bloqueia nenhuma das sete tasks.

## Risks

- **Este spec agora faz a árvore travada crescer, e `revise-standards-subject-folders` também pretende
  revisá-la.** Dois specs editando o mesmo conjunto declarado de subjects podem cada um entregar
  metade dele. **Accepted, with the boundary stated:** este spec adiciona exatamente um subject e não
  toca em nenhum outro, e o spec irmão continua livre para revisar o conjunto como um todo depois —
  inclusive renomeando o que este adicionou. O que este spec não pode fazer é antecipar aquela
  revisão reorganizando subjects de que não precisa. Se o irmão entrar primeiro, a task 1 encolhe para
  uma linha em qualquer conjunto que ele tenha produzido.
- **A citação não resolve em um repositório que nunca adota o bundle.** Um repositório `specs/`-only
  lê uma reference citando `docs/standards/agents/body-language.md`, que ele não tem. **Accepted
  risk** — a alternativa era um dono sob `assets/`, o que colocaria a regra fora do bundle que ela
  governa. Mitigação: as quatro citações nas references nomeiam o doc como *do bundle*, então um
  repositório sem bundle lê um ponteiro para algo que sabidamente não tem, em vez de uma promessa
  quebrada.
- **`agents/` é lido como "definições de agente" e não como "como instruímos agentes".** O nome é
  curto o bastante para convidar à leitura mais estreita, e `docs/standards/automation/agents.md` já
  guarda o contrato de definição de `.claude/agents/`. Mitigado pelo `index.md` do subject enunciando
  o limite em sua primeira linha, e por aquele doc existente ser candidato a mudar de casa quando o
  spec irmão revisar o conjunto — não por este.
- **Regra e valor se afastam — ou a linha simplesmente desaparece.** A **paráfrase** é mitigada pelo
  invariante de `## Validation`: a linha do harness nunca parafraseia a regra, então não há do que ela
  divergir. A **remoção** é o modo de falha mais silencioso dos dois: uma linha cujo conteúdo inteiro
  é um valor mais uma citação é exatamente a forma que uma passagem de emagrecimento do
  `/docs:harness` trata como ponteiro colapsável, e nenhum validador nota a falta dela — os arquivos
  de harness são isentos em `okf-validate.py`. Mitigado pela task 7, que ensina o comando que a linha
  é um KEEP; a detecção é essa task e nada mais, e é por isso que ela não é opcional.
- **Ordem das tasks.** Editar um local para citar o doc antes de o skeleton entregá-lo deixa uma
  citação pendurada em um plugin já lançado. Mitigado pela ordem declarada em `## Tasks`.
- **O grep declarado em `## Validation` não vê todas as ocorrências que precisa ver.** O padrão é de
  uma linha, e em dois dos locais a expressão está quebrada por wrap:
  `docs/standards/workflows/plan-artifacts.md:69` traz `follows the` / `repo's language` e
  `plugins/quenching/assets/references/docs-align/okf-spec.md:110` traz `the repo's` / `language**`.
  Hoje o grep retorna cinco ocorrências e omite justamente as duas mais importantes — a que precisa
  colapsar e a que precisa **não** colapsar. Mitigação: o grep é um alarme contra reenunciação **nova**,
  não um censo; quem executa a task 5 enumera os seis locais pela tabela de `## Design`, e confere os
  dois quebrados por wrap com `grep -rn -A1` antes de declarar a task pronta.
## Handoff

Nada construído ainda — tasks 1–7 abertas, nenhuma bloqueada, nenhuma commitada. Duas ordens são
load-bearing: a task 1 abre o subject antes de qualquer coisa ser escrita nele, e a task 2 entrega o
dono antes de a task 5 fazer qualquer local citá-lo.

Estado que um executor novo não consegue derivar:

- O subject `agents/` não existe em nenhuma das duas árvores. A task 1 o cria **e** o declara em
  `taxonomy.md` §The canonical tree (locked) — editar aquela seção é intencional aqui, não um deslize.
- Não funda `docs/standards/automation/agents.md` dentro do subject novo. Ele é o contrato de
  definição de `.claude/agents/`, fica onde está, e movê-lo pertence a
  `revise-standards-subject-folders`.
- O doc dono não existe em lugar algum ainda. As duas escritas são criações.
- Os seis locais ainda reenunciam a regra literalmente. `okf-spec.md` é o que conserva sua declaração
  — não o colapse.
- `docs/index.md` e `plugins/quenching/assets/docs/index.md` ainda limitam a regra a
  `audience: human`; a task 4 as amplia. Lê-los antes da task 4 dá a redação de antes da decisão.
- Os dois `standards/index.md` carregam uma zona `## Current docs` entre `BEGIN GENERATED` e
  `END GENERATED`, agrupada por subject e reconstruída a partir do disco. **Nada a valida:**
  `okf-validate.py` não conhece o conjunto de subjects e checa apenas `dir-no-index`, links de
  listagem quebrados e docs órfãos. Logo o `verify:` das tasks 1–3 reporta
  `0 error(s), 0 warning(s)` mesmo com a zona sem o grupo `### agents/`. Regenere a zona nas duas
  árvores dentro da própria task em que o doc aterra.
- Esta sessão roda sem branch `plan/`: a isolação foi declinada porque a branch designada da sessão é
  mandatória. Nenhum registro `branch` é estampado, e os commits aterram nessa branch.
- `verification: per-section` — verifique no limite de cada task, conforme o `verify:` daquela task.
## Tasks

Ordenadas, e a ordem é load-bearing duas vezes: a task 1 abre o subject antes de qualquer coisa ser
escrita nele, e a task 2 entrega o dono antes de a task 5 fazer qualquer local citá-lo — ou um plugin
lançado carrega uma citação pendurada. Cada task nomeia o caminho `docs/standards/**` que declara na
própria linha do checkbox, porque `sp-impact-uncovered` casa com aquela linha e não com a continuação
`files:`.

- [ ] 1 Abrir o subject `agents/` nas duas árvores — pasta + `index.md` no skeleton e neste
  repositório, o subject adicionado a `taxonomy.md` §The canonical tree (locked), e uma linha de
  subtopic nos dois `standards/index.md`. O limite do subject: como instruímos agentes — o que a
  surface always-on declara. Distinto de `automation/` (o subject local deste repo para a própria
  command surface).
  files: `plugins/quenching/assets/references/docs-align/taxonomy.md`, `plugins/quenching/assets/docs/standards/index.md`, `plugins/quenching/assets/docs/standards/agents/index.md`, `docs/standards/index.md`, `docs/standards/agents/index.md`
  verify: `python3 plugins/quenching/assets/hooks/okf-validate.py assets/docs` and `... docs` both report `0 error(s), 0 warning(s)`
- [ ] 2 Entregar o dono no skeleton em `docs/standards/agents/body-language.md` sob `assets/docs/`
  Enuncia o que declarar significa, que somente o harness **raiz** o carrega, que o valor é uma tag
  BCP-47, e que o silêncio significa nenhuma restrição. Frontmatter OKF completo;
  `authority: background` até a regra ser provada pelo uso.
  files: `plugins/quenching/assets/docs/standards/agents/body-language.md`, `plugins/quenching/assets/docs/standards/agents/index.md`
  verify: `python3 plugins/quenching/assets/hooks/okf-validate.py assets/docs` → `0 error(s), 0 warning(s)`
- [ ] 3 Instalar o mesmo dono em `docs/standards/agents/body-language.md` no bundle deste repo, e
  declarar a body language deste próprio repositório no harness raiz — o dogfood que o spec alega.
  files: `docs/standards/agents/body-language.md`, `docs/standards/agents/index.md`, `CLAUDE.md`
  verify: `python3 plugins/quenching/assets/hooks/okf-validate.py docs` → `0 error(s), 0 warning(s)`
- [ ] 4 Reconciliar as duas linhas de index que limitam a regra a `audience: human` com a decisão
  deste spec de que a language declarada governa todo body.
  files: `docs/index.md`, `plugins/quenching/assets/docs/index.md`
  verify: `grep -n 'audience: human' docs/index.md plugins/quenching/assets/docs/index.md` shows no
  language clause narrowed by audience
- [ ] 5 Colapsar os seis locais que reenunciam a regra para que citem o dono; `okf-spec.md` conserva
  sua declaração autocontida com a razão registrada inline.
  files: `docs/standards/naming/command-surface.md`, `docs/standards/workflows/plan-artifacts.md`, `plugins/quenching/assets/references/specs-develop/spec-driven.md`, `plugins/quenching/assets/references/docs-align/taxonomy.md`, `plugins/quenching/assets/references/docs-align/migration.md`, `plugins/quenching/assets/references/docs-align/okf-spec.md`
  verify: the `## Validation` grep returns five citing sites and no restatement
- [ ] 6 Ensinar `/docs:align` a perguntar a body language uma vez na adoção e escrever a linha no
  arquivo de harness raiz.
  files: `plugins/quenching/commands/docs/align.md`
  verify: `grep -n 'body language' plugins/quenching/commands/docs/align.md`
- [ ] 7 Ensinar `/docs:harness` que a linha da declaração é um KEEP e nunca deve parafrasear a
  regra — o invariante que `## Validation` afirma.
  files: `plugins/quenching/commands/docs/harness.md`
  verify: `grep -n 'body language' plugins/quenching/commands/docs/harness.md`
