"""Tests for `src/evaluation.py`, with invented data."""

import json

import pytest

from src.evaluation import (
    EvaluationDataError,
    EvaluationLimits,
    GoldFile,
    GoldJob,
    evaluate,
    format_report,
    parse_gold_jobs,
    parse_ground_truth,
)
from src.records import CvFacts, Document, Job, Workspace, YearMonth

_LIMITS = EvaluationLimits(top_k=3, min_relevant_in_top_k=2, min_date_match_percent=90)
_MAY_2018 = YearMonth(2018, 5)
_JAN_2020 = YearMonth(2020, 1)


def _job(
    start: YearMonth = _MAY_2018, end: YearMonth | None = _JAN_2020, is_current: bool = False
) -> Job:
    return Job(
        title="SECRET-TITLE",
        employer="SECRET-EMPLOYER",
        city=None,
        country=None,
        start=start,
        end=end,
        is_current=is_current,
        description="SECRET-DESCRIPTION",
    )


def _facts(*jobs: Job) -> CvFacts:
    return CvFacts(
        name="SECRET-NAME",
        current_title=None,
        skills=(),
        city=None,
        country=None,
        highest_degree=None,
        jobs=jobs,
        education=(),
    )


def _workspace(
    ranked: dict[str, tuple[tuple[str, float | None], ...]] | None = None,
    facts: dict[str, CvFacts] | None = None,
) -> Workspace:
    return Workspace(
        cvs=(Document("a.txt", "SECRET-CV-TEXT"),),
        jobs=(Document("j1.txt", "SECRET-JOB-TEXT"),),
        facts=facts or {},
        attributes={},
        ranked_candidates=ranked or {},
        ranked_jobs={},
        recommendations={},
        failures=(),
    )


def _gold(**cvs: tuple[GoldJob, ...]) -> GoldFile:
    return GoldFile(attribution="Invented attribution", cvs=cvs)


_GOLD_JOB = GoldJob(start=_MAY_2018, end=_JAN_2020, is_current=False)
_RANKED = (("a", 0.9), ("b", 0.8), ("c", 0.7), ("d", 0.1))


def test_nfr_004_counts_the_relevant_cvs_in_the_top_k_per_job() -> None:
    workspace = _workspace(ranked={"j1": _RANKED, "j2": _RANKED})

    report = evaluate(
        workspace, {"j1": frozenset({"a", "c", "d"}), "j2": frozenset({"b"})}, _gold(), _LIMITS
    )

    assert [(r.job_id, r.relevant_in_top_k) for r in report.ranking] == [("j1", 2), ("j2", 1)]


def test_nfr_004_fails_below_the_minimum() -> None:
    workspace = _workspace(ranked={"j1": _RANKED})

    report = evaluate(workspace, {"j1": frozenset({"a", "d"})}, _gold(), _LIMITS)

    assert [r.passed for r in report.ranking] == [False]
    assert report.ranking_passed is False


def test_nfr_004_passes_at_the_minimum() -> None:
    workspace = _workspace(ranked={"j1": _RANKED})

    report = evaluate(workspace, {"j1": frozenset({"a", "b"})}, _gold(), _LIMITS)

    assert report.ranking_passed is True


def test_nfr_004_a_cv_without_a_score_ranks_last() -> None:
    ranked = {"j1": (("a", 0.9), ("b", 0.5), ("c", None))}
    limits = EvaluationLimits(top_k=2, min_relevant_in_top_k=2, min_date_match_percent=90)

    report = evaluate(_workspace(ranked=ranked), {"j1": frozenset({"a", "c"})}, _gold(), limits)

    assert report.ranking[0].relevant_in_top_k == 1


def test_nfr_004_a_job_missing_from_the_workspace_has_no_relevant_cv_in_the_top_k() -> None:
    report = evaluate(_workspace(), {"j1": frozenset({"a"})}, _gold(), _LIMITS)

    assert report.ranking[0].relevant_in_top_k == 0
    assert report.ranking_passed is False


def test_nfr_004_nothing_to_check_fails() -> None:
    report = evaluate(_workspace(), {}, _gold(), _LIMITS)

    assert report.ranking_passed is False


def test_nfr_005_matches_a_job_by_start_end_and_current() -> None:
    extracted = _job()
    gold = _gold(
        **{
            "a": (
                _GOLD_JOB,
                GoldJob(start=YearMonth(2018, 6), end=_JAN_2020, is_current=False),
                GoldJob(start=_MAY_2018, end=YearMonth(2020, 2), is_current=False),
                GoldJob(start=_MAY_2018, end=None, is_current=True),
            )
        }
    )

    report = evaluate(_workspace(facts={"a": _facts(extracted)}), {}, gold, _LIMITS)

    assert (report.dates.matched, report.dates.total) == (1, 4)


def test_nfr_005_a_current_job_and_an_unknown_end_are_different() -> None:
    extracted = _facts(_job(end=None, is_current=True), _job(end=None, is_current=False))
    gold = _gold(
        a=(
            GoldJob(start=_MAY_2018, end=None, is_current=True),
            GoldJob(start=_MAY_2018, end=None, is_current=False),
        )
    )

    report = evaluate(_workspace(facts={"a": extracted}), {}, gold, _LIMITS)

    assert (report.dates.matched, report.dates.total) == (2, 2)


def test_nfr_005_a_failed_extraction_counts_as_misses() -> None:
    gold = _gold(a=(_GOLD_JOB, _GOLD_JOB), b=(_GOLD_JOB,))

    report = evaluate(_workspace(facts={"b": _facts(_job())}), {}, gold, _LIMITS)

    assert (report.dates.matched, report.dates.total) == (1, 3)


def test_nfr_005_extra_extracted_jobs_are_not_penalized() -> None:
    extracted = _facts(_job(start=YearMonth(2010, 1)), _job(), _job(start=YearMonth(2015, 3)))

    report = evaluate(_workspace(facts={"a": extracted}), {}, _gold(a=(_GOLD_JOB,)), _LIMITS)

    assert (report.dates.matched, report.dates.total) == (1, 1)
    assert report.dates.passed is True


@pytest.mark.parametrize(("matched", "passed"), [(9, True), (8, False)])
def test_nfr_005_fails_below_the_percent(matched: int, passed: bool) -> None:
    gold_jobs = tuple(
        GoldJob(start=YearMonth(2000 + i, 1), end=None, is_current=True) for i in range(10)
    )
    extracted = _facts(
        *(_job(start=g.start, end=None, is_current=True) for g in gold_jobs[:matched])
    )

    report = evaluate(_workspace(facts={"a": extracted}), {}, _gold(a=gold_jobs), _LIMITS)

    assert report.dates.matched == matched
    assert report.dates.passed is passed


def test_nfr_005_nothing_to_check_fails() -> None:
    report = evaluate(_workspace(), {}, _gold(), _LIMITS)

    assert report.dates.total == 0
    assert report.dates.passed is False


def test_dec_017_the_run_passes_only_when_both_checks_pass() -> None:
    workspace = _workspace(ranked={"j1": _RANKED}, facts={"a": _facts(_job())})
    ranking_ok = {"j1": frozenset({"a", "b"})}

    assert evaluate(workspace, ranking_ok, _gold(a=(_GOLD_JOB,)), _LIMITS).passed is True
    assert evaluate(workspace, {}, _gold(a=(_GOLD_JOB,)), _LIMITS).passed is False
    assert evaluate(workspace, ranking_ok, _gold(), _LIMITS).passed is False


def test_dec_017_report_has_counts_and_pass_fail_but_no_cv_content() -> None:
    workspace = _workspace(ranked={"j1": _RANKED}, facts={"a": _facts(_job())})
    gold = _gold(a=(_GOLD_JOB, GoldJob(start=YearMonth(1999, 1), end=None, is_current=True)))

    text = format_report(evaluate(workspace, {"j1": frozenset({"a"})}, gold, _LIMITS))

    assert "j1: 1 relevant in the top 3 - FAIL" in text
    assert "1 of 2 gold jobs matched (50%), at least 90% needed - FAIL" in text
    assert "Result: FAIL" in text
    assert "SECRET" not in text


def test_dec_017_report_says_pass_when_both_checks_pass() -> None:
    workspace = _workspace(ranked={"j1": _RANKED}, facts={"a": _facts(_job())})

    text = format_report(
        evaluate(workspace, {"j1": frozenset({"a", "b"})}, _gold(a=(_GOLD_JOB,)), _LIMITS)
    )

    assert "j1: 2 relevant in the top 3 - PASS" in text
    assert "1 of 1 gold jobs matched (100%), at least 90% needed - PASS" in text
    assert "Result: PASS" in text


def test_dec_017_report_says_the_gold_file_counts_only_after_review() -> None:
    text = format_report(evaluate(_workspace(), {}, _gold(), _LIMITS))

    assert "counts only after the user has reviewed it" in text


def test_dec_017_parses_the_ground_truth_and_the_gold_file() -> None:
    truth = parse_ground_truth("job_id\tcv_id\n29243\t11695\n29243\t15087\n\n32447\t367\n")
    gold = parse_gold_jobs(
        json.dumps(
            {
                "attribution": "Invented attribution",
                "cvs": {
                    "11695.txt": [
                        {"start": "2018-05", "end": "2020-01", "is_current": False},
                        {"start": "2020-03", "end": None, "is_current": True},
                    ]
                },
            }
        )
    )

    assert truth == {
        "29243.txt": frozenset({"11695.txt", "15087.txt"}),
        "32447.txt": frozenset({"367.txt"}),
    }
    assert gold == GoldFile(
        attribution="Invented attribution",
        cvs={
            "11695.txt": (
                GoldJob(start=_MAY_2018, end=_JAN_2020, is_current=False),
                GoldJob(start=YearMonth(2020, 3), end=None, is_current=True),
            )
        },
    )


@pytest.mark.parametrize("text", ["", "wrong\theader\n", "job_id\tcv_id\n29243\n"])
def test_dec_017_rejects_a_malformed_ground_truth(text: str) -> None:
    with pytest.raises(EvaluationDataError, match="ground truth"):
        parse_ground_truth(text)


@pytest.mark.parametrize(
    "text",
    [
        "not json",
        "[]",
        json.dumps({"attribution": "x"}),
        json.dumps({"cvs": {}}),
        json.dumps({"attribution": 1, "cvs": {}}),
        json.dumps(
            {
                "attribution": "x",
                "cvs": {"a.txt": [{"start": "2018-13", "end": None, "is_current": False}]},
            }
        ),
        json.dumps(
            {
                "attribution": "x",
                "cvs": {"a.txt": [{"start": "2018-05", "end": None, "is_current": "yes"}]},
            }
        ),
        json.dumps(
            {
                "attribution": "x",
                "cvs": {"a.txt": [{"start": 2018, "end": None, "is_current": False}]},
            }
        ),
    ],
)
def test_dec_017_rejects_a_malformed_gold_file(text: str) -> None:
    with pytest.raises(EvaluationDataError, match="gold file"):
        parse_gold_jobs(text)
