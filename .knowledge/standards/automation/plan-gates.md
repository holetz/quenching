---
type: standard
title: Quando o gate de plano de um comando pode cair
description: As duas classes protegidas — item acoplado a código, ação irreversível de ciclo — são o teste inteiro, e um comando em que nenhuma delas ocorre não tem o que confirmar; o que substitui a janela de aprovação quando o gate sai (a URL do registro, anunciada antes de qualquer leitura e repetida no relatório), a diferença entre a confirmação que cai e a consolidação que fica, o que continua parando o passe de qualquer forma, as três formas intermediárias medidas e rejeitadas, e as três condições sob as quais a autoridade de uma marcha substitui a pessoa no go/no-go
resource: plugins/quenching/commands/**, plugins/quenching/assets/references/align/convergence.md, plugins/quenching/assets/references/specs-develop/questions.md
tags: [automation, commands, gates, confirmation, cost, turns]
timestamp: 2026-08-16
audience: both
authority: background
source: spec revisar-fluxo-do-develop-custo-e-gates, destilada no seu conclude (2026-08-16); §Quando a autoridade substitui a pessoa acrescentada em 2026-08-22 pela reforma que fez a marcha (`priority.complexity`) governar o interior de `/quenching:specs:develop` — sob a marcha `low` o passe carimba `approved` por conta própria, com `by: low-gear` no registro, e essa é a primeira vez que um go/no-go sai do passe neste repositório; a medição pós-merge segue devendo, agora para as duas mudanças — o critério e as três alternativas rejeitadas vêm do `## Design` e do `## Alternatives Considered` dela, e a aplicação medida é `/quenching:specs:develop`, o primeiro comando a rodar sem gate de plano; a afirmação de custo que a motivou (<= 4M para trabalho equivalente a uma linha de base de 9,73M em 100 turnos) segue **sem medição pós-merge**, e é ela a condição de graduação
maintainer: quenching
---

# Quando o gate de plano de um comando pode cair

Um **gate de plano** é a parada em que um comando apresenta o que vai escrever e espera um OK. Ele
custa um par de turnos por unidade de trabalho, e cada turno re-envia a conversa inteira
([context-discipline.md](context-discipline.md) §Emit fewer turns per unit of work). Este documento
é o teste que decide se essa parada está comprando alguma coisa.

## O critério

<!-- rules -->

> Um gate de plano protege exatamente duas classes: **um item acoplado a código** e **uma ação
> irreversível de ciclo**. Um comando em que nenhuma das duas ocorre **não tem o que confirmar**, e
> o gate dele é custo sem contraparte.

As duas classes são as mesmas que
[`align/convergence.md`](/plugins/quenching/assets/references/align/convergence.md)
§The cycle-authorization contract já protege — este critério não inventa uma terceira, e um comando
não sai do gate por ser barato, curto ou "de baixo risco". Ele sai por não conter nenhuma das duas.

**A confirmação cai; a consolidação fica.** São coisas diferentes e só a primeira é o gate. Um
comando que acumulava e escrevia uma vez continua acumulando e escrevendo uma vez — o que sai é a
espera, nunca a apresentação. Um plano narrado por inteiro e aplicado é revisável; seis edições
espalhadas não são, com gate ou sem.

**O que ainda para o passe para depois do gate cair:**

- as perguntas que o próprio trabalho faz — um `AskUserQuestion` cuja resposta muda o que se
  escreve não é um gate de plano e não sai com ele;
- qualquer go/no-go que seja a **única origem** de um registro de julgamento humano — a menos que o
  registro grave **de quem** é a autoridade que o carimbou (§Quando a autoridade substitui a
  pessoa).

<!-- rationale -->

O gate existe para dar ao humano a chance de barrar uma escrita que ele não pode desfazer, ou que
sai do escopo do comando e entra no do repositório. Onde nada disso é possível, a parada não está
protegendo — está cobrando um par de turnos por banco para reobter uma autorização que a invocação
já deu.

## A janela de acompanhamento substitui a janela de aprovação

<!-- rules -->

Removida a parada, o humano deixa de ter um ponto de intervenção **dentro** do passe. O
substituto é o **registro externo em que o trabalho aparece** — uma issue, um work item, um
arquivo — e o comando tem duas obrigações por causa disso:

- **anunciar a URL do registro antes de qualquer leitura**, para que a janela esteja aberta enquanto
  o passe corre, e não depois;
- **repeti-la no relatório**, porque um passe que escreveu sem gate termina apontando para o único
  lugar em que aquela escrita pode ser lida e corrigida.

A URL sai de um dado que o comando já busca. Um comando que precisaria de **uma chamada a mais** para
obtê-la não ganhou esta troca: ele gastou em ferramenta o que economizou em turno.

<!-- rationale -->

A ideia de que a revisão desapareceu é o erro que este par de obrigações evita. Ela mudou de
momento: era síncrona e bloqueante, passa a ser assíncrona e sobre o resultado — e uma revisão
assíncrona sobre um endereço que ninguém recebeu é que seria uma revisão que não existe.

## Quando a autoridade substitui a pessoa

<!-- rules -->

Um go/no-go pode sair do passe — e só sob as três condições, juntas:

1. **O humano declarou o modo antes.** O nível está no disco (`priority.complexity`), foi escrito
   por `triage`, `create` ou `develop` com a escala na frente de alguém, e é ele — não o comando —
   que dispensa a parada. A autorização é do **modo**, nunca daquela spec.
2. **O registro grava a procedência.** `approved: {date, by}` — `by: human` quando uma pessoa
   respondeu, `by: low-gear` quando o nível autorizou o modo e o passe carimbou. Um registro que não
   diz de quem é a palavra não distingue as duas coisas, e é aí que a dispensa deixa de ser
   delegação e vira falsificação.
3. **A janela de acompanhamento vale em dobro.** A URL do registro é anunciada antes de qualquer
   leitura e repetida no relatório, e o relatório **nomeia** o carimbo automático em linha própria.
   Um carimbo que ninguém pediu e que o relatório não conta é indistinguível de um inventado.

Faltando qualquer uma das três, a parada fica.

<!-- rationale -->

O critério de §O critério não mudou: as duas classes protegidas continuam as mesmas, e `approved`
nunca foi nenhuma delas — ele era a terceira coisa que parava o passe, e parava por ser a **única
origem** de um fato. O que a procedência muda é justamente isso: passa a haver duas origens
declaradas e distinguíveis, e quem lê o registro escolhe em qual confia. Sem o campo, dispensar o
go/no-go apagaria o fato; com ele, a dispensa é uma segunda entrada no mesmo livro, e a revisão
continua existindo — assíncrona, sobre o resultado, no endereço que o passe anunciou duas vezes.

## Três formas intermediárias, medidas e rejeitadas

<!-- rationale -->

Todas as três preservam alguma parada. Nenhuma sobreviveu ao mesmo teste:

| Forma | Por que perdeu |
| --- | --- |
| **Autorização de passe** — um OK na abertura autoriza o passe inteiro, o plano segue narrado antes de cada escrita | cobra uma parada que não protege nada: se nenhuma das duas classes ocorre no passe, ela também não ocorre na abertura dele |
| **Confirmação por exceção** — o OK sobrevive só quando o edit sobrescreve ou contradiz conteúdo já presente | acrescenta uma regra de classificação que todo banco passa a aplicar — mais doutrina para resolver um excesso de doutrina, e a classificação é julgamento, não teste |
| **Cortar só a travessia entre etapas, preservando o gate de cada uma** | corta ~1 parada por passe e não entrega o modelo: a confirmação por etapa é justamente a parada que o problema nomeia |

O padrão das três é o mesmo: elas negociam *quantas* paradas, quando a pergunta é se **aquela**
parada protege alguma coisa. Uma parada que não protege não fica melhor por ser rara.

## Por que isto nasce `background`

<!-- rationale -->

O critério está argumentado e foi aplicado com resultado consistente a quatro comandos — um perdeu o
gate, três o mantiveram por conterem as classes protegidas. O que **não** foi medido é a afirmação de
custo que motivou tudo: que o passe sem gate custa uma fração do que custava. Enquanto essa medição
não existir, o que está provado é que o gate não protegia — não que removê-lo comprou o que se
esperava. A graduação para `current` é essa medição.
