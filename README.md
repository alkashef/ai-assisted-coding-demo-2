# ai-assisted-coding-demo-2

## What it does

An app that takes a folder of CVs/resumes in plain-text format and a folder of job descriptions. At start-up it reads both folders, has an LLM extract facts from each CV, calculates attributes such as total experience and employment gaps, and ranks the CVs for each job description by semantic similarity (embeddings in a vector store). It also asks the LLM for a short "interview or not" recommendation per candidate and job. The user browses the results in a web page on their own machine. This is a demo light-weight app.

Requirements are in `docs/spec.md`, decisions in `docs/design.md`.

## Stack

- Python 3.12 in the conda environment `ai-assisted-coding-demo-2`
- FastAPI 0.143.0 and uvicorn 0.54.0: JSON API and static front end (plain JavaScript, no framework)
- OpenAI SDK `openai` 3.29.0: extraction, recommendations and embeddings
- `chromadb` 1.5.9: in-memory vector store; `pydantic` 2.14.1: reply schemas; `python-dotenv` 1.2.4: settings
- pytest 9.1.1, pytest-cov 7.1.0, pytest-asyncio 1.4.0, httpx 0.28.1, ruff 0.17.0, mypy 2.4.0
- Playwright 1.63.0 (Python): headless-browser tests that drive the installed Edge or Chrome (no browser download)

## File structure

| Path | Holds |
| --- | --- |
| `main.py` | The entry point: loads settings, runs the start-up pipeline, starts the server. |
| `src/` | All source code. `src/api/` is the HTTP layer, `src/web/` the front end (`index.html`, `css/`, `js/`). |
| `tests/` | `unit/` tests (Python, and `format.test.js` for the front end), `e2e/` API tests and `e2e/ui/` headless-browser tests. |
| `docs/` | Workflow, spec, design, plan, and the UI mockups in `docs/frontend/`. |
| `config/` | `.env` (never committed) and `.env.example`. |
| `scripts/` | `check.py` (the checks), `lock.py` (regenerates `constraints.txt`), `build_sample.py`, `milestones-runner.py`, `cleanup.py`. |
| `.github/workflows/` | `check.yml`: GitHub Actions runs `scripts/check.py` on every push to `main` and every pull request. |
| `constraints.txt` | The generated full pin list of every installed package (root file, beside `requirements.txt`). |
| `.claude/` | Claude Code settings, including the hook that checks each edit. |
| `.githooks/` | `pre-commit`: refuses a commit unless the checks pass. |
| `.vscode/` | Shared editor settings. |
| `data/` | Input data (ignored by Git). `data/sample/` is the demo sample. |
| `prompts/` | `extract_cv.md` and `match_cv_to_job.md`, the LLM prompts. |
| `logs/` | The log file (ignored by Git). |

## Setup

1. Create the environment and install the dependencies:

   ```bash
   conda create -n ai-assisted-coding-demo-2 python=3.12
   conda activate ai-assisted-coding-demo-2
   pip install -r requirements.txt -c constraints.txt
   ```

   `requirements.txt` lists the direct dependencies. `constraints.txt` pins every installed package, so every install gets the same versions. After you change `requirements.txt`, run `python scripts/lock.py` in the environment to regenerate it. Never edit it by hand. `python scripts/check.py` fails when it lacks a pin of `requirements.txt`.

2. Copy `config/.env.example` to `config/.env` and fill in the values. Every key is listed there. Set `OPENAI_API_KEY` to your OpenAI API key. Keep it only in `config/.env`, which Git ignores. A real environment variable overrides the file. The app stops at start-up with the name of any key that is missing or invalid.

3. Build the sample CVs and job descriptions. Download `TaskA.zip` from the [TalentCLEF 2026 record](https://zenodo.org/records/19652670), unzip it into `data/TaskA/`, then run (adjust the first path to the folder that holds `queries/`, `corpus/` and `qrels.tsv`):

   ```bash
   python scripts/build_sample.py data/TaskA/development/en data/sample --jobs 29243 32447 38671 --counts 4 3 3
   ```

   This writes `data/sample/cvs/`, `data/sample/job_descriptions/` and `ground_truth.tsv`. The raw files are only read. To use your own files instead, point `CV_FOLDER` and `JOB_FOLDER` at folders of `.txt` files.

4. Check the external service before the first run. The app sends CV text and job description text to OpenAI (`docs/design.md`, DEC-006) and nowhere else. Confirm that the key is valid, and that `LLM_MODEL` and `EMBEDDING_MODEL` in `config/.env` are model IDs your key can use. The defaults are untested until the first live run (see "Manual live check").

5. After a fresh clone, turn on the pre-commit hook, which refuses a commit unless the checks pass:

   ```bash
   git config core.hooksPath .githooks
   ```

## How to run

```bash
python main.py
```

The app first runs the start-up pipeline: it logs its progress and calls OpenAI (about 53 calls for the sample). Then it serves the page at `http://127.0.0.1:8000` (the host and port are in `config/.env`). The log is also written to `logs/app.log`.

## How to test

```bash
python -m pytest --cov=src --cov-branch --cov-fail-under=80
```

`python scripts/check.py` runs every check (the lock check, ruff, mypy, pytest, and the web checks). No automated test calls the real OpenAI service. GitHub Actions runs the same script on every push to `main` and every pull request, so a commit made with `--no-verify` is still caught.

The pytest run includes the headless-browser tests in `tests/e2e/ui/`. They start the app on `127.0.0.1` with a fake workspace and drive the installed Edge or Chrome, so one of them must be installed. To run only them: `python -m pytest tests/e2e/ui --no-cov`. The front-end checks are `npm run typecheck`, `npm run lint`, `npm run lint:css`, `npm run format:check` and `npm test` (after `npm install`).

### Manual live check

The automated tests use fakes, so one run with the real service is the user's check (DEC-003, DEC-004):

1. Run `python main.py` on the sample and wait for the page to be served.
2. For each job description, compare the order of the candidates with `data/sample/ground_truth.tsv`, which lists the CVs the dataset labels relevant. Those CVs should rank above the others.
3. Record the failure rate (`GET /api/failures`, or the failure notice on the start page) against the 40 expected LLM calls, the model IDs used (`LLM_MODEL`, `EMBEDDING_MODEL`) and the cost shown on the OpenAI usage page.
