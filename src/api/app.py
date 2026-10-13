"""The app factory: creates FastAPI, includes the routers and serves the front end (DEC-002)."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.api import candidates, jobs, status
from src.records import Workspace


def create_app(workspace: Workspace, web_root: Path) -> FastAPI:
    """Creates the app. There is no authentication and no CORS (DEC-013).

    Args:
        workspace: The finished workspace that the endpoints read.
        web_root: The folder of static front-end files, served at `/`.

    Returns:
        The app. The static files are mounted last so that the API paths win.
    """
    app = FastAPI()
    app.include_router(status.create_router(workspace))
    app.include_router(jobs.create_router(workspace))
    app.include_router(candidates.create_router(workspace))
    app.mount("/", StaticFiles(directory=web_root, html=True), name="web")
    return app
