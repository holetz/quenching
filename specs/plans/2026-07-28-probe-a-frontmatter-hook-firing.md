---
slug: probe-a-frontmatter-hook-firing
title: No probe observes a frontmatter hooks: block actually fire
verification: per-section
priority: {level: 17, criticality: high, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# No probe observes a frontmatter hooks: block actually fire

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

Este repo instalou pequenos gatilhos automáticos — hooks — que rodam sozinhos depois que um comando
grava um arquivo. Três comandos de documentação carregam um desses gatilhos, e o repo já tratou isso
como funcionando: um verificador leu a configuração, achou tudo bem formado, e a regra que descreve o
assunto foi promovida a contrato vigente. **Ninguém nunca viu um desses gatilhos disparar de verdade.**

`## Problem` mostra por que a distinção não é preciosismo, com um caso acontecendo agora mesmo: há
dois gatilhos registrados neste repositório apontando para um arquivo que foi apagado, eles falham a
cada gravação, e nenhuma checagem do repo percebeu. `## Design` explica a razão técnica de nada
perceber — o único harness capaz de abrir uma sessão nova e medir o que ela fez enxerga apenas chamadas
de ferramenta, e um gatilho disparando não é uma chamada de ferramenta — e mostra a saída: observar o
rastro que o próprio verificador deixa em disco quando roda.

`## Proposal` lista o que passa a ser verdade; `## Tasks` é a rota, em seis grupos, e
`## Validation` é como qualquer pessoa confere — incluindo três formas de **quebrar** o check de
propósito, porque um check que nunca foi visto reprovar não é um check. `## Impact` declara os dois
padrões que a medição prova e nomeia a única linha de código fora do harness que muda: um comentário.

`## Out of Scope` marca a fronteira mais fácil de atravessar por engano — este spec constrói o
observador e **não** conserta a configuração quebrada, porque ela é a única prova viva que a medição
tem. `## Alternatives Considered` guarda as quatro rotas mais baratas e por que cada uma prova menos.

Duas coisas ficam abertas de propósito, e vale ler antes de começar: `## Open Decisions` registra que
a medição que fundamenta todo o desenho foi feita num comando de projeto e **não** num comando de
plugin, que é onde os três blocos realmente vivem — fechar isso é a primeira tarefa, e se a resposta
for negativa o spec para em vez de continuar. `## Risks` diz o que o check novo não cobre, para que
um resultado verde não seja lido como mais do que ele mede. `## Handoff` reúne os fatos já medidos
para que nenhum executor os re-derive.
## Problem

`instrument-and-extend-skill-front` acrescentou blocos `hooks:` de frontmatter a `/docs:add`,
`/docs:learn` e `/docs:define`, ensinou `skills.py lint` a lê-los, e graduou
`docs/standards/automation/hooks.md` para `authority: current` sobre essa superfície adotante.

**Nada observou um deles disparar.** Os três blocos parseiam limpos e `lint` reporta zero findings de
hook — mas o registro de comandos é construído no início da sessão, então um bloco escrito numa
sessão é inerte nessa mesma sessão. Toda afirmação sobre eles é verificada-por-parser e não
verificada-por-execução, que é exatamente a distinção que o front `.claude/` foi instrumentado para
parar de aceitar.

**A causa não é "ninguém escreveu a probe" — é que o canal de evidência do harness é cego a hooks.**
`plugins/quenching/assets/checks/functional-checks.sh` é o único harness do repo que abre um
`claude -p` novo e assere sobre chamadas de ferramenta capturadas, e seu extractor `tools()`
(linhas 80-91) lê **apenas** eventos `tool_use` do `--output-format stream-json`. **Um disparo de
hook não é um `tool_use`.** Medido em 30/07/2026 numa box descartável, com um bloco `hooks:` de
frontmatter idêntico ao dos três comandos: o hook disparou de fato — o handler gravou seu próprio
arquivo em disco — e a **única** menção a ele no capture é a prosa do assistente descrevendo o que
tinha acontecido. Assertar sobre isso é o self-report que
`docs/standards/quality/surface-verification.md` §"Assert on what the process did, never on what it
said" proíbe. Nenhuma das onze asserções atuais toca um hook, e nenhuma delas **poderia**, pelo canal
que elas usam.

**Por que agora: o modo de falha acabou de acontecer neste repositório, e nada notou.**
`.claude/settings.json` registra dois hooks — um `PostToolUse` casado em `Write|Edit` (rung 2) e um
`Stop` sem matcher (rung 3) — ambos rodando
`python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/okf-validate.py`, e **nenhum dos dois leva a guarda**
`test -f "{caminho}" || exit 0` que a Policy default do próprio `docs/standards/automation/hooks.md`
exige. O commit `193578c` ("Removing hooks/scripts in the repo", 29/07/2026 10:44:17 -0300) apagou
`.claude/hooks/okf-validate.py` e deixou o registro em pé. Desde então **todo `Write` e todo `Edit`
neste repo volta com erro de hook**. Os transcripts de sessão em
`~/.claude/projects/-home-holetz-Projects-claude-quenching/` datam a regressão: 42 eventos
`type: "system"` carregando `hookCount`, os 40 primeiros verdes (`hookErrors: []`) até
`2026-07-29T13:17:45Z`, e os dois seguintes vermelhos a partir de `2026-07-29T14:20:02Z`, com
`hookErrors: ["Hook script appears to be missing — ... exited 2 with: python3: can't open file
'/home/holetz/Projects/claude-quenching/.claude/hooks/okf-validate.py'"]`. É um
hook-registrado-que-não-dispara observado em produção, não em tese.

**Nenhuma checagem do repo notou, e estruturalmente não poderia.** `_wider_findings`
(`plugins/quenching/assets/bin/skills.py:998`) é o único lugar que lê hooks de `settings*.json`, e só
é alcançado por `doctor`; o `.claude/` daqui contém **apenas** `settings.json`, sem `commands/`, então
`skills.py doctor --root .claude` sai antes com `sk-no-surface`, e o `--root plugins/quenching` que o
CLAUDE.md prescreve nunca vê `.claude/settings.json`. E mesmo alcançado, `hook_ladder_findings`
(`skills.py:1036`) checa só matcher vazio e tipo de handler, sobre
`TOOL_EVENTS = ("PreToolUse", "PostToolUse")` (`skills.py:140`): nunca checa se o script de um handler
`command` existe ou está guardado, e `Stop` está fora de `TOOL_EVENTS`. Um hook morto é invisível dos
dois lados — em processo e fora dele.

A lacuna se ampliou no conclude daquele spec. A revisão de branch achou que os três blocos apontavam
para um `okf-validate.py` que `/docs:align` apenas *oferece* instalar, então
`python3 {arquivo-ausente}` saía 2 — um erro sob o protocolo de hook — em todo `Write`/`Edit` de
qualquer repo que recusou a oferta. Uma guarda `test -f … || exit 0` agora encabeça cada bloco.
**Essa guarda também não foi observada**: foi provada num shell, não num hook disparando. Uma probe
que assere que um bloco rung-1 roda cobre a graduação e a guarda juntas.

Descoberto por `instrument-and-extend-skill-front`; a metade da guarda acrescentada no conclude dele.

## Proposal

- `assets/checks/functional-checks.sh` ganha o **check 5**: uma sessão `claude -p` nova, numa box
  descartável, prova que o bloco `hooks:` de frontmatter de um comando **do plugin** dispara de fato
  quando esse comando escreve na bundle.
- A asserção positiva é o **efeito colateral do handler real**, nunca a prosa da sessão: o marcador
  dirty que `okf-validate.py` grava no braço `PostToolUse` (`_touch_marker`,
  `assets/hooks/okf-validate.py:1326`) existe depois da sessão e não existia antes dela.
- A asserção negativa roda a mesma frase na mesma forma de box **sem** `.claude/hooks/okf-validate.py`
  instalado, e prova que a guarda `test -f … || exit 0` transforma o bloco num no-op: nenhum
  marcador, e nenhum erro de hook no transcript da sessão.
- Nenhuma das duas asserções pode passar vazia: cada uma é condicionada a evidência de que a sessão
  **escreveu** um arquivo, do mesmo jeito que `evidence()` já condiciona as onze asserções
  existentes.
- `docs/standards/quality/surface-verification.md` passa a registrar o fato que ninguém tinha medido:
  um disparo de hook não é um `tool_use` e é invisível ao capture `stream-json`, então uma propriedade
  de hook se verifica por artefato em disco e não pelo stream.
- `docs/standards/automation/hooks.md` passa a dizer que a graduação do rung 1 é **observada**,
  nomeando o check que a observa — e a frase que hoje afirma uma fiação viva em
  `.claude/settings.json` passa a dizer o que foi medido: registrada e morta.
- O check 5 é **opt-in** (`--only 5`), fora do conjunto default `1,2,4`, e a tabela de custo de
  `surface-verification.md` ganha a linha que diz quando rodá-lo.
- Depois deste spec, a afirmação "o bloco `hooks:` dispara" deixa de ser inferência de parser em
  qualquer sessão futura: existe um comando que a mede, e ele reprova se ela deixar de ser verdade.

## Out of Scope

- **Consertar `.claude/settings.json`.** É o vizinho mais fácil de confundir com escopo. Este spec
  **constrói o observador**, não a reparação — e a fiação morta é a única evidência em produção que a
  probe tem para justificar sua existência; consertá-la antes de a probe existir apagaria o caso.
  O reparo vai reportado como oferta (`/skill:hook:new`, que é dono do merge em `settings.json`),
  nunca aplicado aqui.
- **Um check estático de "o script do handler existe".** Seria um código `sk-*` novo em `skills.py`:
  outro front, outro ladder, e in-process — exatamente a classe de verificação que este spec existe
  para complementar, não para substituir. Fica registrado em `## Risks` como lacuna aceita, com o
  follow-up nomeado.
- **Observar os rungs 2 e 3.** A probe cobre o rung 1, que é o rung graduado e o único que nenhum
  outro instrumento alcança. A fiação de `settings.json` é observável **sem** sessão de agente — os
  próprios transcripts a datam — e pagar uma sessão por ela seria comprar de novo o que já se tem.
- **O destino do check 3.** Continua opt-in, com `/skill:eval` como instrumento preferido para
  roteamento falado. `surface-verification.md` decidiu isso em 29/07/2026 com evidência medida sobre
  todo o `specs/archive/`, e revogar uma decisão de padrão exige a mesma barra que a produziu.
- **De qual cópia do plugin os checks carregam, e onde as probes escrevem.** As duas metades são dos
  siblings `plugin-dir-for-functional-checks` e `isolate-functional-checks-probes`. O check 5 herda o
  que eles decidirem e não redecide nenhuma das duas.
- **Instalar `okf-validate.py` no repo alvo por padrão.** A instalação continua uma *oferta* do passo
  6 de `/docs:align`. A probe instala a cópia dentro da própria box porque é precondição do que ela
  mede (precondição 3 de `surface-verification.md`), e isso não muda nada fora da box.
- **O bump de versão.** Uma mudança em `assets/checks/` não é um dos seis artefatos do lockstep, e
  `docs/standards/ci-cd/versioning-release.md` §"When the bump happens" proíbe bump como tarefa: ele
  é o passo 5 de `/specs:conclude`, imediatamente antes do merge.
- **Assertar o texto do finding que o validador emite.** Corte de escopo tomado na revisão adversarial:
  casar redação de mensagem, ou `hookAdditionalContext`, acopla o check à prosa de `okf-validate.py` e
  o faz reprovar a cada ajuste de texto. O marcador prova a afirmação inteira do spec sem esse
  acoplamento — ver `## Design` §"O que a probe deliberadamente NÃO assere".
## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/quality/surface-verification.md` — que um disparo de hook não é um `tool_use` e é
  invisível ao capture `stream-json`, logo uma propriedade de hook se verifica pelo artefato que o
  handler real deixa em disco; mais a linha nova na tabela de custo dizendo quando rodar o check 5.
- `docs/standards/automation/hooks.md` — que a graduação do rung 1 passou a ser **observada**, com o
  check que a observa nomeado; e a correção da frase que hoje afirma uma fiação viva em
  `.claude/settings.json`, para o que foi medido: registrada e morta desde `193578c`.

Os dois são **edições em padrões existentes**, não docs novos, e cada um é nomeado por uma tarefa —
`sp-impact-uncovered` casa pelo caminho no texto da tarefa.

### Standards at `authority: background` this spec may resolve

- `docs/standards/automation/session-evidence.md` — não resolve, mas **encosta**: o braço "ler o
  transcript da sessão" desta probe é o mesmo canal que `session.py` já resolve
  (`resolve_transcript`/`encode_cwd`), e a arm negativa o usa para provar ausência de
  `hook_blocking_error`. Se esse uso se provar, é evidência para a graduação daquele padrão — mas a
  graduação é julgamento dele, não deste spec, e este spec não a reivindica.

### Product code this spec expects to touch

- `plugins/quenching/assets/checks/functional-checks.sh` — o check 5 e as duas arms; `newbox` ganha
  `docs/knowledge/glossary.md` e `docs/knowledge/index.md`; o header ganha o custo e o seletor do 5.
- `plugins/quenching/assets/hooks/okf-validate.py` — **um comentário e nada mais**, em `_marker_path`
  (linha 216), nomeando o check 5 como consumidor do caminho do marcador. Nenhuma mudança de
  comportamento, e portanto nenhuma obrigação de lockstep.

Nada em `plugins/quenching/commands/**` muda: os três blocos `hooks:` são o **sujeito** da medição, e
editá-los invalidaria a medição.

## Validation

A prova é o próprio check, rodado das duas formas — verde quando deve, vermelho quando deve:

```bash
cd /home/holetz/Projects/claude-quenching
./plugins/quenching/assets/checks/functional-checks.sh --only 5
```

Deve imprimir as duas asserções como `PASS` e fechar em `2 passed, 0 failed`, com `exit 0`:

```
5. a frontmatter hooks: block fires, and its guard no-ops when the handler is absent
  PASS   the dirty marker appeared after the session (the rung-1 block fired)
  PASS   no marker and no hook_blocking_error with the handler absent (the guard no-ops)
```

**A arm de vermelho deliberado é obrigatória, não opcional.** Um check que nunca foi visto reprovar
não é um check:

```bash
# 1. quebre a arm positiva: remova a cópia instalada do handler DENTRO da box positiva
#    esperado: a primeira asserção vira FAIL, nunca SKIP
# 2. quebre a arm negativa: apague a guarda `test -f … || exit 0` do bloco do comando portador
#    esperado: a segunda asserção vira FAIL — e a guarda volta antes do commit
# 3. quebre a evidência: faça a frase da probe não escrever nada
#    esperado: as DUAS asserções viram SKIP (inconclusive) e o run sai 2, jamais 0
```

O passo 3 é o que separa este check dos que `surface-verification.md` §precondição 4 documenta como
tendo passado por vacuidade. Se ele não sair 2, a condição de evidência está errada.

Invariantes que continuam valendo depois da mudança:

```bash
cd plugins/quenching
python3 assets/bin/skills.py --root . doctor --json   # 26 commands, no findings
python3 assets/bin/skills.py --root . lint  --json    # exit 0
python3 assets/bin/skills.py --root . lint  --json | grep -c 'sk-hook'   # 0 — nenhum finding de hook novo
python3 assets/hooks/okf-validate.py --version        # segue igual ao VERSION: só um comentário mudou
python3 assets/hooks/okf-validate.py selftest
./assets/checks/functional-checks.sh                  # o default segue 1,2,4 e segue verde
```

E o corte de custo, verificável por leitura: `ONLY` continua com default `1,2,4`
(`functional-checks.sh:48`), então nenhum run existente fica mais caro.

## Design

### O canal de evidência, medido antes de projetar

Três canais existem, e só um serve. Medido em 30/07/2026, com um bloco `hooks:` de frontmatter em
`.claude/commands/` de uma box descartável, `PostToolUse` casado em `Write|Edit`, handler `command`:

| Canal | O que carrega de um disparo | Serve? |
| --- | --- | --- |
| capture `--output-format stream-json --verbose` | nada estruturado. Zero chave `hook*`. O único vestígio é a prosa do assistente contando que um hook disparou | **não** — é self-report, proibido por `surface-verification.md` §"Assert on what the process did" |
| transcript da sessão, `~/.claude/projects/{cwd-codificado}/{id}.jsonl` | no **fracasso**, um evento `type: "attachment"` com `attachment.type == "hook_blocking_error"`, `hookName`, `hookEvent` e o `command`. No **sucesso** de um bloco rung-1, nada | **só metade** — mede o vermelho, é cego ao verde |
| efeito colateral do handler em disco | o que o handler real gravar, verificável por `test -f` depois da sessão | **sim** |

A assimetria da linha do meio é o achado que decide o desenho: um bloco rung-1 que sai 0 não deixa
vestígio nenhum, então uma asserção de sucesso lida do transcript passaria vazia sempre. Para a fiação
de `settings.json` o transcript é mais rico (eventos `type: "system"` com
`hookCount`/`hookInfos`/`hookErrors`/`hookAdditionalContext`, verdes inclusive), mas rung 2 está fora
de escopo.

### A decisão: assertar no marcador dirty do handler real

`okf-validate.py` grava exatamente uma coisa em disco, e ela é perfeita para isto. No braço
`PostToolUse`, depois de confirmar que o caminho tocado é um `.md` dentro da bundle, ele chama
`_touch_marker(project)` (`assets/hooks/okf-validate.py:1326`) — **antes** de validar e
independentemente de haver findings. O caminho é `_marker_path` (linhas 216-218):
`tempfile.gettempdir()` mais `okf-dirty-` mais os 12 primeiros hexdígitos de
`sha1(abspath(project))`. É determinístico, computável pela probe em uma linha de Python, e é um
artefato — o padrão "assere no que o filesystem pode ser perguntado" que
`assets/checks/conclude-order-check.sh` já usa para propriedades de ordenação.

Regra durável que isto estabelece: **uma propriedade de hook se verifica pelo artefato que o handler
real deixa, nunca pelo stream de ferramentas.** O stream é o canal certo para "o comando carregou e
citou seu reference"; ele não vê hooks e nunca verá, porque um hook não é uma chamada de ferramenta.

### As duas arms, e por que o par é obrigatório

`surface-verification.md` §"Assert the negative too" pede o par, e aqui ele é ainda mais necessário
que de hábito, porque as duas metades da afirmação graduada são opostas:

- **Arm positiva** — box com `.claude/hooks/okf-validate.py` instalado (cópia de
  `assets/hooks/okf-validate.py`) e uma bundle mínima. A probe apaga o marcador calculado, roda um
  comando portador do bloco escrevendo um `.md` sob `docs/`, e assere que o marcador **passou a
  existir**. Prova: o bloco disparou, com o handler real, e o handler classificou o caminho como
  conteúdo de bundle.
- **Arm negativa** — a mesma box **sem** o script instalado. A probe assere que o marcador **não**
  existe e que o transcript da sessão **não** carrega `hook_blocking_error`. Prova a guarda
  `test -f … || exit 0`: script ausente vira no-op silencioso, e não um finding sobre o handler.

### As três precondições que este check tem de satisfazer

Herdadas de `surface-verification.md` §"The five preconditions", aplicadas a este caso:

1. **Precondição 3 — satisfaça as precondições do comando, ou você mede a precondição.** O comando
   portador do bloco quer uma bundle OKF, e a arm positiva quer o handler instalado. `newbox` já
   monta a bundle mínima (linhas 126-136); a arm positiva acrescenta a cópia do script. Sem isso a
   sessão gasta os turnos procurando bundle e a probe reporta uma falha de hook que é uma falha de
   fixture.
2. **Precondição 4 — nada pode passar vazio.** As duas asserções são condicionadas a evidência de que
   a sessão **escreveu** um `.md` sob `docs/` — um `tool_use` de `Write`/`Edit` com esse `file_path`
   no capture, que é justamente o que o stream **sabe** reportar. Sem essa condição a arm negativa
   passa em qualquer sessão que não fez nada, e uma box quebrada reporta uma guarda funcionando.
3. **Precondição 5 — `--plugin-dir`, de uma box que habilita nenhum plugin.** É o que faz o check
   medir o bloco `hooks:` do checkout sob edição em vez do que o cache da marketplace serviu. Os
   quatro checks atuais já fazem isso; o 5 não abre exceção.

### Custo, e por que opt-in

Duas sessões de agente por run — a arm positiva e a negativa. O default fica `1,2,4`, inalterado.
`surface-verification.md` §"Scope the run to what the change can break" é a autoridade sobre quando
rodar, e a linha nova é: **mudou um bloco `hooks:` de frontmatter, ou o braço `PostToolUse` de
`okf-validate.py` → `--only 5`.** Um bloco `hooks:` muda quando `/skill:hook:new` cunha um, o que é
raro; cobrar duas sessões de todo run seria pagar caro por uma superfície quase estática.

### Contratos que este desenho não pode contradizer

- `docs/standards/quality/surface-verification.md` — processo novo por check, asserção sobre o que o
  processo fez, as cinco precondições, e o dono do harness é o front skill (não entra em `verify:` de
  tarefa nem em `## Validation` de outro spec).
- `docs/standards/automation/hooks.md` — a Policy default "a handler whose script may not be installed
  guards its own absence". A arm negativa é a prova executada dessa regra.
- `docs/standards/architecture/plugin-layout.md` — o check vive sob `assets/`, fora de `commands/**`,
  que é a única árvore registrada.
- O contrato de saída do harness: inconclusivo não incrementa `PASS`, e um run que não mediu nada sai
  **2**. As duas arms novas obedecem os mesmos `check`/`inconc` já definidos (linhas 70-72).

### O comando portador da probe

Qualquer um dos três comandos com bloco rung-1 serve, então a escolha é de custo de turnos.
`/docs:define` é o mais barato: acrescenta **um bullet** a um `docs/knowledge/glossary.md` que já
existe, sem decidir home nem inventar frontmatter. `/docs:learn` e `/docs:add` criam um doc novo e
gastam turnos escolhendo onde. Decisão: **`/docs:define`**, com `newbox` ganhando
`docs/knowledge/glossary.md` e `docs/knowledge/index.md`; se o corpo de `define` precisar de orientação
que estoure o cap de turnos, o fallback é `/docs:learn`, e a troca é uma linha.

A frase da probe **não nomeia o hook, nem o marcador, nem o validador** — pede só a definição de um
termo. É a regra de `surface-verification.md` §"The prompt must not name what the check looks for":
se a frase mencionasse o hook, um marcador presente poderia ser a sessão sendo prestativa em vez do
registro funcionando.

### O que a probe deliberadamente NÃO assere

Não assere o **conteúdo** do finding que o validador emite — nada de casar texto de mensagem, nem
`hookAdditionalContext`. O corte é de propósito: acoplar a probe à redação de uma mensagem compra 20%
a mais de cobertura por um check que reprova a cada ajuste de texto em `okf-validate.py`. A afirmação
do spec é "o bloco dispara", e o marcador prova isso inteiro. Se um dia a afirmação passar a ser "o
finding chega ao modelo", aí é outra asserção, e ela tem outro canal (`hookAdditionalContext`, no
transcript).

### A lacuna que este desenho aceita

O check 5 prova o rung 1 **disparando**. Ele não prova nada sobre um handler cujo script foi apagado
em `settings.json` — o defeito que este repo tem agora. Isso é deliberado e está aceito em
`## Risks`: a fiação de `settings.json` não precisa de sessão de agente para ser observada, e o
instrumento que teria pegado `193578c` é um check estático em `skills.py`, de outro front. Nomear a
lacuna aqui é o que impede alguém de ler um check 5 verde como "os hooks deste repo estão bem".
## Alternatives Considered

| Abordagem | Custo | O que compra | O que fecha |
| --- | --- | --- | --- |
| **A. Marcador dirty do handler real, duas arms** (escolhida) | duas sessões de agente, opt-in; uma cópia do script dentro da box | prova o bloco real, o handler real e a guarda, com asserção sobre artefato | nada — as outras opções continuam disponíveis por cima |
| B. Ler o transcript da sessão e assertar em `hook_blocking_error` | uma sessão; `session.py` já resolve o caminho do transcript | mede o **vermelho** com precisão e sem tocar em disco | é cega ao verde de um bloco rung-1, então não prova a graduação — só a falha |
| C. Payload sintético no handler (`echo '{...}' \| python3 okf-validate.py`) | quase zero, roda em processo | prova que o handler faz a coisa certa quando chamado | não prova **que ele é chamado**, que é a afirmação inteira do spec. É o que o passo 7 de `/skill:hook:new` já manda fazer, e é justamente a verificação-por-parser que este spec existe para superar |
| D. Não fazer nada | zero | mantém o harness em quatro checks e o custo onde está | deixa `hooks.md` graduado a `authority: current` sobre uma afirmação que nada mediu, e deixa a guarda provada em shell mas não em disparo |
| E. Trocar o handler por um stub que grava um marcador de teste | uma sessão, sem instalar `okf-validate.py` | mais simples de montar, marcador em caminho escolhido pela probe | prova que **um** bloco dispara, não que **este** dispara: o bloco sob teste é o dos três comandos, com o `command` deles, e substituir o handler troca o sujeito da medição |

**Por que A e não B.** B é mais barata e mais elegante, e continua sendo a ferramenta certa para
medir uma falha de hook. Perdeu porque a metade que este spec precisa provar é o **sucesso** — a
graduação de `hooks.md` afirma que o bloco funciona, não que ele falha ruidosamente — e essa metade
não aparece no transcript de um rung-1. Fica registrada aqui para quem quiser instrumentar rung 2 ou
3, onde o transcript é rico.

**Por que A e não C.** C mede o handler; o spec afirma o **registro**. São proposições diferentes, e
confundi-las é precisamente o que `surface-verification.md` §"Nothing under `commands/**` is testable
in the session that writes it" nomeia.

**Por que A e não E.** E é a versão que passa mais fácil e prova menos. Um stub demonstra a mecânica
do harness, não a fiação em produção — e como a asserção é sobre um caminho que a própria probe
escolheu, ela não pode falhar por um motivo real. Um check que só pode passar não é um check.

**Por que não D.** D é a alternativa séria, e teria vencido se a fiação viva do repo não tivesse
morrido. Perdeu por evidência datada: `193578c` deixou dois hooks registrados apontando para um script
ausente, os transcripts mostram o verde virando vermelho em 29/07/2026, e nada no repo notou. O modo
de falha saiu de hipotético.

## Open Decisions

- **Um bloco `hooks:` de frontmatter num comando de *plugin* dispara igual a um de comando de
  projeto?** É a suposição única que, sendo falsa, invalida o spec inteiro, e ninguém a mediu. A
  medição de 30/07/2026 que fundamenta `## Design` foi feita com um comando em `.claude/commands/` de
  uma box descartável; os três blocos que a graduação de `hooks.md` cita vivem em
  `plugins/quenching/commands/docs/`, carregados por `--plugin-dir`. **Como se decide:** é a tarefa
  1.1, e ela roda **antes** de qualquer asserção ser escrita. Se o rung de plugin não disparar, o
  achado é maior que este spec — os três blocos seriam decorativos e a graduação de `hooks.md` estaria
  errada, não apenas não-observada — e o certo é parar, reportar, e deixar a resposta virar spec
  próprio, em vez de continuar construindo um check para uma fiação que não existe.
- **O check 5 entra no conjunto default ou fica opt-in?** `## Design` recomenda opt-in (`--only 5`), e
  a recomendação está escrita lá com a razão de custo. Fica aberto porque o orçamento do harness é
  decisão do humano, e a evidência para decidir só existe depois da tarefa 1.1: um disparo que se
  provar frágil merece o default; um que se provar estável torna opt-in obviamente certo.
  **Como se decide:** no passo de revisão de `/specs:conclude`, com o resultado das duas arms em mão —
  não antes, porque decidir agora seria escolher sem o dado que a própria tarefa produz.

## Risks

- **Marcador obsoleto faz a arm positiva passar sem nada ter disparado.** O marcador vive em
  `tempfile.gettempdir()`, compartilhado pela máquina inteira. Mitigação: a probe calcula o caminho
  pela mesma fórmula do handler, faz `rm -f` **antes** da sessão, e assere que o arquivo passou a
  existir — não que existe. Como a box é um `mktemp -d` novo por run, o digest de `abspath` nunca
  repete entre runs; o `rm -f` custa uma linha e elimina a classe inteira em vez de argumentar sobre
  probabilidade.
- **`okf-validate.py` para de chamar `_touch_marker`, ou muda o caminho, e a probe vira verde
  permanente.** O acoplamento está na direção segura para a primeira metade: remover
  `_touch_marker` **reprova** a arm positiva em vez de silenciá-la. A metade perigosa é mudança de
  **caminho** — aí o marcador some e a arm positiva também reprova, o que é ruído, não falso verde.
  Mitigação: calcular o caminho num único lugar da probe, e deixar em `_marker_path`
  (`assets/hooks/okf-validate.py:216`) um comentário nomeando o check 5 como consumidor, para que
  quem mexer no caminho veja o consumidor antes de mexer.
- **A arm negativa passa vazia.** É o modo de falha da precondição 4: "nenhum marcador" é verdade
  também numa sessão que não fez nada, e uma box quebrada reportaria uma guarda funcionando.
  Mitigação: as duas arms são condicionadas a um `tool_use` de `Write` ou `Edit` com `file_path` sob
  `docs/` no capture — que é exatamente o que o stream **sabe** reportar. Sem essa evidência o
  resultado é `inconc`, nunca `check yes`.
- **A probe mede o rung 1 e o defeito real deste repo é rung 2/3.** `ACCEPTED — ` a probe cobre o
  rung que nenhum outro instrumento alcança, e a fiação de `settings.json` é observável sem sessão de
  agente (os transcripts a datam). O que fica descoberto é o **check estático** que teria pegado
  `193578c`: um handler `command` cujo script não existe e não está guardado. Fica reportado como
  follow-up para `skills.py`, e este spec não o constrói — ver `## Out of Scope`.
- **O check 5 se torna o próximo "check que só pegou a si mesmo".** `ACCEPTED — ` é o padrão que
  `surface-verification.md` documentou, com evidência medida, sobre os quatro checks existentes, e não
  há como saber de antemão. Aceito porque o valor primário deste check é uma **prova única de
  graduação** e não uma rede de regressão permanente. Critério de aposentadoria registrado agora, para
  que ela seja decisão e não debate: dois runs vermelhos seguidos cuja causa traçar para o próprio
  script aposentam o check 5.
- **Um check opt-in que ninguém roda não protege nada.** Mitigação: a linha nova na tabela de custo de
  `surface-verification.md` §"Scope the run to what the change can break" nomeia o gatilho, e o dono é
  `/skill:hook:new` — o mesmo acoplamento que `/skill:new` já tem com os checks 1, 2 e 4. Um check sem
  comando dono é um check que envelhece.
- **Duas sessões de agente com permissão de escrita.** Herdado, não novo: se a box não isolar, a probe
  escreve na árvore que ela verifica. O check 5 usa `newbox` e `--plugin-dir` como os outros e não abre
  exceção; a garantia mecânica contra uma edição futura que reintroduza `cd "$REPO"` é do sibling
  `isolate-functional-checks-probes` e o check 5 a herda sem redecidir.
- **Corrigir a frase de `hooks.md` sobre a fiação de `.claude/settings.json` sem consertar a fiação
  deixa um padrão `authority: current` descrevendo um defeito aberto.** Mitigação: a frase corrigida
  diz o que foi medido — registrada e morta, com o commit e a data — e aponta o comando que conserta.
  Um padrão que descreve honestamente um defeito aberto é melhor que um que afirma um funcionamento
  falso; e a correção da fiação vai no relatório como oferta.

## Tasks

### 1. Fechar a decisão aberta antes de escrever qualquer asserção

- [ ] 1.1 Medir, numa box descartável, se o bloco `hooks:` de frontmatter de um comando **do plugin**
      (carregado por `--plugin-dir`) dispara quando esse comando escreve na bundle — e reportar o
      resultado em `## Open Decisions`. Concluída quando o marcador dirty foi visto aparecer, ou
      quando foi visto **não** aparecer. Se não disparar, **pare o spec aqui** e reporte: os três
      blocos seriam decorativos e a graduação de `hooks.md` estaria errada, o que é um achado maior
      que este spec.
      verify: o estado do marcador antes e depois da sessão está registrado com o comando que o mediu

### 2. A fixture e o check 5

- [ ] 2.1 Estender `newbox` com `docs/knowledge/glossary.md` e `docs/knowledge/index.md`, para que o
      comando portador tenha onde escrever sem gastar turnos decidindo home (precondição 3).
      files: plugins/quenching/assets/checks/functional-checks.sh
      verify: ./plugins/quenching/assets/checks/functional-checks.sh --only 1 segue verde com a box nova
- [ ] 2.2 Acrescentar o check 5 e sua **arm positiva**: box com `.claude/hooks/okf-validate.py`
      instalado a partir de `assets/hooks/okf-validate.py`, marcador calculado e apagado, uma sessão
      `claude -p --plugin-dir` com a frase que não nomeia o hook, e a asserção de que o marcador passou
      a existir.
      files: plugins/quenching/assets/checks/functional-checks.sh
      pattern: plugins/quenching/assets/checks/functional-checks.sh (check 4, o mais recente)
      verify: ./plugins/quenching/assets/checks/functional-checks.sh --only 5
- [ ] 2.3 Acrescentar a **arm negativa**: a mesma frase na mesma forma de box **sem** o handler
      instalado, asserindo que o marcador não existe e que o transcript da sessão não carrega
      `attachment.type == "hook_blocking_error"` — a prova executada da guarda `test -f … || exit 0`.
      files: plugins/quenching/assets/checks/functional-checks.sh
      verify: ./plugins/quenching/assets/checks/functional-checks.sh --only 5
- [ ] 2.4 Condicionar as duas asserções a evidência de escrita: um `tool_use` de `Write` ou `Edit` com
      `file_path` sob `docs/` no capture, senão `inconc` e nunca `check yes`. Reusa `evidence()` e
      `tools()`, não duplica nenhum dos dois.
      files: plugins/quenching/assets/checks/functional-checks.sh
      verify: com a frase trocada por uma que não escreve nada, as duas asserções saem SKIP e o run sai 2
- [ ] 2.5 Atualizar o header do script: o custo do check 5 em sessões, o seletor `--only 5`, e a razão
      registrada de ele ficar fora do default `1,2,4`.
      files: plugins/quenching/assets/checks/functional-checks.sh
      verify: ./plugins/quenching/assets/checks/functional-checks.sh --help mostra o check 5 e seu custo

### 3. O consumidor declarado no handler

- [ ] 3.1 Comentar `_marker_path` em `plugins/quenching/assets/hooks/okf-validate.py` nomeando o check
      5 como consumidor do caminho do marcador, para que quem mudar o caminho veja o consumidor antes.
      Comentário e nada mais — nenhuma mudança de comportamento, nenhuma obrigação de lockstep.
      files: plugins/quenching/assets/hooks/okf-validate.py
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py selftest && python3 plugins/quenching/assets/hooks/okf-validate.py --version

### 4. Ver o check reprovar

- [ ] 4.1 Rodar as três arms de vermelho deliberado de `## Validation` e registrar as três saídas: arm
      positiva quebrada vira FAIL (não SKIP), guarda apagada vira FAIL, frase que não escreve vira dois
      SKIP com `exit 2`. Um check que nunca foi visto reprovar não é um check.
      verify: as três saídas estão registradas, e o passo 3 saiu 2 e não 0

### 5. Os padrões que a medição prova

- [ ] 5.1 Escrever em `docs/standards/quality/surface-verification.md` que um disparo de hook não é um
      `tool_use` e é invisível ao capture `stream-json`, logo uma propriedade de hook se verifica pelo
      artefato que o handler real deixa em disco — mais a linha na tabela §"Scope the run to what the
      change can break" dizendo quando rodar `--only 5`. `authority: current`, porque a tarefa 4.1 a
      provou.
      files: docs/standards/quality/surface-verification.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
- [ ] 5.2 Escrever em `docs/standards/automation/hooks.md` que a graduação do rung 1 é **observada**,
      nomeando o check 5 — e corrigir a frase de §"What this repo's own surface does under it" que
      afirma uma fiação viva em `.claude/settings.json`, para o que foi medido: registrada e morta
      desde `193578c`, com o comando que conserta nomeado.
      files: docs/standards/automation/hooks.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs

### 6. Fechar a segunda decisão aberta

- [ ] 6.1 Decidir, conforme `## Open Decisions`, se o check 5 entra no conjunto default ou fica
      opt-in — com o resultado das duas arms em mão, não antes. A decisão é do humano; a tarefa é
      apresentá-la com a evidência e aplicar a resposta em `ONLY` e no header.
      files: plugins/quenching/assets/checks/functional-checks.sh
      verify: `ONLY` e o header concordam com a decisão registrada
