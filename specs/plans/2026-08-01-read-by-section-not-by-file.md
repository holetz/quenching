---
slug: read-by-section-not-by-file
title: Read by section, not by file — narrow what a command loads before it works
verification: per-section
refined: {mode: gate, date: 2026-08-01}
approved: {date: 2026-08-01}
---

# Read by section, not by file — narrow what a command loads before it works

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

     AUDIENCE. Each section names who reads it. `## Overview`/`## Problem`/`## Proposal`/
     `## Design` are for the human — examples and plain language belong there.
     `## Handoff`/`## Tasks` are for agents — terse, with `files:`/`verify:`/`pattern:`
     metadata. An orchestrator never sends the human sections to an executor; that is what
     lets one file serve both audiences without bloating agent context. -->

## Overview

Este spec faz um comando **abrir menos coisa** antes de trabalhar. Não compacta documentação e não
divide arquivo nenhum: as duas saídas óbvias foram medidas e recusadas, e a conta de cada uma está em
`## Alternatives Considered` — segmentar custaria ~93k tokens de frontmatter novo sem tocar a causa;
compactar apagaria o único ativo que um LLM não reconstrói.

`## Problem` traz os números em disco — ~68k tokens de doutrina antes da primeira linha de código, dos
quais o passo 4 lendo **pastas** de standards é o item dominante — e mostra que a granularidade dos
arquivos já está certa: 315 seções, média ~387 tokens. O que falta é a ferramenta que resolve os
identificadores `§Section` que os corpos **já** citam.

A spec carrega **dois** cortes, que são as duas únicas metades da integral `tokens × turnos_restantes`:
**abrir menos** (seções 1–4 das tasks) e **rodar menos tempo** (seção 5 — a oferta de parar numa
fronteira de seção, que subsume `cut-execute-context-integral` por inteiro).

`## Proposal` lista as sete coisas que passam a ser verdade; `## Design` registra as decisões, entre
elas por que `--rules-only` lê marcador e nunca heurística, e por que compactar aqui é **relocação e
nunca deleção**. `## Impact` nomeia o standard novo e o vizinho revisado; `## Open Decisions` carrega
as cinco coisas sem dono — onde o verbo de leitura mora, e qual evento dispara a oferta de parar; e
`## Risks` guarda os dois preços aceitos: ler por seção pode esconder contexto que a leitura inteira
dava de graça, e parar-e-retomar **move** custo em vez de eliminá-lo se a retomada não for barata.
Nenhuma das duas diferenças aparece numa medição de tokens.

## Problem

Um comando desta superfície carrega **arquivos inteiros** para responder perguntas que estão escritas
**por seção**. Medido em disco, com aritmética sobre a integral `tokens × turnos_restantes`:

- O preâmbulo de `/quenching:specs:execute`, antes de a primeira task escrever uma linha:
  corpo 19.594 chars + cinco referências citadas 76.025 chars + a spec 24.434 chars + o passo 4 lendo
  as **pastas** `docs/standards/<subject>/` dos assuntos tocados, 151.206 chars. Total **~68k tokens**.
  Numa run de ~300 turnos — o tamanho da `configurable-spec-backend`, 29 tasks em 7 seções — isso
  sozinho vale **~20M tokens-turno**, mais que os 17,4M da run inteira que `cut-execute-context-integral`
  mediu.
- **Esse total é o que o corpo manda carregar, não o que toda run comprova ter carregado** — é um
  limite superior. A run medida leu três dos cinco arquivos por inteiro (2,86M tokens-turno) e os
  outros por seção; o que ela estabelece é a **ordenação** — seis leituras pesaram mais que sessenta e
  sete chamadas de shell por mais de dois para um — não a soma acima.
- O passo 4 é o item dominante e nenhum spec o ataca: ele manda ler a **pasta**
  `docs/standards/<subject>/`, não os documentos que as tasks nomeiam. Nessa spec são três pastas
  inteiras — 20 arquivos, ~38k tokens — das quais `## Impact` declara cinco.

A granularidade dos arquivos **não** é o problema. Contados: **315 seções `##` em 488.149 chars, média
1.549 chars (~387 tokens) por seção**; o maior arquivo do bundle tem 22.595 chars. Ler
`execution.md` §The verification policy custa ~400 tokens; ler `execution.md` custa 4.600. O fator 11
não vem de o arquivo ser grande — vem de pedir o arquivo quando se quer a seção.

Os **identificadores já existem** e os corpos já os usam: toda citação é `§Section name`, e
`execution.md` até carrega um `## Contents` com âncoras. O que não existe é a ferramenta que os
resolve. `specs.py section` lê uma seção — **só de spec**; `skills.py` tem `lint · doctor · selftest ·
registry · budget · drift` e **nenhum verbo de leitura**; `docs/` e `assets/references/**` só são
alcançáveis por `Read`, que é file-granular. A doutrina "cite a seção, não o arquivo" que
`cut-execute-context-integral` propõe não tem como ser obedecida mecanicamente hoje — é julgamento.

E a saída óbvia — delegar — sai pior no caso comum. Na `configurable-spec-backend`, 18 das 29 tasks
são elegíveis a executor sub-agente, mas **13 declaram o mesmo arquivo: `specs.py`, 3.108 linhas /
~37k tokens**. Um sub-agente tem contexto novo e não compartilha o prompt cache da sessão: paga a
leitura fria inteira. Em preço equivalente, ~13 × 37k ≈ 480k contra ~150k do orquestrador lendo uma
vez e relendo de cache a 10%. `execution.md` §Delegating an executor autoriza a delegação sem dizer
isso, e medido ela nunca disparou uma única vez em todo o arquivo de transcripts.

## Proposal

- **O passo 4 de `/quenching:specs:execute` deixa de ler pastas.** Passa a ler os `docs/standards/`
  que `## Impact` declara mais os que a task corrente nomeia — e as seções da spec por
  `specs.py section`, não o arquivo por `Read`.
- **Existe um resolvedor de seção para markdown genérico**, com o mesmo contrato do
  `specs.py section` que já serve specs: dado um caminho e nomes de seção, devolve aquelas seções,
  **sem frontmatter**, numa chamada só.
- **A leitura de N seções é UMA chamada.** Turnos são a outra metade da integral: cinco seções em
  cinco chamadas troca tokens por turnos e pode sair pior do que a leitura inteira. `specs.py section`
  ganha a forma plural pela mesma razão.
- **Cada seção normativa separa a regra do racional por marcador**, não por julgamento:
  `<!-- rules -->` no topo com a regra em forma imperativa, `<!-- rationale -->` com a medição, o que
  foi revertido e o v1 que falhou. `--rules-only` devolve o primeiro bloco. **Nada sai do disco** — a
  narrativa continua inteira no arquivo, e continua sendo contrato.
- **A doutrina vira standard escrito**: um comando lê a coisa mais estreita que responde a pergunta —
  os arquivos declarados, não a pasta; as seções citadas, não o arquivo.
- **`/quenching:specs:execute` passa a OFERECER parar numa fronteira de seção**, nomeando o comando
  que retoma. A integral é quadrática nos turnos: sete runs de ~45 turnos custam grosseiramente **1/7**
  de uma de 300 pelo mesmo trabalho, e o trilho de retomada já está pago — `## Handoff`, `git log` e os
  `subjects` que `specs.py status` devolve. Oferece, nunca impõe, e o gatilho é evento, nunca um
  limiar inventado.
- **`execution.md` §Delegating an executor passa a declarar o custo real da delegação**: N sub-agentes
  sobre um arquivo grande compartilhado pagam N leituras frias, e a conta pode inverter. A permissão
  não muda; o que muda é o comando passar a saber quando ela compensa.
- Nada passa a recusar, nenhum comando novo é criado, nenhuma `description` cresce, e nenhum arquivo
  de `docs/` ou de `assets/references/` é dividido, movido ou apagado.

## Out of Scope

- **`cut-execute-context-integral` é subsumida por inteiro.** Os três itens da `## Proposal` dela — o
  passo 4 lendo por seção, a doutrina "cite a seção, não o arquivo", e a oferta de parar numa
  fronteira de seção — entram aqui, os dois primeiros com a ferramenta que os torna mecânicos em vez
  de julgamento. Este spec **não a apaga**: ela fecha como `abandoned` por decisão humana, via
  `/quenching:specs:conclude`, pelo precedente que `rethink-specs-workflow-for-claude-code` já aplica
  às três specs que subsume.
- **Um limiar numérico para "a janela já é longa".** Inventá-lo antes de medir é fixar o resultado. A
  oferta é dirigida a evento, como a cadência do `## Handoff` já é — ver `## Open Decisions`.
- **Impor a parada.** A oferta é oferta: um `/quenching:specs:execute` que decide sozinho encerrar
  uma run desatendida troca um custo por uma surpresa. Nada aqui recusa e nada aqui encerra.
- **Dividir standards ou referências em mais arquivos.** Medido e recusado — ver
  `## Alternatives Considered`. Nenhum arquivo do bundle é criado, dividido ou movido aqui.
- **Apagar racional para compactar.** Recusado pela mesma seção: é o único ativo que um LLM não
  reconstrói, e o repo já trata a narrativa como contrato ("preserva a narrativa antiga como o que foi
  revertido").
- **O instrumento de medição de custo** — `session.py` com subcomando de custo, `/quenching:skill:retro`
  lendo custo, a política de modelo. É do `reduce-execute-conclude-cost`, grupo 1.
- **Os três backends de spec** (`files` em branch dedicada, `github`, `azure-boards`) e a posse de
  worktrees. São da `configurable-spec-backend` e da `rethink-specs-workflow-for-claude-code`. Este
  spec toca `specs.py` **apenas** no verbo `section`.
- **Re-medir os transcripts do arquivo.** A medição que este spec faz é estática e determinística
  sobre arquivos em disco; um censo de transcripts é interessante e não prova nada aqui.
- **`context: fork` em qualquer comando do ciclo.** É a forma óbvia de isolar contexto e o `CLAUDE.md`
  a proíbe por nome. Registrado para que a ideia não volte como otimização — e note que a oferta de
  parar entrega o mesmo isolamento **sem** tirar o humano do alcance das confirmações.
- **Uma task de bump de versão.** `versioning-release.md` §When the bump happens é explícita: as
  strings se movem uma vez, em `/quenching:specs:conclude`, nunca como task.
## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/automation/context-discipline.md` (novo) — o dono do assunto: a integral de uma run
  é `tokens × turnos_restantes` e só há dois jeitos de cortá-la — **abrir menos** e **rodar menos
  tempo**. Abrir menos: os arquivos que `## Impact` declara em vez da pasta, as seções citadas em vez
  do arquivo, N seções em UMA chamada, a convenção `<!-- rules -->` / `<!-- rationale -->` e por que
  ela é marcador e não julgamento, e a recusa medida de segmentar o bundle em mais arquivos. Rodar
  menos tempo: a fronteira de seção como ponto de corte legítimo, por que a oferta é dirigida a evento
  e nunca a limiar, e o que a torna barata (o trilho de retomada já existir)
- `docs/standards/automation/context-budget.md` — revisado: a §The other half hoje é o lugar mais
  próximo de dono deste assunto e passa a apontar para o dono novo, sem absorver o conteúdo dele.
  Continua `authority: background` — nada aqui roda `skills.py budget` em dois repos adotantes, que é
  o gate de graduação dele

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/skills.py` — o verbo de leitura por seção (per `## Open Decisions`
  sobre onde ele mora)
- `plugins/quenching/assets/bin/specs.py` — `section` ganha a forma plural; nada mais
- `plugins/quenching/commands/specs/execute.md` — o passo 4 (pasta → arquivos declarados; `Read` da
  spec → `specs.py section`), as citações que passam pelo leitor, e a oferta de parar numa fronteira
  de seção
- `plugins/quenching/assets/references/specs-execute/execution.md` — os marcadores, e
  §Delegating an executor ganhando o custo real da delegação sobre arquivo compartilhado
- `plugins/quenching/assets/references/specs-isolate/git.md`,
  `.../specs-develop/spec-driven.md`, `.../docs-add/homes.md`, `.../docs-align/conformance.md` — os
  marcadores nas cinco referências que `/quenching:specs:execute` carrega
- `plugins/quenching/README.md` — só se `## Open Decisions` decidir por um quarto script shipped, que
  entra no lockstep

## Validation

Toda a prova é **determinística e estática** de propósito: um spec sobre custo de contexto não abre a
própria prova gerando sessões de agente faturadas.

- `python3 assets/bin/skills.py selftest` — o leitor de seção prova o contrato contra a **mesma lista
  canônica de casos** que `specs.py section` prova, pelo precedente que
  `docs/standards/code/canonical-set-parsing.md` já estabelece para uma regra compartilhada entre
  scripts independentes.
- `python3 assets/bin/specs.py selftest` — a forma plural de `section` contra a mesma lista.
- `python3 assets/hooks/okf-validate.py selftest` e `python3 assets/hooks/okf-validate.py assets/docs`
  → 0 error(s), 0 warning(s).
- `python3 assets/bin/skills.py --root . doctor --json` → 26 comandos, 0 findings;
  `lint --json` sem regressão.
- **A medição antes/depois do preâmbulo**, em chars, por código lendo os arquivos em disco: o que
  `/quenching:specs:execute` carrega hoje (68k tokens estimados) contra o que carrega depois, para a
  mesma spec de referência. Reportada como contagem de arquivo mais aritmética, **nunca** como
  medição de transcript — a distinção que `docs/standards/automation/session-evidence.md` §The rule a
  counted claim must obey impõe.
- **A fração de racional das cinco referências**, medida pelos marcadores depois de aplicados. A
  estimativa de ~25–35% do `## Problem` é chute declarado; o número medido é o que entra no standard.
- **Fallback do `--rules-only` provado**: uma seção sem marcador devolve a seção inteira e **diz que
  não havia marcador**. Um marcador ausente nunca pode virar resposta vazia.
- **A oferta de parar não é provável por teste** — nenhuma edição em `commands/**` é testável na
  sessão que a escreve. A prova é `doctor` mais a distribuição de tamanho das specs de `plans/` que
  decide o gatilho, medida em disco. O ganho de 1/7 é **aritmética declarada sobre a integral**, não
  medição de run, e `## Risks` carrega a hipótese que ela assume.
- O lockstep de versão: `VERSION` e as três ferramentas shipped concordam (quatro, se
  `## Open Decisions` decidir por um script novo).
- **Nenhum `verify:` deste spec dispara sessão de agente faturada.** `execution.md` §The verification
  policy já proíbe; declarado aqui porque este spec edita justamente esse arquivo.

## Design

- **Decisão: a unidade de leitura é a seção, e a unidade de decisão é o arquivo declarado.** São duas
  regras do mesmo princípio em escalas diferentes — *qual arquivo abrir* (o que `## Impact` declara,
  não a pasta) e *quanto do arquivo ler* (as seções citadas, não o arquivo). O passo 4 hoje erra nas
  duas, e a primeira é a mais cara: 38k tokens de pasta contra ~9k dos cinco arquivos declarados.
- **Decisão: um resolvedor genérico, e `specs.py section` continua dono das specs.** Não se funde
  nada: uma seção de spec é um **contrato parseado** (as catorze headings canônicas, validadas), uma
  seção de referência é markdown livre. O que é compartilhado é a *regra*, não o código — exatamente o
  padrão que `docs/standards/code/canonical-set-parsing.md` e `frontmatter-parsing.md` já
  estabelecem: cada script stdlib-only implementa, e os dois provam contra a **mesma lista canônica de
  casos** no `selftest`. Fundir os scripts é assunto do
  `check-canonical-cases-and-map-the-scripts` e não é aberto aqui.
- **Decisão: N seções em UMA chamada, nas duas ferramentas.** O ganho de ler por seção (−37,4% medido
  em `cut-execute-context-integral`) é anulado se custar quatro turnos extras **no início**, onde um
  turno é repago por todos os seguintes. A forma plural não é conveniência, é a metade do resultado.
- **Decisão: o frontmatter não volta na leitura por seção.** ~1.424 chars (~350 tokens) por arquivo
  OKF, que um leitor de seção não tem motivo para carregar. Vinte arquivos lidos são ~7k tokens de
  cabeçalho.
- **Decisão: `--rules-only` lê marcador, nunca heurística.** Um modelo decidindo a cada leitura o que
  é regra e o que é racional é não-determinístico e a falha é silenciosa — uma frase vinculante
  descartada não aparece em lugar nenhum. O marcador é escrito uma vez, por quem escreve a regra, e a
  leitura é mecânica.
- **Decisão: sem marcador, `--rules-only` devolve a seção inteira e reporta a ausência.** A degradação
  é para o comportamento de hoje, nunca para o vazio. Uma convenção que só é aplicada em cinco
  arquivos não pode transformar os outros dezoito em silêncio.
- **Decisão: compactar por relocação, nunca por deleção.** A regra sobe para o topo em forma
  imperativa; a medição, o que foi revertido e o v1 que falhou descem para `<!-- rationale -->`. Nada
  sai do arquivo. É o que reconcilia o corte de custo com o contrato que este repo já tem —
  `plugins/quenching/assets/references/specs-execute/execution.md` §Why a marker and not a counter é o
  exemplo: cara em contexto, insubstituível em disco.
- **Decisão: a delegação continua permitida e passa a declarar seu custo.** `execution.md`
  §Delegating an executor não muda de permissão; ganha a conta: um sub-agente não compartilha o prompt
  cache da sessão, então N tasks sobre o mesmo arquivo grande pagam N leituras frias. Delegar por
  **arquivo ou por seção de tasks**, não por task, e o self-review dos quatro itens acontece **dentro**
  do sub-agente, que devolve veredito — senão o diff volta para o contexto longo e a economia vaza no
  turno seguinte.
- **Decisão: a fronteira de seção é o ponto de corte, e o gatilho é evento.** Uma seção de `## Tasks`
  é a menor unidade independentemente entregável que a frente já define (`per-section` é a política
  de verificação default pela mesma razão), então parar ali não deixa nada meio-feito. O gatilho é
  evento — "acabou uma seção e há outra pela frente" — e nunca um limiar de janela: um número
  inventado antes de medir fixa o resultado, e é a mesma disciplina que fez a cadência do
  `## Handoff` ser quatro eventos em vez de um julgamento de "quando ficou obsoleto".
- **Decisão: a oferta não custa trilho novo.** `## Handoff` (já com cadência de quatro eventos, uma
  delas o último commit da run), o `git log` e os `subjects` que `specs.py status` devolve **já** são
  a retomada completa. Se a oferta exigisse escrever um estado a mais, ela estaria movendo custo em
  vez de cortá-lo — e é exatamente por a retomada já estar paga que o corte é quase grátis.
- **Decisão: oferece, nunca impõe, e nunca encerra sozinha.** Uma run desatendida que decide parar
  troca um custo por uma surpresa. A oferta nomeia o comando que retoma e segue se ninguém responder
  o contrário.
- **Decisão: nenhum arquivo é dividido.** Ver `## Alternatives Considered` — a conta de segmentar está
  lá e é o argumento inteiro.

## Alternatives Considered

Quatro formas foram comparadas. A escolhida está em `## Proposal`; as três derrotadas ficam aqui com a
razão medida de terem perdido.

- **Segmentar mais: uma seção por arquivo, mais pastas, alvo mais fino.** Levar os 50 arquivos de
  `docs/standards/**` e `assets/references/**` às suas 315 seções custaria **265 frontmatters novos ×
  1.424 chars = ~371k chars (~93k tokens)**, um crescimento de ~76% sobre os 488k atuais — puro
  cabeçalho. Mais 265 linhas de `index.md` regeneradas em pastas que passariam a ter 40+ entradas,
  mais cada citação de cada corpo repontada, mais a conformância `okf-*` acompanhando. E não resolve a
  causa: N seções continuam sendo N leituras, ou seja **N turnos**, que é a metade da integral que
  ler por seção pretendia melhorar. Rejeitada por pagar 93k de overhead para não atacar o problema.
- **Compactar: apagar o racional dos documentos.** Barato e imediato. Rejeitada porque apaga o único
  ativo que um LLM não reconstrói — o *porquê* de uma regra é o que impede a próxima sessão de
  "consertar" uma decisão deliberada — e porque contradiz um contrato que o repo já escreveu em três
  lugares ("preserva a narrativa antiga como o que foi revertido"). O que sobrevive dela está na
  decisão de compactar **por relocação** em `## Design`.
- **Sem ferramenta: cada corpo embute um `awk`/`sed` que imprime de `## X` até o próximo `## `.**
  Custo zero de implementação e nenhum script novo no lockstep. Rejeitada por três razões: seria
  duplicada em até 26 corpos sem dono único, não removeria o frontmatter nem honraria os marcadores, e
  quebra em qualquer seção que contenha um bloco de código com `## ` — o que várias contêm. O repo já
  decidiu esse tipo de questão a favor de uma regra com dono (`frontmatter-parsing.md`).

## Open Decisions

- **Onde mora o verbo de leitura de seção.** Em `skills.py` (nenhum script novo, nenhuma string nova
  no lockstep, mas o verbo não tem nada a ver com a superfície de comandos que aquele script governa)
  ou num quarto script shipped (coeso, e custa uma string a mais no lockstep de versão mais uma linha
  no `README.md`). **Decidido na** task 2.1, medindo as duas contra
  `docs/standards/architecture/plugin-layout.md` e `docs/standards/ci-cd/versioning-release.md`; a
  inclinação é `skills.py`, por o lockstep de quatro strings ser um custo permanente contra uma
  incoerência de nome que uma linha de `--help` resolve.
- **Se os marcadores `<!-- rules -->` / `<!-- rationale -->` valem para as 23 referências ou só para
  as cinco que `/quenching:specs:execute` carrega.** **Decidido na** task 3.4, depois de a fração real
  de racional ser medida nas cinco — se ela for pequena, aplicar às outras dezoito é trabalho sem
  retorno, e o fallback já garante que a ausência não custa nada.
- **Se um marcador ausente vira finding do `lint`.** Um aviso por seção sem marcador é honesto e vira
  ruído permanente em dezoito arquivos que podem legitimamente não querer a convenção. **Decidido**
  depois de a convenção ter rodado uma vez, nunca antes — é a mesma disciplina que
  `context-budget.md` aplica ao próprio teto.
- **Qual evento dispara a oferta de parar.** "Toda fronteira de seção" é previsível e vira ruído numa
  spec de duas seções; "fronteira de seção com pelo menos N seções restantes" precisa de um N.
  **Decidido na** task 5.1, contra a distribuição real de tamanho das 33 specs de `plans/` — que é
  medição em disco, não chute.
- **Se o passo 4, ao ler só os `docs/standards/` declarados, precisa de uma rede de segurança.** Hoje
  `sp-impact-uncovered` avisa quando um standard declarado não tem task; não existe o inverso — um
  standard vinculante que ninguém declarou. **Decidido na** task 1.1, olhando se o aviso existente já
  cobre o caso ou se a narrativa do passo basta.

## Risks

- **Ler por seção esconde contexto que a leitura inteira dava de graça.** Uma edição informada pelo
  arquivo todo pode ser melhor que uma informada por uma seção, e a diferença **não aparece numa
  medição de tokens**. `ACCEPTED` — é o mesmo risco que `cut-execute-context-integral` registrou.
  *Mitigação:* o leitor aceita N seções numa chamada, então a resposta a "faltou contexto" é pedir
  mais seções, não voltar ao arquivo; e o `## Contents` das referências continua sendo o índice que
  diz o que existe para pedir.
- **O passo 4 narrowed perde um standard vinculante que ninguém declarou.** Um contrato que a task
  deveria obedecer e que `## Impact` não nomeia deixa de ser lido. *Mitigação:* `## Impact` é
  justamente o lugar onde a frente já exige essa declaração, `sp-impact-uncovered` já cobre metade do
  caso, e `## Open Decisions` decide se falta rede para a outra metade — em vez de presumir que falta.
- **A convenção de marcadores apodrece em silêncio.** Uma seção nova escrita sem marcador retornaria
  vazio sob `--rules-only`, e o comando seguiria como se a regra não existisse — uma falha silenciosa
  e permanente, do tipo que este repo trata como a pior classe. *Mitigação mecânica, não de
  julgamento:* o fallback devolve a seção inteira e **reporta a ausência do marcador**, e
  `## Validation` exige que esse caminho seja provado.
- **Parar e retomar move custo em vez de eliminá-lo** se a sessão nova precisar reler muito para
  recuperar o estado. É precisamente o que o `## Handoff` existe para impedir, mas isso é a hipótese a
  medir, não um fato estabelecido — e o ganho de 1/7 assume que a retomada custa aproximadamente zero.
  *Mitigação:* a oferta nomeia o comando que retoma e nada mais é escrito; se a retomada se revelar
  cara, o que aumenta é o `## Handoff`, que é lido a cada task e cujo tamanho a §6 do corpo já
  restringe.
- **Os números do `## Problem` são contagem de arquivo mais aritmética, não medição de transcript.**
  Os únicos números de run que ele cita (344 turnos, 17,4M, −37,4%) vêm de `cut-execute-context-integral`,
  que carrega `authority: background` por vir de **uma** run. *Mitigação:* `## Validation` obriga cada
  figura a dizer de qual das duas naturezas ela é, e `read-discipline.md` nasce
  `authority: background` até ter rodado em mais de um contexto.
- **Os marcadores tocam cinco arquivos que `/quenching:specs:execute` carrega enquanto roda.** Editar
  a referência que o próprio comando está lendo é confuso de raciocinar. *Mitigação:* o registry e o
  contexto são montados no início da sessão — a edição vale para a **próxima** run, nunca para a
  corrente, e `## Handoff` diz isso.
- **Um quarto script shipped, se `## Open Decisions` escolher assim, é um custo permanente** de
  lockstep em toda release. `ACCEPTED` se escolhido — a decisão registra o preço em vez de descobri-lo
  na primeira release depois.

## Handoff

- **A ordem das seções é deliberada e a seção 1 é independente do resto.** Ela usa só o que já existe
  (`specs.py section`, no singular) e entrega o maior retorno por linha editada — os ~38k tokens de
  pasta do passo 4. Se tudo depois dela parar, o corte principal já está em pé.
- **Nenhuma edição em `commands/**` é testável na sessão que a escreve** — o registry é montado no
  início da sessão. As seções 1 e 4 terminam em `doctor`, nunca em teste funcional. O mesmo vale para
  as referências da seção 3: elas são lidas no início da run, então a edição vale para a **próxima**.
- **A seção 5 é a única que muda o FLUXO da run, e vem depois de tudo que muda a leitura.** Não é
  ordem estética: a oferta de parar só vale a pena com o `## Handoff` sendo o trilho completo, e a
  §4.2 mexe justamente na disciplina de contexto que a antecede. Ela também é a única cujo ganho —
  ~1/7 — é aritmético e não medido, então chegar por último é chegar com mais evidência ao redor.
- **O slug nomeia a metade dominante, não o todo.** Depois de a `cut-execute-context-integral` ser
  subsumida, este spec carrega dois cortes: abrir menos (seções 1–4) e rodar menos tempo (seção 5).
  O slug ficou como a identidade que já foi estampada; `docs/standards/automation/context-discipline.md`
  é onde o nome do princípio inteiro passa a viver.
- **Este spec toca `specs.py` apenas no verbo `section`.** `configurable-spec-backend` e
  `rethink-specs-workflow-for-claude-code` reescrevem partes grandes do mesmo arquivo; manter o
  toque mínimo é o que permite as três coexistirem sem ordem imposta.
- **A convenção da seção 3 é aditiva por construção**: o fallback do `--rules-only` faz um arquivo sem
  marcador se comportar exatamente como hoje. Nenhuma das dezoito referências não tocadas regride.
- **Nenhum `verify:` deste spec pode disparar sessão de agente faturada** — `functional-checks.sh` e
  `/quenching:skill:eval` pertencem à frente skill e ficam fora daqui, o que é especialmente
  importante num spec que edita `execution.md` §The verification policy.
- **A conta de delegação da task 4.2 é aritmética declarada, não medição de run:** ~13 × 37k contra
  ~150k, sob a premissa de que um sub-agente não compartilha o prompt cache da sessão. Escrever isso
  em `execution.md` como estimativa — e dizer que é estimativa — é o contrato; afirmá-la como medida
  não é.

## Tasks

### 1. Estreitar o que o passo 4 abre

- [ ] 1.1 Reescrever o passo 4 de `/quenching:specs:execute`: ler os `docs/standards/` que
      `## Impact` declara mais os que a task corrente nomeia, nunca a pasta `docs/standards/<subject>/`;
      decidir per ## Open Decisions se falta rede de segurança para um standard não declarado
      files: plugins/quenching/commands/specs/execute.md
- [ ] 1.2 No mesmo passo, trocar o `Read` do arquivo da spec por `specs.py section` para as seções
      que ele exige, e dizer que é UMA chamada
      files: plugins/quenching/commands/specs/execute.md
- [ ] 1.3 Medir e registrar o preâmbulo antes/depois em chars, por código lendo os arquivos em disco
      verify: python3 assets/bin/skills.py --root . doctor --json

### 2. O resolvedor de seção

- [ ] 2.1 Decidir per ## Open Decisions onde o verbo mora e implementá-lo:
      `read <path> --sections "A,B"` — N seções numa chamada, sem frontmatter, exit 2 nomeando a
      seção quando ela não existe
      files: plugins/quenching/assets/bin/skills.py
      verify: python3 assets/bin/skills.py selftest
- [ ] 2.2 `specs.py section` ganha a forma plural, com o mesmo contrato de saída
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 assets/bin/specs.py selftest
- [ ] 2.3 A lista canônica de casos de seção provada pelas DUAS ferramentas, per o precedente de
      canonical-set-parsing.md — incluindo a seção que contém um bloco de código com `## ` dentro
      verify: python3 assets/bin/skills.py selftest && python3 assets/bin/specs.py selftest

### 3. A convenção regra/racional

- [ ] 3.1 `--rules-only` sobre os marcadores `<!-- rules -->` / `<!-- rationale -->`, com fallback
      para a seção inteira reportando a ausência do marcador
      files: plugins/quenching/assets/bin/skills.py
      verify: python3 assets/bin/skills.py selftest
- [ ] 3.2 Aplicar os marcadores em specs-execute/execution.md, sem remover uma linha de prosa
      files: plugins/quenching/assets/references/specs-execute/execution.md
- [ ] 3.3 Aplicar os marcadores nas outras quatro referências que /quenching:specs:execute carrega
      files: plugins/quenching/assets/references/specs-isolate/git.md, plugins/quenching/assets/references/specs-develop/spec-driven.md, plugins/quenching/assets/references/docs-add/homes.md, plugins/quenching/assets/references/docs-align/conformance.md
- [ ] 3.4 Medir a fração real de racional nas cinco e decidir per ## Open Decisions se a convenção
      se estende às outras dezoito
      verify: python3 assets/bin/skills.py --root . lint --json

### 4. A superfície passa a usar

- [ ] 4.1 `/quenching:specs:execute` cita as referências pelo leitor de seção em vez de por caminho
      de arquivo, e o corpo diz por quê numa linha
      files: plugins/quenching/commands/specs/execute.md
- [ ] 4.2 `execution.md` §Delegating an executor passa a declarar o custo real: sub-agente não
      compartilha o prompt cache, N tasks sobre o mesmo arquivo grande pagam N leituras frias;
      delegar por seção de tasks, e o self-review dos quatro itens acontece dentro do sub-agente
      files: plugins/quenching/assets/references/specs-execute/execution.md
- [ ] 4.3 Confirmar a superfície: doctor com 26 comandos e 0 findings, lint sem regressão
      verify: python3 assets/bin/skills.py --root . doctor --json

### 5. A fronteira de seção

- [ ] 5.1 Decidir per ## Open Decisions qual evento dispara a oferta, medindo a distribuição de
      tamanho das specs de plans/ em disco
      verify: python3 assets/bin/specs.py list --json
- [ ] 5.2 `/quenching:specs:execute` passa a oferecer parar na fronteira de seção, nomeando o comando
      que retoma; oferece e nunca impõe, e nunca encerra sozinha
      files: plugins/quenching/commands/specs/execute.md
- [ ] 5.3 O passo 6 (`## Handoff`, quatro eventos) declara que a fronteira de seção é retomada pelo
      trilho que ele já mantém, sem escrever estado novo
      files: plugins/quenching/commands/specs/execute.md, plugins/quenching/assets/references/specs-execute/execution.md
- [ ] 5.4 Confirmar a superfície depois das três edições de corpo
      verify: python3 assets/bin/skills.py --root . doctor --json

### 6. Os standards

- [ ] 6.1 Escrever docs/standards/automation/context-discipline.md — as duas metades da integral,
      abrir menos e rodar menos tempo (authority: background — uma medição, um repo)
      verify: python3 assets/hooks/okf-validate.py docs
- [ ] 6.2 Revisar docs/standards/automation/context-budget.md §The other half para apontar para o
      dono novo sem absorvê-lo, preservando a narrativa da medição que ela já carrega
      verify: python3 assets/hooks/okf-validate.py docs

### 7. Fechamento

- [ ] 7.1 O skeleton shipped segue conformante e o lockstep de versão concorda
      verify: python3 assets/hooks/okf-validate.py assets/docs && cat VERSION
- [ ] 7.2 README.md — só se 2.1 tiver escolhido um quarto script shipped
      files: plugins/quenching/README.md
