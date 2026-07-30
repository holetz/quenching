---
slug: name-the-scaffolded-stage
title: Decide whether a spec with an unwritten Problem gets a named stage
verification: per-section
priority: {level: 30, criticality: low, complexity: 2, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# Decide whether a spec with an unwritten Problem gets a named stage

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

Um spec nasce com o heading `## Problem` escrito e vazio — só o comentário de orientação que
`specs.py new` copiou. Nesse instante ele não casa com nenhuma regra de estágio derivado, e a
ferramenta responde com o nome da pasta, `plans`, onde deveria responder com o nome de um estado.

`## Problem` mostra os três lugares onde esse vazamento aparece, e `## Proposal` diz o que passa a ser
verdade depois: um nome único para o estado, o conjunto canônico de estágios intacto, e `next`
apontando para o heading que de fato falta. `## Design` explica por que o nome vive na derivação e não
no schema — o DSL de casamento simplesmente não consegue expressar "presente mas vazio" — e
`## Alternatives Considered` mostra as formas que perderam para essa, incluindo a de fazer o estado
deixar de existir.

`## Out of Scope` separa o que fica com os siblings que tocam os mesmos arquivos, e `## Risks` nomeia
cada um deles junto com a falha silenciosa que a asserção nova de `selftest` passa a pegar.
`## Open Decisions` guarda as duas perguntas que este spec deliberadamente não responde. `## Impact`
declara os dois documentos de `docs/standards/` que o trabalho escreve, e `## Validation` mostra como
observar o estado, que só existe em um workspace descartável.

Quem for executar começa por `## Tasks` com `## Handoff` ao lado: o grupo 1 é uma linha e já entrega o
valor principal, o grupo 2 dá o nome, o grupo 3 paga o vocabulário e o grupo 4 fecha o release que
qualquer edição em `specs.py` obriga.

## Problem

`specs.py new` grava a frontmatter e o heading `## Problem` com seu comentário de orientação, e mais
nada — um spec recém-capturado tem, deliberadamente, quatro linhas de corpo. Mas conteúdo de scaffold
é invisível para `has_real_content()` por construção, então um spec cujo `## Problem` ainda é o
comentário de orientação **não tem nenhuma seção preenchida** e portanto não casa com nenhum estágio
derivado: nem com `captured`, cuja regra é `filled: [Problem]`.

`derive_stage` (`specs.py:1090`) então cai no nome da fase, e o listing renderiza um grupo
`### Plans` dentro de `plans/index.md` — um heading que nomeia uma pasta onde todos os outros nomeiam
um estágio. Lê-se como bug do renderer, e é na verdade um estado sem nome no modelo.

Ler o código mostra que o heading do listing é o menor dos três sintomas do mesmo buraco:

- `next --spec` responde `write ## Proposal (then 9 more)` para um spec cujo `## Problem` está vazio,
  porque `specs.py:2040` concatena `missing + malformed` e pega o primeiro elemento — o heading
  malformado espera no fim da fila. A única "próxima ação" da ferramenta aponta para o heading errado
  exatamente no momento em que ela seria mais útil.
- `cmd_new` (`specs.py:1404`) anuncia `"stage": "captured"` literal para o spec que acabou de criar,
  enquanto `status` sobre o mesmo arquivo deriva `plans`. Duas respostas para um fato.
- `list` imprime `[plans]` e `next --front` explica a posição como `plans, 0d old`
  (`specs.py:1945`), levando o nome da pasta a dois consumidores além do listing.

O estado em si é legítimo e vale distinguir: *um spec existe e ninguém escreveu o problema ainda* é um
fato diferente de *o problema está escrito*. O empurrão, porém, já existe: `validate` emite
`sp-empty-section` com severidade **error** (`specs.py:2516`) desde o instante em que o arquivo
existe, e `conformance.md:186` atribui o conserto ao humano, não ao sweep. O que falta é o **nome**,
não o aviso.

Nomeá-lo não é mudança local: a lista de estágios vive em `assets/specs/schema.json`, é duplicada em
`specs.py` como `DEFAULT_SCHEMA` para cópias instaladas sem assets ao lado, e é ordenada por
`STAGE_ORDER` — e `plans reindex`, `next --front` e `status` leem o resultado.

Registrado durante `specs-flow-consolidation`, que documentou o estado no comentário da zona do seed
de `plans/` em vez de modelá-lo, porque a mudança de schema estava fora do escopo daquele spec. A
decisão que este spec deve é se o estado merece um nome ou se o fallback deve apenas renderizar algo
melhor que um nome de pasta.

## Proposal

- O fallback de `derive_stage` tem nome próprio, `scaffolded`, e nenhum consumidor volta a exibir o
  nome da fase como se fosse um estágio: `### Scaffolded` no listing, `[scaffolded]` em `list`,
  `scaffolded, 0d old` na justificativa de `next --front`.
- O conjunto canônico de estágios em `schema.json` **continua com sete membros**. `scaffolded` é a
  ausência de casamento nomeada no ponto onde ela é produzida, não um oitavo membro declarado.
- `next --spec` de um spec cujo `## Problem` está presente e vazio responde `write ## Problem`, não
  `write ## Proposal`.
- `specs.py new` relata o estágio derivado do arquivo que acabou de escrever, em vez do literal
  `captured` que hoje contradiz `status` sobre o mesmo arquivo.
- `selftest` falha quando um id de estágio declarado, ou o fallback, está fora de `STAGE_ORDER` —
  hoje essa divergência faz linhas desaparecerem do listing sem erro nenhum.
- As cinco superfícies que descrevem os estágios derivados citam o fallback pelo nome: o seed
  `assets/specs/plans/index.md`, `spec-driven.md`, `questions.md`, `plan-lifecycle.md` e a entrada
  **Derived stage** do glossário.

## Out of Scope

- **Estender o DSL de casamento de estágio** (`_stage_match`, `specs.py:1099`) com um predicado para
  "presente mas vazio". É o que a opção A exigiria, e é exatamente o custo que a recomendação evita.
- **Mudar a severidade ou o dono de `sp-empty-section`.** O aviso já existe e já pertence ao humano
  (`conformance.md:186`); reclassificá-lo é outra decisão, com outras evidências.
- **O fallback da fase `archive`.** Nenhuma regra de `stages.derived` tem `phase: archive`, então todo
  spec arquivado deriva o estágio `archive`. Ali o nome da pasta **é** o estado honesto da fase
  inteira, não um estado sem nome — nada a renomear.
- **Um bank de `/specs:develop` que escreva o `## Problem` pelo humano.** Autoria é reportada, nunca
  suprida (`commands/specs/align.md:65`), e um `## Problem` inventado é pior que um vazio.
- **A existência de `plans/index.md`.** Se o listing deve continuar existindo é do sibling
  `decide-plans-index-need`; este spec não depende da resposta, porque nomeia o estado na derivação e
  não no renderer.
- **Qualquer reorganização do quarteto read-parse-derive de `specs.py`** — é do sibling
  `dedupe-specs-py-spec-reader`.
- **Mudar a ordenação de `next --front`.** Um spec `scaffolded` continua ranqueado por idade como
  qualquer outro; a pergunta está registrada em `## Open Decisions`.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/code/canonical-set-parsing.md` — a regra durável: um estado que o DSL de um conjunto
  canônico não consegue expressar não é membro dele, e se nomeia no ponto de derivação; mais o episódio
  do `STAGE_ORDER` que apaga linhas do listing sem erro
- `docs/standards/workflows/plan-lifecycle.md` — a cadeia dos sete estágios ganha o fallback nomeado ao
  lado dela, explicitamente como "nenhuma regra casou" e não como oitavo elo

### Código e assets que este spec espera tocar

- `plugins/quenching/assets/bin/specs.py` — o fallback de `derive_stage`, o sentinela de `STAGE_ORDER`,
  a ordenação de `cmd_next`, o estágio que `cmd_new` relata, e a asserção nova de `selftest`
- `plugins/quenching/assets/specs/plans/index.md` — a tabela "Derived stages" e o comentário da zona
  gerada, que hoje é o único lugar do repo que descreve o estado
- `plugins/quenching/assets/references/specs-develop/spec-driven.md` — §Derived stages
- `plugins/quenching/assets/references/specs-develop/questions.md` — §Choosing the bank, que hoje não
  tem linha para um spec sem `## Problem`
- `docs/knowledge/glossary.md` — a entrada **Derived stage**, via `/docs:define`
- `plugins/quenching/VERSION`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`,
  `assets/bin/skills.py`, `assets/hooks/okf-validate.py` — o lockstep de release

## Validation

Um workspace descartável é o único jeito de observar o estado: o repo não tem fixture de scaffold e
`specs.py new` grava no workspace em que roda. `TMP` abaixo é qualquer diretório fora do repo, e
`SPECS` é o script em `plugins/quenching/assets/bin/specs.py`.

### 1. O estado passa a ter um nome, e um só

```bash
mkdir -p "$TMP/specs/plans"
cp plugins/quenching/assets/specs/plans/index.md "$TMP/specs/plans/"
python3 "$SPECS" --root "$TMP/specs" new probe --title Probe
python3 "$SPECS" --root "$TMP/specs" status --spec probe --json
```

`new` deve imprimir `"stage": "scaffolded"` (hoje imprime `"captured"`) e `status` deve imprimir
`"stage": "scaffolded"` (hoje imprime `"plans"`). **Os dois valores têm de ser iguais** — a
discordância é o defeito da tarefa 1.2.

### 2. `next` aponta para o heading que realmente falta

```bash
python3 "$SPECS" --root "$TMP/specs" next --spec probe --json
```

Deve trazer `"heading": "Problem"` e a mensagem `write ## Problem (then 9 more) to reach the ready
gate`. Hoje traz `"heading": "Proposal"` com `"malformed": ["Problem"]` no mesmo payload.

### 3. O listing deixa de nomear uma pasta

```bash
python3 "$SPECS" --root "$TMP/specs" plans reindex
grep -n 'Scaffolded\|scaffolded\|### Plans' "$TMP/specs/plans/index.md"
```

A zona gerada deve conter `### Scaffolded` e a contagem `1 scaffolded` no cabeçalho, e **nenhuma**
ocorrência de `### Plans` como heading de grupo.

### 4. A asserção nova pega a divergência que hoje é silenciosa

`python3 "$SPECS" selftest` deve sair 0 no repo. E, uma vez, à mão: remover o fallback de
`STAGE_ORDER`, confirmar que `selftest` sai 1 com o código novo, e reverter. Sem essa passagem
vermelha a asserção não está provada — foi exatamente assim que o episódio de
`canonical-set-parsing.md` passou verde.

### 5. O esqueleto shipado continua conformante

O bloco de verificação do repo, sem finding novo:

```bash
cd plugins/quenching
cat VERSION
python3 assets/bin/specs.py --version
python3 assets/bin/skills.py --version
python3 assets/hooks/okf-validate.py --version
python3 assets/hooks/okf-validate.py assets/docs
python3 assets/hooks/okf-validate.py assets/specs/plans --listing-root
python3 assets/bin/skills.py --root . doctor --json
python3 assets/bin/skills.py --root . lint --json
python3 assets/bin/skills.py selftest
python3 assets/bin/specs.py selftest
python3 assets/hooks/okf-validate.py selftest
```

As quatro versões em um único valor; os dois `okf-validate` em `0 error(s), 0 warning(s)`; `doctor` com
26 comandos e nenhum finding; `lint` em exit 0; os três `selftest` limpos.

`functional-checks.sh` **não** entra aqui: nenhum arquivo sob `commands/**` muda, e o harness pertence
à frente skill (`surface-verification.md`).

## Design

### A decisão: nomear onde o fallback é produzido, não onde o conjunto é declarado

`derive_stage` (`specs.py:1083-1096`) começa com `stage = spec["phase"]` e sobrescreve a cada regra
que casa, resolvendo por *last match wins*. Um spec de scaffold não casa com regra nenhuma, então o
valor devolvido é literalmente `"plans"` — o nome da fase vazando como se fosse um estágio.

A correção é substituir esse literal por uma constante nomeada e trocar o sentinela `"plans"` no fim
de `STAGE_ORDER` (`specs.py:2923-2924`) pela mesma constante. `status`, `list`, `next --front` e o
listing passam a concordar em um único valor, **sem mapa de exibição**: dois nomes para um estado é
exatamente o segundo nome que o guard-rail de `/specs:develop` proíbe
(`commands/specs/develop.md:62`).

**Regra durável:** um estado que o DSL de um conjunto canônico não consegue expressar não é membro
daquele conjunto — nomeie-o no ponto de derivação. Crescer o conjunto declarado para acomodar um
estado que nenhum predicado alcança troca uma linha de renderização por um item permanente de
vocabulário em toda superfície que restata o conjunto.

### Por que o conjunto declarado NÃO cresce

`_stage_match` (`specs.py:1099-1109`) entende quatro predicados: `anyOf`, `filled`, `frontmatter` e
`taskState`. Nenhum expressa "heading presente com corpo vazio": `filled` exige
`section_state(...) == "filled"` e não existe negação. Declarar uma regra `scaffolded` em
`schema.json` é, portanto, impossível sem **estender o DSL nas duas cópias** — `schema.json` e
`DEFAULT_SCHEMA` — sob o lockstep de três arquivos de `plan-artifacts.md:189`. Esse é o fato que
elimina a opção A, e ele não aparece na leitura do `## Problem`: aparece na leitura do matcher.

### Por que a correção de `next` vem primeiro

`specs.py:2040` escolhe `(ready["missing"] + ready["malformed"])[0]`. Para um spec de scaffold,
`missing` tem nove headings e `malformed` tem apenas `Problem`, então a resposta é `## Proposal`.
Inverter para `malformed + missing` custa uma linha e entrega o empurrão que o `## Problem` deste spec
diz ser útil — sem tocar em vocabulário nenhum. É a fatia de 80% do valor, e por isso é o grupo 1 da
lista de tarefas: um spec abandonado depois do grupo 1 já se pagou.

A inversão é segura para todo spec que não é scaffold, porque `malformed` só é não-vazio quando algum
heading canônico existe com corpo vazio — e um heading vazio é sempre a próxima ação mais urgente que
um heading ausente: ele já foi criado, então alguém já decidiu que ele pertence ao spec.

### A asserção que faltava

Medido em cópia descartável: com um id de estágio fora de `STAGE_ORDER`, `render_plans_zone`
(`specs.py:2938`) itera apenas `STAGE_ORDER` e **silenciosamente não renderiza** aquelas linhas — o
cabeçalho continua contando `**2 specs**` enquanto a tabela mostra uma, e nada erra. É a mesma forma
de falha que `canonical-set-parsing.md` §A lockstep check does not cover the code over it descreve: a
checagem byte-a-byte das cópias passa enquanto o código sobre elas passou a significar outra coisa.
Daí a asserção nova de `selftest` — todo id declarado, mais o fallback, precisa estar em
`STAGE_ORDER`, afirmada contra a declaração em vez de fixar a resposta atual.

### Contratos que o design não pode contradizer

- `docs/standards/code/canonical-set-parsing.md` — fatiar por pertencimento declarado, nunca por
  posição; e afirmar o **comportamento derivado** contra a declaração, não a declaração contra sua
  cópia.
- `plan-artifacts.md:189` — mudar o vocabulário do schema é edição em lockstep de três arquivos.
  A recomendação evita esse lockstep justamente por não mexer no schema.
- `docs/standards/ci-cd/versioning-release.md` — qualquer edição em `specs.py` obriga o lockstep de
  seis artefatos, com `VERSION` e as três ferramentas em um único valor.
- `docs/standards/workflows/plan-lifecycle.md:97` — a cadeia dos sete estágios é declarada ali uma
  vez; o fallback entra como nota ao lado dela, não como oitavo elo.

## Alternatives Considered

Quatro formas inteiras foram comparadas. A escolhida é a B.

| # | Forma | Custo | O que compra | O que impede |
| --- | --- | --- | --- | --- |
| A | Declarar `scaffolded` em `schema.json` + `DEFAULT_SCHEMA` + `STAGE_ORDER` | novo predicado no DSL de casamento nas duas cópias, lockstep de três arquivos, +1 membro permanente em ~10 superfícies que restatam o conjunto | um estágio autodescritivo em `status --json`, com regra legível na declaração | nada; mas paga vocabulário e DSL por um estado transitório |
| **B** | **Nomear o fallback na derivação (`derive_stage` + `STAGE_ORDER`), schema intacto** | duas linhas de código, quatro notas de documentação, uma asserção de `selftest` | um único valor coerente em `status`, `list`, `next --front` e no listing | nada que A permita e B não: se algum dia o DSL ganhar negação, a regra pode ser declarada sem renomear nada |
| C | Só corrigir `next` e aceitar `### Plans` | uma linha | o empurrão, que é o valor real | deixa um heading que nomeia pasta em um listing gerado para humanos — a pergunta que este spec existe para responder ficaria sem resposta |
| D | Tornar o estado inalcançável: `new` recusa sem prosa de problema | quebra o contrato da CLI de `new`, e `/specs:align`/`migrate` passam a lidar com specs legados que o novo `new` não criaria | o estado deixa de existir | recria uma recusa que a frente removeu de propósito ("um spec entra em segundos como problema cru"), e `/specs:create` já escreve o `## Problem` segundos depois — paga quebra de contrato por um estado que dura segundos |
| E | Não fazer nada | zero | zero | o listing continua mentindo, `next` continua apontando para `## Proposal`, e `new` continua discordando de `status` |

**Por que A perdeu.** Não é uma adição de schema: `_stage_match` não tem predicado para "presente mas
vazio", então A é primeiro uma extensão de DSL e só depois um membro novo. E o membro novo é
permanente — cada superfície que hoje lista sete estágios listaria oito, para um estado que o fluxo
suportado atravessa em segundos.

**Por que D perdeu.** É a única opção que resolve o problema por eliminação, e é sedutora por isso.
Perde porque troca um defeito de renderização por uma recusa em um ponto de entrada, e porque
`specs.py new` também é chamado por `/specs:create` e por probes — exigir prosa muda todos eles.

**Por que E perdeu.** O `## Problem` foi registrado por um spec anterior que deliberadamente adiou a
decisão; não decidir de novo apenas move o mesmo parágrafo para o próximo ciclo.

**Uma alternativa de nome, não de forma:** chamar o estado `unwritten` em vez de `scaffolded`.
Rejeitada por uma razão fraca mas real — `unwritten` descreve uma propriedade de *uma seção*, e o
estágio é uma propriedade *do spec*; `scaffolded` nomeia o que a ferramenta fez e é verificável
(`capture_form()` o produziu), além de ser a palavra que o comentário da zona do seed já usa.

## Open Decisions

- **`sp-empty-section` deve continuar com severidade `error` em um spec recém-criado?** Medido: todo
  spec que `specs.py new` cria falha `validate` com um erro desde o instante em que existe — o
  `## Problem` está presente e vazio. Isso é coerente com a regra explicit-none, e ao mesmo tempo
  significa que o estado que este spec chama de legítimo é reportado como erro. *Como se decide:*
  depois que a tarefa 1.1 entrar, rodar `validate` sobre uma captura nova e julgar se o erro ainda
  carrega informação que a resposta de `next` já não dá. Se não carregar, é um spec de follow-up sobre
  severidade — não uma mudança deste.
- **`next --front` deve rebaixar um spec `scaffolded` para baixo dos specs que já têm forma?** Hoje
  `_candidate` (`specs.py:1922`) não considera o estágio na chave de ordenação, então um spec de
  scaffold pode encabeçar a lista com a justificativa `scaffolded, 40d old`. Escrever o `## Problem`
  é uma ação real e barata, o que defende manter como está. *Como se decide:* deixar intocado neste
  spec e revisitar quando a frente tiver mais de um spec `scaffolded` ao mesmo tempo — evidência que
  ninguém tem ainda.

## Risks

**Três siblings tocam os mesmos arquivos e estão sendo desenvolvidos em paralelo.** Nenhum resultado é
assumido aqui; o que está registrado é a fronteira que este spec mantém.

- **`split-specs-py-backlog-renderer` tira o renderer da zona de `plans/` de dentro de `specs.py`** —
  ou seja, exatamente `render_plans_zone` e o `STAGE_ORDER` que mora ao lado dele
  (`specs.py:2923-2947`). *Fronteira:* este spec edita o fallback de `derive_stage`, o sentinela de
  `STAGE_ORDER`, a ordenação de `cmd_next` e o estágio que `cmd_new` relata; não move código entre
  arquivos. *Mitigação:* quem entrar por último reaplica sobre o outro e roda `selftest` mais
  `plans reindex`; se o renderer já mudou de casa, a edição de `STAGE_ORDER` acompanha a casa nova.
- **`dedupe-specs-py-spec-reader` dobra as quatro cópias de read-parse-derive em um helper** — todo
  chamador de `derive_stage`. *Fronteira:* este spec não toca no quarteto; muda uma linha *dentro* de
  `derive_stage` e nada em quem o chama. *Mitigação:* a mesma reaplicação, e `selftest` cobre as duas.
- **`decide-plans-index-need` pode concluir que `plans/index.md` não é necessário.** *Fronteira:* o
  nome vive na derivação, então `status`, `list` e `next --front` continuam corretos mesmo sem listing;
  só a tarefa 3.1 (o comentário da zona do seed) perde objeto. *Mitigação:* nenhuma tarefa deste spec
  depende do listing existir.
- **`add-specs-py-record-writer` também edita `specs.py`**, na escrita de records de frontmatter.
  Sem sobreposição de comportamento com estágios derivados; nomeado por estar no mesmo arquivo.

**Uma linha que desaparece sem erro nenhum.** Medido: um id de estágio presente na derivação e ausente
de `STAGE_ORDER` faz `render_plans_zone` deixar de renderizar aquelas linhas, enquanto o cabeçalho
continua contando o total — `**2 specs**` com uma linha na tabela. *Mitigação:* as duas edições do
grupo 2 entram no mesmo commit, e a tarefa 2.3 adiciona a asserção de `selftest` que transforma essa
divergência em erro.

**O valor de `stage` em `status --json` muda para consumidores.** *Mitigação medida por grep:* nenhum
corpo de comando e nenhum trecho de `specs.py` compara `stage` com `"plans"`; as únicas comparações
são com `"executing"` (`specs.py:1905` e `specs.py:1984`). O risco residual é uma cópia instalada
antiga em repo adotante continuar relatando `plans` — coberto pela comparação de `--version` que os
aligns já fazem (`versioning-release.md`).

**ACCEPTED — o pedágio de release.** Qualquer edição em `specs.py` obriga o lockstep de seis artefatos,
então uma correção de uma linha custa um release. Aceito porque é o custo padrão do repo e porque é
justamente o argumento para entregar os quatro grupos em um spec, em vez de fatiá-los.

**ACCEPTED — `scaffolded` pode ser lido no futuro como um oitavo estágio declarado**, reintroduzindo a
opção A por engano. Aceito com mitigação de redação: as quatro notas de documentação do grupo 3 dizem
"nenhuma regra de estágio casou" e não "um estágio", e a asserção de `selftest` trata o fallback
explicitamente como fallback, separado da lista declarada.

## Tasks

### 1. Os dois defeitos que não custam vocabulário

- [ ] 1.1 Inverter a próxima ação de `cmd_next` para `malformed + missing`, e não `missing + malformed`
      assim um `## Problem` presente e vazio passa a ser a resposta, em vez de `## Proposal`
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py next --spec name-the-scaffolded-stage --json
- [ ] 1.2 Fazer `cmd_new` relatar o estágio derivado, não o literal `"stage": "captured"`
      `new` e `status` param de discordar sobre o mesmo arquivo recém-escrito
      files: plugins/quenching/assets/bin/specs.py

### 2. Nomear o fallback onde ele é produzido

- [ ] 2.1 Nomear o fallback de `derive_stage` em uma constante, mantendo `stages.derived` com sete membros
      substitui o `stage = spec["phase"]` inicial, sem tocar em `schema.json` nem em `DEFAULT_SCHEMA`
      files: plugins/quenching/assets/bin/specs.py
- [ ] 2.2 Trocar o sentinela `"plans"` no fim de `STAGE_ORDER` pela mesma constante, no commit de 2.1
      as duas edições juntas, porque separadas fazem linhas desaparecerem do listing sem erro
      files: plugins/quenching/assets/bin/specs.py
- [ ] 2.3 Adicionar a asserção de `selftest` que exige o fallback e todo id declarado em `STAGE_ORDER`
      afirmada contra a declaração, e provada com uma passagem vermelha à mão antes de reverter
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py selftest

### 3. Pagar o vocabulário nas superfícies que descrevem os estágios

- [ ] 3.1 Atualizar a tabela "Derived stages" e o comentário da zona gerada no seed de `plans/index.md`
      troca "aparece em **Plans**" pelo nome do fallback, mantendo a redação "nenhuma regra casou"
      files: plugins/quenching/assets/specs/plans/index.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/specs/plans --listing-root
- [ ] 3.2 Citar o fallback em `spec-driven.md` §Derived stages, dizendo que não é membro declarado
      files: plugins/quenching/assets/references/specs-develop/spec-driven.md
- [ ] 3.3 Dar a `questions.md` §Choosing the bank uma linha para o estado: nenhum bank, escreva o `## Problem`
      autoria não é suprida, então a linha aponta o humano e não um bank novo
      files: plugins/quenching/assets/references/specs-develop/questions.md
- [ ] 3.4 Nomear o estado na entrada **Derived stage** do glossário via `/docs:define`
      sem criar uma segunda entrada para o que já tem nome
      files: docs/knowledge/glossary.md
- [ ] 3.5 Escrever a regra durável em `docs/standards/code/canonical-set-parsing.md` (authority: current)
      um estado que o DSL do conjunto não expressa não é membro dele; mais o episódio do `STAGE_ORDER`
      files: docs/standards/code/canonical-set-parsing.md
- [ ] 3.6 Registrar o fallback nomeado em `docs/standards/workflows/plan-lifecycle.md`, ao lado da cadeia
      explicitamente como "nenhuma regra de estágio casou", nunca como oitavo elo
      files: docs/standards/workflows/plan-lifecycle.md

### 4. Fechar o release e provar o conjunto

- [ ] 4.1 Cumprir o lockstep de seis artefatos de `versioning-release.md` em um único valor
      files: plugins/quenching/VERSION, plugins/quenching/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/bin/skills.py, plugins/quenching/assets/hooks/okf-validate.py
- [ ] 4.2 Rodar `## Validation` inteiro e registrar a saída de cada comando
      inclui a passagem vermelha de 2.3 e o bloco do esqueleto shipado
      verify: python3 plugins/quenching/assets/bin/specs.py validate --json
