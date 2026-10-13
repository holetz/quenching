#!/usr/bin/env python3
"""Measure Claude JSONL context exposure; entry proxies are never restart cost.

Repository-only spike instrument, not the S3 live-session verb. Run with --projects,
--output and --inventory. Only the aggregate output is intended for version control.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins/quenching/assets/bin"))
from quenching.session.model import Command, normalize  # noqa: E402
from quenching.session.parse import blocks, close_attribution, COMMAND_NAME_RE  # noqa: E402

TOKEN_KEYS = ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
STAGES = {f"{prefix}:{stage}": stage for prefix in ("specs", "quenching:specs")
          for stage in ("develop", "execute", "conclude", "autopilot", "orchestrate")}


def distribution(values: list[int]) -> dict:
    ordered = sorted(values)
    if not ordered:
        return {"n": 0, "median": None, "p90": None, "p95": None, "max": None}
    return {"n": len(values), "median": statistics.median(values),
            "p90": ordered[math.ceil(len(values) * .90) - 1],
            "p95": ordered[math.ceil(len(values) * .95) - 1], "max": ordered[-1]}


def measure(path: Path, root: Path) -> dict:
    raw = path.read_bytes()
    requests, commands, timeline = {}, {}, []
    anomalies = Counter()
    assistant_records = 0
    summaries = 0
    first_prompt = None
    started_at = None
    query_line = None
    task_checks = []

    def command(name):
        return commands.setdefault(name, Command(name))

    for line, text in enumerate(raw.decode("utf-8", errors="replace").splitlines(), 1):
        if not text.strip():
            continue
        try:
            rec = json.loads(text)
        except ValueError:
            anomalies["unparsed-record"] += 1
            continue
        if not isinstance(rec, dict):
            anomalies["non-object-record"] += 1
            continue
        started_at = started_at or rec.get("timestamp")
        if rec.get("isCompactSummary"):
            summaries += 1
            continue
        attribution = rec.get("attributionSkill")
        name = normalize(attribution) if isinstance(attribution, str) and attribution else "unknown"
        if name != "unknown":
            command(name).touch(line, rec.get("timestamp"))
            timeline.append((line, name))
        msg = rec.get("message")
        if not isinstance(msg, dict):
            continue
        for block in blocks(rec):
            if block.get("type") == "tool_use" and block.get("name") == "Skill":
                target = (block.get("input") or {}).get("skill")
                if isinstance(target, str) and target:
                    cmd = command(normalize(target))
                    cmd.invocations.append({"form": "skill", "line": line,
                                            "invokedBy": None if name == "unknown" else name})
            if block.get("type") == "tool_use" and block.get("name") == "Bash":
                shell = (block.get("input") or {}).get("command", "")
                if query_line is None and re.search(r"\b(?:cq specs|specs\.py) next\b", shell):
                    query_line = line
                check = re.search(r"\b(?:cq specs|specs\.py) task\b.*?--check\s+[\"']?(\d+\.\d+)", shell, re.S)
                if check:
                    task_checks.append({"task": check.group(1), "line": line})
        if rec.get("type") == "user":
            content = msg.get("content")
            content = content if isinstance(content, str) else "\n".join(
                b.get("text", "") for b in blocks(rec) if b.get("type") == "text")
            if first_prompt is None and content and not rec.get("isMeta"):
                first_prompt = content
            for target in COMMAND_NAME_RE.findall(content):
                command(normalize(target)).invocations.append({"form": "typed", "line": line})
        if rec.get("type") != "assistant":
            continue
        assistant_records += 1
        key, usage = msg.get("id"), msg.get("usage")
        if not isinstance(key, str) or not key:
            anomalies["assistant-without-message-id"] += 1
            continue
        if not isinstance(usage, dict):
            anomalies["assistant-without-usage"] += 1
            continue
        if any(type(usage.get(k, 0)) is not int or usage.get(k, 0) < 0
               for k in (*TOKEN_KEYS, "output_tokens")):
            anomalies["invalid-token-usage"] += 1
            continue
        if not any(k in usage for k in TOKEN_KEYS):
            anomalies["usage-without-input-fields"] += 1
            continue
        prev = requests.get(key)
        if prev is None or usage.get("output_tokens", 0) >= prev["output"]:
            iterations = usage.get("iterations")
            executor_iterations = [i for i in iterations if isinstance(i, dict) and i.get("type") == "message"] \
                if isinstance(iterations, list) else []
            valid_iterations = [i for i in executor_iterations if all(
                type(i.get(k, 0)) is int and i.get(k, 0) >= 0 for k in TOKEN_KEYS)]
            if len(valid_iterations) != len(executor_iterations):
                anomalies["invalid-executor-iteration"] += 1
            iteration_windows = [sum(i.get(k, 0) for k in TOKEN_KEYS) for i in valid_iterations]
            requests[key] = {"model": msg.get("model") or "unknown", "command": name,
                             "line": line, "firstLine": prev["firstLine"] if prev else line,
                             "window": sum(usage.get(k, 0) for k in TOKEN_KEYS),
                             "executorIterationWindows": iteration_windows,
                             "quotedUsage": {k: usage.get(k, 0) for k in TOKEN_KEYS},
                             "messageId": key, "hostVersion": rec.get("version"),
                             "freshInput": usage.get("input_tokens", 0) +
                             usage.get("cache_creation_input_tokens", 0),
                             "output": usage.get("output_tokens", 0)}
    attribution_anomalies = []
    close_attribution(list(commands.values()), timeline, attribution_anomalies)
    anomalies.update(a["code"] for a in attribution_anomalies)
    meta = {}
    agent_type = "not-applicable"
    meta_hash = None
    if path.parent.name == "subagents":
        metadata = path.with_name(path.stem + ".meta.json")
        try:
            metadata_raw = metadata.read_bytes()
            meta_hash = hashlib.sha256(metadata_raw).hexdigest()
            meta = json.loads(metadata_raw)
        except (OSError, ValueError):
            anomalies["unreadable-agent-metadata"] += 1
        if not isinstance(meta, dict):
            anomalies["non-object-agent-metadata"] += 1
            meta = {}
        agent_type = meta.get("agentType") or "unknown"
        role = {"quenching:spec-runner": "worker", "quenching:orchestrator": "conductor"}.get(
            agent_type, "unknown-subagent" if agent_type == "unknown" else "other-subagent")
    else:
        role = "main"
    for request in requests.values():
        cmd = commands.get(request["command"])
        request["attribution"] = "unknown" if cmd is None else (
            "pointer-upper-bound" if not cmd.closed else "pointer-closed")
    assignment = re.match(r"(?i)Spec\s*[:#]?\s*(\d+)\b", first_prompt or "")
    explicit_resume = bool(re.search(r"(?i)\bResume(?: execute)?\s*:", (first_prompt or "")[:800]))
    return {"source": path.relative_to(root).as_posix(), "sha256": hashlib.sha256(raw).hexdigest(),
            "metadataSha256": meta_hash, "role": role, "agentType": agent_type,
            "startedAt": started_at, "assignmentSpec": assignment.group(1) if assignment else None,
            "explicitResume": explicit_resume, "firstNextQueryLine": query_line, "taskChecks": task_checks,
            "assistantRecords": assistant_records, "compactSummariesSkipped": summaries,
            "anomalies": dict(anomalies), "requests": list(requests.values())}


def summary(samples: list[dict]) -> dict:
    peaks = [max(r["window"] for r in s["requests"]) for s in samples]
    first = [min(s["requests"], key=lambda r: r["firstLine"]) for s in samples]
    integrals = [sum(r["window"] for r in s["requests"]) for s in samples]
    total = sum(integrals)
    measured_iterations = [r for s in samples for r in s["requests"] if r["executorIterationWindows"]]
    sample_iteration_peaks = [max(w for r in s["requests"] for w in r["executorIterationWindows"])
                             for s in samples if any(r["executorIterationWindows"] for r in s["requests"])]
    return {"samples": len(samples), "requests": sum(len(s["requests"]) for s in samples),
            "peak": distribution(peaks), "tokenExposure": total,
            "observedExecutorIterationPeak": distribution(sample_iteration_peaks),
            "requestsWithIterationBreakdown": len(measured_iterations),
            "requestsWithMultipleExecutorIterations": sum(len(r["executorIterationWindows"]) > 1
                                                         for r in measured_iterations),
            "firstObservedWindow": distribution([r["window"] for r in first]),
            "firstObservedFreshInput": distribution([r["freshInput"] for r in first]),
            "attribution": dict(Counter(r["attribution"] for s in samples for r in s["requests"])),
            "thresholdComparisons": [{"threshold": t, "samplesAbove": sum(p > t for p in peaks),
                                      "exposureFromSamplesAbove": sum(i for p, i in zip(peaks, integrals) if p > t),
                                      "exposureShareAbove": sum(i for p, i in zip(peaks, integrals) if p > t) / total if total else None}
                                     for t in (100000, 150000, 200000)]}


def aggregate(rows: list[dict]) -> dict:
    groups = defaultdict(list)
    for row in rows:
        if not row["requests"]:
            continue
        for dimension in ("role", "agentType"):
            groups[(dimension, row[dimension], "all-token-exposure")].append(row)
        groups[("topology", "main" if row["role"] == "main" else "subagent", "all-token-exposure")].append(row)
        by_model = defaultdict(list)
        by_command = defaultdict(list)
        for request in row["requests"]:
            by_model[request["model"]].append(request)
            by_command[(request["command"], request["model"])].append(request)
        for model, requests in by_model.items():
            groups[("roleByModel", row["role"], model)].append({"requests": requests})
        for (command, model), requests in by_command.items():
            groups[("commandByModel", command, model)].append({"requests": requests})
        by_stage = defaultdict(list)
        for (command, model), requests in by_command.items():
            if command in STAGES:
                by_stage[(STAGES[command], model)].extend(requests)
        for (stage, model), requests in by_stage.items():
            groups[("stageByModel", stage, model)].append({"requests": requests})
    return {"files": len(rows), "filesWithRequests": sum(bool(s["requests"]) for s in rows),
            "filesWithoutRequests": sum(not s["requests"] for s in rows),
            "anomalies": dict(sum((Counter(s["anomalies"]) for s in rows), Counter())),
            "groups": [{"dimension": dim,
                        **({"nameParts": name.split(":")} if dim == "commandByModel" else {"name": name}),
                        "model": model, **summary(samples)}
                       for (dim, name, model), samples in sorted(groups.items())]}


def check_restart(evidence: dict) -> int:
    restart = evidence.get("restartCost", {})
    if restart.get("status") != "measured" or not restart.get("pairs"):
        print("needs-human: incremental restart cost has no identified paired evidence", file=sys.stderr)
        return 2
    return 0


def resumptions(rows: list[dict]) -> dict:
    pairs = []
    for row in rows:
        if row["role"] != "worker" or not row["explicitResume"] or not row["firstNextQueryLine"]:
            continue
        same_spec = [p for p in rows if p["assignmentSpec"] == row["assignmentSpec"]
                     and p["role"] == "worker" and p["taskChecks"] and p["startedAt"]
                     and row["startedAt"] and p["startedAt"] < row["startedAt"]]
        if not same_spec:
            continue
        previous = max(same_spec, key=lambda p: p["startedAt"])
        startup = [r for r in row["requests"] if r["firstLine"] <= row["firstNextQueryLine"]]
        if not startup:
            continue
        pairs.append({"spec": row["assignmentSpec"], "predecessorSha256": previous["sha256"],
                      "resumeSha256": row["sha256"], "predecessorLastTaskCheck": previous["taskChecks"][-1],
                      "firstNextQueryLine": row["firstNextQueryLine"], "startupRequests": len(startup),
                      "startupTokenExposure": sum(r["window"] for r in startup),
                      "startupFreshInput": sum(r["freshInput"] for r in startup),
                      "startupPeak": max(r["window"] for r in startup),
                      "model": startup[0]["model"]})
    return {"status": "measured" if pairs else "not-measured", "kind": "observed-resumption-preparation",
            "pairs": pairs,
            "preparationPeak": distribution([p["startupPeak"] for p in pairs]),
            "preparationTokenExposure": distribution([p["startupTokenExposure"] for p in pairs]),
            "preparationFreshInput": distribution([p["startupFreshInput"] for p in pairs]),
            "scope": "Explicit worker resumes with a preceding task-check invocation for the same spec; preparation ends at first cq specs next invocation. Task-check command success is not inferred.",
            "causalSavings": "not-measured; this is observed preparation, not a warm-versus-cold treatment comparison",
            "limitations": "Small opus-only worker sample after security-hook stops; no clean human-led or conductor restart pair was identified. Two main configurable-spec-backend sessions are contaminated by dirty mid-task work, scope changes and a model change."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projects", type=Path, default=Path.home() / ".claude/projects")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--check-restart", type=Path)
    parser.add_argument("--check-contract", type=Path)
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    if args.check_restart:
        return check_restart(json.loads(args.check_restart.read_text()))
    if args.check_contract:
        if not args.evidence:
            parser.error("--check-contract requires --evidence")
        evidence = json.loads(args.evidence.read_text())
        if check_restart(evidence):
            return 2
        budgets = evidence.get("budgets", {})
        target = evidence.get("reductionTarget")
        if any(type(budgets.get(k)) is not int or budgets[k] <= 0
               for k in ("main", "worker", "conductor")) or target is None:
            print("needs-human: three justified budgets and reduction target are not settled", file=sys.stderr)
            return 2
        text = " ".join(args.check_contract.read_text().replace("`", "").replace("**", "").split())
        return 0 if all(str(v) in text for v in (*budgets.values(), target)) else 1
    if not args.output or not args.inventory:
        parser.error("measurement requires --output and --inventory")
    paths = sorted(p for d in args.projects.glob("*uench*") if d.is_dir() for p in d.rglob("*.jsonl"))
    if not paths:
        print("refused: no transcripts matched the declared corpus", file=sys.stderr)
        return 2
    rows = [measure(p, args.projects) for p in paths]
    inventory = [{k: v for k, v in row.items() if k != "requests"} for row in rows]
    inventory_text = json.dumps(inventory, indent=2, sort_keys=True) + "\n"
    args.inventory.parent.mkdir(parents=True, exist_ok=True)
    args.inventory.write_text(inventory_text)
    report = {"schema": 1, "measuredAt": datetime.now(timezone.utc).isoformat(),
              "arm": "transcript-jsonl", "corpus": "~/.claude/projects/*uench*/**/*.jsonl",
              "inventorySha256": hashlib.sha256(inventory_text.encode()).hexdigest(),
              "quantiles": "median; p90/p95 nearest rank", "metric": "token exposure, not monetary cost",
              "metricDefinitions": {
                  "peak": "Maximum top-level input+cacheRead+cacheCreation per message.id. Matches captured baseline; may sum executor iterations, so not always one context window.",
                  "observedExecutorIterationPeak": "Maximum input+cacheRead+cacheCreation within observed type=message iterations; excludes advisor iterations. A lower bound where some requests lack breakdown.",
                  "firstObservedWindow": "First observed top-level request input; entry proxy, not causal restart cost.",
                  "references": ["https://platform.claude.com/docs/en/build-with-claude/prompt-caching",
                                 "https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool"]},
              "capturedBaseline": {"date": "2026-10-13", "files": 1383, "main": 57, "subagents": 1326,
                                   "mainExposureApprox": 599000000, "mainShareAbove200kApprox": .86},
              "restartCost": resumptions(rows),
              "budgets": None, "reductionTarget": None, **aggregate(rows)}
    report["corpusReconciliation"] = {"rawFilesMinusCaptured": len(rows) - 1383,
                                      "usageBearingFilesMinusCaptured": report["filesWithRequests"] - 1383,
                                      "note": "Captured baseline has no inventory checksum; additions cannot be identified exactly from aggregate totals."}
    examples = sorted(((r["window"], row["source"], r["line"], row["sha256"], r)
                       for row in rows for r in row["requests"]), key=lambda x: x[:3])[-8:]
    report["peakEvidence"] = [{"window": w, "transcriptSha256": sha, "line": line,
                               "commandParts": r["command"].split(":"),
                               **{k: r[k] for k in ("model", "quotedUsage", "messageId",
                                                   "hostVersion", "executorIterationWindows")}}
                              for w, source, line, sha, r in reversed(examples)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(args.output), "files": report["files"],
                      "filesWithRequests": report["filesWithRequests"], "anomalies": report["anomalies"]}))
    return 1 if report["anomalies"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
