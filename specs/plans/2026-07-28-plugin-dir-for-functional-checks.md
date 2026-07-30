---
slug: plugin-dir-for-functional-checks
title: Make functional-checks.sh witness which plugin copy it graded
verification: per-section
priority: {level: 10, criticality: high, complexity: 2, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# Make functional-checks.sh witness which plugin copy it graded

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

Este repo tem um único jeito de saber se uma mudança nos comandos realmente funciona: um script que
abre sessões novas do Claude Code e observa o que elas fazem. Para isso ele precisa carregar a cópia
do plugin que está sendo editada — e por um tempo carregava outra, uma cópia velha guardada em cache
pela instalação. O `## Problem` conta essa medição e conta também que o conserto (uma flag,
`--plugin-dir`) já entrou em disco por fora deste spec.

O que este spec faz é fechar a metade que ficou aberta: o script usa a flag, mas nada dentro dele
verifica que a flag continua surtindo efeito. Um run em que a cópia errada voltasse a ser carregada
ficaria verde do mesmo jeito. O `## Proposal` lista o que passa a ser verdade depois disso, e o
`## Design` explica por que a solução são duas guardas separadas — uma que lê o próprio script, outra
que lê a captura que o script já produz — e por que nenhuma das duas custa uma sessão a mais. Essa
economia é o motivo pelo qual as alternativas mais óbvias perderam, o que o
`## Alternatives Considered` registra.

A tensão central está em `## Risks`, e vale ler antes das tasks: este harness nunca ficou vermelho por
regressão de superfície, só por defeito nele mesmo. Acrescentar asserção a ele é acrescentar
exatamente a superfície que costuma gerar alarme falso — por isso as duas guardas são determinísticas
e provadas contra uma captura escrita à mão antes de entrarem. É também por isso que `## Validation`
não gasta agente: as três provas obrigatórias rodam sem abrir sessão, e a única sessão prevista existe
para responder a uma pergunta de `## Open Decisions`, não para aprovar uma task.

`## Out of Scope` importa aqui porque três specs diferentes mexem neste mesmo script: a fronteira
deste é a testemunha, não o que os probes escrevem nem os checks que faltam — `## Risks` nomeia os
dois irmãos e `## Handoff` repete a instrução para quem executar. E `## Open Decisions` guarda duas
perguntas que ninguém respondeu por conta própria: uma empírica, sobre como um caminho de plugin
aparece na captura, e uma que é do dono do spec — aceitar este reescopo ou fechá-lo como já resolvido.

As doze tasks estão em quatro grupos, na ordem em que dependem uma da outra: a guarda estática, a
âncora com sua fixture, o cabeçalho e o standard, e o fechamento das duas decisões abertas.

## Problem

`functional-checks.sh` gera um `claude -p` por check. Até 2026-07-28, os checks 1-3 rodavam num
sandbox cujo `.claude/settings.json` copiava o `enabledPlugins` deste repo, então o plugin era
carregado **pela registração do marketplace** — de `~/.claude/plugins/cache/`, não do checkout em
que o script foi invocado. Medido em 2026-07-28: o cache servia **3.0.0**, uma árvore que ainda
carregava `commands/align-and-update.md`, apagado em 4.2.0. O único check do repo para uma mudança
em `commands/**` estava avaliando uma cópia que ninguém editava — e passando.

**Esse conserto já está em disco, e não veio deste spec.** O commit `b825f1b` (2026-07-29,
"funcitonal-checks fix") passou `--plugin-dir "$PLUGIN"` nas quatro invocações
(`plugins/quenching/assets/checks/functional-checks.sh:158,184,228,269`), trocou o sandbox por
`newbox()`, que grava `{}` em `.claude/settings.json` e habilita plugin nenhum (linhas 126-136), e
escreveu a precondição 5 em `docs/standards/quality/surface-verification.md:92-100`. O script depois
migrou de `assets/bin/` para `assets/checks/` no commit `af58a52`.

O que sobra é a metade que o conserto não cobriu: **nenhuma asserção do harness testemunha qual
cópia foi carregada.** As asserções são escritas por caminho relativo, nunca ancoradas em `$PLUGIN`.
O check 1 faz `grep -q '/assets/references/'` (linha 165), e um `Read` em
`~/.claude/plugins/cache/claude-quenching/quenching/3.0.0/assets/references/...` casa com esse
padrão exatamente como o caminho do checkout casa. A metade negativa do check 4
(`grep -q 'hooks/skills.py'`, linha 280) tem o mesmo furo. Ou seja: **um pass e um falso-pass
continuam indistinguíveis**, que é precisamente a condição que deixou a regressão anterior passar
dias sem ser vista.

O ambiente segue armado para ela. Hoje `~/.claude/plugins/installed_plugins.json` registra
`quenching@claude-quenching` com `installPath` em `.../cache/claude-quenching/quenching/3.0.0`,
commit `d0908ff`, enquanto `plugins/quenching/VERSION` está em `4.4.0`. O `--plugin-dir` é, hoje,
uma convenção sustentada por quatro literais dentro do script; nada mede que ela continua valendo.

**Por que agora.** A ordenação do gate pré-merge descrita em
`docs/standards/quality/surface-verification.md:146-166` depende da precondição 5 ser verdadeira: só
com `--plugin-dir` o harness passou a enxergar um branch ou um worktree, e é isso que autoriza
`/specs:conclude` a rodar o gate **antes** do merge em vez de reportar depois dele. Se a precondição
regredir em silêncio, esse gate avalia a árvore errada e a justificativa da ordenação cai sem que
nenhum run fique vermelho.

## Proposal

- O harness deixa de confiar numa convenção e passa a **medir** que carregou o checkout sob teste:
  cada run afirma, ou nega, que as sessões enxergaram a cópia em `$PLUGIN`.
- Um autocheck **de custo zero** roda antes do primeiro `claude -p` e derruba o run se alguma
  invocação perdeu o `--plugin-dir`, ou se o `enabledPlugins` voltar para dentro do script. A regra é
  contagem, não enumeração: tantos `--plugin-dir` quantos `claude -p` fora de comentário.
- Toda asserção sobre caminho observado ganha âncora: nenhum caminho lido ou executado pelas sessões
  pode vir de um diretório de cache ou de marketplace do Claude Code.
- Um falso-pass da espécie medida em 2026-07-28 deixa de ser silencioso: ele aparece como um FAIL
  nomeado, com o caminho observado impresso, em vez de um run verde.
- As asserções novas são exercitáveis **sem gerar sessão nenhuma**, contra uma captura sintética em
  disco — provar esta mudança não custa agente.
- Nenhum veredito atual muda: o padrão continua checks 1, 2, 4, o check 3 continua opt-in, e os
  códigos de saída continuam `0` / `1` / `2` com o mesmo significado.

## Out of Scope

- **Resíduo do check 3 dentro de `specs/plans/`** — é do spec irmão `isolate-functional-checks-probes`.
  Aqui garante-se apenas que a caixa do probe não habilita plugin algum; o que o probe escreve dentro
  dela não é assunto deste spec.
- **Um probe que observe um bloco `hooks:` de frontmatter disparar** — é do spec irmão
  `probe-a-frontmatter-hook-firing`. Este spec não acrescenta check novo nem sessão nova; ele ancora
  as asserções que já existem.
- **Consertar o cache stale (`3.0.0` em `installed_plugins.json`) ou reinstalar o plugin pelo
  marketplace.** O ponto deste spec é o harness não depender disso. Deixar o cache velho onde está é
  até útil: ele é a fixture natural do falso-pass.
- **Rever quem roda o harness e quando.** Já decidido, com evidência, em
  `docs/standards/quality/surface-verification.md:107-130` — dono é o front do skill, escopo é o
  `--only`. Reabrir aqui seria refazer uma medição.
- **Dar `--version` aos scripts de `assets/checks/` ou colocá-los no lockstep.** Eles ficam
  deliberadamente fora dele (`plugins/quenching/assets/README.md:78`), e um dono a mais no release
  não é o problema em questão.
- **Mudar o que os checks 1, 2 e 4 medem.** Prompt, cap de turnos e alvo de cada check ficam como
  estão; só a comparação de caminho fica mais estrita.
- **Escrever um standard novo em `docs/standards/`.** Corte de escopo tomado na crítica: a regra já
  existe como precondição 5 em `docs/standards/quality/surface-verification.md:92-100`. Este spec
  emenda esse doc para dizer que a precondição passou a ser **testemunhada**, e não cria doc nenhum.
  Um segundo doc sobre a mesma regra seria a divergência silenciosa que o próprio bundle proíbe.
## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/quality/surface-verification.md` — a precondição 5 passa a registrar que a flag é
  **testemunhada** pelo próprio harness, com as duas guardas nomeadas e a razão de a negativa ser a
  obrigatória. Emenda de doc existente, `authority: current` já vigente; nenhum doc novo.

### Standards at `authority: background` this spec may resolve

- none — nenhum standard vinculado a este trabalho está em `background`. A precondição 5 já entrou
  como `current` no commit `b825f1b`, e `docs/standards/architecture/plugin-layout.md` também é
  `current`.

### Product code this spec expects to touch

- `plugins/quenching/assets/checks/functional-checks.sh` — o único arquivo de código alterado: a
  guarda estática no topo, a função de âncora, e as asserções de caminho dos checks 1 e 4.

Fora dessa lista, nada. Sem tocar em `commands/**`, sem tocar nos três scripts do lockstep
(`specs.py`, `skills.py`, `okf-validate.py`), sem tocar em `assets/references/**`. É o que mantém o
`/skill:eval` e a suíte de selftests inteiramente fora do caminho crítico deste spec.

## Validation

Toda a verificação obrigatória deste spec é **de custo zero em sessão de agente**. Isso é
deliberado: `docs/standards/quality/surface-verification.md:107-130` proíbe pôr este harness no
`verify:` de uma task, e nenhuma task abaixo o faz.

```bash
cd plugins/quenching

# 1. a guarda estática, sozinha, sem gerar nenhuma sessão
./assets/checks/functional-checks.sh --selfcheck
#    espera-se: exit 0 e uma linha PASS por invariante
#    (contagem de `claude -p` igual à de `--plugin-dir`; nenhum `enabledPlugins` fora de comentário)

# 2. a guarda estática pega a regressão de verdade — prova por negação
cp assets/checks/functional-checks.sh /tmp/fc.sh
sed -i '0,/claude -p --plugin-dir/{s/claude -p --plugin-dir "\$PLUGIN"/claude -p/}' /tmp/fc.sh
bash /tmp/fc.sh --selfcheck
#    espera-se: exit 1, e a mensagem nomeando a invocação sem `--plugin-dir`

# 3. a âncora de caminho, contra captura sintética, também sem sessão
./assets/checks/functional-checks.sh --selftest
#    espera-se: exit 0 — a fixture com um Read sob $PLUGIN/assets/references/ passa,
#    e a fixture com um Read sob .../plugins/cache/... reprova
```

**Invariantes que precisam continuar valendo depois da mudança**, cada um checável sem sessão:

- os códigos de saída seguem `0` medido e passou · `1` alguma asserção falhou · `2` nada pôde ser
  medido (`assets/checks/functional-checks.sh:288-302`);
- `--only 3` continua opt-in e o padrão continua `1,2,4` (linha 48);
- toda asserção nova continua dentro do gate `evidence()`, então um run sem captura continua saindo
  `2` e não `1`;
- `./assets/checks/functional-checks.sh --help` continua imprimindo o cabeçalho inteiro (linha 55),
  agora incluindo a descrição das duas guardas.

**Uma confirmação ao vivo, uma vez, autorizada pelo humano — e explicitamente não é `verify:` de
task.** Depois de a mudança entrar, um único `./assets/checks/functional-checks.sh` (padrão: checks
1, 2, 4) roda a partir do front do skill, para responder à decisão aberta sobre canonização de
caminho: espera-se `6 passed, 0 failed` e a linha da âncora positiva mostrando o caminho observado.
Um `exit 2` aqui é inconclusivo, não é pass. Essa é a única despesa em agente que este spec prevê, e
ela existe para fechar `## Open Decisions`, não para gradar uma task.

## Design

### Decisão 1 — duas guardas independentes, a de graça primeiro

Existem dois modos distintos de o harness voltar a avaliar a cópia errada, e uma guarda não cobre o
outro modo:

| Guarda | O que ela pega | Custo | Quando roda |
| --- | --- | --- | --- |
| autocheck estático do próprio script | a **fonte**: alguém escreve um `claude -p` novo sem `--plugin-dir`, ou devolve `enabledPlugins` ao `newbox()` | zero — é `grep` no próprio arquivo | antes do primeiro check, uma vez |
| âncora nos caminhos observados | o **ambiente**: um `$REPO` errado no argumento posicional, um symlink, um `enabledPlugins` vindo de settings de usuário | zero — reusa a captura que já é lida | dentro de cada asserção existente |

A estática vem primeiro e é incondicional porque é a única que funciona quando nenhuma sessão chegou
a rodar.

### Decisão 2 — o autocheck conta, não enumera

Uma guarda que lista os checks conhecidos apodrece no dia em que existir um check 5. A regra é
contagem sobre o próprio `${BASH_SOURCE[0]}`: o número de linhas **não comentadas** contendo
`claude -p` tem de ser igual ao número contendo `claude -p --plugin-dir`, e o script inteiro não pode
conter `enabledPlugins` fora de comentário.

A armadilha aqui é real e precisa estar no código: o cabeçalho do próprio script fala de `claude -p`,
de `--plugin-dir` e de `enabledPlugins` em prosa (linhas 4-15). Um `grep` ingênuo conta comentário.
Filtrar as linhas cujo primeiro caractere não-branco é `#` é obrigatório, e é isso que mantém a
guarda honesta enquanto o cabeçalho cresce.

### Decisão 3 — a metade obrigatória da âncora é a negativa

A âncora positiva (o caminho observado começa com `$PLUGIN`) é a mais forte e a mais frágil: se o
Claude Code canonizar, resolver symlink ou copiar o diretório passado em `--plugin-dir`, o prefixo
observado não bate com a string que o script passou, e uma asserção correta vira FAIL. A âncora
negativa (nenhum caminho observado contém `/plugins/cache/` nem `/plugins/marketplaces/`) não tem
essa fragilidade: ela nomeia exatamente o diretório de onde a cópia errada é servida.

Então: a negativa é a asserção que grada. A positiva entra também, e quando ela falha **imprime o
caminho observado ao lado do `$PLUGIN` esperado**, para que uma surpresa de canonização seja
diagnosticável na primeira linha do output em vez de virar mistério.

### Decisão 4 — nenhuma asserção nova pode deixar um run sem evidência vermelho

As asserções novas ficam **dentro** do `if evidence "$WORK/N.jsonl"` que já existe (linhas 98-109,
164, 189, 277). Uma âncora negativa passa vaziamente sobre captura vazia, que é exatamente a falha
que a precondição 4 nomeia (`docs/standards/quality/surface-verification.md:80-90`); e uma âncora
positiva sobre captura vazia falharia por falta de evidência, não por veredito. Sem evidência
continua `inconc`, e o run continua saindo `2`.

### Decisão 5 — tudo dentro de `functional-checks.sh`, sem arquivo novo

`docs/standards/architecture/plugin-layout.md:139-146` é vinculante aqui: dar dois nomes ao mesmo
defeito é proibido. A guarda mora no script que ela protege, não num tool novo, não num arquivo novo
em `assets/checks/`, e não como `verify:` de outro comando. Um defeito, um nome, um dono.

### Decisão 6 — as asserções novas se provam contra captura sintética

O que muda é a comparação de string sobre um `.jsonl` já capturado, e um `.jsonl` pode ser escrito à
mão. Uma fixture com dois eventos `tool_use` — um `Read` sob `$PLUGIN/assets/references/` e um `Read`
sob um caminho de `/plugins/cache/` — prova a âncora nos dois sentidos sem gerar sessão. Isso é o que
permite este spec ter `verify:` de verdade sem contrariar
`docs/standards/quality/surface-verification.md:107-130`, que proíbe pôr o harness no `verify:` de uma
task.

### Decisão 7 — o defeito vizinho já tem nome, e não é este

`skills.py drift` é o check mais próximo que existe, e foi verificado que ele mede outra coisa:
compara as cópias **instaladas** em `.claude/hooks/` com o `VERSION` embarcado, emitindo
`sk-tool-absent` e afins. Ele nada diz sobre qual cópia do plugin o Claude Code carregou numa sessão
— aliás, é justamente o check 4 do harness que prova que a chamada de `drift` sai da cópia do plugin
e não da instalada (linhas 278-281). Dois defeitos distintos, dois nomes distintos, nenhuma
duplicação a resolver.

### Decisão 8 — dois modos novos, porque `--only` não serve de autocheck

A verificação deste spec tem de ser de custo zero, e o `--only` que já existe não entrega isso: com
`ONLY` vazio nenhum check roda, `PASS` fica em 0 e o script sai **2** por desenho (linhas 298-301) —
"nada pôde ser medido". Um autocheck aprovado que sai 2 é pior do que nenhum, porque treina o
operador a ignorar o código de saída.

Então entram dois modos, ambos sem sessão e ambos saindo 0 ou 1:

- `--selfcheck` — roda só a guarda estática de contagem e sai.
- `--selftest` — roda a função de âncora contra a captura sintética e sai.

São dois e não um porque medem coisas diferentes: um lê o script, o outro lê uma captura. Juntá-los
num só flag daria um veredito que não diz qual metade caiu.

### Contratos que este desenho não pode contrariar

- `docs/standards/quality/surface-verification.md:80-90` (precondição 4) — falta de evidência é
  `inconc`, nunca FAIL; e a metade negativa passa vaziamente, por isso segue atrás do gate.
- `docs/standards/quality/surface-verification.md:92-100` (precondição 5) — a regra que este spec
  passa a testemunhar, em vez de reescrever.
- `docs/standards/quality/surface-verification.md:132-145` (§Scope the run) — nenhuma sessão nova, e a
  conta de sessões por subconjunto fica idêntica.
- `docs/standards/architecture/plugin-layout.md:87-97` — a citação por `${CLAUDE_PLUGIN_ROOT}` é o
  mecanismo sob teste: são 26 command bodies que dependem dele substituir para a cópia certa.
- `plugins/quenching/assets/README.md:78` — `assets/checks/` grada este checkout e não é payload de
  nada; nada aqui entra no lockstep de versão.
## Alternatives Considered

| Abordagem | Custo | O que compra | O que fecha |
| --- | --- | --- | --- |
| **A. Autocheck estático + âncora negativa nos caminhos** (escolhida) | ~15 linhas num script, zero sessão | pega a regressão na fonte e no ambiente; provável por fixture | nada — as duas guardas são removíveis em separado |
| B. Só a âncora positiva em `$PLUGIN` | ~6 linhas | a afirmação mais forte possível | frágil a canonização de caminho: um FAIL falso convida a apagar a guarda |
| C. Uma sessão dedicada que reporta `${CLAUDE_PLUGIN_ROOT}` | uma sessão de agente por run | testemunho direto, sem inferência sobre caminho | contraria §Scope the run: mais uma sessão cobrada em todo run padrão |
| D. Não fazer nada e abandonar o spec | zero | o `## Problem` original já está resolvido em `b825f1b` | deixa o falso-pass invisível: a próxima regressão volta a passar dias em verde |
| E. Guarda num script/tool separado sob `assets/checks/` | um arquivo novo, um dono novo | separação de responsabilidade | proibido por `plugin-layout.md:139-146` — dois nomes para o mesmo defeito |

**Por que A ganhou.** Ela é a única que cobre os dois modos de falha e não cobra sessão. B é metade
de A e a metade mais quebrável; A a inclui como asserção diagnóstica, não como a que grada. C compra
certeza direta pelo preço que o próprio standard do harness mandou parar de pagar. E é a forma que o
`plugin-layout.md` já nomeou como errada.

**Por que D não ganhou, e por que ela ainda é a chamada do humano.** O `## Problem` como estava
escrito realmente já está resolvido — mas foi resolvido por um commit manual, sem spec, sem teste e
sem testemunha, e o valor que sobra no slot é justamente a testemunha. Ainda assim, reescopar um
spec muda a identidade dele, e isso é decisão de quem o criou: está registrado em
`## Open Decisions`.

## Open Decisions

- **`${CLAUDE_PLUGIN_ROOT}` sob `--plugin-dir` expande para a string passada, ou para uma forma
  canonizada dela?** É a suposição que sustenta a âncora positiva, e não foi medida: medir custa uma
  sessão de agente, que este spec deliberadamente não gasta na definição.
  *Como se decide:* pelo primeiro run com a asserção ancorada. Ela imprime o caminho observado ao lado
  do `$PLUGIN` esperado; se divergirem por canonização, a positiva passa a comparar `realpath` dos
  dois lados, ou é rebaixada a linha diagnóstica. A negativa não depende dessa resposta e entra
  gradando desde o primeiro run.
- **O dono do spec aceita este reescopo, ou prefere fechá-lo como já resolvido?** O `## Problem` como
  foi capturado em 2026-07-28 já está resolvido em `b825f1b`; o que restou — a testemunha — é vizinho,
  não idêntico. Reescopar mantém o slot de prioridade 10 produtivo; fechar mantém o histórico limpo e
  manda a testemunha para um spec novo.
  *Como se decide:* palavra do humano no banco de aprovação. Se a resposta for fechar, o caminho é
  `/specs:conclude --outcome abandoned` com o `## Outcome` apontando `b825f1b`, e um
  `/specs:create` para a testemunha. Nada aqui presume a resposta: as duas leituras estão escritas.
- **A fixture sintética de captura mora onde?** `assets/checks/` não tem hoje diretório de fixture, e
  `assets/evals/` é do front do skill, com outra semântica
  (`docs/standards/architecture/plugin-layout.md:118-123`).
  *Como se decide:* na task 2.1, escolhendo entre um heredoc dentro do próprio script (nenhum arquivo
  novo, coerente com `## Design` §Decisão 5) e um arquivo em `assets/checks/fixtures/`. A recomendação
  é o heredoc, por não abrir subtree novo sob `assets/` — o que `plugin-layout.md:80-85` manda evitar.

## Risks

- **A guarda mais nova do harness é, historicamente, a fonte mais provável do próximo run vermelho.**
  `docs/standards/quality/surface-verification.md:107-130` mediu que **todo** run vermelho que este
  harness já produziu veio de defeito nele mesmo — leitura em cp1252, ref de marketplace hardcoded,
  cap de turnos baixo, probe instável — e nenhum de regressão de superfície. Acrescentar asserção a
  ele aumenta exatamente a superfície que gera falso vermelho.
  *Mitigação:* as duas guardas são de custo zero e determinísticas (`grep` sobre arquivo e sobre
  captura, sem sessão nova), ficam atrás do gate `evidence()` e são provadas contra fixture sintética
  antes de entrar. Nenhuma delas depende de comportamento de modelo, que é o traço comum dos quatro
  defeitos anteriores.
- **A âncora positiva pode falhar por canonização de caminho, não por regressão.** Se o Claude Code
  resolver symlink, normalizar ou copiar o diretório passado em `--plugin-dir`, o prefixo observado
  não bate com a string que o script passou.
  *Mitigação:* quem grada é a âncora negativa; a positiva imprime o par observado/esperado e, no
  primeiro run que der divergência, é ajustada ou rebaixada a diagnóstico — está registrada como
  decisão aberta.
- **Alguém apaga a guarda inteira depois de um FAIL falso.** Foi o que aconteceu com o cap de turnos
  antes de ele ser tratado como `inconc`.
  *Mitigação:* as duas asserções são independentes e comentadas como tal no script, com a negativa
  marcada como a metade obrigatória. Apagar a positiva não desarma nada.
- **Um check 5 futuro nasce sem `--plugin-dir` e a guarda não percebe.**
  *Mitigação:* a guarda é por contagem, não por lista de checks conhecidos (`## Design` §Decisão 2):
  um `claude -p` novo sem a flag desiguala a conta e derruba o run na hora.
- **O cabeçalho do script fala de `claude -p`, `--plugin-dir` e `enabledPlugins` em prosa** (linhas
  4-15), então um `grep` ingênuo conta comentário e a guarda passa ou falha por motivo errado.
  *Mitigação:* filtrar linhas cujo primeiro caractere não-branco é `#`, com um caso na fixture que
  prova o filtro.
- **Conflito de edição com dois specs irmãos no mesmo arquivo.** `isolate-functional-checks-probes`
  (prioridade 11) mexe no que os probes do check 3 escrevem, e `probe-a-frontmatter-hook-firing`
  (prioridade 17) quer adicionar um check novo ao mesmo script. Os três tocam
  `plugins/quenching/assets/checks/functional-checks.sh`.
  *Mitigação:* a fronteira deste spec é a **testemunha de qual cópia foi carregada** — a guarda
  estática no topo, a função de âncora, e as asserções de caminho dos checks 1 e 4. Ele não muda o que
  os probes escrevem, não sandboxa nada de novo e não adiciona check. Se um irmão entrar primeiro, a
  guarda de contagem de 1.1 já cobre o `claude -p` que ele acrescentar, sem edição adicional aqui;
  nenhuma suposição é feita sobre o desfecho de nenhum dos dois. `## Handoff` repete a instrução para
  quem executar.
- **ACCEPTED — os checks 2 e 3 não ganham âncora de caminho, e não podem ganhar.** As asserções deles
  são sobre nome de `Skill` invocado, não sobre caminho observado; não há caminho na captura para
  ancorar. Para esses dois, a guarda estática de 1.1 é a única guarda, e isso fica escrito no script
  (task 2.5) em vez de virar uma cobertura presumida.
- **ACCEPTED — este spec não conserta o cache stale de `3.0.0`, e o ambiente segue capaz de servir a
  cópia errada.** É intencional: o valor deste spec é o harness não depender do estado da instalação,
  e o cache velho é a melhor fixture disponível do falso-pass.
- **ACCEPTED — a guarda testemunha qual cópia foi carregada, não que ela esteja correta.** Um
  `--plugin-dir` apontando para um worktree errado do mesmo repo passa nas duas âncoras. Aceito: quem
  escolhe a árvore é quem invoca o script, e imprimir `$PLUGIN` no cabeçalho do run (linha 138) já dá
  ao operador o que ele precisa ver.
## Tasks

### 1. A guarda estática

- [ ] 1.1 Adicionar a guarda de contagem no topo do script: linhas não comentadas com `claude -p`
      têm de igualar as com `claude -p --plugin-dir`, e o script não pode conter `enabledPlugins`
      fora de comentário. Falha imprime a linha ofensora e sai 1.
      files: plugins/quenching/assets/checks/functional-checks.sh
      verify: ./plugins/quenching/assets/checks/functional-checks.sh --selfcheck && echo ok
- [ ] 1.2 Adicionar o modo `--selfcheck`, que roda só a guarda de 1.1 e sai 0 ou 1 sem gerar sessão.
      Não reusar `--only` para isso: com `ONLY` vazio o run termina com `PASS=0` e sai 2 por desenho
      (linhas 298-301), o que faria um autocheck aprovado parecer inconclusivo.
      files: plugins/quenching/assets/checks/functional-checks.sh
      verify: ./plugins/quenching/assets/checks/functional-checks.sh --selfcheck; test $? -eq 0
- [ ] 1.3 Provar a guarda por negação: numa cópia do script em `/tmp`, remover o `--plugin-dir` de
      uma invocação e confirmar exit 1 com a mensagem nomeando-a. Passo 2 de `## Validation`.
      verify: o comando do passo 2 de ## Validation sai 1

### 2. A âncora de caminho e sua fixture

- [ ] 2.1 Extrair a comparação de caminho para uma função `anchored`, que recebe a saída de `tools` e
      responde duas coisas em separado: nenhum caminho sob `/plugins/cache/` ou
      `/plugins/marketplaces/` (metade obrigatória) e todo caminho sob `$PLUGIN` (metade
      diagnóstica, que imprime observado e esperado ao falhar).
      files: plugins/quenching/assets/checks/functional-checks.sh
      pattern: plugins/quenching/assets/checks/functional-checks.sh
- [ ] 2.2 Adicionar o modo `--selftest`, que roda `anchored` contra uma captura `.jsonl` sintética
      embutida em heredoc — um evento sob `$PLUGIN/assets/references/` e um sob um caminho de
      `/plugins/cache/` — e sai 0 quando os dois vereditos saem como esperado. Sem sessão.
      files: plugins/quenching/assets/checks/functional-checks.sh
      verify: ./plugins/quenching/assets/checks/functional-checks.sh --selftest; test $? -eq 0
- [ ] 2.3 Ancorar as duas asserções do check 1: trocar `grep -q '/assets/references/'` (linha 165)
      por `anchored`, mantendo a asserção negativa sobre árvore `skills/` como está. Continua dentro
      do `if evidence` da linha 164.
      files: plugins/quenching/assets/checks/functional-checks.sh
      verify: ./plugins/quenching/assets/checks/functional-checks.sh --selftest; test $? -eq 0
- [ ] 2.4 Ancorar as duas asserções do check 4 do mesmo modo (linhas 278-281), preservando a metade
      negativa sobre `hooks/skills.py`, que mede outra coisa e não é substituída pela âncora.
      files: plugins/quenching/assets/checks/functional-checks.sh
      verify: ./plugins/quenching/assets/checks/functional-checks.sh --selftest; test $? -eq 0
- [ ] 2.5 Registrar em comentário, junto aos checks 2 e 3, que a âncora não se aplica a eles: as
      asserções deles são sobre nome de `Skill`, não sobre caminho observado, então para esses dois a
      guarda estática de 1.1 é a única guarda. Deixar isso escrito no lugar onde alguém iria procurar.
      files: plugins/quenching/assets/checks/functional-checks.sh

### 3. O cabeçalho e o standard

- [ ] 3.1 Estender o cabeçalho do script com as duas guardas, os dois modos novos e a razão de a
      negativa ser a obrigatória. `--help` imprime o cabeçalho inteiro (linha 55), então o cabeçalho é
      a documentação de uso.
      files: plugins/quenching/assets/checks/functional-checks.sh
      verify: ./plugins/quenching/assets/checks/functional-checks.sh --help | grep -c selfcheck
- [ ] 3.2 Emendar `docs/standards/quality/surface-verification.md`: a precondição 5 passa a registrar
      que a flag é testemunhada pelo harness, nomeando as duas guardas e por que a negativa grada e a
      positiva diagnostica. Atualizar `source:` e `timestamp:`; `authority` segue `current`.
      files: docs/standards/quality/surface-verification.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs

### 4. Fechamento

- [ ] 4.1 Rodar `./assets/checks/functional-checks.sh` uma vez, do front do skill, e anotar em
      `## Open Decisions` o caminho observado ao lado do `$PLUGIN` esperado — fechando a pergunta
      sobre canonização. Um `exit 2` aqui é inconclusivo e a decisão segue aberta. Esta é a única
      despesa em agente do spec e não é `verify:` de nenhuma task, conforme
      `docs/standards/quality/surface-verification.md:107-130`.
- [ ] 4.2 Responder em `## Open Decisions` onde a fixture ficou (heredoc no script ou arquivo em
      `assets/checks/fixtures/`), registrando o que foi escolhido e por quê.
