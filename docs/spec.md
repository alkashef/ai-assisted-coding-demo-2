# Spec — ai-assisted-coding-demo-2

Status: Approved

What to build. Written with `/write-spec`. Change only with the user's approval. Each requirement is
in EARS syntax and has an ID that tests cite.

## 1. Purpose and scope

A light-weight proof-of-concept app that takes a folder of CVs/resumes as plain-text files and extracts information from each one. The user enters a job description as the search input. The app finds and ranks the best matching CVs. The search must be intelligent and semantic, not only keyword matching.

**Problem.** A hiring manager, or a recruiter helping them, cannot rely on keyword search to find good candidates, because keywords do not capture the meaning of a job description. The manager then reads many CVs by hand, which is slow. Some important signals are not stated in a CV and must be deduced, for example the average time a candidate stayed in each job (about 6 months is a red flag).

**Scope (draft).**

- In: plain-text CVs in a folder; a job description as the query; semantic ranking; deduced signals such as average job tenure.
- Out: PDF input (decided with the user: plain text only); real CVs.
- Constraint: the sample data is a small subset of TalentCLEF 2026 Task A (English, development set), described in `data/talentclef-dataset-description.md`. Its records are synthetic. The relevance labels in `qrels.tsv` can serve as the expected results.
- Sample (user decision): 3 diverse job descriptions and 10 CVs, with at least 3 matching CVs per job description. In the dataset every CV is labeled relevant to exactly one job description, so a CV labeled for one job description is a non-match for the other two. Job descriptions (confirmed by the user): Healthcare Data Analyst (`29243`), Senior Mechanical/HVAC Engineer (`32447`), Retail Mortgage Loan Closer (`38671`).

**Outcome evaluation.** Not yet defined. See section 7.

## 2. Roles and glossary

- **Manager:** the hiring manager who decides whom to interview. Decision-maker.
- **Recruiter:** helps the manager. Uses the app the same way.
- **User:** a manager or a recruiter.
- **Candidate:** a person whose CV is a plain-text file in the CV folder.
- **Job description:** a plain-text file in the job-description folder.
- **Extracted attribute:** a fact read from a CV (EXT requirements).
- **Calculated attribute:** a value computed from extracted facts (CAL requirements).
- **Semantic match:** closeness in meaning between a CV and a job description, not keyword overlap.
- **Recommendation:** an LLM-generated statement on whether to interview a candidate for a job description.

## 3. User scenarios

Status of all scenarios: drafted by the assistant from the interview; approved with the spec.

**SCN-001: Find the best candidates for an open role.**

- Actor and goal: a hiring manager or recruiter wants to decide whom to interview for a role.
- Trigger and preconditions: the system has started; the job-description and CV folders contain plain-text files.
- Main path: the user selects a job description; the system shows all candidates ranked by semantic match, each with its extracted attributes, calculated attributes and an LLM recommendation; the user compares them and picks candidates to interview.
- Alternate and failure paths: an attribute cannot be determined (MIS-001, MIS-002); the LLM service fails (ERR-001, ERR-002).
- Observable result: a ranked candidate list with attributes and recommendations.
- Requirements: JOB-001, LST-001, JOB-002, RNK-001 to RNK-003, REC-001.

**SCN-002: Review one candidate.**

- Actor and goal: the same user wants to understand one candidate and see where the candidate fits.
- Trigger and preconditions: the system has started.
- Main path: the user selects a candidate; the system shows the raw CV, the extracted and calculated attributes, and the job descriptions ranked by match.
- Alternate and failure paths: as in SCN-001.
- Observable result: the candidate's raw CV, attributes and ranked job descriptions.
- Requirements: EXT-001 to EXT-010, CAL-001 to CAL-005, CAL-007, CAL-008, LST-002, CND-001 to CND-003.

## 4. Functional requirements

| ID | EARS requirement | Priority | Status | Business reason | Source | Scenarios | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EXT-001 | When the system starts, it shall read each plain-text CV file in the CV folder. | Must | Confirmed | The manager no longer reads CVs by hand. | User statement | SCN-001 | TBD |
| EXT-002 | When the system reads a CV, it shall extract the candidate's name. | Must | Confirmed | Identify the candidate in the ranked list. | User statement ("all of the above") | SCN-001, SCN-002 | TBD |
| EXT-003 | When the system reads a CV, it shall extract the candidate's current job title. | Must | Confirmed | Decision attribute. | User statement | SCN-001, SCN-002 | TBD |
| EXT-004 | When the system reads a CV, it shall extract the candidate's skills. | Must | Confirmed | Decision attribute. | User statement | SCN-001, SCN-002 | TBD |
| EXT-005 | Withdrawn: replaced by EXT-010 and EXT-011. | — | Withdrawn | The user asked for more specific education attributes. | User statement (interview 1) | — | — |
| EXT-006 | When the system reads a CV, it shall extract the candidate's current address as a city and a country. | Must | Confirmed | Decision attribute. | User statement | SCN-001, SCN-002 | TBD |
| EXT-007 | When the system reads a CV, it shall extract the list of countries where the candidate has worked. | Must | Confirmed | Decision attribute. | User statement | SCN-001, SCN-002 | TBD |
| EXT-008 | When the system reads a CV, it shall extract the list of companies the candidate has worked for. | Must | Confirmed | Decision attribute. | User statement | SCN-001, SCN-002 | TBD |
| EXT-009 | When the system reads a CV, it shall extract the candidate's last job: employer, location, duration, title, and a brief description. | Must | Confirmed | The last job shows current level and relevance. | User statement | SCN-001, SCN-002 | TBD |
| EXT-010 | When the system reads a CV, it shall extract the candidate's highest degree. | Must | Confirmed | Decision attribute. | User statement (interview 1) | SCN-001, SCN-002 | TBD |
| EXT-011 | When the system reads a CV, it shall extract the list of university and major pairs the candidate attended. | — | Withdrawn (user trim, interview 1) | Decision attribute. | User statement (interview 1) | — | — |
| CAL-001 | When the system reads a CV, it shall calculate the candidate's total employment period. | Must | Confirmed | Decision attribute. | User statement | SCN-001, SCN-002 | EX-001 |
| CAL-002 | When the system reads a CV, it shall calculate the number of jobs the candidate has held. | Must | Confirmed | Decision attribute. | User statement | SCN-001, SCN-002 | EX-001 |
| CAL-003 | When the system reads a CV, it shall calculate the candidate's average time per job. | Must | Confirmed | A short average, such as 6 months, is a red flag that the manager must otherwise deduce by hand. | User statement (interview 1) | SCN-001, SCN-002 | EX-001 |
| CAL-004 | When the system reads a CV, it shall identify employment gaps between jobs. | Must | Confirmed | Decision attribute. | User statement ("all of the above") | SCN-001, SCN-002 | EX-001 |
| CAL-005 | When the system reads a CV, it shall calculate, in months, the time between the candidate's graduation and today, whether the candidate was employed or not. | Must | Confirmed | Decision attribute. Inference: "graduation" is the candidate's most recent graduation. | User statement | SCN-001, SCN-002 | EX-002 |
| CAL-006 | When the system reads a CV, it shall classify the move from the candidate's previous job to the last job by comparing seniority level and field: upgrade (higher seniority), downgrade (lower seniority), horizontal (similar seniority, different field or function), or same (similar seniority, same field). | — | Withdrawn (user trim, interview 1) | Decision attribute. The LLM judges seniority and field from job titles and descriptions. A CV with a single job gives "Not available" (MIS-001). | User statement; user decision (accepted recommendation) | — | — |
| CAL-007 | When the system reads a CV, it shall determine whether the candidate is currently employed, as yes or no. | Must | Confirmed | Decision attribute. Inference: the candidate is currently employed when the last job has no end date ("Present"). | User statement (interview 1) | SCN-001, SCN-002 | EX-001 |
| CAL-008 | When the system calculates a duration in months, it shall count both the start month and the end month, and treat "Present" as the current month. | Must | Confirmed | A job that ends in May followed by one that starts in June is not a gap, and the total employment period equals the span from the first start to now. | User decision (accepted recommendation) | SCN-001, SCN-002 | EX-001, EX-002 |
| JOB-001 | When the system starts, it shall read each plain-text job-description file in the job-description folder. | Must | Confirmed | Job descriptions are supplied as files in a separate folder, like the dataset's query files. | User statement (interview 1) | SCN-001 | TBD |
| LST-001 | When the system starts, it shall list the job descriptions. | Must | Confirmed | The user browses from either side. | User statement (interview 1) | SCN-001 | TBD |
| LST-002 | When the system starts, it shall list the candidates. | Must | Confirmed | The user browses from either side. | User statement (interview 1) | SCN-002 | TBD |
| CND-001 | When the user selects a candidate, the system shall show the raw CV text of the candidate. | Must | Confirmed | The manager can check the source. | User statement (interview 1) | SCN-002 | TBD |
| CND-002 | When the user selects a candidate, the system shall show the extracted attributes (EXT-002 to EXT-010, except withdrawn EXT-005) and the calculated attributes (CAL-001 to CAL-005 and CAL-007) of the candidate. | Must | Confirmed | The manager decides from these attributes without reading the CV. Inference: the user said "calculated attributes"; extracted attributes are included. | User statement, with inference | SCN-002 | TBD |
| CND-003 | When the user selects a candidate, the system shall show the job descriptions ranked by their semantic match to the candidate, best match first. | Must | Confirmed | The manager sees where the candidate fits best. The list has no LLM recommendation. | User statement (interview 1); user decision (no recommendation here) | SCN-002 | TBD |
| JOB-002 | When the user selects a job description, the system shall show all candidates ranked by their semantic match to the job description, best match first. | Must | Confirmed | The manager sees the whole ranking beside the LLM recommendation (REC-001). No threshold is needed. | User statement ("qualified candidates"); user decision (accepted recommendation) | SCN-001 | TBD |
| PRG-001 | When the system starts, it shall show the job-description list and the candidate list without waiting for the attributes and recommendations to be computed. | — | Withdrawn (user trim, interview 1) | The user can browse the raw CVs right away. | User decision (accepted recommendation) | — | — |
| PRG-002 | While an attribute or a recommendation is being computed, the system shall show "Computing…" in its place, and replace it with the result when ready. | — | Withdrawn (user trim, interview 1) | The user gets feedback during the wait. | User decision (accepted recommendation) | — | — |
| PRG-003 | The system shall compute the attributes of each CV once per start and reuse them in every view. | Must | Confirmed | Avoids repeated LLM calls and cost. | User decision (accepted recommendation) | SCN-001, SCN-002 | TBD |
| MIS-001 | If the system cannot determine an attribute of a CV, then it shall show "Not available" for that attribute and shall not guess a value. | Must | Confirmed | The manager can tell a missing attribute from an extracted one and is not misled. | User decision (accepted recommendation) | SCN-001, SCN-002 | TBD |
| MIS-002 | If the system cannot determine an attribute of a CV, then it shall keep the candidate in the candidate list and in every ranking. | Must | Confirmed | A gap in a CV must not hide a good candidate. | User decision (accepted recommendation) | SCN-001, SCN-002 | TBD |
| ERR-001 | If the external LLM service is unavailable or rejects a request, then the system shall show an error message that names the cause. | Must | Confirmed | The manager knows why a result is missing. | User decision (accepted recommendation) | SCN-001, SCN-002 | TBD |
| ERR-002 | If the external LLM service is unavailable or rejects a request, then the system shall keep showing the lists, the raw CV texts, and every result already computed, and shall show "Not available" for each result that failed. | Must | Confirmed | The app stays usable and nothing is faked. | User decision (accepted recommendation) | SCN-001, SCN-002 | TBD |
| ERR-003 | When the user asks to retry after an LLM failure, the system shall repeat the failed requests. | — | Withdrawn (user trim, interview 1) | Partial results can be completed without restarting. | User decision (accepted recommendation) | — | — |
| RNK-001 | The system shall rank by semantic match, not by keyword match alone. | Must | Confirmed | Keyword search misses the meaning of a job description. | User statement (interview 1) | SCN-001 | TBD |
| RNK-002 | The system shall not use the calculated attributes (CAL-001 to CAL-005 and CAL-007) to determine rank. | Must | Confirmed | The manager judges the red flags. Rank stays predictable. | User decision (accepted recommendation) | SCN-001 | TBD |
| RNK-003 | When the system shows a ranked list of candidates, it shall show for each candidate the extracted attributes (EXT-002 to EXT-010, except withdrawn EXT-005) and the calculated attributes (CAL-001 to CAL-005 and CAL-007). | Must | Confirmed | The manager decides from these attributes without opening the CV. | User statement | SCN-001 | TBD |
| REC-001 | When the system shows a ranked list of candidates for a job description, it shall show for each candidate a recommendation generated by an LLM on whether to interview the candidate for that job description. | Must | Confirmed | The manager decides from the attributes and the recommendation. | User statement | SCN-001 | TBD |

Use `AREA-NNN` for IDs, for example `PAY-001`. Distinguish Proposed, Confirmed, and Withdrawn
requirements. A confirmed requirement still needs the spec approval before implementation.

## 5. Non-functional requirements

| ID | EARS requirement | Priority | Status | Business reason | Source | Acceptance evidence |
| --- | --- | --- | --- | --- | --- | --- |
| NFR-001 | The system shall send CV text and job-description text only to the external LLM service approved in `docs/design.md`. | Must | Confirmed | The user allows an external LLM service. `CLAUDE.md` requires every external data flow to be approved and listed in the design. | User decision (interview 1) | TBD |
| NFR-002 | The system shall not show, log or store the LLM service credentials in any message, log or file other than `config/.env`. | Must | Confirmed | A leaked key has cost and security impact. `CLAUDE.md` requires secrets to stay in `config/.env`. | `CLAUDE.md` (Security and privacy) | TBD |
| NFR-003 | When the system starts on the 10-CV sample with the external LLM service available, it shall have computed all extracted and calculated attributes within 2 minutes. | — | Withdrawn (user trim, interview 1) | The manager does not wait long. The 2-minute limit is the assistant's proposal, accepted by the user by following the recommendation. | User decision (accepted recommendation) | One manual run with the real service on the sample (automated tests cannot use a live LLM or a real clock, per `CLAUDE.md`) |

Use `NFR-NNN` for IDs. State the relevant workload, conditions, and measurable acceptance limits.
Keep unknown limits in the open questions. Do not invent values.

## 6. Acceptance examples

| ID | Requirement IDs | Situation and input | Expected result | Reviewed by |
| --- | --- | --- | --- | --- |
| EX-002 | CAL-005, CAL-008 | A CV lists a Bachelor's degree with "Graduated: May 2018" (invented, modeled on dataset CV `49`). Today is October 2026. | Time since graduation: 102 months (May 2018 to October 2026, counting both months). | User (approved with the spec) |
| EX-001 | CAL-008, CAL-001, CAL-002, CAL-003, CAL-004, CAL-007 | A CV lists three jobs: Jan 2018 to May 2019, Jun 2019 to Dec 2021, and Jan 2022 to Present. Today is October 2026. (Invented dates, modeled on dataset CV `49`.) | Durations are 17, 31 and 58 months. Total employment period is 106 months. Number of jobs is 3. Average time per job is about 35.3 months. Employment gaps: none (0 months). Currently employed: yes. | User (accepted the counting rule and these values in the interview) |

Record the actual reviewer or mark the example as awaiting review.
Link rules by ID instead of repeating their text.

## 7. Assumptions and open questions

| Item | Evidence or assumption | Consequence if wrong | Owner | Resolution or revisit condition |
| --- | --- | --- | --- | --- |
| Withdrawn to trim the PoC (user, so it can be built in about an hour): PRG-001, PRG-002, ERR-003, NFR-003, CAL-006, EXT-011 | User decision, interview 1 | The start-up shows no progress, there is no retry and no timing target, and the career move, education pairs are not provided | User | Restore with a spec amendment |
| CAL-001: "total employment period" and "total years of experience" are treated as one attribute: the months from the first job's start to the current month (CAL-008), with gaps shown separately (CAL-004) | Inference: both were requested in some form and EX-001 gives 106 months | Duplicate or different attributes wanted | User | Accepted with the spec approval |
| Acceptance examples exist only for CAL-001 to CAL-005, CAL-007 and CAL-008. Other requirements have none yet | Tests cite requirement IDs; examples for the remaining rules can be written in the plan's tests | Rules without a reviewed example may be misread | User | Add examples by amendment if a misreading appears |
| The interface (command line, local web page, other). The user's flow is interactive: lists, then selection | The spec states behavior only; the design chooses the interface | Affects the layers, dependencies and UI tests | User, in `/write-design` | Decide in the design |
| Which external LLM service, and whether the semantic search also uses an external embedding service | User allows an external service (NFR-001). The choice is not made | Affects cost, secrets and privacy | User, in `/write-design` | Decide in the design with a `DEC-NNN` |
| The dataset has no CVs labeled non-relevant (all 472 labels are `1`) | Inspection of `qrels.tsv` | The sample can test only that labeled CVs rank above CVs labeled for other job descriptions | User | Accept as a limit, or add synthetic non-matches |

## 8. Review and approval

**Approved by the user** on 2026-10-13, in the `/write-spec` interview ("i approve the specs").

- Scope: the whole spec as it stands, including the 34 Must requirements, scenarios SCN-001 and SCN-002, examples EX-001 and EX-002, NFR-001 and NFR-002, and the six withdrawn requirements (PRG-001, PRG-002, ERR-003, NFR-003, CAL-006, EXT-011) plus withdrawn EXT-005.
- The user declined a deeper cut (CND-003, CAL-004, ERR-002 and the second tier EXT-006, EXT-007, EXT-008).
- Left to the design (`/write-design`): the interface, the external LLM and embedding service, and the `DEC-NNN` for the external data flow.
- Amendments: record the approved change and affected IDs here. Preserve IDs and withdrawn rows.
