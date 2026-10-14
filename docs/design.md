# Design — ai-assisted-coding-demo-2

How to build what `spec.md` says. If this file and the spec disagree, the spec wins.

Status: Approved.

## 1. Decisions

One current decision per topic. Delete a decision when it is replaced.

| ID | Decision | Status | Why (spec IDs, constraint) | Alternative not chosen | Check |
| --- | --- | --- | --- | --- | --- |
| DEC-001 | Python 3.12, conda environment `ai-assisted-coding-demo-2`, pytest, ruff, mypy | Approved (project setup) | Project constraint in `CLAUDE.md`. | None. | `python scripts/check.py` |
| DEC-002 | The interface is a local web page. A FastAPI server on `127.0.0.1` serves a JSON API and the static front end (plain JavaScript, no framework). The user opens it in a browser. | Approved by the user | The user chose a web page for a friendlier demo. The flow in LST-001, LST-002, CND-001 to CND-003 and JOB-002 is "list, select, view". | A terminal menu. Far less to build and test. It would be the better choice if build time matters more than the demo. | API tests with the framework's test client. One headless-browser test per UI workflow (DEC-012). |
| DEC-003 | One provider: OpenAI, called through the official `openai` Python SDK (async). It does the text extraction, the embeddings and the recommendations. The model IDs are settings: chat `gpt-6.1-sol` and embeddings `text-embedding-3-small`. | Approved by the user. Model IDs are untested until the first run. | The user has an OpenAI API key and asked to use it for embeddings and text extraction. NFR-001 allows one external service. One provider means one key and one failure mode. | Anthropic Claude. It has no embedding model and the user holds no key. | One manual run on the sample with the real service. Not yet run. Model IDs come from the OpenAI model page read on 2026-10-13 (https://developers.openai.com/api/docs/models) and are not tested. |
| DEC-004 | Semantic ranking uses embeddings in a Chroma vector store. Each CV and each job description is embedded once with the OpenAI embedding model and added to an in-memory Chroma collection (one collection for CVs, one for job descriptions). Our code supplies the vectors, so Chroma computes none and downloads no model. A collection returns the items nearest to a query vector by cosine similarity. The score of a pair is that similarity. Rank is the score, best first, ties broken by file name. An item without a vector is ranked last and shows "Not available". Chroma telemetry is off. The text that is embedded is in DEC-014. | Approved by the user | The user wants a vector store that embeds the CV text and matches by similarity. RNK-001, JOB-002, CND-003. JOB-002 searches the CV collection with a job description vector. CND-003 searches the job-description collection with a CV vector. | A small in-memory store written with the standard library: no dependency, but it is not a real vector database. FAISS: a search library, not a database. Weaviate: a server, a second external service and stored data. | Unit tests for the store module with a fake Chroma client or fixed vectors. Manual run of `python main.py --evaluate` (NFR-004, DEC-017): for each job description, at least 2 of the top 3 CVs are labeled relevant (planned, result unknown). |
| DEC-005 | The LLM extracts facts only (names, titles, employers, dates, degrees). Code calculates every derived attribute (CAL requirements) and derives the lists (EXT-007, EXT-008, EXT-009). | Approved by the user | The calculations are exact, testable with fakes and match EX-001 and EX-002. The LLM does only what needs language understanding. | Asking the LLM for the derived values. Faster to write but it is not testable and can miscount months. | Unit tests with EX-001 and EX-002. |
| DEC-006 | External data flow to OpenAI. The full CV text is sent for extraction and for embedding. The job description text is sent for embedding and for the recommendation. The recommendation prompt sends the job description and the candidate's extracted facts, without name, address or contact details. Nothing else leaves the machine. Telemetry is off. | Approved by the user | NFR-001 and the privacy rule in `CLAUDE.md`. `.claude/rules/llm.md` says to send only the fields the prompt needs. The sample is synthetic. A real CV would send personal data to OpenAI. | Sending the full CV to the recommendation prompt. Simpler, but it sends more personal data than needed. | Unit test that the recommendation request contains no name or contact detail. OpenAI's data-retention terms for API requests are not checked. |
| DEC-007 | `main.py` runs the pipeline before it starts the server: it reads both folders, embeds every document into the vector stores, extracts every CV, calculates attributes, ranks both ways and asks for one recommendation per pair. Then it serves the page. Calls run concurrently up to a limit from settings. Results live in memory for the run. The sample needs about 53 calls: 13 embeddings, 10 extractions and 30 recommendations. | Approved by the user | PRG-003, LST-001, LST-002. With PRG-001 and PRG-002 withdrawn, nothing is shown until the results are ready. The terminal logs the progress. No browser request waits on an LLM call. | Computing inside the server on first request. Starts faster, but the first page load waits and needs a loading state (the withdrawn PRG-002). | End-to-end test: the app is created only from a finished workspace. |
| DEC-008 | A failed LLM call for one CV or one pair is recorded, not raised. Only `LlmError` is caught, in `src/pipeline.py`. The failed result becomes "Not available" and its cause goes to the failure list. Any other exception still stops the app with the raw stack trace. | Approved by the user (exception to the rule) | ERR-001 and ERR-002 require the app to keep showing the other results. `.claude/rules/code-quality.md` says never to catch in order to continue. This decision is the one deliberate exception to that rule. | Follow the rule and stop on the first LLM failure. It means withdrawing ERR-002 from the approved spec. | Tests: a fake LLM that fails for one CV leaves the other results visible and shows the cause. |
| DEC-009 | No data is written. The app only reads the sample folders and writes logs. Candidate and job IDs are the file names, so no generated UUIDs are needed. | Approved by the user | `.claude/rules/data.md`. Nothing in the spec needs storage. | A database or a cache file. It would save LLM cost on re-runs. Not needed for a PoC. | None. |
| DEC-010 | The sample is built by `scripts/build_sample.py` from the raw TalentCLEF files into `data/sample/`. The raw files stay read-only. | Approved by the user | The sample decision in spec section 1. `data/*` is ignored by Git, so the sample is regenerated, not committed. | Hand-copying files. Not repeatable. | Run the script; check 3 job descriptions, 10 CVs, at least 3 matches each. |
| DEC-011 | New direct dependencies for the LLM and vector work: `openai` (the OpenAI client), `pydantic` (the reply schemas that the SDK validates against), `chromadb` (the vector store, DEC-004), `pytest-asyncio` (async tests). Each is pinned when first imported. | Approved by the user | `CLAUDE.md` asks before any dependency. The standard library has no OpenAI client or vector database. A schema gives strict structured output and validation (OpenAI Structured Outputs, `responses.parse` with a Pydantic model; documented at https://developers.openai.com/api/docs/guides/structured-outputs, read 2026-10-13, not tested). `pytest.ini` already sets `asyncio_mode`. | Raw HTTP with the standard library and hand-written validation. No new dependency but about 150 more lines to write and test. | `pip install -r requirements.txt` and `python scripts/check.py`. |
| DEC-012 | New direct dependencies for the web interface: `fastapi` and `uvicorn` (server; `.claude/rules/http-apis.md` requires FastAPI), `httpx` (needed by FastAPI's test client), `playwright` (the headless-browser tool for UI tests, using the installed Edge or Chrome instead of a downloaded browser). | Approved by the user | `CLAUDE.md` says `docs/design.md` chooses the browser tool and the user approves it. The standard library has no ASGI server and no browser driver. | A Node-based browser tool (`@playwright/test`), which adds a second test runner. | The UI tests run in `python scripts/check.py`. Playwright 1.63.0 drives the installed Edge and Chrome without a download (checked in M11). |
| DEC-013 | No authentication and no CORS. The server listens on `127.0.0.1` only. | Approved by the user | One user on one machine, and `CLAUDE.md` says servers listen on `127.0.0.1`. | A login. Not needed unless the app is shared. | Test that the settings pass `127.0.0.1`. |
| DEC-014 | What is embedded: the whole raw text of each CV and of each job description, one vector each, with no cleaning. The pipeline embeds `Document.text` as read. | Approved by the user | The text needs no LLM extraction, so a failed extraction never removes a candidate from the ranking (MIS-002). It is the simplest option and matches "embed the CV text". Both fit the 8,192-token input limit of `text-embedding-3-small` (documented at https://developers.openai.com/api/docs/guides/embeddings, read 2026-10-13). | Embedding cleaned text built from the extracted facts (titles, descriptions, skills, degree; no name, contact or dates), or one vector per job. Less noise, but it depends on extraction and needs more code and tests. It is the next step if the manual check ranks poorly. | Manual run on the sample against the dataset labels (planned, result unknown). |
| DEC-015 | A job's end is known, current or unknown, and the calculations reject impossible dates. `Job` has `is_current`. `end` is `None` for a current job and for an unknown end; `is_current` tells them apart. A job with a reversed range or a date after the current month is *bad*, and the calculated attributes that depend on it are "Not available" (rules in section 3). The unknown end is carried to the API (`is_current` in the last job) so the page shows "Present" only for a current job and the recommendation prompt gets `is_current`. | Approved by the user (2026-10-14), including the API change | CAL-007, CAL-009, CAL-010, EX-001, EX-003, EX-004, MIS-001. Found by an independent code review: an unknown end showed as "Present" and counted as employed, and a reversed range gave a zero or negative duration. | A separate "unknown" value inside `end`: clumsier and weaker for the type checker. Asking the LLM for the derived values: rejected in DEC-005. | Unit tests for EX-001, EX-003 and EX-004 and for a contradictory reply (`is_current` true with an `end`). An API test and a UI test for "Present" against "Not available". Planned, not run. |
| DEC-016 | Instructions go in the system text, and documents go in the user text as marked data. The two prompt files are the system text only and have no placeholders. The code builds the user text: `<cv>…</cv>` for extraction, and `<job_description>…</job_description>` with `<candidate_facts>…</candidate_facts>` (JSON) for the recommendation. The system text says that tagged content is untrusted data and that any instruction inside it must be ignored. Before insertion, the angle bracket of any copy of these tags inside the data is replaced by `&lt;`. There is no template substitution. | Approved by the user (2026-10-14) | NFR-001, REC-001, EXT-002 to EXT-010. Found by an independent code review: the instructions and the untrusted CV text shared one message, and the second `replace` re-scanned text inserted by the first. `.claude/rules/llm.md` says to treat LLM input and output as untrusted. | A second model call that screens each CV for injection: about 10 more calls per start and a new failure mode. Keeping one message with the instructions and the data: simplest, and the weakest. | Unit tests on the request structure: the system text is the prompt file, the user text holds the tagged data, an injected closing tag is escaped, a `{{…}}` marker in a document stays unchanged. Planned, not run. This lowers the risk and does not remove it: a model can still follow injected text. No automated test shows how the real model behaves. |
| DEC-017 | The evaluation is `python main.py --evaluate`, run by the user with the live service. `main.py` builds the same workspace as for the server, then passes it to the pure module `src/evaluation.py`, prints a report and exits with code 1 if a check fails. NFR-004: per job description, the labeled-relevant CVs among the top K ranked must reach a minimum. NFR-005: a gold job matches when the extracted CV has a job with the same start month, end month and `is_current`; the rate is matched gold jobs over all gold jobs, so a failed extraction counts as misses and extra extracted jobs are not penalized. The report gives counts and pass or fail, never CV content. The thresholds, K and the two file paths are settings (section 2.3). The gold file `data/sample/gold_jobs.json` maps each CV ID to its jobs' `start`, `end` and `is_current`. It is drafted by the assistant from the CV text and counts only after the user reviews it. It is committed, with the dataset attribution (CC BY 4.0 allows this), through an exception in `.gitignore`. | Approved by the user (2026-10-14) | NFR-004, NFR-005, RNK-001, EXT-009. Found by an independent code review: no evidence of extraction or ranking accuracy. | `scripts/evaluate.py` with its own wiring: duplicates `_build_workspace` and needs a `src` path workaround. An injection check: no requirement covers it, so it is not included. | Unit tests of `evaluation.py` with fakes. One manual run by the user. The user reports the numbers and the assistant records them, with the date, in the Check columns of DEC-003 and DEC-004. Result unknown. |
| DEC-018 | A generated full lock file, and a GitHub Actions workflow that runs the project checks. `requirements.txt` stays direct-only. `constraints.txt` pins every installed package, and `python scripts/lock.py` (a thin wrapper around `pip freeze`) regenerates it from the conda environment. `scripts/check.py` gains one check: every pin in `requirements.txt` appears in `constraints.txt` with the same version. `.github/workflows/check.yml` runs on every push to `main` and every pull request: set up Python 3.12 and Node, `pip install -r requirements.txt -c constraints.txt`, `pip check`, `npm ci`, then `python scripts/check.py`. The runner is Windows (`windows-latest`). The workflow needs no secrets and no user data: the tests use fakes. Each action is pinned to an exact version resolved when the workflow is built. | Approved by the user (2026-10-14), including the `CLAUDE.md` changes | `CLAUDE.md` (Dependencies, Testing). Found by an independent code review: indirect dependencies float, and the checks run only in a local hook that `--no-verify` skips. | `pip-tools` or `uv` for locking: a new dependency, and `pip freeze` is enough for one environment. A Linux runner: needs a second lock, because the platform-specific lines differ. | Unit test of the lock check in `check.py`. The first CI run, watched by the user. Unverified: the action versions, and whether the tests run without `config/.env`. Planned, not run. |
| DEC-019 | UI layout: a frozen header, and file names as a small grey second line. The `app-header` stays at the top of the window while the page scrolls (plain CSS, `position: sticky`, no JavaScript). The navigation and the main area scroll beneath it. A file name (the ID) is a second line directly under the name or title, in the small size and `--color-muted`, in four places: navigation items (label, then file name, left-aligned), candidate cards (name, file name, then "title. city"), the candidate view heading (name, file name, then the title as meta) and the job view heading (title, file name, then "All N candidates, best match first." as meta). The ranked job rows in the candidate view stay as they are. | Approved by the user (2026-10-14) | LST-001, LST-002, CND-001 to CND-003, JOB-002. A user request. No requirement mentions file names or the header, so the spec is unchanged. `.claude/rules/ui-design.md` (standard layout, quick). | Freezing the header and the selected view's title bar, or the navigation panel: the user chose the header only. | Two headless-browser tests: scrolling the page keeps the header's top edge at 0, and a file name sits below its name in a smaller size. Planned, not run. Visual reference: `docs/frontend/README.md` (updated). The `*.dc.html` mockups are not updated. |
| DEC-020 | A job-detail response, and the job description text as a panel above the ranked candidates. `GET /api/jobs/{job_id}` returns `id`, `title` and `text` (the raw text as read), and 404 with a `detail` message for an unknown ID. `workspace_views.job_detail` builds it. The job view loads the job and the ranked candidates together and shows the text in a `<details open>` panel titled "Job description text", above the cards. It reuses the `.doc` component, in a scrollable box whose maximum height is a new token in `theme.css`. The user can fold the panel. | Approved by the user (2026-10-14), including the new endpoint | JOB-003, JOB-002. A user request. The text is already in the workspace, so no new data leaves the machine. | Two columns with the text beside the cards, as in the candidate view: squeezes the dense cards on a laptop screen. The text added to the ranked-candidates response: turns the array into an object, which breaks the contract, and gives no 404 of its own. | A unit test for `job_detail`, an API test for the endpoint and the 404, and one headless-browser test that selecting a job shows its text above the ranked candidates. Planned, not run. |

## 2. Architecture

### 2.1 Components

Flat Python modules under `src/`, an `api/` package for the HTTP layer and a `web/` folder for the browser files.

| Layer | Module | Single responsibility | Spec IDs |
| --- | --- | --- | --- |
| Entry | `main.py` | Loads config, sets up logging, creates the objects, runs the pipeline, then starts the server, or with `--evaluate` prints the evaluation report instead (DEC-017). No logic. | all |
| Settings | `src/config.py` | The only module that reads `config/.env` and the environment. Returns typed settings. | NFR-002 |
| Domain (pure, synchronous) | `src/records.py` | Typed records: documents, extracted facts, calculated attributes, recommendations, workspace. | all |
| Domain | `src/prompt_data.py` | Wraps a document in a fixed tag and escapes any copy of the known tags inside it (DEC-016). The tag names are an enum. Standard library only. | NFR-001, EXT-002, REC-001 |
| Domain | `src/extraction.py` | Builds the extraction user text (the tagged CV, DEC-016) and turns the validated reply into facts. A reply that gives both `is_current` and an `end` is refused. | EXT-002 to EXT-010, MIS-001 |
| Domain | `src/attributes.py` | Calculates the CAL attributes and derives the EXT-007 to EXT-009 values from the facts and a given date. | CAL-001 to CAL-005, CAL-007 to CAL-010 |
| Domain | `src/recommendation.py` | Builds the recommendation user text (the tagged job description and candidate facts, DEC-016) from the job description and the candidate facts (no name or contact), and turns the validated reply into a recommendation. | REC-001 |
| Domain | `src/llm_schemas.py` | The reply shapes the LLM must return, as `pydantic` models: the CV facts and the recommendation. | EXT-002 to EXT-010, REC-001 |
| Domain | `src/evaluation.py` | Parses the ground truth and the gold file, and checks the workspace against them: the ranking hits per job description and the job-date match rate. Pure. It reads no file and calls no service. | NFR-004, NFR-005 |
| Domain | `src/ranking.py` | Appends the items that have no score to a ranked list, ordered by ID, so that none is dropped. | MIS-002, RNK-002 |
| Gateway | `src/vector_store.py` | The only module that talks to Chroma. Adds vectors by ID and returns every stored item nearest to a query vector as (ID, similarity), best first. Implements `VectorIndex`. | RNK-001, JOB-002, CND-003 |
| Contract | `src/ports.py` | The `StructuredCompleter`, `Embedder` and `VectorIndex` protocols and the `LlmError` types. | ERR-001 |
| Application | `src/pipeline.py` | Runs the start-up steps in DEC-007. Catches `LlmError` per item (DEC-008). Returns one in-memory workspace. | EXT-001, JOB-001, PRG-003, MIS-002, ERR-001, ERR-002 |
| Application | `src/workspace_views.py` | Builds the data for each read from the workspace: the lists, a job detail, a ranked candidate list, a candidate detail, a ranked job list. | LST-001, LST-002, CND-001 to CND-003, JOB-002, JOB-003, RNK-003 |
| API | `src/api/app.py` | The app factory. Creates FastAPI, includes the routers, mounts the static front end. | DEC-002 |
| API | `src/api/jobs.py`, `src/api/candidates.py`, `src/api/status.py` | One router per domain. Each handler calls one `workspace_views` function. `status.py` serves `/health` and the failure list. | LST-001, LST-002, CND-001 to CND-003, JOB-002, JOB-003, ERR-001 |
| API | `src/api/schemas.py` | The response models. | all read endpoints |
| Browser | `src/web/` | The front end, see section 2.2. | LST-001, LST-002, CND-001 to CND-003, JOB-002, ERR-001, MIS-001 |
| Gateway | `src/file_reader.py` | The only module that reads plain-text files: documents from a folder, prompt files, and the two evaluation files (DEC-017). | EXT-001, JOB-001, NFR-004, NFR-005 |
| Gateway | `src/llm_client.py` | The only module that calls OpenAI. Implements both protocols: structured completion and embedding. | NFR-001 |

Import rules. A module imports only from rows above it, or from itself:

- Domain modules import only `records` and `prompt_data` (and the standard library, plus `pydantic` for the schemas).
- `pipeline` imports domain modules, `llm_schemas` and `ports`. It receives the file reader, the LLM client and the two vector stores as arguments.
- `workspace_views` imports `records` and the pure functions of `attributes` (last job, distinct countries and employers). The pipeline has already ranked both ways.
- `src/api/*` imports `workspace_views`, `records` and the schemas. A handler never imports a gateway, the pipeline or the domain directly.
- Gateways import `records`, `llm_schemas` and `ports` only.
- Only `main.py` imports `config`, and it passes values down as typed settings objects.
- Browser code reaches data only through `api.js` (`.claude/rules/javascript.md`).

Start-up flow (DEC-007):

1. `main.py` builds the file reader, the LLM client, the two vector stores and the pipeline.
2. The pipeline reads the job descriptions and CVs, then runs one extraction call per CV.
3. It calculates the attributes with today's date, passed in from `main.py`.
4. It embeds every CV and job description into the two vector stores, ranks both ways by cosine similarity, and asks for one recommendation per pair.
5. It returns the workspace: documents, facts, attributes, ranked lists with scores, recommendations and the failure list.
6. `main.py` creates the app from the workspace and starts the server. The user opens the page.

Browser flow:

1. The page loads the job-description list and the candidate list (LST-001, LST-002), and the failure list (ERR-001).
2. The user selects a job description. The page shows the ranked candidates with attributes and recommendations (JOB-002).
3. The user selects a candidate. The page shows the raw CV, the attributes and the ranked job descriptions (CND-001 to CND-003).

Failure paths:

- An LLM call fails or returns invalid output: `LlmError` is raised at the client or the validator, and the pipeline records it (DEC-008). The page shows each cause in a failure panel, and the results that succeeded.
- A field the LLM cannot find is `null` in the schema. The page shows "Not available" (MIS-001). The candidate stays in every list (MIS-002).
- A missing folder, a missing prompt file or a missing setting stops the app at start-up with a clear message.
- An unknown ID in the URL returns 404 with a `detail` message.

### 2.2 Directory structure

Create a folder only when it is listed here, and update this table in the same change.

| Path | Holds |
| --- | --- |
| `src/` | All source code: the flat modules in section 2.1. |
| `src/api/` | The FastAPI app factory, routers and response models. |
| `src/web/` | The front end. `index.html` (with `<template>` elements), `css/` (`theme.css`, `base.css`, `layout.css`, `detail.css`) and `js/` (`main.js`, `config.js`, `log.js`, `api.js`, `format.js`, `attribute-fill.js`, `list-view.js`, `job-view.js`, `candidate-view.js`, `failures-view.js`). |
| `tests/` | `unit/` (one test file per source module, plus `format.test.js`), `e2e/` (the API with a fake workspace and a fake LLM) and `e2e/ui/` (headless-browser tests). |
| `docs/` | Workflow, spec, design, and plan. |
| `docs/frontend/` | The UI mockups (`*.dc.html`, `mockup.css`) and `README.md`, the visual reference for `src/web/`. |
| `config/` | `.env` (never committed) and `.env.example`. |
| `scripts/` | `check.py` (the checks), `milestones-runner.py`, `cleanup.py`, `build_sample.py` (DEC-010), `lock.py` (DEC-018), setup scripts. |
| `.github/workflows/` | `check.yml`: runs `scripts/check.py` on every push and pull request (DEC-018). |
| Root files | `constraints.txt`: the generated full pin list (DEC-018), beside `requirements.txt`. |
| `.claude/` | Claude Code settings, including the hook that checks each edit. |
| `.githooks/` | `pre-commit`: refuses a commit unless the checks pass. |
| `.vscode/` | Shared editor settings. |
| `data/` | Input data. The raw TalentCLEF files are in `data/TaskA/`. `data/sample/` holds `cvs/`, `job_descriptions/` and `ground_truth.tsv`, generated by `build_sample.py`, and `gold_jobs.json`, reviewed by the user and committed (DEC-017). |
| `prompts/` | `extract_cv.md` and `match_cv_to_job.md`. |
| `logs/` | The log file. Ignored by Git. |

`models/` is not used: the app has no local model.

### 2.3 Settings

All settings come from `config/.env` (or the environment). `config/.env.example` lists every key. The code has no defaults.

| Setting | Default | Meaning |
| --- | --- | --- |
| `OPENAI_API_KEY` | empty (secret) | API key. Never logged (NFR-002). |
| `LLM_BASE_URL` | `https://api.openai.com/v1` | The OpenAI endpoint. |
| `LLM_MODEL` | `gpt-6.1-sol` | Exact chat model ID, never an alias. |
| `LLM_MAX_TOKENS` | `2048` | Output limit per call. |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Exact embedding model ID. |
| `LLM_TIMEOUT_SECONDS` | `60` | Time limit for one call. |
| `LLM_MAX_CONCURRENCY` | `5` | Calls in flight at once. |
| `CV_FOLDER` | `data/sample/cvs` | Folder of plain-text CVs. |
| `JOB_FOLDER` | `data/sample/job_descriptions` | Folder of plain-text job descriptions. |
| `EXTRACT_PROMPT_PATH` | `prompts/extract_cv.md` | Extraction system prompt file. |
| `MATCH_PROMPT_PATH` | `prompts/match_cv_to_job.md` | Match system prompt file. |
| `EVAL_GROUND_TRUTH_PATH` | `data/sample/ground_truth.tsv` | Relevance labels for the evaluation (DEC-017). |
| `EVAL_GOLD_JOBS_PATH` | `data/sample/gold_jobs.json` | Reviewed job dates for the evaluation (DEC-017). |
| `EVAL_TOP_K` | `3` | How many top-ranked CVs the ranking check looks at (NFR-004). |
| `EVAL_MIN_RELEVANT_IN_TOP_K` | `2` | Labeled-relevant CVs needed among the top K, per job description (NFR-004). |
| `EVAL_MIN_DATE_MATCH_PERCENT` | `90` | Share of gold jobs whose dates must match (NFR-005). |
| `WEB_ROOT` | `src/web` | Folder of the static front end. |
| `SERVER_HOST` | `127.0.0.1` | Address the server listens on (DEC-013). |
| `SERVER_PORT` | `8000` | Port the server listens on. |
| `LOG_LEVEL` | `INFO` | Log level. |
| `LOG_FILE` | `logs/app.log` | Log file path. |

The front end has its own `config.js` for the API base path and the "Not available" text.

## 3. Data model

All data is in memory for one run (DEC-009). IDs are file names. An ID is unique only within its kind: a job description and a candidate may share one, so a route, a cache key or a stale-response check must include the kind as well as the ID. Records are frozen dataclasses in `src/records.py`.

| Record | Fields |
| --- | --- |
| `Document` | `doc_id` (file name), `text`. A job description's title is its first line. |
| `YearMonth` | `year`, `month`. |
| `Job` | `title`, `employer`, `city`, `country`, `start`, `end`, `is_current`, `description`. A job with an `end` has ended. A job with no `end` and `is_current` true is current ("Present"). A job with no `end` and `is_current` false has an unknown end (DEC-015). |
| `Education` | `degree`, `university`, `major`, `graduated` (a `YearMonth`). |
| `CvFacts` | `name`, `current_title`, `skills`, `city`, `country`, `highest_degree`, `jobs`, `education`. Every field except the lists may be `None`. |
| `CalculatedAttributes` | `total_months`, `job_count`, `average_job_months`, `gaps` (a list of month counts), `months_since_graduation`, `currently_employed`. Each may be `None` (MIS-001). |
| `Recommendation` | `interview` (true or false), `reason` (text). |
| `Failure` | `item_id` (a file name, or `<job ID> + <CV ID>` for a recommendation), `cause` (the step and the `LlmError` message). |
| `Workspace` | `cvs`, `jobs` (documents), `facts` and `attributes` per CV ID (absent when extraction failed), `ranked_candidates` per job ID, `ranked_jobs` per CV ID (each a list of (ID, score), best first), `recommendations` per (job ID, CV ID) pair, `failures` (the failure list). A score is `None` for an item with no vector. |

Rules for the calculations (CAL-008, EX-001, EX-002):

- Duration in months counts both the start month and the end month. "Present" is the month of the date passed in, and only a job with `is_current` is Present.
- A job is *bad* when its end is before its start, or its start or end is after the current month (CAL-010). A job has an *unknown end* when it has no `end` and is not current (CAL-009).
- Job count is always the number of jobs (CAL-002).
- Total employment period is the months from the earliest job start to the current month. It is "Not available" when any job is bad.
- Average time per job is the sum of the job durations divided by the number of jobs. It is "Not available" when any job is bad or has an unknown end.
- A gap is the months between one job's end and the next job's start, counted only when the next job starts more than one month after. Overlaps give no gap. Gaps are "Not available" when any job is bad or has an unknown end.
- Currently employed is "Not available" when any job is bad. Otherwise it is true when the latest job is current, false when it has an end, and "Not available" when its end is unknown.
- Time since graduation counts from the most recent graduation to the current month. It is "Not available" when any graduation date is after the current month.
- A bad date never changes the extracted facts: the dates are shown as written.
- EXT-007 is the distinct job countries. EXT-008 is the distinct employers. EXT-009 is the job with the latest start.

Evaluation files (DEC-017), read by `main.py` through the file reader and parsed by `src/evaluation.py`:

- `ground_truth.tsv`: a `job_id<TAB>cv_id` header, then one labeled-relevant pair per line. The IDs are the dataset IDs; the parser adds `.txt` to match the file names.
- `gold_jobs.json`: `attribution` (the dataset attribution line) and `cvs`, which maps each CV ID (file name) to a list of jobs, each with `start` (`YYYY-MM`), `end` (`YYYY-MM` or `null`) and `is_current` (true or false).
- A check with nothing to check fails: no labeled job description, or no gold job. An unreadable file or a wrong format stops the run with a message before any LLM call.

LLM output contract (a `pydantic` model in `src/llm_schemas.py`, validated by the SDK, DEC-011):

- Extraction reply: the `CvFacts` fields, dates as `YYYY-MM` or `null`. Each job has `is_current`, true only when the CV marks the job current. A year-only end is `null` with `is_current` false. A job with `is_current` true and an `end` is refused as `LlmOutputError` (DEC-015).
- Recommendation facts (the JSON in the prompt) carry each job's `is_current` beside its `end`.
- Recommendation reply: `interview` (true or false) and `reason` (text).
- A refusal or any other shape raises `LlmOutputError` with the raw output. There is no repair and no retry.
- The prompt file is the system text and holds every instruction. The user text holds only the tagged documents, built by the code (DEC-016).

## 4. Interfaces

JSON API (read-only, all GET, no request bodies). Public endpoints; there is no login (DEC-013).

| Path | Returns |
| --- | --- |
| `/health` | Liveness. |
| `/api/jobs` | The job descriptions: ID and title (LST-001). |
| `/api/jobs/{job_id}` | One job description: ID, title and the raw text (JOB-003). |
| `/api/candidates` | The candidates: ID and name (LST-002). |
| `/api/jobs/{job_id}/ranked-candidates` | All candidates, best match first, each with score, recommendation, extracted attributes and calculated attributes (JOB-002, RNK-003, REC-001). |
| `/api/candidates/{candidate_id}` | The raw CV text, the extracted attributes and the calculated attributes (CND-001, CND-002). |
| `/api/candidates/{candidate_id}/ranked-jobs` | All job descriptions, best match first, each with its score (CND-003). |
| `/api/failures` | The failure list: item ID and cause (ERR-001). |

An unknown ID returns 404 with a `detail` message. A missing value is `null` in the JSON. The browser shows "Not available" (MIS-001).

The last job in the candidate responses has `end` and `is_current` (DEC-015). The browser shows the end as "Present" when `is_current` is true, and as "Not available" when `end` is `null` and `is_current` is false.

The ports (`src/ports.py`): `StructuredCompleter.complete(system, user, schema)` returns an instance of the schema, `Embedder.embed(text)` returns a vector, and `VectorIndex` has `add(item_id, vector)` and `nearest(vector)`, which returns every stored item as (ID, similarity), best first. The first two are asynchronous. The LLM calls raise `LlmError` on any provider failure. `LlmOutputError` (a kind of `LlmError`) carries the raw output.

Test boundaries:

- Unit tests use fakes for the file reader and the LLM client.
- End-to-end tests call the API with the framework's test client, a fake workspace and a fake LLM.
- UI tests start the app on `127.0.0.1` with a fake workspace, drive a headless browser, and cover LST-001, LST-002, CND-001 to CND-003, JOB-002, JOB-003 and ERR-001.
- No automated test uses the real LLM service, the real clock or the real data.

## 5. Risks and unknowns

| Risk | Blocks | Owner | Resolution |
| --- | --- | --- | --- |
| The reply could be refused or malformed, and the rules forbid repair and retry. That CV or pair then fails (DEC-008). | Nothing | Plan | Strict structured output makes this unlikely. The manual run shows the failure rate. |
| Embedding similarity may rank poorly across very different roles, or score all CVs close together, so ranking quality is unknown. | Nothing | User | Planned manual check against the dataset labels. Result unknown. |
| Cost and rate limits for about 53 calls per start are unverified. The model IDs and the chat model's supported settings are unverified. | Nothing | User | Check current pricing, limits and the model page at first run. |
| The web interface adds a server, a front end, checks for JavaScript and CSS, and a browser test per UI workflow, so it takes noticeably longer to build than a terminal menu. | The one-hour goal | User | The user chose the web page (DEC-002). The plan keeps the front end to the minimum in section 2.2. |

## 6. Approval

**Approved by the user** on 2026-10-13, in the `/write-design` session ("approve"), for the whole design as written, including DEC-008 (the exception to the rule against catching in order to continue) and these direct dependencies: `openai`, `pydantic`, `chromadb`, `fastapi`, `uvicorn`, `httpx`, `playwright` and `pytest-asyncio`. Each is installed and pinned in the milestone that first imports it, into the project's conda environment only.

**Amendments, approved by the user on 2026-10-14 ("yes"), from an independent code review:**

- DEC-015 and the changes it made to sections 2.1, 3 and 4. Spec amendments of the same day: CAL-007, CAL-009, CAL-010.
- DEC-016 and the changes it made to sections 2.1, 2.3 and 3.
- DEC-017 and the changes it made to sections 2.1, 2.2 and 2.3. Spec wording change of the same day: the evidence for NFR-004 and NFR-005 is `python main.py --evaluate`.
- DEC-019 (a user request, no spec change).
- DEC-020 and the changes it made to sections 2.1 and 4. Spec amendment of the same day: JOB-003.
- DEC-018 and the changes it made to section 2.2. The user also approved two changes to `CLAUDE.md`: the `constraints.txt` rule under Dependencies, and the directory table rows for `lock.py`, `.github/` and `constraints.txt`.
