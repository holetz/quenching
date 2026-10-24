#!/usr/bin/env python3
"""Run the committed eval case sets against any harness and model, graded by a fixed grader.

Each case runs in a disposable fixture: the suite's `fixture/` tree copied into a temporary
directory, committed as a git repository, then prepared by the suite's optional `setup.sh`. The
harness is a profile from `eval_harnesses.json` (an argv template), so the same cases run under
Claude Code, Codex, OpenCode or any command line. After the arm, the observable state of the
fixture is snapshotted and handed with the arm's output to the grader profile, which is the same
for every arm and model compared. A grade whose evidence is not a verbatim excerpt of that
material is downgraded to `unknown`.

Writes `<out>/<suite>/grading.json`, `<out>/<suite>/benchmark.json` and `<out>/summary.json`.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
EVALS_ROOT = ROOT / "plugins/quenching/assets/evals"
COMMANDS_ROOT = ROOT / "plugins/quenching/commands"
PROFILES = Path(__file__).resolve().with_name("eval_harnesses.json")
CQ = ROOT / "plugins/quenching/assets/bin/cq"
CQ_BIN = ROOT / "plugins/quenching/bin"
ARMS = ("with", "without")
RESULTS = ("pass", "fail", "unknown")
GIT_ENV = {"GIT_AUTHOR_NAME": "Eval fixture", "GIT_AUTHOR_EMAIL": "eval@example.com",
           "GIT_COMMITTER_NAME": "Eval fixture", "GIT_COMMITTER_EMAIL": "eval@example.com"}
# The workspace config belongs to the agent under evaluation: -c wins over it, so the snapshot never runs its commands.
SAFE_GIT = ["-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null", "-c", "diff.external="]
MATERIAL_LIMIT = 60000

GRADER_PROMPT = """You grade one run of a coding agent. For EVERY assertion below, decide whether the
material shows it holds. Reply with ONLY a JSON array, one object per assertion, in order:
[{{"assertion": "<the assertion verbatim>", "result": "pass" | "fail" | "unknown",
  "evidence": "<a verbatim excerpt copied from the material that shows the result>"}}]
The evidence must be copied character for character from the material. When no excerpt settles
an assertion, answer "unknown" with an empty evidence.

ASSERTIONS:
{assertions}

MATERIAL:
{material}
"""


# --------------------------------------------------------------------------- suites

def suite_dirs(paths: list[str]) -> list[Path]:
    if not paths:
        return sorted(p.parent for p in EVALS_ROOT.rglob("evals.json"))
    found = []
    for raw in paths:
        path = Path(raw).resolve()
        found.append(path.parent if path.name == "evals.json" else path)
    return found


def suite_name(directory: Path) -> str:
    try:
        return directory.resolve().relative_to(EVALS_ROOT.resolve()).as_posix()
    except ValueError:
        return directory.name


def command_model(skill: str) -> str | None:
    """The `model:` the evaluated command pins in its own frontmatter, or None when it pins none."""
    _, _, path = skill.lstrip("/").partition(":")
    if not path:
        return None
    file = COMMANDS_ROOT / (path.replace(":", "/") + ".md")
    try:
        lines = file.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, _, value = line.partition(":")
        if key.strip() == "model":
            return value.strip() or None
    return None


def check_suite(directory: Path) -> tuple[dict | None, list[str], list[str]]:
    """The suite's cases, its errors, and its warnings."""
    file = directory / "evals.json"
    if not file.is_file():
        return None, [f"{file}: missing"], []
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"{file}: not JSON ({exc})"], []
    if not isinstance(data, dict):
        return None, [f"{file}: the root must be a JSON object"], []
    errors, warnings = [], []
    if not isinstance(data.get("skill"), str) or not data["skill"]:
        errors.append(f"{file}: `skill` must be a non-empty string")
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append(f"{file}: `cases` must be a non-empty list")
        cases = []
    seen = set()
    for index, case in enumerate(cases):
        where = f"{file}: case {index}"
        if not isinstance(case, dict):
            errors.append(f"{where}: not an object")
            continue
        for key in ("id", "branch", "prompt"):
            if not isinstance(case.get(key), str) or not case[key].strip():
                errors.append(f"{where}: `{key}` must be a non-empty string")
        if isinstance(case.get("id"), str):
            if case["id"] in seen:
                errors.append(f"{where}: duplicate id {case['id']!r}")
            seen.add(case["id"])
        assertions = case.get("assertions")
        if not isinstance(assertions, list) or not assertions or \
                not all(isinstance(a, str) and a.strip() for a in assertions):
            errors.append(f"{where}: `assertions` must be a non-empty list of strings")
    triggers = data.get("triggers")
    if not isinstance(triggers, dict) or not all(
            isinstance(triggers.get(k), list) for k in ("shouldTrigger", "shouldNotTrigger")):
        errors.append(f"{file}: `triggers` needs `shouldTrigger` and `shouldNotTrigger` lists")
    if cases and not any(isinstance(c, dict) and "not for" in str(c.get("branch", "")).lower()
                         for c in cases):
        warnings.append(f"{file}: no case branch names the `Not for:` boundary")
    for script in ("setup.sh", "inspect.sh"):
        if (directory / script).exists() and not (directory / script).is_file():
            errors.append(f"{directory / script}: not a file")
    if (directory / "fixture").exists() and not (directory / "fixture").is_dir():
        errors.append(f"{directory / 'fixture'}: not a directory")
    return (data if not errors else None), errors, warnings


# --------------------------------------------------------------------------- profiles

def load_profiles(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))["profiles"]


def plugin_dirs() -> list[str]:
    manifest = json.loads((ROOT / "plugins/quenching/assets/modules.json").read_text(encoding="utf-8"))
    modules = [m for m in manifest["modules"] if "owned" in m]
    modules.sort(key=lambda m: not m.get("cqPathOwner"))
    return [str(ROOT / m["path"]) for m in modules]


def render(profile: dict, arm: str | None, values: dict, extra: list[str]) -> list[str]:
    """The argv for one invocation; `arm=None` is the grader's, which loads nothing."""
    if arm is not None and arm not in profile.get("arms", {}):
        raise ValueError(f"this harness profile has no `{arm}` arm")
    arm_tokens = profile["arms"][arm] if arm is not None else []
    argv: list[str] = []
    for token in profile["argv"]:
        if token == "{arm}":
            for item in arm_tokens:
                if item == "{plugin_dirs}":
                    for directory in plugin_dirs():
                        argv += ["--plugin-dir", directory]
                else:
                    argv.append(item.format(**values))
        elif token == "{extra}":
            argv += extra
        else:
            argv.append(token.format(**values))
    return argv


def codex_output(stdout: str) -> tuple[str, int | None]:
    """The agent messages of a `codex exec --json` event stream, and the turn's tokens."""
    messages, tokens = [], None
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        item = event.get("item")
        if event.get("type") == "item.completed" and isinstance(item, dict) \
                and item.get("type") == "agent_message":
            messages.append(str(item.get("text", "")))
        usage = event.get("usage") if event.get("type") == "turn.completed" else None
        if isinstance(usage, dict):
            counted = [usage.get(k) for k in ("input_tokens", "output_tokens")]
            tokens = (tokens or 0) + sum(v for v in counted if isinstance(v, int))
    return ("\n\n".join(messages) if messages else stdout), tokens or None


def output_text(profile: dict, stdout: str) -> tuple[str, int | None]:
    """The text to grade and the tokens the run reported, when the profile can parse them."""
    if profile.get("output") == "codex-jsonl":
        return codex_output(stdout)
    if profile.get("output") != "claude-json":
        return stdout, None
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return stdout, None
    usage = payload.get("usage") or {}
    tokens = sum(v for k, v in usage.items() if k.endswith("tokens") and isinstance(v, int))
    return str(payload.get("result", stdout)), tokens or None


def invoke(argv: list[str], cwd: Path, env: dict, timeout: int) -> dict:
    started = time.monotonic()
    try:
        # A new session makes the arm a process group, so the timeout can kill its grandchildren too.
        proc = subprocess.Popen(argv, cwd=cwd, env=env, text=True, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            stdout, stderr = proc.communicate()
            return {"stdout": stdout or "", "stderr": stderr or "", "error": f"timeout after {timeout}s",
                    "durationMs": int((time.monotonic() - started) * 1000)}
    except OSError as exc:
        return {"stdout": "", "stderr": "", "error": f"{argv[0]}: {exc.strerror}",
                "durationMs": int((time.monotonic() - started) * 1000)}
    error = f"exit {proc.returncode}" if proc.returncode else None
    return {"stdout": stdout, "stderr": stderr, "error": error,
            "durationMs": int((time.monotonic() - started) * 1000)}


# --------------------------------------------------------------------------- fixture

def provision(suite: Path, case_id: str, parent: Path) -> tuple[Path, dict]:
    workspace = parent / "workspace"
    if (suite / "fixture").is_dir():
        shutil.copytree(suite / "fixture", workspace)
    else:
        workspace.mkdir()
    env = {**os.environ, **GIT_ENV, "CQ": str(CQ), "EVAL_CASE": case_id,
           "EVAL_WORKSPACE": str(workspace)}
    for argv in (["git", "init", "-q", "-b", "main"], ["git", "add", "-A"],
                 ["git", "commit", "-q", "--allow-empty", "-m", "Fixture"]):
        subprocess.run(argv, cwd=workspace, env=env, check=True, capture_output=True)
    if (suite / "setup.sh").is_file():
        subprocess.run(["bash", str(suite / "setup.sh"), case_id], cwd=workspace, env=env,
                       check=True, capture_output=True, text=True, timeout=120)
    base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=workspace, env=env, check=True,
                          capture_output=True, text=True).stdout.strip()
    env["EVAL_BASE"] = base
    return workspace, env


def snapshot(suite: Path, workspace: Path, env: dict) -> str:
    def capture(argv: list[str]) -> str:
        if argv[0] == "git":
            argv = ["git", *SAFE_GIT, *argv[1:]]
        result = subprocess.run(argv, cwd=workspace, env={**env, "GIT_OPTIONAL_LOCKS": "0"},
                                capture_output=True, text=True, timeout=120)
        return (result.stdout + result.stderr).strip() or "(empty)"

    parts = [("git status --porcelain", capture(["git", "status", "--porcelain"]))]
    refs = capture(["git", "for-each-ref", "--format=%(refname:short)", "refs/heads"]).splitlines()
    for ref in refs:
        parts.append((f"git log --stat -n 5 {ref}", capture(["git", "log", "--stat", "--no-ext-diff", "--no-textconv", "-n", "5", ref])))
    base = env.get("EVAL_BASE")
    if base:
        parts.append((f"git diff {base[:12]} (every change since the fixture, committed or not)",
                      capture(["git", "diff", "--no-ext-diff", "--no-textconv", base])))
    parts.append(("git diff HEAD", capture(["git", "diff", "--no-ext-diff", "--no-textconv", "HEAD"])))
    parts.append(("untracked files", capture(["git", "ls-files", "--others", "--exclude-standard"])))
    if (suite / "inspect.sh").is_file():
        parts.append(("inspect.sh", capture(["bash", str(suite / "inspect.sh")])))
    return "\n\n".join(f"## {title}\n{body}" for title, body in parts)


# --------------------------------------------------------------------------- grading

def squash(text: str) -> str:
    return " ".join(text.split())


def parse_grades(text: str) -> list | None:
    decoder = json.JSONDecoder()
    for match in re.finditer(r"\[", text):
        try:
            value, _ = decoder.raw_decode(text, match.start())
        except json.JSONDecodeError:
            continue
        if isinstance(value, list) and all(isinstance(v, dict) for v in value):
            return value
    return None


def verify_grades(assertions: list[str], raw: list | None, material: str) -> list[dict]:
    """One grade per assertion; anything unparsed or unquoted is `unknown`, with the reason."""
    by_text = {str(g.get("assertion", "")): g for g in raw or []}
    haystack = squash(material)
    grades = []
    for index, assertion in enumerate(assertions):
        grade = by_text.get(assertion)
        if grade is None and raw and index < len(raw):
            named = str(raw[index].get("assertion", ""))
            # a positional match only when that grade does not belong to another assertion
            grade = raw[index] if named not in assertions else None
        if grade is None:
            grades.append({"assertion": assertion, "result": "unknown", "evidence": "",
                           "reason": "the grader returned no grade for this assertion"})
            continue
        result, evidence = grade.get("result"), str(grade.get("evidence") or "")
        entry = {"assertion": assertion, "result": result, "evidence": evidence}
        if result not in RESULTS:
            entry.update(result="unknown", reason=f"the grader answered {result!r}")
        elif result != "unknown" and (not squash(evidence) or squash(evidence) not in haystack):
            entry.update(result="unknown", reason="the evidence is not a verbatim excerpt of the material")
        grades.append(entry)
    return grades


def material_of(output: str, snap: str) -> str:
    return f"# AGENT OUTPUT\n{output[-MATERIAL_LIMIT:]}\n\n# WORKSPACE AFTER THE RUN\n{snap[-MATERIAL_LIMIT:]}"


# --------------------------------------------------------------------------- run

def run_arm(args, profiles: dict, suite: Path, case: dict, arm: str) -> dict:
    profile = profiles[args.harness]
    with tempfile.TemporaryDirectory(prefix="eval-") as temporary:
        try:
            workspace, env = provision(suite, case["id"], Path(temporary))
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
            detail = getattr(exc, "stderr", None) or ""
            detail = detail.decode(errors="replace") if isinstance(detail, bytes) else detail
            error = f"the fixture could not be provisioned: {exc}"
            return {"tokens": None, "durationMs": 0, "output": detail, "snapshot": "(not provisioned)",
                    "error": error, "assertions": [{"assertion": a, "result": "unknown", "evidence": "",
                                                    "reason": error} for a in case["assertions"]]}
        arm_env = dict(env)
        if arm == "with" and CQ_BIN.is_dir():
            arm_env["PATH"] = f"{CQ_BIN}{os.pathsep}{env.get('PATH', '')}"
        if arm != "with":
            arm_env.pop("CQ", None)  # the without arm gets no path to the tool or the skill bodies
        values = {"prompt": case["prompt"], "model": args.model, "workdir": str(workspace),
                  "max_turns": str(args.max_turns)}
        record = invoke(render(profile, arm, values, args.extra_arg), workspace, arm_env, args.timeout)
        text, tokens = output_text(profile, record["stdout"])
        output = text + (f"\n[stderr]\n{record['stderr'][-4000:]}" if record["stderr"] else "")
        try:
            snap = snapshot(suite, workspace, env)
        except (subprocess.TimeoutExpired, OSError) as exc:
            snap = f"(the snapshot failed: {exc})"
    entry = {"tokens": tokens, "durationMs": record["durationMs"], "output": output, "snapshot": snap}
    if record["error"]:
        entry["error"] = record["error"]
        entry["assertions"] = [{"assertion": a, "result": "unknown", "evidence": "",
                                "reason": f"the arm failed: {record['error']}"} for a in case["assertions"]]
        return entry
    entry["assertions"] = grade(args, profiles, case["assertions"], material_of(output, snap))
    return entry


def grade(args, profiles: dict, assertions: list[str], material: str) -> list[dict]:
    profile = profiles[args.grader_harness]
    prompt = GRADER_PROMPT.format(assertions="\n".join(f"- {a}" for a in assertions), material=material)
    with tempfile.TemporaryDirectory(prefix="eval-grader-") as temporary:
        values = {"prompt": prompt, "model": args.grader_model, "workdir": temporary,
                  "max_turns": "1"}
        record = invoke(render(profile, None, values, args.grader_extra_arg), Path(temporary),
                        dict(os.environ), args.timeout)
    if record["error"]:
        return [{"assertion": a, "result": "unknown", "evidence": "",
                 "reason": f"the grader failed: {record['error']}"} for a in assertions]
    text, _ = output_text(profile, record["stdout"])
    return verify_grades(assertions, parse_grades(text), material)


def aggregate(cases: list[dict], arm: str) -> dict:
    graded = [c["arms"][arm] for c in cases if arm in c["arms"]]
    results = [a["result"] for g in graded for a in g["assertions"]]
    tokens = [g["tokens"] for g in graded if g["tokens"] is not None]
    approved = sum(1 for g in graded if g["assertions"] and all(a["result"] == "pass" for a in g["assertions"]))
    return {"passRate": round(results.count("pass") / len(results), 4) if results else 0.0,
            "caseApprovalRate": round(approved / len(graded), 4) if graded else 0.0,
            "cases": len(graded), "assertions": len(results),
            "unknown": results.count("unknown"), "errors": sum(1 for g in graded if "error" in g),
            "tokens": sum(tokens) if tokens else None,
            "durationMs": sum(g["durationMs"] for g in graded)}


def benchmark(data: dict, cases: list[dict], args, arms: list[str]) -> dict:
    result = {"skill": data["skill"], "cases": len(cases), "runId": args.run_id,
              "harness": args.harness, "model": args.model,
              "commandModel": command_model(data["skill"]),
              "grader": {"harness": args.grader_harness, "model": args.grader_model}}
    for arm in arms:
        result[arm] = aggregate(cases, arm)
    if set(arms) == set(ARMS):
        result["delta"] = {k: (round(result["with"][k] - result["without"][k], 4)
                               if None not in (result["with"][k], result["without"][k]) else None)
                           for k in ("passRate", "caseApprovalRate", "tokens", "durationMs")}
    result["unknown"] = sum(result[arm]["unknown"] for arm in arms)
    result["errors"] = sum(result[arm]["errors"] for arm in arms)
    return result


def run(args) -> int:
    profiles = load_profiles(Path(args.harnesses))
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    for name in (args.harness, args.grader_harness):
        if name not in profiles:
            print(f"run_evals: no harness profile {name!r} in {args.harnesses}", file=sys.stderr)
            return 2
    for arm in arms:
        if arm not in ARMS or arm not in profiles[args.harness].get("arms", {}):
            print(f"run_evals: harness {args.harness!r} has no {arm!r} arm", file=sys.stderr)
            return 2
    suites = []
    for directory in suite_dirs(args.suite):
        data, errors, _ = check_suite(directory)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 2
        cases = [c for c in data["cases"] if not args.case or c["id"] in args.case]
        suites.append((directory, data, cases))
    if args.dry_run:
        for directory, _, cases in suites:
            for case in cases:
                for arm in arms:
                    values = {"prompt": case["prompt"], "model": args.model,
                              "workdir": "<workspace>", "max_turns": str(args.max_turns)}
                    argv = render(profiles[args.harness], arm, values, args.extra_arg)
                    print(json.dumps({"suite": suite_name(directory), "case": case["id"], "arm": arm,
                                      "argv": argv}, ensure_ascii=False))
        return 0
    out = Path(args.out or ROOT / ".quenching/evals" / args.run_id)
    summary = {"runId": args.run_id, "harness": args.harness, "model": args.model,
               "grader": {"harness": args.grader_harness, "model": args.grader_model},
               "arms": arms, "suites": []}
    for directory, data, cases in suites:
        name = suite_name(directory)
        target = out / name
        target.mkdir(parents=True, exist_ok=True)
        graded = []
        for case in cases:
            entry = {"case": case["id"], "branch": case["branch"], "arms": {}}
            for arm in arms:
                arm_record = run_arm(args, profiles, directory, case, arm)
                (target / f"{case['id']}.{arm}.output.txt").write_text(arm_record.pop("output"), encoding="utf-8")
                (target / f"{case['id']}.{arm}.snapshot.txt").write_text(arm_record.pop("snapshot"), encoding="utf-8")
                results = [a["result"] for a in arm_record["assertions"]]
                arm_record["passRate"] = round(results.count("pass") / len(results), 4) if results else 0.0
                entry["arms"][arm] = arm_record
            graded.append(entry)
        bench = benchmark(data, graded, args, arms)
        (target / "grading.json").write_text(json.dumps(graded, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (target / "benchmark.json").write_text(json.dumps(bench, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        summary["suites"].append({"suite": name, **{k: bench[k] for k in ("skill", "commandModel", "cases", *arms)}})
    every = summary["suites"]
    summary["overall"] = {}
    for arm in arms:
        assertions = sum(s[arm]["assertions"] for s in every)
        cases = sum(s[arm]["cases"] for s in every)
        summary["overall"][arm] = {
            "passRate": round(sum(s[arm]["passRate"] * s[arm]["assertions"] for s in every) / assertions, 4)
            if assertions else 0.0,
            "caseApprovalRate": round(sum(s[arm]["caseApprovalRate"] * s[arm]["cases"] for s in every) / cases, 4)
            if cases else 0.0,
            "cases": cases, "unknown": sum(s[arm]["unknown"] for s in every),
            "errors": sum(s[arm]["errors"] for s in every)}
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary["overall"], ensure_ascii=False) if args.json else f"run_evals: wrote {out}")
    return 0


def check(args) -> int:
    failed = False
    for directory in suite_dirs(args.suite):
        _, errors, warnings = check_suite(directory)
        for line in warnings:
            print(f"WARN {line}")
        for line in errors:
            print(f"ERROR {line}")
        failed = failed or bool(errors)
        if not errors:
            print(f"OK {suite_name(directory)}")
    return 1 if failed else 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--suite", action="append", default=[],
                   help="a suite directory or its evals.json; repeatable (default: every committed suite)")
    p.add_argument("--case", action="append", default=[], help="run only this case id; repeatable")
    p.add_argument("--check", action="store_true", help="validate the suites and run nothing")
    p.add_argument("--dry-run", action="store_true", help="print each arm's argv and run nothing")
    p.add_argument("--harnesses", default=str(PROFILES), help="the harness profile file")
    p.add_argument("--harness", help="the profile the arms run under")
    p.add_argument("--model", help="the model the arms run on")
    p.add_argument("--arms", default="with", help="comma-separated: with, without (default: with)")
    p.add_argument("--grader-harness", help="the profile the grader runs under (default: --harness)")
    p.add_argument("--grader-model", help="the grader's model, fixed across every compared run")
    p.add_argument("--run-id", help="the run's identifier, e.g. a timestamp; never read from the clock")
    p.add_argument("--out", help="the output directory (default: .quenching/evals/<run-id>)")
    p.add_argument("--timeout", type=int, default=900, help="seconds per invocation")
    p.add_argument("--max-turns", type=int, default=30)
    p.add_argument("--extra-arg", action="append", default=[], help="an argument added to every arm; repeatable")
    p.add_argument("--grader-extra-arg", action="append", default=[], help="an argument added to the grader")
    p.add_argument("--json", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.check:
        return check(args)
    missing = [flag for flag, value in (("--harness", args.harness), ("--model", args.model),
                                        ("--run-id", args.run_id)) if not value]
    args.grader_harness = args.grader_harness or args.harness
    if not args.dry_run and not args.grader_model:
        missing.append("--grader-model")
    if missing:
        print(f"run_evals: missing {', '.join(missing)}", file=sys.stderr)
        return 2
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
