#!/usr/bin/env python3
"""Generate and validate the Omnigent operator agent of the quenching plugin.

`plugins/quenching/` is the only editable source. This generator lays the command surface out as
ONE Omnigent agent bundle with no payload, `plugins/omnigent/quenching/`:

  config.yaml              the operator agent: OpenCode harness, `skills: none`, the sub-agents it
                           may call and the `quenching` MCP server (stdio, uvx on the version tag)
  instructions.md          the operator role and the routing to skills, sub-agents and the MCP
  skills/<id>/SKILL.md     one skill per source command (the OpenCode translation, re-rooted)
  agents/<name>/           one sub-agent per source agent, with its deny-only policy

It also writes `docs/project/model-compat.md`, the per-command model table. The prose is the
OpenCode translation of `scripts/sync_opencode_plugin.py`, re-rooted: one prose pass exists and no
second harness vocabulary is forked. Sub-agent permissions are deny-only (Omnigent has no
positional allow list; see docs/standards/architecture/surface-translation.md). `--check` compares
bytes and validates the generated tree; `--write` regenerates it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync_opencode_plugin as oc  # noqa: E402

translate = oc.translate
REPO = oc.REPO
SOURCE = oc.SOURCE
TARGET = REPO / "plugins/omnigent/quenching"
MODEL_COMPAT = REPO / "docs/project/model-compat.md"
COMPAT = SOURCE / "assets/translation/omnigent-model-compat.json"
MANIFEST = oc.MANIFEST
OMNIGENT_VERSION = "0.19.1"
VERSION = (SOURCE / "VERSION").read_text(encoding="utf-8").strip()
MCP_FROM = f"git+https://github.com/holetz/quenching@{VERSION}#subdirectory=plugins/quenching"
REFERENCES_URI = "quenching://references/"
ROOT = "~/.omnigent/quenching"
CQ_WRAPPER = ('cq() { python3 "${QUENCHING_OMNIGENT_ROOT:-$HOME/.omnigent/quenching}'
              '/scripts/cq" "$@"; }')
HARNESS = "opencode"
CEL_HANDLER = "omnigent.policies.builtins.cel.cel_policy"

WRITE_HEADS = {"Write": ("sys_os_write", "Write", "write"),
               "Edit": ("sys_os_edit", "Edit", "MultiEdit", "edit"),
               "NotebookEdit": ("NotebookEdit",)}
READ_HEADS = {"Read": ("sys_os_read", "Read", "read"), "Grep": ("Grep", "grep"),
              "Glob": ("Glob", "glob")}
SHELL_TOOLS = ("sys_os_shell", "Bash", "Shell", "bash")
WEB_TOOLS = ("WebFetch", "webfetch", "WebSearch", "websearch")
SPAWN_TOOLS = ("sys_session_create", "Task", "Agent", "task")
CQ_SCOPE = re.compile(r"Bash\(cq(?: ([^:()]+))?:\*\)$")
ARG_CLASS = "[^;&|<>$`\\\\\\n]"
SEPARATOR = r"[ \t]*(?:&&|\|\||;)[ \t]*"


def reroot(text: str) -> str:
    """The OpenCode translation, re-rooted: references become MCP resources, the rest Omnigent paths."""
    text = text.replace(oc.OPENCODE_CQ_WRAPPER, CQ_WRAPPER)
    for old, new in ((oc.ROOT + "/references/", REFERENCES_URI), (oc.ROOT, ROOT),
                     ("QUENCHING_OPENCODE_ROOT", "QUENCHING_OMNIGENT_ROOT"),
                     (".opencode/", ".omnigent/"), ("OpenCode", "Omnigent")):
        text = text.replace(old, new)
    # The operator registers its sub-agents by their source name and ships their protocols in the
    # bundle, so neither the OpenCode `quenching-<agent>` name nor a payload copy of them survives.
    agents = "|".join(sorted(oc.agent_names(), key=len, reverse=True))
    text = re.sub(rf"{re.escape(ROOT)}/agents/({agents})\.md", r"agents/\1/instructions.md", text)
    return re.sub(rf"\b{re.escape(oc.AGENT_PREFIX)}({agents})(?![\w/:-])", r"\1", text)


def markdown(text: str) -> str:
    return reroot(oc.markdown(text))


def runtime_policy() -> str:
    return ("## Omnigent runtime\n\n"
            "This runs inside the `quenching` operator agent on whatever model the server's policy "
            "selects; it pins none and names no vendor CLI. The bundle carries no payload: read a "
            "reference through the `quenching` MCP server's resources (`" + REFERENCES_URI
            + "<path>`), and prefer its tools (`<pillar>_<verb>`) to a shell `cq`, which resolves "
            "only where a local install sits under `$QUENCHING_OMNIGENT_ROOT`. Delegate only to the "
            "operator's declared sub-agents. Source model tiers and effort are not switches: a "
            "declared tier or effort below is a preference to report. Token usage comes from host "
            "telemetry when it exists, otherwise it is `not measured`. A tool the permission policy "
            "denies stays denied: report it, never route around it. If delegation is unavailable, "
            "report the limitation; never replace a required independent verification with "
            "self-review.\n\n")


def tool_names(tools: str | None) -> list[str]:
    if tools is None:
        return []
    return [item.strip() for item in re.split(r",\s*(?![^()]*\))", tools) if item.strip()]


def shell_regex(verbs: list[str]) -> str:
    """Full-match regex of `cq <verbs>` segments joined by `&&`, `||` or `;`."""
    if "" in verbs:
        segment = "cq"
    else:
        segment = "cq (?:" + "|".join(re.escape(v).replace("\\ ", " ") for v in verbs) + ")"
    segment += f"(?: {ARG_CLASS}*)?"
    return f"^[ \\t]*{segment}(?:{SEPARATOR}{segment})*[ \\t]*$"


def permission_model(tools: str | None) -> dict:
    """What the source grants, what the sub-agent denies, and what no Omnigent rule expresses."""
    names = tool_names(tools)
    heads = {name.split("(", 1)[0] for name in names}
    denied: list[str] = []
    not_expressed: list[str] = []
    for table in (WRITE_HEADS, READ_HEADS):
        for head, tools_ in table.items():
            if head not in heads:
                denied += tools_
    if "WebFetch" in heads:
        not_expressed.append("WebFetch (granted; Omnigent has no tool to express it)")
    else:
        denied += WEB_TOOLS
    bare_spawn = {"Agent", "Task"} & set(names)
    if not bare_spawn:
        denied += SPAWN_TOOLS
    not_expressed += [name + " (scoped sub-agent allowlist; denied)" for name in names
                      if name.startswith("Agent(")]
    if "Skill" not in heads:
        denied.append("Skill")
    verbs: list[str] = []
    shell = "bare" if "Bash" in names else "none"
    if shell == "none":
        for name in names:
            if match := CQ_SCOPE.match(name):
                verbs.append(match.group(1) or "")
        shell = "scoped" if verbs else "denied"
        if shell == "denied":
            denied += SHELL_TOOLS
        not_expressed += [name + " (non-cq scoped Bash grant; denied)" for name in names
                          if name.startswith("Bash(") and not CQ_SCOPE.match(name)]
    return {"denied": sorted(set(denied), key=denied.index), "shell": shell, "verbs": verbs,
            "regex": shell_regex(verbs) if verbs else None, "not_expressed": not_expressed,
            "os_env": bool(heads & {"Read", "Write", "Edit", "Bash"}), "spawn": bool(bare_spawn)}


def cel_expression(model: dict) -> str:
    def names(items: list[str]) -> str:
        return "[" + ", ".join(json.dumps(item) for item in items) + "]"

    call = 'event.type == "tool_call"'
    deny = lambda why: '{"result": "DENY", "reason": ' + json.dumps(why) + "}"  # noqa: E731
    expression = "false"
    if model["denied"]:
        expression = f"{call} && event.data.name in {names(model['denied'])}"
    shell = "false"
    if model["shell"] == "scoped":
        command = "event.data.arguments.command"
        shell = (f'{call} && event.data.name in {names(list(SHELL_TOOLS))} && !("arguments" in '
                 f'event.data && "command" in event.data.arguments && type({command}) == string '
                 f'&& {command}.matches(r"{model["regex"]}"))')
    return (f"({expression}) ? {deny('Tool not granted by the quenching source.')} : "
            f"(({shell}) ? {deny('Shell call outside the granted cq verbs.')} : "
            '{"result": "ALLOW"})')


def quote(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)


def head_lines(name: str, description: str) -> list[str]:
    return ["spec_version: 1", f"name: {quote(name)}", f"description: {quote(description)}",
            "instructions: instructions.md", "executor:", "  type: omnigent", "  config:",
            f"    harness: {HARNESS}"]


def sub_agent_config(name: str, description: str, model: dict) -> str:
    lines = head_lines(name, description)
    if model["os_env"]:
        lines += ["os_env:", "  type: caller_process", "  cwd: ."]
    if model["spawn"]:
        lines.append("spawn: true")
    lines += ["guardrails:", "  policies:", "    source_tools:", "      type: function",
              "      function:", f"        path: {CEL_HANDLER}", "        arguments:",
              f"          expression: {quote(cel_expression(model))}",
              f"          reason: {quote('Denied by the quenching source tool grant.')}"]
    return "\n".join(lines) + "\n"


def operator_config(sub_agents: list[str]) -> str:
    lines = head_lines("quenching", "The quenching operator: the plugin's commands as skills, its "
                       "agents as sub-agents and the quenching MCP server.")
    lines += ["skills: none", "os_env:", "  type: caller_process", "  cwd: .", "tools:",
              "  agents: [" + ", ".join(quote(name) for name in sub_agents) + "]",
              "  quenching:", "    type: mcp", "    command: uvx",
              f"    args: [\"--from\", {quote(MCP_FROM)}, \"quenching-mcp\"]"]
    return "\n".join(lines) + "\n"


def source_text(source: Path, kind: str, fields: dict[str, str], body: str) -> str:
    origin = f"plugins/quenching/{kind}/" + source.relative_to(SOURCE / kind).as_posix()
    return (f"<!-- GENERATED FROM {origin} -->\n\n<!-- OMNIGENT RUNTIME START -->\n"
            + oc.preferences(fields) + runtime_policy() + "<!-- OMNIGENT RUNTIME END -->\n\n"
            + markdown(body))


def skill(name: str, source: Path) -> str:
    fields, body = oc.frontmatter(source.read_text(encoding="utf-8"), source)
    head = [f"name: {name}", f"description: {quote(reroot(oc.platform(fields['description'])))}"]
    if "allowed-tools" in fields:   # the audit reads this as the source grant, never a missing key
        head.append(f"allowed-tools: {quote(fields['allowed-tools'])}")
    return "---\n" + "\n".join(head) + "\n---\n\n" + source_text(source, "commands", fields, body)


def sub_agent(name: str) -> tuple[dict[str, str], dict]:
    source = SOURCE / "agents" / f"{name}.md"
    fields, body = oc.frontmatter(source.read_text(encoding="utf-8"), source)
    model = permission_model(fields.get("tools"))
    grant = fields.get("tools")
    head = f"---\ntools: {grant}\n---\n\n" if grant is not None else ""
    description = reroot(oc.platform(fields["description"]))
    return {f"agents/{name}/config.yaml": sub_agent_config(name, description, model),
            f"agents/{name}/instructions.md": head + source_text(source, "agents", fields, body)
            }, model


def skill_ids() -> list[tuple[str, Path]]:
    return [("quenching-" + "-".join(path.relative_to(SOURCE / "commands").with_suffix("").parts), path)
            for path in sorted((SOURCE / "commands").rglob("*.md"))]


def instructions(skills: list[tuple[str, Path]], agents: list[str]) -> str:
    def line(name: str, path: Path) -> str:
        fields, _ = oc.frontmatter(path.read_text(encoding="utf-8"), path)
        return f"- `{name}` — {reroot(oc.platform(fields['description']))}"

    return ("# quenching operator\n\n"
            "<!-- GENERATED FROM plugins/quenching/ by scripts/sync_omnigent_plugin.py -->\n\n"
            "You operate the quenching method for the person in this session. Each quenching command "
            "is one of your skills: when a request matches a skill's description, or the person types "
            "`/<skill>`, load that skill and follow its body. Do not paraphrase a skill from memory.\n\n"
            + runtime_policy()
            + "## Sub-agents\n\nDelegate to these, by name, where a skill says to:\n\n"
            + "\n".join(line(name, SOURCE / "agents" / f"{name}.md") for name in agents)
            + f"\n\n## Skills\n\n{len(skills)} skills, one per quenching command.\n")


def readme(commands: int, agents: int) -> str:
    return f"""# quenching for Omnigent (generated)

This Omnigent operator agent is generated from `plugins/quenching/`, the only editable source. Run
`python3 scripts/sync_omnigent_plugin.py --write` to refresh it; never edit it by hand.

One bundle, no payload: {commands} skills (`skills/`), {agents} sub-agents (`agents/`), and the
`quenching` MCP server launched by `uvx` from the tag `{VERSION}`. Built against Omnigent
`v{OMNIGENT_VERSION}` (server image `omnigent-server:v{OMNIGENT_VERSION}`). The bundle pins no model:
the server's policy chooses it. `skills: none` binds the Claude SDK harness only: under OpenCode the
`skill` tool still lists the host skills in `~/.claude/skills/` and `~/.agents/skills/` (only
`~/.config/opencode/skills/` is hidden), so a host that serves this agent must not carry quenching
skills in those two directories.

## Install

Register this directory as an agent on the Omnigent server, or run it locally:

```bash
omnigent run --agent plugins/omnigent/quenching -p "/quenching-specs-status"
```

Do not install the OpenCode distribution on the same machine: it carries the same commands.

## Permissions

The operator runs with the session's tools. Each sub-agent carries one deny-only policy derived from
its source `tools:`; see `docs/standards/architecture/surface-translation.md`. The model table is
`docs/project/model-compat.md`.
"""


def compat() -> dict:
    return json.loads(COMPAT.read_text(encoding="utf-8"))


def costs(data: dict) -> dict:
    total = data["cases_total"]
    per_case = {m: round(c / total, 4) for m, c in data["agent_cost_usd_total"].items()}
    return {"per_case": per_case, "suite_cases": 3,
            "per_suite": {m: round(c * 3, 4) for m, c in per_case.items()},
            "ceiling_left": data["ceiling_left_usd"]}


def compat_doc(ids: list[str], data: dict) -> str:
    models = data["models"]
    figure = costs(data)
    stamp = re.search(r"\d{4}-\d{2}-\d{2}", data["source"])
    lines = ["---", "type: project", "title: Model compatibility",
             "description: The per-command model table of the Omnigent operator agent; only the "
             "cells a spike measured are filled",
             "resource: plugins/quenching/assets/translation/omnigent-model-compat.json",
             "tags:", "  - reference", "  - omnigent", "  - models",
             f"timestamp: {stamp.group(0) if stamp else '1970-01-01'}", "audience: both",
             "authority: current",
             "source: generated by scripts/sync_omnigent_plugin.py from "
             "plugins/quenching/assets/translation/omnigent-model-compat.json", "---", "",
             "# Model compatibility (generated)", "",
             "Cells are filled only where spike H1 measured them. H1 ran "
             f"{data['harness']}, so a cell is evidence about the model on "
             "that harness and not about Omnigent. Every other cell reads `unmeasured`.", "",
             f"Source: {data['source']}. Grader: {data['grader']}.", "",
             "Cell form: `approved/cases, assertion pass rate`.", "",
             "| Command | " + " | ".join(models) + " |", "| --- | " + " | ".join("---" for _ in models) + " |"]
    for ident in ids:
        row = []
        for model in models:
            cell = data["cells"].get(ident, {}).get(model)
            row.append(f"{cell['approved']}/{cell['cases']}, {cell['pass_rate']}%" if cell else "unmeasured")
        lines.append(f"| `{ident}` | " + " | ".join(row) + " |")
    lines += ["", "## Filling the rest (human step)", "",
              f"Agent cost per case in H1 (total over {data['cases_total']} cases, US$): "
              + ", ".join(f"{m} {c:.4f}" for m, c in figure["per_case"].items()) + ".",
              f"One suite holds {figure['suite_cases']} cases, so re-measuring one suite on one model costs "
              "about " + ", ".join(f"{m} US$ {c:.4f}" for m, c in figure["per_suite"].items()) + ".",
              f"The ceiling left is about US$ {figure['ceiling_left']:.2f}; grader cost is not included "
              "(the grader is the Flash 1017 default of `scripts/run_evals.py`).", "",
              "```bash", "python3 scripts/run_evals.py --harness omnigent --model <model> --suite <suite>",
              "```", ""]
    return "\n".join(lines)


def generated_tree() -> dict[str, bytes]:
    out: dict[str, str] = {}
    skills = skill_ids()
    for name, path in skills:
        out[f"skills/{name}/SKILL.md"] = skill(name, path)
    agents = oc.agent_names()
    for name in agents:
        files, _ = sub_agent(name)
        out.update(files)
    out["config.yaml"] = operator_config(agents)
    out["instructions.md"] = instructions(skills, agents)
    out["README.md"] = readme(len(skills), len(agents))
    out[".generated-from.json"] = json.dumps({"source": "plugins/quenching",
        "generator": "scripts/sync_omnigent_plugin.py", "omnigent": OMNIGENT_VERSION,
        "version": VERSION, "skill_count": len(skills), "agent_count": len(agents)}, indent=2) + "\n"
    return {rel: value.encode("utf-8") for rel, value in sorted(out.items())}


def model_compat() -> bytes:
    return compat_doc([name for name, _ in skill_ids()], compat()).encode("utf-8")


def validate(tree: dict[str, bytes]) -> list[str]:
    """Structural findings over the generated tree; empty means it is loadable on Omnigent."""
    problems = []
    skills = [rel for rel in tree if rel.startswith("skills/") and rel.endswith("/SKILL.md")]
    if len(skills) != len(list((SOURCE / "commands").rglob("*.md"))):
        problems.append("skill count differs from the source commands")
    configs = [rel for rel in tree if rel.startswith("agents/") and rel.endswith("/config.yaml")]
    if len(configs) != len(oc.agent_names()):
        problems.append("sub-agent count differs from the source agents")
    operator = tree.get("config.yaml", b"").decode("utf-8")
    for needle in ("spec_version: 1", f"harness: {HARNESS}", "skills: none", "type: mcp",
                   quote(MCP_FROM)):
        if needle not in operator:
            problems.append(f"config.yaml: no {needle}")
    for rel in configs + ["config.yaml"]:
        text = tree[rel].decode("utf-8")
        if f"harness: {HARNESS}" not in text or "spec_version: 1" not in text:
            problems.append(f"{rel}: no harness or spec_version")
        if re.search(r"(?m)^\s*model:", text):
            problems.append(f"{rel}: pins a model")
        folder = rel.rsplit("/", 1)[0] + "/" if "/" in rel else ""
        if f"{folder}instructions.md" not in tree:
            problems.append(f"{rel}: no instructions.md")
    for rel in skills:
        name = rel.split("/")[1]
        if not tree[rel].decode("utf-8").startswith(f"---\nname: {name}\ndescription: "):
            problems.append(f"{rel}: frontmatter does not open with its name and description")
    for rel, content in tree.items():
        if not rel.endswith(".md"):
            continue
        text = content.decode("utf-8")
        if rel.endswith(("instructions.md", "SKILL.md")) and re.search(
                r"opencode|claude_plugin_root", text, re.IGNORECASE):
            problems.append(f"{rel}: carries a foreign harness marker")
        for marker in oc.FORBIDDEN:
            if marker in text:
                problems.append(f"{rel}: carries {marker}")
        for block in re.findall(r"^\s*```bash\n([\s\S]*?)^\s*```", text, re.MULTILINE):
            if translate.has_cq_invocation(block) and CQ_WRAPPER not in block:
                problems.append(f"{rel}: a bash block invokes cq without the wrapper")
        if re.search(re.escape(ROOT) + r"/agents/", text):
            problems.append(f"{rel}: cites a sub-agent protocol under {ROOT}/agents/, which the bundle does not carry")
        for path in sorted(set(re.findall(re.escape(REFERENCES_URI) + r"([A-Za-z0-9_./-]*[A-Za-z0-9_])", text))):
            if not (SOURCE / "assets/references" / path).exists():
                problems.append(f"{rel}: cites {REFERENCES_URI}{path}, which the source does not carry")
    return problems


def manifest_document(tree: dict[str, bytes]) -> bytes:
    return (json.dumps({"files": sorted(tree), "sha256": {rel: hashlib.sha256(content).hexdigest()
                        for rel, content in sorted(tree.items())}}, indent=2) + "\n").encode()


def on_disk(target: Path) -> set[str]:
    if not target.is_dir():
        return set()
    return {path.relative_to(target).as_posix() for path in target.rglob("*")
            if path.is_file() and path.name != MANIFEST and not translate._is_build_artefact(path)}


def differences(tree: dict[str, bytes], target: Path) -> list[str]:
    changed = [rel for rel in sorted(set(tree) | on_disk(target))
               if rel not in tree or not (target / rel).is_file() or (target / rel).read_bytes() != tree[rel]]
    manifest = target / MANIFEST
    if not manifest.is_file() or manifest.read_bytes() != manifest_document(tree):
        changed.append(MANIFEST)
    return changed


def write(tree: dict[str, bytes], target: Path) -> None:
    previous = translate.previous_files(target / MANIFEST, target)
    previous = on_disk(target) if previous is None else previous
    translate.contain(previous | set(tree), target, "the destination")
    for rel in sorted(previous - set(tree)):
        if (target / rel).is_file():
            (target / rel).unlink()
    for rel, content in tree.items():
        (target / rel).parent.mkdir(parents=True, exist_ok=True)
        (target / rel).write_bytes(content)
    (target / MANIFEST).write_bytes(manifest_document(tree))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sync_omnigent_plugin.py", description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    parser.add_argument("--target", default=str(TARGET))
    parser.add_argument("--model-compat", default=str(MODEL_COMPAT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    target = Path(args.target).resolve()
    compat_path = Path(args.model_compat).resolve()
    try:
        tree, table = generated_tree(), model_compat()
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}) if args.json else f"refused: {exc}", file=sys.stderr)
        return 2
    problems = validate(tree)
    if args.write and not problems:
        write(tree, target)
        compat_path.parent.mkdir(parents=True, exist_ok=True)
        compat_path.write_bytes(table)
    changed = [] if args.write and not problems else differences(tree, target)
    if not (args.write and not problems) and (not compat_path.is_file() or compat_path.read_bytes() != table):
        changed.append(compat_path.name)
    payload = {"ok": not problems and not changed,
               "skills": sum(r.startswith("skills/") for r in tree),
               "sub_agents": sum(r.startswith("agents/") and r.endswith("/config.yaml") for r in tree),
               "changed": changed, "count": len(changed), "findings": problems}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"omnigent operator agent — {payload['skills']} skills, {payload['sub_agents']} sub-agents, "
              f"{len(changed)} changed file(s), {len(problems)} finding(s)")
        for line in problems + [f"drift: {rel}" for rel in changed]:
            print("  " + line)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
