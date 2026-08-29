# Documentation validation — strict build and honest rendered QA

The runbook for validating the generated site. It builds into the gitignored `site_dir` and reports
`unverified` when the toolchain is unavailable; it never claims a visual check that did not happen.

## Contents

`cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-documentation/validation.md`
returns the heading index; `--sections <name>` addresses one.

<!-- rules -->

## Strict build

Run from the target repository root using the project's existing dependency manager:

```bash
uv run zensical build --clean --strict
```

Use `uv run` when `pyproject.toml`/`uv.lock` is present and declares Zensical. Otherwise the
fallbacks are `python -m zensical build --clean --strict` and
`zensical build --clean --strict`. There is no per-run output flag: the build writes to the configured `site_dir`, which is
gitignored, and `.cache/` beside the config ignores itself. Where `site/` is **tracked**,
overwriting it would be destructive — write a throwaway config **at the repo root** with its
`site_dir` outside the repo, build it with `-f`, and delete the config after; a config parked
anywhere else resolves `docs_dir` relative to itself and exits `Error: Docs directory does not
exist`. Never run `zensical serve` from this command and never commit a built site.

`--strict` must be zero-issue. Link validation is on by default — `invalid_links` and
`invalid_link_anchors` — so it catches dangling links and dead anchors, and `--strict` turns them
into an abort. A warning is either fixed in the site layer or reported to the page-owning command.

## Editorial publication map

Read the accepted `### Mapa editorial de publicação` before judging navigation or links. Inventory
all `/docs/` homes and use every `publicar`/`publicar derivado` row as the mandatory
coverage denominator. For every such row, prove that its declared route is built under `site/` and
is non-empty; for every `não publicar` row, prove that no matching nav entry, published route or
link exists. A
curated route under `documentation/` is valid; `docs_dir = "docs"` is not a substitute,
because a dot-prefixed root yields **zero** rendered pages while still exiting `0` — measured, with
the evidence in `external/tools/zensical-measured-behaviour.md`.

```bash
# compare plan rows with generated routes; replace <route> with each mapped route
test -f "site/<route>/index.html"
rg -n 'href="[^"]*<unpublished-home>' site
```

The second command must return no match. A bundle path such as `/docs/standards/...` is never
evidence of a published route: validate the mapped URL instead.

## Static rendered checks

Run the structural verifier **after every strict build, unconditionally**; it is the no-browser gate for missing assets,
anchors, sitemap URLs, orphan pages and remote resources:

```bash
python3 <plugin>/assets/checks/documentation-site-check.py site
```

When the canonical glossary exists and the map does not explicitly say `não publicar`, first
verify the deterministic source projection and then pass the same contract to the rendered check:

```bash
cq knowledge project docs --plan .quenching/documentation/plan.md --config zensical.toml --check
python3 <plugin>/assets/checks/documentation-site-check.py site \
  --require-glossary \
  --glossary-source docs/glossary.md \
  --glossary-route reference/glossary.md \
  --glossary-snippet docs/documentation/assets/glossary-abbreviations.md
```

The projection check compares the route and abbreviation snippet with the canonical file's
SHA-256, and the rendered check requires a known term to appear inside `<abbr>`. For a local-only
site with no `site_url`, add `--local`: relative or empty sitemap locations are acceptable there,
but malformed XML and missing page/assets still fail. A local run never proves public delivery.

Quando houver catálogo derivado, rode também o verificador de projeção para provar que o índice de
camada/schema alcança cada detalhe e que a linhagem mínima está presente:

```bash
python3 <plugin>/assets/checks/catalog-publication-check.py docs/documentation
```

O fixture executável `catalog-publication/healthy` mantém a regressão mínima (`id`, `layer`,
`schema` e `lineage`) sem transformar cada item em uma entrada de navegação.

Para cada capacidade habilitada no registro, inspecione o HTML renderizado com a fixture de efeitos:

```bash
python3 <plugin>/assets/checks/zensical-capability-check.py \
  site --enabled autorefs,mkdocstrings,preview,tags,provenance
```

The capability checker accepts either one HTML file or the built site directory; directory mode
scans all rendered pages, so passing `.` or `site/` cannot fail merely because the argument is a
directory.

O verificador exige uma âncora de heading, assinatura de API, URL loopback, atributo de tags e
bloco de proveniência conforme a lista habilitada. Capacidades desabilitadas não são incluídas no
comando e não podem ser tratadas como sucesso implícito.

Planos, ledgers, scorecards `review-<n>.md` e `report.md` são artefatos operacionais: devem viver
em `.quenching/documentation/`, fora de `docs_dir`, e não podem ser alcançados por uma rota
publicada. A validação registra cada `source gap:` no relatório de QA, mas nunca o promove a uma
página para “completar” cobertura.

### Baseline de escala do catálogo

A medição local de 27/08/2026 usou 100 detalhes (101 arquivos incluindo o índice): o verificador
completo levou `0,03 s` e a busca de linhagem via `rg` menos de `0,01 s`. Esses números são apenas
um baseline reprodutível, não um limite de produto; o limite de publicação continua uma decisão
editorial quando o volume real ultrapassar essa ordem de grandeza.

`site-asset-missing`, `site-anchor-missing`, `site-sitemap-empty` and `site-page-orphan` fail the
gate. Until vendoring is deliberately adopted, `site-remote-resource` is a **warning** by default;
run `--remote-policy error` for a target that requires offline operation. Both forms enumerate every
origin and neither claims the site works offline. When a browser or Playwright is available, inspect the landing and one deep page at desktop and
narrow widths in both palettes. Otherwise run the static fallback over the built HTML:

```bash
grep -oE '<title>[^<]*</title>' site/index.html | head -1
grep -R -c 'class="mermaid"' site
grep -R -c 'class="q-badge"' site
grep -oE 'stylesheets/[^" ]+' site/index.html | sort -u
grep -R -Eo 'prefers-reduced-motion' docs/documentation/assets/stylesheets/*.css
```

The static fallback verifies title, Mermaid markup, badges, CSS wiring, the motion guard and mapped
routes. It
does not prove pixel-level dark/light/mobile layout; report that limitation and recommend a
manual browser pass. Check that cards reflow, contrast is readable, tabs switch, and Mermaid is
not a raw code block when a browser is available.

## Required rendered effects

The build report checks the page title, `class="mermaid"`, `class="q-badge"`, connected
`extra_css`, `prefers-reduced-motion`, every mapped route and the absence of unpublished homes.
Custom colors use the theme's own `--md-*` variables or both schemes; animations have a
reduced-motion off switch.

<!-- rationale -->

A green parser run proves markup, not pixels. Separating strict build from static and browser QA
keeps the report precise while retaining a useful no-browser fallback.
