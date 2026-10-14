"""Runs the start-up steps and returns the in-memory workspace that the views read.

Reads both folders, embeds every document into the two vector stores, extracts every CV,
calculates the attributes, ranks both ways and asks for one recommendation per pair (DEC-007).
It does not read files, call OpenAI or Chroma itself: the reader, the LLM client and the vector
stores are passed in. Each prompt file is the system text as read; the user text with the tagged
documents comes from `extraction.py` and `recommendation.py` (DEC-016). Implements EXT-001,
JOB-001, PRG-003, MIS-002, ERR-001, ERR-002, RNK-002 and REC-001.

The only place that catches `LlmError` (DEC-008): a failed call is recorded and the rest go on.
"""

import asyncio
import logging
from collections.abc import Awaitable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Protocol

from src.attributes import calculate_attributes
from src.extraction import build_extraction_user_text, facts_from_reply
from src.llm_schemas import CvFactsReply, RecommendationReply
from src.ports import Embedder, LlmError, LlmOutputError, StructuredCompleter, VectorIndex
from src.ranking import append_unscored
from src.recommendation import build_recommendation_user_text, recommendation_from_reply
from src.records import CvFacts, Document, Failure, Recommendation, Workspace

logger = logging.getLogger(__name__)


class TextReader(Protocol):
    """Reads the input documents and the prompt files."""

    def read_documents(self, folder: Path) -> list[Document]:
        """Reads every text file in a folder, sorted by file name."""
        ...

    def read_text(self, path: Path) -> str:
        """Reads one text file."""
        ...


@dataclass(frozen=True)
class PipelineSettings:
    """Where the inputs are, and how many LLM calls may run at once."""

    cv_folder: Path
    job_folder: Path
    extract_prompt_path: Path
    match_prompt_path: Path
    max_concurrency: int


@dataclass(frozen=True)
class PipelineServices:
    """The collaborators that reach the outside systems."""

    reader: TextReader
    completer: StructuredCompleter
    embedder: Embedder
    cv_index: VectorIndex
    job_index: VectorIndex


@dataclass(frozen=True)
class _Inputs:
    """The documents and the two system texts (the prompt files) read at the start of a run."""

    cvs: list[Document]
    jobs: list[Document]
    extract_system_text: str
    match_system_text: str


class _GuardedCalls:
    """Runs LLM calls within the concurrency limit and records each one that fails.

    State: the semaphore that limits calls in flight (DEC-007) and the failure list (DEC-008).
    """

    def __init__(self, limit: int) -> None:
        """Creates the guard with an empty failure list."""
        self._semaphore = asyncio.Semaphore(limit)
        self.failures: list[Failure] = []

    async def run_all[K: (str, tuple[str, str]), T](
        self, step: str, calls: dict[K, Awaitable[T]]
    ) -> dict[K, T]:
        """Runs the calls concurrently and returns the result of each one that succeeded.

        Args:
            step: The name of the step, such as "Extraction", for the failure list.
            calls: One call per item. The key is a document ID or a (job ID, CV ID) pair.

        Returns:
            The result per key, without the keys whose call raised `LlmError`.
        """
        keys = list(calls)
        results = await asyncio.gather(*(self._run(key, step, calls[key]) for key in keys))
        succeeded = {
            key: result for key, result in zip(keys, results, strict=True) if result is not None
        }
        logger.info("%s done for %d of %d items", step, len(succeeded), len(keys))
        return succeeded

    async def _run[T](self, key: str | tuple[str, str], step: str, call: Awaitable[T]) -> T | None:
        """Runs one call. Records an `LlmError` and returns `None` instead of raising it."""
        async with self._semaphore:
            try:
                result = await call
            except LlmError as err:
                self._record(_item_id(key), step, err)
                return None
        return result

    def _record(self, item_id: str, step: str, err: LlmError) -> None:
        """Adds one failure to the list and logs it, with the raw output only at DEBUG."""
        self.failures.append(Failure(item_id=item_id, cause=f"{step} failed: {err}"))
        logger.error("%s failed for %s: %s", step, item_id, err)
        if isinstance(err, LlmOutputError):
            logger.debug("Raw output for %s: %s", item_id, err.raw_output)


class Pipeline:
    """Builds the workspace at start-up (DEC-007).

    State: the services and the settings. Each build starts with empty results.
    """

    def __init__(self, services: PipelineServices, settings: PipelineSettings) -> None:
        """Creates the pipeline.

        Args:
            services: The reader, the LLM client and the two vector stores.
            settings: The input paths and the concurrency limit.
        """
        self._services = services
        self._settings = settings

    async def build(self, today: date) -> Workspace:
        """Runs every start-up step and returns the results.

        Args:
            today: Today's date. Its month is "Present" for the attributes.

        Returns:
            The workspace. A failed LLM call leaves its result out and is in the failure list.

        Raises:
            InputFileError: The reader cannot read a folder or a prompt file.
        """
        inputs = self._read_inputs()
        calls = _GuardedCalls(self._settings.max_concurrency)
        cv_vectors = await calls.run_all("Embedding", self._embedding_calls(inputs.cvs))
        job_vectors = await calls.run_all("Embedding", self._embedding_calls(inputs.jobs))
        _add_vectors(cv_vectors, self._services.cv_index)
        _add_vectors(job_vectors, self._services.job_index)
        facts = await calls.run_all("Extraction", self._extraction_calls(inputs))
        recommendations = await calls.run_all(
            "Recommendation", self._recommendation_calls(inputs, facts)
        )
        logger.info("Start-up pipeline finished with %d failures", len(calls.failures))
        return Workspace(
            cvs=tuple(inputs.cvs),
            jobs=tuple(inputs.jobs),
            facts=facts,
            attributes={cv_id: calculate_attributes(f, today) for cv_id, f in facts.items()},
            ranked_candidates=_rank(inputs.jobs, job_vectors, self._services.cv_index, inputs.cvs),
            ranked_jobs=_rank(inputs.cvs, cv_vectors, self._services.job_index, inputs.jobs),
            recommendations=recommendations,
            failures=tuple(calls.failures),
        )

    def _read_inputs(self) -> _Inputs:
        """Reads both folders and both prompt files."""
        reader = self._services.reader
        settings = self._settings
        inputs = _Inputs(
            cvs=reader.read_documents(settings.cv_folder),
            jobs=reader.read_documents(settings.job_folder),
            extract_system_text=reader.read_text(settings.extract_prompt_path),
            match_system_text=reader.read_text(settings.match_prompt_path),
        )
        logger.info("Read %d CVs and %d job descriptions", len(inputs.cvs), len(inputs.jobs))
        return inputs

    def _embedding_calls(self, documents: list[Document]) -> dict[str, Awaitable[list[float]]]:
        """Prepares one embedding call per document, on its raw text (DEC-014)."""
        return {doc.doc_id: self._services.embedder.embed(doc.text) for doc in documents}

    def _extraction_calls(self, inputs: _Inputs) -> dict[str, Awaitable[CvFacts]]:
        """Prepares one extraction call per CV."""
        return {cv.doc_id: self._extract(inputs.extract_system_text, cv) for cv in inputs.cvs}

    def _recommendation_calls(
        self, inputs: _Inputs, facts: dict[str, CvFacts]
    ) -> dict[tuple[str, str], Awaitable[Recommendation]]:
        """Prepares one recommendation call per job and extracted CV."""
        return {
            (job.doc_id, cv_id): self._recommend(inputs.match_system_text, job, cv_facts)
            for job in inputs.jobs
            for cv_id, cv_facts in facts.items()
        }

    async def _extract(self, system_text: str, cv: Document) -> CvFacts:
        """Asks the LLM for the facts of one CV."""
        user_text = build_extraction_user_text(cv.text)
        reply = await self._services.completer.complete(system_text, user_text, CvFactsReply)
        return facts_from_reply(reply)

    async def _recommend(self, system_text: str, job: Document, facts: CvFacts) -> Recommendation:
        """Asks the LLM whether to interview one candidate for one job."""
        user_text = build_recommendation_user_text(job.text, facts)
        reply = await self._services.completer.complete(system_text, user_text, RecommendationReply)
        return recommendation_from_reply(reply)


def _add_vectors(vectors: dict[str, list[float]], index: VectorIndex) -> None:
    """Stores each vector in the index under its document ID."""
    for doc_id, vector in vectors.items():
        index.add(doc_id, vector)


def _rank(
    queries: list[Document],
    vectors: dict[str, list[float]],
    index: VectorIndex,
    targets: list[Document],
) -> dict[str, tuple[tuple[str, float | None], ...]]:
    """Ranks every target for each query, best first; unscored targets go last (MIS-002).

    A query without a vector gets every target unscored.
    """
    target_ids = [target.doc_id for target in targets]
    rankings: dict[str, tuple[tuple[str, float | None], ...]] = {}
    for query in queries:
        vector = vectors.get(query.doc_id)
        scored = [] if vector is None else index.nearest(vector)
        rankings[query.doc_id] = tuple(append_unscored(scored, target_ids))
    return rankings


def _item_id(key: str | tuple[str, str]) -> str:
    """Names the item of a call: a document ID, or "job ID + CV ID" for a pair."""
    return key if isinstance(key, str) else " + ".join(key)
