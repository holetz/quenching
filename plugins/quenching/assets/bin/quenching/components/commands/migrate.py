"""`cq components migrate` — move a target repository onto the generic `.agents/` layer.

The plan turns the legacy layout, where `.claude/` was the source and `.agents/` a Codex
translation of it, into the generic one: skills in `.agents/skills/<name>/SKILL.md`, references
in `.agents/references/**`, instructions in `AGENTS.md`, configuration in `.agents/quenching.json`,
and a pointer-only `CLAUDE.md` removed (Claude Code 2.1.277+ reads `AGENTS.md`). A nested `.claude/commands/<a>/<b>.md` becomes the flat
skill `<a>-<b>`, and a nested `.agents/skills/<a>/<b>/` folder becomes `<a>-<b>/` whole, its
sibling files with it.

An `.agents/skills/<path>/` or `.agents/references/<rel>` beside a `.claude/` source is a second
editable copy, whatever wrote it — the retired `cq components translate` included: it is a
conflict for the human to settle, and nothing is written. The legacy `openspec-*` skills and
`opsx/` commands are not this migration's and stay where they are.

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


def legacy_openspec(rel: str) -> bool:
    """`openspec init` leftovers: clearing them is a human's call, never this migration's."""
    return (rel.startswith((CLAUDE / "commands" / "opsx").as_posix() + "/")
            or rel.startswith((CLAUDE / "skills" / "openspec-").as_posix()))


def flat_destination(rel: str, skill_dirs: set[tuple[str, ...]]) -> str:
    """`a/b/scripts/x.sh` -> `a-b/scripts/x.sh` when `a/b/` is a skill folder: the deepest
    skill folder holding a file owns it, and the whole folder flattens together."""
    parts = tuple(rel.split("/"))
    for depth in range(len(parts) - 1, 0, -1):
        if parts[:depth] in skill_dirs:
            return "/".join(("-".join(parts[:depth]),) + parts[depth:])
    return rel


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


def _skill_dirs(paths: list[str]) -> set[tuple[str, ...]]:
    return {tuple(rel.split("/")[:-1]) for rel in paths if rel.split("/")[-1] == "SKILL.md"}


def skill_name(command_relpath: str) -> str:
    """`a/b.md` -> `a-b`: Claude Code discovers only flat skill folders."""
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
    """The `.claude/` source moves into `.agents/`; a copy already there is a conflict."""
    tracked = [rel for rel in _tracked(repo, CLAUDE, AGENTS, Path("CLAUDE.md"), Path("AGENTS.md"))
               if not legacy_openspec(rel)]
    plan = Plan(repo, set(tracked))
    commands = (CLAUDE / "commands").as_posix() + "/"
    references = (CLAUDE / "references").as_posix() + "/"
    for manifest in TRANSLATION_MANIFESTS:
        plan.remove(manifest.as_posix(), "manifest of the old translation")
    plan.remove((AGENTS / "AGENTS.md").as_posix(), "translation of CLAUDE.md")
    for rel in tracked:
        if rel.startswith(commands) and rel.endswith(".md"):
            dst = (SKILLS / skill_name(rel[len(commands):]) / "SKILL.md").as_posix()
            plan.renames[rel] = dst
            plan.move(rel, dst)
        elif rel.startswith(references):
            plan.move(rel, (AGENTS / "references" / rel[len(references):]).as_posix())
    claude_skills = (CLAUDE / "skills").as_posix() + "/"
    bridged = _bridged(repo)
    owned = [rel[len(claude_skills):] for rel in tracked if rel.startswith(claude_skills)
             and rel[len(claude_skills):].split("/", 1)[0] not in bridged
             and rel != BRIDGE_MANIFEST.as_posix()]
    owned_dirs = _skill_dirs(owned)
    for inner in owned:
        dst = (SKILLS / flat_destination(inner, owned_dirs)).as_posix()
        if dst != (SKILLS / inner).as_posix():
            plan.renames[claude_skills + inner] = dst
        plan.move(claude_skills + inner, dst)
    agents_skills = SKILLS.as_posix() + "/"
    nested = [rel[len(agents_skills):] for rel in tracked if rel.startswith(agents_skills)
              and rel not in plan.removed]
    dirs = {d for d in _skill_dirs(nested) if len(d) > 1}
    for inner in nested:
        dst = flat_destination(inner, dirs)
        if dst != inner:
            plan.renames[agents_skills + inner] = agents_skills + dst
            plan.move(agents_skills + inner, agents_skills + dst)
    legacy, home = (CLAUDE / "quenching.json").as_posix(), (AGENTS / "quenching.json").as_posix()
    if legacy in plan.tracked:
        if home in plan.tracked:
            if (repo / legacy).read_bytes() == (repo / home).read_bytes():
                plan.remove(legacy, f"identical to {home}")
            else:
                plan.conflicts.append({"path": home, "with": legacy,
                                       "why": "two configuration files differ"})
        elif (repo / home).exists():
            plan.conflicts.append({"path": home, "with": legacy,
                                   "why": "the home exists but is not tracked"})
        else:
            plan.move(legacy, home)
    claude_md, agents_md = repo / "CLAUDE.md", repo / "AGENTS.md"
    pointer_only = claude_md.is_file() and claude_md.read_text(
        encoding="utf-8").strip() == POINTER.strip()
    if claude_md.is_file() and pointer_only:
        # Claude Code 2.1.277+ reads AGENTS.md directly; the import is legacy residue.
        if "CLAUDE.md" in plan.tracked:
            plan.remove("CLAUDE.md", "legacy @AGENTS.md pointer; AGENTS.md is read directly")
    elif claude_md.is_file():
        if agents_md.is_file() and agents_md.read_bytes() == claude_md.read_bytes():
            plan.remove("CLAUDE.md", "duplicate of AGENTS.md; one source remains")
        elif agents_md.is_file():
            plan.conflicts.append({"path": "AGENTS.md", "with": "CLAUDE.md",
                                   "why": "both carry their own instructions"})
        elif "CLAUDE.md" not in plan.tracked:
            plan.conflicts.append({"path": "CLAUDE.md", "with": "AGENTS.md",
                                   "why": "CLAUDE.md is not tracked, so git mv cannot move it"})
        else:
            plan.ops.append({"op": "move", "from": "CLAUDE.md", "to": "AGENTS.md"})
    return plan


def invocation(path: str) -> str | None:
    """`.claude/commands/a/b.md` -> `/a:b`, the name the moved command answered to."""
    prefix = (CLAUDE / "commands").as_posix() + "/"
    return "/" + path[len(prefix):-3].replace("/", ":") if path.startswith(prefix) else None


def rewrite_text(text: str, renames: dict[str, str]) -> str:
    """Rewrite paths and invocations of the moved commands: `/a:b`, and the Skill tool's
    `Skill(skill="a:b")`, `Skill("a:b")`, `Skill(a:b)` and `"skill": "a:b"` forms."""
    for old, new in sorted(renames.items(), key=lambda item: -len(item[0])):
        text = text.replace(old, new)
        name = invocation(old)
        if name and ":" in name:
            flat = Path(new).parent.name
            text = re.sub(r"(?<![\w/.:-])" + re.escape(name) + r"(?![\w:-])", "/" + flat, text)
            bare = re.escape(name[1:])
            text = re.sub(r"(\bSkill\(\s*(?:skill\s*[=:]\s*)?[\"']?/?)" + bare
                          + r"(?=[\"'\s,)])", lambda m: m.group(1) + flat, text)
            text = re.sub(r"([\"']skill[\"']\s*:\s*[\"']/?)" + bare + r"(?=[\"'])",
                          lambda m: m.group(1) + flat, text)
    return (text.replace(".claude/references/", ".agents/references/")
            .replace(".claude/skills/", ".agents/skills/"))


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
