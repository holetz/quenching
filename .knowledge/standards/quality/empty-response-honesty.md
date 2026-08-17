---
type: standard
title: Empty-response honesty
description: Uma resposta vazia de um transporte de terceiro são dois estados — uma que não chegou e uma que legitimamente não tem nada — e só um deles se prova; a regra de recusar no choke point onde há prova estrutural, avisar onde há apenas suspeita corroborada, e nunca deixar o diagnóstico recusar
resource: plugins/quenching/assets/bin/quenching/specs/backends/**, plugins/quenching/assets/bin/quenching/specs/commands/doctor.py
tags: [quality, verification, backends, findings, severity, transport]
timestamp: 2026-08-17
audience: both
authority: current
source: spec falha-de-leitura-do-backend-vira-front-vazio (tasks 1.1-3.2) — provado pelas guardas em github.py e pelos testes em test_specs_backends.py e test_specs_doctor.py
maintainer: quenching
---

# Empty-response honesty

**Um processo de terceiro que sai 0 e devolve nada não disse "não há nada" — ele não disse nada.**
As duas frases são indistinguíveis para quem lê o valor de retorno, e é essa indistinção que
transforma uma falha de transporte num fato: a listagem volta vazia, o comando responde
`{"ok": true, "count": 0}` com exit 0, e todo consumidor a jusante conclui que o front está vazio.

Este contrato é o irmão de [parse-honesty.md](parse-honesty.md), um nível abaixo. Aquele governa um
**transform com perda** dentro do processo; este governa o **payload que chegou** de fora dele.
Nenhum dos dois alcança o outro: um parser honesto sobre o que leu ainda pode estar lendo um vazio
que nunca aconteceu.

## A regra

> Um leitor que aceita um payload vazio de um processo externo MUST separar a forma que **prova**
> uma falha da forma que apenas a **sugere**, e tratar as duas de modos diferentes: recusa exit 2
> onde há prova, finding `warn` mais uma linha em `stderr` onde há suspeita, e nunca silêncio para
> nenhuma das duas.

Três consequências, na ordem em que obrigam.

### 1. A prova é estrutural, e vem de uma medição com versão

A separação só existe onde o transporte tem uma forma que uma resposta legítima nunca toma. Medido
em `gh 2.97.0 (2026-07-31)`, `gh api --paginate --slurp` sobre uma listagem de issues:

| O que volta | O que é | O que fazer |
| --- | --- | --- |
| `None` — saiu 0 e não imprimiu nada | uma resposta que **não chegou** | recusa, exit 2 |
| `[]` — zero páginas | uma resposta que **não aconteceu** | recusa, exit 2 |
| `[[]]` — uma página, vazia | um front genuinamente vazio | segue |
| `[[…], […]]` | saudável | segue |

`[[]]` versus `[]` é o discriminante inteiro, e ele é uma propriedade do `--slurp` do `gh`, não da
API. Por isso a **versão medida viaja dentro da mensagem da recusa**: um `gh` futuro que mude a
forma precisa quebrar de modo legível, e não em silêncio.

**Onde não há discriminante estrutural, não há recusa.** `azure.py` já escreveu essa metade para o
seu próprio transporte: numa consulta WIQL, zero matches e uma macro que não resolveu são
byte-idênticos — exit 0, stdout vazio, stderr vazio — então recusar por vazio ali recusaria o caso
ordinário "ainda não há specs" com a mesma frequência com que pegaria a falha. Inventar um
discriminante que a medição não sustenta é pior que não ter um.

### 2. A guarda é do CHAMADOR, nunca do transporte compartilhado

A função que executa o processo é compartilhada por leituras e escritas, e uma resposta vazia é a
resposta **certa** para algumas delas: um DELETE cuja resposta legítima é 204 No Content imprime
nada, e `null` ali é correto. Uma guarda por stdout vazio dentro do executor quebraria essa chamada
silenciosamente — e o executor é exatamente o lugar óbvio onde alguém a colocaria.

**Só o chamador sabe qual forma pediu.** Ele afirma essa forma no choke point por onde toda leitura
passa, o que faz todo verbo herdar a guarda de graça — inclusive um verbo escrito amanhã, cujo autor
não precisa saber que a regra existe. É a mesma forma que
[`code/root-override-validation.md`](../code/root-override-validation.md) §One refusal idiom, one
message, two call sites já fixa: **message e remedy escritos uma vez ao lado do predicado, e
citados** por cada call site, nunca redigidos de novo.

### 3. A suspeita é dita em voz alta, nas duas colocações, e o diagnóstico completa

A forma que não se prova ainda merece ser dita, porque ficar em silêncio sobre ela é o defeito
original reaparecendo um passo adiante. Ela precisa de **corroboração que não custe round trip
novo** — um número que a mesma chamada já pagou. Sem corroboração disponível, não há aviso: um
contador ausente nunca é lido como zero.

As duas colocações são as de
[`unproven-capability-warning.md`](unproven-capability-warning.md) §Two placements, e **as duas
embarcam ou a resposta está incompleta**: um finding `warn` no verificador da front, e uma linha em
`stderr`, uma vez por processo. `stderr` e nunca `stdout` — todo chamador ramifica pelo payload
`--json`, e um aviso impresso nele quebra o parse que ele existe para informar.

**A glosa "a linha cai nas escritas e nunca nas leituras", daquele mesmo standard, não se aplica
aqui, e a exceção é declarada em vez de assumida.** Ela se justifica porque "a read of an unproven
backend loses nothing — it returns wrong data or a refusal, and both are visible immediately". Numa
leitura vazia o dado errado é precisamente o que **não** é visível: ele se lê como um fato. A regra
de baixo não muda — a linha cai onde a perda aconteceria; aqui isso é a leitura.

**O verificador nunca recusa.** A mesma evidência que é exit 2 no choke point de leitura vira
finding no `doctor`, com a mensagem e o remedy da própria recusa citados e não recompostos. Isso vale
inclusive para as recusas que não têm nada a ver com vazio: um 503 no meio do diagnóstico também
vira finding, porque um diagnóstico que aborta é justamente o que não se pode ter no momento em que
alguém foi perguntar o que está errado.

**A severidade da suspeita é `warn`, e a razão é a mesma de
[parse-honesty.md](parse-honesty.md) §Severity: warn, and why not error**: um repositório que adotou
o backend sobre um tracker existente e ainda não criou spec nenhum **é** esse estado, exatamente, e é
legítimo. Errar ali reprovaria repositórios conformes.

## A redação é o discriminante que o código não tem

Restringir o gatilho não separa os dois estados — eles são a mesma observação. O que os separa é o
aviso **dizer o número e a leitura esperada**, para que quem está no estado legítimo se reconheça
nele: *"N issues abertas e nenhuma com marcador de spec; se você ainda não criou um spec aqui, isto é
esperado"*. Um aviso que não diz isso é treinado a ser ignorado, e um aviso ignorado é a mesma coisa
que silêncio.

## O teste prova o ramo; a premissa é medida

Um teste que mocka o transporte devolvendo stdout vazio prova que a guarda existe — e **não** prova
que uma resposta saudável nunca sai assim. Essa premissa é uma medição, com data e versão, e vive na
`## Validation` da spec como comando manual, nunca como asserção de suíte.
[`selftest-mutation.md`](selftest-mutation.md) §The rule fecha o par: quebrar a guarda e ver o teste
falhar, uma mutação por regra, revertida depois.

## Onde isto se aplica

Qualquer leitor deste repositório que aceite um payload de um processo de terceiro cujo exit code
não distingue "vazio" de "não respondeu" — os backends `github` e `azure-boards` hoje, e qualquer
transporte que um backend futuro adicione. **Não se aplica** a uma leitura cuja resposta vazia é
inequívoca: um diretório vazio sob o backend `files` não tem processo nem exit code para
interpretar, e ali vazio quer dizer vazio.
