import pytest

from src.extraction import build_extraction_request, facts_from_reply
from src.llm_schemas import CvFactsReply, EducationReply, JobReply
from src.ports import LlmOutputError
from src.records import YearMonth

TEMPLATE = "Extract the facts.\n---\n{{CV_TEXT}}\n---\nAnswer in JSON."


def make_job_reply(
    start: str = "2018-05", end: str | None = "2020-01", is_current: bool = False
) -> JobReply:
    return JobReply(
        title="Data Analyst",
        employer="Example Corp",
        city="Springfield",
        country="Freedonia",
        start=start,
        end=end,
        is_current=is_current,
        description="Built weekly reports.",
    )


def make_reply(**overrides: object) -> CvFactsReply:
    fields: dict[str, object] = {
        "name": "Ada Example",
        "current_title": "Senior Analyst",
        "skills": ["SQL", "Python"],
        "city": "Shelbyville",
        "country": "Freedonia",
        "highest_degree": "Master",
        "jobs": [make_job_reply()],
        "education": [
            EducationReply(
                degree="Master",
                university="Example University",
                major="Statistics",
                graduated="2017-06",
            )
        ],
    }
    fields.update(overrides)
    return CvFactsReply.model_validate(fields)


def test_ext_002_reply_name_becomes_facts_name():
    assert facts_from_reply(make_reply()).name == "Ada Example"


def test_ext_003_reply_current_title_becomes_facts_current_title():
    assert facts_from_reply(make_reply()).current_title == "Senior Analyst"


def test_ext_004_reply_skills_become_facts_skills():
    assert facts_from_reply(make_reply()).skills == ("SQL", "Python")


def test_ext_006_reply_city_and_country_become_facts_address():
    facts = facts_from_reply(make_reply())

    assert (facts.city, facts.country) == ("Shelbyville", "Freedonia")


def test_ext_009_reply_jobs_keep_employer_location_title_dates_and_description():
    job = facts_from_reply(make_reply()).jobs[0]

    assert (
        job.employer,
        job.city,
        job.country,
        job.title,
        job.start,
        job.end,
        job.description,
    ) == (
        "Example Corp",
        "Springfield",
        "Freedonia",
        "Data Analyst",
        YearMonth(2018, 5),
        YearMonth(2020, 1),
        "Built weekly reports.",
    )


def test_ext_010_reply_highest_degree_becomes_facts_highest_degree():
    assert facts_from_reply(make_reply()).highest_degree == "Master"


def test_ext_010_reply_education_keeps_degree_university_major_and_graduation():
    education = facts_from_reply(make_reply()).education[0]

    assert (education.degree, education.university, education.major, education.graduated) == (
        "Master",
        "Example University",
        "Statistics",
        YearMonth(2017, 6),
    )


def test_mis_001_null_reply_field_becomes_none():
    reply = make_reply(name=None, current_title=None, city=None, country=None, highest_degree=None)

    facts = facts_from_reply(reply)

    assert (facts.name, facts.current_title, facts.city, facts.country, facts.highest_degree) == (
        None,
        None,
        None,
        None,
        None,
    )


def test_mis_001_null_job_end_becomes_none():
    reply = make_reply(jobs=[make_job_reply(end=None, is_current=True)])

    assert facts_from_reply(reply).jobs[0].end is None


def test_ext_002_request_contains_the_cv_text():
    request = build_extraction_request(TEMPLATE, "Ada Example, analyst since 2018.")

    assert (
        request == "Extract the facts.\n---\nAda Example, analyst since 2018.\n---\nAnswer in JSON."
    )


@pytest.mark.parametrize("bad_date", ["May 2018", "2018-13", "2018-00", "2018"])
def test_ext_002_bad_date_raises_llm_output_error_with_the_raw_output(bad_date: str):
    reply = make_reply(jobs=[make_job_reply(start=bad_date)])

    with pytest.raises(LlmOutputError) as error:
        facts_from_reply(reply)

    assert error.value.raw_output == reply.model_dump_json()


def test_dec_015_current_marker_with_an_end_is_refused():
    reply = make_reply(jobs=[make_job_reply(end="2020-01", is_current=True)])

    with pytest.raises(LlmOutputError) as error:
        facts_from_reply(reply)

    assert error.value.raw_output == reply.model_dump_json()


def test_dec_015_reply_is_current_flows_into_the_job():
    reply = make_reply(
        jobs=[
            make_job_reply(end=None, is_current=True),
            make_job_reply(end=None, is_current=False),
        ]
    )

    jobs = facts_from_reply(reply).jobs

    assert [job.is_current for job in jobs] == [True, False]
