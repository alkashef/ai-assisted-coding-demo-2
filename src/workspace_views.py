"""Builds the data for each read from the workspace (design section 2.1).

Pure functions over the in-memory workspace. They do not rank, call an LLM or read files: the
pipeline has done that already. Implements LST-001, LST-002, ERR-001, JOB-002, JOB-003, RNK-003,
REC-001 and CND-001 to CND-003.
"""

from dataclasses import dataclass

from src.attributes import distinct_countries, distinct_employers, last_job
from src.records import (
    CalculatedAttributes,
    CvFacts,
    Document,
    Recommendation,
    Workspace,
    YearMonth,
)


@dataclass(frozen=True)
class JobItem:
    """One job description in the list: its ID and its title (the first line)."""

    job_id: str
    title: str


@dataclass(frozen=True)
class JobDetail:
    """The raw text of one job description with its ID and title (JOB-003)."""

    job_id: str
    title: str
    text: str


@dataclass(frozen=True)
class CandidateItem:
    """One candidate in the list: the CV ID and the name, `None` when not available (MIS-001)."""

    candidate_id: str
    name: str | None


@dataclass(frozen=True)
class FailureItem:
    """One failed LLM call: the item and the cause (ERR-001)."""

    item_id: str
    cause: str


@dataclass(frozen=True)
class LastJob:
    """The last job of a CV in display form (EXT-009).

    A `None` end with `is_current` means "Present"; without it the end is unknown (DEC-015).
    """

    title: str | None
    employer: str | None
    city: str | None
    country: str | None
    start: str
    end: str | None
    is_current: bool
    description: str | None


@dataclass(frozen=True)
class ExtractedAttributes:
    """The extracted attributes of one CV (EXT-002 to EXT-010, except withdrawn EXT-005)."""

    name: str | None
    current_title: str | None
    skills: tuple[str, ...]
    city: str | None
    country: str | None
    highest_degree: str | None
    countries: tuple[str, ...]
    employers: tuple[str, ...]
    last_job: LastJob | None


@dataclass(frozen=True)
class RankedCandidate:
    """One candidate in the ranking of a job description.

    The score is `None` for a CV without a vector (MIS-002). The attributes are `None` when the
    extraction failed (ERR-002), and the recommendation is `None` when it is missing.
    """

    candidate_id: str
    score: float | None
    recommendation: Recommendation | None
    extracted: ExtractedAttributes | None
    calculated: CalculatedAttributes | None


@dataclass(frozen=True)
class CandidateDetail:
    """The raw CV text and the attributes of one candidate."""

    candidate_id: str
    text: str
    extracted: ExtractedAttributes | None
    calculated: CalculatedAttributes | None


@dataclass(frozen=True)
class RankedJob:
    """One job description in the ranking of a candidate. The score is `None` without a vector."""

    job_id: str
    title: str
    score: float | None


class NotFoundError(Exception):
    """Raised when an ID names no job description or no candidate."""


def job_list(workspace: Workspace) -> list[JobItem]:
    """Lists the job descriptions with their titles (LST-001)."""
    return [JobItem(job.doc_id, _first_line(job.text)) for job in workspace.jobs]


def job_detail(workspace: Workspace, job_id: str) -> JobDetail:
    """Returns the ID, title and raw text of one job description (JOB-003).

    Args:
        workspace: The finished workspace.
        job_id: The ID of the job description.

    Returns:
        The detail.

    Raises:
        NotFoundError: If no job description has the ID.
    """
    for job in workspace.jobs:
        if job.doc_id == job_id:
            return JobDetail(job.doc_id, _first_line(job.text), job.text)
    raise NotFoundError(f"Job description not found: {job_id}")


def candidate_list(workspace: Workspace) -> list[CandidateItem]:
    """Lists the candidates with their names (LST-002).

    A CV whose extraction failed stays in the list with no name.
    """
    items = []
    for cv in workspace.cvs:
        facts = workspace.facts.get(cv.doc_id)
        items.append(CandidateItem(cv.doc_id, None if facts is None else facts.name))
    return items


def failure_list(workspace: Workspace) -> list[FailureItem]:
    """Lists the failed LLM calls with their causes (ERR-001)."""
    return [FailureItem(failure.item_id, failure.cause) for failure in workspace.failures]


def ranked_candidates(workspace: Workspace, job_id: str) -> list[RankedCandidate]:
    """Lists every candidate for a job description, best match first (JOB-002, RNK-003, REC-001).

    Args:
        workspace: The finished workspace.
        job_id: The ID of the job description.

    Returns:
        One entry per ranked CV, in the ranked order.

    Raises:
        NotFoundError: If no job description has the ID.
    """
    if all(job.doc_id != job_id for job in workspace.jobs):
        raise NotFoundError(f"Job description not found: {job_id}")
    return [
        RankedCandidate(
            candidate_id=candidate_id,
            score=score,
            recommendation=workspace.recommendations.get((job_id, candidate_id)),
            extracted=_extracted(workspace, candidate_id),
            calculated=workspace.attributes.get(candidate_id),
        )
        for candidate_id, score in workspace.ranked_candidates.get(job_id, ())
    ]


def candidate_detail(workspace: Workspace, candidate_id: str) -> CandidateDetail:
    """Returns the raw CV text and the attributes of one candidate (CND-001, CND-002).

    Args:
        workspace: The finished workspace.
        candidate_id: The CV ID.

    Returns:
        The detail. The attributes are `None` when the extraction of the CV failed.

    Raises:
        NotFoundError: If no CV has the ID.
    """
    cv = _find_cv(workspace, candidate_id)
    return CandidateDetail(
        candidate_id=cv.doc_id,
        text=cv.text,
        extracted=_extracted(workspace, candidate_id),
        calculated=workspace.attributes.get(candidate_id),
    )


def ranked_job_list(workspace: Workspace, candidate_id: str) -> list[RankedJob]:
    """Lists every job description for a candidate, best match first (CND-003).

    Args:
        workspace: The finished workspace.
        candidate_id: The CV ID.

    Returns:
        One entry per ranked job description, in the ranked order.

    Raises:
        NotFoundError: If no CV has the ID.
    """
    _find_cv(workspace, candidate_id)
    titles = {item.job_id: item.title for item in job_list(workspace)}
    return [
        RankedJob(job_id=job_id, title=titles.get(job_id, ""), score=score)
        for job_id, score in workspace.ranked_jobs.get(candidate_id, ())
    ]


def _find_cv(workspace: Workspace, candidate_id: str) -> Document:
    """Returns the CV with the ID, or raises `NotFoundError`."""
    for cv in workspace.cvs:
        if cv.doc_id == candidate_id:
            return cv
    raise NotFoundError(f"Candidate not found: {candidate_id}")


def _extracted(workspace: Workspace, candidate_id: str) -> ExtractedAttributes | None:
    """Returns the extracted attributes of a CV, or `None` when its extraction failed."""
    facts = workspace.facts.get(candidate_id)
    if facts is None:
        return None
    return ExtractedAttributes(
        name=facts.name,
        current_title=facts.current_title,
        skills=facts.skills,
        city=facts.city,
        country=facts.country,
        highest_degree=facts.highest_degree,
        countries=distinct_countries(facts),
        employers=distinct_employers(facts),
        last_job=_last_job(facts),
    )


def _last_job(facts: CvFacts) -> LastJob | None:
    """Returns the last job of a CV in display form (EXT-009), or `None` when it has no job."""
    job = last_job(facts)
    if job is None:
        return None
    return LastJob(
        title=job.title,
        employer=job.employer,
        city=job.city,
        country=job.country,
        start=_format_month(job.start),
        end=None if job.end is None else _format_month(job.end),
        is_current=job.is_current,
        description=job.description,
    )


def _format_month(month: YearMonth) -> str:
    """Formats a month as `YYYY-MM`."""
    return f"{month.year:04d}-{month.month:02d}"


def _first_line(text: str) -> str:
    """Returns the first line of a text, or an empty string for an empty text."""
    lines = text.splitlines()
    return lines[0].strip() if lines else ""
