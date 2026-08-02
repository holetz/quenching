---
slug: collapse-remaining-language-clause-restatements
title: Collapse Remaining Language Clause Restatements
verification: per-section
refined: {mode: gate, date: 2026-07-31}
approved: {date: 2026-07-31}
reviewed: {date: 2026-07-31}
merge: {strategy: merge-commit, subject: "plan/collapse-remaining-language-clause-restatements: merge (merge-commit)"}
outcome: done
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
camada acima, o defeito que este spec existe para curar. Depois disto cada local **do censo** ou
cita o dono, ou carrega por escrito a razão de não citar — mas o censo **não fecha** por isso: a
revisão de branch mediu dezenove ocorrências em dezessete arquivos contra os quatorze da tabela.
Ver `## Design` §O que a revisão de branch acrescentou.

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

- **O censo vivo.** Um padrão de **uma linha** não mede este conjunto, e `-A1` não conserta isso:
  ele estende um acerto já encontrado, e a ocorrência de `okf-spec.md` está quebrada por wrap
  (`the repo's` / `language` em linhas distintas), então não há acerto a estender. O escopo também
  precisa incluir `specs/`, que está fora de `plugins/ docs/`. O invariante é este:

  ```bash
  python3 - <<'PY'
  import re, pathlib
  pat = re.compile(r"repo'?s\s+language", re.S)
  files = [p for r in ('plugins', 'docs') for p in pathlib.Path(r).rglob('*')
           if p.suffix in ('.md', '.py')] + [pathlib.Path('specs/QUENCHING.md')]
  hits = {str(p): len(pat.findall(p.read_text(encoding='utf-8', errors='replace')))
          for p in sorted(set(files))}
  hits = {k: v for k, v in hits.items() if v}
  print(sum(hits.values()), 'acertos /', len(hits), 'arquivos')
  PY
  ```

  Medido em 2026-07-31, com a base já mergeada: **19 acertos / 17 arquivos**. Um acerto a mais é
  reenunciação nova, e é falha; **um a menos também é falha**, porque este spec decidiu que os
  lembretes ficam. O número 14 que este bullet declarava batia por coincidência aritmética — ver
  `## Discoveries`.
- **As três notas existem.**
  `grep -n 'agents/communication.md' plugins/quenching/assets/specs/templates/spec.md plugins/quenching/assets/bin/specs.py plugins/quenching/assets/specs/QUENCHING.md`
  → um acerto em cada arquivo.
- **As gêmeas não se afastaram.** `python3 plugins/quenching/assets/bin/specs.py selftest` compara
  `TEMPLATE_SPEC` com `assets/specs/templates/spec.md` **byte-a-byte** e falha com o diff quando
  divergem (`specs.py:246` e `:2791`, sob o comentário `EDIT BOTH OR NEITHER`). O invariante é
  durável e roda no lockstep das surfaces — não um diff manual medido no limite da task 2, como
  este spec supôs ao ser escrito; ver `## Open Decisions`.
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

### O que a revisão de branch acrescentou (2026-07-31)

A tabela acima ainda estava incompleta. Medida pelo invariante multiline de `## Validation`, a
população real é **19 acertos em 17 arquivos**, e dois arquivos inteiros nunca entraram em censo
nenhum — nem no original, nem no reconferido:

| Local | Sai do plugin? | Veredito |
| --- | --- | --- |
| `plugins/quenching/assets/docs/QUENCHING.md` | sim — `/docs:align` | lembrete de fronteira, fica **sem nota** |
| `docs/QUENCHING.md` | cópia instalada | idem, e **atrasada em v4.2.0** contra `VERSION` 4.4.2 |

Ambos passam o guarda-corpo da task 1: uma cláusula, nenhum fato que `communication.md` enuncia,
nenhum estreitamento. **E a nota dos três não se aplica aqui** — que é a distinção que o censo
original não tinha como fazer. O front `specs/` é nativo e instala em repositório sem bundle
algum, mas `/docs:align` copia este manual **junto com** o skeleton que contém
`docs/standards/agents/communication.md`: no alvo, o caminho resolve. Sair do plugin não é o teste;
sair **sem o dono** é.

A defasagem de `docs/QUENCHING.md` é a segunda instância da Open Decision *Nada nota um manual
instalado atrasado*, e não é consertada aqui: sincronizá-la é trabalho de `/docs:align`, e este
spec escopou o front `specs/`.

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

- **O invariante das gêmeas ganha um check mecânico? — RESOLVIDA: já tinha.** Esta decisão foi
  redigida sobre um fato falso. `specs.py selftest` **já** compara `TEMPLATE_SPEC` com
  `assets/specs/templates/spec.md` byte-a-byte e falha com o diff (`specs.py:246` e `:2791`, sob o
  comentário `EDIT BOTH OR NEITHER`). Não há spec próprio a abrir nem gatilho a esperar: o custo
  que ela pesou — código na ferramenta, entrada no lockstep — já estava pago quando ela foi
  escrita. Encontrado na execução, confirmado na revisão de branch.
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
- **As gêmeas se afastam depois do arquivamento — risco inexistente.** Escrito sob o mesmo fato
  falso do bullet acima: `specs.py selftest` compara as duas byte-a-byte a cada execução do
  lockstep, então nada nunca dependeu do diff manual da task 2. Ver `## Open Decisions`.
- **A tabela de `## Design` defasa.** Os números de linha morrem na primeira edição acima deles —
  foi assim que o censo do spec anterior envelheceu, e é por isso que este spec teve de reconferir
  tudo. **Mitigado por construção:** o invariante é o grep do primeiro bullet de `## Validation`,
  não a tabela; a tabela nomeia arquivos e vereditos, e as linhas são conveniência datada.
- **`plugin-layout.md` acusa `stale-doc` por causa deste spec.** O `resource:` dele cobre
  `plugins/quenching/assets/**` e as tasks 2–5 escrevem ali. Neste caso o `timestamp:` sobe
  legitimamente, porque a task 1 edita o próprio doc — mas não confunda isso com licença para
  silenciar o ruído da baseline com bump de timestamp em outros docs.

## Handoff

<!-- AUDIENCE: agent. Warned on when empty once the ready gate is met.

     The context an executor needs and cannot derive: the state of play, the conventions in
     force, what was already tried. Small by construction — it is sent with EVERY task.

     Refresh is bound to EVENTS, not judgment: the orchestrator rewrites this after each
     committed task. Staleness is this section's failure mode. -->

As seis tasks estão commitadas, uma por commit, em
`claude/collapse-language-clause-restatements-3daf9f` — **isolação declinada**, então não há record
`branch:` e o nome da branch não segue `plan/<slug>`. Base: `main`.

Estado do tree após o último commit: limpo. Nada bloqueado, nada pendente das tasks.

O que um executor precisa saber e não deriva:

- **Duas discoveries abertas**, ambas de `## Validation` / `## Open Decisions` e nenhuma resolvida
  aqui: o invariante do censo não mede o que afirma, e o check mecânico das gêmeas já existe em
  `specs.py selftest`. Ver `## Discoveries`.
- **O verify da task 5 passou com 14 acertos por coincidência aritmética.** O conjunto medido não é
  o da tabela de `## Design`: `okf-spec.md` nunca entrou (wrap) e `specs/QUENCHING.md` está fora do
  escopo do grep; o 14º é a prosa nova de `plugin-layout.md`. Não tratar aquele número como prova.
- **Um `stale-doc` do skeleton é ruído de baseline, não deste spec.**
  `assets/docs/standards/agents/communication.md` tem `timestamp: 2026-07-30`, e o commit base
  `8844703` já era de 2026-07-31 tocando `specs/**`. Não silenciar com bump.
- A cópia instalada `specs/QUENCHING.md` é agora byte-a-byte o mold com `<VERSION>` → `4.4.2`.

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
- [x] 4 Corrigir a nota de `plugins/quenching/assets/references/docs-align/okf-spec.md`, que afirma
  um colapso total que não aconteceu — passa a dizer que os normativos foram colapsados e que os
  lembretes de fronteira permanecem por decisão.
  files: `plugins/quenching/assets/references/docs-align/okf-spec.md`
  verify: `grep -n 'every other statement' plugins/quenching/assets/references/docs-align/okf-spec.md` → nenhum acerto
  subject: plan/collapse-remaining-language-clause-restatements: 4 Corrigir a nota falsa de okf-spec
- [x] 5 Varrer os dez lembretes de fronteira da tabela de `## Design` contra o guarda-corpo da task
  1, corrigindo os que acrescentam um fato do dono ou estreitam o escopo. `assets/README.md` é o
  único hoje conhecido; reportar o número efetivamente corrigido, e registrar como discovery
  qualquer caso em que o teste não decida.
  files: `plugins/quenching/assets/README.md`, e os demais da tabela de `## Design` que a varredura condenar
  verify: `grep -n 'audience: human' plugins/quenching/assets/README.md` não devolve linha sobre a cláusula da língua, e o grep do censo devolve exatamente quatorze locais
  subject: plan/collapse-remaining-language-clause-restatements: 5 Varrer os dez lembretes contra o guarda-corpo
- [x] 6 Sincronizar `specs/QUENCHING.md` a partir do mold já anotado pela task 3 — a cópia instalada
  neste repositório, hoje atrás em treze headings contra quatorze.
  files: `specs/QUENCHING.md`
  verify: `grep -n 'Fourteen canonical headings' specs/QUENCHING.md` → 1 acerto, e a nota da task 3 presente
  subject: plan/collapse-remaining-language-clause-restatements: 6 Sincronizar a copia instalada do manual

## Discoveries

- **RESOLVIDA na revisão de branch** (em `## Open Decisions` e `## Risks`). A Open Decision 'o invariante das gêmeas ganha um check mecânico?' já está resolvida: specs.py selftest compara TEMPLATE_SPEC com assets/specs/templates/spec.md byte-a-byte (specs.py:246 e :2790) e o próprio comentário do código diz 'EDIT BOTH OR NEITHER'. O check é durável, roda no lockstep, e não precisa de spec próprio — a decisão pode ser fechada como já-feita.
- **RESOLVIDA na revisão de branch** — o invariante de `## Validation` foi reescrito multiline e com `specs/` no escopo (19 acertos / 17 arquivos), e a lição virou `docs/standards/quality/bundle-verification.md` §Um invariante de grep mede o que o grep alcança. O invariante do censo em ## Validation nao mede o que afirma. O grep declarado (uma linha, escopo plugins/ docs/) nunca pegou okf-spec.md, cuja ocorrencia esta quebrada por wrap ('the repo's' / 'language' em linhas distintas) — e -A1 nao a recupera, so mostra a linha seguinte de um acerto ja encontrado. Tambem nao cobre specs/QUENCHING.md, que esta fora de plugins/ e docs/. E learn.md conta dois acertos num arquivo so. Medido: 13 acertos / 12 arquivos antes deste spec, 14 / 13 depois — o +1 e a nova prosa de plugin-layout.md (task 1), nao um lembrete novo. O numero 14 do verify da task 5 bate por coincidencia aritmetica, nao porque o conjunto seja o da tabela. Um censo que meca de fato precisa de grep multiline e de incluir specs/.
- **ABERTA — pertence a `/docs:align`, não a este spec.** `docs/QUENCHING.md`, a cópia instalada do manual do front `docs/` neste repositório, está em `v4.2.0` contra `VERSION` 4.4.2 — e carrega a mesma cláusula da língua, sem ter entrado em censo nenhum. É a **segunda** instância da Open Decision *Nada nota um manual instalado atrasado*, que até aqui tinha uma só: dois manuais de payload, dois desatualizados, nenhuma máquina notando. Sincronizá-la é um `/docs:align`, fora do escopo deste spec; o que ela acrescenta é a evidência de que a classe tem mais de um membro, que era exatamente o que aquela decisão precisava para ser dimensionada.

## Outcome

Entregue como `done` em 2026-07-31, mergeado em `main` por **merge commit** (`--no-ff`) a partir de
`claude/collapse-language-clause-restatements-3daf9f`. A branch **não segue** `plan/<slug>` e não há
record `branch:`: a isolação foi declinada quando o spec nasceu, e o worktree veio de outra via.
Base `main`, trazida para a branch antes do gate — os commits de task ficaram preservados, cada um
resolvível pelo `subject:` que sua linha registra.

**O que shipou.** As seis tasks. A emenda em `docs/standards/architecture/plugin-layout.md`
§*A boundary reminder is not a restatement* — o critério de propriedade e o guarda-corpo de três
propriedades, que é o único dos dois que teria pego o defeito real. A nota inline nos três artefatos
do front `specs/` que saem do plugin **sem levar o dono junto**
(`assets/specs/templates/spec.md`, `assets/bin/specs.py`, `assets/specs/QUENCHING.md`). A correção
do estreitamento em `assets/README.md`, que limitava a regra a `audience: human`. A correção da nota
de `okf-spec.md`, que afirmava um colapso total que não aconteceu. A varredura dos dez lembretes de
fronteira contra o guarda-corpo — **nenhum outro estreitava**. E a sincronização de
`specs/QUENCHING.md`, que estava treze headings atrás do mold.

**O que a revisão de branch acrescentou**, tudo na branch antes do merge. Seis afirmações falsas do
próprio spec, corrigidas — ver `## Design` §O que a revisão de branch acrescentou. E o doc emergente
`docs/standards/quality/bundle-verification.md` §*A grep invariant measures what the pattern
reaches*: a lição de um invariante que devolveu 14 contra uma população real de 19, com o número
batendo por coincidência aritmética.

**O que ficou de fora, e por quê.** Os dez lembretes de fronteira ficam — decididos pelo
guarda-corpo, não por contagem. Os 48 specs congelados não retroagem por construção. E o censo
**não fechou**: `docs/QUENCHING.md` está atrás em v4.2.0 e carrega a mesma cláusula sem ter entrado
em censo nenhum. É a segunda instância da Open Decision *Nada nota um manual instalado atrasado*, e
sincronizá-la é trabalho de `/docs:align` — registrada como discovery aberta.

**A colisão de versão aconteceu, e foi resolvida como o standard previa.** Este conclude bumpou
para `4.4.3`; enquanto ele rodava, o spec `cut-specs-execute-turns` concluiu, bumpou para o **mesmo
`4.4.3`** e mergeou primeiro. A segunda passagem de `main` para esta branch conflitou em
`VERSION` — e só nele, porque os outros seis mudaram para o mesmo valor dos dois lados e o git os
aceitou em silêncio, que é a metade traiçoeira do modo de falha. Resolvido rebumpando os sete para
**4.4.4**, a partir da base efetivamente mergeada. É a demonstração literal do segundo bullet de
[versioning-release.md](../../docs/standards/ci-cd/versioning-release.md) §*Why not a task*, e a
razão pela qual o bump é ato do merge e não task.

**O que o próximo leitor precisa saber.** O release **4.4.4** sai com este merge, e ele deixa
`specs/QUENCHING.md` — que a task 6 acabara de sincronizar em 4.4.2 — atrás do banner outra vez.
Isso é por construção e não é drift de conteúdo: o `<VERSION>` do banner é preenchido no copy time,
então a cópia se re-stampa no próximo `/specs:align`. E a estratégia foi **merge commit**, não
squash: cada `subject:` registrado nas tasks continua resolvendo contra a história.
