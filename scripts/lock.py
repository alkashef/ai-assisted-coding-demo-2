"""Regenerate `constraints.txt`, the full pin list of the installed packages (DEC-018).

    python scripts/lock.py

Run it from the project's conda environment, in the same change that edits `requirements.txt`.
`scripts/check.py` fails when `constraints.txt` lacks a pin of `requirements.txt`. Never edit
`constraints.txt` by hand.
"""

import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def pip_freeze() -> str:
    """Return the output of `pip freeze` for this Python, without editable installs."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze", "--exclude-editable"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return result.stdout


def write_constraints(target: Path, freeze: Callable[[], str]) -> None:
    """Write the frozen pins to `target`: one pin per line, one newline at the end."""
    lines = [line.strip() for line in freeze().splitlines() if line.strip()]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    """Regenerate `constraints.txt` in the project root. Return 0."""
    target = ROOT / "constraints.txt"
    write_constraints(target, pip_freeze)
    print(f"Wrote {target.name}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
