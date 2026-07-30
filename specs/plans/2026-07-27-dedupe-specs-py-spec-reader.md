---
slug: dedupe-specs-py-spec-reader
title: Fold the four copies of read-parse-derive in specs.py into one helper
verification: per-section
priority: {level: 24, criticality: medium, complexity: 5, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# Fold the four copies of read-parse-derive in specs.py into one helper

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

`specs.py` é o script que dá trilhos determinísticos ao front `specs/`: ele lê um arquivo de spec do
disco e responde o que aquele spec é — quais seções existem, em que estágio ele está, quantas
tarefas foram fechadas. Esta spec não muda nenhuma dessas respostas. Ela muda **quantos lugares no
script sabem como produzi-las**.

`## Problem` conta o que foi medido no código, e corrige a contagem com que esta spec foi capturada:
são cinco funções que fazem a mesma leitura, e uma delas — `load_spec` — já é a leitora
compartilhada que os sete comandos de spec único usam. As outras quatro a contornam, e há um motivo
técnico para isso que decide a forma da solução. `## Proposal` descreve o estado final; `## Design`
explica por que a correção é *dividir* `load_spec` em duas metades em vez de escrever uma função
nova ao lado dela, e `## Alternatives Considered` guarda as formas que perderam.

Como nada no comportamento observável muda, `## Validation` não pede teste novo: ela pede que a saída
`--json` de todos os comandos de leitura seja byte a byte idêntica antes e depois, mais duas
assertivas numéricas com linha de base medida e uma mutação deliberada que prova que a comparação não
é vácua. `## Risks` trata disso mais do que do refactor — a maior parte do que pode dar errado aqui é
a rede de verificação mentir, não o código quebrar.

`## Impact` fecha uma tentação: este refactor **não** escreve standard nenhum, e a razão está medida
lá. `## Tasks` tem nove itens em três seções — capturar a linha de base, mover as cinco funções, e
provar que a rede funciona — e `## Open Decisions` guarda as três perguntas que esta spec
deliberadamente não responde.

## Problem

Cinco funções de `specs.py` transformam um caminho em uma visão utilizável de um spec, repetindo a
mesma sequência: `read_text` → `parse_frontmatter` → `parse_sections(body_after_frontmatter(...))`
→ `parse_tasks` → `derive_stage`.

Contadas no código (`plugins/quenching/assets/bin/specs.py`, 3.125 linhas):

| Função | Linhas | Deriva o estágio? |
| --- | --- | --- |
| `load_spec` | 1253–1282 | sim, L1279 — sem `schema` |
| `cmd_list` | 1415–1424 | sim, L1424 — sem `schema` |
| `_candidate` | 1896–1902 | sim, L1901 — **com** `schema` |
| `validate_spec` | 2463–2466 | **não** — vai direto a `gate_report`/`ready_report` |
| `cmd_plans` | 2962–2968 | sim, L2967 — sem `schema` |

Duas correções em relação ao que esta spec afirmava quando foi capturada. A contagem não é quatro:
são **cinco** leitoras, e a lista original (`cmd_list`, `validate_spec`, `cmd_plans`, `_candidate`)
misturava dois conjuntos diferentes — incluía `validate_spec`, que nunca chama `derive_stage`, e
omitia `load_spec`, que é **exatamente a leitora compartilhada que a spec propunha inventar**.
`load_spec` já existe e já serve sete comandos: `cmd_status` (L1458), `cmd_section` (L1576),
`cmd_promote` (L1641), `cmd_task` (L1747), `cmd_next` (L2028), `cmd_parallel` (L2108) e
`cmd_discover` (L2149).

O enquadramento honesto, então, não é "quatro cópias": é **uma leitora canônica e quatro que a
contornam**.

Por que elas a contornam — e isso é a restrição real do problema: `load_spec(root, slug)` recebe um
**slug**, não uma linha de diretório. Ela chama `resolve_slug`, que varre `spec_files(root)` inteiro
e **recusa com exit 2 (`sp-ambiguous-slug`, L1259–1265) quando dois arquivos batem**. As quatro
contornadoras já têm a linha em mãos, porque varrem o front todo. Passá-las por `load_spec`
transformaria uma varredura de diretório em uma por spec (45 hoje) e faria um slug duplicado recusar
no meio da varredura — apagando justamente o achado `sp-duplicate-slug` que `cmd_validate` (L2620)
existe para reportar.

A duplicação **não produz divergência hoje**, e afirmar o contrário seria desonesto: as cinco usam
`parse_sections(body_after_frontmatter(text))` e `parse_tasks(text)` de forma idêntica, e a única
assimetria — o argumento `schema` de `derive_stage` — não muda o resultado, porque `load_schema()`
devolve o mesmo objeto nos dois caminhos. O que existe é risco **latente**: `derive_stage` é a
computação mais carregada do front (decide o agrupamento de `list`, o que `plans reindex` renderiza,
a ordenação de `next --front` e o portão `ready` que `validate` julga) e nada estrutural garante que
as quatro contornadoras continuem alimentando-a com as mesmas entradas quando uma regra de estágio
nova for adicionada.

Há também um custo medido e não latente: `load_schema()` (L796) não tem cache — cada chamada relê e
reparseia `schema.json`. Como `cmd_list` e `cmd_plans` chamam `derive_stage` sem `schema`, os dois
releem o arquivo **uma vez por spec**; `validate_spec` faz o mesmo em L2479.

Registrado durante `specs-flow-consolidation`, onde foi deliberadamente não feito: as funções
pertenciam a tarefas diferentes daquela spec, e um refactor atravessando todas elas dentro de
qualquer uma das tarefas colocaria no diff mudanças que o `verify:` daquela tarefa não cobria. É uma
limpeza própria, com verificação própria, que é o que esta spec é.

## Proposal

- `specs.py` passa a ter **uma única** função que transforma uma linha de `spec_files` em um
  registro de spec parseado, e ela é a metade de leitura extraída de `load_spec` — não uma função
  nova ao lado dela.
- `load_spec(root, slug)` continua existindo com a mesma assinatura, o mesmo contrato de recusa e o
  mesmo retorno `(info, err)`, passando a ser resolução de slug mais uma chamada à leitora.
- As quatro varreduras que hoje contornam `load_spec` — `cmd_list`, `_candidate`, `validate_spec` e
  `cmd_plans` — passam a chamar a leitora, e nenhuma delas volta a chamar `read_text`,
  `parse_frontmatter`, `parse_sections` ou `parse_tasks` diretamente.
- Um leitor do script consegue apontar **um** lugar que responde "o que é um spec lido do disco", e
  o registro devolvido tem um conjunto de campos declarado em um só lugar.
- `schema.json` é lido **uma vez por varredura** em vez de uma vez por spec, porque a leitora recebe
  o schema já carregado.
- A saída `--json` de todo comando de leitura é byte a byte idêntica à de antes, para os 45 specs do
  repositório: esta spec não muda comportamento nenhum.
- A propriedade fica afirmável por uma checagem mecânica de uma linha: nenhuma função de `specs.py`
  além da leitora combina `read_text` com `parse_frontmatter` e `parse_sections`.

## Out of Scope

- **Memoizar `load_schema()`.** A redução de leituras de `schema.json` vem de graça quando a leitora
  recebe o schema já carregado, e isso basta. Um cache dentro de `load_schema()` é outra decisão:
  muda o comportamento de um processo longo e não é necessário para este refactor.
- **Quebrar `specs.py` em módulos.** O script é stdlib-only e autocontido de propósito — uma cópia
  instalada em `.claude/hooks/specs.py` roda sem assets ao lado. Esta spec mexe em corpos de função
  dentro de um arquivo e em nenhuma fronteira de arquivo; a questão do split é de
  `split-specs-py-backlog-renderer`.
- **Dar nome ao estágio de scaffold.** Mudar o que `derive_stage` devolve é
  `name-the-scaffolded-stage`; esta spec muda apenas **quem** o chama.
- **Escrever os registros de frontmatter mecanicamente.** A leitora é somente leitura; o caminho de
  escrita é `add-specs-py-record-writer`.
- **Fazer `validate` usar o estágio derivado.** Depois do refactor `validate_spec` recebe o estágio
  de graça, mas passar a reportá-lo é campo novo no `--json` e portanto mudança de comportamento —
  registrado em `## Open Decisions`, não feito aqui.
- **A passagem de mutação que gradua `docs/standards/quality/selftest-mutation.md`.** Aquele
  standard pede quatro mutações contra o `selftest` de cada uma das três ferramentas; esta spec
  empresta a prática para provar que a sua própria rede de verificação não é vácua, e não fecha o
  portão de graduação.
- **Os leitores de `skills.py` e `okf-validate.py`.** Foi medido: `skills.py` lê dois artefatos
  *diferentes* (`discover_commands` L600 para comandos, `agent_definitions` L1396 para agentes) e
  `okf-validate.py` não tem helper de leitura nenhum, lendo com `pathlib.read_text` inline em L816 e
  L993. Não há duplicação equivalente para dobrar, então não há regra de repositório a escrever.
- **Renomear `load_spec`.** O nome é citado em sete comandos e trocá-lo pagaria churn sem comprar
  nada.
- **O bump de versão.** `docs/standards/ci-cd/versioning-release.md` (`authority: current`) põe
  `specs.py` como artefato 5 dos seis do lockstep e é determinante quanto ao momento: os seis se
  movem **uma vez por spec, no passo 5 de `/specs:conclude`, imediatamente antes do merge, e nunca
  como tarefa**. Portanto `## Tasks` não carrega tarefa de bump; é obrigação de release do conclude,
  registrada aqui para que ninguém a invente como tarefa depois.

## Impact

### Standards this spec will write into docs/standards/

- none — foi medido, não presumido: a regra que este refactor prova é local a uma função de um
  script. Uma regra de repositório do tipo "uma leitora por artefato" precisaria valer para as três
  ferramentas instaláveis, e não vale. `skills.py` lê dois artefatos **diferentes** (comandos em
  `discover_commands` L600, agentes em `agent_definitions` L1396 — não são cópias uma da outra) e
  `okf-validate.py` não tem helper de leitura nenhum, lendo inline com `pathlib.read_text` em L816 e
  L993. Declarar um standard aqui seria inventar generalidade que o repositório não tem.

### Standards em `authority: background` que esta spec pode resolver

- none — o standard de mutação de selftest é o candidato óbvio e **não** é resolvido aqui. O portão
  de graduação dele pede uma passagem de quatro mutações contra o `selftest` de cada uma das três
  ferramentas instaláveis; esta spec roda mutações contra o seu próprio arnês de
  snapshot, que é outro artefato. A prática é emprestada, o portão fica onde está — e dizer isso é
  mais honesto que reivindicar uma graduação parcial.

### Código de produto que esta spec espera tocar

- `plugins/quenching/assets/bin/specs.py` — e nada mais. Cinco funções:
  - `load_spec` (L1253–1282) — dividida; a metade de leitura sai para `read_spec`
  - `cmd_list` (L1411–1449) — passa a chamar `read_spec`
  - `_candidate` (L1895–1926) — idem
  - `validate_spec` (L2456–2566) — idem, e é a mais arriscada das quatro
  - `cmd_plans` (L2950–2990) — idem
- Nenhum arquivo novo, nenhum import novo, nenhuma mudança em `schema.json` nem em
  `templates/spec.md` — portanto nada que o `selftest` de lockstep possa reprovar.
- Os números de linha valem para a árvore em que esta spec foi desenvolvida. Especificações irmãs
  mexem no mesmo arquivo: confira antes de confiar neles.

## Validation

Esta spec não muda comportamento, então a verificação não pergunta "funciona?" — pergunta "está
idêntico?". Cinco camadas, e a ordem importa.

**1. Guarda de dano colateral — e não rede de regressão.**

```bash
cd plugins/quenching
python3 assets/bin/specs.py selftest            # 0 error(s)
python3 assets/bin/skills.py selftest
python3 assets/hooks/okf-validate.py selftest
cat VERSION && python3 assets/bin/specs.py --version   # o lockstep continua de acordo
```

Ser explícito sobre o que isso **não** prova é parte da verificação. Medido: `cmd_selftest`
(L2707–2831) checa os casos canônicos de frontmatter, a forma de captura contra o portão de entrada e
a deriva byte a byte de `TEMPLATE_SPEC` e `DEFAULT_SCHEMA`. Ele nunca chama `parse_sections`,
`derive_stage` nem qualquer uma das cinco leitoras. O valor dele aqui é pegar uma edição acidental em
`parse_frontmatter` feita de passagem — não a corretude da leitora.

**2. A rede real: snapshot dourado byte a byte.** `stdout` e `stderr` vão para arquivos separados, de
propósito: um arnês que engole traceback no arquivo comparado fica verde por acidente.

```bash
S=plugins/quenching/assets/bin/specs.py
snap () {                                  # $1 = diretório de saída
  mkdir -p "$1"
  python3 $S list --json         > "$1/list.json"       2> "$1/list.err"
  python3 $S next --front --json > "$1/next-front.json" 2> "$1/next-front.err"
  python3 $S validate --json     > "$1/validate.json"   2> "$1/validate.err"
  for sl in $(python3 -c "import json,subprocess;print(' '.join(s['slug'] for s in json.loads(subprocess.run(['python3','$S','list','--json'],capture_output=True,text=True).stdout)['specs']))"); do
    python3 $S status --spec "$sl" --json > "$1/status-$sl.json" 2> "$1/status-$sl.err"
    python3 $S next   --spec "$sl" --json > "$1/next-$sl.json"   2> "$1/next-$sl.err"
  done
}
snap /tmp/spec-reader/before     # ANTES de qualquer edição, no merge-base do branch
# ... o refactor ...
snap /tmp/spec-reader/after
diff -r /tmp/spec-reader/before /tmp/spec-reader/after && echo IDENTICO
find /tmp/spec-reader -name '*.err' -size +0c    # tem de não imprimir nada
```

O que tem de sair: `diff -r` não imprime nada e sai 0, `IDENTICO` aparece, e o `find` não lista
arquivo nenhum. Medido na árvore intocada: **45 specs, 93 arquivos por captura**, e duas capturas
consecutivas da mesma árvore são byte a byte idênticas — o arnês é determinístico o bastante para
servir de rede.

Uma ressalva com dente: `ageDays` em `next --front` vem de `_days_since` (L1851) e portanto muda na
virada do dia. Tire as duas capturas no mesmo dia, ou normalize o campo antes do `diff`.

**3. As duas assertivas numéricas, com linha de base medida.**

```bash
# a propriedade que a spec promete: UMA leitora, e só ela
python3 - <<'EOF'
import ast, pathlib
src = pathlib.Path("plugins/quenching/assets/bin/specs.py").read_text()
hits = [n.name for n in ast.walk(ast.parse(src))
        if isinstance(n, ast.FunctionDef)
        and {"read_text", "parse_frontmatter", "parse_sections"} <=
            {c.func.id for c in ast.walk(n)
             if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}]
print(hits); assert hits == ["read_spec"], hits
EOF

# o hoist do schema aconteceu de fato
python3 - <<'EOF'
import importlib.util, io, contextlib
sp = importlib.util.spec_from_file_location("sp", "plugins/quenching/assets/bin/specs.py")
m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
n = [0]; orig = m.load_schema
m.load_schema = lambda: (n.__setitem__(0, n[0] + 1), orig())[1]
with contextlib.redirect_stdout(io.StringIO()):
    m.main(["list", "--json"])
print("load_schema calls:", n[0])
EOF
```

Linha de base medida hoje: a primeira imprime
`['load_spec', 'cmd_list', '_candidate', 'validate_spec', 'cmd_plans']` e a asserção **falha**; a
segunda imprime `45`. Depois do refactor: `['read_spec']` com asserção passando, e `1`.

**4. A mutação que prova que a camada 2 não é vácua.** Obrigatória, não opcional — uma verificação
que nunca foi observada falhando não é cobertura. Quebre `read_spec` de duas formas, uma por vez, e
confirme que o `diff` da camada 2 **aparece**; depois reverta:

- passar `text` em vez de `body_after_frontmatter(text)` a `parse_sections` → o campo `stage` tem de
  divergir em vários specs;
- devolver `tasks` vazio → as contagens de tarefa e o `stage` `executing` têm de divergir.

Se qualquer uma das duas deixar o `diff` vazio, a camada 2 está quebrada e a verificação inteira
desta spec é nula. Esse é o resultado que importa mais que o verde.

**5. O que o refactor não pode ter mexido de lado.**

```bash
python3 plugins/quenching/assets/bin/specs.py plans reindex
git diff --exit-code specs/plans/index.md         # idempotente: sai 0
cd plugins/quenching
python3 assets/bin/skills.py --root . doctor --json    # 26 commands, no findings
python3 assets/hooks/okf-validate.py assets/docs      # 0 error(s), 0 warning(s)
```

## Design

### Decisão 1 — dividir `load_spec`, não escrever uma função ao lado dela

`load_spec` (L1253–1282) faz duas coisas: **resolve** um slug para uma linha e **lê** aquela linha.
Só a segunda metade é o que as quatro contornadoras precisam. A forma é extrair a segunda metade:

```python
read_spec(row, schema=None) -> dict         # linha -> registro parseado
load_spec(root, slug)       -> (info, err)  # resolve_slug + read_spec
```

O `## Problem` capturado propunha `_read_spec(row)` como função **nova**. Isso deixaria `load_spec`
com a sua própria cópia inline da leitura: cinco leitoras viram duas, não uma, e a duplicação que a
spec existe para remover sobrevive em forma menor. A extração é o que faz a contagem chegar a um.

### Decisão 2 — a leitora recebe uma linha, nunca um slug

Regra durável: **uma função que varre o front recebe a linha que a varredura já tem e nunca
reconsulta o front por identidade.** Passar as quatro por `load_spec(root, slug)` custaria uma
varredura de `spec_files` por spec e, pior, herdaria a recusa `sp-ambiguous-slug` dentro de um laço
— o que apagaria o achado `sp-duplicate-slug` que `cmd_validate` (L2620) emite justamente quando
dois arquivos compartilham um slug. Recusar é o contrato certo para um comando de spec único e o
contrato errado para uma varredura.

### Decisão 3 — o nome é `read_spec`, público

A superfície de parsing do script é pública sem sublinhado (`parse_sections`, `parse_tasks`,
`derive_stage`, `load_spec`); o sublinhado marca ajudantes locais de um comando (`_candidate`,
`_policy`, `_gate_over`). A leitora primária do arquivo pertence ao primeiro grupo, e nomeá-la
`_read_spec` enquanto o invólucro fino sobre ela é público inverteria a convenção.

### Decisão 4 — `schema` é parâmetro opcional, e as varreduras o içam

`derive_stage` já aceita `schema=None` e cai em `load_schema()` (L1089); a leitora repassa o mesmo
contrato. As quatro varreduras carregam o schema uma vez antes do laço e o passam adiante — que é o
que colapsa as leituras de `schema.json` de uma por spec para uma por processo. `load_spec` continua
podendo chamar sem schema: para um comando de spec único não há laço, e uma leitura é uma leitura.

### Decisão 5 — o registro devolvido é um superconjunto do que cada consumidor usa

`read_spec` devolve tudo que `load_spec` devolve hoje — `text`, `frontmatter`, `sections`, `tasks`,
`stage`, `verification`, mais os campos da linha. `validate_spec` passa a receber um `stage` que não
usa e `cmd_plans` a receber `tasks` que não renderiza. Isso é deliberado: um registro de forma única
é o que dá aos consumidores **uma** definição do que é um spec, e campos condicionais
reintroduziriam as visões levemente diferentes que o problema descreve. O custo é uma chamada a
`derive_stage` por spec em `validate`, e `derive_stage` é aritmética sobre dicionários já parseados.

### Contratos que este design não pode contradizer

- `docs/standards/code/canonical-set-parsing.md` (`authority: current`), §"A lockstep check does not
  cover the code over it". É o contrato que decide o formato de `## Validation`: `selftest` compara
  cópias e não prova nada sobre o código que as lê. Medido: `cmd_selftest` (L2707–2831) nunca chama
  `parse_sections`, `derive_stage` nem qualquer uma das cinco leitoras. Portanto `selftest` aqui é
  guarda de dano colateral, não rede de regressão.
- `docs/standards/quality/parse-honesty.md` — `validate_spec` chama `frontmatter_anomalies(text)`
  antes das checagens de chave obrigatória (comentário em L2469–2471) para que uma falha de parse
  nunca apareça como lacuna de conteúdo. A ordem dessa chamada dentro de `validate_spec` não pode
  mudar quando a leitura sair para a leitora.
- `derive_stage` precisa continuar **total**. `validate` é o comando que tem de sobreviver a entrada
  malformada, e depois do refactor ele passa a derivar estágio para todo spec que valida. Hoje é
  total por construção (`_stage_match` devolve `False` para chave desconhecida e o fallback é
  `spec["phase"]`, L1090); isso vira invariante declarada, não sorte.
- `docs/standards/ci-cd/versioning-release.md` (`authority: current`) — `specs.py` é o artefato 5 de
  seis, e cada align decide sobrescrever a cópia instalada em um repo alvo comparando
  `python3 specs.py --version` com o `VERSION` do plugin. Uma mudança nesta leitora que saia sem
  bump nunca chega aos repos que já têm o script. O bump não é tarefa desta spec (ver
  `## Out of Scope`), mas a obrigação existe e é do conclude.
- O script segue stdlib-only e autocontido: nenhum import novo, nenhum arquivo novo.
- **A suposição carregadora, verificada e não suposta.** O design assume que um registro único
  reproduz exatamente a saída das quatro contornadoras. Isso vale porque nenhuma delas constrói
  saída iterando as chaves do registro: `cmd_list` (L1420), `_candidate` (L1912) e `cmd_plans`
  (L2964) montam dicionários literais explícitos, e `validate_spec` devolve achados. Nenhum
  consumidor pode ser perturbado por um campo extra. Se essa suposição fosse falsa, a comparação
  byte a byte de `## Validation` seria o que a pegaria.

## Alternatives Considered

| Forma | Custo | O que compra | O que impede | Veredito |
| --- | --- | --- | --- | --- |
| **A. Extrair `read_spec(row)` de `load_spec` e passar as quatro por ela** | cinco corpos de função editados, uma função nova, nenhum arquivo novo | uma leitora; um registro; `schema.json` lido uma vez por varredura | nada: `load_spec` mantém assinatura e contrato | **escolhida** |
| B. Escrever `_read_spec(row)` nova ao lado de `load_spec`, como o `## Problem` capturado propunha | o mesmo trabalho de A | quatro cópias viram uma | deixa `load_spec` com cópia inline própria — duas leitoras, não uma | rejeitada: preserva em forma menor exatamente a duplicação que a spec remove |
| C. Passar as quatro por `load_spec(root, slug)` sem mexer nele | quase nenhum código | uma leitora imediatamente | uma varredura de `spec_files` por spec, e a recusa `sp-ambiguous-slug` dentro de um laço apaga o achado `sp-duplicate-slug` | rejeitada: perde nas duas contas, e a segunda é regressão de comportamento |
| D. Não fazer nada; anotar a duplicação em comentário | zero | honestidade sobre um risco latente | deixa a próxima regra de estágio a ser verificada contra quatro leitoras independentes | rejeitada: é o que `specs-flow-consolidation` já fez, e o resultado é esta spec |
| E. Introduzir uma classe ou `dataclass` `Spec` e devolver instâncias | reescreve todo acesso `info["campo"]` nos sete comandos que usam `load_spec`, mais o contrato de tupla `(info, err)` | tipagem e atributos no lugar de chaves | desproporcional a uma limpeza sem mudança de comportamento, e o diff deixa de ser revisável | rejeitada: o problema é o número de leitoras, não a forma do registro |
| F. Rotear só as três que derivam estágio (`cmd_list`, `cmd_plans`, `_candidate`) e deixar `validate_spec` | um quarto do trabalho e evita a edição mais arriscada | a maior parte do ganho: as três derivadoras de estágio passam a ser uma | deixa **duas** leitoras, e a promessa de "uma" em `## Proposal` falha | rejeitada como plano, **adotada como posição de recuo** se a tarefa 2.4 se mostrar ruim (ver `## Risks`) |

## Open Decisions

- **`validate` deve passar a *usar* o estágio que agora recebe de graça?** Depois do refactor
  `validate_spec` tem o estágio derivado em mãos e o descarta. Reportá-lo em cada achado seria útil
  para `/specs:status`, e é campo novo no `--json` — ou seja, mudança de comportamento, que esta spec
  proíbe a si mesma. **Como se decide:** quando um consumidor pedir. Enquanto ninguém pede, a
  resposta certa é continuar descartando, e a decisão vira spec própria em vez de carona nesta.
- **O arnês de snapshot dourado é asset comitado ou descartável?** **Como se decide:** aplicando o
  critério de `docs/standards/quality/bundle-verification.md` — qual invariante merece uma checagem
  determinística — na tarefa 3.1, com o ônus sobre comitar: `CLAUDE.md` hoje diz que `specs.py` não
  tem fixture no repositório e deve ser exercitado em workspace descartável, e essa é a posição
  padrão até que o critério diga o contrário.
- **A ordem em relação a `name-the-scaffolded-stage`.** Aquela spec muda o que `derive_stage`
  devolve; esta muda quem o chama. Não há conflito de conteúdo, mas há de linha de base de
  verificação (ver `## Risks`). **Como se decide:** por qual das duas fizer merge primeiro — o que
  esta spec não pode saber, porque a irmã está sendo desenvolvida em paralelo por outro agente. Se a
  irmã entrar antes, a linha de base é simplesmente retirada depois do merge dela, e nada aqui muda.

## Risks

- **A regressão fantasma — a linha de base envelhecida.** O snapshot dourado é a única rede real
  desta spec, e ele compara com um estado anterior. Se a linha de base for tirada antes de uma irmã
  entrar (`name-the-scaffolded-stage` muda o `stage` de todo spec) ou atravessar a virada do dia (o
  campo `ageDays` de `_candidate` vem de `_days_since`, L1851), todos os 45 specs diferem e o
  executor ou queima horas atrás de um fantasma ou — muito pior — regenera a linha de base e passa a
  não validar nada. *Mitigação:* a linha de base é tirada do `merge-base` do próprio branch no
  primeiro commit dele, nunca é comitada e nunca é reaproveitada entre sessões; `ageDays` é
  normalizado antes do `diff`. *Detecção:* um diff **uniforme** — o mesmo campo mudando em todos os
  45 specs — é assinatura de linha de base velha, não de regressão.
- **O snapshot verde que não prova nada.** O arnês redireciona `2>&1` para os arquivos capturados, o
  que significa que um arnês quebrado grava o mesmo traceback antes e depois e reporta verde. É
  exatamente o modo de falha que `docs/standards/quality/selftest-mutation.md` descreve: uma
  verificação que nunca foi observada falhando não é cobertura. *Mitigação:* a tarefa 3.2 é
  obrigatória e não opcional — quebrar a leitora de propósito e **ver** o diff aparecer é o que
  transforma o verde em evidência.
- **`validate` passar a quebrar onde antes reportava.** `validate_spec` passa a derivar estágio para
  todo spec, incluindo os 13 arquivados; `validate` é justamente o comando que tem de sobreviver a
  entrada malformada. *Mitigação:* medido, não esperado — `derive_stage` foi exercitado contra cinco
  entradas malformadas (frontmatter vazio, bloco não fechado, valor de lista onde se espera escalar,
  BOM inicial) nas duas fases e não levantou exceção em nenhuma; o fallback é `spec["phase"]`
  (L1090). A totalidade de `derive_stage` vira invariante declarada na revisão da tarefa 2.4, e o
  corpus de verificação inclui `archive/`.
- **O hoist que silenciosamente não aconteceu.** Se uma varredura esquecer de passar `schema`,
  `derive_stage` cai em `load_schema()` por spec: o comportamento fica idêntico, o snapshot fica
  verde e a promessa de "uma leitura por varredura" fica quietamente falsa. *Mitigação:* é
  assertiva de `## Validation` com número medido, não prosa — a linha de base é **45 chamadas a
  `load_schema()` em `list --json`** hoje, e depois tem de ser 1.
- **A ressurreição.** ACCEPTED — dentro de um ano alguém "simplifica" `read_spec` e `load_spec` de
  volta em uma leitora que recebe slug, restaurando a varredura por spec e apagando
  `sp-duplicate-slug` outra vez. Não há guarda automática possível a custo razoável. O único guarda
  é a docstring de `read_spec` dizendo *por que* a divisão existe e nomeando `sp-duplicate-slug`, e
  isso é aceito como suficiente: o dano é uma regressão de qualidade recuperável, não perda de
  dados.
- **O custo de não fazer.** ACCEPTED como argumento a favor, registrado como risco porque é o único
  jeito honesto de escrevê-lo: a duplicação não machuca hoje, então adiar não custa nada
  imediatamente. O que custa é a próxima regra de estágio — `name-the-scaffolded-stage` — que terá
  de ser verificada contra quatro leitoras independentes em vez de uma.
- **Reversibilidade.** ACCEPTED e barata: um arquivo, só corpos de função, nenhuma mudança de
  schema, nenhum arquivo novo, nenhuma migração de cópia instalada. Desfazer é `git revert` de um
  commit. Se a tarefa 2.4 (`validate_spec`) se mostrar problemática, a posição de recuo é a forma F
  de `## Alternatives Considered` — as três outras já roteadas, `validate_spec` intocado — que
  entrega a maior parte do ganho sem a edição arriscada.

## Tasks

### 1. Linha de base e assertivas

- [ ] 1.1 Escrever o arnês de snapshot com `stdout` e `stderr` em arquivos separados e capturar a linha de base a partir do `merge-base` do branch, antes de qualquer edição
      verify: snap duas vezes a mesma árvore intocada; `diff -r` entre as duas capturas não imprime nada e nenhum arquivo `.err` tem tamanho maior que zero
- [ ] 1.2 Escrever as duas assertivas numéricas de `## Validation` como comandos reexecutáveis e registrar os valores de hoje
      verify: a assertiva AST imprime as cinco leitoras atuais e falha a asserção; o contador imprime 45

### 2. Uma leitora

- [ ] 2.1 Extrair `read_spec(row, schema=None)` da metade de leitura de `load_spec` e reescrever `load_spec` como `resolve_slug` mais uma chamada a ela, com a docstring dizendo por que a divisão existe e nomeando `sp-duplicate-slug`
      files: plugins/quenching/assets/bin/specs.py
      pattern: plugins/quenching/assets/bin/specs.py — a própria `load_spec`, L1253–1282
      verify: python3 plugins/quenching/assets/bin/specs.py selftest && diff -r do snapshot antes/depois não imprime nada
- [ ] 2.2 Apontar `cmd_list` e `cmd_plans` para `read_spec`, içando `load_schema()` para fora dos dois laços
      files: plugins/quenching/assets/bin/specs.py
      verify: diff -r do snapshot não imprime nada, e o contador de `load_schema()` em `list --json` cai de 45 para 1
- [ ] 2.3 Apontar `_candidate` para `read_spec`, mantendo `ready_report` e `task_progress` onde estão
      files: plugins/quenching/assets/bin/specs.py
      verify: diff -r do snapshot não imprime nada, `next-front.json` incluído, com `ageDays` normalizado
- [ ] 2.4 Apontar `validate_spec` para `read_spec` preservando a ordem de `frontmatter_anomalies`, e declarar na revisão da tarefa que `derive_stage` continua total
      files: plugins/quenching/assets/bin/specs.py
      verify: python3 plugins/quenching/assets/bin/specs.py validate --json sai 0 sobre os 45 specs, os 13 arquivados incluídos, e diff -r do snapshot não imprime nada

### 3. Provar que a rede não é vácua

- [ ] 3.1 Rodar as duas assertivas numéricas contra a árvore refatorada
      verify: a assertiva AST imprime ['read_spec'] com a asserção passando, e o contador imprime 1
- [ ] 3.2 Passagem de mutação obrigatória: quebrar `read_spec` das duas formas descritas em `## Validation`, uma por vez, confirmar que o `diff` do snapshot aparece em cada uma, e reverter
      files: plugins/quenching/assets/bin/specs.py
      verify: cada mutação produz `diff` não vazio em campos distintos — `stage` numa, contagem de tarefas noutra — e `git diff` volta limpo depois de reverter as duas
- [ ] 3.3 Confirmar que `plans reindex` continua idempotente e que o bloco de verificação de CLAUDE.md continua verde
      files: specs/plans/index.md
      verify: python3 plugins/quenching/assets/bin/specs.py plans reindex && git diff --exit-code specs/plans/index.md
