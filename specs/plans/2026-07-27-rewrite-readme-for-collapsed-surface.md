---
slug: rewrite-readme-for-collapsed-surface
title: Rewrite README.md for the collapsed command surface
verification: per-section
priority: {level: 20, criticality: high, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# Rewrite README.md for the collapsed command surface

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a fourteen-heading skeleton. Every other heading below is created on
     first write by `specs.py section <slug> "<Heading>" --write`, which inserts it in the
     canonical position with the guidance comment kept here.

     THE PHASE-SCOPED EXPLICIT-NONE RULE. A heading is required — and required to carry
     `- none — <reason>` when it has nothing in it — only once ITS OWN phase gate is reached:

       new (capture)        `## Problem`
       promote -> ready/    the nine definition sections (`## Problem` .. `## Risks`)
                            AND `## Tasks`
       ready/  (warn only)  `## Handoff` non-empty
       promote -> archive/  `## Outcome`

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

O README do plugin é o primeiro arquivo que alguém lê antes de instalar quenching, e hoje ele
descreve uma arquitetura que o plugin abandonou: trinta skills, uma árvore `skills/` que não existe
e doze seções cabeçadas por nomes retirados. `## Problem` mostra que "prosa obsoleta" é o sintoma —
a causa é o README manter uma segunda cópia, escrita à mão e sem nenhuma checagem, da description de
cada command; e mostra o que isso já custa, medido: quatro links que não resolvem, quatro commands
sem entrada nenhuma, e um changelog parado duas releases atrás do `VERSION`.

`## Proposal` lista o que passa a ser verdade, e `## Alternatives Considered` compara as quatro
formas que o manual poderia ter tomado, incluindo a de gerar a lista por código — rejeitada por um
motivo concreto que `## Design` desenvolve: a `description` de um command é material de routing, não
prosa de manual, então a lista continua escrita à mão e ganha uma checagem em vez de um gerador.
`## Design` também fixa o que **não** pode se mover — o heading `## Cost model`, porque quatro
citações vivas apontam para aquela âncora e duas delas embarcam dentro do plugin — o que sai do
arquivo por pertencer aos standards deste repo e não ao produto, e onde a checagem passa a morar
para que ela realmente rode depois deste spec. Essa última decisão é o que `## Impact` declara como
o único standard que este spec escreve.

`## Validation` é onde a promessa fica exigível: oito asserções, todas rodadas contra o arquivo atual
durante o develop, então cada uma já se sabe verde ou vermelha e por quê. Vale ler junto com
`## Risks`: dos nove riscos listados, cinco são fechados por uma asserção nominal, e o mais caro
deles — uma âncora quebrada que embarca para quem já adotou o plugin — é o único cujo conserto não é
um revert, o que é por que ele roda antes do merge.

`## Tasks` põe a checagem antes da reescrita, de propósito, para a autoria ter sinal desde a primeira
linha. `## Out of Scope` desenha a fronteira com três specs que reescreveriam este mesmo arquivo,
`## Risks` nomeia cada um deles, e `## Open Decisions` guarda as duas perguntas que a autoria resolve
melhor do que a antecipação.
## Problem

`plugins/quenching/README.md` ainda documenta a arquitetura de dois arquivos que o spec
`collapse-skills-into-commands` apagou. A task 5.3 daquele spec tinha escopo só em §Cost model, que
foi reescrita; **as outras ~131 linhas não foram** — §The thirty skills, o layout `.claude/skills/`,
os caminhos de citação `skills/*/references/` e toda a prosa de wrapper descrevem uma forma que o
plugin não tem mais.

Um rename cego sobre o arquivo inteiro foi **tentado e revertido** durante aquele spec: mastigou 28
caminhos de link em formas como `skills//docs:add/references/homes.md`. Essa é a evidência de que
aqui é autoria, e não substituição — e a razão de o trabalho ter ficado fora de uma migração cujo
diff tinha de continuar revisável.

Este é o artefato obsoleto mais público que o collapse deixou para trás: o README é o que um adotante
em perspectiva lê primeiro, e hoje ele descreve 30 skills, uma árvore `skills/` que não existe e
caminhos de citação que não resolvem em lugar nenhum.

Registrado nas `## Discoveries` do spec arquivado:
[/specs/archive/2026-07-26-collapse-skills-into-commands.md](/specs/archive/2026-07-26-collapse-skills-into-commands.md)

### A causa, não o sintoma

Ler o arquivo mostra que "prosa obsoleta" é o sintoma. O defeito causal é que o README mantém uma
**segunda cópia, escrita à mão, da description de cada command** — treze blocos `###` cuja única
fonte é alguém redigitando o que o frontmatter de `commands/**/*.md` já diz. Essa cópia não tem
nenhuma checagem, então ela deriva a cada mudança de surface; o collapse apenas tornou a deriva
visível em escala. O próprio arquivo admite isso nas linhas 64–66, com um aviso de que a prosa
por command precede dois folds e que "a full rewrite is parked as its own spec" — este spec.

Os três `QUENCHING.md` shipped, que descrevem a mesma surface, **já foram reescritos e estão
limpos**: `grep -n 'quenching-\|skills/'` em `assets/docs/QUENCHING.md`,
`assets/specs/QUENCHING.md` e `assets/claude/QUENCHING.md` não devolve nenhuma ocorrência do
vocabulário retirado. O README é o último inventário de surface obsoleto que restou dentro de
`plugins/quenching/`.

### Por que agora

O custo já é composto e visível para quem usa:

- **Quatro alvos de link não resolvem** — verificado com um walk sobre todo link relativo do
  arquivo: `skills/quenching-docs-add/references/homes.md` (linha 116),
  `skills/quenching-skill-new/references/doctrine.md` (252),
  `skills/quenching-skill-new/references/taxonomy.md` (255) e
  `skills/quenching-align-all/references/sweep-doctrine.md` (623). Um quinto,
  `/docs/standards/automation/context-budget.md` (461), é absoluto de raiz e morre em qualquer
  render fora de um checkout local.
- **Quatro das vinte e seis commands não têm entrada nenhuma no manual**: `/skill:eval`,
  `/skill:retro`, `/skill:agent:new` e `/skill:hook:new`. `/skill:retro` aparece uma única vez no
  arquivo, dentro de um parêntese de §Cost model.
- **O changelog para em 4.2.0 enquanto `VERSION` lê 4.4.0** — duas releases não registradas no
  único arquivo que um adotante lê para decidir se atualiza.
- A cada semana que passa sobe o custo de conflito com `restructure-claude-front-namespace`, que
  renomearia todo `/skill:*` deste mesmo arquivo.

## Proposal

- O manual descreve **todas** as commands que existem em `commands/**`, uma linha por command, e
  nenhuma entrada nomeia um artefato que o plugin não tem mais. A contagem é uma propriedade das
  linhas da tabela, não uma afirmação em prosa — ela aparece escrita só onde é inevitável, e ali é
  comparada com `doctor --json`.
- Nenhum heading do arquivo carrega nome de skill retirado (`quenching-docs-*`, `quenching-skill-*`):
  a identidade de cada command é o caminho invocável, como
  `docs/standards/naming/command-surface.md` §The path IS the identity (`authority: current`) exige.
- **Todo link relativo do arquivo resolve.** Os quatro alvos hoje quebrados deixam de existir, e o
  único link absoluto de raiz passa a ser relativo.
- As quatro commands hoje sem entrada no manual — `/skill:eval`, `/skill:retro`,
  `/skill:agent:new`, `/skill:hook:new` — aparecem com o mesmo peso das outras vinte e duas.
- `## Upgrade` registra **4.3.0 e 4.4.0**, então o log para de terminar duas releases atrás do
  `VERSION`.
- O heading `## Cost model` e a tabela de model policy dentro dele continuam existindo e continuam
  alcançáveis pela âncora `#cost-model`.
- Nenhuma doutrina de operação **deste** repo permanece restatement no README: o procedimento do
  lockstep de seis fontes e o how-to do `functional-checks.sh` viram ponteiros para os donos em
  `docs/standards/`.
- Uma **checagem mecânica** compara a lista de commands do README com `commands/**`, falha quando as
  duas divergem, e **roda dali para frente** — ela entra no bloco de verificação de CLAUDE.md, junto
  das outras que este repo já roda, em vez de existir só dentro deste spec.
- O arquivo fica **menor** do que as 764 linhas atuais.
## Out of Scope

- **`.claude-plugin/plugin.json` e `.claude-plugin/marketplace.json`.** Carregam a mesma classe de
  defeito — `plugin.json` diz "Twenty-four commands" e `marketplace.json` diz "eight /specs:*" e
  "five /skill:*", contra 26 / 9 / 6 reais. Ficam fora por duas razões: são campos `description`
  sob orçamento de caracteres, uma restrição que o corpo de um README não tem; e o item (4) das
  `## Discoveries` de `retire-skill-vocabulary` já registra `plugin.json` nominalmente. Absorver a
  discovery de um sibling é decidir por ele.
- **Uma regra `sk-*` em `skills.py` para a lista do README.** Cortado no bank adversarial, e a razão
  está em `## Open Decisions`: `skills.py` é instalado em repo de terceiro, e nenhum repo adotante
  tem o README do plugin — a regra cobraria de todos uma checagem que só este repo pode rodar.
- **Os três `QUENCHING.md` shipped.** Verificados limpos, não há trabalho. Eram o candidato mais
  óbvio a "também está obsoleto" e não estão.
- **O `description` de frontmatter de qualquer command.** É território de `/skill:new` e do spec
  `restore-routing-info-on-docs-commands`. Este spec não edita nenhum arquivo sob `commands/**`.
- **Renomear `/skill:*` para `/automation:*`.** É o `restructure-claude-front-namespace`, que está
  `designed` e bloqueado. Este spec descreve a surface que existe hoje.
- **A auditoria dos bodies contra a doutrina de escrita.** É o audit read-only de `/skill:align`,
  human-driven, e nada nele muda o README.
- **Uma zona `<!-- GENERATED -->` renderizada por `skills.py`.** Rejeitada em
  `## Alternatives Considered` e registrada aqui para não voltar: exigiria código novo no tool e
  colaria descriptions de ~1.000 caracteres, ilegíveis como manual.
- **O bump de versão.** `docs/standards/ci-cd/versioning-release.md` §When the bump happens é
  explícito — "A version bump is never a task in a spec's `## Tasks`". O bump acontece em
  `/specs:conclude`, imediatamente antes do merge, e não como trabalho deste spec.
## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/quality/surface-verification.md` — uma seção nova: um inventário escrito à mão de
  uma surface montada em session start precisa de uma checagem mecânica contra o tool, e a casa dessa
  checagem é o bloco de verificação do harness, não um `## Validation` de spec. O doc já é
  `authority: current` e já tem §What this does not cover; a regra entra ali e não vira doc novo,
  porque um segundo doc sobre verificar a surface seria o segundo nome que
  `docs/standards/naming/command-surface.md` proíbe em espírito.

### Standards at `authority: background` this spec may resolve

- none — nenhum standard `background` cobre documentação de produto nem inventário de surface. Os
  candidatos foram checados: `quality/surface-verification.md`, `quality/bundle-verification.md`,
  `naming/command-surface.md` e `ci-cd/versioning-release.md` são todos `authority: current`.

### Product code this spec expects to touch

- `plugins/quenching/README.md` — o arquivo inteiro. É o objeto do spec.
- `CLAUDE.md` — **uma linha** no bloco de verificação de §Operating this repo. Nenhuma outra parte do
  harness muda, e a doutrina que sai do README vira ponteiro para `docs/standards/`, não texto novo
  aqui.

**Nada em repo adotante muda de forma.** O README do plugin não é instalado em lugar nenhum. A única
exposição para fora é a âncora `#cost-model`, que dois arquivos shipped resolvem em runtime — e é
exatamente por isso que ela é a asserção V2.

## Validation

Oito asserções. Todas foram **rodadas contra o arquivo atual** durante o develop, então cada uma é
vermelha hoje pelo motivo certo, ou verde e a obrigação é continuar verde. Rodar de
`plugins/quenching/`, salvo onde indicado.

**V1 — a lista de commands do README bate com o disco.** A asserção central do spec.

```bash
diff <(find commands -name '*.md' | sed 's#^commands/##; s#\.md$##; s#/#:#g; s#^#/#' | sort) \
     <(sed -n '/^## The twenty-six commands/,/^## Install/p' README.md \
        | grep -o '`/[a-z][a-z:-]*`' | tr -d '`' | sort -u)
```
Exit 0, nenhuma linha de saída. Medido hoje: reporta uma diferença,
`/communications:teams:create`, exemplo fictício na prosa de automation que a reescrita apaga. Se o
heading `## The twenty-six commands` mudar de número, o `sed -n` acompanha, e a contagem escrita nele
é conferida por `skills.py --root . doctor --json` (26 commands, `findings: []`).

**V2 — toda âncora `README.md#...` citada no repo resolve.** A asserção cujo custo de falha não é
local. Rodar da raiz do repo:

```bash
grep -rho 'README\.md#[a-z0-9-]\+' --include='*.md' --include='*.py' --include='*.sh' . \
  | sed 's/.*#//' | sort -u | while read -r a; do
    grep -o '^#\+ .*' plugins/quenching/README.md | sed 's/^#\+ //' \
      | tr 'A-Z' 'a-z' | sed 's/[^a-z0-9 -]//g; s/ /-/g' | grep -qx "$a" \
      || echo "MISSING #$a"
  done
```
Nenhuma linha `MISSING`. Medido hoje: `#cost-model` é a única âncora citada e resolve — verde, e a
obrigação é continuar verde. Os quatro citadores são `CLAUDE.md:65`, `README.md:68`,
`plugins/quenching/assets/references/docs-import/sources.md:83` e
`plugins/quenching/commands/docs/import.md:58`.

**V3 — todo link relativo do README resolve, e nenhum é absoluto de raiz.**

```bash
grep -o '](\([^)#]*\))' README.md | sed 's/^](//; s/)$//' | grep -v '^https\?://' | sort -u \
  | while read -r p; do case "$p" in /*) echo "ABS-ROOT $p";; *) [ -e "$p" ] || echo "BROKEN $p";; esac; done
```
Nenhuma linha. Medido hoje: quatro `BROKEN` e um `ABS-ROOT` — os cinco que `## Problem` §Por que
agora enumera.

**V4 — o vocabulário retirado não sobreviveu.**

```bash
grep -c '^### `quenching-' README.md   # 0  (hoje: 12)
grep -c 'skills/' README.md            # 0  (hoje: 12)
```
Zero nas duas. `skills/` é literal e o plugin não tem essa árvore: qualquer ocorrência restante é
caminho morto ou prosa de wrapper.

**V5 — o arquivo encolheu.** `wc -l < README.md` menor que **764**, o valor de hoje.

**V6 — a figura de always-on é o ceiling declarado, não um número lembrado.**

```bash
python3 assets/bin/skills.py --root . budget --json | python3 -c "import json,sys;print(json.load(sys.stdin)['ceiling'])"
```
O valor devolvido aparece nas linhas de §Cost model que fazem a afirmação corrente. A linha da
entrada de changelog **4.2.0** guarda o número histórico e não é tocada — hoje o mesmo `12,726`
aparece em três linhas (451, 459, 562) e só as duas primeiras são afirmação corrente.

**V7 — o changelog alcança o `VERSION`.**

```bash
for v in $(cat VERSION) 4.3.0; do grep -q "^- \*\*$v:\*\*" README.md || echo "ABSENT $v"; done
```
Nenhuma linha. Medido hoje: 4.4.0 e 4.3.0 ausentes, 4.2.0 presente.

**V8 — o esqueleto do repo continua conformante.** O bloco de CLAUDE.md §Operating this repo, sem
alteração de comportamento esperada: `doctor --json` em 26 commands e `findings: []`, `lint --json`
exit 0, os três `selftest`, e `okf-validate.py assets/docs` em `0 error(s), 0 warning(s)`. Este spec
não mexe em nenhum script, então qualquer mudança aqui é regressão.

## Design

### Uma tabela por front, não um bloco de prosa por command

O manual passa a ser **três tabelas mais uma linha de raiz** — dez `/docs:*`, nove `/specs:*`, seis
`/skill:*`, o `/align` de raiz — com uma linha por command: nome invocável e uma frase dizendo o que
ele faz. É a forma que §The `specs/` flow já prova dentro do próprio arquivo (linhas 322–331): foi
o único front reescrito no fold, é o único que não obsoleteu, e é o único cuja contagem é
**estrutural** (linhas se contam) em vez de prosa ("the ten that act on...").

**A regra durável:** um inventário escrito à mão de uma surface montada em session start só se
justifica quando a contagem é uma propriedade da estrutura e não uma afirmação em prosa.

Isso derruba treze blocos `###`, e com eles os quatro caminhos de citação quebrados — que só existem
porque cada bloco reescrevia à mão um caminho que o body do command cita corretamente por
`${CLAUDE_PLUGIN_ROOT}`.

### A coluna de papel é prosa autoral, não paráfrase da description

A suposição que sustentaria "só aponte para o frontmatter" é que a `description` de um command serve
como manual. **Ela é falsa**, e vale testar em vez de assumir: a `description` de
`commands/skill/retro.md` são onze linhas de trigger phrases e de fronteiras `Not for:`. É material
de routing, escrito para o roteador, não para um leitor humano.

Logo a coluna de papel carrega a carga explicativa inteira e é **escrita**, uma frase por command,
como as linhas de `/specs:*` já são. Uma paráfrase da description reproduziria o defeito em prosa
mais curta.

### O que sobrevive byte a byte: `## Cost model`

O heading `## Cost model` e a tabela de model policy dentro dele **não podem ser renomeados nem
cortados**. Quatro citações vivas apontam para aquela âncora:

- `CLAUDE.md:65` — e declara o README **dono** da política: "see the model-policy table in
  README.md#cost-model".
- `README.md:68`, o README de raiz do repo.
- `plugins/quenching/assets/references/docs-import/sources.md:83` e
  `plugins/quenching/commands/docs/import.md:58` — **os dois shipped**, resolvendo
  `${CLAUDE_PLUGIN_ROOT}/README.md#cost-model` em runtime, na sessão de quem adotou o plugin.

Uma âncora markdown quebrada falha em silêncio. Por isso a checagem das âncoras é uma asserção de
`## Validation`, e não uma lembrança de quem escreve.

### O que sai: doutrina de operação do repo, não do produto

CLAUDE.md §The plugin itself diz que o README é a documentação **do produto** e que os standards
deste repo não são restated ali. Duas coisas cruzam essa linha hoje e saem, viram ponteiro:

- o procedimento do lockstep de seis fontes em `## Upgrade` (linhas 539–545) — dono
  `docs/standards/ci-cd/versioning-release.md`. Ficam as duas frases voltadas ao adotante: o que
  Claude Code lê para detectar um upgrade, e que os três tools installed comparam `--version`.
- o how-to do `assets/checks/functional-checks.sh` (linhas 470–482) — donos CLAUDE.md §Operating
  this repo e `docs/standards/quality/surface-verification.md`.

**Duas coisas que parecem candidatas e ficam.** As "two rules that must survive any future
optimization" (linhas 510–518) ficam: aparecem também em CLAUDE.md, mas ali como regra de refactor
deste repo, e aqui como **model policy que embarca para o adotante** que está lendo justamente a
tabela de política. E os "OKF-strict rules the plugin enforces" (linhas 389–408) ficam: é o contrato
que o plugin impõe no repo de terceiro, ou seja, produto.

### Autoria, nunca substituição

O `## Problem` guarda a evidência: um rename cego mastigou 28 caminhos e foi revertido. Portanto
nenhuma passada de `sed`, `perl -pi` ou replace-all sobre este arquivo, em nenhuma task. Cada linha
que muda é lida antes. Custa mais tempo de autoria e é exatamente o que a evidência arquivada
compra.

### A tabela derivada do tool, nunca da memória

A forma como o número errado entra é sempre a mesma: alguém escreve a contagem de cabeça. É o que
`plugin.json`, `marketplace.json` e o README atual exibem, todos os três. A task que escreve as
tabelas parte da saída de
`find commands -name '*.md' | sed 's#^commands/##; s#\.md$##; s#/#:#g; s#^#/#' | sort`, e de
`skills.py --root . doctor --json` para a contagem.

**Corolário do bank adversarial:** a contagem literal é evitada onde é evitável. A surface cresceu
duas vezes na última semana — `/specs:isolate` a 25ª, `/skill:retro` a 26ª — então "vinte e seis"
escrito em prosa é uma afirmação com prazo de validade curto. O texto diz "as commands" e deixa as
linhas da tabela carregarem o número; onde ele é inevitável, a asserção V1 o compara com
`doctor --json`.

### A lista tem de ser checável, e a checagem tem de ter casa

Vinte e seis linhas de tabela em lockstep manual com `commands/**` é o defeito deste spec
reintroduzido a um décimo do tamanho. Isso só se aceita se o lockstep for verificado por máquina — e
uma asserção que vive **só** em `## Validation` roda uma vez, no conclude deste spec, e nunca mais.
Foi assim que a lista chegou ao estado atual.

A checagem entra no bloco de verificação de CLAUDE.md §Operating this repo, junto das outras que este
repo já roda a cada mexida em `plugins/quenching/`. Duas alternativas foram descartadas:

- **Uma regra `sk-*` em `skills.py`.** O tool é instalado em repo de terceiro por `/skill:align`, e
  nenhum repo adotante tem o README do plugin — a regra cobraria de todo adotante uma checagem que
  só este repo pode rodar. Fica em `## Open Decisions` a condição que reabriria isso.
- **Só `## Validation`.** É a forma que não roda. Rejeitada pelo motivo acima.

A checagem em si é um diff de dois conjuntos, e foi **medida contra o arquivo atual** antes de
entrar aqui: os nomes invocáveis derivados de `commands/**/*.md` contra os tokens `/x:y` em backtick
dentro da faixa do manual do README. Hoje ela reporta exatamente uma diferença,
`/communications:teams:create` — um exemplo fictício na prosa obsoleta de automation, que a
reescrita apaga. Ou seja: a checagem já é verde no dia em que a reescrita pousa, e vermelha hoje pelo
motivo certo.

### A estrutura tem de ser barata de renomear

`restructure-claude-front-namespace` renomearia todo `/skill:*` deste arquivo, e já lista
`README.md` entre os arquivos que reescreve. A tabela por front torna esse rename **uma coluna de
find-and-replace** em vez de treze blocos de prosa reautorados. Isso é um argumento a favor da
forma, e não só uma nota de agendamento.

### A figura de always-on lida do tool, não transcrita

Hoje o README afirma 12.726 caracteres em três linhas, e afirma que esse número "equals the
surface's total". `skills.py --root . budget --json` devolve agora `total: 12875`,
`ceiling: 12726`, `ok: false` — a afirmação de igualdade é transitória por construção. O spec
`restore-routing-info-on-docs-commands` é o dono dessa figura (sua task 2.4 edita exatamente "the
three lines carrying the figure, and nothing else").

Decisão: o README passa a citar o **ceiling** declarado, o valor que só se move numa revisão
deliberada e cuja casa é `docs/standards/automation/context-budget.md`, e a asserção de
`## Validation` compara com `budget --json .ceiling`. Assim a ordem em que os dois specs pousam
deixa de importar.

### Contratos que este design não pode contradizer

- `docs/standards/naming/command-surface.md` §The path IS the identity (`authority: current`) —
  "There is **no second name**". O README atual viola isso treze vezes; a reescrita é enforcement,
  não preferência.
- `docs/standards/ci-cd/versioning-release.md` §When the bump happens — nenhuma task de bump.
- CLAUDE.md §The plugin itself — o README é doc do produto; standards do repo não são restated.
- CLAUDE.md §Two rules that must survive any refactor — nada aqui toca `context: fork` nem tier de
  modelo.

## Alternatives Considered

Quatro formas inteiras para o manual, comparadas antes de escrever qualquer linha.

| Forma | Custo | O que compra | O que impede |
| --- | --- | --- | --- |
| **A. Uma tabela por front, uma linha por command** (escolhida) | autoria de 26 linhas mais três cortes | contagem estrutural, ~230 linhas a menos, os quatro links quebrados desaparecem com os blocos, rename barato | nada relevante — a description de cada command continua sendo a fonte longa |
| B. Manter os treze blocos `###` e reescrever cada um | autoria de 26 blocos de prosa | fidelidade à estrutura atual | é a forma que produziu esta bagunça: 26 blocos em lockstep manual com 26 descriptions |
| C. Apagar o manual e apontar para o frontmatter | quase zero | nunca deriva | um adotante no GitHub não lê frontmatter, e §Problem diz que o adotante é o público inteiro do arquivo |
| D. Zona `<!-- GENERATED -->` renderizada por `skills.py` | código novo no tool mais uma checagem | deriva zero por construção | ou cola descriptions de ~1.000 caracteres, ilegíveis, ou exige uma segunda linha curta escrita à mão — a deriva de volta, agora com um gerador para manter |

**B perdeu** porque duplica por design: treze cópias escritas à mão de um texto que já embarca dentro
do arquivo do command. Um bloco por command é o shape skill+wrapper que o collapse acabou de
remover, aplicado a prosa.

**C perdeu** no público, não no custo. É a alternativa mais barata e a mais tentadora, e um README
sem lista de commands falha o único leitor que `## Problem` nomeia. A disciplina dela foi adotada
mesmo assim: uma linha por command, não um parágrafo.

**D perdeu** por legibilidade e por preço. É a forma anti-drift que este repo já usa em
`plans/index.md` e no registry de automation, e teria sido a resposta certa se a description fosse
prosa de manual. Ela não é (ver `## Design` §A coluna de papel). Uma zona gerada a partir de
descriptions de routing seria ilegível; uma gerada a partir de resumos escritos à mão seria a mesma
deriva com um gerador em cima. A parte boa de D — a verificação mecânica — foi extraída sem o
gerador, e virou `## Validation` V1.

**Não fazer nada** foi considerado e perdeu no arquivo: o README já carrega, nas linhas 64–66, um
aviso admitindo que a prosa está obsoleta e prometendo esta reescrita. Um aviso de obsolescência
permanente é pior do que a obsolescência, porque ensina o leitor a não confiar no resto do arquivo.

## Open Decisions

- **A checagem da lista graduaria para dentro de `skills.py lint`?** Este spec a instala como um
  comando no bloco de verificação de CLAUDE.md, e não como código no tool — ver `## Design` §A lista
  tem de ser checável. Motivo: `skills.py` é instalado em repo de terceiro por `/skill:align`, e o
  README do plugin não existe em nenhum repo adotante, então uma regra `sk-*` cobraria de todo
  adotante uma checagem que só o repo do plugin pode rodar. **Decidido por:** aparecer um segundo
  consumidor, isto é, algum repo adotante mantendo à mão um inventário da sua própria surface. Até
  lá, o comando no bloco de CLAUDE.md é a casa correta e a decisão não precisa ser reaberta.
- **A prosa por command do README fica com uma frase por command, ou com um parágrafo para as poucas
  que carregam contrato próprio?** Quatro candidatas a parágrafo: `/docs:align` (a regra de refresh
  de `QUENCHING.md`, hoje dona única na linha 429–433), `/skill:align` (a fronteira do audit
  read-only), `/specs:conclude` (a ordem em que o merge é a última ação) e `/align` (a autorização
  que aninha um nível). **Decidido por:** escrever as vinte e seis linhas primeiro. Se a linha de uma
  dessas quatro só fizer sentido citando o body, ela ganha um parágrafo curto abaixo da tabela do seu
  front; se ela se sustentar sozinha, a tabela basta. É uma decisão que a autoria resolve, não uma
  que a antecede — e resolvê-la antes é o que produziu os treze blocos atuais.

## Risks

| Risco | Mitigação |
| --- | --- |
| **A âncora `#cost-model` quebra em silêncio.** Renomear ou cortar aquele heading mata quatro citações vivas, duas delas dentro de arquivos shipped que resolvem em runtime na sessão de quem adotou o plugin. Um link markdown quebrado não emite erro nenhum. | `## Validation` V2 assere que o heading existe exatamente uma vez **e** que cada `README.md#âncora` citado no repo resolve. É uma asserção de máquina, não uma lembrança de quem escreve. |
| **Este é o risco que o revert não conserta.** Uma âncora quebrada que embarcou fica quebrada na cópia installed de cada adotante até ele atualizar — reverter o arquivo neste repo não alcança o que já saiu. | Por isso V2 roda **antes do merge**, e não na review. É a única asserção deste spec cujo custo de falha não é local. |
| **A contagem erra outra vez.** A surface cresceu duas vezes na última semana (`/specs:isolate` a 25ª, `/skill:retro` a 26ª). Um número escrito em prosa fica errado no dia seguinte. | O texto evita a contagem literal onde ela é evitável, e as linhas da tabela passam a ser o número. Onde ela é inevitável (o heading do manual), V1 compara com `doctor --json`. |
| **Alguém tenta o rename cego de novo.** Foi exatamente o que mastigou 28 caminhos no spec do collapse. `sed` sobre 764 linhas é rápido e parece seguro. | `## Handoff` proíbe nominalmente `sed`, `perl -pi` e replace-all sobre o arquivo, e `## Design` §Autoria, nunca substituição guarda a evidência arquivada de por quê. |
| **A checagem é escrita e nunca roda.** Uma asserção que vive só em `## Validation` roda uma vez, no conclude deste spec, e depois nunca — que é como a lista chegou ao estado atual. | A task 4.1 instala V1 no bloco de verificação de CLAUDE.md, junto das outras sete que este repo já roda. Sem essa task o spec entrega prosa nova e a mesma ausência de checagem. |
| **`restructure-claude-front-namespace` merge primeiro e a reescrita é jogada fora.** Ele renomeia todo `/skill:*` deste arquivo e já lista `README.md` entre os que reescreve. | ACCEPTED — a forma escolhida em `## Design` torna esse rename uma coluna de find-and-replace em vez de treze blocos reautorados, e V1 detecta a divergência no mesmo dia. Ele está `designed`, bloqueado em `instrument-and-extend-skill-front` e com dois `## Open Decisions` abertos: não está perto. |
| **As entradas de changelog 4.3.0 e 4.4.0 são inventadas a partir de subjects de commit.** É a forma mais fácil de escrever duas entradas plausíveis e erradas. | A task 3.1 nomeia as fontes: `git log` mais os specs de `specs/archive/` que cada release fechou. Uma entrada que não sai de um spec arquivado não é escrita. |
| **O arquivo cresce em vez de encolher.** Toda reescrita tende a expansão, e "cobrir as quatro commands que faltavam" é um convite. | É um outcome exigível em `## Proposal` e uma asserção em V5, comparando com as 764 linhas de hoje. |
| **O público primário do arquivo não é medido.** `## Problem` fala do adotante em perspectiva, e não existe telemetria nenhuma que prove que alguém leu este README. | ACCEPTED — e a premissa não depende disso. O consumidor medível é uma sessão Claude neste repo: CLAUDE.md:102 roteia para o arquivo como "the command-by-command manual", e dois arquivos shipped resolvem a âncora em runtime. O adotante é o público secundário, não o único. |

## Tasks

### 1. A checagem primeiro, para a reescrita ter sinal

- [ ] 1.1 Instalar a asserção V1 no bloco de verificação de `CLAUDE.md` §Operating this repo, junto
      das sete que já estão lá, com uma linha dizendo o que ela prova. Nada mais no harness muda
      files: CLAUDE.md
      verify: ## Validation V1
- [ ] 1.2 Escrever a regra em `docs/standards/quality/surface-verification.md` como seção nova
      (`authority: current`, o doc já é): um inventário à mão de uma surface montada em session start
      precisa de checagem mecânica contra o tool, e a casa dela é o bloco do harness. Registrar por
      que não é regra `sk-*` em `skills.py`, com a condição de reabertura que `## Open Decisions`
      guarda
      files: docs/standards/quality/surface-verification.md
      pattern: docs/standards/quality/surface-verification.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs

### 2. O manual

- [ ] 2.1 Derivar a verdade e deixá-la à vista antes de escrever: rodar
      `find commands -name '*.md' | sed 's#^commands/##; s#\.md$##; s#/#:#g; s#^#/#' | sort` e
      `skills.py --root . doctor --json`, e escrever as tabelas a partir dessa saída, nunca de
      memória
      verify: ## Validation V1
- [ ] 2.2 Reescrever §The twenty-six commands: apagar os doze blocos `###` cabeçados por
      `quenching-*` e a nota de obsolescência das linhas 64–66; escrever a tabela `/docs:*` (dez
      linhas) e a tabela `/skill:*` (seis linhas, incluindo `/skill:eval`, `/skill:retro`,
      `/skill:agent:new` e `/skill:hook:new`, hoje sem entrada nenhuma) na forma que §The `specs/`
      flow já usa. Uma frase escrita por command, nunca paráfrase da `description`. Sem `sed`
      files: plugins/quenching/README.md
      pattern: plugins/quenching/README.md
      verify: ## Validation V1 + V4
- [ ] 2.3 Conferir a tabela `/specs:*` existente linha por linha contra o disco e escrever a linha do
      `/align` de raiz. Ela não obsoleteu no fold — o trabalho é confirmar, não reescrever
      files: plugins/quenching/README.md
      verify: ## Validation V1
- [ ] 2.4 Resolver os cinco links: os quatro `skills/...` mortos passam a apontar para o arquivo real
      sob `assets/references/`, e `/docs/standards/automation/context-budget.md` vira relativo
      files: plugins/quenching/README.md
      verify: ## Validation V3
- [ ] 2.5 Varrer o restante do arquivo pelo vocabulário retirado que os blocos não levaram — as
      ocorrências de `.claude/skills/`, "skill" onde se quer dizer command, e "All skills reach the
      shared payload" em §Install. Lido linha por linha, sem replace-all
      files: plugins/quenching/README.md
      verify: ## Validation V4

### 3. Os cortes e o log

- [ ] 3.1 Cortar o procedimento do lockstep de seis fontes em §Upgrade e o how-to do
      `assets/checks/functional-checks.sh`, deixando ponteiro para
      `docs/standards/ci-cd/versioning-release.md` e `docs/standards/quality/surface-verification.md`.
      Preservar as duas frases voltadas ao adotante e as "two rules that must survive" — são model
      policy, e `## Design` §O que sai diz por que ficam
      files: plugins/quenching/README.md
      verify: ## Validation V5
- [ ] 3.2 Escrever as entradas de changelog 4.3.0 e 4.4.0, derivadas de `git log` e dos specs de
      `specs/archive/` que cada release fechou. Uma entrada que não sai de um spec arquivado não é
      escrita
      files: plugins/quenching/README.md
      verify: ## Validation V7
- [ ] 3.3 Trocar a afirmação corrente da figura de always-on por citação do ceiling declarado, sem
      tocar a linha da entrada 4.2.0, que é histórica. `restore-routing-info-on-docs-commands` é o
      dono da figura: se ele já pousou, o valor é o que ele escreveu
      files: plugins/quenching/README.md
      verify: ## Validation V6

### 4. Verificação

- [ ] 4.1 Rodar V1 a V8 e registrar a saída de cada uma
      verify: ## Validation V1 + V2 + V3 + V4 + V5 + V6 + V7 + V8
