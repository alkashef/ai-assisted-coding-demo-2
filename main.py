"""The entry point: loads the settings, builds the objects, runs the pipeline, starts the server.

It sets up logging, then runs the start-up pipeline to the end before the server starts, so the
app is created from a finished workspace (design section 2.1, DEC-007). With `--evaluate` it
prints the evaluation report instead of starting the server (DEC-017). It only connects modules
and holds no logic.
"""

import argparse
import asyncio
import logging
import sys
from datetime import date
from pathlib import Path

import uvicorn

from src.api.app import create_app
from src.config import (
    EvaluationSettings,
    LogSettings,
    Settings,
    load_settings,
    settings_summary,
)
from src.evaluation import (
    EvaluationLimits,
    evaluate,
    format_report,
    parse_gold_jobs,
    parse_ground_truth,
)
from src.file_reader import FileReader
from src.llm_client import LlmClient, build_sdk
from src.pipeline import Pipeline, PipelineServices, PipelineSettings
from src.records import Workspace
from src.vector_store import ChromaVectorStore

logger = logging.getLogger(__name__)


def main(env_file: Path, evaluate: bool = False) -> int:
    """Runs the app until the server stops, or prints the evaluation report.

    Args:
        env_file: The `.env` file with the settings.
        evaluate: True to print the evaluation report instead of starting the server.

    Returns:
        The exit code: 0, or 1 when an evaluation check fails.

    Raises:
        ConfigError: A setting is missing or invalid.
        InputFileError: An input folder, a prompt file or an evaluation file cannot be read.
        EvaluationDataError: An evaluation file is not in the expected format.
    """
    settings = load_settings(env_file)
    _configure_logging(settings.log)
    try:
        logger.info("Starting with %s", settings_summary(settings))
        if evaluate:
            return _run_evaluation(settings)
        workspace = asyncio.run(_build_workspace(settings))
        app = create_app(workspace, settings.server.web_root)
        uvicorn.run(app, host=settings.server.host, port=settings.server.port)
    except Exception:
        logger.exception("The app stopped")
        raise
    return 0


def _run_evaluation(settings: Settings) -> int:
    """Reads the evaluation files, builds the workspace, prints the report, returns the code."""
    files = settings.evaluation
    reader = FileReader()
    relevant = parse_ground_truth(reader.read_text(files.ground_truth_path))
    gold = parse_gold_jobs(reader.read_text(files.gold_jobs_path))
    workspace = asyncio.run(_build_workspace(settings))
    report = evaluate(workspace, relevant, gold, _limits(files))
    sys.stdout.write(format_report(report) + "\n")
    return 0 if report.passed else 1


def _limits(settings: EvaluationSettings) -> EvaluationLimits:
    """Passes the evaluation limits down as the evaluation module's own settings."""
    return EvaluationLimits(
        top_k=settings.top_k,
        min_relevant_in_top_k=settings.min_relevant_in_top_k,
        min_date_match_percent=settings.min_date_match_percent,
    )


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
    parser = argparse.ArgumentParser(description="Run the app, or check it against the sample.")
    parser.add_argument(
        "--evaluate", action="store_true", help="print the evaluation report and exit (DEC-017)"
    )
    sys.exit(main(Path("config/.env"), evaluate=parser.parse_args().evaluate))
