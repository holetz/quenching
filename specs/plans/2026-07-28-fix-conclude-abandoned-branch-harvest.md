---
slug: fix-conclude-abandoned-branch-harvest
title: conclude --outcome abandoned can harvest a note and delete it in the same run
verification: per-section
priority: {level: 9, criticality: high, complexity: 2, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# conclude --outcome abandoned can harvest a note and delete it in the same run

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

Quando alguém desiste de uma spec, `/specs:conclude --outcome abandoned` escreve
o fechamento dela — a seção `## Outcome`, a mudança do arquivo para `archive/`, e
no máximo uma nota curta sobre o que se aprendeu por não ter construído. Hoje
tudo isso é gravado numa branch de trabalho que esse mesmo comando, algumas
linhas depois, oferece apagar. E como um abandono nunca é mergeado, nada tira
esses commits da branch antes da oferta.

`## Problem` mostra a ordem exata, com as linhas do comando, e separa as duas
perdas que ela produz: a nota, que só morre se o humano aceitar apagar a branch,
e o arquivamento, que se perde **sempre** — a base nunca aprende que a spec
fechou, mesmo que ninguém apague nada.

`## Proposal` lista o que passa a ser verdade; `## Design` explica por que a
causa é a premissa perdida (o merge era o carregador) e por que escrever no
checkout da base **não** contraria a regra "o merge é a última ação", já que num
abandono não existe merge. `## Alternatives Considered` compara seis formas,
incluindo a mais barata — só recusar a deleção — e diz o que ela deixa em pé.

`## Risks` guarda o resultado de um premortem, e o risco que mais importa ali é
um que a correção **cria**: escrever no checkout da base significa escrever num
lugar que o humano pode estar usando, e o preço disso é uma recusa quando a
árvore está suja. `## Open Decisions` guarda as duas perguntas que esta spec
deliberadamente não responde — se um abandono deveria colher docs emergentes, e
o que acontece se uma spec irmã fundir os dois momentos de escrita do comando.

Quem for construir isto lê `## Validation` primeiro: a afirmação central é sobre
**ordem**, e ordem não se lê num arquivo. Ela é medida rodando um ciclo de
verdade num repositório descartável e perguntando ao git onde o fechamento
ficou — a mesma forma que a checagem de ordem existente já usa para o caminho
`done`, e que nunca percorreu o caminho abandonado. A asserção que resume a spec
inteira é a quinta: apagar a branch depois do fechamento não pode perder nada.

`## Impact` declara um único doc a escrever, e `## Tasks` vai em seis seções na
ordem em que uma depende da anterior — o corpo do comando, as duas referências, a
checagem, o standard que a checagem prova, o manual embarcado que hoje afirma o
contrário, e a suíte. O bump de versão não está entre elas de propósito: neste
repo isso é obrigação de merge, resolvida pelo próprio `/specs:conclude`.
## Problem

`/specs:conclude --outcome abandoned` destila na branch de trabalho e **depois**
oferece apagar essa mesma branch. Uma nota `authority: background` — a única
colheita que o caminho abandonado permite — pode ser escrita e jogada fora na
mesma execução, sem que nada avise.

A ordem herdada do caminho `done` é a causa: lá a destilação precede o merge, e
o merge é o que leva os commits da branch para a base. No caminho abandonado
não há merge, então nada carrega a nota para fora da branch antes da oferta de
deleção.

Descoberto ao fechar `move-conclude-merge-last`, cujo `## Out of Scope`
congelou deliberadamente o caminho abandonado — então o defeito atravessou a
spec intocado e existe hoje apenas como uma linha em `## Discoveries`.

**A nota é o sintoma, não a causa — e não é a única perda.** Lido inteiro,
`plugins/quenching/commands/specs/conclude.md` põe *tudo* o que escreve num
fechamento abandonado na branch de trabalho:

- passo 3, docs emergentes — "These land **on the branch**, in their own commit,
  so the rule ships with the code that proved it." (linha 155). O passo 3 não
  tem nenhum ramo por `outcome`: vale igual para `done` e para `abandoned`.
- passo 4, `## Outcome` + `git mv` para `archive/` + carimbo
  `outcome: abandoned` — "Commit the move on the branch." (linha 182).
- passo 5, a nota `authority: background` — "Commit what it writes **on the work
  branch**." (linha 204), reafirmado em "For `abandoned` nothing is merged, so
  nothing is stamped ... The distillation above still runs." (linhas 235-236).
- passo 6 — "For `abandoned`, do not merge and do not remove the worktree. Offer
  to keep the branch (default) or delete it" (linhas 336-337).

Disso saem **duas** perdas, de naturezas diferentes:

1. **A nota e os docs emergentes.** Só se perdem se o humano aceitar apagar a
   branch. É a perda que a linha de `## Discoveries` original descreve.
2. **O arquivamento.** Essa se perde **sempre**, sem apagar nada: a base nunca
   recebe o `git mv`, então `specs.py list`, `/specs:status` e `/specs:continue`
   rodados na base continuam vendo a spec em `plans/`, sem `outcome:`, para
   sempre — enquanto o passo 7 relata "The archived path, the outcome" (linha
   343) como se tivesse acontecido. Estado errado silencioso que não depende de
   escolha nenhuma.

**Por que agora.** A perda 2 é garantida em todo fechamento abandonado de spec
isolada desde a 4.2.0, e o custo de esperar não é uma nota: é o front divergindo
da base sem ninguém ver. E o defeito já sobreviveu a uma passada —
`specs/archive/2026-07-28-move-conclude-merge-last.md` linha 511 o registrou
como descoberta, e o `## Out of Scope` daquela spec o congelou com o argumento
"Não há merge, então a reordenação não muda nada ali; o comportamento fica
idêntico." (linhas 123-125). O argumento estava invertido: *não haver merge* é
exatamente o que mudou tudo, porque o merge era o único carregador dos commits
da branch para a base.

## Proposal

O que passa a ser verdade num fechamento com `--outcome abandoned` e hoje não é:

- **Nada que o `/specs:conclude` escreve fica preso na branch.** O `## Outcome`,
  o `git mv` para `archive/`, o carimbo `outcome: abandoned`, os docs emergentes
  do passo 3 e a nota `authority: background` do passo 5 são commitados **no
  checkout que já tem a base**, localizado do mesmo jeito que o passo 6 já
  localiza para mergear (`git worktree list --porcelain`, depois `git -C`).
- **A base sabe que a spec fechou.** `specs.py list`, `/specs:status` e
  `/specs:continue` rodados na base param de oferecer uma spec já concluída.
- **A oferta de apagar a branch não pode mais destruir o fechamento**, porque
  não há fechamento nenhum na branch: ela carrega só o trabalho parcial que
  ninguém adotou — que é o que o próprio `## Doctrine` do comando chama de
  "history, not a change" (linhas 68-69).
- **A oferta diz o que custa.** Ela enumera o que morre com a branch (os commits
  do trabalho parcial) e o que sobrevive (o fechamento, já na base), em vez de
  perguntar sem contexto. E o comando **nunca** passa `-D`: a recusa do git sobre
  branch não mergeada é a mesma segurança que o comando já respeita em
  `git worktree remove`.
- **Um invariante escrito cobre a branch, não só a worktree.** Hoje
  `## Invariants` proíbe `--force` em `git worktree remove` "at all" (linhas
  363-365) e não diz nada sobre apagar branch.
- **Uma execução real observa a ordem.**
  `plugins/quenching/assets/checks/conclude-order-check.sh` ganha um braço
  `abandoned` que percorre create → isolate → execute → conclude(abandoned) num
  repo descartável e pergunta ao **git** — não ao relatório do run — se o
  fechamento está na base e se sobrevive a apagar a branch.
- **O caminho `done` continua idêntico.** Merge-last segue sendo a ordem, e as
  oito asserções atuais do `conclude-order-check.sh` continuam passando.

## Out of Scope

- **A ordem do caminho `done`.** Merge-last fica exatamente como está: review →
  docs emergentes → arquivamento → destilação + carimbo `merge:`, tudo na
  branch, e o merge por último. Esta spec só acrescenta um ramo por `outcome`;
  não reabre a decisão que `move-conclude-merge-last` tomou.
- **Mergear a branch de uma spec abandonada.** Proibido por `## Invariants`
  ("Never merge an abandoned spec's branch", linha 366) e a proibição continua.
  Escrever no checkout da base **não é** um merge: são commits novos, feitos ali,
  sem trazer nenhum commit da branch.
- **Remover a worktree num fechamento abandonado.** As linhas 336-337 e os "three
  bounds" de `specs-isolate/git.md` (linhas 301-302) dizem que não se remove, e
  isso permanece: uma worktree é disco do humano, e a spec não está resolvendo
  limpeza de isolamento.
- **O menu de estratégias de merge e a ressalva do squash.** Nenhuma delas roda
  no caminho abandonado; nada a mudar.
- **Consertar retroativamente fechamentos abandonados já feitos.** Nenhum
  backfill: `archive/**` é intocável, e uma base que nunca recebeu o `git mv` é
  um `git cherry-pick` do humano. A spec conserta o comando, não o histórico.
- **A menor variante — pular os passos 3 e 5 no caminho abandonado.** Arquivar na
  base e não colher nada seria mais simples e resolve as duas perdas, mas troca
  um bug de perda de dado por um bug de dado nunca criado: o comando declara em
  `## Doctrine` (linhas 63-66) que um abandono colhe "at most what was learned by
  *not* building it". Recusada; ver `## Alternatives Considered`.
- **Rever se o passo 3 deveria rodar num abandono.** É uma pergunta de doutrina,
  não de ordem, e está aberta em `## Open Decisions`. Esta spec faz o passo 3
  cair na base *se* ele rodar, sem decidir se deve rodar.
- **`docs/standards/git/**` do repo alvo.** Continua read-if-present, nunca
  instalado e nunca inferido. Se o alvo declarar como apaga branch, vale o dele.
- **Um comando ou flag novo.** Nada de `/specs:abandon` nem de flag nova: o
  `--outcome abandoned` já existe e é o lugar da correção.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/workflows/plan-git-record.md` — a regra de **lugar** ao lado da
  regra de ordem que a seção §Every record is written before the thing it
  describes já enuncia: um registro é escrito onde precisa sobreviver, e num
  fechamento sem merge isso é o checkout da base. Mais a contrapartida de branch
  para §A worktree is removed after a successful merge, and never forced — a linha
  159 desse doc já diz "it does **not** delete the branch — that stays the
  separate offer it already was" e é onde falta dizer *como* apagar.

Este é o único doc que a spec promete escrever, e a escolha é deliberada:
`plan-lifecycle.md` também fala do registro `merge:`, mas seu escopo é pasta,
estágio derivado e "frontmatter registra julgamento humano" — nada disso muda. O
`resource:` de `plan-git-record.md`, por outro lado, já nomeia
`commands/specs/conclude.md` e `specs-isolate/git.md`, que são exatamente os
arquivos que esta spec edita.

### Standards at `authority: background` this spec may resolve

- none — os quatro standards em `background` do bundle
  (`automation/session-evidence.md`, `automation/agents.md`,
  `automation/context-budget.md`, `quality/selftest-mutation.md`) não tocam este
  assunto. Verificado em 2026-07-30 com `grep -rl '^authority: background'
  docs/standards/`.

### Product code this spec expects to touch

- `plugins/quenching/commands/specs/conclude.md` — o ramo por `outcome` nos passos
  3, 4, 5 e 6, mais §Resuming e §Invariants
- `plugins/quenching/assets/references/specs-conclude/distill.md` — §Two moments,
  one table: a coluna "Where it lands" passa a depender do `outcome`
- `plugins/quenching/assets/references/specs-isolate/git.md` — como uma branch é
  apagada, ao lado de §The worktree is removed after a successful merge
- `plugins/quenching/assets/checks/conclude-order-check.sh` — o braço `abandoned`
- `plugins/quenching/assets/specs/QUENCHING.md` — as linhas 273-281, que hoje
  afirmam que o arquivamento e a destilação caem sempre na branch de trabalho

Fora desta lista de propósito: `VERSION`, `plugin.json`, `marketplace.json` e as
constantes `VERSION` dos três scripts. Um bump não é task — `conclude.md` linhas
75-78 dizem que o que um standard prende ao **merge** é resolvido no passo 5 do
próprio fechamento, e nunca agendado como trabalho da spec.

## Validation

A afirmação central desta spec é sobre **ordem**, e nenhum arquivo a contém: "o
fechamento chegou na base" é verdadeiro ou falso de uma *execução*.
`docs/standards/quality/surface-verification.md` §An ordering property is verified
by running the cycle já nomeia a forma — um repo `git init` descartável, o ciclo
percorrido de verdade, e depois asserções sobre o **estado real do git**, "not on
what the run reported" (linhas 184-187).

### A checagem que teria pegado este defeito

O braço `abandoned` de `plugins/quenching/assets/checks/conclude-order-check.sh`.
Ele percorre create → isolate → execute → conclude(`--outcome abandoned`) num repo
descartável, **sem mergear**, e então pergunta ao git — a partir do checkout da
base, com `git -C`:

    ./plugins/quenching/assets/checks/conclude-order-check.sh

Cinco asserções, todas hoje falsas e todas verdadeiras depois da correção:

1. `git -C {base} cat-file -e {base}:specs/archive/{arquivo-da-spec}` sai **0** —
   o `git mv` chegou na base.
2. `git -C {base} cat-file -e {base}:specs/plans/{arquivo-da-spec}` sai
   **diferente de 0** — a spec saiu de `plans/` na base.
3. o `outcome: abandoned` está no frontmatter da versão que a base tem, não só na
   da branch.
4. o caminho da nota `authority: background` que a destilação escreveu resolve na
   base.
5. **e sobrevive a apagar a branch**: depois de `git branch -D plan/{slug}` a
   partir do checkout da base, as asserções 1 a 4 continuam verdadeiras. Esta é a
   asserção que falha hoje, e é o defeito inteiro numa linha.

Mais duas que garantem que a correção não virou um merge disfarçado:

6. `git -C {base} branch --merged` **não** lista `plan/{slug}`.
7. nenhum commit que a run criou na base é um merge — cada um tem um pai só.

`grep -i abandon` nesse script devolve **zero** linhas em 2026-07-30: as oito
asserções existentes cobrem só o caminho `done`, e é por isso que este defeito
atravessou uma spec inteira como descoberta. As oito têm de continuar passando.

### As checagens mecânicas

A partir de `plugins/quenching/`, o mesmo conjunto que o `CLAUDE.md` do repo
declara — mais o bundle da raiz, por causa do standard novo:

    cat VERSION
    python3 assets/bin/specs.py --version
    python3 assets/bin/skills.py --version
    python3 assets/hooks/okf-validate.py --version
    python3 assets/hooks/okf-validate.py assets/docs
    python3 assets/hooks/okf-validate.py assets/specs/plans --listing-root
    python3 assets/bin/skills.py --root . doctor --json    # 26 comandos, sem findings
    python3 assets/bin/skills.py --root . lint --json      # exit 0
    python3 assets/bin/specs.py validate

E da raiz do repositório, porque a task 4 escreve em `docs/standards/`:

    python3 plugins/quenching/assets/hooks/okf-validate.py docs

### O que NÃO é declarado aqui, e por quê

`functional-checks.sh` **não** entra nesta seção nem em nenhum `verify:`, mesmo
esta spec editando um corpo de comando.
`docs/standards/quality/surface-verification.md` §The harness belongs to the skill
front, not to the spec cycle é explícito: o harness "is **not** named in a spec's
`## Validation` or a task's `verify:`" (linha 112), porque cada checagem é uma
sessão de agente cobrada e, medido sobre todo o `specs/archive/`, **toda** run
vermelha que ele já produziu veio de defeito dele mesmo, nenhuma de regressão da
superfície. A prova de que o corpo editado ainda carrega é do `/skill:new`, no
momento em que o corpo é editado. Está declarado como omissão deliberada, não
esquecimento.

### Invariantes que precisam continuar valendo

- nenhum `--amend`, nenhum force-push, nenhum `--no-verify`, nenhum
  `--no-gpg-sign`;
- `specs/archive/**` intocado, com as duas exceções que `conclude.md` linhas
  387-391 já enumeram;
- nada em `commands/**` além de `conclude.md`, porque `commands/**` é a única
  árvore registrada.

## Design

### A ordem exata que perde a nota

Cada linha é uma citação de `plugins/quenching/commands/specs/conclude.md`. A
coluna "chega na base?" é a única que importa.

    passo  o que escreve                         commita em     chega na base?
    ---------------------------------------------------------------------------
    2      reviewed: {date}                      branch         não
    3      docs emergentes (sem ramo por outcome) branch         não   (l. 155)
    4      ## Outcome, git mv, outcome:           branch         não   (l. 182)
    5      nota authority: background            branch         não   (l. 204)
    6      done      -> merge                     base           sim
    6      abandoned -> nada é mergeado           —              nunca (l. 336)
    6      abandoned -> "delete it" é oferecido    —              destrói 2..5

No caminho `done` a linha 6 fecha a conta: "a single merge carries the code, the
emergent docs, the archived spec and the distillation together — and reverting
that merge reverts the spec's whole footprint" (linhas 16-17). No caminho
abandonado essa linha não existe, e nada tomou o lugar dela.

### A causa: o carregador desapareceu junto com o merge

`move-conclude-merge-last` moveu toda escrita para a branch **porque o merge a
levaria para a base**. A premissa é o merge. O caminho abandonado herdou a
conclusão e perdeu a premissa — e o `## Out of Scope` daquela spec registrou o
raciocínio invertido: "Não há merge, então a reordenação não muda nada ali".
Não haver merge não é neutro; é a remoção do único carregador.

A regra que sobrevive à correção é mais forte e mais curta: **um registro é
escrito onde ele precisa sobreviver.** Quando existe merge, isso é a branch,
porque o merge carrega. Quando não existe merge, isso é o checkout da base.

### Por que escrever na base aqui não contraria merge-last

O invariante literal é "Never write anything after the merge" (linha 369) e a
propriedade comprada é "reverting that merge reverts the spec's whole footprint"
(linhas 16-17). Num abandono:

- não há merge, então "depois do merge" é vazio — o invariante não é tocado;
- não há merge para reverter, então a propriedade de reversão nunca esteve
  disponível ali, e não é perdida.

`docs/standards/workflows/plan-git-record.md` §Every record is written before the
thing it describes é o standard que rege isto, e ele fala de *ordem* (nada é
escrito depois daquilo que descreve), não de *lugar*. Um commit no checkout da
base num comando que não mergeia não descreve nada que ainda não exista. O
standard não é contrariado; ele é completado com o caso que não tinha resposta.

### A forma escolhida: escrever no checkout que já tem a base

O mecanismo já existe no passo 6 e é reusado sem inventar nada:

    git worktree list --porcelain      # qual checkout tem a base
    git -C {esse caminho} add ...      # e commita ali

Três propriedades vêm de graça, porque são as mesmas do merge:

- **Nunca `git checkout {base}`** — de dentro de uma worktree isso falha com
  exit 128 (linha 296 e `specs-isolate/git.md` linhas 235-239).
- **Quando nenhum checkout tem a base, o run para e diz** — a mesma recusa que o
  passo 6 já faz (linhas 300-305), pela mesma razão: nada é fabricado.
- **Uma árvore suja da base é uma recusa, não um commit.** É a única
  pré-condição nova que este desenho exige, e ela espelha a árvore-limpa que
  `/specs:execute` já cobra. Escrever num checkout que o humano está usando é
  como se perde trabalho não commitado.

Uma spec **sem** registro `branch:` (trabalho feito no lugar) não muda em nada:
o passo 2 já manda pular para o passo 4 quando não há branch, e ali o checkout
corrente *é* o da base.

### O que o git já recusa, e por que isso não basta

Três recusas do git tornam a perda 1 difícil de acertar, e nenhuma cobre a
perda 2:

| tentativa | o que o git faz |
| --- | --- |
| `git branch -d` numa branch não mergeada | recusa: "not fully merged", exit 1 |
| apagar a branch em que se está | recusa: "Cannot delete branch checked out at" |
| apagar uma branch conferida em outra worktree | recusa, mesma mensagem |
| `git branch -D` do checkout da base | **apaga**, e os commits só voltam pelo reflog, até o gc |

Por isso o desenho não se apoia nelas. A perda 2 acontece com zero deleções, e a
perda 1 depende de um `-D` que o comando hoje não proíbe em lugar nenhum — nem
no corpo, nem em `## Invariants`, nem em `specs-isolate/git.md`. A assimetria é o
buraco: o comando aprendeu a lição sobre `--force` para worktree (linhas
363-365) e não a aplicou a branch.

### A oferta de deleção passa a ser informada

Depois da correção a oferta fica honesta em vez de defensiva, porque o
fechamento já está na base: o que morre com a branch é só o trabalho parcial que
ninguém adotou. A oferta enumera isso e mantém o default "keep" que
`## Doctrine` já fixa (linhas 68-69). O comando oferece `git branch -d` e, na
recusa do git, **relata a saída do git verbatim e mantém a branch** — nunca
repete forçado, exatamente como já faz em `git worktree remove`.

### Como isto é verificado

Ordem não é conteúdo de arquivo: nenhum linter e nenhuma leitura de
`conclude.md` observa "o fechamento chegou na base".
`docs/standards/quality/surface-verification.md` §An ordering property is
verified by running the cycle já nomeia a forma certa e já recomenda usá-la
"whenever a rule is phrased as an ordering, a boundary, or a 'never after'"
(linhas 189-190). O braço `abandoned` do `conclude-order-check.sh` é essa forma;
`## Validation` declara as asserções.

Medido em 2026-07-30: `grep -i abandon` em
`plugins/quenching/assets/checks/conclude-order-check.sh` devolve **zero**
linhas. A única checagem do repo que enxerga ordem nunca percorreu o caminho
abandonado, e é por isso que o defeito atravessou uma spec inteira como
descoberta.

### Contratos que este desenho não pode contrariar

| contrato | o que ele exige | como o desenho obedece |
| --- | --- | --- |
| `conclude.md` §Invariants l. 366 | nunca mergear branch de spec abandonada | não mergeia; commita na base |
| `conclude.md` §Invariants l. 369 | nada é escrito depois do merge | não há merge no caminho |
| `conclude.md` §Invariants l. 387-391 | só duas escritas em `archive/**`, ambas na spec sendo fechada | as duas continuam sendo as mesmas; muda o checkout, não o alvo |
| `plan-lifecycle.md` §The archive is append-only | append só de fato que não existia no `promote` | inalterado |
| `specs-isolate/git.md` l. 301-302 | worktree nunca removida num abandono | inalterado |
| `specs-isolate/git.md` §The read-if-present rule | convenção do alvo vence | a forma de apagar branch respeita `docs/standards/git/**` do alvo |
| `docs/standards/architecture/plugin-layout.md` | `commands/**` é a única árvore registrada | a correção é corpo de comando + referência + checagem, nada novo em `commands/**` |

### O que a ordem atual também quebra: o próprio §Resuming

Achado pelo premortem, e é um segundo defeito da mesma causa. A tabela §Resuming
diz que o estágio "archive" já rodou quando "the file is in `archive/` with
`outcome:` stamped" (linha 92). Num abandono esse sinal existe **só na branch**.
Então um segundo `/specs:conclude` rodado a partir do checkout da base lê o sinal
como falso e refaz o `git mv` — produzindo um arquivamento paralelo que depois
conflita com o da branch. A resumibilidade que o comando anuncia como "a property
of the data, not of a session" (linhas 28-30) é, no caminho abandonado,
dependente de qual checkout você está pisando.

A é a correção dos dois: com o fechamento na base, cada sinal de §Resuming volta
a ser um fato do repositório em vez de um fato da branch.

### A pré-condição nova, e por que ela é o preço de A

A é a única opção que escreve num checkout que o humano pode estar usando, e isso
tem um preço declarado: **a árvore da base tem de estar limpa.** Suja, o run
recusa, relata `git -C {checkout da base} status --porcelain` verbatim e para —
sem escrever nada, do mesmo jeito que o passo 6 já para quando nenhum checkout
tem a base (linhas 300-305). E os commits nomeiam **os caminhos**, nunca
`git add -A`, que `specs-execute/execution.md` §The commit já proíbe.

Esse preço é intrínseco a qualquer correção que faça o arquivamento chegar na
base, ou seja a A, C e E — só B o evita, e o evita justamente por não consertar a
perda que importa.
## Alternatives Considered

### A forma da correção

| | Abordagem | Custo | Ganho | O que fecha |
| --- | --- | --- | --- | --- |
| **A** *(escolhida)* | Num abandono, o fechamento é commitado no checkout que já tem a base; a oferta de apagar a branch diz o que custa e nunca força | ramo por `outcome` nos passos 3, 4, 5 e 6; uma pré-condição nova (árvore da base limpa); um braço novo na checagem de ordem | resolve as **duas** perdas; a base fica consistente sem depender de escolha nenhuma; apagar a branch passa a ser genuinamente seguro | nada — B e E continuam disponíveis se A se mostrar caro |
| B | Manter tudo na branch e **recusar** a oferta de deleção enquanto algo tiver sido escrito | mínimo: uma condição na oferta do passo 6 | salva a nota e os docs emergentes | a base **nunca** aprende que a spec fechou (perda 2 intocada), e a branch vira dívida permanente — um ref que ninguém pode apagar porque é a única cópia do arquivamento |
| C | Mergear só o intervalo do fechamento para a base | um mecanismo de git novo que a frente não tem | um merge carrega o fechamento | contraria `## Invariants` linha 366 ("Never merge an abandoned spec's branch") e reintroduz merge parcial, que nenhuma das quatro estratégias descreve |
| D | Não fazer nada; contar com as três recusas do git | zero | mantém o comportamento registrado como descoberta | não cobre a perda 2, que acontece com zero deleções — e a perda 1 depende de um `-D` que nada no repo proíbe |
| E | A menor coisa que funciona: num abandono, pular os passos 3 e 5 e arquivar direto na base | menor que A — dois ramos em vez de quatro | resolve as duas perdas com menos texto | joga fora a única colheita que `## Doctrine` linhas 63-66 autoriza ("at most what was learned by *not* building it"), trocando perda de dado por dado nunca criado |
| F | Comprar ou emprestar | — | — | não existe: o defeito é ordem dentro de um corpo de comando deste plugin; não há nada a comprar, e dizer isso é mais honesto que preencher a linha |

**Por que A vence B.** B é bem mais barata e é a segunda saída que o
`## Problem` original propunha, então merece o argumento explícito: B protege a
nota e deixa o arquivamento onde está. Como o `git mv` nunca chega na base,
`/specs:continue` continua oferecendo uma spec concluída, `/specs:status`
continua contando ela em `plans/`, e a única saída é o humano mergear à mão uma
branch que `## Invariants` proíbe mergear. B conserta o sintoma que a descoberta
descreveu e deixa em pé a perda que ninguém tinha visto.

**Por que A vence E.** E é tentadora porque o comando *já* diz que um abandono
colhe quase nada ("Most abandonments distil nothing, and that is the correct
result", linha 199). Mas "quase nada" não é "nada", e a diferença é o caso que
justifica o passo 5 existir num abandono: o que se aprendeu **por não** ter
construído. Remover a colheita para consertar a ordem é resolver a pergunta
errada.

**Por que A não é C.** Commitar no checkout da base e mergear a branch para a
base produzem estados diferentes: A não traz nenhum commit da branch, então o
trabalho parcial continua sendo history e não change — exatamente o que
`## Doctrine` linhas 68-69 exige.

### O que o premortem mudou

Uma pergunta, depois das sete histórias: a spec mantém A ou troca?

**Mantém.** A pior história — varrer a árvore suja do checkout da base — é um
risco que **A introduz** e que B não tem, então merece ser dita nesses termos: a
única vantagem real de B é nunca escrever na base. Só que esse preço é
intrínseco a fazer o arquivamento chegar na base, então ele é igual em A, C e E,
e a alternativa que o evita é exatamente a que deixa a perda 2 em pé. O preço se
converte numa recusa — árvore da base suja para o run — e uma recusa é mais
barata que a dívida permanente de branch que B cria.

O premortem também mexeu em duas coisas sem mudar a escolha: acrescentou a
recusa da árvore limpa como task de mitigação, e descobriu que a oferta de
deleção é inaceitável pelo git no caso comum (branch conferida na worktree que
um abandono não remove). As duas estão em `## Risks`.

## Open Decisions

- **O passo 3 (docs emergentes) deve rodar num fechamento abandonado?** Hoje ele
  roda por omissão — não há ramo por `outcome` em lugar nenhum do passo 3 — e
  esta spec preserva isso, só mudando *onde* ele commita. Mas a doutrina do
  comando diz que um abandono colhe "at most what was learned by *not* building
  it" como `authority: background` (linhas 63-66), e o passo 3 não tem esse teto
  escrito: um doc emergente colhido num abandono pode sair `authority: current`.
  Se o passo 3 deve ficar, ficar com teto `background`, ou não rodar, é decisão
  de quem é dono da doutrina de destilação
  (`assets/references/specs-conclude/distill.md` §Two moments, one table), não
  desta correção de ordem. **Como se decide:** no primeiro fechamento abandonado
  real depois desta spec — se ele produzir um candidato de passo 3, a pergunta
  tem um caso concreto para julgar; se não produzir nenhum em vários abandonos, a
  resposta é que o passo 3 nunca teve conteúdo ali e o ramo pode ser removido.
- **Se `reduce-execute-conclude-cost` fundir os passos 3 e 5 numa passada única
  de `docs/`, esta spec passa a ter um momento de escrita em vez de dois.** Essa
  fusão é a alternativa C que `move-conclude-merge-last` deixou explicitamente
  disponível no seu `## Out of Scope` (linhas 122-123), e é uma economia óbvia
  para quem estiver cortando custo do `conclude`. **Como se decide:** pela spec
  irmã, não por esta. Esta spec é escrita para ser indiferente ao número de
  momentos — a regra que ela instala é "num abandono, o fechamento commita no
  checkout da base", e ela vale igual para um momento ou dois. Se a irmã fundir
  primeiro, a task 1 desta spec aplica o ramo ao passo fundido; se esta fundir
  depois, o ramo já está no lugar. Nenhuma das duas precisa esperar a outra, e
  nenhuma pode assumir o resultado da outra.

## Risks

Cada risco abaixo saiu de uma história do premortem — "é três meses depois, isto
foi construído e deu errado" — e cada um virou exatamente uma coisa: uma task de
mitigação, uma mitigação nomeada, ou um risco aceito com o motivo.

- **Varrer a árvore suja do checkout da base.** É o pior caso, e é *novo*: A
  escreve num checkout que o humano provavelmente está usando para outra coisa —
  precisamente o estado que a forma worktree, recomendada sem condição, produz.
  Um `git add -A` ali empacota trabalho não commitado de outra pessoa dentro do
  commit de abandono. Mitigação, em duas partes e ambas com task: **recusar**
  quando `git -C {checkout da base} status --porcelain` não vem vazio, relatando a
  saída verbatim e parando — a mesma recusa que o passo 6 já faz quando nenhum
  checkout tem a base; e commitar **apenas os caminhos nomeados**, nunca
  `git add -A`, que `specs-execute/execution.md` §The commit já proíbe.
- **A oferta de deleção que o git nunca vai aceitar.** Num abandono a worktree
  **não** é removida (linhas 336-337 e os "three bounds" de
  `specs-isolate/git.md` linhas 301-302), então a branch continua conferida ali e
  `git branch -d` recusa com "Cannot delete branch checked out at". Como worktree
  é a forma recomendada, esse é o caso comum, e hoje o comando oferece de
  qualquer jeito e manda "record the choice in the report" (linha 337) — relatando
  uma escolha que não podia ser cumprida. Mitigação: o mesmo
  `git worktree list --porcelain` que o comando já lê diz se a branch está
  conferida em algum lugar; quando está, a oferta declara isso em vez de oferecer
  uma deleção que vai falhar.
- **`-D` pela mão do humano, fora do comando.** Com a oferta endurecida para
  `git branch -d`, quem quer a branch fora vai bater na recusa do git e rodar
  `-D` por conta própria. ACCEPTED — e a aceitação é o ponto de A: depois de A o
  fechamento já está na base, então um `-D` do humano custa só o trabalho parcial
  que ninguém adotou. Antes de A esse mesmo `-D` era a perda. O risco não é
  eliminado; ele deixa de ter consequência.
- **Nada observa a ordem, e a próxima refatoração desfaz.** Medido em 2026-07-30:
  `grep -i abandon` em `plugins/quenching/assets/checks/conclude-order-check.sh`
  devolve zero linhas — a única checagem do repo que enxerga ordem nunca percorreu
  este caminho. E há precedente do modo de falha: o `## Out of Scope` de
  `move-conclude-merge-last` (linhas 123-125) mostra exatamente como um revisor se
  convence de que o caminho abandonado "não muda nada". Mitigação com task: o
  braço `abandoned` do `conclude-order-check.sh`, declarado em `## Validation`.
- **Fechamento pela metade na base.** A run arquiva na base (commit 1) e morre
  antes da nota: a base fica com a spec em `archive/` e `outcome: abandoned`, sem
  linha de destilação no `## Outcome`. ACCEPTED — é literalmente o estado que
  §Resuming já cobre ("the file is in `archive/` with `outcome:` stamped → skip
  the move; go to distil", linha 92), e é **melhor** que o meio-estado de hoje,
  porque hoje esse sinal fica só na branch e um resume feito da base o lê como
  falso (ver `## Design` §O que a ordem atual também quebra).
- **Duas specs irmãs reescrevendo `conclude.md` em paralelo.**
  `reduce-execute-conclude-cost` reavalia o custo de `/specs:execute` e
  `/specs:conclude`, e `add-specs-cycle-run-modes` acrescenta run modes aos
  comandos do ciclo — as três tocam o mesmo arquivo. Mitigação: esta spec
  acrescenta **ramos por `outcome`** dentro dos passos 3, 4, 5 e 6 e não move,
  renumera nem funde passo nenhum, então o conflito esperado é aditivo. A
  fronteira está declarada em `## Open Decisions`; esta spec não assume o
  resultado de nenhuma das duas.
- **O manual embarcado passa a mentir.**
  `plugins/quenching/assets/specs/QUENCHING.md` linhas 280-281 afirmam "The
  archive move, the distillation and these all land on the **work branch**", que
  deixa de valer para `abandoned`. Nada mecânico pega isso: `okf-validate` roda
  sobre `assets/docs` e `assets/specs/plans`, não sobre esse manual. Mitigação com
  task própria, e só no manual da própria frente — o `## Discoveries` de
  `move-conclude-merge-last` (linha 517) já registrou que mexer nos outros dois
  QUENCHING.md é churn.

Uma história foi descartada por não converter em nada: **um repo alvo sem git, ou
uma spec sem registro `branch:`.** O passo 2 já manda pular para o passo 4 quando
não há branch, e nesse caso o checkout corrente *é* o da base — o desenho não
muda nada ali, e inventar um risco para essa linha seria enchimento.

## Tasks

### 1. O ramo por `outcome` em `conclude.md`

- [ ] 1.1 Nos passos 3, 4 e 5, um fechamento `--outcome abandoned` commita no checkout que já tem a base — localizado com o `git worktree list --porcelain` + `git -C` que o passo 6 já usa — e nunca na branch de trabalho
      files: plugins/quenching/commands/specs/conclude.md
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json
- [ ] 1.2 O mesmo ramo recusa quando a árvore da base está suja: relata `git -C {checkout da base} status --porcelain` verbatim e para sem escrever nada, e commita só os caminhos nomeados — nunca `git add -A`
      files: plugins/quenching/commands/specs/conclude.md
      pattern: plugins/quenching/commands/specs/conclude.md
- [ ] 1.3 No passo 6, a oferta de apagar a branch enumera o que morre com ela e o que já está na base, oferece só `git branch -d`, e na recusa do git relata a saída verbatim e mantém a branch
      files: plugins/quenching/commands/specs/conclude.md
- [ ] 1.4 Quando a branch está conferida numa worktree que o abandono não remove, a oferta declara isso em vez de oferecer uma deleção que o git vai recusar
      files: plugins/quenching/commands/specs/conclude.md
- [ ] 1.5 §Resuming lê os sinais de estágio do checkout da base quando o `outcome` é `abandoned`, e §Invariants ganha a proibição de `git branch -D`, espelhando a de `--force` em `git worktree remove`
      files: plugins/quenching/commands/specs/conclude.md
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json

### 2. As referências

- [ ] 2.1 [P] `specs-conclude/distill.md` §Two moments, one table: a coluna "Where it lands" passa a ramificar por `outcome` — branch quando existe merge, checkout da base quando não existe
      files: plugins/quenching/assets/references/specs-conclude/distill.md
- [ ] 2.2 [P] `specs-isolate/git.md` ganha como uma branch é apagada — nunca `-D`, a recusa do git é a segurança — ao lado de §The worktree is removed after a successful merge, and never forced
      files: plugins/quenching/assets/references/specs-isolate/git.md

### 3. A checagem que enxerga a ordem

- [ ] 3.1 O braço `abandoned` de `conclude-order-check.sh` com as sete asserções de `## Validation`, incluindo a que apaga a branch e reconfere que o fechamento sobreviveu
      files: plugins/quenching/assets/checks/conclude-order-check.sh
      pattern: plugins/quenching/assets/checks/conclude-order-check.sh
      verify: ./plugins/quenching/assets/checks/conclude-order-check.sh
- [ ] 3.2 As oito asserções do caminho `done` continuam passando junto com as novas
      verify: ./plugins/quenching/assets/checks/conclude-order-check.sh

### 4. O standard

- [ ] 4.1 Escrever `docs/standards/workflows/plan-git-record.md` — a regra de lugar ao lado da de ordem, e a contrapartida de branch da regra de worktree (`authority: current`, porque a task 3 prova)
      files: docs/standards/workflows/plan-git-record.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs

### 5. O manual embarcado

- [ ] 5.1 `assets/specs/QUENCHING.md` linhas 273-281: "The archive move, the distillation and these all land on the **work branch**" passa a valer só para `done`
      files: plugins/quenching/assets/specs/QUENCHING.md

### 6. A suíte inteira

- [ ] 6.1 Rodar as checagens mecânicas de `## Validation` inteiras e reportar cada saída
      verify: python3 plugins/quenching/assets/bin/specs.py validate
- [ ] 6.2 Relatar o que `okf-validate docs` disser sobre docs que esta branch deixou stale — material do passo 3 do `conclude` (docs emergentes), não de task
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
