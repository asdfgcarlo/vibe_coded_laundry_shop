---
name: "Dina’s Laundry Shop"
description: "Warm household linen, tailored clarity, and an easier laundry day."
colors:
  cream: "#faf7ef"
  paper: "#fffefa"
  navy: "#172f36"
  teal: "#12615b"
  teal-dark: "#0a4945"
  mint: "#dfebe3"
  muted: "#54665f"
  line: "#d6dbd0"
  error: "#a12727"
  field-border: "#bcc8bd"
  pickup-ground: "#eef0e7"
  focus: "#b45b2a"
typography:
  display:
    fontFamily: "Fraunces, Georgia, serif"
    fontSize: "clamp(3.5rem, 5.7vw, 5.6rem)"
    fontWeight: 500
    lineHeight: 1.12
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "Fraunces, Georgia, serif"
    fontSize: "clamp(2.35rem, 3.55vw, 3.5rem)"
    fontWeight: 500
    lineHeight: 1.12
    letterSpacing: "-0.035em"
  service-title:
    fontFamily: "Fraunces, Georgia, serif"
    fontSize: "1.65rem"
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: "-0.02em"
  title:
    fontFamily: "DM Sans, Arial, sans-serif"
    fontSize: "1.35rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "-0.02em"
  body:
    fontFamily: "DM Sans, Arial, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.65
  label:
    fontFamily: "DM Sans, Arial, sans-serif"
    fontSize: "0.8rem"
    fontWeight: 600
    lineHeight: 1.5
  button:
    fontFamily: "DM Sans, Arial, sans-serif"
    fontSize: "0.92rem"
    fontWeight: 600
    lineHeight: 1.4
  estimate:
    fontFamily: "Fraunces, Georgia, serif"
    fontSize: "3.3rem"
    fontWeight: 400
    lineHeight: 1.2
    letterSpacing: "-0.035em"
rounded:
  label: "4px"
  field: "5px"
  button: "6px"
  surface: "12px"
  circle: "50%"
spacing:
  compact: "12px"
  field-gap: "20px"
  control: "24px"
  surface-mobile: "25px"
  group: "30px"
  surface: "34px"
  section-mobile: "62px"
  section-tablet: "80px"
  section: "110px"
components:
  button-primary:
    backgroundColor: "{colors.teal}"
    textColor: "{colors.paper}"
    typography: "{typography.button}"
    rounded: "{rounded.button}"
    padding: "15px 24px"
  button-primary-hover:
    backgroundColor: "{colors.teal-dark}"
    textColor: "{colors.paper}"
  button-small:
    backgroundColor: "{colors.teal}"
    textColor: "{colors.paper}"
    rounded: "{rounded.button}"
    padding: "12px 18px"
  button-round:
    textColor: "{colors.teal}"
    rounded: "{rounded.circle}"
    size: "46px"
  field:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.navy}"
    rounded: "{rounded.field}"
    padding: "13px 14px"
  calculator:
    backgroundColor: "{colors.cream}"
    textColor: "{colors.navy}"
    rounded: "{rounded.surface}"
    padding: "34px"
  pickup-form:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.navy}"
    rounded: "{rounded.surface}"
    padding: "34px"
  sample-label:
    backgroundColor: "#ece9dc"
    textColor: "#5b5947"
    rounded: "{rounded.label}"
    padding: "4px 10px"
---

# Design System: Dina’s Laundry Shop

## Overview

**Creative North Star: "The Household Linen Label"**

Warm paper, deep teal, navy ink, and a soft editorial serif make laundry feel like a manageable household ritual. Broad space and tailored rules give practical information a calm, welcoming rhythm. The system pairs linen photography with original drop-and-wave artwork and restrained line icons.

The expressive elements remain tangible: an arched photograph, a single tilted care tag, and saturated teal grounding the calculator. Operational surfaces are quieter, with upright sans-serif labels, native controls, visible borders, and plainly differentiated states. These rules describe the finished HTML/CSS implementation; the surface contract retains page-specific composition and content strategy.

**Key Characteristics:**

- Warm cream ground with paper-white working surfaces.
- Fraunces for editorial warmth; DM Sans for everyday clarity.
- Tailored dividers and service rows rather than repeated floating cards.
- One tactile care tag and softly arched linen photography.
- Visible focus, native form controls, and reduced-motion support.

## Colors

The palette combines household cream and linen greens with deep teal actions and navy text. The frontmatter is the normative source for shared colors; component-specific tints remain local to their implemented patterns.

### Primary

- **Deep Teal** (`teal`): primary actions, emphasized heading phrases, service prices, line icons, and the calculator section ground.
- **Deep Teal Hover** (`teal-dark`): primary action hover state.

### Neutral

- **Warm Cream** (`cream`): page ground, header, calculator surface, and light text on deep grounds.
- **Paper White** (`paper`): pickup form, native fields, and primary action text.
- **Navy Ink** (`navy`): main text and contact section ground.
- **Linen Mint** (`mint`): service ribbon, weight-control hover, and saved-reference emphasis.
- **Muted Sage Ink** (`muted`): descriptions, hints, captions, and supporting copy.
- **Tailored Rule** (`line`): section, row, result, and footer dividers.
- **Field Stroke** (`field-border`): native fields and the grouped weight control.
- **Pickup Ground** (`pickup-ground`): tonal ground behind the paper request surface.

### State colors

- **Error Red** (`error`): invalid field borders and field-error text. The summary alert also uses its implemented pale peach surface and darker red copy.
- **Warm Focus** (`focus`): general keyboard focus; form controls instead use the primary teal focus outline.

### Named Rules

**The Ground and Ink Rule.** Keep the warm cream and paper surfaces paired with navy or muted sage copy; reserve deep teal and navy grounds for clearly bounded sections with light text.

## Typography

**Display Font:** Fraunces, with Georgia and serif fallbacks.

**Body Font:** DM Sans, with Arial and sans-serif fallbacks.

Both families are self-hosted WOFF2 variable fonts with swap loading. The SVG wordmark is a fixed identity asset using its own Georgia/Arial lettering; it is not the page’s typography template.

**Character:** Fraunces gives headlines a generous, domestic warmth. DM Sans keeps forms, explanations, navigation, and numerical detail direct and legible. Heading emphasis changes to teal without becoming italic. Headings use balanced wrapping; paragraphs have a general maximum measure of 70 characters.

### Hierarchy

- **Display:** the frontmatter display role supplies the desktop hero. On widths at or below 720px, the hero uses `clamp(3.3rem, 9.8vw, 4.4rem)` with a tighter line height (1.08); at or below 400px it settles at 3.35rem.
- **Headline:** the shared headline role supplies section headings. Pickup, calculator, contact, and mobile section headings have observed local sizing overrides; do not force every heading into one size.
- **Service title:** the serif service-title role labels service rows; it reduces through 1.45rem, 1.35rem, and 1.2rem as the rows become compact.
- **Title:** the sans-serif title role supports smaller structural headings; process headings use a quieter local size.
- **Body:** the body role establishes the page baseline. Descriptive and operational copy uses local smaller sizes, while the hero introduction is slightly larger with more leading.
- **Label:** the label role supplies sentence-case field labels. Optional qualifiers use regular weight and muted ink. Labels reduce at tablet and phone widths.
- **Estimate:** the serif estimate role gives the calculated total emphasis; tabular numerals stabilize amounts and service prices. Prices themselves use DM Sans.

### Named Rules

**The Two Voices Rule.** Use Fraunces for editorial headlines and selected high-emphasis totals; keep navigation, actions, fields, and explanatory copy in DM Sans.

## Layout

The desktop content container is capped at 1200px with a total horizontal inset of 112px. The inset becomes 72px at 1150px, 48px at 900px, and 36px at 400px. Standard sections use the frontmatter section spacing, stepping down to its tablet and mobile values. Calculator, pickup, contact, and hero sections keep their own observed vertical rhythm.

The desktop hero is an aligned two-column composition (1.12fr / 1fr), with broad copy and a portrait linen image. Service rows align an icon tile, description, price, and circular action; process steps form three ruled columns. Calculator, pickup, FAQ, and contact sections use unequal two-column layouts. The request form uses two columns, with address and instructions spanning both; fields are separated by roughly the shared field gap.

At 720px and below, the hero and major section layouts stack, process steps become compact icon-and-copy rows, service prices move below the description, and navigation becomes an accessible disclosure when JavaScript is active. The form remains two columns until 400px, then becomes one. Calculator fields stack at tablet widths, return to paired fields on larger phones, and stack again at 400px. The header remains sticky with a fine lower rule; anchor scroll offsets account for it.

## Elevation & Depth

Depth comes primarily from tonal section grounds, borders, and the material in the linen photograph. Calculator and request surfaces have no resting shadow. The care tag is the sole softly lifted paper object; its diffuse shadow and slight rotation reinforce its physical character.

### Shadow Vocabulary

- **Care tag at rest** (`0 10px 24px #172f3612`): the single tilted tag over the hero image.
- **Care tag settling** (`0 16px 30px #172f3620`): the starting frame of its entrance animation.

### Named Rules

**The Single Lift Rule.** Keep working surfaces flat; the care tag carries the page’s small tactile lift.

## Shapes

The shared surface radius softens the calculator, request container, standalone message, and service icon tiles. Actions use the smaller button radius, inputs use the field radius, and small informational labels use the label radius. Circular service actions and the success mark remain truly round.

The hero photograph has a broad arched top and softly rounded lower corners; its radius changes with the viewport. The care tag stays rectangular, rotates by minus five degrees at rest, and has an inset hairline frame. Rules and native field strokes are fine (1px). SVG icons use rounded stroke ends and joins; the drop-and-wave logo and matching favicon are the identity assets.

## Components

### Buttons

Confident, compact, and plainly actionable. Primary buttons use the frontmatter primary variant, a minimum height of 56px, and an arrow icon. Hover deepens the teal and lifts the button by 2px; active returns it to its baseline. Compact header buttons start at a minimum height of 46px. General keyboard focus uses an offset warm outline. Disabled submit buttons retain their form, reduce opacity, show the saving label and spinner, and use a wait cursor.

Text links provide the quieter secondary action, with teal text and an underline that thickens on hover. Circular service actions have a fine green border and invert to teal with cream icon strokes on hover.

### Cards / Containers

Calculator and pickup form containers are flat, warmly rounded working surfaces with generous padding. Shared desktop surface padding reduces to 25px on phones and 21px on the smallest phones. The calculator is cream on a teal section; the request form is paper on the lighter pickup ground. Service information uses ruled rows, not card shadows.

### Inputs / Fields

Native inputs, selects, and textareas use paper fill, the field stroke and radius, and a minimum height of 48px. Hover changes the stroke to teal; keyboard focus uses a teal outline (2px) with an offset (3px). Invalid fields use the error color and explanatory text directly below. The grouped weight control puts the numerical field between two half-kilogram buttons, uses a shared outline on focus within, and applies mint hover to its side buttons.

The preview notice uses a pale green bordered treatment. Failure summaries use a pale peach alert, while success uses a circular mint check mark and a mint reference strip. These status patterns retain written explanations; color is not the only distinction.

### Navigation

The sticky cream header carries the original wordmark, sentence-case DM Sans links, and a compact teal pickup action. Desktop links reveal a thin teal underline on hover. Mobile uses a bordered Menu control with CSS-drawn lines; its expanded state reveals wrapped links and a full-width pickup action. Escape, outside interaction, and selecting a link close the enhanced menu.

### Sample-rate label

A small rounded, muted linen label qualifies sample pricing. It is contextual information beside the service introduction, with compact mixed-case text; it is not a heading prefix or a general-purpose eyebrow style.

### Service row

An editorial ruled row puts a softly tinted icon tile beside the service title and description, a stable tabular price, and a circular arrow. Its mobile arrangement keeps the arrow at the first row’s edge and the price beneath the copy.

### Care tag

The single linen-paper tag pairs a teal four-point motif with two lines of short copy and an inset border. Its entrance settles from a lower, more rotated position over 900ms using the shared easing curve. It remains decorative and is hidden from assistive technology.

### FAQ disclosure

Native details and summary elements form a ruled list. The summary turns teal on hover, and the plus rotates by 45 degrees when open. Expanded answers stay in muted ink with generous leading; the disclosure keeps keyboard focus visible.

### Motion

Button color changes run over 0.2s and its lift over 0.3s. Navigation underline movement uses 0.2s; FAQ icon rotation uses 0.25s. The shared easing curve is `cubic-bezier(0.16, 1, 0.3, 1)`. The loading spinner uses an 0.8s linear rotation. Reduced-motion preference turns off smooth scrolling and tag animation and reduces other animation and transition durations to 0.01ms with one iteration.

## Do's and Don'ts

### Do:

- **Do** use warm tonal grounds and fine rules to organize information before adding containers.
- **Do** keep editorial serif warmth and operational sans-serif clarity in their observed roles.
- **Do** retain visible offset keyboard focus, native controls, and text explanations for status.
- **Do** preserve the original drop-and-wave identity and soft linen material character.
- **Do** keep the care tag’s single tactile lift and honor reduced-motion preference.

### Don't:

- **Don't** spread the care tag’s rotation or shadow across forms, service rows, or navigation.
- **Don't** turn the contextual sample-rate label into a general heading-prefix style.
- **Don't** remove field borders or focus outlines from the cream and paper surfaces.
- **Don't** force compact phone service rows or form fields back into their desktop column structure.
