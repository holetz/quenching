---
type: standard
title: O critério de fan-out e a medição que o decidiu
description: O critério que separa os dois regimes de conduzir N specs — quem escreve na árvore de trabalho serializa, quem não escreve não — a medição de colisão sobre as 20 specs construíveis deste front que descartou o paralelismo na construção, e as quatro formas consideradas e rejeitadas; a procedure que as duas entradas leem em execução vive em specs-fanout/fanout.md e é citada, nunca restatada
resource: plugins/quenching/commands/specs/execute-queue.md, plugins/quenching/commands/specs/develop-batch.md, plugins/quenching/assets/references/specs-fanout/**
tags: [workflows, specs, queue, orchestration, isolation, parallelism]
timestamp: 2026-08-16
audience: both
authority: current
source: orquestrar-specs-em-paralelo plan (task 1.1) — a medição de colisão sobre as 20 specs construíveis deste front, e a sessão d45c0252-9c39-42c4-956a-6badb9fb58ee, que montou a fila à mão por ~1,2M tokens e ~2,1h de relógio serial e terminou em cinco PRs que colidiram entre si; enxugado ao que só o bundle pode carregar pelo review de branch da mesma spec, que mediu seis das oito seções restatando specs-fanout/fanout.md — a segunda cópia que plugin-layout.md §A contract a command reads at runtime is a reference, not a standard existe para impedir
maintainer: quenching
---

# O critério de fan-out e a medição que o decidiu

Conduzir N specs numa autorização só tem dois regimes, e este standard é dono de **por que** eles
são o que são: o critério que os separa, a medição que descartou o paralelismo na construção, e as
formas que foram consideradas e rejeitadas.

**A procedure que as duas entradas leem em execução não está aqui.** A forma da fila, a marca de
branch, o contrato de entrada, a classificação de bloqueio e a volta recursiva são
[fanout.md](/plugins/quenching/assets/references/specs-fanout/fanout.md) §The two regimes
§The queue's shape §The branch carries the slugs §The entry contract §Classifying a block
§The recursive return — citadas, nunca restatadas. Procedure que um comando lê rodando dentro de um
alvo é payload, não fato sobre o alvo
([../architecture/plugin-layout.md](../architecture/plugin-layout.md) §A contract a command reads at
runtime is a reference, not a standard). O que sobra aqui é o que aquela reference não pode
carregar: uma decisão medida contra **este** front.

O ciclo de uma spec é [plan-lifecycle.md](plan-lifecycle.md) e a execução de uma task é
[task-execution.md](task-execution.md). Nada aqui substitui nenhum dos dois.

## O critério que separa os dois regimes

| Regime | Forma | Entrada |
| --- | --- | --- |
| **construção** | fila **serial** sobre um isolamento único | `/quenching:specs:execute-queue` |
| **definição** | lote **paralelo** de verdade | `/quenching:specs:develop-batch` |

**Quem escreve na árvore de trabalho serializa; quem não escreve, não.** Esse é o critério inteiro,
e é contra ele que uma terceira entrada de fan-out será medida: `create` e `develop` não tomam
branch alguma e, sob os backends `github` e `azure-boards`, não tocam arquivo algum; `execute`
escreve código, e código colide.

O critério decide o nome junto com a forma. A entrada de definição **não se chama fila** porque a
serialização é feature declarada apenas da outra, e um nome cujo objeto aparente difere do que ele
opera é proibido por [../naming/command-surface.md](../naming/command-surface.md) §Verb-first names
that reveal the action.

## A medição que descartou o paralelismo na construção

Sobre as 20 specs construíveis deste front, com 143 arquivos declarados sob `## Impact` e 190 pares
possíveis:

| Medida | Valor |
| --- | --- |
| pares que colidem, caminho como declarado | **107 de 190 (56%)** |
| pares que colidem, caminho normalizado pelo basename | **150 de 190 (79%)** |
| maior lote provadamente disjunto | **4 de 20** |
| a pior spec isolada — `upgrade-okf-to-v0-2` | colide com **19 de 19** |

A disjunção que o paralelismo exigiria não existe nessa densidade, e as duas linhas de colisão
divergem porque `## Impact` declara caminhos em notação inconsistente — o que torna não confiável
qualquer prova mecânica de disjunção **entre** specs, ao contrário do `[P]` **dentro** de uma spec,
cujos caminhos um autor só escreveu uma vez.

A forma serial resolve de graça um segundo defeito, e este é o argumento que sobreviveria mesmo se a
colisão fosse zero: **o gate da spec N roda sobre o resultado de 1..N−1**. Runs paralelos medem cada
um seus gates isoladamente contra a mesma base, e a combinação só é verificada depois dos merges —
que é exatamente quando ninguém está olhando.

**A economia de token não vem do paralelismo, e por isso a serialização não a custa.** Ela vem de
cada spec rodar num subagente de contexto próprio — uma fila in-session faria a spec N re-enviar o
contexto das N−1 anteriores a cada turno — e de **um** `conclude` em vez de N, com o review de
branch, o release e o archive pagos uma vez.

## O que esta forma deliberadamente não é

Quatro alternativas foram consideradas e rejeitadas. Cada uma volta a parecer óbvia para quem só vê
a fila pronta, e é por isso que a rejeição fica escrita com o motivo:

- **Lotes provadamente disjuntos** — o `[P]` check subido um nível. Teto medido de 4 em 20, e a
  notação inconsistente dos caminhos torna a prova não confiável sem normalização prévia.
- **Trem de integração** — N branches mergeadas em ordem num `train/<data>`, cada uma rebaseando
  sobre o resultado da anterior. É a única que escalaria para 50, e é a que deixa a spec 3 ter o
  chão mudado pela 2.
- **Fila de merge com rebase-on-green** — preservaria a revisão por spec, ao custo de re-rodar os
  gates N vezes e de manter o paralelismo cujo teto a medição já mostrou ser 4.
- **Menu de run modes** — flags de invocação para volume de perguntas, forma de isolamento ou nível
  de esforço. Elas já foram retiradas uma vez, com o motivo escrito num standard próprio; a fila não
  as reintroduz por uma porta lateral.
