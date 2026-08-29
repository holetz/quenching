# AGENTS.md — claude-quenching

Este repositório publica o plugin `quenching` e sua tradução para Codex. Os corpos de comando em
`plugins/quenching/commands/` e as skills em `plugins/quenching-codex/skills/` são a fonte de
comportamento: trate alterações neles como alterações de código.

Language: pt-BR — the contract is /docs/standards/agents/communication.md.

## Operating this repo

O conhecimento durável vive em `/docs/`; este arquivo é apenas o harness Codex e deve
continuar sendo um ponteiro curto. Antes de alterar ferramentas do plugin, valide o bundle e a
superfície correspondente:

```bash
python3 plugins/quenching-codex/scripts/bin/cq knowledge validate docs
python3 plugins/quenching-codex/scripts/bin/cq --root .agents components doctor --json
```

Quando a superfície `.agents/skills/` ganhar um comando local, acrescente a verificação
`python3 plugins/quenching-codex/scripts/bin/cq --root .agents components lint --json`.
Este checkout não contém `plugins/quenching-codex/tests/`; não há suíte local a executar aqui.

Não há aplicação ou build convencional neste repositório; o backend de specs é GitHub e não há
workspace local `/.specs/`.

## Where knowledge lives

Resolva termos desconhecidos primeiro no [glossário](/docs/glossary.md).

- [/docs/standards/](/docs/standards/index.md) — contratos e convenções do repositório.
- [/docs/concepts/](/docs/concepts/index.md) — entendimento genérico mantido pelo projeto.
- [/docs/external/](/docs/external/index.md) — fatos sobre ferramentas, bibliotecas e fontes externas.
- [/docs/tutorials/](/docs/tutorials/index.md), [/docs/how-to/](/docs/how-to/index.md),
  [/docs/explanation/](/docs/explanation/index.md) — a documentação do produto, por quadrante.
- [/docs/project/](/docs/project/index.md) — o manual deste repositório: comandos, automação, layout.
- [/docs/catalog/](/docs/catalog/index.md) — dados e domínio do repositório.
- [/docs/vision/](/docs/vision/index.md) — direção do projeto.

Para criar, mover ou alinhar conhecimento, use as skills quenching correspondentes; não replique
conhecimento durável neste harness.

<!-- Root harness pointer, auto-loaded by Codex on every turn. Keep this file thin: operational
     rules and navigation only; durable knowledge belongs in /docs/. -->
