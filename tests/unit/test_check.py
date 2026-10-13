"""Tests for the lock check in `scripts/check.py` (DEC-018)."""

from scripts.check import lock_problems, pins

REQUIREMENTS = "# Direct dependencies.\nfastapi==0.143.0\npython-dotenv==1.2.4\n"
CONSTRAINTS = "annotated-types==0.7.0\nfastapi==0.143.0\npython-dotenv==1.2.4\nstarlette==1.0.0\n"


def test_dec_018_lock_check_passes_when_every_pin_is_present() -> None:
    assert lock_problems(REQUIREMENTS, CONSTRAINTS) == []


def test_dec_018_lock_check_fails_when_a_pin_is_missing() -> None:
    constraints = "annotated-types==0.7.0\nfastapi==0.143.0\n"

    problems = lock_problems(REQUIREMENTS, constraints)

    assert len(problems) == 1
    assert "python-dotenv" in problems[0]
    assert "missing" in problems[0]


def test_dec_018_lock_check_fails_when_a_version_differs() -> None:
    constraints = "fastapi==0.142.0\npython-dotenv==1.2.4\n"

    problems = lock_problems(REQUIREMENTS, constraints)

    assert len(problems) == 1
    assert "fastapi==0.143.0" in problems[0]
    assert "0.142.0" in problems[0]


def test_dec_018_pins_ignore_comments_and_normalise_names() -> None:
    lines = ["# comment", "", "PyYAML==6.0  # trailing", "Typing_Extensions==4.12.2"]
    text = "\n".join([*lines, "uvicorn[standard]==0.54.0", ""])

    assert pins(text) == {
        "pyyaml": "6.0",
        "typing-extensions": "4.12.2",
        "uvicorn": "0.54.0",
    }
