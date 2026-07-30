---
slug: revise-standards-subject-folders
title: Revise the fixed docs/standards subject folders
verification: per-section
priority: {level: 22, criticality: medium, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# Revise the fixed docs/standards subject folders

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a fourteen-heading skeleton. Every other heading below is created on
     first write by `specs.py section <slug> "<Heading>" --write`, which inserts it in the
     canonical position with the guidance comment kept here.

     THE STAGE-SCOPED EXPLICIT-NONE RULE. A heading is required — and required to carry
     `- none — <reason>` when it has nothing in it — only once ITS OWN gate is reached:

       new (capture)        `## Problem`
       ready (derived)      the nine definition sections (`## Problem` .. `## Risks`)
                            AND `## Tasks`
       ready (warn only)    `## Overview` non-empty, `## Handoff` non-empty
       promote -> archive/  `## Outcome`

     `ready` is a DERIVED STAGE, not a folder: a spec lives in `plans/` for its whole active
     life, and filling those ten sections is what makes it ready. Nothing refuses on that
     gate — it is a floor `execute` reports against, and the human's go-ahead is the
     `approved:` frontmatter record, asked for inline.

     Before its gate, a heading's absence is NOT an omission — it is a not-yet. After its
     gate, three rules decide whether a section counts as filled:

       1. `- none — <reason>` counts as filled. An omission and a null are different facts.
       2. A heading present with an EMPTY body is malformed and refuses. It is neither an
          answer nor a not-yet.
       3. An absent heading before its gate is legal.

     Headings are a PARSED contract — canonical English, exactly as written here. Body prose
     follows the repo's language. A heading outside this set is a stray and validate flags it.

     AUDIENCE. Each section names who reads it. `## Overview`/`## Problem`/`## Proposal`/
     `## Design` are for the human — examples and plain language belong there.
     `## Handoff`/`## Tasks` are for agents — terse, with `files:`/`verify:`/`pattern:`
     metadata. An orchestrator never sends the human sections to an executor; that is what
     lets one file serve both audiences without bloating agent context. -->

## Overview

Revisa o conjunto fixo de subjects que o skeleton de `docs/standards/` entrega. O `## Problem`
começou em uma pasta — `mlops` —, e a passagem de shape mostrou que ela é o sintoma: seis dos nove
subjects entregues definem o assunto pelo domínio de dados/ML na própria prosa de fronteira, e este
repositório, que é o primeiro alvo do próprio align, ficou com três pastas vazias, duas prosas
reescritas à mão e um décimo subject inventado localmente.

`## Proposal` diz o que fica verdadeiro depois: prosa de fronteira neutra quanto a domínio, `mlops/`
**retirado** do conjunto entregue sem que nenhum alvo já alinhado perca pasta ou linha de listing, e
a regra "only those that apply" — que o align já enuncia e não operacionaliza — transformada em
critério declarado.

`## Design` mostra por que retirar é a única forma segura e traz o fato que governa todo o resto: das
quatro maneiras de as duas árvores saírem de sincronia, três não têm detecção alguma. A passagem
adversarial converteu isso em duas coisas concretas — `## Validation` usa **este próprio repositório
como fixture**, porque ele é um alvo já alinhado, e `## Risks` enumera cada divergência com quem a
detectaria ou com a admissão de que ninguém detectaria.

`## Impact` declara uma única escrita em `docs/standards/`, e ela é uma **edição**: a instância
"subject entregue" acrescentada ao doc que já é dono da assimetria, porque um terceiro arquivo para
uma regra só seria a reenunciação que este repositório proíbe. `## Tasks` ordena o trabalho em quatro
grupos, e a primeira task não muda nada — ela sonda.

`## Out of Scope` guarda o que se parece com este trabalho e não é — sobretudo o subject `agents/`,
que pertence ao spec irmão já aprovado. `## Open Decisions` guarda os seis pontos que este spec
deliberadamente não decide, três deles porque decidir exigiria presumir o resultado de um sibling.
## Problem

A estrutura de subpastas fixas de `docs/standards/` que o plugin instala e espera precisa ser revista. A pasta `mlops` destoa das demais: enquanto as outras nomeiam assuntos de aplicação geral, `mlops` representa um braço muito específico, usado em quase nenhum projeto que o plugin alinha — o que faz o esqueleto canônico carregar, em todo alvo, uma pasta que quase sempre fica vazia.

`mlops` é o sintoma, não a causa. O conjunto entregue em
`plugins/quenching/assets/docs/standards/` enuncia, na própria prosa de fronteira, que foi escrito
para um repositório de dados/ML: `naming/index.md:3` diz "**Data** naming — tables, columns,
descriptions, schemas/catalogs" e cataloga `tables · columns · descriptions · schemas-catalogs`;
`quality/index.md:3` diz "Data and model quality — per-row data checks, data drift/stability, model
monitoring"; `workflows/index.md:3` diz "The job/task/schema framework". Seis dos nove subjects
entregues carregam essa suposição — `mlops` é só o único cujo **nome** a revela.

Este repositório é a prova, porque é o primeiro alvo do próprio `/docs:align`: ficou com todos os
nove, três guardam apenas um `index.md` (`data-modeling/`, `mlops/`, `platform/`), e dois tiveram a
prosa de fronteira **reescrita localmente** para significar algo aqui —
`docs/standards/naming/index.md:3-5` diz textualmente que "the skeleton is oriented toward data
naming …; this repo has no data". Um décimo subject, `automation/`, teve de ser inventado localmente
porque os nove entregues não tinham casa para uma command surface de Claude Code.

**Por que agora.** O conjunto já está em movimento: `declare-repo-body-language` está aprovado
(2026-07-29) e sua task 1 edita `taxonomy.md` §The canonical tree (locked) para acrescentar
`agents/`. E o custo de um subject reservado-e-vazio é cobrado pelo próprio gate do align:
`assets/references/docs-align/conformance.md:133` diz que o gate de verify confirma "each standards
subject's coverage/deferral ledger filled (every candidate present or listed)", e cada subject vazio
entrega um catálogo de candidatos mais um ledger que lê `- _(none yet — fill on population)_`. São
três itens permanentemente abertos só neste repositório.

## Proposal

- O conjunto de subjects entregue deixa de codificar um domínio como se fosse universal: a prosa de
  fronteira de `naming/`, `quality/` e `workflows/` no skeleton passa a enunciar o assunto de forma
  neutra quanto a domínio, com o caso de dados como **exemplo** e não como definição.
- `mlops/` sai do conjunto entregue, **retirado e não desreservado**: nenhum comando o cria, e
  nenhum repositório já alinhado perde pasta ou linha de listing por causa desta mudança.
- `data-modeling/` e `platform/` continuam no conjunto declarado, mas passam a ser
  **disponíveis por demanda** em vez de entregues por padrão — o nome de cada um sobrevive a um
  repositório sem dados; o conteúdo não.
- A regra "only those that apply", que `plugins/quenching/commands/docs/align.md:161` já enuncia,
  passa a ser operacional: o step 4 ganha um critério declarado que decide se um subject é
  escafoldado, em vez de deixar a decisão implícita e o default em copiar tudo.
- As duas árvores param de divergir por acidente: uma lista declarada em `taxonomy.md` §The
  canonical tree (locked) e um invariante verificável que confere as duas árvores contra ela.
- Um alvo já alinhado que atualize o plugin não recebe **nenhum** finding novo de
  `okf-validate.py` por causa desta mudança.
- A situação de `automation/` — hoje subject local só deste repositório, ausente do conjunto
  entregue — fica decidida em vez de herdada; ver `## Open Decisions`.

## Out of Scope

- **Deletar uma pasta de subject vazia em um repositório-alvo já alinhado.**
  `plugins/quenching/commands/docs/align.md:190-192` e
  [retiring-a-reserved-artifact.md](/docs/standards/architecture/retiring-a-reserved-artifact.md)
  §The consequence for disposition já fixam a regra: a disposição de um arquivo sobrevivente é do
  repositório-alvo, não da varredura. Este spec herda a regra — ele não deleta a pasta de ninguém.
  Isso inclui as três pastas vazias deste próprio repositório; ver `## Open Decisions`.
- **Acrescentar o subject `agents/`.** É do spec irmão `declare-repo-body-language`, aprovado em
  2026-07-29, cuja task 1 já o abre nas duas árvores. Este spec não antecipa aquele resultado nem
  edita aquele arquivo; ver `## Risks`.
- **Renomear docs *dentro* de um subject.** `retire-skill-vocabulary` (linhas 191-193) registra
  `docs/standards/automation/skills.md` e `skill-evaluation.md` como nomes que mentem e passa o
  caminho para este spec — mas o que este spec move são **pastas**. Renomear aqueles dois arquivos,
  dentro de qualquer pasta em que terminem, é passada separada.
- **Renomear qualquer subject, `automation/` incluído.** O `## Design` explica por que nenhum
  rename paga o próprio raio, e `restructure-claude-front-namespace` (linha 144) já conta com
  `docs/standards/automation/` mantendo o nome atual.
- **Ensinar `/docs:add` a semear a fronteira de um subject a partir do skeleton.** Consequência real
  do critério de aplicabilidade — um subject criado sob demanda por `/docs:add` ganharia uma porta de
  entrada mais magra do que um escafoldado —, e cortada aqui de propósito: o critério é uma proposta
  ao humano na adoção, então nenhum subject nasce sem que sua listagem entregue tenha sido oferecida.
  Mexer em `/docs:add` alargaria este spec para um segundo comando por um ganho que a mitigação já
  cobre.
- **Os outros seis homes do bundle.** `catalog/`, `vision/`, `documentation/`, `knowledge/` e
  `reference/` respondem à mesma pergunta ("isto foi entregue para um repositório de dados?") em
  outra árvore. Ficam fora, para manter o blast radius em uma listagem só.
- **Um bump de `okf_version`.** O conjunto de subjects **não** é regra de formato:
  `assets/references/docs-align/okf-spec.md` não nomeia subject algum em nenhuma de suas seções
  (Reserved filenames · Frontmatter · Concept `type` · Normative rules · Links · Bundle &
  conformance · o perfil do plugin). É decisão de perfil, declarada só em `taxonomy.md`, então
  mudá-la não muda o formato — e `upgrade-okf-to-v0-2` continua dono daquele bump.
- **Enforcement por máquina do conjunto de subjects.** Ensinar `okf-validate.py` a conhecer a lista
  é um checker novo com raio próprio; este spec declara o invariante e o verifica por grep. Ver
  `## Open Decisions`.
## Impact

**Código e conteúdo que este spec toca**, todo dentro do plugin e do bundle deste repositório: a
declaração autoritativa em `plugins/quenching/assets/references/docs-align/taxonomy.md:23`; a árvore
entregue em `plugins/quenching/assets/docs/standards/` (a pasta `mlops/`, as nove linhas de
`## Subtopics` de seu `index.md`, e a prosa de fronteira de `naming/`, `quality/` e `workflows/`); os
links entre homes que resolvem para dentro de um subject
(`plugins/quenching/assets/docs/reference/index.md:11`,
`plugins/quenching/assets/docs/reference/regulations/index.md:8`,
`plugins/quenching/assets/docs/standards/quality/index.md:6-7`); o step 4 de
`plugins/quenching/commands/docs/align.md`; e as três reenunciações fora da árvore entregue —
`plugins/quenching/README.md:373-374`,
`plugins/quenching/assets/references/docs-align/migration.md:36-38` e
`plugins/quenching/assets/references/docs-add/homes.md:64`.

**O que este spec deliberadamente não toca**, e é por isso que não aparece acima: as dez linhas de
`## Subtopics` de `docs/standards/index.md` e as três pastas vazias deste repositório. Conservá-las é
o invariante da retirada, não um esquecimento — ver `## Validation`.

### Standards this spec will write into docs/standards/

- `docs/standards/architecture/retiring-a-reserved-artifact.md` — a instância "subject entregue"
  acrescentada ao doc que **já é dono** da assimetria que este spec aplica (§Why the reservation is
  load-bearing, §The consequence for disposition). É uma edição, não um doc novo: o spec irmão
  `retire-skill-vocabulary` já declara `docs/standards/architecture/shipped-mold-retirement.md` para
  a instância "mold", e um terceiro arquivo para uma regra só é exatamente a reenunciação que a
  doutrina de colapso deste repositório proíbe

### Standards at `authority: background` this spec may resolve

- none — `grep -rn 'authority: background' docs/standards/` devolve três docs
  (`quality/selftest-mutation.md`, `automation/context-budget.md`,
  `automation/session-evidence.md`) e nenhum deles espera uma decisão sobre o conjunto de subjects.

### Product code this spec expects to touch

- none — este repositório não tem código de aplicação. O que se parece com código aqui são os três
  scripts de `assets/bin/` e `assets/hooks/`, e nenhum deles conhece o conjunto de subjects
  (`grep -n 'subject' plugins/quenching/assets/hooks/okf-validate.py` não devolve nada), então
  nenhum é tocado. Os bodies de comando e as references que este spec edita são payload do plugin,
  já enumerados acima.

## Validation

Quatro asserções. A **fixture é este próprio repositório**, porque ele é um alvo já alinhado — é o
que torna o invariante da retirada verificável em vez de argumentado.

1. **As duas árvores conformam.**
   `python3 plugins/quenching/assets/hooks/okf-validate.py assets/docs` e
   `python3 plugins/quenching/assets/hooks/okf-validate.py docs` reportam, os dois,
   `0 error(s), 0 warning(s)`.

2. **O invariante da retirada, afirmado no positivo.** `ls docs/standards/mlops/index.md` existe e
   `grep -n 'mlops/' docs/standards/index.md` devolve a linha de `## Subtopics`. Nenhum dos dois é
   removido por este spec. Um alvo já alinhado — este — atravessa a mudança sem perder pasta nem
   linha de listing, e é essa a asserção, não a ausência de erro.

3. **O par que impede `index-broken-link`, verificado como par.** Na árvore entregue,
   `plugins/quenching/assets/docs/standards/mlops/` **não existe** *e*
   `grep -n 'mlops/' plugins/quenching/assets/docs/standards/index.md` não devolve nada — os dois na
   mesma verificação, porque cada um isolado é verdadeiro no estado meio-aterrado que a asserção
   existe para excluir. Ao mesmo tempo,
   `grep -n 'mlops' plugins/quenching/assets/references/docs-align/taxonomy.md` **ainda** nomeia o
   subject, como disponível por demanda: retirado do que se copia, não do que se declara.

4. **O censo das reenunciações, com a exclusão registrada.**
   `grep -rn 'mlops' plugins/quenching docs` devolve, e apenas: a linha de `taxonomy.md` §The
   canonical tree (locked); as duas frases de doutrina de bundle density em
   `plugins/quenching/commands/docs/status.md:41` e `:156`; a mesma frase em
   `docs/knowledge/glossary.md:86`; e a pasta mais a linha de listing deste repositório, da asserção 2.
   As três frases de doutrina ficam **verbatim** — o exemplo "a repo that legitimately has no
   `mlops/`" continua verdadeiro, e fica mais verdadeiro. Nenhuma outra ocorrência sobrevive, e
   `plugins/quenching/README.md` não devolve nenhuma.

O grep é alarme contra reenunciação **nova**, não censo autoritativo: quem executa enumera os seis
locais pela tabela de `## Design` antes de declarar qualquer task pronta. Três das quatro formas de
as duas árvores divergirem não têm detecção automática alguma (tabela em `## Design`), e é por isso
que estas asserções rodam dentro da task que muda cada árvore.

## Design

**Retirar, nunca desreservar — a disciplina vem inteira de um contrato que já existe.**
[retiring-a-reserved-artifact.md](/docs/standards/architecture/retiring-a-reserved-artifact.md) foi
escrito para um *nome de arquivo reservado*, mas a assimetria que ele nomeia é a mesma aqui, e o
mecanismo é nomeável: `docs/standards/index.md:29` carrega `* [mlops/](mlops/index.md)`, e
`assets/references/docs-align/conformance.md:64` faz de um link de listing para **uma subpasta que
não existe em disco** um WARN `index-broken-link`. Remover a pasta e conservar a linha — ou o
contrário, em um alvo — é exatamente o "eles não fizeram nada, atualizaram o plugin, e o bundle
ficou amarelo" que aquele doc existe para impedir. Regra durável: **retirar um subject entregue é
parar de entregá-lo e não mexer em mais nada.**

**A assimetria de detecção é direcional, e é o fato que governa todo o resto deste design.**
`grep -n 'subject' plugins/quenching/assets/hooks/okf-validate.py` não retorna nada — o validador
não tem conhecimento algum do conjunto de subjects. O que existe é `index-broken-link`, que é sobre
*links*, não sobre o conjunto:

| Mudança | Quem a detecta |
| --- | --- |
| pasta de subject removida, linha de listing conservada | `index-broken-link` (WARN) |
| linha de listing removida, pasta conservada | **nada** — um `index.md` é reservado, não é concept doc, então `index-orphan` não o alcança |
| subject acrescentado em uma árvore e não na outra | **nada** |
| subject em disco e não em `taxonomy.md` §The canonical tree (locked) | **nada** |

Três das quatro linhas não têm detecção. É por isso que o invariante de duas árvores deste spec é
um grep declarado em `## Validation`, executado dentro da própria task que muda cada árvore, e não
uma confiança de que o gate do align o pegaria.

**Uma lista declarada, seis reenunciações.** O censo, levantado nesta passagem:

| Local | O que carrega |
| --- | --- |
| `plugins/quenching/assets/references/docs-align/taxonomy.md:23` | §The canonical tree (locked) — a declaração autoritativa, em uma linha |
| `plugins/quenching/assets/docs/standards/index.md:22-30` | as nove linhas de `## Subtopics` do skeleton |
| `plugins/quenching/README.md:373-374` | o diagrama de árvore na documentação do produto |
| `docs/standards/index.md:22-31` | as dez linhas de `## Subtopics` deste repositório (as nove mais `automation/`) |
| `plugins/quenching/assets/references/docs-align/migration.md:36-38` | o mapa pt→en de subpastas, que precisa de **alvos** canônicos: `modelagem/`→`data-modeling/`, `plataforma/`→`platform/` |
| `plugins/quenching/assets/references/docs-add/homes.md:64` | o roteamento que nomeia `data-modeling/` |

Mais quatro links **entre homes** que resolvem para dentro de um subject por caminho fixo, e que são
o que torna qualquer rename um rename de verdade: `assets/docs/reference/index.md:11` e
`assets/docs/reference/regulations/index.md:8` apontam para `standards/mlops/`;
`assets/docs/catalog/index.md:11` e `assets/templates/catalog/system.md:46` apontam para
`standards/data-modeling/`. E `mlops` é também o **exemplo** da doutrina de bundle density em três
lugares — `commands/docs/status.md:41` e `:156` e `docs/knowledge/glossary.md:86`, todos com a mesma
frase "a repo that legitimately has no `mlops/`". Retirar o subject do conjunto entregue sem tocar
nesse exemplo é legítimo, porque o exemplo continua verdadeiro e fica mais verdadeiro — mas ele
precisa ser lido antes de alguém afirmar que o grep está limpo.

**O critério de aplicabilidade fica onde a regra já está enunciada.**
`plugins/quenching/commands/docs/align.md:161` já diz "copy the applicable `index.md` listings", e
`assets/docs/standards/index.md:16` já diz "Keep only the subtopics that apply to the repo". Nada
decide o que é *applicable*, e o default observado é copiar tudo — este repositório. A correção é
portanto um critério declarado no step 4, não um mecanismo novo: um subject é escafoldado quando o
align tem, na própria passada, ao menos um doc para colocar nele **ou** o humano o pediu na adoção.
Um subject vazio deixa de nascer, o que também zera o ledger permanentemente aberto que
`conformance.md:133` cobra.

**O que muda de nome e o que só muda de prosa.** Nenhum subject é renomeado por este spec, e isso é
decisão e não omissão: um rename de subject move uma pasta em duas árvores, reescreve seis listagens
e reescreve quatro links entre homes, e trocar `naming/` por um nome mais largo não paga esse raio.
O que muda é a **prosa de fronteira** de `naming/`, `quality/` e `workflows/` no skeleton, que hoje
define o assunto pelo domínio de dados em vez de exemplificá-lo — e é a prosa, não o nome, que este
repositório teve de reescrever à mão para conseguir usar o subject.

**Contratos que este design não pode contradizer.**
[plugin-layout.md](/docs/standards/architecture/plugin-layout.md) — nada disto é entry point, então
tudo vive sob `assets/`. [align-surface.md](/docs/standards/architecture/align-surface.md) — a
mudança é no step 4 de um align que já existe, não em um comando novo.
[versioning-release.md](/docs/standards/ci-cd/versioning-release.md) — o skeleton entregue é payload
versionado, e o bump acontece uma vez, no conclude, fora deste spec.

## Alternatives Considered

| Abordagem | Por que perdeu |
| --- | --- |
| **Só remover `mlops/`** — a leitura literal do `## Problem` | Trata o único subject cujo nome revela a suposição e deixa cinco de pé. `naming/`, `quality/` e `workflows/` continuariam definindo o assunto pelo domínio de dados, e o próximo repositório sem dados repetiria a reescrita local que `docs/standards/naming/index.md:3-5` documenta. |
| **Core universal + packs de domínio** — um núcleo sempre aplicável mais packs nomeados (`data` = `data-modeling/` + `platform/` + `mlops/`) que o align oferece | A alternativa mais atraente, e perdeu por preço: introduz um conceito novo ("pack") em uma taxonomia cujo valor é ser pequena, e o glossário ganharia um termo para uma estrutura que existe em um lugar só. Não compra nada que a escolhida não compre — "only those that apply" já é a regra declarada em `commands/docs/align.md:161`, ela apenas não é operacional. Um critério de aplicabilidade entrega o mesmo resultado sem um nível de indireção. |
| **Destravar o conjunto** — subjects livres por repositório, `taxonomy.md` para de declará-los | Rejeitado por duas dependências de código, não por gosto. `assets/references/docs-align/migration.md:36-38` mapeia `modelagem/`→`data-modeling/` e `plataforma/`→`platform/`, e um mapa de convergência precisa de **alvos** canônicos para existir. E quatro links entre homes resolvem por caminho fixo para dentro de um subject (`assets/docs/reference/index.md:11`, `regulations/index.md:8`, `catalog/index.md:11`, `assets/templates/catalog/system.md:46`). Destravar quebra os dois. |
| **Renomear os subjects domain-bound em vez de retirar** — `mlops/` viraria algo mais largo | Um rename paga o raio inteiro (pasta em duas árvores, seis listagens, quatro links entre homes) para entregar uma pasta que continua vazia em quase todo alvo. Retirar entrega o mesmo alívio com raio zero, porque não mexer em nada é exatamente o que a retirada exige. |
| **Ensinar `okf-validate.py` o conjunto de subjects** — fechar por máquina as três linhas sem detecção | Não perdeu no mérito, perdeu no escopo: é um checker novo, com código de finding novo, com efeito imediato em todo alvo já alinhado — e um checker que reprova um alvo por ter um subject a mais é o oposto do que a retirada garante. Fica em `## Open Decisions` com o que a decide. |
| **Não fazer nada** | O conjunto continua sendo copiado inteiro, o próximo repositório sem dados reescreve as mesmas duas prosas de fronteira à mão, e os três ledgers vazios seguem abertos. E o conjunto vai ser editado de todo modo por `declare-repo-body-language`, então "não mexer" não é o estado que se conserva. |

## Open Decisions

- **`/docs:align` hoje copia os nove subjects, ou só os aplicáveis?** É a suposição load-bearing
  deste spec. A favor da leitura "copia tudo": este repositório é o primeiro alvo do próprio align e
  ficou com nove subjects, três vazios, e um `standards/index.md` listando os dez. Contra: o step 4
  em `commands/docs/align.md:161` diz "copy the applicable `index.md` listings", e
  `git log --diff-filter=A -- docs/standards/mlops/index.md` devolve um único commit cujo subject é
  `.`, o que não diz quem criou a pasta. **Como será decidido:** pela task 1.1 — rodar o caso de
  instalação em um repositório de rascunho sem dados e contar as subpastas de `standards/`. A sondagem
  é barata e decisiva, e roda antes da task 3.1: se a resposta for "só os aplicáveis", aquela task
  encolhe para um esclarecimento de redação.
- **Este repositório deleta as próprias pastas vazias `docs/standards/mlops/`, `data-modeling/` e
  `platform/`?** Este spec **não** as deleta, e a omissão é deliberada:
  [retiring-a-reserved-artifact.md](/docs/standards/architecture/retiring-a-reserved-artifact.md)
  §The consequence for disposition diz que a disposição de um arquivo sobrevivente é do
  repositório-alvo, e este repositório é um alvo. **Como será decidido:** pelo humano, na execução,
  como um item de confirmação próprio — e a resposta não muda task alguma, porque a asserção 3 de
  `## Validation` fala sobre a árvore entregue e a asserção 2 conserva esta.
- **A instância durável fica em `retiring-a-reserved-artifact.md` ou muda para o
  `shipped-mold-retirement.md` do irmão?** A task 4.2 escreve no doc que existe hoje e é dono da
  assimetria. Se `retire-skill-vocabulary` aterrar primeiro seu
  `docs/standards/architecture/shipped-mold-retirement.md`, o lugar mais natural para a instância
  "subject entregue" pode ser aquele doc, que já é a generalização de "o plugin para de nomear
  alguma coisa". **Como será decidido:** lendo quais dos dois docs existem no momento da execução da
  task 4.2. Muda o caminho de destino da task, nunca a task — e em nenhum dos dois casos nasce um
  terceiro arquivo para a mesma regra.
- **`automation/` entra no conjunto entregue, fica local, ou se dissolve no que
  `declare-repo-body-language` produziu?** Hoje é o único subject deste bundle que não existe no
  skeleton, e o `## Design` daquele spec irmão registra que `automation/` "colide justamente nos
  repositórios mais propensos a adotar o bundle". **Como será decidido:** depois que aquele spec
  aterrar, lendo a linha de fronteira do `agents/index.md` que ele escreveu contra a de
  `automation/index.md`. Não é decidível agora sem presumir o resultado dele, e presumir é
  exatamente o que a fronteira citada em `## Risks` proíbe.
- **`docs/standards/automation/agents.md` muda de casa?** O `## Risks` de
  `declare-repo-body-language` o nomeia como candidato a mudar de subject e diz, textualmente, que
  mover pertence a este spec e não a ele. **Como será decidido:** junto com a decisão acima e pela
  mesma razão — o destino é o subject que aquele spec cria, então a decisão não pode preceder o
  aterrissamento dele. Fica registrado aqui para que ninguém precise redescobrir de quem é.
- **`okf-validate.py` algum dia aprende o conjunto de subjects?** Fecharia por máquina as três
  linhas sem detecção da tabela de `## Design`. **Como será decidido:** só por uma divergência real
  observada mais de uma vez. A barra é alta de propósito: um checker que reprova um alvo por ter um
  subject a mais contradiz a garantia da retirada, então o gatilho é evidência repetida, não uma
  hipótese.
## Risks

- **Um alvo já alinhado fica amarelo depois de atualizar o plugin.** Alguém lê "sai do conjunto
  entregue" como "deletar a pasta", e uma passada de `/docs:align` remove `standards/mlops/` em um
  alvo enquanto a linha de `## Subtopics` daquele `standards/index.md` sobrevive — `index-broken-link`
  em um repositório que não mudou nada. É o modo de falha exato que
  [retiring-a-reserved-artifact.md](/docs/standards/architecture/retiring-a-reserved-artifact.md)
  §Why the reservation is load-bearing existe para impedir. **Mitigação:** a palavra em todo lugar é
  *parar de entregar*, nunca *deletar*; `## Out of Scope` nomeia a deleção explicitamente; e o
  invariante de `## Validation` usa **este próprio repositório como fixture**, porque ele é um alvo
  já alinhado — ele conserva `docs/standards/mlops/` e sua linha de listing, e só a árvore entregue
  muda.
- **As duas árvores divergem e ninguém nota por três meses.** A árvore entregue e `taxonomy.md` são
  corrigidas e `plugins/quenching/README.md:373-374` continua listando `mlops/` — o manual do produto
  passa a mentir sobre o que instala. **Detecção: nenhuma.** O README não está no bundle,
  `okf-validate.py` nunca o lê, e `skills.py doctor`/`lint` não leem prosa. **Mitigação:** o grep de
  `## Validation` cobre `README.md` junto com as duas árvores, e não apenas as duas árvores. O spec
  irmão `rewrite-readme-for-collapsed-surface` também edita esse arquivo; a fronteira que este
  mantém é editar **somente** o diagrama de árvore das linhas 373-374.
- **A frase de doutrina que usa `mlops` como exemplo é "corrigida" por um leitor futuro.**
  `commands/docs/status.md:41` e `:156` e `docs/knowledge/glossary.md:86` dizem, os três, "a repo that
  legitimately has no `mlops/`". Quando o plugin para de entregar `mlops/`, a frase passa a parecer
  redundante e convida a uma reescrita que perde o ponto — que um home vazio é figura e não defeito.
  **Detecção: nenhuma. Mitigação:** os três locais são enumerados na task do censo como exclusão
  explícita, com a razão registrada inline: o exemplo continua verdadeiro, e fica mais verdadeiro.
- **O critério de aplicabilidade retém em silêncio um subject que o repositório vai precisar.** No
  caso de instalação normal — repositório vazio, nada a migrar — nenhum subject tem doc para receber,
  e um critério avaliado como filtro entregaria um `standards/` sem subpasta alguma. **Mitigação:** o
  critério é uma **proposta ao humano na adoção**, com a contagem de docs como default proposto, e
  nunca um filtro silencioso. Nenhum subject é retido sem que alguém tenha visto a lista.
- **Estado meio-aterrado entre `taxonomy.md` e o skeleton.** A pasta entregue sai e a linha de
  `## Subtopics` do skeleton fica, ou o contrário. **Esta direção tem detecção:**
  `python3 plugins/quenching/assets/hooks/okf-validate.py assets/docs` reporta `index-broken-link`, e
  esse comando já é um dos checks documentados em `CLAUDE.md`. Mitigado pela ordem declarada em
  `## Tasks` mais esse check dentro de cada task.
- **Colisão direta com `declare-repo-body-language`, que está aprovado (2026-07-29) e edita o mesmo
  conjunto declarado.** A task 1 daquele spec abre o subject `agents/` nas duas árvores e acrescenta a
  linha em `taxonomy.md` §The canonical tree (locked) — a mesma linha que este spec edita. **ACCEPTED
  — com a fronteira citada dos autos dele:** o primeiro bullet de `## Risks` daquele spec diz, nas
  suas palavras, que ele "adiciona exatamente um subject e não toca em nenhum outro, e o spec irmão
  continua livre para revisar o conjunto como um todo depois — inclusive renomeando o que este
  adicionou". Este spec honra a fronteira nos dois sentidos: **não** acrescenta, renomeia ou move
  `agents/`, e **não presume que ele aterrou**. Se o irmão entrar primeiro, a lista que este spec
  edita é a que ele produziu, uma linha maior; se não entrar, a lista é a de hoje. Nenhuma task deste
  spec depende de qual dos dois é verdade.
- **Um repositório de dados/ML perde a descoberta de `mlops/`.** Quem adota o bundle depois desta
  mudança não recebe a pasta por default e pode não saber que o assunto existe. **Mitigação:**
  `mlops/` **continua nomeado** em `taxonomy.md` §The canonical tree (locked) como disponível por
  demanda — retirado do que se copia, não do que se declara. É a mesma forma que
  `retiring-a-reserved-artifact.md` dá a um nome reservado: nada o produz, o nome segue reconhecido.
- **O leg de aplicabilidade pode ser desnecessário.** Se `/docs:align` já escafolda somente os
  subjects aplicáveis, as três pastas vazias deste repositório são artefato histórico e o critério é
  esclarecimento de redação, não mudança de comportamento. **ACCEPTED e condicionado:** a decisão
  está em `## Open Decisions` com a sondagem que a resolve, e a sondagem roda **antes** da task do
  critério, então o pior caso é uma task que encolhe — nunca uma que aterra errado.
- **Siblings em arquivos adjacentes.** `retire-skill-vocabulary` corrige os corpos de
  `docs/standards/automation/skills.md` e `skill-evaluation.md` e passa os **caminhos** para este
  spec (suas linhas 191-193); `restructure-claude-front-namespace` registra em `## Out of Scope`
  (linha 144) que a pasta de assunto `docs/standards/automation/` "já está com o nome de destino" e
  que ele traz a command surface até ela. **Fronteira que este spec mantém:** não renomeia
  `automation/` — renomeá-la quebraria a premissa daquele spec — e não renomeia doc algum dentro de
  um subject.

## Tasks

Quatro grupos, e a ordem é load-bearing três vezes: a sondagem do grupo 1 precede o critério do
grupo 3, porque ela é que diz se aquela task muda comportamento ou só redação; a árvore entregue
muda antes dos docs que a descrevem; e o censo é a última coisa, porque é o invariante e não o
trabalho. Cada task que escreve em `docs/standards/` nomeia o caminho na **própria linha do
checkbox**, porque `sp-impact-uncovered` casa com aquela linha e não com a continuação `files:`.

### 1. Decidir antes de mexer

- [ ] 1.1 Sondar o caso de instalação — rodar o step 4 de `/docs:align` em um repositório de rascunho
  sem dados e contar quantas subpastas de `standards/` aparecem — e registrar a contagem observada em
  `## Open Decisions` como resolução do primeiro item.
      verify: a contagem observada está escrita no spec, e a task 3.1 foi confirmada ou reduzida contra ela

### 2. A árvore entregue

- [ ] 2.1 Retirar `mlops/` do skeleton — remover a pasta **e** sua linha de `## Subtopics` no mesmo
  commit, porque é o par que impede `index-broken-link`.
      files: plugins/quenching/assets/docs/standards/mlops/index.md, plugins/quenching/assets/docs/standards/index.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py assets/docs → 0 error(s), 0 warning(s)
- [ ] 2.2 Reparar os três links entre homes que apontavam para `standards/mlops/`, cada um para o
  destino que descreve o mesmo assunto sem a pasta.
      files: plugins/quenching/assets/docs/reference/index.md, plugins/quenching/assets/docs/reference/regulations/index.md, plugins/quenching/assets/docs/standards/quality/index.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py assets/docs → 0 error(s), 0 warning(s), e grep -rn 'standards/mlops' plugins/quenching/assets/docs não devolve nada
- [ ] 2.3 Reescrever a prosa de fronteira de `naming/`, `quality/` e `workflows/` no skeleton de forma
  neutra quanto a domínio: o caso de dados aparece como **exemplo**, nunca como a definição do
  assunto. O teste de redação é o padrão que este repositório já usa localmente.
      files: plugins/quenching/assets/docs/standards/naming/index.md, plugins/quenching/assets/docs/standards/quality/index.md, plugins/quenching/assets/docs/standards/workflows/index.md
      pattern: docs/standards/quality/index.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py assets/docs → 0 error(s), 0 warning(s)
- [ ] 2.4 Reescrever `taxonomy.md` §The canonical tree (locked): `mlops/` nomeado como **retirado do
  que se copia e ainda declarado**, `data-modeling/` e `platform/` como disponíveis por demanda, e o
  restante intocado.
      files: plugins/quenching/assets/references/docs-align/taxonomy.md
      verify: grep -n 'mlops' plugins/quenching/assets/references/docs-align/taxonomy.md mostra o subject nomeado como disponível

### 3. O critério de aplicabilidade

- [ ] 3.1 Tornar operacional no step 4 de `/docs:align` a regra "only those that apply" que ele já
  enuncia — um critério declarado, apresentado como **proposta ao humano na adoção** e nunca como
  filtro silencioso.
      files: plugins/quenching/commands/docs/align.md
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json → 26 commands, findings vazio

### 4. As duas árvores e o invariante

- [ ] 4.1 Alinhar as três reenunciações fora da árvore entregue: o diagrama de árvore em
  `README.md:373-374` (**somente** o diagrama — o resto do arquivo é de
  `rewrite-readme-for-collapsed-surface`), o mapa pt→en de `migration.md:36-38` e o roteamento de
  `homes.md:64`.
      files: plugins/quenching/README.md, plugins/quenching/assets/references/docs-align/migration.md, plugins/quenching/assets/references/docs-add/homes.md
      verify: grep -rn 'mlops' plugins/quenching/README.md não devolve nada
- [ ] 4.2 Escrever a instância "subject entregue" em `docs/standards/architecture/retiring-a-reserved-artifact.md`
  — acrescentada ao doc que já é dono da assimetria, em `authority: current` como o resto dele, porque
  este spec executa a retirada sob a regra que está escrevendo. **Não** criar um doc novo, e não
  repetir o que §Why the reservation is load-bearing já diz.
      files: docs/standards/architecture/retiring-a-reserved-artifact.md, docs/standards/index.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs → 0 error(s), 0 warning(s)
- [ ] 4.3 Rodar as quatro asserções de `## Validation` como a task final, com a exclusão registrada
  inline: as três frases de doutrina que usam `mlops` como exemplo
  (`plugins/quenching/commands/docs/status.md:41` e `:156`, `docs/knowledge/glossary.md:86`) ficam
  verbatim, e a asserção 2 conserva a pasta e a linha de listing deste repositório.
      verify: as quatro asserções de ## Validation, cada uma com a saída citada
