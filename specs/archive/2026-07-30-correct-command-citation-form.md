---
slug: correct-command-citation-form
title: Corrigir a forma de citação de comando — bare versus prefixada pelo plugin
verification: per-section
approved: {date: 2026-07-31}
branch: {base: main, work: claude/correct-command-citation-form-044087}
reviewed: {date: 2026-07-31}
merge: {strategy: merge-commit, subject: "plan/correct-command-citation-form: merge (merge-commit)"}
outcome: done
---

# Corrigir a forma de citação de comando — bare versus prefixada pelo plugin

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

Uma recomendação de próximo comando saiu como `/specs:develop` quando a forma que resolve é
`/quenching:specs:develop`. Este spec não trata do erro pontual: trata da frase do plugin que o
produziu, e das 687 citações que ela autoriza.

Por onde entrar. `## Problem` mostra a frase-raiz (`commands/docs/align.md:237`), a evidência de que
metade dela é falsa, e o alcance medido; `## Design` Decisão 1 é a correção conceitual — o eixo não é
humano-versus-ferramenta, é **de onde o comando vem** — e a Decisão 4 explica por que as 75 citações
dentro de `description:` ficam deliberadamente de fora, por aritmética de orçamento e não por
descuido. `## Risks` guarda a falha mais provável (o sweep vazar para o frontmatter) com a mitigação
mecânica que a pega.

O que ler antes de aprovar: a primeira questão de `## Open Decisions`. A evidência de que a forma bare
não resolve é **indireta** — não existe `.claude/commands/` neste repo, e o humano digitou a forma
prefixada — e há um teste de um minuto que a fecha. Se a forma bare resolver, o núcleo do spec segue
correto e o sweep vira preferência; a ordem das tasks põe a parte cara por último exatamente por isso.

## Problem

Uma recomendação de próximo comando sai errada: `/specs:develop` em vez de `/quenching:specs:develop`.
A causa não é o modelo improvisando — é o corpo do próprio plugin ditando a forma bare, e uma alegação
`authority`-nenhuma sustentando 687 citações.

**A frase-raiz**, em `plugins/quenching/commands/docs/align.md:237`:

> "A bare `/docs:harness` is what a human types, not what the Skill tool resolves."

Ela declara **duas** formas: bare = o que o humano digita · prefixada = o que o `Skill` tool resolve.
`commands/align.md:157` obedece corretamente (`quenching:skill:align` para a ferramenta).

**A metade "what a human types" é falsa quando o plugin é instalado como plugin.** Medido nesta
árvore em 2026-07-30: não existe `.claude/commands/` — só `settings.json` e um `hooks/`. Os 26
comandos vêm todos do plugin, portanto são namespaced `/quenching:<front>:<verbo>` e não há nada
para uma forma bare resolver. A sessão que produziu este spec foi aberta pelo humano digitando
`/quenching:specs:execute`, e a recomendação bare que o modelo devolveu foi copiada literalmente da
linha `Not for: … → /specs:create` da `description` de `commands/specs/develop.md`.

**Alcance**, medido em 2026-07-30 com `grep -roE '/(docs|specs|skill):[a-z:-]+'`:

| Onde | Citações bare |
| --- | --- |
| `commands/**` | 336 (75 delas dentro de `description:`) |
| `assets/references/**` | 183 |
| `README.md` | 102 |
| `assets/docs/QUENCHING.md` | 57 |
| `CLAUDE.md` | 9 |
| forma prefixada em todo o repo | **0** |

**Nada checa isso.** `grep -n 'prefix' assets/bin/skills.py` não devolve regra alguma — é exatamente o
padrão que `docs/standards/quality/bundle-verification.md` nomeia: um invariante repetido em mais de
dois lugares é devido a um check determinístico ou a uma lacuna aceita registrada, nunca a mais prosa.

**O agravante: a questão já foi encerrada com base na frase errada.** O spec irmão
`restructure-claude-front-namespace` (stage `ready`) tem em `## Out of Scope`: "Prefixar citações
voltadas a humanos com `quenching:`. … Não careciam: o `/skill:new` bare é a forma correta em prosa,
**declarada em `commands/docs/align.md:237`**." Corrigir a frase reabre aquele item — este spec não o
duplica, ele lhe devolve a evidência.

## Proposal

- A alegação de `commands/docs/align.md:237` passa a distinguir **três** formas, não duas:
  - `quenching:docs:harness` — o que o `Skill` tool resolve;
  - `/quenching:docs:harness` — o que o humano digita **com o plugin instalado**;
  - `/docs:harness` — correto **apenas** quando o comando mora no `.claude/commands/` do repo-alvo.
- `docs/standards/naming/command-surface.md` §The path IS the identity deixa de mapear
  `commands/specs/develop.md → /specs:develop` como se fosse a forma digitável, e passa a carregar as
  três formas com a condição de cada uma. É o mapeamento que todo corpo futuro copia, então é ele que
  para de gerar citações erradas.
- `skills.py` ganha **um** finding para citação de comando do plugin sem prefixo em contexto de
  hand-off, para que o sweep seja verificável e não regrida. Nasce em WARN, nunca em ERROR
  (`bundle-verification.md`).
- O sweep corrige os corpos de `commands/**` e `assets/references/**` **fora das `description:`**, que
  ficam para depois pelo motivo aritmético em `## Risks`.
- O achado volta para `restructure-claude-front-namespace` como discovery, reabrindo o item de
  `## Out of Scope` que foi fechado citando a frase corrigida aqui.

## Out of Scope

- **As 75 citações dentro de `description:`.** São always-on e o teto de contexto já estourou —
  ver `## Risks`. Ficam para o spec `route-commands-without-always-on-descriptions`, que é dono do
  orçamento; prefixá-las aqui pioraria um número que aquele spec existe para baixar.
- **`README.md` (102) e `assets/docs/QUENCHING.md` (57).** São material de produto que viaja para
  repos-alvo, onde a forma correta depende de como o plugin foi instalado. A regra escrita aqui é o
  que permite decidir cada site depois; aplicá-la a eles antes da regra existir é adivinhação.
- **A renomeação `/skill` → `/automation`.** É o assunto próprio de
  `restructure-claude-front-namespace`. Este spec não renomeia namespace nenhum.
- **Resolver o estouro de orçamento de contexto.** Medido, citado como risco, e de outro dono.
- **Verificar por execução que a forma bare falha.** Não há como um comando testar a resolução de um
  slash command; a evidência é a ausência de `.claude/commands/` mais o que o humano digitou. Ver
  `## Open Decisions`.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/naming/command-surface.md` — emenda, mantendo `authority: current`: §The path IS
  the identity passa a carregar as três formas de citação e a condição de cada uma, em vez do
  mapeamento de duas que hoje autoriza a forma bare como digitável.

### Standards at `authority: background` this spec may resolve

- none — nenhum standard `background` deste bundle trata de nomeação de comando ou de citação, e este
  trabalho não prova nenhum deles.

### Product code this spec expects to touch

- `plugins/quenching/commands/docs/align.md` — a frase da linha 237, a raiz da alegação
- `plugins/quenching/assets/bin/skills.py` — o finding novo e o seu caso no `selftest`
- `plugins/quenching/commands/**` — as citações bare em prosa de hand-off, **fora** das
  `description:` (261 dos 336 sites)
- `plugins/quenching/assets/references/**` — as 183 citações bare
- `specs/plans/2026-07-27-restructure-claude-front-namespace.md` — uma linha de discovery, escrita por
  `specs.py discover`, nunca à mão

## Validation

Tudo determinístico, rodado da raiz do repo. Nenhuma sessão de agente é gerada: um spec sobre a forma
de uma citação não paga check faturado para se provar.

- `python3 plugins/quenching/assets/bin/skills.py selftest` → PASS, com o caso novo do finding.
- `python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json` →
  `"commands": 26`, `"findings": []`. A identidade da superfície não muda: nenhum arquivo é criado,
  removido ou renomeado.
- `python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json` → exit 0.
- **O sweep, contado.** Antes:
  `grep -roE '/(docs|specs|skill):[a-z:-]+' plugins/quenching/commands/ plugins/quenching/assets/references/ | wc -l`
  devolve **519**. Depois, as citações restantes fora de `description:` devem ser **0**, e
  `grep -c '^description:' -r` mostra que as 75 de `description:` seguem intactas — o corte que
  `## Out of Scope` declara.
- **O orçamento não sobe:**
  `python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching budget --json` → o `total`
  deve ser **idêntico** ao de antes, porque nenhuma `description` é tocada. Um total maior significa
  que o sweep vazou para dentro do frontmatter, que é a falha que `## Risks` prevê.
- `python3 plugins/quenching/assets/hooks/okf-validate.py docs` → `0 error(s)`.
- `python3 plugins/quenching/assets/bin/specs.py validate --json` → sem finding novo.

**Nenhum bump de versão faz parte desta validação** — o lockstep se move uma vez, em
`/quenching:specs:conclude`.

## Design

### Decisão 1 — três formas, não duas

A alegação atual não está errada por metade: ela está errada por **faltar um eixo**. Bare versus
prefixada não é humano-versus-ferramenta, é **de onde o comando vem**. Um comando do
`.claude/commands/` do repo-alvo é bare para o humano; um comando de plugin é prefixado para os dois,
com `/` na frente para quem digita e sem `/` para o `Skill` tool. Escrever isso como três casos com a
condição de cada um é o que faz cada um dos 519 sites decidível sem julgamento.

### Decisão 2 — a regra antes do sweep

Corrigir 519 citações antes de corrigir a frase que as autoriza produz um repo que contradiz o
próprio corpo, e o próximo comando escrito volta a citar bare. Por isso a ordem das tasks é
frase → standard → check → sweep, e não o contrário.

### Decisão 3 — o check nasce em WARN, e é o que substitui a prosa

`bundle-verification.md` proíbe um check nascer em ERROR, e o seu corolário manda **cortar** a prosa
que um check substitui. Aqui a prosa a cortar é a própria frase de duas formas: depois do check, o
standard é o dono único da regra e `align.md` cita em vez de reafirmar. Sem o check, este spec seria
mais uma repetição de um invariante — exatamente o que aquele standard diz não resolver nada.

### Decisão 4 — as `description:` ficam de fora por aritmética, não por preguiça

`route-commands-without-always-on-descriptions` mediu `total 12875 · ceiling 12726 · exit 1`: o teto
já está estourado em 149. As 75 citações em `description:` custam ~10 caracteres cada para prefixar,
~750 caracteres, ~190 tokens — sobre um orçamento que já falha. Corrigi-las aqui tornaria pior o
número que o spec vizinho existe para baixar, e as duas mudanças brigariam no mesmo arquivo. A
fronteira é declarada em `## Out of Scope` e medida em `## Validation`.

### Contratos que este desenho não pode contradizer

- `docs/standards/quality/bundle-verification.md` — nenhum check novo em ERROR; a prosa substituída é
  cortada, não mantida.
- `docs/standards/naming/command-surface.md` — o path continua sendo a identidade; este spec muda
  como a identidade é **citada**, nunca como ela é derivada.
- `docs/standards/architecture/plugin-layout.md` — nenhum comando, hook ou agente é criado.
- A regra do `CLAUDE.md`: nada de `context: fork` nos comandos de varredura tocados.

## Alternatives Considered

| Abordagem | O que compra | Por que perdeu |
| --- | --- | --- |
| **A — só corrigir a frase e o standard** (a menor coisa que funciona) | a regra fica certa e nenhum corpo novo erra | **não perdeu — é o núcleo desta entrega.** O que sobra é que os 519 sites existentes seguem ditando a forma errada a cada leitura |
| **B — frase + standard + check + sweep** (recomendada) | a regra certa, os sites corrigidos, e um check que impede a regressão | nada: o corte das `description:` é declarado, medido e de outro dono |
| **C — reabrir `restructure-claude-front-namespace` e fazer tudo lá** | um dono só para nomeação de comando | aquele spec é dono de uma **renomeação de namespace**; enxertar nele uma correção de citação atrasa um `ready` de assunto diferente. A evidência vai para lá como discovery, que é o que ele precisa |
| **D — não fazer nada** | zero | o repo continua ensinando a forma que não resolve, e a alegação falsa segue de pé como autoridade que já fechou a discussão de um spec |

**Recomendação: B.** A é honesta e insuficiente; C confunde dois assuntos num spec já pronto; D deixa
uma alegação falsa governando 687 sites.

## Open Decisions

- **A forma bare realmente falha, ou apenas não é a canônica?** Não verificado por execução, e
  deliberadamente fora do escopo: nenhum comando consegue testar a resolução de um slash command. A
  evidência é indireta e forte — não existe `.claude/commands/` neste repo, e o humano digitou
  `/quenching:specs:execute`. **Como se decide:** digitar `/specs:develop` numa sessão deste repo e
  observar se resolve. Se resolver, a Decisão 1 continua correta (a forma prefixada segue sendo a
  canônica e sempre válida) mas o sweep vira preferência em vez de correção, e a prioridade cai.
- **O check deve pegar `assets/references/**` também, ou só `commands/**`?** `skills.py` hoje lê
  `commands/**`; alcançar `assets/` amplia o que a ferramenta varre. **Como se decide:** pela contagem
  — 183 dos 519 sites estão em `assets/`, então um check restrito a `commands/` deixa 35% do sweep sem
  rede. Decidir junto da task 3.1.
- **`README.md` e `QUENCHING.md` viram um terceiro caso?** Eles descrevem o produto para quem ainda
  não instalou. **Como se decide:** depois da regra escrita, perguntando se o leitor daquele texto já
  tem o plugin instalado. Fica para quem tocar naqueles arquivos.

## Risks

- **O sweep vaza para dentro das `description:` e piora um orçamento que já falha.** É a falha mais
  provável, porque as 75 citações moram no mesmo arquivo que as outras 261 e um `sed` amplo não
  distingue frontmatter de corpo. `ACCEPTED — a mitigação é mecânica`: `## Validation` exige que
  `skills.py budget --json` devolva um `total` **idêntico** ao de antes; qualquer aumento é o vazamento.

- **A alegação corrigida pode estar errada na direção oposta.** Se a forma bare resolver, o texto novo
  não fica falso — ele continua descrevendo três formas reais — mas o sweep terá custado 519 edições
  por preferência. `ACCEPTED — registrado como a primeira questão de ## Open Decisions`, com o teste de
  um minuto que a fecha, e a ordem das tasks põe frase e standard antes do sweep justamente para que a
  parte cara seja a última a ser paga.

- **Aterrissagem parcial entre `commands/**` e `assets/references/**`.** Nada cruza a consistência
  entre os dois: `doctor` e `lint` leem `commands/**`, não `assets/`. O sintoma seria um corpo citando
  a forma prefixada e a referência que ele cita ainda ensinando a bare. `ACCEPTED`: é exatamente o que
  o finding da task 3.1 existe para cobrir, e é por isso que a segunda questão de `## Open Decisions`
  precisa ser decidida antes do sweep.

- **Sobreposição com `restructure-claude-front-namespace` (ready).** Se aquele spec renomear
  `/skill:` → `/automation:`, cada citação tocada aqui muda de novo. `ACCEPTED — o custo é uma edição,
  não um conflito`: as citações erram uma vez após aquela renomeação, como o próprio spec já
  contabilizou, e este spec não presume o resultado dela. A ordem entre os dois é escolha humana.

- **Sobreposição com `route-commands-without-always-on-descriptions` (ready).** Os dois tocam
  `description:`; este declara não tocar. `ACCEPTED e medido`: a fronteira está em `## Out of Scope` e
  é verificada pelo `total` inalterado do `budget`.

## Handoff

Estado da árvore após o último commit (`f753b5d`), na branch `claude/correct-command-citation-form-044087`:

- **A regra está escrita em dois lugares e cada um sabe o seu papel.** `docs/standards/naming/command-surface.md` §The path IS the identity é a sede (tabela das três formas com a condição de cada uma); `commands/docs/align.md` e `commands/align.md` carregam a versão condensada porque o corpo viaja para repos-alvo, onde o `docs/` deste repo não existe.
- **O check é `sk-bare-citation` (WARN), em `skills.py`.** Alcança `commands/**` e `assets/references/**` — decidido pela contagem, 183 dos 519 sítios estavam em `assets/`. Só dispara quando `<root>/.claude-plugin/plugin.json` existe: num `.claude/` de repo-alvo a forma bare é a correta e o check fica mudo. Lê o corpo **após** o frontmatter, então `description:` está fora por construção, não por regex.
- **O sweep está completo nos dois trechos declarados**: 0 citações bare no corpo, 79 intactas dentro de `description:` (`## Out of Scope`).
- **O `total` do budget não se moveu: 12875 antes e depois.** O `budget` sai com exit 1 porque o teto (12726) já estava estourado antes deste trabalho — é o número que `route-commands-without-always-on-descriptions` existe para baixar, não uma regressão daqui.
- **Dois sítios precisaram de escrita à mão depois do sweep mecânico**, porque neles a forma bare é o *objeto do discurso* e não uma citação: `commands/docs/align.md` §6 e `commands/align.md` §3. Ambos agora usam a forma genérica `/<front>:<verb>`, que não casa o regex do check.
- **Nada de versão foi tocado** — o lockstep se move uma vez, em `/quenching:specs:conclude`.
- **A evidência voltou para `restructure-claude-front-namespace`** como discovery: o item de `## Out of Scope` daquele spec foi fechado citando a frase que este corrigiu.

## Tasks

Serial, sem `[P]`: o grupo 2 depende da regra que o 1 escreve, o 3 depende dos dois, e o 4 mede o
resultado dos três. A ordem frase → standard → check → sweep é a `## Design` Decisão 2.

### 1. A regra

- [x] 1.1 Trocar a frase de duas formas de `align.md:237` pelas três formas, com a condição de cada uma
      files: plugins/quenching/commands/docs/align.md
      verify: grep -c 'quenching:docs:harness' plugins/quenching/commands/docs/align.md
      subject: plan/correct-command-citation-form: 1.1 três formas de citação em align.md
- [x] 1.2 Emendar `docs/standards/naming/command-surface.md` §The path IS the identity com as três formas, mantendo `authority: current`
      files: docs/standards/naming/command-surface.md
      pattern: docs/standards/naming/command-surface.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs | grep -q '0 error(s)'
      subject: plan/correct-command-citation-form: 1.2 três formas em command-surface.md

### 2. O check

- [x] 2.1 Decidir e implementar o alcance do finding — `commands/**` só, ou também `assets/references/**` — conforme a segunda questão de `## Open Decisions`
      files: plugins/quenching/assets/bin/skills.py
      subject: plan/correct-command-citation-form: 2.1 alcance do check inclui assets/references
- [x] 2.2 Acrescentar o finding em WARN para citação de comando do plugin sem prefixo em prosa de hand-off, ignorando `description:`
      files: plugins/quenching/assets/bin/skills.py
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json
      subject: plan/correct-command-citation-form: 2.2 finding sk-bare-citation em WARN
- [x] 2.3 Acrescentar o caso ao `selftest` e provar que uma `description:` com citação bare NÃO dispara
      files: plugins/quenching/assets/bin/skills.py
      verify: python3 plugins/quenching/assets/bin/skills.py selftest
      subject: plan/correct-command-citation-form: 2.3 caso de selftest para sk-bare-citation

### 3. O sweep

- [x] 3.1 Corrigir as citações bare nos corpos de `commands/**`, fora das `description:`
      files: plugins/quenching/commands
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json
      subject: plan/correct-command-citation-form: 3.1 sweep dos corpos de commands/**
- [x] 3.2 Corrigir as 183 citações bare em `assets/references/**`
      files: plugins/quenching/assets/references
      subject: plan/correct-command-citation-form: 3.2 sweep de assets/references/**
- [x] 3.3 Devolver a evidência a `restructure-claude-front-namespace` por `specs.py discover`, reabrindo o item de `## Out of Scope`
      files: specs/plans/2026-07-27-restructure-claude-front-namespace.md
      subject: plan/correct-command-citation-form: 3.3 discovery em restructure-claude-front-namespace

### 4. A prova

- [x] 4.1 Rodar o bloco inteiro de `## Validation` e registrar cada saída, incluindo o `total` do budget inalterado
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching budget --json
      subject: plan/correct-command-citation-form: 4.1 bloco de Validation registrado

## Outcome

**done** — mergeada em `main` por merge-commit `--no-ff`, então os nove `subject:` registrados nas tasks continuam resolvíveis por `git log --grep` indefinidamente.

**O que entregou.** A alegação de duas formas que governava 687 citações foi substituída pela regra de três, cujo eixo é *de onde o comando vem* e não quem lê. A sede é `docs/standards/naming/command-surface.md` §The path IS the identity; os corpos de comando carregam a versão condensada porque viajam para repos-alvo, onde o `docs/` deste repo não existe. O check `sk-bare-citation` (WARN) impede a regressão, alcança `commands/**` e `assets/references/**`, e só fala numa superfície que carrega `.claude-plugin/plugin.json` — num `.claude/` de repo-alvo a forma bare é a correta e ele fica mudo. O sweep zerou as citações bare nos corpos das duas árvores.

**O que ficou de fora, e por quê.** As 79 citações dentro de `description:` (a spec estimava 75; 79 é a medição) seguem intactas — são always-on e o teto de contexto já estava estourado antes deste trabalho, o que torna elas propriedade de `route-commands-without-always-on-descriptions`. O `total` do budget mediu 12875 antes e 12875 depois, que é a prova mecânica de que o sweep não vazou para o frontmatter. `README.md` (102) e `assets/docs/QUENCHING.md` (57) também ficaram: descrevem o produto para quem ainda não instalou, e a regra escrita aqui é justamente o que permite decidir cada sítio depois.

**O que o próximo leitor precisa saber.**

1. **A `## Open Decisions` 1 continua aberta.** Ninguém verificou por execução que a forma bare *falha* — a spec declarou isso fora de escopo e a evidência segue indireta (não existe `.claude/commands/` neste repo, e o humano digitou a forma prefixada). Se ela resolver, nada do texto novo fica falso, mas os 519 sítios terão sido preferência e não correção.
2. **Um bug pré-existente foi achado na revisão da branch e deliberadamente não consertado aqui.** No modo texto, todo finding do `skills.py lint` imprime `-` onde deveria vir o comando: `report_findings` usa `label_key="skill"` por padrão, mas os findings do lint carregam a chave `command`. Atinge os dez códigos anteriores tanto quanto o novo; o modo `--json` está correto. É escopo de outra spec.
3. **Dois sítios precisaram de escrita à mão depois do sweep mecânico**, porque neles a forma bare é o *objeto do discurso* e não uma citação: `commands/docs/align.md` §6 e `commands/align.md` §3. Ambos passaram a usar a forma genérica `/<front>:<verb>`, que não casa o regex do check. Qualquer sweep futuro sobre prosa herda essa armadilha.
4. **A evidência voltou para `restructure-claude-front-namespace`** como discovery: o item de `## Out of Scope` daquele spec foi fechado citando a frase que este corrigiu, e precisa ser reavaliado sobre a evidência nova.

**Destilado no conclude.** O item 3 acima virou um standard: `docs/standards/quality/prose-sweeps.md` (`authority: current`) — o que um sweep mecânico sobre prosa corrompe, por que o checker escrito para guardá-lo reporta esses sítios como limpos, e a forma-placeholder que sobrevive aos dois.

**Nenhum bump de versão foi feito**, por decisão do humano no passo 5, contra o que `docs/standards/ci-cd/versioning-release.md` exige do merge. As sete versões seguem em `4.4.2` e este merge não reivindica release. O próximo spec a concluir bumpa por dois.
