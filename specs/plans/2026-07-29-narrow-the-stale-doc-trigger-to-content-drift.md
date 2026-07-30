---
slug: narrow-the-stale-doc-trigger-to-content-drift
title: Narrow stale-doc — retire the verdict, report resource activity as a figure
verification: per-section
priority: {level: 8, criticality: high, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# Narrow stale-doc — retire the verdict, report resource activity as a figure

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a thirteen-heading skeleton. Every other heading below is created on
     first write by `specs.py section <slug> "<Heading>" --write`, which inserts it in the
     canonical position with the guidance comment kept here.

     THE STAGE-SCOPED EXPLICIT-NONE RULE. A heading is required — and required to carry
     `- none — <reason>` when it has nothing in it — only once ITS OWN gate is reached:

       new (capture)        `## Problem`
       ready (derived)      the nine definition sections (`## Problem` .. `## Risks`)
                            AND `## Tasks`
       ready (warn only)    `## Handoff` non-empty
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

     AUDIENCE. Each section names who reads it. `## Problem`/`## Proposal`/`## Design` are for
     the human — examples and plain language belong there. `## Handoff`/`## Tasks` are for
     agents — terse, with `files:`/`verify:`/`pattern:` metadata. An orchestrator never sends
     the human sections to an executor; that is what lets one file serve both audiences
     without bloating agent context. -->

## Overview

O `okf-validate.py` tem uma checagem de desatualização, `stale-doc`, que compara o `timestamp` de um
doc com a data do último commit que tocou o escopo declarado no seu `resource:`. `## Problem` mede
quanto ela acende hoje neste bundle e por que esse número a inutiliza.

Esta spec **não** faz o que o slug promete, e `## Design` é onde isso é demonstrado em vez de
alegado: com a medição por entrada do `resource:` e com dois standards vinculantes, "content drift"
é inalcançável com o endereçamento que o bundle tem — o `resource:` endereça arquivos, e o assunto
de um doc é menor que um arquivo. `## Proposal` diz o que será feito no lugar: aposentar o veredito
e publicar a medição como figure, com atribuição por entrada.

`## Alternatives Considered` guarda as seis formas pesadas, entre elas o content hash e o
apertamento do glob, e por que cada uma perdeu. `## Out of Scope` separa o que a decisão
deliberadamente não toca — nenhum recarimbo, nenhum `resource:` reescrito — do que fica para as
specs irmãs.

`## Risks` é onde a spec fica desconfortável: a suposição que a sustenta é que **alguém lê figure**,
e ela está escrita lá como suposição, não como certeza, junto das fronteiras com as três specs
irmãs que encostam nesta superfície. O que ainda não foi decidido — se `/docs:status` consome a
figure, e em que ordem esta spec e o upgrade do contrato OKF pousam — está em `## Open Decisions`
com o critério que fecha cada um.

O trabalho em si é pequeno e cabe num arquivo: `## Impact` lista os sete lugares que citam o código
hoje, `## Tasks` divide em seis grupos que a política `verification: per-section` verifica um a um, e
`## Validation` traz o número exato que a saída do validador deve passar a imprimir — de
`0 error(s), 14 warning(s)` para `0 error(s), 2 warning(s)`, com os dois restantes sendo
pré-existentes e de outro assunto.

## Problem

O aviso `stale-doc` do `okf-validate.py` dispara quando o `timestamp` de um doc é anterior ao
último commit que tocou **qualquer** arquivo casado pelo seu `resource:`. Como os globs são largos
por bom motivo (`assets/**`, `specs/**`, ou os três scripts nomeados um a um), o gatilho mede
**atividade no raio do glob**, não deriva de conteúdo.

O efeito foi medido durante o `/specs:conclude` da spec `prefer-worktree-isolation`, em 2026-07-29.
A contagem em `docs/` na raiz saiu de **6** avisos `stale-doc` no início da revisão para **15** no
fim, ao longo de quatro commits legítimos:

- o bump do lockstep de versão tocou `specs.py`, `skills.py` e `okf-validate.py` — e um bump de
  versão toca as três ferramentas **por definição**, então acende todo doc cujo `resource:` nomeia
  qualquer uma delas;
- cada commit da própria conclusão (carimbo `reviewed`, `## Outcome`, a movimentação para
  `archive/`) tocou `specs/**`, acendendo todo doc cujo glob cobre o workspace.

Nenhum dos 15 docs teve o **assunto** alterado. Entre os acesos estão justamente
`ci-cd/versioning-release.md` (que descreve o lockstep corretamente e foi aceso por um lockstep
executado exatamente como ele manda) e `quality/parse-honesty.md`, `naming/command-surface.md`,
`workflows/plan-artifacts.md` — docs que ninguém encostou.

O problema não é o ruído em si, é o que ele faz com a decisão do humano. Com quase todo standard
aceso, `stale-doc` deixa de separar o doc que envelheceu do doc que apenas estava perto de uma
mudança. As duas saídas disponíveis hoje são igualmente ruins: recarimbar em massa é carimbar
`authority` sem lastro — a revisão de conteúdo que o carimbo alega não aconteceu — e ignorar em
massa é treinar o operador a não ler a única checagem que existe para desatualização. A spec
`prefer-worktree-isolation` recusou as duas e deixou os 15 avisos de pé, registrando o motivo.

Vale notar o que **não** é o problema: o `stale-doc` acerta quando o `resource:` é estreito. Dois
avisos desta mesma conclusão eram verdadeiros — `worktree-setup.md` e `plan-git-record.md`
carimbavam `2026-07-28` e tinham sido escritos em 2026-07-29 — e foram fechados por recarimbo
honesto. A regra não está errada em toda parte; ela perde resolução à medida que o glob cresce.

Fica em aberto qual é a correção: apertar o gatilho (comparar contra commits que tocam o assunto do
doc, e não o raio do glob), tratar mudanças que só mexem em versão como não-substantivas, mudar a
granularidade do `resource:`, ou reclassificar o achado. Relacionado, mas distinto, é
`2026-07-25-expose-finding-advisory-as-data`, que trata de **expor** a natureza advisory do achado
como dado — não da precisão do gatilho.

**Medição de 2026-07-30, nesta mesma árvore.** `okf-validate.py docs` imprime hoje
`0 error(s), 14 warning(s)`, dos quais **12** são `stale-doc` — 12 dos 26 concept docs do bundle,
46%. Entre os acesos estão `quality/bundle-verification.md`, que é o standard que **define** a
categoria advisory, e `quality/parse-honesty.md`, que é o standard que a mensagem do achado viola.
Uma checagem que acende quase metade do bundle e acusa os dois documentos que a governam deixou de
ser sinal: virou custo fixo de leitura.

E a hipótese registrada acima — que a regra "perde resolução à medida que o glob cresce" — foi
**parcialmente falseada** pela mesma medição. Atribuindo cada aviso à entrada do `resource:` que o
acendeu, **8 dos 12** acendem por uma entrada de kind `path`: um único arquivo nomeado, o
`resource:` mais estreito que existe. `quality/parse-honesty.md` nomeia três scripts, um a um, e
acende; `quality/bundle-verification.md` nomeia só `okf-validate.py` e acende. Apenas 4 acendem
exclusivamente por glob. A largura do glob agrava, mas não é a causa — a causa é que a unidade de
endereçamento é o **arquivo**, e o assunto de um standard é menor que um arquivo.

Existe ainda a falha simétrica, do mesmo mecanismo e menos visível. `check_stale` filtra as entradas
por `RESOLVABLE_KINDS = ("path", "glob")` (`assets/hooks/okf-validate.py:597-598`) e retorna sem
achado nenhum quando nada sobra (`:599-600`). Um doc cujo `resource:` é uma URL — exatamente o que
`/docs:import` §Anti-fabrication manda derivar quando a fonte é externa
(`commands/docs/import.md:32`) — é **eternamente fresco** para o validador. Não é ruído: é silêncio,
e ninguém olha o que não é impresso.

## Proposal

- `stale-doc` deixa de ser um achado. O código é **aposentado, não apagado**: nada mais o emite, e
  ele continua nomeado e explicado onde já é, pelo precedente do `log.md`
  (`docs/standards/architecture/retiring-a-reserved-artifact.md`).
- No lugar dele, `okf-validate.py` publica a mesma medição como **figure**: por doc e **por entrada
  do `resource:`**, o `timestamp` carimbado, a data do último commit que tocou aquela entrada, e o
  intervalo entre as duas — ordenado pelo maior intervalo primeiro.
- A figure sai por uma saída própria (`--activity`, com `--json` opcional). A lista de findings do
  `--json` de hoje continua byte-compatível: quem lê findings não vê mudança de forma.
- Um doc cujo escopo o validador **não consegue medir** (toda entrada `uri` ou `unknown`) aparece na
  figure marcado como escopo não medido, em vez de sair da checagem em silêncio.
- `/docs:status` deixa de listar `stale-doc` entre os achados e passa a poder ler essa figure na
  tabela da §5, onde ele já era descrito como "an advisory age — never a verdict".
- Nenhum `timestamp:` é recarimbado por esta spec e nenhum `resource:` é reescrito. A contagem de
  `stale-doc` em `okf-validate.py docs` vai de 12 para 0 por aposentadoria, não por conserto de doc.
- Os quatro arquivos do plugin que hoje descrevem `stale-doc` como WARN passam a descrever a figure,
  e `docs/standards/quality/bundle-verification.md` registra a regra que a decisão prova.
- O `selftest` do `okf-validate.py` ganha a fixture que faz a aposentadoria falhar se alguém
  reintroduzir a emissão.

## Out of Scope

- **Apertar o gatilho para "content drift" de verdade.** É o que o slug promete, e `## Design`
  §Decisão 2 mostra por que não se alcança: exigiria endereçamento no nível do assunto, e
  `docs/standards/quality/bundle-verification.md` §The `resource` glob-set format já descartou
  `file:line` — "A line number says *where the rule is written* and rots on any insertion above it".
  Reabrir aquela decisão é outra spec, com outro custo.
- **Recarimbar os 12 docs acesos.** A spec `prefer-worktree-isolation` recusou o recarimbo em massa
  com razão: carimbar sem a revisão de conteúdo que o carimbo alega é a desonestidade que
  `## Problem` descreve. Aposentar o veredito não autoriza fazer o mesmo por outra porta.
- **Mudar o `resource:` de qualquer doc.** A medição mostra que não resolveria (8 dos 12 já usam
  `path`), e estreitar um escopo verdadeiro para calar uma checagem é a fabricação que
  `bundle-verification.md` nomeia no caso `resource-self`.
- **Escalar qualquer coisa para ERROR.** `bundle-verification.md` §What is machine-checked é
  explícito — "No new check is introduced at ERROR" — e um repo alvo que passava não pode ficar
  vermelho num upgrade que ele não pediu.
- **Rodar a medição no `PostToolUse` ou no `Stop`.** Ela shella `git log`; a tabela §Where
  verification runs continua valendo e a figure é CLI-only pelo mesmo motivo.
- **Consertar o doc eternamente fresco de `uri`.** Esta spec o **expõe** na figure; a proveniência e
  a re-ingestão idempotente que o tornariam medível são de `add-import-provenance`.
- **Mudar a forma da lista de findings do `--json`.** É o terreno de
  `expose-finding-advisory-as-data`; a figure sai por saída própria justamente para não colidir.
- **Tocar `specs.py` ou `skills.py` além do bump do lockstep.** A checagem é do validador; nenhum
  outro tool a emite.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/quality/bundle-verification.md` — a regra que a decisão prova: uma checagem que
  não distingue "errado" de "vale um olhar" e acende em quase metade do bundle não é advisory, é
  figure; e o limite do que um checker pode alegar a partir do que mediu

### Standards em `authority: background` que esta spec pode resolver

- `docs/standards/quality/selftest-mutation.md` — a fixture da aposentadoria precisa da passada de
  mutação que este standard exige; feita e observada falhando, o standard ganha lastro para ir a
  `authority: current`

### Código e assets que esta spec deve tocar

- `plugins/quenching/assets/hooks/okf-validate.py` — `check_stale` (`:574-606`),
  `_git_last_commit_date` (`:556-571`), a chamada em `_validate_text` (`:1029-1030`), `run_cli`
  (`:1238-1267`) e a fixture do `selftest`
- `plugins/quenching/assets/references/docs-align/conformance.md` — §Staleness (`:97-105`) e a linha
  do verify gate (`:130`)
- `plugins/quenching/assets/references/docs-align/cycle.md` — a linha de roteamento (`:82`)
- `plugins/quenching/commands/docs/status.md` — as seis citações de `stale-doc` (`:51`, `:70`, `:94`,
  `:118`, `:120`, `:172`) e a tabela de figures da §5
- `plugins/quenching/assets/docs/knowledge/glossary.md` — a semente publicada (`:37`)
- `docs/knowledge/glossary.md` — as entradas **Advisory finding** e **Resource glob set**, por
  `/docs:define`
- `plugins/quenching/VERSION` e os três scripts do lockstep, porque tocar `okf-validate.py` puxa
  `docs/standards/ci-cd/versioning-release.md` inteiro

## Validation

Os caminhos abaixo são relativos à raiz do repo.

- **A contagem, que é a medição que motivou a spec.**
  `python3 plugins/quenching/assets/hooks/okf-validate.py docs` deve imprimir
  `0 error(s), 2 warning(s)` — os dois `resource-unresolved` de `standards/automation/agents.md` e
  `standards/automation/hooks.md`, que são pré-existentes e não são desta spec. E zero linhas do
  código aposentado:
  `python3 plugins/quenching/assets/hooks/okf-validate.py docs | grep -c stale-doc` deve dar `0`.
  Medido hoje, antes da mudança: `0 error(s), 14 warning(s)` e `12`.
- **A figure existe e atribui por entrada.**
  `python3 plugins/quenching/assets/hooks/okf-validate.py docs --activity` deve trazer, para
  `standards/quality/parse-honesty.md`, as **três** entradas `path` do seu `resource:` separadas,
  cada uma com sua data e seu intervalo, com o maior intervalo primeiro. Hoje essa informação não
  existe em nenhuma saída do validador.
- **A forma da lista de findings não mudou.**
  `python3 plugins/quenching/assets/hooks/okf-validate.py docs --json` continua um array JSON de
  objetos com exatamente as chaves `severity`, `path`, `code` e `message` — nada acrescentado no topo.
- **O escopo não medido aparece.** Numa fixture cujo `resource:` é só uma URL, a figure deve marcar o
  doc como escopo não medido. Hoje um doc assim não produz linha nenhuma, em nenhuma saída.
- **A semente e o skeleton continuam conformes por construção.** De `plugins/quenching`:
  `python3 assets/hooks/okf-validate.py assets/docs` → `0 error(s), 0 warning(s)`; e
  `python3 assets/hooks/okf-validate.py assets/specs/plans --listing-root` → o mesmo.
- **O selftest cobre a aposentadoria, e a cobertura foi observada falhando.**
  `python3 plugins/quenching/assets/hooks/okf-validate.py selftest` passa; e a passada de mutação de
  `docs/standards/quality/selftest-mutation.md` foi feita — reintroduzir a emissão do WARN faz o
  selftest falhar, e isso foi visto, não presumido.
- **O lockstep de versão.** `cat plugins/quenching/VERSION` e os três `--version`
  (`assets/bin/specs.py`, `assets/bin/skills.py`, `assets/hooks/okf-validate.py`) concordam, e
  `python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json` continua
  em 26 comandos sem findings.
- **Nenhuma citação órfã.** `grep -rn 'stale-doc' plugins/ docs/` só deve casar os pontos de
  reconhecimento que a aposentadoria mantém de propósito — nenhum texto que ainda descreva um WARN
  emitido, em nenhuma das quatro referências nem na semente.

## Design

### Decisão 1 — o gatilho fica; o veredito sai

`check_stale` (`assets/hooks/okf-validate.py:574-606`) mede uma coisa e diz outra. O que ela mede é
`git log -1 --format=%cI` com pathspec `:(glob)` sobre as entradas do `resource:`
(`_git_last_commit_date`, `:562-571`), comparado com `timestamp`. O que ela **diz** é
"the doc may no longer describe what it governs" (`:604-605`) — um veredito sobre conteúdo tirado de
uma medição de atividade.

`docs/standards/quality/parse-honesty.md` §The rule é vinculante aqui e é literal: um tool que
transforma sua entrada antes de checá-la **deve** poder relatar o que a transformação removeu, como
achado próprio. A perda, neste caso, é toda a distância entre "o arquivo mudou" e "o assunto mudou".
O mesmo standard nomeia o remédio na §Naming the limit is not the same as removing it: nomear o
limite **quita** a obrigação; ensinar o parser a ler mais é decisão separada, com custo próprio.
Logo a correção mínima honesta é a alegação, não o gatilho.

### Decisão 2 — "content drift" é inalcançável com o endereçamento atual, e a medição prova

O `resource:` endereça **arquivos e globs** (`parse_resource` e `_resource_kind`, kinds `path`,
`glob`, `uri`, `unknown`). O assunto de um standard é **menor que um arquivo**: `okf-validate.py`
sozinho carrega o parsing de frontmatter, a integridade de `resource`, a staleness, os quatro modos
de hook e o selftest. Cinco standards deste bundle apontam para ele, e um commit em qualquer um
desses assuntos acende todos os cinco.

É por isso que estreitar o `resource:` não resolve, e a medição confirma:
`quality/parse-honesty.md` já usa a forma mais estreita disponível — três entradas `path`, uma por
script — e acende. Não existe `resource:` mais estreito do que um arquivo nomeado.

O que mediria drift de assunto é endereçamento de assunto: um símbolo, uma faixa de linhas, uma
âncora de seção. `bundle-verification.md` §The `resource` glob-set format já rejeitou exatamente
isso, com a razão certa: "A line number says *where the rule is written* and rots on any insertion
above it; a glob says *what the doc governs*, which is also exactly the input a staleness check
needs." Ou seja: a única entrada capaz de sustentar o nome "content drift" é a que o contrato
vinculante descartou. Esta spec aceita o fechamento em vez de reabri-lo.

### Decisão 3 — um content hash não compra nada, e isso é medido, não suposto

A leitura óbvia do título seria guardar um digest do escopo governado junto do carimbo e comparar.
Ele falha pelos dois lados.

Empiricamente: no episódio de 6 → 15 avisos que `## Problem` registra, **todo** commit envolvido
mudou bytes de verdade. Um bump de lockstep reescreve a constante de versão de cada script; um
carimbo `reviewed` reescreve o frontmatter da spec. Um digest sobre o mesmo conjunto de entradas
reproduz os 15 avisos, um por um. O único caso que ele elimina — um commit que tocou o caminho sem
mudar byte — é praticamente vazio, e um `git log -1` com pathspec já não o produz.

Normativamente: um digest de bytes chamado "content drift" é precisamente a alegação que
`parse-honesty.md` proíbe — um nome que descreve mais do que o tool observou. E cobra caro: uma
chave nova no frontmatter de todo concept doc, propagada para a semente publicada e para todo repo
alvo já alinhado, com migração e lockstep atrás.

### Decisão 4 — a forma da aposentadoria segue o precedente do `log.md`

`docs/standards/architecture/retiring-a-reserved-artifact.md` já resolveu este formato de mudança:
**aposentar não é remover o reconhecimento.** Traduzido de nome reservado para código de achado, a
aposentadoria do `stale-doc` são três movimentos, e o terceiro é o que não se faz:

1. sai a emissão — a chamada em `_validate_text` (`:1029-1030`) e o WARN de `check_stale`;
2. nada mais o produz — nenhum comando e nenhuma referência o descreve como achado ativo;
3. **o resto não muda** — o código continua nomeado e explicado onde já é, do mesmo jeito que
   `log.md` continua em `RESERVED` e o branch dele continua em `_validate_text:1021`
   (`raw = []  # retired: reserved, recognized, never judged`).

O raio de explosão é o mesmo que aquele standard descreve, e é por isso que ele é precedente e não
analogia: um repo alvo que hoje lê `stale-doc` do `--json`, ou o cita numa config, não pode ficar
vermelho num upgrade.

### Decisão 5 — a figure sai por saída própria, não dentro da lista de findings

`run_cli` (`:1256-1259`) imprime hoje um **array** JSON de findings, com as chaves
`severity`/`path`/`code`/`message`. Publicar a figure dentro dele exigiria trocar o topo de array
para objeto, o que quebra todo consumidor — e é exatamente a superfície que a spec irmã
`expose-finding-advisory-as-data` está mexendo. Então a figure sai por uma saída própria
(`--activity`), com documento JSON próprio. Duas specs, duas superfícies, nenhuma colisão de
contrato.

### Decisão 6 — atribuição por entrada, e o custo dela é medido

Hoje `_git_last_commit_date` recebe **todas** as entradas num pathspec só, uma chamada por doc, e o
achado não diz qual entrada acendeu. A figure precisa dizer, então passa a uma chamada por entrada.
Medido nesta árvore em 2026-07-30: **26 chamadas viram 84**, e a passada completa leva **0,6 s** de
wall clock. É aceitável porque a medição continua CLI-only por default-off — a tabela §Where
verification runs de `bundle-verification.md` não muda, e o `with_stale=False` de `_validate_text`
continua sendo a razão pela qual um chamador de hook não a adquire por esquecimento (`:1008-1011`).

### Contratos que este design não pode contradizer

- `docs/standards/quality/parse-honesty.md` — vinculante, `authority: current`. Governa o que a
  checagem pode alegar sobre o que leu.
- `docs/standards/quality/bundle-verification.md` — §Advisory is a real category, and must stay
  small; §What is machine-checked ("No new check is introduced at ERROR"); §Where verification runs.
- `docs/standards/architecture/retiring-a-reserved-artifact.md` — a forma da aposentadoria.
- `docs/standards/ci-cd/versioning-release.md` — qualquer toque em `okf-validate.py` puxa o lockstep
  de versão inteiro.
- `assets/references/docs-align/okf-spec.md` §Frontmatter — `timestamp` é *recommended*, não
  required; a figure não pode passar a exigi-lo de ninguém.

## Alternatives Considered

Seis formas inteiras, medidas contra a mesma evidência. A escolhida é a última.

| Forma | Custo | O que compra | O que fecha |
| --- | --- | --- | --- |
| Não fazer nada — deixar os 12 avisos de pé | zero | nada | treina o operador a não ler a única checagem de desatualização que existe |
| Digest de conteúdo no carimbo | chave nova no frontmatter de todo doc, semente e migração | quase nada — reproduz os 15 avisos medidos | compromete o frontmatter com um dado que não sustenta o nome |
| Estreitar o `resource:` dos docs acesos | revisão manual de 12 docs | nada — 8 dos 12 já são `path` | inventa escopo estreito falso, que é `resource-self` por outro caminho |
| Filtrar commits "não substantivos" (só versão) | um walk de diff por commit candidato | tira o caso do lockstep, deixa o de `specs/**` | faz o tool alegar semântica de diff, que é o que `parse-honesty.md` proíbe |
| Remover a checagem inteira | uma deleção | silêncio limpo | perde os verdadeiros positivos medidos e quebra quem lê `stale-doc` do `--json` |
| **Aposentar o veredito e publicar a figure** | uma saída nova, uma fixture, quatro referências, o lockstep | a medição inteira, honesta e legível, e zero achado a perseguir | nada — o gatilho, o dado e o código continuam lá |

Por que cada uma perdeu:

- **Não fazer nada** já é o estado, e foi escolhido conscientemente uma vez
  (`prefer-worktree-isolation` registrou o motivo). O que mudou desde então é a proporção: 12 de 26
  docs, incluindo os dois standards que governam a checagem. A inação deixou de ser neutra.
- **Digest de conteúdo** é a leitura literal do slug e é a que a medição mata: todo commit do
  episódio mudou bytes, então o digest acende igual. Perde por não comprar nada, antes mesmo de
  perder por `parse-honesty.md`.
- **Estreitar o `resource:`** parte da hipótese do `## Problem`, que a atribuição por entrada
  falseou. Perde porque não existe granularidade abaixo do arquivo, e porque a única forma de
  "estreitar" um escopo verdadeiro é mentir sobre ele.
- **Filtrar commit não substantivo** é atraente e resolve o caso mais gritante (o bump do lockstep),
  mas exige que o tool declare que um diff é irrelevante. É exatamente a alegação a mais que
  `parse-honesty.md` §The rule proíbe, e o custo em chamadas de git é aberto.
- **Remover a checagem** parece a versão simples da escolhida, e é a versão desonesta dela: os dois
  verdadeiros positivos de 2026-07-29 (`worktree-setup.md`, `plan-git-record.md`) mostram que o dado
  vale; o que não vale é o veredito. Remover joga o dado fora junto, e quebra o reconhecimento do
  código, que `retiring-a-reserved-artifact.md` diz para preservar.

## Open Decisions

- **`/docs:status` chama `--activity`, ou a figure fica só no CLI do validador?** Como se decide:
  por medição, antes da task de wiring. A §5 do `commands/docs/status.md` já roda `Glob` e várias
  leituras, e este comando é read-only e barato por contrato
  (`docs/standards/architecture/read-only-views.md`); ~1000 chamadas de git num bundle grande pode
  não caber nesse orçamento. Roda-se a passada `--activity` num bundle de ~200 docs e o número
  decide. Se não couber, a figure fica no CLI e a §5 apenas aponta para ela.
- **A figure precisa de `--json` na primeira versão, ou o texto basta?** Como se decide: pelo
  consumidor. Se `/docs:status` ler a figure (decisão acima), `--json` é obrigatório; se ela ficar
  só para leitura humana no CLI, `--json` é escopo que se adia sem perder nada. As duas decisões
  fecham juntas.
- **A ordem de release entre esta spec e `upgrade-okf-to-v0-2`.** Como se decide: lendo o contrato
  v0.2 quando ele existir. Se o v0.2 mantiver `timestamp` com a mesma semântica, não há nada a
  fazer; se renomear, a figure lê a chave nova e a task correspondente entra na spec que estiver
  aberta na hora. Até lá a figure lê `timestamp` como hoje.
- **Se `stale-doc` deve continuar aparecendo no `--json` sob uma severity que não é WARN, em vez de
  desaparecer.** Como se decide: pelo que `expose-finding-advisory-as-data` fizer com a forma do
  finding. Se aquela spec criar um canal para achado não-blocante, a aposentadoria pode virar
  migração para esse canal em vez de remoção da emissão — o que muda esta spec de forma, não de
  intenção. Precisa da palavra do humano se as duas forem construídas juntas.

## Risks

Cada história do premortem virou exatamente uma linha aqui, uma task de mitigação em `## Tasks`, ou
uma linha de `## Out of Scope`. A que não virou nada foi descartada e está dita no fim.

- **A suposição que sustenta a spec inteira: alguém lê figure.** Se a resposta for não, esta spec
  troca 12 linhas de ruído por silêncio total, que é pior — o ruído pelo menos era visível.
  Mitigação: a figure é **ordenada pelo maior intervalo primeiro** e **nomeia a entrada** que
  produziu o intervalo, então a primeira linha é a acionável e uma leitura basta; e o roteamento não
  muda, porque `assets/references/docs-align/cycle.md:82` já mandava `stale-doc` para o dono do doc
  com "No — advisory". A figure herda o mesmo destino, não um destino novo.
- **Um consumidor externo lê `stale-doc` do `--json` e para de achar linhas sem erro nenhum.**
  Mitigação: é exatamente o raio de explosão que
  `docs/standards/architecture/retiring-a-reserved-artifact.md` descreve, e a resposta dele é a que
  esta spec segue — o código continua reconhecido e explicado, e a mudança é anunciada como
  aposentadoria da emissão, não como remoção do código. Nada aqui pode transformar o silêncio em
  erro para esse consumidor, o que é o resultado que importa.
- **A fixture do selftest passa na primeira vez e não prova nada.** É o defeito que
  `docs/standards/quality/selftest-mutation.md` nomeia. Mitigação: a passada de mutação é uma task
  explícita e a observação da falha é parte do `## Validation`, não uma promessa.
- **A atribuição por entrada custa git em bundle grande.** Medido aqui: 26 → 84 chamadas, 0,6 s. Um
  bundle de 200 docs com 5 entradas cada seria ~1000 chamadas. Mitigação: continua CLI-only por
  default-off, e se `/docs:status` for ligado nela isso é decidido por medição — está em
  `## Open Decisions`.
- **Sibling `expose-finding-advisory-as-data`** — mexe na mesma superfície `--json`, expondo o status
  advisory de um finding como dado. A fronteira que esta spec mantém: ela **não** altera a forma da
  lista de findings e não insere a figure dentro dela; a figure sai por `--activity`. Se aquela spec
  pousar primeiro, o compromisso desta continua válido, porque é um compromisso de não-adição. O que
  esta spec **remove** daquela superfície é um código que deixa de ser emitido, e essa interseção
  precisa da palavra do humano se as duas forem construídas na mesma release.
- **Sibling `add-import-provenance`** — dona do doc importado que aponta para uma URL. A fronteira:
  esta spec apenas **expõe** o escopo não medido na figure; ela não adiciona proveniência, não torna
  a URL medível e não muda `/docs:import`. Se aquela spec introduzir um dado que torne o doc
  medível, a figure passa a medi-lo sem mudança aqui.
- **Sibling `upgrade-okf-to-v0-2`** — dona do contrato que governa `timestamp`. A fronteira: esta
  spec lê `timestamp` exatamente como `check_stale` já lê e não propõe chave nova nem renomeia nada.
  Se o v0.2 mudar a chave ou a semântica, a figure segue o contrato novo — está em
  `## Open Decisions`, não resolvido aqui.
- **ACCEPTED — a figure não mede content drift, e o slug do arquivo continua prometendo que mede.**
  O nome do arquivo é a identidade da spec e não muda. O `title`, o H1 e o `## Overview` dizem o que
  foi de fato decidido, e `## Design` §Decisão 2 registra por que o que o slug promete não é
  alcançável. Aceito porque a alternativa — uma spec nova com slug honesto — jogaria fora a medição e
  o histórico que estão aqui.
- **ACCEPTED — a checagem fica menos alta, e um doc genuinamente velho pode ficar parado mais
  tempo.** Aceito porque os dois verdadeiros positivos de 2026-07-29 não foram achados por leitura de
  WARN: foram achados pela revisão de branch do `/specs:conclude`, que é onde a desatualização
  aparece com contexto. A checagem nunca foi o mecanismo que os pegou.

Uma história do premortem não converteu em nada e está descartada de propósito: "a aposentadoria é
lida como 'desatualização não importa' e o `/docs:align` para de cutucar". Não converte porque
`/docs:align` nunca cutucou por causa deste código — `cycle.md:82` já dizia "No" na coluna de
correção pelo sweep, e o `stale-doc` já era excluído do verify gate
(`assets/references/docs-align/conformance.md:130`). Não há comportamento de sweep para perder.

## Tasks

Toda linha de checkbox e todo valor de metadado cabe em **uma** linha: `TASK_META_RE`
(`assets/bin/specs.py:128`) só casa metadado de uma linha, e uma continuação indentada é
silenciosamente descartada — o executor receberia um `pattern:` cortado ao meio.

### 1. Aposentar a emissão

- [ ] 1.1 Tirar a chamada de `check_stale` de `_validate_text` e o WARN que `check_stale` devolve, deixando a função como medição pura
      files: plugins/quenching/assets/hooks/okf-validate.py
      pattern: plugins/quenching/assets/hooks/okf-validate.py — o branch `log.md` de `_validate_text` (:1021), esta mesma aposentadoria já feita
      verify: test "$(python3 plugins/quenching/assets/hooks/okf-validate.py docs | grep -c stale-doc)" = 0
- [ ] 1.2 Deixar o código reconhecido no lugar da emissão — um comentário nomeando `stale-doc`, o motivo e o precedente, na forma do comentário do `log.md`
      files: plugins/quenching/assets/hooks/okf-validate.py

### 2. A medição, por entrada do `resource:`

- [ ] 2.1 Trocar `_git_last_commit_date` de um pathspec com todas as entradas para uma chamada por entrada, devolvendo entrada, kind, data e intervalo contra o `timestamp`
      files: plugins/quenching/assets/hooks/okf-validate.py
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs --activity
- [ ] 2.2 Marcar como escopo não medido o doc cujas entradas resolvíveis são zero — toda entrada `uri` ou `unknown` — em vez de devolver vazio e ler como eternamente fresco
      files: plugins/quenching/assets/hooks/okf-validate.py

### 3. A figure

- [ ] 3.1 Adicionar `--activity` ao `run_cli`, em texto, ordenado pelo maior intervalo primeiro e sem código de achado em nenhuma linha
      files: plugins/quenching/assets/hooks/okf-validate.py
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs --activity
- [ ] 3.2 Provar que a lista de findings do `--json` continua um array com as quatro chaves de hoje
      files: plugins/quenching/assets/hooks/okf-validate.py
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs --json
- [ ] 3.3 Decidir conforme `## Open Decisions` se `--activity --json` entra nesta versão, medindo a passada num bundle de ~200 docs, e implementar se a resposta for sim
      files: plugins/quenching/assets/hooks/okf-validate.py

### 4. A fixture, e a mutação que a torna verificação

- [ ] 4.1 Fixture no `selftest` que falha se a emissão do WARN voltar e se o escopo não medido sair da figure
      files: plugins/quenching/assets/hooks/okf-validate.py
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py selftest
- [ ] 4.2 Rodar a passada de mutação de `docs/standards/quality/selftest-mutation.md` contra a fixture 4.1 — quebrar cada regra, ver falhar, reverter — e registrar o resultado
      files: plugins/quenching/assets/hooks/okf-validate.py

### 5. As referências e a semente publicada

- [ ] 5.1 Reescrever a §Staleness e a linha do verify gate de `conformance.md` para descrever a figure em vez de um WARN
      files: plugins/quenching/assets/references/docs-align/conformance.md
- [ ] 5.2 Corrigir a linha de roteamento de `cycle.md`, que hoje lista `stale-doc` como achado
      files: plugins/quenching/assets/references/docs-align/cycle.md
- [ ] 5.3 Atualizar as seis citações de `stale-doc` em `commands/docs/status.md` e acrescentar a linha da figure na tabela da §5, sem dar código de achado a nenhuma
      files: plugins/quenching/commands/docs/status.md
- [ ] 5.4 Ajustar a entrada da semente publicada que descreve `stale-doc`
      files: plugins/quenching/assets/docs/knowledge/glossary.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/docs
- [ ] 5.5 Atualizar as entradas **Advisory finding** e **Resource glob set** do glossário do repo via `/docs:define`

### 6. O standard e o fechamento

- [ ] 6.1 Escrever `docs/standards/quality/bundle-verification.md` — a §Staleness registra a regra que esta spec prova, com a medição de 12 em 26 como evidência (`authority: current` uma vez provado)
      files: docs/standards/quality/bundle-verification.md
- [ ] 6.2 Bump do lockstep de versão conforme `docs/standards/ci-cd/versioning-release.md` — `VERSION`, os dois manifests e os três scripts
      files: plugins/quenching/VERSION, plugins/quenching/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/bin/skills.py, plugins/quenching/assets/hooks/okf-validate.py
- [ ] 6.3 Rodar o bloco de verificação inteiro do `CLAUDE.md` e conferir que `okf-validate.py docs` imprime `0 error(s), 2 warning(s)`
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
