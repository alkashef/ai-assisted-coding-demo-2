"""Tests for `src/workspace_views.py`."""

import pytest

from src.records import CvFacts, Document, Failure, Recommendation, Workspace
from src.workspace_views import (
    CandidateItem,
    FailureItem,
    JobItem,
    NotFoundError,
    RankedJob,
    candidate_detail,
    candidate_list,
    failure_list,
    job_list,
    ranked_candidates,
    ranked_job_list,
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


def _ranked_workspace() -> Workspace:
    return Workspace(
        cvs=(Document("a.txt", "Cv A"), Document("b.txt", "Cv B")),
        jobs=(Document("j1.txt", "Data Analyst\nDetails"),),
        facts={"a.txt": _facts("Ada Invented")},
        attributes={},
        ranked_candidates={"j1.txt": (("a.txt", 0.8), ("b.txt", None))},
        ranked_jobs={"a.txt": (("j1.txt", 0.8),)},
        recommendations={("j1.txt", "a.txt"): Recommendation(False, "No SQL")},
        failures=(),
    )


def test_job_002_ranked_candidates_keep_the_ranked_order_and_recommendation() -> None:
    items = ranked_candidates(_ranked_workspace(), "j1.txt")

    assert [(item.candidate_id, item.score) for item in items] == [("a.txt", 0.8), ("b.txt", None)]
    assert items[0].recommendation == Recommendation(False, "No SQL")
    assert items[1].extracted is None


def test_job_002_ranked_candidates_unknown_job_raises() -> None:
    with pytest.raises(NotFoundError):
        ranked_candidates(_ranked_workspace(), "nope.txt")


def test_cnd_001_candidate_detail_has_text_and_extracted_attributes() -> None:
    detail = candidate_detail(_ranked_workspace(), "a.txt")

    assert detail.text == "Cv A"
    assert detail.extracted is not None
    assert detail.extracted.name == "Ada Invented"
    assert detail.extracted.last_job is None


def test_cnd_001_candidate_detail_unknown_candidate_raises() -> None:
    with pytest.raises(NotFoundError):
        candidate_detail(_ranked_workspace(), "nope.txt")


def test_cnd_003_ranked_job_list_has_titles_and_scores() -> None:
    assert ranked_job_list(_ranked_workspace(), "a.txt") == [
        RankedJob("j1.txt", "Data Analyst", 0.8)
    ]


def test_cnd_003_ranked_job_list_unknown_candidate_raises() -> None:
    with pytest.raises(NotFoundError):
        ranked_job_list(_ranked_workspace(), "nope.txt")
