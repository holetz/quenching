---
name: Quenching Portal
description: A local, keyboard-first cockpit where one person supervises many agents
colors:
  accent: "#b4410a"
  accent-ink: "#ffffff"
  heat-tint: "#fbe9dd"
  bg: "#f5f4f0"
  surface: "#ffffff"
  surface-2: "#efece5"
  surface-3: "#e3dfd5"
  ink: "#1b1a17"
  muted: "#5f5b53"
  line: "#dcd8cf"
  control-line: "#8a857b"
  ok: "#1f6f43"
  warn: "#8a5a00"
  bad: "#a3231f"
  focus: "#1558d6"
typography:
  view:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "20px"
    fontWeight: 700
    lineHeight: "26px"
  section:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "16px"
    fontWeight: 600
    lineHeight: "22px"
  strong:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 600
    lineHeight: "20px"
  body:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: "21px"
  small:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: "17px"
  label:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "11px"
    fontWeight: 600
    lineHeight: "14px"
  id:
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: "16px"
rounded:
  radius-0: "4px"
  radius-1: "6px"
  radius-2: "10px"
  radius-3: "14px"
  radius-pill: "999px"
spacing:
  space-1: "4px"
  space-2: "6px"
  space-3: "8px"
  space-4: "12px"
  space-5: "16px"
  space-6: "20px"
  space-7: "28px"
  space-8: "40px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.accent-ink}"
    rounded: "{rounded.radius-1}"
  button-heat:
    textColor: "{colors.accent}"
    rounded: "{rounded.radius-1}"
  button-pressed:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.surface}"
    rounded: "{rounded.radius-1}"
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.radius-2}"
  priority-p1:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.surface}"
    rounded: "{rounded.radius-0}"
---

# Design System: Quenching Portal

`design-system/tokens.json` is the source of truth for every value here, including the dark theme, which this file does not repeat. `design-system/README.md` is the full usage guide.

## Overview

**Creative North Star: "The Supervisor's Cockpit"**

A dense, calm operating surface used for hours beside a terminal. Warm paper and a white sheet stay out of the way, so the one hot colour on screen always means the same thing: a person is needed here. Hierarchy comes from weight and a fixed scale, not from decoration.

**Key Characteristics:**
- Heat is spent only on what waits for the human.
- State is told by a mark or a word, never a coloured edge.
- The shell is fixed and the content scrolls.
- Two warm themes, light paper and dark charcoal, and two densities.

## Colors

A warm neutral ground with a single burnt-orange heat colour and quiet semantic states.

### Primary
- **Burnt Heat** (`accent`): the one primary action of a view, and whatever needs a person now. Nothing else.

### Neutral
- **Warm Paper** (`bg`): the page.
- **White Sheet** (`surface`): cards and panels; `surface-2` and `surface-3` are hover and press.
- **Warm Ink** (`ink`): text, and the current or pressed state.
- **Stone** (`muted`): everything secondary.
- **Hairline** (`line`): decoration only, at 1.4:1. **Control Edge** (`control-line`) is the 3:1 edge of anything a person operates.

### Named Rules
**The Heat Rule.** `accent` marks what waits for the human. A screen where it appears elsewhere is lying. The current nav item, a pressed toggle, a selected row and a link are `ink`.

**The Failure Rule.** `bad` means something failed or is blocked, never attention.

**The One Blue Rule.** `focus` is the only blue in the chrome, so the ring is never mistaken for a state.

## Typography

**Body Font:** the system stack, on purpose; the portal ships no font.
**Label/Mono Font:** the system mono stack.

**Character:** Plain and native. Hierarchy comes from weight and steps, and the scale is fixed, never fluid.

### Hierarchy
- **View**: heads a view.
- **Section**: heads a section.
- **Strong**: a card or row title.
- **Body**: running text.
- **Small**: metadata.
- **Label**: table heads and form labels.

### Named Rules
**The Code Only Rule.** Mono is for data that is code: spec ids, wave labels, commits, branches and commands. It never decorates a label.

**The Tabular Rule.** All counts, ages and progress use tabular numerals.

**The Sentence Case Rule.** Uppercase labels are retired.

## Layout

The app is a fixed grid: top bar (48px), pulse (34px), optional banner, the work area and the status bar (30px). Board lanes scroll one by one under a header that never leaves. Spacing is tight inside a group and generous between groups. `comfortable` and `compact` on `html[data-density]` rescale spacing and type. Layout changes at 1100px and 760px.

## Elevation & Depth

Flat at rest. Lines separate; shadows float.

### Shadow Vocabulary
- **Hover** (`shadow-1`): a hovered card.
- **Float** (`shadow-2`): anything over the page.

### Named Rules
**The Single Sheet Rule.** A panel never sits inside a panel, and a card lives on a lane, not in a box.

## Shapes

Gently curved and graded by role: `radius-1` for what you press, `radius-2` for panels, `radius-3` for dialogs, `radius-0` for tags, and `radius-pill` for count badges only.

## Components

### Buttons
- **Primary:** solid heat, one per view.
- **Heat:** outlined heat for a row action that needs the human.
- **Ghost:** transparent until hovered.
- **Pressed:** solid ink.
- **Disabled:** neutral `surface-2` with muted text, never a faded heat.

### Chips
- **Stage:** the tinted chip is for the one place a stage is the subject, the head of a spec; elsewhere a stage is an 8px square mark beside the word.
- **Hot:** `espera você` on `heat-tint`.

### Cards / Containers
- **Corner Style:** panel radius.
- **Background:** `surface`.
- **Shadow Strategy:** `shadow-1` on hover only.
- **Border:** `line`, rising to `control-line` on hover; the keyboard cursor is a 2px `focus` outline.

### Priority
P1 is solid ink, P2 outlined, P3 and P4 plain text, all in mono. Priority uses no colour, because the accent is taken.

### Pulse
A row of cells with tabular counts under the top bar. A cell turns hot when its count waits for the human. `próximo vencimento` and `mais antiga` carry the spec's id and a fixed-width title.

### Target
Working days to the target, then weeks past 10. Three working days or fewer is filled with the `executing` pair, and overdue with the `blocked` pair.

### Owner
A square badge of initials. Its `person-*` hue only tells people apart and carries no state. The cards of the identified user get a 2px ink ring.

### Balloon and menus
A balloon on `ink` shows exact values on hover and focus. Menus are native popovers anchored to their control.

## Do's and Don'ts

### Do:
- **Do** keep one primary button per view.
- **Do** tell stage with a mark and a word.
- **Do** keep motion between 120 and 200ms, and only to report a state change.
- **Do** add a new value to `tokens.json` before it becomes CSS.

### Don't:
- **Don't** add a coloured left edge to a card, row, toast or quote.
- **Don't** use a stage colour for text; use its `stage-*-ink` pair.
- **Don't** put a panel inside a panel.
- **Don't** use `accent` for navigation, selection or links.
