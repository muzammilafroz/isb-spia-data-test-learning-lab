"""Build Jupyter Book, JupyterLite, quizzes, and local data into one site."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "_build"
DIST = ROOT / "dist"
BASE_URL = "/applied-economics-data-learning-lab"
ASSET_PLACEHOLDER = "/myst_assets_folder/"
INDEX_REDIRECT = "<script>(function(){var p=window.location.pathname;if(p.endsWith('/index.html'))window.location.replace((p.slice(0,-10)||'/')+window.location.search+window.location.hash);})();</script>"
MOBILE_SAFETY_STYLE = (
    '<style id="learning-lab-mobile-safety">'
    "@media(max-width:720px){html,body{max-width:100%;overflow-x:hidden}"
    "pre,table{max-width:100%;overflow-x:auto}"
    "img,svg,canvas{max-width:100%;height:auto}}"
    "</style>"
)


def run(command: list[str], *, environment: dict[str, str] | None = None) -> None:
    print("Running:", " ".join(command))
    subprocess.run(command, cwd=ROOT, env=environment, check=True)


def command_path(name: str) -> str:
    executable = shutil.which(name)
    if not executable:
        candidate = Path(sys.executable).parent / f"{name}.exe"
        if candidate.is_file():
            executable = str(candidate)
    if not executable:
        raise SystemExit(f"Required command is unavailable: {name}")
    return executable


def finalize_book_export(html: Path) -> None:
    """Apply Jupyter Book's static-export rewrites after an interrupted local crawl."""
    replacement = f"{BASE_URL}/build/"
    rewritten = 0
    for path in html.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix == ".map":
            path.unlink()
            continue
        if path.suffix not in {".html", ".js", ".json"}:
            continue
        content = path.read_text(encoding="utf-8")
        updated = content.replace(ASSET_PLACEHOLDER, replacement)
        if path.suffix == ".html":
            updated = re.sub(
                r'<button type="button"(?![^>]*aria-label=)(?=[^>]*class="myst-search-bar)',
                '<button type="button" aria-label="Search course"',
                updated,
            )
            if MOBILE_SAFETY_STYLE not in updated:
                updated = updated.replace("</head>", f"{MOBILE_SAFETY_STYLE}</head>")
        if path.name == "index.html" and INDEX_REDIRECT not in updated:
            updated = updated.replace("</head>", f"{INDEX_REDIRECT}</head>")
        if updated != content:
            path.write_text(updated, encoding="utf-8", newline="\n")
            rewritten += 1
    print(f"Finalized Jupyter Book static paths in {rewritten} files.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reuse-book", action="store_true", help="Reuse an existing _build/html export.")
    parser.add_argument("--reuse-lite", action="store_true", help="Reuse an existing _build/lite export.")
    args = parser.parse_args()
    html = BUILD / "html"
    lite = BUILD / "lite"
    targets_to_clear = [DIST]
    if not args.reuse_book:
        targets_to_clear.append(html)
    if not args.reuse_lite:
        targets_to_clear.append(lite)
    for target in targets_to_clear:
        if target.exists():
            shutil.rmtree(target)

    if not args.reuse_book:
        environment = os.environ.copy()
        environment["BASE_URL"] = BASE_URL
        run(
            [command_path("jupyter-book"), "build", "--html", "--strict"],
            environment=environment,
        )
    if not (html / "index.html").is_file():
        raise SystemExit("Jupyter Book did not create _build/html/index.html")
    finalize_book_export(html)

    if not args.reuse_lite:
        run(
            [
                command_path("jupyter-lite"),
                "build",
                "--contents",
                "notebooks",
                "--output-dir",
                str(lite),
                "--no-sourcemaps",
                "--force",
            ]
        )
    if not (lite / "lab" / "index.html").is_file():
        raise SystemExit("JupyterLite did not create _build/lite/lab/index.html")

    shutil.copytree(html, DIST)
    shutil.copytree(lite, DIST / "lab", dirs_exist_ok=True)
    shutil.copytree(ROOT / "web" / "assets", DIST / "assets")
    shutil.copytree(ROOT / "web" / "tests", DIST / "tests")
    shutil.copytree(ROOT / "web" / "certificate", DIST / "certificate")
    shutil.copytree(ROOT / "data" / "teaching", DIST / "data" / "teaching")
    public_package = DIST / "learning_lab"
    public_package.mkdir()
    for source in sorted((ROOT / "learning_lab").glob("*.py")):
        shutil.copy2(source, public_package / source.name)
    (DIST / ".nojekyll").write_text("", encoding="utf-8")

    print(f"Combined static site built at {DIST}")
    print(f"Python used for orchestration: {sys.version.split()[0]}")


if __name__ == "__main__":
    main()
