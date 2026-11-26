/* Aba Configuração: leitura do schema do `cq config` (GET /api/settings). Somente leitura —
   nenhuma escrita parte daqui. Script próprio, carregado antes do app.js, que o chama por
   window.QuenchingSettings.view({ h, api, emptyState }). Monta o DOM só por h() e não guarda token. */
(function () {
  "use strict";
  const SOURCES = { default: "padrão", user: "usuário", repository: "projeto", local: "local", branch: "branch" };
  const fmt = (v) => (v === null || v === undefined ? "—" : typeof v === "string" ? v : JSON.stringify(v));

  function keyRow(h, row, got, layerPaths) {
    const copy = row.copy["pt-BR"] || row.copy.en;
    const source = got ? got.source : "default";
    const path = got && got.path ? got.path : null;
    const home = row.scope === "project" ? layerPaths.project : row.scope === "machine" ? layerPaths.local : null;
    const text = [row.key, copy.title, copy.summary, row.reader].join(" ").toLowerCase();
    return h("li", { class: "cfg-row", "data-search": text },
      h("div", { class: "cfg-head" },
        h("code", { class: "cfg-key" }, row.key),
        h("span", { class: "chip" }, row.type),
        h("span", { class: "chip" }, "escopo: " + row.scope),
        row.editable ? null : h("span", { class: "chip" }, "somente leitura")),
      h("p", { class: "cfg-title" }, copy.title),
      h("p", { class: "cfg-summary" }, copy.summary),
      h("dl", { class: "cfg-facts" },
        h("dt", {}, "Valor efetivo"), h("dd", {}, h("code", {}, fmt(got ? got.value : row.default))),
        h("dt", {}, "Padrão"), h("dd", {}, h("code", {}, fmt(row.default))),
        h("dt", {}, "Origem"), h("dd", {}, (SOURCES[source] || source) + (path ? " · " + path : "")),
        home ? [h("dt", {}, "Mora em"), h("dd", {}, home)] : null,
        h("dt", {}, "Lido por"), h("dd", {}, row.reader || "—")));
  }

  async function view(ctx) {
    const { h, api, emptyState } = ctx;
    let data;
    try { data = await api("settings"); } catch (e) { data = null; }
    if (!data || !data.ok) {
      return emptyState("Configuração indisponível", "O servidor não devolveu o schema do cq config.");
    }
    const layerPaths = data.layerPaths || {};
    const values = data.values || {};
    const status = h("p", { class: "meta", role: "status" }, `${data.keys.length} chaves`);
    const input = h("input", { type: "search", class: "cfg-search", "aria-label": "Buscar chave de configuração",
      placeholder: "Buscar por chave, título ou descrição…", autocomplete: "off", spellcheck: false });
    const sections = data.categories.map((cat) => {
      const rows = data.keys.filter((k) => k.category === cat.id);
      const list = h("ul", { class: "cfg-list" }, rows.map((r) => keyRow(h, r, values[r.key], layerPaths)));
      const title = cat.title["pt-BR"] || cat.title.en;
      return h("details", { class: "cfg-cat", open: true },
        h("summary", {}, title, " ", h("span", { class: "meta" }, String(rows.length))), list);
    });
    input.addEventListener("input", () => {
      const q = input.value.trim().toLowerCase();
      let shown = 0;
      sections.forEach((sec) => {
        let any = 0;
        sec.querySelectorAll(".cfg-row").forEach((li) => {
          const hit = !q || li.getAttribute("data-search").includes(q);
          li.hidden = !hit;
          if (hit) any += 1;
        });
        sec.hidden = any === 0;
        shown += any;
      });
      status.textContent = `${shown} de ${data.keys.length} chaves`;
    });
    return h("section", { class: "cfg", "aria-label": "Configuração" },
      h("div", { class: "sechead" }, h("h2", {}, "Configuração"), status),
      h("p", { class: "cfg-intro" },
        "Leitura do schema do ", h("code", {}, "cq config"), ": cada chave, o valor em vigor, a camada que o forneceu e o arquivo onde mora. ",
        "Para alterar, use ", h("code", {}, "cq config set"), " — o portal não grava configuração."),
      h("p", { class: "cfg-files" }, "Arquivos: ", h("code", {}, layerPaths.project || "—"), " (projeto) · ", h("code", {}, layerPaths.local || "—"), " (local)"),
      input, sections);
  }
  window.QuenchingSettings = { view };
})();
