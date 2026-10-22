#!/usr/bin/env python3
"""Exercise a real Codex marketplace upgrade in an isolated home, without model calls."""
from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins/quenching/assets/bin"))
from quenching.common.modules import distribution_findings, load_manifest  # noqa: E402


def run(argv: list[str], cwd: Path, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise ValueError(f"{' '.join(argv[:4])}: {(result.stderr or result.stdout).strip()}")
    return result.stdout


def check_upgrade(root: Path, baseline: str, codex: str) -> dict:
    manifest = load_manifest(root)
    findings = distribution_findings(root, manifest)
    if findings:
        raise ValueError("; ".join(findings))
    packages = [d for d in manifest.get("distributions", []) if d["platform"] == "codex"]
    if len(packages) != 1:
        raise ValueError("the upgrade check requires exactly one declared Codex distribution")
    package = packages[0]
    catalog_rel, package_rel = package["marketplace"], package["path"]
    current = root / package_rel
    version = (current / "VERSION").read_text().strip()
    scratch = root / ".quenching"
    scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="codex-upgrade-", dir=scratch) as temporary:
        work = Path(temporary)
        source = work / "source"
        source.mkdir()
        archive = subprocess.run(
            ["git", "archive", baseline, catalog_rel, package_rel], cwd=root,
            capture_output=True, timeout=60, check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(source, filter="data")
        git = ["git", "-C", str(source)]
        run([*git, "init", "-q", "-b", "main"], work)
        for key, value in (("user.name", "Upgrade check"), ("user.email", "check@example.com"),
                           ("commit.gpgsign", "false"), ("core.hooksPath", "/dev/null")):
            run([*git, "config", key, value], work)

        def commit(message: str) -> None:
            run([*git, "add", "-A"], work)
            run([*git, "commit", "-qm", message], work)

        commit("Previously published Codex package")
        old_plugin = source / package_rel / package["pluginManifest"]
        old_version = json.loads(old_plugin.read_text())["version"]
        if old_version == version:
            raise ValueError("baseline must precede the candidate version")
        old_skill = (source / package_rel / "skills/quenching-git-cleanup/SKILL.md").read_bytes()
        home = work / "home"
        home.mkdir()
        workspace = work / "workspace"
        workspace.mkdir()
        run(["git", "init", "-q", workspace.as_posix()], work)
        # Codex uses its real Git refresh path. Git alone rewrites the reserved URL to the
        # disposable source repository; no server, credentials or user Git config is modified.
        url = "https://quenching-upgrade.invalid/marketplace.git"
        env = {**os.environ, "CODEX_HOME": str(home)}
        env.pop("PLUGIN_ROOT", None)
        env.pop("CODEX_PLUGIN_ROOT", None)
        index = int(env.get("GIT_CONFIG_COUNT", "0"))
        env.update({"GIT_CONFIG_COUNT": str(index + 1),
                    f"GIT_CONFIG_KEY_{index}": f"url.{source}.insteadOf",
                    f"GIT_CONFIG_VALUE_{index}": url})

        def host(*args: str) -> dict:
            return json.loads(run([codex, "plugin", *args, "--json"], workspace, env))

        added = host("marketplace", "add", url)
        marketplace = added["marketplaceName"]
        selector = package["name"] + "@" + marketplace
        installed = host("add", selector)
        if installed["version"] != old_version:
            raise ValueError("baseline installation did not resolve the old package")
        shutil.rmtree(source / package_rel)
        shutil.copytree(current, source / package_rel,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        shutil.copy2(root / catalog_rel, source / catalog_rel)
        commit("Candidate Codex package and marketplace")
        refreshed = host("marketplace", "upgrade", marketplace)
        if refreshed.get("errors") or not refreshed.get("upgradedRoots"):
            raise ValueError(f"marketplace refresh did not complete: {refreshed}")
        upgraded = host("add", selector)
        installed_path = Path(upgraded["installedPath"])
        if not installed_path.is_relative_to(home / "plugins/cache"):
            raise ValueError("host returned a package outside the isolated cache")
        if upgraded["version"] != version:
            raise ValueError(f"host kept {upgraded['version']}, expected {version}")
        for rel in (package["pluginManifest"], "VERSION", "scripts/cq",
                    "skills/quenching-git-cleanup/SKILL.md"):
            if (installed_path / rel).read_bytes() != (current / rel).read_bytes():
                raise ValueError(f"installed package differs from candidate: {rel}")
        if old_skill == (installed_path / "skills/quenching-git-cleanup/SKILL.md").read_bytes():
            raise ValueError("cleanup skill did not change from the baseline")
        skill = (installed_path / "skills/quenching-git-cleanup/SKILL.md").read_text()
        first_block = re.search(r"```bash\n(.*?)\n```", skill, re.S)
        if first_block is None:
            raise ValueError("installed cleanup skill has no executable block")
        # Exercise the skill's own resolver. --version changes no Git refs.
        invocation = first_block[1].replace("git stale --remote <remote> --json", "--version")
        skill_version = run(["bash", "-c", invocation], workspace, env).strip()
        if skill_version != version:
            raise ValueError(f"cleanup skill resolves cq {skill_version}, expected {version}")
        tool_version = run([sys.executable, str(installed_path / "scripts/cq"), "--version"],
                           workspace, env).strip()
        if tool_version != version:
            raise ValueError(f"installed cq reports {tool_version}, expected {version}")
        listed = host("list")
        matches = [p for p in listed["installed"] if p["pluginId"] == selector]
        if len(matches) != 1 or matches[0]["version"] != version or not matches[0]["enabled"]:
            raise ValueError(f"installed plugin is missing, stale or disabled: {matches}")
        return {"ok": True, "baseline": baseline, "oldVersion": old_version, "newVersion": version,
                "pluginId": selector, "codex": run([codex, "--version"], workspace, env).strip(),
                "checks": ["git marketplace refresh", "installed cleanup bytes", "skill cq resolution",
                           "bundled cq version"],
                "sessionLoad": "not measured; no model session was launched"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default="6.4.0")
    args = parser.parse_args()
    codex = shutil.which("codex")
    if codex is None:
        print("INCONCLUSIVE: codex is unavailable; marketplace upgrade was not measured", file=sys.stderr)
        return 2
    baseline = subprocess.run(["git", "rev-parse", "--verify", args.baseline + "^{commit}"],
                              cwd=ROOT, capture_output=True)
    if baseline.returncode:
        print(f"INCONCLUSIVE: baseline {args.baseline} is unavailable; fetch its tag", file=sys.stderr)
        return 2
    try:
        print(json.dumps(check_upgrade(ROOT, args.baseline, codex), indent=2))
    except (OSError, ValueError, KeyError, subprocess.SubprocessError, tarfile.TarError) as exc:
        print(f"FAILED: Codex marketplace upgrade: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
