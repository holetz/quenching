"""The portal assets' contract: no HTML strings, no secret in the client, and the UX surface.

`test_specs_portal.py` proves the server and pins the few strings the client must keep. This file
pins the rest of the asset contract: the shape of the shell, the views, the keyboard, the board,
the detail, the live layer and the Gantt. A failure names the missing behaviour, not the file.
"""

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


class Budget(unittest.TestCase):
    def test_the_assets_stay_inside_the_weight_budget(self):
        self.assertLess((ROOT / "app.js").stat().st_size, 120 * 1024)
        self.assertLess((ROOT / "app.css").stat().st_size, 48 * 1024)
        self.assertLess((ROOT / "index.html").stat().st_size, 12 * 1024)


if __name__ == "__main__":
    unittest.main()
