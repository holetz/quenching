---
slug: move-conclude-merge-last
title: Make the merge the last action of /specs:conclude
verification: per-section
refined: {mode: gate, date: 2026-07-28}
approved: {date: 2026-07-28}
branch: {base: main, work: plan/move-conclude-merge-last}
---

# Make the merge the last action of /specs:conclude

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

## Problem

Os registros que ligam uma spec ao git são gravados **depois** do commit que
descrevem, e isso força escrita fora do lugar em dois pontos.

Em `/specs:conclude`, a passada de destilação OKF (passo 6) roda **depois** do
merge, então os docs destilados caem direto na base. O fechamento de
`instrument-and-extend-skill-front` mostra o efeito: `4421185` mergeia,
`a597368` grava o merge, `a3ababe` destila — dois commits na `main` depois que
a branch já tinha entrado. Os docs emergentes (passo 3) e o arquivamento
(passo 4) já commitam na branch; o vazamento é o passo 6.

O que impede mover o passo 6 para antes do merge é o próprio registro
`merge: {strategy, commit}`: o sha do merge só existe depois do merge. Pelo
mesmo motivo, cada task de `/specs:execute` precisa de um commit de
bookkeeping — a caixa só pode ser marcada depois que o commit da task existe.

Nos dois casos a causa é a mesma: o arquivo aponta para um commit que ainda
não existe.

Um terceiro ponto tem a mesma origem em git, com causa diferente. Isolamento só
existe em `/specs:execute`: é lá que a branch é criada e o registro
`branch: {base, work}` é gravado. Mas criar e desenvolver uma spec também
escrevem em `plans/` e sujam a worktree, e às vezes a spec deveria nascer dentro
da própria branch — não há como pedir isolamento antes de executar. E
`/specs:continue` ranqueia sem olhar para git: uma spec que já tem branch aberta
aparece como candidata igual às outras, mesmo já estando em andamento.
## Proposal

Inverter a direção do vínculo: gravar o **subject** da mensagem do commit
(conhecido antes) em vez do sha (conhecido depois). Todo registro passa a ser
escrito antes do commit que ele descreve, e nada sobra para depois. E extrair a
**ação** de git para um comando próprio, de modo que isolamento deixe de ser
privilégio da execução.

Três consequências, uma por comando:

1. **`/specs:conclude`** — a passada de destilação roda na branch de trabalho,
   logo após o arquivamento, e o `merge: {strategy, subject}` é gravado ali. O
   merge passa a ser a última ação do comando, sem exceção.
2. **`/specs:execute`** — a task é marcada antes do commit e entra nele, então
   cada task é exatamente um commit contendo código e caixa marcada. Os commits
   de bookkeeping deixam de existir.
3. **`/specs:isolate`** — um comando novo, invocável pelo humano, que toma ou
   reporta isolamento para UMA spec em qualquer estágio: criação,
   desenvolvimento ou execução. `/specs:execute` passa a delegar a ele em vez de
   reimplementar; `create` e `develop` encaminham. O merge continua dentro de
   `conclude`, onde ficam os portões de review e arquivamento.

O que passa a ser verdade e hoje não é:

- Concluir uma spec produz **um único merge**, que carrega o código, os docs
  emergentes, os docs destilados e a spec arquivada. Reverter o merge reverte a
  pegada inteira da spec.
- Nenhum commit é criado na branch base depois do merge.
- Um subject sobrevive a um rebase, então o vínculo task→commit deixa de morrer
  justamente na estratégia que hoje o destrói.
- Isolar uma spec deixa de exigir `execute`: dá para pedir a branch na criação,
  no desenvolvimento, ou nunca.
- `/specs:continue` deixa de oferecer o que já está em andamento em outra
  branch, e devolve direto a spec da branch em que você está.
## Out of Scope

- Converter specs já arquivadas que carregam `commit: <sha>`. Um sha gravado
  não está errado — descreve um commit que existe — e reescrever o arquivo
  contraria o invariante do próprio `conclude` de nunca editar nada em
  `archive/`. As duas formas coexistem: linha antiga resolve por sha, linha
  nova por `git log --grep`. Nenhum backfill, nunca.
- Fundir os passos 3 e 6 de `conclude` numa única passada de `docs/` (a
  alternativa C). Continua disponível depois; ver `## Alternatives Considered`.
- O caminho `--outcome abandoned`. Não há merge, então a reordenação não muda
  nada ali; o comportamento fica idêntico.
- As quatro estratégias de merge e a ressalva do squash. O menu não muda — só
  muda o que é gravado sobre a escolha.
- As convenções de commit do repositório alvo. `docs/standards/git/**`
  continua read-if-present, nunca instalado e nunca inferido.
- Expor o merge como comando próprio (`/specs:merge`). Um merge invocável fora
  de `conclude` pode rodar sobre spec não revisada nem arquivada, contornando os
  portões; precisaria duplicar as recusas do `conclude`.
- Emendar `docs/standards/naming/command-surface.md` §Verb-first para permitir
  um `/specs:git`. O nome é substantivo puro e a norma proíbe; a spec se ajusta
  à norma em vez de discutir política de nomes.
- Forçar isolamento em `create` ou `develop`. O fluxo atual continua válido;
  isolamento segue opcional e nunca imposto.
## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/workflows/plan-git-record.md` — reescrita: o vínculo passa a
  ser inscrito na mensagem, os dois registros mudam de forma, e a tabela do
  squash muda de consequência
- `docs/standards/workflows/plan-lifecycle.md` — a linha do vocabulário de
  registros: `merge: {strategy, commit}` → `{strategy, subject}`
- `docs/standards/workflows/task-execution.md` — a citação nominal à seção
  renomeada, e §One commit per task, que passa a ser literalmente verdadeira

### Standards at `authority: background` this spec may resolve

- none — nenhum standard em `background` toca este assunto.

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/specs.py` — `task --check --subject`, o registro
  `merge`, o ranking de `next --front`, e as constantes de template em lockstep
- `plugins/quenching/commands/specs/isolate.md` — novo
- `plugins/quenching/commands/specs/{execute,conclude,continue,create,develop}.md`
- `plugins/quenching/assets/references/specs-isolate/git.md` — movido de
  `specs-execute/`, e reescrito
- `plugins/quenching/assets/references/specs-execute/execution.md`,
  `specs-conclude/distill.md`, `specs-develop/{artifacts,spec-driven}.md`
- `plugins/quenching/assets/specs/{templates/spec.md,plans/index.md,QUENCHING.md}`
- `plugins/quenching/assets/bin/conclude-order-check.sh` — novo
- `CLAUDE.md`, `plugins/quenching/README.md`, e os três `QUENCHING.md`

## Validation

Checagens mecânicas, a partir de `plugins/quenching/`:

    python3 assets/bin/specs.py --version                  # lockstep com VERSION
    python3 assets/hooks/okf-validate.py assets/docs
    python3 assets/bin/skills.py --root . doctor --json    # 25 comandos, sem findings
    python3 assets/bin/skills.py --root . lint --json
    python3 assets/bin/specs.py validate
    ./assets/bin/functional-checks.sh   # OBRIGATÓRIO: commands/** e caminhos de citação mudaram

Nenhuma delas enxerga a afirmação central — que nada é escrito depois do merge.
Isso é uma propriedade de ordem, e só uma execução real a observa:

    ./assets/bin/conclude-order-check.sh

Repositório git descartável onde uma spec é criada, uma task é executada e a
spec é concluída. Três asserções:

1. `git rev-parse HEAD` na base **é** o commit de merge — nada o segue.
2. `git show --stat <sha-da-task>` lista **o arquivo de código e o arquivo da
   spec** — a marcação entrou no commit da própria task.
3. `git log --grep=<subject> --fixed-strings` devolve **exatamente um** commit
   para cada task marcada.

Invariantes que devem continuar valendo: nenhum `--amend`, nenhum force-push,
nenhum `--no-verify`; `archive/**` intocado.

## Design

### O subject como âncora

Default, na mesma gramática que `execute` já escreve
(`plan/<slug>: <id> <title>`, `plan/<slug>: record …`):

| Registro | Antes | Depois |
| --- | --- | --- |
| merge | `merge: {strategy, commit: <sha>}` | `merge: {strategy, subject: "plan/<slug>: merge (<strategy>)"}` |
| task | `— commit: abc1234` | `— subject: plan/<slug>: 3.2 Validate the token` |

`conclude` e `execute` são os autores das duas mensagens, então podem garantir
o subject que acabaram de gravar. Quando o repositório alvo declara convenção
própria em `docs/standards/git/**`, o subject gravado é o que a convenção
produziu — o registro acompanha, não impõe.

### Quando não existe commit para ancorar

`fast-forward` e `rebase` não criam commit de merge. Nesses casos o registro é
um explicit none:

    merge:
      strategy: fast-forward
      subject: none — fast-forward não cria commit de merge; os commits da
        branch SÃO o histórico da base

Sob fast-forward os shas das tasks já estão na base e resolvem direto, então um
ponteiro não acrescentaria nada.

### Como o subject é resolvido

`git log --grep=<subject> --fixed-strings` — casamento por substring. Quase todo
hook `commit-msg` real **acrescenta** ao subject (prefixo de ticket, `Change-Id`
como trailer, sign-off), e nesses casos o subject gravado sobrevive como
substring e continua achando exatamente um commit. Só um hook que **substitui**
o subject inteiro quebra o vínculo; isso está em `## Risks`.

### A nova ordem de `conclude`

    hoje                          depois
    2 review          (branch)    2 review          (branch)
    3 docs emergentes (branch)    3 docs emergentes (branch)
    4 Outcome+archive (branch)    4 Outcome+archive (branch)
    5 merge           (base)      5 destilação      (branch)
      merge: stamp    (base)        merge: stamp    (branch)
    6 destilação      (base)      6 merge           (base)  ← última ação

### `/specs:isolate` — isolamento em qualquer estágio

Verb-first, conforme `docs/standards/naming/command-surface.md` §Verb-first.
Owns: criar branch ou worktree, gravar `branch: {base, work}`, e mover para a
branch nova uma spec já escrita em `plans/` (o caso "a spec nasce na própria
branch"). `execute` delega; `create` e `develop` encaminham quando pedido.

O conhecimento de git já estava centralizado em
`assets/references/specs-execute/git.md` — o que não estava extraído era a
**ação**. A referência muda de dono para `specs-isolate/git.md` e passa a ser
citada por `isolate`, `execute` e `conclude`.

### O sinal de "já está em andamento"

Em `specs.py next --front`, o único lugar onde mora lógica de ranking:

| Situação | Posição | Razão na linha |
| --- | --- | --- |
| ref `plan/<slug>` viva e é a branch atual | topo | "você está nesta branch" |
| ref viva, não conferida | rebaixada | "em andamento em `plan/<slug>`" |
| sem ref viva | como hoje | prioridade, estágio, idade |
| humano nomeou o slug | ranking ignorado | `next --spec` nunca consulta `--front` |

O sinal é a **ref viva**, não o registro `branch:` — o humano pode ter cortado a
branch à mão, sem registro nenhum. Com registro, vale `branch:.work`; sem
registro, o padrão `plan/<slug>`. Registro cujo ref sumiu deixa de contar.

### O que isto obriga a reescrever

`docs/standards/workflows/plan-git-record.md` §"The task→commit link is stored,
never inscribed" argumenta exatamente o contrário desta spec e precisa ser
reescrito junto, com `plan-lifecycle.md` e `task-execution.md`. A declaração
formal está em `## Impact`.
## Alternatives Considered

### A forma da correção

| | Abordagem | Custo | Ganho | O que fecha |
| --- | --- | --- | --- | --- |
| **A** *(escolhida)* | Reordenar: destilação na branch, merge por último | ordem em `conclude.md`; coluna "where it lands" de `distill.md` §Two moments | um merge carrega a pegada inteira da spec | nada — C continua disponível |
| C | Fundir passos 3 e 6 numa única passada de `docs/` | reescrita maior; §Two moments desaparece | uma confirmação em vez de duas | a separação de entradas: emergente vem da review, destilação vem da spec arquivada |
| D | Não fazer nada | zero | mantém a justificativa registrada em `distill.md` | o encapsulamento pedido |

A justificativa de `distill.md` para destilar depois do merge — "cheapest to
harvest once the spec is **closed**" — não sobrevive: a spec é fechada no passo
4, na branch. Fechar e mergear foram confundidos.

### O registro do merge

| Opção | Por que perdeu |
| --- | --- |
| Aceitar um commit de bookkeeping na base gravando `{strategy, commit}` | honesto, mas mantém escrita depois do merge — o título vira "quase por último" |
| Remover o campo `commit` do registro | compra pureza e custa um fato que `plan-git-record.md` chama de underivable |
| **Gravar o subject** *(escolhida)* | conhecido antes do merge, então nada sobra para depois; ainda resolve por `git log --grep` |

Manter o carimbo pós-merge do sha só para `fast-forward` e `rebase` também foi
considerado: reintroduz escrita pós-merge em dois caminhos e derruba o ponto
inteiro da spec.

### O comando de git

| Opção | Por que perdeu |
| --- | --- |
| `/specs:isolate` + `/specs:merge` | merge invocável fora de `conclude` roda sobre spec não revisada nem arquivada; precisaria duplicar as recusas |
| Um comando só, isolate + merge | exige o nome `/specs:git`, proibido por §Verb-first, ou emendar a norma — política de nomes em cima de três mudanças |
| **`/specs:isolate`** *(escolhida)* | um verbo, uma ação; o merge fica onde estão seus portões |

Não existe um verbo único que cubra "tomar isolamento" e "mergear" — o que é
evidência de que são duas ações, não uma.

### O sinal usado por `continue`

Ler git dentro de `continue` em vez de `specs.py` foi considerado e rejeitado:
quebra "ranking mora em um lugar só" e transforma um comando de uma chamada em
dois. `specs.py` já executa git (`_git_first_commit_date`), então não é
dependência nova.

### Uma spec ou duas

Separar a inversão do vínculo das tasks numa spec própria foi considerado. Uma
spec só venceu porque as duas metades compartilham um mecanismo (gravar antes,
não depois) e um ganho (nada é escrito depois daquilo que descreve); separar
deixaria `execute` em sha e `conclude` em subject por tempo indefinido. O
terceiro eixo — o comando de git — entrou depois, por decisão explícita de
atacar tudo na mesma spec: compartilha o tema (como a frente lida com git), não
o mecanismo. O slug `move-conclude-merge-last` fica subdimensionado, e isso é
aceito — specs não são renomeadas.

## Open Decisions

- **`create` e `develop` devem oferecer isolamento ativamente, ou só encaminhar
  quando pedido?** Um prompt novo nos dois comandos mais rodados custa atrito em
  todo mundo para servir a minoria que quer isolar cedo. Decide-se **depois de
  `/specs:isolate` existir**, com o comando em mão: se o encaminhamento sob
  demanda se mostrar desconfortável em uso real, vira oferta. Até lá, só
  encaminhamento.

## Risks

- **Hook `commit-msg` que substitui o subject inteiro.** O subject gravado deixa
  de casar e o vínculo task→commit morre. Mitigação: resolução por substring
  (`--fixed-strings`), que sobrevive a todo hook que apenas acrescenta; e uma
  asserção pós-commit em `execute` comparando `git log -1 --format=%s` com o
  gravado, **reportada como finding, sem escrita** — o invariante "nada depois do
  commit" continua válido. ACCEPTED — substituição integral do subject é rara e
  patológica, e o custo fica declarado em `plan-git-record.md`.
- **Colisão de subject.** O default `plan/<slug>: <id> <title>` carrega slug e
  id, e duas specs não compartilham slug, então a colisão exige a mesma task
  commitada duas vezes. Mitigação: `conclude-order-check.sh` assere match único.
  ACCEPTED — o caso restante é revert-e-refaz.
- **Raio de alcance grande para uma spec só.** Três eixos, ~20 arquivos, um
  comando novo. Mitigação: `## Tasks` em seis seções ordenadas por dependência,
  com `verification: per-section`, então cada seção é verificada antes da
  seguinte; nenhuma task toca `archive/**`.
- **Citações quebradas pela mudança de dono da referência.** Mover
  `specs-execute/git.md` para `specs-isolate/` invalida toda citação por caminho
  absoluto. Mitigação: `functional-checks.sh` é a única checagem que pega isso, e
  tem task própria.
- **Specs arquivadas ficam com `commit:` e as novas com `subject:`.** Mitigação:
  coexistência deliberada declarada em `## Out of Scope`, e `plan-git-record.md`
  passa a dizer qual era produziu qual forma.

## Handoff

- Repositório sem suíte de testes: verificação é `specs.py` / `skills.py` /
  `okf-validate.py`, `functional-checks.sh` e o novo `conclude-order-check.sh`.
- `commands/**` é a única árvore registrada pelo Claude Code — nada que não seja
  entry point vive lá. Procedimento compartilhado vai em `assets/references/`.
- Lockstep: `VERSION`, `plugin.json`, `marketplace.json` e a constante `VERSION`
  nos três scripts. Os templates são duplicados como constantes em `specs.py` e
  mudam junto com `assets/specs/templates/`.
- Nunca adicionar `context: fork` a estes comandos; nunca rebaixar os
  sub-agentes de `/docs:import-memory` para haiku.
- Prosa em pt-BR nesta spec; headings, caminhos e chaves em inglês canônico.
- `archive/**` é intocável.

## Tasks

### 1. As rails em `specs.py`

- [x] 1.1 `task --check` aceita `--subject` no lugar de `--commit`, escrevendo `subject:` na linha da task; linhas antigas com `commit:` continuam sendo lidas
      files: plugins/quenching/assets/bin/specs.py
      verify: workspace descartável — `specs.py new x` → `task --check 1.1 --subject "..."` → `status --spec x --json` mostra o subject
      subject: plan/move-conclude-merge-last: 1.1 task --check accepts --subject in place of --commit
- [x] 1.2 O registro `merge` aceita `{strategy, subject}`, incluindo a forma explicit-none de `fast-forward`/`rebase`; `status` e `validate` reportam
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 assets/bin/specs.py validate
      subject: plan/move-conclude-merge-last: 1.2 the merge record carries {strategy, subject}
- [x] 1.3 `next --front` fica ciente de branch conforme `## Design` §O sinal de "já está em andamento"
      files: plugins/quenching/assets/bin/specs.py
      verify: workspace descartável com duas specs, uma com `plan/<slug>` viva
      subject: plan/move-conclude-merge-last: 1.3 next --front ranks on the live plan/<slug> ref
- [x] 1.4 Atualizar os templates e as constantes duplicadas em `specs.py` em lockstep
      files: plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/specs/templates/spec.md, plugins/quenching/assets/specs/plans/index.md
      verify: python3 assets/hooks/okf-validate.py assets/specs/plans --listing-root
      subject: plan/move-conclude-merge-last: 1.4 templates and duplicated constants in lockstep

### 2. O comando `/specs:isolate`

- [ ] 2.1 Mover `assets/references/specs-execute/git.md` para `assets/references/specs-isolate/git.md` e reescrever: âncora por subject, isolamento em qualquer estágio, defaults de branch, estratégias de merge, ressalva do squash, regra read-if-present
      files: plugins/quenching/assets/references/specs-isolate/git.md
- [ ] 2.2 Escrever `commands/specs/isolate.md` — verb-first; toma ou reporta isolamento para UMA spec em qualquer estágio, grava `branch: {base, work}`, move para a branch uma spec já escrita em `plans/`
      files: plugins/quenching/commands/specs/isolate.md
      verify: python3 assets/bin/skills.py --root . lint --json
- [ ] 2.3 Corrigir toda citação por caminho absoluto à referência movida
      verify: ./assets/bin/functional-checks.sh

### 3. Os comandos existentes

- [ ] 3.1 `execute.md`: delegar isolamento a `/specs:isolate`; marcar a caixa antes do commit para que ela entre nele; asserção pós-commit comparando o subject real com o gravado, reportada como finding
      files: plugins/quenching/commands/specs/execute.md
- [ ] 3.2 `conclude.md`: destilação passa para a branch, antes do merge; `merge: {strategy, subject}` gravado na branch; merge vira a última ação
      files: plugins/quenching/commands/specs/conclude.md
- [ ] 3.3 `continue.md`: refletir o ranking ciente de branch na descrição e no corpo
      files: plugins/quenching/commands/specs/continue.md
- [ ] 3.4 `create.md` e `develop.md`: encaminhar para `/specs:isolate` quando pedido, sem oferta ativa (ver `## Open Decisions`)
      files: plugins/quenching/commands/specs/create.md, plugins/quenching/commands/specs/develop.md
- [ ] 3.5 Rodar as checagens da superfície
      verify: python3 assets/bin/skills.py --root . doctor --json && ./assets/bin/functional-checks.sh

### 4. As referências

- [ ] 4.1 [P] `specs-conclude/distill.md` §Two moments: os dois momentos passam a cair na branch
      files: plugins/quenching/assets/references/specs-conclude/distill.md
- [ ] 4.2 [P] `specs-execute/execution.md`: a marcação entra no commit da task; commits de bookkeeping deixam de existir
      files: plugins/quenching/assets/references/specs-execute/execution.md
- [ ] 4.3 [P] `specs-develop/artifacts.md`: a linha `commit:` da tabela de metadados vira `subject:`
      files: plugins/quenching/assets/references/specs-develop/artifacts.md
- [ ] 4.4 [P] `specs-develop/spec-driven.md`: o vocabulário de registros
      files: plugins/quenching/assets/references/specs-develop/spec-driven.md

### 5. Os standards e o glossário

- [ ] 5.1 Reescrever docs/standards/workflows/plan-git-record.md — o vínculo é inscrito na mensagem; renomear a seção "The task→commit link is stored, never inscribed"; os dois registros; a tabela do squash; a coexistência das duas formas no arquivo (authority: current)
      files: docs/standards/workflows/plan-git-record.md
- [ ] 5.2 Atualizar docs/standards/workflows/plan-lifecycle.md — a linha `merge: {strategy, subject}`
      files: docs/standards/workflows/plan-lifecycle.md
- [ ] 5.3 Atualizar docs/standards/workflows/task-execution.md — a citação nominal à seção renomeada e §One commit per task
      files: docs/standards/workflows/task-execution.md
- [ ] 5.4 Redefinir "Commit record" no glossário via `/docs:define`
      files: docs/knowledge/glossary.md
- [ ] 5.5 Verificar o bundle
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs

### 6. A verificação e a superfície

- [ ] 6.1 Escrever `assets/bin/conclude-order-check.sh` com as três asserções de `## Validation`
      files: plugins/quenching/assets/bin/conclude-order-check.sh
      pattern: plugins/quenching/assets/bin/functional-checks.sh
      verify: ./assets/bin/conclude-order-check.sh
- [ ] 6.2 Atualizar os três `QUENCHING.md`, `CLAUDE.md` e `plugins/quenching/README.md` para o comando novo e a contagem
      files: plugins/quenching/assets/docs/QUENCHING.md, plugins/quenching/assets/specs/QUENCHING.md, plugins/quenching/assets/claude/QUENCHING.md, CLAUDE.md, plugins/quenching/README.md
- [ ] 6.3 Bump em lockstep: `VERSION`, `plugin.json`, `marketplace.json` e a constante `VERSION` nos três scripts
      files: plugins/quenching/VERSION, plugins/quenching/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/bin/skills.py, plugins/quenching/assets/hooks/okf-validate.py
- [ ] 6.4 Rodar a suíte inteira de `## Validation`
      verify: ./assets/bin/functional-checks.sh && ./assets/bin/conclude-order-check.sh

## Discoveries

- docs/standards/naming/command-surface.md §Namespaces still names a root '/align-and-update' that the specs-flow-consolidation spec removed — stale, unrelated to this spec
- task 1.2 had to touch assets/specs/schema.json, which no task declares under files: — schema.json shadows the DEFAULT_SCHEMA constant via load_schema(), so the record vocabulary is a THIRD lockstep copy alongside specs.py and the templates
