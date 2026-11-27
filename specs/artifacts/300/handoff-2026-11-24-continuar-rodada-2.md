## Handoff Confidence
Média. A sessão foi interrompida pelo humano no meio dos conclude da 249, 281 e 290. O veredito do verifier da 287 não chegou ao condutor. O estado real está na store (`cq specs status --spec <id> --json`) e nas branches em origin.

## Objective
Autopilot `--until-dry`, sem teto de lançamentos e com no máximo 4 workers em toda a árvore (decisão do humano). Orientação do projeto: não inflar com camadas que custam tokens e retornam pouco, e tratar a economia de tokens como uma frente de trabalho.

## Current Status
- **Mergeadas nesta sessão:** 275 (#291), 233 (#293), 237 (#292), 244 (#294), 251 (#297), 285 (#296) e 286 (#298). O main estava verde em 350ed3c91.
- **Épicos fechados:** 288 (rodada 1) e 289 (decidir com o humano).
- **Abandonadas com evidência:** 280 (juntada à 269), 284 (superada) e 282 (não reproduziu).
- **Épico 300 (rodada 2), em voo:** cada uma tem `## Handoff` com o estado.
  - 287: PR #295 com o veredito pendente.
  - 249, 281 e 290: em conclude.
  - 254 e 256: medições entregues, à espera da decisão de arquivamento.
- **Não iniciadas no 300:** 252 e 189 (depois da 287), 299 (depois da 281), 277 (depois da 252) e 234 (depois da 277).
- **Épico 262:** só falta a 269, bloqueada no segundo FAIL do verifier; o `## Handoff` dela diz o que falta.

## Decisões do humano (registradas nos Designs e nas Discoveries)
- 275: os caminhos no JSON do cq ficam em POSIX.
- 280 juntada à 269; 287 com prioridade; maxWorkers 4.
- 254 só medição; 256 medindo antes; 281 com registro do gate; 234 e 249 construir; 189 com implícitos do conclude.
- CI de push rápido, e o que for lento vai para workflow_dispatch.
- projects.json limpo (5 entradas quenching-gate-*, backup em projects.json.bak-2026-11-23).
- Os slots antigos podem ser limpos com /quenching-git cleanup quando não estiverem em uso.

## Blockers / pedem o humano
1. **Checkout raiz sujo:** `quenching/tests/test_ci_enforce.py` (uma linha da docstring trocada por "X") e `quenching/tests/test_gate_record.py` (vazio, sem rastreio). São resíduo de um worker da 281 (`[IO.File]::WriteAllText` com caminho relativo). Não foi revertido sem aprovação. Para limpar: `git restore quenching/tests/test_ci_enforce.py` e `Remove-Item quenching/tests/test_gate_record.py`.
2. **269:** confirmar o `windows-gate.yml` (workflow_dispatch) e seguir o `## Handoff` dela.
3. **254 e 256:** a store recusa arquivar como done uma spec sem merge; decidir entre abandoned e uma spec que aceite spec só de medição.

## Fila da próxima rodada (sem épico ainda)
- 301: o detector de mojibake recusa `?` em code span de crase dupla (achado do reviewer).
- 302: 3 testes de test_session_cost falham no Windows na base.
- A spec nova do teste instável `test_run_evals Containment::test_a_timeout_kills_the_grandchildren_too`.
- Candidatas a spec sem registro:
  - o orchestrator passou duas vezes do teto de workers, porque não conta os spawns vivos antes de lançar;
  - o brief dos workers não proíbe `[IO.File]` com caminho relativo no Windows;
  - o slot reaproveitado em CRLF (já está no escopo da 269);
  - `cq specs next` trata a ordem dos grupos como ondas.
- Os 26 membros dos épicos humanos antigos (1527, 1662, 1690, 1929, 1971, 2206 e 2252) esperam decisão.

## Next Actions
1. `git pull` no main e `git fetch origin quenching`. Conferir o `git status` do checkout raiz (blocker 1).
2. `cq specs status 300` e `cq specs status 262`, e ler o `## Handoff` de 287, 249, 281, 290 e 269.
3. Retomar com `/quenching-specs orchestrate 300 --autonomous` e `/quenching-specs orchestrate 262 --autonomous`, ou com `/quenching-specs autopilot --until-dry`, sempre com maxWorkers 4 em toda a árvore.
4. O registro da rodada está em `.quenching/autopilot/2026-11-23/rounds.md` e só existe nesta máquina, porque o git o ignora; este handoff o substitui.
