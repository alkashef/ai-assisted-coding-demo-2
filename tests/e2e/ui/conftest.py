"""Fixtures for the headless-browser tests: the app on loopback with a fake workspace (DEC-012)."""

import socket
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
import uvicorn
from playwright.sync_api import Browser, Error, Page, sync_playwright

from src.api.app import create_app
from src.records import (
    CalculatedAttributes,
    CvFacts,
    Document,
    Failure,
    Job,
    Recommendation,
    Workspace,
    YearMonth,
)

_WEB_ROOT = Path(__file__).resolve().parents[3] / "src" / "web"
_BROWSER_CHANNELS = ("msedge", "chrome")
_START_TIMEOUT_SECONDS = 10.0


def _facts(name: str | None) -> CvFacts:
    return CvFacts(
        name=name,
        current_title=None,
        skills=(),
        city=None,
        country=None,
        highest_degree=None,
        jobs=(),
        education=(),
    )


def _fake_workspace() -> Workspace:
    """Two job descriptions, three candidates (one without facts) and two failures."""
    return Workspace(
        cvs=(Document("a.txt", "Cv A"), Document("b.txt", "Cv B"), Document("c.txt", "Cv C")),
        jobs=(
            Document("j1.txt", "Data Analyst\nInvented details"),
            Document("j2.txt", "Site Engineer\nInvented details"),
        ),
        facts={"a.txt": _facts("Ada Invented"), "c.txt": _facts("Bo Invented")},
        attributes={},
        ranked_candidates={},
        ranked_jobs={},
        recommendations={},
        failures=(
            Failure("b.txt", "Extraction failed: rate limited"),
            Failure("j1.txt + c.txt", "Recommendation failed: timed out"),
        ),
    )


def _ranked_workspace() -> Workspace:
    """One job description and three candidates: ranked, unscored, and without extracted facts."""
    ada = CvFacts(
        name="Ada Invented",
        current_title="Senior Data Analyst",
        skills=("SQL", "Tableau"),
        city="Boston",
        country="United States",
        highest_degree=None,
        jobs=(
            Job(
                title="Senior Data Analyst",
                employer="Northwind Invented",
                city="Boston",
                country="United States",
                start=YearMonth(2019, 3),
                end=None,
                description="Leads reporting pipelines.",
            ),
        ),
        education=(),
    )
    return Workspace(
        cvs=(Document("a.txt", "Cv A"), Document("b.txt", "Cv B"), Document("c.txt", "Cv C")),
        jobs=(Document("j1.txt", "Data Analyst\nInvented details"),),
        facts={"a.txt": ada, "b.txt": _facts("Bo Invented")},
        attributes={
            "a.txt": CalculatedAttributes(
                total_months=106,
                job_count=3,
                average_job_months=35.33,
                gaps=(5,),
                months_since_graduation=102,
                currently_employed=True,
            ),
            "b.txt": CalculatedAttributes(
                total_months=None,
                job_count=0,
                average_job_months=None,
                gaps=None,
                months_since_graduation=None,
                currently_employed=False,
            ),
        },
        ranked_candidates={"j1.txt": (("a.txt", 0.7123), ("c.txt", 0.4), ("b.txt", None))},
        ranked_jobs={},
        recommendations={
            ("j1.txt", "a.txt"): Recommendation(True, "Strong reporting background."),
            ("j1.txt", "c.txt"): Recommendation(False, "No analytics experience."),
        },
        failures=(),
    )


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def _wait_until_started(server: uvicorn.Server) -> None:
    """Waits for the server to accept connections, and fails the test when it does not."""
    deadline = time.monotonic() + _START_TIMEOUT_SECONDS
    while not server.started and time.monotonic() < deadline:
        time.sleep(0.05)
    assert server.started, "The test server did not start"


@contextmanager
def _serve(workspace: Workspace) -> Iterator[str]:
    """Serves the real front end with the workspace on 127.0.0.1 and yields its base URL."""
    port = _free_port()
    config = uvicorn.Config(
        create_app(workspace, _WEB_ROOT), host="127.0.0.1", port=port, log_level="warning"
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    _wait_until_started(server)
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        thread.join(timeout=_START_TIMEOUT_SECONDS)


@pytest.fixture(scope="session")
def base_url() -> Iterator[str]:
    """Serves the real front end with the fake workspace for the whole session."""
    with _serve(_fake_workspace()) as url:
        yield url


@pytest.fixture(scope="session")
def ranked_base_url() -> Iterator[str]:
    """Serves the real front end with a workspace that holds rankings and recommendations."""
    with _serve(_ranked_workspace()) as url:
        yield url


@pytest.fixture(scope="module")
def browser() -> Iterator[Browser]:
    """A headless Edge or Chrome that is already installed, so nothing is downloaded.

    Module scope: Playwright's sync API keeps an event loop running while it is open, and that
    would break the async tests that run after the UI tests.
    """
    with sync_playwright() as playwright:
        failures: list[str] = []
        for channel in _BROWSER_CHANNELS:
            try:
                launched = playwright.chromium.launch(channel=channel, headless=True)
            except Error as error:
                failures.append(f"{channel}: {error}")
                continue
            yield launched
            launched.close()
            return
        pytest.fail("No installed Edge or Chrome could be driven. " + "; ".join(failures))


@pytest.fixture
def script_errors() -> list[str]:
    """The uncaught script errors of the page under test. The list fills while the test runs."""
    return []


@pytest.fixture
def page(browser: Browser, script_errors: list[str]) -> Iterator[Page]:
    """A fresh page that records its uncaught script errors."""
    opened = browser.new_page()
    opened.on("pageerror", lambda error: script_errors.append(str(error)))
    yield opened
    opened.close()
