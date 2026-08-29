---
type: standard
title: Varredura de dependências
description: O contrato da varredura de dependências por sub-agente que roda na abertura de uma passada do /quenching:specs:develop, antes que ela pergunte qualquer coisa — gatilho, perfil de ferramentas, entregável, e a persistência do mapa com a data que ele carrega
resource: plugins/quenching/commands/specs/develop.md, plugins/quenching/assets/references/specs-develop/questions.md
tags: [automation, dependency-sweep, subagent, specs-develop]
timestamp: 2026-08-25
audience: both
authority: background
source: spec varredura-de-dependencias-antes-do-banco-shape — a comparação entre o /plan (2,99 M de tokens em 27 chamadas de Explore, seis achados) e o /quenching:specs:develop (20 arquivos tocados) que motivou inserir a varredura antes que a passada pergunte; reancorada na abertura da passada quando compor e refinar substituíram a escada de bancos (compor-e-refinar, 2026-08-25)
maintainer: quenching
---

# Varredura de dependências

Sem dados de dependências cruzadas na mesa, o refino de `/quenching:specs:develop` formula a
pergunta certa e não tem com que respondê-la — foi o sinal que motivou este contrato. A varredura
existe para colocar esses dados na mesa **antes** que a passada pergunte qualquer coisa, em vez de
apenas confirmar decisões já tomadas.

## Posição no fluxo

Na abertura da passada, antes que a composição pergunte. É a única posição em que os dados chegam a
tempo de mudar as perguntas — e, com compor e refinar numa passada só, ela é literal pela primeira
vez: uma varredura, antes de tudo.

## O gatilho

A varredura dispara uma vez por passada, quando `### Mapa de dependências` ainda não está sob
`## Design` — o que cobre de uma vez a spec capturada que a composição vai moldar e a spec nascida
com `## Proposal` preenchida que chega direto ao refino. Antes, eram dois gatilhos declarados
separadamente porque cada banco entrava por um caminho seu.

**Uma spec é varrida no máximo uma vez**, e nunca por estar acima de um nível de `complexity` — uma
spec parece pequena exatamente quando ninguém leu as dependências ainda.

## O perfil do sub-agente

Um perfil **novo**, distinto do `Read, Grep, Glob` dos sub-agentes dos bancos adversarial e gate.
Segue o `Explore` do modo de planejamento nativo do Claude Code:

- conjunto read-only completo — tudo menos `Edit`, `Write`, `NotebookEdit` e `Agent`, com `Bash`
  incluído;
- modelo herdado da sessão, sem override e sem effort fixado;
- largura da busca declarada por invocação.

`Bash` é o que permite devolver o agregado que um `grep`/`gh`/`cq` produz em vez do dump cru — a
mesma exigência que a doutrina de evidência e [agents.md](agents.md) §The verifier shape já fazem a
um sub-agente inspecionador.

## O entregável

Um mapa de dependências cruzadas, não um trilho de leitura: o sub-agente devolve uma tabela e não
toca em nada.

## Persistência do mapa

O mapa entra na própria spec, em `### Mapa de dependências` sob `## Design`, dentro da edição
consolidada do banco que o pediu — escrito pelo **orquestrador**, nunca pelo sub-agente. Escrito
ali ele persiste no board, é lido de graça pelos bancos seguintes em vez de ser re-varrido, e fica
visível para o humano na issue.

O mapa carrega a **data da varredura**, porque uma spec cujo escopo mudou depois nunca é re-varrida
e o mapa envelheceria em silêncio sem essa data para denunciar a defasagem.

## A porta de graduação

Nascido `authority: background`: a regra acima é um contrato que este repositório declarou, ainda
não provado por uso repetido e independente. Ela graduaria para `current` quando o resultado da
varredura — comparado à passada de referência do `/plan` (achados na mesa antes do banco
adversarial, custo somado da sessão) — for medido em uma execução real de
`/quenching:specs:develop` contra a tarefa `res4966_v02`, conforme `## Handoff` da spec que a
originou.
