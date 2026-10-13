"""Loads the settings from `config/.env` and the environment into typed, frozen objects.

The only module that reads `config/.env` or the environment (design section 2.3, NFR-002).
It has no defaults: a missing or invalid value raises `ConfigError`, which names the key and
never a value.
"""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import dotenv_values


class ConfigError(Exception):
    """A setting is missing or invalid. The message names the key, never its value."""


@dataclass(frozen=True)
class LlmSettings:
    """Settings for the LLM client and the pipeline's call limit."""

    api_key: str = field(repr=False)
    base_url: str
    model: str
    max_tokens: int
    embedding_model: str
    timeout_seconds: int
    max_concurrency: int


@dataclass(frozen=True)
class InputSettings:
    """Settings for the input folders and prompt files."""

    cv_folder: Path
    job_folder: Path
    extract_prompt_path: Path
    match_prompt_path: Path


@dataclass(frozen=True)
class ServerSettings:
    """Settings for the web server and the static front end."""

    host: str
    port: int
    web_root: Path


@dataclass(frozen=True)
class LogSettings:
    """Settings for logging."""

    level: str
    file: Path


@dataclass(frozen=True)
class Settings:
    """All settings, grouped per component."""

    llm: LlmSettings
    inputs: InputSettings
    server: ServerSettings
    log: LogSettings


def _text(values: Mapping[str, str], key: str) -> str:
    value = values.get(key)
    if value is None or value.strip() == "":
        raise ConfigError(f"Missing setting: {key}")
    return value.strip()


def _number(values: Mapping[str, str], key: str) -> int:
    text = _text(values, key)
    try:
        number = int(text)
    except ValueError as err:
        raise ConfigError(f"Invalid setting (not a whole number): {key}") from err
    if number <= 0:
        raise ConfigError(f"Invalid setting (must be above zero): {key}")
    return number


def load_settings(env_file: Path, environ: Mapping[str, str] | None = None) -> Settings:
    """Loads the settings. A real environment variable overrides `env_file`.

    Args:
        env_file: The `.env` file. It may be absent if the environment supplies every key.
        environ: The environment. `None` means the process environment.

    Returns:
        The typed settings.

    Raises:
        ConfigError: A key is missing or invalid.
    """
    file_values = {k: v for k, v in dotenv_values(env_file).items() if v is not None}
    values = {**file_values, **(os.environ if environ is None else environ)}
    return Settings(
        llm=LlmSettings(
            api_key=_text(values, "OPENAI_API_KEY"),
            base_url=_text(values, "LLM_BASE_URL"),
            model=_text(values, "LLM_MODEL"),
            max_tokens=_number(values, "LLM_MAX_TOKENS"),
            embedding_model=_text(values, "EMBEDDING_MODEL"),
            timeout_seconds=_number(values, "LLM_TIMEOUT_SECONDS"),
            max_concurrency=_number(values, "LLM_MAX_CONCURRENCY"),
        ),
        inputs=InputSettings(
            cv_folder=Path(_text(values, "CV_FOLDER")),
            job_folder=Path(_text(values, "JOB_FOLDER")),
            extract_prompt_path=Path(_text(values, "EXTRACT_PROMPT_PATH")),
            match_prompt_path=Path(_text(values, "MATCH_PROMPT_PATH")),
        ),
        server=ServerSettings(
            host=_text(values, "SERVER_HOST"),
            port=_number(values, "SERVER_PORT"),
            web_root=Path(_text(values, "WEB_ROOT")),
        ),
        log=LogSettings(level=_text(values, "LOG_LEVEL"), file=Path(_text(values, "LOG_FILE"))),
    )


def settings_summary(settings: Settings) -> str:
    """Returns the settings as text for the log, without the API key."""
    return (
        f"llm={settings.llm}, inputs={settings.inputs}, "
        f"server={settings.server}, log={settings.log}"
    )
