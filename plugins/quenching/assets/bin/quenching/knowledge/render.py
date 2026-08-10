"""Two renderings of one finding list — the operator's report and the agent's proposal.

Moved verbatim out of `assets/hooks/okf-validate.py`, with ONE adjustment: `VERSION` is
imported from `quenching.common.version` rather than declared here.

`_split` is the severity partition every caller branches on, and it is why this pillar
never grew a refusal step: findings are errors or warnings, and the exit code
`quenching.common.output` names is `OK` or `FINDINGS` and nothing else.
"""
from __future__ import annotations

from quenching.common.version import VERSION
from quenching.knowledge.schema import TAG


def _split(findings):
    errors = [f for f in findings if f[0] == "ERROR"]
    warns = [f for f in findings if f[0] == "WARN"]
    return errors, warns


def _render_text(findings, bundle_root: str) -> str:
    errors, warns = _split(findings)
    lines = [f"OKF conformance — {bundle_root} (okf-validate v{VERSION})",
             f"  {len(errors)} error(s), {len(warns)} warning(s)"]
    for sev, rel, code, msg in errors + warns:
        lines.append(f"  [{sev:<5}] {rel}: {msg}  ({code})")
    if not findings:
        lines.append("  OK — bundle conforms.")
    return "\n".join(lines)


def _render_proposal(findings) -> str:
    errors, warns = _split(findings)
    shown = (errors + warns)[:20]
    body = "\n".join(f"  - [{sev}] {rel}: {msg}" for sev, rel, code, msg in shown)
    return (f"[{TAG}] OKF conformance findings ({len(errors)} error(s), {len(warns)} warning(s)):\n"
            f"{body}\n"
            "Fix with the `quenching-docs-align` / `quenching-docs-add` skill (stamp `type`, keep `index.md` a "
            "frontmatter-free listing).")
