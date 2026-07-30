---
slug: wire-the-overview-consumers
title: "Wire the three consumers to read `## Overview`"
verification: per-section
priority: {level: 5, criticality: high, complexity: 4, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# Wire the three consumers to read `## Overview`

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

Um spec agora abre com uma seção de orientação escrita por um humano, `## Overview` — este parágrafo
é uma. Ela existe desde o spec add-eli5-section-to-specs, mas nada a lê: os lugares onde alguém
pergunta "do que este spec trata" continuam remontando a resposta por conta própria, a cada execução,
a partir das seções densas mais abaixo. Este spec liga esses leitores à seção.

Ler o código antes de propor mudou o quadro, e `## Design` abre com ele: dos três leitores que
`## Problem` nomeia, só dois olham para dentro de um spec, e o terceiro — `/specs:continue` — não abre
arquivo nenhum, por invariante publicado. Então a ligação não é a mesma coisa feita em três lugares; é
uma substituição, um acréscimo de entrada e um acréscimo de saída. A forma recomendada aproveita que a
ferramenta `specs.py` já abre cada arquivo e já separa cada seção: levar a orientação dentro dos dados
que os comandos **já** pedem custa uma linha de código e nenhuma chamada nova, e é a única forma que
não obriga `/specs:continue` a desmentir a própria descrição. `## Impact` mostra que isso cabe em um
arquivo de ferramenta, três de prosa e um manual, sem tocar em nada do contrato parseado de seções.

O resto do spec é sobre o que fazer quando a orientação não está lá, que é a maioria dos casos hoje.
A regra é uma só — sem orientação, cada leitor faz exatamente o que faz hoje — porque a ausência não é
uma migração inacabada: todo spec nasce sem a seção, e `## Problem` traz a contagem medida.
`## Out of Scope` guarda o que a regra deliberadamente não faz: escrever a seção, detectar quando ela
envelheceu, mexer no gate, encostar no listing que outro spec está decidindo se sobrevive.
`## Alternatives Considered` guarda a alternativa que quase venceu — não fazer nada, porque hoje
pouquíssimos specs têm orientação de verdade escrita — e `## Risks` a registra como a aposta central,
ao lado da razão de ela não ser fatal: o caminho antigo nunca é removido, e desfazer tudo é apagar um
campo. `## Open Decisions` deixa em aberto só o que uma medição vai decidir, e `## Validation` faz essa
medição, usando este próprio arquivo como fixture do caso em que há orientação para ler.
## Problem

`/specs:triage`, `/specs:continue` e o approval bank de `/specs:develop` são os três lugares onde um
humano pergunta "do que este spec trata" e recebe uma resposta curta. Nenhum dos três lê a seção que
existe para responder isso. Dois deles remontam a resposta a cada execução a partir das seções
densas do spec — `/specs:triage` abrindo cada arquivo e lendo as primeiras linhas de `## Problem`, o
approval bank recomprimindo `## Proposal` em uma linha — e o terceiro, `/specs:continue`, não mostra
resposta nenhuma: por invariante publicado ele não abre arquivo de spec, então tudo que exibe é
`title`, stage, progresso e uma razão de ranking montada pela ferramenta.

`## Overview` existe agora exatamente para isso: uma orientação escrita por humano, primeira no
arquivo, atualizada por todo bank de `/specs:develop`, e o único lugar da frente onde essa frase
pode ser corrigida em vez de refeita. A pré-condição está atendida e os consumidores continuam
desconectados — mas o quanto ela está atendida é modesto, e o número importa para decidir se vale:
medido no HEAD `e4e3922`, dos 32 specs em `plans/` **3 carregam prosa real**, 27 carregam um `- none`
explícito com razão (o backfill honesto de um spec que ainda não tinha nada a conectar) e 2 não
carregam a seção — porque `specs.py new` estampa `## Problem` sozinho, e todo spec nasce assim.

A conexão foi deixada fora do escopo de add-eli5-section-to-specs deliberadamente: o backfill
*habilita* o trabalho, mas estabelece ordenação, não pertinência, e a conexão responde a um problema
diferente do que ele estava resolvendo. Este é aquele problema diferente.

O que precisa ser decidido: o que cada consumidor faz quando o `## Overview` de um spec é um `- none`
explícito ou está ausente — e se ler a seção vale os tokens em `/specs:continue`, que hoje é quase
gratuito por construção e faz exatamente uma chamada de ferramenta.
## Proposal

Depois deste spec:

- `specs.py` carrega a orientação do spec nos payloads que os comandos **já** buscam — um campo
  `overview` por candidato em `next --front`, e o mesmo campo em `next --spec` e em `status` —
  preenchido a partir do corpo de `## Overview` que `parse_sections` já devolve. Nenhuma leitura de
  arquivo nova, nenhuma chamada de ferramenta nova.
- O campo vale `null` quando não existe orientação utilizável: seção ausente, presente-e-vazia, ou
  um `- none` explícito. O teste do `- none` mora na ferramenta, em um lugar só, e não replicado em
  cada consumidor.
- `/specs:continue` mostra a linha de orientação junto do candidato do topo, com os seus dois
  invariantes publicados intactos: uma única chamada e nenhuma leitura de arquivo.
- `/specs:triage` recebe `## Overview` no payload que já pede e o usa **junto** das primeiras linhas
  de `## Problem`, nunca em lugar delas. A coluna Reason continua justificando a **posição** no
  ranking, e urgência é coisa que `## Problem` diz e `## Overview` deliberadamente não diz.
- O approval bank de `/specs:develop` apresenta o `## Overview` que ele mesmo acabou de atualizar,
  em vez de recomprimir `## Proposal` em uma linha.
- Nenhum consumidor degrada, recusa, avisa ou roteia por causa de uma orientação ausente.
  `## Overview` é **aditivo, nunca substitutivo**, nos três: cada um produz hoje uma resposta
  completa sem ele, e continua produzindo.
- Um campo ausente no payload e um campo `null` são tratados igual pelos três corpos de comando, de
  modo que um `specs.py` instalado mais antigo, que não conhece o campo, não faz nenhum deles
  afirmar que um spec não tem orientação.
- Nenhuma mudança no schema, no gate `ready`, na ordem canônica ou no conjunto de seções — logo
  nenhum arquivo do lockstep de contrato parseado (`assets/specs/schema.json`, o `DEFAULT_SCHEMA`
  duplicado, os dois templates) é tocado, e `specs.py selftest` prova a mesma igualdade que provava
  antes.
- Um leitor que abre `/specs:continue` num repo cujos specs foram desenvolvidos vê do que cada um
  trata sem abrir arquivo nenhum; num repo cujos specs não foram, vê exatamente o que vê hoje.
## Out of Scope

- **Gerar um `## Overview` quando falta.** A autoria é do shape bank de `/specs:develop`;
  `/specs:align` apenas reporta `sp-overview-missing` e roteia, por
  `docs/standards/architecture/align-surface.md`. Um consumidor que escrevesse a seção quebraria o
  contrato "reportado, nunca executado" que a superfície de align publica na própria descrição.
- **Detectar um `## Overview` obsoleto.** add-eli5-section-to-specs já rejeitou isso como
  impossível para estas ferramentas — Python stdlib sem modelo — e o máximo que dariam é um hash do
  corpo no momento da escrita, um aviso sobre o qual ninguém age sem reescrever o texto à mão. Fica
  registrado em `## Risks` como risco aceito, não como trabalho.
- **A zona GENERATED de `specs/plans/index.md`.** Quarto candidato a consumidor, e o único fora dos
  três nomeados: `render_plans_zone` (`plugins/quenching/assets/bin/specs.py:2927`) monta
  `| Spec | Title | Since |` a partir do `title` do frontmatter e nunca leu corpo de seção nenhum.
  Deixado de fora porque o spec irmão `decide-plans-index-need` está decidindo se a zona continua
  existindo — acrescentar uma coluna a um arquivo cuja existência está em revisão é trabalho que
  pode ser jogado fora.
- **`/specs:status`.** Não renderiza prosa de corpo nenhuma, por projeto: a sua tabela é
  `Spec | Stage | Tasks | Records | Age | State`, montada de frontmatter e de payloads da
  ferramenta. Não há renderização para substituir, e acrescentar uma seria alargar o escopo de um
  comando cujo valor declarado é ser quase gratuito.
- **Tornar `## Overview` parte do gate `ready`.** `warnWhenEmpty: [Overview, Handoff]` em
  `plugins/quenching/assets/specs/schema.json` mantém a seção como aviso. Um consumidor que
  degradasse sem ela faria uma seção warn-only agir como gate por via indireta, que é exatamente o
  efeito retroativo que add-eli5-section-to-specs evitou.
- **Os specs em `specs/archive/`.** Carregam `## Outcome`, um registro do que aconteceu de fato —
  orientação melhor que uma reconstruída, e já escrita. O backfill original também os deixou de
  fora, pela mesma razão.
- **O bump de versão.** O lockstep de seis artefatos é liquidado por `/specs:conclude`
  imediatamente antes do merge, e `docs/standards/ci-cd/versioning-release.md` diz literalmente
  "never as a task".

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/code/optional-payload-fields.md` — um campo opcional de payload de ferramenta é
  lido como ausente-ou-`null` e nunca como fato, porque uma cópia instalada mais antiga da ferramenta
  simplesmente não o emite; irmão de `canonical-set-parsing.md` e `frontmatter-parsing.md` no mesmo
  subject folder

Uma segunda regra candidata — que o orçamento de custo declarado de um roteador é vinculante para
quem vier depois — **não** é declarada aqui: tem um caso só, o que a torna background e não standard.
Ver `## Open Decisions`.

### Product code this spec expects to touch

- `plugins/quenching/assets/bin/specs.py` — o detector de explicit-none para corpo de seção, e o campo
  `overview` em três payloads: `next --spec` e `status` (corpo inteiro) e `next --front` (primeira
  frase, com teto)
- `plugins/quenching/commands/specs/continue.md` — passa a exibir a orientação do candidato do topo;
  os dois invariantes de custo ficam **intactos**, porque nada de novo é lido
- `plugins/quenching/commands/specs/triage.md` — §1 e a bullet de Doctrine que hoje nomeiam as
  primeiras linhas de `## Problem` como a entrada do raciocínio de ranking
- `plugins/quenching/assets/references/specs-develop/questions.md` — §Bank: approval, onde vive a
  instrução "the proposal in one line". É aqui, e não em `commands/specs/develop.md`, que o terceiro
  consumidor é escrito, e o arquivo é referência compartilhada citada por outros comandos
- `plugins/quenching/assets/specs/QUENCHING.md` — §4 `/specs:continue`, o manual do operador que
  instala em todo repo adotante e hoje descreve o router como "a one-line reason per row"
- `docs/standards/code/index.md` — a linha de listagem do doc novo

Nada em `plugins/quenching/assets/specs/schema.json`, no `DEFAULT_SCHEMA` de `specs.py`, nos dois
templates ou em `specs/plans/index.md`. O conjunto canônico de seções não se move, então o lockstep de
três cópias não é acionado, e a zona GENERATED do listing não é tocada por causa de
`decide-plans-index-need`.

O bump dos seis artefatos de versão é obrigação de release liquidada por `/specs:conclude`
imediatamente antes do merge, e por isso não aparece como task — `docs/standards/ci-cd/versioning-release.md`
diz "never as a task".

A sub-heading do meio (`authority: background`) está deliberadamente ausente: a checagem é opt-in por
escrever a heading, e este spec não promove doc nenhum.

## Validation

Rodar de `plugins/quenching/` salvo onde o caminho disser outra coisa. **Este spec é o próprio
fixture** do caso positivo: ele carrega prosa real em `## Overview` e nenhum outro fixture de leitura
de `## Overview` existe no repo. Os casos negativos são resolvidos **em tempo de execução**, por
regra e não por lista — quais specs carregam `- none` muda a cada sessão de `/specs:develop`, e uma
lista escrita agora já estaria errada na hora de construir.

**As três asserções pelas quais este spec existe.**

- **O campo distingue orientação de explicit-none.** Contra este spec o campo tem texto que começa
  pela primeira frase do seu `## Overview`; contra qualquer spec cujo `## Overview` seja um `- none`
  explícito, ou que não carregue a heading, o campo é `null`. Uma varredura, três classes:

  ```bash
  python3 - <<'PY'
  import glob, json, re, subprocess
  T = ["python3", "plugins/quenching/assets/bin/specs.py", "status", "--spec"]
  for f in sorted(glob.glob("specs/plans/*.md")):
      m = re.match(r"\d{4}-\d{2}-\d{2}-(.+)\.md$", f.rsplit("/", 1)[-1])
      if not m:
          continue
      slug = m.group(1)
      d = json.loads(subprocess.run(T + [slug, "--json"], capture_output=True, text=True).stdout)
      body = json.loads(subprocess.run(
          ["python3", "plugins/quenching/assets/bin/specs.py", "section", slug, "Overview", "--json"],
          capture_output=True, text=True).stdout)
      prose = body["state"] == "filled" and not body["body"].strip().startswith("- none")
      field = d.get("overview")
      if prose != bool(field):
          print("DIVERGE:", slug, "prosa" if prose else "sem prosa", repr(field)[:60])
      if field and field not in body["body"]:
          print("RECUO ERRADO:", slug, "campo nao sai de ## Overview")
  PY
  ```
  A varredura não imprime nada. Uma linha `DIVERGE` é o detector de explicit-none errado; uma linha
  `RECUO ERRADO` é o campo tendo aterrissado em outra seção.

- **`/specs:continue` continua quase gratuito.** O payload de `next --front` cresce apenas pelo teto
  declarado, e nenhum candidato passa dele. Medir, não estimar:

  ```bash
  python3 assets/bin/specs.py next --front --json | wc -c
  python3 assets/bin/specs.py next --front --json \
    | python3 -c "import json,sys; c=json.load(sys.stdin)['candidates']; \
      o=[x.get('overview') or '' for x in c]; \
      print(len(c), 'candidatos', max((len(t) for t in o), default=0), 'chars no maior', sum(map(len,o)), 'chars somados')"
  ```
  Nenhum valor acima de 200 caracteres, e a soma é o número que decide o corte de
  `## Open Decisions`. Registrar a contagem de bytes de **antes** da mudança, na primeira task, para
  ter com o que comparar.

- **O gate não se moveu e o conjunto canônico não se moveu.** `## Overview` continua warn-only e
  continua na posição 1: um spec sem a heading reporta o mesmo `stage` e o mesmo `ready.ok` de antes,
  e `selftest` continua provando que as três cópias do conjunto concordam.

  ```bash
  python3 assets/bin/specs.py selftest
  python3 assets/bin/specs.py validate --json     # nenhum finding novo
  ```

**Os gates de rotina, todos ainda passando.**

- `python3 assets/bin/specs.py validate --json` — nenhum finding novo, e o comportamento de
  `sp-overview-missing` idêntico ao de antes: ele só olha ausente-ou-vazio, e o campo novo não muda
  isso
- `python3 assets/bin/skills.py --root . doctor --json` — **26 commands, no findings**. Este spec não
  cria entry point nenhum, então a contagem tem de ficar igual; se subir, algo virou comando sem
  querer
- `python3 assets/hooks/okf-validate.py docs` (da raiz do repo) — o doc novo de `docs/standards/code/`
  conformante e a sua linha de listagem em `docs/standards/code/index.md` presente, sem
  `index-broken-link` nem `index-orphan`
- `python3 assets/hooks/okf-validate.py assets/docs` e
  `python3 assets/hooks/okf-validate.py assets/specs/plans --listing-root` — 0 errors, 0 warnings

**O que deliberadamente NÃO está aqui.** `./assets/bin/functional-checks.sh` não entra em
`## Validation` nem em nenhum `verify:`, por instrução explícita do `CLAUDE.md` deste repo: o harness
pertence à frente skill, cada checagem é uma sessão de agente cobrada, e medido no arquivo inteiro
toda execução vermelha que ele já produziu foi defeito dele mesmo e nenhuma foi regressão de
superfície. Três corpos de comando mudam neste spec, então a checagem devida é `/skill:new` sobre cada
um depois da edição, e `/skill:eval` se alguma descrição for ajustada — nomeados no relatório de
`/specs:conclude`, não como task aqui. (add-eli5-section-to-specs listou o harness em `## Validation`;
aquela regra do `CLAUDE.md` é posterior.)
## Design

**O inventário real, lido no código, não no `## Problem`.** Os três "consumidores" não fazem a
mesma coisa, e apenas dois deles remontam algo a partir de um corpo de spec:

| Consumidor | O que lê de um spec hoje | O que renderiza hoje | O que a conexão muda |
| --- | --- | --- | --- |
| `/specs:triage` | frontmatter + as primeiras linhas de `## Problem`, arquivo por arquivo (`commands/specs/triage.md` §1 e §Doctrine) | uma linha de razão **por posição no ranking** | acrescenta `## Overview` à entrada, sem tirar `## Problem` |
| `/specs:continue` | **nada** — os invariantes proíbem ler arquivo de spec, e todo o output vem de um único `specs.py next --front --json` | `title`, stage, progresso e o `reason` montado por `_rank_reason()` (`assets/bin/specs.py:1929`) a partir de branch, stage, priority e idade | acrescenta informação que hoje não existe ali |
| approval bank de `/specs:develop` | `## Proposal`, `## Tasks`, `verification`, `## Impact`, `## Risks` (`assets/references/specs-develop/questions.md` §Bank: approval) | "the proposal in one line" mais o resumo do compromisso | substitui a recompressão pelo `## Overview` que o próprio bank acabou de atualizar |
| `render_plans_zone` | só o `title` do frontmatter (`assets/bin/specs.py:2927`) | `\| Spec \| Title \| Since \|` | fora de escopo, ver `## Out of Scope` |

Isso corrige a premissa original de `## Problem`: não há três renderizações independentes divergindo
entre si. Há **uma** substituição, **um** acréscimo de entrada e **um** acréscimo de saída. A conexão
continua valendo, mas o seu valor é "cada leitor passa a ter uma relação definida com
`## Overview`" — e para um deles essa relação é deliberadamente não abrir arquivo nenhum.

**Onde o campo nasce: dentro de `_candidate`, de graça.** `_candidate()`
(`assets/bin/specs.py:1895`) já lê o arquivo inteiro (`read_text`) e já chama
`parse_sections(body_after_frontmatter(raw))` na linha 1898. E `parse_sections`
(`assets/bin/specs.py:1036`) já devolve `body` — o texto do corpo — em cada entrada, ao lado de
`lines`, `lineno` e `filled`. Logo `sections["Overview"]["body"]` está em mão no momento em que o
candidato é montado. O custo marginal é uma entrada de dicionário, e não uma abertura de arquivo.
Esse é o fato de engenharia que decide a forma inteira do spec: `load_spec`, que serve
`next --spec` e `status`, faz o mesmo trabalho pelo mesmo caminho.

**Lido por pertinência, nunca por posição.** O acesso é pela chave da heading em `sections`, e não
por índice na lista canônica — o que `docs/standards/code/canonical-set-parsing.md` (`authority:
current`, escrito pelo próprio add-eli5-section-to-specs depois de `specs.py new` quebrar por leitura
posicional) exige. `## Overview` estar na posição 1 é irrelevante para este código, e tem de
continuar irrelevante.

**Por que a ferramenta, e não cada corpo de comando.** `commands/specs/continue.md` publica na
descrição "One tool call, no sub-agents, no file reads", e repete como invariante: "Never read a
spec file, run a second `specs.py` subcommand, or dispatch a sub-agent. One call." Qualquer forma em
que o comando lê o arquivo torna a própria descrição falsa — e a descrição é o que roteia o
trabalho. Colocar o campo no payload é a única forma que respeita o contrato publicado em vez de
renegociá-lo. Esse orçamento de custo está declarado só no corpo do comando, e em nenhum doc de
`docs/standards/`; ver `## Open Decisions`.

**O `- none` explícito é filtrado na ferramenta, uma vez.** `has_real_content()`
(`assets/bin/specs.py:909`) devolve `True` para `- none` — a regra do explicit-none depende disso —
e `section_state()` então chama a seção de `filled`. Ou seja: `filled` **não** distingue "existe
orientação" de "alguém declarou que não existe". A mesma assimetria explica por que
`sp-overview-missing` (`assets/bin/specs.py:2526`) não dispara nos 27 specs com `- none`: ele só olha
`ready["warn"]`, que é ausente-ou-vazio. Um detector de explicit-none para corpo de seção não existe
hoje em `specs.py` (`RECORD_NONE_RE` só serve para linhas `subject:`), então ele é escrito uma vez e
usado pelos três consumidores através do campo.

**Ausência é estrutural e permanente, não uma cauda legada.** `specs.py new` estampa o frontmatter e
o `## Problem` sozinho, por decisão — o entry gate da fase `plans` é `Problem`. Todo spec novo nasce
portanto **sem** `## Overview`, e continua sem até o primeiro shape bank. Medido no HEAD `e4e3922`
sobre `specs/plans/`: 27 com `- none` explícito, 3 com prosa real, 2 sem a seção — e os 2 são
`wire-the-overview-consumers` e `narrow-the-stale-doc-trigger-to-content-drift`, ambos criados em
2026-07-29, depois do backfill. O recuo não é uma migração a ser terminada; é o estado normal de todo
spec recém-capturado, para sempre.

**Aditivo, nunca substitutivo — e uniforme nos três.** Sem orientação, cada consumidor faz
exatamente o que faz hoje. Nada avisa, nada recusa, nada roteia para `/specs:develop`. Três razões, e
a terceira foi a que mudou a forma do spec durante a crítica: um consumidor que degradasse
transformaria uma seção `warnWhenEmpty` em gate por via indireta; `/specs:continue` já é o roteador,
e dizer "vá desenvolver este spec" quando a pergunta era "o que eu faço agora" troca uma resposta por
um recado; e em `/specs:triage` a substituição seria uma **piora**, não uma economia — o ranking
precisa da urgência, que `## Problem` diz e que uma orientação, por registro, deliberadamente não
diz.

**Campo ausente e campo `null` são a mesma decisão de leitura.** Um `specs.py` instalado em
`.claude/hooks/` mais antigo que este spec simplesmente não emite a chave. Os três corpos tratam
"chave ausente" e `null` do mesmo jeito — sem orientação, siga o caminho de hoje — de modo que um
repo com ferramenta atrasada perde o ganho e não ganha uma afirmação falsa. Os dois fatos são
diferentes, e a distinção não interessa a nenhum dos três: nenhum deles reporta versão de ferramenta,
e a deriva em si é do spec já mergeado `notice-installed-tool-version-drift`.

**Corte de comprimento, por payload.** `next --front` carrega a **primeira frase** do `## Overview`,
com teto de 200 caracteres e elipse, porque devolve um candidato por spec ativo e `/specs:continue`
tem de continuar quase gratuito. `next --spec` e `status` carregam o corpo inteiro: são um spec por
chamada, e quem os chama já está lendo o spec.

**Nenhum contrato parseado se move, e a reversão é apagar um campo.** O conjunto de seções, a ordem
canônica, os stages derivados e o gate `ready` ficam idênticos, então o lockstep de três cópias que
add-eli5-section-to-specs pagou não aparece aqui. Desfazer em um mês custa remover um campo de
payload e reverter três parágrafos de prosa de comando: nenhum arquivo de spec é reescrito, nenhuma
migração é devida, nada em `archive/` é tocado. É a reversão mais barata da frente hoje, e isso é
parte da razão de o spec ser aceitável mesmo com a suposição carregadora de `## Risks` em aberto.
## Alternatives Considered

- **Cada corpo de comando lê o arquivo por conta própria, com a tool `Read`.** A forma mais óbvia, e
  a única que não precisa de mudança em `specs.py`. Rejeitada: `commands/specs/continue.md` declara
  na descrição e nos invariantes uma chamada e zero leituras de arquivo, então essa forma exige
  reescrever o contrato publicado do comando mais executado da frente. Em `/specs:triage` ela até
  serve — o comando já abre todo spec — mas duas formas diferentes para o mesmo dado significa dois
  testes de `- none` e duas regras de recuo.
- **Um subcomando novo, `specs.py overview` por slug.** Uniforme, explícito, fácil de testar.
  Rejeitada: é uma chamada de ferramenta por spec, e `/specs:continue` tem orçamento de uma chamada
  para a frente inteira. Um subcomando cujo único chamador viável seria o approval bank não paga uma
  entrada permanente na superfície da ferramenta.
- **Não fazer nada — retirar a premissa.** A alternativa mais forte, e a que quase ganhou: no HEAD
  apenas 3 de 32 specs carregam prosa real de `## Overview`, então a conexão renderia `null` em 91%
  da frente e o trabalho seria peso morto. Rejeitada por três razões: o custo é de poucas linhas
  dentro de um caminho de código já aberto; `- none` é barato de filtrar; e a proporção é função de
  quantos specs foram desenvolvidos, que só cresce. Registrada em `## Risks` como a suposição
  carregadora, com o gatilho honesto de não-vale-a-pena.
- **A menor coisa que funciona: conectar só `/specs:triage`.** É o consumidor que de fato abre todo
  arquivo de spec e o único cujo custo cai ao usar `## Overview` em vez das primeiras linhas de
  `## Problem`. Rejeitada por pouco — o campo no payload serve os três pelo mesmo preço, então
  parar em um economiza prosa de comando, não código. Sobrevive em `## Open Decisions` como o corte
  a tomar se o peso do payload incomodar.
- **O campo carrega o corpo cru e cada consumidor testa o `- none`.** Mais simples na ferramenta.
  Rejeitada: três implementações do mesmo teste, em prosa de comando, onde nada as verifica — e a
  primeira que divergir produz exatamente a discordância entre renderizações que este spec existe
  para acabar.
- **Fazer `## Overview` gatear o `ready`, para garantir que sempre exista.** Rejeitada, e não é uma
  decisão nova: add-eli5-section-to-specs já mostrou que um gate a mais des-prontifica
  retroativamente todo spec de todo repo alinhado no instante em que o schema embarca, e que
  `- none` satisfaria o gate derrotando o propósito da seção.
- **A ferramenta gera a orientação quando falta.** Rejeitada como impossível, não como indesejável:
  as três ferramentas são stdlib sem modelo. Um listing se deriva de frontmatter; uma orientação
  não.
- **Rotear para `/specs:develop` quando falta.** Rejeitada para `/specs:continue`, que é ele mesmo o
  roteador: trocaria a resposta à pergunta "o que eu faço agora" por um recado sobre o arquivo.
  Também discutível em `/specs:triage`, cuja descrição o compromete a escrever o registro
  `priority` "and nothing else".

## Open Decisions

- **O orçamento de custo de `/specs:continue` é um contrato publicado, e não está em
  `docs/standards/`.** "One tool call, no sub-agents, no file reads" vive só na descrição e nos
  invariantes de `commands/specs/continue.md`; nenhum doc de `docs/standards/` declara que o custo
  declarado de um roteador é vinculante para quem vier depois. Este spec é o primeiro a projetar em
  volta dessa restrição em vez de negociá-la, então é o primeiro candidato a prová-la como regra.
  **Como se decide:** o corpo de `/specs:continue` continua sendo a única fonte enquanto esta for a
  única evidência; um segundo spec que precise contornar o mesmo orçamento é o gatilho para promovê-la
  a `docs/standards/`, via `/docs:add`. Não é declarada em `## Impact` porque uma regra com um caso
  só é background, não standard.
- **Se o peso do payload de `next --front` incomodar, o corte é parar em `/specs:triage`.** É o
  consumidor que já abre todo arquivo de spec e o único cujo custo *cai* ao receber a orientação no
  payload. **Como se decide:** pela medição que `## Validation` já faz — o tamanho do payload de
  `next --front` antes e depois. Se o crescimento passar de algo que um humano note na latência de
  `/specs:continue`, a task do campo em `next --front` sai e as outras duas ficam. A decisão é da
  medida, não do gosto.
- **Quem escreve a orientação de um spec que nunca vai ser desenvolvido continua sem resposta, e este
  spec não a dá.** Um spec capturado e nunca interrogado fica com `null` para sempre, e os três
  consumidores mostrarão sempre o recuo. **Como se decide:** não por este spec — a autoria é de
  `/specs:develop` e o reporte é de `/specs:align` via `sp-overview-missing`, e mudar isso mexeria no
  contrato "reportado, nunca executado" da superfície de align. Fica registrado aqui para que a
  ausência não seja relida depois como omissão deste spec.

## Risks

- **A suposição carregadora: que uma orientação escrita por humano vale mais que a que um comando
  remonta.** Se o `## Overview` for um `- none`, ou tiver envelhecido, a linha remontada a partir de
  `## Problem` é mais fresca — e a conexão inteira perde o sentido. Probabilidade média, gravidade
  média, detecção nenhuma. **Mitigação real, e é estrutural:** o caminho de remontagem nunca é
  removido, então a suposição sustenta o *valor* do spec e nunca a sua *correção*. Nenhum consumidor
  fica pior do que hoje se ela for falsa.
- **`## Overview` obsoleto agora fala com autoridade em três lugares.** Um enquadramento errado
  repetido por três comandos é pior que um enquadramento errado guardado em um arquivo que ninguém
  abre. Probabilidade média, gravidade média, **detecção nenhuma — este é o risco silencioso.**
  `ACCEPTED — ` add-eli5-section-to-specs já aceitou exatamente este risco ao escolher a regra de
  refresh em vez de detecção de deriva, e mostrou que as ferramentas, sendo stdlib sem modelo, não
  conseguem julgar obsolescência semântica. A regra de escrever `## Overview` por último dentro de
  cada edição de bank é a contramedida existente, e é a que há.
- **Quatro specs irmãos editam `specs.py` em paralelo.** `split-specs-py-backlog-renderer`,
  `dedupe-specs-py-spec-reader`, `add-specs-py-record-writer` e `name-the-scaffolded-stage` mexem no
  mesmo arquivo, e `dedupe-specs-py-spec-reader` mexe exatamente no caminho ler-parsear-derivar de que
  este design depende. Probabilidade alta, gravidade baixa a média, detecção alta em conflito de
  merge e **baixa** se o dedupe entrar primeiro e o campo passar a ser preenchido por outro helper.
  **Mitigação:** as tasks nomeiam o comportamento (o campo aparece nos três payloads, `null` quando
  não há orientação) e não o número de linha nem o nome do helper, e `## Validation` afirma o campo a
  partir do payload, que é o contrato que interessa. Se o helper compartilhado já existir quando este
  spec for construído, o campo nasce lá e a task encolhe.
- **`/specs:continue` deixa de ser quase gratuito.** Uma primeira frase por candidato, vezes 32
  specs ativos, é um custo mensurável no payload do comando mais executado da frente. Probabilidade
  média, gravidade média, detecção nenhuma sem medição. **Mitigação:** o teto de 200 caracteres é uma
  decisão de design com número, e `## Validation` mede o tamanho do payload antes e depois em vez de
  confiar na estimativa.
- **O spec meio-aterrissa: a ferramenta ganha o campo e os corpos de comando não, ou o contrário.**
  Nada quebra visivelmente em nenhuma das duas metades — o campo fica sem leitor, ou os corpos leem
  uma chave que ninguém emite e caem no recuo para sempre. Probabilidade média, gravidade baixa,
  **detecção nenhuma**, porque é indistinguível do caso legítimo de ferramenta atrasada.
  **Mitigação:** a ordem das tasks é ferramenta primeiro, três corpos depois, e a asserção de
  `## Validation` roda os três caminhos de leitura contra este próprio spec, cujo `## Overview` tem
  prosa real — de modo que um recuo silencioso aparece como ausência de orientação num spec que
  comprovadamente a tem.
- **Um campo novo de payload é contrato permanente.** Depois de emitido, outros comandos e outros
  repos podem passar a depender dele, e removê-lo deixa de ser grátis. Probabilidade baixa,
  gravidade baixa. `ACCEPTED — ` os payloads de `specs.py` já são o contrato por onde todo comando
  desta frente lê estado, `--json` é declarado em todo subcomando, e um campo opcional lido como
  ausente-ou-`null` é a forma que já sobrevive a deriva de versão instalada.
- **Sobreposição com `decide-plans-index-need`.** Aquele spec decide se a zona GENERATED de
  `specs/plans/index.md` continua existindo; este deixa `render_plans_zone` explicitamente fora de
  escopo por isso. A fronteira que este spec mantém: nada em `plans/index.md` é tocado, e nenhuma
  coluna é acrescentada à zona, aconteça o que acontecer com aquela decisão. Se aquele spec retirar a
  zona, este não perde nada; se a mantiver, ligá-la a `## Overview` é um terceiro spec e não uma
  task escondida aqui.
- **Sobreposição com `name-the-scaffolded-stage`.** Aquele spec propõe nomear o estado "spec existe e
  ninguém escreveu o problema ainda", que é o mesmo estado em que `## Overview` também está ausente.
  A fronteira que este spec mantém: o recuo aqui é por **seção ausente ou explicit-none**, lido de
  `sections`, e não por stage derivado — então ele funciona igual antes e depois daquela decisão, e
  este spec não propõe stage nenhum.

## Tasks

### 1. A ferramenta

- [ ] 1.1 Registrar a linha-base de custo: os bytes de `next --front --json` e de `status --json`
      antes de qualquer mudança, anotados em `## Handoff`, porque a asserção de custo de
      `## Validation` compara com um número que só existe agora
      verify: python3 assets/bin/specs.py next --front --json | wc -c
- [ ] 1.2 Detector de explicit-none para corpo de seção, em um lugar só — reconhece `- none` como
      declaração-de-ausência e não como conteúdo, sem tocar em `has_real_content()`, de que a regra
      do explicit-none depende
      files: plugins/quenching/assets/bin/specs.py
      pattern: a função `has_real_content()` no mesmo arquivo
      verify: python3 assets/bin/specs.py selftest
- [ ] 1.3 Campo `overview` nos payloads de `status --spec` e `next --spec` — corpo inteiro de
      `## Overview`, `null` quando ausente, vazio ou explicit-none; lido por chave de heading em
      `sections` e nunca por posição, per docs/standards/code/canonical-set-parsing.md
      files: plugins/quenching/assets/bin/specs.py
      verify: a varredura de três classes em `## Validation` não imprime nada
- [ ] 1.4 Campo `overview` por candidato em `next --front` — primeira frase, teto de 200 caracteres
      com elipse, `null` pelas mesmas três razões
      files: plugins/quenching/assets/bin/specs.py
      verify: a medição de payload em `## Validation`, nenhum valor acima de 200

### 2. Os três consumidores

- [ ] 2.1 `/specs:continue` exibe a orientação do candidato do topo a partir do campo, tratando
      chave-ausente e `null` do mesmo modo; os dois invariantes de custo ficam textualmente
      intactos, porque nada novo é lido
      files: plugins/quenching/commands/specs/continue.md
- [ ] 2.2 `/specs:triage` usa `## Overview` **junto** das primeiras linhas de `## Problem` como
      entrada do raciocínio de ranking, nunca em lugar delas — §1 e a bullet de Doctrine
      files: plugins/quenching/commands/specs/triage.md
- [ ] 2.3 O approval bank apresenta o `## Overview` recém-atualizado em vez de recomprimir
      `## Proposal` em uma linha, com o recuo para a recompressão quando o campo é `null`
      files: plugins/quenching/assets/references/specs-develop/questions.md
- [ ] 2.4 §4 de `assets/specs/QUENCHING.md` descreve o router como mostrando a orientação além da
      razão de ranking — o manual do operador instala em todo repo adotante
      files: plugins/quenching/assets/specs/QUENCHING.md

### 3. O standard

- [ ] 3.1 Escrever docs/standards/code/optional-payload-fields.md — um campo opcional de payload é
      lido como ausente-ou-`null` e nunca como fato, porque uma cópia instalada mais antiga da
      ferramenta não o emite (authority: current, uma vez provado pelas tasks 1.3/1.4 e 2.1)
      files: docs/standards/code/optional-payload-fields.md, docs/standards/code/index.md
      pattern: docs/standards/code/canonical-set-parsing.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs

### 4. Verificação

- [ ] 4.1 Rodar as três asserções de `## Validation` e os gates de rotina, comparando a medição de
      custo com a linha-base da task 1.1 — e registrar o número somado, que é o que decide o corte
      de `## Open Decisions`
      verify: python3 assets/bin/specs.py selftest && python3 assets/bin/specs.py validate --json && python3 assets/bin/skills.py --root . doctor --json
