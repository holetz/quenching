# Live preview & the strict-build gate

MkDocs ships a dev server that live-reloads on every save — this is how the reader
judges the storytelling in real time. This repo drives it through `uv` (pinned
toolchain) behind `make` targets.

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
- Every save to a `.md` triggers an instant rebuild + browser reload — keep it
  running while you author.
- Run it **in the background** and confirm it printed `Serving on
  http://127.0.0.1:8000` before reporting the URL. Don't block the session on it.

Custom host/port when 8000 is taken:
```bash
uv run mkdocs serve -a 127.0.0.1:8001
```

!!! warning "Restart after editing mkdocs.yml"
    The live server watches `docs/` and `mkdocs.yml`, but changes to
    **`mkdocs.yml`** (new extensions, `extra_css`/`extra_javascript`, Mermaid
    fence) are only fully applied on a **server restart**. After editing config,
    stop the process and re-serve so the preview reflects it.

## The definition of done: a green strict build
```bash
make docs-build          # uv run mkdocs build --strict → ./site
```

!!! warning "A live server locks `site/` — build to a throwaway dir"
    If `mkdocs serve` is running, it holds `./site` and a plain `build` collides.
    Validate to a disposable dir instead, then remove it:
    ```bash
    mkdocs build --strict --site-dir .mkdocs-check && rm -rf .mkdocs-check
    ```
    This is the server-safe validation the studio's phase 8 uses ([visual-qa.md](visual-qa.md)).

`--strict` turns every warning into a failure. It catches exactly the mistakes this
skill must not make:
- **dangling links** — a relative link to a page that moved or doesn't exist;
- **orphan pages** — a `.md` missing from `nav` (or vice-versa);
- **unknown extensions** — `=== "tab"` / ```mermaid without the extension enabled.

The full quality gate (not just the build) is [engagement-checklist.md](engagement-checklist.md).
A red strict build is never "done".

## Verify what actually rendered
After a build, confirm the effects landed in `site/` rather than trusting the log:
```bash
grep -oE '<title>[^<]*</title>' site/index.html | head -1   # page title detected?
grep -c 'class="mermaid"' site/method/*/index.html          # diagrams present?
grep -oE 'stylesheets/.*css|javascripts/.*js' site/index.html | sort -u
```

## Deploy (only when asked)
```bash
make docs-deploy         # mkdocs gh-deploy --force → gh-pages branch
```
CI also auto-deploys on push to `main` touching `docs/`, `mkdocs.yml`,
`pyproject.toml`, or `uv.lock`. Don't deploy by hand unless asked.

## Troubleshooting
| Symptom | Cause | Fix |
| --- | --- | --- |
| `Address already in use` | An old `mkdocs serve` still bound to 8000 | Kill it (`taskkill //F //PID <winpid>`), or serve on `-a 127.0.0.1:8001` |
| `make: command not found` | `make` not on PATH (common on Windows) | Call the underlying commands directly (`uv run mkdocs serve`) |
| `uv: command not found` | `uv` not installed | Install `uv`; the whole toolchain runs through it |
| Strict build fails on a link | Relative path wrong after a page moved | Fix the link; keep it relative to `docs/` |
| New page 404s in nav | Page not added to `mkdocs.yml` `nav:` | Add it; `navigation.indexes` needs an `index.md` per section |
| Emoji/tabs/Mermaid render literally | Extension not enabled, or config not reloaded | Enable it (see material-toolkit.md) and **restart** serve |

## Windows note
This repo runs on Windows; the Bash tool provides a POSIX shell for `make`-style
commands. If `make` isn't available, the underlying `uv run mkdocs …` commands are
identical to what the make targets run.
