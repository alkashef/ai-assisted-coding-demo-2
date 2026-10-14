"""The response models of the JSON API (design section 4)."""

from pydantic import BaseModel, ConfigDict


class JobSummary(BaseModel):
    """A job description in the list (LST-001)."""

    id: str
    title: str


class JobDetail(BaseModel):
    """A job description with its raw text (JOB-003)."""

    id: str
    title: str
    text: str


class CandidateSummary(BaseModel):
    """A candidate in the list (LST-002). A missing name is `null` (MIS-001)."""

    id: str
    name: str | None


class _ViewModel(BaseModel):
    """Base of the models built from the view dataclasses of `workspace_views`."""

    model_config = ConfigDict(from_attributes=True)


class LastJob(_ViewModel):
    """The last job of a candidate (EXT-009).

    A `null` end with `is_current` means "Present"; without it the end is unknown (DEC-015).
    """

    title: str | None
    employer: str | None
    city: str | None
    country: str | None
    start: str
    end: str | None
    is_current: bool
    description: str | None


class ExtractedAttributes(_ViewModel):
    """The extracted attributes of a candidate (EXT-002 to EXT-010)."""

    name: str | None
    current_title: str | None
    skills: list[str]
    city: str | None
    country: str | None
    highest_degree: str | None
    countries: list[str]
    employers: list[str]
    last_job: LastJob | None


class CalculatedAttributes(_ViewModel):
    """The calculated attributes of a candidate (CAL-001 to CAL-005, CAL-007)."""

    total_months: int | None
    job_count: int | None
    average_job_months: float | None
    gaps: list[int] | None
    months_since_graduation: int | None
    currently_employed: bool | None


class Recommendation(_ViewModel):
    """Whether to interview a candidate for a job description, with the reason (REC-001)."""

    interview: bool
    reason: str


class RankedCandidate(_ViewModel):
    """A candidate in the ranking of a job description (JOB-002, RNK-003, REC-001)."""

    candidate_id: str
    score: float | None
    recommendation: Recommendation | None
    extracted: ExtractedAttributes | None
    calculated: CalculatedAttributes | None


class CandidateDetail(_ViewModel):
    """The raw CV text and the attributes of a candidate (CND-001, CND-002)."""

    candidate_id: str
    text: str
    extracted: ExtractedAttributes | None
    calculated: CalculatedAttributes | None


class RankedJob(_ViewModel):
    """A job description in the ranking of a candidate (CND-003)."""

    job_id: str
    title: str
    score: float | None


class FailureSummary(BaseModel):
    """A failed LLM call (ERR-001)."""

    item_id: str
    cause: str


class Health(BaseModel):
    """The liveness report."""

    status: str
