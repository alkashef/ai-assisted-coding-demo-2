"""Tests for `scripts/lock.py` (DEC-018)."""

from pathlib import Path

from scripts.lock import write_constraints

FREEZE_OUTPUT = "annotated-types==0.7.0\nfastapi==0.143.0\npydantic==2.14.1\n"


def test_dec_018_lock_script_writes_pins_from_freeze(tmp_path: Path) -> None:
    target = tmp_path / "constraints.txt"

    write_constraints(target, lambda: FREEZE_OUTPUT)

    assert target.read_text(encoding="utf-8") == FREEZE_OUTPUT


def test_dec_018_lock_script_ends_the_file_with_one_newline(tmp_path: Path) -> None:
    target = tmp_path / "constraints.txt"

    write_constraints(target, lambda: "fastapi==0.143.0\r\n\r\n")

    assert target.read_text(encoding="utf-8") == "fastapi==0.143.0\n"
