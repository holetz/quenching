---
slug: decide-agents-md-harness-default
title: Decide whether AGENTS.md becomes the default harness target
verification: per-section
priority: {level: 29, criticality: medium, date: 2026-07-29}
refined: {mode: gate, date: 2026-07-30}
---

# Decide whether AGENTS.md becomes the default harness target

## Overview

Um arquivo de harness é o `CLAUDE.md` (ou `AGENTS.md`) que a ferramenta do agente lê sozinha no
começo de cada sessão. `/docs:harness` é o comando que mantém esses arquivos finos: ele move o
conhecimento durável para dentro de `docs/` e deixa no lugar apenas um ponteiro.

Este spec responde uma pergunta sobre esse comando: `AGENTS.md` deveria passar a ser o arquivo
preferido? `## Problem` mostra, lendo o código, que a pergunta parte de uma premissa falsa — não
existe preferência nenhuma no comando, que varre os dois igualmente em quinze lugares — e localiza a
assimetria de verdade, que é um molde de arquivo com o título `CLAUDE.md` escrito à mão dentro dele.

`## Proposal` lista o que muda: a resposta é *não há default*, dita por escrito, mais a correção do
molde. `## Design` explica por que a resposta é essa, onde a regra passa a morar e quais contratos
ela não pode contradizer. `## Alternatives Considered` guarda as quatro respostas descartadas,
inclusive a inversão que o título deste spec sugere. `## Out of Scope` marca o que parece próximo e
não entra — em especial consolidar os dois arquivos, que continua sendo escolha de cada repositório,
e renomear os arquivos de molde, cortado por custo.

Uma coisa fica genuinamente aberta e está em `## Open Decisions`: ninguém mediu, neste repositório,
se `AGENTS.md` é realmente carregado. `## Risks` diz por que isso não trava a correção e nomeia os
dois specs irmãos que encostam neste. `## Tasks` começa exatamente por essa medição, e só depois
mexe no gate e no molde — nessa ordem, para que a checagem exista antes do que ela protege.

Duas coisas orientam quem for ler `## Impact`, `## Validation` e `## Handoff`: nenhum script e nenhum
corpo de comando é tocado, então o lockstep de versão não se move e o harness de checks funcionais
não se aplica; e a prova é toda por `grep` sobre assets entregues, porque este repositório não tem um
`AGENTS.md` para exercitar o caminho.

Este spec é o dono de uma decisão que outro spec está esperando: `declare-repo-body-language` adiou a
sua própria pergunta sobre `AGENTS.md` para cá.
## Problem

Deferido do plano `docs-verification-layer` — `AGENTS.md` hoje é uma especificação aberta da Linux
Foundation, com adoção ampla, enquanto os moldes de harness entregam apenas `claude-root.md` e
`claude-subfolder.md`.

_(v1 backlog task — tags: ['docs', 'harness', 'templates'])_

`/docs:harness` refatora tanto `CLAUDE.md` quanto `AGENTS.md`, mas
`plugins/quenching/assets/templates/harness/` entrega apenas `claude-root.md` e
`claude-subfolder.md`. A pergunta original era se o plugin deveria inverter esse default — entregar
um molde `AGENTS.md` e tratar `CLAUDE.md` como o ponteiro específico da Claude — ou manter a forma
atual e registrar o motivo.

**Lido contra o código, o enunciado acima erra num ponto que estreita o spec: não existe um default
específico da Claude no pipeline.** O front trata o par simetricamente em toda parte.
`/docs:harness` faz `Glob` de `**/CLAUDE.md`, `**/AGENTS.md` e `CLAUDE.local.md`
(`plugins/quenching/commands/docs/harness.md:63`); `okf-validate.py` isenta os dois pelo basename
(`EXEMPT = ("CLAUDE.md", "AGENTS.md", "QUENCHING.md")` em
`plugins/quenching/assets/hooks/okf-validate.py:144`); e outros treze sítios citam o par como uma
coisa só — `commands/docs/align.md:93`, `commands/docs/status.md:75` e `:139`,
`commands/docs/glossary-backfill.md:63`, `assets/references/docs-align/okf-spec.md:113`,
`docs-align/conformance.md:16`, `docs-align/taxonomy.md:49`, `docs-align/cycle.md:22` e `:76`,
`assets/references/docs-harness/harness-routing.md:1`, `:23` e `:120`, e
`assets/templates/README.md:32`. Quinze sítios, nenhum deles preferindo um dos dois arquivos.

A assimetria real vive em **dois** lugares, e nenhum é um default:

1. **O conteúdo do molde.** O passo 7 de `/docs:harness` (`harness.md:132-134`) manda qualquer
   arquivo de harness de raiz — `AGENTS.md` incluído — para
   `assets/templates/harness/claude-root.md`, cujo H1 é literalmente `# CLAUDE.md — {repo-name}`
   (linha 1) e cujo comentário final afirma *"Root harness pointer, auto-loaded by Claude Code on
   every turn"* (linhas 57-60). Refatorar o `AGENTS.md` de um repositório hoje produz um arquivo
   cujo próprio título diz `CLAUDE.md`. `claude-subfolder.md:1` tem o mesmo H1 fixo.
2. **A escolha por repositório.** `harness-routing.md` §7 (linhas 120-125) roda o mesmo pipeline nos
   dois arquivos de forma independente, marca **FLAG** num fato duplicado entre eles, e diz que a
   consolidação — tornar um canônico e o outro uma referência de uma linha — é *proposta por
   repositório, nunca assumida*.

**Por que agora.** Dois custos concretos, ambos já presentes na 4.4.0: (a) o arquivo mal-titulado é
um defeito entregue a qualquer repositório que tenha um `AGENTS.md`; (b) o spec irmão
`declare-repo-body-language` deferiu **explicitamente** a sua pergunta de portador para ESTE spec —
*"How it will be decided: by the sibling spec `decide-agents-md-harness-default`, not by this one"*
(`specs/plans/2026-07-28-declare-repo-body-language.md:201-205`) — então um spec enfileirado depende
da resposta, e enquanto ela não é dita a linha fica pendurada.

## Proposal

- A decisão que dá título a este spec fica registrada, e é **não**: `AGENTS.md` não se torna o alvo
  default do harness, porque o plugin não tem — e deliberadamente não passa a ter — um default de
  portador. O que existe no repositório é o que decide, e os quinze sítios que já tratam o par
  simetricamente passam a ser a posição declarada em vez de um acidente não escrito.
- Os dois moldes de `assets/templates/harness/` produzem um arquivo cujo H1 nomeia **o arquivo que
  está sendo escrito**, e não `CLAUDE.md` fixo. Refatorar um `AGENTS.md` deixa de produzir um
  arquivo cujo título mente sobre o próprio nome.
- Nenhum comentário de molde afirma mais que o produto é carregado especificamente pela Claude Code:
  a formulação passa a ser a que `harness-routing.md` §1 (linha 23) já usa para o par.
- O passo 8 de `/docs:harness` reprova um arquivo de harness cujo H1 não corresponde ao próprio nome
  do arquivo — a checklist de honestidade de ponteiro em `harness-routing.md` §5 cresce uma linha,
  para que esse defeito não possa voltar sem ser visto.
- `harness-routing.md` §7 passa a dizer, em uma frase, *por que* não há default — a neutralidade de
  portador é a posição declarada — e a consolidação continua sendo proposta por repositório.
- O spec irmão `declare-repo-body-language` pode fechar o seu §Open Decisions citando este:
  `AGENTS.md` **é** portador em pé de igualdade com `CLAUDE.md`, e a redação do doc dono dele não
  precisa mudar.
- Fica registrado no repositório se `AGENTS.md` é de fato carregado por alguma ferramenta que o
  plugin serve — medido em sonda, não suposto a partir de uma afirmação de adoção.

## Out of Scope

- **Consolidar os dois arquivos neste repositório.** `ls AGENTS.md` falha — este repositório não tem
  um, então não há nada local para consolidar, e criar um só para exercitar o caminho seria pagar
  context tax por um arquivo sem conteúdo próprio.
- **Escrever a consolidação para um repositório-alvo.** `harness-routing.md` §7 já roteia isso como
  proposta por repositório, com FLAG no fato duplicado; este spec mantém a regra e não a automatiza.
  Eleger por conta própria qual dos dois é canônico é exatamente a decisão que §7 diz não assumir.
- **Renomear os arquivos de molde** (`claude-root.md` e `claude-subfolder.md` para nomes neutros).
  Cortado na crítica: o defeito é o *conteúdo* do molde, não o seu nome de arquivo, e o rename
  espalha blast radius por `harness.md:132-134`, `assets/templates/README.md:32` e os dois
  comentários MOLD sem que nenhum agente leia o caminho do asset. Fica registrado como cosmético
  deferido, não esquecido.
- **A tupla `EXEMPT` de `okf-validate.py`.** Já é simétrica (`okf-validate.py:144`) e não muda —
  nenhuma linha de Python entra neste spec, o que é o que mantém o lockstep de versão parado.
- **As outras defasagens de `claude-root.md`.** O molde cita `specs/backlog/` (linha 36), que a
  camada `specs/plans/` substituiu, e nomes `quenching-docs-*` (linhas 48-50) que a coleta de
  comandos retirou. São reais e ficam fora: pertencem a `retire-skill-vocabulary` e ao trabalho de
  layout de `specs/`, não à pergunta de portador.
- **Criar um `AGENTS.md` de raiz onde não existe.** `/docs:harness` só cria ponteiro de subpasta, e
  só com evidência (`harness-routing.md` §6). Passar a criar arquivo de harness de raiz é mudança de
  mandato do comando, não correção de molde.
- **Fechar o §Open Decisions do spec irmão.** A decisão que o irmão espera é declarada aqui, mas a
  linha dele é editada por `/specs:develop` no próprio irmão. Este spec não toca o arquivo de
  nenhum outro spec.

## Impact

**Código e conteúdo que este spec toca:**
`plugins/quenching/assets/templates/harness/claude-root.md` (o H1 da linha 1 e o comentário final das
linhas 57-60), `plugins/quenching/assets/templates/harness/claude-subfolder.md` (o H1 da linha 1),
`plugins/quenching/assets/references/docs-harness/harness-routing.md` (§5 ganha uma linha de
checagem; §7 ganha a frase que declara a neutralidade de portador) e, se a sonda da tarefa 1.1
pedir, `docs/reference/tools/claude-code-skill-command-mechanics.md`.

**O que este spec deliberadamente NÃO toca, e é surpreendente:**
`plugins/quenching/commands/docs/harness.md` fica intacto. O passo 7 dele já cita
`claude-root.md` por nome e o rename do arquivo de molde foi cortado (`## Out of Scope`), então
nenhum corpo sob `commands/**` muda — o que é o que tira `functional-checks.sh` e `/skill:eval` do
caminho. `okf-validate.py`, `specs.py` e `skills.py` também não mudam, então o lockstep de versão
fica em `4.4.0`.

### Standards this spec will write into docs/standards/

- none — a regra já tem dono, e ele não é um doc de standards:
  `plugins/quenching/assets/references/docs-harness/harness-routing.md` §1 é a autoridade sobre o
  que é um arquivo de harness e §7 é a autoridade sobre `AGENTS.md`. Escrever um doc novo para um
  invariante de duas linhas de molde é a restatement que a regra de layout do plugin argumenta
  contra — procedimento compartilhado mora sob `assets/` e é citado, não copiado.

### Standards em `authority: background` que este spec pode resolver

- none — este spec não promove nem resolve nenhuma regra existente; ele conserta um asset entregue e
  escreve uma frase numa reference que já é autoridade.

### Código de produto que este spec espera tocar

- none — este repositório não tem código de produto (`CLAUDE.md`: sem código de aplicação, sem build,
  sem framework de teste). Os dois moldes e a reference são markdown, e nenhum dos três scripts
  entregues é editado.

## Validation

Tudo aqui roda da raiz do repositório. Nada depende de rodar `/docs:harness`, porque este
repositório não tem `AGENTS.md` — a prova é sobre o asset entregue, não sobre uma execução.

- `grep -n '^# ' plugins/quenching/assets/templates/harness/claude-root.md plugins/quenching/assets/templates/harness/claude-subfolder.md`
  não retorna nenhum H1 com `CLAUDE.md` fixo. Os dois H1 nomeiam o arquivo que será escrito, e
  nenhum dos dois carrega placeholder em ângulo no corpo do H1.
- `grep -rn 'auto-loaded by Claude Code' plugins/quenching/assets/templates/` não retorna nada: a
  afirmação específica de ferramenta saiu do comentário final de `claude-root.md`.
- `grep -n 'H1' plugins/quenching/assets/references/docs-harness/harness-routing.md` mostra a linha
  nova **dentro de §5**, a checklist do gate do passo 8. Uma checagem que existe no molde e não na
  checklist é exatamente a defasagem que este spec corrige, então a linha estar em qualquer outra
  seção é uma reprovação.
- `grep -n 'AGENTS' plugins/quenching/assets/references/docs-harness/harness-routing.md` mostra §7
  com a frase de neutralidade de portador e **sem** eleger um canônico. A palavra "default" não pode
  aparecer ali afirmando um.
- `wc -l plugins/quenching/assets/templates/harness/*.md` continua dentro do orçamento que §5
  declara: raiz na ordem de 60 linhas úteis, subpasta na ordem de 20. O spec adiciona conteúdo a uma
  checklist, não a um molde.
- O bloco de lockstep de `CLAUDE.md` §Operating this repo continua verde e **inalterado**, porque
  nenhum script muda: `cat plugins/quenching/VERSION` e os três `--version` concordam em `4.4.0`;
  `python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/docs` e
  `python3 plugins/quenching/assets/hooks/okf-validate.py plugins/quenching/assets/specs/plans --listing-root`
  dão `0 error(s), 0 warning(s)`;
  `python3 plugins/quenching/assets/bin/skills.py --root plugins/quenching doctor --json` dá 26
  comandos sem finding; os três `selftest` passam.
- Se a tarefa 1.2 escrever no bundle deste repositório,
  `python3 plugins/quenching/assets/hooks/okf-validate.py docs` dá `0 error(s), 0 warning(s)`.
- `./plugins/quenching/assets/bin/functional-checks.sh` **não** entra nesta validação, e isso é
  deliberado: nenhum corpo sob `commands/**` muda, e `CLAUDE.md` §Operating this repo diz que o
  harness pertence ao front de skill, depois de mintar ou editar um comando. Rodá-lo aqui seria uma
  sessão de agente cobrada para medir algo que este spec não mexeu.

## Design

**A decisão, como regra durável: o plugin é neutro de portador, e o repositório é a autoridade sobre
qual arquivo existe.** `/docs:harness` refatora o que encontra; não elege portador default, não cria
arquivo de harness de raiz e não consolida um par por conta própria. Isso não é manter o status quo
por inércia — é formalizar o que quinze sítios já fazem, contra a alternativa de inverter o default,
que obrigaria o plugin a decidir por um repositório que ele não conhece.

**O H1 do molde espelha o arquivo produzido.** A correção é de conteúdo, em dois arquivos:
`claude-root.md:1` e `claude-subfolder.md:1` deixam de fixar `CLAUDE.md` e passam a nomear o arquivo
que está sendo escrito; e o comentário final de `claude-root.md:57-60` deixa de afirmar "auto-loaded
by Claude Code on every turn". A afirmação verdadeira é que o arquivo é carregado pelo harness do
agente — que é exatamente como `harness-routing.md` §1 (linha 23) já descreve o par.

**A instrução de preenchimento vive no comentário MOLD, não num placeholder no corpo.** Um
placeholder no H1 é a história de falha S1 do premortem: o passo 7 o preencheria literalmente. Os
comentários MOLD já são o canal de instrução para o agente que aplica o molde
(`claude-root.md:62-77`), e a linha de checagem do passo 8 é o que pega o caso em que ele não foi
seguido.

**A regra não ganha um doc de standards.** Ela já tem dono: `harness-routing.md` §1 define o que é um
arquivo de harness e §7 é dono de `AGENTS.md`. Um doc novo para um invariante de duas linhas de molde
é a restatement que a regra de layout do plugin argumenta contra, e é por isso que a sub-heading
parseada de `## Impact` é um none explícito.

**Contratos que este design não pode contradizer.**

- OKF strict-7 (`assets/references/docs-align/okf-spec.md:113`): arquivo de harness não tem
  frontmatter nem `type`, e o validador o ignora inteiro, link check incluído. Logo nada aqui pode
  depender de uma checagem de `okf-validate.py`; a verificação tem de morar no passo 8 do próprio
  comando, via a checklist de `harness-routing.md` §5.
- `docs/standards/architecture/plugin-layout.md`: procedimento compartilhado mora sob `assets/` e é
  citado, nunca restated — o que decide onde a frase de §7 vai e por que ela não é copiada para
  `commands/docs/harness.md`.
- O bloco de lockstep de `CLAUDE.md` §Operating this repo: `VERSION` e os três scripts entregues têm
  de concordar. Este spec não toca script nenhum, então o lockstep não se move e nenhuma obrigação
  de release entra.
- `harness-routing.md` §5 já declara um orçamento de tamanho (raiz até cerca de 60 linhas, subpasta
  até cerca de 20). A linha nova é uma linha de checklist, não de molde, então nenhum orçamento é
  estourado.

**Reversibilidade.** Desfazer custa uma edição de molde e um parágrafo em `harness-routing.md`. Não
há migração de dados, nada é escrito dentro de um repositório alinhado que precisaria ser revertido,
e nenhum arquivo do usuário muda de nome.

## Alternatives Considered

| Abordagem | Por que perdeu |
| --- | --- |
| **Inverter o default** — `AGENTS.md` canônico, `CLAUDE.md` uma referência de uma linha para ele | A forma mais forte do argumento é boa: `AGENTS.md` é a especificação aberta, o portador que serve mais de uma ferramenta, e um único arquivo canônico elimina a duplicação que `harness-routing.md` §7 já marca como FLAG. Perdeu porque o plugin passaria a decidir a estrutura de instrução do repositório do usuário por ele — e §7 diz, sobre exatamente essa consolidação, que é proposta por repositório, nunca assumida. Inverter também não conserta o defeito real: um molde com H1 fixo em `AGENTS.md` mentiria simetricamente sobre qualquer `CLAUDE.md` produzido. |
| **Paridade total** — entregar `agents-root.md` e `agents-subfolder.md` ao lado dos dois existentes | Resolve o H1 sem discussão nenhuma e é a leitura literal do enunciado do problema. Perdeu por duplicação: os arquivos novos difeririam dos atuais em um H1 e um comentário, e as cerca de 77 e 32 linhas restantes seriam cópia — a divergência silenciosa que a regra de layout do plugin existe para impedir. Quatro moldes para um par de nomes de arquivo é caro num asset que ninguém consegue testar automaticamente. |
| **Só documentar o motivo, sem tocar molde** — a leitura literal do "manter a forma atual e registrar o motivo" do `## Problem` | É a opção mais barata e deixa a decisão registrada. Perdeu porque deixa o defeito entregue: um `AGENTS.md` refatorado continua saindo com `# CLAUDE.md` no título, e um doc explicando que o plugin é neutro de portador ao lado de um molde que não é seria a mesma desonestidade de ponteiro que `/docs:harness` existe para remover. |
| **A menor coisa que funcionaria** — corrigir o H1 do molde de raiz e mais nada | Um diff de uma linha, sem risco. Perdeu por dois furos: `claude-subfolder.md:1` tem o mesmo H1 fixo e continuaria errado, e sem a linha na checklist de §5 nada impede a regressão — o passo 8 não checa H1 hoje, e um molde é justamente o tipo de asset que é editado por outra pessoa meses depois. O custo da diferença é uma linha de checklist e uma frase. |
| **Não fazer nada** | Defensável enquanto nenhum repositório alinhado tiver `AGENTS.md`: o pipeline já é simétrico e o defeito é latente. Perdeu por dois motivos concretos e não hipotéticos: o defeito está entregue na 4.4.0, e o spec irmão `declare-repo-body-language` deferiu a decisão de portador para cá, então não decidir mantém a pendência dele aberta em vez de fechá-la. |

## Open Decisions

- **`AGENTS.md` é de fato carregado por alguma ferramenta que este plugin serve?** O repositório não
  tem essa medição. `docs/reference/tools/claude-code-skill-command-mechanics.md` mede o carregamento
  de comandos e skills na Claude Code 2.1.215 e **não diz nada** sobre `AGENTS.md`; a afirmação de
  adoção ampla vem do plano arquivado (`specs/archive/2026-07-25-docs-verification-layer.md:61`),
  não de uma sonda. **Como se decide:** pela mesma sonda em repositório descartável que produziu
  aquele doc de reference — um repositório vazio com um `AGENTS.md` e nenhum `CLAUDE.md` ao lado,
  observando se o conteúdo entra em contexto no início da sessão, com a versão da ferramenta
  registrada. A tarefa 1.1 existe para isso. O resultado **não** muda a correção de molde: o H1
  mentiroso é defeito de qualquer jeito. Ele muda a linha seguinte.
- **Se a sonda vier negativa, `AGENTS.md` continua no pipeline?** Nesse caso a leitura honesta deixa
  de ser "neutro de portador" e passa a ser "quinze sítios tratam como par um arquivo que ninguém
  carrega". **Como se decide:** com a sonda na mão, pela pessoa, entre manter (custo: nada, o par já
  está escrito, e a especificação aberta pode ser adotada por uma ferramenta amanhã) e retirar
  (custo: quinze sítios, mais uma decisão que fecha uma porta). Este spec não antecipa a escolha; a
  tarefa 1.2 existe para registrá-la quando ela for feita.
- **Com os dois arquivos presentes, o passo 7 escreve o mapa de homes nos dois?** Hoje sim, porque
  §7 manda rodar o pipeline "independentemente" e nada olha o que o outro arquivo acabou de receber.
  **Como se decide:** pela frase que a tarefa 2.2 escreve em §7 — e a escolha é entre apresentar a
  proposta de consolidação em vez de preencher os dois, ou dar ao segundo arquivo um corpo reduzido
  que aponta para o primeiro. A primeira opção é a recomendada, porque a segunda é a consolidação
  automática que §7 diz não assumir; a decisão final é de quem escreve a frase.

## Risks

- **O H1 neutro é preenchido literalmente.** Se o molde passar a trazer um placeholder no H1, o passo
  7 o copia como está e o repositório fica com um título que não é nome de arquivo nenhum — pior que
  o defeito atual, porque o atual pelo menos é um nome válido. Probabilidade média: é exatamente o
  que o molde de raiz já faz com os outros placeholders do corpo. **Mitigação:** a instrução fica no
  comentário MOLD e não no corpo (`## Design`), e a linha de checagem de §5 entra **antes** da edição
  do H1 — grupo 2 antes do grupo 3 em `## Tasks` — para que o gate exista quando o molde mudar.
- **Um repositório com os dois arquivos recebe o mapa de homes duplicado.** §7 marca FLAG num fato
  duplicado *lido*, não em conteúdo *escrito*, então nada hoje nota que o passo 7 acabou de escrever
  o mesmo mapa duas vezes — e o resultado é dois arquivos always-on cobrando context tax pela mesma
  informação, que é o oposto do que `/docs:harness` existe para fazer. Detecção: nenhuma hoje.
  **Mitigação:** a frase da tarefa 2.2, com a escolha registrada em `## Open Decisions`. Fora dessa
  frase nada é automatizado.
- **Irmão `declare-repo-body-language` (em `executing`), cujo §Open Decisions defere a pergunta de
  portador a ESTE spec** (`specs/plans/2026-07-28-declare-repo-body-language.md:201-205`). **ACCEPTED,
  com a fronteira dita:** a resposta daqui é "sim, portador em pé de igualdade", que é exatamente a
  suposição que o irmão já declarou ter feito — então a redação do doc dono dele não muda e nada
  precisa ser refeito. Nenhuma colisão de arquivo: o `## Impact` do irmão nomeia
  `commands/docs/harness.md` e cinco sítios de restatement, e este spec não toca nenhum deles, só
  `assets/templates/harness/*.md` e `assets/references/docs-harness/harness-routing.md`. Este spec
  não edita o arquivo do irmão; quem fecha a linha dele é `/specs:develop` no próprio irmão.
- **Irmão `retire-skill-vocabulary` provavelmente alcança os mesmos dois moldes**, porque
  `claude-root.md:48-50` e `claude-subfolder.md:10-11` carregam nomes `quenching-docs-*` que a
  coleta de comandos retirou. **Mitigação:** este spec toca apenas a linha 1 de cada molde e o
  comentário final de `claude-root.md`; não reescreve corpo nem os bullets de vocabulário, então os
  dois conjuntos de edição não se sobrepõem. Se o irmão entrar primeiro, as tarefas do grupo 3 não
  mudam. A fronteira que este spec mantém: portador, não vocabulário.
- **ACCEPTED — a sonda de carregamento pode nunca ser rodada**, e então a decisão de portador fica
  apoiada numa afirmação de adoção herdada de um plano arquivado. Aceitável porque a correção de
  molde não depende dela e porque a alternativa — travar a correção de um H1 mentiroso numa medição
  de ferramenta externa — troca um defeito entregue por uma espera indefinida.
- **ACCEPTED — a linha de checagem de §5 é uma regra que um humano ou agente aplica lendo, não um
  check mecânico.** OKF strict-7 impede que `okf-validate.py` chegue perto de arquivo de harness, e
  este spec não abre essa porta. É a mesma classe de garantia que todo o resto de §5 já tem, e
  aceitá-la aqui é consistente em vez de novo.

## Tasks

### 1. Decisão e evidência

- [ ] 1.1 Sondar, em repositório descartável fora desta árvore, se um `AGENTS.md` sem `CLAUDE.md` ao lado entra em contexto no início da sessão; registrar a versão exata da ferramenta medida
      verify: o relatório da tarefa cita a versão medida e o comportamento observado, não uma suposição nem a afirmação de adoção herdada do plano arquivado
- [ ] 1.2 Decidir, conforme `## Open Decisions`, se `AGENTS.md` permanece no pipeline, e acrescentar o fato medido a `docs/reference/tools/claude-code-skill-command-mechanics.md` seguindo o procedimento de `/docs:add` (stamp, listagem, self-check) — o skeleton sob `assets/docs/` não recebe nada, porque ele não entrega docs de reference
      files: docs/reference/tools/claude-code-skill-command-mechanics.md, docs/reference/tools/index.md
      verify: python3 plugins/quenching/assets/hooks/okf-validate.py docs

### 2. O gate, antes do molde

- [ ] 2.1 Acrescentar a `harness-routing.md` §5 a linha de checagem do H1, para que o passo 8 de `/docs:harness` reprove um arquivo de harness cujo título não corresponde ao próprio nome do arquivo
      files: plugins/quenching/assets/references/docs-harness/harness-routing.md
      verify: grep -n 'H1' plugins/quenching/assets/references/docs-harness/harness-routing.md mostra a linha dentro de §5 e em nenhuma outra seção
- [ ] 2.2 Escrever em `harness-routing.md` §7 a frase que declara a neutralidade de portador — sem eleger canônico — e a regra escolhida em `## Open Decisions` para quando os dois arquivos existem
      files: plugins/quenching/assets/references/docs-harness/harness-routing.md
      verify: grep -n 'AGENTS' plugins/quenching/assets/references/docs-harness/harness-routing.md mostra §7 com a frase e sem um canônico eleito

### 3. Os moldes

- [ ] 3.1 Trocar o H1 fixo de `claude-root.md` e de `claude-subfolder.md` por um H1 que nomeia o arquivo produzido, com a instrução de preenchimento no comentário MOLD e nenhum placeholder no corpo do H1
      files: plugins/quenching/assets/templates/harness/claude-root.md, plugins/quenching/assets/templates/harness/claude-subfolder.md
      pattern: plugins/quenching/assets/templates/harness/claude-root.md
      verify: grep -n '^# ' plugins/quenching/assets/templates/harness/*.md sem nenhum H1 com `CLAUDE.md` fixo
- [ ] 3.2 Retirar do comentário final de `claude-root.md` a afirmação "auto-loaded by Claude Code on every turn", trocando-a pela formulação de portador neutro que `harness-routing.md` §1 já usa
      files: plugins/quenching/assets/templates/harness/claude-root.md
      verify: grep -rn 'auto-loaded by Claude Code' plugins/quenching/assets/templates/ sem resultado
- [ ] 3.3 Confirmar que o bloco de lockstep de `CLAUDE.md` §Operating this repo continua verde e que nada sob `commands/**` nem em script foi tocado
      verify: cat plugins/quenching/VERSION mais os três --version em `4.4.0`; okf-validate.py em assets/docs e em assets/specs/plans --listing-root com `0 error(s), 0 warning(s)`; skills.py doctor --json com 26 comandos e sem finding; os três selftest passando; git diff --name-only sem nenhum caminho sob commands/ nem nenhum .py
