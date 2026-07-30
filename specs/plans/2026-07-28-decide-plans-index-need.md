---
slug: decide-plans-index-need
title: Reassess whether specs/plans/index.md is needed
verification: per-section
priority: {level: 6, criticality: medium, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
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

Todo spec ativo deste repo é um arquivo em `specs/plans/`. Dentro dessa pasta existe um
`index.md` cuja metade de baixo é uma tabela gerada por script, listando cada spec e em que ponto
da vida ele está — e é essa metade gerada que este spec põe em questão.

O `## Problem` mostra por que: a tabela pode estar errada sem que nada acuse, e neste momento ela
está. Como a mesma informação sai pronta de `specs.py list`, a tabela é uma segunda cópia de um
fato que já se lê do disco — e uma cópia que ninguém consegue provar fresca.

O `## Proposal` lista o que fica verdadeiro no fim: a tabela sai, o arquivo fica com o texto que
explica a pasta, e os comandos param de pagar por mantê-la. `## Design` mostra que o arquivo tem
dois papéis distintos e que só um deles apodrece — é aí que o corte passa — e enuncia a regra que
sobra: uma listagem gerada só se paga quando um programa consegue provar que ela está fresca.
`## Alternatives Considered` guarda as três formas recusadas, incluindo a de simplesmente consertar
a tabela em vez de removê-la, com o motivo de cada derrota. `## Out of Scope` separa este arquivo
das listagens do bundle `docs/`, que se parecem com ele e são outra coisa.

Duas seções dizem o que ainda não está resolvido, e vale ler antes de construir. `## Open Decisions`
abre com a única pergunta capaz de inverter tudo — se alguém de fato lê essa tabela no navegador —
e é por isso que perguntar vem antes de mexer em código. `## Risks` reúne o que pode dar errado, com
destaque para dois acoplamentos medidos: se o sweep continuar semeando a tabela ele desfaz a
remoção sozinho, e se o flag `--listing-root` ficar para trás os 32 specs da pasta viram 32 avisos
de arquivo órfão. Também é ali que ficam nomeados os specs vizinhos que tocam os mesmos arquivos,
com a fronteira que este mantém em cada caso.

O resto é execução. `## Impact` declara o único standard que este spec promete escrever e lista
todo arquivo que ele espera tocar; `## Validation` dá os comandos que provam a retirada, incluindo
o que precisa **continuar** funcionando; `## Tasks` põe as decisões na seção 1, antes de qualquer
código, porque a resposta da primeira pergunta pode cancelar as outras seis; e `## Handoff` reúne os
números já medidos para que quem construir não precise redescobri-los.
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

- A GENERATED zone de `specs/plans/index.md` deixa de existir: nenhum comando a reconstrói, nenhum
  tool a renderiza, e nenhuma condição de convergência depende de ela bater com o disco.
- O arquivo `plans/index.md` **continua existindo** com a prosa fixa que já carrega — o que é o
  folder, a tabela de derived stages, para onde o split `backlog/`+`ready/` foi, o que não vai ali
  — mais um ponteiro dizendo que a listagem viva é `specs.py list` e `/specs:status`. As duas
  citações que hoje resolvem nele (`commands/specs/create.md:12` e `commands/specs/triage.md:13`)
  continuam resolvendo.
- `specs.py` perde `cmd_plans`, `render_plans_zone`, `PLANS_EMPTY` e o uso de
  `GEN_BEGIN`/`GEN_END`; o subcomando `plans reindex` sai da superfície do tool, e
  `specs.py --help` não o oferece mais.
- Os quatro command bodies que hoje chamam `plans reindex` — `commands/specs/create.md`,
  `commands/specs/triage.md`, `commands/specs/align.md`, `commands/docs/import-memory.md` — perdem
  esse passo e não ganham nada no lugar dele.
- `/specs:align` continua semeando `plans/index.md` quando ele falta, e o seed passa a ser a
  versão só-prosa: `sp-no-plans-index` **sobrevive**, porque o arquivo continua sendo esperado.
  Saem `sp-no-generated-zone` e `sp-zone-stale`, que só descrevem a zona.
- `okf-validate.py --listing-root` e `_is_spec_file` são retirados **na mesma mudança**, não
  depois: sem zona, `index.md` não linka nada e cada spec em `plans/` passa a emitir
  `index-orphan`. Medido em sandbox em 2026-07-30 — 32 specs, 32 warnings — e a condição de
  convergência do front exige zero `index-orphan`, então deixar o flag no lugar impediria o front
  `specs/` de reportar clean para sempre.
- A condição de convergência do front `specs/` passa a citar só o que um programa consegue decidir:
  `specs.py doctor` e `specs.py validate`, e nada sobre uma zona bater com o disco.
- Um `plans/index.md` que sobreviva num target repo já alinhado continua legível e gravável, e
  nenhum align o apaga.
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
  ninguém mais produz o artefato; nunca que um sweep destrói conteúdo que não é dele.
- **Dar nome ao stage `plans`** que hoje aparece como `### Plans` na zona. Ele é o assunto do spec
  `name-the-scaffolded-stage`, e continua existindo em `next --front` e `status` mesmo sem zona.
- **Reordenar, renomear ou remover qualquer derived stage**, e qualquer edição em
  `assets/specs/schema.json`.
- **Melhorar o formato da tabela** — acrescentar coluna, mudar ordenação, mostrar `## Overview`.
  Se a zona sai, não há tabela para melhorar.
- **Escrever um checker de staleness de zona em `okf-validate.py` ou em `specs.py`.** Foi
  considerado e recusado (`## Alternatives Considered`): um checker novo é o gasto certo para um
  artefato que se paga, e este não se paga.
- **Consertar a ausência de reindex em `/specs:conclude` mantendo a zona.** É a mesma opção
  recusada acima, vista pelo outro lado: se a zona fica, esse conserto é obrigatório; como ela
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

- `docs/standards/quality/selftest-mutation.md` — a guarda desta retirada é exatamente um selftest
  que precisa falhar quando a retirada é desfeita; se ela se provar, é evidência para promover
  aquele standard a `current`

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/specs.py` — `cmd_plans`, `render_plans_zone`, `PLANS_EMPTY`,
  `GEN_BEGIN`/`GEN_END`, o subparser `plans`, e o finding `sp-no-generated-zone`
- `plugins/quenching/assets/hooks/okf-validate.py` — o modo `--listing-root` e `_is_spec_file`
- `plugins/quenching/assets/specs/plans/index.md` — o seed, que perde os markers
- `plugins/quenching/commands/specs/create.md`, `commands/specs/triage.md`,
  `commands/specs/align.md`, `commands/docs/import-memory.md` — os quatro bodies que chamam
  `plans reindex`
- `plugins/quenching/assets/references/specs-create/plans-zone.md` — dono declarado do contrato da
  zona; perde duas seções
- `plugins/quenching/assets/references/specs-align/conformance.md`,
  `assets/references/align/convergence.md`, `assets/references/align/sweep-doctrine.md` — os
  códigos e a condição de convergência
- `plugins/quenching/assets/specs/QUENCHING.md`, `assets/claude/QUENCHING.md`,
  `plugins/quenching/README.md`, `assets/README.md` — 7 linhas que descrevem a zona ou o flag
- `plugins/quenching/VERSION` — o lockstep

## Validation

A política é `verification: per-section`: cada seção de tasks fecha com um comando que roda, e o
acoplamento medido entre a zona e `--listing-root` obriga a verificar as duas remoções juntas —
`end-of-plan` deixaria o front sem poder reportar clean no meio do caminho, e `per-task` rodaria o
mesmo selftest cinco vezes sem informação nova.

Rodado de `plugins/quenching/`, salvo indicação em contrário.

**A superfície do tool perdeu o subcomando:**

```bash
python3 assets/bin/specs.py --help | grep -c plans     # 0
python3 assets/bin/specs.py plans reindex              # exit != 0, erro de argumento inválido
```

**O flag saiu do validador:**

```bash
python3 assets/hooks/okf-validate.py --help | grep -c listing-root   # 0
```

**Nada no plugin ainda chama o que foi retirado** (o único texto que pode sobrar é histórico, em
`specs/archive/**`, que nunca é tocado):

```bash
grep -rn "plans reindex\|--listing-root\|render_plans_zone\|sp-zone-stale\|sp-no-generated-zone" \
  plugins/quenching/   # nenhuma linha
```

**O seed não tem mais zona, e o front continua conformante:**

```bash
grep -c "BEGIN GENERATED" assets/specs/plans/index.md   # 0
python3 assets/bin/specs.py validate --json             # ok: true, 0 findings
python3 assets/bin/specs.py doctor --json               # nenhum código novo; sp-no-plans-index
                                                        # apenas quando o arquivo falta de fato
```

**As três guardas de selftest passam, e a nova falha quando a retirada é desfeita:**

```bash
python3 assets/bin/specs.py selftest
python3 assets/bin/skills.py selftest
python3 assets/hooks/okf-validate.py selftest
```

**O bundle e a superfície de comandos seguem limpos:**

```bash
python3 assets/hooks/okf-validate.py assets/docs        # 0 error(s), 0 warning(s)
python3 assets/bin/skills.py --root . doctor --json     # 26 commands, no findings
```

**O lockstep de versão concorda:**

```bash
cat VERSION
python3 assets/bin/specs.py --version
python3 assets/bin/skills.py --version
python3 assets/hooks/okf-validate.py --version
```

**Invariante que precisa continuar valendo:** `okf-validate.py assets/docs` segue checando
`index-orphan` e `index-broken-link` dentro do bundle. A retirada é do modo `--listing-root`, nunca
dos checks — se um doc do bundle deixar de ser flagrado por órfão, a mudança foi longe demais.

**O que esta validação deliberadamente não cobre:** que um humano prefira a tabela ao
`specs.py list`. Isso não é verificável por comando; é a primeira task do plano e vive em
`## Open Decisions`.

## Design

### A decisão: o artefato se divide na linha onde a staleness mora

`plans/index.md` tem dois papéis que ninguém separou até agora, e só um deles apodrece.

| Papel | De onde a verdade vem | Custo de staleness |
| --- | --- | --- |
| Prosa fixa — o que é o folder, a tabela de derived stages, para onde o split de folders foi, o que não vai ali | escrita à mão; muda quando a doutrina muda | nenhum: descreve o contrato, não o conteúdo do disco |
| GENERATED zone — contagens mais uma tabela por stage | `plans/*.md` no disco | total: reconstruída por 4 comandos, quebrada por um 5º, checável por nenhum |

Daí a decisão ser **retirar a zona e manter o arquivo**, e não "manter" nem "apagar". As três
opções que o `## Problem` ofereceu tratam `plans/index.md` como um átomo, e ele não é. Apagar o
arquivo inteiro custaria duas coisas que a zona não paga: as citações vivas em
`commands/specs/create.md:12` e `commands/specs/triage.md:13`, que usam o arquivo como a explicação
do folder, e a própria prosa, que é a única descrição em prosa de onde o split `backlog/`+`ready/`
foi parar.

### Por que "manter e consertar" perde

Consertar significa duas adições, não uma: um `changed` de verdade em `specs.py plans reindex` (o
campo que três documentos já mandam ler) **mais** um checker que compare a zona com o disco, porque
`changed` só diz se *aquela* chamada escreveu — não se a zona está fresca agora. Depois disso,
`/specs:conclude` precisa passar a reindexar, e cada comando futuro que mexer em `plans/` herda a
mesma obrigação.

O front já tem essa resposta escrita, para outro artefato:
`docs/standards/quality/bundle-verification.md` §Prose does not enforce — "past two skills, the
honest options are a **deterministic check** or an accepted gap recorded as one — never a third
paragraph", com o corolário "when a check lands, the prose it replaces gets *cut*". Aplicado aqui,
o cálculo é o inverso do que parece: pagar um checker novo para manter uma cópia é gastar duas vezes
por um fato que `specs.py list` já entrega de graça, do disco, sem cópia para conferir.

### A regra durável que sai daqui

**Uma listagem gerada só se paga quando um programa consegue provar que ela está fresca.** O
corolário é o critério de decisão, e ele é verificável antes de escrever qualquer código: se existe
um comando que deriva o mesmo fato do disco sob demanda, a listagem gerada é uma segunda fonte da
verdade e a verificação dela é puro custo. Se não existe — o caso dos `index.md` do bundle `docs/`,
que são a própria navegação — a listagem é a fonte, e aí o checker é obrigatório e se paga.

Isso é a doutrina do próprio front aplicada a um artefato que escapou dela.
`assets/references/specs-develop/spec-driven.md` §Frontmatter já diz que "two declared sources of
one fact will diverge", e §Identity que "one truth never gets two declared sources" — foi o
argumento que matou o campo `created`, o campo `phase` e o campo `ready`. A zona é exatamente a
mesma forma: um campo declarado para um fato derivável, só que renderizado em markdown.

### O que a retirada exige, procedimentalmente

`docs/standards/architecture/retiring-a-reserved-artifact.md` é vinculante e governa este caso
(`plans/index.md` casa com `index.md`, que está em `RESERVED`). As três pernas dele, traduzidas
para cá:

1. **Remover o checker** — os quatro códigos `sp-*` da listagem, e o modo `--listing-root` se ele
   ficar sem chamador.
2. **Parar de produzir** — nenhum comando reindexa, nenhum align semeia a zona.
3. **Não mudar mais nada** — `index.md` fica em `RESERVED` (o bundle `docs/` o produz de qualquer
   modo), e um `plans/index.md` sobrevivente num target repo continua legível e gravável.
   `/specs:align` não o cria nem o apaga, e `/specs:status` o reporta como figura sem código de
   finding, no registro que `docs/standards/architecture/read-only-views.md` §What the read command
   therefore owns já autoriza para figuras que não são defeito.

E a perna que o standard chama de guarda: uma regra cujo modo de falha é silencioso precisa de
teste, não de parágrafo. Aqui isso é uma asserção de `specs.py selftest` de que `plans reindex`
não existe mais na superfície do tool, e um fixture em `okf-validate.py selftest` com um
`plans/index.md` sobrevivente validando limpo.

### Contratos que este design não pode contrariar

- `docs/standards/architecture/retiring-a-reserved-artifact.md` — retirar, nunca desreservar.
- `docs/standards/quality/bundle-verification.md` §What is machine-checked — nenhum check novo
  nasce em ERROR, e o que sai daqui é subtração, não escalada.
- `docs/standards/quality/selftest-mutation.md` — a guarda acima tem que falhar quando a
  retirada é desfeita.
- `docs/standards/ci-cd/versioning-release.md` — `specs.py` muda, então o lockstep de versão vale:
  `VERSION` e os três scripts precisam continuar concordando.
- `assets/references/specs-create/plans-zone.md` é hoje o dono declarado do contrato da zona; com a
  zona fora, o arquivo perde duas seções inteiras e não pode ficar descrevendo um artefato que não
  existe.

## Alternatives Considered

As quatro formas inteiras que o spec podia tomar, comparadas antes de escolher. As três primeiras
são as que o `## Problem` nomeou; a quarta é a que ganhou.

| Forma | Custo | O que compra | O que impede depois |
| --- | --- | --- | --- |
| **A. Manter a zona e instrumentá-la** — `changed` de verdade, um checker de staleness, e reindex em `/specs:conclude` | dois acréscimos de código em dois tools, mais um passo novo em `conclude`, mais o passo herdado por todo comando futuro que mexa em `plans/` | uma listagem navegável no GitHub que passa a ser confiável | nada; é a opção conservadora |
| **B. Apagar `plans/index.md` inteiro** | quebra `commands/specs/create.md:12` e `commands/specs/triage.md:13`, que citam o arquivo como a explicação do folder; perde a única prosa que registra para onde o split `backlog/`+`ready/` foi | a subtração máxima | ter um lugar canônico para a doutrina do folder |
| **C. Encolher para um ponteiro estático de poucas linhas** | reescrever a prosa que já está boa | subtração quase máxima | nada relevante |
| **D. Retirar a zona, manter o arquivo e sua prosa** *(escolhida)* | uma retirada em três tools, quatro command bodies e três references | remove a única parte que apodrece, mantém as citações resolvendo e a doutrina onde está | nada que a zona oferecia e `specs.py list` não ofereça |

Por que cada uma perdeu:

- **A perdeu por aritmética, não por gosto.** Ela paga dois checks novos para manter uma cópia de
  um fato que `specs.py list` entrega do disco sob demanda. O argumento de
  `docs/standards/quality/bundle-verification.md` §Prose does not enforce — check determinístico ou
  lacuna aceita, nunca um terceiro parágrafo — é o que justifica pagar por um check; ele não
  justifica pagar por um check que existe só para vigiar uma duplicata evitável.
- **B perdeu por evidência concreta**, não por prudência: duas citações vivas em command bodies
  apontam para o arquivo, e a prosa dele não tem custo de staleness nenhum. Apagar conteúdo que não
  é o problema para resolver o que é seria destruir a parte sã do artefato.
- **C perdeu por ser B com passos extras.** Se a prosa fica de qualquer jeito, reescrevê-la mais
  curta não compra nada mensurável e joga fora texto revisado.
- **Fazer nada** não está na tabela porque já é o estado atual, e o estado atual é o que o
  `## Problem` mede: uma listagem errada agora, com toda a pilha de verificação verde.

## Open Decisions

- **Alguém realmente lê a zona como view de status?** É a única pergunta que pode inverter o spec:
  se um humano navega `plans/index.md` no GitHub para saber onde o front está, a zona se paga e a
  alternativa A volta a ganhar. Não é decidível a partir do repo — leitura não deixa rastro em
  `git log`. **Como se decide:** o humano responde, e essa resposta é a primeira task do plano,
  antes de qualquer mudança de código. Até lá a recomendação é D, por um motivo verificável: a
  prosa mantida carrega o ponteiro para `specs.py list`, que serve um leitor de navegador também —
  sem tabela, mas sem mentir.
- **`/specs:align` remove uma GENERATED zone sobrevivente de um `plans/index.md` de target repo, ou
  deixa como está?** `docs/standards/architecture/retiring-a-reserved-artifact.md` §The consequence
  for disposition proíbe um sweep apagar um **artefato** retirado, e não resolve o caso de uma
  **zona** dentro de um artefato mantido — que o align semeou e portanto owna. **Como se decide:**
  lendo esse standard junto com o humano na hora de escrever a task do align; se a leitura não for
  conclusiva, o default é deixar como está, porque é o lado que não destrói nada.
- **`sp-index-frontmatter` sobrevive como regra de prosa, ou a lacuna é aceita e registrada?** Hoje
  quem checa que `plans/index.md` não tem frontmatter é `okf-validate.py … --listing-root`, que sai
  na mesma mudança. **Como se decide:** por consumo — nada hoje lê frontmatter desse arquivo, então
  o default é lacuna aceita e escrita como tal (`bundle-verification.md` §Prose does not enforce
  admite "an accepted gap recorded as one"); o humano confirma antes de a task fechar.

## Risks

- **`/specs:align` volta a semear a zona e desfaz a retirada.** É a perna que se esquece: hoje
  `commands/specs/align.md:163-175` semeia `plans/index.md` a partir de
  `assets/specs/plans/index.md` e depois chama `plans reindex`, e `conformance.md:112` descreve o
  seed como não-evidence-gated, isto é, incondicional. Se o asset semeado ainda tiver os markers, o
  próprio sweep que deveria honrar a retirada a reverte em todo target repo.
  *Mitigação:* o asset `assets/specs/plans/index.md` perde os markers na mesma task que muda o
  align, e a guarda de selftest afirma que `plans reindex` não existe mais na superfície do tool.
- **Retirar a zona sem retirar `--listing-root` no mesmo passo.** Medido: 32 specs, 32 warnings
  `index-orphan`, e a condição de convergência exige zero deles — o front `specs/` nunca mais
  reportaria clean. *Mitigação:* as duas mudanças ficam na mesma seção de tasks, verificadas pelo
  mesmo comando; nunca em commits separados por uma fronteira de verificação.
- **Um target repo com zona sobrevivente e ninguém para atualizá-la.** O humano lê uma listagem
  congelada e trabalha no spec errado — exatamente o modo de falha que este spec existe para
  matar, só que sem nem o reindex ocasional que hoje o disfarça.
  *Mitigação:* o ponteiro na prosa mantida diz que a listagem viva é `specs.py list`, e
  `/specs:status` reporta a zona sobrevivente como figura sem código de finding
  (`docs/standards/architecture/read-only-views.md` §What the read command therefore owns). O
  descarte em si é decisão do target repo, per `## Open Decisions`.
- **Colisão com o sibling `split-specs-py-backlog-renderer`.** Aquele spec quer *extrair*
  `render_plans_zone` de `specs.py` para tirar o arquivo de cima do limiar de ~1.200 linhas; este
  quer *deletar* a mesma função. É a mesma função, e os dois não podem ganhar.
  *Fronteira que este spec mantém:* ele remove `cmd_plans` e `render_plans_zone` e não toca em mais
  nenhum renderer nem no limiar de linhas; a decisão de qual dos dois roda primeiro é do humano, e
  este spec não assume o resultado do outro. Se aquele landar primeiro, a task de remoção aqui
  passa a mirar o módulo extraído em vez da função inline.
- **Sobreposição com o sibling `name-the-scaffolded-stage`.** A zona é onde o stage sem nome
  aparece hoje, como `### Plans`, e aquele spec cita exatamente esse sintoma.
  *Fronteira:* este spec remove **um renderizador** do estado sem nome e não decide nada sobre
  nomeá-lo — o estado continua existindo em `derive_stage`, `next --front` e `status`. O risco real
  é aquele spec perder seu sintoma mais visível e a decisão nunca ser tomada; nomeá-lo continua
  valendo por conta própria, e dizer isso aqui é o máximo que este spec pode fazer.
- **Sobreposição com o sibling `wire-the-overview-consumers`.** Os três consumidores dele são
  `/specs:triage`, `/specs:continue` e o approval bank de `/specs:develop` — a listagem não é um
  deles, então não há colisão de design. Há colisão de arquivo: os dois editam
  `commands/specs/triage.md`, um acrescentando uma leitura de `## Overview` e o outro removendo o
  passo de reindex. *Fronteira:* este spec só remove o passo de reindex e a citação de
  `--listing-root` naquele body, e não mexe em como o triage renderiza cada spec.
- **Sobreposição com o sibling `dedupe-specs-py-spec-reader`.** `cmd_plans` faz sua própria cópia
  inline de read-parse-derive em `assets/bin/specs.py:2961-2969` — uma das cópias que aquele spec
  vai dobrar em um helper. *Fronteira:* apagar `cmd_plans` remove um dos call sites dele; este spec
  não escreve o helper nem toca nas outras cópias.
- **Sobreposição com o sibling `revise-standards-subject-folders`.** O standard declarado em
  `## Impact` mora em `docs/standards/architecture/`, e aquele spec revisa justamente as subject
  folders fixas. *Fronteira:* este spec escreve o standard no path que existir quando a task rodar,
  e não propõe nem impede nenhuma mudança de folder.
- **O lockstep de versão passar batido.** `specs.py` muda, então `VERSION` e os três scripts
  precisam continuar concordando (`docs/standards/ci-cd/versioning-release.md`).
  *Mitigação:* uma task explícita de release, verificada pelos comandos de lockstep do
  `CLAUDE.md`.
- **ACCEPTED — a retirada é barata de desfazer, e é isso que autoriza fazê-la.** `cmd_plans` e
  `render_plans_zone` são cerca de 65 linhas recuperáveis do `git log`, a zona é determinística, e
  não há estado nenhum para migrar de volta: um único reindex a reconstruiria do disco sem perda.
  A assimetria é o argumento — a remoção é reversível, e a staleness que ela mata não é
  detectável.
- **ACCEPTED — a lacuna do check de frontmatter em `plans/index.md`.** Nada consome o frontmatter
  desse arquivo hoje, então perder o check custa zero mensurável; fica registrada como lacuna
  aceita em vez de virar um checker novo, pendente da confirmação em `## Open Decisions`.

## Tasks

Cada primeira linha é a task inteira e se lê sozinha — `specs.py next` entrega só ela ao executor.
As tasks 1.1 e 1.2 não têm `verify:` de propósito: são decisões, e `## Validation` já declara que
essa parte não é verificável por comando.

### 1. Decidir antes de mexer

- [ ] 1.1 Perguntar ao humano se ele lê a tabela no navegador e registrar a resposta em `## Open Decisions`
      Se a resposta for "eu leio e quero a tabela", o plano para aqui e reabre pela alternativa A de
      `## Alternatives Considered`. Nenhuma task abaixo roda antes desta.
- [ ] 1.2 Resolver as outras duas entradas de `## Open Decisions` e escrever cada resolução na seção
      São: se `/specs:align` remove uma zona sobrevivente num target repo, e se
      `sp-index-frontmatter` sobrevive como regra de prosa ou vira lacuna aceita registrada.

### 2. Retirar a zona de `specs.py`

- [ ] 2.1 Remover `cmd_plans`, `render_plans_zone`, `PLANS_EMPTY`, o subparser `plans` e o finding `sp-no-generated-zone` de `specs.py`
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py --help | grep -c plans
      Manter `sp-no-plans-index`: o arquivo continua esperado, e o remedy passa a apontar para o
      seed só-prosa. O `verify:` tem que imprimir `0`.
- [ ] 2.2 Acrescentar a `specs.py selftest` a asserção de que `plans reindex` não existe mais na superfície do tool
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py selftest
      Escrita para falhar se alguém reintroduzir o subcomando — é a guarda que
      `docs/standards/architecture/retiring-a-reserved-artifact.md` §The guard exige.

### 3. Retirar `--listing-root` no mesmo movimento

- [ ] 3.1 Remover o modo `--listing-root` e `_is_spec_file` de `okf-validate.py`, preservando `index-orphan` e `index-broken-link` para o bundle
      files: plugins/quenching/assets/hooks/okf-validate.py
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py --help | grep -c listing-root
      Tem que imprimir `0`. Esta task e a 2.1 fecham a mesma seção de verificação porque separá-las
      produz os 32 `index-orphan` medidos em `## Risks`.
- [ ] 3.2 Acrescentar a `okf-validate.py selftest` um fixture com um `plans/index.md` sobrevivente que valida limpo
      files: plugins/quenching/assets/hooks/okf-validate.py
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py selftest && python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/docs
      O fixture também afirma que `index.md` continua em `RESERVED`.

### 4. Parar de produzir a zona

- [ ] 4.1 Tirar os markers GENERATED e a tabela do seed `assets/specs/plans/index.md` e acrescentar o ponteiro para `specs.py list`
      files: plugins/quenching/assets/specs/plans/index.md
      verify: grep -c "BEGIN GENERATED" plugins/quenching/assets/specs/plans/index.md
      Tem que imprimir `0`. A prosa existente fica; só a zona sai.
- [ ] 4.2 Remover o passo de reindex e as menções a `--listing-root` dos quatro command bodies que os têm
      files: plugins/quenching/commands/specs/create.md, plugins/quenching/commands/specs/triage.md, plugins/quenching/commands/specs/align.md, plugins/quenching/commands/docs/import-memory.md
      verify: grep -rn "plans reindex\|--listing-root" plugins/quenching/commands/
      Tem que não imprimir nenhuma linha. As citações do arquivo em `create.md:12` e `triage.md:13`
      continuam como estão — elas apontam para a prosa, não para a zona.

### 5. Atualizar as references que descrevem o artefato retirado

- [ ] 5.1 Cortar de `plans-zone.md` as seções que descrevem a GENERATED zone e o on-write check
      files: plugins/quenching/assets/references/specs-create/plans-zone.md
      Mantém §Resolving the tool e §The `specs/` front records itself, que não falam da zona.
- [ ] 5.2 Remover `sp-no-generated-zone` e `sp-zone-stale` de `conformance.md` e reescrever a condição de convergência do front
      files: plugins/quenching/assets/references/specs-align/conformance.md
      A condição nova cita só o que um programa decide. Aplicar aqui a resolução de 1.2 sobre
      `sp-index-frontmatter`.
- [ ] 5.3 Tirar a cláusula `--listing-root` do contrato de convergência e da tabela de verificadores por front
      files: plugins/quenching/assets/references/align/convergence.md, plugins/quenching/assets/references/align/sweep-doctrine.md
- [ ] 5.4 Corrigir as 7 linhas de manual e README que descrevem a zona ou o flag
      files: plugins/quenching/assets/specs/QUENCHING.md, plugins/quenching/assets/claude/QUENCHING.md, plugins/quenching/README.md, plugins/quenching/assets/README.md
      verify: grep -rn "plans reindex\|--listing-root\|render_plans_zone" plugins/quenching/
      Tem que não imprimir nenhuma linha.

### 6. Escrever a regra durável

- [ ] 6.1 Escrever `docs/standards/architecture/generated-listings.md` via `/docs:add`, em `authority: current`
      files: docs/standards/architecture/generated-listings.md
      pattern: docs/standards/architecture/retiring-a-reserved-artifact.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
      Conteúdo: uma listagem gerada só se paga quando um programa consegue provar que ela está
      fresca; o critério de decisão; e os `index.md` do bundle `docs/` como o contraexemplo que
      delimita a regra. `current` porque esta retirada é a prova.

### 7. Fechar as obrigações de release

- [ ] 7.1 Acertar o lockstep de versão entre `VERSION` e os três scripts
      verify: cat plugins/quenching/VERSION && python3 plugins/quenching/assets/bin/specs.py --version && python3 plugins/quenching/assets/bin/skills.py --version && python3 plugins/quenching/assets/hooks/okf-validate.py --version
      As quatro saídas têm que concordar.
- [ ] 7.2 Rodar a validação inteira de `## Validation` e registrar a saída de cada comando
      verify: python3 plugins/quenching/assets/bin/specs.py validate --json && python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json
