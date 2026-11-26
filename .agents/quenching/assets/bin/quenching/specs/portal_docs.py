"""`GET /api/docs` — the Docs tab's read-only payload.

The tab is a single place to navigate from: the manual, the docs index, the configuration
standard and the site, plus the command catalog derived from the installed skills'
descriptions. It reads the target's disk and writes nothing; no file's content is served, only
whether each link's path exists and the skill descriptions the target already carries.
"""
from __future__ import annotations

import re
from pathlib import Path

LINKS = (
    ("manual", "Manual do produto", "quenching/README.md"),
    ("index", "Índice da documentação", "docs/index.md"),
    ("configuration", "Padrão de configuração", "docs/standards/workflows/plugin-configuration.md"),
)
SKILL_DIRS = (".claude/skills", ".agents/skills")
_SITE_URL = re.compile(r'^\s*site_url\s*=\s*"(https?://[^"\s]+)"', re.MULTILINE)
_FLOWS = re.compile(r"^Run one [\w-]+ flows?: ([^.:]+)\.")


def _flows(description: str) -> list[str]:
    """The flow names a `Run one X flow: a, b.` description opens with; empty when it does not."""
    match = _FLOWS.match(description)
    return [part.strip() for part in match.group(1).split(",") if part.strip()] if match else []


def _catalog(base: Path) -> list[dict]:
    from quenching.common.frontmatter import parse_frontmatter

    seen: dict[str, dict] = {}
    for rel in SKILL_DIRS:
        for skill in sorted((base / rel).glob("*/SKILL.md")):
            try:
                meta = parse_frontmatter(skill.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError):
                continue
            name = meta.get("name") if isinstance(meta.get("name"), str) else skill.parent.name
            description = meta.get("description")
            if name in seen or not isinstance(description, str):
                continue
            seen[name] = {"name": name, "flows": _flows(description), "description": description}
    return sorted(seen.values(), key=lambda row: row["name"])


def _site(base: Path) -> str | None:
    try:
        match = _SITE_URL.search((base / "zensical.toml").read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return None
    return match.group(1) if match else None


def docs_payload(root: str) -> tuple[int, dict]:
    """`(status, body)` for `GET /api/docs`."""
    base = Path(root)
    links = [{"id": ident, "label": label, "path": path, "exists": (base / path).is_file()}
             for ident, label, path in LINKS]
    return 200, {"ok": True, "target": root, "links": links, "site": _site(base),
                 "commands": _catalog(base)}
