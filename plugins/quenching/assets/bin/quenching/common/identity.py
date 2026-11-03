"""The identity allowlist: which emails may sign a commit in this repository.

`shared.gitIdentity.allowedEmails` in `.agents/quenching.json` is a non-empty list of exact
addresses or `fnmatch` patterns (`*@users.noreply.github.com`), matched case-insensitively. Absent,
nothing is judged; malformed, the caller fails closed (`AllowlistInvalid`), so a typo never turns
the check off in silence. A denylist cannot enumerate every address that must not appear; an
allowlist names the few that may.

The findings reuse the leak gate's `Finding`, labelled `email-not-allowed`, and — unlike a leak
excerpt — carry the email itself: the person refused needs to see which identity to fix.
"""
from __future__ import annotations

import subprocess
from fnmatch import fnmatchcase

from quenching.common.config import load_config, namespace
from quenching.common.leak import Finding, _commits_to_push, _git

KEY = "shared.gitIdentity.allowedEmails"
LABEL = "email-not-allowed"
STAGED_REMEDY = "set an allowed identity: git config user.email <an allowed address>"
PUSH_REMEDY = ("re-sign the commit: git commit --amend --reset-author (or rebase the older "
               "commits) with an allowed user.email")


class AllowlistInvalid(Exception):
    """The declaration exists but is not a non-empty list of non-blank strings."""

    def __init__(self, value: object) -> None:
        super().__init__(f"{KEY} must be a non-empty list of email addresses or patterns; "
                         f"found {value!r}")
        self.value = value


def load_allowlist(root: str) -> list[str] | None:
    """The declared patterns, or `None` when the repository declares none."""
    block = namespace(load_config(root, detect_provider_info=False), "shared").get("gitIdentity")
    if block is None:
        return None
    if not isinstance(block, dict):
        raise AllowlistInvalid(block)
    if "allowedEmails" not in block:
        return None
    value = block["allowedEmails"]
    if (not isinstance(value, list) or not value
            or not all(isinstance(item, str) and item.strip() for item in value)):
        raise AllowlistInvalid(value)
    return [item.strip() for item in value]


def allowed(email: str, patterns: list[str]) -> bool:
    address = email.strip().lower()
    return any(fnmatchcase(address, pattern.lower()) for pattern in patterns)


def _finding(where: str, email: str) -> Finding:
    return Finding(where, 1, LABEL, email)


def ident_email(raw: str) -> str:
    """The address inside a `Name <email> timestamp tz` ident line."""
    return raw.partition("<")[2].partition(">")[0]


def staged_findings(root: str, patterns: list[str]) -> list[Finding]:
    """The author and committer the next commit will carry, as git reports them to the hook."""
    findings: list[Finding] = []
    for var in ("GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT"):
        done = subprocess.run(["git", "var", var], cwd=root, capture_output=True, text=True)
        email = ident_email(done.stdout) if done.returncode == 0 else ""
        if email and not allowed(email, patterns):
            findings.append(_finding(f"git var {var}", email))
    return findings


def push_findings(root: str, hook_input: str, patterns: list[str],
                  remote: str | None = None) -> list[Finding]:
    """The author and committer of every commit the `pre-push` stdin lines publish."""
    findings: list[Finding] = []
    seen: set[str] = set()
    for line in hook_input.splitlines():
        fields = line.split()
        if len(fields) != 4:
            continue
        for sha in _commits_to_push(root, fields[1], fields[3], remote):
            if sha in seen:
                continue
            seen.add(sha)
            author, committer = _git(root, "show", "-s", "--format=%ae%n%ce", sha).splitlines()[:2]
            for role, email in (("author", author), ("committer", committer)):
                if not allowed(email, patterns):
                    findings.append(_finding(f"commit {sha[:12]} ({role})", email))
    return findings
