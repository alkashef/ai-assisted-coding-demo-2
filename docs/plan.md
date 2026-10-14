# Plan — ai-assisted-coding-demo-2

Only unfinished milestones. Delete a milestone's row and block in the commit that finishes it; git
history is the record. Template: `docs/workflow.md`.

**Next milestone number: M23**

## Milestones at a glance

| Milestone | Description | Model | Effort | Status |
| --- | --- | --- | --- | --- |
| **M22** Gold file draft | Drafts `data/sample/gold_jobs.json` from the 10 sample CVs, with a `.gitignore` exception (NFR-005, DEC-017) | sonnet | high | open |

## Milestones

### M22 — Gold file draft

- **Refs:** NFR-005, DEC-017.
- **Owner:** `data/sample/gold_jobs.json`, `.gitignore`.
- **Tests first:** none new. The file is data, and tests may not read real data. The M21 parser is the check, run in the Gate.
- **Build:** read the 10 synthetic sample CVs in `data/sample/cvs/` and write `data/sample/gold_jobs.json` in the format M21 defined: for each job its `start`, `end` and `is_current`, taken only from what the CV states (a job with no stated end and no "Present" has `is_current` false and a `null` end), plus the dataset attribution line. Add the `.gitignore` exception for this one file. Add a README line that the user must review the file before NFR-005 counts.
- **Gate:** the M21 parser accepts the file; `git check-ignore` shows the gold file is not ignored and the rest of `data/sample/` still is; the report gives only counts (CVs and jobs), no CV content, and says the file is a draft until the user reviews it.
