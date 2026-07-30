---
slug: stop-develop-offering-follow-up-specs
title: /specs:develop should not offer to create a follow-up spec
verification: per-section
priority: {level: 7, criticality: medium, complexity: 1, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# /specs:develop should not offer to create a follow-up spec

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

Este spec muda **para onde vai um achado que um pass de `/specs:develop` levanta e que não pertence
ao spec que ele está desenvolvendo**.

Hoje o comando oferece criar um spec novo para esse achado. `## Problem` mostra as linhas exatas onde
isso está escrito, e traz a medição desta sessão: um pass autônomo sobre 32 specs levantou bem mais
de cem candidatos, com duplicatas entre agentes que não podiam se ver.

`## Proposal` diz o que passa a ser verdade: o achado é estacionado como uma linha na seção
`## Discoveries` do próprio spec, e quem transforma follow-up em spec continua sendo
`/specs:conclude`. `## Design` explica por que essa linha é barata — a ferramenta e a permissão já
existem, e a seção não altera o stage derivado — e enfrenta de frente a objeção de que isso só adia a
criação do arquivo por um pass. `## Alternatives Considered` mostra as cinco outras formas pesadas,
incluindo simplesmente apagar a oferta e colocar um teto nela, e por que cada uma perdeu.

`## Out of Scope` marca o que fica intocado, em especial a resolução `promoted:`, que é justamente a
saída que impede um achado real de ser perdido. `## Risks` reúne o que a crítica e o premortem
encontraram: o adiamento, o risco de `## Discoveries` virar depósito, o limite da evidência desta
sessão, e as fronteiras com os siblings `reduce-execute-conclude-cost` e `add-specs-cycle-run-modes`.
`## Open Decisions` deixa em aberto duas perguntas que só evidência futura fecha.

Do lado executável: `## Impact` declara o único standard que o trabalho escreve — uma seção nova em
`docs/standards/workflows/plan-lifecycle.md`, estendendo o doc que já é dono do ciclo de vida —
`## Validation` reúne cinco asserções mecânicas de grep e ferramenta e diz o que elas deliberadamente
não provam, e `## Tasks` são cinco itens em três grupos, com os três primeiros obrigados a pousar
juntos.

## Problem

`/specs:develop` encerra um pass oferecendo criar um spec de follow-up para tudo o que acabou
ficando fora do escopo do spec em questão. O invariante do próprio body diz isso literalmente
(`plugins/quenching/commands/specs/develop.md:163-165`): uma regra durável vai para `/docs:add`,
um entendimento para `/docs:learn`, um termo para `/docs:define`, e "an out-of-scope follow-up to
`/specs:create` — **offered, never auto-written**". O passo 5 repete o roteamento
(`develop.md:115-116`) e o passo 8 manda relatar cada routed offer e se foi aceita
(`develop.md:148`).

Esse destino duplica trabalho que `/specs:conclude` já possui. A tabela de harvest da distilação
em `assets/references/specs-conclude/distill.md:20` carrega a linha "a **follow-up** the spec
surfaced but did not pursue → a fresh spec in `specs/plans/` via `/specs:create`", e
`commands/specs/conclude.md:195` nomeia "a follow-up worth its own spec" como um dos quatro
by-products que o pass `done` colhe. A front já tem, portanto, um lugar projetado onde um follow-up
vira spec — e é o lugar onde já se sabe se o spec pai chegou a ser entregue.

**Medição desta sessão.** Este repositório acabou de rodar `/specs:develop` de forma autônoma sobre
os 32 specs abertos, um agente por spec, com a criação de specs proibida — de modo que cada agente
relatou seus follow-ups exatamente como routed offers. O agregado foi de cerca de 4 a 6 offers por
spec: bem mais de cem candidatos a spec de follow-up levantados em um único pass sobre uma front de
32 specs. Vários eram duplicatas entre si: os mesmos defeitos de `specs.py` apareceram de forma
independente em três ou quatro agentes distintos, nenhum deles capaz de ver os outros. É medição
direta do que o mecanismo de offer produz em escala, e do modo de falha que ele carrega — um backlog
inflado por duplicatas que ninguém vai triar.

O custo é cobrado duas vezes: um prompt no fim de cada pass de develop, e specs em `plans/` que
entram na lista ranqueada de `specs.py next --front` (`assets/bin/specs.py:1948-1990`), na tabela de
`/specs:continue` e na leitura de `/specs:triage` antes de qualquer um decidir que valiam a pena.

## Proposal

- Um pass de `/specs:develop` deixa de nomear `/specs:create` como destino de um follow-up fora de
  escopo que ele mesmo levantou.
- Esse achado passa a ser **estacionado como UMA linha de `## Discoveries`** no próprio spec sendo
  desenvolvido, via `specs.py discover`, dentro da mesma edição de uma confirmação que o bank já
  produz — nada é perdido e nenhum arquivo novo é criado.
- `/specs:conclude` continua sendo o único lugar onde um follow-up vira spec, sem nenhuma alteração:
  a linha de harvest em `distill.md:20` fica exatamente como está.
- O discoveries bank mantém a resolução `promoted:` e ganha um passo de deduplicação: quando já
  existe em `specs/plans/` um spec que cobre a linha, ela resolve como
  `dismissed: already covered by {slug}` em vez de mintar um segundo arquivo.
- O `## Invariants` de `develop.md` passa a carregar uma guarda explícita — dentro de um pass de
  develop, `specs.py new` só roda como a resolução `promoted:` do discoveries bank.
- A rota de mudança de intenção (`develop.md:65`) mantém `/specs:create`, porque um humano pedindo
  agora um spec diferente não é um follow-up especulativo.
- `docs/standards/workflows/plan-lifecycle.md` passa a declarar em que momento do ciclo de vida um
  follow-up vira spec, para que uma reescrita futura de `develop.md` não reintroduza a offer.

## Out of Scope

- **A linha de harvest de `/specs:conclude`** (`assets/references/specs-conclude/distill.md:20` e o
  passo 5 de `commands/specs/conclude.md`) — é o lugar projetado para isso, no momento em que já se
  sabe se o spec pai foi entregue. Nada nele muda.
- **A resolução `promoted:` do discoveries bank** (`questions.md:273`) — ela resolve uma linha que JÁ
  está em disco, então seu custo é limitado pelo tamanho da fila e não pelo que o pass imagina.
  Removê-la deixaria um achado real com apenas `folded:` ou `dismissed:` disponíveis, que é
  exatamente a perda que este spec existe para evitar.
- **As três rotas `/docs:*` do mesmo invariante** (`/docs:add`, `/docs:learn`, `/docs:define`) — uma
  regra durável não tem equivalente barato de estacionamento, e escrever em `docs/` durante a
  definição é proibido por outro motivo. Ficam como estão; a unificação está em `## Open Decisions`.
- **A rota de mudança de intenção** (`develop.md:65`) — ali o humano está pedindo, agora, algo que
  reescreveria um spec já acordado. A alternativa a um spec novo é reescrever o existente, que é o
  dano. Continua apontando para `/specs:create`.
- **`specs.py` e qualquer código de ferramenta** — a mudança é inteiramente command body, arquivo de
  reference e um standard. `specs.py discover` já faz o necessário, inclusive criar `## Discoveries`
  quando a seção está ausente (`assets/bin/specs.py:2144-2158`), e `develop.md:4` já libera
  `Bash(python3:*)`.
- **Um bump de versão** — `docs/standards/ci-cd/versioning-release.md` §When the bump happens proíbe
  bump como task; ele acontece em `/specs:conclude` passo 5, na work branch, antes do merge.
- **Podar retroativamente as offers desta sessão** — elas foram relatadas, nunca escritas. Não há
  arquivo para remover.
- **Uma varredura de duplicatas na front inteira** — território de `/specs:triage`. As duplicatas
  medidas nesta sessão estavam em relatórios, não em arquivos.
- **A linha 181 de `assets/specs/QUENCHING.md`**, que narra o discoveries bank com apenas duas
  resoluções ("promote to its own spec, or dismiss with a reason") e omite `folded:`. É defeito
  pré-existente do manual do operador, independente desta mudança, relatado como achado separado.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/workflows/plan-lifecycle.md` — em que momento do ciclo de vida um follow-up vira
  spec: um pass de definição estaciona, `/specs:conclude` minta. Inclui a dependência de que
  `## Discoveries` preenchida não é gatilho de stage.

O doc **já existe** e é o dono declarado de "onde um spec vive ao longo da vida, quais estados são
computados e quais fatos são registrados". A crítica adversarial perguntou se três edições de body
justificam um standard; a resposta é que o modo de falha temido é uma reescrita futura de
`develop.md` reintroduzir a offer, e um invariante em um único body é uma guarda mais fraca que uma
regra de ciclo de vida. Mas a task **estende o doc existente e não minta um novo** — abrir um segundo
dono para "qual momento do ciclo faz o quê" seria o defeito de segundo nome que
`docs/standards/naming/command-surface.md` proíbe.

### Standards em `authority: background` que este spec pode resolver

- none — nenhum standard em `background` cobre roteamento de achado fora de escopo; a seção nova
  nasce `authority: current`, porque os bodies que ela descreve entram no mesmo branch e a provam.

### Código de produto que este spec espera tocar

Neste repositório, command body é código-fonte (`CLAUDE.md` §Operating this repo).

- `plugins/quenching/commands/specs/develop.md` — o `## Invariants` (linhas 163-165), o passo 5
  (115-116) e a lista de escritas do passo 6 (122-127)
- `plugins/quenching/assets/references/specs-develop/questions.md` — a linha `promoted:` da tabela de
  resoluções do discoveries bank (273)
- `docs/standards/workflows/plan-lifecycle.md` — a seção nova mais o `timestamp:`

Não tocados de propósito: `assets/bin/specs.py`, `assets/specs/schema.json`,
`assets/references/specs-conclude/distill.md`, `commands/specs/conclude.md` e os seis artefatos do
lockstep de versão.

## Validation

Nada aqui é testável por execução: a mudança é prosa que uma sessão futura de Claude executa. As
asserções abaixo são todas mecânicas, e o rodapé diz o que elas deliberadamente **não** provam.

**A partir de `plugins/quenching/`:**

```bash
# 1. develop.md nomeia /specs:create em exatamente DUAS linhas: a fronteira do frontmatter
#    (linha 2, "Not for: creating a spec") e a rota de mudança de intenção (linha 65).
#    A rota de follow-up do ## Invariants não aparece mais.
grep -c 'specs:create' commands/specs/develop.md          # 2

# 2. o destino substituto está escrito no body
grep -n 'specs.py discover' commands/specs/develop.md      # pelo menos 1 hit

# 3. a guarda contra reintroduzir a offer existe
grep -n 'specs.py new' commands/specs/develop.md           # pelo menos 1 hit, no ## Invariants

# 4. a deduplicação entrou na resolução promoted:
grep -n 'already covered by' assets/references/specs-develop/questions.md   # 1 hit

# 5. a superfície de comandos continua conformante
python3 assets/bin/skills.py --root . doctor --json        # 26 commands, no findings
python3 assets/bin/skills.py --root . lint --json          # exit 0
```

**A partir da raiz do repositório**, para o standard:

```bash
python3 plugins/quenching/assets/hooks/okf-validate.py docs   # 0 error(s), 0 warning(s)
python3 plugins/quenching/assets/bin/specs.py validate --json  # sem finding novo neste spec
```

**Invariantes que devem continuar valendo:**

- `assets/references/specs-conclude/distill.md` e `commands/specs/conclude.md` byte-identical —
  `git diff --stat` no branch não pode listar nenhum dos dois.
- As três resoluções do discoveries bank continuam sendo `promoted:`, `folded:` e `dismissed:`. A
  deduplicação usa `dismissed:` e não introduz um quarto token.
- `assets/specs/schema.json` intocado: `## Discoveries` continua fora de qualquer regra de stage.

**O que isto não prova, deliberadamente.** Nenhuma dessas asserções verifica que a superfície
*carrega* nem que uma sessão futura obedece à regra nova — isso é território de
`assets/bin/functional-checks.sh`, que por `CLAUDE.md` §Operating this repo pertence à front de skill
e **não entra** em `## Validation` de spec nem em `verify:` de task, porque cada check é uma sessão de
agente cobrada. Se alguém quiser essa medição, o caminho é `/skill:new` depois de a mudança pousar.

## Design

### O alvo é o destino da offer, não uma auto-criação

`develop` **não** cria specs sozinho hoje: o invariante em `develop.md:164-165` já diz "offered,
never auto-written". Logo, não existe auto-criação para remover — o título do spec descreve a
*offer*, e a decisão real é sobre o **destino** dela.

Mas `develop` tem **dois** caminhos que produzem specs, e o `## Problem` os confundia:

| Caminho | Onde | O que faz | Custo limitado por |
| --- | --- | --- | --- |
| a routed offer do passo 5 | `develop.md:115-116`, `163-165` | apenas *nomeia* `/specs:create` no relatório | nada — dispara sobre tudo o que o pass *notou* |
| a resolução `promoted:` | `questions.md:273` | roda `specs.py new` e grava o slug de volta na linha | o número de linhas não resolvidas em disco |

Só o primeiro muda. O segundo resolve um achado que **já está registrado**, com procedência
preservada e a decisão paga em lote — que é o desenho da front, não um defeito dele.

### O destino substituto é uma linha de `## Discoveries`

Uma offer removida sem nada no lugar perde o achado, e essa perda é pior que o backlog inflado: um
"não" ao prompt de hoje não deixa registro nenhum. Estacionar deixa. Quatro fatos verificados fazem
disso a opção barata:

1. `develop.md:4` já declara `allowed-tools: Read, Grep, Glob, Edit, Bash(python3:*), Bash(py:*),
   AskUserQuestion` — nenhuma mudança de frontmatter é necessária para chamar `specs.py discover`.
2. `specs.py discover` cria `## Discoveries` quando a seção está ausente
   (`assets/bin/specs.py:2144-2158`), então não há pré-requisito de scaffolding.
3. Uma `## Discoveries` preenchida **não move o stage derivado**. Em `assets/specs/schema.json`
   §stages, `executing` dispara em `anyOf: [taskState [x, !], filled: [Handoff]]` e em nada mais —
   estacionar um achado não faz o spec se reportar errado em `/specs:continue`, `/specs:status` ou
   `plans/index.md`.
4. É exatamente o mecanismo que `/specs:execute` já usa para tudo o que o trabalho revela e que
   nenhuma task nomeou (`commands/specs/execute.md:134` e `:237`). `develop` passa a copiar um
   padrão existente em vez de introduzir um novo.

### O adiamento é o ganho, não um efeito colateral

A objeção mais forte contra esta forma: estacionar não elimina o `specs.py new`, apenas o adia um
pass — porque o discoveries bank roda **primeiro** em qualquer stage (`develop.md:89-90`,
`questions.md:34`) e vai cobrar a resolução da linha. Está correto, e o adiamento compra três coisas
concretas:

- **Decisão em lote.** A linha é julgada contra todas as outras linhas não resolvidas, não uma por
  vez no fim de um pass em que o pass acabou de gerar o máximo de ideias novas.
- **`folded:` se torna possível.** Quando o pass seguinte roda, a forma do spec pai já assentou, e
  boa parte do que parecia "fora de escopo" cabe numa seção que ainda não existia quando o achado
  apareceu. A offer do passo 5 nunca oferece essa saída.
- **`dismissed: {reason}` se torna um resultado registrado.** Recusar a offer de hoje é um descarte
  silencioso e sem rastro; `dismissed:` mantém o achado e o motivo na procedência.

### A deduplicação fica onde a duplicata custa um arquivo

Estacionar uma linha duplicada custa uma linha; mintar um spec duplicado custa um arquivo que entra
na fila ranqueada de todo mundo. Por isso o grep de deduplicação entra na resolução `promoted:`, e
não no momento de estacionar — e ele não precisa de vocabulário novo: uma linha já coberta por um
spec existente resolve como `dismissed: already covered by {slug}`, dentro das três resoluções que
`questions.md` já permite.

### Contratos vinculantes que o desenho não pode contradizer

- `docs/standards/workflows/plan-lifecycle.md` — frontmatter registra julgamento humano e o resto é
  derivado. Uma linha estacionada não escreve nenhum record e não move nenhum stage; a mudança é
  compatível por construção.
- `docs/standards/ci-cd/versioning-release.md` §When the bump happens — bump nunca é task. Nenhuma
  task deste spec toca as seis versões.
- `CLAUDE.md` §Operating this repo — `functional-checks.sh` pertence à front de skill e
  **explicitamente não entra** em `## Validation` de um spec nem em `verify:` de uma task. Por isso
  `## Validation` usa `skills.py`, greps e `okf-validate.py`.
- `assets/references/specs-develop/questions.md` §The four shared mechanics, item 2 — nada é escrito
  no meio de um bank. Estacionar é uma escrita, então precisa entrar na edição consolidada do bank
  (passo 6 de `develop.md`), nunca como uma chamada solta no meio do passo 4.

### Uma analogia, não uma dependência

`/specs:align` relata ações de autoria com o comando que fecha cada uma, em vez de executá-las, e
`assets/references/align/convergence.md:113-138` chama isso de anti-fabrication boundary. O mesmo
instinto — não fabricar artefato a partir do que a sessão apenas notou — é o que este spec aplica um
nível abaixo. É analogia: `/specs:develop` não é stage de align nenhum, então nada aqui depende
daquela regra.

## Alternatives Considered

Seis formas inteiras foram pesadas. A escolhida é a 2.

| # | Forma | Custo | Ganho | Por que perdeu |
| --- | --- | --- | --- | --- |
| 1 | **Não fazer nada** — manter a offer | zero | zero | Deixa em pé o backlog duplicado que esta sessão mediu: cerca de 4 a 6 offers por spec sobre 32 specs, com os mesmos defeitos de `specs.py` levantados por três ou quatro agentes independentes. |
| 2 | **Estacionar como linha de `## Discoveries`; `conclude` continua mintando** | três edições de body e um standard | O achado sobrevive registrado, nenhum arquivo é criado, a decisão vira lote, `folded:` e `dismissed:` passam a existir como saídas | **Escolhida.** |
| 3 | **Remover a frase de roteamento e não dizer nada** sobre achados fora de escopo | uma edição | a menor mudança possível | Perde o achado em silêncio — o modo de falha exato que o mecanismo de `## Discoveries` existe para evitar. Um pass sem destino declarado volta a inventar um. |
| 4 | **Manter a offer com um teto** de N por pass | uma edição | limita o volume | Derruba achados em silêncio depois do N-ésimo e não dá nenhuma regra sobre *quais* N sobrevivem. Trocar "duplicatas demais" por "perdas arbitrárias" não é melhoria. |
| 5 | **Deduplicar antes de oferecer**, mantendo `/specs:create` como destino | uma edição em `develop.md` mais o grep | mata a duplicata na origem | Mantém o custo de um arquivo por achado, e um spec nascido no meio do develop do pai frequentemente não pode ser construído antes de o pai fechar. A ideia do grep foi **adotada**, movida para a resolução `promoted:`, onde a duplicata realmente custa um arquivo. |
| 6 | **Um arquivo de estacionamento próprio** (algo como `specs/plans/ideas.md`) | um artefato novo | separa follow-ups de discoveries de execução | Artefato fora do conjunto canônico, sem dono, sem stage e sem gate — `specs.py validate` o trataria como stray. E `## Discoveries` já É o estacionamento da front, com procedência amarrada ao spec que produziu o achado. |

## Open Decisions

- **As três rotas `/docs:*` do mesmo invariante devem receber a mesma regra de estacionamento?** Uma
  regra durável levantada no meio de um develop também poderia virar linha de `## Discoveries` — e o
  momento emergent de `/specs:conclude` já colhe linhas de discovery para dentro de `docs/`
  (`distill.md` §Two moments). *Como se decide:* pela leitura da task 1.1 depois de escrita. Se o
  invariante reescrito ficar natural com as quatro rotas divididas duas a duas, fica assim; se a rota
  de follow-up ler como caso especial pregado no meio de uma lista uniforme, a unificação vira um
  spec de follow-up seu — que, por este próprio spec, nasce estacionado como linha de
  `## Discoveries`.

- **A deduplicação também deve rodar no momento de estacionar, e não só em `promoted:`?** A task 1.3
  a coloca apenas onde a duplicata custa um arquivo. *Como se decide:* por medição, e existe um
  experimento barato — um segundo pass autônomo sobre a front. Se as linhas estacionadas por agentes
  paralelos duplicarem entre si de forma perceptível em `specs.py status`, o grep sobe também para o
  momento de estacionar. A medição desta sessão não responde isso: os agentes relataram offers em
  relatórios separados, então nenhum deles teve a chance de encontrar a linha do outro em disco.

## Risks

- **A criação do spec é adiada, não eliminada.** O discoveries bank roda primeiro em qualquer stage
  (`develop.md:89-90`), então a linha estacionada cobra sua resolução no pass seguinte, e
  `promoted:` ainda custa um `specs.py new`. *Mitigação:* o ganho não é a eliminação e sim o lote —
  ver `## Design` §O adiamento é o ganho. A deduplicação da task 1.3 ataca diretamente o modo de
  falha medido, e `folded:` e `dismissed:` só existem nesse momento posterior.

- **`## Discoveries` deixa de ser uma seção só de execução.** Hoje ela nasce durante
  `/specs:execute`; estacionar a faz nascer também durante a definição, e um spec que ninguém volta
  a desenvolver mantém suas linhas para sempre. *Mitigação:* a regra de estacionamento precisa
  manter a **mesma barra** da offer que substitui — só o que o pass teria oferecido, não tudo o que
  notou. Um teto foi considerado e rejeitado (`## Alternatives Considered` #4) porque derruba achados
  em silêncio. **ACCEPTED —** uma linha esquecida custa uma linha; a alternativa de hoje é um arquivo
  esquecido na fila ranqueada de todo mundo.

- **A evidência desta sessão não estabelece a taxa do dia a dia.** As 4 a 6 offers por spec vieram de
  um pass autônomo, de 32 specs de largura, com a resposta das perguntas delegada ao agente. Um pass
  interativo sobre um spec produz muito menos. *Mitigação:* a decisão não depende do número — uma
  linha estacionada é mais barata que um spec oferecido em **qualquer** taxa, então a mudança é
  segura sob as duas hipóteses. **ACCEPTED —** a medição limita o teto e demonstra o modo de
  duplicata; não é usada para nada além disso.

- **Um pass parcialmente aplicado é pior que o estado atual.** Se a task 1.1 entra (invariante
  reescrito) e a 1.3 não (tabela do bank intocada), `develop` passa a estacionar linhas e o
  discoveries bank continua mintando um spec por linha sem deduplicar — o mesmo achado custando uma
  linha **e** um arquivo. *Mitigação:* 1.1, 1.2 e 1.3 estão no **mesmo grupo de tasks**, e
  `verification: per-section` faz a verificação rodar depois do grupo inteiro, não no meio dele.

- **Uma reescrita futura de `develop.md` reintroduz a offer.** É o motivo pelo qual o spec escreve um
  standard em vez de confiar em um invariante de body. *Mitigação:* task 2.1, mais a guarda explícita
  da task 1.1.

- **Uma mudança futura de schema poderia transformar `## Discoveries` em gatilho de stage.** Hoje não
  é (`schema.json` §stages), e a mudança depende disso; se algum dia virar, todo spec com linha
  estacionada passaria a se reportar adiantado. *Mitigação:* a task 2.1 registra essa dependência no
  standard, para que quem edite `schema.json` a veja. Adjacência com o sibling
  `name-the-scaffolded-stage`, que mexe em nomenclatura de stage — este spec não assume nada sobre o
  resultado dele e não toca `schema.json`.

- **Sobreposição com `reduce-execute-conclude-cost`.** Aquele spec reavalia o custo dos runs de
  `/specs:execute` e `/specs:conclude`; este remove um prompt de `/specs:develop` e **aumenta** de
  leve o que `/specs:conclude` colhe, ao concentrar nele a criação de follow-ups. *Fronteira que este
  spec mantém:* não altera nenhuma etapa de `conclude` — `distill.md:20` e o passo 5 de `conclude.md`
  ficam byte-identical (`## Out of Scope`). Se aquele spec reduzir a distilação, a decisão é dele, e
  este não a antecipa.

- **Sobreposição com `add-specs-cycle-run-modes`.** Run modes customizáveis para os comandos do ciclo
  poderiam expressar "estacione" contra "ofereça" como modo em vez de como regra fixa. *Fronteira que
  este spec mantém:* decide o comportamento **padrão** de `develop` e não introduz nenhum flag, modo
  ou opção. Se `add-specs-cycle-run-modes` acabar tornando isso configurável, ele configura o padrão
  que este spec estabelece. Nenhum dos dois resolve o outro.

- **Permanência e reversibilidade.** O custo permanente é uma linha de invariante e uma instrução na
  tabela de resoluções, ambas em bodies já lidos a cada pass — custo por invocação, não always-on
  (`docs/standards/automation/context-budget.md` governa descrição, não body) — e em troca um prompt
  desaparece. Desfazer é um `git revert` de um merge: três edições de body e uma seção de standard,
  nada gerado, nenhum layout de arquivo, nenhuma constante de versão.

- **A suposição que sustenta o spec.** Que uma linha estacionada será revisitada. Se ninguém rodar
  `develop` naquele spec de novo, o achado fica parado — tão morto quanto uma offer que ninguém
  aceitou, com a diferença de estar registrado. **ACCEPTED —** o piso do benefício é "o registro
  sobrevive", e esse piso já é melhor que hoje.

**Duas histórias de premortem não converteram em nada e foram descartadas, conforme
`questions.md` §Lens: premortem.** (1) "O spec assumiu algo falso sobre o código": as duas suposições
foram verificadas — `Bash(python3:*)` já está em `develop.md:4` e `## Discoveries` não move o stage
derivado. (2) "Alguém não conseguiu usar o resultado": nada aqui toca `specs.py`, e body e reference
viajam juntos no mesmo plugin, então não existe drift de cópia instalada.

## Tasks

Política do spec: `verification: per-section` — as três tasks do grupo 1 precisam pousar juntas
(`## Risks`, história do pass parcial), então a verificação roda depois do grupo, nunca no meio dele.

Cada task abre com uma primeira linha completa: é só ela que `specs.py next` entrega a um executor.

### 1. A regra de parking

- [ ] 1.1 Trocar a rota de follow-up do `## Invariants` de `develop.md` por estacionar em `## Discoveries`
      Onde hoje se lê `an out-of-scope follow-up to /specs:create — offered, never auto-written`,
      passa a ler: estacionar o achado como uma linha de `## Discoveries` no spec sendo desenvolvido,
      via `specs.py discover`. Adicionar na mesma lista a guarda de que, dentro de um pass de develop,
      `specs.py new` só roda como a resolução `promoted:` do discoveries bank. Manter intactas as três
      rotas `/docs:*` da mesma linha e a rota de mudança de intenção da linha 65.
      files: plugins/quenching/commands/specs/develop.md
      verify: grep -c 'specs:create' plugins/quenching/commands/specs/develop.md  →  2
- [ ] 1.2 Fazer o estacionamento pousar dentro da edição de uma confirmação, nos passos 5 e 6 de `develop.md`
      No passo 5, a frase que lista `a durable rule, a term, a follow-up` como routed offer passa a
      tratar o follow-up como linha a estacionar. No passo 6, incluir a chamada `specs.py discover` na
      lista de escritas, para que o estacionamento nunca aconteça solto no meio do passo 4 — mecânica
      2 de `questions.md` proíbe qualquer escrita no meio de um bank.
      files: plugins/quenching/commands/specs/develop.md
      verify: grep -n 'specs.py discover' plugins/quenching/commands/specs/develop.md  →  1 hit ou mais
- [ ] 1.3 Acrescentar o passo de deduplicação à linha `promoted:` da tabela de resoluções em `questions.md`
      Antes de mintar, procurar em `specs/plans/` um spec que já cubra a linha; havendo match, a linha
      resolve como `dismissed: already covered by {slug}`. Sem token novo — continuam sendo as três
      resoluções `promoted:`, `folded:` e `dismissed:`.
      files: plugins/quenching/assets/references/specs-develop/questions.md
      verify: grep -n 'already covered by' plugins/quenching/assets/references/specs-develop/questions.md  →  1 hit

### 2. O standard

- [ ] 2.1 Escrever em `docs/standards/workflows/plan-lifecycle.md` a seção do momento em que um follow-up vira spec
      A regra: um pass de definição estaciona, `/specs:conclude` minta. Citar as linhas de
      `develop.md` e `questions.md` alteradas no grupo 1, e registrar a dependência de que
      `## Discoveries` preenchida não é gatilho de stage em `assets/specs/schema.json`.
      `authority: current`, `timestamp` atualizado, `resource:` derivado dos anchors reais. Estender o
      doc existente — não mintar doc novo.
      files: docs/standards/workflows/plan-lifecycle.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs  →  0 error(s), 0 warning(s)

### 3. Verificação

- [ ] 3.1 Rodar o bloco inteiro de `## Validation` e conferir cada número esperado
      Inclui os invariantes de que `distill.md`, `conclude.md` e `schema.json` não aparecem em
      `git diff --stat`.
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json && python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json
