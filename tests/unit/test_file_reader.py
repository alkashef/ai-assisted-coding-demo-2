"""Tests for `src/file_reader.py`."""

from pathlib import Path

import pytest

from src.file_reader import FileReader, InputFileError
from src.records import Document


def _write(folder: Path, name: str, text: str) -> None:
    (folder / name).write_text(text, encoding="utf-8")


def test_ext_001_reads_every_text_file_in_the_cv_folder(tmp_path: Path) -> None:
    _write(tmp_path, "b.txt", "Second CV é")
    _write(tmp_path, "a.txt", "First CV")
    _write(tmp_path, "notes.md", "not a CV")

    documents = FileReader().read_documents(tmp_path)

    assert documents == [Document("a.txt", "First CV"), Document("b.txt", "Second CV é")]


def test_job_001_reads_every_text_file_in_the_job_folder(tmp_path: Path) -> None:
    _write(tmp_path, "job2.txt", "Nurse")
    _write(tmp_path, "job1.txt", "Welder")

    documents = FileReader().read_documents(tmp_path)

    assert [d.doc_id for d in documents] == ["job1.txt", "job2.txt"]


def test_ext_001_missing_folder_stops_with_a_clear_message(tmp_path: Path) -> None:
    missing = tmp_path / "nope"

    with pytest.raises(InputFileError, match="folder not found"):
        FileReader().read_documents(missing)


def test_ext_001_prompt_file_is_read_as_text(tmp_path: Path) -> None:
    _write(tmp_path, "prompt.md", "Extract {{CV_TEXT}}")

    assert FileReader().read_text(tmp_path / "prompt.md") == "Extract {{CV_TEXT}}"


def test_ext_001_missing_prompt_file_stops_with_a_clear_message(tmp_path: Path) -> None:
    with pytest.raises(InputFileError, match="file not found"):
        FileReader().read_text(tmp_path / "missing.md")
