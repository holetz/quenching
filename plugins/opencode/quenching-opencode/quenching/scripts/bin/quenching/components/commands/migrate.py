"""`cq components migrate` — move a target repository onto the generic `.agents/` layer.

The plan turns the legacy layout, where `.agents/` was the source and `.agents/` a Codex
translation of it, into the generic one: skills in `.agents/skills/<name>/SKILL.md`, references
in `.agents/references/**`, instructions in `AGENTS.md`, configuration in `.agents/quenching.json`,
and `AGENTS.md` reduced to `@AGENTS.md`. A nested `.agents/skills/<a>/<b>.md` becomes the flat
skill `<a>-<b>`. The old translation's generated files are removed, never merged.

Without `--write` it only plans: exit 0 with `conformant: true` when there is nothing to do, exit
1 with the operations otherwise. Two editable copies that disagree are a conflict: reported, and
nothing is written. `--write` applies the plan with `git mv` and `git rm`, so history follows the
moved files, then rewrites the citations inside them.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

from quenching.common.output import FINDINGS, OK, emit, refuse
from quenching.components.commands.bridge import MANIFEST as BRIDGE_MANIFEST

CLAUDE = Path(".claude")
AGENTS = Path(".agents")
SKILLS = AGENTS / "skills"
POINTER = "@AGENTS.md\n"
TRANSLATION_MANIFESTS = (AGENTS / ".generated-from.json", AGENTS / ".generated-files.json")


def _tracked(repo: Path, *paths: Path) -> list[str]:
    """Repo-relative tracked files under `paths`: only what git holds can move with history."""
    done = subprocess.run(["git", "-C", str(repo), "ls-files", "-z", "--",
                           *(p.as_posix() for p in paths)],
                          check=True, capture_output=True, text=True)
    return sorted(name for name in done.stdout.split("\0") if name)


def _bridged(repo: Path) -> set[str]:
    path = repo / BRIDGE_MANIFEST
    if not path.is_file():
        return set()
    try:
        files = json.loads(path.read_text(encoding="utf-8")).get("files", {})
    except (ValueError, AttributeError):
        return set()
    return {rel.split("/", 1)[0] for rel in files}


def skill_name(command_relpath: str) -> str:
    """`a/b.md` -> `a-b`: Codex discovers only flat skill folders."""
    return command_relpath[:-3].replace("/", "-")


class Plan:
    def __init__(self, repo: Path, tracked: set[str]):
        self.repo = repo
        self.tracked = tracked
        self.ops: list[dict] = []
        self.conflicts: list[dict] = []
        self.renames: dict[str, str] = {}
        self.removed: set[str] = set()
        self.claimed: set[str] = set()

    def remove(self, rel: str, why: str) -> None:
        if rel in self.tracked and rel not in self.removed:
            self.removed.add(rel)
            self.ops.append({"op": "remove", "path": rel, "why": why})

    def move(self, src: str, dst: str) -> None:
        if dst in self.claimed or (dst in self.tracked and dst not in self.removed):
            self.conflicts.append({"path": dst, "with": src, "why": "two editable copies"})
            return
        self.claimed.add(dst)
        self.ops.append({"op": "move", "from": src, "to": dst})


def build_plan(repo: Path) -> Plan:
    """The legacy layout's `.agents/skills/<path>/` and `.agents/references/**` are the
    translation of `.agents/`: they are removed and the `.agents/` source moves into place."""
    tracked = _tracked(repo, CLAUDE, AGENTS, Path("AGENTS.md"), Path("AGENTS.md"))
    plan = Plan(repo, set(tracked))
    commands = (CLAUDE / "commands").as_posix() + "/"
    for rel in tracked:
        if rel.startswith(commands) and rel.endswith(".md"):
            relpath = rel[len(commands):]
            plan.remove((SKILLS / relpath[:-3] / "SKILL.md").as_posix(),
                        f"translation of {rel}")
    references = (CLAUDE / "references").as_posix() + "/"
    for rel in tracked:
        if rel.startswith(references):
            plan.remove((AGENTS / "references" / rel[len(references):]).as_posix(),
                        f"translation of {rel}")
    for manifest in TRANSLATION_MANIFESTS:
        plan.remove(manifest.as_posix(), "manifest of the old translation")
    plan.remove((AGENTS / "AGENTS.md").as_posix(), "translation of AGENTS.md")
    for rel in tracked:
        if rel.startswith(commands) and rel.endswith(".md"):
            dst = (SKILLS / skill_name(rel[len(commands):]) / "SKILL.md").as_posix()
            plan.renames[rel] = dst
            plan.move(rel, dst)
        elif rel.startswith(references):
            plan.move(rel, (AGENTS / "references" / rel[len(references):]).as_posix())
    claude_skills = (CLAUDE / "skills").as_posix() + "/"
    bridged = _bridged(repo)
    for rel in tracked:
        if rel.startswith(claude_skills) and rel[len(claude_skills):].split("/", 1)[0] not in bridged \
                and rel != BRIDGE_MANIFEST.as_posix():
            plan.move(rel, (SKILLS / rel[len(claude_skills):]).as_posix())
    agents_skills = SKILLS.as_posix() + "/"
    for rel in tracked:
        parts = rel[len(agents_skills):].split("/") if rel.startswith(agents_skills) else []
        if len(parts) > 2 and parts[-1] == "SKILL.md" and rel not in plan.removed:
            dst = (SKILLS / "-".join(parts[:-1]) / "SKILL.md").as_posix()
            plan.renames[rel] = dst
            plan.move(rel, dst)
    legacy, home = (CLAUDE / "quenching.json").as_posix(), (AGENTS / "quenching.json").as_posix()
    if legacy in plan.tracked:
        if home in plan.tracked:
            if (repo / legacy).read_bytes() == (repo / home).read_bytes():
                plan.remove(legacy, f"identical to {home}")
            else:
                plan.conflicts.append({"path": home, "with": legacy,
                                       "why": "two configuration files differ"})
        else:
            plan.move(legacy, home)
    claude_md, agents_md = repo / "AGENTS.md", repo / "AGENTS.md"
    if agents_md.is_file() and not claude_md.exists():
        plan.ops.append({"op": "pointer", "path": "AGENTS.md"})
    if claude_md.is_file() and claude_md.read_text(encoding="utf-8").strip() != POINTER.strip():
        if agents_md.is_file() and agents_md.read_bytes() == claude_md.read_bytes():
            plan.ops.append({"op": "pointer", "path": "AGENTS.md"})
        elif agents_md.is_file():
            plan.conflicts.append({"path": "AGENTS.md", "with": "AGENTS.md",
                                   "why": "both carry their own instructions"})
        elif "AGENTS.md" not in plan.tracked:
            plan.conflicts.append({"path": "AGENTS.md", "with": "AGENTS.md",
                                   "why": "AGENTS.md is not tracked, so git mv cannot move it"})
        else:
            plan.ops.append({"op": "move", "from": "AGENTS.md", "to": "AGENTS.md"})
            plan.ops.append({"op": "pointer", "path": "AGENTS.md"})
    return plan


def invocation(path: str) -> str | None:
    """`.agents/skills/a/b.md` -> `/a:b`, the name the moved command answered to."""
    prefix = (CLAUDE / "commands").as_posix() + "/"
    return "/" + path[len(prefix):-3].replace("/", ":") if path.startswith(prefix) else None


def rewrite_text(text: str, renames: dict[str, str]) -> str:
    for old, new in sorted(renames.items(), key=lambda item: -len(item[0])):
        text = text.replace(old, new)
        name = invocation(old)
        if name and ":" in name:
            text = re.sub(r"(?<![\w/.:-])" + re.escape(name) + r"(?![\w:-])",
                          "/" + Path(new).parent.name, text)
    return (text.replace(".agents/references/", ".agents/references/")
            .replace(".agents/skills/", ".agents/skills/"))


def with_name(text: str, name: str) -> str:
    """Set the frontmatter `name:` to the folder name, which OpenCode requires to match."""
    nl = "\r\n" if text.startswith("---\r\n") else "\n"
    if not text.startswith("---" + nl):
        return f"---{nl}name: {name}{nl}---{nl}" + text
    start = len("---" + nl)
    end = text.find(nl + "---", start - len(nl))
    if end < 0:
        return text
    head = text[start:end + len(nl)] if end >= start else ""
    if re.search(r"(?m)^name:", head):
        head = re.sub(r"(?m)^name:[^\r\n]*", f"name: {name}", head, count=1)
    else:
        head = f"name: {name}{nl}" + head
    return "---" + nl + head + text[end + len(nl):]


def _git(repo: Path, *argv: str) -> None:
    subprocess.run(["git", "-C", str(repo), *argv], check=True, capture_output=True, text=True)


def apply(plan: Plan) -> None:
    repo = plan.repo
    for op in plan.ops:
        if op["op"] == "remove":
            _git(repo, "rm", "-q", "-r", "--", op["path"])
        elif op["op"] == "move":
            (repo / op["to"]).parent.mkdir(parents=True, exist_ok=True)
            _git(repo, "mv", "--", op["from"], op["to"])
        elif op["op"] == "pointer":
            (repo / op["path"]).write_text(POINTER, encoding="utf-8")
            _git(repo, "add", "--", op["path"])
    for op in plan.ops:
        parent = (repo / op.get("from", op.get("path", ""))).parent
        while parent != repo and parent.is_dir() and not any(parent.iterdir()):
            parent.rmdir()
            parent = parent.parent
    targets = {repo / op["to"] for op in plan.ops
               if op["op"] == "move" and op["to"].endswith(".md")}
    for path in sorted(targets):
        text = path.read_text(encoding="utf-8")
        new = rewrite_text(text, plan.renames)
        if path.name == "SKILL.md" and path.parent.parent == repo / SKILLS:
            new = with_name(new, path.parent.name)
        if new != text:
            path.write_text(new, encoding="utf-8")
            _git(repo, "add", "--", path.relative_to(repo).as_posix())


def add_arguments(sp) -> None:
    sp.add_argument("--target", default=".", help="the repository to migrate")
    sp.add_argument("--write", action="store_true", help="apply the plan with git mv / git rm")
    sp.add_argument("--json", action="store_true", help="machine-readable output")


def cmd_migrate(args, _root: str) -> int:
    repo = Path(os.path.abspath(args.target))
    if subprocess.run(["git", "-C", str(repo), "rev-parse", "--is-inside-work-tree"],
                      capture_output=True, text=True).stdout.strip() != "true":
        return refuse({"code": "ct-migrate-not-git", "target": str(repo),
                       "message": f"{repo} is not a git checkout; the migration moves files "
                                  "with git mv to keep their history"}, args.json)
    plan = build_plan(repo)
    if args.write and plan.conflicts:
        return refuse({"code": "ct-migrate-conflict", "conflicts": plan.conflicts,
                       "message": "the plan has conflicts; nothing was written",
                       "remedy": "settle each pair by hand, then rerun"}, args.json)
    if args.write and plan.ops:
        try:
            apply(plan)
        except subprocess.CalledProcessError as error:
            return refuse({"code": "ct-migrate-git", "command": " ".join(error.cmd),
                           "message": f"git failed mid-migration: {error.stderr.strip()}",
                           "remedy": "inspect `git status` in the target; the index holds "
                                     "what was applied so far"}, args.json)
    pending = [] if args.write else plan.ops
    payload = {"ok": not plan.conflicts, "target": str(repo),
               "conformant": not plan.ops and not plan.conflicts,
               "operations": plan.ops, "conflicts": plan.conflicts,
               "renames": plan.renames, "written": bool(args.write and plan.ops)}
    lines = [f"components migrate — {repo}",
             "  conformant, nothing to align" if payload["conformant"] else
             f"  operations: {len(plan.ops)}  conflicts: {len(plan.conflicts)}"
             + ("  (written)" if payload["written"] else "")]
    for op in plan.ops:
        lines.append("  " + " ".join(f"{k}={v}" for k, v in op.items()))
    for conflict in plan.conflicts:
        lines.append(f"  conflict: {conflict['path']} vs {conflict['with']} — {conflict['why']}")
    emit(args.json, payload, "\n".join(lines))
    return FINDINGS if pending or plan.conflicts else OK
