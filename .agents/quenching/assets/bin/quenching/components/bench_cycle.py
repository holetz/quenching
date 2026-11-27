"""bench, layer `ciclo` — create → develop → execute → conclude on a throwaway fixture, verb by verb.

The fixture is a new git repository with a bare local origin, the runtime `.agents/quenching/` of
the measured root copied in and a minimal `backend: git` config, so nothing reaches the real store,
a forge or the checkout. The cycle runs through the runtime's own `cq`, in the order the flow
references name the verbs; what belongs to the forge (the PR merge) is plain git, outside the
measure. Per verb: wall clock and the response size in tokens. A verb that fails is a finding, and
an essential one stops the cycle. The fixture is removed at the end unless `keep` says otherwise.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from quenching.common.output import finding

BASE = "main"
NAME = "ensaio"
SESSION = "bench"
IDENTITY = {"GIT_AUTHOR_NAME": "bench", "GIT_AUTHOR_EMAIL": "bench@example.invalid",
            "GIT_COMMITTER_NAME": "bench", "GIT_COMMITTER_EMAIL": "bench@example.invalid"}
#: Variables that would point the fixture's `cq` at the real session, store or config.
STRIPPED = ("QUENCHING_", "GIT_", "CLAUDE_", "OPENCODE_", "COPILOT_")
TIMEOUT_S = 120

SECTIONS = """## Problem

- Fixture do bench.

## Proposal

- O bench escreve `ensaio.txt` na raiz.

## Out of Scope

- Qualquer outro arquivo.

## Impact

### Standards this spec will write into docs/standards/

- none — fixture do bench.

### Product code this spec expects to touch

- `ensaio.txt` (novo).

## Validation

- `test -f ensaio.txt` passa.

## Design

### Assumptions

- A fixture é descartável — `## Proposal`.

## Alternatives Considered

- none — fixture do bench.

## Open Decisions

- none — fixture do bench.

## Risks

- none — fixture do bench.

## Tasks

### 1. Arquivo

- [ ] 1.1 Escrever o arquivo do bench
      files: ensaio.txt (new)
      verify: test -f ensaio.txt
"""
HEADINGS = ("Problem,Proposal,Out of Scope,Impact,Validation,Design,Alternatives Considered,"
            "Open Decisions,Risks,Tasks")


@dataclass
class Step:
    flow: str
    verb: str
    seconds: float
    tokens: int
    ok: bool
    code: str | None = None


@dataclass
class Cycle:
    root: Path
    base: Path
    repo: Path
    env: dict[str, str]
    cq: list[str]
    steps: list[Step] = field(default_factory=list)
    spec: str | None = None
    slot: Path | None = None
    branch: str | None = None
    interrupted: str | None = None

    def git(self, *args: str, cwd: Path | None = None) -> str:
        result = subprocess.run(["git", *args], cwd=cwd or self.repo, env=self.env,
                                capture_output=True, text=True, check=False)
        if result.returncode:
            raise RuntimeError(f"git {' '.join(args)}: {result.stderr.strip()[:300]}")
        return result.stdout

    def run(self, flow: str, verb: str, *args: str, cwd: Path | None = None, stdin: str | None = None,
            essential: bool = False) -> dict:
        start = time.perf_counter()
        result = subprocess.run([*self.cq, *args], cwd=cwd or self.repo, env=self.env, input=stdin,
                                capture_output=True, text=True, check=False, timeout=TIMEOUT_S)
        seconds = time.perf_counter() - start
        try:
            data = json.loads(result.stdout) if result.stdout.strip().startswith("{") else {}
        except ValueError:
            data = {}
        ok = result.returncode == 0 and data.get("ok") is not False
        code = None if ok else str(data.get("code") or f"exit {result.returncode}")
        self.steps.append(Step(flow, verb, seconds, -(-len(result.stdout) // 4), ok, code))
        if not ok and essential:
            self.interrupted = f"{flow}: {verb} failed ({code})"
            raise RuntimeError(self.interrupted)
        return data


def make_env(base: Path) -> dict[str, str]:
    empty = base / "gitconfig"
    empty.touch()
    env = {k: v for k, v in os.environ.items() if not k.startswith(STRIPPED)}
    env.update(IDENTITY)
    env.update({"GIT_CONFIG_GLOBAL": str(empty), "GIT_CONFIG_NOSYSTEM": "1"})
    return env


def running_cq() -> list[str]:
    """This process's own `cq`, the fallback when the measured root carries no installed runtime."""
    return [sys.executable, str(Path(__file__).resolve().parents[2] / "cq")]


def build_fixture(root: Path, base: Path) -> Cycle:
    env = make_env(base)
    origin, repo = base / "origin.git", base / "repo"
    cycle = Cycle(root, base, repo, env, running_cq())
    cycle.git("init", "-q", "--bare", str(origin), cwd=base)
    cycle.git("init", "-q", "-b", BASE, str(repo), cwd=base)
    installed = root / ".agents/quenching"
    if installed.is_dir():
        shutil.copytree(installed, repo / ".agents/quenching", symlinks=True,
                        ignore=shutil.ignore_patterns("__pycache__"))
    (repo / ".agents").mkdir(exist_ok=True)
    (repo / ".agents/quenching.json").write_text(json.dumps({"backend": "git"}) + "\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Fixture do bench\n", encoding="utf-8")
    (repo / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    cycle.git("add", "-A")
    cycle.git("commit", "-q", "-m", "Fixture do bench")
    cycle.git("remote", "add", "origin", str(origin))
    cycle.git("push", "-q", "-u", "origin", BASE)
    if installed.is_dir():
        cycle.cq = [sys.executable, str(repo / ".agents/quenching/bin/cq")]
    return cycle


def _create(c: Cycle) -> None:
    data = c.run("create", "specs new", "specs", "new", NAME, "--json", essential=True)
    c.spec = str(data["id"])
    c.run("create", "specs list", "specs", "list", "--json")


def _develop(c: Cycle) -> None:
    spec = c.spec
    c.run("develop", "specs section --write", "specs", "section", spec, HEADINGS, "--write", "--json",
          stdin=SECTIONS, essential=True)
    c.run("develop", "specs record refined", "specs", "record", spec, "refined", "--set", "mode=compose",
          "--set", f"date={date.today().isoformat()}", "--json", essential=True)
    c.run("develop", "specs validate", "specs", "validate", "--spec", spec, "--json")
    c.run("develop", "specs parallel", "specs", "parallel", spec, "--json")
    c.run("develop", "specs status", "specs", "status", spec, "--json")
    c.run("develop", "specs record approved", "specs", "record", spec, "approved", "--set", "by=session",
          "--json", essential=True)


def _execute(c: Cycle) -> None:
    spec = c.spec
    c.branch = f"plan/{spec}-{NAME}"
    c.run("execute", "specs status", "specs", "status", spec, "--json")
    c.run("execute", "specs claim acquire", "specs", "claim", "acquire", spec, "--session", SESSION, "--json",
          essential=True)
    data = c.run("execute", "git worktree acquire", "git", "worktree", "acquire", "--branch", c.branch,
                 "--base", BASE, "--spec", spec, "--session", SESSION, "--no-setup", "--json", essential=True)
    c.slot = Path(data["path"])
    (c.slot / "ensaio.txt").write_text("ensaio\n", encoding="utf-8")
    c.git("add", "ensaio.txt", cwd=c.slot)
    data = c.run("execute", "git commit", "git", "commit", "--subject",
                 f"{c.branch}: 1.1 Escrever o arquivo do bench", "--json", cwd=c.slot, essential=True)
    c.run("execute", "specs task check", "specs", "task", "--spec", spec, "--check", "1.1", "--commit",
          str(data.get("sha")), "--json", essential=True)
    c.run("execute", "specs status", "specs", "status", spec, "--json")


def _conclude(c: Cycle) -> None:
    spec = c.spec
    c.run("conclude", "specs section --write", "specs", "section", spec, "Outcome", "--write", "--json",
          stdin="- O bench escreveu `ensaio.txt`.\n", essential=True)
    c.run("conclude", "specs validate", "specs", "validate", "--spec", spec, "--json")
    c.run("conclude", "git push", "git", "push", "--branch", c.branch, "--json", cwd=c.slot, essential=True)
    # The PR merge belongs to the forge: plain git on the fixture, outside the measure.
    c.git("fetch", "-q", "origin")
    c.git("merge", "-q", "--no-ff", f"origin/{c.branch}", "-m", f"Merge {c.branch}")
    c.git("push", "-q", "origin", BASE)
    c.run("conclude", "specs reconcile", "specs", "reconcile", "--write", "--json", essential=True)
    c.run("conclude", "git worktree release", "git", "worktree", "release", "--path", str(c.slot), "--json")
    c.run("conclude", "specs claim release", "specs", "claim", "release", spec, "--session", SESSION, "--json")
    c.run("conclude", "specs status", "specs", "status", spec, "--json")


SCRIPT = (("create", _create), ("develop", _develop), ("execute", _execute), ("conclude", _conclude))


def archived(c: Cycle) -> bool:
    if c.spec is None:
        return False
    out = subprocess.run([*c.cq, "specs", "status", c.spec, "--json"], cwd=c.repo, env=c.env,
                         capture_output=True, text=True, check=False)
    try:
        data = json.loads(out.stdout)
    except ValueError:
        return False
    return data.get("phase") == "archive" or data.get("stage") == "archived"


def measure(root: Path, keep: bool = False, slow_s: float = 20.0,
            big_tokens: int = 4_000) -> tuple[dict, list[dict]]:
    """Run the cycle on a fixture: the payload and its findings. A fixture that cannot even be built
    raises, which the verb reports as a layer that could not run (exit 2)."""
    base = Path(tempfile.mkdtemp(prefix="cq-bench-"))
    findings: list[dict] = []
    try:
        cycle = build_fixture(root, base)
        try:
            for _flow, step in SCRIPT:
                step(cycle)
        except (RuntimeError, subprocess.TimeoutExpired, KeyError) as exc:
            cycle.interrupted = cycle.interrupted or f"{type(exc).__name__}: {exc}"
        closed = cycle.interrupted is None and archived(cycle)
        for s in cycle.steps:
            if not s.ok:
                findings.append(finding("ct-bench-verb-failed", "error",
                                        f"{s.flow}: `{s.verb}` failed ({s.code})", flow=s.flow, verb=s.verb,
                                        remedy="reproduce the verb on the fixture (`--keep-fixture`)"))
            elif s.seconds > slow_s:
                findings.append(finding("ct-bench-verb-slow", "warning",
                                        f"{s.flow}: `{s.verb}` took {s.seconds:.1f}s", flow=s.flow, verb=s.verb,
                                        remedy="profile the verb"))
            elif s.tokens > big_tokens:
                findings.append(finding("ct-bench-response-big", "warning",
                                        f"{s.flow}: `{s.verb}` answered {s.tokens} tokens", flow=s.flow,
                                        verb=s.verb, remedy="page or summarise the response"))
        if cycle.interrupted or not closed:
            findings.append(finding("ct-bench-cycle-open", "error",
                                    cycle.interrupted or "the fixture spec did not reach archive/",
                                    remedy="rerun with `--keep-fixture` and reproduce the failing verb"))
        flows: dict[str, dict] = {}
        for s in cycle.steps:
            row = flows.setdefault(s.flow, {"seconds": 0.0, "tokens": 0, "verbs": 0})
            row["seconds"] = round(row["seconds"] + s.seconds, 3)
            row["tokens"] += s.tokens
            row["verbs"] += 1
        payload = {"closed": closed, "flows": flows, "fixture": str(base) if keep else None,
                   "steps": [s.__dict__ for s in cycle.steps]}
        return payload, findings
    finally:
        if not keep:
            shutil.rmtree(base, ignore_errors=True)
