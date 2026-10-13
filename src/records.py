"""Frozen records that carry the CV facts and the calculated attributes.

Holds data only. It does not read files (the file reader does), call an LLM, or calculate
anything (`attributes.py` does). Implements the data model in design section 3 (DEC-005, DEC-009).
A value that is missing is `None` (MIS-001).
"""

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    """A text file read from a folder. The ID is the file name."""

    doc_id: str
    text: str


@dataclass(frozen=True)
class YearMonth:
    """A calendar month, such as 2018-05."""

    year: int
    month: int


@dataclass(frozen=True)
class Job:
    """One job in a CV. A `None` end means "Present"."""

    title: str | None
    employer: str | None
    city: str | None
    country: str | None
    start: YearMonth
    end: YearMonth | None
    description: str | None


@dataclass(frozen=True)
class Education:
    """One education entry in a CV."""

    degree: str | None
    university: str | None
    major: str | None
    graduated: YearMonth | None


@dataclass(frozen=True)
class CvFacts:
    """The facts the LLM extracts from one CV (DEC-005)."""

    name: str | None
    current_title: str | None
    skills: tuple[str, ...]
    city: str | None
    country: str | None
    highest_degree: str | None
    jobs: tuple[Job, ...]
    education: tuple[Education, ...]


@dataclass(frozen=True)
class Recommendation:
    """The LLM's advice on whether to interview a candidate for a job (REC-001)."""

    interview: bool
    reason: str


@dataclass(frozen=True)
class CalculatedAttributes:
    """The attributes that code calculates from the facts (CAL-001 to CAL-005, CAL-007).

    `gaps` lists the length in months of each employment gap, and is empty when there is none.
    """

    total_months: int | None
    job_count: int | None
    average_job_months: float | None
    gaps: tuple[int, ...] | None
    months_since_graduation: int | None
    currently_employed: bool | None


@dataclass(frozen=True)
class Failure:
    """One failed LLM call: the item it was for and why it failed (ERR-001, DEC-008)."""

    item_id: str
    cause: str


@dataclass(frozen=True)
class Workspace:
    """Everything the start-up pipeline computed, kept in memory for the run (DEC-007).

    A CV whose extraction failed has no facts, no attributes and no recommendations (ERR-002).
    A ranking lists every item as (ID, score), best first; the score is `None` for an item
    without a vector, which is listed last (MIS-002).

    Attributes:
        cvs: The CVs, ordered by file name.
        jobs: The job descriptions, ordered by file name.
        facts: The extracted facts per CV ID.
        attributes: The calculated attributes per CV ID.
        ranked_candidates: Per job ID, every CV ID with its score, best first.
        ranked_jobs: Per CV ID, every job ID with its score, best first.
        recommendations: Per (job ID, CV ID) pair, the recommendation.
        failures: The failed LLM calls, in the order they were recorded.
    """

    cvs: tuple[Document, ...]
    jobs: tuple[Document, ...]
    facts: Mapping[str, CvFacts]
    attributes: Mapping[str, CalculatedAttributes]
    ranked_candidates: Mapping[str, tuple[tuple[str, float | None], ...]]
    ranked_jobs: Mapping[str, tuple[tuple[str, float | None], ...]]
    recommendations: Mapping[tuple[str, str], Recommendation]
    failures: tuple[Failure, ...]
