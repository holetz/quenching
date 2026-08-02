---
slug: route-commands-without-always-on-descriptions
title: Route a 10x command surface without per-command always-on descriptions
verification: per-section
priority: {level: 1, criticality: critical, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
approved: {date: 2026-08-02}
branch: {base: main, work: plan/route-commands-without-always-on-descriptions}
---

# Route a 10x command surface without per-command always-on descriptions

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

A descrição de todo comando fica em contexto em toda sessão, mesmo quando ninguém usa aquele
comando. Hoje são 26 comandos e 12.875 caracteres — 149 acima do teto que o próprio repositório
mediu, e o instrumento que reporta isso não está na rotina de verificação. `## Problem` mostra como
esse número estourou sem nenhum comando novo ser criado, e por que ele não sobrevive se a superfície
crescer como se espera.

`## Proposal` não propõe escrever descrições melhores nem mais curtas. Propõe decidir, comando por
comando, **se a descrição precisa estar em contexto** — usando um campo que o Claude Code já oferece
e que o `skills.py` já sabe cobrar como zero. A consequência que faz essa forma valer a pena está em
`## Design` §D2: um comando fora do contexto mantém a descrição inteira, então nada de texto é
perdido. `## Out of Scope` traça a fronteira com os dois specs vizinhos que mexem na mesma superfície,
e `## Alternatives Considered` registra as outras cinco formas, respondendo explicitamente às duas que
o arquivo do repositório já havia rejeitado, cujas razões expiraram.

Duas coisas devem ser lidas antes de qualquer aprovação, e as duas estão ditas em voz alta em vez de
enterradas. A primeira é uma mecânica que ninguém mediu: se o campo também bloqueia a invocação **por
nome** pelo Skill tool, da qual doze comandos deste plugin dependem — dois artefatos afirmam que sim,
o doc de referência que é dono desse tipo de fato não tem linha nenhuma sobre isso, e `## Tasks`
começa medindo. A segunda é que, **a 26 comandos, esta política quase não economiza caracteres**: os
14 comandos de descrição completa carregam 92,7% do custo e praticamente todos passam no critério de
admissão, então o que se compra hoje é um custo que para de crescer com o tamanho da superfície, não
um corte. `## Risks` abre com essa crítica aceita, e `## Open Decisions` item 5 é o gatilho que
encolhe este spec se a superfície não for crescer.

O resto liga as pontas. `## Design` §D3 explica por que a forma escolhida sobrevive às duas respostas
do spike; `## Impact` declara os dois padrões que este spec reescreve e nomeia, separadamente, os
arquivos que ele edita sem prometer contrato nenhum; `## Validation` diz qual execução prova cada
afirmação, com o antes já medido para o depois ser comparável; e `## Tasks` está ordenado para que
nada seja reclassificado antes de existir o check que pega o erro de classificação.
## Problem

A `description` de cada comando é **always-on**: ela está em contexto em toda sessão, em todo
repositório que instala o plugin, antes de qualquer comando ser selecionado.
[context-budget.md](/docs/standards/automation/context-budget.md) governa esse custo e manda o que
uma descrição carrega — um conceito de abertura, frases-gatilho entre aspas e uma fronteira
`Not for:` — partindo da premissa de que o modelo roteia a partir de prosa.

**O teto já está estourado, hoje, com 26 comandos.** Medido nesta árvore em 2026-07-30:

```
python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching budget --json
  → total 12875 · ceiling 12726 · ok false · sk-budget-ceiling (error) · exit 1
```

O estouro é rastreável e não veio de comando novo. Comparando com `a03f31a`, o commit que fixou
`DEFAULT_CEILING = 12726` (`plugins/quenching/assets/bin/skills.py:167`):

| Comando | então | agora | delta |
| --- | ---: | ---: | ---: |
| `/specs:execute` | 937 | 999 | +62 |
| `/specs:develop` | 951 | 1.007 | +56 |
| `/specs:conclude` | 974 | 1.005 | +31 |
| **superfície inteira** | **12.726** | **12.875** | **+149** |

Três acréscimos de gatilho, nenhum arquivo novo, nenhum `/skill:new` executado — e ninguém
re-mediu. O padrão descreve o ratchet disparando **quando um comando é cunhado**
(§*The ratchet fired exactly as predicted*); não tem registro deste modo, que é silencioso por
construção. E `CLAUDE.md` §*Operating this repo* executa `doctor` e `lint` na verificação do
esqueleto, **não `budget`** — então o único instrumento que reporta o estouro não está na rotina
que se pede para rodar.

**A superfície é esperada crescer ~10x, para cerca de 250 comandos.** Nesse tamanho a descrição
always-on por comando não sobrevive em variante nenhuma. Projetado a partir das bases medidas nesta
árvore (26 comandos, 25 always-on, 12.875 caracteres):

| Superfície com ~250 comandos | base por comando | chars always-on | ~tokens |
| --- | ---: | ---: | ---: |
| typed-only (`disable-model-invocation: true`) | 0 | 0 | 0 |
| um ponto de entrada de roteamento | ~150 (alvo de projeto) | ~150 | ~40 |
| os rótulos `/`-menu curtos de hoje | 74 (média dos 11 curtos) | ~18.500 | ~4.625 |
| as três partes mandatórias na faixa 400–650 | 525 | ~131.250 | ~32.800 |
| as três partes no tamanho de hoje | 853 (média dos 14 completos) | ~213.250 | ~53.300 |

Não fazer nada ainda custa ~4.625 tokens por sessão. Obedecer ao padrão custa ~32.800. O padrão é
`authority: background` e seu teto é "one surface's measurement" — foi escrito para uma superfície
de 25 comandos e sua economia falha uma ordem de grandeza adiante.

**As descrições curtas foram deliberadas, e o repositório vem lendo isso como dano.** Elas estão
registradas como dano colateral do collapse — "the deleted skill description is where the quoted
trigger phrases and the `Not for:` boundary lived" — e restaurá-las é chamado de *affordable*. Um
spec foi levado até o portão `ready` sobre essa leitura
([restore-routing-info-on-docs-commands](/specs/plans/2026-07-28-restore-routing-info-on-docs-commands.md),
aprovação retida em 2026-07-28) antes de a expectativa de 10x aparecer. `skills.py lint` ainda
reporta 11 `sk-trigger-position` e 10 `sk-no-boundary`, exatamente contra os 11 comandos de descrição
curta, então os instrumentos empurram para a opção que escala pior.

**A incógnita que decide tudo — e nada além de prosa a sustenta.**
`disable-model-invocation: true` tira a descrição do contexto por inteiro: `skills.py:1439` detecta
o campo, `skills.py:1441` cobra 0 e marca `alwaysOn: false`, e
`context-budget.md` §*The one command that costs nothing* explica por quê — a descrição continua
sendo lida por um humano, no arquivo e no menu `/`, mas não é residente em sessão nenhuma. Ou seja:
a classe typed-only não paga em **texto**, paga em **alcançabilidade pelo modelo**. Só que os
conductors deste plugin alcançam seus estágios **por nome pelo Skill tool**, e ninguém mediu se o
campo bloqueia apenas a seleção autônoma ou também a chamada por nome:

- bloqueia só a seleção → a cauda longa da superfície pode ir para custo zero com os conductors
  intactos;
- bloqueia também por nome → nenhum estágio de conductor pode entrar na classe typed-only, e o
  conjunto que pode é o resto.

O estado da evidência sobre essa mecânica é o achado mais desconfortável deste `## Problem`:

| Artefato | O que diz | Medido? |
| --- | --- | --- |
| `docs/standards/automation/skills.md` (`authority: current`) | o campo "also stops a conductor reaching the command by name"; a tabela de invocação diz "never a conductor stage, which it would silently break" | **não** |
| `specs/archive/2026-07-26-collapse-skills-into-commands.md` §Out of Scope | a alavanca está "closed by mechanics, not deferred" | **não** |
| `docs/reference/tools/claude-code-skill-command-mechanics.md` — o dono do comportamento medido do Claude Code | **não tem linha nenhuma sobre isso** | — |
| `/skill:retro` | carrega o campo e `budget` o reporta com 0 | sim, mas é uma folha que nenhum corpo de comando invoca por nome, então não testa a afirmação |

O próprio doc de referência registra esse modo de falha, a respeito da sua linha 6: *"an unmeasured
row invites its opposite, because a reader who finds no measured claim will supply one."* Aqui
aconteceu a versão simétrica — dois artefatos supriram a afirmação que ninguém mediu, e um deles é
`authority: current`.

**O conjunto alcançável por nome é pequeno e é autorado.** Medido por varredura de `commands/**`:
`/align` nomeia `quenching:docs:align`, `quenching:specs:align` e `quenching:skill:align`;
`/docs:align` nomeia `quenching:docs:import-memory`, `quenching:docs:harness` e
`quenching:docs:glossary-backfill`; `/specs:execute` entrega isolamento a `/specs:isolate` e encadeia
em `/specs:conclude` pelo Skill tool; `/specs:continue` invoca pelo Skill tool o comando de ciclo que
recomendou. São no máximo doze dos 26 — e esse conjunto cresce com o número de **conductors**, que é
uma lista escrita à mão, não com o número de comandos.

O registry que `skills.py registry reindex` já gera em
`docs/documentation/reference/automation.md` é uma tabela completa e mantida por máquina da
superfície — então um único ponto de entrada model-invocable cujo corpo é esse registry está
disponível como resposta candidata, trocando custo always-on O(n) por O(1) mais um hop. É candidato,
não decisão: `specs/archive/2026-07-26-skill-description-tiering.md:365` registra a ideia como
*superseded*, e derrotar essa razão é trabalho de `## Alternatives Considered`.

Duas lacunas de instrumento já estão visíveis de qualquer forma: `lint` não escapa os dois códigos de
roteamento para um comando typed-only embora `budget` já o cobre como zero, então os dois discordam
sobre a mesma superfície — hoje inobservável, porque o único comando typed-only por coincidência
carrega gatilhos e fronteira e não dispara nenhum dos dois; e `context-budget.md`
§*What the description may carry* não tem tier para um comando cuja descrição não está em contexto.

## Proposal

- A pergunta "esta descrição precisa estar **em contexto**?" tem dono, é respondida comando por
  comando, e a resposta fica registrada no campo que o Claude Code já lê
  (`disable-model-invocation`) — **nenhuma chave de frontmatter nova é inventada**.
- Está **medido**, e não afirmado, se `disable-model-invocation: true` bloqueia apenas a seleção
  autônoma pelo modelo ou também a invocação por nome pelo Skill tool. O resultado vira uma linha
  datada e versionada em `docs/reference/tools/claude-code-skill-command-mechanics.md`.
- `docs/standards/automation/skills.md` para de afirmar como fato uma mecânica que ninguém mediu: ou
  a célula da tabela de invocação cita a medição que a sustenta, ou é reescrita para dizer o que se
  sabe.
- **Nenhum texto de descrição fica mais curto por causa deste spec.** Um comando typed-only mantém a
  descrição inteira — humano e menu `/` continuam lendo tudo. O que ele deixa de pagar é residência,
  não conteúdo.
- Existe um **critério de admissão declarado** à classe roteada: um comando é roteado se, e somente
  se, alguém o alcança **sem digitar o nome** — por fala, ou por um conductor que o nomeia. Todo o
  resto é typed-only.
- O conjunto alcançável **por nome** deixa de ser algo que se descobre por `grep`: `skills.py` passa
  a derivá-lo dos corpos de comando, e marcar um membro desse conjunto como typed-only produz um
  finding em vez de um conductor silenciosamente inerte.
- `budget --json` reporta a divisão entre as duas classes — quantos comandos e quantos caracteres em
  cada — de modo que "fomos typed-only para escapar da medição" fica visível, em vez de
  indistinguível de uma queda legítima de custo.
- `lint` e `budget` param de discordar sobre a mesma superfície: `sk-trigger-position` e
  `sk-no-boundary` não são reportados contra um comando cuja descrição não está em contexto, porque
  não existe roteamento por prosa para eles avaliarem.
- `context-budget.md` ganha o tier que falta (o que uma descrição typed-only deve carregar) e o
  registro de que o teto pode ser estourado por **crescimento de descrição**, sem nenhum comando
  novo — o modo que produziu os +149 de hoje.
- O teto volta a bater com o disco, re-medido **de uma execução**, nos três lugares que o
  transcrevem.
- Existe um **gatilho declarado** para o caso de a própria classe roteada estourar seu orçamento: o
  próximo passo é o ponto de entrada único sobre o registry gerado, registrado com sua condição de
  disparo em `## Alternatives Considered` — não construído aqui.

## Out of Scope

- **Reescrever o texto de qualquer descrição.** As onze descrições curtas (nove `/docs:*`,
  `/skill:eval`, `/skill:new`) são de `restore-routing-info-on-docs-commands`. Este spec decide
  **residência**, não redação — e as duas decisões são ortogonais: uma descrição pode ser completa
  e não-residente ao mesmo tempo.
- **Renomear, mover, criar ou remover qualquer comando.** `restructure-claude-front-namespace` é
  dono disso, incluindo mover `/docs:harness` — que é um estágio invocado por nome — para outro
  namespace.
- **Fazer a superfície crescer.** Este spec prepara a política de custo; não cunha nenhum dos ~224
  comandos que a projeção supõe, e nenhuma tarefa depende de o crescimento acontecer.
- **Construir o ponto de entrada único sobre o registry.** É a saída declarada com gatilho, não uma
  entrega. Construí-la agora seria pagar um hop no caminho comum para economizar residência que a
  classe typed-only já economiza de graça.
- **O menu `/` com 250 entradas.** Corte de escopo tomado no premortem: uma superfície de 250
  comandos tem um problema de descoberta **humana** que nenhuma decisão de residência resolve, e
  `hide-from-slash-command-tool` — que existe como campo, registrado em
  `docs/reference/tools/claude-code-skill-command-mechanics.md` §5 — é a alavanca daquele problema, não
  deste. Nomeado aqui para não voltar como escopo.
- **Medir se o roteamento por prosa melhora ou piora.** É uma medição
  should-trigger / should-not-trigger, de `/skill:eval` — e `plugins/quenching/assets/evals/` tem
  dois conjuntos de casos hoje (`skill/agent/new`, `skill/hook/new`), nenhum no front `docs`.
  `context-budget.md` §*What the collapse measured* é explícita: barateza e roteabilidade são
  perguntas independentes.
- **Medir a curva de degradação do roteamento em função do tamanho da superfície.** Corte de escopo
  tomado no premortem, e maior que o anterior: ninguém tem instrumento para isso, `/skill:eval` mede um
  comando por vez, e construir a bancada seria maior que este spec inteiro. A consequência está aceita
  em `## Risks`.
- **A enforcement de `allowed-tools`.** A linha 6 do doc de mecânica é uma pista, não um veredito, e
  não toca em residência de descrição.
- **Os `sk-step-criterion` e `sk-unscoped-bash` que `lint` reporta hoje** (9 e 5). São findings sobre
  corpos e grants, não sobre metadado always-on, e misturá-los tornaria o diff deste spec ilegível.
- **Transformar `budget` em portão que recusa.** `budget` reporta e nunca recusa, e
  `context-budget.md` §*The per-surface ceiling* escolheu isso explicitamente. O que falta não é
  teeth, é a execução estar na rotina — que é a tarefa 2.3, e é tudo.
- **Promover `context-budget.md` a `authority: current`.** A condição de graduação dele é este plugin
  mais dois repositórios adotantes; este spec entrega mais uma medição na mesma superfície, que não é
  a condição.
## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/automation/context-budget.md` — **revisado, não criado.** Ganha o tier que falta em
  §*What the description may carry* (o que uma descrição carrega quando não está em contexto: ela é
  lida por humano e pelo menu `/`, não por um roteador, e portanto não fica mais curta), ganha a
  divisão roteada/typed-only que `budget` passa a reportar, e ganha o registro do modo de disparo do
  ratchet que ele hoje não tem — **crescimento de descrição**, sem nenhum comando cunhado, medido em
  +149 sobre três descrições desde `a03f31a`. O teto é re-transcrito de uma execução. Continua
  `authority: background`.
- `docs/standards/automation/skills.md` — **revisado, não criado.** A célula da tabela de invocação
  que hoje afirma que `disable-model-invocation: true` bloqueia a invocação por nome passa a citar a
  linha medida, ou é reescrita para dizer o que se sabe; e §*Invocation and permission are authored
  decisions* ganha o critério de admissão à classe roteada, que é a regra durável deste spec.

### Padrões em `authority: background` que este spec pode promover a `current`

- none — `context-budget.md` é o único `background` em jogo, e a condição de graduação declarada nele
  é este plugin mais dois repositórios adotantes. Este spec entrega mais uma medição na **mesma**
  superfície, que não é essa condição. Continua `background` de propósito, e está dito para que
  ninguém promova por engano ao ver o teto recém-medido.

### Arquivos que este spec edita sem prometer contrato em `docs/standards/`

- `docs/reference/tools/claude-code-skill-command-mechanics.md` — uma linha nova na tabela
  §*The findings* com seu status, a subseção que a explica, e a entrada correspondente em
  §*Re-measurements* com data e versão do binário. É `docs/reference/`, não `docs/standards/`: é fato
  medido sobre uma ferramenta que consumimos, não contrato nosso.
- `plugins/quenching/assets/bin/skills.py` — o predicado "esta descrição está em contexto?" extraído
  de `budget_rows` (linha 1436, condição na 1439) para um helper usado também pelo lint dos dois
  códigos de roteamento; a divisão por classe no payload de `cmd_budget` (linha 1446); o finding novo
  em `_lint_invocation` (linha 861) com o conjunto alcançável-por-nome derivado dos corpos; e
  `DEFAULT_CEILING` (linha 167) re-transcrito.
- `plugins/quenching/commands/**` — **apenas frontmatter de invocação**, e apenas nos comandos que o
  humano confirmar na tarefa 3.1. Nenhum corpo, nenhum caminho, nenhum texto de descrição.
- `CLAUDE.md` §*Operating this repo* — o bloco de verificação lista `doctor` e `lint` e não lista
  `budget`, que é por que o estouro de hoje passou sem ninguém ver.
- `plugins/quenching/README.md` §*Cost model* — transcreve o teto e a contagem.
- `plugins/quenching/VERSION`, `plugins/quenching/.claude-plugin/plugin.json`,
  `.claude-plugin/marketplace.json`, `plugins/quenching/assets/bin/specs.py`,
  `plugins/quenching/assets/hooks/okf-validate.py` — o lockstep de versão, porque `skills.py` muda.

## Validation

Tudo aqui é verificável por execução. As duas afirmações que **não** são — se o roteamento por prosa
melhora, e se a superfície vai crescer — estão em `## Out of Scope` e em `## Risks`, não aqui.

**O antes, medido nesta árvore em 2026-07-30, para que o depois seja comparável:**

```
python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching budget --json
  → total 12875 · ceiling 12726 · ok false · sk-budget-ceiling · exit 1
python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json
  → exit 0 · 35 findings: 11 sk-trigger-position, 10 sk-no-boundary, 9 sk-step-criterion, 5 sk-unscoped-bash
python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json
  → ok true · 26 comandos · 0 findings
```

**O depois:**

- `budget --json` sai **0** com `ok: true`, e o `total` que ele imprime é byte-a-byte o número
  transcrito em `skills.py` `DEFAULT_CEILING`, em `context-budget.md` e em `README.md`. Um número
  estimado em qualquer um dos três é falha da tarefa 3.2, não detalhe.
- `budget --json` carrega a divisão por classe: contagem e caracteres de roteada e de typed-only, com
  a soma da parte roteada igual a `breakdown.commands`.
- `lint --json` não reporta `sk-trigger-position` nem `sk-no-boundary` contra nenhum comando cuja
  descrição não está em contexto. **Isto é hoje inobservável na superfície real** — `/skill:retro` é o
  único typed-only e por coincidência carrega gatilhos e fronteira — então a tarefa 1.1 entrega junto o
  caso de `selftest` que a demonstra. Uma regra cuja violação nenhum caso exercita não está provada.
- `lint --json` reporta a severidade decidida em `## Open Decisions` item 6 para um comando **nomeado
  pelo corpo de outro comando** que carregue `disable-model-invocation: true` — provado por um caso no
  `selftest`, nunca editando a superfície real, porque provar por edição da superfície é exactly o
  conductor inerte que o check existe para impedir.
- `doctor --json` continua `ok: true` com 26 comandos. Este spec não cria nem remove entry point.
- `python3 plugins/quenching/assets/bin/skills.py selftest`,
  `python3 plugins/quenching/assets/bin/specs.py selftest` e
  `python3 plugins/quenching/assets/hooks/okf-validate.py selftest` saem 0.
- `python3 plugins/quenching/assets/hooks/okf-validate.py docs` sai 0 depois dos edits em
  `docs/standards/automation/` e `docs/reference/tools/` (hoje sai 0 com avisos `stale-doc`
  pré-existentes em três docs não relacionados; nenhum aviso novo pode aparecer nos arquivos que este
  spec toca).
- **Lockstep:** `cat plugins/quenching/VERSION` concorda com `--version` de `skills.py`, `specs.py` e
  `okf-validate.py`, e com `plugin.json` e o manifest do marketplace.
- **O spike é decisivo e é barato.** Custa **uma** sessão `claude -p` nova — nova porque o registry é
  construído no início da sessão (`claude-code-skill-command-mechanics.md`, linha 4 da tabela
  §*The findings*) — e o resultado é registrado com data e versão aconteça o que acontecer, incluindo
  se vier ambíguo. O arquivo de probe é revertido nos dois casos. Nenhuma outra tarefa deste spec gasta
  uma sessão cobrada, o que é o que
  [surface-verification.md](/docs/standards/quality/surface-verification.md) pede.
- **A política de verificação continua `per-section`**, revisada neste passe e mantida: cada grupo de
  `## Tasks` é uma unidade que faz sentido verificar inteira — a medição, os instrumentos, a política,
  a classificação — e nenhum grupo tem tarefa cujo erro só apareça no grupo seguinte, que é o que
  exigiria `per-task`.

## Design

### O que muda de forma, em uma figura

O custo always-on é hoje linear no tamanho da superfície. A proposta não o reduz por comando: ela
tira a maioria dos comandos da conta.

```
custo always-on em função de n = tamanho da superfície

hoje       custo = n x 74..853 chars            linear em n
proposto   custo = r x 400..650 chars           linear em r, e r NAO cresce com n
                   r = comandos alcançados sem digitar o nome (12 medidos hoje)
saída      custo = 1 x ~150 chars + um hop      constante, se r estourar seu orçamento
```

```
hoje                                    proposto
--------------------------------        --------------------------------
26 descrições residentes                classe roteada (12 medidos)
        |                                 três partes, cobradas no teto
        v                                         |
[ 12.875 chars em TODA sessão ]                   v
        |                               [ o teto se aplica só a esta classe ]
        v
    um comando                          classe typed-only (o resto)
                                          descrição INTEIRA, 0 chars
                                                  |
                                                  v
                                        [ fora do contexto; alcançada digitando / ]
                                                  |
                                                  v
                                              um comando
```

### D1. A classe é declarada no campo que o Claude Code já lê, nunca em uma chave nova

`skill-description-tiering` propôs `routing: direct | inferred` em frontmatter, e registrou em
`## Open Decisions` o risco dessa escolha: *"it is a new frontmatter key on a surface that also
ships into other repos. If a future Agent Skills revision claims `routing`, this collides."* Ele
também registrou, no seu `## Design`, por que **não** usou o campo do Claude Code:
*"this plugin cannot set that flag while the wrappers exist, so every skill would classify as
`inferred`."*

Essa restrição **expirou**. Não há wrappers — um arquivo por entry point
([command-surface.md](/docs/standards/naming/command-surface.md) §*The path IS the identity*);
`skills.py:1439` já lê o campo; `context-budget.md` §*The one command that costs nothing* já o
documenta como a segunda saída do ratchet; e `/skill:retro` já o carrega em produção. A regra
durável: **quando o host já expressa a distinção, a declaração é o campo do host, e o instrumento
lê o campo — não se cunha uma segunda fonte de verdade para o mesmo fato.**

### D2. A classe typed-only não custa nada em qualidade de texto

Este é o ponto onde a forma difere de tudo o que já foi tentado aqui.
`context-budget.md` §*The one command that costs nothing* é explícita: *"The description is still
read — by a human, in the file, and by `/skill:*` — but it is not resident in any session's
context."* Logo a descrição de um comando typed-only continua inteira: as três partes, os gatilhos,
a fronteira `Not for:`.

`skill-description-tiering` pagava exatamente aqui. Ele substituía uma descrição de ~1.066
caracteres por um stub de ~74 e assumia, no próprio `## Risks`, a perda: *"Whether that is enough is
unmeasured by choice."* A regra durável: **residência e conteúdo são eixos independentes, e só a
residência custa contexto.** Cortar texto para economizar residência é pagar duas vezes.

### D3. O conjunto alcançável por nome é uma lista autorada, não uma função de n

Medido por varredura de `commands/**` em 2026-07-30:

| Quem invoca por nome | Alvos |
| --- | --- |
| `/align` | `quenching:docs:align`, `quenching:specs:align`, `quenching:skill:align` |
| `/docs:align` | `quenching:docs:import-memory`, `quenching:docs:harness`, `quenching:docs:glossary-backfill` |
| `/specs:execute` | `/specs:isolate` (isolamento), `/specs:conclude` (encadeamento a 100%) |
| `/specs:continue` | o comando de ciclo que ele recomendou, pelo Skill tool |

No máximo doze dos 26. E o tamanho desse conjunto é limitado por **quantos corpos de conductor
nomeiam alguém**, que é texto escrito à mão. Duplicar a superfície não duplica esse conjunto.

É por isso que esta forma **sobrevive às duas respostas do spike**, ao contrário da leitura que o
`## Problem` capturado carregava ("bloqueia por nome → typed-only está morto"). Se o campo bloquear
a invocação por nome, a classe typed-only simplesmente exclui esses doze; a cauda longa — que é onde
os ~224 comandos hipotéticos estariam — continua elegível.

### D4. A ordem: medir, instrumentar, só então classificar

1. **Medir** (grupo 0). Em uma sessão `claude -p` nova, porque o registry é construído no início da
   sessão — linha 4 de
   [claude-code-skill-command-mechanics.md](/docs/reference/tools/claude-code-skill-command-mechanics.md),
   e a mesma razão que fez aquele spike anterior precisar de processo novo.
2. **Instrumentar** (grupo 1). O finding de D5 e a divisão no `budget` pousam **antes** de qualquer
   reclassificação, para que um erro de classificação seja reportado em vez de descoberto por um
   conductor que rodou e não fez nada.
3. **Escrever a política** (grupo 2), porque o critério tem de estar citável antes de ser aplicado.
4. **Classificar** (grupo 3), com uma tabela e uma confirmação, e só então re-medir o teto.

Nada é reclassificado antes de existir o check que pega o erro. Essa é a mesma razão pela qual
`skill-description-tiering` pôs a mudança do linter antes de cortar a primeira descrição — e é a
única parte do desenho dele que este spec herda de propósito.

### D5. O finding que a própria mecânica deste spec torna necessário

`skills.py` já tem `sk-unreachable` (`_lint_invocation`, `skills.py:877`) para
`user-invocable: false` combinado com `disable-model-invocation: true` — nenhum caller possível. Não
tem nada para o modo de falha que **esta** política cria: um comando **nomeado pelo corpo de outro
comando** carregando `disable-model-invocation: true`.

O predicado é derivável do disco: os alvos de D3 estão escritos nos corpos. A severidade vem do
spike — `error` se o campo bloquear a invocação por nome, porque então a combinação é um conductor
inerte, e não há sinal nenhum que a delate hoje (`budget` reporta 0, `doctor` passa, `lint` não
olha).

### D6. `budget` e `lint` leem o mesmo predicado, de um lugar só

`budget_rows` (`skills.py:1436`) já calcula "esta descrição está em contexto?" na linha 1439. A
correção não é escrever a mesma condição em `_lint_description`: é extrair o predicado para um helper
e chamar dos dois lados. Duas cópias da mesma condição é a forma que divergem em silêncio — o mesmo
argumento que `spec-driven.md` usa para as dez seções do portão viverem em um lugar só.

### Contratos que este desenho não pode contradizer

- [command-surface.md](/docs/standards/naming/command-surface.md) — o caminho é a identidade. Este
  spec não toca em caminho nenhum, o que é o que o mantém ortogonal a
  `restructure-claude-front-namespace`.
- [skills.md](/docs/standards/automation/skills.md) §*Invocation and permission are authored
  decisions* — a tabela de quatro linhas continua sendo a fonte. Este spec acrescenta **quando**
  escolher a terceira linha; não acrescenta uma quinta.
- [context-budget.md](/docs/standards/automation/context-budget.md) — "revised only from a
  measurement". O teto novo vem de uma execução de `budget`, nunca de estimativa; e a segunda saída
  do ratchet "is only honest when typed-only is the *right* design, never as a way to dodge the
  measurement", que é exatamente o que a divisão de D6 torna visível.
- [surface-verification.md](/docs/standards/quality/surface-verification.md) — cada probe é uma
  sessão cobrada. O spike é **um** probe, e é o único deste spec.
- `CLAUDE.md` §*Two rules that must survive any refactor* — nada de `context: fork` nos sweeps, nada
  de `haiku` em `/docs:import-memory`. Nenhum dos dois é tocado; este spec só escreve frontmatter de
  invocação e `skills.py`.

## Alternatives Considered

Cinco formas inteiras, mais a versão comprar-em-vez-de-construir. Cada uma está escrita como seu
melhor advogado a escreveria; as duas que o arquivo já rejeitou têm a razão registrada citada e
respondida, não ignorada.

| Forma | Custo a 250 comandos | O que compra | O que impede |
| --- | ---: | --- | --- |
| **A. Duas classes pelo campo do host** (escolhida) | ~5.000–8.000 chars (só a classe roteada) | custo O(r) com r autorado; nenhum texto encurtado; nenhuma chave nova | exige uma medição e um finding novo antes de classificar |
| B. Não fazer nada | ~18.500 chars | zero trabalho | o teto vira decoração e nenhum rótulo discrimina vizinhos |
| C. Só re-medir o teto | ~18.500 chars | um edit de três arquivos, risco zero | converte o teto em registro do que já se gasta |
| D. Restaurar as três partes em todos e subir o teto | ~131.250 chars | conformidade total com o padrão como está escrito | ~32.800 tokens por sessão, para sempre |
| E. Um ponto de entrada único sobre o registry | ~150 chars | O(1) de verdade | um hop no caminho comum e a decisão de roteamento fica pior |
| F. Comprar/emprestar | — | o host já dá os campos | política e instrumento não se emprestam |

**B — Não fazer nada.** Manter os rótulos curtos e conviver com o teto estourado. Perde por duas
razões medidas, não por gosto: `budget` já sai 1 hoje com `sk-budget-ceiling` (severidade `error`) e
nada na rotina de verificação do repositório o executa, então o sinal que `context-budget.md`
construiu deixa de significar qualquer coisa; e um rótulo `/`-menu não **discrimina**. "Escreve isso
na documentação" tem de escolher entre `/docs:add`, `/docs:learn`, `/docs:define` e `/docs:import`, e
a única prosa que responde é o `Not for:`.

**C — A coisa menor que funcionaria: só re-medir o teto.** Honestamente boa e honestamente pequena:
fecha o `sk-budget-ceiling` de hoje com um edit em três arquivos e risco zero. Perde como
**resposta**, porque re-medir converte o teto em um registro do que a superfície já gasta, que é o
modo de falha que `context-budget.md` §*Why the ceiling went 2,083 → 11,565* descreve do outro lado.
**Não é rejeitada — é dobrada para dentro** deste spec como tarefa 3.2, depois de a política existir.

**D — Restaurar as três partes em todos os comandos e subir o teto.** A direção que
`restore-routing-info-on-docs-commands` levou ao portão, e ela está certa sobre o que compra:
conformidade com o padrão exatamente como está escrito, e discriminação entre todos os vizinhos.
Perde como resposta **para 250 comandos**, a ~131.250 caracteres. Não perde para 26 — e é por isso
que os dois specs não se anulam: D é a política de residência aplicada com r = n. Se o humano
declarar que a superfície não passa de ~40 comandos, D passa a ser a resposta certa e este spec
encolhe para a medição mais os dois instrumentos (`## Open Decisions`).

**E — Um ponto de entrada único sobre o registry gerado.** O arquivo registra a ideia como
superada: *"This supersedes the earlier 'one router skill per front' idea, which added a hop on the
common path to save descriptions the collapse removes outright"*
(`specs/archive/2026-07-26-skill-description-tiering.md:365`). **Essa razão é derrotada em dois
pontos, não contornada.**

Primeiro: *"descriptions the collapse removes outright"* nomeia a **segunda** descrição de cada par
skill+wrapper. Essa economia já foi sacada — 30.705 → 2.083 caracteres — e não há segunda cópia para
remover de novo. A frase descrevia um saldo disponível em 2026-07-26; hoje descreve um saldo gasto, e
o que sobrou é a descrição única por comando, que nenhum collapse futuro remove.

Segundo: o hop é **O(1) por invocação** e é pago só quando alguém precisa rotear; a residência é
**O(n) por sessão** e é paga tenha ou não algum comando disparado. A 25 comandos o hop perdia com
folga. A 250 a razão inverte, e é exactly a inversão que o `## Problem` deste spec mede.

Ainda assim E **não é a entrega**, por duas razões próprias: a classe roteada medida hoje tem doze
membros, não duzentos, então A já entrega O(r) sem hop nenhum; e um hop troca uma decisão de
roteamento a partir de descrições curadas por uma decisão a partir de uma tabela que o modelo tem de
ler e interpretar, o que é uma piora de qualidade que ninguém aqui mediu. E fica registrada como
**saída declarada**, com gatilho: se a classe roteada estourar seu próprio orçamento, E é o próximo
passo.

**Tiering declarado em uma chave nova (`routing: direct | inferred`)** — a forma de
`skill-description-tiering`, abandonada com 2/17 tarefas. Não é re-proposta aqui, e perde por duas
razões, a primeira registrada por ele mesmo: ele **encurtava** a descrição para um stub de ~74
caracteres e aceitava a perda de roteamento sem medi-la (`## Risks`: *"unmeasured by choice"*),
enquanto residência via `disable-model-invocation` não encurta nada (D2). A segunda: a razão pela
qual aquele spec rejeitou o campo do host — os wrappers — expirou, e `skills.py` já lê o campo (D1).
Re-propor a chave nova hoje seria pagar a colisão de nomes que ele mesmo listou como Open Decision
para comprar algo que o campo existente já entrega. Vale registrar o que **sobrevive** dele e este
spec herda: a ordem "linter antes do corte" (D4) e a insistência em que o tier seja **declarado**, e
não inferido de comprimento de descrição.

**F — Comprar ou emprestar em vez de construir.** Boa parte deste spec já é isso: os campos
`disable-model-invocation` e `hide-from-slash-command-tool` são do host, e a economia de residência
vem de graça de uma feature do Claude Code. O que não se empresta são as duas metades que sobram — a
**política** (qual comando entra em qual classe) e o **instrumento** que a checa. Nenhum host vai
reportar que um conductor deste plugin ficou inerte.

## Open Decisions

1. **`disable-model-invocation: true` bloqueia apenas a seleção autônoma, ou também a invocação por
   nome pelo Skill tool?** É a decisão que dimensiona a classe typed-only, e é a única coisa neste
   spec que ninguém pode responder lendo o repositório. Decidida pela **tarefa 0.1**, em uma sessão
   `claude -p` nova. Regra de leitura fixada agora, para que o resultado não seja interpretado depois:
   **ambiguidade conta como "bloqueia"** — é a leitura conservadora e é a que
   `docs/standards/automation/skills.md` já afirma, então adotá-la não muda nada que já esteja escrito.

   **RESOLVIDO (0.1, 2026-08-02, Claude Code 2.1.220) — bloqueia os DOIS caminhos.** Dois braços com
   controle, verificado no sistema de arquivos: o braço sem o campo foi listado e invocado por nome
   com sucesso; o braço com o campo não foi listado e a invocação por nome foi **recusada** com
   `Skill quenching:zzprobeb cannot be used with Skill tool due to disable-model-invocation`. Não foi
   preciso recorrer à regra de ambiguidade — o host nomeia o campo na própria recusa. Registrado como
   linha 7 de `docs/reference/tools/claude-code-skill-command-mechanics.md` (0.2).

2. **`skills.md` ganha a medição, ou perde a afirmação?** Se o spike confirmar o bloqueio, a célula da
   tabela de invocação fica e passa a citar a linha medida. Se contradisser, um padrão
   `authority: current` está errado em uma célula, e corrigi-lo é maior que um edit de prosa — arrasta
   a tabela de quatro linhas, a §*Invocation and permission are authored decisions* e o
   `## Out of Scope` do collapse arquivado, que declarou a alavanca "closed by mechanics". Decidido
   **pelo resultado** da 0.1; registrado aqui porque o spec não pode e não deve escolher antes.

   **RESOLVIDO (0.3) — ganha a medição.** O spike confirmou o bloqueio, então a célula estava certa e
   fica. A tarefa 2.2 a faz **citar** a linha 7 em vez de afirmar. Nenhum padrão `authority: current`
   está errado, e a cascata que o item temia não existe: o `## Out of Scope` do collapse arquivado
   ("closed by mechanics") também estava certo.

3. **Quem entra na classe roteada, comando por comando.** O critério está em `## Proposal`; a lista
   não está, e não deve estar: escrevê-la agora seria decidir 26 casos sem o instrumento que deriva a
   parte mecânica deles. Decidida pelo humano na **tarefa 3.1**, com o conjunto alcançável-por-nome
   vindo do instrumento da 1.3, aplicada só na parte aprovada.

   **EM ABERTO** — é da 3.1, como projetado. Mas a medição de 0.1 já estreita o resultado esperado:
   ver a nota de dimensionamento no fim desta seção.

4. **Qual é o orçamento da classe roteada — e portanto quando a saída E de
   `## Alternatives Considered` dispara.** Decidido **de uma execução** de `budget` depois da 3.1,
   nunca de estimativa: é a regra do próprio `context-budget.md`. Até essa execução existir, a forma E
   não tem gatilho numérico, só condição qualitativa, e este spec não finge o contrário.

   **EM ABERTO** — depende da 3.1, como projetado.

5. **A projeção de ~250 comandos é o alvo contra o qual planejar?** Se o humano declarar que a
   superfície não passa de ~40 comandos, a resposta honesta passa a ser a forma **D** de
   `## Alternatives Considered` — restaurar as três partes em todos e re-medir o teto — e este spec
   encolhe para o grupo 0 (a medição) mais o grupo 1 (os dois instrumentos), abandonando os grupos 2 e
   3. Decidido pelo humano **antes** da tarefa 3.1, e é a decisão que mais muda o tamanho deste spec.
   O `## Risks` §*A crítica que mais dói* é o material dessa conversa.

   **RESOLVIDO (0.3, 2026-08-02) — sim, ~250 é o alvo. O spec é construído inteiro**, grupos 1, 2 e 3.
   Decidido com os números re-medidos nesta árvore, e não com a estimativa pré-spike, incluindo a nota
   abaixo: a decisão foi tomada **sabendo** que o grupo 3 classifica perto de nada hoje. O que se
   compra é o instrumento e a política, e o retorno está inteiramente nos comandos ainda não cunhados.

6. **A severidade do finding da tarefa 1.3.** `error` se a 0.1 disser que o campo bloqueia por nome,
   porque então a combinação é um conductor inerte; `warn` se não bloquear, porque então é só uma
   escolha de projeto discutível. Decidido pela 0.1, não por gosto — escrito aqui para que a tarefa não
   tenha de decidir sozinha no meio da execução.

   **RESOLVIDO (0.1) — `error`.** O campo bloqueia por nome, logo a combinação é literalmente um
   conductor inerte: a chamada é recusada e o conductor segue sem falhar.

### A nota de dimensionamento que a medição obriga (0.3)

Re-medido nesta árvore em 2026-08-02, e mais duro do que o `## Risks` previu:

| | comandos | chars | fatia |
| --- | ---: | ---: | ---: |
| descrição completa | 15 | 12.816 | **99,5%** |
| descrição curta | 11 | 935 | 0,5% |
| **superfície** | **26** | **12.875** | teto 12.726 — **estourado em 149** |

O `## Risks` estimava a classe typed-only como "essencialmente o conjunto das descrições curtas, 935
caracteres". A medição de 0.1 a encolhe mais: três das onze curtas — `/docs:harness`,
`/docs:import-memory`, `/docs:glossary-backfill`, 217 chars — são estágios que `/docs:align` alcança
**por nome**, e agora estão **duramente** excluídas. As demais são alcançadas por fala, que o critério
de admissão também exclui.

**Aplicado honestamente hoje, o grupo 3 classifica zero ou perto de zero comandos, e a
reclassificação não fecha nenhum dos 149 caracteres de estouro.** Quem fecha o estouro é a 3.2
(re-medir o teto — a forma C dobrada para dentro), e quem impede o próximo é a 2.3 (pôr `budget` na
rotina). Isto está escrito aqui para que ninguém leia o `budget` verde do fim como prova de que a
política economizou alguma coisa: ela não economizou, ela parou de crescer.
## Risks

Gerado por um premortem contra o conteúdo deste spec — *é 2026-10-30, isto foi construído e deu
errado* — e cada história virou exatamente uma coisa: uma tarefa de mitigação, um risco com
mitigação nomeada, um risco aceito com a razão, ou um corte em `## Out of Scope`. Duas histórias não
viraram nada e estão registradas como tal no fim.

### A crítica que mais dói, e ela é aceita em vez de respondida

**ACCEPTED — a 26 comandos esta política não economiza praticamente nada, e o spec não deve ser
vendido como se economizasse.** Medido: os 14 comandos de descrição completa custam 11.940 dos 12.875
caracteres (92,7%), e praticamente todos os 14 satisfazem o critério de admissão de `## Proposal` —
os quatro aligns e os oito comandos de ciclo são alcançados por fala **e** nomeados por conductor,
e os dois `/skill:*:new` são alcançados por fala. Sobra como candidato à classe typed-only,
essencialmente, o conjunto das descrições curtas, que soma **935 caracteres**. Ou seja: aplicar isto
hoje pode fechar o `sk-budget-ceiling` e nada mais.

O que este spec compra a 26 comandos não é um corte, é **um custo que para de crescer com n** — mais
a medição que falta e os dois instrumentos que hoje discordam. O corte só aparece com o crescimento.
Aceito com a razão dita em voz alta, porque a alternativa é vender um número que a medição não
sustenta; e o gatilho de reversão está em `## Open Decisions` item 5: se a superfície não passar de
~40 comandos, a resposta certa é a forma D de `## Alternatives Considered` e este spec encolhe para o
grupo 0 mais o grupo 1.

### Riscos com mitigação nomeada

- **Um estágio de conductor é classificado como typed-only e o conductor roda sem fazer nada.** É a
  história mais provável do premortem, e por uma razão específica: `/docs:harness`,
  `/docs:import-memory` e `/docs:glossary-backfill` são estágios invocados por nome **e** digitáveis
  por um humano, então "um humano digita isto" parece bastar como critério e não basta. Detecção
  hoje: **nenhuma** — `budget` reporta 0, `doctor` passa, `lint` não olha, e o conductor não falha,
  só não faz nada. Mitigação: a tarefa 1.3 entrega o finding derivado dos corpos, e a ordem de
  `## Design` §D4 o põe **antes** de qualquer reclassificação.
- **Uma ferramenta de captura para de ser alcançada por fala.** `/docs:learn`, `/docs:define` e
  `/docs:add` são alcançadas falando; classificá-las como typed-only é a **única** mudança visível ao
  usuário que este spec pode causar. Detecção: silenciosa — o usuário recebe uma resposta em vez de um
  doc capturado. Mitigação: o critério de admissão põe "alcançado sem digitar o nome" como condição
  suficiente, e `plugins/quenching/assets/checks/functional-checks.sh:243` já mede uma delas
  (`"add a standard: we always use snake_case for database columns"` → `quenching:docs:add`, contra
  uma descrição de 76 caracteres).
- **O flag typed-only usado como atalho para fechar o teto.** `context-budget.md` §*The one command
  that costs nothing* já proíbe isso em prosa — *"only honest when typed-only is the right design,
  never as a way to dodge the measurement"* — e prosa não detecta nada. Mitigação: a divisão que a
  tarefa 1.2 põe no `budget --json` torna a razão visível; sem ela, uma queda de 12.875 para 3.000 é
  indistinguível de uma melhora.
- **A tabela de 26 linhas da tarefa 3.1 recebe um "ok" global de um humano cansado.** Mitigação: a
  parte mecanicamente derivável — quem é alcançado por nome — vem do instrumento da tarefa 1.3, não
  do julgamento; só as linhas fora desse conjunto são decisão humana, e são as de risco baixo.
- **O estouro por crescimento de descrição continua silencioso depois deste spec.** Re-medir o teto
  não faz ninguém executar `budget`: `CLAUDE.md` §*Operating this repo* lista `doctor` e `lint` e não
  lista `budget`, que é justamente por que os +149 passaram. Mitigação: tarefa 2.3 põe a execução na
  rotina, e é a mitigação mais barata deste spec inteiro.
- **`restore-routing-info-on-docs-commands` pousa primeiro e o teto é re-medido duas vezes em
  direções opostas.** Sibling em desenvolvimento paralelo, aprovação retida. Ele engorda onze
  descrições e re-mede o teto para cima; este spec decide residência e re-mede depois. Fronteira que
  este spec mantém: **nenhum texto de descrição é escrito ou encurtado aqui**, então os dois diffs não
  colidem em arquivo nenhum a não ser `skills.py` `DEFAULT_CEILING`, `context-budget.md` e
  `README.md` — os três lugares que transcrevem o teto, e a regra de ambos é a mesma: o número vem de
  uma execução. Registro de fato, sem resolver nada: aquele spec afirma ser "the **second** firing
  and the first caused by description growth", e a medição desta árvore mostra que o disparo por
  crescimento de descrição **já aconteceu** (+149 desde `a03f31a`), antes de ele pousar. Os dois
  specs também carregam 12.726 como baseline, e o disco diz 12.875.
- **`restructure-claude-front-namespace` renomeia os caminhos que esta política classifica.** Sibling.
  Ele move `commands/skill/**` para `commands/automation/**` e leva `/docs:harness` — um estágio
  invocado por nome — para outro namespace. Fronteira: este spec nunca decide um caminho nem um nome.
  Mitigação estrutural: o instrumento da tarefa 1.3 **deriva** o conjunto alcançável por nome dos
  corpos de comando, então uma renomeação em massa muda os caminhos e não invalida o check.
- **`skills.py` viaja para outros repositórios.** Um repo com cópia antiga não conhece o finding novo
  nem a divisão no `budget`. Ruído, não quebra — e é a razão de `skills.py --version` estar no
  conjunto do lockstep (tarefa 1.4).

### Riscos aceitos, com a razão

- **ACCEPTED — o spike mede uma versão do Claude Code, não um contrato publicado.** A mecânica de
  hoje foi medida em 2.1.215 e pode mudar. Aceito porque
  [claude-code-skill-command-mechanics.md](/docs/reference/tools/claude-code-skill-command-mechanics.md)
  existe exatamente para isso: a linha nova entra com data e versão na tabela §Re-measurements, que é
  a disciplina que aquele doc pede e raramente recebe.
- **ACCEPTED — este spec não mede se o roteamento por prosa degrada com o tamanho da superfície.**
  Ninguém mediu essa curva, e `/skill:eval` mede um comando, não uma superfície. Aceito porque a
  alternativa é construir uma bancada de avaliação de superfície inteira antes de poder fechar um teto
  que já está estourado — e porque nenhuma entrega daqui encurta um texto de descrição, então não há
  nada para o roteamento perder além de residência.
- **ACCEPTED — a projeção de ~250 comandos é uma expectativa humana, não uma medição.** Sua única
  fonte no repositório é `restore-routing-info-on-docs-commands` linha 455, que a cita como uma
  declaração. Aceito porque a mitigação é estrutural e não custa nada: toda entrega deste spec paga a
  26 comandos — a medição que falta, os dois instrumentos que discordam, o teto estourado hoje — e
  nenhuma tarefa depende de o crescimento acontecer.

### Duas histórias do premortem que não viraram nada, e por quê

- **"Um comando ficou inalcançável pelos dois caminhos."** Já coberto: `sk-unreachable`
  (`skills.py:877`, severidade `error`) pega `user-invocable: false` combinado com
  `disable-model-invocation: true`. Nada a acrescentar.
- **"A classe typed-only cresceu sem limite e ninguém mede o total dela."** Converte em nada porque
  não há custo agregado para limitar: uma descrição typed-only é lida quando alguém digita o comando,
  e os caps por comando (`sk-metadata-cap` 1.536 `error`, `sk-description-portable` 1.024 `warn`)
  continuam valendo comando a comando. Registrado para que ninguém a redescubra como risco.

## Handoff

Estado da árvore após o grupo 0 (0.1, 0.2, 0.3 commitados). Grupo 0 verificado: `okf-validate.py docs`
sai 0 — 25 avisos, todos `stale-doc` pré-existentes, nenhum em arquivo que este spec tocou.

**A mecânica está medida e BLOQUEIA os dois caminhos** (Claude Code 2.1.220, dois braços com controle,
verificado no sistema de arquivos): descrição fora da listagem **e** invocação por nome pelo Skill tool
recusada, com o host nomeando o campo — `Skill quenching:zzprobeb cannot be used with Skill tool due to
disable-model-invocation`. Está na linha 7 de `docs/reference/tools/claude-code-skill-command-mechanics.md`.

**Decisões fechadas — não re-decidir.** Ver `## Open Decisions` para o registro completo.

- item 1 → bloqueia também por nome (observado, não por ambiguidade);
- item 2 → `skills.md` **ganha a medição**; a célula estava certa e passa a citar a linha 7. Sem cascata;
- item 5 → **~250 é o alvo; construir o spec inteiro**, grupos 1, 2 e 3;
- item 6 → severidade do finding de 1.3 é **`error`**;
- itens 3 e 4 seguem abertos por projeto (são da 3.1 e da execução de `budget` depois dela).

**O que o grupo 3 vai encontrar, já medido — não é uma surpresa a descobrir na 3.1.** 26 comandos,
12.875 chars, teto 12.726, estourado em 149. 15 descrições completas = 12.816 chars (99,5%); 11 curtas
= 935. Das onze curtas, três (`/docs:harness`, `/docs:import-memory`, `/docs:glossary-backfill`, 217
chars) são estágios alcançados **por nome** e agora estão duramente excluídas; as outras são alcançadas
por fala, que o critério também exclui. **A 3.1 deve classificar zero ou perto de zero.** Quem fecha o
estouro é a 3.2, não a reclassificação.

**Armadilha para a 1.3.** Um `grep -rhoE 'quenching:[a-z-]+(:[a-z-]+)*' commands/` casa **25 dos 26**
comandos — porque as fronteiras `Not for: X → /outro-comando` e as citações em prosa mencionam nomes
sem os invocar. O conjunto real alcançável-por-nome é ~12 (`## Design` §D3). O instrumento da 1.3 tem
de distinguir **invocação pelo Skill tool** de **menção**, ou vai marcar a superfície inteira.

**Ambiente, que difere do que o spec assume.** O plugin vivo nesta máquina é a instalação user-scope
`quenching@quenching` em `~/.claude/plugins/cache/quenching/quenching/4.4.0/`, **não** a árvore de
trabalho. Ver `## Discoveries`.

**Números de linha de `skills.py` em `## Impact`/`## Design` estão defasados** — trabalhar por conteúdo.
`budget_rows` ~1667 (condição do campo ~1674), `_lint_invocation` ~921 (`sk-unreachable` ~931).

Isolamento: worktree em `../claude-quenching-route-commands-without-always-on-descriptions`, branch
`plan/route-commands-without-always-on-descriptions` sobre `main`.

**Próximo: grupo 1**, as três tarefas que tocam o mesmo arquivo (`skills.py`) e por isso não são `[P]`,
mais o lockstep da 1.4. `verification: per-section` — a verificação roda ao fim do grupo, não por tarefa.
## Tasks

Ordenado por `## Design` §D4: medir, instrumentar, escrever a política, só então classificar. Nada é
reclassificado antes de existir o check que pega o erro de classificação. `SK` abaixo é
`python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching`.

Nenhuma tarefa carrega `[P]`: as três do grupo 1 tocam o mesmo arquivo, e as do grupo 2 escrevem em
`docs/`, o que `specs.py parallel` nunca considera elegível.

### 0. Medir a mecânica que todo o resto assume

- [x] 0.1 Medir, em uma sessão `claude -p` **nova** e contra um comando descartável, se
      `disable-model-invocation: true` bloqueia (a) a seleção autônoma pelo modelo e (b) a invocação
      **por nome** pelo Skill tool. Reverter o arquivo de probe nos dois casos. Ambiguidade conta como
      "bloqueia", por `## Open Decisions` item 1. Sessão nova porque o registry é construído no início
      da sessão.
      files: plugins/quenching/commands/zzprobe.md (descartável, revertido ao fim)
      pattern: specs/archive/2026-07-26-skill-description-tiering.md §Discoveries — o método do spike
      subject: plan/route-commands-without-always-on-descriptions: 0.1 medir a mecânica de disable-model-invocation
      anterior, incluindo o cuidado de verificar no sistema de arquivos em vez de acreditar no
      auto-relato do probe
- [x] 0.2 Registrar o resultado de 0.1 em
      `docs/reference/tools/claude-code-skill-command-mechanics.md`: uma linha na tabela
      §*The findings* com status Observed ou Inferred, a subseção que a explica, e a entrada em
      §*Re-measurements* com data e versão do binário. Registrar mesmo se o resultado vier ambíguo —
      um resultado ambíguo registrado é o que impede o próximo leitor de suprir a afirmação, que é o
      modo de falha que aquele doc documenta.
      files: docs/reference/tools/claude-code-skill-command-mechanics.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
      subject: plan/route-commands-without-always-on-descriptions: 0.2 registrar a medição em claude-code-skill-command-mechanics
- [x] 0.3 Decidir com o humano, contra o resultado de 0.1, os itens 1, 2, 5 e 6 de
      `## Open Decisions` — a mecânica, o que acontece com `skills.md`, se a projeção de ~250 é o alvo,
      e a severidade do finding de 1.3. Sem a resposta do item 5 os grupos 2 e 3 não têm justificativa,
      e sem a do item 6 a tarefa 1.3 não tem critério.
      subject: plan/route-commands-without-always-on-descriptions: 0.3 decidir os itens 1, 2, 5 e 6 contra a medição

### 1. Fechar a discordância entre os dois instrumentos

- [x] 1.1 Extrair o predicado "esta descrição está em contexto?" de `budget_rows`
      (`skills.py:1439`) para um helper, e escopar `sk-trigger-position` e `sk-no-boundary` por ele, de
      modo que `lint` e `budget` leiam a mesma condição de um lugar só. Entregar junto o caso de
      `selftest` que demonstra a regra, porque na superfície real ela é hoje inobservável.
      files: plugins/quenching/assets/bin/skills.py
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json
      subject: plan/route-commands-without-always-on-descriptions: 1.1 extrair description_is_resident e escopar os dois códigos de roteamento
- [x] 1.2 Fazer `budget --json` reportar a divisão por classe — contagem e caracteres de roteada e de
      typed-only — para que uma queda de custo obtida por reclassificação seja distinguível de uma
      obtida por escrever menos.
      files: plugins/quenching/assets/bin/skills.py
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching budget --json
      subject: plan/route-commands-without-always-on-descriptions: 1.2 reportar a divisão roteada/typed-only no budget
- [ ] 1.3 Adicionar em `_lint_invocation` o finding que esta política torna necessário: um comando
      **nomeado pelo corpo de outro comando** carregando `disable-model-invocation: true`, com o
      conjunto de alvos derivado de `commands/**` e não de lista fixa, para sobreviver à renomeação que
      `restructure-claude-front-namespace` propõe. Severidade por `## Open Decisions` item 6. Provar por
      caso no `selftest`, nunca editando a superfície real.
      files: plugins/quenching/assets/bin/skills.py
      verify: python3 plugins/quenching/assets/bin/skills.py selftest
- [ ] 1.4 Lockstep de versão, porque `skills.py` mudou: `VERSION`, `plugin.json`, o manifest do
      marketplace e o `--version` das outras duas ferramentas movem juntos.
      files: plugins/quenching/VERSION, plugins/quenching/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/hooks/okf-validate.py
      verify: python3 plugins/quenching/assets/bin/skills.py --version

### 2. Escrever a política antes de aplicá-la

- [ ] 2.1 Escrever `docs/standards/automation/context-budget.md` (`authority: background`, mantido):
      o tier que falta em §*What the description may carry* para uma descrição que não está em
      contexto, a divisão que `budget` agora reporta, e o modo de disparo do ratchet por **crescimento
      de descrição** — medido, +149 sobre `/specs:execute`, `/specs:develop` e `/specs:conclude` desde
      `a03f31a`, com `budget` saindo 1 e nada na rotina do repositório executando `budget`.
      files: docs/standards/automation/context-budget.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
- [ ] 2.2 Escrever `docs/standards/automation/skills.md`: o critério de admissão à classe roteada em
      §*Invocation and permission are authored decisions*, e a célula da tabela de invocação sobre
      invocação por nome passando a citar a linha medida em 0.2 — ou reescrita para dizer o que se sabe,
      se 0.1 a contradisser, conforme `## Open Decisions` item 2.
      files: docs/standards/automation/skills.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
- [ ] 2.3 Pôr `budget` no bloco de verificação de `CLAUDE.md` §*Operating this repo*, ao lado de
      `doctor` e `lint`. É a mitigação mais barata deste spec: sem ela, re-medir o teto não faz ninguém
      executar o instrumento, e o próximo estouro por crescimento de descrição passa igual.
      files: CLAUDE.md
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching budget --json

### 3. Classificar com confirmação, e re-medir o teto

- [ ] 3.1 Propor ao humano UMA tabela com todos os 26 comandos contra o critério escrito em 2.2 — a
      coluna alcançável-por-nome vinda do instrumento de 1.3, não de julgamento — e aplicar só as linhas
      aprovadas. Apenas frontmatter de invocação: nenhum texto de descrição é alterado, nenhum caminho é
      movido.
      files: plugins/quenching/commands/**
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json
- [ ] 3.2 Re-medir o teto de uma execução de `budget` e transcrever o número nos três lugares que o
      guardam — `skills.py` `DEFAULT_CEILING`, `context-budget.md` e `README.md` §*Cost model* — nunca
      estimá-lo, que é a regra do próprio padrão.
      files: plugins/quenching/assets/bin/skills.py, docs/standards/automation/context-budget.md, plugins/quenching/README.md
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching budget --json

### 4. Provar

- [ ] 4.1 Os três instrumentos concordam: `budget` sai 0 com `ok: true` e `total` igual ao teto
      transcrito, `lint` sem `sk-trigger-position` nem `sk-no-boundary` contra comando fora de contexto,
      `doctor` com 26 comandos e `ok: true`.
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching budget --json && python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json && python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json
- [ ] 4.2 Os três selftests e o bundle OKF continuam limpos, sem aviso novo nos arquivos que este spec
      tocou.
      verify: python3 plugins/quenching/assets/bin/skills.py selftest && python3 plugins/quenching/assets/bin/specs.py selftest && python3 plugins/quenching/assets/hooks/okf-validate.py selftest && python3 plugins/quenching/assets/hooks/okf-validate.py docs
- [ ] 4.3 Confirmar o que a classe typed-only promete: um comando reclassificado continua com a
      descrição inteira no arquivo e continua com `total: 0` e `alwaysOn: false` no `budget`. A metade
      "continua digitável no menu `/`" é checagem **manual** e tem de ser dita como manual no relatório,
      porque nenhum instrumento deste repositório observa o menu.
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching budget --json

## Discoveries

- 0.1: o probe teve de ser instalado na raiz VIVA do plugin (~/.claude/plugins/cache/quenching/quenching/4.4.0/commands/), nao no caminho declarado plugins/quenching/commands/ — nesta maquina o quenching carregado e a instalacao user-scope quenching@quenching vinda do git, e a arvore de trabalho nao e o plugin vivo. Qualquer spike futuro sobre a superficie precisa resolver a raiz viva antes de escrever o probe.
- 0.1: a versao medida e Claude Code 2.1.220, nao a 2.1.215 que claude-code-skill-command-mechanics.md registra como base de todas as suas linhas. Nenhuma outra linha daquele doc foi re-medida contra a 2.1.220 por este spec.
- specs.py next quebra o campo files: de 0.1 em duas entradas (plugins/quenching/commands/zzprobe.md (descartavel + revertido ao fim)) — o parser separa por virgula sem respeitar parenteses, entao um comentario entre parenteses num files: vira um caminho falso para o executor.
- Os numeros de linha que ## Impact e ## Design citam de skills.py estao defasados: budget_rows/1436-1439 esta hoje em ~1667-1674 e _lint_invocation/861-877 em ~921-931. Trabalhar por conteudo, nunca por linha.
- 0.2: o baseline que ## Validation afirma para okf-validate.py docs esta defasado — ele diz 'avisos stale-doc pre-existentes em tres docs nao relacionados'; a medicao de 2026-08-02 nesta arvore da 0 error(s), 25 warning(s), TODOS stale-doc e todos pre-existentes. Nenhum sobre reference/tools/. O spec 2026-08-01-stale-doc-mass-aging e o dono disso.
- 1.1: o baseline de lint em ## Validation esta defasado — diz 35 findings; a arvore (inclusive em main, antes de qualquer mudanca deste spec) da 36: 11 sk-trigger-position, 10 sk-no-boundary, 9 sk-step-criterion, 5 sk-unscoped-bash e 1 sk-bare-citation que o spec nao lista.
- 1.1: escopar os dois codigos por description_is_resident nao muda NADA na superficie real (11/10 antes e depois) — /skill:retro, o unico typed-only, carrega gatilho e fronteira. A regra so existe provada pelo caso de selftest, e o caso foi verificado por mutacao: trocar o if por True faz o selftest FALHAR com 'expected routing codes [], got [sk-no-boundary, sk-trigger-position]'.
