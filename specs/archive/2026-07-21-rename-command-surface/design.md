## Context

A superfície do plugin são 19 skills espelhadas por 19 wrappers em dois namespaces de
comando (`/opsx:*`, `/docs:*`). A exploração (openspec-explore, 2026-07-21) auditou os nomes
como o usuário os vê no menu `/` e fixou três alavancas: renomear para o verbo revelar a
ação, re-agrupar namespaces por sujeito, e (descartado nesta change) consolidar entradas. O
usuário escolheu **renomear + re-agrupar**, mantendo `opsx:` e a bijeção 19:19.

Restrições do repo (CLAUDE.md): nomes de pasta, slugs, chaves e `type` são inglês canônico
(cross-repo greppável); todo skill tem exatamente um wrapper; `/opsx:*` espelha os oito
`openspec-*` e `/docs:*` espelha os onze `quenching-*`; nunca `context: fork`. Duas regras
"must survive any refactor" do CLAUDE.md citam skills pelo nome (`quenching-memory-to-docs`)
— renomeá-las obriga a atualizar essas regras no mesmo passo.

## Goals / Non-Goals

**Goals:**
- Cada nome de comando é um verbo que revela a ação; cada namespace é honesto quanto ao
  artefato que toca.
- Um novo namespace `skill:` separa a automação `.claude/` do bundle `docs/`.
- Preservar `opsx:` e os nomes `openspec-*` upstream; preservar a bijeção 19:19.
- Superfície documental (CLAUDE.md, READMEs, keywords, moldes) coerente com os nomes novos.

**Non-Goals:**
- Consolidar pares item/varredura num comando com flag (alavanca 3 — descartada aqui; quebra
  um-skill-um-wrapper).
- Mudar `okf-validate.py`, o skeleton `assets/docs/`, ou qualquer `type`/regra OKF.
- Manter aliases dos nomes antigos (decisão 4).
- Renomear as oito skills `openspec-*` (decisão 1).

## The mapping (canonical)

**`opsx:` — namespace e nomes de skill mantidos; só o comando muda:**

| Comando hoje | → Comando | Skill (inalterada) |
| --- | --- | --- |
| `opsx:apply` | `opsx:implement` | `openspec-apply-change` |
| `opsx:update` | `opsx:revise` | `openspec-update-change` |
| `opsx:sync` | `opsx:sync-specs` | `openspec-sync-specs` |
| `opsx:backlog` | `opsx:backlog-add` | `openspec-backlog` |
| `opsx:explore` `opsx:propose` `opsx:archive` `opsx:backlog-triage` | *(mantidos)* | *(mantidas)* |

**`docs:` → `docs:` + `skill:` — comando e skill renomeiam em lockstep:**

| Comando hoje | → Comando | Skill hoje | → Skill |
| --- | --- | --- | --- |
| `docs:insert` | `docs:add` | `quenching-insert` | `quenching-add` |
| `docs:enrich` | `docs:import` | `quenching-enrich` | `quenching-import` |
| `docs:knowledge` | `docs:learn` | `quenching-knowledge` | `quenching-learn` |
| `docs:glossary` | `docs:define` | `quenching-glossary` | `quenching-define` |
| `docs:knowledge-scan` | `docs:glossary-backfill` | `quenching-knowledge-scan` | `quenching-glossary-backfill` |
| `docs:memory-to-docs` | `docs:import-memory` | `quenching-memory-to-docs` | `quenching-import-memory` |
| `docs:cycle` | `docs:converge` | `quenching-cycle` | `quenching-converge` |
| `docs:align` | *(mantido)* | `quenching-align` | *(mantida)* |
| `docs:harness` | *(mantido)* | `quenching-harness` | *(mantida)* |
| `docs:skill` | `skill:new` | `quenching-skill` | *(mantida)* |
| `docs:skill-align` | `skill:align` | `quenching-skill-align` | *(mantida)* |

Superfície final para o usuário:
```
opsx:   explore propose implement revise sync-specs archive backlog-add backlog-triage
docs:   align add import learn define glossary-backfill import-memory converge harness
skill:  new align
```

## Decisions

1. **Skills `openspec-*` mantêm o nome; só o comando muda.** Foram adaptadas 1:1 do CLI
   upstream (`generatedBy`); manter `opsx:` foi escolha de alinhamento upstream, então o nome
   de skill segue upstream também. O espelho já não é igualdade de nome hoje (`apply` ↔
   `apply-change`), logo `opsx:implement` → `openspec-apply-change` é consistente. As duas
   skills quenching-native do lado opsx (`openspec-backlog`, `openspec-backlog-triage`) também
   mantêm o nome — só `backlog`→`backlog-add` muda no comando, por simetria com `backlog-triage`.

2. **Skills quenching-native renomeiam em lockstep com o comando.** Sem amarra upstream; o
   nome de skill e o de comando devem contar a mesma história e serem greppáveis juntos.

3. **Novo namespace `skill:` para a automação `.claude/`.** `skill`/`skill-align` não tocam
   `docs/` — mantê-las em `docs:` era a mentira mais gritante do namespace. `commands/skill/`
   passa a existir; `commands/docs/skill*.md` some.

4. **Corte limpo, sem aliases.** A superfície é descoberta pelo menu `/`; um alias stale
   reintroduziria a ambiguidade que estamos removendo e dobraria a contagem visível. O
   plugin versiona em lockstep e o upgrade é atômico. A troca é registrada uma vez no
   `log.md` do bundle-alvo quando a skill roda; no plugin, o bump de versão é o marco.

5. **Um-skill-um-wrapper preservado (19:19).** Nada de consolidar pares item/varredura — essa
   era a alavanca 3, fora de escopo. A change só altera nomes e namespaces.

6. **`docs:align` e `docs:harness` mantidos.** `align` é o verbo-núcleo do plugin
   (quenching = "align/force-conform"); `harness` é termo do glossário (CLAUDE.md/AGENTS.md =
   "the harness"), e a doutrina do próprio plugin manda falar a língua do repo.

## Open Questions (bikesheds — defaults escolhidos, revisitáveis no apply)

- **`docs:harness`** — mantido (termo do glossário). Alternativa: `docs:slim-harness`
  (autoexplicativo p/ novato). *Default: manter.*
- **`skill:new`** — a skill também *edita*, então `new` é levemente estreito. Alternativa:
  `skill:add` (semântica add-or-update). *Default: `skill:new`.*
- **`opsx:sync-specs`** — clareza vs. brevidade. Alternativa: `opsx:sync`. *Default:
  `sync-specs` (nomeia o objeto).*
- **`docs:learn` × `docs:add`** — os dois "adicionam ao bundle"; a distinção (saber genérico
  vs. doc qualquer) é inerente ao design das skills, não ao nome. *Default: manter distintos.*

Nenhuma é bloqueante para o apply; flipar qualquer uma é editar uma célula do mapa acima e as
tarefas correspondentes.

## Risks / Trade-offs

- [Renome de skill deixa uma referência cruzada órfã] → `tasks.md` enumera os citadores por
  nome: `quenching-converge` cita o pipeline (align/import-memory/harness/glossary-backfill),
  `quenching-skill-align` cita `quenching-skill`, e as duas regras "must survive" do CLAUDE.md
  citam `quenching-memory-to-docs`. Grep final (task 7) por todo nome antigo garante zero
  resíduo.
- [Usuário com memória muscular do nome antigo] → aceito: corte limpo (decisão 4); os nomes
  novos são mais autoexplicativos, e o menu `/` é a descoberta canônica.
- [Nome de pasta de skill ≠ `name:` da frontmatter após renome] → cada renome de dir move o
  `name:` no mesmo passo; o self-check de nome (dir == `name:`) roda por skill afetada.
- [Namespace `skill:` sem precedente no plugin] → é só um diretório novo em `commands/`; a
  invocação `/claude-quenching:skill:new` deriva do caminho, igual a `opsx`/`docs`.

## Migration Plan

Sem migração de dados. Ordem no apply: (1) renomear dirs de skill quenching-native e ajustar
frontmatter; (2) renomear/mover wrappers e criar `commands/skill/`; (3) reparar referências
cruzadas entre skills; (4) atualizar CLAUDE.md (tabela + duas regras), READMEs, keywords,
moldes; (5) bump de versão em lockstep; (6) grep de resíduo. Rollback = reverter o commit do
renome (é tudo movimento de arquivo + edição de texto; nenhum estado gerado). Repos-alvo já
instalados recebem os nomes novos no próximo upgrade do plugin.
