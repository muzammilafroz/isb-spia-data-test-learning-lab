"""Execute every lesson notebook from a clean kernel."""

from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbconvert.preprocessors import ClearOutputPreprocessor

ROOT = Path(__file__).resolve().parents[1]
LESSON_DIR = ROOT / "notebooks" / "lessons"


def execute(source: Path, destination: Path) -> None:
    notebook = nbformat.read(source, as_version=4)
    notebook, _ = ClearOutputPreprocessor().preprocess(notebook, {})
    client = NotebookClient(
        notebook,
        timeout=300,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
        allow_errors=False,
    )
    client.execute(cwd=str(ROOT))
    nbformat.write(notebook, destination)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="Replace committed lesson notebooks with freshly executed copies.",
    )
    args = parser.parse_args()
    os.environ.setdefault("LEARNING_LAB_DATA_BASE", str(ROOT / "data" / "teaching"))

    lessons = sorted(LESSON_DIR.glob("*.ipynb"))
    if args.write:
        for lesson in lessons:
            execute(lesson, lesson)
            print(f"Executed {lesson.relative_to(ROOT)}")
        return

    with tempfile.TemporaryDirectory(prefix="learning-lab-notebooks-") as folder:
        temporary = Path(folder)
        for lesson in lessons:
            execute(lesson, temporary / lesson.name)
            print(f"Fresh-kernel check passed: {lesson.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
