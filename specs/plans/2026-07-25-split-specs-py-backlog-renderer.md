---
slug: split-specs-py-backlog-renderer
title: Split the backlog-zone renderer out of specs.py
verification: per-section
priority: {level: 26, criticality: medium, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# Split the backlog-zone renderer out of specs.py

## Overview

Este spec responde a uma anotação, não a um defeito de código. Um plano já arquivado
(`refine-and-execute-specs-flow`) escreveu na seção Risks dele uma regra numérica: se `specs.py`
passasse de ~1.200 linhas, o renderizador da listagem de specs deveria ser extraído para um módulo
separado. `## Problem` abaixo é essa anotação, com as palavras e os números de 25/07/2026.

Três coisas mudaram desde então, e `## Design` mede cada uma. O arquivo está em 3.125 linhas, ou 2,6x
o limite. O alvo que a anotação nomeou representa hoje cerca de 66 linhas — 2,1% do arquivo. E um
standard escrito três dias depois da anotação (`docs/standards/code/frontmatter-parsing.md`) passou a
proibir exatamente o remédio que ela mandava aplicar, porque cada tool que este plugin instala vai
sozinho para o `.claude/hooks/` de um repo alvo e não pode importar um irmão.

Então `## Proposal` não faz o split. Ele retira a regra de limite de linhas e escreve no lugar dela o
contrato que de fato vale para um tool de arquivo único: sem extração, sem orçamento de linhas, e
navegabilidade declarada como a obrigação que substitui as duas. `## Impact` nomeia o único doc que
este spec promete escrever, e `## Alternatives Considered` traz as cinco formas que a resposta poderia
ter tomado — incluindo não fazer nada, e a única extração que seria legal — com o motivo de cada
derrota, para que quem tiver a mesma ideia leia por que ela já foi recusada.

`## Out of Scope` marca a fronteira com os specs irmãos que mexem no mesmo arquivo: nenhuma linha de
lógica é movida aqui. `## Risks` converte o premortem em mitigações nomeadas e em três riscos aceitos
com o motivo escrito, e `## Open Decisions` deixa registrado o que só o humano fecha — se o standard
vale o próprio custo, ou se basta arquivar o spec com o motivo.

Do lado executável: `## Tasks` ordena o trabalho de propósito para que o código prove a regra **antes**
de o standard afirmá-la, `## Validation` fixa os baselines medidos hoje — inclusive o fato de que a
bundle já sai com quatorze warnings advisory, o que torna "zero warnings" uma asserção falsa — e
`## Handoff` carrega o que um executor não consegue derivar, incluindo a obrigação de bump que pertence
ao `/specs:conclude` e nunca a uma task.

## Problem

specs.py passou do limite de ~1.200 linhas que o próprio design dele fixou para o split, e agora tem 1.388 linhas

_(tarefa de backlog v1 — tags: ['specs', 'tooling', 'maintainability'])_

O design do plano `refine-and-execute-specs-flow` nomeou um limite na seção Risks dele: se
`specs.py` passar de ~1.200 linhas, extrair o renderizador da backlog zone para um módulo "rather
than growing one file past reviewability — and note it, do not do it silently." Seis features
entraram naquele plano e o arquivo agora tem 1.388 linhas, então o limite foi ultrapassado e o split
não foi feito. Esta tarefa é o registro. Qualquer split precisa manter o script stdlib-only e
self-contained, já que uma cópia instalada em `.claude/hooks/specs.py` de um repo alvo tem de
continuar funcionando por conta própria.

## Proposal

- A regra de limite de ~1.200 linhas herdada do plano `refine-and-execute-specs-flow` está
  formalmente retirada: nenhum spec, standard ou docstring do repo passa a citá-la como obrigação
  pendente.
- Existe um standard em `docs/standards/code/` que responde, por escrito e no lugar onde o próximo
  leitor tropeça nele, três perguntas que hoje só têm resposta espalhada: um tool shipped pode ser
  mais de um arquivo (não pode), existe um orçamento de linhas (não existe), e o que um arquivo
  longo deve entregar em troca (navegabilidade declarada).
- `specs.py` está em conformidade com esse standard: o docstring do módulo carrega um mapa das dez
  regiões banner do arquivo, por nome e sem números de linha.
- `specs.py selftest` falha quando o mapa e os banners divergem em qualquer direção — uma região
  nova sem entrada no mapa, ou uma entrada no mapa sem região correspondente.
- `render_plans_zone`, `cmd_plans` e todo o resto do comportamento de `specs.py` ficam inalterados:
  este spec não move nenhuma linha de lógica.
- Os dois tools shipped que ainda não carregam o mapa (`skills.py`, `okf-validate.py`) estão
  nomeados como deferral no ledger do próprio standard, não silenciosamente ignorados.

## Out of Scope

- **Reduzir a contagem de linhas de `specs.py`.** A única redução legítima é deduplicação in-file, e
  ela é o spec irmão `dedupe-specs-py-spec-reader`, que nomeia `cmd_plans` como um dos quatro call
  sites dele. Este spec não remove lógica nenhuma, e a fronteira é essa.
- **Extrair `render_plans_zone` / `cmd_plans` para qualquer lugar** — nem para um módulo importável,
  nem para um segundo entry point. `## Design` mede por que o alvo nomeado pela anotação original
  não é uma folha.
- **Virar um orçamento de tamanho para quem cresce o arquivo.** Retirar o limite *permite*
  crescimento; o spec irmão `add-specs-py-record-writer` adiciona um subcomando `record` e não deve
  ser lido como bloqueado por este spec.
- **Levar `skills.py` e `okf-validate.py` à conformidade com o mapa de regiões.** O standard governa
  os três tools shipped, mas este spec só traz `specs.py`; os outros dois entram como deferral
  declarado no ledger do standard, com o gatilho de revisita escrito.
- **Mexer no lockstep de versão.** O bump é ato do `/specs:conclude`, nunca task de spec
  (`docs/standards/ci-cd/versioning-release.md` §When the bump happens).
- **Reabrir a decisão dos três parsers duplicados.** `docs/standards/code/frontmatter-parsing.md` já
  a fechou; este spec cita esse standard como contrato vinculante, não o revisa.
- **Mudar a saída de `plans reindex`.** O formato da GENERATED zone de `plans/index.md` não é
  assunto deste spec; ele é o assunto do spec irmão `decide-plans-index-need`, que pergunta se o
  arquivo precisa existir.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/code/single-file-tool-structure.md` — um tool shipped é um arquivo: sem extração
  para irmão importável, sem orçamento de linhas, navegabilidade declarada como a obrigação que
  substitui as duas, e a regra da folha (só a extração de uma folha paga; um subcomando que consome o
  parser central nunca é folha)

### Standards at `authority: background` this spec may resolve

- none — nenhum standard `authority: background` deste repositório trata de tamanho ou estrutura de
  tool shipped. `quality/selftest-mutation.md` é `background`, mas trata do portão de graduação das
  passadas de mutação, que `## Out of Scope` deixa explicitamente de fora; este spec empresta a
  prática dele sem prová-lo nem promovê-lo.

### Código e docs que este spec espera tocar

- `plugins/quenching/assets/bin/specs.py` — só duas regiões: o docstring do módulo (o mapa das dez
  regiões) e `cmd_selftest` (a assertion `sp-region-map-drift`). Nenhuma outra função, e nenhuma
  mudança de comportamento.
- `docs/standards/code/frontmatter-parsing.md` — uma linha de cross-reference para o standard novo, na
  seção §Why there are three copies and not one module, que é onde alguém com esta pergunta chega
  primeiro. É acréscimo de referência, não revisão da regra daquele doc.
- `docs/standards/code/index.md` e `docs/standards/index.md` — as entradas de listing do doc novo,
  escritas por `/docs:add`, nunca à mão: as tabelas "Current docs" são derivadas do disco e a zona
  GENERATED não se edita.

## Validation

Todos os comandos rodam a partir da raiz do repositório. Os valores de baseline abaixo foram medidos
em 2026-07-30, antes de qualquer task; é contra eles que a comparação vale.

**A assertion nova, e a prova de que ela não é vácua.** As duas execuções juntas são o que
`docs/standards/quality/selftest-mutation.md` exige — um selftest que nunca foi visto falhar não
provou nada:

- `python3 plugins/quenching/assets/bin/specs.py selftest` → exit 0, e a linha de resumo continua
  dizendo `0 error(s)`.
- com **uma entrada removida do mapa de regiões** no docstring, o mesmo comando → exit 1, com um
  finding de código `sp-region-map-drift` nomeando a região sem entrada. Reverter em seguida.
- com **um banner de região removido** e o mapa intacto → exit 1, com um finding
  `sp-region-map-drift` na direção oposta, nomeando a entrada sem região. Reverter em seguida. As
  duas direções são checadas porque um invariante de membresia checado em um só sentido passa com
  metade do conjunto errado.

**Que nada de comportamento mudou.** É a afirmação central de `## Proposal`, e ela é verificável
mecanicamente:

- `python3 plugins/quenching/assets/bin/specs.py plans reindex` seguido de
  `git diff --stat specs/plans/index.md` → o diff tem de estar **vazio**, o que prova que
  `render_plans_zone` e `cmd_plans` produzem a mesma zona de antes.
- `python3 plugins/quenching/assets/bin/specs.py validate --json` → sem finding novo atribuível a
  este spec.
- `python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json` →
  `26 commands`, zero findings, idêntico ao baseline: este spec não toca o command surface.
- `python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json` → exit 0.

**Que o standard novo é conformante.** O baseline da bundle **não** é limpo, e a asserção precisa
respeitar isso ou vira falso positivo:

- `python3 plugins/quenching/assets/hooks/okf-validate.py docs` → baseline medido:
  `0 error(s), 14 warning(s)` (12 `stale-doc`, 2 `resource-unresolved`). A asserção é
  **`0 error(s)`, e nenhum warning novo cujo `path` seja o doc novo**. A contagem total de
  `stale-doc` pode variar sozinha, porque ela depende de datas de commit e é advisory — comparar o
  número total seria uma checagem que quebra por conta própria.
- `python3 plugins/quenching/assets/hooks/okf-validate.py docs --json` → o doc novo aparece na saída
  sem nenhum finding de `severity: ERROR` associado ao caminho dele.

**Que o lockstep continua íntegro.** Um docstring novo em `specs.py` sem bump não chega a repo alvo
nenhum, então a integridade é lida ao fim:

- `cat plugins/quenching/VERSION` e
  `python3 plugins/quenching/assets/bin/specs.py --version` → um único valor. O bump em si é ato do
  `/specs:conclude`, nunca task; esta linha só garante que ninguém o fez pela metade.

**Que a regra morta saiu.**

- `grep -rn '1,200' docs/ plugins/ specs/plans/` → nenhuma ocorrência que apresente o limite como
  obrigação pendente. A citação histórica dentro de `## Problem` e de `## Design` deste spec é
  esperada e não conta: ela é o registro do que a anotação dizia.

## Design

### O que o código realmente é hoje (medido em 2026-07-30, VERSION 4.4.0)

Os números do `## Problem` são de 25/07/2026, quando o spec foi capturado, e não descrevem mais o
arquivo. Medição atual de `plugins/quenching/assets/bin/specs.py`:

| Fato | Valor |
| --- | --- |
| o arquivo inteiro | 3.125 linhas |
| docstring do módulo | linhas 1–83 |
| assets embutidos verbatim (`DEFAULT_SCHEMA` + `TEMPLATE_SPEC`) | linhas 164–495, cerca de 332 linhas |
| linhas em branco / linhas só de comentário | 430 / 188 |
| o alvo nomeado pela anotação: `render_plans_zone` | linhas 2927–2947 (21 linhas) |
| `cmd_plans` | linhas 2950–2990 (41 linhas) |
| `STAGE_ORDER` (2923–2924) + `PLANS_EMPTY` (157–158) | 4 linhas |
| **o alvo nomeado, somado** | **cerca de 66 linhas = 2,1% do arquivo** |
| os dois tools shipped irmãos | `skills.py` 1.802 linhas · `okf-validate.py` 1.369 linhas |

Duas leituras saem daí, e as duas contrariam a anotação.

O limite não foi "ultrapassado": ele está **2,6x atrás**, e nada quebrou nesse caminho. E
`okf-validate.py`, com 1.369 linhas, também já o ultrapassou sem que ninguém tenha anotado nada — o
que é a evidência mais direta de que a regra nunca foi uma regra do repositório. Ela viveu na seção
Risks de **um** plano, sobre **um** arquivo, e nunca subiu para `docs/standards/`. O plano de origem
não existe mais na árvore de trabalho: era uma pasta v1 de três arquivos em
`specs/archive/2026-07-25-refine-and-execute-specs-flow/`, dobrada pela migração, e o texto do risco
só é recuperável por `git show`.

### Decisão 1 — não extrair, porque um standard vinculante proíbe

`docs/standards/code/frontmatter-parsing.md:16-19` (`authority: current`, 2026-07-28) declara que
cada um dos três tools shipped "installs **standalone** into a target's `.claude/hooks/`, so none may
import the others and there is no shared module to hold the rule", e a seção §Why there are three
copies and not one module recusa nominalmente um `frontmatter.py` extraído, porque ele "trades a
duplication problem for a distribution problem". `specs.py:498-501` repete a mesma frase dentro do
código, e `docs/standards/ci-cd/versioning-release.md` §Why each half matters fecha o argumento pelo
outro lado: os artefatos 4–6 do lockstep são o *installed-copy trigger*, e um quarto arquivo shipped
viraria um sétimo membro, com version-match próprio em cada repo alvo.

O standard é três dias mais novo que este spec. Não há conflito a resolver: **o remédio que a
anotação mandava aplicar foi proibido depois que ela foi escrita.**

### Decisão 2 — o alvo nomeado não é uma folha, então a extração não pagaria nem se fosse permitida

`render_plans_zone` e `cmd_plans` referenciam catorze nomes de nível de módulo: `PLANS_EMPTY`,
`GEN_BEGIN`, `GEN_END`, `STAGE_ORDER`, `read_text`, `write_text`, `spec_files`, `parse_frontmatter`,
`parse_sections`, `body_after_frontmatter`, `parse_tasks`, `derive_stage`, `titleize` e `emit`.

Um módulo com aquelas 66 linhas importaria de volta o núcleo que ele deveria aliviar, e a costura
passaria exatamente por `derive_stage` — a computação mais load-bearing do front, como o spec irmão
`dedupe-specs-py-spec-reader` mede em detalhe. Extração aqui **inverte a dependência** e reduz zero
do que um revisor precisa ter na cabeça.

A regra durável que sai daí, e é ela que o standard vai escrever: **em um tool de arquivo único, a
única extração que paga é a de uma folha, e um subcomando que consome o parser central nunca é
folha.**

### Decisão 3 — o que substitui um limite de linhas

O risco original queria evitar "growing one file past reviewability". Recusada a extração, a
obrigação continua de pé e precisa de outra forma. A forma escolhida é **navegabilidade declarada e
verificada.**

`specs.py` já é dividido por dez banners de região (`# ---` … título … `# ---`): embedded assets ·
minimal frontmatter parser · helpers · workspace resolution and spec discovery · the single-file
parser · output · commands · migrate · validate / doctor / plans reindex · dispatch. Mas o docstring
de 83 linhas descreve o **modelo** (uma spec é um arquivo, os estágios derivados, o contrato de
saída) e não diz uma palavra sobre onde as coisas ficam. Um mapa dessas dez regiões, **por nome e sem
números de linha**, é a coisa mais barata que quita a dívida de reviewability.

Sem números de linha por decisão: um mapa com linhas envelhece no primeiro commit e vira ruído com
aparência de contrato. Por nome, ele só envelhece quando uma região **nasce ou morre** — e é
exatamente isso que a assertion nova de `selftest` pega, nas duas direções.

A assertion é de **membresia**, não de texto, e isso é deliberado:
`docs/standards/code/canonical-set-parsing.md` já registra que um lockstep byte a byte prova que as
cópias concordam mas nunca que o código que as lê ainda quer dizer o mesmo, então um invariante de
membresia é devido à sua própria assertion. Ela também é self-contained (lê o próprio `__doc__` e o
próprio arquivo), então roda numa cópia instalada — que é justamente onde uma divergência passaria
desapercebida, pelo mesmo raciocínio que `cmd_selftest` já aplica às canonical frontmatter cases.

### Decisão 4 — onde o standard mora

`docs/standards/code/`, não `docs/standards/architecture/`.

`architecture/plugin-layout.md` responde *onde um executável fica* ("by how it is invoked, not by
whether it ships") e não *de quantos arquivos um tool pode ser*; e o `resource:` de uma regra de
estrutura de tool é o mesmo trio de caminhos que `code/frontmatter-parsing.md` já declara. A
alternativa de estender `plugin-layout.md` com uma seção foi pesada e perdeu: aquele doc já carrega
quatro linhas na tabela de subtrees e a própria seção §"Four rows is one past what the warning above
tolerates" avisa contra somar mais. Um standard por arquivo é a regra declarada em
`docs/standards/code/index.md`, e `code/` tem hoje dois standards, os dois com `resource:` nos três
tools shipped — o novo é o terceiro vizinho de prateleira, não um intruso.

### Contratos que este design não pode contrariar

- `docs/standards/code/frontmatter-parsing.md` — sem módulo irmão importável (Decisão 1).
- `docs/standards/ci-cd/versioning-release.md` — o bump é ato do conclude, nunca task de spec.
- `docs/standards/quality/selftest-mutation.md` — a assertion nova só conta como verificação depois
  de ter sido vista falhar uma vez, com a mutação revertida.
- `docs/standards/code/canonical-set-parsing.md` — um invariante de membresia é devido à sua própria
  assertion; é por isso que a checagem do mapa compara conjuntos e não texto.
- `docs/standards/architecture/plugin-layout.md` — `assets/bin/` é "tool the plugin executes"; nada
  aqui move arquivo de subtree.
- o docstring de `specs.py` §ASSETS — "EDIT BOTH OR NEITHER" continua valendo, e este spec não toca
  `DEFAULT_SCHEMA` nem `TEMPLATE_SPEC`.

## Alternatives Considered

As cinco formas que a resposta a esta anotação poderia tomar, com o motivo de cada derrota. A tabela
inclui as três que quase sempre existem e quase nunca são escritas: **não fazer nada**, **a menor
coisa que funcionaria** e **comprar em vez de construir**.

| Forma | Custo | O que compra | O que fecha | Veredito |
| --- | --- | --- | --- | --- |
| **A. Extrair `cmd_plans` / `render_plans_zone` para um módulo irmão** — o remédio literal da anotação | proibido nominalmente por `docs/standards/code/frontmatter-parsing.md`; sétimo artefato de lockstep; um segundo arquivo instalado em cada repo alvo, com version-match próprio | −66 linhas, ou 2,1% do arquivo | o contrato de instalação standalone, que é o que faz uma cópia em `.claude/hooks/` funcionar sem nada ao lado | **rejeitada** — é o único remédio da tabela que um standard `authority: current` proíbe pelo nome, e Decisão 2 mostra que ele importaria de volta o núcleo que deveria aliviar |
| **B. Build de amalgamação** — fontes pequenas concatenadas em um `specs.py` gerado | um build step em um repositório cujo CLAUDE.md declara não ter nenhum; revisar diff de arquivo gerado; `selftest` passaria a rodar contra o artefato e não contra as fontes | fontes revisáveis **e** um único arquivo shipped, o que é genuinamente as duas coisas | "sem build step", que hoje é uma propriedade do repositório e não um acidente | **rejeitada** — troca um arquivo longo que qualquer pessoa abre e lê por uma toolchain que ninguém aqui mantém, e move a verificação para longe do que é distribuído |
| **C. Separar `migrate` como um segundo *entry point*** — não como import, então sem violar Decisão 1 | duplica os helpers de núcleo que `migrate` usa (`read_text`, `write_text`, `parse_frontmatter`, `capture_form`, `canonical_headings`, `spec_files`, `_git`) para mover 283 linhas; sétimo artefato de lockstep; muda a surface documentada em `specs-develop/spec-driven.md` §The `specs.py` tool surface e em todo comando que a cita | −283 linhas do arquivo principal, e `migrate` é de fato o subsistema mais autocontido que existe ali | nada estruturalmente — é a alternativa mais forte da tabela | **rejeitada** — soma mais duplicação do que remove linhas, e é o mesmo "distribution problem" do standard com outro nome. Vale registrar que ela é legal, ao contrário de A |
| **D. Não fazer nada** — concluir o spec como `abandoned`, com o motivo no `## Outcome` | uma linha | fecha a anotação pelo custo mínimo, e o custo mínimo é um argumento real | a chance de escrever a regra onde o próximo leitor tropeça nela | **rejeitada, e é o fallback declarado em `## Open Decisions`** — repetiria o defeito de origem: a regra do limite morreu porque foi registrada na seção Risks de um plano que hoje só existe em `git show`, e "decidimos não splitar" no `## Outcome` de um spec arquivado é o mesmo erro na mesma pasta |
| **E. Retirar o limite e escrever o contrato que vale no lugar dele** — a escolhida, e também a "menor coisa que funcionaria" desta lista | um doc curto em `docs/standards/code/`, um mapa de regiões no docstring, uma assertion de `selftest` | uma resposta escrita e mecanicamente verificada, no lugar onde ela é lida; e mata a métrica que hoje desencaminha três specs vivos | argumentos futuros por contagem de linhas, que é exatamente o que se quer fechar | **escolhida** |

**Comprar ou emprestar em vez de construir** não tem linha própria porque não existe nada para
comprar. A decisão é sobre a estrutura interna de um script stdlib de um repositório, e nenhuma
dependência externa é sequer admissível: o contrato zero-dependency é anterior a esta discussão e não
está em jogo aqui. Registrado para que ninguém precise procurar de novo.

Uma nota sobre A e C, que é o que separa as duas: **C é permitida e perde por aritmética; A é
proibida e perderia por aritmética também.** Quem voltar a este assunto deve atacar C, não A.

## Open Decisions

- **O standard vale o próprio custo, ou basta arquivar este spec como abandonado?** Este spec
  recomenda a forma E e carrega a forma D como fallback explícito em `## Alternatives Considered`.
  **Como se decide:** é a palavra do humano no momento da aprovação, e não há evidência a coletar que
  decida por ele — a pergunta é se o repositório quer pagar um doc permanente para não rederivar esta
  análise. A evidência que existe está dividida, e vale registrada honestamente: nenhum dos dois
  specs irmãos que mexem no tamanho de `specs.py` (`dedupe-specs-py-spec-reader`,
  `add-specs-py-record-writer`) pergunta se pode splitar, o que é sinal fraco de que a regra não é
  urgente; já `name-the-scaffolded-stage` mostra uma mudança que exige mover três cópias
  sincronizadas dentro do mesmo arquivo, o que é sinal de que o custo do self-containment é real e
  merece estar escrito. Se a resposta for D, as seções 2 e 4 de `## Tasks` caem inteiras e o spec
  fecha com um `## Outcome` que registra por que o limite está morto.
- **A assertion `sp-region-map-drift` entra, ou o mapa fica sendo um comentário sem contrato?**
  Recomendação: entra, porque é ela que faz o standard nascer `authority: current` em vez de
  `background` — sem ela, o mapa é uma afirmação que o repositório não checa, e o próprio
  `cmd_selftest` de `specs.py` já registra que "a duplicate nobody checks is just a bug with a delay
  on it". **Como se decide:** pelo custo real da assertion quando ela for escrita — se ela não couber
  em algo próximo do tamanho do bloco `sp-schema-drift` que já existe ali, ela não vale o preço e o
  doc desce para `authority: background`. É uma decisão que se fecha durante a task 2.2, com o
  código na mão, não antes.
- **O mapa de regiões entra também em `skills.py` e `okf-validate.py`, ou fica como deferral?**
  Recomendação: deferral declarado no ledger do próprio standard, com o gatilho escrito.
  **Como se decide:** por evento, não por data — a primeira vez que alguém precisar navegar
  `skills.py` (1.802 linhas) e não achar o que procura. É o mesmo formato de ledger que
  `docs/standards/code/index.md` já usa para os sub-standards diferidos, então não há mecanismo novo
  a inventar.

## Risks

As histórias vieram de um premortem sobre o conteúdo deste spec — "é três meses depois, isto foi
construído e deu errado" — e cada uma converteu em um risco com mitigação nomeada, um risco aceito ou
um corte de escopo. As que não converteram em nada foram descartadas e não estão aqui.

- **O mapa de regiões envelhece e passa a mentir.** É a falha mais provável, porque um comentário que
  descreve estrutura é exatamente o que ninguém atualiza. *Mitigação:* a assertion
  `sp-region-map-drift` em `specs.py selftest`, verificando membresia nas **duas** direções (banner
  sem entrada no mapa, entrada no mapa sem banner), e o mapa sem números de linha, para que só
  nascimento e morte de região o invalidem.
- **A assertion nova nunca é vista falhar e vira teste morto.** *Mitigação:* a passada de mutação é
  task própria (2.3) e item explícito de `## Validation`, como
  `docs/standards/quality/selftest-mutation.md` exige — remover uma entrada do mapa, ver o finding
  disparar, reverter.
- **O standard é escrito e o código não é, então o doc afirma `authority: current` sobre uma regra
  que nada provou.** *Mitigação:* a ordem das tasks é a mitigação — a seção 2 (mapa e assertion) vem
  **antes** da seção 4 (o standard), então o doc só é escrito depois de a regra ter sido provada uma
  vez neste repositório.
- **O standard é lido como "nunca divida arquivo nenhum" e alguém recusa uma extração de folha
  legítima em algum tool futuro.** *Mitigação:* a regra da Decisão 2 entra no standard como
  **permissão** e não só como proibição — a extração de uma folha paga; a de um consumidor do parser
  central, não.
- **Editar o docstring de `specs.py` mexe num gatilho de lockstep sem ninguém notar.** O artefato 5
  do lockstep de seis é o `VERSION` de `specs.py`, e é ele que decide se `/specs:align` sobrescreve a
  cópia instalada num repo alvo; um docstring novo sem bump nunca chega a repo nenhum.
  *Mitigação:* nenhuma task de bump, porque `docs/standards/ci-cd/versioning-release.md` proíbe — mas
  `## Handoff` registra a obrigação para o `/specs:conclude` que fechar este branch.
- **O spec é lido como um mandato de split e o executor extrai o módulo "de brinde".** *Mitigação:*
  `## Proposal` e `## Out of Scope` dizem o contrário nas primeiras linhas de cada um, e o standard
  escrito é o artefato durável que sobrevive ao arquivamento do spec.
- **Colisão de merge com `dedupe-specs-py-spec-reader`.** Aquele spec nomeia `cmd_plans` como um dos
  call sites que vai reescrever para usar uma leitora compartilhada. Este spec **não toca**
  `cmd_plans`, então a colisão é de merge no mesmo arquivo, não de contrato — e os dois pedaços do
  arquivo são distintos (docstring e `cmd_selftest` aqui; corpos de varredura lá). *Mitigação:* a
  fronteira está declarada em `## Out of Scope`; quem executar em segundo rebaseia e não reabre a
  decisão do outro. Nenhum dos dois specs pode presumir o resultado do outro.
- **Colisão de premissa com `add-specs-py-record-writer`.** Aquele spec adiciona um subcomando
  `record`, o que cresce o arquivo e, sob a regra antiga, precisaria pedir licença. *Mitigação:*
  retirar o limite é justamente o que remove a objeção; o standard é escrito sem orçamento de linhas
  nenhum, de propósito, e `## Out of Scope` diz isso com o slug do irmão.
- **`revise-standards-subject-folders` mexe no conjunto fixo de subpastas de `docs/standards/` e o
  caminho do doc novo muda debaixo dele.** *Mitigação:* o risco é baixo — aquele spec ataca `mlops`,
  uma pasta específica demais, e `code/` é uma das de aplicação geral — e a migração de caminho é
  mecânica por `/docs:align`, que mantém as listings em sincronia. Nomeado aqui para que a colisão
  não seja descoberta no merge.
- **ACCEPTED — o repositório ganha um standard permanente a mais para manter.** É custo recorrente e
  reconhecido: um doc em `docs/standards/code/` que precisa continuar verdadeiro, um mapa no docstring
  e uma assertion. Aceito por três motivos medidos: a alternativa D já falhou uma vez exatamente por
  não ter escrito a regra em lugar algum; o mecanismo tem histórico neste repositório, já que
  `frontmatter-parsing.md` é citado de dentro do próprio código (`specs.py:498-501`) e por
  `versioning-release.md`; e desfazer é barato, porque nada de comportamento muda — apagar um doc,
  reverter um docstring e uma assertion, sem nenhum consumidor a jusante.
- **ACCEPTED — a assertion `sp-region-map-drift` não decorre diretamente de `## Problem`.** A crítica
  é justa: `## Problem` fala de tamanho de arquivo, e uma checagem de membresia entre docstring e
  banners está dois passos adiante. Aceito porque é ela que separa um contrato de um comentário, e
  porque é cortável de forma isolada — as tasks 2.2 e 2.3 caem sem tocar 2.1 nem a seção 4, ao preço
  de o doc nascer `authority: background`. A decisão está aberta e registrada em `## Open Decisions`.
- **ACCEPTED — o benefício é recorrente mas raro.** A pergunta "posso dividir este tool?" apareceu
  uma vez em cinco dias. Aceito com uma restrição de tamanho no próprio standard: a regra são poucas
  frases mais a regra da folha, e o doc não deve virar ensaio — um standard curto tem manutenção
  próxima de zero, e é isso que torna o custo recorrente aceitável.

## Tasks

### 1. Confirmar a medição e localizar a regra morta

- [ ] 1.1 Remedir `specs.py` e confrontar a tabela de medição de `## Design`, corrigindo-a se divergir
      Qualquer divergência entra como discovery e a tabela é corrigida antes de qualquer outra task.
      files: specs/plans/2026-07-25-split-specs-py-backlog-renderer.md
      verify: wc -l plugins/quenching/assets/bin/specs.py && python3 plugins/quenching/assets/bin/specs.py --version
- [ ] 1.2 Listar toda citação sobrevivente do limite de ~1.200 linhas e classificar cada uma
      Duas classes: registro histórico (o `## Problem` e o `## Design` deste spec) ou obrigação
      pendente. Só a segunda classe é trabalho; a primeira fica como está.
      verify: grep -rn '1,200' docs/ plugins/ specs/plans/ || true

### 2. O mapa de regiões e a assertion que o sustenta

- [ ] 2.1 Acrescentar ao docstring de `specs.py` o mapa das dez regiões banner, por nome e sem linhas
      Na ordem em que aparecem no arquivo. Sem números de linha, por decisão: um mapa com linhas
      envelhece no primeiro commit.
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py selftest && python3 plugins/quenching/assets/bin/specs.py --version
- [ ] 2.2 Acrescentar a `cmd_selftest` a assertion `sp-region-map-drift`, por membresia nas duas direções
      Compara o conjunto de banners do próprio arquivo com o conjunto de entradas do mapa: banner sem
      entrada e entrada sem banner são os dois findings. Roda antes do early return, como as canonical
      frontmatter cases, para valer também em cópia instalada sem assets adjacentes.
      files: plugins/quenching/assets/bin/specs.py
      pattern: plugins/quenching/assets/bin/specs.py (o bloco que emite `sp-schema-drift` em `cmd_selftest`)
      verify: python3 plugins/quenching/assets/bin/specs.py selftest --json
- [ ] 2.3 Rodar a passada de mutação da assertion nova nas duas direções e registrar o resultado
      Remover uma entrada do mapa e ver o finding disparar; remover um banner e ver disparar do outro
      lado; reverter as duas. O commit registra qual assertion falhou em cada caso, como
      `docs/standards/quality/selftest-mutation.md` pede.
      verify: python3 plugins/quenching/assets/bin/specs.py selftest

### 3. Provar que nenhum comportamento mudou

- [ ] 3.1 Confirmar que `plans reindex` reproduz a zona byte a byte e que o surface está intacto
      Contra os baselines de `## Validation`: diff vazio em `specs/plans/index.md`, 26 commands e zero
      findings no doctor.
      verify: python3 plugins/quenching/assets/bin/specs.py plans reindex && git diff --stat specs/plans/index.md && python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json && python3 plugins/quenching/assets/bin/specs.py validate --json

### 4. O standard, escrito depois de a regra ter sido provada

- [ ] 4.1 Escrever `docs/standards/code/single-file-tool-structure.md` por `/docs:add`
      `resource:` nos três tools shipped, `authority: current`. Conteúdo: sem extração para irmão
      importável, sem orçamento de linhas, navegabilidade declarada como a obrigação que substitui as
      duas, e a regra da folha da Decisão 2 escrita como permissão além de proibição. Curto — a regra
      e a regra da folha, não um ensaio.
      files: docs/standards/code/single-file-tool-structure.md, docs/standards/code/index.md, docs/standards/index.md
      pattern: docs/standards/code/frontmatter-parsing.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs --json
- [ ] 4.2 Registrar no ledger do standard novo o deferral de `skills.py` e `okf-validate.py`
      Quanto ao mapa de regiões, com o gatilho de revisita por evento e não por data — a primeira vez
      que alguém precisar navegar `skills.py` e não achar o que procura.
      files: docs/standards/code/single-file-tool-structure.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs --json
- [ ] 4.3 Acrescentar em `docs/standards/code/frontmatter-parsing.md` um cross-reference ao doc novo
      Na seção §Why there are three copies and not one module, que é onde alguém com esta pergunta
      chega primeiro. Só a referência; a regra daquele doc não é revisada.
      files: docs/standards/code/frontmatter-parsing.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs --json

### 5. Fechamento

- [ ] 5.1 Revalidar a bundle e o front de specs contra os baselines, e conferir o lockstep
      `0 error(s)` e nenhum warning novo no caminho do doc novo — nunca a contagem total, que é
      advisory e varia sozinha. `VERSION` e `specs.py --version` num único valor.
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs && python3 plugins/quenching/assets/bin/specs.py validate --json && cat plugins/quenching/VERSION && python3 plugins/quenching/assets/bin/specs.py --version
