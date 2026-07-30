---
slug: isolate-functional-checks-probes
title: functional-checks.sh check 3 creates real specs in the repo it probes
verification: per-section
priority: {level: 11, criticality: medium, complexity: 3, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# functional-checks.sh check 3 creates real specs in the repo it probes

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

Este spec nasceu de um defeito real e **encontra o defeito já corrigido**. Em 27/07/2026 o check 3 de
`functional-checks.sh` — a verificação que confere se uma frase falada ainda aciona o comando certo —
rodava dentro do próprio repositório, e como duas das frases testadas são frases de "guarde isso para
depois", cada execução criava specs de verdade e meio-escritos em `specs/plans/`. Três horas e meia
depois desta captura, outra tarefa passou a rodar cada probe em um repositório descartável, e o
problema desapareceu.

`## Problem` conta essa história com commit e horário, para que ninguém re-descubra nem re-implemente
a correção. O que resta é o que `## Proposal` propõe: o isolamento existe, e **nada o mede** —
reverter uma linha o desfaz sem reprovar nenhuma asserção. `## Design` explica como medir sem inventar
um falso vermelho (a árvore de quem roda o harness está suja por construção, então o que se compara é
o antes com o depois, não a limpeza) e por que a nova asserção não pode contar como aprovação nem usar
nada do encanamento de sessão que já produziu todas as falhas deste harness.

`## Alternatives Considered` guarda a discussão que importa mais que a implementação: apagar o check 3
é defensável, e perde aqui por jurisdição, porque o padrão que governa o harness já tomou essa decisão
em separado. `## Out of Scope` marca as fronteiras com os specs vizinhos que mexem no mesmo arquivo, e
`## Risks` registra os acoplamentos com eles.

O trabalho é pequeno e a prova é a parte incomum: das cinco linhas de `## Validation`, quatro custam
zero sessão de agente, e uma delas é uma **passada de mutação** — quebrar o isolamento de propósito e
observar a asserção nova ficar vermelha, porque uma verificação que nunca foi vista falhar não é
verificação. `## Tasks` traz oito itens em três grupos: a invariante, a prova de que ela reprova, e a
frase que falta no padrão.
## Problem

**O defeito descrito neste spec já está corrigido — por outro spec, três horas e meia depois desta
captura.** O registro fica porque a lição é durável e nada no repositório a protege.

O que era verdade quando este spec nasceu (`58f8fd6`, 27/07/2026 17:52): o check 3 de
`functional-checks.sh` prova que uma frase falada ainda roteia só pela `description`, e rodava suas
probes **dentro do repositório real**. Duas das três probes eram frases de captura, então cada
execução disparava `/specs:create` de verdade contra `specs/plans/` — e `--max-turns` cortava a
sessão antes de `## Problem` ser escrito, deixando dois specs meio-escritos e dois erros
`sp-empty-section` que não pertencem a ninguém. O commit `5f31d19` (26/07/2026) carrega a prova
commitada: `specs/export-csv-timeout-large-accounts/` e `specs/webhook-sender-retry-logic/`, ainda
no formato v1 de três arquivos, entraram na árvore junto com o próprio harness.

O que é verdade hoje: `probe()` (`plugins/quenching/assets/checks/functional-checks.sh:224-240`)
chama `newbox "$box"` com `box="$WORK/probe-$id"` sob um `mktemp -d` protegido por
`trap 'rm -rf "$WORK"' EXIT`; `newbox` (linhas 126-136) grava `{}` em `.claude/settings.json` e o
plugin chega por `--plugin-dir "$PLUGIN"`. Nenhum dos quatro checks roda com cwd em `REPO`.
`python3 plugins/quenching/assets/bin/specs.py validate --json` reporta **0 findings**. A correção
entrou em `c959ec5` (27/07/2026 21:17), tarefa 1.4 de `instrument-and-extend-skill-front`, de
raspão — efeito colateral de acrescentar as probes `d` e `e`, não resposta a este spec. O conclude
de `verify-allowed-tools-enforcement` confirmou de fora: "No check-3 residue: the probes now sandbox
into their own repos, and the tree was clean after the run."

**O que sobra é o que importa.** O isolamento existe e não é medido por nada. Reintroduzir um
`cd "$REPO"` em `probe()` passaria as onze asserções da suíte em verde, e o resíduo voltaria a ser
indistinguível de trabalho real — o modo de falha que
`docs/standards/quality/surface-verification.md` já registra em §"Rules 2 and 3 pull against each
other". O próprio `## Problem` original já argumentava que a sandbox é a versão mais forte "porque
uma probe que não alcança o workspace real não pode danificá-lo nem quando uma edição futura muda o
que ela pede". A sandbox chegou; a garantia contra a edição futura, não.

## Proposal

- `functional-checks.sh` passa a **medir** o próprio isolamento: cada check compara o
  `git status --porcelain` e o `git diff --shortstat` de `REPO` antes e depois de rodar, e a suíte
  reprova nomeando o check que sujou a árvore que ela verifica.
- A asserção é **delta, nunca exigência de árvore limpa**: a suíte continua rodando com árvore
  suja, que é o caso normal (um spec em desenvolvimento), e só o que a própria suíte introduziu
  conta como falha.
- A garantia vale para os **quatro** checks e para qualquer probe futura, não só para o check 3 —
  quem acrescentar uma probe herda a invariante sem precisar saber que ela existe.
- Um tripwire estático no mesmo run reprova o harness se o próprio script voltar a invocar
  `claude -p` com cwd em `REPO`.
- A asserção de resíduo **não incrementa `PASS`**, então um run cujas asserções de superfície foram
  todas inconclusivas continua saindo com `exit 2` e nunca pode ser citado como verde.
- `docs/standards/quality/surface-verification.md` passa a exigir a prova junto da precondição: hoje
  a precondição 2 manda rodar em repo descartável e não manda **verificar** que rodou.
- O `## Problem` deste spec deixa de descrever um defeito aberto e passa a registrar, com commit e
  horário, que a correção veio de fora — para que ninguém a re-descubra nem a re-implemente.
- Nada sobre o destino do check 3 muda: ele continua opt-in, com `/skill:eval` como instrumento
  preferido para roteamento.

## Out of Scope

- **Apagar o check 3.** É a alternativa mais forte contra este spec (ver
  `## Alternatives Considered`, linha C) e fica fora de propósito:
  `docs/standards/quality/surface-verification.md` decidiu em 29/07/2026, com evidência medida sobre
  todo o `specs/archive/`, manter o check como opt-in, e revogar uma decisão de padrão exige a mesma
  barra de evidência que a produziu — não uma correção de isolamento. Apagar o check 3 também não
  resolveria nada para os checks 1, 2 e 4, que continuam sendo sessões de agente com permissão de
  escrita.
- **De qual cópia do plugin os checks carregam.** Essa metade do par é do sibling
  `plugin-dir-for-functional-checks`. Este spec cuida de **onde a probe escreve**, não de **qual
  árvore ela lê**.
- **Acrescentar qualquer probe nova**, inclusive a probe de `hooks:` que o sibling
  `probe-a-frontmatter-hook-firing` propõe. Aqui só se define a invariante que uma probe nova herda.
- **Limpar o resíduo histórico.** Os dois specs em formato v1 de `5f31d19` já saíram da árvore e
  `specs.py validate` reporta 0 findings; não há nada para limpar.
- **Tornar a box hermética copiando o plugin para dentro dela.** `${CLAUDE_PLUGIN_ROOT}` aponta para
  o checkout vivo e gravável, mas nenhum comando da superfície escreve em assets do plugin; o risco
  fica registrado em `## Risks` em vez de pagar uma cópia da árvore por check.
- **O bump de versão.** Uma mudança em `assets/checks/` não é um dos seis artefatos do lockstep, e
  de qualquer forma `docs/standards/ci-cd/versioning-release.md` proíbe bump como tarefa: ele é o
  passo 5 de `/specs:conclude`.

- **Uma sexta precondição no padrão.** A mudança em `docs/standards/quality/surface-verification.md`
  é a metade que faltava da precondição 2, não uma regra nova; o julgamento de autoria fica em
  `## Open Decisions`.
- **A válvula de escape para um check que precise escrever em `REPO`.** Nenhum precisa hoje, e
  construí-la agora seria generalidade não construída; ver `## Open Decisions`.
## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/quality/surface-verification.md` — a precondição 2 ganha a metade que lhe falta:
  rodar em repo descartável não basta, o run tem de **verificar** que rodou. Fica em
  `authority: current`, que já é o grau do doc.

### Standards at `authority: background` this spec may resolve

- `docs/standards/quality/selftest-mutation.md` — **exercitado, não resolvido.** A tarefa 2.1 aplica
  a passada de mutação da regra a uma verificação que não é um subcomando `selftest`, o que é
  evidência a favor da regra; a graduação dela, porém, depende dos três selftests embarcados, que
  este spec não toca.

### Código de produto que este spec espera tocar

- `plugins/quenching/assets/checks/functional-checks.sh` — o par de snapshots por check, o tripwire
  estático, a contagem própria e a mensagem de delta. É a única mudança de código do spec.

Nada em `commands/**` muda, então nada aqui exige uma sessão nova para ser testado, e o registro de
comandos não é tocado.

## Validation

Cinco verificações. As quatro primeiras custam **zero sessão de agente** e são o que prova o design;
a quinta é a única que paga o preço da suíte.

1. **Sintaxe.** `bash -n plugins/quenching/assets/checks/functional-checks.sh` — sem saída, exit 0.
2. **A asserção é alcançada e não infla `PASS`.** Rodar a suíte com um `PATH` que não contém
   `claude`, o que torna toda asserção de superfície inconclusiva por captura vazia:
   `env PATH=/usr/bin:/bin ./plugins/quenching/assets/checks/functional-checks.sh --only 1` deve
   **imprimir a asserção de resíduo aprovada** e ainda assim sair com **exit 2**, com a linha
   `nothing could be measured — this is not a pass`. Um `exit 0` aqui é a decisão 4 violada.
3. **A asserção reprova quando o isolamento sai (passada de mutação).** Reintroduzir `cd "$REPO"` em
   `probe()`, rodar `./plugins/quenching/assets/checks/functional-checks.sh --only 3`: exit **1**, com
   a asserção de resíduo reprovada **nomeando o check 3** e imprimindo o delta de `porcelain`.
   Reverter a mutação em seguida. Sem esta linha vermelha observada, a asserção não pode ser citada
   como verificação — `docs/standards/quality/selftest-mutation.md`.
4. **O gate de `git` existe e a asserção está dentro dele.** `git -C "$(mktemp -d)" rev-parse
   --git-dir` sai diferente de zero, e um `grep` no script mostra a asserção de resíduo fechada por
   esse teste, reportada como pulada quando ele falha — nunca aprovada.
5. **Nenhum resíduo, medido pela ferramenta que o resíduo quebrava.** Depois de um
   `./plugins/quenching/assets/checks/functional-checks.sh --only 3` completo:
   `python3 plugins/quenching/assets/bin/specs.py validate --json` reporta **0 findings**, e
   `git status --porcelain` traz exatamente as mesmas linhas de antes do run.

A política de verificação do spec é `per-section`, já declarada no frontmatter e mantida: as tarefas
da seção 1 são cobertas pelas verificações 1 e 2, que são baratas; a seção 2 **é** as verificações 3
e 4; e a 5 fecha a seção 3.

## Design

### Decisão 1 — a invariante é um delta de estado git, não uma exigência de árvore limpa

`git -C "$REPO" status --porcelain` é capturado antes e depois de cada check e comparado string a
string. Exigir árvore limpa na entrada seria mais simples e estaria errado: o chamador normal do
harness é `/skill:new` numa sessão que acabou de editar `commands/**`, então a árvore está suja por
construção. Uma exigência de limpeza reprovaria pelo trabalho do operador — a mesma classe de falso
vermelho que a precondição 4 do padrão existe para nomear, e um check que reprova sem verdicto não
pode servir de gate.

`--porcelain` sozinho tem um buraco: um arquivo já modificado que a suíte modifique de novo continua
listado como ` M path` e a string não muda. Por isso o par é `status --porcelain` **mais**
`git diff --shortstat`, que muda quando a contagem de linhas muda. Resta um caso não coberto — uma
edição que zera a contagem — aceito em `## Risks`, porque a falha realmente observada foi de
**criação** de arquivo e não de mutação, e um hash da árvore inteira é custo que este check não paga.

### Decisão 2 — o snapshot é por check, o verdicto é uma asserção só

Quatro pares de chamadas git custam milissegundos, e localizar o culpado é a diferença entre "a
suíte sujou o repo" e "o check 2 sujou o repo". Mas o relatório recebe **uma** asserção nomeada, não
quatro, para não inflar a contagem de `PASS` com medição que não é de superfície.

### Decisão 3 — o tripwire estático é um segundo andar, não a prova

Reprovar quando o próprio script casa `cd "$REPO"` é leitura de string sobre si mesmo, e portanto
frágil a `pushd` ou a um `cd` sem aspas. Ele fica porque pega exatamente a regressão que já
aconteceu — o estado anterior a `c959ec5` — e pega no momento da edição, não no do dano. O delta git
é a prova; o tripwire é o aviso barato.

### Decisão 4 — a asserção de resíduo não conta como `PASS`

Esta é a decisão que uma implementação ingênua erra. As asserções existentes são todas fechadas pelo
gate `evidence()` e reportadas como inconclusivas quando a captura não traz evento nenhum; a
asserção de resíduo **não pode** ser inconclusiva, porque `git status` sempre responde. Se ela
incrementasse `PASS`, um run em que todos os agentes falharam por falta de evidência terminaria com
`PASS=1` e `exit 0`, quebrando exatamente a regra do padrão: "an all-inconclusive run must not exit
0". Logo: contador próprio, contribui só para `FAIL`, e a lógica de saída em
`functional-checks.sh:297-302` continua decidindo `exit 2` pelo `PASS` das asserções de superfície.

### Contratos que este design não pode contradizer

- `docs/standards/quality/surface-verification.md` — precondição 2 (repo descartável), precondição 4
  (inconclusivo não é reprovação) e a semântica de `exit 2`. A decisão 4 existe só para não violar a
  última.
- O contrato de saída declarado no cabeçalho do próprio script (`functional-checks.sh:20-22`).
- `docs/standards/architecture/plugin-layout.md` — o harness vive sob `assets/`, fora de
  `commands/**`, então nada aqui toca o registro de comandos. Esta é a única parte do harness que é
  verificável em processo, e é justamente por isso que ela é barata.

### Decisão 5 — a asserção não pode usar nada do encanamento de sessão

Consequência direta da crítica registrada em `## Risks`: a asserção de resíduo é a única da suíte que
é em processo e determinística, e isso é uma restrição de design em vez de uma coincidência. Ela não
lê a captura `stream-json`, não dispara processo, não é fechada por `evidence()` e não depende do
modelo. As quatro falhas que este harness já produziu contra si mesmo estão todas nesse encanamento;
manter a asserção fora dele é o que a impede de virar a quinta. Se alguma versão futura precisar de
qualquer uma das quatro coisas, ela deixou de ser esta asserção.
## Alternatives Considered

Cinco formas inteiras que este spec poderia ter, comparadas depois de medir que a correção original
já havia entrado:

| Abordagem | Custo | O que compra | O que fecha |
| --- | --- | --- | --- |
| A. Abandonar: fechar como já-corrigido | ~zero | uma frente mais honesta, um spec a menos | a garantia durável: a próxima edição desfaz o isolamento sem ninguém ver |
| **B. Invariante de resíduo no harness** (escolhida) | ~20 linhas de bash, nenhuma sessão de agente nova | o isolamento passa a ser medido, para os quatro checks e para toda probe futura | nada; não decide o destino do check 3 |
| C. Apagar o check 3 inteiro | editar o script, o padrão e a tabela de custo | cinco sessões cobradas a menos por run, elimina o único check não-determinístico, mata a classe "uma probe escreve no repo" na raiz do maior ofensor | perde as cinco frases já afinadas como guarda de regressão, inclusive a probe `e`, guarda exato da única falha de roteamento real que o repo registrou |
| D. Limpar depois em vez de isolar | um passo de cleanup por check | árvore limpa no fim | frágil: o cleanup precisa saber o que `plans/` ganhou, e uma probe nova o desatualiza |
| E. Só o tripwire estático, a menor coisa que funcionaria | duas linhas | pega a regressão exata que já aconteceu | não vê dano nenhum que não passe por um `cd "$REPO"` literal |

**A perdeu** porque a correção entrou de raspão, como efeito colateral de outra tarefa. Uma correção
que ninguém pediu e nada verifica é uma correção que a próxima refatoração devolve; fechar o spec sem
a invariante troca um defeito conhecido por um defeito futuro invisível.

**C é a alternativa forte, e perde por jurisdição, não por mérito.** O padrão
`surface-verification.md` já mediu, sobre todo o `specs/archive/`, que todo run vermelho que este
harness produziu veio de um defeito dele mesmo e nenhum de uma regressão de superfície, e concluiu
mantendo o check 3 **opt-in** com `/skill:eval` como instrumento preferido, porque as cinco frases
afinadas ainda valem como guarda. Revogar uma decisão de padrão de 29/07/2026 exige a mesma barra de
evidência que a produziu, e isso é outro spec. C também não fecha o problema: os checks 1, 2 e 4
continuam sendo sessões de agente com permissão de escrita, e é a **invariante** que os cobre, não a
ausência do check 3.

**D perdeu** pelo argumento que o próprio `## Problem` original já fazia: uma probe que não alcança o
workspace real não pode danificá-lo nem quando uma edição futura muda o que ela pede. Isolar domina
limpar.

**E perdeu** por ser prova de intenção e não de efeito — mas foi absorvida em vez de descartada:
virou o segundo andar da decisão 3.

**Comprar em vez de construir** foi considerado e já está comprado: `/skill:eval` é o instrumento
externo para roteamento graduado, e este spec não tenta reimplementá-lo.

## Open Decisions

- **Como um check que legitimamente precise escrever em `REPO` sai da invariante.** Hoje nenhum
  precisa: os quatro escrevem só nas suas boxes de `mktemp -d`. Construir a válvula de escape agora
  seria generalidade não construída. *Como se decide:* quando existir o primeiro check que precise
  dela. O candidato conhecido é a probe de `hooks:` do sibling `probe-a-frontmatter-hook-firing`, se
  ela precisar observar um `Write` em `REPO` para provar que o bloco disparou. A decisão pertence ao
  spec que trouxer o caso, e a forma provável é o check declarar seu próprio par de snapshots em
  volta de si mesmo.
- **Se a mudança no padrão é uma frase na precondição 2 ou uma precondição 6 inteira.** Recomendação
  registrada: uma frase na precondição 2, mais uma linha em §"Rules 2 and 3 pull against each other".
  Uma sexta precondição é inflação, porque a regra não é nova — é a metade que faltava de uma regra
  que já existe. *Como se decide:* na execução da tarefa que escreve o padrão, lendo a precondição 2
  na íntegra; se a frase não couber sem reescrever o parágrafo, ela virou precondição própria e o
  spec registra isso em `## Discoveries`.

## Risks

- **A crítica mais forte contra este spec: acrescentar uma asserção a este harness é acrescentar a
  décima segunda forma de ele se auto-indiciar.** `docs/standards/quality/surface-verification.md`
  mediu que todo run vermelho que este harness produziu veio de um defeito dele mesmo — leitura em
  cp1252, ref de marketplace hardcoded, cap de turnos, probe instável — e nenhum de uma regressão de
  superfície. *Mitigação:* os quatro defeitos registrados vivem, sem exceção, no encanamento da
  sessão de agente: spawn de processo, parsing de `stream-json`, encoding, não-determinismo do
  modelo. A asserção de resíduo não tem nada disso, e a mitigação é uma regra dura em vez de uma
  esperança — ver `## Design` decisão 5.
- **Falso vermelho por escrita de terceiros na árvore.** A suíte completa leva minutos e oito
  sessões de agente; um formatter-on-save, um language server gravando cache ou o próprio operador
  editando em paralelo mudam o `git status` sem que check nenhum tenha culpa. Um falso vermelho aqui
  é exatamente o desgaste de confiança que o padrão registra. *Mitigação:* a mensagem de falha
  imprime o **delta** — as linhas de `porcelain` que entraram ou saíram — para que um falso vermelho
  se auto-diagnostique em uma olhada em vez de exigir investigação.
- **A asserção aprova vacuamente onde `git` não responde.** Se `REPO` não for um repositório git (o
  plugin extraído de um tarball) ou `git` não estiver no PATH, os dois snapshots são a mesma string
  de erro, são iguais, e a asserção passa. É a forma exata da precondição 4 reproduzida em git em vez
  de em `stream-json`. *Mitigação:* a asserção é fechada por `git -C "$REPO" rev-parse --git-dir` e
  reportada como pulada — nem aprovada nem reprovada — quando ele falha.
- **A asserção cobre `$REPO`, e só.** O script aceita um caminho como `$1` e deriva `REPO` de
  `BASH_SOURCE` quando ele não vem, então `$REPO` é sempre o checkout sob teste, inclusive um
  worktree. O que fica descoberto é o cwd de quem invocou, quando for outra árvore. *Mitigação:*
  aceito por construção — nenhum check tem negócio escrevendo fora de `$REPO` nem fora da sua box, e
  ampliar o alvo trocaria uma invariante clara por duas parciais.
- **Uma verificação cuja mutação nunca foi observada.** `docs/standards/quality/selftest-mutation.md`
  é explícito: uma verificação que nunca foi vista falhar é uma verificação não testada.
  *Mitigação:* a passada de mutação é uma tarefa, não uma intenção — reintroduzir `cd "$REPO"` em uma
  probe, rodar `--only 3`, observar a asserção ficar vermelha nomeando o check 3, reverter.
- **ACCEPTED — a asserção pode ser colocada depois de um `exit` e nunca rodar.** Não há selftest para
  o script de shell, então nada prova mecanicamente que ela é alcançada. Aceito porque ela aparece na
  linha de contagem em stdout: um run que não a imprime está visivelmente sem ela, e um arnês para o
  arnês não se paga.
- **ACCEPTED — uma mutação que zera a contagem de linhas escapa do par de comandos git.** Ver
  `## Design` decisão 1. Aceito porque a falha realmente observada foi criação de arquivo, e um hash
  da árvore inteira custa mais do que a classe de dano que ele acrescentaria cobrir.
- **Sobreposição com o sibling `plugin-dir-for-functional-checks`.** Os dois specs editam
  `plugins/quenching/assets/checks/functional-checks.sh` e citam o mesmo padrão. *Mitigação:* a
  fronteira está em `## Out of Scope` — aquele spec é sobre **qual cópia carrega**, este sobre **onde
  a probe escreve** — e as duas mudanças não tocam as mesmas linhas: `--plugin-dir` está dentro das
  invocações `claude -p`, a invariante fica em volta delas. Se aquele entrar primeiro, este rebase
  sem conflito semântico; se este entrar primeiro, a invariante vale para as invocações que aquele
  reescrever. Nenhum dos dois assume o resultado do outro.
- **Sobreposição com o sibling `probe-a-frontmatter-hook-firing`.** Aquele spec **acrescenta** uma
  probe; este restringe onde qualquer probe pode escrever. *Mitigação:* a probe nova herda a
  invariante sem precisar declará-la, e este spec não depende de nada daquele. O único acoplamento
  real: se a probe de `hooks:` precisar observar uma escrita em `REPO` para provar que o bloco
  disparou, ela colide com a invariante — e essa é a pergunta registrada em `## Open Decisions`.

## Tasks

### 1. A invariante no harness

- [ ] 1.1 Capturar `git status --porcelain` e `git diff --shortstat` de `REPO` antes e depois de cada
      check, comparar string a string, e reportar UMA asserção nomeada com o check culpado — com
      contador próprio que contribui só para `FAIL` e nunca para `PASS`
      files: plugins/quenching/assets/checks/functional-checks.sh
      pattern: plugins/quenching/assets/checks/functional-checks.sh
      verify: bash -n plugins/quenching/assets/checks/functional-checks.sh
- [ ] 1.2 Fechar a asserção por `git -C "$REPO" rev-parse --git-dir` e reportá-la como pulada, nem
      aprovada nem reprovada, quando ele falhar — a forma da precondição 4 aplicada a git
      files: plugins/quenching/assets/checks/functional-checks.sh
      verify: bash -n plugins/quenching/assets/checks/functional-checks.sh
- [ ] 1.3 Imprimir o delta na falha: as linhas de `porcelain` que entraram ou saíram, para que um
      falso vermelho por escrita de terceiros se auto-diagnostique
      files: plugins/quenching/assets/checks/functional-checks.sh
      verify: bash -n plugins/quenching/assets/checks/functional-checks.sh
- [ ] 1.4 Acrescentar o tripwire estático que reprova o harness se ele voltar a invocar `claude -p`
      com cwd em `REPO`, casando a forma exata da regressão e não um `cd` qualquer
      files: plugins/quenching/assets/checks/functional-checks.sh
      verify: env PATH=/usr/bin:/bin ./plugins/quenching/assets/checks/functional-checks.sh --only 1; test $? -eq 2

### 2. Provar que a invariante reprova

- [ ] 2.1 Passada de mutação: reintroduzir `cd "$REPO"` em `probe()`, rodar
      `functional-checks.sh --only 3`, registrar no commit que a asserção ficou vermelha nomeando o
      check 3, reverter a mutação
      files: plugins/quenching/assets/checks/functional-checks.sh
      verify: ./plugins/quenching/assets/checks/functional-checks.sh --only 3
- [ ] 2.2 Provar a decisão 4 medindo o exit code: com um `PATH` sem `claude`, a suíte imprime a
      asserção de resíduo aprovada e ainda sai com exit 2
      verify: env PATH=/usr/bin:/bin ./plugins/quenching/assets/checks/functional-checks.sh --only 1; test $? -eq 2

### 3. O padrão

- [ ] 3.1 Escrever em `docs/standards/quality/surface-verification.md` a metade que falta da
      precondição 2 — o run verifica que rodou em repo descartável — mais uma linha em §"Rules 2 and
      3 pull against each other" apontando para a asserção; `authority: current`, que já é o grau do
      doc. Se a frase não couber sem reescrever o parágrafo, ela virou precondição própria: registrar
      a decisão via `specs.py discover` em vez de decidir sozinho
      files: docs/standards/quality/surface-verification.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
- [ ] 3.2 Registrar no `## Outcome` que o isolamento em si chegou em `c959ec5`, por
      `instrument-and-extend-skill-front`, e que este spec entregou a medição dele — para que a
      próxima leitura do `git log` não atribua a correção ao spec errado
      verify: python3 plugins/quenching/assets/bin/specs.py validate --json
