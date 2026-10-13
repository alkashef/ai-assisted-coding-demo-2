from datetime import date

import pytest

from src.attributes import (
    calculate_attributes,
    distinct_countries,
    distinct_employers,
    job_months,
    last_job,
)
from src.records import CvFacts, Education, Job, YearMonth


def today() -> date:
    return date(2026, 10, 13)


def make_job(
    start: YearMonth,
    end: YearMonth | None,
    employer: str | None = None,
    country: str | None = None,
) -> Job:
    return Job(
        title=None,
        employer=employer,
        city=None,
        country=country,
        start=start,
        end=end,
        description=None,
    )


def make_facts(
    jobs: tuple[Job, ...] = (),
    education: tuple[Education, ...] = (),
) -> CvFacts:
    return CvFacts(
        name=None,
        current_title=None,
        skills=(),
        city=None,
        country=None,
        highest_degree=None,
        jobs=jobs,
        education=education,
    )


def ex_001_jobs() -> tuple[Job, ...]:
    return (
        make_job(YearMonth(2018, 1), YearMonth(2019, 5)),
        make_job(YearMonth(2019, 6), YearMonth(2021, 12)),
        make_job(YearMonth(2022, 1), None),
    )


def test_cal_008_duration_counts_both_months():
    job = make_job(YearMonth(2018, 1), YearMonth(2019, 5))

    assert job_months(job, today()) == 17


def test_cal_008_present_is_the_current_month():
    job = make_job(YearMonth(2026, 1), None)

    assert job_months(job, today()) == 10


def test_cal_001_total_period_is_first_start_to_current_month():
    attributes = calculate_attributes(make_facts(ex_001_jobs()), today())

    assert attributes.total_months == 106


def test_cal_001_no_jobs_gives_none():
    attributes = calculate_attributes(make_facts(), today())

    assert attributes.total_months is None


def test_cal_002_job_count():
    attributes = calculate_attributes(make_facts(ex_001_jobs()), today())

    assert attributes.job_count == 3


def test_cal_003_average_is_sum_of_durations_over_job_count():
    attributes = calculate_attributes(make_facts(ex_001_jobs()), today())

    assert attributes.average_job_months == pytest.approx(106 / 3)


def test_cal_004_back_to_back_jobs_have_no_gap():
    attributes = calculate_attributes(make_facts(ex_001_jobs()), today())

    assert attributes.gaps == ()


def test_cal_004_gap_is_months_between_end_and_next_start():
    jobs = (
        make_job(YearMonth(2018, 1), YearMonth(2018, 5)),
        make_job(YearMonth(2018, 8), YearMonth(2019, 1)),
    )

    attributes = calculate_attributes(make_facts(jobs), today())

    assert attributes.gaps == (2,)


def test_cal_004_gaps_are_found_in_start_order_whatever_the_input_order():
    jobs = (
        make_job(YearMonth(2019, 1), YearMonth(2019, 6)),
        make_job(YearMonth(2018, 1), YearMonth(2018, 5)),
    )

    attributes = calculate_attributes(make_facts(jobs), today())

    assert attributes.gaps == (7,)


def test_cal_004_overlapping_jobs_have_no_gap():
    jobs = (
        make_job(YearMonth(2018, 1), YearMonth(2019, 12)),
        make_job(YearMonth(2019, 3), YearMonth(2019, 6)),
        make_job(YearMonth(2020, 1), YearMonth(2020, 6)),
    )

    attributes = calculate_attributes(make_facts(jobs), today())

    assert attributes.gaps == ()


def test_cal_005_months_since_most_recent_graduation():
    education = (
        Education("Diploma", "Univ A", None, YearMonth(2014, 6)),
        Education("Bachelor", "Univ B", None, YearMonth(2018, 5)),
    )

    attributes = calculate_attributes(make_facts(education=education), today())

    assert attributes.months_since_graduation == 102


def test_cal_005_no_graduation_gives_none():
    education = (Education("Bachelor", None, None, None),)

    attributes = calculate_attributes(make_facts(education=education), today())

    assert attributes.months_since_graduation is None


def test_cal_007_employed_when_latest_job_has_no_end():
    attributes = calculate_attributes(make_facts(ex_001_jobs()), today())

    assert attributes.currently_employed is True


def test_cal_007_not_employed_when_latest_job_has_an_end():
    jobs = (
        make_job(YearMonth(2018, 1), None),
        make_job(YearMonth(2020, 1), YearMonth(2021, 1)),
    )

    attributes = calculate_attributes(make_facts(jobs), today())

    assert attributes.currently_employed is False


def test_ext_007_distinct_job_countries():
    jobs = (
        make_job(YearMonth(2018, 1), YearMonth(2018, 12), country="Egypt"),
        make_job(YearMonth(2019, 1), YearMonth(2019, 12), country="Germany"),
        make_job(YearMonth(2020, 1), YearMonth(2020, 12), country="Egypt"),
        make_job(YearMonth(2021, 1), YearMonth(2021, 12), country=None),
    )

    assert distinct_countries(make_facts(jobs)) == ("Egypt", "Germany")


def test_ext_008_distinct_employers():
    jobs = (
        make_job(YearMonth(2018, 1), YearMonth(2018, 12), employer="Acme"),
        make_job(YearMonth(2019, 1), YearMonth(2019, 12), employer="Globex"),
        make_job(YearMonth(2020, 1), YearMonth(2020, 12), employer="Acme"),
        make_job(YearMonth(2021, 1), YearMonth(2021, 12), employer=None),
    )

    assert distinct_employers(make_facts(jobs)) == ("Acme", "Globex")


def test_ext_009_last_job_is_the_one_with_latest_start():
    jobs = ex_001_jobs()

    assert last_job(make_facts((jobs[2], jobs[0], jobs[1]))) == jobs[2]


def test_ext_009_no_jobs_gives_no_last_job():
    assert last_job(make_facts()) is None
