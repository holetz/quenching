---
slug: fix-github-backend-tasks-fidelity
title: "Fidelidade do documento no backend github — grupos de task, títulos e o cap de corpo"
verification: per-section
branch: {base: main, work: plan/fix-github-backend-tasks-fidelity}
approved: {date: 2026-08-02}
---

# Fidelidade do documento no backend github — grupos de task, títulos e o cap de corpo

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
     *(`standards/agents/communication.md` owns that language rule for a repo whose bundle has
     one. This template states it self-contained rather than citing it: `/specs:align` is native
     and installs here into repos that never adopted the bundle, where that path resolves to
     nothing.)*

     MOMENT. Each section belongs to one of three moments on the spec's timeline: `decision`
     (the human, deciding whether to build), `build` (the executor, in step 4 of
     `/specs:execute`), `close` (`/specs:conclude`, at archive time). `## Discoveries` belongs
     to none of them — captured indiscriminately while building, resolved later by
     `/specs:develop`'s triage sweep on its own schedule. An orchestrator sends an executor
     exactly the `build` set; that is what lets one file serve every moment without bloating
     agent context. -->

## Overview

Esta spec conserta a **única obrigação** que o standard da interface de backend impõe a uma
implementação externa: remontar o documento canônico na leitura. O backend `github` não a cumpre —
perde os agrupamentos `### N.` de `## Tasks` — e é bloqueante para a migração das specs deste
repositório, que é o que a `## Proposal` da spec seguinte precisa.

`## Problem` traz a medição sobre os specs em disco; `## Proposal` lista as três correções e o
que passa a ser verdade; `## Design` registra por onde a estrutura de grupo viaja e por que o
título truncado não é perda; `## Risks` carrega o que uma serialização já escrita no GitHub sofre
quando o formato muda.

## Problem

O backend `github` entregue pela spec `configurable-spec-backend` **não remonta o documento
canônico**: ele perde os agrupamentos `### N. <Section>` de `## Tasks`. `hybrid_tasks_shell` esvazia
o corpo inteiro da seção — headings de grupo inclusive — e `hybrid_rebuild_tasks_section` remonta
apenas a concatenação dos blocos de checkbox. O que entra como grupo não volta como grupo, e a CLI
não tem por onde recuperá-lo.

Isso contradiz a obrigação única que `docs/standards/architecture/spec-backend.md` impõe a um
backend externo — *"reassembles the canonical document on read"* — e o `### N. <Section>` não é
convenção de escrita: é gramática documentada no template (`## Tasks` §"Checkboxes `- [ ] <id>
<text>` grouped under `### N. <Section>` headings"), é contada por `parse_tasks` no campo `section`
de toda task, e é a unidade sobre a qual `verification: per-section` e o `[P]` de `specs.py
parallel` raciocinam.

Medido em 2026-08-02 contra os 66 specs deste repositório (42 em `plans/`, 24 em `archive/`,
680 tasks), rodando split e rebuild offline: **47 specs usam grupos** e **~35 documentos não
sobrevivem ao round trip**. A perda é silenciosa dos dois lados — a escrita não falha, e a leitura
devolve um documento bem formado com um nível de estrutura a menos.

Duas falhas menores da mesma superfície de escrita vieram na mesma medição, e são do mesmo tipo
(um limite do GitHub que o código não conhece):

- **`_sync_tasks` manda `t["text"]` cru como título da sub-issue**, sem guarda contra o teto de 256
  caracteres de título de issue do GitHub. **15 tasks** em 12 specs deste repo estouram, a maior com
  946 caracteres.
- **Nada guarda o teto de 65.536 caracteres de corpo de issue.** O maior shell aqui dá 63.686 — passa
  hoje, com 1,8 KB de folga, e falha em pleno `write_spec` no dia em que uma seção crescer.

Nada disso apareceu no E2E da task 4.6 daquela spec porque a spec de teste não tinha grupos nem
títulos longos: o teste provou o caminho, não a forma dos documentos reais.

## Proposal

- **Os agrupamentos `### N. <Section>` sobrevivem ao round trip.** Split e rebuild passam a devolver
  o documento **byte a byte** para todo spec deste repositório, grupos e prosa dentro de `## Tasks`
  inclusive.
- A prova disso deixa de ser argumento e vira uma asserção do `selftest`: a lista canônica de casos
  ganha um documento **com grupos**, e o round trip híbrido é comparado por igualdade estrita.
- **Um título de sub-issue nunca é rejeitado pelo GitHub por comprimento.** O título é uma
  *projeção* do documento — reescrito a cada `write_spec`, nunca lido de volta — então recortá-lo
  não perde nada; o texto íntegro da task continua no corpo da sub-issue, que é de onde
  `parse_tasks` lê.
- **Um corpo acima do teto do GitHub é recusa nomeada (exit 2), nunca um 422 no meio de uma
  escrita.** A recusa nomeia o spec, o tamanho medido e o teto, e nada é escrito.
- O contrato de serialização híbrida passa a estar **declarado** no standard
  `docs/standards/architecture/spec-backend.md`, que hoje diz "reassembles the canonical document on
  read" sem dizer o que isso obriga a preservar.
- O `azure-boards` herda as três correções de graça: os helpers `hybrid_*` já são código
  compartilhado pelos dois backends externos (decisão registrada na task 6.2 de
  `configurable-spec-backend`).

## Out of Scope

- **A migração das specs deste repositório** — é a spec
  `migrate-this-repo-to-github-backend`, que depende desta e não a contém.
- **Prova end-to-end do `azure-boards`** — continua sem ambiente para exercitar, exatamente como
  `configurable-spec-backend` aceitou. As correções entram no código compartilhado e ficam provadas
  pelo selftest contra o fake, não contra um board real.
- **Os cinco achados abertos do conclude de `configurable-spec-backend`** (`sp-dest-exists` inerte,
  `doctor` lendo o root cru, o campo `root` mentindo, a asserção genérica de dispatch, o
  `/specs:align` sem pasta) — têm suas próprias specs e nenhuma delas é pré-requisito da migração.
- **Reduzir o custo de rede do backend `github`** — 33 chamadas para um ciclo de 12 comandos está
  registrado como discovery daquela spec e não é fidelidade de documento.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/architecture/spec-backend.md` — reescrito em §"Hybrid serialisation lives inside
  each external implementation": a obrigação de remontar o documento canônico passa a nomear o que
  ela abrange (toda a estrutura da seção, não só as linhas de checkbox) e o round trip por igualdade
  estrita passa a ser a prova declarada.

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/specs.py` — `hybrid_tasks_shell`, `hybrid_rebuild_tasks_section`,
  `hybrid_wrap_task`/`hybrid_unwrap_task`, `_sync_tasks`, `_write_api`, e a lista canônica de casos
  do `selftest`

## Validation

- `python3 assets/bin/specs.py selftest` — a lista canônica de casos ganha um documento com
  `### N.` e prosa dentro de `## Tasks`, e o round trip híbrido é asserido por **igualdade estrita**.
- **Os specs reais deste repositório como fixture de fato**: um script descartável roda split e
  rebuild sobre `specs/plans/` e `specs/archive/` e exige TODOS idênticos byte a byte. É a mesma
  medição que produziu o `## Problem`, virada do avesso.
- A recusa de corpo grande é exercitada **sem rede**: um documento sintético acima do teto,
  verificando código e exit 2 e que nenhuma chamada de escrita saiu.
- O truncamento de título é exercitado sobre a task de 946 caracteres deste repo, verificando que o
  título cabe em 256 e que o **corpo** da sub-issue mantém o bloco íntegro.
- `python3 assets/bin/skills.py --root . doctor --json` → 26 comandos, 0 findings.
- `python3 assets/hooks/okf-validate.py docs` → 0 error(s).
- O lockstep de versão: `VERSION` e as três ferramentas shipped concordam.

## Design

- **Decisão: a estrutura de `## Tasks` que não é task fica no shell; o rebuild interleava por
  `section`.** O shell (corpo da issue-mãe) passa a manter, dentro de `## Tasks`, tudo que **não é
  um bloco de task** — os `### N.` e qualquer prosa — em posição. O rebuild caminha esse corpo e,
  depois de cada heading, emite os blocos cujo `section` bate com a contagem daquele heading; tasks
  com `section` 0 (antes de qualquer grupo) saem primeiro. `parse_tasks` já entrega `section` em
  toda task, então o número não é derivado por ninguém novo — é o mesmo campo que o resto da CLI já
  usa, o que mantém de pé a regra de que **um backend que passa a derivar algo está quebrado**.
- **Descartada: carregar o heading do grupo dentro do bloco da primeira task do grupo.** Seria
  concatenação pura, sem tocar o rebuild — e faz o heading desaparecer no dia em que aquela task for
  removida ou reordenada. A estrutura do plano ficaria refém do ciclo de vida de uma task
  específica.
- **Descartada: um marcador novo no shell por posição de task.** Reintroduz um formato que só um
  parser novo lê de volta, que é exatamente o que a task 4.2 daquela spec recusou ao manter os sete
  records no frontmatter.
- **Decisão: o `section` de cada task viaja no marcador da sub-issue, ao lado de `index`.** O
  rebuild precisa saber a que grupo cada bloco pertence antes de reparsear o documento — e o
  documento só existe depois do rebuild. `index` já viaja ali pela mesma razão (ordem de documento
  contra ordem de listagem do GitHub); `section` é o segundo fato da mesma família. Uma sub-issue
  escrita pelo formato antigo não carrega a chave, e a ausência é lida como `section` 0 — o
  comportamento de hoje, que é o pior caso e não uma quebra.
- **Decisão: o título da sub-issue é recortado em 256 caracteres, e isso não é perda.** O docstring
  de `hybrid_title` já declara o título da issue-mãe como **projeção** do documento, reescrita a
  cada escrita e nunca fonte: editá-la na web é desfeito pela próxima escrita. O mesmo vale para a
  sub-issue — `parse_tasks` lê o **corpo**, nunca o título. Recorta-se na última fronteira de palavra
  antes do teto, com `…`, para que a lista de sub-issues continue legível.
- **Decisão: um corpo acima do teto recusa antes de escrever, e a checagem mora no transporte.** Em
  `_write_api`, não em cada chamador: é o único ponto por onde toda escrita passa, e uma checagem
  por chamador é a forma de deixar um de fora. Código `sp-gh-body-too-large`, exit 2, nomeando o
  tamanho medido e o teto. Recusar é estritamente melhor que um 422: no meio de uma migração de dezenas de
  specs, um 422 é um traceback sem nome de spec.
- **Decisão: a prova é igualdade estrita sobre um documento com grupos, não uma asserção sobre
  headings.** Verificar "os `###` continuam lá" passa com a ordem trocada e com a prosa perdida.
  Byte a byte é a asserção que `backend_equivalence_failures` já usa para a igualdade entre `files`
  e `memory`, e é a mesma forma de prova.

## Alternatives Considered

- **Proibir `### N.` dentro de `## Tasks` e normalizar os 47 specs que os usam:** rejeitada — o
  agrupamento é gramática documentada no template, contada por `parse_tasks` e usada por
  `verification: per-section`; apagá-la para caber no backend é o backend ditando o modelo
  conceitual, que é a inversão exata do que `spec-backend.md` estabelece.
- **Guardar o documento inteiro no corpo da issue-mãe e usar sub-issues só como espelho de leitura:**
  rejeitada — cria dois lugares onde o estado de uma task existe, e o primeiro humano que fechar uma
  sub-issue pela web cria a divergência. É também o "store canônico duplicado" que
  `spec-backend.md` §"The selected backend is the source of truth" recusa.
- **Aceitar a perda e documentá-la como limitação conhecida:** rejeitada — é perda silenciosa, não
  limitação: a escrita não falha e a leitura devolve um documento bem formado. Uma limitação que não
  se anuncia é indistinguível de um bug.

## Open Decisions

- none — as três correções e a forma da prova estão decididas em `## Design`; nenhuma depende de
  medição que ainda não foi feita.

## Risks

- **Uma sub-issue já escrita pelo formato antigo não carrega `section`** — `MITIGATED`: a ausência
  da chave é lida como `section` 0, que reproduz o comportamento de hoje em vez de recusar. Como
  este repositório ainda não migrou nada e o repo alvo do E2E da task 4.6 teve sua issue removida,
  não há hoje nenhuma sub-issue no mundo escrita pelo formato antigo — o caminho existe pela
  disciplina, não por um dado conhecido.
- **O rebuild passa a depender de dois fatos por task (`index` e `section`) em vez de um** —
  `ACCEPTED`: é o preço de remontar uma estrutura de dois níveis a partir de partes independentes.
  *Mitigação:* ambos saem do mesmo `parse_tasks` que todo o resto usa, e o round trip por igualdade
  estrita falha imediatamente se um dos dois divergir.
- **O truncamento de título esconde o fim de uma task longa na lista de sub-issues** — `ACCEPTED`:
  o corpo mantém o bloco íntegro e é dele que a CLI lê. A alternativa — deixar o GitHub recusar — não
  esconde nada e não escreve nada.
- **A recusa por tamanho de corpo pode barrar um spec legítimo** — `ACCEPTED`: dois specs deste repo
  já estão a menos de 5 KB do teto. Recusar com o tamanho medido é o que dá ao humano o que fazer
  (encurtar uma seção); um 422 do GitHub não dá.

## Handoff

- O pre-flight que produziu os números do `## Problem` é reprodutível offline e sem rede: importar
  `specs.py` como módulo, e para cada arquivo em `specs/plans/` e `specs/archive/` comparar
  `hybrid_rebuild_tasks_section(hybrid_tasks_shell(t), [hybrid_task_block(t, x) for x in
  parse_tasks(t)])` com o texto original. A task 3.1 o transforma na fixture de verificação.
- **Os helpers `hybrid_*` são compartilhados pelos dois backends externos** desde a task 6.2 de
  `configurable-spec-backend` — o prefixo `gh_` foi retirado justamente por isso. Toda correção aqui
  vale para `azure-boards` sem uma linha a mais, e uma que precise ser específica de GitHub é sinal
  de que está no lugar errado.
- O teto de título é 256 caracteres e o de corpo 65.536, ambos do GitHub. Nenhum dos dois está
  documentado na referência REST de "Create an issue" — se a task 2.1 medir outro valor contra a API
  real, o valor medido ganha e vira uma constante nomeada, não um literal solto.
- Não há sub-issue viva no mundo escrita pelo formato de marcador antigo (a issue do E2E da task 4.6
  foi removida ao fim daquele exercício), então a compatibilidade retroativa da task 1.2 é
  disciplina e não migração de dado.

## Tasks

### 1. Os grupos sobrevivem ao round trip

- [x] 1.1 `hybrid_tasks_shell` passa a preservar dentro de `## Tasks` tudo que não é bloco de task —
      os `### N.` e a prosa — em posição, removendo apenas os blocos
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 assets/bin/specs.py selftest
      subject: plan/fix-github-backend-tasks-fidelity: 1.1 o shell preserva os grupos de ## Tasks
- [x] 1.2 `section` viaja no marcador da sub-issue ao lado de `index`, e a ausência da chave é lida
      como 0 em vez de recusar
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 assets/bin/specs.py selftest
      subject: plan/fix-github-backend-tasks-fidelity: 1.2+1.3 o marcador carrega o ancora e o rebuild restaura por ele
- [x] 1.3 `hybrid_rebuild_tasks_section` interleava os blocos por `section` sob o heading
      correspondente, em vez de concatenar
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 assets/bin/specs.py selftest
      subject: plan/fix-github-backend-tasks-fidelity: 1.2+1.3 o marcador carrega o ancora e o rebuild restaura por ele
- [ ] 1.4 A lista canônica de casos do selftest ganha um documento com `### N.` e prosa em
      `## Tasks`, asserido por igualdade estrita no round trip híbrido
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 assets/bin/specs.py selftest
      subject: plan/fix-github-backend-tasks-fidelity: 1.4 o selftest prova o round trip com grupos

### 2. Os dois tetos do GitHub

- [ ] 2.1 O título da sub-issue é recortado na última fronteira de palavra antes de 256 caracteres,
      com o corpo mantendo o bloco íntegro
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 assets/bin/specs.py selftest
      subject: plan/fix-github-backend-tasks-fidelity: 2.1 titulo de sub-issue recortado em 256
- [ ] 2.2 `_write_api` recusa (exit 2, `sp-gh-body-too-large`) um corpo acima de 65.536 caracteres,
      nomeando o tamanho medido e o teto, sem emitir a chamada
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 assets/bin/specs.py selftest
      subject: plan/fix-github-backend-tasks-fidelity: 2.2 recusa nomeada acima do teto de corpo

### 3. Prova sobre os documentos reais

- [ ] 3.1 Provar split e rebuild sobre todo spec em `specs/plans/` e `specs/archive/`, exigindo
      identidade byte a byte em todos
      verify: python3 assets/bin/specs.py selftest
      subject: plan/fix-github-backend-tasks-fidelity: 3.1 os specs reais sobrevivem ao round trip
- [ ] 3.2 Reescrever `docs/standards/architecture/spec-backend.md` §Hybrid serialisation para nomear
      o que a remontagem abrange e a igualdade estrita como prova declarada
      files: docs/standards/architecture/spec-backend.md
      verify: python3 assets/hooks/okf-validate.py docs
      subject: plan/fix-github-backend-tasks-fidelity: 3.2 o standard nomeia o que a remontagem abrange
- [ ] 3.3 Fechar a superfície: doctor com 26 comandos e 0 findings, okf-validate limpo e o lockstep
      de versão concordando
      verify: python3 assets/bin/skills.py --root . doctor --json
      subject: plan/fix-github-backend-tasks-fidelity: 3.3 fecha a superficie e o lockstep

## Discoveries

- As tasks 1.2 e 1.3 sairam numa commit so: o campo anchor no marcador nao tem leitor sem o rebuild que o consome, e o rebuild nao tem o dado sem o marcador. Separa-las produziria uma commit que nao roda. As duas gravam o mesmo subject, entao os dois registros resolvem.
- Refinado na 1.2: o marcador carrega anchor (quantas linhas mantidas do ## Tasks precedem o bloco) e nao section, como o ## Design dizia. section diz a que grupo o bloco pertence mas nao onde dentro dele, e nao diz nada sobre as linhas em branco que o documento usa entre tasks — o round trip seria uma re-diagramacao, nao uma identidade. Medido: com anchor, 68 de 68 documentos reais voltam byte a byte.
