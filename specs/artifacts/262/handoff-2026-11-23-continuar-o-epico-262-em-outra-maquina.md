## Handoff Confidence
High: o estado inteiro está no origin (main, tag 7.15.0 e a store na branch `quenching`); nada ficou sem commit ou sem push.

## Objective
Fazer o quenching funcionar bem no Windows e custar menos na máquina local e em tokens, sem inflar o projeto com camadas que custam tokens e retornam pouco (cautela do humano, declarada em `shared.guidance.autopilot` no `.agents/quenching.json`). A frente atual é o épico 262: zerar o gate local no Windows e prová-lo no CI.

## Last Request
faça isso
Status: Answered (o pedido era gerar este handoff para continuar o desenvolvimento em outra máquina).

## Current Status
**Working:** releases 7.12.0, 7.13.0, 7.14.0 (feito pelo humano fora da sessão, confirmado como correto) e 7.15.0 publicados, cada um com CI verde no commit exato e `functional-checks.sh` 10/10. O MCP `quenching` vem registrado pelo `opencode.json` do repo. O gate local no Windows caiu de 276 falhas e 12 erros para 2 falhas.
**Broken:** no Windows, 2 falhas em `test_golden` (provider-github e provider-azure), que dependem da decisão de contrato da spec 275. Clones e worktrees criados antes do `.gitattributes` da 264 continuam com a cópia de trabalho em CRLF.

## Decisions
- Piso Python 3.11+, nunca travar em versão ausente; PEP 810 só via `__lazy_modules__`, nunca a sintaxe `lazy import` (231, épico 230).
- `shared.ci.enforce` tem padrão `required`; check vermelho nunca passa; com o CI relaxado, o merge exige o gate local verde (274).
- No Windows, gate local vermelho de plataforma é inconclusivo e o CI é a prova do merge (regra das rodadas).
- FAIL de ruler (`gate-shrunk`) restrito a reescrita foi aceito pelo condutor com o diff como evidência (208, 2249, 2221, 2253, 264, 265), e a decisão fica no `## Design` de cada spec.
- 2271 abandonada com evidência (premissa de retomadas frias não reproduzida).
- A 269 ficou aberta por decisão do humano, com a detecção barata de cópia de trabalho em CRLF incluída no escopo, sem correção automática.
- Nenhum worker regrava cópia de trabalho à força nem roda testes no checkout raiz.

## Completed Work
- Épico 230 (correções Windows, release 7.12.0): 225, 226, 2221, 228, 229, 231, 235; MCP ativado no PR #239.
- Épico 245 (fila original e economia de tokens, release 7.13.0 e 7.14.0): 224, 246, 2201, 2217, 1962, 1965, 2165, 227, 2253, 2272, 2254, 2255, 2256.
- Épico 262 (gate Windows, release 7.14.0 e 7.15.0): 264 (#273), 268 (#272), 266 (#276), 265 (#278), 274 (#279), 267 (#283).
- Histórico das rodadas: `.quenching/autopilot/2026-11-22/rounds.md` só na máquina antiga (o git o ignora); o estado real está na store.

## Open Work
- 269 (job Windows no CI com o gate completo) aberta no épico 262; a 280 se sobrepõe e deve ser juntada a ela.
- Worktrees `C:/Projetos/quenching-slot-1` a `-7` na máquina antiga, descartáveis; limpeza com `/quenching-git cleanup` quando o humano pedir.
- `%USERPROFILE%\.config\quenching\projects.json` na máquina antiga tem 4 entradas de testes (`quenching-gate-*`); o humano ainda não autorizou a limpeza.

## Validation Evidence
- `gh api repos/{owner}/{repo}/commits/8dcef94585e689871c5d4e13cfcf0aff083eb440/check-runs`: 5 checks `success` (incluindo o job Windows focado).
- `QUENCHING_FUNCTIONAL=1 functional-checks.sh` pelo Git Bash: 10 passed, 0 failed.
- Gate afetado da 267 no Windows: 2 falhas (`test_golden`), 0 erros.
- Não rodou: o gate completo no Windows com exit 0 (é o objetivo da 269 e da 275).

## Blockers
- 275: decisão do humano sobre o caminho dentro do payload JSON dos goldens, POSIX ou nativo.
- 189: o check 8 do verifier cobra o registro `outcome` antes do merge e o check 3 lê o gate local de plataforma como FAIL; decisão do humano.

## Next Actions
1. Na máquina nova: `git clone`, `git fetch origin quenching`, `uv sync`; em `~/.config/opencode/opencode.jsonc`, `"experimental": {"subagent_depth": 5}` (sem isso o orchestrator não lança workers). No Windows, instalar o Git for Windows (o gate usa o Git Bash; o `bash` do PATH pode ser o WSL).
2. Conferir: `cq --version` dá 7.15.0 e `cq specs status 262` mostra a 269 aberta.
3. Decidir com o humano o contrato da 275, construí-la e zerar as 2 falhas.
4. Juntar a 280 à 269 e rodar o épico 262 com `/quenching-specs orchestrate 262 --autonomous`.
5. Depois, perguntar ao humano sobre a 189, a 254 (execute e conclude num só runner) e a 256 (fluxos lidos por estágio, cerca de 132M tokens relidos medidos), e sobre as soltas 233, 234, 244, 249, 251, 252, 277, 281, 282, 284, 285 e 286.
