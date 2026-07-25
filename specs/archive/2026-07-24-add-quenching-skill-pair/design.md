## Context

O plugin resolve organização de *conhecimento* (docs/ OKF) mas não da *superfície de
automação* dos repos-alvo: `.claude/skills/` e `.claude/commands/` crescem sem taxonomia,
sem relação legível com a estrutura do monorepo e sem registro no bundle. A exploração
(openspec-explore, 2026-07-20) fixou as decisões de base; este design as consolida para
implementação. Fonte da doutrina de redação: mattpocock/skills `writing-great-skills`
(previsibilidade como virtude-raiz; description com um gatilho por branch; hierarquia
in-skill steps → in-skill reference → references/; modos de falha: conclusão prematura,
duplicação, sedimento, sprawl, no-op, negação).

Restrições do repo (CLAUDE.md): description ≤ 1.536 chars com gatilhos na segunda frase;
corpo < 500 linhas; procedimento compartilhado mora UMA vez no dono e é citado; nunca
`context: fork` em skill com confirmação mid-flow; artefatos shipped em inglês.

## Goals / Non-Goals

**Goals:**
- `quenching-skill` (per-item) e `quenching-skill-align` (sweep) prontas no plugin, com o
  padrão de grão já usado por insert/align.
- Taxonomia de eixo único formalizada e enforçável: domínio-vinculada (nome =
  caminho-achatado + wrapper espelhado) × genérica (verbo-objeto, nunca espelhada).
- Dois artefatos OKF mantidos nos repos-alvo: regra (`standards/automation/skills.md`) e
  registro com zona GENERATED (`documentation/reference/automation.md`).
- Moldes em `assets/templates/` para tudo que as skills stampam.

**Non-Goals:**
- Mudar o validador `okf-validate.py` (os artefatos usam `type`s existentes: `standard`,
  `documentation`; `.claude/` está fora do escopo do validador).
- Suporte prescritivo a directory-scoped skills (`<pasta>/.claude/skills/`) — anotado como
  variação na regra, não gerado pelo mint.
- Entrar no loop do `quenching-cycle` — ambas são ferramentas on-demand.
- Gerir skills de plugins de terceiros instalados no repo-alvo (só a superfície local).

## Decisions

1. **Commands aninhados como mecanismo de espelhamento (mecanismo A), não
   directory-scoped skills (B).** A é o padrão da casa (`commands/opsx/` →
   `/opsx:*`), tem descoberta via `/`+tab e mantém `.claude/` auditável num lugar só. B
   elimina drift mas dispersa a superfície e tem suporte menos maduro. B fica documentado
   como variação aceita na regra de taxonomia; o mint gera sempre A. Separador é o `:`
   nativo — `::` do enunciado original mapeia para `:`.

2. **Nome da skill domínio-vinculada = caminho-achatado + verbo**
   (`communications-teams-create`): o nome sozinho conta onde atua, e o wrapper
   `.claude/commands/communications/teams/create.md` dá a invocação navegável. Alternativa
   descartada: nome curto + só o command carregando o caminho — quebraria a busca por nome
   em `.claude/skills/`.

3. **Registro em `documentation/reference/automation.md`, não em `catalog/`.** O
   vocabulário de `type` do `catalog/` é fixo (`system`/`schema`/`table`) e modela ativos
   de dados; skills não têm slot ali. Diátaxis "reference" é exatamente listagem
   autoritativa de maquinaria. O anti-drift vem da **zona GENERATED** (padrão
   `backlog/index.md`): só as skills donas escrevem entre os marcadores, e o self-check
   diffa a zona contra `.claude/skills/*/SKILL.md`. Alternativa descartada: nenhum
   registro em docs/ — perderia a visão do novato no bundle e no `quenching-visualize`.

4. **Regra como `standard` authority-graded, oferecida na primeira execução** — nasce
   `authority: background` (acordada-mas-não-provada) e gradua a `current` quando o time a
   valida na prática; nunca criada sem OK. Sem bundle OKF: mint prossegue (skill +
   wrapper), tail OKF silenciosamente pulado, sugerir `quenching-align` uma vez.

5. **Doutrina compartilhada mora na `quenching-skill`** (dona), em dois references:
   `references/doctrine.md` (redação — adaptação Pocock) e `references/taxonomy.md`
   (eixo, nomeação, espelhamento, formato do registro/zona). `quenching-skill-align` cita
   ambos e não restata — mesmo padrão insert(homes.md)/align(conformance.md).

6. **Sem `context: fork` em nenhuma das duas** — ambas gateiam em confirmação mid-flow
   (regra do CLAUDE.md que sobrevive a qualquer refactor).

7. **Molde do wrapper = o padrão opsx literal**: frontmatter `description` +
   `argument-hint`, corpo de uma frase invocando a skill via Skill tool com `$ARGUMENTS`.

8. **Zona GENERATED do registro**: marcadores `<!-- GENERATED:BEGIN -->` /
   `<!-- GENERATED:END -->`, tabela `| Comando | Skill | Atua em | Gatilho típico |`,
   linhas ordenadas por comando; derivada exclusivamente da frontmatter dos `SKILL.md`
   locais. Conteúdo curado (prosa, link para a regra) vive fora dos marcadores.

## Risks / Trade-offs

- [Drift registro × `.claude/skills/` editado à mão fora das skills] → self-check em todo
  mint/edit + verificação pós-apply da sweep regeneram a zona; a regra declara as skills
  donas como únicas editoras da zona.
- [Renome de skill referenciada por código/CI quebra o repo-alvo] → a sweep confirma
  renomes code-coupled individualmente (spec `skill-alignment`), padrão já usado por
  `quenching-align`.
- [Classificação ambígua (skill servindo várias pastas)] → keep-and-report: fica intocada
  e listada como unroutable; nunca forçada num eixo.
- [Sprawl da própria doutrina (ironia: a skill de escrever skills mal escrita)] →
  description das duas dentro do cap com gatilhos na segunda frase; doutrina em
  references/ carregada só em execução; corpo < 500 linhas verificado no apply.
- [Duas capabilities numa change só = apply maior] → tasks.md sequencia
  quenching-skill (dona das references) antes da sweep; a sweep só cita.

## Migration Plan

Sem migração de dados: skills novas são aditivas ao plugin. Release = bump em lockstep
(`plugin.json` + `VERSION` + entrada no `marketplace.json`) — dezoito → vinte skills nas
tabelas de README/CLAUDE.md. Rollback = remover as duas pastas de skill e reverter o bump.
Nos repos-alvo nada muda até alguém invocar as skills (todas as escritas gateiam em OK).

## Open Questions

- Nenhuma bloqueante. (Menor, resolvível no apply: se o registro lista também os commands
  `opsx`/plugin — decisão default: não; a zona lista só a superfície local do repo-alvo,
  a prosa curada pode apontar para os plugins instalados.)
