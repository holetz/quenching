---
slug: prefer-worktree-isolation
title: Prefer worktrees for spec isolation and remove them after a successful merge
verification: per-section
priority: {level: 20, criticality: medium, date: 2026-07-28}
branch: {base: main, work: plan/prefer-worktree-isolation}
refined: {mode: gate, date: 2026-07-28}
approved: {date: 2026-07-28}
reviewed: {date: 2026-07-29}
---

# Prefer worktrees for spec isolation and remove them after a successful merge

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

Duas coisas a ajustar na isolação de uma spec, ambas sobre worktree.

A primeira: `/specs:isolate` oferece branch **ou** worktree, e hoje a branch é o
caminho de menor atrito — o worktree é a alternativa que só aparece quando
alguém pede. Deveria ser o contrário: uma spec construída num worktree deixa o
repositório principal intocado, o que permite trabalhar em várias specs em
paralelo e mantém a árvore limpa que `/specs:execute` exige. A preferência
precisa inverter, sem que a branch simples deixe de ser possível.

A segunda: nada apaga o worktree depois. `/specs:conclude` termina no merge —
essa é sua última ação — e o worktree fica no disco, ao lado do repositório,
apontando para uma branch já integrada. Quem conclui várias specs acumula
diretórios órfãos que ninguém sabe se ainda são necessários. Depois de um merge
bem-sucedido, o worktree deveria ser removido.

Fica em aberto o quanto disso é automático: remover um worktree é irreversível
para qualquer trabalho não commitado que ainda esteja nele, e `conclude` já
oferece — sem executar — a deleção da branch.

Há ainda um terceiro defeito, não declarado acima e verificado no código:
`/specs:conclude` §6 faz literalmente `git checkout <base> && git merge --no-ff
plan/<slug>`, e de dentro de uma worktree isso falha com `fatal: '<base>' is
already used by worktree at …` (exit 128). Hoje `conclude` não está apenas
desarrumado para worktrees — está quebrado para elas.

## Proposal

Quatro mudanças, uma direção só: a worktree deixa de ser a alternativa e passa a ser o caminho
inteiro, do isolamento até a limpeza.

1. **`/specs:isolate` §4 oferece Worktree primeiro e recomendada**, incondicionalmente — sem
   heurística sobre o repositório alvo. A branch simples e o trabalho em lugar nenhum continuam
   disponíveis, na mesma ordem depois dela. A própria oferta diz numa linha o que a worktree **não**
   carrega — dependências instaladas, `.env`, venv, tudo que o git ignora ou não rastreia — para que
   escolher Branch seja uma decisão lida, e não uma descoberta no primeiro `verify:` que falha.

2. **`/specs:conclude` faz o merge sem `git checkout`.** Localiza qual checkout detém a base e roda
   `git -C <esse caminho> merge …`. É uma via só: da worktree o caminho é o checkout principal, do
   checkout principal é ele mesmo.

3. **Depois de um merge bem-sucedido, `conclude` remove a worktree** — `git worktree remove`, nunca
   `--force`, rodado a partir do checkout da base. Árvore limpa sai do disco em silêncio; árvore
   suja o git recusa por conta própria, e `conclude` reporta o caminho e o motivo em vez de insistir.

4. **O repositório alvo pode declarar um script de setup** em `specs/config.json`, lido
   deterministicamente por `specs.py` e rodado por `/specs:isolate` na worktree recém-criada, para
   que ela nasça utilizável num repo com dependências instaladas.

O que passa a ser verdade depois, e não é hoje: concluir uma spec isolada não deixa diretório no
disco; o caminho recomendado é o que funciona até a última ação; e um repo com build pode adotar
worktree sem que o primeiro `verify:` quebre.

## Out of Scope

- o eixo "o run move para uma worktree?" de `/specs:develop`, `/specs:execute` e `/specs:conclude` —
  é da spec `2026-07-28-add-specs-cycle-run-modes`, que passa a ler como default o que esta decide.
  Esta spec define o default de `/specs:isolate`; aquela define se um run pode sobrescrevê-lo por
  invocação.
- varrer worktrees órfãs deixadas por specs concluídas **antes** desta mudança — esta spec fecha a
  torneira, e limpar o passivo histórico é um sweep com raio de ação próprio, candidato a
  `/specs:align` ou a uma spec dedicada.
- rodar o script de setup sobre uma worktree que já existe (um `/specs:isolate --setup` sobre uma
  worktree viva) — é uma segunda porta de entrada para o mesmo gancho, e só faz sentido depois que
  ele existir.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/workflows/plan-git-record.md` — o merge de um plano nunca é `git checkout <base>`; a
  worktree é removida após um merge bem-sucedido, sem `--force`
- `docs/standards/workflows/worktree-setup.md` — o contrato do `specs/config.json`: onde mora, qual
  chave, o que significa ausente, quem roda o script e com qual cwd

### Standards at `authority: background` this spec may resolve

- none — nenhum standard em `authority: background` toca isolamento, merge ou o front `specs/`

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/specs.py` — leitura do `specs/config.json` e os dois achados do doctor
- `plugins/quenching/commands/specs/isolate.md` — a oferta invertida e o gancho de setup
- `plugins/quenching/commands/specs/conclude.md` — o merge por `git -C` e a remoção da worktree
- `plugins/quenching/assets/references/specs-isolate/git.md` — dono da colocação da worktree e das
  estratégias de merge; a mudança é dele antes de ser dos comandos que o citam
- `plugins/quenching/assets/specs/QUENCHING.md` — o manual do front, que enumera a própria superfície
- `CLAUDE.md` — a afirmação "no Node runtime, no `config.yaml`" deixa de ser verdadeira quando
  `specs/config.json` existe

## Validation

### Os checadores que já existem

De `plugins/quenching/`:

```bash
cat VERSION && python3 assets/bin/specs.py --version && python3 assets/bin/skills.py --version \
  && python3 assets/hooks/okf-validate.py --version        # os quatro devem coincidir
python3 assets/bin/skills.py --root . doctor --json        # 25 commands, 0 findings
python3 assets/bin/skills.py --root . lint --json          # exit 0
python3 assets/hooks/okf-validate.py assets/docs           # 0 error(s), 0 warning(s)
python3 assets/bin/specs.py selftest && python3 assets/bin/skills.py selftest \
  && python3 assets/hooks/okf-validate.py selftest         # os três, exit 0
./assets/bin/functional-checks.sh                          # 9 assertions, exit 0
```

E da raiz do repositório, cobrindo o standard novo:

```bash
python3 plugins/quenching/assets/hooks/okf-validate.py docs   # 0 error(s), 0 warning(s)
```

### O roteiro end-to-end, num repositório descartável

É o único lugar que prova os dois comportamentos que vivem em prosa. Roda à mão, em menos de um
minuto:

```bash
T=$(mktemp -d) && git -C "$T" init -q
# scaffold do workspace, uma spec, isolamento em worktree, e a conclusão até o merge
```

Duas asserções observáveis, e nenhuma sobre o que o comando disse ter feito:

```bash
git -C "$T" log --oneline <base> | grep -q "merge (merge-commit)"   # o merge chegou à base
test ! -d "<caminho da worktree>"                                    # a worktree saiu do disco
```

### O exercício do `specs/config.json`

```bash
printf '{"worktreeSetup":"./setup.sh"}' > "$T/specs/config.json"
python3 <specs.py> doctor --json      # nenhum achado de config
printf '{"worktree_setup":"./setup.sh"}' > "$T/specs/config.json"
python3 <specs.py> doctor --json      # sp-config-unknown-key
printf '{' > "$T/specs/config.json"
python3 <specs.py> doctor --json      # sp-config-unparseable — e NÃO um traceback
```

O terceiro caso é o que importa: um JSON truncado tem de sair como achado, nunca como exceção crua.

## Design

### O merge, sem `git checkout`

```bash
git worktree list --porcelain                 # qual checkout detém <base>
git -C <caminho> merge --no-ff plan/<slug> -m "plan/<slug>: merge (merge-commit)"
```

Nunca `git checkout <base>`: de dentro de uma worktree isso é
`fatal: '<base>' is already used by worktree at …`, exit 128 — verificado neste repositório. A mesma
chamada serve os dois casos, porque do checkout principal `<caminho>` é ele mesmo.

**Quando nenhum checkout detém a base**, `/specs:conclude` diz qual base procurava, que ninguém a
detém, e o que fazer (`git checkout <base>` no principal, ou uma worktree da base) — e **para, sem
merjar**. Não inventa um checkout e não faz um temporário. O `merge:` já foi carimbado antes do
merge, então o run é retomável sem perder nada, e recusar aqui é a mesma recusa que `conclude` já
faz com caixas abertas.

### A remoção da worktree

```bash
git -C <checkout da base> worktree remove <caminho da worktree>
```

Sem `--force`, jamais. `git worktree remove` já recusa sozinho quando há arquivo modificado ou não
rastreado (`contains modified or untracked files`, exit 128 — verificado), de modo que a
irreversibilidade que o `## Problem` teme é exatamente o que o git se nega a fazer: nenhum prompt
compra segurança aqui, e nenhum é feito. Roda a partir do checkout da base porque ninguém remove a
árvore em que está pisando, e só após um merge verificado em exit 0.

Recusa do git → `conclude` reporta o caminho e a saída verbatim, e segue. A worktree fica.

### O gancho de setup

`specs/config.json`, na raiz do workspace, lido por `specs.py` com `json.load` — sem formato novo e
sem parse de prosa:

```json
{"worktreeSetup": "./scripts/wt-setup.sh"}
```

Arquivo ausente, chave ausente, ou script inexistente = nenhum setup, e nada disso é um achado.
`/specs:isolate` roda o comando com cwd na worktree recém-criada e reporta saída e exit code. Uma
falha do script não desfaz a worktree — ela existe e é utilizável ou não, e qual dos dois é um fato
reportado.

**O consentimento vem do OK que já existe.** O bloco de plano do `/specs:isolate` §4 — que já mostra
spec, base, nome da branch e caminho da worktree — passa a mostrar também o comando lido do
`specs/config.json`, **verbatim**. Escolher **Worktree** já é o OK para ele: nenhum prompt novo,
nenhum estado do tipo "este repositório já foi autorizado", e o humano lê o comando na mesma tela em
que decide a forma, que é onde consegue julgá-lo. O script nunca roda sem ter sido exibido antes.

**O schema é uma chave.** `worktreeSetup` é a única reconhecida. `specs.py doctor` reporta
`sp-config-unknown-key` (warn) para qualquer outra e `sp-config-unparseable` (warn) para JSON
malformado — nunca uma exceção crua, nunca uma recusa. O modo de falha real de um arquivo lido por
máquina é `worktree_setup` escrito onde se esperava `worktreeSetup`, e o silêncio que se segue; os
dois achados existem para que esse silêncio não aconteça.
## Alternatives Considered

| Decisão | Escolhido | Rejeitado, e por quê |
| --- | --- | --- |
| o merge | `git -C` no checkout que detém a base | *recusar e mandar rodar do checkout principal* — parte o run em dois e devolve ao humano exatamente o atrito que a worktree como default deveria remover; *dois caminhos separados* (`git checkout` no principal, `git -C` na worktree) — duas vias para o mesmo resultado, com o dobro de superfície e um ramo que quase nunca roda |
| a remoção | remove sem perguntar, nunca `--force` | *oferecer e esperar o OK* — consistente com a deleção da branch que `conclude` já oferece, mas paga um prompt em toda conclusão contra um risco que o git já recusa, e um prompt sempre respondido "sim" é só atrito; *tentar e oferecer `--force` na recusa* — põe `conclude` oferecendo destruir trabalho não commitado logo depois de um merge, o momento em que o humano menos olha |
| o default | incondicional, com o custo dito na própria oferta | *condicional por heurística* (`node_modules/`, `.venv/`, `.env`, `package.json`) — acerta mais casos sozinho, mas coloca uma heurística advinhando o build de um repo alheio, e uma recomendação que muda de repo em repo é impossível de documentar numa frase; *incondicional e calado* — o mais barato de escrever, e o que transforma o caminho recomendado numa armadilha silenciosa em qualquer repo com dependências |
| o gancho | `specs/config.json` lido por `specs.py` | *`specs/worktree-setup.sh`, cuja existência seria a declaração* — determinístico por um `stat`, sem formato para errar, e não reintroduz configuração no front; *um doc em `docs/standards/` com a chave no frontmatter* — segue o contrato read-if-present que `git.md` já usa, mas obriga `specs.py` a parsear frontmatter de markdown para achar um caminho executável, e mistura o home dos contratos com um ponteiro operacional |

**Nota honesta sobre o gancho.** Escolher `specs/config.json` **reverte uma decisão registrada**: o
`CLAUDE.md` afirma que este front não tem arquivo de configuração ("no Node runtime, no
`config.yaml`"), e `specs.py` hoje carrega schema e templates de `assets/specs/` quando adjacentes,
senão de constantes embutidas — nunca de configuração do alvo. A escolha foi feita com isso à
vista: um arquivo declarativo extensível vale mais que a ausência dele quando o próximo parâmetro
aparecer. Quem revisar precisa saber que a ausência de config era deliberada, não um esquecimento —
e que esta spec é quem a desfaz.

## Open Decisions

- none — as três decisões que estavam aqui foram resolvidas no banco do gate em 2026-07-28, e cada
  uma caiu na seção que a detém: o consentimento para rodar o script do alvo e o caso da base não
  checada em lugar nenhum estão em `## Design`; o schema do `specs/config.json` está em `## Design` e
  é provado por `## Validation` §exercício, com as tarefas 1.2 e 4.2 escrevendo-o. A primeira delas
  havia sido estacionada no banco adversarial e foi decidida por pergunta direta — não passou por um
  premortem, e quem quiser esse ângulo ainda pode rodá-lo.
## Risks

- **O gancho executa código do repositório alvo.** `/specs:isolate` hoje não roda nada do alvo, e
  passar a rodar é uma mudança de postura. **Mitigação:** o comando é exibido verbatim no bloco de
  plano, e escolher Worktree é o OK para ele — jamais roda sem ter sido exibido.
- **A remoção acontece logo depois do merge**, o ponto do ciclo em que o humano menos olha.
  **Mitigação:** só ocorre com o merge verificado em exit 0, e nunca com `--force`; o git recusa
  sozinho qualquer árvore com modificado ou não rastreado, e a recusa é reportada em vez de contornada.
- **Metade da spec é prosa em corpo de comando**, que `skills.py` e `okf-validate.py` não conseguem
  provar — um corpo pode dizer `git -C` e o run continuar fazendo `git checkout`. **Mitigação:** o
  roteiro end-to-end de `## Validation`, rodado à mão antes de concluir, assere sobre o estado do
  disco e do `git log`, não sobre o que o comando disse ter feito.
- **ACCEPTED** — worktree como default incondicional quebra o primeiro `verify:` num repositório com
  dependências instaladas que não declarou `worktreeSetup`. *Por quê é aceitável:* o custo é dito na
  própria oferta, em uma linha, e Branch continua a um clique de distância; a alternativa era uma
  heurística advinhando o build de um repo alheio.
- **ACCEPTED** — `specs/config.json` reverte a decisão registrada de que este front não tem arquivo
  de configuração. *Por quê é aceitável:* está escrito em voz alta em `## Alternatives Considered`,
  com o motivo, para que quem revisar saiba que a ausência era deliberada e que esta spec é quem a
  desfaz.

## Handoff

Todas as 12 tasks estão `- [x]`, cada uma em seu próprio commit na branch `plan/prefer-worktree-isolation`
(base: `main`). Nenhuma bloqueada. Pronta para `/specs:conclude`.

**Duas descobertas abertas em `## Discoveries`, para o `/specs:conclude` resolver:**
- `functional-checks.sh` check 3 (roteamento por gatilho falado) é não-determinístico — uma
  reprovação isolada não é evidência de regressão.
- O fechamento da seção 5 (`okf-validate.py docs` na raiz) reportou 6 warnings `stale-doc` novos
  (além do `resource-unresolved` pré-existente em `automation/agents.md`), porque os `resource:`
  globs de `plugin-layout.md`, `skills.md`, `plan-git-record.md`, `plan-lifecycle.md`,
  `task-execution.md` e `worktree-setup.md` casam com arquivos que esta spec commitou (`git.md`,
  `QUENCHING.md`, o próprio arquivo da spec) — e esses commits landaram em 2026-07-29, um dia
  depois do timestamp `2026-07-28` desses cinco documentos. Nenhum é `files:` de nenhuma task
  desta spec, então nenhum foi tocado; o conteúdo de `plan-git-record.md` e `worktree-setup.md`
  foi escrito para antecipar exatamente o `git.md` que a 5.1 implementou depois, e é o caso mais
  provável de já estar correto.

O roteiro end-to-end de `## Validation` (merge por `git -C`, remoção da worktree sem `--force`)
foi exercitado à mão num repositório descartável na 6.1 — as duas asserções passaram e o
descartável foi limpo.

## Tasks

- [x] 1.1 `specs.py` lê `specs/config.json` e expõe `worktreeSetup`
      files: plugins/quenching/assets/bin/specs.py
      verify: config com a chave certa num workspace descartável; ausência de arquivo não é achado
      subject: plan/prefer-worktree-isolation: 1.1 specs.py lê specs/config.json e expõe worktreeSetup
- [x] 1.2 `specs.py doctor` reporta `sp-config-unknown-key` e `sp-config-unparseable`, ambos warn
      files: plugins/quenching/assets/bin/specs.py
      verify: os três casos de `## Validation` §exercício; JSON truncado sai como achado, não traceback
      subject: plan/prefer-worktree-isolation: 1.2 specs.py doctor reporta sp-config-unknown-key e sp-config-unparseable
- [x] 2.1 `/specs:isolate` §4 oferece Worktree primeiro e recomendada, com a linha do que ela não carrega
      files: plugins/quenching/commands/specs/isolate.md
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json
      subject: plan/prefer-worktree-isolation: 2.1 /specs:isolate oferece Worktree primeiro e recomendada
- [x] 2.2 `/specs:isolate` exibe o comando do `worktreeSetup` no bloco de plano e o roda após `git worktree add`
      files: plugins/quenching/commands/specs/isolate.md
      verify: skills.py lint exit 0; o corpo diz que o comando é exibido antes de rodar
      subject: plan/prefer-worktree-isolation: 2.2 /specs:isolate exibe e roda o worktreeSetup
- [x] 3.1 `/specs:conclude` faz o merge por `git -C` no checkout da base, e recusa quando nenhum a detém
      files: plugins/quenching/commands/specs/conclude.md
      verify: skills.py lint exit 0; o corpo não contém mais `git checkout <base>` no passo do merge
      subject: plan/prefer-worktree-isolation: 3.1 /specs:conclude faz o merge por git -C no checkout da base
- [x] 3.2 `/specs:conclude` remove a worktree após um merge bem-sucedido, sem `--force`
      files: plugins/quenching/commands/specs/conclude.md
      verify: skills.py lint exit 0; `--force` não aparece no passo de remoção
      subject: plan/prefer-worktree-isolation: 3.2 /specs:conclude remove a worktree após o merge, sem --force
- [x] 4.1 [P] Escrever docs/standards/workflows/plan-git-record.md — o merge sem checkout e a remoção da worktree
      files: docs/standards/workflows/plan-git-record.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
      subject: plan/prefer-worktree-isolation: 4.1 plan-git-record.md — o merge sem checkout e a remoção da worktree
- [x] 4.2 [P] Escrever docs/standards/workflows/worktree-setup.md — o contrato do `specs/config.json`
      files: docs/standards/workflows/worktree-setup.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
      subject: plan/prefer-worktree-isolation: 4.2 worktree-setup.md — o contrato do specs/config.json
- [x] 5.1 [P] Emendar `specs-isolate/git.md` — a worktree como forma preferida e o merge por `git -C`
      files: plugins/quenching/assets/references/specs-isolate/git.md
      verify: ./plugins/quenching/assets/bin/functional-checks.sh
      subject: plan/prefer-worktree-isolation: 5.1 git.md — a worktree como forma preferida e o merge por git -C
- [x] 5.2 [P] Emendar `assets/specs/QUENCHING.md` com a oferta invertida e o `specs/config.json`
      files: plugins/quenching/assets/specs/QUENCHING.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/specs/plans --listing-root
      subject: plan/prefer-worktree-isolation: 5.2 QUENCHING.md — a oferta invertida e o specs/config.json
- [x] 5.3 [P] Corrigir no `CLAUDE.md` a afirmação de que este front não tem arquivo de configuração
      files: CLAUDE.md
      verify: a frase "no Node runtime, no `config.yaml`" não descreve mais o front
      subject: plan/prefer-worktree-isolation: 5.3 CLAUDE.md — a afirmação já não existe (removida pelo align anterior)
- [x] 6.1 Rodar o roteiro end-to-end de `## Validation` e registrar as duas asserções
      files: none
      verify: `git log --oneline <base>` contém `merge (merge-commit)` e `test ! -d <worktree>`
      subject: plan/prefer-worktree-isolation: 6.1 roteiro end-to-end — merge por git -C e remoção da worktree, ambos confirmados

## Discoveries

- functional-checks.sh check 3 (spoken-trigger routing) is nondeterministic — the /docs:add assertion failed once and passed on an identical re-run, so a single red run is not evidence of a regression and the script's exit 0 is not reproducible per-run
- 5.3: a frase citada ("no Node runtime, no `config.yaml`") já não existe em CLAUDE.md — o commit fcb2a52 (align: converge all three fronts in one pass), incorporado pelo merge de main antes da task 1.1, reescreveu o arquivo de 374 para ~106 linhas e removeu a alegação junto com todo o bloco em que vivia. O verify da task ("a frase ... não descreve mais o front") já é verdadeiro sem edição; nenhuma mudança em CLAUDE.md foi necessária.
- Fechamento da seção 5: `okf-validate.py docs` na raiz reporta 0 erro(s) mas 7 warning(s), não 0/0 como o bloco de ## Validation antecipava — 1 é o `resource-unresolved` pré-existente em automation/agents.md (já registrado em log.md), e 6 são `stale-doc` novos (architecture/plugin-layout.md, automation/skills.md, workflows/plan-git-record.md, workflows/plan-lifecycle.md, workflows/task-execution.md, workflows/worktree-setup.md). Causa: seus `resource:` globs (assets/**, specs/**, ou citando git.md diretamente) casam com arquivos que esta spec commitou (git.md na 5.1, QUENCHING.md na 5.2, e o próprio arquivo da spec em toda task) — e esses commits landaram em 2026-07-29 depois que o relógio real virou o dia, enquanto os cinco documentos carregam timestamp: 2026-07-28. Nenhum dos cinco é files: de nenhuma task desta spec, então nenhum foi tocado — bater o timestamp sem uma revisão de conteúdo real seria carimbar authority sem lastro. O conteúdo de plan-git-record.md e worktree-setup.md (tasks 4.1/4.2) foi escrito para antecipar exatamente o git.md que a 5.1 implementou depois, então é o caso mais provável de já estar correto; plugin-layout.md, skills.md e plan-lifecycle.md têm globs amplos que capturam qualquer coisa sob assets/** ou specs/**, não mudanças no assunto que eles próprios descrevem.
