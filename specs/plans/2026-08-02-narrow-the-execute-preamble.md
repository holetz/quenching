---
slug: narrow-the-execute-preamble
title: Estreitar o preâmbulo de /specs:execute — os seis itens que sobraram de read-by-section
verification: per-section
refined: {mode: gate, date: 2026-08-02}
approved: 2026-08-02
branch: {base: main, work: plan/narrow-the-execute-preamble}
---

# Estreitar o preâmbulo de /specs:execute — os seis itens que sobraram de read-by-section

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
     *(`standards/agents/communication.md` owns that language rule for a repo whose bundle has
     one. This template states it self-contained rather than citing it: `/specs:align` is native
     and installs here into repos that never adopted the bundle, where that path resolves to
     nothing.)*

     AUDIENCE. Each section names who reads it. `## Overview`/`## Problem`/`## Proposal`/
     `## Design` are for the human — examples and plain language belong there.
     `## Handoff`/`## Tasks` are for agents — terse, with `files:`/`verify:`/`pattern:`
     metadata. An orchestrator never sends the human sections to an executor; that is what
     lets one file serve both audiences without bloating agent context. -->

## Overview

Antes de `/quenching:specs:execute` escrever a primeira linha de código, ele **abre um monte de
coisa** — o próprio corpo, cinco arquivos de referência, seis seções da spec e os standards que ela
declara. Tudo isso entra no turno 1 e é **re-enviado em todo turno seguinte**, então cada char ali é
multiplicado pela run inteira. Hoje são 160.856 chars (~40,2k tokens) antes de qualquer trabalho.

`read-by-section-not-by-file` já cortou isso em 44% ensinando o comando a pedir **seções** em vez de
arquivos. Este spec pega os seis pedaços que aquele deixou para trás. Nenhum deles é uma ideia nova:

1. Seis citações no topo do corpo dão o **caminho do arquivo** e não o endereço da seção — e o texto
   já enumera as seções em prosa, logo antes de mandar abrir o arquivo inteiro.
2. Duas referências existem para um passo que quase nunca dispara, e são pagas em toda run.
3. O passo 4 manda ao executor as seções que o template diz em voz alta serem **do humano** — e não
   manda `## Out of Scope`, que é justamente a que diz ao construtor o que não tocar.
4. Os standards declarados são lidos inteiros, mesmo já sendo endereçáveis.
5. O corpo do comando é o maior item isolado depois dos cortes.
6. A ferramenta sai `1` em toda primeira run, num caso que é normal.
7. E o espelho do primeiro, achado ao definir este spec: cinco `§`endereços não dizem de que arquivo
   são, e o mesmo `§` ainda significa três coisas diferentes no mesmo corpo.

O que muda: toda citação vira um endereço **completo** — arquivo mais seção, sem quebra de linha —, a
referência de ramo condicional é lida no ramo, a audiência de uma seção passa a ser um **momento**
(decidir / construir / fechar) em vez de uma pessoa, um standard declarado pode dizer quais seções o
governam, e o `exit 1` deixa de acontecer porque o comando pergunta a partir do que já sabe.

A regra de audiência sai do papel de vez: o schema já carrega um campo `audience` que **ninguém lê** —
é por isso que ela nunca foi aplicada. Ele vira `moment` e ganha um consumidor, `specs.py section
--moment build`, de modo que o passo 4 pede um momento em vez de repetir uma lista que pode derivar.

**O corte garantido é 161.256 → 103.091 chars (~40,3k → ~25,8k tokens, −36%)** — e −64% contra o ponto
de partida de antes de `read-by-section`. Nada passa a recusar, nenhum comando novo nasce, e nenhum
arquivo é dividido ou movido.

## Problem

`read-by-section-not-by-file` entregou o leitor de seção e estreitou o passo 4 de
`/quenching:specs:execute`. **Nenhuma run aconteceu desde o merge** (`a98e634`, 2026-08-01), então
tudo abaixo é medição estática em disco — a mesma natureza de prova que aquela spec escolheu para si.

Medido em 2026-08-02 contra
[route-commands-without-always-on-descriptions](/specs/plans/2026-07-28-route-commands-without-always-on-descriptions.md)
(56.673 chars, `## Impact` declarando 2 standards, 3 pastas de assunto tocadas):

| Preâmbulo antes da primeira linha de código | chars | ~tokens |
| --- | ---: | ---: |
| antes de `read-by-section` (arquivo inteiro + pasta) | 287.709 | 71,9k |
| se o corpo for obedecido ao pé da letra | 100.252 | 25,1k (−65%) |
| **no caminho que o corpo realmente descreve** | **160.856** | **40,2k (−44%)** |

Os 21 pontos entre as duas últimas linhas são o assunto deste spec. Tudo o que entra no turno 1 é
re-enviado em todo turno seguinte, então cada char aqui é multiplicado pela run inteira.

**1. Seis citações não viraram endereço.** A tarefa 4.1 daquela spec entregou a regra em
`commands/specs/execute.md:22` — *"Every `§X` below is an address, and it is loaded as one — never by
opening the file."* Ela só alcança citações **que carregam um `§`**. Seis não carregam, e são as do
preâmbulo de topo, lidas no turno 1:

| linha | citação | arquivo | as §seções que o próprio texto enumera |
| --- | --- | ---: | ---: |
| `:19` | `specs-execute/execution.md` | 22.183 | 11.610 (−48%) |
| `:43` | `specs-isolate/git.md` | 16.617 | 4.233 (−75%) |
| `:48` | `specs-develop/spec-driven.md` | 22.666 | 10.149 (−55%) |
| `:50`, `:213` | `docs-add/homes.md` | 9.804 | 6.615 |
| `:215` | `docs-align/conformance.md` | 8.622 | — |

A linha 19 é o caso exemplar: ela **enumera em prosa** as sete seções de `execution.md` ("the
clean-tree precondition, the verification policy, the validation loop…"), que existem no arquivo com
esses nomes exatos, e então entrega o caminho do arquivo. Um executor lendo isso abre o arquivo.
São **60.604 chars (~15,2k tokens) por turno** num item já endereçável — as cinco referências têm
`## Contents` e nomes de seção limpos.

**2. Duas referências são carregadas para um passo que quase nunca dispara.** `homes.md` e
`conformance.md` (18.426 chars, ~4,6k tokens) só são usadas no passo 5c, e só para tasks que escrevem
`docs/`. Na spec medida são 3 de 15 tasks; nas outras 12 o custo é integral e é pago no turno 1.

**3. O passo 4 manda ao executor as seções que o template declara serem do humano.** Ele lê
`Problem,Proposal,Design,Impact,Handoff,Tasks`. Medido na spec de referência: `Problem` 7.253 +
`Proposal` 2.614 + `Design` 8.217 = **61% do que o passo 4 traz da spec**. O template de toda spec diz
o contrário em voz alta: *"`## Overview`/`## Problem`/`## Proposal`/`## Design` are for the human… An
orchestrator never sends the human sections to an executor; that is what lets one file serve both
audiences without bloating agent context."* A regra existe, tem dono e não é obedecida — e o conserto
não é simplesmente parar de mandá-las, porque `## Design` carrega as decisões que impedem uma task de
"consertar" algo deliberado.

**4. Os standards declarados são lidos inteiros.** 28.236 chars na spec medida. Eles **já** são
endereçáveis — `skills.py read docs/standards/automation/context-budget.md` devolve 12 seções — mas o
passo 4 manda ler o arquivo. E o marcador não resolve: `--rules-only` sobre `context-budget.md` rende
**−9%** (16.811 → 15.225), consistente com os 7% que a tarefa 3.4 mediu.

**5. O corpo do comando é o maior item isolado depois dos cortes.** 23.557 chars (~5,9k tokens),
residente em todo turno. Não é endereçável por seção: é o prompt.

**6. `specs.py section` sai 1 em toda primeira run.** O passo 4 pede `Handoff`, que não existe numa
spec nunca executada. A ferramenta degrada corretamente — imprime o resto e diz `(## Handoff is
absent)` — mas sai **1**, e o corpo manda "branch on the exit code (0 ok · 1 findings · 2 refusal)"
sem dizer que esse 1 é o caso normal.

**7. Cinco `§`endereços não carregam arquivo, e o mesmo sigilo tem três significados.** Espelho do
item 1, medido em 2026-08-02 sobre os 18 `§` do corpo. `§Delegating an executor` (`:208`, `:363`),
`§Declared versus emergent \`docs/\`` (`:217`), `§The verification policy` (`:240`) e
`§The section boundary` (`:271`) são todos de `execution.md` — e nenhum diz isso: o leitor tem de
lembrar. Um endereço sem arquivo não é mais resolvível que um arquivo sem endereço; é o mesmo defeito
virado do avesso. Pior, `§6` (`:268`) e `§5g` (`:298`) endereçam **passos deste corpo**, não seções de
referência, então o sigilo carrega três sentidos ao mesmo tempo. E dois dos endereços que **têm**
arquivo (`:92`, `:101`) quebram a linha no meio do endereço, o que impede qualquer leitura mecânica
dele. Nada disso é caro em chars — é o que torna a citação inverificável, e é por isso que o item
entra aqui e não em `## Risks`.

**A fronteira já está declarada pelo vizinho.**
[reduce-execute-conclude-cost](/specs/plans/2026-07-28-reduce-execute-conclude-cost.md)
`## Out of Scope` põe a doutrina de citação fora do seu escopo e a estima em "cerca de 22k tokens"
para corpo mais cinco referências — esta medição confirma (23.557 + 80.196 = 103.753 chars ≈ 26k).
Os itens 1 e 2 não têm dono hoje.

## Proposal

- **Toda citação de referência no corpo de `/quenching:specs:execute` é um endereço `§`.** As seis que
  hoje nomeiam só o arquivo passam a nomear as seções que o próprio texto já enumera, e o corpo deixa
  de ter duas formas de citar a mesma coisa. Escritas em **forma de prefixo**, porque `--sections`
  quebra o valor em vírgulas e sete seções das cinco referências não são endereçáveis pelo nome
  completo (`## Risks`).
- **`homes.md` e `conformance.md` são carregadas quando o passo 5c dispara, não antes.** Uma referência
  que só serve a um ramo condicional é lida naquele ramo.
- **A audiência de uma seção vira um momento, não uma pessoa.** `decision` / `build` / `close`, um
  valor por seção canônica, e o passo 4 lê o conjunto `build` — que perde `## Problem` e **ganha
  `## Out of Scope`**, hoje invisível para quem constrói. A regra de audiência do template deixa de
  ser prosa que ninguém aplica e vira o que `specs.py section` serve.
- **Um `docs/standards/` declarado pode carregar um `§`endereço no `## Impact`.** Sem endereço, o
  executor lê o arquivo inteiro — ler menos passa a ser uma afirmação que o autor faz, nunca uma
  economia que o executor toma sozinho. Custa zero de código.
- **O `exit 1` por seção ausente deixa de acontecer.** O passo 4 monta sua lista a partir do
  `sections[].state` que o `status` do passo 2 já devolveu, em vez de pedir uma seção que não existe.
- **O racional do corpo é relocado para `execution.md`** sob `<!-- rationale -->`, medido em vez de
  afirmado, mantendo no prompt a metade-regra dos três blocos que intercalam os dois.
- **A medição antes/depois é refeita da mesma forma**: contagem de arquivo mais aritmética, sobre a
  mesma spec de referência, para o número deste spec ser comparável ao dos −35% e −44% já registrados.
  O corte **garantido** é 161.256 → 103.091 chars (~40,3k → ~25,8k tokens, **−36%**), e sobre isso o
  endereço declarado e a relocação rendem o que renderem, sem promessa.
- Nada passa a recusar, nenhum comando novo é criado, nenhuma `description` cresce, e nenhum arquivo
  de `docs/` ou de `assets/references/` é dividido, movido ou apagado — as três recusas que
  `read-by-section` já mediu continuam valendo.

## Out of Scope

- **O instrumento de medição de custo de run** — `session.py` com subcomando de custo, `/skill:retro`
  lendo custo, a tabela de model policy. É de
  [reduce-execute-conclude-cost](/specs/plans/2026-07-28-reduce-execute-conclude-cost.md), grupo 1, e
  aquele spec é o dono de `run-cost.md`.
- **Consertar o `--sections` que quebra em vírgula.** Medido aqui e registrado em `## Risks`: sete
  seções das cinco referências recusam com `exit 2` quando endereçadas pelo nome completo, e a
  mensagem de erro lista a recusada em `available:`. Este spec **contorna** escrevendo as citações em
  forma de prefixo; consertar o parser é follow-up, da mesma família do
  [fix-the-files-field-parser-splitting-on-commas-inside-parentheses](/specs/plans/2026-08-02-fix-the-files-field-parser-splitting-on-commas-inside-parentheses.md).
- **Pin inline de `model` ou `effort`.** Recusado com conta pelo mesmo vizinho: model e effort são
  parte da chave do prompt cache da sessão, então um pin força recompute do contexto que este spec
  está justamente barateando.
- **`context: fork` em qualquer comando do ciclo.** Proibido por nome no `CLAUDE.md`. Registrado aqui
  para que a ideia não volte como otimização.
- **Dividir standards ou referências em mais arquivos.** Medido e recusado por `read-by-section`
  `## Alternatives Considered` — ~93k tokens de frontmatter novo sem tocar a causa. Nenhum arquivo é
  criado, dividido ou movido aqui.
- **Apagar racional para compactar.** Recusado pela mesma seção, e a decisão de compactar **por
  relocação** já é contrato em `context-discipline.md` — que é a forma que a `## Open Decisions` 3
  autorizou para o corpo.
- **Estender a convenção `<!-- rules -->` às outras dezoito referências, ou aos 39 standards que não a
  carregam.** Decidido e fechado na tarefa 3.4 de `read-by-section`: 7% de racional medido, contra os
  25–35% chutados. É por isso que `--rules-only` não é a resposta da `## Open Decisions` 2.
- **Os outros vinte e cinco comandos da superfície.** A doutrina de citação é escrita como regra da
  superfície inteira e **provada em um**, que é onde a medição existe. Converter os outros vinte e
  cinco corpos é o próximo spec, não este.
- **Re-medir os transcripts do arquivo.** A prova aqui é estática e determinística, pela mesma razão
  que `read-by-section` deu: um spec sobre custo de contexto não abre a própria prova gerando sessões
  de agente faturadas.
- **Uma task de bump de versão.** `versioning-release.md` §When the bump happens é explícita: as
  strings se movem uma vez, em `/quenching:specs:conclude`, nunca como task.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/automation/context-discipline.md` — **revisado, não criado.** É o dono declarado do
  assunto. §Open less regra 2 hoje **afirma** que toda citação do repositório já é um `§`endereço, o
  que o item 1 do `## Problem` mede ser falso; a afirmação vira regra. Ganha: uma citação de
  referência num corpo de comando é um endereço `§` e um caminho nu é um finding — **regra da
  superfície inteira, provada em um comando**; uma referência usada só por um ramo condicional é lida
  naquele ramo; e um `docs/standards/` declarado pode carregar um `§`endereço, cujo default é o
  arquivo inteiro porque ler menos é uma afirmação do autor, não uma economia do executor. Continua
  `authority: background` — nada aqui roda em dois repos adotantes, que é o gate de graduação dele.
- `docs/standards/workflows/plan-artifacts.md` — **revisado, não criado.** §Fourteen canonical
  sections ganha a coluna `moment` (`decision` / `build` / `close`), um valor por seção, substituindo
  a binária humano/agente que hoje vive só no comentário do template. §`## Impact` carries one parsed
  sub-heading ganha a forma opcional do `§`endereço e a nota de que o parser já a tolera. §The
  template is duplicated on purpose é o aviso que essa edição tem de respeitar: são **três** cópias e
  uma delas sombreia em vez de servir de fallback.

### Product code this spec expects to touch

- `plugins/quenching/commands/specs/execute.md` — as seis citações de topo viram endereços `§` em
  forma de prefixo; o carregamento de `homes.md`/`conformance.md` desce para o passo 5c; o passo 4 lê
  o conjunto `build` montado a partir do `sections[].state` do `status`; o racional dos seis blocos
  do `## Design` §5 sai.
- `plugins/quenching/assets/references/specs-execute/execution.md` — recebe o racional relocado sob
  `<!-- rationale -->`, e ganha seção só se um `§`endereço do corpo precisar de uma que não existe.
- `plugins/quenching/assets/references/specs-develop/spec-driven.md` — §The fourteen sections recebe
  o eixo de momento, §The executor contract passa a nomear o conjunto `build`, e §`## Impact` — the
  one parsed declaration ganha a forma do `§`endereço.
- `plugins/quenching/assets/bin/specs.py` e `plugins/quenching/assets/specs/schema.json` — o campo
  `audience` das quatorze seções vira `moment`, e `section` ganha `--moment <valor>`. Hoje `audience`
  é **dado morto**: declarado nos dois arquivos e lido por ninguém, que é exatamente por que a regra
  de audiência do template nunca foi aplicada. §There is a THIRD copy manda tratar isso como lockstep
  de três arquivos — os dois acima mais `templates/spec.md`.
  **`parse_impact_standards` não muda:** medido, ele já tolera o `§`endereço no bullet e
  `sp-impact-uncovered` segue funcionando. Essa ausência de mudança é um resultado do `## Design` §2,
  não um esquecimento.
- `plugins/quenching/assets/specs/templates/spec.md` e as outras duas cópias — o comentário de
  audiência é reescrito como momento. §The template is duplicated on purpose diz quais são e qual
  sombreia.
- `plugins/quenching/assets/bin/skills.py` — **nada.** A avaliação do item 4 não pediu nada do leitor;
  o defeito de vírgula do `--sections` é follow-up, não este spec.

## Validation

Tudo aqui é verificável por execução ou por contagem em disco. Nenhuma sessão de agente faturada é
aberta para provar um spec sobre custo de contexto, pela razão que `## Out of Scope` registra —
e por isso `assets/checks/functional-checks.sh` **não** aparece nesta seção nem em nenhum `verify:`,
por [surface-verification.md](/docs/standards/quality/surface-verification.md): ele pertence à front
de skill, não ao `## Validation` de uma spec.

**O antes, medido nesta árvore em 2026-08-02** — contagem sem frontmatter, sobre a mesma spec de
referência do `## Problem`, [route-commands-without-always-on-descriptions](/specs/plans/2026-07-28-route-commands-without-always-on-descriptions.md):

```
corpo de execute.md                                      23.557
execution.md            (arquivo inteiro, citação :19)   22.183
git.md                  (arquivo inteiro, citação :43)   16.617
spec-driven.md          (arquivo inteiro, citação :48)   22.666
homes.md                (arquivo inteiro, citação :50)    9.804
conformance.md          (arquivo inteiro, citação :215)   8.622
seções da spec lidas pelo passo 4                        29.571
docs/standards/ declarados, arquivos inteiros            28.236
                                                        -------
                                                        161.256 chars  (~40,3k tokens)
```

O `## Problem` registra **160.856** para o mesmo caminho. A diferença de 0,25% é qual contagem — com
ou sem frontmatter — foi usada em cada item. **A tarefa 0.1 refaz as duas pontas com uma convenção
só**, e é esse par que vale; o número solto de qualquer uma das pontas não vale nada.

**O depois, garantido:**

```
corpo de execute.md                                      23.557  (menos o que a relocação mover)
execution.md            (§seções que o texto enumera)    11.610
git.md                  (§seções que o texto enumera)     4.233
spec-driven.md          (§seções que o texto enumera)    10.149
homes.md + conformance.md   → descem para o passo 5c          0
seções da spec, conjunto `build`                         25.306
docs/standards/ declarados, sem §endereço                28.236
                                                        -------
                                                        103.091 chars  (~25,8k tokens)   −36%
```

E **−64%** contra os 287.709 de antes de `read-by-section`. O que o `§`endereço declarado e a
relocação do corpo renderem entra por cima disso, medido e **não prometido**.

**O que cada afirmação prova:**

- **O corte.** A tarefa 7.1 refaz as duas pontas com a convenção fixada em 0.1 e registra o par no
  commit e no `## Outcome`. Um número estimado em qualquer uma das pontas é falha da tarefa, não
  detalhe — é a regra que `read-by-section` já pagou para aprender.
- **Toda citação resolve.** Uma chamada `skills.py read` por referência citada, com exatamente os
  `§`endereços que o corpo passou a carregar, todas saindo **0**. Provado no `verify:` da tarefa 1.1,
  sem check permanente novo: `## Risks` aceitou a podridão futura porque ela falha alto — `exit 2` no
  turno 1, antes de qualquer código.
- **Todo endereço é completo.** `grep -c "§" plugins/quenching/commands/specs/execute.md` bate com o
  número de endereços cobertos pelas chamadas acima, mais os passos deste corpo — que depois de 1.2
  não usam mais `§`. Zero endereço sem arquivo, zero endereço partido por quebra de linha.
- **O passo 4 lê o conjunto `build`.** O corpo nomeia as seis seções, e nenhuma delas é `## Problem`.
  `specs.py section <slug> "Proposal,Out of Scope,Design,Impact,Handoff,Tasks"` sai **0** contra uma
  spec com as seis preenchidas, e o `exit 1` por seção ausente deixa de ser alcançável porque a lista
  vem do `sections[].state`.
- **O `§`endereço no `## Impact` não quebrou nada.** `specs.py validate` continua com **0 error(s)** e
  sem `sp-impact-uncovered`, contra um `## Impact` que carrega endereço em um standard e não no outro
  — provado por `specs.py selftest`, nunca por editar a superfície real.
- **A superfície continua íntegra.** Lockstep de versão concordando entre `VERSION` e os três scripts;
  `okf-validate.py assets/docs` e `okf-validate.py docs` em 0 error(s); `skills.py doctor` em 26
  comandos e 0 findings; `skills.py lint` em exit 0; os três `selftest` passando. Este spec não cria
  nem remove entry point e não faz nenhuma `description` crescer.

## Design

As cinco decisões que este spec fecha. Todas foram medidas em disco em 2026-08-02, contra a mesma
spec de referência do `## Problem` — [route-commands-without-always-on-descriptions](/specs/plans/2026-07-28-route-commands-without-always-on-descriptions.md).

### 1. A audiência de uma seção é um MOMENTO, não uma pessoa

O template de spec declara uma binária — quatro seções "para o humano", duas "para o agente", e
silêncio sobre as outras oito. Medida, a binária não sobrevive: o corte que ela sugere rende
**−14%**, e erra o alvo. `## Out of Scope` é a seção que mais governa um executor e a binária não a
menciona.

A regra que substitui a binária tem três valores, e cada seção canônica recebe exatamente um:

| Momento | Quem lê, e quando | Seções | chars |
| --- | --- | --- | ---: |
| `decision` | o humano, decidindo **construir ou não** | `## Overview`, `## Problem`, `## Alternatives Considered`, `## Risks`, `## Open Decisions` | 26.549 |
| `build` | o executor, no passo 4 de `/quenching:specs:execute` | `## Proposal`, `## Out of Scope`, `## Design`, `## Impact`, `## Handoff`, `## Tasks` | **25.306** |
| `close` | `/quenching:specs:conclude` | `## Validation`, `## Outcome` | 3.681 |

O passo 4 passa a ler o conjunto `build`. Contra os 29.571 de hoje são **−4.265 (−14%)**, e o valor
não está aí: `## Problem` (7.253) sai porque argumenta **se** construir; `## Out of Scope` (2.988)
**entra pela primeira vez**, que é o defeito real — nada hoje diz ao construtor o que não tocar.
`## Design` fica, pela razão que o próprio `## Problem` deu: ele carrega as decisões que impedem uma
task de "consertar" algo deliberado.

O eixo é **ligado**, não só declarado. Hoje o schema já carrega um campo `audience` nas quatorze
seções — em `specs.py` e em `schema.json` — e **ninguém o lê**: é dado morto, e é por isso que a regra
de audiência do template nunca passou de prosa. `moment` toma o lugar dele e ganha um consumidor:
`specs.py section --moment build` resolve a lista pelo schema, e o passo 4 pede um momento em vez de
enumerar seis headings. Sem isso o corpo repetiria o que o schema declara, que é a deriva de três
cópias que §There is a THIRD copy documenta.

`plan-artifacts.md` §Fourteen canonical sections ganha a coluna `moment`. É o dono do contrato de
arquivo de uma spec, e §The template is duplicated on purpose é o aviso que a edição respeita: são
**três** cópias do template e a terceira sombreia em vez de servir de fallback.

### 2. Um `docs/standards/` declarado pode carregar um endereço — e isso custa zero de código

A pergunta do item 4 do `## Problem` era o que um executor precisa de um standard vinculante. As
quatro formas, medidas:

| Forma | Rende | Por que ganha ou perde |
| --- | --- | --- |
| arquivo inteiro (hoje) | — | nunca lê contrato pela metade; é o piso, e é caro |
| `--rules-only` | **inviável** | **2 de 41** arquivos de `docs/standards/` carregam o marcador (contra 5 de 23 nas referências). Estender é recusado pelo `## Out of Scope` |
| resumo normativo por standard | −? | artefato novo, custo permanente, e deriva da fonte sem sinal |
| **`§`endereço declarado no `## Impact`** | até −49% no arquivo endereçado | **escolhida** |

A escolha inverte quem decide. Um executor que escolhe seções está adivinhando quais partes de um
contrato o governam; o **autor da spec** sabe, porque foi ele que declarou o standard. Então a
declaração passa a poder carregar o endereço:

```markdown
### Standards this spec will write into docs/standards/

- `docs/standards/automation/context-budget.md` §The two caps §The per-surface ceiling — revisado.
- `docs/standards/workflows/plan-artifacts.md` — revisado, sem endereço: o executor lê inteiro.
```

**Sem endereço, o executor lê o arquivo inteiro.** O default é o comportamento de hoje, então
nenhuma leitura fica silenciosamente pela metade: ler menos é uma afirmação que alguém escreveu, não
uma economia que o executor tomou sozinho.

Custa **zero** de código, e isso foi provado, não presumido: `parse_impact_standards` roda
`STANDARD_PATH_RE.finditer` sobre cada bullet e devolve o caminho ignorando o resto da linha —
`['docs/standards/automation/context-budget.md', 'docs/standards/workflows/plan-artifacts.md']` para
o bloco acima. `sp-impact-uncovered` continua funcionando sem uma linha de mudança.

### 3. O passo 4 monta sua lista de seções a partir do `status` que o passo 2 já leu

O item 6 do `## Problem` perguntava se `specs.py section` muda a semântica do `exit 1` ou se o corpo
explica que ele é normal. **Nenhum dos dois.** O passo 2 já roda
`specs.py status --spec "<slug>" --json` — "que o passo 3 lê de qualquer jeito, então é lido aqui uma
vez" — e o payload carrega `sections[].state` por seção. O passo 4 pede as seções do conjunto
`build` **que o `status` reportou `filled`**.

`exit 1` por seção ausente deixa de acontecer em vez de ser explicado. Nenhum consumidor do exit code
é arrastado, nenhuma linha de ressalva entra no corpo, e uma seção ausente também para de ser paga.

### 4. Toda citação de referência num corpo de comando é um endereço `§`

`context-discipline.md` §Open less regra 2 hoje afirma: *"Every citation in this repository is already
written `§Section name` — the address exists; what was missing was the resolver."* O item 1 do
`## Problem` mede que isso é **falso** — seis citações em `execute.md` nomeiam só o arquivo. A
afirmação vira a regra: uma citação de referência num corpo de comando **é** um endereço `§`, e um
caminho nu é um finding, não um estilo.

A regra é escrita como regra **da superfície inteira** — um contrato que vale para um comando só não é
um standard. Ela é **provada** em um, que é onde a medição existe; converter os outros vinte e cinco é
o próximo spec, e o `## Out of Scope` já recusa fazê-lo aqui.

**Um endereço é completo ou não é um endereço.** O item 7 do `## Problem` mede o espelho do item 1:
cinco `§`endereços sem arquivo, dois `§<dígito>` que apontam para passos deste corpo, e dois endereços
partidos por quebra de linha. A regra tem três metades, e as três existem para a mesma coisa — que a
citação seja resolvível por quem lê **e** por um comando:

1. Todo `§`endereço carrega o arquivo a que pertence, no mesmo link ou colado nele.
2. Um endereço nunca é partido por quebra de linha.
3. Um passo deste corpo é referido por `passo 5g`, nunca por `§5g` — o `§` fica reservado para seção
   de arquivo, com um sentido só.

É a regra 1 que torna a `## Validation` possível: sem ela, "esta citação resolve?" não tem resposta
mecânica, porque não há como saber em que arquivo procurar.

Sobe junto a segunda regra que o item 2 mede: **uma referência que só serve a um ramo condicional é
lida naquele ramo, não no preâmbulo.**

### 5. O corpo é reduzido por relocação, e a conta movível é menor que 3.020

Medido: 6 dos 65 blocos do corpo são racional, **3.020 chars (13%)**. Contra o preâmbulo de ~103.000
pós-cortes isso é **−2,9%** — resíduo, e a decisão de fazê-lo mesmo assim é do humano, registrada
aqui com o custo à vista.

A conta honesta é menor que 3.020, porque **três dos seis blocos intercalam regra e racional** e não
podem se mover inteiros:

| bloco | chars | movível |
| --- | ---: | --- |
| `**Why \`Bash\` is unrestricted here.**` | 279 | inteiro |
| `**No mechanical net for a contract nobody declared**` | 695 | ~520 — a regra operativa é uma linha |
| `**Not after every committed task.**` | 430 | ~380 — a cadência é a regra |
| `**This command stops at the last commit.**` | 418 | ~200 — a fronteira é regra |
| o bloco de `docs/standards/` do passo 4 | 788 | ~330 — a instrução é regra |
| o fallback de `skills.py read` | 410 | ~90 — a escada é regra |

**~1.900 de 3.020.** O destino é `execution.md` sob `<!-- rationale -->`, e a task não **afirma** o
número: ela mede o corpo antes e depois e reporta o que de fato saiu.

## Alternatives Considered

Cinco formas de atacar o mesmo preâmbulo. Cada uma está escrita como seu melhor advogado a
escreveria; a recusada que não sobrevivesse a isso não era alternativa e não está na tabela.

| Forma | Custa | Compra | Fecha a porta para |
| --- | --- | --- | --- |
| **A. Não fazer nada** | zero | risco zero no comando que constrói toda spec | nada — os itens continuam medidos e disponíveis |
| **B. Só os itens 1 e 2** | ~2 tasks, nenhum standard revisado | **−53.900 chars** no turno 1 | nada; 3 e 4 seguem disponíveis |
| **C. Itens 1–4 + relocação do corpo** *(escolhida)* | ~5 grupos de tasks, 2 standards revisados, 3 cópias de template | **−58.165 garantidos** mais o que o endereço e a relocação renderem | nada |
| **D. A superfície inteira de uma vez** | 26 corpos editados numa branch | 25× o benefício | a medição — ela existe para um comando só |
| **E. Um mecanismo genérico de corte** | um hook que reescreva o que o modelo lê | corte automático, sem editar corpo | — |

**A — não fazer nada.** O preâmbulo fica em 160.856 chars (~40,2k tokens) pagos antes da primeira
linha de código e re-enviados em todo turno. É defensável: `read-by-section` acabou de mexer neste
mesmo comando, e um segundo spec sobre ele em dois dias é uma superfície instável. *Perde* porque os
itens 1 e 2 não envolvem julgamento nenhum — um caminho vira um endereço, uma referência de ramo
condicional é lida no ramo — e deixar 53.900 chars por turno na mesa por medo de mexer é o custo
recorrente vencendo um risco pontual.

**B — o menor que funcionaria.** Converter as seis citações e descer as duas referências
condicionais. Não toca no passo 4, não revisa standard nenhum, não muda a forma do `## Impact`.
Rende **93%** do corte garantido de C por **~40%** do trabalho, e é a alternativa mais forte da
tabela. *Perde por pouco*, e por uma razão que não é de tokens: deixa a regra de audiência como
prosa que ninguém aplica e deixa `## Out of Scope` sem chegar ao executor — que é o defeito de
correção, não de custo, que o item 3 encontrou.

**C — escolhida.** Itens 1–4 mais a relocação do corpo. O corte garantido é **161.256 → 103.091
chars (−36%)**, e sobre isso o endereço declarado e a relocação rendem o que renderem, sem promessa.

**D — generalizar agora.** A doutrina de citação vale para todo comando que cita uma referência, e
aplicá-la nos vinte e seis de uma vez multiplica o benefício. *Perde* porque a medição existe para
**um** comando: o número de qualquer outro seria estimativa, e este front já recusou estimativa uma
vez (os 25–35% de racional que a medição derrubou para 7%). E vinte e seis corpos numa branch é
exatamente o raio de explosão que o `## Out of Scope` recusa.

**E — comprar em vez de construir.** Um mecanismo genérico que corte contexto em runtime, sem editar
corpo nenhum. *Perde* por não existir: o que o corpo faz é **instruir um modelo sobre o que abrir**, e
nenhum hook do Claude Code intercepta isso. Mesmo se existisse, seria mágica invisível por cima de um
prompt explícito — o oposto do que `context-discipline.md` está construindo.

## Open Decisions

As cinco foram fechadas na passada adversarial de 2026-08-02. Ficam registradas com onde cada uma
caiu, porque a decisão é o que a próxima pessoa vai querer ler — não o fato de ter havido uma.

1. **Qual é a frente humana de uma spec?** — **Fechada pelo humano.** A hipótese de que ela é "bem
   menor" não sobreviveu à medição: o corte que a binária do template sugere rende −14%. A binária
   virou um eixo de três valores por **momento** — `decision` / `build` / `close` — e o passo 4 lê o
   conjunto `build`. `## Design` §1.

2. **O que um executor precisa de um `docs/standards/` declarado?** — **Fechada pela avaliação, com a
   conta.** `--rules-only` é inviável (2 de 41 arquivos carregam o marcador); resumo normativo é
   artefato novo que deriva da fonte. Escolhido: o `## Impact` pode carregar um `§`endereço, o default
   segue o arquivo inteiro, e custa **zero** de código — provado contra `parse_impact_standards`.
   `## Design` §2.

3. **O corpo do comando é reduzido aqui?** — **Fechada pelo humano: sim.** Contra a recomendação, que
   media −2,9% e pedia adiamento. A conta movível honesta é **~1.900 de 3.020 chars**, porque três dos
   seis blocos intercalam regra e racional, e a task mede em vez de afirmar. `## Design` §5.

4. **`specs.py section` muda a semântica do `exit 1`, ou o corpo explica?** — **Fechada: nenhum dos
   dois.** O passo 2 já lê `status --json`, que carrega `sections[].state`; o passo 4 pede só as
   seções `filled`. O `exit 1` deixa de acontecer em vez de ser explicado, e nenhum consumidor do exit
   code é arrastado. `## Design` §3.

5. **A doutrina de citação vale para os outros vinte e cinco comandos?** — **Fechada: o standard a
   escreve como regra da superfície inteira, provada em um comando.** Um contrato que vale para um
   comando só não é um standard. Converter os outros vinte e cinco segue em `## Out of Scope`.
   `## Design` §4.

**Nada em aberto.** Uma decisão nova que aparecer durante a construção entra por
`specs.py discover`, não aqui.

## Risks

Gerados pelo enquadramento *"é daqui a três meses, isto foi construído e deu errado — o que
aconteceu?"*, a partir do conteúdo deste spec e não de uma lista genérica. Cada história virou uma
coisa só: risco com mitigação nomeada, risco aceito com a razão, ou task de mitigação. As que não
viraram nada foram derrubadas e estão ditas.

- **Um executor obedece metade de um contrato vinculante.** O `§`endereço de um standard declarado é
  escrito pelo autor da spec; um autor que endereça estreito demais faz o executor cumprir metade de
  um contrato **sem sinal nenhum de que faltou**. Probabilidade média, dano alto, e a detecção é ruim
  — só a revisão de branch pega. *Mitigação nomeada:* o default é o arquivo inteiro. O endereço é
  opt-in e `context-discipline.md` escreve que ele é uma **afirmação que o autor faz**, nunca uma
  economia que o executor toma. Um standard sem endereço lê como hoje.

- **Uma task fica ambígua sem `## Problem`.** O executor perde o *porquê* e não consegue desempatar o
  que a task quer. *Aceito, com a razão:* `## Out of Scope` entra no conjunto `build` e é o
  instrumento mais afiado para o mesmo problema, e o passo 5 do comando já tem o caminho de parada
  ("a task is unclear → pause"). A saída de uma ambiguidade é uma pausa, não um palpite, e essa
  saída já existe.

- **A relocação leva uma regra junto com o racional.** Três dos seis blocos intercalam os dois; um
  movimento descuidado tira uma regra do prompt e a esconde num arquivo que o preâmbulo nem sempre
  abre. Detecção fraca: o corpo continua parecendo certo. *Vira task de mitigação:* a task move
  **apenas** os seis blocos nomeados no `## Design`, mantém a metade-regra de cada um no corpo, e o
  `verify:` mede o corpo antes e depois **e** afirma que as sentenças-regra seguem presentes.

- **Um `§`endereço apodrece quando uma referência é re-titulada.** Uma citação que nomeia uma seção
  que não existe mais recusa com `exit 2` no turno 1. *Aceito, e a detecção é a mitigação:* falha
  alta e imediata, no primeiro turno, antes de qualquer código. Um endereço podre é melhor que um
  caminho de arquivo que sempre "funciona" trazendo cinco vezes o necessário. Um check de `skills.py
  lint` sobre citações é follow-up, não este spec.

- **O defeito da vírgula morde uma citação nova.** `skills.py read --sections` quebra o valor em
  vírgulas incondicionalmente, então **sete** seções das cinco referências — três das dez de
  `execution.md` — recusam com `exit 2` quando endereçadas pelo nome completo, incluindo a maior
  (`§The commit — one per task, carrying its own ticked box`, 4.638 chars). Um prefixo que pare antes
  da vírgula resolve, e o exemplo `§The commit` do próprio corpo funciona por sorte. Pior: a mensagem
  de erro lista a seção recusada em `available:`. *Vira task de mitigação:* toda citação nova é
  escrita em forma de prefixo e uma task prova que cada `§` do corpo resolve `exit 0`. O conserto do
  `--sections` em si é **follow-up spec** — mesma família do
  `fix-the-files-field-parser-splitting-on-commas-inside-parentheses` que já está em `plans/`.

- **Descer `homes.md`/`conformance.md` para o 5c faz uma task de `docs/` pagar uma leitura no meio da
  run.** *Aceito, com a conta:* na spec de referência são 3 de 15 tasks. Hoje se paga 18.426 chars
  **em todo turno**; depois, 18.426 chars **três vezes**. A troca só perderia numa spec em que quase
  toda task escreve `docs/`, e nessa o preâmbulo nunca foi o problema.

**Derrubadas, e por quê.** *"O corte quebra uma run em andamento"* — não vira nada: o corpo é lido no
turno 1 e nenhuma run atravessa uma edição de comando, porque a superfície é montada no início da
sessão. *"O executor fica sem `## Risks`"* — não vira nada: nenhum risco desta lista é acionável por
uma task; os que são viram task, e é assim que o premortem converte.

## Handoff

**Nada construído.** Nenhuma task rodou, nenhum commit existe, a árvore está limpa. O spec foi
definido em duas passadas de `/quenching:specs:develop` em 2026-08-02 — adversarial e gate — e espera
o `approved` do humano.

**O que quem começar precisa saber antes da tarefa 0.1:**

- **A ordem não é arbitrária.** Grupos 1 e 2 não têm julgamento nenhum (um caminho vira endereço, uma
  referência de ramo condicional desce para o ramo) e por isso vêm antes do grupo 3, que escreve a
  política que eles provaram. Mesma forma nos grupos 4–6 contra o 7.
- **Cinco dos nove grupos editam `commands/specs/execute.md`.** Nenhum `[P]`, e o arquivo é o mesmo o
  tempo todo — um rebase no meio do caminho custa caro.
- **Este spec edita o comando que constrói specs.** A superfície é montada no início da sessão, então
  nenhuma edição em `commands/**` é testável na sessão que a escreve. O que prova cada task é o
  `verify:` dela, não a run em andamento.
- **A convenção de contagem de 0.1 é pré-requisito de 9.1.** Sem o par medido sob a mesma convenção, a
  afirmação de −36% não é verificável — e é a afirmação central do spec.
- **`assets/checks/functional-checks.sh` não entra em `verify:` nenhum**, por
  [surface-verification.md](/docs/standards/quality/surface-verification.md). Ele é da front de skill.

## Tasks

Ordenado por `## Design`: medir com uma convenção só, converter o que não tem julgamento, escrever a
política que aquilo provou, só então mexer no que depende de decisão. `SP` abaixo é
`python3 plugins/quenching/assets/bin/specs.py` e `SK` é `python3 plugins/quenching/assets/bin/skills.py`.

Nenhuma tarefa carrega `[P]`: os grupos 1, 2, 5, 6 e 8 editam o **mesmo** arquivo
(`commands/specs/execute.md`), e as dos grupos 3 e 7 escrevem em `docs/`, que `specs.py parallel`
nunca considera elegível.

### 0. Fixar a convenção de contagem antes de qualquer edição

- [x] 0.1 Fixar a convenção de contagem (com ou sem frontmatter, e quais itens entram) e refazer o
      **antes** dos oito itens da `## Validation` sob ela, corrigindo a divergência de 0,25% entre os
      161.256 daquela seção e os 160.856 do `## Problem`. Registrar a convenção no corpo do commit —
      o número de uma ponta só não vale nada, e é o par que a tarefa 9.1 vai comparar.
      files: (nenhum — medição; o resultado vive no commit e é relido por 9.1)
      verify: os oito itens somados batem com o total registrado, e a mesma convenção é aplicável a
      subject: plan/narrow-the-execute-preamble: 0.1 Fixar a convenção de contagem e refazer o antes
      cada um deles isoladamente

### 1. Toda citação vira um endereço completo

- [x] 1.1 Converter as seis citações do preâmbulo de topo em endereços `§`, nomeando as seções que o
      próprio texto já enumera, em **forma de prefixo** que pare antes de qualquer vírgula — sete
      seções das cinco referências recusam com `exit 2` pelo nome completo (`## Risks`). As seções
      alvo e os tamanhos estão na tabela do `## Problem` item 1.
      files: plugins/quenching/commands/specs/execute.md
      verify: uma chamada `SK read <referência> --sections "§…"` por referência citada, com
      subject: plan/narrow-the-execute-preamble: 1.1 Converter as seis citações do preâmbulo em endereços
      exatamente os endereços que o corpo passou a carregar, **todas saindo 0**
- [x] 1.2 Completar os endereços que o `## Problem` item 7 mede: dar arquivo aos cinco `§` que não
      têm (`:208`, `:217`, `:240`, `:271`, `:363`), juntar os dois que quebram linha no meio do
      endereço (`:92`, `:101`), e trocar `§6`/`§5g` por `passo 6`/`passo 5g` — o `§` fica com um
      sentido só, seção de arquivo.
      files: plugins/quenching/commands/specs/execute.md
      verify: `grep -c "§" plugins/quenching/commands/specs/execute.md` bate com o número de endereços
      subject: plan/narrow-the-execute-preamble: 1.2 Completar os endereços sem arquivo, quebra de linha e §<dígito>
      cobertos pelas chamadas de 1.1; zero `§` sem arquivo e zero `§<dígito>`

### 2. A referência de ramo condicional é lida no ramo

- [x] 2.1 Descer o carregamento de `homes.md` e `conformance.md` do preâmbulo de topo para o passo 5c,
      onde já são citadas, e deixar o topo sem menção a elas. São 18.426 chars que hoje todo turno
      paga e que passam a ser lidos só nas tasks que escrevem `docs/`.
      files: plugins/quenching/commands/specs/execute.md
      verify: `grep -n "homes.md\|conformance.md" plugins/quenching/commands/specs/execute.md` só
      subject: plan/narrow-the-execute-preamble: 2.1 Descer homes.md/conformance.md para o passo 5c
      devolve linhas dentro do passo 5c

### 3. Escrever a doutrina de citação no dono dela

- [x] 3.1 Revisar `docs/standards/automation/context-discipline.md` §Open less: a regra 2 hoje
      **afirma** que toda citação do repositório já é um `§`endereço, o que os itens 1 e 7 do
      `## Problem` medem ser falso. A afirmação vira regra da superfície inteira, com as três metades
      do `## Design` §4 (o endereço carrega o arquivo, não quebra linha, e `§` só significa seção de
      arquivo) mais a regra de que uma referência de ramo condicional é lida naquele ramo. Citar os
      grupos 1 e 2 como a prova, em um comando. Mantém `authority: background`.
      files: docs/standards/automation/context-discipline.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
      subject: plan/narrow-the-execute-preamble: 3.1 Revisar context-discipline.md §Open less regra 2

### 4. O eixo `moment` substitui o `audience` morto

- [x] 4.1 Trocar `audience` por `moment` (`decision` / `build` / `close`) nas quatorze seções, em
      **lockstep de três arquivos** — `DEFAULT_SCHEMA` em `specs.py`, `assets/specs/schema.json` e o
      comentário de audiência do template — pelos valores da tabela do `## Design` §1.
      `plan-artifacts.md` §There is a THIRD copy é o aviso: mudar só a constante é invisível no layout
      que o plugin shipa.
      files: plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/specs/schema.json, plugins/quenching/assets/specs/templates/spec.md
      verify: python3 plugins/quenching/assets/bin/specs.py selftest
      subject: plan/narrow-the-execute-preamble: 4.1 Trocar audience por moment nas quatorze seções
- [x] 4.2 Dar a `specs.py section` a opção `--moment <valor>`, que resolve a lista de headings pelo
      schema em vez de recebê-la enumerada, mantendo a forma por lista intacta. Entregar junto o caso
      de `selftest` que prova que `--moment build` devolve exatamente as seis seções da tabela —
      sem ele a regra fica sendo prosa outra vez, que é o defeito que este grupo existe para tirar.
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py selftest
      subject: plan/narrow-the-execute-preamble: 4.2 Dar a specs.py section a opção --moment

### 5. O passo 4 lê o conjunto `build`

- [x] 5.1 Reescrever o passo 4 para pedir `SP section "<slug>" --moment build`, restrito às seções que
      o `sections[].state` do `status` do passo 2 já reportou `filled`. Some `## Problem`, entra
      `## Out of Scope`, e o `exit 1` por seção ausente deixa de ser alcançável — sem ressalva no
      corpo e sem tocar na semântica do exit code.
      files: plugins/quenching/commands/specs/execute.md
      verify: o corpo não enumera heading nenhum no passo 4; `SP section <slug> --moment build` sai 0
      subject: plan/narrow-the-execute-preamble: 5.1 Passo 4 lê o conjunto build via --moment
      contra uma spec com as seis preenchidas

### 6. Um standard declarado pode carregar um endereço

- [x] 6.1 Fazer o passo 4 honrar um `§`endereço escrito ao lado de um caminho na sub-heading parseada
      do `## Impact`, **lendo o arquivo inteiro quando não houver endereço**. Nenhuma mudança em
      `parse_impact_standards`: medido, ele já tolera o sufixo e devolve o caminho nu.
      files: plugins/quenching/commands/specs/execute.md
      verify: python3 plugins/quenching/assets/bin/specs.py validate — 0 error(s), nenhum
      subject: plan/narrow-the-execute-preamble: 6.1 Passo 4 honra um §endereço no Impact
      `sp-impact-uncovered` novo
- [x] 6.2 Provar a tolerância por caso de `selftest`, contra um `## Impact` com endereço em um standard
      e sem endereço no outro. Provar editando a superfície real seria provar por coincidência.
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py selftest
      subject: plan/narrow-the-execute-preamble: 6.2 Provar a tolerância ao §endereço por selftest

### 7. Escrever o contrato de arquivo que os grupos 4–6 provaram

- [x] 7.1 Revisar `docs/standards/workflows/plan-artifacts.md`: §Fourteen canonical sections ganha a
      coluna `moment` com um valor por seção; §`## Impact` carries one parsed sub-heading ganha a forma
      opcional do `§`endereço e a nota de que o parser já a tolera; §There is a THIRD copy ganha o
      schema `moment` na lista do lockstep.
      files: docs/standards/workflows/plan-artifacts.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
      subject: plan/narrow-the-execute-preamble: 7.1 Revisar plan-artifacts.md com o eixo moment
- [x] 7.2 Alinhar `specs-develop/spec-driven.md` — §The fourteen sections recebe o eixo de momento,
      §The executor contract passa a nomear o conjunto `build`, e §`## Impact` — the one parsed
      declaration ganha a forma do endereço.
      files: plugins/quenching/assets/references/specs-develop/spec-driven.md
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json
      subject: plan/narrow-the-execute-preamble: 7.2 Alinhar spec-driven.md com moment e o endereço

### 8. Relocar o racional do corpo

- [ ] 8.1 Mover para `execution.md`, sob `<!-- rationale -->`, o racional dos seis blocos nomeados na
      tabela do `## Design` §5, **mantendo no corpo a metade-regra dos três que intercalam** os dois.
      A tarefa **mede** o corpo antes e depois e reporta o que de fato saiu; a estimativa de ~1.900 de
      3.020 é ponto de partida, não meta.
      files: plugins/quenching/commands/specs/execute.md, plugins/quenching/assets/references/specs-execute/execution.md
      verify: as sentenças-regra dos três blocos intercalados seguem presentes no corpo, e o delta
      medido é reportado no commit

### 9. Fechar a medição

- [ ] 9.1 Refazer o **depois** dos oito itens sob a convenção fixada em 0.1 e registrar o par
      antes/depois. Um número estimado em qualquer uma das pontas é falha da tarefa.
      files: (nenhum — medição; o par vai para o commit e para o `## Outcome` em `/specs:conclude`)
      verify: o total do depois bate item a item com a `## Validation`, e a diferença contra o
      garantido de 103.091 é explicada item a item, não arredondada
- [ ] 9.2 Rodar a bateria de integridade da superfície e reportar: lockstep de `VERSION` contra os três
      scripts, `okf-validate.py assets/docs` e `okf-validate.py docs`, `doctor`, `lint` e os três
      `selftest`.
      verify: 0 error(s) nos dois `okf-validate`, `doctor` com 26 comandos e 0 findings, `lint` em
      exit 0, os três `selftest` passando
