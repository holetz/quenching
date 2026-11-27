# Extensão ou plugin do VS Code para o quenching — avaliação

**Medição de 2026-11-25.** Evidência da spec 466 (épico 453). O ADR `docs/decisions/0021-no-vscode-extension.md` carrega a decisão; o guia
`docs/how-to/work-in-vs-code.md` carrega o uso. Este artefato é a
matriz que os dois citam: o que cada candidata acrescenta, o que duplica, o que custa e o veredito.

## Condições da medição

| Campo | Valor |
|---|---|
| Data | 2026-11-25 |
| Cliente | Visual Studio Code – Insiders 1.149.0-insider (commit `d8b0b6fc93e3027e3dae61d348d73f8b3f33c59c`) |
| Extensão do Copilot | `GitHub.copilot-chat` 0.77.2026112501 |
| Extensões instaladas | 23 ids únicos em 28 diretórios de versão (o cliente guarda duas versões de algumas) |
| Inventário | `python3 scripts/copilot_bench.py --target . --json` → `measurements.clients.extensions` |
| Fonte do inventário | 452, H9; a sonda corrigida nesta spec conta ids, não diretórios |

```bash
python3 scripts/copilot_bench.py --target . --json \
  | python3 -c "import json,sys; c=json.load(sys.stdin)['measurements']['clients']['extensions']; print(c['count'], c['directories'])"
# 23 28
```

Os 23 ids instalados, medidos em 2026-11-25:

```text
adrianwilczynski.terminal-commands
anthropic.claude-code
astral-sh.ty
charliermarsh.ruff
cweijan.vscode-office
databricks.databricks
dracula-theme.theme-dracula
kevinrose.vsc-python-indent
mgesbert.python-path
mhutchie.git-graph
ms-azuretools.vscode-containers
ms-python.debugpy
ms-python.python
ms-python.vscode-python-envs
ms-toolsai.datawrangler
ms-toolsai.jupyter
ms-toolsai.jupyter-keymap
ms-toolsai.jupyter-renderers
ms-vscode-remote.remote-containers
pkief.material-icon-theme
redhat.vscode-yaml
southsystem.4devstudio
tamasfe.even-better-toml
```

Nenhum id instalado é o GitHub Pull Requests nem um gerenciador de worktree; o
`anthropic.claude-code` é a extensão do harness Claude Code, não do Copilot.

## O que o cliente já lê

| Capacidade | Artefato deployado | Evidência |
| --- | --- | --- |
| Skills | `.claude/skills` (ponte) e `.agents/skills` (camada genérica) | 452 H1 `confirmed`; 455 `## Design` |
| Agentes | `.claude/agents`; `.github/agents` com `shared.projections: ["github"]` | 452 H2 `confirmed`; `agents.md` §The client projections |
| Hooks | `.claude/settings.json` | 452 H4 `confirmed` no Linux; fail-open por timeout `unmeasured-live` |
| MCP | `.mcp.json` (configuração nativa, lida no host) | `mcp.md`; `deploy/mcpfiles.py`; 452 H3 |
| Regras por caminho | `.claude/rules` e `.github/instructions` | 463; 452 H11 `unmeasured-live` |
| Settings e tarefas | `.vscode/settings.json` e `.vscode/tasks.json` | 457 e 460 |
| Slots | `cq git worktree workspace --write` → `.code-workspace` + `code -n` | 460 |
| Worktrees | Source Control Repositories → Worktrees | `branches-worktrees.md`; 458 |

A única capacidade da lista do `## Problem` que não está nessa tabela é a **status bar**: uma linha
persistente com spec, slot, custo e cota. Tudo o mais o cliente lê do que o deploy escreve.

## As candidatas

| # | Candidata | Rota | O que acrescenta | O que duplica | Custo | Veredito |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | Extensão própria com status bar | API de status bar + `cq ... --json` | uma linha persistente com spec, slot, custo e cota | `cq specs status`, `cq git worktree slots`, `cq components session cost` e as tarefas | publisher, VSIX, teste do editor, lockstep, dono de release | rejeitada agora |
| C2 | MCP server definition provider | `contributes.mcpServerDefinitionProviders` + `vscode.lm.registerMcpServerDefinitionProvider` | registro do servidor sem editar o `.mcp.json` | `.mcp.json` nativo, que o harness lê no host; o deploy já o mescla | extensão; a definição do editor não transfere a outro cliente | rejeitada |
| C3 | `chatSkills` ou plugin de agente | `contributes.chatSkills`, ou plugin por deep link | um bundle instalado no editor | skills, agentes, hooks e MCP já deployados; o caminho do `chatSkills` é dentro da extensão | segunda cópia da superfície, trust prompt, release próprio; ADR 0017 | rejeitada |
| C4 | GitHub Pull Requests | `GitHub.vscode-pull-request-github` | revisão de PR, checks e comentários no editor | o `gh` no terminal; complementa | nenhum para o repositório; a pessoa instala | recomendada (opcional) |
| C5 | Git Worktree Manager | `jackiotyu.git-worktree-manager` | lista e ações de worktree, clonagem | o built-in do cliente e a projeção do pool | um segundo gerente sobre o mesmo repositório; um `remove` forçado vence o lock do slot | não recomendada para o pool |

O built-in do cliente não é uma extensão: ele cobre criar, abrir, comparar, migrar e apagar um
worktree, e o `cq git worktree workspace --write` abre os slots ativos num `.code-workspace`.

## Fontes, com a data da leitura

| Fonte | URL | Lida em | O que sustenta |
| --- | --- | --- | --- |
| Contribution points | https://code.visualstudio.com/api/references/contribution-points | 2026-11-25 | `chatSkills`, `chatAgents`, `chatInstructions` e `chatPromptFiles`; o caminho da skill é dentro da extensão |
| Integração MCP | https://code.visualstudio.com/api/extension-guides/ai/mcp | 2026-11-25 | `.mcp.json` como configuração nativa; a definição vinda do editor não transfere a outro cliente |
| Agent Skills | https://code.visualstudio.com/docs/agent-customization/agent-skills | 2026-11-25 | os diretórios de skill por harness; extensões contribuem via `chatSkills` |
| Agent plugins | https://code.visualstudio.com/docs/agent-customization/agent-plugins | 2026-11-25 | plugin e extensão são coisas distintas; o deep link instala um bundle |
| Git worktrees | https://code.visualstudio.com/docs/sourcecontrol/branches-worktrees | 2026-11-25 | o built-in cria, abre, compara, migra e apaga worktrees |
| GitHub Pull Requests | https://marketplace.visualstudio.com/items?itemName=GitHub.vscode-pull-request-github | 2026-11-25 | 37.641.537 instalações; versão 0.183.2026112504; publicado em 2026-11-25 |
| Git Worktree Manager | https://marketplace.visualstudio.com/items?itemName=jackiotyu.git-worktree-manager | 2026-11-25 | 41.848 instalações; versão 3.34.2; avaliação 5,0 |
| ADR 0017 | `docs/decisions/0017-install-only-by-deploy.md` | 2026-11-25 | o quenching chega ao repositório só pelo `cq deploy` |
| Deploy mode | `docs/standards/architecture/deploy-mode.md` | 2026-11-25 | as sementes `.vscode/` e as projeções |
| Versioning and release | `docs/standards/ci-cd/versioning-release.md` | 2026-11-25 | o custo de mais um artefato no lockstep |
| Bancada 452 | `specs/artifacts/452/copilot-bench.md` | 2026-11-25 | o inventário e as metades medidas do cliente |
| 455 | `specs/455.md` | 2026-11-25 | o cliente lê as duas cópias de skills e desduplica |
| 460 | `specs/460.md` | 2026-11-25 | a projeção do workspace e a extensão adiada para esta avaliação |

As duas consultas da marketplace, para reproduzir os números:

```bash
curl -sS -X POST 'https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery' \
  -H 'Content-Type: application/json' -H 'Accept: application/json;api-version=7.2-preview.1' \
  -d '{"filters":[{"criteria":[{"filterType":7,"value":"GitHub.vscode-pull-request-github"}],"pageSize":5}],"flags":914}'

curl -sS -X POST 'https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery' \
  -H 'Content-Type: application/json' -H 'Accept: application/json;api-version=7.2-preview.1' \
  -d '{"filters":[{"criteria":[{"filterType":7,"value":"jackiotyu.git-worktree-manager"}],"pageSize":5}],"flags":914}'
```

## A decisão

O quenching **não publica** extensão do VS Code nem plugin de agente nesta rodada. O critério da H9
é duplo: cobrir um fluxo que o quenching não alcança **e** não virar uma segunda superfície.
Nenhuma das cinco candidatas passa nos dois. A status bar passa no primeiro e falha no segundo: é
apresentação de dados que o `cq` e as tarefas já expõem, e o preço é um artefato de release inteiro.
O que a decisão entrega no lugar:

- o guia `docs/how-to/work-in-vs-code.md`, com o que o cliente lê, as tarefas, os slots, os
  worktrees e a recomendação;
- a recomendação do **GitHub Pull Requests** para a revisão dos PRs que `cq git pr create` abre;
- a recomendação do **built-in de worktrees** para o pool, com o `cq git worktree workspace --write`;
- o README apresentando o VS Code + GitHub Copilot como cliente.

## O que reabre a decisão

Uma segunda solicitação de um alvo, ou o uso repetido de `cq specs status`/`cq git worktree slots`
no terminal, abre uma spec de `integrations/quenching-vscode` somente-leitura, instalada à parte e
nunca pelo `cq deploy`. A extensão seria uma integração opcional, como o HUD e o quota dos outros
harnesses, e não uma peça da superfície deployada.

## O que não foi medido

- O comportamento ao vivo de cada extensão candidata (a status bar, o provider MCP, a lista de
  worktrees): a avaliação é documental, e a documentação do cliente é a fonte datada.
- A metade ao vivo da H6, H7, H11 e H12: continuam `unmeasured-live` na bancada, e o guia não as
  trata como passe.
- Os números da marketplace mudam com o tempo; a leitura é de 2026-11-25, e uma versão nova é uma
  nova medição.
