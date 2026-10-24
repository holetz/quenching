"use strict";
/* Quenching spec portal. No build, no CDN, no HTML strings: every node is created with
   textContent, so spec text can never inject markup. */
(() => {
  const $ = (s) => document.querySelector(s);
  const state = { specs: [], stages: [], fetchedAt: 0, ttl: 5, writable: false, why: "",
                  filters: { subject: "", tag: "", type: "", assignee: "", complexity: "" },
                  epics: { supported: false, epics: [] }, human: null, busy: false,
                  sessionsOn: false, sessions: null, chatOn: false, chatBudget: null,
                  chat: { draft: "", worktree: "", job: null, status: "", events: [], next: 0, cost: null, error: "" },
                  projects: null, project: "", base: "" };

  /* ── helpers ─────────────────────────────────────────────────────────────── */
  function h(tag, attrs, ...kids) {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v === false || v == null) continue;
      if (k === "on") { for (const [ev, fn] of Object.entries(v)) el.addEventListener(ev, fn); }
      else if (k === "class") el.className = v;
      else if (k === "style") el.style.cssText = v;
      else if (k in el && k !== "list" && k !== "form") el[k] = v;
      else el.setAttribute(k, v === true ? "" : v);
    }
    for (const kid of kids.flat()) {
      if (kid == null || kid === false) continue;
      el.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
    }
    return el;
  }
  function safeHref(url) { return /^https?:\/\//i.test(url) ? url : ""; }

  /* Change token: the list reads carry an ETag. The server answers no-store, so the page keeps
     the validator and the body itself and sends If-None-Match; a 304 reuses the kept body. */
  const validated = {};
  let changed = false;
  async function api(path, opts = {}) {
    const init = { method: opts.body ? "POST" : "GET", headers: {}, credentials: "same-origin" };
    const key = state.base + path;
    const kept = !opts.body && /^(specs|epics|human|sessions)(\?|$)/.test(path) ? validated[key] : null;
    if (kept) init.headers["If-None-Match"] = kept.etag;
    if (opts.body) { init.headers["Content-Type"] = "application/json"; init.body = JSON.stringify(opts.body); }
    let res, data;
    try {
      res = await fetch(state.base + "/api/" + path, init);
      if (res.status === 304 && kept) return kept.data;
      data = await res.json();
    } catch (e) { throw { code: "network", message: "the portal server is not reachable" }; }
    if (!res.ok || data.ok === false) throw { code: data.code || "http-" + res.status, message: data.message || res.statusText, data };
    const etag = res.headers.get("ETag");
    if (etag && !opts.body && /^(specs|epics|human|sessions)(\?|$)/.test(path)) { validated[key] = { etag, data }; changed = true; }
    return data;
  }
  function toast(msg, ok) {
    const t = h("div", { class: "toast" + (ok ? " ok" : "") }, msg);
    $("#toasts").append(t);
    setTimeout(() => t.remove(), ok ? 3500 : 9000);
  }
  function fail(e) { toast([h("code", {}, e.code), ": " + e.message]); }

  /* ── minimal safe markdown: headings, lists, checkboxes, code, links, emphasis ── */
  function inline(text) {
    const out = [];
    const re = /(`[^`]+`)|(\[[^\]]+\]\([^)\s]+\))|(\*\*[^*]+\*\*)|(\*[^*\s][^*]*\*)|(_[^_\s][^_]*_)/g;
    let last = 0, m;
    while ((m = re.exec(text))) {
      if (m.index > last) out.push(text.slice(last, m.index));
      const t = m[0];
      if (m[1]) out.push(h("code", {}, t.slice(1, -1)));
      else if (m[2]) {
        const [, label, url] = /^\[([^\]]+)\]\(([^)]+)\)$/.exec(t);
        const href = safeHref(url);
        out.push(href ? h("a", { href, target: "_blank", rel: "noopener noreferrer" }, label) : label);
      } else if (m[3]) out.push(h("strong", {}, t.slice(2, -2)));
      else out.push(h("em", {}, t.slice(1, -1)));
      last = m.index + t.length;
    }
    if (last < text.length) out.push(text.slice(last));
    return out;
  }
  function markdown(src) {
    const root = h("div", { class: "md" });
    const lines = String(src || "").replace(/\r/g, "").split("\n");
    let list = null, para = [], i = 0;
    const flushPara = () => { if (para.length) { root.append(h("p", {}, inline(para.join(" ")))); para = []; } };
    const flushList = () => { list = null; };
    while (i < lines.length) {
      const line = lines[i];
      if (/^```/.test(line)) {
        flushPara(); flushList();
        const code = []; i++;
        while (i < lines.length && !/^```/.test(lines[i])) code.push(lines[i++]);
        root.append(h("pre", {}, h("code", {}, code.join("\n"))));
        i++; continue;
      }
      let m;
      if ((m = /^(#{1,6})\s+(.*)$/.exec(line))) {
        flushPara(); flushList();
        root.append(h("h" + Math.min(4, m[1].length + 1), {}, inline(m[2])));
      } else if ((m = /^\s*[-*+]\s+(?:\[([ xX!])\]\s+)?(.*)$/.exec(line)) || (m = /^\s*\d+[.)]\s+(?:\[([ xX!])\]\s+)?(.*)$/.exec(line))) {
        flushPara();
        if (!list) { list = h("ul"); root.append(list); }
        const box = m[1] === undefined ? null
          : h("input", { type: "checkbox", disabled: true, checked: /[xX]/.test(m[1]), "aria-label": m[1] === "!" ? "blocked" : "task" });
        list.append(h("li", { class: box ? "task" : "" }, box, box ? " " : "", inline(m[2])));
      } else if (!line.trim()) { flushPara(); flushList(); }
      else { flushList(); para.push(line.trim()); }
      i++;
    }
    flushPara();
    return root;
  }

  /* ── data ────────────────────────────────────────────────────────────────── */
  async function load(refresh) {
    changed = false;
    const before = state.human ? state.human.count : null;
    const data = await api("specs" + (refresh ? "?refresh=1" : ""));
    state.specs = data.specs; state.stages = data.stages; state.ttl = data.ttlSeconds;
    state.fetchedAt = Date.now();
    try {
      const ep = await api("epics");
      state.epics = ep;
    } catch (e) { state.epics = { supported: false, epics: [] }; }
    $("#nav-epics").hidden = !state.epics.supported;
    try { state.human = await api("human"); } catch (e) { state.human = null; }
    if (state.sessionsOn) {
      try { state.sessions = await api("sessions"); } catch (e) { state.sessions = null; }
      paintSessionsCount();
    }
    paintHumanCount();
    notifyGrowth(before, state.human ? state.human.count : 0);
    tickFreshness();
    return changed;
  }
  /* Opt-in browser notification (off by default, no OpenCode permission): only when the queue grows. */
  function notifyOn() { return localStorageGet("qnotify") === "1" && typeof Notification !== "undefined" && Notification.permission === "granted"; }
  function localStorageGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function localStorageSet(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } }
  function notifyGrowth(before, now) {
    if (before == null || now <= before || !notifyOn()) return;
    try { new Notification("Quenching specs", { body: `${now} ${now === 1 ? "spec waits" : "specs wait"} for the human` }); } catch (e) { /* unsupported */ }
  }
  function paintNotify() {
    const b = $("#notify");
    if (typeof Notification === "undefined") { b.hidden = true; return; }
    b.textContent = notifyOn() ? "Notifications: on" : "Notifications: off";
    b.setAttribute("aria-pressed", notifyOn() ? "true" : "false");
  }
  async function toggleNotify() {
    if (notifyOn()) { localStorageSet("qnotify", "0"); paintNotify(); return; }
    const perm = Notification.permission === "granted" ? "granted" : await Notification.requestPermission();
    if (perm === "granted") localStorageSet("qnotify", "1"); else toast("Notifications were not allowed by the browser.");
    paintNotify();
  }
  async function loadConfig() {
    try {
      const c = await api("config");
      state.writable = c.writable; state.why = c.readOnlyReason; state.sessionsOn = !!c.sessions;
      state.chatOn = !!c.chat; state.chatBudget = c.chatBudgetUsd;
    } catch (e) { fail(e); }
    $("#nav-sessions").hidden = !state.sessionsOn;
    $("#nav-chat").hidden = !state.chatOn;
    $("#capture").disabled = !state.writable;
    const b = $("#banner");
    b.hidden = state.writable;
    b.textContent = state.writable ? "" : "Read-only: " + state.why + ". Write actions are disabled on the server.";
  }
  function tickFreshness() {
    const el = $("#fresh");
    if (!state.fetchedAt) return;
    const s = Math.max(0, Math.round((Date.now() - state.fetchedAt) / 1000));
    el.textContent = "updated " + (s < 60 ? s + "s" : Math.floor(s / 60) + "m") + " ago";
    $(".fresh").classList.toggle("stale", s > 120);
  }
  async function refresh(force) {
    $("#refresh").disabled = true;
    try { const did = await load(force); if (force || did) await render(); } catch (e) { fail(e); } finally { $("#refresh").disabled = false; }
  }

  /* ── views ───────────────────────────────────────────────────────────────── */
  function progress(p) {
    if (!p.total) return null;
    return [h("span", {}, `${p.checked}/${p.total}`),
            h("span", { class: "bar", role: "img", "aria-label": `${p.checked} of ${p.total} tasks done` },
              h("i", { style: `width:${Math.round(100 * p.checked / p.total)}%` }))];
  }
  function cardMeta(s) {
    const links = [];
    if (safeHref(s.card)) links.push(h("a", { href: s.card, target: "_blank", rel: "noopener noreferrer" }, "card"));
    if (safeHref(s.pr)) links.push(h("a", { href: s.pr, target: "_blank", rel: "noopener noreferrer" }, "PR"));
    return h("div", { class: "meta" },
      s.priority && s.priority.level ? h("span", { class: "chip" }, "P" + s.priority.level) : null,
      s.complexity ? h("span", { class: "chip" }, s.complexity) : null,
      s.run && s.run.state ? h("span", {
        class: "chip run" + (s.run.state === "failed" || s.run.state === "blocked" || s.run.verifier === "fail" ? " run-bad" : ""),
        title: "last runner step" + (s.run.date ? " on " + s.run.date : "") }, "run: " + s.run.state + (s.run.verifier ? " / " + s.run.verifier : "")) : null,
      s.subject ? h("span", { class: "chip" }, s.subject) : null,
      s.tags.map((t) => h("span", { class: "chip" }, "#" + t)),
      s.assignee ? h("span", {}, "@" + s.assignee) : null,
      progress(s.progress), links);
  }
  function card(s) {
    return h("article", { class: "card" },
      h("a", { class: "title", href: "#/spec/" + s.id }, `${s.id} · ${s.title || "(untitled)"}`),
      s.summary ? h("div", { class: "meta" }, s.summary) : null, cardMeta(s));
  }
  function filtered() {
    const f = state.filters;
    return state.specs.filter((s) =>
      (!f.subject || s.subject === f.subject) && (!f.tag || s.tags.includes(f.tag)) &&
      (!f.type || s.workItemType === f.type) && (!f.assignee || s.assignee === f.assignee) &&
      (!f.complexity || s.complexity === f.complexity));
  }
  function viewBoard() {
    const specs = filtered();
    return [filterBar(), h("div", { class: "board" }, state.stages.map((stage) => {
      const col = specs.filter((s) => s.stage === stage);
      return h("section", { class: "col", "aria-label": stage },
        h("h2", {}, h("span", {}, stage), h("span", {}, col.length)),
        col.length ? col.map(card) : h("p", { class: "empty" }, "nothing here"));
    }))];
  }
  function distinct(key) {
    const set = new Set();
    state.specs.forEach((s) => (key === "tag" ? s.tags : [s[key === "type" ? "workItemType" : key]]).forEach((v) => v && set.add(v)));
    return [...set].sort();
  }
  function filterBar() {
    const mk = (key, label) => h("label", {}, label,
      h("select", { on: { change: (e) => { state.filters[key] = e.target.value; render(); } } },
        h("option", { value: "" }, "all"),
        distinct(key).map((v) => h("option", { value: v, selected: state.filters[key] === v }, v))));
    return h("div", { class: "filters", role: "group", "aria-label": "Filters" },
      mk("subject", "Subject"), mk("tag", "Tag"), mk("type", "Type"), mk("assignee", "Assignee"), mk("complexity", "Complexity"));
  }
  function anyFilter() { return Object.values(state.filters).some(Boolean); }

  function stagePill(stage) {
    return h("span", { class: "chip stage-" + stage }, stage);
  }

  function viewList() {
    const plans = state.specs.filter((s) => s.phase === "plans").sort((a, b) => a.rank - b.rank);
    const visible = filtered().filter((s) => s.phase === "plans").sort((a, b) => a.rank - b.rank);
    const canDrag = state.writable && !anyFilter();
    let dragId = null;
    const rows = visible.map((s, idx) => {
      const tr = h("tr", { draggable: canDrag, "data-id": s.id,
        on: {
          dragstart: (e) => { dragId = s.id; tr.classList.add("dragging"); e.dataTransfer.effectAllowed = "move"; e.dataTransfer.setData("text/plain", String(s.id)); },
          dragend: () => tr.classList.remove("dragging"),
          dragover: (e) => { if (dragId != null) { e.preventDefault(); tr.classList.add("over"); } },
          dragleave: () => tr.classList.remove("over"),
          drop: (e) => { e.preventDefault(); tr.classList.remove("over"); if (dragId != null && dragId !== s.id) move(plans, dragId, s.id); dragId = null; },
        } },
        h("td", { class: "num" }, s.rank),
        h("td", {}, h("a", { href: "#/spec/" + s.id }, `${s.id} · ${s.title}`)),
        h("td", {}, stagePill(s.stage)), h("td", {}, cardMeta(s)),
        h("td", { class: "grip" },
          h("button", { type: "button", disabled: !canDrag || idx === 0, "aria-label": `Move ${s.id} up`, on: { click: () => step(plans, s.id, -1) } }, "▲"),
          h("button", { type: "button", disabled: !canDrag || idx === visible.length - 1, "aria-label": `Move ${s.id} down`, on: { click: () => step(plans, s.id, 1) } }, "▼")));
      return tr;
    });
    return [filterBar(),
      !state.writable ? h("p", { class: "empty" }, "Reordering is disabled (read-only).")
        : anyFilter() ? h("p", { class: "empty" }, "Clear the filters to reorder: the ranking is global.") : h("p", { class: "empty" }, "Drag a row, or use the arrows, to change priority. One reorder is one commit where the backend supports it."),
      h("table", {}, h("thead", {}, h("tr", {}, ["#", "Spec", "Stage", "Details", "Move"].map((t) => h("th", { scope: "col" }, t)))),
        h("tbody", {}, rows))];
  }
  async function move(plans, fromId, toId) {
    const order = plans.map((s) => s.id).filter((id) => id !== fromId);
    order.splice(order.indexOf(toId), 0, fromId);
    await reorder(order);
  }
  async function step(plans, id, delta) {
    const order = plans.map((s) => s.id), i = order.indexOf(id), j = i + delta;
    if (j < 0 || j >= order.length) return;
    [order[i], order[j]] = [order[j], order[i]];
    await reorder(order, id);
  }
  async function reorder(order, focusId) {
    try {
      const r = await api("reorder", { body: { order } });
      toast(`Reordered: ${r.written} spec(s) written${r.batched ? " in one commit" : ""}`, true);
    } catch (e) { fail(e); }
    await load(true); await render();
    if (focusId != null) { const b = document.querySelector(`tr[data-id="${focusId}"] button:not(:disabled)`); if (b) b.focus(); }
  }

  // A cross-repository id (`owner/repo#id`) has no detail in this store: it is shown, never linked.
  const isRemoteId = (id) => /[\/#]/.test(String(id));
  function epicItem(it, critical) {
    const on = critical.includes(it.label);
    return h("li", { class: "wave-item" + (on ? " critical" : ""), "data-label": it.label },
      h("div", {}, h("strong", {}, it.label), " ", it.spec && !isRemoteId(it.spec) ? h("a", { href: "#/spec/" + it.spec }, it.title) : it.title),
      h("div", { class: "meta" }, h("span", { class: "chip st-" + it.status }, it.status), on ? h("span", { class: "chip crit" }, "critical path") : null),
      it.after.length ? h("div", { class: "meta" }, "after: " + it.after.join(", ") + (it.waitingOn.length ? " (waiting on " + it.waitingOn.join(", ") + ")" : "")) : null);
  }

  function viewEpics() {
    return state.epics.epics.map((e) => h("section", { class: "panel" },
      h("div", { class: "sechead" }, h("h2", {}, h("a", { href: "#/spec/" + e.id }, `${e.id} · ${e.title}`)), h("span", {}, `${e.done}/${e.total} done`)),
      e.total ? h("div", { class: "meta" }, h("span", { class: "bar", role: "img", "aria-label": `${e.done} of ${e.total} children archived` }, h("i", { style: `width:${Math.round(100 * e.done / e.total)}%` }))) : h("p", { class: "empty" }, "no children yet"),
      e.cycle ? h("p", { class: "bad", role: "alert" }, "Dependency cycle: " + e.cycle.join(" → ")) : null,
      e.criticalPath.length ? h("p", { class: "meta" }, "Critical path: " + e.criticalPath.join(" → ")) : null,
      e.items.length
        ? h("div", { class: "waves" }, e.groups.map((g) => h("div", { class: "wave" },
          h("h3", {}, `Wave ${g.group}${g.title ? " · " + g.title : ""}`, " ", h("span", { class: "meta" }, `${g.done}/${g.total}`)),
          h("ul", {}, e.items.filter((it) => it.group === g.group).map((it) => epicItem(it, e.criticalPath))))))
        : h("ul", {}, e.children.map((c) => h("li", {}, h("a", { href: "#/spec/" + c.id }, `${c.id} · ${c.title}`), " ", stagePill(c.stage))))));
  }

  /* ── sessões ao vivo (only under `serve --sessions`) ─────────────────────── */
  function isWaiting(s) { return s.state === "waiting" || s.status === "waiting"; }
  function sessionLabel(s) {
    const w = s.worktree;
    if (w && w.branch) return w.branch + (w.main ? " (main checkout)" : "");
    return (s.cwd || "").split("/").filter(Boolean).pop() || s.sessionId;
  }
  function paintSessionsCount() {
    const n = state.sessions ? state.sessions.sessions.filter(isWaiting).length : 0;
    $("#sessions-count").textContent = n;
    $("#sessions-count").classList.toggle("hot", n > 0);
  }
  function since(iso) {
    if (!iso) return "";
    const m = Math.max(0, Math.round((Date.now() - Date.parse(iso)) / 60000));
    return m < 1 ? "just now" : m < 60 ? m + " min ago" : Math.floor(m / 60) + " h ago";
  }
  function radar(activity) {
    const peak = Math.max(1, ...activity);
    const total = activity.reduce((a, b) => a + b, 0);
    return h("div", { class: "radar", role: "img", "aria-label": `${total} events in the last ${activity.length} minutes` },
      activity.map((n) => h("i", { class: n ? "on" : "", style: `height:${n ? Math.max(12, Math.round(100 * n / peak)) : 4}%` })));
  }
  function subLane(sa, winStart, winMs) {
    const at = (iso, fallback) => Math.min(1, Math.max(0, ((iso ? Date.parse(iso) : fallback) - winStart) / winMs));
    const from = at(sa.start, winStart), to = at(sa.end, winStart + winMs);
    return h("div", { class: "sublane" },
      h("span", { class: "sublabel" }, sa.agentType || "sub-agent", sa.active ? h("span", { class: "chip st-in-progress" }, "active") : null),
      h("div", { class: "track", role: "img", "aria-label": `${sa.agentType || "sub-agent"} from ${sa.start || "?"} to ${sa.end || "now"}` },
        h("i", { class: sa.active ? "span active" : "span", style: `left:${(100 * from).toFixed(1)}%;width:${Math.max(0.8, 100 * (to - from)).toFixed(1)}%` })));
  }
  function viewSessions() {
    const ss = state.sessions;
    if (!ss) return h("p", { class: "empty" }, "The live sessions could not be read.");
    const waiting = ss.sessions.filter(isWaiting);
    const winMs = ss.windowMinutes * 60000;
    const winStart = Date.parse(ss.generatedAt) - winMs;
    return [
      h("section", { class: "panel waiting" },
        h("div", { class: "sechead" }, h("h2", {}, "Esperando você"), h("span", {}, waiting.length)),
        waiting.length ? h("ul", { class: "humanlist" }, waiting.map((s) => h("li", {},
          h("strong", {}, sessionLabel(s)), " ", h("span", { class: "meta" }, "since " + since(s.statusSince || s.lastEvent)),
          s.pendingTool ? h("span", { class: "chip" }, s.pendingTool) : null,
          h("blockquote", { class: "question" }, s.pendingQuestion || "(waiting, no question text)"))))
          : h("p", { class: "empty" }, "no session is waiting for you")),
      h("section", { class: "panel" },
        h("div", { class: "sechead" }, h("h2", {}, `Sessões · last ${ss.windowMinutes} min`), h("span", {}, ss.sessions.length)),
        ss.sessions.length ? ss.sessions.map((s) => h("div", { class: "lane" + (isWaiting(s) ? " hot" : "") },
          h("div", { class: "lanehead" },
            h("strong", {}, sessionLabel(s)), " ", h("span", { class: "chip ss-" + s.state }, s.state),
            h("span", { class: "meta" }, "last event " + (since(s.lastEvent) || "never"))),
          radar(s.activity || []),
          (s.subagents || []).map((sa) => subLane(sa, winStart, winMs))))
          : h("p", { class: "empty" }, "no live session in this repository's worktrees"))];
  }

  /* ── chat (only under `serve --chat`): one read-only `claude -p` job, polled ── */
  const CHAT_POLL_MS = 1500;
  const CHAT_DONE = ["done", "failed", "timeout"];
  function chatTrees() {
    const p = state.projects && state.projects.find((x) => x.name === state.project);
    return p ? p.worktrees || [] : [];
  }
  function chatLog() {
    const c = state.chat;
    const items = c.events.map((ev) =>
      ev.kind === "tool" ? h("li", { class: "chat-tool" }, "ferramenta: ", h("code", {}, ev.name))
        : ev.kind === "result" ? h("li", { class: "chat-result" + (ev.isError ? " bad" : "") }, h("strong", {}, "Resposta"), h("div", { class: "chat-text" }, ev.text || ""))
          : h("li", { class: "chat-text" }, ev.text || ""));
    const tail = [];
    if (c.job && !CHAT_DONE.includes(c.status)) tail.push(h("p", { class: "meta", role: "status" }, "rodando…"));
    if (c.status && c.status !== "running") tail.push(h("p", { class: "meta" }, "estado: " + c.status));
    if (c.error) tail.push(h("p", { class: "bad" }, c.error));
    if (c.cost != null) tail.push(h("p", { class: "meta" }, `custo: US$ ${Number(c.cost).toFixed(4)}`));
    return h("div", { id: "chat-log", "aria-live": "polite" }, items.length ? h("ol", { class: "chat-events" }, items) : null, tail);
  }
  function paintChatLog() {
    const old = $("#chat-log");
    if (old) old.replaceWith(chatLog());
    const send = $("#chat-send");
    if (send) send.disabled = !!state.chat.job && !CHAT_DONE.includes(state.chat.status);
  }
  async function pollChat(job) {
    const c = state.chat;
    while (c.job === job && !CHAT_DONE.includes(c.status)) {
      await new Promise((r) => setTimeout(r, CHAT_POLL_MS));
      if (c.job !== job) return;
      let r;
      try { r = await api(`chat/${encodeURIComponent(job)}?after=${c.next}`); }
      catch (e) { c.status = "failed"; c.error = e.message; paintChatLog(); return; }
      c.events.push(...(r.events || [])); c.next = r.next; c.status = r.status;
      c.error = r.error || ""; c.cost = r.costUsd;
      paintChatLog();
    }
  }
  async function askChat(e) {
    e.preventDefault();
    const c = state.chat;
    const question = c.draft.trim();
    if (!question) return;
    const body = { question };
    if (c.worktree) body.worktree = c.worktree;
    let r;
    try { r = await api("chat", { body }); } catch (err) { fail(err); return; }
    Object.assign(c, { job: r.job, status: "running", events: [], next: 0, cost: null, error: "" });
    paintChatLog();
    pollChat(r.job);
  }
  function viewChat() {
    const c = state.chat;
    const trees = chatTrees();
    if (c.worktree && !trees.some((w) => w.path === c.worktree)) c.worktree = "";
    return h("section", { class: "panel chat" },
      h("div", { class: "sechead" }, h("h2", {}, "Chat"),
        h("span", { class: "meta" }, "só leitura (Read, Grep, Glob)" + (state.chatBudget != null ? ` · teto US$ ${state.chatBudget}` : ""))),
      h("form", { class: "chat-form", on: { submit: askChat } },
        trees.length ? h("label", {}, "Worktree",
          h("select", { on: { change: (ev) => { c.worktree = ev.target.value; } } },
            trees.map((w) => h("option", { value: w.main ? "" : w.path, selected: (w.main ? "" : w.path) === c.worktree, title: w.path },
              (w.branch || "(detached)") + (w.main ? " · main" : ""))))) : null,
        h("label", {}, "Pergunta",
          h("textarea", { maxLength: 4000, required: true, value: c.draft, on: { input: (ev) => { c.draft = ev.target.value; } } })),
        h("div", { class: "actions" }, h("button", { type: "submit", class: "primary", id: "chat-send" }, "Perguntar"))),
      chatLog());
  }

  /* ── decidir com o humano ────────────────────────────────────────────────── */
  function paintHumanCount() {
    const n = state.human ? state.human.count : 0;
    $("#human-count").textContent = n;
    $("#human-count").classList.toggle("hot", n > 0);
    document.title = (n > 0 ? `(${n}) ` : "") + (state.project ? state.project + " — " : "") + "Quenching specs";
    const c = document.createElement("canvas");
    c.width = c.height = 32;
    const g = c.getContext && c.getContext("2d");
    if (!g) return;
    g.fillStyle = n > 0 ? "#b4410a" : "#5f5c56";
    g.beginPath(); g.arc(16, 16, 15, 0, 2 * Math.PI); g.fill();
    g.fillStyle = "#ffffff"; g.font = "bold 20px sans-serif"; g.textAlign = "center"; g.textBaseline = "middle";
    g.fillText(n > 99 ? "99" : String(n), 16, 17);
    $("#favicon").href = c.toDataURL("image/png");
  }
  let drawerOpener = null;
  function closeDrawer() {
    const d = $("#drawer");
    if (d.hidden) return;
    d.hidden = true; d.replaceChildren();
    if (drawerOpener && drawerOpener.isConnected) drawerOpener.focus();
    drawerOpener = null;
  }
  async function openDrawer(id, opener) {
    drawerOpener = opener;
    const d = $("#drawer");
    let det;
    try { det = await api("specs/" + encodeURIComponent(id)); } catch (e) { fail(e); return; }
    const problem = det.sections.find((x) => x.heading === "Problem");
    d.replaceChildren(
      h("div", { class: "sechead" }, h("h2", { id: "drawer-title" }, `${det.spec.id} · ${det.spec.title}`),
        h("button", { type: "button", id: "drawer-close", on: { click: closeDrawer } }, "Close (Esc)")),
      h("div", { class: "meta" }, stagePill(det.spec.stage), " ", h("a", { href: "#/spec/" + det.spec.id }, "open the whole spec")),
      h("h3", {}, "Problem"),
      problem && problem.state !== "absent" ? markdown(problem.body) : h("p", { class: "empty" }, "no Problem written"));
    d.hidden = false;
    $("#drawer-close").focus();
  }
  function humanRow(id, title, stage, extra, label) {
    const btn = id && !isRemoteId(id) ? h("button", { type: "button", class: "link", on: { click: (e) => openDrawer(id, e.currentTarget) } }, `${id} · ${title}`) : h("span", {}, `${id || label || "?"} · ${title}`);
    return h("li", {}, btn, " ", stagePill(stage), extra);
  }
  function viewHuman() {
    const hu = state.human;
    if (!hu) return h("p", { class: "empty" }, "The waiting list could not be read.");
    const list = (title, rows, empty) => h("section", { class: "panel" },
      h("div", { class: "sechead" }, h("h2", {}, title), h("span", {}, rows.length)),
      rows.length ? h("ul", { class: "humanlist" }, rows) : h("p", { class: "empty" }, empty));
    return [
      h("div", { class: "hero", role: "status" }, h("strong", { class: "heronum" }, hu.count),
        h("span", {}, hu.count === 1 ? "spec waits for the human" : "specs wait for the human")),
      list("Open in human-decision epics", hu.epicMembers.map((m) => humanRow(m.id, m.title, m.stage, h("span", { class: "meta" }, ` epic ${m.epic} · ${m.label}`), m.label)), "no open decision"),
      list("Blocked tasks", hu.blocked.map((b) => humanRow(b.id, b.title, b.stage, h("div", { class: "bad" }, b.reasons.map((r) => `${r.task}: ${r.reason || "(no reason)"}`).join("; ")))), "nothing blocked"),
      list("Ready, awaiting approval", hu.awaitingApproval.map((r) => humanRow(r.id, r.title, r.stage)), "nothing to approve")];
  }

  async function viewDetail(id) {
    let d;
    try { d = await api("specs/" + encodeURIComponent(id)); } catch (e) { fail(e); return h("p", { class: "empty" }, "Spec not found."); }
    const s = d.spec;
    const write = state.writable;
    const cmd = d.executeCommand;
    const left = [
      h("div", { class: "panel" },
        h("h2", {}, `${s.id} · ${s.title}`), cardMeta(s),
        h("div", { class: "actions" },
          h("button", { type: "button", on: { click: async () => { try { await navigator.clipboard.writeText(cmd); toast("Copied: " + cmd, true); } catch (e) { toast(cmd, true); } } } }, "Copy execute command"),
          s.phase === "plans" ? h("button", { type: "button", class: "primary", disabled: !write || !!s.approved, title: s.approved ? "already approved" : "records approved by: human",
            on: { click: () => approve(s.id) } }, s.approved ? "Approved" : "Approve") : null,
          h("button", { type: "button", disabled: !write, on: { click: () => discoveryDialog(s.id) } }, "Add discovery"))),
      d.sections.map((sec) => h("section", { class: "panel" },
        h("div", { class: "sechead" }, h("h3", {}, sec.heading),
          h("button", { type: "button", disabled: !write, on: { click: () => sectionDialog(s.id, sec) } }, "Edit")),
        sec.state === "absent" ? h("p", { class: "empty" }, "absent") : markdown(sec.body)))];
    const right = [
      h("section", { class: "panel" }, h("h3", {}, `Tasks ${s.progress.checked}/${s.progress.total}`),
        d.tasks.length ? h("ul", { class: "tasks" }, d.tasks.map((t) => h("li", {},
          h("input", { type: "checkbox", disabled: true, checked: t.checked, "aria-label": t.state }), " ", t.text,
          t.blocked ? h("span", { class: "bad" }, ` blocked: ${t.reason || ""}`) : null,
          t.verify ? h("span", { class: "verify" }, "verify: " + (Array.isArray(t.verify) ? t.verify.join("; ") : t.verify)) : null,
          t.commit ? h("span", { class: "verify" }, "commit " + t.commit) : null))) : h("p", { class: "empty" }, "no tasks yet")),
      h("section", { class: "panel" }, h("h3", {}, "Records"),
        d.timeline.length ? h("ol", { class: "timeline" }, d.timeline.map((r) => h("li", {}, h("b", {}, r.record),
          typeof r.value === "object" ? Object.entries(r.value).map(([k, v]) => `${k}: ${v}`).join(", ") : String(r.value))))
          : h("p", { class: "empty" }, "no records yet")),
    ];
    return h("div", {}, h("p", {}, h("a", { href: "#/board" }, "← back")), h("div", { class: "detail" }, h("div", {}, left), h("aside", {}, right)));
  }
  async function approve(id) {
    if (!confirm(`Approve spec ${id}? This records "approved by: human".`)) return;
    try { await api("approve", { body: { spec: id } }); toast("Approved by: human", true); }
    catch (e) { fail(e); }
    await load(true); await render();
  }

  /* ── dialogs ─────────────────────────────────────────────────────────────── */
  function openDialog(title, fields, submitLabel, onSubmit) {
    const dlg = $("#dlg");
    const form = h("form", { method: "dialog", on: { submit: async (e) => {
      e.preventDefault();
      const values = {};
      fields.forEach((f) => { values[f.name] = form.elements[f.name].value; });
      try { await onSubmit(values); dlg.close(); } catch (err) { fail(err); }
    } } },
      h("h2", { id: "dlg-title" }, title),
      fields.map((f) => h("label", {}, f.label, f.multiline
        ? h("textarea", { name: f.name, required: !!f.required, value: f.value || "" })
        : h("input", { type: "text", name: f.name, required: !!f.required, value: f.value || "" }))),
      h("div", { class: "actions" },
        h("button", { type: "button", on: { click: () => dlg.close() } }, "Cancel"),
        h("button", { type: "submit", class: "primary" }, submitLabel)));
    dlg.replaceChildren(form);
    dlg.showModal();
    const first = form.querySelector("input,textarea"); if (first) first.focus();
  }
  function captureDialog() {
    openDialog("Capture a spec", [{ name: "title", label: "Title", required: true }, { name: "problem", label: "Problem", multiline: true, required: true }], "Capture",
      async (v) => { const r = await api("capture", { body: v }); toast(`Captured #${r.id}`, true); await load(true); location.hash = "#/spec/" + r.id; await render(); });
  }
  function sectionDialog(id, sec) {
    openDialog(`Edit ## ${sec.heading}`, [{ name: "body", label: "Markdown body", multiline: true, value: sec.body }], "Save",
      async (v) => { await api("section", { body: { spec: id, heading: sec.heading, body: v.body } }); toast("Section saved", true); await load(true); await render(); });
  }
  function discoveryDialog(id) {
    openDialog("Add a discovery", [{ name: "text", label: "What did you find?", required: true }], "Add",
      async (v) => { await api("discovery", { body: { spec: id, text: v.text } }); toast("Discovery recorded", true); await load(true); await render(); });
  }

  /* ── search ──────────────────────────────────────────────────────────────── */
  async function viewSearch(q) {
    let r;
    try { r = await api("search?q=" + encodeURIComponent(q)); } catch (e) { fail(e); return h("p", {}, "Search failed."); }
    return h("section", { class: "panel" }, h("h2", {}, `${r.count} result(s) for "${q}"`),
      h("ul", {}, r.results.map((x) => h("li", {}, h("a", { href: "#/spec/" + x.id }, `${x.id} · ${x.title}`), " ", stagePill(x.stage), x.snippet ? h("div", { class: "meta" }, "…" + x.snippet + "…") : null))));
  }

  /* ── projects: only `cq portal serve` answers /api/projects; `cq specs serve` 404s it ── */
  async function loadProjects() {
    let r;
    try { r = await api("projects"); } catch (e) { return; }
    if (!r || !Array.isArray(r.projects) || !r.projects.length) return;
    state.projects = r.projects;
    const kept = localStorageGet("qproject");
    const chosen = r.projects.find((p) => p.name === kept) || r.projects[0];
    state.project = chosen.name; state.base = chosen.prefix;
    paintProjects();
  }
  function paintProjects() {
    const nav = $("#projects");
    const pick = (p) => ({ click: () => switchProject(p) });
    nav.replaceChildren(h("h2", {}, "Projetos"), h("ul", {}, state.projects.map((p) => h("li", {},
      h("button", { type: "button", class: "project", "aria-current": p.name === state.project ? "true" : false, on: pick(p) }, p.name),
      h("ul", { class: "trees", "aria-label": "Worktrees de " + p.name }, (p.worktrees || []).map((w) => h("li", {},
        h("button", { type: "button", class: "tree", title: w.path, on: pick(p) },
          (w.branch || "(detached)") + (w.main ? " · main" : "")))))))));
    nav.hidden = false;
  }
  async function switchProject(p) {
    if (p.name === state.project) return;
    state.project = p.name; state.base = p.prefix; localStorageSet("qproject", p.name);
    state.human = null; state.sessions = null;
    Object.assign(state.chat, { worktree: "", job: null, status: "", events: [], next: 0, cost: null, error: "" });
    paintProjects();
    await loadConfig();
    try { await load(true); } catch (e) { fail(e); }
    if (location.hash && !/^#\/?(board)?$/.test(location.hash)) location.hash = "#/board";
    else await render();
  }

  /* ── router ──────────────────────────────────────────────────────────────── */
  async function render() {
    closeDrawer();
    const route = location.hash.replace(/^#\/?/, "") || "board";
    const [view, arg] = route.split("/");
    document.querySelectorAll("#nav a").forEach((a) => { if (a.dataset.view === view) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current"); });
    let content;
    if (view === "spec") content = await viewDetail(decodeURIComponent(arg || ""));
    else if (view === "search") content = await viewSearch(decodeURIComponent(arg || ""));
    else if (view === "list") content = viewList();
    else if (view === "human") content = viewHuman();
    else if (view === "epics" && state.epics.supported) content = viewEpics();
    else if (view === "sessions" && state.sessionsOn) content = viewSessions();
    else if (view === "chat" && state.chatOn) content = viewChat();
    else content = viewBoard();
    $("#main").replaceChildren(...[content].flat());
    if (view === "chat") paintChatLog();
  }

  /* ── boot ────────────────────────────────────────────────────────────────── */
  $("#refresh").addEventListener("click", () => refresh(true));
  $("#capture").addEventListener("click", captureDialog);
  $("#search-form").addEventListener("submit", (e) => { e.preventDefault(); const q = $("#q").value.trim(); if (q) location.hash = "#/search/" + encodeURIComponent(q); });
  window.addEventListener("hashchange", () => { render().then(() => $("#main").focus()); });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeDrawer();
    if (e.key === "/" && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) { e.preventDefault(); $("#q").focus(); }
  });
  setInterval(tickFreshness, 1000);
  $("#notify").addEventListener("click", toggleNotify);
  paintNotify();
  /* 8 s: just above the server's 5 s cache; a 304 makes each unchanged poll nearly free, and a
     hidden tab keeps polling so the title, the favicon and the notification still move. */
  setInterval(() => { if (!$("#dlg").open) refresh(false); }, 8000);

  (async () => {
    await loadProjects();
    await loadConfig();
    try { await load(false); } catch (e) { fail(e); }
    await render();
  })();
})();
