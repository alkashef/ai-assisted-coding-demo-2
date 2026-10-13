# Plan — ai-assisted-coding-demo-2

Only unfinished milestones. Delete a milestone's row and block in the commit that finishes it; git
history is the record. Template: `docs/workflow.md`.

**Next milestone number: M23**

## Milestones at a glance

| Milestone | Description | Model | Effort | Status |
| --- | --- | --- | --- | --- |
| **M16** End states and impossible dates | `Job.is_current`, the extraction reply, and the "Not available" rules in `attributes.py` (CAL-007, CAL-009, CAL-010, DEC-015) | sonnet | high | open |
| **M17** Show the unknown end | `is_current` in the API's last job, the recommendation facts, and the page ("Present" or "Not available") (DEC-015) | sonnet | medium | open |
| **M18** Prompt isolation | Prompt files become system text, and the documents go in as tagged, escaped user text (DEC-016) | opus | high | open |
| **M19** Job description text | `GET /api/jobs/{job_id}` and the foldable text panel above the candidates (JOB-003, DEC-020) | sonnet | medium | open |
| **M20** Frozen header and file names | Sticky header and the grey file-name lines in four places (DEC-019) | sonnet | medium | open |
| **M21** Evaluation command | `python main.py --evaluate`, `src/evaluation.py`, five settings (NFR-004, NFR-005, DEC-017) | sonnet | high | open |
| **M22** Gold file draft | Drafts `data/sample/gold_jobs.json` from the 10 sample CVs, with a `.gitignore` exception (NFR-005, DEC-017) | sonnet | high | open |

## Milestones

### M16 — End states and impossible dates

- **Refs:** CAL-007, CAL-009, CAL-010, CAL-002, EX-001, EX-003, EX-004, MIS-001, DEC-015.
- **Owner:** `src/records.py`, `src/llm_schemas.py`, `src/extraction.py`, `src/attributes.py`, `prompts/extract_cv.md`.
- **Tests first:** in `tests/unit/test_attributes.py`: `test_cal_007_current_marker_gives_yes`, `test_cal_007_end_date_gives_no`, `test_cal_007_unknown_end_is_not_available` (EX-003), `test_cal_009_unknown_end_makes_average_and_gaps_not_available` (EX-003), `test_cal_002_job_count_unaffected_by_bad_or_unknown_dates`, `test_cal_010_reversed_range_makes_dependents_not_available` (EX-004 a), `test_cal_010_future_job_date_makes_dependents_not_available`, `test_cal_010_future_graduation_makes_time_since_graduation_not_available` (EX-004 b), `test_cal_001_ex_001_values_unchanged`. In `tests/unit/test_extraction.py`: `test_dec_015_current_marker_with_an_end_is_refused`, `test_dec_015_reply_is_current_flows_into_the_job`.
- **Build:** `Job` gets `is_current`; `JobReply` gets a required `is_current`; `extraction.py` refuses a reply with `is_current` true and an `end` (`LlmOutputError` with the raw output); `attributes.py` applies the rules in design section 3 ("Rules for the calculations"); `prompts/extract_cv.md` states that `is_current` is true only when the CV marks the job current and that a year-only end is `null` with `is_current` false. Update every existing test and fake that builds a `Job`. The tests that cite CAL-007 change because the requirement changed: say so in the report.
- **Gate:** the tests and the checks pass; EX-001, EX-003 and EX-004 pass as written in the spec; the report lists the changed CAL-007 tests.

### M17 — Show the unknown end

- **Refs:** CAL-007, CAL-009, EXT-009, REC-001, MIS-001, DEC-015, DEC-006.
- **Owner:** `src/workspace_views.py`, `src/api/schemas.py`, `src/recommendation.py`, `src/web/js/format.js`, `src/web/js/api.js`.
- **Tests first:** `test_ext_009_last_job_view_has_is_current` (unit, `test_workspace_views.py`), `test_ext_009_api_last_job_has_end_and_is_current` (e2e), `test_rec_001_facts_carry_is_current_beside_end` (`test_recommendation.py`), `formatLastJob shows Present only when is_current` and `formatLastJob shows Not available for an unknown end` (`format.test.js`), `test_ext_009_ui_unknown_end_shows_not_available` and `test_ext_009_ui_current_job_shows_present` (UI).
- **Build:** the last-job object gets `is_current`; the recommendation facts JSON gets `is_current` beside `end` (still no name or contact detail); `format.js` shows "Present" only for a current job and "Not available" for an unknown end; update the API typedef in `api.js`.
- **Gate:** the tests and the checks pass; design section 4 matches the API shape.

### M18 — Prompt isolation

- **Refs:** EXT-002 to EXT-010, REC-001, NFR-001, DEC-016.
- **Owner:** `src/extraction.py`, `src/recommendation.py`, `src/pipeline.py`, `prompts/extract_cv.md`, `prompts/match_cv_to_job.md`, and one new domain module `src/prompt_data.py` (single responsibility: wrap a text in a fixed tag and escape copies of the tags inside it; the tag names are an enum there).
- **Tests first:** `test_ext_002_user_text_wraps_the_cv_in_a_tag`, `test_dec_016_closing_tag_inside_the_cv_is_escaped`, `test_dec_016_placeholder_marker_inside_the_cv_is_unchanged`, `test_rec_001_user_text_wraps_job_and_facts_in_tags`, `test_rec_001_marker_inside_the_facts_is_not_replaced_by_the_job_text`, `test_dec_016_pipeline_sends_the_prompt_file_as_the_system_text` (`test_pipeline.py`), `test_dec_016_prompt_files_have_no_placeholders_and_name_the_untrusted_data_rule`. Test files: `test_prompt_data.py` and the existing ones for each module.
- **Build:** `prompt_data.py` as above (a domain module: it imports only the standard library); `extraction.py` and `recommendation.py` build the tagged user text; the pipeline passes the prompt file text as `system` and the tagged text as `user`; both prompt files lose their `{{...}}` markers and gain the rule that tagged content is untrusted data and any instruction in it is ignored (keep the `is_current` rule from M16). Add the `prompt_data.py` row to design section 2.1 in the same change.
- **Gate:** the tests and the checks pass; no prompt file contains `{{`; the report says that no automated test shows how the real model behaves.

### M19 — Job description text

- **Refs:** JOB-003, JOB-002, DEC-020.
- **Owner:** `src/workspace_views.py` (`job_detail`), `src/api/jobs.py`, `src/api/schemas.py`, `src/web/js/api.js`, `src/web/js/job-view.js`, `src/web/js/main.js`, `src/web/index.html`, `src/web/css/detail.css`, `src/web/css/theme.css`.
- **Tests first:** `test_job_003_job_detail_returns_id_title_and_text` and `test_job_003_job_detail_unknown_id_raises_not_found` (unit), `test_job_003_api_returns_the_job_text` and `test_job_003_api_unknown_job_returns_404_with_detail` (e2e), `test_job_003_ui_selecting_a_job_shows_its_text_above_the_ranked_candidates` (UI).
- **Build:** `job_detail` and the route `GET /api/jobs/{job_id}`; `getJob` in `api.js`; the job view loads the job and the ranked candidates together and shows the text in a `<details open>` panel titled "Job description text" above the cards, with the `.doc` component in a scrollable box. The maximum height is a new token in `theme.css`; the stale-response guard from M15 applies to it. The text is inserted with `textContent`. Update `docs/frontend/README.md` if it differs.
- **Gate:** the tests and the checks pass; design section 4 lists the endpoint.

### M20 — Frozen header and file names

- **Refs:** DEC-019, LST-001, LST-002, CND-001, JOB-002.
- **Owner:** `src/web/css/layout.css`, `src/web/css/detail.css`, `src/web/index.html`, `src/web/js/list-view.js`, `src/web/js/job-view.js`, `src/web/js/candidate-view.js`.
- **Tests first:** `test_dec_019_ui_header_stays_at_the_top_when_the_page_scrolls`, `test_dec_019_ui_navigation_file_name_is_below_the_label_in_small_grey_text`, `test_dec_019_ui_card_file_name_is_below_the_name`, `test_dec_019_ui_job_and_candidate_headings_show_the_file_name_below_the_title`.
- **Build:** `.app-header` becomes sticky (plain CSS, no JavaScript); the file name moves to a second line in the small size and `--color-muted` in the navigation items, the candidate cards, and the candidate and job view headings, as in DEC-019; the heading meta lines lose the "CV <id>." and "Job description <id>." text. The existing UI tests that look for that text change because the design changed: say so in the report. The ranked job rows stay as they are.
- **Gate:** the tests and the checks pass; `docs/frontend/README.md` matches; the report lists the changed UI tests.

### M21 — Evaluation command

- **Refs:** NFR-004, NFR-005, RNK-001, EXT-009, DEC-017.
- **Owner:** `src/evaluation.py`, `src/file_reader.py`, `src/config.py`, `main.py`, `config/.env.example`, `config/.env`, `README.md`.
- **Tests first:** in `tests/unit/test_evaluation.py`: `test_nfr_004_counts_the_relevant_cvs_in_the_top_k_per_job`, `test_nfr_004_fails_below_the_minimum`, `test_nfr_004_a_cv_without_a_score_ranks_last`, `test_nfr_005_matches_a_job_by_start_end_and_current`, `test_nfr_005_a_failed_extraction_counts_as_misses`, `test_nfr_005_extra_extracted_jobs_are_not_penalized`, `test_nfr_005_fails_below_the_percent`, `test_dec_017_report_has_counts_and_pass_fail_but_no_cv_content`, `test_dec_017_parses_the_ground_truth_and_the_gold_file`. In `test_config.py`: `test_dec_017_loads_the_five_evaluation_settings`. In `tests/e2e/test_main.py`: `test_dec_017_evaluate_flag_prints_the_report_and_starts_no_server`, `test_dec_017_evaluate_flag_exits_with_code_1_when_a_check_fails`.
- **Build:** `src/evaluation.py` (pure, as in DEC-017); `FileReader` reads the ground truth and the gold file; the five `EVAL_*` settings in the five places `CLAUDE.md` lists (`config/.env.example`, `config/.env`, a typed field in `config.py`, the design settings table which is already there, and `main.py` passing them down); `main.py --evaluate`; the README "How to run" and Setup gain the evaluation. Choose the gold file keys and record them in design section 3: `attribution` plus, for each CV ID, the jobs with `start`, `end` and `is_current`.
- **Gate:** the tests and the checks pass; `--evaluate` was not run against the live service (say so); the README explains that NFR-004 and NFR-005 need one manual run by the user.

### M22 — Gold file draft

- **Refs:** NFR-005, DEC-017.
- **Owner:** `data/sample/gold_jobs.json`, `.gitignore`.
- **Tests first:** none new. The file is data, and tests may not read real data. The M21 parser is the check, run in the Gate.
- **Build:** read the 10 synthetic sample CVs in `data/sample/cvs/` and write `data/sample/gold_jobs.json` in the format M21 defined: for each job its `start`, `end` and `is_current`, taken only from what the CV states (a job with no stated end and no "Present" has `is_current` false and a `null` end), plus the dataset attribution line. Add the `.gitignore` exception for this one file. Add a README line that the user must review the file before NFR-005 counts.
- **Gate:** the M21 parser accepts the file; `git check-ignore` shows the gold file is not ignored and the rest of `data/sample/` still is; the report gives only counts (CVs and jobs), no CV content, and says the file is a draft until the user reviews it.
