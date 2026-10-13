"""The reply shapes the LLM must return, as `pydantic` models.

Holds shapes only. It does not turn a reply into records (`extraction.py` and `recommendation.py`
do) or call the LLM (`llm_client.py` does). Implements the output contract in design section 3
(EXT-002 to EXT-010, REC-001, DEC-005, DEC-011).

Every field is required and a missing value is `null`, as strict structured output demands
(MIS-001). Dates are `YYYY-MM` text; the extraction module checks them.
"""

from pydantic import BaseModel, ConfigDict


class _Reply(BaseModel):
    """Base of the replies: no extra fields, no changes after validation."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class JobReply(_Reply):
    """One job in a CV. A `null` end means "Present"."""

    title: str | None
    employer: str | None
    city: str | None
    country: str | None
    start: str
    end: str | None
    description: str | None


class EducationReply(_Reply):
    """One education entry in a CV."""

    degree: str | None
    university: str | None
    major: str | None
    graduated: str | None


class CvFactsReply(_Reply):
    """The facts extracted from one CV."""

    name: str | None
    current_title: str | None
    skills: list[str]
    city: str | None
    country: str | None
    highest_degree: str | None
    jobs: list[JobReply]
    education: list[EducationReply]


class RecommendationReply(_Reply):
    """Whether to interview a candidate for a job, and why."""

    interview: bool
    reason: str
