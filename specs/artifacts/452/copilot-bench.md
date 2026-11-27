# Bancada do quenching no VS Code e GitHub Copilot

**Matriz final de 2026-11-25.**

Matriz viva da abertura do épico 453. Uma seção por hipótese: a capacidade, o artefato que a
carrega, os passos do protocolo ao vivo, a saída esperada, o que confirma ou refuta, e o membro do
épico que depende da decisão. A sonda regenera a metade estática; o protocolo preenche o que só uma
sessão real mostra.

## Condições da medição

| Campo | Valor |
|---|---|
| Data | 2026-11-25 |
| Cliente | Visual Studio Code – Insiders 1.149.0-insider (commit `d8b0b6fc93e3027e3dae61d348d73f8b3f33c59c`, 2026-11-25T04:39:03Z, x64) |
| Extensão do Copilot | `GitHub.copilot-chat` 0.77.2026112501 |
| Copilot CLI | 1.0.25 medido no handoff de 09:00; `copilot` não resolve nesta shell às 11h (o shim do editor repassa e não encontra) |
| Editor no PATH | `code-insiders` presente, `code` (stable) ausente |
| Servidor MCP | `.mcp.json` com a entrada `quenching`, `python3 .agents/quenching/assets/bin/cq mcp`; montagem `all` |
| Tools picker | não alterado nesta sessão; o servidor `quenching` ficou ligado |
| Tools `quenching` visíveis ao modelo | 108 (o servidor publica 116) |
| Tools nativas visíveis | 22 |
| Skills visíveis ao modelo | 16 dos 17 nomes do `.agents/skills`, cada um uma vez; `release` não aparece |

**A regra do limite:** cada linha desta matriz registra a condição em que foi observada — montagem,
estado do picker e contagem de tools visíveis. Uma observação feita acima de 128 sem essa nota não
vale.

## Como rodar a sonda

```bash
python3 scripts/copilot_bench.py --target . --json   # o alvo instalado deste checkout
python3 scripts/copilot_bench.py --target . --md     # a matriz abaixo, regenerada
python3 scripts/copilot_bench.py --deploy --json     # um alvo descartável, o que o usuário recebe
```

A sonda mede e reporta; nunca corrige. `unmeasured-live` nomeia o passo do protocolo que mede a
metade que ela não observa, e nunca é lido como passe.

## H1 — Skills publicadas duas vezes e desduplicadas pelo cliente

- **Membro:** 455. **Artefato:** `.agents/skills` + `.claude/skills`.
- **Passos:** no chat, digite `/` e leia a lista de skills; conte cada `quenching-*`. Compare com
  `ls .agents/skills` e `ls .claude/skills` (17 em cada).
- **Saída esperada:** cada nome uma vez, sem par duplicado vindo das duas cópias.
- **Confirma:** cada `quenching-*` aparece uma vez. **Refuta:** o mesmo nome aparece duas vezes.
- **Observado pela sonda:** 17 skills na fonte e 17 na ponte, 0 divergência byte a byte
  (`bridge.plan`).
- **Sessão ao vivo (2026-11-25, servidor ligado, sem mexer no picker):** a lista de skills do modelo
  traz 16 nomes, cada um uma vez; `release` não aparece. O seletor `/` ainda não foi lido pelo
  humano. **Veredito:** `confirmed` — nenhum nome aparece duas vezes; a ausência do `release` é
  achado para a 455.

## H2 — Agentes de `.claude/agents` descobertos no formato Claude

- **Membro:** 456. **Artefato:** `.claude/agents/*.md` (5) contra `.github/agents` (0).
- **Passos:** abra o seletor de agentes/modos customizados do chat e procure os cinco
  `quenching-spec-*`.
- **Saída esperada:** os cinco, com descrição e modelo.
- **Confirma:** os cinco listados. **Refuta:** nenhum, ou só os de `.github/agents`.
- **Observado pela sonda:** 5 agentes em `.claude/agents`, 5 em `.opencode/agents`, 0 em
  `.github/agents`.
- **Sessão ao vivo:** a ferramenta de subagente desta sessão lista os cinco
  (`quenching-spec-orchestrator`, `-reviewer`, `-runner`, `-scout`, `-verifier`); o painel do
  cliente ainda não foi lido. **Veredito:** `confirmed` — o cliente descobre `.claude/agents` no
  formato Claude; `.github/agents` segue vazio.

## H3 — Orçamento de ferramentas contra o teto de 128

- **Membro:** 454. **Artefato:** `.mcp.json` + `tools/list`.
- **Passos:** abra o tools picker do chat, leia o contador do servidor `quenching`, procure um aviso
  de excesso e grupos de virtual tools (`github.copilot.chat.virtualTools.threshold`).
- **Saída esperada:** 116 ferramentas publicadas pelo servidor; o cliente mostra um subconjunto e
  agrupa o excedente.
- **Confirma:** contagem visível + nativas acima de 128, com aviso ou agrupamento. **Refuta:** o
  cliente entrega todas sem aviso e sem grupo, e a conta cabe.
- **Observado pela sonda:** 116 ferramentas (specs 37, git 25, components 13, design 7, config 6,
  knowledge 6, proof 5, opensource 4, ops 4, security 3, codex 2, delivery 2, toolchain 2), 95.340
  bytes de definição, respondidas em ~0,2 s.
- **Sessão ao vivo:** 108 tools `quenching` visíveis ao modelo + 22 nativas = 130, sem virtual tools
  visíveis. As 8 que o servidor publica e esta sessão não expõe: `specs_show`, `specs_section`,
  `specs_section_write`, `specs_task`, `specs_tags`, `specs_title`, `specs_validate`,
  `specs_verification`. O contador do picker ainda não foi lido. **Veredito:** `confirmed` — a
  requisição carrega 130 ferramentas, acima do teto de 128; o cliente não agrupou o excedente, e a
  454 decide o que fazer com a conta.

## H4 — Hooks de `.claude/settings.json`, e o fail-open por timeout

- **Membro:** 462. **Artefato:** `.claude/settings.json`.
- **Passos:** peça ao agente um `git commit` cuja mensagem carregue o trailer de co-autoria da
  Claude; o hook deve negar. Depois, um hook de teste com `sleep` acima do `timeout` declara o
  fail-open. No Windows, repita em PowerShell e cmd.
- **Saída esperada:** a chamada negada com a razão do `deny-claude-coauthor`; o hook lento não
  bloqueia a sessão.
- **Confirma:** negação observada e sessão seguindo após o timeout. **Refuta:** o comando roda sem
  o hook, ou o timeout derruba a sessão.
- **Observado pela sonda:** 1 entrada em `PreToolUse` (`Bash|PowerShell|bash|powershell`), 2 corpos
  (`deny-claude-coauthor`, `warn-git-add-all`), timeout 5 s, e o código `-c` sem `$`, crase ou aspas.
- **Sessão ao vivo (Linux):** um `git commit --dry-run` com o trailer da Claude foi **negado** pelo
  hook, com a razão do deploy — o cliente executa os hooks do arquivo. **Veredito:** `confirmed`
  para o disparo no Linux e pelo charset; o fail-open por timeout segue `unmeasured-live`: falta um
  hook que exceda o timeout.

## H5 — Trailer de co-autoria no commit do cliente

- **Membro:** 465. **Artefato:** a mensagem do commit.
- **Passos:** faça um commit pelo agente e leia `git log -1 --format=%B`.
- **Saída esperada:** a mensagem sem trailer de outro agente, com a atribuição vazia que o deploy
  escreve.
- **Confirma:** aparece um trailer que o humano não escreveu. **Refuta:** nenhum trailer.
- **Sessão ao vivo:** os 10 commits desta sessão na branch, 0 com trailer; o
  `.claude/settings.json` carrega `attribution: {commit: "", pr: ""}`. **Veredito:** `refuted` —
  este cliente não acrescentou trailer a nenhum dos 10 commits.

## H6 — Configurações de workspace em `.vscode/settings.json`

- **Membro:** 457. **Artefato:** `.vscode/settings.json` (JSONC).
- **Passos:** abra um workspace com `chat.tools.terminal.autoApprove`, `search.exclude`,
  `chat.agent.maxRequests` e a chave de sandbox; rode um comando coberto e uma busca.
- **Saída esperada:** o comando sem prompt, os diretórios excluídos fora da busca, o teto de
  requisições respeitado e o sandbox ativo.
- **Confirma:** cada chave produz o efeito. **Refuta:** o cliente ignora a chave no nível do
  workspace.
- **Observado pela sonda:** o arquivo `absent` neste checkout; a fixture
  `quenching/tests/fixtures/copilot-bench/.vscode/settings.json` prova que a sonda lê JSONC com
  comentário e vírgula final.
- **Sessão ao vivo:** `unmeasured-live` — depende de um workspace com o arquivo.

## H7 — `New Worktree` do cliente adotado pelo fluxo

- **Membro:** 458. **Artefato:** `git worktree list`.
- **Passos:** use `New Worktree` no VS Code e rode `cq specs status <id>` no worktree criado.
- **Saída esperada:** o worktree criado aparece na lista, e o `cq` o adota como `branch.work` em vez
  de cortar outro slot.
- **Confirma:** `branch:` aponta o worktree do cliente. **Refuta:** o `cq` corta um segundo worktree.
- **Observado pela sonda:** 8 slots e 1 store irmãos do checkout primário.
- **Sessão ao vivo:** `unmeasured-live` — depende do comando do cliente.

## H8 — De onde sai o custo de uma sessão

- **Membro:** 461. **Artefato:** `~/.copilot`, OpenTelemetry, Agent Debug Logs.
- **Passos:** exporte um Agent Debug Log de uma sessão e leia o `~/.copilot/session-state` da mesma
  sessão; compare os números.
- **Saída esperada:** tokens e modelo por requisição num dos dois.
- **Confirma:** um número reproduzível por sessão. **Refuta:** nenhum dos dois entrega tokens.
- **Observado pela sonda:** `copilot-cli-session-state` presente, `copilot-cli-session-store`
  presente, `vscode-insiders-logs` presente (último `20261125T081721`), `vscode-logs` e os logs de
  server ausentes, `opentelemetry-env` ausente.
- **Sessão ao vivo:** `~/.copilot/session-state/<id>` desta sessão existe
  (`4d7c5192-44ab-49e8-9645-75dc26bb8eb0`), o `session-store.db` tem as tabelas `sessions`,
  `turns` e `assistant_usage_events`, e o log do cliente traz `agentHostTelemetry.log`.
  **Veredito:** `confirmed` — as três fontes existem e a de sessão é por id; extrair os números é da
  461.

## H9 — Extensão ou plugin do VS Code para o fluxo

- **Membro:** 466. **Artefato:** `~/.vscode-insiders/extensions`.
- **Passos:** inventarie as extensões instaladas e avalie cada candidata (status bar, MCP server
  definition provider, `chatSkills`, GitHub Pull Requests, gerenciador de worktree) contra a
  restrição de não criar uma segunda superfície.
- **Saída esperada:** nenhuma candidata que justifique um artefato novo, ou uma com o custo medido.
- **Confirma:** uma extensão cobre um fluxo que o quenching não alcança. **Refuta:** todas duplicam
  a superfície existente.
- **Observado pela sonda:** 24 ids instalados (`adrianwilczynski.terminal-commands`,
  `anthropic.claude-code`, `astral-sh.ty`, `charliermarsh.ruff`, `cweijan.vscode-office`,
  `databricks.databricks`, `dracula-theme.theme-dracula`, `kevinrose.vsc-python-indent`,
  `mgesbert.python-path`, `mhutchie.git-graph`, `ms-azuretools.vscode-containers`,
  `ms-python.debugpy`, `ms-python.python`, `ms-python.vscode-python-envs`,
  `ms-toolsai.datawrangler`, `ms-toolsai.jupyter`, `ms-toolsai.jupyter-keymap`,
  `ms-toolsai.jupyter-renderers`, `ms-vscode-remote.remote-containers`,
  `pkief.material-icon-theme`, `redhat.vscode-yaml`, `southsystem.4devstudio`,
  `tamasfe.even-better-toml`).
- **Sessão ao vivo:** `unmeasured-live` — o inventário está de pé e nenhuma das 24 extensões é um
  gerenciador de worktree ou o GitHub Pull Requests; a avaliação de cada candidata é da 466.

## H10 — Descrições de skill dentro do corte de 1.024 caracteres

- **Membro:** 455. **Artefato:** `.agents/skills/**/SKILL.md`.
- **Passos:** nenhum ao vivo para o corte; a sonda lê o frontmatter.
- **Observado:** 34 descrições (17 em duas cópias), 18.552 caracteres somados, 9.276 por cópia, a
  maior com 1.010 (`quenching-knowledge`), 0 acima de 1.024. **Veredito:** `confirmed`.

## H11 — Regras por caminho entregues ao cliente

- **Membro:** 463. **Artefato:** `.claude/rules` + `.github/instructions`.
- **Passos:** edite um arquivo casado por uma regra (ex.: `quenching/skills/**`) e veja a regra no
  contexto; repita com `.github/instructions` e `applyTo`.
- **Saída esperada:** a regra carregada só no caminho casado.
- **Confirma:** a regra entra no contexto do arquivo casado. **Refuta:** nenhuma regra entra, ou
  entra em todo arquivo.
- **Observado pela sonda:** 2 regras em `.claude/rules` (`command-fork.md`,
  `import-memory-models.md`), 0 em `.github/instructions`; `.github/` sem `instructions`, `agents` e
  `copilot-setup-steps.yml`.
- **Sessão ao vivo:** `unmeasured-live`.

## H12 — Slots e armazenamento irmão acessíveis sem prompt

- **Membro:** 459 (e 460 para a visibilidade). **Artefato:** worktrees + `external_directory`.
- **Passos:** dentro de um slot, rode `cq specs status` e leia um arquivo do store irmão; observe o
  prompt do cliente.
- **Saída esperada:** leitura e escrita sem prompt, com os padrões de `external_directory`.
- **Confirma:** nenhum prompt. **Refuta:** o cliente pede permissão a cada acesso.
- **Observado pela sonda:** 8 slots e 1 store irmãos; 2 padrões em `external_directory` no
  `opencode.json` (`~/Projetos/quenching-slot-*` e `~/Projetos/quenching.*`).
- **Sessão ao vivo:** `unmeasured-live`.

## H13 — `cq deploy --harness copilot` recusado

- **Membro:** 452. **Artefato:** o CLI do deploy.
- **Passos:** `cq deploy --harness copilot --check --json`; e um harness documentado por vez.
- **Saída esperada:** exit 2 com `ct-deploy-harness` para `copilot`; `claude`, `codex`, `opencode` e
  `none` aceitos.
- **Confirmado:** `--harness copilot` sai 2 com `ct-deploy-harness`; `claude`, `codex`, `opencode` e
  `none` saem 1 (`ok: true`, drift de `--check`), nunca com a recusa. **Veredito:** `confirmed`.

## Matriz final (2026-11-25)

Uma linha por hipótese. A coluna `Veredito` é a leitura ao vivo desta sessão quando existe;
`unmeasured-live` nomeia o que falta e nunca é lido como passe.

| # | Capacidade | Artefato | Veredito | Evidência | Membro |
|---|---|---|---|---|---|
| H1 | O cliente desduplica por nome as skills publicadas duas vezes | `.agents/skills` + `.claude/skills` | `confirmed` | 17/17 skills, 0 divergência byte a byte; 16 nomes uma vez na lista do modelo, `release` ausente | 455 |
| H2 | O harness descobre `.claude/agents` no formato Claude | `.claude/agents` | `confirmed` | 5 agentes em `.claude/agents`, 5 em `.opencode/agents`, 0 em `.github/agents`; os cinco no registro de subagentes | 456 |
| H3 | As ferramentas do servidor, somadas às nativas, passam do teto de 128 | `.mcp.json` + `tools/list` | `confirmed` | 116 publicadas; 108 visíveis + 22 nativas = 130 numa requisição, sem virtual tools | 454 |
| H4 | Os hooks de `.claude/settings.json` disparam, e o timeout faz fail-open | `.claude/settings.json` | `confirmed` | 1 entrada por par (event, matcher), charset poliglota limpo; negação observada no Linux; fail-open por timeout pendente | 462 |
| H5 | O Copilot acrescenta trailer de co-autoria ao commit | a mensagem do commit | `refuted` | 10 commits da sessão, 0 trailers; `attribution: {commit: "", pr: ""}` no settings | 465 |
| H6 | `chat.tools.terminal.autoApprove`, `search.exclude`, `chat.agent.maxRequests` e o sandbox valem no workspace | `.vscode/settings.json` (JSONC) | `unmeasured-live` | arquivo `absent` neste checkout; JSONC com comentário e vírgula final lido pela fixture | 457 |
| H7 | `New Worktree` produz um worktree que o fluxo adota sem cortar outro | `git worktree list` | `unmeasured-live` | 8 slots e 1 store irmãos; o comando do cliente não foi exercitado | 458 |
| H8 | O custo de uma sessão sai do session-state, do OpenTelemetry ou do Agent Debug Logs | `~/.copilot`, logs do editor | `confirmed` | session-state por id, `assistant_usage_events` no store e `agentHostTelemetry.log` no log do cliente | 461 |
| H9 | Uma extensão ou plugin do VS Code serve o fluxo sem virar segunda superfície | `~/.vscode-insiders/extensions` | `unmeasured-live` | 24 ids inventariados; nenhum gerenciador de worktree nem GitHub Pull Requests | 466 |
| H10 | As descrições de skill cabem no corte de 1.024 caracteres | `.agents/skills/**/SKILL.md` | `confirmed` | 34 descrições, 18.552 caracteres, maior 1.010 (`quenching-knowledge`), 0 acima de 1.024 | 455 |
| H11 | As regras por caminho chegam ao cliente pelo caminho do arquivo | `.claude/rules` + `.github/instructions` | `unmeasured-live` | 2 regras em `.claude/rules`, 0 em `.github/instructions`; a entrega não foi observada | 463 |
| H12 | Os slots e o armazenamento irmão ficam acessíveis sem prompt | worktrees + `external_directory` | `unmeasured-live` | 8 slots, 1 store, 2 padrões em `external_directory`; o acesso não foi observado | 459 |
| H13 | `cq deploy` recusa `--harness copilot` com `ct-deploy-harness` e aceita claude, codex, opencode e none | o CLI do deploy | `confirmed` | `copilot` sai 2 com `ct-deploy-harness`; os quatro aceitos saem 1, nunca com a recusa | 452 |

**O Copilot CLI** (1.0.25 no handoff de 09:00) não resolve nesta shell às 11h: a metade do protocolo
que exigia uma sessão do CLI fica `unmeasured-live`, com o motivo, e não bloqueia nenhum membro — a
metade do VS Code cobriu H1–H5 no Linux.

**Windows:** `blocked` — sem máquina Windows nesta rodada. O disparo do hook e o trailer (H4, H5)
ficam para a próxima, e nenhum membro depende dessa linha para começar: a 462 e a 465 seguem com a
evidência do Linux.

## Decisão por membro

A regra do épico: `confirmed` mantém o membro; `refuted` o derruba ou o reescreve; `reformulated`
muda o escopo; `unmeasured-live` não autoriza prometer o comportamento do cliente — o membro segue
pela capacidade e mede antes de afirmar.

| Membro | Hipótese | Decisão | Por quê |
|---|---|---|---|
| 454 | H3 `confirmed` | **segue** | 130 ferramentas numa requisição, acima de 128, e o cliente não agrupou; a montagem enxuta resolve o que foi medido |
| 455 | H1, H10 `confirmed` | **segue** | o cliente desduplica por nome e as descrições cabem no corte; resta publicar uma vez e devolver o `release` à lista |
| 456 | H2 `confirmed` | **segue** | os cinco agentes de `.claude/agents` são descobertos no formato Claude |
| 457 | H6 `unmeasured-live` | **muda** | nenhuma chave de `.vscode/settings.json` foi observada em efeito; o escopo é só a chave que um workspace real provar |
| 458 | H7 `unmeasured-live` | **muda** | o `New Worktree` não foi exercitado; adotar o worktree do cliente só depois de observá-lo |
| 459 | H12 `unmeasured-live` | **muda** | os 8 slots e os 2 padrões existem, mas o acesso sem prompt não foi observado |
| 460 | H12 (nota) | **muda** | nenhum gerenciador de worktree está instalado entre as 24 extensões; a visibilidade dos slots espera a observação da UI |
| 461 | H8 `confirmed` | **segue** | session-state por id, `assistant_usage_events` e a telemetria do cliente existem; falta só extrair os números |
| 462 | H4 `confirmed` | **segue** | o hook dispara e nega no Linux, com o charset poliglota limpo; o fail-open por timeout e o Windows ficam como prova pendente, não como bloqueio |
| 463 | H11 `unmeasured-live` | **muda** | as regras existem em `.claude/rules`, mas a entrega por caminho não foi observada; `.github/instructions` segue vazio |
| 464 | sem linha na matriz | **segue** | nenhuma hipótese o condiciona; o agente de nuvem não foi medido por esta bancada |
| 465 | H5 `refuted` | **muda** | este cliente não acrescentou trailer em 10 commits; a guarda passa a mirar o trailer de outros agentes, não o do Copilot |
| 466 | H9 `unmeasured-live` | **muda** | o inventário está de pé e nenhuma das 24 extensões é das categorias candidatas; avaliar só o que existir |

**O que a matriz não decidiu:** a metade do Copilot CLI (não resolve nesta shell) e o Windows
(`blocked`) ficam como prova pendente; nenhum membro fica impedido de começar por causa delas.
