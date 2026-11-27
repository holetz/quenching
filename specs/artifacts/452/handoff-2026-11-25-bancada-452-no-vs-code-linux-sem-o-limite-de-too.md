## Handoff Confidence
Medium: a #452 está aprovada e o plano é claro, mas o VS Code não está no PATH desta máquina (`command -v code` vazio) e nenhuma hipótese foi observada ao vivo ainda.

## Objective
Fechar a abertura do épico 453 (#452): a sonda estática e o piso de contrato construídos, e a matriz `copilot-bench.md` preenchida com o que uma sessão real do VS Code com Copilot no **Linux** consegue observar. Com a matriz, desenvolver 454–466 e orquestrar o épico. Restrição do dono: nada de `--harness copilot`; tudo agnóstico ao cliente.

## Last Request
"O handoff precisa tratar de alguma forma o limite que nasce de tools do MCP, antes de prosseguir e ser influenciado pelo limiite"
(Pedido anterior: "Monte um handoff para rodarmos o que for possível num VSCode Linux primeiro".)
Status: Answered — ver `## Tool Limit` e o passo 0 de `## Next Actions`.

## Current Status
**Working:** store de specs sincronizado com `origin/quenching` (00111bafc). As 15 escritas locais pendentes de 452–466 eram obsoletas (08:16, antes do develop da sessão VS Code às 09:00) e foram descartadas com `cq specs push --drop 452..466`; a origem já tinha 454–466 idênticas. `cq specs status 452` → `[approved]`, ready gate met, 0/13 tasks. `cq specs reconcile --write` → nada a arquivar.
**Broken:** nada.

## Decisions
- Lançar o épico pelo orchestrator agora foi adiado: só a #452 roda sozinha; 454–466 estão `captured` e dependem da matriz (S1). O dono escolheu rodar primeiro o que der num VS Code Linux.
- O limite de 128 tools é tratado antes do trabalho, sem tocar em `.mcp.json` nem em `shared.mcp.mount`: H3 observada primeiro, depois o servidor desligado no tools picker e o trabalho segue pelo CLI (`## Tool Limit`).
- Windows (H4/H5 no PowerShell/cmd, task 3.3) fica para depois: nesta rodada as linhas Windows saem `blocked` com o motivo "sem máquina Windows nesta rodada", conforme `## Open Decisions` da #452.

## Completed Work
- Desenvolvimento e aprovação da #452 e refinamento do épico #453: feitos na sessão VS Code (commit do store 00111bafc). Ler com `cq specs show 452 --full` e `cq specs show 453 --full`.

## Open Work
- Nenhuma task da #452 iniciada; nenhum worktree cortado para ela.

## Validation Evidence
- `cq specs status 452` → approved {'date': '2026-11-25', 'by': 'session'}, 13 tasks abertas.
- `cq config show --effective` → runAloneUpTo=low, merge=policy, maxWorkers=3 (defaults).
- Nesta máquina: `copilot --version` → `GitHub Copilot CLI 1.0.25.`; `gh` presente; `code` ausente do PATH.
- Nada da sonda ou dos testes foi executado.

## Blockers
- Tasks 3.2 (parte VS Code) exigem o humano operando o chat do Copilot no VS Code Linux; o agente só prepara o roteiro e registra o que o humano observar.
- Task 3.3 (Windows) bloqueada por falta de máquina — registrar `blocked`.

## Tool Limit
O teto de 128 ferramentas por requisição do Copilot vale também para a sessão que faz a bancada; sem tratar isso, ela mede e trabalha já sob o defeito que deveria medir (virtual tools agrupando ou escondendo tools, e o modelo escolhendo errado).
- Medido nesta sessão (2026-11-25, `initialize` + `tools/list` via stdio): `cq mcp` (montagem `all`, a do `.mcp.json` atual) = **116 tools, 95.638 bytes de schema**; `cq specs mcp` (montagem `specs`) = **16 tools, 13.610 bytes**. As 116, somadas às nativas do Copilot e às das extensões, passam de 128.
- Regra da rodada: **H3 é observada primeiro, numa sessão nova, antes de qualquer outro trabalho**, com o `.mcp.json` como está. Anotar o que o VS Code mostra: contador do tools picker, aviso de excesso de 128, se aparecem grupos de virtual tools (`github.copilot.chat.virtualTools.threshold`), quantas tools `quenching` ficam visíveis ao modelo.
- Logo depois, **desligar o servidor `quenching` no tools picker do chat** (estado local do workspace, reversível, nenhum arquivo commitado) e só então abrir a sessão de trabalho. Não mudar `shared.mcp.mount` em `.agents/quenching.json` nem o `.mcp.json`: isso é decisão da 454 e mudaria o que `copilot_bench.py --target .` precisa reproduzir (116).
- Com o servidor desligado, os fluxos usam o CLI `.agents/quenching/bin/cq …` no terminal (o fallback de `align/tool-resolution.md` §Resolving the tool); aceitar o prompt de terminal ou liberar `cq` por sessão.
- Cada linha da matriz registra a condição em que foi observada: montagem, estado do picker e contagem de tools visíveis. Uma observação feita acima de 128 sem essa nota não vale.
- Achado para a 454 (registrar em `## Discoveries` da 452): `specs` já cabe no orçamento (16 tools); a diferença `all` → `specs` é 100 tools e ~82 KB de schema por requisição.

## Next Actions
0. Sessão nova no VS Code Linux: observar H3 como em `## Tool Limit`, anotar, e desligar `quenching` no tools picker antes do passo 1.
1. `/quenching-specs execute 452` no VS Code Linux (ou num worktree dele): fases 1 e 2 são estáticas e rodam inteiras — `scripts/copilot_bench.py` (1.1–1.6), fixtures e `test_copilot_bench.py`/`test_deploy_client_contract.py` (2.1–2.3). Conferir `python3 scripts/copilot_bench.py --target . --json` contra os números do `## Validation` (116 tools, 17+17 skills, 13.414 chars, maior 1.062, 5+5 agentes).
2. Task 3.1: escrever o artefato `copilot-bench.md` com o roteiro por hipótese e a versão do VS Code (`code --version`, Help › About) e do Copilot CLI (1.0.25 aqui).
3. Task 3.2 no VS Code Linux, com o humano no chat (Agent mode), anotando no artefato:
   - H1 skills: o seletor `/` lista cada `quenching-*` uma vez ou duas (`.claude/skills` + `.agents/skills`)?
   - H2 agentes: `.claude/agents/*.md` aparece como agente/modo customizado?
   - H3 ferramentas: quantas tools do servidor `quenching` chegam (painel de tools; aviso de 128 / virtual tools)?
   - H4 hooks (Linux): um hook de `.claude/settings.json` dispara? O fail-open por timeout se comporta?
   - H5 trailer: um commit feito pelo Copilot carrega `Co-authored-by`? (`git log -1 --format=%B`)
   - Settings de workspace: `chat.tools.terminal.autoApprove`, `search.exclude`, `chat.agent.maxRequests`, sandbox — valem em `.vscode/settings.json`?
   - Worktrees: comportamento de `New Worktree` e acesso a `../quenching-slot-*` sem prompt.
   - Custo: Agent Debug Logs / OpenTelemetry do VS Code; session-state do Copilot CLI (`~/.copilot/`).
   - Extensões: inventário (status bar, MCP server definition provider, `chatSkills`, GitHub Pull Requests, gerenciadores de worktree).
   - Repetir o que couber no Copilot CLI 1.0.25 (H1–H5, custo).
   O que não der para observar fica `unmeasured-live` com o motivo.
4. Task 3.3: registrar as linhas Windows como `blocked` (sem máquina nesta rodada).
5. Task 3.4: matriz final com veredito por hipótese e decisão por membro (segue/muda/cai); depois `/quenching-specs conclude 452`.
6. Com a matriz publicada: `/quenching-specs develop <id>` para 454–466 (as que seguem) e `/quenching-specs orchestrate 453`.
