#!/usr/bin/env python3
"""Build the Quenching Portal design system: tokens.css and every component and screen preview.

The markup of a screen and of its components comes from the same fragments and the same sample
data, so a card on the board is the card in the catalogue. Standard library only.

    python3 design-system/build.py          # write tokens.css and components/*/preview.html
    python3 design-system/build.py --check  # write nothing; fail on drift or a broken contract

The checks are the design system's contract: every class used is defined, every var() resolves,
the stated colour pairs hold their floor in both themes, and no preview reaches outside itself.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, timedelta
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMPONENTS = ROOT / "components"

# ── icons: one authored 16px set, 1.5 stroke, round caps. Paths only, so app.js can draw them
#    with createElementNS and the CSP stays untouched. ─────────────────────────────────────────
ICONS = {
    "search": "M7 12A5 5 0 1 0 7 2a5 5 0 0 0 0 10Zm7 2-3.5-3.5",
    "theme": "M8 14A6 6 0 1 0 8 2a6 6 0 0 0 0 12Zm0-12v12M8 5h3.6M8 8h4.9M8 11h3.6",
    "help": "M8 14.5a6.5 6.5 0 1 0 0-13 6.5 6.5 0 0 0 0 13ZM6.1 6.2a2 2 0 1 1 2.9 1.8c-.6.3-1 .8-1 1.5M8 11.6v.1",
    "plus": "M8 3v10M3 8h10",
    "board": "M2.5 2.5h3v11h-3zM6.5 2.5h3v7h-3zM10.5 2.5h3v9h-3z",
    "list": "M3 13.5v-4h3v4M6.5 13.5v-11h3v11M10 13.5v-7h3v7",
    "human": "M8 13.5v-5L3.5 5.5M8 8.5l4.5-3M3.5 2.5v3h3M12.5 2.5v3h-3",
    "epics": "M8 2l6 3-6 3-6-3 6-3ZM2 8l6 3 6-3M2 11l6 3 6-3",
    "gantt": "M2.5 3.5h6M5.5 8h6M8.5 12.5h5",
    "sessions": "M2.5 3h11v10h-11zM5 6l2.5 2L5 10M8.5 10.5H11",
    "chat": "M2.5 3h11v8H7l-3 2.5V11H2.5z",
    "target": "M8 2v2M8 12v2M2 8h2M12 8h2M8 12.5a4.5 4.5 0 1 0 0-9 4.5 4.5 0 0 0 0 9Z",
    "send": "M8 13V3M4 7l4-4 4 4",
    "down": "m4 6 4 4 4-4",
    "right": "m6 4 4 4-4 4",
    "up": "m4 10 4-4 4 4",
    "x": "m4 4 8 8M12 4l-8 8",
    "filter": "M2.5 4h11M5 8h6M7 12h2",
    "copy": "M5.5 5.5h7v8h-7zM3.5 10.5v-8h7",
    "panel": "M2.5 3h11v10h-11zM9.5 3v10",
    "expand": "M9.5 2.5h4v4M13.5 2.5 9 7M6.5 13.5h-4v-4M2.5 13.5 7 9",
    "link": "M6.5 3.5h-3v9h9v-3M9 2.5h4.5V7M13.5 2.5 7.5 8.5",
    "check": "m3 8.5 3.2 3L13 4.5",
    "lock": "M4 7h8v6.5H4zM5.5 7V5a2.5 2.5 0 0 1 5 0v2",
    "alert": "M8 2.5 14.5 13.5h-13L8 2.5ZM8 6.5v3.2M8 11.8v.1",
    "pause": "M5.5 3.5v9M10.5 3.5v9",
    "play": "m5 3 8 5-8 5V3Z",
    "refresh": "M13 8a5 5 0 1 1-1.6-3.7M13 2v3h-3",
    "bell": "M4 11.5V7.2a4 4 0 0 1 8 0v4.3l1 1.2H3l1-1.2ZM6.6 14.5h2.8",
}


def ic(name: str, label: str = "") -> str:
    aria = f'role="img" aria-label="{e(label)}"' if label else 'aria-hidden="true"'
    return f'<svg class="i" viewBox="0 0 16 16" {aria}><path d="{ICONS[name]}"/></svg>'


# ── sample data: invented specs about this very project; nothing real from any store ───────────
STAGES = [
    ("captured", "capturada", "foi escrita e ainda não entrou na fila."),
    ("ready", "na fila", "foi escolhida para desenvolver; desenvolvida, espera aprovação humana."),
    ("approved", "aprovada", "foi aprovada por uma pessoa e pode ser executada."),
    ("executing", "em execução", "tem tarefa em andamento ou já concluída."),
    ("blocked", "bloqueada", "tem tarefa marcada como bloqueada; o motivo está na spec."),
    ("review", "em revisão", "foi executada e espera revisão ou merge."),
    ("archived", "arquivada", "saiu do trabalho ativo; o resultado está no registro."),
]
STAGE_PT = {k: v for k, v, _ in STAGES}


def spec(id_, title, stage, pri, cx, who, age, done=0, total=0, subject="Portal", **kw):
    return {"id": id_, "title": title, "stage": stage, "pri": pri, "cx": cx, "who": who, "age": age,
            "done": done, "total": total, "subject": subject, **kw}


SPECS = [
    spec(2148, "Exportar o board como CSV para a revisão do trimestre", "captured", 3, "média", None, "ontem"),
    spec(2147, "Mostrar o custo estimado de uma spec antes de aprovar, por modelo e por etapa, com o teto configurado no repositório", "captured", 2, "alta", None, "há 3 d", subject="Store"),
    spec(2146, "Agrupar o board por marco de entrega", "captured", 4, "média", None, "há 5 d"),
    spec(2144, "Avisar quando uma spec fica parada por mais de 14 dias", "captured", 3, "baixa", "rui", "há 9 d"),
    spec(2141, "Resumo semanal do store para quem não abre o portal", "captured", 4, "média", None, "há 12 d", subject="Store"),
    spec(2133, "Importar specs antigas do tracker sem perder o histórico", "captured", 3, "alta", None, "há 26 d", subject="Store"),
    spec(2145, "Aprovar em lote na fila de decisão, com uma confirmação só", "ready", 2, "média", "ana", "há 4 d", 0, 7, hot=True, summary="Aprovar as vinte filhas de um épico hoje pede vinte cliques e vinte confirmações."),
    spec(2143, "Filtro por responsável no Gantt", "ready", 3, "baixa", "rui", "há 6 d", 0, 4, hot=True, summary="Quem conduz várias frentes precisa ver só as barras de uma pessoa."),
    spec(2140, "Carregar o Gantt sem travar em stores com mais de 500 specs", "ready", 2, "alta", "ana", "há 11 d", 0, 9, hot=True, summary="O Gantt relê o schedule inteiro a cada troca de zoom, e a aba congela em stores grandes."),
    spec(2139, "Atalho para copiar o comando de execução com a worktree", "ready", 4, "baixa", None, "há 13 d", 0, 3, hot=True, summary="O comando copiado não leva a worktree, e o agente abre no checkout errado."),
    spec(2142, "Mostrar no board quantas specs entraram na fila nesta semana", "ready", 3, "baixa", None, "há 7 d"),
    spec(2136, "Documentar o teclado do portal no manual do plugin", "approved", 3, "baixa", "davi", "há 2 d", 0, 3, subject="Docs"),
    spec(2134, "Contrato de cores por etapa na documentação", "approved", 3, "média", None, "há 5 d", 0, 5, subject="Docs"),
    spec(2131, "Histórico de decisões no detalhe da spec", "approved", 2, "alta", "rui", "há 8 d", 0, 8),
    spec(2137, "Publicar as escritas pendentes a partir do shell 2.0", "executing", 1, "alta", "ana", "hoje", 5, 6, run=("continua", "verificado", "pass"), pr=True),
    spec(2127, "Experiência do portal 2.0: shell, board e visões ao vivo", "executing", 1, "muito alta", "ana", "há 16 d", 4, 11, run=("continua", "verificado", "pass"), pr=True),
    spec(2132, "Sincronizar o store com escrita local e ponto de envio", "executing", 2, "alta", "davi", "há 9 d", 7, 12, subject="Store", run=("feito", "sem verificador", "")),
    spec(2129, "Reconciliar os cards do tracker com a etapa derivada", "executing", 2, "média", "rui", "há 10 d", 2, 9, subject="Store", tags=("tracker",), run=("falhou", "reprovado", "bad")),
    spec(2128, "Um servidor por máquina para vários projetos", "executing", 3, "média", "davi", "há 14 d", 9, 11),
    spec(2119, "Assinar as releases do plugin com a chave do CI", "blocked", 2, "média", "davi", "há 24 d", 3, 7, subject="Release", why="3.2: a chave de assinatura ainda não existe no cofre do CI."),
    spec(2112, "Migrar o manifesto do deploy para o formato 2", "blocked", 2, "alta", "rui", "há 38 d", 4, 10, subject="Release", why="5.1: depende da decisão sobre arquivos sem dono no alvo. 5.2: espera a 5.1."),
    spec(2125, "A release redeploya a própria superfície", "review", 2, "média", "ana", "ontem", 6, 6, subject="Release", run=("feito", "verificado", "pass"), pr=True),
    spec(2126, "O deploy --check compara o bit de execução", "review", 3, "baixa", "davi", "há 3 d", 4, 4, subject="Release", run=("feito", "verificado", "pass"), pr=True),
]
BY_ID = {s["id"]: s for s in SPECS}
TODAY = date(2026, 10, 31)
ME = "ana"
ME_EMAIL = "ana@exemplo.dev"
PEOPLE = {"ana": 1, "rui": 2, "davi": 3}
DUE = {2145: "2026-11-02", 2137: "2026-11-03", 2125: "2026-11-04", 2140: "2026-11-05", 2132: "2026-10-29",
       2131: "2026-11-10", 2127: "2026-11-12", 2126: "2026-11-16", 2129: "2026-11-20", 2136: "2026-11-24",
       2119: "2026-12-04"}
# An epic is made of features, a feature of user stories or tasks, a user story of tasks only.
KINDS = {2127: "epic", 2128: "feature", 2129: "feature", 2131: "feature", 2132: "feature", 2136: "feature",
         2137: "feature", 2140: "feature", 2119: "feature"}
PARTS = {"epic": "features concluídas", "feature": "itens concluídos"}
for s in SPECS:
    s["due"] = DUE.get(s["id"])
    s["kind"] = KINDS.get(s["id"])
ARCHIVED = 14
OPEN = len(SPECS)
TASKS_DONE = sum(s["done"] for s in SPECS if s["kind"] != "epic")
TASKS_ALL = sum(s["total"] for s in SPECS)
READY = [s for s in SPECS if s.get("hot")]
BLOCKED = [s for s in SPECS if s["stage"] == "blocked"]
EPIC_MEMBERS = 1
WAITING = len(READY) + len(BLOCKED) + EPIC_MEMBERS
NAV = [("board", "Board"), ("list", "Ranking"), ("human", "Decidir"), ("epics", "Épicos"),
       ("gantt", "Gantt"), ("sessions", "Sessões"), ("chat", "Chat")]


# ── fragments ──────────────────────────────────────────────────────────────────────────────────
def brand() -> str:
    return ('<h1 class="brand"><a href="#/board"><span class="mark" aria-hidden="true">Q</span> '
            'Quenching <span class="brand-sub">specs</span></a></h1>')


def nav(current="board", waiting=WAITING, sessions=1) -> str:
    links = []
    for key, label in NAV:
        cur = ' aria-current="page"' if key == current else ""
        badge = ""
        if key == "human":
            badge = f' <span class="count{" hot" if waiting else ""}" aria-label="esperando você">{waiting}</span>'
        if key == "sessions" and sessions:
            badge = f' <span class="count hot" aria-label="sessões esperando você">{sessions}</span>'
        links.append(f'<a href="#/{key}"{cur}>{ic(key)}{label}{badge}</a>')
    return f'<nav class="nav" aria-label="Visões">{"".join(links)}</nav>'


def topbar(current="board", capture=True, push=0, waiting=WAITING, sessions=1) -> str:
    send = (f'<button type="button" class="heat">{ic("send")} Enviar <span class="count hot" '
            f'aria-label="specs com escritas locais">{push}</span></button>') if push else ""
    dis = "" if capture else ' disabled title="O portal está em somente leitura."'
    return f"""<header class="top">{brand()}{nav(current, waiting, sessions)}
<div class="top-actions">
<button type="button" class="searchbtn" aria-haspopup="dialog">{ic("search")}<span class="searchbtn-label">Buscar ou executar</span> <kbd>Ctrl K</kbd></button>
<button type="button" class="ghost icon theme" aria-label="Tema: automático" title="Tema (t)">{ic("theme")}</button>
<button type="button" class="ghost icon helpbtn" aria-label="Ajuda e atalhos" title="Ajuda e atalhos (?)" aria-haspopup="dialog">{ic("help")}</button>
{send}<button type="button" class="primary"{dis}>{ic("plus")} Capturar</button>
<span class="me" tabindex="0" data-tip="Você: {ME_EMAIL}, do git config user.email">{person(ME)}</span>
</div></header>"""


def work_days(target: date) -> int:
    """Working days from today to the target, Monday to Friday, negative when overdue."""
    step = 1 if target >= TODAY else -1
    days = [TODAY + timedelta(i * step) for i in range(1, abs((target - TODAY).days) + 1)]
    return step * sum(d.weekday() < 5 for d in days)


def br_date(d: date) -> str:
    return f'{d:%d/%m/%Y}, {("segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo")[d.weekday()]}'


def due_label(iso: str) -> tuple[str, str, str]:
    """Label, band class and the balloon's exact date for a target date."""
    target = date.fromisoformat(iso)
    n = work_days(target)
    unit = "dia útil" if abs(n) == 1 else "dias úteis"
    if n < 0:
        return f"\u2212{-n} du", " late", f"Alvo {br_date(target)} · {-n} {unit} de atraso"
    if target == TODAY:
        return "hoje", " soon", f"Alvo {br_date(target)} · hoje"
    label = f"{n} du" if n <= 10 else f"{n // 5} sem"
    return label, " soon" if n <= 3 else "", f"Alvo {br_date(target)} · {n} {unit}"


def pulse_spec(s: dict) -> str:
    return (f'<span class="pulse-spec"><span class="id">{s["id"]}</span> '
            f'<span class="pulse-title">{e(s["title"])}</span></span>')


def pulse(waiting=WAITING) -> str:
    oldest = BY_ID[2112]
    due_next = min((s for s in SPECS if s["due"] and s["due"] >= TODAY.isoformat()), key=lambda s: s["due"])
    next_label, _, next_tip = due_label(due_next["due"])
    cells = [
        ("#/human", str(waiting), "esperando você", "fila de decisão do humano", "hot" if waiting else ""),
        ("#/board?f=stage:blocked", str(len(BLOCKED)), "bloqueadas", "specs com tarefa bloqueada", "bad"),
        ("#/board?f=stage:executing", "5", "em execução", "specs na etapa em execução", ""),
        ("#/board", str(OPEN), "abertas", "specs em plans", ""),
        ("#/list", f"{TASKS_DONE}/{TASKS_ALL}", "tarefas", "tarefas concluídas nas specs abertas", ""),
        ("#/list", next_label, "próximo vencimento", f'{next_tip}: {due_next["title"]}', "", pulse_spec(due_next)),
        ("#/list", "há 38 d", "mais antiga", f'Aberta desde 23/09/2026: {oldest["title"]}', "", pulse_spec(oldest)),
    ]
    html = "".join(
        f'<a class="pulse-cell {c[4]}" href="{c[0]}" data-tip="{e(c[3])}"><strong class="pulse-value">{c[1]}</strong> '
        f'{e(c[2])}{c[5] if len(c) > 5 else ""}</a>' for c in cells)
    return f'<section class="pulse" aria-label="Pulso do repositório">{html}</section>'


def statusbar(state="live", fresh="atualizado há 3 s · 15:00", notes=2, stale=False) -> str:
    words = {"live": "ao vivo", "unstable": "instável", "offline": "offline"}
    cls = "fresh stale" if stale else "fresh"
    return f"""<footer class="statusbar">
<span class="conn-state {state}" role="status">{words[state]}</span>
<span class="{cls}">{e(fresh)}</span>
<button type="button" class="ghost icon small" aria-label="Pausar o auto-refresh" title="Pausar">{ic("pause")}</button>
<button type="button" class="ghost icon small" aria-label="Atualizar agora" title="Atualizar">{ic("refresh")}</button>
<span class="grow"></span>
<span class="hint">pressione <kbd>?</kbd> para atalhos</span>
<button type="button" class="ghost small" aria-label="Notificações">{ic("bell")} <span class="count">{notes}</span></button>
</footer>"""


def stage_mark(stage: str) -> str:
    return f'<span class="stage" data-stage="{stage}">{STAGE_PT[stage]}</span>'


def stage_chip(stage: str) -> str:
    return f'<span class="chip stage-{stage}">{STAGE_PT[stage]}</span>'


def person(who: str) -> str:
    return f'<span class="av" data-person="{PEOPLE[who]}" aria-hidden="true">{who[:2]}</span>'


PRI_WORD = {1: "crítica", 2: "alta", 3: "média", 4: "baixa"}


def pri_button(n: int) -> str:
    cls = f" p{n}" if n <= 2 else ""
    return (f'<button type="button" class="pri{cls}" popovertarget="m-pri" aria-label="Prioridade P{n}, mudar" '
            f'data-tip="Prioridade P{n} · {PRI_WORD[n]}">P{n}</button>')


def target_button(s: dict) -> str:
    if not s["due"]:
        return (f'<button type="button" class="target none" popovertarget="m-date" aria-label="Definir alvo">'
                f'{ic("target")}alvo</button>')
    label, band, tip = due_label(s["due"])
    return (f'<button type="button" class="target{band}" popovertarget="m-date" aria-label="{e(tip)}, mudar" '
            f'data-tip="{e(tip)}">{ic("target")}{label}</button>')


def owner_button(s: dict) -> str:
    if not s["who"]:
        return '<button type="button" class="ghost small" popovertarget="m-who">Atribuir</button>'
    return (f'<button type="button" class="who" popovertarget="m-who" aria-label="Responsável @{s["who"]}, mudar" '
            f'data-tip="Responsável: @{s["who"]}">{person(s["who"])}{s["who"]}</button>')


def age_tip(age: str) -> str:
    days = {"hoje": 0, "ontem": 1}.get(age)
    if days is None:
        days = int(re.search(r"\d+", age)[0])
    return f"Modificada em {br_date(TODAY - timedelta(days))}"


def menus() -> str:
    pris = "".join(f'<button type="button" class="ghost small" popovertarget="m-pri" popovertargetaction="hide">'
                   f'{pri(n)} {PRI_WORD[n]}</button>' for n in PRI_WORD)
    who = "".join(f'<button type="button" class="ghost small" popovertarget="m-who" popovertargetaction="hide">'
                  f'{person(p)} {p}{" (você)" if p == ME else ""}</button>' for p in PEOPLE)
    fields = "".join(f"<option>{f}</option>" for f in (
        "Etapa", "Prioridade", "Responsável", "Assunto", "Complexidade", "Tag", "Alvo", "Título", "Conteúdo"))
    return f"""<div id="m-pri" class="menu" popover aria-label="Prioridade">{pris}</div>
<div id="m-who" class="menu" popover aria-label="Responsável">{who}<button type="button" class="ghost small" popovertarget="m-who" popovertargetaction="hide">Remover responsável</button></div>
<div id="m-date" class="menu" popover aria-label="Alvo">
<label class="field">Alvo <input type="date" value="2026-11-03"></label>
<p class="field-hint">O prazo conta dias úteis, de segunda a sexta.</p>
<div class="chips"><button type="button" class="primary small" popovertarget="m-date" popovertargetaction="hide">Salvar</button>
<button type="button" class="ghost small" popovertarget="m-date" popovertargetaction="hide">Remover alvo</button></div></div>
<div id="m-filter" class="menu filter-menu" popover aria-label="Filtrar">
<label class="field">Qualquer palavra <input type="search" placeholder="Título, seções, tarefas, registros"></label>
<div class="filter-row"><select aria-label="Campo">{fields}</select><select aria-label="Condição"><option>contém</option><option>é</option><option>não é</option><option>vazio</option></select><input type="text" aria-label="Valor" placeholder="Valor"></div>
<div class="chips"><button type="button" class="ghost small">{ic("plus")} Condição</button><span class="grow"></span>
<button type="button" class="primary small" popovertarget="m-filter" popovertargetaction="hide">Aplicar</button></div></div>"""


def pri(n: int) -> str:
    cls = f" p{n}" if n <= 2 else ""
    return f'<span class="pri{cls}" title="prioridade P{n}">P{n}</span>'


def run_mark(s: dict) -> str:
    if not s.get("run"):
        return ""
    state, ver, tone = s["run"]
    icon = ic("check") if tone == "pass" else ic("alert") if tone == "bad" else ""
    return (f'<span class="run {tone}" title="último passo do runner: {state} · verificador: {ver}">'
            f"{icon}{state}, {ver}</span>")


def progress(s: dict) -> str:
    if not s["total"]:
        return ""
    pct = round(100 * s["done"] / s["total"])
    bad = " has-blocked" if s["stage"] == "blocked" else ""
    return (f'<span class="progress-num">{s["done"]}/{s["total"]}</span>'
            f'<span class="bar{bad}" role="img" aria-label="{s["done"]} de {s["total"]} {PARTS.get(s["kind"], "tarefas concluídas")}">'
            f'<i style="width:{pct}%"></i></span>')


def fresh(age: str) -> str:
    """The card's recency band: today and yesterday, up to 3 days, up to 7 days, then nothing."""
    days = {"hoje": 0, "ontem": 1}.get(age)
    if days is None:
        days = int(re.search(r"\d+", age)[0]) if age.endswith(" d") else 30
    band = 1 if days <= 1 else 2 if days <= 3 else 3 if days <= 7 else 0
    return f" fresh-{band}" if band else ""


KIND_PT = {"epic": "épico", "feature": "feature"}


def card(s: dict, *, cursor=False, show_stage=False, approve=True) -> str:
    cls = "card" + (" is-cursor" if cursor else "") + (" is-mine" if s["who"] == ME else "")
    kind = s["kind"]
    kind_attr = f' data-kind="{kind}"' if kind else ""
    kind_tag = f'<span class="tag">{KIND_PT[kind]}</span>' if kind else ""
    if approve:
        who = owner_button(s)
    elif s["who"]:
        who = f'<span class="who" data-tip="Responsável: @{s["who"]}">{person(s["who"])}{s["who"]}</span>'
    else:
        who = "sem responsável"
    tags = "".join(f" · #{t}" for t in s.get("tags", ()))
    pr = '<a class="pr" href="#">PR</a>' if s.get("pr") else ""
    stage = stage_mark(s["stage"]) if show_stage else ""
    signal = progress(s) if s["done"] or s["stage"] in ("executing", "blocked", "review") else ""
    sig = f'<div class="card-signal">{signal}</div>' if signal else ""
    run = f'<div class="card-signal">{run_mark(s)}</div>' if s.get("run") else ""
    why = f'<p class="card-why">{ic("alert")}<span>{e(s["why"])}</span></p>' if s.get("why") else ""
    btn = ""
    if approve and s.get("hot"):
        btn = '<button type="button" class="heat small approve">Aprovar</button>'
    elif approve and s["stage"] == "captured":
        btn = '<button type="button" class="small enqueue">Mover para a fila</button>'
    return f"""<article class="{cls}" data-spec="{s["id"]}"{kind_attr}>
<div class="card-top"><span class="id">{s["id"]}</span>{pri_button(s["pri"]) if approve else pri(s["pri"])}{target_button(s) if approve else ""}{stage}<span class="age{fresh(s["age"])}" data-tip="{age_tip(s["age"])}">{s["age"]}</span></div>
<a class="title" href="#/spec/{s["id"]}">{e(s["title"])}</a>
{sig}{run}{why}{btn}
<div class="card-foot">{who}{kind_tag}<span>{e(s["subject"])}{tags}</span>{pr}</div>
<div class="quick"><button type="button" class="ghost icon small" aria-label="Abrir a gaveta">{ic("panel")}</button><button type="button" class="ghost icon small" aria-label="Copiar o comando">{ic("copy")}</button></div>
</article>"""


def lane(stage: str, specs: list, *, cursor=None, approve=True) -> str:
    cards = "\n".join(card(s, cursor=s["id"] == cursor, approve=approve) for s in specs)
    body = cards or '<p class="col-empty">nada aqui</p>'
    return f"""<section class="col" data-stage="{stage}" aria-label="{STAGE_PT[stage]}">
<h2 class="col-head"><button type="button" class="col-toggle" aria-expanded="true"><span class="col-name">{STAGE_PT[stage].capitalize()}</span><span class="count">{len(specs)}</span></button></h2>
<div class="col-body">{body}</div></section>"""


def lane_collapsed(stage: str, n: int) -> str:
    return f"""<section class="col is-collapsed" data-stage="{stage}" aria-label="{STAGE_PT[stage]}">
<h2 class="col-head"><button type="button" class="col-toggle" aria-expanded="false"><span class="col-name">{STAGE_PT[stage].capitalize()}</span><span class="count">{n}</span></button></h2></section>"""


GROUPS = ("Etapa", "Prioridade", "Responsável", "Assunto", "Épico", "Feature", "Alvo", "Complexidade", "Tipo", "Tag")
SORTS = ("Ranking", "Alvo", "Prioridade", "Modificação", "Criação", "Título", "Progresso", "Responsável")
QUICK = ("minhas", "bloqueadas", "em execução", "sem responsável", "aguardando você")
EPIC_GROUPS = ("Nenhum", "Estado", "Prioridade", "Responsável", "Assunto", "Alvo")
EPIC_SORTS = ("Ranking", "Alvo", "Progresso", "Prioridade", "Modificação", "Criação", "Título")
EPIC_QUICK = ("meus", "bloqueados", "em andamento", "sem responsável", "aguardando você")


def options(items, current: str) -> str:
    return "".join(f'<option{" selected" if i == current else ""}>{i}</option>' for i in items)


def toolbar(*, group="Etapa", pressed=(), chips="", sort="Ranking", compact=False, groups=GROUPS, sorts=SORTS,
            quick_items=QUICK, label="Controles do board", board=True) -> str:
    quick = "".join(
        f'<button type="button" class="ghost small" aria-pressed="{"true" if q in pressed else "false"}">{q}</button>'
        for q in quick_items)
    extra = f'<div class="chips wide">{chips}</div>' if chips else ""
    on = " checked" if compact else ""
    checks = ('<label class="check wide"><input type="checkbox" id="show-epics" checked> épicos</label>'
              '<label class="check wide"><input type="checkbox" id="show-features" checked> features</label>'
              '<label class="check wide"><input type="checkbox"> ocultar vazias</label>') if board else ""
    return f"""<section class="board-tools" aria-label="{label}">
<label class="control">Agrupar <select>{options(groups, group)}</select></label>
<label class="control">Ordenar <select>{options(sorts, sort)}</select></label>
<button type="button" class="ghost small" popovertarget="m-filter">{ic("filter")} Filtros</button>
<span class="tools-sep wide"></span><div class="chips wide">{quick}</div>{extra}
<span class="grow"></span>
{checks}
<label class="check wide"><input type="checkbox" class="density"{on}> compacto</label>
<button type="button" class="ghost small wide">Visões {ic("down")}</button>
</section>"""


def board_lanes(cursor=2137, approve=True) -> str:
    lanes = [lane(k, [s for s in SPECS if s["stage"] == k], cursor=cursor, approve=approve)
             for k, _, _ in STAGES if k != "archived"]
    lanes.append(lane_collapsed("archived", ARCHIVED))
    return f'<div class="board">{"".join(lanes)}</div>'


def app(body: str, *, current="board", h=900, banner="", rail="", push=0, capture=True, status=None,
        main_cls="", overlay="", waiting=WAITING, sessions=1, pulse_html=None) -> str:
    cls = f' class="{main_cls}"' if main_cls else ""
    p = pulse_html if pulse_html is not None else pulse(waiting)
    return f"""<div class="app" style="--app-h:{h}px">
<a class="skip" href="#main">Ir para o conteúdo</a>
{topbar(current, capture, push, waiting, sessions)}
{p}
{banner or "<div></div>"}
<div class="shell">{rail}<main id="main"{cls}>{body}</main></div>
{status or statusbar()}
{overlay}{menus()}</div>"""


def rank_signal(s: dict) -> str:
    """What the row adds to the ranking: the blocker, else the last run, else the summary."""
    if s.get("why"):
        return f'<span class="rank-signal is-bad">{ic("alert")}<span>{e(s["why"])}</span></span>'
    if s.get("run"):
        return f'<span class="rank-signal">{run_mark(s)}</span>'
    if s.get("summary"):
        return f'<span class="rank-signal"><span>{e(s["summary"])}</span></span>'
    return ""


RELEASE = {**spec(2108, "Release autônoma do plugin", "executing", 2, "alta", "davi", "há 24 d", 6, 7, subject="Release",
                  why="S6 espera a 2119"), "due": None, "kind": "epic"}
RANK_TREE = [  # id, children in their own order, open
    (2127, (2137, 2132, 2129, 2131, 2140, 2128, 2136), True),
    (2145, (), False), (2108, (2119,), False), (2112, (), False), (2125, (), False), (2147, (), False),
    (2143, (), False), (2126, (), False),
]


def rank_row(s: dict, n: str, *, depth=0, kids=0, open_=False) -> str:
    sid = s["id"]
    cls = ("card rank-card" + (f" depth-{depth}" if depth else "") + (" is-cursor" if sid == 2140 else "")
           + (" is-mine" if s["who"] == ME else ""))
    kind = f'<span class="tag">{KIND_PT[s["kind"]]}</span>' if s["kind"] else ""
    tags = "".join(f" · #{t}" for t in s.get("tags", ()))
    pr = '<a class="pr" href="#">PR</a>' if s.get("pr") else ""
    act = '<button type="button" class="heat small">Aprovar</button>' if s.get("hot") else ""
    verb = "Recolher" if open_ else "Abrir"
    fold = (f'<button type="button" class="ghost icon small" aria-expanded="{str(open_).lower()}" aria-label="{verb} {kids} de {sid}">'
            f'{ic("down") if open_ else ic("right")}</button>') if kids else ""
    return f"""<li class="{cls}" draggable="true" data-spec="{sid}"{f' data-kind="{s["kind"]}"' if s["kind"] else ""}>
<div class="rank-order"><div class="grip"><button type="button" class="ghost icon small" aria-label="Mover {sid} para cima">{ic("up")}</button><button type="button" class="ghost icon small" aria-label="Mover {sid} para baixo">{ic("down")}</button></div><span class="rank-n num">{n}</span></div>
<div class="rank-main"><div class="rank-line">{fold}<span class="id">{sid}</span>{pri_button(s["pri"])}<a class="row-title" href="#/spec/{sid}">{e(s["title"])}</a>{kind}</div>
<div class="rank-line rank-sub"><span class="rank-ctx">{e(s["subject"])}{tags} · complexidade {s["cx"]}</span>{rank_signal(s)}{pr}</div></div>
<div class="rank-side">{stage_mark(s["stage"])}{target_button(s)}<span class="age{fresh(s["age"])}" data-tip="{age_tip(s["age"])}">{s["age"]}</span>
<div class="card-signal">{progress(s)}</div>{owner_button(s)}<span class="rank-act">{act}</span></div></li>"""


def rows_ranking() -> str:
    specs = {**BY_ID, 2108: RELEASE}
    placed = {k for _, kids, _ in RANK_TREE for k in kids} | {t[0] for t in RANK_TREE} | {2108}
    tree = RANK_TREE + [(s["id"], (), False) for s in SPECS if s["id"] not in placed]
    rows = []
    for i, (sid, kids, open_) in enumerate(tree, 1):
        rows.append(rank_row(specs[sid], str(i), kids=len(kids), open_=open_))
        if open_:
            rows += [rank_row(specs[k], f"{i}.{j}", depth=1) for j, k in enumerate(kids, 1)]
    return "\n".join(rows)


def rank_list() -> str:
    return f'<ol class="rank-list">{rows_ranking()}</ol>'


def triage(s: dict, why: str, *, bad=False, armed=False, cursor=False, kind="approve") -> str:
    cls = "triage" + (" is-armed" if armed else "") + (" is-cursor" if cursor else "")
    if armed:
        act = ('<button type="button" class="primary small">Confirmar aprovação</button>'
               '<button type="button" class="ghost small">Cancelar</button>')
    elif kind == "approve":
        act = ('<button type="button" class="ghost small">Abrir</button>'
               '<button type="button" class="heat small">Aprovar</button>')
    else:
        act = ('<button type="button" class="ghost small">Abrir</button>'
               '<button type="button" class="ghost small">Copiar comando</button>')
    why_cls = "why is-bad" if bad else "why"
    return f"""<li class="{cls}" data-spec="{s["id"]}">
<div class="triage-main"><span class="id">{s["id"]}</span><a href="#/spec/{s["id"]}">{e(s["title"])}</a></div>
<div class="triage-aside"><span class="age">{s["age"]}</span>{act}</div>
<p class="{why_cls}">{e(why)}</p></li>"""


def segmented(items, current=0) -> str:
    btns = "".join(
        f'<button type="button" class="ghost small" aria-pressed="{"true" if i == current else "false"}">{e(t)}</button>'
        for i, t in enumerate(items))
    return f'<div class="segmented" role="group">{btns}</div>'


def decide_body(armed=True) -> str:
    rows_ready = [
        triage(BY_ID[2140], "Isto grava “approved by: human” e não se desfaz." if armed else BY_ID[2140]["summary"], armed=armed, cursor=True),
        triage(BY_ID[2139], BY_ID[2139]["summary"]),
        triage(BY_ID[2143], BY_ID[2143]["summary"]),
        triage(BY_ID[2145], BY_ID[2145]["summary"]),
    ]
    rows_blocked = [triage(s, s["why"], bad=True, kind="open") for s in reversed(BLOCKED)]
    member = spec(2152, "Política de aprovação quando o épico cruza dois repositórios", "ready", 2, "alta", None, "há 7 d")
    rows_epic = [triage(member, "Feature do épico 2127 · S9 · esperando decisão do humano.", kind="open")]
    return f"""<div class="wrap">
<div class="view-head"><h2>Decidir</h2><span class="sub">{WAITING} decisões esperam por você</span><span class="grow"></span>
{segmented([f"Todas {WAITING}", f"Aprovar {len(READY)}", f"Desbloquear {len(BLOCKED)}", f"Épicos {EPIC_MEMBERS}"])}</div>
<div class="group-head"><h3>Na fila, aguardando aprovação</h3><p>Mais antigas primeiro. Aprovar grava um registro que não se desfaz.</p></div>
<ul class="triagelist">{"".join(rows_ready)}</ul>
<div class="group-head"><h3>Tarefas bloqueadas</h3><p>O motivo está na tarefa; a spec tem o resto.</p></div>
<ul class="triagelist">{"".join(rows_blocked)}</ul>
<div class="group-head"><h3>Features de épicos abertos</h3><p>Features marcadas como decisão do humano.</p></div>
<ul class="triagelist">{"".join(rows_epic)}</ul>
<p class="quiet-row"><kbd>j</kbd> <kbd>k</kbd> navegar · <kbd>Enter</kbd> abrir · <kbd>a</kbd> aprovar · <kbd>Esc</kbd> desarmar</p>
</div>"""


def wave_item(label, sid, title, stage, critical=False) -> str:
    cls = "wave-item" + (" critical" if critical else "")
    return (f'<li class="{cls}"><span class="label">{label}</span><a href="#/spec/{sid}">{e(title)}</a>'
            f'{stage_mark(stage)}</li>')


def epic_panel() -> str:
    w2 = "".join([
        wave_item("S4", 2128, "Um servidor por máquina para vários projetos", "executing"),
        wave_item("S5", 2132, "Sincronizar o store com escrita local e ponto de envio", "executing"),
        wave_item("S6", 2129, "Reconciliar os cards do tracker com a etapa derivada", "executing"),
    ])
    w3 = "".join([
        wave_item("S7", 2137, "Publicar as escritas pendentes a partir do shell 2.0", "executing", True),
        wave_item("S8", 2131, "Histórico de decisões no detalhe da spec", "approved"),
        wave_item("S9", 2152, "Política de aprovação quando o épico cruza dois repositórios", "ready", True),
    ])
    w4 = "".join([
        wave_item("S10", 2140, "Carregar o Gantt sem travar em stores com mais de 500 specs", "ready", True),
        wave_item("S11", 2136, "Documentar o teclado do portal no manual do plugin", "approved"),
    ])
    def wave(n, title, done, total, body, open_=True):
        chev = ic("down") if open_ else ic("right")
        ul = f"<ul>{body}</ul>" if open_ else ""
        cls = "wave" if open_ else "wave is-closed"
        return (f'<section class="{cls}"><h3><button type="button" class="wave-toggle" aria-expanded="{str(open_).lower()}">'
                f'<span>Onda {n} · {e(title)}</span><span class="wave-count"><span class="progress-num">{done}/{total}</span>{chev}</span></button></h3>{ul}</section>')
    meter = "".join(f'<span style="--n:{t}"><i style="width:{round(100*d/t)}%"></i></span>' for d, t in ((3, 3), (1, 3), (0, 3), (0, 2)))
    return f"""<section class="panel epic">
<div class="epic-head">
<h2 class="epic-title"><span class="id">2127</span> <a href="#/spec/2127">Portal 2.0: shell, board e visões ao vivo</a></h2>
<div class="epic-progress"><span>4 de 11 features · onda 2 de 4</span><div class="meter" role="img" aria-label="4 de 11 features concluídas, em 4 ondas">{meter}</div></div>
<div class="epic-meta"><span class="chip info" title="há feature em execução">em andamento</span><span>caminho crítico: S7 → S9 → S10</span></div>
</div>
<p class="next-step"><strong>Próximo passo:</strong> S7 · Publicar as escritas pendentes a partir do shell 2.0</p>
<div class="waves">{wave(1, "Fundação do shell", 3, 3, "", False)}{wave(2, "Dados e servidor", 1, 3, w2)}{wave(3, "Escrita e decisão", 0, 3, w3)}{wave(4, "Fechamento", 0, 2, w4)}</div>
</section>"""


def epic_closed() -> str:
    meter = "".join(f'<span style="--n:{t}"><i style="width:{round(100*d/t)}%"></i></span>' for d, t in ((4, 4), (2, 3)))
    return f"""<section class="panel epic">
<div class="epic-head">
<h2 class="epic-title"><span class="id">2108</span> <a href="#/spec/2108">Release autônoma do plugin</a></h2>
<div class="epic-progress"><span>6 de 7 features · onda 2 de 2</span><div class="meter" role="img" aria-label="6 de 7 features concluídas, em 2 ondas">{meter}</div></div>
<div class="epic-meta"><span class="chip warn" title="há feature com tarefa bloqueada">bloqueio</span><span>S6 espera a 2119</span></div>
</div>
<p class="next-step"><strong>Próximo passo:</strong> S6 espera 2119 · Assinar as releases do plugin com a chave do CI</p>
</section>"""


GANTT = [  # id, title, stage, start day, length, critical, slip
    (2127, "Experiência do portal 2.0", "executing", 0, 26, False, False),
    (2132, "Sincronizar o store", "executing", 6, 16, False, False),
    (2137, "Publicar as escritas pendentes", "executing", 13, 11, True, False),
    (2129, "Reconciliar os cards do tracker", "executing", 9, 20, False, True),
    (2131, "Histórico de decisões", "approved", 22, 12, False, False),
    (2140, "Carregar o Gantt sem travar", "ready", 24, 14, True, False),
    (2143, "Filtro por responsável no Gantt", "ready", 38, 7, True, False),
    (2136, "Documentar o teclado", "approved", 34, 6, False, False),
    (2119, "Assinar as releases", "blocked", 17, 24, False, True),
]


def gantt_svg(width=1376) -> str:
    left, rowh, head, scale = 280, 32, 30, (width - 280) / 49
    height = head + rowh * len(GANTT) + 8
    parts = [f'<svg class="gantt-svg" width="{width}" height="{height}" role="img" aria-label="Cronograma de {len(GANTT)} specs">']
    for week in range(8):
        x = left + week * 7 * scale
        parts.append(f'<line class="gantt-grid" x1="{x:.0f}" x2="{x:.0f}" y1="{head}" y2="{height}"/>')
        parts.append(f'<text class="gantt-tick" x="{x + 4:.0f}" y="19">{5 + 7 * week if week < 4 else 5 + 7 * week - 30:02d}/{10 if week < 4 else 11}</text>')
    pos = {}
    for i, (sid, title, stage, start, length, crit, slip) in enumerate(GANTT):
        y = head + i * rowh
        x, w = left + start * scale, length * scale
        pos[sid] = (x, y + 15, x + w)
        cls = f"gantt-rect st-{stage}" + (" critical" if crit else "") + (" slip" if slip else "")
        parts.append(f'<text class="gantt-label" x="12" y="{y + 20}">{sid}</text><text x="60" y="{y + 20}">{e(title)}</text>')
        parts.append(f'<a href="#/spec/{sid}" aria-label="{sid}: {e(title)}"><rect class="{cls}" x="{x:.1f}" y="{y + 7}" width="{w:.1f}" height="18" rx="3"/></a>')
    for a, b, crit in ((2137, 2140, True), (2140, 2143, True), (2132, 2131, False), (2131, 2136, False)):
        _, y1, end = pos[a]
        x2, y2, _ = pos[b]
        cls = "gantt-dep critical" if crit else "gantt-dep"
        x, y = max(end + 10, x2 + 10), y2 - 9
        parts.append(f'<path class="{cls}" d="M{end:.0f} {y1}H{x:.0f}V{y - 5}"/><path class="gantt-arrow{" critical" if crit else ""}" d="M{x - 3:.0f} {y - 5}h6l-3 5z"/>')
    today = left + 26 * scale
    parts.append(f'<line class="gantt-today" x1="{today:.0f}" x2="{today:.0f}" y1="{head - 6}" y2="{height}"/><text class="gantt-todaylabel" x="{today + 4:.0f}" y="19">hoje</text>')
    parts.append("</svg>")
    return "".join(parts)


def gantt_body() -> str:
    legend = "".join(f"<li>{stage_mark(k)}</li>" for k in ("ready", "approved", "executing", "blocked"))
    undated = "".join(
        f'<tr><td><span class="id">{s["id"]}</span> &nbsp;<a class="row-title" href="#/spec/{s["id"]}">{e(s["title"])}</a></td><td class="fit">{stage_mark(s["stage"])}</td><td class="fit muted t-small">{dep}</td></tr>'
        for s, dep in ((BY_ID[2147], "—"), (BY_ID[2133], "depois de 2112"), (BY_ID[2141], "—")))
    return f"""<div class="view-head"><h2>Gantt</h2><span class="sub">{len(GANTT)} specs com datas · 3 no caminho crítico</span><span class="grow"></span>
{segmented(["Dia", "Semana", "Mês"], 1)}<button type="button" class="ghost small">Hoje</button>
<label class="check"><input type="checkbox" checked> dependências</label><label class="check"><input type="checkbox" checked> caminho crítico</label></div>
<ul class="legend">{legend}<li><svg width="18" height="12" aria-hidden="true"><rect class="gantt-rect st-executing critical" x="1" y="1" width="16" height="10" rx="2"/></svg>caminho crítico</li><li><svg width="18" height="12" aria-hidden="true"><rect class="gantt-rect st-executing slip" x="1" y="1" width="16" height="10" rx="2"/></svg>com folga estourada</li></ul>
<div class="gantt-scroll" tabindex="0" style="margin-top:8px">{gantt_svg()}</div>
<div class="group-head"><h3>Sem datas</h3><p>3 specs fora do cronograma: o servidor não deriva datas sem estimativa.</p></div>
<div class="table-wrap"><table><thead><tr><th scope="col">Spec</th><th scope="col">Etapa</th><th scope="col">Dependências</th></tr></thead><tbody>{undated}</tbody></table></div>"""


OPENCODE_STATE = "Estado lido da atividade recente: o OpenCode não registra o processo da sessão."


def radar(active: dict) -> str:
    cells = []
    for i in range(60):
        h = active.get(i)
        cells.append(f'<i class="on" style="--h:{h}%"></i>' if h else "<i></i>")
    return f'<div class="radar" role="img" aria-label="Atividade dos últimos 60 minutos">{"".join(cells)}</div>'


def host_tag(host: str) -> str:
    if host == "OpenCode":
        return f'<span class="tag" tabindex="0" data-tip="{e(OPENCODE_STATE)}">{host}</span>'
    return f'<span class="tag">{host}</span>'


def session_lane(branch, host, where, state, label, last, active, subs="") -> str:
    tone = {"waiting": "chip hot", "busy": "chip warn", "idle": "chip"}[state]
    return f"""<div class="lane"><div class="lane-id"><strong>{e(branch)}</strong>{host_tag(host)} <span>{e(where)}</span></div>
{radar(active)}<div class="epic-meta"><span class="{tone}">{label}</span><span>{last}</span></div>{subs}</div>"""


def sublane(name, left, width, active=False, state="concluído") -> str:
    cls = "span active" if active else "span"
    return f"""<div class="sublane"><span class="sublabel">{e(name)}</span><div class="track" role="img" aria-label="{e(name)}"><i class="{cls}" style="--l:{left}%;--w:{width}%"></i></div><span>{state}</span></div>"""


def sessions_body() -> str:
    lanes = [
        session_lane("plan/2137-portal-push", "OpenCode", "quenching-2137 · sessão 8f3a", "waiting", "esperando você", "há 4 min", {54: 60, 55: 90, 49: 40, 48: 30}),
        session_lane("plan/2127-portal-experience", "Claude Code", "quenching-portal · sessão c21e", "busy", "ocupada", "agora", {52: 40, 54: 70, 55: 100, 56: 80, 57: 60, 58: 90, 59: 70},
                     sublane("quenching-verifier", 88, 9, True, "ativo") + sublane("quenching-scout", 70, 12)),
        session_lane("plan/2132-store-sync", "OpenCode", "quenching-2132 · sessão e7d2", "busy", "ocupada", "há 1 min", {44: 30, 47: 50, 50: 80, 53: 60, 56: 70, 58: 90},
                     sublane("quenching-spec-runner", 74, 22, True, "ativo")),
        session_lane("main", "Claude Code", "checkout principal · sessão 03bd", "idle", "ociosa", "há 22 min", {30: 40, 31: 60, 33: 50, 36: 30}),
    ]
    return f"""<div class="wrap">
<div class="view-head"><h2>Sessões</h2><span class="sub">1 espera por você · 4 nos últimos 60 min · 2 no Claude Code, 2 no OpenCode</span></div>
<div class="group-head"><h3>Esperando você</h3></div>
<div class="waiting-list"><div><div class="waiting-head"><span class="id">plan/2137-portal-push</span>{host_tag("OpenCode")}<span class="muted">desde 4 min atrás · question</span></div>
<blockquote class="question" style="margin:0">Subo as escritas pendentes com um push único ou uma spec por vez?</blockquote></div></div>
<div class="group-head"><h3>Atividade</h3></div>
<div class="triagelist">{"".join(lanes)}</div></div>"""


def chat_body() -> str:
    return f"""<div class="chat">
<div class="chat-log" aria-live="polite">
<p class="chat-q">Quais rotas POST o portal aceita hoje e qual delas faz push?</p>
<p class="chat-tool">{ic("search")} ferramenta: <code>Grep</code></p>
<p class="chat-tool">{ic("panel")} ferramenta: <code>Read</code></p>
<div class="chat-a md"><p>São seis rotas de escrita: <code>/api/capture</code>, <code>/api/section</code>, <code>/api/approve</code>, <code>/api/reorder</code>, <code>/api/discovery</code> e <code>/api/push</code>.</p>
<p>A captura é ponto de sincronia e faz push sozinha. As outras ficam no commit local pendente até <code>/api/push</code>, um <code>cq specs push</code> ou a próxima captura.</p></div>
<p class="chat-foot"><span class="chip ok">concluído</span><span>custo: US$ 0,0412</span></p>
</div>
<form class="chat-form"><label class="field">Pergunta<textarea maxlength="4000" placeholder="Pergunte sobre o código desta worktree…"></textarea></label>
<div class="chat-form-row"><label class="control">Worktree <select><option>plan/2127-portal-experience</option></select></label><span class="muted" style="font-size:12px">somente leitura (Read, Grep, Glob) · teto US$ 0,50</span><span class="grow"></span><button type="submit" class="primary">Perguntar</button></div></form>
</div>"""


SPEC_DOC = 2137


def tasks_block() -> str:
    t = [("1.1", "Adicionar a rota de envio ao servidor do portal", True, "commit 244032c"),
         ("1.2", "Expor as escritas pendentes em GET /api/specs", True, "commit 244032c"),
         ("2.1", "Botão Enviar com contagem no shell", True, "commit 5eb7ea4"),
         ("2.2", "Recusar escrita obsoleta com 409 e remédio visível", True, "commit 5eb7ea4"),
         ("3.1", "Testar a publicação com um remoto mais novo", True, "commit ba5e2e6"),
         ("3.2", "Documentar o gesto de envio no standard do portal", False, "verificar: rodar o gate")]
    items = "".join(
        f'<li class="task{" is-done" if done else ""}"><input type="checkbox" disabled{" checked" if done else ""} aria-label="{"feita" if done else "aberta"}">'
        f'<div><span class="task-id">{i}</span> <span class="task-text">{e(text)}</span><span class="task-meta">{e(meta)}</span></div></li>'
        for i, text, done, meta in t)
    return f"""<section class="side-block"><div class="sechead"><h3>Tarefas 5/6</h3></div>
{segmented(["Todas 6", "Abertas 1", "Feitas 5", "Bloqueadas 0"])}
<ul style="margin-top:8px">{items}</ul></section>"""


def records_block() -> str:
    return """<section class="side-block"><h3>Registros</h3><ol class="timeline">
<li><div><b>approved</b>by: human · 28/10/2026</div></li>
<li><div><b>isolation</b>worktree: quenching-2137</div></li>
<li><div><b>run</b>continua · verificado · 31/10/2026</div></li>
<li><div><b>pr</b>#45 · aberto</div></li></ol></section>"""


def sections_block() -> str:
    return """<section class="spec-section" id="sec-1"><div class="sechead"><h3>Problem</h3><button type="button" class="ghost small">Editar</button></div>
<div class="md"><p>As aprovações, seções e descobertas feitas no portal ficam no commit local pendente. Sem um gesto de envio, quem trabalha só pelo navegador precisa abrir um terminal para publicar.</p></div></section>
<section class="spec-section" id="sec-2"><div class="sechead"><h3>Proposal</h3><button type="button" class="ghost small">Editar</button></div>
<div class="md"><p>Um botão <strong>Enviar</strong> no topo, com a contagem de specs com escritas locais, que delega ao mesmo verbo de <code>cq specs push</code>.</p>
<ul><li>Sem <code>--drop</code>: o portal nunca descarta escrita.</li><li>Conflito com o remoto vira <code>409 sp-git-stale-write</code>, com o remédio em texto.</li></ul>
<blockquote><p>Publicar é um gesto explícito: nada sai sozinho do repositório local.</p></blockquote></div></section>
<section class="spec-section" id="sec-3"><div class="sechead"><h3>Impact</h3><button type="button" class="ghost small">Editar</button></div>
<div class="md"><table><thead><tr><th>Arquivo</th><th>Mudança</th></tr></thead><tbody><tr><td><code>specs/portal.py</code></td><td>rota e leitura de pendências</td></tr><tr><td><code>portal/app.js</code></td><td>botão e notificação</td></tr></tbody></table></div></section>"""


def detail_head(s: dict, drawer=False) -> str:
    end = ('<a class="ghost small" href="#/spec/2137">' + ic("expand") + ' Página inteira</a>'
           '<button type="button" class="ghost icon small" aria-label="Fechar">' + ic("x") + "</button>") if drawer else \
          '<a class="ghost small" href="#/board">Voltar ao board</a>'
    return f"""<header class="detail-head">
<h2 class="detail-title"><span class="id">{s["id"]}</span>{e(s["title"])}</h2>
<div class="actions"><button type="button" class="ghost small">{ic("copy")} Copiar comando</button><button type="button" class="ghost small">Registrar descoberta</button>{end}</div>
<p class="detail-meta">{stage_chip(s["stage"])}{pri_button(s["pri"])}{target_button(s)}{owner_button(s)}<span>{s["done"]}/{s["total"]} {PARTS.get(s["kind"], "tarefas concluídas").split()[0]}</span><span>aberta {s["age"]}</span><a href="#">PR #45</a></p>
</header>"""


def detail_foot() -> str:
    a, b = BY_ID[2127], BY_ID[2132]
    return f'<footer class="detail-foot"><a href="#/spec/{a["id"]}">← {a["id"]} · {e(a["title"])}</a><a href="#/spec/{b["id"]}">{b["id"]} · {e(b["title"])} →</a></footer>'


def spec_page() -> str:
    s = BY_ID[SPEC_DOC]
    toc = """<nav class="toc" aria-label="Seções da spec"><h3>Seções</h3><a href="#sec-1" aria-current="true">Problem</a><a href="#sec-2">Proposal</a><a href="#sec-3">Impact</a><span class="absent">Design · ausente</span><span class="absent">Risks · ausente</span></nav>"""
    return f"""{detail_head(s)}<div class="detail">{toc}<div>{sections_block()}</div><aside class="detail-side">{tasks_block()}{records_block()}</aside></div>{detail_foot()}"""


def spec_drawer() -> str:
    s = BY_ID[SPEC_DOC]
    return f"""<div class="backdrop"></div><aside class="drawer" role="dialog" aria-label="Detalhe da spec">{detail_head(s, True)}
<div class="drawer-scroll"><div class="detail in-drawer"><div>{sections_block()}</div><aside class="detail-side">{tasks_block()}{records_block()}</aside></div>{detail_foot()}</div></aside>"""


def palette(query="gantt") -> str:
    def item(label, tail="", active=False):
        cls = "palette-item is-active" if active else "palette-item"
        sel = "true" if active else "false"
        return f'<li class="{cls}" role="option" aria-selected="{sel}"><span class="palette-label">{label}</span>{tail}</li>'
    q = e(query)
    def hl(text):
        return re.sub(f"({re.escape(query)})", r"<mark>\1</mark>", e(text), flags=re.I)
    return f"""<div class="backdrop"></div><div class="dialog palette" role="dialog" aria-label="Paleta de comandos">
<div class="palette-input">{ic("search")}<input role="combobox" aria-label="Buscar specs ou executar uma ação" aria-expanded="true" value="{q}" placeholder="Buscar specs ou executar uma ação…" autocomplete="off" spellcheck="false"></div>
<ul class="palette-list" role="listbox" aria-label="Resultados">
<li class="palette-group" role="presentation">Ações</li>
{item(hl("Ir para o Gantt"), "<kbd>g g</kbd>", True)}
<li class="palette-group" role="presentation">Specs</li>
{item('<span class="id">2140</span> ' + hl(BY_ID[2140]["title"]), stage_mark("ready"))}
{item('<span class="id">2143</span> ' + hl(BY_ID[2143]["title"]), stage_mark("ready"))}
{item(f'Ver todos os resultados para “{q}”', "<kbd>Enter</kbd>")}
</ul>
<div class="palette-foot"><kbd>↑</kbd> <kbd>↓</kbd> navegar · <kbd>Enter</kbd> abrir · <kbd>Esc</kbd> fechar</div></div>"""


SHORTCUTS = [("Ctrl/Cmd+K", "Abrir a paleta de comandos"), ("/", "Buscar na paleta"), ("?", "Abrir este mapa de atalhos"),
             ("g b", "Ir para o board"), ("g l", "Ir para o ranking"), ("g d", "Ir para a fila de decisão"), ("g e", "Ir para os épicos"),
             ("g g", "Ir para o Gantt"), ("g s", "Ir para as sessões"), ("j / k", "Próximo / anterior na lista"), ("Enter", "Abrir a gaveta"),
             ("Ctrl/Cmd+Enter", "Abrir a página inteira"), ("a", "Aprovar a spec em foco"), ("t", "Alternar o tema"), ("Esc", "Fechar o diálogo")]


def help_sheet() -> str:
    gloss = "".join(f"<div><dt>{stage_mark(k)}</dt><dd>{e(m)}</dd></div>" for k, _, m in STAGES)
    keys = "".join(f"<div><span>{e(label)}</span><kbd>{e(k)}</kbd></div>" for k, label in SHORTCUTS)
    return f"""<div class="backdrop"></div><div class="dialog help" role="dialog" aria-labelledby="help-title">
<div class="dialog-head"><h2 id="help-title">Ajuda e atalhos</h2><button type="button" class="ghost icon small" aria-label="Fechar">{ic("x")}</button></div>
<div class="help-grid"><section>
<h3>O que é este portal</h3>
<p>É a leitura local do store de specs: o board mostra o trabalho por etapa, o ranking mostra a prioridade global, Decidir mostra o que espera por você, Épicos mostra o programa e o Gantt mostra o cronograma derivado.</p>
<p>Nada aqui inventa dado: cada número sai do servidor. A etapa de uma spec é derivada das tarefas e da aprovação, não é um campo que se arrasta.</p>
<h3>O que cada etapa significa</h3><dl class="glossary">{gloss}</dl></section>
<section><h3>Atalhos</h3><div class="keys">{keys}</div>
<h3>O que o portal não faz</h3><ul class="plain"><li>Não move cartão entre etapas: a etapa é derivada.</li><li>Não edita tarefa nem marca checkbox: a tarefa é lida.</li><li>Não escreve fora das seis ações: capturar, editar seção, aprovar, reordenar, registrar descoberta e enviar.</li></ul></section></div></div>"""


def capture_dialog() -> str:
    return f"""<div class="backdrop"></div><div class="dialog" role="dialog" aria-labelledby="dlg-title">
<div class="dialog-head"><h2 id="dlg-title">Capturar uma spec</h2><button type="button" class="ghost icon small" aria-label="Fechar">{ic("x")}</button></div>
<form class="dialog-form">
<label class="field">Título<input type="text" required value="Mostrar quem aprovou no card da spec"></label>
<label class="field">Problema<textarea required placeholder="O que está errado hoje e quem sofre com isso?"></textarea><span class="field-hint">A captura vai ao remoto na hora: é um ponto de sincronia.</span></label>
<div class="actions"><button type="button">Cancelar</button><button type="submit" class="primary">Capturar</button></div></form></div>"""


def search_body() -> str:
    def row(s, snip):
        return f"""<li class="triage"><div class="triage-main"><span class="id">{s["id"]}</span><a href="#/spec/{s["id"]}">{e(s["title"]).replace("Gantt", "<mark>Gantt</mark>")}</a></div>
<div class="triage-aside">{stage_mark(s["stage"])}</div><p class="why">…{snip}…</p></li>"""
    rows = [row(BY_ID[2140], "o <mark>Gantt</mark> lê o schedule inteiro a cada troca de zoom"),
            row(BY_ID[2143], "filtrar as barras do <mark>Gantt</mark> pelo responsável da spec")]
    return f"""<div class="wrap"><div class="view-head"><h2>2 de 2 resultados para “gantt”</h2><span class="grow"></span><button type="button" class="ghost small">{ic("search")} Nova busca</button></div>
<div class="board-tools" style="padding:0;border:0;margin-bottom:12px"><label class="control">Etapa <select><option>todas (2)</option></select></label><label class="control">Assunto <select><option>todos (2)</option></select></label><label class="control">Tipo <select><option>todos (2)</option></select></label></div>
<ul class="triagelist">{"".join(rows)}</ul></div>"""


def rail() -> str:
    return """<nav class="projects" aria-label="Projetos"><h2>Projetos</h2><ul>
<li><button type="button" class="project" aria-current="true">quenching</button><ul class="trees"><li><button type="button" class="tree">main</button></li><li><button type="button" class="tree">plan/2137-portal-push</button></li><li><button type="button" class="tree">plan/2127-portal-experience</button></li></ul></li>
<li><button type="button" class="project" aria-current="false">forge</button><ul class="trees"><li><button type="button" class="tree">main</button></li></ul></li>
<li><button type="button" class="project" aria-current="false">hallmark</button><ul class="trees"><li><button type="button" class="tree">main</button></li></ul></li>
</ul></nav>"""


READ_ONLY = (f'<p class="banner" role="status">{ic("lock")}<span>Somente leitura: o servidor foi iniciado com <code>--read-only</code>. '
             "Capturar, aprovar e enviar estão desligados.</span></p>")
OFFLINE = (f'<p class="banner conn" role="alert">{ic("alert")}<span>Sem conexão com o portal desde 15:04. Os dados abaixo são de 15:03.</span>'
           '<button type="button" class="ghost small">Tentar de novo</button></p>')


def skeleton_board() -> str:
    def sk():
        return '<div class="sk-card"><span class="sk w70"></span><span class="sk w95"></span><span class="sk w45"></span></div>'
    cols = "".join(
        f'<section class="col" data-stage="{k}"><h2 class="col-head"><span class="col-toggle" style="display:flex;align-items:center"><span class="col-name">{STAGE_PT[k].capitalize()}</span><span class="count">·</span></span></h2><div class="col-body">{sk()}{sk()}{sk()}</div></section>'
        for k in ("captured", "ready", "approved", "executing", "blocked", "review"))
    return f'<p class="loading-line" role="status">Lendo o repositório de specs…</p><div class="board" aria-hidden="true">{cols}</div>'


# ── catalogue ─────────────────────────────────────────────────────────────────────────────────
def pad(html: str, gap=12, width="") -> str:
    w = f"max-width:{width};" if width else ""
    return f'<div style="padding:16px;display:grid;gap:{gap}px;{w}">{html}</div>'


def row(html: str) -> str:
    return f'<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">{html}</div>'


def c_stages():
    rows = "".join(
        f'<tr><td class="fit">{stage_mark(k)}</td><td class="fit">{stage_chip(k)}</td><td><div class="col-head" data-stage="{k}" style="height:12px"></div></td><td class="muted">{e(m)}</td></tr>'
        for k, _, m in STAGES)
    return pad(f'<div class="table-wrap"><table><thead><tr><th scope="col">Marca</th><th scope="col">Chip</th><th scope="col">Trilho</th><th scope="col">Significado</th></tr></thead><tbody>{rows}</tbody></table></div>')


def c_icons():
    cells = "".join(f'<div style="display:grid;justify-items:center;gap:6px;padding:12px 4px;font-size:11px;color:var(--muted)">{ic(k)}<code>{k}</code></div>' for k in ICONS)
    return pad(f'<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(84px,1fr));gap:4px">{cells}</div>')


def c_buttons():
    return pad(row('<button type="button" class="primary">' + ic("plus") + ' Capturar</button><button type="button" class="heat">Aprovar</button><button type="button">Cancelar</button><button type="button" class="ghost">Abrir</button><button type="button" class="link">ver a spec</button>')
               + row('<button type="button" class="primary small">Confirmar aprovação</button><button type="button" class="heat small">Aprovar</button><button type="button" class="small">Copiar comando</button><button type="button" class="ghost small">Abrir</button>')
               + row(f'<button type="button" class="ghost icon" aria-label="Ajuda">{ic("help")}</button><button type="button" class="ghost icon small" aria-label="Copiar">{ic("copy")}</button><button type="button" class="ghost small" aria-pressed="true">em execução</button><button type="button" class="ghost small" aria-pressed="false">bloqueadas</button>')
               + row('<button type="button" class="primary" disabled>Capturar</button><button type="button" disabled>Enviar</button><button type="button" class="ghost" disabled>Abrir</button>')
               + row(f'Decidir <span class="count hot">{WAITING}</span> Épicos <span class="count">3</span> <kbd>Ctrl K</kbd> <kbd>g b</kbd>'))


def c_fields():
    return pad(f"""<label class="field">Título<input type="text" value="Filtro por responsável no Gantt"></label>
<label class="field">Problema<textarea placeholder="O que está errado hoje e quem sofre com isso?"></textarea><span class="field-hint">A captura vai ao remoto na hora.</span></label>
<label class="field">Título<input type="text" aria-invalid="true" value=""><span class="field-hint" style="color:var(--bad)">Dê um título à spec.</span></label>
{row('<label class="control">Agrupar <select><option>Etapa</option></select></label><label class="control">Ordenar <select><option>Ranking</option></select></label><label class="check"><input type="checkbox" checked> compacto</label><label class="check"><input type="checkbox"> ocultar vazias</label>')}
{segmented(["Dia", "Semana", "Mês"], 1)}""", width="520px")


def c_tags():
    return pad(row("".join(stage_mark(k) for k, _, _ in STAGES))
               + row("".join(stage_chip(k) for k, _, _ in STAGES))
               + row(pri(1) + pri(2) + pri(3) + pri(4) + '<span class="chip">Portal</span><span class="tag">#store</span><span class="chip hot">espera você</span><span class="chip ok">concluído</span><span class="chip warn">em andamento</span><span class="chip bad">bloqueio</span>')
               + row(run_mark(BY_ID[2137]) + run_mark(BY_ID[2132]) + run_mark(BY_ID[2129])))


def c_progress():
    return pad(f'<div class="card-signal">{progress(BY_ID[2137])}</div><div class="card-signal">{progress(BY_ID[2119])}</div>'
               '<div class="epic-progress"><span>4 de 11 features · onda 2 de 4</span><div class="meter" role="img" aria-label="4 de 11"><span style="--n:3"><i style="width:100%"></i></span><span style="--n:3"><i style="width:33%"></i></span><span style="--n:3"><i style="width:0"></i></span><span style="--n:2"><i style="width:0"></i></span></div></div>', width="320px")


def c_cards():
    picks = [card(BY_ID[2137], cursor=True), card(BY_ID[2140]), card(BY_ID[2119]), card(BY_ID[2129]), card(BY_ID[2148]), card(BY_ID[2125], show_stage=True)]
    grid = f'<div style="display:grid;grid-template-columns:repeat(3,236px);gap:12px;align-items:start">{"".join(picks)}</div>'
    compact = f'<div class="board compact" style="display:grid;grid-template-columns:repeat(3,236px);gap:8px;overflow:visible">{"".join(card(BY_ID[i]) for i in (2137, 2140, 2119))}</div>'
    return pad(grid + compact, gap=20)


def c_lane():
    return f'<div class="board" style="height:420px">{lane("ready", READY[:3])}{lane("blocked", BLOCKED)}{lane("review", [])}{lane_collapsed("archived", ARCHIVED)}</div>'


def c_events():
    ev = [("15:00", "data", "2 specs mudaram de etapa"), ("14:58", "action", "Spec #2131 aprovada"), ("14:51", "conn", "conexão instável por 40 s")]
    rows = "".join(f'<li class="ev {k}"><time>{t}</time><span>{e(m)}</span></li>' for t, k, m in ev)
    return pad(f'<section class="events" aria-label="Notificações"><div class="events-head"><h2>Notificações</h2><button type="button" class="ghost small">Avisar no navegador</button></div><ol class="events-list">{rows}</ol></section>')


def c_toast():
    return pad(f'<div class="toast ok" style="max-width:420px">{ic("check")}<span>Aprovada por: human</span><button type="button" class="ghost small">Ver a fila</button></div>'
               f'<div class="toast bad" style="max-width:420px">{ic("alert")}<span>Conflito com o remoto: rode <code>cq specs push</code> no terminal.</span></div>')


def c_empty():
    return pad('<div class="panel empty-state"><p class="empty-title">Nada espera por você</p><p class="empty-hint">Nenhuma feature de épico aberta, tarefa bloqueada ou spec desenvolvida sem aprovação.</p><a class="ghost" href="#/board">Ver o board</a></div>'
               '<div class="panel empty-state"><p class="empty-title">O portal não conseguiu ler o repositório</p><p class="empty-hint">git: remote ref not found</p><button type="button" class="primary">Tentar de novo</button></div>', width="640px")


def c_skeleton():
    return pad('<p class="loading-line" style="padding:0">Lendo o repositório de specs…</p><div class="sk-card" style="max-width:236px"><span class="sk w70"></span><span class="sk w95"></span><span class="sk w45"></span></div>')


def c_popover():
    selects = "".join(f'<label class="control">{k} <select><option>todos</option></select></label>' for k in ("Etapa", "Assunto", "Tag", "Tipo", "Responsável", "Complexidade"))
    return f'<div style="padding:16px;height:300px"><div class="pop" style="display:inline-block"><button type="button" class="ghost small" aria-expanded="true">{ic("filter")} Filtros</button><div class="pop-body">{selects}</div></div></div>'


def c_overlay(html: str, h: int) -> str:
    return f'<div class="app" style="--app-h:{h}px;display:block">{html}</div>'


CARDS = [  # folder, group, height, width, subtitle, body
    ("Stages", "Foundations", 420, 960, "Seven derived stages: mark, chip and lane rule", c_stages),
    ("Icons", "Foundations", 410, 800, "One authored 16px set, inline SVG, 1.5 stroke", c_icons),
    ("TopBar", "Shell", 64, 1280, "Brand, seven destinations, search, theme, help, capture", lambda: topbar()),
    ("Pulse", "Shell", 48, 1280, "Seven counts in one strip, the human's first", lambda: pulse()),
    ("Banner", "Shell", 96, 1000, "Read-only and connection states", lambda: pad(READ_ONLY + OFFLINE, gap=8)),
    ("StatusBar", "Shell", 96, 1000, "Connection, freshness, pause, refresh, notifications", lambda: pad(statusbar() + statusbar("offline", "dados de 15:03 · há 2 min", 3, True), gap=8)),
    ("ProjectRail", "Shell", 300, 320, "Projects and worktrees under the central server", rail),
    ("Buttons", "Actions and inputs", 250, 800, "Primary, heat, default, ghost, link, icon, toggle", c_buttons),
    ("Fields", "Actions and inputs", 340, 600, "Text, textarea, select, check, segmented", c_fields),
    ("BoardToolbar", "Actions and inputs", 110, 1280, "One row: group, sort, filters, quick toggles, views", lambda: toolbar(pressed=("em execução",), chips='<button type="button" class="fchip">tag: portal ' + ic("x") + "</button>")),
    ("Popover", "Actions and inputs", 300, 400, "Facet filters and saved views", c_popover),
    ("Tags", "Status", 170, 900, "Stage mark, chips, priority, runner verdict", c_tags),
    ("Progress", "Status", 120, 400, "Task bar and the epic meter by wave", c_progress),
    ("SpecCard", "Board", 660, 800, "The board's unit, comfortable and compact", c_cards),
    ("Lane", "Board", 420, 1000, "A stage column: rule, count, own scroll, collapsible", c_lane),
    ("RankList", "Views", 520, 1280, "The global order as row cards, with drag and arrow keys", lambda: pad(rank_list())),
    ("DecisionRow", "Views", 300, 1100, "One decision per row; approval is armed in place", lambda: pad(f'<ul class="triagelist">{triage(BY_ID[2140], "Isto grava “approved by: human” e não se desfaz.", armed=True)}{triage(BY_ID[2139], BY_ID[2139]["summary"])}{triage(BY_ID[2112], BY_ID[2112]["why"], bad=True, kind="open")}</ul>')),
    ("EpicPanel", "Views", 470, 1100, "Health, wave meter, next step and the waves", lambda: pad(epic_panel())),
    ("GanttChart", "Views", 370, 1400, "The server's schedule as SVG", lambda: pad(f'<div class="gantt-scroll">{gantt_svg()}</div>')),
    ("SessionLane", "Views", 280, 1100, "Live sessions told apart by branch, host, worktree and id", lambda: pad(f'<div class="triagelist">{session_lane("plan/2137-portal-push", "OpenCode", "quenching-2137 · sessão 8f3a", "waiting", "esperando você", "há 4 min", {54: 60, 55: 90})}{session_lane("plan/2127-portal-experience", "Claude Code", "quenching-portal · sessão c21e", "busy", "ocupada", "agora", {55: 100, 56: 80, 58: 90}, sublane("quenching-verifier", 88, 9, True, "ativo"))}</div>')),
    ("ChatPanel", "Views", 520, 900, "One read-only question at a time, with its cost", lambda: f'<div style="height:500px;padding:16px">{chat_body()}</div>'),
    ("SpecHeader", "Detail", 130, 1100, "Title, stage, facts and actions in one block", lambda: detail_head(BY_ID[2137])),
    ("Markdown", "Detail", 430, 800, "The safe subset, built node by node", lambda: pad(sections_block())),
    ("TaskList", "Detail", 400, 420, "Tasks with filter, verify and commit", lambda: pad(tasks_block())),
    ("Timeline", "Detail", 190, 420, "The spec's records in order", lambda: pad(records_block())),
    ("Drawer", "Overlays", 640, 1200, "The detail beside the board, with focus returned", lambda: c_overlay(spec_drawer(), 640)),
    ("Dialog", "Overlays", 480, 900, "Capture, edit section, register a discovery", lambda: c_overlay(capture_dialog(), 480)),
    ("Palette", "Overlays", 400, 900, "Ctrl K: actions, specs and recents by group", lambda: c_overlay(palette(), 400)),
    ("HelpSheet", "Overlays", 820, 1100, "What the portal is, stages, keys and limits", lambda: c_overlay(help_sheet(), 820)),
    ("Toast", "Feedback", 130, 600, "One line of outcome, with one optional action", c_toast),
    ("Events", "Feedback", 220, 600, "The notification centre", c_events),
    ("EmptyState", "Feedback", 380, 800, "Teaches the next step, or names the failure", c_empty),
    ("Skeleton", "Feedback", 140, 400, "First paint: the shape of the board, not a spinner", c_skeleton),
]

GROUPED = sorted(SPECS, key=lambda s: s["pri"])


def screen_grouped() -> str:
    groups = []
    labels = {1: "P1 · crítica", 2: "P2 · alta", 3: "P3 · média", 4: "P4 · baixa"}
    for p in (1, 2, 3, 4):
        specs = [s for s in GROUPED if s["pri"] == p]
        cards = "\n".join(card(s, show_stage=True, approve=False) for s in specs)
        groups.append(f'<section class="col" aria-label="{labels[p]}"><h2 class="col-head"><button type="button" class="col-toggle" aria-expanded="true"><span class="col-name">{labels[p]}</span><span class="count">{len(specs)}</span></button></h2><div class="col-body">{cards}</div></section>')
    chips = '<button type="button" class="fchip">assunto: Portal ' + ic("x") + '</button><button type="button" class="ghost small">limpar tudo</button>'
    return toolbar(group="Prioridade", chips=chips, compact=True) + f'<div class="board compact">{"".join(groups)}</div>'


SCREENS = [  # folder, height, width, subtitle, body
    ("ScreenBoard", 900, 1440, "Board by stage: the entry page", lambda: app(toolbar() + board_lanes(), main_cls="is-board")),
    ("ScreenBoardGrouped", 900, 1440, "Board by priority, compact, with a filter", lambda: app(screen_grouped(), main_cls="is-board")),
    ("ScreenRanking", 900, 1440, "Global ranking", lambda: app(f'<div class="view-head"><h2>Ranking</h2><span class="sub">{OPEN} specs abertas · arraste uma linha ou use as setas, dentro do mesmo nível; cada mudança é um commit</span></div>{rank_list()}', current="list")),
    ("ScreenDecide", 900, 1440, "Decide: the human queue, with an armed approval", lambda: app(decide_body(), current="human", push=2)),
    ("ScreenEpics", 900, 1440, "Epics as programmes", lambda: app(toolbar(group="Nenhum", groups=EPIC_GROUPS, sorts=EPIC_SORTS, quick_items=EPIC_QUICK, label="Controles de épicos", board=False) + f'<div class="view-scroll"><div class="view-head"><h2>Épicos</h2><span class="sub">2 abertos · 18 features</span></div>{epic_panel()}{epic_closed()}</div>', current="epics", main_cls="is-board")),
    ("ScreenGantt", 900, 1440, "Gantt with dated and undated specs", lambda: app(gantt_body(), current="gantt")),
    ("ScreenSessions", 900, 1440, "Live sessions", lambda: app(sessions_body(), current="sessions")),
    ("ScreenChat", 900, 1440, "Read-only chat", lambda: app(chat_body(), current="chat")),
    ("ScreenSpecPage", 900, 1440, "A spec on its own page", lambda: app(spec_page(), current="board", main_cls="is-page")),
    ("ScreenSpecDrawer", 900, 1440, "A spec in the drawer, over the board", lambda: app(toolbar() + board_lanes(), main_cls="is-board", overlay=spec_drawer())),
    ("ScreenPalette", 900, 1440, "Command palette, filtered", lambda: app(toolbar() + board_lanes(), main_cls="is-board", overlay=palette())),
    ("ScreenHelp", 900, 1440, "Help and shortcuts", lambda: app(toolbar() + board_lanes(), main_cls="is-board", overlay=help_sheet())),
    ("ScreenCapture", 900, 1440, "Capture a spec", lambda: app(toolbar() + board_lanes(), main_cls="is-board", overlay=capture_dialog())),
    ("ScreenSearch", 900, 1440, "Search results with facets", lambda: app(search_body(), current="")),
    ("ScreenCentral", 900, 1440, "Central server: project rail beside the board", lambda: app(toolbar() + board_lanes(), rail=rail(), main_cls="is-board")),
    ("ScreenReadOnly", 900, 1440, "Read-only server: no writes offered", lambda: app(toolbar() + board_lanes(approve=False), main_cls="is-board", banner=READ_ONLY, capture=False)),
    ("ScreenOffline", 900, 1440, "Connection lost: data kept and dated", lambda: app(toolbar() + board_lanes(), main_cls="is-board", banner=OFFLINE, status=statusbar("offline", "dados de 15:03 · há 2 min", 3, True))),
    ("ScreenLoading", 900, 1440, "First paint", lambda: app(skeleton_board(), main_cls="is-board", waiting=0, sessions=0, status=statusbar("unstable", "carregando", 0),
                                                         pulse_html='<section class="pulse" aria-hidden="true">' + '<span class="pulse-cell skeleton" style="width:150px"></span>' * 6 + "</section>")),
    ("ScreenDecideEmpty", 900, 1440, "Decide with nothing waiting", lambda: app('<div class="wrap"><div class="view-head"><h2>Decidir</h2><span class="sub">Nada espera por você</span></div><div class="panel empty-state"><p class="empty-title">Fila limpa</p><p class="empty-hint">Nenhuma feature de épico aberta, tarefa bloqueada ou spec desenvolvida sem aprovação. Quando algo precisar de você, o contador do topo acende.</p><a class="ghost" href="#/board">Ver o board</a></div></div>', current="human", waiting=0, sessions=0)),
    ("ScreenMobileBoard", 844, 390, "Board on a phone", lambda: app(toolbar() + board_lanes(cursor=None), main_cls="is-board", h=844)),
    ("ScreenMobileDecide", 844, 390, "Decide on a phone", lambda: app(decide_body(armed=False), current="human", h=844)),
]


# ── tokens.css, laid out as the Design System page compiles it ─────────────────────────────────
def compile_tokens(t: dict) -> str:
    title = t["name"]
    themes = [x["id"] for x in t["color"]["themes"]]
    first = themes[0]

    def theme_block(theme):
        out = []
        for tok in t["color"]["tokens"] + t["shadow"]["tokens"]:
            v = tok["value"]
            out.append(f'  --{tok["name"]}: {v[theme] if isinstance(v, dict) else v};')
        return "\n".join(out)

    lines = [f"/* {title} — generated from tokens.json */",
             f':root, [data-theme="{first}"] {{', theme_block(first), "}"]
    for theme in themes[1:]:
        lines += [f'[data-theme="{theme}"] {{', theme_block(theme), "}"]
    lines.append(":root {")
    for fam in ("spacing", "radius", "step"):
        lines += [f'  --{tok["name"]}: {tok["value"]};' for tok in t[fam]["tokens"]]
    lines += [f"  --font-{k}: {v};" for k, v in t["type"]["families"].items()]
    lines.append("}")
    for group in t["type"]["groups"]:
        for s in group["styles"]:
            lines.append(f'.{s["name"]} {{ font-family: var(--font-{group["family"]}); font-size: {s["fontSize"]}; '
                         f'line-height: {s["lineHeight"]}; font-weight: {s["fontWeight"]}; }}')
    return "\n".join(lines) + "\n"


def doc(title: str, marker: str, body: str) -> str:
    return f"""<!-- @dsCard {marker} -->
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<link rel="stylesheet" href="../../tokens.css">
<link rel="stylesheet" href="../bundle.css">
</head>
<body>
{body}
</body>
</html>
"""


def outputs() -> dict[Path, str]:
    tokens = json.loads((ROOT / "tokens.json").read_text(encoding="utf-8"))
    out = {ROOT / "tokens.css": compile_tokens(tokens)}
    for name, group, height, width, sub, render in CARDS:
        marker = f'group="{group}" height={height} width={width} subtitle="{sub}"'
        out[COMPONENTS / name / "preview.html"] = doc(name, marker, render())
    for name, height, width, sub, render in SCREENS:
        marker = f'group="Target screens" height={height} width={width} page subtitle="{sub}"'
        out[COMPONENTS / name / "preview.html"] = doc(name, marker, render())
    return out


# ── the contract ───────────────────────────────────────────────────────────────────────────────
def lum(hex_: str) -> float:
    h = hex_.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    def linear(c):
        return c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    return .2126 * linear(r) + .7152 * linear(g) + .0722 * linear(b)


def ratio(a: str, b: str) -> float:
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + .05) / (y + .05)


PAIRS = [(fg, bg, 4.5) for fg, bg in (
    ("person-1-ink", "person-1-bg"), ("person-2-ink", "person-2-bg"),
    ("person-3-ink", "person-3-bg"),
    ("ink", "bg"), ("ink", "surface"), ("ink", "surface-2"), ("ink", "surface-3"), ("muted", "bg"), ("muted", "surface"),
    ("muted", "surface-2"), ("accent", "surface"), ("accent", "bg"), ("accent", "heat-tint"), ("accent-ink", "accent"),
    ("bad", "surface"), ("bad", "bg"), ("bad", "bad-tint"), ("warn", "surface"), ("ok", "surface"), ("info", "surface"),
    ("chip-ink", "chip-bg"), ("stage-executing-ink", "stage-executing-bg"), ("ink", "heat-tint"),
)] + [(f"stage-{k}-ink", f"stage-{k}-bg", 4.5) for k, _, _ in STAGES] + [
    ("control-line", "surface", 3), ("control-line", "bg", 3), ("control-line", "surface-2", 3),
    ("focus", "surface", 3), ("focus", "bg", 3), ("focus", "surface-2", 3),
] + [(f"stage-{k}", "surface", 3) for k, _, _ in STAGES]


def check(files: dict[Path, str]) -> list[str]:
    problems = []
    tokens = json.loads((ROOT / "tokens.json").read_text(encoding="utf-8"))
    css = (COMPONENTS / "bundle.css").read_text(encoding="utf-8")
    tokens_css = files[ROOT / "tokens.css"]
    colors = {t["name"]: t["value"] for t in tokens["color"]["tokens"]}
    for theme in ("light", "dark"):
        for fg, bg, floor in PAIRS:
            r = ratio(colors[fg][theme], colors[bg][theme])
            if r < floor:
                problems.append(f"contrast {theme}: {fg} on {bg} is {r:.2f}, floor {floor}")
    declared = set(re.findall(r"--([\w-]+)\s*:", css + tokens_css))
    for name in sorted(set(re.findall(r"var\(--([\w-]+)", css))):
        if name not in declared and name not in {"stage", "app-h", "n", "l", "w", "h"}:
            problems.append(f"var(--{name}) has no declaration")
    defined = set(re.findall(r"\.([A-Za-z][\w-]*)", re.sub(r"url\([^)]*\)|\d\.\d+", "", css + tokens_css)))
    used = set()
    for path, text in files.items():
        if path.suffix != ".html":
            continue
        for attr in re.findall(r'class="([^"]*)"', text):
            used.update(attr.split())
        if re.search(r"(?:src|href)=\"https?://|url\(http|@import", text):
            problems.append(f"{path.parent.name}: reaches outside itself")
    # state and hook classes that need no rule of their own
    hooks = {"action", "wide", "theme", "helpbtn", "tree", "project", "trees", "st-executing", "searchbtn-label", "hint", "approve", "pass"}
    for name in sorted(used - defined - hooks):
        problems.append(f"class .{name} is used but not defined")
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="write nothing; fail on drift or a broken contract")
    args = parser.parse_args(argv)
    files = outputs()
    drift = [p for p, text in files.items() if not p.exists() or p.read_text(encoding="utf-8") != text]
    if args.check:
        problems = check(files) + [f"stale: {p.relative_to(ROOT)}" for p in drift]
    else:
        for path in drift:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(files[path], encoding="utf-8")
        problems = check(files)
    print(f"{len(files)} files, {len(drift)} {'stale' if args.check else 'written'}, {len(problems)} problems")
    for p in problems:
        print(" -", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
