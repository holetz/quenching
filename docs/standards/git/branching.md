---
type: standard
title: Fluxo de branches — develop integra, main publica
description: A main acumulava duas funções que este standard separa — develop como branch de integração onde as specs mergeiam, main como canal de publicação que só recebe o merge deliberado develop → main — o gatilho por demanda e sem cadência, a pergunta que empurra para o agrupamento quando develop carrega um só merge desde a última tag, a publicação sempre local, e os dois consumidores que leem os nomes das branches declarados em .claude/quenching.json
resource: .claude/quenching.json, plugins/quenching/assets/bin/specs.py, plugins/quenching/commands/specs/execute.md
tags: [git, branching, release, workflow, develop, main]
timestamp: 2026-08-04
audience: both
authority: current
source: spec plan/configurable-branch-strategy (task 1.1) — a main acumulava integração e publicação na mesma branch, sem que nada marcasse a segunda como um ato deliberado; hoje o gatilho é "todo merge" e não existe momento em que alguém decide publicar; §Adotando o fluxo num repositório já em andamento acrescentado pela revisão da própria branch ao concluir (2026-08-04), que notou que esta spec é o próprio caso de bootstrap que ela descreve
maintainer: quenching
---

# Fluxo de branches — develop integra, main publica

Este repositório usa duas branches de longa duração, cada uma com uma função só.

## As duas branches

| Branch | Função |
| --- | --- |
| `develop` | **Integra.** As branches `plan/<slug>` são cortadas dela e mergeiam nela. Várias specs se acumulam aqui sem que nada seja publicado. |
| `main` | **Publica.** Só recebe o merge `develop → main`, e é esse merge — nunca outro — que move o lockstep de versão ([versioning-release.md](../ci-cd/versioning-release.md)) e cria a tag. |

`main` continua sendo a branch default do repositório no GitHub — ver
[§O consumidor não muda nada](#o-consumidor-não-muda-nada) — e é por isso que quem já instalou o
plugin não precisa agir.

## O gatilho é a demanda, não a cadência

A release é um ato deliberado do mantenedor. Não há cadência, não há contador de merges, não há
janela de tempo. Antes deste standard o gatilho era "todo merge em `main`" — o que, na prática,
significava que não existia nenhum momento em que alguém decidisse publicar.

**A mitigação contra o hábito.** Nada no fluxo obriga a agrupar várias specs numa release: o
mantenedor é uma pessoa só, então o cenário em que cada spec vira uma release por hábito produz o
estado de hoje **mais** uma branch a manter, sem ganhar nada. Por isso, quando `develop` carrega **um
só merge** desde a última tag, o comando de release pergunta se aquilo é uma release ou é hábito —
sem contador, sem bloqueio, uma pergunta só, no único momento em que ela cabe.

## Onde o fluxo é declarado

| O quê | Onde | Consumidores |
| --- | --- | --- |
| Os nomes das duas branches | `.claude/quenching.json` (chaves `integrationBranch` e `releaseBranch`, degradando para `develop`/`main`) | o verbo de release, e a cadeia de inferência de `base` de uma spec não carimbada |
| A política em prosa | este documento | `/quenching:specs:execute` e `/quenching:specs:conclude`, como read-if-present |
| O bump de versão | [versioning-release.md](../ci-cd/versioning-release.md) | o verbo de release |

A cadeia de inferência de `base` — usada quando uma spec começa numa branch que ninguém carimbou —
consulta a branch de integração declarada antes de cair em `origin/HEAD` e em `main`, porque sem
isso uma spec não carimbada mergearia por padrão na branch de **publicação**. Ver
[plan-git-record.md](../workflows/plan-git-record.md).

## Adotando o fluxo num repositório já em andamento

O `branch.base` de uma spec é carimbado uma vez, no início do trabalho, e nunca re-inferido depois
— ver [plan-git-record.md](../workflows/plan-git-record.md). Uma spec cortada **antes** de
`integrationBranch` estar declarado carrega `base: main`, como toda spec anterior a este standard;
o `/quenching:specs:conclude` dela mergeia direto em `main`, exatamente como sempre mergeou. Só uma
spec cortada **depois** da declaração ganha `base: develop` automaticamente, pela cadeia de
inferência.

A própria spec que introduziu este standard, `plan/configurable-branch-strategy`, é o caso: sua
branch foi cortada com `base: main` porque `integrationBranch` ainda não existia quando o trabalho
começou. Recarimbar esse valor para `develop` depois do fato reescreveria um registro write-once
para caber numa regra que ainda não existia quando ele foi feito — por isso ele fica como está, e o
merge dela em `main` segue o registro, não o fluxo que ela mesma declara. Isso deixa `develop`
temporariamente atrás de `main`; trazer as duas de volta à paridade, e decidir quando rodar a
primeira release de verdade, é uma decisão humana — nenhum comando deste front a toma sozinho.

## A publicação, em duas metades

- **O que a release é** — patch, minor ou major; se vale publicar agora; o que muda para quem
  instala — é **julgamento humano**, conduzido por um comando dedicado. Esse julgamento não é
  automatizável: ver [versioning-release.md](../ci-cd/versioning-release.md) sobre por que uma
  política de versionamento fica fora de escopo.
- **Como a release é executada** — o lockstep dos sete artefatos e a tag, mecanicamente — é o verbo
  `specs.py release`. Sem string surgery, coberto por selftest.

## A publicação é sempre local

O merge `develop → main` nunca passa por pull request. A rota PR continua existindo — é a escolha
de cada spec ao concluir **na `develop`**, não da publicação. Um merge local para o ato de publicar
é o que permite ao mantenedor decidir "publico agora" sem depender de nenhuma revisão externa: a
revisão de cada spec já aconteceu ao entrar em `develop`.

## O consumidor não muda nada

Um marketplace aceita `ref` — branch, tag ou commit — e, na ausência dele, resolve pela branch
default do repositório. `main` continua sendo essa default e passa a receber só releases; quem já
instalou (com `ref` ou sem) passa a receber publicações em vez de todo merge, sem tocar em nada.
É essa propriedade que torna outras formas — mudar a branch default, ou exigir que o consumidor
fixe um `ref` — desnecessárias.
