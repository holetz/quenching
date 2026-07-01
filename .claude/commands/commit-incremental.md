---
name: commit-incremental
description: Analyzes all uncommitted changes in the working tree, groups them into atomic, cohesive commits, and generates short, standardized messages in Portuguese following the repository's style. Use WHENEVER the user asks to "commit the changes", "make incremental commits", "break the changes into commits", "organize the commits", "slice this branch", "commit in stages" — or on any generic commit request when there are several unrelated changes in the working tree that warrant separate commits. Unlike a single commit, this skill is the right path when the diff spans multiple scopes/domains/features that should become distinct commits.
model: sonnet
---

# commit-incremental

Breaks a messy working tree into a sequence of atomic commits, each with a short Portuguese message in the repository's style.

## Flow

Run exactly in this order. Each step justifies the next — if a step is skipped, the result is wrong (commits mixing scopes, off-standard messages, or worse, committing things the user did not expect).

### 1. Establish the real state

```bash
git status --short
git diff --stat
git diff
git diff --cached --stat
```

If `git status` is clean, stop and report: "Nothing to commit."

### 2. Detect an already-staged index

If any file is in the index (a line in `git status --short` whose first column is non-empty/non-`?`), **stop and hand control back to the user**. Ask: "You already have N file(s) staged — do you want to commit that first with your own message, reset with `git reset` so I regroup everything, or include those files in the grouping?"

The reason: staged files usually represent an intent the user has already formed. Regrouping on your own can silently destroy that intent.

### 3. Actually read the diff

For each modified/new file, read the diff content — do not group by filename alone. A single file may contain changes from different scopes (e.g., an MLOps model tweak + an import fix); in that case, either (a) commit the whole file together with the dominant group, or (b) if the changes are clearly independent, use `git add -p` to slice it. Prefer (a) when the overhead of (b) is not worth it.

For `untracked` files (`??`), read the content with `Read` to classify them.

### 4. Group by logical affinity

Good groupings respect these affinities, in order of priority:

1. **Same functional domain** — changes in the same MLOps model, same gold task, same documentation. E.g., `pipeline/model.py` + `pipeline/features.py` + `lib/columns.py` for the same `cura_e3_v02_r03` form ONE commit.
2. **Source + generated artifact** — in this repo, co-located YAMLs (`src/safra/bundle/jobs/*.job.yml`, `src/safra/bundle/catalogs/**/*.schema.yml`) and `tasks_manifest.json` are generated from the Python sources (see CLAUDE.md). They must travel **in the same commit** as the source that produced them, never in a separate "regenerate YAMLs" commit.
3. **Homogeneous change type** — several small, unrelated tweaks in unrelated files may become ONE "Ajustes diversos" commit only if they are truly tiny; otherwise, separate them.
4. **New feature vs tweak vs fix** — do not mix a large new file with a cosmetic tweak elsewhere.

Anti-patterns to avoid:
- One commit per file (history pollution).
- One giant "WIP" commit covering everything (loses the granularity that justifies the skill).
- Pure formatting/lint commits mixed with logic changes.
- Separating generated YAML from the source that generated it.

Aim for **2-6 commits**. Beyond that, you are probably over-fragmenting; if it is just 1, you may not need the skill.

### 5. Write the messages

Repository style (extracted from `git log`):

- Short: 3-8 words, ideally fitting in ~50 characters.
- Portuguese.
- **No prefixes** like `feat:`, `fix:`, `chore:` — this repo does not use conventional commits.
- **No `Co-Authored-By` trailer** — the team does not use it.
- Starts with a present-tense indicative verb (Adiciona, Cria, Atualiza, Corrige, Remove, Refatora, Habilita, Integra, Migra, Padroniza, Regenera, Reformula, Documenta) OR a scope noun (Ajustes ASR, Desenvolvimento FL, Organização repositório, Limpeza backup).
- Include the scope/domain when it helps (ASR, FL, gold, silver, MLOps, res4966, garantias, etc.).
- No trailing period.

Real examples from this repo (use as a reference for tone):
```
Ajustes Cura E3/E2/AP
Cria task vinculo_manual_grupo_economico no domínio silver
Habilita domínio SIM res4966_v02 e regenera YAMLs/manifest
Adiciona suporte a time travel em TableTask.read
Corrige janela de deterioração e exclusões da predição ASR
Integra Score Unicred às features e modelo do PD Lifetime
Padroniza domain_key/version para o formato vNN_rNN
```

Avoid: "update files", "various fixes", "WIP", "improvements", emojis, generic descriptions like "ajusta código".

### 6. Present the plan and ask for ONE OK

Show the user in a compact format:

```
Plano de commits (N grupos):

[1] <proposed message>
    - arquivo/a.py
    - arquivo/b.py
    (reason: <1 line on why these files belong together>)

[2] <proposed message>
    - ...

Confirma? (s para executar tudo, ou diga o que ajustar)
```

Wait for the response. If the user asks for adjustments (rename a message, move a file between groups, merge/split), apply them and show the plan again. Do not commit until you receive explicit confirmation.

### 7. Execute

Once confirmed, for each group, in order:

```bash
git add <group files, by explicit name>
git commit -m "<message>"
```

**Never** use `git add -A` or `git add .` — add by explicit name to avoid accidentally picking up a file from another group. Never use `--no-verify`. Never `--amend` commits that are not from this same run.

If a pre-commit hook fails, stop the sequence, show the error, and ask the user how to proceed. Do not try to "fix" it on your own by skipping the hook.

At the end, run `git log --oneline -N` (where N = number of commits created) and `git status` to show the result.

## Edge cases

- **Only untracked files**: treat the same — read, classify, group. `git add` handles `untracked` normally.
- **Deletions**: group with what motivated the removal (e.g., deleting an obsolete notebook alongside the commit that replaces it).
- **Files with secrets** (`.env`, `credentials.json`, keys): do not include them in any group. Warn the user and ask explicitly first.
- **Huge diff** (>500 files or >50k lines): warn the user that the grouping may be coarse and offer to narrow the scope first (e.g., start with folder X).
- **Large binary files**: treat as a separate group and confirm with the user.
```