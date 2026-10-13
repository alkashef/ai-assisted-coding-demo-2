"""Builds the extraction request text and turns the validated reply into CV facts.

Pure and synchronous. It does not call the LLM (`llm_client.py` does) or read the prompt file
(`file_reader.py` does). Implements EXT-002, EXT-003, EXT-004, EXT-006, EXT-009, EXT-010 and
MIS-001 (DEC-005). A date that is not `YYYY-MM` raises `LlmOutputError` (no repair, no retry).
"""

import re

from src.llm_schemas import CvFactsReply, EducationReply, JobReply
from src.ports import LlmOutputError
from src.records import CvFacts, Education, Job, YearMonth

_CV_TEXT_PLACEHOLDER = "{{CV_TEXT}}"
_DATE_PATTERN = re.compile(r"(\d{4})-(\d{2})")
_LAST_MONTH = 12


def build_extraction_request(template: str, cv_text: str) -> str:
    """Fills the CV text into the extraction prompt.

    Args:
        template: The prompt text with the `{{CV_TEXT}}` placeholder.
        cv_text: The full text of one CV.

    Returns:
        The request text to send to the LLM.
    """
    return template.replace(_CV_TEXT_PLACEHOLDER, cv_text)


def facts_from_reply(reply: CvFactsReply) -> CvFacts:
    """Turns a validated extraction reply into CV facts.

    Args:
        reply: The reply the LLM returned.

    Returns:
        The facts. A `null` in the reply is `None` (MIS-001).

    Raises:
        LlmOutputError: A date in the reply is not `YYYY-MM`. The error carries the reply as JSON.
    """
    raw_output = reply.model_dump_json()
    return CvFacts(
        name=reply.name,
        current_title=reply.current_title,
        skills=tuple(reply.skills),
        city=reply.city,
        country=reply.country,
        highest_degree=reply.highest_degree,
        jobs=tuple(_job_from_reply(job, raw_output) for job in reply.jobs),
        education=tuple(_education_from_reply(entry, raw_output) for entry in reply.education),
    )


def _job_from_reply(job: JobReply, raw_output: str) -> Job:
    """Turns one job in the reply into a job record."""
    return Job(
        title=job.title,
        employer=job.employer,
        city=job.city,
        country=job.country,
        start=_required_month(job.start, raw_output),
        end=_optional_month(job.end, raw_output),
        description=job.description,
    )


def _education_from_reply(entry: EducationReply, raw_output: str) -> Education:
    """Turns one education entry in the reply into an education record."""
    return Education(
        degree=entry.degree,
        university=entry.university,
        major=entry.major,
        graduated=_optional_month(entry.graduated, raw_output),
    )


def _optional_month(value: str | None, raw_output: str) -> YearMonth | None:
    """Parses a `YYYY-MM` text, or returns `None` for a `null`."""
    return None if value is None else _required_month(value, raw_output)


def _required_month(value: str, raw_output: str) -> YearMonth:
    """Parses a `YYYY-MM` text.

    Raises:
        LlmOutputError: The text is not a year and a month from 01 to 12.
    """
    match = _DATE_PATTERN.fullmatch(value)
    if match is None or not 1 <= int(match[2]) <= _LAST_MONTH:
        raise LlmOutputError("Extraction reply has a date that is not YYYY-MM", raw_output)
    return YearMonth(year=int(match[1]), month=int(match[2]))
