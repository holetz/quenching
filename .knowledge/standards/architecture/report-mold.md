---
type: standard
title: O report de uma frente é um mold, possuído uma vez
description: A forma em que os comandos de uma frente imprimem seu relatório pertence a UMA seção citada por todos — três bandas fixas, um conjunto ordenado de colunas do qual cada comando toma um subconjunto, e toda coluna que nomeie um comando executável como impressa — porque um formato reescrito em oito corpos envelhece em sete e nenhum checker vê
resource: plugins/quenching/assets/references/specs-develop/spec-driven.md, plugins/quenching/commands/specs/*.md
tags: [architecture, commands, report, output, references, specs]
timestamp: 2026-08-15
audience: both
authority: current
source: branch holetz/specs-report (2026-08-04) — medido sobre os oito corpos /quenching:specs:* antes e depois; a divergência com commands/knowledge/status.md §4 está registrada abaixo e foi deliberadamente não corrigida
maintainer: quenching
---

# O report de uma frente é um mold, possuído uma vez

Uma frente tem vários comandos e **um** leitor. O que ele vê no fim de cada execução é o produto
mais visível da frente inteira, e é a única parte que nenhum validador inspeciona.

## A regra

> A forma em que os comandos de uma frente imprimem seu relatório pertence a **uma** seção que todos
> citam. Cada corpo declara apenas o seu delta: quais blocos do corpo, fixos ou opcionais; quais
> colunas; quais candidatos a próximo passo e sob que condição.

para a frente `specs` essa seção é
[/plugins/quenching/assets/references/specs-develop/spec-driven.md](/plugins/quenching/assets/references/specs-develop/spec-driven.md)
§The report mold, citada pelos oito comandos `/quenching:specs:*`.

O mold é **literal**: ele carrega o bloco renderizado que o corpo copia e substitui, não uma
descrição do que o bloco deveria conter. Essa escolha não é estética — os dois únicos comandos que
já tinham saída consistente antes deste trabalho (`/quenching:specs:continue` e
`/quenching:specs:execute`) eram exatamente os dois que carregavam um bloco literal, e os seis que
descreviam o report em prosa produziram seis formas diferentes.

### O que o mold fixa

- **Três bandas, nesta ordem, sempre:** cabeçalho · corpo · próximo passo.
- **Fixo versus opcional é declarado, não improvisado.** Um bloco fixo sem conteúdo imprime seu
  título e `—`; um bloco opcional sem conteúdo é omitido inteiro. Um bloco fixo que some quando
  vazio é indistinguível de uma passagem que o deixou cair; um opcional impresso vazio é ruído em
  toda execução.
- **Um conjunto ordenado de colunas**, do qual cada comando toma um subconjunto — nunca reordenando,
  nunca inventando. Cada coluna declara a **fonte** de onde sai e quando vale `—`.
- **Um molde com coluna de código só serve saída cujo código um contrato define.** Afrouxar essa
  coluna para acomodar uma saída que não tem código tira dos demais citadores a garantia que faz o
  molde valer. Saída sem código pede molde próprio — outra sub-seção da mesma seção — nunca um
  código inventado nem uma coluna relaxada.
- **Executável como impresso vale para qualquer coluna que nomeie um comando** — o argumento real
  substituído; um `<slug>` literal na saída é defeito, e um nome de comando sem o argumento que ele
  exige também. A regra nasceu no bloco de próximo passo e vale igual em toda coluna que aponte o
  leitor para um comando: uma ação que o leitor tem de completar não é uma ação, é um lembrete.
- **Um bloco de próximo passo por último**, sob a regra acima. Exatamente uma linha recomendada, e a
  cauda de motivo só quando há mais de uma linha.

## Por que uma seção, e não prosa em cada corpo

Um formato de saída é um fato que o corpo do comando *reescreve*. É o fan-out que
[../quality/computed-fact-prose-fanout.md](../quality/computed-fact-prose-fanout.md) descreve:
muda no primeiro corpo, envelhece nos outros sete, e `cq components doctor`, `cq components lint` e
`cq knowledge validate` ficam todos verdes — nenhum deles enxerga prosa que descreve
uma forma.

**A medição, antes.** Dos oito corpos, dois renderizavam bloco literal e seis descreviam o report em
prosa. O resultado acumulado:

| Sintoma | Contagem |
| --- | --- |
| verbos diferentes para a linha de fechamento | 6 |
| comandos sem nenhuma sugestão de próximo passo | 1 (`/quenching:specs:conclude`, o que encerra a spec) |
| encadeamentos que nomeiam o comando sem o slug | 1 (`/quenching:specs:execute` → `conclude`) |
| redações de "verbatim" sem dono | 7 |
| vocabulário de glifo compartilhado | nenhum |
| tabelas usando o `title` que `cq specs` já emitia | nenhuma |

O último é o mais revelador: `list --json` e `next --front` devolvem `title` desde sempre, e nenhuma
tabela o mostrava. Ninguém decidiu omiti-lo — não havia lugar onde a decisão pudesse ser tomada uma
vez.

## Onde o mold mora, e por quê

**A seção vai dentro de um arquivo que os corpos já carregam, não em arquivo próprio.**

`cq components read` aceita **um arquivo por chamada**. Um mold em arquivo novo custaria `+1 tool call`
por execução de cada comando da frente; como seção de um arquivo que todos já citam, custa zero
chamadas — apenas os seus próprios caracteres.

Isso estica o charter do arquivo hospedeiro, e o preço é declarado em vez de escondido: o H1 nomeia
a banda nova. Uma frente cujos comandos **não** compartilhem nenhum arquivo não tem essa opção, e aí
o arquivo próprio é o certo — a regra é a comparação, não o destino.

**O custo medido, e ele não é pequeno.** Na frente `specs`: a seção custa **9.171 chars**, e os oito
corpos somados **cresceram 3.615 chars líquidos** em vez de encolher. O mold não é uma economia de
contexto; é a troca de oito descrições divergentes e não checáveis por uma definição. Quem aplicar
esta regra deve medir e dizer o número, nunca estimá-lo
([../automation/context-discipline.md](../automation/context-discipline.md)).

**Uma banda nova chega sozinha a quem já cita o mold.** `cq components read --sections "§The report
mold"` devolve as sub-seções `###` junto com a seção-pai, então acrescentar uma sub-seção ao mold não
exige tocar o carregamento de corpo nenhum — muda só o corpo que vai *usá-la*, para declarar o seu
delta. É o argumento acima levado adiante: o mold como seção de um arquivo compartilhado custa zero
chamadas hoje e zero chamadas quando cresce.

Sete dos oito corpos citam o arquivo hospedeiro pelo **caminho nu** e portanto o leem inteiro, o que
é por si só deriva contra a regra de citar por `§`-endereço. Estreitá-las cortaria bem mais do que o
mold acrescenta, e é trabalho próprio com medição própria — não foi feito aqui.

## O que o mold não possui

A **língua** dos rótulos. Este plugin escreve seus corpos e references em inglês, mas o relatório
que um comando imprime segue a tag do repo alvo
([../agents/communication.md](../agents/communication.md) §What it governs). Por isso cada coluna
tem um **nome canônico**, que é o seu endereço dentro do mold, e um **rótulo impresso**, que segue a
tag. Permanecem canônicos em qualquer língua: o slug, os valores de `stage`, os nomes de registro,
os códigos `sp-*`, as catorze `##` de uma spec e os nomes de comando.

Um mold que fixasse os rótulos em inglês entregaria, em todo repo adotante, exatamente a falha que
aquele standard nomeia — ler a tag no início da sessão e ainda assim reportar em inglês.

## Divergência conhecida, aceita e não corrigida

Até esta branch, `plugins/quenching/commands/knowledge/status.md` §4 era cópia quase literal de
`plugins/quenching/commands/specs/status.md` §4 — as mesmas cinco seções, os mesmos títulos, a
mesma frase de fechamento. Era um formato compartilhado *de fato*, escrito duas vezes e possuído por
nenhum arquivo.

Este trabalho tocou apenas a frente `specs`, então **as duas deixaram de ser espelhos**. Isso está
registrado como divergência aceita, não como pendência silenciosa: a frente `docs` adotar o mold é
trabalho próprio, e até lá `/quenching:knowledge:status` continua sendo dono da sua própria forma. A
alternativa — generalizar o mold para três vocabulários de finding diferentes no mesmo movimento —
teria escrito um contrato genérico antes de haver dois casos provados para generalizar a partir de.

## Relação com os standards vizinhos

- [read-only-views.md](read-only-views.md) diz que a view read-only **divide os achados por quem os
  fecha**. Esta regra dá a essa divisão uma forma: a tabela de achados, com a coluna `Fecha com`.
- [shared-mold-keys.md](shared-mold-keys.md) governa o que um mold **compartilhado pode conter** —
  ali, chaves de frontmatter; aqui, blocos de saída. A pergunta é a mesma: todo citador pode
  legitimamente emitir este bloco?
- [../quality/computed-fact-prose-fanout.md](../quality/computed-fact-prose-fanout.md) é a razão de
  a regra existir, e o grep que ela prescreve é o que encontra os restos quando o conjunto de
  colunas muda: procure a forma escrita por extenso (a lista de colunas), não o nome do conceito.
