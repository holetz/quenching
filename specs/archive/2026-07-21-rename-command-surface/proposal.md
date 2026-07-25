## Why

Os nomes de skill e comando de hoje **escondem** a atuação em vez de revelá-la, e o
namespace `docs:` **mente** para ~4 dos seus 11 comandos: `skill`/`skill-align` mexem em
`.claude/` (não em `docs/`) e `harness` mexe em `CLAUDE.md`. Alguns comandos são jargão
(`opsx:apply`), colidem com um irmão (`opsx:update` × `apply`), pedem um objeto que o nome
não dá (`opsx:sync` — "sync o quê→onde?"), leem como consulta em vez de ação (`opsx:backlog`),
são opacos (`docs:cycle`), ou **mentem** direto (`docs:knowledge-scan` varre para preencher o
*glossário*, não "escaneia conhecimento"). O usuário paga esse custo toda vez que abre o menu
`/`. Esta change torna cada nome de comando um verbo que revela a ação e cada namespace
honesto quanto ao artefato que toca — em inglês, cross-repo greppável.

## What Changes

- **Lado `opsx:` — mantém o namespace e os nomes de skill, clareia só os comandos.** As seis
  skills adaptadas 1:1 do CLI upstream (`openspec-*`, com `generatedBy`) mantêm o nome de
  skill (alinhamento upstream — a razão de manter `opsx:`); só o comando visível muda:
  `apply→implement`, `update→revise`, `sync→sync-specs`, `backlog→backlog-add`.
  `explore`, `propose`, `archive`, `backlog-triage` já são claros e ficam.
- **Lado `docs:` — divide em `docs:` (bundle OKF) + novo namespace `skill:` (automação
  `.claude/`).** Renomeia comando **e** skill quenching-native em lockstep:
  `insert→add`, `enrich→import`, `knowledge→learn`, `glossary→define`,
  `knowledge-scan→glossary-backfill` (corrige o nome que mente), `memory-to-docs→import-memory`,
  `cycle→converge`. `align` e `harness` ficam (verbo-núcleo; termo do glossário). `skill` e
  `skill-align` saem de `docs:` para `skill:new` e `skill:align` — mantêm o nome de skill
  (`quenching-skill`, `quenching-skill-align`), só mudam de namespace de comando.
- **Invariantes preservados:** 19 skills / 19 wrappers (um-skill-um-wrapper intacto — nenhuma
  consolidação); nenhum `context: fork` novo; nenhuma mudança no validador
  (`okf-validate.py`) — nenhum `type` nem regra OKF muda.
- **Corte limpo, sem aliases:** os nomes antigos são removidos, não mantidos como alias
  (superfície descoberta via menu `/`; um alias stale reintroduziria a ambiguidade que
  removemos). Registrado no `log.md` como decisão.
- **Superfície documental em lockstep:** tabela grande do `CLAUDE.md` raiz, `README.md` do
  plugin e READMEs de skill, keywords de `marketplace.json`/`plugin.json`, os moldes
  `assets/templates/automation/registry.md` + `skills-standard.md`, e as duas regras
  "must survive any refactor" do `CLAUDE.md` que citam skills pelo nome. Bump de versão.

## Capabilities

### New Capabilities

- `command-naming`: a convenção de nomeação da superfície de comando/skill do plugin —
  comandos verbo-primeiro que revelam a ação, namespaces honestos por sujeito
  (`opsx:` ciclo de mudança, `docs:` bundle OKF, `skill:` automação `.claude/`), preservação
  do namespace `opsx:` e dos nomes `openspec-*` upstream, bijeção 19:19 um-skill-um-wrapper,
  e corte limpo sem aliases.

### Modified Capabilities

<!-- nenhuma — o store de specs está vazio; nenhuma capability existente muda -->

## Impact

- `plugins/claude-quenching/skills/` — renome de 8 dirs de skill quenching-native
  (`quenching-insert`→`quenching-add`, `-enrich`→`-import`, `-knowledge`→`-learn`,
  `-glossary`→`-define`, `-knowledge-scan`→`-glossary-backfill`,
  `-memory-to-docs`→`-import-memory`, `-cycle`→`-converge`); `name:`/`description`/boundary
  de cada `SKILL.md` afetado; referências cruzadas (`quenching-converge` cita o pipeline por
  nome; `quenching-skill-align` cita `quenching-skill`). As 8 skills `openspec-*` não mudam
  de nome.
- `plugins/claude-quenching/commands/` — renome/movimento de wrappers: `commands/opsx/`
  (4 renomes), `commands/docs/` (7 renomes + remoção de `skill*`), novo `commands/skill/`
  (`new.md`, `align.md`).
- `plugins/claude-quenching/CLAUDE.md`? não existe — a doutrina mora no `CLAUDE.md` raiz;
  ambas as regras "must survive" e a tabela grande atualizam lá.
- `plugins/claude-quenching/README.md` + READMEs de skill; `.claude-plugin/plugin.json`,
  `VERSION`, `.claude-plugin/marketplace.json` (bump em lockstep, minor — só renomes);
  `assets/templates/automation/registry.md` + `skills-standard.md` (exemplos/nomes).
- Nenhuma mudança em `assets/hooks/okf-validate.py` nem no skeleton `assets/docs/`.
