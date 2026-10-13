# Design — ai-assisted-coding-demo-2

How to build what `spec.md` says. If this file and the spec disagree, the spec wins.

## 1. Decisions

One current decision per topic. Delete a decision when it is replaced.

| ID | Decision | Why |
| --- | --- | --- |
| DEC-001 | Python 3.12, conda environment `ai-assisted-coding-demo-2`, pytest, ruff, mypy | TBD |

## 2. Architecture

### 2.1 Components

TBD

### 2.2 Directory structure

Create a folder only when it is listed here, and update this table in the same change.

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

### 2.3 Settings

| Setting | Default | Meaning |
| --- | --- | --- |

## 3. Data model

TBD

## 4. Interfaces

TBD
