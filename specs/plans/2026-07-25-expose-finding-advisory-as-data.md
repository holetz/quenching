---
slug: expose-finding-advisory-as-data
title: Expose a finding's advisory/blocking status as data in okf-validate --json
verification: per-section
priority: {level: 23, criticality: medium, complexity: 3, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# Expose a finding's advisory/blocking status as data in okf-validate --json

## Overview

O validador do bundle `docs/` reporta problemas em dois níveis de gravidade: erro e aviso. Alguns
avisos precisam ser corrigidos antes de o repositório ser considerado alinhado; um deles é apenas um
lembrete de que um documento pode ter envelhecido. Essa diferença nunca foi escrita no dado que o
validador devolve — ela foi escrita em texto, em cinco arquivos, para cada comando reler e lembrar.

`## Problem` mostra o resultado disso, medido: os arquivos que repetem a regra já discordam sobre
quais avisos precisam ser corrigidos, e a discordância aprova ou reprova **este mesmo repositório**
dependendo de qual arquivo o comando leu. `## Proposal` diz o que passa a ser verdade depois: o próprio
validador responde a pergunta, uma vez, e quem consulta apenas lê a resposta.

`## Design` explica por que a resposta entra como um campo novo ao lado da gravidade em vez de virar
uma gravidade nova, por que ela é calculada num único ponto do código e não nos vinte e quatro lugares
onde os avisos nascem, e qual suposição sustenta tudo isso — se ela cair, a forma certa deixa de ser um
campo. `## Alternatives Considered` guarda as cinco formas que a resposta poderia ter tido, incluindo
não fazer nada, com o motivo de cada recusa. `## Out of Scope` marca a fronteira mais fácil de
confundir: esta mudança **classifica** os avisos que já existem, sem inventar classificação para os
seis que ninguém classificou e sem mexer em quando cada um dispara.

`## Risks` é onde o trabalho de imaginar o fracasso foi parar, e a pior história tem nome: um aviso novo
entra sem classificação e o gate emudece sem avisar ninguém — por isso `## Tasks` gasta uma task
inteira em fazer o autoteste reprovar exatamente esse caso. `## Validation` fixa o baseline de hoje em
números, para que "funcionou" seja comparável e não uma impressão. `## Open Decisions` guarda as três
perguntas que esta spec deliberadamente **não** responde, cada uma com o que as decidiria. `## Impact`
declara o único standard que a spec promete escrever, e `## Handoff` avisa quem for construir que os
números de linha citados aqui envelhecem — o alvo se acha pelo texto.
## Problem

Encontrado pela revisão de fim de plano do `docs-verification-layer` — "`stale-doc` é advisory" está
repetido em prosa em cinco arquivos e doze lugares, enquanto o payload JSON não carrega campo nenhum
em que um comando possa decidir

_(v1 backlog task — tags: ['docs', 'validator', 'conformance'])_

`okf-validate.py --json` emite `severity`, `path`, `code`, `message` (`okf-validate.py:1257-1259`).
Se um WARN é **must-fix** (`resource-self`, `index-broken-link`, …) ou **advisory** (`stale-doc`)
não está no payload — está na prosa, repetido em `docs-align/conformance.md` (×3),
`commands/docs/status.md` (×6), `docs-align/cycle.md`, `docs/standards/quality/bundle-verification.md`
e no docstring do próprio validador (×2). A contagem original citava
`quenching-docs-status/SKILL.md` (×5); o arquivo foi renomeado para `commands/docs/status.md` pelo
collapse da superfície e a contagem subiu para ×6, então o problema não encolheu com o tempo.

Esse é exatamente o padrão contra o qual o plano que o encontrou escreveu um standard.
`docs/standards/quality/bundle-verification.md` diz que um invariante repetido em mais de dois
lugares deve um **check determinístico**, não uma terceira repetição — e o mesmo plano produziu doze
repetições de uma regra. Também contraria o princípio declarado da front: um comando decide por
**dado, nunca por prosa**.

**As cópias já divergiram — isso é medido, não previsto.** O verify gate está enumerado em três
arquivos e os três discordam sobre quantos códigos bloqueiam:

| Arquivo | Códigos must-fix que nomeia |
| --- | --- |
| `assets/references/docs-align/conformance.md:127` | **seis** — `dir-no-index`, `index-broken-link`, `index-orphan`, `glossary-broken-link`, `resource-unresolved`, `resource-self` |
| `assets/references/align/convergence.md:85` | **três** — `dir-no-index`, `index-broken-link`, `index-orphan` |
| `commands/docs/align.md:270` (step 8, o verify do próprio align) | **três** — os mesmos três |

**E a divergência morde hoje, neste repositório.** `okf-validate.py docs --json` sobre o bundle deste
próprio plugin devolve 14 findings: 12 `stale-doc` e **2 `resource-unresolved`**. Sob o gate de seis
códigos do `conformance.md`, o bundle **não está limpo**. Sob o gate de três do `convergence.md` e do
step 8 do `commands/docs/align.md`, ele **está**. Ou seja: `/docs:align` declara este repositório
alinhado e `/align` declara a front `docs/` limpa, enquanto o contrato que ambos citam diz que não.
Não é um risco futuro — é reproduzível numa chamada.

O defeito não é a contagem de repetições; a contagem é o mecanismo. O defeito é que **duas frentes do
mesmo plugin rodam gates incompatíveis**, e nenhuma delas está errada em relação à sua própria cópia.

A forma a considerar é um campo por finding — derivado do `code` — para que o gate de um comando
filtre mecanicamente em vez de cada arquivo relembrar quais códigos excluir. A prosa substituída
deve então ser **cortada**, não mantida ao lado, conforme o corolário desse mesmo standard.
## Proposal

- Cada finding no payload de `okf-validate.py --json` carrega uma chave nova, `blocking`, booleana.
  Hoje o objeto tem exatamente quatro chaves e nenhuma responde "isso reprova o verify gate?".
- A classificação passa a existir em **um** lugar: uma constante de módulo dentro do
  `okf-validate.py`. Hoje o conjunto must-fix é enumerado em prosa em três arquivos que **não
  concordam** entre si.
- Um consumidor filtra o gate mecanicamente — `[f for f in findings if f["blocking"]]` — em vez de
  carregar a lista de códigos junto com o corpo do comando.
- Os três gates do plugin (`docs-align/conformance.md` §Verify gate, `align/convergence.md` §The
  convergence contract, `commands/docs/align.md` step 8) passam a concordar por construção, porque
  passam a ler a mesma fonte em vez de repeti-la.
- As enumerações de código na prosa são **cortadas**, não mantidas ao lado do campo. O *porquê* de
  `stale-doc` ser advisory continua escrito no standard; a *lista* que cada consumidor tinha de
  repetir desaparece.
- `okf-validate.py selftest` passa a provar a classificação, e não apenas a prosa que a descreve.
- Nada muda no exit code, no relatório de texto, nem em nenhum dos três caminhos de hook
  (`PreToolUse`, `PostToolUse`, `Stop`).

## Out of Scope

- **Uma terceira severidade (`ADVISORY` ao lado de `ERROR`/`WARN`)** — descartada com razões em
  `## Alternatives Considered`. Mudaria o contrato de exit code de todo target repo já alinhado.
- **Reclassificar os seis WARNs que hoje nenhum documento classifica** —
  `okf-frontmatter-unparsed`, `root-no-okf-version`, `root-okf-version-mismatch`, `root-extra-keys`,
  `readme-not-index`, `bundle-no-index`. Esta spec **transcreve** o gate que existe: nenhum gate os
  nomeia hoje, então recebem `blocking: false`. Se algum deveria bloquear é uma decisão separada,
  com sua própria evidência, registrada em `## Open Decisions`.
- **O relatório humano (`_render_text`, `okf-validate.py:1102-1110`)** — quem lê texto lê a mensagem
  inteira e o código entre parênteses; o campo existe para quem filtra, não para quem lê.
- **O vocabulário `sp-*` e `sk-*` (`specs.py`, `skills.py`)** — severidade minúscula própria
  (`"warn"`/`"error"`) e ambos já têm um helper `finding(..., **extra)` (`specs.py:2452`,
  `skills.py:653`) onde um campo assim custa uma linha. O problema medido é do `okf-*`; estender por
  simetria seria escopo sem evidência. O `skills.py exit_for` (`skills.py:659-663`) já declara a
  regra que o `okf-*` viola: "a conductor can gate on an exit code without a severity table of its
  own". A spec irmã `decide-sp-unrefined-severity` faz a pergunta de *escalar severidade* dentro do
  vocabulário `sp-*`; esta spec **rejeita** escalar severidade no `okf-*` (`## Alternatives
  Considered`) e não presume nada sobre o que aquela decidir — os dois vocabulários são independentes
  por construção, porque os tools não se importam.
- **O bump das seis versões do lockstep** — `docs/standards/ci-cd/versioning-release.md` §When the
  bump happens diz que ele acontece uma vez, no `/specs:conclude` step 5, imediatamente antes do
  merge, e **nunca como task**.
- **Estreitar quando o `stale-doc` dispara** — é a spec irmã
  `narrow-the-stale-doc-trigger-to-content-drift`. Esta spec classifica o código; não toca no
  gatilho.
- **Consolidar os três gates num único documento de prosa** — cortar as listas é obrigação desta
  spec; reorganizar qual arquivo é dono de qual contrato não é, e cairia em cima de
  `revise-standards-subject-folders`.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/quality/bundle-verification.md` — a coluna "Blocking?" da tabela deixa de ser a
  fonte da classificação e passa a apontar para o campo `blocking` do validador; o §Corollary passa a
  citar esta mudança como o caso em que ele foi aplicado. A tabela em si permanece, porque ela é o
  *porquê*, e é o porquê que um standard existe para guardar.

### Standards at `authority: background` this spec may resolve

- none — os dois standards que este design cita, `quality/bundle-verification.md` e
  `quality/parse-honesty.md`, já são `authority: current`. Não há regra acordada-mas-não-provada aqui
  para promover.

### Product code this spec expects to touch

- `plugins/quenching/assets/hooks/okf-validate.py` — a constante de classificação, o predicado, a
  chave no `--json` (`run_cli`), o `selftest`, e as duas repetições no docstring do módulo.
- `plugins/quenching/assets/references/docs-align/conformance.md` — o dono declarado do contrato
  código-a-código: a **enumeração** do verify gate sai, a explicação por código fica.
- `plugins/quenching/assets/references/align/convergence.md` — a lista de três códigos em §The
  convergence contract.
- `plugins/quenching/commands/docs/align.md` — a lista de três códigos no step 8.
- `plugins/quenching/commands/docs/status.md` — a lista de seis códigos mais as repetições de
  "`stale-doc` é advisory" espalhadas pelo corpo.
- `docs/knowledge/glossary.md` — a entrada **Advisory finding** repete o conjunto de seis inteiro.
  Ela é uma **quinta** cópia, que a captura original não contou; entra no corte pela mesma razão que
  as outras, e por `/docs:define`, nunca por edição direta.

**O que deliberadamente NÃO é tocado, e por quê — a armadilha da ortogonalidade.**
"Auto-fechável pelo align" e "bloqueia o gate" são dois eixos diferentes que usam **os mesmos nomes de
código**, e confundi-los destrói informação. A prova: `resource-unresolved` é `No` na tabela de
auto-fechamento (o align não o fecha sozinho) e ao mesmo tempo **bloqueia** o gate. Três lugares caem
nessa armadilha e **permanecem intactos**:

- `assets/references/docs-align/cycle.md` — a coluna "Auto-closed by the align?" inteira, incluindo a
  linha do `stale-doc`. É o eixo do auto-fechamento, não a repetição do gate.
- `commands/docs/align.md:186` — `no dir-no-index, no index-broken-link, no index-orphan left behind`
  descreve o **alvo** do trabalho estrutural do stage 1, e carrega exatamente os mesmos três códigos
  que a frase do gate no step 8, que sai.
- `commands/docs/status.md:107` — a lista `stage 1 (dir-no-index, index-broken-link, index-orphan, ...)`
  do §4 item 3 é o conjunto auto-fechável que o relatório promete mostrar.

Isso foi descoberto rodando os `verify:` da seção 2 contra o repositório **antes** do trabalho: uma
primeira versão contava códigos por linha e teria exigido cortar os três lugares acima. Os `verify:`
atuais ancoram na frase do gate e **asseram que as linhas ortogonais sobreviveram** — é por isso que
eles falham hoje pelo motivo certo, e não por contagem.

## Validation

Baseline medido em 2026-07-30, antes de qualquer task, a partir de `plugins/quenching/`:

| Comando | Saída hoje |
| --- | --- |
| `cat VERSION` · `okf-validate.py --version` | `4.4.0` · `okf-validate 4.4.0` |
| `okf-validate.py selftest` | `12 canonical frontmatter case(s) + the retired-log fixture` · `PASS` |
| `okf-validate.py assets/docs` | `0 error(s), 0 warning(s)` |
| `okf-validate.py assets/specs/plans --listing-root` | `0 error(s), 0 warning(s)` |
| `skills.py --root . doctor --json` | 26 commands, 0 findings |
| `skills.py --root . lint --json` | exit 0 |
| `okf-validate.py ../../docs --json` | 14 findings — 2 `resource-unresolved`, 12 `stale-doc` |

O que deve ser verdade ao final:

1. **A chave existe em todo finding.** Da raiz do repositório:
   `python3 plugins/quenching/assets/hooks/okf-validate.py docs --json`
   e todo objeto do array carrega `blocking` — nenhum ausente, nenhum `null`.
2. **A classificação está certa nos findings que este repositório de fato produz.** Os
   `resource-unresolved` voltam com `blocking: true`; todo `stale-doc` volta com `blocking: false`.
   **A contagem de `stale-doc` não é asserção**: editar `assets/**` faz subir o número por largura de
   glob, comportamento conhecido e registrado na spec irmã
   `narrow-the-stale-doc-trigger-to-content-drift`. O que se assere é a classificação de cada um,
   qualquer que seja a contagem.
3. **A cobertura é total e provada.** `python3 plugins/quenching/assets/hooks/okf-validate.py selftest`
   sai `PASS` com contagem de casos **maior** que os 12 de hoje, e um dos casos novos falha quando um
   código emitido pelo validador não aparece na classificação. A prova de que o caso funciona é
   removê-lo temporariamente da constante e ver o selftest sair 1 — feito uma vez, na task, e narrado
   no relatório.
4. **Todo `ERROR` é `blocking: true`.** Asserido no `selftest`, não por inspeção.
5. **As enumerações saíram.** `grep -rn 'index-orphan' plugins/ docs/` não devolve nenhuma linha que
   *enumere o conjunto do gate* — só as linhas que explicam o código individualmente
   (`conformance.md` §Structural integrity, o docstring do validador) e a linha de `cycle.md`, que é
   ortogonal e permanece. Contagem esperada de linhas enumerativas: **zero**.
6. **Nada regrediu no resto.** `okf-validate.py assets/docs` e
   `okf-validate.py assets/specs/plans --listing-root` seguem em `0 error(s), 0 warning(s)`;
   `skills.py --root . doctor --json` segue com 26 commands e 0 findings; `skills.py --root . lint --json`
   segue em exit 0. Os corpos de comando editados são os de `docs/align.md` e `docs/status.md`, então o
   `doctor` e o `lint` são a única prova mecânica disponível na sessão que os escreve.
7. **O lockstep continua íntegro.** `okf-validate.py --version` concorda com `VERSION`. O **bump** não
   é verificado aqui porque não é feito aqui — `docs/standards/ci-cd/versioning-release.md` §When the
   bump happens o coloca no `/specs:conclude` step 5.

**Fora do alcance de verificação mecânica:** se o corte preservou o *rationale*. Isso é leitura
humana, na revisão de branch do `/specs:conclude`, e o critério está escrito em `## Risks`.

## Design

### Decisão 1 — a chave se chama `blocking`, não `advisory`

Três razões, todas verificadas no repositório:

- a pergunta que **todo** consumidor faz é "isso reprova o gate?", não "isso é conselho?" —
  `docs-align/conformance.md` §Verify gate, `align/convergence.md` §The convergence contract e
  `commands/docs/align.md` step 8 todos formulam exatamente essa pergunta;
- `advisory` obriga uma negação dupla no único lugar onde o campo é lido (`if not f["advisory"]`), e
  esse lugar é um gate;
- a categoria advisory tem hoje **um** membro (`stale-doc`). Um booleano batizado pelo caso raro se
  lê como flag de exceção, não como classificação, e `bundle-verification.md` §"Advisory is a real
  category, and must stay small" garante que ele continuará raro.

`blocking` também é **total**, não parcial: vale `true` para todo `ERROR` (que já reprova pelo exit
code) e para os seis WARN must-fix, `false` para o resto. Um campo que responde para todo finding não
exige que o leitor saiba antes se a pergunta se aplica. A redundância em `ERROR` é aceita
explicitamente em `## Risks`.

### Decisão 2 — a classificação é um lookup no ponto de serialização, não um quinto elemento da tupla

`okf-validate.py` monta findings como tuplas cruas `(severity, path, code, message)` em ~24 sítios de
emissão (linhas 603, 688, 692, 705, 709, 716, 718, 725, 734, 737, 741, 746, 749, 753, 757, 929, 971,
974, 981, 995, 1025, 1073, 1080, 1087) e as converte em dict em **exatamente um** lugar: `run_cli`,
`okf-validate.py:1256-1259`. Alargar a tupla obrigaria 24 sítios a declarar algo que se lê em um.

Esse é literalmente o argumento que `docs/standards/quality/parse-honesty.md` §"The shape: a sidecar,
not a changed return type" já fixou para este mesmo arquivo: devolver `(value, understood)` do parser
foi rejeitado "across nine call sites" porque "the signal is only *read* in two places, so it should
only be *asked for* in two places". Aqui são ~24 sítios de escrita e **um** ponto de leitura, então o
mesmo raciocínio pesa mais, não menos.

Forma: uma constante de módulo `BLOCKING_WARN_CODES` (frozenset com os seis códigos) e um predicado
de uma linha consultado ao montar o dict — nada acima dele muda de assinatura.

### Decisão 3 — o conjunto must-fix é transcrito do gate existente, não redesenhado

`assets/references/docs-align/conformance.md:127` é a única das três cópias que enumera os seis:
`dir-no-index`, `index-broken-link`, `index-orphan`, `glossary-broken-link`, `resource-unresolved`,
`resource-self`. É essa lista que a constante recebe.

A escolha de tomar essa cópia como verdade não é preferência: `docs/standards/quality/bundle-verification.md`
(linha 18, `authority: current`) declara `conformance.md` **"the code-by-code contract"**, e as outras
duas a citam. Ou seja, existe um dono documentado do conjunto, e as listas de três códigos são
consumidores repetindo o dono de forma incompleta — não um gate deliberadamente mais frouxo. O `git log`
**não** consegue confirmar isso de forma independente: um commit de rename em massa achatou o histórico
das três linhas, então a evidência é a ownership declarada e o fato de que só o `conformance.md`
justifica cada um dos seis códigos individualmente.

### Decisão 4 — acrescentar a chave é aditivo, e a preocupação levantada na captura não se aplica

A captura pedia para pesar que "qualquer consumidor lendo o payload posicionalmente precisaria ser
verificado". Verificado: o payload é um **array de objetos JSON** (`okf-validate.py:1257-1259`), e um
objeto não tem posição. Uma chave nova não desloca nada; nenhum dos três consumidores lê por índice.
A preocupação era legítima na captura e se dissolve na leitura — registrada aqui para que ninguém a
levante de novo.

### Decisão 5 — a suposição que sustenta a spec, dita em voz alta

O design assume que **"bloqueia" é propriedade do código sozinho**, não do código mais o chamador. Se
`/docs:align` legitimamente precisasse de um gate mais estreito que `/docs:status` — por exemplo, uma
instalação nova não devendo bloquear em `index-orphan` enquanto o bundle ainda está sendo montado —
então um booleano não expressa isso e a forma da spec estaria errada.

A divergência medida aponta na direção dessa dúvida (dois arquivos com três códigos, um com seis), e é
por isso que a suposição fica escrita aqui em vez de enterrada: quem for construir isso deve conferir
a ownership do `bundle-verification.md:18` antes de a tomar como resolvida. Resolvida por essa
ownership, a suposição se sustenta; se ela caísse, a forma correta passaria a ser um gate nomeado por
chamador, e não um campo — o que tornaria esta spec inteira a coisa errada a construir. Nenhuma task
depende dessa dúvida ficar aberta, mas nenhuma task pode contradizê-la em silêncio.

### Contratos que este design não pode contradizer

- `docs/standards/quality/bundle-verification.md` §"No new check is introduced at ERROR" — nenhuma
  severidade sobe. O campo é paralelo à severidade, e é isso que o mantém compatível.
- idem §Corollary — "when a check lands, the prose it replaces gets *cut*, not kept as
  belt-and-braces. Two enforcers for one invariant is how they drift." Manter as listas ao lado do
  campo reproduziria o defeito com um passo extra.
- idem linha 18 — `conformance.md` é o dono declarado do contrato código-a-código.
- `docs/standards/quality/parse-honesty.md` §The shape — sidecar, nunca assinatura alargada; e §The
  rule, consequência 3 — a regra não entra sem o `selftest` que a prova.
- `docs/standards/ci-cd/versioning-release.md` — os três tools **não podem importar** uns aos outros,
  porque cada um instala sozinho em `.claude/hooks/` de um target. A constante fica dentro do
  `okf-validate.py`; não existe módulo compartilhado para ela. E o bump das seis versões acontece no
  `/specs:conclude`, nunca como task.
- OKF v0.1 não governa o formato do `--json` do validador, então nenhuma cláusula do contrato externo
  é tocada.
## Alternatives Considered

| Alternativa | Custo | Ganho | O que fecharia | Veredito |
| --- | --- | --- | --- | --- |
| Uma terceira severidade, `ADVISORY` | toca o contrato de exit code e os dois caminhos de hook | uma dimensão só, sem campo paralelo | qualquer consumidor que teste `== "WARN"` | **rejeitada** |
| Não fazer nada — manter em prosa | zero | zero | nada | **rejeitada** |
| Só a constante no validador, sem campo no JSON | mínimo | prosa unificada | o acesso do consumidor | **rejeitada** |
| Dois arrays no topo (`blocking` / `advisory`) | quebra todo consumidor atual | dispensa o filtro | a forma do payload | **rejeitada** |
| Um subcomando `gate` com exit 1 | superfície de CLI permanente | ergonomia | nada — não substitui o campo | **rejeitada como esta spec** |

**Uma terceira severidade, `ADVISORY`.** Foi a alternativa que a própria captura sugeriu ("a
severity vocabulary may be the better place to express it"), e é a mais atraente porque não
acrescenta campo nenhum: a severidade já é o eixo em que o leitor pensa. Perdeu na leitura do código.
`_split()` (`okf-validate.py:1096-1099`) parte os findings exatamente em `"ERROR"` e `"WARN"`; o exit
code (`1262-1267`), o `warnAsError` (`1265`) e os filtros de report dos dois caminhos de hook
(`1329`, `1348`) todos testam `== "WARN"` literalmente. Um `stale-doc` que deixasse de ser `WARN`
sairia silenciosamente de `warnAsError`, e todo target repo já alinhado veria o comportamento mudar
num upgrade que ninguém pediu — precisamente o que `bundle-verification.md` §"No new check is
introduced at ERROR" proíbe ("makes previously passing target repos start failing on upgrade, for
docs nobody touched").

**Não fazer nada — deixar em prosa.** Dita da forma mais forte: prosa é revisável por humanos, um
campo booleano não explica por que `stale-doc` não bloqueia, e o repositório já tem um standard que
diz o porquê. Perdeu porque **é a alternativa que já foi testada e falhou de forma medida**: as três
cópias divergiram (seis códigos em `conformance.md:127`, três em `align/convergence.md:85`, três em
`commands/docs/align.md:270`). Prosa não é a opção neutra aqui; é a opção com resultado conhecido. E
`bundle-verification.md` diz literalmente que "the seventh restatement would not have either".

**A menor coisa que poderia funcionar: a constante no validador e nada no JSON.** Resolve a
divergência entre as prosas por um custo quase nulo, e por um momento parece suficiente. Perdeu por
pouco, e a razão é mecânica: nenhum consumidor **importa** o `okf-validate.py` — cada um o **invoca**
como CLI e lê o `--json` (`commands/docs/status.md:70`, `commands/docs/align.md:90`,
`align/convergence.md:84`). Uma constante que nenhum consumidor alcança é documentação escrita em
sintaxe de Python. Ela é parte da solução, não a solução.

**Dois arrays no topo, `{"blocking": [...], "advisory": [...]}`.** O gate fica sem filtro nenhum, e a
separação é impossível de ignorar. Perdeu porque o topo do payload deixa de ser uma lista de findings
e todo consumidor atual quebra de uma vez — um custo de migração real para poupar um list
comprehension de uma linha.

**Um subcomando novo, `okf-validate.py gate {docs}`, com exit 1 quando algo bloqueia.** É a forma mais
ergonômica de todas: o consumidor deixa de filtrar e passa a ler um exit code, que é a interface que
`skills.py exit_for` (`skills.py:659-663`) já defende como a certa. Rejeitada **como esta spec**, não
como ideia: acrescenta superfície de CLI permanente, e não elimina o campo, porque
`commands/docs/status.md` §4 tem de **reportar** advisory e blocking em seções separadas do relatório
— um gate por exit code responde sim/não, o campo responde quais e por quê. Fica registrada como
possível sequência depois que o campo existir e alguém medir que o filtro incomoda.

## Open Decisions

- **Algum dos seis WARNs que ninguém classificou deveria bloquear?** `okf-frontmatter-unparsed`,
  `root-no-okf-version`, `root-okf-version-mismatch`, `root-extra-keys`, `readme-not-index` e
  `bundle-no-index` não aparecem em nenhum gate e em nenhuma tabela de
  `bundle-verification.md`. Esta spec os transcreve como `blocking: false` porque é o que o gate atual
  diz por silêncio, e transcrever não é decidir. O caso mais forte para reabrir é o
  `okf-frontmatter-unparsed`: ele significa que o validador **leu o arquivo errado**, então todo outro
  finding sobre aquele doc é suspeito, e `docs/standards/quality/parse-honesty.md` §Severity explica
  por que ele é WARN — mas isso é sobre *severidade*, não sobre o *gate*.
  *Como se decide:* fora desta spec, com a evidência que falta — quantas vezes cada um dos seis
  disparou em bundles reais. Uma chamada de `okf-validate.py --json` em cada repositório alinhado
  responde, e é barata. Até lá, `blocking: false` é a transcrição honesta, e o campo torna a pergunta
  **visível** em vez de deixá-la implícita, que é ganho por si só.

- **O corte de prosa em `commands/docs/*.md` pertence a `/specs:execute` ou a `/skill:new`?**
  `CLAUDE.md` diz que corpos de comando são o código-fonte deste repositório e que uma edição ali se
  trata como edição de função; a superfície `.claude` tem um comando próprio para cunhar e editar
  comandos (`/skill:new`), e `commands/**` não é testável na sessão que o escreve. Um corte de duas
  enumerações é mecânico e cabe numa task; mas se a leitura do gate exigir reescrever o step 8 do
  `commands/docs/align.md`, isso é autoria de comando.
  *Como se decide:* na revisão de branch do `/specs:conclude`, pela natureza do diff que a task
  produziu — se o corte virou reescrita, ele é roteado para `/skill:new` em vez de ficar. A task deve
  ser escrita para falhar visivelmente nesse caso, não para absorvê-lo.

- **A chave é `blocking` ou o par `{severity, blocking}` deveria virar um objeto aninhado?** Nenhum
  consumidor pediu aninhamento e a forma plana é a que os outros dois tools já usam
  (`specs.py:2452`, `skills.py:653`), então a spec fica plana.
  *Como se decide:* só reabre se um consumidor futuro precisar de uma terceira dimensão sobre o mesmo
  finding — nesse momento a forma plana já terá três chaves irmãs e a pergunta se responde sozinha.

## Risks

- **Um código novo entra sem classificação e silenciosamente nunca bloqueia.** O frozenset é
  exatamente o tipo de lista paralela que apodrece: quem acrescentar um `code` numa spec futura pode
  não tocar nele, e o default (`blocking: false`) faz o gate emudecer em vez de reclamar. É a pior
  falha possível aqui, porque enfraquece o gate sem produzir sinal.
  *Mitigação (deve uma task):* o `selftest` assere **cobertura total** — todo código que o validador
  pode emitir aparece na classificação, e um código sem classificação **falha** o selftest. Isso é a
  terceira consequência de `docs/standards/quality/parse-honesty.md` §The rule aplicada a esta
  mudança: "a tool with no way to prove it implements the rule does not get the rule".

- **Version skew: a cópia instalada num target repo é antiga e não emite a chave.** Os três tools são
  instalados dentro de `.claude/hooks/` de cada target e só são sobrescritos quando o align compara
  `--version` (`docs/standards/ci-cd/versioning-release.md` §"Artifacts 4-6 are the *installed-copy*
  trigger"). Um comando que leia `f["blocking"]` contra uma cópia velha levanta `KeyError`, ou pior,
  um comando que leia com default errado inverte o gate.
  *Mitigação:* todo consumidor lê com default explícito e conservador — ausência da chave significa
  "não sei", e o comando cai de volta na enumeração antiga **dizendo no relatório que caiu**, como
  `commands/docs/status.md` §1 já faz para o checker ausente. O `skills.py drift` e a chamada de drift
  do align já detectam a cópia atrasada; o que esta spec deve é não *depender* dela.

- **A prosa é cortada junto com o motivo.** Se o corte levar as frases de *rationale* e não só as
  *enumerações*, alguém lê `blocking: false` no `stale-doc` daqui a seis meses, não encontra o porquê,
  e re-escala o código — reintroduzindo exatamente o ruído que
  `docs/standards/quality/bundle-verification.md` §"Advisory is a real category" existe para impedir.
  *Mitigação:* o corte é **enumeração-apenas**, declarado assim em `## Impact` e em cada task de
  corte; `bundle-verification.md` §"Advisory is a real category, and must stay small" e o docstring
  por código do validador permanecem intactos, e a constante cita o standard.

- **O campo entra e a prosa não é cortada.** Dois enforcers para um invariante é literalmente como
  eles divergem (`bundle-verification.md` §Corollary). Uma spec que entrega o campo e deixa as listas
  reproduz o defeito com um passo a mais.
  *Mitigação:* os cortes são tasks explícitas, uma por arquivo, com o caminho no texto da task — não
  uma linha final "e atualizar a documentação".

- **Sobreposição de arquivo com specs irmãs em `commands/docs/*.md`.**
  `restore-routing-info-on-docs-commands` e `route-commands-without-always-on-descriptions` estão
  sendo desenvolvidas em paralelo e mexem nos mesmos arquivos que o corte de prosa toca. A fronteira
  que esta spec mantém: ela edita **corpo** (as enumerações de código nos steps), nunca o
  `description` do frontmatter, que é o território daquelas duas. `narrow-the-stale-doc-trigger-to-content-drift`
  mexe no mesmo código (`stale-doc`) mas no **gatilho**, não na classificação, e
  `upgrade-okf-to-v0-2` pode mudar o conjunto de códigos que existe.
  *Mitigação:* nenhuma resolução é assumida aqui. O `## Handoff` deve registrar que um merge dessas
  irmãs antes desta spec muda os números de linha citados, e que o corte se guia pelo **texto**
  procurado, nunca por número de linha.

- **ACCEPTED — o campo é redundante para findings `ERROR`.** Um `ERROR` já reprova pelo exit code, e
  `blocking: true` nele não informa nada novo. Aceito de propósito: um campo presente só em WARN
  obrigaria todo leitor a tratar a ausência, que é o problema da dupla negação em outra roupa. Um
  campo total custa uma chave redundante e poupa um `if` em cada consumidor.

- **ACCEPTED — a classificação continua sendo uma segunda declaração ao lado do `severity`.** Duas
  dimensões sobre o mesmo finding podem, em princípio, discordar (um `ERROR` com `blocking: false`).
  Aceito porque a alternativa — uma dimensão só — é a terceira severidade já rejeitada em
  `## Alternatives Considered`, e porque o selftest pode assertar a invariante que impede a
  discordância: todo `ERROR` é `blocking: true`, sem exceção.

## Tasks

### 1. A classificação, no validador

- [ ] 1.1 Declarar `BLOCKING_WARN_CODES` (frozenset com os seis códigos de `conformance.md:127`) junto
      às outras constantes de módulo, com um predicado de uma linha, e emitir a chave `blocking` no
      dict do `--json` em `run_cli` — sem alargar a tupla de nenhum sítio de emissão. O comentário da
      constante cita `docs/standards/quality/bundle-verification.md` como a origem da lista.
      files: plugins/quenching/assets/hooks/okf-validate.py
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs --json | python3 -c "import json,sys; d=json.load(sys.stdin); assert d, 'no findings to check'; assert all('blocking' in f for f in d); assert all(f['blocking'] is (f['code']=='resource-unresolved') for f in d if f['code'] in ('resource-unresolved','stale-doc')); print('ok', len(d))"

- [ ] 1.2 Estender o `selftest` com dois casos: **cobertura total** — todo código que o validador pode
      emitir aparece classificado, e um código sem classificação faz o selftest sair 1 — e a
      invariante **todo `ERROR` é `blocking: true`**. Provar o primeiro caso removendo um código da
      constante, confirmando exit 1, e restaurando; narrar essa prova no relatório da task.
      files: plugins/quenching/assets/hooks/okf-validate.py
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py selftest

- [ ] 1.3 Cortar as duas repetições de "advisory, never blocking" do docstring do módulo, deixando a
      explicação por código intacta e apontando a classificação para a constante. A seção STALENESS
      mantém o motivo de o `stale-doc` não bloquear; perde a afirmação de que a lista vive na prosa.
      files: plugins/quenching/assets/hooks/okf-validate.py
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py selftest && python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/docs

### 2. O corte das enumerações

- [ ] 2.1 Em `conformance.md` §Verify gate, substituir a enumeração dos seis códigos pela leitura do
      campo (`blocking: true` no `--json`). A explicação por código de §Structural integrity,
      §Resource integrity e §Staleness **permanece** — o que sai é a lista repetida do gate. Confirmar
      antes de cortar que a linha visada é a do gate, localizando-a pelo **texto**, nunca por número de
      linha.
      files: plugins/quenching/assets/references/docs-align/conformance.md
      verify: python3 -c "t=open('plugins/quenching/assets/references/docs-align/conformance.md').read(); assert 'WARNs are all cleared' not in t, 'a frase do gate ainda enumera codigos'; assert 'blocking' in t, 'o gate nao cita o campo'; print('gate le o campo')"

- [ ] 2.2 Em `align/convergence.md` §The convergence contract, trocar a lista de três códigos pela
      leitura de `blocking` — o que também corrige o gate frouxo, já que a lista de três omitia
      `glossary-broken-link`, `resource-unresolved` e `resource-self`.
      files: plugins/quenching/assets/references/align/convergence.md
      verify: python3 -c "t=open('plugins/quenching/assets/references/align/convergence.md').read(); assert 'reporting zero \`dir-no-index\`' not in t, 'a frase do gate ainda enumera codigos'; assert 'blocking' in t, 'o gate nao cita o campo'; print('gate le o campo')"

- [ ] 2.3 No step 8 de `commands/docs/align.md` (a frase "structural-integrity WARNs are cleared"),
      trocar a lista de três códigos pela leitura de `blocking`. **A linha 186 fica** — `no dir-no-index,
      no index-broken-link, no index-orphan left behind` descreve o alvo do trabalho estrutural do
      stage 1, não o gate, e carrega os mesmos três códigos: é a mesma armadilha de ortogonalidade do
      `cycle.md`. Se o corte exigir reescrever o step em vez de substituir a enumeração, **parar** e
      registrar a rota para `/skill:new` conforme `## Open Decisions`, em vez de absorver a autoria.
      files: plugins/quenching/commands/docs/align.md
      verify: python3 -c "t=open('plugins/quenching/commands/docs/align.md').read(); assert 'structural-integrity WARNs are cleared' not in t, 'a frase do gate ainda enumera codigos'; assert 'left behind' in t, 'a linha ortogonal do stage 1 foi cortada por engano'; assert 'blocking' in t, 'o gate nao cita o campo'; print('gate le o campo, linha ortogonal preservada')" && python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json

- [ ] 2.4 Em `commands/docs/status.md`, colapsar a lista de seis códigos (a frase "are what a verify
      gate blocks on") e as repetições de "`stale-doc` é advisory" numa única instrução que lê o campo.
      **A linha 107 fica** — a lista `stage 1 (dir-no-index, index-broken-link, index-orphan, ...)` do
      §4 item 3 é o conjunto **auto-fechável**, ortogonal a `blocking`, e o relatório do §4 continua
      **separando** advisory de blocking em seções distintas; o que muda é de onde ele sabe qual é qual.
      files: plugins/quenching/commands/docs/status.md
      verify: python3 -c "t=open('plugins/quenching/commands/docs/status.md').read(); assert 'are what a verify gate blocks on' not in t, 'a frase do gate ainda enumera codigos'; assert 'stage 1 (\`dir-no-index\`' in t, 'a lista auto-fechavel do §4 foi cortada por engano'; assert t.count('advisory')<=3, ('advisory ainda repetido', t.count('advisory')); assert 'blocking' in t, 'o corpo nao cita o campo'; print('enumeracao cortada, lista ortogonal preservada')" && python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json && python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json

### 3. Os documentos duráveis

- [ ] 3.1 Escrever `docs/standards/quality/bundle-verification.md` (`authority: current`, a regra é
      provada pelas tasks 1.1-1.2): a coluna "Blocking?" passa a apontar para o campo `blocking` como
      fonte, o §Corollary ganha este corte como o caso concreto em que foi aplicado, e a §"Advisory is
      a real category" permanece inteira — é o *porquê*, e é o que o standard existe para guardar.
      Re-carimbar `timestamp`.
      files: docs/standards/quality/bundle-verification.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs --json | python3 -c "import json,sys; d=json.load(sys.stdin); mine=[f for f in d if f['path'].endswith('bundle-verification.md')]; assert not [f for f in mine if f['blocking']], mine; print('standard limpo, findings restantes:', [f['code'] for f in mine])"

- [ ] 3.2 Refinar a entrada **Advisory finding** de `docs/knowledge/glossary.md` via `/docs:define`,
      trocando a enumeração dos seis códigos pela definição da categoria mais o ponteiro para o campo.
      A entrada é a quinta cópia da lista e a captura original não a contou.
      files: docs/knowledge/glossary.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs --json | python3 -c "import json,sys; d=json.load(sys.stdin); assert not [f for f in d if f['code']=='glossary-broken-link']; print('glossary links ok')"
