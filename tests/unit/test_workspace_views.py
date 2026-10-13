"""Tests for `src/workspace_views.py`."""

from src.records import CvFacts, Document, Failure, Workspace
from src.workspace_views import (
    CandidateItem,
    FailureItem,
    JobItem,
    candidate_list,
    failure_list,
    job_list,
)


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


def _workspace(failures: tuple[Failure, ...] = ()) -> Workspace:
    return Workspace(
        cvs=(Document("a.txt", "Cv A"), Document("b.txt", "Cv B")),
        jobs=(Document("j1.txt", "Data Analyst\nDetails"), Document("j2.txt", "Nurse")),
        facts={"a.txt": _facts("Ada Invented")},
        attributes={},
        ranked_candidates={},
        ranked_jobs={},
        recommendations={},
        failures=failures,
    )


def test_lst_001_job_list_has_id_and_title() -> None:
    assert job_list(_workspace()) == [JobItem("j1.txt", "Data Analyst"), JobItem("j2.txt", "Nurse")]


def test_lst_002_candidate_list_has_id_and_name() -> None:
    assert candidate_list(_workspace()) == [
        CandidateItem("a.txt", "Ada Invented"),
        CandidateItem("b.txt", None),
    ]


def test_err_001_failure_list_has_item_and_cause() -> None:
    failures = (Failure("b.txt", "Extraction failed: rate limited"),)

    assert failure_list(_workspace(failures)) == [
        FailureItem("b.txt", "Extraction failed: rate limited")
    ]
