---
slug: make-sk-unscoped-bash-read-the-body
title: sk-unscoped-bash cannot read the body its own remedy points at
verification: per-section
priority: {level: 18, criticality: medium, complexity: 3, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# sk-unscoped-bash cannot read the body its own remedy points at

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

`skills.py lint` avisa quando um comando concede `Bash` sem escopo, e o texto desse aviso oferece
duas saídas: escopar o grant, ou escrever no corpo a razão de ele ser largo. A segunda saída não
existe de verdade — a checagem só olha o frontmatter. Este spec faz a saída existir.

`## Problem` mostra o aviso rodando contra o repo hoje e o número que expõe a falha: cinco comandos
avisados, todos os cinco já com a razão escrita, todos avisados de forma idêntica. `## Proposal` lista
o que passa a ser verdade depois, e o essencial é que **nada desaparece do relatório** — a linha
continua lá, dizendo qual dos dois casos ela é.

`## Design` é a seção a ler antes das tasks. Ensinar uma checagem a ler prosa para decidir se um
grant foi pensado seria inferência de linguagem natural, que
`docs/standards/quality/parse-honesty.md` não permite; a saída é um **marcador literal e ancorado** —
o mesmo mecanismo que `**Done when:**` já usa — de forma que a checagem afirme apenas *"o marcador
está lá"* e o julgamento sobre a razão continue sendo de quem lê. O mesmo `## Design` traz o achado
do exame adversarial: **o defeito não é único**. `sk-hook-unmatched` tem o mesmo remedy impossível, e
como um hook de `settings.json` não tem corpo nenhum, o remédio honesto lá é outro — que é por isso
que a regra durável saiu escrita de forma escopada em vez de absoluta.

`## Alternatives Considered` mostra as formas recusadas, inclusive a mais barata (só consertar a
frase), e por que a metade barata dela foi absorvida em vez de descartada. `## Out of Scope` é longo
de propósito: quase tudo que parece vizinho aqui pertence a outro contrato ou a outro spec — a
severidade `advisory`, um segundo código `sk-*`, o bump de versão, e qualquer afirmação sobre
`allowed-tools` restringir algo.

`## Risks` guarda a falha mais provável (alguém edita a prosa e cinco linhas precificadas voltam a ser
indistintas, em silêncio) e nomeia os quatro specs irmãos que tocam esta fronteira sem decidir nada
por eles. `## Open Decisions` tem três perguntas abertas de propósito, cada uma com o teste que a
fecha. `## Impact` declara os dois standards que serão escritos e o terceiro, em `background`, que
esta mudança pode graduar de passagem.

`## Validation` é o par que dá dentes ao resto: a contagem dos dois lados contra o próprio surface do
plugin, e uma passagem de mutação sobre o `selftest` novo — porque um `selftest` que nunca foi visto
falhar não prova nada. `## Handoff` e `## Tasks` são curtos porque a mudança é pequena: uma função de
leitura, dois textos de mensagem, um campo de dado, quatro casos de teste, três frases em contratos e
um standard novo.
## Problem

O próprio texto do remedy de `sk-unscoped-bash` oferece duas saídas: *"scope it to the commands the
workflow runs, **or state the reason in the body**"* (`plugins/quenching/assets/bin/skills.py:823-824`).
A checagem que emite esse remedy lê apenas `allowed-tools` (`skills.py:821`) e nunca abre o corpo.
Então a segunda saída que ela oferece não fecha nada: quem a percorre até o fim recebe exatamente o
mesmo aviso de antes.

Isso já foi feito de verdade, em escala. Depois da task 3.2 de `instrument-and-extend-skill-front` o
finding caiu 8 → 5 e **todos os cinco sobreviventes passaram a declarar a razão** num bloco
``**Why `Bash` is unrestricted here.**``. Rodando hoje contra `main` em 4.4.0:

```
python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json
```

os cinco são `/docs:align`, `/docs:documentation:build`, `/specs:conclude`, `/specs:execute` e
`/specs:isolate` — todos com o bloco escrito, e todos avisando com bytes idênticos aos de quando
cinco dos oito originais não declaravam nada. (`/docs:import-memory`, que era um dos cinco quando o
problema foi descoberto, teve o grant escopado em `0a0aa4b` e hoje carrega a variante
``**Why `Bash` is scoped here.**``; `/specs:isolate` entrou no lugar dele em `dcc0eb8`. A lista de
cinco é móvel — o defeito não é a lista, é a checagem.)

O sintoma é que o finding não separa um grant **precificado** de um **não examinado**. A causa é uma
regra mais geral, e é ela que este spec ataca: **um remedy que nomeia uma ação cuja conclusão a
própria checagem não consegue observar**. O leitor que trabalha a lista para baixo não tem como
saber quais linhas foram consideradas e quais nunca foram tocadas, e o trabalho honesto de
precificar um grant não rende nada no relatório — o que é a definição de uma regra que decai,
porque nada muda quando ela é cumprida.

**Por que agora.** No surface deste próprio repo o custo é pequeno: são cinco linhas, todas
precificadas, e um humano pode ler os cinco corpos. Mas `skills.py` é **instalado em repos-alvo**
pelo `/skill:align`, e lá o caso comum é o inverso — um `Bash` cru que ninguém examinou, misturado
no relatório com um que alguém pensou. O relatório é o único sinal que o alvo tem, e hoje ele
achata os dois casos. `docs/standards/quality/bundle-verification.md` §Advisory já diz a frase que
condena o estado atual: *"A check that cannot distinguish 'wrong' from 'worth a look' belongs here
or nowhere."*

Descoberto por `instrument-and-extend-skill-front`, confirmado contra `main` em 4.1.0 durante o
`conclude` dele, e re-confirmado contra 4.4.0 em 2026-07-30.

## Proposal

- `skills.py lint` distingue, em cada linha `sk-unscoped-bash`, um grant **precificado no corpo** de
  um **não examinado**. Hoje as duas situações produzem bytes idênticos.
- A distinção chega pelos dois canais que têm consumidor: o texto da mensagem, que um humano lê
  linha a linha no relatório, e um campo de dado no `--json`, que `/skill:align` pode ordenar sem
  interpretar prosa.
- O que a checagem lê é um **marcador literal**, não prosa livre:
  ``**Why `Bash` is unrestricted here.**`` no início de uma linha do corpo, fora de bloco cercado.
  É a mesma espécie de contrato que `**Done when:**` já é para `sk-step-criterion`
  (`skills.py:137` e `skills.py:748`).
- Nenhuma linha sai do relatório por estar precificada. As cinco continuam sendo reportadas, porque
  o grant continua sendo o shell inteiro do turno em todas elas.
- O remedy deixa de oferecer uma ação que a checagem não observa: o caso não precificado pede o
  bloco pelo nome, e o caso precificado não pede nada — ele informa.
- A mensagem da linha precificada afirma **presença do marcador** e nada além disso, para que
  ninguém a leia como atestado de que a razão é boa.
- `docs/standards/automation/skills.md` §`allowed-tools` is always scoped nomeia a forma literal do
  marcador, convertendo o informal *"provided its body says so and says why"* em contrato
  verificável — sem mudar quem julga se a razão presta.
- `skills.py selftest` prova as três metades que importam: marcador presente, marcador ausente, e o
  quase-acerto ``**Why `Bash` is scoped here.**`` (a forma que `/docs:import-memory` carrega hoje),
  que não precifica nada porque descreve um grant escopado.

## Out of Scope

- **Julgar se a razão declarada presta.** Fora, e permanentemente. `doctrine.md` põe *"Every
  non-default lever carries a stated buy"* na linha cujo verificador é **um leitor**, ao lado do
  no-op test e do sediment, exatamente porque cada um deles exige uma afirmação sobre comportamento
  que nenhum parser faz. A checagem passa a responder *"alguém escreveu a razão no formato
  acordado?"* e nunca *"a razão é boa?"*.
- **Suprimir a linha quando ela está precificada.** Fora: contradiz
  `docs/standards/automation/skills.md:134-135`, que declara *"The finding is still reported; what
  the stated reason buys is a reader who can tell a deliberate grant from an unexamined one."* E no
  surface deste repo levaria a contagem de 5 → 0, tornando invisível o grant mais largo que o plugin
  concede.
- **Um terceiro valor de severidade** (`advisory` ao lado de `error` e `warn`). Fora deste spec.
  `skills.py` tem duas severidades (`skills.py:663`, `skills.py:668`) e "Advisory finding" já é
  vocabulário do repo como *categoria*, não como valor — a promoção dela a dado é território do spec
  irmão `expose-finding-advisory-as-data`.
- **Um segundo código `sk-*`.** Fora: um código é vocabulário público e aparece em três lugares que
  o citam sem restatear (`assets/references/skill-new/doctrine.md` tabela, `skills.md` §The
  verifier, `commands/skill/align.md:242-244`). Pagar três documentos por uma distinção que um campo
  de dado já carrega é a inflação de escopo que este spec recusa.
- **Estender a leitura de marcador a outras ferramentas.** `UNSCOPED_TOOLS` tem um único item hoje
  (`skills.py:138`). O marcador é parametrizado pelo nome da ferramenta para não travar a decisão,
  mas nenhuma outra ferramenta entra em `UNSCOPED_TOOLS` aqui.
- **Reivindicar que `allowed-tools` restringe algo.** Fora, por contrato:
  `docs/standards/quality/surface-verification.md` §What this does not cover proíbe a afirmação nas
  duas direções até que seja medida. Este spec mexe no que o grant **declara**, nunca no que ele
  impede.
- **Reescrever os cinco corpos.** Os cinco já carregam o bloco na forma literal exigida — foi por
  isso que o problema apareceu. Nenhum corpo de comando muda.
- **Escopar algum dos cinco grants.** Cada um tem sua razão escrita e nenhuma delas foi contestada;
  reduzir a contagem de 5 é um trabalho de autoria por comando, não deste spec.
- **O bump de versão.** Fora por contrato: `docs/standards/ci-cd/versioning-release.md` §When the
  bump happens — os seis artefatos se movem uma vez, no `/specs:conclude` step 5, e um bump **nunca
  é uma task**.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/quality/remedy-honesty.md` — a regra de que o remedy de um finding só oferece uma
  ação cuja conclusão a checagem consegue observar; a irmã de saída de `parse-honesty.md`, na mesma
  família de `surface-verification.md` e `bundle-verification.md`. Nasce aqui porque uma regra
  enterrada como seção num doc chamado *Parse honesty* não é encontrável por quem está escrevendo o
  texto de um finding.
- `docs/standards/automation/skills.md` — §`allowed-tools` is always scoped passa a nomear a forma
  literal do marcador, convertendo *"provided its body says so and says why"* em contrato
  verificável, e registra que o finding continua sendo reportado nos dois casos.

### Standards at `authority: background` this spec may resolve

- `docs/standards/quality/selftest-mutation.md` — está em `background` porque *"the three shipped
  tools have not had it"*. Este spec acrescenta casos ao `selftest` de `skills.py` e roda a passagem
  de mutação sobre eles, então pode graduar a regra **para `skills.py`**. Não promete graduar o doc
  inteiro: `specs.py` e `okf-validate.py` continuam sem a passagem, e a promoção do `authority` é
  julgamento de quem fecha o spec.

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/skills.py` — o leitor do marcador, os dois textos de mensagem, o
  campo do `--json`, e os casos de `selftest`. É o único arquivo de código.
- `plugins/quenching/assets/templates/automation/skills-standard.md` — o molde que um repo-alvo
  recebe como o seu próprio `docs/standards/automation/skills.md`. Ele restatea a regra de
  `allowed-tools`, então precisa do marcador ou as duas cópias divergem.
- `plugins/quenching/assets/templates/automation/command.md` — o comentário de `allowed-tools` no
  molde (linhas 9-12) é onde um autor lê a regra pela primeira vez; é lá que o marcador tem de estar
  escrito para ser adotado.
- `plugins/quenching/commands/skill/align.md` — **condicional**, ver `## Open Decisions`: uma linha
  na lista de códigos, e um corpo sob `commands/**` tem preço de harness.

## Validation

Tudo daqui roda de `plugins/quenching/`, exceto onde o caminho diz o contrário. Os números são a
linha de base medida contra `main` em 4.4.0 em 2026-07-30, então uma divergência é sinal e não ruído.

**1. A distinção existe e está do lado certo.** O teste central:

```bash
python3 assets/bin/skills.py --root . lint --json
```

Hoje: cinco linhas `sk-unscoped-bash`, para `/docs:align`, `/docs:documentation:build`,
`/specs:conclude`, `/specs:execute` e `/specs:isolate`, com mensagens byte-idênticas. Depois: as
**mesmas cinco** linhas, **todas** marcadas como precificadas no campo do `--json`, e **zero** não
precificadas. Nenhuma linha somiu e o total de findings do surface não muda (35 hoje).

**2. A passagem de mutação, que é o que faz o `selftest` valer algo.** Por
`docs/standards/quality/selftest-mutation.md`, uma mutação por regra que o fixture existe para
provar, revertida em seguida:

- tirar os backticks de ``Bash`` no bloco de `/specs:execute` → aquela linha tem de virar **não
  precificada**; se continuar precificada, o match não está ancorado;
- trocar *unrestricted* por *scoped* no mesmo bloco → não precificada (é a forma que
  `/docs:import-memory` carrega, e ela descreve o caso oposto);
- indentar o marcador para dentro de um bloco cercado → não precificada;
- inverter a comparação no leitor → `selftest` tem de falhar.

Cada mutação é revertida, e o resultado das quatro é registrado no commit que escreve o `selftest`.

**3. O `selftest` passa e cresce.**

```bash
python3 assets/bin/skills.py selftest
```

Hoje: `PASS`. Depois: `PASS`, com a contagem de `cases` maior pelos casos novos — precificado, não
precificado, quase-acerto ``**Why `Bash` is scoped here.**``, e marcador dentro de cerca.

**4. Nada mais no surface se move.**

```bash
python3 assets/bin/skills.py --root . doctor --json     # 26 commands, nenhum finding
python3 assets/bin/specs.py selftest                    # PASS
python3 assets/hooks/okf-validate.py selftest           # PASS
```

Os dois últimos provam que a regra compartilhada de frontmatter não derivou: as três ferramentas
julgam a **mesma** lista canônica de casos, e é por isso que rodá-las aqui não é cerimônia.

**5. O bundle continua conforme depois do standard novo.** Da raiz do repo:

```bash
python3 plugins/quenching/assets/hooks/okf-validate.py docs
```

Linha de base: `0 error(s), 14 warning(s)`, exit 0. Depois: ainda **0 erros**. Os 14 warnings são
`stale-doc` e afins, pré-existentes e advisory por
`docs/standards/quality/bundle-verification.md` §Advisory — não são desta mudança, e o número pode
subir em um se o `resource:` do doc novo apontar para um arquivo com commit mais recente que o
`timestamp`. O que **não** é aceitável é qualquer `dir-no-index`, `index-orphan` ou
`index-broken-link`: esses são WARN-mas-obrigatórios e significam que a cauda OKF do doc novo não foi
feita.

**6. O que este spec deliberadamente NÃO verifica.** Que o surface **carrega**.
`docs/standards/quality/surface-verification.md` é explícito: nada sob `commands/**` é testável na
sessão que o escreve, e `lint`/`doctor` leem disco, não o registry. Se a task condicional 3.4 for
adiante e mudar `commands/skill/align.md`, aí — e só aí — a prova é
`./assets/bin/functional-checks.sh` no subconjunto default, com o custo de três sessões declarado em
`## Open Decisions`. Se a task não for adiante, **nenhum corpo de comando muda e o harness não é
acionado**, e isso é para ser dito no relatório em vez de citar `lint` como se ele tivesse carregado
algo.

## Design

### Onde exatamente está o defeito

Nem a checagem nem o remedy é desonesto isoladamente:

- A checagem lê `allowed-tools` e reporta fielmente o que leu. `parse-honesty.md` §Where this
  applies é explícito: *"It does not apply to a tool reading less on purpose and checking nothing
  about it."* Não ler o corpo é uma decisão de escopo, não um misread.
- O remedy descreve duas ações que de fato resolvem o problema **no mundo** — escopar o grant, ou
  declarar a razão.

O defeito é a **junção**: a segunda ação está fora da evidência da própria checagem, então cumpri-la
não muda o relatório. **Regra durável, e é o que este spec prova:** *o remedy de um finding só nomeia
ações cuja conclusão a checagem consegue observar. Uma ação fora da evidência da checagem entra no
texto como informação, nunca como remedy.* Isso é o irmão de `parse-honesty.md` do lado do
**output** — parse-honesty governa o que um verificador pode afirmar sobre o que **leu**; esta regra
governa o que ele pode **pedir**.

### Ler o corpo é legítimo, e o limite é a presença do marcador

`_step_criteria()` (`skills.py:735-750`) já lê o corpo e conta um marcador literal
(`DONE_WHEN_MARKER`, `skills.py:137`); `sk-step-criterion` reporta *"N de M passos não carregam
critério"* e nunca opina sobre o critério. É o precedente inteiro de que se precisa, e é o que
mantém a mudança dentro de `parse-honesty.md`: a checagem transforma o corpo num booleano
`marcador presente`, e é exatamente isso — e só isso — que ela afirma na mensagem.

O contra-argumento que este spec confronta e recusa: *"ler um corpo para decidir se um grant é
consciente é inferência de linguagem natural."* Seria, se o predicado fosse *"o corpo justifica o
grant"*. Com um marcador literal e ancorado o predicado é uma comparação de string, do mesmo tipo
que `BOUNDARY_MARKER not in description` (`skills.py:802`) já é.

### O marcador é ancorado, e o quase-acerto prova por quê

Forma exata: ``**Why `Bash` is unrestricted here.**``, no **início de uma linha**, **fora de bloco
cercado**, com o nome da ferramenta vindo de `UNSCOPED_TOOLS` em vez de hardcoded.

A evidência de que um match frouxo falha está no repo: `/docs:import-memory` carrega
``**Why `Bash` is scoped here.**`` (introduzido em `0a0aa4b`). Um match por substring ``Why `Bash` ``
precificaria um comando cujo grant **está** escopado — ou seja, marcaria como "considerado" um corpo
que descreve o caso oposto. A ancoragem no início da linha e a palavra `unrestricted` são o que
separa os dois.

### A linha precificada continua no relatório, e o dado vai no `--json`

Uma decisão, três razões:

1. **Contrato.** `skills.md:134-135` já decidiu isso: *"The finding is still reported."*
2. **Visibilidade.** Suprimir levaria este surface a 5 → 0 e o grant mais largo do plugin
   desapareceria do único lugar que o mostra.
3. **Custo.** Um segundo código `sk-*` obriga três documentos citadores a mudar
   (`doctrine.md`, `skills.md` §The verifier, `commands/skill/align.md:242-244`); um campo booleano
   no `--json` não obriga nenhum, e um consumidor que não o lê continua correto.

A severidade permanece `warn` nos dois casos, pela mesma razão que `parse-honesty.md` §Severity dá:
`warn` é a única severidade que cabe numa afirmação da forma *"eu li isto, e pode ser que eu tenha
lido errado"*. Um grant precificado ainda é o shell inteiro do turno.

### Onde a distinção pertence conceitualmente

`bundle-verification.md` §Advisory nomeia a categoria: *"A check that cannot distinguish 'wrong' from
'worth a look' belongs here or nowhere"*, e a categoria tem de ficar pequena. Um grant precificado é
literalmente um *worth a look*. Este spec **não** cria o valor de severidade que expressaria isso —
ver `## Out of Scope` e o overlap com `expose-finding-advisory-as-data` em `## Risks` — ele coloca a
distinção no canal mais barato que já existe e deixa a promoção para quem decide a severidade.

### Contratos vinculantes que o design não pode contradizer

| Contrato | O que ele impõe aqui |
| --- | --- |
| `docs/standards/quality/parse-honesty.md` | a checagem afirma o que leu; a mensagem nomeia o marcador, não a justificativa; o diagnóstico embarca junto com a transformação |
| `docs/standards/automation/skills.md` §`allowed-tools` | o finding continua sendo reportado; a exceção continua exigindo declaração no corpo |
| `docs/standards/quality/surface-verification.md` §What this does not cover | nada aqui pode reivindicar que `allowed-tools` restringe algo |
| `docs/standards/quality/parse-honesty.md` §consequência 3 | *"A tool with no way to prove it implements the rule does not get the rule"* — o caso de `selftest` é parte da mudança, não um follow-up |
| `docs/standards/ci-cd/versioning-release.md` | nenhuma task de bump; os seis artefatos são do `/specs:conclude` step 5 |
| `docs/standards/code/frontmatter-parsing.md` | o parser de frontmatter não muda; a leitura nova é de corpo |

### A mesma doença tem dois sítios, e eles pedem remédios diferentes

`sk-hook-unmatched` (`skills.py:1052-1058`) carrega o defeito idêntico: o remedy diz *"add a matcher,
**or state where it is wired why nothing narrower suffices**"*, e a segunda metade é prosa que a
checagem nunca lê. Descobrir isso muda o enquadramento — não é um erro de digitação num finding, é
uma **família**.

E a família não tem um remédio único, o que é o achado mais útil deste spec: `hook_ladder_findings()`
roda sobre **dois** rungs (`skills.py:1039-1042`), e um deles é o wiring de `settings.json`, que
**não tem corpo nenhum para ler**. Onde não há corpo, a forma C é impossível e a honesta é a forma A
— consertar o texto. Daí a formulação escopada da regra durável: ela proíbe *oferecer uma ação que
deixa o finding byte-idêntico*, e a saída pode ser tanto ensinar a checagem a observar a ação quanto
parar de chamá-la de remedy.

Este spec conserta **um** sítio, e escreve a regra uma vez. O segundo sítio é `## Open Decisions`.

### Por que a ação continua na mensagem, e não no campo `remedy`

O refactor aparentemente mais limpo — mover a ação para o kwarg `remedy=` que `finding()` já aceita
(`skills.py:653-656`), deixando `message` com o fato — **perde informação**: `report_findings()`
imprime apenas `message` (`skills.py:675`), então o campo `remedy` só existe no `--json`. Num
relatório de texto, que é como um humano lê `lint`, a ação desapareceria. Os findings de `lint` que
hoje usam `remedy=` chegam pelo caminho dos hooks; os da própria `lint_command()` põem a ação na
mensagem, e essa convenção é mantida.

### O código não é citado por nenhum consumidor

`commands/skill/align.md:242-244` enumera os códigos que carregam "a metade mecanicamente decidível"
— `sk-body-length`, `sk-step-criterion`, `sk-trigger-position`, `sk-no-boundary`,
`sk-description-portable`, `sk-metadata-cap` — e `sk-unscoped-bash` **não está lá**, nem em
`commands/skill/new.md`. Melhorar uma linha que nenhum consumidor nomeia é o risco de escopo deste
spec, e a decisão de fechá-lo tem um custo de harness próprio: ver `## Open Decisions`.
## Alternatives Considered

Quatro formas inteiras, não quatro parâmetros da mesma forma. A escolhida é a **C**.

| Forma | Custo | O que compra | O que fecha |
| --- | --- | --- | --- |
| **A — só consertar o texto do remedy** | uma string em `skills.py:823-824` | o remedy para de prometer o que não observa; risco zero de parse | não separa precificado de não examinado, que é a queixa do `## Problem`; o trabalho de precificar continua não rendendo nada |
| **B — ler o marcador e suprimir a linha** | leitura de corpo + supressão | relatório curto: sobram só os grants não examinados | contradiz `skills.md:134-135`; leva este surface a 5 → 0 e esconde o grant mais largo do plugin |
| **C — ler o marcador, manter as duas linhas, distinguir na mensagem e num campo do `--json`** | leitura de corpo ancorada + dois textos de mensagem + um booleano no JSON + caso de `selftest` + uma frase em `skills.md` | a distinção que o `## Problem` pede, sem esconder nada e sem novo vocabulário de código ou severidade | nada que este spec queira: a promoção a `advisory` continua possível depois, por cima do campo |
| **D — ler o marcador e emitir um segundo código `sk-*`** | tudo de C, mais três documentos citadores e um código público novo | um `grep` por código separa as duas listas | um código é vocabulário permanente; um campo booleano é reversível |

**Por que A perde.** É honesta e quase gratuita, e por isso é a alternativa mais forte — foi
considerada como o resultado inteiro do spec. Ela perde porque resolve a *frase* e não o *leitor*:
`bundle-verification.md` §Advisory já decidiu que uma checagem incapaz de separar "errado" de "vale
uma olhada" pertence a uma das duas categorias e não a um meio-termo, e A deixa exatamente o
meio-termo. Em repo-alvo, onde o caso comum é o `Bash` cru não examinado, A entrega um relatório em
que a linha considerada e a esquecida continuam idênticas. **O texto do remedy de A é adotado por
dentro de C** — não é uma alternativa descartada inteira, é a metade barata de C.

**Por que B perde.** Silencia por design. É o modo de falha que `parse-honesty.md` §Severity descreve
do outro lado: *"Staying silent is what produced the original defect."* Um grant precificado ainda
concede o shell inteiro; uma linha que desaparece afirma o contrário.

**Por que D perde.** Não é mais informativa que C, só mais caro de reverter. Um código `sk-*` entra em
`doctrine.md`, em `skills.md` §The verifier e na lista de `commands/skill/align.md:242-244`, e sai de
lá com um spec. Um campo no `--json` é aditivo e nenhum consumidor atual quebra por ignorá-lo.

**Não fazer nada** é a quinta, e perde pelo `## Problem`: cinco linhas cujo cumprimento não rende
nada ensinam ao leitor que o finding não vale ser trabalhado, e é assim que uma regra decai enquanto
o checker continua verde.

## Open Decisions

- **O segundo sítio da família — `sk-hook-unmatched` — entra neste spec ou num próprio?** O remedy
  dele (`skills.py:1057-1058`) tem o defeito idêntico, mas `hook_ladder_findings()` também roda sobre
  o wiring de `settings.json`, que não tem corpo para ler; lá a saída honesta é a forma A (consertar
  o texto), não a forma C. *Como se decide:* depois de a regra durável estar escrita, rodar
  `skills.py doctor --json` contra um alvo com hook sem matcher e ler a linha: se ela ainda oferecer
  uma ação que não muda o relatório, a correção é de uma string e cabe numa task deste spec; se
  exigir decidir onde a razão de um hook de `settings.json` deveria morar, é spec próprio. A decisão
  é do humano no `/specs:execute`, e a recomendação registrada é **spec próprio** — dois artefatos
  diferentes com dois remédios diferentes numa task só é o inchaço de escopo que este spec recusou em
  `## Out of Scope`.
- **`sk-unscoped-bash` entra na lista de códigos de `commands/skill/align.md:242-244`?** Hoje nenhum
  consumidor nomeia o código, o que enfraquece o valor de refiná-lo. *Como se decide:* pesando o
  preço declarado em `docs/standards/quality/surface-verification.md` §Scope the run — mudar um corpo
  sob `commands/**` aciona `functional-checks.sh` no subconjunto default, três sessões de agente
  cobradas. Recomendação registrada: **sim, mas só se a task 3.1 já for a única que toca
  `commands/**`**; caso contrário a linha vira um `specs.py discover` para o próximo spec que já
  precise abrir aquele corpo.
- **Como o campo do `--json` se chama.** Nenhum dos candidatos plausíveis existe em
  `docs/knowledge/glossary.md` hoje, então o campo e a entrada de glossário nascem juntos. *Como se
  decide:* na task que escreve o campo, escolhendo entre `priced`, `reasonStated` e `bodyPriced` pelo
  critério do standard de naming — o termo que o repo já usa em prosa. `capabilities.md` §The default
  profile e `doctrine.md` já falam em *stated buy* e em **precificar** um lever, o que faz `priced`
  ser o candidato coerente com a linguagem existente; a entrada de glossário é rota `/docs:define` e
  não é escrita aqui.

## Risks

Cada história do premortem virou exatamente uma linha aqui, uma task, ou um `## Open Decisions`.

- **O marcador é quebrado por uma edição de prosa e cinco comandos precificados voltam a "não
  examinados" em silêncio.** É a falha mais provável: alguém tira os backticks de ``Bash``, troca
  *unrestricted* por *unscoped*, ou reindenta o bloco, e o relatório fica verde-idêntico ao de hoje.
  *Mitigação:* `## Validation` afirma a contagem nos dois lados (cinco precificados, zero não
  precificados) contra o próprio surface do plugin, então uma regressão de marcador aparece como um
  número errado e não como ausência de sinal. O `selftest` guarda a forma.
- **Auto-precificação por citação.** O marcador é prosa que a documentação do próprio plugin ensina
  (`assets/templates/automation/command.md:11-12`); um corpo que **cite** o marcador num exemplo
  passaria a se precificar sem ter grant algum a precificar. *Mitigação:* match ancorado no início da
  linha **e** fora de bloco cercado, com um caso de `selftest` que ponha o marcador dentro de uma
  cerca e exija que ele não conte.
- **Um repo-alvo que declarou a razão em outro formato passa a ler "não precificado" para sempre.**
  É um falso negativo que a checagem de hoje não consegue ter, porque hoje ela não lê nada.
  *Mitigação:* a mensagem do caso não precificado cita o texto **exato** do marcador, de modo que a
  correção seja mecânica e de uma linha. E a mudança não introduz nenhum finding novo em nenhum repo:
  o aviso já disparava para todo `Bash` cru, então nada que passava começa a falhar — a regra de
  `bundle-verification.md` §No new check is introduced at ERROR é respeitada por construção.
- **A regra durável, lida ao pé da letra, indicia remedies que estão certos.** `sk-body-length` manda
  *"push shared procedure into a bundled reference and cite it by absolute path"* e a checagem não
  observa nada disso — observa a contagem de linhas. *Mitigação:* a regra é escrita na forma
  escopada, proibindo a ação que deixa o finding **byte-idêntico**, não toda ação que a checagem não
  executa. Reduzir o corpo faz `sk-body-length` desaparecer; declarar a razão não faz nada com
  `sk-unscoped-bash`, e é só essa segunda forma que a regra proíbe.
- **Editar `commands/skill/align.md` aciona o harness.** Se a task que acrescenta o código à lista de
  consumidores for adiante, um corpo sob `commands/**` muda e
  `docs/standards/quality/surface-verification.md` §Scope the run manda rodar o subconjunto default
  de `functional-checks.sh` — três sessões de agente cobradas por uma linha de tabela.
  *Mitigação:* a task é condicional a `## Open Decisions`, decidida antes de ser executada.
- **ACCEPTED — prosa morta num alvo, se a decisão for revertida.** Desfazer é barato do lado do
  plugin (dois textos de mensagem, um campo, um caso de `selftest`, uma frase em `skills.md`; nenhum
  corpo de comando muda), mas um repo-alvo que já tiver adotado o marcador fica com prosa que ninguém
  lê mais. Aceitável: o bloco continua sendo documentação útil para um humano mesmo sem checagem, que
  é exatamente o que ele é hoje.

### Specs irmãos que tocam a mesma fronteira

Estão sendo desenvolvidos em paralelo; nenhum resultado é presumido aqui.

- **`expose-finding-advisory-as-data`** — expõe o status advisory/blocking como dado no `--json` do
  `okf-validate.py`. É a mesma forma de solução num tribunal vizinho. *Fronteira deste spec:* não
  cria valor de severidade nem campo `advisory`, e o campo que cria é específico deste código. Se o
  irmão landar primeiro e definir uma convenção de nome, este campo pode ser reexpresso por cima
  dela — o que não é presumido nem bloqueado aqui.
- **`retire-skill-vocabulary`** — o prefixo `sk-` é vocabulário de skill. *Fronteira deste spec:*
  **nenhum código `sk-*` novo é criado**, precisamente para não somar renomeações ao irmão. É uma
  razão adicional pela qual a alternativa D foi recusada.
- **`restructure-claude-front-namespace`** — renomeia o namespace `/skill` e move
  `commands/skill/align.md`, que este spec cita por caminho. *Fronteira deste spec:* nenhum corpo de
  comando é reescrito por causa do rename; as citações vivem em prosa de spec e de standard, e o
  irmão as reescreve se landar.
- **`decide-sp-unrefined-severity`** — decide se um finding escala de warn para error. *Fronteira
  deste spec:* a severidade de `sk-unscoped-bash` não muda, nos dois casos, e a decisão sobre escalar
  qualquer finding permanece do irmão.

## Tasks

Cada texto de task e cada valor de metadado cabe em **uma linha**: `parse_tasks` lê o texto da linha
do checkbox e o valor da linha do próprio metadado, então uma linha quebrada é conteúdo que o
executor nunca recebe.

### 1. O leitor do marcador

- [ ] 1.1 Declarar a constante do marcador e a função que o acha no corpo — ancorada no início da linha, fora de bloco cercado, com o nome da ferramenta vindo de `UNSCOPED_TOOLS` em vez de hardcoded
      files: plugins/quenching/assets/bin/skills.py
      pattern: plugins/quenching/assets/bin/skills.py — o par `_numbered_steps` / `_step_criteria` (linhas 716-750), que já lê o corpo procurando um marcador literal
      verify: python3 plugins/quenching/assets/bin/skills.py selftest
- [ ] 1.2 Separar a mensagem de `sk-unscoped-bash` nos dois casos e acrescentar o campo booleano ao finding — o caso não precificado cita o texto exato do marcador, e o precificado afirma só que o marcador está presente e que o grant continua sendo o shell inteiro do turno
      files: plugins/quenching/assets/bin/skills.py
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json — cinco linhas `sk-unscoped-bash`, todas precificadas, nenhuma a menos

### 2. A prova, e a prova de que a prova serve

- [ ] 2.1 Acrescentar quatro casos ao fixture do `selftest`: marcador presente, marcador ausente, quase-acerto com *scoped* no lugar de *unrestricted*, e marcador dentro de bloco cercado
      files: plugins/quenching/assets/bin/skills.py
      verify: python3 plugins/quenching/assets/bin/skills.py selftest — `PASS`, com `cases` maior que hoje
- [ ] 2.2 Rodar a passagem de mutação de `## Validation` item 2 — quatro mutações, cada uma revertida — e registrar os quatro resultados no corpo do commit, que é o que docs/standards/quality/selftest-mutation.md aceita como prova
      verify: python3 plugins/quenching/assets/bin/skills.py selftest

### 3. Os contratos que passam a nomear o marcador

- [ ] 3.1 Escrever a forma literal do marcador em docs/standards/automation/skills.md §`allowed-tools` is always scoped, registrando ali que o finding continua sendo reportado nos dois casos (authority: current, o doc já é current)
      files: docs/standards/automation/skills.md
- [ ] 3.2 Levar a mesma frase ao molde que um repo-alvo recebe como o seu próprio standard, para que as duas cópias da regra não divirjam
      files: plugins/quenching/assets/templates/automation/skills-standard.md
- [ ] 3.3 Nomear o marcador no comentário de `allowed-tools` do molde de comando, que é onde um autor lê a regra pela primeira vez
      files: plugins/quenching/assets/templates/automation/command.md
- [ ] 3.4 Decidir por `## Open Decisions` se `sk-unscoped-bash` entra na lista de códigos de `commands/skill/align.md`, e aplicar só se a resposta for sim — um corpo sob `commands/**` que muda aciona o harness no subconjunto default, três sessões cobradas
      files: plugins/quenching/commands/skill/align.md
      verify: ./assets/bin/functional-checks.sh

### 4. A regra durável

- [ ] 4.1 Escrever docs/standards/quality/remedy-honesty.md via `/docs:add` — a regra escopada (um remedy não oferece a ação que deixa o finding byte-idêntico), o segundo sítio da família e por que ele pede outro remédio, e os cross-links para parse-honesty.md, surface-verification.md e bundle-verification.md (authority: current, provado pelo `selftest` da task 2)
      files: docs/standards/quality/remedy-honesty.md
- [ ] 4.2 Fechar a cauda OKF do doc novo — zona GENERATED do índice de `docs/standards/` regenerada, e oferecer via `/docs:define` a entrada de glossário do termo que o campo do `--json` coina
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs — 0 erros, e nenhum `dir-no-index` / `index-orphan` / `index-broken-link`
