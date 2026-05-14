"""Run fetch → classify → build DB in order."""

import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def run(name: str) -> None:
    subprocess.check_call([sys.executable, str(SCRIPTS / name)])


def main() -> None:
    run("fetch_datasets.py")
    run("classify_zero_shot.py")
    run("build_eval_db.py")


if __name__ == "__main__":
    main()
