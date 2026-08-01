---
slug: restructure-claude-front-namespace
title: Rename the /skill namespace to /claude and split it into artifact contexts
verification: per-section
priority: {level: 19, criticality: medium, date: 2026-07-29}
refined: {mode: adversarial, date: 2026-08-01}
---

# Rename the /skill namespace to /claude and split it into artifact contexts

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

O front de comandos `.claude/` do plugin se chama `skill`, mas `skill` também é o nome de um tipo
específico de artefato dentro dele, então os agents e os hooks aninhados em `commands/skill/` se leem
como sub-tipos de uma skill quando não são — é esse o defeito que este spec existe para corrigir.
`## Problem` conta como a árvore chegou nesse estado.

A correção renomeia o front inteiro para **`claude`** — a árvore que ele possui, do mesmo jeito que
os fronts `docs` e `specs` são nomeados pelas suas — e lhe dá quatro contextos irmãos, um por
artefato que ele cunha: `command/`, `agent/`, `hook/`, `harness/`, com o comando que alinha o
`CLAUDE.md` migrando para `harness`. `## Proposal` lista o que passa a ser verdade; `## Out of Scope`
marca sete coisas vizinhas que se parecem com isso e ficam de fora, incluindo o diretório de payload
`assets/claude/`, os registros históricos de medição, e a pasta de assunto `docs/standards/automation/`,
cujo nome deixa de casar com o do front — uma incoerência declarada de propósito em vez de resolvida.

`## Design` percorre as escolhas que a renomeação força, e a primeira é o nome: `automation` perdeu
por colidir com domínio de produto no alvo, e `agents` por reintroduzir o defeito deste spec, já que
`agent/` é um dos quatro contextos. Depois: onde cada um dos sete comandos movidos vai parar (numa
tabela, para que nenhum sobre), o que a renomeação de caminho **arrasta consigo** por obrigação de
`plugin-layout.md` — as pastas de referência e as árvores de eval seguem o comando dono —, por que o
estágio compartilhado `harness` pode ser invocado com segurança por dois aligns diferentes, e por que
a regra bare-vs-registry-name precisa de dono em duas formas, uma citável pelo plugin e uma de
standard.

`## Alternatives Considered` guarda duas tabelas: os três nomes de front, com a razão de cada
derrota para que não sejam refeitas, e as cinco formas inteiras do spec. Entre estas, a que perde de
forma menos óbvia é "dividir em dois specs": parece a mais segura e é a mais cara, porque o segundo
rebaseia por cima da reescrita que o primeiro fez dos mesmos arquivos. `## Risks` é o produto de um
premortem, e as duas histórias que mais importam são silenciosas — um `resource:` órfão em seis
standards derruba a conformidade do bundle, e uma renomeação pela metade não falha em nada, apenas
fica quietamente errada. Um terceiro risco é aceito de olhos abertos: nada reescreve o texto
`/skill:*` que já foi instalado em repositórios-alvo pelos moldes.

`## Impact` separa o que este spec **promete escrever** — dois standards, os únicos que carregam regra
— do muito maior conjunto que ele apenas reescreve mecanicamente. `## Validation` traz cinco
assertivas, e uma delas deliberadamente não é um número limpo: o bundle já carrega 14 warnings hoje, e
o alvo real é "nenhuma finding must-fix nova", com um `git grep` que precisa voltar vazio como a única
assertiva capaz de distinguir renomeado de renomeado-pela-metade. `## Tasks` organiza 278 strings em 59
arquivos em cinco grupos, sob uma regra só: mover e recitar é uma task, nunca duas — e sem citar
contagem nenhuma, porque os números da versão anterior envelheceram em quatro dias. A queda de 326/61
para 278/59 é escopo entregue por `correct-command-citation-form`, não escopo perdido. A dependência
de `instrument-and-extend-skill-front` está quitada (merge `4421185`), e `## Open Decisions` deixa
quatro perguntas para depois: se `skills.py` e os seus códigos `sk-*` também são renomeados, se a
pasta de assunto acompanha o front, se um spec irmão sobre vocabulário obsoleto fica superado, e quem
reescreve o que já está instalado em um alvo.
## Problem

O plugin fez o fluxo de autoria crescer dentro de `commands/skill/`, quando um comando era o único
artefato que aquele front cunhava. Hoje a árvore também abriga `commands/skill/agent/` e
`commands/skill/hook/`, então `skill` nomeia ao mesmo tempo o front `.claude/` **inteiro** *e* um
único tipo de artefato dentro dele — agents e hooks se leem como sub-tipos de uma skill, o que não
são.

A proposta original era renomear `commands/skill/` para um nome de front genérico, como `claude`, e
criar dentro dele um contexto `skill` que ficasse ao lado de `hook` e `agent`, e não acima deles. Os
comandos que alinham ou atualizam `CLAUDE.md` deveriam se mudar para esse front também.

Separadamente, a premissa original era que `assets/` cita os comandos do plugin sem o prefixo do
nome do plugin — p.ex. `assets/references/skill-new/doctrine.md` nomeia `/skill:new` onde a
identidade registrada é `/quenching:skill:new` — e que todas essas citações estariam erradas duas
vezes depois de uma renomeação. Essa metade da premissa foi fechada por outro spec antes que este
fosse construído: ver `## Out of Scope`, primeiro item.
## Proposal

- O front `.claude/` passa a se chamar **`claude`**, a árvore que ele possui — a mesma regra que
  nomeia os fronts `docs` e `specs`, e que passa a valer também para o payload `assets/claude/`. Os
  dois nomes que perderam estão em `## Alternatives Considered` com a razão: `automation` colide com
  domínio de produto no alvo, e `agents` reintroduz o defeito que este spec existe para corrigir.
- `commands/skill/` passa a ser `commands/claude/`, abrigando **quatro contextos irmãos nomeados
  pelo artefato que cada um cunha** — `command/`, `agent/`, `hook/`, `harness/`. Nenhum contexto é
  sub-tipo de outro, que é justamente o defeito que este spec existe para corrigir.
- `/skill:new` passa a ser `/claude:command:new`, então o front deixa de usar uma palavra só para si
  mesmo e para um artefato dentro de si.
- `/docs:harness` passa a ser `/claude:harness:align`, entrando no front que é dono de todo arquivo
  que o Claude Code lê como instrução.
- Verbos de nível de front ficam na raiz do front (`/claude:align`); verbos de nível de artefato
  ficam sob o seu contexto (`/claude:command:eval`, `/claude:command:retro`).
- Os seis comandos hoje sob `commands/skill/` têm destino declarado, nenhum sobra: ver a tabela em
  `## Design` §*Um contexto é nomeado pelo artefato que cunha*.
- Toda citação de um caminho movido em `commands/**`, `assets/**`, `docs/**`, `CLAUDE.md`,
  `README.md` e nos quatro manuais `QUENCHING.md` resolve para o nome novo — 278 strings medidas em
  59 arquivos, e a superfície continua com 26 comandos porque nenhum comando é criado ou removido.
- O substantivo "skill" deixa de aparecer onde se quer dizer "command" — a varredura de vocabulário
  que `retire-skill-vocabulary` descreve é entregue no mesmo diff da renomeação de caminhos, porque
  as duas reescrevem os mesmos arquivos.
- A regra bare-vs-registry-name passa a ter exatamente um dono citável que os dois aligns citam, em
  vez de ser repetida inline em dois corpos de comando.
## Out of Scope

- **Prefixar citações voltadas a humanos com `quenching:`.** A premissa original deste spec era que
  as citações em `assets/` careciam do prefixo do plugin, e o item foi fechado citando
  `commands/docs/align.md`, que declarava a forma bare como "what a human types". Essa frase era
  falsa com o plugin instalado **como plugin**, e `correct-command-citation-form` (2026-07-31) a
  corrigiu: são **três** formas, e a bare resolve **apenas** onde o arquivo do comando mora no
  `.claude/commands/` do repo-alvo — `docs/standards/naming/command-surface.md`
  §*Three citation forms, and the condition on each*. A varredura já foi feita em `commands/**` e
  `assets/references/**`, e o finding `sk-bare-citation` (WARN) guarda a regra daqui em diante.
  Fica fora de escopo porque **o trabalho já foi feito por outro spec**, não porque a forma bare
  esteja certa — e é por isso que a assertiva 3 de `## Validation` grepa as **duas** formas.
- **Renomear o arquivo ou o slug deste spec.** Um spec nunca se move a não ser para `archive/`. O
  slug `restructure-claude-front-namespace` ficou correto por acidente da história: `claude` era o
  nome proposto no início, perdeu para `automation` durante o `## Design`, e voltou a ganhar.
- **Renomear a pasta de assunto `docs/standards/automation/`.** Com o front chamado `claude`, o nome
  da pasta deixa de casar com o do front, e essa incoerência é **declarada aqui em vez de
  resolvida**: é ela que carrega a colisão de domínio no alvo — o plugin escreve
  `docs/standards/<assunto>/**` em repositórios que podem ter automação como assunto de produto — e
  fechá-la é uma decisão sobre o bundle OKF, não sobre a superfície de comandos. Ver
  `## Open Decisions`.
- **Renomear o diretório de payload `plugins/quenching/assets/claude/`.** Ele é nomeado pela **árvore
  do alvo** em que é copiado, exatamente como `assets/docs/` → `docs/` e `assets/specs/` → `specs/`.
  Com o front chamado `claude` os dois nomes passam a coincidir, o que é a simetria funcionando e não
  uma renomeação a fazer.
- **Reescrever `plugins/quenching/assets/evals/**/runs/**`.** Aqueles `benchmark.json` e
  `grading.json` são medições de execuções que realmente aconteceram contra um comando realmente
  chamado `quenching:skill:agent:new`. Reescrevê-los falsificaria o registro. O diretório se move
  para manter o espelho 1:1 e o `evals.json` (o arquivo de casos vivo) é reescrito; `runs/**` fica
  byte-idêntico — ver `## Design` §*O que se move e o que não se reescreve*.
- **Auditar corpos de comando em busca de deriva de doutrina.** Essa é a auditoria read-only do
  `/claude:align` e continua sendo uma passada separada, dirigida por humano.
- **Decidir se descrições always-on continuam existindo.** É o objeto de
  `route-commands-without-always-on-descriptions`; este spec reescreve o texto das descrições apenas
  onde ele nomeia um caminho renomeado, e não opina sobre a existência delas.
## Impact

Escopo declarado para revisão humana. Só a primeira sub-seção é parseada.

### Standards this spec will write into docs/standards/

- `docs/standards/naming/command-surface.md` — o front `.claude/` passa a ser `claude`, com quatro
  contextos irmãos nomeados pelo artefato que cada um cunha; verbos de front na raiz e verbos de
  artefato sob o seu contexto; e a regra bare-vs-registry-name, que ganha o seu enunciado de standard
  ao lado do §*Three citation forms* que `correct-command-citation-form` já escreveu. É o doc cujo
  §*Namespaces are honest by artifact* enumera `/skill:` como o nome do front, então ele erra no
  minuto do `git mv` se não for reescrito.
- `docs/standards/architecture/align-surface.md` — a linha `.claude/` da tabela §*The 1×4 column* lê
  `/skill:align` e passa a ler `/claude:align`; e o §*Probe before the inventory* nomeia
  `skills.py doctor`/`lint` como o verificador daquele front, cujo nome depende de `## Open Decisions`.

Só estes dois carregam **regra**. Todos os outros standards tocados recebem reescrita de citação e de
`resource:` — trabalho mecânico, não decisão nova — e por isso estão listados abaixo em vez de aqui:
declarar nove caminhos onde dois carregam a regra inflaria a promessa que `sp-impact-uncovered`
verifica.

### Standards at `authority: background` this spec may resolve

- none — três dos standards tocados são `background`
  (`docs/standards/automation/session-evidence.md`, `context-budget.md`, `agents.md`), mas este spec
  não prova nenhuma das regras deles. Ele reescreve os `resource:` e as citações; o grau de
  `authority` de cada um continua exatamente onde está, e promovê-los aqui seria mentir sobre o que
  esta renomeação demonstrou.

### Product code this spec expects to touch

Sete arquivos de comando movidos, três pastas de referência, duas árvores de eval, e a varredura
mecânica de 278 strings em 59 arquivos:

- `plugins/quenching/commands/skill/**` (6 arquivos) → `plugins/quenching/commands/claude/**`
- `plugins/quenching/commands/docs/harness.md` → `plugins/quenching/commands/claude/harness/align.md`
- `plugins/quenching/commands/align.md`, `commands/docs/align.md`, `commands/docs/status.md`,
  `commands/specs/align.md` — as citações e as invocações por registry name, que são 71 strings
  `quenching:skill*` e não a única que este item já declarou
- `plugins/quenching/assets/references/skill-new/`, `skill-eval/`, `docs-harness/` — renomeadas por
  obrigação de `plugin-layout.md` §`{name}` is the owning command's path, flattened
- `plugins/quenching/assets/references/align/sweep-doctrine.md` — passa a ser o dono citável da regra
  bare-vs-registry-name
- `plugins/quenching/assets/evals/skill/{agent,hook}/new/` → `assets/evals/claude/{agent,hook}/new/`,
  com `runs/**` byte-idêntico
- `plugins/quenching/assets/templates/automation/` (7 moldes) — o **conteúdo** das citações muda; o
  nome da pasta não, porque ela é nomeada pelo assunto do bundle e não pelo front (`## Out of Scope`)
- `plugins/quenching/assets/bin/skills.py` — as strings `/skill:*` dentro dos textos de remédio das
  findings; é um dos seis artefatos do lockstep, então a correção só chega a um alvo com o bump de
  versão
- `plugins/quenching/assets/checks/functional-checks.sh` — expectativas do probe e o bloco de
  comentário WHO RUNS THIS
- `plugins/quenching/.claude-plugin/plugin.json` e `.claude-plugin/marketplace.json` — a descrição do
  plugin que um humano lê **antes** de instalar nomeia `/skill:align`
- `plugins/quenching/README.md`, `assets/README.md`, `assets/templates/README.md`, `CLAUDE.md` na raiz
- os quatro manuais: `assets/claude/QUENCHING.md`, `assets/docs/QUENCHING.md`,
  `assets/specs/QUENCHING.md` e `docs/QUENCHING.md` — o rider de
  `docs/standards/ci-cd/versioning-release.md` §*The operator-manual rider* diz que uma renomeação de
  comando obriga a editar o `QUENCHING.md` do front daquele comando, e aqui **dois** fronts são
  atingidos porque `/docs:harness` sai de um e entra no outro
- entradas `resource:` e `timestamp` em `docs/standards/quality/surface-verification.md`,
  `architecture/align-surface.md`, `architecture/plugin-layout.md`, `automation/session-evidence.md`,
  `automation/skill-evaluation.md`, `automation/agents.md`, `automation/hooks.md`,
  `automation/skills.md`, `ci-cd/versioning-release.md`, e o link do glossário em
  `docs/knowledge/glossary.md:90`
## Validation

Cinco assertivas. Uma delas não pode ser um número limpo, e dizer isso é parte da validação: o bundle
deste repositório já carrega **14 warnings hoje**, então "zero warnings" seria um alvo falso que
esconderia a única coisa que esta renomeação de fato quebra.

Rodar da raiz do repositório, exceto onde indicado.

**1. A superfície continua carregando, com a mesma contagem.**

```bash
python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json
```

Deve reportar `"commands": 26` e `"findings": []`. A contagem é o invariante que separa "movido" de
"perdido": sete comandos trocam de caminho, nenhum é criado e nenhum é removido, então 26 antes e 26
depois. Qualquer outro número significa que um `git mv` deixou um arquivo fora de `commands/**` ou
criou um caminho duplicado.

```bash
python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json
```

Exit 0. Warnings são reportados e não são fatais, mas nenhum `sk-*` **novo** deve aparecer em relação
ao baseline tirado antes do grupo 1 — inclusive nenhum `sk-bare-citation` novo, que é o finding que
guarda a forma de citação e o que uma renomeação descuidada mais facilmente reintroduz.

**2. O bundle OKF não ganhou nenhuma finding must-fix.**

```bash
python3 plugins/quenching/assets/hooks/okf-validate.py docs
```

O alvo não é zero. O alvo é: **nenhum `resource-unresolved` que nomeie um caminho `commands/`**, e
**nenhum `glossary-broken-link`**. As duas entradas `resource-unresolved` pré-existentes
(`.claude/agents/**` e `.claude/hooks/**`, em `automation/agents.md` e `automation/hooks.md`) continuam
lá e não são deste spec. `stale-doc` é advisory pela entrada *Advisory finding* de
`docs/knowledge/glossary.md` e não bloqueia; ainda assim, nenhum doc cujo `timestamp` uma task deste
spec deveria ter subido pode aparecer na lista.

**3. Nenhuma string antiga sobrou.** É a única assertiva que distingue "renomeado" de "renomeado pela
metade", porque nenhuma das duas falha em nada por si só.

```bash
git grep -nE '/skill:|quenching:skill|commands/skill|references/skill-|evals/skill|docs:harness|references/docs-harness' -- ':!specs/' ':!plugins/quenching/assets/evals/*/*/*/runs/'
```

Deve voltar **vazio**. O padrão do harness é `docs:harness` e não `/docs:harness` **de propósito**:
as citações estão hoje metade na forma bare e metade na prefixada (`/quenching:docs:harness`), e uma
âncora com `/` deixaria a metade prefixada passar — que é exatamente a renomeação-pela-metade que
esta assertiva existe para pegar. `specs/` está excluído porque os specs arquivados registram
história e não se reescrevem, e `runs/` porque uma medição histórica nomeia o comando como ele foi
invocado (`## Out of Scope`).

Antes do grupo 1, esse mesmo comando volta **278 hits em 59 arquivos**; esse é o baseline a
registrar. O número caiu de 326/61 porque `correct-command-citation-form` já converteu as citações
bare de `commands/**` e `assets/references/**` para a forma prefixada — é escopo já entregue por
outro spec, não escopo perdido por este.

**4. O esqueleto embarcado e os selftests continuam conformes.**

```bash
cd plugins/quenching
cat VERSION && python3 assets/bin/specs.py --version && python3 assets/bin/skills.py --version \
  && python3 assets/hooks/okf-validate.py --version && python3 assets/bin/session.py --version
python3 assets/hooks/okf-validate.py assets/docs                        # 0 error(s), 0 warning(s)
python3 assets/hooks/okf-validate.py assets/specs/plans --listing-root  # 0 error(s), 0 warning(s)
python3 assets/bin/skills.py selftest
python3 assets/bin/specs.py selftest
python3 assets/hooks/okf-validate.py selftest
```

Todos os cinco números de versão iguais. Os selftests importam aqui por um motivo específico: o de
`skills.py` monta uma superfície descartável e afirma que `sk-no-description` dispara nela, que é o
único check que cobre a regra de layout de `commands/**` — a regra que esta renomeação exercita mais
do que qualquer mudança anterior.

**5. A superfície de fato carrega e roteia — e esta é a única assertiva cobrada.**

```bash
plugins/quenching/assets/checks/functional-checks.sh              # checks 1, 2, 4
plugins/quenching/assets/checks/functional-checks.sh --only 3     # roteamento falado
```

`exit 0` todas as assertivas medidas passaram · `1` uma falhou · `2` nada pôde ser medido, o que
**não é um pass**. O check 3 é opt-in e cada execução é uma sessão de agente cobrada; ele é rodado
**uma vez**, no fim do grupo 5, depois de as suas próprias expectativas terem sido reescritas — rodar
antes disso mede o harness, não a superfície. Um vermelho aqui deve ser tratado como regressão real
até prova em contrário, apesar de `CLAUDE.md` registrar que todo vermelho histórico deste harness veio
de defeito do próprio harness: esta é exatamente a mudança que inverte essa estatística.
## Design

### O front é nomeado pela árvore que possui

`docs` e `specs` são nomeados pelas árvores que possuem, e `claude` mantém essa simetria: o front
possui `.claude/`, exatamente como `assets/docs/` → `docs/` e `assets/specs/` → `specs/`. A simetria
vale também para o payload — `assets/claude/` deixa de ser uma exceção que precisa de explicação e
passa a ser a terceira linha da mesma regra.

`automation` foi rejeitado por **colisão de domínio no alvo**: o plugin escreve
`docs/standards/<front>/**` em repositórios que podem ter automação como assunto de produto, e ali o
nome disputa com conteúdo do domínio. `agents` foi rejeitado por **reintroduzir o defeito que este
spec existe para corrigir** — `agent/` é um dos quatro contextos, então o front e um artefato dentro
dele voltariam a dividir uma palavra — e por colidir com `docs/standards/agents/`, cujo `index.md`
já gasta um parágrafo separando a conduta dada a um agente da definição de um. Ver
`## Alternatives Considered`, que guarda as duas com a razão para que não sejam refeitas.

A exposição aceita: se o Claude Code renomear `.claude/`, o nome do front fica devendo uma migração.
É um custo hipotético e reversível, contra uma colisão de domínio que é certa.

### Um contexto é nomeado pelo artefato que cunha

`command/`, `agent/`, `hook/`, `harness/`. `skill/` foi rejeitado como segmento do meio: o artefato
que ele cunha é um **command** (o *Entry point* do glossário, em
`docs/knowledge/glossary.md:128`), e `retire-skill-vocabulary` está retirando esse substantivo — um
segmento de caminho permanente reintroduzindo-o exigiria uma exceção justamente na instância mais
difícil de justificar.

Os seis comandos hoje sob `commands/skill/` mais o `/docs:harness`, com destino declarado — nenhum
sobra, o total de 26 comandos não muda:

| Hoje | Depois | Contexto |
| --- | --- | --- |
| `commands/skill/align.md` | `commands/claude/align.md` | raiz do front (varre o front inteiro) |
| `commands/skill/new.md` | `commands/claude/command/new.md` | `command` |
| `commands/skill/eval.md` | `commands/claude/command/eval.md` | `command` |
| `commands/skill/retro.md` | `commands/claude/command/retro.md` | `command` |
| `commands/skill/agent/new.md` | `commands/claude/agent/new.md` | `agent` |
| `commands/skill/hook/new.md` | `commands/claude/hook/new.md` | `hook` |
| `commands/docs/harness.md` | `commands/claude/harness/align.md` | `harness` |

`retro` fica em `command/` porque o seu próprio frontmatter declara o escopo: "ONE session for what
it evidences about ONE **command** that ran in it". Ele tem exatamente o escopo de `eval` e pertence
ao mesmo contexto. O caminho dele também é citado por
`docs/standards/automation/session-evidence.md:5` (em `resource:`) e por
`docs/standards/ci-cd/versioning-release.md:82`, que nomeia `/skill:retro` em prosa ao explicar por
que `session.py` fica fora do lockstep de seis artefatos.

Alternativa rejeitada: nenhum segmento do meio (`/claude:new` cunha um command, e agent e hook
continuam aninhados). Reproduz a assimetria de "um tipo de artefato é o default" um nível abaixo, que
é a forma que este spec remove.

### Verbos de front na raiz, verbos de artefato sob o seu contexto

`/claude:align` varre o front inteiro. `/claude:command:eval` mede um comando e lê apenas arquivos de
comando, então fica no contexto cujo escopo ele de fato tem. Estender o eval a definições de agent ou
a wiring de hook depois é uma renomeação, e esse custo é aceito em vez de chamá-lo de `/claude:eval`
hoje e implicar um escopo que ele não tem.

Rejeitado: um eval por contexto. Três corpos repetindo um procedimento de medição é a forma
skill+wrapper que o spec de collapse acabou de remover.

### O que a renomeação de caminho arrasta consigo

Duas consequências mecânicas que `docs/standards/architecture/plugin-layout.md` torna obrigatórias, e
que não são opcionais nem adiáveis:

- **As pastas de referência seguem o comando dono.** §`{name}` is the owning command's path,
  flattened: o nome da pasta é o caminho do comando, com `/` → `-`, e nada mais — e um nome de
  diretório que mente é proibido por `docs/standards/naming/command-surface.md`. Então
  `assets/references/skill-new/` vira `assets/references/claude-command-new/` (3 arquivos, citada
  por quatro comandos) e `assets/references/skill-eval/` vira
  `assets/references/claude-command-eval/` (1 arquivo).
- **As árvores de eval mantêm as barras.** §*`evals/` encodes the same source differently*:
  `commands/skill/hook/new.md` ↔ `evals/skill/hook/new/`, espelho 1:1 renomeado "in the same
  mechanical step as that command". Então `assets/evals/skill/agent/new/` vira
  `assets/evals/claude/agent/new/` e `assets/evals/skill/hook/new/` vira
  `assets/evals/claude/hook/new/`.

`assets/references/docs-harness/` segue a mesma regra e vira
`assets/references/claude-harness-align/`.

### O que se move e o que não se reescreve

Dentro de uma árvore de eval, `evals.json` é o arquivo de casos **vivo** e é reescrito. Já
`runs/2026-07-27-1930/benchmark.json` e `grading.json` são a **medição de uma execução que
aconteceu**, contra um comando que naquele momento realmente se chamava `quenching:skill:agent:new`.
A regra, declarada para que ela sobreviva à próxima renomeação: **o diretório se move, o arquivo de
casos é reescrito, `runs/**` fica byte-idêntico.** Uma medição histórica nomeia o comando como ele
foi invocado, e é exatamente isso que dá valor a guardá-la.

### `harness` é um estágio compartilhado e idempotente, com dois chamadores

`/docs:align` e `/claude:align` ambos invocam `quenching:claude:harness:align`, e ambos computam o
sinal de probe de harness gordo. O estágio é idempotente, então uma execução dupla dentro de `/align`
é no-op.

É uma duplicação consciente, tomada contra as duas alternativas:

- **Só `/claude:align` dirige** — um `/docs:align` bare pararia de convergir no trabalho de
  glossário que o harness cria, e fechar esse laço exigiria `/align`.
- **Só `/docs:align` dirige** — a fronteira de front fica decorativa, já que uma varredura de docs
  escreveria através de um comando do front claude.

`plugins/quenching/assets/references/align/sweep-doctrine.md` não declara nenhuma regra de dono único
por estágio, então isto não contradiz contrato nenhum. O custo é que o sinal de probe é computado em
dois corpos e pode derivar; a mitigação está em `## Risks`.

### A regra bare-vs-registry-name ganha um dono, em duas formas

Hoje ela está inline em `plugins/quenching/commands/docs/align.md` e
`plugins/quenching/commands/align.md`, e nenhum arquivo de referência é dono dela. Uma renomeação de
namespace é precisamente a mudança que pode violá-la em silêncio — uma invocação de estágio de um
conductor reescrita para a forma bare continua lendo-se corretamente e simplesmente para de resolver.

O dono **citável** é `plugins/quenching/assets/references/align/sweep-doctrine.md`: um corpo de
comando só pode citar `${CLAUDE_PLUGIN_ROOT}/assets/**`, nunca o `docs/` deste repositório, porque o
plugin é instalado sem ele (`plugin-layout.md` §*References are cited by absolute path* e §*A mold
cites nothing it does not also install*), e esse arquivo já é o contrato comportamental compartilhado
que `docs/standards/architecture/align-surface.md:19` nomeia. O dono **de standard** é
`docs/standards/naming/command-surface.md` §*Three citation forms*, que é onde um revisor procura a
regra de nomes e onde `correct-command-citation-form` já a escreveu.

Duas formas do mesmo texto é a regra sendo obedecida, não deriva — é a mesma divisão
plugin-versus-molde que `plugin-layout.md` §*A mold cites nothing it does not also install* já
abençoa explicitamente. Não "reconcilie" as duas.

### Sequenciamento — a dependência era real e está quitada

Este spec era **bloqueado pelo merge de `instrument-and-extend-skill-front`**: toda task restante
daquele spec caía em um arquivo que esta renomeação move, e renomear primeiro significaria resolver o
mesmo conflito sete vezes, contra tasks cujos `subject:` gravados apontam para caminhos que deixariam
de existir.

**O bloqueio caiu.** Aquele spec está em
`specs/archive/2026-07-25-instrument-and-extend-skill-front.md` com as 14 caixas marcadas,
`reviewed: 2026-07-27` e `merge: {strategy: merge-commit, commit: 4421185}`. O registro fica aqui
porque explica por que o sequenciamento importou, e para que um leitor futuro não reintroduza a espera.

O que resta de sequenciamento não é dependência de spec, é ordem interna de `## Tasks`: o contrato
citável antes de qualquer `git mv`, os movimentos antes das varreduras mecânicas, e o harness de
verificação por último, porque o check 3 custa uma sessão de agente cobrada e só deve ser pago quando
a superfície estiver final.
## Alternatives Considered

Alternativas de **forma inteira** — as que teriam mudado o formato do spec. As alternativas de uma
decisão isolada ficam em `## Design`.

### O nome do front

Interrogado depois de o resto do spec estar fechado, o que mudou a decisão: `automation` estava
escolhido e perdeu.

| Nome | Custo | O que compra | O que fecha | Veredito |
| --- | --- | --- | --- | --- |
| **`automation`** | zero sobre a forma escolhida | usa a palavra que o repositório já emprega para este território, em `docs/standards/automation/` e `assets/templates/automation/` | o plugin escreve `docs/standards/<front>/**` no alvo, e num repositório cujo produto **é** automação o nome disputa com o assunto do domínio | **rejeitada** — a colisão acontece no alvo, onde não há como desambiguar, e o alvo é o cliente deste plugin |
| **`agents`** | renomear o contexto `agent/` para `subagent/`, e reescrever a fronteira declarada em `docs/standards/agents/index.md` | vocabulário de indústria estável, ao contrário de `skill`, que o próprio Claude Code já remexeu | `agent/` é um dos quatro contextos, então front e artefato voltam a dividir uma palavra — o defeito deste spec com outro nome; e `docs/standards/agents/` já significa conduta, não artefato | **rejeitada** — seria um terceiro sentido para `agents` num repositório que já gastou um parágrafo de index para separar os dois primeiros |
| **`claude`** | reescrever `## Design` §1 e dois itens de `## Out of Scope` | o front é nomeado pela árvore que possui, como `docs` e `specs`; `assets/claude/` deixa de ser exceção; nenhum contexto divide o nome; não colide com domínio de alvo nenhum | expõe o nome a um eventual rename de `.claude/` pelo Claude Code | **escolhida** |

### A forma do spec

| Abordagem | Custo | O que compra | O que fecha | Veredito |
| --- | --- | --- | --- | --- |
| **Não fazer nada** — o front continua se chamando `skill` | zero | nada muda, e nenhum diff de 59 arquivos precisa ser revisado | mantém `skill` nomeando o front inteiro *e* um artefato dentro dele | **rejeitada** — o defeito é permanente e piora a cada artefato novo: `agent/` e `hook/` já se leem como sub-tipos de uma skill, e o quinto artefato herdaria a mesma leitura errada |
| **A menor coisa que funcionaria** — inserir só o segmento `command/` sob o front atual (`/skill:command:new`) | ~40 strings | remove a assimetria entre os contextos, que é o sintoma mais visível | o nome do front continua sendo o nome de um artefato, e `retire-skill-vocabulary` teria de abrir uma exceção para o segmento de caminho mais difícil de justificar — um permanente | **rejeitada** — arruma a hierarquia e deixa intacta a palavra de duplo sentido, que é a causa |
| **Renomear o front e manter verbos planos** — `/claude:new`, `/claude:agent-new`, `/claude:hook-new` | ~250 strings | um só nome de front, sem nenhum nível de aninhamento novo | reproduz "um tipo de artefato é o default" dentro do nome do verbo, exatamente a forma que este spec existe para remover | **rejeitada** — o hífen esconde a hierarquia que o separador `:` do Claude Code já expressa de graça |
| **Dividir em dois specs sequenciados** — (a) renomear o front e criar os contextos, (b) mover `/docs:harness` e dar dono à regra bare-vs-registry | dois branches, dois merges, dois concludes | cada merge fica menor e mais fácil de revisar sozinho | o segundo spec rebaseia por cima da reescrita que o primeiro fez dos **mesmos** 59 arquivos | **rejeitada** — é a alternativa que parece mais segura e é a mais cara: dividir multiplica justamente o conflito que ela existe para evitar, e `docs/standards/ci-cd/versioning-release.md` §*When the bump happens* já registra que dois specs em voo colidem nos seis arquivos de versão |
| **Um diff único: renomear o front, criar os quatro contextos e mover o harness** | ~278 strings em 59 arquivos, um branch | a árvore fica honesta em uma passada, e cada string errada erra exatamente uma vez | obriga a varredura de citações a ser mecânica e verificável, nunca manual | **escolhida** |

Sobre **comprar ou emprestar em vez de construir**: não há alternativa externa. O layout de
`commands/**` é imposto pelo Claude Code
(`docs/standards/architecture/plugin-layout.md` §`commands/**` is the only tree Claude Code
registers), e não existe ferramenta de terceiros que renomeie um namespace de comandos preservando
as citações. A varredura é `git mv` mais `grep`, e as duas já estão à mão.

### O `/docs:harness` precisa mesmo trocar de front?

A alternativa é deixá-lo em `/docs:harness` e apenas dar um dono à regra bare-vs-registry, o que
tiraria dois arquivos e ~36 strings do diff. Ela perde porque o argumento não é de simetria, é
contratual: `docs/standards/naming/command-surface.md` §*Namespaces are honest by artifact* diz que
"a command's namespace MUST match what it touches", e `/docs:harness` escreve `CLAUDE.md` e
`AGENTS.md` — arquivos que o Claude Code lê como instrução, que é o artefato do front `.claude/`, e
não o bundle OKF. Manter o comando sob `/docs:` é violação permanente de um standard
`authority: current`, e o próprio manual do front docs já trata esses arquivos como fora do bundle
(`plugins/quenching/assets/docs/QUENCHING.md:84` — "Exempt from OKF").
## Open Decisions

- **`skills.py` é renomeado, e os seus códigos de finding `sk-*` mudam?** É a ferramenta que verifica
  o front `claude` e carrega no nome do arquivo, nas findings e em todo consumidor de `--json` o
  substantivo que `retire-skill-vocabulary` está retirando. Os outros dois verificadores são nomeados
  pelos seus fronts — `specs.py` e `okf-validate.py` — então `skills.py` é o único que nomeia um
  artefato em vez do território que verifica. Decidido por: precificar a renomeação contra o fato de
  que os códigos `sk-*` aparecem em alvos instalados que este plugin não consegue reescrever.
  Qualquer resposta é aceitável; o que não é aceitável é registrá-la como neutra. Resolver antes de o
  grupo 1 de `## Tasks` começar.
- **A pasta de assunto `docs/standards/automation/` acompanha o front, e para qual nome?** É onde a
  colisão com automação de domínio de fato mora: o plugin escreve `docs/standards/<assunto>/**` no
  alvo, enquanto o namespace de comandos não sofre porque no alvo ele é sempre `/quenching:claude:*`,
  prefixado — `command-surface.md` §*Three citation forms*. Renomear o front não fecha isso, e é por
  isso que a pasta está em `## Out of Scope` com a incoerência declarada. Decidido por: contar, numa
  instalação real, se algum alvo tem assunto de produto disputando aquele nome, e pesar contra o
  custo de mover sete standards com `resource:` e links entrantes. Fora do escopo deste spec.
- **`retire-skill-vocabulary` fecha como superado, ou se estreita para a prosa de `docs/` que só ele
  encontrou?** Ele descobriu independentemente quatro referências obsoletas em `docs/standards/` e
  `docs/knowledge/glossary.md` que nenhuma renomeação de caminho alcança. Decidido por: conferir,
  agora que `## Tasks` existe, se a varredura de `docs/` está dentro dela — o grupo 4 diz que está.
  Se estiver, aquele spec é encerrado com `/specs:conclude --outcome abandoned` e a razão. **Este
  spec não fecha o irmão e não presume o resultado.**
- **Quem reescreve o texto `/skill:*` que já está instalado em repositórios-alvo?** `## Risks`
  §*Nada reescreve o que já foi instalado* aceita o risco; o que fica aberto é a saída. Três formas:
  (a) `/claude:align` passa a reescrever `docs/standards/automation/**` do alvo, o que é a violação
  de fronteira de front que este spec recusou em outro lugar; (b) `/docs:align` ganha um estágio de
  migração de vocabulário, o que põe conhecimento do front claude dentro do front docs; (c) nada é
  feito e o alvo lê instruções que nomeiam comandos inexistentes até que alguém rode o align que
  recopia o molde. Decidido por: contar, na primeira instalação real pós-merge, quantos arquivos de
  um alvo ficam de fato errados — se for só o trio de standards de molde, (c) é defensável; se
  alcançar o registro ou o `settings.json`, não é. Fora do escopo deste spec construir qualquer uma
  das três.
## Risks

Cada história de falha do premortem virou uma linha aqui, uma task em `## Tasks`, ou um corte em
`## Out of Scope`. As que não converteram em nada foram descartadas.

### `resource:` órfão em seis standards, e o bundle deixa de ser conforme

Seis docs de `docs/standards/**` carregam entradas `resource:` que nomeiam caminhos sob
`plugins/quenching/commands/skill/`: `quality/surface-verification.md:5`,
`architecture/align-surface.md:5`, `automation/session-evidence.md:5`,
`automation/skill-evaluation.md:5` e `automation/agents.md:5` (duas entradas na mesma linha). Depois
do `git mv` nenhum desses caminhos casa com nada em disco e `okf-validate.py` emite
`resource-unresolved`, que a entrada *Advisory finding* de `docs/knowledge/glossary.md` classifica
como WARN-**must-fix**, não advisory. O resultado é que todo `/docs:align` passa a reportar seis
achados que nada fecha.

**Mitigação:** a task que reescreve as entradas `resource:` enumera os seis caminhos, e
`## Validation` roda `okf-validate.py docs` exigindo zero `resource-unresolved` que nomeie um
caminho `commands/`. Probabilidade alta, detecção barata, custo de conserto depois do merge igual ao
custo de fazer certo agora — por isso é task e não risco aceito.

### Link quebrado no glossário e em cinco standards

`docs/standards/architecture/plugin-layout.md` §`{name}` is the owning command's path flattened
obriga `assets/references/skill-new/` a virar `assets/references/claude-command-new/` e
`assets/references/skill-eval/` a virar `assets/references/claude-command-eval/` — o nome da
pasta é o caminho do comando dono, achatado, e um nome de diretório que mente é proibido. Isso
quebra `docs/knowledge/glossary.md:90` (entrada *Cache trap*), que produz `glossary-broken-link`,
também WARN-must-fix, mais links em `plugin-layout.md:121`, `automation/skills.md:22` e `:121`,
`automation/hooks.md:87`, `automation/agents.md:59`, `automation/skill-evaluation.md:143` e
`plugins/quenching/README.md:488`.

**Mitigação:** o `git mv` de cada pasta de referência e a reescrita das suas citações são **uma
única task**, nunca duas, e `## Validation` carrega o `grep` que precisa voltar vazio.

### A renomeação pela metade é silenciosa

`docs/standards/architecture/plugin-layout.md` §*How a violation actually presents* já diz o pior:
um arquivo errado sob `commands/` não falha ao carregar — ele registra, paga o seu espaço na
listagem always-on e aparece no menu `/` como um comando que não faz nada. Uma citação
`${CLAUDE_PLUGIN_ROOT}/assets/references/skill-new/...` pendurada se comporta igual: o corpo do
comando roda, a citação não resolve, e a doutrina que ela deveria carregar simplesmente não chega.
Nada quebra; a superfície só fica quietamente errada, e um commit intermediário desta renomeação
está exatamente nesse estado.

**Mitigação:** `verification: per-section` (o bundle só é consistente na borda de um grupo de
tasks), cada mover-e-recitar em uma task só, e o `grep` de `## Validation` como invariante — é a
única assertiva que distingue "renomeado" de "renomeado pela metade".

### O invocador por registry name é a violação mais fácil de não ver

`plugins/quenching/commands/align.md` invoca `quenching:skill:align` pela ferramenta Skill.
Reescrito para a forma bare `/claude:align` ele continua lendo-se corretamente e simplesmente
para de resolver — é a razão pela qual `## Design` §*A regra bare-vs-registry-name ganha um dono*
existe. Há 71 strings `quenching:skill*` no repositório sujeitas a isso, e o número subiu porque
`correct-command-citation-form` converteu as citações bare para a forma prefixada: a varredura que
corrigiu uma classe de erro aumentou a superfície desta.

**Mitigação:** a regra ganha dono citável antes de qualquer `git mv` (grupo 1 de `## Tasks`), e
`## Validation` grepa `quenching:skill` além de `/skill:`.

### O harness de verificação fica vermelho, e o vermelho será lido como ruído

`plugins/quenching/assets/checks/functional-checks.sh` fixa `quenching:skill:agent:new` e
`quenching:skill:hook:new` como alvos de roteamento esperados e grepa por um `quenching-docs-align`
retirado. Depois da renomeação o check 3 fica vermelho. O perigoso não é a falha, é a leitura dela:
`CLAUDE.md` registra que **todo run vermelho que esse harness já produziu se rastreou a um defeito
do próprio harness, nenhum a uma regressão de superfície**, então um vermelho legítimo aqui é o mais
propenso a ser descartado como ruído — e o check 3 é opt-in (`--only 3`), então pode ficar meses sem
rodar.

**Mitigação:** as expectativas do probe são reescritas na mesma task que renomeia os comandos
`agent`/`hook`, e não numa task de "arrumar o harness" depois.

### Nada reescreve o que já foi instalado em repositórios-alvo

`.claude/QUENCHING.md` se salva: `commands/skill/align.md` recopia o manual quando a versão do banner
instalado é menor que a do plugin, e o lockstep de seis artefatos garante o bump em
`/specs:conclude`. Os moldes **não** se salvam. `docs/standards/automation/skills.md`, `agents.md` e
`hooks.md` de um alvo foram aplicados a partir de `assets/templates/automation/*-standard.md` por
inserção, e só quando ausentes (`commands/skill/new.md`), então nunca são recopiados: as citações
`/skill:*` espalhadas pelos sete moldes são corrigidas no plugin e continuam erradas para sempre em
todo alvo que já instalou. Nenhum detector existe para isso.

**ACCEPTED — e a decisão de como fechar fica em `## Open Decisions`.** A correção óbvia é
`/claude:align` reescrever `docs/standards/automation/**` do alvo, e isso é exatamente a violação de
fronteira de front que o próprio `## Design` §*`harness` é um estágio compartilhado* pesou e recusou.
Aceitar aqui é honesto porque o alvo continua funcionando — só lê instruções que nomeiam comandos
inexistentes — e porque a alternativa muda a arquitetura do plugin, não esta renomeação.

### `stale-doc` em todo standard cujo `resource:` a renomeação toca

`okf-validate.py` avisa quando o `timestamp` de um doc precede o último commit que tocou o seu
`resource:`. O bundle já carrega 14 desses avisos hoje; a renomeação acrescenta um por standard cujo
`resource:` nomeia um caminho movido.

**ACCEPTED — `stale-doc` é a única finding advisory do conjunto**, pela mesma entrada *Advisory
finding* do glossário, e as tasks que reescrevem cada standard já sobem o `timestamp` de tabela.
Sobrepõe-se a `narrow-the-stale-doc-trigger-to-content-drift`, que discute exatamente se esse
gatilho deveria disparar para mudança mecânica de caminho; este spec não resolve isso e não depende
da resposta.

### Colisão com quatro specs irmãos nos mesmos arquivos

Todos reescrevem `commands/**` ou `README.md` ao mesmo tempo que este:

- `restore-routing-info-on-docs-commands` (**`executing`**) reescreve as descrições dos nove
  comandos `/docs:*`, e uma delas é `/docs:harness` — o comando que este spec **move de front**. É a
  colisão mais direta do lote: se aquele spec mergear primeiro, a descrição reescrita muda de
  arquivo; se este mergear primeiro, ele reescreve uma descrição que o outro está reescrevendo.
- `retire-skill-vocabulary` retira o substantivo nos mesmos ~59 arquivos. `## Open Decisions` já
  pergunta se ele fecha como superado.
- `route-commands-without-always-on-descriptions` decide se descrições always-on continuam
  existindo. Se a resposta for não, o texto das descrições que esta renomeação reescreve deixa de
  existir na forma atual.
- `rewrite-readme-for-collapsed-surface` reescreve `plugins/quenching/README.md`, que carrega 40+
  ocorrências de `skill`.

**Mitigação:** este spec mantém a sua fronteira em **caminhos e nomes registrados**; não decide se
descrições always-on continuam existindo, não reescreve o README além das strings renomeadas, e não
fecha nenhum spec irmão. Quem mergear por último paga a reescrita mecânica no rebase, que é o custo
que a alternativa "dividir em dois specs" tornaria recorrente.
## Tasks

Cinco grupos, em ordem de dependência. Nenhuma task é marcada `[P]`: praticamente toda uma reescreve
citações espalhadas pelos mesmos 59 arquivos, então os conjuntos `files:` não são disjuntos e serial é
a única execução correta.

A regra que decide o formato de cada task dos grupos 2 e 3: **mover e recitar é UMA task, nunca duas.**
Um commit intermediário que moveu o arquivo e não reescreveu as citações não falha em nada — ele fica
quietamente errado (`## Risks` §*A renomeação pela metade é silenciosa*), então a task só é ticável
quando o `grep` da sua própria string antiga volta vazio.

**Nenhuma task cita uma contagem.** Os números inline da versão anterior deste spec envelheceram em
quatro dias e mentiam por quase o dobro — o `verify:` de cada task é a autoridade, e o único número
que fica é o invariante que `## Validation` checa: **26 comandos**. A task 1.1 grava o baseline vivo.

Cada texto de checkbox cabe em uma linha de propósito: `specs.py next` entrega ao executor a primeira
linha e só ela, então uma task que continua na linha seguinte chega pela metade.

### 1. Contrato e decisão, antes de qualquer movimento

- [ ] 1.1 Registrar o baseline das cinco assertivas de `## Validation` na árvore intacta — hits, arquivos, warnings de bundle, findings `sk-*` atuais — para que "não piorou" seja verificável
      verify: git grep -nE '/skill:|quenching:skill|commands/skill|references/skill-|evals/skill|docs:harness|references/docs-harness' -- ':!specs/' ':!plugins/quenching/assets/evals/*/*/*/runs/' | wc -l
- [ ] 1.2 Resolver a primeira pergunta de `## Open Decisions` (renomear `skills.py` e os códigos `sk-*`?) e gravar a resposta com a razão na seção, incluindo a inconsistência aceita se a resposta for não
      files: specs/plans/2026-07-27-restructure-claude-front-namespace.md
- [ ] 1.3 Dar dono citável à regra bare-vs-registry-name em `assets/references/align/sweep-doctrine.md` e trocar os dois enunciados inline por uma citação `${CLAUDE_PLUGIN_ROOT}` desse dono
      files: plugins/quenching/assets/references/align/sweep-doctrine.md, plugins/quenching/commands/docs/align.md, plugins/quenching/commands/align.md
      pattern: plugins/quenching/assets/references/align/convergence.md
      verify: grep -c 'sweep-doctrine.md' plugins/quenching/commands/docs/align.md plugins/quenching/commands/align.md

### 2. A árvore de comandos — sete movimentos, cada um com as suas citações

- [ ] 2.1 Mover `commands/skill/align.md` para `commands/claude/align.md` e reescrever toda citação de `/skill:align` e `quenching:skill:align`, inclusive a invocação por registry name em `commands/align.md`
      verify: git grep -n '/skill:align\|quenching:skill:align' -- ':!specs/'
- [ ] 2.2 Mover `commands/skill/new.md` para `commands/claude/command/new.md` e reescrever toda citação de `/skill:new`, inclusive as dos textos de remédio de `assets/bin/skills.py`
      verify: git grep -n '/skill:new' -- ':!specs/'
- [ ] 2.3 Mover `commands/skill/eval.md` para `commands/claude/command/eval.md` e reescrever toda citação de `/skill:eval`, inclusive as de `assets/checks/functional-checks.sh` e de `docs/standards/quality/surface-verification.md`
      verify: git grep -n '/skill:eval' -- ':!specs/'
- [ ] 2.4 Mover `commands/skill/retro.md` para `commands/claude/command/retro.md` e reescrever toda citação de `/skill:retro`, inclusive a de `docs/standards/ci-cd/versioning-release.md` §The seventh file
      verify: git grep -n '/skill:retro' -- ':!specs/'
- [ ] 2.5 Mover `commands/skill/agent/new.md` para `commands/claude/agent/new.md` e reescrever `/skill:agent:new` e `quenching:skill:agent:new`, inclusive as de `assets/bin/skills.py`
      verify: git grep -n 'skill:agent:new' -- ':!specs/'
- [ ] 2.6 Mover `commands/skill/hook/new.md` para `commands/claude/hook/new.md` e reescrever `/skill:hook:new` e `quenching:skill:hook:new`, inclusive as de `assets/bin/skills.py`
      verify: git grep -n 'skill:hook:new' -- ':!specs/'
- [ ] 2.7 Mover `commands/docs/harness.md` para `commands/claude/harness/align.md` e reescrever toda citação de `/docs:harness` e `quenching:docs:harness`, nas duas formas, preservando o sentido do site de `commands/docs/align.md` que usa o nome como exemplo da regra bare-vs-registry
      verify: git grep -n 'docs:harness' -- ':!specs/'
- [ ] 2.8 Confirmar que `commands/skill/` não existe mais e que a superfície mantém 26 comandos sem findings
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json

### 3. As árvores que a renomeação arrasta consigo

- [ ] 3.1 Mover `assets/references/skill-new/` para `assets/references/claude-command-new/` e reescrever as suas citações, inclusive o link *Cache trap* de `docs/knowledge/glossary.md:90`, que viraria `glossary-broken-link`
      verify: git grep -n 'references/skill-new' -- ':!specs/'
- [ ] 3.2 Mover `assets/references/skill-eval/` para `assets/references/claude-command-eval/` e reescrever as suas citações, inclusive `plugin-layout.md:121` e `automation/skill-evaluation.md:143`
      verify: git grep -n 'references/skill-eval' -- ':!specs/'
- [ ] 3.3 Mover `assets/references/docs-harness/` para `assets/references/claude-harness-align/` e reescrever as suas citações
      verify: git grep -n 'references/docs-harness' -- ':!specs/'
- [ ] 3.4 Mover `assets/evals/skill/agent/new/` para `assets/evals/claude/agent/new/`, reescrever `evals.json` e deixar `runs/` byte-idêntico
      verify: git diff --stat -- plugins/quenching/assets/evals
- [ ] 3.5 Mover `assets/evals/skill/hook/new/` para `assets/evals/claude/hook/new/` sob a mesma regra e confirmar que `assets/evals/skill/` não existe mais
      verify: git grep -n 'evals/skill' -- ':!specs/'

### 4. As varreduras mecânicas que não são movimento de caminho

- [ ] 4.1 Reescrever as entradas `resource:` que nomeiam caminhos movidos e subir o `timestamp` em `docs/standards/quality/surface-verification.md`, `docs/standards/architecture/align-surface.md`, `docs/standards/automation/session-evidence.md`, `docs/standards/automation/skill-evaluation.md` e `docs/standards/automation/agents.md` (duas entradas na mesma linha)
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
- [ ] 4.2 Reescrever as citações `/skill:*` nos sete moldes de `assets/templates/automation/`, mantendo a regra de que um molde só cita o que o mesmo align instala junto e sem renomear a pasta, que é nomeada pelo assunto do bundle
      files: plugins/quenching/assets/templates/automation/
      verify: git grep -n '/skill:' -- plugins/quenching/assets/templates
- [ ] 4.3 Atualizar os quatro manuais de operador (`assets/claude/QUENCHING.md`, `assets/docs/QUENCHING.md`, `assets/specs/QUENCHING.md`, `docs/QUENCHING.md`), movendo a linha do harness do manual do front docs para o do front claude
      verify: git grep -n '/skill:\|docs:harness' -- '*QUENCHING.md'
- [ ] 4.4 Atualizar `plugins/quenching/README.md`, `assets/README.md`, `assets/templates/README.md`, o `CLAUDE.md` da raiz e a descrição do plugin em `plugin.json` e `marketplace.json` — o texto que um humano lê antes de instalar
      verify: git grep -n '/skill:' -- '*.json' '*.md' ':!specs/' ':!plugins/quenching/commands/'
- [ ] 4.5 Retirar o substantivo "skill" onde se quer dizer "command" na prosa de `docs/standards/` e de `docs/knowledge/glossary.md`, sem renomear `automation/skills.md` nem `automation/skill-evaluation.md` antes de 1.2 estar decidida

### 5. Provar a regra e provar a superfície

- [ ] 5.1 Reescrever as expectativas do probe em `assets/checks/functional-checks.sh` — alvos de roteamento, grep de nome retirado, bloco WHO RUNS THIS — para que um vermelho do check 3 volte a significar regressão de superfície
      files: plugins/quenching/assets/checks/functional-checks.sh
- [ ] 5.2 Escrever `docs/standards/naming/command-surface.md` com o front `claude`, os quatro contextos, a regra verbo-de-front versus verbo-de-artefato e a regra bare-vs-registry-name ao lado do §Three citation forms que já existe (`authority: current`, provado por este branch)
      files: docs/standards/naming/command-surface.md
- [ ] 5.3 Escrever `docs/standards/architecture/align-surface.md` com `/claude:align` na tabela 1×4 e o verificador do front nomeado conforme a decisão de 1.2 (`authority: current`)
      files: docs/standards/architecture/align-surface.md
- [ ] 5.4 Rodar as assertivas 1 a 4 de `## Validation` e conferir contra o baseline de 1.1: 26 comandos, nenhuma finding must-fix nova, `git grep` vazio, cinco versões iguais, três selftests limpos
- [ ] 5.5 Rodar `functional-checks.sh` e depois `--only 3`, uma única vez, com a superfície já final — é a assertiva cobrada, e um `exit 2` não é um pass
      verify: plugins/quenching/assets/checks/functional-checks.sh --only 3
## Discoveries

- O item de ## Out of Scope 'Prefixar citações voltadas a humanos com quenching:' foi fechado citando commands/docs/align.md:237, que declarava a forma bare como 'what a human types'. Essa alegação era falsa com o plugin instalado como plugin e foi corrigida por correct-command-citation-form (2026-07-31): três formas, e a bare resolve apenas onde o comando mora no .claude/commands/ do repo-alvo. commands/** e assets/references/** já foram varridos e o finding sk-bare-citation (WARN) guarda a regra. O item precisa ser reavaliado sobre a evidência nova, não sobre a frase antiga. -> folded: ## Out of Scope — o item continua fora de escopo, mas a razão passa a ser "o trabalho já foi feito por outro spec" em vez de "a forma bare é a correta em prosa"; e o baseline herdado (326 hits/61 arquivos) foi remedido para 278/59, com a assertiva 3 de ## Validation passando a grepar `docs:harness` sem a âncora `/`, para alcançar as 18 citações já convertidas para a forma prefixada.
