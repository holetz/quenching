## 1. References da quenching-skill (a dona da doutrina)

- [x] 1.1 Escrever `skills/quenching-skill/references/doctrine.md` — doutrina de redação
      adaptada de mattpocock/skills `writing-great-skills`: previsibilidade como
      virtude-raiz, description com conceito líder + um gatilho por branch, hierarquia
      (in-skill steps → in-skill reference → references/), critérios de conclusão
      checáveis, no-op test, prescrição positiva (sem negação), modos de falha nomeados
      (conclusão prematura, duplicação, sedimento, sprawl)
- [x] 1.2 Escrever `skills/quenching-skill/references/taxonomy.md` — o eixo único
      (domínio-vinculada × genérica) com o teste de classificação, nomeação
      (caminho-achatado + verbo × verbo-objeto), regra de espelhamento
      (`.claude/commands/<caminho>/<verbo>.md` → `/a:b:verbo`, separador `:`,
      genérica nunca espelhada), variação directory-scoped anotada (não gerada), e o
      formato do registro (marcadores GENERATED, colunas, ordenação, donas da zona)

## 2. Moldes em assets/templates/automation/

- [x] 2.1 Criar `assets/templates/automation/skill.md` — molde de SKILL.md conformante à
      doutrina (frontmatter name/description/when_to_use com placeholder de gatilhos,
      esqueleto de steps com critérios checáveis)
- [x] 2.2 Criar `assets/templates/automation/command.md` — molde do wrapper fino no padrão
      opsx (frontmatter description + argument-hint, corpo de uma frase invocando a skill
      via Skill tool com `$ARGUMENTS`)
- [x] 2.3 Criar `assets/templates/automation/registry.md` — molde de
      `docs/documentation/reference/automation.md` (`type: documentation`, prosa curada
      apontando para a regra, zona `<!-- GENERATED:BEGIN/END -->` com a tabela
      `| Comando | Skill | Atua em | Gatilho típico |`)
- [x] 2.4 Criar `assets/templates/automation/skills-standard.md` — molde de
      `docs/standards/automation/skills.md` (`type: standard`,
      `authority: background` de nascença, a regra de taxonomia/nomeação/espelhamento)
- [x] 2.5 Atualizar `assets/templates/README.md` com a família `automation/`

## 3. Skill quenching-skill (per-item)

- [x] 3.1 Escrever `skills/quenching-skill/SKILL.md`: fluxo mint/edit — ler regra (ou
      oferecer criá-la; sem bundle OKF: prosseguir sem tail e sugerir `quenching-align`
      uma vez) → classificar no eixo → derivar nome + wrapper → redigir sob
      `references/doctrine.md` → UM plano → um OK → escrever → tail (regenerar zona
      GENERATED, glossário se batizou termo, log.md, self-check com diff registro ×
      `.claude/skills/*`)
- [x] 3.2 Frontmatter da skill: description ≤ 1.536 chars, gatilhos na segunda frase
      ("create a skill", "nova skill para X", "organizar skill", …), boundary "Not for:
      migrar as skills existentes → quenching-skill-align; um doc no bundle →
      quenching-insert"; sem `context: fork`

## 4. Skill quenching-skill-align (sweep)

- [x] 4.1 Escrever `skills/quenching-skill-align/SKILL.md`: inventário read-only
      (`.claude/skills/`, `.claude/commands/`, directory-scoped `**/.claude/skills/`) →
      UM plano consolidado (renomes, espelhamentos, regra+registro se faltarem;
      keep-and-report para inclassificáveis; nunca deletar sem palavra humana) → um OK
      (renome code-coupled confirma individualmente) → aplicar → verificação pós-apply
      (zona regenerada, todo wrapper resolve, registro == `.claude/skills/`)
- [x] 4.2 Frontmatter da sweep: description ≤ 1.536 chars com gatilhos ("organize as
      skills", "migrar skills para a taxonomia", "alinhar commands ao monorepo", …),
      boundary "Not for: criar UMA skill → quenching-skill"; cita
      `../quenching-skill/references/{doctrine,taxonomy}.md` sem restatar; sem
      `context: fork`

## 5. Documentação do plugin

- [x] 5.1 Atualizar a tabela de skills do `CLAUDE.md` raiz (dezoito → vinte, com as duas
      linhas novas e papel de cada uma) e a lista de procedimento compartilhado (doctrine/
      taxonomy da quenching-skill como doutrina citada pela sweep)
- [x] 5.2 Atualizar `plugins/claude-quenching/README.md`: tabela de skills, seção da
      família automation (taxonomia + registro), linha das duas skills na tabela de
      cost-model (ambas sem sub-agents — modelo padrão)
- [x] 5.3 Atualizar `plugins/claude-quenching/.claude-plugin/plugin.json` keywords se a
      família nova pedir termo novo (ex.: "skill-authoring")

## 6. Release

- [x] 6.1 Bump de versão em lockstep: `plugin.json` + `VERSION` + entrada do plugin no
      `.claude-plugin/marketplace.json` (minor — duas skills novas)

## 7. Verificação

- [x] 7.1 `python3 assets/hooks/okf-validate.py assets/docs` continua `0 error(s),
      0 warning(s)` (o skeleton não é tocado por esta change)
- [x] 7.2 Checar caps: descriptions das duas skills ≤ 1.536 chars com gatilhos na segunda
      frase; corpos de SKILL.md < 500 linhas; nenhum `context: fork`
- [x] 7.3 Smoke de coerência: toda citação cruzada resolve (sweep → references da irmã;
      SKILL.md → moldes em `assets/templates/automation/`); tabelas README/CLAUDE.md
      dizem "vinte" e listam as duas
