from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {".git", ".venv", "node_modules", "_build", "dist", "tmp"}
SELF = Path(__file__).resolve()

forbidden_names = {
    "BurkinaFaso_2018_survey.csv",
    "BurkinaFaso_2018_test_results.csv",
    "full_survey_provided.csv",
}
forbidden_fragments = (
    "Problem 1 - Uganda map of sampling points",
    "Problem 2 - Relationship between malaria and wealth",
)
forbidden_path_fragments = (
    "predoc",
    "submission_package",
    "problem 1 -",
    "problem 2 -",
    "uganda",
    "burkinafaso",
)
microdata_signature = {"hv271", "hv201", "hv227", "hml1a", "hv204", "hv220"}
institutional_terms = (
    "".join(("i", "s", "b")),
    "".join(("s", "p", "i", "a")),
)


def notebook_visible_text(raw_text: str) -> str:
    """Return searchable notebook text without opaque binary display payloads."""
    notebook = json.loads(raw_text)
    chunks: list[str] = []
    for cell in notebook.get("cells", []):
        source = cell.get("source", "")
        chunks.append("".join(source) if isinstance(source, list) else str(source))
        for output in cell.get("outputs", []):
            stream = output.get("text", "")
            chunks.append("".join(stream) if isinstance(stream, list) else str(stream))
            chunks.append(str(output.get("evalue", "")))
            chunks.extend(output.get("traceback", []))
            for mime_type, value in output.get("data", {}).items():
                if mime_type.startswith("image/"):
                    continue
                chunks.append("".join(value) if isinstance(value, list) else str(value))
    return "\n".join(chunks)

errors = []
for path in ROOT.rglob("*"):
    if not path.is_file() or any(part in EXCLUDED_PARTS for part in path.parts):
        continue
    if path.name in forbidden_names:
        errors.append(f"forbidden file name: {path.relative_to(ROOT)}")
    relative_lower = str(path.relative_to(ROOT)).lower()
    for fragment in forbidden_path_fragments:
        if fragment in relative_lower:
            errors.append(f"forbidden private-workspace path fragment in {path.relative_to(ROOT)}")
    if path.resolve() == SELF or path.suffix.lower() in {".png", ".jpg", ".zip", ".pdf", ".woff", ".woff2"}:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    searchable_text = notebook_visible_text(text) if path.suffix.lower() == ".ipynb" else text
    for fragment in forbidden_fragments:
        if fragment.lower() in searchable_text.lower():
            errors.append(f"forbidden private-workspace text in {path.relative_to(ROOT)}")
    for term in institutional_terms:
        if term in searchable_text.lower():
            errors.append(f"institution-specific term in {path.relative_to(ROOT)}")
    if path.suffix.lower() == ".csv":
        header = set(re.split(r",", text.splitlines()[0])) if text else set()
        if len(header & microdata_signature) >= 4:
            errors.append(f"DHS-style microdata signature in {path.relative_to(ROOT)}")
    if "\u2014" in text:
        errors.append(f"em dash in {path.relative_to(ROOT)}")

if errors:
    print("Publication guard failed:")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)
print("Publication guard passed: no private assessment materials detected.")
