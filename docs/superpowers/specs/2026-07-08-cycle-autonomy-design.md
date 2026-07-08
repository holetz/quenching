# Design — Autonomia do `quenching-cycle` (um OK por ciclo + prep paralelo)

**Data:** 2026-07-08
**Plugin:** `claude-quenching` (marketplace `claude-quenching`)
**Versão-alvo:** 0.10.0 (bump minor — muda o modelo de confirmação do cycle e a doutrina de 4 sub-skills)
**Status:** design aprovado; implementar sobre a base 0.9.0 (branch `feature/documentation-home`).

---

## 1. Objetivo

Fazer o `quenching-cycle` rodar até o fixpoint com **uma única confirmação humana no
início do ciclo** (não mais um OK por pass nem um OK por estágio), e **baratear cada
pass** sobrepondo a fase read-only de descoberta do `quenching-harness` à execução do
`quenching-memory-to-docs`.

Hoje uma única pass pode gerar até 5 confirmações (1 do cycle + 1 de cada um dos até
4 estágios), multiplicado por até 5 passes ≈ 20 idas-e-voltas por ciclo. Nenhum dos 4
sub-skills tem qualquer noção de "fui invocado pelo cycle, já fui autorizado".

**O que NÃO muda:** o gate de item **code-coupled** (rename/edit cujo blast radius
alcança código de produto) continua pausando SEMPRE — é a regra dura do `CLAUDE.md`
("never suppress a sub-skill's own confirmation") e este design a preserva
integralmente. Invocado standalone (fora do cycle), cada sub-skill mantém exatamente o
comportamento atual de plan→OK.

## 2. Decisões travadas (com rationale)

| # | Decisão | Rationale |
| --- | --- | --- |
| D1 | **Um OK por ciclo, não por pass.** O usuário autoriza o ciclo inteiro (até fixpoint ou pass cap 5) sobre a prévia grosseira (contagens/escopo) do assessment inicial. Passes 2–5 rodam sem gate, só narrando. | Escolha do usuário ("sem iteração humana"). A alternativa "batch-plan + replay" (rodar a fase de classificação de cada estágio 2×: uma para agregar planos detalhados, outra para executar) foi descartada — dobra o custo de classificação, contra o objetivo de baratear o pass. |
| D2 | **Code-coupled sempre gateia**, mesmo cycle-authorized. É o ÚNICO ponto de parada possível depois da autorização inicial. | Regra dura do `CLAUDE.md`; um rename que atinge código de produto tem blast radius que nenhuma prévia por contagem antecipa. |
| D3 | **Contrato definido UMA vez em `cycle.md`** (nova seção "The cycle-authorization contract"); cada sub-skill ganha só UMA frase de exceção citando `cycle.md §contract` — nunca restatement da lógica. | Regra do repo: procedimento compartilhado vive no dono, os outros citam. Mas a frase local é necessária: sem ela, a instrução do cycle ("pule sua pausa") conflita frontalmente com a invariante local ("never skip") e o comportamento fica imprevisível. |
| D4 | **O plano de cada estágio vira narração, não gate.** A tabela completa continua sendo apresentada antes das escritas. | Transparência/auditabilidade preservadas — o usuário acompanhando a sessão vê tudo; só não digita OK. |
| D5 | **Escopo-surpresa não re-gateia.** Se um pass posterior descobrir escopo bem maior que o estimado (ex: 3× mais memórias), o ciclo segue, limitado pelo pass cap e pelas invariantes de segurança de cada estágio. | Trade-off aceito explicitamente pelo usuário (§Seção 1 da conversa de design). Freios remanescentes: item code-coupled, ou interrupção manual da sessão. |
| D6 | **Paralelização = "plano em paralelo, escrita em série".** Só a fase read-only de descoberta do harness (steps 1–4) roda em background durante o memory-to-docs; TODA escrita em `docs/` é de um estágio por vez. | `memory-to-docs` e `harness` escrevem nos MESMOS arquivos compartilhados (`index.md` por home, `docs/log.md`, `knowledge/glossary.md`) via o mesmo procedimento de insert. Escrita concorrente = corrida read-modify-write sem lock. A alternativa "concorrência total com lock por home" foi descartada: overlap de home (ex: ambos alimentando `knowledge/`) é plausível e a Edit tool não trava nada entre execuções concorrentes. |
| D7 | **Prep paralelo é condicional**: só quando o assessment achou trabalho nos DOIS estágios no mesmo pass. Um estágio só → fluxo serial normal. | Despachar o agente de descoberta sem ter com o que sobrepor só custa tokens. |
| D8 | **Delta-recheck de staleness obrigatório** no harness antes de escrever: docs recém-criados pelo memory-to-docs podem virar o veredito de uma unidade de MOVE→DEDUPE. Só unidades cujo assunto cruza com os docs novos são re-verificadas (Grep barato). | A tabela do harness foi coletada ANTES das escritas do memory-to-docs; sem o recheck, um fato migraria em duplicata (MOVE de algo que já tem doc) — exatamente o drift que o plugin combate. |
| D9 | **O agente de descoberta lê a lógica do próprio `quenching-harness/SKILL.md`** (executa os steps 1–4 como escritos lá, read-only, devolve a tabela-rascunho). Modelo `sonnet`. | "Conduct, never reimplement": a lógica continua no dono; o cycle só antecipa o prefixo read-only. Sonnet porque classificação MOVE/KEEP é julgamento real (mesma razão do agente de assessment do cycle). |
| D10 | **Fan-outs internos existentes intactos** (slices de classificação do memory-to-docs, slices por home do knowledge-scan). | Já são read-only e internos a cada estágio; fora do problema. |
| D11 | **Versão 0.10.0**, bump em lockstep: `plugin.json` + `VERSION` + constante `VERSION` nos 2 scripts + entrada no `marketplace.json`. | Regra de release do repo. Os scripts não mudam funcionalmente, mas a constante acompanha o par. |

## 3. O contrato de autorização de ciclo (conteúdo normativo → `cycle.md`)

Nova seção em `quenching-cycle/references/cycle.md`, dona do conceito:

**Cobre** (pré-autorizado pelo OK único): toda escrita rotineira de cada estágio —
frontmatter, novos docs, entradas de index/log/glossary, migração+deleção de memória
(pós self-check), corte de unidades de harness (pós self-check) — desde que não toque
código de produto.

**Nunca cobre** (gate sempre): qualquer rename/edit cujo blast radius alcança código
de produto (constante de path, import, docstring). Depois da autorização inicial, este
é o único ponto de parada.

**Não altera invariantes de escrita segura:** write-then-verify-then-delete (memória)
e write-then-verify-then-cut (harness) não dependem de quem autorizou — permanecem.

**Sinalização:** o cycle declara o modo na invocação de cada estágio, em linguagem
natural: *"Running under quenching-cycle authorization granted at cycle start — skip
your plan-confirmation pause; present your plan as narration and execute; code-coupled
items still gate individually."*

**Gate único (substitui o Step 3 por-pass):** roda uma vez, antes do Pass 1, junto do
preflight — mostra o assessment grosseiro e deixa explícito: *"isso autoriza até N
passes rodando os estágios abaixo; qualquer item que toque código de produto ainda
pausa e pede confirmação separada, sempre."*

## 4. Fluxo do pass com prep paralelo (→ `cycle.md` §pipeline)

Quando o assessment achou trabalho em memory-to-docs E harness no mesmo pass:

1. `align` roda primeiro, serial, como hoje.
2. Ao fim do align, o cycle despacha **um `Task` read-only em background** (sonnet):
   executar os steps 1–4 do `quenching-harness/SKILL.md`, devolver a tabela-rascunho.
3. Em paralelo, o orquestrador roda o `quenching-memory-to-docs` inteiro, inline
   (plano narrado → write-verify-delete por memória).
4. Terminado o memory-to-docs, o cycle invoca `quenching-harness` entregando a tabela
   pré-coletada + a lista de docs criados pelo memory-to-docs. Harness faz o
   delta-recheck (D8) e então executa.
5. **Invariante novo:** escrita em `docs/` é sempre de um estágio por vez.
6. `knowledge-scan` fecha o pass como hoje.

Caso comum (um estágio só com trabalho): fluxo serial normal, sem agente de descoberta.

## 5. Alterações por arquivo

| Arquivo | Mudança |
| --- | --- |
| `quenching-cycle/references/cycle.md` | Nova seção "The cycle-authorization contract" (§3 acima); §pipeline ganha o fluxo de prep paralelo, o delta-recheck e o invariante de escrita serial (§4). |
| `quenching-cycle/SKILL.md` | Doutrina "One OK per pass" → "One OK per **cycle**; the cycle run is the unit"; Step 3 vira gate único pré-Pass-1; Step 4 ganha o despacho condicional do prep paralelo; Step 5 não re-gateia passes; invariante "never suppress a sub-skill's own confirmation" reescrita como "never suppress a sub-skill's **code-coupled** confirmation" (+ nota de que a pausa de plano rotineira é absorvida pelo contrato); `description` do frontmatter atualizada (hoje diz "one OK [per pass] … under their own doctrines and confirmations"), sob o cap de 1.536 chars. |
| `quenching-align/SKILL.md` | No bullet "Force with ONE confirmation": *"Exception — cycle-authorized runs: when invoked by `quenching-cycle` under its cycle-authorization contract (see cycle.md §contract), the plan is presented as narration, not a gate; a code-coupled item still confirms on its own, always."* + mesmo apêndice na invariante correspondente. |
| `quenching-memory-to-docs/SKILL.md` | Mesma frase de exceção no bullet "Plan first, execute on one confirmation" + apêndice na invariante "Never skip the single up-front plan+confirmation". |
| `quenching-harness/SKILL.md` | Mesma frase de exceção + apêndice na invariante; MAIS uma frase aceitando a tabela de descoberta pré-coletada do cycle e assumindo o dever do delta-recheck (D8) antes de escrever. |
| `quenching-knowledge-scan/SKILL.md` | Frase de exceção simples (sem code-coupled: cycle-authorized = zero paradas) no bullet "Plan first, one confirmation" + apêndice na invariante. |
| `CLAUDE.md` (raiz) | Retocar a regra do `context: fork`: razão continua válida (standalone ainda gateia; code-coupled ainda pausa mid-flow) mas o texto "every sweep skill gates on a mid-flow confirmation" ganha a ressalva do modo cycle-authorized para não mentir. |
| `plugin.json`, `VERSION`, `marketplace.json`, `okf-validate.py`, `okf-visualize.py` | Bump 0.9.0 → 0.10.0 em lockstep (D11). |

**Fora de escopo:** per-item skills (`insert`/`knowledge`/`glossary`) intactas; nenhuma
mudança funcional no validador/visualizador; nenhuma escrita paralela em `docs/`;
nenhum `context: fork` (regra dura — as confirmações code-coupled seguem mid-flow).

## 6. Verificação

Não há suite de testes — o "código" é prosa. Checks:

1. `cd plugins/claude-quenching && python3 assets/hooks/okf-validate.py assets/docs`
   → segue `0 error(s), 0 warning(s)`.
2. `python3 assets/tools/okf-visualize.py --version` e `assets/hooks/okf-validate.py --version`
   → ambos `0.10.0`, iguais a `VERSION` e `plugin.json`.
3. `description` de cada frontmatter editado sob 1.536 chars; corpos sob 500 linhas.
4. Grep de coerência: toda menção a "cycle-authorized" resolve para `cycle.md §contract`;
   nenhuma skill restaura/duplica a lógica do contrato.
5. **Ensaio manual num repo-alvo de sandbox** (fixture com memória de projeto + CLAUDE.md
   gordo + um rename code-coupled plantado): (a) exatamente 1 OK pedido no início do
   ciclo; (b) passes 2+ rodam sem parar; (c) o rename code-coupled pausa mesmo
   autorizado; (d) `quenching-harness` invocado standalone ainda pede seu OK normal;
   (e) com trabalho nos dois estágios de conteúdo, o agente de descoberta despacha em
   background e o harness faz o delta-recheck contra os docs novos.
