"""One rendering of one finding list — the operator's report.

Moved verbatim out of the pre-refactor OKF validator script, with ONE adjustment: `VERSION` is
imported from `quenching.common.version` rather than declared here.

The agent's proposal rendering (`_render_proposal`, feeding a hook's `additionalContext`) was
retired along with the `hook` mode it served.

`_split` is the severity partition every caller branches on, and it is why this pillar
never grew a refusal step: findings are errors or warnings, and the exit code
`quenching.common.output` names is `OK` or `FINDINGS` and nothing else.
"""
from __future__ import annotations

from quenching.common.version import VERSION


def _split(findings):
    errors = [f for f in findings if f[0] == "ERROR"]
    warns = [f for f in findings if f[0] == "WARN"]
    return errors, warns


def _render_text(findings, bundle_root: str) -> str:
    errors, warns = _split(findings)
    # `cq knowledge`, not the pre-refactor validator's filename — see this pillar's `main`. This
    # header prints on EVERY text-mode validation, so it was the most-seen citation of a deleted
    # file anywhere in the product.
    lines = [f"OKF conformance — {bundle_root} (cq knowledge v{VERSION})",
             f"  {len(errors)} error(s), {len(warns)} warning(s)"]
    for sev, rel, code, msg in errors + warns:
        lines.append(f"  [{sev:<5}] {rel}: {msg}  ({code})")
    if not findings:
        lines.append("  OK — bundle conforms.")
    return "\n".join(lines)
