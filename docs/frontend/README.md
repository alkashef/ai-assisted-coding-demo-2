# Front-end mockups

Visual reference for the browser UI that `src/web/` implements. It is a reference, not code to copy: the real
code follows `.claude/rules/html-css.md`, `.claude/rules/javascript.md` and `.claude/rules/ui-design.md`, and
the architecture in `docs/design.md` (DEC-002, section 2.1 and section 4).

All names, CVs and numbers in the mockups are invented. The three job-description titles come from the
synthetic TalentCLEF 2026 sample (DEC-010).

## How to open the mockups

Open any `*.dc.html` file in a browser. Each one links to `mockup.css` and to the others, so the links work as a
click-through prototype. The same files are on the design canvas: https://claude.ai/artifact/NekMwN3zpKJrtipfvubinU
(private; only the owner can open it until it is shared).

## Screens

| File | Screen | Requirements |
| --- | --- | --- |
| `Main.dc.html` | Start page: both lists, an empty selection, and the failure notice | LST-001, LST-002, ERR-001, ERR-002 |
| `Job-view.dc.html` | A job description is selected: its text (JOB-003, DEC-020, not in the mockup), then all candidates ranked, best first | JOB-002, JOB-003, RNK-001 to RNK-003, REC-001, MIS-001, MIS-002 |
| `Candidate-view.dc.html` | A candidate is selected: raw CV, attributes, job descriptions ranked | CND-001 to CND-003, EXT-002 to EXT-010, CAL-001 to CAL-005, CAL-007 |
| `States.dc.html` | Failure notice, empty selection, missing values, navigation states, badges, unknown item | ERR-001, ERR-002, MIS-001, MIS-002 |
| `Mobile-job-view.dc.html` | The job view at phone width (390 px) | ui-design rule: responsive |

## Layout

The standard layout from `.claude/rules/ui-design.md`: header, navigation, main content, footer.

- **Header:** the app name and a one-line tagline. No other controls. It is frozen: it stays at the top of the window
  while the page scrolls (DEC-019). Nothing else is frozen.
- **Navigation (left):** two lists, "Job descriptions" and "Candidates". Each item shows its name, with its file-name ID
  below it in small grey text (DEC-019). The current item is highlighted and has `aria-current="page"`.
- **File names:** wherever an ID is shown, it is a second line under the name or title, in the small size and
  `--color-muted` (DEC-019): navigation items, candidate cards, and the headings of the candidate and job views.
- **Main:** one selection at a time. The failure notice, when there is one, sits at the top of main.
- **Footer:** the dataset attribution (TalentCLEF 2026, CC BY 4.0).
- **Responsive:** the navigation and main wrap onto separate rows on narrow screens. At phone width the navigation
  folds into a `<details>` element so the results come first. No horizontal scrolling at any width.

## Behavior

- Selecting a navigation item loads that view without a full page reload. The address uses hash links
  (`#/jobs/<id>` and `#/candidates/<id>`), so the browser back button and a bookmark work. This is a front-end
  recommendation, not a spec requirement.
- Data comes only from the JSON API in `docs/design.md` section 4, through `api.js`. Every view needs one
  request: `/api/jobs/{id}` plus `/api/jobs/{id}/ranked-candidates` for the job view, and `/api/candidates/{id}` plus
  `/api/candidates/{id}/ranked-jobs` for the candidate view. The lists and the failure notice load at start.
- Everything is computed before the server starts (DEC-007), so reads are instant and the UI has no loading
  state. PRG-001 and PRG-002 are withdrawn.
- A `null` value in the JSON renders as the text "Not available" in the `not-available` style (MIS-001). The text
  itself carries the meaning, never the color alone.
- A candidate with no similarity score (no vector) is listed last in a ranking, with "Not available" as the
  score (MIS-002).
- An unknown ID (404) shows the "not found" panel from `States.dc.html`.

## What the mockups deliberately leave out

- **No red-flag highlight.** The spec gives no threshold for a short average tenure, and RNK-002 says the manager
  judges the attributes. The values are shown plainly.
- **No career-move label, no university-and-major pairs.** CAL-006 and EXT-011 are withdrawn.
- **No recommendation on the candidate view.** The user decided that CND-003 shows only the ranked job
  descriptions with their scores.
- **No retry button.** ERR-003 is withdrawn.
- **No search box, filter or sort control.** The spec has none.

## Card fields (job view)

Each ranked candidate card shows, in this order:

1. Rank, name (a link to the candidate view), the CV ID below the name in small grey text (DEC-019), then current job
   title (EXT-003) and current city and country (EXT-006).
2. Similarity score and the recommendation badge: "Interview" or "Do not interview" (REC-001), with the reason
   text beneath.
3. Six key values: total employment in months (CAL-001), jobs held (CAL-002), average per job in months
   (CAL-003), employment gaps (CAL-004), currently employed (CAL-007) and months since graduation (CAL-005).
4. The last job (EXT-009): title, employer, location, duration and brief description.
5. A "More attributes" `<details>` with the rest: current job title, address, highest degree (EXT-010), countries
   worked in (EXT-007), companies (EXT-008) and skills (EXT-004).

Number formats: months are shown as "N months", with one decimal for the average. Gaps are "None" or
"N gap(s): X months".

## Design tokens

Define these as custom properties in `src/web/css/theme.css`. No other file may contain a color value.

| Token | Value | Use |
| --- | --- | --- |
| `--color-bg` | `#f6f7f9` | Page background |
| `--color-surface` | `#ffffff` | Header, footer, panels, cards |
| `--color-hover` | `#eceff3` | Hover, chips, neutral badge |
| `--color-text` | `#1d2430` | Body text |
| `--color-muted` | `#566170` | Labels, secondary text |
| `--color-border` | `#d5dae1` | Borders |
| `--color-accent` / `--color-accent-bg` | `#1f5fae` / `#e8f0fb` | Links, current item, rank badge |
| `--color-positive` / `--color-positive-bg` | `#17633a` / `#e3f4ea` | "Interview" badge |
| `--color-negative` / `--color-negative-bg` | `#8f2222` / `#fbe9e9` | "Do not interview" badge |
| `--color-notice` / `--color-notice-bg` | `#7a4e00` / `#fff3d1` | Failure notice |
| `--space-1` to `--space-6` | 4, 8, 12, 16, 24, 32 px | Spacing scale |
| `--radius` | 6 px | Corners |
| `--measure` | 72ch | Maximum line length for prose |
| `--font-body` | system font stack | Text. No web font. |
| `--font-mono` | monospace stack | Raw CV text |

Text and badge colors have a contrast of at least 4.5:1 on their backgrounds. The sizes are 13 px (small), 15 px
(body), 17 px (heading) and 22 px (page title).

## Components to implement

Class names are lowercase words joined by single hyphens, such as `app-header` or `nav-link-current`, and they
name the purpose (`.claude/rules/html-css.md`). The start of an element or modifier name is its block's name
(`card-score-label` belongs to `card`). The mockups use the same names, so the classes in `mockup.css` can be
reused as they are. `mockup.css` shows the styles. Map them to the sheets in `docs/design.md` section 2.2:

| Sheet | Holds |
| --- | --- |
| `theme.css` | The tokens above |
| `base.css` | Body, links, focus outline, `.not-available`, `.chips`, `.badge` |
| `layout.css` | `.app`, `.app-header`, `.app-body`, `.app-nav`, `.app-main`, `.app-footer`, `.nav`, `.nav-fold`, `.page-head` |
| `detail.css` | `.card`, `.cards`, `.stat`, `.facts`, `.panel`, `.notice`, `.doc`, `.ranking`, `.detail` |

Markup that JavaScript builds lives in `<template>` elements in `index.html`: one for a nav item, a ranked
candidate card, a ranking row, and the failure notice. JavaScript fills text with `textContent` and toggles
classes. It never writes HTML strings or inline styles. The `style=""` attributes in the mockups (the hover and
focus demos, and a few phone-width tweaks) are mockup-only.

## Accessibility

- Real `<a>`, `<details>` and `<summary>` elements, so keyboard and screen readers work with no extra code.
- A visible focus outline on links and summaries (`--color-accent`).
- The failure notice has `role="status"`.
- One `<h1>` for the app. Each view's title is an `<h2>`. Cards and panels use `<h3>`.
- Every `<title>` is short. The real page sets the title to the current selection.
- Recommendation badges carry text ("Interview", "Do not interview"), so color is never the only signal.
