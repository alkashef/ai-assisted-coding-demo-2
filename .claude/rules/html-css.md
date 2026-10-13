---
paths:
  - "**/*.html"
  - "**/*.css"
---

## HTML and CSS

- Stylelint (`.stylelintrc.json`) checks the CSS and Prettier (`.prettierrc.json`) formats the
  JavaScript, CSS, and HTML (`npm run lint:css`, `npm run format:check`). Fix findings and never
  weaken the configuration.
- Use semantic elements (`header`, `main`, `nav`, `aside`, `article`, `section`, `footer`). Every
  page has a clear `<title>` and one main heading.
- No `style=""` attributes and no `<style>` blocks. Pass computed values to CSS through custom
  properties set from JavaScript.
- No `onclick=""` or other inline handlers, and no `<script>` blocks, except the module entry in
  `index.html`. Attach behavior in JavaScript, using event delegation with `data-` attributes.
- HTML holds structure only. Markup that JavaScript needs lives in `<template>` elements in the
  HTML, not in JavaScript strings.
- Nothing loads from the network: no CDN, no Google Fonts. Store third-party files in the repo. A
  required external script is listed in `docs/design.md`.
- Colors, spacing, and fonts come only from custom properties in `theme.css`. Never write a color
  value in any other file.
- Keep shared sheets (`theme.css`, base, layout) and add one sheet per view or component only for
  styles specific to it. Every CSS file starts with a header comment that says what it styles and
  what it does not.
- Name CSS classes with BEM, `block__element--modifier`, and by purpose, not appearance
  (`sidebar__toggle`, not `blue-box`).
- Avoid duplicate rules, unused classes, excessive specificity, and layout hacks.
- Use meaningful link text and `alt` text on images. Keep text contrast readable. Do not rely on
  color alone to convey meaning.
- Mockups in `docs/` are a visual reference, not code to copy.
