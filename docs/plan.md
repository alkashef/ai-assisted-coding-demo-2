# Plan — ai-assisted-coding-demo-2

Only unfinished milestones. Delete a milestone's row and block in the commit that finishes it; git
history is the record. Template: `docs/workflow.md`.

**Next milestone number: M14**

## Milestones at a glance

| Milestone | Description | Model | Effort | Status |
| --- | --- | --- | --- | --- |
| **M1** Calculated attributes | Pure date math from facts: total period, jobs held, average, gaps, graduation, employed, countries, companies, last job | sonnet | high | open |
| **M2** Settings and file reading | Typed settings from `config/.env` with the key hidden; read the CV and job-description folders | sonnet | medium | open |
| **M3** LLM contract and request text | Ports, reply schemas, extraction and recommendation request and reply handling | sonnet | high | open |
| **M4** OpenAI client | The only module that calls OpenAI: structured replies and embeddings, errors wrapped as `LlmError` | sonnet | high | open |
| **M5** Vector store and ranking | Chroma collection, cosine nearest, items without a vector ranked last | sonnet | high | open |
| **M6** Start-up pipeline | Embed, extract, calculate, rank both ways and recommend; a failed call is recorded and the rest continue | opus | high | open |
| **M7** API app and lists | App factory on loopback, `/health`, job and candidate lists, failure list | sonnet | medium | open |
| **M8** API ranked views | Ranked candidates for a job, candidate detail, ranked jobs, 404 for an unknown ID | sonnet | medium | open |
| **M9** Sample builder | `scripts/build_sample.py`: 3 diverse jobs and 10 CVs from the raw dataset, with ground truth | sonnet | medium | open |
| **M10** Prompts and entry point | The two prompt files, `main.py`, start-to-API end-to-end test with fakes, README setup and manual live check | sonnet | high | open |
| **M11** Front-end shell and start page | `index.html`, tokens and layout, the lists and the failure notice, browser-test harness | sonnet | high | open |
| **M12** Job view UI | Ranked candidate cards from the mockups | sonnet | medium | open |
| **M13** Candidate view UI | Raw CV, attributes and ranked job descriptions | sonnet | medium | open |

## Milestones

### M1 — Calculated attributes

- **Refs:** CAL-001, CAL-002, CAL-003, CAL-004, CAL-005, CAL-007, CAL-008, EXT-007, EXT-008, EXT-009, EX-001, EX-002; DEC-005, design section 3 (records and calculation rules).
- **Owner:** `src/records.py` and `src/attributes.py`.
- **Tests first:** in `tests/unit/test_attributes.py`: `test_cal_008_duration_counts_both_months`, `test_cal_008_present_is_the_current_month`, `test_cal_001_total_period_is_first_start_to_current_month` (EX-001: 106), `test_cal_002_job_count` (EX-001: 3), `test_cal_003_average_is_sum_of_durations_over_job_count` (EX-001: 35.3), `test_cal_004_back_to_back_jobs_have_no_gap` (EX-001), `test_cal_004_gap_is_months_between_end_and_next_start`, `test_cal_004_overlapping_jobs_have_no_gap`, `test_cal_005_months_since_most_recent_graduation` (EX-002: 102), `test_cal_005_no_graduation_gives_none`, `test_cal_007_employed_when_latest_job_has_no_end`, `test_cal_007_not_employed_when_latest_job_has_an_end`, `test_ext_007_distinct_job_countries`, `test_ext_008_distinct_employers`, `test_ext_009_last_job_is_the_one_with_latest_start`, `test_cal_001_no_jobs_gives_none`.
- **Build:** frozen dataclasses in `records.py` (`Document`, `YearMonth`, `Job`, `Education`, `CvFacts`, `CalculatedAttributes`); pure functions in `attributes.py` that take the facts and today's date and return the calculated attributes and the derived lists. No I/O, no clock.
- **Gate:** the tests and the checks in `CLAUDE.md` pass (`python scripts/check.py`); EX-001 and EX-002 are reproduced exactly; `docs/design.md` section 3 is still accurate.

### M2 — Settings and file reading

- **Refs:** EXT-001, JOB-001, NFR-002; DEC-009, DEC-013, design section 2.3.
- **Owner:** `src/config.py`, `src/file_reader.py`, `config/.env.example`, `config/.env`.
- **Tests first:** in `tests/unit/test_file_reader.py`: `test_ext_001_reads_every_text_file_in_the_cv_folder`, `test_job_001_reads_every_text_file_in_the_job_folder`, `test_ext_001_missing_folder_stops_with_a_clear_message`, `test_ext_001_prompt_file_is_read_as_text`. In `tests/unit/test_config.py`: `test_nfr_002_settings_text_hides_the_api_key`, `test_nfr_002_log_summary_of_settings_omits_the_api_key`, `test_nfr_002_missing_setting_error_names_the_key_not_a_value`, `test_dec_013_server_host_comes_from_the_setting`.
- **Build:** `config.py` loads `config/.env` with `python-dotenv`, lets a real environment variable override it, and returns frozen settings objects grouped per component; the code has no defaults and a missing or invalid value fails at start-up. `file_reader.py` reads documents (ID is the file name, UTF-8, sorted by name) and single text files. Add every key in design section 2.3 to `config/.env.example` (non-secret keys with their default, `OPENAI_API_KEY` empty) and to the local `config/.env`.
- **Gate:** the tests and the checks pass; `config/.env` is not committed; every key in design section 2.3 is in `config/.env.example`.

### M3 — LLM contract and request text

- **Refs:** EXT-002, EXT-003, EXT-004, EXT-006, EXT-009, EXT-010, MIS-001, REC-001; DEC-005, DEC-006, DEC-011, design sections 3 and 4.
- **Owner:** `src/ports.py`, `src/llm_schemas.py`, `src/extraction.py`, `src/recommendation.py`; `requirements.txt` (`pydantic`).
- **Tests first:** in `tests/unit/test_extraction.py`: `test_ext_002_reply_name_becomes_facts_name`, `test_ext_003_reply_current_title_becomes_facts_current_title`, `test_ext_004_reply_skills_become_facts_skills`, `test_ext_006_reply_city_and_country_become_facts_address`, `test_ext_009_reply_jobs_keep_employer_location_title_dates_and_description`, `test_ext_010_reply_highest_degree_becomes_facts_highest_degree`, `test_mis_001_null_reply_field_becomes_none`, `test_ext_002_request_contains_the_cv_text`, `test_ext_002_bad_date_raises_llm_output_error_with_the_raw_output`. In `tests/unit/test_recommendation.py`: `test_rec_001_reply_becomes_a_recommendation_with_verdict_and_reason`, `test_rec_001_request_contains_the_job_text_and_the_candidate_facts`, `test_dec_006_request_excludes_name_address_and_contact_details`.
- **Build:** `ports.py` with the `StructuredCompleter`, `Embedder` and `VectorIndex` protocols and `LlmError` and `LlmOutputError` (carries the raw output); `llm_schemas.py` with the `pydantic` reply models; `extraction.py` and `recommendation.py` build the request text from a prompt template (placeholders `{{CV_TEXT}}`, `{{JOB_TEXT}}`, `{{CANDIDATE_FACTS}}`) and turn a validated reply into the records. Pure and synchronous. Install `pydantic` into the conda environment and pin it in `requirements.txt`.
- **Gate:** the tests and the checks pass; no test calls an LLM; `pydantic` is pinned and used by an import.

### M4 — OpenAI client

- **Refs:** NFR-001, NFR-002, ERR-001; DEC-003, DEC-006, DEC-011, design section 4 (ports).
- **Owner:** `src/llm_client.py`; `requirements.txt` (`openai`, `pytest-asyncio`).
- **Tests first:** in `tests/unit/test_llm_client.py` (async, with a fake SDK object): `test_nfr_001_client_is_built_with_the_configured_base_url`, `test_nfr_001_completion_sends_only_the_given_system_and_user_text`, `test_err_001_provider_error_becomes_llm_error_naming_the_operation_and_model`, `test_err_001_refusal_raises_llm_output_error_with_the_raw_output`, `test_nfr_002_llm_error_message_excludes_the_api_key`, `test_dec_003_complete_returns_an_instance_of_the_schema`, `test_dec_003_embed_returns_the_vector_for_the_text`.
- **Build:** one class that implements `StructuredCompleter` and `Embedder` with the official async SDK: a strict structured reply into the given schema, and an embedding call. Model IDs, base URL, key, token limit and timeout come in as typed settings. Wrap each provider exception in `LlmError` with context and the original error chained. Before using any SDK call, read the pinned version's documentation and use only calls that exist in it. Pin both libraries.
- **Gate:** the tests and the checks pass; no test uses the network; the report says which SDK calls were used and that the model IDs are untested until the live check in M10.

### M5 — Vector store and ranking

- **Refs:** RNK-001, MIS-002; DEC-004, DEC-011, design section 5 (Chroma risk).
- **Owner:** `src/vector_store.py`, `src/ranking.py`; `requirements.txt` (`chromadb`).
- **Tests first:** in `tests/unit/test_vector_store.py`: `test_rnk_001_nearest_orders_items_by_cosine_similarity`, `test_rnk_001_nearest_returns_every_stored_item`, `test_rnk_001_ties_are_ordered_by_item_id`, `test_dec_004_chroma_telemetry_is_disabled`, `test_dec_004_vectors_are_supplied_so_no_embedding_model_is_used`. In `tests/unit/test_ranking.py`: `test_mis_002_item_without_a_score_is_ranked_last`, `test_mis_002_unscored_items_are_ordered_by_id`, `test_mis_002_no_item_is_dropped`.
- **Build:** `ChromaVectorStore` implements `VectorIndex` with an in-memory Chroma client, telemetry off, cosine similarity, and our own vectors; `ranking.py` appends the unscored items. Check the pinned version's documentation for the cosine setting and the default embedding function, and use only calls that exist in it.
- **Gate:** the tests and the checks pass; the report states what was checked about the default model, telemetry and the cosine setting; `chromadb` is pinned.

### M6 — Start-up pipeline

- **Refs:** EXT-001, JOB-001, PRG-003, MIS-002, ERR-001, ERR-002, RNK-002, REC-001; DEC-005, DEC-007, DEC-008, design sections 2.1 and 3.
- **Owner:** `src/pipeline.py`; `src/records.py` (`Workspace`, `Recommendation`).
- **Tests first:** in `tests/unit/test_pipeline.py` (async, with fakes): `test_ext_001_every_cv_from_the_reader_is_in_the_workspace`, `test_job_001_every_job_description_from_the_reader_is_in_the_workspace`, `test_prg_003_each_cv_is_extracted_once`, `test_prg_003_each_document_is_embedded_once`, `test_prg_003_attributes_are_calculated_once_per_cv`, `test_rec_001_one_recommendation_per_job_and_cv_pair`, `test_rnk_002_rank_does_not_change_when_attributes_change`, `test_err_002_failed_extraction_keeps_the_other_results`, `test_err_001_failure_list_names_the_item_and_the_cause`, `test_err_002_failed_recommendation_leaves_that_pair_without_a_recommendation`, `test_mis_002_cv_with_a_failed_embedding_stays_in_every_ranking_last`, `test_dec_008_an_error_that_is_not_an_llm_error_is_not_caught`, `test_dec_007_calls_stay_within_the_concurrency_limit`.
- **Build:** `Pipeline.build(today)` runs the steps in DEC-007 with an async semaphore: read documents, embed into the two stores, extract, calculate, rank both ways with `ranking`, recommend per pair; returns one `Workspace`. It catches only `LlmError`, per item, in one place, records it in the failure list and continues (DEC-008). It logs progress at INFO.
- **Gate:** the tests and the checks pass; the only `except` for DEC-008 is in `pipeline.py` and names `LlmError`; no real LLM call.

### M7 — API app and lists

- **Refs:** LST-001, LST-002, ERR-001; DEC-002, DEC-012, DEC-013, design section 4.
- **Owner:** `src/workspace_views.py`, `src/api/app.py`, `src/api/jobs.py`, `src/api/candidates.py`, `src/api/status.py`, `src/api/schemas.py`; `requirements.txt` (`fastapi`, `httpx`).
- **Tests first:** in `tests/e2e/test_api_lists.py` (the framework's test client, a fake workspace): `test_lst_001_jobs_endpoint_lists_job_ids_and_titles`, `test_lst_002_candidates_endpoint_lists_candidate_ids_and_names`, `test_err_001_failures_endpoint_lists_item_and_cause`, `test_dec_002_health_endpoint_reports_alive`, `test_dec_002_static_front_end_is_served_from_the_web_root`. In `tests/unit/test_workspace_views.py`: `test_lst_001_job_list_has_id_and_title`, `test_lst_002_candidate_list_has_id_and_name`, `test_err_001_failure_list_has_item_and_cause`.
- **Build:** view functions in `workspace_views.py`; one router per domain whose handlers each call one view function; response models in `schemas.py`; `create_app(workspace, web_root)` includes the routers and mounts the static files last. No authentication and no CORS (DEC-013).
- **Gate:** the tests and the checks pass; handlers hold no logic; no server is started in tests.

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
