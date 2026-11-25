"""The deterministic target tree `cq deploy` writes.

The tree is built in memory and applied by `cli`; nothing here touches the target.  Generated
files are the vendored payload, one skill per selected command, the Claude bridge and the Claude
agent definitions.  `AGENTS.md` and `.agents/quenching.json` are seeds: created only when absent.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath

from quenching.common.deploy import dumps_hash_manifest, read_manifest
from quenching.common.workspace import snippet as workspace_snippet
from quenching.common.version import VERSION
from quenching.components.commands import bridge
from quenching.deploy import mcpfiles
from quenching.deploy import settings as claude_settings
from quenching.deploy import translate

PAYLOAD = ".agents/quenching"
SKILLS = ".agents/skills"
CLAUDE_SKILLS = ".claude/skills"
CLAUDE_AGENTS = ".claude/agents"
OPENCODE_AGENTS = ".opencode/agents"
GITHUB_AGENTS = ".github/agents"
MODULE_SHORT = {
    "quenching-specs": "specs",
    "quenching-git": "git",
    "quenching-knowledge": "knowledge",
    "quenching-components": "components",
    "quenching-design": "design",
    "quenching-ops": "ops",
    "quenching-proof": "proof",
    "quenching-toolchain": "toolchain",
    "quenching-delivery": "delivery",
    "quenching-security": "security",
    "quenching-opensource": "opensource",
}
CORE = "specs,git,knowledge,components"
# A manifest recorded before the split names `quenching-align`: it stood for the two verticals now apart.
MODULE_ALIAS = {"align": "knowledge,components", "quenching-align": "knowledge,components"}
FRONT_BY_MODULE = {
    "quenching-specs": ("specs",),
    "quenching-git": ("git",),
    "quenching-knowledge": ("knowledge",),
    "quenching-components": ("components",),
    "quenching-design": ("design",),
    "quenching-ops": ("ops",),
    "quenching-proof": ("proof",),
    "quenching-toolchain": ("toolchain",),
    "quenching-delivery": ("delivery",),
    "quenching-security": ("security",),
    "quenching-opensource": ("opensource",),
}
ASSETS_BY_MODULE = {
    "quenching-specs": ("assets/specs", "assets/portal"),
    "quenching-knowledge": ("assets/knowledge", "assets/zensical"),
    "quenching-design": ("assets/design",),
    "quenching-opensource": ("assets/opensource",),
}
MARKDOWN_DIRS = ("references", "assets/templates", "assets/knowledge", "assets/zensical",
                 "assets/design", "assets/opensource", "assets/specs")
IGNORE = {"__pycache__", "tests", "evals", "checks"}


class DeployError(ValueError):
    pass


def source_root() -> Path:
    """The installed plugin root that carries `assets/`, `skills/` and `references/`."""
    return Path(__file__).resolve().parents[4]


def _is_build(path: Path) -> bool:
    return "__pycache__" in path.parts or path.suffix in (".pyc", ".pyo")


def _mode(path: Path) -> int:
    return 0o755 if path.stat().st_mode & 0o111 else 0o644


def eol_canonical(data: bytes) -> bytes:
    """Text with LF line ends — the bytes git keeps in the index.

    A `core.autocrlf` checkout holds CRLF in the work tree for the same blob, in the source and in
    the target alike. Binary data (a NUL byte, or not UTF-8) is returned untouched.
    """
    if b"\r\n" not in data or b"\0" in data:
        return data
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return data.replace(b"\r\n", b"\n")


def _read(path: Path) -> bytes:
    """A source file as the index holds it; `read_text` already gives LF on the translated paths."""
    return eol_canonical(path.read_bytes())


def _add(tree: dict[str, tuple[bytes, int]], rel: str, data: bytes, mode: int = 0o644) -> None:
    tree[PurePosixPath(rel).as_posix()] = (data, mode)


def _add_tree(tree: dict, source: Path, rel: str, transform=None, exclude=IGNORE) -> None:
    root = source / rel
    if not root.exists():
        return
    paths = [root] if root.is_file() else sorted(root.rglob("*"))
    for path in paths:
        if not path.is_file() or _is_build(path) or any(part in exclude for part in path.parts):
            continue
        relative = path.relative_to(source).as_posix()
        data = _read(path)
        if transform is not None and path.suffix == ".md":
            data = transform(data.decode("utf-8")).encode("utf-8")
        _add(tree, PAYLOAD + "/" + relative, data, _mode(path))


def load_modules(source: Path) -> dict:
    return json.loads((source / "assets" / "modules.json").read_text(encoding="utf-8"))


def normalize_modules(values: list[str] | None, manifest: dict) -> list[str]:
    # Registry order, never a set's: `all` lands in the deploy manifest, compared byte for byte.
    owned = [module["name"] for module in manifest["modules"] if "owned" in module]
    known = set(owned)
    selected: list[str] = []
    for raw in values or ["core"]:
        token = raw.strip()
        if not token:
            continue
        if token == "core":
            token = CORE
        elif token == "all":
            token = ",".join(MODULE_SHORT[name] for name in owned)
        parts = []
        for part in token.split(","):
            parts += MODULE_ALIAS.get(part.strip(), part).split(",")
        for part in parts:
            part = part.strip()
            if not part:
                continue
            name = part if part.startswith("quenching-") else "quenching-" + part
            if name not in known:
                raise DeployError(f"unknown module: {part}")
            if name not in selected:
                selected.append(name)
    if "quenching-specs" not in selected:
        # The one `cq` owner is not optional in a deployed target.
        selected.insert(0, "quenching-specs")
    return selected


def profiles_for(modules: list[str]) -> list[str]:
    fronts: list[str] = []
    for module in modules:
        for front in FRONT_BY_MODULE.get(module, ()):
            if front not in fronts:
                fronts.append(front)
    local = [front for front in ("knowledge", "components", "design", "ops", "proof", "toolchain",
                                 "delivery", "opensource") if front in fronts]
    return (["specs"] if "quenching-specs" in modules else []) + local


def _selected_modules(manifest: dict, modules: list[str]) -> list[dict]:
    return [module for module in manifest["modules"] if module.get("name") in modules]


def _packages(selected: list[dict]) -> list[str]:
    packages: list[str] = []
    for module in selected:
        owned = module.get("owned", {})
        for package in [*owned.get("packages", []),
                        *module.get("generatedSupport", {}).get("packages", [])]:
            if package not in packages:
                packages.append(package)
    return packages


def _agents(source: Path) -> dict[str, Path]:
    return {path.stem: path for path in sorted((source / "agents").glob("*.md"))}


def _agents_md(target: Path, dirs: tuple[str, ...]) -> str:
    docs = target / "docs" / "index.md"
    knowledge = ("- Durable knowledge: [`docs/index.md`](docs/index.md).\n" if docs.is_file()
                 else "- Durable knowledge: run `/quenching-knowledge align` to install the "
                      "`/docs/` bundle.\n")
    if CLAUDE_SKILLS in dirs and SKILLS not in dirs:
        skills = ("- Skills: `.claude/skills/` (published for the declared clients); author a "
                  "target's own skill in `.agents/skills/`, which is copied here.\n")
    elif CLAUDE_SKILLS in dirs:
        skills = "- Skills: `.agents/skills/` (source) and `.claude/skills/` (generated copy).\n"
    else:
        skills = ("- Skills: `.agents/skills/` (source; a target's own skill is authored "
                  "here).\n")
    interface = (
        "This repository uses quenching. The editable automation surface is `.agents/`; the\n"
        "Claude Code bridge under `.claude/skills/` is generated from it.\n\n"
        if CLAUDE_SKILLS in dirs else
        "This repository uses quenching. The editable automation surface is `.agents/`.\n\n"
    )
    return (
        "# AGENTS.md\n\n"
        + interface +
        "- Configuration: [`.agents/quenching.json`](.agents/quenching.json).\n"
        + knowledge + skills +
        "- Deployed runtime: `.agents/quenching/` (generated; do not edit).\n"
        "- Upgrade with `cq deploy --write` from a new quenching release; never edit a generated "
        "file.\n"
    )


def _seed_config(target: Path, profiles: list[str]) -> str:
    from quenching.config.seed import seed_document
    document = seed_document(str(target))
    # Deploy installs the surface; it does not choose a specs backend. The target's own
    # `/quenching-knowledge align` (or `cq doctor --setup`) records that decision.
    document.pop("backend", None)
    shared = document.setdefault("shared", {})
    shared["profiles"] = {"installed": profiles}
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def _uvx_shim(version: str) -> tuple[bytes, bytes]:
    source = f"git+https://github.com/holetz/quenching@{version}#subdirectory=quenching"
    sh = ("#!/usr/bin/env sh\n"
          f"exec uvx --from \"{source}\" cq \"$@\"\n")
    cmd = ("@echo off\r\n"
           f"uvx --from \"{source}\" cq %*\r\n")
    return sh.encode(), cmd.encode()


_VENDOR_SH = '''#!/usr/bin/env python3
"""cq — the launcher of this deployed surface, generated by `cq deploy`; do not edit.

It runs `../assets/bin/cq` and hands the shell cq's own exit code (0 ok / 1 findings / 2 refusal),
which every command body branches on. On POSIX it re-executes with `os.execv`, one process. On
Windows `os.execv` joins the arguments unquoted, so one with a space arrives split, and a second
interpreter per call is scanned again by the target's antivirus; there the launcher puts
`assets/bin` on `sys.path` (the `sys.path[0]` Python would build from the script's directory, which
`cq` needs to reach its `quenching` package) and calls `main` in the same process. The root comes
from `__file__`, never
from a variable the harness expands.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
REAL = os.path.join(ROOT, "assets", "bin", "cq")

if os.name == "nt":
    import runpy
    sys.path.insert(0, os.path.dirname(REAL))
    cq = runpy.run_path(REAL)  # run_name is not "__main__", so cq's own UTF-8 forcing never ran
    cq["force_utf8_streams"]()
    sys.exit(cq["main"](sys.argv[1:]))
os.execv(sys.executable, [sys.executable, REAL, *sys.argv[1:]])
'''

_VENDOR_CMD = (
    "@echo off\r\n"
    "rem cq launcher for a Windows PATH: runs ..\\assets\\bin\\cq with Python and hands back its exit code.\r\n"
    "setlocal\r\n"
    'set "CQ=%~dp0..\\assets\\bin\\cq"\r\n'
    "where py >nul 2>nul\r\n"
    "if %ERRORLEVEL% EQU 0 (\r\n"
    '  py -3 "%CQ%" %*\r\n'
    ") else (\r\n"
    '  python "%CQ%" %*\r\n'
    ")\r\n"
    "exit /b %ERRORLEVEL%\r\n"
)


def skill_dirs(harnesses: list[str]) -> tuple[str, ...]:
    """The directories this deploy publishes skills into: the minimal cover of what the
    declared harnesses read.

    Measured 2026-11-25: Claude Code 2.1.332 reads `.claude/skills` only, and OpenCode reads both,
    the `.agents` copy winning a repeated name. So a target declaring `claude` publishes once in
    `.claude/skills` — `opencode` reads it — and a deploy without `claude` (opencode alone, or no
    harness) keeps the generic layer. The `codex` harness was removed (ADR 0020); a client that
    reads only `.agents/skills` would force that copy if it ever returns as a harness.
    """
    return (CLAUDE_SKILLS,) if "claude" in harnesses else (SKILLS,)


def _without_marker(text: str, name: str) -> str:
    """The source form of a Claude copy.

    A target's vendored payload carries no skill source, so the installed folder is the last-resort
    source for a generated skill; the `.claude` copy's `SKILL.md` carries the bridge marker, and the
    publication loop adds it back only when it writes `.claude`.
    """
    return text.replace(bridge.marker(name) + "\n", "", 1)


def _bridge_tree(tree: dict, target: Path, dirs: tuple[str, ...],
                 generated_names: set[str]) -> None:
    """The target's own skills get the marked Claude copy, when `.claude/skills` is published.

    The deploy's generated skills are written by `build_tree` itself; this manifest lists only
    the target's own files, so `cq components bridge --check` never reads a generated skill as a
    source it lost, and a claude-only target has nothing for the bridge to own.
    """
    if CLAUDE_SKILLS not in dirs:
        return
    source = target / ".agents" / "skills"
    # A file the previous deploy owned is leaving with this write, not the target's: bridging it
    # would re-own a skill whose source the same write deletes.
    owned = (read_manifest(str(target)) or {}).get("files")
    leaving = set(owned) if isinstance(owned, dict) else set()
    manifest: dict[str, str] = {}
    if source.is_dir():
        for folder in sorted(source.iterdir()):
            if not folder.is_dir() or folder.name in generated_names:
                continue
            # A file the previous deploy owned is leaving with this write, not the target's: a
            # folder whose `SKILL.md` is one of those is not a skill any more, and the stray
            # files beside it stay in their `.agents` home.
            if f"{SKILLS}/{folder.name}/{bridge.SKILL_FILE}" in leaving:
                continue
            # Only a folder carrying a `SKILL.md` is a skill, the same rule the bridge's own
            # `expected_tree` reads.
            if not (folder / bridge.SKILL_FILE).is_file():
                continue
            for path in sorted(folder.rglob("*")):
                if not path.is_file():
                    continue
                relative = path.relative_to(source).as_posix()
                if f"{SKILLS}/{relative}" in leaving:
                    continue
                data = _read(path)
                if path.name == bridge.SKILL_FILE and path.parent == folder:
                    data = bridge.with_marker(data.decode("utf-8"), folder.name).encode("utf-8")
                _add(tree, CLAUDE_SKILLS + "/" + relative, data, _mode(path))
                manifest[relative] = hashlib.sha256(data).hexdigest()
    if manifest:
        document = {
            "generator": "cq deploy (cq components bridge marker)",
            "source": SKILLS,
            "verifiedClaudeCode": bridge.VERIFIED_CLAUDE_CODE,
            "files": dict(sorted(manifest.items())),
        }
        _add(tree, CLAUDE_SKILLS + "/.generated-files.json",
             dumps_hash_manifest(document).encode(), 0o644)


def mcp_argv(mcp: dict) -> list[str]:
    """The Python prefix, the vendored entry point and the mount: the whole server for `all`, the
    mounted pillar's own `mcp` for `specs`, and `mcp --only <pillars>` for a named mount (`core`) or
    a comma list, with the name expanded so the registered file says which pillars it publishes."""
    from quenching.mcp import catalog
    mount = mcp["mount"]
    if mount == "all":
        tail = ["mcp"]
    elif mount == "specs":
        tail = ["specs", "mcp"]
    else:
        tail = ["mcp", "--only", ",".join(catalog.mount_pillars(mount))]
    return [*mcp["command"], PAYLOAD + "/assets/bin/cq", *tail]


def _declared_hooks(selected: list[dict]) -> list[dict]:
    return [hook for module in selected for hook in module.get("owned", {}).get("hooks", [])]


def build_tree(source: Path, target: Path, modules: list[str], harnesses: list[str],
               runtime: str = "vendor", profiles: list[str] | None = None,
               mcp: dict | None = None, python: list[str] | None = None,
               hooks_python: list[str] | None = None,
               projections: list[str] | None = None,
               workspace: bool = False) -> dict:
    manifest = load_modules(source)
    selected = _selected_modules(manifest, modules)
    if not selected:
        raise DeployError("no module selected")
    packages = _packages(selected)
    # The registered whole server replaces every `cq` verb it serves: the grants the harness reads
    # drop that shell door unless `shared.mcp.cliFallback` keeps both.
    narrow = bool(mcp) and mcp["mount"] == "all" and not mcp.get("cliFallback")
    # A named mount publishes fewer tools: the grants it writes never name a tool the server does
    # not publish, so `.claude/agents` and `.opencode/agents` do not declare phantom tools.
    from quenching.mcp import catalog as mcp_catalog
    mount = (None if not mcp or mcp["mount"] == "all"
             else frozenset(mcp_catalog.mount_pillars(mcp["mount"])))
    missing = [package for package in packages
               if not (source / "assets" / "bin" / "quenching" / package).is_dir()]
    if missing:
        raise DeployError("source does not carry the selected module packages: "
                          + ", ".join(sorted(missing)))
    tree: dict[str, tuple[bytes, int]] = {}

    # Payload: the runtime and the shared procedure the conductor reads.
    if runtime == "vendor":
        for package in packages:
            _add_tree(tree, source, "assets/bin/quenching/" + package)
        # quenching_launch.py is the wheel entry point only (the build maps it to launch.py);
        # the vendored target runs the generated bin/cq, so a clone and a uvx deploy write the same tree.
        _add_tree(tree, source, "assets/bin/cq")
        _add(tree, PAYLOAD + "/bin/cq", _VENDOR_SH.encode(), 0o755)
        _add(tree, PAYLOAD + "/bin/cq.cmd", _VENDOR_CMD.encode(), 0o644)
    _add_tree(tree, source, "assets/modules.json")
    _add_tree(tree, source, "VERSION")
    _add_tree(tree, source, "references", translate.reference_document)
    _add_tree(tree, source, "assets/templates", translate.reference_document)
    _add_tree(tree, source, "assets/translation")
    # The identity hooks: inert until a clone points `core.hooksPath` at them.
    _add_tree(tree, source, "assets/githooks")
    for module in selected:
        for rel in ASSETS_BY_MODULE.get(module["name"], ()):
            _add_tree(tree, source, rel, translate.reference_document)
    # The hooks the selected modules declare, installed in `.claude/settings.json` by `cli`; Claude
    # Code and the GitHub Copilot harness both read that file, so the bodies travel with `claude`.
    hooks = _declared_hooks(selected) if "claude" in harnesses else []
    # Every entry runs the dispatcher, which runs the bodies; both travel.
    if hooks:
        _add_tree(tree, source, f"assets/hooks/{claude_settings.DISPATCH}.py")
    for hook in hooks:
        _add_tree(tree, source, f"assets/hooks/{hook['name']}.py")

    # The payload's agents are the source a target-local deploy re-reads: never narrowed.
    for name, path in _agents(source).items():
        _add(tree, f"{PAYLOAD}/agents/{name}.md",
             translate.agent_document(path.read_text(encoding="utf-8"), name).encode(), _mode(path))

    if runtime == "uvx":
        sh, cmd = _uvx_shim(VERSION)
        _add(tree, PAYLOAD + "/bin/cq", sh, 0o755)
        _add(tree, PAYLOAD + "/bin/cq.cmd", cmd, 0o644)

    # A skill is its whole folder: the `SKILL.md` and the `references/` beside it. Each skill is
    # rendered once and published into the directories the declared clients read.
    dirs = skill_dirs(harnesses)
    # A module outside the selection whose mirror the target already tracks: the files stay, so
    # they are regenerated from the source like a selected module's, never left to age while
    # `--check` reads green. A module the target never carried adds nothing.
    # A folder the last deploy owned is a module the caller just deselected: that one leaves with
    # the write, it is not a mirror.
    outside = [module for module in manifest["modules"] if module not in selected]
    previous = read_manifest(str(target)) or {}
    left = set(previous.get("files") or {})
    kept_before = set(previous.get("mirrors") or [])
    mirrored: list[str] = []
    folders: list[str] = []

    def kept(rel: str, marker: str) -> bool:
        present = ((target / rel / marker).is_file() if marker != "*.py"
                   else any((target / rel).glob("*.py")))
        return present and (rel in kept_before
                            or not any(owned.startswith(rel + "/") for owned in left))

    for package in _packages(outside):
        folder = "assets/bin/quenching/" + package
        if package not in packages and kept(PAYLOAD + "/" + folder, "*.py") and (source / folder).is_dir():
            before = set(tree)
            folders.append(PAYLOAD + "/" + folder)
            _add_tree(tree, source, folder)
            mirrored.extend(sorted(set(tree) - before))

    skill_names: list[str] = []
    generated: dict[str, dict[str, tuple[bytes, int]]] = {}
    mirrors: set[str] = set()
    # A skill mirror is read from the directory this deploy publishes: `.claude/skills` for a
    # target declaring `claude`, `.agents/skills` otherwise. There is no second generated copy:
    # a target's own skill stays under `.agents/skills` and is bridged.
    published = dirs[0]
    skill_sources = [(name, True) for module in selected for name in module["owned"]["skills"]]
    skill_sources += [(name, False) for module in outside
                      for name in module.get("owned", {}).get("skills", [])
                      # A mirror read where this deploy publishes it, or recorded at its old
                      # `.agents/skills` home by a manifest written before this layout: the
                      # source stays the truth and the copy moves to the new directory.
                      if (kept(published + "/" + name, bridge.SKILL_FILE)
                          or f"{SKILLS}/{name}" in kept_before)
                      and (source / "skills" / name).is_dir()]
    for name, chosen in skill_sources:
        if name in skill_names:
            continue
        if chosen:
            skill_names.append(name)
        else:
            mirrors.add(name)
        root = source / "skills" / name
        # A vendored payload carries no skill source: the installed folder is already the
        # generated form, so it is re-asserted byte for byte.
        installed = not root.is_dir()
        from_claude = False
        if installed:
            root = target / SKILLS / name
        if installed and not root.is_dir():
            # A target deployed for a claude-only client has the generated form only in
            # `.claude/skills`; its own `cq deploy --check` must re-assert that copy.
            root = target / CLAUDE_SKILLS / name
            from_claude = root.is_dir()
        if not root.is_dir():
            continue
        files = generated.setdefault(name, {})
        for path in sorted(root.rglob("*")):
            if not path.is_file() or _is_build(path):
                continue
            rel = path.relative_to(root).as_posix()
            if installed:
                data = _read(path)
                if from_claude and rel == "SKILL.md":
                    data = _without_marker(data.decode("utf-8"), name).encode("utf-8")
            elif rel == "SKILL.md":
                data = translate.skill_document(path.read_text(encoding="utf-8"), name,
                                                narrow, mount).encode("utf-8")
            elif path.suffix == ".md":
                data = translate.reference_document(path.read_text(encoding="utf-8")).encode("utf-8")
            else:
                data = _read(path)
            files[rel] = (data, _mode(path))

    for name, files in generated.items():
        for rel, (data, mode) in files.items():
            for out in dirs:
                bridged = (bridge.with_marker(data.decode("utf-8"), name).encode("utf-8")
                           if out == CLAUDE_SKILLS and rel == bridge.SKILL_FILE else data)
                _add(tree, f"{out}/{name}/{rel}", bridged, mode)
                if name in mirrors:
                    mirrored.append(f"{out}/{name}/{rel}")
                    if f"{out}/{name}" not in folders:
                        folders.append(f"{out}/{name}")

    if CLAUDE_SKILLS in dirs:
        _bridge_tree(tree, target, dirs, set(generated))
    if "claude" in harnesses:
        for name, path in _agents(source).items():
            _add(tree, f"{CLAUDE_AGENTS}/{translate.agent_name(name)}.md",
                 translate.agent_document(path.read_text(encoding="utf-8"), name,
                                          narrow, mount).encode(), 0o644)
    if "opencode" in harnesses:
        # OpenCode reads `.opencode/agents/`, not `.claude/agents/`; without this copy a target
        # would keep every skill and lose the operator agents.
        for name, path in _agents(source).items():
            _add(tree, f"{OPENCODE_AGENTS}/{translate.agent_name(name)}.md",
                 translate.opencode_agent_document(path.read_text(encoding="utf-8"), name,
                                                   narrow, mount).encode(),
                 0o644)
    if "github" in (projections or []):
        # The GitHub Copilot harness reads the native format, not the Claude one; a repository
        # declares the projection, so a target without Copilot pays no second register.
        for name, path in _agents(source).items():
            _add(tree, f"{GITHUB_AGENTS}/{translate.agent_name(name)}.agent.md",
                 translate.copilot_agent_document(path.read_text(encoding="utf-8"), name,
                                                  narrow, mount).encode(),
                 0o644)

    seeds = {
        "AGENTS.md": _agents_md(target, dirs),
        ".agents/quenching.json": _seed_config(target, profiles or profiles_for(modules)),
    }
    if workspace:
        # A client projection, opted in by the repository's own `shared.workspace.vscode`:
        # created only when absent, never listed in the manifest, never drift-checked.
        seeds[".vscode/settings.json"] = workspace_snippet()
    document = {
        "generator": "cq deploy",
        "version": VERSION,
        "source": "quenching",
        "modules": modules,
        "profiles": profiles or profiles_for(modules),
        "harnesses": harnesses,
        "runtime": runtime,
        "skills": sorted(skill_names),
        "files": {rel: hashlib.sha256(data).hexdigest() for rel, (data, _mode_) in sorted(tree.items())},
    }
    if folders:
        # The tracked mirrors of modules outside the selection, kept in step with the source.
        document["mirrors"] = sorted(folders)
    if mcp:
        # The harness files are the user's and merged by `cli`; the manifest names which ones.
        document["mcp"] = mcp
        document["mcpFiles"] = mcpfiles.harness_files(harnesses)
    settings = None
    if "claude" in harnesses:
        # `.claude/settings.json` is the user's file: it is merged by `cli`, never listed in `files`.
        # `attribution` holds the keys this deploy wrote; `cli` replaces it once the merge ran.
        # The hooks' own prefix: never `uv` (`mcpfiles.direct_prefix`), recorded so it does not flap.
        prefix = list(hooks_python or python or claude_settings.PYTHON)
        # A registered `.mcp.json` server is approved by name, so it starts without a prompt.
        settings = {"hooks": claude_settings.desired_entries(hooks, prefix),
                    "attribution": dict(claude_settings.ATTRIBUTION),
                    "mcpjson": bool(mcp)}
        document["claudeSettings"] = {"hooks": [hook["name"] for hook in hooks],
                                      "attribution": sorted(claude_settings.ATTRIBUTION),
                                      "command": prefix, "mcpjson": bool(mcp),
                                      "permissions": []}
    return {"tree": tree, "seeds": seeds, "manifest": document, "settings": settings,
            "mirrored": sorted(set(mirrored))}
