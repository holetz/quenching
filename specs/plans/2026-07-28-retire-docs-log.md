---
slug: retire-docs-log
title: Retire the docs/ log
verification: per-section
priority: {level: 9, criticality: medium, date: 2026-07-28}
branch: {base: main, work: plan/retire-docs-log}
refined: {mode: gate, date: 2026-07-28}
approved: {date: 2026-07-28}
---

# Retire the docs/ log

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

Remover a criação e a manutenção do `log.md` no bundle `docs/`. Hoje vários
comandos de captura do plugin gastam passos para localizar ou criar a data de
hoje e acrescentar uma linha ao `docs/log.md`, e a conformidade OKF trata o
arquivo como parte do contrato do bundle.

O que se quer decidir e executar é o fim desse artefato: nem criado pelo
`/docs:align`, nem alimentado pelos comandos de captura, nem exigido pelo
validador.

## Proposal

Encerrar o `log.md` como artefato do bundle OKF. Depois desta spec:

- `/docs:align` não cria mais `docs/log.md` nem `docs/standards/log.md`, e o
  esqueleto em `assets/docs/` deixa de trazê-los;
- o procedimento de inserção em `docs-add/homes.md` perde a etapa
  **Appending to `log.md`**, passando de cinco etapas para quatro (stamp → index
  → glossary → self-check), e os quatro comandos de captura que a citam —
  `/docs:add`, `/docs:learn`, `/docs:harness`, `/docs:import-memory` — deixam de
  pagá-la;
- `/docs:align` deixa de acrescentar a própria entrada de encerramento (passo 9);
- `okf-validate.py` deixa de executar `check_log`; os três códigos
  `log-has-type`, `log-no-date-heading` e `log-not-newest-first` somem;
- `/specs:conclude` deixa de registrar a ponte no log: a distilação passa a ser
  narrada no `## Outcome` da própria spec arquivada — seção já obrigatória no
  promote e já escrita na mesma passagem;
- os dois logs deste repositório são removidos.

`log.md` continua **isento** no validador — reconhecido, nunca tratado como
concept doc, nunca bloqueado. Um log que sobreviva em um repositório já alinhado
continua legível e gravável; simplesmente ninguém mais o produz, alimenta ou
julga.

## Out of Scope

- Remover `log.md` de repositórios-alvo já alinhados. `/docs:align` não apaga nem
  menciona o arquivo; a disposição é decisão de cada repositório.
- Backfill das entradas `**Update**` existentes para o `## Outcome` das specs já
  arquivadas — perda aceita, ver `## Risks`.
- `index.md` e sua zona GENERATED. A outra reserva do contrato OKF permanece
  intacta, inclusive `specs/plans/index.md`, reavaliado separadamente pela spec
  `decide-plans-index-need`.
- Provenance por termo em `knowledge/glossary.md` — considerada e descartada, ver
  `## Alternatives Considered`.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/architecture/retiring-a-reserved-artifact.md` — um nome
  reservado que é aposentado continua isento: perde o checker, nunca a reserva

### Product code this spec expects to touch

- `plugins/quenching/assets/hooks/okf-validate.py` — `check_log`, os três
  códigos `log-*`, o selftest
- `plugins/quenching/commands/**` — 17 arquivos, 38 ocorrências
- `plugins/quenching/assets/references/**` — 8 arquivos, 22 ocorrências
- `plugins/quenching/assets/docs/`, `plugins/quenching/assets/templates/` —
  esqueleto e moldes, incluindo `log.md.tmpl`
- `docs/`, `CLAUDE.md`, `README.md`, `plugins/quenching/README.md` — o próprio
  repositório

## Validation

Salvo indicação, cada comando roda a partir de `plugins/quenching/`.

1. `python3 assets/hooks/okf-validate.py selftest` — passa, **incluindo o caso
   novo**: um bundle com `log.md` populado valida em `0 error(s)` e nunca é
   bloqueado pelo `PreToolUse`. É a guarda permanente da regra escrita em
   `## Impact`.
2. `python3 assets/hooks/okf-validate.py assets/docs` — `0 error(s), 0
   warning(s)`, e o esqueleto não contém mais nenhum `log.md`.
3. `python3 assets/bin/specs.py selftest` e `python3 assets/bin/skills.py
   selftest` — passam; o lockstep de `CANONICAL_CASES` segue intacto.
4. `python3 assets/bin/skills.py --root . doctor --json` — 25 comandos, sem
   findings; `lint --json` sai 0.
5. `grep -rn 'log\.md' commands assets/references` — retorna apenas as menções
   deliberadas (a isenção no validador e o registro em `/docs:status`), nenhuma
   instrução de append.
6. `./assets/bin/functional-checks.sh` — sai 0, 9 asserções. **Obrigatório**: 17
   arquivos sob `commands/**` mudam, e nada mais neste repositório prova que a
   superfície ainda carrega.
7. Na raiz do repositório: `grep -rn 'log\.md' docs CLAUDE.md README.md` — nada
   além do standard novo.

## Design

`log.md` aparece em **três** pontos de `okf-validate.py`, e só o segundo é
aposentado:

| Ponto | Hoje | Depois |
| --- | --- | --- |
| `RESERVED = ("index.md", "log.md")` (l. 130) | reservado | **mantém** |
| despacho para `check_log` (l. 1035) | valida o log | **removido** |
| skip do hard block em `PreToolUse` (l. 1251) | nunca bloqueia | **mantém** |

Tirar `log.md` dos três derrubaria todo log sobrevivente em repositórios já
alinhados para o caminho genérico de concept doc: `missing-type` em nível ERROR
e, com `hardBlock` ligado, negação de escrita no arquivo. Aposentado não é
desconhecido — o arquivo deixa de ser produzido e julgado, sem deixar de ser
reconhecido.

## Alternatives Considered

| Alternativa | Por que perdeu |
| --- | --- |
| Aposentar só a metade derivável: matar `**Creation**`, manter `**Update**` | Mantém o custo por captura (localizar-ou-criar a data de hoje) que é a queixa original, e deixa o artefato meio vivo. |
| Mirar a obrigação de append, deixando o destino do arquivo como consequência | Inverte o `## Problem`, que é explícito quanto ao fim do artefato. Adiar a decisão sobre o arquivo não a torna mais barata. |
| Provenance por entrada no `glossary.md` | Muda um formato que todo comando de captura e o validador tocam — blast radius maior que a própria aposentadoria. |
| Aceitar a perda da distilação sem destino algum | `## Outcome` já é obrigatório no promote e já é escrito na mesma passagem: destino sem artefato novo, custo zero. |
| Deixar os dois logs deste repositório no lugar | Faria deste repo o único lugar onde o artefato aposentado sobrevive. |

## Open Decisions

- none — as quatro perguntas do gate foram respondidas nesta passagem. O único
  ponto que continuava aberto ao fim do banco de shape — o que `/docs:status`
  faz com um `log.md` sobrevivente — foi decidido e está registrado em
  `## Design`.

## Risks

- **Perda da provenance já registrada.** As 28 entradas `**Update**` de
  `docs/log.md` narram por que certos termos do glossário existem, e várias
  apontam para specs já arquivadas. O destino no `## Outcome` vale daqui para a
  frente e não as recupera. Aceito: reconstruir provenance de specs arquivadas é
  trabalho real de valor decrescente — os termos estão definidos, linkados e em
  uso, e ninguém vai perguntar por que entraram.

## Handoff

Estado: spec isolada no worktree `../claude-quenching-retire-docs-log`, branch
`plan/retire-docs-log` a partir de `main`. Nada commitado ainda.

Convenções em vigor:

- `log.md` **permanece** em `RESERVED` e no skip do hard block do `PreToolUse`.
  Só `check_log` sai. Tirar dos três pontos derruba todo `log.md` sobrevivente
  em repositório já alinhado para `missing-type` (ERROR) e nega escrita nele —
  ver `## Design`.
- Prosa dos corpos em português; headings, slugs, chaves de frontmatter e
  valores de `type` em inglês canônico.
- Depois de qualquer mudança em `commands/**`, `functional-checks.sh` é a única
  prova de que a superfície ainda carrega — o registry é montado no início da
  sessão, então nada mais neste repositório detecta um corpo inalcançável.
- O bump de `VERSION` + `plugin.json` + `marketplace.json` + a constante
  `VERSION` dos três scripts é lockstep de release e não é decisão desta spec.

Inventário já medido de `log.md`: 17 arquivos em `commands/` (38 ocorrências),
8 em `assets/references/` (22), 8 no esqueleto e nos moldes, 8 na raiz deste
repositório.

## Tasks

### 1. Validator

- [x] 1.1 Remover de `okf-validate.py` o despacho para `check_log` e os três códigos `log-has-type`, `log-no-date-heading` e `log-not-newest-first`, **mantendo** `log.md` em `RESERVED` (l. 130) e no skip do hard block do `PreToolUse` (l. 1251)
      files: plugins/quenching/assets/hooks/okf-validate.py
      subject: plan/retire-docs-log: 1.1 drop check_log and the three log-* codes
- [x] 1.2 Adicionar ao `selftest` o caso que prova a regra: um bundle com `log.md` populado valida em `0 error(s)` e não é bloqueado
      files: plugins/quenching/assets/hooks/okf-validate.py
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py selftest
      subject: plan/retire-docs-log: 1.2 guard the retirement with a selftest fixture

### 2. Skeleton and templates

- [x] 2.1 Apagar `assets/docs/log.md`, `assets/docs/standards/log.md` e `assets/templates/log.md.tmpl`
      files: plugins/quenching/assets/docs/log.md, plugins/quenching/assets/docs/standards/log.md, plugins/quenching/assets/templates/log.md.tmpl
      subject: plan/retire-docs-log: 2.1 delete the skeleton logs and the log mold
- [x] 2.2 Atualizar os sete arquivos do esqueleto e dos moldes que referenciam o log: `assets/docs/index.md`, `assets/docs/QUENCHING.md`, `assets/docs/standards/index.md`, `assets/docs/standards/CLAUDE.md`, `assets/templates/README.md`, `assets/templates/standard-front.md`, `assets/templates/harness/claude-root.md`
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/docs
      subject: plan/retire-docs-log: 2.2 drop the log from the skeleton and the molds

### 3. References

- [ ] 3.1 Remover de `docs-add/homes.md` a seção **Appending to `log.md`** e reescrever o procedimento de inserção de cinco etapas para quatro (stamp → index → glossary → self-check), incluindo o sumário e as citações internas
      files: plugins/quenching/assets/references/docs-add/homes.md
- [ ] 3.2 Retirar o log do contrato OKF em `docs-align/okf-spec.md`, `docs-align/taxonomy.md`, `docs-align/conformance.md` e `docs-align/cycle.md`
      files: plugins/quenching/assets/references/docs-align/okf-spec.md, plugins/quenching/assets/references/docs-align/taxonomy.md, plugins/quenching/assets/references/docs-align/conformance.md, plugins/quenching/assets/references/docs-align/cycle.md
- [ ] 3.3 Reescrever o passo 4 de `specs-conclude/distill.md`: a ponte deixa de ser uma entrada no log e passa a ser narrada no `## Outcome` da própria spec arquivada
      files: plugins/quenching/assets/references/specs-conclude/distill.md
- [ ] 3.4 Ajustar as menções restantes em `specs-create/plans-zone.md` e `specs-develop/spec-driven.md`
      files: plugins/quenching/assets/references/specs-create/plans-zone.md, plugins/quenching/assets/references/specs-develop/spec-driven.md

### 4. Commands

- [ ] 4.1 `/docs:align`: remover o passo 4(f) (estabelecer `log.md`), o estabelecer/append do passo 7 e a entrada única do passo 9
      files: plugins/quenching/commands/docs/align.md
- [ ] 4.2 `/docs:status`: passar a reportar um `log.md` sobrevivente como resíduo aposentado, **sem código de finding**, como já faz com as figuras de densidade
      files: plugins/quenching/commands/docs/status.md
- [ ] 4.3 Remover as menções ao log dos quinze arquivos de comando restantes, em um commit
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json

### 5. This repository

- [ ] 5.1 Apagar `docs/log.md` e `docs/standards/log.md` e atualizar os quatro arquivos do bundle que os linkam: `docs/index.md`, `docs/QUENCHING.md`, `docs/standards/index.md`, `docs/standards/CLAUDE.md`
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
- [ ] 5.2 Atualizar `CLAUDE.md`, `README.md` e `plugins/quenching/README.md`
      files: CLAUDE.md, README.md, plugins/quenching/README.md

### 6. Standard

- [ ] 6.1 Escrever `docs/standards/architecture/retiring-a-reserved-artifact.md` (`authority: current`), citando o caso de selftest da tarefa 1.2 como sua guarda
      files: docs/standards/architecture/retiring-a-reserved-artifact.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs

### 7. Verification

- [ ] 7.1 Rodar a bateria completa de `## Validation` e registrar a saída
      verify: cd plugins/quenching && ./assets/bin/functional-checks.sh
