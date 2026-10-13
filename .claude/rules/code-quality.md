---
paths:
  - "src/**"
  - "tests/**"
  - "scripts/**"
  - "main.py"
---

## Code smells

Ruff, mypy, and ESLint enforce the limits below (`ruff.toml`, `mypy.ini`, `eslint.config.js`).
Never weaken their configuration, and never add `noqa`, `type: ignore`, or `eslint-disable` to make
a change pass. Fix the code.

Two hooks run `scripts/check.py`. After each edit, ruff or ESLint fixes the file and reports what is
left: fix it before moving on. Before each commit, every check and test runs, and a failure
refuses the commit. Never bypass the hooks (`--no-verify`, `core.hooksPath`). Editing the check configs or
the hook files asks the user first; ask only to change a rule on purpose, never to pass a check.

- Each function, class, and module does one thing. If its name needs two verbs, or describing it
  needs "and", split it. Keep functions near 20 lines (15 statements), 4 parameters, and complexity
  8. When a file passes about 300 lines, check it for a second responsibility and split it only if
  you find one.
- Prefer composition to inheritance. Group values that always travel together into one typed
  object. Inject long-lived collaborators through the constructor, not through every call.
- Do not write: duplicated logic (search for a helper first; extract on the second use); dead code;
  abstractions or design patterns the task does not need; pass-through wrappers or classes too small
  to justify themselves (the single owner of an external system is not one); mutable global state.
- Write code a beginner-to-intermediate programmer can read. Prefer plain constructs to clever ones.

## Naming and code documentation

- Name things for their purpose, not for how they look or are built. Use one term per concept.
- Every module, class, and function has a docstring. Tests are exempt: their names carry the
  requirement ID.
  - Module: what it does, what it does not do (and which module does), and the requirement or
    decision IDs it implements.
  - Class: its single responsibility, stated explicitly, and the state it owns, if any.
  - Public function: a summary, then parameters, return value, and errors raised. A private or
    trivial function gets a one-line summary.
- Comment only where the behavior is not obvious. Do not narrate the code.
- Leave no TODO comments. Report out-of-scope findings under "Assumptions and open questions".

## Error handling

- Catch an exception only at an external boundary (file system, network, database, LLM,
  subprocess), and only to add context (what was being done, on which resource) and re-raise with
  the original error attached. Never catch to recover, fall back, continue, or swallow. Ruff and
  ESLint block bare and blind catches.
- Do not catch unexpected errors. The top level shows the raw error and the full stack trace, logs
  it, and stops. No friendly message, no retry.
- Invalid user input is not an error. Handle it as Input validation says. Error messages name what
  failed and the resource (path, endpoint, ID), never secrets or user content.
- If other users can reach the app, `docs/design.md` records a `DEC-NNN` that shows a short message
  and logs the trace instead.

## Logging

- Use the language's logging library for diagnostics. Ruff and ESLint block `print` and `console`;
  a CLI may print its intended user output.
- Configure logging once, in the entry point, from settings. The log level and the log file path
  come from config. Log to the console and the file. Write plain text, one line per event, with
  timestamp, level, and module name.
- Log startup (with the settings in use, secrets excluded), key events, and failures. Levels:
  `INFO` for startup and key events, `DEBUG` for payloads and raw external responses, `WARNING` for
  rejected input, `ERROR` for failures.
- Never log secrets. Log user content only at `DEBUG`. Log an error once, at the top level. Do not
  log and re-raise at a boundary.

## Long-running work

- Long-running work never blocks the UI or the request path. Use async I/O for waits, and keep
  blocking or CPU-heavy work off the main loop.
- Python: `async def` and `await` for I/O at the boundaries (API handlers, LLM and network
  clients). Pure business logic stays synchronous. Ruff flags blocking calls inside `async def`;
  run them with `asyncio.to_thread`. Async tests use `pytest-asyncio`.
- JavaScript: `async`/`await` with `fetch`. Move heavy computation to a Web Worker. Never freeze the
  main thread.
- An API request that can run long starts the task and returns `202` with a job ID at once. The
  task runs in the background as an async task. `GET /api/jobs/<id>` reports status and progress,
  and the UI polls it. One object created in `main.py` holds the job state.

## Input validation

- Every user input passes through a validation component (a class or module) at the boundary,
  before any logic uses it. The validation rules live only there, never in handlers, views, or
  business logic.
- The component checks type, required fields, length or range, format, and allowed values. It
  reports every problem at once, naming the field and the rule, never the rejected value. Valid
  input leaves as a typed object. Invalid input is rejected with a clear message about what to fix;
  it is not an error.
- The server-side component is the authority. The browser may give fast feedback with native HTML
  constraint attributes (`required`, `type`, `min`, `max`, `pattern`), and a small validation-view
  module in JavaScript shows the server's field errors next to the fields. It does not copy the
  rules.
- Python: a Pydantic model for API bodies and a validator class for other inputs. Each rule has a
  test.
