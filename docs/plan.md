# Plan — ai-assisted-coding-demo-2

Only unfinished milestones. Delete a milestone's row and block in the commit that finishes it; git
history is the record. Template: `docs/workflow.md`.

**Next milestone number: M14**

## Milestones at a glance

| Milestone | Description | Model | Effort | Status |
| --- | --- | --- | --- | --- |
| **M11** Front-end shell and start page | `index.html`, tokens and layout, the lists and the failure notice, browser-test harness | sonnet | high | open |
| **M12** Job view UI | Ranked candidate cards from the mockups | sonnet | medium | open |
| **M13** Candidate view UI | Raw CV, attributes and ranked job descriptions | sonnet | medium | open |

## Milestones

### M11 — Front-end shell and start page

- **Refs:** LST-001, LST-002, ERR-001, MIS-001; DEC-002, DEC-012, `docs/frontend/README.md`, `docs/frontend/Main.dc.html`, `docs/frontend/States.dc.html`.
- **Owner:** `src/web/index.html`, `src/web/css/theme.css`, `src/web/css/base.css`, `src/web/css/layout.css`, `src/web/css/detail.css`, `src/web/js/main.js`, `config.js`, `log.js`, `api.js`, `format.js`, `list-view.js`, `failures-view.js`; `tests/e2e/ui/`; `requirements.txt` (`playwright`).
- **Tests first:** in `tests/unit/format.test.js`: `test_mis_001_null_renders_as_not_available`, `test_cal_004_gaps_render_as_none_or_a_count_and_months`, `test_cal_003_months_render_with_one_decimal_for_the_average`. In `tests/e2e/ui/test_start_page.py` (a fixture starts the app on loopback with a fake workspace, headless browser): `test_lst_001_ui_lists_the_job_descriptions`, `test_lst_002_ui_lists_the_candidates`, `test_err_001_ui_shows_the_failure_notice_with_the_causes`, `test_mis_001_ui_shows_not_available_for_a_missing_candidate_name`.
- **Build:** the page from the mockups: header, navigation, main, footer; tokens only in `theme.css`; `<template>` elements for markup; plain ES modules with JSDoc; `api.js` is the only module that calls `fetch`; hash routes `#/jobs/<id>` and `#/candidates/<id>` reserved for M12 and M13. Add the browser-test fixture. If Playwright cannot drive the installed Edge or Chrome without a download, set this milestone to `blocked` with the exact question (a download needs the user's approval).
- **Gate:** the tests and the checks pass, including `npm run typecheck`, `npm run lint`, `npm run lint:css`, `npm run format:check` and `npm test`; no inline styles and no color value outside `theme.css`; the UI tests ran headless and passed.

### M12 — Job view UI

- **Refs:** JOB-002, RNK-003, REC-001, MIS-001, MIS-002; `docs/frontend/Job-view.dc.html`, `docs/frontend/Mobile-job-view.dc.html`.
- **Owner:** `src/web/js/job-view.js`, `src/web/css/detail.css`, a card template in `src/web/index.html`.
- **Tests first:** in `tests/e2e/ui/test_job_view.py`: `test_job_002_ui_selecting_a_job_description_shows_all_candidates_best_first`, `test_rnk_003_ui_card_shows_extracted_and_calculated_attributes`, `test_rec_001_ui_card_shows_the_recommendation_badge_and_reason`, `test_mis_001_ui_missing_value_shows_not_available`, `test_mis_002_ui_candidate_without_a_score_is_listed_last`.
- **Build:** `job-view.js` loads `/api/jobs/{id}/ranked-candidates`, clones the card template and fills text with `textContent`; the key values, last job and "More attributes" fold as in the mockup; the layout wraps at phone width.
- **Gate:** the tests and all checks pass; the view matches the mockup's fields and order.

### M13 — Candidate view UI

- **Refs:** CND-001, CND-002, CND-003, MIS-001; `docs/frontend/Candidate-view.dc.html`, `docs/frontend/States.dc.html` (unknown item).
- **Owner:** `src/web/js/candidate-view.js`, `src/web/css/detail.css`, templates in `src/web/index.html`.
- **Tests first:** in `tests/e2e/ui/test_candidate_view.py`: `test_cnd_001_ui_selecting_a_candidate_shows_the_raw_cv`, `test_cnd_002_ui_shows_extracted_and_calculated_attributes`, `test_cnd_003_ui_shows_the_job_descriptions_ranked_with_scores`, `test_mis_001_ui_missing_attribute_shows_not_available`, `test_cnd_001_ui_unknown_candidate_shows_the_not_found_panel`.
- **Build:** `candidate-view.js` loads `/api/candidates/{id}` and `/api/candidates/{id}/ranked-jobs`; the attributes list, the ranked job list and the raw CV text as in the mockup; no recommendation on this view; the not-found panel for a 404.
- **Gate:** the tests and all checks pass; the view matches the mockup's fields and order.
