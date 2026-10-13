"""Builds the data for each read from the workspace (design section 2.1).

Pure functions over the in-memory workspace. They do not rank, call an LLM or read files: the
pipeline has done that already. Implements LST-001, LST-002 and ERR-001.
"""

from dataclasses import dataclass

from src.records import Workspace


@dataclass(frozen=True)
class JobItem:
    """One job description in the list: its ID and its title (the first line)."""

    job_id: str
    title: str


@dataclass(frozen=True)
class CandidateItem:
    """One candidate in the list: the CV ID and the name, `None` when not available (MIS-001)."""

    candidate_id: str
    name: str | None


@dataclass(frozen=True)
class FailureItem:
    """One failed LLM call: the item and the cause (ERR-001)."""

    item_id: str
    cause: str


def job_list(workspace: Workspace) -> list[JobItem]:
    """Lists the job descriptions with their titles (LST-001)."""
    return [JobItem(job.doc_id, _first_line(job.text)) for job in workspace.jobs]


def candidate_list(workspace: Workspace) -> list[CandidateItem]:
    """Lists the candidates with their names (LST-002).

    A CV whose extraction failed stays in the list with no name.
    """
    items = []
    for cv in workspace.cvs:
        facts = workspace.facts.get(cv.doc_id)
        items.append(CandidateItem(cv.doc_id, None if facts is None else facts.name))
    return items


def failure_list(workspace: Workspace) -> list[FailureItem]:
    """Lists the failed LLM calls with their causes (ERR-001)."""
    return [FailureItem(failure.item_id, failure.cause) for failure in workspace.failures]


def _first_line(text: str) -> str:
    """Returns the first line of a text, or an empty string for an empty text."""
    lines = text.splitlines()
    return lines[0].strip() if lines else ""
