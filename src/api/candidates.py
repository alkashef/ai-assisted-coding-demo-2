"""The candidate router (LST-002, CND-001 to CND-003)."""

from fastapi import APIRouter, HTTPException

from src.api.schemas import CandidateDetail, CandidateSummary, RankedJob
from src.records import Workspace
from src.workspace_views import NotFoundError, candidate_detail, candidate_list, ranked_job_list


def create_router(workspace: Workspace) -> APIRouter:
    """Creates the router for the candidates, reading from the given workspace."""
    router = APIRouter(prefix="/api/candidates")

    @router.get("")
    async def list_candidates() -> list[CandidateSummary]:
        return [
            CandidateSummary(id=item.candidate_id, name=item.name)
            for item in candidate_list(workspace)
        ]

    @router.get("/{candidate_id}")
    async def get_candidate(candidate_id: str) -> CandidateDetail:
        try:
            detail = candidate_detail(workspace, candidate_id)
        except NotFoundError as err:
            raise HTTPException(status_code=404, detail=str(err)) from err
        return CandidateDetail.model_validate(detail)

    @router.get("/{candidate_id}/ranked-jobs")
    async def list_ranked_jobs(candidate_id: str) -> list[RankedJob]:
        try:
            items = ranked_job_list(workspace, candidate_id)
        except NotFoundError as err:
            raise HTTPException(status_code=404, detail=str(err)) from err
        return [RankedJob.model_validate(item) for item in items]

    return router
