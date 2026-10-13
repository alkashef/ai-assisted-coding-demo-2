"""The candidate router (LST-002)."""

from fastapi import APIRouter

from src.api.schemas import CandidateSummary
from src.records import Workspace
from src.workspace_views import candidate_list


def create_router(workspace: Workspace) -> APIRouter:
    """Creates the router for the candidates, reading from the given workspace."""
    router = APIRouter(prefix="/api/candidates")

    @router.get("")
    async def list_candidates() -> list[CandidateSummary]:
        return [
            CandidateSummary(id=item.candidate_id, name=item.name)
            for item in candidate_list(workspace)
        ]

    return router
