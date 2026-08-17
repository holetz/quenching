---
type: standard
title: Fluxo de branches — PR na primária, release deliberado
description: Uma branch única de longa duração — a primária (main) — onde todo PR mergeia e a revisão vive, o release como ato deliberado local que bumpe, tageia e publica o que a primária acumulou, o gatilho por demanda e sem cadência, a pergunta que empurra para o agrupamento quando a primária carrega um só PR desde a última tag, e a transição para quem vinha do fluxo de duas branches
resource: .claude/commands/release.md, plugins/quenching/assets/bin/quenching/git/**, plugins/quenching/assets/bin/quenching/specs/**, plugins/quenching/commands/specs/execute.md, plugins/quenching/commands/specs/cycle.md, plugins/quenching/assets/references/align/convergence.md
tags: [git, branching, release, workflow, main]
timestamp: 2026-08-17
audience: both
authority: current
source: reescrito pelo spec eliminar-branch-de-integracao (2026-08-17) — o fluxo de duas branches (develop integra, main publica) deixou de existir: a primária recebe todo PR e o release é o ato deliberado local que a publica; a transição para quem vinha do fluxo antigo acrescentada na mesma reescrita
maintainer: quenching
---

# Fluxo de branches — PR na primária, release deliberado

Este repositório publica a partir de **uma** branch de longa duração. Não há branch de integração
separada: todo trabalho entra por pull request e o release é o único ato que publica.

## A branch única

| Branch | Função |
| --- | --- |
| `main` | **Publica.** É a branch default do repositório e onde todo PR mergeia. O release é o único ato que move o lockstep de versão ([versioning-release.md](../ci-cd/versioning-release.md)) e cria a tag. |

A branch primária não é configurada — resolve-se pela cadeia `origin/HEAD → init.defaultBranch →
main` ([plan-git-record.md](../workflows/plan-git-record.md)).

## O PR é a rota de entrada

Todo trabalho entra em `main` por pull request: o ciclo de specs (`/quenching:specs:cycle`,
`/quenching:specs:execute`, `/quenching:specs:execute-queue`) abre o PR contra a branch primária e
a revisão humana vive no PR. Não há merge local de specs — a revisão de cada mudança acontece
antes de entrar, não depois.

## O gatilho é a demanda, não a cadência

A release é um ato deliberado do mantenedor. Não há cadência, não há contador de merges, não há
janela de tempo — o gatilho é "decidi publicar", nunca "passou tempo" nem "mergeou".

**A mitigação contra o hábito.** Nada no fluxo obriga a agrupar várias specs numa release: o
mantenedor é uma pessoa só, então o cenário em que cada spec vira uma release por hábito custa uma
release por spec sem ganhar nada. Por isso, quando a primária carrega **um só PR** desde a última
tag, o comando de release pergunta se aquilo é uma release ou é hábito — sem contador, sem
bloqueio, uma pergunta só, no único momento em que ela cabe.

## Onde o fluxo é declarado

| O quê | Onde | Consumidores |
| --- | --- | --- |
| A política em prosa | este documento | `/quenching:specs:execute` e `/quenching:specs:conclude`, como read-if-present |
| O bump de versão | [versioning-release.md](../ci-cd/versioning-release.md) | o verbo de release |
| A cadeia de inferência de `base` | [plan-git-record.md](../workflows/plan-git-record.md) | a spec não carimbada |

A cadeia de inferência de `base` — usada quando uma spec começa numa branch que ninguém carimbou —
resolve `origin/HEAD → init.defaultBranch → main`, a branch primária, que é onde o trabalho
pertence.

## Adotando o fluxo num repositório que tinha develop

Um repositório que vinha do fluxo de duas branches (develop integra, main publica) tem um
acumulado em `develop` que `main` ainda não recebeu. A transição é **um ato do mantenedor**: um
último PR `develop → main` publica o acumulado de uma vez, e a partir dele develop vira órfã e o
fluxo de uma branch rege. O release novo (sem merge `develop → main`) não publica esse acumulado —
a transição usa a própria rota que o novo fluxo adota, o PR.

O `branch.base` de uma spec é carimbado uma vez, no início do trabalho, e nunca re-inferido depois
— ver [plan-git-record.md](../workflows/plan-git-record.md). Uma spec em flight com `base: develop`
segue o registro write-once até concluir; só as specs cortadas depois da transição nascem com a
primária como base.

## A publicação, em duas metades

- **O que a release é** — patch, minor ou major; se vale publicar agora; o que muda para quem
  instala — é **julgamento humano**, conduzido por um comando dedicado. Esse julgamento não é
  automatizável: ver [versioning-release.md](../ci-cd/versioning-release.md) sobre por que uma
  política de versionamento fica fora de escopo.
- **Como a release é executada** — o lockstep dos artefatos e a tag, mecanicamente — é o verbo
  `cq specs release`. Sem string surgery, coberto pela suíte de testes.

## A publicação é sempre local

O bump, o commit e a tag acontecem na branch primária, sem PR de release. Um ato local permite ao
mantenedor decidir "publico agora" sem depender de nenhuma revisão externa: a revisão de cada spec
já aconteceu no PR de entrada, e o release só escolhe quando o acumulado vira versão.

## O consumidor não muda nada

Um marketplace aceita `ref` — branch, tag ou commit — e, na ausência dele, resolve pela branch
default do repositório. `main` é essa default e recebe tudo o que o repo publica; quem já instalou
(com `ref` ou sem) continua recebendo o que `main` carrega, sem tocar em nada.
