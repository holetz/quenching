---
type: standard
title: Um `verify:` que faz grep de prosa fixa a redação que afirma
description: Um check escrito como grep sobre prosa não prova a prosa — ele a prende à frase que o check nomeou, e a falha resultante é ambígua entre "o texto está errado" e "o check nomeou uma frase que ninguém acordou"; como escrever a asserção, como ler a falha, e a terceira leitura que nunca é permitida
resource: plugins/quenching/commands/**, plugins/quenching/assets/references/**
tags: [quality, verification, prose, specs, verify]
timestamp: 2026-08-15
audience: both
authority: current
source: spec observacoes-do-triage-sem-portador-de-acao (distilada no conclude) — medido na task 3.1, cujo `verify:` exigia "qualquer coluna que nomeie um comando" em minúsculas e falhou porque o bullet efetivamente escrito abria com "Qualquer"
maintainer: quenching
---

# Um `verify:` que faz grep de prosa fixa a redação que afirma

## A regra

> Um `verify:` que faz grep de prosa **não prova a prosa — prende-a à frase que o check nomeou.**
> Escreva a asserção sobre uma frase que a redação já decidiu, ou aceite que o check está
> escolhendo as palavras antes de quem escreve.

Um check sobre código afirma um **comportamento**: passa com qualquer implementação que se comporte
daquele jeito. Um check sobre prosa afirma uma **sequência de caracteres**, e prosa tem infinitas
sequências que dizem a mesma coisa. Na linha `verify:` os dois se parecem, e não são a mesma coisa.

## Como ler a falha

Uma falha aqui é **ambígua por construção**, e as duas leituras honestas pedem ações opostas:

| O que está errado | Como se reconhece | O que fazer |
| --- | --- | --- |
| o texto | a frase exigida é a que o autor de fato quis dizer, e o texto não a contém | mudar o texto |
| o check | a frase exigida nunca foi acordada — maiúscula de início de frase, um sinônimo, outra ordem | é defeito de definição: `/quenching:specs:develop` conserta o `verify:` |

A **terceira leitura nunca é permitida**: reescrever o check para casar com o que o texto por acaso
diz. É a proibição que `/quenching:specs:execute` já carrega — nunca editar a asserção para ela
parar de falhar — aplicada ao caso em que a asserção é uma string.

## Como escrever a asserção

- **Nomeie uma frase que a redação já decidiu**, nunca uma que ela ainda vai escolher. O momento de
  escrever esse `verify:` é depois de o texto existir; antes disso ele é um palpite sobre palavras.
- **Prefira o miolo da frase à borda.** Um trecho que pode abrir um bullet vai ser capitalizado por
  quem escreve, e a maiúscula é exatamente a diferença que derruba um `grep` sem `-i`.
- **Afirme o termo, não a sentença.** Quanto menor o trecho exigido, menos redação o check prende —
  e o termo é justamente a parte que não deveria variar.
- **Prove que o check sabe falhar** antes de escrever o texto que o faz passar: rodá-lo contra a
  árvore antes da correção e exigir saída não-zero é o que separa um check de um enfeite.

## Relação com standards vizinhos

- [self-matching-guards.md](self-matching-guards.md) — o caso em que o próprio checker casa com o
  texto que ele proíbe. Aqui é o inverso: o check **não** casa com um texto que está certo.
- [prose-sweeps.md](prose-sweeps.md) — uma substituição mecânica corrompe justamente as frases que
  *falam sobre* a forma substituída. As três dizem o mesmo de ângulos diferentes: prosa não é alvo
  mecânico estável.
