# Design — Home `documentation/` + setup de site mkdocs

**Data:** 2026-07-08
**Plugin:** `claude-quenching` (marketplace `claude-quenching`)
**Versão-alvo:** 0.9.0 — **release combinado** com a feature paralela "backlog-idea" (ver §4.5)
**Status:** design aprovado; implementar **por cima** do working tree atual (base = backlog-idea).

---

## 1. Objetivo

Adicionar ao bundle OKF um novo home, **`documentation/`**, que reúne a documentação
em prosa voltada a leitores humanos (formato Diátaxis) e serve de insumo para um site
gerado por **mkdocs**. A mudança **funde o home `guides/` dentro de `documentation/how-to/`**
(guides deixa de existir como home) e faz o plugin **enviar e instalar um setup de site
mkdocs completo** (config + nav + build) no repositório-alvo.

Estado final da árvore de homes (10, era 10 antes — `guides/` sai, `documentation/` entra):

```
docs/  standards/  decisions/  vision/  backlog/
       documentation/  knowledge/  reference/  catalog/  communications/  presentations/
```

## 2. Decisões travadas (com rationale)

| # | Decisão | Rationale |
| --- | --- | --- |
| D1 | `documentation/` é um home de **conteúdo novo** para docs de produto/usuário, com frontmatter OKF. | Escolha do usuário; coerente com "um home, um propósito". |
| D2 | Fronteira **por formato/audiência**, não subject: *"página que eu poria no site de docs (prosa, p/ humano)? → `documentation/`; conhecimento estruturado p/ time+agente? → outros homes."* | A fusão de `guides/` (que é sobre o processo do time, não sobre o produto) reposicionou a fronteira de "subject=produto" para "prosa-para-humanos Diátaxis". |
| D3 | Interior = **4 subfolders Diátaxis fixos**: `getting-started/` (tutorial), `how-to/` (how-to, ex-`guides/`), `reference/` (referência do nosso produto), `concepts/` (explanation). | Escolha do usuário; previsível para quem vem do mundo mkdocs. Precedente OKF de home com subfolders fixos + type único: `standards/`, `reference/`. |
| D4 | **`guides/` é fundido de vez** em `documentation/how-to/`. Deixa de existir como home. | Escolha do usuário ("fundir de vez"). Elimina o overlap guides×how-to na raiz. |
| D5 | **`knowledge/` permanece intacto.** `documentation/concepts/` (explanation p/ o site) × `knowledge/` (entendimento interno do time) distinguem-se por *"é página do site publicado? → concepts/; é conhecimento de trabalho? → knowledge/"*. | O usuário só pediu fusão de `guides/`. Evita ballooning. |
| D6 | `documentation/reference/` **mantém o nome** `reference/` (canônico Diátaxis), com nota de fronteira vs. o home raiz `reference/` (externo que consumimos). Caminhos desambiguam. | Menor atrito; nome Diátaxis reconhecível. |
| D7 | **`type: documentation`** único para todo o home (os 4 subfolders). `type: guide` é aposentado. | Padrão OKF "um type por home"; evita colisão `type: reference` dentro de `documentation/reference/`. |
| D8 | Mold **reusa `assets/templates/concept-front.md`** (que `guides/` já usava); defaults do home: `audience: human`, `authority: current`. | KISS; frontmatter OKF já é lido nativamente pelo mkdocs-material. |
| D9 | **Site renderiza SÓ `documentation/`** (`docs_dir: docs/documentation`). Os outros homes ficam internos, não publicados. | Escolha do usuário; não vaza governança interna; simplifica o caveat de cross-links. |
| D10 | **Gerador default = mkdocs + Material.** O markdown OKF permanece **neutro de gerador**; só a camada de config (`mkdocs.yml` + `.pages`) é mkdocs-específica. | Melhor encaixe: Python/pip (congruente com o plugin low-dependency), consome a árvore .md+frontmatter direto, `navigation.indexes` + awesome-pages resolvem index.md-landing e auto-nav. |
| D11 | **Nav via `mkdocs-awesome-pages-plugin`** (`.pages` embutidos no skeleton). Nav espelha a árvore; nenhum skill regenera nav. | Zero ônus contínuo de sincronização; `.pages` é YAML, invisível ao validador OKF. |
| D12 | **Versão → 0.9.0 combinada** com a backlog-idea. `VERSION`/`plugin.json` **já estão em 0.9.0** (bumpados por ela) — **não re-bumpar**, só garantir consistência e `--version` do hook em lockstep. | Escolha do usuário (release combinado). Remove um home canônico + muda a migração — breaking de qualquer forma. |

## 3. Escopo

**Entra:**
- O home `documentation/` + 4 subfolders + índices reservados.
- `type: documentation`; reuso de `concept-front.md`.
- Setup de site mkdocs: `mkdocs.yml`, nav awesome-pages (`.pages`), `requirements.txt`, workflow CI opt-in.
- Novo passo no `quenching-align` que instala/atualiza o setup mkdocs (oferecer-se-ausente, sem clobber).
- Fusão `guides/` → `documentation/how-to/`: doutrina, regra de home-aposentado na migração, varredura das referências vivas.
- Bump de versão 0.9.0.

**Fora (YAGNI):**
- **Não** renderiza o bundle inteiro (site só de `documentation/`).
- **Não** funde `knowledge/` nem toca na identidade dos outros homes.
- **Não** reescreve cross-links `/docs/...` para o site (páginas do home devem ser autocontidas).
- **Não** há nav gerado por skill (awesome-pages cobre).
- Nenhum outro gerador (Docusaurus/Hugo/Sphinx) é enviado — mkdocs-material é o default suportado; o markdown continua neutro.

## 4. Design detalhado

### 4.1 O home `documentation/`

**Identidade** (para `documentation/index.md` — listing reservado, sem frontmatter):
documentação em prosa narrativa escrita para um leitor humano, estruturada como um site
Diátaxis — o que se publica com mkdocs. Absorve o antigo `guides/`.

**Régua de fronteira (uma linha):** *"É uma página que eu poria no site de documentação
(prosa, para um humano ler)? → `documentation/`. É conhecimento estruturado/tipado para o
time+agente operarem? → os outros homes."*

**Tie-breakers a gravar na doutrina:**
- vs. `knowledge/` — página do site publicado (narrativa, p/ o leitor) → `documentation/concepts/`;
  entendimento interno do time (modelo mental, aprendizado, glossário) → `knowledge/`.
- vs. `standards/` — um "how-to" que na verdade descreve o **contrato atual** (a regra) →
  `standards/`; ensinar a **executar** uma tarefa → `documentation/how-to/`. (Tie-breaker
  existente de guides, reescrito.)
- vs. home raiz `reference/` — referência do **nosso produto** (p/ quem o usa) →
  `documentation/reference/`; fatos sobre um **ativo externo que consumimos** (tool/lib/regulação
  nomeada) → `reference/`.

### 4.2 Estrutura interna e frontmatter

Quatro subfolders fixos, cada um um listing reservado (`index.md` sem frontmatter) com a
régua Diátaxis daquele quadrante + seção "How to organize" (subject-first dentro do quadrante):

| Subfolder | Quadrante | Conteúdo |
| --- | --- | --- |
| `getting-started/` | tutorial | trilha de aprendizado, "coloque pra rodar" |
| `how-to/` | how-to | receitas por tarefa (ex-`guides/`) |
| `reference/` | reference | referência do nosso produto/API |
| `concepts/` | explanation | explicação narrativa p/ o leitor do site |

- **`type: documentation`** em toda página do home.
- **Mold:** `concept-front.md` com `type: documentation`, `audience: human`, `authority: current`;
  `resource:` aponta para o que a página documenta (feature, glob de código, URL) — nunca vazio.
- **Sem página-seed** (como `guides/`/`knowledge/`): o skeleton envia só os índices; o repo preenche.
- **Sem `log.md` próprio** por padrão (per-home log é opcional; eventos vão pro `docs/log.md`).

### 4.3 Setup de site mkdocs

**Payload novo em `assets/mkdocs/`** (carimbado na **raiz do repo-alvo**, fora do bundle):

- **`mkdocs.yml.tmpl`** — mold com:
  - `site_name` / `site_description` (placeholders p/ o repo preencher);
  - `docs_dir: docs/documentation`;
  - `theme: name: material` com features: **`navigation.indexes`** (faz o `index.md` reservado
    virar a landing da seção — casa as duas funções), `navigation.sections`, `navigation.top`,
    `search`, `content.code.copy`;
  - `plugins: [search, awesome-pages]`;
  - **sem bloco `nav:` manual** — o nav vem do awesome-pages.
- **`.pages`** (awesome-pages) embutidos no skeleton `assets/docs/documentation/**`:
  - `documentation/.pages` — ordena as 4 seções (getting-started → how-to → reference → concepts);
  - um `.pages` por subfolder com `title:` legível ("Getting started", "How-to guides",
    "Reference", "Concepts") e ordem;
  - se um repo adicionar `log.md`, ocultá-lo via `.pages` (`hide` / `not_in_nav`).
  - **Trade-off deliberado:** os `.pages` são a única camada de config que mora *dentro* do
    bundle (D10 mantém o resto neutro). É intencional — o awesome-pages exige `.pages` in-tree
    para o auto-nav; são YAML (invisíveis ao validador OKF) e inertes para qualquer gerador
    não-mkdocs. O ganho (nav que segue a árvore sem regen) supera o custo.
- **`requirements.txt`** — `mkdocs-material` + `mkdocs-awesome-pages-plugin` (pin exato fixado
  na implementação, verificado via context7).
- **CI opt-in** — `assets/mkdocs/ci-github-pages.yml`: workflow que roda `mkdocs gh-deploy`
  no push pra `main`. O `align` **oferece** copiar p/ `.github/workflows/docs.yml`; recusável
  (é específico de plataforma).

**Quem instala:** o **`quenching-align` ganha um passo** análogo ao passo 6 (instalação do hook):
oferece instalar/atualizar o setup mkdocs — carimba `mkdocs.yml` **se ausente** (não faz clobber
de um customizado; mostra diff se já existir), traz os `.pages` junto com o skeleton do home,
oferece `requirements.txt` e o CI. Como o nav é awesome-pages, **nenhum skill sincroniza nav**.

**Caveat de links (documentar em `documentation/index.md`):** links absolutos OKF
(`/docs/standards/...`) apontam para fora de um site enraizado em `documentation/` e **não
resolvem** no HTML. Mitigação: manter páginas do home autocontidas; linkar pra outros homes
com parcimônia.

### 4.4 Fusão `guides/` → `documentation/how-to/`

**Doutrina (definições da árvore canônica):**
- `taxonomy.md` — remover o home `guides/` (árvore, linha `guide` da tabela de `type`, boundary,
  parágrafo); adicionar `documentation/` (árvore, `type: documentation`, boundary, parágrafo com
  os 4 subfolders + nota concepts×knowledge). Corrigir o bullet de fronteira de `knowledge/` que cita guides.
- `okf-spec.md` — vocabulário de `type`: trocar `guide` por `documentation`.
- `homes.md` (roteamento do insert) — linha "how-to/tutorial" da tabela de classificação passa a
  `documentation/{how-to,getting-started}/` (`type: documentation`); atualizar tie-breakers que citam guides.

**Migração (`migration.md`):**
- Mapa de variantes: `docs/guias/`,`docs/howto/` → `docs/documentation/how-to/`;
  `docs/tutorials/` → `docs/documentation/getting-started/`; novas variantes
  `docs/`,`docs/user-docs/`,`docs/site/`,`docs/manual/`,`docs/wiki/` → `docs/documentation/`.
- **Regra de "home canônico aposentado" (nova):** um repo **já no canônico antigo**
  (`docs/guides/`) é realocado para `docs/documentation/how-to/`, com `type: guide` → `documentation`,
  sob confirmação própria (code-coupled se links alcançam código). Sem essa regra, o `align`
  veria `guides/` como conforme e não migraria.
- Migração de frontmatter: adicionar `type: guide` → `type: documentation`.
- Edge case: repo com `guides/` **e** `documentation/` → merge em `documentation/how-to/`
  (não clobber); conflitos sinalizados item-a-item.

### 4.5 Coordenação com o trabalho paralelo (backlog-idea + skills novos)

A implementação parte do **working tree atual** (não do último commit), que já contém, **não
commitado**, uma feature separada e dois skills novos. A minha feature empilha por cima:

- **Feature "backlog-idea"** ([spec](2026-07-08-backlog-idea-inbox-design.md)): reformula
  `backlog/` para "raw idea inbox" (`type: backlog-item` → `type: idea`, flat, feeding
  brainstorming), renomeia `assets/templates/backlog/backlog-item.md` → `idea.md`, e já
  editou o vocabulário de `type` (okf-spec.md), `taxonomy.md`, `concept-front.md`, README,
  `plugin.json`, `VERSION`, `marketplace.json`, `okf-validate.py`, entre outros.
  - **Interação com a minha mudança:** minha troca `guide` → `documentation` incide **nas
    mesmas linhas de enum** que a backlog-idea já tocou (a lista de `type` em `okf-spec.md`
    e `concept-front.md` hoje é `…vision, idea, guide, knowledge…` → passa a
    `…vision, idea, documentation, knowledge…`). O `type: idea` **coexiste** com
    `type: documentation`; sem conflito, apenas edições sequenciais.
- **Skills novos não rastreados** — `quenching-enrich/`, `quenching-visualize/` e
  `assets/tools/` (`okf-visualize.py` + `viewer/`). Já estão na varredura (§5); `viz.md` já
  lista `idea` no vocabulário e precisa da troca `guide` → `documentation`.
- **Versão:** release combinado `0.9.0`. **Não** re-bumpar `VERSION`/`plugin.json` (já em
  0.9.0); apenas conferir lockstep do `--version` do hook e acrescentar keywords/changelog.

## 5. Arquivos afetados (exaustivo)

### Criar
- `plugins/claude-quenching/assets/docs/documentation/index.md` (+ `.pages`)
- `.../documentation/getting-started/index.md` (+ `.pages`)
- `.../documentation/how-to/index.md` (+ `.pages`)
- `.../documentation/reference/index.md` (+ `.pages`)
- `.../documentation/concepts/index.md` (+ `.pages`)
- `plugins/claude-quenching/assets/mkdocs/mkdocs.yml.tmpl`
- `plugins/claude-quenching/assets/mkdocs/requirements.txt`
- `plugins/claude-quenching/assets/mkdocs/ci-github-pages.yml`
- (opcional) `plugins/claude-quenching/assets/mkdocs/README.md` — como o payload é carimbado

### Deletar
- `plugins/claude-quenching/assets/docs/guides/` (e seu `index.md`)

### Editar (doutrina + wiring — cada um verificado; "guide" às vezes é só "guidance")
- `skills/quenching-align/references/taxonomy.md` — remove guides, add documentation
- `skills/quenching-align/references/okf-spec.md` — type vocab `guide`→`documentation`
- `skills/quenching-align/references/migration.md` — variantes + regra home-aposentado + frontmatter
- `skills/quenching-align/references/conformance.md` — verificar menção a guides (provável: nenhuma)
- `skills/quenching-align/SKILL.md` — lista de instalação do skeleton + **novo passo mkdocs** + menção a guides
- `skills/quenching-insert/references/homes.md` — tabela de classificação + tie-breakers
- `skills/quenching-insert/SKILL.md` — menção a guides
- `skills/quenching-knowledge/SKILL.md` — boundary "Not for" cita guides
- `skills/quenching-knowledge-scan/SKILL.md` — lista de fatias de home (linha ~78: `guides/`→`documentation/`)
- `skills/quenching-harness/references/harness-routing.md` — menção a guides
- `skills/quenching-memory-to-docs/SKILL.md` + `references/memory-routing.md` — menção a guides
- `skills/quenching-enrich/references/sources.md` — linha ~51 "how-to → `guides/` unit" → `documentation/how-to/`
- `skills/quenching-visualize/references/viz.md` — linha ~44 type vocab `guide`→`documentation`
- `assets/docs/index.md` (raiz) — lista de homes + resumo de fronteiras
- `assets/docs/knowledge/index.md` — bullet "vs guides/" → documentation
- `assets/docs/communications/index.md` — cross-link a guides
- `assets/templates/concept-front.md` — dica de `type` `guide`→`documentation`
- `assets/templates/README.md` — verificar se lista molds/homes; add referência mkdocs se couber
- `assets/tools/okf-visualize.py` — linha ~69 chave de cor `"guide"` → `"documentation"`
- `assets/hooks/okf-validate.py` — `--version` → 0.9.0
- `README.md` — descrição de homes, nota de changelog (guides aposentado → documentation/how-to; novo setup mkdocs), cost model se algum sub-agent novo (não há)
- `plugins/claude-quenching/.claude-plugin/plugin.json` — **já em 0.9.0** (backlog-idea); só considerar keywords `mkdocs`,`documentation`
- `plugins/claude-quenching/VERSION` — **já em 0.9.0**; não re-bumpar
- `CLAUDE.md` (raiz do repo) — homes list + contagem de skills (nota: hoje diz "oito skills"; o repo já tem `enrich`/`visualize` — atualizar de passagem; arquivo untracked)

### Verificar (podem não precisar mudar)
- `.claude-plugin/marketplace.json` — confirmar que não pina versão do plugin.

## 6. Verificação

Sem framework de teste — grep + validador:

1. **Conformidade do skeleton:**
   `cd plugins/claude-quenching && python3 assets/hooks/okf-validate.py assets/docs`
   deve reportar `0 error(s), 0 warning(s)` após adicionar `documentation/` e remover `guides/`.
   Os 4 `index.md` sem frontmatter; `documentation/index.md` presente (sem `dir-no-index`);
   sem seed → sem risco de orphan/broken-link.
2. **`.pages` invisível ao validador:** confirmar que os arquivos `.pages` (não-`.md`) não
   disparam nenhum check (orphan/dir-no-index) do `okf-validate.py`.
3. **Varredura de referência-fantasma:**
   `grep -rn 'guides/' plugins/claude-quenching` só deve retornar menções intencionais
   (mapa de variantes em `migration.md`, nota de changelog no README). Idem
   `grep -rn 'type: guide\b\|"guide"' plugins/claude-quenching`.
4. **Validador inalterado:** é estrutural (sem allowlist de home); `--version` reporta 0.9.0.
5. **Visualizer:** `okf-visualize.py` roda sem erro e mostra `documentation` (homes derivados
   dinamicamente; só a chave de cor muda).
6. **Site builda:** com o payload carimbado num repo de teste, `pip install -r requirements.txt`
   + `mkdocs build` produz o site a partir de `docs/documentation/`, com `index.md` como landing
   de seção e nav espelhando a árvore.

## 7. Edge cases

- Repo com `guides/` **e** `documentation/`: merge em `documentation/how-to/`, sem clobber.
- `documentation/reference/` × `reference/` raiz: sem conflito no validador (caminhos distintos);
  nota de fronteira nos dois índices.
- Cross-links `/docs/...` de páginas do home não resolvem num site enraizado em `documentation/`:
  caveat documentado; recomendar páginas autocontidas.
- `mkdocs.yml` já existente e customizado no repo-alvo: `align` não faz clobber — mostra diff e oferece.
- "how-to" que é na verdade contrato → continua indo pra `standards/` (tie-breaker preservado).

## 8. A fixar na implementação

- Sintaxe/versões exatas de `mkdocs-material` e `mkdocs-awesome-pages-plugin`
  (features do tema, chaves do `.pages`, pin do `requirements.txt`) — verificar contra a doc
  atual **via context7** no momento da implementação, não de memória.
- Conteúdo exato dos 5 `index.md` do home e dos `.pages` (títulos/ordem das seções).
- Texto final da nota "Rendering this home" em `documentation/index.md`.
