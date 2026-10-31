The specs portal is where one person supervises many agents: a local, keyboard-first cockpit over the specs store. It is an operating surface, used for hours beside a terminal. This system is the target for its refinement. Build new work from these tokens and classes, and treat the `Screen*` cards as the destination of each view.

## The one rule

Heat marks what waits for the human. `accent` is spent on exactly two things: the one primary action of a view, and whatever needs a person now (the `Decidir` count, an approval, unsent writes, a session asking a question). If a screen is calm, nothing on it needs you; if it burns, the orange tells you where. Everything else is ink and paper.

- Never use `accent` for the current nav item, a pressed toggle, a selected row or a link. Those are `ink`.
- Never use `bad` for attention. It means something failed or is blocked.
- Keep one `button.primary` per view. A row action that needs the human is `button.heat`, the outlined form.

## Content

The interface speaks pt-BR, the portal's declared language; this documentation is English, like the rest of the repository.

- Write sentence case, always. Uppercase labels are retired, so `Em execução`, not `EM EXECUÇÃO`.
- Translate every state. The store's keys never reach a person: `executing` reads `em execução`, `in-progress` reads `em andamento`, `busy` reads `ocupada`, and `done / not-run` reads `feito, sem verificador`. The vocabulary is **etapa**, never estágio.
- Controls name their action with a verb: `Aprovar`, `Capturar`, `Copiar comando`, `Registrar descoberta`.
- Errors name the problem and the remedy: “Conflito com o remoto: rode `cq specs push` no terminal.”
- Be plain about what the portal is. Copy states facts, in the portal's own words: “Nada aqui inventa dado: cada número sai do servidor.” No exclamation marks, no emoji.
- Dates are relative and short (`há 3 d`), with the full date in the `title`.

## Color

`bg` is warm paper and `surface` is the white sheet on it; `surface-2` and `surface-3` are the neutral layers for hover and press. `ink` carries text, `muted` carries everything secondary. Both themes are warm: dark is charcoal, never blue-grey.

- Stage is told by a mark, not a fill. `.stage` is an 8px square in `stage-*` beside the word. The tinted `.chip.stage-*` is for the one place a stage is the subject, the head of a spec.
- `stage-*` colours are marks and lane rules. They never set text; text on a stage tint uses its `stage-*-ink` pair.
- `line` is decoration only, at 1.4:1. Anything a person operates has a `control-line` edge at 3:1.
- `focus` is the only blue in the chrome, so the ring is never mistaken for a state.

## Type

The system stack, on purpose: the portal ships no font, no CDN and no build. Hierarchy comes from weight and from `step-*`, and the scale is fixed, never fluid.

- `t-view` heads a view, `t-section` a section, `t-strong` a card or row title. Body is `t-body`, metadata `t-small`, table heads and form labels `t-label`.
- `font-mono` is for data that is code: spec ids, wave labels, commits, branches, commands. It never decorates a label.
- All counts, ages and progress use tabular numerals.

## Layout

The shell is fixed and the content scrolls. `.app` is a grid of top bar (48px), pulse (34px), optional banner, the work area and the status bar (30px). The board lanes scroll one by one under a header that never leaves, so the toolbar stays reachable with sixty cards in a lane.

- Spacing comes from `space-1` to `space-8`, tight inside a group and generous between groups.
- `radius-1` for what you press, `radius-2` for panels, `radius-3` for dialogs, `radius-0` for tags. `radius-pill` is for count badges only.
- Lines separate; shadows float. `shadow-1` is a hovered card and `shadow-2` is anything over the page. A panel never sits inside a panel, and a card lives on a lane, not in a box.
- Never add a coloured left edge to a card, row, toast or quote. State is a mark or a word.
- Density has two settings, `comfortable` and `compact`, set on `html[data-density]`; they rescale `space-*` and `step-*`.

## Motion and states

Motion is 120 to 200ms on `--ease` and it only reports a state change. Every interactive part has hover, focus, active and disabled; every view has loading, empty and error. The first paint is a skeleton of the real shape, an empty state teaches the next step, and a failed read says so and offers `Tentar de novo`. Destructive or irreversible actions arm in place (`.triage.is-armed`) instead of opening a browser `confirm()`.

## Iconography

One authored set of 16px line icons at 1.5 stroke with round caps, shown in the `Icons` card, drawn as inline SVG by `createElementNS` so the CSP stays intact. Paths live in `ICONS` in `design-system/build.py`. Use `.i`; colour comes from `currentColor`. Unicode glyphs never stand in for icons. There is no logo file: the mark is the `.mark` block, a Q on a heat gradient, and the wordmark is plain type.

## Keyboard

The keyboard comes first and every view answers it. `Ctrl K` opens the palette, `/` searches, `?` opens help, `g` then a letter navigates, `j` and `k` move the cursor, `Enter` opens the drawer, `a` approves, `t` cycles the theme, `Esc` closes. The cursor is drawn by `.is-cursor` with the `focus` ring.

## Hard limits

These come from `docs/standards/architecture/specs-portal.md` and hold for everything here.

- No CDN, no external font, no framework, no build step, and no inline `style` attribute in the shipped portal (`style-src 'self'`). Previews use inline custom properties only as a sample; the portal sets them through the CSSOM.
- Every node is built with `createElement` and `textContent`. No `innerHTML`.
- `app.css` under 48 KB, `app.js` under 120 KB, `index.html` under 12 KB. `tokens.css`, `bundle.css` and the auto-theme copy together must stay inside the first; `build.py --check` enforces it.
- The stage is derived. A card never drags between stages, and no view invents a number the server did not send.
- No new write route without a human decision.

## Growing this system

- A new value is a token in `tokens.json`, with a usage note, before it is CSS.
- A new component is a family in `components/bundle.css`, a fragment and a catalogue row in `build.py`, and `components/<Name>/README.md`. Reuse the portal's class name when the concept already exists.
- A new screen is a row in `SCREENS` and in `screen-map.md`, with its status. A target screen uses real fragments and invented sample data, never data from a real store.
- Run `python3 design-system/build.py`, then `--check`. Class, variable, contrast, budget and leak checks all live there.
- A change that departs from the portal's standard goes in `refinement.md` under contract changes.

## Intentional additions

Beyond what `app.css` defines: `control-line` (control borders at 3:1), `heat-tint` and `bad-tint` (fills under accent and bad text), `radius-0` and `radius-pill` (the literals that were repeated), `step--2` (the literal 11px), the `.heat` button, the `.stage` mark, the `.meter` for epics and the icon set.

## Not synced

From `plugins/quenching/assets/portal/app.css`: `--dur-1`, `--dur-2` and `--ease` stay in `components/bundle.css`, because this format has no motion family. The gradient of `.mark` uses `color-mix()` and stays in the stylesheet. No font files exist to bring. The portal has no component library, so previews are plain HTML over `components/bundle.css`, and there is no `bundle.js`.
