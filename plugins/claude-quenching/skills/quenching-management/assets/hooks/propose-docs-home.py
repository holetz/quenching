#!/usr/bin/env python3
"""Portable hook (PostToolUse, matcher Write|Edit) — coverage of the ``docs/`` taxonomy.

Payload of the ``quenching-management`` method. Generic and self-contained.
Materializes the **trigger (1) "by event" of Step 8** (recurring maintenance
loop) on the axis of the canonical ``docs/`` taxonomy ([docs-taxonomy.md]): when the agent writes
or edits a file **under ``docs/``**, this hook checks the touched file against
the canonical taxonomy ([docs-taxonomy.md]) and, if something does not fit — a home in
a **variant name** to migrate, **two homes** for the same layer, material **without
a home**, a binary **without a sidecar**, a doc **without an audience label** —,
**PROPOSES** (never blocks) the fix **while the edit is fresh**. It is the
continuous audit applied to the canonical ``docs/`` taxonomy at runtime.

Distinct from the **lifecycle** sibling hooks (Stop ``propose-knowledge-delta``,
SessionStart ``reinject-conventions``, ConfigChange ``audit-config-change``):
those fire by **moment** (end of turn / restart / config change);
**this one fires by TOOL EVENT** (PostToolUse after a Write/Edit) and looks at
the **touched file**, not the session. It is the *automated* version of what the method does
manually in block **2b** of ``detection-and-smells.md`` — **the same criteria**
(VARIANT / TWO-HOMES / NO-HOME / NO-SIDECAR / NO-LABEL), applied to a single
recently-touched file instead of scanning the entire repo. It does not invent new smells.

Official contract (PostToolUse — code.claude.com/docs/en/hooks#posttooluse):

- **Fires AFTER the tool succeeds** (*"After a tool call
  succeeds"*); matcher = **tool name** (``"Edit|Write"``). The input JSON carries
  ``tool_name`` and ``tool_input.file_path`` (the written/edited file).
- **PROPOSES — NEVER blocks the edit.** *"PostToolUse hooks cannot undo actions
  since the tool has already executed"* and in the exit-codes table PostToolUse is
  **"Can block? No"**. We return the proposal via
  ``hookSpecificOutput.additionalContext`` (*"String added to Claude's context at
  the point where the hook fired… injected as a system reminder that Claude reads
  as plain text"*), with **exit 0**. We do **not** use ``decision: "block"`` — for
  PostToolUse it only *"ends the turn"* with a warning, without undoing the edit: the
  opposite of an optional suggestion about where the file should live.
- **Stdout does NOT become context in this event.** Unlike SessionStart/
  UserPromptSubmit, the stdout of PostToolUse goes to the debug log; that is why the
  proposal goes via ``additionalContext`` (JSON on stdout, exit 0), not as raw text.
- **Actionable error (dim 14).** Each proposal says **WHICH** home/slot is missing and **WHERE**
  to move/migrate (the exact canonical name), never a silent code — a
  well-written response guides the agent to the right fix.
- **Latency ceiling (~500 ms on the critical path).** Only inspects **one** path
  (string + one ``os.path.exists`` for the sidecar + the file head for the
  label); ``deadlineMs`` as a guard. PostToolUse runs on every Write/Edit: slow
  here = slow editing.

Pre-trust vector: hook config is **executable code** with shell privileges.
This script is **read-only** (reads the touched path and, at most, the head of the
file for the label; writes nothing) — version and review it like infra. Register the
``command`` in ``settings.json`` under the ``PostToolUse`` event with ``matcher:
"Write|Edit"`` (use ``settings.snippet.json``). Honors ``hooks-config.json``/
``hooks-config.local.json`` (block ``proposeDocsHome``): ``enabled: false`` exits
silently.

[docs-taxonomy.md]: ../references/docs-taxonomy.md
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TAG = "knowledge-management"

# Variant → canonical map (the SAME pairs from block 2b of detection-and-smells.md).
# Home in variant name ⇒ propose MIGRATION to canonical (deprecatable, with OK).
VARIANT_TO_CANON: dict[str, str] = {
    "arquitetura": "standards",
    "architecture": "standards",
    "patterns": "standards/architecture",
    "adr": "decisions",
    "catalogo_dados": "catalog",
    "dominio": "catalog",
    "domain": "catalog",
    "apresentacoes": "presentations",
    "diagramas": "presentations",
    "normativos": "reference/regulations",
    "comunicados": "communications",
    "comunicacao": "communications",
    "comunicacoes": "communications",
    "avisos": "communications",
}
# Legitimate canonical homes (do not trigger VARIANT/NO-HOME).
CANON_HOMES = frozenset(
    {
        "standards",
        "decisions",
        "vision",
        "backlog",
        "guides",
        "reference",
        "catalog",
        "communications",
        "presentations",
        "agents",  # consumption/domain doctrine (docs/agents/)
    }
)
# Slots where human binaries MAY live (= $SLOTS from 2b). Found outside here = out of home.
BINARY_SLOT_DIRS = ("presentations", "reference/regulations")
BINARY_EXTS = (".pdf", ".pptx", ".drawio", ".vsdx", ".png", ".svg")
# Slot binary whose content governs a decision ⇒ requires a .md sidecar.
SIDECAR_EXTS = (".pdf", ".pptx", ".drawio", ".vsdx")

DEFAULTS = {
    "enabled": True,
    "docsDir": "docs",        # root of the docs layer in the target (derivable)
    "maxHeadBytes": 2000,     # only the file head to check the label
    "deadlineMs": 200,        # ceiling < ~500 ms on the critical path
    "maxFindings": 3,         # do not flood the context
}


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
        cfg.update(data.get("proposeDocsHome") or {})
    return cfg


def _read_input() -> dict:
    try:
        return json.loads(sys.stdin.read() or "{}")
    except (OSError, json.JSONDecodeError):
        return {}


def _project_dir(data: dict) -> str:
    return os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()


def _rel_under_docs(file_path: str, root: str, docs_dir: str) -> str | None:
    """Path of the touched file relative to docs/ (None if it is outside docs/)."""
    if not file_path:
        return None
    abspath = file_path if os.path.isabs(file_path) else os.path.join(root, file_path)
    docs_root = os.path.normpath(os.path.join(root, docs_dir))
    norm = os.path.normpath(abspath)
    prefix = docs_root + os.sep
    if not norm.startswith(prefix):
        return None
    return os.path.relpath(norm, docs_root).replace(os.sep, "/")


def _has_label(abspath: str, max_head: int) -> bool:
    """Does the doc declare audience/authority in the frontmatter (file head)?"""
    try:
        with pathlib.Path(abspath).open("rb") as fh:
            head = fh.read(max_head).decode("utf-8", errors="ignore").lower()
    except OSError:
        return True  # could not read ⇒ do not flag (avoid false positive)
    return "audience:" in head or "authority:" in head


def _has_sidecar(abspath: str) -> bool:
    """Does the binary have a .md alongside (sidecar/extract) or an index that cites it?"""
    base, _ext = os.path.splitext(abspath)
    if pathlib.Path(base + ".md").exists():
        return True
    folder = os.path.dirname(abspath)
    target = os.path.basename(abspath)
    try:
        for entry in os.listdir(folder):
            if not entry.lower().endswith(".md"):
                continue
            try:
                with pathlib.Path(os.path.join(folder, entry)).open(
                    encoding="utf-8", errors="ignore"
                ) as fh:
                    if target in fh.read():
                        return True
            except OSError:
                continue
    except OSError:
        pass
    return False


def _findings(rel: str, abspath: str, root: str, docs_dir: str, cfg: dict) -> list[str]:
    """Applies the 2b criteria to the TOUCHED FILE. Returns actionable proposals."""
    out: list[str] = []
    parts = rel.split("/")
    top = parts[0] if len(parts) > 1 else ""  # 1st segment = home; no home = loose at root
    ext = os.path.splitext(rel)[1].lower()
    is_binary = ext in BINARY_EXTS
    in_slot = any(("/" + s + "/") in ("/" + rel) or rel.startswith(s + "/") for s in BINARY_SLOT_DIRS)
    docs_root = os.path.join(root, docs_dir)

    # VARIANT / TWO-HOMES — home in variant name when the canonical exists (or not).
    if top in VARIANT_TO_CANON:
        canon = VARIANT_TO_CANON[top]
        canon_top = canon.split("/")[0]
        if pathlib.Path(os.path.join(docs_root, canon_top)).exists():
            out.append(
                f"TWO-HOMES: '{docs_dir}/{top}/' coexists with the canonical home "
                f"'{docs_dir}/{canon}/' — migrate '{top}/' → '{canon}/' (do not duplicate; "
                "single-home), with OK."
            )
        else:
            out.append(
                f"VARIANT: '{docs_dir}/{top}/' is a variant name of the canonical home "
                f"'{docs_dir}/{canon}/' — propose migration to the canonical name "
                "(deprecatable, with OK; never rename without confirmation)."
            )

    # NO-HOME — technical markdown loose at the ROOT of docs/ (without a named home).
    if not top and ext == ".md" and os.path.basename(rel).lower() not in (
        "readme.md",
        "index.md",
        "indice.md",
    ):
        out.append(
            f"NO-HOME: '{docs_dir}/{rel}' is loose at the root of '{docs_dir}/' — "
            "move to a canonical home (standards/decisions/vision/backlog/guides/"
            "reference/catalog/communications/presentations) by function."
        )

    # NO-HOME (new subfolder) — 1st segment does not match any canonical/variant home.
    if top and top not in CANON_HOMES and top not in VARIANT_TO_CANON:
        out.append(
            f"NO-HOME: '{docs_dir}/{top}/' does not match any canonical home — it is a "
            "legitimate home to add to the taxonomy, or material in the wrong quadrant "
            "(reclassify into the right canonical home)."
        )

    # HUMAN/binary material outside a slot home (leaking into the technical layer/root).
    if is_binary and not in_slot:
        out.append(
            f"OUT-OF-HOME: binary '{docs_dir}/{rel}' is outside the binary slots — "
            "move to 'presentations/' (slides/diagrams) or 'reference/regulations/' "
            "(external regulations)."
        )

    # NO-SIDECAR — slot binary whose content governs a decision, with no .md alongside or index.
    if ext in SIDECAR_EXTS and in_slot and not _has_sidecar(abspath):
        out.append(
            f"NO-SIDECAR: '{docs_dir}/{rel}' has no '.md' extract alongside nor is cited "
            "in a folder index — create a sidecar (template templates/docs/sidecar.md, with "
            "'binary:' pointing to the source) so the LLM reads the extract, not the binary (~7x tokens)."
        )

    # NO-LABEL — .md doc under docs/ without audience/authority in the frontmatter.
    if ext == ".md" and os.path.basename(rel).lower() != "readme.md" and not _has_label(
        abspath, int(cfg.get("maxHeadBytes", DEFAULTS["maxHeadBytes"]))
    ):
        out.append(
            f"NO-LABEL: '{docs_dir}/{rel}' does not declare 'audience'/'authority' — "
            "add the frontmatter (template templates/docs/docs-front.md); the label can "
            "be in the home's README, but then the home needs to have it."
        )

    return out


def _emit(rel: str, docs_dir: str, findings: list[str], cap: int) -> None:
    """Returns the PROPOSAL via additionalContext (does not block; exit 0)."""
    lines = [
        f"[{TAG}] docs/ coverage: the recently-touched file '{docs_dir}/{rel}' may "
        "not fit the canonical taxonomy. PROPOSAL (not mandatory) — adjust "
        "while it is fresh:",
    ]
    for item in findings[:cap]:
        lines.append(f"  - {item}")
    lines.append(
        "If confirmed, move/migrate with confirmation (deprecation doctrine: never "
        "rename/delete without OK). Ignore if it is noise."
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
    docs_dir = cfg.get("docsDir") or DEFAULTS["docsDir"]
    rel = _rel_under_docs(file_path, root, docs_dir)
    if rel is None:  # file outside docs/ → silence
        return 0
    if time.monotonic() - started > deadline:
        return 0

    abspath = file_path if os.path.isabs(file_path) else os.path.join(root, file_path)
    findings = _findings(rel, abspath, root, docs_dir, cfg)
    if findings:
        _emit(rel, docs_dir, findings, int(cfg.get("maxFindings", DEFAULTS["maxFindings"])))
    return 0  # ALWAYS exit 0 — PROPOSES, never blocks (PostToolUse cannot undo the edit)


if __name__ == "__main__":
    sys.exit(main())
