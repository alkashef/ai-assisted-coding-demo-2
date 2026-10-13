"""The status router: liveness and the failure list (ERR-001)."""

from fastapi import APIRouter

from src.api.schemas import FailureSummary, Health
from src.records import Workspace
from src.workspace_views import failure_list


def create_router(workspace: Workspace) -> APIRouter:
    """Creates the router for `/health` and `/api/failures`."""
    router = APIRouter()

    @router.get("/health")
    async def health() -> Health:
        return Health(status="ok")

    @router.get("/api/failures")
    async def list_failures() -> list[FailureSummary]:
        return [FailureSummary(item_id=f.item_id, cause=f.cause) for f in failure_list(workspace)]

    return router
