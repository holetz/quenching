---
type: standard
title: Aplicabilidade do remédio de um finding
description: Um remédio declarado nomeia uma ação que a superfície que emitiu o finding realmente oferece — o caso medido em que a mesma CLI recusava as duas ações que aconselhava, por que um remédio inaplicável ensina a ignorar o findings inteiro e não só aquele, e a recusa própria que um caso sem caminho ainda deve dar
resource: plugins/quenching/assets/bin/quenching/specs/commands/validate.py, plugins/quenching/assets/bin/quenching/specs/commands/doctor.py, plugins/quenching/assets/bin/quenching/components/commands/doctor.py, plugins/quenching/assets/bin/quenching/components/commands/lint.py, plugins/quenching/assets/bin/quenching/components/commands/registry.py, plugins/quenching/assets/bin/quenching/components/hooks.py
tags: [quality, findings, remedy, cli, surface]
timestamp: 2026-08-27
audience: both
authority: current
source: spec remover-secao-stray-de-um-documento (task 2.2) — o `sp-stray-heading` cujo remédio declarado aconselhava duas ações que a própria CLI que o emitia recusava com exit 2, medido em 2026-08-17; o segundo sítio da família — o remédio cuja conclusão a própria checagem não observa — acrescentado por sk-unscoped-bash-le-o-corpo (2026-08-27), medido sobre o `sk-unscoped-bash` que aconselhava declarar a razão no corpo lendo apenas `allowed-tools`
maintainer: quenching
---

# Aplicabilidade do remédio de um finding

**Um `remedy` nomeia uma ação que a superfície que emitiu o finding oferece.** Não uma descrição do
estado desejado, não um conselho editorial: um caminho que quem lê o finding consegue percorrer com
a mesma ferramenta que o imprimiu.

O teste é de uma linha: *qual comando fecha isto?* Se a resposta não existe, o remédio não está
escrito ainda.

## O caso medido

`cq specs validate` emitia, por anos, este par:

```
[warn ] plans/x.md: `## O que mudou` is not one of the fourteen canonical headings  (sp-stray-heading)
        remedy: rename it to a canonical heading or fold it into one
```

As duas ações aconselhadas eram impossíveis **pela CLI que as aconselhava**. `cmd_section` resolvia
todo heading pedido contra as catorze canônicas e saía 2 no primeiro que não casava — *antes* de
olhar para `--write` — então a seção stray não podia nem ser **nomeada**, muito menos renomeada ou
fundida. Não existia `--delete`, e `upsert_section` só alcançava uma seção que a resolução já
tivesse aceitado. Fechar o aviso exigia editar o documento por fora da ferramenta; sob um backend
externo, isso significa editar a issue à mão.

O custo não é o aviso. É que ele foi **permanente por construção**: nove documentos de `archive/`
carregavam o finding em 2026-08-17, e nenhum deles tinha caminho de saída.

## Por que a régua é essa, e não "o texto está correto"

Um remédio inaplicável não custa só o finding que ele acompanha. **Ele ensina a ignorar a saída
inteira.** Quem tenta seguir um conselho e descobre que a ferramenta o recusa aprende a ler o bloco
`remedy:` como decoração — e passa a pular também os quinze que eram aplicáveis. Um verificador vive
da confiança de que o que ele diz vale a pena fazer; um item que não vale gasta essa confiança para
todos os outros.

É também por isso que "elevar a severidade" nunca é a resposta primeiro. Enquanto não houvesse
caminho de conserto, subir `sp-stray-heading` de `warn` para `error` teria transformado um aviso
insolúvel numa falha insolúvel. **A pergunta sobre severidade só é respondível depois que a ação
existe.**

## Como escrever o remédio

- **Nomeie o verbo, com os argumentos deste caso.** `cq specs section <slug> --fold "<stray>"` é um
  remédio; "funda numa seção canônica" é um desejo. Onde os valores estão em mãos no ponto de
  emissão — o slug, o heading, a chave que falta — interpole-os: o leitor copia e cola.
- **Um remédio que é uma edição manual continua sendo um remédio**, desde que a edição seja
  descrita como ação (`fill it, or write \`- none — <reason>\``) e não como estado.
- **A ação pode recusar, e isso não quebra a regra — desde que a recusa se explique.** `--fold`
  recusa um stray sem nenhuma seção canônica acima dele, com mensagem própria (`sp-fold-no-anchor`),
  porque escolher um anfitrião ali seria inventar um dono para o texto. O leitor que segue o remédio
  recebe uma resposta da ferramenta, que é exatamente o que o remédio prometia. O que a regra proíbe
  é a ação que **não existe**, não a que existe e decide não agir.
- **Quando a ação não existe ainda, o remédio não é o lugar de fingir que existe.** Ou o finding
  ganha o comando que o fecha — que é trabalho de spec, não de redação — ou o texto diz honestamente
  que o conserto é manual e por quê.

## O segundo sítio: o remédio que a própria checagem não observa

O primeiro caso é a ação que **não existe**. O segundo é mais silencioso: a ação existe, quem lê
consegue percorrê-la — e a checagem que a aconselhou não olha para o resultado.

`sk-unscoped-bash` aconselhava, por construção, *"scope it to the commands the workflow runs, or
state the reason in the body"*, lendo apenas `allowed-tools`. A primeira metade fecha o finding: um
grant com escopo deixa de casar. A segunda **não muda um byte** — um corpo que já declarava a razão
recebia exatamente a mesma saída de um que ninguém tinha lido. Quem seguiu o conselho não tem como
saber que o seguiu.

A régua é a mesma de `## Por que a régua é essa`, aplicada um passo adiante: um remédio cuja
conclusão a checagem não observa gasta a mesma confiança que um remédio impossível, e gasta de um
jeito pior, porque quem o segue acredita ter terminado.

**O conserto não é apagar a metade não observável.** A razão declarada continua valendo — o que
faltava era torná-la observável, e isso pede uma forma que a checagem possa ver sem fingir que leu
prosa: uma linha literal, e um booleano no finding dizendo se ela está lá. `lint` passou a procurar
`**Why \`Bash\` is unrestricted here.**` fora de cerca e a carregar `priced` no JSON, e as duas
mensagens passaram a ser diferentes. O finding continua reportado nos dois casos, porque o grant é
o shell inteiro do turno de qualquer jeito.

**O que a forma literal compra, e o que ela deliberadamente não compra.** Ela dá ao remédio um fim
observável; ela não julga a razão. Um predicado que decidisse se a justificativa é *boa* estaria
inventando um veredito sobre prosa que só casou um padrão — a mesma desonestidade que
[parse-honesty.md](parse-honesty.md) recusa quando um parser falha e reporta lacuna de conteúdo.

**A pergunta que este sítio acrescenta ao teste de uma linha:** depois de *qual comando fecha isto?*,
vem *e a checagem enxerga que foi fechado?* Um remédio cuja resposta à segunda é não ainda não está
escrito — mesmo que a ação exista e alguém consiga executá-la.

## O gatilho de revisão

Todo finding novo nasce com essa pergunta respondida. Todo finding existente é reavaliado quando o
comando que o fecharia muda de forma: uma flag renomeada, um verbo retirado, uma recusa nova
adicionada antes do caminho que o remédio nomeia. É o mesmo fan-out de
[computed-fact-prose-fanout.md](computed-fact-prose-fanout.md) — a diferença é que aqui o fato
restatado é uma **capacidade**, e ela envelhece quando a superfície muda, não quando um valor muda.
