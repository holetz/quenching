"""`GET /api/settings` — the configuration tab's read-only payload.

The tab shows the SAME carrier `cq config schema --values` prints (`config.schema_payload`), so
the terminal, the OpenCode page and the portal never drift. It reads the registry and the
layers' effective values and writes nothing: the portal's POST surface does not know this route.
"""
from __future__ import annotations


def settings_payload(root: str, query: dict) -> tuple[int, dict]:
    """`(status, body)` for `GET /api/settings[?category=<id>&key=<prefix>]`."""
    from quenching.config import schema_payload  # lazy: only this route needs the config pillar

    category = (query.get("category") or [""])[0] or None
    prefix = (query.get("key") or [""])[0] or None
    payload, refusal = schema_payload(root, category, prefix, values=True)
    if refusal:
        return 404, {"ok": False, **refusal}
    return 200, payload
