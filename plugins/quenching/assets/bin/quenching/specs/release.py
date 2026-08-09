"""The version lockstep's mechanical half — the seven artifacts and the two-pass
bump that moves all of them or none.

Moved verbatim out of `specs.py`."""
from __future__ import annotations

import os
import re

from quenching.common.io import read_text, write_text


# --------------------------------------------------------------------------- #
# release — the mechanical half of /.docs/standards/ci-cd/versioning-release.md
# --------------------------------------------------------------------------- #
# Seven artifacts, not six: `session.py` sits outside the SIX-artifact lockstep that
# standard names (nothing installs a copy of it, so `drift` never compares it against
# one) but still carries a `VERSION` constant and is bumped WITH the six, at the same
# release, per that standard's own rule. All seven are relative to the REPO root, and
# this verb only makes sense run from the plugin's own checkout — a target repository
# that merely has this plugin installed carries none of them.
RELEASE_ARTIFACTS = (
    ("plugins/quenching/VERSION", "plain"),
    ("plugins/quenching/.claude-plugin/plugin.json", "json"),
    (".claude-plugin/marketplace.json", "json"),
    ("plugins/quenching/assets/hooks/okf-validate.py", "py"),
    ("plugins/quenching/assets/bin/specs.py", "py"),
    ("plugins/quenching/assets/bin/skills.py", "py"),
    ("plugins/quenching/assets/bin/session.py", "py"),
)
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
# The same shape `skills.py`'s own `VERSION_CONSTANT_RE` reads for `drift` — duplicated
# rather than imported, like every other cross-tool agreement in this codebase.
_RELEASE_JSON_VERSION_RE = re.compile(r'("version"\s*:\s*")([^"]+)(")')
_RELEASE_PY_VERSION_RE = re.compile(r'^(VERSION\s*=\s*["\'])([^"\']+)(["\'])', re.M)


def bump_release_artifacts(repo_root: str, new_version: str) -> dict:
    """Move all seven version-carrying artifacts to `new_version`, or change NOTHING.

    Two passes on purpose. The first only READS: every artifact's current version is
    collected before anything is written, so a lockstep that is ALREADY drifted — one
    artifact disagreeing with the rest — is refused outright rather than compounded with
    an eighth value. The second pass writes only once every artifact was read
    successfully and every one of them agreed."""
    reads: list[dict] = []
    for rel, kind in RELEASE_ARTIFACTS:
        path = os.path.join(repo_root, rel)
        text = read_text(path)
        if text is None:
            return {"ok": False, "error": f"missing or unreadable: {rel}", "artifacts": []}
        if kind == "plain":
            old = text.strip()
        else:
            pat = _RELEASE_JSON_VERSION_RE if kind == "json" else _RELEASE_PY_VERSION_RE
            m = pat.search(text)
            if not m:
                return {"ok": False, "error": f"no version found in: {rel}", "artifacts": []}
            old = m.group(2)
        reads.append({"rel": rel, "kind": kind, "path": path, "text": text, "old": old})

    disagreeing = sorted({r["old"] for r in reads})
    if len(disagreeing) > 1:
        detail = ", ".join(f"{r['rel']}={r['old']}" for r in reads)
        return {"ok": False,
                "error": f"the lockstep already disagrees before this release: {detail}",
                "artifacts": []}
    old_version = disagreeing[0]
    if old_version == new_version:
        return {"ok": False, "error": f"already at {new_version}", "artifacts": []}

    artifacts = []
    for r in reads:
        if r["kind"] == "plain":
            new_text = new_version + ("\n" if r["text"].endswith("\n") else "")
        else:
            pat = _RELEASE_JSON_VERSION_RE if r["kind"] == "json" else _RELEASE_PY_VERSION_RE
            new_text = pat.sub(rf"\g<1>{new_version}\g<3>", r["text"], count=1)
        write_text(r["path"], new_text)
        artifacts.append({"path": r["rel"], "old": r["old"], "new": new_version})
    return {"ok": True, "oldVersion": old_version, "newVersion": new_version,
            "artifacts": artifacts, "error": None}
