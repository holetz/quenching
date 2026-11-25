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

NOT_MEASURED = "não medido por esta build"
# Which task of the spec fills each section; a section not yet filled says so instead of guessing.
SECTION_TASK = {"deploy": "1.2", "mcp": "1.3", "skills": "1.4", "clients": "1.5",
                "harness": "1.6"}


class BenchRefusal(ValueError):
    """The bench cannot measure what was asked; exit 2 with a code and a reason."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code, self.message = code, message


def not_measured(section: str) -> dict:
    """A section `tasks 1.2..1.6` has not filled yet, honest about it and claiming no verdict."""
    return {"state": "not-measured", "reason": f"task {SECTION_TASK[section]}",
            "hypotheses": {}}


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
def measure_mcp(root: pathlib.Path) -> dict:
    return not_measured("mcp")


# --- 1.4 · hooks, permissions and skills ------------------------------------------------------
def measure_skills(root: pathlib.Path) -> dict:
    return not_measured("skills")


# --- 1.5 · agents, .github/, .vscode/ and the cost sources -------------------------------------
def measure_clients(root: pathlib.Path) -> dict:
    return not_measured("clients")


# --- 1.6 · the harness refusal ----------------------------------------------------------------
def measure_harness(root: pathlib.Path) -> dict:
    return not_measured("harness")


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
                     "observation": row.get("observation") or NOT_MEASURED,
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
