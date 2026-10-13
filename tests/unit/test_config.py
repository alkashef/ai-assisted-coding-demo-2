"""Tests for `src/config.py`."""

from pathlib import Path

import pytest

from src.config import ConfigError, Settings, load_settings, settings_summary

_KEY = "sk-test-secret-123"

_VALUES = {
    "OPENAI_API_KEY": _KEY,
    "LLM_BASE_URL": "https://example.test/v1",
    "LLM_MODEL": "model-a",
    "LLM_MAX_TOKENS": "100",
    "EMBEDDING_MODEL": "embed-a",
    "LLM_TIMEOUT_SECONDS": "30",
    "LLM_MAX_CONCURRENCY": "2",
    "CV_FOLDER": "cvs",
    "JOB_FOLDER": "jobs",
    "EXTRACT_PROMPT_PATH": "p1.md",
    "MATCH_PROMPT_PATH": "p2.md",
    "WEB_ROOT": "web",
    "SERVER_HOST": "127.0.0.1",
    "SERVER_PORT": "8000",
    "LOG_LEVEL": "INFO",
    "LOG_FILE": "logs/app.log",
}


def _load(tmp_path: Path, environ: dict[str, str]) -> Settings:
    return load_settings(tmp_path / "missing.env", environ)


def test_nfr_002_settings_text_hides_the_api_key(tmp_path: Path) -> None:
    settings = _load(tmp_path, _VALUES)

    assert settings.llm.api_key == _KEY
    assert _KEY not in repr(settings)
    assert _KEY not in str(settings)


def test_nfr_002_log_summary_of_settings_omits_the_api_key(tmp_path: Path) -> None:
    summary = settings_summary(_load(tmp_path, _VALUES))

    assert _KEY not in summary
    assert "model-a" in summary


def test_nfr_002_missing_setting_error_names_the_key_not_a_value(tmp_path: Path) -> None:
    environ = {k: v for k, v in _VALUES.items() if k != "LLM_MODEL"}

    with pytest.raises(ConfigError) as error:
        _load(tmp_path, environ)

    assert "LLM_MODEL" in str(error.value)
    assert _KEY not in str(error.value)


def test_nfr_002_invalid_number_error_names_the_key_not_the_value(tmp_path: Path) -> None:
    with pytest.raises(ConfigError) as error:
        _load(tmp_path, {**_VALUES, "SERVER_PORT": "abc"})

    assert "SERVER_PORT" in str(error.value)
    assert "abc" not in str(error.value)


def test_nfr_002_empty_api_key_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="OPENAI_API_KEY"):
        _load(tmp_path, {**_VALUES, "OPENAI_API_KEY": ""})


def test_dec_013_server_host_comes_from_the_setting(tmp_path: Path) -> None:
    settings = _load(tmp_path, {**_VALUES, "SERVER_HOST": "127.0.0.2"})

    assert settings.server.host == "127.0.0.2"
    assert settings.server.port == 8000


def test_nfr_002_environment_overrides_the_env_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("\n".join(f"{k}={v}" for k, v in _VALUES.items()), encoding="utf-8")

    settings = load_settings(env_file, {"LLM_MODEL": "model-b"})

    assert settings.llm.model == "model-b"
    assert settings.llm.max_tokens == 100
