"""The version lockstep's mechanical half — the version artifacts and the changelog
entry check, followed by the two-pass
bump that moves all of them or none.

Moved verbatim out of the pre-refactor specs script."""
from __future__ import annotations

import json
import os
import re

from quenching.common.io import read_text, write_text


# --------------------------------------------------------------------------- #
# release — the mechanical half of /docs/standards/ci-cd/versioning-release.md
# --------------------------------------------------------------------------- #
# Four artifacts, down from the seven the pre-refactor scripts carried: each of the
# four self-contained tools declared its own `VERSION` constant, and folding them into
# one package folded those four declarations into the single one `common/version.py`
# now carries — the package's every module imports it rather than repeating it. All
# four are relative to the REPO root, and this verb only makes sense run from the
# plugin's own checkout — a target repository that merely has this plugin installed
# carries none of them.
# The generated siblings (Codex, specs-reader) and EVERY marketplace entry move too: a
# "jsonall" artifact carries one `"version"` per plugin entry and each is rewritten.
RELEASE_ARTIFACTS = (
    ("plugins/quenching/VERSION", "plain"),
    ("plugins/quenching/.claude-plugin/plugin.json", "json"),
    ("plugins/quenching-codex/VERSION", "plain"),
    ("plugins/quenching-codex/.codex-plugin/plugin.json", "json"),
    ("plugins/quenching-specs-reader/VERSION", "plain"),
    ("plugins/quenching-specs-reader/.claude-plugin/plugin.json", "json"),
    (".claude-plugin/marketplace.json", "jsonall"),
    ("plugins/quenching/assets/bin/quenching/common/version.py", "py"),
)
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
_RELEASE_JSON_VERSION_RE = re.compile(r'("version"\s*:\s*")([^"]+)(")')
_RELEASE_PY_VERSION_RE = re.compile(r'^(VERSION\s*=\s*["\'])([^"\']+)(["\'])', re.M)
_CHANGELOG_ENTRY_RE = re.compile(r"^##\s+([^\s#]+)\s*$", re.MULTILINE)


def bump_release_artifacts(repo_root: str, new_version: str) -> dict:
    """Require a changelog entry, then move every artifact or change NOTHING.

    The changelog gate and the first pass only READ: every artifact's current version is
    collected before anything is written, so a lockstep that is ALREADY drifted — one
    artifact disagreeing with the rest — is refused outright rather than compounded with
    a fifth value. The second pass writes only once every artifact was read
    successfully and every one of them agreed."""
    changelog = read_text(os.path.join(repo_root, "CHANGELOG.md"))
    if changelog is None or new_version not in _CHANGELOG_ENTRY_RE.findall(changelog):
        return {"ok": False,
                "error": f"CHANGELOG.md has no release entry: ## {new_version}",
                "artifacts": []}
    reads: list[dict] = []
    for rel, kind in RELEASE_ARTIFACTS:
        path = os.path.join(repo_root, rel)
        text = read_text(path)
        if text is None:
            return {"ok": False, "error": f"missing or unreadable: {rel}", "artifacts": []}
        if kind == "plain":
            old = text.strip()
        else:
            pat = _RELEASE_PY_VERSION_RE if kind == "py" else _RELEASE_JSON_VERSION_RE
            found = [m.group(2) for m in pat.finditer(text)]
            if not found:
                return {"ok": False, "error": f"no version found in: {rel}", "artifacts": []}
            if kind == "jsonall":
                try:
                    entries = json.loads(text).get("plugins", [])
                except ValueError:
                    return {"ok": False, "error": f"not valid JSON: {rel}", "artifacts": []}
                if len(found) != len(entries):
                    return {"ok": False, "artifacts": [],
                            "error": f"{rel}: {len(entries)} plugin entries but "
                                     f"{len(found)} versions — an entry has no version"}
                if len(set(found)) > 1:
                    return {"ok": False, "artifacts": [],
                            "error": f"{rel}: plugin entries disagree: {', '.join(found)}"}
            old = found[0]
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
            pat = _RELEASE_PY_VERSION_RE if r["kind"] == "py" else _RELEASE_JSON_VERSION_RE
            # every plugin entry of the marketplace, never just the first
            new_text = pat.sub(rf"\g<1>{new_version}\g<3>", r["text"],
                               count=0 if r["kind"] == "jsonall" else 1)
        write_text(r["path"], new_text)
        artifacts.append({"path": r["rel"], "old": r["old"], "new": new_version})
    return {"ok": True, "oldVersion": old_version, "newVersion": new_version,
            "artifacts": artifacts, "error": None}
