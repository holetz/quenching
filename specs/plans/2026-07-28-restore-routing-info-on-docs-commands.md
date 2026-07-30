---
slug: restore-routing-info-on-docs-commands
title: Restore trigger phrases and boundaries on the nine bare /docs:* descriptions
verification: per-task
priority: {level: 2, criticality: high, complexity: 4, date: 2026-07-29}
refined: {mode: adversarial, date: 2026-07-30}
---

# Restore trigger phrases and boundaries on the nine bare /docs:* descriptions

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

Nove das onze descrições de comando `/docs:*` e `/skill:*` perderam suas frases-gatilho entre
aspas e a cláusula de fronteira `Not for:` quando a superfície de comandos foi colapsada em um
arquivo por ponto de entrada, então um pedido em linguagem simples como "write this down in the
docs" não tem nada que o separe de `/docs:add`, `/docs:learn`, `/docs:define` ou `/docs:import`.
`## Proposal` restaura as três partes de uma descrição conformante — conceito, gatilhos, fronteira
— reaproveitando fraseado que já existe em outros pontos do repo em vez de inventar texto novo, e
`## Design` exige que todas as onze descrições sejam rascunhadas como uma única tabela de alocação,
revisada contra colisões, antes de qualquer arquivo ser editado. Restaurá-las empurra a superfície
além do seu teto de caracteres always-on, que tem zero folga por construção, então `## Tasks` roda
em ordem fixa: escrever as descrições, depois re-medir o teto a partir de uma execução real e
transcrever esse número para todos os lugares onde ele vive, depois subir a versão de release.
`## Open Decisions` sinaliza que a aprovação está retida no momento: um spike ainda aberto sobre
`disable-model-invocation` pode tornar toda esta restauração desnecessária, ou confirmá-la e
multiplicar seu custo por cerca de dez vezes quando a superfície crescer como planejado. E
`## Risks` registra que a linha de base já derivou por conta própria: medido em 2026-07-30, antes
de esta spec somar um caractere, `budget` reporta 12,875 contra um teto de 12,726 e sai 1.

## Problem

O colapso em um arquivo por ponto de entrada apagou a metade de cada par que carregava as
frases-gatilho entre aspas e a fronteira `Not for:`. Restaurá-las foi julgado barato, e aconteceu —
em `/specs:*` e na maior parte de `/skill:*`. Nunca chegou a `/docs:*`.

Medido na `main` em 4.1.0, `skills.py lint` reporta `sk-trigger-position` **e** `sk-no-boundary` em
nove dos onze comandos `/docs:*`: `add`, `define`, `documentation:build`, `glossary-backfill`,
`harness`, `import`, `import-memory`, `learn`, `status`. Somente `/docs:align` carrega uma descrição
completa. `/skill:eval` carrega as duas findings também, e `/skill:new` carrega
`sk-trigger-position` — ou seja, o comando que mede roteamento e o comando que cunha comandos estão
eles mesmos entre os menos roteáveis da superfície.

As duas são warnings, então a superfície reporta limpa enquanto a informação de roteamento está
ausente do único texto que está sempre em contexto. Um usuário que diz "capture this thought" chega
em `/specs:create` porque aquela descrição cita a frase; um usuário que diz "write this down in the
docs" não tem nada para onde rotear.

**A restrição que faz disto uma spec e não uma edição.** O teto always-on **não tem folga por
construção** — ele é igual ao total corrente da superfície. Marcava 11,565 quando isto foi
capturado; marca **12,726** hoje, porque o ratchet disparou em 2026-07-28, quando `/specs:isolate`
se tornou o 25º comando e um humano re-mediu. Restaurar as descrições ausentes vai cruzá-lo de
novo, e cruzar é o sinal funcionando, não uma falha: força um re-ajuste medido em vez de uma
expansão sem preço. Então esta spec precisa comprar a informação de roteamento e re-medir o teto a
partir de uma execução, nessa ordem, e declarar os dois números.

Descoberto por `instrument-and-extend-skill-front` (território da tarefa 3.x, registrado no seu
`## Discoveries` como dois comandos) e re-medido durante o seu conclude, onde acabou sendo onze.

## Proposal

Todo comando da superfície carrega as três partes que
[context-budget.md](/docs/standards/automation/context-budget.md) §What the description may carry
já chama de obrigatórias — o conceito à frente, frases-gatilho entre aspas na **segunda** frase, e
uma fronteira `Not for: {trabalho adjacente} → {comando dono}` — e o teto de superfície inteira é
re-medido **a partir de uma execução** depois, nessa ordem.

**Onze descrições, não nove.** O título nomeia as nove `/docs:*` nuas que motivaram a spec. O
escopo decidido durante a modelagem é *todo comando que reporta qualquer um dos dois códigos*, o
que acrescenta `/skill:eval` (os dois códigos) e `/skill:new` (`sk-trigger-position` apenas — ele já
carrega uma fronteira). Isso faz do estado final um absoluto verificável em vez de uma lista de
arquivos melhorados: `skills.py lint` reporta **zero** `sk-trigger-position` e **zero**
`sk-no-boundary` nos 25 comandos.

**O que isto compra — declarado mais estreitamente do que `## Problem` declarou.** Não é
"roteamento agora funciona". Um rótulo nu já roteia um pedido claramente formulado:
`functional-checks.sh`, probe c, dispara
`"add a standard: we always use snake_case for database columns"` → `quenching:docs:add` contra uma
descrição de 76 caracteres, e as três probes faladas do colapso sobreviveram todas. O que onze
rótulos nus não conseguem fazer é **discriminar**. "Write this down in the docs" tem que escolher
entre `/docs:add`, `/docs:learn`, `/docs:define` e `/docs:import`, e nada em um rótulo de menu `/`
responde isso — a cláusula `Not for:` é o único texto que responde, e é a parte que a truncagem come
primeiro. Então a afirmação é: *a informação de roteamento que o padrão exige está presente,
alocada sem colisão, e à prova de truncagem.* Se o roteamento melhorou de forma mensurável é uma
pergunta should-trigger/should-not-trigger que esta spec deliberadamente não responde — ver
`## Out of Scope`.

**O que custa, e por que esse custo é a spec e não uma edição.** As onze descrições somam 935
caracteres hoje. Na faixa de 400–650 que `## Design` fixa, elas chegam perto de 5,450, levando a
superfície de 12,726 para cerca de **17,200** (~4,300 tokens aproximados, saindo de ~3,182). Isso
cruza `DEFAULT_CEILING`, que é igual ao total corrente por construção, então `skills.py budget` sai
1 com `sk-budget-ceiling`. **Isso é o ratchet funcionando, não uma regressão** — e esta spec é o seu
**segundo** disparo e o primeiro causado por *crescimento de descrição* em vez de por um comando
novo sendo cunhado, que é um fato sobre o mecanismo que o padrão ainda não registra.

O re-ajuste é portanto uma parte declarada desta spec, não contabilidade descoberta no fim: a nova
cifra é transcrita do que `budget` imprimiu para os três lugares que a guardam —
`DEFAULT_CEILING` em `skills.py`, `context-budget.md` e `README.md` — e nunca estimada. Todo número
acima, exceto os dois medidos (935 e 12,726), é uma estimativa, e a spec está pronta quando a
execução os tiver substituído.

## Out of Scope

- **Provar que os gatilhos restaurados de fato roteiam.** Isso é uma medição should-trigger /
  should-not-trigger, de responsabilidade de `/skill:eval` contra uma fixture de eval por comando —
  e `assets/evals/` guarda exatamente três conjuntos de casos hoje (`skill/agent/new`,
  `skill/hook/new`, `specs/capture`), nenhum deles na front `docs`. Construir nove fixtures e rodar
  cada uma duas vezes em sub-agentes isolados é um trabalho maior que a restauração em si, e
  [context-budget.md](/docs/standards/automation/context-budget.md) §What the collapse measured é
  explícito que baixo custo e roteabilidade são perguntas independentes. Esta spec fecha a lacuna
  de conformidade; a medição é um follow-up, e até ela rodar nenhuma afirmação de roteamento
  melhorado é feita em lugar algum desta spec.
- **Acrescentar probes de discriminação em `functional-checks.sh`.** O instrumento barato natural —
  uma probe afirmando que `"write this down in the docs"` chega em `/docs:learn` e não em
  `/docs:add` — está bloqueado duas vezes: cada probe custa uma sessão `claude -p` nova, e o script
  não consegue decodificar a própria evidência nesta plataforma de jeito nenhum
  (`fix-functional-checks-encoding`). Postergado até aquela spec aterrissar.
- **Dar a `skills.py lint` uma forma de falhar em cima de um código de warning selecionado.**
  `lint` sai 0 em warnings, então todo consumidor que quer que um warning quebre um build precisa
  filtrar o `--json` por conta própria — incluindo todo `verify:` no `## Tasks` desta spec. Um par
  `--code X --fail-on warn` resolveria isso de vez, e não decorre do `## Problem` desta spec. O
  filtro inline em `## Design` não custa nada e funciona hoje; a flag é um follow-up.
- **Os outros três códigos de lint.** `sk-step-criterion` (9 comandos), `sk-unscoped-bash` (5) e
  todo defeito de nível de corpo ficam intocados. São trabalho de corpo; esta spec edita **somente**
  valores de `description` no frontmatter, mais três transcrições de um número.
- **Mudar o ratchet de folga zero.** `context-budget.md` §The ratchet fired exactly as predicted já
  precifica a forma — todo re-ajuste é uma mudança de contabilidade em três arquivos — e a escolhe
  deliberadamente. Re-litigar isso é uma spec própria; esta paga o preço e registra um segundo ponto
  de dado sobre quando o ratchet dispara.
- **A renomeação `/skill` → `/automation`.** `restructure-claude-front-namespace` (stage `designed`)
  move `/skill:new` → `/automation:command:new`, `/skill:eval` → `/automation:command:eval` e
  `/docs:harness` → `/automation:harness:align`, e reescreve toda citação de caminho movido em
  `commands/**`. Nada aqui antecipa isso: as descrições são escritas para os caminhos que existem
  hoje, e a própria tarefa de citação daquela spec cobre as cláusulas de fronteira de qualquer forma
  — ver `## Risks`.
- **Reescrever o `README.md`.** Só as três linhas que transcrevem a cifra do teto mudam.
  `rewrite-readme-for-collapsed-surface` é dono do resto daquele arquivo.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/automation/context-budget.md` — o teto re-medido em §The per-surface ceiling e na
  amostra de `breakdown`, mais uma **terceira** entrada no histórico do ratchet: o primeiro disparo
  causado por crescimento de descrição em vez de por um comando novo sendo cunhado. Seu `timestamp`
  passa para a data do build, ou o doc dispara `stale-doc` no seu próprio recurso `commands/**`.

### Padrões em `authority: background` que esta spec pode resolver

- none — `context-budget.md` é `authority: background` e esta spec **não** o gradua. A condição
  declarada por ele mesmo é uma medição neste plugin mais pelo menos dois repos adotantes, e ele
  exclui exatamente o que esta spec acrescenta: "a bigger number from the same repo is still one
  repo."

### Código de produto que esta spec espera tocar

- `plugins/quenching/commands/docs/{add,define,glossary-backfill,harness,import,import-memory,learn,status}.md`
  e `commands/docs/documentation/build.md` — o valor de `description` no frontmatter **apenas**;
  nenhuma linha de corpo muda.
- `plugins/quenching/commands/skill/{new,eval}.md` — o mesmo, e os únicos arquivos fora da front
  `docs`.
- `plugins/quenching/assets/bin/skills.py` — `DEFAULT_CEILING` e seu comentário de changelog datado
  (a constante é a casa do teto; os dois docs a transcrevem).
- `plugins/quenching/README.md` — as três linhas que carregam a cifra, e nada mais.
- `plugins/quenching/VERSION`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, e a
  constante `VERSION` nos três scripts distribuídos — o release lockstep, porque o comportamento de
  um script distribuído muda.

**Nada em um repo alvo muda de forma.** Nenhum artefato instalado é reescrito, nenhuma migração
roda, e um adotante vê isto só como um upgrade de plugin. O custo always-on, no entanto, cai em toda
sessão de todo repo que o instala — que é justamente o motivo de precificá-lo aqui em vez de
descobri-lo depois.

## Validation

Todos os comandos rodam a partir de `plugins/quenching/`. Toda checagem é determinística e local; a
única que não é (**V7**) é declarada condicional em vez de descartada. `## Tasks` cita estas por id.

**V1 — os dois códigos alvo desapareceram, em toda a superfície.** Precisa imprimir nada e sair 0.
Checar só o código de saída de `lint` não prova nada: os dois códigos são `severity: warn`, e `lint`
retorna `"ok": true` com eles presentes (medido em `commands/docs/add.md`, saída 0). O filtro é a
checagem.

```bash
python3 assets/bin/skills.py --root . lint --json | python3 -c "import json,sys; \
B=[f for f in json.load(sys.stdin)['findings'] \
   if f['code'] in ('sk-trigger-position','sk-no-boundary')]; \
[print(f['code'], f['command']) for f in B]; sys.exit(1 if B else 0)"
```

**V2 — fechá-los não estourou um cap.** Mesma forma, códigos `sk-metadata-cap` (error, 1,536) e
`sk-description-portable` (warn, 1,024). Precisa imprimir nada e sair 0. A faixa de 400–650
significa que isto nunca deveria chegar perto; se disparar, uma descrição está carregando *como
funciona*.

**V3 — o teto foi ajustado a partir da execução, não da estimativa desta spec.** Precisa imprimir
dois números **iguais** e sair 0.

```bash
python3 assets/bin/skills.py --root . budget --json | python3 -c "import json,sys; \
d=json.load(sys.stdin); print(d['total'], d['ceiling']); \
sys.exit(0 if d['total']==d['ceiling'] else 1)"
```

`budget` sair 0 **não** é a checagem — ele sai 0 para qualquer `total <= ceiling`, então um teto
transcrito 200 caracteres alto a partir da estimativa de `## Proposal` passa por um gate de código
de saída tendo silenciosamente desligado o ratchet para o próximo comando cunhado. Igualdade é o
que prova que a propriedade de folga zero sobreviveu (risco 1).

**V4 — a superfície ainda tem a forma que tinha.** `doctor --json` reporta `"commands": 25`,
`"findings": []`, saída 0. Esta spec não acrescenta nem remove comando; uma mudança aqui significa
que uma edição de descrição corrompeu frontmatter. (A contagem escrita aqui foi medida em 4.2.0 e
já derivou — ver `## Risks` risco 8 e `## Open Decisions`.)

**V5 — a cifra concorda nos três lugares.** `grep -rn "<measured>" assets/bin/skills.py
../../docs/standards/automation/context-budget.md README.md` acerta os três arquivos, e nenhum site
de *valor corrente* ainda lê 12,726. As frases históricas em `context-budget.md` que narram
`2,083 → 11,565 → 12,726` **precisam sobreviver** — elas são o registro do ratchet, e esta spec
acrescenta uma terceira transição em vez de sobrescrever a segunda.

**V6 — o release lockstep se sustenta.** Todos os quatro imprimem a mesma versão nova, e
`.claude-plugin/plugin.json` + `../../.claude-plugin/marketplace.json` a carregam também:

```bash
cat VERSION; python3 assets/bin/skills.py --version; python3 assets/bin/specs.py --version
python3 assets/hooks/okf-validate.py --version
```

**V7 — o roteamento falado não regrediu. CONDICIONAL.** `./assets/bin/functional-checks.sh` é o
instrumento obrigatório para qualquer spec que toque `commands/**`, e a probe c afirma `/docs:add`
contra uma descrição que esta spec reescreve. Ele **não consegue decodificar a própria evidência
nesta plataforma** (`fix-functional-checks-encoding`): toda asserção falha por falta de evidência,
indistinguível de uma superfície que não carregou. Então:

- se aquela spec aterrissou, V7 é um gate duro e precisa sair 0;
- se não, a execução é registrada como **inconclusiva** e vale nada em nenhuma das duas direções,
  conforme `docs/standards/quality/surface-verification.md` §The four preconditions, item 4. Uma
  execução que não consegue ler a própria evidência nunca é registrada como aprovação, e nunca como
  falha.

**V8 — o bundle ainda conforma.** `python3 assets/hooks/okf-validate.py ../../docs` reporta
**0 errors**. Linha de base antes desta spec: 0 errors, 2 warnings (`resource-unresolved` em
`agents.md`, `stale-doc` em `hooks.md`) — ambos pré-existentes e intocados aqui. Editar
`context-budget.md` sem mover o `timestamp` dele acrescentaria um terceiro warning no mesmo doc que
esta spec declara, então V8 pega isso direto.

**O que nenhuma checagem aqui prova.** Que as descrições restauradas roteiam melhor do que os
rótulos nus roteavam. Nada nesta lista mede roteamento, por desenho — ver `## Out of Scope` e o
risco 7 aceito. Uma execução verde significa *a informação de roteamento que o padrão exige está
presente, alocada sem colisão, e à prova de truncagem*, e nada além disso.

## Design

### Uma tabela de alocação, escrita antes de qualquer arquivo ser editado

O modo de falha que tornaria esta spec pior do que não fazer nada é **colisão de gatilhos**: duas
descrições citando frases que cobrem o mesmo pedido, de modo que o modelo passa a ter dois
candidatos confiantes onde antes tinha uma moeda ao ar entre rótulos.
[doctrine.md](/plugins/quenching/assets/references/skill-new/doctrine.md) nomeia as duas metades —
"a branch without a trigger is a branch that never fires, and two triggers for the same branch are
sediment".

Colisão só é visível no conjunto inteiro, então as frases-gatilho e as cláusulas de fronteira dos
onze comandos são rascunhadas como **uma tabela** e revisadas como um artefato só, *antes* de o
primeiro arquivo ser tocado. Escrevê-las comando por comando é o que produz sedimento.

As linhas da tabela são os clusters confundíveis, porque uma fronteira que não nomeia o sósia mais
próximo é decoração:

| Cluster | Comandos | O que tem de discriminá-los |
| --- | --- | --- |
| escrever uma coisa | `add` · `learn` · `define` | um doc de conceito completo · um fato que um humano acabou de dizer · um termo de glossário |
| ingestão em massa | `import` · `import-memory` | uma fonte externa (arquivos/pastas/URLs) · a memória Claude Code deste projeto |
| grão do glossário | `define` · `glossary-backfill` | UM termo sob demanda · uma varredura do bundle inteiro |
| ler vs convergir | `status` · `align` | reporta e não escreve nada · força o bundle para a forma canônica |
| site vs conteúdo | `documentation:build` · o resto | a config e a nav do mkdocs · as próprias páginas |
| arquivos de instrução | `harness` · `add` | ponteiros em `CLAUDE.md`/`AGENTS.md` · um doc dentro do bundle |
| front de automação | `skill:new` · `skill:eval` | cunhar ou editar UM comando · medir se um deles ensina algo |

### A maior parte do conteúdo já existe, nas palavras do próprio repo

A descrição de `/docs:align` é a única completa na front, e sua cláusula `Not for:` já declara o
trabalho distintivo de **seis** das nove:

> Not for: adding ONE doc → /docs:add; capturing ONE fact a human just stated → /docs:learn; ONE
> glossary term → /docs:define; importing an external source → /docs:import; reading the bundle
> without changing it → /docs:status; the mkdocs site layer → /docs:documentation:build.

Então o trabalho é em grande parte **inverter uma cláusula que já existe**, o que também é o que
mantém o conjunto consistente: dois comandos não podem reivindicar o mesmo trabalho se ambos foram
escritos a partir de uma frase que já os separava. As três restantes (`glossary-backfill`,
`harness`, `import-memory`) tiram seu trabalho distintivo da tabela de papéis em `CLAUDE.md`. As
frases-gatilho vêm do mesmo vocabulário — nunca inventadas para preencher um espaço, porque uma
frase inventada custa caracteres always-on e não roteia nada.

### Orçamento de tamanho: 400–650 caracteres, não os 1,018 de `/docs:align`

`/docs:align` (1,018) e a faixa `/specs:*` (614–974) **não** são o modelo a copiar. Aquelas
descrições carregam prosa sobre *como o comando funciona* — "probes okf-validate.py plus two cheap
out-of-band signals before reading anything", "one inventory, ONE plan, one OK" — o que
[context-budget.md](/docs/standards/automation/context-budget.md) §What the description may carry
põe na lista do "belongs in none of them".

Conceito + gatilhos + fronteira, e nada mais, dimensiona em aproximadamente:

```
  leading concept      ~ 80-110   (the nine already have this; it is the whole current cost)
  3-4 quoted triggers  ~150-220
  Not for: 2-4 clauses ~150-250
                       ---------
  per description       400-650
```

**Trilho duro: nenhuma descrição restaurada passa de 1,024 caracteres**, o limite portável de Agent
Skills (`sk-description-portable`). A faixa deixa margem larga; o trilho é o que o `verify:` afirma,
para que a margem não possa ser gasta em silêncio. O cap duro de 1,536 (`sk-metadata-cap`, um error)
nunca é aproximado.

### A forma do `verify:`, e as duas armadilhas que ela existe para evitar

**Armadilha 1 — `lint` sai 0 em warnings.** Os dois códigos alvo são `severity: warn`, e warnings
não definem o código de saída. Medido: `skills.py lint commands/docs/add.md --json` imprime
`"ok": true` com as duas findings presentes e sai **0**. Um `verify:` que checa o código de saída
não prova absolutamente nada.

**Armadilha 2 — um `lint` de arquivo único re-enraíza.** Dado um arquivo, `lint` resolve a raiz para
o diretório daquele arquivo, então a finding volta como `"command": "/add", "path": "add.md"` — não
`/docs:add`. Um filtro escrito contra o caminho completo do comando não casa com nada em silêncio,
o que se lê como aprovação.

Todo `verify:` portanto roda o lint de **superfície inteira** e filtra o JSON por código e por
caminho. Uma forma só, com `$P` sendo o arquivo sob teste:

```bash
cd plugins/quenching && python3 assets/bin/skills.py --root . lint --json \
| python3 -c "import json,sys; P='$P'; \
F=json.load(sys.stdin)['findings']; \
B=[f for f in F if f['path']==P and f['code'] in \
  ('sk-trigger-position','sk-no-boundary','sk-metadata-cap','sk-description-portable')]; \
[print(f['code'],f['message']) for f in B]; sys.exit(1 if B else 0)"
```

Quatro códigos, não dois: a mesma chamada prova que a finding fechou **e** que fechá-la não estourou
um cap — a única regressão que esta spec pode causar no arquivo que está editando.

### Ordem é uma restrição, não uma preferência

```
  1. draft the allocation table (all eleven, one artifact)   <- no file edited yet
  2. apply it, one description per task, each verified
  3. run `budget --json`  -> it EXITS 1 with sk-budget-ceiling.  Read the total.
  4. transcribe THAT number into the three places that hold it
  5. re-run `budget`      -> exits 0, total == ceiling, headroom zero again
```

O passo 3 não pode vir mais cedo e o passo 4 não pode ser estimado: `context-budget.md` exige que o
teto seja "revised only from a measurement", e toda revisão anterior registra a execução que a
produziu. Os três lugares são `skills.py:166` (`DEFAULT_CEILING`, mais seu comentário de changelog
datado), `context-budget.md` (§The per-surface ceiling, a seção do ratchet, e a amostra de
`breakdown`) e `README.md` (três linhas). Medido em 2026-07-30 a constante está na linha 167, não
166 — ver `## Risks` risco 8.

## Alternatives Considered

| Abordagem | Custo | O que compra | O que impede |
| --- | --- | --- | --- |
| **Não fazer nada** | 0 | superfície fica em 12,726; ratchet fica quieto | nada — mas o padrão segue violado em 11 dos 25 comandos |
| **Copiar o dimensionamento de `/specs:*`** (~850–1,000 cada) | ~+9,000 chars → ~22,000 | consistência de front para front | a dieta; propaga um defeito |
| **Só fronteira, sem gatilhos** | ~+2,400 chars | fecha `sk-no-boundary` em 10 | deixa `sk-trigger-position` em 11; nenhum roteamento à prova de truncagem |
| **Encolher em vez de crescer** (dois níveis) | negativo | ~11,000 chars de volta | já tentado e superado |
| **Medir primeiro, escrever só o que pontuar** | 9 fixtures de eval × 2 execuções | todo caractere respaldado por evidência | impossível nesta ordem — ver abaixo |
| **Amolecer o padrão em vez da superfície** | 0 caracteres; uma edição em `context-budget.md` | fecha as onze findings sem custo always-on algum | o único instrumento que tornou esta lacuna visível |
| **Restaurar conceito+gatilhos+fronteira em 400–650** ← escolhida | ~+4,500 chars → ~17,200 | conformidade, discriminação, resistência a truncagem | nada; a medição por eval segue disponível |

**Não fazer nada** é a que precisa ser argumentada em vez de descartada, porque é o que de fato vem
acontecendo desde o colapso. Ela perde por um custo de segunda ordem: os dois códigos são warnings,
então a superfície reporta *limpa* enquanto onze comandos violam um padrão que o próprio repo
escreveu. Um checker que reporta um defeito que ninguém nunca fecha ensina todo mundo a passar o
olho pela sua saída, e a próxima finding real é ignorada junto. Ou o padrão é aplicado, ou §What the
description may carry deveria ser amolecido — deixar os dois no lugar é o único desfecho sem
defensor.

**Copiar o dimensionamento de `/specs:*`** perde pela própria evidência. Aquelas descrições rodam
614–974 porque narram *como o comando funciona*, o que `context-budget.md` exclui explicitamente.
Copiá-las dobra o custo em caracteres desta spec para propagar um defeito. (Isso também argumenta
que as descrições `/specs:*` deveriam elas mesmas ser enxugadas um dia — anotado, não tentado aqui.)

**Só fronteira** é a decisão mais apertada, e é genuinamente barata: a fronteira é a metade que
discrimina, e a probe c mostra que um pedido formulado convencionalmente já chega ao seu comando sem
gatilho nenhum. Ela perde porque as duas metades servem usuários diferentes. A fronteira ajuda o
leitor que formulou o pedido do jeito que a documentação formula; o gatilho entre aspas ajuda quem
não formulou — e o padrão põe gatilhos na **segunda frase** exatamente para que a truncagem não os
alcance, que é uma garantia que uma descrição só-fronteira não pode oferecer. Levar metade agora
também torna a outra metade mais difícil depois: um segundo passe reabre onze arquivos e dispara o
ratchet uma segunda vez.

**Encolher em vez de crescer** foi uma spec real: `skill-description-tiering` (2026-07-26,
`outcome: abandoned`), que propunha cortar 87% dos metadados always-on sob a premissa de que estes
comandos são operados por `/` digitado e que uma descrição que o humano nunca lê não compra nada.
Declarada na sua forma mais forte, aquela premissa continua viva. Ela perde por dois fatos que
aterrissaram depois dela:

- Ela foi **superada, não refutada** — abandonada no próprio gate em favor de
  `collapse-skills-into-commands`, com sua análise registrada como tendo se sustentado. Então o
  argumento dela merece a resposta abaixo em vez de uma citação.
- A superfície então escolheu o outro lado, deliberadamente: todo comando mantém **invocação
  padrão** (sem `user-invocable: false`, sem `disable-model-invocation`), então espera-se que o
  modelo selecione comandos a partir de prosa — e `context-budget.md` §What the collapse measured
  registra que o roteamento falado *foi medido depois do colapso e sobreviveu*, três frases naturais
  chegando ao seu comando só pela descrição. Uma descrição que roteia não é metadado que o humano
  nunca lê; é a única coisa que serve o caminho de invocação que o plugin deliberadamente manteve.

**Medir primeiro** é a que esta spec mais gostaria de tomar, e não está disponível. Uma execução de
eval pontua prompts `shouldTrigger` / `shouldNotTrigger` contra uma descrição que já contém as
frases; não há como medir a taxa de acerto de um gatilho que ainda não foi escrito.
`skill-evaluation.md` §Description tuning traça a mesma linha — medição autoriza *tuning* (um
gatilho é removido só sob um miss medido), enquanto escrever um é **autoria**, que precisa do humano
cuja intenção o comando codifica. Escrever primeiro, medir depois, remover só sob um miss medido. É
também por isso que nada aqui pode ser enxugado por tamanho mais tarde.

**Amolecer o padrão** é a outra metade da frase que o parágrafo "Não fazer nada" já pronuncia, e ela
nunca foi precificada como opção própria. Na sua forma mais forte: §What the description may carry
passa a exigir as três partes só acima de um limiar de tamanho, ou só nos comandos condutores, e
`sk-trigger-position`/`sk-no-boundary` passam a ser condicionais. Custa zero caractere always-on,
fecha onze findings em uma edição, e é reversível em um `git revert` de um arquivo. Perde por dois
motivos. Primeiro, um padrão enfraquecido até caber na superfície deixa de ser um contrato: `lint`
para de ter sinal sobre o próximo comando cunhado sem gatilho, e foi exatamente esse sinal que
tornou esta lacuna encontrável — o mesmo custo de segunda ordem que derruba "não fazer nada", só
que pago de propósito. Segundo, ele não sobrevive melhor ao cenário 10x: a 250 comandos um padrão
amolecido continua não dizendo nada sobre o que roteia, então desarma o instrumento sem responder a
pergunta que `## Open Decisions` levanta. O caminho honesto para amolecer o padrão é o spike, não
uma edição de conveniência.

## Open Decisions

**BLOCKING — a premissa que sustenta a spec está contestada, e a aprovação foi retida por causa
dela (2026-07-28).** `## Risks` abre nomeando a premissa em que esta spec se apoia: que um modelo
roteia melhor a partir de gatilhos entre aspas mais uma fronteira do que a partir de um rótulo nu, a
um custo que vale pagar. A metade do custo está agora contradita por uma restrição declarada que não
estava em `## Problem`:

> espera-se que a superfície de comandos cresça **~10x** (25 → ~250), e a redução das descrições foi
> **deliberada para esse cenário** em vez de dano colateral do colapso.

Escalando a partir dos 12,726 medidos sobre 25 comandos, o custo always-on em 250 é de ~18,250
caracteres (~4,560 tokens) com rótulos nus, ~131,250 (~32,800 tokens) na faixa de 400–650 desta
spec, e ~210,500 (~52,600 tokens) no dimensionamento `/specs:*`. Nessa escala o modelo de descrição
always-on por comando não sobrevive **em nenhuma variante**, incluindo não fazer nada. Esta spec
compraria, então, conformidade com um padrão cuja própria economia falha uma ordem de magnitude
adiante.

**Como se decide — um spike, e ele decide as duas direções.** Se
`disable-model-invocation: true` bloqueia apenas a seleção autônoma, ou **também** bloqueia uma
chamada Skill explícita por nome. Os condutores deste plugin alcançam seus estágios por nome
(`/align` → `quenching:docs:align`), que é por que `CLAUDE.md` proíbe a flag hoje, e ninguém
estabeleceu qual dos dois é o caso. `functional-checks.sh` check 2 já tem essa forma.

- **bloqueia apenas** → a superfície inteira pode ir typed-only com custo always-on **zero**, e esta
  spec fica moot em vez de meramente caro.
- **também bloqueia por nome** → os condutores quebram, typed-only morre, e a descrição por comando
  é o único mecanismo de roteamento que existe — o que revive esta spec, a 10x o custo que ela
  precifica.

**A substituição candidata**, se o spike permitir: comandos typed-only (descrição zero) mais UM
roteador model-invocable cujo corpo é o registro que `skills.py registry reindex` já gera em
`docs/documentation/reference/automation.md`. O custo vai de O(n) → O(1); o problema de roteamento
não é removido, é relocado para uma descrição que pode ser medida e ajustada, em vez de 250 que não
podem. Duas lacunas conhecidas: `lint` não pula `sk-trigger-position`/`sk-no-boundary` em comandos
typed-only, apesar de `budget` já contá-los como 0, então os dois instrumentos discordariam; e
`context-budget.md` §What the description may carry precisaria de um segundo nível.

**O irmão que pode tornar tudo isto discutível tem nome.**
`route-commands-without-always-on-descriptions` (prioridade nível 1, criticidade `critical`, em
desenvolvimento em paralelo a esta spec) é a spec que carrega a substituição candidata descrita
acima. Ela é a dona da decisão de arquitetura; esta é a dona da conformidade sob a arquitetura de
hoje. Esta spec não presume o resultado dela, não a edita, e não a espera: se ela vencer, esta fica
moot e sua `## Alternatives Considered` é justamente o material que aquela precisa; se não vencer,
esta segue como está escrita. `restructure-claude-front-namespace` (stage `designed`) e
`retire-skill-vocabulary` movem ou renomeiam os caminhos que as cláusulas `Not for:` citam, não a
decisão de carregá-las — essa fronteira está em `## Out of Scope` e no risco 6.

**ABERTO — o re-ajuste do teto absorve, ou atribui, os 149 caracteres que esta spec não somou?** A
tarefa 2.2 escreve em `DEFAULT_CEILING` o total que `budget` imprimir. Medido em 2026-07-30 esse
total já está 149 caracteres acima do teto **antes** de qualquer descrição ser restaurada
(`## Risks` risco 8). Transcrever o número cru é o que a spec manda e é mecanicamente correto, mas
lava crescimento de terceiros dentro da medição desta spec: a terceira entrada do histórico do
ratchet passaria a atribuir a ela um custo que ela não gerou, e esse histórico é exatamente o
registro que `context-budget.md` existe para manter honesto.

- **Como se decide.** Antes da tarefa 2.1, um `git log -p` sobre os valores de `description` entre o
  commit que fixou 12,726 e a `main` atribui os 149 caracteres. Depois, uma de duas: (a) transcrever
  o total cru e registrar a atribuição em uma frase dentro da terceira entrada do ratchet, ou (b)
  tratar a deriva como um disparo separado, com seu próprio re-ajuste, e medir esta spec contra a
  linha de base corrigida. A recomendação é (a) — um teto é uma medição da superfície, não uma
  alocação de culpa, e uma frase de atribuição preserva o registro sem inventar um disparo que
  nenhum humano mediu. É decisão do humano porque muda o que a tarefa 2.3 escreve.

**Esta spec não está abandonada e não está aprovada.** Sua `## Alternatives Considered` e seus
`## Risks` são o material de que uma spec substituta precisa — em particular ela é agora a
declaração honesta da opção "restaurar descrições por comando", com o custo precificado, para a
tabela de alternativas daquela spec.

---

As quatro decisões abaixo foram resolvidas durante a modelagem e se sustentam por si — elas
descrevem o que esta spec faria **se** o spike a revivesse.

1. **Nove comandos ou onze** → onze. `/skill:eval` e `/skill:new` carregam os mesmos códigos, e
   `restructure-claude-front-namespace` reescreve citações de caminho movido em *todo* comando de
   qualquer forma, então incluí-los não acrescenta acoplamento que excluí-los evitaria.
2. **Que tamanho** → 400–650 caracteres, não os 1,018 de `/docs:align` nem os 614–974 de
   `/specs:*`. Aqueles carregam *como funciona*, que o padrão vinculante exclui.
3. **Escrever primeiro ou medir primeiro** → escrever primeiro. A taxa de acerto de um gatilho não
   pode ser medida antes de o gatilho existir; `skill-evaluation.md` limita a medição a *tuning*, e
   a remoção a um miss medido.
4. **Política de `verification`** → `per-task`, mudada de `per-section`. A checagem de cada tarefa é
   uma execução local de script em menos de um segundo contra um arquivo, então não há custo de
   suíte a amortizar.

## Risks

**A premissa que sustenta tudo, declarada primeiro.** Que um modelo roteia melhor a partir de
frases-gatilho entre aspas mais uma fronteira `Not for:` do que a partir de um rótulo nu de menu
`/`. Está escrita como padrão e está não medida **nesta front** — a única medição de roteamento que
este repo possui (três probes faladas, 2026-07-26) testou os rótulos *nus* e os encontrou
funcionando. Se a premissa é falsa, esta spec não compra nada e custa ~4,500 caracteres always-on em
toda sessão de todo repo adotante, para sempre. Tudo abaixo é a jusante dela.

| # | História de falha | Provável | Grave | Como é detectada | Resposta |
| --- | --- | --- | --- | --- | --- |
| 1 | o teto é re-ajustado a partir da estimativa desta própria spec em vez da execução | méd | **alta** | `budget` reporta `total != ceiling` | mitigado — `## Validation` afirma igualdade |
| 2 | duas descrições citam frases sobrepostas; o roteamento acaba pior que rótulos nus | méd | **alta** | nada mecânico | mitigado — uma tabela de alocação, revisada inteira |
| 3 | uma descrição restaurada rouba uma frase que `functional-checks.sh` já afirma | méd | méd | aquele script — **que não roda aqui** | mitigado — restrição de design abaixo |
| 4 | as descrições aterrissam, o teto nunca é re-ajustado | baixa | méd | `budget` sai 1 para sempre depois | mitigado — gate em `## Validation` |
| 5 | `skills.py` muda sem bump de versão; cópias instaladas seguem em silêncio com o teto antigo | méd | méd | nada — `/skill:align` compara `--version`, que casou | mitigado — tarefa de bump declarada |
| 6 | `restructure-claude-front-namespace` aterrissa primeiro; três cláusulas de fronteira citam caminhos mortos | baixa | baixa | qualquer checagem de citação | **ACCEPTED** |
| 7 | o follow-up de eval nunca roda; os caracteres são pagos para sempre, sem medição | **alta** | méd | nunca, por construção | **ACCEPTED — a maior delas** |
| 8 | a linha de base já derivou antes de esta spec começar: `budget` mede 12,875 contra o teto 12,726, `doctor` conta 26 comandos e a versão é 4.4.0 | **já ocorreu** | méd | `budget --json` sai 1 numa `main` limpa | mitigado — nenhum número desta spec vale sem ser relido de uma execução; ver abaixo |

**O risco 1 é o que merece mais cuidado**, porque a checagem óbvia não o pega. `budget` sai 0 sempre
que `total <= ceiling`, então um teto ajustado 200 caracteres alto a partir de uma estimativa passa
por um gate de código de saída tendo silenciosamente desligado o ratchet — o mecanismo não consegue
mais disparar no próximo comando cunhado, que é a razão inteira de ele existir. A asserção precisa
ser `total == ceiling`, não `exit == 0`. Esta spec imprime uma estimativa (~17,200) em duas seções,
que é exatamente a tentação; as duas a rotulam como estimativa por esse motivo.

**A mitigação do risco 3 é uma restrição de design sobre a tabela de alocação**, já que seu detector
está indisponível: nenhuma descrição restaurada pode introduzir uma frase que compita com as cinco
que `functional-checks.sh` já afirma —

```
  a  "park a spec for later: …"                                  -> quenching:specs:create
  b  "capture this for the backlog — …"                          -> quenching:specs:create
  c  "add a standard: we always use snake_case for …"            -> quenching:docs:add
  d  "set up something that audits our migrations and reports back" -> quenching:skill:agent:new
  e  "I want something to catch it automatically whenever a migration lands" -> quenching:skill:hook:new
```

Duas são perigos vivos. A probe c afirma `/docs:add` contra a descrição que esta spec reescreve,
então `/docs:add` precisa manter um gatilho com a forma de "add a standard" em vez de estreitar para
"concept doc". As probes d e e pertencem a `/skill:agent:new` e `/skill:hook:new`, que **não** estão
no escopo — então os gatilhos novos de `/skill:new` não podem alcançar "set up something…" nem
"catch it automatically…", ou esta spec quebra duas asserções em comandos que nunca editou.

**O risco 7 é ACCEPTED, não mitigado, e é sobre ele que a pergunta de aprovação realmente trata.** O
follow-up (fixtures de `/skill:eval` para a front `docs`) não tem dono e não tem data. Aprovar esta
spec significa aceitar um custo always-on recorrente e não medido pela autoridade de um padrão em
vez de uma medição — que é a mesma base sobre a qual `/specs:*` e `/skill:*` já foram restaurados, e
`context-budget.md` é `authority: background` justamente porque não mereceu mais que isso. O
enquadramento honesto: isto traz a última front para a linha de uma regra que o repo escolheu, e a
regra segue não provada.

**O risco 8 já se materializou, e ele invalida três números escritos nesta spec.** Medido na `main`
em 2026-07-30, antes de qualquer tarefa desta spec rodar:

```
python3 assets/bin/skills.py --root . budget --json  -> ok: false, total 12875, ceiling 12726
python3 assets/bin/skills.py --root . doctor --json  -> "commands": 26, "findings": []
cat VERSION                                          -> 4.4.0
```

O 26º comando é `/skill:retro`, cunhado por `improve-command-from-session`. Ele mesmo custa **0** —
carrega `disable-model-invocation: true`, e `budget` conta uma descrição escondida como zero de
propósito (`skills.py` `budget_rows`) — e tanto `context-budget.md` (linhas 10 e 185) quanto
`README.md` registram essa saída de custo zero afirmando que o total ficou em 12,726. A medição
contradiz o registro: os 25 comandos ainda visíveis somam **12,875**, 149 caracteres acima do teto,
porque as cláusulas `Not for:` que passaram a citar `/skill:retro` nos seus vizinhos foram somadas
sem serem precificadas. O ratchet está portanto **vermelho na `main` por um motivo que esta spec não
causou**, e o "segundo disparo" que `## Proposal` reivindica já não é o próximo.

Três consequências concretas, nenhuma resolvida aqui:

- `## Validation` V4 afirma `"commands": 25`; a superfície tem 26. V4 falharia hoje sem nenhuma
  edição desta spec.
- `## Handoff` diz que o total da superfície é 12,726 = `DEFAULT_CEILING` exatamente, com folga zero,
  medido em 4.2.0; a linha de base real é 12,875 sobre 12,726 em 4.4.0, e a tarefa 3.1 nomeia um
  salto 4.2.0 → 4.3.0 que a versão já passou.
- `## Design` cita `skills.py:166` para `DEFAULT_CEILING`; a constante está na linha 167.

**A mitigação é a que a spec já escolheu, só aplicada mais cedo:** nenhum desses números pode ser
escrito a partir desta spec. A tarefa 2.1 relê o total de uma execução e o risco 1 já proíbe
transcrever uma estimativa — a única mudança que a deriva exige é que a tarefa 2.1 rode **antes** de
qualquer contagem citada aqui ser tratada como linha de base. Corrigir os três números acima muda
critérios declarados desta spec, então fica para o humano, e a atribuição dos 149 caracteres é a
segunda entrada de `## Open Decisions`.

**A reversibilidade é alta, e é isso que torna o acima aceitável.** A mudança inteira são onze
valores de string em frontmatter mais uma constante inteira e suas três transcrições. Reverter é um
`git revert`, sem migração de dados, sem estado instalado para desfazer, e sem ação do adotante além
de um upgrade de plugin.

## Handoff

**Estado atual.** Nada construído. Medido na `main` em 4.2.0, 2026-07-28. Uma medição mais nova em
2026-07-30 contradiz os números abaixo — leia `## Risks` risco 8 antes de confiar em qualquer um
deles, e re-meça antes de escrever.

**Os números de que você precisa.** As onze descrições somam **935** caracteres hoje (nove `/docs:*`
= 660; `/skill:eval` 80; `/skill:new` 195). Total da superfície **12,726** = `DEFAULT_CEILING`
exatamente, folga zero. Faixa alvo 400–650 por descrição; novo total esperado ~17,200 — **uma
estimativa, e nunca o número que você escreve em lugar algum.** A tarefa 2.1 produz o real.

**Duas armadilhas mecânicas, as duas medidas, as duas já custaram uma suposição errada:**

1. `skills.py lint` sai **0** com findings de `severity: warn` presentes. Nunca use o código de
   saída dele como gate — filtre o `--json` por código (`## Validation` V1/V2).
2. `lint <single-file>` re-enraíza para o diretório daquele arquivo e reporta `"command": "/add"`,
   não `/docs:add`. Rode o lint de superfície inteira e filtre por `path`.

**De onde vem o conteúdo — não invente.** A cláusula `Not for:` que já existe em `/docs:align` nomeia
o trabalho distintivo de seis das nove, nas palavras do próprio repo; as outras três
(`glossary-backfill`, `harness`, `import-memory`) vêm da tabela de papéis em `CLAUDE.md`. Uma frase
inventada custa caracteres always-on em toda sessão para sempre e não roteia nada.

**Convenções em vigor.** `context-budget.md` §What the description may carry — três coisas, em
ordem, e **nada sobre como o comando funciona**. Essa última regra é por que `/docs:align` (1,018) e
a faixa `/specs:*` (614–974) *não* são o modelo a copiar, apesar de serem o precedente óbvio.

**Já tentado, não refaça.** Encolher em vez de crescer foi uma spec real
(`skill-description-tiering`, abandonada — superada pelo colapso, *não* refutada). Medir antes de
escrever é impossível: a taxa de acerto de um gatilho não pode ser pontuada antes de o gatilho
existir. As duas estão argumentadas em `## Alternatives Considered`.

**Não toque.** Corpos de comando, `sk-step-criterion`, `sk-unscoped-bash`, o resto do `README.md`, e
o próprio desenho do ratchet de folga zero.

## Tasks

Serial de ponta a ponta. Nenhuma tarefa é `[P]`: o ponto inteiro de `## Design` §Uma tabela de
alocação é que o conjunto de frases é decidido nos onze comandos de uma vez, e dois executores
rascunhando metades em paralelo é exatamente a colisão que esta spec existe para evitar. O tempo de
parede economizado seria de segundos.

### 1. Restaurar a informação de roteamento

- [ ] 1.1 Escrever todas as nove descrições `/docs:*` como UM conjunto, em um commit — a alocação
      completa é rascunhada nas onze antes da primeira edição desta tarefa, e só então aplicada
      files: plugins/quenching/commands/docs/add.md, plugins/quenching/commands/docs/define.md, plugins/quenching/commands/docs/glossary-backfill.md, plugins/quenching/commands/docs/harness.md, plugins/quenching/commands/docs/import.md, plugins/quenching/commands/docs/import-memory.md, plugins/quenching/commands/docs/learn.md, plugins/quenching/commands/docs/status.md, plugins/quenching/commands/docs/documentation/build.md
      pattern: plugins/quenching/commands/docs/align.md
      verify: ## Validation V1 + V2 + V4
- [ ] 1.2 Escrever as duas descrições da front de automação — `/skill:eval` ganha as duas partes,
      `/skill:new` ganha apenas frases-gatilho (já carrega uma fronteira)
      files: plugins/quenching/commands/skill/eval.md, plugins/quenching/commands/skill/new.md
      pattern: plugins/quenching/commands/skill/agent/new.md
      verify: ## Validation V1 + V2 + V4
- [ ] 1.3 Conferir a alocação nos onze de uma vez: nenhuma frase entre aspas serve dois comandos, e
      nenhuma compete com as cinco frases que `functional-checks.sh` já afirma (`## Risks`) — em
      particular `/docs:add` mantém um gatilho com a forma de "add a standard", e `/skill:new` não
      alcança nem "set up something…" nem "catch it automatically…"
      files: plugins/quenching/commands/docs/, plugins/quenching/commands/skill/
      verify: ## Validation V1 + V2 + V4

### 2. Re-medir e re-ajustar o teto — estritamente depois de toda tarefa do grupo 1

- [ ] 2.1 Rodar `skills.py --root . budget --json` e registrar o `total` medido na mensagem de
      commit. É ESPERADO que saia 1 com `sk-budget-ceiling`; esse é o ratchet disparando, não uma
      falha, e esta tarefa está completa quando o número tiver sido capturado da execução
      verify: the run's `total` is quoted verbatim in the commit message
- [ ] 2.2 Ajustar `DEFAULT_CEILING` para esse total medido, com um comentário de changelog datado no
      mesmo estilo das duas entradas acima dele — nomeando que este disparo foi causado por
      crescimento de descrição, não por um comando novo
      files: plugins/quenching/assets/bin/skills.py
      verify: ## Validation V3
- [ ] 2.3 Transcrever a cifra para `docs/standards/automation/context-budget.md`: §The per-surface
      ceiling, a amostra de `breakdown`, uma TERCEIRA entrada no histórico do ratchet, e mover
      `timestamp` para a data do build. Deixar de pé toda frase histórica
      `2,083 → 11,565 → 12,726`
      files: docs/standards/automation/context-budget.md
      verify: ## Validation V5 + V8
- [ ] 2.4 Transcrever a cifra para as três linhas do `README.md` que a carregam, e nada mais naquele
      arquivo
      files: plugins/quenching/README.md
      verify: ## Validation V5

### 3. Release lockstep

- [ ] 3.1 Subir 4.2.0 → 4.3.0 nos seis sites — o comportamento de um script distribuído mudou, e uma
      cópia instalada cujo `--version` ainda casa nunca é atualizada por `/skill:align`
      files: plugins/quenching/VERSION, plugins/quenching/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, plugins/quenching/assets/bin/skills.py, plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/hooks/okf-validate.py
      pattern: git show f6c8038
      verify: ## Validation V6

### 4. Verificação final

- [ ] 4.1 Rodar V1–V6 e V8 juntas e registrar as saídas; rodar V7 e registrá-la como aprovação ou
      **inconclusiva**, nunca como uma falha que ela não consegue distinguir de um decodificador
      quebrado
      verify: ## Validation V1–V8
