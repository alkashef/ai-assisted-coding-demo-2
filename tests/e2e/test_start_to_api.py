"""End-to-end tests from start-up to the API, with fakes at the OpenAI and Chroma boundaries.

The real file reader reads temporary folders of invented documents. The pipeline builds the
workspace, and the framework's test client reads it through the API.
"""

import math
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient
from pydantic import BaseModel

from src.api.app import create_app
from src.file_reader import FileReader
from src.llm_schemas import CvFactsReply
from src.pipeline import Pipeline, PipelineServices, PipelineSettings
from src.ports import LlmError
from src.records import Workspace

_TODAY = date(2026, 10, 13)
_BROKEN_CV = "broken.txt"
_EXTRACT_PROMPT = "Extract the facts.\n{{CV_TEXT}}"
_MATCH_PROMPT = "Interview?\n{{JOB_TEXT}}\n{{CANDIDATE_FACTS}}"


class _FakeLlm:
    """Counts its calls. Extraction fails for the broken CV. Names come from the CV text."""

    def __init__(self) -> None:
        self.completions = 0
        self.embeddings = 0

    async def complete[T: BaseModel](self, system: str, user: str, schema: type[T]) -> T:
        self.completions += 1
        if schema is CvFactsReply:
            return self._facts(user, schema)
        return schema.model_validate({"interview": True, "reason": "Fits the job."})

    def _facts(self, user: str, schema: type[BaseModel]) -> BaseModel:
        if "BROKEN" in user:
            raise LlmError("extraction with model fake failed: RateLimitError")
        name = user.split("Name: ")[1].split("\n")[0]
        return schema.model_validate(
            {
                "name": name,
                "current_title": None,
                "skills": [],
                "city": None,
                "country": None,
                "highest_degree": None,
                "jobs": [],
                "education": [],
            }
        )

    async def embed(self, text: str) -> list[float]:
        self.embeddings += 1
        return [float(text.count("data")), float(text.count("care")), 1.0]


class _FakeIndex:
    """Holds vectors in a dict and ranks them by cosine similarity."""

    def __init__(self) -> None:
        self._vectors: dict[str, list[float]] = {}

    def add(self, item_id: str, vector: list[float]) -> None:
        self._vectors[item_id] = vector

    def nearest(self, vector: list[float]) -> list[tuple[str, float]]:
        scored = [(item_id, _cosine(vector, other)) for item_id, other in self._vectors.items()]
        return sorted(scored, key=lambda pair: (-pair[1], pair[0]))


def _cosine(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    return dot / (math.hypot(*left) * math.hypot(*right))


def _write(folder: Path, name: str, text: str) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_text(text, encoding="utf-8")


def _settings(tmp_path: Path) -> PipelineSettings:
    _write(tmp_path / "cvs", "ada.txt", "Name: Ada Invented\nA data analyst.")
    _write(tmp_path / "cvs", "ben.txt", "Name: Ben Invented\nA care nurse.")
    _write(tmp_path / "cvs", _BROKEN_CV, "BROKEN care care")
    _write(tmp_path / "jobs", "analyst.txt", "Data Analyst\nWork with data.")
    _write(tmp_path / "jobs", "nurse.txt", "Nurse\nGive care.")
    _write(tmp_path / "prompts", "extract.md", _EXTRACT_PROMPT)
    _write(tmp_path / "prompts", "match.md", _MATCH_PROMPT)
    return PipelineSettings(
        cv_folder=tmp_path / "cvs",
        job_folder=tmp_path / "jobs",
        extract_prompt_path=tmp_path / "prompts" / "extract.md",
        match_prompt_path=tmp_path / "prompts" / "match.md",
        max_concurrency=2,
    )


async def _start(tmp_path: Path, llm: _FakeLlm) -> Workspace:
    services = PipelineServices(
        reader=FileReader(),
        completer=llm,
        embedder=llm,
        cv_index=_FakeIndex(),
        job_index=_FakeIndex(),
    )
    return await Pipeline(services, _settings(tmp_path)).build(_TODAY)


def _client(workspace: Workspace, tmp_path: Path) -> TestClient:
    _write(tmp_path / "web", "index.html", "<h1>Front end</h1>")
    return TestClient(create_app(workspace, tmp_path / "web"))


async def test_ext_001_start_reads_the_cv_folder_and_the_api_lists_the_candidates(
    tmp_path: Path,
) -> None:
    client = _client(await _start(tmp_path, _FakeLlm()), tmp_path)

    response = client.get("/api/candidates")

    assert response.status_code == 200
    assert response.json() == [
        {"id": "ada.txt", "name": "Ada Invented"},
        {"id": "ben.txt", "name": "Ben Invented"},
        {"id": _BROKEN_CV, "name": None},
    ]


async def test_job_001_start_reads_the_job_folder_and_the_api_lists_the_jobs(
    tmp_path: Path,
) -> None:
    client = _client(await _start(tmp_path, _FakeLlm()), tmp_path)

    response = client.get("/api/jobs")

    assert response.status_code == 200
    assert response.json() == [
        {"id": "analyst.txt", "title": "Data Analyst"},
        {"id": "nurse.txt", "title": "Nurse"},
    ]


async def test_prg_003_repeated_reads_do_not_trigger_new_llm_calls(tmp_path: Path) -> None:
    llm = _FakeLlm()
    client = _client(await _start(tmp_path, llm), tmp_path)
    calls_after_start = (llm.completions, llm.embeddings)

    for _ in range(2):
        client.get("/api/jobs/analyst.txt/ranked-candidates")
        client.get("/api/candidates/ada.txt")
        client.get("/api/candidates/ada.txt/ranked-jobs")

    assert (llm.completions, llm.embeddings) == calls_after_start
    assert calls_after_start == (3 + 2 * 2, 5)


async def test_dec_007_the_app_is_created_from_a_finished_workspace(tmp_path: Path) -> None:
    workspace = await _start(tmp_path, _FakeLlm())
    client = _client(workspace, tmp_path)

    response = client.get("/api/jobs/analyst.txt/ranked-candidates")

    ranked = response.json()
    assert [item["candidate_id"] for item in ranked] == ["ada.txt", "ben.txt", _BROKEN_CV]
    assert ranked[0]["recommendation"] == {"interview": True, "reason": "Fits the job."}
    assert ranked[2]["recommendation"] is None
    assert client.get("/api/failures").json() == [
        {
            "item_id": _BROKEN_CV,
            "cause": "Extraction failed: extraction with model fake failed: RateLimitError",
        }
    ]


async def test_lst_001_and_lst_002_lists_are_complete_after_start(tmp_path: Path) -> None:
    llm = _FakeLlm()
    client = _client(await _start(tmp_path, llm), tmp_path)

    jobs = client.get("/api/jobs").json()
    candidates = client.get("/api/candidates").json()

    assert len(jobs) == len(list((tmp_path / "jobs").iterdir()))
    assert len(candidates) == len(list((tmp_path / "cvs").iterdir()))
