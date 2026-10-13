"""The response models of the JSON API (design section 4)."""

from pydantic import BaseModel


class JobSummary(BaseModel):
    """A job description in the list (LST-001)."""

    id: str
    title: str


class CandidateSummary(BaseModel):
    """A candidate in the list (LST-002). A missing name is `null` (MIS-001)."""

    id: str
    name: str | None


class FailureSummary(BaseModel):
    """A failed LLM call (ERR-001)."""

    item_id: str
    cause: str


class Health(BaseModel):
    """The liveness report."""

    status: str
