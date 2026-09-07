---
name: train-me-brand-identity
description: "Guide Train Me AI frontend UI work with its canonical purple-led color system, semantic roles, contrast expectations, and restrained category accents."
---

# Train Me Brand Identity

Use this skill whenever creating, editing, reviewing, or styling Train Me AI frontend interfaces. Treat the palette below as the product’s source of truth. Prefer semantic names in code so components communicate intent instead of coupling themselves to raw hex values.

## Canonical palette

The core brand combination is:

```css
--primary: #6658DC;
--dark: #111025;
--background: #F5F7FA;
--surface: #FFFFFF;
--light-purple: #E6E2FF;
--orange: #FF6B2C;
--muted-text: #8C8B98;
```

Supporting colors and intended roles:

| Token | Hex | Use |
| --- | --- | --- |
| `primary` / violet | `#6658DC` | Primary actions, selected states, links, key highlights |
| `dark` / dark purple | `#111025` | Buttons, strong text accents, dark panels |
| `background` / cool gray | `#F5F7FA` | Main page background |
| `outer-preview` / blue-gray | `#B8BEC6` | Outer preview or canvas background |
| `surface` / white | `#FFFFFF` | Cards, panels, inputs, elevated surfaces |
| `light-purple` | `#E6E2FF` | Tags, soft selected states, chart bars, tinted surfaces |
| `pink-accent` | `#F5D7F0` | Branding category accent |
| `blue-accent` | `#DDF2F7` | Front-end category accent |
| `orange` | `#FF6B2C` | Logo and logout accents; occasional attention/action accent |
| `main-text` | `#141326` | Primary body and heading text on light surfaces |
| `muted-text` | `#8C8B98` | Secondary text, metadata, placeholders |
| `border` | `#E8E8EE` | Borders, dividers, subtle outlines |

## Visual direction

- The dominant identity is purple + white + very light cool gray.
- Use `primary` for the visual anchor and `dark` for confident text or controls.
- Keep `orange`, `pink-accent`, and `blue-accent` sparse and purposeful. They distinguish categories or brand actions; they should not compete with the primary purple.
- Use `surface` cards against `background`, with `border` for quiet separation and `light-purple` for soft emphasis.
- Reserve `outer-preview` for a surrounding preview/canvas context, not ordinary page content.
- When a component needs a new shade, first derive a transparent or tonal treatment from an existing token; do not introduce an unrelated hue.

## Accessibility and interaction

- Check text and control contrast for every foreground/background pairing, especially muted text, tinted category surfaces, and hover states.
- Never use color alone to communicate status or category; pair it with text, an icon, shape, or another visual cue.
- Make hover, focus, active, disabled, and selected states visibly distinct while preserving the same semantic color roles.
- Prefer `main-text` for readable copy. Use `muted-text` for supporting information only, never for essential instructions or critical status.
- Use visible focus styles; `primary` or a clearly contrasting outline is preferred over removing the browser focus indicator.

## Implementation guidance

- In CSS, expose the tokens as custom properties with the names in the canonical palette.
- In Tailwind, map semantic names such as `primary`, `dark`, `background`, `surface`, `light-purple`, `orange`, `main-text`, `muted-text`, and `border` to these values in the project theme.
- Prefer semantic utility classes (`bg-background`, `text-main-text`, `border-border`) over arbitrary hex values in components.
- Keep the token names stable if the visual implementation changes; components should depend on roles, not color descriptions.
