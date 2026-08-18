---
type: standard
title: Quando o gate de plano de um comando pode cair
description: As duas classes protegidas — item acoplado a código, ação irreversível de ciclo — são o teste inteiro, e um comando em que nenhuma delas ocorre não tem o que confirmar; o que substitui a janela de aprovação quando o gate sai (a URL do registro, anunciada antes de qualquer leitura e repetida no relatório), a diferença entre a confirmação que cai e a consolidação que fica, o que continua parando o passe de qualquer forma, as três formas intermediárias medidas e rejeitadas, e a quarta que sobreviveu — o gate consolidado, para quando as classes protegidas ocorrem uma vez por passe e não uma por etapa
resource: plugins/quenching/commands/**, plugins/quenching/assets/references/align/convergence.md, plugins/quenching/assets/references/specs-develop/questions.md
tags: [automation, commands, gates, confirmation, cost, turns]
timestamp: 2026-08-18
audience: both
authority: background
source: spec revisar-fluxo-do-develop-custo-e-gates, destilada no seu conclude (2026-08-16) — o critério e as três alternativas rejeitadas vêm do `## Design` e do `## Alternatives Considered` dela, e a aplicação medida é `/quenching:specs:develop`, o primeiro comando a rodar sem gate de plano; a afirmação de custo que a motivou (<= 4M para trabalho equivalente a uma linha de base de 9,73M em 100 turnos) segue **sem medição pós-merge**, e é ela a condição de graduação; a quarta forma — o gate consolidado — vem da sessão `c5ffb0aa` (2026-08-18), um `/quenching:specs:conclude` medido de ponta a ponta por `cq components session`, onde as 5 paradas custaram 12h52m de espera contra 21m30s de máquina e 5 das 6 perguntas apenas ratificaram a recomendação, e cuja própria afirmação de custo segue sem medição pós-merge
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
- qualquer go/no-go que seja a **única origem** de um registro de julgamento humano.

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

## Uma quarta forma: o gate consolidado, quando as classes ocorrem uma vez por passe

<!-- rules -->

As três acima negociam *quantas* paradas sem responder se aquela parada protege. Há um caso em que a
contagem é a resposta certa, e ele tem teste próprio:

> Quando as duas classes protegidas ocorrem **uma vez por passe** — e não uma vez por etapa — o
> comando deve **um** gate, não um por etapa. As etapas seguintes apresentam e escrevem o que esse
> gate já decidiu.

O teste é a **evidência**, nunca a etapa: se tudo o que as etapas decidem já está em mãos quando a
primeira delas pergunta, as perguntas seguintes não colhem julgamento novo — recobram o mesmo
julgamento em parcelas. Um gate por etapa ali não protege N vezes; protege uma e cobra N.

O caso aplicado é `/quenching:specs:conclude`. As duas classes ocorrem nele — o passe edita código
de produto (as correções da revisão) e executa uma ação irreversível de ciclo (arquivar e destilar),
então o gate **não** cai como caiu no `/quenching:specs:develop` — mas ambas ficam decididas assim
que o diff da branch foi lido. As quatro confirmações que ele cobrava viraram **uma tela**, sob
[`specs-develop/questions.md`](/plugins/quenching/assets/references/specs-develop/questions.md)
§1, com as escritas ainda na ordem que o corpo declara.

**Não é nenhuma das três acima.** Não é a *autorização de passe*, que pede o OK na abertura sobre
trabalho que ninguém viu: esta tela vem depois da leitura e carrega os itens concretos, então ela
protege exatamente o que as quatro protegiam. Não é *cortar só a travessia*, que preserva o gate de
cada etapa e corta ~1 parada: esta remove o gate de cada etapa e mantém um do passe.

**O limite.** Duas perguntas cujas respostas podem mudar uma à outra continuam separadas — a regra é
de `questions.md` §1 e não se negocia contra contagem de turnos. Consolidar só é legítimo depois de
tornar as perguntas independentes; onde isso não é possível, elas não viajam juntas. E o item que o
humano riscar da tela precisa reaparecer no relatório: uma tela consolidada que descarta calado
perde o que quatro separadas não perdiam.

<!-- rationale -->

Medido na sessão `c5ffb0aa` — um `/quenching:specs:conclude` inteiro, contagens exatas por
`cq components session` com `attributedRun.closed: true`: **97 tool calls, 5 paradas**, e o humano
ratificou a recomendação em **5 das 6** perguntas. **21m30s de trabalho de máquina contra 12h52m de
espera humana**; descontada a parada que caiu de madrugada, 40% do tempo decorrido foi esperando um
humano digitar. Zero interrupções, zero correções manuais, zero leituras repetidas — o custo era
inteiramente as paradas, e não um defeito que uma delas estivesse pegando.

A afirmação de custo segue **sem medição pós-merge**, como a do critério acima e pela mesma razão: o
que está argumentado é que quatro gates protegiam o que um protege — não que a consolidação comprou
o que se espera dela. A próxima run do comando, medida pelo mesmo instrumento, é essa medição.

## Por que isto nasce `background`

<!-- rationale -->

O critério está argumentado e foi aplicado com resultado consistente a quatro comandos — um perdeu o
gate, três o mantiveram por conterem as classes protegidas. O que **não** foi medido é a afirmação de
custo que motivou tudo: que o passe sem gate custa uma fração do que custava. Enquanto essa medição
não existir, o que está provado é que o gate não protegia — não que removê-lo comprou o que se
esperava. A graduação para `current` é essa medição.
