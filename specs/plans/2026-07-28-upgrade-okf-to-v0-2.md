---
slug: upgrade-okf-to-v0-2
title: Upgrade the OKF contract to v0.2 or later
verification: per-section
priority: {level: 27, criticality: medium, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# Upgrade the OKF contract to v0.2 or later

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

O `docs/` deste repo, e o de todo repositório que o plugin alinha, é um bundle de um formato
externo: **OKF**, o Open Knowledge Format. O plugin declara qual versão do formato ele obedece — o
campo `okf_version` no `docs/index.md` — e uma cópia condensada das regras dessa versão vive dentro
do plugin, em `okf-spec.md`, de onde o validador e os comandos `/docs:*` foram derivados. Hoje esse
número é `0.1`.

O `## Problem` mostra duas coisas: o upstream publicou uma **v0.2**, com duas quebras nomeadas; e
este repo não tem nenhuma cópia dela, então ninguém aqui pode dizer o que a subida implica. É essa
segunda metade que dá a forma ao `## Proposal` — a primeira entrega é a **transcrição de v0.2 mais
uma tabela de delta com um veredicto por mudança**, e só depois vem adoção. `## Alternatives
Considered` registra as formas rejeitadas, incluindo a de subir só o número, e registra que ficar em
v0.1 de propósito é saída legítima deste spec, não fracasso dele.

`## Design` é onde a subida encontra o código real. A parte que mais decide não é o número: é que o
parser de frontmatter do validador lê **só escalares de nível superior**, enquanto os campos novos
de v0.2 são todos aninhados. `## Design` mostra as duas formas de errar isso — uma é avisada, a
outra é silenciosa — e mede, arquivo por arquivo, onde o `0.1` está fixado hoje.

`## Risks` continua essa história pelo lado do que dá errado: a checagem de desatualização morrendo
sem avisar, o stamp subindo à frente da fiscalização, um bundle alvo já alinhado quebrando no
upgrade. Cada uma tem mitigação ou está aceita com o motivo. É também onde os specs vizinhos que
tocam os mesmos arquivos são nomeados, com a fronteira que este mantém — sem decidir por nenhum
deles.

`## Out of Scope` afasta o que se confunde com isto, e o item que mais confunde é o lockstep de
versão do **plugin**: seis artefatos, outro número, outro momento. `## Open Decisions` guarda as seis
perguntas que este spec não fecha — em especial se o parser será estendido e se o stamp sobe agora —,
cada uma com o que a destrava. `## Validation` e `## Tasks` são a parte executável, e a ordem entre
as tasks é ela mesma uma mitigação: fiscalizar antes de estampar.
## Problem

O contrato de bundle que este repo entrega e fiscaliza é OKF v0.1 — a versão estampada em
`docs/index.md`, condensada em `assets/references/docs-align/okf-spec.md` e comparada por
`okf-validate.py`. O upstream andou: **existe uma v0.2 publicada**, e este plugin não a adotou.

**Isso foi verificado, não suposto.** Em 2026-07-30 uma leitura de
`https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/SPEC.md`
devolveu *"This document specifies OKF version 0.2"* e um §13 *"Changes from v0.1"* com **duas
quebras nomeadas** — `timestamp` substituído por `generated: {by, at}`, e a lista de corpo
`# Citations` substituída pelo campo de frontmatter `sources` — mais famílias aditivas
(`sources` com sinais de credibilidade e `usage_window`, `generated`/`verified`, o ciclo de vida
`status`/`stale_after`, o tipo `Attested Computation` e o heading `# Computation`, e a convenção
de actor). O §12 mantém o mecanismo de declaração: `okf_version: "0.2"` no `index.md` da raiz do
bundle, o único `index.md` que aceita frontmatter.

**O defeito, porém, não é só a versão estar velha — é que o delta não está escrito em lugar
nenhum deste repo.** A única declaração local do contrato é `okf-spec.md`, que condensa v0.1. Sem
uma transcrição de v0.2 aqui dentro, nenhuma decisão de adoção é decidível: não há como dizer
quais checks do `okf-validate.py` mudam, o que o `/docs:align` passa a estampar, nem o que um
bundle já alinhado precisa migrar. Qualquer lista de tarefas escrita antes disso seria inventada.

**Por que agora, dado que nada ramifica sobre o valor.** Mecanicamente, a espera custa pouco:
`okf-validate.py:748` lê `okf_version` para exatamente um fim — comparar com o literal `"0.1"` e
emitir WARN `root-okf-version-mismatch`. Nenhum check, comando ou template ramifica sobre o valor.
O custo real é outro e é acumulativo: a promessa central do plugin — *seu bundle é OKF portável* —
descola do que OKF passou a dizer, e cada bundle novo alinhado em v0.1 acumula um `timestamp:` a
mais para migrar depois. Só o bundle deste repo já carrega **25** docs com `timestamp:`.

## Proposal

O spec entrega o **delta primeiro** e só depois adota o que o delta justificar. Ao final:

- `assets/references/docs-align/okf-spec.md` deixa de condensar v0.1 e passa a condensar **v0.2**,
  com a procedência registrada no próprio arquivo: a URL upstream, a data da leitura e a versão que
  o documento declara.
- O mesmo arquivo carrega uma **tabela de delta v0.1 para v0.2**, com uma linha por item do §13 do
  upstream e, em cada linha, um dos três veredictos: **adotado**, **inaplicável** (com o motivo) ou
  **diferido** (com o que o destrava). Nenhum item do §13 fica sem veredicto — é isso que um
  revisor confere.
- A quebra `timestamp` para `generated: {by, at}` está implementada como **leitura dupla**:
  `okf-validate.py` lê `generated.at` e cai de volta em `timestamp:` quando o primeiro está
  ausente. Nenhum código novo nasce em ERROR.
- Um doc que carrega `generated:` e não carrega `timestamp:` **nunca volta com zero findings** —
  ou o campo é lido, ou o misread é nomeado. É o que impede o `stale-doc` de morrer calado.
- A regra de migração para um bundle já alinhado em v0.1 existe por escrito em
  `docs-align/migration.md` §5, ao lado dos renomes de campo que já vivem lá.
- O stamp `okf_version` só passa a `"0.2"` quando todo MUST de v0.2 estiver satisfeito e a leitura
  dupla estiver no lugar. Se não estiver, o stamp **fica em `"0.1"` de propósito** e o pin fica
  registrado como decisão, não como esquecimento.
- Existe um standard que diz como este plugin acompanha uma versão de contrato externo — e que
  **versão de contrato não é versão de plugin** —, para que a próxima subida não redescubra a lista
  de arquivos a mover.

**O spec tem um gate próprio e ele pode fechá-lo.** Se a tabela de delta sair com todos os itens
`inaplicável`, o resultado honesto é um pin registrado em v0.1, não uma subida — e isso conta como
o spec ter sido concluído, não como ele ter falhado.

## Out of Scope

- **O lockstep de versão do plugin.** `docs/standards/ci-cd/versioning-release.md` nomeia seis
  artefatos mais o sétimo (`session.py`); `okf_version` **não é nenhum deles**. Uma subida de
  contrato não é um release, e o bump dos seis continua acontecendo uma vez, no passo 5 do
  `/specs:conclude`, imediatamente antes do merge — nunca como task deste spec.
- **O tipo `Attested Computation` e o heading de corpo `# Computation`.** São aditivos de v0.2 para
  bundles que descrevem computação atestada; este plugin fixa um vocabulário descritivo por home
  (`okf-spec.md` §Concept `type`) e nenhuma das homes entregues tem esse conceito. Entra na tabela
  de delta como `inaplicável`, com o motivo, e não vira superfície.
- **O formato do payload `--json` do validador.** É de `expose-finding-advisory-as-data`, e o
  próprio sibling já registra que o contrato externo não governa esse payload. v0.2 não muda isso.
- **O redesenho do gatilho do `stale-doc`.** É de
  `narrow-the-stale-doc-trigger-to-content-drift`. Este spec só garante que o `stale-doc` continue
  conseguindo **ler uma data**; qual sinal ele deve medir é do sibling.
- **Desreservar `log.md`.** v0.2 mantém `index.md` e `log.md` reservados, então o perfil
  OKF-strict que *aposenta* o `log.md` (`okf-spec.md` §4) atravessa a subida intacto.
  `docs/standards/architecture/retiring-a-reserved-artifact.md` já governa a diferença entre
  aposentar e desreservar, e nada aqui a reabre.
- **Migrar bundles de terceiros automaticamente.** A regra de migração é escrita; aplicá-la num
  repo alvo continua sendo o `/docs:align` propondo e um humano confirmando, com rename acoplado a
  código confirmando por conta própria (`docs-align/migration.md` §4).
- **Trocar `authority:` pelo `status:` de v0.2, ou lastrear `authority` no `verified:` de v0.2.**
  São reaproveitamentos plausíveis das famílias aditivas, e nenhum é necessário para estar
  conformante com v0.2. Ficam em `## Open Decisions`, não em `## Tasks`.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/architecture/okf-contract-version.md` — como este plugin acompanha uma versão de
  contrato externo: que versão de contrato não é versão de plugin, que uma quebra de campo upstream
  é adotada como leitura dupla e nunca como check novo em ERROR, que o stamp move por último, e a
  tabela medida de artefatos que pinam a versão. Nova, `type: standard`, `authority: current` quando
  a subida a provar.
- `docs/standards/code/frontmatter-parsing.md` — existente. A tabela §The subset each parser claims
  to read é reconciliada com o que a decisão de parser produzir: a linha do `okf-validate.py` muda,
  ou o doc registra que o subset atravessou a subida inalterado. Nos dois casos a lista canônica de
  casos volta a valer nos três `selftest`.

### Standards at `authority: background` this spec may resolve

- none — os quatro standards em `authority: background` hoje
  (`automation/session-evidence.md`, `automation/context-budget.md`, `automation/agents.md`,
  `quality/selftest-mutation.md`) tratam de evidência de sessão, budget de contexto, subagentes e
  mutação de selftest. Nenhum deles é provado nem refutado por uma subida de versão do contrato OKF,
  então não há promoção que este spec possa fazer honestamente.

### Product code this spec expects to touch

- `plugins/quenching/assets/references/docs-align/okf-spec.md` — a transcrição inteira e a tabela de
  delta; é o artefato central do spec.
- `plugins/quenching/assets/hooks/okf-validate.py` — a leitura dupla em `check_concept` e
  `check_stale_doc`, o fixture do `selftest`, o literal de versão e o docstring do conformance core.
- `plugins/quenching/assets/references/docs-align/migration.md` — a regra de migração de campo no §5.
- `plugins/quenching/assets/references/docs-align/conformance.md` e `taxonomy.md` — o texto do código
  `root-okf-version-mismatch` e o diagrama da árvore.
- `plugins/quenching/commands/docs/align.md` — o passo que escreve o stamp no alvo.
- `plugins/quenching/assets/docs/index.md`, `plugins/quenching/assets/templates/index.md.tmpl`,
  `plugins/quenching/assets/checks/functional-checks.sh` — o skeleton entregue, o mold e o bundle
  sintético da checagem 4.
- `docs/index.md` e os 25 docs de `docs/**` deste bundle que carregam `timestamp:`, mais
  `plugins/quenching/assets/docs/knowledge/glossary.md` no skeleton.
- `docs/QUENCHING.md`, `plugins/quenching/assets/docs/QUENCHING.md` — os manuais de operador.
- `README.md`, `plugins/quenching/README.md`, `plugins/quenching/assets/README.md`,
  `plugins/quenching/assets/hooks/README.md`, `.claude-plugin/marketplace.json` — apenas o número na
  prosa de produto.

**Nenhum campo de versão do lockstep do plugin é tocado, e isso é deliberado.** Um arquivo da lista
acima é membro dos seis — `.claude-plugin/marketplace.json` —, mas o que muda nele é o texto da
`description` que diz "OKF v0.1", nunca o campo `version` da entrada do plugin. Os outros cinco
(`VERSION`, `plugin.json`, e os constantes `VERSION` de `specs.py`, `skills.py`, `okf-validate.py`)
não aparecem por causa do número de contrato; o `okf-validate.py` está na lista por causa do código,
e seu `VERSION` continua sendo movido só no passo 5 do `/specs:conclude`. Ver `## Out of Scope`.

## Validation

A política declarada é `verification: per-section` — cada grupo de `## Tasks` termina num estado
verificável, e é o que impede a 3.2 de estampar antes de a 2.3 provar a leitura. `per-task` rodaria a
bateria inteira quatorze vezes sem ganho; `end-of-plan` deixaria o stamp pousar antes da prova, que é
exatamente a história de premortem que a ordem existe para evitar.

### A bateria do repo — precisa continuar limpa

```bash
cd plugins/quenching
python3 assets/hooks/okf-validate.py selftest
python3 assets/bin/specs.py selftest
python3 assets/bin/skills.py selftest
python3 assets/hooks/okf-validate.py assets/docs                       # 0 error(s), 0 warning(s)
python3 assets/hooks/okf-validate.py assets/specs/plans --listing-root  # 0 error(s), 0 warning(s)
python3 assets/bin/skills.py --root . doctor --json                    # 26 commands, no findings
python3 assets/bin/skills.py --root . lint --json                      # exit 0
```

Os três `selftest` são o gate do lockstep de parsing: `docs/standards/code/frontmatter-parsing.md`
declara a lista canônica de casos como unidade compartilhada, então uma mudança no subset do
`okf-validate.py` que não passe nos três é a divergência que a task 5.2 existe para fechar.

### A asserção que só este spec tem: o misread não pode ser silencioso

É a verificação central, porque a falha que ela pega não produz sintoma nenhum.

```bash
mkdir -p /tmp/okf-v02-probe
printf '%s\n' '---' 'type: standard' 'title: t' 'description: d' \
  'resource: index.md' 'generated: {by: quenching, at: 2026-07-30}' '---' '' '# t' \
  > /tmp/okf-v02-probe/x.md
printf '%s\n' '# Bundle' '' '- [t](x.md)' > /tmp/okf-v02-probe/index.md
python3 plugins/quenching/assets/hooks/okf-validate.py /tmp/okf-v02-probe --json
```

A asserção é sobre **quais códigos** aparecem para `x.md`, não sobre a contagem — outros findings do
bundle sintético tornariam uma contagem indiscriminada. O conjunto de códigos precisa conter **ao
menos um** entre: o código de campo de data que a subida definir (hoje é `missing-timestamp`, que já
dispara porque `timestamp` está em `RECOMMENDED`, `okf-validate.py:145`), ou
`okf-frontmatter-unparsed` nomeando o misread do registro inline. Um doc cuja única declaração de
data é um `generated:` que o parser não sabe ler **não pode sair calado sobre isso** —
`docs/standards/quality/parse-honesty.md` é o contrato que a mudez violaria.

**A parte que realmente é silenciosa é o `stale-doc`, e ela precisa da segunda metade da asserção.**
Nenhum código é emitido quando `check_stale_doc` recebe `{by: quenc` como data, falha o teste de ISO
e volta vazio (`okf-validate.py:588-592`) — a ausência de `stale-doc` é indistinguível de um doc
fresco. Por isso a medida é no bundle deste próprio repo, depois da migração da task 4.1:

```bash
python3 plugins/quenching/assets/hooks/okf-validate.py docs --json
```

A contagem de `stale-doc` **não pode cair a zero** por efeito da migração. Ela pode mudar de valor,
mas cair a zero de uma vez é o sintoma de que o gatilho parou de ler a data, não de que os docs
ficaram frescos. A contagem de referência é a de hoje, registrada antes da 4.1 rodar.

### A tabela de delta tem cobertura total

Uma checagem de leitura, declarada porque não há como automatizá-la contra um documento externo: cada
item do §13 do `okf/SPEC.md` upstream tem **exatamente uma** linha na tabela de delta do
`okf-spec.md`, e cada linha carrega um dos três veredictos (`adotado`, `inaplicável`, `diferido`).
Um item do §13 sem linha, ou uma linha sem veredicto, é falha. A procedência gravada pela task 1.1
(URL, data, versão declarada) é o que torna essa conferência refazível.

### O lockstep de versão do plugin não se moveu por causa disto

```bash
cd plugins/quenching
cat VERSION
python3 assets/bin/specs.py --version
python3 assets/bin/skills.py --version
python3 assets/hooks/okf-validate.py --version
python3 assets/bin/session.py --version
```

Os cinco valores concordam entre si **e continuam iguais ao da base do branch**. Que eles subam é
obrigação do passo 5 do `/specs:conclude`, imediatamente antes do merge — nunca deste spec, e nunca
consequência do número de contrato ter mudado.

### O que continua verdade depois

- `okf-spec.md` linha 92: a listagem raiz continua pinada a `okf_version` e nada mais.
- `okf-spec.md` linha 111: a declaração de body language continua **autocontida**, sem deferir para
  um doc local deste repo.
- `RESERVED` continua com `index.md` e `log.md`; nenhum check de `log.md` reaparece
  (`docs/standards/architecture/retiring-a-reserved-artifact.md`).
- Nenhum código de finding novo nasce em ERROR
  (`docs/standards/quality/bundle-verification.md`).

### Fora da bateria, de propósito

`./assets/checks/functional-checks.sh` não entra: `CLAUDE.md` e
`docs/standards/quality/surface-verification.md` reservam o harness ao front `/skill`, e nada aqui
mexe em corpo de comando novo. A task 3.2 toca `functional-checks.sh:131` apenas porque aquele bundle
sintético carrega o stamp — rodar o harness por causa disso seria pagar sessão de agente por uma
linha de `printf`.

## Design

### A forma escolhida: transcrição primeiro, adoção depois

Quatro formas foram comparadas antes de qualquer linha ser escrita.

| Forma | Custo | O que compra | O que fecha |
| --- | --- | --- | --- |
| **A. Transcrição primeiro, adoção gated** (escolhida) | duas etapas em vez de uma; o spec fica aberto mais tempo | cada decisão de adoção passa a ser decidível, porque o delta existe por escrito antes dela | nada — a forma B continua alcançável a partir daqui |
| **B. Adoção completa numa passada** | não dimensionável hoje: uma quebra de campo em 25 docs locais mais todo bundle alvo já alinhado | acaba de uma vez | dimensionar honestamente; a lista de tasks seria inventada |
| **C. Só o stamp** — subir `okf_version` e o literal de `okf-validate.py:748` | uma linha | silencia o `root-okf-version-mismatch` | a honestidade: o bundle passa a alegar uma versão cujas regras ele não fiscaliza |
| **D. Ficar em v0.1 de propósito** e registrar o pin | um standard | encerra a pergunta | a portabilidade que o plugin promete, se o delta tiver algo adotável |

A forma A ganha por um motivo verificável, não estético: **hoje o repo não contém nenhuma
declaração de v0.2**. A única declaração local do contrato é `okf-spec.md`, que condensa v0.1, e o
upstream não está vendorizado. A forma A também **contém** a forma D: se a tabela de delta sair
toda `inaplicável`, o spec termina com o pin registrado.

### A restrição que decide quase tudo: o parser lê só escalares de topo

`okf-validate.py` tem parser de frontmatter próprio, e ele lê **apenas pares `key: value` de nível
superior** — `parse_frontmatter` descarta qualquer linha indentada (`raw[:1] in (" ", "\t")` para
continuar). `docs/standards/code/frontmatter-parsing.md` §The subset each parser claims to read
declara isso como contrato, com a linha do `okf-validate.py` marcando **`no`** para registro inline
`{a: b}` e para registro em bloco.

Todas as famílias novas de v0.2 são aninhadas: `generated: {by, at}`, `verified` como lista de
mapas, `sources` como array de entradas, `executor: {resource, receipt}`. Logo:

- Um `generated:` **em bloco** (chaves indentadas embaixo) já é pego: `frontmatter_anomalies`
  classifica a corrida indentada como `indented-continuation` e o validador emite WARN
  `okf-frontmatter-unparsed` (`okf-validate.py:716`). O misread é nomeado.
- Um `generated:` **inline** passa batido e é o caminho perigoso. `partition(":")` devolve a chave
  `generated` e o valor `{by: quenching, at: 2026-07-30}` como **string**; não há `#`, não há aspas
  abertas, o valor não é vazio — nenhuma anomalia é registrada. Pior: `_nonempty(fm, "generated")`
  passa a ser verdadeiro, então um check ingênuo de campo recomendado ficaria satisfeito, e
  `check_stale_doc` faria `str(fm["generated"]).strip()[:10]`, obtendo `{by: quenc`, que não é ISO
  e o faz **retornar lista vazia em silêncio** (`okf-validate.py:588-592`).

Ou seja: adotar `generated:` sem tocar no parser desliga o `stale-doc` sem emitir nada.
`docs/standards/quality/parse-honesty.md` proíbe exatamente isso — *"a tool that transforms its
input before checking it MUST be able to report what the transform removed or could not
represent"*. Por isso o item "um doc com `generated:` e sem `timestamp:` nunca volta com zero
findings" é entregável de `## Proposal`, e não detalhe de implementação.

Estender o parser tem preço declarado: `frontmatter-parsing.md` chama a lista canônica de casos de
**unidade de lockstep** entre as três ferramentas, rodada pelo `selftest` de cada uma, e as três
**não podem se importar** porque cada uma se instala sozinha no `.claude/hooks/` do alvo. Um passo
no subset do `okf-validate.py` é, portanto, um passo na tabela do standard mais três selftests que
precisam concordar. É por isso que a extensão é `## Open Decisions`, e não uma task já decidida.

### A leitura dupla é o que v0.2 prescreve, não um remendo

O próprio §13 diz que consumidores **podem** cair de volta no `timestamp` legado quando o
`generated` está ausente. Isso alinha com dois contratos locais que já valem:

- `docs/standards/quality/bundle-verification.md` §*No new check is introduced at ERROR* — um check
  nascido em ERROR faz repo alvo que passava começar a falhar no upgrade, por docs que ninguém
  tocou. Logo `missing-generated`, se existir, nasce **WARN**, e só depois do fallback.
- O mesmo doc registra que o plugin é mais estrito que OKF **para os bundles que ele alinha**, e
  expressa isso no verify gate dos comandos, não no exit code.

A leitura dupla é permanente, e isso é aceito de propósito: enquanto existir bundle alinhado em
v0.1 no mundo, `timestamp:` é dado vivo. Só o bundle deste repo tem 25 docs com ele; o skeleton
entregue tem um (`assets/docs/knowledge/glossary.md`).

### A superfície que a subida move, medida

`okf_version`/`OKF v0.1` estão fixados em código e prosa nestes lugares, e é essa a lista que o
standard novo passa a carregar para a próxima subida não a redescobrir:

| Artefato | O que pina |
| --- | --- |
| `assets/hooks/okf-validate.py:748` | o literal `!= "0.1"` que produz `root-okf-version-mismatch` — sem constante nomeada |
| `assets/hooks/okf-validate.py:1180` | o fixture do `selftest` com `okf_version: "0.1"` |
| `assets/hooks/okf-validate.py:56,59-60` | o docstring do conformance core |
| `assets/docs/index.md:2` | o stamp do skeleton entregue |
| `docs/index.md:2` | o stamp do bundle deste repo |
| `commands/docs/align.md:189` | o passo que escreve `okf_version: "0.1"` no alvo |
| `assets/references/docs-align/okf-spec.md` | a transcrição inteira, incluindo a linha 92 e o §Frontmatter |
| `assets/references/docs-align/conformance.md:36` | o texto do `root-okf-version-mismatch` |
| `assets/references/docs-align/taxonomy.md:19` | o diagrama da árvore |
| `assets/templates/index.md.tmpl` | o mold da listagem |
| `assets/checks/functional-checks.sh:131` | o bundle sintético da checagem 4 |
| `docs/QUENCHING.md` e `assets/docs/QUENCHING.md` | o manual do operador de cada front |
| `assets/README.md`, `assets/hooks/README.md`, `plugins/quenching/README.md`, `README.md`, `.claude-plugin/marketplace.json` | a prosa de produto que diz "OKF v0.1" |

### Duas linhas do `okf-spec.md` que a reescrita não pode atropelar

- **Linha 92** fixa o `docs/index.md` da raiz a **`okf_version` e nada mais**. v0.2 §12 mantém essa
  forma, então a reescrita conserva o pin — e ele é exatamente o pin que o sibling
  `declare-repo-body-language` registrou como motivo para **não** pôr uma chave de idioma ali.
- **Linha 111** mantém, de propósito, uma declaração **autocontida** da regra de body language
  ("frontmatter é inglês; a prosa do corpo PODE seguir o idioma do repo"). É um format spec que
  outros implementadores leem: deferir para um doc local do repo o tornaria não autodescritivo. A
  reescrita para v0.2 preserva essa autocontenção literalmente.

### Onde a transcrição continua morando

Continua sendo `assets/references/docs-align/okf-spec.md`, asset do plugin citado por caminho
`${CLAUDE_PLUGIN_ROOT}` absoluto — não migra para `docs/reference/`. Duas razões: a regra de layout
(`docs/standards/architecture/plugin-layout.md`) põe procedimento compartilhado sob `assets/`
porque `commands/**` é a única árvore registrada, e `docs/reference/` é conhecimento **deste** repo,
que não viaja para o alvo junto com o plugin. Vendorizar o SPEC.md inteiro ao lado da condensação
criaria duas cópias do mesmo contrato — a forma exata que
`docs/standards/quality/bundle-verification.md` §*An invariant restated in more than two skills*
diz que sempre diverge.

### A regra durável que sai daqui

`docs/standards/architecture/okf-contract-version.md`, escrita como contrato e não como diário:

1. **Versão de contrato não é versão de plugin.** `okf_version` está fora dos seis do lockstep e
   fora do sétimo. As mudanças de código que a subida provoca entram no bump normal do conclude; o
   número do contrato não.
2. **Uma quebra de campo upstream é adotada como leitura dupla, com a chave legada como fallback,
   nunca como check novo em ERROR.**
3. **O stamp move por último**, e só quando todo MUST da versão nova está satisfeito. Um stamp à
   frente do que o validador fiscaliza é a forma C, rejeitada.
4. **A lista de artefatos que pinam a versão vive no standard**, medida, para que a próxima subida
   seja uma leitura e não uma varredura.

## Alternatives Considered

Alternativas de **forma inteira**, rejeitadas no nível do spec. As comparações por decisão ficam em
`## Design`.

| Abordagem | Por que perdeu |
| --- | --- |
| **Adoção completa numa passada** — reescrever a transcrição, renomear `timestamp` para `generated` em toda parte, adotar `sources`, subir o stamp e migrar os 25 docs locais mais o skeleton, tudo sob um único conjunto de tasks | Não é dimensionável hoje, e isso é literal: o repo não contém nenhuma declaração de v0.2, então a lista de tasks teria que ser escrita a partir de uma leitura que ninguém pode revisar contra um artefato local. Perde por inventar escopo, não por ser ambiciosa. Continua alcançável depois da tabela de delta. |
| **Só o stamp** — `okf_version: "0.2"` e o literal do `okf-validate.py:748`, sem adotar nada | Cala o `root-okf-version-mismatch` e passa a alegar uma versão cujas regras o validador não fiscaliza. É a forma que faz o único consumidor do campo mentir. Um stamp é uma afirmação sobre o que o bundle obedece, e nada obedeceria. |
| **Ficar em v0.1 de propósito e registrar o pin** | Não perdeu de fato — é a saída legítima do gate deste spec (task 0.3). Rejeitada apenas como *ponto de partida*: adotá-la antes da tabela de delta seria decidir sem ler, e as duas quebras do §13 tocam campo (`timestamp`) que este plugin usa em check e em gatilho, então o pin sem exame é palpite. |
| **Vendorizar o `okf/SPEC.md` upstream verbatim em `docs/reference/tools/`** e citá-lo em vez de condensar | Segunda cópia do mesmo contrato ao lado da condensação, que é a forma que `docs/standards/quality/bundle-verification.md` registra como divergente por construção — o mesmo doc mostra o gate de verify enumerado em três arquivos, os três discordando. E `docs/reference/` é conhecimento deste repo, que não viaja com o plugin para o alvo, então os comandos continuariam citando a condensação. A procedência que o vendor compraria é entregue por três linhas no topo do `okf-spec.md`: URL, data da leitura, versão declarada. |
| **Escrever um perfil "OKF-strict v2" próprio** e parar de acompanhar o upstream | Compra liberdade e perde a única coisa que o número entrega: o bundle ser reconhecível por um consumidor que não é este plugin. `okf-spec.md` §What this plugin adds on top já existe justamente para manter o perfil estrito **dentro** de OKF válido; um fork transformaria cada divergência num dialeto sem leitor. |
| **Esperar a v0.3** | Nada indica que ela venha; e a espera é onerosa de forma acumulativa, não neutra — cada bundle alinhado em v0.1 adiciona `timestamp:` para migrar depois. O §12 do upstream versiona em `major.minor` com aditivos compatíveis em minor, então subir para v0.2 não fica mais caro por existir uma v0.3, e a tabela de delta é reutilizável. |
| **Não fazer nada e deixar o `root-okf-version-mismatch` como está** | Não dispara: `docs/index.md` declara `"0.1"` e o validador espera `"0.1"`, então hoje não há finding nenhum. Ou seja, nada avisa. Rejeitada porque o silêncio é o problema, não o sintoma. |

## Open Decisions

Seis perguntas que este spec deliberadamente **não** decide. Cada uma traz a evidência ou o momento
que a fecha — nenhuma é um "a definir".

- **O parser do `okf-validate.py` passa a ler registros aninhados?** Todas as famílias novas de v0.2
  são aninhadas, e hoje o parser lê só escalares de topo por contrato declarado
  (`docs/standards/code/frontmatter-parsing.md` §The subset each parser claims to read, linha do
  `okf-validate.py` marcando `no` para registro inline e em bloco). **Como se decide:** a tabela de
  delta da task 1.3 diz se algum campo aninhado é de fato adotado; se for, a task 2.1 pesa o preço
  declarado — a lista canônica de casos é unidade de lockstep entre os `selftest` das três
  ferramentas, que não podem se importar — contra a alternativa mais barata de **exigir a forma em
  bloco**, que o `okf-frontmatter-unparsed` já nomeia hoje sem código novo. Decidido na 2.1, antes
  de qualquer adoção, e o veredicto é gravado no spec.

- **O stamp sobe para `"0.2"` neste spec, ou fica pinado em `"0.1"`?** **Como se decide:** a task
  2.1 lê a tabela de delta e sobe apenas se dois fatos valerem juntos — todo MUST de v0.2
  satisfeito, e as tasks 2.2/2.3 verdes. Se qualquer um faltar, o stamp fica em `"0.1"` e o pin é
  gravado como decisão no standard novo, com o que o destrava. Um stamp à frente do que o validador
  fiscaliza é a forma C rejeitada.

- **O `status: draft|stable|deprecated` de v0.2 coexiste com o `authority: current|background` deste
  plugin, ou um substitui o outro?** Os dois falam de maturidade e nenhum é necessário para estar
  conformante — `status` é opcional em v0.2, e `authority` é chave extra de produtor. **Como se
  decide:** a evidência que destrava é o primeiro consumidor externo real de um bundle deste plugin
  pedindo o campo padronizado. Até lá `authority` fica, `status` não é estampado, e a tabela de delta
  registra a sobreposição semântica em vez de escondê-la.

- **O `verified: [{by, at}]` de v0.2 pode lastrear o grading de `authority`?** É a família aditiva
  mais interessante para este repo, porque `authority: current` significa hoje "provado por um spec"
  e nada carrega quem provou nem quando. **Como se decide:** a pergunta só é respondível depois da
  decisão do parser — sem ler mapa aninhado, um campo de verificação é uma string opaca. Reavaliar
  quando a 2.1 tiver veredicto.

- **A chave própria `source:` é renomeada por causa do `sources:` de v0.2?** **Como se decide:**
  medindo o raio com a varredura de blast radius de `docs-align/migration.md` §3 (duas passadas, uma
  `git grep` e uma `grep -rn --no-ignore`) e decidindo num item de confirmação próprio, porque 25
  docs deste bundle mais os molds de `assets/templates/` estão no caminho. Nunca dentro do delta
  mínimo: um rename de chave de frontmatter durante uma subida de contrato mistura duas mudanças que
  precisam ser revertíveis em separado.

- **O `stale_after` de v0.2 substitui, complementa ou é ignorado pelo gatilho do `stale-doc`?** v0.2
  oferece um prazo de validade **declarado** onde o plugin hoje **deriva** desatualização de commits
  no raio do `resource:`. **Como se decide:** a pergunta pertence a
  `narrow-the-stale-doc-trigger-to-content-drift`, que está reescrevendo exatamente esse gatilho.
  Este spec registra que o campo existe, para que aquele sibling não decida sem saber, e não escolhe.
## Risks

Cada linha abaixo saiu de uma história de premortem — *"é três meses depois, isto foi construído e
deu errado"* — e cada história virou exatamente uma coisa: mitigação, risco aceito, ou corte que já
está em `## Out of Scope`.

### O que quebra silenciosamente

- **O `stale-doc` morre calado.** É a história mais provável e a pior de detectar. Adotar
  `generated:` na forma inline sem tocar no parser faz `check_stale_doc` ler `{by: quenc` como data,
  falhar o teste de ISO e **retornar vazio** (`okf-validate.py:588-592`), enquanto
  `_nonempty(fm, "generated")` passa a valer. O validador segue devolvendo exit 0 e ninguém percebe
  que a única checagem de desatualização que existe parou. *Mitigação:* a task 2.3 e as duas metades
  da asserção de `## Validation` transformam isso em teste — um doc cuja única data é um `generated:`
  ilegível tem de sair com **algum** código sobre isso, e a contagem de `stale-doc` neste bundle não
  pode cair a zero por efeito da migração. É o que `docs/standards/quality/parse-honesty.md` exige, e
  o mecanismo já existe (`okf-frontmatter-unparsed`, `okf-validate.py:716`).

- **Meia adoção: o stamp sobe e a fiscalização não.** Se a decisão do parser ficar diferida e a task
  do stamp rodar de todo modo, o bundle passa a alegar `"0.2"` sem obedecer v0.2 — que é
  exatamente a forma C rejeitada em `## Alternatives Considered`, chegando por acidente.
  *Mitigação:* dependência dura nas tasks — 3.1 e 3.2 só rodam depois de 2.2 e 2.3 verdes — e a
  regra 3 do standard novo ("o stamp move por último") existe para o próximo caso.

### O que a subida pode ter entendido errado sobre o upstream

- **A transcrição divergir do SPEC.md real.** A leitura de 2026-07-30 que fundamenta este spec veio
  de uma busca resumida, **não** de uma transcrição byte-exata. Se ela omitiu ou deformou um MUST, a
  tabela de delta nasce errada e todo veredicto em cima dela herda o erro — e nada no repo compara
  com o upstream, então a detecção é zero. *Mitigação:* a task 1.1 re-busca o texto bruto e registra
  procedência (URL, data da leitura, versão declarada) no topo do `okf-spec.md`, que é o que permite
  a um humano futuro re-conferir sem refazer a arqueologia. **A tabela de delta só é autoritativa
  depois da 1.1.**

- **ACCEPTED — o upstream publicar v0.3 no meio do spec.** O §12 versiona em `major.minor` com
  aditivos compatíveis em minor, então a tabela de delta e o standard novo se reaproveitam, e a
  subida de v0.1 para v0.2 não fica mais cara por existir uma v0.3. Aceitar é mais barato que
  esperar indefinidamente, que é a alternativa já rejeitada.

### O que quebra para quem consome o plugin

- **Um bundle alvo já alinhado em v0.1 começar a falhar no upgrade.** Todo doc lá carrega
  `timestamp:`; um `missing-generated` nascido em ERROR faria repo que passava falhar por docs que
  ninguém tocou. *Mitigação:* a leitura dupla com `timestamp:` como fallback — que o próprio §13 do
  upstream abençoa — mais a regra de `docs/standards/quality/bundle-verification.md` §*No new check
  is introduced at ERROR*. A regra 2 do standard novo grava isso para a próxima quebra.

- **ACCEPTED — um alvo que nunca roda `/docs:align` de novo fica em v0.1 e nada diz.** É a mesma
  assimetria que `docs/standards/ci-cd/versioning-release.md` §*Noticing drift* já registra: o
  offer é o único momento em que uma versão é comparada. Notar drift de **contrato** (e não de
  ferramenta, que o `skills.py drift` cobre) seria uma checagem nova, com seu próprio dono e seu
  próprio custo. Fica de fora de propósito, registrado aqui para não ser redescoberto como bug.

- **ACCEPTED — a leitura dupla é permanente.** Enquanto existir bundle alinhado em v0.1 no mundo,
  `timestamp:` é dado vivo, então o caminho de duas chaves não tem data de remoção. É o preço de
  não quebrar quem já adotou, e é o que v0.2 prescreve — não um remendo.

### Reversibilidade

Baixa exposição, e vale dizer por quê: quase tudo aqui é aditivo (a leitura dupla, a tabela de
delta, o standard novo) ou uma linha (o literal de versão em cada artefato de `## Design`). O único
item com massa é a migração de `timestamp:` nos 25 docs deste bundle, que é um commit revertível.
Desfazer o spec é reverter o merge, e nenhuma etapa deixa estado fora do repo.

### Siblings que tocam a mesma superfície — a fronteira, nunca a resolução

Nenhuma linha abaixo assume o resultado do sibling, e nenhum arquivo de sibling é editado aqui.

- **`declare-repo-body-language`** (aprovado, em execução) registra no seu `## Alternatives
  Considered` que pôr uma chave de body language no `docs/index.md`, ao lado do `okf_version`, foi
  rejeitado em parte por **colidir com este spec**: a linha 92 do `okf-spec.md` fixa aquela listagem
  a `okf_version` e nada mais. A fronteira que este spec mantém: a reescrita para v0.2 **conserva**
  aquele pin (v0.2 §12 mantém a mesma forma) e **conserva** a declaração autocontida de body
  language da linha 111, que o mesmo sibling mapeou como o único ponto que não deve deferir para um
  doc local. Este spec não adiciona chave nenhuma àquela listagem.
- **`narrow-the-stale-doc-trigger-to-content-drift`** reescreve o gatilho do `stale-doc`; as tasks
  2.2 e 2.3 aqui tocam a mesma função `check_stale_doc`, mas por outro motivo — que ela consiga
  **ler uma data**, não o que ela deveria medir. v0.2 ainda traz um `stale_after` declarativo, que
  é matéria daquele sibling e entra aqui só como registro em `## Open Decisions`. Qual dos dois
  pousa primeiro decide quem rebaseia; nenhum decide pelo outro.
- **`expose-finding-advisory-as-data`** muda o payload `--json` do validador. A fronteira já está
  escrita pelo próprio sibling, que registra que o contrato externo não governa aquele payload —
  e v0.2 não muda isso. Um código de finding novo que saia daqui herda o campo de advisory que o
  sibling definir, sem que este spec o defina.
- **`revise-standards-subject-folders`** pode mover as pastas de subject de `docs/standards/`. O
  standard novo é declarado em `architecture/` por vizinhança com
  `retiring-a-reserved-artifact.md`, que é o parente mais próximo; se aquele sibling renomear o
  subject, o caminho declarado em `## Impact` muda com ele. Este spec não escolhe a árvore.
- **`rewrite-readme-for-collapsed-surface`** reescreve o `README.md`, cuja linha 4 diz "OKF v0.1".
  A task 3.4 aqui toca a mesma linha. A fronteira: este spec muda **apenas o número da versão** na
  prosa de produto; a reescrita da prosa é do sibling.

### Colisão de nome de chave

- **`source:` (deste plugin) versus `sources:` (v0.2).** 25 docs deste bundle carregam `source:`,
  prosa livre de procedência, listada em `okf-spec.md` §Frontmatter como chave extra de produtor.
  v0.2 define `sources:` como array com forma declarada. Um consumidor OKF genérico não confunde as
  duas, mas um humano confunde e um `/docs:add` futuro pode estampar a errada. *Mitigação:* fica em
  `## Open Decisions` com o raio a medir, e a tabela de delta registra a proximidade explicitamente
  para que ela não seja descoberta por acidente.
## Tasks

Serial por padrão, e a ordem é ela mesma uma mitigação: **ler o campo antes de exigi-lo, fiscalizar
antes de estampar**. Nenhum grupo é marcado `[P]` — quase toda task toca `okf-spec.md` ou
`okf-validate.py`, então os conjuntos de `files:` não são disjuntos e paralelizar trocaria
wall-clock por conflito.

### 1. A transcrição e o delta

- [ ] 1.1 Re-buscar o `okf/SPEC.md` upstream em texto bruto e gravar a procedência no topo de `okf-spec.md`: a URL, a data da leitura e a `okf_version` que o documento declara. Nada abaixo é autoritativo antes disto.
      files: plugins/quenching/assets/references/docs-align/okf-spec.md
      verify: grep -n "knowledge-catalog" plugins/quenching/assets/references/docs-align/okf-spec.md
- [ ] 1.2 Reescrever `okf-spec.md` como condensação de **v0.2** — §Frontmatter, §Reserved filenames, §Normative rules e a política de versionamento —, conservando literalmente duas coisas: o pin da linha 92 (a listagem raiz carrega `okf_version` e nada mais) e a declaração **autocontida** de body language da linha 111.
      files: plugins/quenching/assets/references/docs-align/okf-spec.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/docs
- [ ] 1.3 **O gate do spec.** Escrever a tabela de delta v0.1 para v0.2 em `okf-spec.md`: uma linha por item do §13 upstream, cada uma com `adotado`, `inaplicável` (com motivo) ou `diferido` (com o que destrava). Registrar na tabela a proximidade `source:` versus `sources:` e a sobreposição `authority:` versus `status:`. **Se todos os itens saírem `inaplicável`, o spec para aqui:** só as tasks 5.1 e 6.1 rodam, gravando o pin em v0.1 como decisão.
      files: plugins/quenching/assets/references/docs-align/okf-spec.md
      verify: cada item do §13 tem exatamente uma linha e cada linha tem um dos três veredictos

### 2. Ler o campo antes de exigi-lo

- [ ] 2.1 Decidir, per `## Open Decisions`, se o parser do `okf-validate.py` passa a ler registros aninhados ou se a forma em bloco passa a ser exigida, e gravar o veredicto com o motivo em `## Design`. A decisão é o entregável; qualquer código depende dela.
      files: specs/plans/2026-07-28-upgrade-okf-to-v0-2.md
- [ ] 2.2 Implementar a leitura dupla `generated.at` com fallback para `timestamp:` em `check_concept` e `check_stale_doc`, conforme o veredicto da 2.1. Todo código de finding novo nasce **WARN**, per `docs/standards/quality/bundle-verification.md`.
      files: plugins/quenching/assets/hooks/okf-validate.py
      pattern: plugins/quenching/assets/hooks/okf-validate.py (check_stale_doc, linhas 575-605)
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py selftest
- [ ] 2.3 Fechar o caminho silencioso: um doc cuja única data é um `generated:` que o parser não lê **não sai calado** — o campo é lido, ou `okf-frontmatter-unparsed` nomeia o misread. Adicionar o caso ao fixture do `selftest` e rodar a sonda de `## Validation`.
      files: plugins/quenching/assets/hooks/okf-validate.py
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py selftest

### 3. O stamp e a superfície — só com 2.2 e 2.3 verdes

- [ ] 3.1 Decidir, per `## Open Decisions`, se o stamp sobe para `"0.2"`. Sobe só com todo MUST de v0.2 satisfeito **e** 2.2/2.3 verdes; caso contrário fica em `"0.1"` e o pin é gravado como decisão. Veredicto em `## Design`.
      files: specs/plans/2026-07-28-upgrade-okf-to-v0-2.md
- [ ] 3.2 Se a 3.1 subiu o stamp, mover o número em todo lugar que o pina: o literal `!= "0.1"` (`okf-validate.py:748`), o fixture (`:1180`), o docstring do conformance core (`:56,59-60`), o skeleton (`assets/docs/index.md`), este bundle (`docs/index.md`), o passo do align (`commands/docs/align.md:189`), o mold (`assets/templates/index.md.tmpl`) e o bundle sintético (`assets/checks/functional-checks.sh:131`).
      files: plugins/quenching/assets/hooks/okf-validate.py, plugins/quenching/assets/docs/index.md, docs/index.md, plugins/quenching/commands/docs/align.md, plugins/quenching/assets/templates/index.md.tmpl, plugins/quenching/assets/checks/functional-checks.sh
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py selftest
- [ ] 3.3 Escrever a regra de migração `timestamp:` para `generated:` em `docs-align/migration.md` §5, ao lado dos renomes de campo que já vivem lá, dizendo a leitura dupla explicitamente e deixando claro que a aplicação num alvo continua sendo proposta com OK.
      files: plugins/quenching/assets/references/docs-align/migration.md
- [ ] 3.4 Atualizar o texto do código `root-okf-version-mismatch` em `docs-align/conformance.md`, o diagrama de `taxonomy.md`, os dois `QUENCHING.md`, e **apenas o número** na prosa de produto (`README.md`, `plugins/quenching/README.md`, `assets/README.md`, `assets/hooks/README.md`, a `description` de `.claude-plugin/marketplace.json` — nunca o campo `version` dela).
      files: plugins/quenching/assets/references/docs-align/conformance.md, plugins/quenching/assets/references/docs-align/taxonomy.md, docs/QUENCHING.md, plugins/quenching/assets/docs/QUENCHING.md, README.md, plugins/quenching/README.md, plugins/quenching/assets/README.md, plugins/quenching/assets/hooks/README.md, .claude-plugin/marketplace.json

### 4. Migrar o que este repo já carrega

- [ ] 4.1 Aplicar ao bundle deste repo e ao skeleton entregue exatamente o que a 3.3 manda um alvo fazer, nem mais nem menos: os 25 docs de `docs/**` com `timestamp:` e o `glossary.md` do skeleton. Se a 3.1 pinou em v0.1, a task fecha registrando que não há migração a fazer.
      files: docs, plugins/quenching/assets/docs/knowledge/glossary.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs --json

### 5. Os standards que a subida prova

- [ ] 5.1 Escrever `docs/standards/architecture/okf-contract-version.md` (`type: standard`, `authority: current` quando a subida a provar) com as quatro regras de `## Design` §A regra durável e a tabela medida de artefatos que pinam a versão.
      files: docs/standards/architecture/okf-contract-version.md
      pattern: docs/standards/architecture/retiring-a-reserved-artifact.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs --json
- [ ] 5.2 Reconciliar `docs/standards/code/frontmatter-parsing.md` §The subset each parser claims to read com o veredicto da 2.1: a linha do `okf-validate.py` muda, ou o doc registra que o subset atravessou a subida inalterado. Nos dois casos a lista canônica de casos volta a valer nos três `selftest`.
      files: docs/standards/code/frontmatter-parsing.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py selftest && python3 plugins/quenching/assets/bin/specs.py selftest && python3 plugins/quenching/assets/bin/skills.py selftest

### 6. Verificação

- [ ] 6.1 Rodar a bateria inteira de `## Validation` e registrar a saída, incluindo a contagem de `stale-doc` antes e depois da 4.1 e a conferência de cobertura da tabela de delta.
      verify: ver `## Validation`
