---
slug: collapse-remaining-language-clause-restatements
title: Collapse Remaining Language Clause Restatements
verification: per-section
refined: {mode: gate, date: 2026-07-31}
approved: {date: 2026-07-31}
---

# Collapse Remaining Language Clause Restatements

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

O dano das reenunciações da cláusula da língua não é haver treze cópias — é elas **divergirem**, e
duas já divergiram em semanas: `assets/README.md` estreita a regra a `audience: human`, redação que
o spec anterior removeu dos dois `index.md`, e a nota de `okf-spec.md` afirma um colapso total que
não aconteceu. Nenhum validador pega qualquer uma: `plugin-layout.md` registra que uma citação
pendurada lê como prosa comum.

Então este spec não conta cópias. Ele aplica o teste que já existe — **uma cópia disto sai do
plugin?** — categoria por categoria, e o resultado desmonta a dicotomia do censo original: só
**três** locais saem de fato, todos do front `specs/`, que roda em repositório sem bundle algum. Os
outros dez ficam dentro, e o que enunciam não é a regra da língua e sim a fronteira estrutura/prosa,
cujo dono é `naming/command-surface.md` e que precisa estar em contexto no instante em que um slug é
escrito.

O trabalho, portanto: corrigir as duas divergências, dar aos três que saem uma nota inline no molde
do precedente de `okf-spec.md` — nomeando o dono e a razão de não citar —, reler os dez lembretes
para que nenhum estreite a regra, e sincronizar a cópia instalada de `specs/QUENCHING.md`, que está
atrás do mold.

Uma única adição a `docs/standards/`, e ela é uma emenda: `plugin-layout.md` — o doc cujo
`resource:` já cobre os dez — ganha o teste que distingue um lembrete de fronteira de uma
reenunciação, porque sem ele a próxima passagem de colapso não tem como saber que os dez ficam por
decisão. O critério de *citar versus autocontido* continua sendo o que já estava escrito ali; nenhum
doc novo, nenhum segundo dono.
## Problem

O spec `declare-repo-body-language` instalou o dono único da regra de língua em
`docs/standards/agents/communication.md` e colapsou **seis** reenunciações — as normativas, que
vivem em `docs/` e `plugins/quenching/assets/references/`. Ele deliberadamente deixou as demais de
fora e registrou o censo em seu `## Open Decisions`, sob a hipótese de que as restantes eram ou
texto de template entregue ou condição lateral dentro de um body de comando.

**Essa hipótese não sobrevive ao disco, e o censo transcrito também não.** A reconferência está em
`## Design`: as linhas mudaram, dois locais faltavam no censo, os molds de harness não são texto
entregue — vivem dentro de uma nota `MOLD … do NOT copy this note into the produced file` — e só
três locais de fato saem do plugin.

**E o dano real é outro.** Duas das cópias já divergiram do dono: `plugins/quenching/assets/README.md`
estreita a regra a `audience: human`, exatamente a redação que a task 4 do spec anterior removeu dos
dois `index.md`; e a nota deliberada de `plugins/quenching/assets/references/docs-align/okf-spec.md`
afirma que todo o resto foi colapsado em citação, com dez lembretes vivos por decisão. Nenhum
validador pega qualquer uma das duas — `docs/standards/architecture/plugin-layout.md`
§*A mold cites nothing it does not also install* registra que uma citação pendurada lê como prosa
comum.

**A restrição que o spec anterior já descobriu:** as gêmeas de template obrigam edição em par —
`plugins/quenching/assets/bin/specs.py` e `plugins/quenching/assets/specs/templates/spec.md`
carregam o mesmo texto sob a regra "edit both or neither".

**E a restrição que a revisão de branch daquele spec acrescentou:** um artefato que um align copia
para o repositório-alvo **não pode citar o que a cópia não instala**. É essa regra — não uma nova —
que decide este spec, categoria por categoria.

## Proposal

Este spec não conta cópias; ele decide, corrige o que divergiu, e deixa a razão legível onde a
tentação de "reconciliar" aparece.

**O teste é um só, e já existe:** `docs/standards/architecture/plugin-layout.md`
§*A mold cites nothing it does not also install* — *uma cópia disto sai do plugin, para um
repositório que pode não ter o bundle?* Aplicado ao censo reconferido, ele parte os treze locais em
dois grupos de tamanhos que ninguém previu: **três** saem, **dez** não.

**Os três que saem conservam o enunciado, e ganham uma nota.** São todos do front `specs/` —
`assets/specs/templates/spec.md`, `assets/bin/specs.py` (a gêmea) e `assets/specs/QUENCHING.md`.
`/specs:align` é inteiramente nativo e roda em repositório que nunca adotou o bundle, então uma
citação a `docs/standards/agents/communication.md` ali é a violação literal daquela regra. Cada um
passa a carregar uma nota inline no molde do precedente que `okf-spec.md` já estabeleceu: nomeia o
dono, diz por que este local não cita, e é isso.

**Os dez que não saem ficam como estão — porque não são reenunciação da regra.** Eles enunciam a
**fronteira** estrutura-canônica / prosa-local, cujo dono é
`docs/standards/naming/command-surface.md`, e o valor deles é estar em contexto no instante em que
um slug é escrito. Trocá-los por uma citação custa uma tool call exatamente ali, contra o argumento
*uma linha, zero tool calls* que escolheu a forma do mecanismo. O trabalho neles é negativo:
garantir que nenhum **estreite** a regra.

**Duas correções de drift comprovado.** `plugins/quenching/assets/README.md` deixa de limitar a
regra a `audience: human`. A nota de `okf-spec.md` deixa de afirmar que todo o resto foi colapsado e
passa a dizer o que é verdade: os enunciados normativos foram colapsados, e os lembretes de
fronteira permanecem por decisão.

**E a cópia instalada é sincronizada.** `specs/QUENCHING.md` neste repositório está atrás do mold —
anuncia treze headings canônicos contra quatorze — e carrega a mesma cláusula. É drift de
reinstalação, não de reenunciação, mas é o mesmo arquivo do censo e fica dentro.

**Nada novo em `docs/standards/`.** O critério já tem dono; escrevê-lo uma segunda vez seria, uma
camada acima, o defeito que este spec existe para curar. Depois disto o censo está fechado: cada
local ou cita o dono, ou carrega por escrito a razão de não citar.

## Out of Scope

- **Os 48 specs sob `specs/plans/` e `specs/archive/`.** Cada um carrega o comentário de guidance do
  template, com a cláusula congelada na data de criação. Editar o mold não retroage a nenhum deles,
  e eles são registro histórico — a cláusula ali nunca foi lida como normativa.
- **Colapsar os dez lembretes de fronteira em citações.** Decidido contra, com a razão em
  `## Design`: eles enunciam a fronteira, não a regra, e o custo é uma tool call no pior momento.
- **Uma regra nova sobre quando um enunciado autocontido é legítimo.**
  `docs/standards/architecture/plugin-layout.md` §*A mold cites nothing it does not also install* já
  é essa regra, e já declara que uma árvore acrescentada depois a herda sem emendar a lista. O que
  este spec acrescenta àquela mesma seção é outra pergunta, que ninguém possui hoje: se um lembrete
  de fronteira conta como reenunciação. Ver `## Impact`.
- **Traduzir a prosa em inglês já escrita.** Herdado de `declare-repo-body-language`: declarar uma
  tag não retraduz o que existe. É migração, e é outro trabalho.
- **Enforcement por máquina.** Nenhum validador identifica a língua de um documento nem resolve uma
  citação em prosa; é por isso que a nota no local é a detecção, e não um check.
- **Reabrir os seis locais que `declare-repo-body-language` já colapsou.** Eles citam o dono e estão
  certos.
## Impact

**O que este spec toca.** A emenda em `docs/standards/architecture/plugin-layout.md` (declarada
abaixo); as duas gêmeas `plugins/quenching/assets/specs/templates/spec.md` e
`plugins/quenching/assets/bin/specs.py`; `plugins/quenching/assets/specs/QUENCHING.md`;
`plugins/quenching/assets/references/docs-align/okf-spec.md`;
`plugins/quenching/assets/README.md`; e `specs/QUENCHING.md`, a cópia instalada. Os dez lembretes de
fronteira da tabela de `## Design` são **lidos** na task 5 e só editados se estreitarem a regra —
`assets/README.md` é o único que hoje se sabe que estreita.

**A zona `GENERATED` de `docs/standards/index.md` não se move:** a emenda não acrescenta um doc, só
altera o corpo e o `timestamp:` de um existente. E `plugin-layout.md` **não tem gêmea no skeleton** —
`plugins/quenching/assets/docs/standards/architecture/` só carrega `index.md` —, então a emenda vive
em uma árvore só, ao contrário do que o spec anterior enfrentou com `communication.md`.

**Custo previsível e não silenciável:** o `resource:` de `plugin-layout.md` cobre
`plugins/quenching/assets/**`, e as tasks 2–5 escrevem ali. Ele vai acusar `stale-doc`. Neste spec o
`timestamp:` sobe legitimamente pela task 1, que edita o próprio doc — mas o ruído da baseline
permanece, e o critério é `0 error(s)` e nenhum finding novo, doc-a-doc.

### Standards this spec will write into docs/standards/

- `docs/standards/architecture/plugin-layout.md` — emenda à §*A mold cites nothing it does not also
  install*, acrescentando o teste que separa lembrete de fronteira de reenunciação: o **critério de
  propriedade** (um lembrete enuncia a fronteira da regra que o local já possui, vista do outro
  lado) e o **guarda-corpo verificável** (uma cláusula, nenhum fato que o dono enuncia, e jamais um
  estreitamento de escopo). Uma árvore só — o doc não existe no skeleton.

## Validation

- **O censo vivo.** `grep -rn -A1 "repo.s language" --include='*.md' --include='*.py' plugins/ docs/`
  devolve **exatamente** os quatorze locais da tabela de `## Design`. O `-A1` não é opcional: a
  ocorrência de `okf-spec.md` está quebrada por wrap e escapa a um padrão de uma linha — foi assim
  que o invariante do spec anterior deixou de medir o que afirmava. Um décimo-quinto acerto é
  reenunciação nova, e é falha. **Um acerto a menos também é falha**, porque este spec decidiu que
  os dez ficam.
- **As três notas existem.**
  `grep -n 'agents/communication.md' plugins/quenching/assets/specs/templates/spec.md plugins/quenching/assets/bin/specs.py plugins/quenching/assets/specs/QUENCHING.md`
  → um acerto em cada arquivo.
- **As gêmeas não se afastaram.** O diff dos dois blocos de guidance — de `THE STAGE-SCOPED
  EXPLICIT-NONE RULE` até o fim de `AUDIENCE` — é vazio entre `assets/bin/specs.py` e
  `assets/specs/templates/spec.md`. Este é o único invariante do spec que divergiria em silêncio, e
  ele é medido no limite da task 2 e em nenhum outro momento; ver `## Risks`.
- **Nenhum lembrete estreita a regra.**
  `grep -n 'audience: human' plugins/quenching/assets/README.md` não devolve nenhuma linha sobre a
  cláusula da língua. O escopo que o dono declara é toda prosa autorada pelo agente, e um lembrete
  que o reduz é o defeito nomeado em `## Problem`.
- **A nota de `okf-spec.md` diz a verdade.** Ela afirma que os enunciados **normativos** foram
  colapsados e que os lembretes de fronteira permanecem por decisão — não mais "every other
  statement of it in this plugin was collapsed into a citation", que era falso já quando foi escrito.
- **A cópia instalada está sincronizada.**
  `grep -n 'Fourteen canonical headings' specs/QUENCHING.md` → um acerto, e a nota da task 3
  presente nela.
- **O bundle continua conformante.** `python3 plugins/quenching/assets/hooks/okf-validate.py docs`
  reporta `0 error(s)` e **nenhum finding novo**, comparado **doc-a-doc** contra a mesma execução em
  `main` e nunca por contagem — a baseline já carrega 13–14 warnings `stale-doc` alheios, e
  silenciá-los com bump de `timestamp:` é a mentira que
  `narrow-the-stale-doc-trigger-to-content-drift` existe para evitar.

## Design

### O censo, reconferido no disco (2026-07-31)

O transcrito no `## Problem` original estava com linhas defasadas, faltavam dois locais e um deles
estava errado. Este é o estado medido, com o veredito de cada um:

| Local | Sai do plugin? | Veredito |
| --- | --- | --- |
| `assets/specs/templates/spec.md:39` | sim — `/specs:align` | conserva + nota (gêmea) |
| `assets/bin/specs.py:286` | sim — `/specs:align` | conserva + nota (gêmea) |
| `assets/specs/QUENCHING.md:380` | sim — `/specs:align` | conserva + nota · **fora do censo original** |
| `assets/templates/harness/claude-root.md:71` | **não** — nota `MOLD`, não copiada | lembrete de fronteira, fica |
| `assets/templates/harness/claude-subfolder.md:32` | **não** — idem | lembrete de fronteira, fica |
| `commands/docs/add.md:37` | não | lembrete de fronteira, fica |
| `commands/docs/align.md:79` | não | lembrete de fronteira, fica |
| `commands/docs/define.md:76` | não | lembrete de fronteira, fica |
| `commands/docs/learn.md:41` e `:79` | não | lembrete de fronteira, fica |
| `commands/docs/harness.md:143` | não | fica — já reescrito pela task 7 do spec anterior, carrega o KEEP junto |
| `plugins/quenching/README.md:401` | não | lembrete de fronteira, fica · **fora do censo original** |
| `assets/README.md:115` | não | **corrigir** — estreita a regra a `audience: human` |
| `assets/references/docs-align/okf-spec.md:113` | sim (format spec) | conserva — **corrigir a nota**, que afirma um colapso total falso |
| `specs/QUENCHING.md:355` | cópia instalada | **sincronizar** com o mold (treze headings vs quatorze) |

### Por que os molds de harness não contam como texto entregue

`assets/templates/harness/claude-root.md:62` abre com
`MOLD (quenching · root harness pointer — do NOT copy this note into the produced file)`. A cláusula
da linha 71 vive dentro dessa nota: ela instrui quem autora, e é descartada do arquivo produzido. O
`CLAUDE.md` deste repositório é a evidência — não carrega o bloco. É por isso que o teste "sai do
plugin?" responde **não** para os dois molds, contra o que o censo original assumia.

### A forma da nota

O precedente é `okf-spec.md`: um parêntese em itálico, imediatamente após a cláusula, que nomeia
`standards/agents/communication.md` como o dono e diz por que **este** local não defere a ele. Três
propriedades a fazem a escolha certa aqui: fica onde o drift ocorreria, não inventa um segundo dono
de regra, e é a única detecção possível — `plugin-layout.md` registra que nenhum validador pega uma
citação pendurada.

A razão dos três é a mesma e deve ser escrita como tal: o front `specs/` é nativo e roda em
repositório sem bundle, então o caminho não resolveria.

### A regra do par

`assets/bin/specs.py` e `assets/specs/templates/spec.md` carregam o mesmo bloco sob "edit both or
neither". A nota entra nos dois no mesmo commit, ou em nenhum.

## Alternatives Considered

| Abordagem | Por que perdeu |
| --- | --- |
| **Colapsar o máximo possível** — cada local é colapsável até prova em contrário | Trata o dano como contagem de cópias. As duas divergências reais que este spec encontrou não foram causadas por haver muitas cópias, e sim por ninguém saber se aquela cópia era legítima — que é exatamente o que colapsar cegamente não responde. Também introduziria dez citações que só resolvem depois que um align rodou. |
| **Colapsar os dez que não saem do plugin** | Defensável pelo teste, e rejeitada pelo que os dez de fato dizem: a fronteira estrutura/prosa, cujo dono é `naming/command-surface.md`. O valor deles é estar em contexto no instante em que um slug é escrito; uma citação ali custa uma tool call e contradiz o argumento *uma linha, zero tool calls*. |
| **Colapsar só os dois READMEs** | Meio-termo sem critério: os READMEs enunciam a mesma fronteira que os bodies, apenas para um leitor humano. Tratá-los diferente exigiria uma segunda regra para dizer quando o leitor muda o veredito. |
| **Uma regra nova no dono** — `communication.md` ganha uma linha sobre quando o autocontido é legítimo | Um ponto único de consulta, ao preço de um segundo enunciado de uma regra que `plugin-layout.md` já possui — o defeito deste spec, uma camada acima. Aquela seção já declara que uma árvore acrescentada depois herda a regra sem emendar a lista, então não há lacuna a preencher. |
| **Só a tabela de vereditos neste spec, sem notas** | O mais barato, e garante um terceiro spec: o censo fecharia como artefato arquivado, e quem editasse `spec.md` em seis meses não teria o que consultar no local. |
| **Puxar os 48 specs congelados para dentro** | 48 edições em registro histórico, para uma cláusula que ninguém lê como normativa ali. O mold não retroage a eles por construção, e isso é correto. |
| **Não fazer nada** | As duas divergências ficam. `assets/README.md` continua ensinando um escopo mais estreito do que o dono decidiu, e `okf-spec.md` — o documento que outros implementadores leem — continua afirmando um colapso que não aconteceu. |

## Open Decisions

- **O invariante das gêmeas ganha um check mecânico?** Este spec o prova por um diff rodado no
  limite da task 2; depois do arquivamento nada o roda. Uma asserção em `specs.py selftest` seria
  durável, e foi rejeitada aqui por proporção: custa código na ferramenta e entra no lockstep das
  sete surfaces, para um spec que são seis edições. **Como será decidido:** por um spec próprio, e o
  gatilho é factual — a primeira vez que as duas gêmeas forem encontradas divergentes.
- **Nada nota um manual instalado atrasado.** `specs/QUENCHING.md` estava atrás do mold — treze
  headings contra quatorze — e nenhuma máquina notou: `QUENCHING.md` é `EXEMPT` em
  `okf-validate.py`, e o refresh só ocorre quando alguém roda `/specs:align`. O spec irmão
  `notice-installed-tool-version-drift` resolveu a classe vizinha e não esta: ferramentas têm
  `--version` e lockstep, um manual não tem nenhum dos dois. Este spec conserta a instância e não
  opina sobre a classe. **Como será decidido:** por um spec de follow-up, que precisa primeiro
  dimensionar quantos artefatos de payload não-ferramenta existem.

## Risks

- **A emenda vira licença para duplicar qualquer coisa.** "Um lembrete de fronteira não é
  reenunciação" é uma frase que, lida frouxo, absolve toda cópia — e `assets/README.md` mostra a
  forma exata que o abuso toma: um lembrete que acrescentou um fato (`audience: human`) e com isso
  estreitou a regra vizinha. **Mitigação nomeada:** a emenda carrega os dois testes, não a frase. O
  critério de propriedade diz por que a fronteira é legítima; o guarda-corpo verificável — uma
  cláusula, nenhum fato do dono, nenhum estreitamento — é o que alguém aplica a um caso concreto, e
  é o único dos dois que teria pegado o defeito que este spec encontrou.
- **A nota é apagada por uma passagem de emagrecimento.** Um parêntese em itálico é exatamente o que
  uma varredura de concisão trata como resíduo colapsável, e nenhum validador nota a falta — é o
  mesmo modo de falha que o spec anterior registrou para a linha do harness, que precisou de uma
  task inteira ensinando `/docs:harness` que ela é KEEP. **Aceito, com a detecção nomeada:** o
  segundo bullet de `## Validation` é a única detecção que existe, e ele só roda quando alguém o
  roda. A mitigação real é a nota dizer *por que* inline, de modo que apagá-la exija ler a razão.
- **As gêmeas se afastam depois do arquivamento.** O diff roda no limite da task 2 e nunca mais.
  **Risco aceito**, com a alternativa registrada em `## Open Decisions` e o gatilho que a reabre.
- **A tabela de `## Design` defasa.** Os números de linha morrem na primeira edição acima deles —
  foi assim que o censo do spec anterior envelheceu, e é por isso que este spec teve de reconferir
  tudo. **Mitigado por construção:** o invariante é o grep do primeiro bullet de `## Validation`,
  não a tabela; a tabela nomeia arquivos e vereditos, e as linhas são conveniência datada.
- **`plugin-layout.md` acusa `stale-doc` por causa deste spec.** O `resource:` dele cobre
  `plugins/quenching/assets/**` e as tasks 2–5 escrevem ali. Neste caso o `timestamp:` sobe
  legitimamente, porque a task 1 edita o próprio doc — mas não confunda isso com licença para
  silenciar o ruído da baseline com bump de timestamp em outros docs.

## Tasks

Ordenadas, e a ordem é load-bearing três vezes: a task 1 escreve o critério antes de a task 5
aplicá-lo; a task 2 é **um** commit, porque as gêmeas editam em par ou não editam; e a task 6 vem
depois da task 3, ou a cópia instalada é sincronizada duas vezes. A task 1 nomeia seu caminho
`docs/standards/**` na própria linha do checkbox, porque `sp-impact-uncovered` casa com aquela linha
e não com a continuação `files:`.

- [x] 1 Emendar `docs/standards/architecture/plugin-layout.md` §A mold cites nothing it does not
  also install com o teste que separa lembrete de fronteira de reenunciação — o critério de
  propriedade e o guarda-corpo verificável, ambos redigidos em `## Risks`. Uma árvore só; o doc não
  existe no skeleton.
  files: `docs/standards/architecture/plugin-layout.md`
  verify: `grep -n 'lembrete\|boundary reminder' docs/standards/architecture/plugin-layout.md` mostra os dois testes, e `python3 plugins/quenching/assets/hooks/okf-validate.py docs` → 0 error(s), nenhum finding novo doc-a-doc
  subject: plan/collapse-remaining-language-clause-restatements: 1 Emendar plugin-layout com o teste do lembrete de fronteira
- [x] 2 Escrever a nota nas duas gêmeas, no mesmo commit — nomeia
  `standards/agents/communication.md` como dono e diz por que este local não cita: o front `specs/`
  é nativo e roda em repositório sem bundle.
  files: `plugins/quenching/assets/specs/templates/spec.md`, `plugins/quenching/assets/bin/specs.py`
  verify: o diff dos dois blocos de guidance é vazio, e `grep -n 'agents/communication.md'` devolve um acerto em cada
  subject: plan/collapse-remaining-language-clause-restatements: 2 Nota nas duas gemeas de template
- [x] 3 Escrever a mesma nota em `plugins/quenching/assets/specs/QUENCHING.md`, o terceiro artefato
  que sai do plugin.
  files: `plugins/quenching/assets/specs/QUENCHING.md`
  verify: `grep -n 'agents/communication.md' plugins/quenching/assets/specs/QUENCHING.md` → 1 acerto
  subject: plan/collapse-remaining-language-clause-restatements: 3 Nota no manual do front specs
- [ ] 4 Corrigir a nota de `plugins/quenching/assets/references/docs-align/okf-spec.md`, que afirma
  um colapso total que não aconteceu — passa a dizer que os normativos foram colapsados e que os
  lembretes de fronteira permanecem por decisão.
  files: `plugins/quenching/assets/references/docs-align/okf-spec.md`
  verify: `grep -n 'every other statement' plugins/quenching/assets/references/docs-align/okf-spec.md` → nenhum acerto
  subject: plan/collapse-remaining-language-clause-restatements: 4 Corrigir a nota falsa de okf-spec
- [ ] 5 Varrer os dez lembretes de fronteira da tabela de `## Design` contra o guarda-corpo da task
  1, corrigindo os que acrescentam um fato do dono ou estreitam o escopo. `assets/README.md` é o
  único hoje conhecido; reportar o número efetivamente corrigido, e registrar como discovery
  qualquer caso em que o teste não decida.
  files: `plugins/quenching/assets/README.md`, e os demais da tabela de `## Design` que a varredura condenar
  verify: `grep -n 'audience: human' plugins/quenching/assets/README.md` não devolve linha sobre a cláusula da língua, e o grep do censo devolve exatamente quatorze locais
  subject: plan/collapse-remaining-language-clause-restatements: 5 Varrer os dez lembretes contra o guarda-corpo
- [ ] 6 Sincronizar `specs/QUENCHING.md` a partir do mold já anotado pela task 3 — a cópia instalada
  neste repositório, hoje atrás em treze headings contra quatorze.
  files: `specs/QUENCHING.md`
  verify: `grep -n 'Fourteen canonical headings' specs/QUENCHING.md` → 1 acerto, e a nota da task 3 presente
  subject: plan/collapse-remaining-language-clause-restatements: 6 Sincronizar a copia instalada do manual

## Discoveries

- A Open Decision 'o invariante das gêmeas ganha um check mecânico?' já está resolvida: specs.py selftest compara TEMPLATE_SPEC com assets/specs/templates/spec.md byte-a-byte (specs.py:246 e :2790) e o próprio comentário do código diz 'EDIT BOTH OR NEITHER'. O check é durável, roda no lockstep, e não precisa de spec próprio — a decisão pode ser fechada como já-feita.
