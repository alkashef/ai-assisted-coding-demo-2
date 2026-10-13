---
paths:
  - "src/api/**"
---

## HTTP APIs

- Use FastAPI. Handlers are `async def`. The server serves the front end as static files and exposes
  a JSON API. No server-side HTML templating.
- A route handler calls one service function and returns the response. It holds no business logic.
  One router per domain.
- API paths are `kebab-case` plural nouns under `/api/`, for example `/api/triage-options`. Use GET
  to read, POST to create, PATCH to update, and DELETE to delete. A `/health` endpoint reports
  liveness.
- A Pydantic model validates every request body (see Input validation). Invalid input returns
  FastAPI's standard 422 `detail`, one entry per problem. Use 404 for a missing record and 409 for a
  conflict, both with a `detail` message.
- Authentication goes through one shared dependency or decorator, used by every protected endpoint.
  `docs/design.md` lists the public endpoints.
- Allowed CORS origins come from config. The default is none.
- End-to-end tests call the API through the framework's test client against temporary data. They do
  not start a server.
