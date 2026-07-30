---
slug: add-import-provenance
title: Add provenance and idempotent re-ingestion to quenching-docs-import
verification: per-section
priority: {level: 28, criticality: medium, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
approved: {date: 2026-07-30}
branch: {base: main, work: plan/add-import-provenance}
---

# Add provenance and idempotent re-ingestion to quenching-docs-import

## Overview

`/docs:import` é o comando que lê uma fonte externa — arquivos, uma pasta, uma URL — e cria vários
docs dentro do bundle `docs/`. Ele já é obrigado a dizer de onde cada doc veio, mas diz isso em prosa
livre, num campo que nenhum código lê e que neste repositório já significa outra coisa. Esta spec
conserta a metade barata e permanente desse problema: dá à origem uma chave própria e exata,
`source_uri:`, escrita apenas pelo import, e transforma "achar o doc que já cobre esta unidade" numa
consulta em vez de um reconhecimento.

Para se orientar entre as seções: `## Problem` mostra por que o enunciado original estava
parcialmente errado e por que a conta muda mesmo sem urgência; `## Proposal` lista o que fica
verdadeiro depois; `## Design` explica por que a detecção de mudança da fonte **não** cabe no
validador, por que a chave não entra no mold compartilhado, e por que a entrega foi encolhida até não
depender de uma reimportação; `## Alternatives Considered` guarda as formas que perderam, incluindo a
de não fazer nada; `## Risks` guarda o que foi aceito de olhos abertos — em primeiro lugar que
conteúdo importado é eternamente fresco para o validador; `## Out of Scope` e `## Open Decisions`
guardam a metade que não é construída, junto com a evidência que a reabriria.

O trabalho em si é pequeno e todo de prosa: `## Impact` nomeia os cinco arquivos do plugin e o único
standard tocados, `## Tasks` os percorre na ordem contrato-antes-de-comando que `## Risks` exige, e
`## Validation` diz o que roda por máquina e admite o único passo que só pode ser feito à mão, porque
não há fixture possível para um caminho que precisa de uma fonte externa real.
## Problem

Adiado do plano `docs-verification-layer` — um identificador da origem mais um hash de conteúdo,
para que uma fonte alterada seja detectável e uma reimportação enriqueça em vez de duplicar.

_(v1 backlog task — tags: ['docs', 'import', 'provenance'])_

O enunciado original desta spec afirma que `/docs:import` "não registra nada que identifique a
fonte". Lido contra o código, isso é **parcialmente falso**, e a correção muda o que precisa ser
construído:

- **A atribuição já é obrigatória.** `plugins/quenching/assets/references/docs-import/sources.md`
  §Attribution (linhas 56-62) manda gravar o caminho ou a URL da fonte no campo de frontmatter
  `source:`; `plugins/quenching/commands/docs/import.md` repete a regra duas vezes (linha 33, na
  doutrina de anti-fabricação, e linha 73, no passo 4) e
  `plugins/quenching/assets/docs/QUENCHING.md` (linha 157) a repete uma terceira vez.
- **O que falta não é o registro, é a leitura mecânica dele.** `source:` é prosa livre: não está em
  `RECOMMENDED` em `plugins/quenching/assets/hooks/okf-validate.py` (linha 145), portanto nenhum
  código o lê, o resolve ou reclama da sua ausência. Chave extra em concept doc não gera finding
  algum — `root-extra-keys` só existe para o `index.md` da raiz do bundle (linhas 751-754).
- **Pior: a chave já carrega outro sentido neste repositório.** Os 51 docs do bundle usam `source:`
  para narrar qual spec escreveu a regra (`source: docs-verification-layer plan (sections 2-4)`).
  Nenhum valor do bundle é uma URI. Uma chave, dois significados, zero verificação.

A consequência é a que o enunciado acerta: a regra **MERGE, never clobber** — repetida em
`import.md` (linhas 35-37 e no invariante da linha 87), em `sources.md` §Dedup e em
`plugins/quenching/assets/references/docs-add/homes.md` §Enriching the glossary — não tem base
mecânica. Achar o doc que já cobre uma unidade depende do modelo reconhecer prosa que ele mesmo
escreveu antes.

**Por que agora.** Nada mudou desde o adiamento: o caminho de import continua sem uso aqui — um
`grep '^source:' docs/` devolve 51 narrativas de spec e nenhuma URI. O que muda a conta é a
**irreversibilidade**, não a urgência. Procedência só pode ser estampada no instante em que o doc é
criado; a primeira importação real que rodar sem ela produz um lote cuja origem só se reconstrói à
mão depois, e é exatamente esse lote que uma reimportação não conseguirá classificar. E o argumento
do adiamento vale para **este** repositório, não para o produto: `QUENCHING.md` (linha 307)
documenta `/docs:import` como o caminho de onboarding de uma nova fonte de verdade num
repositório-alvo, que é onde o plugin é instalado.

## Proposal

- `/docs:import` estampa em cada doc que cria uma chave de frontmatter dedicada, `source_uri:`, com
  a URI ou o caminho exato da unidade de origem — separada de `source:`, que continua sendo a prosa
  de procedência autoral que os 51 docs deste bundle já usam.
- Achar o alvo de MERGE deixa de ser reconhecimento de prosa e passa a ser consulta exata: antes de
  criar qualquer doc, a etapa de dedup procura a URI da unidade no bundle
  (`grep -rn 'source_uri: {a-uri-da-unidade}' docs/`) e trata um acerto como alvo de
  enriquecimento.
- O plano da etapa 3 passa a mostrar, para cada unidade, se ela é **nova** ou **já importada
  antes**, com a URI que motivou a classificação — o humano vê a decisão duplicar-versus-enriquecer
  antes do OK único, em vez de confiar nela depois.
- A prosa de atribuição passa a ter **um** dono: hoje está escrita em quatro lugares; depois,
  `sources.md` é o dono e os outros três citam.
- A metade que **não** é construída fica registrada como **lacuna aceita** em
  `docs/standards/quality/bundle-verification.md`, com o motivo pelo qual não é verificável — não
  como um quarto parágrafo de doutrina.
- Nada disso adiciona código de finding, muda o validador, ou reescreve um único doc existente.

## Out of Scope

- **O hash de conteúdo e a detecção de drift.** É a metade que o enunciado pede explicitamente, e
  ela não é construível hoje. O validador nunca busca a fonte — a nota de trust de
  `okf-validate.py` (linhas 108-112) declara que os caminhos de hook nunca criam subprocesso e que
  o modo CLI só chama `git`, read-only. E `/docs:import` não tem `Bash` em `allowed-tools`
  (`commands/docs/import.md`, linha 4), então o próprio comando também não consegue calcular um
  digest. Fica em `## Open Decisions`, com a evidência que reabre a questão — não como trabalho
  silenciosamente esquecido.
- **Um finding para `source_uri:` ausente, inválido ou não resolvível.** É o vizinho que mais parece
  estar dentro do escopo. Fica fora por duas razões do próprio contrato:
  `docs/standards/quality/bundle-verification.md` proíbe nascer um check em ERROR, e um WARN
  dispararia nos 51 docs autorais que legitimamente não têm origem externa — ruído permanente, que
  é exatamente o critério pelo qual `TYPES_WITHOUT_RESOURCE` existe.
- **Colocar `source_uri:` no mold compartilhado de `homes.md`.** Cortado deliberadamente: quatro
  comandos citam aquele bloco de stamp, e uma chave lá é um convite para `/docs:add` inventar valor.
  Ver `## Design` §Decisão 2.
- **Backfill de `source:` para `source_uri:` nos docs existentes.** Nenhum deles veio de import;
  reescrever a chave inventaria uma procedência que não existe.
- **Mexer na semântica de `resource:`.** Para um doc de `reference/`, a URI do ativo já é o
  `resource:` (`homes.md` §The frontmatter stamp); para um `standard` importado, `resource:` é o
  glob set do que o doc governa **neste** repositório. Os dois campos respondem perguntas diferentes
  e não se fundem.
- **A procedência de `/docs:import-memory`.** Aquele comando apaga a memória depois de o doc
  aterrissar, o que faz da origem um caminho que deixa de existir — decisão de outra natureza, com
  outro risco.
- **Um comando de re-sincronização (`/docs:resync`) ou qualquer varredura periódica das fontes.**
  Nada aqui agenda uma releitura; o que esta spec entrega é o dado que uma releitura futura leria.

## Impact

Alcance declarado para revisão humana. Um único comando muda de comportamento, `/docs:import`;
nenhum outro comando, hook, agente ou script é tocado.

### Standards this spec will write into docs/standards/

- `docs/standards/quality/bundle-verification.md` — emenda, mantendo `authority: current`:
  procedência de importação é identidade mecânica e não deriva verificável; o validador nunca busca a
  fonte, logo "inalterado versus alterado" não é um check possível ali; e a atribuição fica
  registrada como **lacuna aceita** em vez de um quarto parágrafo de doutrina, que é a saída que o
  próprio standard autoriza.

### Standards at `authority: background` this spec may resolve

- none — os quatro standards em `authority: background` deste bundle
  (`quality/selftest-mutation.md`, `automation/session-evidence.md`, `automation/agents.md`,
  `automation/context-budget.md`) tratam de mutação de selftest, evidência de sessão, agentes e
  orçamento de contexto. Nenhum fala de import, procedência ou frontmatter, e este trabalho não prova
  nenhum deles.

### Product code this spec expects to touch

- `plugins/quenching/assets/references/docs-import/sources.md` — o dono do contrato de `source_uri:`
  (§Attribution e §Dedup)
- `plugins/quenching/commands/docs/import.md` — as etapas 2, 3 e 4, mais o corte da doutrina
  duplicada de atribuição
- `plugins/quenching/assets/references/docs-align/okf-spec.md` — a lista de chaves extras do perfil,
  em §Frontmatter
- `plugins/quenching/assets/references/docs-add/homes.md` — uma linha em §The frontmatter stamp
  marcando a chave como exclusiva do import
- `plugins/quenching/assets/docs/QUENCHING.md` — o manual do operador que `/docs:align` instala:
  a seção `/docs:import` e o parágrafo de chaves de frontmatter da linha 90

## Validation

Não existe fixture do caminho de import neste repositório e não é possível criar uma sem uma fonte
externa real, então a validação é deliberadamente dividida: o que é mecânico roda, e o que não é fica
**declarado como manual** — nunca silenciosamente omitido.

**Mecânico** — tudo roda da raiz do repositório:

- `python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/docs` →
  `0 error(s), 0 warning(s)`. Prova que a chave nova não quebra o esqueleto embarcado: chave extra em
  concept doc não é finding, e o `index.md` da raiz (o único lugar onde `root-extra-keys` existe) não
  é tocado.
- `python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/specs/plans --listing-root`
  → `0 error(s), 0 warning(s)`.
- `python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json` →
  `"commands": 26` e `"findings": []`. Prova que editar o corpo de `import.md` não mexeu na
  identidade da superfície.
- `python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching lint --json` → exit 0.
- Os três selftests, que devem continuar verdes porque nenhum script muda:
  `python3 plugins/quenching/assets/bin/specs.py selftest`,
  `python3 plugins/quenching/assets/bin/skills.py selftest`,
  `python3 plugins/quenching/assets/hooks/okf-validate.py selftest`.
- **O corte da doutrina duplicada, contado:** `grep -in attribut plugins/quenching/commands/docs/import.md`
  devolve **3** linhas hoje (17, 33, 73) — a 17 é uma citação de `sources.md`, a 33 e a 73 reafirmam a
  regra. Depois deve devolver **1**, e essa uma deve ser a citação.
- **A chave não vazou para os molds compartilhados:**
  `grep -rl source_uri plugins/quenching/assets/templates/` não devolve arquivo nenhum, e
  `grep -rl source_uri plugins/quenching/` devolve exatamente cinco caminhos: `sources.md`,
  `import.md`, `okf-spec.md`, `homes.md` e `assets/docs/QUENCHING.md`. Um sexto arquivo é a
  falha que `## Design` §Decisão 2 existe para evitar.
- `grep -n 'context: fork' plugins/quenching/commands/docs/import.md` → nada, sempre.
- Sobre o bundle **deste** repositório, o portão é **zero erros**, não zero avisos:
  `python3 plugins/quenching/assets/hooks/okf-validate.py docs` já devolve oito WARN de `stale-doc`
  pré-existentes, incluindo um em `standards/quality/bundle-verification.md`, e `stale-doc` é
  advisory e não faz parte de portão nenhum (`bundle-verification.md` §What is machine-checked).
  Editar aquele doc com `timestamp` de hoje remove aquele WARN específico como efeito colateral; os
  outros sete não são desta spec.

**Manual, declarado** — um walkthrough de reimportação registrado na revisão do branch: uma fonte
local pequena com duas seeds que se sobrepõem, `/docs:import` rodado duas vezes, conferindo que a
segunda rodada classifica as unidades como já importadas **pela URI** e propõe MERGE em vez de criar
um segundo doc. Sem esse passo a spec só pode afirmar que o contrato está escrito, não que o caminho
funciona — e o relatório precisa dizer que o check foi manual.

**Nenhum bump de versão faz parte desta validação.** Os seis artefatos do lockstep se movem uma vez,
em `/specs:conclude`, imediatamente antes do merge
(`docs/standards/ci-cd/versioning-release.md` §When the bump happens).

## Design

### Decisão 1 — uma chave nova, não a reutilização de `source:`

`source:` já é prosa carregada em 51 docs, com o sentido "qual spec ou pessoa originou esta regra".
Sobrecarregá-la com uma URI faria o mesmo campo responder duas perguntas, e nenhum consumidor
poderia confiar no formato. `source_uri:` é aditiva e segura por construção: o validador só reclama
de chaves extras no `index.md` da **raiz** do bundle (`root-extra-keys`, `okf-validate.py` linhas
751-754); em um concept doc, chave desconhecida não gera finding nenhum. O próprio OKF permite
(`okf-spec.md` §Frontmatter: "Producers MAY add any additional keys").

**Regra durável:** procedência autoral e procedência de importação são campos **diferentes** —
uma é prosa para um humano, a outra é chave de busca exata.

### Decisão 2 — a chave é estampada só pelo import, e não entra no mold compartilhado

`homes.md` §The frontmatter stamp é citado por `/docs:add`, `/docs:learn`, `/docs:harness` e
`/docs:import-memory`. Pôr `source_uri:` naquele bloco convidaria os quatro a inventar um valor —
exatamente a falha que este repositório já viveu com `resource:`, onde quatro comandos proibiam
inventar e nada verificava (`bundle-verification.md`, linhas 34-36). Por isso o contrato da chave
mora em `sources.md`, e `homes.md` ganha no máximo uma linha dizendo que o import acrescenta a chave
e que os demais comandos nunca a escrevem.

### Decisão 3 — a classificação é do comando, não do validador

Comparar a fonte com o que está no disco exige **buscar** a fonte. O validador não busca nada, por
projeto declarado. Logo a única execução em que "inalterado / alterado / novo" pode ser decidido é a
própria rodada de `/docs:import`, que já tem a unidade em contexto. O que o frontmatter carrega é o
**estado que a próxima rodada lê**, não um invariante que um checker prova. Essa é a diferença que
reclassifica a spec inteira: isto não é um recurso do validador, é um recurso do comando.

### Decisão 4 — a lacuna é registrada, não repetida

`bundle-verification.md` diz que um invariante repetido em mais de dois comandos é devido a um check
determinístico **ou** a uma lacuna aceita registrada como tal, nunca a um terceiro parágrafo; e o
corolário diz que, quando um check chega, a prosa que ele substitui é **cortada**. A atribuição está
escrita em quatro lugares. Esta spec, portanto, tem uma tarefa de **corte**, não só de escrita: a
doutrina de `import.md` passa a citar `sources.md` em vez de reafirmar a regra.

### Contratos que este desenho não pode contradizer

- `docs/standards/quality/bundle-verification.md` — nenhum check novo em ERROR; advisory é categoria
  pequena; a prosa substituída é cortada, não mantida como cinto-e-suspensório.
- `plugins/quenching/assets/references/docs-align/okf-spec.md` §3 e §6 — `resource` derivado e nunca
  inventado; frontmatter em inglês canônico, o que fixa o nome da chave como `source_uri`.
- `docs/standards/architecture/plugin-layout.md` e `align-surface.md` — nada aqui adiciona comando,
  hook ou agente; o alcance é prosa em `commands/**` e `assets/references/**`, mais um standard.
- A regra do próprio `CLAUDE.md`: nunca acrescentar `context: fork` a `import.md`, que segue sendo um
  comando de varredura com confirmação no meio do fluxo.
### Decisão 5 — o valor entregue não pode depender de uma reimportação

A crítica mais forte contra esta spec é que ela supõe um fluxo que ninguém observou: reimportar.
A resposta não é defender a suposição, é **encolher a entrega até ela não precisar da suposição**.
Uma consulta exata por `source_uri:` é útil na primeira rodada, porque uma lista de seeds com duas
páginas sobrepostas produz o mesmo problema de alvo de MERGE dentro de uma única execução — que é o
caso que `sources.md` §Dedup item 1 já reconhece ("within the source"). A reimportação passa a ser um
benefício adicional, e não a premissa. O que resta de suposição está registrado como risco aceito.

### Decisão 6 — a data da leitura vive no corpo, não numa segunda chave

Uma URI sem idade envelhece mal, e `timestamp:` já significa "última alteração do doc". A tentação é
uma segunda chave (`source_fetched:`). Recusada: duas chaves novas dobram a superfície de contrato
para um dado que a linha de atribuição no corpo — já exigida por `sources.md` §Attribution para
fonte estável — carrega sem custo nenhum de parsing. Uma chave nova por spec é o teto que este
desenho se impõe.
## Alternatives Considered

As quatro formas que a resposta podia tomar, comparadas antes de escolher:

| Abordagem | Custo | O que compra | O que fecha |
| --- | --- | --- | --- |
| **A — procedência mecânica completa**: `source_uri` + digest + código de finding no validador | alto: contrato de frontmatter, validador, `conformance.md`, `taxonomy.md`, os manuais `QUENCHING.md` e o corpo do comando | detecção automática de fonte alterada | exige rede dentro do validador, que ele declara não ter |
| **B — identidade agora, drift adiado e registrado** (recomendada) | 4 arquivos do plugin + 1 standard emendado | consulta exata do alvo de MERGE, plano honesto na etapa 3, lacuna registrada | nada: o digest continua possível depois, sobre a mesma chave |
| **C — manter o adiamento e abandonar a spec** | zero | fecha a fila | deixa a primeira importação real produzir docs sem origem recuperável |
| **D — um ledger de importação fora do frontmatter** (`docs/_imports/…`) | médio | um lugar só para consultar tudo que foi importado | cria uma segunda casa para o mesmo fato |

**Recomendação: B.** A é a que o enunciado pede e é a que o código proíbe — o validador não busca
fonte nenhuma. C é honesta mas paga o preço no pior momento possível, porque procedência só é barata
antes do primeiro import. D perde por dois motivos concretos: diretórios com prefixo `_` são podados
de toda a varredura do bundle (`okf-validate.py` linhas 165-168), então um ledger ali é invisível
para todo check e para todo `index.md`; e uma segunda casa para procedência é exatamente o erro que
este repositório já cometeu e desfez — `log.md` foi aposentado porque a procedência tinha dois
donos (`okf-spec.md` §4 e `docs/standards/architecture/retiring-a-reserved-artifact.md`), e a
procedência que morava lá foi realocada para o `## Outcome` da spec arquivada.

### As três alternativas que quase nunca são escritas

| Alternativa | Como o seu melhor defensor a defenderia | Por que perdeu |
| --- | --- | --- |
| **Não fazer nada** | o caminho segue sem uso; um recurso para um fluxo que ninguém exercitou é especulação, e foi assim que o plano-mãe decidiu | perde porque hoje o estado não é "adiado", é **não registrado**: `bundle-verification.md` exige check determinístico **ou** lacuna aceita escrita, e a atribuição não tem nenhum dos dois |
| **A menor coisa que poderia funcionar**: escrever só a lacuna aceita no standard e não tocar em mais nada | um parágrafo honesto num standard resolve a violação de contrato por 1 arquivo, e fecha a spec hoje | **não perdeu — foi absorvida.** A lacuna aceita é parte de B (`## Proposal`, último item), não uma alternativa a ela. O que B acrescenta são 4 edições de prosa que a lacuna sozinha não compra |
| **Comprar ou emprestar**: adotar o modelo de procedência do `enrich` da implementação de referência do OKF | é código já pensado, com caps de ingestão já provados, e `sources.md` §Bounded ingestion já ecoa esses caps | perde porque aquele `enrich` depende de BigQuery e de dependências pesadas, explicitamente excluídas por `import.md` (linhas 11-12) — o que se pode emprestar dele é disciplina, e isso já foi emprestado |

## Open Decisions

- **O digest de conteúdo é acrescentado depois, ou nunca?** Deliberadamente não decidido aqui — é a
  metade que o enunciado original pedia. **Como se decide:** na primeira rodada real de
  `/docs:import` contra uma fonte web, buscar a mesma página duas vezes com `WebFetch` e comparar os
  dois retornos. `WebFetch` devolve markdown já processado por modelo, não os bytes brutos; se os dois
  retornos forem idênticos, um digest sobre a saída de `WebFetch` é reprodutível e a questão reabre.
  Se diferirem, um digest de fonte web fica recusado por construção e sobra apenas a hipótese de
  fonte local.
- **Dar `Bash` a `/docs:import` é aceitável?** Não decidido, e não precisa ser para esta spec — sem
  `Bash` (`import.md`, linha 4) nenhum digest é calculável, nem para fonte local. **Como se decide:**
  junto da questão acima, e pelo critério de segurança, não de conveniência: o comando ingere conteúdo
  externo não confiável, e somar shell a isso amplia o raio de uma injeção de prompt. Uma alternativa
  a considerar na mesma ocasião é expor o cálculo por um subcomando de um script já embarcado — o
  `okf-validate.py` já importa `hashlib` (linha 118) — em vez de conceder shell ao comando.
- **`/docs:import-memory` também deveria estampar `source_uri:`?** Não decidido. **Como se decide:**
  pela pergunta de se a procedência deve sobreviver ao apagamento da memória que a originou. Aquele
  comando limpa a memória depois de o doc aterrissar, então o caminho de origem deixa de existir e a
  chave passaria a apontar para o nada — caso em que o campo certo continua sendo prosa em `source:`.
  Fica para quem tocar naquele comando, e esta spec não o toca.

## Risks

- **A suposição que sustenta a spec é que uma reimportação vai acontecer, e não há evidência disso.**
  `QUENCHING.md` (linha 307) documenta `/docs:import` como onboarding de uma nova fonte de verdade —
  um ato de uma vez. Reimportar é fluxo suposto, não observado.
  `ACCEPTED — o valor entregue foi deliberadamente desacoplado da reimportação`: a consulta exata por
  `source_uri:` também serve a **primeira** rodada, porque duas seeds da mesma lista de seeds se
  sobrepõem com frequência e a busca do alvo de MERGE é a mesma. Se a reimportação nunca acontecer,
  o que sobra ainda é atribuição legível por máquina; nada do que esta spec constrói fica órfão.

- **Um doc importado é eternamente fresco, e isto não muda.** Quando `resource:` de um doc importado
  é a URI do ativo, `parse_resource` classifica a entrada como `uri`, e tanto `check_resource`
  (linhas 685-686) quanto `check_stale` (linhas 597-600) descartam entradas fora de
  `RESOLVABLE_KINDS`. Ou seja: nenhum sinal de obsolescência jamais dispara para conteúdo importado.
  `ACCEPTED — é a razão pela qual o drift é uma questão aberta e não uma tarefa`; qualquer sinal de
  deriva de conteúdo é território da spec irmã `narrow-the-stale-doc-trigger-to-content-drift`, e
  esta spec não toca em `stale-doc`, em `check_stale`, nem em `RESOLVABLE_KINDS`.

- **`/docs:add` pode passar a inventar `source_uri:`.** Custo permanente de qualquer chave nova num
  ecossistema onde quatro comandos citam o mesmo bloco de stamp. Mitigação: a chave **não** entra no
  bloco de `homes.md` (`## Design` §Decisão 2); só `sources.md` a especifica.
  `ACCEPTED — a mitigação é posicional, e a detecção é nenhuma`: nada verifica um valor inventado,
  e é precisamente essa a lacuna que a tarefa 4.1 registra em
  `docs/standards/quality/bundle-verification.md` em vez de fingir que a prosa resolve.

- **A URI estampada morre com o tempo.** Uma URL que hoje responde devolve 404 num ano, e nenhum
  check vai notar (mesmo motivo do item acima). Mitigação: a linha de atribuição no corpo do doc,
  que `sources.md` §Attribution já exige para fonte estável, passa a carregar **a data da leitura**,
  de modo que um leitor julgue a idade da URI sem depender de `timestamp:`, que significa outra coisa
  (última alteração do doc).

- **Aterrissagem parcial entre um corpo de comando e a sua referência.** A mudança toca quatro
  arquivos de prosa, e nada cruza a consistência entre eles: `skills.py doctor` e `skills.py lint`
  leem `commands/**`, não `assets/references/**`. O sintoma seria `/docs:import` estampando uma chave
  que `sources.md` não documenta, ou o contrário — silenciosamente. Mitigação: a ordem das tarefas
  põe o contrato antes do comando, e a política `verification: per-section` já declarada faz cada
  grupo verificar junto.

- **Sobreposição com `upgrade-okf-to-v0-2` (spec irmã, em desenvolvimento em paralelo).** Aquela spec
  pode reescrever o contrato de frontmatter do perfil OKF-strict. Fronteira que esta mantém:
  acrescenta **uma** chave aditiva dentro do perfil v0.1 corrente e não toca em `okf_version`, nem na
  numeração das regras de `okf-spec.md` §What this plugin adds on top. Se a irmã reespecificar o
  conjunto de chaves, `source_uri` é uma linha que ela precisa carregar; esta spec não presume o
  resultado dela.

- **Sobreposição com `expose-finding-advisory-as-data` (spec irmã).** Esta spec **não** cria nenhum
  código de finding, então não há status advisory novo para aquela expor. Registrado para que a irmã
  não precise contabilizar um.

- **Sobreposição com `revise-standards-subject-folders` (spec irmã).** O standard emendado é
  declarado no caminho em que ele mora hoje, `docs/standards/quality/bundle-verification.md`. Se
  aquela spec mover a pasta de assunto, o caminho declarado em `## Impact` muda com ela; esta spec
  não escolhe a pasta nem antecipa a mudança.

## Handoff

As treze tarefas estão construídas, verificadas e commitadas — uma por commit, treze commits em
`plan/add-import-provenance`. O que falta é `/specs:conclude`: a revisão do branch, os `docs/` que o
trabalho revelou, o merge e a distilação. Estado que não se deriva da árvore:

- **Isolamento:** worktree em `../claude-quenching-add-import-provenance`, cortado de `main` em
  `9c289f1`. O checkout principal `~/Projects/claude-quenching` está sendo usado por **outra sessão
  Claude Code em paralelo**, que edita `specs/plans/2026-07-28-decide-plans-index-need.md`. Rebasear
  ou mergear a partir de lá sem olhar essa árvore suja é o risco desta spec.
- **Uma mudança fora do escopo declarado, deliberadamente NÃO commitada.**
  `.claude/settings.json` (versionado) aponta para `.claude/hooks/okf-validate.py`, que o commit
  `193578c` apagou sem tirar a fiação — todo `Write|Edit` e todo `Stop` do repo disparavam um hook
  inexistente. O arquivo foi reinstalado em 4.4.0 **sem ser versionado**, nos dois checkouts, para
  manter os treze commits dentro dos arquivos que `## Impact` declara. **Decidir em `/specs:conclude`**
  se ele entra no repo, se a fiação sai de `settings.json`, ou se fica local.
- **Duas falhas de desenho encontradas pelo walkthrough**, em `## Discoveries`: a unidade colapsada
  de duas seeds carrega só uma `source_uri:`, e o argumento da `## Design` §Decisão 5 não se
  sustenta. Nenhuma das duas invalida o que foi entregue, e as duas são material de revisão de
  branch — não de mais uma tarefa aqui.
- **Portões, na última medição (2026-07-30):** okf-validate 0/0 nos dois bundles embarcados; `docs`
  do repo com **0 error(s)**, 15 warning(s) — todos advisory, sendo 14 `stale-doc` e um
  `resource-unresolved` pré-existente; `doctor` com 26 comandos e zero findings; `lint` exit 0; os
  três selftests verdes. A base `main` já trazia 12 + 1.
- **Não exercitado, e não exercitável aqui:** o comando `/docs:import` registrado. O registry é
  montado no início da sessão, então o corpo editado só carrega numa sessão nova. A primeira sessão
  depois do merge deve rodar `/skill:new` ou uma importação real antes de confiar na superfície.
## Tasks

### 1. O contrato da chave

- [x] 1.1 Escrever o contrato de `source_uri:` em `sources.md` §Attribution — formato do valor, só `/docs:import` estampa, `source:` segue sendo prosa autoral, e a linha de atribuição no corpo passa a carregar a data da leitura
      files: plugins/quenching/assets/references/docs-import/sources.md
      verify: grep -n source_uri plugins/quenching/assets/references/docs-import/sources.md
      subject: plan/add-import-provenance: 1.1 Escrever o contrato de source_uri: em sources.md §Attribution
- [x] 1.2 Trocar §Dedup item 2 de `sources.md` para começar pela consulta exata à `source_uri:` no bundle e só depois cair no grep por título, slug e termo
      files: plugins/quenching/assets/references/docs-import/sources.md
      subject: plan/add-import-provenance: 1.2 §Dedup começa pela consulta exata à source_uri
- [x] 1.3 Acrescentar `source_uri` à lista de chaves extras do perfil em `okf-spec.md` §Frontmatter, ao lado de `audience`, `authority`, `source` e `maintainer`
      files: plugins/quenching/assets/references/docs-align/okf-spec.md
      subject: plan/add-import-provenance: 1.3 source_uri na lista de chaves extras do perfil em okf-spec.md
- [x] 1.4 Marcar em `homes.md` §The frontmatter stamp, em uma linha e sem acrescentar a chave ao bloco, que `source_uri:` é escrita apenas por `/docs:import` e nunca inventada pelos outros comandos que citam o bloco
      files: plugins/quenching/assets/references/docs-add/homes.md
      verify: test -z "$(grep -rl source_uri plugins/quenching/assets/templates/)"
      subject: plan/add-import-provenance: 1.4 marcar em homes.md que source_uri é escrita só pelo import

### 2. O comando

- [x] 2.1 Fazer a etapa 2 de `import.md` classificar cada unidade como nova ou já importada pela consulta exata à `source_uri:`, antes do grep por prosa
      files: plugins/quenching/commands/docs/import.md
      subject: plan/add-import-provenance: 2.1 etapa 2 classifica cada unidade pela consulta exata à source_uri
- [x] 2.2 Fazer a etapa 3 mostrar a classificação de cada unidade no plano único, com a URI que a motivou, tornando a decisão duplicar-versus-enriquecer visível antes do OK
      files: plugins/quenching/commands/docs/import.md
      subject: plan/add-import-provenance: 2.2 a etapa 3 mostra a classificação de cada unidade no plano
- [x] 2.3 Fazer a etapa 4 estampar `source_uri:` em cada doc criado e escrever a linha de atribuição no corpo com a data da leitura
      files: plugins/quenching/commands/docs/import.md
      subject: plan/add-import-provenance: 2.3 a etapa 4 estampa source_uri e a data da leitura
- [x] 2.4 Cortar a doutrina duplicada de atribuição — as linhas 33 e 73 passam a citar `sources.md` em vez de reafirmar a regra, restando uma única menção no arquivo
      files: plugins/quenching/commands/docs/import.md
      verify: test 1 -eq $(grep -ic attribut plugins/quenching/commands/docs/import.md)
      subject: plan/add-import-provenance: 2.4 cortar a doutrina duplicada de atribuição em import.md
- [x] 2.5 Conferir que a superfície não mudou de identidade — 26 comandos, sem findings, e lint em exit 0
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json
      subject: plan/add-import-provenance: 2.5 conferir que a superfície não mudou de identidade

### 3. O manual do operador

- [x] 3.1 Atualizar `assets/docs/QUENCHING.md` — a seção `/docs:import` e o parágrafo de chaves de frontmatter da linha 90 — descrevendo a chave e a classificação nova versus já importada
      files: plugins/quenching/assets/docs/QUENCHING.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/docs
      subject: plan/add-import-provenance: 3.1 atualizar QUENCHING.md com a chave e a classificação

### 4. O standard

- [x] 4.1 Escrever a emenda em `docs/standards/quality/bundle-verification.md`, mantendo `authority: current`: a lacuna aceita da atribuição, e a regra de que a deriva da fonte não é verificável dentro de um validador que nunca busca nada
      files: docs/standards/quality/bundle-verification.md
      pattern: docs/standards/quality/bundle-verification.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs | grep -q '0 error(s)'
      subject: plan/add-import-provenance: 4.1 a lacuna aceita da procedência em bundle-verification.md

### 5. Verificação

- [x] 5.1 Rodar o bloco mecânico inteiro de `## Validation` e registrar cada saída
      subject: plan/add-import-provenance: 5.1 rodar o bloco mecânico de ## Validation e registrar as saídas
- [x] 5.2 Executar e registrar o walkthrough manual de reimportação descrito em `## Validation`, dizendo no relatório que o check foi manual
      subject: plan/add-import-provenance: 5.2 walkthrough manual de reimportação, executado e registrado

## Discoveries

- A asserção de `## Validation` "grep -n 'context: fork' import.md → nada, sempre" é falsa por construção: a própria invariante que proíbe a chave contém a string (linha 96, `- **Never add \`context: fork\`.**`). O grep literal devolve essa linha antes e depois desta spec. O que o check quer dizer é "a chave não aparece no frontmatter"; escrito como está, ele nunca pode passar.
- `## Validation` afirma que `okf-validate.py docs` devolve oito WARN de `stale-doc` pré-existentes. Medido em 2026-07-30 sobre `main` (9c289f1), são **doze**, mais um `resource-unresolved` em `standards/automation/agents.md` (`.claude/agents/**` não casa nada) que a spec não menciona. O número da spec envelheceu; o portão declarado (zero erros) continua válido e nenhum dos dois é desta spec.
- Efeito colateral estrutural de qualquer spec que toque `plugins/quenching/**`: os commits refrescam o último commit dos `resource` que vários standards governam, então a contagem de `stale-doc` **sobe** durante a construção (12 → 14 aqui) mesmo sem nenhum doc ficar errado. É advisory e fora de todo portão, mas convém dizer no relatório em vez de deixar parecer regressão.
- Furo no contrato de `source_uri:` que o walkthrough expôs: uma unidade **colapsada de duas seeds** (§Dedup item 1, dedup dentro da fonte) recebe UMA só URI, porque a chave é single-valued por contrato ("One value on one line"). A URI da segunda seed nunca é estampada, então numa reimportação ela **não** casa por URI e cai na busca por semelhança — exatamente o reconhecimento que a spec queria substituir. Medido em 2026-07-30: `source/api-notes.md:3` colapsada em `handbook.md:3` não casou na rodada 2. Decidir se a chave vira lista, se cada seed colapsada ganha a sua linha no corpo, ou se o furo é aceito e registrado.
- `## Design` §Decisão 5 afirma que a consulta exata já se paga na PRIMEIRA rodada, porque duas seeds sobrepostas produzem o mesmo problema de alvo de MERGE dentro de uma execução. O walkthrough não sustenta isso: duas seeds sobrepostas têm URIs **diferentes**, logo a consulta exata nunca as casa — quem as junta é o dedup por prosa dentro da fonte (§Dedup item 1). O valor real da chave é mesmo na REIMPORTAÇÃO, que é a suposição de que a Decisão 5 tentou desacoplar a entrega. O argumento da Decisão 5 precisa ser corrigido ou retirado; o que ele defende (a entrega não depender de reimportação) fica sem sustentação empírica.
