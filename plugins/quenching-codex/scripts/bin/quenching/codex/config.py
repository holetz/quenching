"""The `shared.codex` block of `.claude/quenching.json`, with its defaults.

The block is optional: absent, every default holds and `crossReview` is `auto`. `"off"` is the
explicit opt-out. A value of the wrong shape falls back to its default and is named in
`warnings`, so a typo never silently changes the threshold a caller relies on.
"""
from __future__ import annotations

from quenching.common.config import load_config, namespace

DEFAULTS = {
    "crossReview": "auto",
    "maxUsedPercent": {"primary": 80, "secondary": 90},
    "timeoutSeconds": 900,
    "model": "gpt-6-astra",
}
CROSS_REVIEW = ("auto", "off")


def _percent(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 100


def load_settings(root: str) -> tuple[dict, list[str]]:
    """Return the effective settings and the warnings for every value that was ignored."""
    block = namespace(load_config(root, detect_provider_info=False), "shared").get("codex")
    settings = {**DEFAULTS, "maxUsedPercent": dict(DEFAULTS["maxUsedPercent"])}
    warnings: list[str] = []
    if block is None:
        return settings, warnings
    if not isinstance(block, dict):
        return settings, ["shared.codex is not an object; defaults apply"]

    if "crossReview" in block:
        if block["crossReview"] in CROSS_REVIEW:
            settings["crossReview"] = block["crossReview"]
        else:
            warnings.append("shared.codex.crossReview must be 'auto' or 'off'; 'auto' applies")
    ceilings = block.get("maxUsedPercent", {})
    if isinstance(ceilings, dict):
        for window in ("primary", "secondary"):
            if window not in ceilings:
                continue
            if _percent(ceilings[window]):
                settings["maxUsedPercent"][window] = ceilings[window]
            else:
                warnings.append(f"shared.codex.maxUsedPercent.{window} must be 0-100; "
                                f"{DEFAULTS['maxUsedPercent'][window]} applies")
    else:
        warnings.append("shared.codex.maxUsedPercent is not an object; defaults apply")
    if "timeoutSeconds" in block:
        value = block["timeoutSeconds"]
        if isinstance(value, int) and not isinstance(value, bool) and value > 0:
            settings["timeoutSeconds"] = value
        else:
            warnings.append("shared.codex.timeoutSeconds must be a positive integer; "
                            f"{DEFAULTS['timeoutSeconds']} applies")
    if "model" in block:
        if isinstance(block["model"], str) and block["model"].strip():
            settings["model"] = block["model"].strip()
        else:
            warnings.append(f"shared.codex.model must be a name; {DEFAULTS['model']} applies")
    return settings, warnings
