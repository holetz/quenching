---
slug: decide-plans-index-need
title: Reassess whether specs/plans/index.md is needed
verification: per-section
priority: {level: 6, criticality: medium, date: 2026-07-29}
refined: {mode: adversarial, date: 2026-07-30}
approved: {date: 2026-07-30}
branch: {base: main, work: plan/decide-plans-index-need}
---

# Reassess whether specs/plans/index.md is needed

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

Todo spec ativo deste repo é um arquivo em `specs/plans/`. Dentro dessa pasta existe um `index.md`,
e este spec o retira por inteiro — o arquivo, o seed que o produz e o validador que o checava.

O `## Problem` mostra por que a metade de baixo tinha de sair: é uma tabela gerada que pode estar
errada sem que nada acuse, e neste momento está. O `## Design` mostra por que a metade de cima foi
junto — procurado o dono da prosa, ele existe e não é este arquivo: `spec-driven.md` para a doutrina
da pasta, `QUENCHING.md` para o manual do operador. Um artefato que não é fonte de nada não se paga.

`## Proposal` lista o que fica verdadeiro no fim, e `## Out of Scope` separa este arquivo de duas
coisas que se parecem com ele: as listagens do bundle `docs/`, que são a única navegação dele e por
isso se pagam, e um `plans/index.md` sobrevivente num target repo, que ninguém apaga.

`## Alternatives Considered` guarda as quatro formas recusadas e, em especial, **por que a escolha
inverteu**: manter o arquivo foi a decisão da primeira passada, e perdeu na segunda porque os dois
custos que sustentavam a recusa da retirada não sobreviveram à medição — as "citações vivas" eram
dois links markdown para o seed do plugin, e a prosa "única" era a terceira cópia.
`## Open Decisions` fecha as três perguntas que a decisão respondeu e abre uma só, sobre o nome de
uma reference que sobrevive ao artefato que descrevia.

O resto é execução, ordenada por dependência para que o front nunca fique vermelho no meio:
`## Tasks` tira o validador antes de apagar o arquivo que ele validava, e o arquivo antes dos
ponteiros para ele. `## Risks` reúne os acoplamentos medidos — com destaque para o seed do
`/specs:align`, que desfaria a retirada sozinho — e nomeia os seis specs vizinhos que tocam os
mesmos arquivos, com a fronteira que este mantém em cada caso. `## Impact` declara o único standard
que este spec promete escrever e lista todo arquivo que ele espera tocar; `## Validation` dá os
comandos que provam a retirada, incluindo o que precisa **continuar** funcionando.
## Problem

`specs/plans/index.md` carrega uma GENERATED listing zone reconstruída por
`specs.py plans reindex`, e todo comando que cria, promove ou ranqueia um spec paga uma chamada de
reindex para mantê-la atual. Se esse custo ainda compra alguma coisa é justamente o que ninguém
examinou: a listagem duplica o que `specs.py list`, `specs.py status` e `/specs:status` já derivam
do disco sob demanda, e é a única razão pela qual o validador OKF é apontado para `specs/plans/`
com `--listing-root`.

O defeito não é a duplicação — é o silêncio. Medido neste repo em 2026-07-30:
`declare-repo-body-language` deriva `executing` no disco
(`specs.py status --spec declare-repo-body-language --json`) e está listado na tabela
`### Captured`, em `specs/plans/index.md:118`. Nenhum verificador reclama:
`okf-validate.py specs/plans --listing-root` responde `0 error(s), 0 warning(s) — OK — bundle
conforms`, e `specs.py validate` responde 0 findings. A listagem está errada agora, e a pilha
inteira de verificação diz que o front está conformante.

Duas coisas dão o "por que agora":

- `/specs:conclude` é o único comando que **remove** um spec de `plans/`, e nunca reindexa: zero
  ocorrências de `reindex` em `commands/specs/conclude.md`, e `cmd_promote` faz um `git mv` sem
  tocar na zona. Medido em sandbox — depois do promote,
  `okf-validate.py specs/plans --listing-root` emite `index-broken-link` em nível WARN e sai com
  **exit 0**, então um comando que ramifica só no exit code enxerga um pass. A zona só volta a
  bater com o disco no próximo `/specs:create`, `/specs:triage` ou `/specs:align`.
- A condição de convergência declarada exige que a GENERATED zone "matches disk"
  (`assets/references/specs-align/conformance.md` §The convergence condition), e nenhum programa
  consegue avaliar isso: `specs.py` não emite campo `changed` em lugar nenhum, enquanto
  `skills.py` emite o dele em `assets/bin/skills.py:1369` — e é nesse campo que a mesma condição
  se apoia para o front `.claude/`. Pior: `assets/references/specs-create/plans-zone.md` e
  `commands/specs/triage.md` mandam o comando **ler** um campo `changed` que o tool nunca produziu.

O que este spec deve resolver é se o arquivo fica, encolhe para um ponteiro estático, ou sai — e o
que cada opção custa em `/specs:create`, `/specs:conclude`, `/specs:align` e no caminho de
conformance `--listing-root`.

## Proposal

- O artefato `plans/index.md` é **retirado por inteiro**: o plugin para de semeá-lo, nenhum comando
  o cria ou reconstrói, e o `specs/plans/index.md` deste repo sai por `git rm`.
- `assets/specs/plans/index.md` deixa de existir. A prosa dele **não precisa de novo endereço** —
  é a terceira cópia, medido em 2026-07-30: o layout e o §Why one active folder em
  `assets/references/specs-develop/spec-driven.md:30-53`, a tabela de derived stages em
  `spec-driven.md:194` e `assets/specs/QUENCHING.md:419`, o schema de frontmatter em
  `spec-driven.md:79`, e o roteamento "o que não vai aqui" em
  `assets/references/docs-add/homes.md:58`.
- As duas citações que hoje resolvem no seed — `commands/specs/create.md:12` e
  `commands/specs/triage.md:13` — **perdem o link**: `specs/plans/` vira texto puro nos dois bodies.
- `specs.py` perde `cmd_plans`, `render_plans_zone`, `PLANS_EMPTY` e o uso de `GEN_BEGIN`/`GEN_END`;
  o subparser `plans` sai da superfície do tool, e `specs.py --help` não o oferece mais. Saem
  **dois** findings: `sp-no-generated-zone` e `sp-no-plans-index` — este último também, porque o
  arquivo deixa de ser esperado.
- Os quatro command bodies que hoje chamam `plans reindex` — `commands/specs/create.md`,
  `commands/specs/triage.md`, `commands/specs/align.md`, `commands/docs/import-memory.md` — perdem
  esse passo e não ganham nada no lugar dele. `/specs:align` para de semear o arquivo.
- `okf-validate.py` perde o modo `--listing-root` e `_is_spec_file`. `index.md` **continua em
  `RESERVED` e em `hard_block_exempt()`** — o bundle `docs/` continua produzindo o nome, então
  retirar nunca vira desreservar.
- Um `plans/index.md` sobrevivente num target repo já alinhado continua legível e gravável: nenhum
  sweep o cria, o apaga, ou o reporta como defeito.
- A condição de convergência do front `specs/` passa a citar só o que um programa consegue decidir:
  `specs.py doctor` e `specs.py validate`.
- Fica escrita uma regra durável em `docs/standards/`: uma listagem gerada só se paga quando um
  programa consegue provar que ela está fresca.
## Out of Scope

- **As GENERATED zones dos `index.md` do bundle `docs/`.** É o que mais gente vai confundir com
  in-scope, e é um artefato diferente: elas são a *única* navegação do bundle — um doc que nenhum
  index alcança é invisível, e `index-orphan` / `dir-no-index` são contrato estrutural
  (`docs/standards/quality/bundle-verification.md` §What is machine-checked, and at which
  severity). Não existe nenhum `docs.py list` derivando aquilo do disco sob demanda, então lá a
  listagem não duplica nada e a comparação não se transfere.
- **Tirar `index.md` de `RESERVED`.** Proibido por
  `docs/standards/architecture/retiring-a-reserved-artifact.md` §The rule, e irrelevante aqui de
  qualquer forma: o nome continua sendo produzido pelo bundle `docs/`, então a reserva não fica
  órfã.
- **Apagar um `plans/index.md` que sobreviva em qualquer target repo.** Retirar significa que
  ninguém mais produz o artefato; nunca que um sweep destrói conteúdo que não é dele. O `git rm`
  desta retirada é do arquivo **deste** repo e do asset **deste** plugin, e de mais nada.
- **Reescrever a prosa do seed em outro endereço** — um `specs/plans/README.md`, ou uma seção nova
  em `assets/specs/QUENCHING.md`. Recusado por medição: cada papel do arquivo já tem dono
  (`## Design`), e um endereço novo seria a quarta cópia.
- **Renomear `assets/references/specs-create/plans-zone.md`.** O arquivo sobrevive à retirada com
  duas das cinco seções, e o nome passa a descrever um artefato que não existe — mas 18 arquivos o
  citam, e uma renomeação de reference tem raio próprio. Fica em `## Open Decisions` com o default
  de manter o nome.
- **Dar nome ao stage `plans`** que hoje aparece como `### Plans` na zona. Ele é o assunto do spec
  `name-the-scaffolded-stage`, e continua existindo em `next --front` e `status` mesmo sem zona.
- **Reordenar, renomear ou remover qualquer derived stage**, e qualquer edição em
  `assets/specs/schema.json`.
- **Escrever um checker de staleness de zona em `okf-validate.py` ou em `specs.py`.** Foi
  considerado e recusado (`## Alternatives Considered`, alternativa A): um checker novo é o gasto
  certo para um artefato que se paga, e este não se paga.
- **Consertar a ausência de reindex em `/specs:conclude` mantendo o arquivo.** É a mesma opção
  recusada acima, vista pelo outro lado: se o artefato fica, esse conserto é obrigatório; como ele
  sai, o buraco fecha sozinho.
## Impact

Escopo declarado para revisão humana. O contrato que **governa** esta retirada —
`docs/standards/architecture/retiring-a-reserved-artifact.md` — não aparece abaixo de propósito:
ele é seguido, não escrito, e já está em `authority: current`.

### Standards this spec will write into docs/standards/

- `docs/standards/architecture/generated-listings.md` — uma listagem gerada só se paga quando um
  programa consegue provar que ela está fresca; o corolário é o critério de decisão (existe um
  comando que deriva o mesmo fato do disco sob demanda?), e o caso dos `index.md` do bundle `docs/`
  é o contraexemplo que delimita a regra

### Standards at `authority: background` this spec may resolve

- `docs/standards/quality/selftest-mutation.md` — as guardas desta retirada são exatamente dois
  selftests que precisam falhar quando ela é desfeita; se se provarem, é evidência para promover
  aquele standard a `current`

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/specs.py` — `cmd_plans`, `render_plans_zone`, `PLANS_EMPTY`,
  `GEN_BEGIN`/`GEN_END`, o subparser `plans`, e os findings `sp-no-generated-zone` e
  `sp-no-plans-index`
- `plugins/quenching/assets/hooks/okf-validate.py` — o modo `--listing-root` e `_is_spec_file`
- `plugins/quenching/assets/specs/plans/index.md` — **apagado**; o plugin para de semear o artefato
- `specs/plans/index.md` — **apagado** deste repo por `git rm`
- `plugins/quenching/commands/specs/create.md`, `commands/specs/triage.md`,
  `commands/specs/align.md`, `commands/docs/import-memory.md` — os quatro bodies que chamam
  `plans reindex`; os dois primeiros também perdem o link da citação, e `align.md:163-164` perde o
  seed
- `plugins/quenching/commands/specs/status.md` — lê `plans/index.md` e roda `--listing-root`
- `plugins/quenching/assets/references/specs-create/plans-zone.md` — dono declarado do contrato da
  zona; perde §The GENERATED zone e §The on-write check, mantém §Resolving the tool e §The `specs/`
  front records itself
- `plugins/quenching/assets/references/specs-align/conformance.md`,
  `assets/references/align/convergence.md`, `assets/references/align/sweep-doctrine.md` — os
  códigos e a condição de convergência
- `plugins/quenching/assets/references/specs-develop/spec-driven.md` — a árvore de layout, a
  cláusula `--listing-root`, a linha da zona em §Derived stages e a do subcomando na tabela do tool
- `plugins/quenching/assets/references/docs-add/homes.md`,
  `assets/references/docs-align/migration.md` — os apartes que remetem à zona
- `plugins/quenching/assets/bin/skills.py:1557` — comentário que cita `plans-zone.md`
- `plugins/quenching/assets/checks/functional-checks.sh:134` — o fixture que escreve um
  `specs/plans/index.md`
- `plugins/quenching/assets/specs/QUENCHING.md`, `assets/claude/QUENCHING.md`,
  `plugins/quenching/README.md`, `assets/README.md` — as linhas que descrevem a zona ou o flag
- `specs/QUENCHING.md` — a cópia semeada **neste** repo, que fica obsoleta junto
- `CLAUDE.md` — o link direto em `:90` quebra, e a receita de verificação invoca
  `okf-validate.py assets/specs/plans --listing-root`, que deixa de existir
- `plugins/quenching/VERSION` — o lockstep
## Validation

A política é `verification: per-section`: cada seção de tasks fecha com um comando que roda. A ordem
das seções é o que torna isso possível — o validador sai **antes** do arquivo que ele validava, e o
arquivo sai antes dos ponteiros para ele. Invertida, a seção do meio deixaria o front sem poder
reportar clean.

Rodado de `plugins/quenching/`, salvo indicação em contrário.

**O flag saiu do validador:**

```bash
python3 assets/hooks/okf-validate.py --help | grep -c listing-root   # 0
```

**A superfície do tool perdeu o subcomando:**

```bash
python3 assets/bin/specs.py --help | grep -c plans     # 0
python3 assets/bin/specs.py plans reindex              # exit != 0, erro de argumento inválido
```

**O artefato não é mais produzido nem existe:**

```bash
test ! -e assets/specs/plans/index.md                  # exit 0
test ! -e ../../specs/plans/index.md                   # exit 0 (da raiz do repo)
python3 assets/bin/specs.py validate --json            # ok: true, 0 findings
python3 assets/bin/specs.py doctor --json              # nenhum sp-no-plans-index, nenhum
                                                       # sp-no-generated-zone, nenhum código novo
```

**Nada no plugin nem no repo ainda chama o que foi retirado** (o único texto que pode sobrar é
histórico, em `specs/archive/**` e nos specs irmãos, que este spec não toca):

```bash
grep -rn "plans reindex\|--listing-root\|render_plans_zone\|sp-zone-stale\|sp-no-generated-zone\|sp-no-plans-index" \
  plugins/quenching/ CLAUDE.md specs/QUENCHING.md   # nenhuma linha
grep -rn "plans/index\.md" plugins/quenching/ CLAUDE.md specs/QUENCHING.md   # nenhuma linha
```

**As três guardas de selftest passam, e as duas novas falham quando a retirada é desfeita:**

```bash
python3 assets/bin/specs.py selftest
python3 assets/bin/skills.py selftest
python3 assets/hooks/okf-validate.py selftest
```

**O bundle e a superfície de comandos seguem limpos:**

```bash
python3 assets/hooks/okf-validate.py assets/docs        # 0 error(s), 0 warning(s)
python3 assets/bin/skills.py --root . doctor --json     # 26 commands, no findings
python3 assets/bin/skills.py --root . lint --json       # exit 0
```

**O fixture do harness ainda monta uma caixa válida:**

```bash
./assets/checks/functional-checks.sh                    # exit 0
```

**O lockstep de versão concorda:**

```bash
cat VERSION
python3 assets/bin/specs.py --version
python3 assets/bin/skills.py --version
python3 assets/hooks/okf-validate.py --version
```

**Invariante que precisa continuar valendo:** `okf-validate.py assets/docs` segue checando
`index-orphan` e `index-broken-link` dentro do bundle, e `index.md` segue em `RESERVED` e em
`hard_block_exempt()`. A retirada é do modo `--listing-root`, nunca dos checks nem da reserva — se
um doc do bundle deixar de ser flagrado por órfão, ou um `index.md` sobrevivente começar a reportar
`no-frontmatter`, a mudança foi longe demais.

**O que esta validação deliberadamente não cobre:** que um humano prefira a tabela ao
`specs.py list`. Não é verificável por comando, e não é mais uma pergunta aberta — foi respondida
em 2026-07-30 e está registrada em `## Open Decisions`.
## Design

### A decisão: o arquivo inteiro é duplicação, não só a metade de baixo

`plans/index.md` tem dois papéis. A primeira passada deste spec olhou de onde a verdade de cada um
vem e concluiu que só um apodrece. Faltava a terceira coluna — **quem já é dono daquele papel** —
e é ela que muda o resultado.

| Papel | De onde a verdade vem | Custo de staleness | Quem já é dono |
| --- | --- | --- | --- |
| Prosa fixa — o que é o folder, a tabela de derived stages, para onde o split de folders foi, o schema de frontmatter, o que não vai ali | escrita à mão | nenhum: descreve o contrato, não o disco | `spec-driven.md:30-53` (layout, §Why one active folder), `:79` (frontmatter), `:194` (derived stages); `assets/specs/QUENCHING.md:419` (a mesma tabela, no manual semeado); `docs-add/homes.md:58` (o roteamento) |
| GENERATED zone — contagens mais uma tabela por stage | `plans/*.md` no disco | total: reconstruída por 4 comandos, quebrada por um 5º, checável por nenhum | nada — é uma cópia de `specs.py list` |

O corte não passa mais **dentro** do arquivo. A prosa parecia insubstituível porque ninguém tinha
procurado o dono dela; procurado, o arquivo inteiro é duplicação — a metade de baixo duplica o
disco, a metade de cima duplica `spec-driven.md`. Um artefato que não é fonte de nada não se paga,
e retirá-lo é subtração sem contrapartida.

### As duas citações não eram um contrato

`commands/specs/create.md:12` e `commands/specs/triage.md:13` linkam a frase `specs/plans/` para
`${CLAUDE_PLUGIN_ROOT}/assets/specs/plans/index.md` — o **seed do plugin**, não o arquivo que um
target repo produz. São dois links markdown, e o remédio é tirar o link: `specs/plans/` fica como
texto puro. Escolhido sobre repontar para `spec-driven.md` porque um body que explica a pasta em
duas frases não precisa mandar o leitor a lugar nenhum, e sobre repontar para
`assets/specs/QUENCHING.md` porque aquele arquivo é um seed — a cópia que o leitor deve abrir é o
`specs/QUENCHING.md` do próprio repo, e um `${CLAUDE_PLUGIN_ROOT}` o levaria à errada.

### A regra durável que sai daqui

**Uma listagem gerada só se paga quando um programa consegue provar que ela está fresca.** O
corolário é o critério de decisão, e ele é verificável antes de escrever qualquer código: se existe
um comando que deriva o mesmo fato do disco sob demanda, a listagem gerada é uma segunda fonte da
verdade e a verificação dela é puro custo. Se não existe — o caso dos `index.md` do bundle `docs/`,
que são a própria navegação — a listagem é a fonte, e aí o checker é obrigatório e se paga.

Isso é a doutrina do próprio front aplicada a um artefato que escapou dela.
`assets/references/specs-develop/spec-driven.md` §Frontmatter já diz que "two declared sources of
one fact will diverge", e §Identity que "one truth never gets two declared sources" — foi o
argumento que matou o campo `created`, o campo `phase` e o campo `ready`. O arquivo é a mesma forma
duas vezes: uma zona declarada para um fato derivável, e uma prosa declarada para um contrato que
já tem dono.

### O que a retirada exige, procedimentalmente

`docs/standards/architecture/retiring-a-reserved-artifact.md` é vinculante e governa este caso
(`plans/index.md` casa com `index.md`, que está em `RESERVED`). As três pernas dele, traduzidas
para cá:

1. **Remover o checker** — os quatro códigos `sp-*` da listagem, e o modo `--listing-root` inteiro,
   que fica sem chamador.
2. **Parar de produzir** — nenhum comando reindexa, nenhum align semeia, e o asset sai do plugin.
3. **Não mudar mais nada** — `index.md` fica em `RESERVED` e em `hard_block_exempt()`, porque o
   bundle `docs/` continua produzindo o nome.

E o standard §The consequence for disposition **resolve sozinho** o que a primeira passada deixava
aberto: um artefato retirado é legível e gravável para sempre, `/specs:align` nem o cria nem o
apaga, e `/specs:status` o reporta como figura sem código de finding. Manter o arquivo tornava isso
ambíguo — uma *zona* dentro de um artefato mantido, semeada e portanto ownada pelo align, que o
standard não cobre. Retirando o arquivo não há ambiguidade: é o caso exato que ele descreve.

A perna que o standard chama de guarda: uma regra cujo modo de falha é silencioso precisa de teste,
não de parágrafo. Aqui isso é uma asserção de `specs.py selftest` de que `plans reindex` não existe
mais na superfície do tool, e uma de `okf-validate.py selftest` de que `--listing-root` saiu
enquanto `index.md` segue em `RESERVED` e em `hard_block_exempt()`.

### Contratos que este design não pode contrariar

- `docs/standards/architecture/retiring-a-reserved-artifact.md` — retirar, nunca desreservar.
- `docs/standards/quality/bundle-verification.md` §What is machine-checked — nenhum check novo
  nasce em ERROR, e o que sai daqui é subtração, não escalada.
- `docs/standards/quality/selftest-mutation.md` — as guardas acima têm que falhar quando a
  retirada é desfeita.
- `docs/standards/ci-cd/versioning-release.md` — `specs.py` e `okf-validate.py` mudam, então o
  lockstep de versão vale: `VERSION` e os três scripts precisam continuar concordando.
- `assets/references/specs-create/plans-zone.md` é hoje o dono declarado do contrato da zona; com o
  artefato fora, ele perde duas das cinco seções e não pode ficar descrevendo o que não existe.
## Alternatives Considered

As quatro formas inteiras que o spec podia tomar. As três primeiras são as que o `## Problem`
nomeou; a quarta foi a escolhida na primeira passada e perdeu na segunda.

| Forma | Custo | O que compra | O que impede depois |
| --- | --- | --- | --- |
| **A. Manter a zona e instrumentá-la** — `changed` de verdade, um checker de staleness, e reindex em `/specs:conclude` | dois acréscimos de código em dois tools, mais um passo novo em `conclude`, mais o passo herdado por todo comando futuro que mexa em `plans/` | uma listagem navegável no GitHub que passa a ser confiável | nada; é a opção conservadora |
| **B. Retirar `plans/index.md` inteiro** *(escolhida)* | uma retirada em três tools, seis command bodies, cinco references e dois manuais; a pasta fica sem explicação interna | a subtração máxima: nenhum artefato, nenhum checker, nenhuma cópia de prosa | nada — cada papel do arquivo tem dono medido em outro lugar |
| **C. Encolher para um ponteiro estático de poucas linhas** | reescrever a prosa que já está boa | subtração quase máxima | nada relevante |
| **D. Retirar só a zona, manter o arquivo e sua prosa** | uma retirada em três tools, quatro command bodies e três references, mais um arquivo mantido para sempre | remove a única parte que apodrece | nada que a zona oferecia |

Por que cada uma perdeu:

- **A perdeu por aritmética, não por gosto.** Ela paga dois checks novos para manter uma cópia de
  um fato que `specs.py list` entrega do disco sob demanda. O argumento de
  `docs/standards/quality/bundle-verification.md` §Prose does not enforce — check determinístico ou
  lacuna aceita, nunca um terceiro parágrafo — é o que justifica pagar por um check; ele não
  justifica pagar por um check que existe só para vigiar uma duplicata evitável.
- **C perdeu por ser B com passos extras.** Se a prosa não se paga, encurtá-la não é uma decisão —
  é adiá-la.
- **D perdeu por aritmética também**, e é a inversão que esta segunda passada registra. Ela mantém
  um arquivo inteiro, e todo o custo de manutenção dele, para preservar uma terceira cópia de prosa
  que dois donos declarados já carregam.
- **Fazer nada** não está na tabela porque já é o estado atual, e o estado atual é o que o
  `## Problem` mede: uma listagem errada agora, com toda a pilha de verificação verde.

### Por que a escolha inverteu

A primeira passada recusou B por dois custos que, medidos em 2026-07-30, não existem.

1. **"Quebra duas citações vivas."** As duas apontam para o **seed do plugin**
   (`${CLAUDE_PLUGIN_ROOT}/assets/specs/plans/index.md`), não para o arquivo produzido. São dois
   links markdown num body, e o remédio é tirar o link.
2. **"Perde a única prosa que registra para onde o split `backlog/`+`ready/` foi."** Falso:
   `spec-driven.md:50-53` é o dono declarado daquela história, e `assets/specs/QUENCHING.md:77` a
   repete no manual que `/specs:align` semeia em todo target repo. A tabela de derived stages, o
   schema de frontmatter e o roteamento "o que não vai aqui" têm o mesmo tratamento.

Nenhum dos dois motivos sobreviveu à medição, e com eles fora D não compra mais nada que B não
compre — só custa um arquivo a mais, para sempre.
## Open Decisions

- ~~**Alguém realmente lê a zona como view de status?**~~ **RESOLVIDA 2026-07-30:** não. O humano
  decidiu excluir o arquivo inteiro, o que torna a alternativa A definitivamente morta e inverte a
  escolha de D para B (`## Alternatives Considered` §Por que a escolha inverteu).
- ~~**`/specs:align` remove uma GENERATED zone sobrevivente de um `plans/index.md` de target
  repo?**~~ **RESOLVIDA por contrato:** a pergunta só existia porque a primeira forma mantinha o
  arquivo, deixando uma *zona* dentro de um artefato mantido — um caso que o standard não cobre.
  Com o artefato inteiro retirado, `retiring-a-reserved-artifact.md` §The consequence for
  disposition decide direto: nenhum sweep cria ou apaga um artefato retirado, e um sobrevivente é
  legível e gravável para sempre.
- ~~**`sp-index-frontmatter` sobrevive como regra de prosa, ou a lacuna é aceita e registrada?**~~
  **MOOT:** sem artefato produzido não há frontmatter para checar, nem lacuna para registrar. O
  código sai junto com o modo `--listing-root` que o emitia.
- ~~**NOVA — o nome `assets/references/specs-create/plans-zone.md` descreve um artefato
  retirado.**~~ **RESOLVIDA 2026-07-30, contra o default:** renomeado para `specs-front.md`. O
  humano escolheu o nome mais largo, que cobre as três seções sobreviventes — §The folder is the
  listing, §Resolving the tool e §The `specs/` front records itself — em vez de `tool-resolution.md`,
  que nomearia só a dominante. Renomeação code-coupled, aplicada atômica no commit da task 5.1: 21
  sítios de citação medidos, 17 arquivos do plugin reescritos, `plans-zone` a zero, e as quatro
  frases que descreviam a citação como "the listing-zone format" corrigidas junto. As 225 citações
  em link markdown do plugin resolvem.
## Risks

- **Retirar o artefato sem retirar `--listing-root` no mesmo movimento.** Medido em 2026-07-30: com
  a zona fora e o flag no lugar são 32 specs, 32 warnings `index-orphan`; com o arquivo fora
  também entra `dir-no-index`. A condição de convergência exige zero deles, então o front `specs/`
  nunca mais reportaria clean. *Mitigação:* `## Tasks` tira o validador **primeiro** — o flag sai
  na seção 1, o arquivo só na seção 3 —, de modo que nenhuma fronteira de verificação cai no meio
  do acoplamento.
- **`/specs:align` volta a semear o arquivo e desfaz a retirada.** É a perna que se esquece: hoje
  `commands/specs/align.md:163-164` semeia `specs/plans/index.md` a partir de
  `assets/specs/plans/index.md`, e `conformance.md:112` descreve o seed como não-evidence-gated,
  isto é, incondicional. *Mitigação:* mais forte aqui do que seria mantendo o arquivo — o asset
  **não existe** para semear, e a guarda de selftest afirma que `plans reindex` não existe mais na
  superfície do tool.
- **A receita de verificação do `CLAUDE.md` quebra silenciosamente.** Ela invoca
  `okf-validate.py assets/specs/plans --listing-root` e o link `specs/plans/index.md` em `:90`.
  Uma receita que aponta para o que não existe é pior que nenhuma, porque quem a segue conclui que
  o repo está quebrado. *Mitigação:* as duas linhas saem na mesma seção que remove o flag, e
  `/docs:harness` é quem edita o `CLAUDE.md`.
- **Um target repo com o arquivo sobrevivente e ninguém para atualizá-lo.** O humano lê uma
  listagem congelada e trabalha no spec errado — exatamente o modo de falha que este spec existe
  para matar, só que sem nem o reindex ocasional que hoje o disfarça. *Mitigação:* `/specs:status`
  o reporta como figura sem código de finding
  (`docs/standards/architecture/read-only-views.md` §What the read command therefore owns), e o
  manual `specs/QUENCHING.md` — semeado por `/specs:align` em todo target repo — diz que a listagem
  viva é `specs.py list`. O descarte em si é decisão do target repo, per `## Out of Scope`.
- **Colisão com o sibling `split-specs-py-backlog-renderer`.** Aquele spec quer *extrair*
  `render_plans_zone` de `specs.py` para tirar o arquivo de cima do limiar de ~1.200 linhas; este
  quer *deletar* a mesma função. É a mesma função, e os dois não podem ganhar. Aquele spec ainda
  usa `git diff --stat specs/plans/index.md` como baseline em `## Validation`, um arquivo que este
  apaga. *Fronteira que este spec mantém:* ele remove `cmd_plans` e `render_plans_zone` e não toca
  em mais nenhum renderer nem no limiar de linhas; a decisão de qual dos dois roda primeiro é do
  humano, e este spec não assume o resultado do outro. Se aquele landar primeiro, a task de remoção
  aqui passa a mirar o módulo extraído em vez da função inline.
- **Sobreposição com o sibling `name-the-scaffolded-stage`.** Sob a forma anterior aquele spec
  perdia só o comentário da zona; sob esta, sua task 3.1 perde o **arquivo inteiro** que declara em
  `files:`. Ele já declarou em `:138` que a existência de `plans/index.md` é decisão deste spec e
  em `:360` que este pode concluir que não é necessário, então a fronteira está reconhecida dos
  dois lados. *Fronteira:* este spec remove **um renderizador** do estado sem nome e não decide
  nada sobre nomeá-lo — o estado continua existindo em `derive_stage`, `next --front` e `status`.
  O risco real é aquele spec perder seu sintoma mais visível e a decisão nunca ser tomada; nomeá-lo
  continua valendo por conta própria.
- **Sobreposição com o sibling `commit-on-worktree-specs`.** Ele declara em `:363` que o destino de
  `plans/index.md` é decidido pelo resultado **deste** spec, e aceita em `:403` a staleness do
  arquivo depois de um commit. *Fronteira:* este spec fecha aquela pendência com "não há nada para
  regenerar", e não toca em mais nada do escopo de commit dele.
- **Sobreposição com o sibling `wire-the-overview-consumers`.** A listagem não é um dos três
  consumidores dele, então não há colisão de design; ele já deixa `render_plans_zone` explicitamente
  fora de escopo em `:475-476`. Há colisão de arquivo: os dois editam `commands/specs/triage.md`.
  *Fronteira:* este spec só remove o passo de reindex, a citação de `--listing-root` e o link da
  linha 13 naquele body, e não mexe em como o triage renderiza cada spec.
- **Sobreposição com o sibling `dedupe-specs-py-spec-reader`.** `cmd_plans` faz sua própria cópia
  inline de read-parse-derive em `assets/bin/specs.py:2961-2969` — uma das cópias que aquele spec
  vai dobrar em um helper —, e ele usa `git diff --exit-code specs/plans/index.md` como asserção de
  idempotência em `:308` e `:497-498`, sobre um arquivo que este apaga. *Fronteira:* apagar
  `cmd_plans` remove um dos call sites; este spec não escreve o helper nem toca nas outras cópias.
- **Sobreposição com o sibling `revise-standards-subject-folders`.** O standard declarado em
  `## Impact` mora em `docs/standards/architecture/`, e aquele spec revisa justamente as subject
  folders fixas. *Fronteira:* este spec escreve o standard no path que existir quando a task rodar,
  e não propõe nem impede nenhuma mudança de folder.
- **O lockstep de versão passar batido.** `specs.py` e `okf-validate.py` mudam, então `VERSION` e
  os três scripts precisam continuar concordando
  (`docs/standards/ci-cd/versioning-release.md`). *Mitigação:* uma task explícita de release,
  verificada pelos comandos de lockstep do `CLAUDE.md`.
- **ACCEPTED — a pasta `specs/plans/` fica sem explicação interna.** Quem a abre num target repo
  passa a ver só arquivos datados. Aceito porque `specs/QUENCHING.md` é semeado em todo target repo
  pelo próprio `/specs:align` e já carrega a tabela de derived stages, a história do
  `backlog/`+`ready/` e a superfície do `specs.py`: a explicação não some, muda de endereço um
  nível acima, para um arquivo que não apodrece. Um `README.md` na pasta foi considerado e recusado
  em `## Out of Scope` — seria a quarta cópia da mesma prosa.
- **ACCEPTED — a retirada é barata de desfazer, e é isso que autoriza fazê-la.** `cmd_plans` e
  `render_plans_zone` são cerca de 65 linhas recuperáveis do `git log`, o arquivo inteiro está no
  histórico, a zona é determinística, e não há estado nenhum para migrar de volta: um único reindex
  a reconstruiria do disco sem perda. A assimetria é o argumento — a remoção é reversível, e a
  staleness que ela mata não é detectável.
## Handoff

<!-- AUDIENCE: agent. Warned on when empty once the ready gate is met.

     The context an executor needs and cannot derive: the state of play, the conventions in
     force, what was already tried. Small by construction — it is sent with EVERY task.

     Refresh is bound to EVENTS, not judgment: the orchestrator rewrites this after each
     committed task. Staleness is this section's failure mode. -->

Worktree `../claude-quenching-decide-plans-index-need`, branch `plan/decide-plans-index-need`
cut from `main`. Um commit por task, subject `plan/<slug>: <id> <título>`.

**Estado após 3.3.** Seções 1, 2 e 3 fechadas — **o artefato não existe mais em lugar nenhum**.
Os dois tools estão limpos e cada um carrega a guarda da própria retirada, mutation-proven
(4/4 e 2/2). Os dois arquivos foram apagados, o seed saiu do `/specs:align`, os cinco command
bodies perderam o reindex e o flag, e a caixa do `functional-checks.sh` monta sem o arquivo.
`assets/specs/plans/.gitkeep` mantém a pasta no git no lugar do `index.md`.

Sobra a documentação: seção 4 (dois links + `CLAUDE.md`), seção 5 (references e manuais),
seção 6 (o standard novo). Nada mais em `commands/**` ou nos tools.

**Três correções de fato que o executor precisa saber:**

1. **Dois `verify:` estavam defeituosos, em direções opostas**, e foram corrigidos nas tasks 1.1
   e 2.1 (autorizado pelo humano em 2026-07-30). `okf-validate.py` **não tem `--help`** — cai num
   scan normal do bundle, então `--help | grep -c X` nunca falha. E `specs.py --help | grep -c
   plans` nunca passa: `plans/` é pasta real citada no help de `new`, `promote` e `migrate`.
   **Regra ao corrigir um `verify:`: a substituição tem de ser pelo menos tão forte, medida contra
   o blob anterior à task.** As duas atuais discriminam (3→0 e 1→0).
2. `index.md` **nunca esteve** em `hard_block_exempt()` — só em `RESERVED`, e tem de continuar
   fora do skip: negar um `index.md` com `type` de conceito é a função do gate PreToolUse.
   O spec afirma o contrário em `## Proposal`, `## Design` §3, `## Validation` e na task 1.2.
3. Task 7.1 está **bloqueada por contrato**: `docs/standards/ci-cd/versioning-release.md`
   §When the bump happens proíbe bump como task — é do `/specs:conclude` step 5.

**Convenção adotada:** toda guarda de selftest escrita aqui passa por mutation pass
(`docs/standards/quality/selftest-mutation.md`) antes do commit; o resultado vai em
`## Discoveries`.

## Tasks

Cada primeira linha é a task inteira e se lê sozinha — `specs.py next` entrega só ela ao executor.

**A ordem é uma dependência, não uma preferência.** O validador sai antes do arquivo que ele
validava, o arquivo antes dos ponteiros para ele. Invertida, a seção do meio deixa o front `specs/`
sem poder reportar clean — os 32 `index-orphan` medidos em `## Risks`.

As decisões que a primeira passada colocava na seção 1 já estão tomadas e registradas em
`## Open Decisions`; sobra uma, no default de manter, dentro da task 5.1.

### 1. Retirar `--listing-root` primeiro

- [x] 1.1 Remover o modo `--listing-root` e `_is_spec_file` de `okf-validate.py`, preservando `index-orphan` e `index-broken-link` para o bundle
      files: plugins/quenching/assets/hooks/okf-validate.py
      verify: grep -c "listing_root: bool" plugins/quenching/assets/hooks/okf-validate.py
      subject: plan/decide-plans-index-need: 1.1 Remover o modo --listing-root e _is_spec_file de okf-validate.py
      Tem que imprimir `0` — conta as três assinaturas que carregavam o modo. `index.md` continua
      em `RESERVED` — retirar nunca é desreservar. **Correção medida em 2026-07-30:** `index.md`
      nunca esteve em `hard_block_exempt()` e não pode entrar — negar um `index.md` com `type` de
      conceito é a função do gate PreToolUse (`## Discoveries`).
- [x] 1.2 Acrescentar a `okf-validate.py selftest` a asserção de que `--listing-root` saiu enquanto `index.md` segue em `RESERVED` e em `hard_block_exempt()`
      files: plugins/quenching/assets/hooks/okf-validate.py
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py selftest && python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/docs
      subject: plan/decide-plans-index-need: 1.2 Acrescentar a okf-validate.py selftest a guarda da retirada
      É a guarda que `docs/standards/architecture/retiring-a-reserved-artifact.md` §The guard exige:
      tem que falhar se alguém reintroduzir o flag ou tirar o nome da reserva. Escrita como
      `retired_listing_root_failures()`, quatro asserções, mutation pass 4/4 (`## Discoveries`).
      A quarta afirma que `index.md` **não** está em `hard_block_exempt()`, ao contrário do que
      o título desta task diz.
- [x] 1.3 Tirar do `CLAUDE.md` e de `assets/README.md` as duas receitas que invocam o flag retirado
      files: CLAUDE.md, plugins/quenching/assets/README.md
      verify: grep -rn -- "--listing-root" CLAUDE.md plugins/quenching/assets/README.md
      subject: plan/decide-plans-index-need: 1.3 Tirar as receitas que invocam o flag retirado
      Não pode imprimir nenhuma linha. Uma receita que aponta para o que não existe é pior que
      nenhuma. Usar `/docs:harness` para o `CLAUDE.md`.

### 2. Retirar a zona e o subcomando de `specs.py`

- [x] 2.1 Remover `cmd_plans`, `render_plans_zone`, `PLANS_EMPTY`, o subparser `plans` e os findings `sp-no-generated-zone` e `sp-no-plans-index` de `specs.py`
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py --help | grep -cE '^ +plans +'
      subject: plan/decide-plans-index-need: 2.1 Remover a zona e o subcomando plans de specs.py
      Tem que imprimir `0` — conta a LINHA do subcomando, não a palavra: `plans/` é uma pasta real
      citada no help de `new`, `promote` e `migrate`, então um `grep -c plans` cru imprime `3` mesmo
      com a retirada correta (`## Discoveries`). `sp-no-plans-index` sai junto desta vez: o arquivo deixa de ser
      esperado, então um finding por ausência dele seria um checker de um artefato retirado.
- [x] 2.2 Acrescentar a `specs.py selftest` a asserção de que `plans reindex` não existe mais na superfície do tool
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py selftest
      subject: plan/decide-plans-index-need: 2.2 Acrescentar a specs.py selftest a guarda do subcomando
      Escrita para falhar se alguém reintroduzir o subcomando — a segunda perna da guarda que
      `retiring-a-reserved-artifact.md` §The guard exige.

### 3. Parar de produzir o artefato, e apagá-lo

- [x] 3.1 Apagar `assets/specs/plans/index.md` e remover o passo de seed de `commands/specs/align.md`
      files: plugins/quenching/assets/specs/plans/index.md, plugins/quenching/commands/specs/align.md
      verify: test ! -e plugins/quenching/assets/specs/plans/index.md && grep -c "assets/specs/plans/index.md" plugins/quenching/commands/specs/align.md
      subject: plan/decide-plans-index-need: 3.1 Apagar o seed e remover o passo de seed do align
      O `grep` tem que imprimir `0`. Sem asset não há o que semear — é o que torna a retirada
      irreversível por sweep.
- [x] 3.2 Remover o passo de reindex e as menções a `--listing-root` dos cinco command bodies que os têm
      files: plugins/quenching/commands/specs/create.md, plugins/quenching/commands/specs/triage.md, plugins/quenching/commands/specs/align.md, plugins/quenching/commands/specs/status.md, plugins/quenching/commands/docs/import-memory.md
      verify: grep -rn -- "plans reindex\|--listing-root" plugins/quenching/commands/; grep -rn "plans/index\.md" plugins/quenching/commands/ | grep -v "assets/specs/plans/index.md" | grep -v "Never \|retired artifact"
      subject: plan/decide-plans-index-need: 3.2 Remover o reindex e o flag dos cinco command bodies
      Nenhum dos dois pode imprimir linha. `status.md:76` também lê o arquivo — essa leitura sai.
      **Escopo corrigido em 2026-07-30:** o grep cru de `plans/index.md` era largo demais em duas
      direções. Casava os dois links do seed, que são da task 4.1; e casava as próprias linhas
      `Never recreate ...` que esta task ESCREVE — a única guarda que impede um command body de
      voltar a semear o artefato, já que os selftests só cobrem os tools. Um verify que exigisse
      apagá-las mandaria remover a proibição junto com a prática (`## Discoveries`).
- [x] 3.3 Apagar `specs/plans/index.md` deste repo por `git rm` e tirar a linha do fixture de `functional-checks.sh`
      files: specs/plans/index.md, plugins/quenching/assets/checks/functional-checks.sh
      verify: test ! -e specs/plans/index.md && grep -c "specs/plans/index.md" plugins/quenching/assets/checks/functional-checks.sh && bash -n plugins/quenching/assets/checks/functional-checks.sh && python3 plugins/quenching/assets/bin/specs.py doctor --json
      subject: plan/decide-plans-index-need: 3.3 Apagar o index.md deste repo e tirar a linha do fixture
      O `grep` tem que imprimir `0` e o `doctor` sair `0`. `specs/archive/**` nunca é tocado.
      **`functional-checks.sh` retirado deste `verify:` em 2026-07-30**, por contradizer
      `docs/standards/quality/surface-verification.md` §The harness belongs to the skill front,
      que diz literalmente que o harness "is not named in a spec's `## Validation` or a task's
      `verify:`" — ele é do `/skill:new`, e toda corrida vermelha que ele já produziu foi defeito
      dele próprio. A caixa continua montada e válida: `mkdir -p .../specs/plans` fica, só o seed
      do arquivo sai. O mesmo corte vale para `## Validation` (`## Discoveries`).

### 4. Tirar os ponteiros que sobraram

- [x] 4.1 Tirar o link das duas citações de `specs/plans/` em `create.md:12` e `triage.md:13`, deixando texto puro
      files: plugins/quenching/commands/specs/create.md, plugins/quenching/commands/specs/triage.md
      verify: grep -rn "assets/specs/plans" plugins/quenching/commands/
      subject: plan/decide-plans-index-need: 4.1 Tirar o link das duas citacoes de specs/plans/
      Não pode imprimir nenhuma linha. A frase ao redor de cada link explica a pasta em duas frases
      e não precisa mandar o leitor a lugar nenhum — decidido em `## Design`.
- [x] 4.2 Corrigir o link `specs/plans/index.md` do `CLAUDE.md`
      files: CLAUDE.md
      verify: grep -c "plans/index.md" CLAUDE.md
      subject: plan/decide-plans-index-need: 4.2 Corrigir o link plans/index.md do CLAUDE.md
      Tem que imprimir `0`. Usar `/docs:harness`.

### 5. Atualizar as references e os manuais que descrevem o artefato retirado

- [x] 5.1 Cortar de `plans-zone.md` as seções §The GENERATED zone e §The on-write check, e resolver o nome do arquivo com o humano
      files: plugins/quenching/assets/references/specs-create/plans-zone.md
      subject: plan/decide-plans-index-need: 5.1 Cortar as duas secoes da zona e renomear para specs-front.md
      Mantém §Resolving the tool e §The `specs/` front records itself, que não falam da zona. O H1
      passa a nomear o que sobrou. A renomeação do arquivo é a entrada aberta de
      `## Open Decisions` — 18 arquivos o citam, e o default é manter o nome.
- [ ] 5.2 Remover `sp-no-generated-zone`, `sp-zone-stale`, `sp-no-plans-index` e `sp-index-frontmatter` de `conformance.md` e reescrever a condição de convergência do front
      files: plugins/quenching/assets/references/specs-align/conformance.md
      A condição nova cita só `specs.py doctor` e `specs.py validate` — o que um programa decide.
- [ ] 5.3 Tirar a cláusula `--listing-root` do contrato de convergência e da tabela de verificadores por front
      files: plugins/quenching/assets/references/align/convergence.md, plugins/quenching/assets/references/align/sweep-doctrine.md
- [ ] 5.4 Corrigir `spec-driven.md`, `docs-add/homes.md`, `docs-align/migration.md` e o comentário de `skills.py:1557`
      files: plugins/quenching/assets/references/specs-develop/spec-driven.md, plugins/quenching/assets/references/docs-add/homes.md, plugins/quenching/assets/references/docs-align/migration.md, plugins/quenching/assets/bin/skills.py
      A árvore de layout de `spec-driven.md:38` perde a linha do `index.md`, `:56-57` perde a
      cláusula `--listing-root`, `:217` perde a zona da lista de agrupadores e `:312` perde a linha
      do subcomando na tabela do tool.
- [ ] 5.5 Corrigir os manuais e READMEs que descrevem a zona ou o flag
      files: plugins/quenching/assets/specs/QUENCHING.md, plugins/quenching/assets/claude/QUENCHING.md, plugins/quenching/README.md, specs/QUENCHING.md
      verify: grep -rn -- "plans reindex\|--listing-root\|render_plans_zone\|plans/index.md" plugins/quenching/ CLAUDE.md specs/QUENCHING.md
      Não pode imprimir nenhuma linha. `assets/specs/QUENCHING.md` é o seed e `specs/QUENCHING.md` a
      cópia deste repo — as duas ficam obsoletas juntas. `assets/claude/QUENCHING.md:179` cita o
      arquivo como precedente da regra anti-drift do registry; a regra fica, o precedente muda.

### 6. Escrever a regra durável

- [ ] 6.1 Escrever `docs/standards/architecture/generated-listings.md` via `/docs:add`, em `authority: current`
      files: docs/standards/architecture/generated-listings.md
      pattern: docs/standards/architecture/retiring-a-reserved-artifact.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
      Conteúdo: uma listagem gerada só se paga quando um programa consegue provar que ela está
      fresca; o critério de decisão (existe um comando que deriva o mesmo fato do disco sob
      demanda?); e os `index.md` do bundle `docs/` como o contraexemplo que delimita a regra.
      `current` porque esta retirada é a prova.

### 7. Fechar as obrigações de release

- [ ] 7.1 Acertar o lockstep de versão entre `VERSION` e os três scripts
      verify: cat plugins/quenching/VERSION && python3 plugins/quenching/assets/bin/specs.py --version && python3 plugins/quenching/assets/bin/skills.py --version && python3 plugins/quenching/assets/hooks/okf-validate.py --version
      As quatro saídas têm que concordar.
- [ ] 7.2 Rodar a validação inteira de `## Validation` e registrar a saída de cada comando
      verify: python3 plugins/quenching/assets/bin/specs.py validate --json && python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json && python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json

## Discoveries

- okf-validate.py has NO `--help` handler — `--help` falls through to a normal bundle scan of the default docsDir. The `verify:` of task 1.1 (`--help | grep -c listing-root`) therefore printed `0` BEFORE the change too: it is vacuous and cannot fail either way. Same vacuity in `## Validation`. A load-bearing check is `grep -c -- listing_root <file>`. (specs.py DOES have argparse --help, so task 2.1's verify is real.)
- `index.md` was NEVER in `hard_block_exempt()` — that predicate covers EXEMPT (CLAUDE.md/AGENTS.md/QUENCHING.md) plus log.md and README.md. `index.md` is in RESERVED only, and is deliberately NOT hard-block-exempt: the PreToolUse gate's whole job is denying an index.md that carries a concept `type`. The claim appears in `## Proposal`, `## Design` §3, `## Validation` and task 1.2's body; only the RESERVED half is true. Task 1.2's assertion was written against what is actually true.
- Mutation pass run against the new `retired_listing_root_failures()` guard, per docs/standards/quality/selftest-mutation.md: 4 mutations (re-add the _is_spec_file skip · re-add the listing_root param · drop index.md from RESERVED · add index.md to hard_block_exempt) — 4/4 CAUGHT, each failing exactly ONE assertion, which is the discriminating signal that standard asks for. This is the first of the three shipped tools to clear the pass; okf-validate.py's OTHER selftest legs (12 canonical cases + retired-log) were NOT mutation-checked, so the standard's graduation gate to `current` is not met by this spec alone.
- Task 2.1's `verify:` (`specs.py --help | grep -c plans` expecting 0) is defective in the OPPOSITE direction to 1.1's: it can never pass on a CORRECT implementation. `plans/` is a real folder named in three other subcommands' help text (new: 'capture a spec into plans/', promote: 'plans/ -> archive/', migrate: 'backlog/ + ready/ -> plans/'), so it prints 3. The subcommand IS gone, proved by the spec's own `## Validation` line: `specs.py plans reindex` -> exit 2, 'invalid choice: plans'. A correct assertion is that exit code, or `grep -cE '^ +plans '`.
- Para o sibling `split-specs-py-backlog-renderer` (colisão nomeada em `## Risks`): a remoção de `cmd_plans` + `render_plans_zone` + `STAGE_ORDER` + `PLANS_EMPTY` tira 83 linhas de specs.py — 3125 -> 3042. Aquele spec queria EXTRAIR a função para baixar o arquivo do limiar de ~1.200 linhas; a extração agora não tem alvo, e 3042 segue muito acima do limiar, então o problema dele continua inteiro e precisa de outro corte. Esta retirada não o resolve, só remove uma das opções.
- Mutation pass sobre a guarda `sp-plans-subcommand-back` de specs.py: 2 mutações (recolocar `plans` no argparse · recolocar `plans` no DISPATCH) — 2/2 pegas, cada uma na sua superfície. As duas são asseridas separadamente de propósito: recolocar só uma é a forma que um revert parcial toma. Com isto, DUAS das três selftests shipped passaram por mutation pass nesta branch (okf-validate.py e specs.py, só as guardas novas); skills.py não.
- Gap que o spec não previu, fechado na task 3.1: `assets/specs/plans/` era mantida no git APENAS por `index.md`. Apagando o arquivo, git deixa de rastrear a pasta, e o `Copy assets/specs/` do step 6 do /specs:align pararia de criar `specs/plans/` num target repo novo — `specs.py doctor` reportaria `sp-missing-phase` em todo repo recém-alinhado. Adicionado `assets/specs/plans/.gitkeep`, espelhando `assets/specs/archive/.gitkeep` que já existia pelo mesmo motivo. Sem isso a retirada quebrava o scaffold.
- Terceiro `verify:` defeituoso (task 3.2): `grep -rn 'plans/index.md' commands/` exigindo zero linhas é incompatível com a própria retirada. As linhas que sobram são as invariantes `Never recreate plans/index.md` que a task escreve — e elas são a ÚNICA guarda contra um command body voltar a semear o artefato, porque os selftests de 1.2 e 2.2 cobrem só os tools. Um verify literal mandaria apagar a proibição junto com a prática. Escopo corrigido para: nenhum `plans reindex`, nenhum `--listing-root`, e nenhuma menção OPERATIVA (excluídas as que dizem 'Never' ou 'retired artifact'). Testado contra um arquivo-sonda com uso operativo: dispara.
- CONTRADIÇÃO com standard, resolvida pelo humano em 2026-07-30: a task 3.3 e o bloco `## Validation` invocam `functional-checks.sh`, e `docs/standards/quality/surface-verification.md` (authority: current) §The harness belongs to the skill front diz literalmente que ele 'is not named in a spec's ## Validation or a task's verify:'. Retirado dos dois lugares — resta corrigir `## Validation`, que ainda o cita. PENDÊNCIA SEPARADA para o /specs:conclude: esta branch editou CINCO command bodies na task 3.2, e o mesmo standard manda rodar o harness onde a superfície é editada, uma vez, sob /skill:new — que este spec não atravessa. `skills.py doctor` (26 comandos, 0 findings) e `lint` (exit 0) passam, mas nenhum dos dois prova que a superfície CARREGA.
