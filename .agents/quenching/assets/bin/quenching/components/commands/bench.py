"""bench — the fixed cost and the specs cycle of an installed quenching, against any target.

Two layers (`superficie`, `ciclo`) over `quenching.components.bench` and `bench_cycle`. The target is
the repository measured (`--target`, default the cwd); nothing is written into it, and the `ciclo`
fixture lives in the temp area and is removed. Exit 0 no finding, 1 a finding (a budget passed, a
citation that does not resolve, a verb of the cycle that failed), 2 a layer that could not run.
"""
from __future__ import annotations

import json
from pathlib import Path

from quenching.common.output import finding, refuse
from quenching.components import bench, bench_cycle

LAYERS = ("superficie", "ciclo")


def _csv(allowed: tuple[str, ...]):
    def parse(text: str) -> tuple[str, ...]:
        items = tuple(dict.fromkeys(p.strip() for p in text.split(",") if p.strip()))
        bad = [i for i in items if i not in allowed]
        if not items or bad:
            import argparse
            raise argparse.ArgumentTypeError(f"use one or more of {', '.join(allowed)}, comma-separated")
        return items
    return parse


def add_arguments(sp) -> None:
    sp.add_argument("--layers", type=_csv(LAYERS), default=("superficie",),
                    help="superficie (fixed cost and flow ceilings; default), ciclo (the specs cycle on a "
                         "throwaway fixture), or both comma-separated")
    sp.add_argument("--harness", type=_csv(bench.HARNESSES), default=bench.HARNESSES,
                    help="claude,opencode,copilot")
    sp.add_argument("--budget", help="a JSON file {prefix: {harness: tokens}, flow: {flow: tokens}} "
                                     "replacing the defaults, key by key")
    sp.add_argument("--target", help="the repository to measure (default: the cwd)")
    sp.add_argument("--keep-fixture", action="store_true", help="ciclo: do not remove the fixture")
    sp.add_argument("--json", action="store_true", help="machine-readable output")


def _human(payload: dict, findings: list[dict]) -> str:
    lines = ["components bench"]
    sup = payload.get("superficie")
    if sup:
        for name, row in sup["harnesses"].items():
            parts = ", ".join(f"{k} {v}" for k, v in row["tokens"].items())
            lines.append(f"  {name}: {row['total']} tokens ({parts}); budget {row['budget']}")
        for flow, row in sup["flows"].items():
            lines.append(f"  flow {flow}: {row['tokens']} tokens; budget {row['budget']}")
    cycle = payload.get("ciclo")
    if cycle:
        lines.append(f"  ciclo: {'closed' if cycle['closed'] else 'open'}")
        for flow, row in cycle["flows"].items():
            lines.append(f"    {flow}: {row['verbs']} verbs, {row['seconds']}s, {row['tokens']} tokens")
    errors = sum(f["severity"] == "error" for f in findings)
    lines.append(f"  {errors} error(s), {len(findings) - errors} warning(s)")
    lines += [f"  [{f['severity']}] {f['message']}  ({f['code']})" for f in findings]
    return "\n".join(lines)


def cmd_bench(args, root: str) -> int:
    target = Path(args.target or ".").resolve()
    if not target.is_dir():
        return refuse({"code": "ct-bench-no-target", "message": f"{target} is not a directory"}, args.json)
    try:
        budget = bench.load_budget(args.budget)
    except (OSError, ValueError) as exc:
        return refuse({"code": "ct-bench-budget", "message": f"cannot read the budget: {exc}"}, args.json)
    payload: dict = {"target": str(target)}
    findings: list[dict] = []
    failed: dict[str, str] = {}
    for layer in args.layers:
        try:
            if layer == "superficie":
                payload[layer], found = bench.measure(target, args.harness, budget)
            else:
                payload[layer], found = bench_cycle.measure(target, keep=args.keep_fixture)
            findings.extend(found)
        except Exception as exc:  # a layer that breaks is exit 2, never a finding
            failed[layer] = f"{type(exc).__name__}: {exc}"
    if failed:
        payload["failed"] = failed
        findings.append(finding("ct-bench-layer-failed", "error",
                                "; ".join(f"{k}: {v}" for k, v in failed.items())))
    errors = sum(f["severity"] == "error" for f in findings)
    out = {"ok": errors == 0, **payload, "findings": findings}
    print(json.dumps(out, indent=2, ensure_ascii=False) if args.json else _human(payload, findings))
    return 2 if failed else (1 if errors else 0)
