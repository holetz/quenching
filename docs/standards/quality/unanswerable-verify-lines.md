---
type: standard
title: Unanswerable verify lines
description: Um `verify:` cujo veredito não vem do estado do código — o padrão que a shell desfigura antes de comparar, o escalar YAML que o parser trunca antes de ler, o ponto de entrada que saiu 0 sem executar nada — e a regra de exercitar a linha nos dois sentidos no momento em que ela é escrita, nunca no momento em que ela precisa fechar
resource: plugins/quenching/assets/references/specs-execute/execution.md, plugins/quenching/assets/references/specs-develop/*.md, docs/standards/workflows/task-execution.md
tags: [quality, verification, verify, authoring, shell-quoting, frontmatter]
timestamp: 2026-08-17
audience: both
authority: current
source: fila /quenching:specs:execute-queue de 2026-08-17 — três instâncias independentes medidas nas specs cq-specs-task-check-stale-subject-sem-commit, falha-de-leitura-do-backend-vira-front-vazio e validar-a-zona-generated-contra-o-disco
maintainer: quenching
---

# Unanswerable verify lines

<!-- rules -->

**Um `verify:` responde sobre o estado do código, ou não responde.** Uma linha cujo veredito é
decidido pela sua própria grafia — antes de qualquer coisa ser medida — não é um check frouxo: é um
check que não está lá. As duas leituras que ela produz são igualmente falsas, e uma delas é verde.

Três formas, todas medidas numa única fila de nove specs:

| A linha | O que a desfigura | Como ela mente |
| --- | --- | --- |
| grep cujo padrão contém crases, escrito entre **aspas duplas** | a shell faz substituição de comando antes do grep ver o padrão | o padrão degrada para algo que **nunca casa** — vermelho impossível de fechar |
| escalar YAML **não-aspado** contendo `#` | o parser trata o resto da linha como comentário | o valor chega truncado, e o finding só aparece depois do commit |
| ponto de entrada que não existe mais (módulo sem guarda `__main__`, `main()` aposentada) | nada — ele sai 0 | **verde sem executar nada** |

**A regra: exercite a linha nos dois sentidos no momento em que ela é escrita.** Rode-a contra a
árvore como ela está (deve dar o vermelho que a task existe para fechar) e contra o estado que a
task vai produzir (deve dar verde). Uma linha que dá o mesmo resultado nos dois sentidos não
discrimina, e o custo de descobrir isso na hora de fechar a caixa é uma execução inteira.

**Quem encontra uma linha assim reporta, e nunca a substitui em silêncio.** Rodar a forma corrigida
para saber o que ela diria é legítimo e é o que produz a evidência; reescrever a linha `verify:`
para que ela passe apaga a asserção que alguém pretendeu fazer. As duas coisas vão no relatório —
o que a linha declarava, e o que a forma correta mediu.

<!-- rationale -->

As três instâncias apareceram em specs diferentes, escritas por autores diferentes, na mesma run —
o que é a evidência de que a causa é a forma de escrever, não o descuido de um autor. Nenhuma foi
pega pelo `cq specs validate`, e nenhuma poderia ser: o validador lê a linha como texto, e o que
está errado nela só se manifesta quando a shell ou o parser YAML a interpretam. É por isso que a
mitigação é de **autoria**, e não mais um checker — o momento em que a informação existe é o
momento em que a linha é escrita.

A terceira forma é a mais cara das três, e a única que não dá trabalho a ninguém: um vermelho
impossível para o autor no mesmo dia, mas um verde vazio atravessa a run inteira, entra no PR e
sustenta uma afirmação de cobertura que nunca foi medida. Ela é irmã de
[selftest-mutation.md](selftest-mutation.md) — um teste que nunca foi observado falhando não está
testado — aplicada ao `verify:` de uma task em vez de a um caso de fixture.

O escopo é o `verify:` porque é ali que a linha é executada sem ninguém olhando. A mesma armadilha
de quoting num comando digitado à mão é vista e corrigida em segundos.
