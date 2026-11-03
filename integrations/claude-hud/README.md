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
- `cq specs status --spec <id> --no-fetch --json`

O plugin não escreve em spec nem em branch e não registra comando, botão nem hook de ferramenta. `--no-fetch` faz o
`cq specs status` ler só o ref local `refs/remotes/origin/quenching` que já existe: sem `fetch`, sem rede, sem ssh, sem
escrita de ref e sem cache. A faixa mostra o estado da última vez que outro comando `cq` buscou `origin`, então pode estar
defasada. Sem esse ref, ou num backend que não é o git (github, azure), o comando recusa e a faixa some, sem chamar a API
do GitHub.

## Pré-requisito

`cq` no `PATH`, o que o plugin `quenching` garante quando está ativo. Sem `cq` a faixa some, sem erro.

## Instalação

```
/plugin install quenching-hud --marketplace holetz/claude-quenching
```

## Verificação

```bash
claude plugin validate plugins/claude/quenching-hud
claude plugin test plugins/claude/quenching-hud
```
