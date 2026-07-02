# Live preview & the strict-build gate

MkDocs ships a dev server that live-reloads on every save — this is how the
reader judges the storytelling in real time. This repo drives it through `uv`
(pinned toolchain) behind `make` targets.

## Spin up the dev server
```bash
make docs-serve          # uv sync + uv run mkdocs serve → http://127.0.0.1:8000
```
Equivalent without make:
```bash
uv sync                  # first run only: builds .venv from uv.lock
uv run mkdocs serve      # serve with live reload
```
- Serves at **http://127.0.0.1:8000** by default. Hand this URL to the user.
- Every save to a `.md` or `mkdocs.yml` triggers an instant rebuild + browser
  reload — keep it running while you author.
- Run it **in the background** (it's a long-lived process) and confirm it
  printed `Serving on http://127.0.0.1:8000` before reporting the URL. Don't
  block the session waiting on it.

Custom host/port when 8000 is taken:
```bash
uv run mkdocs serve -a 127.0.0.1:8001
```

## The definition of done: a green strict build
```bash
make docs-build          # uv run mkdocs build --strict → ./site
```
`--strict` turns every warning into a failure. It catches exactly the mistakes
this skill must not make:
- **dangling links** — a relative link to a page that moved or doesn't exist,
- **orphan pages** — a `.md` in `docs/` missing from `nav` (or vice-versa),
- **unknown extensions** — using `=== "tab"` without `pymdownx.tabbed` enabled.

Read the output, fix each line, re-run until it's clean. A red strict build is
never "done".

## Deploy (only when asked)
```bash
make docs-deploy         # mkdocs gh-deploy --force → gh-pages branch
```
CI also auto-deploys on push to `main` touching `docs/`, `mkdocs.yml`,
`pyproject.toml`, or `uv.lock` (`.github/workflows/docs.yml`). Don't deploy by
hand unless the user explicitly asks.

## Troubleshooting
| Symptom | Cause | Fix |
| --- | --- | --- |
| `Address already in use` | An old `mkdocs serve` is still bound to 8000 | Kill it, or serve on `-a 127.0.0.1:8001` |
| `uv: command not found` | `uv` not installed | Install `uv` (see pyproject.toml note) — the whole toolchain runs through it |
| Strict build fails on a link | Relative path wrong after a page moved | Fix the link; keep links **relative** to `docs/` |
| A new page 404s in nav | Page not added to `mkdocs.yml` `nav:` | Add it; `navigation.indexes` needs an `index.md` per section |
| Emoji/tabs render literally | Extension not enabled | Add the extension (see material-toolkit.md) and restart serve |

## Windows note
This repo runs on Windows; the Bash tool provides a POSIX shell for `make`.
If `make` isn't available, call the underlying commands directly
(`uv run mkdocs serve`) — they're identical to what the make targets run.
