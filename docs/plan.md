# Plan — ai-assisted-coding-demo-2

Only unfinished milestones. Delete a milestone's row and block in the commit that finishes it; git
history is the record. Template: `docs/workflow.md`.

**Next milestone number: M14**

## Milestones at a glance

| Milestone | Description | Model | Effort | Status |
| --- | --- | --- | --- | --- |
| **M12** Job view UI | Ranked candidate cards from the mockups | sonnet | medium | open |
| **M13** Candidate view UI | Raw CV, attributes and ranked job descriptions | sonnet | medium | open |

## Milestones

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
