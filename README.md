# ai-assisted-coding-demo-2

## What it does

An app that takes a folder of CVs/resumes in PDF format and extracts information from each one. The user enters a search criteria. The app finds and ranks the best matching CVs. The search must be intelligent and semantic, not only keyword matching. This is a demo light-weight app.

## Stack

Python 3.12, conda environment `ai-assisted-coding-demo-2`, pytest, ruff, mypy

## File structure

| Path | Holds |
| --- | --- |
| `src/` | All source code. |
| `tests/` | `unit/` and `e2e/` tests. |
| `docs/` | Workflow, spec, design, and plan. |
| `config/` | `.env` (never committed) and `.env.example`. |
| `scripts/` | `check.py` (the checks), `milestones-runner.py`, `cleanup.py`, setup scripts. |
| `.claude/` | Claude Code settings, including the hook that checks each edit. |
| `.githooks/` | `pre-commit`: refuses a commit unless the checks pass. |
| `.vscode/` | Shared editor settings. |
| `data/` | Input and runtime data. |
| `models/` | Downloaded model weights (never committed). |
| `prompts/` | LLM prompt files. |

## Setup

```bash
conda create -n ai-assisted-coding-demo-2 python=3.12
conda activate ai-assisted-coding-demo-2
pip install -r requirements.txt
```

Copy `config/.env.example` to `config/.env` and fill in the values.

External dependencies (LLM server, models, API keys): none yet. Explain here how to set up and check each one before the first run.

After a fresh clone, turn on the pre-commit hook, which refuses a commit unless the checks pass:

```bash
git config core.hooksPath .githooks
```

## How to run

```bash
python main.py
```

## How to test

```bash
python -m pytest --cov=src --cov-branch --cov-fail-under=80
```
