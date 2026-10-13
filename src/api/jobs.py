"""The job-description router (LST-001, JOB-002, RNK-003, REC-001)."""

from fastapi import APIRouter, HTTPException

from src.api.schemas import JobSummary, RankedCandidate
from src.records import Workspace
from src.workspace_views import NotFoundError, job_list, ranked_candidates


def create_router(workspace: Workspace) -> APIRouter:
    """Creates the router for the job descriptions, reading from the given workspace."""
    router = APIRouter(prefix="/api/jobs")

    @router.get("")
    async def list_jobs() -> list[JobSummary]:
        return [JobSummary(id=item.job_id, title=item.title) for item in job_list(workspace)]

    @router.get("/{job_id}/ranked-candidates")
    async def list_ranked_candidates(job_id: str) -> list[RankedCandidate]:
        try:
            items = ranked_candidates(workspace, job_id)
        except NotFoundError as err:
            raise HTTPException(status_code=404, detail=str(err)) from err
        return [RankedCandidate.model_validate(item) for item in items]

    return router
