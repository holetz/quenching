#!/usr/bin/env python3
"""Build the Zensical documentation site and serve it on loopback.

The site is always rebuilt before serving so that ``site/`` reflects the current
documentation sources.  Stop the server with Ctrl-C.
"""

from __future__ import annotations

import argparse
import http.server
import shlex
import shutil
import socketserver
import subprocess
import sys
from functools import partial
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
CHECKER = ROOT / "plugins" / "quenching" / "assets" / "checks" / "documentation-site-check.py"
CQ = ROOT / "plugins" / "quenching" / "assets" / "bin" / "cq"
HOST = "127.0.0.1"


class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Serve each preview request independently and stop cleanly with the process."""

    daemon_threads = True
    allow_reuse_address = True


def _command_label(command: list[str]) -> str:
    return shlex.join(command)


def _run(command: list[str]) -> int:
    print(f"+ {_command_label(command)}", flush=True)
    return subprocess.run(command, cwd=ROOT, check=False).returncode


def _build_commands() -> tuple[list[str] | None, list[str]]:
    """Return an optional environment sync and the command that builds the site."""
    uv = shutil.which("uv")
    if uv:
        return (
            [uv, "sync", "--locked"],
            [uv, "run", "zensical", "build", "--clean", "--strict"],
        )

    project_zensical = ROOT / ".venv" / "bin" / "zensical"
    if project_zensical.is_file():
        runner = str(project_zensical)
    else:
        runner = shutil.which("zensical")

    if runner:
        return None, [runner, "build", "--clean", "--strict"]
    return None, [sys.executable, "-m", "zensical", "build", "--clean", "--strict"]


def build_site() -> int:
    if not (ROOT / "zensical.toml").is_file():
        print(f"error: missing Zensical configuration: {ROOT / 'zensical.toml'}", file=sys.stderr)
        return 1
    if not CHECKER.is_file():
        print(f"error: missing documentation site checker: {CHECKER}", file=sys.stderr)
        return 1
    if not CQ.is_file():
        print(f"error: missing knowledge CLI: {CQ}", file=sys.stderr)
        return 1

    stage_command = [
        sys.executable,
        str(CQ),
        "knowledge",
        "site-source",
        "docs",
        "site-source",
        "--write",
    ]
    if _run(stage_command) != 0:
        return 1

    sync_command, build_command = _build_commands()
    if sync_command and _run(sync_command) != 0:
        return 1
    if _run(build_command) != 0:
        return 1

    # Keep this immediately after the build: a successful generator exit alone
    # does not prove that links, assets, pages, and the sitemap are usable.
    check_command = [
        sys.executable,
        str(CHECKER),
        str(SITE),
        "--local",
        "--remote-policy",
        "error",
        "--require-glossary",
        "--glossary-source",
        "docs/glossary.md",
        "--glossary-snippet",
        "docs/assets/glossary-abbreviations.txt",
        "--glossary-route",
        "glossary.md",
    ]
    return _run(check_command)


def _port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("port must be an integer") from error
    if not 0 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 0 and 65535")
    return port


def serve(port: int) -> int:
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(SITE))
    with ThreadingHTTPServer((HOST, port), handler) as server:
        allocated_port = server.server_address[1]
        print(f"Serving {SITE} at http://{HOST}:{allocated_port}/ (Ctrl-C to stop)", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nPreview stopped.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the Zensical site into site/ and serve it on 127.0.0.1."
    )
    parser.add_argument(
        "--port",
        type=_port,
        default=0,
        help="TCP port; 0 chooses a free port (default: 0)",
    )
    args = parser.parse_args()

    if build_site() != 0:
        return 1
    if not (SITE / "index.html").is_file():
        print(f"error: build completed without {SITE / 'index.html'}", file=sys.stderr)
        return 1
    return serve(args.port)


if __name__ == "__main__":
    raise SystemExit(main())
