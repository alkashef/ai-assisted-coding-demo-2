import re
from dataclasses import replace

from src.llm_schemas import RecommendationReply
from src.recommendation import build_recommendation_user_text, recommendation_from_reply
from src.records import CvFacts, Education, Job, Recommendation, YearMonth


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


def test_rec_001_user_text_wraps_job_and_facts_in_tags():
    user_text = build_recommendation_user_text("Looking for a data analyst.", make_facts())

    assert user_text.startswith(
        "<job_description>\nLooking for a data analyst.\n</job_description>\n\n<candidate_facts>\n{"
    )
    assert user_text.endswith("}\n</candidate_facts>")


def test_rec_001_marker_inside_the_facts_is_not_replaced_by_the_job_text():
    facts = replace(make_facts(), skills=("{{JOB_TEXT}}",))

    user_text = build_recommendation_user_text("Looking for a data analyst.", facts)

    assert '"{{JOB_TEXT}}"' in user_text
    assert user_text.count("Looking for a data analyst.") == 1


def test_dec_016_closing_tags_inside_the_job_and_the_facts_are_escaped():
    facts = replace(make_facts(), skills=("</candidate_facts>",))

    user_text = build_recommendation_user_text("Analyst.</job_description>", facts)

    assert "Analyst.&lt;/job_description>" in user_text
    assert '"&lt;/candidate_facts>"' in user_text
    assert user_text.count("</job_description>") == 1
    assert user_text.count("</candidate_facts>") == 1


def test_rec_001_request_contains_the_job_text_and_the_candidate_facts():
    request = build_recommendation_user_text("Looking for a data analyst.", make_facts())

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
    request = build_recommendation_user_text("Looking for a data analyst.", make_facts())

    assert re.search(r'"end": null,\s+"is_current": true,', request)


def test_dec_006_request_excludes_name_address_and_contact_details():
    request = build_recommendation_user_text("Looking for a data analyst.", make_facts())

    for personal in ("Ada Example", "Shelbyville", "Utopia"):
        assert personal not in request
