## 1. Renomear skills quenching-native (dir + frontmatter em lockstep)

Para cada par abaixo: renomear o diretório da skill, ajustar `name:` na frontmatter do
`SKILL.md`, e conferir `dir basename == name:`.

- [x] 1.1 `skills/quenching-insert/` → `skills/quenching-add/` (`name: quenching-add`)
- [x] 1.2 `skills/quenching-enrich/` → `skills/quenching-import/` (`name: quenching-import`)
- [x] 1.3 `skills/quenching-knowledge/` → `skills/quenching-learn/` (`name: quenching-learn`)
- [x] 1.4 `skills/quenching-glossary/` → `skills/quenching-define/` (`name: quenching-define`)
- [x] 1.5 `skills/quenching-knowledge-scan/` → `skills/quenching-glossary-backfill/`
      (`name: quenching-glossary-backfill`)
- [x] 1.6 `skills/quenching-memory-to-docs/` → `skills/quenching-import-memory/`
      (`name: quenching-import-memory`)
- [x] 1.7 `skills/quenching-cycle/` → `skills/quenching-converge/` (`name: quenching-converge`)
- [x] 1.8 As oito skills `openspec-*` e as três `quenching-align/-harness/-skill/-skill-align`
      NÃO renomeiam (confirmar que ficaram intocadas no diff)

## 2. Renomear/mover wrappers de comando

O corpo de cada wrapper invoca `claude-quenching:<skill>` — atualizar o nome da skill no
corpo junto com o nome do arquivo.

- [x] 2.1 `commands/opsx/`: `apply.md`→`implement.md`, `update.md`→`revise.md`,
      `sync.md`→`sync-specs.md`, `backlog.md`→`backlog-add.md` (só o nome do arquivo e o
      `description`; o corpo já aponta para a skill `openspec-*` inalterada)
- [x] 2.2 `commands/docs/`: renomear `insert.md`→`add.md`, `enrich.md`→`import.md`,
      `knowledge.md`→`learn.md`, `glossary.md`→`define.md`,
      `knowledge-scan.md`→`glossary-backfill.md`, `memory-to-docs.md`→`import-memory.md`,
      `cycle.md`→`converge.md` — e no corpo de cada um trocar
      `claude-quenching:quenching-<antigo>` pelo nome novo da skill (task 1)
- [x] 2.3 `commands/docs/align.md` e `commands/docs/harness.md`: intocados
- [x] 2.4 Criar `commands/skill/new.md` (a partir de `commands/docs/skill.md`) e
      `commands/skill/align.md` (a partir de `commands/docs/skill-align.md`), corpos
      apontando para `quenching-skill` / `quenching-skill-align` (nomes de skill mantidos);
      remover `commands/docs/skill.md` e `commands/docs/skill-align.md`
- [x] 2.5 Conferir bijeção: 19 wrappers, cada um resolve para exatamente uma skill existente

## 3. Reparar referências cruzadas entre skills

- [x] 3.1 `quenching-converge` (ex-cycle): em `SKILL.md` e `references/cycle.md`, trocar o
      pipeline citado — `quenching-align` (mantém) → `quenching-import-memory` →
      `quenching-harness` (mantém) → `quenching-glossary-backfill`; e toda auto-referência
      a `quenching-cycle` vira `quenching-converge`
- [x] 3.2 `quenching-skill-align/SKILL.md`: citações a `quenching-skill` ficam (nome mantido)
      — confirmar que não citam nenhum nome antigo
- [x] 3.3 Boundary "Not for: X → other-skill" na `description` de cada `SKILL.md`: atualizar
      todo ponteiro para um nome renomeado (ex.: `quenching-insert`→`quenching-add`,
      `quenching-memory-to-docs`→`quenching-import-memory`) — varrer as 19 skills
- [x] 3.4 References que citam nomes antigos (`quenching-insert/references/homes.md` — agora
      `quenching-add/…`, `quenching-enrich/references/sources.md`, os `openspec-*/…` que
      citam `quenching-insert`/`quenching-knowledge`/`quenching-glossary`): atualizar cada
      ocorrência para o nome novo

## 4. Superfície documental do plugin

- [x] 4.1 `CLAUDE.md` raiz — tabela grande das skills: renomear as sete linhas afetadas e a
      linha de papel de `skill`/`skill-align` (namespace `skill:`); atualizar a lista de
      "procedimento compartilhado" (paths `quenching-insert/references/homes.md` →
      `quenching-add/…`); atualizar o parágrafo dos namespaces (`/docs:*` deixa de cobrir
      skill/skill-align → `/skill:*`)
- [x] 4.2 `CLAUDE.md` raiz — as DUAS regras "must survive any refactor": a que cita
      `quenching-memory-to-docs` vira `quenching-import-memory`; a que cita
      `quenching-cycle/references/cycle.md` vira `quenching-converge/references/cycle.md`;
      conferir a que cita `quenching-align` (mantém)
- [x] 4.3 `plugins/claude-quenching/README.md` — tabela de skills, tabela de cost-model,
      qualquer menção a `docs:`/`opsx:` renomeado e ao novo `skill:`
- [x] 4.4 READMEs de skill afetados (`skills/*/README.md` se existirem) e
      `assets/templates/automation/registry.md` + `skills-standard.md` — exemplos/nomes que
      citem comandos renomeados
- [x] 4.5 `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` — atualizar
      keywords/descrição se citarem um nome renomeado (grep confirmou: manifests não citam
      hoje — verificar após as edições de prosa)

## 5. Release

- [x] 5.1 Bump de versão em lockstep: `plugin.json` + `VERSION` + entrada do plugin no
      `.claude-plugin/marketplace.json` (minor — renome de superfície, sem mudança de
      comportamento); manter o `VERSION` do `okf-validate.py` em lockstep se a política do
      repo exigir (nenhuma mudança no script, mas o par plugin.json/VERSION sobe)

## 6. Retirar a exploração-seed (se aplicável)

- [x] 6.1 Não há task-seed em `openspec/backlog/` para esta change (nasceu de explore); nada
      a retirar

## 7. Verificação

- [x] 7.1 Grep de resíduo — nenhum nome antigo sobrevive fora de `openspec/changes/`:
      `grep -rnE 'quenching-(insert|enrich|knowledge|glossary|knowledge-scan|memory-to-docs|cycle)\b' plugins/ CLAUDE.md` retorna vazio; idem para
      comandos `docs:(insert|enrich|knowledge|glossary|knowledge-scan|memory-to-docs|cycle|skill|skill-align)` e `opsx:(apply|update|sync|backlog)\b`
- [x] 7.2 Bijeção e resolução: 19 dirs de skill, 19 wrappers; todo wrapper invoca uma skill
      existente; todo `dir basename == name:`
- [x] 7.3 Caps preservados: nenhuma `description` ultrapassa 1.536 chars após a edição do
      boundary; nenhum `context: fork` novo; corpos < 500 linhas
- [x] 7.4 `python3 plugins/claude-quenching/assets/hooks/okf-validate.py plugins/claude-quenching/assets/docs`
      continua `0 error(s), 0 warning(s)` (skeleton não tocado)
- [x] 7.5 Namespaces honestos: `commands/skill/` existe com `new.md`+`align.md`;
      `commands/docs/` não contém mais `skill*.md`
