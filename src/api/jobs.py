"""The job-description router (LST-001)."""

from fastapi import APIRouter

from src.api.schemas import JobSummary
from src.records import Workspace
from src.workspace_views import job_list


def create_router(workspace: Workspace) -> APIRouter:
    """Creates the router for the job descriptions, reading from the given workspace."""
    router = APIRouter(prefix="/api/jobs")

    @router.get("")
    async def list_jobs() -> list[JobSummary]:
        return [JobSummary(id=item.job_id, title=item.title) for item in job_list(workspace)]

    return router
