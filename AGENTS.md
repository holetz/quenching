# AGENTS.md — claude-quenching

Este repositório publica o plugin `quenching` e sua tradução para Codex. Os corpos de comando em
`plugins/quenching/commands/` e as skills em `plugins/quenching-codex/skills/` são a fonte de
comportamento: trate alterações neles como alterações de código.

Language: pt-BR — the contract is /.knowledge/standards/agents/communication.md.

## Operating this repo

O conhecimento durável vive em `/.knowledge/`; este arquivo é apenas o harness Codex e deve
continuar sendo um ponteiro curto. Antes de alterar ferramentas do plugin, valide o bundle e a
superfície correspondente:

```bash
python3 plugins/quenching-codex/scripts/bin/cq knowledge validate .knowledge
python3 plugins/quenching-codex/scripts/bin/cq --root .agents components doctor --json
```

Quando a superfície `.agents/skills/` ganhar um comando local, acrescente a verificação
`python3 plugins/quenching-codex/scripts/bin/cq --root .agents components lint --json`.
Este checkout não contém `plugins/quenching-codex/tests/`; não há suíte local a executar aqui.

Não há aplicação ou build convencional neste repositório; o backend de specs é GitHub e não há
workspace local `/.specs/`.

## Where knowledge lives

Resolva termos desconhecidos primeiro no [glossário](/.knowledge/glossary.md).

- [/.knowledge/standards/](/.knowledge/standards/index.md) — contratos e convenções do repositório.
- [/.knowledge/concepts/](/.knowledge/concepts/index.md) — entendimento genérico mantido pelo projeto.
- [/.knowledge/external/](/.knowledge/external/index.md) — fatos sobre ferramentas, bibliotecas e fontes externas.
- [/.knowledge/documentation/](/.knowledge/documentation/index.md) — documentação do produto.
- [/.knowledge/catalog/](/.knowledge/catalog/index.md) — dados e domínio do repositório.
- [/.knowledge/vision/](/.knowledge/vision/index.md) — direção do projeto.

Para criar, mover ou alinhar conhecimento, use as skills quenching correspondentes; não replique
conhecimento durável neste harness.

<!-- Root harness pointer, auto-loaded by Codex on every turn. Keep this file thin: operational
     rules and navigation only; durable knowledge belongs in /.knowledge/. -->
