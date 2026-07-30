---
slug: reduce-execute-conclude-cost
title: Re-evaluate /specs:execute and /specs:conclude runs for cost reduction
verification: per-section
priority: {level: 3, criticality: high, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# Re-evaluate /specs:execute and /specs:conclude runs for cost reduction

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

Este spec começou como uma pergunta de economia: quais passos de `/specs:execute` e `/specs:conclude`
poderiam rodar num modelo mais barato. Ler o `## Problem` primeiro é ler o pedido como ele foi feito; o
`## Proposal` guarda o que sobrou dele depois de medir os transcripts das runs que já aconteceram.

A conclusão, em uma linha: o dinheiro desses dois comandos não vai em preço de token, vai em contexto
relido — 98% dos tokens medidos são leitura de cache, o mesmo contexto voltando a cada turno. Trocar o
modelo mexe no preço unitário da parte mais barata da conta, e um pin inline ainda invalida o cache que
torna ela barata. Então o pedido é respondido com "nenhum passo, por pin", e a economia real está em
mover trabalho para um contexto que ninguém relê.

Por onde entrar. `## Design` D0 tem a medição com os números e de onde vieram; D1 e D2 são a razão pela
qual o eixo do pedido não funciona; D3 conta a descoberta mais desconfortável — a delegação que o repo já
autorizou por escrito nunca rodou uma única vez. `## Alternatives Considered` argumenta a recusa do pedido
literal em vez de apenas afirmá-la, ao lado de não-fazer-nada e da menor coisa que funcionaria.
`## Out of Scope` impede as ideias vizinhas de voltarem, cada uma com o documento ou a medição que a
recusa.

O que ler antes de confiar no resultado. `## Risks` guarda os dois jeitos silenciosos disso dar errado —
um número de limite superior citado como exato, e um coletor de diff que perde um hunk e devolve um verde
— cada um com a mitigação que é mecânica e não depende de julgamento. E `## Open Decisions` é honesto
sobre o que esta medição **não** alcança: o custo das sessões de agente que o harness de checks cria fica
em transcripts separados, e é justamente esse número que o spec irmão `add-specs-cycle-run-modes` está
esperando. O jeito de medir está escrito; o resultado não é presumido.

A entrega é pequena para o tamanho do argumento e cabe em quatro grupos de task: um subcomando de custo em
`session.py`, cinco textos que passam a lê-lo, dois standards e uma prova. `## Validation` é toda
determinística de propósito — um spec sobre custo de run não abre a própria prova gerando sessões de agente
faturadas — e inclui a medição de antes e depois da própria entrega, com o limiar que decide se a única
mudança de comportamento fica ou sai.
## Problem

`/specs:execute` e `/specs:conclude` são os dois comandos mais caros da front de specs, e ninguém
nunca olhou o que esse custo está de fato comprando. Os dois rodam longo — execute caminha task por
task, conclude revisa um branch inteiro — e nenhum dos dois declara quais dos seus passos realmente
precisam do modelo da sessão e quais sobreviveriam em um mais fraco.

Re-avaliar as runs dos dois comandos em busca de redução de custo: olhar os transcripts de sessões
que já os executaram procurando evidência de para onde o dinheiro foi, e usar essa evidência para
dizer quais passos (chamadas de sub-agente, verificação por task, a revisão de branch) poderiam cair
para um modelo mais barato ou um effort mais baixo sem enfraquecer o que o comando garante.

## Proposal

A entrega é **uma medição em código, mais a regra que ela prova**, e só depois as mudanças de corpo
que a medição justifica. O eixo que o `## Problem` pediu — "qual passo cai para um modelo mais
barato" — é respondido, e a resposta medida é **nenhum, por pin inline**: o custo desses dois
comandos não é preço de token, é `turnos × contexto` relido a cada turno, e um pin inline invalida
justamente o cache que torna esse contexto barato (`## Design` D1 e D2). O que sobra é mover
trabalho para um contexto que não é relido — não trocar o modelo do contexto que é.

Depois desta entrega:

- `session.py` ganha um subcomando de custo: por comando atribuído, os tokens separados por tipo
  (`cache_read_input_tokens`, `cache_creation_input_tokens`, `output_tokens`), a contagem de turnos, e
  os valores de `model` e `effort` vistos. Lidos do transcript por código, nunca recontados por um
  modelo — a mesma regra que `session-evidence.md` §The rule a counted claim must obey já impõe às
  contagens de tool call.
- Cada figura de custo carrega o mesmo `closed` / `mayIncludeTurnsFrom` que `session.py` já anexa a um
  stage conduzido, então o número de um comando alcançado por `Skill` é reportado como **limite
  superior** e nunca como exato.
- `/skill:retro` reporta custo ao lado das contagens que já reporta, sem ganhar concessão de
  ferramenta nenhuma e continuando typed-only.
- `docs/standards/automation/run-cost.md` passa a ser o dono do assunto: por que a integral é
  `turnos × contexto`, por que um pin inline de `model` ou `effort` nesses dois comandos **aumenta** o
  gasto, quais delegações são seguras e por quê, e a regra do limite superior.
- `docs/standards/automation/session-evidence.md` para de prometer custo que não entrega: a §What a
  command's run cost aponta para o dono novo e nomeia os campos que o digest passou a devolver.
- `/specs:conclude` passo 2 passa a **permitir** delegar a *coleta* do diff de branch a um sub-agente
  read-only (`model: sonnet`, `effort: low`), com o veredito, cada confirmação e cada escrita ficando
  no orquestrador, e com um cross-check mecânico contra `git diff --stat` que impede uma coleta
  incompleta de virar "nada a revisar".
- `/specs:execute` passo 5b passa a dizer **o que a delegação de executor economiza e quando vale** —
  a delegação que `execution.md` §Delegating an executor já permite e que, medida, nunca disparou uma
  única vez em todo o arquivo de transcripts.
- A tabela de model policy do `README.md` ganha a linha do coletor e passa a registrar o motivo
  **medido** pelo qual nenhum dos dois comandos recebe pin inline, no lugar do motivo apenas
  qualitativo que a linha de `/specs:conclude` carrega hoje.
- Nada passa a recusar, nada passa a ser obrigatório, nenhum comando novo é criado e nenhuma
  `description` cresce.

## Out of Scope

- **Pin inline de `model` ou `effort` em `/specs:execute` ou `/specs:conclude`** — é literalmente o
  que o `## Problem` pediu, e é a recusa mais importante deste spec. Medido, o pico de contexto por
  turno é de 349k tokens em execute e 265k em conclude; `capabilities.md` §The cache trap diz que
  model e effort fazem parte da chave do prompt cache da sessão, então um pin inline força **um
  recompute inteiro desse contexto** em troca de desconto em tokens que já são cobrados a 10% por
  serem cache read. A troca é negativa e a conta está em `## Design` D2.
- **`context: fork` em qualquer comando do ciclo.** É a forma óbvia de isolar contexto e o `CLAUDE.md`
  a proíbe por nome: todo sweep precisa apresentar confirmações acopladas a código no meio do fluxo, e
  um contexto forkado não alcança a conversa onde o OK é dado. Fica registrado aqui para que a ideia
  não volte como otimização.
- **Downgrade de qualquer sub-agente de `/docs:import-memory`.** Também proibido pelo `CLAUDE.md`:
  uma classificação errada lá vira uma deleção errada de memória. Este spec não toca naquele comando.
- **O menu de run modes e a chave `gateCommand`** — pertencem ao spec irmão `add-specs-cycle-run-modes`,
  que já recusou o menu por escrito e é o dono da declaração no workspace. A fronteira está em
  `## Risks`.
- **O custo das sessões `claude -p` que `functional-checks.sh` cria.** Cada check é uma sessão de
  agente faturada, e ela aparece como um transcript **separado**, com outro `cwd`, então ela é
  invisível nas figuras deste spec. Dizer que o gate pré-merge é pequeno seria uma afirmação que a
  medição não sustenta — fica em `## Open Decisions` com o jeito de medir.
- **A doutrina "cite a seção, não o arquivo".** `/specs:execute` carrega para o contexto o próprio
  corpo mais cinco referências (`execution.md`, `git.md`, `spec-driven.md`, `homes.md`,
  `conformance.md`), cerca de 22k tokens que ficam sendo relidos a cada turno: numa run de 300 turnos
  isso é aproximadamente 6,6M tokens de cache read, ~10% da pior run medida. É real e é o corte que
  este spec **não** faz: valeria para todo comando que cita uma referência, não só para estes dois, e
  é mudança de doutrina de citação — encaminhada como follow-up em `## Open Decisions`.
- **O teto always-on de `docs/standards/automation/context-budget.md`.** Aquele standard é dono do que
  a superfície custa **antes de qualquer comando disparar**; este é dono do que **uma run** custa
  depois. São duas medições diferentes e o doc novo só cita o vizinho.
- **Uma task de bump de versão.** `versioning-release.md` §When the bump happens é explícita: as seis
  strings se movem uma vez, em `/specs:conclude` passo 5, e nunca como task. E `session.py` está
  deliberadamente **fora** desse lockstep (`session.py:16-23`), então mexer nele não acrescenta
  obrigação de release nenhuma.
- **Instalar `session.py` em um repo target.** O cabeçalho do arquivo já decidiu isso: a entrada dele
  é `~/.claude/projects/**`, a máquina do operador, e não existe nada para um target guardar.
- **Re-medir os 121 transcripts do arquivo como entregável.** A medição que este spec precisa é a de
  duas runs comparáveis, antes e depois. Um censo do arquivo é interessante e não é a prova de nada.
- **Mudar a política `verification` deste spec.** Fica `per-section`, e o motivo está em
  `## Validation`.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/automation/run-cost.md` — o dono do assunto: por que a integral de uma run é
  `turnos × contexto`, a armadilha do pin inline nos comandos longos, quais delegações são seguras e
  com qual modelo, a regra de que toda figura de um stage conduzido é limite superior, e o gate de
  graduação do próprio doc
- `docs/standards/automation/session-evidence.md` — revisado: a §What a command's run cost passa a
  apontar para o dono novo e a nomear os campos de custo que o digest devolve, em vez de prometer
  custo que a ferramenta não entrega

### Standards at `authority: background` this spec may resolve

- none — nenhum standard `background` é provado nem promovido por esta entrega. Dois são tocados e
  nenhum gradua: `docs/standards/automation/context-budget.md` é citado e continua `background`
  porque o que o graduaria é `skills.py budget` rodando em dois repos adotantes, coisa que este spec
  não faz; e `docs/standards/automation/session-evidence.md` é **revisado** pela task 3.2 mas não
  promovido, porque o gate de graduação dele pede uso independente repetido de `/skill:retro`, e uma
  revisão de seção não é uso.

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/session.py` — os campos de custo em `Command` (`session.py:177`), a
  soma de `message.usage` em `read_session` (`session.py:299`), a saída em `as_dict`
  (`session.py:207`), `cmd_list` (`session.py:848`) e `cmd_digest` (`session.py:557`), e as fixtures
  embutidas (`session.py:652`, `session.py:710`)
- `plugins/quenching/commands/skill/retro.md` — os passos 3 e 4 passam a ler e a pesar as figuras de
  custo; a `description` não cresce, porque ela já lista `"what did this command cost"` como gatilho
- `plugins/quenching/commands/specs/conclude.md` — o passo 2 permite o coletor read-only com o
  cross-check mecânico, e o passo 7 reporta se a coleta foi delegada
- `plugins/quenching/commands/specs/execute.md` — o passo 5b diz o que a delegação de executor
  economiza e quando ela vale
- `plugins/quenching/assets/references/specs-execute/execution.md` — a §Delegating an executor
  (`execution.md:233`) ganha o motivo medido, e a §This is not `context: fork` continua intacta
- `plugins/quenching/README.md` — a tabela de model policy ganha a linha do coletor e o motivo medido
  nas linhas de `/specs:execute` e `/specs:conclude`
- `docs/knowledge/glossary.md` — uma entrada para a integral de custo de run, roteada por
  `/docs:define` e nomeada pela task 3.3, nunca escrita à mão daqui

## Validation

Tudo abaixo roda a partir da raiz do repositório e é determinístico. **Nenhum comando deste conjunto
gera sessão de agente** — o que importa especialmente aqui, porque o assunto do spec é custo de run: um
spec sobre custo que abre a própria prova gerando sessões faturadas estaria se contradizendo.

**1. A ferramenta continua legível e o selftest cresceu com o assunto.**

```bash
python3 plugins/quenching/assets/bin/session.py --version
python3 plugins/quenching/assets/bin/session.py selftest
```
O baseline de hoje é `session 4.4.0` e `session selftest — 15 fixture record(s)` seguido de `PASS`.
Depois da entrega o `--version` continua rastreando o plugin (`session.py` está **fora** do lockstep das
seis strings, `session.py:16-23`, então nenhuma task bump nada), a contagem de fixture records **sobe**,
e o `PASS` continua. Um selftest com a mesma contagem de antes é prova de que as asserções de custo não
entraram.

**2. As duas leituras de custo, exata e limite superior, são asseridas pelo selftest.** As fixtures
embutidas passam a carregar `message.usage`, e o selftest tem que assertar as duas: um comando **typed**
(atribuição fechada) devolve custo exato; um stage **conduzido cujo condutor nunca retomou** devolve
`closed: false` com `mayIncludeTurnsFrom` preenchido **nas figuras de custo**, não só nas contagens de
tool call. Uma figura de custo sem essa marca num stage não fechado é a falha que esta asserção existe
para pegar.

**3. O subcomando bate com o transcript real.** A run de `/specs:conclude` da sessão
`94612f74-3749-491d-a506-c7ed067839e0` é o caso limpo — entrada typed, `closed: true`, zero anomalias,
exit 0 hoje. Somando `message.usage` dos turnos atribuídos a ela:

| Campo | Valor esperado |
| --- | --- |
| turnos | 247 |
| `cache_read_input_tokens` | 35.143.072 |
| `cache_creation_input_tokens` | 496.710 |
| `output_tokens` | 226.443 |
| `closed` | `true`, sem `mayIncludeTurnsFrom` |

O subcomando novo tem que devolver exatamente esses números para esse transcript, e continuar exit 0.
Um número diferente é bug de soma, não interpretação.

**4. A superfície de comandos continua conforme depois das edições de corpo.**

```bash
cd plugins/quenching
python3 assets/bin/skills.py --root . doctor --json    # 26 commands, nenhum finding
python3 assets/bin/skills.py --root . lint --json      # exit 0
python3 assets/bin/skills.py --root . budget --json    # o total NÃO sobe
```
O baseline de hoje é `total: 12875` contra `ceiling: 12726`, ou seja `ok: false` e exit 1 — o ratchet
**já disparou** antes desta entrega, é condição pré-existente e não é desta entrega para consertar. O que
esta entrega tem que provar é que o número **não sobe**: nenhum comando novo é criado, e nenhuma
`description` cresce para explicar custo ou delegação (as edições de 2.1 a 2.4 são todas no corpo).

**5. O bundle aceita o standard novo e a revisão.**

```bash
python3 plugins/quenching/assets/hooks/okf-validate.py docs
```
O baseline de hoje é `0 error(s), 14 warning(s)`, todos `stale-doc` pré-existentes, e
`session-evidence.md` **não** é um deles. A entrega não pode acrescentar `error` nenhum, e a task 3.2
atualiza o `timestamp` daquele doc junto com o conteúdo, então ela também não pode criar um `stale-doc`
novo.

**6. O spec fecha as próprias contas.**

```bash
python3 plugins/quenching/assets/bin/specs.py validate --spec reduce-execute-conclude-cost --json
```
Sem `sp-impact-uncovered`: os dois caminhos declarados em `## Impact` são nomeados no texto das tasks
3.1 e 3.2.

**7. A medição de antes e depois da própria entrega.** A task 4.2 roda o subcomando novo sobre uma run de
`/specs:conclude` sem delegação e sobre uma com, num branch de tamanho comparável, e registra
`cache_read` e turnos dos dois lados. O limiar declarado é ~10%: abaixo dele a linha de permissão sai do
corpo e o número medido é escrito no standard como o motivo. Uma economia não medida não conta como
economia.

**Fora deste conjunto, de propósito:** `./assets/bin/functional-checks.sh`. Cada check é uma sessão
`claude -p` faturada, `surface-verification.md` já diz que essa verificação pertence à front de skill e ao
comando que edita a superfície, e nenhuma edição desta entrega muda o **registro** de comandos — só
corpos. Rodá-lo aqui seria cobrar do spec exatamente o gasto que ele existe para tornar visível.

**A política `verification` fica `per-section`.** Os quatro grupos de `## Tasks` são unidades
independentes — a ferramenta, os consumidores, os standards, a prova — e o `selftest` de `session.py` é
barato o suficiente para rodar uma vez por grupo. `per-task` re-rodaria um selftest de fixture a cada
edição de texto sem comprar informação; `end-of-plan` deixaria uma soma errada em `read_session` ser
descoberta só depois de quatro corpos editados em cima dela.

## Design

As alternativas de **forma inteira** estão em `## Alternatives Considered`. Aqui ficam as decisões,
cada uma com a alternativa pesada dentro dela, e cada número vem da medição descrita em D0.

### D0. De onde vêm os números deste spec

Todos os valores abaixo foram lidos dos transcripts em `~/.claude/projects/*claude-quenching*/*.jsonl`
agrupando registros `type: assistant` por `attributionSkill` — o mesmo campo que `session.py` já usa
(`session.py:299`). Somando `message.usage`:

| Comando | Sessões | Turnos | cache read | cache creation | output | pico de contexto/turno |
| --- | --- | --- | --- | --- | --- | --- |
| `/specs:execute` | 9 | 1.339 | 213,79M | 3,48M | 1,06M | 349k |
| `/specs:conclude` | 7 | 1.309 | 171,29M | 3,47M | 0,98M | 265k |

São os dois maiores itens atribuídos de todo o arquivo, e juntos somam cerca de 394M de tokens
brutos. A pior run isolada de execute: 299 turnos, 64,3M de contexto lido, pico de 349k. A pior de
conclude: 247 turnos, 35,6M.

**Uma medição feita à mão, dentro de um spec, é exatamente a afirmação que
`session-evidence.md` §The rule a counted claim must obey proíbe** — um número que só existe na prosa
não é re-verificável e envelhece igual ao teto de `context-budget.md`. É por isso que a primeira
entrega é o instrumento e não a conclusão.

### D1. A integral do custo é `turnos × contexto`, não preço de token

98% dos tokens brutos dos dois comandos são `cache_read_input_tokens`: 213,79M de 218,3M em execute,
171,29M de 175,7M em conclude. Cache read é o **mesmo contexto sendo relido a cada turno**, e o total
de uma run é a soma do tamanho do contexto ao longo dos turnos. Numa run de 299 turnos com contexto
médio de ~215k, quase todo o gasto é essa soma.

Disso segue quais alavancas existem, e são três: **menos turnos no contexto do orquestrador**,
**contexto menor por turno**, e **mover trabalho para um contexto que não é relido**. Trocar o modelo
não é nenhuma das três — muda o preço unitário de tokens que já estão na faixa mais barata.

### D2. Por isso um pin inline aumenta o custo em vez de reduzir

`capabilities.md` §The cache trap: model e effort fazem parte da chave do prompt cache da sessão, e um
pin inline "invalida o cache inteiro — a próxima requisição recomputa cada token de input". Com pico
de 349k tokens de contexto, o pin cobra um recompute na faixa de cache creation para economizar em
tokens cobrados a 10%. A conta só fecha para o pin se a run terminar logo depois dele, que é o
oposto do que estes dois comandos fazem.

A tabela de model policy do `README.md` já recusa pin nas duas linhas, por um motivo **qualitativo**
("nada mecânico para downgradear" em conclude; executor pinado no modelo da sessão em execute). Esta
decisão não contradiz nem substitui esse motivo: acrescenta o quantitativo, que é o que faltava para
a recusa parar de parecer conservadorismo.

Duas colocações continuam cache-safe, e o mesmo doc diz por quê: um pin dentro de `context: fork` — que
o `CLAUDE.md` proíbe aqui — e um pin em **definição de sub-agente**, que carrega o próprio contexto.
Sobra exatamente uma forma legítima de usar um modelo mais barato nesses comandos, e é D4.

### D3. A alavanca já concedida nunca disparou

Em **121 transcripts** do arquivo não existe **um único** registro `assistant` com
`isSidechain: true`. Ou seja: nenhuma delegação de nenhum comando quenching jamais rodou neste repo,
inclusive a que `execution.md` §Delegating an executor (`execution.md:233`) já permite por escrito para
uma task que declara `files:` e não escreve em `docs/`.

O contrato não está errado, está inerte. A alavanca mais barata deste spec não é uma regra nova: é o
corpo de `/specs:execute` passar a dizer **o que a delegação economiza** — o trail de leitura e edição
da task fica no contexto do sub-agente e nunca entra no do orquestrador, logo nunca é relido pelos
turnos restantes — e a definição continua pinada no modelo da sessão, **nunca `haiku`**, exatamente
como a linha de `/specs:execute` na tabela de model policy já manda.

### D4. O coletor de diff é `sonnet` + `effort: low`, e o veredito nunca sai do orquestrador

O passo 2 de `/specs:conclude` (`conclude.md:126`) lê o diff inteiro do branch. Medido, conclude gasta
511 chamadas de `Bash` em 7 sessões — cerca de 73 por run — das quais 35 são `git diff` e outras 80
são `sed -n` / `grep -n` relendo pedaços. Cada saída dessas cai no contexto do orquestrador e passa a
ser relida por todos os turnos seguintes.

Fica **permitido** delegar a *coleta* a um sub-agente read-only, que devolve um inventário de hunks —
arquivo, contagem, faixas de linha, e o que cada um faz — em vez do diff. Três garantias, cada uma
copiada de um precedente que a tabela de model policy já registra:

- **`model: sonnet`, `effort: low`, nunca `haiku`.** O motivo é o mesmo que a linha de
  `/docs:align` (content passes) dá para descartar haiku: um falso "nada a fazer" encerra o loop
  antes da hora. Aqui o falso equivalente é "nada a revisar", e ele passa verde.
- **O veredito fica no orquestrador.** É o precedente da linha de `/skill:align`: a coleta é
  delegável, e "esse corpo não tem prescrição positiva" é uma afirmação sobre comportamento, que quem
  a faz também precisa pesar. Coerência de branch é a mesma classe de julgamento.
- **Cross-check mecânico.** O inventário é conferido contra `git diff --stat` — contagem de arquivos e
  de hunks — antes de qualquer revisão. É o padrão "cross-checked by the orchestrator" que a linha de
  `/docs:glossary-backfill` já usa, e é o que impede uma coleta incompleta de virar um verde.

Isso **não** é `context: fork`: o orquestrador continua na conversa viva, que é a distinção que
`execution.md` §This is not `context: fork` já escreveu e que nenhuma otimização futura deve "consertar".

### D5. Todo número de custo é limite superior, e o instrumento diz isso na mesma frase

`session-evidence.md` §What a command's run cost já mediu que `attributionSkill` é um **ponteiro, não
um span**: em 43 stages conduzidos a atribuição volta para o condutor 1 vez, nunca volta 36 vezes, e
salta para um terceiro comando 6 vezes. E os dois comandos deste spec se conduzem: `/specs:execute`
passo 7 oferece encadear em `/specs:conclude` via `Skill`.

Logo as figuras de D0 **são limites superiores** para uma run conduzida, e o subcomando de custo
carrega `closed` e `mayIncludeTurnsFrom` nas figuras de custo do mesmo jeito que `close_attribution`
(`session.py:267`) já os carrega nas contagens de tool call. `parse-honesty.md` aplicada a um
ponteiro: nomear o erro de leitura, nunca inventar a consequência.

### D6. Dois donos: o instrumento e o assunto

`session-evidence.md` é dona de **como um transcript é lido como evidência** — onde ele mora, as duas
formas de entrada, a escada de arms, a honestidade da atribuição. O assunto novo é **o que uma run
custa e qual alavanca a move**, consumido pelos comandos do ciclo e pela tabela de model policy, não
pela ferramenta de retro. Doc novo, mais uma revisão de uma seção do vizinho:

- `docs/standards/automation/run-cost.md` (novo) — a integral, a armadilha do pin inline, as
  delegações seguras com o motivo de cada modelo, a regra do limite superior.
- `docs/standards/automation/session-evidence.md` (revisado) — a §What a command's run cost aponta
  para o dono novo e nomeia os campos de custo. A revisão é **requisito**, não arrumação: o título
  daquela seção promete custo e a ferramenta só entrega contagens.

### Contratos que este design não pode contrariar

- `CLAUDE.md`, as duas regras que precisam sobreviver a qualquer refactor: nada de `context: fork`
  nesses comandos, e nada de `haiku` na classificação ou nos executores de `/docs:import-memory`.
- `docs/standards/architecture/read-only-views.md` — concessão de ferramenta é por comando; o coletor
  recebe grant read-only, então a garantia está na concessão e não só na prosa.
- `docs/standards/automation/context-budget.md` — o teto não tem folga e já está estourado por
  condição pré-existente (12.875 contra 12.726); nenhum comando novo é criado e nenhuma `description`
  cresce.
- `docs/standards/automation/session-evidence.md` — uma afirmação contada vem de código lendo o
  transcript, nunca de um modelo relembrando a própria run.
- `docs/standards/quality/parse-honesty.md` — o que não pôde ser lido é reportado, não estimado.
- `docs/standards/quality/surface-verification.md` — inconclusivo não é verde, e um harness que gera
  sessões de agente é cobrado por sessão.
- `docs/standards/ci-cd/versioning-release.md` — o bump acontece no conclude, nunca como task; e
  `session.py` está fora do lockstep das seis strings.

## Alternatives Considered

Alternativas de **forma inteira**, cada uma escrita como seu melhor defensor a escreveria. As
alternativas de decisão isolada ficam dentro de `## Design`.

| # | Alternativa | Custo | O que compra | Por que perdeu |
| --- | --- | --- | --- | --- |
| A | **Pinar `model`/`effort` nos passos "mecânicos"** dos dois comandos, como o `## Problem` pede | uma linha de frontmatter por comando | o efeito que todo mundo espera de redução de custo: os passos baratos ficam num modelo barato | `capabilities.md` §The cache trap mais a medição: com pico de 349k de contexto por turno, o pin invalida o cache e cobra um recompute inteiro para descontar tokens já cobrados a 10%. É aumento de custo, não redução (`## Design` D2) |
| B | **`context: fork` nos dois comandos**, isolando o contexto da run | zero código | seria a maior redução possível de contexto relido, de uma vez | proibido pelo `CLAUDE.md` por nome: os dois precisam apresentar confirmações acopladas a código no meio do fluxo, e um contexto forkado não alcança a conversa onde o OK é dado. `/specs:conclude` tem 34 chamadas de `AskUserQuestion` medidas em 7 sessões — cerca de 5 confirmações por run, exatamente o que o fork perderia |
| C | **A menor coisa que funcionaria**: escrever o standard com a medição feita à mão neste spec, e não mexer em código nenhum | uma task de doc; zero mudança de ferramenta, zero lockstep | a decisão hoje, e o irmão `add-specs-cycle-run-modes` desbloqueado imediatamente | perde por pouco, e é a alternativa a reabrir se D ficar caro: um número que só existe na prosa não é re-verificável e envelhece igual ao teto de `context-budget.md` (que precisou de uma re-medição humana quando disparou). `session-evidence.md` já decidiu que uma afirmação contada vem de código |
| D | **O instrumento, o standard, e só as mudanças de corpo que a medição justifica** (escolhida) | um subcomando em `session.py` mais fixture, dois docs, três corpos, uma linha de tabela | tira a decisão de custo da prosa e põe num comando que qualquer um roda de novo; e a mesma medição serve para provar o antes/depois da própria entrega | — |
| E | **Não fazer nada** | zero | zero | os dois comandos são os dois maiores itens atribuídos do arquivo (218,3M e 175,7M de tokens brutos), a alavanca que o repo já concedeu nunca disparou (zero sidechain em 121 transcripts), e o irmão `add-specs-cycle-run-modes` registrou em `## Open Decisions` que está esperando esta medição |
| F | **Comprar emprestado**: usar `/cost` da sessão ou a conta de uso da API em vez de instrumentar | zero código | número autoritativo, vindo de quem cobra | nenhum dos dois atribui gasto **por comando** — é por sessão, e uma sessão deste repo roda quatro ou cinco comandos. A pergunta do `## Problem` é qual *passo* cai, e essa granularidade só existe em `attributionSkill` |
| G | **Uma ferramenta nova de custo**, separada de `session.py` | um quarto script no `assets/bin` | separação de assuntos limpa | `session.py` já resolve o transcript (`session.py:148`), já lê `attributionSkill` (`session.py:299`), já tem o contrato de honestidade da atribuição e já está **fora** do lockstep das seis strings (`session.py:16-23`). Uma ferramenta nova duplicaria os três e precisaria de um dono novo para a mesma regra |
| H | **Cortar contexto encurtando as referências** que os dois comandos carregam | reescrever `execution.md`, `git.md`, `spec-driven.md` | ~22k tokens por turno a menos, ~6,6M numa run de 300 turnos | é ~10% da pior run, e cobra o preço que este repo menos quer pagar: corpo de comando é código-fonte, e encurtar uma referência é apagar uma regra. A versão barata da mesma ideia — citar a seção em vez do arquivo — está em `## Out of Scope` com o número |

A tensão que este spec precisa declarar: a alternativa A **é** o pedido literal do `## Problem`, e
está sendo recusada com evidência em vez de atendida. Se a medição de D0 estivesse errada quanto à
proporção de cache read, A voltaria a ser a entrega certa — e é por isso que o instrumento de D vem
antes do standard e não depois.

## Open Decisions

- **A delegação de coleta do diff se paga?** É a suposição que sustenta a única mudança de
  comportamento da entrega. **Como se decide:** com o subcomando novo, medindo a mesma run de
  `/specs:conclude` sem e com delegação — `cache_read` total e turnos — sobre um branch de tamanho
  comparável ao das runs de `## Design` D0. Limiar declarado: abaixo de ~10% de economia a linha de
  permissão sai do corpo e o motivo medido fica escrito no standard. Isso é a task 4.2, não uma
  pendência para depois do merge.
- **O gate pré-merge é o maior item, ou não?** É a pergunta que `add-specs-cycle-run-modes` registrou
  em `## Open Decisions` esperando este spec, e este spec **não a responde**: cada check de
  `functional-checks.sh` é uma sessão `claude -p` faturada, e ela grava um transcript **separado**, com
  outro `cwd`, então ela é invisível nas figuras de D0. **Como se decide:** contando os transcripts que
  aparecem sob o `cwd` do checkout sob teste durante uma run do harness, e somando o custo de cada um
  com o mesmo subcomando. É uma medição de outra unidade — sessões, não turnos — e fica registrada aqui
  em vez de estimada. Nenhum resultado é presumido, e a fronteira com o spec irmão está em `## Risks`.
- **A doutrina "cite a seção, não o arquivo" vira um spec?** `/specs:execute` carrega ~22k tokens de
  referência que são relidos a cada turno (~6,6M numa run de 300 turnos, ~10% da pior run medida).
  **Como se decide:** com o subcomando novo, comparando uma run que leu a referência inteira com uma que
  leu por `offset`/`limit` — o `read_window` que `session.py` já modela. Se a economia se confirmar, é um
  spec próprio, porque a mudança vale para todo comando que cita uma referência e não só para estes dois.
  Encaminhado, não feito aqui.
- **`per-task` para o grupo da ferramenta?** A política declarada é `per-section`, e o grupo 1 mexe em
  `session.py`, onde o `selftest` é barato o suficiente para rodar por task. **Como se decide:** se
  durante a build o grupo 1 crescer para mais de três tasks, vale reabrir; com o tamanho atual,
  `per-section` roda o `selftest` uma vez por grupo, que é o que `## Validation` pede.
- **A casa do standard.** A recomendação é `docs/standards/automation/run-cost.md`, ao lado de
  `context-budget.md` (custo antes de disparar) e de `session-evidence.md` (como o transcript é lido).
  **Como se decide:** depende de `revise-standards-subject-folders`, que pode mexer nas pastas de
  assunto fixas. Enquanto isso o caminho declarado é o de hoje, e a fronteira está em `## Risks`.

## Risks

- **Um número de limite superior é citado como exato, e uma política é decidida em cima dele.** É o
  modo de falha mais provável desta entrega, porque um número com unidade parece exato. As figuras de
  `## Design` D0 incluem, para um stage conduzido, turnos que podem ser do condutor — `/specs:execute`
  passo 7 encadeia em `/specs:conclude` por `Skill`, e `session-evidence.md` mediu a atribuição
  voltando ao condutor 1 vez em 43 stages. *Mitigação:* o subcomando de custo carrega `closed` e
  `mayIncludeTurnsFrom` **nas figuras de custo**, não só nas contagens de tool call, e o standard novo
  declara a regra do limite superior na mesma frase em que dá o número.
- **O coletor de diff perde um hunk e o relatório diz "nada a revisar".** É o único jeito silencioso
  desta entrega dar errado: um merge passa verde levando o que a revisão de branch teria pego, e o
  passo 6 de `/specs:conclude` nem chega a ser o guarda, porque ele grada a suíte e não a leitura.
  *Mitigação:* três, e nenhuma depende de julgamento — `model: sonnet` e nunca `haiku` (o motivo
  registrado na linha de `/docs:align` content passes: um falso "nada a fazer" encerra o loop antes da
  hora); cross-check mecânico do inventário contra `git diff --stat` antes de qualquer revisão; e o
  veredito de coerência ficando no orquestrador, que é o precedente da linha de `/skill:align`.
- **Alguém "otimiza" isto virando `context: fork`.** O raciocínio deste spec — mover trabalho para um
  contexto que não é relido — é exatamente o argumento que alguém usaria para forkar os dois comandos,
  e essa é a coisa que o `CLAUDE.md` proíbe por nome. *Mitigação:* recusado por nome em
  `## Out of Scope` e registrado no standard novo com o motivo, para que a próxima pessoa leia a recusa
  em vez de repropor. `/specs:conclude` tem 34 `AskUserQuestion` medidas em 7 sessões — cerca de 5
  confirmações por run — e é isso que um fork perderia.
- **O standard nasce com um número e envelhece.** É precisamente o que aconteceu com o teto de
  `context-budget.md`, que precisou de uma re-medição humana no dia em que disparou. *Mitigação:*
  `authority: background` com gate de graduação declarado no doc, e o instrumento existe justamente
  para que re-medir seja um comando em vez de uma investigação.
- **A delegação custa o que economiza.** `capabilities.md` §Subagents — delegar desperdiça quando o
  handoff é do tamanho do trabalho, e um inventário de hunks de um diff grande pode ser quase o diff.
  *Mitigação:* a task de prova mede a mesma run antes e depois com o subcomando novo; abaixo de ~10%
  de economia a linha de permissão sai do corpo e o motivo medido fica escrito. A permissão é
  **permissão**, nunca obrigação, então uma run que não delega continua correta.
- **O spec entrega um número e nada muda.** Medir é a parte confortável; mexer em `conclude.md` e em
  `execute.md` é a parte que exige cuidado, e é a que um executor com pressa corta. *Mitigação:* as
  três edições de corpo estão em `## Tasks` com caminho e verify próprios, não em `## Open Decisions`.
- **Assunto de duas fronts.** O instrumento (`session.py`, `/skill:retro`) é da front de skill e o
  problema é da front de specs, então este spec cruza a fronteira. *Mitigação:* não é fronteira nova —
  a própria `description` de `/skill:retro` já lista `"what did this command cost"` como frase de
  gatilho, e o título da §What a command's run cost de `session-evidence.md` já promete custo. Os dois
  prometem e nenhum entrega; esta entrega fecha a promessa em vez de abrir assunto.
- **Sobreposição com `add-specs-cycle-run-modes`.** Os dois specs falam de custo do ciclo, e aquele
  spec **nomeia este** em `## Open Decisions` como quem vai medir se o gate pré-merge é o maior item.
  *Fronteira mantida:* este spec entrega **a medição e a política de modelo/effort** — nenhuma chave de
  `specs/config.json` é criada, lida ou presumida aqui. Aquele entrega **a declaração** — onde o
  parâmetro mora e quem o lê. E a resposta que ele espera fica em `## Open Decisions`, explicitamente
  **não decidida** por este spec: o custo das sessões `claude -p` do harness aparece em transcripts
  separados e é invisível nas figuras de D0. Este spec não presume o desenho daquele e não edita o
  arquivo dele.
- **Sobreposição de caminho com `revise-standards-subject-folders`.** O standard novo é declarado em
  `docs/standards/automation/`, uma pasta de assunto que aquele spec pode reorganizar. *Fronteira
  mantida:* o caminho declarado em `## Impact` é o de hoje; se a pasta mudar antes do merge, o caminho
  segue a reorganização e o conteúdo do standard não muda.
- **Sobreposição de caminho com `restructure-claude-front-namespace`.** Aquele spec pode renomear o
  namespace `/skill`, e este toca `commands/skill/retro.md`. *Fronteira mantida:* este spec edita o
  corpo, nunca o nome nem o lugar do arquivo; um rename feito por lá reposiciona a mesma edição.
- ACCEPTED — **custo permanente**: um subcomando a mais em `session.py`, um standard a mais no bundle,
  e uma linha a mais na tabela de model policy. É aceitável porque a reversão é barata e assimétrica:
  `session.py` está fora do lockstep das seis strings (`session.py:16-23`), então remover o subcomando
  não degrada nenhum target, e as linhas de delegação são prosa marcada como **permitida**, então quem
  desconfiar delas simplesmente não delega.
- ACCEPTED — **a medição é de um repo e de um operador**. Os 121 transcripts são todos deste
  repositório, e o perfil de custo de um repo com suíte de teste pesada pode ser outro. É aceitável
  porque a conclusão que a entrega grava não é o número, é a **forma** da conta (`turnos × contexto`) e
  a armadilha do cache, e as duas são propriedades do harness e não deste repo. O número fica
  `background` até rodar em outro lugar.

## Tasks

Serial de ponta a ponta, sem `[P]`: o grupo 1 é um arquivo só, os grupos 2 e 3 dependem do que ele
devolve, e o grupo 4 depende dos três. Provar disjunção de `files:` compraria segundos e custaria um
marcador para manter. Cada texto de checkbox cabe em uma linha, porque `specs.py next` entrega ao
executor a primeira linha e só ela.

### 1. O instrumento

- [ ] 1.1 Somar `message.usage` por comando atribuído em `read_session` e guardar os campos de custo em `Command`
      files: plugins/quenching/assets/bin/session.py
      pattern: plugins/quenching/assets/bin/session.py (os contadores `tools`/`reads`/`touches`, session.py:177 e session.py:299)
      verify: python3 plugins/quenching/assets/bin/session.py selftest
- [ ] 1.2 Devolver custo em `as_dict`, `cmd_list` e `cmd_digest`, com `closed` e `mayIncludeTurnsFrom` aplicados às figuras de custo
      files: plugins/quenching/assets/bin/session.py
      verify: python3 plugins/quenching/assets/bin/session.py list --json 94612f74-3749-491d-a506-c7ed067839e0
- [ ] 1.3 Estender as fixtures embutidas com `usage` e assertar as duas leituras, exata e limite superior, no selftest
      files: plugins/quenching/assets/bin/session.py
      verify: python3 plugins/quenching/assets/bin/session.py selftest  (contagem de fixture records maior que 15, PASS)
- [ ] 1.4 Conferir a soma contra o transcript real da tabela de ## Validation §3, sem tolerância
      files: plugins/quenching/assets/bin/session.py
      verify: ver ## Validation §3

### 2. Os consumidores

- [ ] 2.1 Fazer `/skill:retro` ler e pesar as figuras de custo nos passos 3 e 4, sem crescer a `description` nem ganhar tool grant
      files: plugins/quenching/commands/skill/retro.md
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json  (exit 0)
- [ ] 2.2 Fazer o passo 2 de `/specs:conclude` permitir o coletor de diff read-only com cross-check contra `git diff --stat`, e o passo 7 reportar se delegou
      files: plugins/quenching/commands/specs/conclude.md
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json  (26 commands, sem findings)
- [ ] 2.3 Fazer o passo 5b de `/specs:execute` dizer o que a delegação de executor economiza e quando vale, mantendo o pin no modelo da sessão
      files: plugins/quenching/commands/specs/execute.md
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json  (exit 0)
- [ ] 2.4 Dar à §Delegating an executor de `execution.md` o motivo medido, sem tocar na §This is not `context: fork`
      files: plugins/quenching/assets/references/specs-execute/execution.md
- [ ] 2.5 Acrescentar a linha do coletor à tabela de model policy do README e o motivo medido nas linhas de execute e conclude
      files: plugins/quenching/README.md
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching budget --json  (total não sobe)

### 3. Os standards

- [ ] 3.1 Escrever docs/standards/automation/run-cost.md com a integral, a armadilha do pin, as delegações seguras e a regra do limite superior
      files: docs/standards/automation/run-cost.md, docs/standards/automation/index.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs  (0 error(s))
- [ ] 3.2 Revisar docs/standards/automation/session-evidence.md: apontar a §What a command's run cost para o dono novo, nomear os campos, atualizar o timestamp
      files: docs/standards/automation/session-evidence.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs  (0 error(s), nenhum stale-doc novo)
- [ ] 3.3 Capturar via `/docs:define` a entrada de glossário da integral de custo de run
      files: docs/knowledge/glossary.md

### 4. A prova

- [ ] 4.1 Rodar o conjunto de ## Validation inteiro e registrar a saída de cada comando, com o budget antes e depois
      verify: ver ## Validation
- [ ] 4.2 Medir uma run de conclude sem e com delegação de coleta, decidir a linha de permissão pelo limiar de ~10% e escrever o número medido no standard
      files: docs/standards/automation/run-cost.md, plugins/quenching/commands/specs/conclude.md
      verify: ver ## Validation §7
