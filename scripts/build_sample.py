"""Build the demo sample from the raw TalentCLEF files (DEC-010).

    python scripts/build_sample.py RAW_DIR OUT_DIR --jobs 29243 32447 38671 --counts 4 3 3

RAW_DIR holds `queries/`, `corpus/` and `qrels.tsv`. The raw files are only read. OUT_DIR gets
`cvs/`, `job_descriptions/`, `ground_truth.tsv` and `ATTRIBUTION.txt`.
"""

import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class JobPick:
    """A job description to copy and how many of its matching CVs to copy with it."""

    job_id: str
    cv_count: int


class SampleError(Exception):
    """The sample cannot be built from the given input."""


def _read_matches(qrels: Path) -> dict[str, list[str]]:
    """Return the relevant CV IDs per job ID, in file order."""
    matches: dict[str, list[str]] = {}
    for line in qrels.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        job_id, _, cv_id, relevance = line.split("\t")
        if relevance == "1":
            matches.setdefault(job_id, []).append(cv_id)
    return matches


def _choose_matches(raw: Path, picks: list[JobPick], min_matches: int) -> list[tuple[str, str]]:
    """Return (job ID, CV ID) pairs: the first `cv_count` matching CVs of each job."""
    matches = _read_matches(raw / "qrels.tsv")
    chosen: list[tuple[str, str]] = []
    for pick in picks:
        if pick.cv_count < min_matches:
            raise SampleError(f"Each job needs at least {min_matches} matching CVs.")
        found = matches.get(pick.job_id, [])
        if len(found) < pick.cv_count:
            raise SampleError(
                f"Job {pick.job_id} has {len(found)} matching CVs, {pick.cv_count} needed."
            )
        chosen.extend((pick.job_id, cv_id) for cv_id in found[: pick.cv_count])
    return chosen


def _copy_files(raw: Path, out: Path, picks: list[JobPick], chosen: list[tuple[str, str]]) -> None:
    """Copy the job descriptions and CVs into `out`, adding the .txt extension."""
    (out / "cvs").mkdir(parents=True, exist_ok=True)
    (out / "job_descriptions").mkdir(parents=True, exist_ok=True)
    for pick in picks:
        source = raw / "queries" / pick.job_id
        shutil.copyfile(source, out / "job_descriptions" / f"{pick.job_id}.txt")
    for _, cv_id in chosen:
        shutil.copyfile(raw / "corpus" / cv_id, out / "cvs" / f"{cv_id}.txt")


def build_sample(raw: Path, out: Path, picks: list[JobPick], min_matches: int) -> None:
    """Copy the chosen jobs and their first matching CVs from `raw` into `out`.

    Args:
        raw: Folder with `queries/`, `corpus/` and `qrels.tsv`. Only read.
        out: Folder to fill. It must be missing or empty.
        picks: The job descriptions to copy, each with its number of matching CVs.
        min_matches: Least number of matching CVs each job must get.

    Raises:
        SampleError: `out` is not empty, a count is below the minimum, or the raw data
            has too few matches.
    """
    if out.exists() and any(out.iterdir()):
        raise SampleError(f"The output folder is not empty: {out}")
    chosen = _choose_matches(raw, picks, min_matches)
    _copy_files(raw, out, picks, chosen)
    rows = ["job_id\tcv_id", *(f"{job_id}\t{cv_id}" for job_id, cv_id in chosen)]
    (out / "ground_truth.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (out / "ATTRIBUTION.txt").write_text(
        "Data: TalentCLEF 2026 Task A, version 0.3.0 (English development set).\n"
        "DOI: 10.5281/zenodo.19652670\n"
        "License: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)\n"
        "The files are copied unchanged, with a .txt extension added.\n",
        encoding="utf-8",
    )


def _parse_args() -> argparse.Namespace:
    """Read the command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--jobs", nargs="+", required=True)
    parser.add_argument("--counts", nargs="+", type=int, required=True)
    parser.add_argument("--min-matches", type=int, default=3)
    return parser.parse_args()


def main() -> int:
    """Build the sample from the command-line arguments and print the counts."""
    args = _parse_args()
    if len(args.jobs) != len(args.counts):
        print("error: give one count per job ID")
        return 1
    picks = [JobPick(job, count) for job, count in zip(args.jobs, args.counts, strict=True)]
    try:
        build_sample(args.raw, args.out, picks, args.min_matches)
    except SampleError as error:
        print(f"error: {error}")
        return 1
    cvs = len(list((args.out / "cvs").iterdir()))
    jobs = len(list((args.out / "job_descriptions").iterdir()))
    print(f"Built {jobs} job descriptions and {cvs} CVs in {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
