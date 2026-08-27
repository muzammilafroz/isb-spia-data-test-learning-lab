"""Extract committed notebook image outputs for temporary visual inspection."""

from __future__ import annotations

import argparse
import base64
import shutil
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "tmp" / "notebook-images")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    count = 0
    for notebook_path in sorted((ROOT / "notebooks" / "lessons").glob("*.ipynb")):
        notebook = nbformat.read(notebook_path, as_version=4)
        for cell_index, cell in enumerate(notebook.cells):
            if cell.cell_type != "code":
                continue
            for output_index, item in enumerate(cell.outputs):
                payload = item.get("data", {}).get("image/png")
                if not payload:
                    continue
                count += 1
                destination = output / f"{notebook_path.stem}-cell-{cell_index:02d}-output-{output_index:02d}.png"
                destination.write_bytes(base64.b64decode(payload))
                print(destination)
    print(f"Extracted {count} notebook image outputs.")


if __name__ == "__main__":
    main()
