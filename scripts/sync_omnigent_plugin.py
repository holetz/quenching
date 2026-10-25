#!/usr/bin/env python3
"""Generate and validate the Omnigent distribution of the quenching plugin.

`plugins/quenching/` is the only editable source. This generator lays the command surface out as
Omnigent agent bundles, `plugins/quenching-omnigent/`:

  agents/<id>/config.yaml        one Omnigent agent spec per source command and per source agent
  agents/<id>/instructions.md    its instructions (the OpenCode translation, re-rooted)
  quenching/                     the payload: references, templates, specs, knowledge, design,
                                 portal, agent protocols and the bundled `cq`
  PERMISSIONS.md                 per bundle: what is denied and what the policy cannot express
  MODEL-COMPAT.md                per-command model table; only measured cells are filled

The prose is the OpenCode translation of `scripts/sync_opencode_plugin.py`, re-rooted: one prose pass
exists and no second harness vocabulary is forked. Permissions are deny-only (Omnigent has no
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
TARGET = REPO / "plugins/quenching-omnigent"
COMPAT = SOURCE / "assets/translation/omnigent-model-compat.json"
MANIFEST = oc.MANIFEST
AGENT_PREFIX = oc.AGENT_PREFIX
OMNIGENT_VERSION = "0.19.1"
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
UNSAFE = "; & | < > $ ` \\ and newline"
ARG_CLASS = "[^;&|<>$`\\\\\\n]"
SEPARATOR = r"[ \t]*(?:&&|\|\||;)[ \t]*"


def reroot(text: str) -> str:
    """The OpenCode translation, re-rooted to the Omnigent install path and vocabulary."""
    text = text.replace(oc.OPENCODE_CQ_WRAPPER, CQ_WRAPPER)
    for old, new in ((oc.ROOT, ROOT), ("QUENCHING_OPENCODE_ROOT", "QUENCHING_OMNIGENT_ROOT"),
                     (".opencode/", ".omnigent/"), ("OpenCode", "Omnigent")):
        text = text.replace(old, new)
    return text


def markdown(text: str) -> str:
    return reroot(oc.markdown(text))


def runtime_policy() -> str:
    return ("## Omnigent runtime\n\n"
            "This bundle runs on whatever harness and model the caller passes "
            "(`omnigent run --harness X --model Y`); it pins neither and names no vendor CLI. "
            "Delegate only through Omnigent's own session tools, and only when this bundle's "
            "`config.yaml` sets `spawn: true`; protocol copies of the subagents live under `"
            + ROOT + "/agents/`. Source model tiers and effort are not switches: a declared tier "
            "or effort below is a preference to report. Token usage comes from host telemetry when "
            "it exists, otherwise it is `not measured`; `cq components session cost` and `context` "
            "read no Omnigent log and refuse (exit 2, unmeasured). A tool the permission policy "
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
    """What the source grants, what the bundle denies, and what no Omnigent rule expresses."""
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
    elif any(name.startswith("Bash(") and not CQ_SCOPE.match(name) for name in names):
        pass  # a bare Bash already covers every scoped grant
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


def config_yaml(name: str, description: str, model: dict) -> str:
    lines = ["spec_version: 1", f"name: {quote(name)}", f"description: {quote(description)}",
             "instructions: instructions.md", "executor:", "  type: omnigent", "  config:",
             f"    harness: {HARNESS}"]
    if model["os_env"]:
        lines += ["os_env:", "  type: caller_process", "  cwd: ."]
    if model["spawn"]:
        lines.append("spawn: true")
    lines += ["guardrails:", "  policies:", "    source_tools:", "      type: function",
              "      function:", f"        path: {CEL_HANDLER}", "        arguments:",
              f"          expression: {quote(cel_expression(model))}",
              f"          reason: {quote('Denied by the quenching source tool grant.')}"]
    return "\n".join(lines) + "\n"


def dropped(fields: dict[str, str]) -> list[str]:
    return [key for key in ("hooks", "model") if key in fields]


def bundle(name: str, source: Path, kind: str) -> tuple[dict[str, str], dict]:
    fields, body = oc.frontmatter(source.read_text(encoding="utf-8"), source)
    model = permission_model(fields.get("tools") if kind == "agent" else fields.get("allowed-tools"))
    model["dropped"] = dropped(fields)
    description = reroot(oc.platform(fields["description"]))
    origin = f"plugins/quenching/{'agents' if kind == 'agent' else 'commands'}/" + (
        source.name if kind == "agent" else source.relative_to(SOURCE / "commands").as_posix())
    instructions = (f"<!-- GENERATED FROM {origin} -->\n\n<!-- OMNIGENT RUNTIME START -->\n"
                    + oc.preferences(fields) + runtime_policy() + "<!-- OMNIGENT RUNTIME END -->\n\n"
                    + markdown(body))
    return {f"agents/{name}/config.yaml": config_yaml(name, description, model),
            f"agents/{name}/instructions.md": instructions}, model


def permissions_doc(models: dict[str, dict]) -> str:
    lines = ["# Permissions (generated)", "",
             f"Every bundle carries one deny-only CEL policy (`{CEL_HANDLER}`) derived from the source "
             "`allowed-tools:` (commands) or `tools:` (agents). What the source does not grant is denied; "
             "Omnigent has no positional allow list and a DENY outranks every ALLOW, so no rule is an "
             "allow. A scoped `Bash(cq <verbs>:*)` is the exception inside the one shell denial: a call "
             f"passes only when it matches, in full, `cq <verbs>` segments joined by `&&`, `||` or `;` "
             f"with arguments free of {UNSAFE}. Grants Omnigent cannot express are denied and listed "
             "below as not expressed.", "",
             "| Bundle | Shell | Spawn | Denied tool names | Not expressed | Dropped |",
             "| --- | --- | --- | --- | --- | --- |"]
    for name, model in sorted(models.items()):
        shell = {"bare": "bare (no rule)", "none": "denied", "denied": "denied",
                 "scoped": "cq " + " / ".join(v or "*" for v in model["verbs"])}[model["shell"]]
        lines.append(f"| `{name}` | {shell} | {'yes' if model['spawn'] else 'no'} | "
                     f"{len(model['denied'])} | {'; '.join(model['not_expressed']) or '-'} | "
                     f"{', '.join(model['dropped']) or '-'} |")
    lines += ["", "`hooks:` and `model:` frontmatter, scoped `Agent(...)` allowlists and non-`cq` scoped "
              "`Bash` grants are never generated or approximated.", ""]
    return "\n".join(lines)


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
    lines = ["# Model compatibility (generated)", "",
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


def readme(commands: int, agents: int) -> str:
    return f"""# quenching-omnigent (generated)

This Omnigent distribution is generated from `plugins/quenching/`, the only editable source. Run
`python3 scripts/sync_omnigent_plugin.py --write` to refresh it; never edit it by hand.

It carries {commands} command bundles and {agents} agent bundles (`agents/<id>/config.yaml` plus
`instructions.md`) and the payload they cite (`quenching/`, including the bundled `cq`). Pinned
Omnigent version: `v{OMNIGENT_VERSION}` (server image `omnigent-server:v{OMNIGENT_VERSION}`).

## Install

```bash
mkdir -p ~/.omnigent/quenching
cp -R quenching/. ~/.omnigent/quenching/
omnigent run --agent agents/quenching-git-commit --harness <harness> --model <model> -p "<prompt>"
```

Prose paths assume `{ROOT}`; `cq` honours `QUENCHING_OMNIGENT_ROOT` for another root. Bundles pin
no model: `--harness` and `--model` choose the runtime.

## Permissions

Each bundle carries one deny-only policy; see `PERMISSIONS.md` for what each denies and what Omnigent
cannot express. See `MODEL-COMPAT.md` for the models measured on the quenching commands.
"""


def plugin_manifest() -> str:
    return oc.plugin_manifest().replace("OpenCode", "Omnigent")


def generated_tree() -> dict[str, bytes]:
    out: dict[str, str | bytes] = {}
    models: dict[str, dict] = {}
    command_ids = []
    commands = sorted((SOURCE / "commands").rglob("*.md"))
    for command in commands:
        name = "quenching-" + "-".join(command.relative_to(SOURCE / "commands").with_suffix("").parts)
        files, models[name] = bundle(name, command, "command")
        out.update(files)
        command_ids.append(name)
    for agent in oc.agent_names():
        files, models[AGENT_PREFIX + agent] = bundle(AGENT_PREFIX + agent, SOURCE / "agents" / f"{agent}.md", "agent")
        out.update(files)
        fields, body = oc.frontmatter((SOURCE / "agents" / f"{agent}.md").read_text(encoding="utf-8"),
                                      SOURCE / "agents" / f"{agent}.md")
        out[f"quenching/agents/{agent}.md"] = markdown(body) + "\n" + runtime_policy()
    for rel, content in oc.generated_tree().items():
        if not rel.startswith("quenching/") or rel.startswith("quenching/agents/"):
            continue
        if rel.startswith("quenching/scripts/"):
            out[rel] = content
            continue
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            out[rel] = content
            continue
        out[rel] = reroot(text)
    out["quenching/.claude-plugin/plugin.json"] = plugin_manifest()
    out["PERMISSIONS.md"] = permissions_doc(models)
    out["MODEL-COMPAT.md"] = compat_doc(command_ids, compat())
    out["README.md"] = readme(len(commands), len(oc.agent_names()))
    out[".generated-from.json"] = json.dumps({"source": "plugins/quenching",
        "generator": "scripts/sync_omnigent_plugin.py", "omnigent": OMNIGENT_VERSION,
        "command_count": len(commands), "agent_count": len(oc.agent_names())}, indent=2) + "\n"
    return {rel: value if isinstance(value, bytes) else value.encode("utf-8")
            for rel, value in sorted(out.items())}


def validate(tree: dict[str, bytes]) -> list[str]:
    """Structural findings over the generated tree; empty means it is loadable on Omnigent."""
    problems = []
    configs = [rel for rel in tree if rel.endswith("/config.yaml")]
    expected = len(list((SOURCE / "commands").rglob("*.md"))) + len(oc.agent_names())
    if len(configs) != expected:
        problems.append("bundle count differs from the source")
    for rel in configs:
        bundle_dir = rel.rsplit("/", 1)[0]
        if f"{bundle_dir}/instructions.md" not in tree:
            problems.append(f"{rel}: no instructions.md")
        text = tree[rel].decode("utf-8")
        if f"harness: {HARNESS}" not in text or "spec_version: 1" not in text:
            problems.append(f"{rel}: no harness or spec_version")
        if "model:" in text.replace("os_env", ""):
            problems.append(f"{rel}: pins a model")
        instructions = tree.get(f"{bundle_dir}/instructions.md", b"").decode("utf-8")
        if re.search(r"opencode|claude_plugin_root", instructions, re.IGNORECASE):
            problems.append(f"{bundle_dir}/instructions.md: carries a foreign harness marker")
        for block in re.findall(r"^\s*```bash\n([\s\S]*?)^\s*```", instructions, re.MULTILINE):
            if translate.has_cq_invocation(block) and CQ_WRAPPER not in block:
                problems.append(f"{bundle_dir}/instructions.md: a bash block invokes cq without the wrapper")
    for rel, content in tree.items():
        if not rel.endswith(".md") or rel.startswith("quenching/scripts/"):
            continue
        text = content.decode("utf-8")
        for marker in oc.FORBIDDEN:
            if marker in text:
                problems.append(f"{rel}: carries {marker}")
    cited = re.compile(re.escape(ROOT) + r"/((?:" + "|".join(oc.PAYLOAD_DIRS) + r")/[A-Za-z0-9_./-]*[A-Za-z0-9_])")
    for rel, content in tree.items():
        if not rel.endswith(".md"):
            continue
        for path in sorted(set(cited.findall(content.decode("utf-8")))):
            target = f"quenching/{path}"
            if target not in tree and not any(key.startswith(target + "/") for key in tree):
                problems.append(f"{rel}: cites {ROOT}/{path}, which the tree does not carry")
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
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    target = Path(args.target).resolve()
    try:
        tree = generated_tree()
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}) if args.json else f"refused: {exc}", file=sys.stderr)
        return 2
    problems = validate(tree)
    if args.write and not problems:
        write(tree, target)
    changed = [] if args.write and not problems else differences(tree, target)
    payload = {"ok": not problems and not changed, "bundles": sum(r.endswith("/config.yaml") for r in tree),
               "changed": changed, "count": len(changed), "findings": problems}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"omnigent distribution — {payload['bundles']} bundles, "
              f"{len(changed)} changed file(s), {len(problems)} finding(s)")
        for line in problems + [f"drift: {rel}" for rel in changed]:
            print("  " + line)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
