#!/usr/bin/env python3
"""Portable hook (PostToolUse, matcher Write|Edit) — guard of the ``.claude/`` config surface.

Payload of the ``quenching-management`` method. Generic and self-contained.
Materializes the **``.claude/`` slice of trigger (1) "by event" of Step 8**
(recurring maintenance loop): when the agent writes or edits the **harness
itself** — a skill, a sub-agent, a hook script, ``settings.json`` — this hook
re-applies the **cheap scoped checks of dims 6/7/8** to the touched artifact
and **PROPOSES** (never blocks) the fix **while the edit is fresh**. It is the
continuous audit applied to the config surface at runtime: the harness that
guards the knowledge base must not itself rot silently between audits.

Distinct from the sibling payloads:

- ``propose-docs-home.py`` (PostToolUse) proposes about **``docs/``**; this one
  proposes about **``.claude/``** — together they close trigger (1) of Step 8.
- ``audit-config-change.py`` (ConfigChange) **records** metadata of a config
  change (who/when/what, append-only); this one **evaluates** the touched
  artifact against the method's criteria and proposes fixes.
- ``protect-generated.py`` (PreToolUse) **blocks** before the edit; this one
  runs after and never blocks.

Checks (deliberately cheap — one file head + one settings parse; the SAME
criteria the method measures in dims 6/7/8, no new smells invented):

- **skill touched** (``.claude/skills/<name>/SKILL.md``): frontmatter present
  with ``name:`` + ``description:``; ``name`` == folder name; description long
  enough to be a routing trigger (sub-trigger smell, dim 6).
- **sub-agent touched** (``.claude/agents/<name>.md``): frontmatter present
  with ``name:`` + ``description:`` (return contract/doctrine stays in the
  audit — here only the discoverability minimum, dim 7).
- **hook script touched** (``.claude/hooks/*.py``): the script is **wired** in
  ``settings.json`` (orphan check, block 8b — a hook only runs if wired).
- **settings touched** (``.claude/settings*.json``): 1:1 wiring — every
  ``command`` entry points to an existing script (**dangling**), every script
  in ``.claude/hooks/`` has an entry (**orphan**).

Official contract (PostToolUse — code.claude.com/docs/en/hooks#posttooluse):
fires AFTER the tool succeeds; cannot undo/block ("Can block? No"), so the
proposal goes via ``hookSpecificOutput.additionalContext`` with **exit 0
always**; stdout does not become context in this event. Actionable error
(dim 14): each proposal names the exact artifact and the exact fix. Latency
ceiling on the critical path (``deadlineMs`` guard) — it runs on every
Write/Edit, so everything outside ``.claude/`` returns immediately.

Pre-trust vector: hook config is executable code with shell privileges. This
script is **read-only** (reads the touched file head + settings.json; writes
nothing) — version and review it like infra. Register the ``command`` in
``settings.json`` under ``PostToolUse`` with ``matcher: "Write|Edit"`` (use
``settings.snippet.json``). Honors ``hooks-config.json``/
``hooks-config.local.json`` (block ``guardConfigSurface``): ``enabled: false``
exits silently.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TAG = "knowledge-management"

DEFAULTS = {
    "enabled": True,
    "claudeDir": ".claude",      # harness root in the target (derivable)
    "maxHeadBytes": 2000,        # only the file head for frontmatter checks
    "minDescriptionChars": 60,   # below this, description is a sub-trigger smell (dim 6)
    "deadlineMs": 200,           # ceiling on the critical path
    "maxFindings": 3,            # do not flood the context
}

FRONT_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def _load_config() -> dict:
    cfg = dict(DEFAULTS)
    for name in ("hooks-config.json", "hooks-config.local.json"):
        path = os.path.join(HERE, name)
        if not pathlib.Path(path).exists():
            continue
        try:
            with pathlib.Path(path).open(encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        cfg.update(data.get("guardConfigSurface") or {})
    return cfg


def _read_input() -> dict:
    try:
        return json.loads(sys.stdin.read() or "{}")
    except (OSError, json.JSONDecodeError):
        return {}


def _project_dir(data: dict) -> str:
    return os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()


def _rel_under(file_path: str, root: str, subdir: str) -> str | None:
    """Path of the touched file relative to <root>/<subdir> (None if outside)."""
    if not file_path:
        return None
    abspath = file_path if os.path.isabs(file_path) else os.path.join(root, file_path)
    base = os.path.normpath(os.path.join(root, subdir))
    norm = os.path.normpath(abspath)
    if not norm.startswith(base + os.sep):
        return None
    return os.path.relpath(norm, base).replace(os.sep, "/")


def _frontmatter(abspath: str, max_head: int) -> dict[str, str] | None:
    """Naive key: value map of the frontmatter head (None = no frontmatter)."""
    try:
        with pathlib.Path(abspath).open("rb") as fh:
            head = fh.read(max_head).decode("utf-8", errors="ignore")
    except OSError:
        return {}  # could not read ⇒ do not flag (avoid false positive)
    match = FRONT_RE.match(head)
    if not match:
        return None
    out: dict[str, str] = {}
    key = None
    for line in match.group(1).splitlines():
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if m:
            key = m.group(1)
            out[key] = m.group(2).strip().strip("'\"")
        elif key and line.startswith((" ", "\t")):
            out[key] += " " + line.strip()  # folded >-/multi-line values
    return out


def _wired_commands(root: str, claude_dir: str) -> tuple[list[str], bool]:
    """All hook command strings wired in settings*.json (and whether any settings parsed)."""
    commands: list[str] = []
    parsed_any = False
    for name in ("settings.json", "settings.local.json"):
        path = os.path.join(root, claude_dir, name)
        try:
            with pathlib.Path(path).open(encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        parsed_any = True
        for groups in (data.get("hooks") or {}).values():
            for group in groups or []:
                for hook in group.get("hooks") or []:
                    if hook.get("type") == "command" and hook.get("command"):
                        commands.append(str(hook["command"]))
    return commands, parsed_any


def _findings_skill(rel: str, abspath: str, cfg: dict) -> list[str]:
    parts = rel.split("/")  # skills/<folder>/SKILL.md
    folder = parts[1] if len(parts) >= 3 else ""
    front = _frontmatter(abspath, int(cfg["maxHeadBytes"]))
    if front is None:
        return [
            f"NO-FRONTMATTER: '{rel}' has no frontmatter — a skill without "
            "'name:'/'description:' is not routable; stamp templates/claude/skill.md."
        ]
    out: list[str] = []
    if not front.get("name") or not front.get("description"):
        out.append(
            f"MISSING-KEY: '{rel}' frontmatter lacks "
            f"{'name' if not front.get('name') else 'description'}: — the description "
            "is the routing code (dim 6); without it the skill never triggers."
        )
    if folder and front.get("name") and front["name"] != folder:
        out.append(
            f"NAME-MISMATCH: frontmatter name '{front['name']}' ≠ folder '{folder}' — "
            "align them (the folder is the invocation fallback; divergence breaks routing)."
        )
    desc = front.get("description") or ""
    if desc and len(desc) < int(cfg["minDescriptionChars"]):
        out.append(
            f"SUB-TRIGGER: '{rel}' description has {len(desc)} chars — too thin to route "
            "(dim 6): state WHEN to use it, with the literal user phrasings that should trigger it."
        )
    return out


def _findings_agent(rel: str, abspath: str, cfg: dict) -> list[str]:
    front = _frontmatter(abspath, int(cfg["maxHeadBytes"]))
    if front is None:
        return [
            f"NO-FRONTMATTER: '{rel}' has no frontmatter — a sub-agent without "
            "'name:'/'description:' is not discoverable; stamp templates/claude/agent.md."
        ]
    if not front.get("name") or not front.get("description"):
        return [
            f"MISSING-KEY: '{rel}' frontmatter lacks "
            f"{'name' if not front.get('name') else 'description'}: — minimum for the "
            "sub-agent to be delegable (dim 7)."
        ]
    return []


def _findings_hook_script(rel: str, root: str, claude_dir: str) -> list[str]:
    script = os.path.basename(rel)
    commands, parsed = _wired_commands(root, claude_dir)
    if not parsed:
        return []  # no settings to check against ⇒ stay silent (avoid false positive)
    if any(script in cmd for cmd in commands):
        return []
    return [
        f"ORPHAN-HOOK: '{claude_dir}/hooks/{script}' has no entry in "
        f"'{claude_dir}/settings.json' — a hook only runs if WIRED (block 8b); merge the "
        "matching block from settings.snippet.json (never overwrite existing groups)."
    ]


def _findings_settings(root: str, claude_dir: str) -> list[str]:
    out: list[str] = []
    commands, parsed = _wired_commands(root, claude_dir)
    if not parsed:
        return []
    hooks_dir = os.path.join(root, claude_dir, "hooks")
    # dangling: wired command points to a script that does not exist
    for cmd in commands:
        for token in cmd.split():
            expanded = token.replace("${CLAUDE_PROJECT_DIR}", root)
            if expanded.endswith(".py") and not pathlib.Path(expanded).exists():
                out.append(
                    f"DANGLING-HOOK: settings wire '{token}' but the script does not "
                    "exist — restore the script or remove the entry (block 8b)."
                )
    # orphan: script on disk with no wired entry
    try:
        for entry in os.listdir(hooks_dir):
            if entry.endswith(".py") and not any(entry in cmd for cmd in commands):
                out.append(
                    f"ORPHAN-HOOK: '{claude_dir}/hooks/{entry}' is not wired in settings — "
                    "inert script; wire it (settings.snippet.json) or remove it (block 8b)."
                )
    except OSError:
        pass
    return out


def _emit(rel: str, claude_dir: str, findings: list[str], cap: int) -> None:
    """Returns the PROPOSAL via additionalContext (does not block; exit 0)."""
    lines = [
        f"[{TAG}] config-surface guard: the recently-touched '{claude_dir}/{rel}' may "
        "leave the harness inconsistent. PROPOSAL (not mandatory) — adjust while it is fresh:",
    ]
    for item in findings[:cap]:
        lines.append(f"  - {item}")
    lines.append(
        "If confirmed, fix with confirmation (never delete/rewire without OK). "
        "Ignore if it is noise."
    )
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": "\n".join(lines),
        }
    }
    print(json.dumps(payload))


def main() -> int:
    cfg = _load_config()
    if cfg.get("enabled") is False:
        return 0

    data = _read_input()
    started = time.monotonic()
    deadline = float(cfg.get("deadlineMs", DEFAULTS["deadlineMs"])) / 1000.0

    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path") or ""
    if not file_path:
        return 0

    root = _project_dir(data)
    claude_dir = cfg.get("claudeDir") or DEFAULTS["claudeDir"]
    rel = _rel_under(file_path, root, claude_dir)
    if rel is None:  # file outside .claude/ → silence (the common, fast path)
        return 0
    if time.monotonic() - started > deadline:
        return 0

    abspath = file_path if os.path.isabs(file_path) else os.path.join(root, file_path)
    findings: list[str] = []
    if rel.startswith("skills/") and rel.endswith("SKILL.md"):
        findings = _findings_skill(rel, abspath, cfg)
    elif rel.startswith("agents/") and rel.endswith(".md"):
        findings = _findings_agent(rel, abspath, cfg)
    elif rel.startswith("hooks/") and rel.endswith(".py"):
        findings = _findings_hook_script(rel, root, claude_dir)
    elif os.path.basename(rel) in ("settings.json", "settings.local.json"):
        findings = _findings_settings(root, claude_dir)

    if findings:
        _emit(rel, claude_dir, findings, int(cfg.get("maxFindings", DEFAULTS["maxFindings"])))
    return 0  # ALWAYS exit 0 — PROPOSES, never blocks (PostToolUse cannot undo the edit)


if __name__ == "__main__":
    sys.exit(main())
