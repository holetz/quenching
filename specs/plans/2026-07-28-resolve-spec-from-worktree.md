---
slug: resolve-spec-from-worktree
title: Resolve a spec from its own worktree before falling back to the current branch
verification: per-section
priority: {level: 12, criticality: high, complexity: 3, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# Resolve a spec from its own worktree before falling back to the current branch

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

Um spec pode ser isolado num **worktree**: um segundo checkout do mesmo repositório, ao lado do
principal, com a branch `plan/{slug}` daquele spec. É a forma que o plugin recomenda antes de
construir, e ela deixa o checkout principal intocado.

O incômodo que o `## Problem` descreve é que `/specs:execute` lê o spec do checkout em que a sessão
está, e não daquele worktree. Lendo o código, a leitura obsoleta acabou sendo só o sintoma mais
visível: o `## Problem` termina nomeando a causa medida — nada nunca move a run para dentro da árvore
que `/specs:isolate` acabou de criar — e as outras consequências que vêm com ela, das quais commitar
na branch errada é a pior. `## Proposal` lista o que fica verdadeiro depois.

`## Design` é onde a diferença entre sintoma e causa decide o desenho: ele move a *árvore* em que a run
opera, em vez de redirecionar o *arquivo* que ela lê, e explica por que redirecionar o arquivo é
impossível de commitar. Ele mede quatro comandos de git para separar o que cada um responde, porque o
candidato mais óbvio (`--git-common-dir`) responde a pergunta errada; mostra que a detecção tem **três**
estados e não dois; e diz por que a correção mora nos corpos de comando e não no resolvedor de
workspace, que está correto.

`## Alternatives Considered` guarda as seis formas inteiras, incluindo "não fazer nada" e a proposta
inversa de deixar de recomendar worktree. `## Out of Scope` fecha o que este spec deliberadamente não
abre — começando por `/specs:create`, que foi um corte tomado na crítica — e nomeia os dois specs
irmãos que ficam com a vizinhança.

`## Risks` é o resultado do premortem: oito histórias com como cada uma seria detectada, e a pior é a
que ninguém veria — escrever na árvore errada em silêncio, que é por que o desenho carrega uma asserção
de `git rev-parse --show-toplevel`. `## Open Decisions` guarda o que honestamente não está decidido,
começando pela pergunta mecânica que a tarefa 1.1 mede em vez de supor.

`## Impact` declara o único documento de `docs/standards/` que este spec escreve e lista os seis
arquivos que ele altera — neste repo os corpos de comando **são** o código-fonte. `## Validation`
separa o que um comando prova do que nada prova nesta sessão, e nomeia o harness que deliberadamente
**não** entra ali. `## Tasks` está ordenado de propósito: medir, o contrato compartilhado, o braço de
recusa que já entrega a correção, a automação que pode ser cortada sem perdê-la, o roteador isolado
para poder migrar, o standard, e a verificação no fim.

## Problem

Quando `/specs:execute` constrói um spec, ele lê o arquivo do spec a partir do checkout em que
está por acaso — a branch atual. Mas um spec que foi isolado em um worktree também vive lá, e essa
cópia é a que o trabalho está de fato acontecendo contra: ela carrega as caixas marcadas, as
descobertas e qualquer seção que o executor tenha atualizado na branch.

Ler a cópia do checkout principal significa executar contra uma visão obsoleta — caixas já
marcadas no worktree continuam parecendo abertas, e uma escrita cai no arquivo errado.
`/specs:execute` deveria preferir o spec dentro do worktree para aquele slug quando um existe, e
recair na branch atual apenas quando não existe.

**A causa é mais funda do que a leitura obsoleta, e foi medida.** O resolvedor de workspace não
está quebrado: `find_specs_root` (`plugins/quenching/assets/bin/specs.py:931-949`) caminha para
cima até o `specs/` mais próximo e acerta para *a árvore em que está* — de `/repo` resolve
`/repo/specs`, de `/repo-slug` resolve `/repo-slug/specs`. O que falta é que **nada move a run para
dentro do worktree**. `/specs:isolate` faz `cd` para dentro da árvore nova apenas para rodar o
`worktreeSetup` (`commands/specs/isolate.md:150-151`); todo o resto da run, e todo comando que vem
depois dela, mantém o cwd original. A leitura obsoleta é então uma consequência entre várias, e as
outras são piores:

- `commands/specs/isolate.md:139-141` roda `git add "{caminho do spec}" && git commit` a partir do
  checkout principal, o que commita o spec na branch **base** — exatamente o oposto do que aquele
  passo promete ("so the base is left exactly as it was").
- `/specs:execute` escreve o código no checkout principal e commita na base também, então nem o
  código nem a caixa marcada chegam a `plan/{slug}`.
- `git status --porcelain` é por árvore. A pré-condição de árvore limpa
  (`assets/references/specs-execute/execution.md:27-29`) lê o checkout principal e passa limpa
  enquanto o worktree guarda trabalho não commitado — medido.
- `/specs:continue` manda "check it out to continue" para um spec cuja branch está viva num worktree
  ao lado. Aquele `git checkout` falha com exit 128 (`fatal: 'plan/{slug}' is already used by
  worktree at ...`) — a mesma falha que `assets/references/specs-isolate/git.md:235` já documenta
  para `git checkout {base}`.

## Proposal

Depois desta mudança:

- Existe **uma regra escrita num só lugar** dizendo qual árvore uma run de `/specs:*` opera, e os
  comandos do ciclo a citam em vez de cada um decidir por conta própria.
- `/specs:isolate` termina reportando **o caminho do worktree** que criou, ou que já existia para
  aquele slug, como fato explícito da saída e não só na prosa.
- `/specs:isolate` commita o arquivo do spec na árvore onde `plan/{slug}` está checada, então a base
  fica exatamente como estava — que é o que o passo 5 daquele corpo já promete e hoje não entrega.
- `/specs:execute`, `/specs:develop` e `/specs:create` rodam **dentro do worktree** quando o spec já
  está isolado num, então a pré-condição de árvore limpa, a leitura do spec, as escritas de seção,
  as escritas de código e os commits todos concordam sobre qual árvore é o assunto.
- Quando mover a run é impossível — a árvore está registrada mas o caminho não existe, ou a branch
  está viva num clone diferente — o comando **para e diz onde o trabalho está**, em vez de operar na
  árvore errada em silêncio.
- `/specs:continue` para de mandar `git checkout` numa branch que um worktree já ocupa; ele nomeia o
  caminho da árvore, porque aquele `checkout` falha com exit 128.
- `find_specs_root` não muda: a caminhada para cima continua sendo a única resolução de workspace, e
  continua correta para a árvore em que está.

## Out of Scope

- **`/specs:create`** — **corte tomado na crítica.** Um spec que está sendo criado ainda não tem slug
  mintado, então `git worktree list` não pode ter `plan/{slug}` para ele: não existe árvore para
  resolver. O único caso restante é criar um spec estando dentro do worktree de *outro* spec, que não
  é o problema deste spec e cujo comportamento atual — o arquivo cai na árvore em que você está — já
  é o correto. O `## Problem` nomeia `/specs:execute`; incluir `create` era inflação de escopo.
- **Commitar o trabalho da run no fim de `develop` / `create` / `execute`** — é o spec irmão
  `commit-on-worktree-specs`. Este spec decide *qual árvore* a run opera; aquele decide *se e quando*
  o que ela produziu é commitado. Os dois se encontram na mesma árvore, e este não escreve nenhuma
  regra sobre commitar no fim.
- **Dar aos aligns forma de worktree + merge** (`/docs:align`, `/specs:align`, `/skill:align` e o
  condutor `/align`) — é `align-in-worktree-then-merge`, outra frente. Nenhum corpo de align é tocado
  aqui.
- **Merge e remoção do worktree** — já são de `/specs:conclude` e já estão corretos: `git -C` para
  merge na árvore que tem a base, `git -C {base} worktree remove` depois, e `git checkout {base}`
  proibido (`assets/references/specs-isolate/git.md` §Merge strategies). Nada disso é reaberto.
- **Criar isolamento quando não existe** — continua sendo `/specs:isolate`, atrás da oferta com UM OK.
  Este spec nunca cria worktree; ele só encontra o que já existe.
- **Podar worktrees obsoletos** — a run *reporta* um `prunable` e nomeia `git worktree prune`, mas
  nunca o roda. Apagar isolamento é irreversível e não é o assunto deste spec.
- **Mudar `find_specs_root`** — deliberadamente não, e o motivo está em `## Design`: a caminhada para
  cima está correta, e ensinar git a ela contaminaria todo chamador.
- **Adicionar chave a `specs/config.json`** — o contrato é uma chave só, `worktreeSetup`
  (`docs/standards/workflows/worktree-setup.md` §One file, one key). O caminho do worktree é derivável
  de git; declará-lo não compra nada e abriria um sistema de configuração.
- **`/docs:import-memory`** — ele já resolve worktree por conta própria, caminhando dos pais do cwd
  (`commands/docs/import-memory.md:123,143`). Frente diferente, chave diferente, fica como está.
- **Rodar o `worktreeSetup` de novo** — mover o cwd de uma run não é segunda entrada para aquele hook,
  e `worktree-setup.md` §Who runs it, and where diz que só a criação o roda.
## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/workflows/worktree-run-tree.md` — qual árvore uma run de `/specs:*` opera quando o
  spec está isolado num worktree: os três estados do `git worktree list --porcelain`, a assimetria
  entre entrar num worktree e mover entre dois, e a asserção de `git rev-parse --show-toplevel` que
  cobre o modo de falha silencioso

O home é `workflows/` porque é onde os dois contratos vizinhos já moram —
`docs/standards/workflows/worktree-setup.md` e `docs/standards/workflows/plan-git-record.md`, ambos
com `resource:` apontando para `plugins/quenching/**`. Existe precedente direto: um contrato sobre o
comportamento do plugin é um standard deste repo, não só procedimento embarcado.

### Standards em `authority: background` que este spec pode resolver

- none — nenhum standard em `authority: background` cobre isolamento, worktree ou a frente de
  `specs/`. Os que existem estão em `automation/` e `quality/`, sobre assuntos que este spec não
  toca. O standard novo nasce `authority: current`, porque o spec prova a regra ao construí-la.

### Código de produto que este spec espera tocar

Neste repo os corpos de comando **são** o código-fonte, então a lista abaixo é o produto:

- `plugins/quenching/assets/references/specs-isolate/git.md` — a seção nova, dona única da regra
- `plugins/quenching/commands/specs/isolate.md` — reportar o caminho da árvore; commitar o spec na
  árvore que tem a branch (passos 5 e 7)
- `plugins/quenching/commands/specs/execute.md` — o passo 2, que hoje delega isolamento e não olha
  para onde a árvore ficou
- `plugins/quenching/commands/specs/develop.md` — mesma resolução antes de escrever seção ou
  frontmatter
- `plugins/quenching/commands/specs/continue.md` — a tabela de `branch` em `:87-94`, que hoje manda
  `git checkout`
- `plugins/quenching/assets/bin/specs.py` — `_candidate` e a vizinhança de `_git_refs`, aditivo: um
  campo no payload, nenhuma assinatura alterada

**Obrigação de release, não deste comando.** Tocar `specs.py` aciona o lockstep de versão — `VERSION`
e o `--version` dos três scripts embarcados têm de concordar (`docs/standards/ci-cd/versioning-release.md`).
Quem liquida isso é `/specs:conclude`, antes do merge; nenhuma tarefa aqui bumpa versão.

## Validation

Três camadas, e a terceira é honesta sobre o que nada prova.

### O que os checks permanentes provam

```bash
cd plugins/quenching
python3 assets/bin/skills.py --root . doctor --json   # baseline medido: 26 comandos, 0 findings
python3 assets/bin/skills.py --root . lint --json     # exit 0
python3 assets/bin/specs.py selftest                  # 12 canonical case(s), 0 error(s)
python3 assets/hooks/okf-validate.py assets/docs      # 0 error(s), 0 warning(s)
```

O standard novo entra na varredura de conformidade do bundle deste repo:

```bash
python3 plugins/quenching/assets/hooks/okf-validate.py docs
```
Tem de sair `0 error(s)` já contando `docs/standards/workflows/worktree-run-tree.md`, com o
`resource:` derivado dos anchors reais do doc e a entrada na tabela GENERATED de
`docs/standards/index.md` regenerada.

### O que prova esta mudança em particular

A mitigação do `## Risks` #4 — meia aterrissagem — tem de ser um comando, não uma intenção:

```bash
grep -l 'specs-isolate/git.md' \
  plugins/quenching/commands/specs/isolate.md \
  plugins/quenching/commands/specs/execute.md \
  plugins/quenching/commands/specs/develop.md \
  plugins/quenching/commands/specs/continue.md | wc -l
```
Tem de imprimir **4**. Hoje imprime **2** — medido: `develop.md` e `continue.md` não citam aquele
arquivo nenhuma vez. É por isso que a asserção vale: ela falha antes da mudança e passa depois, que é
a única forma de um check deste tipo significar algo.

O campo novo do payload é exercitado num workspace descartável, que é como o CLAUDE.md manda exercitar
`specs.py` (ele não tem fixture no repo):

```bash
# num repo temporário: specs.py new x, depois git worktree add ../tmp-x -b plan/x
python3 {caminho}/specs.py next --front --json    # o candidato de x traz o caminho da árvore
rm -rf ../tmp-x
python3 {caminho}/specs.py next --front --json    # agora o estado prunable, e NÃO o caminho
```
Os três estados do `## Design` são o roteiro do teste, e o terceiro — `prunable` — é exatamente o que
uma verificação ingênua deixaria passar.

### O que nada prova nesta sessão, declarado

O registro de comandos é montado no **início** da sessão, então nenhuma mudança em `commands/**` é
testável na sessão que a escreve (CLAUDE.md). As quatro edições de corpo ficam como **verificação
manual declarada**: `/skill:new` depois de editar cada comando, e o relatório da run tem de dizer que
a checagem foi manual em vez de omiti-la.

**`functional-checks.sh` não entra aqui, e isso é deliberado.** O CLAUDE.md é explícito: aquele
harness pertence à frente de skill, não vai no `## Validation` de um spec nem no `verify:` de uma
tarefa, porque cada check é uma sessão de agente cobrada e, medido no arquivo inteiro, toda run
vermelha que ele já produziu foi defeito dele mesmo e nenhuma foi regressão de superfície. Para
roteamento falado o instrumento é `/skill:eval`.

## Design

### A decisão: preferir a árvore, não o arquivo

O título deste spec diz "resolve a spec"; o desenho resolve **a árvore**. Apontar só a leitura do
spec para o worktree, mantendo o cwd no checkout principal, parte a run em duas: as escritas de
seção cairiam no worktree e as escritas de código no checkout principal, e o commit por tarefa — que
estagia os arquivos declarados **e** o arquivo do spec (`commands/specs/execute.md:156-157`) — não
teria como existir. Uma árvore por run é a única forma em que código e caixa marcada chegam no mesmo
commit, que é a garantia central de `docs/standards/workflows/plan-git-record.md` §Every record is
written before the thing it describes.

### Hoje, e depois

```
HOJE
  cwd = /repo  (base)                       worktree = /repo-slug  (plan/{slug})
  ├─ find_specs_root -> /repo/specs         ├─ specs/plans/...  (as caixas de verdade)
  ├─ git status --porcelain -> limpo        └─ nunca lido, nunca escrito, nunca commitado
  ├─ lê/escreve /repo/specs/plans/...
  └─ git commit -> cai na BASE

DEPOIS
  /specs:isolate reporta o caminho da árvore; a run passa a operar nele
  cwd = /repo-slug  (plan/{slug})
  ├─ find_specs_root -> /repo-slug/specs    (a mesma caminhada para cima, sem mudança)
  ├─ git status --porcelain -> a árvore que o trabalho está sujando
  ├─ lê/escreve /repo-slug/specs/plans/...
  └─ git commit -> cai em plan/{slug}
```

### O primitivo é `git worktree list --porcelain`, e `--git-common-dir` não serve

Medido, com um worktree criado por `git worktree add ../repo-demo -b plan/demo`:

| Comando | Do checkout principal | De dentro do worktree |
| --- | --- | --- |
| `git rev-parse --git-dir` | `.git` | `/repo/.git/worktrees/repo-demo` |
| `git rev-parse --git-common-dir` | `.git` | `/repo/.git` |
| `git rev-parse --show-toplevel` | `/repo` | `/repo-demo` |
| `git rev-parse --abbrev-ref HEAD` | `master` | `plan/demo` |

`--git-common-dir` responde uma pergunta diferente da que este spec tem. Comparado com `--git-dir`
ele diz **"estou dentro de um worktree vinculado?"**, e isolado ele diz **onde está o checkout
principal**. Do checkout principal os dois valores são idênticos — `.git` — então dali ele não
localiza worktree nenhum, que é justamente a direção em que a run começa. A pergunta deste spec é
*qual árvore tem `plan/{slug}` checada*, e só `git worktree list --porcelain` responde isso, dos dois
lados, com o mapeamento branch para caminho numa chamada.

Isso não é primitivo novo neste repo: `/specs:conclude` e o `git.md` já usam exatamente essa chamada
para achar quem tem a base checada (`commands/specs/conclude.md:292`,
`assets/references/specs-isolate/git.md:231`). O desenho reusa a chamada que já existe em vez de
introduzir uma segunda forma de detectar a mesma coisa.

**E o que qualquer detecção compra sobre a caminhada para cima?** Sobre ela, nada — porque ela não
está errada. `find_specs_root` acerta para a árvore em que está, medido nas duas direções. A detecção
compra a *escolha da árvore*, que hoje ninguém faz. É exatamente por isso que a correção não é no
resolvedor.

### São três estados, não dois

A mesma chamada distingue os três, e o terceiro foi encontrado no premortem:

| Estado no `--porcelain` | O que significa | O que a run faz |
| --- | --- | --- |
| `branch refs/heads/plan/{slug}` num caminho que existe | isolado numa árvore utilizável | opera nela |
| nenhuma linha casa o slug | não há worktree para este spec | segue na árvore atual — o comportamento de hoje |
| a entrada casa **e** traz `prunable ...` | isolamento obsoleto: o diretório foi apagado à mão e nunca podado | reporta, nomeia `git worktree prune`, **não** entra e **não** poda |

Tratar `prunable` como se fosse o primeiro estado é entrar num caminho inexistente; tratá-lo como o
segundo é operar na árvore errada em silêncio. Ele precisa ser lido, e é uma linha da saída que já
está em mãos. Medido: nesse estado `git checkout plan/{slug}` **ainda** falha com exit 128, então
"check it out" é conselho errado aqui por um terceiro motivo.

### O mecanismo de mover, e a asserção que o cobre

"Mover a run" só é um `cd` se o diretório de trabalho sobreviver de uma chamada de ferramenta para a
próxima. Isso **não é assumido**: é a primeira tarefa medir, e é uma entrada de `## Open Decisions`.
Independente do resultado, a seção compartilhada exige a mesma asserção barata — a run reafirma a
árvore antes da primeira escrita e antes do commit:

```
git rev-parse --show-toplevel      # tem de ser a árvore que tem plan/{slug}
```

Isso converte o pior modo de falha do desenho — escrever na árvore errada em silêncio — numa parada
alta, e vale tanto para a forma com um `cd` quanto para a forma que prefixa cada chamada.

Duas assimetrias deliberadas, escritas na seção compartilhada: mover **do checkout principal para um
worktree** é feito e anunciado; mover **entre dois worktrees** é recusado, com os dois caminhos
nomeados (`## Risks` #3).

### Correção antes de conveniência

A ordem de `## Tasks` carrega o argumento, e vem da crítica por caminho mais barato. Os 20% que
compram 80% são: `/specs:isolate` reportar o caminho, e cada comando do ciclo **parar** quando a
branch do spec vive numa árvore que não é o cwd. Isso entrega a correção inteira — nada aterrissa na
branch errada — e desiste só da conveniência de não digitar `cd`. Por isso o braço de recusa vem
**antes** da parte automática nas tarefas: se a automação for cortada depois, a correção fica.

### Onde a correção mora: nos corpos, mais uma seção de referência

`specs.py` não precisa de superfície nova. Ele já aceita `--root` e `$SPECS_ROOT`
(`assets/bin/specs.py:931-936`, e o epílogo §WORKSPACE RESOLUTION) — e `--root` é precisamente a
forma que o desenho **rejeita**, porque é a Alternativa A.

A regra é escrita **uma vez**, como seção nova de `assets/references/specs-isolate/git.md`: o arquivo
que já é dono de "como o trabalho de um spec é isolado" e que os comandos do ciclo já citam. Os
corpos ganham um passo que **cita**, nunca restata, seguindo
`docs/standards/architecture/plugin-layout.md`.

Uma exceção fica no lado da ferramenta, e é pequena. `_candidate`
(`assets/bin/specs.py:1895-1926`) calcula `on_it = live and work == current`, e `current` vem de
`_git_refs`, que roda `rev-parse --abbrev-ref HEAD` com cwd na raiz do workspace
(`assets/bin/specs.py:1865-1866, 1872-1881`). Uma branch viva num worktree ao lado sai como
`live: true, current: false`, e `_rank_reason` (`assets/bin/specs.py:1935`) devolve "check it out to
continue" — conselho que falha com exit 128. O payload precisa carregar **o caminho da árvore que tem
a branch** para que `commands/specs/continue.md:87-94` possa dizer "cd" em vez de "checkout". Custo:
uma chamada `git worktree list --porcelain` por run, não por spec, o que preserva a promessa de custo
do roteador (`commands/specs/continue.md:15-17`, "one `specs.py` call").

E aqui a exceção deixa de ser preferência e passa a ser a única saída: o `allowed-tools` de
`continue.md:4` é `Bash(python3:*), Bash(py:*), AskUserQuestion, Skill` — **sem `Bash` irrestrito**.
Aquele corpo não *pode* chamar `git`. Então o caminho da árvore só chega nele por dentro do payload de
`specs.py`, e "coloque a detecção no corpo" não é uma alternativa que exista para este comando.

### Contratos que o desenho não pode contrariar

- **Um commit por tarefa, carregando código e caixa juntos** — `plan-git-record.md` §The task→commit
  link is the commit's own subject.
- **`branch: {base, work}` é write-once, e o ref é o sinal, nunca o registro** —
  `assets/references/specs-isolate/git.md` §Recording the isolation. Este spec não escreve nem
  reescreve o registro; ele lê git.
- **`/specs:isolate` nunca faz merge; `/specs:conclude` nunca faz `git checkout {base}`** — mesmo
  arquivo, §Merge strategies. Intocado.
- **`worktreeSetup` roda uma vez, só na criação, com cwd dentro da árvore nova** —
  `docs/standards/workflows/worktree-setup.md` §Who runs it, and where. Mover o cwd de uma run
  posterior **não** autoriza rodar setup ali.
- **Nunca `context: fork` nestes comandos** — CLAUDE.md. Nada aqui pede contexto isolado, e a
  confirmação mid-flow de `/specs:isolate` continua sendo apresentada normalmente.
- **`commands/**` é a única árvore registrada** — `docs/standards/architecture/plugin-layout.md`, que
  é o motivo de a regra compartilhada morar em `assets/references/`.
## Alternatives Considered

Seis formas inteiras, cada uma escrita como seu melhor defensor a escreveria.

| Forma | O que custa | O que compra | O que fecha | Veredito |
| --- | --- | --- | --- | --- |
| **A** — plumbar `--root {worktree}/specs` em toda chamada, cwd intocado | uma flag em cada chamada de `specs.py` nos quatro corpos | a leitura correta do spec sem mexer em cwd | nada explicitamente | recusada |
| **B** — mover o cwd da run para o worktree | um passo novo em quatro corpos, mais uma seção de referência | resolução, `git status`, leitura, escrita e commit concordando; `find_specs_root` intocado | uma run que toque as duas árvores de propósito | **escolhida** |
| **C** — ensinar `find_specs_root` a detectar o worktree do slug | git dentro do resolvedor | todo chamador acertando sem mudar corpo nenhum | a caminhada para cima como resolução previsível | recusada |
| **D** — recusar quando a branch está checada em outra árvore | quase zero | a run nunca escrevendo na árvore errada | a automação | absorvida em B |
| **E** — não fazer nada | zero hoje | nada | nada | recusada |
| **F** — demover o worktree e voltar a recomendar branch simples | reverter uma decisão registrada | o problema deixando de existir, porque numa branch simples cwd e branch coincidem | o build paralelo de vários specs | recusada |

**A perdeu porque corrige o sintoma e deixa a causa.** Ela parte a run em duas árvores: as escritas
de seção iriam para o worktree e as escritas de código para o checkout principal, e o commit por
tarefa estagia os dois juntos (`commands/specs/execute.md:156-157`) — não existe commit possível.
É a leitura literal do `## Problem`, e é o motivo de o `## Problem` ter sido corrigido para a causa.

**C perdeu por camada errada.** `list`, `doctor`, `validate` e `plans reindex` não recebem slug
nenhum, então um resolvedor com chave de slug não tem o que responder para eles; e faria a resposta
do resolvedor depender de estado de git para *todo* chamador, invisivelmente. Também contraria o
epílogo do próprio script, que declara a resolução de workspace em três linhas legíveis.

**D não foi recusada, foi absorvida** — é o braço de fallback de B, para quando mover é impossível, e
`commands/specs/execute.md:72-73` já tem metade dela ("say so and stop"). Sozinha, deixa o caminho
que o repo recomenda exigindo um `cd` manual que documento nenhum menciona.

**E perdeu porque o custo de não fazer nada não é zero.** É um commit na branch errada no caminho que
o repo recomenda **incondicionalmente** (`assets/references/specs-isolate/git.md:96-108`), e um erro
silencioso no default é o pior lugar possível para deixá-lo.

**F perdeu porque joga fora a capacidade para evitar a correção.** Fica registrada porque é o inverso
honesto deste spec: se uma decisão futura demover o worktree, este spec encolhe para o braço D
sozinho. Isso está em `## Open Decisions`.

## Open Decisions

- **O cwd de uma run sobrevive entre chamadas de ferramenta?** Decide se o desenho é B com um único
  `cd`, ou B implementado prefixando cada chamada. **Como se decide:** medir numa sessão real — `cd`
  numa chamada, `pwd` na seguinte — **antes** da primeira tarefa que edita corpo. É por isso que essa
  medição é a primeira tarefa de `## Tasks` e não uma suposição do `## Design`.
- **Mover entre worktrees: recusar ou confirmar?** `## Risks` #3 recusa. **Como se decide:** fica
  recusado até alguém pedir. Recusar é reversível; confirmar não desfaz uma escrita já feita, e o
  custo de errar é assimétrico.
- **A tarefa de `/specs:continue` fica neste spec ou migra para os irmãos de `specs.py`?** É o único
  pedaço que altera `specs.py`, e é read-only. **Como se decide:** se `dedupe-specs-py-spec-reader` ou
  `add-specs-py-record-writer` for aprovado antes deste, a tarefa migra para lá; caso contrário fica.
  Ela está isolada na última seção de `## Tasks` exatamente para poder migrar sem tocar no resto.
- **A recomendação incondicional de worktree continua?** Este spec inteiro pressupõe que sim
  (`assets/references/specs-isolate/git.md:96-108`). Se uma decisão futura demover o worktree — a
  Alternativa F — este spec encolhe para o braço D sozinho. **Como se decide:** não é deste spec para
  decidir; fica registrado como a suposição que o sustenta.
- **As pessoas realmente usam worktree?** Ninguém mediu, e o spec irmão `align-in-worktree-then-merge`
  registra a mesma lacuna para a frente dele. Não bloqueia: diferente de uma capacidade nova, este é
  conserto de correção num caminho que o repo recomenda incondicionalmente, então vale enquanto a
  recomendação existir. **Como se decide:** aceitar que uma recomendação incondicional merece estar
  correta, ou contar `git worktree list` em uso real antes de investir na parte automática (o braço D
  já entrega a correção sem ela).

## Risks

Resultado do premortem — oito histórias, cada uma com quão provável, quão grave e **como seria
detectada**, convertidas em mitigação, risco aceito ou corte de escopo.

1. **Árvore sem dependências instaladas.** A run entra num worktree onde o `worktreeSetup` falhou ou
   nunca existiu, e todo `verify:` falha. Provável (um worktree carrega só o que git rastreia,
   `assets/references/specs-isolate/git.md:96-108`), gravidade média. **Detecção:** o primeiro
   `verify:` falha alto — mas é *mal atribuído*, lido como "o spec está quebrado" em vez de "a árvore
   não está provisionada", e é isso que faz dele risco. **Mitigação:** ao mover, a run anuncia o
   caminho da árvore em uma linha, então um `verify:` que falha tem a árvore no transcript.

2. **Worktree apagado à mão e nunca podado.** Medido: `git worktree list --porcelain` continua
   listando o caminho, agora com a linha `prunable gitdir file points to non-existent location`. Uma
   run que confie na listagem entraria num caminho que não existe. Média, gravidade média.
   **Detecção:** o `cd` falha. **Mitigação:** a linha `prunable` é lida como **terceiro estado**, não
   ignorada — a run reporta isolamento obsoleto, nomeia `git worktree prune`, e nunca segue o
   caminho. Medido também que `git checkout` continua falhando com exit 128 nesse estado, então
   "check it out" seria conselho errado aqui de um terceiro jeito.

3. **Mover de um worktree para outro.** A pessoa roda o comando de dentro do worktree do spec A
   pedindo o spec B. Improvável, gravidade alta — parece ter funcionado. **Detecção:** nenhuma
   automática. **Mitigação:** mover **do checkout principal para um worktree** é feito e anunciado;
   mover **entre worktrees** é recusado, nomeando os dois caminhos. A assimetria é deliberada e fica
   escrita na seção compartilhada.

4. **Meia aterrissagem.** A seção compartilhada é escrita e só parte dos corpos passa a citá-la, então
   metade do ciclo opera numa árvore e metade na outra — pior que tudo velho. Média: neste repo os
   corpos são editados um por commit. **Detecção:** nenhum checker vê. **Mitigação:** ordem das
   tarefas (contrato compartilhado primeiro, corpos em seguida) mais o `grep` em `## Validation` que
   exige que todo corpo do ciclo cite a seção.

5. **O cwd não persistir entre chamadas de ferramenta.** "Mover a run" só é implementável como um
   `cd` se o diretório de trabalho sobreviver de uma chamada para a próxima. Média, gravidade alta:
   se não sobrevive, o desenho volta a precisar de `--root` ou `git -C` em cada chamada, que é a
   Alternativa A que este spec recusou. **Detecção:** silenciosa — o pior caso. **Mitigação:** a seção
   compartilhada declara o mecanismo **e** exige que a run reafirme a árvore com
   `git rev-parse --show-toplevel` antes da primeira escrita e antes do commit. É barato e converte
   escrita silenciosa na árvore errada em parada alta. Também está em `## Open Decisions`.

6. **Conflito com os specs irmãos de `specs.py`.** O campo novo no payload de `_candidate` encosta em
   `dedupe-specs-py-spec-reader`, `add-specs-py-record-writer` e `split-specs-py-backlog-renderer`,
   todos em desenvolvimento em paralelo agora. Média-alta, gravidade baixa. **Detecção:** conflito de
   merge, alto. **Mitigação:** a mudança em `specs.py` é aditiva — um campo no dicionário devolvido,
   nenhuma assinatura alterada — e é a **última** tarefa, então quem chegar depois rebaseia sobre uma
   diff pequena.

7. **ACCEPTED — a invariante não é checável mecanicamente.** "A run opera na árvore que tem a branch
   do spec" não é vista por `skills.py lint`, por `okf-validate.py` nem por `functional-checks.sh`, e
   o registro de comandos é montado no início da sessão, então mudança em `commands/**` não é testável
   na sessão que a escreve (CLAUDE.md). Aceito porque é a mesma condição de toda regra de corpo de
   comando neste repo; o que compensa é a asserção do risco 5, verificável em tempo de run.

8. **ACCEPTED — nome de branch fora do default falha aberto.** A detecção casa `plan/{slug}`, ou o
   `work` do registro `branch:` via `_work_ref` (`assets/bin/specs.py:1884-1892`). Uma branch cortada
   à mão com outro nome e sem registro não casa com nada. Aceito porque não casar significa "não
   existe worktree para este spec", que é exatamente o comportamento de hoje: o fallback é o status
   quo, nunca a árvore errada.

## Tasks

A ordem carrega o argumento: medir antes de supor, contrato compartilhado antes dos corpos, o braço de
recusa antes da automação (`## Design` §Correção antes de conveniência), e o pedaço que pode migrar
para outro spec por último.

### 1. Medir antes de desenhar

- [ ] 1.1 Medir se o cwd de uma run sobrevive entre chamadas de ferramenta: `cd` numa chamada, `pwd`
      na seguinte, numa sessão real. Registrar o resultado como uma linha em `## Design` e resolver a
      primeira entrada de `## Open Decisions`. Se não sobreviver, a tarefa 4.1 muda de forma (prefixar
      cada chamada) sem mudar nenhuma outra tarefa.
      verify: o resultado está escrito no spec e a entrada de `## Open Decisions` está resolvida

### 2. O contrato compartilhado, dono único da regra

- [ ] 2.1 Escrever a seção "The tree a run operates in" em `assets/references/specs-isolate/git.md`:
      os três estados do `git worktree list --porcelain` (utilizável, ausente, `prunable`), a
      assimetria entre entrar num worktree e mover entre dois, a asserção de
      `git rev-parse --show-toplevel`, e a declaração explícita de que mover o cwd NÃO autoriza rodar
      `worktreeSetup` de novo.
      files: plugins/quenching/assets/references/specs-isolate/git.md
      pattern: plugins/quenching/assets/references/specs-isolate/git.md
      verify: a seção existe, aparece no índice de Contents do arquivo, e não restata nada que os
      corpos já digam

### 3. O braço de recusa — a correção, sem automação nenhuma

- [ ] 3.1 `/specs:isolate` passa a reportar o caminho da árvore como fato explícito da saída, para o
      worktree que acabou de criar e para um que já existia (passos 5 e 7).
      files: plugins/quenching/commands/specs/isolate.md
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json
- [ ] 3.2 `/specs:isolate` commita o arquivo do spec na árvore onde `plan/{slug}` está checada, não no
      checkout de onde a run partiu — corrigindo a promessa de `isolate.md:139-141` ("so the base is
      left exactly as it was"), que hoje commita na base.
      files: plugins/quenching/commands/specs/isolate.md
      verify: o passo cita a seção de 2.1 e nenhum `git add` do corpo roda sem árvore resolvida
- [ ] 3.3 [P] `/specs:execute` resolve a árvore no passo 2 e **para** quando a branch do spec vive numa
      árvore que não é o cwd, nomeando o caminho — em vez de seguir e escrever na árvore errada.
      files: plugins/quenching/commands/specs/execute.md
      verify: grep -c 'specs-isolate/git.md' plugins/quenching/commands/specs/execute.md
- [ ] 3.4 [P] `/specs:develop` faz a mesma resolução antes da primeira escrita de seção ou de
      frontmatter, e para pelo mesmo critério.
      files: plugins/quenching/commands/specs/develop.md
      verify: grep -c 'specs-isolate/git.md' plugins/quenching/commands/specs/develop.md

### 4. A parte automática, que pode ser cortada sem perder a correção

- [ ] 4.1 Os comandos do ciclo passam a **operar dentro** da árvore resolvida, com a asserção de
      `git rev-parse --show-toplevel` antes da primeira escrita e antes do commit, e o anúncio em uma
      linha do caminho da árvore (mitigação de `## Risks` #1). Mover entre dois worktrees é recusado.
      files: plugins/quenching/commands/specs/isolate.md, plugins/quenching/commands/specs/execute.md, plugins/quenching/commands/specs/develop.md
      verify: cada corpo tocado carrega a asserção, e a recusa entre worktrees está escrita

### 5. O roteador — isolado de propósito, para poder migrar

- [ ] 5.1 `specs.py`: `_candidate` passa a carregar o caminho da árvore que tem a branch do spec, e o
      estado `prunable`, lidos de UMA chamada `git worktree list --porcelain` por run e nunca por
      spec. Aditivo: um campo no dicionário devolvido, nenhuma assinatura alterada.
      files: plugins/quenching/assets/bin/specs.py
      pattern: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py selftest
- [ ] 5.2 `/specs:continue`: a tabela de `branch` em `:87-94` para de mandar `git checkout` numa branch
      que um worktree ocupa e passa a nomear o caminho, mais o terceiro estado com
      `git worktree prune`. O corpo lê o campo do payload e **não** chama git — ele não tem `Bash`
      irrestrito em `allowed-tools`, o que é exatamente por que o fato vem da ferramenta.
      files: plugins/quenching/commands/specs/continue.md
      verify: grep -c 'specs-isolate/git.md' plugins/quenching/commands/specs/continue.md

### 6. O standard que a mudança prova

- [ ] 6.1 Escrever `docs/standards/workflows/worktree-run-tree.md` (`authority: current`, porque o spec
      prova a regra ao construí-la), via o procedimento de insert de `docs-add/homes.md`, e regenerar
      a zona GENERATED de `docs/standards/index.md`.
      files: docs/standards/workflows/worktree-run-tree.md, docs/standards/index.md
      pattern: docs/standards/workflows/worktree-setup.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs

### 7. Verificação

- [ ] 7.1 Rodar os checks permanentes e as asserções desta mudança, na ordem de `## Validation`,
      incluindo o `grep -l` que tem de imprimir 4 e o exercício de `specs.py` num workspace
      descartável cobrindo os três estados. Registrar no relatório que as quatro edições de corpo
      ficaram como verificação manual declarada, porque o registro de comandos é montado no início da
      sessão.
      verify: todos os comandos de `## Validation` §O que os checks permanentes provam e §O que prova
      esta mudança em particular saem no valor esperado
