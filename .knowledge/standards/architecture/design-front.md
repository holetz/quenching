---
type: standard
title: Design front
description: A fonte DTCG única, suas projeções portáteis e editoriais, a arbitragem explícita com o Impeccable e o limite entre drift web e não-web
resource: plugins/quenching/assets/bin/quenching/design/**, plugins/quenching/assets/design/**, plugins/quenching/commands/design/**
tags: [architecture, design, dtcg, impeccable, projections]
timestamp: 2026-08-28
audience: both
authority: current
source: proposta de arquitetura do front design revisão 2, confirmada pela implementação e por plugins/quenching/tests/test_design.py
maintainer: quenching
---

# Front design

O front design mantém valores, julgamento e artefatos em camadas diferentes sem duplicar
autoridade. Ele é um front do quenching; o Impeccable é um consumidor opcional e continua dono do
ofício visual de tela.

## Uma fonte, três classes de saída

`/.design/tokens.json` é um documento DTCG 2025.10. Valores próprios do quenching ocupam apenas a
extensão `org.quenching`; propriedades livres de componentes não fingem ser tokens de um tipo
`string` que DTCG não possui ([model.py](../../../plugins/quenching/assets/bin/quenching/design/model.py)).

`cq design build` projeta essa fonte em três classes:

| Classe | Artefatos | Autoridade |
| --- | --- | --- |
| Interoperabilidade | `PRODUCT.md`, `DESIGN.md`, `.impeccable/design.json` | derivados completos para consumidores externos |
| Editorial | `MEDIUM.md` e instâncias renderizadas por gênero | contratos e saídas por meio |
| Adaptadores internos | `tokens.css`, `tokens.typ`, `tokens.py`, `brand-api.md` | valores do mesmo grafo DTCG por runtime |

A lista executável e o cálculo em memória vivem em
[build.py](../../../plugins/quenching/assets/bin/quenching/design/build.py):70. Ponteiro não é uma
projeção válida, porque os consumidores leem o conteúdo do artefato.

## A fronteira portátil é deliberadamente lossy

`DESIGN.md` emite somente `colors`, `typography`, `rounded`, `spacing` e componentes limitados a
oito propriedades — o conjunto fechado está em
[model.py](../../../plugins/quenching/assets/bin/quenching/design/model.py):29. Motion, sombras,
breakpoints, rampas e snippets completos ficam no DTCG e no sidecar schema 2. Uma importação nunca
remove tokens DTCG omitidos pela projeção; ela os nomeia como retidos.

`PRODUCT.md` vem de headings canônicos nos homes OKF. `## Platform` precisa ser o valor puro
`web`, `ios`, `android` ou `adaptive`; o gerador recusa inferi-lo. Os três artefatos portáteis
nascem na raiz, a localização comum às buscas de contexto e detector do Impeccable 4.1.2.

## Dois sentidos, uma escolha humana

Um `DESIGN.md` escrito por `/impeccable document` é uma proposta de mudança. `cq design import`
dobra seu subconjunto portátil em `tokens.json`; `cq design build` faz a fonte vigente vencer. O
doctor acusa a divergência byte a byte e não escolhe gosto — a implementação da dobra está em
[importer.py](../../../plugins/quenching/assets/bin/quenching/design/importer.py):27.

O cabeçalho GENERATED existe para declarar proveniência, não para arbitrar. Um primeiro align
preserva um `DESIGN.md` externo até criar a fonte e importá-lo; só então constrói as projeções
([align.py](../../../plugins/quenching/assets/bin/quenching/design/align.py):68).

## Verificação dividida por competência

`cq design doctor` decide validade da fonte, identidade dos gerados, assets órfãos e literais
repetidos em primitivos não-web ([doctor.py](../../../plugins/quenching/assets/bin/quenching/design/doctor.py):21).
O detector do Impeccable decide drift web de cor, fonte, raio e tamanho quando estiver instalado.
Sua ausência nunca falha o build nem vira um verde inventado.

## Um gênero, N destinos

Um contrato sob `/.design/genres/` declara campos, registro e meios. `cq design render` aplica os
mesmos tokens a HTML ou Typst; PDF é compilação da projeção Typst, não um segundo template. As duas
operações e seus gates vivem em
[genre.py](../../../plugins/quenching/assets/bin/quenching/design/genre.py):23. Button, input,
navigation, chip e card formam o vocabulário interoperável; eyebrow, rule e frame são a extensão
editorial do brand pack.

## Ordem de alinhamento

O root `/align` conduz `/.knowledge/` → `/.design/` → `.claude/`. Design vem depois de knowledge
porque projeta produto e instala standards; vem antes de components porque o relatório consolidado
precisa descrever a superfície final. A entrada determinística do novo pilar está em
[cq](../../../plugins/quenching/assets/bin/cq):66.
