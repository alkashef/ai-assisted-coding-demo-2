---
paths:
  - "**/*.js"
  - "**/*.mjs"
  - "**/*.ts"
---

## JavaScript and TypeScript

- No front-end framework (React, Vue, Angular, and the like) and no UI library, unless
  `docs/design.md` chooses one. HTML, CSS, and JavaScript stay in separate files.
- Plain JavaScript as ES modules, typed with JSDoc and checked by the TypeScript compiler
  (`tsconfig.json` sets `checkJs` and `strict`). Start every file with `// @ts-check`. Write
  TypeScript source only if `docs/design.md` chooses a build toolchain. Write no `any`. The runtime
  has no dependencies and no build step. A dev-only `package.json` holds the check tools. Unit tests
  use `node --test`.
- ESLint (`eslint.config.js`) and `tsc` enforce the 20-line, 4-parameter, and complexity limits, the
  300-line file warning, typed parameters, `fetch` only in `api.js`, `console` only in `log.js`, no
  module-level `let`, and no `innerHTML`. Fix findings and never weaken the configuration.
- Naming: `kebab-case` files, `camelCase` functions and variables, `PascalCase` classes. Every
  function has JSDoc with `@param {Type}` and `@returns {Type}`, even when it is not exported.
  Describe a shared object shape once with `@typedef`. Every module starts with an `@module` block.
- Structure mirrors the Architecture rules. `main.js` only imports and connects modules. Logic
  modules (no DOM, no `fetch`) stay apart from view modules (each owns its own DOM) and `api.js`.
  Export only the public API. Modules talk through function calls or custom events, never by
  reaching into another module's DOM or state. Pass collaborators (the api module, storage, the
  clock) into the functions that use them, so tests can use fakes. Create state in `main.js` and
  pass it in.
- Behavior-affecting values (URLs, timeouts, limits) live in one `config.js` that exports a frozen
  object. Fixed vocabularies are frozen objects in the module that owns them.
- Errors: `try/catch` only in `api.js`, adding context and rethrowing with
  `new Error(message, { cause })`. Unexpected errors reach a top-level handler in `main.js` (the
  `error` and `unhandledrejection` events) that shows the raw error and stack trace on screen and
  logs it. One `log.js` wraps `console` with levels from config.
- JavaScript holds behavior only: no HTML markup strings and no styles. Clone `<template>` elements
  from the HTML or use `createElement`, and toggle CSS classes. Insert dynamic text with
  `textContent`. Never keep app data in `localStorage` or `sessionStorage`; the API is the only
  source of data. UI preferences may use `localStorage`.
- Checks. Run all of them and fix every failure: `npm run typecheck`, `npm run lint`, `npm test`,
  and the headless-browser tests (the command is in the README under How to test).
- The UI is built and maintained entirely by AI. Report front-end changes by their behavior in plain
  language, and prove correctness with the checks.
