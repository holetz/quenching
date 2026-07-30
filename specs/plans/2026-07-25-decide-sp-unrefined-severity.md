---
slug: decide-sp-unrefined-severity
title: Decide whether sp-unrefined should escalate to error
verification: per-section
refined: {mode: gate, date: 2026-07-30}
---

# Decide whether sp-unrefined should escalate to error

## Overview

Quando um spec já tem tudo o que precisa para ser construído mas ninguém discutiu com ele, a
ferramenta do front avisa. Esse aviso é o `sp-unrefined`, e ele é só um aviso: nunca impediu ninguém
de construir. A pergunta guardada aqui é antiga — o aviso deveria ser mais severo? — e ela foi deixada
em espera de propósito, à espera de evidência sobre quantos specs realmente chegam ao ponto de
construção sem terem sido questionados.

`## Problem` guarda a pergunta como ela foi capturada, e acrescenta a correção de que dois termos que
ela usa descrevem uma versão antiga da ferramenta que já não existe. `## Design` faz o trabalho
central em cinco partes: mostra onde o aviso nasce no código; mostra que a severidade dele não decide
nada, nem o código de saída nem se alguém pode construir; conta os números que hoje existem no
histórico de specs encerrados; e então vira essa conta do avesso duas vezes, explicando o que ela não
consegue medir e como este próprio dia de trabalho atrapalha a medição futura.
`## Alternatives Considered` compara as cinco saídas possíveis, incluindo a de não fazer nada, e diz
por que cada uma perdeu.

`## Proposal` é a consequência disso: nada muda na severidade, e o esforço vai para escrever, num
documento permanente, por que ela é assim e o que precisaria acontecer para mudá-la. `## Impact`
declara esse documento — um só — e diz explicitamente o que o spec não promete escrever e que código
ele apenas lê. `## Validation` traz o comando que mede a condição de reabertura, já executado, porque
o maior perigo deste spec não é errar a severidade: é escrever uma condição que ninguém nunca mede.
`## Risks` é longo pelo mesmo motivo, e porque três specs irmãos estão em desenvolvimento ao mesmo
tempo e podem mexer no mesmo arquivo, na mesma língua ou no mesmo conceito.

`## Open Decisions` é onde a pergunta continua viva, agora com uma condição concreta que a reabre em
vez de uma promessa vaga de revisitar, e com o único número que ainda precisa do aval de um humano.
`## Out of Scope` marca as vizinhas que se parecem com este trabalho e não são dele. `## Handoff` e
`## Tasks` são curtos porque quase todo o resultado deste spec é texto que fica registrado, não código
novo: seis tasks, e nenhuma delas toca `specs.py`.

## Problem

Decisão aberta herdada do plano `refine-and-execute-specs-flow` — revisitar a severidade do warning
quando houver evidência sobre plans não refinados.

_(tarefa de backlog v1 — tags: ['specs', 'validation'])_

`specs.py validate` emite `sp-unrefined` em severidade **warn** quando um plan tem um `tasks.md` e
nenhum refinamento registrado, deixando `applyReady` deliberadamente intacto — gatear em refinamento
quebraria todo plan existente em todo repositório instalado no momento do upgrade, e a doutrina do
front é que um sweep nunca bloqueia em juízo de valor. Se o warning é forte o bastante é uma questão
aberta, e o design do plano manda revisitá-la "once there is evidence about how often plans reach
apply unrefined" — evidência, não argumento. Não há data de trigger; isso fica parado até o registro
de refinamento acumular história suficiente para ser lida.

**Correção de vocabulário levantada pelo pass de refinamento de 2026-07-30.** Ela é aditiva: o
parágrafo acima fica preservado como foi capturado, porque é ele que registra a intenção original.
Os dois termos v1 que ele usa já não descrevem o código:

- `tasks.md` era um arquivo do plan de três arquivos da v1. Hoje ele só é detectado como resíduo, por
  `_v1_leftovers()` em `plugins/quenching/assets/bin/specs.py:2676`, e um spec é UM arquivo por toda
  a sua vida.
- `applyReady` não existe em nenhum lugar do repositório. `grep -rn applyReady .` devolve exatamente
  uma ocorrência: a desta própria seção.

A emissão real de hoje está em `plugins/quenching/assets/bin/specs.py:2553`, condicionada a
`ready and ready["ok"] and not fm.get("refined")` — um arquivo único julgado contra o stage derivado
`ready`, e não contra a presença de um `tasks.md`. A pergunta de fundo sobrevive intacta; o
vocabulário que a descrevia, não.

## Proposal

Este spec não escolhe a severidade por decreto — ele torna a escolha decidível, e desloca o ônus da
prova para quem quiser mudá-la. Depois dele:

- O `## Problem` deixa de descrever o código em vocabulário v1: `tasks.md` e `applyReady` estão
  nomeados como obsoletos, com o sítio de emissão real citado por caminho e linha.
- Está escrito, e conferível no código, que **severidade não é gate**: nada no front deriva
  comportamento da severidade de `sp-unrefined`. "Escalar para error" e "gatear o build em
  refinamento" são duas alavancas distintas, e a decisão original tratava as duas como uma só.
- A alavanca (a), a severidade em `specs.py validate`, segue `warn` — não por inércia, mas porque a
  evidência disponível não sustenta mudá-la, e o motivo fica registrado como regra durável em
  `docs/standards/workflows/plan-artifacts.md` em vez de viver só neste spec.
- A alavanca (b), uma recusa real em `/specs:execute` ou em `specs.py next`, segue fora de escopo, e
  o spec diz em que arquivos e linhas essa doutrina está escrita.
- A questão para de ser um "revisitar algum dia" sem data: passa a existir um **trigger
  falsificável**, medível por um comando de uma linha sobre `specs/archive/`, que a reabre quando a
  evidência mudar de sinal.
- A evidência de 2026-07-30 fica registrada com os números, não com adjetivos, para que um leitor
  futuro veja contra o que o trigger foi calibrado — e possa refazer a conta.

## Out of Scope

- **Expor advisory/blocking como dado no payload `--json`** — é o spec irmão
  `expose-finding-advisory-as-data`, do lado do `okf-validate.py`. Este spec decide a severidade de
  UM código em `specs.py validate`; ele não redesenha como a distinção advisory/blocking é expressa.
- **Mudar o contrato de exit code de `specs.py validate`** — hoje `cmd_validate` devolve
  `1 if findings else 0` (`plugins/quenching/assets/bin/specs.py:2673`), enquanto `doctor`
  (linha 2916) e `selftest` (linha 2831) devolvem `1 if errors else 0`. A assimetria é real e
  provavelmente merece discussão própria, mas ela vale para o vocabulário `sp-*` inteiro; resolvê-la
  aqui, partindo de um código só, seria decidir o geral pelo particular.
- **Gatear `/specs:execute` ou `specs.py next` em refinamento** — fora de escopo por doutrina
  escrita, não por falta de tempo: `plugins/quenching/commands/specs/develop.md:180` e
  `docs/standards/workflows/plan-artifacts.md:173`. Mudar isso é outra decisão, de alcance maior, e
  este spec não tem evidência que a sustente.
- **Instrumentar o front para coletar a evidência** — nenhuma telemetria é necessária. Os números de
  que o trigger precisa já estão no disco, em `specs/archive/**` (o registro `refined` e o registro
  `outcome`), e são lidos com `grep`.
- **Retirar, renomear ou reposicionar o código `sp-unrefined`** — o código continua existindo, com a
  mesma condição de disparo. Só a sua severidade estava em questão.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/workflows/plan-artifacts.md` — a distinção severidade-versus-gate no vocabulário
  `sp-*`, e a regra de reabertura da decisão sobre `sp-unrefined`, ambas acrescentadas à seção que já
  existe ("Refinement is recorded, surfaced, and never gating"). É uma edição **aditiva dentro de um
  home existente**: nenhuma seção nova, nenhuma superfície nova para um leitor futuro ter de aprender.

### Documentos que este spec deliberadamente NÃO promete escrever

- `docs/knowledge/glossary.md` — a entrada **Refinement record** (linha 175) já diz "non-gating", que
  continua verdadeiro. Nada a corrigir, e uma edição de glossário passa por `/docs:define`, não por
  uma task deste spec.
- Os nove sítios de doutrina listados em `## Design` — permanecem exatamente como estão. O spec os
  cita como evidência do custo de escalar; ele não os toca.

### Código que este spec lê e não altera

- `plugins/quenching/assets/bin/specs.py` — `_finding()` (2452), a emissão de `sp-unrefined`
  (2550-2557), o consumo de `severity` em `cmd_validate` (2661-2673) e `CONFIG_KEYS` (953). Nenhuma
  linha de `specs.py` muda: a severidade fica `warn`, e é essa a decisão.

## Validation

Este spec não muda comportamento, então a validação é de duas naturezas: uma **guarda de regressão**
(provar que a severidade continua onde estava) e a prova de que o trigger é **executável**, não uma
promessa.

**1. `sp-unrefined` continua `warn`, num único sítio.**

```bash
grep -n 'sp-unrefined' plugins/quenching/assets/bin/specs.py
```

Deve devolver exatamente uma linha, a 2554, e a chamada de `_finding` ao redor dela deve continuar
carregando `"warn"`. Qualquer segunda ocorrência em `specs.py` significa que a emissão foi duplicada.

**2. O front continua conformante e nenhum sítio de doutrina foi contradito.**

```bash
python3 plugins/quenching/assets/bin/specs.py validate --json
python3 plugins/quenching/assets/hooks/okf-validate.py docs
```

O primeiro não deve reportar `sp-impact-uncovered` para este spec — o caminho declarado em
`## Impact` é nomeado por task. O segundo deve imprimir `0 error(s), 0 warning(s)` depois da edição do
standard.

**3. O trigger roda e imprime um número.** Esta é a validação que importa, porque o risco principal do
spec é escrever uma condição que ninguém consegue medir:

```bash
for f in specs/archive/2026-*.md; do
  [ "$(basename "$f" | cut -c1-10)" \> "2026-07-27" ] || continue
  grep -q '^outcome: *done' "$f" || continue
  grep -q '^refined:' "$f" || echo "$f"
done | wc -l
```

Numerador: specs concluídos como `done`, nascidos depois de 2026-07-27, sem registro `refined`.
Medido em 2026-07-30 o resultado é **0**, contra um denominador de **6** specs `done` no mesmo
recorte. O comando tem de aparecer no standard junto com a regra, e tem de rodar sem erro no
repositório limpo — se ele deixar de rodar, a regra de reabertura morreu silenciosamente, que é
exatamente o modo de falha registrado em `## Risks`.

**4. Invariante que deve continuar valendo**: nenhuma linha de `plugins/quenching/assets/bin/specs.py`
foi modificada por este spec. `git diff --stat` na conclusão não deve listar esse arquivo.

## Design

### Como `sp-unrefined` é emitido hoje

Um único sítio, em `plugins/quenching/assets/bin/specs.py:2550-2557`:

```python
# Judged against the READY gate: a spec is "unrefined" once it could be built, not the
# moment it is captured. Warning on every fresh capture would train the reader to
# ignore the code.
if ready and ready["ok"] and not fm.get("refined"):
    out.append(_finding("sp-unrefined", "warn",
                        f"{where}: ready to build, but nobody has interrogated it",
                        spec=s["slug"], path=where,
                        remedy="run a refinement pass, or build as-is (never gated)"))
```

`ready` vem de `ready_report(...)` e só é calculado quando `s["phase"] == "plans"` (linha 2523), então
um spec arquivado nunca dispara o código. A condição é exatamente esta: as dez seções do gate `ready`
preenchidas **e** nenhum registro `refined` no frontmatter.

### A regra durável que este spec estabelece: severidade não é gate

`_finding()` (linha 2452) guarda `severity` como um campo de dados qualquer. Quem consome esse campo,
em todo o `specs.py`:

| Consumidor | O que faz com `severity` |
| --- | --- |
| `cmd_validate`, linhas 2661-2662 | calcula `errors` e publica `"ok": not errors` no JSON |
| `cmd_validate`, linhas 2666-2669 | imprime a contagem `N error(s), M warning(s)` e o rótulo de cada linha |
| `cmd_validate`, linha 2673 | **nada**: o retorno é `1 if findings else 0`, indiferente à severidade |

Três consequências medidas, e é sobre elas que a decisão gira:

- **O exit code de `specs.py validate` já é 1 para qualquer finding.** Um spec `ready` e não refinado
  já deixa a probe de `/specs:align` suja hoje — `plugins/quenching/commands/specs/align.md:41` diz
  "Both exit 0 with no findings". Escalar a severidade não acrescenta um único gate a isso.
- **`/specs:execute` não lê `validate` para decidir nada.** Ele ramifica em `specs.py next`
  (`plugins/quenching/commands/specs/execute.md:91-100`) e apenas *menciona* o warning uma vez, sem
  poder de recusa.
- Logo, o efeito observável total de escalar para `error` é: `"ok"` vira `false` no `validate --json`,
  e um item migra da contagem de warnings para a de errors. Nada mais.

A suposição que sustentava a decisão original — "escalar a severidade endurece o comportamento" — é
**falsa neste código**. Registrar isso é o produto mais valioso deste spec: é o que transforma uma
pergunta insolúvel em duas perguntas separadas e respondíveis.

### A evidência, medida em 2026-07-30

`specs/archive/` tem 13 specs concluídos. Cruzando o registro `refined` com o registro `outcome`:

| Spec arquivado | `outcome` | Tasks | `refined` |
| --- | --- | --- | --- |
| `2026-07-25-docs-verification-layer` | done | 26/26 | ausente |
| `2026-07-25-instrument-and-extend-skill-front` | done | 14/14 | ausente |
| `2026-07-26-collapse-skills-into-commands` | done | 35/35 | ausente |
| `2026-07-27-specs-flow-consolidation` | done | 33/33 | ausente |
| `2026-07-26-skill-description-tiering` | abandoned | 2/17 | `{mode: interview, date: 2026-07-26}` |
| os outros 8 | done | completos, exceto dois com uma box aberta (6/7 e 11/12) | `{mode: gate, date: 2026-07-28}` |

Leitura honesta desses números, com o confundidor à mostra:

- Bruto, 4 de 13 (31%) chegaram a `outcome: done` sem refinamento — e são justamente os quatro
  maiores do arquivo, 108 tasks somadas.
- Mas o registro `refined` só passa a existir em 2026-07-27, nos commits `488b794` (o registro em
  `schema.json`) e `d0908ff` (a emissão em `specs.py`). Os quatro nasceram entre 2026-07-25 e
  2026-07-27, ou seja, toda a fase de definição deles antecede o registro: não havia o que estampar.
- A leitura contrária, que merece ficar escrita: dois dos quatro foram arquivados em 2026-07-28, já
  depois do registro existir, e mesmo assim seguiram sem estampa. Isso não é um contraexemplo, porque
  `refined` é estampado na definição e não na conclusão — mas mostra que um warning não corrige
  retroativamente specs em voo.
- Dos 8 specs com estampa `{mode: gate}`, todos os 8 a têm datada de 2026-07-28: a prática vira
  universal a partir do dia seguinte à introdução do registro.
- O único spec refinado e depois abandonado (`skill-description-tiering`, `mode: interview`, 2/17
  tasks) é o warning funcionando como projetado: o refinamento pegou um spec que não devia ser
  construído, sem ter precisado bloquear nada.

Conclusão da leitura: a amostra de specs **nascidos depois** de 2026-07-27 que chegaram a `done` sem
refinamento é **zero**. A evidência que a decisão original esperava começou a chegar, e ela aponta
para manter `warn`. O tamanho da amostra (n=13, com 4 confundidos pela data de introdução do próprio
registro) é pequeno o bastante para que isso seja um ônus da prova, não um veredicto — e é por isso
que a decisão fica com um trigger em `## Open Decisions`, e não fechada aqui.

### Por que escalar seria uma mudança de doutrina, não de severidade

A afirmação "nunca gateia" está escrita em nove sítios, e um deles é um contrato vinculante:

| Sítio | O que diz |
| --- | --- |
| `docs/standards/workflows/plan-artifacts.md:172-173` | "It is a warning **by construction** ... **A spec may always be built unrefined.**" |
| `docs/knowledge/glossary.md:175` | "the **non-gating** `sp-unrefined` warning" |
| `plugins/quenching/assets/references/specs-align/conformance.md:192` | "**Never gates** — a spec may always be built unrefined." |
| `plugins/quenching/commands/specs/develop.md:180-181` | "Never gate on refinement." |
| `plugins/quenching/commands/specs/execute.md:98-100` | "Never gate on it: the ready gate is a floor, not a verdict." |
| `plugins/quenching/commands/specs/status.md:114-116` | "**none of these gates anything**" |
| `specs/QUENCHING.md:187` | "a warning, never a gate" |
| `plugins/quenching/assets/specs/QUENCHING.md:189` | a mesma frase, na cópia shipada do manual |
| `plugins/quenching/assets/bin/specs.py:2557` | o `remedy`: "or build as-is (never gated)" |

Escalar exigiria um lockstep de nove sítios cuja única mudança de comportamento seria um booleano
`ok`. Essa relação entre custo e efeito é o argumento decisivo, e é o que orienta o `## Proposal`:
gastar o esforço em tornar o trigger explícito, não em mexer na severidade.

### O que a evidência acima NÃO consegue medir

O pass adversarial derrubou uma premissa da leitura anterior, e ela fica registrada porque limita o
que qualquer trigger pode concluir.

A conta de 2026-07-30 usa a presença do registro `refined` como proxy de "alguém interrogou este
spec". Os dois não são a mesma coisa. O registro é estampado pela própria sessão que rodou o pass, e
`questions.md` §Recording the pass precisa dizer em voz alta "**Never fabricate it**" exatamente
porque nada no código pode verificar isso — `validate` confere que o registro existe e tem forma
válida, nunca que houve pergunta e resposta. Logo, uma taxa de 9 em 13 mede **estampas**, não
qualidade de interrogação.

Consequência prática para este spec: o trigger tem de dizer, na própria redação, que conta
**registros ausentes**, e não interrogações ausentes. Ele é um detector de omissão declarada, e é
honesto nessa escala; não é um medidor de rigor. Não há como corrigir isso barato — medir qualidade de
interrogação exigiria um juiz por spec — então isso entra como risco aceito, e não como task.

### O confundidor que este próprio pass introduz

Em 2026-07-30 trinta e dois specs de `plans/` estão recebendo um pass de refinamento autônomo, em
paralelo, cada um estampando `refined: {mode: ..., date: 2026-07-30}`. Este spec é um deles. Isso
significa que a linha de base contra a qual o trigger será medido no futuro contém um evento de
estampagem em massa num único dia, e um leitor que não soubesse disso concluiria que a prática de
refinamento é mais consistente do que a história realmente mostra.

A direção do viés importa e é favorável ao status quo: o trigger conta specs que chegaram a
`outcome: done` **sem** registro `refined`, e um evento de estampagem em massa reduz essa contagem.
Ou seja, o confundidor torna o trigger **menos** propenso a disparar, nunca mais. Um trigger que
disparar apesar dele é, por isso, um sinal mais forte do que os números sozinhos sugerem. Fica
registrado aqui em vez de corrigido, porque a correção — descartar os specs estampados em 2026-07-30 —
descartaria trinta e dois dos quarenta e cinco specs do workspace e deixaria a amostra sem tamanho
nenhum.

### O que fica resolvido, e o que fica aberto

- **Resolvido**: o status quo prevalece por ausência de evidência a favor da mudança, e o motivo
  passa a ser regra durável em `docs/standards/workflows/plan-artifacts.md` — junto com a distinção
  severidade-versus-gate, que hoje não está escrita em nenhum lugar do bundle.
- **Aberto**, em `## Open Decisions`: o trigger que reabre a questão e o seu limiar, e se a expressão
  certa para "isto é advisory" é severidade ou um campo de dado, o que depende do spec irmão
  `expose-finding-advisory-as-data`.

## Alternatives Considered

Alternativas de forma inteira, avaliadas contra o código lido em 2026-07-30. Cada uma está no seu
melhor argumento, não numa versão de palha.

| Abordagem | Custo | O que compra | O que impede | Veredicto |
| --- | --- | --- | --- | --- |
| **A. Escalar `sp-unrefined` para `error`** | lockstep de nove sítios, um deles contrato vinculante; `ok: false` em todo repositório instalado que tenha um spec `ready` não refinado, já no upgrade | um booleano `ok` mais alto, e nada mais: o exit code já é 1 | a regra própria do front de que um sweep nunca bloqueia em juízo de valor | **rejeitada** — paga uma mudança de doutrina por um efeito que não é um gate |
| **B. Não fazer nada e abandonar o spec** | zero | zero trabalho | nada | **rejeitada** — deixaria de pé o vocabulário v1 errado no `## Problem` e um "revisitar" sem data, que é o defeito que criou este spec |
| **C. Manter `warn` e escrever o trigger** | um spec pequeno, sem tocar a severidade; uma edição em `plan-artifacts.md` | a decisão fica falsificável e medível; a confusão severidade-versus-gate para de se repetir | nada: nenhum comportamento muda | **escolhida** — é o caminho que compra 80% do valor com 20% da mudança |
| **D. Tornar a severidade configurável por workspace** | uma chave nova em `specs/config.json` (`CONFIG_KEYS` hoje é `("worktreeSetup",)`, `specs.py:953`), mais a máquina de `sp-config-unknown-key` | um repositório que queira regra dura consegue uma | a doutrina única: dois repositórios passariam a discordar sobre o que é conformidade, e o vocabulário `sp-*` deixaria de significar a mesma coisa em toda instalação | **rejeitada** — configurabilidade aqui é uma segunda fonte de verdade sobre severidade |
| **E. Gatear `/specs:execute` em refinamento** | a mudança de comportamento real que A não entrega | garantiria que nada é construído sem interrogação | a doutrina escrita em `develop.md:180` e `plan-artifacts.md:173`, e o princípio de que o gate `ready` é um piso, não um veredicto | **rejeitada** — é a alavanca certa para a preocupação original, e é exatamente a que a doutrina proíbe; mudá-la exige um spec próprio, com evidência que hoje não existe |

As três que quase nunca ficam escritas, explicitamente consideradas: **não fazer nada** é B;
**a menor coisa que funcionaria** é C, e foi a escolhida; **comprar ou emprestar em vez de
construir** não se aplica — não há verificador externo que decida a severidade de um código do
vocabulário `sp-*` deste repositório.

## Open Decisions

- **O limiar do trigger.** A regra proposta: reabrir a decisão quando, numa janela móvel dos **dez**
  specs mais recentemente concluídos em `specs/archive/` — contando **apenas** os nascidos depois de
  2026-07-27, a data em que o registro `refined` passou a existir — **três ou mais** carregarem
  `outcome: done` sem registro `refined`. Abaixo disso, a severidade permanece `warn` sem discussão.
  *Como se decide*: o número 3 é o único botão de juízo aqui, e é a recomendação deste pass, não um
  fato medido; ele precisa do OK de um humano antes de virar regra no standard, e a task 2.2 existe
  para pedir esse OK. A medição em si não precisa de ninguém: é o comando de `## Validation` §3, que
  hoje devolve 0 de 6.
- **Se a severidade é o veículo certo para "isto é advisory".** O spec irmão
  `expose-finding-advisory-as-data` está avaliando trocar a prosa por um campo de dado no payload
  `--json` do `okf-validate.py`, e o `## Problem` dele diz textualmente que "the severity vocabulary
  (`ERROR`/`WARN`) may be the better place to express it than a parallel field". Se ele concluir que o
  campo de dado é o lugar certo, a pergunta deste spec muda de forma: não seria mais "warn ou error",
  e sim "qual o valor de `blocking` para `sp-unrefined`". *Como se decide*: pelo desfecho do irmão.
  Este spec não o antecipa e não depende dele — o trecho que ele escreve no standard afirma a
  distinção entre severidade e gate, que sobrevive às duas saídas.
- **A decisão original, a severidade de `sp-unrefined`.** Continua formalmente aberta, mas com o ônus
  da prova invertido: o status quo `warn` prevalece, e passa a exigir evidência de quem quiser
  mudá-lo, em vez de exigir evidência de quem quer mantê-lo. *Como se decide*: pelo trigger do
  primeiro item. Enquanto ele não disparar, não há decisão pendente para ninguém tomar — e é essa
  transformação, de pergunta em espera indefinida para condição verificável, o produto deste spec.

## Risks

- **O trigger é escrito e nunca é medido**, virando o mesmo "revisitar algum dia" que ele substitui,
  agora com mais palavras. É o modo de falha mais provável deste spec, e o pior: ninguém o percebe,
  porque nada agenda a medição. *Mitigação*: o trigger nasce junto com o comando de uma linha que o
  mede, escrito em `## Validation` **e** dentro do próprio standard, para que um leitor futuro rode a
  conta em segundos em vez de ter de rederivá-la a partir do frontmatter. Não há como garantir que
  alguém rode; há como garantir que rodar seja trivial.
- **`refined` mede estampa, não interrogação** (ver `## Design` §O que a evidência acima NÃO consegue
  medir). `ACCEPTED — ` não existe medição barata de qualidade de interrogação, e o trigger declara
  explicitamente que conta registros ausentes, o que o mantém honesto na escala em que ele opera.
- **O pass em massa de 2026-07-30 polui a linha de base** deste spec e de outros trinta e um.
  ACCEPTED — o viés é direcional e favorece o status quo: ele só reduz a contagem que faria o
  trigger disparar, então um disparo futuro continua sendo sinal válido. Descartar os specs afetados
  deixaria a amostra sem tamanho.
- **Amostra pequena**: n=13 specs arquivados, dos quais 4 confundidos pela data de introdução do
  próprio registro. `ACCEPTED — ` é precisamente por isso que a saída deste spec é um ônus da prova
  com trigger, e não um veredicto definitivo sobre a severidade.
- **O spec irmão `revise-standards-subject-folders` pode mover
  `docs/standards/workflows/plan-artifacts.md` para outra pasta de assunto**, invalidando o caminho
  que este spec declara em `## Impact`. *Mitigação*: a task que edita o standard resolve o arquivo
  pela sua âncora de conteúdo (a seção "Refinement is recorded, surfaced, and never gating") com
  `grep -rl`, e não por caminho fixo; se o irmão já tiver aterrissado, o caminho dele prevalece e a
  declaração de `## Impact` é corrigida na hora, não discutida. Este spec não assume nenhum desfecho
  do irmão.
- **O spec irmão `declare-repo-body-language` pode mudar a língua em que o standard deve ser
  escrito.** Hoje `plan-artifacts.md` está em inglês. *Mitigação*: a task escreve o trecho novo na
  língua que o arquivo já usar no momento da execução, sem traduzir o resto do documento — a decisão
  de língua é do irmão, e este spec apenas a obedece.
- **O spec irmão `expose-finding-advisory-as-data` pode tornar a severidade o veículo errado** para
  expressar "isto é advisory", trocando-a por um campo de dado no payload. *Mitigação*: o trecho que
  este spec escreve no standard afirma a **distinção** entre severidade e gate, não a frase "warn é a
  severidade correta". Essa formulação sobrevive a qualquer desfecho do irmão, inclusive ao de a
  severidade deixar de ser o lugar onde advisory é expressa.
- **Risco de valor, não de execução**: se o front precisar cortar specs de baixo retorno, este é um
  candidato legítimo a `abandoned` — quase todo o seu produto é texto. *Mitigação*: antes de abandonar,
  colher a correção de vocabulário do `## Problem` via `/docs:learn`, porque ela é uma constatação
  sobre o código que sobrevive à morte do spec.

## Tasks

### 1. A regra durável no standard

- [ ] 1.1 Resolver o home atual do standard pela âncora de conteúdo e conferir a declaração de `## Impact`
      verify: grep -rl 'Refinement is recorded, surfaced, and never gating' docs/standards/
- [ ] 1.2 Escrever em `docs/standards/workflows/plan-artifacts.md` a distinção severidade-versus-gate, citando o sítio de emissão e o retorno de `cmd_validate` por linha (authority: current)
      files: docs/standards/workflows/plan-artifacts.md
      pattern: docs/standards/workflows/plan-artifacts.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
- [ ] 1.3 Escrever em `docs/standards/workflows/plan-artifacts.md` a regra de reabertura, com o comando que a mede embutido e o valor medido em 2026-07-30 (0 de 6) como linha de base
      files: docs/standards/workflows/plan-artifacts.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs

### 2. Guarda de regressão e fechamento da decisão

- [ ] 2.1 Provar que a severidade não mudou e que nenhum dos nove sítios de doutrina foi contradito
      verify: grep -c 'sp-unrefined' plugins/quenching/assets/bin/specs.py
- [ ] 2.2 Pedir ao humano o OK sobre o limiar do trigger (três em dez, recomendado) e registrar a resposta em `## Open Decisions`
- [ ] 2.3 Confirmar que `git diff --stat` não lista `plugins/quenching/assets/bin/specs.py`
      verify: git diff --stat
