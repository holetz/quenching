"""bench, layer `superficie` — what each harness loads before the first request, and what a flow costs.

Per harness: the instruction files, the skills listing, the agents listing and the MCP catalog of
the `quenching` server, in tokens (characters / 4, the unit of `cq components session cache
--inflow`). Per specs flow (`create`, `develop`, `execute`, `conclude`): the instruction ceiling —
the router plus the flow reference plus every cited `§` section, measured by the same code
`cq components cost` uses. A measure above its budget, a skill name visible twice to one harness
and a citation that does not resolve are findings; the verb exits 1 on any of them.

The budget is a non-regression ruler, not a cut target: `DEFAULT_BUDGET` carries the numbers of
this repository, and `--budget FILE` carries a target's own, in the same shape.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

from quenching.common.output import finding
from quenching.components.commands.cost import STAGE_FILE_RE, measure_command
from quenching.components.surface import discover_references, surface_references

HARNESSES = ("claude", "opencode", "copilot")
FLOWS = ("create", "develop", "execute", "conclude")
SPECS_SKILL = "quenching-specs"
CHARS_PER_TOKEN = 4

#: What each harness reads before the first request. `skills` and `agents` are folders in
#: precedence order (the last one wins a repeated name); `mcp` are the files that register servers.
HARNESS_RULES: dict[str, dict[str, tuple[str, ...]]] = {
    "claude": {
        "instructions": ("CLAUDE.md",),
        "fallback": ("AGENTS.md",),
        "skills": (".claude/skills",),
        "agents": (".claude/agents",),
        "mcp": (".mcp.json",),
    },
    "opencode": {
        "instructions": ("AGENTS.md",),
        "fallback": ("CLAUDE.md",),
        "skills": (".claude/skills", ".agents/skills", ".opencode/skills"),
        "agents": (".opencode/agents", ".opencode/agent"),
        "mcp": ("opencode.json", "opencode.jsonc"),
    },
    "copilot": {
        "instructions": (".github/copilot-instructions.md", "AGENTS.md"),
        "fallback": (),
        "skills": (".claude/skills", ".agents/skills", ".github/skills"),
        "agents": (".github/agents",),
        "mcp": (".vscode/mcp.json",),
    },
}

#: Tokens. `prefix` is the fixed cost per harness (instructions + skills + agents + MCP catalog),
#: `flow` the instruction ceiling per specs flow. Measured on this repository at 7.18.3, with a
#: margin so a rounding never trips the gate; a target passes its own through `--budget`.
DEFAULT_BUDGET: dict[str, dict[str, int]] = {
    "prefix": {"claude": 7_000, "opencode": 7_000, "copilot": 7_000},
    "flow": {"create": 15_000, "develop": 15_000, "execute": 15_000, "conclude": 15_000},
}


def tokens(chars: int) -> int:
    return -(-chars // CHARS_PER_TOKEN)


@dataclass(frozen=True)
class Entry:
    name: str
    folder: str
    chars: int  # name + description, what the listing carries


def _frontmatter(text: str) -> dict[str, str]:
    """The flat `key: value` lines of a Markdown frontmatter — enough for `name` and `description`."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    out: dict[str, str] = {}
    key = None
    for line in text[3:end].splitlines():
        match = re.match(r"([A-Za-z_-]+):\s*(.*)$", line)
        if match:
            key = match.group(1)
            out[key] = match.group(2).strip().strip("'\"").lstrip(">|-").strip()
        elif key and line.startswith((" ", "\t")):
            out[key] = (out[key] + " " + line.strip()).strip()
    return out


def _entries(root: Path, folder: str, pattern: str) -> list[Entry]:
    base = root / folder
    if not base.is_dir():
        return []
    out = []
    for path in sorted(base.glob(pattern)):
        data = _frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        stem = path.parent.name if path.name == "SKILL.md" else re.sub(r"(\.agent)?\.md$", "", path.name)
        name = data.get("name") or stem
        out.append(Entry(name, folder, len(name) + len(data.get("description", ""))))
    return out


def _visible(entries: list[Entry]) -> tuple[list[Entry], dict[str, list[str]]]:
    """The last folder wins a repeated name; the folders each repeated name lives in come back."""
    by_name: dict[str, Entry] = {}
    folders: dict[str, list[str]] = {}
    for entry in entries:
        by_name[entry.name] = entry
        folders.setdefault(entry.name, []).append(entry.folder)
    return list(by_name.values()), {n: f for n, f in folders.items() if len(f) > 1}


def _read(root: Path, names: tuple[str, ...]) -> tuple[int, list[str]]:
    total, files = 0, []
    for name in names:
        path = root / name
        if path.is_file():
            total += len(path.read_text(encoding="utf-8", errors="replace"))
            files.append(name)
    return total, files


def _mcp_only(root: Path, files: tuple[str, ...]) -> tuple[bool, str | None]:
    """Whether a harness config registers the `quenching` server, and its `--only` mount."""
    for name in files:
        path = root / name
        if not path.is_file():
            continue
        text = "\n".join(line for line in path.read_text(encoding="utf-8").splitlines()
                         if not line.lstrip().startswith("//"))
        try:
            doc = json.loads(text)
        except ValueError:
            continue
        block = doc.get("mcpServers") or doc.get("servers") or doc.get("mcp") or {}
        server = block.get("quenching") if isinstance(block, dict) else None
        if not isinstance(server, dict) or server.get("enabled") is False:
            continue
        command = server.get("command")
        argv = ([str(p) for p in command] if isinstance(command, list)
                else [str(command), *(str(a) for a in server.get("args") or [])])
        only = argv[argv.index("--only") + 1] if "--only" in argv[:-1] else None
        return True, only
    return False, None


def mcp_catalog_chars(only: str | None) -> int:
    """The `tools/list` of the `quenching` server, built in-process by the code the server runs."""
    from quenching.mcp import catalog, cli
    pillars = catalog.mount_pillars(only) if only else None
    tools = cli.surface(only=pillars).list_tools()
    return len(json.dumps(tools, ensure_ascii=False))


def measure_harness(root: Path, harness: str) -> dict:
    rules = HARNESS_RULES[harness]
    instr, files = _read(root, rules["instructions"])
    if not files:
        instr, files = _read(root, rules["fallback"])
    skills = [e for folder in rules["skills"] for e in _entries(root, folder, "*/SKILL.md")]
    agents = [e for folder in rules["agents"] for e in _entries(root, folder, "*.md")]
    skills_seen, skill_dupes = _visible(skills)
    agents_seen, _ = _visible(agents)
    registered, only = _mcp_only(root, rules["mcp"])
    mcp = mcp_catalog_chars(only) if registered else 0
    parts = {"instructions": tokens(instr),
             "skills": tokens(sum(e.chars for e in skills_seen)),
             "agents": tokens(sum(e.chars for e in agents_seen)),
             "mcp": tokens(mcp)}
    return {"harness": harness, "instructionFiles": files, "skillCount": len(skills_seen),
            "agentCount": len(agents_seen), "mcpRegistered": registered, "tokens": parts,
            "total": sum(parts.values()), "duplicateSkills": skill_dupes}


def _router_dir(root: Path) -> Path | None:
    for folder in (".agents/skills", ".claude/skills"):
        candidate = root / folder / SPECS_SKILL
        if (candidate / "SKILL.md").is_file():
            return candidate
    return None


def measure_flows(root: Path) -> tuple[dict[str, dict], list[dict]]:
    """The instruction ceiling per flow, and the citations that do not resolve."""
    router = _router_dir(root)
    if router is None:
        return {}, []
    surface_root = str(root / ".agents")
    references = {item["relpath"].replace(os.sep, "/"): item for item in surface_references(surface_root)}
    # A generated router is the deploy's, so the target's surface leaves it out; its flows cite
    # their own references at the source, `.agents/skills/<name>/references/`.
    for item in discover_references(str(router / "references")):
        references.setdefault(f".agents/skills/{SPECS_SKILL}/references/{item['relpath']}".replace(os.sep, "/"), item)
    router_bytes = len((router / "SKILL.md").read_bytes())
    rows, findings = {}, []
    for flow in FLOWS:
        path = router / "references" / f"{flow}.md"
        if not path.is_file():
            continue
        command = {"command": f"/{SPECS_SKILL} {flow}", "path": str(path),
                   "body": path.read_text(encoding="utf-8")}
        row, row_findings = measure_command(command, references, surface_root)
        rows[flow] = {"routerBytes": router_bytes, "flowBytes": row["bodyBytes"],
                      "citedBytes": row["totalBytes"] - row["bodyBytes"],
                      "tokens": tokens(router_bytes + row["totalBytes"])}
        findings.extend(row_findings)
        stage_files = list(dict.fromkeys(STAGE_FILE_RE.findall(command["body"])))
        if stage_files:
            _measure_stages(root, flow, rows[flow], row, stage_files, references, surface_root, findings)
    return rows, findings


def _measure_stages(root: Path, flow: str, out: dict, index: dict, stage_files: list[str],
                    references: dict, surface_root: str, findings: list[dict]) -> None:
    """A split flow's ceiling is its most expensive stage: the router, the flow's index, one step
    file and the sections that step cites."""
    stages: dict[str, int] = {}
    # A step file may link sub-steps (`step-<n><letter>-…`); each is its own stage, run together with its step.
    for relpath in list(stage_files):
        path = root / relpath
        if path.is_file():
            for linked in STAGE_FILE_RE.findall(path.read_text(encoding="utf-8")):
                if linked not in stage_files:
                    stage_files.append(linked)
    # A step links back to the flow index and to its parent step, both already in the stage's
    # count: the index through `index`, the parent through the body it is joined to. Counted
    # again through the link, they would double.
    counted = {f".agents/skills/{SPECS_SKILL}/references/{flow}.md", *stage_files}
    references = {relpath: (dict(item, body="") if relpath in counted else item)
                  for relpath, item in references.items()}
    for relpath in stage_files:
        path = root / relpath
        name = path.stem
        if not path.is_file():
            findings.append(finding(
                "ct-cost-no-reference", "error",
                f"/{SPECS_SKILL} {flow} cites missing stage file {relpath}",
                command=f"/{SPECS_SKILL} {flow}", path=relpath,
                remedy="repair the link or add the step file before measuring cost"))
            continue
        body = path.read_text(encoding="utf-8")
        sub = re.match(r"step-(\d+)[a-z]+-", name)
        if sub:
            parent = next((r for r in stage_files if Path(r).name.startswith(f"step-{sub.group(1)}-")), None)
            if parent and (root / parent).is_file():
                body = (root / parent).read_text(encoding="utf-8") + "\n" + body
        command = {"command": f"/{SPECS_SKILL} {flow} {name}", "path": str(path), "body": body}
        row, row_findings = measure_command(command, references, surface_root)
        findings.extend(row_findings)
        stages[name] = tokens(out["routerBytes"] + index["totalBytes"] + row["totalBytes"])
    if stages:
        out["stages"] = stages
        out["tokens"] = max(stages.values())


def measure(root: Path, harnesses: tuple[str, ...], budget: dict | None = None) -> tuple[dict, list[dict]]:
    """Run the layer: the payload and its findings."""
    budget = budget or DEFAULT_BUDGET
    findings: list[dict] = []
    per_harness = {h: measure_harness(root, h) for h in harnesses}
    for harness, row in per_harness.items():
        limit = (budget.get("prefix") or {}).get(harness)
        row["budget"] = limit
        if limit is not None and row["total"] > limit:
            findings.append(finding(
                "ct-bench-prefix-over", "error",
                f"{harness}: fixed prefix is {row['total']} tokens, budget {limit}",
                harness=harness, tokens=row["total"], budget=limit,
                remedy="cut the instructions, skills, agents or MCP catalog, or raise the budget with the reason"))
        for name, folders in row["duplicateSkills"].items():
            findings.append(finding(
                "ct-bench-skill-duplicate", "warning",
                f"{harness}: skill {name!r} is visible in {', '.join(folders)}",
                harness=harness, skill=name, folders=folders,
                remedy="project each skill once per harness"))
    flows, flow_findings = measure_flows(root)
    findings.extend(flow_findings)
    for flow, row in flows.items():
        limit = (budget.get("flow") or {}).get(flow)
        row["budget"] = limit
        if limit is not None and row["tokens"] > limit:
            findings.append(finding(
                "ct-bench-flow-over", "error",
                f"flow {flow}: instruction ceiling is {row['tokens']} tokens, budget {limit}",
                flow=flow, tokens=row["tokens"], budget=limit,
                remedy="load fewer sections or cut the flow, or raise the budget with the reason"))
    return {"harnesses": per_harness, "flows": flows, "unit": "tokens = chars / 4"}, findings


def load_budget_dict(declared: dict) -> dict:
    """`DEFAULT_BUDGET` with a declared budget laid over it, key by key."""
    return {key: {**DEFAULT_BUDGET[key], **(declared.get(key) or {})} for key in DEFAULT_BUDGET}


def load_budget(path: str | None) -> dict:
    """`DEFAULT_BUDGET`, or the JSON a target passes in the same shape (missing keys keep the default)."""
    if not path:
        return DEFAULT_BUDGET
    return load_budget_dict(json.loads(Path(path).read_text(encoding="utf-8")))
