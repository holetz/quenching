---
type: standard
title: Retiring a standard — removal, the stamp, and the review as the net
description: Como um standard do bundle é aposentado — remoção, nunca deprecação (o verbo é `git rm`; um doc que sobrevive anotado vira ritual que ninguém age sobre); o herdeiro carrega o carimbo `retired with <doc> (<spec>, <data>)` no `source:` e no corpo; a varredura das citações é humana e o `## Impact` deve nomear a classe de docs que citam; a zona GENERATED da listagem é reconstruída no mesmo movimento; e o review de branch é a rede — com a atividade de recurso lida como figure, nunca como falha
resource: /.knowledge/**, /.specs/**
tags: [workflows, docs, bundle, retirement]
timestamp: 2026-08-27
audience: both
authority: background
source: extensible-surface-and-budget-retirement plan, executed at close-out — tasks 2.1–2.3 deleted context-budget.md and re-pointed its citations, the inheriting note in context-discipline.md, and the review that caught the strays (2026-08-06); the missing index row this procedure lists first was itself the one stray the review did not catch
maintainer: quenching
---

# Retiring a standard — removal, the stamp, and the review as the net

Aposentar um standard do bundle é **remoção, não deprecação**. Um doc que sobrevive anotado
(`deprecated:`, uma nota de rodapé, uma prosa "histórica") vira ritual que ninguém age sobre: o
leitor continua pagando o texto a cada sessão, sem ter como saber que a regra foi aposentada. O
verbo de aposentar é `git rm`; o que fica é o que o herdeiro registra (abaixo).

O procedimento abaixo foi executado uma vez nesta casa — `context-budget.md`, aposentado em
2026-08-06 pela spec `extensible-surface-and-budget-retirement` — e o erro que ele lista primeiro
é o stray que o próprio review daquela spec deixou passar. Não é uma prova de repetibilidade
(`authority: background`), é o registro do que aconteceu.

## O procedimento

1. **A spec que aposenta lista o que vai citar, e o `## Impact` nomeia a CLASSE dos docs que
   citam** — ver [withdrawn-contract-residue.md](../quality/withdrawn-contract-residue.md). O
   contrário foi medido: uma citação de um contrato removido não tem grafia canônica para grep,
   cada site a afirma com as próprias palavras. As citações que a spec conhece são re-apontadas
   como tarefas; as que ela não conhece são o que o review pega.
2. **A listagem é reconstruída no mesmo movimento.** O standard instalado entra na subpasta
   (`index.md` da casa) E na zona `GENERATED` de `standards/index.md` — os dois, no mesmo commit do
   `git rm`. Um doc cuja row falta na zona GENERATED é um `index-orphan` que **nenhum checker vê**
   (a figure de atividade só fala onde um `resource:` nomeia o arquivo, e nunca foi um achado —
   a zona não é validada por ninguém). Foi exatamente o que aconteceu na primeira execução: a subpasta foi atualizada, a
   zona não, e o review não pegou.
3. **O herdeiro carrega o carimbo.** A doc que herda o terreno do que saiu registra no `source:` e
   no corpo: `retired with <doc aposentado> (<spec>, <data>)`. É o único lugar onde a história do
   que sumiu continua viva — e é o que o leitor futuro consulta para saber o que aconteceu e por
   quê. Na primeira execução, `context-discipline.md` passou a fechar com "The measurement history
   behind the integral, 344-turn run included, retired with context-budget.md; this file owns what
   to *do* about it".
4. **A varredura dos strays é humana, e o review de branch é a rede.** Nenhum checker separa uma
   citação que fala SOBRE a doc aposentada (correta como está, história) de uma que a invoca como
   regra viva — o mesmo julgamento menção/uso que [prose-sweeps.md](../quality/prose-sweeps.md)
   declara invisível a regex. A atividade de recurso do herdeiro é uma figure, nunca um achado e
   muito menos uma falha do gate; quem aposenta assume que o review do concluir vai achar um ou
   dois sites órfãos — na
   primeira execução foram quatro (glossário ×2, um payload instalado, o corpo de um comando).

## O que a aposentadoria não é

- **Não é bump de versão.** O lockstep dos seis artefatos é ato do release
  ([versioning-release.md](../ci-cd/versioning-release.md) — o bump acontece na branch primária,
  no release, nunca no concluir e nunca como tarefa). Aposentar um standard não toca no
  VERSION.
- **Não é a mesma coisa de retirar um arquivo reservado.** O artefato reservado aposentado
  **mantém** o slot em `RESERVED` e o skip no hard block
  ([retiring-a-reserved-artifact.md](../architecture/retiring-a-reserved-artifact.md)) — porque
  desreservar silenciosamente converte cada arquivo sobrevivente em malformado. Um standard do
  bundle não tem consumidores que precisem ser desarmados; ele simplesmente deixa de existir.
- **Não é reescrita de história.** A doc aposentada continua no git; o que o repo ganha é o leitor
  que não paga mais o texto. Re-escrever o passado (amend, force-push) é proibido por razões
  independentes — a remoção é um commit ordinário como qualquer outro.
