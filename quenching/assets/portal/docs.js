/* Aba Docs: links de navegação (manual, índice, padrão de configuração, site) e o catálogo de
   comandos derivado das descrições das skills instaladas (GET /api/docs). Somente leitura — o
   portal não serve arquivos nem grava nada: a aba mostra caminhos relativos ao alvo e, para o
   site, o link declarado no zensical.toml. Script próprio, carregado antes do app.js, que o chama
   por window.QuenchingDocs.view({ h, api, emptyState }). Monta o DOM só por h() e não guarda token. */
(function () {
  "use strict";

  function publishedUrl(link) {
    return !link.exists && typeof link.url === "string" && /^https:\/\//i.test(link.url) ? link.url : "";
  }

  function linkRow(h, link) {
    const url = publishedUrl(link);
    return h("li", { class: "doc-row" },
      h("span", { class: "doc-label" }, link.label),
      h("code", { class: "doc-path" }, link.path),
      h("span", { class: link.exists ? "chip doc-on" : "chip" }, link.exists ? "presente" : "ausente"),
      url ? h("a", { href: url, target: "_blank", rel: "noopener noreferrer" }, "versão publicada") : null);
  }

  function commandRow(h, cmd) {
    return h("li", { class: "doc-cmd" },
      h("div", { class: "doc-head" },
        h("code", { class: "doc-name" }, "/" + cmd.name),
        cmd.flows.map((f) => h("span", { class: "chip" }, f))),
      h("p", { class: "doc-desc" }, cmd.description));
  }

  async function view(ctx) {
    const { h, api, emptyState } = ctx;
    let data;
    try { data = await api("docs"); } catch (e) { data = null; }
    if (!data || !data.ok) {
      return emptyState("Docs indisponíveis", "O servidor não devolveu os links nem o catálogo de comandos.");
    }
    const site = data.site
      ? h("p", { class: "doc-site" }, "Site: ",
        h("a", { href: data.site, target: "_blank", rel: "noopener noreferrer" }, data.site))
      : h("p", { class: "doc-site" }, "Site: sem ", h("code", {}, "site_url"), " no ", h("code", {}, "zensical.toml"), " deste alvo.");
    return h("section", { class: "doc", "aria-label": "Docs" },
      h("div", { class: "sechead" }, h("h2", {}, "Docs"),
        h("p", { class: "meta", role: "status" }, `${data.commands.length} comando(s) instalado(s)`)),
      h("p", { class: "doc-intro" }, "Pontos de partida do alvo e o catálogo de comandos lido das skills instaladas. ",
        "O portal não abre nem edita arquivos: abra os caminhos no editor."),
      h("h3", {}, "Links"),
      h("ul", { class: "doc-list" }, data.links.map((l) => linkRow(h, l))),
      site,
      h("h3", {}, "Catálogo de comandos"),
      data.commands.length
        ? h("ul", { class: "doc-list" }, data.commands.map((c) => commandRow(h, c)))
        : h("p", { class: "meta" }, "Nenhuma skill instalada em .claude/skills ou .agents/skills."));
  }
  window.QuenchingDocs = { view };
})();
