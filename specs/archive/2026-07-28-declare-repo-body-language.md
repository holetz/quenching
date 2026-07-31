---
slug: declare-repo-body-language
title: Declare the repo's communication language and conduct in docs/standards so every command reads it for free
verification: per-section
priority: {level: 16, criticality: high, date: 2026-07-29}
refined: {mode: adversarial, date: 2026-07-30}
approved: {date: 2026-07-29}
branch: {base: main, work: plan/declare-repo-body-language}
reviewed: {date: 2026-07-30}
merge: {strategy: merge-commit, subject: "plan/declare-repo-body-language: merge (merge-commit)"}
outcome: done
---

# Declare the repo's communication language and conduct in docs/standards so every command reads it for free

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
pelas references entregues deferem sem que nenhuma delas a defina. Um repositório declara sua
language como uma tag BCP-47 em uma linha do seu harness **raiz** — em contexto no início da sessão,
e funcionando sem um `docs/` bundle — enquanto um doc de standards entregue **é o dono** da regra que
essas seis cláusulas passam a citar em vez de reenunciar.

**A regra governa toda prosa que o agente autora**, artefato e conversa: body de doc, body de spec,
`## Handoff` e `## Tasks`, resposta ao humano, pergunta de comando, relatório, commit. Duas
exclusões, e só duas — a estrutura canônica e a surface do plugin sob `commands/**` (cujos bodies
são inglês, mas cuja **saída** segue a tag).

O mesmo doc enuncia a etiqueta de comunicação: **uma variável declarada, um contrato constante.** A
linha do harness carrega só a tag, porque é isso que varia entre repositórios; a etiqueta é
enunciada como constante não configurável, citando `questions.md` §The four shared mechanics e
`docs/standards/automation/` em vez de reenunciá-los — o que a mantém fora da faixa que os vinte e
seis command bodies já ocupam.

O dono é `docs/standards/agents/communication.md` — um conceito, do qual a língua é o meio e a
etiqueta é a forma. Ele vai para um subject novo, `agents/` — *como instruímos agentes* —, que faz a
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

**A regra vale para toda prosa que o agente autora**, não só para o body de artefatos: um doc, um
body de spec, uma resposta ao humano, uma pergunta de comando, um relatório, uma mensagem de commit.
As seis cláusulas cobrem apenas o primeiro caso, e a lacuna que mais custa por dia é a última — um
agente que lê `pt-BR` no harness e ainda assim responde, pergunta e reporta em inglês. Duas
exclusões, e só duas: a estrutura canônica (nomes de pasta, slugs, chaves de frontmatter, valores de
`type`, os `##` headings parseados) e a surface do plugin sob `commands/**`.

Um repositório declara sua language em uma linha do seu arquivo de harness **raiz** (`CLAUDE.md` /
`AGENTS.md`): em contexto no início da sessão, custando zero tool calls, e funcionando em um
repositório que tem `specs/` e nenhum `docs/` bundle. **Somente o harness raiz carrega a
declaração.** Um arquivo de harness aninhado (`docs/standards/CLAUDE.md`) é carregado quando aquela
pasta é tocada, não no início da sessão, então não entregaria nada do custo zero pelo qual esta forma
foi escolhida.

**Uma variável declarada, um contrato constante.** A linha do harness declara **só** a tag BCP-47,
porque é isso que varia entre repositórios. O doc dono enuncia, além dela, a etiqueta de comunicação
— uma pergunta por vez, confirmação antes do irreversível, relato fiel do que aconteceu — e a enuncia
como **constante não configurável**: nenhum repositório a sobrescreve, e nenhuma segunda chave entra
na linha do harness. É o que mantém o mecanismo em uma linha e zero tool calls, e o que faz "uma
definição única" ser uma definição em vez de um arquivo de config.

A metade da etiqueta **cita, nunca reenuncia**. Os contratos por comando continuam nos vinte e seis
bodies sob `commands/**`, a mecânica de perguntas continua em
`assets/references/specs-develop/questions.md` §The four shared mechanics, e o subject
`docs/standards/automation/` continua dono de skills, hooks, agents e context budget. O doc possui o
que vale em **toda** tarefa, comando ou não — a faixa que nenhum deles ocupa.

O enunciado da regra ganha **um único dono** — `docs/standards/agents/communication.md`, entregue no
skeleton sob `assets/docs/`. As seis cláusulas deixam de reenunciar a regra e passam a citar esse
doc: o colapso que `docs/standards/architecture/plugin-layout.md` já defende, aplicado a uma regra
que havia sido escrita seis vezes.

`/docs:align` pergunta a language **uma vez**, quando um repositório adota o bundle, e escreve a
linha no harness raiz; `/docs:harness` a mantém dali em diante. **O silêncio conserva seu significado
atual** — um repositório que não declara nada não está sob restrição alguma, exatamente como as seis
cláusulas `MAY` são lidas hoje. Nada se torna retroativamente não conformante e nenhum repositório já
adotado precisa mudar.

Depois disso, um agente que precise saber em que língua escrever — e como se dirigir a quem está
digitando — lê essa informação de graça no início da sessão, em vez de adivinhar ou perguntar.
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
  `commands/**` são em inglês, qualquer que seja a language que um repositório-alvo declare. **A
  saída que esses bodies produzem não é a mesma coisa:** a pergunta que um comando faz e o relatório
  que ele imprime são prosa dirigida ao humano e seguem a tag declarada. O body em inglês, a saída na
  language — traduzir um body é o erro que esta linha existe para impedir.
- **Etiqueta configurável.** A metade da etiqueta é constante. Definir um conjunto de perfis de
  interação, permitir que um repositório sobrescreva cláusulas nomeadas, ou versionar esse conjunto
  está fora: é superfície de configuração, e o argumento de custo inteiro deste spec é uma linha com
  um valor.
- **Auditar os vinte e seis bodies contra a etiqueta.** O doc enuncia o contrato; conformar cada
  comando a ele é trabalho de `/skill:align`, que já lê todo body contra a doutrina de escrita — não
  uma task aqui.
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

- `docs/standards/agents/communication.md` — o dono único da regra, escrito duas vezes no mesmo
  caminho relativo ao bundle: uma vez no skeleton entregue sob
  `plugins/quenching/assets/docs/`, e uma vez no bundle deste próprio repositório, para que o repo
  que entrega a regra seja também seu primeiro consumidor
## Validation

- O invariante do colapso é um **par** de greps, não um só: os seis locais deixaram de conter a
  frase — é isso que colapsar significa — então procurá-la não os encontra mais.

  O **alarme de reenunciação nova** precisa casar a frase mesmo quebrada por wrap, e por isso
  ancora na continuação em vez de na linha inteira:

      grep -rn -B1 'repo.s language\|^ *language\*\*' docs/ plugins/quenching/assets/references/

  Ele retorna **exatamente dois**: a prosa do próprio dono
  (`docs/standards/agents/communication.md`, que é onde a regra vive) e a declaração autocontida
  deliberada de `okf-spec.md`. Um terceiro acerto dentro dessas duas árvores é reenunciação nova, e
  é falha.

  O **censo das citações** é o grep complementar,
  `grep -rn 'agents/communication.md' docs/ plugins/quenching/assets/references/`: os seis locais
  que citam o dono, mais a nota de ponteiro do próprio `okf-spec.md` e a linha derivada de
  `standards/index.md` — esta última listagem gerada, não citação.

  As reenunciações que vivem **fora** dessas duas árvores estão registradas em `## Open Decisions` e
  não pertencem a este invariante.
- A metade da etiqueta de `docs/standards/agents/communication.md` **cita**
  `plugins/quenching/assets/references/specs-develop/questions.md` §The four shared mechanics e os
  docs de `docs/standards/automation/`, e não reenuncia nenhum deles. Uma reenunciação aqui é o único
  modo de falha desta metade: ela transformaria o dono no sétimo enunciado concorrente da mesma
  regra, que é exatamente o defeito que este spec existe para curar.
- A linha do harness raiz carrega um valor e uma citação e **nenhuma paráfrase da regra** — o
  invariante que mantém este design compatível com `/docs:harness` §Move, never copy. A linha carrega
  **um** valor: a tag. Uma segunda chave de configuração nela é falha.
- `grep -n 'agents/' plugins/quenching/assets/references/docs-align/taxonomy.md` mostra o subject
  dentro de §The canonical tree (locked), e os dois arquivos `standards/index.md` carregam sua linha de
  subtopic. Um subject que existe em disco mas não na árvore travada é a não conformidade que este
  spec está corrigindo, não um estado que ele possa deixar para trás.
- `python3 plugins/quenching/assets/hooks/okf-validate.py assets/docs` reporta
  `0 error(s), 0 warning(s)` com o novo subject e o novo doc de standards no lugar. Sobre `docs/` o
  critério é **`0 error(s)` e nenhum finding novo**, comparado **doc-a-doc** contra a mesma execução
  em `main` e nunca por contagem: a baseline já carrega 13 warnings `stale-doc`/`resource-unresolved`
  alheios a este spec, e o número sobe sozinho conforme as datas de commit rolam sob os globs de
  `resource:` existentes. O spec irmão `narrow-the-stale-doc-trigger-to-content-drift` é quem cura
  esse ruído; silenciá-lo aqui com bump de `timestamp:` seria a mentira que ele existe para evitar.

## Design

**Regra e valor são dois fatos diferentes, cada um em um lugar só.** A linha do harness carrega o
**valor** e uma citação; o doc de standards carrega o **contrato** — o que declarar significa, o que o
silêncio significa. Nenhum dos dois parafraseia o outro. É isso que mantém o mecanismo do lado certo
de `/docs:harness` §Move, never copy: uma regra reenunciada em um arquivo de harness é exatamente o
drift que aquele comando existe para remover, enquanto um valor mais uma citação não é reenunciação.

**O valor é uma tag BCP-47** (`pt-BR`, `en`), não um nome de língua. Um nome convida `Português`,
`portugues` e `Portuguese` a significarem a mesma coisa, e nenhuma citação resolve isso; uma tag é uma
string com uma grafia só.

**A regra governa toda prosa autorada pelo agente** — artefato e conversa. Body de doc, body de spec,
`## Handoff` e `## Tasks`, resposta ao humano, pergunta de comando, relatório, mensagem de commit,
corpo de PR. As seções voltadas a agente continuam terse, porque são contexto de agente, mas terse na
language declarada. Isso é mais amplo que `docs/index.md`, que hoje limita a regra a material
`audience: human`, então aquela linha e sua gêmea no skeleton são reconciliadas como parte deste spec
(ver `## Impact`). O limite está em `## Out of Scope`: a estrutura canônica e a surface do plugin sob
`commands/**` — e a distinção que essa segunda exclusão obriga a escrever é entre o **body** de um
comando, que é inglês, e a **saída** que ele produz, que segue a tag.

### Uma variável declarada, um contrato constante

A linha do harness declara **uma** coisa: a tag. A etiqueta de comunicação vive no doc dono e é
**enunciada, não declarada** — constante, não configurável, idêntica em todo repositório.

O critério é qual dos dois fatos varia. A língua varia entre repositórios: é por isso que ela precisa
de um lugar por repositório para ser dita. A etiqueta não varia — "uma pergunta por vez",
"confirmação antes do irreversível", "relato fiel do que aconteceu" não são preferências locais, são
o contrato. Declarar o que não varia compra zero e custa uma superfície de configuração inteira: o
conjunto de perfis válidos, sua evolução, e o fim do argumento *uma linha, zero tool calls* que
escolheu esta forma. Um doc com uma variável e uma constante é uma definição única; dois valores
declarados são duas configurações compartilhando um arquivo.

Isso também é o que impede a metade da etiqueta de virar um enunciado concorrente. Ela **cita**: os
contratos por comando ficam nos vinte e seis bodies, a mecânica de perguntas fica em `questions.md`
§The four shared mechanics, e skills/hooks/agents/context-budget ficam em `docs/standards/automation/`.
O doc possui somente o que vale em **toda** tarefa, comando ou não — a faixa que nenhum deles ocupa —
e o segundo bullet de `## Validation` é o invariante que prova isso.

### O nome, e a regra "one standard per file"

**O dono é `docs/standards/agents/communication.md`.** `docs/standards/index.md` exige um standard por
arquivo, e um doc que enuncia língua *e* etiqueta parece dois. O nome é o que decide a leitura: o
conceito é **como o agente se comunica**, do qual a língua é o **meio** e a etiqueta é a **forma**.
Um artefato escrito é comunicação; uma resposta ao humano é comunicação. Um nome composto
(`language-and-conduct.md`) admitiria no próprio slug que são dois contratos empilhados, e não há
nenhum slug com `and` na árvore inteira.

O caminho é load-bearing: ele aparece em quatro das sete tasks, nos dois `index.md` de subject, nas
seis citações que a task 5 escreve e em dois bullets de `## Validation` — nove lugares. É por isso que
o nome foi decidido antes de qualquer task rodar, e não depois.

### O subject

O subject `agents/` é novo, e a árvore travada cresce em um para acomodá-lo. O subject é *como
instruímos agentes*: o que a surface always-on declara a quem a lê no início da sessão. Que a regra
cubra a conversa, e não só o body dos artefatos, **fortalece** essa escolha — "como instruímos
agentes" descreve mal "os docs são em pt-BR" e descreve bem "fale pt-BR com quem está digitando".

Duas casas de aparência mais próxima foram rejeitadas nos autos, em `## Alternatives Considered`; a
forma curta é que `naming/` governa nomes e esta regra não nomeia nada, e `automation/` colide
justamente nos repositórios mais propensos a adotar o bundle — um repo cujo próprio produto é
automação não consegue distinguir "how we drive Claude Code" de "our automation domain" sob uma única
pasta. `automation/` também não está no conjunto entregue: é o subject local deste repositório, o que
é precisamente a ambiguidade que se está evitando.

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
| **Escopo só body de artefato** — a regra governa docs e specs, e a conversa fica de fora | A forma original, e rejeitada porque não é mais simples: é a mesma máquina — subject novo, dono, seis colapsos, dois comandos — entregando menos. A lacuna que mais custa por dia não é o body; é um agente que lê `pt-BR` no harness e responde, pergunta e reporta em inglês. E `## Out of Scope` não excluía isso, o que faz dela buraco e não fronteira. Deixar para um spec de follow-up reabriria exatamente estes mesmos seis arquivos. |
| **Etiqueta declarada por repositório** — um perfil de interação na linha do harness, ao lado da tag | O mecanismo carrega uma tag BCP-47; uma tag carrega língua, não "pergunte antes do irreversível". Declarar a etiqueta obriga a definir o conjunto de perfis válidos e sua evolução, e transforma *uma linha, zero tool calls* em um arquivo de config — o argumento de custo que escolheu esta forma. O que varia entre repositórios é a língua; a etiqueta não varia. O ponytail (`DietrichGebert/ponytail`) apoia isso pelo negativo: o ruleset dele é constante e não configurável, e é justamente por isso que consegue ser espelhado em quatro plataformas sem carregar config nenhuma. |
| **Dois docs** — `agents/language.md` mais `agents/interaction.md`, lendo o mesmo valor declarado | Respeita "one standard per file" ao preço de desfazer o que este spec entrega: uma definição única. Duas casas para o meio e a forma do mesmo ato obrigam cada consumidor a saber que existem duas, e a fronteira entre elas passa a precisar de manutenção própria. O nome `communication.md` resolve a mesma tensão sem o segundo arquivo. |
| **Manter o nome `body-language.md`** | Zero churn nas nove referências ao caminho, ao custo de um nome que descreve um terço do conteúdo. Um doc cuja etiqueta o nome não anuncia ganha uma seção que ninguém encontra — e corrigir o nome depois custa uma migração de citações em um plugin já lançado, o mesmo modo de falha que `## Risks` registra sobre ordem de tasks. |
| **Medir a metade da etiqueta com `/skill:eval`** | O único instrumento de medição do repo mede um **comando**, com braço com/sem; não existe braço "sem" para um doc de standards lido passivamente. E `CLAUDE.md` registra que cada check funcional é uma sessão de agente cobrada e que todo red run que esse harness já produziu se rastreou a um defeito do próprio harness. Substituído pelo segundo bullet de `## Validation`, que é grepável e mira o único modo de falha que esta metade tem. |
| **O dono sob `naming/`** — onde a cláusula sendo vinculada já vive | Vizinhança, não pertencimento. `docs/standards/naming/index.md` limita o subject a "the globally unique, predictable **names** this repo commits to", e a gêmea do skeleton o limita à nomenclatura de **dados** sem rodeios — `tables · columns · descriptions · schemas-catalogs`. Em que língua natural a prosa está escrita não nomeia nada. Colocá-lo ali significava esticar um subject declarado de dentro de uma task. |
| **O dono sob `automation/`** | A pasta existente que melhor se encaixa — o carregador é o harness always-on e `automation/context-budget.md` já governa esse budget — e rejeitada de todo modo, porque colide exatamente nos repositórios que adotam este bundle: um cujo produto *é* automação não consegue distinguir "how we drive Claude Code" de "our automation domain" sob uma única pasta. Também não está nos nove entregues; é o subject local deste repo, que é a mesma ambiguidade um nível abaixo. |
| **Uma chave em `docs/index.md`**, ao lado de `okf_version` | Ser legível por máquina não compra nada aqui: `docs-align/conformance.md` registra que nenhum validador jamais vai ramificar sobre esse valor, então o único consumidor é o agente — que lê o harness de graça. Também custa uma edição em `okf-spec.md`, cuja linha 92 fixa aquela listagem apenas a `okf_version`, colidindo com o spec enfileirado `upgrade-okf-to-v0-2`. E exclui um repositório com `specs/` e sem bundle. |
| **Um hook `SessionStart` injetando o valor** | Um processo por sessão, para sempre, para entregar uma constante que o harness auto-carregado já entrega de graça. `docs/standards/automation/hooks.md` exige que um hook justifique seu escopo; este não consegue. |
| **Só o doc de standards, sem carregador** | Dá à regra uma casa, uma autoridade e um mantenedor, mas nada faz um agente lê-la — descoberta é exatamente o custo que `## Problem` diz que precisa ficar perto de zero. |
| **Não fazer nada** | As seis cláusulas dizem `MAY`, então um repositório escrevendo português já é conformante sem declarar nada. Rejeitado porque a lacuna não é conformidade: é que um agente não tem como *saber*, e é isso que o faz adivinhar. |
| **`agents/` só neste repositório, criado sob demanda pelo `/docs:align` no alvo** — em vez de fazer o skeleton entregue crescer | Perdeu por transformar um risco limitado em universal. As quatro citações em `assets/references/**` são relativas ao bundle, então um subject criado sob demanda faz o risco "a citação não resolve" valer para todo bundle que ainda não rodou o align, e não apenas para um repositório `specs/`-only. Um subject que existe na árvore travada e não no skeleton entregue é também exatamente a divergência que o quarto bullet de `## Validation` foi escrito para impedir. |
## Open Decisions

- **`AGENTS.md` é um carregador em pé de igualdade com `CLAUDE.md`?** Este spec assume que sim,
  porque o plugin já trata o par como um só em nove pontos e `/docs:harness` varre os dois. **Como
  será decidido:** pelo spec irmão `decide-agents-md-harness-default`, não por este. Se ele tornar
  `AGENTS.md` o alvo padrão, o que muda é a redação do doc dono, não este mecanismo — razão pela qual
  este spec não espera por ele. Evidência externa levantada nesta passagem e que pertence àquele
  spec: `DietrichGebert/ponytail` espelha o mesmo ruleset em `.claude-plugin/`, `.cursor/rules/`,
  `.windsurf/rules/` e `.agents/`, com `AGENTS.md` como o portátil e os demais como espelhos.
- **As outras dez reenunciações da mesma cláusula `MAY`, fora das duas árvores que este spec varre,
  também colapsam?** O censo completo, levantado na primeira passagem adversarial:
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
- **Quando o doc dono sai de `authority: background` para `current`?** As duas metades promovem por
  critérios diferentes, e é preciso dizer os dois — um critério só deixaria uma delas em `background`
  para sempre.
  - **A metade da língua** promove pelo primeiro comando que efetivamente ramifique sobre o valor
    declarado. Hoje nenhum ramifica: `/docs:align` e `/docs:harness` apenas escrevem e preservam a
    linha.
  - **A metade da etiqueta** não pode usar esse critério, porque é uma constante e nada jamais vai
    ramificar sobre ela. Ela promove quando uma passagem do `/skill:align` — que já lê todo body
    contra a doutrina de escrita — puder citá-la como a regra que está aplicando. É evidência de uso
    real, não custa sessão de medição alguma, e usa um comando que já existe.

  Em ambos os casos a promoção é uma edição de uma linha em `authority:`. Este spec não a agenda, e a
  decisão não bloqueia nenhuma das sete tasks.
## Risks

- **A metade da etiqueta vira o sétimo enunciado concorrente da mesma regra.** O doc passa a falar de
  como o agente conversa, e três donos já falam disso por outros ângulos: os vinte e seis command
  bodies (o contrato de cada comando), `questions.md` §The four shared mechanics (a mecânica de
  perguntas) e `docs/standards/automation/` (skills, hooks, agents, context budget). Um doc que
  reenunciasse qualquer um deles cometeria uma camada acima o defeito que este spec existe para
  curar. **Mitigação nomeada:** o segundo bullet de `## Validation` — a metade da etiqueta cita e não
  reenuncia — e a fronteira escrita em `## Design`: o doc possui só o que vale em toda tarefa,
  comando ou não.
- **O caminho do dono aparece em nove lugares.** Quatro das sete tasks, os dois `index.md` de
  subject, as seis citações da task 5 e dois bullets de `## Validation`. Errar o nome é errar em nove
  lugares de uma vez, e corrigir depois é uma migração de citações em um plugin já lançado.
  **Mitigado por decisão, não por task:** o nome foi resolvido nesta passagem, antes de qualquer task
  rodar; nenhuma task escreve `body-language.md` em lugar algum.
- **Este spec faz a árvore travada crescer, e `revise-standards-subject-folders` também pretende
  revisá-la.** Dois specs editando o mesmo conjunto declarado de subjects podem cada um entregar
  metade dele. **Accepted, with the boundary stated:** este spec adiciona exatamente um subject e não
  toca em nenhum outro, e o spec irmão continua livre para revisar o conjunto como um todo depois —
  inclusive renomeando o que este adicionou. O que este spec não pode fazer é antecipar aquela
  revisão reorganizando subjects de que não precisa. Se o irmão entrar primeiro, a task 1 encolhe para
  uma linha em qualquer conjunto que ele tenha produzido.
- **A citação não resolve em um repositório que nunca adota o bundle.** Um repositório `specs/`-only
  lê uma reference citando `docs/standards/agents/communication.md`, que ele não tem. **Accepted
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
- **Nada mede o efeito da metade da etiqueta.** O spec passa a alegar um efeito sobre comportamento —
  que o agente pergunte antes do irreversível, que reporte o que de fato aconteceu — e `## Validation`
  é estrutural de ponta a ponta. **Accepted risk, com a razão registrada:** o único instrumento do
  repo, `/skill:eval`, mede um comando com braço com/sem, e não existe braço "sem" para um doc lido
  passivamente; `CLAUDE.md` registra que cada check funcional é uma sessão cobrada e que todo red run
  que aquele harness já produziu se rastreou a um defeito do próprio harness. O que se compra em
  lugar da medição é o segundo bullet de `## Validation` mais o critério de promoção da etiqueta em
  `## Open Decisions`.
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

**As sete tasks estão commitadas, nenhuma bloqueada.** O que resta é `/specs:conclude`: revisar a
branch inteira, escrever o `docs/` que o trabalho revelou, resolver as quatro linhas de
`## Discoveries`, arquivar e mergear. Duas delas pedem correção de redação **no próprio spec** antes
do arquivamento — o primeiro e o quinto bullet de `## Validation`, cujos greps não medem o que
afirmam medir.

**Este repositório declara `pt-BR`** (task 3, escolhido pelo humano). A partir daí a prosa autorada
pelo agente aqui segue a tag — body de doc e de spec, mensagem de commit, e também resposta,
pergunta e relatório. Os docs em inglês já escritos ficam como estão: traduzi-los é `## Out of Scope`.

Estado que um executor novo não consegue derivar:

- **O slug deste spec precede a decisão do nome.** Ele diz `declare-repo-body-language` porque um
  slug de spec é congelado; o dono se chama `docs/standards/agents/communication.md`. Não procure
  `body-language` no disco e conclua que a task 2 não foi feita — esse arquivo nunca é escrito.
- O subject `agents/` existe nas duas árvores (task 1) e **o dono já aterrou nas duas** (tasks 2 e
  3), com o ledger de coverage de cada `agents/index.md` preenchido e a zona `GENERATED` dos dois
  `standards/index.md` regenerada com o grupo `### agents/`.
- **As duas cópias do dono não são byte-idênticas, e isso é intencional.** A do skeleton fala de "a
  plugin's own command surface" e cita a árvore de standards genericamente; a deste repo cita
  `../naming/command-surface.md`, `../automation/index.md` e `plugins/quenching/commands/**` por
  caminho real. Ao editar uma, decida conscientemente se a outra acompanha.
- **O `verify:` das tasks 1–3 pede `0 error(s), 0 warning(s)` nas duas árvores, e sobre `docs/` isso
  é inalcançável e não por culpa deste spec:** `main` já trazia 13 warnings `stale-doc` /
  `resource-unresolved` alheios a ele. O critério aplicado foi **`0 error(s)` e nenhum finding
  novo**; meça contra a baseline, não contra zero. `assets/docs` fica em `0 error(s), 0 warning(s)`
  literais. Desde a task 1 são **14**: escrever sob `plugins/quenching/assets/**` fez
  `architecture/plugin-layout.md` acusar `stale-doc` sem que seu contrato mudasse (ver
  `## Discoveries`) — não silencie com bump de timestamp.
- Não funda `docs/standards/automation/agents.md` dentro do subject novo. Ele é o contrato de
  definição de `.claude/agents/`, fica onde está, e movê-lo pertence a
  `revise-standards-subject-folders`.
- Os seis locais ainda reenunciam a regra literalmente. `okf-spec.md` é o que conserva sua declaração
  — não o colapse.
- `docs/index.md` e `plugins/quenching/assets/docs/index.md` ainda limitam a regra a
  `audience: human`; a task 4 as amplia para toda prosa autorada pelo agente. Lê-los antes da task 4
  dá a redação de antes da decisão.
- **Nada valida a zona `GENERATED` dos `standards/index.md`:** `okf-validate.py` não conhece o
  conjunto de subjects e checa apenas `dir-no-index`, links de listagem quebrados e docs órfãos. Se
  uma task futura acrescentar um doc de standards, regenere a zona dentro da própria task — o
  `verify:` não vai reclamar. As tasks 2 e 3 tocaram o `standards/index.md` de sua árvore por essa
  razão, embora ele não conste do `files:` declarado de nenhuma das duas.
- A isolação está tomada: `plan/declare-repo-body-language`, cortada de `main`, no worktree
  `.claude/worktrees/declare-repo-body-language-a66245`. O registro `branch` está estampado.
- `verification: per-section` — verifique no limite de cada task, conforme o `verify:` daquela task.
## Tasks

Ordenadas, e a ordem é load-bearing duas vezes: a task 1 abre o subject antes de qualquer coisa ser
escrita nele, e a task 2 entrega o dono antes de a task 5 fazer qualquer local citá-lo — ou um plugin
lançado carrega uma citação pendurada. Cada task nomeia o caminho `docs/standards/**` que declara na
própria linha do checkbox, porque `sp-impact-uncovered` casa com aquela linha e não com a continuação
`files:`.

- [x] 1 Abrir o subject `agents/` nas duas árvores — pasta + `index.md` no skeleton e neste
  repositório, o subject adicionado a `taxonomy.md` §The canonical tree (locked), e uma linha de
  subtopic nos dois `standards/index.md`. O limite do subject: como instruímos agentes — o que a
  surface always-on declara. Distinto de `automation/` (o subject local deste repo para a própria
  command surface).
  files: `plugins/quenching/assets/references/docs-align/taxonomy.md`, `plugins/quenching/assets/docs/standards/index.md`, `plugins/quenching/assets/docs/standards/agents/index.md`, `docs/standards/index.md`, `docs/standards/agents/index.md`
  verify: `python3 plugins/quenching/assets/hooks/okf-validate.py assets/docs` and `... docs` both report `0 error(s), 0 warning(s)`
  subject: plan/declare-repo-body-language: 1 Abrir o subject agents/ nas duas árvores
- [x] 2 Entregar o dono no skeleton em `docs/standards/agents/communication.md` sob `assets/docs/`
  Duas metades. **A língua:** o que declarar significa, que somente o harness **raiz** carrega a
  declaração, que o valor é uma tag BCP-47, que ela governa toda prosa autorada pelo agente
  (artefato e conversa) com as duas exclusões de `## Out of Scope`, e que o silêncio significa
  nenhuma restrição. **A etiqueta:** o contrato de comunicação, enunciado como constante não
  configurável, escrito citando `questions.md` §The four shared mechanics e `docs/standards/automation/`
  em vez de reenunciá-los. Frontmatter OKF completo; `authority: background` até a regra ser provada
  pelo uso.
  files: `plugins/quenching/assets/docs/standards/agents/communication.md`, `plugins/quenching/assets/docs/standards/agents/index.md`
  verify: `python3 plugins/quenching/assets/hooks/okf-validate.py assets/docs` → `0 error(s), 0 warning(s)`, and the `## Validation` citation grep shows the etiquette half citing and not restating
  subject: plan/declare-repo-body-language: 2 Entregar o dono no skeleton
- [x] 3 Instalar o mesmo dono em `docs/standards/agents/communication.md` no bundle deste repo, e
  declarar a language deste próprio repositório no harness raiz — o dogfood que o spec alega. A
  linha carrega a tag e uma citação, e nada mais.
  files: `docs/standards/agents/communication.md`, `docs/standards/agents/index.md`, `CLAUDE.md`
  verify: `python3 plugins/quenching/assets/hooks/okf-validate.py docs` → `0 error(s), 0 warning(s)`
  subject: plan/declare-repo-body-language: 3 Instalar o dono neste repo e declarar pt-BR
- [x] 4 Reconciliar as duas linhas de index que limitam a regra a `audience: human` com a decisão
  deste spec de que ela governa toda prosa autorada pelo agente.
  files: `docs/index.md`, `plugins/quenching/assets/docs/index.md`
  verify: `grep -n 'audience: human' docs/index.md plugins/quenching/assets/docs/index.md` shows no
  subject: plan/declare-repo-body-language: 4 Reconciliar as duas linhas de index
  language clause narrowed by audience
- [x] 5 Colapsar os seis locais que reenunciam a regra para que citem o dono; `okf-spec.md` conserva
  sua declaração autocontida com a razão registrada inline.
  files: `docs/standards/naming/command-surface.md`, `docs/standards/workflows/plan-artifacts.md`, `plugins/quenching/assets/references/specs-develop/spec-driven.md`, `plugins/quenching/assets/references/docs-align/taxonomy.md`, `plugins/quenching/assets/references/docs-align/migration.md`, `plugins/quenching/assets/references/docs-align/okf-spec.md`
  verify: the `## Validation` grep returns five citing sites and no restatement
  subject: plan/declare-repo-body-language: 5 Colapsar os seis locais para citarem o dono
- [x] 6 Ensinar `/docs:align` a perguntar a language uma vez na adoção e escrever a linha no
  arquivo de harness raiz — a tag e uma citação, nunca uma segunda chave de configuração.
  files: `plugins/quenching/commands/docs/align.md`
  verify: `grep -n 'communication' plugins/quenching/commands/docs/align.md`
  subject: plan/declare-repo-body-language: 6 Ensinar /docs:align a perguntar a language
- [x] 7 Ensinar `/docs:harness` que a linha da declaração é um KEEP e nunca deve parafrasear a
  regra — o invariante que `## Validation` afirma.
  files: `plugins/quenching/commands/docs/harness.md`
  verify: `grep -n 'communication' plugins/quenching/commands/docs/harness.md`
  subject: plan/declare-repo-body-language: 7 Ensinar /docs:harness que a linha e KEEP

## Discoveries

- O verify: das tasks 1-3 e o quinto bullet de ## Validation exigem 0 warning(s) do okf-validate.py sobre docs/, mas a baseline ja carrega 13 warnings stale-doc/resource-unresolved pre-existentes e alheios a este spec (identicos antes e depois da task 1). O criterio efetivo aplicado e: 0 error(s) e nenhum finding NOVO. O spec irmao narrow-the-stale-doc-trigger-to-content-drift e quem cura o ruido.
- As tasks 1-2 fizeram docs/standards/architecture/plugin-layout.md acusar stale-doc: o resource dele cobre plugins/quenching/assets/**, e este spec escreve ali. O contrato do doc nao mudou - so o glob foi tocado. Nao foi silenciado com bump de timestamp; e o mesmo gatilho que narrow-the-stale-doc-trigger-to-content-drift existe para estreitar. Baseline docs/: 13 warnings em main, 14 a partir da task 1.
- O primeiro bullet de ## Validation espera que o grep 'the repo.s language' retorne cinco locais citando o dono. Depois da task 5 ele retorna ZERO: os cinco colapsados deixaram de conter a frase, e a unica ocorrencia viva - a declaracao autocontida de okf-spec.md - esta quebrada por wrap e escapa ao padrao de uma linha. O invariante util virou um par: grep da frase = alarme de reenunciacao NOVA (deve dar so okf-spec, via -A1); grep de 'agents/communication.md' = as cinco citacoes. Vale corrigir a redacao do bullet no conclude.
- Uma decima-primeira reenunciacao, fora do censo de ## Open Decisions: plugins/quenching/commands/docs/harness.md passo 7 diz 'Structure and links are canonical English; prose may follow the repo's language'. Nao foi colapsada - e body de comando, a mesma categoria que o censo deixou para um spec de follow-up. Some-a ao censo quando aquele spec for escrito.

## Outcome

**Entregue como `done`, merjado em `main` por merge commit** — os sete commits por task ficam na
base, e todo `subject:` registrado em `## Tasks` resolve a partir dela sem que a branch precise
sobreviver.

**O que entrou.** O subject `standards/agents/` passou a existir nas duas árvores — o bundle deste
repo e o skeleton entregue em `plugins/quenching/assets/docs/` — cada uma com seu `index.md` e com
o dono único `communication.md`. O doc tem duas metades: a **língua**, que cada repo declara por uma
tag BCP-47 em uma linha do harness raiz, e a **conduta**, que é constante e nenhum repo sobrescreve.
Este repo virou o primeiro consumidor da regra que entrega: `CLAUDE.md` declara `pt-BR`. Os seis
locais que reenunciavam a regra passaram a citá-la; `okf-spec.md` manteve a sua deliberadamente
autocontida, com a nota que explica o porquê — um format spec que defere a um doc de dentro do
bundle de um repo específico deixa de ser autodescritivo. `/docs:align` ganhou a pergunta única na
adoção, e `/docs:harness` ganhou a regra de que a linha é **KEEP** — a única coisa entre ela e uma
deleção silenciosa, já que arquivos de harness são isentos das checagens do bundle.

**O que ficou de fora, e onde está registrado.** O censo de `## Open Decisions` deixou para um spec
de follow-up as reenunciações que vivem **fora** de `docs/` e `assets/references/`; a
`## Discoveries` acrescentou a décima-primeira, em `commands/docs/harness.md` passo 7. Declarar uma
tag **não** retraduz o que já está escrito — isso é migração, e é outro trabalho. E nada
máquina-checa nada disto, por construção: um validador não identifica a língua de um documento.

**Dois achados da revisão de branch entraram antes do merge.** Os bullets 1 e 5 de `## Validation`
não eram executáveis como escritos — o primeiro procurava a frase que os seis locais deixaram de
conter, o segundo exigia `0 warning(s)` sobre `docs/`, que nunca foi atingível — e foram corrigidos
para os critérios realmente aplicáveis. A citação por `${CLAUDE_PLUGIN_ROOT}` na tabela de conduta
foi corrigida nas duas cópias, cada uma na forma certa para seu contexto. O que esse segundo achado
revelou virou a única doc emergente deste conclude: a emenda a
`docs/standards/architecture/plugin-layout.md` §*A mold cites nothing it does not also install*,
cujo escopo nomeava só `assets/templates/**` quando o raciocínio cobre toda árvore que um align
copia para um repo alvo.

**O que o próximo leitor precisa saber.** O ruído de `stale-doc` em `docs/` **não** é deste spec: a
baseline em `main` já carregava 13, e o critério aplicado durante toda a execução foi `0 error(s)` e
nenhum finding novo, comparado doc-a-doc e nunca por contagem. `narrow-the-stale-doc-trigger-to-content-drift`
é quem cura esse ruído. Pela mesma razão ficou como está o `resource: docs/**, specs/**` de
`communication.md`, hoje o único resource do bundle que aponta para as árvores de conteúdo do repo
em vez de para `plugins/quenching/**`: ele vai acusar `stale-doc` no primeiro commit sob `docs/` ou
`specs/` depois deste merge, e isso é esperado.
