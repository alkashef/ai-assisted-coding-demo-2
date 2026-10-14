# Plan — ai-assisted-coding-demo-2

Only unfinished milestones. Delete a milestone's row and block in the commit that finishes it; git
history is the record. Template: `docs/workflow.md`.

**Next milestone number: M23**

## Milestones at a glance

| Milestone | Description | Model | Effort | Status |
| --- | --- | --- | --- | --- |
| **M21** Evaluation command | `python main.py --evaluate`, `src/evaluation.py`, five settings (NFR-004, NFR-005, DEC-017) | sonnet | high | open |
| **M22** Gold file draft | Drafts `data/sample/gold_jobs.json` from the 10 sample CVs, with a `.gitignore` exception (NFR-005, DEC-017) | sonnet | high | open |

## Milestones

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
