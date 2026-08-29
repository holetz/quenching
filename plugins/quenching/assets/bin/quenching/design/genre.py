"""Genre contracts and deterministic multi-medium rendering."""
from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from quenching.design.build import build_drift, compute_build, write_build
from quenching.design.markdown import parse_document_frontmatter, split_h2
from quenching.design.model import DesignError


SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FIELD_RE = re.compile(r"^- `([A-Za-z][A-Za-z0-9_-]*)` — (required|optional)\s*(.*)$")


def new_genre(root: Path, slug: str, name: str, register: str, media: list[str],
              fields: list[str], write: bool = True) -> dict[str, Any]:
    root = root.resolve()
    if not SLUG_RE.fullmatch(slug):
        raise DesignError("genre slug must be kebab-case")
    normalized_media = _media(media)
    parsed_fields = [_parse_field(field) for field in fields]
    if not parsed_fields:
        raise DesignError("a genre needs at least one declared field")
    targets = {f".design/genres/{slug}.md": _genre_document(slug, name, register, normalized_media, parsed_fields)}
    for medium in normalized_media:
        template_medium = "typst" if medium == "pdf" else medium
        if template_medium not in {"html", "typst"}:
            continue
        relative = f".design/media/{template_medium}/{slug}.{'html' if template_medium == 'html' else 'typ'}"
        if relative in targets:
            continue
        targets[relative] = _genre_template(name, template_medium, parsed_fields)
    collisions = sorted(relative for relative in targets if (root / relative).exists())
    if collisions:
        raise DesignError("genre would overwrite existing files: " + ", ".join(collisions))
    if write:
        for relative, content in targets.items():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")
    generated = write_build(compute_build(root)) if write else []
    return {"ok": True, "mode": "write" if write else "check", "files": sorted(targets),
            "generated": generated, "genre": slug, "media": normalized_media}


def render_genre(root: Path, slug: str, medium: str, data_path: Path,
                 output: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    medium = medium.lower()
    if medium not in {"html", "typst", "pdf"}:
        raise DesignError("medium must be html, typst, or pdf")
    result = compute_build(root)
    drift = build_drift(result)
    if drift:
        raise DesignError("generated design projections are stale; run `cq design build` before rendering")
    genre_path = root / ".design" / "genres" / f"{slug}.md"
    try:
        frontmatter, body = parse_document_frontmatter(genre_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DesignError(f"unknown genre: {slug}") from exc
    allowed = _media(frontmatter.get("media", "").split(","))
    if medium not in allowed:
        raise DesignError(f"genre {slug} does not declare medium {medium}")
    fields = _fields_from_body(body)
    data = _read_data(data_path)
    missing = sorted(name for name, required, _ in fields if required and not str(data.get(name) or "").strip())
    if missing:
        raise DesignError("render data is missing required fields: " + ", ".join(missing))
    template_medium = "typst" if medium == "pdf" else medium
    suffix = "html" if medium == "html" else ("pdf" if medium == "pdf" else "typ")
    template_suffix = "html" if template_medium == "html" else "typ"
    template_path = root / ".design" / "media" / template_medium / f"{slug}.{template_suffix}"
    try:
        template = template_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise DesignError(f"genre {slug} has no {template_medium} template") from exc
    target = (output if output and output.is_absolute() else root / output) if output else (
        root / ".design" / "build" / f"{slug}.{suffix}")
    target = target.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    rendered = _substitute(template, data, medium, target, root)
    if medium == "pdf":
        _compile_pdf(rendered, target, root)
    else:
        target.write_text(rendered, encoding="utf-8", newline="\n")
    return {"ok": True, "genre": slug, "medium": medium,
            "output": _relative(target, root), "fields": sorted(data)}


def _media(values: list[str]) -> list[str]:
    media = sorted({value.strip().lower() for value in values if value.strip()})
    unknown = sorted(set(media) - {"html", "typst", "pdf"})
    if unknown:
        raise DesignError("unsupported genre media: " + ", ".join(unknown))
    return media


def _parse_field(value: str) -> tuple[str, bool, str]:
    parts = value.split(":", 2)
    if len(parts) < 2 or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", parts[0]):
        raise DesignError(f"invalid field {value!r}; use name:required|optional[:description]")
    requirement = parts[1].lower()
    if requirement not in {"required", "optional"}:
        raise DesignError(f"invalid field {value!r}; requirement must be required or optional")
    return parts[0], requirement == "required", parts[2].strip() if len(parts) == 3 else ""


def _genre_document(slug: str, name: str, register: str, media: list[str],
                    fields: list[tuple[str, bool, str]]) -> str:
    lines = ["---", f"name: {json.dumps(name, ensure_ascii=False)}", f"slug: {json.dumps(slug)}",
             f"register: {json.dumps(register, ensure_ascii=False)}",
             f"media: {json.dumps(', '.join(media))}", "---", "", f"# {name}", "", "## Fields", ""]
    for field, required, description in fields:
        suffix = f" {description}" if description else ""
        lines.append(f"- `{field}` — {'required' if required else 'optional'}{suffix}")
    lines.extend(["", "## Composition", "", "Describe the stable composition this genre preserves across media.",
                  "", "## Guardrails", "", "- Cite `/.knowledge/standards/design/production.md`.",
                  "- Import generated medium tokens; never repeat a primitive value."])
    return "\n".join(lines).rstrip() + "\n"


def _genre_template(name: str, medium: str,
                    fields: list[tuple[str, bool, str]]) -> str:
    """Mint a template whose placeholders are exactly the genre's declared fields."""
    if medium == "html":
        title_field = "title" if any(field == "title" for field, _, _ in fields) else fields[0][0]
        blocks = []
        for field, _, description in fields:
            label = html.escape(description or field.replace("-", " ").replace("_", " ").title())
            if field == title_field:
                blocks.append(f"    <h1>{{{{field.{field}}}}}</h1>")
            elif field == "body":
                blocks.append(f"    <article aria-label={json.dumps(label)}>{{{{field.{field}}}}}</article>")
            else:
                blocks.append(
                    f"    <section class=\"field field-{html.escape(field)}\">"
                    f"<h2>{label}</h2><p>{{{{field.{field}}}}}</p></section>"
                )
        return "\n".join([
            "<!doctype html>", '<html lang="en">', "<head>", '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            f"  <title>{{{{field.{title_field}}}}}</title>", "  <style>{{tokens.css}}</style>",
            "  <style>",
            "    body { margin: 0; color: var(--design-colors-on-surface); background: var(--design-colors-surface); font-family: var(--design-typography-body-font-family); }",
            "    main { max-width: var(--design-layout-content-wide); margin: auto; padding: var(--design-spacing-xl) var(--design-spacing-lg); }",
            "    h1 { font-family: var(--design-typography-display-font-family); font-size: var(--design-typography-display-font-size); line-height: var(--design-typography-display-line-height); }",
            "    article, section { max-width: var(--design-layout-reading); line-height: var(--design-typography-body-line-height); }",
            "  </style>", "</head>", "<body>", f"  <main aria-label={json.dumps(name)}>",
            *blocks, "  </main>", "</body>", "</html>", "",
        ])
    lines = [
        '#import "{{tokens.typ}}": *',
        '#import "{{primitives.typ}}": eyebrow, rule, frame', "",
        "#set text(font: token-typography-body-font-family, size: token-typography-body-font-size, weight: token-typography-body-font-weight)",
        "#show heading.where(level: 1): it => text(size: token-typography-display-font-size, weight: token-typography-display-font-weight, it.body)",
        "", "#frame[",
    ]
    for index, (field, _, description) in enumerate(fields):
        label = description or field.replace("-", " ").replace("_", " ").title()
        if index == 0 or field == "title":
            lines.append(f"  = {{{{field.{field}}}}}")
        elif field == "body":
            lines.append(f"  {{{{field.{field}}}}}")
        else:
            lines.extend([f"  == {label}", f"  {{{{field.{field}}}}}"])
    lines.extend(["]", ""])
    return "\n".join(lines)


def _fields_from_body(body: str) -> list[tuple[str, bool, str]]:
    section = split_h2(body).get("Fields", "")
    fields = []
    for line in section.splitlines():
        match = FIELD_RE.match(line)
        if match:
            fields.append((match.group(1), match.group(2) == "required", match.group(3).strip()))
    if not fields:
        raise DesignError("genre contract declares no parseable fields")
    return fields


def _read_data(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DesignError(f"cannot read render data: {exc}") from exc
    if not isinstance(value, dict):
        raise DesignError("render data must be one JSON object")
    return value


def _substitute(template: str, data: dict[str, Any], medium: str, target: Path, root: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        if key == "tokens.css":
            return (root / ".design" / "build" / "tokens.css").read_text(encoding="utf-8")
        if key == "tokens.typ":
            return os.path.relpath(root / ".design" / "build" / "tokens.typ", target.parent).replace(os.sep, "/")
        if key == "primitives.typ":
            return os.path.relpath(root / ".design" / "media" / "typst" / "primitives.typ", target.parent).replace(os.sep, "/")
        if key.startswith("field."):
            name = key[6:]
            value = str(data.get(name, ""))
            if medium == "html":
                return _markdown_html(value) if name == "body" else html.escape(value)
            return _typst_escape(value)
        raise DesignError(f"template uses unknown placeholder {key!r}")
    rendered = re.sub(r"\{\{\s*([^{}]+?)\s*\}\}", replace, template)
    if "{{" in rendered or "}}" in rendered:
        raise DesignError("template retains an unresolved placeholder")
    return rendered.rstrip() + "\n"


def _markdown_html(value: str) -> str:
    blocks = []
    for paragraph in re.split(r"\n\s*\n", value.strip()):
        escaped = html.escape(paragraph.strip()).replace("\n", "<br>\n")
        if escaped:
            blocks.append(f"<p>{escaped}</p>")
    return "\n".join(blocks)


def _typst_escape(value: str) -> str:
    return re.sub(r"([\\#\[\]*_])", r"\\\1", value)


def _compile_pdf(source: str, target: Path, root: Path) -> None:
    compiler = shutil.which("typst")
    if not compiler:
        raise DesignError("PDF rendering requires `typst` on PATH; HTML and .typ rendering remain available")
    fd, temporary = tempfile.mkstemp(prefix=f".{target.stem}.", suffix=".typ", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(source)
        run = subprocess.run([compiler, "compile", temporary, str(target), "--root", str(root)],
                             capture_output=True, text=True)
        if run.returncode:
            raise DesignError(f"typst compile failed: {(run.stderr or run.stdout).strip()}")
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)
