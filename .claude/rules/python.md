---
paths:
  - "**/*.py"
---

## Python

- Ruff (`ruff.toml`) and mypy (`mypy.ini`) enforce naming, type annotations, Google-style
  docstrings, absolute imports at the top of the file, `pathlib`, explicit file encodings,
  `raise ... from err`, and no `print`. Fix findings and never weaken the configuration.
- Test files are `test_<module>.py`. Test functions are `test_<requirement id>_<behavior>`, for
  example `test_tri_024_unsure_duplicate_creates_item`.
- Annotate every parameter, return value, and class attribute, using built-in generics and `|`. No
  `Any` unless a library forces it; then add a comment saying why.
- Use dataclasses for typed records. Settings are frozen dataclasses. Use f-strings, and `with` for
  resources. Do not write your own decorators, metaclasses, context managers, or descriptors.
  Library decorators such as `@dataclass` and `@pytest.fixture` are fine. Prefix internal names with
  `_`. Every folder under `src/` has an `__init__.py`, and imports read
  `from src.<module> import <name>`.
- A module may define `logger = logging.getLogger(__name__)`. It is the only module-level object
  besides enums.
- `main.py` at the repo root is the entry point. It loads config, sets up logging, creates the
  objects, and starts the app. It holds no logic. `config.py` loads `config/.env` with
  `python-dotenv`.
- Use the project's conda environment (its name and Python version are in the README Stack). Conda
  supplies Python only. Install packages with `pip install -r requirements.txt`, never
  `conda install`.
- Checks. Run all of them and fix every failure: `mypy src`, `ruff check .`,
  `ruff format --check .`, and `python -m pytest --cov=src --cov-branch --cov-fail-under=80`.
  `python scripts/check.py` runs all of them.
  `requirements.txt` lists `pytest`, `pytest-cov`, `mypy`, `ruff`, and `python-dotenv`, plus
  `pytest-asyncio` for async code.
