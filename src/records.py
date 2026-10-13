"""Frozen records that carry the CV facts and the calculated attributes.

Holds data only. It does not read files (the file reader does), call an LLM, or calculate
anything (`attributes.py` does). Implements the data model in design section 3 (DEC-005, DEC-009).
A value that is missing is `None` (MIS-001).
"""

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
