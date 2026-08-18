---
type: standard
title: Varredura de dependências
description: O contrato da varredura de dependências por sub-agente que roda entre a captura e o banco shape do /quenching:specs:develop — gatilho, perfil de ferramentas, entregável, e a persistência do mapa com a data que ele carrega
resource: plugins/quenching/commands/specs/develop.md, plugins/quenching/assets/references/specs-develop/questions.md
tags: [automation, dependency-sweep, subagent, specs-develop]
timestamp: 2026-08-17
audience: both
authority: background
source: spec varredura-de-dependencias-antes-do-banco-shape — a comparação entre o /plan (2,99 M de tokens em 27 chamadas de Explore, seis achados) e o /quenching:specs:develop (20 arquivos tocados) que motivou inserir a varredura entre a captura e o banco shape
maintainer: quenching
---

# Varredura de dependências

Sem dados de dependências cruzadas na mesa, o banco adversarial de `/quenching:specs:develop`
formula a pergunta certa e não tem com que respondê-la — foi o sinal que motivou este contrato. A
varredura existe para colocar esses dados na mesa **antes** que os quatro bancos perguntem, em vez
de apenas confirmar decisões já tomadas.

## Posição no fluxo

Depois da captura, antes do banco *shape*. É a única posição em que os dados chegam a tempo de
mudar as perguntas dos quatro bancos.

## O gatilho

A varredura dispara em dois pontos:

- quando o banco *shape* é selecionado;
- quando a spec nasceu já com `## Proposal` preenchida e nunca foi varrida, na primeira entrada do
  banco *adversarial* — o caminho comum, `/quenching:specs:create` entregando uma spec já em
  `proposed`, passaria direto pela varredura sem este segundo ponto.

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
