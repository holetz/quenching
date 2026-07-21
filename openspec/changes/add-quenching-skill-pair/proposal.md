## Why

As skills dos repos-alvo hoje nascem desorganizadas: nomes sem relação legível com a
estrutura do monorepo, sem descoberta previsível (`/` + tab não conta a história), sem
registro no bundle OKF — um colaborador novo não sabe o que existe de automação nem onde
cada skill atua. O plugin já resolve esse problema para *conhecimento* (docs/) mas não
para a *superfície de automação* (.claude/skills + commands); este par fecha essa lacuna
com a mesma doutrina (taxonomia canônica, um plano → um OK, artefatos OKF derivados).

## What Changes

- Nova skill per-item **`quenching-skill`**: minta ou edita UMA skill conformante num
  repo-alvo — classifica no eixo único (domínio-vinculada × genérica), deriva nome e
  wrapper de command espelhado (`.claude/commands/<caminho>/<verbo>.md` →
  `/a:b:verbo`), redige o `SKILL.md` sob a doutrina de redação (previsibilidade,
  gatilhos por branch, no-op test, sem negação), e no tail regenera os artefatos OKF
  derivados (registro, glossário, log) com self-check.
- Nova skill sweep **`quenching-skill-align`**: varre `.claude/skills/` +
  `.claude/commands/` existentes de um repo-alvo e propõe UM plano de migração para a
  taxonomia (renomes, espelhamento de commands, criação da regra e do registro se
  faltarem), aplicado numa única confirmação.
- Dois artefatos OKF fixos passam a ser mantidos nos repos-alvo:
  `docs/standards/automation/skills.md` (a regra, `type: standard`, authority-graded) e
  `docs/documentation/reference/automation.md` (o registro, `type: documentation`, com
  zona GENERATED regenerada só pelas skills donas — padrão do `backlog/index.md`).
- Doutrina de redação de skills (adaptada de mattpocock/skills `writing-great-skills`)
  mora UMA vez em `quenching-skill/references/`; a sweep cita, nunca restata.
- Moldes novos em `assets/templates/` (skill, wrapper de command, registro, standard de
  taxonomia); tabelas do README/CLAUDE.md passam de dezoito para vinte skills; bump de
  versão do plugin.

## Capabilities

### New Capabilities

- `skill-authoring`: mint/edição de UMA skill conformante em repo-alvo — taxonomia de
  eixo único, nomeação canônica, wrapper de command espelhado, doutrina de redação, e o
  tail OKF (registro em zona GENERATED, glossário, log, self-check).
- `skill-alignment`: varredura de migração da superfície de automação existente de um
  repo-alvo para a taxonomia — inventário, plano único de renomes/espelhamentos/
  criações, uma confirmação, verificação final contra o registro.

### Modified Capabilities

<!-- nenhuma — o store de specs está vazio; nenhuma capability existente muda -->

## Impact

- `plugins/claude-quenching/skills/quenching-skill/` (nova: SKILL.md + references/ com a
  doutrina de redação e a taxonomia) e
  `plugins/claude-quenching/skills/quenching-skill-align/` (nova: SKILL.md citando as
  references da irmã).
- `plugins/claude-quenching/assets/templates/` — moldes novos (skill mold, command
  wrapper mold, `automation.md` do registro, standard de taxonomia).
- `plugins/claude-quenching/README.md` e `CLAUDE.md` (raiz) — tabelas de skills
  (dezoito → vinte) e seções de doutrina compartilhada.
- `plugins/claude-quenching/.claude-plugin/plugin.json`, `VERSION`,
  `.claude-plugin/marketplace.json` — bump de versão em lockstep.
- Nos repos-alvo (em uso): `.claude/skills/`, `.claude/commands/`,
  `docs/standards/automation/`, `docs/documentation/reference/` — sempre via um plano →
  um OK; nenhuma mudança no validador (`okf-validate.py`) é necessária: os artefatos
  novos usam `type`s já existentes (`standard`, `documentation`).
