"""Checks a finished workspace against the labeled sample: ranking hits and job-date matches.

Pure logic. It reads no file and calls no service: the entry point reads the two evaluation files
(`file_reader.py`) and builds the workspace (`pipeline.py`), then passes them in as text and
objects. The report gives counts and pass or fail, never CV content. Implements NFR-004 and
NFR-005 (DEC-017).

IDs are file names. `ground_truth.tsv` holds bare dataset IDs, and `build_sample.py` adds `.txt`
to every file name, so the parser adds it too.
"""

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass

from src.records import Job, Workspace, YearMonth


class EvaluationDataError(Exception):
    """An evaluation file is not in the expected format. The message names the file kind."""


@dataclass(frozen=True)
class EvaluationLimits:
    """How many top-ranked CVs to look at, and what the two checks must reach."""

    top_k: int
    min_relevant_in_top_k: int
    min_date_match_percent: int


@dataclass(frozen=True)
class GoldJob:
    """The reviewed dates of one job: the same three fields as an extracted `Job` (DEC-015)."""

    start: YearMonth
    end: YearMonth | None
    is_current: bool


@dataclass(frozen=True)
class GoldFile:
    """The parsed gold file: its attribution line, and the reviewed jobs per CV ID."""

    attribution: str
    cvs: Mapping[str, tuple[GoldJob, ...]]


@dataclass(frozen=True)
class JobRanking:
    """The ranking check for one job description."""

    job_id: str
    relevant_in_top_k: int
    passed: bool


@dataclass(frozen=True)
class DateMatches:
    """The date check: gold jobs that an extracted job matches, over all gold jobs."""

    matched: int
    total: int
    percent: int
    passed: bool


@dataclass(frozen=True)
class EvaluationReport:
    """Both checks, with the limits they were judged against."""

    limits: EvaluationLimits
    ranking: tuple[JobRanking, ...]
    dates: DateMatches

    @property
    def ranking_passed(self) -> bool:
        """True when at least one job description was checked and every one passed."""
        return bool(self.ranking) and all(result.passed for result in self.ranking)

    @property
    def passed(self) -> bool:
        """True when both checks passed."""
        return self.ranking_passed and self.dates.passed


def parse_ground_truth(text: str) -> dict[str, frozenset[str]]:
    """Parses `ground_truth.tsv` into the relevant CV IDs per job description ID.

    Args:
        text: The file content: a `job_id<TAB>cv_id` header, then one pair per line.

    Returns:
        The set of labeled-relevant CV file names per job description file name.

    Raises:
        EvaluationDataError: The header is wrong or a row does not have two columns.
    """
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines or lines[0].split("\t") != ["job_id", "cv_id"]:
        raise EvaluationDataError("The ground truth file must start with a job_id, cv_id header")
    relevant: dict[str, set[str]] = {}
    for line in lines[1:]:
        job_id, _, cv_id = line.partition("\t")
        if not job_id or not cv_id or "\t" in cv_id:
            raise EvaluationDataError("A ground truth row must have a job ID and a CV ID")
        relevant.setdefault(f"{job_id}.txt", set()).add(f"{cv_id}.txt")
    return {job_id: frozenset(cv_ids) for job_id, cv_ids in relevant.items()}


def parse_gold_jobs(text: str) -> GoldFile:
    """Parses the gold file: `attribution` and `cvs`, which maps a CV ID to its jobs.

    Each job has `start` (`YYYY-MM`), `end` (`YYYY-MM` or `null`) and `is_current` (true or false).

    Args:
        text: The file content (JSON).

    Returns:
        The attribution and the gold jobs per CV ID.

    Raises:
        EvaluationDataError: The text is not JSON or does not have this shape.
    """
    try:
        data = json.loads(text)
        attribution = _text(data["attribution"])
        cvs = {cv_id: tuple(_gold_job(job) for job in jobs) for cv_id, jobs in data["cvs"].items()}
    except (ValueError, KeyError, TypeError, AttributeError) as err:
        raise EvaluationDataError("The gold file is not in the expected format") from err
    return GoldFile(attribution=attribution, cvs=cvs)


def _text(value: object) -> str:
    """Returns the value if it is text."""
    if not isinstance(value, str):
        raise TypeError("a value must be text")
    return value


def _gold_job(data: Mapping[str, object]) -> GoldJob:
    """Builds one gold job. A wrong type or format raises `ValueError` or `TypeError`."""
    is_current = data["is_current"]
    if not isinstance(is_current, bool):
        raise TypeError("is_current must be true or false")
    end = data["end"]
    return GoldJob(
        start=_year_month(data["start"]),
        end=None if end is None else _year_month(end),
        is_current=is_current,
    )


def _year_month(text: object) -> YearMonth:
    """Parses `YYYY-MM`."""
    found = re.fullmatch(r"(\d{4})-(0[1-9]|1[0-2])", _text(text))
    if found is None:
        raise ValueError("a date must be YYYY-MM")
    return YearMonth(int(found[1]), int(found[2]))


def evaluate(
    workspace: Workspace,
    relevant: Mapping[str, frozenset[str]],
    gold: GoldFile,
    limits: EvaluationLimits,
) -> EvaluationReport:
    """Runs the ranking check (NFR-004) and the date check (NFR-005).

    Args:
        workspace: The finished workspace of the run.
        relevant: The labeled-relevant CV IDs per job description ID.
        gold: The reviewed job dates.
        limits: K and the two minimums.

    Returns:
        Both checks. A check with nothing to check fails.
    """
    ranking = tuple(
        _check_job(job_id, cv_ids, workspace, limits) for job_id, cv_ids in relevant.items()
    )
    return EvaluationReport(
        limits=limits, ranking=ranking, dates=_check_dates(workspace, gold, limits)
    )


def _check_job(
    job_id: str, relevant_cvs: frozenset[str], workspace: Workspace, limits: EvaluationLimits
) -> JobRanking:
    """Counts the labeled-relevant CVs among the top K of one job description's ranking."""
    top = workspace.ranked_candidates.get(job_id, ())[: limits.top_k]
    hits = sum(1 for cv_id, _ in top if cv_id in relevant_cvs)
    return JobRanking(job_id, hits, hits >= limits.min_relevant_in_top_k)


def _check_dates(workspace: Workspace, gold: GoldFile, limits: EvaluationLimits) -> DateMatches:
    """Counts the gold jobs that an extracted job of the same CV matches."""
    matched = 0
    total = 0
    for cv_id, gold_jobs in gold.cvs.items():
        facts = workspace.facts.get(cv_id)
        extracted = facts.jobs if facts is not None else ()
        total += len(gold_jobs)
        matched += sum(1 for gold_job in gold_jobs if _has_match(gold_job, extracted))
    passed = total > 0 and matched * 100 >= limits.min_date_match_percent * total
    return DateMatches(matched, total, matched * 100 // total if total else 0, passed)


def _has_match(gold_job: GoldJob, extracted: tuple[Job, ...]) -> bool:
    """True when an extracted job has the same start, end and current marker."""
    return any(
        (job.start, job.end, job.is_current) == (gold_job.start, gold_job.end, gold_job.is_current)
        for job in extracted
    )


def format_report(report: EvaluationReport) -> str:
    """Formats the report as text: counts and pass or fail, never CV content.

    Args:
        report: The result of `evaluate`.

    Returns:
        The report lines, joined by newlines.
    """
    limits = report.limits
    lines = [
        f"Ranking (NFR-004): at least {limits.min_relevant_in_top_k} labeled-relevant CVs "
        f"in the top {limits.top_k}, per job description"
    ]
    lines += [
        f"  {r.job_id}: {r.relevant_in_top_k} relevant in the top {limits.top_k} - "
        f"{_verdict(r.passed)}"
        for r in report.ranking
    ]
    dates = report.dates
    lines += [
        f"Ranking: {_verdict(report.ranking_passed)}",
        f"Job dates (NFR-005): {dates.matched} of {dates.total} gold jobs matched "
        f"({dates.percent}%), at least {limits.min_date_match_percent}% needed - "
        f"{_verdict(dates.passed)}",
        "The gold file counts only after the user has reviewed it.",
        f"Result: {_verdict(report.passed)}",
    ]
    return "\n".join(lines)


def _verdict(passed: bool) -> str:
    """Returns PASS or FAIL."""
    return "PASS" if passed else "FAIL"
