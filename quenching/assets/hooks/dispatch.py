"""The one process every quenching hook of an `(event, matcher)` pair runs in.

The deploy wires a single `.claude/settings.json` entry per pair and passes the body names as
arguments: `<python> -I -c "<load this file>" deny-claude-coauthor warn-git-add-all`. This file
reads stdin once, hands it to each body's `decide(raw) -> dict` in the order given, and prints one
combined answer, so a shell call pays one interpreter start however many hooks are declared.

Combining: the first `permissionDecision: deny` wins and every deny reason is kept; the
`systemMessage` of each body is joined with "; " and its `additionalContext` with " ". A body that
is not installed, has no `decide` or raises is skipped. Fails open: any error of its own prints
`{}`, and it always exits 0 — exit 2 is what Claude Code reads as a block.
"""
import importlib.util
import json
import os
import re
import sys

NAME = re.compile(r"[A-Za-z0-9_-]+")


def _decide(directory: str, name: str):
    """The body's `decide`, or None when it is not installed or has none."""
    if not NAME.fullmatch(name) or name == "dispatch":
        return None
    path = os.path.join(directory, name + ".py")
    if not os.path.isfile(path):
        return None
    spec = importlib.util.spec_from_file_location("quenching_hook_" + name.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "decide", None)


def combine(outputs: list[dict]) -> dict:
    messages, contexts, denies, specific = [], [], [], {}
    for out in outputs:
        if not isinstance(out, dict) or not out:
            continue
        if isinstance(out.get("systemMessage"), str):
            messages.append(out["systemMessage"])
        inner = out.get("hookSpecificOutput")
        if not isinstance(inner, dict):
            continue
        specific.setdefault("hookEventName", inner.get("hookEventName"))
        if inner.get("permissionDecision") == "deny":
            denies.append(inner.get("permissionDecisionReason") or "")
        if isinstance(inner.get("additionalContext"), str):
            contexts.append(inner["additionalContext"])
    if not (messages or contexts or denies):
        return {}
    result: dict = {}
    if messages:
        result["systemMessage"] = "; ".join(messages)
    if denies:
        specific["permissionDecision"] = "deny"
        specific["permissionDecisionReason"] = " ".join(reason for reason in denies if reason)
    if contexts:
        specific["additionalContext"] = " ".join(contexts)
    if denies or contexts:
        result["hookSpecificOutput"] = {key: value for key, value in specific.items()
                                        if value is not None}
    return result


def run(raw: str, names: list[str], directory: str) -> dict:
    outputs = []
    for name in names:
        try:
            decide = _decide(directory, name)
            if decide is not None:
                outputs.append(decide(raw))
        except Exception:
            continue
    return combine(outputs)


def main() -> None:
    try:
        out = run(sys.stdin.read(), sys.argv[1:], os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        out = {}
    print(json.dumps(out))
    sys.exit(0)


if __name__ == "__main__":
    main()
