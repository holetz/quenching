---
type: standard
title: Contrato da fila de specs
description: Conduzir N specs de uma vez — a construção é uma fila serial sobre um isolamento único e a definição é um lote paralelo, a medição de colisão que decidiu qual é qual, o estágio de entrada derivado de priority.complexity, a classificação de bloqueio e a saída do contaminante, a regra uma branch/uma PR, a ausência deliberada de teto de N, e o contrato de parada da volta recursiva
resource: plugins/quenching/commands/specs/execute-queue.md, plugins/quenching/commands/specs/develop-batch.md, plugins/quenching/commands/specs/cycle.md, plugins/quenching/assets/references/specs-fanout/**
tags: [workflows, specs, queue, orchestration, isolation, parallelism]
timestamp: 2026-08-16
audience: both
authority: current
source: orquestrar-specs-em-paralelo plan (task 1.1) — a medição de colisão sobre as 20 specs construíveis deste front, e a sessão d45c0252-9c39-42c4-956a-6badb9fb58ee, que montou a fila à mão por ~1,2M tokens e ~2,1h de relógio serial e terminou em cinco PRs que colidiram entre si
maintainer: quenching
---

# Contrato da fila de specs

Conduzir N specs numa autorização só. Este standard é o dono normativo de **como** N specs
avançam juntas; o ciclo de uma spec — captura, definição, construção, fechamento — é
[plan-lifecycle.md](plan-lifecycle.md), e a execução de uma task é
[task-execution.md](task-execution.md). Nada aqui substitui os dois: a fila **invoca** os comandos
de uma spec e nunca reimplementa o que eles fazem.

## Dois regimes, e o que separa um do outro

| Regime | Forma | Por quê |
| --- | --- | --- |
| **construção** — `/quenching:specs:execute-queue` | fila **serial** sobre um isolamento único | as specs escrevem arquivos, e os arquivos colidem (§A medição) |
| **definição** — `/quenching:specs:develop-batch` | lote **paralelo** de verdade | `create` e `develop` não tomam branch alguma, e sob backend `github` não tocam a árvore de trabalho |

O critério é um só: **quem escreve na árvore de trabalho serializa; quem não escreve, não**. É por
isso que a entrada de definição não se chama fila — a serialização é a feature declarada apenas da
outra, e um nome cujo objeto aparente difere do que ele opera é proibido por
[../naming/command-surface.md](../naming/command-surface.md) §Verb-first names that reveal the
action.

## A medição que descartou o paralelismo na construção

Sobre as 20 specs construíveis deste front, com 143 arquivos declarados sob `## Impact` e 190 pares
possíveis:

| Medida | Valor |
| --- | --- |
| pares que colidem, caminho como declarado | **107 de 190 (56%)** |
| pares que colidem, caminho normalizado pelo basename | **150 de 190 (79%)** |
| maior lote provadamente disjunto | **4 de 20** |
| a pior spec isolada — `upgrade-okf-to-v0-2` | colide com **19 de 19** |

A disjunção que o paralelismo exigiria não existe aqui, e as duas linhas de colisão divergem porque
`## Impact` declara caminhos em notação inconsistente — o que torna não confiável qualquer prova
mecânica de disjunção **entre** specs, ao contrário do `[P]` **dentro** de uma spec, cujos caminhos
um autor só escreveu uma vez.

A forma serial resolve de graça um segundo defeito, e este é o argumento que sobreviveria mesmo se a
colisão fosse zero: **o gate da spec N roda sobre o resultado de 1..N−1**. Runs paralelos medem cada
um seus gates isoladamente contra a mesma base, e a combinação só é verificada depois dos merges —
que é exatamente quando ninguém está olhando.

**A economia de token não vem do paralelismo, e por isso a serialização não a custa.** Ela vem de
cada spec rodar num subagente de contexto próprio (uma fila in-session faria a spec N re-enviar o
contexto das N−1 anteriores a cada turno) e de **um** `conclude` em vez de N — o review de branch, o
release e o archive pagos uma vez.

## Uma branch, uma PR

A fila é: **isolar uma vez → N × `/quenching:specs:execute` na mesma branch → 1 ×
`/quenching:specs:conclude` sem `--spec`**.

A branch carrega a marca `quenching-slugs:` com os slugs de todas as specs que entraram nela, e é
essa marca que o `conclude` sem `--spec` lê para resolver o conjunto —
[plan-git-record.md](plan-git-record.md) §The branch also carries a git-native mark é dona do
formato e da resolução. Nada é encadeado: sem stacked branches, sem PRs empilhadas, sem merge queue
com rebase-on-green. Encadear troca conflito de merge por conflito de rebase e acopla o destino das
specs em cadeia.

`/quenching:specs:execute` para no último commit — o review, o merge e o archive são de outro
comando — e é exatamente aí que uma fila precisa que ele pare.

## O estágio de entrada deriva de `priority.complexity`

Nenhuma flag de invocação, nenhum menu:

| `priority.complexity` | Onde a spec entra |
| --- | --- |
| `low` | pela definição, e segue até o fim |
| `medium` ou acima | exige `ready`/`approved`; é apenas construída |

Uma spec cuja `complexity` **sobe durante a fila** sai da fila e pede autorização nova, sob o mesmo
contrato que `specs-cycle/gears.md` §Re-evaluating a gear já define. `complexity` declara
`[triage, create, develop]` como escritores ([plan-lifecycle.md](plan-lifecycle.md) §Frontmatter
records human judgments), então a subida é um fato que a própria fila observa, nunca um que ela
carimba.

**A fila roda a política de verificação que cada spec declara, e não julga quem a escolheu.** Uma
política declarada é autoritativa por definição; separar decisão de carimbo é um assunto de
frontmatter que a fila não pode resolver e não tenta.

## Classificação de bloqueio, e a saída do contaminante

Um bloqueio é **declarado onde é julgamento e medido onde é verificável**.

| Classificação | Quem decide | O que a fila faz |
| --- | --- | --- |
| **local** | o executor da spec | marca `[!]` e segue para a próxima |
| **contaminante** | o executor da spec | para a fila e pergunta |
| **gate vermelho** | o gate declarado, após cada spec | para a fila, independentemente da classificação acima |

Só o executor sabe se a decisão pendente muda as próximas, e por isso a classificação é dele; o gate
declarado é o piso objetivo por baixo dela.

**Uma spec bloqueada sai da marca, não da PR.** Ela deixa o `quenching-slugs:` da branch, fica em
`plans/` com `[!]`, e o relatório final nomeia qual ficou de fora e por quê. A PR entrega o que já
ficou pronto e **nunca insinua que carrega o que não carrega** — que é a única forma de uma parada
no meio da fila continuar sendo um resultado, e não um prejuízo.

## Não há teto de N, e não há aviso

O plano de autorização mostra a **lista inteira e o N antes de qualquer isolamento**, e é sobre isso
que o humano decide. Um limiar que ninguém mediu acrescentaria a aparência de medição sem a medição;
se a revisão de uma PR grande saturar, o que muda é o número que o humano digita no próximo run, não
uma regra no corpo do comando.

## A volta recursiva e suas três formas

Um run pode absorver o trabalho que ele próprio revelar. A **única** fonte de absorção são specs
promovidas de `## Discoveries` — nada mais entra numa volta — e elas passam pelo mesmo contrato de
entrada da §acima.

| Forma | O que faz | Termina porque |
| --- | --- | --- |
| **sem recursão** | o que o run revelar fica em `plans/` para o próximo | não há volta |
| **uma geração** | absorve as specs promovidas nesta volta, e para | a segunda geração não é oferecida |
| **ponto fixo sem limite** | repete até uma volta não promover nada | o contrato de entrada filtra: `medium` ou acima exige `ready`/`approved`, e portanto **nunca entra sozinha numa volta** |

As três são **sempre apresentadas** no plano de autorização, junto com a forma escolhida e o
critério de limite do humano. Qual delas chega pré-marcada não está decidido: até que um run real
absorva uma spec promovida e diga se a segunda geração vale o tamanho que acrescenta à PR, o plano
pré-marca **sem recursão** e diz na tela que esse é o padrão provisório.

A terceira forma é a que pode não terminar se o trabalho gerar trabalho, e a garantia acima é o que
a limita: uma spec promovida que exija `ready`/`approved` sai da volta e espera um humano.

## O que esta forma deliberadamente não é

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
