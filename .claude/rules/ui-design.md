---
paths:
  - "**/*.html"
  - "**/*.css"
  - "**/*.js"
---

## UI design

- Quick: no unnecessary scripts, fonts, or images. Every action gives immediate feedback, and slow
  work shows a loading state.
- Responsive: the layout adapts from phone to wide desktop widths without horizontal scrolling, and
  content keeps a readable width on large screens.
- Minimal and uncluttered: show only what the current task needs, with one primary action per view,
  few colors, and generous whitespace. No decorative effects and no complex animation.
- Standard layout: header, navigation, main content, and footer, in the usual places. Use native
  HTML controls (`button`, `a`, `input`, `select`) instead of custom widgets.
- Every button and icon control has hover text (`title`) that explains what it does. Hover is not
  the only explanation: an icon-only control also has an `aria-label`, because touch screens have no
  hover.
- Prefer the system font stack. Add a custom font or an image only when `docs/design.md` requires
  it. Download it with `scripts/download_assets.py` into `src/assets/fonts/` or
  `src/assets/images/`, and commit the files. Never link to a font or an image online. The script
  records each source URL and license, and only assets whose license allows redistribution are used.
