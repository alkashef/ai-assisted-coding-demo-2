---
paths:
  - "prompts/**"
  - "src/**/llm*"
---

## LLMs and prompts

- A project uses one provider, chosen in `docs/design.md`. Build no provider switch unless the spec
  requires one.
- Prompts live in files under `prompts/`, never as strings in code, and their paths come from
  config. The model ID (exact, not a moving alias), base URL, models folder path, and sampling and
  token limits also come from config.
- Treat LLM output as untrusted input: parse and validate it against a schema. On failure raise an
  error that includes the raw output. Do not repair it and do not retry.
- The LLM only produces data. It never executes tools, runs code, or decides transport or server
  behavior. Code runs the tools.
- API-hosted model: data leaves the machine, so send only the fields the prompt needs.
  `docs/design.md` states which data goes to which provider.
- Local model: the base URL points at localhost. Fail clearly when the server is not running or the
  model is not pulled. Download models only with `scripts/download_models.py`, never at run time.
  At run time the app is offline, with telemetry off. Weights live in `models/` and are never
  committed.
