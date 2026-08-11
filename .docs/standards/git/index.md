# `standards/git/`

Como este repositório usa o git — branches de longa duração, o gatilho de publicação, e as
convenções que `/quenching:specs:execute`/`/quenching:specs:conclude` leem como read-if-present.

**Boundary:** o *fluxo* de branches e publicação vive aqui; o lockstep de versão que a publicação
move vive em [../ci-cd/](../ci-cd/index.md); o registro de tarefa→commit de uma spec individual
vive em [../workflows/](../workflows/index.md). One standard per file; each carries `type:
standard` + a derived `resource:`; add each to [../index.md](../index.md).

## Current docs

* [branching.md](branching.md) — a `main` acumulava integração e publicação; este standard separa
  as duas funções (`develop` integra, `main` publica), declara o gatilho por demanda e a rota
  sempre local da publicação.

## Candidate sub-standards

Break this subject **one concept per file**. The method evaluates each candidate against
the repo, generates the applicable ones (`file:line`-anchored, full OKF frontmatter), and
records the rest below as deferrals (never a silent skip):
`branching` · `commit-conventions` · `tagging`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads. A subject is "done" only when every candidate is
**present or listed here** with a one-line why.

- `branching` — **present**: [branching.md](branching.md).
- `commit-conventions` — **deferred, not applicable.** Sem um `/.docs/standards/git/**` de
  mensagens de commit, `/quenching:specs:execute` já aplica o default do plugin
  ([specs-execute/git.md](/plugins/quenching/assets/references/specs-execute/git.md) §Commit
  messages); escrever um aqui converteria esse default num contrato deste repositório sem que
  ninguém tenha pedido isso.
- `tagging` — **deferred, coberto por `versioning-release.md`.** A tag é criada pelo mesmo verbo
  `cq specs release` que move o lockstep; [../ci-cd/versioning-release.md](../ci-cd/versioning-release.md)
  já a documenta como parte do lockstep, e um standard próprio duplicaria essa seção.
