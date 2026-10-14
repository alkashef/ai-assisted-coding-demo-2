import re

from src.llm_schemas import RecommendationReply
from src.recommendation import build_recommendation_request, recommendation_from_reply
from src.records import CvFacts, Education, Job, Recommendation, YearMonth

TEMPLATE = "Decide.\nJOB:\n{{JOB_TEXT}}\nCANDIDATE:\n{{CANDIDATE_FACTS}}\nAnswer in JSON."


def make_facts() -> CvFacts:
    return CvFacts(
        name="Ada Example",
        current_title="Senior Analyst",
        skills=("SQL", "Python"),
        city="Shelbyville",
        country="Utopia",
        highest_degree="Master",
        jobs=(
            Job(
                title="Data Analyst",
                employer="Example Corp",
                city="Springfield",
                country="Freedonia",
                start=YearMonth(2018, 5),
                end=None,
                is_current=True,
                description="Built weekly reports.",
            ),
        ),
        education=(
            Education(
                degree="Master",
                university="Example University",
                major="Statistics",
                graduated=YearMonth(2017, 6),
            ),
        ),
    )


def test_rec_001_reply_becomes_a_recommendation_with_verdict_and_reason():
    reply = RecommendationReply(interview=True, reason="Strong SQL background.")

    assert recommendation_from_reply(reply) == Recommendation(
        interview=True, reason="Strong SQL background."
    )


def test_rec_001_request_contains_the_job_text_and_the_candidate_facts():
    request = build_recommendation_request(TEMPLATE, "Looking for a data analyst.", make_facts())

    assert "Looking for a data analyst." in request
    for fact in (
        "Senior Analyst",
        "SQL",
        "Master",
        "Example Corp",
        "Built weekly reports.",
        "2018-05",
    ):
        assert fact in request


def test_rec_001_facts_carry_is_current_beside_end():
    request = build_recommendation_request(TEMPLATE, "Looking for a data analyst.", make_facts())

    assert re.search(r'"end": null,\s+"is_current": true,', request)


def test_dec_006_request_excludes_name_address_and_contact_details():
    request = build_recommendation_request(TEMPLATE, "Looking for a data analyst.", make_facts())

    for personal in ("Ada Example", "Shelbyville", "Utopia"):
        assert personal not in request
