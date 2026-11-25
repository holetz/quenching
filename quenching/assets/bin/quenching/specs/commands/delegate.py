"""`cq specs delegate` — deliver ONE approved spec to the GitHub Copilot cloud agent.

The delegation is a command, not an agent: it reads the spec from the store, validates the facts
the cloud session depends on, and builds a deterministic briefing.  Without `--send` it prints the
briefing (the operator pipes it); with `--send` it hands the briefing to `gh agent-task create`,
which is the client's own invocation — the one function a preview change touches.

The branch contract is the spec's: `branch.work` is the base of the pull request the cloud agent
opens, and the head stays the client's own branch.  `branch.work` remains the integration branch,
so the record is never rewritten here, and this verb writes no record: the agent task is a fact of
the git host, not a substitute for `pr:`.

Refusals are before any remote write: the spec must be `approved` (develop's word), carry the
`branch:` record (the isolation), declare the `github` projection and a GitHub provider (the
environment), find the branch on `origin` (the PR base) and carry the projected custom agent.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess

from quenching.common.config import repository_document
from quenching.common.git import _git
from quenching.specs.backends import open_backend
from quenching.specs.commands.output import Emitter, display_locator
from quenching.specs.config import load_config

CUSTOM_AGENT = "quenching-spec-runner"
SPEC_SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
GH_TIMEOUT_S = 120


def add_parser(sub, add_json) -> None:
    sp = add_json(sub.add_parser(
        "delegate", help="deliver an approved spec to the GitHub Copilot cloud agent"))
    sp.add_argument("spec_id", nargs="?", metavar="ID", help="the spec id (same as --spec)")
    sp.add_argument("--spec", help="the spec ID")
    sp.set_defaults(id_required=True)
    sp.add_argument("--send", action="store_true",
                    help="create the cloud agent task; without it, print the brief")
    sp.add_argument("--custom-agent", default=CUSTOM_AGENT,
                    help=f"the projected custom agent (default: {CUSTOM_AGENT})")


def _refusal(out: Emitter, args, code: str, message: str, **extra) -> int:
    out.emit(args.json, {"ok": False, "code": code, "message": message, **extra},
             f"error: {message}")
    return 2


def _projections(root: str) -> list[str] | None:
    """`shared.projections` from the repository document, or None when unreadable."""
    document, _info, refusal = repository_document(root)
    if refusal:
        return None
    shared = (document or {}).get("shared")
    raw = shared.get("projections") if isinstance(shared, dict) else None
    return list(raw) if isinstance(raw, list) else []


def delegation_brief(info: dict, work: str, base: str, tasks_open: int) -> str:
    """The task description the cloud agent receives: the pointer to the spec, the branch
    contract, one-task-one-commit, the tick and the fixed report.  The spec's own sections stay
    on the store — the brief never restates them."""
    spec_id = info["id"]
    title = str((info.get("frontmatter") or {}).get("title") or "").strip()
    return (
        f"# Spec {spec_id} — {title}\n\n"
        f"You are the executor for ONE developed spec of this repository, delegated by "
        f"`cq specs delegate`.\n\n"
        f"- The spec lives on the git store branch `quenching`; read it with\n"
        f"  `.agents/quenching/bin/cq specs show {spec_id} --full`. The command fetches the "
        f"store itself.\n"
        f"- Your pull request's base is `{work}`. Never push to `{base}`, never merge, and never\n"
        f"  close or archive the spec.\n"
        f"- Execute the spec's `## Tasks` in order ({tasks_open} open task(s)). For each task:\n"
        f"  implement only what its `files:` declares, run its `verify:` from the repository\n"
        f"  root, and keep it green before ticking.\n"
        f"- One task, one commit. The subject follows the repository's convention:\n"
        f"  `{work}: <task-id> <task title>`. After the commit, tick the box with\n"
        f"  `.agents/quenching/bin/cq specs task --spec {spec_id} --check <task-id> "
        f"--subject \"<subject>\" --commit <sha>`.\n"
        f"- Rewrite only the `## Handoff` block of the open section, on the four events the\n"
        f"  execution contract names; never rewrite `## Problem`, `## Proposal` or `## Tasks`.\n"
        f"- Finish with the fixed report: SPEC/WORKTREE/STATE/SHAS/TASKS/CODEX/GATE/GATE_EXIT/PR/"
        f"DISCOVERIES/HOOKS/GIT AUDIT/NOTE. The conclude is the human's.\n")


def _gh_agent_task(root: str, base: str, agent: str,
                   brief: str) -> tuple[int, str, str]:
    """One client invocation, isolated here: `gh agent-task create` reads the brief on stdin and
    opens the session against `base`.  A missing `gh` is a refusal the caller builds."""
    argv = ["gh", "agent-task", "create", "-F", "-", "--base", base,
            "--custom-agent", agent]
    done = subprocess.run(argv, cwd=root, input=brief, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=GH_TIMEOUT_S)
    return done.returncode, done.stdout.strip(), done.stderr.strip()


def cmd_delegate(args, root: str, out: Emitter) -> int:
    spec_id = args.spec
    agent = str(getattr(args, "custom_agent", CUSTOM_AGENT) or CUSTOM_AGENT).strip()
    if not SPEC_SLUG.match(agent):
        return _refusal(out, args, "sp-delegate-agent",
                        f"--custom-agent must be a flat project-file slug, not '{agent}'")

    backend, err = open_backend(root)
    if err:
        return out.emit_err(args.json, err)
    info, rerr = backend.read_spec(spec_id)
    if rerr or info is None:
        return out.emit_err(args.json, rerr or {
            "code": "sp-unknown-id", "exit": 2, "id": spec_id,
            "message": f"no spec with id '{spec_id}'"})

    fm = info.get("frontmatter") or {}
    if not fm.get("approved"):
        return _refusal(out, args, "sp-delegate-approved",
                        f"spec {spec_id} is not approved; develop stamps `approved:` before "
                        f"a delegation",
                        remedy=f"run `/quenching-specs develop {spec_id}` or approve it first")
    branch = fm.get("branch") or {}
    work = str(branch.get("work") or "").strip() if isinstance(branch, dict) else ""
    base = str(branch.get("base") or "").strip() if isinstance(branch, dict) else ""
    if not work:
        return _refusal(out, args, "sp-delegate-branch",
                        f"spec {spec_id} has no `branch:` record; a delegation needs the work "
                        f"branch as the pull request's base",
                        remedy=f"run `/quenching-git branch {spec_id}` first")

    projections = _projections(root)
    if projections is None:
        return _refusal(out, args, "sp-delegate-config",
                        "the repository configuration is unreadable; fix the provider first")
    if "github" not in projections:
        return _refusal(out, args, "sp-delegate-projection",
                        "the delegation environment needs `shared.projections: [\"github\"]`: "
                        "the setup workflow and the projected runner agent come from it",
                        remedy="declare the key and run `cq deploy --target . --write`")
    cfg = load_config(root)
    provider = cfg.get("provider")
    card_provider = (cfg.get("card") or {}).get("provider") if isinstance(cfg.get("card"), dict) else None
    if provider != "github" and card_provider != "github":
        return _refusal(out, args, "sp-delegate-provider",
                        f"the delegation is GitHub-only; this repository's provider is "
                        f"{provider or 'unknown'}",
                        provider=provider)
    if not _git(root, "ls-remote", "--heads", "origin", work).strip():
        return _refusal(out, args, "sp-delegate-remote",
                        f"the branch {work} is not on `origin`; the cloud agent's pull request "
                        f"needs it as its base",
                        work=work,
                        remedy=f"push the branch first: `.agents/quenching/bin/cq git push "
                               f"--branch {work}`")
    agent_file = f".github/agents/{agent}.agent.md"
    if not (root and os.path.isfile(os.path.join(root, agent_file))):
        return _refusal(out, args, "sp-delegate-agent",
                        f"the projected custom agent {agent_file} is missing",
                        remedy="run `cq deploy --target . --write` to write the projection")

    tasks = info.get("tasks") or []
    tasks_open = sum(1 for task in tasks if not task.get("checked"))
    brief = delegation_brief(info, work, base, tasks_open)
    payload = {"ok": True, "id": info["id"], "title": str(fm.get("title") or ""),
               "path": display_locator(info.get("path"), root),
               "base": base, "work": work, "customAgent": agent,
               "tasks": {"open": tasks_open, "total": len(tasks)},
               "brief": brief, "sent": False}

    if not args.send:
        out.emit(args.json, payload, brief)
        return 0

    if shutil.which("gh") is None:
        return _refusal(out, args, "sp-delegate-gh",
                        "`gh` is not on PATH; the cloud agent task is created by the GitHub CLI",
                        remedy="install the GitHub CLI and authenticate with `gh auth login`")
    try:
        code, stdout, stderr = _gh_agent_task(root, work, agent, brief)
    except (OSError, subprocess.SubprocessError) as exc:
        return _refusal(out, args, "sp-delegate-gh",
                        f"`gh agent-task create` could not run: {exc}")
    if code != 0:
        return _refusal(out, args, "sp-delegate-gh",
                        f"`gh agent-task create` exited {code}: {stderr or stdout or 'no output'}",
                        detail=stderr or stdout)
    payload.update({"sent": True, "task": stdout})
    out.emit(args.json, payload, f"delegated {info['id']} to {agent} on {work}: "
                                 f"{stdout or 'task created'}")
    return 0
