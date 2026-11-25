"""The `shared.quota` block: what the `quenching-quota` OpenCode plugin reads, through
`cq config show --effective`, to colour and pace the subscription-quota band.

The defaults live here once, as data: the registry (`config/schema.py`) and the effective view
(`config/effective.py`) read them from this module, and the plugin keeps the same numbers as its
fallback for a session without `cq`. `intervalSeconds` never goes below `MIN_INTERVAL_SECONDS`:
the usage endpoint is asked at most once a minute."""
from __future__ import annotations

MIN_INTERVAL_SECONDS = 60

DEFAULTS = {
    "warnPercent": 70,
    "dangerPercent": 90,
    "intervalSeconds": 300,
    "showSonnet": True,
}
