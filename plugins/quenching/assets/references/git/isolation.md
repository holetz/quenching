# Taking isolation, and recording it

How a checkout gets onto its own branch or worktree before code is written, and what gets recorded
once it has — the offer's shape, the default names, and the two records that survive it: the
`branch:` frontmatter record and the branch's own description line. Read
[conventions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/git/conventions.md) first: the read-if-present
rule and the two prohibitions bind here too.

## Contents

`cq components read <this file>` returns the heading index; `--sections` addresses one.

## Isolation happens on the way into a build

<!-- rules -->

Isolation was a command of its own for one release, offered at any stage. It is now a **step inside**
`/quenching:specs:execute`, taken once, before the first task is written — and offered only when the
session is standing on the repository's base branch:

| Where the session stands | What `execute` does |
| --- | --- |
| **on** the spec's work ref | nothing — the spec is isolated, and the loop starts |
| on any other non-base branch | **adopts it** as `work`, stamps `branch:`, and starts the loop |
| on the base, work ref alive and unclaimed | offers to **take** it — worktree over it, or checkout — and stamps nothing |
| on the base, no work ref | offers worktree · branch · in place, and stamps whichever was taken |

Standing anywhere but the base means the human already answered the isolation question at checkout,
so asking again buys nothing and costs the turns it takes. Isolation stays optional, is recommended
before building, and is never imposed.

**Isolated means "this checkout is on the work ref", never "the ref exists".** The two come apart in
one ordinary case — the base checked out, `plan/<slug>` sitting one branch over from an earlier
session, nobody holding it — and treating existence as the answer sends the loop to build and commit
onto the base, which is precisely what the offer is for. The work ref itself is the `branch` record's
`work` when one is stamped, else `plan/<slug>`; a live ref held by another worktree is a **stop**,
not an offer, because two checkouts building one spec fork it.

`/quenching:specs:create` and `/quenching:specs:develop` take no branch at all — they write into
`plans/` and stay wherever they were run. That is a narrowing from the retired command, and the
trade is deliberate: the offer costs a confirmation, and the stage where it reliably pays is the one
about to write code.

**Asking "am I isolated?" writes nothing and is answered elsewhere.** `cq specs next --front`
reads the live ref and reports it, and demotes a spec whose branch is checked out somewhere else.
`/quenching:specs:status` reads the frontmatter records and deliberately never asks git.

**Merging is not here.** It stays inside `/quenching:specs:conclude`, behind that command's review and
archive gates — a merge invocable on its own could run against a spec nobody reviewed and nothing
archived, and would have to duplicate every refusal `conclude` already owns.

<!-- rationale -->

**On `plan/<slug>` as the default name.** A branch named to it is greppable against `cq specs list`,
and `git branch --list 'plan/*'` is the list of work cut by the default. A human who already checked
out `fix/isolate-flow` or `123-my-branch` before running `execute` gets that branch recorded, not a
second one cut beside it.

**On putting the worktree beside the repo.** Inside the repo it lands in the tree the spec is about
to change, and shows up in every `git status`, every glob, and every checker this plugin runs. A
worktree leaves the main checkout untouched, which is what lets several specs be built at once and
what keeps satisfying the clean tree the loop demands of itself. A recommendation that changes from
repo to repo cannot be documented in one sentence, and guessing somebody else's build is how a
recommended path becomes a silent trap. So choosing Branch is a decision the human read rather than
a discovery at the first `verify:` that fails.

**The home moved, and the move is the point.** This used to be `specs/config.json`, at the root of
the specs workspace — which only had a place to live while every repo was guaranteed a `specs/`
folder. A repo that declares an external backend may hold no `specs/` at all, so the plugin's
configuration lives in one neutral home shared by all three fronts, and `worktreeSetup` moved there
with the rest of it. Whether the command resolves can only be judged against the new worktree's
path, which `cq specs` is never told.

**On stamping `branch:` for a branch this plugin never cut.** A human may have checked one out by
hand before running `execute`, and a spec built there with nothing stamped leaves
`/quenching:specs:conclude` unable to say what it merges into.

**On removing the worktree after a merge.** Isolation nobody cleans up accumulates: directories
beside the repo, each pointing at an already integrated branch, none of them obviously safe to
delete.

## Branch and worktree names

<!-- rules -->

```
plan/<slug>
```

The **suggested default** when the inline offer cuts a new branch or worktree — kebab-case, no
date prefix, no id. `cq specs next --front` ranks on whether
`plan/<slug>` is **alive**, so a branch named to the default is what tells that ranking this
spec is already under way without a stamped `branch` record.

**The name is a suggestion, never a contract.** When `/quenching:specs:execute` starts on a branch that is not
the repository's base — whatever it is named — that branch is **adopted** as `work` outright: no
rename, no refusal, and no requirement that it match `plan/<slug>`.

A worktree goes beside the repo, never inside it:

```bash
git worktree add ../<repo>-<slug> -b plan/<slug>
```

### The worktree is the preferred form

<!-- rules -->

`/quenching:specs:execute`'s inline isolation offer leads with **Worktree and recommends it**, unconditionally — a
plain branch and working in place stay available, in that order after it.

**Unconditionally** means no heuristic sniffing the target for `package.json` or `.venv/`. What is
offered instead is the **cost, stated in the offer itself**: a fresh checkout carries only what git
tracks — no installed dependencies, no `.env`, no venv, no build output.

### A target may declare a setup command

<!-- rules -->

`.claude/quenching.json`, at the repo root, under the `worktreeSetup` key:

```json
{"backend": "files", "worktreeSetup": "./scripts/wt-setup.sh"}
```

See
[plugin-configuration.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/plugin-configuration.md)
§The recognised keys.

Read by `cq specs config --json` (exit 0 whether or not anything is declared) and run **once** by
the inline offer, immediately after `git worktree add`, with **cwd inside the new worktree** — the
tree lacking the dependencies is the tree that must install them. `cq specs` reads the value and
never executes it.

No file, no key, or a command that does not resolve all mean **no setup**, and none of them is a
finding — most repos declare nothing, and declaring nothing must cost nothing. `cq specs doctor`
reports only the two ways it can be *wrong*, both `warn`: `sp-config-unknown-key` and
`sp-config-unparseable`. They exist for the one real failure mode of a machine-read config —
`worktree_setup` written where `worktreeSetup` was expected, and silence afterwards.

**Its consent is the isolation offer.** The command is displayed **verbatim** in `/quenching:specs:execute`'s
isolation-offer block, and choosing Worktree is the OK for it: no second prompt, no remembered
authorisation. A failing setup is reported and **never undoes the worktree**.

## Recording the isolation

<!-- rules -->

```bash
cq specs record <slug> branch --set base=main --set work=plan/<slug>
```

`base` is whatever was checked out when the branch was cut. It is **not** assumed to be `main`.
`work` is derivable from `git branch --show-current` while the branch is checked out; `base` is
not — **after the merge, git cannot say what the branch was cut from**, which is the whole reason
the record exists and why it is captured while still true.

**Every resolved work ref gets `branch:` stamped**, including a branch this plugin never cut and
including the in-place case, where `work` equals `base`. That last one is not the silence it used
to be: an absent record and a record reading `work == base` are different claims — nobody has
decided yet, versus a human declined isolation — and only the second is a fact worth carrying.

**`work == base` means no isolation was taken, and every consumer must read it that way.** It is
not a work ref that happens to be alive: the base is always alive, so anything ranking, diffing or
merging on the mere PRESENCE of the record gets the in-place case backwards. `cq specs next` guards
it explicitly, and `/quenching:specs:conclude` branches on `work != base` rather than on the record
existing — there is no branch diff to review and nothing to merge when the work never left the base.

**For a branch this plugin cuts, `base` is an observed fact** — it was what stood checked out the
moment the branch was created. **For a branch it adopts, `base` is inferred**, in this order,
stopping at the first that answers:

1. the spec's own `branch.base` record, when one already exists;
2. `git symbolic-ref refs/remotes/origin/HEAD` — the default the remote declares;
3. `git config init.defaultBranch`, and then `main`.

**Show the inference on the same line as the confirmation, before stamping** —
`base: main — inferred; this branch was not cut by this command` — because the record is
write-once and that is the only moment disagreeing with it is cheap. Never derive `base` from
`git merge-base` or `--fork-point`: both answer a **commit**, not a branch name, and a commit
ancestral to three branches identifies none of them.

The record is `writeOnce: true`, and `cq specs record` enforces it: a second stamp refuses (exit 2)
naming the value already held. A later run **reads** it rather than rewriting it, and a current
branch that disagrees with `work` is a finding to report, never a value to correct. Never edit the
frontmatter to get past that refusal — the refusal is the rule, working.

**The record is not the signal.** A human may cut `plan/<slug>` by hand and stamp nothing, and a
record outlives the branch it names. Anything asking "is this spec in flight?" asks git for a live
ref — the record only supplies the ref's name when it is not the default.

### Marking the branch with the specs it built

<!-- rules -->

Beside the `branch:` frontmatter record, `/quenching:specs:execute` also marks the branch itself, in a
form that survives outside the spec's own file — a recognizable line in the branch's own
description:

```bash
git config branch.<name>.description
```

the same slot `git branch --edit-description` opens an editor on. After every task's commit, read
the current description and rewrite — never duplicate — the one line it owns:

```
quenching-slugs: <slug1>,<slug2>
```

Any other text already in the description — a line a human wrote by hand — is preserved untouched
above and below it. A second spec built on the same branch appends its slug to the same line rather
than writing a second one, and the line is rewritten on every task commit, which is what keeps it
current with HEAD without a separate cleanup pass. The read-merge-write, run by
`/quenching:specs:execute` after every task's commit:

```bash
python3 -c "
import subprocess, re, sys
name, slug = sys.argv[1], sys.argv[2]
r = subprocess.run(['git', 'config', 'branch.%s.description' % name], capture_output=True, text=True)
lines = r.stdout.splitlines() if r.returncode == 0 else []
slugs, idx = set(), None
for i, line in enumerate(lines):
    m = re.match(r'quenching-slugs: (.*)', line)
    if m:
        slugs, idx = {s.strip() for s in m.group(1).split(',') if s.strip()}, i
slugs.add(slug)
newline = 'quenching-slugs: ' + ','.join(sorted(slugs))
if idx is not None:
    lines[idx] = newline
else:
    lines.append(newline)
subprocess.run(['git', 'config', 'branch.%s.description' % name, chr(10).join(lines)], check=True)
" "<work>" "<slug>"
```

**Never marked under `In place`.** The mark exists only when this command controls the branch it is
building on — one adopted or cut by the isolation offer. Building in place, on a branch that was
already checked out and possibly shared or someone else's, writes nothing here, exactly as it
stamps no `branch:` record there.

The description is tied to the **ref**, not to a worktree's physical directory, so it reads back
identically whether the isolation taken was **Worktree** or plain **Branch**.

`/quenching:specs:conclude`, without a `--spec` argument, reads this same line to resolve which spec(s)
built the branch it is closing — the record git alone cannot reproduce once the branch is merged and
deleted.

<!-- rationale -->

The branch description was chosen over a dedicated `git config` key, a branch-name convention, or a
versioned file in the branch: it needs no new git plumbing, ties to the ref rather than a directory
or a name a human might rename, and never leaks into the branch's own tree. Its cost is symmetric
with its simplicity — the description is local to the `.git` that wrote it and does not survive a
clone or fetch, which `/quenching:specs:conclude`'s own fallback exists to cover when it does not
resolve.
