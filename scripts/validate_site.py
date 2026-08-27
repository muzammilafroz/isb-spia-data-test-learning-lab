"""Validate the combined static artifact before publication."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import unquote, urlsplit

import nbformat
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PAGES_ROOT = "https://muzammilafroz.github.io/isb-spia-data-test-learning-lab"
BASE_PATH = "/isb-spia-data-test-learning-lab"


def require(path: Path, errors: list[str]) -> None:
    if not path.is_file():
        errors.append(f"missing built file: {path.relative_to(ROOT)}")


def resolve_built_target(reference: str, source: Path) -> Path | None:
    if not reference or reference.startswith(("#", "mailto:", "data:", "javascript:")):
        return None
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc:
        return None
    path = unquote(parsed.path)
    if path.startswith(BASE_PATH):
        path = path[len(BASE_PATH):]
    if path.startswith("/"):
        candidate = DIST / path.lstrip("/")
    else:
        candidate = source.parent / path
    if candidate.is_dir():
        candidate = candidate / "index.html"
    elif not candidate.suffix and (candidate / "index.html").is_file():
        candidate = candidate / "index.html"
    return candidate


def check_internal_links(errors: list[str]) -> None:
    pages = [DIST / "index.html", DIST / "tests" / "index.html", DIST / "certificate" / "index.html"]
    pages.extend((DIST / "book").rglob("index.html"))
    pages.extend((DIST / "notebooks").rglob("index.html"))
    for page in pages:
        soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
        for tag, attribute in (("a", "href"), ("link", "href"), ("script", "src"), ("img", "src")):
            for element in soup.find_all(tag):
                reference = element.get(attribute)
                target = resolve_built_target(reference, page)
                if target is not None and not target.is_file():
                    errors.append(
                        f"broken internal link in {page.relative_to(DIST)}: {reference}"
                    )


def main() -> None:
    errors: list[str] = []
    required = [
        DIST / "index.html",
        DIST / "lab" / "lab" / "index.html",
        DIST / "tests" / "index.html",
        DIST / "certificate" / "index.html",
        DIST / "assets" / "quiz-spec.v1.json",
        DIST / "data" / "teaching" / "data_manifest.json",
        DIST / "learning_lab" / "io.py",
        DIST / ".nojekyll",
    ]
    for path in required:
        require(path, errors)

    quiz_path = ROOT / "web" / "assets" / "quiz-spec.v1.json"
    quiz = json.loads(quiz_path.read_text(encoding="utf-8"))
    if quiz["pass_percent"] != 80:
        errors.append("quiz pass percent is not 80")
    if len(quiz["modules"]) != 6:
        errors.append("quiz spec does not contain five modules and one capstone")
    if sum(len(item["questions"]) for item in quiz["modules"]) != 54:
        errors.append("quiz spec does not contain 54 questions")

    for folder in ("lessons", "tests"):
        for path in sorted((ROOT / "notebooks" / folder).glob("*.ipynb")):
            notebook = nbformat.read(path, as_version=4)
            source = "\n".join(cell.source for cell in notebook.cells)
            expected_colab = f"https://colab.research.google.com/github/muzammilafroz/isb-spia-data-test-learning-lab/blob/main/notebooks/{folder}/{path.name}"
            expected_lite = f"{PAGES_ROOT}/lab/index.html?path={folder}/{path.name}"
            if expected_colab not in source:
                errors.append(f"missing Colab link in {path.relative_to(ROOT)}")
            if expected_lite not in source:
                errors.append(f"missing JupyterLite link in {path.relative_to(ROOT)}")

    test_html = (ROOT / "web" / "tests" / "index.html").read_text(encoding="utf-8")
    certificate_html = (ROOT / "web" / "certificate" / "index.html").read_text(encoding="utf-8")
    for name, text in (("test form", test_html), ("certificate", certificate_html)):
        if '<meta name="viewport"' not in text:
            errors.append(f"{name} is missing a mobile viewport declaration")
        if 'lang="en"' not in text:
            errors.append(f"{name} is missing a document language")
    if "Self-assessed Learning Lab Completion Record" not in certificate_html:
        errors.append("certificate title is incorrect")
    if "not externally verified" not in certificate_html:
        errors.append("certificate limitation is missing")
    if 'class="myst-search-bar' in (DIST / "index.html").read_text(encoding="utf-8") and 'aria-label="Search course"' not in (DIST / "index.html").read_text(encoding="utf-8"):
        errors.append("rendered course search button is missing an accessible name")

    check_internal_links(errors)

    if errors:
        print("Site validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("Combined site structure, links, quiz counts, and certificate contract passed.")


if __name__ == "__main__":
    main()
