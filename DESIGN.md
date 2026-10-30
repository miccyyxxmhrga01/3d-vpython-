---
name: Caybin Dream House
description: A quiet architectural frame for a warm modern Python house.
colors:
  primary: "#3c5744"
  primary-hover: "#2e4935"
  ground: "#eeeee8"
  surface: "#f8f8f4"
  ink: "#2d342e"
  muted: "#596252"
  rule: "#dcded4"
  raised: "#fff"
  focus: "#547d5e"
  canvas: "#e4e6dc"
  overlay: "#f6f7f0"
  navigation-active: "#e1e5d9"
  navigation-hover: "#e7e9e0"
  concrete-swatch: "#c4c3b8"
  oak-swatch: "#a57e54"
  glass-swatch: "#bad1c8"
  model-plaster: "#e7e2d7"
  model-concrete: "#bcbcb1"
  model-stone: "#d2cabc"
  model-wood: "#9a7250"
  model-frame: "#343b35"
  model-glass: "#b3d4ce"
  model-linen: "#e6dfce"
  model-leaf: "#6d7c51"
  model-water: "#79b5ad"
typography:
  headline:
    fontFamily: 'House Display, "Segoe UI", sans-serif'
    fontSize: "32px"
    fontWeight: 500
    lineHeight: 1.16
    letterSpacing: "-1px"
  wordmark:
    fontFamily: 'House Display, "Segoe UI", sans-serif'
    fontSize: "21px"
    fontWeight: 500
    letterSpacing: "-0.6px"
  body:
    fontFamily: '"Segoe UI", Helvetica, Arial, sans-serif'
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.8
  title:
    fontFamily: '"Segoe UI", Helvetica, Arial, sans-serif'
    fontSize: "13px"
    fontWeight: 500
  label:
    fontFamily: '"Segoe UI", Helvetica, Arial, sans-serif'
    fontSize: "12px"
    fontWeight: 400
  figure:
    fontFamily: '"Segoe UI", Helvetica, Arial, sans-serif'
    fontSize: "20px"
    fontWeight: 500
rounded:
  swatch: "3px"
  tab: "4px"
  control: "6px"
  navigation: "7px"
  overlay: "8px"
  panel: "10px"
  viewport: "12px"
spacing:
  compact: "8px"
  control: "12px"
  inset: "16px"
  group: "20px"
  section: "30px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.raised}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "0 15px"
    height: "44px"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
    textColor: "{colors.raised}"
  room-navigation:
    textColor: "{colors.ink}"
    rounded: "{rounded.navigation}"
    padding: "11px 9px"
  room-navigation-active:
    backgroundColor: "{colors.navigation-active}"
  room-navigation-hover:
    backgroundColor: "{colors.navigation-hover}"
  viewer-overlay:
    backgroundColor: "{colors.overlay}"
    textColor: "{colors.ink}"
    rounded: "{rounded.overlay}"
  viewer-shell:
    backgroundColor: "{colors.canvas}"
    rounded: "{rounded.viewport}"
---

# Design System: Caybin Dream House

## Overview

**Creative North Star: "The Quiet Architectural Frame"**

The interface gives a warm modern house room to be seen. Pale stone surfaces, charcoal type, and a forest primary control form a restrained working frame; timber, planting, glass, and water belong to the three-dimensional architecture. The experience is a compact concept viewer rather than a marketing page.

Density stays measured and useful: short room labels, small familiar controls, and readable context around a dominant model. The project title leads directly, without an introductory kicker. This records the implemented warm modern direction in [the surface contract](.impeccable/surface.md); new surfaces should inherit its materials and restraint rather than its exact composition.

**Key Characteristics:**

- Pale stone framing with a single forest action color.
- Dedicated display type for project identity; compact sans type for operation.
- Flat, lightly bordered controls around a richly modeled scene.
- Immediate room, camera, and walkthrough feedback.

## Colors

The palette combines softened architectural neutrals with forest controls and natural material colors. Frontmatter values are normative; UI swatches are deliberately distinct from the model's shaded materials.

### Primary

- **Forest:** the entry action, brand mark, interactive emphasis, and range input. Its darker hover sibling reinforces the same action.
- **Leaf Focus:** keyboard outlines remain visible against both pale UI surfaces and the model.

### Secondary

- **Warm Oak and Concrete:** material swatches preview the house; their model counterparts color geometry rather than interface controls.
- **Soft Glass and Pool Water:** restrained blue-green material notes in the architecture and plan.

### Neutral

- **Pale Stone Ground:** the application shell.
- **Chalk Surface and Raised White:** support surfaces and reversed primary text.
- **Charcoal Ink and Moss Gray:** main text and supporting labels.
- **Stone Rule:** subtle division between material groups.
- **Canvas Sage and Chalk Overlay:** the scene backdrop and readable floating controls.
- **Navigation Tints:** selection and hover use tonal fills rather than a competing accent.

**The Material Ownership Rule.** Keep oak, glass, and water as material information; use forest for interface action.

## Typography

**Display Font:** House Display, a self-hosted Roboto Medium font served at `/vendor/Roboto-Medium.ttf`, with Segoe UI and sans-serif fallbacks.

**Body Font:** Segoe UI, Helvetica, Arial, sans-serif.

The display face identifies the project and wordmark without becoming ornamental. Operational copy stays small, regular, and sentence case. The stylesheet root is (14px), while the actual interface predominantly uses the label and body roles recorded above.

- **Headline:** project title; tight tracking and short lines. It becomes (29px) on short desktop viewports and (20px), with (-0.5px) tracking, on mobile.
- **Wordmark:** compact identity; becomes (19px) on mobile.
- **Title:** room names use medium weight above muted descriptive text.
- **Body:** sidebar introduction uses generous leading and a (26ch) measure; it becomes (13px) above the large-screen breakpoint.
- **Label:** controls, captions, navigation descriptions, and help copy.
- **Figure:** house facts use tabular numerals; unit suffixes return to label size.

**The Identity Pair Rule.** Reserve House Display for the project heading and wordmark; keep operational labels in the body stack.

## Layout

The desktop application fills the dynamic viewport. A (74px) topbar sits above a two-column workspace with a (282px) sidebar and a flexible viewer, leaving a (14px) outer inset on the viewer's right and bottom. The sidebar scrolls independently when necessary; the canvas remains framed.

At widths up to (1050px), the sidebar narrows to (246px), tool text collapses to icons, and overlays shrink. From (1600px), the sidebar grows to (312px) and the canvas controls gain larger insets. Short desktop viewports up to (800px) high compress sidebar spacing rather than clipping navigation.

At widths up to (760px), a (60px) topbar precedes a flexible viewer and a compact controls area beneath it. Room navigation becomes a horizontally scrollable row; project facts, material swatches, and secondary copy recede. The tour slider stays visible for touch. The shell uses (8px) outer insets and a smaller corner radius. Scene controls remain at the upper corners, with walkthrough information below.

Spacing is component-led rather than a strict numerical grid: compact inner gaps, moderate panel insets, and larger separation between project, room, and material groups. Use the frontmatter spacing steps as recurring anchors, while preserving the precise offsets needed by a working canvas.

## Elevation & Depth

The interface is flat by default: tonal fills, fine borders, clipping, and positional layering separate controls from the model. The help panel alone has a soft ambient shadow (`0 8px 28px #29352618`). The architecture supplies physical depth through geometry, light, transparency, and occlusion; do not imitate that depth with raised UI cards.

**The Flat Frame Rule.** Use tonal separation for resting controls; reserve the documented shadow for the floating help panel.

## Shapes

Corners are gently rounded and practical. Small controls use the control and tab radii, room rows use the navigation radius, floating information uses the overlay radius, and the desktop canvas receives the largest radius. Thin borders define scene controls and information panels. Material swatches are nearly rectangular; status indicators are tiny circles. Icons are fine, rounded-stroke SVG drawings, generally (14–20px).

## Components

### Buttons

The forest primary spans its sidebar column, with a trailing arrow and compact label. Desktop height is at least (44px); mobile uses (39px). Hover deepens the fill. Text buttons retain a transparent background; scene tool buttons use pale surfaces, fine borders, and (37px) height, shrinking to (32px) on mobile. Pressed tools gain a green-tinted fill and stronger border.

Keyboard focus uses a (2px) focus outline with (4px) offset. Buttons move down (1px) when pressed. The loading state disables the entry action with reduced opacity and a waiting cursor.

### Room Navigation

A full-width row combines a room number or SVG, a medium-weight name, a muted description, and a trailing chevron. Desktop rows are at least (56px) high; the selected row uses a tonal fill and `aria-current`. Hover also reveals the chevron. Mobile rows become compact single-line buttons without numbers or descriptions; preserve the selected fill and horizontal overflow.

### Camera Tools

The Perspective button returns to the exterior view using the same pale surface and border as the scene tools. Roof and light tools expose pressed state; their labels collapse where space is limited while their accessible names remain useful.

### Viewer Information

The scene caption and walkthrough bar use opaque pale surfaces so labels remain readable over geometry. The walkthrough bar combines an instruction, a thin progress track, position feedback, and reset.

### Walkthrough Range

The native range control uses forest accent color. On desktop it fades into view when the viewer is hovered or the range is focused; on mobile it remains visible. Keep its accessible label. The walkthrough camera smooths toward the requested route position, and reduced-motion mode removes smoothing as well as CSS transitions.

### Help and Recovery

Help is a compact floating panel with a short explanation and aligned input/action pairs. Recovery uses a centered pale panel with a direct error explanation and the primary retry action. Loading occupies the scene with an SVG, one short status line, and a muted detail line. These states retain the same quiet typography and surfaces.

## Do's and Don'ts

### Do:

- **Do** keep material colors tied to architecture and forest tied to interface action.
- **Do** preserve opaque labels and clear focus outlines over the changing scene.
- **Do** use the dedicated display face for project identity and the body stack for controls.
- **Do** adapt control density and navigation to narrow and short viewports.
- **Do** honor reduced motion in both UI transitions and camera movement.

### Don't:

- **Don't** introduce a kicker above the project title.
- **Don't** add ornamental gradients, decorative cards, or hard offset shadows to this quiet material world.
- **Don't** turn the material swatches into additional competing action colors.
- **Don't** promote the desktop sidebar composition into a requirement for every future surface.
