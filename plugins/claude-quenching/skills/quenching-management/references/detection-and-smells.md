# Detection and score rule

> **Back path:** [../SKILL.md](../SKILL.md) (agent roadmap) ·
> human overview & architecture: the project docs site ·
> [README.md](README.md) (`references/` index).

**Detection cookbook**: read-only commands per dimension (run from the root of the
target repo). **Step 0** derives the real paths; each transversal block contains the
bash + how to read the result + a pointer to the **complete doctrine** in the
corresponding dimension of [dimensions-template.md](dimensions-template.md).

`docs/` has a **prescriptive canonical taxonomy** ([docs-taxonomy.md](docs-taxonomy.md)):
Step 0 derives **against the canonical names first** (`standards/`/`decisions/`/
`vision/`/`backlog/`/`guides/`/`reference/`/`catalog/`/`presentations/`) and treats a
**variant name** (`docs/arquitetura/`, `docs/adr/`, `VISION.md`) as a **migration candidate**,
not as "the repo form that wins". Outside `docs/` (`.claude/`, root) the
method is **portable/adaptive**: adjust the variables to the repo's form.

## The four-state rule

| State | When to assign |
| --- | --- |
| **Present** | The artifact exists and the dimension check passes without caveat. |
| **Partial** | Exists, but coverage is missing (e.g.: backlog with no reference to the vision; skill without `references/` in a 600-line SKILL.md). |
| **Drifted** | Exists, but **lies**: index cites a non-existent file, broken link, completed item still in the tree, implemented ADR not removed, stale catalog. Generally **top priority** (misleads the agent). |
| **Absent** | Does not exist and **should**, given the derived form. In a greenfield repo, nearly everything starts Absent — this becomes the **installation** roadmap (stamp the payloads from [../assets/](../assets/)). |

Always record **evidence `file:line`** (not "seems outdated").

## Step 0 — derive the target repo's paths (do this before everything else)

```bash
# Current standards layer: CANONICAL docs/standards/ first; then variants (= migrate)
ARCH_DIR=$(for d in docs/standards docs/arquitetura docs/architecture docs/adr \
  architecture standards; do [ -d "$d" ] && { echo "$d"; break; }; done)
# Current layer index: CANONICAL INDEX.md first (INDICE.md is a variant)
ARCH_INDEX=$(ls "$ARCH_DIR"/INDEX.md "$ARCH_DIR"/INDICE.md "$ARCH_DIR"/README.md 2>/dev/null | head -1)
# Vision: CANONICAL docs/vision/ folder first; single VISION.md/ROADMAP.md = variant (segment it)
VISION=$(for d in docs/vision; do [ -d "$d" ] && { echo "$d"; break; }; done)
[ -z "$VISION" ] && VISION=$(ls docs/VISION.md VISION.md docs/vision.md ROADMAP.md docs/ROADMAP.md 2>/dev/null | head -1)
# Backlog tree (canonical docs/backlog/)
BACKLOG=$(for d in docs/backlog backlog docs/todo; do [ -d "$d" ] && { echo "$d"; break; }; done)
# Open decisions: CANONICAL docs/decisions/ first; docs/adr/ = variant (migrate)
ADR=$(for d in docs/decisions docs/adr adr decisions; do [ -d "$d" ] && { echo "$d"; break; }; done)
# Catalog/domain (canonical docs/catalog/)
CATALOG=$(for d in docs/catalog docs/catalogo_dados docs/data_catalog docs/dominio; do [ -d "$d" ] && { echo "$d"; break; }; done)
# Domain/consumption doctrine (if present)
DOMAIN=$(ls docs/agents/domain.md docs/domain.md docs/CONTEXT.md 2>/dev/null | head -1)
echo "ARCH_DIR=$ARCH_DIR  ARCH_INDEX=$ARCH_INDEX  VISION=$VISION"
echo "BACKLOG=$BACKLOG  ADR=$ADR  CATALOG=$CATALOG  DOMAIN=$DOMAIN"
#   Empty variable = canonical home does not exist ⇒ candidate for Absent (install the package scaffold)
#   Variable pointing to a VARIANT NAME (arquitetura/adr/VISION.md/INDICE.md) ⇒ candidate for MIGRATION
for v in "$ARCH_DIR:docs/standards" "$ADR:docs/decisions" "$VISION:docs/vision" \
         "$ARCH_INDEX:INDEX.md" "$CATALOG:docs/catalog"; do
  got=${v%%:*}; want=${v##*:}; [ -n "$got" ] && [ "${got##*/}" != "${want##*/}" ] \
    && echo "VARIANT  $got  → canonical: $want (migration candidate, propose with OK)"; done
```

## Commands per dimension

```bash
# 1. Entry map (CLAUDE.md): inventory + line ceiling (derive the ceiling from the repo hook)
find . -name CLAUDE.md -not -path './.git/*' | while read -r f; do
  printf '%5s  %s\n' "$(wc -l < "$f")" "$f"; done | sort -rn
#   above the ceiling ⇒ Drifted/Partial (a validation hook also flags this; the package
#   loads ../assets/hooks/validate-claude-md.py with a configurable ceiling)

# 1. CLAUDE.md links pointing to a non-existent file (sample)
grep -rEno '\]\(([^)]+\.md)\)' --include=CLAUDE.md . | head -50
#   resolve each link against the real file

# 2. Normative reference: index × real files
[ -n "$ARCH_INDEX" ] && sed -n 's/.*(\([^)]*\.md\)).*/\1/p' "$ARCH_INDEX"   # docs cited in the index
[ -n "$ARCH_DIR" ] && find "$ARCH_DIR" -name '*.md' | sort                  # docs that exist
#   difference between the two lists ⇒ Drifted (index lies)
[ -n "$ARCH_DIR" ] && grep -rEn "$ARCH_DIR/[a-z0-9/-]+\.md" --include='*.md' --include='*.py' . \
  | grep -v "/$ARCH_DIR/"   # external pointers to the folder

# 3. Vision (VISION): infiltrated dates/milestones (vision does not carry deadlines)
[ -n "$VISION" ] && grep -nEi '\b(202[0-9]|q[1-4]/20|sprint|prazo|deadline|cronograma|marco)\b' "$VISION"

# 4. Backlog: items per pillar; items with no reference to the vision
[ -n "$BACKLOG" ] && find "$BACKLOG" -name '*.md' | sort
[ -n "$BACKLOG" ] && grep -RLn 'vision_refs\|rumo\|vision' "$BACKLOG" 2>/dev/null   # items with no vision ref

# 5. ADR: ledger × folders; implemented ADRs that were not removed
[ -n "$ADR" ] && ls -d "$ADR"/[0-9]*/ 2>/dev/null
[ -n "$ADR" ] && sed -n '/[Dd]estilad/,$p' "$ADR"/README.md 2>/dev/null   # ledger of removed entries

# 6. Skills: size + name vs folder + short description (subtrigger)
for f in .claude/skills/*/SKILL.md; do
  [ -e "$f" ] && printf '%5s  %s\n' "$(wc -l < "$f")" "$f"; done | sort -rn   # >500 ⇒ split
grep -rEl '^name:' .claude/skills/*/SKILL.md   # verify name == folder name
# 6. Subtrigger: vague description / 1st-2nd person / side-effect without a lock
grep -rEni 'description:.*(helps? with|does stuff|handle[s]? (files|data)\b)' .claude/skills/*/SKILL.md
grep -rEni 'description:.*\b(I can|you can|we can)\b' .claude/skills/*/SKILL.md   # must be 3rd person
grep -rLni 'disable-model-invocation:[[:space:]]*true' \
  $(grep -rEli 'description:.*(deploy|commit|push|migrar|enviar|envio|delete|apagar)' .claude/skills/*/SKILL.md 2>/dev/null) 2>/dev/null  # side effect ⇒ lock auto-trigger

# 7. Sub-agents: inventory + frontmatter
ls .claude/agents/*.md 2>/dev/null
grep -rEn '^(name|description|tools|model):' .claude/agents/*.md 2>/dev/null

# 8. Hooks: does each command point to an existing script?
sed -n 's/.*\(\.claude\/hooks\/[A-Za-z0-9_.-]*\).*/\1/p' .claude/settings.json 2>/dev/null | sort -u
ls .claude/hooks/ 2>/dev/null

# 9. Commands: orphans (command with no corresponding skill)
ls .claude/commands/*.md 2>/dev/null

# 11. Catalog/domain (if present): $CATALOG already derived in Step 0 (canonical docs/catalog/)
[ -n "$CATALOG" ] && grep -rL 'AUTO-GERADO\|AUTO-GENERATED' "$CATALOG"/**/*.md 2>/dev/null   # expected: few

# 13. Conventions: code/naming docs in the normative layer
[ -n "$ARCH_DIR" ] && ls "$ARCH_DIR"/codigo/ "$ARCH_DIR"/code/ "$ARCH_DIR"/nomenclatura/ "$ARCH_DIR"/naming/ 2>/dev/null

# 14. Guardrails: guardrails skill present and cited (not copied) in CLAUDE.md
ls .claude/skills/*guardrail*/SKILL.md .claude/skills/*karpathy*/SKILL.md 2>/dev/null
grep -niE 'guardrail|karpathy|think before coding|simplicity first' CLAUDE.md 2>/dev/null

# 15. MCP: .mcp.json versioned? literal secret? documented in CLAUDE.md?
ls -la .mcp.json managed-mcp.json 2>/dev/null   # absent ⇒ no server in project scope
#   hardcoded secret (should be ${VAR}): credential keys with a literal value
grep -nE '"(api_?key|token|secret|password|authorization|bearer)"[[:space:]]*:[[:space:]]*"[^$]' .mcp.json 2>/dev/null
grep -ni 'mcp' CLAUDE.md 2>/dev/null   # does the repo document which MCP servers it expects and in which scope?
#   ACTIVE server without a project entry = phantom dependency (local/user scope):
#   ask the user to run `claude mcp list` / `/mcp` and cross-reference with .mcp.json (outside read-only)
```

## Dimensions / transversal blocks

Each block below is just **bash + how to read + pointer**. The doctrine (why it matters,
decision criteria, semantics) lives in the **dimension** indicated.

### 10. Memory (Auto Memory)

Cross the index (`MEMORY.md`) of the project memory directory (path from the session
context) with the `.md` files alongside it. The greps **list candidates**; whoever decides
the smell is the reading. The method **only signals** — it does not write memory. Run from the
memory folder (replace `$MEM` with the context path).

```bash
# (1) index orphan: topic file with no line in MEMORY.md
for f in "$MEM"/*.md; do b=$(basename "$f"); [ "$b" = MEMORY.md ] && continue; \
  grep -q "$b" "$MEM/MEMORY.md" || echo "ORPHAN  $b"; done
wc -l "$MEM/MEMORY.md"   # >200 lines (or >25KB) ⇒ the tail of the index never loads
# (3) vague temporal reference instead of an exact date
grep -rniE '\b(recently|recente(mente)?|last time|outro dia|hoje|ontem|agora)\b' "$MEM"/*.md
# (4) silent conflict: entry marked obsolete that should be pruned
grep -rniE '\b(errad[oa]|corrigid[oa]|supersed|obsolet|deprecat|ignorar|desconsider)' "$MEM"/*.md
# dates present? (provenance — smell 5 when absent/old)
grep -rnoE '20[0-9]{2}-[01][0-9]-[0-3][0-9]' "$MEM"/*.md | head
```

Smells (2) duplicates-the-repo and (6) wrong-type/scope **have no grep**: they are
comparative reading. Complete doctrine: **dim 10** in [dimensions-template.md](dimensions-template.md).

### 1b. Pruning criterion / context budget

`wc -l` (command 1) finds the **size**; these greps only **list candidates** for
cutting/conversion. Who decides "does this matter?" is the reading applying the pruning criterion.

```bash
# pruning candidates: obvious practice / standard language convention (model default)
grep -rniE 'código limpo|clean code|boas práticas|seja consistente|escreva testes\b' \
  $(find . -name CLAUDE.md -not -path './.git/*')
# candidates to CONVERT to a hook (mandatory rule in prose = enforcement, not a map)
grep -rniE '\b(sempre|nunca|obrigatóri|você (deve|precisa)|antes de (commit|fazer))\b' \
  $(find . -name CLAUDE.md -not -path './.git/*')
# @import does NOT save context (expands inline) — flag if used to "slim down"
grep -rnoE '@[A-Za-z0-9_./~-]+\.md' $(find . -name CLAUDE.md -not -path './.git/*')
```

**Fossil / context rot (no grep):** for each directive in CLAUDE.md that references a
standard, check in `$ARCH_DIR` whether the standard **is still current**; a directive
describing a replaced standard is a fossil loaded in every session ⇒ Drifted. Complete
doctrine: **dim 1** in [dimensions-template.md](dimensions-template.md).

### 2b. `docs/` coverage against the canonical taxonomy

The greps **list candidates**; reading decides. Step 0 already derived each layer
against the canonical names; this step checks the **set** against the taxonomy
([docs-taxonomy.md](docs-taxonomy.md)): absent canonical homes, homes in a **variant name** (to
migrate), material **outside** a home.

```bash
DOCS=$(for d in docs documentation doc; do [ -d "$d" ] && { echo "$d"; break; }; done)
# absent canonical homes (empty in Step 0 = candidate for Absent, given the repo's form)
for v in ARCH_DIR VISION BACKLOG ADR CATALOG DOMAIN; do \
  eval "val=\$$v"; [ -z "$val" ] && echo "CANONICAL-HOME-MISSING  $v"; done
# loose technical markdown at the ROOT of docs/ (outside a named home) ⇒ no segmentation
[ -n "$DOCS" ] && find "$DOCS" -maxdepth 1 -name '*.md' -not -iname 'README.md' -not -iname 'INDEX*' -not -iname 'INDICE*'
# canonical binary SLOTS: presentations/ (slides/diagrams/reports) + reference/regulations/
#   (variants: apresentacoes/diagramas/normativos)
SLOTS='-path */presentations/* -o -path */reference/regulations/* -o -path */apresentacoes/* -o -path */diagramas/* -o -path */normativos/*'
# HUMAN/binary material without a slot home (leaking into the technical layer or into the root)
[ -n "$DOCS" ] && find "$DOCS" -type f \( -iname '*.pdf' -o -iname '*.pptx' -o -iname '*.drawio' \
  -o -iname '*.vsdx' -o -iname '*.png' -o -iname '*.svg' \) \
  -not \( $SLOTS \) | head
#   found in standards/ (or arquitetura/) or at the root of docs/ ⇒ should go to presentations/ or reference/ (dim 2 smell)
# Slot BINARY WITHOUT sidecar/extract: <source>.pdf/.pptx/... with no .md alongside
[ -n "$DOCS" ] && for b in $(find "$DOCS" \( $SLOTS \) -type f \( -iname '*.pdf' -o -iname '*.pptx' \
  -o -iname '*.drawio' -o -iname '*.vsdx' \) 2>/dev/null); do \
  [ -e "${b%.*}.md" ] || grep -rqlF "$(basename "$b")" "$(dirname "$b")"/*.md 2>/dev/null \
    || echo "NO-SIDECAR  $b"; done | head
#   no .md alongside NOR cited in a folder index ⇒ the agent would have to ingest the binary (vision, ~7x tokens)
#   — extract for what governs a technical decision; folder index for what is just a reference file
# SIDECAR without provenance (missing binary:/source/updated) or marked as current (extract ≠ contract)
[ -n "$DOCS" ] && for f in $(find "$DOCS" \( $SLOTS \) -name '*.md' -not -iname 'README.md' 2>/dev/null); do \
  head -12 "$f" | grep -qiE '^\s*binary\s*:' || echo "SIDECAR-NO-SOURCE  $f"; \
  head -12 "$f" | grep -qiE '^\s*authority\s*:\s*current' && echo "SIDECAR-CURRENT!  $f"; done | head
# Missing audience+provenance LABEL: .md doc in docs/ without `audience`/`authority` in frontmatter
[ -n "$DOCS" ] && for f in $(find "$DOCS" -name '*.md' -not -iname 'README.md' 2>/dev/null); do \
  head -20 "$f" | grep -qiE '^\s*(audience|authority)\s*:' || echo "NO-LABEL  $f"; done | head
#   (the label may be at the FOLDER level — home README/index; only a smell if neither the doc nor the home has it)
# CONVERGENCE: docs/ home that matches NO canonical home (neither by canonical name,
#   nor by a known variant, nor by what Step 0 derived)
[ -n "$DOCS" ] && for d in $(find "$DOCS" -mindepth 1 -maxdepth 1 -type d 2>/dev/null); do \
  b=$(basename "$d"); case "$b" in \
    standards|decisions|vision|backlog|guides|reference|catalog|communications|presentations|\
    arquitetura|architecture|adr|todo|catalogo_dados|dominio|domain|\
    comunicados|comunicacao|comunicacoes|avisos|\
    apresentacoes|diagramas|normativos|diagrams|agents) ;; \
    *) [ "$d" = "$ARCH_DIR" ] || [ "$d" = "$ADR" ] || [ "$d" = "$BACKLOG" ] \
       || [ "$d" = "$CATALOG" ] || [ "$d" = "$DOMAIN" ] \
       || echo "NO-HOME  $d"; ;; \
  esac; done | head
#   NO-HOME ⇒ either a legitimate home to add to the taxonomy, or material in the wrong quadrant
# NON-CONVERGENCE / TWO-HOMES: home in a VARIANT NAME when the canonical already exists, OR both coexisting
for pair in "standards:arquitetura architecture" "decisions:adr" "catalog:catalogo_dados dominio domain" \
            "communications:comunicados comunicacao comunicacoes avisos" "presentations:apresentacoes" ; do \
  canon=${pair%%:*}; vars=${pair#*:}; have_canon=0; [ -d "$DOCS/$canon" ] && have_canon=1; \
  for v in $vars; do [ -d "$DOCS/$v" ] && { \
    [ "$have_canon" -eq 1 ] && echo "TWO-HOMES  $canon AND $v (migrate $v → $canon, do not duplicate)" \
                            || echo "VARIANT  $v → canonical $canon (propose migration, with OK)"; }; done; done
# DIRECTED COMMUNICATION (communications/ home) — PENDING measurement vs. fixtures (no Bash in this context)
# loose communication outside its home: notice/incident/announcement md at the ROOT of docs/ or in guides/standards/
[ -n "$DOCS" ] && grep -rliE '^\s*\*?\*?(comunicado|escopo|status|impacto|público|público afetado|incidente)\b' \
  "$DOCS" --include='*.md' 2>/dev/null | grep -vE "/communications/" | head
#   md that looks like a communication (escopo/status/impacto header) outside communications/ ⇒ communication outside its home
# channel WITHOUT template: the repo communicates on a channel but communications/templates/<channel>.md is missing
[ -n "$DOCS" ] && { [ -d "$DOCS/communications" ] && ! ls "$DOCS"/communications/templates/*.md >/dev/null 2>&1 \
  && echo "CHANNEL-NO-TEMPLATE  $DOCS/communications has no templates/<channel>.md"; }
# communication WITHOUT scannable header: file in communications/archive/ without the fixed header fields
[ -n "$DOCS" ] && for f in $(find "$DOCS"/communications/archive -name '*.md' -not -iname 'README.md' 2>/dev/null); do \
  head -20 "$f" | grep -qiE '\b(status|impacto|ação necessária)\b' || echo "NO-HEADER  $f"; done | head
```

Index/taxonomy detail lives in [docs-taxonomy.md](docs-taxonomy.md); a variant name is
a **migration** candidate (with OK), never renamed without confirmation. **The
`communications/` greps above are PENDING measurement vs. fixtures** (no Bash in this
context) — tracked in the project's evolution log (maintainers only). Complete doctrine (convergence,
audience+provenance label, sidecar/extract, directed communication): **dim 2** in
[dimensions-template.md](dimensions-template.md).

### 6b. Trigger collision + toolset bloat

The greps **list candidates** (skills whose description shares a strong keyword, or
name+verb clusters on the same artifact); who decides collision × bloat is reading + the
should-trigger test.

```bash
# collision/bloat candidates: the same domain keyword in description/when_to_use of >1 skill
for kw in "claude.md" "backlog" "arquitetura" "task" "schema" "commit" "plan"; do
  n=$(grep -rliE "(description|when_to_use):.*$kw" .claude/skills/*/SKILL.md 2>/dev/null | wc -l)
  [ "$n" -ge 2 ] && { echo "== '$kw' in $n skills =="; \
    grep -rliE "(description|when_to_use):.*$kw" .claude/skills/*/SKILL.md; }
done
#   2+ skills on the same keyword WITHOUT a clause that separates them ⇒ latent false-trigger
# BLOAT candidates (overlapping scope): clusters of skills whose NAME and action verb
# converge on the same artifact (e.g.: audit/check/lint/sync of "claude-md") — reading decides
ls -d .claude/skills/*/ 2>/dev/null | sed 's#.*/skills/##; s#/$##' | sort
#   names that repeat the same target noun with different verbs (drift/link/enhance/sync
#   of claude-md; plan-*; bundle-*) ⇒ cluster candidate for consolidation, not for +1 skill
```

**Collision × bloat (reading):** apply the **toolset test** — distinct scopes, only
the keyword collides ⇒ **collision** (fix = exclusion clause); scopes cover the same
work ⇒ **bloat** (fix = consolidate). Complete doctrine: **dim 6** in
[dimensions-template.md](dimensions-template.md).

### 7b. Sub-agent least-privilege + home selection

The grep **lists candidates** for the critical `tools`-omitted smell (inheriting all
tools) and for a vague return contract; home selection is reading.

```bash
# implicit inheritance candidates: agent WITHOUT tools or disallowedTools in frontmatter
for f in .claude/agents/*.md; do
  [ -e "$f" ] && { grep -qE '^(tools|disallowedTools):' "$f" || echo "NO-TOOLS  $f"; }; done
#   without the field, the sub-agent inherits ALL parent tools ⇒ breaks least-privilege
# read-only audit candidates without a cheap profile (model/permissionMode)
for f in .claude/agents/*.md; do
  [ -e "$f" ] && { grep -qE '^model:' "$f" || echo "NO-MODEL  $f"; }; done
# return-that-floods candidates: body instructs to return the read content instead of condensing
grep -rniE 'devolv[ae].*(conteúdo|arquivos?|log|tudo|completo)|retorn[ae].*(dump|na íntegra|todo o)' \
  .claude/agents/*.md 2>/dev/null
# opaque identifier in the return (should be file:line/slug)
grep -rniE '\b(uuid|hash|id interno|internal id)\b' .claude/agents/*.md 2>/dev/null
#   absence of a "Return format"/"condensed summary" block in the body = vague contract smell
for f in .claude/agents/*.md; do
  [ -e "$f" ] && grep -qiE 'formato de retorno|return format|sumário|summary|condensad' "$f" \
    || echo "NO-RETURN-CONTRACT  $f"; done
```

**Return contract (reading):** if the observed return size is close to the context
consumed, it became a read proxy ⇒ Drifted/Partial. **Home selection (no grep):**
skill (operator directs each step) × sub-agent (output would flood the parent) ×
command (manual shortcut) × hook (deterministic enforcement). Complete doctrine: **dim
7** in [dimensions-template.md](dimensions-template.md).

### 8b. Lifecycle hooks + exit semantics

The greps **list candidates**; who decides is the reading of `settings.json` + the
scripts.

```bash
# presence of the 3 knowledge lifecycle hooks (absence = smell)
grep -nE '"SessionStart"|"Stop"|"ConfigChange"|"InstructionsLoaded"' \
  .claude/settings.json .claude/settings.local.json 2>/dev/null
grep -nE '"matcher"[[:space:]]*:[[:space:]]*"compact"' .claude/settings.json 2>/dev/null  # SessionStart compact re-injects after /compact
# Stop hook WITHOUT loop guard (should check stop_hook_active; cap = 8 blocks)
for f in $(sed -n 's/.*\(\.claude\/hooks\/[A-Za-z0-9_.-]*\).*/\1/p' .claude/settings.json 2>/dev/null | sort -u); do
  [ -e "$f" ] && grep -lq 'stop_hook_active' "$f" || echo "NO-GUARD?  $f"; done
# blocking hook with exit 1 (warns but does NOT block — should be exit 2)
grep -rnE '\bexit[[:space:]]+1\b' .claude/hooks/ 2>/dev/null
# --- WIRING: a hook only RUNS if it is wired in settings.json --- (PENDING measurement vs. fixtures)
# ORPHAN: script in .claude/hooks/ WITHOUT any entry in settings.json (inert, never fires)
WIRED=$(sed -n 's/.*\(\.claude\/hooks\/[A-Za-z0-9_.-]*\).*/\1/p' \
  .claude/settings.json .claude/settings.local.json 2>/dev/null | sort -u)
for f in .claude/hooks/*.py .claude/hooks/*.sh; do [ -e "$f" ] || continue; \
  case "$f" in *config.json) continue;; esac; \
  echo "$WIRED" | grep -qF "$f" || echo "HOOK-ORPHAN  $f (in hooks/ but not wired in settings.json ⇒ inert)"; done
# DANGLING: entry in settings.json pointing to a script that does NOT exist
for f in $WIRED; do [ -e "$f" ] || echo "HOOK-DANGLING  $f (wired in settings.json but the script does not exist)"; done
# --- scripts/ HOME (executable logic that the surface invokes — crosses dim 1/9) --- (PENDING measurement vs. fixtures)
# organization by purpose: scripts/ exists but without a purpose subfolder (single bag)?
[ -d scripts ] && { ls -d scripts/ci scripts/checks scripts/maintenance scripts/dev 2>/dev/null \
  | grep -q . || echo "SCRIPTS-SINGLE-BAG  scripts/ has no purpose subfolder (ci/checks/maintenance/dev)"; }
# scripts loose at the ROOT of the repo (outside scripts/ and src/) — no purpose home
ls *.py *.sh 2>/dev/null | grep -vE '^(setup|conftest)\.py$' \
  | sed 's/^/SCRIPT-AT-ROOT  /'
# hook with INLINE BUSINESS LOGIC (long command) instead of calling a scripts/… (docs say: "a separate script file that the hook calls")
grep -nE '"command"[[:space:]]*:[[:space:]]*"[^"]{120,}"' .claude/settings.json 2>/dev/null \
  | sed 's/^/HOOK-INLINE-LOGIC?  /'
# script invoked by hook/command/CI that does NOT exist (dangling on the repo script side)
#   -m module: scripts.ci.deploy → scripts/ci/deploy.py ; direct path: scripts/checks/x.py
for ref in $(grep -rhoE 'scripts\.[A-Za-z0-9_.]+|scripts/[A-Za-z0-9_./-]+\.(py|sh)' \
    .claude/ Makefile .github/ 2>/dev/null | sort -u); do
  case "$ref" in
    scripts.*) p="$(echo "$ref" | tr '.' '/').py" ;;   # -m module form
    *)         p="$ref" ;;                              # direct path form
  esac; [ -e "$p" ] || echo "SCRIPT-NONEXISTENT  $ref → $p (invoked but absent)"; done
# scripts/ README map lies vs. disk? (module on disk without a line in README, or vice versa) — manual reading
[ -f scripts/README.md ] || { [ -d scripts ] && echo "SCRIPTS-NO-MAP  scripts/ without a README map"; }
```

Read: orphan (script without entry, inert) × dangling (entry without script) × wrong
event/matcher; blocking uses `exit 2` (not `exit 1`); every `Stop` checks
`stop_hook_active`; and the **`scripts/` home** organized by purpose (no single bag /
loose-at-root), the hook calling the script (not inline logic), the invoked
`scripts/<…>` existing, and the README map in sync with the disk. **The wiring and
`scripts/` greps are PENDING measurement vs. fixtures** — no Bash in this context; see
the spine's review queue. Complete doctrine (exit semantics, 3 lifecycle hooks,
wiring/scope/precedence): **dim 8** in [dimensions-template.md](dimensions-template.md); the
`scripts/` organization: [scripts-taxonomy.md](scripts-taxonomy.md).

### 9b. Legacy command × skill + name collision

`.claude/commands/<name>.md` is **legacy**; `.claude/skills/<name>/SKILL.md` is the
**recommended** form (only the skill auto-triggers). The greps **list candidates**; migration
is reading applying the criterion.

```bash
# migration candidates: legacy command >50 lines (needs references/) — criterion (b)
for f in .claude/commands/**/*.md .claude/commands/*.md; do
  [ -e "$f" ] && { n=$(wc -l < "$f"); [ "$n" -gt 50 ] && printf '%5s  %s\n' "$n" "$f"; }; done 2>/dev/null
# migration candidates: command that references external files (@file / !`cmd`) — criterion (b)
grep -rlnE '@[A-Za-z0-9_./-]+|!`' .claude/commands/ 2>/dev/null
# basename collision: two .md files with the same name in different subfolders of commands/
find .claude/commands -name '*.md' 2>/dev/null -exec basename {} \; | sort | uniq -d
#   duplicate basename ⇒ /name is ambiguous (the subfolder does NOT become part of the command name)
# bundled skill shadowing: custom command with the name of a built-in skill (code-review, verify, ...)
for n in code-review verify; do
  [ -e ".claude/commands/$n.md" ] && echo "SHADOW  .claude/commands/$n.md shadows the bundled skill /$n"; done
```

Migrate command → skill for auto-trigger / >50 lines / multi-repo; keep a command only as
the manual shortcut for a side-effect action. Complete doctrine: **dim 9** in
[dimensions-template.md](dimensions-template.md).

### 12. Boundary doctrine

No grep can find semantic contradiction — it is comparative reading, the core of the
method (full recipe: boundary table × 3 artifacts, Diátaxis quadrant test, semantic DRY).
The grep below only **lists candidates** for duplicated rules.

```bash
# duplicated rule candidates: the same anchor directive in >1 boundary artifact
grep -rniE 'define [a-z]+|fonte (única|da verdade)|single source|nunca edit|gerado pelo ci|auto-?gerado' \
  CLAUDE.md "$ARCH_INDEX" "$DOMAIN" 2>/dev/null
#   2+ occurrences with divergent wording ⇒ choose the canonical home, link from the others
```

Complete doctrine: **dim 12** in [dimensions-template.md](dimensions-template.md).

### 14b. Actionable error + poka-yoke in executables

Audits the **other end** of guardrails: hooks/scripts/tools that the agent triggers
speak through their failure message (applies to the package payloads **and** to
pre-existing executables). The greps **list candidates**; who decides if the message is
actionable is the reading of the script.

```bash
# opaque error candidates: hook script that exits with an error WITHOUT writing explanatory stderr
for f in .claude/hooks/* $(sed -n 's/.*\(\.claude\/hooks\/[A-Za-z0-9_.-]*\).*/\1/p' .claude/settings.json 2>/dev/null | sort -u); do
  [ -e "$f" ] || continue
  grep -qE '(sys\.stderr|>&2|console\.error|print.*file=sys\.stderr)' "$f" || echo "NO-STDERR?  $f"
done
#   exits with non-zero but never writes to stderr ⇒ the agent receives a silent code, not the fix
# raw traceback leaking to the agent candidates (no try/except that translates to a message)
for f in .claude/hooks/*.py; do
  [ -e "$f" ] && { grep -qE '(try:|except )' "$f" || echo "NO-TRANSLATION  $f"; }; done 2>/dev/null
# missing poka-yoke candidates: tool/script that accepts a RELATIVE path where an absolute would prevent errors
grep -rnniE 'relative ?path|caminho relativo|os\.path\.relpath|\./[a-z]' .claude/hooks/ 2>/dev/null
```

The failure message must state **what is missing + how to fix it** (not `KeyError`/silent
stack trace); a blocking `exit 2` (8b) needs explanatory stderr; where a parameter
accepts a relative path, prefer absolute/enum (poka-yoke). Complete doctrine: **dim 14**
in [dimensions-template.md](dimensions-template.md).

## Installation reminder

Detection is the first half; filling the gap means **installing the package payload**
([installation.md](installation.md)). No command here edits anything (read-only); installation
happens in Step 5 of [SKILL.md](../SKILL.md), **with confirmation**, copying from
[../assets/](../assets/) and adapting to the derived form.
