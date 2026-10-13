"""The entry point: loads the settings, builds the objects, runs the pipeline, starts the server.

It sets up logging, then runs the start-up pipeline to the end before the server starts, so the
app is created from a finished workspace (design section 2.1, DEC-007). It only connects modules
and holds no logic.
"""

import asyncio
import logging
from datetime import date
from pathlib import Path

import uvicorn

from src.api.app import create_app
from src.config import LogSettings, Settings, load_settings, settings_summary
from src.file_reader import FileReader
from src.llm_client import LlmClient, build_sdk
from src.pipeline import Pipeline, PipelineServices, PipelineSettings
from src.records import Workspace
from src.vector_store import ChromaVectorStore

logger = logging.getLogger(__name__)


def main(env_file: Path) -> None:
    """Runs the app until the server stops.

    Args:
        env_file: The `.env` file with the settings.

    Raises:
        ConfigError: A setting is missing or invalid.
        InputFileError: An input folder or a prompt file cannot be read.
    """
    settings = load_settings(env_file)
    _configure_logging(settings.log)
    try:
        logger.info("Starting with %s", settings_summary(settings))
        workspace = asyncio.run(_build_workspace(settings))
        app = create_app(workspace, settings.server.web_root)
        uvicorn.run(app, host=settings.server.host, port=settings.server.port)
    except Exception:
        logger.exception("The app stopped")
        raise


def _configure_logging(settings: LogSettings) -> None:
    """Logs plain text lines to the console and to the log file."""
    settings.file.parent.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    root = logging.getLogger()
    root.setLevel(settings.level)
    for handler in (logging.StreamHandler(), logging.FileHandler(settings.file, encoding="utf-8")):
        handler.setFormatter(formatter)
        root.addHandler(handler)


async def _build_workspace(settings: Settings) -> Workspace:
    """Builds the gateways and runs the start-up pipeline."""
    inputs = settings.inputs
    async with build_sdk(settings.llm) as sdk:
        client = LlmClient(settings.llm, sdk)
        services = PipelineServices(
            reader=FileReader(),
            completer=client,
            embedder=client,
            cv_index=ChromaVectorStore("cvs"),
            job_index=ChromaVectorStore("jobs"),
        )
        pipeline_settings = PipelineSettings(
            cv_folder=inputs.cv_folder,
            job_folder=inputs.job_folder,
            extract_prompt_path=inputs.extract_prompt_path,
            match_prompt_path=inputs.match_prompt_path,
            max_concurrency=settings.llm.max_concurrency,
        )
        return await Pipeline(services, pipeline_settings).build(date.today())


if __name__ == "__main__":
    main(Path("config/.env"))
