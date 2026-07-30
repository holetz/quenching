---
slug: check-the-lockstep-itself
title: Assert the seven-surface version lockstep in skills.py selftest
verification: per-section
priority: {level: 14, criticality: medium, complexity: 1, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# Assert the seven-surface version lockstep in skills.py selftest

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

Uma release deste plugin move sete números de versão que precisam concordar entre si, e **nada
compara nenhum par**. `## Problem` mostra onde o buraco está escrito no próprio código: o comentário
que explica por que `skills.py drift` compara contra a constante do tool termina dizendo que a
concordância com o arquivo `VERSION` é *"checked elsewhere"*, e esse `elsewhere` não existe.

`## Proposal` diz o que passa a ser verdade: `skills.py selftest` afirma o lockstep sobre as sete
superfícies, lidas de uma tabela declarada, com fixture para a regra e um skip honesto numa cópia
instalada. `## Design` explica por que a casa é o `selftest` e não o `drift`, um hook ou o harness de
sessão — a escolha sai de regras já escritas em `docs/standards/` — e fecha dizendo o que o check
**não** prova, porque um detector de duplicata não é cobertura.
`## Alternatives Considered` guarda as sete formas pesadas com o motivo de cada derrota, incluindo a
versão barata de `grep` e a de não fazer nada.

`## Impact` declara um único padrão a ser escrito, e `## Validation` traz cinco braços, dos quais o
segundo é o que dá sentido ao primeiro: a asserção precisa ter sido **vista falhar**. `## Risks`
reúne o que o argumento adversarial encontrou — o vermelho legítimo no meio de um bump, uma raiz de
plugin resolvida para o lugar errado, a tabela ficando atrás do layout — e nomeia a sobreposição com
os specs irmãos que podem mover os caminhos e o namespace que este cita. Duas coisas ficam
deliberadamente abertas em `## Open Decisions`, e as duas têm dono: a ordem de merge e a revisão de
branch.

`## Out of Scope` mantém a fronteira mais fácil de atravessar: o `drift` continua respondendo sobre
as cópias instaladas num alvo, e este spec não bumpa nada nem decide qual é o próximo número.
`## Tasks` põe o padrão no fim, depois que o check existe, porque só aí a prosa antiga pode ser
cortada sem deixar o repositório sem nenhum dos dois.

## Problem

O lockstep de versões não tem verificador nenhum. `skills.py drift` compara cada cópia instalada
contra a constante `VERSION` do tool embarcado no plugin — escolha correta, porque é essa constante
que uma instalação escreveria no disco — e o comentário que a justifica
(`plugins/quenching/assets/bin/skills.py:1606-1608`) termina dizendo em voz alta:
*"The two agreeing is the lockstep's business, checked elsewhere."* **Esse `elsewhere` não existe.**

E o buraco é mais largo do que uma comparação.
[versioning-release.md](/docs/standards/ci-cd/versioning-release.md) §The six declara **seis**
artefatos que precisam concordar (`VERSION`, `plugin.json`, `marketplace.json` e as constantes de
`specs.py`, `skills.py`, `okf-validate.py`), e §The seventh file acrescenta um sétimo,
`assets/bin/session.py`, sobre o qual o próprio padrão admite: *"This one is enforced by nothing at
all — `skills.py drift` does not know about it, no selftest asserts it, and `--version` still
answers, just with the wrong number."* CLAUDE.md §Operating this repo lê **quatro** deles de volta à
mão, um comando por linha, e nenhuma das leituras compara nada: quem confere é o olho de quem rodou.

O custo de errar um dos artefatos 4–6 é silencioso por construção — *"a tool whose constant was not
bumped is therefore never upgraded in any target repo that already has it"* — o plugin publica a
correção e ela nunca chega aos repositórios para os quais foi escrita.

Isso já aconteceu duas vezes, e nenhuma delas em teoria:

- `session.py` foi escrito em `4.2.0` num branch que ficou aberto enquanto a main lançou `4.3.0`, e
  chegou à revisão de branch ainda reportando `4.2.0`, sob um comentário que dizia *"tracks the
  plugin"*. O único filtro que pegou foi um humano lendo o diff inteiro no `/specs:conclude`
  (versioning-release.md §The seventh file).
- este repositório rodou `.claude/hooks/specs.py` em **1.0.0** contra um plugin em **4.2.0** por
  meses — tempo suficiente para a cópia velha ainda aceitar `--plan` onde a atual exige `--spec`
  (versioning-release.md §Noticing drift).

Descoberto ao construir `notice-installed-tool-version-drift`, cujo `drift` já resolve o plugin root
e já lê todos esses números: a comparação que falta custa quase nada onde os dados já estão.

## Proposal

- `skills.py selftest` passa a **afirmar o lockstep**, e não só a exercitar fixtures: uma função pura
  `lockstep_failures(plugin_root)` lê `VERSION` e compara com todas as superfícies do plugin que
  carregam uma versão, devolvendo uma falha por divergência.
- As superfícies não ficam espalhadas pelo código: elas viram uma **tabela declarada** no topo do
  módulo, no mesmo formato de `INSTALLED_TOOLS` (`skills.py:1516`), e a tabela *é* o conjunto.
- A cobertura é de **sete** superfícies, não das quatro que CLAUDE.md lê hoje: os seis de
  versioning-release.md §The six mais `assets/bin/session.py`, que é justamente o único que nada
  hoje verifica.
- A afirmação roda contra o plugin real quando `resolve_plugin_root()` resolve
  (`skills.py:1680`), e numa cópia instalada — onde não há plugin ao lado para comparar — reporta
  `skipped: true` em vez de passar em silêncio. O `pluginRoot` resolvido aparece no payload, como
  `drift` já faz (`skills.py:1734`), para que uma raiz errada seja visível e não inferida.
- Uma constante ausente, ilegível ou num arquivo que não existe é uma falha própria, nunca um
  `current` vacuoso: a comparação usa a constante **parseada**, jamais o valor com fallback.
- A entrada de `marketplace.json` é selecionada **pelo `name`**, não por índice: a versão vive em
  `plugins[].version` de uma lista, e indexar `[0]` seria exatamente a posição-no-lugar-de-membro que
  canonical-set-parsing.md §Slice by membership proíbe.
- A regra ganha fixture: um plugin divergente entra ao lado do controle conformante que já existe em
  `DRIFT_FIXTURE` (`skills.py:1164-1188`), e o controle continua obrigado a ficar limpo.
- O código de finding nasce no vocabulário de **selftest sobre o tool**, não no vocabulário de sweep
  de `/skill:align` — a mesma separação que `sp-template-drift` e `sp-capture-gate-missing` já têm.
- `drift` não muda de comportamento: `INSTALLED_TOOLS` continua com três tools e o payload continua
  o mesmo. O que muda é que o comentário em `skills.py:1608` passa a apontar para um lugar existente.
- **§Verifying de versioning-release.md ganha um chamador que hoje não tem**: o bloco prescreve cinco
  leituras manuais e não menciona `selftest`; ele passa a prescrever a chamada que falha, e a prosa
  substituída é **cortada**, não mantida em paralelo.
- A passagem de mutação exigida por
  [selftest-mutation.md](/docs/standards/quality/selftest-mutation.md) é executada sobre a asserção
  nova e o resultado fica registrado — a asserção nasce tendo sido vista falhar.
## Out of Scope

- **Mexer em `drift` ou em `INSTALLED_TOOLS`.** A comparação cópia-instalada-versus-tool-embarcado
  está correta e é uma pergunta diferente: ela fala do repositório-alvo, o lockstep fala do plugin.
  Só o comentário de `skills.py:1606-1608` é atualizado, e apenas para citar onde o check passou a
  morar.
- **Emitir o finding do lockstep no sweep de `/skill:align`, ou em qualquer probe que rode num
  repositório-alvo.** Um defeito de release do plugin reportado como erro dentro do repositório de
  outra pessoa é ruído que ela não tem como resolver — ver `## Design`.
- **Dar qualquer cobertura ao repositório-alvo.** O check é do lado do plugin por construção; quem
  adota o plugin não ganha nada dele, e ganha do `drift` o que lhe diz respeito. Isso é escopo, não
  omissão.
- **Executar ou automatizar o bump.** Escolher entre patch, minor e major é a decisão que
  versioning-release.md §When the bump happens coloca deliberadamente no `/specs:conclude` step 5,
  porque *o que o release é* só se sabe quando o branch inteiro está escrito. Um verificador que
  bumpasse estaria adivinhando isso.
- **Adicionar `session.py` aos seis.** Ele entra no *check*, não no *contrato*: a razão de estar
  fora dos seis (nunca é instalado num alvo) continua valendo, e colocá-lo em `INSTALLED_TOOLS`
  faria `drift` comparar uma versão que nenhum alvo carrega — exatamente o que o padrão proíbe.
- **Rodar a passagem de mutação nos outros três selftests.** O gate de graduação de
  selftest-mutation.md pede a passagem em `skills.py`, `specs.py` e `okf-validate.py` inteiros; este
  spec roda a passagem na única asserção que adiciona e não promove o padrão a `authority: current`.
- **Consertar o hook morto em `.claude/settings.json`.** Ele é citado em `## Risks` como *evidência*
  de que um check registrado apodrece calado, não como trabalho deste spec.
- **Verificar qualquer outro campo de `plugin.json` e `marketplace.json`** além de `version`. As
  duas descrições longas divergem entre si hoje e isso é outro assunto.
## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/ci-cd/versioning-release.md` — §Verifying deixa de prescrever cinco leituras
  manuais e passa a prescrever a chamada que falha, com a prosa substituída **cortada**; e §The
  seventh file deixa de afirmar que o sétimo arquivo é *"enforced by nothing at all"*, porque passa a
  ser conferido.

Só um caminho é declarado, de propósito. `canonical-set-parsing.md` já enuncia a regra de que um
detector de duplicata não é cobertura e não precisa dela repetida; `selftest-mutation.md` continua
`authority: background` porque o gate de graduação dela pede a passagem de mutação nos **três**
selftests, e este spec faz um. O resultado da passagem que ele faz vive no commit que a fez, que é
onde selftest-mutation.md §The rule o coloca: *"What survives the pass is not tooling but a claim in
the commit that wrote it."*

### Standards at `authority: background` this spec may resolve

- none — o único candidato adjacente é `docs/standards/quality/selftest-mutation.md`, e ele **não**
  é resolvido aqui: o gate dele exige a passagem rodada contra `skills.py`, `specs.py` e
  `okf-validate.py` inteiros, e este spec roda contra uma asserção. Dizer que resolve seria alegar um
  gate que não foi vencido.

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/skills.py` — a tabela declarada das superfícies, a função de
  comparação, o gancho em `cmd_selftest`, a fixture divergente e o comentário de `:1606-1608`.
- `plugins/quenching/assets/bin/specs.py` e `plugins/quenching/assets/hooks/okf-validate.py` —
  **apenas** o comentário de uma linha ao lado de cada `VERSION`, para que os três citem a tabela em
  vez de enumerarem subconjuntos diferentes. Nenhuma lógica é tocada, e nenhuma constante é alterada.

## Validation

A política declarada é `verification: per-section`, então os comandos abaixo rodam ao fim de cada
grupo `### N.` de `## Tasks`, não a cada checkbox.

Tudo é rodado de `plugins/quenching`.

**1. O check passa, e diz quantos casos rodou.**

```bash
python3 assets/bin/skills.py selftest
python3 assets/bin/skills.py selftest --json
```

A saída em texto termina em `PASS`, com a contagem de casos maior que os 25 de hoje pelas linhas de
lockstep acrescentadas. O JSON traz `"ok": true`, `failures: []` e o `pluginRoot` resolvido — a raiz
aparece na saída para que uma raiz errada seja visível, e não inferida.

**2. O braço negativo, que é o que dá sentido ao braço 1.** Exigido por
[selftest-mutation.md](/docs/standards/quality/selftest-mutation.md) §The rule: a asserção precisa
ter sido vista falhar.

```bash
# uma superfície fora por um dígito
python3 - <<'PY'
import pathlib, re
p = pathlib.Path("assets/bin/session.py"); t = p.read_text(encoding="utf-8")
p.write_text(t.replace('VERSION = "4.4.0"', 'VERSION = "4.3.0"', 1), encoding="utf-8")
PY
python3 assets/bin/skills.py selftest; echo "esperado 1, obtido $?"
git checkout -- assets/bin/session.py
python3 assets/bin/skills.py selftest; echo "esperado 0, obtido $?"
```

Exit **1** com a falha nomeando `assets/bin/session.py`, a versão encontrada e a do arquivo
`VERSION`; e exit **0** depois do revert. Uma mutação que não faz nada falhar é uma asserção que não
está segurando nada. Repetir para uma constante apagada: também precisa falhar, e como *superfície
ilegível*, nunca como igual.

**3. O braço do skip, para que silêncio não leia como limpo.** Chamada da função de comparação contra
um diretório que não é raiz de plugin: o resultado é `skipped`, jamais um `ok: true` sozinho.

**4. O não-objetivo, provado e não presumido.** `drift` sai inalterado:

```bash
python3 assets/bin/skills.py drift --json    # exit 0 neste repositório
```

O payload continua com três entradas em `tools` e o único finding continua sendo `sk-tool-absent`
para `okf-validate.py`, que é o estado correto de um repositório só-plugin. Nenhum código
`sk-lockstep-*` aparece aqui.

**5. Os invariantes que precisam continuar valendo.** O bloco de verificação do skeleton em
CLAUDE.md §Operating this repo inteiro, porque a asserção nova entra dentro dele:

```bash
python3 assets/bin/specs.py selftest
python3 assets/hooks/okf-validate.py selftest
python3 assets/hooks/okf-validate.py assets/docs                        # 0 error(s), 0 warning(s)
python3 assets/bin/skills.py --root . doctor --json                     # 26 commands, no findings
python3 assets/bin/skills.py --root . lint --json                       # exit 0
python3 assets/hooks/okf-validate.py ../../docs                         # o padrão editado valida
```

**O que nada disto prova**, e o spec não alega:

- que o número escolhido é o certo para o que o release contém — patch, minor ou major é julgamento
  humano no `/specs:conclude` step 5;
- que um align **decide** o overwrite a partir da comparação (isso é a fixture do `drift`);
- que Claude Code dispara o upgrade a partir do par `plugin.json` + `VERSION`.

**O que deliberadamente não é rodado.** `assets/checks/functional-checks.sh` não é citado aqui e não
recebe check novo: nada muda sob `commands/**`, e
[surface-verification.md](/docs/standards/quality/surface-verification.md) §The harness belongs to
the skill front proíbe nomeá-lo no `## Validation` de um spec.

## Design

### A casa do check: o `selftest` de `skills.py`

Cinco casas foram pesadas (a tabela completa está em `## Alternatives Considered`). A escolhida é
uma asserção dentro de `skills.py selftest`, e a decisão se apoia em três regras já escritas neste
repositório, não em preferência:

1. **O vocabulário decide `selftest` contra `drift`.**
   [canonical-set-parsing.md](/docs/standards/code/canonical-set-parsing.md) já resolveu este caso
   exato para o outro par duplicado: *"Neither code belongs to the `/specs:align` sweep vocabulary —
   like `sp-template-drift`, they are selftest findings about the tool, not findings about a
   workspace."* Uma divergência de lockstep é um defeito **do tool**, então é finding de `selftest`.
2. **`drift` tem outro sujeito.** Seu docstring (`skills.py:1493-1503`) escopa o subcomando às
   cópias sob `.claude/hooks/` de um alvo, e ele é invocado como probe do step 1 de quatro aligns
   (`commands/align.md:104`, `commands/docs/align.md:209`, `commands/specs/align.md:94`,
   `commands/skill/align.md:188`). Um erro de lockstep ali apareceria no `/docs:align` de todo
   repositório que adotou o plugin, com remédio que só o autor do plugin pode aplicar.
3. **`skills.py` é o tool que já tem as ferramentas.** `PLUGIN_VERSION_FILE` (`:1505`),
   `VERSION_CONSTANT_RE` (`:1531`), `read_tool_version()` e `resolve_plugin_root()` (`:1680`) já
   existem lá por causa do `drift`. Nenhuma máquina nova é necessária, e uma asserção em cada um dos
   três tools seriam três cópias de uma regra que — ao contrário do parser de frontmatter — nunca
   precisa rodar numa cópia instalada.

### As sete superfícies, e por que o sétimo entra

```
  VERSION  (a verdade)
     |
     +-- plugin.json      -> version              artefato 1  |  Claude Code decide o upgrade
     +-- marketplace.json -> plugins[].version    artefato 3  |  a listagem
     +-- specs.py         -> VERSION = "..."      artefato 5  |  /specs:align compara com o alvo
     +-- skills.py        -> VERSION = "..."      artefato 6  |  /skill:align  idem
     +-- okf-validate.py  -> VERSION = "..."      artefato 4  |  /docs:align   idem
     +-- session.py       -> VERSION = "..."      o setimo    |  ninguem le -> ninguem verifica
```

Os seis existem porque **dois consumidores diferentes** leem duas metades diferentes. O sétimo está
fora dos seis porque nunca é instalado num alvo, e é exatamente por isso que ele pertence a este
check: a razão de ficar fora do contrato é irrelevante para uma leitura feita do lado do plugin, e o
padrão diz literalmente que hoje *nada* o verifica. Manter o sétimo fora do check seria escolher não
cobrir o único artefato cuja falha já chegou a uma revisão de branch.

### A tabela declarada é o conjunto

As sete superfícies são uma tabela no topo do módulo, no formato que `INSTALLED_TOOLS`
(`skills.py:1516`) já usa: caminho, como a versão é extraída, e para que serve. Duas consequências
que o design assume de propósito:

- **Adicionar um oitavo arquivo com versão é adicionar uma linha.** Sete leituras inline seriam sete
  lugares para esquecer, que é o modo de falha de canonical-set-parsing.md §When the set grows.
- **Uma superfície declarada cujo arquivo não existe é falha, não skip.** Arquivo ausente significa
  que o layout se mexeu e a tabela não acompanhou; encolher calado transformaria a mudança de layout
  em perda silenciosa de cobertura.

### Ler a constante, nunca executar `--version`

Mesma regra que `drift` já aplica (versioning-release.md §Noticing drift, item 1b): a versão sai do
`VERSION = "..."` parseado por `VERSION_CONSTANT_RE`. Rodar cada script custaria `python3` no `PATH`
e transformaria uma leitura em execução, sem comprar nada — os arquivos aqui são todos do próprio
plugin. Para `plugin.json` e `marketplace.json` a leitura é um `json.load` e um `get`.

### A constante parseada, nunca o valor com fallback

`drift_rows()` faz `tool_shipped = read_tool_version(...) or shipped` (`skills.py:1609`). Esse
fallback é correto para o que `drift` pergunta e **fatal** para o que o lockstep pergunta: uma
constante apagada ou renomeada viraria igual ao `VERSION` e passaria. Então a comparação do lockstep
usa o retorno cru: `None` é uma falha própria — *superfície ilegível* — no mesmo espírito do
`unreadable` de `compare_versions()`, e nunca um `current` vacuoso.

### `marketplace.json` é selecionado por nome, não por índice

A versão da listagem vive em `plugins[].version`, dentro de uma **lista** de entradas com `name`.
Ler `plugins[0]` responderia à pergunta de membro com uma posição — literalmente o que
canonical-set-parsing.md §Slice by membership proíbe, e um segundo plugin no marketplace faria o
check passar a medir outra coisa sem erro nenhum. A entrada é selecionada por `name == "quenching"`,
e *nenhuma entrada com esse nome* é falha.

### Skip honesto numa cópia instalada, e o que isso custa

`skills.py selftest` hoje é 100% fixture: monta tudo num `tempfile.TemporaryDirectory()` e roda
idêntico em qualquer lugar. A asserção do lockstep quebra essa propriedade, porque só faz sentido
onde há um plugin ao lado. O precedente já está escrito no outro tool: `specs.py cmd_selftest`
compara `TEMPLATE_SPEC` e `DEFAULT_SCHEMA` com os arquivos adjacentes e, quando não há nenhum, sai
cedo com `skipped: true` e uma mensagem que diz *"no adjacent assets to compare (installed copy)"*
(`assets/bin/specs.py:2765`). O mesmo formato é adotado aqui: `resolve_plugin_root()` devolvendo
`None` produz `skipped`, nunca `ok: true` sozinho — um check que não sabe distinguir "sem
divergência" de "não consegui olhar" reporta o silêncio que existe para quebrar. O `pluginRoot`
resolvido vai no payload por isso mesmo.

Isso reparte a cobertura em duas metades que se conferem: a **fixture** prova que a regra pega uma
divergência plantada e não acusa o controle conformante; a **chamada viva** prova que *este* plugin
está em lockstep agora.

### O que este check NÃO prova

canonical-set-parsing.md §A lockstep check does not cover the code over it é explícito, e a advertência
cai em cima deste spec: *"That check proves the copies agree. It cannot prove the code reading them
still means the same thing."* O que entra aqui é um **detector de duplicata** — sete strings iguais —
e nada além:

- não prova que um align **decide** o overwrite a partir da comparação (isso é a fixture de `drift`,
  `EXPECTED_DRIFT` em `skills.py:1185`);
- não prova que o número escolhido é o certo para o que o release contém (patch, minor ou major é
  julgamento humano no step 5);
- não prova que Claude Code de fato dispara o upgrade a partir do par `plugin.json` + `VERSION`.

Este spec não pode alegar nenhuma das três, e `## Validation` diz isso na cara.

### Onde o check ganha um chamador

Um check sem chamador é um subcomando disponível, não uma verificação. Dois chamadores — e só um
deles já existe:

- **CLAUDE.md §Operating this repo** já roda `skills.py selftest` no bloco de verificação do
  skeleton. A asserção entra de graça ali.
- **versioning-release.md §Verifying** ainda **não** menciona `selftest`: hoje prescreve cinco
  leituras manuais cujo comparador é o olho humano, e é esse bloco que o `/specs:conclude` step 5
  consulta ao acertar as obrigações de release. Transformá-lo num chamador é a parte que faz este
  spec ser enforcement e não mais um comando disponível — logo é task nomeada, não conserto de
  passagem. A prosa substituída é **cortada**, porque
  [bundle-verification.md](/docs/standards/quality/bundle-verification.md) §Corollary é explícito:
  *"When a check lands, the prose it replaces gets cut, not kept as belt-and-braces. Two enforcers
  for one invariant is how they drift."*

### Contratos que este design não pode contrariar

| Contrato | O que ele impõe aqui |
| --- | --- |
| canonical-set-parsing.md §A lockstep check does not cover the code over it | um detector de duplicata não é cobertura; o spec não pode alegar mais do que igualdade de strings |
| canonical-set-parsing.md §Slice by membership | `marketplace.json` por `name`, nunca por índice |
| versioning-release.md §The seventh file | `session.py` entra no check e **não** nos seis |
| bundle-verification.md §Corollary | a prosa que o check substitui é cortada |
| selftest-mutation.md §The rule | a asserção precisa ter sido vista falhar antes de ser alegada como verificação |
| [hooks.md](/docs/standards/automation/hooks.md) §The scope ladder | um hook precisa justificar o escopo; aqui não justifica — ver `## Alternatives Considered` |
| [surface-verification.md](/docs/standards/quality/surface-verification.md) §The harness belongs to the skill front | `functional-checks.sh` não recebe check novo e este spec não o cita em `## Validation` |

## Alternatives Considered

Seis formas inteiras foram consideradas para *onde o lockstep é conferido mecanicamente*. A primeira
foi escolhida.

| Forma | Custo | O que compra | Por que perdeu |
| --- | --- | --- | --- |
| **A. asserção no `skills.py selftest`** (escolhida) | uma função pura, uma tabela declarada, uma fixture, um skip honesto | roda num chamador que já existe e cria o segundo onde o bump acontece; vocabulário certo; nenhuma máquina nova | — |
| **B. subcomando novo `skills.py lockstep`** | um subcomando, um `register()`, uma linha em toda documentação que enumera a superfície do tool | saída dedicada e legível | é a forma A **sem chamador**. Cada lugar que hoje roda `selftest` precisaria aprender um comando novo, e um verificador que ninguém invoca é o mesmo silêncio que este spec existe para quebrar |
| **C. estender o payload e os findings de `drift`** | quase zero: `drift` já tem `plugin_root`, `VERSION` e as três constantes na mão | o check ganharia quatro call sites de graça (o step 1 de todos os aligns) | reprovado pela regra de vocabulário de canonical-set-parsing.md — é finding sobre o tool, não sobre um workspace — e porque faria um defeito de release do plugin virar erro no `/docs:align` de todo repositório-alvo, com remédio que o dono do alvo não tem. `drift` também refuse com exit 2 quando o plugin root não resolve, o que é certo para o sujeito dele e forte demais para este |
| **D. hook `PostToolUse` casado com `Write` e `Edit` sobre os sete arquivos** | rung 2 da escada de hooks.md, cobrando toda escrita do repositório | pegaria o bump no exato momento em que ele é digitado | falha por mecânica, não por gosto: o bump toca sete arquivos, então o hook dispara depois do **primeiro** deles, quando o lockstep está legitimamente quebrado no meio da edição — um erro falso garantido em todo release. E `.claude/settings.json` deste repositório é a prova viva do custo de manutenção: dois hooks registrados apontando para um script que o commit `193578c` apagou |
| **E. uma linha em `assets/checks/functional-checks.sh`** | uma sessão de agente cobrada por execução | nada que as outras não comprem | o header do próprio script se descreve como *"the four checks nothing in-process can make"*, e o lockstep são sete leituras de arquivo — inteiramente in-process. surface-verification.md §The harness belongs to the skill front mede que **toda** execução vermelha desse harness veio de defeito nele mesmo, e proíbe citá-lo no `## Validation` de um spec |
| **G. um `grep` de uma linha no bloco de verificação do CLAUDE.md** | zero código; a versão 80/20 honesta | comparar as três constantes entre si cabe em `grep -h '^VERSION' ... ; sort -u ; wc -l` | perde três coisas, e é por isso que o 80/20 não fecha: não alcança `plugin.json` nem `marketplace.json`, que são JSON; prova que as três constantes concordam **entre si** e não que concordam com o arquivo `VERSION`; e não tem onde pendurar fixture, então selftest-mutation.md §The rule não tem o que exigir. Sobretudo, mora em prosa de CLAUDE.md — exatamente o modo de enforcement que bundle-verification.md mediu produzindo **zero** em duas execuções reais |
| **F. não fazer nada** | zero | o status quo: `/specs:conclude` step 5 apresenta um plano, um humano edita sete arquivos e confere lendo cinco linhas de saída | o processo já vazou duas vezes, e as duas estão escritas no padrão: `session.py` em `4.2.0` contra um plugin em `4.3.0`, e `specs.py` instalado em `1.0.0` contra `4.2.0` por meses. Com 32 specs em voo, todos passando pelo mesmo step 5 manual, o modo de falha é recorrente e não pontual |

Duas variações menores dentro da forma A foram rejeitadas, cada uma por um motivo próprio:

- **cobrir só os quatro artefatos que CLAUDE.md lê hoje** — deixaria `plugin.json`,
  `marketplace.json` e `session.py` sem verificador nenhum, e é o sétimo que já falhou de verdade.
- **replicar a asserção nos três selftests** — a duplicação tripla das constantes existe porque cada
  tool instala sozinho num alvo; a asserção de lockstep nunca roda num alvo, então não herda esse
  motivo, e três cópias de uma regra sem motivo é como elas divergem.
## Open Decisions

- **O prefixo do código de finding.** A proposta é `sk-lockstep-drift`, mas `sk-` é o vocabulário do
  front de skill, e o sibling `restructure-claude-front-namespace` pode renomear o namespace
  `/skill` para `/automation`. **Como se decide:** pela ordem de merge — quem merge depois adota o
  prefixo em vigor naquele momento, e o código novo viaja no mesmo rename de todos os outros `sk-*`,
  sem exceção própria. Este spec não presume o resultado do sibling e não cria um prefixo terceiro.
- **Quanto de §The seventh file é reescrito.** O corte da prosa em §Verifying é claro
  (bundle-verification.md §Corollary é explícita: o que o check substitui é cortado). Mas §The seventh file
  argumenta que `session.py` *"is enforced by nothing at all"*, e essa frase fica **falsa** quando o
  check entra — reescrevê-la muda o argumento do padrão, não só o seu bloco de verificação.
  **Como se decide:** na revisão de branch do `/specs:conclude` step 3, lendo o padrão contra o check
  que aterrissou. Se a reescrita passar de acertar a frase para refazer o argumento, o resto vira
  oferta de `/docs:add` e não entra neste branch. A task 4.2 existe para fechar esta decisão.

## Risks

| Risco | Como se manifesta | Mitigação |
| --- | --- | --- |
| **Vermelho legítimo no meio do bump** | o bump toca sete arquivos; entre o primeiro e o último o lockstep está quebrado de verdade, e quem rodar `selftest` por hábito vê vermelho | `ACCEPTED — ` é o comportamento correto, não um defeito. A mitigação é de **redação**: a mensagem do finding nomeia quais superfícies discordam e aponta `/specs:conclude` step 5 como o momento em que as sete se movem juntas, para que um vermelho leia "você está no meio do bump" e não "o tool quebrou" |
| **`resolve_plugin_root()` resolve para o plugin errado** | ele sobe até quatro níveis a partir de `__file__` procurando `VERSION` ao lado de `assets/` (`skills.py:1680-1699`); num checkout aninhado ou numa cópia vendorizada pode encontrar um estranho e comparar contra o número dele, reportando `ok` | o payload imprime o `pluginRoot` resolvido, como `drift` já faz em `skills.py:1734`. Uma raiz errada fica visível na saída em vez de silenciosa |
| **A tabela de superfícies fica atrás do layout** | um oitavo arquivo passa a carregar versão e ninguém adiciona a linha; o check continua verde cobrindo sete de oito — a falha que canonical-set-parsing.md §When the set grows nomeia | uma superfície declarada cujo arquivo não existe é **falha**, nunca skip: se o layout se mexeu, o check acusa em vez de encolher calado. E a tabela declarada em vez de sete leituras inline é o que faz "adicionar um membro" ser uma linha |
| **A prosa é cortada e o check regride depois** | §Verifying perde as cinco leituras manuais; anos depois o check cobre uma superfície a menos e o repositório fica sem os dois | o corte só é seguro porque o check cobre **mais** do que a prosa cobria (sete contra quatro), e ele acontece na mesma task em que o check entra, nunca antes. A regra de um enforcer só é de bundle-verification.md §Corollary; o preço dela é a task de missing-path acima |
| **A passagem de mutação é pulada por ser "óbvia"** | nasce uma asserção de selftest que nunca foi vista falhar, exatamente o que selftest-mutation.md §The rule proíbe | a passagem é uma task com resultado registrado, e aqui é barata: uma constante da fixture fora por um dígito |
| **Um check registrado que apodrece** | `.claude/settings.json` deste repositório registra dois hooks (`PostToolUse` casado com `Write` e `Edit`, e um `Stop`) apontando para `.claude/hooks/okf-validate.py`, que o commit `193578c` apagou junto com o diretório inteiro. Toda escrita neste repositório devolve `can't open file` desde então, e ninguém removeu o registro | `ACCEPTED — ` não se aplica a este spec, e essa é a razão positiva de escolher a forma A: a asserção mora **dentro de um subcomando que já existe**, então não há registro para apodrecer. É também a evidência viva contra a forma D, e hooks.md §Policy defaults já escreveu o remédio que faltou ali (`test -f` antes do `python3`) |
| **Colisão com `revise-standards-subject-folders`** | o `## Impact` deste spec declara `docs/standards/ci-cd/versioning-release.md`; aquele spec pode mover as pastas de assunto e o caminho declarado sai do lugar, quebrando a checagem `sp-impact-uncovered` | fronteira: este spec **edita o conteúdo** do padrão e mantém o caminho atual; a **mudança de caminho** é do sibling, e é ele quem reescreve declarações que o apontem. Nada aqui presume o resultado dele |
| **Colisão com `restructure-claude-front-namespace`** | aquele spec renomeia o namespace `/skill` para `/automation`; este cita `/skill:align`, `commands/skill/align.md` e herda o prefixo `sk-` no nome do código de finding | fronteira: este spec usa o vocabulário `sk-` que existe hoje e **não** decide o prefixo futuro. Se o sibling renomear, o código novo viaja no mesmo rename que todos os outros `sk-*`, sem exceção própria |
| **Colisão com os três siblings de `functional-checks.sh`** | `isolate-functional-checks-probes`, `plugin-dir-for-functional-checks` e `probe-a-frontmatter-hook-firing` mexem no harness que este spec recusa como casa (forma E) | não há sobreposição de arquivo: este spec não adiciona, remove nem move check nenhum lá, e não cita o harness no seu `## Validation` |
| **Colisão com os siblings de `specs.py`** | `dedupe-specs-py-spec-reader`, `add-specs-py-record-writer` e `split-specs-py-backlog-renderer` refatoram `specs.py`, que este spec cita como precedente (`specs.py:2765`, `cmd_selftest`) | apenas números de linha em prosa podem envelhecer; nenhum comportamento é compartilhado, porque este spec escreve só em `skills.py`. A citação nomeia a função além da linha, para sobreviver a um deslocamento |

## Tasks

### 1. A tabela declarada e a comparação

- [ ] 1.1 Declarar a tabela das sete superfícies de versão no topo do módulo, com caminho, forma de extração e consumidor
      files: plugins/quenching/assets/bin/skills.py
      pattern: plugins/quenching/assets/bin/skills.py (INSTALLED_TOOLS, linha 1516)
- [ ] 1.2 Escrever a função de comparação: constante parseada e nunca o valor com fallback, `marketplace.json` pela entrada cujo `name` é `quenching`, arquivo declarado ausente como falha e não skip
      files: plugins/quenching/assets/bin/skills.py
      verify: python3 plugins/quenching/assets/bin/skills.py selftest
- [ ] 1.3 Ligar a asserção em `cmd_selftest` com o skip honesto quando `resolve_plugin_root()` devolve `None`, e publicar o `pluginRoot` resolvido no payload
      files: plugins/quenching/assets/bin/skills.py
      pattern: plugins/quenching/assets/bin/specs.py (cmd_selftest, o early return da linha 2765)
      verify: python3 plugins/quenching/assets/bin/skills.py selftest --json
- [ ] 1.4 Redigir a mensagem do finding para nomear as superfícies em desacordo e apontar o `/specs:conclude` step 5 como o momento em que as sete se movem juntas, para que um vermelho no meio do bump se leia como tal
      files: plugins/quenching/assets/bin/skills.py

### 2. A fixture e a passagem de mutação

- [ ] 2.1 Acrescentar a fixture de plugin divergente ao lado do controle conformante já existente, e a expectativa correspondente
      files: plugins/quenching/assets/bin/skills.py
      pattern: plugins/quenching/assets/bin/skills.py (DRIFT_FIXTURE e EXPECTED_DRIFT, linhas 1164-1188)
      verify: python3 plugins/quenching/assets/bin/skills.py selftest
- [ ] 2.2 Provar que o controle conformante continua limpo — uma checagem que acusa um plugin em ordem vale menos que nenhuma
      verify: python3 plugins/quenching/assets/bin/skills.py selftest --json
- [ ] 2.3 Rodar a passagem de mutação de `docs/standards/quality/selftest-mutation.md` sobre a asserção nova, conforme `## Validation` braço 2, e registrar o resultado na mensagem do commit que a fez
      verify: uma constante fora por um dígito faz o selftest sair 1 nomeando a superfície; revertida, sai 0; uma constante apagada falha como superfície ilegível

### 3. O vocabulário e os três comentários

- [ ] 3.1 Nomear o código de finding com o prefixo em vigor no momento do merge, conforme `## Open Decisions`, e mantê-lo fora do vocabulário de sweep do `/skill:align`
      files: plugins/quenching/assets/bin/skills.py
      verify: python3 plugins/quenching/assets/bin/skills.py --root . lint --json
- [ ] 3.2 Apontar o comentário das linhas 1606-1608 de `skills.py` para o lugar onde o lockstep passou a ser conferido, em vez de para um `elsewhere` inexistente
      files: plugins/quenching/assets/bin/skills.py
- [ ] 3.3 Fazer os três comentários ao lado de `VERSION` citarem a tabela declarada em vez de enumerarem subconjuntos diferentes entre si
      files: plugins/quenching/assets/bin/skills.py, plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/hooks/okf-validate.py
      verify: python3 plugins/quenching/assets/bin/specs.py selftest && python3 plugins/quenching/assets/hooks/okf-validate.py selftest

### 4. O padrão que passa a ter um verificador

- [ ] 4.1 Reescrever §Verifying de `docs/standards/ci-cd/versioning-release.md` para a chamada única que falha, e **cortar** as cinco leituras manuais que ela substitui
      files: docs/standards/ci-cd/versioning-release.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
- [ ] 4.2 Acertar §The seventh file de `docs/standards/ci-cd/versioning-release.md` conforme a decisão registrada em `## Open Decisions`, e rotear como oferta de `/docs:add` o que passar de acertar a frase para refazer o argumento
      files: docs/standards/ci-cd/versioning-release.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
- [ ] 4.3 Rodar o bloco de verificação do skeleton inteiro de CLAUDE.md §Operating this repo, conforme `## Validation` braço 5
      verify: os seis comandos do braço 5 saem como o bloco declara
