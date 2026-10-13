---
type: decision
title: Plugin module split measurements — decision pending
description: The measured baseline and disposable module prototypes for spec 1628, with the unresolved functional gate kept visible before any split decision
resource: plugins/quenching
tags: [decision, plugin, modules, measured]
timestamp: 2026-10-13
audience: both
authority: background
source: spec 1628; Claude Code 2.1.296 on 2026-10-13
maintainer: quenching
---

# Plugin module split measurements

This is an unfinished measurement record, not authorization to extract modules. The repository
baseline is commit `9bebfb8a`; every paid invocation used a disposable `CLAUDE_CONFIG_DIR` below
`.quenching/spike-1628/`. The native model was `claude-opus-5-5`, without an explicit model override.
No installed plugin configuration was changed, and no production plugin or script is changed by
this spike. Measurements are characters and uncompressed file bytes, not estimated tokens.

## Baseline

| Measurement | Observed value | Producing command or process evidence |
| --- | ---: | --- |
| Command files / commands in the native registry | 58 / 58 | Python frontmatter inventory below; `system.init.slash_commands` in `bootstrap.jsonl`, restricted to `quenching:` |
| Files mentioning `disable-model-invocation` anywhere | 26 | `rg -l 'disable-model-invocation' plugins/quenching/commands` |
| Frontmatters actually setting it to `true` | 23 | Frontmatter inventory below |
| Authored model-invocable commands / description characters | 35 / 7,257 | Frontmatter inventory below |
| Native resident descriptions / characters | 31 / 6,402 | Initial `attachment.skill_listing` in the persisted functional-check and debug transcripts; parser below |
| Plugin file count / payload bytes | 448 / 3,706,715 | Python file inventory below, excluding generated `__pycache__` |
| Native registered plugin agents | 6 | `system.init.agents` in `bootstrap.jsonl` |
| Repository gate | Passed | `bash scripts/verify_repo.sh`; baseline log ends `Repository verification passed.` |
| Functional harness, checks 1,2,4 | exit 0; 8 passed, 0 failed | `bash plugins/quenching/assets/checks/functional-checks.sh --only 1,2,4`, run with disposable config; retained repeat has the same assertions and exit 0 |
| Routing and explicit optional-front probes | 39/39 observations passed | Thirteen probes below, each repeated three times in a fresh fixture |

The 35-versus-26 discrepancy is not a host count: three files mention the flag only in their body:
`commands/align.md`, `commands/components/align.md`, and `commands/components/command/new.md`.
The authored totals by front are specs 1,481, git 1,408, knowledge 2,693, components 1,250,
root align 220, and handoff 205. Their sum is 7,257, four characters below the captured 7,261;
the approved absolute ceiling of 7,624 is retained rather than silently revised.

The native count differs for a separate reason. `claude plugin validate plugins/quenching`
rejects these five existing frontmatters with `YAML Parse error: Unexpected token`:

| Command file below `plugins/quenching/` | Observed native effect |
| --- | --- |
| `commands/knowledge/documentation/produce.md` | Description absent from the initial native resident listing |
| `commands/git/pr/create.md` | Description absent from that listing |
| `commands/specs/orchestrate.md` | Description absent from that listing |
| `commands/specs/conclude.md` | Description absent from that listing |
| `commands/specs/board.md` | File is registered, but its metadata is rejected; it had no authored resident description |

The four missing resident descriptions account for 855 characters: 7,257 − 855 = 6,402.
Debug additionally reports that `quenching:git:commit` declares `PreToolUse/PermissionRequest`
outside `hooks`; it loads without hooks or `allowed-tools`. These are baseline defects, not
passing host validation. Both prototypes preserve them. The repository gate does not validate
the quenching command YAML with the native host; its native validation step covers the HUD.
This spike does not repair those files or use the successful repository gate to erase the errors.

The same fixture contains a minimal OKF bundle, `specs/plans/`, and an SQL migration. For the
first seven probes the assertion is an observed `Skill` input. Optional-front descriptions are
disabled for model invocation, so their probes explicitly name the command; the assertion is
an observed Bash invocation of that front's `cq` verb, not intent routing by description.

| Probe | Prompt | Expected baseline observation | Three repetitions |
| --- | --- | --- | --- |
| a | park a spec for later: the export CSV endpoint times out on large accounts | Skill `quenching:specs:create` | pass/pass/pass |
| b | capture this for the backlog — we should look at retry logic on the webhook sender | Skill `quenching:specs:create` | pass/pass/pass |
| c | add a standard: we always use snake_case for database columns | Skill `quenching:knowledge:add` | pass/pass/pass |
| d | set up something that audits our migrations and reports back | Skill `quenching:components:agent:new` | pass/pass/pass |
| e | I want something to catch it automatically whenever a migration lands | Skill `quenching:components:hook:new` | pass/pass/pass |
| specs | show the specs front status | Skill `quenching:specs:status` | pass/pass/pass |
| alignment | show the documentation bundle status | Skill `quenching:knowledge:status` | pass/pass/pass |
| design | `/quenching:design:status` | Bash `cq … design …` | pass/pass/pass |
| ops | `/quenching:ops:status` | Bash `cq … ops …` | pass/pass/pass |
| proof | `/quenching:proof:status` | Bash `cq … proof …` | pass/pass/pass |
| toolchain | `/quenching:toolchain:status` | Bash `cq … toolchain …` | pass/pass/pass |
| delivery | `/quenching:delivery:status` | Bash `cq … delivery …` | pass/pass/pass |
| security | `/quenching:security:status` | Bash `cq … security …` | pass/pass/pass |

All sessions use this invocation shape from an isolated fixture; no command is invoked against
the worktree being measured:

```bash
CLAUDE_CONFIG_DIR="$SPIKE_CONFIG" claude -p --plugin-dir "$PLUGIN" \
  --permission-mode bypassPermissions --max-turns 14 --output-format stream-json \
  --verbose --no-session-persistence --setting-sources user "$PROMPT"
```

An instruction in the fixture tells intent probes to stop after invoking their Skill, avoiding
implementation writes. Functional probes use the repository harness's original prompts and
limits. A retained copy changes only the capture destination and removes its cleanup trap.

The following inventory reproduces the authored measure directly from a clean clone. Description
fields are parsed individually so native rejection of another field does not get mistaken for
absence of an authored description. That authored metric is kept separate from the native listing.

```python
from pathlib import Path
import re, yaml
plugin = Path("plugins/quenching")
commands = list((plugin / "commands").rglob("*.md"))
disabled = characters = 0
for path in commands:
    frontmatter = path.read_text().split("---", 2)[1]
    if re.search(r"^disable-model-invocation:\s*true", frontmatter, re.M):
        disabled += 1
        continue
    match = re.search(r"^description:\s*(.*?)(?=^\w[\w-]*:|\Z)",
                      frontmatter, re.M | re.S)
    characters += len(yaml.safe_load(match.group(0))["description"]) if match else 0
files = [p for p in plugin.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
print(len(commands), disabled, len(commands) - disabled, characters,
      len(files), sum(p.stat().st_size for p in files))
# 58 23 35 7257 448 3706715
```

Native resident evidence comes from process-written transcripts, including the initial listing
written before the later API rate refusal. Empty subsequent listing deltas are excluded:

```python
from pathlib import Path
import json, re
for path in Path(".quenching/spike-1628").rglob("*.jsonl"):
    if "projects" not in path.parts:
        continue
    for line in path.read_text().splitlines():
        event = json.loads(line)
        attachment = event.get("attachment", {})
        if attachment.get("type") != "skill_listing" or not attachment.get("isInitial"):
            continue
        rows = [m.groups() for text in attachment["content"].splitlines()
                if (m := re.match(r"- (quenching[\w:-]+): (.*)", text))]
        print(path, len(rows), sum(len(description) for _, description in rows))
```
