# Plan — ai-assisted-coding-demo-2

Only unfinished milestones. Delete a milestone's row and block in the commit that finishes it; git
history is the record. Template: `docs/workflow.md`.

**Next milestone number: M14**

## Milestones at a glance

| Milestone | Description | Model | Effort | Status |
| --- | --- | --- | --- | --- |
| **M7** API app and lists | App factory on loopback, `/health`, job and candidate lists, failure list | sonnet | medium | Approved |
| **M8** API ranked views | Ranked candidates for a job, candidate detail, ranked jobs, 404 for an unknown ID | sonnet | medium | open |
| **M9** Sample builder | `scripts/build_sample.py`: 3 diverse jobs and 10 CVs from the raw dataset, with ground truth | sonnet | medium | open |
| **M10** Prompts and entry point | The two prompt files, `main.py`, start-to-API end-to-end test with fakes, README setup and manual live check | sonnet | high | open |
| **M11** Front-end shell and start page | `index.html`, tokens and layout, the lists and the failure notice, browser-test harness | sonnet | high | open |
| **M12** Job view UI | Ranked candidate cards from the mockups | sonnet | medium | open |
| **M13** Candidate view UI | Raw CV, attributes and ranked job descriptions | sonnet | medium | open |

## Milestones

### M7 — API app and lists

- **Refs:** LST-001, LST-002, ERR-001; DEC-002, DEC-012, DEC-013, design section 4.
- **Owner:** `src/workspace_views.py`, `src/api/app.py`, `src/api/jobs.py`, `src/api/candidates.py`, `src/api/status.py`, `src/api/schemas.py`; `requirements.txt` (`fastapi`, `httpx`).
- **Tests first:** in `tests/e2e/test_api_lists.py` (the framework's test client, a fake workspace): `test_lst_001_jobs_endpoint_lists_job_ids_and_titles`, `test_lst_002_candidates_endpoint_lists_candidate_ids_and_names`, `test_err_001_failures_endpoint_lists_item_and_cause`, `test_dec_002_health_endpoint_reports_alive`, `test_dec_002_static_front_end_is_served_from_the_web_root`. In `tests/unit/test_workspace_views.py`: `test_lst_001_job_list_has_id_and_title`, `test_lst_002_candidate_list_has_id_and_name`, `test_err_001_failure_list_has_item_and_cause`.
- **Build:** view functions in `workspace_views.py`; one router per domain whose handlers each call one view function; response models in `schemas.py`; `create_app(workspace, web_root)` includes the routers and mounts the static files last. No authentication and no CORS (DEC-013).
- **Gate:** the tests and the checks pass; handlers hold no logic; no server is started in tests.
- **Blocked:** M7 needs `fastapi` installed in the conda environment, and the install was not approved in this unattended run.
  - `fastapi` is not installed (`import fastapi` fails; `httpx` and `uvicorn` are). `CLAUDE.md` (Git and destructive actions) says `.claude/settings.json` asks before installs; no one could answer, and the Bash tool refused `pip install fastapi`.
  - The M7 block lists `fastapi` and `httpx` in `requirements.txt`, but no **Approval** entry permits the install.
  - Nothing else was changed. To continue, approve one of these:
    1. Permit `pip install fastapi` into the `ai-assisted-coding-demo-2` conda environment only, and pin the installed version in `requirements.txt` (`httpx==0.28.1` is already installed).
    2. Install `fastapi` yourself in that environment, then set the Status to `approved`.

### M8 — API ranked views

- **Refs:** JOB-002, CND-001, CND-002, CND-003, RNK-003, REC-001, MIS-001; DEC-002, design section 4.
- **Owner:** `src/workspace_views.py`, `src/api/jobs.py`, `src/api/candidates.py`, `src/api/schemas.py`.
- **Tests first:** in `tests/e2e/test_api_ranked_views.py`: `test_job_002_ranked_candidates_lists_all_candidates_best_first`, `test_rnk_003_ranked_candidate_has_extracted_and_calculated_attributes`, `test_rec_001_ranked_candidate_has_a_recommendation`, `test_mis_001_missing_value_is_null_in_the_json`, `test_cnd_001_candidate_detail_has_the_raw_cv_text`, `test_cnd_002_candidate_detail_has_extracted_and_calculated_attributes`, `test_cnd_003_ranked_jobs_lists_all_job_descriptions_best_first`, `test_job_002_unknown_job_returns_404_with_a_detail`, `test_cnd_001_unknown_candidate_returns_404_with_a_detail`.
- **Build:** the three endpoints `/api/jobs/{job_id}/ranked-candidates`, `/api/candidates/{candidate_id}` and `/api/candidates/{candidate_id}/ranked-jobs`, each calling one view function; a score or value that is `None` is `null` in the JSON.
- **Gate:** the tests and the checks pass; the JSON shapes match design section 4.

### M9 — Sample builder

- **Refs:** DEC-010, spec section 1 (the sample), design section 2.2.
- **Owner:** `scripts/build_sample.py`.
- **Tests first:** in `tests/unit/test_build_sample.py` (temporary folders, invented raw files): `test_dec_010_copies_three_job_descriptions_and_ten_cvs`, `test_dec_010_each_job_has_at_least_three_matching_cvs`, `test_dec_010_writes_ground_truth_with_the_expected_matches`, `test_dec_010_raw_input_is_not_modified`, `test_dec_010_refuses_to_overwrite_a_non_empty_output_folder`, `test_dec_010_writes_the_dataset_attribution`.
- **Build:** a script that takes the raw dataset folder, the output folder, the job IDs (`29243 32447 38671`) and the CV counts per job (`4 3 3`) as arguments, copies those files into `cvs/` and `job_descriptions/`, and writes `ground_truth.tsv` and an attribution text (TalentCLEF 2026, version 0.3.0, DOI 10.5281/zenodo.19652670, CC BY 4.0). It selects the first matching CVs in `qrels.tsv` order. Run it once to create `data/sample/` (ignored by Git).
- **Gate:** the tests and the checks pass; the report gives the counts in `data/sample/` (3 job descriptions, 10 CVs) and no CV content.

### M10 — Prompts and entry point

- **Refs:** EXT-001, JOB-001, PRG-003, LST-001, LST-002, NFR-001, NFR-002; DEC-003, DEC-007, DEC-013, DEC-014, design section 2.1.
- **Owner:** `main.py`, `prompts/extract_cv.md`, `prompts/match_cv_to_job.md`, `README.md`; `requirements.txt` (`uvicorn`).
- **Tests first:** in `tests/e2e/test_start_to_api.py` (fake reader folders with invented CVs, fake completer, fake embedder, fake vector index, test client): `test_ext_001_start_reads_the_cv_folder_and_the_api_lists_the_candidates`, `test_job_001_start_reads_the_job_folder_and_the_api_lists_the_jobs`, `test_prg_003_repeated_reads_do_not_trigger_new_llm_calls`, `test_dec_007_the_app_is_created_from_a_finished_workspace`, `test_lst_001_and_lst_002_lists_are_complete_after_start`.
- **Build:** the two prompt files (instruct the model to leave unknown fields `null`, use `YYYY-MM` dates, never guess, and for the recommendation to answer interview or not with a short reason); `main.py` loads config, sets up logging from settings, builds the reader, the OpenAI client, the two Chroma stores and the pipeline, runs the pipeline, then starts `uvicorn` on the configured loopback host and port. It holds no logic. README: What it does, Stack with versions, File structure, Setup (conda environment, `pip install -r requirements.txt`, `config/.env` and the OpenAI key, building the sample), How to run, How to test, and the manual live check (one run on the sample, compare the ranking with `ground_truth.tsv`, record the failure rate, the model IDs and the cost).
- **Gate:** the tests and the checks pass; the README has every section `CLAUDE.md` requires; the milestone does not call the real OpenAI service (the live run is the user's check).

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
