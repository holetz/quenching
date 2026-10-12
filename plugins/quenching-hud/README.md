# quenching-hud

Faixa acima do prompt do Claude Code: a spec ativa da worktree, o estágio dela e o
progresso das tasks, sem gastar uma tool call por consulta.

```
spec 1521 · approved · 3/7 · claude-quenching-1521-plugin-quenching-hud-minimo
```

## O que aparece

A faixa aparece quando o branch atual é `plan/<id>-<handle>`; em qualquer outro branch ela some.
Ela se atualiza em `session.start` e a cada `turn.complete`.

## O que executa

Só dois comandos, por argv fixo e sem shell, e o id vem de dígitos do nome do branch:

- `git branch --show-current`
- `cq specs status --spec <id> --json`

O plugin não escreve em spec nem em branch e não registra comando, botão nem hook de ferramenta. Mas `cq specs status` não é
livre de efeitos: no backend git, quando o cache passa de 30s, ele faz `fetch` de `origin` (rede e ssh, timeout de 120s) e
grava `refs/remotes/origin/quenching` no `.git` compartilhado com as worktrees, mais um cache em
`$XDG_CACHE_HOME/quenching/git/`. Sem `.claude/quenching.json`, o backend padrão (github) consulta a API do GitHub. Isso
ocorre em `session.start` e a cada `turn.complete`, em qualquer branch `plan/<id>-`.

## Pré-requisito

`cq` no `PATH`, o que o plugin `quenching` garante quando está ativo. Sem `cq` a faixa some, sem erro.

## Instalação

```
/plugin install quenching-hud --marketplace holetz/claude-quenching
```

## Verificação

```bash
claude plugin validate plugins/quenching-hud
claude plugin test plugins/quenching-hud
```
