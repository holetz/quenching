---
type: standard
title: Um `verify:` que faz grep de prosa fixa a redação que afirma
description: Um check escrito como grep sobre prosa não prova a prosa — ele a prende à frase que o check nomeou, e a falha resultante é ambígua entre "o texto está errado" e "o check nomeou uma frase que ninguém acordou"; como escrever a asserção, como ler a falha, a terceira leitura que nunca é permitida, e a face negativa em que o check proíbe uma string que o próprio spec exige em outro lugar
resource: plugins/quenching/commands/**, plugins/quenching/assets/references/**
tags: [quality, verification, prose, specs, verify]
timestamp: 2026-08-27
audience: both
authority: current
source: spec observacoes-do-triage-sem-portador-de-acao (distilada no conclude) — medido na task 3.1, cujo `verify:` exigia "qualquer coluna que nomeie um comando" em minúsculas e falhou porque o bullet efetivamente escrito abria com "Qualquer"; §A face negativa acrescentada pela spec 1003 (2026-08-27), que mediu o inverso três vezes na mesma branch — um `verify:` proibindo a string `mkdocs` em três arquivos onde a própria `## Proposal` exigia que ela aparecesse
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

## A face negativa: o check que proíbe uma string

A forma inversa — `! grep -q "<palavra>" <arquivo>` — parece mais segura, porque não escolhe
palavras: ela só proíbe uma. **Ela prende mais, não menos.** Uma proibição vale sobre o arquivo
inteiro, então ela alcança todo uso legítimo da palavra que a própria spec exige em outro lugar, e
o autor descobre isso só quando o check fecha a porta na frente do texto certo.

Três medições na mesma branch (spec 1003), todas com a string `mkdocs`:

| Onde | O uso legítimo que o check proibia |
| --- | --- |
| o corpo de um comando | a spec exigia, num bullet da `## Proposal`, que o comando reconhecesse a configuração legada — o que só se escreve nomeando-a |
| o README do plugin | o changelog de versões registra o que a 0.9.0 de fato entregou; reescrever isso falsificaria o registro |
| o espelho traduzido | é tradução literal da fonte, então herda tanto o tratamento do legado quanto o changelog |

O modo de falha é o mesmo nos três: **o alvo do check é o arquivo, e o alvo da regra era o
mecanismo.** O que tinha de sumir não era a palavra — era o comando que ninguém pode mais rodar, a
flag que não existe, o plugin que não roda. Escrito assim, o check volta a afirmar comportamento:

```bash
# proíbe o mecanismo morto, não a palavra
! grep -qE "mkdocs build|--site-dir|awesome-pages" <arquivo>
# e, quando o arquivo tem uma metade histórica, varre só a metade viva
! awk '/^- \*\*[0-9]+\.[0-9]+\.[0-9]+:/{exit} {print}' README.md | grep -qi mkdocs
```

**Duas regras que caem daqui.** Uma proibição sobre um arquivo que contém histórico precisa
delimitar a parte viva, porque histórico não se corrige — se reescreve, e reescrevê-lo é mentir.
E uma proibição sobre um artefato **gerado** nunca é o check certo: o que se afirma dele é que ele
está em dia com a fonte, não o que o tradutor por acaso produziu.

A terceira leitura continua proibida aqui: nada disso autoriza afrouxar a proibição para o texto
que por acaso existe passar. O que autoriza a troca é a proibição **contradizer uma exigência
escrita da própria spec** — e a troca então é declarada, com a razão registrada onde o revisor a
encontre.

## Relação com standards vizinhos

- [self-matching-guards.md](self-matching-guards.md) — o caso em que o próprio checker casa com o
  texto que ele proíbe. Aqui é o inverso: o check **não** casa com um texto que está certo.
- [prose-sweeps.md](prose-sweeps.md) — uma substituição mecânica corrompe justamente as frases que
  *falam sobre* a forma substituída. As três dizem o mesmo de ângulos diferentes: prosa não é alvo
  mecânico estável.
