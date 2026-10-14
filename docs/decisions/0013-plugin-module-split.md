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


## Host facts

All facts below are observed on Claude Code 2.1.296. Minimal plugins, their markers, their
marketplace, and their configuration are below `.quenching/spike-1628/facts/` and `config/`.

| Fact | Command / captured process observation | Result | Consequence for the tested forms |
| --- | --- | --- | --- |
| Dependency declaration and auto-install | Consumer manifest `{"name":"quenching-consumer","version":"0.0.1","dependencies":["quenching-base"]}`; `claude plugin marketplace add "$SPIKE/facts"`; `claude plugin install quenching-consumer@spike-1628` | `Successfully installed … (+ 1 dependency: quenching-base)`; `claude plugin list --json` shows both enabled at user scope | The host genuinely supports installation dependencies; absence of this capability does not kill B |
| Auto-dependency pruning | `claude plugin uninstall quenching-consumer@spike-1628`; `claude plugin prune`; then `claude plugin prune -y` | First identifies one orphan and asks for `-y` outside a TTY; confirmed invocation prints `Removed 1 auto-installed plugin: quenching-base` | Dependencies have a reversible lifecycle within the throwaway config |
| Duplicate binary order | Fresh session with `--plugin-dir facts/quenching-specs --plugin-dir facts/quenching-base`; observed Bash `type -a cq; printf "PATH=%s\n" "$PATH"; cq` | Two entries, specs first, base second; running `cq` prints `quenching-specs` | A survives only by shipping one PATH shim; copying a shim into every module fails the binary invariant |
| Cross-plugin reference expansion | Consumer body tells Read to open the base's absolute `shared.md`; that fixture file cites the `${CLAUDE_PLUGIN_ROOT}` token followed by `/marker.txt`; captured Read and Bash inspect it and both real marker files | Placeholder remains literal in the Read result; shell `CLAUDE_PLUGIN_ROOT` is empty; both marker contents exist, with no automatically resolved citation root | Dependencies do not export another plugin's root or substitute text returned by Read. Pure B cannot preserve own-root citations to files shipped only in its base |
| Flat and nested command ids | Native `system.init.slash_commands`; direct `/quenching-specs:specs:develop` reads the specs marker | Both `quenching-specs:develop` and `quenching-specs:specs:develop` are registered; the nested body reads the intended absolute marker | Both naming forms are supported; a rename is a cost, not a veto |
| Agent id across plugins | Fresh session with specs and consumer; captured Agent input `subagent_type=quenching-specs:root-probe` | Agent reads the specs plugin's absolute marker and returns `SPECS_ROOT_MARKER` | Cross-plugin agents are addressed by their owner's plugin namespace |

The nested/flat ids and agent-id tests are separate halves of the fifth host question; the
extra pruning row is part of the dependency question, not an additional requirement.

**Disposition of B:** the pure host-dependency form is rejected for the existing citation layout.
The dependent's `${CLAUDE_PLUGIN_ROOT}/assets/references/...` points at the dependent, not the base;
putting the reference only in the base leaves that path missing. The measured cross-plugin Read
also receives an unexpanded placeholder, so it provides no native bridge. A new root locator,
rewritten read prologue, or resource export could make a different B work; none was proved here.
This is a limit of the tested form, not a claim that shared-base plugins are impossible in general.
Copying those resources into dependents instead is the A form tested below.

A and C survive these host facts. Installed targets and their real plugin state remain untouched.
The dependency marketplace's source must start with `./`; the initial `../` fixture was rejected
before installation, then replaced with a marketplace at the common parent and `./<plugin>` sources.


## Partition

A has eight installable modules in three tiers. Source ownership remains specs for session;
this conservative generated-core prototype also copies session support into alignment so its
unchanged components parser remains self-contained. The specs module copies components support
for section reading and the session mount, but exposes no components commands. These support
copies are priced in the payload, not hidden as a supposedly minimal extraction.

| Module | Command fronts | Python subpackages physically shipped |
| --- | --- | --- |
| `quenching-specs` | specs, git, handoff; all six agents | common, specs, git, session, components |
| `quenching-align` | knowledge, components, root align | common, knowledge, components, generated session support |
| `quenching-design` | design | common, design |
| `quenching-ops` | ops | common, ops |
| `quenching-proof` | proof | common, proof, ops |
| `quenching-toolchain` | toolchain | common, toolchain |
| `quenching-delivery` | delivery | common, delivery |
| `quenching-security` | security | common, security |

The proof module carries ops code to satisfy its imports, without exposing ops commands. Only
specs owns `bin/cq`; every other module has an empty `bin/`. The disposable `assets/bin/cq`
prototype extends the Python package search path from those plugin bin directories that the
host places on PATH, allowing the single executable to import enabled optional subpackages.
That loader is prototype code, not an established shipping rule or an implementation in this PR.

Reference directories are copied by transitive citation closure. The shared closure S is:
`align`, `components-command-new`, `git`, `knowledge-add`, `knowledge-align`, `knowledge-import`,
`specs-align`, `specs-conclude`, `specs-develop`, `specs-execute`.

| Module | Reference directories physically shipped |
| --- | --- |
| specs | S plus `specs-create` |
| alignment | S plus `components-command-eval`, `components-harness-align`, `front-align`, `knowledge-documentation`, `knowledge-import-memory` |
| design | S plus `design-align`, `front-align` |
| ops | S plus `ops-align`, `front-align` |
| proof | S plus `proof-align`, `front-align` |
| toolchain | S plus `toolchain-align`, `front-align` |
| delivery | S plus `delivery-align`, `front-align` |
| security | S |

Other asset directories are conservatively copied to each module. Tests and agents live only
in specs; the full unchanged test payload is included in its measured install. This deliberately
prices shared-core duplication instead of claiming an optimized extraction was proved.

Commands retain nested front suffixes: `/quenching-specs:specs:develop`,
`/quenching-specs:git:branch`, `/quenching-align:knowledge:add`, and
`/quenching-design:design:status`. Both host naming choices work, but this one preserves suffixes
and avoids collisions within alignment. The existing command surface has 350 `/quenching:`
literals in 57 files (`re.findall(r"/quenching:", body)` over the 58 command files); changing
those prefixes is an accepted migration cost. Wildcard `/quenching:*:align` prose needs a
separate explicit multi-module treatment during extraction; the spike does not pretend that
one replacement establishes every production routing rule.

C retains one plugin and all non-command assets, with unwanted command files excluded from its
loaded profile. Thus it really hides optional fronts while preserving their code payload.
C/all is byte-identical to the baseline, so its three-repeat routing evidence is shared with
that baseline instead of purchasing identical sessions again. B is not generated after the
citation-layout disposition above.

Reproduce the surviving prototypes by saving the following generator at
`.quenching/spike-1628/generate.py` and running `python3 .quenching/spike-1628/generate.py`.
It reads the source plugin, writes only inside that spike directory, and prints the static
form × arrangement measurements; native host checks are separate.

```python
import json, pathlib, re, shutil
import yaml

ROOT=pathlib.Path(__file__).resolve().parent
SOURCE=ROOT.parents[1]/'plugins/quenching'
GROUPS={'specs':['specs','git','handoff.md'],'align':['knowledge','components','align.md'],'design':['design'],'ops':['ops'],'proof':['proof'],'toolchain':['toolchain'],'delivery':['delivery'],'security':['security']}
CODE={'specs':['common','specs','git','session','components'],'align':['common','knowledge','components','session'],'design':['common','design'],'ops':['common','ops'],'proof':['common','proof','ops'],'toolchain':['common','toolchain'],'delivery':['common','delivery'],'security':['common','security']}
OWNERS={front:module for module,fronts in GROUPS.items() for front in fronts}
ARRANGEMENTS={'specs':['specs'],'specs-align':['specs','align'],'minus-design':[x for x in GROUPS if x!='design'],'all':list(GROUPS)}

def rename(text):
    def sub(m):
        front=m.group(1)
        module=OWNERS.get(front, 'specs' if front in ['orchestrator','spec-runner','spec-architect','verifier','git-steward','scout','handoff'] else 'align' if front=='align' else None)
        return 'quenching-'+module+':'+front if module else m.group(0)
    return re.sub(r'quenching:([a-z-]+)',sub,text)

def metadata(plugin):
    commands=list((plugin/'commands').rglob('*.md'));resident=chars=0
    for p in commands:
        fm=p.read_text().split('---',2)[1]
        if re.search(r'^disable-model-invocation:\s*true',fm,re.M):continue
        m=re.search(r'^description:\s*(.*?)(?=^\w[\w-]*:|\Z)',fm,re.M|re.S)
        resident+=1;chars+=len(yaml.safe_load(m.group(0))['description']) if m else 0
    files=[p for p in plugin.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    return {'commands':len(commands),'resident':resident,'characters':chars,'files':len(files),'bytes':sum(p.stat().st_size for p in files)}

def main():
    for module,fronts in GROUPS.items():
        p=ROOT/'A'/('quenching-'+module)
        shutil.copytree(SOURCE,p,ignore=shutil.ignore_patterns('__pycache__'),dirs_exist_ok=True)
        for f in (p/'commands').iterdir():
            if f.name not in fronts:
                shutil.rmtree(f) if f.is_dir() else f.unlink()
        if module!='specs':
            shutil.rmtree(p/'agents');shutil.rmtree(p/'tests');shutil.rmtree(p/'bin')
            (p/'bin').mkdir()
        manifest=json.loads((p/'.claude-plugin/plugin.json').read_text());manifest['name']='quenching-'+module
        (p/'.claude-plugin/plugin.json').write_text(json.dumps(manifest,indent=2)+'\n')
        for f in (p/'assets/bin/quenching').iterdir():
            if f.is_dir() and f.name not in CODE[module]:shutil.rmtree(f)
        refs=p/'assets/references'
        needed=set(); pending=list((p/'commands').rglob('*.md'))+list((p/'agents').rglob('*.md')) if (p/'agents').exists() else list((p/'commands').rglob('*.md'))
        for file in pending:
            for match in re.finditer(r'assets/references/([a-z0-9-]+)/',file.read_text()):needed.add(match.group(1))
        while True:
            extra={match.group(1) for folder in needed if (refs/folder).exists() for file in (refs/folder).rglob('*.md') for match in re.finditer(r'assets/references/([a-z0-9-]+)/',file.read_text())}
            if extra<=needed:break
            needed|=extra
        for f in refs.iterdir():
            if f.is_dir() and f.name not in needed:shutil.rmtree(f)
        for f in p.rglob('*.md'):f.write_text(rename(f.read_text()))
        entry=p/'assets/bin/cq';txt=entry.read_text();needle='from quenching.common.output import CQArgumentParser, USAGE'
        hook='''import pathlib
import quenching
for path_entry in os.environ.get("PATH", "").split(os.pathsep):
    package = pathlib.Path(path_entry).parent / "assets" / "bin" / "quenching"
    if package.is_dir() and str(package) not in quenching.__path__:
        quenching.__path__.append(str(package))
'''
        txt=txt.replace(needle,hook+'\n'+needle)
        entry.write_text(txt)
        (ROOT/'A'/('quenching-'+module+'.partition.json')).write_text(json.dumps({'fronts':fronts,'code':CODE[module],'reference_directories':sorted(needed),'metadata':metadata(p)},indent=2))
    for arrangement,modules in ARRANGEMENTS.items():
        p=ROOT/'C'/arrangement/'quenching';shutil.copytree(SOURCE,p,ignore=shutil.ignore_patterns('__pycache__'),dirs_exist_ok=True)
        allowed={front for module in modules for front in GROUPS[module]}
        for f in (p/'commands').iterdir():
            if f.name not in allowed:shutil.rmtree(f) if f.is_dir() else f.unlink()
    matrix={form:{arrangement:{k:sum(metadata(p)[k] for p in plugins) for k in ('commands','resident','characters','files','bytes')} for arrangement,modules in ARRANGEMENTS.items() for plugins in [[ROOT/'A'/('quenching-'+m) for m in modules] if form=='A' else [ROOT/'C'/arrangement/'quenching']]} for form in ['A','C']}
    (ROOT/'static-matrix.json').write_text(json.dumps(matrix,indent=2));print(json.dumps(matrix,indent=2))

if __name__=='__main__':main()
```


## Matrix

The completed measurements are preserved below. The initially incomplete functional gate was
resumed after the recorded reset, preserving all earlier evidence. No inconclusive check was
promoted to pass; the repeated full A harness supplied the missing observations. Repository verification is a separate repository-wide
check of the durable ADR and unchanged product; it is not the native prototype surface proof.

| Form | Arrangement | Authored cost axis | Binary axis | Install payload / visible commands | Citation axis | Routing axis | Functional surface gate | Overall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | specs | pass: 3226 chars | pass: 1 cq | 2,869,338 bytes / 22 commands | pass: 145 citation reads | not required by D4 | not run on subsets | subset process assertions pass |
| A | specs-align | pass: 7539 chars | pass: 1 cq | 4,239,597 bytes / 44 commands | pass: 338 citation reads | not required by D4 | not run on subsets | subset process assertions pass |
| A | minus-design | pass: 7539 chars | pass: 1 cq | 8,386,867 bytes / 55 commands | pass: 661 citation reads | not required by D4 | not run on subsets | subset process assertions pass |
| A | all | pass: 7539 chars | pass: 1 cq | 9,301,297 bytes / 58 commands | pass: 724 citation reads | pass: 39/39 | pass: 8/8; exit 0 on resume | pass against baseline |
| B | specs | not built | not measured | not measured | fail: native dependency does not supply the cited own-root file | not run | not run | not proved |
| B | specs-align | not built | not measured | not measured | fail: native dependency does not supply the cited own-root file | not run | not run | not proved |
| B | minus-design | not built | not measured | not measured | fail: native dependency does not supply the cited own-root file | not run | not run | not proved |
| B | all | not built | not measured | not measured | fail: native dependency does not supply the cited own-root file | not run | not run | not proved |
| C | specs | pass: 3094 chars | pass: 1 cq | 3,417,816 bytes / 22 commands | pass: 157 citation reads | not required by D4 | not run on subsets | subset process assertions pass |
| C | specs-align | pass: 7257 chars | pass: 1 cq | 3,632,411 bytes / 44 commands | pass: 282 citation reads | not required by D4 | not run on subsets | subset process assertions pass |
| C | minus-design | pass: 7257 chars | pass: 1 cq | 3,694,013 bytes / 55 commands | pass: 325 citation reads | not required by D4 | not run on subsets | subset process assertions pass |
| C | all | pass: 7257 chars | pass: 1 cq | 3,706,715 bytes / 58 commands | pass: 332 citation reads | pass: 39/39 | pass: 8/8; exit 0 | pass against baseline |

The native resident description axis is measured from initial native `skill_listing` attachments:
C/baseline all = 31 descriptions and 6,402 characters; A/all = 31 and 6,654. The 252-character
increase is **3.9362699%**, below the relative limit 6,402 × 1.05 = 6,722.1. A also passes the
independent approved authored ceiling: 7,539 ≤ 7,624. These are two different measures, both
passing; neither is substituted for the other.

Fresh persisted initial listings now directly confirm every partial arrangement: A/specs =
12 descriptions / 2,540 characters; A/specs+alignment and A/minus-design = 31 / 6,654;
C/specs = 12 / 2,438; C/specs+alignment and C/minus-design = 31 / 6,402.
Those readings match the earlier registry/listing projections. The first A/specs capture was
written before an API authentication refusal caused by the expired disposable seed; its native
listing remains direct process evidence. Updating only the disposable credential copy from the
already renewed real credential restored successful sessions on the same model.

Static cells are produced by the embedded generator. Process cells come from seven fresh
arrangement sessions. Each executed this Python check through Bash, with `roots` set to that
arrangement's absolute plugin roots. It asserts on process exit codes and actual file reads:

```python
import pathlib, os, re, subprocess, json
# roots = [absolute paths of the enabled prototype plugins]
paths = [str(pathlib.Path(p) / "cq") for p in os.environ["PATH"].split(os.pathsep)
         if (pathlib.Path(p) / "cq").is_file()]
assert len(set(paths)) == 1, paths
calls = {}
for argv in [["cq", "--version"], ["cq", "components", "--help"], ["cq", "specs", "--help"]]:
    result = subprocess.run(argv, capture_output=True, text=True)
    calls[" ".join(argv)] = result.returncode
    assert result.returncode == 0, (argv, result.stderr)
references = 0
for root in map(pathlib.Path, roots):
    for folder in ["commands", "agents", "assets/references"]:
        for path in (root / folder).rglob("*.md"):
            for target in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/(assets/references/[a-zA-Z0-9_./-]+\.md)",
                                     path.read_text()):
                assert (root / target).read_bytes(), (path, target)
                references += 1
print(json.dumps({"cq_matches": paths, "calls": calls, "citations_read": references}))
```

The single binary in A is the specs module's shim, returning version `6.4.0`. All tested
`--help` calls exit 0. Local comparison of all 448 source files to C/all confirms byte equality
(excluding generated `__pycache__`), so baseline observations supply its all-loaded row.
All thirteen A routing/load probes pass their three repetitions, with expected ids transformed
by the generator's namespace map. The optional-front Bash assertions match the same verbs as
baseline. There are no observed routing regressions under the spec's baseline-three-pass rule.

The A functional harness is a disposable copy of the original harness. Changes are limited to
its plugin-directory root, equivalent renamed expected ids, and retained captures; assertions,
prompts, turn limits, and anchoring are preserved. The initial run returned 0 but printed
2 passed / 6 inconclusive after the account limit, so it was not treated as green. On
2026-10-14 01:16 UTC (2026-10-13 in the declared target timezone), the full repeated
`--only 1,2,4` harness returned **0 with 8 passed, 0 failed, no inconclusive checks**.
Each of its four terminal native results is successful, on `claude-opus-5-5`.
Retained output is `A-functional-resume.log`; native captures are in `functional-A-resume/`.
The earlier failures and captures remain retained.

| Benefit comparison against C | Measured result | What it establishes |
| --- | --- | --- |
| A, specs only | 2,869,338 vs 3,417,816 bytes: 548,478 fewer, or 16.0476164% | Actual code/reference absence yields an installation benefit the front-hiding C prototype does not supply |
| A, all modules | 9,301,297 vs 3,706,715 bytes | Generated support duplication is substantial; the prototype does not claim an all-loaded size benefit |
| A, everything except design | 8,386,867 vs 3,694,013 bytes | Removing design saves 914,430 bytes from A's own full install, but A is still larger than C in this arrangement |
| B, pure native dependencies | Citation axis failed before prototype generation | No measured installation benefit; a future locator is unproved |
| C | Same exposed fronts with one plugin; assets and code remain installed | It supplies visibility control, preserving names and avoiding duplicated payload |

## Verdict

**Needs human / pending; neither go nor no-go is earned.** A has a measured installation benefit,
passes both description-cost measures, and has no observed routing, binary, or citation
regression. The missing functional observations prevent the required parity proof. The
missing observations are account capacity, not evidence that A's implementation fails.
The B disposition does not make a locator-based variant impossible.

Keep 1634, 1635 and the deployment shape of 1637 held. Do not abandon extraction members on
this partial record, propagate a split/no-split verdict into epic 1627, or mark spec 1628 done.
The four on-disk Open Decisions and tasks 3.1/3.2 remain open. Working choices of nested names,
specs as the sole cq owner, alignment as root-align owner, and specs as handoff owner remain
prototype choices until the full gate and decision are settled. A go would still have to state
the installed-target migration and update obligations of plugin-layout, command-surface,
versioning-release, and the Codex translator; no shipping rule is changed here.

### Capacity and evidence retention

Before the capacity pause, the spike had made **103 fresh CLI sessions**, below its limit of **120 sessions**. At that pause, aggregate measured
list-price cost from deduplicated native result/cost-state records was **US$22.4056688**; this is
not a charge or a currency conversion. All measured result model keys are `claude-opus-5-5`.
Five terminal records contain the account-limit response: the four A functional sessions and
the debug attempt; the latter and three completely blocked functional sessions cost zero.
The native response says `You've hit your session limit · resets 7:10pm (America/Sao_Paulo)`;
the API error is HTTP 429. No retry-after interval was observed, and no further Claude calls
were started until the orchestrator resumed the run after the recorded reset.

Retained evidence lives under `.quenching/spike-1628/`: `captures/*.jsonl`, native transcripts
under disposable configs, `runtime-listings.json`, `static-matrix.json`, partition JSON files,
the original and retained functional logs, `functional-A/*.jsonl`, the repository gate logs,
and `totals.json`. The original functional harness deletes its temporary boxes; its four
persistent native transcripts retain their observations and cost-state records. No raw
credential or full transcript is versioned; the durable tables record the pertinent observations.
The resumed pass used the planned six partial resident snapshots and four full functional
sessions. Total across both passes is **113 fresh CLI sessions / 120**, and the deduplicated
native list-price total is **US$24.2255896**, leaving seven sessions unused. The first resumed
call cost zero and reported a revoked expired-seed OAuth token; it still wrote the A/specs
initial listing. The next call used the already renewed credential in a disposable copy and
succeeded. No owner reauthorization, installed-config change, new routing suite, or larger
session ceiling was required. `totals-resumed.json` and `runtime-resume-listings.json` retain
the final aggregates and snapshot source paths; the original totals remain intact.
