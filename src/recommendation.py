"""Builds the recommendation request text and turns the validated reply into a recommendation.

Pure and synchronous. It does not call the LLM (`llm_client.py` does). Implements REC-001 and
DEC-006: the request carries the job description and the candidate's extracted facts, never the
name or the address. CV facts hold no contact details.
"""

import json

from src.llm_schemas import RecommendationReply
from src.records import CvFacts, Education, Job, Recommendation, YearMonth

_JOB_TEXT_PLACEHOLDER = "{{JOB_TEXT}}"
_CANDIDATE_FACTS_PLACEHOLDER = "{{CANDIDATE_FACTS}}"


def build_recommendation_request(template: str, job_text: str, facts: CvFacts) -> str:
    """Fills the job description and the candidate facts into the recommendation prompt.

    Args:
        template: The prompt text with the `{{JOB_TEXT}}` and `{{CANDIDATE_FACTS}}` placeholders.
        job_text: The full text of one job description.
        facts: The extracted facts of one candidate.

    Returns:
        The request text to send to the LLM. The facts are JSON without name and address.
    """
    candidate = json.dumps(_facts_for_request(facts), ensure_ascii=False, indent=2)
    return template.replace(_CANDIDATE_FACTS_PLACEHOLDER, candidate).replace(
        _JOB_TEXT_PLACEHOLDER, job_text
    )


def recommendation_from_reply(reply: RecommendationReply) -> Recommendation:
    """Turns a validated recommendation reply into a recommendation.

    Args:
        reply: The reply the LLM returned.

    Returns:
        The verdict and the reason.
    """
    return Recommendation(interview=reply.interview, reason=reply.reason)


def _facts_for_request(facts: CvFacts) -> dict[str, object]:
    """Lists the facts the recommendation needs: all but the name and the address."""
    return {
        "current_title": facts.current_title,
        "skills": list(facts.skills),
        "highest_degree": facts.highest_degree,
        "jobs": [_job_for_request(job) for job in facts.jobs],
        "education": [_education_for_request(entry) for entry in facts.education],
    }


def _job_for_request(job: Job) -> dict[str, object]:
    """Lists the fields of one job."""
    return {
        "title": job.title,
        "employer": job.employer,
        "city": job.city,
        "country": job.country,
        "start": _month_text(job.start),
        "end": _month_text(job.end),
        "is_current": job.is_current,
        "description": job.description,
    }


def _education_for_request(entry: Education) -> dict[str, object]:
    """Lists the fields of one education entry."""
    return {
        "degree": entry.degree,
        "university": entry.university,
        "major": entry.major,
        "graduated": _month_text(entry.graduated),
    }


def _month_text(month: YearMonth | None) -> str | None:
    """Writes a month as `YYYY-MM`, or `None` when there is none."""
    return None if month is None else f"{month.year:04d}-{month.month:02d}"
