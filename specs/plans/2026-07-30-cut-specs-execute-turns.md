---
slug: cut-specs-execute-turns
title: Cut /specs:execute's turn count through body wording
verification: per-section
---

# Cut /specs:execute's turn count through body wording

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

Uma run de `/specs:execute` custa `turnos × contexto`. Este spec ataca a metade **turnos**, e por um
mecanismo barato: a redação do próprio comando pede mais chamadas de ferramenta do que as garantias
que ele oferece exigem. O `## Problem` reúne a evidência de uma run real de 13 tasks e cinco lugares
onde isso acontece; a `## Proposal` diz o que passa a ser verdade em cada um deles.

A distinção que organiza o resto está em `## Design` D1: quatro dos cinco achados são texto que pode
mudar sem que garantia nenhuma se mova, e um — quando o `## Handoff` é reescrito — é mudança de
contrato, que por isso vira regra escrita junto com o seu motivo. `## Out of Scope` marca a fronteira
com o spec irmão `reduce-execute-conclude-cost`, dono da metade **contexto**, e registra também o
maior corte disponível que este spec deliberadamente não faz.

`## Validation` explica por que a prova é medida em turnos e não em chamadas de ferramenta, e
`## Risks` registra o que acontece se essa diferença for grande.

## Problem

O custo de uma run de `/specs:execute` é `turnos × contexto` — a integral que o spec irmão
`reduce-execute-conclude-cost` mediu e cujo `## Design` D1/D2 já argumenta. Aquele spec ataca a
metade **contexto**: um subcomando de custo em `session.py`, `/skill:retro` lendo custo, a
delegação de executor no passo 5b, e dois standards. Este ataca a outra metade, **turnos**, e por um
mecanismo que aquele não toca: a redação do corpo de `/specs:execute` induz mais chamadas de
ferramenta do que o que ele garante exige.

Evidência de uma run real de 13 tasks (transcript `985b372b-348c-4911-a5dd-146ca0b4ab7b`, spec
`add-import-provenance`, medida por `session.py` em 2026-07-30): **93 tool calls** — 16 exatos
atribuídos a `/specs:execute` mais 77 de limite superior atribuídos ao stage — com
`repeatedReadTargets: 0`, `repeatedShellCommands: 0`, `interrupts: 0`, `interjections: 0`. Nada foi
lido duas vezes e nenhum comando de shell foi repetido: **não há desperdício de repetição a
colher**. O que sobra é estrutural, e é isto:

1. **`## Handoff` é especificado para ser reescrito depois de CADA task commitada** (passo 6). Numa
   spec de 13 tasks isso são 13 reescritas de ~400 palavras cada. Na run medida foram 4, e as quatro
   eram ~90% idênticas. O trilho de retomada por task já existe em `git log` mais os `subjects` que
   `specs.py status` devolve; o que só o Handoff carrega é o estado que nada deriva — uma sessão
   paralela no checkout, um hook não versionado, uma falha de desenho encontrada. Esse estado mudou
   três vezes na run inteira. A cadência deveria ser dirigida a evento (mudança de estado
   não-derivável, mais pausa e conclusão), não por task.

2. **O passo 5 apresenta d-e-f-g como atos separados**, então `verify` rodou como chamada própria,
   separada de `--check` e do commit. Encadear `verify && tick && commit` numa única chamada
   **preserva exatamente a ordenação que o corpo exige** — o `&&` é o que a impõe — e faz
   curto-circuito seguro na falha. São ~10 chamadas numa spec de 13 tasks, sem perder rigor algum.

3. **O passo 2 exige árvore limpa e não diz nada sobre ambiente quebrado.** Na run medida,
   `.claude/settings.json` fiava um hook que o commit `193578c` apagou; diagnosticar isso ad hoc
   custou ~10 chamadas. Uma verificação de uma linha — todo hook fiado resolve no disco? — o
   revelaria em uma.

4. **Um portão de seção reroda checks cujos insumos a seção não pode ter mudado.** Na run medida os
   três selftests rodaram no fecho da seção 1 e de novo em 5.1, quando o próprio spec declarava que
   nenhum script mudava. Um portão deveria ser escopado ao que a seção pôde quebrar.

5. **`/specs:execute` delega isolamento no passo 2 e nunca reconquista atribuição.** `attributionSkill`
   é um ponteiro "entrei-por-último" do próprio Claude Code, setado na entrada e **nunca limpo no
   retorno** (`session.py:55`): medido em 43 stages de 86 transcripts, a atribuição volta ao condutor
   **1 vez**, nunca volta 36 e pula para um terceiro comando 6. Na run medida isso arquiva o loop de
   build inteiro sob `/specs:isolate` (linhas 70-367) e deixa `/specs:execute` em 16 chamadas e 5,5
   minutos — os passos 1 e 2 apenas. **O instrumento não está errado**: `session.py` detecta o erro de
   leitura, marca o stage `closed: false`, anexa `mayIncludeTurnsFrom` e emite
   `se-attribution-unclosed` (`session.py:267-297`), que é `parse-honesty.md` aplicado a um ponteiro
   em vez de a um parser. O relator de custo do grupo 1 de `reduce-execute-conclude-cost` herdaria um
   **limite superior corretamente rotulado**, não uma mentira. O que está errado é o corpo: ele
   despacha um stage mesmo quando não há nada para isolar.

**Fronteira com `reduce-execute-conclude-cost`** (level 3, criticality high, stage ready, 14 tasks,
0 construídas): aquele spec é dono da medição de custo, da política de modelo, da delegação de
executor e dos dois standards de custo; o único ponto dele em `execute.md` é o passo 5b. Este spec
não toca 5b, não escreve standard de custo, não mexe em `session.py`, e acrescenta o campo
`constraint:` que tornaria a delegação viável sem tocar a decisão de usá-la. Se os dois forem
construídos, este deve vir depois, porque o passo 2 novo muda o que aquele consegue medir.

## Proposal

A entrega é **redação de corpo mais as regras que ela move**: onde a garantia não muda, muda só o
texto; onde a garantia muda, a regra nova é escrita com o motivo, para não ser revertida pelo
próximo refactor.

Depois desta entrega:

- O passo 2 de `/specs:execute` **checa antes de despachar** — um spec já isolado (record `branch`
  presente, ou `plan/<slug>` existindo) segue direto, sem chamar `/specs:isolate`. Numa run retomada
  a atribuição do transcript nunca sai de `/specs:execute`, e um retro passa a medir o comando que é
  dono do build.
- O passo 2 também **detecta ambiente quebrado** numa verificação de uma linha — todo hook fiado em
  `.claude/settings.json` resolve no disco? — antes de qualquer código ser escrito.
- Os atos d–g do passo 5 passam a ser **uma chamada encadeada** por task. O `&&` é o que impõe a
  ordenação que o corpo já exige, e uma falha em qualquer elo interrompe os seguintes.
- A cadência do `## Handoff` passa a ser **dirigida a quatro eventos** — pausa, task bloqueada,
  descoberta registrada, último commit da run — em vez de por task commitada.
- `docs/standards/workflows/task-execution.md` passa a ser dono dessa cadência **e do motivo dela**,
  mais o que se perde quando um comando precisa mesmo despachar um stage no meio do fluxo: a própria
  medição, que passa a ser reportada como limite superior.
- `artifacts.md` §Execution metadata e o standard passam a dizer que **`verify:` é escopado ao que
  aquela task pôde quebrar**, então um portão de seção deixa de rerodar checks cujos insumos a seção
  não tocou.
- `specs.py` aceita **`constraint:`** como chave de metadata de task, documentada em `artifacts.md`.
  Nenhum comando a lê — o campo entra inerte, para que a delegação de executor possa se auto-briefar
  quando o spec irmão a decidir.
- As três referências que hoje duplicam a cadência antiga (`specs-develop/artifacts.md`,
  `specs-develop/spec-driven.md`, `specs-align/conformance.md`) passam a concordar com a regra nova.
- Nenhum comando novo é criado, nenhuma `description` cresce, nada passa a recusar, e nada toca
  `session.py` nem o passo 5b.

## Out of Scope

- **Consertar a atribuição em `session.py`.** Não há o que consertar: o ponteiro é do Claude Code e o
  instrumento já nomeia o erro de leitura em vez de adivinhar onde o stage terminou. Mudá-lo para
  inferir um fim fabricaria achados, que é exatamente a falha que `parse-honesty.md` existe para
  impedir.
- **Reganhar a atribuição depois de um dispatch inevitável.** Medido, isso aconteceu 1 vez em 43 e
  ninguém sabe o que a causou. Uma task cujo desfecho provável é "nada" não é uma task; a limitação
  residual é escrita em vez de perseguida.
- **`context: fork` em qualquer comando do ciclo.** Proibido por nome no `CLAUDE.md`: um contexto
  forkado não alcança a conversa onde a confirmação acoplada a código é dada. Registrado aqui para
  não voltar como otimização.
- **Uma regra de portão que pule `verify:` por julgamento.** Seria julgamento sobre correção, e este
  spec já recusou julgamento como gatilho de cadência. O achado 4 é consertado na autoria.
- **O passo 5b e a decisão de delegar um executor.** São do `reduce-execute-conclude-cost`. Este spec
  entrega o campo que a viabiliza e não a decisão de usá-lo.
- **A doutrina "cite a seção, não o arquivo".** `/specs:execute` carrega o corpo mais cinco
  referências, ~22k tokens relidos a cada turno — o maior corte disponível, e o que este spec
  deliberadamente **não** faz: é a metade *contexto*, valeria para todo comando que cita uma
  referência, e já está encaminhada como follow-up no `## Open Decisions` do spec irmão.
- **Uma task de bump de versão.** `specs.py` está no lockstep, mas `versioning-release.md` §When the
  bump happens põe as seis strings movendo-se uma vez em `/specs:conclude` passo 5, nunca como task.
- **`functional-checks.sh` como validação deste spec.** O `CLAUDE.md` é explícito: o harness pertence
  à frente skill e não vai na `## Validation` de um spec.

## Validation

A prova é **uma comparação de turnos**, não de tool calls. A integral de custo é `turnos × contexto`,
e a pior run medida de `/specs:execute` foram 299 turnos contra as 93 chamadas da run de 13 tasks —
as duas métricas não são intercambiáveis, e um corte reportado na errada não prova nada sobre a que
custa.

- Rodar `/specs:execute` sobre um spec de tamanho comparável antes e depois, e comparar os **turnos
  atribuídos** que `session.py` devolve para a run.
- Reportar junto a razão **turnos/tool calls** das duas runs. É o número que julga o resultado: ele
  diz que fração do corte medido em chamadas chegou à métrica que custa.
- Toda figura carrega o `closed` / `mayIncludeTurnsFrom` que `session.py` já anexa. Depois do passo 2
  novo, uma run sobre um spec já isolado deve vir `closed: true` — o que é por si só a prova do
  achado 5.
- `python3 assets/bin/specs.py selftest` cobre `constraint:` (exit 0), `skills.py doctor` e `lint`
  seguem limpos, e `okf-validate.py assets/docs` mais o `docs/` do repo seguem em 0 error(s).

## Design

### D1. A cadência é contrato; o resto é redação

Encadear `verify && tick && commit` e checar o ambiente no passo 2 não movem garantia nenhuma — o
`&&` *é* a ordenação que o corpo exige, e um probe a mais não retira nada de ninguém. Mudar **quando**
o `## Handoff` é reescrito move. Por isso só ela vira regra escrita: uma mudança de garantia que só
existe em três referências volta no próximo refactor, e a regra atual carrega o seu motivo justamente
porque a versão anterior dela já foi revertida uma vez.

### D2. Um gatilho de cadência não pode ser julgamento

A regra que a atual substituiu era "reescreva quando estiver obsoleto", e falhava porque uma run
desassistida nunca julga que algo ficou obsoleto. "Quando o estado não-derivável mudou" é a mesma
falha com outro nome.

Os quatro gatilhos escolhidos — **pausa, task bloqueada, descoberta registrada, último commit da
run** — são momentos em que o corpo *acabou de fazer algo*, nunca em que ele *avalia algo*, e são
exatamente onde o estado que nada deriva de fato muda: uma pausa e um bloqueio produzem contexto que
nada recupera, uma descoberta é por definição um achado novo, e o último commit é o ponto de retomada.
Medido: ~3 reescritas onde hoje são 13, das quais ~90% eram idênticas.

Por seção (`### N.`), pegando carona na política `verification`, foi a alternativa mais forte:
mecânica, sem julgamento, e 5 reescritas em vez de 13. Perde por ainda reescrever quando nada mudou.

### D3. O passo 2 não despacha o que não precisa — e é assim que o achado 5 se resolve no corpo

`/specs:isolate` já reporta o branch existente e não carimba nada quando o spec está isolado, então o
dispatch nesse caso é custo puro **e** custa a atribuição da run inteira. Checar o record `branch` e
`git branch --list plan/<slug>` é barato e não move o ponteiro.

Isto não delega menos: quando há o que isolar, `/specs:isolate` continua sendo o dono da forma, do
nome `plan/<slug>` e do carimbo `branch: {base, work}`, e o invariante "delegate isolation … never
reimplement it here" fica intacto. O caso residual — precisar mesmo isolar — perde a medição, e essa
perda é escrita como regra em vez de redescoberta a cada retro.

### D4. `verify:` é escopado na autoria, não filtrado no portão

Quem decide *o que* roda num portão é o `verify:` de cada task; a política `verification` decide só
*quando*. Os três selftests rodaram duas vezes porque as tasks de duas seções declararam os mesmos
três — o corpo obedeceu exatamente o que o spec pediu. Consertar na origem, com `verify:` escopado ao
que aquela task pôde quebrar, não precisa de julgamento em tempo de build e vale para todo spec
futuro, não só para o medido.

### D5. `constraint:` entra inerte, de propósito

`TASK_META_RE` (`specs.py:128`) tem lista fechada, então o campo exige a regex, o selftest e
`artifacts.md`. Nenhum comando o lê: o único consumidor seria o passo 5b, que é do spec irmão. Entrar
inerte é o que mantém a medição deste spec limpa — um campo que ninguém lê não move turno nenhum — ao
custo de o campo poder ficar sem consumidor, registrado em `## Risks`.

### Contratos que este design não pode contrariar

- O invariante do `CLAUDE.md`: **nunca** `context: fork` nestes comandos.
- `execute.md`: delegar isolamento a `/specs:isolate`, nunca reimplementá-lo aqui.
- `docs/standards/quality/parse-honesty.md`: nomear o erro de leitura, nunca a consequência inferida.
- `docs/standards/ci-cd/versioning-release.md` §When the bump happens: o bump é de `/specs:conclude`.
- O `CLAUDE.md`: `functional-checks.sh` pertence à frente skill e não vai em `## Validation`.

## Alternatives Considered

- **A — só redação, sem contrato.** Endereçaria os achados 1–4 com uma edição de prosa e nenhum
  `docs/standards/` novo: mais barato, mais rápido, nenhuma obrigação de doc. Perdeu porque a cadência
  do `## Handoff` está escrita em três referências e em nenhum standard — mudá-la nos três sem
  escrever a regra nova em lugar nenhum é literalmente o mecanismo pelo qual ela volta.
- **C — mover a garantia para a ferramenta.** `specs.py` ganharia um subcomando que emite a linha
  encadeada `verify && task --check && commit`, tornando a ordenação mecanismo em vez de prosa. O
  argumento é forte e verdadeiro: prosa é sugestão, mecanismo não deriva. Perdeu por preço — o achado
  2 é trocar quatro atos por um `&&` no corpo, e um subcomando com selftest e lockstep de versão custa
  mais do que o defeito que corrige.
- **D — dobrar os cinco achados no `reduce-execute-conclude-cost`.** Uma medição só, um release só,
  nenhuma fronteira para manter. Perdeu porque aquele spec está `ready` com 14 tasks e 0 construídas:
  reabrir a definição dele atrasa os dois. E os mecanismos são diferentes — lá é contexto e
  instrumento, aqui é redação de corpo.

## Risks

- **O corte pode ser pequeno na métrica que importa.** Toda evidência do `## Problem` está em tool
  calls, e a integral de custo está em turnos. Se as chamadas forem uma fração pequena dos turnos, ~23
  cortadas de 93 viram poucos por cento da integral. **Mitigação:** a razão turnos/chamadas é medida e
  reportada (`## Validation`), então o spec relata o tamanho real do seu efeito em vez de o presumir.
- **`constraint:` pode ficar no schema sem consumidor.** O campo entra inerte e depende de o spec
  irmão decidir usá-lo no passo 5b. **ACCEPTED** — custa uma alternância de regex e três linhas de
  doc, e se o irmão o recusar, removê-lo é uma linha; o custo de carregá-lo é menor que o de
  re-litigar o schema depois.
- **Editar `artifacts.md` e `task-execution.md` alcança toda a frente `/specs:*`, não só `execute`.**
  **Mitigação:** as duas edições são aditivas — uma cadência nova e uma regra de escopo de `verify:` —
  e não removem contrato de nenhum outro comando; `specs.py selftest` e `okf-validate.py` cobrem a
  forma.
- **Nada disto é testável na sessão que o escreve** — o registro da superfície é montado no início da
  sessão, então nenhuma mudança sob `commands/**` é verificável ali. **ACCEPTED**, e é precisamente a
  razão de a `## Validation` ser uma run seguinte e não um check.
