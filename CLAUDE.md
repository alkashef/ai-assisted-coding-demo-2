# CLAUDE.md

## Project

- Purpose: An app that takes a folder of CVs/resumes in plain-text format and extracts information from each one. The user enters a search criteria. The app finds and ranks the best matching CVs. The search must be intelligent and semantic, not only keyword matching. This is a demo light-weight app.
- Stack: Python 3.12, conda environment `ai-assisted-coding-demo-2`, pytest, ruff, mypy
- Test command: python -m pytest --cov=src --cov-branch --cov-fail-under=80
- Run command: python main.py
- Project rules: none yet (rules that apply only to this project, including protected paths)

## Identity and source of truth

The objective is clean, maintainable code for humans and machines. Humans can read and change it.
Machines (AI agents, type checkers, linters, tests) can navigate and verify it. All code is written
by AI. Follow every rule in this file exactly.

- `docs/workflow.md`, `spec.md`, `design.md`, and `plan.md` always exist.
  `workflow.md` says what each is for.
- Requirements live only in `docs/spec.md`. Never implement one that exists only in chat, code, or
  memory. If a request is not covered by the spec or contradicts it, stop and ask.
- Write the spec in EARS syntax (ubiquitous, event, state, unwanted-behavior, optional-feature),
  one requirement per statement.
- Every requirement has a stable ID `AREA-NNN` (`NFR-NNN` for non-functional). Every design decision
  has a `DEC-NNN` in `docs/design.md`. Never renumber or reuse an ID. Mark a retired requirement
  "withdrawn".
- Cite spec and design IDs. Do not copy their content into this file or into code comments.

## Workflow

Follow the workflow in @docs/workflow.md exactly.

Do not refactor, rename, or move anything outside the current milestone.

## Communication and reporting

- Be very concise and direct. No narration, no recap beyond the report below.
- Go top-down, big picture first. Handle one thing at a time: one item, question, or suggestion per
  message.
- When you ask the user to decide, give a recommendation and brief pros and cons.
- When discussing requirements, design, the plan, or an approach the user proposes, act as a
  rigorous critical-thinking partner: challenge assumptions, expose blind spots, test the
  reasoning, present alternatives, and agree only when the argument is strong. In the spec act as a
  product manager; in the design act as a software architect. While executing an approved
  milestone, do not debate. Flag only blockers and spec conflicts.

End every task that changes files with this report, one line per item:

- **Files changed:** a list.
- **Tests added or updated:** a list.
- **Tests run:** N passed out of M.
- **Assumptions and open questions:** very concise.
- **TLDR: what I need to know if I read nothing else.** (last, whole line in bold)

## Architecture and layers

- `docs/design.md` defines the layers and their import rules. Follow them. Before writing code,
  name the module that owns the change. Before creating a module, state its name, layer, and single
  responsibility.
- One module per concern. Entry points (the main script, the app factory, the front-end main
  module) only import and connect modules. They hold no logic.
- Business logic is pure: no HTTP, UI, or database imports. Transport and UI layers only translate
  and delegate.
- Exactly one module talks to each external system (a file area, a database, a network API, an
  LLM). A module exposes only what others need and never reaches into another module's internals.
- Pass anything that touches an external system (repository, API client, file writer, LLM client)
  into the code that uses it, so tests can use fakes. Do not use a dependency-injection framework.
- Changing a layer, a module boundary, the data model, the public API, or the tech stack needs the
  user's approval and a `DEC-NNN` in `docs/design.md`.

## Directory structure

| Path | Holds |
| --- | --- |
| `src/` | All source code. `docs/design.md` has the detailed layout. |
| `tests/` | `unit/`, `e2e/`, and `e2e/ui/`. |
| `docs/` | `workflow.md`, `spec.md`, `design.md`, `plan.md`, and reference material. |
| `config/` | `.env` (never committed) and `.env.example` (committed). |
| `data/` | Input and runtime data. |
| `content/`, `site/` | Static site: Markdown source (authors edit only this) and generated output (committed, never edited by hand). |
| `models/`, `prompts/` | Downloaded model weights (never committed; path from config) and LLM prompt files. |
| `scripts/` | Setup, download, and maintenance scripts: `cleanup.py`, `check.py` (the checks the hooks run), `milestones-runner.py` (runs the plan unattended), `download_models.py`, `download_assets.py`. |
| `.vscode/`, `.claude/` | Shared editor settings and Claude Code settings. |
| Root | `CLAUDE.md`, `README.md`, `requirements.txt`, `.gitignore`, `main.py` (Python entry point), `Dockerfile`, `compose.yaml`, `.dockerignore` (Docker), and the tool configs: `ruff.toml`, `mypy.ini`, `pytest.ini` (Python), `package.json`, `tsconfig.json`, `eslint.config.js` (JavaScript). |

- All source code lives under `src/`, except the entry point `main.py`. Create a folder only when
  the layout in `docs/design.md` lists it, and update the layout in the same change.
- Never edit a generated file by hand. Regenerate it with the script that makes it.
- `scripts/cleanup.py` removes caches and generated artifacts by name (for example `__pycache__`,
  tool caches, logs). It never deletes source, tests, docs, config, input data, or dependencies.

## Configuration and constants

- Settings live in `config/.env`, which is never committed. `config/.env.example` is committed and
  lists every key: non-secret keys carry their default, secret keys are empty. `config.py` is the
  only module that reads `config/.env` or the environment. A real environment variable overrides
  `config/.env`.
- Only the entry point imports `config`. It passes values down as arguments, grouped into small
  typed settings objects per component. The code has no defaults: a missing or invalid value fails
  clearly at startup.
- Never write a behavior-affecting value inline: URLs, ports, file paths, model names, thresholds,
  limits, timeouts. They come from config.
- Fixed vocabularies (statuses, sources, error codes) are enums, or named immutable constants where
  the language has no enums, in the module that owns them. No other module-level constants.
- To add a setting, in the same change: (1) add the key to `config/.env.example` (its default, or
  empty if secret); (2) add it to `config/.env`; (3) add a typed field in `config.py`; (4) add a row
  to the settings table in `docs/design.md`; (5) pass the value in from the entry point.

## Dependencies

- Prefer the standard library. Ask before adding any dependency, and say why the standard library is
  not enough. Install only into the project's isolated environment, never into the global
  interpreter or a base environment.
- The dependency file (`requirements.txt`; `package.json` for JavaScript) is the only list. Add a
  library in the same change that first imports it, never import an unlisted library, and remove it
  when its last import goes.
- List direct dependencies only, pinned to the version installed when added (`==` in
  `requirements.txt`, exact versions in `package.json`). Do not use `pip freeze`. Use only APIs that
  exist in the pinned version.

## Testing

- Every requirement ID has a test at the lowest level that proves it. Every new public function in
  the business-logic layer also has a unit test.
- Every user workflow (an event-driven requirement, `When <trigger>, ...`) has an end-to-end test
  through the outermost non-browser entry point (HTTP API, CLI, or service), with fakes at the
  external boundaries. The UI is AI-built and never read by the user, so every UI workflow
  requirement also gets one headless-browser test in `tests/e2e/ui/`. `docs/design.md` chooses the
  browser tool, and the user approves it under Dependencies.
- Layout: `tests/unit/` (logic with fakes, one test file per source module) and `tests/e2e/`.
  Requirement coverage is the primary measure. Line and branch coverage on `src/` has a floor of 80%.
- Test public behavior, not private implementation: one behavior per test, and every test asserts
  something. Tests are deterministic (seed randomness; no real clock, network, or sleeps; exact
  outputs). They use temporary folders and invented data, and never touch real config, data, or user
  files, or need a live LLM or external server.
- Never weaken or edit an existing test, baseline, or fixture to make it pass. Change one only when
  its requirement changed, and say so in the report.

## Git and destructive actions

- Work on `main` unless told otherwise. Never commit `config/.env`, secrets, user data, model
  weights, exports, logs, or caches. Before the first commit, check that `.gitignore` covers them.
- `.claude/settings.json` blocks force-push, `reset --hard`, `git clean`, `git restore`, and Docker
  volume deletion. It asks before recursive deletes, installs, killing processes, and edits to the
  spec, `CLAUDE.md`, or the settings. Never work around a block with a different command.
- Delete recursively only a scratch folder you made in this milestone, and clear caches with
  `scripts/cleanup.py`. Never touch files outside this repo (except scratch folders you make and
  delete), the paths listed as protected under Project rules, or another program's process.
- If a task needs a forbidden action, or an approval you cannot get now (a new dependency, an
  architecture change, a spec change), stop that milestone: in `docs/plan.md`, set its Status to
  `blocked` and add a **Blocked** entry with the reason and the exact question (template in
  `docs/workflow.md`), and ask in chat if the user is present. An **Approval** entry in the block
  permits exactly what it says, and nothing more.

## Security and privacy

- Secrets (API keys, tokens, passwords, database IDs) live only in `config/.env` or the platform's
  secret store. They never appear in code, committed files, logs, error messages, reports, or
  browser-side code.
- User data stays on the machine. A flow of user data to an external service (an LLM API, Notion, a
  cloud store) must be listed in `docs/design.md` as a `DEC-NNN` and approved by the user. Servers
  listen on `127.0.0.1` unless the design says otherwise. Telemetry is off. At run time the app
  calls only the services the design lists.
- Never run, test, or debug against the user's real data. Copy it to a scratch folder, point the
  process at the copy through environment variables of that process only, and delete the copy
  afterwards. Reports give counts, never content. Never put real personal data in source, fixtures,
  or docs. Use invented data.

## Living docs

- Update every doc a change makes inaccurate in the same change, and be specific: "Added
  `domain/review.py`: computes Needs Review", not "updated code". Each doc owns one kind of fact.
  Link to the owner; do not copy.

  | Change | Update |
  | --- | --- |
  | Behavior or a requirement | `docs/spec.md`, with the user's approval |
  | Architecture, data model, settings, directory layout, rules, thresholds | `docs/design.md` |
  | Setup, how to run, user-visible changes | `README.md` |
  | A library added or removed | `requirements.txt`, in the same change as the import |
  | New generated files, caches, secrets | `.gitignore` |

- `README.md` always has: What it does, Stack (with versions), File structure (top-level folders,
  one line each), Setup, How to run, How to test. Setup explains how to install dependencies,
  configure `config/.env`, and set up and check every external dependency (the LLM server, models,
  API keys) before the first run.
- Never edit `CLAUDE.md` without the user's approval. When a fact in it goes stale (stack, test
  command, run command) or a rule needs to change, flag it, propose the exact change, and edit only
  after approval.
