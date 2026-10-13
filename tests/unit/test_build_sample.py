"""Tests for `scripts/build_sample.py`."""

from pathlib import Path

import pytest

from scripts.build_sample import JobPick, SampleError, build_sample

PICKS = [JobPick("J1", 4), JobPick("J2", 3)]
MIN_MATCHES = 3


def _make_raw(root: Path) -> Path:
    raw = root / "raw"
    (raw / "queries").mkdir(parents=True)
    (raw / "corpus").mkdir()
    for job in ("J1", "J2", "J3"):
        (raw / "queries" / job).write_text(f"job {job}", encoding="utf-8")
    rows = [("J3", "c0")]
    rows += [("J1", f"a{i}") for i in range(1, 6)]
    rows += [("J2", f"b{i}") for i in range(1, 5)]
    for _, cv in rows:
        (raw / "corpus" / cv).write_text(f"cv {cv}", encoding="utf-8")
    lines = [f"{job}\t0\t{cv}\t1" for job, cv in rows]
    (raw / "qrels.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return raw


def _build(tmp_path: Path) -> Path:
    out = tmp_path / "sample"
    build_sample(_make_raw(tmp_path), out, PICKS, MIN_MATCHES)
    return out


def test_dec_010_copies_three_job_descriptions_and_ten_cvs(tmp_path: Path) -> None:
    out = _build(tmp_path)

    assert sorted(p.name for p in (out / "job_descriptions").iterdir()) == ["J1.txt", "J2.txt"]
    assert len(list((out / "cvs").iterdir())) == 7
    assert (out / "cvs" / "a1.txt").read_text(encoding="utf-8") == "cv a1"


def test_dec_010_each_job_has_at_least_three_matching_cvs(tmp_path: Path) -> None:
    raw = _make_raw(tmp_path)

    with pytest.raises(SampleError):
        build_sample(raw, tmp_path / "sample", [JobPick("J2", 2)], MIN_MATCHES)


def test_dec_010_writes_ground_truth_with_the_expected_matches(tmp_path: Path) -> None:
    out = _build(tmp_path)

    lines = (out / "ground_truth.tsv").read_text(encoding="utf-8").splitlines()
    expected = [f"J1\ta{i}" for i in range(1, 5)] + [f"J2\tb{i}" for i in range(1, 4)]
    assert lines == ["job_id\tcv_id", *expected]


def test_dec_010_raw_input_is_not_modified(tmp_path: Path) -> None:
    raw = _make_raw(tmp_path)
    before = sorted((p.relative_to(raw), p.read_bytes()) for p in raw.rglob("*") if p.is_file())

    build_sample(raw, tmp_path / "sample", PICKS, MIN_MATCHES)

    after = sorted((p.relative_to(raw), p.read_bytes()) for p in raw.rglob("*") if p.is_file())
    assert after == before


def test_dec_010_refuses_to_overwrite_a_non_empty_output_folder(tmp_path: Path) -> None:
    raw = _make_raw(tmp_path)
    out = tmp_path / "sample"
    out.mkdir()
    (out / "keep.txt").write_text("keep", encoding="utf-8")

    with pytest.raises(SampleError):
        build_sample(raw, out, PICKS, MIN_MATCHES)

    assert (out / "keep.txt").read_text(encoding="utf-8") == "keep"


def test_dec_010_writes_the_dataset_attribution(tmp_path: Path) -> None:
    out = _build(tmp_path)

    text = (out / "ATTRIBUTION.txt").read_text(encoding="utf-8")
    assert "TalentCLEF 2026" in text
    assert "0.3.0" in text
    assert "10.5281/zenodo.19652670" in text
    assert "CC BY 4.0" in text
