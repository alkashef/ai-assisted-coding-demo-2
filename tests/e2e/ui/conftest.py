"""Fixtures for the headless-browser tests: the app on loopback with a fake workspace (DEC-012)."""

import socket
import threading
import time
from collections.abc import Iterator
from pathlib import Path

import pytest
import uvicorn
from playwright.sync_api import Browser, Error, Page, sync_playwright

from src.api.app import create_app
from src.records import CvFacts, Document, Failure, Workspace

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


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


@pytest.fixture(scope="session")
def base_url() -> Iterator[str]:
    """Serves the real front end with the fake workspace on 127.0.0.1 for the whole session."""
    port = _free_port()
    config = uvicorn.Config(
        create_app(_fake_workspace(), _WEB_ROOT), host="127.0.0.1", port=port, log_level="warning"
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + _START_TIMEOUT_SECONDS
    while not server.started and time.monotonic() < deadline:
        time.sleep(0.05)
    assert server.started, "The test server did not start"
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    thread.join(timeout=_START_TIMEOUT_SECONDS)


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
