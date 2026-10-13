"""End-to-end tests for the entry point, with empty input folders so that no LLM call is made."""

import logging
from dataclasses import dataclass
from pathlib import Path

import pytest
from fastapi import FastAPI

import main

_API_KEY = "sk-invented-key-for-tests"


@dataclass(frozen=True)
class Started:
    """What one run of `main.main` left behind."""

    calls: list[tuple[object, str, int]]
    log: str


def _env_file(tmp_path: Path) -> Path:
    for folder in ("cvs", "jobs", "web"):
        (tmp_path / folder).mkdir()
    (tmp_path / "extract.md").write_text("{{CV_TEXT}}", encoding="utf-8")
    (tmp_path / "match.md").write_text("{{JOB_TEXT}}{{CANDIDATE_FACTS}}", encoding="utf-8")
    lines = [
        f"OPENAI_API_KEY={_API_KEY}",
        "LLM_BASE_URL=https://api.invalid/v1",
        "LLM_MODEL=model-a",
        "LLM_MAX_TOKENS=100",
        "EMBEDDING_MODEL=model-b",
        "LLM_TIMEOUT_SECONDS=5",
        "LLM_MAX_CONCURRENCY=2",
        f"CV_FOLDER={tmp_path / 'cvs'}",
        f"JOB_FOLDER={tmp_path / 'jobs'}",
        f"EXTRACT_PROMPT_PATH={tmp_path / 'extract.md'}",
        f"MATCH_PROMPT_PATH={tmp_path / 'match.md'}",
        f"WEB_ROOT={tmp_path / 'web'}",
        "SERVER_HOST=127.0.0.1",
        "SERVER_PORT=8765",
        "LOG_LEVEL=INFO",
        f"LOG_FILE={tmp_path / 'logs' / 'app.log'}",
    ]
    env_file = tmp_path / ".env"
    env_file.write_text("\n".join(lines), encoding="utf-8")
    return env_file


@pytest.fixture(scope="module")
def started(tmp_path_factory: pytest.TempPathFactory) -> Started:
    """Runs `main.main` once, because the Chroma collection names are unique per process."""
    tmp_path = tmp_path_factory.mktemp("main")
    calls: list[tuple[object, str, int]] = []
    root = logging.getLogger()
    saved = (list(root.handlers), root.level)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(main.uvicorn, "run", lambda app, host, port: calls.append((app, host, port)))
        main.main(_env_file(tmp_path))
    for handler in root.handlers:
        if handler not in saved[0]:
            handler.close()
    root.handlers[:] = saved[0]
    root.setLevel(saved[1])
    return Started(calls=calls, log=(tmp_path / "logs" / "app.log").read_text(encoding="utf-8"))


def test_dec_013_the_server_starts_on_the_configured_loopback_host_and_port(
    started: Started,
) -> None:
    assert len(started.calls) == 1
    app, host, port = started.calls[0]
    assert isinstance(app, FastAPI)
    assert (host, port) == ("127.0.0.1", 8765)


def test_nfr_002_the_log_file_records_the_start_without_the_api_key(started: Started) -> None:
    assert "Starting with" in started.log
    assert _API_KEY not in started.log
