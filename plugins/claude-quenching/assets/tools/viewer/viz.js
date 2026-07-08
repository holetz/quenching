/*
  OKF bundle viewer behaviour — adapted from
  okf/src/reference_agent/viewer/static/viz.js in
  https://github.com/GoogleCloudPlatform/knowledge-catalog (Apache-2.0).
  Added: combined search+type+home filtering, a clickable colour legend, home/
  timestamp rows, linkmap-driven internal navigation, and empty-bundle handling.
  Reads window.BUNDLE / window.BUNDLE_NAME injected by okf-visualize.py.
*/
(function () {
  const bundle = window.BUNDLE || {};
  const bundleName = window.BUNDLE_NAME || "docs";
  const nodes = bundle.nodes || [];
  const edges = bundle.edges || [];
  const bodies = bundle.bodies || {};
  const linkmaps = bundle.linkmaps || {};
  const palette = bundle.palette || {};

  document.title = `${bundleName} — OKF Viewer`;
  document.getElementById("bundle-name").textContent = bundleName;
  document.getElementById("counts").textContent =
    `${nodes.length} concept(s) · ${edges.length} link(s)`;

  // Populate the type + home filters.
  const typeSelect = document.getElementById("filter-type");
  for (const t of bundle.types || []) {
    const opt = document.createElement("option");
    opt.value = t; opt.textContent = t;
    typeSelect.appendChild(opt);
  }
  const homeSelect = document.getElementById("filter-home");
  for (const h of bundle.homes || []) {
    const opt = document.createElement("option");
    opt.value = h; opt.textContent = h;
    homeSelect.appendChild(opt);
  }

  // Reverse-link index (backlinks) and node lookup.
  const backlinks = {};
  for (const edge of edges) {
    const { source, target } = edge.data;
    (backlinks[target] ||= []).push(source);
  }
  const nodeIndex = {};
  for (const n of nodes) nodeIndex[n.data.id] = n.data;

  const graphEl = document.getElementById("graph");
  if (!nodes.length) {
    document.getElementById("empty-graph").hidden = false;
    renderLegend();
    return;
  }

  const cy = cytoscape({
    container: graphEl,
    elements: [...nodes, ...edges],
    style: [
      { selector: "node", style: {
        "background-color": "data(color)",
        "label": "data(label)",
        "color": "#0f172a",
        "font-size": 11,
        "text-valign": "bottom",
        "text-margin-y": 4,
        "text-wrap": "wrap",
        "text-max-width": 120,
        "width": "data(size)",
        "height": "data(size)",
        "border-width": 1,
        "border-color": "#0f172a",
      } },
      { selector: "node:selected", style: { "border-width": 3, "border-color": "#f59e0b" } },
      { selector: "edge", style: {
        "width": 1.5,
        "line-color": "#cbd5e1",
        "target-arrow-color": "#cbd5e1",
        "target-arrow-shape": "triangle",
        "curve-style": "bezier",
        "arrow-scale": 0.9,
      } },
      { selector: "edge:selected", style: {
        "line-color": "#f59e0b", "target-arrow-color": "#f59e0b", "width": 2.5,
      } },
      { selector: ".dim", style: { "opacity": 0.12 } },
    ],
    layout: { name: "cose", animate: false, padding: 30 },
    wheelSensitivity: 0.2,
  });

  cy.on("tap", "node", (evt) => showDetail(evt.target.id()));
  cy.on("tap", (evt) => { if (evt.target === cy) clearSelection(); });

  document.getElementById("layout").addEventListener("change", (e) => {
    cy.layout({ name: e.target.value, animate: false, padding: 30 }).run();
  });
  document.getElementById("reset").addEventListener("click", () => {
    cy.fit(null, 30);
    clearSelection();
  });

  // Combined filter: a node shows only if it clears search + type + home + legend.
  const hiddenTypes = new Set();
  document.getElementById("search").addEventListener("input", applyFilters);
  typeSelect.addEventListener("change", applyFilters);
  homeSelect.addEventListener("change", applyFilters);

  function applyFilters() {
    const q = document.getElementById("search").value.trim().toLowerCase();
    const type = typeSelect.value;
    const home = homeSelect.value;
    cy.nodes().forEach((n) => {
      const d = n.data();
      const hay = (d.label || "").toLowerCase() + " " + d.id.toLowerCase() + " " +
        (d.tags || []).join(" ").toLowerCase();
      const hide =
        (q && !hay.includes(q)) ||
        (type && d.type !== type) ||
        (home && d.home !== home) ||
        hiddenTypes.has(d.type);
      n.toggleClass("dim", hide);
    });
    cy.edges().forEach((edge) => {
      edge.toggleClass("dim", edge.source().hasClass("dim") || edge.target().hasClass("dim"));
    });
  }

  renderLegend();

  function renderLegend() {
    const el = document.getElementById("legend");
    if (!el) return;
    const types = bundle.types || [];
    if (!types.length) { el.hidden = true; return; }
    const title = document.createElement("div");
    title.className = "legend-title";
    title.textContent = "Type";
    el.appendChild(title);
    for (const t of types) {
      const row = document.createElement("div");
      row.className = "row";
      row.dataset.type = t;
      const sw = document.createElement("span");
      sw.className = "swatch";
      sw.style.background = palette[t] || "#64748b";
      const label = document.createElement("span");
      label.textContent = t;
      row.appendChild(sw);
      row.appendChild(label);
      row.addEventListener("click", () => {
        if (hiddenTypes.has(t)) { hiddenTypes.delete(t); row.classList.remove("off"); }
        else { hiddenTypes.add(t); row.classList.add("off"); }
        if (typeof applyFilters === "function") applyFilters();
      });
      el.appendChild(row);
    }
  }

  function clearSelection() {
    cy.elements().unselect();
    document.getElementById("detail-empty").hidden = false;
    document.getElementById("detail-content").hidden = true;
  }

  function setRow(id, value) {
    const el = document.getElementById(id);
    el.textContent = value && String(value).trim() ? value : "—";
  }

  function showDetail(conceptId) {
    const data = nodeIndex[conceptId];
    if (!data) return;
    cy.elements().unselect();
    const node = cy.getElementById(conceptId);
    if (node) node.select();

    document.getElementById("detail-empty").hidden = true;
    document.getElementById("detail-content").hidden = false;

    const chip = document.getElementById("detail-type");
    chip.textContent = data.type;
    chip.style.background = data.color;

    document.getElementById("detail-title").textContent = data.label;
    document.getElementById("detail-id").textContent = conceptId;
    setRow("detail-description", data.description);
    setRow("detail-home", data.home);
    setRow("detail-timestamp", data.timestamp);

    const resourceEl = document.getElementById("detail-resource");
    resourceEl.innerHTML = "";
    if (data.resource) {
      const a = document.createElement("a");
      a.href = data.resource;
      a.textContent = data.resource;
      a.target = "_blank";
      a.rel = "noopener";
      a.className = "external";
      resourceEl.appendChild(a);
    } else {
      resourceEl.textContent = "—";
    }

    const tagsEl = document.getElementById("detail-tags");
    tagsEl.innerHTML = "";
    if (data.tags && data.tags.length) {
      for (const t of data.tags) {
        const span = document.createElement("span");
        span.className = "tag";
        span.textContent = t;
        tagsEl.appendChild(span);
      }
    } else {
      tagsEl.textContent = "—";
    }

    const body = bodies[conceptId] || "";
    const bodyEl = document.getElementById("detail-body");
    bodyEl.innerHTML = (typeof marked !== "undefined")
      ? marked.parse(body, { breaks: false, gfm: true })
      : "";
    rewriteInternalLinks(bodyEl, conceptId);

    const bl = backlinks[conceptId] || [];
    const blSection = document.getElementById("detail-backlinks");
    const blList = document.getElementById("backlinks-list");
    blList.innerHTML = "";
    if (bl.length) {
      blSection.hidden = false;
      for (const src of bl) {
        const li = document.createElement("li");
        const a = document.createElement("a");
        a.textContent = nodeIndex[src]?.label || src;
        a.addEventListener("click", () => showDetail(src));
        li.appendChild(a);
        const muted = document.createElement("span");
        muted.className = "muted";
        muted.textContent = ` (${src})`;
        li.appendChild(muted);
        blList.appendChild(li);
      }
    } else {
      blSection.hidden = true;
    }

    if (node) cy.animate({ center: { eles: node }, zoom: Math.max(cy.zoom(), 1.0) }, { duration: 200 });
  }

  // Rewrite body links: a raw href the generator resolved to a concept node
  // (linkmaps[conceptId]) becomes internal navigation; everything else opens out.
  function rewriteInternalLinks(root, conceptId) {
    const lm = linkmaps[conceptId] || {};
    root.querySelectorAll("a[href]").forEach((a) => {
      const href = a.getAttribute("href");
      if (!href) return;
      const bare = href.split("#")[0];
      const target = lm[href] || lm[bare];
      if (target && nodeIndex[target]) {
        a.className = "internal";
        a.setAttribute("href", "javascript:void(0)");
        a.addEventListener("click", (e) => { e.preventDefault(); showDetail(target); });
        return;
      }
      a.className = "external";
      a.setAttribute("target", "_blank");
      a.setAttribute("rel", "noopener");
    });
  }

  // Auto-show the first concept.
  if (nodes[0]) showDetail(nodes[0].data.id);
})();
