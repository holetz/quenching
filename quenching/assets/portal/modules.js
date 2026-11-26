/* Aba Módulos: módulos do quenching, versão instalada contra a da fonte e o plano do deploy
   (GET /api/modules e /api/deploy-plan). Somente leitura — nenhuma escrita parte daqui e o portal
   não roda deploy: a aba mostra o comando `cq deploy` e quem o roda é o humano. Script próprio,
   carregado antes do app.js, que o chama por window.QuenchingModules.view({ h, api, emptyState }).
   Monta o DOM só por h() e não guarda token. */
(function () {
  "use strict";
  const CHANGES = { create: "criar", update: "atualizar", delete: "remover", edited: "editado no alvo",
    adopt: "adotar", mode: "modo", settings: "settings", mcp: "mcp", manifest: "manifesto", seed: "semente" };

  function moduleRow(h, row) {
    return h("li", { class: "mod-row" },
      h("div", { class: "mod-head" },
        h("code", { class: "mod-name" }, row.name),
        h("span", { class: row.installed ? "chip mod-on" : "chip" }, row.installed ? "instalado" : "disponível"),
        row.core ? h("span", { class: "chip" }, "núcleo") : null),
      h("p", { class: "mod-meta" }, "Skills: ", row.skills.length ? row.skills.join(", ") : "—"),
      h("p", { class: "mod-meta" }, "Pacotes: ", row.packages.length ? row.packages.join(", ") : "—"));
  }

  function planBlock(h, plan) {
    if (!plan || !plan.changes) {
      return h("p", { class: "meta", role: "status" }, "Plano indisponível: o servidor não o devolveu.");
    }
    const items = plan.changes.map((c) => h("li", { class: "mod-change" },
      h("span", { class: "chip" }, CHANGES[c.change] || c.change), " ", h("code", {}, c.path)));
    const notes = [...(plan.conflicts || []).map((c) => c.path + " — " + c.why), ...(plan.warnings || [])];
    return h("div", { class: "mod-plan" },
      h("p", { class: "meta", role: "status" },
        plan.changes.length ? `${plan.changes.length} mudança(s) num deploy` : "Nada a mudar: o alvo está em dia com a fonte."),
      items.length ? h("ul", { class: "mod-changes" }, items) : null,
      notes.length ? h("ul", { class: "mod-notes" }, notes.map((n) => h("li", {}, n))) : null);
  }

  async function view(ctx) {
    const { h, api, emptyState } = ctx;
    let mods, plan;
    try { mods = await api("modules"); } catch (e) { mods = null; }
    try { plan = await api("deploy-plan"); } catch (e) { plan = null; }
    if (!mods || !mods.ok) {
      return emptyState("Módulos indisponíveis", "O servidor não devolveu o registro de módulos.");
    }
    const behind = mods.installedVersion && mods.installedVersion !== mods.version;
    const versions = mods.deployed
      ? `Instalado: ${mods.installedVersion || "—"} · Fonte: ${mods.version}` + (behind ? " · há atualização" : " · em dia")
      : `Este alvo não tem deploy do quenching (fonte ${mods.version}).`;
    return h("section", { class: "mod", "aria-label": "Módulos" },
      h("div", { class: "sechead" }, h("h2", {}, "Módulos"),
        h("p", { class: "meta", role: "status" }, `${mods.installed.length} de ${mods.modules.length} instalados`)),
      h("p", { class: "mod-intro" }, "Leitura do registro de módulos e do plano do ", h("code", {}, "cq deploy"),
        ". O portal não instala nem atualiza nada: rode o comando abaixo no terminal."),
      h("p", { class: "mod-versions" }, versions),
      h("p", { class: "mod-meta" }, "Fonte: ", h("code", {}, mods.source)),
      h("h3", {}, "Comando"),
      h("pre", { class: "mod-command" }, h("code", {}, mods.command)),
      h("h3", {}, "Plano do deploy"),
      planBlock(h, plan),
      h("h3", {}, "Módulos"),
      h("ul", { class: "mod-list" }, mods.modules.map((m) => moduleRow(h, m))));
  }
  window.QuenchingModules = { view };
})();
