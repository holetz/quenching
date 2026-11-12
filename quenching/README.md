# quenching (plugin)

A team tool for the Claude Code surface of a
repository: **specs, git, knowledge and components** are its core. It carries one canonical **Open Knowledge Format (OKF v0.2)** bundle
of `/docs/` and the tools used to inspect it, force an existing base into conformance,
insert new knowledge, capture terms into a fixed glossary, drain the project's Claude
Code memory into it, import external sources into it, keep the repo's `AGENTS.md` a thin pointer over it, and organize
the repo's own **automation surface** (`.agents/skills/`) under one
taxonomy — so every repository that adopts the plugin looks the **same**. It also carries the repo's
**spec-driven plan lifecycle**: the ten `/quenching-specs` flows over a specs
front stored on a git branch with thin GitHub or Azure Boards cards, with the OKF bundle as its knowledge substrate, driven end
to end by the bundled stdlib `cq specs`.

The **design front** adds one DTCG source at `/.design/tokens.json`, deterministic projections
for Impeccable and editorial media, and a human-arbitrated import path for an Impeccable-authored
`DESIGN.md`. Impeccable remains optional and owns web craft; quenching owns the source, product
projection, genres, and non-web adapters.

**Core fronts** (maintained actively): `knowledge`, `specs`, `git` and `components`. **Non-core
fronts** (`design`, `ops`, `proof`, `toolchain`, `delivery`, `security`): human-only commands under
the same names, with reduced maintenance — defect fixes, no new features. quenching is not a
security boundary: the documentation makes no claim that an assistant cannot write through an
available shell or Python interpreter.

All of it sits behind **one interface, repeated on every front**: ONE `align` per front —
probe-first, so a clean front costs a couple of tool calls — that forces the structure into
shape and carries that front's content stages. Read the next section and you know the whole
plugin.

## The eight fronts, the non-converging axes, and the one align per front

The plugin acts on **eight** surfaces of a repository, and the interface is the **same on each**.
Eight local fronts have an align, the specs axis has no local tree to converge,
and one root command spans the eight aligned fronts. The `security` and `git` axes are
**pillars** rather than fronts — they converge no tree of their own, so they carry no align at all
(see [`architecture/align-surface.md`](../docs/standards/architecture/align-surface.md)
§The security subject is pillar-shaped and §The git pillar has no align):

| Front / pillar | Namespace | **align** — probe-first, structure + content |
| --- | --- | --- |
| `/docs/` — the OKF bundle | `/quenching-knowledge` | `/quenching-knowledge align` |
| specs — the `quenching` branch, with GitHub or Azure Boards cards | `/quenching-specs` | lifecycle and status commands |
| `/.design/` — the DTCG design source | `/quenching-design` | `/quenching-design align` |
| `.claude/` — the automation surface | `/quenching-components` | `/quenching-components align` |
| target-declared operations root | `/quenching-ops` | `/quenching-ops align` |
| target-declared verification root | `/quenching-proof` | `/quenching-proof align` |
| target-declared toolchain surface | `/quenching-toolchain` | `/quenching-toolchain align` |
| target-declared delivery surface | `/quenching-delivery` | `/quenching-delivery align` |
| license, community and governance artifacts | `/quenching-opensource` | `/quenching-opensource align` |
| *(pillar)* — read-only security questions | `/quenching-security` | **none** |
| *(pillar)* — a repository's own git facts | `/quenching-git` | **none** |
| **all eight aligned fronts** | *(root)* | **`/quenching-align`** |

**The probe comes before the inventory.** Each implemented align opens by running its front's own verifier
(`cq knowledge validate`, `cq design doctor`, `cq components doctor`/`lint`, `cq ops doctor`, `cq proof doctor`, `cq toolchain doctor`, `cq delivery doctor`, `cq opensource doctor`); a clean
probe stops with nothing to inventory, plan, or confirm. Otherwise: one read-only inventory → ONE
consolidated plan → one OK → apply → verify, then the front's content stages, each run only when
the probe found it work:

| Front | Content its align carries beyond structure |
| --- | --- |
| `docs` | drains project memory, thins the harness (moving durable knowledge into homes), and OFFERS the glossary backfill on a cheap proxy — looping to a fixpoint, the one front with a real internal loop |
| `specs` | none driven — an empty section, a complete spec awaiting its close, an unresolved discovery are each **reported with the command that owns it**; every lifecycle action needs fresh human intent |
| `/.design/` | imports or preserves an external `DESIGN.md` only after source arbitration, installs missing brand assets, builds projections, and reports optional Impeccable detector results |
| `.claude/` | audits every command **body** against the writing doctrine — the one thing the migration itself is forbidden to fix — and reports each violation with the `/quenching-components command-new` that closes it |
| `ops` | probes the declared root and router, applies mechanical and structural drift under one plan, and reports judgement findings; status is the read-only view |
| `proof` | probes the declared verification surface, applies bounded gate repairs, reports judgement findings, and keeps status read-only |
| `toolchain` | probes manifests, locks, language pins and tool configuration, applies only bounded repairs, and leaves build policy with the target owner; status is the read-only view |
| `delivery` | probes provider-equivalent workflows, reports pipeline reachability and provenance, and leaves provider, environment, promotion, publication and permission policy with the target owner; status is the read-only view |
| `opensource` | aggregates every owner's catalog answers into the baseline level, writes only the license, community and governance artifacts it owns from pinned templates, and leaves the license, maintainers, contact and funding to the owner; status is the read-only view |

The cross-front `/quenching-align` conducts the eight aligned fronts in dependency order on one nested OK and **loops
across fronts**, because they feed each other: a spec's distillation is glossary work the
`docs` front must then index; the design front installs product/design standards; the components front creates the rule and registry that the `docs`
listings must carry.

The specs axis has no sweep conductor: each spec is captured, defined, built, reviewed and closed
by the command that owns that stage. Defining and building remain separate decisions, and each
stage's own authorization and verification contract stays visible to the human.

Every entry point shares one contract: any item whose blast radius reaches **product code**
confirms on its own, always — and inside a conducted run, so does every **irreversible close**.
That contract lives once, in
[`align/convergence.md`](references/align/convergence.md).

## The 13 skills

**One folder per skill** — each `skills/<name>/SKILL.md` carries both the description that routes to
it and the body that runs. A front router (`quenching-specs`, `quenching-git`, `quenching-knowledge`,
`quenching-components`, and the non-core `quenching-design`, `quenching-ops`, `quenching-proof`,
`quenching-toolchain`, `quenching-delivery`, `quenching-security`, `quenching-opensource`) keeps its flows in its own `references/`, so its rows below are flows, not
extra skills. The tables below are the manual, and the count is a property of their rows rather than a
second structural inventory: the `13` in this heading is the manual's canonical displayed total, while
[`tests/test_readme_surface.py`](tests/test_readme_surface.py) reads it and fails the suite whenever
these tables and `skills/**` disagree
([`quality/surface-verification.md`](../docs/standards/quality/surface-verification.md)
§A hand-written inventory of the surface needs a machine holding its lockstep).

**The listing cost.** All thirteen descriptions are resident in every session, so the descriptions are
the always-on cost of the plugin. Each router's description is a map of intent per flow with pt-BR and
English triggers, at most 1,024 characters (the Agent Skills limit Codex and OpenCode read; Claude's own
cap is 1,536). Today the thirteen total about 6.4 thousand characters (about 1.6 thousand tokens); the
ceiling is 13 × 1,024 = 13.3 thousand characters (about 3.3 thousand tokens). Before the non-core fronts
had routers, the six resident descriptions were about 1.4 thousand characters.

The split is by front and pillar: `/quenching-knowledge` acts on the OKF `/docs/` bundle,
`/quenching-specs` on the specs branch and its cards, `/quenching-design` on the DTCG
source and its projections, `/quenching-components` on the target's `.claude/` automation surface,
`/quenching-ops` on the target's operations surface, `/quenching-proof` on the target's verification surface, `/quenching-toolchain` on the target's toolchain surface, `/quenching-delivery` on the target's delivery surface, `/quenching-opensource` on its license, community and governance artifacts, and `/quenching-git-*` on a repository's own git facts. Two commands sit at the root. Claude auto-routes to a command by its `description`; typing the command is
the explicit entry point.

### The `knowledge` front — the OKF `/docs/` bundle

| Command | Does |
| --- | --- |
| `/quenching-knowledge` | The single entry point of the knowledge flows: picks one of the thirteen flows (add, align, define, learn, import, import-memory, glossary-backfill, status, documentation build, plan, produce, review, write) by the flow you name and loads that flow's reference; no alias entry stands for a flow. |
| `/quenching-knowledge align` | Forces `/docs/` into the canonical OKF bundle and pulls in the content sitting out-of-band — probe first, then ONE confirmed plan, looped to a fixpoint. |
| `/quenching-knowledge status` | The front's only **read-only** view: where the bundle stands, what is conformant, what drifted. Writes nothing. |
| `/quenching-knowledge add` | Inserts ONE concept doc — right home, right type, honest stamp. |
| `/quenching-knowledge learn` | Captures ONE piece of generic understanding into `concepts/`, for what is true beyond this repo. |
| `/quenching-knowledge define` | Adds or refines ONE entry in the fixed glossary. |
| `/quenching-knowledge glossary-backfill` | Sweeps the whole bundle for terms nobody ever defined, and backfills them. |
| `/quenching-knowledge import` | Imports an external source — files, folders, URLs — into the bundle as many docs, with provenance. |
| `/quenching-knowledge import-memory` | Drains the project's Claude Code memory into the bundle, then clears it. |
| `/quenching-knowledge documentation-produce` | Conducts the whole documentation pipeline: site layer, sourced pages, bounded review, strict-build QA. |
| `/quenching-knowledge documentation-plan` | Builds the sourced architecture — reader journeys and the output contracts each page answers to. |
| `/quenching-knowledge documentation-write` | Writes the Diátaxis pages from that plan, sourced and never invented. |
| `/quenching-knowledge documentation-review` | Scores pages against the eleven-dimension quality gate **without changing a byte**. |
| `/quenching-knowledge documentation-build` | Owns the Zensical site layer — extensions, CSS, nav, and the strict build. |

### The `design` front — the `/.design/` DTCG source and projections

| Command | Does |
| --- | --- |
| `/quenching-design` | The single entry point of the design flows: picks `align`, `status`, `genre-new` by the flow you name or by the words of the request. |
| `/quenching-design align` | Installs or converges the brand pack, preserves source truth, arbitrates external DESIGN.md proposals, and rebuilds every projection. |
| `/quenching-design status` | Reports DTCG validity, generated identity, sidecar/assets, genres, adapters, and optional Impeccable detector state without writing. |
| `/quenching-design genre-new` | Mints ONE editorial genre contract with fields, register, and HTML/Typst/PDF destinations. |

`cq design build` and `cq design import` are the deterministic rails used by these commands. The
source is DTCG 2025.10; `DESIGN.md` is a deliberately lossy portable projection, while rich
motion, shadows, breakpoints, and snippets remain in the source and sidecar.

### The `components` front — the target's `.claude/` surface

| Command | Does |
| --- | --- |
| `/quenching-components` | The single entry point of the components flows: picks `command-new`, `agent-new`, `hook-new`, `align`, `status` or `harness-align` by the flow you name and loads that flow's reference; no alias entry stands for a flow. |
| `/quenching-components align` | Converges the whole `.claude/` surface onto one file per entry point, then audits every body and rewrites every description against the writing doctrine. |
| `/quenching-components status` | Reports the command count, fronts and finding codes for the target's automation surface without writing. |
| `/quenching-components command-new` | Mints or edits ONE command — the structural half, including its `description`. |
| `/quenching-components command-eval` | Measures whether a command actually teaches anything: with/without runs, graded on evidence rather than on how the body reads. |
| `/quenching-components command-retro` | Mines ONE session for what it evidences about ONE command that ran in it — cost, redundancy, bugs, and what the human had to fix by hand. |
| `/quenching-components agent-new` | Mints or edits ONE subagent definition, scoping its tools to the narrowest set and pricing its always-on cost. |
| `/quenching-components hook-new` | Wires ONE scoped hook — the narrowest scope and cheapest handler that still catch what they must. Warns by default; blocks only on the human's word. |
| `/quenching-components harness-align` | Refactors `AGENTS.md` into a thin pointer over the bundle, so doctrine lives once; legacy `CLAUDE.md` is removed. |

### The ops front — the target's declared operations surface

| Command | Does |
| --- | --- |
| `/quenching-ops` | The single entry point of the ops flows: picks `align`, `status`, `entrypoint-new` by the flow you name or by the words of the request. |
| `/quenching-ops align` | Probes the declared operations root and router, applies mechanical and structural drift under one plan, and reports judgement findings without driving them. |
| `/quenching-ops status` | Reports the root, router, packages, lifecycle, findings by band, and registry freshness without writing. |
| `/quenching-ops entrypoint-new` | Mints ONE Python entry point from the contract, registers it in the declared router, and regenerates the operations registry. |

### The proof front — the target's declared verification surface

| Command | Does |
| --- | --- |
| `/quenching-proof` | The single entry point of the proof flows: picks `align`, `status`, `layer-new` by the flow you name or by the words of the request. |
| `/quenching-proof align` | Probes the proof gate, applies mechanical and bounded structural repairs under one plan, defers a floor when the measured surface changes, and reports judgement findings without driving them. |
| `/quenching-proof status` | Reports layers, fixtures, measured roots, floors, CI evidence, findings by band, and the explicit fact that the suite was not run — without writing. |
| `/quenching-proof layer-new` | Mints one named layer with its marker, reach, budget, fixture home and collection rule, then proposes test moves for a separate confirmation. |

### The toolchain front — manifests, locks, pins and tool configuration

| Command | Does |
| --- | --- |
| `/quenching-toolchain` | The single entry point of the toolchain flows: picks `align`, `status` by the flow you name or by the words of the request. |
| `/quenching-toolchain align` | Probes applicability, inventories the target's toolchain artifacts, applies only mechanical and bounded structural repairs, and reports target-owned build policy. |
| `/quenching-toolchain status` | Reports applicability, manifests, locks, language pins, tool configuration and `tc-*` findings without writing. |

### The delivery front — workflows, reachability and release shape

| Command | Does |
| --- | --- |
| `/quenching-delivery` | The single entry point of the delivery flows: picks `align`, `status` by the flow you name or by the words of the request. |
| `/quenching-delivery align` | Probes provider-equivalent workflows, applies bounded pipeline-shape repairs under one plan, and reports provider and release policy without choosing it. |
| `/quenching-delivery status` | Reports applicability, workflow inventory, reachability, provenance and `delivery-*` findings without writing or running a pipeline. |

### The opensource front — license, community and governance artifacts

| Command | Does |
| --- | --- |
| `/quenching-opensource` | The single entry point of the opensource flows: picks `align`, `status`, `readiness` by the flow you name or by the words of the request. |
| `/quenching-opensource align` | Probes applicability, plans the license, contributing, conduct, support, governance, owners and template artifacts on one OK, and writes each through `cq opensource apply` from a pinned template, never choosing the owner's license, maintainers, contact or funding. |
| `/quenching-opensource status` | Reports every owner's catalog answers, the OSPS baseline level reached and `os-*` findings without writing. |
| `/quenching-opensource readiness` | Assesses secrets in tree and history, internal identifiers, attribution and the owner's license and consent evidence before a repository goes public, read-only; reports blockers, warnings and unmeasured coverage and never approves publication. |

### The security pillar — read-only repository security questions

| Command | Does |
| --- | --- |
| `/quenching-security` | The single entry point of the security flows: picks `status` by the flow you name or by the words of the request. |
| `/quenching-security status` | Reports security questions and ownership findings without aligning, repairing or writing repository values. |

### The `git` pillar — a repository's own git facts

| Command | Does |
| --- | --- |
| `/quenching-git` | The single entry point of the git flows: picks `branch`, `commit`, `merge`, `sync`, `pr-create`, `pr-review` or `pr-status` by the flow you name and loads that flow's reference; no alias entry stands for a flow. |
| `/quenching-git branch` | Takes isolation for a build: a worktree by default and unasked, a plain branch only when the human asks, stating the cost and stamping the `branch:` record. |
| `/quenching-git commit` | Commits what is already staged, under the target's own convention when one is declared. Never `git add -A`. |
| `/quenching-git commit-incremental` | Turns the current worktree's pending changes into cohesive commits with explicit paths and safe stop conditions. |
| `/quenching-git push` | Publishes one branch to an exact remote and refspec after measuring preconditions and receiving confirmation, without force or PR side effects. |
| `/quenching-git revert` | Creates a compensating commit for one known target after showing its effect and requiring an explicit mainline for merges, without rewriting history. |
| `/quenching-git pr-create` | Pushes and opens a pull request, with `Closes #<n>` when an issue is named, reporting plainly whether that keyword will actually close it. The word `autonomous` (accepted by `pr:create`, `conclude`, `spec-runner` and `spec-orchestrator`) is the conductor's pre-answer to its confirmation: the PR is published without asking, by the `spec-orchestrator`, after the `spec-verifier` PASS. |
| `/quenching-git pr-status` | Reports one read-only snapshot of a pull request's provider state, checks, reviews, threads and mergeability, preserving unknown causes. |
| `/quenching-git merge` | Merges a branch home on one of four strategies, offered and never chosen for the human. |
| `/quenching-git sync` | Rebases a work branch onto the latest base, with `--update-refs` so a stacked branch is not orphaned. |
| `/quenching-git cleanup` | Prunes branches merged or gone and worktrees git still registers with no directory on disk — nothing pruned the human did not pick from that report. |
| `/quenching-git pr-review` | Works through a PR's unresolved review threads, one confirmation per thread. |

**The one plugin-wide hook.** `quenching-specs` ships `hooks/hooks.json`: a `PreToolUse` hook on
`Bash` that **denies** any `git commit`/`merge`/`tag`/`notes`, `gh pr` or `cq git` command whose
message carries Claude's co-authorship (`Co-Authored-By: Claude …`, `noreply@anthropic.com`,
`Generated with Claude Code`), so Claude reruns it without the attribution. It never rewrites the
command (`updatedInput` only applies paired with `allow`, which would auto-approve whatever the
command chains), fails open without `python3`, and is off when `QUENCHING_ALLOW_CLAUDE_COAUTHOR=1`.
Pair it with `"attribution": {"commit": "", "pr": ""}` in the target's settings so the trailer is
never written in the first place.

The `security` and `git` pillars carry no `align`: they converge no tree, only answer read-only
questions about the target's live evidence, so there is nothing a probe could find drifted
([`architecture/align-surface.md`](../docs/standards/architecture/align-surface.md) §The
security subject is pillar-shaped and §The git pillar has no align). The `specs` axis hands off to
the git pillar rather than executing git
itself — `/quenching-specs execute` invokes `/quenching-git branch` for isolation, and
`/quenching-specs conclude` reviews, distils, archives, sweeps its own flow — each defect of the
project's automation becomes its own captured spec, never a task of this one — and proves the
pre-merge gate green, then
**names** `/quenching-git pr-create` or `/quenching-git merge` as the human's own next command
instead of running either.

### The two root commands

| Command | Does |
| --- | --- |
| `/quenching-align` | The one align that spans the eight aligned fronts, on ONE confirmation — conducting each front's own align in dependency order, never reimplementing any of them. |
| `/quenching-handoff` | Compacts the current conversation into a handoff stored beside its spec on the `quenching` branch, pushes it, and closes with the locator, the read command and the prompt the next session starts from — referencing existing plans, issues, commits and diffs rather than duplicating them. |

The `specs` front has ten commands and a flow worth reading as a whole, so it gets its own section
below.

## The `specs` flow — the ten `/quenching-specs` flows

The plugin's **spec-driven plan cycle** keeps each spec as a canonical document on the `quenching`
branch of the code repository's remote (`"backend": "git"`), with a thin GitHub or Azure Boards
**card** beside it as the human-facing projection. The conceptual model (thirteen sections, seven
frontmatter records, derived stages) is identical on every backend, which is why every command
drives `assets/bin/cq specs` (uniform `--json`, strict exit codes `0` ok · `1` findings · `2`
refusal) rather than a repository path. The `github` and `azure-boards` backends, which keep the
document in the tracker item, still work but are deprecated: `cq specs doctor` flags them and
`cq specs migrate --to git` (a dry run unless `--write`) moves a repository onto the branch. Every
command on this front reads the `/docs/` bundle as context going in and distils durable
knowledge back out when a spec closes.

The **unit of work is a spec** — ONE canonical markdown document for its whole lifecycle. It is
`specs/<id>.md` on the branch (`specs/archive/<id>.md` once closed), written without a checkout into
ONE local pending commit and sent only at sync points (`cq specs new`, archive and restore,
`cq git push`, `cq git pr create|merge`, `cq specs push`): each sync replaces the branch with one
parentless commit under `--force-with-lease`, so concurrent writes to different specs both land and
the branch always holds a single commit. `cq specs status` lists the specs with unsent local
writes. The card holds a
title, a summary, `Tasks n/N`, the phase and stage, a link to the file and the `spec:*` labels, is
rewritten only at lifecycle transitions, and never holds the plan; `card: github | azure-boards |
none` configures it, and `cq specs new --card <n>` adopts an existing issue. **Frontmatter records human judgments** (`priority`, `refined`,
`approved`, `branch`, `reviewed`, `merge`, `outcome`); the store, git and section state record
everything else — `ready` is a *derived* stage, and the OK to build is the
`approved: {date, by}` stamp, where `by` is `human`, `session`, `orchestrator-forced` or the historical `low-gear`. Four more frontmatter keys — `tags`, `assignee`, `start`, `target` — are
**state, never records**: first-level frontmatter keys (a deprecated tracker backend stores them
natively instead). A fifth key, `summary:`, is neither a record nor one of those four — one line
saying what the spec is, written at capture and refreshed by every
`/quenching-specs develop` pass, and it is what
`cq specs next --front --table` prints as its `Summary` column. `.agents/quenching.json` (or the legacy `.claude/quenching.json`) is where a target declares
`backend`, the `card`, the Azure placement (`azureStates`, `azurePlacement`, `azureColumns`) and the
project's own `subjects`/`tagCatalog` — the closed sets `/quenching-specs create` proposes a spec's subject
and tags from, confirmed by a human, never picked silently. Because a spec writes its durable rule
**directly into `/docs/standards/`** (honestly `authority`-graded), there is no second store to
bridge to:
isolation-while-building is a real git **branch or worktree** (offered inline by `/quenching-specs execute`
when it starts from the base branch, recorded as `branch: {base, work}`, each task committed alone
with its sha on the task line; step 5g never writes `origin/HEAD` and aims a declared security-review hook at the work checkout's `origin/<base>...HEAD` diff, so the review sees the worktree and not the base). `cq specs export --spec <slug> | --all` dumps the canonical markdown to disk on demand —
write-only, nothing reads it back, so it is never a second store.
`cq specs serve [--port N] [--host 127.0.0.1] [--read-only] [--open] [--sessions] [--chat] [--chat-budget-usd N]` starts the local spec portal (loopback only, a per-run token on every call, `Host`/`Origin` validated; writes go through the CLI's own verbs, so CAS and refusals are the CLI's, and a refusal is shown with its code). `--sessions`, off by default, adds `GET /api/sessions` and the board's Sessions view: the live Claude Code sessions of this repository's worktrees, fixed fields only. `--chat`, off by default, adds `POST /api/chat` and `GET /api/chat/<job>` and the Chat tab: a question answered by one read-only `claude -p` (`Read`/`Grep`/`Glob` only, secrets denied, hooks off) in a worktree of the project, polled by the page, capped by `--chat-budget-usd` (default `0.50`) and a 300 s timeout; it needs `claude` on `PATH`. `/quenching-specs board` launches it.

`cq config show --effective [--json]` prints every configuration key with its effective value and the layer it came from (`default`, `user`, `repository`, `branch`), plus the path and state of each layer; it only reads.

`cq config init [--write]` seeds `.agents/quenching.json` with every adjustable default spelled out (preview without `--write`; an existing file is refused, never merged), and `cq config check [--json]` lists the seeded keys the file lacks (exit 1). `cq doctor` prints the same list in a `config` block and only reports it; `/quenching-align` runs the check and seeds an absent file under its one authorization.

The repository layer is read through a configuration provider. `file` is the default and the compatibility read: with nothing declared, every value, refusal and `cq config show --effective` row is what it was, `.agents/quenching.json` included (and the legacy `.claude/quenching.json`). `QUENCHING_CONFIG_PROVIDER=<name>` (read from the environment, never from the file) selects another registered provider; a name nothing answers to is a refusal (exit 2) naming the registered providers, never a fallback to the file. Under a non-file provider the repository needs no `.agents/quenching.json`, `cq doctor` stops asking for it, `cq config show --effective` names the provider as the repository layer's source, and `cq config init` and `cq config check` refuse, because a write the provider did not receive would be a silent divergence. `cq config export [--json]` prints the repository layer as the envelope a service would hold, so the file can be loaded there and then deleted; it only reads. No service provider ships yet: this release delivers the seam.

### Azure Boards sync — a local cache kept in step by service hooks

With `QUENCHING_SPECS_SYNC=1` and the `azure-boards` backend, every read is answered from a per-machine cache and every write still goes through the adapter. It is off by default and wraps no other backend. The cache is not a store: Azure Boards stays the source of truth, and deleting the cache loses nothing.

- **Cache location.** `<user cache dir>/quenching/azure-sync/<hash of org and project>/` (`$XDG_CACHE_HOME` or `~/.cache`), one JSON file per work item plus `meta.json`, outside the repository. No credential is stored.
- **Staleness.** Each entry carries the `rev` it was read at. A service-hook event or a reconciliation that names a higher `rev` marks it stale and the next read refetches it. Without a receiver, the staleness bound is `QUENCHING_SYNC_RECONCILE_S` (default `300` seconds): a read past it reconciles first. With a receiver, a change is seen on the next read after the event arrives. A write based on a stale read is refused by the adapter's `rev` test, never applied.
- **Verbs.** `cq specs sync status` (path, items, stale count, last reconciliation), `cq specs sync reconcile` (diff every id and `rev` against Azure, refetch what changed, drop what left), `cq specs sync apply` (one service-hook event on stdin, for any receiver that is not ours) and `cq specs sync serve [--host 127.0.0.1] [--port N]`.
- **Receiver.** `cq specs sync serve` listens on loopback only (any other host is refused) at `POST /hooks/azure`, reconciles in the background every `QUENCHING_SYNC_RECONCILE_S`, and answers `401` without the secret, `405` off POST, `400` for an unreadable event, `413` past 1 MiB. Reaching it from Azure DevOps (a tunnel, a reverse proxy) is the operator's.
- **Hook payload and secret.** Create a service hook for `Work item created`, `updated`, `deleted` and `restored` with the Web Hooks consumer, basic authentication (any user name; the password is the secret), resource details `All`. The server reads the secret from `QUENCHING_SYNC_HOOK_SECRET` in its environment: it is never an argument, never logged and compared in constant time. The event is read as `resource.workItemId` (updated) or `resource.id`, and `resource.rev` or `resource.revision.rev`; the shape follows the public documentation and the first real delivery is yours to check.

`cq portal serve [--port N] [--host 127.0.0.1] [--read-only] [--open] [--sessions] [--chat] [--chat-budget-usd N]` serves every project registered with `cq portal add` from one loopback server: the page gains a side menu of projects and their worktrees, each project's API lives under `/p/<name>/api/`, and one token cookie covers them all; with `--chat` the Chat tab offers that project's worktrees. `cq specs serve` is unchanged.

| Command | Role |
| --- | --- |
| `/quenching-specs` | The single entry point of the specs flows: picks `create`, `develop`, `execute`, `conclude`, `triage`, `status` or `orchestrate` by the flow you name or the spec's stage, and loads that flow's reference. No alias entry stands for a flow. |
| `/quenching-specs status` | The front's only **read-only** view: specs by derived stage with task progress, the frontmatter records as the history they narrate, the verifier results, and provider configuration findings. |
| `/quenching-specs create` | ONE spec in `plans/`, ONE call, ONE closing screen — effort proportional to input, never an interrogation. A sentence becomes `## Problem` and `summary:`; a Claude Code plan file becomes every section it actually supports, mapped and never invented. Subject, type, tags and `complexity` are resolved and written with the capture, then shown — corrected or not — on the one screen at the end, which also offers to hand straight into `/quenching-specs develop` — whether that pass asks anything is the `complexity` the same screen shows. |
| `/quenching-specs develop` | Two operations in ONE pass, both derived and neither offered as a choice: **compose** takes the spec from wherever its derived stage leaves it to a closed ten-section ready set, and **refine** argues with the composed spec and may overturn anything in it, the proposal included. Discovery resolution opens the pass, the approval close ends it — recommending approve, refine, or refine with the premortem against the spec's own signals. Questions grouped by dependency, each with an inline recommendation; one edit per pass, records `refined:`. Never edits code. |
| `/quenching-specs execute` | Builds `## Tasks` one verified commit at a time: clean tree required, a worktree taken inline when it starts from the base branch, `verify:` run under the spec's declared policy, four-item diff self-review, then the box ticked with the subject of the commit it is about to make (`cq specs task --check --subject`) so code and box land in ONE commit. Writes only the `/docs/standards/` a task explicitly names; everything else is one `cq specs discover` line. Marks an isolated branch's own description with the slug(s) it built there — never on the base — so `conclude` can self-discover it later. Stops at the last commit. |
| `/quenching-specs conclude` | Closes a spec out, resumable, **merging last**: whole-branch review (`reviewed:`), the emergent `/docs/`, the archive with `outcome: done` (refuses on open boxes unless forced) or `abandoned` (always allowed), ONE distillation pass, the flow sweep that captures each defect of the project's own automation as its own spec — never developed in this run —, the release obligations your standards attach to the merge itself (a version bump, a changelog entry — never a spec task) and the `merge: {strategy, subject, pr}` stamp — all on the work branch — and only then the merge, by the **route** you chose alongside the strategy: local, or a pull request where `gh` resolves the repo (pushed, opened and merged in one consented block, with `pr:` recorded). Called with no `--spec`, reads the branch's own marking first — one valid slug resolves silently, several ask, none falls to a diff-measured offer to materialize a minimal spec — before falling back to a plain list-and-ask. Nothing is committed to the base after it. |
| `/quenching-specs improve` | **Typed only.** Maps a repository's genuinely relevant improvement opportunities with read-only scouts (evidence, consequence, no duplicate of an open spec, at most 15), settles the owner's decisions in rounds (the epic's autonomy policy among them, written into its `## Design`), and turns the approved part of the plan into an epic with member specs. Never builds. |
| `/quenching-specs orchestrate` | Launches the `spec-orchestrator` agent over an epic id or a list of spec ids: dependency waves, at most 3 workers, a result accepted only on a `spec-verifier` PASS. A pre-check separates the specs that run alone from those that need a human (develop now, launch the independent subset, or `--autonomous`, which stamps `by=orchestrator-forced`); without `--autonomous` a `medium`+ spec with no `approved` comes back `blocked` as `needs-approval`. A thin launcher; the protocol lives in `agents/spec-orchestrator.md`. A spec is accepted as done only when archived with an Outcome, and a worker `blocked` with a `needs-human:` note is never re-spawned: its question goes to the human. |
| `/quenching-specs autopilot` | **Typed only.** The invocation is the human's delegation for an unattended run: rounds of health, queue (each loose spec proves relevance or is abandoned with evidence), the `/quenching-specs improve` map decided by the conductor as delegated owner, an epic with the dated autonomy policy in its `## Design`, the `spec-orchestrator` with `autonomous`, a read-only correctness review per epic, run in parallel with a Codex review when the quota allows (fallback reported, `codex`-only findings kept only once reproduced), whose reproduced findings become next-round specs, then the gate. Never forces a decision that widens a grant or an executing surface — those go to a human epic. Runs ONE round by default; `--until-dry` or `--until` repeat rounds (a resumable round record, the next round in a fresh context) until the deadline or a whole round produces no spec with evidence and consequence, and `--max-launches` (provisional 40) caps the launches of the whole tree. |
| `/quenching-specs triage` | Ranks the whole front in ONE confirmed table, writing `priority: {level, criticality, complexity, date}` per spec and nothing else — merging, never clobbering a human's ranking. |
| `/quenching-specs board` | Human-only. Starts `cq specs serve` in the background and prints the URL: a local browser portal (board by derived stage, drag-to-rank list, spec detail, search, capture, approve as `by: human`) over the same backend as the CLI. Loopback only, per-run token, `Host`/`Origin` checks, `--read-only` disables writes on the server; `cq-specs-read serve` is always read-only. |

### The quenching MCP server — the CLI catalog and references

`cq mcp` starts the stdio `quenching` server. The Claude Code plugin registers it from its own
`.mcp.json`; a deployed target instead gets the file generated by `cq deploy` when it declares
`shared.mcp`; a harness that reads neither manifest launches `cq mcp` itself.
It exposes a closed catalog of available CLI verbs, including the specs tools below. Tool names
follow `<pillar>_<verb>[_<subverb>]` (`components_read`, `git_pr_create`); `tools/list` reports
which are available. Schemas come from each verb's parser. An absent pillar contributes no tool.
The `read`, `write` and `external` classes describe effects through MCP annotations, without
adding grants. The workspace is the launch cwd or launch-time `--root`, never a tool argument.

Run a released version without installing the plugin manually:

```bash
uvx --from "git+https://github.com/holetz/quenching@<tag>#subdirectory=quenching" quenching-mcp
```

Replace `<tag>` with a published release tag. The same package exposes `cq` as a console script;
its runtime uses only the Python standard library (Python 3.11+). The wheel preserves the plugin's
asset layout under `quenching_plugin/`. Packaging a local committed HEAD can be checked with
`bash quenching/assets/checks/functional-checks.sh --mcp-smoke`; exit 2 is inconclusive.

`quenching://references` lists the shipped reference documents; read one with
`quenching://references/<path>.md`, or select headings with `?section=<heading>`. Large documents
return outlines, and the shared response guard bounds the result. The specs resources below
remain available. The architectural contract is
[mcp-server.md](../docs/standards/architecture/mcp-server.md).

### The specs MCP server — reads, writes and gated moves, stdio

`cq specs mcp` remains the specs-only stdio MCP server (JSON-RPC 2.0, stdlib only).
Its tools also appear in the full `quenching` server above. Every tool
dispatches in-process through the same core as `cq specs`, so the backend, refusals and exit codes are the
CLI's; the server holds no store logic.

| Tool | Arguments | Answers |
|---|---|---|
| `specs_list` | `limit` (default 50, max 200), `offset` | the lean listing, paged (`count`, `returned`, `nextOffset`) |
| `specs_status` | `spec` | one spec's sections, stage, tasks and gates |
| `specs_show` | `spec`, `tasks` (ids, at most 20) | the map, or only the named tasks |
| `specs_section` | `spec`, `headings` or `moment`, `scope` | the named sections only |
| `specs_next` | `spec` or `epic` (neither: the ranked front), `limit` | the next action, the epic's ready members, or the front, paged |
| `specs_epic_progress` | `epic` | one epic's progress |

Write tools run the same CLI verbs, in the same process, and add no store logic:

| Tool | Arguments | Does |
|---|---|---|
| `specs_create` | `name`, `title`, `type`, `tags`, `complexity`, `verification` | captures a spec into `plans/` |
| `specs_section_write` | `spec`, `heading`, `body`, `scope` | replaces ONE section (body up to 200,000 characters) |
| `specs_record` | `spec`, `name`, `fields` | merges fields into a record; only `approved` is gated |
| `specs_task` | `spec`, `action` (check, uncheck, block, descope), `task`, `reason`, `subject`, `commit` | moves one checkbox |
| `specs_epic_add` | `epic`, `spec`, `after`, `group`, `label`, `move` | lists a spec as an epic item |
| `specs_discover` | `spec`, `text` | appends one line to `## Discoveries` |
| `specs_promote` | `spec`, `to`, `outcome` | moves between `plans/` and `archive/`, stamping the outcome; never forced |

One human decision, asked once: `approved` is the only gated write. The server asks the human
through the client (MCP `elicitation/create`) and runs the verb only on an accept — no argument
confirms anything, a client without the `elicitation` capability gets
`mcp-confirmation-unavailable`, a decline or cancel gets `mcp-confirmation-refused`, and nothing
changes. `approved` takes no fields: the server writes `date` and `by=human` after the accept, and
only on a spec that met the ready gate (`mcp-not-ready` otherwise, before the question).

What the flow concludes after that approval writes without asking: the `reviewed`, `merge` and
`outcome` records and `specs_promote` run as the CLI verbs do. The archive is refused (exit 2) only
by its own content gate — an empty `## Outcome`, or an open task under `done` — never by a
confirmation; `outcome` is not a `specs_record` at all, because `specs_promote` is its one writer.

Size policy: no tool returns a whole spec; reads go by section and by task, listings are paged, and any
answer above 60,000 characters is cut with `truncated: true` and a `hint` naming the narrower call.
Closed surface: the tool tables are closed maps to fixed verbs, with no generic `cq` tool and no argv
passthrough, so no other verb is reachable and a flag-shaped value is refused before the core runs. A
failure is a result with `isError: true` and the CLI's refusal `code`. Registering the server adds no
permission or grant, and nothing here swaps a `Bash(cq specs ...)` grant for these tools.

Resources: the server also lists and reads read-only context, so an agent can fetch the contracts without a
file path. `quenching://config` is the payload of `cq specs config`; `quenching://standards` lists the
standards under `docs/standards/` (title, authority, URI) and `quenching://standards/<path>.md` reads one;
`quenching://glossary` lists the OKF glossary terms. A standard under `DOC_WHOLE` (24,000 characters) comes
whole with its outline; a larger one answers the outline, and `quenching://standards/<path>.md?section=<heading>`
reads one section. `quenching://glossary?term=<term>` reads the entries (comma-separated, at most 20 terms).
A URI resolves only to those two fixed files or to a `.md` inside `docs/standards/`: any other path, a
traversal or an unknown URI is a JSON-RPC error (`-32602` bad parameters, `-32002` not found), never a file
read. The same 60,000-character ceiling cuts an oversized answer with `truncated: true` and a `hint`.

### A revisão Codex independente

Step 6 of `/quenching-specs autopilot` runs, once per epic, a second and independent
correctness review by Codex beside the Claude reviewer. Only the conductor calls `cq codex`; the
reviewer gets no Codex grant. Two verbs of the `codex` pillar carry it:

- `cq codex probe [--json]` answers whether Codex may be called now, without spending quota:
  exit `0` available, `1` unavailable (a window over its ceiling, `crossReview: "off"`, no `codex`
  on `PATH`), `2` unknown (no readable source or a stale snapshot).
- `cq codex review --worktree <dir> --prompt <file> --run <name>` runs `codex exec` with a fixed
  argv that ignores the user's Codex configuration and never asks for Codex's native sandbox; a
  git guard proves afterwards that the review changed nothing.

**Default and opt-out.** The review runs by default whenever the quota allows
(`shared.codex.crossReview: "auto"`); `"off"` in `.agents/quenching.json` is the explicit refusal.
The optional `shared.codex` block defaults to `maxUsedPercent` `80` (primary) and `90`
(secondary), `timeoutSeconds` `900` and `model` `gpt-6-astra`; an absent block is every default.

**Cost and quota.** One Codex call per epic, billed to the ChatGPT/Codex quota and never to the
Claude one. The final report carries its tokens as measured, or `not measured`, apart from the
Claude tiers.

**Where the output lands.** `.quenching/codex/<run>/` holds `prompt.md` (the caller's prompt and
the rule that Codex only reads), `review.md` and `events.jsonl`.

**No sandbox, a git guard instead.** Codex runs with `--dangerously-bypass-approvals-and-sandbox`,
because the native sandbox needs admin rights most machines lack and fails there with errors. The
environment loses `GH_TOKEN`, `GITHUB_TOKEN`, `AWS_*`, `AZURE_*` and `GOOGLE_*`, and the guard
compares the reviewed worktree's `HEAD`, branch, reflog, stash, the index, the status
and bytes of every path `git status` reports and the ignored local configuration (`.claude/**`,
`*.local.json`), before and after. Every symlink that resolves to a file (tracked, ignored or
pointing outside the worktree) is recorded with its target and the hash of the resolved bytes; a
symlink to a directory is not walked and stays a residual risk. Any change, a git command of the
guard that fails, or any file-system error while taking the snapshot, before or after, is exit `2`
`codex-git-guard` with no fallback (the refusal before the run removes the run's folder): the tree
is never cleaned by Claude and goes to the human.

**Fallback.** A probe that exits `1`, or a review that times out or exits `1`, leaves the step with
the Claude review alone, and the final report names the fallback and its reason. A refusal (exit
`2`) is reported the same way and never blocks the step — except `codex-git-guard`, which stops
the run for the human.

**Findings need reproduction.** A finding only Codex raised becomes a spec only once the Claude
side reproduces it, with the command and its output. The Codex surface (`quenching-codex`) has no such step.

### O executor Codex

Step 5b of `/quenching-specs execute` hands **one task at a time** to Codex when the code
admits it; Claude keeps the self-review, the `verify:`, the commit, the tick and the verifier. It
is **on by default**, under `shared.codex.executor` in `.agents/quenching.json`, and independent of
`crossReview` (`executor.enabled: false` is its opt-out).

- **Eligibility** — `cq codex eligible --spec <id> --task <tid> --json`: an open task that declares
  `files:`, writes nothing under `docs/` or `knowledge/`, and is small (bytes of its `files:` / 4 ≤
  `maxTaskTokens`, `20000`) or carries a `verify:`. A cheap model (`modelSmall`, `modelVerified`)
  at `reasoningEffort` `medium`.
- **Quota** — one dispatch at a time, only under `maxUsedPercent − reservePercent` (`80 − 10`) in
  both windows. A task that moves the primary window by more than `stopLossPercent` (`15` points)
  keeps its diff and turns the executor off for the rest of the run.
- **Failure** — a red `verify:` is fixed by Claude on top of Codex's diff; a timeout, a Codex error
  or a spent quota falls back to Claude. Codex never gets a second attempt.

**Bypass, and its risk.** `cq codex implement` always runs `codex exec
--dangerously-bypass-approvals-and-sandbox -C <worktree>`; Codex's native sandbox is never asked
for, because most machines lack the admin rights it needs. The bounds are the plugin's: `--ignore-user-config`, an
environment without `GH_TOKEN`, `GITHUB_TOKEN`, `AWS_*`, `AZURE_*` or `GOOGLE_*`, a prompt that
forbids git, and a **git guard** that compares the worktree's `HEAD`, branch, reflog, stash
and `git status` before and after — any divergence or a path outside `files:` is exit `2`,
the diff is discarded inside `files:` and Claude writes the task. What remains is a command run
outside the worktree that git cannot see. There is no sandbox setting: a leftover
`shared.codex.executor.sandbox` or `windowsSandbox` is ignored.

The Codex surface (`quenching-codex`) has no executor: a Codex run never launches Codex.

The shared facts live once — the spec document, the thirteen canonical sections, the
gates, the record vocabulary, and the `cq specs` surface in
[`specs-develop/spec-driven.md`](references/specs-develop/spec-driven.md),
the execution mechanics in
[`specs-execute/execution.md`](references/specs-execute/execution.md),
the git defaults (read-if-present, never installed) in
[`git/conventions.md`](references/git/conventions.md),
the distillation doctrine in
[`specs-conclude/distill.md`](references/specs-conclude/distill.md).
The per-spec commands are never conducted by any sweep, because each needs fresh human intent a
conducted pass does not have. Every command on this front is **quenching-native** — no
`metadata.generatedBy` anywhere.

## The signature: a canonical OKF bundle of `/docs/`

quenching installs **the same tree** in every repo (adapted to what fits — a repo
without data gets no `catalog/`):

```
/docs/               # OKF bundle root
  index.md               # the ONLY index.md with frontmatter: okf_version: "0.2" + home listing
  glossary.md            # the fixed A–Z term lookup, bundle root — not inside a home
  standards/             # "how WE do it" (current) — architecture/ code/ naming/ data-modeling/
                         #   ci-cd/ workflows/ mlops/ quality/ platform/  (type: standard)
  catalog/               # our data — <system>/index.md · <schema>.md · <schema>/<table>.md
  vision/                # direction by area (type: vision)
  documentation/         # product docs site — Diátaxis prose (type: documentation)
  concepts/              # generic knowledge we hold (type: concept)
  external/              # what we consume — tools/ libraries/ regulations/ (type: external)
```

Specs live on the `quenching` branch, not in the code tree or the OKF bundle. `/quenching-specs create` and `/quenching-specs triage` operate through `cq specs`,
not through files checked into the target repository. An agreed-but-unproven decision is a
`standard` with `authority: background`; its history lives in `decisions/`.

**OKF-strict rules the plugin enforces:**

- `index.md` is **reserved** — a listing, **no frontmatter** (the one exception is the
  root `/docs/index.md`, which carries **only** `okf_version: "0.2"`).
- Every concept doc (non-`index.md`/`log.md`) carries **non-empty `type`** from the
  fixed vocabulary above, plus the OKF recommended fields and the method's extra keys.
- `log.md` is **retired**: nothing creates one, appends to one, or checks one. The name
  stays reserved so a log surviving an earlier alignment is recognized rather than flagged
  as a malformed concept doc — retired is not unreserved.
- Links are **relative** within a home, **absolute from the bundle root** (`/docs/...`)
  across homes.
- Folder names **and concept-doc file slugs**, frontmatter keys/enums, and the `type`
  vocabulary are **canonical English** (cross-repo greppable); **body prose may follow the
  repo's language**, and identifier-derived slugs (catalog tables, repo names)
  stay verbatim.
- **Structure is aggregated and listed** — a run of prefix-clustered files
  (`nomenclatura-*.md`) folds into a subject subfolder; every folder that holds concept docs
  has an honest `index.md`. The validator flags (WARN) a missing `index.md` (`dir-no-index`),
  a listing that links to a nonexistent file (`index-broken-link`), and a concept doc nothing
  links to (`index-orphan`).

The OKF contract lives in the skills' `references/`; the installable payload is in
[`assets/`](assets/README.md).

## Model policy

`cq specs estimate <id> --json` reports a **declared-reading estimate** by task section: unique
declared files and Impact standards, plus the execute command body and spec build sections, using
UTF-8 bytes / 4 rounded upward. Files repeated in one section count once; a new section counts its
reads again. Missing/new files and tasks without declared files remain `unresolved`. The default
worker **size estimate** is **100000 input-context tokens** (S2): it says how much reading a spec of
that size fits, and it never stops a build; `--worker-budget` declares an explicit override.
The estimate **never proves** a full build fits: system/harness overhead, conditional references,
future code, tool/test output, iteration count and growing history are excluded. Total reading
volume is not a context peak. Develop compares the largest section before approval and proposes
decomposition in the main session when known reading exceeds the budget. It presents independent
slices first; capturing an epic requires explicit authorization. Declared autonomy leaves an oversized
source unapproved and returns the decision to its conductor.

The command registry loads at **session start**, so surface changes require fresh `claude -p`
processes. `assets/checks/functional-checks.sh` deploys this checkout into throwaway targets and proves root
substitution, conductor reachability and description routing. Each check is a **billed agent
session** owned by the command that changes the surface; the default is the body subset and
spoken routing is opt-in (`--only 3`).

**The model policy is conservative — judgment is never downgraded:** the small tier (`haiku` in
Claude, `gpt-6-luna` in Codex) writes product code only as the executor of ONE testable task —
an executable `verify:` whose tests sit outside the task's `files:`, a disposable worktree,
nothing under `/docs/`, and a projected context at or under 80k (`cq specs estimate --task`
reports `smallTierEligible`). One attempt; a failed `verify:` returns the task to the session
model. Develop, triage, conclude, the spec-orchestrator, spec-verifier, spec-reviewer, spec-runner and every
`/docs/standards/` write never descend, and `import-memory` stays never-`haiku`.

| Surface | Policy |
| --- | --- |
| `/quenching-knowledge define` | **no pin** — the edit is mechanical, but an inline `effort: low` is part of the session's prompt-cache key, so it recomputes every input token on the next request ([`capabilities.md`](references/components-command-new/capabilities.md) §Model and effort). A single-entry edit does not buy that back. **No hook either** — the rung-1 frontmatter block this row once described was removed when the plugin's own wiring covered the same case, and that wiring was later discontinued outright, so nothing answers a write event here any more (`/docs/standards/automation/hooks.md`). What checks conformance at write time is the body's own **Self-check against the conformance core** step, run by the command, not fired by anything |
| `/quenching-specs create` | **`model: sonnet`** — the capture is mechanical and effort-proportional, so the tier it does not need is the expensive one. Zero interrogation before the write, no sub-agents. The pin is paid for once, in the **cache trap** ([`capabilities.md`](references/components-command-new/capabilities.md) §Model and effort): an inline `model:` is part of the session's prompt-cache key, so **changing** it recomputes every input token on the next request. A pin left alone costs nothing after the first run, which is what makes a stable pin affordable and pin-churn expensive. **The closing screen's hand-off into `/quenching-specs develop` (`model: opus`) is the one path that changes the pin mid-session** — an inline `model:` switch recomputes the input tokens on the very next request, so the hand-off is not free the way an ordinary `Skill` invocation is; unmeasured as of this writing, and worth a real run before assuming the cost is negligible |
| `/quenching-specs triage` | **`model: opus`**, no `effort` override — the *reading* is cheap (a few small frontmatter blocks) but the *output* is a ranking grounded in `vision/`, which is exactly the judgment the top tier exists for; the human plan-gate contains misjudgment but should not have to catch it. No sub-agents |
| `/quenching-specs status` | **no pin**, no sub-agents, **no `Write`/`Edit` in `allowed-tools`** — it classifies against a fixed finding vocabulary it does not own, and `cq specs status` is scoped to full-progress plans rather than run per plan. The former `effort: low` was dropped for the cache trap: a read-only view is not worth invalidating the session's prompt cache |
| `/quenching-knowledge status` | **no pin**, no sub-agents, **no `Write`/`Edit` in `allowed-tools`** — the `docs` counterpart of the row above, and its `effort: low` was dropped for the same reason. Both bodies also forbid `context: fork` by name: each doubles as a sweep's preview, and the report has to land in the conversation where the OK will be given |
| `/quenching-specs board` | **no pin**, `disable-model-invocation: true`, `Bash(cq:*)` only — a launcher over `cq specs serve`; the server is stdlib Python and its assets live in `assets/portal/` (no build, no CDN) |
| `/quenching-specs orchestrate` | **no pin**, no `Write`/`Edit` in `allowed-tools` — a launcher; the plugin ships five agents in `agents/` that carry the pins: `spec-orchestrator` opus/medium, `spec-runner` sonnet/medium (opus when `complexity: high`, passed by the orchestrator), `spec-verifier` and `spec-scout` sonnet/low, `spec-reviewer` opus/high (read-only, once per epic, launched by the autopilot conductor, not by the orchestrator). No spec route runs on haiku: the small-tier rung is per task, inside execute. |
| `/quenching-specs conclude` | **`model: opus`** when a human invokes it directly (under the `spec-runner` it runs on the runner's model, sonnet or opus by `complexity`, because the pin does not switch the runner's session), no sub-agents — the branch review, the merge choice, the outcome, and the distillation are all judgment; there is nothing mechanical here to downgrade, and the review reads a whole branch diff for coherence rather than one task's |
| `/quenching-knowledge glossary-backfill` | **no pin** on the orchestrator (the former inline `effort: medium` charged the cache trap); slice sub-agents `model: haiku` + `effort: low` (pure extraction, cross-checked by the orchestrator) — a sub-agent's pin is cache-safe, it has its own context. `Bash` scoped to `python3`/`py`: its reading is `Grep`/`Glob`/`Task`, and the checker is the only shell it runs |
| `/quenching-knowledge import-memory` | classification sub-agents `model: sonnet` + `effort: low`; **executor sub-agents inherit the session model** (their self-check authorizes memory deletion). `Bash` stays unrestricted **and is now priced in the body**: step 1 derives the memory directory as one compound shell expression, which no prefix grant can match |
| `/quenching-knowledge align` / `/quenching-components harness-align` | repo-wide grep/find sweeps delegable to one read-only `haiku` + `effort: low` collector; every classification stays with the orchestrator when run standalone. `/quenching-components harness-align`'s `Bash` is scoped to `git grep` / `git check-ignore` / `grep` / `python3` / `py` — the two-scan sweep, the build-artifact check, the checker, and nothing else; `/quenching-knowledge align` keeps the unrestricted grant its body prices. **Exception:** under `/quenching-knowledge align`'s parallel content prep, harness's read-only discovery (steps 1–4, incl. MOVE/KEEP classification) runs in a background `Task` agent pinned `model: sonnet` — never haiku, same misclassification-risk rationale as the cycle's assessment agent |
| `/quenching-knowledge align` (content passes) | per-pass read-only assessment via a `sonnet` + `effort: low` sub-agent (haiku ruled out: a false "nothing to do" ends the loop early) |
| `/quenching-align` | no pin, no sub-agents — the front probe is a handful of globs and two CLI calls, and every write belongs to the sweep it invokes (which carries its own policy row) |
| `/quenching-knowledge import` | extraction/executor sub-agents may run `model: haiku` + `effort: low` — import **deletes nothing**, so a misclassification only misfiles a doc (correctable); the orchestrator keeps each `index.md` honest and resolves cross-slice dedup |
| `/quenching-knowledge add` / `/quenching-knowledge learn` | no pin — they inherit the session model (they classify, route, and gate operations). **Neither carries a frontmatter hook block** — the rung-1 blocks these two once carried were removed when the plugin's own wiring covered the same case, and that wiring was later discontinued outright, so no hook fires on their writes (`/docs/standards/automation/hooks.md`). Each body's own **Self-check against the conformance core** step is the conformance check at write time: a step the command runs, not a rung anything enforces |
| `/quenching-knowledge documentation-build` | no pin, no sub-agents — the inventory is a handful of globs plus one config parse, and the expensive step is an external `zensical build`, not tokens; the config **merge** and the fix-vs-report split are exactly the judgment the plan gate exists to contain. `Bash` stays unrestricted **and is now priced in the body**: it drives a toolchain the plugin does not own, reachable through `pip`, `uv` or a bare `python -m` |
| `/quenching-knowledge documentation-produce` | no pin, no sub-agents — the conductor sequences four named stages under one authorization and reports their summaries; it has no `Write`/`Edit` grant |
| `/quenching-knowledge documentation-plan` | no pin, no sub-agents — source diagnosis, IA and six contracts require the session's judgment; only the plan-of-record is written |
| `/quenching-knowledge documentation-write` | no pin on the author; large batches may fan out `Task` slices pinned to the session model, never `haiku`, because each slice writes human-facing prose |
| `/quenching-knowledge documentation-review` | no pin, read-only; large page sets may fan out `Task` slices without write tools, returning condensed rubric verdicts |
| `/quenching-components command-new` | no pin, no sub-agents — classification on the axis, doctrine-grade drafting, and the plan gates inherit the session model |
| `/quenching-components align` | no pin. Its §7 doctrine audit **may delegate collection** to read-only `Task` collectors — one per slice, reporting *what each body contains* (which levers its frontmatter carries, what it cites, where its steps end) on a surface large enough that reading every body would bury the conversation. Every verdict stays with the orchestrator: "this body has no positive prescription" is a claim about behaviour, and the read that makes it must also weigh the fix |
| `/quenching-specs develop` | **`model: opus`** when a human invokes it directly (under the `spec-runner` it runs on the runner's model, sonnet or opus by `complexity`, because the pin does not switch the runner's session) — the whole command *is* judgment: generating the questions a spec never answered, recommending an answer to each, and deciding when the interrogation is done. There is nothing mechanical here to downgrade, and a cheap model that asks generic questions produces exactly the refinement theatre the command exists to replace. Cost is bounded by each stage's declared stop condition and by one edit per pass, not by a model tier. One **read-only** sub-agent is permitted, and only for compose and refine: it sweeps the code and the `/docs/standards/` the spec declares and returns one table (`references/specs-develop/questions.md` §Gathering the evidence). It reads; it never asks, writes, or decides — every question, every `cq specs` call and every confirmation stays with the orchestrator. **This is not `context: fork`**, which cannot ask a question at all, so the never-fork rule is untouched |
| `/quenching-specs execute` | **`model: sonnet`** — the loop is write · verify · self-review · tick · commit against a spec that already decided what to build, and the judgment it does keep is gated by a human at every confirmation. A per-task **executor sub-agent is permitted** when the task declares `files:` and touches no `/docs/` — pinned to the **session model** — `sonnet` with this command pinned — or to `haiku` for ONE attempt on a task `cq specs estimate --task` reports `smallTierEligible` (a protected oracle catches the cheap model's mistake; a failed `verify:` returns the task to the session model). The orchestrator keeps spec selection, every confirmation, every `cq specs task --check`/`--block`, every `/docs/standards/` write, the commit, and the pause decision. Two tasks run concurrently only when `cq specs parallel` reports the `[P]` group eligible; serial is the default. **This is not `context: fork`** — the orchestrator stays in the live conversation, so the never-fork rule is untouched (`references/specs-execute/execution.md` §This is not `context: fork`) |

Shared contracts keep gates explicit; missing `gh` or `az` is a named refusal
(exit 2).

## Install

quenching is served only by installation into the target repository with `cq deploy`
([ADR 0017](../docs/decisions/0017-install-only-by-deploy.md)); there is no marketplace plugin
to install for it. Try it first in a disposable repository. From a clone of this repository:

```bash
python3 quenching/assets/bin/cq deploy --target <repo> --write
```

Or, with no clone, from a release tag through `uvx` (Python 3.11+, no Node):

```bash
uvx --from "git+https://github.com/holetz/quenching@<tag>#subdirectory=quenching" \
  cq deploy --target . --modules core --write
```

`<tag>` is a release tag such as `7.0.0` (list them with
`git ls-remote --tags https://github.com/holetz/quenching`); a literal `<tag>` fails with
`Git operation failed`. To upgrade an installed target, drop `--modules`: the recorded manifest
keeps its modules, while `--modules core` narrows a wider install and deletes the rest.

| Option | Values |
| --- | --- |
| `--modules` | `core` (default: `quenching-specs` plus `quenching-align` — specs, git, knowledge, components), `all`, or a comma list of modules; `specs` is always included because it owns the one `cq` |
| `--harness` | `claude`, `codex`, `opencode` (default: all three) or `none` |
| `--runtime` | `vendor` (default, offline) copies the runtime; `uvx` writes a shim pinned to the release tag |
| `--profiles` | overrides the derived `shared.profiles.installed` |
| `--check` | exit 1 on drift instead of writing |
| `--prune-legacy` | removes a pointer-only `CLAUDE.md` |

Deploy writes `AGENTS.md` and `.agents/quenching.json` only when absent, plus the generated
`.agents/skills/`, `.agents/quenching/` (with the target's own `.agents/quenching/bin/cq`), the
`.claude/skills/` bridge and, per selected harness, the Claude and OpenCode subagents. It records
what it owns in `.agents/.quenching-deploy.json`. `CLAUDE.md` is not created. Deploy installs the
surface only: the target's `/quenching-knowledge align` installs `/docs/` and converges the fronts.
The full contract, including the surface translation, is [deploy-mode.md](../docs/standards/architecture/deploy-mode.md).

A deployed target runs the same ids this manual writes: `/quenching-<vertical> <flow>`, for
example `/quenching-specs create`, with the source written in that dialect
([source-layout.md](../docs/standards/architecture/source-layout.md)). A route into a module that was
not deployed is reported `not-installed: <module>`, and `cq <front>` for it exits 2 naming the
module.

Local development of this repository uses the same path: it runs its own deployed surface, and
`python3 quenching/assets/bin/cq deploy --target . --write` refreshes it after a change to
a skill body, a reference or the payload.

### Migrating from the retired plugins

Releases before ADR 0017 published the surface as Claude marketplace plugins (`quenching`, then the
nine `quenching-<module>` modules and `quenching-specs-reader`), a Codex plugin and an OpenCode
distribution under `~/.opencode/`. None is published any more, and an installed copy competes with
the deployed one for the same command names. Migrate a target once:

1. Uninstall the retired plugins from each harness, and remove their `enabledPlugins` entries
   from the target's `.claude/settings.json`.
2. Run `cq deploy --target <repo> --write` as above.
3. Rename every typed or cited command in the target's own files — `.agents/skills/**`,
   `AGENTS.md` (legacy `CLAUDE.md`), hooks and scripts — from `/quenching-<module>:<front>:<verb>`
   to `/quenching-<vertical> <flow>`.

Nothing in the target's `/docs/`, `.agents/quenching.json` (or legacy `.claude/quenching.json`) or
spec store changes. A project that only read another project's specs through the retired reader
deploys `core` instead: the read verbs ship with it.

## Uninstall or reverse

Re-running `cq deploy --write` with a narrower `--modules` or `--harness` removes the dropped part
of the surface. To remove all of it, delete the files `.agents/.quenching-deploy.json` lists and
the manifest itself, or revert the commit that deployed them. Neither touches the target's `/docs/`,
its own skills or `.agents/quenching.json`: those are repository-owned data and configuration. To
reverse an alignment, review and revert the target repository's own commits; removing the surface
is not a data rollback. If an upgrade is the problem, deploy the previous release tag again.

In a deployed target the CLI is `.agents/quenching/bin/cq`; this checkout runs
`quenching/assets/bin/cq`. The resolution rules are in
[`references/align/tool-resolution.md`](references/align/tool-resolution.md).

## Upgrade

A target upgrades by running `cq deploy --target <repo> --write` again from a newer checkout or
release tag; the manifest keeps the recorded modules, harnesses and runtime unless a flag overrides
them, and `cq deploy --target <repo> --check` reports drift in between.

The release history is kept in the root [`CHANGELOG.md`](../CHANGELOG.md). The plugin version is
updated only by a deliberate release; `cq specs release <version>` checks the changelog entry and
updates the published artifacts in lockstep. See
[`ci-cd/versioning-release.md`](../docs/standards/ci-cd/versioning-release.md) for the release
contract.

<!-- quenching-proof-readme-start -->
<!-- quenching-proof-readme-sha256 9ad4379bf2d166f8387f74a629cc66c237c574ef00d192082e89ef7c2fa8780b -->
## Declared proof layers

### tests
- Proves: the `tests` proof contract declared by the target.
- Marker: `tests`
- Reach: tree
- Budget: not declared
- Required: yes
- Test modules: 164
- Fixture modules: none

### Declared cost contract
- Temp root: `isolated` — outside the repository, removed when the run ends
- Workers: `auto`
- Task scope: `python3 -m scripts.toolchain.test --affected`
- Close scope: `QUENCHING_TEST_SCOPE=affected bash scripts/verify_repo.sh`
- CI scope: `bash scripts/verify_repo.sh`
<!-- quenching-proof-readme-end -->
