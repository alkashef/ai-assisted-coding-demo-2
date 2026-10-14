"""Builds the recommendation user text and turns the validated reply into a recommendation.

Pure and synchronous. It does not call the LLM (`llm_client.py` does) or read the prompt file,
which is the system text. Implements REC-001, DEC-006 and DEC-016: the user text carries the job
description and the candidate's extracted facts as tagged data, never the name or the address.
CV facts hold no contact details.
"""

import json

from src.llm_schemas import RecommendationReply
from src.prompt_data import Tag, tagged
from src.records import CvFacts, Education, Job, Recommendation, YearMonth


def build_recommendation_user_text(job_text: str, facts: CvFacts) -> str:
    """Builds the user text of the recommendation request: the job and the facts as tagged data.

    Args:
        job_text: The full text of one job description.
        facts: The extracted facts of one candidate.

    Returns:
        The job description inside `<job_description>` tags, then the facts as JSON without name
        and address inside `<candidate_facts>` tags. Any copy of a known tag in either is escaped.
    """
    candidate = json.dumps(_facts_for_request(facts), ensure_ascii=False, indent=2)
    return f"{tagged(Tag.JOB_DESCRIPTION, job_text)}\n\n{tagged(Tag.CANDIDATE_FACTS, candidate)}"


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
