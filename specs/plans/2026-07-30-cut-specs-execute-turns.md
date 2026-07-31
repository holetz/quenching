---
slug: cut-specs-execute-turns
title: Cut /specs:execute's turn count through body wording
verification: per-section
refined:
  mode: gate
  date: 2026-07-31
approved:
  date: 2026-07-31
branch:
  base: claude/quenching-specs-execute-turns-4ff7e4
  work: plan/cut-specs-execute-turns
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
onde isso acontece; a `## Proposal` diz o que passa a ser verdade em cada um deles, e `## Tasks` os
constrói em seis seções, do contrato para os corpos.

A distinção que organiza o resto está em `## Design` D1: quatro dos cinco achados são texto que pode
mudar sem que garantia nenhuma se mova, e um — quando o `## Handoff` é reescrito — é mudança de
contrato, que por isso vira regra escrita junto com o seu motivo. `## Impact` declara o único
`docs/standards/` que este spec escreve. `## Out of Scope` marca a fronteira com o spec irmão
`reduce-execute-conclude-cost`, dono da metade **contexto**, e registra também o maior corte
disponível que este spec deliberadamente não faz.

`## Validation` explica por que a prova é medida em turnos e não em chamadas de ferramenta — e por
que ela **não subtrai**: o número de antes é um limite superior e o de depois seria exato, e a
diferença entre os dois mediria a medição em vez do comando. `## Open Decisions` guarda as duas
coisas que só a run seguinte decide, e `## Risks` registra o preço dessa honestidade — o spec sabe a
direção do seu efeito sem saber o tamanho.

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
- `docs/standards/workflows/task-execution.md` passa a ser dono dessa cadência **e do motivo dela**.
  O que se perde quando um comando precisa mesmo despachar um stage no meio do fluxo — a medição, que
  vira limite superior — já é de `docs/standards/automation/session-evidence.md` §What a command's
  run cost, e é **citado** de lá, nunca redeclarado.
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

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/workflows/task-execution.md` — a cadência do `## Handoff` dirigida a quatro
  eventos, com o motivo pelo qual um gatilho de cadência não pode ser julgamento; e a regra de que
  `verify:` é escopado na autoria ao que aquela task pôde quebrar.

### Standards at `authority: background` this spec may resolve

- `docs/standards/automation/session-evidence.md` — já é dona da perda de atribuição num dispatch e
  da regra do limite superior. Este spec não a reescreve nem a promove: o passo 2 novo produz uma
  run `closed: true` onde hoje há `closed: false`, que é a primeira evidência a favor dela. Promover
  a `current` é de quem a mediu.

### Product code this spec expects to touch

- `plugins/quenching/commands/specs/execute.md` — passos 2, 5 (atos d–g) e 6
- `plugins/quenching/assets/references/specs-execute/execution.md` — §Isolation is somebody else's
  job, §The commit
- `plugins/quenching/assets/references/specs-develop/artifacts.md` — §`## Handoff`, §Execution
  metadata
- `plugins/quenching/assets/references/specs-develop/spec-driven.md` — §The executor contract
- `plugins/quenching/assets/references/specs-align/conformance.md` — a remediação de
  `sp-handoff-empty`
- `plugins/quenching/assets/bin/specs.py` — `TASK_META_RE` (:127) e o `selftest`

## Validation

A prova é **uma comparação de turnos**, não de tool calls. A integral de custo é `turnos × contexto`,
e a pior run medida de `/specs:execute` foram 299 turnos contra as 93 chamadas da run de 13 tasks —
as duas métricas não são intercambiáveis, e um corte reportado na errada não prova nada sobre a que
custa.

**Este spec não subtrai.** O baseline disponível é `closed: false` — 16 chamadas exatas mais 77 de
limite superior — e o achado 5 prevê que a run "depois" venha `closed: true`. Subtrair um número
exato de um limite superior mede duas coisas de uma vez, a redação nova e a mudança de regime da
medição, e credita a segunda à primeira. Nenhuma afirmação da forma "cortou N turnos" é feita.

- Rodar `/specs:execute` sobre um spec de tamanho comparável antes e depois, e reportar os **dois
  pares crus** — turnos atribuídos e tool calls de cada run — cada um carregando o `closed` /
  `mayIncludeTurnsFrom` que `session.py` anexa. O rótulo viaja com o número: quem quiser subtrair vê
  o que está subtraindo.
- Reportar a razão **turnos/tool calls** de cada lado. Estável significa que o corte em chamadas
  chegou aos turnos na mesma proporção; em alta significa que ficou nas chamadas. É um sinal de
  direção, não um tamanho de efeito, e é reportado como sinal.
- Reportar o flip de `closed` **isolado**, como prova do achado 5 — nunca somado ao corte, porque ele
  é a medição passando a enxergar, não o comando gastando menos.
- Cada task de edição de prosa carrega um `verify:` próprio que lê o arquivo inteiro com `re.DOTALL`,
  **provado a sair 1 contra a árvore antes da edição**. Nenhum `grep` de linha única sobre prosa: a
  frase que quebra de linha é a falha que `docs/standards/workflows/task-execution.md` já registra.
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

## Open Decisions

- **Qual spec serve de alvo da run "depois" da `## Validation`.** Não é escolhível agora: exige um
  spec `ready` de tamanho comparável ao baseline (~13 tasks) que ainda não tenha sido construído.
  **Como se decide:** na hora de medir, tomando de `plans/` o spec `ready` cuja contagem de tasks
  mais se aproxima de 13; se nenhum estiver dentro de ±3, a comparação é reportada com a diferença
  de tamanho declarada, nunca silenciada.
- **O que conta como sucesso, agora que a `## Validation` não subtrai.** Sem "cortou N turnos" não há
  número-alvo, e fixar um antes de medir é inventar o resultado. **Como se decide:** lendo, depois da
  run "depois", a razão turnos/tool calls dos dois lados mais o flip de `closed` — razão estável ou
  em queda com `closed: true` é o resultado que o spec buscava; razão em alta significa que o corte
  ficou nas chamadas e não chegou aos turnos, e isso é reportado como tal em vez de reenquadrado.

## Risks

- **O corte pode ser pequeno na métrica que importa.** Toda evidência do `## Problem` está em tool
  calls, e a integral de custo está em turnos. Se as chamadas forem uma fração pequena dos turnos, ~23
  cortadas de 93 viram poucos por cento da integral. **PARCIALMENTE ACEITO** — a razão turnos/chamadas
  é medida e reportada dos dois lados (`## Validation`), o que dá a **direção** do efeito; mas a
  `## Validation` deliberadamente não subtrai, então o **tamanho** fica não quantificado. Trocar uma
  sub-quantificação honesta por um número inflado pela mudança de regime da medição seria o pior dos
  dois negócios, e é a troca que este spec recusa.
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

## Handoff

Construído até 4.5. Branch `plan/cut-specs-execute-turns`, cortada de
`claude/quenching-specs-execute-turns-4ff7e4` (uma worktree do harness, **não** `main`) — é o que o
record `branch` carimba, e é de lá que o merge sai.

Estado que nada deriva:

- **O `verify:` da task 4.5 foi fortalecido em linha**, com autorização do humano nesta run. O
  declarado tinha falso negativo (`**` inline entre as palavras); o novo normaliza marcação e
  whitespace, provado a pegar 4 de 4 contra `HEAD~5` e a sair 0 contra a árvore atual. A descoberta
  registra o mecanismo.
- **A run está usando a cadência nova de `## Handoff`** (os quatro eventos), escrita na task 1.1 —
  o corpo que a sessão carrega em memória é o antigo, porque o registro da superfície é montado no
  início da sessão.
- **A task 5.1 corrigiu um bug que a spec não previu**: o despacho de metadata de task terminava em
  `else: verify = val`, então `constraint:` sequestrava o `verify:`. O `selftest` ganhou
  `sp-task-meta-dispatch` para segurar essa linha. A mutation pass de `selftest-mutation.md` rodou
  **quatro** mutações contra as asserções novas, cada uma falhando exatamente a que ataca — o
  registro que aquele standard pede que viva no commit está no corpo do commit de 5.1.

Convenções em vigor:

- `docs/standards/**` e as referências do plugin são prosa em **inglês**; o corpo deste spec é pt-BR.
- Todo `verify:` de task de prosa lê o arquivo inteiro com `re.DOTALL` e **precisa sair 1 contra a
  árvore antes da edição**. `grep` de linha única sobre prosa é proibido aqui.
- Caminhos nos `verify:` são relativos à raiz do repo.
- Nada toca `session.py`, o passo 5b, nem `functional-checks.sh`. O bump de versão é do
  `/specs:conclude` passo 5, nunca uma task.

Os quatro lugares que declaram a cadência antiga, todos com a mesma frase "after each committed
task": `commands/specs/execute.md` passo 6 · `specs-develop/artifacts.md` §`## Handoff` ·
`specs-develop/spec-driven.md` §The executor contract · `specs-align/conformance.md`
(`sp-handoff-empty`).

## Tasks

### 1. O contrato em docs/standards/

- [x] 1.1 Escrever a cadência de `## Handoff` por quatro eventos em `docs/standards/workflows/task-execution.md`, com o motivo — um gatilho de cadência não pode ser julgamento
      files: docs/standards/workflows/task-execution.md
      verify: python3 -c "import re,pathlib,sys;t=pathlib.Path('docs/standards/workflows/task-execution.md').read_text();sys.exit(0 if re.search(r'Handoff.{0,40}cadence.{0,40}events',t,re.S|re.I) and re.search(r'blocked task.*?discovery recorded',t,re.S|re.I) else 1)"
      subject: plan/cut-specs-execute-turns: 1.1 a cadência de ## Handoff por quatro eventos
- [x] 1.2 Escrever em `docs/standards/workflows/task-execution.md` que `verify:` é escopado na autoria, citando `session-evidence.md` para a perda de medição em vez de a redeclarar
      files: docs/standards/workflows/task-execution.md
      verify: python3 -c "import re,pathlib,sys;t=pathlib.Path('docs/standards/workflows/task-execution.md').read_text();sys.exit(0 if re.search(r'session-evidence\.md',t,re.S) and re.search(r'verify:.{0,80}scoped',t,re.S|re.I) else 1)"
      subject: plan/cut-specs-execute-turns: 1.2 verify: escopado na autoria, citando session-evidence.md

### 2. O passo 2 — checar antes de despachar

- [x] 2.1 Fazer o passo 2 de `/specs:execute` checar o record `branch` e `git branch --list plan/<slug>` antes de invocar `/specs:isolate`
      files: plugins/quenching/commands/specs/execute.md
      verify: python3 -c "import re,pathlib,sys;sys.exit(0 if re.search(r'branch --list\s+plan/',pathlib.Path('plugins/quenching/commands/specs/execute.md').read_text(),re.S) else 1)"
      subject: plan/cut-specs-execute-turns: 2.1 o passo 2 checa a isolação antes de despachar
- [x] 2.2 Registrar a mesma regra em `execution.md` §Isolation is somebody else's job, com o caso residual que perde a medição da run
      files: plugins/quenching/assets/references/specs-execute/execution.md
      verify: python3 -c "import re,pathlib,sys;sys.exit(0 if re.search(r'already isolated.*?session-evidence',pathlib.Path('plugins/quenching/assets/references/specs-execute/execution.md').read_text(),re.S|re.I) else 1)"
      subject: plan/cut-specs-execute-turns: 2.2 a regra do dispatch em execution.md, com o caso residual
- [x] 2.3 Acrescentar ao passo 2 o probe de ambiente de uma linha — todo hook fiado em `.claude/settings.json` resolve no disco?
      files: plugins/quenching/commands/specs/execute.md
      verify: python3 -c "import re,pathlib,sys;sys.exit(0 if re.search(r'settings\.json.{0,200}hook',pathlib.Path('plugins/quenching/commands/specs/execute.md').read_text(),re.S|re.I) else 1)"
      subject: plan/cut-specs-execute-turns: 2.3 o probe de hooks fiados no passo 2

### 3. O passo 5 encadeado

- [x] 3.1 Reescrever os atos d–g do passo 5 como UMA chamada encadeada por task, com o `&&` impondo a ordenação que o corpo já exige
      files: plugins/quenching/commands/specs/execute.md
      verify: python3 -c "import re,pathlib,sys;sys.exit(0 if re.search(r'task --check.{0,120}&&.{0,120}git commit',pathlib.Path('plugins/quenching/commands/specs/execute.md').read_text(),re.S) else 1)"
      subject: plan/cut-specs-execute-turns: 3.1 os atos d-g do passo 5 como uma chamada encadeada
- [x] 3.2 Alinhar `execution.md` §The commit ao encadeamento, sem mover a ordenação tick-antes-do-commit
      files: plugins/quenching/assets/references/specs-execute/execution.md
      verify: python3 -c "import re,pathlib,sys;sys.exit(0 if re.search(r'task --check.{0,120}&&.{0,120}git commit',pathlib.Path('plugins/quenching/assets/references/specs-execute/execution.md').read_text(),re.S) else 1)"
      subject: plan/cut-specs-execute-turns: 3.2 execution.md §The commit alinhado ao encadeamento

### 4. A cadência nova nos quatro lugares que hoje dizem a antiga

- [x] 4.1 Reescrever o passo 6 de `/specs:execute` para os quatro eventos
      files: plugins/quenching/commands/specs/execute.md
      subject: plan/cut-specs-execute-turns: 4.1 o passo 6 reescrito para os quatro eventos
- [x] 4.2 Reescrever `artifacts.md` §`## Handoff` — small, and refreshed on events
      files: plugins/quenching/assets/references/specs-develop/artifacts.md
      subject: plan/cut-specs-execute-turns: 4.2 artifacts.md §## Handoff na cadência de quatro eventos
- [x] 4.3 Reescrever o parágrafo do refresh em `spec-driven.md` §The executor contract
      files: plugins/quenching/assets/references/specs-develop/spec-driven.md
      subject: plan/cut-specs-execute-turns: 4.3 spec-driven.md §The executor contract na cadência nova
- [x] 4.4 Reescrever a remediação de `sp-handoff-empty` em `conformance.md`
      files: plugins/quenching/assets/references/specs-align/conformance.md
      subject: plan/cut-specs-execute-turns: 4.4 a remediação de sp-handoff-empty na cadência nova
- [x] 4.5 Provar, com um check que normaliza marcação inline e whitespace, que a frase antiga não sobreviveu em nenhum dos quatro arquivos
      verify: python3 -c "import re,pathlib,sys;p=['plugins/quenching/commands/specs/execute.md','plugins/quenching/assets/references/specs-develop/artifacts.md','plugins/quenching/assets/references/specs-develop/spec-driven.md','plugins/quenching/assets/references/specs-align/conformance.md'];n=lambda t:re.sub(r'\s+',' ',re.sub(r'[*_\x60]','',t));sys.exit(1 if any(re.search(r'after each committed task',n(pathlib.Path(f).read_text()),re.I) for f in p) else 0)"
      subject: plan/cut-specs-execute-turns: 4.5 o check da frase antiga, fortalecido contra marcação inline

### 5. `constraint:` e o escopo de `verify:` nas referências

- [x] 5.1 Admitir `constraint:` em `TASK_META_RE` (`specs.py:127`) e cobrir o campo no `selftest`
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py selftest
      subject: plan/cut-specs-execute-turns: 5.1 constraint: na gramática de metadata, e o despacho exaustivo
- [x] 5.2 Documentar `constraint:` (inerte, com o motivo) e a regra de escopo de `verify:` em `artifacts.md` §Execution metadata
      files: plugins/quenching/assets/references/specs-develop/artifacts.md
      verify: python3 -c "import re,pathlib,sys;sys.exit(0 if re.search(r'`constraint:`',pathlib.Path('plugins/quenching/assets/references/specs-develop/artifacts.md').read_text(),re.S) else 1)"
      subject: plan/cut-specs-execute-turns: 5.2 constraint: e o escopo de verify: em artifacts.md

### 6. Fecho

- [ ] 6.1 Rodar a bateria do CLAUDE.md — os três `selftest`, `okf-validate.py` sobre `assets/docs` e o `docs/` do repo, `skills.py doctor` e `lint`
      verify: cd plugins/quenching && python3 assets/bin/specs.py selftest && python3 assets/bin/skills.py selftest && python3 assets/hooks/okf-validate.py selftest && python3 assets/hooks/okf-validate.py assets/docs && python3 assets/bin/skills.py --root . doctor --json
- [ ] 6.2 Medir com `session.py` o par cru do baseline da run `985b372b` e registrá-lo em `## Validation`
      files: specs/plans/2026-07-30-cut-specs-execute-turns.md

## Discoveries

- O verify: da task 4.5 tem falso negativo: em artifacts.md a frase era 'after **each committed\ntask**' e o regex 'after\s+each\s+committed\s+task' nao casa por causa do ** inline. Provado contra HEAD~3: frase presente, regex nao encontra. O check passaria com 1 dos 4 alvos intocado — o mesmo defeito que task-execution.md §A verify: that cannot fail proves nothing ja registra, agora com marcacao inline em vez de quebra de linha. Um check sobre prosa precisa normalizar marcacao, nao so whitespace.
- Admitir constraint: em TASK_META_RE expos um fallthrough latente no parser de tasks (specs.py:1168): o despacho terminava em 'else: verify = val', entao QUALQUER chave nova na gramatica vira o verify da task. Provado: uma task com 'constraint:' depois de 'verify:' devolvia verify='nao toque em src/b.ts' — o loop rodaria prosa como comando de shell. Corrigido para despacho exaustivo (elif key == 'verify'), com constraint deliberadamente sem arm. A licao generaliza: admitir uma chave na gramatica e' metade do trabalho; a outra metade e' o despacho, e um 'else' final e' um sequestro esperando a proxima chave.
