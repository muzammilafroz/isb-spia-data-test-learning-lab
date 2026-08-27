"""Ensure formative test notebooks remain blank and structurally complete."""

from __future__ import annotations

from pathlib import Path

import nbformat

from course_spec import MODULES

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    errors: list[str] = []
    question_total = 0
    for module in MODULES:
        path = ROOT / "notebooks" / "tests" / module["test"]
        notebook = nbformat.read(path, as_version=4)
        sources = "\n".join(cell.source for cell in notebook.cells)
        for index, cell in enumerate(notebook.cells):
            if cell.cell_type != "code":
                continue
            if cell.execution_count is not None:
                errors.append(f"{path.name} cell {index}: execution count is not blank")
            if cell.outputs:
                errors.append(f"{path.name} cell {index}: output is not blank")
        for item in module["questions"]:
            question_total += 1
            marker = f"Question ID: `{item['question_id']}`"
            blank = f"{item['variable']} = None"
            if sources.count(marker) != 1:
                errors.append(f"{path.name}: missing or repeated {item['question_id']}")
            if sources.count(blank) != 1:
                errors.append(f"{path.name}: answer variable is not a single blank: {item['variable']}")
        if "from course_spec import" in sources or "quiz-spec.v1.json" in sources:
            errors.append(f"{path.name}: answer-key source reference found")

    if question_total != 54:
        errors.append(f"expected 54 questions, found {question_total}")
    if errors:
        print("Test notebook validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("Test notebooks are blank, unexecuted, and complete for all 54 questions.")


if __name__ == "__main__":
    main()
