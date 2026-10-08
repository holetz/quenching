"""`cost` — what a session's subagents spent, per agent type, model and window.

Reads `<session>/subagents/agent-*.jsonl`, with the agent type taken from the
`agent-*.meta.json` beside each. The Claude Code transcript writes one record per content
block and repeats the same `message.id` with a growing `usage`, so the unit counted here is
the request (one `message.id`), never the line, and the request keeps its final usage.

Tokens are never summed across models: tiers price differently, so the totals are per model
and the payload has no grand total."""
from __future__ import annotations

import json
from pathlib import Path

from quenching.common.output import FINDINGS, OK, refuse
from quenching.session.transcript import resolve_transcript

UNKNOWN = "unknown"


def subagents_dir(arg: str | None) -> tuple[Path | None, str]:
    """The `subagents/` directory for an explicit directory, or the session `resolve_transcript` finds."""
    if arg:
        p = Path(arg).expanduser()
        if p.is_dir():
            sub = p / "subagents"
            return (sub if sub.is_dir() else p), "explicit directory"
    path, how = resolve_transcript(arg, Path.cwd().resolve())
    if path is None:
        return None, how
    return path.with_suffix("") / "subagents", how


def _agent_type(transcript: Path) -> str:
    meta = transcript.with_name(transcript.stem + ".meta.json")
    try:
        return json.loads(meta.read_text(encoding="utf-8")).get("agentType") or UNKNOWN
    except (OSError, ValueError, AttributeError):
        return UNKNOWN


def _requests(transcript: Path, anomalies: list) -> dict:
    """message.id -> (model, usage) with the usage of the largest `output_tokens` seen."""
    seen: dict = {}
    with transcript.open(encoding="utf-8", errors="replace") as fh:
        for n, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                anomalies.append({"file": transcript.name, "line": n, "message": "unparsable record"})
                continue
            msg = rec.get("message") if rec.get("type") == "assistant" else None
            usage = msg.get("usage") if isinstance(msg, dict) else None
            if not isinstance(usage, dict):
                continue
            key = msg.get("id") or rec.get("requestId") or rec.get("uuid")
            if key is None:
                continue
            prev = seen.get(key)
            if prev is None or (usage.get("output_tokens") or 0) >= (prev[1].get("output_tokens") or 0):
                seen[key] = (msg.get("model") or UNKNOWN, usage)
    return seen


def _n(usage: dict, key: str) -> int:
    v = usage.get(key)
    return v if isinstance(v, int) else 0


def aggregate(directory: Path) -> dict:
    anomalies: list = []
    groups: dict = {}
    for tr in sorted(directory.glob("agent-*.jsonl")):
        agent = _agent_type(tr)
        for model, usage in _requests(tr, anomalies).values():
            g = groups.setdefault((agent, model), {
                "agentType": agent, "model": model, "requests": 0, "input": 0,
                "cacheRead": 0, "cacheWrite": 0, "output": 0, "maxWindow": 0})
            inp, cr, cw = _n(usage, "input_tokens"), _n(usage, "cache_read_input_tokens"), \
                _n(usage, "cache_creation_input_tokens")
            g["requests"] += 1
            g["input"] += inp
            g["cacheRead"] += cr
            g["cacheWrite"] += cw
            g["output"] += _n(usage, "output_tokens")
            g["maxWindow"] = max(g["maxWindow"], inp + cr + cw)
    rows = sorted(groups.values(), key=lambda g: (g["agentType"], g["model"]))
    models: dict = {}
    for g in rows:
        m = models.setdefault(g["model"], {"model": g["model"], "requests": 0, "input": 0,
                                           "cacheRead": 0, "cacheWrite": 0, "output": 0})
        for k in ("requests", "input", "cacheRead", "cacheWrite", "output"):
            m[k] += g[k]
    return {"groups": rows, "byModel": sorted(models.values(), key=lambda m: m["model"]),
            "anomalies": anomalies}


def cmd_cost(args) -> int:
    directory, how = subagents_dir(args.transcript)
    if directory is None:
        return refuse({"code": "se-no-transcript", "message": how}, args.json)
    if not directory.is_dir():
        return refuse({"code": "se-no-subagents", "message": f"no subagents directory at {directory}"},
                      args.json)
    out = aggregate(directory)
    if not out["groups"]:
        return refuse({"code": "se-no-requests",
                       "message": f"no subagent request with usage under {directory}"}, args.json)
    out.update(ok=True, subagents=str(directory), resolvedBy=how)
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(f"subagents: {directory}  ({how})")
        print(f"{'agentType':<22}{'model':<26}{'req':>6}{'input':>9}{'cacheRead':>12}"
              f"{'cacheWrite':>12}{'output':>9}{'maxWindow':>11}")
        for g in out["groups"]:
            print(f"{g['agentType']:<22}{g['model']:<26}{g['requests']:>6}{g['input']:>9}"
                  f"{g['cacheRead']:>12}{g['cacheWrite']:>12}{g['output']:>9}{g['maxWindow']:>11}")
        print("\nper model (tiers are never summed together):")
        for m in out["byModel"]:
            print(f"  {m['model']}: req={m['requests']} input={m['input']} cacheRead={m['cacheRead']}"
                  f" cacheWrite={m['cacheWrite']} output={m['output']}")
        for a in out["anomalies"]:
            print(f"  ! {a['file']} line {a['line']}: {a['message']}")
    return FINDINGS if out["anomalies"] else OK
