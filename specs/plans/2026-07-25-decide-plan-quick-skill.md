---
slug: decide-plan-quick-skill
title: Decide whether quenching-specs-plan-quick is still needed
verification: per-section
refined: {mode: gate, date: 2026-07-30}
---

# Decide whether quenching-specs-plan-quick is still needed

## Overview

Este spec é uma **decisão**, não uma construção. Ele herdou uma pergunta em aberto do plano
`refine-and-execute-specs-flow`: a express lane `quenching-specs-plan-quick` — um único ponto de
entrada que levaria um spec de propose a archive sob uma só confirmação — deveria finalmente existir?

`## Problem` reproduz a pergunta como ela foi registrada em 2026-07-25, com a data de revisão que ela
mesma marcou. `## Design` mostra, com os comandos que qualquer pessoa pode rodar, por que essa data
não chega em termos úteis: o artefato que a pergunta nomeia não existe mais em nenhuma forma, o
caminho encadeado sobre o qual ela pedia evidência foi reconstruído no meio do próprio prazo, e a
promessa de "uma confirmação até archive" colide com um contrato que já está em vigor.
`## Proposal` é o resultado dessa leitura — nenhum comando novo, nenhum arquivo de código alterado —
e `## Alternatives Considered` guarda as três formas que perderam, para quem tiver a mesma ideia
outra vez.

`## Impact`, `## Validation`, `## Tasks` e `## Handoff` existem para uma coisa só: tornar o "nada a
construir" **verificável em vez de declarado**. `## Validation` traz os quatro comandos que sustentam
a decisão e manda rodá-los de novo no fechamento; `## Tasks` é um explicit none, e é por isso que
`specs.py next` roteia este spec para `promote`, não para `implement_task`; `## Handoff` fala com quem
fecha, não com quem executa.

O que **não** se resolve aqui está separado de propósito: `## Out of Scope` nomeia os specs irmãos que
ficam com o atrito, `## Open Decisions` mantém aberta a única pergunta de mérito que sobrevive, e
`## Risks` trata o modo de falha mais provável deste spec, que é a pergunta desaparecer junto com ele
ao ir para `archive/`.
## Problem

Decisão em aberto vinda do plano `refine-and-execute-specs-flow` — reavaliar a express lane depois de duas semanas usando o caminho encadeado

_(tarefa de backlog v1 — tags: ['specs', 'skills', 'taxonomy'])_

Uma skill de express lane rodando propose → branch → apply → archive sob uma única confirmação foi
rejeitada **por ora** em favor do encadeamento (`from-claude` oferece encadear em apply, `apply`
oferece encadear em archive aos 100%), porque o encadeamento entrega o mesmo caminho sem uma 29ª
description always-on. O design do plano diz que a decisão se resolve "usando o caminho encadeado em
trabalho pequeno real por duas semanas, não por argumento" — portanto revisitar por volta de
2026-08-08. Se o atrito sobreviver, a skill volta para a mesa; se não sobreviver, fechar isto e
registrar a resposta.
## Proposal

- Fica registrado que **nenhum ponto de entrada express existe** na superfície colapsada e que
  **nenhum será criado por este spec**. Um revisor confere isso com os três comandos de
  `## Validation`.
- Fica registrado **por que** a pergunta original não pode mais ser respondida nos termos em que foi
  escrita: a classe de artefato que ela nomeia (`skill`) foi retirada, e os quatro passos que a
  express lane encadearia deixaram de existir com aqueles nomes.
- Fica registrado que, se a express lane voltar algum dia, ela só pode voltar como **run mode dos
  comandos de ciclo que já existem**, nunca como um 27º comando. Isso não é preferência deste spec:
  é a regra que `docs/standards/automation/skills.md:41` §*A technique is a parameter of a verb, not
  a new axis* já vincula, reforçada pelo ceiling sem folga de
  `docs/standards/automation/context-budget.md:96`.
- O atrito residual — se o ciclo `create → develop → execute → conclude` precisa de fato de um modo
  de uma confirmação — passa a ter **um dono nomeado** (`add-specs-cycle-run-modes`) em vez de ficar
  pendurado num spec cujo title nomeia algo inexistente.
- `plans/` perde uma pergunta obsoleta: este spec sai de `plans/` por
  `/specs:conclude --outcome abandoned`, com a decisão e a evidência dela em `## Outcome`.
- **Nenhum arquivo de `plugins/`, `docs/` ou `.claude/` é alterado por este spec.** O entregável é a
  decisão registrada, não código.

## Out of Scope

- **Projetar ou adicionar um run mode aos comandos de ciclo.** É o atrito que sobra, e ele tem dono:
  o spec irmão `add-specs-cycle-run-modes`. Este spec entrega apenas a leitura de que o formato certo
  é um mode; escolher a flag, a semântica e o custo é do irmão.
- **Reduzir o que `/specs:execute` e `/specs:conclude` custam por run** — outro irmão,
  `reduce-execute-conclude-cost`. É a leitura mais fácil de confundir com "express lane", porque as
  duas prometem menos cerimônia. A diferença é que uma mexe em *quantas confirmações* o ciclo pede e
  a outra em *quanto cada comando gasta*.
- **Limpar o vocabulário `quenching-specs-*` e `skill` que sobrou nos bodies e no `docs/`** — inclui
  a citação obsoleta `/specs:refine --mode` em `docs/standards/automation/skills.md:45`, que nomeia um
  comando que não existe mais (hoje é `/specs:develop`, com bank derivado e sem flag de mode). Isso é
  `retire-skill-vocabulary`. Este spec também **não** renomeia o próprio `slug` nem o próprio
  `title`, que carregam esse mesmo vocabulário: a identidade que `specs.py` resolve é o slug, e
  trocá-lo no meio da vida do spec quebra toda referência a ele.
- **Mexer na única oferta de encadeamento que sobreviveu** —
  `plugins/quenching/commands/specs/execute.md:190`, mais o ramo de branch já 100% em `:94`, ambos
  oferecendo `/specs:conclude`. Ela funciona, ninguém reclamou dela, e alargá-la aqui seria construir
  a express lane por outro nome.
- **Reabrir a decisão do ceiling de always-on context.** `skills.py budget` já reporta hoje
  `total: 12875` contra `ceiling: 12726` com `ok: false`. Este spec *usa* esse fato como evidência;
  consertá-lo é do ratchet descrito em `docs/standards/automation/context-budget.md`.
- **Decidir se o atrito do ciclo é real.** Isso é uma pergunta empírica cuja janela de evidência não
  fechou, e ela está em `## Open Decisions` com o dono que a decide — não respondida aqui.

## Impact

Escopo declarado: **nenhum arquivo do produto**. O único arquivo que este spec altera é ele mesmo,
`specs/plans/2026-07-25-decide-plan-quick-skill.md`, e o fechamento o move para `specs/archive/` por
`specs.py promote` (um `git mv`, sem renomear).

### Standards this spec will write into docs/standards/

- none — a regra que este spec aplicaria já está escrita e vinculante em
  `docs/standards/automation/skills.md` §*A technique is a parameter of a verb, not a new axis*, e em
  `docs/standards/automation/context-budget.md` §The per-surface ceiling. Escrever uma segunda cópia
  seria dar um segundo nome ao mesmo contrato, que é exatamente a falha que
  `docs/standards/naming/` proíbe. O raciocínio específico deste caso é *aplicação* das duas regras,
  não uma regra nova, e o lugar dele é o `## Outcome` deste spec.

### Standards em `authority: background` que este spec pode resolver

- none — este spec não constrói nada, então não prova nem promove nenhum standard.

### Código de produto que este spec espera tocar

- none — nada em `plugins/`, nada em `.claude/`, nada em `docs/`. Em particular, a oferta de
  encadeamento sobrevivente em `plugins/quenching/commands/specs/execute.md` fica intocada.

## Validation

Não há código para testar; o que precisa ser confirmado são as **quatro afirmações factuais** em que a
decisão se apoia. Todas as quatro são um comando, e todas devem ser **rodadas de novo** no
fechamento — nenhum número transcrito aqui vale como prova.

1. **Nenhum ponto de entrada express existe, sob nenhum nome.** Da raiz do repositório:

   ```bash
   grep -rni --include='*.md' --include='*.py' --include='*.sh' \
     'plan-quick|express lane|express-lane' . \
     | grep -v '2026-07-25-decide-plan-quick-skill'
   ```

   Deve imprimir **zero linhas**. Qualquer linha fora deste arquivo de spec invalida `## Proposal` e
   reabre a pergunta.

2. **A superfície colapsada continua sem uma express lane.**

   ```bash
   python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json
   ```

   Em 2026-07-30 devolvia `"commands": 26` e `"findings": []`. O que importa não é o número, é que
   `find plugins/quenching/commands -name '*.md'` continue mostrando os nove comandos do front
   `specs/` (`align`, `conclude`, `continue`, `create`, `develop`, `execute`, `isolate`, `status`,
   `triage`) e nenhum décimo que leve um spec de ponta a ponta.

3. **O argumento de custo continua válido.**

   ```bash
   python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching budget --json
   ```

   Em 2026-07-30: `"total": 12875`, `"ceiling": 12726`, `"ok": false`. Se um dia devolver `ok: true`
   com folga larga, o argumento de custo enfraquece — e aí a decisão volta a ser inteiramente a de
   `add-specs-cycle-run-modes`, pelos motivos de contrato, não pelos de orçamento.

4. **O spec roteia para fechamento, não para execução.**

   ```bash
   python3 plugins/quenching/assets/bin/specs.py next --spec decide-plan-quick-skill --json
   python3 plugins/quenching/assets/bin/specs.py validate --spec decide-plan-quick-skill
   ```

   `next` deve reportar `"action": "promote"` — a prova mecânica de que o explicit none em
   `## Tasks` é a resposta e não uma lacuna. `validate` deve sair com 0.

**Invariante que precisa continuar valendo:** `git diff --stat` para o trabalho deste spec mostra
**apenas** `specs/plans/2026-07-25-decide-plan-quick-skill.md`. Qualquer outro arquivo no diff
significa que alguém começou a construir a express lane em vez de decidir sobre ela.

## Design

### O ponto de entrada nomeado não existe, e a ausência é verificável

`quenching-specs-plan-quick` é vocabulário v2: nomeia uma *skill* de nome achatado, classe de
artefato que `2026-07-26-collapse-skills-into-commands` retirou ao colapsar cada par
skill+wrapper em um arquivo por ponto de entrada. Na superfície de hoje:

- `python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json` reporta
  `"commands": 26` e `"findings": []`;
- os nove comandos do front `specs/` são `align`, `conclude`, `continue`, `create`, `develop`,
  `execute`, `isolate`, `status` e `triage`. Nenhum deles é uma express lane, e nenhum aceita flag
  que faça um deles virar uma;
- um grep no repositório inteiro por `plan-quick`, `express lane` e `express-lane` não retorna
  **nenhuma** ocorrência fora deste próprio arquivo de spec.

**Regra durável:** um spec cujo title nomeia um artefato de vocabulário retirado não se resolve
traduzindo o nome para o vocabulário novo. Primeiro se verifica se a *capacidade* que ele nomeava foi
absorvida — e a resposta reescreve a pergunta em vez de respondê-la.

### O caminho sobre o qual a pergunta pedia evidência foi reconstruído no meio do prazo

O `## Problem` marcou 2026-08-08 para decidir "usando o caminho encadeado por duas semanas". Dois
specs arquivados caíram dentro dessa janela e refizeram o caminho:

- `2026-07-26-collapse-skills-into-commands` — apagou a metade wrapper de cada par e levou a
  metadata always-on de 30.705 para 2.069 caracteres;
- `2026-07-27-specs-flow-consolidation` — dobrou `backlog/` + `ready/` em `plans/` e trocou os quatro
  passos encadeados por `create → develop → execute → conclude`, com `/specs:continue` como roteador
  do front inteiro em uma chamada de ferramenta.

Das duas ofertas de encadeamento em que a decisão original se apoiou, **sobrou uma**:
`plugins/quenching/commands/specs/execute.md:190` oferece encadear em `/specs:conclude` aos 100%, e
`:94` faz o mesmo quando toda task já está `- [x]`. As outras duas viraram *comando nomeado no
relatório*, não oferta encadeada: `commands/specs/create.md:162` nomeia `/specs:develop` como próximo
passo, e `commands/specs/develop.md:149` nomeia `/specs:execute`. Isolamento é explicitamente
"forwarded, never offered" (`commands/specs/create.md:165-169`).

**Portanto a data de revisão não decide nada.** Duas semanas de evidência sobre um caminho que foi
substituído no quinto dia não respondem a pergunta como ela foi escrita. Esperar até 2026-08-08 não
produziria a evidência pedida — produziria evidência sobre um caminho diferente, que é exatamente a
pergunta que o irmão `add-specs-cycle-run-modes` existe para fazer.

### O que `/align` já entrega, e o que ele deliberadamente não entrega

A objeção mais forte contra este spec é que a capacidade *já foi entregue* e a leitura de "não
existe" é enganosa: `/align` roda vários comandos sob **uma** confirmação, via a cycle-authorization
de `plugins/quenching/assets/references/align/convergence.md:34`, e entre os stages que ela cobre
estão `/specs:conclude` e `/specs:triage`.

A objeção é meio certa, e a metade que falha é a que importa. O que existe é uma confirmação única na
direção **sweep** — convergir o front inteiro. A express lane pedia a direção **cycle** — levar *um*
spec de ponta a ponta. As duas não se encontram, e isso é escolhido, não acidental: a própria
description de `/specs:align` diz que "Authoring and cycle actions are reported with the command that
closes each, never performed", de modo que nenhum align invoca `create` nem `execute` — justamente os
dois passos que a express lane precisava encadear.

Além disso, o mesmo contrato que dá a autorização única **nega** a promessa central da express lane:
`convergence.md` §What it NEVER covers classifica concluir um spec como ação irreversível e exige
"one OK **per item**", porque um spec com todas as tasks marcadas ainda pode estar esperando um
deploy. Ou seja, "de propose a archive sob uma confirmação" não é caro — é incompatível com uma regra
já em vigor. Uma express lane bem-comportada entregaria duas confirmações; uma rápida quebraria o
contrato.

### Se a express lane voltar, ela é um mode — e isso já é contrato

Uma express lane é a *mesma* sequência de verbos com menos cerimônia: nenhum objeto novo, nenhum
verbo novo, só uma profundidade diferente. `docs/standards/automation/skills.md:41` §*A technique is
a parameter of a verb, not a new axis* vincula esse caso a um argumento de um comando só, e o exemplo
que ele dá é do mesmo front. O eixo se divide "only when the *object* or the *verb* differs", e aqui
nenhum dos dois difere.

O custo confirma a mesma conclusão por outro caminho. `docs/standards/automation/context-budget.md:96`
declara um ceiling **sem folga por construção** — ele é igual ao total da superfície, para que o
próximo comando always-on o cruze no dia em que for criado. Medido em 2026-07-30,
`skills.py --root plugins/quenching budget --json` devolve `"total": 12875`, `"ceiling": 12726`,
`"ok": false`: a superfície **já está acima** do próprio ceiling. Um 27º comando always-on é a forma
mais cara disponível, e a única que o ratchet foi desenhado para sinalizar.

### Contratos que este design não pode contradizer

- `docs/standards/automation/skills.md` §*A technique is a parameter of a verb* — nenhum comando novo
  para uma variante de profundidade.
- `docs/standards/automation/context-budget.md` §The per-surface ceiling — descrição always-on é
  orçamento compartilhado, e o ceiling é medido, nunca escolhido.
- `assets/references/align/convergence.md` §The cycle-authorization contract — concluir um spec gate
  individualmente, sempre.
- `assets/references/specs-develop/spec-driven.md` §Identity — a identidade é o slug; este spec não
  se renomeia para consertar o próprio vocabulário.
## Alternatives Considered

Quatro formas inteiras que este spec poderia ter tomado. A escolhida é a terceira.

| Forma | Custo | O que compra | O que impede |
| --- | --- | --- | --- |
| **1. Criar a express lane com nome novo** (`/specs:quick`) | um 27º comando always-on numa superfície já acima do ceiling; um body que reimplementa quatro comandos | uma confirmação só, no caso pequeno | viola `skills.md:41` e o contrato de cycle-authorization que gate `conclude` por item |
| **2. Esperar até 2026-08-08 e então decidir** | nove dias, e a pergunta continua ocupando `plans/` | nada: a evidência coletada é sobre outro caminho | fechar uma pergunta cujos termos já morreram |
| **3. Fechar como absorvido e nomear o dono do resíduo** (escolhida) | uma passada de `/specs:conclude --outcome abandoned` | tira a pergunta obsoleta de `plans/`, preserva o raciocínio em `## Outcome` e dá dono ao atrito | nada que alguém queira: o mérito continua decidível pelo irmão |
| **4. Dobrar este spec dentro de `add-specs-cycle-run-modes`** | editar um spec irmão que está sendo desenvolvido em paralelo | um spec a menos | proibido aqui, e presumiria o resultado do irmão |

**Por que a 1 perdeu.** Não é o custo isolado — é que ela contradiz duas regras vinculantes ao mesmo
tempo. E a promessa central dela ("de propose a archive sob uma confirmação") é impossível de honrar:
`convergence.md:34` classifica concluir um spec como ação irreversível que exige OK próprio, então a
express lane entregaria duas confirmações se comportada, ou quebraria o contrato se rápida.

**Por que a 2 perdeu.** A data de revisão foi escolhida quando o caminho encadeado tinha quatro elos.
Ele tem um. Um prazo cuja premissa mudou não vira evidência ao expirar.

**Por que a 4 perdeu.** Editar o arquivo de um irmão que está sendo desenvolvido em paralelo é
exatamente o que produz duas verdades divergentes sobre uma decisão. Nomear o irmão em
`## Out of Scope` entrega o mesmo apontamento sem tocar no arquivo dele.

## Open Decisions

- **O ciclo `create → develop → execute → conclude` precisa de um modo de menos cerimônia?** Esta é a
  única pergunta de mérito que sobrevive à leitura deste spec, e ela é **deliberadamente não
  respondida aqui**. Ela deixou de ser desta pergunta ("criar a skill?") e passou a ser uma pergunta
  de formato sobre comandos existentes.
  **Como se decide:** pelo spec irmão `add-specs-cycle-run-modes`, que é o dono do formato de run
  mode, com evidência de uso real do ciclo colapsado — não de argumento, e não do caminho encadeado
  de quatro elos que já não existe. Este spec não presume o resultado do irmão nem edita o arquivo
  dele.
- **A superfície fica acima do ceiling de always-on, ou o ceiling é remedido?** Medido em 2026-07-30,
  `skills.py budget` reporta `total: 12875` contra `ceiling: 12726`, `ok: false`. Este spec só usa o
  número como evidência.
  **Como se decide:** pelo ratchet de `docs/standards/automation/context-budget.md` §The per-surface
  ceiling — um humano remede e reajusta, ou corta descrição. Fora do escopo daqui, e registrado
  porque o argumento de custo deste spec depende de um número que alguém vai mexer.

## Risks

- **A pergunta desaparece junto com o spec.** Ao ir para `archive/`, este spec sai de `plans/`, e
  portanto sai de `specs.py next --front`, de `/specs:continue` e da zona GENERATED de
  `plans/index.md`. Se `add-specs-cycle-run-modes` também for abandonado, o atrito do ciclo não terá
  nenhum dono vivo e ninguém vai lembrar que a pergunta foi feita — é a falha silenciosa, a pior
  classe.
  **Mitigação:** o `## Outcome` escrito no fechamento nomeia a pergunta, o irmão e os comandos de
  `## Validation`, para que `grep -ri "express lane" specs/archive/` reencontre o raciocínio inteiro.
  Não presumimos o resultado do irmão: se ele for abandonado, a mitigação é criar um spec novo, e o
  custo disso é uma passada de `/specs:create`.
- **Alguém lê `## Design` como autorização para adicionar um flag `--quick`.** A frase "se voltar, é
  um mode" descreve o *formato* permitido, não uma aprovação da mudança.
  **Mitigação:** `## Proposal` diz explicitamente que a decisão de mérito é de
  `add-specs-cycle-run-modes`, e `## Out of Scope` repete o limite. Um flag adicionado sem essa
  decisão é regressão de escopo, não continuação deste spec.
- **Os números citados envelhecem e viram argumento morto.** `26` comandos, `total: 12875`,
  `ceiling: 12726` e as citações por linha (`skills.md:41`, `context-budget.md:96`,
  `execute.md:94` e `:190`) são medidas de 2026-07-30.
  **Mitigação:** cada número aparece datado, e `## Validation` manda **rodar** os comandos em vez de
  confiar no valor transcrito. As citações trazem também o título da seção, para sobreviverem a um
  deslocamento de linha.
- **Um irmão reescreve um arquivo que este spec cita.** `retire-skill-vocabulary` é dono da citação
  obsoleta `/specs:refine --mode` em `docs/standards/automation/skills.md:45`, exatamente no bloco que
  este spec usa como contrato vinculante.
  **Mitigação:** citar a seção por nome (§*A technique is a parameter of a verb, not a new axis*),
  que é o que sobrevive à limpeza; a regra em si não muda, só o exemplo dela.
- **O stage derivado deste spec lê `executing` sem que nada tenha sido executado.** Efeito mecânico
  da regra de derivação: `## Handoff` preenchido já basta para o stage virar `executing`
  (`assets/references/specs-develop/spec-driven.md` §Derived stages), e aqui o `## Handoff` existe para
  orientar quem **fecha**, não quem constrói. Quem lê `/specs:status` ou `plans/index.md` vai ver este
  spec agrupado com trabalho em andamento.
  **Mitigação:** `specs.py next` desmente na hora — reporta `"action": "promote"`, não
  `implement_task` — e é essa saída que `## Validation` manda conferir. O nome dos stages derivados é
  território do irmão `name-the-scaffolded-stage`; este spec só registra a observação, não muda a
  regra.
- **ACCEPTED** — este spec gastou uma passada completa de `/specs:develop` para concluir que nada
  precisa ser construído, o que é mais caro do que abandoná-lo com uma linha. Aceito porque o
  entregável de um spec de decisão *é* o "por quê": um `## Outcome` dizendo apenas "obsoleto" faz a
  mesma ideia voltar à mesa em três meses sem nada para ler contra ela. O custo é limitado por
  construção — nenhuma task, nenhum doc escrito, nenhum arquivo fora deste.
- **ACCEPTED** — `## Tasks` fica com um explicit none, então este spec passa o ready gate sem nunca
  poder ser executado. Aceito porque é a verdade do spec: inventar uma task cerimonial para "parecer
  construível" faria `/specs:execute` abrir um branch para não fazer nada.
## Tasks

- none — este spec é uma decisão, e a decisão é que **nada deve ser construído**: nenhum comando novo,
  nenhum flag, nenhum standard, nenhuma edição em `plugins/`, `docs/` ou `.claude/`. O entregável é o
  registro do "por quê", que `/specs:conclude --outcome abandoned` escreve em `## Outcome` — e escrever
  o `## Outcome` é do comando de fechamento, nunca de uma task. Inventar uma task cerimonial aqui só
  para o spec parecer construível deixaria `/specs:execute` abrir um branch para não fazer nada.
  `specs.py next` reporta `promote`, que é o roteamento correto.
