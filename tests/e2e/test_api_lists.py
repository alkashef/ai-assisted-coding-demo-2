"""End-to-end tests for the list endpoints, through the framework's test client."""

from pathlib import Path

from fastapi.testclient import TestClient

from src.api.app import create_app
from src.records import CvFacts, Document, Failure, Workspace


def _workspace() -> Workspace:
    facts = CvFacts(
        name="Ada Invented",
        current_title=None,
        skills=(),
        city=None,
        country=None,
        highest_degree=None,
        jobs=(),
        education=(),
    )
    return Workspace(
        cvs=(Document("a.txt", "Cv A"), Document("b.txt", "Cv B")),
        jobs=(Document("j1.txt", "Data Analyst\nDetails"),),
        facts={"a.txt": facts},
        attributes={},
        ranked_candidates={},
        ranked_jobs={},
        recommendations={},
        failures=(Failure("b.txt", "Extraction failed: rate limited"),),
    )


def _client(tmp_path: Path) -> TestClient:
    (tmp_path / "index.html").write_text("<h1>Front end</h1>", encoding="utf-8")
    return TestClient(create_app(_workspace(), tmp_path))


def test_lst_001_jobs_endpoint_lists_job_ids_and_titles(tmp_path: Path) -> None:
    response = _client(tmp_path).get("/api/jobs")

    assert response.status_code == 200
    assert response.json() == [{"id": "j1.txt", "title": "Data Analyst"}]


def test_lst_002_candidates_endpoint_lists_candidate_ids_and_names(tmp_path: Path) -> None:
    response = _client(tmp_path).get("/api/candidates")

    assert response.status_code == 200
    assert response.json() == [
        {"id": "a.txt", "name": "Ada Invented"},
        {"id": "b.txt", "name": None},
    ]


def test_err_001_failures_endpoint_lists_item_and_cause(tmp_path: Path) -> None:
    response = _client(tmp_path).get("/api/failures")

    assert response.status_code == 200
    assert response.json() == [{"item_id": "b.txt", "cause": "Extraction failed: rate limited"}]


def test_dec_002_health_endpoint_reports_alive(tmp_path: Path) -> None:
    response = _client(tmp_path).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_dec_002_static_front_end_is_served_from_the_web_root(tmp_path: Path) -> None:
    response = _client(tmp_path).get("/")

    assert response.status_code == 200
    assert "<h1>Front end</h1>" in response.text
