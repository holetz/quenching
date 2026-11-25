#!/usr/bin/env python3
"""`copilot_bench` — a bancada que mede o que um cliente recebe, e reporta; nunca corrige.

Uma linha por hipótese da abertura do épico 453: a capacidade que o cliente deveria ter, o
artefato que a carrega, o que este alvo de fato mostra, o método, o veredito e o membro do épico
cuja decisão depende dela.

* `confirmed` — o alvo entrega o que a hipótese afirma; o membro segue.
* `refuted` — o alvo desmente a hipótese; o membro cai ou é reescrito.
* `reformulated` — o artefato existe noutra forma; o escopo do membro muda.
* `unmeasured-live` — a metade estática está medida e o resto exige uma sessão real; o passo do
  protocolo que o mede vai na linha, e o veredito nunca é lido como passe.
* `blocked` — falta ambiente (uma máquina, um cliente); a linha nomeia o que falta.

Mede-se o artefato, nunca o cliente: cada linha nomeia uma capacidade e o caminho que a carrega.
A sonda lê um alvo já instalado (`--target`) ou instala um descartável com `cq deploy --write`
(`--deploy`) num diretório temporário — nunca escreve no checkout.

Os limiares ficam numa tabela única, com fonte e data, impressa junto da matriz: uma mudança de
cliente é uma linha da tabela, não uma varredura.
"""
from __future__ import annotations

import argparse
import atexit
import json
import os
import pathlib
import shutil
import subprocess
import time
import sys
import tempfile
from datetime import datetime

REPO = pathlib.Path(__file__).resolve().parent.parent
# The source payload, which carries `skills/`; the deployed copy (`.agents/quenching`) does not, so
# a disposable target installed from it would silently receive no skill at all.
SOURCE_CQ = REPO / "quenching" / "assets" / "bin" / "cq"

CONFIRMED = "confirmed"
REFUTED = "refuted"
REFORMULATED = "reformulated"
UNMEASURED = "unmeasured-live"
BLOCKED = "blocked"
VERDICTS = (CONFIRMED, REFUTED, REFORMULATED, UNMEASURED, BLOCKED)

# The limits a client imposes on what the deploy installs. Each row names the knob that shows it,
# so a change of client is one row here and never a sweep through the code.
THRESHOLDS = (
    {"name": "tools-per-request", "value": 128, "unit": "tools", "date": "2026-11-25",
     "source": "levantamento de 2026-11-25 (spec 452, ## Design)",
     "knob": "tools nativas, das extensões e do MCP contam na mesma requisição; o cliente agrupa "
             "em virtual tools (`github.copilot.chat.virtualTools.threshold`) acima do corte"},
    {"name": "skill-description", "value": 1024, "unit": "chars", "date": "2026-11-25",
     "source": "levantamento de 2026-11-25 (spec 452, ## Design)",
     "knob": "a `description` lida do `SKILL.md`; acima do corte o cliente trunca ou ignora"},
)

# H1..H13, na ordem do `## Problem` da 452, com o membro do épico que cada uma destrava.
HYPOTHESES = (
    {"id": "H1", "member": "455", "method": "static+live",
     "capability": "O cliente desduplica por nome as skills publicadas duas vezes",
     "artifact": ".agents/skills + .claude/skills",
     "protocol": "o seletor `/` do chat lista cada `quenching-*` uma vez ou duas"},
    {"id": "H2", "member": "456", "method": "static+live",
     "capability": "O harness descobre `.claude/agents/*.md` no formato Claude",
     "artifact": ".claude/agents",
     "protocol": "o painel de agentes/modos customizados do VS Code lista os cinco "
                 "`quenching-spec-*`"},
    {"id": "H3", "member": "454", "method": "static+live",
     "capability": "As ferramentas do servidor, somadas às nativas, passam do teto de 128",
     "artifact": ".mcp.json + tools/list",
     "protocol": "contador do tools picker, aviso de excesso e grupos de virtual tools"},
    {"id": "H4", "member": "462", "method": "static+live",
     "capability": "Os hooks de `.claude/settings.json` disparam no VS Code e no Copilot CLI, e o "
                   "timeout faz fail-open",
     "artifact": ".claude/settings.json",
     "protocol": "uma chamada de shell negada por `deny-claude-coauthor` e um hook lento que não "
                 "bloqueia a sessão"},
    {"id": "H5", "member": "465", "method": "live",
     "capability": "O Copilot acrescenta trailer de co-autoria ao commit",
     "artifact": "git commit",
     "protocol": "`git log -1 --format=%B` de um commit feito pelo agente"},
    {"id": "H6", "member": "457", "method": "static+live",
     "capability": "`chat.tools.terminal.autoApprove`, `search.exclude`, `chat.agent.maxRequests` "
                   "e o sandbox valem em `.vscode/settings.json`",
     "artifact": ".vscode/settings.json (JSONC)",
     "protocol": "um comando de terminal aprovado sem prompt sob a chave, e a busca sem os "
                 "diretórios excluídos"},
    {"id": "H7", "member": "458", "method": "live",
     "capability": "`New Worktree` produz um worktree que o fluxo adota sem cortar outro",
     "artifact": "git worktree list",
     "protocol": "New Worktree no VS Code e o `branch:` que `cq specs status` grava ali"},
    {"id": "H8", "member": "461", "method": "static+live",
     "capability": "O custo de uma sessão sai do session-state do CLI, do OpenTelemetry ou do "
                   "Agent Debug Logs",
     "artifact": "~/.copilot, OTel, Agent Debug Logs",
     "protocol": "um Agent Debug Log exportado e o `~/.copilot` de uma sessão real"},
    {"id": "H9", "member": "466", "method": "static+live",
     "capability": "Uma extensão ou plugin do VS Code serve o fluxo sem virar segunda superfície",
     "artifact": "~/.vscode/extensions + extensions.json",
     "protocol": "inventário e teste de cada candidata (status bar, MCP provider, `chatSkills`, "
                 "GitHub Pull Requests, gerenciador de worktree)"},
    {"id": "H10", "member": "455", "method": "static",
     "capability": "As descrições de skill cabem no corte de 1.024 caracteres e somam o orçamento "
                   "medido",
     "artifact": ".agents/skills/**/SKILL.md",
     "protocol": "o seletor `/` mostra a descrição longa truncada"},
    {"id": "H11", "member": "463", "method": "static+live",
     "capability": "As regras por caminho chegam ao cliente pelo caminho do arquivo",
     "artifact": ".claude/rules + .github/instructions",
     "protocol": "editar um arquivo casado por uma regra e vê-la no contexto"},
    {"id": "H12", "member": "459", "method": "static+live",
     "capability": "Os slots `../<repo>-slot-*` e o armazenamento irmão ficam acessíveis sem "
                   "prompt",
     "artifact": "worktrees + `external_directory`",
     "protocol": "rodar `cq` dentro do slot e ler o store irmão sem prompt"},
    {"id": "H13", "member": "452", "method": "static",
     "capability": "`cq deploy` recusa `--harness copilot` com `ct-deploy-harness` e aceita "
                   "claude, codex, opencode e none",
     "artifact": "deploy CLI",
     "protocol": "—"},
)

class BenchRefusal(ValueError):
    """The bench cannot measure what was asked; exit 2 with a code and a reason."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code, self.message = code, message


# --- 1.2 · the disposable target --------------------------------------------------------------
def deploy_target(modules: str) -> tuple[pathlib.Path, dict]:
    """Install the surface into a temporary directory and hand back the root and the deploy facts.

    The deploy runs the source payload (`quenching/assets/bin/cq`), which carries `skills/`: the
    installed copy would find neither its own skill source nor a target one and write none. The
    user's global OpenCode config stays out, as in `test_deploy`, so the target is the deploy's.
    """
    if not SOURCE_CQ.is_file():
        raise BenchRefusal("cb-source", f"o payload-fonte não existe: {SOURCE_CQ}")
    root = pathlib.Path(tempfile.mkdtemp(prefix="quenching-copilot-bench-"))
    atexit.register(shutil.rmtree, str(root), True)
    target = root / "target"
    target.mkdir()
    env = dict(os.environ, XDG_CONFIG_HOME=str(root / "xdg"), OPENCODE_CONFIG="")
    done = subprocess.run([sys.executable, str(SOURCE_CQ), "deploy", "--target", str(target),
                           "--modules", modules, "--write", "--json"],
                          capture_output=True, text=True, env=env, timeout=600)
    try:
        payload = json.loads(done.stdout or "{}")
    except ValueError:
        payload = {}
    if done.returncode != 0 or not payload.get("ok"):
        code = payload.get("code") or f"exit {done.returncode}"
        detail = payload.get("message") or (done.stderr.strip().splitlines() or [""])[-1]
        raise BenchRefusal("cb-deploy", f"o deploy descartável falhou: {code}: {detail}")
    return target, {"version": payload.get("version"),
                    "modules": payload.get("modules"),
                    "harnesses": payload.get("harnesses"),
                    "runtime": payload.get("runtime"),
                    "written": len(payload.get("changes") or [])}


# --- 1.3 · the MCP server ---------------------------------------------------------------------
def import_payload() -> None:
    """Make the installed payload importable, for the JSONC reader the deploy already owns."""
    payload = REPO / "quenching" / "assets" / "bin"
    if str(payload) not in sys.path:
        sys.path.insert(0, str(payload))


def read_mcp_entry(root: pathlib.Path) -> dict:
    """.mcp.json as the client reads it: the `quenching` entry, the other servers left named."""
    path = root / ".mcp.json"
    if not path.is_file():
        return {"state": "absent", "path": ".mcp.json"}
    try:
        import_payload()
        from quenching.deploy.mcpfiles import jsonc_loads
        document = jsonc_loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return {"state": "unreadable", "path": ".mcp.json", "reason": str(error)}
    servers = document.get("mcpServers") if isinstance(document, dict) else None
    if not isinstance(servers, dict) or "quenching" not in servers:
        return {"state": "absent", "path": ".mcp.json", "reason": "sem a entrada `quenching`",
                "servers": sorted(servers or {})}
    entry = servers["quenching"] if isinstance(servers["quenching"], dict) else {}
    return {"state": "present", "path": ".mcp.json", "servers": sorted(servers),
            "command": entry.get("command"), "args": list(entry.get("args") or [])}


def probe_server(root: pathlib.Path, command: str, args: list[str]) -> dict:
    """One stdio session: `initialize`, `initialized`, `tools/list`; what the client would pay."""
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                    "clientInfo": {"name": "copilot_bench", "version": "1"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    ]
    started = time.monotonic()
    try:
        done = subprocess.run([command, *args],
                              input="\n".join(json.dumps(message) for message in messages) + "\n",
                              cwd=root, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as error:
        return {"state": "failed", "reason": str(error)}
    seconds = round(time.monotonic() - started, 3)
    replies = {}
    for line in done.stdout.splitlines():
        try:
            message = json.loads(line)
        except ValueError:
            continue
        if isinstance(message, dict) and "id" in message:
            replies[message["id"]] = message
    listing = (replies.get(2) or {}).get("result") or {}
    tools = listing.get("tools")
    if not isinstance(tools, list):
        error = (replies.get(2) or {}).get("error") or done.stderr.strip()[-300:]
        return {"state": "failed", "reason": f"tools/list ausente: {error}", "seconds": seconds}
    by_pillar: dict[str, int] = {}
    for tool in tools:
        pillar = str(tool.get("name", "")).split("_", 1)[0]
        by_pillar[pillar] = by_pillar.get(pillar, 0) + 1
    largest = max(tools, key=lambda t: len(t.get("description") or ""), default={})
    info = ((replies.get(1) or {}).get("result") or {}).get("serverInfo") or {}
    return {"state": "ok", "seconds": seconds, "tools": len(tools),
            "byPillar": dict(sorted(by_pillar.items(), key=lambda kv: (-kv[1], kv[0]))),
            "schemaBytes": len(json.dumps(tools, ensure_ascii=False)),
            "descriptionChars": sum(len(tool.get("description") or "") for tool in tools),
            "largestDescription": {"tool": largest.get("name"),
                                   "chars": len(largest.get("description") or "")},
            "server": info}


def measure_mcp(root: pathlib.Path) -> dict:
    entry = read_mcp_entry(root)
    if entry["state"] != "present":
        return entry | {"hypotheses": {}}
    server = probe_server(root, str(entry["command"]), [str(arg) for arg in entry["args"]])
    section = {**entry, **server}
    if server["state"] != "ok":
        observation = (f"o servidor `quenching` não respondeu `tools/list` "
                       f"({server.get('reason')})")
        verdict = UNMEASURED
    else:
        limit = THRESHOLDS[0]["value"]
        pillars = ", ".join(f"{name} {count}" for name, count in server["byPillar"].items())
        observation = (f"{server['tools']} ferramentas ({pillars}), "
                       f"{server['schemaBytes']} bytes de definição, respondidas em "
                       f"{server['seconds']} s; o teto de {limit} é por requisição e inclui as "
                       f"nativas e as das extensões")
        verdict = UNMEASURED
    section["hypotheses"] = {"H3": {"observation": observation, "verdict": verdict}}
    return section


# --- 1.4 · hooks, permissions and skills ------------------------------------------------------
def frontmatter_fields(text: str) -> dict[str, str]:
    """The `key: value` fields of a `---` frontmatter, in the shapes this repo writes: a quoted
    scalar, a folded block (`>-`), or a literal block (`|`). No YAML dependency."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    fields: dict[str, str] = {}
    key, raw = None, []

    def settle() -> None:
        if key is None:
            return
        value = "\n".join(raw).strip()
        if value[:1] in (">", "|"):
            folded = value[0] == ">"
            body = value[1:].lstrip("-+").strip("\n").splitlines()
            lines = [line.strip() for line in body if line.strip()]
            fields[key] = (" " if folded else "\n").join(lines)
        elif value.startswith('"'):
            fields[key] = value[1:-1].replace('\\"', '"').replace("\\\\", "\\") \
                if value.endswith('"') else value[1:]
        else:
            fields[key] = value

    for line in text[3:end].splitlines():
        if line[:1].isspace() and key is not None:
            raw.append(line)
            continue
        settle()
        if ":" in line:
            key, _, rest = line.partition(":")
            key, raw = key.strip(), [rest]
        else:
            key, raw = None, []
    settle()
    return fields


def hook_entries(settings: dict) -> list[dict]:
    """One row per command hook: the pair it is grouped under, its bodies, timeout and charset."""
    entries = []
    hooks = settings.get("hooks") if isinstance(settings.get("hooks"), dict) else {}
    for event, groups in hooks.items():
        for group in groups if isinstance(groups, list) else []:
            inner = group.get("hooks") if isinstance(group, dict) else None
            matcher = group.get("matcher", "") if isinstance(group, dict) else ""
            for hook in inner if isinstance(inner, list) else []:
                if not isinstance(hook, dict) or hook.get("type") != "command":
                    continue
                command = str(hook.get("command") or "")
                marked = ".agents/quenching/assets/hooks/" in command
                body, bodies = "", []
                if marked and ' -I -c "' in command:
                    body, _, rest = command.partition(' -I -c "')[2].partition('"')
                    bodies = rest.split()
                entries.append({"event": event, "matcher": matcher, "marked": marked,
                                "bodies": bodies, "timeout": hook.get("timeout"),
                                # The deploy's rule: the `-c` code carries no `$`, no backtick and
                                # no double quote, so bash, PowerShell and cmd hand it over intact.
                                "expansive": sorted({char for char in '$`"' if char in body})})
    return entries


def measure_skills(root: pathlib.Path) -> dict:
    section: dict = {"hypotheses": {}}
    source = root / ".agents" / "skills"
    bridge = root / ".claude" / "skills"
    names = sorted(path.name for path in source.iterdir()
                   if (path / "SKILL.md").is_file()) if source.is_dir() else []
    bridged = sorted(path.name for path in bridge.iterdir()
                     if (path / "SKILL.md").is_file()) if bridge.is_dir() else []
    descriptions = []
    for name in names:
        fields = frontmatter_fields((source / name / "SKILL.md").read_text(encoding="utf-8"))
        descriptions.append({"skill": name, "chars": len(fields.get("description") or "")})
    cut = THRESHOLDS[1]["value"]
    changes: list = []
    if source.is_dir() and bridge.is_dir():
        try:
            import_payload()
            from quenching.components.commands.bridge import plan as bridge_plan
            changes = bridge_plan(root)["changes"]
        except (ImportError, OSError) as error:
            changes = [{"path": str(error), "change": "unverifiable"}]
    section |= {"state": "present" if source.is_dir() else "absent",
                "source": {"count": len(names), "names": names},
                "bridge": {"count": len(bridged), "names": bridged,
                           "changes": changes},
                "descriptions": {
                    "count": len(descriptions) * (2 if bridged else 1),
                    "perCopy": sum(item["chars"] for item in descriptions),
                    "total": sum(item["chars"] for item in descriptions) *
                             (2 if bridged else 1),
                    "largest": max(descriptions, key=lambda item: item["chars"], default=None),
                    "cut": cut,
                    "overCut": [item for item in descriptions if item["chars"] > cut]},
                "settings": {}}
    settings_path = root / ".claude" / "settings.json"
    settings: dict = {}
    if settings_path.is_file():
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except ValueError as error:
            settings = {"unreadable": str(error)}
    entries = hook_entries(settings)
    section["settings"] = {
        "state": "absent" if not settings_path.is_file() else ("unreadable" if "unreadable"
                                                               in settings else "present"),
        "hooks": entries,
        "enabledMcpjsonServers": settings.get("enabledMcpjsonServers") or [],
        "disabledMcpjsonServers": settings.get("disabledMcpjsonServers") or [],
        "attribution": settings.get("attribution") or {}}
    if section["state"] == "present":
        pairs = sorted({(entry["event"], entry["matcher"]) for entry in entries})
        expansive = [entry for entry in entries if entry["expansive"]]
        section["hypotheses"] = {
            "H1": {"verdict": UNMEASURED,
                   "observation": (f"{len(names)} skills em `.agents/skills` e {len(bridged)} em "
                                   f"`.claude/skills`; a ponte tem {len(changes)} divergência(s)"
                                   f"{'' if not changes else ': ' + ', '.join(change['path'] for change in changes[:5])}"
                                   f"; a desduplicação pelo cliente é live")},
            "H4": {"verdict": UNMEASURED,
                   "observation": (f"{len(entries)} entrada(s) de hook em {len(pairs)} par(es) "
                                   f"(event, matcher), "
                                   f"{sum(len(entry['bodies']) for entry in entries)} corpo(s) "
                                   f"declarado(s), timeout {max((entry['timeout'] or 0) for entry in entries) if entries else 0} s; "
                                   f"{'sem caractere expansível' if not expansive else str(len(expansive)) + ' com caractere expansível'}"
                                   f"; o disparo é live")},
            "H10": {"verdict": CONFIRMED if not section["descriptions"]["overCut"] else REFUTED,
                    "observation": (
                        f"{section['descriptions']['count']} descrições, "
                        f"{section['descriptions']['total']} caracteres somados "
                        f"({section['descriptions']['perCopy']} por cópia), a maior com "
                        f"{section['descriptions']['largest']['chars']} "
                        f"(`{section['descriptions']['largest']['skill']}`), "
                        f"{len(section['descriptions']['overCut'])} acima do corte de {cut}")}}
    return section


# --- 1.5 · agents, .github/, .vscode/ and the cost sources -------------------------------------
GITHUB_FORMATS = ("instructions", "agents", "copilot-setup-steps.yml")
VSCODE_KEYS = ("chat.tools.terminal.autoApprove", "search.exclude", "chat.agent.maxRequests")
# Every directory the editor ships under: stable, Insiders, and their remote servers. The client is
# a capability, never a name — a machine with Insiders alone still has to be measured.
EXTENSION_DIRS = (".vscode/extensions", ".vscode-insiders/extensions",
                  ".vscode-server/extensions", ".vscode-server-insiders/extensions")
LOG_DIRS = (("vscode-logs", ".config/Code/logs"),
            ("vscode-insiders-logs", ".config/Code - Insiders/logs"),
            ("vscode-server-logs", ".vscode-server/data/logs"),
            ("vscode-server-insiders-logs", ".vscode-server-insiders/data/logs"))


def home() -> pathlib.Path:
    """Read at call time, so a test can point it at a machine of its own."""
    return pathlib.Path.home()


def cost_sources(home_dir: pathlib.Path) -> list[dict]:
    """What a session's cost can be read from, and where the client puts it. A path that is not
    there is `absent`, never an error: most machines have some of them and no machine has all."""
    return [{"name": "copilot-cli-session-state", "path": home_dir / ".copilot" / "session-state"},
            {"name": "copilot-cli-session-store", "path": home_dir / ".copilot" / "session-store.db"},
            *({"name": name, "path": home_dir / path} for name, path in LOG_DIRS),
            {"name": "opentelemetry-env",
             "env": ("OTEL_EXPORTER_OTLP_ENDPOINT", "COPILOT_OTEL_ENABLED")}]


def markdown_files(folder: pathlib.Path) -> list[str]:
    if not folder.is_dir():
        return []
    return sorted(path.relative_to(folder).as_posix() for path in folder.rglob("*")
                  if path.is_file())


def agent_rows(folder: pathlib.Path) -> list[dict]:
    rows = []
    for path in sorted(folder.glob("*.md")) if folder.is_dir() else []:
        fields = frontmatter_fields(path.read_text(encoding="utf-8", errors="replace"))
        rows.append({"name": path.stem, "description": bool(fields.get("description")),
                     "tools": fields.get("tools") or fields.get("allowed-tools") or "",
                     "model": fields.get("model") or ""})
    return rows


def read_vscode(root: pathlib.Path) -> dict:
    path = root / ".vscode" / "settings.json"
    if not path.is_file():
        return {"state": "absent", "path": ".vscode/settings.json"}
    try:
        import_payload()
        from quenching.deploy.mcpfiles import jsonc_loads
        document = jsonc_loads(path.read_text(encoding="utf-8"))
    except (ImportError, OSError, ValueError) as error:
        return {"state": "unreadable", "path": ".vscode/settings.json", "reason": str(error)}
    document = document if isinstance(document, dict) else {}
    return {"state": "present", "path": ".vscode/settings.json",
            "keys": {key: key in document for key in VSCODE_KEYS},
            "sandbox": sorted(key for key in document if "sandbox" in key),
            "searchExclude": sorted((document.get("search.exclude") or {}).keys())
            if isinstance(document.get("search.exclude"), dict) else []}


def worktree_facts(root: pathlib.Path) -> dict:
    """The primary checkout, its slots and its sibling stores — asked of git, so a target that is
    itself a slot still reports the family it belongs to."""
    try:
        done = subprocess.run(["git", "-C", str(root), "rev-parse", "--path-format=absolute",
                               "--git-common-dir"], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError) as error:
        return {"state": "absent", "reason": str(error)}
    if done.returncode != 0:
        return {"state": "absent", "reason": "not a git checkout"}
    primary = pathlib.Path(done.stdout.strip()).parent
    parent, name = primary.parent, primary.name
    return {"state": "present", "primary": str(primary),
            "slots": sorted(path.name for path in parent.glob(f"{name}-slot-*") if path.is_dir()),
            "stores": sorted(path.name for path in parent.glob(f"{name}.*") if path.is_dir())}


def external_directory(root: pathlib.Path) -> dict:
    path = root / "opencode.json"
    if not path.is_file():
        return {"state": "absent", "path": "opencode.json"}
    try:
        import_payload()
        from quenching.deploy.mcpfiles import jsonc_loads
        document = jsonc_loads(path.read_text(encoding="utf-8"))
    except (ImportError, OSError, ValueError) as error:
        return {"state": "unreadable", "path": "opencode.json", "reason": str(error)}
    permission = document.get("permission") if isinstance(document, dict) else None
    directories = permission.get("external_directory") if isinstance(permission, dict) else None
    return {"state": "present", "path": "opencode.json",
            "patterns": sorted(directories or {})}


def access_facts(root: pathlib.Path) -> dict:
    """The out-of-tree access report, from the same source `cq doctor --access` reads."""
    try:
        import_payload()
        from quenching.common.access import report
        return report(str(root))
    except (ImportError, OSError, ValueError) as error:
        return {"state": "unreadable", "reason": str(error)}


def measure_clients(root: pathlib.Path) -> dict:
    github = root / ".github"
    agents = {"claude": agent_rows(root / ".claude" / "agents"),
              "opencode": agent_rows(root / ".opencode" / "agents"),
              "github": agent_rows(github / "agents"),
              "source": agent_rows(root / ".agents" / "quenching" / "agents")}
    formats = {name: (github / name).exists() for name in GITHUB_FORMATS}
    rules = {"claude": markdown_files(root / ".claude" / "rules"),
             "github": markdown_files(github / "instructions")}
    home_dir = home()
    costs = []
    for source in cost_sources(home_dir):
        if "path" in source:
            costs.append({"name": source["name"], "state": "present" if source["path"].exists()
                          else "absent", "path": str(source["path"])})
        else:
            found = {name: os.environ.get(name) for name in source["env"]
                     if os.environ.get(name)}
            costs.append({"name": source["name"], "state": "present" if found else "absent",
                          **({"env": found} if found else {})})
    bases = [base for base in (home_dir / path for path in EXTENSION_DIRS) if base.is_dir()]
    installed = sorted(path.name for base in bases for path in base.iterdir() if path.is_dir())
    worktrees = worktree_facts(root)
    external = external_directory(root)
    access = access_facts(root)
    section = {"state": "present",
               "agents": {name: {"count": len(rows), "rows": rows} for name, rows in agents.items()},
               "github": {"state": "present" if github.is_dir() else "absent",
                          "formats": formats},
               "vscode": read_vscode(root),
               "rules": {name: {"count": len(paths), "paths": paths}
                         for name, paths in rules.items()},
               "cost": costs,
               "worktrees": worktrees,
               "externalDirectory": external,
               "access": access,
               "extensions": {"state": "present" if installed else "absent",
                              "count": len(installed),
                              "installed": installed[:40]},
               "hypotheses": {}}
    claude = agents["claude"]
    missing = [name for name in GITHUB_FORMATS if not formats[name]]
    vscode = section["vscode"]
    slots = worktrees.get("slots") or []
    patterns = external.get("patterns") or []
    section["hypotheses"] = {
        "H2": {"verdict": UNMEASURED,
               "observation": (f"{len(claude)} agentes em `.claude/agents` e "
                               f"{len(agents['opencode'])} em `.opencode/agents`, "
                               f"{len(agents['github'])} em `.github/agents`; a descoberta pelo "
                               f"cliente é live")},
        "H6": {"verdict": UNMEASURED,
               "observation": (f"`.vscode/settings.json` {vscode['state']}"
                               f"{'' if vscode['state'] != 'present' else ': ' + ', '.join(key + (' presente' if present else ' ausente') for key, present in vscode['keys'].items())}"
                               f"; se cada chave vale no workspace é live")},
        "H7": {"verdict": UNMEASURED,
               "observation": (f"{len(slots)} slot(s) irmãos do checkout primário; o `New "
                               f"Worktree` do cliente e o `branch:` que ele grava são live")},
        "H8": {"verdict": UNMEASURED,
               "observation": "; ".join(f"{item['name']} {item['state']}" for item in costs)
                              + "; qual delas entrega o custo é live"},
        "H9": {"verdict": UNMEASURED,
               "observation": (f"{section['extensions']['count']} extensões instaladas nos "
                               f"diretórios do VS Code; nenhuma é recomendada por esta sonda"
                               if installed else
                               "nenhum diretório de extensões do VS Code nesta máquina; o "
                               "inventário é live")},
        "H11": {"verdict": UNMEASURED,
                "observation": (f"{len(rules['claude'])} regra(s) em `.claude/rules` e "
                                f"{len(rules['github'])} em `.github/instructions`"
                                f"{'' if not missing else '; `.github/` sem ' + ', '.join(missing)}"
                                f"; a entrega por caminho é live")},
        "H12": {"verdict": UNMEASURED,
                "observation": (f"{len(slots)} slot(s) e {len(worktrees.get('stores') or [])} "
                                f"store(s) irmãos do checkout primário; "
                                f"{len(patterns)} padrão(ões) em `external_directory`; "
                                f"{len((access.get('claude') or {}).get('rules') or [])} regra(s) "
                                f"em `.claude/settings.json`; "
                                f"`.vscode/settings.json` {(access.get('vscode') or {}).get('state')}; "
                                f"copilot CLI com "
                                f"{len((access.get('copilotCli') or {}).get('directories') or [])} "
                                f"diretório(s); o acesso sem prompt é live")}}
    return section


# --- 1.6 · the harness refusal ----------------------------------------------------------------
ACCEPTED_HARNESSES = ("claude", "codex", "opencode", "none")
REFUSAL_CODE = "ct-deploy-harness"


def run_deploy_check(target: pathlib.Path, harness: str) -> tuple[int, dict]:
    done = subprocess.run([sys.executable, str(SOURCE_CQ), "deploy", "--target", str(target),
                           "--modules", "core", "--harness", harness, "--check", "--json"],
                          capture_output=True, text=True, timeout=300)
    try:
        payload = json.loads(done.stdout or "{}")
    except ValueError:
        payload = {}
    return done.returncode, payload


def measure_harness(_root: pathlib.Path) -> dict:
    """Which harnesses the deploy accepts, and the refusal `--harness copilot` must keep."""
    scratch = pathlib.Path(tempfile.mkdtemp(prefix="quenching-copilot-bench-deploy-"))
    atexit.register(shutil.rmtree, str(scratch), True)
    accepted, wrongly_refused = {}, []
    for harness in ACCEPTED_HARNESSES:
        code, payload = run_deploy_check(scratch, harness)
        refused = payload.get("code") == REFUSAL_CODE
        accepted[harness] = {"exit": code, "refused": refused}
        if refused:
            wrongly_refused.append(harness)
    code, payload = run_deploy_check(scratch, "copilot")
    copilot = {"exit": code, "code": payload.get("code"), "message": payload.get("message")}
    refused = code == 2 and copilot["code"] == REFUSAL_CODE
    if refused and not wrongly_refused:
        verdict = CONFIRMED
    elif not refused:
        verdict = REFUTED
    else:
        verdict = REFORMULATED
    observation = (f"`--harness copilot` sai {code}"
                   f"{'' if not copilot['code'] else ' com ' + copilot['code']}; aceitos: "
                   + ", ".join(f"{name} (exit {accepted[name]['exit']})" for name in ACCEPTED_HARNESSES)
                   + ("" if not wrongly_refused else
                      f"; recusados por engano: {', '.join(wrongly_refused)}"))
    return {"state": "present", "accepted": accepted, "copilot": copilot,
            "hypotheses": {"H13": {"verdict": verdict, "observation": observation}}}


def measure_sections(root: pathlib.Path, deploy: dict | None = None) -> dict:
    return {"deploy": {"state": "ok" if deploy is not None else "target",
                       "target": str(root), **(deploy or {}), "hypotheses": {}},
            "mcp": measure_mcp(root),
            "skills": measure_skills(root),
            "clients": measure_clients(root),
            "harness": measure_harness(root)}


def matrix(sections: dict) -> list[dict]:
    """One row per hypothesis, in the spec's order; a section that fills it wins over the blank."""
    claimed: dict[str, dict] = {}
    for section in sections.values():
        for hidden, row in (section.get("hypotheses") or {}).items():
            claimed[hidden] = row
    rows = []
    for hypothesis in HYPOTHESES:
        row = claimed.get(hypothesis["id"]) or {}
        rows.append({**hypothesis,
                     "observation": row.get("observation") or f"live: {hypothesis['protocol']}",
                     "verdict": row.get("verdict") or UNMEASURED})
    return rows


def bench(root: pathlib.Path, mode: str, modules: str = "all",
          deploy: dict | None = None) -> dict:
    sections = measure_sections(root, deploy)
    return {"ok": True,
            "target": str(root),
            "mode": mode,
            "modules": modules,
            "measuredAt": datetime.now().astimezone().isoformat(timespec="seconds"),
            "thresholds": list(THRESHOLDS),
            "measurements": sections,
            "hypotheses": matrix(sections)}


def resolve_root(args: argparse.Namespace) -> tuple[pathlib.Path, str, dict | None]:
    if args.deploy:
        root, facts = deploy_target(args.modules)
        return root, "deploy", facts
    root = pathlib.Path(args.target).expanduser().resolve()
    if not root.is_dir():
        raise BenchRefusal("cb-target", f"`--target` não é um diretório: {args.target}")
    return root, "target", None


# --- rendering --------------------------------------------------------------------------------
COLUMNS = (("id", "H"), ("capability", "Capacidade"), ("artifact", "Artefato"),
           ("observation", "Observação"), ("method", "Método"), ("verdict", "Veredito"),
           ("member", "Membro"))


def cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip() or "—"


def markdown(payload: dict) -> str:
    """The matrix as the artifact carries it: one row per hypothesis, limits above, no prose."""
    lines = [f"**Alvo:** `{payload['target']}` — modo `{payload['mode']}` · "
             f"medido em {payload['measuredAt']}", "",
             "| Limite | Valor | Fonte | Data |", "|---|---|---|---|"]
    for limit in payload["thresholds"]:
        lines.append(f"| {cell(limit['name'])} | {limit['value']} {cell(limit['unit'])} | "
                     f"{cell(limit['source'])} | {cell(limit['date'])} |")
    lines += ["", "| " + " | ".join(title for _, title in COLUMNS) + " |",
              "|" + "---|" * len(COLUMNS)]
    for row in payload["hypotheses"]:
        lines.append("| " + " | ".join(cell(row[key]) for key, _ in COLUMNS) + " |")
    return "\n".join(lines) + "\n"


def human(payload: dict) -> str:
    lines = [f"alvo: {payload['target']}  modo: {payload['mode']}  "
             f"medido em: {payload['measuredAt']}", ""]
    width = max(len(row["id"]) for row in payload["hypotheses"])
    for row in payload["hypotheses"]:
        lines.append(f"{row['id']:<{width}}  {row['verdict']:<15}  "
                     f"membro {row['member']:<4}  {row['observation']}")
    return "\n".join(lines) + "\n"


def refuse(error: BenchRefusal, as_json: bool) -> int:
    if as_json:
        print(json.dumps({"ok": False, "code": error.code, "message": error.message},
                         ensure_ascii=False, indent=2))
    else:
        print(f"recusado: {error.message}", file=sys.stderr)
    return 2


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="copilot_bench.py",
        description="mede o que um cliente recebe de um alvo deployado, uma linha por hipótese; "
                    "reporta e nunca corrige")
    p.add_argument("--target", default=".", help="alvo já instalado a medir (padrão: o diretório "
                                                 "atual)")
    p.add_argument("--deploy", action="store_true",
                   help="instala um alvo descartável com `cq deploy --write` e mede esse alvo")
    p.add_argument("--modules", default="all",
                   help="módulos do deploy descartável: all, core ou lista (padrão: all)")
    out = p.add_mutually_exclusive_group()
    out.add_argument("--json", action="store_true", help="o payload completo, para a máquina")
    out.add_argument("--md", action="store_true", help="a matriz em Markdown, para o artefato")
    return p


def main(argv: list[str]) -> int:
    args = parser().parse_args(argv)
    try:
        root, mode, deploy = resolve_root(args)
    except BenchRefusal as error:
        return refuse(error, args.json)
    payload = bench(root, mode, args.modules, deploy)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif args.md:
        print(markdown(payload), end="")
    else:
        print(human(payload), end="")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
