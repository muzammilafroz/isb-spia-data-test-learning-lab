from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.request import urlopen

import pandas as pd

REPOSITORY = "muzammilafroz/applied-economics-data-learning-lab"
DEFAULT_REF = "v1.0.1"


def _patch_browser_http() -> None:
    if sys.platform != "emscripten":
        return
    import pyodide_http

    pyodide_http.patch_all()


def get_data_url(filename: str, ref: str = DEFAULT_REF) -> str:
    """Return a local path or versioned raw GitHub URL for one teaching file."""
    if Path(filename).name != filename:
        raise ValueError("filename must be one plain file name")

    base_override = os.getenv("LEARNING_LAB_DATA_BASE")
    if base_override:
        if base_override.startswith(("http://", "https://")):
            return f"{base_override.rstrip('/')}/{filename}"
        return str(Path(base_override).expanduser().resolve() / filename)

    selected_ref = os.getenv("LEARNING_LAB_DATA_REF", ref)
    return (
        f"https://raw.githubusercontent.com/{REPOSITORY}/"
        f"{selected_ref}/data/teaching/{filename}"
    )


def read_teaching_csv(filename: str, **kwargs) -> pd.DataFrame:
    _patch_browser_http()
    return pd.read_csv(get_data_url(filename), **kwargs)


def read_teaching_geojson(filename: str = "training_districts.geojson"):
    _patch_browser_http()
    import geopandas as gpd

    location = get_data_url(filename)
    if location.startswith(("http://", "https://")):
        with urlopen(location) as response:
            payload = json.loads(response.read().decode("utf-8"))
    else:
        payload = json.loads(Path(location).read_text(encoding="utf-8"))
    return gpd.GeoDataFrame.from_features(payload["features"], crs="EPSG:4326")
