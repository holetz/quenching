---
type: standard
title: Carregar é uma chamada dentro do passo; citar é prosa de preâmbulo
description: Um corpo que precisa de uma seção de reference no passo N carrega essa seção no passo N, com a invocação literal e copiável de cq components read — uma citação de preâmbulo diz onde a regra mora e não faz a sessão abrir o arquivo, e o oposto foi medido acontecendo nos oito corpos /quenching:specs:*
resource: plugins/quenching/commands/**/*.md
tags: [architecture, references, commands, skills, cq]
timestamp: 2026-08-10
audience: both
authority: current
source: spec plans/alinhar-specs-ao-report-mold.md, seção Design decisão 2 (provada em 2026-08-05) — antes das tasks 1.1-1.3 desta spec, sete dos oito corpos /quenching:specs:* citavam spec-driven.md §The report mold como prosa de preâmbulo ("owns the shape step N prints in") e nenhum dos oito continha a string --sections "§The report mold"; develop.md chegava a adiar explicitamente para o passo 8, e o passo 8 não trazia chamada nenhuma
maintainer: quenching
---

# Carregar é uma chamada dentro do passo; citar é prosa de preâmbulo

Todo corpo `commands/**/*.md` deste plugin cita references por `§`-endereço em vez de restatá-las —
essa é a economia de contexto que sustenta a arquitetura inteira. Mas uma citação e um carregamento
são dois atos diferentes, e confundi-los é como um corpo termina obedecendo a metade da própria regra
que ele mesmo declara.

## A regra

> Um corpo que precisa de uma seção de reference no passo N **carrega** essa seção no passo N, com a
> invocação literal e copiável:
>
> ```bash
> cq components read <arquivo> --sections "§X"
> ```
>
> Uma citação de preâmbulo — "a regra vive em `arquivo.md` §X" — diz **onde** a regra mora. Ela não
> faz a sessão abrir o arquivo.

Uma seção citada apenas em prosa é um endereço, não uma ação. Uma sessão que lê o corpo do comando de
ponta a ponta vê a frase, sabe que a regra existe em algum lugar, e segue adiante — o mesmo resultado
de um `import` nunca executado.

## A prova

Antes das tasks que este standard documenta, sete dos oito corpos `/quenching:specs:*` citavam
`spec-driven.md` §The report mold assim, no preâmbulo:

> "whose §The report mold owns the shape step 7 prints in"

e nenhum dos oito continha, em nenhum ponto do próprio corpo, a chamada
`cq components read ... --sections "§The report mold"`. `develop.md` ia além: adiava explicitamente para
o passo 8 ("step 8 loads spec-driven.md's §The report mold") — e o passo 8, quando lido, não trazia
chamada nenhuma, só a mesma frase de prosa.

O sintoma medido foi exatamente o que a citação sozinha permite: um report emitido em forma livre,
com blocos, verbos de fechamento e vocabulário de glifo que a seção citada já fixava — porque nada no
passo obrigava a sessão a abri-la antes de escrever.

A correção não foi reescrever a prosa do preâmbulo — ela já dizia a verdade sobre onde a regra mora,
e apagá-la perderia a explicação de por quê. A correção foi inserir, dentro de cada um dos oito
passos de report, a chamada que os dois corpos que já reportavam de forma consistente
(`/quenching:specs:continue` e `/quenching:specs:execute`, antes desta spec) já continham: a
invocação literal, no ponto exato em que o bloco carregado é usado.

## Onde a citação de preâmbulo continua certa

Uma reference citada no preâmbulo e **nunca carregada em nenhum passo** não é um defeito — é o caso
comum. A maior parte do que um corpo cita é contexto de fundo que orienta como a sessão pensa sobre o
comando, e restatá-lo dentro de um passo específico não teria destino: nada no passo consome aquele
bloco como instrução a seguir literalmente.

O carregamento dentro do passo é exigido quando, e só quando, o passo produz algo cuja **forma** vem
inteira de uma seção nomeada — um report, um bloco de frontmatter, um formato de commit. Nesses
casos a seção é o molde que o passo copia, e copiar um molde não visto nesta execução é copiar de
memória.

## Relação com standards vizinhos

- [report-mold.md](report-mold.md) é o caso que revelou esta regra: um mold citado por oito corpos,
  onde carregar dentro do passo — em vez de confiar na citação de preâmbulo — é o que faz a forma
  realmente convergir.
- [../automation/skills.md](../automation/skills.md) governa o outro lado da mesma
  balança: por que uma reference vive fora do preâmbulo em primeiro lugar, e o teto que um `§`-
  endereço evita estourar.
- [plugin-layout.md](plugin-layout.md) estabelece que `commands/**` é a única árvore registrada e
  `assets/` guarda o que é citado por caminho absoluto — esta regra é sobre o **quando** dentro do
  corpo, não sobre onde a reference mora.
