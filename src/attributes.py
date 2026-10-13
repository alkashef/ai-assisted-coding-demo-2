"""Calculate the attributes of a CV from its facts, and derive its lists.

Pure date math. It does no I/O, reads no clock (the caller passes today's date) and calls no LLM.
Implements CAL-001 to CAL-005, CAL-007, CAL-008 and EXT-007 to EXT-009 (DEC-005, design section 3).
"""

from datetime import date

from src.records import CalculatedAttributes, CvFacts, Job, YearMonth


def _month_index(month: YearMonth) -> int:
    """Return the number of months from year 0 to the given month."""
    return month.year * 12 + month.month


def _inclusive_months(first: int, last: int) -> int:
    """Return how many months lie from `first` to `last`, counting both (CAL-008)."""
    return last - first + 1


def _current_month(today: date) -> int:
    """Return the month index of today's date."""
    return _month_index(YearMonth(today.year, today.month))


def _end_index(job: Job, current: int) -> int:
    """Return the month index where the job ends. "Present" is the current month."""
    return current if job.end is None else _month_index(job.end)


def job_months(job: Job, today: date) -> int:
    """Return the length of a job in months, counting both its start and end month (CAL-008).

    Args:
        job: The job. A `None` end means "Present", which is the month of `today`.
        today: Today's date.

    Returns:
        The number of months.
    """
    current = _current_month(today)
    return _inclusive_months(_month_index(job.start), _end_index(job, current))


def _gaps(jobs: tuple[Job, ...], current: int) -> tuple[int, ...]:
    """Return the length of each gap between jobs, in start order (CAL-004).

    A gap is counted only when a job starts more than one month after everything before it ended.
    """
    gaps: list[int] = []
    covered_until: int | None = None
    for job in sorted(jobs, key=lambda item: _month_index(item.start)):
        start = _month_index(job.start)
        if covered_until is not None and start - covered_until > 1:
            gaps.append(start - covered_until - 1)
        end = _end_index(job, current)
        covered_until = end if covered_until is None else max(covered_until, end)
    return tuple(gaps)


def _months_since_graduation(facts: CvFacts, current: int) -> int | None:
    """Return the months from the most recent graduation to now (CAL-005), or None."""
    graduations = [entry.graduated for entry in facts.education if entry.graduated is not None]
    if not graduations:
        return None
    latest = max(_month_index(month) for month in graduations)
    return _inclusive_months(latest, current)


def last_job(facts: CvFacts) -> Job | None:
    """Return the job with the latest start (EXT-009), or None when there is no job.

    Args:
        facts: The facts of one CV.

    Returns:
        The last job.
    """
    if not facts.jobs:
        return None
    return max(facts.jobs, key=lambda job: _month_index(job.start))


def distinct_countries(facts: CvFacts) -> tuple[str, ...]:
    """Return the countries of the jobs, each once, in order of first use (EXT-007).

    Args:
        facts: The facts of one CV.

    Returns:
        The countries. A job without a country adds none.
    """
    countries = [job.country for job in facts.jobs if job.country is not None]
    return tuple(dict.fromkeys(countries))


def distinct_employers(facts: CvFacts) -> tuple[str, ...]:
    """Return the employers of the jobs, each once, in order of first use (EXT-008).

    Args:
        facts: The facts of one CV.

    Returns:
        The employers. A job without an employer adds none.
    """
    employers = [job.employer for job in facts.jobs if job.employer is not None]
    return tuple(dict.fromkeys(employers))


def calculate_attributes(facts: CvFacts, today: date) -> CalculatedAttributes:
    """Calculate the attributes of one CV (CAL-001 to CAL-005 and CAL-007).

    Args:
        facts: The facts of the CV.
        today: Today's date. The month of this date is "Present".

    Returns:
        The attributes. A value that the facts cannot give is `None`, which is every job-based
        value for a CV with no job, and the time since graduation for a CV with no graduation.
    """
    current = _current_month(today)
    since_graduation = _months_since_graduation(facts, current)
    if not facts.jobs:
        return CalculatedAttributes(None, None, None, None, since_graduation, None)
    durations = [job_months(job, today) for job in facts.jobs]
    first_start = min(_month_index(job.start) for job in facts.jobs)
    latest = last_job(facts)
    return CalculatedAttributes(
        total_months=_inclusive_months(first_start, current),
        job_count=len(durations),
        average_job_months=sum(durations) / len(durations),
        gaps=_gaps(facts.jobs, current),
        months_since_graduation=since_graduation,
        currently_employed=latest is not None and latest.end is None,
    )
