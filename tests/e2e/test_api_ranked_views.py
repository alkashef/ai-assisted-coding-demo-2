"""End-to-end tests for the ranked-view endpoints, through the framework's test client."""

from pathlib import Path

from fastapi.testclient import TestClient

from src.api.app import create_app
from src.records import (
    CalculatedAttributes,
    CvFacts,
    Document,
    Education,
    Job,
    Recommendation,
    Workspace,
    YearMonth,
)


def _facts(name: str | None, country: str | None = "Egypt") -> CvFacts:
    jobs = (
        Job("Analyst", "Acme", "Cairo", "Egypt", YearMonth(2015, 1), YearMonth(2017, 12), "Old"),
        Job("Lead", "Beta", "Cairo", country, YearMonth(2018, 5), None, "Current"),
    )
    return CvFacts(
        name=name,
        current_title="Lead",
        skills=("sql", "python"),
        city="Cairo",
        country="Egypt",
        highest_degree="MSc",
        jobs=jobs,
        education=(Education("MSc", "Uni", "Stats", YearMonth(2014, 6)),),
    )


def _workspace() -> Workspace:
    attributes = CalculatedAttributes(100, 2, 50.0, (), 150, True)
    return Workspace(
        cvs=(Document("a.txt", "Cv A text"), Document("b.txt", "Cv B"), Document("c.txt", "Cv C")),
        jobs=(Document("j1.txt", "Data Analyst\nDetails"), Document("j2.txt", "Nurse")),
        facts={"a.txt": _facts("Ada Invented", country=None), "b.txt": _facts(None)},
        attributes={"a.txt": attributes},
        ranked_candidates={
            "j1.txt": (("b.txt", 0.9), ("a.txt", 0.5), ("c.txt", None)),
            "j2.txt": (),
        },
        ranked_jobs={"a.txt": (("j2.txt", 0.7), ("j1.txt", 0.2))},
        recommendations={("j1.txt", "a.txt"): Recommendation(True, "Strong SQL")},
        failures=(),
    )


def _client(tmp_path: Path) -> TestClient:
    (tmp_path / "index.html").write_text("<h1>Front end</h1>", encoding="utf-8")
    return TestClient(create_app(_workspace(), tmp_path))


def _ranked(tmp_path: Path) -> list[dict]:
    return _client(tmp_path).get("/api/jobs/j1.txt/ranked-candidates").json()


def test_job_002_ranked_candidates_lists_all_candidates_best_first(tmp_path: Path) -> None:
    response = _client(tmp_path).get("/api/jobs/j1.txt/ranked-candidates")

    assert response.status_code == 200
    assert [(item["candidate_id"], item["score"]) for item in response.json()] == [
        ("b.txt", 0.9),
        ("a.txt", 0.5),
        ("c.txt", None),
    ]


def test_rnk_003_ranked_candidate_has_extracted_and_calculated_attributes(
    tmp_path: Path,
) -> None:
    candidate = _ranked(tmp_path)[1]

    assert candidate["extracted"]["name"] == "Ada Invented"
    assert candidate["extracted"]["skills"] == ["sql", "python"]
    assert candidate["extracted"]["countries"] == ["Egypt"]
    assert candidate["extracted"]["employers"] == ["Acme", "Beta"]
    assert candidate["extracted"]["highest_degree"] == "MSc"
    assert candidate["extracted"]["last_job"]["employer"] == "Beta"
    assert candidate["extracted"]["last_job"]["start"] == "2018-05"
    assert candidate["extracted"]["last_job"]["end"] is None
    assert candidate["calculated"] == {
        "total_months": 100,
        "job_count": 2,
        "average_job_months": 50.0,
        "gaps": [],
        "months_since_graduation": 150,
        "currently_employed": True,
    }


def test_rec_001_ranked_candidate_has_a_recommendation(tmp_path: Path) -> None:
    candidates = _ranked(tmp_path)

    assert candidates[1]["recommendation"] == {"interview": True, "reason": "Strong SQL"}
    assert candidates[0]["recommendation"] is None


def test_mis_001_missing_value_is_null_in_the_json(tmp_path: Path) -> None:
    candidates = _ranked(tmp_path)

    assert candidates[0]["extracted"]["name"] is None
    assert candidates[0]["calculated"] is None
    assert candidates[2]["extracted"] is None
    assert candidates[2]["score"] is None


def test_cnd_001_candidate_detail_has_the_raw_cv_text(tmp_path: Path) -> None:
    response = _client(tmp_path).get("/api/candidates/a.txt")

    assert response.status_code == 200
    assert response.json()["candidate_id"] == "a.txt"
    assert response.json()["text"] == "Cv A text"


def test_cnd_002_candidate_detail_has_extracted_and_calculated_attributes(
    tmp_path: Path,
) -> None:
    detail = _client(tmp_path).get("/api/candidates/a.txt").json()

    assert detail["extracted"]["name"] == "Ada Invented"
    assert detail["extracted"]["current_title"] == "Lead"
    assert detail["calculated"]["total_months"] == 100


def test_cnd_003_ranked_jobs_lists_all_job_descriptions_best_first(tmp_path: Path) -> None:
    response = _client(tmp_path).get("/api/candidates/a.txt/ranked-jobs")

    assert response.status_code == 200
    assert response.json() == [
        {"job_id": "j2.txt", "title": "Nurse", "score": 0.7},
        {"job_id": "j1.txt", "title": "Data Analyst", "score": 0.2},
    ]


def test_job_002_unknown_job_returns_404_with_a_detail(tmp_path: Path) -> None:
    response = _client(tmp_path).get("/api/jobs/missing.txt/ranked-candidates")

    assert response.status_code == 404
    assert "missing.txt" in response.json()["detail"]


def test_cnd_001_unknown_candidate_returns_404_with_a_detail(tmp_path: Path) -> None:
    client = _client(tmp_path)

    detail = client.get("/api/candidates/missing.txt")
    ranked_jobs = client.get("/api/candidates/missing.txt/ranked-jobs")

    assert detail.status_code == 404
    assert "missing.txt" in detail.json()["detail"]
    assert ranked_jobs.status_code == 404
