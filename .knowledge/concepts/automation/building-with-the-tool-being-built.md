---
type: concept
title: Building with the tool being built
description: Neste repositório a ferramenta que registra o progresso de uma task é a mesma que a task edita, então uma edição no meio do caminho pode deixar o próprio `cq` inexecutável e a caixa impossível de marcar — o que torna certas tasks inseparáveis e obriga a capturar antes de editar tudo que o passo seguinte vai precisar ler
resource: plugins/quenching/assets/bin/**, plugins/quenching/assets/references/specs-execute/execution.md
tags: [automation, self-hosting, bootstrapping, specs, execution]
timestamp: 2026-08-17
audience: both
authority: current
source: fila /quenching:specs:execute-queue de 2026-08-17 — specs remover-secao-stray-de-um-documento (import de fold_stray_heading) e squash-de-secao-deve-resetar-para-um-sha (o squash consertado pela spec que o usou)
maintainer: quenching
---

# Building with the tool being built

O `cq` marca a caixa, estampa o registro e executa o squash de seção. O `cq` é também, com
frequência, **o que a task está editando**. Enquanto essas duas frases forem verdadeiras ao mesmo
tempo, o procedimento de execução tem um estado intermediário em que ele não consegue registrar o
próprio progresso.

## As duas formas que isso toma

**A janela quebrada.** Uma task adiciona a um módulo o import de uma função que a task *seguinte*
vai escrever. Entre um commit e outro, todo `cq specs` falha no import — inclusive o `cq specs task
--check` que fecharia a primeira caixa. As duas tasks não são duas: são uma, e declarar `files:`
separados não as separa. Medido quando `granular.py` passou a importar `fold_stray_heading` antes
de `parse/edit.py` existir.

**O chão que se move.** Uma task conserta o mecanismo que ela própria usa para commitar. O squash
de seção resolvia a base por ref; a spec que trocou isso por um sha capturado e verificado como
ancestral precisou capturar o sha da base **antes de qualquer edição**, porque depois da primeira
edição o mecanismo em uso já não era o mesmo que estava sendo descrito.

## O que isso obriga

- **Capture antes de editar** tudo que um passo posterior vai precisar ler: o sha da base, a saída
  de referência, o comportamento anterior. Depois da edição, a fonte pode já não responder o que
  respondia.
- **Trate uma janela quebrada como uma task só.** Se o estado intermediário deixa o `cq`
  inexecutável, a fronteira entre as duas tasks não existe na prática — e o `## Impact` deveria
  dizer isso, em vez de a execução descobrir.
- **Prove a mudança contra uma cópia do código anterior**, não contra a memória do que ele fazia:
  carregar a implementação pré-mudança de `git show <base>:<caminho>` num módulo à parte e comparar
  as duas saídas é o que separa "equivalente" de "parece equivalente".

A propriedade compensadora é que o conserto se prova sozinho na mesma run: a spec que corrigiu o
squash rodou os três squashes dela sob a regra nova, com o `merge-base --is-ancestor` verificado nos
três e zero remoções em cada commit de seção — que é exatamente a propriedade que ela existia para
garantir.
