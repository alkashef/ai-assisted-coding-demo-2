"""Tests for `src/pipeline.py`. Every collaborator is a fake: no file, no LLM, no Chroma."""

import asyncio
import math
from collections import Counter
from datetime import date
from pathlib import Path

import pytest
from pydantic import BaseModel

import src.pipeline
from src.attributes import calculate_attributes
from src.llm_schemas import CvFactsReply, JobReply, RecommendationReply
from src.pipeline import Pipeline, PipelineServices, PipelineSettings
from src.ports import LlmError, LlmOutputError
from src.records import Document, Failure, Recommendation

TODAY = date(2026, 10, 13)
CV_FOLDER = Path("cvs")
JOB_FOLDER = Path("jobs")
EXTRACT_PROMPT = Path("extract.md")
MATCH_PROMPT = Path("match.md")
EXTRACT_TEMPLATE = "Extract the facts."
MATCH_TEMPLATE = "Match."

CVS = [
    Document("a.txt", "CV of a data analyst"),
    Document("b.txt", "CV of a nurse"),
    Document("c.txt", "CV of a welder"),
]
JOBS = [
    Document("j1.txt", "Data analyst wanted"),
    Document("j2.txt", "Welder wanted"),
]
VECTORS = {
    "CV of a data analyst": [1.0, 0.0],
    "CV of a nurse": [0.6, 0.8],
    "CV of a welder": [0.0, 1.0],
    "Data analyst wanted": [0.995, 0.1],
    "Welder wanted": [0.1, 0.995],
}


def _facts_reply(start: str = "2018-05") -> CvFactsReply:
    job = JobReply(
        title="Analyst",
        employer="Example Corp",
        city="Springfield",
        country="Freedonia",
        start=start,
        end=None,
        is_current=True,
        description="Built reports.",
    )
    return CvFactsReply(
        name="Invented Person",
        current_title="Analyst",
        skills=["SQL"],
        city="Springfield",
        country="Freedonia",
        highest_degree=None,
        jobs=[job],
        education=[],
    )


class FakeReader:
    def read_documents(self, folder: Path) -> list[Document]:
        return {CV_FOLDER: CVS, JOB_FOLDER: JOBS}[folder]

    def read_text(self, path: Path) -> str:
        return {EXTRACT_PROMPT: EXTRACT_TEMPLATE, MATCH_PROMPT: MATCH_TEMPLATE}[path]


class FakeLlm:
    """Answers by request text. A text that starts with an entry of `failing` raises `error`."""

    def __init__(
        self,
        facts: CvFactsReply | None = None,
        failing: tuple[str, ...] = (),
        error: Exception | None = None,
    ) -> None:
        self.facts = facts or _facts_reply()
        self.failing = failing
        self.error = error or LlmError("call with model m failed: APIConnectionError")
        self.embedded: Counter[str] = Counter()
        self.requests: list[str] = []
        self.system_texts: dict[type[BaseModel], set[str]] = {}
        self.in_flight = 0
        self.max_in_flight = 0

    async def _enter(self, text: str) -> None:
        self.in_flight += 1
        self.max_in_flight = max(self.max_in_flight, self.in_flight)
        await asyncio.sleep(0)
        self.in_flight -= 1
        if text.startswith(self.failing):
            raise self.error

    async def embed(self, text: str) -> list[float]:
        self.embedded[text] += 1
        await self._enter(text)
        return VECTORS[text]

    async def complete[T: BaseModel](self, system: str, user: str, schema: type[T]) -> T:
        self.requests.append(user)
        self.system_texts.setdefault(schema, set()).add(system)
        await self._enter(user)
        if schema is CvFactsReply:
            return schema.model_validate(self.facts.model_dump())
        return schema.model_validate({"interview": True, "reason": "Fits."})


class FakeIndex:
    def __init__(self) -> None:
        self.vectors: dict[str, list[float]] = {}

    def add(self, item_id: str, vector: list[float]) -> None:
        self.vectors[item_id] = vector

    def nearest(self, vector: list[float]) -> list[tuple[str, float]]:
        pairs = [(item_id, _cosine(vector, other)) for item_id, other in self.vectors.items()]
        return sorted(pairs, key=lambda pair: (-pair[1], pair[0]))


def _cosine(left: list[float], right: list[float]) -> float:
    dot = sum(x * y for x, y in zip(left, right, strict=True))
    return dot / (math.hypot(*left) * math.hypot(*right))


def _pipeline(llm: FakeLlm, max_concurrency: int = 5) -> Pipeline:
    services = PipelineServices(
        reader=FakeReader(),
        completer=llm,
        embedder=llm,
        cv_index=FakeIndex(),
        job_index=FakeIndex(),
    )
    settings = PipelineSettings(
        cv_folder=CV_FOLDER,
        job_folder=JOB_FOLDER,
        extract_prompt_path=EXTRACT_PROMPT,
        match_prompt_path=MATCH_PROMPT,
        max_concurrency=max_concurrency,
    )
    return Pipeline(services, settings)


def _ids(ranking: tuple[tuple[str, float | None], ...]) -> list[str]:
    return [item_id for item_id, _ in ranking]


async def test_ext_001_every_cv_from_the_reader_is_in_the_workspace():
    workspace = await _pipeline(FakeLlm()).build(TODAY)

    assert workspace.cvs == tuple(CVS)


async def test_job_001_every_job_description_from_the_reader_is_in_the_workspace():
    workspace = await _pipeline(FakeLlm()).build(TODAY)

    assert workspace.jobs == tuple(JOBS)


async def test_prg_003_each_cv_is_extracted_once():
    llm = FakeLlm()

    workspace = await _pipeline(llm).build(TODAY)

    extraction_requests = [r for r in llm.requests if r.startswith("<cv>")]
    assert sorted(extraction_requests) == sorted(f"<cv>\n{cv.text}\n</cv>" for cv in CVS)
    assert set(workspace.facts) == {"a.txt", "b.txt", "c.txt"}


async def test_prg_003_each_document_is_embedded_once():
    llm = FakeLlm()

    await _pipeline(llm).build(TODAY)

    assert llm.embedded == Counter({doc.text: 1 for doc in [*CVS, *JOBS]})


async def test_prg_003_attributes_are_calculated_once_per_cv(monkeypatch: pytest.MonkeyPatch):
    calculated: list[date] = []

    def counting_calculate(facts, today):
        calculated.append(today)
        return calculate_attributes(facts, today)

    monkeypatch.setattr(src.pipeline, "calculate_attributes", counting_calculate)

    workspace = await _pipeline(FakeLlm()).build(TODAY)

    assert calculated == [TODAY, TODAY, TODAY]
    expected = calculate_attributes(workspace.facts["a.txt"], TODAY)
    assert workspace.attributes == {"a.txt": expected, "b.txt": expected, "c.txt": expected}


async def test_rec_001_one_recommendation_per_job_and_cv_pair():
    workspace = await _pipeline(FakeLlm()).build(TODAY)

    pairs = {(job.doc_id, cv.doc_id) for job in JOBS for cv in CVS}
    assert set(workspace.recommendations) == pairs
    assert set(workspace.recommendations.values()) == {Recommendation(True, "Fits.")}


async def test_rnk_002_rank_does_not_change_when_attributes_change():
    short_career = await _pipeline(FakeLlm(facts=_facts_reply("2025-01"))).build(TODAY)
    long_career = await _pipeline(FakeLlm(facts=_facts_reply("1990-01"))).build(TODAY)

    assert short_career.attributes != long_career.attributes
    assert short_career.ranked_candidates == long_career.ranked_candidates
    assert short_career.ranked_jobs == long_career.ranked_jobs
    assert _ids(long_career.ranked_candidates["j1.txt"]) == ["a.txt", "b.txt", "c.txt"]
    assert _ids(long_career.ranked_candidates["j2.txt"]) == ["c.txt", "b.txt", "a.txt"]


async def test_err_002_failed_extraction_keeps_the_other_results():
    llm = FakeLlm(failing=("<cv>\nCV of a nurse",))

    workspace = await _pipeline(llm).build(TODAY)

    assert set(workspace.facts) == {"a.txt", "c.txt"}
    assert set(workspace.attributes) == {"a.txt", "c.txt"}
    assert workspace.cvs == tuple(CVS)
    assert {cv for _, cv in workspace.recommendations} == {"a.txt", "c.txt"}


async def test_err_001_failure_list_names_the_item_and_the_cause():
    error = LlmOutputError("completion with model m returned no answer", "raw reply")
    llm = FakeLlm(failing=("<cv>\nCV of a nurse",), error=error)

    workspace = await _pipeline(llm).build(TODAY)

    assert workspace.failures == (
        Failure("b.txt", "Extraction failed: completion with model m returned no answer"),
    )


async def test_err_002_failed_recommendation_leaves_that_pair_without_a_recommendation():
    llm = FakeLlm(failing=("<job_description>\nWelder wanted",))

    workspace = await _pipeline(llm).build(TODAY)

    assert set(workspace.recommendations) == {("j1.txt", cv.doc_id) for cv in CVS}
    assert len(workspace.facts) == 3
    assert [failure.item_id for failure in workspace.failures] == [
        "j2.txt + a.txt",
        "j2.txt + b.txt",
        "j2.txt + c.txt",
    ]


async def test_mis_002_cv_with_a_failed_embedding_stays_in_every_ranking_last():
    llm = FakeLlm(failing=("CV of a data analyst",))

    workspace = await _pipeline(llm).build(TODAY)

    for job in JOBS:
        assert workspace.ranked_candidates[job.doc_id][-1] == ("a.txt", None)
        assert len(workspace.ranked_candidates[job.doc_id]) == 3
    assert workspace.ranked_jobs["a.txt"] == (("j1.txt", None), ("j2.txt", None))
    assert "a.txt" in workspace.facts
    assert workspace.failures[0].item_id == "a.txt"


async def test_dec_016_pipeline_sends_the_prompt_file_as_the_system_text():
    llm = FakeLlm()

    await _pipeline(llm).build(TODAY)

    assert llm.system_texts == {
        CvFactsReply: {EXTRACT_TEMPLATE},
        RecommendationReply: {MATCH_TEMPLATE},
    }


async def test_dec_008_an_error_that_is_not_an_llm_error_is_not_caught():
    llm = FakeLlm(failing=("CV of a nurse",), error=ValueError("bug"))

    with pytest.raises(ValueError, match="bug"):
        await _pipeline(llm).build(TODAY)


async def test_dec_007_calls_stay_within_the_concurrency_limit():
    llm = FakeLlm()

    await _pipeline(llm, max_concurrency=2).build(TODAY)

    assert llm.max_in_flight == 2
