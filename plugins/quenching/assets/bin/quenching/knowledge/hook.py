"""HOOK mode — the three Claude Code events this pillar answers, and the JSON it answers with.

Moved verbatim out of the pre-refactor OKF validator script, with TWO mechanical changes: the
frontmatter call shape (bare dict from `parse_frontmatter`, the two fence bits from the
`frontmatter_block` sidecar), and `0` written as `OK` where it already meant "the verb
answered".

HOOK  (reads the hook JSON on stdin)
Dispatches on `hook_event_name`:
- **PostToolUse** (matcher `Write|Edit`): validates the single touched
  `/.knowledge/**` file and, on a finding, **PROPOSES** the fix via
  `additionalContext` (exit 0). With `blockOnFail: true` it escalates to
  `decision: block` (the reason is fed back to Claude). It also touches the
  **dirty marker** (a stamp file in the system temp dir) so the Stop sweep
  knows the bundle changed this session.
- **Stop**: with `stopScan: "dirty"` (the default), exits immediately when
  the dirty marker is absent — a turn that touched no `/.knowledge/**` file costs
  one stat, not a full-bundle scan. When the marker is present (or
  `stopScan: "always"`), validates the whole bundle in a SINGLE read pass
  and PROPOSES residual gaps (`additionalContext`, exit 0); the marker is
  cleared after any completed scan and kept when the deadline aborts one.
  Honors `stop_hook_active` to avoid loops.
- **PreToolUse** (matcher `Write|Edit`, OPT-IN via `hardBlock: true`): inspects
  the *pending* `tool_input.content` and **BLOCKS** (`permissionDecision: deny`)
  only the two hard violations — writing an `index.md` that carries a concept
  `type`, or writing a concept doc with no non-empty `type`. This is the single
  hard gate; everything else proposes. Off by default (proposes, never blocks).

EVERY PATH RETURNS `OK`. The hook signals through the JSON on stdout — `_emit_block`,
`_emit_deny`, `_emit_additional_context` — and never through the exit code, which is why
this pillar has no `FINDINGS` step in hook mode and no refusal step anywhere.

THE MODE IS A VERB, NEVER A HEURISTIC. `run_hook` is a plain function with no argv and no
`isatty` test of its own; `quenching.knowledge.cli.main` is what routes the declared `hook`
token here. Nothing in this module inspects the terminal.
"""
from __future__ import annotations

import json
import os
import time

from quenching.common.frontmatter import frontmatter_block, parse_frontmatter
from quenching.common.output import OK
from quenching.knowledge.config import DEFAULTS, _load_config, _project_dir, _read_stdin
from quenching.knowledge.corpus import _is_ignored_path
from quenching.knowledge.marker import _clear_marker, _marker_path, _touch_marker
from quenching.knowledge.render import _render_proposal, _split
from quenching.knowledge.schema import EXEMPT, TAG, _nonempty
from quenching.knowledge.validate import validate_file, validate_tree


# --------------------------------------------------------------------------- #
# hook outputs
# --------------------------------------------------------------------------- #
def _emit_additional_context(event: str, text: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}))


def _emit_block(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": reason}))


def _emit_deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))


def hard_block_exempt(base: str) -> bool:
    """Filenames the PreToolUse hard gate never denies: the harness pointers, the
    retired `log.md`, and the migration README. A named predicate rather than an
    inline condition so `selftest` can assert the retirement without standing up a
    hook invocation — `run_hook` reads its config from disk beside this script, so a
    subprocess would return early on `hardBlock` being off and prove nothing."""
    return base in EXEMPT or base in ("log.md", "README.md")


def _under_docs(rel: str, docs_dir: str) -> bool:
    return rel == docs_dir or rel.startswith(docs_dir.rstrip("/") + "/")


def _docs_relpath(rel: str, docs_dir: str) -> str:
    """`rel` is project-relative (already confirmed `_under_docs`); returns the
    path relative to the bundle root instead, for `_is_ignored_path`."""
    return rel[len(docs_dir):].lstrip("/")


# --------------------------------------------------------------------------- #
# HOOK
# --------------------------------------------------------------------------- #
def run_hook() -> int:
    data = _read_stdin()
    project = _project_dir(data)
    cfg = _load_config(project)
    if cfg.get("enabled") is False:
        return OK
    event = data.get("hook_event_name") or ""
    docs_dir = ".knowledge"
    bundle_root = os.path.join(project, docs_dir)
    started = time.monotonic()
    deadline = float(cfg.get("deadlineMs", DEFAULTS["deadlineMs"])) / 1000.0
    ignore_globs = tuple(cfg.get("ignoreGlobs") or ())

    if event == "PreToolUse":
        if not cfg.get("hardBlock"):
            return OK  # hard gate opt-in; default is propose-only (PostToolUse handles it)
        tool_input = data.get("tool_input") or {}
        file_path = tool_input.get("file_path") or ""
        content = tool_input.get("content")
        if content is None:  # Edit gives no full content → cannot judge pre-write; let it through
            return OK
        rel = os.path.relpath(os.path.abspath(file_path), os.path.abspath(project)).replace(os.sep, "/")
        if not file_path.endswith(".md") or not _under_docs(rel, docs_dir):
            return OK
        if _is_ignored_path(_docs_relpath(rel, docs_dir), ignore_globs):
            return OK  # regenerable/vendored path (ignoreGlobs) — not authored OKF knowledge
        base = os.path.basename(file_path)
        if hard_block_exempt(base):
            return OK  # harness/reserved/migration files — never hard-blocked
        if base == "index.md":
            fm = parse_frontmatter(content)
            if _nonempty(fm, "type"):
                _emit_deny(f"[{TAG}] `index.md` is a reserved OKF listing — it must not carry a concept "
                           "`type`. Move that content into a concept doc and keep the index a link listing.")
                return OK
        else:
            fm = parse_frontmatter(content)
            has_block, well_formed = frontmatter_block(content)
            if not has_block or not well_formed or not _nonempty(fm, "type"):
                _emit_deny(f"[{TAG}] this concept doc needs parseable frontmatter with a non-empty `type` "
                           "(OKF requirement). Add the `type` before writing, or use `quenching-docs-add`.")
                return OK
        return OK

    if event == "PostToolUse":
        tool_input = data.get("tool_input") or {}
        file_path = tool_input.get("file_path") or ""
        if not file_path.endswith(".md"):
            return OK
        rel = os.path.relpath(os.path.abspath(file_path), os.path.abspath(project)).replace(os.sep, "/")
        if not _under_docs(rel, docs_dir):
            return OK
        if _is_ignored_path(_docs_relpath(rel, docs_dir), ignore_globs):
            return OK  # regenerable/vendored path (ignoreGlobs) — not authored OKF knowledge
        _touch_marker(project)  # bundle changed — arm the Stop sweep for this session
        findings = validate_file(file_path, bundle_root)
        errors, warns = _split(findings)
        report = [f for f in findings if f[0] == "ERROR" or (f[0] == "WARN" and cfg.get("warnAsError"))]
        if not report:
            return OK
        if errors and cfg.get("blockOnFail"):
            _emit_block(_render_proposal(findings))
        else:
            _emit_additional_context("PostToolUse", _render_proposal(findings))
        return OK

    if event == "Stop":
        if data.get("stop_hook_active"):
            return OK
        if str(cfg.get("stopScan", "dirty")) != "always" and not os.path.exists(_marker_path(project)):
            return OK  # no .knowledge/** edit since the last completed scan — 1 stat, no walk
        findings = validate_tree(bundle_root, deadline=started + deadline, ignore_globs=ignore_globs)
        if findings is None:
            return OK  # deadline expired mid-walk — abort silently, KEEP the marker for next turn
        _clear_marker(project)  # scan completed; a fixing edit re-arms the marker via PostToolUse
        errors, warns = _split(findings)
        report = [f for f in findings if f[0] == "ERROR" or (f[0] == "WARN" and cfg.get("warnAsError"))]
        if not report:
            return OK
        if errors and cfg.get("blockOnFail"):
            _emit_block(_render_proposal(findings))
        else:
            _emit_additional_context("Stop", _render_proposal(findings))
        return OK

    return OK
