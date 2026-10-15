"use strict";
/* Quenching spec portal. No build, no CDN, no innerHTML: every node is created with
   textContent, so spec text can never inject markup. */
(() => {
  const params = new URLSearchParams(location.search);
  const TOKEN = params.get("token") || sessionStorageGet("qtoken") || "";
  if (TOKEN) { sessionStorageSet("qtoken", TOKEN); }
  if (params.has("token")) history.replaceState(null, "", location.pathname + location.hash);

  function sessionStorageGet(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }
  function sessionStorageSet(k, v) { try { sessionStorage.setItem(k, v); } catch (e) { /* private mode */ } }

  const $ = (s) => document.querySelector(s);
  const state = { specs: [], stages: [], fetchedAt: 0, ttl: 5, writable: false, why: "",
                  filters: { subject: "", tag: "", type: "", assignee: "", complexity: "" },
                  epics: { supported: false, epics: [] }, busy: false };

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

  async function api(path, opts = {}) {
    const init = { method: opts.body ? "POST" : "GET", headers: { "X-Quenching-Token": TOKEN } };
    if (opts.body) { init.headers["Content-Type"] = "application/json"; init.body = JSON.stringify(opts.body); }
    let res, data;
    try { res = await fetch("/api/" + path, init); data = await res.json(); }
    catch (e) { throw { code: "network", message: "the portal server is not reachable" }; }
    if (!res.ok || data.ok === false) throw { code: data.code || "http-" + res.status, message: data.message || res.statusText, data };
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
    const data = await api("specs" + (refresh ? "?refresh=1" : ""));
    state.specs = data.specs; state.stages = data.stages; state.ttl = data.ttlSeconds;
    state.fetchedAt = data.fetchedAt * 1000;
    try {
      const ep = await api("epics");
      state.epics = ep;
    } catch (e) { state.epics = { supported: false, epics: [] }; }
    $("#nav-epics").hidden = !state.epics.supported;
    tickFreshness();
  }
  async function loadConfig() {
    try {
      const c = await api("config");
      state.writable = c.writable; state.why = c.readOnlyReason;
    } catch (e) { fail(e); }
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
    try { await load(force); await render(); } catch (e) { fail(e); } finally { $("#refresh").disabled = false; }
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
        h("td", {}, s.stage), h("td", {}, cardMeta(s)),
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

  function viewEpics() {
    return state.epics.epics.map((e) => h("section", { class: "panel" },
      h("div", { class: "sechead" }, h("h2", {}, h("a", { href: "#/spec/" + e.id }, `${e.id} · ${e.title}`)), h("span", {}, `${e.done}/${e.total} done`)),
      e.total ? h("div", { class: "meta" }, h("span", { class: "bar", role: "img", "aria-label": `${e.done} of ${e.total} children archived` }, h("i", { style: `width:${Math.round(100 * e.done / e.total)}%` }))) : h("p", { class: "empty" }, "no children yet"),
      h("ul", {}, e.children.map((c) => h("li", {}, h("a", { href: "#/spec/" + c.id }, `${c.id} · ${c.title}`), " ", h("span", { class: "chip" }, c.stage))))));
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
      h("ul", {}, r.results.map((x) => h("li", {}, h("a", { href: "#/spec/" + x.id }, `${x.id} · ${x.title}`), " ", h("span", { class: "chip" }, x.stage), x.snippet ? h("div", { class: "meta" }, "…" + x.snippet + "…") : null))));
  }

  /* ── router ──────────────────────────────────────────────────────────────── */
  async function render() {
    const route = location.hash.replace(/^#\/?/, "") || "board";
    const [view, arg] = route.split("/");
    document.querySelectorAll("#nav a").forEach((a) => { if (a.dataset.view === view) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current"); });
    let content;
    if (view === "spec") content = await viewDetail(decodeURIComponent(arg || ""));
    else if (view === "search") content = await viewSearch(decodeURIComponent(arg || ""));
    else if (view === "list") content = viewList();
    else if (view === "epics" && state.epics.supported) content = viewEpics();
    else content = viewBoard();
    $("#main").replaceChildren(...[content].flat());
  }

  /* ── boot ────────────────────────────────────────────────────────────────── */
  $("#refresh").addEventListener("click", () => refresh(true));
  $("#capture").addEventListener("click", captureDialog);
  $("#search-form").addEventListener("submit", (e) => { e.preventDefault(); const q = $("#q").value.trim(); if (q) location.hash = "#/search/" + encodeURIComponent(q); });
  window.addEventListener("hashchange", () => { render().then(() => $("#main").focus()); });
  document.addEventListener("keydown", (e) => {
    if (e.key === "/" && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) { e.preventDefault(); $("#q").focus(); }
  });
  setInterval(tickFreshness, 1000);
  setInterval(() => { if (!document.hidden && !$("#dlg").open) refresh(false); }, 30000);

  (async () => {
    if (!TOKEN) { $("#main").replaceChildren(h("p", { class: "bad" }, "Open the URL printed by `cq specs serve`: it carries the access token.")); return; }
    await loadConfig();
    try { await load(false); } catch (e) { fail(e); }
    await render();
  })();
})();
