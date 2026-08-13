#!/usr/bin/env python3
"""Freeze the `--json` contract of the four shipped scripts as golden outputs.

DO NOT RUN THIS FILE DIRECTLY. `SPECS_PY`/`SKILLS_PY`/`SESSION_PY`/`OKF_PY` name the
four pre-refactor scripts `plan/modularizar-specs-knowledge-components` (task 10.1)
deleted. `main()` still deletes every existing golden first, then shells out to
those paths; each `Capture.run` gets an empty stdout back (`python3: can't open
file ...`, exit 2, recorded in `INDEX.json` but never checked), and `main()`
reports success regardless. Running it today does not regenerate the goldens —
it silently empties them.

The four `capture_*` functions below are still live: `test_golden.Replay` imports
and reuses them, pointed at `cq` instead of `SCRIPTS`, to both compare against and
(`renomear-docs-para-knowledge`, task 6.1, 2026-08-13) refresh the frozen bytes.
`main()` itself has had no working target since that refactor; fix `SCRIPTS` before
ever invoking it again.

Everything that varies between machines or runs goes through `normalize`, which
the regression suite re-imports so both sides of a comparison are normalized by
the same code.
"""
from __future__ import annotations

import datetime
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
PLUGIN_ROOT = HERE.parent
REPO_ROOT = PLUGIN_ROOT.parent.parent
GOLDEN_DIR = HERE / "fixtures" / "golden"

SPECS_PY = PLUGIN_ROOT / "assets" / "bin" / "specs.py"
SKILLS_PY = PLUGIN_ROOT / "assets" / "bin" / "skills.py"
SESSION_PY = PLUGIN_ROOT / "assets" / "bin" / "session.py"
OKF_PY = PLUGIN_ROOT / "assets" / "hooks" / "okf-validate.py"

SCRIPTS = {
    "specs": SPECS_PY,
    "skills": SKILLS_PY,
    "session": SESSION_PY,
    "okf": OKF_PY,
}

VERSION = (PLUGIN_ROOT / "VERSION").read_text(encoding="utf-8").strip()
TODAY = datetime.date.today().isoformat()

READ_TARGET = "assets/references/align/convergence.md"


# --------------------------------------------------------------------------- #
# normalization — re-imported by the regression suite
# --------------------------------------------------------------------------- #
def normalize(text: str, ws: str | pathlib.Path | None = None) -> str:
    """Strip everything that is true of THIS run rather than of the contract.

    `ws` is the throwaway workspace root, whose path carries a fresh mkdtemp
    suffix on every run; the repo root differs per checkout. Both are replaced
    realpath-first, because macOS resolves `/tmp` to `/private/tmp` and a tool
    that calls `os.path.realpath` then prints a path the caller never passed.
    """
    subs: list[tuple[str, str]] = []
    for raw, token in ((ws, "<WS>"), (REPO_ROOT, "<REPO>")):
        if raw is None:
            continue
        path = str(raw)
        subs.append((path, token))
        subs.append((os.path.realpath(path), token))
    for src, token in sorted(subs, key=lambda pair: -len(pair[0])):
        text = text.replace(src, token)
    text = text.replace(VERSION, "<VERSION>")
    # Only TODAY, never every date: the fixture's own dates are fixed and part of
    # the contract under test.
    return text.replace(TODAY, "<TODAY>")


# --------------------------------------------------------------------------- #
# fixture workspace
# --------------------------------------------------------------------------- #
QUENCHING_JSON = """{
  "backend": "files",
  "integrationBranch": "develop",
  "releaseBranch": "main"
}
"""

ALPHA = """---
slug: alpha-widget
title: Alpha Widget
date: 2026-01-05
verification: per-task
tags: [fixture, golden]
assignee: fixture-owner
start: 2026-01-06
target: 2026-02-06
priority: {level: 1, criticality: high, complexity: medium, date: 2026-01-05}
refined: {mode: deep, date: 2026-01-06}
approved: {date: 2026-01-07}
branch: {base: develop, work: plan/alpha-widget}
---

# Alpha Widget

## Overview

The widget front has two halves that drifted apart; this spec pulls them back onto one shape.

## Problem

The loader and the renderer each keep their own copy of the widget list, so a widget added to
one is invisible to the other.

## Proposal

- One registry owns the widget list.
- The loader and the renderer both read it.

## Out of Scope

- none — the boundary is the widget list, and nothing else was near it.

## Impact

### Standards this spec will write into /.knowledge/standards/

- `/.knowledge/standards/architecture/widget-registry.md` — one registry owns the list

### Standards at `authority: background` this spec may resolve

- none

### Product code this spec expects to touch

- `src/widgets/loader.py` — reads the registry instead of its own list

## Validation

- `python3 -m unittest discover tests/widgets` passes.

## Design

- The registry is a module-level dict, built once at import — the two readers are in-process.

## Alternatives Considered

- A database table — rejected, the list is static and ships with the code.

## Open Decisions

- none — every question was settled while writing the proposal.

## Risks

- ACCEPTED — a third reader could appear and skip the registry; nothing enforces it yet.

## Handoff

The registry lives in `src/widgets/registry.py`. Both readers import it; neither builds a list.

## Tasks

### 1. Registry

- [x] 1.1 Create the registry module
      files: src/widgets/registry.py (new)
      verify: python3 -m unittest tests.widgets.test_registry
      subject: plan/alpha-widget: 1.1 Create the registry module
- [ ] 1.2 Point the loader at the registry
      files: src/widgets/loader.py
      pattern: src/widgets/registry.py
      verify: python3 -m unittest tests.widgets.test_loader
- [ ] 1.3 Write the registry standard
      files: /.knowledge/standards/architecture/widget-registry.md (new)
      verify: python3 assets/hooks/okf-validate.py .knowledge

### 2. Readers

- [ ] 2.1 [P] Point the renderer at the registry
      files: src/widgets/renderer.py
      verify: python3 -m unittest tests.widgets.test_renderer
- [ ] 2.2 [P] Point the exporter at the registry
      files: src/widgets/exporter.py
      verify: python3 -m unittest tests.widgets.test_exporter
- [!] 2.3 Drop the loader's private list — blocked: the vendor SDK still imports it

## Discoveries

- the renderer caches the list for a whole request → promoted: widget-cache-invalidation
- the exporter logs one line per widget → dismissed: noise, but harmless
"""

BETA = """---
slug: beta-gizmo
title: Beta Gizmo
date: 2026-01-09
verification: per-section
---

# Beta Gizmo

## Problem

The gizmo endpoint answers with a 200 and an empty body when the upstream store is down, so
every caller reads an outage as an empty result set.
"""

OUTCOME = """
## Outcome

Shipped: the registry is the one list, and both readers import it.
"""

LEGACY = """---
slug: legacy-knob
title: Legacy Knob
date: 2025-11-02
verification: end-of-plan
outcome: done
merge: {strategy: merge-commit, subject: "plan/legacy-knob: merge", pr: 41}
---

# Legacy Knob

## Problem

The knob had two owners and no default.

## Tasks

### 1. Knob

- [x] 1.1 Give the knob one owner and a default

## Outcome

Shipped: the knob has one owner, and its default is declared beside it.
"""


def build_workspace(dest: pathlib.Path) -> pathlib.Path:
    """A self-contained `files`-backend workspace. Returns the workspace root.

    The backend is `files` and never the `github` this repo declares: a capture
    that reaches the network is neither reproducible nor offline-runnable.
    """
    (dest / ".claude").mkdir(parents=True)
    (dest / ".claude" / "quenching.json").write_text(QUENCHING_JSON, encoding="utf-8")
    plans = dest / ".specs" / "plans"
    plans.mkdir(parents=True)
    (plans / "alpha-widget.md").write_text(ALPHA, encoding="utf-8")
    (plans / "beta-gizmo.md").write_text(BETA, encoding="utf-8")
    archive = dest / ".specs" / "archive"
    archive.mkdir(parents=True)
    (archive / "legacy-knob.md").write_text(LEGACY, encoding="utf-8")
    return dest


def build_legacy_workspace(dest: pathlib.Path) -> pathlib.Path:
    """The v2 layout `migrate` folds away: specs in `backlog/` and `ready/` instead
    of `plans/`. Nothing else reaches that code path — against a current workspace
    `migrate` refuses with `sp-nothing-to-migrate`."""
    (dest / ".claude").mkdir(parents=True)
    (dest / ".claude" / "quenching.json").write_text(QUENCHING_JSON, encoding="utf-8")
    backlog = dest / ".specs" / "backlog"
    backlog.mkdir(parents=True)
    (backlog / "beta-gizmo.md").write_text(BETA, encoding="utf-8")
    ready = dest / ".specs" / "ready"
    ready.mkdir(parents=True)
    (ready / "alpha-widget.md").write_text(ALPHA, encoding="utf-8")
    return dest


# --------------------------------------------------------------------------- #
# capture
# --------------------------------------------------------------------------- #
class Capture:
    def __init__(self, tmp: pathlib.Path) -> None:
        self.tmp = tmp
        self.entries: list[dict] = []
        self.skipped: list[dict] = []

    def workspace(self, tag: str, legacy: bool = False) -> pathlib.Path:
        """A pristine workspace. Every WRITE case gets its own, so the goldens do
        not depend on the order the cases run in."""
        build = build_legacy_workspace if legacy else build_workspace
        return build(self.tmp / f"ws-{tag}")

    def env(self) -> dict:
        env = dict(os.environ)
        # okf-validate.py prefers this over the hook payload's own `cwd`, so leaving
        # it set points the hook capture at whatever repo the caller is standing in.
        env.pop("CLAUDE_PROJECT_DIR", None)
        # The hook's dirty marker is written to the system tempdir, keyed by a digest
        # of the project path; redirecting keeps that stamp inside the throwaway tree.
        env["TMPDIR"] = str(self.tmp / "tmpdir")
        return env

    def run(self, name: str, script: str, argv: list[str], *, cwd: pathlib.Path,
            ws: pathlib.Path | None = None, stdin: str | None = None,
            ext: str = "json") -> None:
        cmd = [sys.executable, str(SCRIPTS[script])] + argv
        proc = subprocess.run(cmd, cwd=str(cwd), env=self.env(), input=stdin,
                              capture_output=True, text=True)
        stdout = normalize(proc.stdout, ws)
        golden = f"{name}.{ext}"
        (GOLDEN_DIR / golden).write_text(stdout, encoding="utf-8")
        self.entries.append({
            "golden": golden,
            "script": str(SCRIPTS[script].relative_to(REPO_ROOT)),
            "argv": [normalize(a, ws) for a in argv],
            "cwd": normalize(str(cwd), ws),
            "stdin": normalize(stdin, ws) if stdin is not None else None,
            "exit": proc.returncode,
            "stderr": normalize(proc.stderr, ws),
        })

    def skip(self, name: str, reason: str) -> None:
        self.skipped.append({"id": name, "reason": reason})


# --------------------------------------------------------------------------- #
# the cases
# --------------------------------------------------------------------------- #
def capture_specs(cap: Capture) -> None:
    ws = cap.workspace("read")
    root = str(ws / ".specs")
    plugin = PLUGIN_ROOT

    def read(name: str, argv: list[str], ext: str = "json") -> None:
        cap.run(f"specs-{name}", "specs", ["--root", root] + argv, cwd=plugin, ws=ws, ext=ext)

    read("version", ["--version"], ext="txt")
    read("list", ["list", "--json"])
    read("status-alpha", ["status", "--spec", "alpha-widget", "--json"])
    read("status-beta", ["status", "--spec", "beta-gizmo", "--json"])
    read("show-map", ["show", "--spec", "alpha-widget", "--json"])
    read("show-task", ["show", "--spec", "alpha-widget", "--task", "1.2", "--json"])
    read("show-full", ["show", "--spec", "alpha-widget", "--full", "--json"])
    read("show-missing", ["show", "--spec", "no-such-spec", "--json"])
    read("section-one", ["section", "alpha-widget", "## Problem", "--json"])
    read("section-many", ["section", "alpha-widget", "## Problem,## Risks", "--json"])
    read("section-moment", ["section", "alpha-widget", "--moment", "build", "--json"])
    read("verification-read", ["verification", "alpha-widget", "--json"])
    read("verification-bad", ["verification", "alpha-widget", "whenever", "--json"])
    read("tags-read", ["tags", "alpha-widget", "--json"])
    read("assignee-read", ["assignee", "alpha-widget", "--json"])
    read("start-read", ["start", "alpha-widget", "--json"])
    read("target-read", ["target", "alpha-widget", "--json"])
    read("record-read", ["record", "alpha-widget", "priority", "--json"])
    read("record-unset", ["record", "beta-gizmo", "approved", "--json"])
    read("record-unknown", ["record", "alpha-widget", "nonesuch", "--json"])
    read("next-spec", ["next", "--spec", "alpha-widget", "--json"])
    read("next-front", ["next", "--front", "--json"])
    read("parallel", ["parallel", "--spec", "alpha-widget", "--json"])
    read("validate-all", ["validate", "--json"])
    read("validate-one", ["validate", "--spec", "beta-gizmo", "--json"])
    read("config", ["config", "--json"])
    read("doctor", ["doctor", "--json"])
    read("selftest", ["selftest", "--json"])
    read("migrate-noop", ["migrate", "--dry-run", "--json"])
    read("promote-gate-unmet", ["promote", "alpha-widget", "--dry-run", "--json"])

    def write(name: str, argv: list[str], stdin: str | None = None,
              legacy: bool = False, outcome_for: str | None = None) -> None:
        w = cap.workspace(name, legacy=legacy)
        if outcome_for:
            spec = w / ".specs" / "plans" / f"{outcome_for}.md"
            spec.write_text(spec.read_text(encoding="utf-8") + OUTCOME, encoding="utf-8")
        cap.run(f"specs-{name}", "specs",
                ["--root", str(w / ".specs")] + argv, cwd=plugin, ws=w, stdin=stdin)

    write("new", ["new", "gamma-lever", "--title", "Gamma Lever",
                  "--verification", "end-of-plan", "--json"])
    write("section-write", ["section", "beta-gizmo", "## Risks", "--write", "--json"],
          stdin="- the upstream store has no health endpoint; mitigated by a timeout.\n")
    write("task-check", ["task", "--spec", "alpha-widget", "--check", "1.2",
                         "--subject", "plan/alpha-widget: 1.2 Point the loader at the registry",
                         "--json"])
    write("task-uncheck", ["task", "--spec", "alpha-widget", "--uncheck", "1.1", "--json"])
    write("task-block", ["task", "--spec", "alpha-widget", "--block", "2.1",
                         "--reason", "the renderer is mid-rewrite on another branch", "--json"])
    write("record-set", ["record", "alpha-widget", "reviewed", "--set", "date=2026-02-01",
                         "--json"])
    write("verification-set", ["verification", "beta-gizmo", "end-of-plan", "--json"])
    write("tags-set", ["tags", "beta-gizmo", "fixture,golden,second", "--json"])
    write("assignee-set", ["assignee", "beta-gizmo", "second-owner", "--json"])
    write("start-set", ["start", "beta-gizmo", "2026-03-01", "--json"])
    write("target-set", ["target", "beta-gizmo", "2026-04-01", "--json"])
    write("discover", ["discover", "beta-gizmo",
                       "the upstream store answers 200 on a cold cache", "--json"])
    write("promote-abandoned", ["promote", "beta-gizmo", "--outcome", "abandoned", "--json"],
          outcome_for="beta-gizmo")
    write("promote-forced", ["promote", "alpha-widget", "--outcome", "done", "--force", "--json"],
          outcome_for="alpha-widget")
    write("migrate-dry-run", ["migrate", "--dry-run", "--json"], legacy=True)
    write("migrate", ["migrate", "--json"], legacy=True)

    # `--root` naming the CONTAINER of a phased `.specs/`, not the workspace itself —
    # `sp-root-too-high`. One workspace serves the read-only cases below (`list`/`validate`/
    # `status`/`doctor`, over the SAME fixture the control pair reads correctly); `new` gets its
    # own so a bug that fails to refuse cannot leave a stray `plans/` behind for the others to
    # read.
    too_high = cap.workspace("root-too-high")
    container = str(too_high)
    correct = str(too_high / ".specs")

    def over_root(name: str, root: str, argv: list[str]) -> None:
        cap.run(f"specs-root-too-high-{name}", "specs", ["--root", root] + argv,
                cwd=plugin, ws=too_high)

    over_root("list", container, ["list", "--json"])
    over_root("validate", container, ["validate", "--json"])
    over_root("status", container, ["status", "--spec", "alpha-widget", "--json"])
    over_root("doctor", container, ["doctor", "--json"])
    # Control — same fixture, `--root` pointed at `.specs/` itself: unaffected, exactly as
    # before this predicate existed.
    over_root("control-list", correct, ["list", "--json"])
    over_root("control-validate", correct, ["validate", "--json"])

    new_ws = cap.workspace("root-too-high-new")
    cap.run("specs-root-too-high-new", "specs",
            ["--root", str(new_ws), "new", "some-spec", "--json"], cwd=plugin, ws=new_ws)

    exp = cap.workspace("export")
    cap.run("specs-export", "specs",
            ["--root", str(exp / ".specs"), "export", "--all",
             "--out", str(exp / "export"), "--json"],
            cwd=plugin, ws=exp)

    cap.skip("specs-release",
             "`release` has no read-only or dry-run mode: it rewrites the seven "
             "version-carrying artifacts and creates a git tag. Running it to capture a "
             "golden would bump this repo's own version.")


def capture_skills(cap: Capture) -> None:
    root = str(PLUGIN_ROOT)

    def run(name: str, argv: list[str], ext: str = "json",
            ws: pathlib.Path | None = None) -> None:
        # cwd is the plugin root because `read` resolves its path argument against the
        # process cwd, not against --root.
        cap.run(f"skills-{name}", "skills", ["--root", root] + argv,
                cwd=PLUGIN_ROOT, ws=ws, ext=ext)

    run("version", ["--version"], ext="txt")
    run("lint", ["lint", "--json"])
    run("lint-one", ["lint", "commands/knowledge/add.md", "--json"])
    run("doctor", ["doctor", "--json"])
    run("selftest", ["selftest", "--json"])
    run("drift", ["drift", "--json"])
    run("read-index", ["read", READ_TARGET, "--json"])
    run("read-section", ["read", READ_TARGET, "--sections", "The convergence contract", "--json"])
    run("read-rules-only", ["read", READ_TARGET, "--sections", "The convergence contract",
                            "--rules-only", "--json"])
    run("read-missing", ["read", READ_TARGET, "--sections", "cycle-authorization", "--json"])

    # `registry reindex` REWRITES the doc it is pointed at, so it is aimed at a copy
    # of the shipped template rather than at the repo's own listing.
    reg_dir = cap.tmp / "ws-registry"
    reg_dir.mkdir(parents=True)
    reg = reg_dir / "automation.md"
    shutil.copyfile(PLUGIN_ROOT / "assets" / "templates" / "automation" / "registry.md", reg)
    run("registry-reindex", ["registry", "reindex", "--registry", str(reg), "--json"],
        ws=reg_dir)


def capture_session(cap: Capture) -> None:
    """`list` and `digest` need a transcript; the only one that ships is the
    `FIXTURE` constant `selftest` materialized into a tempfile. Task 10.1 removed the
    script this used to import that constant from; `FIXTURE` migrated verbatim to
    `test_session.py` under task 6.3 (its docstring says so), so this reads it from
    there instead — the same records, a different, still-live home."""
    fixture = __import__("test_session").FIXTURE

    tdir = cap.tmp / "ws-session"
    tdir.mkdir(parents=True)
    transcript = tdir / "fixture.jsonl"
    transcript.write_text("\n".join(json.dumps(r) for r in fixture) + "\n",
                          encoding="utf-8")

    def run(name: str, argv: list[str], ext: str = "json") -> None:
        cap.run(f"session-{name}", "session", argv, cwd=REPO_ROOT, ws=tdir, ext=ext)

    run("version", ["--version"], ext="txt")
    run("selftest", ["selftest", "--json"])
    run("list", ["list", str(transcript), "--json"])
    run("digest", ["digest", str(transcript), "--json"])
    run("digest-one", ["digest", str(transcript), "--command", "demo:conduct", "--json"])


def capture_okf(cap: Capture) -> None:
    """The embedded skeleton is validated through a COPY outside git.

    CLI mode is the one mode that shells out to `git log` per doc to age it, so
    validating the skeleton in place would emit `stale-doc` warnings that move with
    this repo's commit history. The copy carries no git, so the scan is the
    structural verdict alone — which is the contract these goldens exist to freeze.

    The copy keeps the skeleton's own layout, `<project>/.knowledge/`, matching what
    `standards/architecture/bundle-root.md` fixes for every target repo: a doc's
    `resource` globs resolve against the bundle's parent, so a copy under any other
    name would turn every one of them into a `resource-unresolved` warning the
    shipped skeleton does not have (`renomear-docs-para-knowledge`, task 6.1,
    2026-08-13 — this copy used to sit at `<project>/docs/` while the skeleton
    declared `/.docs/`, a mismatch `okf-validate-skeleton`/`-text`/`-findings`
    carried as UNROUTED entries until this fix).
    """
    proj = cap.tmp / "ws-okf"
    proj.mkdir(parents=True)
    bundle = proj / ".knowledge"
    shutil.copytree(PLUGIN_ROOT / "assets" / "knowledge", bundle)

    cap.run("okf-version", "okf", ["--version"], cwd=proj, ws=proj, ext="txt")
    cap.run("okf-selftest", "okf", ["selftest", "--json"], cwd=proj, ws=proj)
    cap.run("okf-validate-skeleton", "okf", [str(bundle), "--json"], cwd=proj, ws=proj)
    cap.run("okf-validate-skeleton-text", "okf", [str(bundle)], cwd=proj, ws=proj, ext="txt")

    bad_body = "# Golden Fixture Bad\n\nA concept doc carrying no frontmatter at all.\n"
    (bundle / "concepts" / "golden-fixture-bad.md").write_text(bad_body, encoding="utf-8")
    cap.run("okf-validate-findings", "okf", [str(bundle), "--json"], cwd=proj, ws=proj)

    # Hook mode reads the bundle at `<project>/.knowledge` and never at a path argument,
    # so it needs its own copy under that name.
    hook_proj = cap.tmp / "ws-okf-hook"
    hook_proj.mkdir(parents=True)
    shutil.copytree(PLUGIN_ROOT / "assets" / "knowledge", hook_proj / ".knowledge")
    bad = hook_proj / ".knowledge" / "concepts" / "golden-fixture-bad.md"
    bad.write_text(bad_body, encoding="utf-8")
    payload = json.dumps({
        "hook_event_name": "PostToolUse",
        "cwd": str(hook_proj),
        "tool_name": "Write",
        "tool_input": {"file_path": str(bad)},
    })
    cap.run("okf-hook-posttooluse", "okf", [], cwd=hook_proj, ws=hook_proj, stdin=payload)


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main() -> int:
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    for stale in GOLDEN_DIR.iterdir():
        stale.unlink()

    with tempfile.TemporaryDirectory(prefix="quenching-golden-") as raw:
        tmp = pathlib.Path(raw)
        (tmp / "tmpdir").mkdir()
        cap = Capture(tmp)
        capture_specs(cap)
        capture_skills(cap)
        capture_session(cap)
        capture_okf(cap)

    index = {
        "capturedFromVersion": VERSION,
        "notes": [
            "Captured by tests/capture_golden.py while specs.py, skills.py, session.py and "
            "okf-validate.py are four separate scripts. A later refactor cannot recapture "
            "these — it can only be measured against them.",
            "Every golden holds the normalized STDOUT of one invocation; the exit code and "
            "the normalized stderr live in this index, because the command bodies branch on "
            "the exit code (0 ok / 1 findings / 2 refusal) as much as on the payload.",
            "Paths are normalized to <REPO> and <WS>, the plugin version to <VERSION>, and "
            "the capture date to <TODAY>. Re-import capture_golden.normalize to compare.",
        ],
        "captured": cap.entries,
        "skipped": cap.skipped,
    }
    (GOLDEN_DIR / "INDEX.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(cap.entries)} golden(s) in {GOLDEN_DIR.relative_to(REPO_ROOT)}, "
          f"{len(cap.skipped)} skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
