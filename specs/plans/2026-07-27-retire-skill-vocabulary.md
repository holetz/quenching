---
slug: retire-skill-vocabulary
title: Retire the skill vocabulary left behind by the collapse
verification: per-section
priority: {level: 21, criticality: low, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# Retire the skill vocabulary left behind by the collapse

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

O `collapse-skills-into-commands` trocou a forma da superfície de comandos e, de propósito, deixou
as **palavras** para depois. Este spec é o "depois", e é menor e mais concreto do que o título
sugere.

`## Problem` mede o que sobrou — 582 ocorrências de "skill", 145 nomes de comando retirados — e
mostra que a maior parte **não** é defeito: `skills.py`, `/skill:*` e os códigos `sk-*` são a
superfície de hoje, porque o caminho do arquivo é a identidade do comando. O defeito são 60 nomes em
22 arquivos.

`## Design` explica por que a ordem é por **raio de propagação** e não por árvore: primeiro os
arquivos que o plugin *copia* para dentro de cada repo alvo, porque um mold errado se reproduz uma
vez por instalação; depois o `docs/` deste repo. `## Impact` lista os vinte e dois arquivos por anel
e nomeia a única norma que este trabalho prova.

`## Validation` é onde a honestidade do spec fica visível: o gate **não** é zero. Quatro nomes
retirados devem sobreviver — três são registro histórico, um pertence a outro spec — e a allowlist
diz quais e por quê. Dois braços extras cobrem o que o `grep` não vê.

`## Out of Scope` diz de quem é cada coisa que ficou fora: `restructure-claude-front-namespace` para
os entry points e a prosa dos corpos de comando, `rewrite-readme-for-collapsed-surface` para o
README, os três specs de probe para `functional-checks.sh`. `## Open Decisions` guarda a única
pergunta que nenhum dos dois lados pode responder sozinho — se este spec fecha como superseded pelo
rename de namespace, ou se entrega o anel copiado antes dele. `## Alternatives Considered` mostra as
quatro formas que isto podia ter, incluindo essa, e por que a escolhida ganhou.

## Problem

O spec `collapse-skills-into-commands` corrigiu toda referência **factual** obsoleta — caminho ou
link nomeando arquivo que não existe mais — e deixou o **vocabulário** de fora de propósito,
porque julgar centenas de trechos de prosa é a auditoria de corpo que seu `## Out of Scope`
excluía para manter um diff de 28 arquivos revisável.

O que sobrou tem duas formas: o substantivo *"skill"* onde hoje se quer dizer *"command"*, e os
nomes de comando v2 no formato `quenching-docs-add`, que
[docs/standards/naming/command-surface.md](/docs/standards/naming/command-surface.md) já declara
retirados — *"There is **no second name**"*.

**Medido em 2026-07-30**, não estimado:

| Sinal | Como foi medido | Hits |
| --- | --- | --- |
| ocorrências de "skill" nas três árvores | `grep -rin 'skill' plugins/quenching/commands/ docs/ plugins/quenching/assets/references/` | 582 |
| nomes de comando v2 retirados, no plugin inteiro mais `docs/` | o comando do `## Validation` §Braço 1, sem a exclusão do README | 145 em 27 arquivos |
| os mesmos, **fora** de `plugins/quenching/README.md` | o comando do `## Validation` §Braço 1 | 64 em 26 arquivos |

Uma correção da própria medição, porque ela importa para o gate: a primeira tentativa filtrou por
prefixo de front (`quenching-docs-`, `-skill-`, `-specs-`, `-align-`) e **subcontou** — perdeu
`quenching-backlog`, `quenching-backlog-triage`, `quenching-converge` e `quenching-visualize`, todos
igualmente retirados. O comando do `## Validation` filtra pelo caminho oposto: pega qualquer
`quenching-` seguido de minúsculas e hifens, e exclui por lista as duas palavras vivas,
`quenching-managed` e `quenching-native`. É a razão de os números acima serem 145/64 e não 134/63.

Os 582 **não** são todos defeito, e essa distinção é o que decide o escopo: `skills.py`, o
namespace `/skill:*` e os códigos `sk-*` são a **superfície atual** — o caminho do arquivo é a
identidade — e retirá-los exige renomear entry points, o que pertence a outro spec (ver
`## Out of Scope`). O que é defeito são 60 dos 64 nomes retirados — quatro devem **sobreviver**, e
o `## Validation` §allowlist enumera quais e por quê — mais o substantivo em prosa, que só uma
leitura decide e que sai do escopo.

**Chegou a `docs/` também**, o que o spec arquivado não registrou. Reconferido site por site hoje
— três seguem obsoletos, um já foi corrigido:

- `docs/standards/automation/index.md` — a fronteira do assunto ainda diz *"skills and their
  command wrappers"* e *"the plugin's own `skills/` + `commands/`"*. **Obsoleto.**
- `docs/standards/quality/bundle-verification.md:18` — cita
  `quenching-docs-align/references/conformance.md`, caminho que não existe (a árvore
  `plugins/quenching/skills/` foi apagada); as linhas 25–26 nomeiam cinco comandos retirados.
  **Obsoleto, e factualmente quebrado, não cosmético.**
- `docs/knowledge/glossary.md:220-224` §How to enrich — nomeia cinco `quenching-docs-*` retirados
  como o caminho de entrada. **Obsoleto.**
- `docs/standards/CLAUDE.md` — o texto original deste `## Problem` o acusava de rotear para
  `quenching-docs-add` / `quenching-docs-align`; hoje `grep -iE 'skill|quenching-'` nesse arquivo
  não retorna nada. **Já corrigido**, registrado para não ser recontado.

**O anel que mais importa é o que o plugin COPIA para o repo alvo** (dobrado da linha de
`## Discoveries`, 2026-07-28). Um mold com vocabulário retirado não é cosmético: ele re-semeia o
vocabulário em cada repo que instala ou atualiza o plugin.

- `assets/hooks/okf-validate.py:1119` — a mensagem de finding manda o usuário *"Fix with the
  `quenching-docs-align` / `quenching-docs-add` skill"*, emitida a cada disparo do hook em todo
  repo alvo. É a instância de maior tráfego do plugin e é **conselho errado**: quem digitar esses
  nomes não encontra comando algum. A linha `:1312` repete com `quenching-docs-add`.
- `assets/templates/harness/claude-root.md` (9 nomes retirados) e `claude-subfolder.md` (5) — o
  mold de onde `/docs:harness` escreve. `claude-root.md:35` ainda aponta para `specs/backlog/`,
  layout que `plans/` substituiu.
- `assets/docs/**` — o esqueleto instalado: 15 nomes retirados em 8 arquivos, o maior deles
  `assets/docs/knowledge/glossary.md` (5). `assets/docs/QUENCHING.md`, o manual do operador copiado
  para todo repo alvo, carrega o **substantivo** em cinco lugares mas nenhum nome retirado — logo
  fica fora deste spec, com o anel 3.
- `assets/templates/automation/skills-standard.md` — o nome do arquivo e o `title: Skill taxonomy
  and naming` do frontmatter contradizem o H1 do próprio arquivo, `# Command taxonomy and naming`.
- `.claude-plugin/plugin.json` — a `description` diz *"Twenty-four commands"*; a linha de
  `## Discoveries` corrigiu para vinte e cinco; `skills.py doctor --json` reporta **26**. Os três
  números discordam entre si.

`plugins/quenching/README.md` (81 nomes retirados, mais que todo o resto do repo somado) é o site
mais público e **não é deste spec**: `rewrite-readme-for-collapsed-surface` já o possui.

Registrado no `## Discoveries` do spec arquivado:
[/specs/archive/2026-07-26-collapse-skills-into-commands.md](/specs/archive/2026-07-26-collapse-skills-into-commands.md)

## Proposal

- Nenhum nome de comando v2 retirado (formato `quenching-docs-add`) sobrevive fora de
  `plugins/quenching/README.md`. O `grep` do `## Validation` retorna **0**; hoje retorna **63 em 25
  arquivos**.
- A mensagem de finding que todo repo alvo lê a cada disparo do hook nomeia comandos que existem:
  `assets/hooks/okf-validate.py:1119` e `:1312` passam a citar `/docs:align` e `/docs:add`.
- Nenhum mold copiado para o repo alvo re-semeia o vocabulário: os dois arquivos de
  `assets/templates/harness/`, os de `assets/templates/automation/` e os oito de `assets/docs/**`
  afetados nomeiam apenas comandos vivos, e `claude-root.md` aponta para `specs/plans/` em vez de
  `specs/backlog/`.
- Os três sites obsoletos de `docs/` que o spec arquivado não registrou estão corrigidos, e o
  quarto (`docs/standards/CLAUDE.md`) fica registrado como já corrigido em vez de recontado.
- `docs/standards/automation/index.md` descreve a superfície que existe — comandos, um arquivo por
  entry point — em vez de *"skills and their command wrappers"* e *"the plugin's own `skills/` +
  `commands/`"*.
- `assets/templates/automation/skills-standard.md` deixa de carregar um `title` que contradiz o H1
  do próprio arquivo.
- A `description` de `.claude-plugin/plugin.json` declara a mesma contagem que
  `skills.py doctor --json` reporta, em vez de uma terceira.
- Todo par mold/bundle tocado (`assets/docs/X` e `docs/X`) é corrigido nos dois lados no mesmo
  commit — um par corrigido só de um lado não conta como entregue.

## Out of Scope

- **`skills.py`, o namespace `/skill:*`, os códigos `sk-*`, `commands/skill/**` e as references
  `skill-new/` + `skill-eval/`** — cerca de 330 dos 582 hits. Não são resíduo: são a **superfície
  atual**. [command-surface.md](/docs/standards/naming/command-surface.md) faz do caminho do arquivo
  a identidade do comando, então retirar a palavra aí é **renomear entry points** — assunto inteiro
  de `restructure-claude-front-namespace`, cujo `## Open Decisions` ainda pergunta se `skills.py` e
  os códigos `sk-*` mudam. Este spec não decide por ele e não antecipa a resposta.
- **`plugins/quenching/README.md`** — 71 dos 134 nomes retirados. `rewrite-readme-for-collapsed-surface`
  possui o arquivo, e um rename cego sobre ele já foi tentado e revertido uma vez: mangleou 28
  caminhos de link. Aquele arquivo precisa de autoria, não de substituição.
- **A varredura do substantivo em prosa nos ~50 arquivos que o rename de namespace reescreve** —
  `restructure-claude-front-namespace` declara no próprio `## Proposal` que entrega essa varredura
  no mesmo diff do rename, *"because both rewrite the same ~50 files"*. Duplicar aqui garante
  conflito em cada arquivo. O que acontece se aquele spec não for construído está em
  `## Open Decisions`.
- **O nome da ferramenta `Skill` em `allowed-tools:`; o layout legado `.claude/skills/*/SKILL.md`
  que `/skill:align` precisa detectar; a superfície `openspec-*` que `/specs:align` detecta; e
  `docs/reference/tools/claude-code-skill-command-mechanics.md`** — vocabulário do Claude Code e de
  artefatos externos, não do quenching. Retirar essas palavras deixaria os comandos incapazes de
  nomear exatamente o que existem para encontrar.
- **Renomear `docs/standards/automation/skills.md` e `skill-evaluation.md`** — os nomes mentem (o
  primeiro carrega `title: Command authoring and alignment`), mas mover um doc dentro de
  `docs/standards/` é assunto de `revise-standards-subject-folders`. Aqui só o corpo é corrigido; o
  caminho fica onde está.
- **Bump de versão.** [versioning-release.md](/docs/standards/ci-cd/versioning-release.md) §When the
  bump happens é explícito: o bump acontece uma vez, no conclude, imediatamente antes do merge, e
  **nunca** como task. Este spec edita dois arquivos que carregam string de versão do lockstep
  (`okf-validate.py` e `plugin.json`) sem tocar nenhuma dessas strings.
- **Cunhar um termo de glossário para "command" ou "skill".** O glossário já tem **Entry point** e
  nenhuma entrada "Skill"; um segundo nome é exatamente o que a norma de naming proíbe. A correção
  em `docs/knowledge/glossary.md` §How to enrich troca nomes de comando retirados, não define termo
  novo.

## Impact

### Standards this spec will write into docs/standards/

- `docs/standards/architecture/shipped-mold-retirement.md` — retirar um nome no plugin só está
  feito quando todo **mold que o plugin copia** para o repo alvo também para de nomeá-lo, porque um
  mold reproduz o nome uma vez por instalação. **Cita**, e não repete,
  [retiring-a-reserved-artifact.md](/docs/standards/architecture/retiring-a-reserved-artifact.md)
  §Why the reservation is load-bearing, que já estabelece a assimetria de raio de propagação para
  um artefato diferente (nome de arquivo reservado). É o único contrato durável que este trabalho
  prova e que não existe escrito.

### Standards at `authority: background` this spec may resolve

- none — nenhuma norma de `docs/standards/` está em `authority: background` esperando este
  trabalho. Os contratos que este spec obedece (`command-surface.md`,
  `versioning-release.md`, `plugin-layout.md`, `retiring-a-reserved-artifact.md`) já estão em
  `current`.

### Product code this spec expects to touch

Vinte e seis arquivos carregam nome de comando retirado. Quatro deles ficam como estão (ver
`## Validation` §allowlist), então vinte e dois são editados:

| Anel | Arquivos | Por quê |
| --- | --- | --- |
| runtime | `assets/hooks/okf-validate.py` (8 hits) | as linhas 1119 e 1312 são strings que o usuário lê; as outras seis são docstring e comentário |
| molds copiados | `assets/templates/harness/claude-root.md` (9), `claude-subfolder.md` (5), `assets/templates/automation/registry.md` (1), `skills-standard.md` (1), `assets/mkdocs/mkdocs.yml.tmpl` (1) | `/docs:harness` e `/docs:align` escrevem a partir deles |
| esqueleto copiado | `assets/docs/**` — 15 hits em 8 arquivos (`knowledge/glossary.md` 5, `standards/CLAUDE.md` 2, `standards/index.md` 2, `knowledge/index.md` 2, mais `catalog/`, `documentation/`, `vision/`, `reference/regulations/` com 1 cada) | instalado no bundle do alvo |
| `docs/` deste repo | 19 hits em 8 arquivos (`quality/bundle-verification.md` 6, `knowledge/glossary.md` 5, `knowledge/index.md` 2, `standards/index.md` 2, mais `catalog/`, `documentation/`, `vision/`, `reference/regulations/`) | ensina errado a sessão seguinte |
| comentário | `assets/bin/skills.py:686` (1) | ver `## Open Decisions` |
| prosa sem nome retirado | `docs/standards/automation/index.md`, `.claude-plugin/plugin.json` | o defeito é a moldura "skills and their command wrappers" e a contagem, invisíveis ao `grep` |

**Sete desses arquivos são metades de par** (`docs/X` e `assets/docs/X`): `knowledge/glossary.md`,
`knowledge/index.md`, `standards/index.md`, `catalog/index.md`, `documentation/index.md`,
`vision/index.md`, `reference/regulations/index.md`. Cada par é corrigido nos dois lados no mesmo
commit — ver `## Risks`.

**Não tocado, apesar de aparecer no `resource:` de uma norma:** nenhuma das seis strings de versão do
lockstep. `okf-validate.py` e `plugin.json` são editados **sem** que seu `VERSION`/`version` mude.

## Validation

Três braços, porque um `grep` sozinho não cobre o defeito todo.

### Braço 1 — o gate mecânico

```bash
grep -rnoE 'quenching-[a-z][a-z-]*' plugins/quenching docs .claude-plugin CLAUDE.md \
  | grep -vE 'quenching-(managed|native)' \
  | grep -v 'quenching/README.md'
```

Hoje imprime **64** linhas em 26 arquivos. Depois deve imprimir **exatamente 4**, e as quatro devem
ser precisamente estas — nem uma a mais, nem uma a menos:

```
docs/standards/automation/skills.md:10:quenching-skill-pair
docs/standards/automation/skills.md:17:quenching-skill-pair
docs/standards/architecture/plugin-layout.md:108:quenching-align-all
plugins/quenching/assets/checks/functional-checks.sh:192:quenching-docs-align
```

**A allowlist, com a razão de cada uma** — um gate de zero absoluto forçaria apagar registro:

| Linha | Por que fica |
| --- | --- |
| `skills.md:10` e `:17` | `add-quenching-skill-pair` é o nome da **mudança** que criou o doc, não de um comando. Provenance no `source:` e na prosa que o cita |
| `plugin-layout.md:108` | a frase é *"name of the retired `quenching-align-all` skill, was renamed"* — é a citação **da** retirada. Apagá-la destrói o registro dela |
| `functional-checks.sh:192` | assertion de probe, e o arquivo é dos specs `isolate-functional-checks-probes`, `plugin-dir-for-functional-checks` e `probe-a-frontmatter-hook-firing`. Ver `## Out of Scope` |

**Validade da exclusão do README:** ela expira quando `rewrite-readme-for-collapsed-surface` for
construído. Enquanto ela existir, `plugins/quenching/README.md` (81 hits) é o único arquivo fora da
medição, e o número esperado acima **não muda** quando aquele spec fechar — só a exclusão sai do
comando.

### Braço 2 — os quatro sites que o `grep` não vê

```bash
grep -c 'command wrappers' docs/standards/automation/index.md         # 1 hoje  -> 0
grep -o 'Twenty-[a-z]* commands' plugins/quenching/.claude-plugin/plugin.json
python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json
grep -m1 '^title:' plugins/quenching/assets/templates/automation/skills-standard.md
```

- `automation/index.md` não contém mais `command wrappers` nem `the plugin's own skills/`.
- a contagem escrita na `description` do `plugin.json` é a mesma que `doctor --json` reporta em
  `commands` (hoje a `description` diz *Twenty-four* e o `doctor` reporta **26**).
- o `title:` de `skills-standard.md` casa com o H1 do próprio arquivo.

### Braço 3 — o piso de regressão

Este spec edita `okf-validate.py` e o esqueleto entregue, então o bloco de verificação do
`CLAUDE.md` inteiro precisa continuar verde, sem exceção:

```bash
cd plugins/quenching
python3 assets/bin/specs.py selftest
python3 assets/bin/skills.py selftest
python3 assets/hooks/okf-validate.py selftest
python3 assets/hooks/okf-validate.py assets/docs                       # 0 error(s), 0 warning(s)
python3 assets/hooks/okf-validate.py assets/specs/plans --listing-root # 0 error(s), 0 warning(s)
python3 assets/bin/skills.py --root . doctor --json                    # 26 commands, no findings
python3 assets/bin/skills.py --root . lint --json                      # exit 0
python3 assets/hooks/okf-validate.py ../../docs                        # 0 error(s), 0 warning(s)
```

`functional-checks.sh` **não** entra aqui: nada neste spec toca `commands/**`, e o `CLAUDE.md` é
explícito em que o harness pertence à front de comandos e não a um `## Validation` de spec.

## Design

### A ordem é por raio de propagação, nunca por árvore

Três anéis, e o spec só reivindica os dois primeiros:

```
anel 1  assets/{hooks,templates,docs}/**  -> COPIADO para o repo alvo   (re-semeia)
anel 2  docs/** deste repo                -> lido por sessões futuras   (ensina errado)
anel 3  commands/** + assets/references/  -> prosa, ~50 arquivos        (fora de escopo)
```

A regra vem de um contrato que já existe:
[retiring-a-reserved-artifact.md](/docs/standards/architecture/retiring-a-reserved-artifact.md)
§Why the reservation is load-bearing — *"the blast radius is not this repo — it is every
already-aligned target repo"*. Um mold errado não é um arquivo errado; é N arquivos errados, um por
repo que instalar. O anel 3, por contraste, custa contexto de sessão e nada mais.

### O gate é `grep`, não leitura

Os 63 nomes retirados são **decidíveis mecanicamente**, com regex e código de saída. O substantivo
em prosa só uma leitura decide, e é por isso que ele sai do escopo em vez de entrar como task
imprecisa. O spec compra apenas o que consegue provar — ver `## Validation`.

### `docs/` e `assets/docs/` são bundles IRMÃOS, não cópias

Medido com `diff -rq docs plugins/quenching/assets/docs`: quatro arquivos compartilhados divergem e
cerca de dez existem só em `docs/`. Logo `QUENCHING.md`, `standards/CLAUDE.md`, os `index.md` e
`glossary.md` precisam ser corrigidos **nos dois lados**, e um par corrigido de um lado só é o modo
de falha deste spec. Nota de fronteira: `docs/QUENCHING.md` já declara `quenching v4.2.0` contra o
`VERSION` 4.4.0 — drift do lockstep de release, não deste spec, e nada aqui o corrige.

### A auditoria de doutrina do `/skill:align` NÃO cobre isto

O `## Problem` original mandava checar antes de escrever tasks. Checado em
`plugins/quenching/commands/skill/align.md` §7: a auditoria julga no-op test, sediment, sprawl,
positive prescription e *cited rather than restated*. `skills.py lint` emite `sk-body-length`,
`sk-step-criterion`, `sk-trigger-position`, `sk-no-boundary`, `sk-description-portable` e
`sk-metadata-cap`. **Nenhum dos dois é lexical.** Não há cobertura prévia, nenhuma task pode
delegar para lá, e nenhuma task deve inventar um código `sk-*` novo para isto — o anel 3, que seria
o candidato natural a um lint, está fora de escopo.

### Corrigir o mold não corrige as cópias já instaladas

`/docs:align` reinstala `QUENCHING.md` e regenera os `index.md`, então esses se auto-curam no
upgrade. Um `CLAUDE.md` que o repo alvo já escreveu a partir do mold antigo só muda quando
`/docs:harness` rodar de novo, e nenhum sweep reescreve prosa que não possui — mesmo princípio de
`retiring-a-reserved-artifact.md` §The consequence for disposition. A entrega é *parar de
re-semear*, não *desfazer o que já foi semeado*. Registrado em `## Risks`.

### Contratos vinculantes que este design não pode contradizer

| Contrato | O que ele obriga aqui |
| --- | --- |
| [command-surface.md](/docs/standards/naming/command-surface.md) | o caminho é a identidade; não há segundo nome. É o que põe `/skill:*` fora de escopo |
| [versioning-release.md](/docs/standards/ci-cd/versioning-release.md) | nenhum bump como task, mesmo tocando arquivos do lockstep |
| [plugin-layout.md](/docs/standards/architecture/plugin-layout.md) | `commands/**` é a única árvore registrada; molds e references ficam sob `assets/` |
| [retiring-a-reserved-artifact.md](/docs/standards/architecture/retiring-a-reserved-artifact.md) | retirar é parar de produzir, não apagar o que já existe no alvo |

## Alternatives Considered

| Forma | Custo | O que compra | O que fecha |
| --- | --- | --- | --- |
| **1. Varredura total agora** — os 582 hits, três árvores mais `assets/**` mais o README | conflito garantido com dois specs irmãos; diff irrevisável; é a segunda tentativa do rename cego que já foi revertido uma vez | acaba em uma passada | nada, mas provavelmente é revertido de novo |
| **2. Só o conjunto decidível por `grep`** — os 63 nomes retirados fora do README | uma passada mecânica, verificável por código de saída | mata toda instrução factualmente errada, inclusive a de runtime | deixa `docs/standards/automation/index.md` mentindo, porque lá o defeito é prosa e não nome |
| **3. Anel copiado primeiro, depois `docs/` deste repo, prosa adiada** — a forma 2 mais os três sites de prosa em `docs/` e as duas mentiras de nome (`plugin.json`, `skills-standard.md`) | duas passadas ordenadas, uma delas julgada | para o mecanismo de re-semeadura **e** corrige os três sites de `docs/` que o spec arquivado nunca registrou | nada; o anel 3 continua disponível para o irmão |
| **4. Fechar como superseded**, entregando tudo a `restructure-claude-front-namespace` | zero | nenhum trabalho duplicado | a mensagem de finding segue entregando conselho errado enquanto aquele spec estiver bloqueado, e o `## Out of Scope` dele nunca reivindica os molds nem as strings do `okf-validate.py` |

**Escolhida: 3.** É o anel que nenhum irmão reivindica, seu núcleo é verificável por `grep`, e ela
remove o *mecanismo* de propagação em vez do resíduo.

**Por que a 1 perdeu:** não é uma alternativa de forma diferente, é a mesma com o escopo maior — e o
escopo maior é exatamente o que foi revertido em `collapse-skills-into-commands` e o que
`rewrite-readme-for-collapsed-surface` registra como mangleando 28 links.

**Por que a 2 perdeu:** subestima o defeito. `docs/standards/automation/index.md` não contém nome
retirado nenhum e ainda assim é o site que ensina errado a fronteira de um assunto inteiro de
`docs/standards/`. Um gate de `grep` que passasse com aquele arquivo intacto estaria medindo a
coisa errada — daí o gate misto do `## Validation`.

**Por que a 4 perdeu:** é a resposta que o `## Open Decisions` de `restructure-claude-front-namespace`
propõe, e ela seria correta se aquele spec cobrisse o anel 1. O `## Proposal` dele cita `assets/**`
genericamente, mas nenhuma linha dele nomeia `okf-validate.py:1119`, os molds de harness ou o
esqueleto `assets/docs/**` — e ele está bloqueado em `instrument-and-extend-skill-front`. Fechar
agora troca trabalho pequeno e provável por espera de duração indefinida.

**Não considerada como alternativa real:** adicionar um código `sk-*` lexical ao `skills.py` para
que o lint pegasse o vocabulário continuamente. Ela só faz sentido para o anel 3, que está fora de
escopo, e criaria um código `sk-*` novo justamente no momento em que
`restructure-claude-front-namespace` está decidindo se esses códigos sobrevivem. Registrada em
`## Open Decisions`, não aqui.

## Open Decisions

- **Este spec fecha como superseded por `restructure-claude-front-namespace`, ou entrega o anel 1
  antes dele?** O `## Open Decisions` daquele spec faz a mesma pergunta pelo outro lado, propondo
  fechar este como `abandoned` se a varredura de `docs/` couber nas tasks dele.
  *Decidido por:* ler o `## Tasks` daquele spec quando ele existir, e checar se alguma task nomeia
  `assets/hooks/okf-validate.py`, `assets/templates/harness/` ou `assets/docs/**`. Hoje o
  `## Proposal` dele cita `assets/**` de forma genérica e nenhuma linha nomeia esses três. Se as
  tasks nomearem, este spec fecha via `/specs:conclude --outcome abandoned` com essa razão. Se não
  nomearem, este spec segue e reduz o diff daquele. **Nenhum dos dois specs decide pelo outro.**
- **A ordem de merge entre os dois.** Se este entrar primeiro, o rename de namespace reescreve
  menos arquivos; se entrar depois, 60 das 64 correções podem já estar feitas.
  *Decidido por:* qual dos dois estiver `approved` primeiro. Sem coordenação técnica possível — os
  dois specs estão sendo desenvolvidos em paralelo por sessões que não se veem.
- **`skills.py` ganha um código `sk-*` lexical que pegue vocabulário retirado continuamente?**
  Seria o gate permanente que o `grep` do `## Validation` só simula uma vez, e cobriria o anel 3
  sem exigir julgamento por arquivo.
  *Decidido por:* **não agora, e a razão é de sequenciamento** — o `## Open Decisions` de
  `restructure-claude-front-namespace` está decidindo se os códigos `sk-*` sobrevivem à renomeação
  da front. Cunhar um código novo enquanto isso está aberto cria justamente o trabalho que aquela
  decisão pode desfazer. Reavaliar depois que aquele spec fechar.
- **O comentário de `assets/bin/skills.py:686` conta como nome retirado a corrigir ou como
  provenance a preservar?** Ele cita *"`quenching-skill-align-and-update` Stage 2"* para explicar
  uma decisão de design. *Decidido por:* tratado como **a corrigir** (fica dentro dos 60), porque a
  frase descreve o comportamento de hoje e não o registro de uma mudança; se na execução a leitura
  mostrar que ele narra história, migra para a allowlist do `## Validation` e o gate passa a esperar
  5, não 4. A decisão é do executor com o arquivo aberto, e trocar o número esperado é uma edição de
  uma linha.

## Risks

- **A evidência é assimétrica, e o `## Problem` fala de uma população que este repo não mede.**
  Existe defeito com vítima demonstrável em exatamente dois sites: `okf-validate.py:1119`/`:1312`
  mandam rodar comando inexistente, e `bundle-verification.md:18` cita caminho apagado. Nos outros
  ~60 ninguém reportou confusão, e o número de repos alvo instalados é **desconhecido**.
  `ACCEPTED — o escopo é o anel copiado justamente porque o custo por site é baixo e o trabalho é
  mecânico; a frase "todo repo alvo" é o mecanismo, não uma contagem medida.`
- **O par `docs/X` ↔ `assets/docs/X` divergir, corrigido de um lado só.** Não é hipotético: já
  aconteceu. `docs/standards/CLAUDE.md` tem **0** nomes retirados e
  `assets/docs/standards/CLAUDE.md` tem **2** — o bundle foi corrigido e o mold não.
  *Mitigação:* uma task dedicada aos pares, e o gate do `## Validation` roda sobre as duas árvores
  na mesma invocação, então um lado esquecido não passa.
- **Inferir uma task de bump de versão a partir do `resource:` de
  [versioning-release.md](/docs/standards/ci-cd/versioning-release.md).** Este spec edita
  `okf-validate.py` e `plugin.json`, dois dos seis artefatos do lockstep. O erro já foi cometido
  antes por este mesmo comando — o `source:` daquela norma registra: *"the conclude-time rule added
  after `/specs:develop` inferred a bump task from this doc's `resource:` alone"*.
  *Mitigação:* está em `## Out of Scope` **e** no `## Handoff`, porque um executor lê Handoff e
  Tasks, não `## Out of Scope`.
- **Um nome substituto digitado errado propaga igual a um certo.** Reverter o commit deste repo não
  reverte molds já copiados para um repo alvo. *Mitigação:* cada nome novo é conferido contra a
  lista que `skills.py doctor --json` reporta, não digitado de memória; o `verify:` da task de
  molds faz exatamente isso.
- **`revise-standards-subject-folders` mover `docs/standards/automation/`** enquanto este spec
  edita `automation/index.md` e `automation/skills.md`. *Mitigação:* nenhuma técnica — os dois specs
  não se veem. Este spec só toca o **corpo** desses dois arquivos e nunca o caminho, então um move
  do irmão resolve como conflito de conteúdo em arquivo renomeado, que o git segue, e não como
  edição concorrente do mesmo caminho.
- **`restructure-claude-front-namespace` entregar o anel 1 antes deste spec**, tornando 60 das 64
  correções redundantes. *Mitigação:* nenhuma — é a incerteza registrada em `## Open Decisions`, e
  a ordem das tasks limita o dano: a task 1 é a única com vítima demonstrável e é independente das
  outras.
- **`/docs:harness` rodar num repo alvo entre a correção do mold e o upgrade do plugin**, gravando
  vocabulário retirado num `CLAUDE.md` novo. Não há detecção: nenhum check deste plugin lê o
  `CLAUDE.md` de um alvo.
  `ACCEPTED — a entrega é parar de re-semear, não desfazer o que já foi semeado; é o mesmo princípio
  de retiring-a-reserved-artifact.md §The consequence for disposition, onde um sweep nunca reescreve
  conteúdo que não possui.`
- **História apagada por um gate cego.** Quatro nomes retirados **devem sobreviver**: um gate de
  zero absoluto forçaria um executor a apagar registro. *Mitigação:* o gate é "exatamente 4, todos
  na allowlist enumerada", especificado no `## Validation`.

**Uma história de premortem que não converteu em nada, registrada como descartada:** *"a string de
finding está dentro do bloco duplicado verbatim entre os três tools, então corrigi-la quebra os três
selftests."* Conferido — `_render_proposal` fica em `okf-validate.py:1113`, fora da região
duplicada, e `grep -c 'Fix with the'` retorna 1 no `okf-validate.py` e 0 no `specs.py` e no
`skills.py`. Não é risco.

## Tasks

### 1. A instrução que o usuário lê em runtime

- [ ] 1.1 Trocar os oito nomes retirados de `okf-validate.py` por `/docs:align` e `/docs:add` — as
      duas strings que o usuário lê (`:1119` no `_render_proposal`, `:1312`) e as seis de docstring
      e comentário (`:7`, `:16`, `:91`, e as demais)
      files: plugins/quenching/assets/hooks/okf-validate.py
      verify: grep -cE 'quenching-[a-z]' plugins/quenching/assets/hooks/okf-validate.py; python3 plugins/quenching/assets/hooks/okf-validate.py selftest
      Feito quando o `grep` conta 0 e o `selftest` passa. **Não mudar a constante `VERSION`.**

### 2. Os molds que o plugin copia para o repo alvo

- [ ] 2.1 Reescrever os dois molds de harness, e corrigir `claude-root.md:35`, que aponta para
      `specs/backlog/`, para `specs/plans/`
      files: plugins/quenching/assets/templates/harness/claude-root.md, plugins/quenching/assets/templates/harness/claude-subfolder.md
      verify: grep -cE 'quenching-[a-z]|specs/backlog' plugins/quenching/assets/templates/harness/*.md
      Feito quando o `grep` conta 0 nos dois arquivos.
- [ ] 2.2 Corrigir os dois molds de `automation/`: o exemplo de `source:` em `registry.md:10` e em
      `skills-standard.md:10`, e o `title: Skill taxonomy and naming` de `skills-standard.md`, que
      contradiz o H1 `# Command taxonomy and naming` do mesmo arquivo
      files: plugins/quenching/assets/templates/automation/registry.md, plugins/quenching/assets/templates/automation/skills-standard.md
      verify: grep -m1 '^title:' plugins/quenching/assets/templates/automation/skills-standard.md
      Feito quando o `title:` casa com o H1 e nenhum dos dois arquivos nomeia comando retirado.
- [ ] 2.3 Trocar `quenching-align` por `/align` em `mkdocs.yml.tmpl:2`
      files: plugins/quenching/assets/mkdocs/mkdocs.yml.tmpl
      verify: grep -cE 'quenching-[a-z]' plugins/quenching/assets/mkdocs/mkdocs.yml.tmpl
      Feito quando conta 0.
- [ ] 2.4 Resolver `assets/bin/skills.py:686` conforme a entrada de `## Open Decisions`: se o
      comentário descreve comportamento de hoje, trocar o nome; se narra história, deixar e somar 1
      ao número esperado do `## Validation` §Braço 1
      files: plugins/quenching/assets/bin/skills.py
      verify: python3 plugins/quenching/assets/bin/skills.py selftest
      Feito quando a linha foi decidida por escrito no commit e o `selftest` passa. **Não mudar a
      constante `VERSION`.**

### 3. O esqueleto entregue e o bundle deste repo — os dois lados de cada par

- [ ] 3.1 Corrigir os sete pares `docs/X` + `assets/docs/X` no MESMO commit:
      `knowledge/glossary.md` (5+5), `knowledge/index.md` (2+2), `standards/index.md` (2+2),
      `catalog/index.md`, `documentation/index.md`, `vision/index.md`,
      `reference/regulations/index.md` (1+1 cada). Em `glossary.md` o site é §How to enrich, que
      nomeia cinco `quenching-docs-*` retirados como o caminho de entrada
      pattern: docs/standards/CLAUDE.md
      verify: diff <(grep -coE 'quenching-[a-z][a-z-]*' docs/knowledge/glossary.md) <(grep -coE 'quenching-[a-z][a-z-]*' plugins/quenching/assets/docs/knowledge/glossary.md)
      Feito quando os catorze arquivos contam 0 e cada par bate entre si.
- [ ] 3.2 Corrigir `assets/docs/standards/CLAUDE.md` (2), a metade de par que já divergiu: o
      `docs/standards/CLAUDE.md` deste repo foi corrigido e o mold não
      files: plugins/quenching/assets/docs/standards/CLAUDE.md
      verify: grep -cE 'quenching-[a-z]' plugins/quenching/assets/docs/standards/CLAUDE.md
      Feito quando conta 0.
- [ ] 3.3 Corrigir os seis nomes de `docs/standards/quality/bundle-verification.md`, incluindo a
      linha 18, que cita `quenching-docs-align/references/conformance.md` — caminho que não existe
      desde que a árvore `plugins/quenching/skills/` foi apagada. O destino correto é
      `plugins/quenching/assets/references/docs-align/conformance.md`
      files: docs/standards/quality/bundle-verification.md
      verify: grep -cE 'quenching-[a-z]' docs/standards/quality/bundle-verification.md
      Feito quando conta 0 e o caminho citado na linha 18 existe em disco.

### 4. A prosa que o `grep` não enxerga

- [ ] 4.1 Reescrever a fronteira de assunto em `docs/standards/automation/index.md`: as linhas 3, 6
      e 7 dizem *"skills and their command wrappers"* e *"the plugin's own `skills/` + `commands/`"*,
      e a superfície é um arquivo por entry point sem wrapper nenhum
      files: docs/standards/automation/index.md
      verify: grep -c 'command wrappers' docs/standards/automation/index.md
      Feito quando conta 0 e a linha `skills.md` da tabela do índice descreve comandos.
- [ ] 4.2 Corrigir a `description` de `plugin.json`: a contagem *"Twenty-four commands"* passa a ser
      a que `skills.py doctor --json` reporta, e a claim de vocabulário na mesma frase é conferida
      files: plugins/quenching/.claude-plugin/plugin.json
      verify: python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json
      Feito quando o número escrito na `description` é o mesmo de `commands` no `--json`. **Não mudar
      a chave `version`.**

### 5. A norma que este trabalho prova, e o gate

- [ ] 5.1 Escrever `docs/standards/architecture/shipped-mold-retirement.md` (`authority: current`
      assim que os braços 1 e 2 do `## Validation` passarem): retirar um nome só está feito quando
      todo mold copiado para o repo alvo para de nomeá-lo, porque um mold reproduz o nome uma vez
      por instalação. **Citar**, não repetir,
      `docs/standards/architecture/retiring-a-reserved-artifact.md` §Why the reservation is
      load-bearing
      files: docs/standards/architecture/shipped-mold-retirement.md, docs/standards/architecture/index.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs
      Feito quando o validador reporta 0 error / 0 warning e o `index.md` de `architecture/` lista o
      doc novo.
- [ ] 5.2 Rodar os três braços do `## Validation` e registrar a saída de cada um
      verify: ver `## Validation`
      Feito quando o braço 1 imprime exatamente as 4 linhas da allowlist, o braço 2 passa nos quatro
      sinais, e o braço 3 fica todo verde.

## Discoveries

- O escopo passa dos corpos de comando, das references e de docs/ e chega ao CÓDIGO-FONTE ENTREGUE, onde o vocabulário retirado é visível ao usuário em tempo de execução: (1) a própria mensagem de finding do okf-validate.py manda todo usuário 'Fix with the quenching-docs-align / quenching-docs-add skill' — emitida a cada disparo do hook em todo repo alvo, o que faz dela a instância de maior tráfego do plugin, e não algo cosmético; (2) plugins/quenching/README.md ainda encabeça suas seções por comando com nomes quenching-docs-* / quenching-skill-*; (3) assets/templates/harness/claude-root.md, o mold de onde /docs:harness escreve, nomeia cinco skills retiradas e specs/backlog/, então um refactor de harness propaga vocabulário retirado para todo repo alvo que ele toca; (4) a description de .claude-plugin/plugin.json diz 'Twenty-four commands' onde há vinte e cinco. Os itens 1 e 3 são os que sustentam o peso — os dois são copiados para dentro dos repos alvo, então re-semeiam o vocabulário que este spec existe para retirar. Encontrado durante uma rodada de /align, 2026-07-28. -> folded: Problem
