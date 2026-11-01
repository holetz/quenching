"""The portal assets' contract: no HTML strings, no secret in the client, and the UX surface.

`test_specs_portal.py` proves the server and pins the few strings the client must keep. This file
pins the rest of the asset contract: the shape of the shell, the views, the keyboard, the board,
the detail, the live layer and the Gantt. A failure names the missing behaviour, not the file.
"""

import json
import pathlib
import re
import sys
import unittest

try:
    import _paths  # noqa: F401  — must precede the `quenching` import
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.specs import portal as portal_mod

ROOT = portal_mod.static_dir()
HTML = (ROOT / "index.html").read_text()
CSS = (ROOT / "app.css").read_text()
JS = (ROOT / "app.js").read_text()
TOKENS = json.loads((ROOT.parents[3] / "design-system" / "tokens.json").read_text(encoding="utf-8"))


def declared(block):
    """The custom properties a CSS block declares, name → value; the last declaration wins."""
    return {name: value.strip() for name, value in re.findall(r"--([\w-]+)\s*:\s*([^;]+);", block)}


def css_block(selector):
    """Declarations of the first `selector { … }` rule whose body holds no nested rule."""
    match = re.search(re.escape(selector) + r"\s*\{([^{}]*)\}", CSS)
    return declared(match.group(1)) if match else {}


def rule(selector):
    """The body of the first rule whose selector is exactly `selector`."""
    match = re.search(r"(?:^|\n)" + re.escape(selector) + r"\s*\{([^{}]*)\}", CSS)
    return match.group(1) if match else ""


WRITES = {"capture", "section", "approve", "reorder", "discovery", "chat", "push"}
READS = {"specs", "epics", "human", "sessions", "schedule", "config", "projects", "search", "chat"}


class Assets(unittest.TestCase):
    def test_the_page_references_only_the_two_local_assets(self):
        refs = re.findall(r'(?:src|href)="([^"]+)"', HTML)
        self.assertTrue(refs)
        for ref in refs:
            with self.subTest(ref=ref):
                self.assertTrue(ref.startswith("#") or ref in ("/app.css", "/app.js", "data:,"), ref)

    def test_the_page_has_no_external_url_and_no_inline_code(self):
        self.assertNotIn("http://", HTML)
        self.assertNotIn("https://", HTML)
        self.assertNotIn("<style", HTML)
        self.assertEqual(len(re.findall(r"<script\b", HTML)), 1)
        self.assertNotIn("<script>", HTML)
        self.assertNotIn('style="', HTML)

    def test_the_page_is_portuguese_and_has_the_landmarks(self):
        self.assertIn('lang="pt-BR"', HTML)
        for needle in ('<header class="top"', '<nav aria-label="Visões" id="nav"',
                       '<main id="main"', '<footer class="statusbar"', 'class="skip"'):
            with self.subTest(needle=needle):
                self.assertIn(needle, HTML)
        self.assertEqual(len(re.findall(r"<h1\b", HTML)), 1)

    def test_the_page_carries_the_three_dialogs(self):
        for needle in ('<dialog id="drawer"', '<dialog id="dlg"', '<dialog id="palette"',
                       '<dialog id="help"', 'role="combobox"', 'role="listbox"',
                       'aria-activedescendant', 'aria-controls="palette-list"',
                       'aria-labelledby="drawer-title"'):
            with self.subTest(needle=needle):
                self.assertIn(needle, HTML)

    def test_the_page_links_every_view_including_the_gantt(self):
        for view in ("board", "list", "human", "epics", "gantt", "sessions", "chat"):
            with self.subTest(view=view):
                self.assertIn(f'data-view="{view}"', HTML)
        self.assertIn('href="#/gantt"', HTML)


class Shell(unittest.TestCase):
    """The document is one `.app` grid: bar, pulse, banners, shell and status, in that order."""

    def app(self):
        return HTML[HTML.index('<div class="app">'):HTML.index('<div id="events"')]

    def test_the_shell_lives_in_one_app_grid(self):
        self.assertEqual(HTML.count('<div class="app">'), 1)
        self.assertIn("</footer>\n</div>", HTML)

    def test_the_five_bands_keep_their_order_inside_the_grid(self):
        app = self.app()
        order = ['<a class="skip"', '<header class="top"', '<section class="pulse"',
                 '<div class="banners">', '<div class="shell">', '<footer class="statusbar"']
        positions = [app.index(needle) for needle in order]
        self.assertEqual(positions, sorted(positions))

    def test_the_banners_sit_inside_the_grid_as_one_band(self):
        app = self.app()
        self.assertIn('id="banner"', app)
        self.assertIn('id="connbanner"', app)

    def test_every_id_is_unique(self):
        ids = re.findall(r'\bid="([^"]+)"', HTML)
        self.assertEqual(len(ids), len(set(ids)))


class Security(unittest.TestCase):
    def test_the_client_builds_no_html_string(self):
        for needle in ("innerHTML", "insertAdjacentHTML", "document.write", "outerHTML"):
            with self.subTest(needle=needle):
                self.assertNotIn(needle, JS)

    def test_the_client_keeps_no_secret_and_no_session_storage(self):
        for needle in ("X-Quenching-Token", "sessionStorage", "?token", 'get("token")'):
            with self.subTest(needle=needle):
                self.assertNotIn(needle, JS)

    def test_the_client_never_evaluates_a_string(self):
        self.assertIsNone(re.search(r"\beval\s*\(", JS))
        self.assertIsNone(re.search(r"\bnew\s+Function\s*\(", JS))

    def test_every_link_passes_through_safe_href(self):
        self.assertIn("function safeHref(url)", JS)
        self.assertGreaterEqual(JS.count("safeHref("), 4)
        self.assertNotIn('href: "http', JS)

    def test_the_client_adds_no_write_route(self):
        found = set(re.findall(r'api\("([a-z0-9/_-]+)"\s*,\s*\{\s*body', JS))
        self.assertEqual(found, WRITES)


class Routes(unittest.TestCase):
    def test_every_api_literal_is_a_known_read_or_write(self):
        routes = {r.split("?")[0].split("/")[0] for r in re.findall(r'api\("([a-z0-9/?=&_-]+)"', JS)}
        self.assertTrue(routes)
        self.assertLessEqual(routes, READS | WRITES)

    def test_the_router_covers_the_views(self):
        for view in ("board", "list", "human", "epics", "gantt", "sessions", "chat", "spec", "search"):
            with self.subTest(view=view):
                self.assertIn(f'view === "{view}"', JS)
        self.assertIn('api("schedule")', JS)

    def test_the_board_state_lives_in_the_url(self):
        self.assertIn("history.replaceState", JS)
        self.assertIn("new URLSearchParams", JS)
        for key in ('p.set("group"', 'p.set("sort"', 'p.set("q"', 'p.append("f"'):
            with self.subTest(key=key):
                self.assertIn(key, JS)

    def test_in_page_anchors_do_not_rerender_the_route(self):
        self.assertIn("function isRouteHash()", JS)
        self.assertIn("location.hash.startsWith", JS)
        self.assertIn('$(".skip")', JS)

    def test_the_search_reads_the_query_and_the_path(self):
        self.assertIn('route.query.get("q") || decodeURIComponent(route.arg', JS)

    def test_the_gantt_state_lives_in_the_url(self):
        for key in ('p.set("zoom"', 'p.set("deps"', 'p.set("crit"'):
            with self.subTest(key=key):
                self.assertIn(key, JS)


class Keyboard(unittest.TestCase):
    def test_the_shortcut_table_covers_the_documented_keys(self):
        for keys in ("Ctrl/Cmd+K", "/", "?", "g b", "g l", "g d", "g e", "g g", "g s",
                     "j / k", "Enter", "Ctrl/Cmd+Enter", "a", "t", "Esc"):
            with self.subTest(keys=keys):
                self.assertIn(f'keys: "{keys}"', JS)

    def test_the_palette_is_a_combobox_and_runs_from_the_keyboard(self):
        for needle in ("ArrowDown", "ArrowUp", "aria-activedescendant", "runPalette",
                       "palette.index", "isSubsequence"):
            with self.subTest(needle=needle):
                self.assertIn(needle, JS)

    def test_the_g_sequence_maps_every_letter(self):
        self.assertIn('map = { b: "board", l: "list", d: "human", e: "epics", g: "gantt", s: "sessions" }', JS)
        self.assertIn("gPending", JS)

    def test_the_keyboard_never_fires_inside_a_field_or_dialog(self):
        self.assertIn("function typingIn(el)", JS)
        self.assertIn('document.querySelector("dialog[open]")', JS)
        self.assertIn("isContentEditable", JS)


class Board(unittest.TestCase):
    def test_the_six_groupings_exist(self):
        for key in ('{ key: "stage"', '{ key: "subject"', '{ key: "priority"',
                    '{ key: "assignee"', '{ key: "complexity"', '{ key: "type"'):
            with self.subTest(key=key):
                self.assertIn(key, JS)

    def test_the_card_carries_state_progress_and_actions(self):
        card = JS[JS.index("function cardMeta(s)"):JS.index("function filtered()")]
        for needle in ('class: "stripe', "progress(s)", "ageLabel(s.date)", "abrir", "copiar comando", "aprovar"):
            with self.subTest(needle=needle):
                self.assertIn(needle, card)

    def test_the_board_does_not_drag_cards_between_stages(self):
        board = JS[JS.index("function card(s)"):JS.index("function viewList()")]
        self.assertNotIn("draggable", board)
        self.assertNotIn("dragstart", board)

    def test_the_control_bar_is_one_row_and_its_panels_open_over_the_lanes(self):
        body = rule(".board-tools")
        self.assertIn("display: flex", body)
        self.assertIn("flex-wrap: wrap", body)
        self.assertIn("min-height: var(--tools-h)", body)
        self.assertNotIn("display: grid", body)
        panel = rule(".pop-body")
        self.assertIn("position: absolute", panel)
        self.assertIn("z-index: 15", panel)
        self.assertIn("box-shadow: var(--shadow-2)", panel)
        self.assertIn("@media (max-width: 1100px) { .chips.quick { display: none; } }", CSS)

    def test_the_filter_chips_appear_only_when_a_filter_is_active(self):
        bar = JS[JS.index("function toolbar()"):JS.index("function labelOfKey(")]
        self.assertIn('h("div", { class: "chips quick" }', bar)
        self.assertRegex(bar, r'chips\.length\s*\?\s*h\("div", \{ class: "chips" \}')
        self.assertEqual(bar.count("limpar tudo"), 1)
        self.assertNotIn("sem filtro", bar)
        self.assertNotIn("empty-inline", bar)
        self.assertIn('"aria-pressed": chips.length ? "true" : "false"', bar)

    def test_the_lane_is_a_stage_rule_with_a_fixed_head_and_its_own_scroll(self):
        col = rule(".col")
        self.assertIn("flex-direction: column", col)
        self.assertIn("min-height: 0", col)
        self.assertIn("border-right: 1px solid var(--line)", col)
        self.assertNotIn("background", col)
        self.assertIn("border-top: 2px solid var(--stage, var(--line))", rule(".col-head"))
        body = rule(".col-body")
        self.assertIn("flex: 1 1 auto", body)
        self.assertIn("overflow-y: auto", body)
        self.assertIn("flex: 0 0 40px", rule(".col.is-collapsed"))
        lane = JS[JS.index("function column(g, gi)"):JS.index("function copyCommand(")]
        self.assertIn('h("h2", { class: "col-head" }', lane)
        self.assertIn('class: "count"', lane)
        self.assertNotIn("col-count", lane)
        self.assertIn("col-empty", lane)

    def test_the_rule_colour_comes_from_the_stage_and_only_from_a_stage_grouping(self):
        lane = JS[JS.index("function column(g, gi)"):JS.index("function copyCommand(")]
        self.assertIn('const stage = state.board.group === "stage" ? String(g.key) : null;', lane)
        self.assertIn('"data-stage": stage', lane)

    def test_the_archived_lane_starts_collapsed_and_the_preference_still_wins(self):
        loader = JS[JS.index("function loadCollapsed("):JS.index("\n  }", JS.index("function loadCollapsed("))]
        self.assertIn('["stage:archived"]', loader)

    def test_priority_and_complexity_are_banded_not_raw_levels(self):
        for needle in ("function priorityBand(", "function priorityShort(", "function complexityOf(",
                       "P1 · crítica", "P4 · baixa", "sem complexidade"):
            with self.subTest(needle=needle):
                self.assertIn(needle, JS)
        self.assertNotIn('"P" + s.priority.level', JS)

    def test_the_columns_collapse_and_saved_views_are_local(self):
        for needle in ("aria-expanded", "toggleCollapse", "q2.", 'return "views."', "savedViews", "prefsSet(viewsKey()"):
            with self.subTest(needle=needle):
                self.assertIn(needle, JS)
        self.assertIn("scroll-snap-type", CSS)


class Detail(unittest.TestCase):
    def test_the_drawer_is_a_modal_dialog_with_focus_return(self):
        for needle in ("showModal()", "drawerOpener", '$("#drawer")', "drawer-title"):
            with self.subTest(needle=needle):
                self.assertIn(needle, JS)

    def test_the_markdown_is_wide_and_safe(self):
        for needle in ('h("blockquote"', 'h("table"', 'h("hr"', 'h("del"', "safeHref(url)"):
            with self.subTest(needle=needle):
                self.assertIn(needle, JS)

    def test_the_tasks_filter_by_state(self):
        for key in ("all", "open", "done", "blocked"):
            with self.subTest(key=key):
                self.assertIn(f'key: "{key}"', JS)
        for needle in ("data-task-filter", "reason", "commit", "verify"):
            with self.subTest(needle=needle):
                self.assertIn(needle, JS)

    def test_the_page_and_the_drawer_share_one_builder(self):
        self.assertIn("function specDetail(d, opts)", JS)
        self.assertEqual(JS.count("specDetail("), 3)


class Live(unittest.TestCase):
    def test_the_connection_has_three_honest_states(self):
        for state in ("live", "unstable", "offline"):
            with self.subTest(state=state):
                self.assertIn(f'"{state}"', JS)
        self.assertIn("function connState()", JS)
        self.assertIn("lastError > state.lastOk", JS)

    def test_the_refresh_can_be_paused_and_says_so(self):
        self.assertIn('$("#pause")', JS)
        self.assertIn('aria-pressed", state.paused', JS)
        self.assertIn('prefsGet("autorefresh"', JS)

    def test_scroll_and_focus_survive_a_poll(self):
        for needle in ("function captureView()", "function restoreView(", "data-fkey", "preventScroll"):
            with self.subTest(needle=needle):
                self.assertIn(needle, JS)

    def test_the_event_centre_and_the_browser_notification_exist(self):
        for needle in ("function logEvent(", "function paintEventList(", "new Notification(",
                       "Notification.requestPermission", "openDrawer(first.id)"):
            with self.subTest(needle=needle):
                self.assertIn(needle, JS)

    def test_the_first_paint_is_a_skeleton_and_failure_is_honest(self):
        for needle in ("function loadingView(", "function skeletonCard(", "function errorView(",
                       'state.loading && !state.specs.length', "loadError ="):
            with self.subTest(needle=needle):
                self.assertIn(needle, JS)
        self.assertIn("Promise.allSettled", JS)

    def test_the_poll_follows_the_last_load_and_skips_hidden_tabs(self):
        for needle in ("function schedulePoll(", "state.lastLoadMs * 2", "document.hidden",
                       "Math.min(60000"):
            with self.subTest(needle=needle):
                self.assertIn(needle, JS)

    def test_a_toast_can_carry_one_action(self):
        self.assertIn("function toast(msg, ok, action)", JS)
        self.assertIn("action.run()", JS)


class Publish(unittest.TestCase):
    def test_the_header_carries_the_publish_button(self):
        self.assertIn('<button id="push" type="button" class="primary" hidden>', HTML)
        self.assertIn('id="push-count"', HTML)

    def test_only_a_writable_store_with_pending_writes_shows_it(self):
        for needle in ("function paintPending(", "state.writable", "p.supported === false",
                       "state.pushing", "b.hidden = true"):
            with self.subTest(needle=needle):
                self.assertIn(needle, JS)
        self.assertIn('$("#push").addEventListener("click", pushNow)', JS)

    def test_the_click_publishes_and_reports_the_cards(self):
        for needle in ('api("push", { body: {} })', "cardFailures", "await load(true); await render();"):
            with self.subTest(needle=needle):
                self.assertIn(needle, JS)

    def test_the_palette_offers_the_publish(self):
        self.assertIn("Enviar ${state.pending.count}", JS)
        self.assertIn("run: pushNow", JS)


class Gantt(unittest.TestCase):
    def test_the_three_zooms_and_today_exist(self):
        self.assertIn("const GANTT_ZOOMS = { day: 26, week: 9, month: 3 }", JS)
        self.assertIn('"Hoje"', JS)

    def test_the_legend_and_the_accessible_table_exist(self):
        for needle in ('class: "legend"', 'class: "gantt-table"', 'h("caption"', '"Caminho crítico"'):
            with self.subTest(needle=needle):
                self.assertIn(needle, JS)

    def test_the_client_does_not_recompute_the_critical_path(self):
        self.assertIn("data.criticalPath", JS)
        self.assertNotIn("criticalPath =", JS)

    def test_the_dependencies_and_the_critical_path_can_be_toggled(self):
        for needle in ('g.deps', 'g.crit', 'aria-pressed'):
            with self.subTest(needle=needle):
                self.assertIn(needle, JS)


class Tokens(unittest.TestCase):
    def test_the_three_token_layers_exist(self):
        for token in ("--surface", "--ink", "--line", "--accent", "--focus",
                      "--stage-ready", "--stage-blocked", "--stage-review"):
            with self.subTest(token=token):
                self.assertIn(token, CSS)

    def test_the_theme_and_the_density_are_switchable(self):
        for needle in ('[data-theme="dark"]', '[data-theme="auto"]', '[data-density="compact"]'):
            with self.subTest(needle=needle):
                self.assertIn(needle, CSS)
        self.assertIn("prefers-color-scheme: dark", CSS)

    def test_the_css_has_no_external_reference(self):
        self.assertNotIn("@import", CSS)
        self.assertNotIn("url(", CSS)

    def test_reduced_motion_and_small_screens_are_handled(self):
        self.assertIn("prefers-reduced-motion", CSS)
        self.assertIn("@media (max-width: 480px)", CSS)
        self.assertIn("@media (max-width: 760px)", CSS)


class TokenBlock(unittest.TestCase):
    """`app.css` carries the design system's tokens verbatim, in all three theme layers."""

    def test_the_block_is_delimited(self):
        self.assertIn("/* ── tokens: generated from design-system/tokens.json ── */", CSS)
        self.assertIn("/* ── end tokens ── */", CSS)

    def test_the_light_block_carries_every_value_from_the_json(self):
        light = css_block(':root, :root[data-theme="light"]')
        self.assertTrue(light)
        for family in ("step", "spacing", "radius"):
            for token in TOKENS[family]["tokens"]:
                with self.subTest(token=token["name"]):
                    self.assertEqual(light.get(token["name"]), token["value"])
        for family, value in TOKENS["type"]["families"].items():
            with self.subTest(token=f"font-{family}"):
                self.assertEqual(light.get(f"font-{family}"), value)
        for family in ("color", "shadow"):
            for token in TOKENS[family]["tokens"]:
                with self.subTest(token=token["name"]):
                    self.assertEqual(light.get(token["name"]), token["value"]["light"])

    def test_the_dark_block_carries_every_dark_value(self):
        dark = css_block(':root[data-theme="dark"]')
        self.assertTrue(dark)
        for family in ("color", "shadow"):
            for token in TOKENS[family]["tokens"]:
                with self.subTest(token=token["name"]):
                    self.assertEqual(dark.get(token["name"]), token["value"]["dark"])

    def test_the_auto_theme_repeats_the_dark_block(self):
        dark = css_block(':root[data-theme="dark"]')
        auto = css_block(':root[data-theme="auto"], :root:not([data-theme])')
        self.assertTrue(dark)
        self.assertTrue(auto)
        self.assertEqual(auto, dark)


class ShellGeometry(unittest.TestCase):
    """The shell is a fixed grid: bar 48, pulse 34, status 30, and `main` is the scroller."""

    def test_the_band_heights_are_the_target_tokens(self):
        root = css_block(":root")
        self.assertEqual(root.get("bar-h"), "48px")
        self.assertEqual(root.get("pulse-h"), "34px")
        self.assertEqual(root.get("tools-h"), "44px")
        self.assertEqual(root.get("status-h"), "30px")

    def test_the_grid_holds_the_five_bands_with_an_elastic_middle(self):
        body = rule(".app")
        self.assertIn("display: grid", body)
        self.assertIn("grid-template-rows: var(--bar-h) var(--pulse-h) auto minmax(0, 1fr) var(--status-h)", body)
        self.assertIn("height: 100dvh", body)
        self.assertIn("overflow: hidden", body)

    def test_main_scrolls_inside_the_shell_and_the_board_keeps_its_own_scroll(self):
        self.assertIn("overflow: auto", rule(".shell main"))
        board = rule("main.is-board")
        self.assertIn("display: flex", board)
        self.assertIn("flex-direction: column", board)
        self.assertIn("overflow: hidden", board)

    def test_the_status_bar_is_a_thirty_pixel_row_not_a_fixed_strip(self):
        body = rule(".statusbar")
        self.assertIn("height: var(--status-h)", body)
        self.assertNotIn("position: fixed", body)
        self.assertNotIn("padding-bottom", rule("body"))

    def test_the_current_nav_item_is_ink_underlined_not_accent(self):
        body = rule('#nav a[aria-current="page"]')
        self.assertIn("color: var(--ink)", body)
        self.assertIn("box-shadow: inset 0 -2px 0 var(--ink)", body)
        self.assertNotIn("accent", body)

    def test_the_pulse_is_a_horizontal_ribbon_of_links(self):
        pulse = rule(".pulse")
        self.assertIn("display: flex", pulse)
        self.assertIn("height: var(--pulse-h)", pulse)
        cell = rule(".pulse-cell")
        self.assertIn("white-space: nowrap", cell)
        self.assertIn("text-decoration: none", cell)


    def test_the_phone_bar_keeps_the_navigation_inside_the_bar(self):
        phone = CSS[CSS.index("@media (max-width: 760px)"):CSS.index("@media (max-width: 480px)")]
        self.assertIn(".brand-sub, #theme, #help-open { display: none; }", phone)
        self.assertIn(".searchbtn kbd { display: none; }", phone)
        self.assertNotIn("position: fixed", phone)


class Primitives(unittest.TestCase):
    """The design system's generic pieces: icon base, heat action, stage mark and control edges."""

    def test_every_variable_the_css_reads_is_declared(self):
        declared_names = set(re.findall(r"--([\w-]+)\s*:", CSS))
        read = set(re.findall(r"var\(--([\w-]+)", CSS))
        self.assertTrue(read)
        self.assertEqual(sorted(read - declared_names), [])

    def test_the_icon_base_is_sixteen_pixels_of_current_color(self):
        body = rule(".i")
        for needle in ("width: 16px", "height: 16px", "fill: none", "stroke: currentColor",
                       "stroke-width: 1.5", "stroke-linecap: round", "stroke-linejoin: round"):
            with self.subTest(needle=needle):
                self.assertIn(needle, body)

    def test_the_heat_action_wears_the_accent_edge_and_the_tint(self):
        self.assertIn("button.heat { background: transparent; color: var(--accent); border-color: var(--accent);", CSS)
        self.assertIn("button.heat:hover { background: var(--heat-tint); }", CSS)

    def test_the_stage_mark_is_an_eight_pixel_square_per_stage(self):
        body = rule(".stage::before")
        self.assertIn("width: 8px", body)
        self.assertIn("height: 8px", body)
        self.assertIn("background: var(--stage", body)
        for stage in ("captured", "ready", "approved", "executing", "blocked", "review", "archived"):
            with self.subTest(stage=stage):
                self.assertIn(f'[data-stage="{stage}"] {{ --stage: var(--stage-{stage}); }}', CSS)

    def test_every_control_borrows_the_control_line(self):
        for selector in ("input[type=search], input[type=text], select, textarea", "button, .ghost", ".fchip"):
            with self.subTest(selector=selector):
                self.assertIn("var(--control-line)", rule(selector))

    def test_disabled_is_neutral_not_a_faded_accent(self):
        body = rule("button:disabled")
        self.assertIn("background: var(--surface-2)", body)
        self.assertIn("color: var(--muted)", body)
        self.assertNotIn("opacity", body)

    def test_tags_take_radius_zero_and_counters_the_pill(self):
        self.assertIn("border-radius: var(--radius-0)", rule(".chip"))
        self.assertIn("border-radius: var(--radius-pill)", rule(".count"))
        self.assertNotIn(".col-count", CSS)


class ShellPaint(unittest.TestCase):
    """The bar carries icons, the pulse is a ribbon of links, and the board owns the scroll."""

    def test_the_nav_draws_the_icon_of_its_view_once(self):
        body = JS[JS.index("function paintNav("):JS.index("\n  }", JS.index("function paintNav("))]
        self.assertIn('a.querySelector("svg.i")', body)
        self.assertIn("icon(a.dataset.view)", body)

    def test_the_pulse_is_a_ribbon_of_links_in_the_target_order(self):
        body = JS[JS.index("function pulseCell("):JS.index("function emptyState(", JS.index("function pulseCell("))]
        order = ['pulseCell("esperando você"', 'pulseCell("bloqueadas"', 'pulseCell("em execução"',
                 'pulseCell("abertas"', 'pulseCell("tarefas"', 'pulseCell("mais antiga"']
        positions = [body.index(needle) for needle in order]
        self.assertEqual(positions, sorted(positions))
        self.assertIn('h("a", { class: "pulse-cell"', body)
        for href in ('"#/human"', '"#/board?f=stage:blocked"', '"#/board?f=stage:executing"', '"#/board"', '"#/list"'):
            with self.subTest(href=href):
                self.assertIn(href, body)

    def test_the_oldest_cell_carries_the_spec_beside_the_value(self):
        body = JS[JS.index("function pulseCell("):JS.index("function emptyState(", JS.index("function pulseCell("))]
        self.assertIn('class: "pulse-spec"', body)
        self.assertIn('class: "pulse-title"', body)

    def test_the_theme_button_draws_its_icon_and_keeps_the_state_in_the_label(self):
        self.assertNotIn("THEME_GLYPH", JS)
        self.assertIn('icon("theme")', JS)
        self.assertIn("Tema: ${THEME_LABEL[t]} (t alterna)", JS)

    def test_the_board_view_takes_the_elastic_main(self):
        self.assertIn('main.className = route.view === "board" ? "is-board" : ""', JS)

    def test_the_status_bar_paints_its_icons_and_keeps_the_pause_state(self):
        body = JS[JS.index("function paintPause("):JS.index("\n  }", JS.index("function paintPause("))]
        self.assertIn('icon("pause")', body)
        self.assertIn('aria-pressed", state.paused', body)
        for needle in ('$("#refresh").prepend(icon("refresh"))', '$("#events-open").prepend(icon("bell"))'):
            self.assertIn(needle, JS)


class Icons(unittest.TestCase):
    """One authored 16px set in `ICONS`, drawn through `createElementNS` by `icon(name)`."""

    def icons(self):
        block = JS[JS.index("const ICONS = {"):JS.index("\n  };", JS.index("const ICONS = {"))]
        return {name: re.findall(r'"([^"]+)"', paths) for name, paths in re.findall(r"(\w+): \[([^\]]*)\]", block)}

    def test_every_icon_is_a_non_empty_list_of_paths(self):
        icons = self.icons()
        self.assertTrue(icons)
        for name, paths in icons.items():
            with self.subTest(icon=name):
                self.assertTrue(paths)
                for d in paths:
                    self.assertTrue(d.startswith(("M", "m")), d)

    def test_the_shell_and_the_board_have_their_icons(self):
        icons = self.icons()
        for name in ("board", "list", "human", "epics", "gantt", "sessions", "chat", "search",
                     "theme", "help", "plus", "filter", "down", "right", "up", "x", "copy",
                     "panel", "pause", "refresh", "bell", "alert", "check"):
            with self.subTest(icon=name):
                self.assertIn(name, icons)

    def test_the_helper_draws_an_inline_svg_without_markup(self):
        body = JS[JS.index("function icon(name)"):JS.index("\n  }", JS.index("function icon(name)"))]
        self.assertIn('svg("svg", { class: "i", viewBox: "0 0 16 16", "aria-hidden": "true" }', body)
        self.assertIn("svg(", body)
        self.assertIn("createElementNS", JS)


class Budget(unittest.TestCase):
    def test_the_assets_stay_inside_the_weight_budget(self):
        self.assertLess((ROOT / "app.js").stat().st_size, 120 * 1024)
        self.assertLess((ROOT / "app.css").stat().st_size, 48 * 1024)
        self.assertLess((ROOT / "index.html").stat().st_size, 12 * 1024)


if __name__ == "__main__":
    unittest.main()
