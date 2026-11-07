# Changelog

Release history for the quenching plugin. The installation and upgrade contract remains in the plugin
README; this file keeps the versioned record that `cq specs release` checks before publishing.

Since 7.0.0 quenching reaches a repository only through `cq deploy`: the target carries its own
copy of the tool at `.agents/quenching/bin/cq` and upgrades by deploying again from a newer release
tag. The only plugins left are the ones that install into no repository (the HUD, the OpenCode
vitrine and the Omnigent operator agent).

What a bump moves, when it moves, and why each half of the lockstep matters is one rule with one
owner: [`ci-cd/versioning-release.md`](docs/standards/ci-cd/versioning-release.md). The
short version for a consumer: the version is published once, deliberately, as a release — never at a
spec's own conclude — and `cq --version` is what answers which one you are running.

## 7.6.0

**O alvo declara o custo do run, e o doutor cobra a diferença entre as três provas.** O
  `proof.cost` em `.agents/quenching.json` nomeia a raiz temporária (`isolated` ou `system`), o
  orçamento de workers (`auto` ou um inteiro) e os três escopos — o que uma task paga, o que o
  fechamento paga e o que o CI paga. O `cq proof doctor` reporta `pf-cost-undeclared` para a chave
  que falta, `pf-temp-shared` para raiz no disco da máquina, `pf-scope-wide` quando o fechamento é o
  CI e `pf-task-wide` quando a task é o fechamento: uma task paga a prova **dirigida** — o arquivo ou
  diretório que ela tocou —, o fechamento paga a **seletiva** do diff dentro do gate, e o CI e o
  release pagam a **inteira**. Como a cadência não mora no comando, ela continua onde já morava: na
  política `verification` da spec (`per-task`, `per-section` ou `end-of-plan`). A declaração é
  renderizada na zona gerada do README de provas, então o que o alvo lê e o que ele declara não
  divergem; a norma `ci-cd/test-cost.md` acompanha o plugin e explica a adoção sem os helpers deste
  repositório. Nada disso instala runner: a frente ensina o contrato e gradua a declaração.

## 7.5.0

**A suíte e o gate deixam de escrever centenas de megabytes no disco.** O gate resolve um único
  temp root em RAM (`$XDG_RUNTIME_DIR`, `/dev/shm` ou um Dev Drive no Windows, com o temp do sistema
  como último recurso e um `NOTICE`) e o remove no fim, inclusive em SIGINT/SIGTERM; a suíte com
  `-n auto` caiu de 688,6 MB e 54.538 escritas para 1,7 MB e 1.536, e o gate inteiro de 723,2 MB para
  36,3 MB. O mesmo bootstrap dá a todo `git` um arquivo de configuração do run
  (`GIT_CONFIG_GLOBAL`), então hooks, assinatura e `init.defaultBranch` da máquina não entram num
  teste. Um orçamento de workers em arquivos com lock de kernel divide os núcleos entre gates
  concorrentes, e uma execução aninhada roda serial dentro da cota do pai em vez de enfileirar.
  **Três camadas, um gate:** `scripts.toolchain.test --affected` para a task, o gate com
  `QUENCHING_TEST_SCOPE=affected` no fechamento (piso de cobertura `SKIPPED`) e a suíte inteira no CI
  e no `/release`; `QUENCHING_FULL_GATE=1` força a camada completa mesmo com um escopo exportado no
  shell, e a skill de release passa essa flag para que uma tag nunca seja decidida sobre um
  subconjunto. Os testes das próprias ferramentas rodam no job Windows.

## 7.4.0

**`cq git stale` separa cache regenerável de ignorado que pode guardar trabalho.** Cada worktree
  avaliado passa a carregar `ignored: {regenerable, unrecognized}` e motivos granulares
  (`tracked-changes`, `untracked-files`, `ignored-content-unrecognized`) no lugar do rótulo único
  `dirty-or-ignored-content`. O conteúdo que o repositório recompõe — a lista embutida de caches de
  Python somada ao `shared.regenerablePaths` declarado — não bloqueia nem alerta; qualquer outro
  ignorado é listado por caminho e mantém o worktree preservado. Um worktree mesclado, limpo,
  destravado e sem ignorado não declarado vira `candidate` e `recommended: true`; a remoção continua
  exigindo a confirmação do dono e nunca usa `--force`.
  **`worktree retire` lê a mesma fonte** (`quenching/git/ignored.py`), então o `.venv` que travava o
  cleanup orquestrado também deixa de travar o `retire`. A lista embutida cobre caches inequívocos
  (`.venv`, `__pycache__`, `.pytest_cache`, `.ruff_cache`, `*.egg-info`, `.coverage`, `.coverage.*`,
  `node_modules`, …) e deixa `build/` e `dist/` para o alvo declarar. O `cleanup.md` ganha a decisão
  D3, separada das branches, com as duas classes e os caminhos exatos.
  **Compatibilidade:** o rótulo `dirty-or-ignored-content` sai de `blockers` — quem casava a string
  passa a ver `tracked-changes`, `untracked-files` ou `ignored-content-unrecognized`.

## 7.3.0

**A home `communications/` entra na árvore canônica e `type: communication` dispensa `resource`.**
  O aviso já enviado a um público — incidente, mudança, release — passa a ter casa própria no
  bundle: uma página por aviso, datada no caminho (`<ano>/<aaaa-mm-dd>-<slug>.md`) e na ficha, com
  `index.md` reservado na home e em cada ano. O tipo `communication` entra na tabela por home e em
  `TYPES_WITHOUT_RESOURCE`: um aviso operacional muitas vezes não aponta para ativo nenhum, e o
  `resource` que ele **tem** continua sendo resolvido. O roteiro do `/quenching-knowledge add`
  ganha a linha e o desempate contra `documentation/`; o caminho do `/quenching-knowledge align`
  deixa de tratar a home como fora da árvore.

## 7.2.0

**`cq git worktree add` roda o `worktreeSetup` declarado.** Logo depois do corte e do link, o
  próprio verbo executa uma vez o setup declarado em `.agents/quenching.json`, com cwd dentro do
  worktree novo, e todo chamador (skill, subagente, humano) recebe um worktree pronto. A declaração
  é lida da base cortada, nunca da árvore de quem chama. O comando é impresso literalmente e a saída
  vai para stderr, de modo que `--json` segue parseável (`setup`: `command`, `exit`, `ok`). Uma falha
  do setup é exit 1 e não desfaz o worktree. `--no-setup` pula a etapa.
  **Segurança:** quem tem o grant do verbo passa a rodar o setup do repositório sem novo prompt; a
  declaração rastreada é o consentimento (`git/isolation.md`).

## 7.1.0

**Uma skill roteadora por vertical ou front, e a invocação `/quenching-<vertical> <fluxo>`.**
  Cada fluxo é uma reference da skill da vertical (`quenching-specs`, `quenching-git`,
  `quenching-knowledge`, `quenching-components` e uma por front), que escolhe o fluxo pela própria
  tabela e concede a união dos grants dos fluxos. **O deploy do tag `7.1.0` reescreve a superfície do
  alvo**; num repositório que ainda carrega a família antiga de comandos,
  `cq components migrate --write --router` agrupa a família sob o roteador com as references dentro
  (ADR 0019).

**A fonte é escrita no dialeto do alvo, nas raízes `quenching/` e `integrations/`.** `plugins/` sai.
  O `cq deploy` reescreve só o frontmatter, o cabeçalho gerado, os grants e o launcher, e recusa uma
  fonte que ainda carregue marcador de plugin; o HUD do Claude e o vitrine do OpenCode passam a viver
  em `integrations/`. Os módulos acompanham: `quenching-git`, `quenching-knowledge` e
  `quenching-components` entram, e `quenching-align` vira apelido de `knowledge,components`. O layout,
  o modo de deploy e os perfis de instalação estão em `source-layout.md`, `deploy-mode.md` e
  `install-profiles.md`.

**O deploy instala os hooks.** Cada módulo declara seus hooks em `assets/modules.json` e o `deploy`
  mescla o `.claude/settings.json` do alvo, preservando as linhas de atribuição; um `settings.json`
  que não é arquivo é recusado em vez de sobrescrito.

**Allowlist de identidade no git.** `shared.gitIdentity.allowedEmails` recusa em exit 2 o commit ou o
  push cujo autor não casa a lista exata ou o padrão `fnmatch` declarado. Ausente a chave, nada é
  julgado.

**O orçamento de 100k do worker vira estimativa de tamanho.** O `spec-runner` não devolve mais
  `STATE: continue` com `NOTE: budget:`: ele termina a spec e reporta o pico, e `execute` sob
  `autonomous` imprime e segue. O orçamento do conductor (150k) continua o único stop, entre waves; o
  da sessão principal (200k) continua oferta. `context-discipline.md` §Measured context budgets passa
  a separar estimativa de tamanho de limite de parada, e `cq specs estimate --worker-budget` continua
  usando o número para recomendar decomposição.

## 7.0.2

**A cor transparente dos tokens vira cor Typst.** O `tokens.typ` projeta `srgb`, `srgb-linear`,
  `hsl`, `oklab` e `oklch` como construtor de cor do Typst, `alpha` incluso, para o template consumir
  o token em `fill:` ou `stroke:`; um espaço que o Typst não constrói mantém a string CSS portátil, e
  o adaptador nunca converte wide-gamut por conta própria. A linha do `srgb` opaco mantém os bytes que
  os repositórios instalados já carregam.

**O ciclo de spec para de pagar contexto que já está quente.** Um `needs-human:` respondido volta ao
  MESMO agente por `SendMessage`, dentro da janela medida em `cq components session cache`, em vez de
  um relançamento frio — que continua sendo a resposta honesta para `budget:`, host sem canal,
  `agentId` perdido, decisão fora da janela e repetição de uma decisão já registrada. A resume conta
  em `resumes:`, nunca em `launches`, e vale também para o `spec-runner` em economy mode.

**O relatório fixo carrega o exit do gate em campo próprio.** `GATE_EXIT:` fica ao lado de `GATE:` em
  todo STATE, e o verifier lê o código como claim, sem garimpar número em prosa; linha omitida é
  inconclusiva, nunca passe.

**Task que não escreve arquivo se declara `files: (operational)`.** O marcador é o `files:` inteiro —
  `validate` recusa misturado com caminho (`sp-files-operational`), a operacional sem `verify:` avisa
  (`sp-operational-no-verify`), o grupo `[P]` fica inelegível e o Codex não a recebe. `next` e
  `show --task` entregam `operational: true` com `files: []`, e é o flag — nunca a lista vazia — que
  dispensa o sha no verifier; o scope check continua cobrando qualquer arquivo que a task escreveu. O
  template e o schema documentam a anotação em lockstep byte a byte.

**Sob `autonomous` o `conclude` abre o PR.** O run publica sozinho depois do gate verde, em qualquer
  complexidade, porque a publicação não pode depender de um orquestrador que talvez não exista; o
  `spec-orchestrator` adota esse PR no PASS do verifier em vez de abrir um segundo.

**O corte de worktree aceita a base suja sob autorização explícita.** O passo 1 do autopilot decide o
  checkout sujo e grava a decisão no round record e no `## Design` do épico antes do lançamento que
  depende dela; o corte autorizado parte de `origin/<base>` e reporta os caminhos que ficam na base,
  nunca dentro da worktree. O formulário Branch, que roda `git checkout -b` no próprio checkout,
  continua recusando.

**O `## Design` do épico passa a ser leitura, append e uma escrita.** `cq specs section --write`
  substitui a seção, então as decisões do dono delegado viram bullets datados escritos antes do
  lançamento; o brief do passo 5 abre com o prefixo fixo e fecha com as variáveis, e o develop
  pergunta na composição quais testes a task toca, para declará-los em `files:` junto da
  implementação.

## 7.0.1

**Painel Specs do OpenCode sem depender do `cq` no PATH.** O `quenching-vitrine` passa a rodar o
  `cq` do checkout de onde é carregado (`plugins/quenching/assets/bin/cq`) para a checagem de versão e
  o deploy, na ordem `QUENCHING_CQ` → checkout do plugin → PATH; as leituras de spec continuam
  preferindo o `.agents/quenching/bin/cq` do projeto. Scripts Python rodam pelo interpretador
  (`python3`; `py -3` ou `python` no Windows) e o shim do `--runtime uvx` pelo `cq.cmd` via `cmd.exe`,
  o que destrava o painel no Windows. Requisito do painel: Python 3.11+ e git. Para atualizar, basta
  atualizar o checkout e reiniciar o OpenCode.

**Delivery reconhece `rustup toolchain install` como setup do job.** Um job que instala a toolchain
  Rust por `rustup` deixa de ser acusado de `delivery-setup-missing`.

**Deploy por clone deixa de vendorizar o `quenching_launch.py`**, como o deploy por uvx já fazia; a
  documentação explica o placeholder `<tag>` do uvx e o `--modules` no upgrade.

**Dependências**: `actions/setup-python` 7.1.0, `astral-sh/setup-uv` 10.3.3, `ruff` 0.17.3,
  `coverage` 7.17.0, `pytest` 9.2.0, `zensical` 0.0.73.

## 7.0.0

**Quebra: o quenching deixa de ser distribuído como plugin e passa a ser servido só por instalação
  no repositório alvo (`cq deploy`).** Saíram os oito plugins de módulo do Claude e o
  `quenching-specs-reader`, o plugin Codex com seu marketplace (`.agents/plugins/marketplace.json`),
  a distribuição OpenCode em `~/.opencode/`, os seis geradores e validadores dessas árvores,
  `cq components translate` e a checagem de upgrade do Codex no gate e na CI. **Quem instalou pelo
  marketplace** deve desinstalar os plugins `quenching-*` (menos o `quenching-hud`, se quiser a faixa)
  e rodar, a partir de um clone deste repositório no tag `7.0.0`,
  `python3 plugins/quenching/assets/bin/cq deploy --target <repo> --write`; os comandos passam a se
  chamar `/quenching-<front>-<verb>`. Ficam como plugin só o `quenching-hud` (único item do
  marketplace), o `quenching-vitrine` — painel Specs do OpenCode Desktop, adotado nesta versão — e o
  agente operador do Omnigent. `assets/modules.json` vira o manifesto do deploy (schema 2), o lockstep
  de versão cobre a fonte, o HUD e o marketplace, e as checagens de carga da superfície e o braço
  `with` das evals medem alvos instalados por `cq deploy` (ADR 0017, que supera o 0013).

**Skills roteadoras por vertical.** Specs, knowledge, components e git ganham um ponto de entrada
  cada (`quenching-<vertical>-<vertical>`), com os fluxos em references e os atalhos fora da lista do
  modelo; o align dos repositórios alvo propõe o roteador da família e estende verticais sem editar os
  agentes do pacote.

**Contrato de confiança no intent.** Os gears deram lugar a profundidade calculada e autonomia
  declarada: o desenvolvimento roda na sessão principal com perguntas em lote e refino escolhido por
  necessidade, e a execução aprovada segue sozinha, registrando decisões e parando só em bloqueio
  real.

**Cinco agentes de spec** — runner, verifier, reviewer, scout e orchestrator; git e decomposição
  viraram fluxos das verticais.

**Medição por harness.** `cq components session cache` publicado, `session context` mede sessões do
  OpenCode, o worker do OpenCode ganhou orçamento, e a medição por harness foi refeita e registrada em
  `context-discipline.md`.

## 6.14.2

**A regra do `AGENTS.md` para no PR quando o humano não declara autonomia.** O molde do harness
  raiz mandava um pedido omisso rodar o fluxo inteiro — PR/merge e deploy inclusive. A fronteira
  agora é o **PR**: um pedido que nomeia a mudança ("implemente X melhoria") vai até o PR aberto sem
  parar para perguntar, e **merge e deploy só rodam quando o humano declara autonomia no próprio
  pedido** ("faça de forma autônoma", "PR e merge", "até o deploy"); sem essa palavra o run termina
  no PR, nomeado para o humano decidir. A skill `components:harness:align` mantém a linha como KEEP
  e diz a mesma fronteira.

## 6.14.1

**Um membro de épico com a branch renomeada depois do carimbo deixa de aparecer `unverified`.** O
  `epic status` só aceitava o estado do PR quando o head era igual ao `branch.work` gravado, e o
  `branch:` é write-once: uma branch renomeada depois do stamp — como as specs 984570 e 1018611
  fizeram — ficava com o nome velho no registro e a entrega provada pelo merge virava "PR #N state
  could not be read". Agora o estado é aceito quando o membro carrega um record `merge:` que nomeia
  **o mesmo** PR e esse PR está `MERGED`; `merge.pr` diferente, PR aberto e membro sem record
  `merge:` continuam fora, e a derivação segue marcando `unverified`.

## 6.14.0

**Arquivar uma spec não pede mais aprovação ao humano.** `specs_promote` e os registros `reviewed`,
  `merge` e `outcome` deixaram de abrir `elicitation/create` na superfície MCP: num fluxo autônomo
  — e em qualquer cliente sem `elicitation`, onde a resposta era `mcp-confirmation-unavailable` — a
  conclusão parava no pedido de aprovação e o agente voltava ao humano no meio do processo. A
  decisão humana continua recolhida **uma vez**, no registro `approved` (`by=human`, e só numa spec
  que cumpriu o gate de pronto); o que o fluxo conclui depois disso roda como os verbos do CLI, que
  nunca pediram confirmação. O `promote` segue recusando (exit 2) o que o gate de conteúdo recusa —
  `## Outcome` vazio, tarefa aberta sob `done` —, e continua sem `--force` pela superfície.

**`outcome` saiu do enum de `specs_record`.** A ferramenta o listava e sempre falhava com
  `sp-record-not-writable`; `specs_promote` é o único escritor do carimbo, e agora a descrição diz
  isso.

**Um pedido de desenvolvimento é um pedido para rodar o fluxo inteiro.** O molde do `AGENTS.md`
  raiz, que a skill `components:harness:align` escreve, passa a carregar a regra: "implemente X
  melhoria" é um pedido para construir — develop, execute, conclude, PR/merge, deploy —, e só "crie
  uma spec para X" para na spec. A linha é KEEP onde o repositório tem store de specs, e a skill a
  mantém em toda realinhagem.

## 6.13.0

**The knowledge front reads and writes OKF v0.2.** A bundle may declare
  `okf_version: "0.2"`; `0.1` is still read under the spec's fallbacks. The validator now
  checks the optional v0.2 families when they are present — `generated` (`by` actor + `at`
  ISO 8601 datetime), `verified`, `status`/`stale_after`, `sources`/`usage_window`, and the
  `Attested Computation` type — and reports a malformed value without rejecting a bundle that
  omits the family. The actor convention is `human:<id>`, `process:<id>` or
  `<producer>/<version>`.

**`generated.at` supersedes `timestamp`; the legacy key stays readable.** Templates, the
  alignment molds and the capture commands now write `generated: { by, at }`. A doc that still
  carries only `timestamp` is not a finding: it is the v0.2 fallback, and rewriting it without
  an evidenced actor would fabricate provenance. `cq knowledge status` and `--activity` read
  `generated.at` first and fall back to `timestamp`.

**`generated: true` is the projection marker, not the family.** The generated-glossary marker
  keeps its name; the validator only reads the v0.2 family when `generated` is a mapping.

**The reference is the canonical v0.2 text.** `knowledge-align/okf-spec.md` now condenses
  `GoogleCloudPlatform/open-knowledge-format/SPEC.md` (the old `knowledge-catalog/okf/` copy is
  a frozen v0.1 snapshot), including the `Attested Computation` contract and the
  `sources` footnote attribution.

## 6.12.0

**Spec store writes accumulate locally, and the store branch keeps one commit.** A write to the
  git-backed store lands in the local ref `refs/quenching/pending/<branch>` instead of pushing. That
  ref holds one commit, replaced on each write, and reads see it. The pending change reaches the
  remote only at a sync point:
  - create, archive or restore, import, and `write_config`;
  - the new `cq specs push [--drop <id>…]`;
  - the end of `cq git push`, `pr create` and `pr merge`.

  A sync sends one parentless commit under `--force-with-lease`. It falls back to a fast-forward
  when the remote refuses rewrites. Conflicts are judged per spec id at the sync. Card transitions
  fire once per sync, and `cq specs status` reports unsent local writes. ADR 0016 records the
  decision.

**Every module is visible to the router again.** Claude Code 2.1.312 puts a plugin's `bin/` on
  `PATH` only when the directory exists. Every principal module except `quenching-specs` now ships a
  non-executable `bin/README` marker, so the router discovers its siblings. Without it, a bare
  `cq knowledge …` refused with "module not enabled".

**One suite run per gate.** `scripts/verify_repo.sh` runs the randomized suite in parallel under
  coverage, once. CI drops the duplicate suite step.

**Deploy completes its own surface.** An upgrade with `cq deploy --write` reuses the module
  selection recorded in the manifest. The `opencode` harness writes OpenCode subagents. The gate
  checks the repository's installed surface against its source.

## 6.11.0

**Deploy selected quenching modules directly into a target repository.** `cq deploy` creates
  the generic `.agents/skills/` surface, a manifest-owned payload under `.agents/quenching/`,
  and the generated Claude skills bridge. The default runtime is vendored and offline;
  `--runtime uvx` uses a shim pinned to the release tag. Module selection, drift checks and
  ownership conflicts are deterministic. Existing target instructions, configuration and
  authored skills are preserved, and installation does not run alignment or choose a backend.

**`AGENTS.md` is the native instructions source.** Harness templates, migration, the shipped
  knowledge skeleton and documentation use `AGENTS.md` directly for Claude Code 2.1.277+.
  Migration removes redundant legacy pointers instead of creating them. Generated deploy skills
  are reported separately from the target's authored components. Claude, Codex and OpenCode
  distributions carry the regenerated runtime and instructions.

## 6.10.1

**The shipped prose cites the generic `.agents/` layer, Omnigent reads references as MCP
  resources, and the OpenCode upgrade path is explicit.** `components:command:eval` writes the case
  set beside the skill at `.agents/evals/<name>/`; the plugin README, standards, references,
  templates and the OKF skeleton name `.agents/quenching.json`, with `.claude/quenching.json` kept
  as the documented legacy read. The MCP server rewrites a served reference's plugin-root sibling
  links to `quenching://references/`, and the Omnigent operator replaces the 23 `cq components read
  quenching://...` shell blocks with the resource URI they should read. The OpenCode distribution
  documents the 6.9.0 → 6.10.x upgrade: remove the old `~/.config/opencode` copy before installing
  under `~/.opencode`. The verifier protocol records that the orchestrator stamps
  `verifier=pass|fail` from a verifier verdict; the verifier itself stays read-only.

## 6.10.0

**`plugins/` is organised by harness, target repositories align on the generic `.agents/` layer,
  and the `cq` core is served over MCP.** The Claude modules live under `plugins/claude/`, the
  Codex package under `plugins/codex/quenching-codex/`, the OpenCode distribution under
  `plugins/opencode/quenching-opencode/` (installed at `~/.opencode/quenching`), and Omnigent gets
  one operator-agent bundle at `plugins/omnigent/quenching/` with the seven sub-agents and the MCP
  server launched by `uvx` from the tag; under OpenCode `skills: none` does not hide the host's
  `~/.claude/skills` or `~/.agents/skills`. `cq mcp` serves the whole catalog (specs reads and
  gated writes, `git_pr_merge`, `git_worktree_retire`, configuration, standards and the glossary),
  and the Claude plugin's `.mcp.json` names it `quenching`. In a target repository, skills are
  authored in `.agents/skills/<name>/SKILL.md` with `AGENTS.md` as the instructions source and
  `CLAUDE.md` reduced to `@AGENTS.md`; `cq components bridge` generates the Claude copy under
  `.claude/skills/` with a sha256 manifest and fails on drift, and `cq components migrate` plans
  and applies the move from the old layout, classifying an old translation by its content and
  reporting anything hand-written as a conflict, with no writes. `cq components translate` refuses a
  migrated target. The configuration home is `.agents/quenching.json`, but `.claude/quenching.json`
  is still the file read while it exists, so an upgrade changes no repository's configuration.
  The specs store gains a GitHub Issues adapter with native dependencies, Azure Boards predecessor
  links, a migration from the git store onto Azure Boards, a local Azure DevOps cache, a Gantt view
  in the specs service and `--root` on `cq specs` and `cq git` for cross-repository checks.
  `quenching.json` is read through a configuration provider. OpenCode receives the command surface
  with per-agent `cq` grants. Windows runs without administrator rights, with a Windows job in the
  PR gate. The leak gate covers every project repository. The orchestrator, spec-runner and
  verifier protocol is tightened: only the orchestrator stamps `verifier=pass|fail` from a
  verifier verdict (the verifier itself stays read-only), and `cq git pr merge` records the merge.

## 6.9.0

**The Codex package is published through the Git marketplace and its upgrade is measured before
  every release**, and **the `components` verbs judge the target they are given**. A new
  `.agents/plugins/marketplace.json` lists `quenching-codex` under the existing `quenching`
  identity, so installations from 6.4.0 keep their update route; `assets/modules.json` declares
  each package under `distributions`, and `distribution_findings` refuses a release whose catalogs
  miss, misplace or misname a package. `scripts/check_codex_upgrade.py` installs the published 6.4.0
  package in an isolated home, upgrades it through a disposable Git marketplace and checks the
  installed skill and bundled `cq --version` without a model call; CI runs it, and the gate runs it
  under `QUENCHING_DISTRIBUTION=1`, which `/release` requires. Generated Codex shell blocks resolve
  the host-provided root or the single enabled installation, never the first or newest cache
  directory. `cq components lint` and `cq components cost` now judge the path passed (citations,
  a nested command file named by its full nested path, agents, a surface with no commands refused
  with `sk-no-commands` before any ratchet); the agent autocheck keeps every error of the agent
  itself; a removed command still cited elsewhere is a finding; `cq components registry reindex`
  stops at the target repository's root. `cq git pr merge` re-reads the provider state before
  reporting a refusal, so a concurrent merge is reported as merged; `cq codex implement` no longer
  returns `fallback: true` on a `codex-git-guard` refusal. The repository gate runs
  `cq knowledge doctor`, the validator warns `sp-generator-no-files` on a generator task with
  `files: []`, and the verifier's scope rule covers such tasks.

## 6.8.0

**`git cleanup` assesses registered worktrees and works from one dated manifest**, and **Azure
  DevOps pull requests complete through `cq git pr merge`**. `cq git stale` now assesses every
  registered worktree (dirty, unpushed, locked, merged) next to the branches, dates each item by its
  tip's committer date, and emits a manifest of stable ids with the exact action per item and
  recommended groups; `/git:cleanup` offers grouped local and remote choices over that manifest and
  stops only when it is empty, so a clean detached candidate worktree is offered too; `cq git prune`
  takes `--id`/`--expect-tip` and refuses an item whose tip moved since the report, and a live
  worktree only with `--confirm-inactive`. The merge route accepts modern and legacy Azure browser
  URLs, requires an approved build-validation policy, pins the verified source commit and completes
  no-fast-forward without bypassing policies, deleting the source branch or transitioning work
  items, confirming completion before cleanup. The Codex review guard fails closed on any
  file-system error while taking its snapshot (the run folder is removed before the run) and sees
  writes through tracked and ignored symlinks to files; a symlink to a directory stays a declared
  residual risk. The ops registry reads the lifecycle only from hand-written lines, never from its
  generated zone, so a component can move to `archived`; the opensource front writes and audits
  community artifacts in English through a declarative `language: en` per template, whatever the
  repository's declared language; and the repository no longer carries employer identifiers in
  code comments, docs or test fixtures.

## 6.7.0

**Azure DevOps pull requests are read wherever `cq` judged them through `gh` alone**, and **Codex
  runs only under bypass with a git guard**. On an Azure origin the epic derivation (`status
  --epic`, `next --epic`, `promote`) reads member PRs with `az repos pr show` instead of marking
  every merged member `unverified`; the new read-only `cq git pr view --number N` gives the
  verifier's delivery check one route on GitHub and Azure; `cq git stale`/`prune` keep an Azure
  branch with an open PR; and `cq git preflight` probes the `az` route under `ghAuth`. The native
  Codex sandbox path is gone: review and executor run under bypass behind a git guard that now
  also catches the index, refs outside `HEAD`, ignored files, a failing `git status`,
  assume-unchanged/skip-worktree entries and ignored symlinks, and `cq git worktree retire` no
  longer refuses the `.quenching/codex/` artifacts (Windows paths included). A plugin-wide hook
  denies Claude co-authorship in commit and PR messages; the portal's sessions panel shows the
  pending question's `pendingTool`; `files:` must name derived mirrors from develop on; and `cq
  specs doctor` warns when the `github` backend is only inferred from the remote.

## 6.6.0

**Codex became a per-task executor, on by default**, and **configuration became one visible home**.
  `/quenching-specs:specs:execute` hands a task to Codex when `cq codex eligible` admits it — small
  by its declared `files:`, or carrying a runnable `verify:` — one dispatch at a time, behind a quota
  reserve and a stop-loss, through `cq codex implement` (bypass by default, native sandbox opt-in),
  with a git guard and the session model correcting on top of the Codex diff when `verify:` fails.
  The model policy now admits the small tier — `haiku` and `gpt-6-luna` — on a task with a protected
  `verify:` oracle projected under 80k (`cq specs estimate --task`), provisional until the pilot (ADR
  0014); judgment never moves down. Configuration gained a user layer
  (`~/.config/quenching/config.json`, the repository wins key by key), `cq config show --effective`
  with each value's origin, `cq config init` seeding every tunable default, `shared.autonomy`
  (which complexity runs unattended, merge, parallelism, stops), `shared.workHost` for heavy work
  over SSH, and the context budgets, launch ceiling and portal chat limits as keys. `cq specs
  release` now regenerates the module copies and commits the changelog entry.

## 6.5.0

the plugin **split into installable modules** (`quenching-specs`, `-align`, `-design`, `-ops`,
  `-proof`, `-toolchain`, `-delivery`, `-security`, `-opensource`), generated from one source,
  and **Codex became an independent reviewer by default when quota allows**: a `cq codex` pillar
  (`probe` reads the quota, `review` runs read-only), a Codex pass beside the opus review in the
  autopilot and in conclude with a reported fallback, and an optional per-task hook in execute.
  The autopilot gained cost control — one round by default (`--until-dry` drains the queue), a
  measured launch ceiling, an orchestrator that returns `continue` past its own budget, an
  economy mode without an orchestrator for small epics, and a deterministic `cq git preflight`.
  The portal became multi-project (`cq portal serve`, `cq portal add/remove/list`) with a live
  sessions panel behind `--sessions`, a read-only chat tab, an HttpOnly cookie in place of the
  URL token, and the spec-runner's last record on the board. Every human question became a text
  decision sheet; the verifier tells relocation from widening and accepts byte-identical generator
  output; the git-steward no longer fires two merges for one PR; `session cost --self` scopes cost
  per orchestrator; and `opensource` controls with `SECURITY.md` bring the repository to OSPS
  level 1.

## 6.4.0

specs **left the issue body**. A spec now lives on the git branch `quenching` (`specs/`,
  `specs/archive/`, `quenching.json`), written by plumbing without a worktree, with the push as the
  compare-and-swap; the GitHub issue or Azure work item becomes a thin card written only at
  lifecycle transitions (`cq specs new --card <n>` adopts an existing one). `cq specs migrate --to
  git` moves a tracker-backed repository; the tracker backends keep working and `doctor` flags them
  deprecated. Also new: epics (`workItemType: epic`, `status`/`next --epic`), a local portal
  (`cq specs serve`, `/quenching:specs:board`), plugin agents with `/quenching:specs:orchestrate`,
  and `AGENTS.md` as the single harness. Non-core fronts (design, ops, proof, toolchain, delivery,
  security) and human-only leaf commands are now typed-only (`disable-model-invocation`), and every
  description fits 250 characters.

## 6.3.0

the ranked front became **native to the tool**. `cq specs next --front --table`
  renders the ordered listing itself instead of every caller re-deriving it, with `summary:` as its
  own column — one line saying what a spec is, written at capture and refreshed by every
  `/quenching:specs:develop` pass, and the only short description a ranked listing prints. Four
  command bodies dropped their hand-rolled renderers onto it.

## 6.2.0

`cq` stopped depending on how it was invoked. The tool resolves per call — bare on the
  PATH or at `${CLAUDE_PLUGIN_ROOT}/assets/bin/cq`, the same file either way — which removed the
  `PATH` assumption every body used to carry. Commands were also re-allocated by category, so a
  command's path names the front that owns it.

## 6.1.0

**`/.docs/` became `/docs/`.** The bundle, the commands, the standards, the
  skeleton and every citation moved together; `type` follows the home a doc sits in, and that rule
  became a standard rather than a convention people remembered.

## 6.0.1

the section squash — a build commits one commit **per `## Tasks` section**, not one per
  task, with the per-task subjects repaired onto the squashed commit afterwards. `/quenching:specs:execute`'s
  steps f/h/i were tightened to fit the body cap.

## 6.0.0

**the tooling modularized.** Three standalone tools from the pre-modularization
  layout became one binary, `cq`, over a `quenching` package with a pillar per front —
  `cq specs`, `cq knowledge`, `cq components`, `cq git`. The `skills` pillar was renamed
  `components` with it. Every command body drives the pillar, and nothing installs a copy of
  anything any more.

## 5.0.0

the Azure Boards backend stopped costing one `az` call per field. Writes batch into a
  single PATCH, the board column is resolved and diffed rather than written blind, and
  `architecture/spec-backend.md` was written to hold the placement and granular-reading rules the
  work revealed.

## 4.13.0

the specs front's preamble citations were aligned to the bodies that actually carry
  them, and the Azure Boards backend was positioned honestly — shipped, but without an end-to-end
  run against a real project, which `doctor`'s `sp-backend-unproved` finding names on every
  selection.

## 4.2.0

**nothing is written after the thing it describes, so the merge is last.** The
  task→commit anchor inverted from the commit's **sha** to its **subject** — known *before* the
  commit exists — which let two writes move ahead of the events they record. `/quenching:specs:execute` now
  ticks the box with `cq specs task --check --subject` and commits code and box together, so one
  task is literally one commit and the per-task bookkeeping commit is gone. `/quenching:specs:conclude`
  reordered: the branch review, the emergent `/docs/`, the archive, the distillation and the
  `merge: {strategy, subject}` stamp all land on the work branch, and **the merge is its last
  action** — one merge carries the spec's whole footprint and nothing is committed to the base
  after it. Rebase stops destroying the record, since a subject survives a rewrite; the squash
  caveat stands. A **25th command** (an isolation command, since retired) extracts the git *action* — branch or
  worktree, at **any** stage rather than only at build time — and `cq specs next --front` became
  branch-aware, so the front router (since retired) returned the spec whose branch you were standing on and demoted
  one alive elsewhere. `parse_frontmatter` learned block mappings (indent-scoped), which is what
  lets an explicit-none merge record wrap or carry a comma. The ordering check (now retired)
  asserted the ordering on a real history — the one claim no in-process check can see. The always-on
  ceiling fired on the 25th command exactly as designed and was re-measured to **12,726**.

## 4.1.0

**the capability layer got proved, applied and closed.** Both new mints were measured
  by `/quenching:components:command:eval` — `/quenching:components:agent:new` at +0.364 pass rate for 182,367 fewer tokens,
  `/quenching:components:hook:new` at +0.5 for 52.5% cheaper — and each gained an intent-shaped trigger plus a
  sandboxed routing probe, taking `functional-checks.sh` to **9 assertions across 7 sandboxed
  sessions**. `cq components` closed its two blind spots: `lint` now reads a **frontmatter `hooks:`
  block** (the scope ladder's narrowest rung, the mold's shape only, fail-open via
  `sk-hook-unparseable`) and serves both rungs from one implementation, and the cost report counts
  `agents/*.md` descriptions as its own breakdown line; the ceiling was re-measured and re-set to
  **11,565** from a run. The profile doctrine was then applied to its own author: five inline
  `effort:` pins dropped for the prompt-cache trap, `Bash` scoped on the specs-front align,
  `/quenching:components:harness:align` and `/quenching:knowledge:glossary-backfill` and priced in the body of the two that keep it,
  frontmatter `hooks:` blocks on `/quenching:knowledge:add`/`/quenching:knowledge:learn`/`/quenching:knowledge:define`, and a collection-only
  `Task` for `/quenching:components:align`'s doctrine audit — `sk-unscoped-bash` 8 → 5, every survivor stating
  its reason. `/docs/standards/automation/hooks.md` graduated to `authority: current` on that
  adopting surface; `agents.md` stayed `background` because there is no `.claude/agents/` anywhere
  to follow it. A proposed `components package` verb was **dismissed on a real packaging run**: four mechanical
  operations, then six fields that came back requiring a human. Still twenty-four commands.

## 1.0.0

**the middle front went fully native — the external OpenSpec CLI is gone.** The
  `openspec/` workspace this plugin used to *drive* (`@fission-ai/openspec`, `openspec init`,
  `config.yaml`, a main-spec store, delta specs) is replaced by a **native `specs` front** the
  plugin owns end to end. There is **no `npm i -g`, no Node prerequisite, no delta format**: the
  deterministic rails are the new bundled stdlib **`assets/bin/cq specs`**
  (`new`/`list`/`status`/`next`/`task`/`backlog`/`validate`/`archive`/`doctor`, uniform `--json`,
  exit codes `0`/`1`/`2`), the second self-contained tool beside `cq knowledge validate`, installed by
  the specs-front align into a target's `.claude/hooks/`. The **unit of work is a plan**
  (`/.specs/<plan-name>/`: `proposal.md`, `design.md`, `tasks.md`, `.specs.json`), not an
  "OpenSpec change" — and because a plan writes its durable rule **straight into
  `/docs/standards/`**, honestly `authority`-graded, there is nothing to sync: isolation-while-building
  is a real git **branch or worktree** (offered by `/specs:apply`), not a markdown delta. The
  `specs`-front conductor pipeline drops to **3 stages** (align → plan-archive → backlog-triage) —
  the old sync stage and `openspec-sync-specs` skill are **removed**. Commands moved from `/opsx:*`
  to **`/quenching:specs:*`** (plan skills under `/quenching:specs:develop`, inbox under `/specs:capture`), the inbox
  from `openspec/backlog/` to **`/.specs/backlog/`**, and every finding code from `os-*` to `sp-*`.
  All twenty-seven skills now share **one `quenching-<front>-<object>-<verb>` taxonomy** — no
  separate `openspec-*` family, no `metadata.generatedBy` anywhere. New
  **`/specs:from-claude`** turns a `~/.claude/plans/*.md`
  file into an archivable plan so ad-hoc work gains the archive-time distillation. That align
  **migrates a legacy `openspec/` workspace one-way** (flatten, fold main specs into
  `/docs/standards/`, drop `config.yaml`/deltas, clear the CLI shadow copies) — interop with the
  external CLI is lost by design. Still **twenty-seven** skills; the skill↔wrapper bijection holds
  at 27↔27.

## 0.19.0

**the `openspec/` front's lifecycle closed, and the sweep contract given one
  owner.** Two new quenching-native skills complete the front. **`/quenching:specs:status`**
  is its only read-only view — changes with progress and state, the backlog by
  priority, the three verifier results, split into what the specs-front align would fix, what
  `/specs:align-and-update` would drive, and what neither closes; it reports in the sweep's own
  `os-*` vocabulary, so it is an honest dry run of the sweep you are about to authorize.
  **`/specs:archive`** is the exit `archive-change` could not give: a
  change that will **not** be built is archived with an `ABANDONED.md` and **no spec sync**, its
  seed backlog task is offered back (untriaged), and the harvest is capped at
  `authority: background`. That closes the one real hole in the task lifecycle — `/quenching:specs:develop`
  retires a seed task at **apply-ready** (*developed*, not *done*), so a change dropped afterwards
  used to leave the archive/ record claiming work that no longer existed; that state now has a
  name (`os-ledger-orphan`, with `os-ledger-in-flight` for its healthy sibling) and a command that
  prevents it. Abandonment is never inferred: no sweep and no conductor may invoke it, at any
  authorization level.
  **Redundancy removed.** The three aligns' shared doctrine — convergence over accommodation, one
  plan → one OK with code-coupled items gating individually, the cycle-authorized narration
  exception, blast radius, MERGE-never-clobber, never-delete-on-a-guess,
  align-conformance-report-the-cycle — now lives once in
  [`align/sweep-doctrine.md`](assets/references/align/sweep-doctrine.md),
  and each align states only its own front's deltas. The `openspec/` ↔ `/docs/` boundary is
  declared normatively once, in the specs-develop skill's `openspec.md` §Boundary (retired along
  with `openspec/` support itself in 1.0.0). The backlog's
  prose "self-check" is gone: `cq knowledge validate` gained **`--listing-root`** and now checks
  `openspec/backlog/` for real (`type: task` is also exempted from the `resource` recommendation,
  since the mold omits it on purpose) — the same checker that guards `/docs/`, pointed at a tree
  the bundle root never covers.
  **Performance.** `/specs:align-and-update` hands its assessment inventory down to
  the specs-front align instead of making it re-collect against an untouched disk (a pass paid for
  `doctor`/`validate`/`list --json` three times); `status --json` is scoped to full-progress
  changes rather than run per active change; the rename blast-radius sweep is **two** repo scans
  for the whole set instead of two per rename; `/specs:archive` invokes
  `openspec-sync-specs` directly via `Skill` with the delta analysis it already built, instead of
  spending a `general-purpose` sub-agent to re-derive it; and the task-capture hot path drops the
  glossary tail step, which was an expected no-op costing two bundle reads on a path whose whole
  contract is "seconds".
  **Defects fixed.** Eleven references to three commands that do not exist (`/opsx:implement`,
  `/opsx:archive`, `/opsx:revise` — CLI names that survived the adaptation) now point at the real
  wrappers. Six skills instructed tools their `allowed-tools` did not grant (`AskUserQuestion`,
  `TodoWrite`, `Task`/`Skill` in archive, `Bash` in both backlog skills). The two backlog
  descriptions said "OKF backlog", contradicting every other statement that the inbox is outside
  the bundle.
  **The documentation site got an owner.** New **`quenching-knowledge-documentation-build`**
  (`/quenching:knowledge:documentation:build`) owns the mkdocs-material **site layer** over the `documentation/`
  home end to end: install, config **merge** (missing required keys only, shown as a diff),
  `.pages` nav regeneration as sections come and go, `site/` gitignore, the opt-in Pages workflow,
  and a real `mkdocs build --strict` verification that says `unverified` rather than lying. Until
  now that layer was stamped **once** by `quenching-knowledge-align` step 7 and then drifted with no command
  to fix it: a section added later had no `.pages`, and a customized `mkdocs.yml` had nowhere to be
  merged forward. The new skill touches the **site layer only** — page-level drift is reported with
  the command that fixes it, never repaired — and align's step 7 now names it as the owner it hands
  off to. It is an on-demand tool, deliberately **not** a stage of `quenching-knowledge-align-and-update`'s
  loop (like `quenching-knowledge-import`): a site build is a publishing act, not part of reaching an OKF
  fixpoint. Twenty-four skills → **twenty-seven** (fifteen `quenching-*` + twelve `openspec-*`);
  the skill↔wrapper bijection holds at 27↔27.

## 0.18.0

**the interface completed — one 2×4 matrix, and `converge` renamed.** 0.17.0 gave
  every front an `align`; this release gives every front an **`align-and-update`** and renames
  the concept so it says what it does. `quenching-converge` → **`quenching-knowledge-align-and-update`**
  (`knowledge:converge` → `knowledge:align-and-update`, both retired since) — clean cut, no compatibility alias. New
  **`specs:align-and-update`** (retired since) drives the cycle actions
  the specs-front align only reports: align → archive each complete change (syncing specs and
  distilling into `/docs/`) → sync leftover deltas → triage the inbox, looped; **each archive
  confirms on its own**. New **`quenching-components-align-and-update`** (`components:align-and-update`, retired since)
  adds the one thing the align is forbidden to do — a **read-only doctrine audit of every skill
  body**, reported with the `/quenching:components:command:new` that fixes it, never rewritten. New
  **`quenching-align-and-update-all`** (root `/align-and-update`) loops all three fronts,
  because they feed each other (an archive's distillation is glossary work; the skill front's
  registry is a `/docs/` listing). **Architectural fix:** the cycle-authorization + convergence
  contract left `quenching-converge/references/cycle.md` — where it had become misplaced, being
  cited by every conductor — for its own neutral owner,
  `quenching-align-and-update-all/references/convergence.md`; each front's `cycle.md` now holds
  only that front's pipeline and routing. The contract also grew a second never-covered class
  beside code-coupled items: **irreversible cycle actions** (an OpenSpec archive, a backlog
  removal) always gate individually, and authorization **nests one level** so the cross-front
  run still costs exactly one OK. Twenty-one skills → **twenty-four** (fourteen `quenching-*` +
  ten `openspec-*`); the skill↔wrapper bijection holds at 24↔24.

## 0.17.0

**one interface across the three fronts.** The plugin acts on three surfaces —
  `/docs/`, `openspec/`, `.claude/` — but only two had an align sweep. A new **specs-front align**
  (quenching-native) gives the `openspec/` workspace the same
  install-and-force-conformance entry point: scaffold via `openspec init`, doctor/validate,
  canonical change + archive names, the `backlog/` inbox and its derived zone, `config.yaml`'s
  `context:` thinned into a pointer at `/docs/`, and removal of the CLI-generated
  `.claude/skills/openspec-*` + `.claude/commands/opsx/` shadow copies — with cycle actions
  (archive, triage, sync, boundary smells) **reported, never driven**. Its contract lives in
  the new `specs-align/references/conformance.md`; `quenching-components-align` now explicitly
  leaves the `openspec-*`/`opsx/` surface to it. New **`quenching-align-all`** (root `/align`)
  is the second conductor: the three aligns in dependency order (`/docs/` → `openspec/` →
  `.claude/`) on **one** confirmation, orthogonal to `quenching-knowledge-align-and-update` (which loops the
  `docs` front alone to a fixpoint). The cycle-authorization contract in
  `quenching-knowledge-align-and-update/references/cycle.md` is now the shared normative home for **both**
  conductors. Nineteen skills → **twenty-one** (twelve `quenching-*` + nine `openspec-*`), and
  the skill↔wrapper bijection is preserved.

## 0.16.0

**verb-first command surface, honest namespaces.** Renamed the command wrappers
  so each names its action, and split the `quenching-*` surface by the artifact it touches.
  `opsx:` keeps its namespace and every `openspec-*` skill name (upstream alignment); only the
  commands change: `apply`→`implement`, `update`→`revise`, `sync`→`sync-specs`,
  `backlog`→`backlog-add`. The seven quenching-native `docs:` skills rename in lockstep with
  their command: `insert`→`add`, `enrich`→`import`, `knowledge`→`learn`, `glossary`→`define`,
  `knowledge-scan`→`glossary-backfill` (the name no longer lies), `memory-to-docs`→`import-memory`,
  `cycle`→`converge`. `align`/`harness` stay. A new **`skill:` namespace** carries the two
  `.claude/`-automation skills out of `docs:` — `quenching-components-command-new` → `/quenching:components:command:new`,
  `quenching-components-align` → `/quenching:components:align` (skill names unchanged, namespace honest). Clean
  cut, no compatibility aliases; the 19-skill/19-wrapper bijection is preserved.

## 0.15.0

every skill is now `user-invocable: false` (hidden from the `/` menu) and paired
  with a thin **command wrapper** — `/opsx:*` for the eight `openspec-*` skills, `/quenching:knowledge:*` for
  the eleven `quenching-*` skills; Claude still auto-routes by `description`, the wrappers are the
  explicit user entry points. **Renamed** the backlog pair into the OpenSpec family — capture
  and triage, quenching-native — they own the `openspec/backlog/` inbox and carry
  no `metadata.generatedBy`. **Removed** `quenching-visualize` and the offline HTML diagram
  generator it drove (`assets/tools/okf-visualize.py` + the vendored `viewer/` — Cytoscape.js +
  marked). Twenty skills → **nineteen** (eleven `quenching-*` + eight `openspec-*`).

## 0.14.0

added the **automation family** — `quenching-components-command-new` (mint/edit ONE
  conformant skill: single-axis classification domain-bound × generic, flattened-path
  naming, mirrored command wrapper, writing doctrine, OKF tail) and
  `quenching-components-align` (migrate the existing `.claude/skills/` + `.claude/commands/`
  surface to the taxonomy in one plan → one OK). Two OKF artifacts now maintained in
  target repos: the rule `/docs/standards/automation/skills.md` (born
  `authority: background`) and the registry `/docs/project/automation.md`
  with a GENERATED zone only the pair writes. New `assets/templates/automation/` molds
  (skill, command wrapper, registry, standard). Fourteen quenching skills → **twenty** in
  all.

## 0.13.0

straightened the work pipeline to `openspec/backlog/` (task) →
  `openspec/changes/…` (design records the decision) → `/docs/standards/` (proven rule), with no
  middle element. **Moved the backlog out of the OKF bundle** to `openspec/backlog/` — a
  quenching-managed sibling of `/.specs/`/`changes/`, no longer scanned by `cq knowledge validate`, and
  `type: task` left the OKF `type` vocabulary; `quenching-backlog`/`-triage` still own capture,
  triage, the derived index zone, and an on-write self-check (the new
  `quenching-backlog/references/backlog-zone.md` is its single owner). **Retired the standalone
  `decisions/` ADR home**: an agreed-but-unproven decision is now a `standards/` doc with
  `authority: background`, a proven one `authority: current`; a change's rationale/alternatives
  live in its `design.md` while active and distill to a `standard` at archive time.
  `migration.md` gains rules (§1e/§1f) to relocate an existing bundle's `backlog/` home → `openspec/backlog/`
  and restamp its `decisions/` ADRs into `standards/`. Still **eighteen** skills.

## 0.12.0

narrowed the OKF taxonomy from eleven homes to **nine** — retired the
  `communications/` and `presentations/` homes (and dropped the leftover empty
  `superpowers/` folder), removing the `communication`/`communication-template` types from
  the vocabulary (the `sidecar` type stays, now scoped to `reference/regulations/` extracts).
  Same release: added an optional **`complexity`** field to backlog tasks — a rough size in
  development hours, stamped only when stated (like `priority`/`tags`), surfaced as a column
  in `backlog/index.md`'s derived zone and proposable by `quenching-backlog-triage`.

## 0.11.0

absorbed the OpenSpec spec-driven cycle — six `openspec-*` skills (adapted
  from OpenSpec 1.6.0's generated skills, with OKF knowledge bridges) plus thin `/opsx`
  commands; the backlog lifecycle now seeds `/quenching:specs:develop` (the previous
  brainstorming-based flow is retired). Same release: renamed the backlog item `idea` →
  `task` (optional `priority`/`tags`; derived GENERATED zone in `backlog/index.md`;
  "Developed" → "Completed" ledger) and added `quenching-backlog` (capture) +
  `quenching-backlog-triage` (triage sweep) — ten quenching skills → twelve, eighteen in
  all.

## 0.9.0

retired the `guides/` home into `documentation/how-to/`; added the `documentation/`
  home (Diátaxis product docs) and a shippable mkdocs-material site setup (`assets/mkdocs/`).
