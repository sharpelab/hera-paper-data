"""``submit_output``: what the grader agent runs after writing its output file.

Runs the grader's ``grade.py check`` on the file (shape and sanity only; the score is never
computed here, so the agent cannot tune toward it), prints ``accepted`` or the reasons, and on
accept writes the sentinel the runner watches.  The runner sets the environment:

    HERA_GRADER_DIR   the grader directory (holds grade.py)
    HERA_OUTPUT_PATH  where the agent was told to write the file
    HERA_SENTINEL     written on accept
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    try:
        grader_dir = Path(os.environ["HERA_GRADER_DIR"])
        output = Path(os.environ["HERA_OUTPUT_PATH"])
        sentinel = Path(os.environ["HERA_SENTINEL"])
    except KeyError as e:
        print(f"submit_output: {e.args[0]} is not set; this command only works inside a grading run")
        return 2
    if not output.exists():
        print(f"rejected: {output} does not exist; write the output file there first")
        return 1
    proc = subprocess.run([sys.executable, str(grader_dir / "grade.py"), "check", str(output)],
                          capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    if proc.returncode != 0:
        if proc.stderr.strip():
            sys.stdout.write(proc.stderr[-2000:])
        return 1
    sentinel.write_text("accepted\n", encoding="utf-8")
    print("stop now: the output file has been accepted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
