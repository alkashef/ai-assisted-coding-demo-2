"""End-to-end tests for the entry point, with empty input folders so that no LLM call is made."""

import json
import logging
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import pytest
from fastapi import FastAPI

import main
from src.records import CvFacts, Document, Job, Workspace, YearMonth

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
        f"EVAL_GROUND_TRUTH_PATH={tmp_path / 'truth.tsv'}",
        f"EVAL_GOLD_JOBS_PATH={tmp_path / 'gold.json'}",
        "EVAL_TOP_K=2",
        "EVAL_MIN_RELEVANT_IN_TOP_K=1",
        "EVAL_MIN_DATE_MATCH_PERCENT=100",
        f"WEB_ROOT={tmp_path / 'web'}",
        "SERVER_HOST=127.0.0.1",
        "SERVER_PORT=8765",
        "LOG_LEVEL=INFO",
        f"LOG_FILE={tmp_path / 'logs' / 'app.log'}",
    ]
    env_file = tmp_path / ".env"
    env_file.write_text("\n".join(lines), encoding="utf-8")
    return env_file


@contextmanager
def _restored_logging() -> Iterator[None]:
    """Removes the handlers that `main.main` adds to the root logger."""
    root = logging.getLogger()
    saved = (list(root.handlers), root.level)
    try:
        yield
    finally:
        for handler in root.handlers:
            if handler not in saved[0]:
                handler.close()
        root.handlers[:] = saved[0]
        root.setLevel(saved[1])


@pytest.fixture(scope="module")
def started(tmp_path_factory: pytest.TempPathFactory) -> Started:
    """Runs `main.main` once, because the Chroma collection names are unique per process."""
    tmp_path = tmp_path_factory.mktemp("main")
    calls: list[tuple[object, str, int]] = []
    with pytest.MonkeyPatch.context() as patch, _restored_logging():
        patch.setattr(main.uvicorn, "run", lambda app, host, port: calls.append((app, host, port)))
        main.main(_env_file(tmp_path))
    return Started(calls=calls, log=(tmp_path / "logs" / "app.log").read_text(encoding="utf-8"))


def _workspace() -> Workspace:
    """A finished workspace: CV `a.txt` has one extracted job, and `b.txt` is ranked second."""
    job = Job(
        title=None,
        employer=None,
        city=None,
        country=None,
        start=YearMonth(2018, 5),
        end=YearMonth(2020, 1),
        is_current=False,
        description=None,
    )
    facts = CvFacts(
        name="SECRET-NAME",
        current_title=None,
        skills=(),
        city=None,
        country=None,
        highest_degree=None,
        jobs=(job,),
        education=(),
    )
    return Workspace(
        cvs=(Document("a.txt", "SECRET-CV-TEXT"), Document("b.txt", "other")),
        jobs=(Document("j1.txt", "job"),),
        facts={"a.txt": facts},
        attributes={},
        ranked_candidates={"j1.txt": (("a.txt", 0.9), ("b.txt", 0.1))},
        ranked_jobs={},
        recommendations={},
        failures=(),
    )


def _evaluate(tmp_path: Path, gold_end: str, capsys: pytest.CaptureFixture[str]) -> tuple[int, str]:
    """Runs `main.main` with `evaluate` on a fake workspace. Returns the exit code and stdout."""
    env_file = _env_file(tmp_path)
    (tmp_path / "truth.tsv").write_text("job_id\tcv_id\nj1\ta\n", encoding="utf-8")
    jobs = [{"start": "2018-05", "end": gold_end, "is_current": False}]
    gold = {"attribution": "Invented attribution", "cvs": {"a.txt": jobs}}
    (tmp_path / "gold.json").write_text(json.dumps(gold), encoding="utf-8")
    server_calls: list[object] = []

    async def fake_build_workspace(settings: object) -> Workspace:
        return _workspace()

    with pytest.MonkeyPatch.context() as patch, _restored_logging():
        patch.setattr(main, "_build_workspace", fake_build_workspace)
        patch.setattr(main.uvicorn, "run", lambda *args, **kwargs: server_calls.append(args))
        code = main.main(env_file, evaluate=True)
    assert server_calls == []
    return code, capsys.readouterr().out


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


def test_dec_017_evaluate_flag_prints_the_report_and_starts_no_server(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, output = _evaluate(tmp_path, "2020-01", capsys)

    assert code == 0
    assert "j1.txt: 1 relevant in the top 2 - PASS" in output
    assert "1 of 1 gold jobs matched (100%), at least 100% needed - PASS" in output
    assert "Result: PASS" in output
    assert "SECRET" not in output


def test_dec_017_evaluate_flag_exits_with_code_1_when_a_check_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, output = _evaluate(tmp_path, "2020-02", capsys)

    assert code == 1
    assert "Result: FAIL" in output
