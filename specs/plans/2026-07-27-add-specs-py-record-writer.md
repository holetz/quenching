---
slug: add-specs-py-record-writer
title: Give the frontmatter records a mechanical writer in specs.py
verification: per-section
priority: {level: 25, criticality: medium, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# Give the frontmatter records a mechanical writer in specs.py

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

O frontmatter de um spec guarda um punhado de **records** — `priority`, `refined`, `approved`,
`branch`, `reviewed`, `merge`, `outcome` — que registram julgamentos humanos que nada no repositório
consegue recalcular. `## Problem` mostra que esses records são a única parte de um spec ainda
escrita à mão, com `Edit`, e o que isso custa na prática: um valor com vírgula volta cortado da
leitura sem ninguém avisar, e nada recusa uma segunda escrita num record que deveria ser definitivo.

`## Proposal` responde com um caminho único de escrita e lista o que passa a ser verdade depois
dele. `## Design` explica as decisões que o fazem funcionar — de onde vem a validação, como a forma
do record é escolhida a partir dos próprios valores, por que o escritor relê o que escreveu, e por
que uma delas (quem tem permissão de escrever cada record) não tem resposta mecânica nenhuma.
`## Out of Scope` e `## Alternatives Considered` guardam os caminhos vizinhos recusados, incluindo o
mais tentador deles, que era mexer na leitura em vez da escrita.

`## Risks` é onde a interrogação adversarial parou: o próprio escritor corromper um frontmatter, uma
recusa travando uma correção legítima, e um dos quatro comandos ficando para trás. Cada um tem a sua
detecção nomeada, e três são aceitos por escrito em vez de mitigados. `## Open Decisions` guarda o
que só evidência de uso resolve.

Do lado da execução: `## Impact` declara o único standard que este spec promete escrever e o código
que ele espera tocar; `## Validation` traz os comandos exatos, a tabela de casos de round-trip e a
passagem de mutação que torna o selftest uma prova em vez de uma afirmação; `## Tasks` está ordenado
para que o **primeiro** grupo já elimine a perda silenciosa de dados, e `## Handoff` diz o que já
existe no código e não deve ser reescrito.

## Problem

`specs.py` é dono de toda mutação que um spec sofre — `new` o estampa, `section --write` insere um
heading, `task --check|--uncheck|--block` edita uma linha de tarefa, `discover` acrescenta uma
linha, `promote` move o arquivo e estampa `outcome`. **Todo record de frontmatter exceto `outcome`
é a exceção**: `priority`, `refined`, `approved`, `branch`, `reviewed` e `merge` são escritos à mão
com `Edit` por quatro comandos diferentes (`triage`, `develop`, `isolate` — a quem `execute` delega
— e `conclude`).

Ler o código torna o diagnóstico mais específico, e pior, do que "não existe escritor mecânico". O
escritor existe: `set_frontmatter_key` (`specs.py:1610`) troca uma chave de topo preservando todas
as outras linhas como foram autoradas. Ele está ligado a exatamente **um** record, `outcome`, num
único ponto (`cmd_promote`, `specs.py:1723`). Os três defeitos são consequência disso:

- **`writeOnce` não é imposto por nada.** `schema.json` marca `approved`, `branch`, `merge` e
  `outcome` como write-once e diz por que cada um não é derivável, mas o que separa um record de
  uma sobrescrita é um invariante em prosa em quatro corpos de comando. Um comando que o esquece
  reescreve história em silêncio — exatamente a falha que a flag existe para impedir.
- **A renderização perde dados, e sem aviso.** O ramo de flow mapping de `parse_frontmatter`
  (`specs.py:643-650`) quebra o interior em `,` **antes** de tirar as aspas, então
  `merge: {strategy: merge-commit, subject: "plan/x: release 4.4.0 — the six, plus the seventh file"}`
  volta da leitura como `plan/x: release 4.4.0 — the six`. Nenhuma anomalia é reportada e
  `merge_record_finding` (`specs.py:2569`) aprova o record. Não é hipotético: o commit `5d14099`
  deste próprio repositório carrega exatamente esse assunto. Um ` #` no valor é pior — o record
  inteiro degrada para string, com uma única anomalia `comment-stripped` para explicar.
- **O escritor que existe não faz round-trip da forma de bloco.** `parse_frontmatter` lê record em
  bloco indentado (`specs.py:617-636`), mas `set_frontmatter_key` troca só a linha da chave:
  aplicá-la a um `merge:` escrito em bloco deixa as linhas indentadas órfãs abaixo de um novo valor
  em flow, e o arquivo passa a ter duas respostas para a mesma chave.

O **por que agora** é o `merge.subject`. Enquanto a âncora era um sha (`merge: {strategy, commit}`)
nenhum valor de record continha vírgula. Trocar a âncora pelo assunto do commit — a mudança mais
recente no conjunto de records — introduziu a única classe de valor que a forma flow não sobrevive,
e assuntos de commit deste repositório já trazem vírgula e travessão. O custo de esperar é uma
âncora de merge truncada por conclude, descoberta só quando alguém tentar resolver o commit.

Levantado pela revisão de branch do `specs-flow-consolidation` e demonstrado duas vezes pelo próprio
conclude dele: `reviewed` e `merge` foram estampados com `Edit` direto no arquivo, sem nenhuma
ferramenta capaz de recusar se o valor já estivesse posto.

## Proposal

- Existe um subcomando `specs.py record --spec {slug} {nome} --field k=v ...` e ele é o **único**
  caminho pelo qual um record de frontmatter é escrito. Os quatro comandos donos (`triage`,
  `develop`, `isolate`, `conclude`) o invocam em vez de usar `Edit`.
- Escrever um record `writeOnce` que já está posto **recusa com exit 2** e mostra o valor atual, em
  vez de sobrescrever. `--force` é o único jeito de passar, e o motivo da recusa continua na saída.
- Um nome de record fora de `schema.json` ou um campo fora de `records[nome].fields` recusa com
  exit 2 e lista os campos aceitos — a forma de cada record deixa de ser restatada em quatro corpos
  de comando.
- O record é renderizado na forma que **os seus próprios valores sobrevivem**: flow (`{k: v, ...}`)
  quando nenhum valor contém `,` nem ` #`, bloco indentado quando algum contém. Um `subject:` com
  vírgula deixa de ser truncado em silêncio.
- Escrever um record substitui a linha da chave **e a corrida indentada abaixo dela**, então
  reescrever um record que estava em bloco não deixa linhas órfãs.
- O escritor relê o que acabou de escrever e **recusa sem gravar** se os campos não voltarem
  idênticos — a garantia de round-trip é verificada em cada chamada, não presumida.
- Toda escrita preserva o resto do bloco byte a byte: `slug`, `title`, `verification` e os outros
  records sobrevivem na ordem e na formatação em que o humano os deixou.
- `validate` passa a checar todo record na mesma leitura de schema, no vocabulário `sp-*`, e
  `merge_record_finding` vira um caso dessa checagem em vez de ser o único record checado.
- `docs/standards/code/frontmatter-writing.md` existe e diz a regra de escrita, do mesmo modo que
  `frontmatter-parsing.md` diz a de leitura.

## Out of Scope

- **Ensinar `parse_frontmatter` a quebrar flow mapping respeitando aspas.** Corrigiria a leitura, não
  a escrita, e é uma mudança de lockstep em três cópias (`frontmatter-parsing.md` §The three-copy
  lockstep obligation) por uma forma que `skills.py` e `okf-validate.py` nem leem — então a linha
  nem poderia virar caso canônico. Escolher a forma na escrita remove o perigo na origem.
- **Uma dependência de YAML de verdade.** Fora de contrato permanentemente: zero-dependência é o que
  deixa os três scripts instalarem sozinhos (`frontmatter-parsing.md` §What this does not cover).
- **Reescrever records de specs que já estão em `specs/archive/`.** Um `merge: {strategy, commit}`
  antigo descreve um commit que existe, é lido como está e nunca é retroalimentado
  (`schema.json` `records.merge.why`, `plan-lifecycle.md` §a regra append-only do arquivo).
- **Impor propriedade de record mecanicamente.** Um CLI não tem identidade de chamador — ver
  `## Design` e `## Open Decisions`.
- **Estender o conjunto de records.** Nenhum record novo e nenhum campo novo em record existente:
  este spec dá escritor ao conjunto que `schema.json` já declara.
- **Validação de record além de nome, campo e forma.** A checagem que entra em `validate` é o
  subproduto da mesma leitura de `records[nome]` que o escritor já faz: nome de record conhecido,
  campo declarado, e a forma que `merge_record_finding` já checa. Nada de checar semântica de valor —
  se uma data é plausível, se um `level` é único no front, se um `subject` resolve em `git log`. Corte
  tomado na crítica: essas checagens não decorrem de `## Problem` e cada uma é uma decisão própria.
- **Reportar anomalia de frontmatter por record.** `frontmatter_anomalies` já é o sidecar disso e não
  ganha categoria nova aqui.
- **Bump de versão.** Os seis artefatos do lockstep se movem uma vez, no `/specs:conclude` passo 5,
  imediatamente antes do merge, nunca como tarefa (`versioning-release.md` §When the bump happens).
- **Qualquer seção do corpo do spec.** `task --check` e `discover` já são mecânicos; este spec é só
  sobre o bloco de frontmatter.
## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/code/frontmatter-writing.md` — a regra de **escrita** de record: a forma escolhida
  a partir dos próprios valores, a substituição da chave mais a corrida indentada, a releitura de
  conferência antes de gravar, e por que propriedade de record é prosa e não pode ser checagem. É a
  contraparte de `code/frontmatter-parsing.md`, que governa a leitura dos mesmos bytes.

### Standards at `authority: background` this spec may resolve

- `docs/standards/quality/selftest-mutation.md` — a passagem de mutação roda aqui contra o selftest
  de `specs.py`, o que fecha **um terço** do portão de graduação que o próprio doc declara. Não
  promove para `current`: aquele portão exige as três ferramentas, e este spec entrega uma.

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/specs.py` — `cmd_record` e o seu parser, o renderizador de forma, a
  substituição da corrida indentada, a generalização de `merge_record_finding`, os casos novos de
  `selftest` e `DEFAULT_SCHEMA`.
- `plugins/quenching/assets/specs/schema.json` — **só** a correção de `records.branch.writtenBy`
  (`execute` para `isolate`). Em lockstep com `DEFAULT_SCHEMA` (`specs.py:186`), porque `_behavioral`
  descarta `note` e `why` mas **não** `writtenBy`, então `selftest` compara esse campo.
- `plugins/quenching/commands/specs/triage.md`, `develop.md`, `isolate.md`, `conclude.md` — a
  instrução de estampar passa a nomear `specs.py record`. Nenhum precisa de `allowed-tools` novo: os
  quatro já declaram `Bash(python3:*)` ou `Bash`.

## Validation

Tudo roda de `plugins/quenching/`, exceto onde o caminho diz outra coisa. A política é
`per-section`, então este bloco corre depois de cada grupo de `## Tasks`.

**O escritor, contra as formas que o quebram.** Casos novos no `selftest`, cada um asserindo o
round-trip completo (escreve, relê, compara):

```bash
python3 assets/bin/specs.py selftest          # 0 error(s)
```

Os casos que precisam existir, porque cada um é uma regra que hoje falha:

| Caso | Deve produzir |
| --- | --- |
| `subject` com `,` | forma de bloco, e a releitura devolve a vírgula |
| `subject` com ` #` | forma de bloco, e a releitura devolve o `#` |
| valor comum | forma flow, uma linha |
| record que estava em bloco, reescrito | nenhuma linha indentada órfã |
| o resto do bloco | `slug`, `title`, `verification` e os outros records byte a byte iguais |
| record `writeOnce` já posto | exit 2, valor atual na saída, arquivo intocado |
| record `writeOnce` com `--force` | exit 0, e a saída diz que forçou |
| nome de record desconhecido | exit 2, lista os nomes válidos |
| campo fora de `records[nome].fields` | exit 2, lista os campos válidos |
| releitura divergindo do escrito | exit 2 e **nada gravado** |

**A passagem de mutação, que é o que torna o selftest acima uma prova.**
`docs/standards/quality/selftest-mutation.md` exige uma mutação por regra que a fixture existe para
provar, aplicada e revertida, com o resultado registrado. No mínimo quatro, e cada uma deve derrubar
**uma ou duas** asserções, não todas:

- fixar a forma em flow sempre → os dois primeiros casos falham;
- substituir só a linha da chave, sem a corrida indentada → o caso de bloco reescrito falha;
- ignorar `writeOnce` → os dois casos de recusa falham;
- gravar antes da releitura de conferência → o último caso falha.

Uma mutação que derruba tudo ou nada é fixture a consertar, não selftest aprovado.

**O lockstep e o front inteiro.**

```bash
cat VERSION && python3 assets/bin/specs.py --version          # iguais
python3 assets/bin/specs.py --root ../../specs validate --json # nenhum finding novo nos 46 specs
python3 assets/bin/skills.py --root . doctor --json            # 26 commands, no findings
python3 assets/hooks/okf-validate.py ../../docs                # exit 0, nenhum finding novo
```

**A linha de base, medida em 2026-07-30:** `validate` reporta **zero** findings atribuíveis a este
spec. O caminho declarado em `## Impact` é nomeado no texto da tarefa 4.1, que é o que
`sp-impact-uncovered` casa, então o par já fecha antes de qualquer linha ser escrita — e se ele
reaparecer, foi porque alguém reescreveu 4.1 sem o caminho. Findings de **outros** specs do front não
contam: 32 specs estão sendo desenvolvidos em paralelo e a contagem global se move sozinha. O
critério é sempre "nenhum finding novo nomeando este spec".

`okf-validate.py` já reporta warnings `stale-doc` pré-existentes neste bundle e sai 0 — o critério é
**nenhum finding novo**, nunca "zero warnings".

**Que nenhum comando ficou para trás.** O risco de três dos quatro corpos migrarem tem esta
detecção, e ela é a única que o pega:

```bash
grep -rn "Edit" commands/specs/*.md | grep -iE "frontmatter|record|stamp"
```

Deve voltar vazio para os quatro records, ou só com a menção de `verification`, que é chave escalar
requerida e não record — essa continua fora do escritor de records de propósito.

**Invariante que precisa continuar valendo:** os doze casos canônicos de frontmatter passam nas três
ferramentas. Este spec não toca nenhuma das três cópias do leitor, então a asserção é que
`skills.py selftest` e `okf-validate.py selftest` continuam em 0 error(s) sem terem sido editados.

## Design

### Onde o escritor vive

Um subcomando novo, `cmd_record`, ao lado de `cmd_task` e `cmd_discover` em `specs.py`, com a mesma
uniformidade dos outros: `--json`, exit 0 escreveu · 1 nada a escrever · 2 recusa. Nada de módulo
novo — os três scripts não podem importar nada e um `frontmatter.py` extraído trocaria um problema de
duplicação por um de distribuição (`frontmatter-parsing.md` §Why there are three copies).

### A forma do record é escolhida a partir dos valores, nunca fixada

Regra durável: **um record é renderizado na forma mais compacta que os seus próprios valores
sobrevivem.**

| Valor contém | Forma | Por que |
| --- | --- | --- |
| nada de especial | flow — `merge: {strategy: squash, subject: "…"}` | uma linha, e é a forma que 14 dos 15 records em `specs/archive/` já usam |
| `,` em qualquer valor | bloco indentado | `parse_frontmatter` quebra o interior do flow em `,` antes de tirar as aspas; aspas **não** protegem |
| ` #` em qualquer valor | bloco indentado | `_split_comment` corta o valor antes de o ramo de flow ser alcançado, e o record inteiro degrada para string |

Duas coisas fazem essa regra ser a decisão certa em vez de um detalhe de estilo. A primeira: aspas
parecem proteger e não protegem — todo `merge:` no arquivo hoje é `subject: "…"`, e é justamente
essa aparência de segurança que faz o defeito passar por revisão. A segunda: o bloco indentado é
lido corretamente pelas duas formas (`specs.py:617-636`) e é a única que aceita valor longo o
bastante para quebrar linha, então escolher bloco nunca é uma perda — só é mais verboso.

### Substituir a chave e a corrida indentada, não a linha

`set_frontmatter_key` (`specs.py:1610`) troca a linha da chave e para ali. Para o record em bloco
isso é corrupção, provada: aplicá-la a um `merge:` de três linhas produz um valor em flow com as
linhas antigas penduradas embaixo. O escritor de record usa `_indented_run` (`specs.py:525`), que já
existe para o sidecar de anomalias e já sabe exatamente onde o valor de cima termina e a próxima
chave de topo começa. `set_frontmatter_key` fica onde está, para `outcome`, que é escalar.

**Preservar o resto do bloco byte a byte é parte do contrato, não um efeito colateral.** Nada de
reserializar o frontmatter inteiro: a ordem das chaves, o espaçamento e as aspas que o humano
escolheu em `slug`, `title`, `verification` e nos outros records saem intactos. É a mesma razão que
`set_frontmatter_key` já documenta na própria docstring — reescrever o bloco reformataria o
`refined: {mode, date}` de alguém e reordenaria as chaves dele.

### O escritor confere o que escreveu

Depois de montar o novo texto e **antes** de gravar, o escritor roda `parse_frontmatter` no
resultado e compara os campos que acabou de escrever. Se algum não voltar idêntico, ele recusa com
exit 2, nomeia o campo e **não grava nada**. Isso troca uma classe inteira de falha silenciosa por
uma recusa: nenhuma regra de renderização precisa estar certa para sempre, só precisa ser conferida
em cada chamada. É a mesma lógica que faz `specs.py selftest` existir — um duplicado que ninguém
checa é um bug com atraso.

### Onde `writeOnce` é imposto

No escritor, lendo `records[nome].writeOnce` de `schema.json` — nunca numa lista em código. Record
write-once já posto: exit 2, mostra o valor atual, aponta `--force`. `--force` grava e ecoa que
forçou, na mesma forma que `promote --force` já usa para tarefa aberta. Records `writeOnce: false`
(`priority`, `refined`, `reviewed`) sempre regravam, porque um julgamento que foi refeito é fato
novo.

### Propriedade de record: declarada, não imposta

`schema.json` diz `writtenBy` para cada record e `frontmatter-parsing.md` não tem equivalente
disso — porque **não há como impor**. `python3 specs.py record ...` não carrega identidade de
chamador: não existe nada em um processo filho que diga qual corpo de comando o invocou, e um flag
`--by conclude` seria autodeclarado, ou seja, documentação com aparência de checagem. A decisão é
não fingir: o escritor **ecoa** o `writtenBy` do record na saída, para que um comando errado se veja
nomeado no próprio output, e a propriedade continua sendo regra em prosa. Ver `## Open Decisions`.

Isso já rendeu uma correção: `records.branch.writtenBy` diz `execute`, mas `isolate.md` passo 6 é
quem estampa e `execute.md` proíbe explicitamente ("Never stamp or rewrite a `branch` record here").
Um escritor que ecoa `writtenBy` não pode ecoar um dono errado.

### A ordem em que o valor chega

O corte de 80/20 da crítica virou ordem de tarefa, não redução de escopo: o **primeiro** grupo de
`## Tasks` é a escolha de forma mais a substituição da corrida indentada mais a releitura de
conferência. Terminado esse grupo, o caminho de perda silenciosa de dados já não existe, mesmo que a
recusa `writeOnce`, a generalização de `validate` e o quarto corpo de comando ainda não tenham
chegado. É o que torna um branch interrompido no meio ainda lucrativo.

### Contratos que este design não pode contrariar

- `frontmatter-parsing.md` — o subconjunto de YAML, a regra do `#`, a lista canônica de 12 casos e o
  lockstep de três cópias. Este spec **não** toca em nenhuma das três cópias do leitor, então nenhum
  caso canônico muda e nenhum selftest de outra ferramenta é afetado.
- `canonical-set-parsing.md` — todo conjunto sai de `schema.json` por pertencimento declarado, nunca
  por posição.
- `plan-lifecycle.md` / `plan-git-record.md` — o que cada record significa e quando é estampado
  continua deles; este spec só governa os bytes.
- `versioning-release.md` — `VERSION` em `specs.py` é um dos seis; o bump acontece no conclude.
- `selftest-mutation.md` — um selftest nunca observado falhando não prova nada; ver `## Validation`.

## Alternatives Considered

Quatro formas foram comparadas antes de o subcomando ser escolhido. A tabela é a comparação; os
motivos de derrota estão embaixo dela, porque é isso que impede a mesma ideia de voltar.

| Forma | Custo | O que compra | O que fecha |
| --- | --- | --- | --- |
| **Subcomando `record` que escreve e valida** (escolhida) | um subcomando, ~120 linhas, quatro corpos de comando reescritos | recusa `writeOnce`, forma escolhida pelo valor, round-trip conferido, forma declarada uma vez | nada — os corpos podem voltar a `Edit` se for revertido |
| Só validação: generalizar `merge_record_finding` | ~30 linhas, nenhum corpo mexido | avisa depois do fato | a escrita já aconteceu; o valor original só existe no git |
| Um helper de renderização que os corpos citam | zero código novo no CLI | uma única descrição da forma | continua sendo prosa; nada recusa nada |
| Consertar o leitor (flow com aspas) | três cópias em lockstep + caso canônico novo | leitura correta de arquivos já corrompidos | não resolve `writeOnce`, nem o bloco órfão, nem a primeira escrita |
| Não fazer nada | zero | zero | a próxima âncora de merge com vírgula é perdida em silêncio |

**Só validação perdeu porque o dano é a escrita.** Um `sp-bad-record` avisando depois chega tarde: o
`subject:` truncado não é recuperável do arquivo, só do git, e ninguém vai ao git por causa de um
warning. Ainda assim a validação entra — como subproduto, na mesma leitura de `schema.json` que o
escritor já faz.

**O helper de renderização perdeu porque não recusa.** É exatamente o estado atual com melhor
redação: quatro corpos concordando por boa vontade. O problema levantado por `## Problem` é a
ausência de um ponto onde algo possa dizer não.

**Consertar o leitor é a alternativa mais tentadora e a que precisa estar escrita aqui.** Ela ataca
o mesmo defeito um nível abaixo e parece mais fundamental. Perde por três motivos somados: é uma
edição de lockstep em três ferramentas (`frontmatter-parsing.md` §The three-copy lockstep
obligation) por uma forma que só uma delas lê, o que impede a linha de virar caso canônico; deixa
`writeOnce` e a corrida indentada órfã intocados; e não impede a **primeira** escrita ruim, só a lê
melhor depois. Escolher a forma na escrita custa um arquivo e remove a classe toda.

**Não fazer nada perdeu num fato, não numa preferência**: `5d14099` neste repositório tem assunto
com vírgula, e `conclude` estampa exatamente esse assunto.

## Open Decisions

- **Propriedade de record ganha declaração explícita (`--by {comando}`) ou fica só no eco?**
  Recomendação: fica no eco. Um flag autodeclarado é documentação parecendo checagem, e um CLI não
  tem identidade de chamador (`## Design` §Propriedade de record).
  **Como se decide:** depois de os quatro corpos estarem ligados, olhar se algum run real escreve um
  record que não é seu — o `writtenBy` ecoado na saída aparece ao lado do comando que rodou, então a
  evidência existe sem instrumentação nova. Um caso observado paga o flag; zero casos encerram a
  questão.
- **`sp-bad-record` entra como `warn` ou `error`?** Recomendação: `warn`, igual a `sp-bad-merge`, que
  ele generaliza — um record com campo desconhecido é uma suspeita sobre intenção humana, não uma
  violação provada, e `validate` deste front não recusa por record nenhum hoje.
  **Como se decide:** rodar a checagem contra os 58 specs em `specs/plans/` e `specs/archive/` antes
  de escolher a severidade — 33 em `plans/` mais 13 em `archive/`, contados em 2026-07-30. Se nenhum
  spec real dispara, `error` é barato; se algum dispara por uma forma legítima antiga, `warn` é a
  resposta e o motivo fica escrito.
- **O escritor aceita apagar um record (`--unset`)?** Recomendação: não neste spec. Nenhum comando
  precisa disso hoje, e um caminho de remoção num conjunto cujo ponto é ser append-only é superfície
  pedindo mau uso.
  **Como se decide:** quando um comando real precisar — hoje nenhum precisa, e essa é a resposta.

## Risks

- **O escritor corrompe o frontmatter que veio consertar.** A lógica de "trocar a chave e a corrida
  indentada" é exatamente a que hoje está subtilmente errada em `set_frontmatter_key`, e um spec cujo
  frontmatter deixa de parsear perde `slug` e `verification` — `status` e `next` passam a mentir sobre
  ele. Pior momento possível: durante um `conclude`, imediatamente antes do merge.
  **Mitigação:** o escritor relê o próprio resultado com `parse_frontmatter` e recusa **antes de
  gravar** se os campos não voltarem idênticos (`## Design` §O escritor confere o que escreveu). A
  detecção acontece na mesma chamada, não numa validação posterior que ninguém roda.
- **A recusa `writeOnce` trava uma correção legítima.** Um `approved` com data errada, ou um `merge`
  estampado antes de um merge que depois falhou, viram trabalho bloqueado por uma ferramenta.
  **Mitigação:** `--force`, com o valor antigo e o aviso de que foi forçado na saída — a mesma forma
  que `promote --force` já usa. A recusa é alta e visível, que é o oposto da falha atual.
- **Três dos quatro corpos são reescritos e o quarto não.** Aí `## Proposal` afirma que o `Edit`
  saiu do caminho enquanto um comando ainda escreve record à mão, e a afirmação lê como verdadeira.
  **Mitigação:** uma asserção de grep em `## Validation` — nenhum corpo em `commands/specs/` ainda
  descreve estampar record com `Edit` — e uma tarefa por corpo, não uma tarefa para os quatro.
- **`specs.py` cresce mais.** O arquivo tem 3.125 linhas e o spec irmão
  `split-specs-py-backlog-renderer` existe justamente porque o limiar de ~1.200 linhas que o próprio
  design do front declarou foi ultrapassado. Este spec adiciona ~120.
  **ACCEPTED —** as ~120 linhas substituem prosa duplicada em quatro corpos de comando, e adiar um
  caminho de escrita por contagem de linhas trocaria perda silenciosa de dados por arrumação. O
  limite é do irmão para resolver; este spec não move função nenhuma para módulo novo, então nada
  do que ele escreve conflita com um split posterior.
- **O caminho declarado em `## Impact` pode ser renomeado por baixo.** `docs/standards/code/` é uma
  pasta de assunto, e o spec irmão `revise-standards-subject-folders` pode revisar esse conjunto.
  **Mitigação:** nenhuma aqui — o caminho é declarado como está hoje e uma renomeação é migração
  daquele spec, com `okf-validate.py` detectando o link órfão. Nomear é a fronteira; resolver não é
  deste spec.
- **A suposição que sustenta tudo:** `specs.py` é o único consumidor que lê os records de frontmatter
  de um spec. Verificado — `parse_frontmatter` existe em três scripts, e os outros dois leem
  `commands/**` (`skills.py`) e `docs/**` mais a zona de listagem de `plans/` (`okf-validate.py`,
  `--listing-root`), nunca os records de um spec; specs não são comandos, então o registry do Claude
  Code também não os parseia.
  **ACCEPTED —** se um quarto consumidor aparecer, a forma em bloco é a que os dois leitores
  existentes já leem igual, então a escolha continua sendo a segura.
- **Reversibilidade.** Reverter custa cinco arquivos (o script mais os quatro corpos) e **nenhuma
  migração**: todo record já escrito continua legível, porque as duas formas são lidas desde antes
  deste spec. **ACCEPTED —** o custo de desfazer é menor que o de manter.
- **Este spec deriva como `executing` sem nenhuma caixa marcada.** Preencher `## Handoff` na
  definição — que é o que a regra do gate pede, já que `validate` avisa sobre `## Handoff` vazio num
  spec que passou o ready — dispara a regra `executing` de `stages.derived`, que casa em
  "`## Handoff` filled". Então a ordem em que o front pede as seções e a ordem em que ele deriva
  estágio se contradizem.
  **ACCEPTED aqui, e nomeado como fronteira:** a derivação de estágio é do spec irmão
  `name-the-scaffolded-stage`, que já está aberto sobre exatamente essa família de perguntas. Este
  spec **não** mexe em `stages.derived` e não presume o que aquele vai decidir; só registra a
  evidência que encontrou, porque o próximo a preencher `## Handoff` na definição vai tropeçar no
  mesmo lugar.

## Tasks

### 1. O escritor mecânico

O grupo que fecha o caminho de perda silenciosa de dados. Terminado ele, um `subject:` com vírgula já
não é truncado, mesmo que nada mais deste spec chegue.

- [ ] 1.1 Escrever `render_record(name, fields)` — escolhe flow ou bloco indentado pela regra de
      `## Design` §A forma do record: bloco quando algum valor contém `,` ou ` #`, flow no resto
      files: plugins/quenching/assets/bin/specs.py
      pattern: plugins/quenching/assets/bin/specs.py (`set_frontmatter_key`, linha 1610)
      verify: python3 plugins/quenching/assets/bin/specs.py selftest
- [ ] 1.2 Escrever `set_frontmatter_record(text, name, rendered)` — substitui a linha da chave **e** a
      corrida indentada abaixo dela via `_indented_run`, preservando todas as outras linhas byte a
      byte. `set_frontmatter_key` fica intacto, servindo `outcome`
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py selftest
- [ ] 1.3 Adicionar `cmd_record`, a entrada em `build_parser` e a entrada em `DISPATCH`, com a
      releitura de conferência rodando **antes** de gravar e recusando com exit 2 sem tocar o arquivo
      quando um campo não volta idêntico
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py record --help
- [ ] 1.4 Adicionar ao `selftest` os cinco casos de round-trip da tabela de `## Validation` — vírgula,
      ` #`, valor comum, record que estava em bloco, e preservação do resto do bloco
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py selftest

### 2. Recusa e validação

- [ ] 2.1 Impor `writeOnce` lendo `records[nome].writeOnce` de `schema.json`: exit 2 mostrando o valor
      atual, com `--force` gravando e ecoando que forçou
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py selftest
- [ ] 2.2 Recusar nome de record desconhecido e campo fora de `records[nome].fields`, listando os
      aceitos na saída, e ecoar o `writtenBy` do record em toda escrita bem-sucedida
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py selftest
- [ ] 2.3 Generalizar `merge_record_finding` em uma checagem `sp-bad-record` sobre todos os records,
      na mesma leitura de `records[nome]`, mantendo as duas formas legais de `merge` — e decidir a
      severidade per `## Open Decisions` rodando a checagem contra os 46 specs do repositório
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py --root specs validate --json
- [ ] 2.4 Corrigir `records.branch.writtenBy` de `execute` para `isolate` em `schema.json` **e** em
      `DEFAULT_SCHEMA`, porque `_behavioral` compara esse campo
      files: plugins/quenching/assets/specs/schema.json, plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py selftest

### 3. Ligar os quatro comandos donos

Um corpo por tarefa, não uma tarefa para os quatro: é o que faz o risco "três migram e um fica" ser
visível na lista em vez de escondido dentro de um commit.

- [ ] 3.1 `conclude.md` — `reviewed` e `merge` passam a ser escritos por `specs.py record`. Primeiro
      da fila porque é o corpo que estampa o record de valor perigoso
      files: plugins/quenching/commands/specs/conclude.md
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json
- [ ] 3.2 `isolate.md` — `branch: {base, work}` passa pelo escritor, mantendo a regra de que um record
      já presente é lido e nunca reescrito
      files: plugins/quenching/commands/specs/isolate.md
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json
- [ ] 3.3 `develop.md` — `refined` e `approved` passam pelo escritor. A linha de `verification` na
      tabela do passo 6 fica como está: é chave escalar requerida, não record, e está fora do escopo
      files: plugins/quenching/commands/specs/develop.md
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json
- [ ] 3.4 `triage.md` — `priority` passa pelo escritor, e a instrução de "merging, never rewrite"
      deixa de ser prosa e passa a ser o que a ferramenta faz
      files: plugins/quenching/commands/specs/triage.md
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json
- [ ] 3.5 Rodar a asserção de grep de `## Validation` e confirmar que nenhum corpo em
      `commands/specs/` ainda descreve estampar um record com `Edit`
      verify: grep -rn "Edit" plugins/quenching/commands/specs/*.md | grep -iE "frontmatter|record|stamp"

### 4. O standard e a prova

- [ ] 4.1 Escrever `docs/standards/code/frontmatter-writing.md` (`authority: current` uma vez provado
      pelos grupos 1 a 3), cobrindo a forma escolhida pelos valores, a substituição da corrida
      indentada, a releitura de conferência e por que propriedade de record não é imposta
      files: docs/standards/code/frontmatter-writing.md
      pattern: docs/standards/code/frontmatter-parsing.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
- [ ] 4.2 Rodar a passagem de mutação de `## Validation` — as quatro mutações, uma por vez, revertidas
      depois — e registrar o resultado no commit que a fecha, per `selftest-mutation.md`
      verify: python3 plugins/quenching/assets/bin/specs.py selftest
- [ ] 4.3 Rodar o bloco de verificação inteiro de `## Validation` e confirmar que `sp-impact-uncovered`
      sumiu e que nenhum finding novo apareceu em `validate`, `doctor` ou `okf-validate.py`
      verify: python3 plugins/quenching/assets/bin/specs.py --root specs validate --json
